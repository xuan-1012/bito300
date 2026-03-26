"""
Reason Code Assigner for the Explainability Module.

Maps risk factor strings to standardized ReasonCode values using
case-insensitive substring matching against predefined patterns.
"""

from typing import List

from src.explainability.models import REASON_CODE_DEFAULT, REASON_CODE_MAPPING


class ReasonCodeAssigner:
    """Maps risk factor strings to standardized reason code values."""

    def assign(self, risk_factors: List[str]) -> List[str]:
        """
        Map a list of risk factor strings to standardized reason code strings.

        Each factor is matched case-insensitively against the known patterns.
        Unrecognized factors are mapped to OTHER.

        Args:
            risk_factors: List of risk factor description strings.

        Returns:
            List of reason code strings (e.g. ["HIGH_VOLUME", "OTHER"]).
        """
        result: List[str] = []
        for factor in risk_factors:
            factor_lower = factor.lower()
            matched = REASON_CODE_DEFAULT
            for pattern, code in REASON_CODE_MAPPING.items():
                if pattern in factor_lower:
                    matched = code
                    break
            result.append(matched)
        return result
