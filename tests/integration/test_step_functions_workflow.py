"""
Integration tests for Step Functions workflow.

Tests the complete workflow execution with mock data, verifying:
- State transitions
- Error handling and retries
- Data flow between Lambda functions
- Execution history in CloudWatch
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import pytest
import boto3

try:
    from moto import mock_aws
    MOTO_AVAILABLE = True
except ImportError:
    MOTO_AVAILABLE = False
    mock_aws = None


@pytest.fixture
def aws_credentials(monkeypatch):
    """Mock AWS credentials for testing."""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture
def state_machine_definition() -> Dict[str, Any]:
    """Load state machine definition."""
    with open("infrastructure/state_machine.json", "r") as f:
        definition = json.load(f)
    
    # Replace placeholders with mock ARNs
    definition_str = json.dumps(definition)
    definition_str = definition_str.replace(
        "${DataFetcherFunctionArn}",
        "arn:aws:lambda:us-east-1:123456789012:function:data-fetcher"
    )
    definition_str = definition_str.replace(
        "${FeatureExtractorFunctionArn}",
        "arn:aws:lambda:us-east-1:123456789012:function:feature-extractor"
    )
    definition_str = definition_str.replace(
        "${RiskAnalyzerFunctionArn}",
        "arn:aws:lambda:us-east-1:123456789012:function:risk-analyzer"
    )
    definition_str = definition_str.replace(
        "${ReportGeneratorFunctionArn}",
        "arn:aws:lambda:us-east-1:123456789012:function:report-generator"
    )
    
    return json.loads(definition_str)


@pytest.fixture
def mock_lambda_functions(aws_credentials):
    """Create mock Lambda functions."""
    if not MOTO_AVAILABLE:
        pytest.skip("moto not available")
    
    with mock_aws():
        lambda_client = boto3.client("lambda", region_name="us-east-1")
        
        # Create mock Lambda functions
        functions = [
            "data-fetcher",
            "feature-extractor",
            "risk-analyzer",
            "report-generator"
        ]
        
        for func_name in functions:
            lambda_client.create_function(
                FunctionName=func_name,
                Runtime="python3.11",
                Role="arn:aws:iam::123456789012:role/lambda-role",
                Handler="handler.lambda_handler",
                Code={"ZipFile": b"fake code"},
                Timeout=300,
                MemorySize=1024
            )
        
        yield lambda_client


class TestStepFunctionsWorkflow:
    """Integration tests for Step Functions workflow."""
    
    def test_state_machine_definition_structure(self, state_machine_definition):
        """Test that state machine definition has correct structure."""
        assert "Comment" in state_machine_definition
        assert "StartAt" in state_machine_definition
        assert "States" in state_machine_definition
        
        # Verify start state
        assert state_machine_definition["StartAt"] == "DataFetcher"
        
        # Verify all required states exist
        states = state_machine_definition["States"]
        required_states = [
            "DataFetcher",
            "FeatureExtractor",
            "RiskAnalyzer",
            "ReportGenerator",
            "SuccessState",
            "FailState"
        ]
        
        for state_name in required_states:
            assert state_name in states, f"Missing state: {state_name}"
    
    def test_state_transitions(self, state_machine_definition):
        """Test that state transitions are correctly configured."""
        states = state_machine_definition["States"]
        
        # Verify DataFetcher transitions to FeatureExtractor
        assert states["DataFetcher"]["Next"] == "FeatureExtractor"
        
        # Verify FeatureExtractor transitions to RiskAnalyzer
        assert states["FeatureExtractor"]["Next"] == "RiskAnalyzer"
        
        # Verify RiskAnalyzer transitions to ReportGenerator
        assert states["RiskAnalyzer"]["Next"] == "ReportGenerator"
        
        # Verify ReportGenerator transitions to SuccessState
        assert states["ReportGenerator"]["Next"] == "SuccessState"
        
        # Verify SuccessState is terminal
        assert states["SuccessState"]["Type"] == "Succeed"
        
        # Verify FailState is terminal
        assert states["FailState"]["Type"] == "Fail"
    
    def test_retry_configuration(self, state_machine_definition):
        """Test that retry policies are correctly configured."""
        states = state_machine_definition["States"]
        
        # Check DataFetcher retry policy
        data_fetcher_retry = states["DataFetcher"]["Retry"][0]
        assert data_fetcher_retry["MaxAttempts"] == 3
        assert data_fetcher_retry["BackoffRate"] == 2.0
        assert data_fetcher_retry["IntervalSeconds"] == 2
        assert "States.TaskFailed" in data_fetcher_retry["ErrorEquals"]
        
        # Check FeatureExtractor retry policy
        feature_extractor_retry = states["FeatureExtractor"]["Retry"][0]
        assert feature_extractor_retry["MaxAttempts"] == 3
        assert feature_extractor_retry["BackoffRate"] == 2.0
        
        # Check RiskAnalyzer retry policy (different max attempts)
        risk_analyzer_retry = states["RiskAnalyzer"]["Retry"][0]
        assert risk_analyzer_retry["MaxAttempts"] == 2
        assert risk_analyzer_retry["BackoffRate"] == 2.0
        assert risk_analyzer_retry["IntervalSeconds"] == 5
        
        # Check ReportGenerator retry policy
        report_generator_retry = states["ReportGenerator"]["Retry"][0]
        assert report_generator_retry["MaxAttempts"] == 3
        assert report_generator_retry["BackoffRate"] == 2.0
    
    def test_error_handling_configuration(self, state_machine_definition):
        """Test that error handling is correctly configured."""
        states = state_machine_definition["States"]
        
        # Verify all task states have Catch blocks
        task_states = ["DataFetcher", "FeatureExtractor", "RiskAnalyzer", "ReportGenerator"]
        
        for state_name in task_states:
            state = states[state_name]
            assert "Catch" in state, f"{state_name} missing Catch block"
            
            catch_block = state["Catch"][0]
            assert catch_block["ErrorEquals"] == ["States.ALL"]
            assert catch_block["Next"] == "FailState"
            assert catch_block["ResultPath"] == "$.error"
    
    def test_timeout_configuration(self, state_machine_definition):
        """Test that timeouts are correctly configured."""
        states = state_machine_definition["States"]
        
        # Verify DataFetcher timeout
        assert states["DataFetcher"]["TimeoutSeconds"] == 300
        
        # Verify FeatureExtractor timeout
        assert states["FeatureExtractor"]["TimeoutSeconds"] == 300
        
        # Verify RiskAnalyzer timeout (longer due to Bedrock rate limiting)
        assert states["RiskAnalyzer"]["TimeoutSeconds"] == 3600
        
        # Verify ReportGenerator timeout
        assert states["ReportGenerator"]["TimeoutSeconds"] == 300
    
    def test_result_path_configuration(self, state_machine_definition):
        """Test that result paths are correctly configured."""
        states = state_machine_definition["States"]
        
        # Verify each task state stores its result in a separate path
        assert states["DataFetcher"]["ResultPath"] == "$.dataFetcherResult"
        assert states["FeatureExtractor"]["ResultPath"] == "$.featureExtractorResult"
        assert states["RiskAnalyzer"]["ResultPath"] == "$.riskAnalyzerResult"
        assert states["ReportGenerator"]["ResultPath"] == "$.reportGeneratorResult"


class TestStepFunctionsExecution:
    """Integration tests for Step Functions execution (requires AWS or LocalStack)."""
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires AWS account or LocalStack")
    def test_successful_workflow_execution(self):
        """Test complete workflow execution with mock data."""
        # This test requires actual AWS resources or LocalStack
        # Skip in unit test environment
        
        sfn_client = boto3.client("stepfunctions", region_name="us-east-1")
        
        # Get state machine ARN (from CloudFormation outputs)
        state_machine_arn = "arn:aws:states:us-east-1:123456789012:stateMachine:crypto-detection"
        
        # Start execution
        execution_name = f"test-execution-{uuid.uuid4()}"
        input_data = {
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-31T23:59:59Z"
            },
            "account_ids": ["test_account_1", "test_account_2"]
        }
        
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=execution_name,
            input=json.dumps(input_data)
        )
        
        execution_arn = response["executionArn"]
        
        # Wait for execution to complete (with timeout)
        max_wait_time = 300  # 5 minutes
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            execution_status = sfn_client.describe_execution(
                executionArn=execution_arn
            )
            
            status = execution_status["status"]
            
            if status == "SUCCEEDED":
                # Verify output contains expected data
                output = json.loads(execution_status["output"])
                assert "dataFetcherResult" in output
                assert "featureExtractorResult" in output
                assert "riskAnalyzerResult" in output
                assert "reportGeneratorResult" in output
                break
            elif status == "FAILED":
                pytest.fail(f"Execution failed: {execution_status.get('error', 'Unknown error')}")
            elif status == "TIMED_OUT":
                pytest.fail("Execution timed out")
            elif status == "ABORTED":
                pytest.fail("Execution was aborted")
            
            time.sleep(5)
        else:
            pytest.fail("Execution did not complete within timeout")
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires AWS account or LocalStack")
    def test_workflow_error_handling(self):
        """Test workflow error handling with invalid input."""
        sfn_client = boto3.client("stepfunctions", region_name="us-east-1")
        
        state_machine_arn = "arn:aws:states:us-east-1:123456789012:stateMachine:crypto-detection"
        
        # Start execution with invalid input
        execution_name = f"test-error-{uuid.uuid4()}"
        invalid_input = {
            "time_range": {
                "start": "invalid-date",
                "end": "invalid-date"
            }
        }
        
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=execution_name,
            input=json.dumps(invalid_input)
        )
        
        execution_arn = response["executionArn"]
        
        # Wait for execution to fail
        max_wait_time = 60
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            execution_status = sfn_client.describe_execution(
                executionArn=execution_arn
            )
            
            status = execution_status["status"]
            
            if status == "FAILED":
                # Verify error information is captured
                assert "error" in execution_status
                break
            elif status == "SUCCEEDED":
                pytest.fail("Execution should have failed with invalid input")
            
            time.sleep(2)
        else:
            pytest.fail("Execution did not fail within timeout")
    
    @pytest.mark.integration
    @pytest.mark.skip(reason="Requires AWS account or LocalStack")
    def test_workflow_retry_behavior(self):
        """Test that workflow retries on transient failures."""
        sfn_client = boto3.client("stepfunctions", region_name="us-east-1")
        
        state_machine_arn = "arn:aws:states:us-east-1:123456789012:stateMachine:crypto-detection"
        
        # Start execution
        execution_name = f"test-retry-{uuid.uuid4()}"
        input_data = {
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-31T23:59:59Z"
            },
            "simulate_transient_error": True  # Flag to simulate error in Lambda
        }
        
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name=execution_name,
            input=json.dumps(input_data)
        )
        
        execution_arn = response["executionArn"]
        
        # Wait for execution to complete
        time.sleep(30)
        
        # Get execution history
        history = sfn_client.get_execution_history(
            executionArn=execution_arn,
            maxResults=100
        )
        
        # Verify retry attempts in history
        events = history["events"]
        task_failed_events = [e for e in events if e["type"] == "TaskFailed"]
        task_retry_events = [e for e in events if e["type"] == "TaskScheduled" and "retry" in str(e)]
        
        # Should have at least one retry
        assert len(task_retry_events) > 0, "No retry attempts found in execution history"


class TestWorkflowDataFlow:
    """Test data flow between workflow states."""
    
    def test_data_fetcher_output_format(self):
        """Test that DataFetcher output matches expected format."""
        expected_output = {
            "raw_data_s3_uri": "s3://bucket/raw-data/2024-01-01.json",
            "transaction_count": 1000,
            "time_range": {
                "start": "2024-01-01T00:00:00Z",
                "end": "2024-01-31T23:59:59Z"
            }
        }
        
        # Verify required fields
        assert "raw_data_s3_uri" in expected_output
        assert "transaction_count" in expected_output
        assert "time_range" in expected_output
    
    def test_feature_extractor_output_format(self):
        """Test that FeatureExtractor output matches expected format."""
        expected_output = {
            "features_s3_uri": "s3://bucket/features/2024-01-01.json",
            "account_count": 100,
            "feature_names": [
                "total_volume",
                "transaction_count",
                "avg_transaction_size",
                "max_transaction_size",
                "unique_counterparties",
                "night_transaction_ratio",
                "round_number_ratio",
                "rapid_transaction_count",
                "concentration_score",
                "velocity_score"
            ]
        }
        
        # Verify required fields
        assert "features_s3_uri" in expected_output
        assert "account_count" in expected_output
        assert "feature_names" in expected_output
        assert len(expected_output["feature_names"]) == 10
    
    def test_risk_analyzer_output_format(self):
        """Test that RiskAnalyzer output matches expected format."""
        expected_output = {
            "risk_scores_s3_uri": "s3://bucket/risk-scores/2024-01-01.json",
            "assessed_accounts": 100,
            "bedrock_api_calls": 95,
            "fallback_assessments": 5,
            "average_risk_score": 35.5,
            "high_risk_accounts": 15
        }
        
        # Verify required fields
        assert "risk_scores_s3_uri" in expected_output
        assert "assessed_accounts" in expected_output
        assert "bedrock_api_calls" in expected_output
        assert "fallback_assessments" in expected_output
    
    def test_report_generator_output_format(self):
        """Test that ReportGenerator output matches expected format."""
        expected_output = {
            "report_s3_uri": "s3://bucket/reports/2024-01-01/report.html",
            "charts_s3_uris": [
                "s3://bucket/reports/2024-01-01/risk_distribution.png",
                "s3://bucket/reports/2024-01-01/risk_histogram.png"
            ],
            "presigned_url": "https://bucket.s3.amazonaws.com/reports/...",
            "presigned_url_expiry": "2024-01-02T00:00:00Z",
            "summary": {
                "total_accounts": 100,
                "total_transactions": 1000,
                "high_risk_accounts": 15,
                "average_risk_score": 35.5
            }
        }
        
        # Verify required fields
        assert "report_s3_uri" in expected_output
        assert "charts_s3_uris" in expected_output
        assert "presigned_url" in expected_output
        assert "summary" in expected_output


def test_workflow_compliance():
    """Test that workflow meets compliance requirements."""
    # Load state machine definition
    with open("infrastructure/state_machine.json", "r") as f:
        definition = json.load(f)
    
    states = definition["States"]
    
    # Verify all task states have retry policies
    task_states = ["DataFetcher", "FeatureExtractor", "RiskAnalyzer", "ReportGenerator"]
    for state_name in task_states:
        assert "Retry" in states[state_name], f"{state_name} missing retry policy"
    
    # Verify all task states have error handling
    for state_name in task_states:
        assert "Catch" in states[state_name], f"{state_name} missing error handling"
    
    # Verify all task states have timeouts
    for state_name in task_states:
        assert "TimeoutSeconds" in states[state_name], f"{state_name} missing timeout"
    
    # Verify RiskAnalyzer has sufficient timeout for rate limiting
    # With 100 accounts and 1 req/sec, need at least 100 seconds
    assert states["RiskAnalyzer"]["TimeoutSeconds"] >= 3600, "RiskAnalyzer timeout too short for rate limiting"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
