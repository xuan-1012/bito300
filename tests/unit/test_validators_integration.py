"""
Integration tests demonstrating validators working together.

**Validates: Requirements 2.1-2.6, 15.1-15.6**
"""

import pytest
from datetime import datetime
from src.common.models import Transaction, TransactionFeatures, RiskAssessment, RiskLevel
from src.common.validators import validate_transaction, validate_features, validate_risk_assessment


class TestValidatorsIntegration:
    """Integration tests for validators module."""
    
    def test_complete_validation_workflow(self):
        """Test complete validation workflow from transactions to risk assessment."""
        # Step 1: Create and validate transactions
        transactions = [
            Transaction(
                transaction_id=f"tx_{i}",
                timestamp=datetime(2024, 1, 1, 12, i),
                from_account="acc_001",
                to_account=f"acc_{i+2}",
                amount=100.0 * (i + 1),
                currency="BTC",
                transaction_type="transfer",
                status="completed",
                fee=1.0
            )
            for i in range(5)
        ]
        
        # Validate all transactions
        for txn in transactions:
            assert validate_transaction(txn) is True
        
        # Step 2: Create and validate features
        total_volume = sum(txn.amount for txn in transactions)
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=total_volume,
            transaction_count=len(transactions),
            avg_transaction_size=total_volume / len(transactions),
            max_transaction_size=max(txn.amount for txn in transactions),
            unique_counterparties=len(set(txn.to_account for txn in transactions)),
            night_transaction_ratio=0.0,
            rapid_transaction_count=0,
            round_number_ratio=1.0,
            concentration_score=0.2,
            velocity_score=5.0
        )
        
        # Validate features without transactions
        assert validate_features(features) is True
        
        # Validate features with transactions
        assert validate_features(features, transactions) is True
        
        # Step 3: Create and validate risk assessment
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=65.0,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High transaction volume", "Multiple counterparties"],
            explanation="Account shows moderate risk patterns with high volume",
            confidence=0.85,
            timestamp=datetime(2024, 1, 1, 13, 0)
        )
        
        # Validate risk assessment
        assert validate_risk_assessment(assessment) is True
    
    def test_validation_catches_inconsistent_data(self):
        """Test that validators catch inconsistent data across the pipeline."""
        # Create transactions
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
        
        # Create features with WRONG total_volume
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=500.0,  # Should be 300.0
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
        
        # Validation should fail when cross-checking with transactions
        assert validate_features(features, transactions) is False
        
        # But should pass without transactions (no cross-validation)
        assert validate_features(features) is True
    
    def test_validation_with_edge_cases(self):
        """Test validators with edge case values."""
        # Single transaction
        transaction = Transaction(
            transaction_id="tx_001",
            timestamp=datetime(2024, 1, 1, 12, 0),
            from_account="acc_001",
            to_account="acc_002",
            amount=0.01,  # Minimum positive amount
            currency="BTC",
            transaction_type="transfer",
            status="completed",
            fee=0.0  # Zero fee is valid
        )
        assert validate_transaction(transaction) is True
        
        # Features with boundary values
        features = TransactionFeatures(
            account_id="acc_001",
            total_volume=0.01,
            transaction_count=1,
            avg_transaction_size=0.01,
            max_transaction_size=0.01,
            unique_counterparties=1,
            night_transaction_ratio=0.0,  # Minimum
            rapid_transaction_count=0,
            round_number_ratio=1.0,  # Maximum
            concentration_score=1.0,  # Maximum (single counterparty)
            velocity_score=0.0
        )
        assert validate_features(features) is True
        
        # Risk assessment with boundary values
        assessment = RiskAssessment(
            account_id="acc_001",
            risk_score=0.0,  # Minimum
            risk_level=RiskLevel.LOW,
            risk_factors=["No risk factors identified"],
            explanation="Account shows no suspicious patterns",
            confidence=1.0,  # Maximum
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assert validate_risk_assessment(assessment) is True
        
        # Critical risk assessment
        assessment_critical = RiskAssessment(
            account_id="acc_002",
            risk_score=100.0,  # Maximum
            risk_level=RiskLevel.CRITICAL,
            risk_factors=["Multiple high-risk factors"],
            explanation="Account shows severe risk patterns",
            confidence=0.0,  # Minimum (low confidence)
            timestamp=datetime(2024, 1, 1, 12, 0)
        )
        assert validate_risk_assessment(assessment_critical) is True
