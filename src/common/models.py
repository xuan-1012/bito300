"""
Data models for Crypto Suspicious Account Detection system.

This module defines the core data structures used throughout the system:
- Transaction: Raw transaction data from BitoPro API
- TransactionFeatures: Extracted risk features for an account
- RiskAssessment: AI-driven risk assessment results
- AnalysisReport: Comprehensive analysis report with statistics
- RiskLevel: Enum for risk classification
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class RiskLevel(Enum):
    """
    Risk level classification based on risk score ranges.
    
    - LOW: 0-25 (minimal risk)
    - MEDIUM: 26-50 (moderate risk, monitor)
    - HIGH: 51-75 (significant risk, investigate)
    - CRITICAL: 76-100 (severe risk, immediate action)
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def from_score(cls, score: float) -> 'RiskLevel':
        """
        Determine risk level from risk score.
        
        Args:
            score: Risk score between 0 and 100
            
        Returns:
            Corresponding RiskLevel
            
        Raises:
            ValueError: If score is not between 0 and 100
        """
        if not 0 <= score <= 100:
            raise ValueError(f"Risk score must be between 0 and 100, got {score}")
        
        if score >= 76:
            return cls.CRITICAL
        elif score >= 51:
            return cls.HIGH
        elif score >= 26:
            return cls.MEDIUM
        else:
            return cls.LOW


@dataclass
class Transaction:
    """
    Represents a cryptocurrency transaction from BitoPro API.
    
    Attributes:
        transaction_id: Unique transaction identifier
        timestamp: Transaction timestamp
        from_account: Sender account identifier
        to_account: Receiver account identifier
        amount: Transaction amount (must be positive)
        currency: Cryptocurrency code (BTC, ETH, USDT, etc.)
        transaction_type: Type of transaction (deposit, withdrawal, transfer)
        status: Transaction status (completed, pending, failed)
        fee: Transaction fee
        metadata: Optional additional transaction metadata
    """
    transaction_id: str
    timestamp: datetime
    from_account: str
    to_account: str
    amount: float
    currency: str
    transaction_type: str
    status: str
    fee: float
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate transaction data after initialization."""
        if not self.transaction_id:
            raise ValueError("transaction_id cannot be empty")
        
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime object")
        
        if self.amount <= 0:
            raise ValueError(f"amount must be positive, got {self.amount}")
        
        if not self.from_account:
            raise ValueError("from_account cannot be empty")
        
        if not self.to_account:
            raise ValueError("to_account cannot be empty")
        
        if not self.currency:
            raise ValueError("currency cannot be empty")
        
        if self.transaction_type not in ["deposit", "withdrawal", "transfer"]:
            raise ValueError(
                f"transaction_type must be one of [deposit, withdrawal, transfer], "
                f"got {self.transaction_type}"
            )
        
        if self.status not in ["completed", "pending", "failed"]:
            raise ValueError(
                f"status must be one of [completed, pending, failed], "
                f"got {self.status}"
            )
        
        if self.fee < 0:
            raise ValueError(f"fee cannot be negative, got {self.fee}")


@dataclass
class TransactionFeatures:
    """
    Extracted risk features for an account based on transaction history.
    
    These features are used for risk assessment and fraud detection.
    
    Attributes:
        account_id: Account identifier
        total_volume: Sum of all transaction amounts
        transaction_count: Number of transactions
        avg_transaction_size: Average transaction amount
        max_transaction_size: Maximum transaction amount
        unique_counterparties: Number of unique counterparties
        night_transaction_ratio: Proportion of transactions between 00:00-06:00 (0-1)
        rapid_transaction_count: Number of transactions within 5 minutes of each other
        round_number_ratio: Proportion of round number amounts (0-1)
        concentration_score: Herfindahl index for counterparty concentration (0-1)
        velocity_score: Transaction frequency per hour
    """
    account_id: str
    total_volume: float
    transaction_count: int
    avg_transaction_size: float
    max_transaction_size: float
    unique_counterparties: int
    night_transaction_ratio: float
    rapid_transaction_count: int
    round_number_ratio: float
    concentration_score: float
    velocity_score: float
    
    def __post_init__(self):
        """Validate feature values after initialization."""
        if not self.account_id:
            raise ValueError("account_id cannot be empty")
        
        if self.total_volume < 0:
            raise ValueError(f"total_volume must be non-negative, got {self.total_volume}")
        
        if self.transaction_count <= 0:
            raise ValueError(f"transaction_count must be positive, got {self.transaction_count}")
        
        if self.avg_transaction_size < 0:
            raise ValueError(f"avg_transaction_size must be non-negative, got {self.avg_transaction_size}")
        
        if self.max_transaction_size < 0:
            raise ValueError(f"max_transaction_size must be non-negative, got {self.max_transaction_size}")
        
        if self.unique_counterparties < 0:
            raise ValueError(f"unique_counterparties must be non-negative, got {self.unique_counterparties}")
        
        if not 0 <= self.night_transaction_ratio <= 1:
            raise ValueError(
                f"night_transaction_ratio must be between 0 and 1, "
                f"got {self.night_transaction_ratio}"
            )
        
        if self.rapid_transaction_count < 0:
            raise ValueError(
                f"rapid_transaction_count must be non-negative, "
                f"got {self.rapid_transaction_count}"
            )
        
        if not 0 <= self.round_number_ratio <= 1:
            raise ValueError(
                f"round_number_ratio must be between 0 and 1, "
                f"got {self.round_number_ratio}"
            )
        
        if not 0 <= self.concentration_score <= 1:
            raise ValueError(
                f"concentration_score must be between 0 and 1, "
                f"got {self.concentration_score}"
            )
        
        if self.velocity_score < 0:
            raise ValueError(f"velocity_score must be non-negative, got {self.velocity_score}")


@dataclass
class RiskAssessment:
    """
    AI-driven risk assessment for an account.
    
    Attributes:
        account_id: Account identifier
        risk_score: Risk score between 0 and 100
        risk_level: Risk level classification (LOW, MEDIUM, HIGH, CRITICAL)
        risk_factors: List of identified risk factors
        explanation: Human-readable explanation of the risk assessment
        confidence: Confidence score between 0 and 1
        timestamp: Assessment timestamp
    """
    account_id: str
    risk_score: float
    risk_level: RiskLevel
    risk_factors: List[str]
    explanation: str
    confidence: float
    timestamp: datetime
    
    def __post_init__(self):
        """Validate risk assessment data after initialization."""
        if not self.account_id:
            raise ValueError("account_id cannot be empty")
        
        if not 0 <= self.risk_score <= 100:
            raise ValueError(f"risk_score must be between 0 and 100, got {self.risk_score}")
        
        if not isinstance(self.risk_level, RiskLevel):
            raise ValueError(f"risk_level must be a RiskLevel enum, got {type(self.risk_level)}")
        
        # Validate risk level matches risk score
        expected_level = RiskLevel.from_score(self.risk_score)
        if self.risk_level != expected_level:
            raise ValueError(
                f"risk_level {self.risk_level.value} does not match risk_score {self.risk_score}. "
                f"Expected {expected_level.value}"
            )
        
        if not self.risk_factors:
            raise ValueError("risk_factors cannot be empty")
        
        if not self.explanation:
            raise ValueError("explanation cannot be empty")
        
        if not 0 <= self.confidence <= 1:
            raise ValueError(f"confidence must be between 0 and 1, got {self.confidence}")
        
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime object")


@dataclass
class AnalysisReport:
    """
    Comprehensive analysis report with statistics and visualizations.
    
    Attributes:
        report_id: Unique report identifier
        created_at: Report creation timestamp
        total_accounts: Total number of accounts analyzed
        total_transactions: Total number of transactions processed
        risk_distribution: Count of accounts by risk level
        average_risk_score: Average risk score across all accounts
        top_suspicious_accounts: List of account IDs sorted by risk score (descending)
        charts: List of S3 URIs for generated charts
        summary: Additional summary statistics and metadata
    """
    report_id: str
    created_at: datetime
    total_accounts: int
    total_transactions: int
    risk_distribution: Dict[RiskLevel, int]
    average_risk_score: float
    top_suspicious_accounts: List[str]
    charts: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate report data after initialization."""
        if not self.report_id:
            raise ValueError("report_id cannot be empty")
        
        if not isinstance(self.created_at, datetime):
            raise ValueError("created_at must be a datetime object")
        
        if self.total_accounts < 0:
            raise ValueError(f"total_accounts must be non-negative, got {self.total_accounts}")
        
        if self.total_transactions < 0:
            raise ValueError(f"total_transactions must be non-negative, got {self.total_transactions}")
        
        if not 0 <= self.average_risk_score <= 100:
            raise ValueError(
                f"average_risk_score must be between 0 and 100, "
                f"got {self.average_risk_score}"
            )
        
        # Validate risk distribution sums to total accounts
        if self.risk_distribution:
            distribution_sum = sum(self.risk_distribution.values())
            if distribution_sum != self.total_accounts:
                raise ValueError(
                    f"Sum of risk_distribution ({distribution_sum}) must equal "
                    f"total_accounts ({self.total_accounts})"
                )
        
        # Validate all chart URIs are non-empty strings
        for chart_uri in self.charts:
            if not chart_uri or not isinstance(chart_uri, str):
                raise ValueError(f"Invalid chart URI: {chart_uri}")
