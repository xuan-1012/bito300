"""Batch Generation Demo

Demonstrates the batch_generate() method for generating all charts at once.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.model_evaluation_viz.core.chart_generator import ChartGenerator


def generate_sample_data():
    """Generate realistic sample data."""
    np.random.seed(42)
    
    n_samples = 200
    y_true = np.random.randint(0, 2, n_samples)
    y_proba = np.random.rand(n_samples) * 0.5 + y_true * 0.4
    y_proba = np.clip(y_proba, 0, 1)
    y_pred = (y_proba >= 0.5).astype(int)
    
    return y_true, y_pred, y_proba


def demo_basic_batch():
    """Demo 1: Basic batch generation."""
    print("\n" + "=" * 70)
    print("  Demo 1: Basic Batch Generation")
    print("=" * 70)
    
    # Create generator
    generator = ChartGenerator(output_dir='output/batch_demo')
    
    # Generate sample data
    y_true, y_pred, y_proba = generate_sample_data()
    
    print("\n📊 Generating all charts in batch mode...")
    
    # Generate all charts at once
    result = generator.batch_generate(
        y_true=y_true,
        y_pred=y_pred,
        y_proba=y_proba,
        class_labels=['Normal', 'Suspicious']
    )
    
    # Print summary
    print("\n" + result.get_summary())
    
    print("\n✅ Batch generation complete!")
    print(f"   Generated {len(result.generated_charts)} charts")
    if result.failed_charts:
        print(f"   Failed {len(result.failed_charts)} charts")


def demo_batch_with_prefix():
    """Demo 2: Batch generation with filename prefix."""
    print("\n" + "=" * 70)
    print("  Demo 2: Batch Generation with Prefix")
    print("=" * 70)
    
    # Create generator
    generator = ChartGenerator(output_dir='output/batch_demo_prefix')
    
    # Generate sample data
    y_true, y_pred, y_proba = generate_sample_data()
    
    print("\n📊 Generating charts with 'model_v2_' prefix...")
    
    # Generate with prefix
    result = generator.batch_generate(
        y_true=y_true,
        y_pred=y_pred,
        y_proba=y_proba,
        class_labels=['Normal', 'Suspicious'],
        prefix='model_v2_'
    )
    
    # Print summary
    print("\n" + result.get_summary())
    
    print("\n✅ Batch generation with prefix complete!")


def demo_multiple_models():
    """Demo 3: Generate charts for multiple model versions."""
    print("\n" + "=" * 70)
    print("  Demo 3: Multiple Model Versions")
    print("=" * 70)
    
    # Create generator
    generator = ChartGenerator(output_dir='output/batch_demo_multi')
    
    print("\n📊 Generating charts for 3 model versions...")
    
    # Simulate 3 different models
    np.random.seed(42)
    for i in range(1, 4):
        print(f"\n  Model V{i}:")
        
        # Generate slightly different data for each model
        n_samples = 200
        y_true = np.random.randint(0, 2, n_samples)
        # Each model has slightly better performance
        y_proba = np.random.rand(n_samples) * 0.5 + y_true * (0.3 + i * 0.05)
        y_proba = np.clip(y_proba, 0, 1)
        y_pred = (y_proba >= 0.5).astype(int)
        
        # Generate charts with model-specific prefix
        result = generator.batch_generate(
            y_true=y_true,
            y_pred=y_pred,
            y_proba=y_proba,
            class_labels=['Normal', 'Suspicious'],
            prefix=f'model_v{i}_'
        )
        
        print(f"    ✓ Generated {len(result.generated_charts)} charts")
    
    print("\n✅ All model versions processed!")
    print("   Check output/batch_demo_multi/ for all charts")


def demo_error_resilience():
    """Demo 4: Error resilience in batch generation."""
    print("\n" + "=" * 70)
    print("  Demo 4: Error Resilience")
    print("=" * 70)
    
    # Create generator
    generator = ChartGenerator(output_dir='output/batch_demo_errors')
    
    # Generate valid data
    y_true, y_pred, y_proba = generate_sample_data()
    
    print("\n📊 Testing batch generation with valid data...")
    
    # This should succeed for all charts
    result = generator.batch_generate(
        y_true=y_true,
        y_pred=y_pred,
        y_proba=y_proba
    )
    
    print(f"\n✅ Successfully generated {len(result.generated_charts)} charts")
    if result.failed_charts:
        print(f"⚠️  Failed charts: {len(result.failed_charts)}")
        for chart_type, error in result.failed_charts.items():
            print(f"    - {chart_type}: {error}")
    else:
        print("   No errors encountered!")


def main():
    """Run all batch generation demos."""
    print("\n" + "=" * 70)
    print("  BATCH GENERATION DEMONSTRATION")
    print("  Generate All Charts at Once")
    print("=" * 70)
    
    demo_basic_batch()
    demo_batch_with_prefix()
    demo_multiple_models()
    demo_error_resilience()
    
    print("\n" + "=" * 70)
    print("  ✅ ALL DEMOS COMPLETE!")
    print("=" * 70)
    print("\n✨ Key Features Demonstrated:")
    print("  • Generate all charts with single method call")
    print("  • Consistent naming with timestamps")
    print("  • Custom filename prefixes for organization")
    print("  • Error resilience - continues on failure")
    print("  • Automatic summary report generation")
    print("  • Batch processing for multiple models")
    print("\n📁 Output directories:")
    print("  • output/batch_demo/")
    print("  • output/batch_demo_prefix/")
    print("  • output/batch_demo_multi/")
    print("  • output/batch_demo_errors/")
    print("\n")


if __name__ == '__main__':
    main()
