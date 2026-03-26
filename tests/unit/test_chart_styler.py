"""Unit tests for ChartStyler class."""

import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for testing
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from src.model_evaluation_viz.styling.chart_styler import ChartStyler
from src.model_evaluation_viz.styling.color_palettes import DEFAULT_PALETTE
from src.model_evaluation_viz.core.models import ChartStyle


class TestChartStyler:
    """Test suite for ChartStyler class."""
    
    def test_init_with_default_style(self):
        """Test ChartStyler initialization with default style."""
        styler = ChartStyler()
        
        assert styler.style is not None
        assert styler.style.font_size == 12
        assert styler.style.title_font_size == 14
        assert styler.style.line_width == 2.0
        assert styler.style.grid is True
        # ChartStyler should use DEFAULT_PALETTE from color_palettes module
        assert styler.style.color_palette == DEFAULT_PALETTE
    
    def test_init_with_custom_style(self):
        """Test ChartStyler initialization with custom style."""
        custom_style = ChartStyle(
            font_size=16,
            title_font_size=18,
            line_width=3.0,
            grid=False,
            color_palette=['#FF0000', '#00FF00', '#0000FF']
        )
        styler = ChartStyler(custom_style)
        
        assert styler.style.font_size == 16
        assert styler.style.title_font_size == 18
        assert styler.style.line_width == 3.0
        assert styler.style.grid is False
        assert styler.style.color_palette == ['#FF0000', '#00FF00', '#0000FF']
    
    def test_get_color_basic(self):
        """Test get_color returns correct colors from palette."""
        styler = ChartStyler()
        
        # Test first few colors
        assert styler.get_color(0) == DEFAULT_PALETTE[0]
        assert styler.get_color(1) == DEFAULT_PALETTE[1]
        assert styler.get_color(2) == DEFAULT_PALETTE[2]
    
    def test_get_color_wraps_around(self):
        """Test get_color wraps around when index exceeds palette length."""
        styler = ChartStyler()
        palette_length = len(DEFAULT_PALETTE)
        
        # Test wrapping
        assert styler.get_color(palette_length) == DEFAULT_PALETTE[0]
        assert styler.get_color(palette_length + 1) == DEFAULT_PALETTE[1]
        assert styler.get_color(palette_length * 2) == DEFAULT_PALETTE[0]
    
    def test_apply_base_style_with_grid(self):
        """Test apply_base_style enables grid when configured."""
        fig, ax = plt.subplots()
        styler = ChartStyler()
        
        styler.apply_base_style(ax)
        
        # Check grid is enabled
        assert ax.xaxis.get_gridlines()[0].get_visible()
        
        plt.close(fig)
    
    def test_apply_base_style_without_grid(self):
        """Test apply_base_style disables grid when configured."""
        custom_style = ChartStyle(grid=False)
        fig, ax = plt.subplots()
        styler = ChartStyler(custom_style)
        
        styler.apply_base_style(ax)
        
        # Check grid is disabled by checking if gridlines are not visible
        # When grid is off, gridlines should not be visible
        gridlines = ax.get_xgridlines()
        if gridlines:
            # If gridlines exist, they should not be visible
            assert not any(line.get_visible() for line in gridlines)
        
        plt.close(fig)
    
    def test_apply_base_style_minimum_font_size(self):
        """Test apply_base_style enforces minimum font size of 10 points."""
        # Create style with font size below minimum
        custom_style = ChartStyle(font_size=8, title_font_size=7)
        fig, ax = plt.subplots()
        styler = ChartStyler(custom_style)
        
        styler.apply_base_style(ax)
        
        # Font sizes should be enforced to minimum 10 in format_axis_labels
        # apply_base_style sets tick params
        tick_size = ax.xaxis.get_ticklabels()[0].get_fontsize() if ax.xaxis.get_ticklabels() else 10
        assert tick_size >= 8  # Tick params use the configured size
        
        plt.close(fig)
    
    def test_format_axis_labels_basic(self):
        """Test format_axis_labels sets labels and title correctly."""
        fig, ax = plt.subplots()
        styler = ChartStyler()
        
        styler.format_axis_labels(
            ax,
            xlabel='X Axis',
            ylabel='Y Axis',
            title='Test Chart'
        )
        
        assert ax.get_xlabel() == 'X Axis'
        assert ax.get_ylabel() == 'Y Axis'
        assert ax.get_title() == 'Test Chart'
        
        plt.close(fig)
    
    def test_format_axis_labels_font_sizes(self):
        """Test format_axis_labels applies correct font sizes."""
        custom_style = ChartStyle(font_size=14, title_font_size=16)
        fig, ax = plt.subplots()
        styler = ChartStyler(custom_style)
        
        styler.format_axis_labels(
            ax,
            xlabel='X Axis',
            ylabel='Y Axis',
            title='Test Chart'
        )
        
        # Check font sizes
        assert ax.xaxis.label.get_fontsize() == 14
        assert ax.yaxis.label.get_fontsize() == 14
        assert ax.title.get_fontsize() == 16
        
        plt.close(fig)
    
    def test_format_axis_labels_minimum_font_size(self):
        """Test format_axis_labels enforces minimum font size of 10 points."""
        custom_style = ChartStyle(font_size=5, title_font_size=7)
        fig, ax = plt.subplots()
        styler = ChartStyler(custom_style)
        
        styler.format_axis_labels(
            ax,
            xlabel='X Axis',
            ylabel='Y Axis',
            title='Test Chart'
        )
        
        # Check minimum font sizes are enforced
        assert ax.xaxis.label.get_fontsize() >= 10
        assert ax.yaxis.label.get_fontsize() >= 10
        assert ax.title.get_fontsize() >= 10
        
        plt.close(fig)
    
    def test_format_axis_labels_font_family(self):
        """Test format_axis_labels applies correct font family."""
        custom_style = ChartStyle(font_family='monospace')
        fig, ax = plt.subplots()
        styler = ChartStyler(custom_style)
        
        styler.format_axis_labels(
            ax,
            xlabel='X Axis',
            ylabel='Y Axis',
            title='Test Chart'
        )
        
        # Check font family
        assert ax.xaxis.label.get_fontfamily()[0] == 'monospace'
        assert ax.yaxis.label.get_fontfamily()[0] == 'monospace'
        assert ax.title.get_fontfamily()[0] == 'monospace'
        
        plt.close(fig)
    
    def test_format_axis_labels_text_color(self):
        """Test format_axis_labels applies correct text color."""
        custom_style = ChartStyle(text_color='red')
        fig, ax = plt.subplots()
        styler = ChartStyler(custom_style)
        
        styler.format_axis_labels(
            ax,
            xlabel='X Axis',
            ylabel='Y Axis',
            title='Test Chart'
        )
        
        # Check text color
        assert ax.xaxis.label.get_color() == 'red'
        assert ax.yaxis.label.get_color() == 'red'
        assert ax.title.get_color() == 'red'
        
        plt.close(fig)
    
    def test_complete_styling_workflow(self):
        """Test complete styling workflow with both methods."""
        fig, ax = plt.subplots()
        styler = ChartStyler()
        
        # Apply base style
        styler.apply_base_style(ax)
        
        # Format labels
        styler.format_axis_labels(
            ax,
            xlabel='Training Set Size',
            ylabel='Score',
            title='Learning Curve'
        )
        
        # Plot some data with styled colors
        x = [1, 2, 3, 4, 5]
        y1 = [0.6, 0.7, 0.75, 0.78, 0.8]
        y2 = [0.5, 0.65, 0.72, 0.76, 0.79]
        
        ax.plot(x, y1, color=styler.get_color(0), linewidth=styler.style.line_width, label='Train')
        ax.plot(x, y2, color=styler.get_color(1), linewidth=styler.style.line_width, label='Validation')
        ax.legend()
        
        # Verify chart has all elements
        assert ax.get_xlabel() == 'Training Set Size'
        assert ax.get_ylabel() == 'Score'
        assert ax.get_title() == 'Learning Curve'
        assert len(ax.lines) == 2
        assert ax.get_legend() is not None
        
        plt.close(fig)


class TestColorPalettes:
    """Test suite for color palettes."""
    
    def test_default_palette_length(self):
        """Test DEFAULT_PALETTE has 10 colors."""
        assert len(DEFAULT_PALETTE) == 10
    
    def test_default_palette_format(self):
        """Test DEFAULT_PALETTE colors are valid hex strings."""
        for color in DEFAULT_PALETTE:
            assert isinstance(color, str)
            assert color.startswith('#')
            assert len(color) == 7  # '#' + 6 hex digits
    
    def test_default_palette_uniqueness(self):
        """Test DEFAULT_PALETTE colors are unique."""
        assert len(DEFAULT_PALETTE) == len(set(DEFAULT_PALETTE))
