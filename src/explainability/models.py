"""
Data models and constants for the Explainability Module.

This module defines:
- FeatureContribution: per-feature contribution to risk score
- RuleContribution: per-rule contribution for rule-based assessments
- Explanation: full explanation object for a single account
- BatchResult: aggregated result for batch explanation generation
- Feature contextualization threshold constants
- Reason code mapping constants
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from src.common.models import RiskLevel


# ---------------------------------------------------------------------------
# Feature Contextualization Thresholds
# Each entry: (threshold_value, label_when_exceeded)
# ---------------------------------------------------------------------------

FEATURE_THRESHOLDS: Dict[str, tuple] = {
    "total_volume": (100_000, "significantly above normal"),
    "night_transaction_ratio": (0.3, "unusually high"),
    "round_number_ratio": (0.5, "suspicious pattern detected"),
    "concentration_score": (0.7, "highly concentrated"),
    "rapid_transaction_count": (10, "abnormally frequent"),
    "velocity_score": (10, "extremely high velocity"),
}

CONTEXT_LABEL_NORMAL = "within normal range"


# ---------------------------------------------------------------------------
# Reason Code Mapping
# Maps lowercase keyword patterns to standardized reason codes.
# ---------------------------------------------------------------------------

REASON_CODE_MAPPING: Dict[str, str] = {
    "high transaction volume": "HIGH_VOLUME",
    "night transactions": "NIGHT_ACTIVITY",
    "round number amounts": "ROUND_AMOUNTS",
    "high counterparty concentration": "HIGH_CONCENTRATION",
    "rapid transactions": "RAPID_TRANSACTIONS",
    "high velocity": "HIGH_VELOCITY",
}

REASON_CODE_DEFAULT = "OTHER"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class FeatureContribution:
    """
    Represents a single feature's contribution to the risk score.

    Attributes:
        feature_name: Name of the feature (e.g. "total_volume")
        contribution: Normalized contribution value in [0, 1]
        raw_value: Original feature value before normalization (optional)
        context_label: Human-readable context label (e.g. "significantly above normal")
    """
    feature_name: str
    contribution: float
    raw_value: Optional[float]
    context_label: str


@dataclass
class RuleContribution:
    """
    Represents a single rule's contribution in a rule-based risk assessment.

    Attributes:
        rule_name: Name of the triggered rule
        score_contribution: Absolute score points contributed by this rule
        percentage: Fraction of total risk score (score_contribution / total_score)
        trigger_condition: Human-readable description of the trigger condition
        is_major: True when percentage > 0.20
    """
    rule_name: str
    score_contribution: float
    percentage: float
    trigger_condition: str
    is_major: bool


@dataclass
class Explanation:
    """
    Full explanation for a single account's risk assessment.

    Attributes:
        account_id: Account identifier
        risk_score: Risk score in [0, 100]
        risk_level: Risk level classification
        reason_codes: List of standardized reason codes (e.g. ["HIGH_VOLUME"])
        top_features: Top contributing features sorted by contribution descending
        feature_contributions: All features with normalized contributions
        natural_language_summary: Human-readable explanation text
        language: Language code ("en" or "zh-TW")
        is_fallback: True when template-based NLG was used instead of Bedrock
        is_validated: True when ExplanationValidator has passed this explanation
        generated_at: Timestamp of explanation generation
        generation_time_ms: Time taken to generate the explanation in milliseconds
        s3_uri: S3 URI where the explanation is stored (set after persistence)
        triggered_rules: Rule contributions for rule-based assessments (optional)
    """
    account_id: str
    risk_score: float
    risk_level: RiskLevel
    reason_codes: List[str]
    top_features: List[FeatureContribution]
    feature_contributions: Dict[str, float]
    natural_language_summary: str
    language: str
    is_fallback: bool
    is_validated: bool
    generated_at: datetime
    generation_time_ms: float
    s3_uri: Optional[str] = None
    triggered_rules: Optional[List[RuleContribution]] = None


@dataclass
class BatchResult:
    """
    Aggregated result for a batch explanation generation run.

    Attributes:
        explanations: List of successfully generated Explanation objects
        total: Total number of assessments submitted
        successful: Number of successfully generated explanations
        failed: Number of failed explanation generations
        errors: Mapping of account_id to error message for failed accounts
    """
    explanations: List[Explanation]
    total: int
    successful: int
    failed: int
    errors: Dict[str, str]
