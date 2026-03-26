"""
Property-based tests for Report Generator.

**Property 5: Report total_accounts equals number of risk assessments**
**Validates: Requirements 8.1**

**Property 6: Sum of risk_distribution values equals total_accounts**
**Validates: Requirements 8.2**
"""

from datetime import datetime
from hypothesis import given, strategies as st, settings

from src.common.models import RiskAssessment, RiskLevel
from src.lambdas.report_generator.handler import generate_summary_report


# ---------------------------------------------------------------------------
# Hypothesis strategy for RiskAssessment
# ---------------------------------------------------------------------------

@st.composite
def risk_assessment_strategy(draw):
    """Generate a valid RiskAssessment object with arbitrary values."""
    # Generate risk score first
    risk_score = draw(st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False))
    
    # Determine risk level based on score to ensure consistency
    if risk_score >= 76:
        risk_level = RiskLevel.CRITICAL
    elif risk_score >= 51:
        risk_level = RiskLevel.HIGH
    elif risk_score >= 26:
        risk_level = RiskLevel.MEDIUM
    else:
        risk_level = RiskLevel.LOW
    
    return RiskAssessment(
        account_id=draw(st.text(min_size=1, max_size=50)),
        risk_score=risk_score,
        risk_level=risk_level,
        risk_factors=draw(st.lists(st.text(min_size=1, max_size=100), min_size=1, max_size=10)),
        explanation=draw(st.text(min_size=1, max_size=500)),
        confidence=draw(st.floats(min_value=0, max_value=1, allow_nan=False, allow_infinity=False)),
        timestamp=datetime.now(),
    )


# ---------------------------------------------------------------------------
# Property: Report total_accounts equals number of risk assessments
# **Validates: Requirements 8.1**
# ---------------------------------------------------------------------------

class TestReportTotalAccountsProperty:
    """
    Property 5: generate_summary_report() always returns total_accounts
    equal to the number of risk assessments provided.

    **Validates: Requirements 8.1**
    """

    @given(st.lists(risk_assessment_strategy(), min_size=0, max_size=100))
    @settings(max_examples=200, deadline=None)
    def test_total_accounts_equals_assessment_count(self, risk_assessments):
        """
        Property: total_accounts equals the number of risk assessments.

        **Validates: Requirements 8.1**
        """
        report = generate_summary_report(risk_assessments, total_transactions=0)
        
        expected_count = len(risk_assessments)
        actual_count = report["total_accounts"]
        
        assert actual_count == expected_count, (
            f"total_accounts={actual_count} does not equal "
            f"number of risk assessments={expected_count}"
        )

    @given(st.lists(risk_assessment_strategy(), min_size=1, max_size=50))
    @settings(max_examples=100, deadline=None)
    def test_total_accounts_positive_when_assessments_exist(self, risk_assessments):
        """
        Property: total_accounts is positive when risk assessments exist.

        **Validates: Requirements 8.1**
        """
        report = generate_summary_report(risk_assessments, total_transactions=0)
        
        assert report["total_accounts"] > 0, (
            f"total_accounts should be positive when assessments exist, "
            f"got {report['total_accounts']}"
        )

    @given(st.just([]))
    @settings(max_examples=10, deadline=None)
    def test_total_accounts_zero_when_no_assessments(self, risk_assessments):
        """
        Property: total_accounts is zero when no risk assessments provided.

        **Validates: Requirements 8.1**
        """
        report = generate_summary_report(risk_assessments, total_transactions=0)
        
        assert report["total_accounts"] == 0, (
            f"total_accounts should be 0 when no assessments provided, "
            f"got {report['total_accounts']}"
        )


# ---------------------------------------------------------------------------
# Property: Sum of risk_distribution values equals total_accounts
# **Validates: Requirements 8.2**
# ---------------------------------------------------------------------------

class TestRiskDistributionSumProperty:
    """
    Property 6: generate_summary_report() always returns risk_distribution
    where the sum of all values equals total_accounts.

    **Validates: Requirements 8.2**
    """

    @given(st.lists(risk_assessment_strategy(), min_size=0, max_size=100))
    @settings(max_examples=200, deadline=None)
    def test_risk_distribution_sum_equals_total_accounts(self, risk_assessments):
        """
        Property: Sum of risk_distribution values equals total_accounts.

        **Validates: Requirements 8.2**
        """
        report = generate_summary_report(risk_assessments, total_transactions=0)
        
        total_accounts = report["total_accounts"]
        risk_distribution = report["risk_distribution"]
        
        # Sum all values in risk_distribution
        distribution_sum = sum(risk_distribution.values())
        
        assert distribution_sum == total_accounts, (
            f"Sum of risk_distribution values ({distribution_sum}) does not equal "
            f"total_accounts ({total_accounts}). "
            f"Distribution: {risk_distribution}"
        )

    @given(st.lists(risk_assessment_strategy(), min_size=1, max_size=50))
    @settings(max_examples=100, deadline=None)
    def test_risk_distribution_all_levels_accounted(self, risk_assessments):
        """
        Property: All risk assessments are accounted for in risk_distribution.

        **Validates: Requirements 8.2**
        """
        report = generate_summary_report(risk_assessments, total_transactions=0)
        
        risk_distribution = report["risk_distribution"]
        
        # Count assessments by risk level manually
        expected_counts = {level.value: 0 for level in RiskLevel}
        for assessment in risk_assessments:
            expected_counts[assessment.risk_level.value] += 1
        
        # Verify each level count matches
        for level_value, expected_count in expected_counts.items():
            actual_count = risk_distribution.get(level_value, 0)
            assert actual_count == expected_count, (
                f"Risk level '{level_value}' count mismatch: "
                f"expected {expected_count}, got {actual_count}"
            )

    @given(st.just([]))
    @settings(max_examples=10, deadline=None)
    def test_risk_distribution_sum_zero_when_no_assessments(self, risk_assessments):
        """
        Property: Sum of risk_distribution is zero when no assessments provided.

        **Validates: Requirements 8.2**
        """
        report = generate_summary_report(risk_assessments, total_transactions=0)
        
        risk_distribution = report["risk_distribution"]
        distribution_sum = sum(risk_distribution.values())
        
        assert distribution_sum == 0, (
            f"Sum of risk_distribution should be 0 when no assessments provided, "
            f"got {distribution_sum}"
        )
