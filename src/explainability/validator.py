"""
Explanation Validator for the Explainability Module.

Validates a completed Explanation object against all structural invariants
defined in Requirements 13.1–13.8.
"""

from src.common.models import RiskLevel
from src.explainability.models import Explanation


class ExplanationValidationError(Exception):
    """Raised when an Explanation fails structural validation."""


class ExplanationValidator:
    """
    Validates Explanation objects against all structural invariants.

    On success, sets explanation.is_validated = True.
    On any failure, raises ExplanationValidationError with a descriptive message.
    """

    # Tolerance for feature_contributions sum check (Requirement 13.6)
    CONTRIBUTION_SUM_TOLERANCE = 0.01

    # Minimum length for natural_language_summary (Requirement 13.4)
    MIN_SUMMARY_LENGTH = 20

    def validate(self, explanation: Explanation) -> None:
        """
        Validate all structural invariants of an Explanation.

        Args:
            explanation: The Explanation object to validate.

        Raises:
            ExplanationValidationError: If any invariant is violated.
        """
        self._validate_account_id(explanation)
        self._validate_risk_score(explanation)
        self._validate_risk_level(explanation)
        self._validate_summary(explanation)
        self._validate_reason_codes(explanation)
        self._validate_feature_contributions(explanation)

        explanation.is_validated = True

    # ------------------------------------------------------------------
    # Private validation helpers
    # ------------------------------------------------------------------

    def _validate_account_id(self, explanation: Explanation) -> None:
        """Requirement 13.1 — account_id must be a non-empty string."""
        if not explanation.account_id or not explanation.account_id.strip():
            raise ExplanationValidationError(
                "account_id must be a non-empty string, got: "
                f"{explanation.account_id!r}"
            )

    def _validate_risk_score(self, explanation: Explanation) -> None:
        """Requirement 13.2 — risk_score must be in [0, 100]."""
        score = explanation.risk_score
        if not (0 <= score <= 100):
            raise ExplanationValidationError(
                f"risk_score must be between 0 and 100, got: {score}"
            )

    def _validate_risk_level(self, explanation: Explanation) -> None:
        """Requirement 13.3 — risk_level must match the risk_score range."""
        expected = RiskLevel.from_score(explanation.risk_score)
        if explanation.risk_level != expected:
            raise ExplanationValidationError(
                f"risk_level {explanation.risk_level!r} does not match "
                f"risk_score {explanation.risk_score} "
                f"(expected {expected!r})"
            )

    def _validate_summary(self, explanation: Explanation) -> None:
        """Requirement 13.4 — natural_language_summary must be >= 20 characters."""
        summary = explanation.natural_language_summary
        if not summary or len(summary) < self.MIN_SUMMARY_LENGTH:
            raise ExplanationValidationError(
                f"natural_language_summary must be at least "
                f"{self.MIN_SUMMARY_LENGTH} characters long, "
                f"got {len(summary) if summary else 0} characters"
            )

    def _validate_reason_codes(self, explanation: Explanation) -> None:
        """Requirement 13.5 — at least one reason_code must be present."""
        if not explanation.reason_codes:
            raise ExplanationValidationError(
                "reason_codes must contain at least one entry"
            )

    def _validate_feature_contributions(self, explanation: Explanation) -> None:
        """Requirement 13.6 — feature_contributions must sum to 1.0 ± 0.01."""
        contributions = explanation.feature_contributions
        if not contributions:
            raise ExplanationValidationError(
                "feature_contributions must not be empty"
            )
        total = sum(contributions.values())
        if abs(total - 1.0) > self.CONTRIBUTION_SUM_TOLERANCE:
            raise ExplanationValidationError(
                f"feature_contributions must sum to 1.0 ± "
                f"{self.CONTRIBUTION_SUM_TOLERANCE}, got {total:.6f}"
            )
