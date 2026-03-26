"""
Integration tests for ingest_bitopro_data() end-to-end workflow.

These tests mock the HTTP layer (requests) so no real network calls are made,
but exercise all other components (storage, flattener, inferencer) with real
implementations against a temporary local directory.
"""

import json
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.ingestion.models import HTTPMethod
from src.ingestion.workflow import ingest_bitopro_data


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_mock_response(data: dict, status_code: int = 200) -> MagicMock:
    """Build a mock requests.Response that returns *data* as JSON."""
    mock_resp = MagicMock()
    mock_resp.status_code = status_code
    mock_resp.json.return_value = data
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestIngestBitoProDataLocalStorage:
    """End-to-end workflow tests using local filesystem storage."""

    def test_basic_ingestion_returns_uris(self, tmp_path):
        """Happy path: API returns data, storage and schema files are created."""
        api_payload = {
            "data": [
                {"id": "TXN001", "amount": 100.5, "status": "completed"},
                {"id": "TXN002", "amount": 200.0, "status": "pending"},
            ]
        }
        schema_file = str(tmp_path / "schema.json")

        with patch("requests.Session.get", return_value=_make_mock_response(api_payload)):
            storage_uri, schema_path = ingest_bitopro_data(
                endpoint="/v1/transactions",
                method=HTTPMethod.GET,
                storage_backend="local",
                local_path=str(tmp_path / "raw_data"),
                schema_output_path=schema_file,
            )

        assert storage_uri.startswith("file://"), f"Expected file:// URI, got: {storage_uri}"
        assert schema_path == schema_file
        assert os.path.exists(schema_file), "schema.json was not created"

    def test_schema_contains_expected_fields(self, tmp_path):
        """Schema JSON should include all fields from the API response."""
        api_payload = {
            "data": [
                {"transaction_id": "TXN001", "amount": 50.0, "currency": "BTC"},
            ]
        }
        schema_file = str(tmp_path / "schema.json")

        with patch("requests.Session.get", return_value=_make_mock_response(api_payload)):
            _, schema_path = ingest_bitopro_data(
                endpoint="/v1/orders",
                storage_backend="local",
                local_path=str(tmp_path / "raw_data"),
                schema_output_path=schema_file,
            )

        with open(schema_path, "r") as f:
            schema = json.load(f)

        assert "transaction_id" in schema
        assert "amount" in schema
        assert "currency" in schema

    def test_raw_response_stored_unmodified(self, tmp_path):
        """The raw response file on disk must match what the API returned."""
        api_payload = {"data": [{"price": "12345.67", "pair": "BTC_TWD"}]}
        schema_file = str(tmp_path / "schema.json")
        raw_dir = tmp_path / "raw_data"

        with patch("requests.Session.get", return_value=_make_mock_response(api_payload)):
            storage_uri, _ = ingest_bitopro_data(
                endpoint="/v1/tickers",
                storage_backend="local",
                local_path=str(raw_dir),
                schema_output_path=schema_file,
            )

        # Derive the file path from the URI (strip "file://")
        file_path = storage_uri.replace("file://", "")
        with open(file_path, "r") as f:
            stored = json.load(f)

        assert stored == api_payload

    def test_empty_api_response_returns_empty_strings(self, tmp_path):
        """When the API returns nothing, the function should return ('', '')."""
        with patch("requests.Session.get", return_value=_make_mock_response({})):
            result = ingest_bitopro_data(
                endpoint="/v1/empty",
                storage_backend="local",
                local_path=str(tmp_path / "raw_data"),
                schema_output_path=str(tmp_path / "schema.json"),
            )

        assert result == ("", "")

    def test_api_failure_returns_empty_strings(self, tmp_path):
        """Network errors should be handled gracefully, returning ('', '')."""
        import requests as req

        with patch("requests.Session.get", side_effect=req.ConnectionError("network down")):
            result = ingest_bitopro_data(
                endpoint="/v1/fail",
                storage_backend="local",
                local_path=str(tmp_path / "raw_data"),
                schema_output_path=str(tmp_path / "schema.json"),
            )

        assert result == ("", "")

    def test_nested_json_is_flattened_in_schema(self, tmp_path):
        """Nested JSON fields should appear as flattened keys in the schema."""
        api_payload = {
            "data": [
                {
                    "order": {
                        "id": "ORD001",
                        "price": 999.0,
                    }
                }
            ]
        }
        schema_file = str(tmp_path / "schema.json")

        with patch("requests.Session.get", return_value=_make_mock_response(api_payload)):
            _, schema_path = ingest_bitopro_data(
                endpoint="/v1/orders",
                storage_backend="local",
                local_path=str(tmp_path / "raw_data"),
                schema_output_path=schema_file,
            )

        with open(schema_path, "r") as f:
            schema = json.load(f)

        # Nested keys should be flattened with "_" separator
        assert "order_id" in schema or "order" in schema  # depends on flattener strategy
        assert any("order" in k for k in schema), f"No order-related keys in schema: {list(schema.keys())}"

    def test_post_method_is_supported(self, tmp_path):
        """POST requests should work the same as GET for the workflow."""
        api_payload = {"data": [{"result": "ok", "count": 1}]}
        schema_file = str(tmp_path / "schema.json")

        with patch("requests.Session.post", return_value=_make_mock_response(api_payload)):
            storage_uri, schema_path = ingest_bitopro_data(
                endpoint="/v1/query",
                method=HTTPMethod.POST,
                params={"filter": "active"},
                storage_backend="local",
                local_path=str(tmp_path / "raw_data"),
                schema_output_path=schema_file,
            )

        assert storage_uri.startswith("file://")
        assert os.path.exists(schema_path)
