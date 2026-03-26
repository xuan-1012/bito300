"""
Demo script showing usage of custom exceptions in the risk scoring system.

This script demonstrates how to use the custom exception classes for
error handling in the AWS Model Risk Scoring system.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_risk_scoring.exceptions import (
    ValidationError,
    InferenceError,
    BedrockError,
    SageMakerError,
    ParseError,
    ConfigurationError,
)


def demo_validation_error():
    """Demonstrate ValidationError usage."""
    print("\n=== ValidationError Demo ===")
    
    try:
        # Simulate feature validation failure
        total_volume = -1000
        if total_volume < 0:
            raise ValidationError(
                "total_volume must be non-negative",
                field="total_volume"
            )
    except ValidationError as e:
        print(f"Caught ValidationError: {e.message}")
        print(f"Failed field: {e.field}")


def demo_inference_error():
    """Demonstrate InferenceError usage."""
    print("\n=== InferenceError Demo ===")
    
    try:
        # Simulate inference failure
        original_error = ConnectionError("Network timeout")
        raise InferenceError(
            "Inference failed and fallback is disabled",
            original_error=original_error
        )
    except InferenceError as e:
        print(f"Caught InferenceError: {e.message}")
        print(f"Original error: {e.original_error}")


def demo_bedrock_error():
    """Demonstrate BedrockError usage."""
    print("\n=== BedrockError Demo ===")
    
    try:
        # Simulate Bedrock API failure
        raise BedrockError(
            "Bedrock API throttling limit exceeded",
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            status_code=429
        )
    except BedrockError as e:
        print(f"Caught BedrockError: {e.message}")
        print(f"Model ID: {e.model_id}")
        print(f"Status code: {e.status_code}")


def demo_sagemaker_error():
    """Demonstrate SageMakerError usage."""
    print("\n=== SageMakerError Demo ===")
    
    try:
        # Simulate SageMaker endpoint failure
        raise SageMakerError(
            "SageMaker endpoint is not in service",
            endpoint_name="fraud-detection-endpoint",
            status_code=503
        )
    except SageMakerError as e:
        print(f"Caught SageMakerError: {e.message}")
        print(f"Endpoint name: {e.endpoint_name}")
        print(f"Status code: {e.status_code}")


def demo_parse_error():
    """Demonstrate ParseError usage."""
    print("\n=== ParseError Demo ===")
    
    try:
        # Simulate JSON parsing failure
        response = '{"risk_score": invalid_json}'
        raise ParseError(
            "Failed to parse LLM response as JSON",
            response_text=response
        )
    except ParseError as e:
        print(f"Caught ParseError: {e.message}")
        print(f"Response text: {e.response_text}")


def demo_configuration_error():
    """Demonstrate ConfigurationError usage."""
    print("\n=== ConfigurationError Demo ===")
    
    try:
        # Simulate configuration validation failure
        max_rps = 1.5
        if max_rps >= 1.0:
            raise ConfigurationError(
                "max_requests_per_second must be < 1.0",
                config_field="max_requests_per_second"
            )
    except ConfigurationError as e:
        print(f"Caught ConfigurationError: {e.message}")
        print(f"Config field: {e.config_field}")


def demo_exception_hierarchy():
    """Demonstrate exception hierarchy and catching."""
    print("\n=== Exception Hierarchy Demo ===")
    
    # All custom exceptions can be caught as generic Exception
    exceptions_to_test = [
        ValidationError("test"),
        InferenceError("test"),
        BedrockError("test"),
        SageMakerError("test"),
        ParseError("test"),
        ConfigurationError("test"),
    ]
    
    for exc in exceptions_to_test:
        try:
            raise exc
        except Exception as e:
            print(f"Caught {type(e).__name__} as Exception: {e}")


def main():
    """Run all exception demos."""
    print("=" * 60)
    print("AWS Model Risk Scoring - Custom Exceptions Demo")
    print("=" * 60)
    
    demo_validation_error()
    demo_inference_error()
    demo_bedrock_error()
    demo_sagemaker_error()
    demo_parse_error()
    demo_configuration_error()
    demo_exception_hierarchy()
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
