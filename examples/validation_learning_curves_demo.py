"""Demo script for validation and learning curve generators.

This script demonstrates how to use the ValidationCurveGenerator and
LearningCurveGenerator classes to create publication-quality charts
for model evaluation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.generators.validation_curve import ValidationCurveGenerator
from src.model_evaluation_viz.generators.learning_curve import LearningCurveGenerator
from src.model_evaluation_viz.core.models import ChartStyle
from src.model_evaluation_viz.styling.chart_styler import ChartStyler


def demo_validation_curve():
    """Demonstrate validation curve generation."""
    print("Generating validation curve examples...")
    
    # Example 1: Regularization parameter (C) with log scale
    param_values = np.array([0.001, 0.01, 0.1, 1.0, 10.0, 100.0])
    train_scores = np.array([0.95, 0.93, 0.90, 0.88, 0.85, 0.82])
    val_scores = np.array([0.70, 0.78, 0.84, 0.86, 0.85, 0.82])
    
    generator = ValidationCurveGenerator()
    
    # Generate with log scale
    fig = generator.generate(
        param_values=param_values,
        train_scores=train_scores,
        val_scores=val_scores,
        param_name='C (Regularization Parameter)',
        log_scale=True
    )
    
    fig.savefig('output/validation_curve_regularization.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/validation_curve_regularization.png")
    plt.close(fig)
    
    # Example 2: Max depth parameter (no log scale)
    param_values_depth = np.array([1, 2, 3, 5, 7, 10, 15, 20])
    train_scores_depth = np.array([0.75, 0.82, 0.88, 0.92, 0.95, 0.97, 0.98, 0.99])
    val_scores_depth = np.array([0.74, 0.80, 0.85, 0.87, 0.86, 0.84, 0.81, 0.78])
    
    fig2 = generator.generate(
        param_values=param_values_depth,
        train_scores=train_scores_depth,
        val_scores=val_scores_depth,
        param_name='Max Depth',
        log_scale=False
    )
    
    fig2.savefig('output/validation_curve_max_depth.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/validation_curve_max_depth.png")
    plt.close(fig2)
    
    # Example 3: Custom styling
    custom_style = ChartStyle(
        figure_size=(12, 7),
        font_size=14,
        title_font_size=16,
        line_width=2.5,
        grid=True
    )
    custom_styler = ChartStyler(custom_style)
    custom_generator = ValidationCurveGenerator(styler=custom_styler)
    
    fig3 = custom_generator.generate(
        param_values=param_values,
        train_scores=train_scores,
        val_scores=val_scores,
        param_name='C (Regularization Parameter)',
        log_scale=True
    )
    
    fig3.savefig('output/validation_curve_custom_style.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/validation_curve_custom_style.png")
    plt.close(fig3)


def demo_learning_curve():
    """Demonstrate learning curve generation."""
    print("\nGenerating learning curve examples...")
    
    # Example 1: Basic learning curve without variance
    train_sizes = np.array([50, 100, 200, 500, 1000, 2000, 5000])
    train_scores = np.array([0.98, 0.95, 0.92, 0.90, 0.88, 0.87, 0.86])
    val_scores = np.array([0.65, 0.72, 0.78, 0.82, 0.84, 0.85, 0.86])
    
    generator = LearningCurveGenerator()
    
    fig = generator.generate(
        train_sizes=train_sizes,
        train_scores=train_scores,
        val_scores=val_scores
    )
    
    fig.savefig('output/learning_curve_basic.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/learning_curve_basic.png")
    plt.close(fig)
    
    # Example 2: Learning curve with variance bands
    train_std = np.array([0.03, 0.025, 0.02, 0.015, 0.01, 0.008, 0.005])
    val_std = np.array([0.08, 0.06, 0.05, 0.04, 0.03, 0.025, 0.02])
    
    fig2 = generator.generate(
        train_sizes=train_sizes,
        train_scores=train_scores,
        val_scores=val_scores,
        train_std=train_std,
        val_std=val_std
    )
    
    fig2.savefig('output/learning_curve_with_variance.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/learning_curve_with_variance.png")
    plt.close(fig2)
    
    # Example 3: Well-fitted model (converging scores)
    train_sizes_good = np.array([100, 250, 500, 1000, 2000, 4000])
    train_scores_good = np.array([0.92, 0.90, 0.88, 0.87, 0.86, 0.86])
    val_scores_good = np.array([0.80, 0.82, 0.84, 0.85, 0.86, 0.86])
    
    fig3 = generator.generate(
        train_sizes=train_sizes_good,
        train_scores=train_scores_good,
        val_scores=val_scores_good
    )
    
    fig3.savefig('output/learning_curve_well_fitted.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/learning_curve_well_fitted.png")
    plt.close(fig3)
    
    # Example 4: Custom styling
    custom_style = ChartStyle(
        figure_size=(12, 7),
        font_size=14,
        title_font_size=16,
        line_width=2.5,
        marker_size=8.0,
        grid=True
    )
    custom_styler = ChartStyler(custom_style)
    custom_generator = LearningCurveGenerator(styler=custom_styler)
    
    fig4 = custom_generator.generate(
        train_sizes=train_sizes,
        train_scores=train_scores,
        val_scores=val_scores,
        train_std=train_std,
        val_std=val_std
    )
    
    fig4.savefig('output/learning_curve_custom_style.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/learning_curve_custom_style.png")
    plt.close(fig4)


def main():
    """Run all demos."""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    print("=" * 60)
    print("Validation and Learning Curve Generator Demo")
    print("=" * 60)
    
    demo_validation_curve()
    demo_learning_curve()
    
    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("Check the 'output' directory for generated charts.")
    print("=" * 60)


if __name__ == '__main__':
    main()
