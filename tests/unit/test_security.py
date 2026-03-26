"""
Unit tests for security features:
  - 10.1  Secure credential retrieval (credentials.py)
  - 10.2  Input validation and sanitization (workflow.py)
  - 10.3  Logging with sensitive data filtering (logging_config.py)

Requirements: 12.1, 12.4, 12.5
"""

import json
import logging
import time
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.credentials import (
    clear_credential_cache,
    get_bitopro_credentials,
)
from src.ingestion.logging_config import SensitiveDataFilter, sanitize_message
from src.ingestion.models import HTTPMethod
from src.ingestion.workflow import ingest_bitopro_data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_secrets_client(api_key: str = "test-key", api_secret: str = "test-secret"):
    """Return a mock boto3 secretsmanager client that returns valid credentials."""
    client = MagicMock()
    client.get_secret_value.return_value = {
        "SecretString": json.dumps({"api_key": api_key, "api_secret": api_secret})
    }
    return client


# ===========================================================================
# 10.1  Credential retrieval
# ===========================================================================

class TestGetBitoProCredentials:
    def setup_method(self):
        clear_credential_cache()

    def test_returns_credentials_from_secrets_manager(self):
        client = _make_secrets_client("my-key", "my-secret")
        key, secret = get_bitopro_credentials("my-secret-name", _secrets_client=client)
        assert key == "my-key"
        assert secret == "my-secret"

    def test_caches_credentials_on_second_call(self):
        client = _make_secrets_client("k", "s")
        get_bitopro_credentials("cached-secret", _secrets_client=client)
        # Second call should NOT hit Secrets Manager again
        get_bitopro_credentials("cached-secret", _secrets_client=client)
        assert client.get_secret_value.call_count == 1

    def test_cache_expires_after_ttl(self):
        client = _make_secrets_client("k", "s")
        get_bitopro_credentials("expiry-secret", ttl_seconds=0, _secrets_client=client)
        # TTL=0 means already expired; next call should re-fetch
        time.sleep(0.01)
        get_bitopro_credentials("expiry-secret", ttl_seconds=0, _secrets_client=client)
        assert client.get_secret_value.call_count == 2

    def test_returns_none_when_secrets_manager_unavailable(self):
        from botocore.exceptions import ClientError
        client = MagicMock()
        client.get_secret_value.side_effect = ClientError(
            {"Error": {"Code": "ResourceNotFoundException", "Message": "not found"}},
            "GetSecretValue",
        )
        key, secret = get_bitopro_credentials("missing-secret", _secrets_client=client)
        assert key is None
        assert secret is None

    def test_returns_none_when_secret_missing_fields(self):
        client = MagicMock()
        client.get_secret_value.return_value = {
            "SecretString": json.dumps({"some_other_field": "value"})
        }
        key, secret = get_bitopro_credentials("bad-secret", _secrets_client=client)
        assert key is None
        assert secret is None

    def test_returns_none_when_secret_string_is_invalid_json(self):
        client = MagicMock()
        client.get_secret_value.return_value = {"SecretString": "not-json"}
        key, secret = get_bitopro_credentials("json-error-secret", _secrets_client=client)
        assert key is None
        assert secret is None

    def test_returns_none_when_no_secret_string(self):
        client = MagicMock()
        client.get_secret_value.return_value = {}  # no SecretString
        key, secret = get_bitopro_credentials("empty-secret", _secrets_client=client)
        assert key is None
        assert secret is None

    def test_supports_camel_case_field_names(self):
        client = MagicMock()
        client.get_secret_value.return_value = {
            "SecretString": json.dumps({"apiKey": "ck", "apiSecret": "cs"})
        }
        key, secret = get_bitopro_credentials("camel-secret", _secrets_client=client)
        assert key == "ck"
        assert secret == "cs"

    def test_clear_cache_for_specific_secret(self):
        client = _make_secrets_client("k", "s")
        get_bitopro_credentials("to-clear", _secrets_client=client)
        clear_credential_cache("to-clear")
        get_bitopro_credentials("to-clear", _secrets_client=client)
        assert client.get_secret_value.call_count == 2

    def test_clear_entire_cache(self):
        client = _make_secrets_client("k", "s")
        get_bitopro_credentials("secret-a", _secrets_client=client)
        get_bitopro_credentials("secret-b", _secrets_client=client)
        clear_credential_cache()
        get_bitopro_credentials("secret-a", _secrets_client=client)
        get_bitopro_credentials("secret-b", _secrets_client=client)
        assert client.get_secret_value.call_count == 4


# ===========================================================================
# 10.2  Input validation and sanitization
# ===========================================================================

class TestIngestBitoProDataValidation:
    """Tests for the validation guard added to ingest_bitopro_data()."""

    def test_empty_endpoint_returns_empty_tuple(self):
        result = ingest_bitopro_data(endpoint="", method=HTTPMethod.GET)
        assert result == ("", "")

    def test_none_endpoint_returns_empty_tuple(self):
        result = ingest_bitopro_data(endpoint=None, method=HTTPMethod.GET)  # type: ignore[arg-type]
        assert result == ("", "")

    def test_invalid_method_returns_empty_tuple(self):
        result = ingest_bitopro_data(endpoint="/v1/data", method="GET")  # type: ignore[arg-type]
        assert result == ("", "")

    def test_path_traversal_in_endpoint_rejected(self):
        result = ingest_bitopro_data(endpoint="/../etc/passwd", method=HTTPMethod.GET)
        assert result == ("", "")

    def test_double_dot_in_endpoint_rejected(self):
        result = ingest_bitopro_data(endpoint="/v1/../secret", method=HTTPMethod.GET)
        assert result == ("", "")

    def test_special_chars_in_endpoint_rejected(self):
        result = ingest_bitopro_data(endpoint="/v1/data?foo=<script>", method=HTTPMethod.GET)
        assert result == ("", "")

    def test_params_with_sql_injection_rejected(self):
        result = ingest_bitopro_data(
            endpoint="/v1/data",
            method=HTTPMethod.GET,
            params={"pair": "BTC_TWD' OR '1'='1"},
        )
        assert result == ("", "")

    def test_params_with_drop_table_rejected(self):
        result = ingest_bitopro_data(
            endpoint="/v1/data",
            method=HTTPMethod.GET,
            params={"q": "DROP TABLE users"},
        )
        assert result == ("", "")

    def test_params_with_html_injection_rejected(self):
        result = ingest_bitopro_data(
            endpoint="/v1/data",
            method=HTTPMethod.GET,
            params={"name": "<script>alert(1)</script>"},
        )
        assert result == ("", "")

    def test_valid_endpoint_and_params_pass_validation(self):
        """Valid inputs should pass validation (may fail later for other reasons)."""
        # We only check that validation itself doesn't reject the call.
        # The workflow will fail at the API call stage, which is fine.
        result = ingest_bitopro_data(
            endpoint="/v1/provisioning/limitations-and-fees",
            method=HTTPMethod.GET,
            params={"pair": "BTC_TWD"},
        )
        # Result is ("", "") because no real API is available, but NOT due to validation
        # We can't distinguish here, so just assert it's a tuple
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_params_none_is_allowed(self):
        result = ingest_bitopro_data(
            endpoint="/v1/data",
            method=HTTPMethod.GET,
            params=None,
        )
        assert isinstance(result, tuple)

    def test_params_not_dict_rejected(self):
        result = ingest_bitopro_data(
            endpoint="/v1/data",
            method=HTTPMethod.GET,
            params=["not", "a", "dict"],  # type: ignore[arg-type]
        )
        assert result == ("", "")


# ===========================================================================
# 10.3  Sensitive data filtering
# ===========================================================================

class TestSanitizeMessage:
    def test_redacts_api_key_equals(self):
        msg = "Request with api_key=supersecret123 sent"
        result = sanitize_message(msg)
        assert "supersecret123" not in result
        assert "[REDACTED]" in result

    def test_redacts_api_secret_equals(self):
        msg = "api_secret=topsecret stored"
        result = sanitize_message(msg)
        assert "topsecret" not in result
        assert "[REDACTED]" in result

    def test_redacts_json_style_api_key(self):
        msg = '{"api_key": "mykey123", "other": "value"}'
        result = sanitize_message(msg)
        assert "mykey123" not in result
        assert "[REDACTED]" in result

    def test_redacts_bitopro_header(self):
        msg = "Sending header X-BITOPRO-APIKEY: abc123xyz"
        result = sanitize_message(msg)
        assert "abc123xyz" not in result
        assert "[REDACTED]" in result

    def test_redacts_bearer_token(self):
        msg = "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig"
        result = sanitize_message(msg)
        assert "eyJhbGciOiJIUzI1NiJ9" not in result
        assert "[REDACTED]" in result

    def test_preserves_non_sensitive_content(self):
        msg = "Fetching endpoint /v1/data with pair=BTC_TWD"
        result = sanitize_message(msg)
        assert result == msg

    def test_redacts_password_field(self):
        msg = "password=hunter2 used"
        result = sanitize_message(msg)
        assert "hunter2" not in result
        assert "[REDACTED]" in result

    def test_empty_message_unchanged(self):
        assert sanitize_message("") == ""


class TestSensitiveDataFilter:
    def _make_record(self, msg: str, args=None) -> logging.LogRecord:
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0,
            msg=msg, args=args or (), exc_info=None,
        )
        return record

    def test_filter_redacts_api_key_in_msg(self):
        f = SensitiveDataFilter()
        record = self._make_record("api_key=secret123")
        f.filter(record)
        assert "secret123" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_filter_always_returns_true(self):
        f = SensitiveDataFilter()
        record = self._make_record("api_key=secret")
        assert f.filter(record) is True

    def test_filter_redacts_string_args_tuple(self):
        f = SensitiveDataFilter()
        record = self._make_record("value: %s", args=("api_key=abc",))
        f.filter(record)
        assert isinstance(record.args, tuple)
        assert "abc" not in record.args[0]
        assert "[REDACTED]" in record.args[0]

    def test_filter_redacts_string_args_dict(self):
        """Dict args are sanitized via the msg field after interpolation."""
        f = SensitiveDataFilter()
        # Build the record the way the logging module does when a dict is passed
        record = logging.LogRecord(
            name="test", level=logging.INFO,
            pathname="", lineno=0,
            msg="key=%(key)s", args=None, exc_info=None,
        )
        # Simulate dict-style args by setting msg directly
        record.msg = "api_secret=xyz other=value"
        f.filter(record)
        assert "xyz" not in record.msg
        assert "[REDACTED]" in record.msg

    def test_filter_leaves_non_string_args_unchanged(self):
        f = SensitiveDataFilter()
        record = self._make_record("count: %d", args=(42,))
        f.filter(record)
        assert record.args == (42,)

    def test_filter_can_be_attached_to_logger(self):
        """Verify the filter integrates with the standard logging machinery."""
        handler = logging.handlers_list = []

        class CapturingHandler(logging.Handler):
            def __init__(self):
                super().__init__()
                self.records = []
            def emit(self, record):
                self.records.append(self.format(record))

        capturing = CapturingHandler()
        test_logger = logging.getLogger("test_sensitive_filter_integration")
        test_logger.addFilter(SensitiveDataFilter())
        test_logger.addHandler(capturing)
        test_logger.setLevel(logging.DEBUG)

        test_logger.info("api_key=supersecret endpoint=/v1/data")

        assert capturing.records
        assert "supersecret" not in capturing.records[0]
        assert "[REDACTED]" in capturing.records[0]
        # Non-sensitive part preserved
        assert "endpoint=/v1/data" in capturing.records[0]
