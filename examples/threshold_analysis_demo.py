"""Demo script for ThresholdAnalysisGenerator.

This script demonstrates how to use the ThresholdAnalysisGenerator to create
threshold analysis plots for binary classification models. The plot shows how
Precision, Recall, and F1 Score vary across different classification thresholds,
helping identify the optimal threshold for your use case.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

from src.model_evaluation_viz.generators.threshold_analysis import ThresholdAnalysisGenerator
from src.model_evaluation_viz.core.models import ChartStyle
from src.model_evaluation_viz.styling.chart_styler import ChartStyler
from src.model_evaluation_viz.export.image_exporter import ImageExporter


def main():
    """Run threshold analysis demo."""
    print("=" * 70)
    print("Threshold Analysis Generator Demo")
    print("=" * 70)
    
    # Create output directory
    output_dir = Path("output/threshold_analysis_demo")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate sample binary classification data
    np.random.seed(42)
    n_samples = 200
    
    # Simulate a reasonably good classifier
    # True labels: 60% negative, 40% positive
    y_true = np.random.choice([0, 1], size=n_samples, p=[0.6, 0.4])
    
    # Predicted probabilities: higher for positive class
    y_proba = np.zeros(n_samples)
    for i in range(n_samples):
        if y_true[i] == 1:
            # Positive class: higher probabilities
            y_proba[i] = np.random.beta(5, 2)
        else:
            # Negative class: lower probabilities
            y_proba[i] = np.random.beta(2, 5)
    
    # Clip to [0, 1] range
    y_proba = np.clip(y_proba, 0, 1)
    
    print(f"\nGenerated {n_samples} samples:")
    print(f"  - Positive class: {y_true.sum()} samples ({y_true.sum()/n_samples*100:.1f}%)")
    print(f"  - Negative class: {(1-y_true).sum()} samples ({(1-y_true).sum()/n_samples*100:.1f}%)")
    print(f"  - Probability range: [{y_proba.min():.3f}, {y_proba.max():.3f}]")
    
    # Example 1: Default styling
    print("\n" + "-" * 70)
    print("Example 1: Threshold Analysis with Default Styling")
    print("-" * 70)
    
    generator = ThresholdAnalysisGenerator()
    fig = generator.generate(y_true=y_true, y_proba=y_proba)
    
    # Save the figure
    exporter = ImageExporter(output_dir=str(output_dir))
    filepath = exporter.export(fig, "threshold_analysis_default", format='png')
    print(f"✓ Saved: {filepath}")
    
    plt.close(fig)
    
    # Example 2: Custom styling
    print("\n" + "-" * 70)
    print("Example 2: Threshold Analysis with Custom Styling")
    print("-" * 70)
    
    custom_style = ChartStyle(
        figure_size=(12, 8),
        dpi=300,
        font_size=14,
        title_font_size=16,
        line_width=2.5,
        grid=True,
        grid_alpha=0.4,
        color_palette=['#E63946', '#457B9D', '#2A9D8F']  # Red, Blue, Teal
    )
    
    custom_styler = ChartStyler(custom_style)
    generator_custom = ThresholdAnalysisGenerator(styler=custom_styler)
    fig_custom = generator_custom.generate(y_true=y_true, y_proba=y_proba)
    
    filepath_custom = exporter.export(fig_custom, "threshold_analysis_custom", format='png')
    print(f"✓ Saved: {filepath_custom}")
    
    plt.close(fig_custom)
    
    # Example 3: Imbalanced dataset
    print("\n" + "-" * 70)
    print("Example 3: Threshold Analysis with Imbalanced Dataset")
    print("-" * 70)
    
    # Create highly imbalanced dataset (95% negative, 5% positive)
    y_true_imbalanced = np.random.choice([0, 1], size=n_samples, p=[0.95, 0.05])
    y_proba_imbalanced = np.zeros(n_samples)
    
    for i in range(n_samples):
        if y_true_imbalanced[i] == 1:
            y_proba_imbalanced[i] = np.random.beta(6, 2)
        else:
            y_proba_imbalanced[i] = np.random.beta(2, 6)
    
    y_proba_imbalanced = np.clip(y_proba_imbalanced, 0, 1)
    
    print(f"Imbalanced dataset:")
    print(f"  - Positive class: {y_true_imbalanced.sum()} samples ({y_true_imbalanced.sum()/n_samples*100:.1f}%)")
    print(f"  - Negative class: {(1-y_true_imbalanced).sum()} samples ({(1-y_true_imbalanced).sum()/n_samples*100:.1f}%)")
    
    fig_imbalanced = generator.generate(y_true=y_true_imbalanced, y_proba=y_proba_imbalanced)
    filepath_imbalanced = exporter.export(fig_imbalanced, "threshold_analysis_imbalanced", format='png')
    print(f"✓ Saved: {filepath_imbalanced}")
    
    plt.close(fig_imbalanced)
    
    # Example 4: Export in multiple formats
    print("\n" + "-" * 70)
    print("Example 4: Export in Multiple Formats")
    print("-" * 70)
    
    fig_multi = generator.generate(y_true=y_true, y_proba=y_proba)
    
    formats = ['png', 'svg', 'jpeg']
    for fmt in formats:
        filepath_fmt = exporter.export(fig_multi, f"threshold_analysis_multi", format=fmt)
        print(f"✓ Saved {fmt.upper()}: {filepath_fmt}")
    
    plt.close(fig_multi)
    
    # Summary
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print(f"\nAll charts saved to: {output_dir.absolute()}")
    print("\nKey Insights from Threshold Analysis:")
    print("  • Precision: Higher at higher thresholds (fewer false positives)")
    print("  • Recall: Higher at lower thresholds (fewer false negatives)")
    print("  • F1 Score: Balances precision and recall")
    print("  • Optimal Threshold: Marked with vertical line (maximizes F1)")
    print("\nUse Cases:")
    print("  • Select threshold based on business requirements")
    print("  • Balance false positives vs false negatives")
    print("  • Optimize for specific metric (precision, recall, or F1)")
    print("  • Compare model performance at different operating points")


if __name__ == "__main__":
    main()
