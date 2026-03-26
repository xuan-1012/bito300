"""
Property-based tests for Feature Extractor.

**Property 2: Feature ratios are always between 0 and 1**
**Validates: Requirements 3.6, 3.7, 3.9, 15.2**

**Property 2: Total volume equals sum of transaction amounts**
**Validates: Requirements 3.2, 15.5**
"""

import pytest
from datetime import datetime, timezone
from hypothesis import given, strategies as st, settings, assume

from src.common.models import Transaction
from src.lambdas.feature_extractor.handler import extract_features


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

transaction_id_st = st.text(min_size=1, max_size=50)
account_id_st = st.text(min_size=1, max_size=50)
amount_st = st.floats(min_value=0.01, max_value=1e9, allow_nan=False, allow_infinity=False)
timestamp_st = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2030, 12, 31),
)


@st.composite
def transaction_strategy(draw, from_account: str = None):
    """Generate a single valid Transaction object."""
    from_acc = from_account if from_account is not None else draw(account_id_st)
    to_acc = draw(account_id_st)
    # Ensure to_account is non-empty
    assume(to_acc)
    assume(from_acc)

    return Transaction(
        transaction_id=draw(transaction_id_st),
        timestamp=draw(timestamp_st),
        from_account=from_acc,
        to_account=to_acc,
        amount=draw(amount_st),
        currency="USDT",
        transaction_type="transfer",
        status="completed",
        fee=0.0,
    )


@st.composite
def transaction_list_strategy(draw):
    """Generate a non-empty list of Transactions all from the same account."""
    from_acc = draw(account_id_st)
    assume(from_acc)

    txns = draw(
        st.lists(
            transaction_strategy(from_account=from_acc),
            min_size=1,
            max_size=50,
        )
    )
    return txns


# ---------------------------------------------------------------------------
# Property: Feature ratios are always between 0 and 1
# **Validates: Requirements 3.6, 3.7, 3.9, 15.2**
# ---------------------------------------------------------------------------

class TestFeatureRatiosProperty:
    """
    Property 2: Feature ratios (night_transaction_ratio, round_number_ratio,
    concentration_score) are always between 0 and 1 for any valid transaction list.

    **Validates: Requirements 3.6, 3.7, 3.9, 15.2**
    """

    @given(transaction_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_night_transaction_ratio_in_range(self, transactions):
        """
        Property: night_transaction_ratio is always in [0, 1].

        **Validates: Requirements 3.6, 15.2**
        """
        features = extract_features(transactions)
        assert 0.0 <= features.night_transaction_ratio <= 1.0, (
            f"night_transaction_ratio={features.night_transaction_ratio} is out of [0, 1] "
            f"for {len(transactions)} transactions"
        )

    @given(transaction_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_round_number_ratio_in_range(self, transactions):
        """
        Property: round_number_ratio is always in [0, 1].

        **Validates: Requirements 3.7, 15.2**
        """
        features = extract_features(transactions)
        assert 0.0 <= features.round_number_ratio <= 1.0, (
            f"round_number_ratio={features.round_number_ratio} is out of [0, 1] "
            f"for {len(transactions)} transactions"
        )

    @given(transaction_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_concentration_score_in_range(self, transactions):
        """
        Property: concentration_score is always in [0, 1].

        **Validates: Requirements 3.9, 15.2**
        """
        features = extract_features(transactions)
        assert 0.0 <= features.concentration_score <= 1.0, (
            f"concentration_score={features.concentration_score} is out of [0, 1] "
            f"for {len(transactions)} transactions"
        )

    @given(transaction_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_all_ratios_in_range(self, transactions):
        """
        Property: All three ratio features are simultaneously in [0, 1].

        **Validates: Requirements 3.6, 3.7, 3.9, 15.2**
        """
        features = extract_features(transactions)
        assert 0.0 <= features.night_transaction_ratio <= 1.0
        assert 0.0 <= features.round_number_ratio <= 1.0
        assert 0.0 <= features.concentration_score <= 1.0


# ---------------------------------------------------------------------------
# Property: Total volume equals sum of transaction amounts
# **Validates: Requirements 3.2, 15.5**
# ---------------------------------------------------------------------------

class TestTotalVolumeProperty:
    """
    Property 2: total_volume always equals the sum of all transaction amounts
    within a tolerance of 0.01.

    **Validates: Requirements 3.2, 15.5**
    """

    @given(transaction_list_strategy())
    @settings(max_examples=200, deadline=None)
    def test_total_volume_equals_sum_of_amounts(self, transactions):
        """
        Property: total_volume == sum(txn.amount for txn in transactions)
        within tolerance 0.01.

        **Validates: Requirements 3.2, 15.5**
        """
        features = extract_features(transactions)
        expected_volume = sum(txn.amount for txn in transactions)
        assert abs(features.total_volume - expected_volume) <= 0.01, (
            f"total_volume={features.total_volume} differs from "
            f"expected sum={expected_volume} by more than 0.01"
        )
