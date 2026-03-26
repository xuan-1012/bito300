"""
Unit tests for Feature Extractor.

Tests specific known values for feature extraction functions.
Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10
"""

import pytest
from datetime import datetime, timezone

from src.common.models import Transaction, TransactionFeatures
from src.lambdas.feature_extractor.handler import (
    extract_features,
    is_round_number,
    calculate_concentration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_txn(
    txn_id: str,
    from_account: str,
    to_account: str,
    amount: float,
    hour: int = 12,
    minute: int = 0,
    second: int = 0,
    day: int = 1,
) -> Transaction:
    """Create a Transaction with a fixed date for deterministic tests."""
    return Transaction(
        transaction_id=txn_id,
        timestamp=datetime(2024, 1, day, hour, minute, second),
        from_account=from_account,
        to_account=to_account,
        amount=amount,
        currency="USDT",
        transaction_type="transfer",
        status="completed",
        fee=0.0,
    )


# ---------------------------------------------------------------------------
# Tests for is_round_number
# ---------------------------------------------------------------------------

class TestIsRoundNumber:
    """Tests for the is_round_number helper. Requirement 3.7"""

    def test_exact_multiple_of_100_is_round(self):
        assert is_round_number(1000.0) is True

    def test_500_is_round(self):
        assert is_round_number(500.0) is True

    def test_zero_is_round(self):
        # 0 rounds to 0, difference is 0 < 0.01
        assert is_round_number(0.0) is True

    def test_non_round_amount(self):
        assert is_round_number(123.45) is False

    def test_amount_just_below_threshold_is_round(self):
        # 1000.005 rounds to 1000, diff = 0.005 < 0.01
        assert is_round_number(1000.005) is True

    def test_amount_just_above_threshold_is_not_round(self):
        # 1000.02 rounds to 1000, diff = 0.02 >= 0.01
        assert is_round_number(1000.02) is False

    def test_custom_threshold(self):
        # With threshold=1.0, 1050 rounds to 1100, diff=50 >= 1.0 → not round
        assert is_round_number(1050.0, threshold=1.0) is False
        # 1000.5 rounds to 1000, diff=0.5 < 1.0 → round
        assert is_round_number(1000.5, threshold=1.0) is True


# ---------------------------------------------------------------------------
# Tests for calculate_concentration
# ---------------------------------------------------------------------------

class TestCalculateConcentration:
    """Tests for the Herfindahl concentration index. Requirement 3.9"""

    def test_all_same_counterparty_gives_score_1(self):
        txns = [
            make_txn("t1", "acc_a", "acc_b", 100.0),
            make_txn("t2", "acc_a", "acc_b", 200.0),
            make_txn("t3", "acc_a", "acc_b", 300.0),
        ]
        score = calculate_concentration(txns, "acc_a")
        assert score == pytest.approx(1.0)

    def test_all_different_counterparties_gives_low_score(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0),
            make_txn("t2", "acc_a", "cp2", 100.0),
            make_txn("t3", "acc_a", "cp3", 100.0),
            make_txn("t4", "acc_a", "cp4", 100.0),
        ]
        score = calculate_concentration(txns, "acc_a")
        # 4 equal counterparties → HHI = 4 * (1/4)^2 = 0.25
        assert score == pytest.approx(0.25)

    def test_single_transaction_gives_score_1(self):
        txns = [make_txn("t1", "acc_a", "acc_b", 500.0)]
        score = calculate_concentration(txns, "acc_a")
        assert score == pytest.approx(1.0)

    def test_score_is_between_0_and_1(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0),
            make_txn("t2", "acc_a", "cp2", 200.0),
            make_txn("t3", "acc_a", "cp1", 300.0),
        ]
        score = calculate_concentration(txns, "acc_a")
        assert 0.0 <= score <= 1.0

    def test_two_equal_counterparties(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0),
            make_txn("t2", "acc_a", "cp2", 100.0),
        ]
        score = calculate_concentration(txns, "acc_a")
        # HHI = 2 * (1/2)^2 = 0.5
        assert score == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Tests for extract_features - single transaction
# ---------------------------------------------------------------------------

class TestExtractFeaturesSingleTransaction:
    """Edge case: single transaction. Requirements 3.2, 3.3, 3.4, 3.5, 3.10"""

    def setup_method(self):
        self.txn = make_txn("t1", "acc_a", "acc_b", 1000.0, hour=14)
        self.features = extract_features([self.txn])

    def test_account_id(self):
        assert self.features.account_id == "acc_a"

    def test_transaction_count(self):
        assert self.features.transaction_count == 1

    def test_total_volume(self):
        assert self.features.total_volume == pytest.approx(1000.0)

    def test_avg_transaction_size(self):
        assert self.features.avg_transaction_size == pytest.approx(1000.0)

    def test_max_transaction_size(self):
        assert self.features.max_transaction_size == pytest.approx(1000.0)

    def test_unique_counterparties(self):
        assert self.features.unique_counterparties == 1

    def test_night_transaction_ratio_daytime(self):
        # hour=14 is not night (00:00-06:00)
        assert self.features.night_transaction_ratio == pytest.approx(0.0)

    def test_round_number_ratio(self):
        # 1000.0 is a round number
        assert self.features.round_number_ratio == pytest.approx(1.0)

    def test_rapid_transaction_count(self):
        # Only one transaction, no pairs to compare
        assert self.features.rapid_transaction_count == 0

    def test_concentration_score(self):
        # Single counterparty → concentration = 1.0
        assert self.features.concentration_score == pytest.approx(1.0)

    def test_velocity_score_single_transaction(self):
        # Single transaction: time span = 0, velocity = 0
        assert self.features.velocity_score == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Tests for extract_features - multiple transactions aggregation
# ---------------------------------------------------------------------------

class TestExtractFeaturesMultipleTransactions:
    """Tests for aggregation across multiple transactions. Requirements 3.2, 3.3, 3.4, 3.5"""

    def setup_method(self):
        self.txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10, minute=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=11, minute=0),
            make_txn("t3", "acc_a", "cp3", 300.0, hour=12, minute=0),
        ]
        self.features = extract_features(self.txns)

    def test_transaction_count(self):
        assert self.features.transaction_count == 3

    def test_total_volume(self):
        assert self.features.total_volume == pytest.approx(600.0)

    def test_avg_transaction_size(self):
        assert self.features.avg_transaction_size == pytest.approx(200.0)

    def test_max_transaction_size(self):
        assert self.features.max_transaction_size == pytest.approx(300.0)

    def test_unique_counterparties(self):
        assert self.features.unique_counterparties == 3

    def test_no_night_transactions(self):
        assert self.features.night_transaction_ratio == pytest.approx(0.0)

    def test_no_round_numbers(self):
        # 100, 200, 300 are all round numbers (multiples of 100)
        assert self.features.round_number_ratio == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Tests for night transaction ratio
# ---------------------------------------------------------------------------

class TestNightTransactionRatio:
    """Tests for night_transaction_ratio (00:00-06:00). Requirement 3.6"""

    def test_all_night_transactions(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=1),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=3),
            make_txn("t3", "acc_a", "cp3", 300.0, hour=5),
        ]
        features = extract_features(txns)
        assert features.night_transaction_ratio == pytest.approx(1.0)

    def test_no_night_transactions(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=8),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=14),
            make_txn("t3", "acc_a", "cp3", 300.0, hour=20),
        ]
        features = extract_features(txns)
        assert features.night_transaction_ratio == pytest.approx(0.0)

    def test_half_night_transactions(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=2),   # night
            make_txn("t2", "acc_a", "cp2", 200.0, hour=4),   # night
            make_txn("t3", "acc_a", "cp3", 300.0, hour=10),  # day
            make_txn("t4", "acc_a", "cp4", 400.0, hour=16),  # day
        ]
        features = extract_features(txns)
        assert features.night_transaction_ratio == pytest.approx(0.5)

    def test_boundary_hour_0_is_night(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=12),
        ]
        features = extract_features(txns)
        assert features.night_transaction_ratio == pytest.approx(0.5)

    def test_boundary_hour_6_is_not_night(self):
        # hour=6 is NOT in [0, 6) range
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=6),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=12),
        ]
        features = extract_features(txns)
        assert features.night_transaction_ratio == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Tests for round number ratio
# ---------------------------------------------------------------------------

class TestRoundNumberRatio:
    """Tests for round_number_ratio. Requirement 3.7"""

    def test_all_round_numbers(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 1000.0, hour=10),
            make_txn("t2", "acc_a", "cp2", 5000.0, hour=11),
            make_txn("t3", "acc_a", "cp3", 200.0, hour=12),
        ]
        features = extract_features(txns)
        assert features.round_number_ratio == pytest.approx(1.0)

    def test_no_round_numbers(self):
        # Amounts that are NOT close to a multiple of 100
        # 123.45 → nearest 100 is 100, diff=23.45 ≥ 0.01 → not round
        # 67.89  → nearest 100 is 100, diff=32.11 ≥ 0.01 → not round
        # 550.50 → nearest 100 is 600, diff=49.50 ≥ 0.01 → not round
        txns = [
            make_txn("t1", "acc_a", "cp1", 123.45, hour=10),
            make_txn("t2", "acc_a", "cp2", 67.89, hour=11),
            make_txn("t3", "acc_a", "cp3", 550.50, hour=12),
        ]
        features = extract_features(txns)
        assert features.round_number_ratio == pytest.approx(0.0)

    def test_mixed_round_and_non_round(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 1000.0, hour=10),  # round
            make_txn("t2", "acc_a", "cp2", 123.45, hour=11),  # not round
        ]
        features = extract_features(txns)
        assert features.round_number_ratio == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Tests for concentration score
# ---------------------------------------------------------------------------

class TestConcentrationScore:
    """Tests for concentration_score (Herfindahl index). Requirement 3.9"""

    def test_all_same_counterparty(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10),
            make_txn("t2", "acc_a", "cp1", 200.0, hour=11),
            make_txn("t3", "acc_a", "cp1", 300.0, hour=12),
        ]
        features = extract_features(txns)
        assert features.concentration_score == pytest.approx(1.0)

    def test_all_different_counterparties(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10),
            make_txn("t2", "acc_a", "cp2", 100.0, hour=11),
            make_txn("t3", "acc_a", "cp3", 100.0, hour=12),
            make_txn("t4", "acc_a", "cp4", 100.0, hour=13),
        ]
        features = extract_features(txns)
        # HHI = 4 * (1/4)^2 = 0.25
        assert features.concentration_score == pytest.approx(0.25)

    def test_concentration_score_in_range(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=11),
            make_txn("t3", "acc_a", "cp1", 300.0, hour=12),
        ]
        features = extract_features(txns)
        assert 0.0 <= features.concentration_score <= 1.0


# ---------------------------------------------------------------------------
# Tests for rapid transaction count
# ---------------------------------------------------------------------------

class TestRapidTransactionCount:
    """Tests for rapid_transaction_count (< 5 minutes apart). Requirement 3.8"""

    def test_no_rapid_transactions(self):
        # Transactions 1 hour apart
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10, minute=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=11, minute=0),
            make_txn("t3", "acc_a", "cp3", 300.0, hour=12, minute=0),
        ]
        features = extract_features(txns)
        assert features.rapid_transaction_count == 0

    def test_all_rapid_transactions(self):
        # All within 1 minute of each other
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10, minute=0, second=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=10, minute=1, second=0),
            make_txn("t3", "acc_a", "cp3", 300.0, hour=10, minute=2, second=0),
        ]
        features = extract_features(txns)
        # t2 is rapid after t1, t3 is rapid after t2 → count = 2
        assert features.rapid_transaction_count == 2

    def test_boundary_exactly_5_minutes_is_not_rapid(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10, minute=0, second=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=10, minute=5, second=0),
        ]
        features = extract_features(txns)
        # Exactly 300 seconds is NOT < 300, so not rapid
        assert features.rapid_transaction_count == 0

    def test_just_under_5_minutes_is_rapid(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10, minute=0, second=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=10, minute=4, second=59),
        ]
        features = extract_features(txns)
        # 299 seconds < 300 → rapid
        assert features.rapid_transaction_count == 1


# ---------------------------------------------------------------------------
# Tests for velocity score
# ---------------------------------------------------------------------------

class TestVelocityScore:
    """Tests for velocity_score (transactions per hour). Requirement 3.10"""

    def test_velocity_score_two_transactions_one_hour_apart(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10, minute=0),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=11, minute=0),
        ]
        features = extract_features(txns)
        # 2 transactions over 1 hour = 2.0 tx/hr
        assert features.velocity_score == pytest.approx(2.0)

    def test_velocity_score_single_transaction_is_zero(self):
        txns = [make_txn("t1", "acc_a", "cp1", 100.0, hour=10)]
        features = extract_features(txns)
        assert features.velocity_score == pytest.approx(0.0)

    def test_velocity_score_non_negative(self):
        txns = [
            make_txn("t1", "acc_a", "cp1", 100.0, hour=10),
            make_txn("t2", "acc_a", "cp2", 200.0, hour=12),
        ]
        features = extract_features(txns)
        assert features.velocity_score >= 0.0


# ---------------------------------------------------------------------------
# Edge case: all transactions to same counterparty
# ---------------------------------------------------------------------------

class TestAllSameCounterparty:
    """Edge case: all transactions go to the same counterparty."""

    def setup_method(self):
        self.txns = [
            make_txn("t1", "acc_a", "acc_b", 100.0, hour=10, minute=0),
            make_txn("t2", "acc_a", "acc_b", 200.0, hour=11, minute=0),
            make_txn("t3", "acc_a", "acc_b", 300.0, hour=12, minute=0),
        ]
        self.features = extract_features(self.txns)

    def test_unique_counterparties_is_one(self):
        assert self.features.unique_counterparties == 1

    def test_concentration_score_is_one(self):
        assert self.features.concentration_score == pytest.approx(1.0)

    def test_total_volume_correct(self):
        assert self.features.total_volume == pytest.approx(600.0)

    def test_transaction_count_correct(self):
        assert self.features.transaction_count == 3
