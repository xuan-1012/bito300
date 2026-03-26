"""
Integration tests for Report Generator Lambda handler.

Tests the complete lambda_handler function with mocked AWS services.
"""

import json
import pytest
from datetime import datetime
from unittest.mock import MagicMock, patch, Mock
from src.common.models import RiskAssessment, RiskLevel


class TestReportGeneratorLambdaHandler:
    """Test suite for lambda_handler function (Task 8.4)."""

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_success(self, mock_get_clients):
        """Test successful lambda handler execution with all components."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_clients.dynamodb = mock_dynamodb
        mock_get_clients.return_value = mock_clients

        # Mock S3 get_object to return risk assessments
        risk_assessments_data = [
            {
                "account_id": "acc_001",
                "risk_score": 85.0,
                "risk_level": "critical",
                "risk_factors": ["High volume", "Night transactions"],
                "explanation": "Critical risk account",
                "confidence": 0.9,
                "timestamp": datetime.now().isoformat(),
            },
            {
                "account_id": "acc_002",
                "risk_score": 60.0,
                "risk_level": "high",
                "risk_factors": ["Round numbers"],
                "explanation": "High risk account",
                "confidence": 0.85,
                "timestamp": datetime.now().isoformat(),
            },
        ]
        
        mock_response = {
            "Body": Mock(read=lambda: json.dumps(risk_assessments_data).encode("utf-8"))
        }
        mock_s3.get_object.return_value = mock_response
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/presigned-url"

        # Mock DynamoDB table
        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb.Table.return_value = mock_table

        # Create event
        event = {
            "s3_uri": "s3://test-bucket/risk-scores/test.json",
            "total_transactions": 100,
        }

        # Execute handler
        result = lambda_handler(event, None)

        # Verify response
        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        
        # Requirement 8.9: Return report S3 URI
        assert "report_s3_uri" in body
        assert body["report_s3_uri"].startswith("s3://")
        
        # Requirement 16.5: Pre-signed URL with 24-hour expiry
        assert "presigned_url" in body
        assert body["presigned_url"] == "https://example.com/presigned-url"
        
        # Verify summary statistics
        assert body["total_accounts"] == 2
        assert body["total_transactions"] == 100
        assert "average_risk_score" in body
        assert "risk_distribution" in body
        
        # Verify S3 operations
        # Should read risk assessments
        assert mock_s3.get_object.called
        
        # Should store summary.json, top_suspicious_accounts.json, and presentation.html
        assert mock_s3.put_object.call_count >= 3
        
        # Verify pre-signed URL generation with 24-hour expiry
        mock_s3.generate_presigned_url.assert_called_once()
        call_args = mock_s3.generate_presigned_url.call_args
        assert call_args[0][0] == "get_object"
        assert call_args[1]["ExpiresIn"] == 86400  # 24 hours

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_empty_assessments(self, mock_get_clients):
        """Test handler with no risk assessments."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_clients.dynamodb = mock_dynamodb
        mock_get_clients.return_value = mock_clients

        # Mock S3 to return empty list
        mock_response = {
            "Body": Mock(read=lambda: json.dumps([]).encode("utf-8"))
        }
        mock_s3.get_object.return_value = mock_response
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/presigned-url"

        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb.Table.return_value = mock_table

        event = {
            "s3_uri": "s3://test-bucket/risk-scores/empty.json",
            "total_transactions": 0,
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["total_accounts"] == 0
        assert body["total_transactions"] == 0

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_missing_s3_uri(self, mock_get_clients):
        """Test handler with missing s3_uri in event."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        event = {}
        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_s3_read_failure(self, mock_get_clients):
        """Test handler when S3 read fails."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_get_clients.return_value = mock_clients

        # Mock S3 to raise exception
        mock_s3.get_object.side_effect = Exception("S3 read failed")

        event = {
            "s3_uri": "s3://test-bucket/risk-scores/test.json",
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 500
        body = json.loads(result["body"])
        assert "error" in body

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_dynamodb_failure_non_fatal(self, mock_get_clients):
        """Test that DynamoDB read failure is non-fatal."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_clients.dynamodb = mock_dynamodb
        mock_get_clients.return_value = mock_clients

        # Mock S3 to return valid data
        risk_assessments_data = [
            {
                "account_id": "acc_001",
                "risk_score": 50.0,
                "risk_level": "medium",
                "risk_factors": ["Test"],
                "explanation": "Test account",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
            }
        ]
        mock_response = {
            "Body": Mock(read=lambda: json.dumps(risk_assessments_data).encode("utf-8"))
        }
        mock_s3.get_object.return_value = mock_response
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/presigned-url"

        # Mock DynamoDB to fail
        mock_table = MagicMock()
        mock_table.scan.side_effect = Exception("DynamoDB scan failed")
        mock_dynamodb.Table.return_value = mock_table

        event = {
            "s3_uri": "s3://test-bucket/risk-scores/test.json",
        }

        # Should still succeed despite DynamoDB failure
        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["total_accounts"] == 1

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_presigned_url_failure_non_fatal(self, mock_get_clients):
        """Test that pre-signed URL generation failure is non-fatal."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_clients.dynamodb = mock_dynamodb
        mock_get_clients.return_value = mock_clients

        # Mock S3 to return valid data
        risk_assessments_data = [
            {
                "account_id": "acc_001",
                "risk_score": 50.0,
                "risk_level": "medium",
                "risk_factors": ["Test"],
                "explanation": "Test account",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
            }
        ]
        mock_response = {
            "Body": Mock(read=lambda: json.dumps(risk_assessments_data).encode("utf-8"))
        }
        mock_s3.get_object.return_value = mock_response
        mock_s3.put_object.return_value = {}
        
        # Mock pre-signed URL generation to fail
        mock_s3.generate_presigned_url.side_effect = Exception("URL generation failed")

        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb.Table.return_value = mock_table

        event = {
            "s3_uri": "s3://test-bucket/risk-scores/test.json",
        }

        # Should still succeed despite pre-signed URL failure
        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["total_accounts"] == 1
        # Pre-signed URL should be None
        assert body["presigned_url"] is None

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_stores_all_outputs(self, mock_get_clients):
        """Test that handler stores all required outputs to S3."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_clients.dynamodb = mock_dynamodb
        mock_get_clients.return_value = mock_clients

        # Mock S3 to return valid data
        risk_assessments_data = [
            {
                "account_id": "acc_001",
                "risk_score": 85.0,
                "risk_level": "critical",
                "risk_factors": ["High volume"],
                "explanation": "Critical risk",
                "confidence": 0.9,
                "timestamp": datetime.now().isoformat(),
            }
        ]
        mock_response = {
            "Body": Mock(read=lambda: json.dumps(risk_assessments_data).encode("utf-8"))
        }
        mock_s3.get_object.return_value = mock_response
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/presigned-url"

        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb.Table.return_value = mock_table

        event = {
            "s3_uri": "s3://test-bucket/risk-scores/test.json",
            "total_transactions": 50,
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200

        # Verify all required S3 put_object calls
        put_calls = mock_s3.put_object.call_args_list
        
        # Should have at least 3 calls: summary.json, top_suspicious_accounts.json, presentation.html
        # Plus 2 more for charts (risk_distribution.png, risk_score_histogram.png)
        assert len(put_calls) >= 3
        
        # Verify keys contain expected patterns
        keys = [call[1]["Key"] for call in put_calls]
        assert any("summary.json" in key for key in keys)
        assert any("top_suspicious_accounts.json" in key for key in keys)
        assert any("presentation.html" in key for key in keys)
        
        # Verify all uploads use AES256 encryption (Requirement 9.6)
        for call in put_calls:
            assert call[1]["ServerSideEncryption"] == "AES256"

    @patch("src.lambdas.report_generator.handler.get_aws_clients")
    def test_lambda_handler_event_body_parsing(self, mock_get_clients):
        """Test handler can parse s3_uri from event body."""
        from src.lambdas.report_generator.handler import lambda_handler
        
        # Mock AWS clients
        mock_s3 = MagicMock()
        mock_dynamodb = MagicMock()
        mock_clients = MagicMock()
        mock_clients.s3 = mock_s3
        mock_clients.dynamodb = mock_dynamodb
        mock_get_clients.return_value = mock_clients

        # Mock S3 to return valid data
        risk_assessments_data = [
            {
                "account_id": "acc_001",
                "risk_score": 50.0,
                "risk_level": "medium",
                "risk_factors": ["Test"],
                "explanation": "Test",
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat(),
            }
        ]
        mock_response = {
            "Body": Mock(read=lambda: json.dumps(risk_assessments_data).encode("utf-8"))
        }
        mock_s3.get_object.return_value = mock_response
        mock_s3.put_object.return_value = {}
        mock_s3.generate_presigned_url.return_value = "https://example.com/presigned-url"

        # Mock DynamoDB
        mock_table = MagicMock()
        mock_table.scan.return_value = {"Items": []}
        mock_dynamodb.Table.return_value = mock_table

        # Test with s3_uri in body (as string)
        event = {
            "body": json.dumps({
                "s3_uri": "s3://test-bucket/risk-scores/test.json"
            })
        }

        result = lambda_handler(event, None)

        assert result["statusCode"] == 200
        body = json.loads(result["body"])
        assert body["total_accounts"] == 1
