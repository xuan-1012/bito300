"""
Integration tests for BitoProAPIClient

Tests the client's integration with requests library and session management.

**Validates: Requirements 1.1, 1.3, 1.4, 1.5, 10.1, 12.2**
"""

import pytest
from src.ingestion.client import BitoProAPIClient
from src.ingestion.models import APIConfig


class TestClientIntegration:
    """Integration tests for BitoProAPIClient"""
    
    def test_client_lifecycle(self):
        """Test complete client lifecycle: create, use, close"""
        # Create client
        client = BitoProAPIClient(
            api_key="test_key",
            api_secret="test_secret"
        )
        
        # Verify initialization
        assert client.session is not None
        assert client.api_key == "test_key"
        assert client.api_secret == "test_secret"
        
        # Build headers
        headers = client._build_headers()
        assert "X-BITOPRO-APIKEY" in headers
        assert "X-BITOPRO-APISECRET" in headers
        
        # Close client
        client.close()
    
    def test_client_as_context_manager(self):
        """Test client used as context manager"""
        with BitoProAPIClient(api_key="test") as client:
            headers = client._build_headers()
            assert "X-BITOPRO-APIKEY" in headers
            assert headers["X-BITOPRO-APIKEY"] == "test"
    
    def test_multiple_clients_independent(self):
        """Test that multiple clients are independent"""
        client1 = BitoProAPIClient(api_key="key1")
        client2 = BitoProAPIClient(api_key="key2")
        
        headers1 = client1._build_headers()
        headers2 = client2._build_headers()
        
        assert headers1["X-BITOPRO-APIKEY"] == "key1"
        assert headers2["X-BITOPRO-APIKEY"] == "key2"
        
        client1.close()
        client2.close()
    
    def test_custom_config_applied(self):
        """Test that custom configuration is properly applied"""
        config = APIConfig(
            base_url="https://test.api.com/",
            timeout=45,
            max_retries=5,
            retry_backoff=3.0,
            rate_limit_per_second=0.5
        )
        
        client = BitoProAPIClient(config=config)
        
        assert client.config.base_url == "https://test.api.com/"
        assert client.config.timeout == 45
        assert client.config.max_retries == 5
        assert client.config.retry_backoff == 3.0
        assert client.config.rate_limit_per_second == 0.5
        
        client.close()
    
    def test_session_adapters_configured(self):
        """Test that session has proper adapters configured"""
        client = BitoProAPIClient()
        
        # Verify HTTPS adapter exists
        https_adapter = client.session.get_adapter("https://test.com")
        assert https_adapter is not None
        
        # Verify HTTP adapter exists (though we only use HTTPS in practice)
        http_adapter = client.session.get_adapter("http://test.com")
        assert http_adapter is not None
        
        client.close()
    
    def test_headers_merge_correctly(self):
        """Test that custom headers merge with default headers"""
        client = BitoProAPIClient(
            api_key="test_key",
            api_secret="test_secret"
        )
        
        custom_headers = {
            "X-Custom": "value",
            "User-Agent": "TestAgent/1.0"
        }
        
        headers = client._build_headers(custom_headers=custom_headers)
        
        # Verify all headers present
        assert headers["X-BITOPRO-APIKEY"] == "test_key"
        assert headers["X-BITOPRO-APISECRET"] == "test_secret"
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"
        assert headers["X-Custom"] == "value"
        assert headers["User-Agent"] == "TestAgent/1.0"
        
        client.close()
