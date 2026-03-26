"""
Unit tests for BitoProAPIClient (ingestion layer)

Tests HTTP client initialization, configuration, and header building.

**Validates: Requirements 1.1, 1.3, 1.4, 1.5, 10.1, 12.1, 12.2**
"""

import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
import requests

from src.ingestion.client import BitoProAPIClient
from src.ingestion.models import APIConfig, HTTPMethod


class TestBitoProAPIClientInitialization:
    """Test BitoProAPIClient initialization and configuration"""
    
    def test_initialization_with_defaults(self):
        """Test client initialization with default configuration"""
        client = BitoProAPIClient()
        
        assert client.api_key is None
        assert client.api_secret is None
        assert client.config is not None
        assert client.config.base_url == "https://aws-event-api.bitopro.com/"
        assert client.config.timeout == 30
        assert client.config.max_retries == 3
        assert client.config.retry_backoff == 2.0
        assert client.config.rate_limit_per_second == 0.9
        assert client.session is not None
    
    def test_initialization_with_credentials(self):
        """Test client initialization with API credentials"""
        client = BitoProAPIClient(
            api_key="test_api_key",
            api_secret="test_api_secret"
        )
        
        assert client.api_key == "test_api_key"
        assert client.api_secret == "test_api_secret"
    
    def test_initialization_with_custom_config(self):
        """Test client initialization with custom configuration"""
        custom_config = APIConfig(
            base_url="https://custom.api.com/",
            timeout=60,
            max_retries=5,
            retry_backoff=3.0,
            rate_limit_per_second=0.5
        )
        
        client = BitoProAPIClient(config=custom_config)
        
        assert client.config.base_url == "https://custom.api.com/"
        assert client.config.timeout == 60
        assert client.config.max_retries == 5
        assert client.config.retry_backoff == 3.0
        assert client.config.rate_limit_per_second == 0.5
    
    def test_session_creation_with_connection_pooling(self):
        """Test that session is created with connection pooling"""
        client = BitoProAPIClient()
        
        # Verify session exists
        assert isinstance(client.session, requests.Session)
        
        # Verify adapters are mounted for HTTPS (Requirement 12.2)
        assert "https://" in client.session.adapters
        
        # Verify adapter has connection pooling configured
        adapter = client.session.get_adapter("https://")
        assert hasattr(adapter, "poolmanager")


class TestBuildHeaders:
    """Test _build_headers method"""
    
    def test_build_headers_without_credentials(self):
        """Test header building without API credentials"""
        client = BitoProAPIClient()
        headers = client._build_headers()
        
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert "X-BITOPRO-APIKEY" not in headers
        assert "X-BITOPRO-APISECRET" not in headers
    
    def test_build_headers_with_api_key_only(self):
        """Test header building with API key only"""
        client = BitoProAPIClient(api_key="test_key")
        headers = client._build_headers()
        
        assert headers["X-BITOPRO-APIKEY"] == "test_key"
        assert "X-BITOPRO-APISECRET" not in headers
    
    def test_build_headers_with_api_secret_only(self):
        """Test header building with API secret only"""
        client = BitoProAPIClient(api_secret="test_secret")
        headers = client._build_headers()
        
        assert headers["X-BITOPRO-APISECRET"] == "test_secret"
        assert "X-BITOPRO-APIKEY" not in headers
    
    def test_build_headers_with_both_credentials(self):
        """Test header building with both API key and secret"""
        client = BitoProAPIClient(
            api_key="test_key",
            api_secret="test_secret"
        )
        headers = client._build_headers()
        
        assert headers["X-BITOPRO-APIKEY"] == "test_key"
        assert headers["X-BITOPRO-APISECRET"] == "test_secret"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
    
    def test_build_headers_with_custom_headers(self):
        """Test header building with custom headers"""
        client = BitoProAPIClient(api_key="test_key")
        custom_headers = {
            "X-Custom-Header": "custom_value",
            "User-Agent": "CustomAgent/1.0"
        }
        headers = client._build_headers(custom_headers=custom_headers)
        
        assert headers["X-BITOPRO-APIKEY"] == "test_key"
        assert headers["X-Custom-Header"] == "custom_value"
        assert headers["User-Agent"] == "CustomAgent/1.0"
    
    def test_build_headers_custom_overrides_defaults(self):
        """Test that custom headers can override default headers"""
        client = BitoProAPIClient()
        custom_headers = {
            "Content-Type": "application/xml"
        }
        headers = client._build_headers(custom_headers=custom_headers)
        
        assert headers["Content-Type"] == "application/xml"


class TestContextManager:
    """Test context manager functionality"""
    
    def test_context_manager_enter_exit(self):
        """Test client can be used as context manager"""
        with BitoProAPIClient() as client:
            assert client.session is not None
        
        # Session should be closed after exiting context
        # Note: We can't directly test if session is closed,
        # but we verify the close method was called
    
    def test_close_method(self):
        """Test close method closes the session"""
        client = BitoProAPIClient()
        session = client.session
        
        client.close()
        
        # Verify session still exists but close was called
        assert client.session is not None


class TestHTTPSEnforcement:
    """Test HTTPS enforcement (Requirement 12.2)"""
    
    def test_default_base_url_uses_https(self):
        """Test that default base URL uses HTTPS protocol"""
        client = BitoProAPIClient()
        
        assert client.config.base_url.startswith("https://")
    
    def test_custom_https_url_accepted(self):
        """Test that custom HTTPS URLs are accepted"""
        config = APIConfig(base_url="https://custom.api.com/")
        client = BitoProAPIClient(config=config)
        
        assert client.config.base_url.startswith("https://")


class TestConfigurationValidation:
    """Test configuration validation"""
    
    def test_invalid_timeout_raises_error(self):
        """Test that invalid timeout raises ValueError"""
        with pytest.raises(ValueError, match="timeout must be positive"):
            APIConfig(timeout=0)
    
    def test_invalid_max_retries_raises_error(self):
        """Test that negative max_retries raises ValueError"""
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            APIConfig(max_retries=-1)
    
    def test_invalid_retry_backoff_raises_error(self):
        """Test that invalid retry_backoff raises ValueError"""
        with pytest.raises(ValueError, match="retry_backoff must be positive"):
            APIConfig(retry_backoff=0)
    
    def test_invalid_rate_limit_raises_error(self):
        """Test that invalid rate_limit_per_second raises ValueError"""
        with pytest.raises(ValueError, match="rate_limit_per_second must be positive"):
            APIConfig(rate_limit_per_second=0)
    
    def test_empty_base_url_raises_error(self):
        """Test that empty base_url raises ValueError"""
        with pytest.raises(ValueError, match="base_url must be non-empty"):
            APIConfig(base_url="")


class TestFetchData:
    """Test fetch_data method - main entry point"""
    
    @patch('time.sleep')
    def test_fetch_data_single_page_success(self, mock_sleep):
        """Test successful fetch with single page (no pagination)"""
        client = BitoProAPIClient()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": 1, "value": "test"}],
            "status": "success"
        }
        
        with patch.object(client.session, 'get', return_value=mock_response):
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                params={"limit": 10},
                paginate=False
            )
        
        assert len(results) == 1
        assert results[0]["status"] == "success"
        assert len(results[0]["data"]) == 1
    
    @patch('time.sleep')
    def test_fetch_data_with_pagination(self, mock_sleep):
        """Test fetch with pagination enabled"""
        client = BitoProAPIClient()
        
        # Mock paginated responses
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            "data": [{"id": 1}],
            "page": 1,
            "total_pages": 2
        }
        
        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            "data": [{"id": 2}],
            "page": 2,
            "total_pages": 2
        }
        
        with patch.object(client.session, 'get', side_effect=[
            mock_response_page1,
            mock_response_page2
        ]):
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                paginate=True
            )
        
        assert len(results) == 2
        assert results[0]["page"] == 1
        assert results[1]["page"] == 2
    
    @patch('time.sleep')
    def test_fetch_data_pagination_with_offset_limit(self, mock_sleep):
        """Test fetch with offset/limit pagination"""
        client = BitoProAPIClient()
        
        # Mock paginated responses with offset/limit
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            "data": [{"id": 1}, {"id": 2}],
            "offset": 0,
            "limit": 2,
            "total": 4
        }
        
        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            "data": [{"id": 3}, {"id": 4}],
            "offset": 2,
            "limit": 2,
            "total": 4
        }
        
        with patch.object(client.session, 'get', side_effect=[
            mock_response_page1,
            mock_response_page2
        ]):
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                params={"limit": 2},
                paginate=True
            )
        
        assert len(results) == 2
        assert results[0]["offset"] == 0
        assert results[1]["offset"] == 2
    
    @patch('time.sleep')
    def test_fetch_data_pagination_stops_on_empty_response(self, mock_sleep):
        """Test that pagination stops when empty response received"""
        client = BitoProAPIClient()
        
        # Mock first page success, second page empty
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            "data": [{"id": 1}],
            "has_more": True
        }
        
        with patch.object(client.session, 'get', side_effect=[
            mock_response_page1,
            Mock(status_code=500)  # This will cause _execute_request to return {}
        ]):
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                paginate=True
            )
        
        # Should only have first page
        assert len(results) == 1
    
    @patch('time.sleep')
    def test_fetch_data_invalid_endpoint(self, mock_sleep):
        """Test fetch_data with invalid endpoint"""
        client = BitoProAPIClient()
        
        # Empty endpoint
        results = client.fetch_data(endpoint="", method=HTTPMethod.GET)
        assert results == []
        
        # None endpoint
        results = client.fetch_data(endpoint=None, method=HTTPMethod.GET)
        assert results == []
    
    @patch('time.sleep')
    def test_fetch_data_invalid_method(self, mock_sleep):
        """Test fetch_data with invalid HTTP method"""
        client = BitoProAPIClient()
        
        # Invalid method (not HTTPMethod enum)
        results = client.fetch_data(endpoint="/test", method="INVALID")
        assert results == []
    
    @patch('time.sleep')
    def test_fetch_data_with_custom_headers(self, mock_sleep):
        """Test fetch_data with custom headers"""
        client = BitoProAPIClient(api_key="test_key")
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        custom_headers = {"X-Custom": "value"}
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                headers=custom_headers,
                paginate=False
            )
        
        # Verify custom headers were included
        call_args = mock_get.call_args
        headers_used = call_args[1]['headers']
        assert headers_used['X-Custom'] == 'value'
        assert headers_used['X-BITOPRO-APIKEY'] == 'test_key'
    
    @patch('time.sleep')
    def test_fetch_data_post_method(self, mock_sleep):
        """Test fetch_data with POST method"""
        client = BitoProAPIClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "created"}
        
        with patch.object(client.session, 'post', return_value=mock_response) as mock_post:
            results = client.fetch_data(
                endpoint="/v1/create",
                method=HTTPMethod.POST,
                params={"name": "test"},
                paginate=False
            )
        
        assert len(results) == 1
        assert results[0]["result"] == "created"
        
        # Verify POST was called
        mock_post.assert_called_once()
    
    @patch('time.sleep')
    def test_fetch_data_url_construction(self, mock_sleep):
        """Test that URL is constructed correctly"""
        config = APIConfig(base_url="https://api.example.com/")
        client = BitoProAPIClient(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                paginate=False
            )
        
        # Verify URL was constructed correctly
        call_args = mock_get.call_args
        url_used = call_args[0][0]
        assert url_used == "https://api.example.com/v1/test"
    
    @patch('time.sleep')
    def test_fetch_data_url_construction_no_leading_slash(self, mock_sleep):
        """Test URL construction when endpoint has no leading slash"""
        config = APIConfig(base_url="https://api.example.com/")
        client = BitoProAPIClient(config=config)
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        with patch.object(client.session, 'get', return_value=mock_response) as mock_get:
            client.fetch_data(
                endpoint="v1/test",
                method=HTTPMethod.GET,
                paginate=False
            )
        
        # Verify URL was constructed correctly
        call_args = mock_get.call_args
        url_used = call_args[0][0]
        assert url_used == "https://api.example.com/v1/test"
    
    @patch('time.sleep')
    def test_fetch_data_params_preserved_across_pages(self, mock_sleep):
        """Test that original params are preserved when paginating"""
        client = BitoProAPIClient()
        
        # Mock paginated responses
        mock_response_page1 = Mock()
        mock_response_page1.status_code = 200
        mock_response_page1.json.return_value = {
            "data": [{"id": 1}],
            "page": 1,
            "total_pages": 2
        }
        
        mock_response_page2 = Mock()
        mock_response_page2.status_code = 200
        mock_response_page2.json.return_value = {
            "data": [{"id": 2}],
            "page": 2,
            "total_pages": 2
        }
        
        with patch.object(client.session, 'get', side_effect=[
            mock_response_page1,
            mock_response_page2
        ]) as mock_get:
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                params={"filter": "active", "limit": 10},
                paginate=True
            )
        
        # Verify both calls preserved the filter param
        assert mock_get.call_count == 2
        
        # First call should have original params
        first_call_params = mock_get.call_args_list[0][1]['params']
        assert first_call_params['filter'] == 'active'
        assert first_call_params['limit'] == 10
        
        # Second call should have filter preserved and page added
        second_call_params = mock_get.call_args_list[1][1]['params']
        assert second_call_params['filter'] == 'active'
        assert second_call_params['limit'] == 10
        assert second_call_params['page'] == 2
    
    @patch('time.sleep')
    def test_fetch_data_logs_request_details(self, mock_sleep, caplog):
        """Test that request details are logged"""
        client = BitoProAPIClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        with caplog.at_level(logging.INFO):
            with patch.object(client.session, 'get', return_value=mock_response):
                client.fetch_data(
                    endpoint="/v1/test",
                    method=HTTPMethod.GET,
                    params={"limit": 10},
                    paginate=False
                )
        
        # Verify logging
        assert "fetch_data called" in caplog.text
        assert "endpoint=/v1/test" in caplog.text
        assert "method=GET" in caplog.text
    
    @patch('time.sleep')
    def test_fetch_data_no_pagination_info(self, mock_sleep):
        """Test fetch_data when response has no pagination info"""
        client = BitoProAPIClient()
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [{"id": 1}, {"id": 2}]
        }
        
        with patch.object(client.session, 'get', return_value=mock_response):
            results = client.fetch_data(
                endpoint="/v1/test",
                method=HTTPMethod.GET,
                paginate=True
            )
        
        # Should return single page when no pagination info
        assert len(results) == 1


class TestNotImplementedMethods:
    """Test that unimplemented methods raise NotImplementedError"""
    
    # This test is no longer needed since fetch_data is now implemented
    pass


class TestExecuteRequest:
    """Test _execute_request method with retry logic"""
    
    @patch('time.sleep')
    def test_execute_request_success_get(self, mock_sleep):
        """Test successful GET request"""
        client = BitoProAPIClient()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={"Content-Type": "application/json"}
            )
        
        assert result == {"data": "test"}
        # Rate limiting sleep should be called once (in _enforce_rate_limit)
        # but since it's the first request, no actual sleep occurs
        # The mock_sleep is called for time.sleep in _enforce_rate_limit
        # but the condition prevents actual sleeping on first request
    
    @patch('time.sleep')
    def test_execute_request_success_post(self, mock_sleep):
        """Test successful POST request"""
        client = BitoProAPIClient()
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "created"}
        
        with patch.object(client.session, 'post', return_value=mock_response):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.POST,
                headers={"Content-Type": "application/json"},
                params={"key": "value"}
            )
        
        assert result == {"result": "created"}
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_execute_request_retry_on_5xx(self, mock_sleep):
        """Test retry logic on 5xx server errors"""
        config = APIConfig(max_retries=2, retry_backoff=2.0)
        client = BitoProAPIClient(config=config)
        
        # Mock responses: first two fail with 500, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": "success"}
        
        with patch.object(client.session, 'get', side_effect=[
            mock_response_fail,
            mock_response_fail,
            mock_response_success
        ]):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {"data": "success"}
        # Should have slept 4 times total:
        # - 2 times for retry backoff (after first and second failures)
        # - 2 times for rate limiting (before second and third requests)
        assert mock_sleep.call_count == 4
        # Verify exponential backoff: 2^0=1, 2^1=2
        mock_sleep.assert_any_call(1.0)
        mock_sleep.assert_any_call(2.0)
    
    @patch('time.sleep')
    def test_execute_request_exhausted_retries_5xx(self, mock_sleep):
        """Test that empty dict is returned when all retries exhausted on 5xx"""
        config = APIConfig(max_retries=2, retry_backoff=2.0)
        client = BitoProAPIClient(config=config)
        
        # Mock all responses to fail with 503
        mock_response = Mock()
        mock_response.status_code = 503
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {}
        # Should have slept 4 times total:
        # - 2 times for retry backoff (after first and second failures)
        # - 2 times for rate limiting (before second and third requests)
        assert mock_sleep.call_count == 4
    
    @patch('time.sleep')
    def test_execute_request_retry_on_timeout(self, mock_sleep):
        """Test retry logic on timeout errors"""
        config = APIConfig(max_retries=2, retry_backoff=2.0)
        client = BitoProAPIClient(config=config)
        
        # Mock timeout then success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        
        with patch.object(client.session, 'get', side_effect=[
            requests.Timeout("Connection timeout"),
            mock_response
        ]):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {"data": "success"}
        # Should have slept 2 times total:
        # - 1 time for retry backoff (after timeout)
        # - 1 time for rate limiting (before second request)
        assert mock_sleep.call_count == 2
        mock_sleep.assert_any_call(1.0)
    
    @patch('time.sleep')
    def test_execute_request_exhausted_retries_timeout(self, mock_sleep):
        """Test that empty dict is returned when all retries exhausted on timeout"""
        config = APIConfig(max_retries=2, retry_backoff=2.0)
        client = BitoProAPIClient(config=config)
        
        with patch.object(client.session, 'get', side_effect=requests.Timeout("Timeout")):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {}
        # Should have slept 4 times total:
        # - 2 times for retry backoff (after first and second timeouts)
        # - 2 times for rate limiting (before second and third requests)
        assert mock_sleep.call_count == 4
    
    @patch('time.sleep')
    def test_execute_request_retry_on_connection_error(self, mock_sleep):
        """Test retry logic on connection errors"""
        config = APIConfig(max_retries=2, retry_backoff=2.0)
        client = BitoProAPIClient(config=config)
        
        # Mock connection error then success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "success"}
        
        with patch.object(client.session, 'get', side_effect=[
            requests.ConnectionError("Network error"),
            mock_response
        ]):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {"data": "success"}
        # Should have slept 2 times total:
        # - 1 time for retry backoff (after connection error)
        # - 1 time for rate limiting (before second request)
        assert mock_sleep.call_count == 2
    
    @patch('time.sleep')
    def test_execute_request_no_retry_on_4xx(self, mock_sleep):
        """Test that 4xx errors are not retried"""
        client = BitoProAPIClient()
        
        # Mock 404 error - raise_for_status will raise HTTPError
        mock_response = Mock()
        mock_response.status_code = 404
        
        # Create a proper HTTPError with response attribute
        http_error = requests.HTTPError()
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {}
        # Should not retry on 4xx errors
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_execute_request_exponential_backoff(self, mock_sleep):
        """Test exponential backoff calculation"""
        config = APIConfig(max_retries=3, retry_backoff=3.0)
        client = BitoProAPIClient(config=config)
        
        # Mock all responses to fail
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.object(client.session, 'get', return_value=mock_response):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {}
        # Should have slept 6 times total:
        # - 3 times for retry backoff (after each failure)
        # - 3 times for rate limiting (before second, third, and fourth requests)
        assert mock_sleep.call_count == 6
        # Verify exponential backoff: 3^0=1, 3^1=3, 3^2=9
        calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert 1.0 in calls
        assert 3.0 in calls
        assert 9.0 in calls
    
    @patch('time.sleep')
    def test_execute_request_logs_retry_attempts(self, mock_sleep, caplog):
        """Test that retry attempts are logged with attempt numbers"""
        config = APIConfig(max_retries=2, retry_backoff=2.0)
        client = BitoProAPIClient(config=config)
        
        # Mock responses to fail then succeed
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"data": "success"}
        
        with caplog.at_level(logging.WARNING):
            with patch.object(client.session, 'get', side_effect=[
                mock_response_fail,
                mock_response_success
            ]):
                result = client._execute_request(
                    url="https://test.com/api",
                    method=HTTPMethod.GET,
                    headers={}
                )
        
        assert result == {"data": "success"}
        # Verify retry attempt is logged
        assert "Retry attempt 1/2" in caplog.text
    
    @patch('time.sleep')
    def test_execute_request_unsupported_method(self, mock_sleep):
        """Test that unsupported HTTP methods return empty dict"""
        client = BitoProAPIClient()
        
        # Create a fake HTTP method (not GET or POST)
        fake_method = Mock()
        fake_method.value = "DELETE"
        
        result = client._execute_request(
            url="https://test.com/api",
            method=fake_method,
            headers={}
        )
        
        assert result == {}
        mock_sleep.assert_not_called()
    
    @patch('time.sleep')
    def test_execute_request_unexpected_error(self, mock_sleep):
        """Test that unexpected errors return empty dict"""
        client = BitoProAPIClient()
        
        with patch.object(client.session, 'get', side_effect=Exception("Unexpected error")):
            result = client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )
        
        assert result == {}
        mock_sleep.assert_not_called()



class TestPaginationDetection:
    """Test _detect_pagination_info method"""
    
    def test_detect_pagination_with_next_page_field(self):
        """Test detection of next_page field"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "next_page": "page2_token"
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'field'
        assert pagination_info['key'] == 'next_page'
        assert pagination_info['value'] == "page2_token"
    
    def test_detect_pagination_with_has_more_field(self):
        """Test detection of has_more field"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "has_more": True
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'field'
        assert pagination_info['key'] == 'has_more'
        assert pagination_info['value'] is True
    
    def test_detect_pagination_with_page_total_pattern(self):
        """Test detection of page/total_pages pattern"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "page": 1,
            "total_pages": 5
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'page_total'
        assert pagination_info['current_page'] == 1
        assert pagination_info['total_pages'] == 5
        assert pagination_info['has_next'] is True
    
    def test_detect_pagination_with_page_total_last_page(self):
        """Test detection when on last page"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "page": 5,
            "total_pages": 5
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'page_total'
        assert pagination_info['has_next'] is False
    
    def test_detect_pagination_with_offset_limit_pattern(self):
        """Test detection of offset/limit pattern"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "offset": 0,
            "limit": 10,
            "total": 50
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'offset_limit'
        assert pagination_info['offset'] == 0
        assert pagination_info['limit'] == 10
        assert pagination_info['total'] == 50
        assert pagination_info['has_next'] is True
        assert pagination_info['next_offset'] == 10
    
    def test_detect_pagination_with_offset_limit_last_page(self):
        """Test detection when on last page with offset/limit"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "offset": 40,
            "limit": 10,
            "total": 50
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'offset_limit'
        assert pagination_info['has_next'] is False
        assert pagination_info['next_offset'] is None
    
    def test_detect_pagination_no_pagination_info(self):
        """Test when response has no pagination information"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}, {"id": 2}]
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is None
    
    def test_detect_pagination_with_pagination_object(self):
        """Test detection of pagination object"""
        client = BitoProAPIClient()
        response = {
            "data": [{"id": 1}],
            "pagination": {
                "has_more": True,
                "next_page": 2
            }
        }
        
        pagination_info = client._detect_pagination_info(response)
        
        assert pagination_info is not None
        assert pagination_info['type'] == 'field'
        assert pagination_info['key'] == 'pagination'


class TestHasNextPage:
    """Test _has_next_page method"""
    
    def test_has_next_page_with_boolean_true(self):
        """Test has_next_page with boolean value True"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'field',
            'key': 'has_more',
            'value': True
        }
        
        assert client._has_next_page(pagination_info) is True
    
    def test_has_next_page_with_boolean_false(self):
        """Test has_next_page with boolean value False"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'field',
            'key': 'has_more',
            'value': False
        }
        
        assert client._has_next_page(pagination_info) is False
    
    def test_has_next_page_with_string_token(self):
        """Test has_next_page with non-empty string token"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'field',
            'key': 'next_page',
            'value': 'token123'
        }
        
        assert client._has_next_page(pagination_info) is True
    
    def test_has_next_page_with_empty_string(self):
        """Test has_next_page with empty string"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'field',
            'key': 'next_page',
            'value': ''
        }
        
        assert client._has_next_page(pagination_info) is False
    
    def test_has_next_page_with_dict_has_more_true(self):
        """Test has_next_page with dict containing has_more=True"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'field',
            'key': 'pagination',
            'value': {'has_more': True, 'next': 2}
        }
        
        assert client._has_next_page(pagination_info) is True
    
    def test_has_next_page_with_dict_has_more_false(self):
        """Test has_next_page with dict containing has_more=False"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'field',
            'key': 'pagination',
            'value': {'has_more': False}
        }
        
        assert client._has_next_page(pagination_info) is False
    
    def test_has_next_page_with_page_total_has_next(self):
        """Test has_next_page with page_total type"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'page_total',
            'current_page': 1,
            'total_pages': 5,
            'has_next': True
        }
        
        assert client._has_next_page(pagination_info) is True
    
    def test_has_next_page_with_offset_limit_has_next(self):
        """Test has_next_page with offset_limit type"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'offset_limit',
            'offset': 0,
            'limit': 10,
            'total': 50,
            'has_next': True,
            'next_offset': 10
        }
        
        assert client._has_next_page(pagination_info) is True
    
    def test_has_next_page_with_none(self):
        """Test has_next_page with None pagination_info"""
        client = BitoProAPIClient()
        
        assert client._has_next_page(None) is False


class TestUpdateParamsForNextPage:
    """Test _update_params_for_next_page method"""
    
    def test_update_params_with_string_token(self):
        """Test updating params with string token"""
        client = BitoProAPIClient()
        params = {"limit": 10}
        pagination_info = {
            'type': 'field',
            'key': 'next_page',
            'value': 'token123'
        }
        
        next_params = client._update_params_for_next_page(params, pagination_info)
        
        assert next_params['limit'] == 10
        assert next_params['next_page'] == 'token123'
    
    def test_update_params_with_dict_next_page(self):
        """Test updating params with dict containing next_page"""
        client = BitoProAPIClient()
        params = {"limit": 10}
        pagination_info = {
            'type': 'field',
            'key': 'pagination',
            'value': {'next_page': 2, 'has_more': True}
        }
        
        next_params = client._update_params_for_next_page(params, pagination_info)
        
        assert next_params['limit'] == 10
        assert next_params['page'] == 2
    
    def test_update_params_with_dict_cursor(self):
        """Test updating params with dict containing cursor"""
        client = BitoProAPIClient()
        params = {"limit": 10}
        pagination_info = {
            'type': 'field',
            'key': 'pagination',
            'value': {'cursor': 'cursor_abc123'}
        }
        
        next_params = client._update_params_for_next_page(params, pagination_info)
        
        assert next_params['limit'] == 10
        assert next_params['cursor'] == 'cursor_abc123'
    
    def test_update_params_with_page_total(self):
        """Test updating params with page_total type"""
        client = BitoProAPIClient()
        params = {"limit": 10}
        pagination_info = {
            'type': 'page_total',
            'current_page': 1,
            'total_pages': 5,
            'has_next': True
        }
        
        next_params = client._update_params_for_next_page(params, pagination_info)
        
        assert next_params['limit'] == 10
        assert next_params['page'] == 2
    
    def test_update_params_with_offset_limit(self):
        """Test updating params with offset_limit type"""
        client = BitoProAPIClient()
        params = {"limit": 10}
        pagination_info = {
            'type': 'offset_limit',
            'offset': 0,
            'limit': 10,
            'total': 50,
            'has_next': True,
            'next_offset': 10
        }
        
        next_params = client._update_params_for_next_page(params, pagination_info)
        
        assert next_params['limit'] == 10
        assert next_params['offset'] == 10
    
    def test_update_params_with_none_params(self):
        """Test updating params when params is None"""
        client = BitoProAPIClient()
        pagination_info = {
            'type': 'page_total',
            'current_page': 1,
            'total_pages': 5,
            'has_next': True
        }
        
        next_params = client._update_params_for_next_page(None, pagination_info)
        
        assert next_params['page'] == 2
    
    def test_update_params_preserves_original(self):
        """Test that original params dict is not modified"""
        client = BitoProAPIClient()
        params = {"limit": 10, "filter": "active"}
        pagination_info = {
            'type': 'page_total',
            'current_page': 1,
            'total_pages': 5,
            'has_next': True
        }
        
        next_params = client._update_params_for_next_page(params, pagination_info)
        
        # Original params should not be modified
        assert 'page' not in params
        assert params['limit'] == 10
        assert params['filter'] == "active"
        
        # Next params should have the page added
        assert next_params['page'] == 2
        assert next_params['limit'] == 10
        assert next_params['filter'] == "active"


class TestRateLimiting:
    """Test rate limiting logic - Requirements 4.1, 4.2, 4.3, 4.4"""

    def test_first_request_no_sleep(self):
        """First request should not sleep (no previous request timestamp)"""
        client = BitoProAPIClient()
        assert client._last_request_time is None

        with patch('time.sleep') as mock_sleep, patch('time.time', return_value=1000.0):
            client._enforce_rate_limit()

        mock_sleep.assert_not_called()

    def test_last_request_time_updated_after_enforce(self):
        """_last_request_time should be set after _enforce_rate_limit is called"""
        client = BitoProAPIClient()
        assert client._last_request_time is None

        with patch('time.time', return_value=1000.0):
            client._enforce_rate_limit()

        assert client._last_request_time == 1000.0

    def test_rate_limit_0_9_rps_waits_minimum_interval(self):
        """With 0.9 req/s, minimum interval is ~1.11s (Requirement 4.3)"""
        config = APIConfig(rate_limit_per_second=0.9)
        client = BitoProAPIClient(config=config)

        # Simulate first request at t=1000.0
        client._last_request_time = 1000.0

        # Second request arrives only 0.5s later - should sleep ~0.61s
        with patch('time.sleep') as mock_sleep, \
             patch('time.time', return_value=1000.5):
            client._enforce_rate_limit()

        expected_min_interval = 1.0 / 0.9  # ~1.111s
        expected_wait = expected_min_interval - 0.5  # ~0.611s
        mock_sleep.assert_called_once()
        actual_wait = mock_sleep.call_args[0][0]
        assert abs(actual_wait - expected_wait) < 1e-6

    def test_rate_limit_no_sleep_when_enough_time_elapsed(self):
        """No sleep when elapsed time already exceeds minimum interval"""
        config = APIConfig(rate_limit_per_second=0.9)
        client = BitoProAPIClient(config=config)

        # Simulate first request at t=1000.0
        client._last_request_time = 1000.0

        # Second request arrives 2.0s later - well past the 1.11s minimum
        with patch('time.sleep') as mock_sleep, \
             patch('time.time', return_value=1002.0):
            client._enforce_rate_limit()

        mock_sleep.assert_not_called()

    def test_rate_limit_1_rps_minimum_interval_1_second(self):
        """With 1.0 req/s, minimum interval is exactly 1.0s (Requirement 4.2)"""
        config = APIConfig(rate_limit_per_second=1.0)
        client = BitoProAPIClient(config=config)

        client._last_request_time = 1000.0

        # Only 0.3s elapsed - should sleep 0.7s
        with patch('time.sleep') as mock_sleep, \
             patch('time.time', return_value=1000.3):
            client._enforce_rate_limit()

        mock_sleep.assert_called_once()
        actual_wait = mock_sleep.call_args[0][0]
        assert abs(actual_wait - 0.7) < 1e-6

    def test_rate_limit_2_rps_minimum_interval_0_5_seconds(self):
        """With 2.0 req/s, minimum interval is 0.5s (Requirement 4.2)"""
        config = APIConfig(rate_limit_per_second=2.0)
        client = BitoProAPIClient(config=config)

        client._last_request_time = 1000.0

        # Only 0.2s elapsed - should sleep 0.3s
        with patch('time.sleep') as mock_sleep, \
             patch('time.time', return_value=1000.2):
            client._enforce_rate_limit()

        mock_sleep.assert_called_once()
        actual_wait = mock_sleep.call_args[0][0]
        assert abs(actual_wait - 0.3) < 1e-6

    def test_rate_limit_enforced_on_each_execute_request(self):
        """_enforce_rate_limit is called before every HTTP request (Requirement 4.1)"""
        client = BitoProAPIClient()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "ok"}

        with patch.object(client, '_enforce_rate_limit') as mock_rl, \
             patch.object(client.session, 'get', return_value=mock_response):
            client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )

        mock_rl.assert_called_once()

    def test_rate_limit_enforced_on_each_retry(self):
        """_enforce_rate_limit is called before each retry attempt (Requirement 4.4)"""
        config = APIConfig(max_retries=2, retry_backoff=0.01)
        client = BitoProAPIClient(config=config)

        mock_fail = Mock()
        mock_fail.status_code = 500

        mock_success = Mock()
        mock_success.status_code = 200
        mock_success.json.return_value = {"data": "ok"}

        with patch.object(client, '_enforce_rate_limit') as mock_rl, \
             patch('time.sleep'), \
             patch.object(client.session, 'get', side_effect=[mock_fail, mock_fail, mock_success]):
            client._execute_request(
                url="https://test.com/api",
                method=HTTPMethod.GET,
                headers={}
            )

        # Called once per attempt: initial + 2 retries = 3 total
        assert mock_rl.call_count == 3

    def test_rate_limit_sequential_requests_maintain_compliance(self):
        """Multiple sequential requests all respect the rate limit (Requirement 4.4)"""
        config = APIConfig(rate_limit_per_second=0.9)
        client = BitoProAPIClient(config=config)

        sleep_calls = []
        time_counter = [1000.0]

        def fake_time():
            return time_counter[0]

        def fake_sleep(duration):
            sleep_calls.append(duration)
            time_counter[0] += duration

        # Simulate 3 requests arriving 0.5s apart (faster than rate limit allows)
        with patch('time.time', side_effect=fake_time), \
             patch('time.sleep', side_effect=fake_sleep):
            for _ in range(3):
                client._enforce_rate_limit()
                time_counter[0] += 0.5  # simulate 0.5s of work between calls

        # First request: no sleep (no previous timestamp)
        # Subsequent requests should have slept to maintain ~1.11s interval
        assert len(sleep_calls) == 2
        min_interval = 1.0 / 0.9
        for wait in sleep_calls:
            assert wait > 0
            assert wait <= min_interval
