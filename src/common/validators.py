"""
Validators module for Crypto Suspicious Account Detection system.

This module provides validation functions for Transaction, TransactionFeatures,
and RiskAssessment objects to ensure data integrity throughout the system.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6**
"""

import logging
from typing import List, Optional
from datetime import datetime

from src.common.models import Transaction, TransactionFeatures, RiskAssessment, RiskLevel


# Configure logging
logger = logging.getLogger(__name__)


def validate_transaction(transaction: Transaction) -> bool:
    """
    Validate a Transaction object for required fields and data types.
    
    **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**
    
    Args:
        transaction: Transaction object to validate
        
    Returns:
        True if transaction is valid, False otherwise
        
    Validation Rules:
        - transaction_id must be non-empty (Requirement 2.1)
        - timestamp must be valid datetime (Requirement 2.2)
        - amount must be positive (Requirement 2.3)
        - from_account and to_account must be valid identifiers (Requirement 2.4)
        - currency must be valid code (Requirement 2.5)
        - Logs validation errors (Requirement 2.6, 15.6)
    """
    try:
        # Requirement 2.1: Validate transaction_id is non-empty
        if not transaction.transaction_id:
            logger.error(f"Validation failed: transaction_id is empty")
            return False
        
        # Requirement 2.2: Validate timestamp is valid datetime
        if not isinstance(transaction.timestamp, datetime):
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"timestamp is not a datetime object"
            )
            return False
        
        # Requirement 2.3: Validate amount is positive
        if transaction.amount <= 0:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"amount {transaction.amount} is not positive"
            )
            return False
        
        # Requirement 2.4: Validate from_account and to_account are valid
        if not transaction.from_account:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"from_account is empty"
            )
            return False
        
        if not transaction.to_account:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"to_account is empty"
            )
            return False
        
        # Requirement 2.5: Validate currency is valid
        if not transaction.currency:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"currency is empty"
            )
            return False
        
        # Additional validations from Transaction model
        if transaction.transaction_type not in ["deposit", "withdrawal", "transfer"]:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"invalid transaction_type '{transaction.transaction_type}'"
            )
            return False
        
        if transaction.status not in ["completed", "pending", "failed"]:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"invalid status '{transaction.status}'"
            )
            return False
        
        if transaction.fee < 0:
            logger.error(
                f"Validation failed for transaction {transaction.transaction_id}: "
                f"fee {transaction.fee} is negative"
            )
            return False
        
        return True
        
    except Exception as e:
        # Requirement 2.6, 15.6: Log validation errors
        logger.error(
            f"Validation exception for transaction {getattr(transaction, 'transaction_id', 'unknown')}: {e}"
        )
        return False


def validate_features(
    features: TransactionFeatures,
    input_transactions: Optional[List[Transaction]] = None
) -> bool:
    """
    Validate a TransactionFeatures object for data quality and consistency.
    
    **Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5, 15.6**
    
    Args:
        features: TransactionFeatures object to validate
        input_transactions: Optional list of input transactions for cross-validation
        
    Returns:
        True if features are valid, False otherwise
        
    Validation Rules:
        - All feature values must be non-negative (Requirement 15.1)
        - Ratio features must be between 0 and 1 (Requirement 15.2)
        - concentration_score must be between 0 and 1 (Requirement 15.3)
        - transaction_count must match input if provided (Requirement 15.4)
        - total_volume must equal sum of amounts if input provided (Requirement 15.5)
        - Logs validation errors (Requirement 15.6)
    """
    try:
        # Requirement 15.1: Validate all feature values are non-negative
        if features.total_volume < 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"total_volume {features.total_volume} is negative"
            )
            return False
        
        if features.transaction_count <= 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"transaction_count {features.transaction_count} is not positive"
            )
            return False
        
        if features.avg_transaction_size < 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"avg_transaction_size {features.avg_transaction_size} is negative"
            )
            return False
        
        if features.max_transaction_size < 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"max_transaction_size {features.max_transaction_size} is negative"
            )
            return False
        
        if features.unique_counterparties < 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"unique_counterparties {features.unique_counterparties} is negative"
            )
            return False
        
        if features.rapid_transaction_count < 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"rapid_transaction_count {features.rapid_transaction_count} is negative"
            )
            return False
        
        if features.velocity_score < 0:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"velocity_score {features.velocity_score} is negative"
            )
            return False
        
        # Requirement 15.2: Validate ratio features are between 0 and 1
        if not 0 <= features.night_transaction_ratio <= 1:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"night_transaction_ratio {features.night_transaction_ratio} is not between 0 and 1"
            )
            return False
        
        if not 0 <= features.round_number_ratio <= 1:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"round_number_ratio {features.round_number_ratio} is not between 0 and 1"
            )
            return False
        
        # Requirement 15.3: Validate concentration_score is between 0 and 1
        if not 0 <= features.concentration_score <= 1:
            logger.error(
                f"Validation failed for account {features.account_id}: "
                f"concentration_score {features.concentration_score} is not between 0 and 1"
            )
            return False
        
        # Cross-validation with input transactions if provided
        if input_transactions is not None:
            # Requirement 15.4: Validate transaction_count matches input
            if features.transaction_count != len(input_transactions):
                logger.error(
                    f"Validation failed for account {features.account_id}: "
                    f"transaction_count {features.transaction_count} does not match "
                    f"input count {len(input_transactions)}"
                )
                return False
            
            # Requirement 15.5: Validate total_volume equals sum of amounts (within tolerance)
            expected_volume = sum(txn.amount for txn in input_transactions)
            tolerance = 0.01
            if abs(features.total_volume - expected_volume) > tolerance:
                logger.error(
                    f"Validation failed for account {features.account_id}: "
                    f"total_volume {features.total_volume} does not match "
                    f"sum of amounts {expected_volume} (tolerance: {tolerance})"
                )
                return False
        
        return True
        
    except Exception as e:
        # Requirement 15.6: Log validation errors
        logger.error(
            f"Validation exception for account {getattr(features, 'account_id', 'unknown')}: {e}"
        )
        return False


def validate_risk_assessment(assessment: RiskAssessment) -> bool:
    """
    Validate a RiskAssessment object for correctness and consistency.
    
    **Validates: Requirements related to risk assessment validation**
    
    Args:
        assessment: RiskAssessment object to validate
        
    Returns:
        True if assessment is valid, False otherwise
        
    Validation Rules:
        - account_id must be non-empty
        - risk_score must be between 0 and 100
        - risk_level must match risk_score range
        - risk_factors must be non-empty list
        - explanation must be non-empty
        - confidence must be between 0 and 1
        - timestamp must be valid datetime
        - Logs validation errors
    """
    try:
        # Validate account_id is non-empty
        if not assessment.account_id:
            logger.error("Validation failed: account_id is empty")
            return False
        
        # Validate risk_score is between 0 and 100
        if not 0 <= assessment.risk_score <= 100:
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"risk_score {assessment.risk_score} is not between 0 and 100"
            )
            return False
        
        # Validate risk_level is a RiskLevel enum
        if not isinstance(assessment.risk_level, RiskLevel):
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"risk_level is not a RiskLevel enum"
            )
            return False
        
        # Validate risk_level matches risk_score range
        expected_level = RiskLevel.from_score(assessment.risk_score)
        if assessment.risk_level != expected_level:
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"risk_level {assessment.risk_level.value} does not match "
                f"risk_score {assessment.risk_score} (expected {expected_level.value})"
            )
            return False
        
        # Validate risk_factors is non-empty
        if not assessment.risk_factors:
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"risk_factors is empty"
            )
            return False
        
        # Validate explanation is non-empty
        if not assessment.explanation:
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"explanation is empty"
            )
            return False
        
        # Validate confidence is between 0 and 1
        if not 0 <= assessment.confidence <= 1:
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"confidence {assessment.confidence} is not between 0 and 1"
            )
            return False
        
        # Validate timestamp is valid datetime
        if not isinstance(assessment.timestamp, datetime):
            logger.error(
                f"Validation failed for account {assessment.account_id}: "
                f"timestamp is not a datetime object"
            )
            return False
        
        return True
        
    except Exception as e:
        # Log validation errors
        logger.error(
            f"Validation exception for account {getattr(assessment, 'account_id', 'unknown')}: {e}"
        )
        return False
