"""
Demo script for risk level classification.

This script demonstrates how to use the classify_risk_level function
to map risk scores to risk levels.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_risk_scoring.utils.risk_classifier import classify_risk_level
from src.model_risk_scoring.models.data_models import RiskLevel


def main():
    """Demonstrate risk level classification with various scores."""
    
    print("Risk Level Classification Demo")
    print("=" * 50)
    print()
    
    # Test various risk scores
    test_scores = [0, 10, 25, 26, 40, 50, 51, 65, 75, 76, 90, 100]
    
    print("Risk Score -> Risk Level Mapping:")
    print("-" * 50)
    
    for score in test_scores:
        level = classify_risk_level(score)
        print(f"Score: {score:3d} -> Level: {level.level:8s} (Color: {level.color})")
    
    print()
    print("=" * 50)
    print()
    
    # Demonstrate with float values
    print("Float Score Examples:")
    print("-" * 50)
    
    float_scores = [12.5, 25.9, 26.1, 50.5, 75.9, 88.3]
    
    for score in float_scores:
        level = classify_risk_level(score)
        print(f"Score: {score:5.1f} -> Level: {level.level:8s} (Color: {level.color})")
    
    print()
    print("=" * 50)
    print()
    
    # Demonstrate error handling
    print("Error Handling:")
    print("-" * 50)
    
    invalid_scores = [-10, 150]
    
    for score in invalid_scores:
        try:
            level = classify_risk_level(score)
            print(f"Score: {score} -> Level: {level.level}")
        except ValueError as e:
            print(f"Score: {score} -> Error: {e}")
    
    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
