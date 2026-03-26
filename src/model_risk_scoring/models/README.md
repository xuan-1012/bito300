# AWS Model Risk Scoring - Data Models

This module contains the core data models for the AWS Model Risk Scoring system.

## Overview

The data models define the structure for:
- Transaction features used for risk assessment
- Risk assessment results
- Model and feature configurations
- Inference modes and risk levels

## Models

### Enums

#### InferenceMode

Defines the inference mode for risk assessment:

- `SUPERVISED`: Use SageMaker Endpoint with labeled training data
- `UNSUPERVISED`: Use Bedrock LLM without labeled data
- `FALLBACK`: Use rule-based engine when AI services are unavailable

```python
from model_risk_scoring.models import InferenceMode

mode = InferenceMode.UNSUPERVISED
print(mode.value)  # "unsupervised"
```

#### RiskLevel

Defines risk level classification with color codes for visualization:

- `LOW`: Green (#16a34a) - Risk score 0-25
- `MEDIUM`: Yellow (#ca8a04) - Risk score 26-50
- `HIGH`: Orange (#ea580c) - Risk score 51-75
- `CRITICAL`: Red (#dc2626) - Risk score 76-100

```python
from model_risk_scoring.models import RiskLevel

level = RiskLevel.HIGH
print(f"{level.level}: {level.color}")  # "high: #ea580c"
```

### Dataclasses

#### TransactionFeatures

Contains all extracted features from account transaction history.

**Fields:**
- `account_id` (str): Account identifier
- `total_volume` (float): Total transaction volume in USD
- `transaction_count` (int): Number of transactions
- `avg_transaction_size` (float): Average transaction amount in USD
- `max_transaction_size` (float): Maximum transaction amount in USD
- `unique_counterparties` (int): Number of unique counterparties
- `night_transaction_ratio` (float): Ratio of night transactions (0-1)
- `rapid_transaction_count` (int): Number of rapid consecutive transactions
- `round_number_ratio` (float): Ratio of round number amounts (0-1)
- `concentration_score` (float): Counterparty concentration score (0-1)
- `velocity_score` (float): Transaction velocity (transactions per hour)

**Example:**
```python
from model_risk_scoring.models import TransactionFeatures

features = TransactionFeatures(
    account_id="account_123",
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
```

#### RiskAssessment

Contains the risk assessment result for an account.

**Required Fields:**
- `account_id` (str): Account identifier
- `risk_score` (float): Risk score (0-100)
- `risk_level` (RiskLevel): Risk level classification
- `risk_factors` (List[str]): List of identified risk factors
- `explanation` (str): Natural language explanation
- `confidence` (float): Confidence score (0-1)
- `inference_mode` (InferenceMode): Inference mode used

**Optional Fields:**
- `model_id` (str): Bedrock model ID or SageMaker endpoint name
- `inference_time_ms` (float): Inference time in milliseconds
- `fallback_used` (bool): Whether fallback was used
- `feature_importance` (Dict[str, float]): Feature importance scores
- `timestamp` (datetime): Assessment timestamp (auto-generated)

**Example:**
```python
from model_risk_scoring.models import RiskAssessment, RiskLevel, InferenceMode

assessment = RiskAssessment(
    account_id="account_123",
    risk_score=75.5,
    risk_level=RiskLevel.HIGH,
    risk_factors=["High volume", "Night transactions"],
    explanation="Account shows suspicious patterns",
    confidence=0.85,
    inference_mode=InferenceMode.UNSUPERVISED,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    inference_time_ms=2500.0
)
```

#### ModelConfig

Configuration for the model service.

**Required Fields:**
- `inference_mode` (InferenceMode): Inference mode to use

**Bedrock Configuration:**
- `bedrock_model_id` (str): Bedrock model ID (default: Claude 3 Sonnet)
- `bedrock_max_tokens` (int): Max tokens for response (default: 1024)
- `bedrock_temperature` (float): Temperature for sampling (default: 0.0)

**SageMaker Configuration:**
- `sagemaker_endpoint_name` (str): SageMaker endpoint name (required for SUPERVISED mode)
- `sagemaker_content_type` (str): Content type (default: "text/csv")
- `sagemaker_accept` (str): Accept type (default: "application/json")

**Rate Limiting:**
- `max_requests_per_second` (float): Max RPS for Bedrock (default: 0.9, must be < 1.0)

**Fallback Configuration:**
- `fallback_enabled` (bool): Enable fallback (default: True)
- `fallback_confidence` (float): Confidence for fallback (default: 0.7)

**Feature Scaling:**
- `feature_scaling_enabled` (bool): Enable feature scaling (default: True)
- `scaler_params` (Dict): Normalization parameters (optional)

**Validation:**
- `max_requests_per_second` must be < 1.0
- `bedrock_temperature` must be between 0.0 and 1.0
- `fallback_confidence` must be between 0.0 and 1.0
- `sagemaker_endpoint_name` is required when `inference_mode` is SUPERVISED

**Example:**
```python
from model_risk_scoring.models import ModelConfig, InferenceMode

# Unsupervised mode
config = ModelConfig(
    inference_mode=InferenceMode.UNSUPERVISED,
    max_requests_per_second=0.9,
    fallback_enabled=True
)

# Supervised mode
config = ModelConfig(
    inference_mode=InferenceMode.SUPERVISED,
    sagemaker_endpoint_name="fraud-detection-endpoint"
)
```

#### FeatureConfig

Configuration for feature processing.

**Fields:**
- `feature_names` (List[str]): Feature names in order (default: all 10 features)
- `scaler_params` (Dict): Normalization parameters (optional)
- `validation_rules` (Dict): Feature validation rules (default: predefined rules)

**Default Feature Order:**
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

**Validation Rules:**
- Numeric features: min >= 0
- Ratio features: min = 0, max = 1
- transaction_count: min = 1

**Example:**
```python
from model_risk_scoring.models import FeatureConfig

config = FeatureConfig()
print(config.feature_names)  # List of 10 feature names
print(config.validation_rules["night_transaction_ratio"])  # {"min": 0, "max": 1}
```

## Usage Examples

See `examples/data_models_demo.py` for comprehensive usage examples.

### Basic Usage

```python
from model_risk_scoring.models import (
    InferenceMode,
    RiskLevel,
    TransactionFeatures,
    RiskAssessment,
    ModelConfig,
    FeatureConfig,
)

# Create transaction features
features = TransactionFeatures(
    account_id="account_123",
    total_volume=150000.0,
    transaction_count=50,
    # ... other fields
)

# Create model configuration
config = ModelConfig(
    inference_mode=InferenceMode.UNSUPERVISED
)

# Create risk assessment
assessment = RiskAssessment(
    account_id="account_123",
    risk_score=75.5,
    risk_level=RiskLevel.HIGH,
    risk_factors=["High volume"],
    explanation="Suspicious patterns detected",
    confidence=0.85,
    inference_mode=InferenceMode.UNSUPERVISED
)
```

## Testing

Run unit tests:
```bash
pytest tests/unit/test_data_models.py -v
```

Run demo:
```bash
python examples/data_models_demo.py
```

## Requirements

This module satisfies the following requirements from the specification:
- Requirements 1.1-1.10: Feature validation and standardization
- Requirements 6.1-6.10: Risk level classification
- Requirements 12.1-12.10: Configuration management
