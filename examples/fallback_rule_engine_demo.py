"""
Demo script for FallbackRuleEngine.

This script demonstrates how to use the FallbackRuleEngine for rule-based
risk assessment when Bedrock or SageMaker are unavailable.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_risk_scoring.engines.fallback_rule_engine import FallbackRuleEngine
from src.model_risk_scoring.models.data_models import TransactionFeatures


def main():
    """Demonstrate FallbackRuleEngine usage with various scenarios."""
    
    # Initialize the engine
    engine = FallbackRuleEngine()
    
    print("=" * 80)
    print("FallbackRuleEngine Demo")
    print("=" * 80)
    print()
    
    # Scenario 1: Low-risk account (no rules triggered)
    print("Scenario 1: Low-Risk Account")
    print("-" * 80)
    low_risk_features = TransactionFeatures(
        account_id="account_001",
        total_volume=50000,
        transaction_count=20,
        avg_transaction_size=2500,
        max_transaction_size=5000,
        unique_counterparties=10,
        night_transaction_ratio=0.1,
        rapid_transaction_count=2,
        round_number_ratio=0.2,
        concentration_score=0.3,
        velocity_score=2.5
    )
    
    result1 = engine.calculate_risk_score(low_risk_features)
    print(f"Account ID: {low_risk_features.account_id}")
    print(f"Risk Score: {result1['risk_score']}/100")
    print(f"Risk Factors: {result1['risk_factors']}")
    print(f"Confidence: {result1['confidence']}")
    print(f"Explanation:\n{result1['explanation']}")
    print()
    
    # Scenario 2: Medium-risk account (2-3 rules triggered)
    print("Scenario 2: Medium-Risk Account")
    print("-" * 80)
    medium_risk_features = TransactionFeatures(
        account_id="account_002",
        total_volume=150000,  # Triggers high_volume (+20)
        transaction_count=50,
        avg_transaction_size=3000,
        max_transaction_size=10000,
        unique_counterparties=8,
        night_transaction_ratio=0.4,  # Triggers night_transactions (+15)
        rapid_transaction_count=5,
        round_number_ratio=0.3,
        concentration_score=0.5,
        velocity_score=5
    )
    
    result2 = engine.calculate_risk_score(medium_risk_features)
    print(f"Account ID: {medium_risk_features.account_id}")
    print(f"Risk Score: {result2['risk_score']}/100")
    print(f"Risk Factors: {result2['risk_factors']}")
    print(f"Confidence: {result2['confidence']}")
    print(f"Explanation:\n{result2['explanation']}")
    print()
    
    # Scenario 3: High-risk account (4-5 rules triggered)
    print("Scenario 3: High-Risk Account")
    print("-" * 80)
    high_risk_features = TransactionFeatures(
        account_id="account_003",
        total_volume=200000,  # Triggers high_volume (+20)
        transaction_count=100,
        avg_transaction_size=2000,
        max_transaction_size=15000,
        unique_counterparties=5,
        night_transaction_ratio=0.5,  # Triggers night_transactions (+15)
        rapid_transaction_count=15,  # Triggers rapid_transactions (+15)
        round_number_ratio=0.7,  # Triggers round_numbers (+20)
        concentration_score=0.8,  # Triggers high_concentration (+15)
        velocity_score=8
    )
    
    result3 = engine.calculate_risk_score(high_risk_features)
    print(f"Account ID: {high_risk_features.account_id}")
    print(f"Risk Score: {result3['risk_score']}/100")
    print(f"Risk Factors: {result3['risk_factors']}")
    print(f"Confidence: {result3['confidence']}")
    print(f"Explanation:\n{result3['explanation']}")
    print()
    
    # Scenario 4: Critical-risk account (all rules triggered)
    print("Scenario 4: Critical-Risk Account (All Rules Triggered)")
    print("-" * 80)
    critical_risk_features = TransactionFeatures(
        account_id="account_004",
        total_volume=500000,  # Triggers high_volume (+20)
        transaction_count=200,
        avg_transaction_size=2500,
        max_transaction_size=50000,
        unique_counterparties=3,
        night_transaction_ratio=0.8,  # Triggers night_transactions (+15)
        rapid_transaction_count=25,  # Triggers rapid_transactions (+15)
        round_number_ratio=0.9,  # Triggers round_numbers (+20)
        concentration_score=0.95,  # Triggers high_concentration (+15)
        velocity_score=15  # Triggers high_velocity (+15)
    )
    
    result4 = engine.calculate_risk_score(critical_risk_features)
    print(f"Account ID: {critical_risk_features.account_id}")
    print(f"Risk Score: {result4['risk_score']}/100 (capped)")
    print(f"Risk Factors: {result4['risk_factors']}")
    print(f"Confidence: {result4['confidence']}")
    print(f"Explanation:\n{result4['explanation']}")
    print()
    
    # Scenario 5: Boundary testing
    print("Scenario 5: Boundary Testing (Exactly at Thresholds)")
    print("-" * 80)
    boundary_features = TransactionFeatures(
        account_id="account_005",
        total_volume=100000,  # Exactly at threshold (should NOT trigger)
        transaction_count=10,
        avg_transaction_size=10000,
        max_transaction_size=20000,
        unique_counterparties=5,
        night_transaction_ratio=0.3,  # Exactly at threshold (should NOT trigger)
        rapid_transaction_count=10,  # Exactly at threshold (should NOT trigger)
        round_number_ratio=0.5,  # Exactly at threshold (should NOT trigger)
        concentration_score=0.7,  # Exactly at threshold (should NOT trigger)
        velocity_score=10  # Exactly at threshold (should NOT trigger)
    )
    
    result5 = engine.calculate_risk_score(boundary_features)
    print(f"Account ID: {boundary_features.account_id}")
    print(f"Risk Score: {result5['risk_score']}/100")
    print(f"Risk Factors: {result5['risk_factors']}")
    print(f"Confidence: {result5['confidence']}")
    print(f"Explanation:\n{result5['explanation']}")
    print()
    
    print("=" * 80)
    print("Demo Complete")
    print("=" * 80)


if __name__ == "__main__":
    main()
