"""Model Comparison Table Demo

Demonstrates the ModelComparisonTableGenerator for comparing multiple models.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.generators.model_comparison import ModelComparisonTableGenerator


def demo_basic_comparison():
    """Demo 1: Basic model comparison with standard metrics."""
    print("\n" + "=" * 70)
    print("  Demo 1: Basic Model Comparison")
    print("=" * 70)
    
    generator = ModelComparisonTableGenerator()
    
    # Define model metrics
    models_data = {
        'Baseline_Model': {
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
        'Model_V3_Final': {
            'Accuracy': 0.8900,
            'Precision': 0.8700,
            'Recall': 0.9100,
            'F1 Score': 0.8900,
            'AUC': 0.9400,
            'Average Precision': 0.9200
        }
    }
    
    fig = generator.generate(models_data=models_data)
    
    output_path = 'output/model_comparison_basic.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: 4 models compared across 6 standard metrics")
    print("  Best values highlighted in green")


def demo_csv_export():
    """Demo 2: Export comparison to CSV."""
    print("\n" + "=" * 70)
    print("  Demo 2: CSV Export")
    print("=" * 70)
    
    generator = ModelComparisonTableGenerator()
    
    models_data = {
        'Model_A': {
            'Accuracy': 0.8500,
            'Precision': 0.8200,
            'Recall': 0.8800,
            'F1 Score': 0.8500,
            'AUC': 0.9000,
            'Average Precision': 0.8700
        },
        'Model_B': {
            'Accuracy': 0.8700,
            'Precision': 0.8500,
            'Recall': 0.8900,
            'F1 Score': 0.8700,
            'AUC': 0.9200,
            'Average Precision': 0.8900
        }
    }
    
    csv_path = 'output/model_comparison.csv'
    generator.export_to_csv(models_data, csv_path)
    
    print(f"✓ Exported: {csv_path}")
    print("  CSV file ready for spreadsheet analysis")


def demo_custom_metrics():
    """Demo 3: Comparison with custom metrics."""
    print("\n" + "=" * 70)
    print("  Demo 3: Custom Metrics")
    print("=" * 70)
    
    generator = ModelComparisonTableGenerator()
    
    # Include custom metrics beyond standard ones
    models_data = {
        'XGBoost': {
            'Accuracy': 0.8700,
            'Precision': 0.8500,
            'Recall': 0.8900,
            'F1 Score': 0.8700,
            'AUC': 0.9200,
            'Average Precision': 0.8900,
            'Specificity': 0.8600,
            'NPV': 0.8800
        },
        'Random_Forest': {
            'Accuracy': 0.8500,
            'Precision': 0.8200,
            'Recall': 0.8800,
            'F1 Score': 0.8500,
            'AUC': 0.9000,
            'Average Precision': 0.8700,
            'Specificity': 0.8400,
            'NPV': 0.8600
        },
        'Logistic_Regression': {
            'Accuracy': 0.8200,
            'Precision': 0.7900,
            'Recall': 0.8500,
            'F1 Score': 0.8200,
            'AUC': 0.8800,
            'Average Precision': 0.8400,
            'Specificity': 0.8100,
            'NPV': 0.8300
        }
    }
    
    fig = generator.generate(models_data=models_data)
    
    output_path = 'output/model_comparison_custom.png'
    fig.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Generated: {output_path}")
    print("  Shows: 3 models with 8 metrics (including custom ones)")


def main():
    """Run all model comparison demos."""
    import os
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    print("\n" + "=" * 70)
    print("  MODEL COMPARISON TABLE DEMO")
    print("=" * 70)
    
    demo_basic_comparison()
    demo_csv_export()
    demo_custom_metrics()
    
    print("\n" + "=" * 70)
    print("  ✅ ALL DEMOS COMPLETE!")
    print("=" * 70)
    print("\n📊 Generated files:")
    print("  • output/model_comparison_basic.png")
    print("  • output/model_comparison_custom.png")
    print("  • output/model_comparison.csv")
    print("\n")


if __name__ == '__main__':
    main()
