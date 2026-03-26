"""
Core data models for AWS Model Risk Scoring system.

This module defines all the core data structures used throughout the risk scoring system,
including enums, dataclasses for features, assessments, and configurations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class InferenceMode(Enum):
    """Inference mode for risk assessment."""
    SUPERVISED = "supervised"      # Labeled data: use SageMaker
    UNSUPERVISED = "unsupervised"  # Unlabeled data: use Bedrock LLM
    FALLBACK = "fallback"          # Degraded: use rule engine


class RiskLevel(Enum):
    """Risk level classification with color codes for visualization."""
    LOW = ("low", "#16a34a")        # Green
    MEDIUM = ("medium", "#ca8a04")  # Yellow
    HIGH = ("high", "#ea580c")      # Orange
    CRITICAL = ("critical", "#dc2626")  # Red
    
    def __init__(self, level: str, color: str):
        self.level = level
        self.color = color


@dataclass
class TransactionFeatures:
    """
    Transaction features for risk assessment.
    
    Contains all extracted features from account transaction history
    used for risk scoring.
    """
    account_id: str
    total_volume: float  # Total transaction volume in USD
    transaction_count: int  # Number of transactions
    avg_transaction_size: float  # Average transaction amount in USD
    max_transaction_size: float  # Maximum transaction amount in USD
    unique_counterparties: int  # Number of unique counterparties
    night_transaction_ratio: float  # Ratio of transactions during night hours (0-1)
    rapid_transaction_count: int  # Number of rapid consecutive transactions
    round_number_ratio: float  # Ratio of round number amounts (0-1)
    concentration_score: float  # Counterparty concentration score (0-1)
    velocity_score: float  # Transaction velocity (transactions per hour)


@dataclass
class RiskAssessment:
    """
    Risk assessment result for an account.
    
    Contains the risk score, level, contributing factors, explanation,
    and metadata about the inference process.
    """
    account_id: str
    risk_score: float  # Risk score (0-100)
    risk_level: RiskLevel  # Risk level classification
    risk_factors: List[str]  # List of risk factors identified
    explanation: str  # Natural language explanation of the assessment
    confidence: float  # Confidence score (0-1)
    
    # Inference metadata
    inference_mode: InferenceMode
    model_id: Optional[str] = None  # Bedrock model ID or SageMaker endpoint name
    inference_time_ms: float = 0.0  # Inference time in milliseconds
    fallback_used: bool = False  # Whether fallback was used
    
    # Optional feature importance (if available from model)
    feature_importance: Optional[Dict[str, float]] = None
    
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class ModelConfig:
    """
    Configuration for model service.
    
    Contains all configuration parameters for Bedrock, SageMaker,
    rate limiting, and fallback behavior.
    """
    # Inference mode
    inference_mode: InferenceMode
    
    # Bedrock configuration
    bedrock_model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0"
    bedrock_max_tokens: int = 1024
    bedrock_temperature: float = 0.0
    
    # SageMaker configuration
    sagemaker_endpoint_name: Optional[str] = None
    sagemaker_content_type: str = "text/csv"
    sagemaker_accept: str = "application/json"
    
    # Rate limiting
    max_requests_per_second: float = 0.9
    
    # Fallback configuration
    fallback_enabled: bool = True
    fallback_confidence: float = 0.7
    
    # Feature scaling
    feature_scaling_enabled: bool = True
    scaler_params: Optional[Dict[str, Dict[str, float]]] = None
    
    def __post_init__(self):
        """Validate configuration parameters."""
        if self.max_requests_per_second >= 1.0:
            raise ValueError("max_requests_per_second must be < 1.0")
        
        if not 0.0 <= self.bedrock_temperature <= 1.0:
            raise ValueError("bedrock_temperature must be between 0.0 and 1.0")
        
        if not 0.0 <= self.fallback_confidence <= 1.0:
            raise ValueError("fallback_confidence must be between 0.0 and 1.0")
        
        if self.inference_mode == InferenceMode.SUPERVISED and self.sagemaker_endpoint_name is None:
            raise ValueError("sagemaker_endpoint_name is required when inference_mode is SUPERVISED")


@dataclass
class FeatureConfig:
    """
    Configuration for feature processing.
    
    Defines feature names, order, validation rules, and normalization parameters.
    """
    # Feature field order (used for SageMaker input)
    feature_names: List[str] = field(default_factory=lambda: [
        "total_volume",
        "transaction_count",
        "avg_transaction_size",
        "max_transaction_size",
        "unique_counterparties",
        "night_transaction_ratio",
        "rapid_transaction_count",
        "round_number_ratio",
        "concentration_score",
        "velocity_score"
    ])
    
    # Normalization parameters (mean and std for each feature)
    scaler_params: Optional[Dict[str, Dict[str, float]]] = None
    
    # Feature validation rules (min and max values)
    validation_rules: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "total_volume": {"min": 0, "max": float('inf')},
        "transaction_count": {"min": 1, "max": float('inf')},
        "avg_transaction_size": {"min": 0, "max": float('inf')},
        "max_transaction_size": {"min": 0, "max": float('inf')},
        "unique_counterparties": {"min": 0, "max": float('inf')},
        "night_transaction_ratio": {"min": 0, "max": 1},
        "rapid_transaction_count": {"min": 0, "max": float('inf')},
        "round_number_ratio": {"min": 0, "max": 1},
        "concentration_score": {"min": 0, "max": 1},
        "velocity_score": {"min": 0, "max": float('inf')}
    })
