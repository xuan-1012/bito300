"""
Risk level classification utilities.

This module provides functions for classifying risk scores into risk levels.
"""

from ..models.data_models import RiskLevel


def classify_risk_level(risk_score: float) -> RiskLevel:
    """
    Classify a risk score into a risk level.
    
    Maps risk scores (0-100) to risk levels (LOW/MEDIUM/HIGH/CRITICAL)
    for clear categorization.
    
    Args:
        risk_score: Risk score between 0 and 100
        
    Returns:
        RiskLevel: The corresponding risk level
        - LOW: scores 0-25
        - MEDIUM: scores 26-50
        - HIGH: scores 51-75
        - CRITICAL: scores 76-100
        
    Raises:
        ValueError: If risk_score is not in the range [0, 100]
        
    Examples:
        >>> classify_risk_level(0)
        RiskLevel.LOW
        >>> classify_risk_level(25)
        RiskLevel.LOW
        >>> classify_risk_level(26)
        RiskLevel.MEDIUM
        >>> classify_risk_level(50)
        RiskLevel.MEDIUM
        >>> classify_risk_level(51)
        RiskLevel.HIGH
        >>> classify_risk_level(75)
        RiskLevel.HIGH
        >>> classify_risk_level(76)
        RiskLevel.CRITICAL
        >>> classify_risk_level(100)
        RiskLevel.CRITICAL
    """
    if not 0 <= risk_score <= 100:
        raise ValueError(f"risk_score must be between 0 and 100, got {risk_score}")
    
    if risk_score >= 76:
        return RiskLevel.CRITICAL
    elif risk_score >= 51:
        return RiskLevel.HIGH
    elif risk_score >= 26:
        return RiskLevel.MEDIUM
    else:
        return RiskLevel.LOW
