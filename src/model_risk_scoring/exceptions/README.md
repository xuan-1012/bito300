# Custom Exceptions for AWS Model Risk Scoring

This module defines custom exception classes for error handling throughout the AWS Model Risk Scoring system.

## Exception Classes

### ValidationError
Raised when feature validation fails.

**Use cases:**
- Invalid feature values (negative numbers, out-of-range ratios)
- Missing required fields
- Type mismatches

**Attributes:**
- `message`: Detailed error message
- `field`: Optional field name that failed validation

**Example:**
```python
from src.model_risk_scoring.exceptions import ValidationError

if total_volume < 0:
    raise ValidationError(
        "total_volume must be non-negative",
        field="total_volume"
    )
```

### InferenceError
Raised when inference fails and fallback is not enabled or also fails.

**Use cases:**
- Both primary inference and fallback fail
- Fallback is disabled and primary inference fails
- Unrecoverable inference errors

**Attributes:**
- `message`: Detailed error message
- `original_error`: Optional original exception that caused the failure

**Example:**
```python
from src.model_risk_scoring.exceptions import InferenceError

try:
    result = bedrock_engine.infer(features)
except Exception as e:
    if not fallback_enabled:
        raise InferenceError(
            "Inference failed and fallback is disabled",
            original_error=e
        )
```

### BedrockError
Raised when Amazon Bedrock API calls fail.

**Use cases:**
- Bedrock service errors
- API throttling (429 status)
- Invalid model IDs
- Network timeouts

**Attributes:**
- `message`: Detailed error message
- `model_id`: Bedrock model ID that was being called
- `status_code`: Optional HTTP status code

**Example:**
```python
from src.model_risk_scoring.exceptions import BedrockError

try:
    response = bedrock_client.invoke_model(...)
except Exception as e:
    raise BedrockError(
        "Bedrock API call failed",
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        status_code=429
    )
```

### SageMakerError
Raised when SageMaker Endpoint calls fail.

**Use cases:**
- Endpoint not found
- Endpoint not in service
- Service unavailable (503 status)
- Invalid input format

**Attributes:**
- `message`: Detailed error message
- `endpoint_name`: SageMaker endpoint name
- `status_code`: Optional HTTP status code

**Example:**
```python
from src.model_risk_scoring.exceptions import SageMakerError

try:
    response = sagemaker_client.invoke_endpoint(...)
except Exception as e:
    raise SageMakerError(
        "SageMaker endpoint call failed",
        endpoint_name="fraud-detection-endpoint",
        status_code=503
    )
```

### ParseError
Raised when parsing LLM or model responses fails.

**Use cases:**
- Invalid JSON in LLM response
- Missing required fields in response
- Malformed response structure
- Type conversion errors

**Attributes:**
- `message`: Detailed error message
- `response_text`: Optional original response text

**Example:**
```python
from src.model_risk_scoring.exceptions import ParseError

try:
    result = json.loads(llm_response)
except json.JSONDecodeError as e:
    raise ParseError(
        "Failed to parse LLM response as JSON",
        response_text=llm_response
    )
```

### ConfigurationError
Raised when model configuration is invalid.

**Use cases:**
- Invalid inference mode
- Missing required configuration parameters
- Out-of-range configuration values
- Incompatible configuration combinations

**Attributes:**
- `message`: Detailed error message
- `config_field`: Optional configuration field that is invalid

**Example:**
```python
from src.model_risk_scoring.exceptions import ConfigurationError

if max_requests_per_second >= 1.0:
    raise ConfigurationError(
        "max_requests_per_second must be < 1.0",
        config_field="max_requests_per_second"
    )
```

## Exception Hierarchy

All custom exceptions inherit from Python's built-in `Exception` class:

```
Exception
├── ValidationError
├── InferenceError
├── BedrockError
├── SageMakerError
├── ParseError
└── ConfigurationError
```

This allows you to catch all custom exceptions as generic `Exception` if needed:

```python
try:
    result = model_service.infer_risk(features)
except Exception as e:
    logger.error(f"Error during inference: {e}")
```

## Requirements Mapping

This module satisfies the following requirements:

- **Requirement 8.4**: Error handling with detailed messages
- **Requirement 8.5**: Specific exception types for different error scenarios
- **Requirement 12.9**: Configuration validation with ConfigurationError

## Testing

The module has 100% test coverage. Run tests with:

```bash
pytest tests/unit/test_exceptions.py -v
```

## Demo

See `examples/exceptions_demo.py` for usage examples of all exception classes.
