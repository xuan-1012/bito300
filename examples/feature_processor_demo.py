"""
Demo script for FeatureProcessor usage.

This script demonstrates how to use the FeatureProcessor class to validate,
normalize, and convert transaction features for model inference.
"""

from src.model_risk_scoring.exceptions import ValidationError
from src.model_risk_scoring.models.data_models import TransactionFeatures
from src.model_risk_scoring.utils import FeatureProcessor


def demo_basic_validation():
    """Demonstrate basic feature validation."""
    print("=" * 60)
    print("Demo 1: Basic Feature Validation")
    print("=" * 60)
    
    # Create a valid feature set
    valid_features = TransactionFeatures(
        account_id="ACC123",
        total_volume=50000.0,
        transaction_count=100,
        avg_transaction_size=500.0,
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=0.2,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=2.5
    )
    
    processor = FeatureProcessor()
    
    try:
        is_valid = processor.validate(valid_features)
        print(f"✓ Valid features passed validation: {is_valid}")
    except ValidationError as e:
        print(f"✗ Validation failed: {e.message}")
    
    print()


def demo_validation_errors():
    """Demonstrate validation error handling."""
    print("=" * 60)
    print("Demo 2: Validation Error Handling")
    print("=" * 60)
    
    processor = FeatureProcessor()
    
    # Test 1: Empty account_id
    print("\nTest 1: Empty account_id")
    invalid_features_1 = TransactionFeatures(
        account_id="",
        total_volume=50000.0,
        transaction_count=100,
        avg_transaction_size=500.0,
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=0.2,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=2.5
    )
    
    try:
        processor.validate(invalid_features_1)
    except ValidationError as e:
        print(f"✓ Caught expected error: {e.message}")
        print(f"  Field: {e.field}")
    
    # Test 2: Negative total_volume
    print("\nTest 2: Negative total_volume")
    invalid_features_2 = TransactionFeatures(
        account_id="ACC123",
        total_volume=-1000.0,
        transaction_count=100,
        avg_transaction_size=500.0,
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=0.2,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=2.5
    )
    
    try:
        processor.validate(invalid_features_2)
    except ValidationError as e:
        print(f"✓ Caught expected error: {e.message}")
        print(f"  Field: {e.field}")
    
    # Test 3: Invalid ratio (> 1)
    print("\nTest 3: Invalid night_transaction_ratio (> 1)")
    invalid_features_3 = TransactionFeatures(
        account_id="ACC123",
        total_volume=50000.0,
        transaction_count=100,
        avg_transaction_size=500.0,
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=1.5,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=2.5
    )
    
    try:
        processor.validate(invalid_features_3)
    except ValidationError as e:
        print(f"✓ Caught expected error: {e.message}")
        print(f"  Field: {e.field}")
    
    print()


def demo_normalization_without_params():
    """Demonstrate normalization without scaler parameters."""
    print("=" * 60)
    print("Demo 3: Normalization Without Scaler Parameters")
    print("=" * 60)
    
    features = TransactionFeatures(
        account_id="ACC123",
        total_volume=50000.0,
        transaction_count=100,
        avg_transaction_size=500.0,
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=0.2,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=2.5
    )
    
    processor = FeatureProcessor()
    normalized = processor.normalize(features)
    
    print("\nNormalized features (raw values, no scaling):")
    for feature_name, value in normalized.items():
        print(f"  {feature_name}: {value}")
    
    print()


def demo_normalization_with_params():
    """Demonstrate normalization with scaler parameters."""
    print("=" * 60)
    print("Demo 4: Normalization With Scaler Parameters")
    print("=" * 60)
    
    # Define scaler parameters (mean and std for each feature)
    scaler_params = {
        "total_volume": {"mean": 50000.0, "std": 10000.0},
        "transaction_count": {"mean": 100.0, "std": 20.0},
        "avg_transaction_size": {"mean": 500.0, "std": 100.0},
        "velocity_score": {"mean": 2.0, "std": 1.0}
    }
    
    features = TransactionFeatures(
        account_id="ACC123",
        total_volume=60000.0,  # 1 std above mean
        transaction_count=120,  # 1 std above mean
        avg_transaction_size=600.0,  # 1 std above mean
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=0.2,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=3.0  # 1 std above mean
    )
    
    processor = FeatureProcessor(scaler_params=scaler_params)
    normalized = processor.normalize(features)
    
    print("\nOriginal vs Normalized values:")
    print(f"  total_volume: {features.total_volume} → {normalized['total_volume']:.2f}")
    print(f"  transaction_count: {features.transaction_count} → {normalized['transaction_count']:.2f}")
    print(f"  avg_transaction_size: {features.avg_transaction_size} → {normalized['avg_transaction_size']:.2f}")
    print(f"  velocity_score: {features.velocity_score} → {normalized['velocity_score']:.2f}")
    print(f"\n  Features without scaler params remain unchanged:")
    print(f"  night_transaction_ratio: {normalized['night_transaction_ratio']}")
    print(f"  concentration_score: {normalized['concentration_score']}")
    
    print()


def demo_to_vector():
    """Demonstrate feature vector conversion."""
    print("=" * 60)
    print("Demo 5: Feature Vector Conversion")
    print("=" * 60)
    
    features = TransactionFeatures(
        account_id="ACC123",
        total_volume=50000.0,
        transaction_count=100,
        avg_transaction_size=500.0,
        max_transaction_size=5000.0,
        unique_counterparties=20,
        night_transaction_ratio=0.2,
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=2.5
    )
    
    processor = FeatureProcessor()
    vector = processor.to_vector(features)
    
    print("\nFeature vector (for SageMaker inference):")
    feature_names = [
        "total_volume",
        "transaction_count",
        "avg_transaction_size",
        "max_transaction_size",
        "unique_counterparties",
        "night_transaction_ratio",
        "rapid_transaction_count",
        "round_number_ratio",
        "concentration_score",
        "velocity_score"
    ]
    
    for name, value in zip(feature_names, vector):
        print(f"  {name}: {value}")
    
    print(f"\nVector length: {len(vector)}")
    print(f"Vector: {vector}")
    
    print()


def demo_real_world_scenario():
    """Demonstrate a real-world usage scenario."""
    print("=" * 60)
    print("Demo 6: Real-World Scenario")
    print("=" * 60)
    
    print("\nScenario: Processing features for a suspicious account")
    
    # High-risk account features
    suspicious_features = TransactionFeatures(
        account_id="SUSP456",
        total_volume=150000.0,  # High volume
        transaction_count=200,
        avg_transaction_size=750.0,
        max_transaction_size=10000.0,
        unique_counterparties=5,  # Low diversity
        night_transaction_ratio=0.6,  # High night activity
        rapid_transaction_count=25,  # Many rapid transactions
        round_number_ratio=0.8,  # High round number ratio
        concentration_score=0.9,  # High concentration
        velocity_score=15.0  # High velocity
    )
    
    # Scaler parameters from training data
    scaler_params = {
        "total_volume": {"mean": 50000.0, "std": 30000.0},
        "transaction_count": {"mean": 100.0, "std": 50.0},
        "velocity_score": {"mean": 5.0, "std": 3.0}
    }
    
    processor = FeatureProcessor(scaler_params=scaler_params)
    
    # Step 1: Validate
    print("\nStep 1: Validating features...")
    try:
        processor.validate(suspicious_features)
        print("✓ Features are valid")
    except ValidationError as e:
        print(f"✗ Validation failed: {e.message}")
        return
    
    # Step 2: Normalize
    print("\nStep 2: Normalizing features...")
    normalized = processor.normalize(suspicious_features)
    print(f"  Normalized total_volume: {normalized['total_volume']:.2f} (z-score)")
    print(f"  Normalized velocity_score: {normalized['velocity_score']:.2f} (z-score)")
    
    # Step 3: Convert to vector
    print("\nStep 3: Converting to feature vector for model inference...")
    vector = processor.to_vector(suspicious_features)
    print(f"  Vector ready for SageMaker: {len(vector)} features")
    
    # Step 4: Identify risk indicators
    print("\nStep 4: Risk indicators identified:")
    if suspicious_features.night_transaction_ratio > 0.3:
        print(f"  ⚠ High night transaction ratio: {suspicious_features.night_transaction_ratio:.1%}")
    if suspicious_features.round_number_ratio > 0.5:
        print(f"  ⚠ High round number ratio: {suspicious_features.round_number_ratio:.1%}")
    if suspicious_features.concentration_score > 0.7:
        print(f"  ⚠ High concentration score: {suspicious_features.concentration_score:.2f}")
    if suspicious_features.velocity_score > 10:
        print(f"  ⚠ High velocity: {suspicious_features.velocity_score:.1f} tx/hour")
    
    print("\n✓ Account flagged for further investigation")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("FeatureProcessor Demo")
    print("=" * 60)
    print()
    
    demo_basic_validation()
    demo_validation_errors()
    demo_normalization_without_params()
    demo_normalization_with_params()
    demo_to_vector()
    demo_real_world_scenario()
    
    print("=" * 60)
    print("Demo completed!")
    print("=" * 60)
