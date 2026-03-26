# Utils Module

This module provides utility functions and classes for the AWS Model Risk Scoring system.

## Components

### FeatureProcessor

The `FeatureProcessor` class provides feature validation, normalization, and conversion capabilities for the AWS Model Risk Scoring system.

#### Overview

The FeatureProcessor ensures that transaction features meet all validation requirements before being used for model inference. It validates feature values, normalizes numerical features using Z-score normalization, and converts features to vectors for SageMaker endpoints.

#### Features

- **Validation**: Validates all feature values against defined rules
- **Normalization**: Applies Z-score normalization using optional scaler parameters
- **Vector Conversion**: Converts features to consistent vector format for model inference
- **Error Handling**: Provides detailed error messages for validation failures

#### Usage

##### Basic Validation

```python
from src.model_risk_scoring.models.data_models import TransactionFeatures
from src.model_risk_scoring.utils import FeatureProcessor

# Create features
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

# Validate
processor = FeatureProcessor()
processor.validate(features)  # Returns True or raises ValidationError
```

##### Normalization Without Scaler Parameters

```python
# Normalize (returns raw values if no scaler params)
normalized = processor.normalize(features)
# Returns: {"total_volume": 50000.0, "transaction_count": 100.0, ...}
```

##### Normalization With Scaler Parameters

```python
# Define scaler parameters (mean and std for each feature)
scaler_params = {
    "total_volume": {"mean": 50000.0, "std": 10000.0},
    "transaction_count": {"mean": 100.0, "std": 20.0},
    "velocity_score": {"mean": 2.0, "std": 1.0}
}

processor = FeatureProcessor(scaler_params=scaler_params)
normalized = processor.normalize(features)
# Returns Z-score normalized values: (value - mean) / std
```

##### Feature Vector Conversion

```python
# Convert to vector for SageMaker inference
vector = processor.to_vector(features)
# Returns: [50000.0, 100.0, 500.0, 5000.0, 20.0, 0.2, 5.0, 0.3, 0.5, 2.5]
```

#### Validation Rules

The FeatureProcessor validates the following rules:

1. **account_id**: Must be non-empty string
2. **total_volume**: Must be >= 0
3. **transaction_count**: Must be > 0
4. **night_transaction_ratio**: Must be in [0, 1]
5. **round_number_ratio**: Must be in [0, 1]
6. **concentration_score**: Must be in [0, 1]

#### Error Handling

When validation fails, the processor raises a `ValidationError` with:
- Detailed error message describing the issue
- Field name that failed validation

```python
from src.model_risk_scoring.exceptions import ValidationError

try:
    processor.validate(invalid_features)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
    print(f"Field: {e.field}")
```

#### Feature Vector Order

The `to_vector()` method returns features in the following order:

1. total_volume
2. transaction_count
3. avg_transaction_size
4. max_transaction_size
5. unique_counterparties
6. night_transaction_ratio
7. rapid_transaction_count
8. round_number_ratio
9. concentration_score
10. velocity_score

This order is consistent with the `FeatureConfig.feature_names` definition.

#### Z-Score Normalization

When scaler parameters are provided, the processor applies Z-score normalization:

```
normalized_value = (value - mean) / std
```

Features without scaler parameters remain unchanged. If `std` is 0, the normalized value is set to 0.0 to avoid division by zero.

#### Examples

See `examples/feature_processor_demo.py` for comprehensive usage examples including:
- Basic validation
- Error handling
- Normalization with and without scaler parameters
- Feature vector conversion
- Real-world scenario with suspicious account detection

#### Testing

Run unit tests:

```bash
python -m pytest tests/unit/test_feature_processor.py -v
```

The test suite includes:
- Validation rule tests for all features
- Boundary value tests
- Normalization tests with and without scaler parameters
- Feature vector conversion tests
- Error handling tests

#### Integration

The FeatureProcessor is used by:
- **ModelService**: Validates features before inference
- **SageMakerInferenceEngine**: Converts features to vectors for endpoint calls
- **BedrockInferenceEngine**: Validates features before building prompts

#### Requirements Mapping

This implementation satisfies:
- **Requirement 1.1**: Validates account_id is non-empty
- **Requirement 1.2**: Validates total_volume >= 0
- **Requirement 1.3**: Validates transaction_count > 0
- **Requirement 1.4**: Validates night_transaction_ratio in [0, 1]
- **Requirement 1.5**: Validates round_number_ratio in [0, 1]
- **Requirement 1.6**: Validates concentration_score in [0, 1]
- **Requirement 1.7**: Raises ValidationError with detailed messages
- **Requirement 1.8**: Normalizes features using Z-score normalization
- **Requirement 1.9**: Uses scaler_params when provided
- **Requirement 1.10**: Returns normalized feature dictionary

---

### Risk Classifier

The `classify_risk_level()` function maps risk scores (0-100) to risk levels (LOW/MEDIUM/HIGH/CRITICAL) for clear categorization.

#### Overview

The risk classifier provides a simple, deterministic mapping from numerical risk scores to categorical risk levels. This enables clear communication of risk assessments and supports visualization with color-coded risk levels.

#### Usage

```python
from src.model_risk_scoring.utils import classify_risk_level
from src.model_risk_scoring.models.data_models import RiskLevel

# Classify a risk score
risk_score = 85.0
level = classify_risk_level(risk_score)

print(f"Risk Score: {risk_score}")
print(f"Risk Level: {level.level}")  # "critical"
print(f"Color Code: {level.color}")  # "#dc2626" (red)
```

#### Risk Level Mapping

The function uses the following mapping:

| Risk Score Range | Risk Level | Color Code | Color Name |
|-----------------|------------|------------|------------|
| 0 - 25          | LOW        | #16a34a    | Green      |
| 26 - 50         | MEDIUM     | #ca8a04    | Yellow     |
| 51 - 75         | HIGH       | #ea580c    | Orange     |
| 76 - 100        | CRITICAL   | #dc2626    | Red        |

#### Boundary Behavior

- Score 25: LOW (upper boundary inclusive)
- Score 26: MEDIUM (lower boundary inclusive)
- Score 50: MEDIUM (upper boundary inclusive)
- Score 51: HIGH (lower boundary inclusive)
- Score 75: HIGH (upper boundary inclusive)
- Score 76: CRITICAL (lower boundary inclusive)

#### Error Handling

The function validates that the risk score is in the valid range [0, 100]:

```python
try:
    level = classify_risk_level(150)  # Invalid score
except ValueError as e:
    print(e)  # "risk_score must be between 0 and 100, got 150"
```

#### Examples

See `examples/risk_classifier_demo.py` for comprehensive usage examples including:
- Boundary value classification
- Float score classification
- Error handling
- Color code usage for visualization

#### Testing

Run unit tests:

```bash
python -m pytest tests/unit/test_risk_classifier.py -v
```

The test suite includes:
- Boundary value tests (0, 25, 26, 50, 51, 75, 76, 100)
- Mid-range value tests for each level
- Float value tests
- Invalid input tests (negative, > 100)
- Near-boundary tests

#### Integration

The risk classifier is used by:
- **ModelService**: Classifies risk scores after inference
- **RiskAssessment**: Stores both risk_score and risk_level
- **Visualization**: Uses color codes for dashboard display

#### Requirements Mapping

This implementation satisfies:
- **Requirement 6.1**: Classifies scores 0-25 as LOW
- **Requirement 6.2**: Classifies scores 26-50 as MEDIUM
- **Requirement 6.3**: Classifies scores 51-75 as HIGH
- **Requirement 6.4**: Classifies scores 76-100 as CRITICAL
- **Requirement 6.5**: Ensures consistency between risk_score and risk_level
- **Requirement 6.7-6.10**: Provides color codes for visualization
