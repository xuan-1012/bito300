"""Custom exceptions for risk scoring system."""


class ValidationError(Exception):
    """
    Raised when feature validation fails.
    
    This exception is raised when TransactionFeatures do not meet
    validation requirements (e.g., negative values, out-of-range ratios).
    
    Attributes:
        message: Detailed error message describing the validation failure
        field: Optional field name that failed validation
    """
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class InferenceError(Exception):
    """
    Raised when inference fails and fallback is not enabled or also fails.
    
    This exception is raised when both primary inference (Bedrock/SageMaker)
    and fallback mechanisms fail, or when fallback is disabled.
    
    Attributes:
        message: Detailed error message describing the inference failure
        original_error: Optional original exception that caused the failure
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class BedrockError(Exception):
    """
    Raised when Amazon Bedrock API calls fail.
    
    This exception is raised when Bedrock InvokeModel API calls fail
    due to service errors, throttling, or invalid requests.
    
    Attributes:
        message: Detailed error message describing the Bedrock failure
        model_id: Bedrock model ID that was being called
        status_code: Optional HTTP status code from the API response
    """
    
    def __init__(self, message: str, model_id: str = None, status_code: int = None):
        self.message = message
        self.model_id = model_id
        self.status_code = status_code
        super().__init__(self.message)


class SageMakerError(Exception):
    """
    Raised when SageMaker Endpoint calls fail.
    
    This exception is raised when SageMaker InvokeEndpoint API calls fail
    due to endpoint unavailability, service errors, or invalid inputs.
    
    Attributes:
        message: Detailed error message describing the SageMaker failure
        endpoint_name: SageMaker endpoint name that was being called
        status_code: Optional HTTP status code from the API response
    """
    
    def __init__(self, message: str, endpoint_name: str = None, status_code: int = None):
        self.message = message
        self.endpoint_name = endpoint_name
        self.status_code = status_code
        super().__init__(self.message)


class ParseError(Exception):
    """
    Raised when parsing LLM or model responses fails.
    
    This exception is raised when the system cannot parse JSON responses
    from Bedrock LLM or SageMaker models, or when responses are malformed.
    
    Attributes:
        message: Detailed error message describing the parsing failure
        response_text: Optional original response text that failed to parse
    """
    
    def __init__(self, message: str, response_text: str = None):
        self.message = message
        self.response_text = response_text
        super().__init__(self.message)


class ConfigurationError(Exception):
    """
    Raised when model configuration is invalid.
    
    This exception is raised when ModelConfig contains invalid values
    (e.g., invalid inference mode, missing required parameters).
    
    Attributes:
        message: Detailed error message describing the configuration issue
        config_field: Optional configuration field that is invalid
    """
    
    def __init__(self, message: str, config_field: str = None):
        self.message = message
        self.config_field = config_field
        super().__init__(self.message)


# Export all exceptions
__all__ = [
    'ValidationError',
    'InferenceError',
    'BedrockError',
    'SageMakerError',
    'ParseError',
    'ConfigurationError',
]
