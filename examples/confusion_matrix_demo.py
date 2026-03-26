"""Demo script for confusion matrix generator.

This script demonstrates how to use the ConfusionMatrixGenerator class
to create publication-quality confusion matrix visualizations for
classification model evaluation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for saving
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.generators.confusion_matrix import ConfusionMatrixGenerator
from src.model_evaluation_viz.core.models import ChartStyle
from src.model_evaluation_viz.styling.chart_styler import ChartStyler


def demo_binary_classification():
    """Demonstrate confusion matrix for binary classification."""
    print("Generating binary classification confusion matrix examples...")
    
    # Example 1: Basic binary classification
    np.random.seed(42)
    y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0])
    y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0])
    
    generator = ConfusionMatrixGenerator()
    
    # Generate with default numeric labels
    fig = generator.generate(
        y_true=y_true,
        y_pred=y_pred
    )
    
    fig.savefig('output/confusion_matrix_binary_default.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_binary_default.png")
    plt.close(fig)
    
    # Example 2: Binary classification with custom labels
    fig2 = generator.generate(
        y_true=y_true,
        y_pred=y_pred,
        class_labels=['Negative', 'Positive']
    )
    
    fig2.savefig('output/confusion_matrix_binary_labeled.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_binary_labeled.png")
    plt.close(fig2)
    
    # Example 3: High accuracy classifier
    y_true_good = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0])
    y_pred_good = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0])  # Perfect predictions
    
    fig3 = generator.generate(
        y_true=y_true_good,
        y_pred=y_pred_good,
        class_labels=['Normal', 'Fraud']
    )
    
    fig3.savefig('output/confusion_matrix_high_accuracy.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_high_accuracy.png")
    plt.close(fig3)


def demo_multiclass_classification():
    """Demonstrate confusion matrix for multi-class classification."""
    print("\nGenerating multi-class classification confusion matrix examples...")
    
    # Example 1: 3-class classification
    np.random.seed(42)
    y_true = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1, 2, 0, 1])
    y_pred = np.array([0, 1, 2, 1, 1, 2, 0, 2, 2, 0, 1, 1, 0, 1, 2, 1, 1, 2, 0, 1])
    
    generator = ConfusionMatrixGenerator()
    
    fig = generator.generate(
        y_true=y_true,
        y_pred=y_pred,
        class_labels=['Class A', 'Class B', 'Class C']
    )
    
    fig.savefig('output/confusion_matrix_3class.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_3class.png")
    plt.close(fig)
    
    # Example 2: 4-class classification with descriptive labels
    y_true_4 = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
    y_pred_4 = np.array([0, 1, 2, 3, 1, 1, 2, 3, 0, 2, 2, 3, 0, 1, 3, 3, 0, 1, 2, 2])
    
    fig2 = generator.generate(
        y_true=y_true_4,
        y_pred=y_pred_4,
        class_labels=['Low Risk', 'Medium Risk', 'High Risk', 'Critical']
    )
    
    fig2.savefig('output/confusion_matrix_4class_risk.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_4class_risk.png")
    plt.close(fig2)


def demo_custom_styling():
    """Demonstrate confusion matrix with custom styling."""
    print("\nGenerating confusion matrix with custom styling...")
    
    # Create sample data
    np.random.seed(42)
    y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0])
    y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0])
    
    # Custom style with larger figure and fonts
    custom_style = ChartStyle(
        figure_size=(10, 8),
        font_size=14,
        title_font_size=18,
        grid=False  # No grid for heatmaps
    )
    custom_styler = ChartStyler(custom_style)
    custom_generator = ConfusionMatrixGenerator(styler=custom_styler)
    
    fig = custom_generator.generate(
        y_true=y_true,
        y_pred=y_pred,
        class_labels=['Benign', 'Malignant']
    )
    
    fig.savefig('output/confusion_matrix_custom_style.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_custom_style.png")
    plt.close(fig)


def demo_realistic_scenarios():
    """Demonstrate confusion matrices for realistic ML scenarios."""
    print("\nGenerating confusion matrices for realistic scenarios...")
    
    generator = ConfusionMatrixGenerator()
    
    # Scenario 1: Imbalanced dataset (fraud detection)
    # 95% negative, 5% positive
    np.random.seed(42)
    n_samples = 100
    y_true_imb = np.concatenate([
        np.zeros(95),
        np.ones(5)
    ])
    # Model catches 3 out of 5 frauds, but has 2 false positives
    y_pred_imb = y_true_imb.copy()
    y_pred_imb[95] = 0  # Miss 1 fraud
    y_pred_imb[96] = 0  # Miss 1 fraud
    y_pred_imb[10] = 1  # False positive
    y_pred_imb[20] = 1  # False positive
    
    fig1 = generator.generate(
        y_true=y_true_imb,
        y_pred=y_pred_imb,
        class_labels=['Legitimate', 'Fraud']
    )
    
    fig1.savefig('output/confusion_matrix_fraud_detection.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_fraud_detection.png")
    plt.close(fig1)
    
    # Scenario 2: Medical diagnosis (high recall needed)
    np.random.seed(42)
    y_true_med = np.array([0]*40 + [1]*10)
    y_pred_med = y_true_med.copy()
    # High sensitivity: catch all diseases but some false positives
    y_pred_med[5] = 1   # False positive
    y_pred_med[15] = 1  # False positive
    y_pred_med[25] = 1  # False positive
    # No false negatives (high recall)
    
    fig2 = generator.generate(
        y_true=y_true_med,
        y_pred=y_pred_med,
        class_labels=['Healthy', 'Disease']
    )
    
    fig2.savefig('output/confusion_matrix_medical_diagnosis.png', dpi=300, bbox_inches='tight')
    print("✓ Saved: output/confusion_matrix_medical_diagnosis.png")
    plt.close(fig2)


def main():
    """Run all demos."""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    print("=" * 60)
    print("Confusion Matrix Generator Demo")
    print("=" * 60)
    
    demo_binary_classification()
    demo_multiclass_classification()
    demo_custom_styling()
    demo_realistic_scenarios()
    
    print("\n" + "=" * 60)
    print("✅ All demos completed successfully!")
    print("Check the 'output' directory for generated charts.")
    print("=" * 60)


if __name__ == '__main__':
    main()

