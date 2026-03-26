"""
Fallback Rule Engine for risk assessment.

This module provides a rule-based fallback mechanism when Bedrock or SageMaker
are unavailable. It uses threshold-based rules to calculate risk scores.
"""

from typing import Dict, List, Tuple, Union
from ..models.data_models import TransactionFeatures


class FallbackRuleEngine:
    """
    Rule-based fallback engine for risk assessment.
    
    When Bedrock or SageMaker are unavailable, this engine provides
    a stable fallback using threshold-based rules. Always returns
    confidence of 0.7.
    """
    
    def __init__(self):
        """Initialize the fallback rule engine with predefined rules."""
        self.rules = [
            {
                "name": "high_volume",
                "condition": lambda f: f.total_volume > 100000,
                "score": 20,
                "reason": "總交易量超過 $100,000，屬於高風險範圍"
            },
            {
                "name": "night_transactions",
                "condition": lambda f: f.night_transaction_ratio > 0.3,
                "score": 15,
                "reason": "深夜交易比例超過 30%，可能規避監控"
            },
            {
                "name": "round_numbers",
                "condition": lambda f: f.round_number_ratio > 0.5,
                "score": 20,
                "reason": "整數金額比例超過 50%，疑似結構化交易"
            },
            {
                "name": "high_concentration",
                "condition": lambda f: f.concentration_score > 0.7,
                "score": 15,
                "reason": "交易對手集中度過高，可能循環交易"
            },
            {
                "name": "rapid_transactions",
                "condition": lambda f: f.rapid_transaction_count > 10,
                "score": 15,
                "reason": "短時間內大量交易，可能自動化洗錢"
            },
            {
                "name": "high_velocity",
                "condition": lambda f: f.velocity_score > 10,
                "score": 15,
                "reason": "交易速度超過 10 筆/小時，異常活躍"
            }
        ]
    
    def calculate_risk_score(
        self,
        features: TransactionFeatures
    ) -> Dict[str, Union[float, List[str], str]]:
        """
        Calculate risk score using rule-based approach.
        
        Args:
            features: Transaction features for the account
            
        Returns:
            Dictionary containing:
                - risk_score: Risk score (0-100), capped at 100
                - risk_factors: List of triggered rule names
                - explanation: Natural language explanation
                - confidence: Always 0.7 for fallback
        """
        triggered_rules = self.apply_rules(features)
        
        # Calculate total score
        total_score = sum(score for _, score, _ in triggered_rules)
        
        # Cap at 100
        risk_score = min(total_score, 100)
        
        # Extract risk factors (rule names)
        risk_factors = [name for name, _, _ in triggered_rules]
        
        # Generate explanation
        explanation = self._generate_explanation(triggered_rules, risk_score)
        
        return {
            "risk_score": risk_score,
            "risk_factors": risk_factors,
            "explanation": explanation,
            "confidence": 0.7
        }
    
    def apply_rules(
        self,
        features: TransactionFeatures
    ) -> List[Tuple[str, float, str]]:
        """
        Apply all rules and return triggered rules.
        
        Args:
            features: Transaction features for the account
            
        Returns:
            List of tuples (rule_name, score_contribution, reason)
            for all triggered rules
        """
        triggered = []
        
        for rule in self.rules:
            if rule["condition"](features):
                triggered.append((
                    rule["name"],
                    rule["score"],
                    rule["reason"]
                ))
        
        return triggered
    
    def _generate_explanation(
        self,
        triggered_rules: List[Tuple[str, float, str]],
        risk_score: float
    ) -> str:
        """
        Generate natural language explanation for the risk assessment.
        
        Args:
            triggered_rules: List of triggered rules with reasons
            risk_score: Final risk score
            
        Returns:
            Natural language explanation in Traditional Chinese
        """
        if not triggered_rules:
            return "未發現明顯風險因子，交易行為正常。"
        
        explanation_parts = [
            f"風險評分：{risk_score}/100",
            f"觸發 {len(triggered_rules)} 項風險規則："
        ]
        
        for name, score, reason in triggered_rules:
            explanation_parts.append(f"- {reason} (+{score} 分)")
        
        return "\n".join(explanation_parts)
