"""
Feature Contribution Calculator for the Explainability Module.

Computes normalized feature contributions from SHAP values, model feature
importance, rule weights, or equal-weight fallback across risk_factors.
"""

from typing import Dict, List, Optional

from src.common.models import RiskAssessment
from src.explainability.models import (
    CONTEXT_LABEL_NORMAL,
    FEATURE_THRESHOLDS,
    FeatureContribution,
)


class FeatureContributionCalculator:
    """
    Computes and contextualizes feature contributions for a RiskAssessment.

    Priority order for raw contribution source:
      1. shap_values (dict attribute on assessment)
      2. feature_importance (dict attribute on assessment)
      3. triggered_rules (list of dicts with 'score_contribution' and 'rule_name')
      4. Equal weights across risk_factors
    """

    def calculate(self, assessment: RiskAssessment) -> Dict[str, float]:
        """
        Return a dict of feature_name -> normalized contribution in [0, 1].

        Normalization: divide each raw value by the total sum so they sum to 1.0.
        Returns an empty dict when there are no features or all values are zero.
        """
        raw: Dict[str, float] = {}

        shap_values = getattr(assessment, "shap_values", None)
        feature_importance = getattr(assessment, "feature_importance", None)
        triggered_rules = getattr(assessment, "triggered_rules", None)

        if isinstance(shap_values, dict) and shap_values:
            raw = {k: float(v) for k, v in shap_values.items()}

        elif isinstance(feature_importance, dict) and feature_importance:
            raw = {k: float(v) for k, v in feature_importance.items()}

        elif isinstance(triggered_rules, list) and triggered_rules:
            for rule in triggered_rules:
                name = rule.get("rule_name", "unknown_rule")
                contrib = float(rule.get("score_contribution", 0.0))
                raw[name] = raw.get(name, 0.0) + contrib

        else:
            # Equal weights across risk_factors
            factors = assessment.risk_factors or []
            if factors:
                weight = 1.0 / len(factors)
                raw = {factor: weight for factor in factors}

        return self._normalize(raw)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _normalize(self, raw: Dict[str, float]) -> Dict[str, float]:
        """Normalize raw values so they sum to 1.0; return {} if all zero."""
        if not raw:
            return {}
        total = sum(raw.values())
        if total == 0.0:
            return {}
        return {k: v / total for k, v in raw.items()}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_top_features(
        self,
        contributions: Dict[str, float],
        threshold: float = 0.05,
        max_fallback: int = 5,
        assessment: Optional[RiskAssessment] = None,
    ) -> List[FeatureContribution]:
        """
        Select top features from a normalized contribution map.

        - Features with contribution > threshold are selected.
        - If none exceed the threshold, the top max_fallback features are used.
        - Results are sorted descending by contribution.
        - raw_value is populated from assessment.features if available.
        """
        if not contributions:
            return []

        above_threshold = {
            k: v for k, v in contributions.items() if v > threshold
        }

        if above_threshold:
            selected = above_threshold
        else:
            sorted_all = sorted(contributions.items(), key=lambda x: x[1], reverse=True)
            selected = dict(sorted_all[:max_fallback])

        # Retrieve raw feature values if possible
        features_dict: Dict[str, float] = {}
        if assessment is not None:
            features_attr = getattr(assessment, "features", None)
            if isinstance(features_attr, dict):
                features_dict = features_attr

        result: List[FeatureContribution] = []
        for name, contrib in selected.items():
            raw_value: Optional[float] = features_dict.get(name)
            context_label = self.contextualize(name, raw_value if raw_value is not None else 0.0)
            result.append(
                FeatureContribution(
                    feature_name=name,
                    contribution=contrib,
                    raw_value=raw_value,
                    context_label=context_label,
                )
            )

        result.sort(key=lambda fc: fc.contribution, reverse=True)
        return result

    def contextualize(self, feature_name: str, value: float) -> str:
        """
        Return a human-readable context label for a feature value.

        Uses FEATURE_THRESHOLDS from models.py:
          - If feature_name is in FEATURE_THRESHOLDS and value > threshold → return label
          - Otherwise → return CONTEXT_LABEL_NORMAL
        """
        if feature_name in FEATURE_THRESHOLDS:
            threshold_value, label = FEATURE_THRESHOLDS[feature_name]
            if value > threshold_value:
                return label
        return CONTEXT_LABEL_NORMAL
