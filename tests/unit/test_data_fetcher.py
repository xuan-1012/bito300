"""
Unit tests for Data Fetcher Lambda handler.

Tests cover:
- API key retrieval from Secrets Manager
- Transaction validation logic
- S3 storage with mocked boto3
- Retry logic on API failures

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime, timedelta

from src.lambdas.data_fetcher.handler import (
    lambda_handler,
    _parse_event_parameters,
    _convert_to_transaction,
    _store_to_s3,
)
from src.common.models import Transaction
from src.utils.bitopro_client import BitoproClientError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def mock_aws_clients():
    """Mock AWSClients with pre-configured S3 and Secrets Manager."""
    clients = Mock()
    clients.get_secret.return_value = {
        'api_key': 'test_api_key',
        'api_secret': 'test_api_secret',
    }
    clients.s3 = Mock()
    clients.s3.put_object.return_value = {}
    return clients


@pytest.fixture
def sample_raw_transaction():
    """A minimal valid raw transaction dict as returned by BitoPro API."""
    return {
        'transaction_id': 'tx_001',
        'timestamp': '2024-01-15T10:30:00',
        'from_account': 'acc_sender',
        'to_account': 'acc_receiver',
        'amount': '250.5',
        'currency': 'BTC',
        'transaction_type': 'transfer',
        'status': 'completed',
        'fee': '0.5',
    }


@pytest.fixture
def sample_event():
    """A minimal valid Lambda event."""
    return {
        'start_time': '2024-01-15T00:00:00',
        'end_time': '2024-01-15T23:59:59',
        'limit': 100,
    }


@pytest.fixture
def lambda_context():
    """Minimal Lambda context mock."""
    ctx = Mock()
    ctx.function_name = 'data-fetcher'
    ctx.aws_request_id = 'test-request-id'
    return ctx


# ---------------------------------------------------------------------------
# Tests: API key retrieval from Secrets Manager (Requirement 1.1)
# ---------------------------------------------------------------------------

class TestApiKeyRetrieval:
    """Test that the handler retrieves the BitoPro API key from Secrets Manager."""

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_handler_retrieves_api_key_from_secrets_manager(
        self, mock_client_cls, mock_get_clients, mock_aws_clients, sample_event, lambda_context
    ):
        """Handler must initialise BitoproClient with the secret_id from env."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = []
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'BITOPRO_SECRET_ID': 'my-secret', 'RAW_DATA_BUCKET': 'bucket'}):
            lambda_handler(sample_event, lambda_context)

        mock_client_cls.assert_called_once_with(
            aws_clients=mock_aws_clients,
            secret_id='my-secret',
        )

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_handler_uses_default_secret_id_when_env_not_set(
        self, mock_client_cls, mock_get_clients, mock_aws_clients, sample_event, lambda_context
    ):
        """Handler falls back to 'bitopro-api-key' when env var is absent."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = []
        mock_client_cls.return_value = mock_client

        env = {'RAW_DATA_BUCKET': 'bucket'}
        # Ensure BITOPRO_SECRET_ID is not set
        with patch.dict('os.environ', env, clear=False):
            import os
            os.environ.pop('BITOPRO_SECRET_ID', None)
            lambda_handler(sample_event, lambda_context)

        call_kwargs = mock_client_cls.call_args[1]
        assert call_kwargs['secret_id'] == 'bitopro-api-key'

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_handler_returns_500_when_secrets_manager_fails(
        self, mock_client_cls, mock_get_clients, mock_aws_clients, sample_event, lambda_context
    ):
        """Handler returns 500 when BitoproClient raises on credential retrieval."""
        mock_get_clients.return_value = mock_aws_clients
        mock_client_cls.side_effect = BitoproClientError('Cannot retrieve secret')

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'bucket'}):
            response = lambda_handler(sample_event, lambda_context)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body


# ---------------------------------------------------------------------------
# Tests: Transaction validation logic (Requirements 1.3, 2.x)
# ---------------------------------------------------------------------------

class TestTransactionValidation:
    """Test that the handler validates each transaction correctly."""

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_valid_transactions_are_stored(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """All valid transactions should be included in the S3 payload."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler({}, lambda_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['valid_count'] == 1
        assert body['invalid_count'] == 0

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_invalid_transactions_are_excluded(
        self, mock_client_cls, mock_get_clients, mock_aws_clients, lambda_context
    ):
        """Transactions with missing required fields should be excluded."""
        mock_get_clients.return_value = mock_aws_clients

        invalid_txn = {
            'transaction_id': '',   # empty id → invalid
            'timestamp': '2024-01-15T10:00:00',
            'from_account': 'acc_a',
            'to_account': 'acc_b',
            'amount': '100',
            'currency': 'ETH',
            'transaction_type': 'transfer',
            'status': 'completed',
            'fee': '0',
        }

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [invalid_txn]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler({}, lambda_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['valid_count'] == 0
        assert body['invalid_count'] == 1

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_mixed_valid_and_invalid_transactions(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """Valid and invalid transactions are counted separately."""
        mock_get_clients.return_value = mock_aws_clients

        invalid_txn = dict(sample_raw_transaction)
        invalid_txn['transaction_id'] = 'tx_002'
        invalid_txn['amount'] = '-10'   # negative amount → invalid after conversion

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction, invalid_txn]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler({}, lambda_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['transaction_count'] == 2
        assert body['valid_count'] == 1
        assert body['invalid_count'] == 1

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_zero_transactions_returns_success(
        self, mock_client_cls, mock_get_clients, mock_aws_clients, lambda_context
    ):
        """Handler succeeds even when API returns no transactions."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = []
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler({}, lambda_context)

        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['valid_count'] == 0
        assert body['invalid_count'] == 0


# ---------------------------------------------------------------------------
# Tests: S3 storage with mocked boto3 (Requirement 1.4, 9.1)
# ---------------------------------------------------------------------------

class TestS3Storage:
    """Test that validated transactions are stored to S3 correctly."""

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_data_stored_to_correct_bucket(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """Handler stores data to the bucket specified by RAW_DATA_BUCKET env var."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'my-raw-bucket'}):
            lambda_handler({}, lambda_context)

        put_call = mock_aws_clients.s3.put_object.call_args
        assert put_call[1]['Bucket'] == 'my-raw-bucket'

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_s3_key_follows_path_pattern(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """S3 key must follow the raw-data/{timestamp}.json pattern (Requirement 9.1)."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            lambda_handler({}, lambda_context)

        put_call = mock_aws_clients.s3.put_object.call_args
        key = put_call[1]['Key']
        assert key.startswith('raw-data/')
        assert key.endswith('.json')

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_s3_uses_server_side_encryption(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """S3 put_object must use AES256 server-side encryption (Requirement 9.6)."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            lambda_handler({}, lambda_context)

        put_call = mock_aws_clients.s3.put_object.call_args
        assert put_call[1].get('ServerSideEncryption') == 'AES256'

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_s3_content_type_is_json(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """S3 object must be stored with application/json content type."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            lambda_handler({}, lambda_context)

        put_call = mock_aws_clients.s3.put_object.call_args
        assert put_call[1].get('ContentType') == 'application/json'

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_response_contains_s3_uri(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_raw_transaction, lambda_context
    ):
        """Response body must include the s3_uri of the stored data."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = [sample_raw_transaction]
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler({}, lambda_context)

        body = json.loads(response['body'])
        assert 's3_uri' in body
        assert body['s3_uri'].startswith('s3://test-bucket/raw-data/')

    def test_store_to_s3_helper_returns_correct_uri(self, mock_aws_clients):
        """_store_to_s3 returns the correct s3:// URI."""
        uri = _store_to_s3(
            aws_clients=mock_aws_clients,
            bucket='my-bucket',
            key='raw-data/20240115_120000.json',
            data=[{'id': 'tx1'}],
        )
        assert uri == 's3://my-bucket/raw-data/20240115_120000.json'

    def test_store_to_s3_raises_on_s3_error(self, mock_aws_clients):
        """_store_to_s3 propagates S3 exceptions."""
        mock_aws_clients.s3.put_object.side_effect = Exception('S3 unavailable')

        with pytest.raises(Exception, match='S3 unavailable'):
            _store_to_s3(
                aws_clients=mock_aws_clients,
                bucket='my-bucket',
                key='raw-data/test.json',
                data=[],
            )


# ---------------------------------------------------------------------------
# Tests: Retry logic on API failures (Requirement 1.5, 11.1)
# ---------------------------------------------------------------------------

class TestRetryLogic:
    """Test that the handler handles BitoPro API failures via BitoproClient retry."""

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_handler_returns_500_on_bitopro_error(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_event, lambda_context
    ):
        """Handler returns 500 when BitoproClient raises BitoproClientError."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.side_effect = BitoproClientError(
            'Request timed out after 3 attempts'
        )
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler(sample_event, lambda_context)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert body['error'] == 'BitoPro API error'

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_handler_returns_500_on_unexpected_error(
        self, mock_client_cls, mock_get_clients, mock_aws_clients,
        sample_event, lambda_context
    ):
        """Handler returns 500 on any unexpected exception."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.side_effect = RuntimeError('Unexpected crash')
        mock_client_cls.return_value = mock_client

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            response = lambda_handler(sample_event, lambda_context)

        assert response['statusCode'] == 500
        body = json.loads(response['body'])
        assert 'error' in body

    @patch('src.lambdas.data_fetcher.handler.get_aws_clients')
    @patch('src.lambdas.data_fetcher.handler.BitoproClient')
    def test_bitopro_client_receives_correct_time_range(
        self, mock_client_cls, mock_get_clients, mock_aws_clients, lambda_context
    ):
        """Handler passes the parsed time range to BitoproClient.fetch_transactions."""
        mock_get_clients.return_value = mock_aws_clients

        mock_client = Mock()
        mock_client.fetch_transactions.return_value = []
        mock_client_cls.return_value = mock_client

        event = {
            'start_time': '2024-03-01T08:00:00',
            'end_time': '2024-03-01T20:00:00',
            'limit': 500,
        }

        with patch.dict('os.environ', {'RAW_DATA_BUCKET': 'test-bucket'}):
            lambda_handler(event, lambda_context)

        call_kwargs = mock_client.fetch_transactions.call_args[1]
        assert call_kwargs['start_time'] == datetime(2024, 3, 1, 8, 0, 0)
        assert call_kwargs['end_time'] == datetime(2024, 3, 1, 20, 0, 0)
        assert call_kwargs['limit'] == 500


# ---------------------------------------------------------------------------
# Tests: _parse_event_parameters helper
# ---------------------------------------------------------------------------

class TestParseEventParameters:
    """Test the event parameter parsing helper."""

    def test_parses_valid_start_and_end_time(self):
        event = {
            'start_time': '2024-06-01T00:00:00',
            'end_time': '2024-06-01T12:00:00',
            'limit': 200,
        }
        start, end, limit = _parse_event_parameters(event)
        assert start == datetime(2024, 6, 1, 0, 0, 0)
        assert end == datetime(2024, 6, 1, 12, 0, 0)
        assert limit == 200

    def test_defaults_to_last_24_hours_when_times_absent(self):
        before = datetime.now()
        start, end, limit = _parse_event_parameters({})
        after = datetime.now()

        assert before - timedelta(days=1, seconds=1) <= start <= after
        assert before <= end <= after
        assert limit == 1000

    def test_invalid_start_time_uses_default(self):
        event = {'start_time': 'not-a-date', 'end_time': '2024-01-01T00:00:00'}
        start, end, limit = _parse_event_parameters(event)
        # Should not raise; start falls back to default (roughly 24h before end)
        assert isinstance(start, datetime)

    def test_invalid_limit_uses_default(self):
        _, _, limit = _parse_event_parameters({'limit': 'bad'})
        assert limit == 1000

    def test_negative_limit_uses_default(self):
        _, _, limit = _parse_event_parameters({'limit': -5})
        assert limit == 1000

    def test_zero_limit_uses_default(self):
        _, _, limit = _parse_event_parameters({'limit': 0})
        assert limit == 1000


# ---------------------------------------------------------------------------
# Tests: _convert_to_transaction helper
# ---------------------------------------------------------------------------

class TestConvertToTransaction:
    """Test the raw dict → Transaction conversion helper."""

    def test_converts_valid_dict(self, sample_raw_transaction):
        txn = _convert_to_transaction(sample_raw_transaction)
        assert isinstance(txn, Transaction)
        assert txn.transaction_id == 'tx_001'
        assert txn.amount == 250.5
        assert txn.currency == 'BTC'

    def test_handles_alternative_field_names(self):
        """BitoPro may return 'id', 'from', 'to' instead of longer names."""
        raw = {
            'id': 'tx_alt',
            'timestamp': '2024-01-01T00:00:00',
            'from': 'acc_a',
            'to': 'acc_b',
            'amount': '50',
            'currency': 'ETH',
            'type': 'transfer',
            'status': 'completed',
            'fee': '0',
        }
        txn = _convert_to_transaction(raw)
        assert txn.transaction_id == 'tx_alt'
        assert txn.from_account == 'acc_a'
        assert txn.to_account == 'acc_b'

    def test_handles_unix_timestamp_in_milliseconds(self):
        """Numeric timestamps (ms) should be converted to datetime."""
        raw = {
            'transaction_id': 'tx_ms',
            'timestamp': 1705312200000,  # milliseconds
            'from_account': 'acc_a',
            'to_account': 'acc_b',
            'amount': '10',
            'currency': 'USDT',
            'transaction_type': 'transfer',
            'status': 'completed',
            'fee': '0',
        }
        txn = _convert_to_transaction(raw)
        assert isinstance(txn.timestamp, datetime)

    def test_handles_iso_timestamp_with_z_suffix(self):
        """ISO timestamps ending in 'Z' should be parsed correctly."""
        raw = {
            'transaction_id': 'tx_z',
            'timestamp': '2024-01-15T10:30:00Z',
            'from_account': 'acc_a',
            'to_account': 'acc_b',
            'amount': '75',
            'currency': 'BTC',
            'transaction_type': 'deposit',
            'status': 'completed',
            'fee': '0',
        }
        txn = _convert_to_transaction(raw)
        assert isinstance(txn.timestamp, datetime)
