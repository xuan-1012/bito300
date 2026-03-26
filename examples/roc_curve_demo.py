"""Demo script for ROC curve generation.

This script demonstrates how to use the ROCCurveGenerator to create
ROC curves for binary classification model evaluation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.generators.roc_curve import ROCCurveGenerator
from src.model_evaluation_viz.core.models import ChartStyle


def main():
    """Generate example ROC curves."""
    
    # Create output directory
    output_dir = Path("output/roc_curves")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Example 1: Perfect classifier
    print("Generating ROC curve for perfect classifier...")
    y_true_perfect = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    y_proba_perfect = np.array([0.1, 0.2, 0.15, 0.05, 0.9, 0.95, 0.85, 0.92])
    
    generator = ROCCurveGenerator()
    fig = generator.generate(y_true=y_true_perfect, y_proba=y_proba_perfect)
    fig.savefig(output_dir / "roc_curve_perfect.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to {output_dir / 'roc_curve_perfect.png'}")
    
    # Example 2: Good classifier
    print("\nGenerating ROC curve for good classifier...")
    np.random.seed(42)
    n_samples = 200
    y_true_good = np.random.randint(0, 2, n_samples)
    # Add signal to probabilities
    y_proba_good = np.random.rand(n_samples) * 0.5 + y_true_good * 0.4
    y_proba_good = np.clip(y_proba_good, 0, 1)
    
    fig = generator.generate(y_true=y_true_good, y_proba=y_proba_good)
    fig.savefig(output_dir / "roc_curve_good.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to {output_dir / 'roc_curve_good.png'}")
    
    # Example 3: Random classifier
    print("\nGenerating ROC curve for random classifier...")
    y_true_random = np.random.randint(0, 2, n_samples)
    y_proba_random = np.random.rand(n_samples)
    
    fig = generator.generate(y_true=y_true_random, y_proba=y_proba_random)
    fig.savefig(output_dir / "roc_curve_random.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to {output_dir / 'roc_curve_random.png'}")
    
    # Example 4: Custom styling
    print("\nGenerating ROC curve with custom styling...")
    custom_style = ChartStyle(
        figure_size=(8, 8),
        font_size=14,
        title_font_size=16,
        line_width=3.0,
        grid=True
    )
    from src.model_evaluation_viz.styling.chart_styler import ChartStyler
    custom_styler = ChartStyler(custom_style)
    generator_custom = ROCCurveGenerator(styler=custom_styler)
    
    fig = generator_custom.generate(y_true=y_true_good, y_proba=y_proba_good)
    fig.savefig(output_dir / "roc_curve_custom_style.png", dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved to {output_dir / 'roc_curve_custom_style.png'}")
    
    print("\n✓ All ROC curves generated successfully!")
    print(f"  Output directory: {output_dir.absolute()}")


if __name__ == "__main__":
    main()
