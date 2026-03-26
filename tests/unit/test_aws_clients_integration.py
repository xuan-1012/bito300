"""
Integration tests for AWS Clients module.

Tests realistic usage patterns for Lambda functions using the AWS clients.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from botocore.exceptions import ClientError

from src.common.aws_clients import get_aws_clients, AWSClients


@pytest.fixture(autouse=True)
def reset_singleton():
    """Reset the singleton instance before each test."""
    AWSClients.reset_instance()
    yield
    AWSClients.reset_instance()


class TestLambdaUsagePatterns:
    """Test realistic Lambda function usage patterns."""
    
    @patch('boto3.client')
    def test_lambda_fetches_secret_and_stores_to_s3(self, mock_boto_client):
        """Test Lambda pattern: fetch secret and store data to S3."""
        # Mock Secrets Manager
        mock_secrets_client = Mock()
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': '{"api_key": "test-key", "api_secret": "test-secret"}'
        }
        
        # Mock S3
        mock_s3_client = Mock()
        mock_s3_client.put_object.return_value = {
            'ETag': '"abc123"',
            'VersionId': 'v1'
        }
        
        def client_side_effect(service_name, **kwargs):
            if service_name == 'secretsmanager':
                return mock_secrets_client
            elif service_name == 's3':
                return mock_s3_client
            return Mock()
        
        mock_boto_client.side_effect = client_side_effect
        
        # Lambda handler pattern
        clients = get_aws_clients()
        
        # Step 1: Fetch API credentials
        secret = clients.get_secret('bitopro-api-key')
        assert secret['api_key'] == 'test-key'
        
        # Step 2: Store data to S3
        data = {'transactions': [{'id': '1', 'amount': 100}]}
        clients.s3.put_object(
            Bucket='crypto-detection-raw',
            Key='raw-data/2024-01-15.json',
            Body=json.dumps(data)
        )
        
        # Verify calls
        mock_secrets_client.get_secret_value.assert_called_once()
        mock_s3_client.put_object.assert_called_once()
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_lambda_reads_s3_and_writes_dynamodb(self, mock_boto_resource, mock_boto_client):
        """Test Lambda pattern: read from S3 and write to DynamoDB."""
        # Mock S3
        mock_s3_client = Mock()
        mock_s3_client.get_object.return_value = {
            'Body': Mock(read=lambda: b'{"account_id": "acc_001", "risk_score": 85}')
        }
        
        # Mock DynamoDB
        mock_dynamodb = Mock()
        mock_table = Mock()
        mock_dynamodb.Table.return_value = mock_table
        mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        mock_boto_client.return_value = mock_s3_client
        mock_boto_resource.return_value = mock_dynamodb
        
        # Lambda handler pattern
        clients = get_aws_clients()
        
        # Step 1: Read from S3
        response = clients.s3.get_object(
            Bucket='crypto-detection-features',
            Key='features/2024-01-15.json'
        )
        data = json.loads(response['Body'].read())
        
        # Step 2: Write to DynamoDB
        table = clients.dynamodb.Table('crypto-risk-profiles')
        table.put_item(Item=data)
        
        # Verify calls
        mock_s3_client.get_object.assert_called_once()
        mock_table.put_item.assert_called_once()
    
    @patch('boto3.client')
    def test_lambda_calls_bedrock_with_rate_limiting(self, mock_boto_client):
        """Test Lambda pattern: call Bedrock for risk analysis."""
        # Mock Bedrock Runtime
        mock_bedrock_client = Mock()
        mock_bedrock_client.invoke_model.return_value = {
            'body': Mock(read=lambda: json.dumps({
                'content': [{
                    'text': json.dumps({
                        'risk_score': 75,
                        'risk_level': 'high',
                        'risk_factors': ['High volume', 'Night transactions'],
                        'explanation': 'Account shows suspicious patterns',
                        'confidence': 0.85
                    })
                }]
            }).encode())
        }
        
        mock_boto_client.return_value = mock_bedrock_client
        
        # Lambda handler pattern
        clients = get_aws_clients()
        
        # Call Bedrock for risk analysis
        response = clients.bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1024,
                'messages': [{'role': 'user', 'content': 'Analyze risk'}]
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        risk_data = json.loads(response_body['content'][0]['text'])
        
        assert risk_data['risk_score'] == 75
        assert risk_data['risk_level'] == 'high'
        
        # Verify call
        mock_bedrock_client.invoke_model.assert_called_once()


class TestErrorHandlingPatterns:
    """Test error handling patterns for Lambda functions."""
    
    @patch('boto3.client')
    def test_lambda_handles_s3_error_gracefully(self, mock_boto_client):
        """Test Lambda handles S3 errors gracefully."""
        mock_s3_client = Mock()
        mock_s3_client.get_object.side_effect = ClientError(
            {'Error': {'Code': 'NoSuchKey', 'Message': 'Key not found'}},
            'GetObject'
        )
        
        mock_boto_client.return_value = mock_s3_client
        
        clients = get_aws_clients()
        
        # Lambda should handle the error
        with pytest.raises(ClientError) as exc_info:
            clients.s3.get_object(Bucket='test-bucket', Key='nonexistent.json')
        
        assert exc_info.value.response['Error']['Code'] == 'NoSuchKey'
    
    @patch('boto3.client')
    def test_lambda_handles_secret_not_found(self, mock_boto_client):
        """Test Lambda handles missing secret gracefully."""
        mock_secrets_client = Mock()
        mock_secrets_client.get_secret_value.side_effect = ClientError(
            {'Error': {'Code': 'ResourceNotFoundException', 'Message': 'Secret not found'}},
            'GetSecretValue'
        )
        
        mock_boto_client.return_value = mock_secrets_client
        
        clients = get_aws_clients()
        
        # Lambda should handle the error
        from src.common.aws_clients import AWSClientError
        with pytest.raises(AWSClientError, match="Failed to retrieve secret"):
            clients.get_secret('nonexistent-secret')


class TestConnectionPooling:
    """Test connection pooling and reuse across Lambda invocations."""
    
    @patch('boto3.client')
    def test_clients_reused_across_invocations(self, mock_boto_client):
        """Test that clients are reused across multiple Lambda invocations."""
        mock_s3 = Mock()
        mock_boto_client.return_value = mock_s3
        
        # Simulate multiple Lambda invocations
        for _ in range(5):
            clients = get_aws_clients()
            s3 = clients.s3
            # Use the client
            s3.list_buckets()
        
        # boto3.client should only be called once (connection pooling)
        assert mock_boto_client.call_count == 1
        # But list_buckets should be called 5 times
        assert mock_s3.list_buckets.call_count == 5


class TestRealWorldScenario:
    """Test a complete real-world scenario."""
    
    @patch('boto3.client')
    @patch('boto3.resource')
    def test_complete_risk_analysis_workflow(self, mock_boto_resource, mock_boto_client):
        """Test complete workflow: fetch secret, read S3, call Bedrock, write DynamoDB."""
        # Setup mocks
        mock_secrets_client = Mock()
        mock_s3_client = Mock()
        mock_bedrock_client = Mock()
        mock_dynamodb = Mock()
        mock_table = Mock()
        
        # Configure Secrets Manager
        mock_secrets_client.get_secret_value.return_value = {
            'SecretString': '{"api_key": "test-key"}'
        }
        
        # Configure S3
        mock_s3_client.get_object.return_value = {
            'Body': Mock(read=lambda: json.dumps({
                'account_id': 'acc_001',
                'total_volume': 150000,
                'night_transaction_ratio': 0.4
            }).encode())
        }
        
        # Configure Bedrock
        mock_bedrock_client.invoke_model.return_value = {
            'body': Mock(read=lambda: json.dumps({
                'content': [{
                    'text': json.dumps({
                        'risk_score': 80,
                        'risk_level': 'critical',
                        'risk_factors': ['High volume', 'Night transactions'],
                        'explanation': 'Suspicious activity detected',
                        'confidence': 0.9
                    })
                }]
            }).encode())
        }
        
        # Configure DynamoDB
        mock_dynamodb.Table.return_value = mock_table
        mock_table.put_item.return_value = {'ResponseMetadata': {'HTTPStatusCode': 200}}
        
        def client_side_effect(service_name, **kwargs):
            if service_name == 'secretsmanager':
                return mock_secrets_client
            elif service_name == 's3':
                return mock_s3_client
            elif service_name == 'bedrock-runtime':
                return mock_bedrock_client
            return Mock()
        
        mock_boto_client.side_effect = client_side_effect
        mock_boto_resource.return_value = mock_dynamodb
        
        # Execute complete workflow
        clients = get_aws_clients()
        
        # Step 1: Get API credentials
        secret = clients.get_secret('bitopro-api-key')
        assert 'api_key' in secret
        
        # Step 2: Read features from S3
        response = clients.s3.get_object(
            Bucket='crypto-detection-features',
            Key='features/acc_001.json'
        )
        features = json.loads(response['Body'].read())
        
        # Step 3: Analyze risk with Bedrock
        bedrock_response = clients.bedrock_runtime.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'messages': [{'role': 'user', 'content': f'Analyze: {features}'}]
            })
        )
        risk_data = json.loads(
            json.loads(bedrock_response['body'].read())['content'][0]['text']
        )
        
        # Step 4: Store results to DynamoDB
        table = clients.dynamodb.Table('crypto-risk-profiles')
        table.put_item(Item={
            'account_id': features['account_id'],
            'risk_score': risk_data['risk_score'],
            'risk_level': risk_data['risk_level']
        })
        
        # Verify all steps executed
        mock_secrets_client.get_secret_value.assert_called_once()
        mock_s3_client.get_object.assert_called_once()
        mock_bedrock_client.invoke_model.assert_called_once()
        mock_table.put_item.assert_called_once()
