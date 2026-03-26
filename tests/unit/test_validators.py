"""
Unit tests for validators module.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6**
"""

import pytest
from datetime import datetime
from src.common.models import Transaction, TransactionFeatures, RiskAssessment, RiskLevel
from src.common.validators import validate_transaction, validate_features, validate_risk_assessment


class TestValidateTransaction:
    """Tests for validate_transaction function."""
    
    def test_valid_transaction_passes(self):
        """Valid transaction should pass validation."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        assert validate_transaction(transaction) is True
    
    def test_empty_transaction_id_fails(self):
        """Transaction with empty transaction_id should fail."""
        transaction = Transaction(
            transaction_id="temp",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.transaction_id = ""
        assert validate_transaction(transaction) is False
    
    def test_invalid_timestamp_fails(self):
        """Transaction with invalid timestamp should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.timestamp = "not a datetime"
        assert validate_transaction(transaction) is False
    
    def test_negative_amount_fails(self):
        """Transaction with negative amount should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.amount = -50.0
        assert validate_transaction(transaction) is False
    
    def test_zero_amount_fails(self):
        """Transaction with zero amount should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.amount = 0.0
        assert validate_transaction(transaction) is False
    
    def test_empty_from_account_fails(self):
        """Transaction with empty from_account should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.from_account = ""
        assert validate_transaction(transaction) is False
    
    def test_empty_to_account_fails(self):
        """Transaction with empty to_account should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.to_account = ""
        assert validate_transaction(transaction) is False
    
    def test_empty_currency_fails(self):
        """Transaction with empty currency should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.currency = ""
        assert validate_transaction(transaction) is False
    
    def test_invalid_transaction_type_fails(self):
        """Transaction with invalid transaction_type should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.transaction_type = "invalid"
        assert validate_transaction(transaction) is False
    
    def test_invalid_status_fails(self):
        """Transaction with invalid status should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.status = "invalid"
        assert validate_transaction(transaction) is False
    
    def test_negative_fee_fails(self):
        """Transaction with negative fee should fail."""
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=100.0,
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=1.0
        )
        transaction.fee = -1.0
        assert validate_transaction(transaction) is False


class TestValidateFeatures:
    """Tests for validate_features function."""
    
    def test_valid_features_pass(self):
        """Valid features should pass validation."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=1000.0,
            transaction_count=10,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=5,
            night_transaction_ratio=0.2,
            rapid_transaction_count=2,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=5.0
        )
        assert validate_features(features) is True
    
    def test_negative_total_volume_fails(self):
        """Features with negative total_volume should fail."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=1000.0,
            transaction_count=10,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=5,
            night_transaction_ratio=0.2,
            rapid_transaction_count=2,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=5.0
        )
        features.total_volume = -100.0
        assert validate_features(features) is False
    
    def test_night_transaction_ratio_out_of_range_fails(self):
        """Features with night_transaction_ratio > 1 should fail."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=1000.0,
            transaction_count=10,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=5,
            night_transaction_ratio=0.2,
            rapid_transaction_count=2,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=5.0
        )
        features.night_transaction_ratio = 1.5
        assert validate_features(features) is False
    
    def test_round_number_ratio_out_of_range_fails(self):
        """Features with round_number_ratio > 1 should fail."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=1000.0,
            transaction_count=10,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=5,
            night_transaction_ratio=0.2,
            rapid_transaction_count=2,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=5.0
        )
        features.round_number_ratio = 1.2
        assert validate_features(features) is False
    
    def test_concentration_score_out_of_range_fails(self):
        """Features with concentration_score > 1 should fail."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=1000.0,
            transaction_count=10,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=5,
            night_transaction_ratio=0.2,
            rapid_transaction_count=2,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=5.0
        )
        features.concentration_score = 1.5
        assert validate_features(features) is False
    
    def test_transaction_count_mismatch_fails(self):
        """Features with mismatched transaction_count should fail."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=300.0,
            transaction_count=3,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=2,
            night_transaction_ratio=0.0,
            rapid_transaction_count=0,
            round_number_ratio=0.0,
            concentration_score=0.5,
            velocity_score=1.0
        )
        
        transactions = [
            Transaction(
                transaction_id=f"tx_{i}",
                timestamp=datetime(2024, 1, 1, 12, i),
                from_account="acc_001",
                to_account=f"acc_{i+2}",
                amount=100.0,
                currency="BTC",
                transaction_type="transfer",
                status="completed",
                fee=1.0
            )
            for i in range(5)  # 5 transactions, but features say 3
        ]
        
        assert validate_features(features, transactions) is False
    
    def test_total_volume_mismatch_fails(self):
        """Features with mismatched total_volume should fail."""
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=500.0,  # Wrong total
            transaction_count=3,
            avg_transaction_size=100.0,
            max_transaction_size=200.0,
            unique_counterparties=2,
            night_transaction_ratio=0.0,
            rapid_transaction_count=0,
            round_number_ratio=0.0,
            concentration_score=0.5,
            velocity_score=1.0
        )
        
        transactions = [
            Transaction(
                transaction_id=f"tx_{i}",
                timestamp=datetime(2024, 1, 1, 12, i),
                from_account="acc_001",
                to_account=f"acc_{i+2}",
                amount=100.0,
                currency="BTC",
                transaction_type="transfer",
                status="completed",
                fee=1.0
            )
            for i in range(3)  # Total should be 300.0
        ]
        
        assert validate_features(features, transactions) is False
    
    def test_valid_features_with_transactions_pass(self):
        """Valid features with matching transactions should pass."""
        transactions = [
            Transaction(
                transaction_id=f"tx_{i}",
                timestamp=datetime(2024, 1, 1, 12, i),
                from_account="acc_001",
                to_account=f"acc_{i+2}",
                amount=100.0,
                currency="BTC",
                transaction_type="transfer",
                status="completed",
                fee=1.0
            )
            for i in range(3)
        ]
        
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=300.0,
            transaction_count=3,
            avg_transaction_size=100.0,
            max_transaction_size=100.0,
            unique_counterparties=3,
            night_transaction_ratio=0.0,
            rapid_transaction_count=0,
            round_number_ratio=1.0,
            concentration_score=0.33,
            velocity_score=1.0
        )
        
        assert validate_features(features, transactions) is True


class TestValidateRiskAssessment:
    """Tests for validate_risk_assessment function."""
    
    def test_valid_risk_assessment_passes(self):
        """Valid risk assessment should pass validation."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume", "Night transactions"],
            explanation="Account shows suspicious patterns",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assert validate_risk_assessment(assessment) is True
    
    def test_risk_score_out_of_range_fails(self):
        """Risk assessment with score > 100 should fail."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume"],
            explanation="Test",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assessment.risk_score = 150.0
        assert validate_risk_assessment(assessment) is False
    
    def test_risk_level_mismatch_fails(self):
        """Risk assessment with mismatched risk_level should fail."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume"],
            explanation="Test",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assessment.risk_level = RiskLevel.LOW  # Doesn't match score of 75
        assert validate_risk_assessment(assessment) is False
    
    def test_empty_risk_factors_fails(self):
        """Risk assessment with empty risk_factors should fail."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume"],
            explanation="Test",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assessment.risk_factors = []
        assert validate_risk_assessment(assessment) is False
    
    def test_empty_explanation_fails(self):
        """Risk assessment with empty explanation should fail."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume"],
            explanation="Test",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assessment.explanation = ""
        assert validate_risk_assessment(assessment) is False
    
    def test_confidence_out_of_range_fails(self):
        """Risk assessment with confidence > 1 should fail."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume"],
            explanation="Test",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assessment.confidence = 1.5
        assert validate_risk_assessment(assessment) is False
    
    def test_invalid_timestamp_fails(self):
        """Risk assessment with invalid timestamp should fail."""
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=75.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume"],
            explanation="Test",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assessment.timestamp = "not a datetime"
        assert validate_risk_assessment(assessment) is False
