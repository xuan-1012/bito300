"""Demo script for LiftCurveGenerator.

This script demonstrates how to use the LiftCurveGenerator to create
lift curves for binary classification model evaluation.
"""

import numpy as np
import matplotlib.pyplot as plt
from src.model_evaluation_viz.generators.lift_curve import LiftCurveGenerator
from src.model_evaluation_viz.styling.chart_styler import ChartStyler
from src.model_evaluation_viz.core.models import ChartStyle


def demo_basic_lift_curve():
    """Demonstrate basic lift curve generation."""
    print("=" * 60)
    print("Demo 1: Basic Lift Curve")
    print("=" * 60)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 100
    
    # Simulate a good classifier: positives get higher probabilities
    y_true = np.array([0] * 70 + [1] * 30)  # 30% positive class
    y_proba = np.concatenate([
        np.random.beta(2, 5, 70),  # Lower probabilities for negatives
        np.random.beta(5, 2, 30)   # Higher probabilities for positives
    ])
    
    # Create generator and generate lift curve
    generator = LiftCurveGenerator()
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    print(f"Generated lift curve with {n_samples} samples")
    print(f"Positive class proportion: {y_true.sum() / len(y_true):.2%}")
    
    plt.savefig('examples/output/lift_curve_basic.png', dpi=300, bbox_inches='tight')
    print("Saved to: examples/output/lift_curve_basic.png")
    plt.close(fig)


def demo_perfect_vs_random_classifier():
    """Compare perfect classifier vs random classifier."""
    print("\n" + "=" * 60)
    print("Demo 2: Perfect vs Random Classifier")
    print("=" * 60)
    
    # Create sample data
    n_samples = 50
    y_true = np.array([0] * 30 + [1] * 20)
    
    # Perfect classifier: all positives ranked first
    y_proba_perfect = np.concatenate([
        np.linspace(0.9, 1.0, 20),   # Positives get high scores
        np.linspace(0.0, 0.1, 30)    # Negatives get low scores
    ])
    
    # Random classifier
    np.random.seed(123)
    y_proba_random = np.random.random(n_samples)
    
    # Generate both curves
    generator = LiftCurveGenerator()
    
    fig1 = generator.generate(y_true=y_true, y_proba=y_proba_perfect)
    plt.savefig('examples/output/lift_curve_perfect.png', dpi=300, bbox_inches='tight')
    print("Perfect classifier saved to: examples/output/lift_curve_perfect.png")
    plt.close(fig1)
    
    fig2 = generator.generate(y_true=y_true, y_proba=y_proba_random)
    plt.savefig('examples/output/lift_curve_random.png', dpi=300, bbox_inches='tight')
    print("Random classifier saved to: examples/output/lift_curve_random.png")
    plt.close(fig2)


def demo_imbalanced_dataset():
    """Demonstrate lift curve with highly imbalanced dataset."""
    print("\n" + "=" * 60)
    print("Demo 3: Imbalanced Dataset (5% positive class)")
    print("=" * 60)
    
    # Create highly imbalanced data
    np.random.seed(456)
    n_samples = 200
    n_positives = 10  # Only 5% positive
    
    y_true = np.array([0] * (n_samples - n_positives) + [1] * n_positives)
    
    # Good model should rank positives highly
    y_proba = np.concatenate([
        np.random.beta(2, 8, n_samples - n_positives),  # Low scores for negatives
        np.random.beta(8, 2, n_positives)               # High scores for positives
    ])
    
    # Generate lift curve
    generator = LiftCurveGenerator()
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    print(f"Dataset: {n_samples} samples, {n_positives} positives ({n_positives/n_samples:.1%})")
    print("Lift curve shows model's ability to identify rare positive cases")
    
    plt.savefig('examples/output/lift_curve_imbalanced.png', dpi=300, bbox_inches='tight')
    print("Saved to: examples/output/lift_curve_imbalanced.png")
    plt.close(fig)


def demo_custom_styling():
    """Demonstrate lift curve with custom styling."""
    print("\n" + "=" * 60)
    print("Demo 4: Custom Styling")
    print("=" * 60)
    
    # Create sample data
    np.random.seed(789)
    n_samples = 80
    y_true = np.array([0] * 50 + [1] * 30)
    y_proba = np.concatenate([
        np.random.beta(2, 5, 50),
        np.random.beta(5, 2, 30)
    ])
    
    # Create custom style
    custom_style = ChartStyle(
        figure_size=(12, 8),
        dpi=300,
        font_size=14,
        line_width=3.0,
        color_palette=['#2E86AB', '#A23B72', '#F18F01']
    )
    
    # Create generator with custom styling
    styler = ChartStyler(style=custom_style)
    generator = LiftCurveGenerator(styler=styler)
    
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    print("Generated lift curve with custom styling:")
    print(f"  - Figure size: {custom_style.figure_size}")
    print(f"  - Font size: {custom_style.font_size}")
    print(f"  - Line width: {custom_style.line_width}")
    
    plt.savefig('examples/output/lift_curve_custom.png', dpi=300, bbox_inches='tight')
    print("Saved to: examples/output/lift_curve_custom.png")
    plt.close(fig)


def demo_real_world_scenario():
    """Simulate a real-world fraud detection scenario."""
    print("\n" + "=" * 60)
    print("Demo 5: Real-World Fraud Detection Scenario")
    print("=" * 60)
    
    # Simulate fraud detection: 2% fraud rate
    np.random.seed(999)
    n_samples = 500
    n_fraud = 10  # 2% fraud rate
    
    y_true = np.array([0] * (n_samples - n_fraud) + [1] * n_fraud)
    
    # Model with good but not perfect performance
    # Frauds get higher scores on average, but with some overlap
    y_proba = np.concatenate([
        np.random.beta(1.5, 8, n_samples - n_fraud),  # Normal transactions
        np.random.beta(6, 2, n_fraud)                  # Fraudulent transactions
    ])
    
    # Generate lift curve
    generator = LiftCurveGenerator()
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    # Calculate some insights
    sorted_indices = np.argsort(y_proba)[::-1]
    y_true_sorted = y_true[sorted_indices]
    
    # How many frauds in top 10%?
    top_10_pct = int(n_samples * 0.1)
    frauds_in_top_10 = y_true_sorted[:top_10_pct].sum()
    
    print(f"Fraud Detection Scenario:")
    print(f"  - Total transactions: {n_samples}")
    print(f"  - Fraudulent transactions: {n_fraud} ({n_fraud/n_samples:.1%})")
    print(f"  - Frauds caught in top 10% of predictions: {frauds_in_top_10}/{n_fraud} ({frauds_in_top_10/n_fraud:.1%})")
    print(f"  - Lift at 10%: {(frauds_in_top_10/n_fraud) / 0.1:.2f}x")
    
    plt.savefig('examples/output/lift_curve_fraud_detection.png', dpi=300, bbox_inches='tight')
    print("Saved to: examples/output/lift_curve_fraud_detection.png")
    plt.close(fig)


if __name__ == "__main__":
    # Create output directory if it doesn't exist
    import os
    os.makedirs('examples/output', exist_ok=True)
    
    # Run all demos
    demo_basic_lift_curve()
    demo_perfect_vs_random_classifier()
    demo_imbalanced_dataset()
    demo_custom_styling()
    demo_real_world_scenario()
    
    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60)
