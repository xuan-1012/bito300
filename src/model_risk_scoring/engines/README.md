# Inference Engines

This module contains inference engines for risk assessment using different approaches:
- **BedrockInferenceEngine**: Uses Amazon Bedrock LLM for unsupervised risk assessment
- **SageMakerInferenceEngine**: Uses SageMaker Endpoint for supervised risk assessment
- **FallbackRuleEngine**: Rule-based fallback when AI services are unavailable

## FallbackRuleEngine

The `FallbackRuleEngine` provides a stable, rule-based fallback mechanism when Bedrock or SageMaker are unavailable. It uses threshold-based rules to calculate risk scores.

### Features

- **Always Available**: No dependency on external AI services
- **Deterministic**: Same inputs always produce same outputs
- **Fast**: Completes in < 50ms
- **Explainable**: Provides clear reasons for each triggered rule
- **Confidence**: Always returns 0.7 confidence (lower than AI models)

### Rules

The engine implements 6 rules with specific thresholds:

| Rule | Condition | Score | Description |
|------|-----------|-------|-------------|
| high_volume | total_volume > 100000 | +20 | Total transaction volume exceeds $100,000 |
| night_transactions | night_transaction_ratio > 0.3 | +15 | More than 30% transactions during night hours |
| round_numbers | round_number_ratio > 0.5 | +20 | More than 50% transactions with round amounts |
| high_concentration | concentration_score > 0.7 | +15 | High counterparty concentration |
| rapid_transactions | rapid_transaction_count > 10 | +15 | More than 10 rapid consecutive transactions |
| high_velocity | velocity_score > 10 | +15 | Transaction velocity exceeds 10 tx/hour |

**Maximum Score**: 100 (capped even if rules sum to more)

### Usage

```python
from src.model_risk_scoring.engines import FallbackRuleEngine
from src.model_risk_scoring.models.data_models import TransactionFeatures

# Initialize engine
engine = FallbackRuleEngine()

# Create features
features = TransactionFeatures(
    account_id="account_123",
    total_volume=150000,  # Will trigger high_volume rule
    transaction_count=50,
    avg_transaction_size=3000,
    max_transaction_size=10000,
    unique_counterparties=8,
    night_transaction_ratio=0.4,  # Will trigger night_transactions rule
    rapid_transaction_count=5,
    round_number_ratio=0.3,
    concentration_score=0.5,
    velocity_score=5
)

# Calculate risk score
result = engine.calculate_risk_score(features)

print(f"Risk Score: {result['risk_score']}/100")
print(f"Risk Factors: {result['risk_factors']}")
print(f"Confidence: {result['confidence']}")
print(f"Explanation:\n{result['explanation']}")
```

**Output:**
```
Risk Score: 35/100
Risk Factors: ['high_volume', 'night_transactions']
Confidence: 0.7
Explanation:
風險評分：35/100
觸發 2 項風險規則：
- 總交易量超過 $100,000，屬於高風險範圍 (+20 分)
- 深夜交易比例超過 30%，可能規避監控 (+15 分)
```

### API Reference

#### `FallbackRuleEngine.__init__()`

Initialize the fallback rule engine with predefined rules.

**Parameters:** None

**Returns:** FallbackRuleEngine instance

---

#### `calculate_risk_score(features: TransactionFeatures) -> Dict`

Calculate risk score using rule-based approach.

**Parameters:**
- `features` (TransactionFeatures): Transaction features for the account

**Returns:** Dictionary containing:
- `risk_score` (float): Risk score (0-100), capped at 100
- `risk_factors` (List[str]): List of triggered rule names
- `explanation` (str): Natural language explanation in Traditional Chinese
- `confidence` (float): Always 0.7 for fallback

**Example:**
```python
result = engine.calculate_risk_score(features)
assert 0 <= result['risk_score'] <= 100
assert result['confidence'] == 0.7
```

---

#### `apply_rules(features: TransactionFeatures) -> List[Tuple[str, float, str]]`

Apply all rules and return triggered rules.

**Parameters:**
- `features` (TransactionFeatures): Transaction features for the account

**Returns:** List of tuples `(rule_name, score_contribution, reason)` for all triggered rules

**Example:**
```python
triggered = engine.apply_rules(features)
for name, score, reason in triggered:
    print(f"{name}: +{score} points - {reason}")
```

### Design Decisions

1. **Threshold-Based Rules**: Simple, interpretable rules based on domain knowledge
2. **Additive Scoring**: Rules contribute independently to total score
3. **Score Capping**: Maximum score of 100 prevents overflow
4. **Fixed Confidence**: 0.7 confidence reflects lower accuracy vs AI models
5. **Traditional Chinese**: Explanations in Traditional Chinese for target audience
6. **No External Dependencies**: Pure Python, no API calls

### Testing

Run unit tests:
```bash
pytest tests/unit/test_fallback_rule_engine.py -v
```

Run demo:
```bash
python examples/fallback_rule_engine_demo.py
```

### Performance

- **Latency**: < 50ms per inference
- **Throughput**: > 1000 inferences/second
- **Memory**: < 1MB
- **Availability**: 100% (no external dependencies)

### When to Use

Use FallbackRuleEngine when:
- Bedrock or SageMaker are unavailable
- Network connectivity is lost
- Cost optimization is needed (no API charges)
- Deterministic behavior is required
- Low latency is critical (< 50ms)

**Note**: FallbackRuleEngine has lower accuracy than AI models but provides guaranteed availability.
