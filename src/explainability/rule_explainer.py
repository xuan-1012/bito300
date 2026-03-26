"""
Rule-based explanation decomposition for the Explainability Module.

This module provides the RuleExplainer class, which extracts triggered rules,
score contributions, and trigger conditions from a rule-based RiskAssessment,
then computes percentage contributions and flags major contributors.
"""

from typing import List

from src.common.models import RiskAssessment
from src.explainability.models import RuleContribution


class RuleExplainer:
    """
    Decomposes a rule-based RiskAssessment into a list of RuleContribution objects.

    Each RuleContribution captures:
    - rule_name: the name of the triggered rule
    - score_contribution: absolute score points added by this rule
    - percentage: fraction of total risk_score (score_contribution / total_score)
    - trigger_condition: human-readable description of what triggered the rule
    - is_major: True when percentage > 0.20

    Rules are sorted by score_contribution in descending order.

    Requirements: 7.1–7.7
    """

    def explain(self, assessment: RiskAssessment) -> List[RuleContribution]:
        """
        Extract and decompose triggered rules from a rule-based RiskAssessment.

        Args:
            assessment: A RiskAssessment object. Rule data is read from
                        ``assessment.triggered_rules``, which must be a list of
                        dicts with keys ``rule_name``, ``score_contribution``,
                        and ``trigger_condition``.

        Returns:
            A list of RuleContribution objects sorted by score_contribution
            descending. Returns an empty list when no rules are triggered or
            when ``triggered_rules`` is absent.
        """
        triggered_rules = getattr(assessment, "triggered_rules", None) or []

        if not triggered_rules:
            return []

        total_score = assessment.risk_score

        contributions: List[RuleContribution] = []
        for rule in triggered_rules:
            rule_name: str = rule["rule_name"]
            score_contribution: float = float(rule["score_contribution"])
            trigger_condition: str = rule["trigger_condition"]

            # Avoid division by zero when total score is 0
            percentage = score_contribution / total_score if total_score > 0 else 0.0
            is_major = percentage > 0.20

            contributions.append(
                RuleContribution(
                    rule_name=rule_name,
                    score_contribution=score_contribution,
                    percentage=percentage,
                    trigger_condition=trigger_condition,
                    is_major=is_major,
                )
            )

        # Sort by score_contribution descending (Requirement 7.4)
        contributions.sort(key=lambda rc: rc.score_contribution, reverse=True)

        return contributions
