"""
Demo script showing usage of core data models.

This script demonstrates how to create and use the core data models
for the AWS Model Risk Scoring system.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from model_risk_scoring.models import (
    InferenceMode,
    RiskLevel,
    TransactionFeatures,
    RiskAssessment,
    ModelConfig,
    FeatureConfig,
)


def demo_inference_modes():
    """Demonstrate InferenceMode enum usage."""
    print("=== InferenceMode Demo ===")
    print(f"Supervised mode: {InferenceMode.SUPERVISED.value}")
    print(f"Unsupervised mode: {InferenceMode.UNSUPERVISED.value}")
    print(f"Fallback mode: {InferenceMode.FALLBACK.value}")
    print()


def demo_risk_levels():
    """Demonstrate RiskLevel enum usage."""
    print("=== RiskLevel Demo ===")
    for level in RiskLevel:
        print(f"{level.level.upper()}: {level.color}")
    print()


def demo_transaction_features():
    """Demonstrate TransactionFeatures creation."""
    print("=== TransactionFeatures Demo ===")
    
    features = TransactionFeatures(
        account_id="account_12345",
        total_volume=150000.0,
        transaction_count=50,
        avg_transaction_size=3000.0,
        max_transaction_size=25000.0,
        unique_counterparties=5,
        night_transaction_ratio=0.4,
        rapid_transaction_count=15,
        round_number_ratio=0.6,
        concentration_score=0.8,
        velocity_score=12.5
    )
    
    print(f"Account ID: {features.account_id}")
    print(f"Total Volume: ${features.total_volume:,.2f}")
    print(f"Transaction Count: {features.transaction_count}")
    print(f"Night Transaction Ratio: {features.night_transaction_ratio:.1%}")
    print(f"Round Number Ratio: {features.round_number_ratio:.1%}")
    print(f"Concentration Score: {features.concentration_score:.2f}")
    print()


def demo_risk_assessment():
    """Demonstrate RiskAssessment creation."""
    print("=== RiskAssessment Demo ===")
    
    assessment = RiskAssessment(
        account_id="account_12345",
        risk_score=75.5,
        risk_level=RiskLevel.HIGH,
        risk_factors=[
            "High transaction volume ($150,000)",
            "High night transaction ratio (40%)",
            "High round number ratio (60%)",
            "High concentration score (0.8)"
        ],
        explanation="Account shows multiple suspicious patterns including high volume, "
                   "frequent night transactions, and concentrated counterparty relationships.",
        confidence=0.85,
        inference_mode=InferenceMode.UNSUPERVISED,
        model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        inference_time_ms=2500.0,
        fallback_used=False
    )
    
    print(f"Account: {assessment.account_id}")
    print(f"Risk Score: {assessment.risk_score:.1f}/100")
    print(f"Risk Level: {assessment.risk_level.level.upper()} ({assessment.risk_level.color})")
    print(f"Confidence: {assessment.confidence:.1%}")
    print(f"Inference Mode: {assessment.inference_mode.value}")
    print(f"Model ID: {assessment.model_id}")
    print(f"Inference Time: {assessment.inference_time_ms:.1f}ms")
    print(f"\nRisk Factors:")
    for factor in assessment.risk_factors:
        print(f"  - {factor}")
    print(f"\nExplanation: {assessment.explanation}")
    print()


def demo_model_config():
    """Demonstrate ModelConfig creation."""
    print("=== ModelConfig Demo ===")
    
    # Unsupervised mode config
    print("Unsupervised Mode Configuration:")
    config_unsupervised = ModelConfig(
        inference_mode=InferenceMode.UNSUPERVISED,
        bedrock_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
        bedrock_max_tokens=1024,
        bedrock_temperature=0.0,
        max_requests_per_second=0.9,
        fallback_enabled=True
    )
    print(f"  Mode: {config_unsupervised.inference_mode.value}")
    print(f"  Bedrock Model: {config_unsupervised.bedrock_model_id}")
    print(f"  Max RPS: {config_unsupervised.max_requests_per_second}")
    print(f"  Fallback Enabled: {config_unsupervised.fallback_enabled}")
    print()
    
    # Supervised mode config
    print("Supervised Mode Configuration:")
    config_supervised = ModelConfig(
        inference_mode=InferenceMode.SUPERVISED,
        sagemaker_endpoint_name="fraud-detection-xgboost-endpoint",
        sagemaker_content_type="text/csv",
        fallback_enabled=True
    )
    print(f"  Mode: {config_supervised.inference_mode.value}")
    print(f"  SageMaker Endpoint: {config_supervised.sagemaker_endpoint_name}")
    print(f"  Content Type: {config_supervised.sagemaker_content_type}")
    print()


def demo_feature_config():
    """Demonstrate FeatureConfig creation."""
    print("=== FeatureConfig Demo ===")
    
    config = FeatureConfig()
    
    print("Feature Names (in order):")
    for i, name in enumerate(config.feature_names, 1):
        print(f"  {i}. {name}")
    
    print("\nValidation Rules (sample):")
    for feature in ["total_volume", "night_transaction_ratio", "concentration_score"]:
        rules = config.validation_rules[feature]
        print(f"  {feature}: min={rules['min']}, max={rules['max']}")
    print()


def demo_config_validation():
    """Demonstrate configuration validation."""
    print("=== Configuration Validation Demo ===")
    
    # Valid configuration
    print("Creating valid configuration...")
    try:
        config = ModelConfig(
            inference_mode=InferenceMode.UNSUPERVISED,
            max_requests_per_second=0.9
        )
        print("✓ Valid configuration created successfully")
    except ValueError as e:
        print(f"✗ Validation failed: {e}")
    
    # Invalid max_requests_per_second
    print("\nTrying invalid max_requests_per_second (>= 1.0)...")
    try:
        config = ModelConfig(
            inference_mode=InferenceMode.UNSUPERVISED,
            max_requests_per_second=1.5
        )
        print("✓ Configuration created")
    except ValueError as e:
        print(f"✗ Validation failed (expected): {e}")
    
    # Invalid temperature
    print("\nTrying invalid bedrock_temperature (> 1.0)...")
    try:
        config = ModelConfig(
            inference_mode=InferenceMode.UNSUPERVISED,
            bedrock_temperature=1.5
        )
        print("✓ Configuration created")
    except ValueError as e:
        print(f"✗ Validation failed (expected): {e}")
    
    # Missing endpoint for supervised mode
    print("\nTrying supervised mode without endpoint...")
    try:
        config = ModelConfig(
            inference_mode=InferenceMode.SUPERVISED,
            sagemaker_endpoint_name=None
        )
        print("✓ Configuration created")
    except ValueError as e:
        print(f"✗ Validation failed (expected): {e}")
    print()


def main():
    """Run all demos."""
    print("=" * 60)
    print("AWS Model Risk Scoring - Data Models Demo")
    print("=" * 60)
    print()
    
    demo_inference_modes()
    demo_risk_levels()
    demo_transaction_features()
    demo_risk_assessment()
    demo_model_config()
    demo_feature_config()
    demo_config_validation()
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
