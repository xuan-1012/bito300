"""ChartGenerator API Demo

Demonstrates the main ChartGenerator API for unified chart generation.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.core.chart_generator import ChartGenerator
from src.model_evaluation_viz.core.models import ChartStyle


def generate_sample_data():
    """Generate realistic sample data."""
    np.random.seed(42)
    
    n_samples = 200
    y_true = np.random.randint(0, 2, n_samples)
    y_proba = np.random.rand(n_samples) * 0.5 + y_true * 0.4
    y_proba = np.clip(y_proba, 0, 1)
    y_pred = (y_proba >= 0.5).astype(int)
    
    return y_true, y_pred, y_proba


def demo_unified_api():
    """Demo: Using the unified ChartGenerator API."""
    print("\n" + "=" * 70)
    print("  ChartGenerator API Demo")
    print("=" * 70)
    
    # Create generator with default settings
    generator = ChartGenerator(output_dir='output/api_demo')
    
    # Generate sample data
    y_true, y_pred, y_proba = generate_sample_data()
    
    print("\n📊 Generating charts using unified API...")
    
    # 1. Confusion Matrix
    print("\n1. Generating confusion matrix...")
    fig = generator.generate_confusion_matrix(
        y_true=y_true,
        y_pred=y_pred,
        class_labels=['Normal', 'Suspicious'],
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 2. ROC Curve
    print("2. Generating ROC curve...")
    fig = generator.generate_roc_curve(
        y_true=y_true,
        y_proba=y_proba,
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 3. Precision-Recall Curve
    print("3. Generating precision-recall curve...")
    fig = generator.generate_precision_recall_curve(
        y_true=y_true,
        y_proba=y_proba,
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 4. Threshold Analysis
    print("4. Generating threshold analysis...")
    fig = generator.generate_threshold_analysis(
        y_true=y_true,
        y_proba=y_proba,
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 5. Lift Curve
    print("5. Generating lift curve...")
    fig = generator.generate_lift_curve(
        y_true=y_true,
        y_proba=y_proba,
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 6. Validation Curve
    print("6. Generating validation curve...")
    param_values = np.array([0.001, 0.01, 0.1, 1.0, 10.0, 100.0])
    train_scores = np.array([0.95, 0.93, 0.90, 0.88, 0.85, 0.82])
    val_scores = np.array([0.70, 0.78, 0.84, 0.86, 0.85, 0.82])
    
    fig = generator.generate_validation_curve(
        param_values=param_values,
        train_scores=train_scores,
        val_scores=val_scores,
        param_name='C (Regularization)',
        log_scale=True,
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 7. Learning Curve
    print("7. Generating learning curve...")
    train_sizes = np.array([50, 100, 200, 500, 1000, 2000])
    train_scores = np.array([0.98, 0.95, 0.92, 0.90, 0.88, 0.87])
    val_scores = np.array([0.65, 0.72, 0.78, 0.82, 0.84, 0.85])
    
    fig = generator.generate_learning_curve(
        train_sizes=train_sizes,
        train_scores=train_scores,
        val_scores=val_scores,
        save=True
    )
    print("   ✓ Saved to output/api_demo/")
    
    # 8. Model Comparison
    print("8. Generating model comparison table...")
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
        'Final_Model': {
            'Accuracy': 0.8900,
            'Precision': 0.8700,
            'Recall': 0.9100,
            'F1 Score': 0.8900,
            'AUC': 0.9400,
            'Average Precision': 0.9200
        }
    }
    
    fig = generator.generate_model_comparison(
        models_data=models_data,
        save=True,
        export_csv=True
    )
    print("   ✓ Saved PNG and CSV to output/api_demo/")
    
    print("\n" + "=" * 70)
    print("  ✅ All charts generated successfully!")
    print("=" * 70)
    print("\n📁 Output directory: output/api_demo/")
    print("   All charts saved with auto-generated filenames")


def demo_custom_styling():
    """Demo: Using custom styling with the API."""
    print("\n" + "=" * 70)
    print("  Custom Styling Demo")
    print("=" * 70)
    
    # Create custom style
    custom_style = ChartStyle(
        figure_size=(12, 8),
        dpi=300,
        font_size=14,
        title_font_size=18,
        line_width=2.5,
        grid=True,
        font_family='sans-serif'
    )
    
    # Create generator with custom style
    generator = ChartGenerator(
        output_dir='output/api_demo_custom',
        style=custom_style
    )
    
    # Generate sample data
    y_true, y_pred, y_proba = generate_sample_data()
    
    print("\n📊 Generating charts with custom styling...")
    
    # Generate ROC curve with custom style
    fig = generator.generate_roc_curve(
        y_true=y_true,
        y_proba=y_proba,
        save=True,
        filename='custom_styled_roc.png'
    )
    print("   ✓ Custom styled ROC curve saved")
    
    # Generate confusion matrix with custom style
    fig = generator.generate_confusion_matrix(
        y_true=y_true,
        y_pred=y_pred,
        class_labels=['Normal', 'Suspicious'],
        save=True,
        filename='custom_styled_confusion.png'
    )
    print("   ✓ Custom styled confusion matrix saved")
    
    print("\n" + "=" * 70)
    print("  ✅ Custom styling applied successfully!")
    print("=" * 70)
    print("\n📁 Output directory: output/api_demo_custom/")


def main():
    """Run all API demos."""
    print("\n" + "=" * 70)
    print("  CHARTGENERATOR API DEMONSTRATION")
    print("  Unified Interface for All Chart Types")
    print("=" * 70)
    
    demo_unified_api()
    demo_custom_styling()
    
    print("\n" + "=" * 70)
    print("  ✅ ALL DEMOS COMPLETE!")
    print("=" * 70)
    print("\n✨ Key Features Demonstrated:")
    print("  • Unified API for all chart types")
    print("  • Automatic input validation")
    print("  • Consistent styling across charts")
    print("  • Auto-generated filenames with timestamps")
    print("  • Custom styling support")
    print("  • CSV export for model comparison")
    print("\n")


if __name__ == '__main__':
    main()
