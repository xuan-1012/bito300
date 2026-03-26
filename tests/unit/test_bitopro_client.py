"""
Unit tests for BitoPro API client.

**Validates: Requirements 1.1, 1.2, 1.5, 11.1**
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import requests
from botocore.exceptions import ClientError

from src.utils.bitopro_client import BitoproClient, BitoproClientError


@pytest.fixture
def mock_aws_clients():
    """Create mock AWS clients."""
    mock_clients = Mock()
    mock_clients.get_secret.return_value = {
        'api_key': 'test_api_key',
        'api_secret': 'test_api_secret'
    }
    return mock_clients


@pytest.fixture
def bitopro_client(mock_aws_clients):
    """Create BitoPro client with mocked AWS clients."""
    return BitoproClient(
        aws_clients=mock_aws_clients,
        secret_id='test-secret',
        max_retries=3
    )


class TestBitoproClientInitialization:
    """Test BitoPro client initialization."""
    
    def test_successful_initialization(self, mock_aws_clients):
        """Test successful client initialization with valid credentials."""
        client = BitoproClient(
            aws_clients=mock_aws_clients,
            secret_id='test-secret'
        )
        
        assert client.api_key == 'test_api_key'
        assert client.api_secret == 'test_api_secret'
        assert client.base_url == 'https://api.bitopro.com/v3'
        assert client.timeout == 30
        assert client.max_retries == 3
    
    def test_initialization_with_custom_params(self, mock_aws_clients):
        """Test initialization with custom parameters."""
        client = BitoproClient(
            aws_clients=mock_aws_clients,
            secret_id='custom-secret',
            base_url='https://custom.api.com',
            timeout=60,
            max_retries=5
        )
        
        assert client.base_url == 'https://custom.api.com'
        assert client.timeout == 60
        assert client.max_retries == 5
    
    def test_initialization_missing_api_key(self, mock_aws_clients):
        """Test initialization fails when API key is missing."""
        mock_aws_clients.get_secret.return_value = {
            'api_secret': 'test_secret'
        }
        
        with pytest.raises(BitoproClientError) as exc_info:
            BitoproClient(aws_clients=mock_aws_clients)
        
        assert "api_key" in str(exc_info.value)
    
    def test_initialization_missing_api_secret(self, mock_aws_clients):
        """Test initialization fails when API secret is missing."""
        mock_aws_clients.get_secret.return_value = {
            'api_key': 'test_key'
        }
        
        with pytest.raises(BitoproClientError) as exc_info:
            BitoproClient(aws_clients=mock_aws_clients)
        
        assert "api_secret" in str(exc_info.value)
    
    def test_initialization_secrets_manager_error(self, mock_aws_clients):
        """Test initialization fails when Secrets Manager returns error."""
        mock_aws_clients.get_secret.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException'}},
            'GetSecretValue'
        )
        
        with pytest.raises(BitoproClientError) as exc_info:
            BitoproClient(aws_clients=mock_aws_clients)
        
        assert "Failed to retrieve" in str(exc_info.value)


class TestFetchTransactions:
    """Test fetch_transactions method."""
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_successful_fetch(self, mock_request, bitopro_client):
        """Test successful transaction fetch."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 'tx1', 'amount': 100.0},
            {'id': 'tx2', 'amount': 200.0}
        ]
        mock_request.return_value = mock_response
        
        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 2)
        
        transactions = bitopro_client.fetch_transactions(
            start_time=start_time,
            end_time=end_time,
            limit=1000
        )
        
        assert len(transactions) == 2
        assert transactions[0]['id'] == 'tx1'
        assert transactions[1]['id'] == 'tx2'
        
        # Verify request was made with correct parameters
        mock_request.assert_called_once()
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs['params']['limit'] == 1000
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_fetch_with_default_time_range(self, mock_request, bitopro_client):
        """Test fetch with default time range (last 24 hours)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_request.return_value = mock_response
        
        transactions = bitopro_client.fetch_transactions()
        
        assert transactions == []
        
        # Verify time range parameters were set
        call_kwargs = mock_request.call_args[1]
        assert 'startTime' in call_kwargs['params']
        assert 'endTime' in call_kwargs['params']
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_fetch_with_data_wrapper(self, mock_request, bitopro_client):
        """Test fetch when response has 'data' wrapper."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': [
                {'id': 'tx1', 'amount': 100.0}
            ]
        }
        mock_request.return_value = mock_response
        
        transactions = bitopro_client.fetch_transactions()
        
        assert len(transactions) == 1
        assert transactions[0]['id'] == 'tx1'
    
    @patch('src.utils.bitopro_client.requests.request')
    @patch('src.utils.bitopro_client.time.sleep')
    def test_retry_on_timeout(self, mock_sleep, mock_request, bitopro_client):
        """Test retry logic on timeout."""
        # First two attempts timeout, third succeeds
        mock_request.side_effect = [
            requests.exceptions.Timeout("Connection timeout"),
            requests.exceptions.Timeout("Connection timeout"),
            Mock(status_code=200, json=lambda: [{'id': 'tx1'}])
        ]
        
        transactions = bitopro_client.fetch_transactions()
        
        assert len(transactions) == 1
        assert mock_request.call_count == 3
        assert mock_sleep.call_count == 2  # Backoff after first two failures
    
    @patch('src.utils.bitopro_client.requests.request')
    @patch('src.utils.bitopro_client.time.sleep')
    def test_max_retries_exceeded(self, mock_sleep, mock_request, bitopro_client):
        """Test failure after max retries exceeded."""
        # All attempts timeout
        mock_request.side_effect = requests.exceptions.Timeout("Connection timeout")
        
        with pytest.raises(BitoproClientError) as exc_info:
            bitopro_client.fetch_transactions()
        
        assert "timed out" in str(exc_info.value).lower()
        assert mock_request.call_count == 3  # max_retries
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_rate_limit_error(self, mock_request, bitopro_client):
        """Test handling of rate limit error (429)."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {'Retry-After': '60'}
        mock_request.return_value = mock_response
        
        with pytest.raises(BitoproClientError) as exc_info:
            bitopro_client.fetch_transactions()
        
        assert "rate limit" in str(exc_info.value).lower()
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_authentication_error(self, mock_request, bitopro_client):
        """Test handling of authentication error (401)."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        with pytest.raises(BitoproClientError) as exc_info:
            bitopro_client.fetch_transactions()
        
        assert "authentication" in str(exc_info.value).lower()
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_api_error_response(self, mock_request, bitopro_client):
        """Test handling of API error in response body."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'error': 'Invalid parameters'
        }
        mock_request.return_value = mock_response
        
        with pytest.raises(BitoproClientError) as exc_info:
            bitopro_client.fetch_transactions()
        
        assert "Invalid parameters" in str(exc_info.value)
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_json_decode_error(self, mock_request, bitopro_client):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_request.return_value = mock_response
        
        with pytest.raises(BitoproClientError) as exc_info:
            bitopro_client.fetch_transactions()
        
        assert "parse JSON" in str(exc_info.value)


class TestExponentialBackoff:
    """Test exponential backoff logic."""
    
    @patch('src.utils.bitopro_client.time.sleep')
    def test_backoff_timing(self, mock_sleep, bitopro_client):
        """Test exponential backoff timing."""
        bitopro_client._exponential_backoff(1)
        mock_sleep.assert_called_once_with(2)  # 2^1 = 2 seconds
        
        mock_sleep.reset_mock()
        bitopro_client._exponential_backoff(2)
        mock_sleep.assert_called_once_with(4)  # 2^2 = 4 seconds
        
        mock_sleep.reset_mock()
        bitopro_client._exponential_backoff(3)
        mock_sleep.assert_called_once_with(8)  # 2^3 = 8 seconds


class TestMakeRequest:
    """Test _make_request method."""
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_request_headers(self, mock_request, bitopro_client):
        """Test that request includes correct authentication headers."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_request.return_value = mock_response
        
        bitopro_client._make_request('/test')
        
        call_kwargs = mock_request.call_args[1]
        headers = call_kwargs['headers']
        
        assert 'X-BITOPRO-APIKEY' in headers
        assert headers['X-BITOPRO-APIKEY'] == 'test_api_key'
        assert headers['Content-Type'] == 'application/json'
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_request_timeout(self, mock_request, bitopro_client):
        """Test that request includes timeout."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_request.return_value = mock_response
        
        bitopro_client._make_request('/test')
        
        call_kwargs = mock_request.call_args[1]
        assert call_kwargs['timeout'] == 30
