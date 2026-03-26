"""Complete Model Evaluation Visualization Demo

This comprehensive demo showcases all implemented chart generators
for model evaluation and risk scoring visualization.

Generated Charts:
1. Validation Curves (hyperparameter tuning)
2. Learning Curves (training set size analysis)
3. Confusion Matrix (classification performance)
4. ROC Curve (TPR vs FPR with AUC)
5. Precision-Recall Curve (precision vs recall with AP)
6. Threshold Analysis (optimal threshold selection)
7. Lift Curve (ranking quality assessment)
8. Model Comparison Table (multi-model comparison)

All charts are publication-quality with 300 DPI resolution.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.generators.validation_curve import ValidationCurveGenerator
from src.model_evaluation_viz.generators.learning_curve import LearningCurveGenerator
from src.model_evaluation_viz.generators.confusion_matrix import ConfusionMatrixGenerator
from src.model_evaluation_viz.generators.roc_curve import ROCCurveGenerator
from src.model_evaluation_viz.generators.precision_recall import PrecisionRecallCurveGenerator
from src.model_evaluation_viz.generators.threshold_analysis import ThresholdAnalysisGenerator
from src.model_evaluation_viz.generators.lift_curve import LiftCurveGenerator
from src.model_evaluation_viz.generators.model_comparison import ModelComparisonTableGenerator
from src.model_evaluation_viz.core.models import ChartStyle
from src.model_evaluation_viz.styling.chart_styler import ChartStyler


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def generate_sample_data():
    """Generate realistic sample data for demonstrations."""
    np.random.seed(42)
    
    # Binary classification data (200 samples)
    n_samples = 200
    y_true = np.random.randint(0, 2, n_samples)
    
    # Good classifier: probabilities correlated with true labels
    y_proba = np.random.rand(n_samples) * 0.5 + y_true * 0.4
    y_proba = np.clip(y_proba, 0, 1)
    
    # Predictions based on 0.5 threshold
    y_pred = (y_proba >= 0.5).astype(int)
    
    return y_true, y_pred, y_proba


def demo_validation_curves():
    """Demo 1: Validation Curves for Hyperparameter Tuning."""
    print_section("1. Validation Curves - Hyperparameter Tuning")
    
    generator = ValidationCurveGenerator()
    
    # Example: Regularization parameter C
    param_values = np.array([0.001, 0.01, 0.1, 1.0, 10.0, 100.0])
    train_scores = np.array([0.95, 0.93, 0.90, 0.88, 0.85, 0.82])
    val_scores = np.array([0.70, 0.78, 0.84, 0.86, 0.85, 0.82])
    
    fig = generator.generate(
        param_values=param_values,
        train_scores=train_scores,
        val_scores=val_scores,
        param_name='C (Regularization Parameter)',
        log_scale=True
    )
    
    output_path = 'output/demo_validation_curve.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: Training vs validation scores across hyperparameter values")
    print("  Use case: Identify optimal hyperparameter and detect overfitting")


def demo_learning_curves():
    """Demo 2: Learning Curves for Training Set Size Analysis."""
    print_section("2. Learning Curves - Training Set Size Analysis")
    
    generator = LearningCurveGenerator()
    
    # Training set sizes and corresponding scores
    train_sizes = np.array([50, 100, 200, 500, 1000, 2000, 5000])
    train_scores = np.array([0.98, 0.95, 0.92, 0.90, 0.88, 0.87, 0.86])
    val_scores = np.array([0.65, 0.72, 0.78, 0.82, 0.84, 0.85, 0.86])
    train_std = np.array([0.03, 0.025, 0.02, 0.015, 0.01, 0.008, 0.005])
    val_std = np.array([0.08, 0.06, 0.05, 0.04, 0.03, 0.025, 0.02])
    
    fig = generator.generate(
        train_sizes=train_sizes,
        train_scores=train_scores,
        val_scores=val_scores,
        train_std=train_std,
        val_std=val_std
    )
    
    output_path = 'output/demo_learning_curve.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: Training vs validation scores as training data increases")
    print("  Use case: Determine if more data would improve performance")


def demo_confusion_matrix(y_true, y_pred):
    """Demo 3: Confusion Matrix for Classification Performance."""
    print_section("3. Confusion Matrix - Classification Performance")
    
    generator = ConfusionMatrixGenerator()
    
    fig = generator.generate(
        y_true=y_true,
        y_pred=y_pred,
        class_labels=['Normal', 'Suspicious']
    )
    
    output_path = 'output/demo_confusion_matrix.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: TP, FP, TN, FN counts in heatmap format")
    print("  Use case: Understand classification errors and accuracy")


def demo_roc_curve(y_true, y_proba):
    """Demo 4: ROC Curve with AUC Score."""
    print_section("4. ROC Curve - TPR vs FPR with AUC")
    
    generator = ROCCurveGenerator()
    
    fig = generator.generate(
        y_true=y_true,
        y_proba=y_proba
    )
    
    output_path = 'output/demo_roc_curve.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: True Positive Rate vs False Positive Rate")
    print("  Use case: Evaluate classifier performance across all thresholds")


def demo_precision_recall_curve(y_true, y_proba):
    """Demo 5: Precision-Recall Curve with Average Precision."""
    print_section("5. Precision-Recall Curve - Precision vs Recall")
    
    generator = PrecisionRecallCurveGenerator()
    
    fig = generator.generate(
        y_true=y_true,
        y_proba=y_proba
    )
    
    output_path = 'output/demo_pr_curve.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: Precision vs Recall with Average Precision score")
    print("  Use case: Evaluate performance on imbalanced datasets")


def demo_threshold_analysis(y_true, y_proba):
    """Demo 6: Threshold Analysis for Optimal Threshold Selection."""
    print_section("6. Threshold Analysis - Optimal Threshold Selection")
    
    generator = ThresholdAnalysisGenerator()
    
    fig = generator.generate(
        y_true=y_true,
        y_proba=y_proba
    )
    
    output_path = 'output/demo_threshold_analysis.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: Precision, Recall, F1 across different thresholds")
    print("  Use case: Select optimal classification threshold")


def demo_lift_curve(y_true, y_proba):
    """Demo 7: Lift Curve for Ranking Quality Assessment."""
    print_section("7. Lift Curve - Ranking Quality Assessment")
    
    generator = LiftCurveGenerator()
    
    fig = generator.generate(
        y_true=y_true,
        y_proba=y_proba
    )
    
    output_path = 'output/demo_lift_curve.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: Cumulative gains and lift at different percentiles")
    print("  Use case: Evaluate ranking quality for risk scoring")


def demo_custom_styling():
    """Demo 8: Custom Styling Example."""
    print_section("8. Custom Styling - Professional Appearance")
    
    # Create custom style
    custom_style = ChartStyle(
        figure_size=(12, 8),
        dpi=300,
        font_size=14,
        title_font_size=18,
        line_width=2.5,
        marker_size=8.0,
        grid=True,
        font_family='sans-serif',
        text_color='#333333'
    )
    
    custom_styler = ChartStyler(custom_style)
    generator = ValidationCurveGenerator(styler=custom_styler)
    
    # Generate with custom styling
    param_values = np.array([1, 2, 3, 5, 7, 10, 15, 20])
    train_scores = np.array([0.75, 0.82, 0.88, 0.92, 0.95, 0.97, 0.98, 0.99])
    val_scores = np.array([0.74, 0.80, 0.85, 0.87, 0.86, 0.84, 0.81, 0.78])
    
    fig = generator.generate(
        param_values=param_values,
        train_scores=train_scores,
        val_scores=val_scores,
        param_name='Max Depth',
        log_scale=False
    )
    
    output_path = 'output/demo_custom_styling.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: Custom figure size, fonts, colors, and styling")
    print("  Use case: Match corporate branding or presentation requirements")


def demo_model_comparison():
    """Demo 9: Model Comparison Table."""
    print_section("9. Model Comparison Table - Multi-Model Evaluation")
    
    generator = ModelComparisonTableGenerator()
    
    # Define model metrics for comparison
    models_data = {
        'Baseline': {
            'Accuracy': 0.8200,
            'Precision': 0.7800,
            'Recall': 0.8500,
            'F1 Score': 0.8100,
            'AUC': 0.8700,
            'Average Precision': 0.8300
        },
        'Model_V1': {
            'Accuracy': 0.8500,
            'Precision': 0.8200,
            'Recall': 0.8800,
            'F1 Score': 0.8500,
            'AUC': 0.9000,
            'Average Precision': 0.8700
        },
        'Model_V2': {
            'Accuracy': 0.8700,
            'Precision': 0.8500,
            'Recall': 0.8900,
            'F1 Score': 0.8700,
            'AUC': 0.9200,
            'Average Precision': 0.8900
        },
        'Final_Model': {
            'Accuracy': 0.8900,
            'Precision': 0.8700,
            'Recall': 0.9100,
            'F1 Score': 0.8900,
            'AUC': 0.9400,
            'Average Precision': 0.9200
        }
    }
    
    fig = generator.generate(models_data=models_data)
    
    output_path = 'output/demo_model_comparison.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: 4 models compared across 6 metrics")
    print("  Use case: Select best model version for deployment")


def print_summary():
    """Print summary of generated charts."""
    print_section("Summary - All Charts Generated Successfully")
    
    charts = [
        ("Validation Curve", "output/demo_validation_curve.png"),
        ("Learning Curve", "output/demo_learning_curve.png"),
        ("Confusion Matrix", "output/demo_confusion_matrix.png"),
        ("ROC Curve", "output/demo_roc_curve.png"),
        ("Precision-Recall Curve", "output/demo_pr_curve.png"),
        ("Threshold Analysis", "output/demo_threshold_analysis.png"),
        ("Lift Curve", "output/demo_lift_curve.png"),
        ("Custom Styling Example", "output/demo_custom_styling.png"),
        ("Model Comparison Table", "output/demo_model_comparison.png"),
    ]
    
    print("\n📊 Generated Charts:")
    for i, (name, path) in enumerate(charts, 1):
        print(f"  {i}. {name:30s} → {path}")
    
    print("\n✨ All charts are:")
    print("  • Publication-quality (300 DPI)")
    print("  • Ready for presentations and reports")
    print("  • Professionally styled with clear labels")
    print("  • Suitable for academic papers and business reports")
    
    print("\n📁 Output directory: output/")
    print("   Open the PNG files to view the generated visualizations.")


def main():
    """Run complete visualization demo."""
    import os
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    print("\n" + "=" * 70)
    print("  COMPLETE MODEL EVALUATION VISUALIZATION DEMO")
    print("  Showcasing All Implemented Chart Generators")
    print("=" * 70)
    
    # Generate sample data
    print("\n📊 Generating sample data for demonstrations...")
    y_true, y_pred, y_proba = generate_sample_data()
    print(f"   Created {len(y_true)} samples for binary classification")
    
    # Run all demos
    demo_validation_curves()
    demo_learning_curves()
    demo_confusion_matrix(y_true, y_pred)
    demo_roc_curve(y_true, y_proba)
    demo_precision_recall_curve(y_true, y_proba)
    demo_threshold_analysis(y_true, y_proba)
    demo_lift_curve(y_true, y_proba)
    demo_custom_styling()
    demo_model_comparison()
    
    # Print summary
    print_summary()
    
    print("\n" + "=" * 70)
    print("  ✅ DEMO COMPLETE!")
    print("=" * 70 + "\n")


if __name__ == '__main__':
    main()
