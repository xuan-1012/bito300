"""
Explainability Module for the Crypto Suspicious Account Detection system.

Public API:
    - FeatureContribution
    - RuleContribution
    - Explanation
    - BatchResult
    - FEATURE_THRESHOLDS
    - CONTEXT_LABEL_NORMAL
    - REASON_CODE_MAPPING
    - REASON_CODE_DEFAULT
"""

from src.explainability.models import (
    BatchResult,
    CONTEXT_LABEL_NORMAL,
    Explanation,
    FeatureContribution,
    FEATURE_THRESHOLDS,
    REASON_CODE_DEFAULT,
    REASON_CODE_MAPPING,
    RuleContribution,
)

__all__ = [
    "BatchResult",
    "CONTEXT_LABEL_NORMAL",
    "Explanation",
    "FeatureContribution",
    "FEATURE_THRESHOLDS",
    "REASON_CODE_DEFAULT",
    "REASON_CODE_MAPPING",
    "RuleContribution",
]
