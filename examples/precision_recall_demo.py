"""Demo script for PrecisionRecallCurveGenerator.

This script demonstrates how to generate Precision-Recall curves for
binary classification model evaluation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.generators.precision_recall import PrecisionRecallCurveGenerator
from src.model_evaluation_viz.styling.chart_styler import ChartStyler
from src.model_evaluation_viz.core.models import ChartStyle


def demo_basic_pr_curve():
    """Demonstrate basic Precision-Recall curve generation."""
    print("Demo 1: Basic Precision-Recall Curve")
    print("-" * 50)
    
    # Create sample data with good separation
    np.random.seed(42)
    y_true = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.3, 0.15, 0.25, 0.7, 0.8, 0.9, 0.75, 0.85])
    
    # Create generator and generate curve
    generator = PrecisionRecallCurveGenerator()
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    # Save the figure
    output_path = "output/pr_curve_basic.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved basic PR curve to: {output_path}")
    
    plt.close(fig)
    print()


def demo_imbalanced_dataset():
    """Demonstrate PR curve with imbalanced dataset."""
    print("Demo 2: Precision-Recall Curve with Imbalanced Dataset")
    print("-" * 50)
    
    # Create imbalanced dataset (90% negative, 10% positive)
    np.random.seed(42)
    n_samples = 100
    n_positive = 10
    n_negative = n_samples - n_positive
    
    y_true = np.array([0] * n_negative + [1] * n_positive)
    
    # Generate probabilities with some separation
    y_proba_negative = np.random.beta(2, 5, n_negative)  # Skewed towards 0
    y_proba_positive = np.random.beta(5, 2, n_positive)  # Skewed towards 1
    y_proba = np.concatenate([y_proba_negative, y_proba_positive])
    
    # Create generator and generate curve
    generator = PrecisionRecallCurveGenerator()
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    # Save the figure
    output_path = "output/pr_curve_imbalanced.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved imbalanced PR curve to: {output_path}")
    print(f"Dataset: {n_negative} negative, {n_positive} positive samples")
    print(f"Baseline precision: {n_positive / n_samples:.3f}")
    
    plt.close(fig)
    print()


def demo_custom_styling():
    """Demonstrate PR curve with custom styling."""
    print("Demo 3: Precision-Recall Curve with Custom Styling")
    print("-" * 50)
    
    # Create sample data
    np.random.seed(42)
    y_true = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
    y_proba = np.array([0.1, 0.2, 0.3, 0.15, 0.25, 0.7, 0.8, 0.9, 0.75, 0.85])
    
    # Create custom style
    custom_style = ChartStyle(
        figure_size=(12, 8),
        dpi=300,
        font_size=14,
        title_font_size=16,
        line_width=3.0,
        grid=True,
        grid_alpha=0.4
    )
    
    # Create generator with custom styling
    styler = ChartStyler(custom_style)
    generator = PrecisionRecallCurveGenerator(styler=styler)
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    # Save the figure
    output_path = "output/pr_curve_custom_style.png"
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Saved custom styled PR curve to: {output_path}")
    print(f"Custom settings: figure_size={custom_style.figure_size}, line_width={custom_style.line_width}")
    
    plt.close(fig)
    print()


def demo_perfect_vs_random_classifier():
    """Compare perfect and random classifiers."""
    print("Demo 4: Perfect vs Random Classifier Comparison")
    print("-" * 50)
    
    # Perfect classifier
    y_true_perfect = np.array([0, 0, 0, 1, 1, 1])
    y_proba_perfect = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
    
    generator = PrecisionRecallCurveGenerator()
    fig_perfect = generator.generate(y_true=y_true_perfect, y_proba=y_proba_perfect)
    fig_perfect.savefig("output/pr_curve_perfect.png", dpi=300, bbox_inches='tight')
    print("Saved perfect classifier PR curve to: output/pr_curve_perfect.png")
    plt.close(fig_perfect)
    
    # Random classifier
    np.random.seed(42)
    y_true_random = np.random.randint(0, 2, 100)
    y_proba_random = np.random.random(100)
    
    fig_random = generator.generate(y_true=y_true_random, y_proba=y_proba_random)
    fig_random.savefig("output/pr_curve_random.png", dpi=300, bbox_inches='tight')
    print("Saved random classifier PR curve to: output/pr_curve_random.png")
    plt.close(fig_random)
    
    print()


def main():
    """Run all demos."""
    print("=" * 50)
    print("Precision-Recall Curve Generator Demo")
    print("=" * 50)
    print()
    
    # Create output directory if it doesn't exist
    import os
    os.makedirs("output", exist_ok=True)
    
    # Run demos
    demo_basic_pr_curve()
    demo_imbalanced_dataset()
    demo_custom_styling()
    demo_perfect_vs_random_classifier()
    
    print("=" * 50)
    print("All demos completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
