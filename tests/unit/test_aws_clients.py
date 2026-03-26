"""
Unit tests for AWS Clients utility module.

Tests the initialization, connection pooling, error handling, and
singleton behavior of the AWSClients class.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError, BotoCoreError

from src.common.aws_clients import AWSClients, AWSClientError, get_aws_clients


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    AWSClients.reset_instance()
    yield
    AWSClients.reset_instance()


@pytest.fixture
def mock_env():
    """Mock environment variables."""
    with patch.dict(os.environ, {
        'AWS_REGION': 'us-west-2',
        'AWS_MAX_ATTEMPTS': '5',
        'AWS_CONNECT_TIMEOUT': '10',
        'AWS_READ_TIMEOUT': '120'
    }):
        yield


class TestAWSClientsInitialization:
    """Test AWSClients initialization and configuration."""
    
    def test_singleton_pattern(self):
        """Test that AWSClients follows singleton pattern."""
        instance1 = AWSClients.get_instance()
        instance2 = AWSClients.get_instance()
        
        assert instance1 is instance2
    
    def test_direct_instantiation_raises_error(self):
        """Test that direct instantiation after get_instance raises error."""
        AWSClients.get_instance()
        
        with pytest.raises(RuntimeError, match="singleton"):
            AWSClients()
    
    def test_default_configuration(self):
        """Test default configuration values."""
        clients = AWSClients.get_instance()
        
        assert clients.region == 'us-east-1'
        assert clients.config.region_name == 'us-east-1'
        assert clients.config.retries['max_attempts'] == 3
        assert clients.config.connect_timeout == 5
        assert clients.config.read_timeout == 60
    
    def test_custom_configuration(self, mock_env):
        """Test custom configuration from environment variables."""
        clients = AWSClients.get_instance()
        
        assert clients.region == 'us-west-2'
        assert clients.config.region_name == 'us-west-2'
        assert clients.config.retries['max_attempts'] == 5
        assert clients.config.connect_timeout == 10
        assert clients.config.read_timeout == 120
    
    def test_reset_instance(self):
        """Test that reset_instance clears the singleton."""
        instance1 = AWSClients.get_instance()
        AWSClients.reset_instance()
        instance2 = AWSClients.get_instance()
        
        assert instance1 is not instance2


class TestS3Client:
    """Test S3 client initialization and error handling."""
    
    @patch('boto3.client')
    def test_s3_client_initialization(self, mock_boto_client):
        """Test successful S3 client initialization."""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        clients = AWSClients.get_instance()
        s3 = clients.s3
        
        assert s3 is mock_s3
        mock_boto_client.assert_called_once()
        assert mock_boto_client.call_args[0][0] == 's3'
    
    @patch('boto3.client')
    def test_s3_client_reuse(self, mock_boto_client):
        """Test that S3 client is reused (connection pooling)."""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        clients = AWSClients.get_instance()
        s3_1 = clients.s3
        s3_2 = clients.s3
        
        assert s3_1 is s3_2
        # boto3.client should only be called once
        assert mock_boto_client.call_count == 1
    
    @patch('boto3.client')
    def test_s3_client_initialization_error(self, mock_boto_client):
        """Test S3 client initialization error handling."""
        mock_boto_client.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied', 'Message': 'Access denied'}},
            'CreateClient'
        )
        
        clients = AWSClients.get_instance()
        
        with pytest.raises(AWSClientError, match="Failed to initialize S3 client"):
            _ = clients.s3


class TestDynamoDBClient:
    """Test DynamoDB resource initialization and error handling."""
    
    @patch('boto3.resource')
    def test_dynamodb_resource_initialization(self, mock_boto_resource):
        """Test successful DynamoDB resource initialization."""
        mock_dynamodb = Mock()
        mock_boto_resource.return_value = mock_dynamodb
        
        clients = AWSClients.get_instance()
        dynamodb = clients.dynamodb
        
        assert dynamodb is mock_dynamodb
        mock_boto_resource.assert_called_once()
        assert mock_boto_resource.call_args[0][0] == 'dynamodb'
    
    @patch('boto3.resource')
    def test_dynamodb_resource_reuse(self, mock_boto_resource):
        """Test that DynamoDB resource is reused."""
        mock_dynamodb = Mock()
        mock_boto_resource.return_value = mock_dynamodb
        
        clients = AWSClients.get_instance()
        dynamodb_1 = clients.dynamodb
        dynamodb_2 = clients.dynamodb
        
        assert dynamodb_1 is dynamodb_2
        assert mock_boto_resource.call_count == 1
    
    @patch('boto3.resource')
    def test_dynamodb_resource_initialization_error(self, mock_boto_resource):
        """Test DynamoDB resource initialization error handling."""
        mock_boto_resource.side_effect = BotoCoreError()
        
        clients = AWSClients.get_instance()
        
        with pytest.raises(AWSClientError, match="Failed to initialize DynamoDB resource"):
            _ = clients.dynamodb


class TestBedrockRuntimeClient:
    """Test Bedrock Runtime client initialization and error handling."""
    
    @patch('boto3.client')
    def test_bedrock_runtime_client_initialization(self, mock_boto_client):
        """Test successful Bedrock Runtime client initialization."""
        mock_bedrock = Mock()
        mock_boto_client.return_value = mock_bedrock
        
        clients = AWSClients.get_instance()
        bedrock = clients.bedrock_runtime
        
        assert bedrock is mock_bedrock
        mock_boto_client.assert_called_once()
        assert mock_boto_client.call_args[0][0] == 'bedrock-runtime'
    
    @patch('boto3.client')
    def test_bedrock_runtime_client_reuse(self, mock_boto_client):
        """Test that Bedrock Runtime client is reused."""
        mock_bedrock = Mock()
        mock_boto_client.return_value = mock_bedrock
        
        clients = AWSClients.get_instance()
        bedrock_1 = clients.bedrock_runtime
        bedrock_2 = clients.bedrock_runtime
        
        assert bedrock_1 is bedrock_2
        assert mock_boto_client.call_count == 1
    
    @patch('boto3.client')
    def test_bedrock_runtime_client_initialization_error(self, mock_boto_client):
        """Test Bedrock Runtime client initialization error handling."""
        mock_boto_client.side_effect = ClientError(
            {'Error': {'Code': 'ServiceUnavailable', 'Message': 'Service unavailable'}},
            'CreateClient'
        )
        
        clients = AWSClients.get_instance()
        
        with pytest.raises(AWSClientError, match="Failed to initialize Bedrock Runtime client"):
            _ = clients.bedrock_runtime


class TestSecretsManagerClient:
    """Test Secrets Manager client initialization and error handling."""
    
    @patch('boto3.client')
    def test_secrets_manager_client_initialization(self, mock_boto_client):
        """Test successful Secrets Manager client initialization."""
        mock_secrets = Mock()
        mock_boto_client.return_value = mock_secrets
        
        clients = AWSClients.get_instance()
        secrets = clients.secrets_manager
        
        assert secrets is mock_secrets
        mock_boto_client.assert_called_once()
        assert mock_boto_client.call_args[0][0] == 'secretsmanager'
    
    @patch('boto3.client')
    def test_secrets_manager_client_reuse(self, mock_boto_client):
        """Test that Secrets Manager client is reused."""
        mock_secrets = Mock()
        mock_boto_client.return_value = mock_secrets
        
        clients = AWSClients.get_instance()
        secrets_1 = clients.secrets_manager
        secrets_2 = clients.secrets_manager
        
        assert secrets_1 is secrets_2
        assert mock_boto_client.call_count == 1
    
    @patch('boto3.client')
    def test_secrets_manager_client_initialization_error(self, mock_boto_client):
        """Test Secrets Manager client initialization error handling."""
        mock_boto_client.side_effect = BotoCoreError()
        
        clients = AWSClients.get_instance()
        
        with pytest.raises(AWSClientError, match="Failed to initialize Secrets Manager client"):
            _ = clients.secrets_manager


class TestGetSecret:
    """Test get_secret convenience method."""
    
    @patch('boto3.client')
    def test_get_secret_success(self, mock_boto_client):
        """Test successful secret retrieval."""
        mock_secrets_client = Mock()
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': '{"api_key": "test-key-123", "api_secret": "test-secret-456"}'
        }
        mock_boto_client.return_value = mock_secrets_client
        
        clients = AWSClients.get_instance()
        secret = clients.get_secret('bitopro-api-key')
        
        assert secret == {
            'api_key': 'test-key-123',
            'api_secret': 'test-secret-456'
        }
        mock_secrets_client.get_secret_value.assert_called_once_with(
            SecretId='bitopro-api-key'
        )
    
    @patch('boto3.client')
    def test_get_secret_binary(self, mock_boto_client):
        """Test binary secret retrieval."""
        mock_secrets_client = Mock()
        mock_secrets_client.get_secret_value.return_value = {
            'SecretBinary': b'binary-secret-data'
        }
        mock_boto_client.return_value = mock_secrets_client
        
        clients = AWSClients.get_instance()
        secret = clients.get_secret('binary-secret')
        
        assert secret == {'SecretBinary': b'binary-secret-data'}
    
    @patch('boto3.client')
    def test_get_secret_not_found(self, mock_boto_client):
        """Test secret not found error."""
        mock_secrets_client = Mock()
        mock_secrets_client.get_secret_value.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Secret not found'}},
            'GetSecretValue'
        )
        mock_boto_client.return_value = mock_secrets_client
        
        clients = AWSClients.get_instance()
        
        with pytest.raises(AWSClientError, match="Failed to retrieve secret"):
            clients.get_secret('nonexistent-secret')
    
    @patch('boto3.client')
    def test_get_secret_access_denied(self, mock_boto_client):
        """Test secret access denied error."""
        mock_secrets_client = Mock()
        mock_secrets_client.get_secret_value.side_effect = ClientError(
            {'Error': {'Code': 'AccessDeniedException', 'Message': 'Access denied'}},
            'GetSecretValue'
        )
        mock_boto_client.return_value = mock_secrets_client
        
        clients = AWSClients.get_instance()
        
        with pytest.raises(AWSClientError, match="Failed to retrieve secret"):
            clients.get_secret('restricted-secret')


class TestConvenienceFunction:
    """Test get_aws_clients convenience function."""
    
    def test_get_aws_clients_returns_singleton(self):
        """Test that get_aws_clients returns the singleton instance."""
        clients1 = get_aws_clients()
        clients2 = get_aws_clients()
        
        assert clients1 is clients2
        assert isinstance(clients1, AWSClients)


class TestMultipleClients:
    """Test using multiple clients together."""
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_multiple_clients_initialization(self, mock_boto_resource, mock_boto_client):
        """Test initializing multiple clients in sequence."""
        mock_s3 = Mock()
        mock_bedrock = Mock()
        mock_secrets = Mock()
        mock_dynamodb = Mock()
        
        # Configure mocks to return different objects based on service name
        def client_side_effect(service_name, **kwargs):
            if service_name == 's3':
                return mock_s3
            elif service_name == 'bedrock-runtime':
                return mock_bedrock
            elif service_name == 'secretsmanager':
                return mock_secrets
            return Mock()
        
        mock_boto_client.side_effect = client_side_effect
        mock_boto_resource.return_value = mock_dynamodb
        
        clients = AWSClients.get_instance()
        
        # Access all clients
        s3 = clients.s3
        dynamodb = clients.dynamodb
        bedrock = clients.bedrock_runtime
        secrets = clients.secrets_manager
        
        # Verify all clients are initialized correctly
        assert s3 is mock_s3
        assert dynamodb is mock_dynamodb
        assert bedrock is mock_bedrock
        assert secrets is mock_secrets
        
        # Verify each client was created only once
        assert mock_boto_client.call_count == 3  # s3, bedrock-runtime, secretsmanager
        assert mock_boto_resource.call_count == 1  # dynamodb
