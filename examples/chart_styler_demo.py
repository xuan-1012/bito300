"""Demo script for ChartStyler and color palette management.

This script demonstrates how to use the ChartStyler class to apply
consistent styling to matplotlib charts.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np

from model_evaluation_viz.styling.chart_styler import ChartStyler
from model_evaluation_viz.styling.color_palettes import DEFAULT_PALETTE
from model_evaluation_viz.core.models import ChartStyle


def demo_default_styling():
    """Demonstrate default styling with colorblind-accessible palette."""
    print("Demo 1: Default Styling")
    print("=" * 50)
    
    # Create styler with default settings
    styler = ChartStyler()
    
    # Create a simple chart
    fig, ax = plt.subplots(figsize=styler.style.figure_size, dpi=styler.style.dpi)
    
    # Apply base styling
    styler.apply_base_style(ax)
    
    # Generate sample data
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    y3 = np.sin(x) * np.cos(x)
    
    # Plot with styled colors
    ax.plot(x, y1, color=styler.get_color(0), linewidth=styler.style.line_width, label='sin(x)')
    ax.plot(x, y2, color=styler.get_color(1), linewidth=styler.style.line_width, label='cos(x)')
    ax.plot(x, y3, color=styler.get_color(2), linewidth=styler.style.line_width, label='sin(x)*cos(x)')
    
    # Format labels
    styler.format_axis_labels(ax, 'X Values', 'Y Values', 'Trigonometric Functions')
    
    # Add legend
    ax.legend(fontsize=styler.style.font_size)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('output/demo_default_styling.png', dpi=styler.style.dpi, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Chart saved to output/demo_default_styling.png")
    print(f"  - Font size: {styler.style.font_size}")
    print(f"  - Title font size: {styler.style.title_font_size}")
    print(f"  - Line width: {styler.style.line_width}")
    print(f"  - Grid enabled: {styler.style.grid}")
    print(f"  - Color palette: {len(styler.style.color_palette)} colors")
    print()


def demo_custom_styling():
    """Demonstrate custom styling options."""
    print("Demo 2: Custom Styling")
    print("=" * 50)
    
    # Create custom style
    custom_style = ChartStyle(
        figure_size=(12, 7),
        dpi=300,
        font_size=14,
        title_font_size=18,
        line_width=2.5,
        grid=True,
        grid_alpha=0.5,
        color_palette=['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
    )
    
    styler = ChartStyler(custom_style)
    
    # Create a bar chart
    fig, ax = plt.subplots(figsize=styler.style.figure_size, dpi=styler.style.dpi)
    
    # Apply base styling
    styler.apply_base_style(ax)
    
    # Generate sample data
    categories = ['A', 'B', 'C', 'D', 'E']
    values = [23, 45, 56, 78, 32]
    
    # Create bars with styled colors
    bars = ax.bar(
        categories,
        values,
        color=[styler.get_color(i) for i in range(len(categories))],
        edgecolor='black',
        linewidth=1.5
    )
    
    # Format labels
    styler.format_axis_labels(ax, 'Categories', 'Values', 'Custom Styled Bar Chart')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('output/demo_custom_styling.png', dpi=styler.style.dpi, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Chart saved to output/demo_custom_styling.png")
    print(f"  - Custom figure size: {custom_style.figure_size}")
    print(f"  - Custom font size: {custom_style.font_size}")
    print(f"  - Custom title font size: {custom_style.title_font_size}")
    print(f"  - Custom line width: {custom_style.line_width}")
    print(f"  - Custom color palette: {len(custom_style.color_palette)} colors")
    print()


def demo_colorblind_palette():
    """Demonstrate the colorblind-accessible palette."""
    print("Demo 3: Colorblind-Accessible Palette")
    print("=" * 50)
    
    styler = ChartStyler()
    
    # Create a figure showing all colors in the palette
    fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
    
    # Apply base styling
    styler.apply_base_style(ax)
    
    # Display color swatches
    for i, color in enumerate(DEFAULT_PALETTE):
        ax.barh(i, 1, color=color, edgecolor='black', linewidth=1)
        ax.text(0.5, i, f'Color {i}: {color}', 
                ha='center', va='center', 
                fontsize=12, fontweight='bold',
                color='white' if i in [0, 2, 5] else 'black')
    
    # Format the chart
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.5, len(DEFAULT_PALETTE) - 0.5)
    ax.set_yticks(range(len(DEFAULT_PALETTE)))
    ax.set_yticklabels([f'Color {i}' for i in range(len(DEFAULT_PALETTE))])
    ax.set_xticks([])
    ax.set_title('Colorblind-Accessible Palette', 
                 fontsize=18, fontfamily='sans-serif', pad=15)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('output/demo_colorblind_palette.png', dpi=300, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Palette visualization saved to output/demo_colorblind_palette.png")
    print(f"  - Total colors: {len(DEFAULT_PALETTE)}")
    print(f"  - Colors are designed for:")
    print(f"    • Protanopia (red-blind)")
    print(f"    • Deuteranopia (green-blind)")
    print(f"    • Tritanopia (blue-blind)")
    print()


def demo_minimum_font_size():
    """Demonstrate minimum font size enforcement."""
    print("Demo 4: Minimum Font Size Enforcement")
    print("=" * 50)
    
    # Try to create a style with very small fonts
    small_font_style = ChartStyle(
        font_size=5,  # Below minimum
        title_font_size=7  # Below minimum
    )
    
    styler = ChartStyler(small_font_style)
    
    # Create a chart
    fig, ax = plt.subplots(figsize=styler.style.figure_size, dpi=styler.style.dpi)
    
    # Apply styling
    styler.apply_base_style(ax)
    
    # Plot simple data
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    ax.plot(x, y, color=styler.get_color(0), linewidth=styler.style.line_width)
    
    # Format labels (minimum font size will be enforced)
    styler.format_axis_labels(ax, 'X Axis', 'Y Axis', 'Minimum Font Size Demo')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig('output/demo_minimum_font_size.png', dpi=styler.style.dpi, bbox_inches='tight')
    plt.close(fig)
    
    print(f"✓ Chart saved to output/demo_minimum_font_size.png")
    print(f"  - Requested font size: {small_font_style.font_size}")
    print(f"  - Requested title font size: {small_font_style.title_font_size}")
    print(f"  - Enforced minimum: 10 points")
    print(f"  - All text elements have readable font sizes")
    print()


def main():
    """Run all demos."""
    import os
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    print("\n" + "=" * 50)
    print("ChartStyler Demo Script")
    print("=" * 50 + "\n")
    
    demo_default_styling()
    demo_custom_styling()
    demo_colorblind_palette()
    demo_minimum_font_size()
    
    print("=" * 50)
    print("All demos completed successfully!")
    print("=" * 50)


if __name__ == '__main__':
    main()
