"""
Property-based tests for Risk Analyzer.

**Property 3: Risk score is always between 0 and 100**
**Validates: Requirements 4.4, 7.1, 7.2, 7.3, 7.4**

**Property 3: Risk level always matches risk score range**
**Validates: Requirements 4.5, 7.1, 7.2, 7.3, 7.4, 7.5**
"""

from hypothesis import given, strategies as st, settings

from src.common.models import TransactionFeatures, RiskLevel
from src.lambdas.risk_analyzer.handler import fallback_risk_scoring


# ---------------------------------------------------------------------------
# Hypothesis strategy for TransactionFeatures
# ---------------------------------------------------------------------------

@st.composite
def transaction_features_strategy(draw):
    """Generate a valid TransactionFeatures object with arbitrary values."""
    return TransactionFeatures(
        account_id=draw(st.text(min_size=1)),
        total_volume=draw(st.floats(min_value=0, max_value=1e12, allow_nan=False, allow_infinity=False)),
        transaction_count=draw(st.integers(min_value=1, max_value=10000)),
        avg_transaction_size=draw(st.floats(min_value=0, max_value=1e9, allow_nan=False, allow_infinity=False)),
        max_transaction_size=draw(st.floats(min_value=0, max_value=1e9, allow_nan=False, allow_infinity=False)),
        unique_counterparties=draw(st.integers(min_value=1, max_value=1000)),
        night_transaction_ratio=draw(st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)),
        rapid_transaction_count=draw(st.integers(min_value=0, max_value=1000)),
        round_number_ratio=draw(st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)),
        concentration_score=draw(st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)),
        velocity_score=draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False)),
    )


# ---------------------------------------------------------------------------
# Property: Risk score is always between 0 and 100
# **Validates: Requirements 4.4, 7.1, 7.2, 7.3, 7.4**
# ---------------------------------------------------------------------------

class TestRiskScoreRangeProperty:
    """
    Property 3: fallback_risk_scoring() always returns a risk_score in [0, 100]
    for any valid TransactionFeatures input.

    **Validates: Requirements 4.4, 7.1, 7.2, 7.3, 7.4**
    """

    @given(transaction_features_strategy())
    @settings(max_examples=200, deadline=None)
    def test_risk_score_always_in_range(self, features):
        """
        Property: risk_score is always in [0, 100].

        **Validates: Requirements 4.4, 7.1, 7.2, 7.3, 7.4**
        """
        assessment = fallback_risk_scoring(features)
        assert 0 <= assessment.risk_score <= 100, (
            f"risk_score={assessment.risk_score} is out of [0, 100] "
            f"for account {features.account_id}"
        )


# ---------------------------------------------------------------------------
# Property: Risk level always matches risk score range
# **Validates: Requirements 4.5, 7.1, 7.2, 7.3, 7.4, 7.5**
# ---------------------------------------------------------------------------

class TestRiskLevelMatchesScoreProperty:
    """
    Property 3: The risk_level returned by fallback_risk_scoring() always
    matches the risk_score range:
        LOW      → 0–25
        MEDIUM   → 26–50
        HIGH     → 51–75
        CRITICAL → 76–100

    **Validates: Requirements 4.5, 7.1, 7.2, 7.3, 7.4, 7.5**
    """

    @given(transaction_features_strategy())
    @settings(max_examples=200, deadline=None)
    def test_risk_level_matches_score_range(self, features):
        """
        Property: risk_level always matches the risk_score range.

        **Validates: Requirements 4.5, 7.1, 7.2, 7.3, 7.4, 7.5**
        """
        assessment = fallback_risk_scoring(features)
        score = assessment.risk_score
        level = assessment.risk_level

        expected_level = RiskLevel.from_score(score)
        assert level == expected_level, (
            f"risk_level={level.value} does not match risk_score={score} "
            f"(expected {expected_level.value})"
        )

    @given(transaction_features_strategy())
    @settings(max_examples=200, deadline=None)
    def test_low_score_gives_low_level(self, features):
        """
        Property: When risk_score is in [0, 25], risk_level is LOW.

        **Validates: Requirements 7.1, 7.5**
        """
        assessment = fallback_risk_scoring(features)
        if assessment.risk_score <= 25:
            assert assessment.risk_level == RiskLevel.LOW, (
                f"Expected LOW for score={assessment.risk_score}, "
                f"got {assessment.risk_level.value}"
            )

    @given(transaction_features_strategy())
    @settings(max_examples=200, deadline=None)
    def test_critical_score_gives_critical_level(self, features):
        """
        Property: When risk_score is in [76, 100], risk_level is CRITICAL.

        **Validates: Requirements 7.4, 7.5**
        """
        assessment = fallback_risk_scoring(features)
        if assessment.risk_score >= 76:
            assert assessment.risk_level == RiskLevel.CRITICAL, (
                f"Expected CRITICAL for score={assessment.risk_score}, "
                f"got {assessment.risk_level.value}"
            )
