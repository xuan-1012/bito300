"""Demo script for ImageExporter functionality.

This script demonstrates how to use the ImageExporter class to save
matplotlib figures in various formats with different options.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from src.model_evaluation_viz.export.image_exporter import ImageExporter


def create_sample_chart():
    """Create a sample chart for demonstration."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # Plot data
    ax.plot(x, y1, label='sin(x)', linewidth=2)
    ax.plot(x, y2, label='cos(x)', linewidth=2)
    
    # Add labels and title
    ax.set_xlabel('X Values', fontsize=12)
    ax.set_ylabel('Y Values', fontsize=12)
    ax.set_title('Sample Chart: Sine and Cosine Functions', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    return fig


def main():
    """Run ImageExporter demonstrations."""
    print("ImageExporter Demo")
    print("=" * 60)
    
    # Create output directory
    output_dir = "./output/image_exporter_demo"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Initialize exporter
    exporter = ImageExporter(output_dir=output_dir)
    print(f"\n1. Initialized ImageExporter with output directory: {output_dir}")
    
    # Create sample chart
    fig = create_sample_chart()
    print("\n2. Created sample chart")
    
    # Demo 1: Export as PNG with default settings
    print("\n3. Exporting as PNG (300 DPI)...")
    png_path = exporter.export(fig, "demo_chart.png", format='png', dpi=300)
    print(f"   Saved to: {png_path}")
    
    # Demo 2: Export as transparent PNG
    print("\n4. Exporting as transparent PNG...")
    transparent_path = exporter.export(
        fig, "demo_chart_transparent.png", 
        format='png', dpi=300, transparent=True
    )
    print(f"   Saved to: {transparent_path}")
    
    # Demo 3: Export as SVG (vector format)
    print("\n5. Exporting as SVG (vector format)...")
    svg_path = exporter.export(fig, "demo_chart.svg", format='svg')
    print(f"   Saved to: {svg_path}")
    
    # Demo 4: Export as JPEG
    print("\n6. Exporting as JPEG...")
    jpeg_path = exporter.export(fig, "demo_chart.jpeg", format='jpeg', dpi=300)
    print(f"   Saved to: {jpeg_path}")
    
    # Demo 5: Export with custom dimensions
    print("\n7. Exporting with custom dimensions (12x8 inches)...")
    custom_path = exporter.export(
        fig, "demo_chart_custom_size.png",
        format='png', dpi=300,
        width=12.0, height=8.0
    )
    print(f"   Saved to: {custom_path}")
    
    # Demo 6: Export to multiple formats at once
    print("\n8. Exporting to multiple formats...")
    multi_paths = exporter.export_multiple_formats(
        fig, "demo_chart_multi",
        formats=['png', 'svg', 'jpeg'],
        dpi=300
    )
    print(f"   Saved {len(multi_paths)} files:")
    for path in multi_paths:
        print(f"   - {path}")
    
    # Demo 7: Generate filename with timestamp
    print("\n9. Generating filename with timestamp...")
    filename = exporter.generate_filename('roc_curve', timestamp=True)
    print(f"   Generated filename: {filename}")
    
    # Demo 8: Generate filename without timestamp
    print("\n10. Generating filename without timestamp...")
    filename_no_ts = exporter.generate_filename('confusion_matrix', timestamp=False)
    print(f"    Generated filename: {filename_no_ts}")
    
    # Clean up
    plt.close(fig)
    
    print("\n" + "=" * 60)
    print("Demo complete! Check the output directory for generated files.")
    print(f"Output directory: {Path(output_dir).absolute()}")


if __name__ == "__main__":
    main()
