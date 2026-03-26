"""
End-to-end integration test for crypto suspicious account detection workflow.

Tests the complete workflow with mock BitoPro API and Bedrock, verifying:
- All intermediate data stored correctly in S3
- Risk assessments stored in DynamoDB
- Final report contains expected data
- Uses LocalStack for local AWS service testing

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.1, 3.11, 4.1, 4.7, 8.1, 8.9,
              9.1, 9.2, 9.3, 9.4, 9.5**
"""

import json
import os
import tempfile
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock
import pytest

try:
    from moto import mock_aws
    MOTO_AVAILABLE = True
except ImportError:
    MOTO_AVAILABLE = False
    mock_aws = None

import boto3

# Import Lambda handlers
from src.lambdas.data_fetcher.handler import lambda_handler as data_fetcher_handler
from src.lambdas.feature_extractor.handler import lambda_handler as feature_extractor_handler
from src.lambdas.risk_analyzer.handler import lambda_handler as risk_analyzer_handler
from src.lambdas.report_generator.handler import lambda_handler as report_generator_handler


# ---------------------------------------------------------------------------
# Test Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def aws_credentials(monkeypatch):
    """Mock AWS credentials for testing."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def mock_bitopro_transactions():
    """Generate mock BitoPro transaction data."""
    base_time = datetime.now()
    
    transactions = []
    for i in range(50):
        # Create varied transaction patterns
        hour = i % 24
        amount = 1000.0 if i % 5 == 0 else 1234.56  # Some round numbers
        
        transactions.append({
            "transaction_id": f"TXN_{i:04d}",
            "timestamp": (base_time - timedelta(hours=i)).isoformat(),
            "from_account": f"account_{i % 10}",  # 10 different accounts
            "to_account": f"counterparty_{i % 5}",  # 5 counterparties
            "amount": amount,
            "currency": "BTC",
            "transaction_type": "transfer",
            "status": "completed",
            "fee": 0.001,
            "metadata": {"test": True}
        })
    
    return transactions


@pytest.fixture
def mock_bedrock_response():
    """Generate mock Bedrock API response."""
    def _generate_response(features: Dict[str, Any]) -> Dict[str, Any]:
        # Simulate AI analysis based on features
        risk_score = 30.0
        risk_factors = []
        
        if features.get("total_volume", 0) > 10000:
            risk_score += 20
            risk_factors.append("High transaction volume")
        
        if features.get("night_transaction_ratio", 0) > 0.3:
            risk_score += 15
            risk_factors.append("Frequent night transactions")
        
        if features.get("round_number_ratio", 0) > 0.3:
            risk_score += 15
            risk_factors.append("Suspicious round number amounts")
        
        risk_score = min(risk_score, 100.0)
        
        if risk_score >= 76:
            risk_level = "critical"
        elif risk_score >= 51:
            risk_level = "high"
        elif risk_score >= 26:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        if not risk_factors:
            risk_factors = ["No significant risk indicators detected"]
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "explanation": f"Analysis based on {len(risk_factors)} risk factors",
            "confidence": 0.85
        }
    
    return _generate_response


# ---------------------------------------------------------------------------
# End-to-End Integration Test
# ---------------------------------------------------------------------------

@pytest.mark.integration
class TestEndToEndWorkflow:
    """
    End-to-end integration test for complete workflow.
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 3.1, 3.11, 4.1, 4.7, 8.1, 8.9,
                  9.1, 9.2, 9.3, 9.4, 9.5**
    """
    
    def test_complete_workflow_with_mocked_services(
        self,
        aws_credentials,
        mock_bitopro_transactions,
        mock_bedrock_response,
        monkeypatch
    ):
        """
        Test complete workflow from data ingestion to report generation.
        
        This test:
        1. Mocks BitoPro API to return test transactions
        2. Runs Data Fetcher Lambda
        3. Verifies raw data stored in S3 (Requirement 1.4, 9.1)
        4. Runs Feature Extractor Lambda
        5. Verifies features stored in S3 (Requirement 3.11, 9.2)
        6. Mocks Bedrock API for risk analysis
        7. Runs Risk Analyzer Lambda
        8. Verifies risk assessments in S3 and DynamoDB (Requirement 4.7, 9.3, 9.5)
        9. Runs Report Generator Lambda
        10. Verifies final report in S3 (Requirement 8.9, 9.4)
        11. Validates report contains expected data (Requirement 8.1)
        """
        if not MOTO_AVAILABLE:
            pytest.skip("moto not available for AWS mocking")
        
        with mock_aws():
            # Setup AWS resources
            s3_client = boto3.client("s3", region_name="us-east-1")
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
            
            # Create S3 buckets (Requirement 9.1, 9.2, 9.3, 9.4)
            raw_bucket = "test-raw-data"
            features_bucket = "test-features"
            risk_scores_bucket = "test-risk-scores"
            reports_bucket = "test-reports"
            
            for bucket in [raw_bucket, features_bucket, risk_scores_bucket, reports_bucket]:
                s3_client.create_bucket(Bucket=bucket)
            
            # Create DynamoDB table (Requirement 9.5)
            table_name = "test-accounts"
            table = dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": "account_id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "account_id", "AttributeType": "S"}],
                BillingMode="PAY_PER_REQUEST"
            )
            
            # Create Secrets Manager secret (Requirement 1.1)
            secrets_client.create_secret(
                Name="test-bitopro-api-key",
                SecretString=json.dumps({"api_key": "test_key", "api_secret": "test_secret"})
            )
            
            # Set environment variables
            monkeypatch.setenv("RAW_DATA_BUCKET", raw_bucket)
            monkeypatch.setenv("FEATURES_BUCKET", features_bucket)
            monkeypatch.setenv("RISK_SCORES_BUCKET", risk_scores_bucket)
            monkeypatch.setenv("REPORTS_BUCKET", reports_bucket)
            monkeypatch.setenv("DYNAMODB_TABLE", table_name)
            monkeypatch.setenv("BITOPRO_SECRET_ID", "test-bitopro-api-key")
            
            # --- Step 1: Data Fetcher ---
            # Mock BitoPro API client (Requirement 1.2)
            with patch("src.utils.bitopro_client.BitoproClient.fetch_transactions") as mock_fetch:
                mock_fetch.return_value = mock_bitopro_transactions
                
                # Invoke Data Fetcher Lambda
                data_fetcher_event = {
                    "start_time": (datetime.now() - timedelta(days=1)).isoformat(),
                    "end_time": datetime.now().isoformat(),
                    "limit": 1000
                }
                
                data_fetcher_response = data_fetcher_handler(data_fetcher_event, None)
                
                # Verify response
                assert data_fetcher_response["statusCode"] == 200
                body = json.loads(data_fetcher_response["body"])
                assert "s3_uri" in body
                assert body["valid_count"] > 0
                
                raw_data_s3_uri = body["s3_uri"]
                
                # Requirement 1.4, 9.1: Verify raw data stored in S3
                bucket, key = raw_data_s3_uri.replace("s3://", "").split("/", 1)
                response = s3_client.get_object(Bucket=bucket, Key=key)
                raw_data = json.loads(response["Body"].read().decode("utf-8"))
                
                assert len(raw_data) > 0
                assert all("transaction_id" in txn for txn in raw_data)
                assert all("amount" in txn for txn in raw_data)
            
            # --- Step 2: Feature Extractor ---
            # Invoke Feature Extractor Lambda
            feature_extractor_event = {
                "s3_uri": raw_data_s3_uri
            }
            
            feature_extractor_response = feature_extractor_handler(feature_extractor_event, None)
            
            # Verify response
            assert feature_extractor_response["statusCode"] == 200
            body = json.loads(feature_extractor_response["body"])
            assert "s3_uri" in body
            assert body["accounts_processed"] > 0
            
            features_s3_uri = body["s3_uri"]
            
            # Requirement 3.11, 9.2: Verify features stored in S3
            bucket, key = features_s3_uri.replace("s3://", "").split("/", 1)
            response = s3_client.get_object(Bucket=bucket, Key=key)
            features_data = json.loads(response["Body"].read().decode("utf-8"))
            
            assert len(features_data) > 0
            # Requirement 3.1: Verify features grouped by account
            assert all("account_id" in f for f in features_data)
            # Verify all required feature fields present
            required_fields = [
                "total_volume", "transaction_count", "avg_transaction_size",
                "max_transaction_size", "unique_counterparties",
                "night_transaction_ratio", "rapid_transaction_count",
                "round_number_ratio", "concentration_score", "velocity_score"
            ]
            for feature in features_data:
                for field in required_fields:
                    assert field in feature, f"Missing field {field} in features"
            
            # --- Step 3: Risk Analyzer ---
            # Mock Bedrock API (Requirement 4.1)
            def mock_invoke_model(modelId, body):
                request_body = json.loads(body)
                prompt = request_body["messages"][0]["content"]
                
                # Extract features from prompt (simplified)
                # In real test, parse the prompt to get actual feature values
                mock_features = {
                    "total_volume": 15000,
                    "night_transaction_ratio": 0.2,
                    "round_number_ratio": 0.2
                }
                
                risk_assessment = mock_bedrock_response(mock_features)
                
                response_body = {
                    "content": [{
                        "text": json.dumps(risk_assessment)
                    }]
                }
                
                mock_response = MagicMock()
                mock_response.__getitem__.return_value.read.return_value = json.dumps(response_body).encode()
                return mock_response
            
            with patch("boto3.client") as mock_boto_client:
                # Setup mock clients
                mock_bedrock = MagicMock()
                mock_bedrock.invoke_model.side_effect = mock_invoke_model
                
                def client_factory(service_name, **kwargs):
                    if service_name == "bedrock-runtime":
                        return mock_bedrock
                    elif service_name == "s3":
                        return s3_client
                    elif service_name == "secretsmanager":
                        return secrets_client
                    else:
                        return boto3.client(service_name, **kwargs)
                
                mock_boto_client.side_effect = client_factory
                
                # Also patch boto3.resource for DynamoDB
                with patch("boto3.resource") as mock_boto_resource:
                    def resource_factory(service_name, **kwargs):
                        if service_name == "dynamodb":
                            return dynamodb
                        else:
                            return boto3.resource(service_name, **kwargs)
                    
                    mock_boto_resource.side_effect = resource_factory
                    
                    # Invoke Risk Analyzer Lambda
                    risk_analyzer_event = {
                        "s3_uri": features_s3_uri
                    }
                    
                    risk_analyzer_response = risk_analyzer_handler(risk_analyzer_event, None)
                    
                    # Verify response
                    assert risk_analyzer_response["statusCode"] == 200
                    body = json.loads(risk_analyzer_response["body"])
                    assert "s3_uri" in body
                    assert body["accounts_analyzed"] > 0
                    
                    risk_scores_s3_uri = body["s3_uri"]
                    
                    # Requirement 9.3: Verify risk assessments stored in S3
                    bucket, key = risk_scores_s3_uri.replace("s3://", "").split("/", 1)
                    response = s3_client.get_object(Bucket=bucket, Key=key)
                    risk_assessments = json.loads(response["Body"].read().decode("utf-8"))
                    
                    assert len(risk_assessments) > 0
                    # Requirement 4.1: Verify risk assessment structure
                    for assessment in risk_assessments:
                        assert "account_id" in assessment
                        assert "risk_score" in assessment
                        assert "risk_level" in assessment
                        assert "risk_factors" in assessment
                        assert "explanation" in assessment
                        assert "confidence" in assessment
                        # Verify risk score in valid range
                        assert 0 <= assessment["risk_score"] <= 100
                        # Verify risk level is valid
                        assert assessment["risk_level"] in ["low", "medium", "high", "critical"]
                    
                    # Requirement 4.7, 9.5: Verify risk assessments stored in DynamoDB
                    scan_response = table.scan()
                    ddb_items = scan_response.get("Items", [])
                    assert len(ddb_items) > 0
                    
                    for item in ddb_items:
                        assert "account_id" in item
                        assert "risk_score" in item
                        assert "risk_level" in item
                    
                    # --- Step 4: Report Generator ---
                    # Invoke Report Generator Lambda
                    report_generator_event = {
                        "s3_uri": risk_scores_s3_uri,
                        "total_transactions": len(mock_bitopro_transactions)
                    }
                    
                    report_generator_response = report_generator_handler(report_generator_event, None)
                    
                    # Verify response
                    assert report_generator_response["statusCode"] == 200
                    body = json.loads(report_generator_response["body"])
                    assert "report_s3_uri" in body
                    assert "report_id" in body
                    
                    report_s3_uri = body["report_s3_uri"]
                    
                    # Requirement 8.9, 9.4: Verify report stored in S3
                    bucket, key = report_s3_uri.replace("s3://", "").split("/", 1)
                    response = s3_client.get_object(Bucket=bucket, Key=key)
                    report_html = response["Body"].read().decode("utf-8")
                    
                    assert len(report_html) > 0
                    assert "<!DOCTYPE html>" in report_html
                    assert "Crypto Suspicious Account Detection" in report_html
                    
                    # Requirement 8.1: Verify report contains expected data
                    assert body["total_accounts"] > 0
                    assert body["total_transactions"] == len(mock_bitopro_transactions)
                    assert "average_risk_score" in body
                    assert "risk_distribution" in body
                    
                    # Verify risk distribution
                    risk_dist = body["risk_distribution"]
                    assert isinstance(risk_dist, dict)
                    total_in_dist = sum(risk_dist.values())
                    assert total_in_dist == body["total_accounts"]
                    
                    # Verify charts were generated
                    assert "chart_uris" in body
                    
                    # Verify summary.json exists
                    summary_key = key.replace("presentation.html", "summary.json")
                    summary_response = s3_client.get_object(Bucket=bucket, Key=summary_key)
                    summary_data = json.loads(summary_response["Body"].read().decode("utf-8"))
                    
                    assert "total_accounts" in summary_data
                    assert "risk_distribution" in summary_data
                    assert "average_risk_score" in summary_data
                    assert "top_suspicious_accounts" in summary_data
    
    def test_workflow_handles_empty_transactions(self, aws_credentials, monkeypatch):
        """Test workflow handles empty transaction data gracefully."""
        if not MOTO_AVAILABLE:
            pytest.skip("moto not available for AWS mocking")
        
        with mock_aws():
            # Setup AWS resources
            s3_client = boto3.client("s3", region_name="us-east-1")
            
            raw_bucket = "test-raw-data"
            s3_client.create_bucket(Bucket=raw_bucket)
            
            monkeypatch.setenv("RAW_DATA_BUCKET", raw_bucket)
            monkeypatch.setenv("BITOPRO_SECRET_ID", "test-bitopro-api-key")
            
            # Create secret
            secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
            secrets_client.create_secret(
                Name="test-bitopro-api-key",
                SecretString=json.dumps({"api_key": "test_key"})
            )
            
            # Mock BitoPro API to return empty list
            with patch("src.utils.bitopro_client.BitoproClient.fetch_transactions") as mock_fetch:
                mock_fetch.return_value = []
                
                data_fetcher_event = {
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat()
                }
                
                response = data_fetcher_handler(data_fetcher_event, None)
                
                # Should still succeed but with zero transactions
                assert response["statusCode"] == 200
                body = json.loads(response["body"])
                assert body["valid_count"] == 0
    
    def test_workflow_handles_invalid_transactions(self, aws_credentials, monkeypatch):
        """Test workflow filters out invalid transactions."""
        if not MOTO_AVAILABLE:
            pytest.skip("moto not available for AWS mocking")
        
        with mock_aws():
            # Setup AWS resources
            s3_client = boto3.client("s3", region_name="us-east-1")
            
            raw_bucket = "test-raw-data"
            s3_client.create_bucket(Bucket=raw_bucket)
            
            monkeypatch.setenv("RAW_DATA_BUCKET", raw_bucket)
            monkeypatch.setenv("BITOPRO_SECRET_ID", "test-bitopro-api-key")
            
            # Create secret
            secrets_client = boto3.client("secretsmanager", region_name="us-east-1")
            secrets_client.create_secret(
                Name="test-bitopro-api-key",
                SecretString=json.dumps({"api_key": "test_key"})
            )
            
            # Mock transactions with some invalid ones
            mixed_transactions = [
                {  # Valid
                    "transaction_id": "TXN_001",
                    "timestamp": datetime.now().isoformat(),
                    "from_account": "acc_1",
                    "to_account": "acc_2",
                    "amount": 100.0,
                    "currency": "BTC",
                    "transaction_type": "transfer",
                    "status": "completed",
                    "fee": 0.001
                },
                {  # Invalid - negative amount
                    "transaction_id": "TXN_002",
                    "timestamp": datetime.now().isoformat(),
                    "from_account": "acc_1",
                    "to_account": "acc_2",
                    "amount": -100.0,
                    "currency": "BTC",
                    "transaction_type": "transfer",
                    "status": "completed",
                    "fee": 0.001
                },
                {  # Invalid - missing required field
                    "transaction_id": "TXN_003",
                    "timestamp": datetime.now().isoformat(),
                    # Missing from_account
                    "to_account": "acc_2",
                    "amount": 100.0,
                    "currency": "BTC"
                }
            ]
            
            with patch("src.utils.bitopro_client.BitoproClient.fetch_transactions") as mock_fetch:
                mock_fetch.return_value = mixed_transactions
                
                data_fetcher_event = {
                    "start_time": datetime.now().isoformat(),
                    "end_time": datetime.now().isoformat()
                }
                
                response = data_fetcher_handler(data_fetcher_event, None)
                
                # Should succeed with only valid transactions
                assert response["statusCode"] == 200
                body = json.loads(response["body"])
                assert body["valid_count"] == 1
                assert body["invalid_count"] == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
