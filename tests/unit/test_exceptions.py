"""Unit tests for custom exceptions."""

import pytest
from src.model_risk_scoring.exceptions import (
    ValidationError,
    InferenceError,
    BedrockError,
    SageMakerError,
    ParseError,
    ConfigurationError,
)


class TestValidationError:
    """Tests for ValidationError exception."""
    
    def test_validation_error_with_message_only(self):
        """Test ValidationError with message only."""
        error = ValidationError("Invalid feature value")
        assert str(error) == "Invalid feature value"
        assert error.message == "Invalid feature value"
        assert error.field is None
    
    def test_validation_error_with_field(self):
        """Test ValidationError with field name."""
        error = ValidationError("Value must be non-negative", field="total_volume")
        assert error.message == "Value must be non-negative"
        assert error.field == "total_volume"
    
    def test_validation_error_is_exception(self):
        """Test ValidationError is an Exception."""
        error = ValidationError("Test error")
        assert isinstance(error, Exception)
    
    def test_validation_error_can_be_raised(self):
        """Test ValidationError can be raised and caught."""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("Test validation error", field="test_field")
        
        assert exc_info.value.message == "Test validation error"
        assert exc_info.value.field == "test_field"


class TestInferenceError:
    """Tests for InferenceError exception."""
    
    def test_inference_error_with_message_only(self):
        """Test InferenceError with message only."""
        error = InferenceError("Inference failed")
        assert str(error) == "Inference failed"
        assert error.message == "Inference failed"
        assert error.original_error is None
    
    def test_inference_error_with_original_error(self):
        """Test InferenceError with original error."""
        original = ValueError("Original error")
        error = InferenceError("Inference failed", original_error=original)
        assert error.message == "Inference failed"
        assert error.original_error == original
    
    def test_inference_error_is_exception(self):
        """Test InferenceError is an Exception."""
        error = InferenceError("Test error")
        assert isinstance(error, Exception)
    
    def test_inference_error_can_be_raised(self):
        """Test InferenceError can be raised and caught."""
        with pytest.raises(InferenceError) as exc_info:
            raise InferenceError("Test inference error")
        
        assert exc_info.value.message == "Test inference error"


class TestBedrockError:
    """Tests for BedrockError exception."""
    
    def test_bedrock_error_with_message_only(self):
        """Test BedrockError with message only."""
        error = BedrockError("Bedrock API call failed")
        assert str(error) == "Bedrock API call failed"
        assert error.message == "Bedrock API call failed"
        assert error.model_id is None
        assert error.status_code is None
    
    def test_bedrock_error_with_model_id(self):
        """Test BedrockError with model ID."""
        error = BedrockError(
            "API call failed",
            model_id="anthropic.claude-3-sonnet-20240229-v1:0"
        )
        assert error.message == "API call failed"
        assert error.model_id == "anthropic.claude-3-sonnet-20240229-v1:0"
    
    def test_bedrock_error_with_status_code(self):
        """Test BedrockError with status code."""
        error = BedrockError("API call failed", status_code=429)
        assert error.message == "API call failed"
        assert error.status_code == 429
    
    def test_bedrock_error_with_all_attributes(self):
        """Test BedrockError with all attributes."""
        error = BedrockError(
            "Throttling error",
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            status_code=429
        )
        assert error.message == "Throttling error"
        assert error.model_id == "anthropic.claude-3-sonnet-20240229-v1:0"
        assert error.status_code == 429
    
    def test_bedrock_error_is_exception(self):
        """Test BedrockError is an Exception."""
        error = BedrockError("Test error")
        assert isinstance(error, Exception)
    
    def test_bedrock_error_can_be_raised(self):
        """Test BedrockError can be raised and caught."""
        with pytest.raises(BedrockError) as exc_info:
            raise BedrockError("Test bedrock error", model_id="test-model")
        
        assert exc_info.value.message == "Test bedrock error"
        assert exc_info.value.model_id == "test-model"


class TestSageMakerError:
    """Tests for SageMakerError exception."""
    
    def test_sagemaker_error_with_message_only(self):
        """Test SageMakerError with message only."""
        error = SageMakerError("SageMaker endpoint call failed")
        assert str(error) == "SageMaker endpoint call failed"
        assert error.message == "SageMaker endpoint call failed"
        assert error.endpoint_name is None
        assert error.status_code is None
    
    def test_sagemaker_error_with_endpoint_name(self):
        """Test SageMakerError with endpoint name."""
        error = SageMakerError(
            "Endpoint not found",
            endpoint_name="fraud-detection-endpoint"
        )
        assert error.message == "Endpoint not found"
        assert error.endpoint_name == "fraud-detection-endpoint"
    
    def test_sagemaker_error_with_status_code(self):
        """Test SageMakerError with status code."""
        error = SageMakerError("Endpoint call failed", status_code=503)
        assert error.message == "Endpoint call failed"
        assert error.status_code == 503
    
    def test_sagemaker_error_with_all_attributes(self):
        """Test SageMakerError with all attributes."""
        error = SageMakerError(
            "Service unavailable",
            endpoint_name="fraud-detection-endpoint",
            status_code=503
        )
        assert error.message == "Service unavailable"
        assert error.endpoint_name == "fraud-detection-endpoint"
        assert error.status_code == 503
    
    def test_sagemaker_error_is_exception(self):
        """Test SageMakerError is an Exception."""
        error = SageMakerError("Test error")
        assert isinstance(error, Exception)
    
    def test_sagemaker_error_can_be_raised(self):
        """Test SageMakerError can be raised and caught."""
        with pytest.raises(SageMakerError) as exc_info:
            raise SageMakerError("Test sagemaker error", endpoint_name="test-endpoint")
        
        assert exc_info.value.message == "Test sagemaker error"
        assert exc_info.value.endpoint_name == "test-endpoint"


class TestParseError:
    """Tests for ParseError exception."""
    
    def test_parse_error_with_message_only(self):
        """Test ParseError with message only."""
        error = ParseError("Failed to parse JSON response")
        assert str(error) == "Failed to parse JSON response"
        assert error.message == "Failed to parse JSON response"
        assert error.response_text is None
    
    def test_parse_error_with_response_text(self):
        """Test ParseError with response text."""
        response = '{"invalid": json}'
        error = ParseError("Invalid JSON", response_text=response)
        assert error.message == "Invalid JSON"
        assert error.response_text == response
    
    def test_parse_error_is_exception(self):
        """Test ParseError is an Exception."""
        error = ParseError("Test error")
        assert isinstance(error, Exception)
    
    def test_parse_error_can_be_raised(self):
        """Test ParseError can be raised and caught."""
        with pytest.raises(ParseError) as exc_info:
            raise ParseError("Test parse error", response_text="bad response")
        
        assert exc_info.value.message == "Test parse error"
        assert exc_info.value.response_text == "bad response"


class TestConfigurationError:
    """Tests for ConfigurationError exception."""
    
    def test_configuration_error_with_message_only(self):
        """Test ConfigurationError with message only."""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert error.message == "Invalid configuration"
        assert error.config_field is None
    
    def test_configuration_error_with_config_field(self):
        """Test ConfigurationError with config field."""
        error = ConfigurationError(
            "Invalid inference mode",
            config_field="inference_mode"
        )
        assert error.message == "Invalid inference mode"
        assert error.config_field == "inference_mode"
    
    def test_configuration_error_is_exception(self):
        """Test ConfigurationError is an Exception."""
        error = ConfigurationError("Test error")
        assert isinstance(error, Exception)
    
    def test_configuration_error_can_be_raised(self):
        """Test ConfigurationError can be raised and caught."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Test config error", config_field="test_field")
        
        assert exc_info.value.message == "Test config error"
        assert exc_info.value.config_field == "test_field"


class TestExceptionHierarchy:
    """Tests for exception hierarchy and behavior."""
    
    def test_all_exceptions_inherit_from_exception(self):
        """Test all custom exceptions inherit from Exception."""
        exceptions = [
            ValidationError("test"),
            InferenceError("test"),
            BedrockError("test"),
            SageMakerError("test"),
            ParseError("test"),
            ConfigurationError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, Exception)
    
    def test_exceptions_can_be_caught_as_exception(self):
        """Test custom exceptions can be caught as generic Exception."""
        with pytest.raises(Exception):
            raise ValidationError("test")
        
        with pytest.raises(Exception):
            raise InferenceError("test")
        
        with pytest.raises(Exception):
            raise BedrockError("test")
    
    def test_exceptions_have_unique_types(self):
        """Test each exception has a unique type."""
        exceptions = [
            ValidationError("test"),
            InferenceError("test"),
            BedrockError("test"),
            SageMakerError("test"),
            ParseError("test"),
            ConfigurationError("test"),
        ]
        
        # Check that each exception has a different type
        types = [type(exc) for exc in exceptions]
        assert len(types) == len(set(types))
