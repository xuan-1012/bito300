"""
Integration tests for BitoPro API client with AWS services.

**Validates: Requirements 1.1, 1.2, 1.5, 11.1**
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.utils.bitopro_client import BitoproClient, BitoproClientError
from src.common.aws_clients import AWSClients


@pytest.fixture
def mock_secrets_manager():
    """Mock Secrets Manager client."""
    with patch('boto3.client') as mock_client:
        mock_sm = Mock()
        mock_sm.get_secret_value.return_value = {
            'SecretString': '{"api_key": "test_key", "api_secret": "test_secret"}'
        }
        
        def client_factory(service_name, **kwargs):
            if service_name == 'secretsmanager':
                return mock_sm
            return Mock()
        
        mock_client.side_effect = client_factory
        yield mock_sm


class TestBitoproClientIntegration:
    """Integration tests for BitoPro client with AWS clients."""
    
    def test_client_initialization_with_aws_clients(self, mock_secrets_manager):
        """Test client initialization using real AWSClients instance."""
        # Reset singleton to ensure clean state
        AWSClients.reset_instance()
        
        aws_clients = AWSClients.get_instance()
        
        client = BitoproClient(
            aws_clients=aws_clients,
            secret_id='bitopro-api-key'
        )
        
        assert client.api_key == 'test_key'
        assert client.api_secret == 'test_secret'
    
    @patch('src.utils.bitopro_client.requests.request')
    def test_end_to_end_fetch_with_aws(self, mock_request, mock_secrets_manager):
        """Test end-to-end transaction fetch with AWS integration."""
        # Reset singleton
        AWSClients.reset_instance()
        
        # Mock API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': 'tx_001',
                'timestamp': 1704067200000,
                'from': 'account_1',
                'to': 'account_2',
                'amount': 1000.0,
                'currency': 'BTC'
            }
        ]
        mock_request.return_value = mock_response
        
        # Create client with AWS integration
        aws_clients = AWSClients.get_instance()
        client = BitoproClient(aws_clients=aws_clients)
        
        # Fetch transactions
        start_time = datetime(2024, 1, 1)
        end_time = datetime(2024, 1, 2)
        
        transactions = client.fetch_transactions(
            start_time=start_time,
            end_time=end_time,
            limit=100
        )
        
        assert len(transactions) == 1
        assert transactions[0]['id'] == 'tx_001'
        assert transactions[0]['amount'] == 1000.0
    
    def test_secrets_manager_error_handling(self):
        """Test error handling when Secrets Manager fails."""
        # Reset singleton
        AWSClients.reset_instance()
        
        from botocore.exceptions import ClientError
        
        with patch('boto3.client') as mock_client:
            mock_sm = Mock()
            # Simulate ClientError from boto3
            mock_sm.get_secret_value.side_effect = ClientError(
                {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Secret not found'}},
                'GetSecretValue'
            )
            
            def client_factory(service_name, **kwargs):
                if service_name == 'secretsmanager':
                    return mock_sm
                return Mock()
            
            mock_client.side_effect = client_factory
            
            aws_clients = AWSClients.get_instance()
            
            with pytest.raises(BitoproClientError) as exc_info:
                BitoproClient(aws_clients=aws_clients)
            
            assert "Failed to retrieve" in str(exc_info.value)
