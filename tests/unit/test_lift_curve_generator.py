"""Unit tests for LiftCurveGenerator class."""

import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.model_evaluation_viz.generators.lift_curve import LiftCurveGenerator
from src.model_evaluation_viz.styling.chart_styler import ChartStyler


class TestLiftCurveGenerator:
    """Test suite for LiftCurveGenerator class."""
    
    def test_initialization_default_styler(self):
        """Test generator initialization with default styler."""
        generator = LiftCurveGenerator()
        
        assert generator.styler is not None
        assert isinstance(generator.styler, ChartStyler)
        assert generator.calculator is not None
    
    def test_initialization_custom_styler(self):
        """Test generator initialization with custom styler."""
        custom_styler = ChartStyler()
        generator = LiftCurveGenerator(styler=custom_styler)
        
        assert generator.styler is custom_styler
    
    def test_generate_returns_figure(self):
        """Test that generate returns a matplotlib Figure."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        
        assert isinstance(fig, Figure)
        plt.close(fig)
    
    def test_generate_with_perfect_classifier(self):
        """Test lift curve generation with perfect classifier."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        
        assert isinstance(fig, Figure)
        
        # Check that figure has axes
        axes = fig.get_axes()
        assert len(axes) == 1
        
        ax = axes[0]
        
        # Check axis labels
        assert 'Percentage of Samples' in ax.get_xlabel()
        assert 'Cumulative Percentage of Positives' in ax.get_ylabel()
        assert 'Lift Curve' in ax.get_title()
        
        # Check axis limits (should be 0-100 for percentages)
        assert ax.get_xlim() == (0.0, 100.0)
        assert ax.get_ylim() == (0.0, 100.0)
        
        # Check that there are lines plotted
        lines = ax.get_lines()
        assert len(lines) >= 2  # Model curve + diagonal reference
        
        # Check legend exists
        legend = ax.get_legend()
        assert legend is not None
        
        plt.close(fig)
    
    def test_generate_axis_ranges(self):
        """Test that axes range from 0 to 100 (percentages)."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Get the lift curve line (first line)
        lines = ax.get_lines()
        lift_line = lines[0]
        
        xdata = lift_line.get_xdata()
        ydata = lift_line.get_ydata()
        
        # X-axis should be percentage of samples (0 to 100)
        assert np.min(xdata) >= 0 and np.max(xdata) <= 100
        # Y-axis should be cumulative percentage of positives (0 to 100)
        assert np.min(ydata) >= 0 and np.max(ydata) <= 100
        
        plt.close(fig)
    
    def test_generate_reference_line(self):
        """Test that diagonal reference line is included."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Check that there are at least 2 lines (lift curve + reference)
        lines = ax.get_lines()
        assert len(lines) >= 2
        
        # The reference line should be diagonal from (0,0) to (100,100)
        reference = lines[1]
        xdata = reference.get_xdata()
        ydata = reference.get_ydata()
        
        # Should start at (0,0) and end at (100,100)
        assert xdata[0] == 0 and xdata[-1] == 100
        assert ydata[0] == 0 and ydata[-1] == 100
        
        plt.close(fig)
    
    def test_generate_percentile_annotations(self):
        """Test that lift values at specific percentiles are displayed."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15, 0.95, 0.88])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Check that there are annotations on the chart
        annotations = [child for child in ax.get_children() 
                      if isinstance(child, matplotlib.text.Annotation)]
        
        # Should have annotations for percentiles (10%, 20%, 30%, 50%)
        assert len(annotations) > 0
        
        # Check that annotations contain "Lift" text
        annotation_texts = [ann.get_text() for ann in annotations]
        lift_annotations = [text for text in annotation_texts if 'Lift' in text]
        assert len(lift_annotations) > 0
        
        plt.close(fig)
    
    def test_generate_validates_input_length(self):
        """Test that generator validates input array lengths."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8])  # Different length
        
        with pytest.raises(ValueError, match="must have the same length"):
            generator.generate(y_true=y_true, y_proba=y_proba)
    
    def test_generate_validates_binary_labels(self):
        """Test that generator validates binary labels."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 2, 0, 1])  # Three classes
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        with pytest.raises(ValueError, match="exactly 2 unique values"):
            generator.generate(y_true=y_true, y_proba=y_proba)
    
    def test_generate_validates_probability_range(self):
        """Test that generator validates probability range."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 1.5, 0.8, 0.2, 0.7])  # Value > 1
        
        with pytest.raises(ValueError, match="must contain values in the range"):
            generator.generate(y_true=y_true, y_proba=y_proba)
    
    def test_generate_with_good_model(self):
        """Test lift curve with a model that ranks positives well."""
        generator = LiftCurveGenerator()
        # Good model: high probabilities for positives, low for negatives
        y_true = np.array([1, 1, 1, 1, 0, 0, 0, 0])
        y_proba = np.array([0.9, 0.85, 0.8, 0.75, 0.3, 0.2, 0.15, 0.1])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Get the lift curve
        lines = ax.get_lines()
        lift_line = lines[0]
        ydata = lift_line.get_ydata()
        
        # For a good model, the curve should be above the diagonal
        # At 50% of samples, should have captured more than 50% of positives
        mid_idx = len(ydata) // 2
        assert ydata[mid_idx] > 50
        
        plt.close(fig)
    
    def test_generate_chart_completeness(self):
        """Test that generated chart contains all required elements."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Check axis labels
        assert ax.get_xlabel() != ''
        assert ax.get_ylabel() != ''
        
        # Check title
        assert ax.get_title() != ''
        
        # Check legend
        assert ax.get_legend() is not None
        
        # Check that there are lines plotted
        assert len(ax.get_lines()) >= 2
        
        plt.close(fig)
    
    def test_generate_applies_styling(self):
        """Test that generator applies ChartStyler styling."""
        generator = LiftCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Check that lines have appropriate width
        lines = ax.get_lines()
        assert len(lines) >= 2
        for line in lines:
            assert line.get_linewidth() > 0
        
        # Check that figure has proper DPI
        assert fig.dpi > 0
        
        plt.close(fig)
    
    def test_generate_sorted_by_probability(self):
        """Test that samples are sorted by predicted probability descending."""
        generator = LiftCurveGenerator()
        # Create data where sorting matters
        y_true = np.array([0, 1, 0, 1, 0, 1])
        y_proba = np.array([0.2, 0.9, 0.3, 0.7, 0.1, 0.8])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        
        # The function should not raise an error and should produce a valid figure
        assert isinstance(fig, Figure)
        
        # Get the lift curve
        ax = fig.get_axes()[0]
        lines = ax.get_lines()
        lift_line = lines[0]
        ydata = lift_line.get_ydata()
        
        # The cumulative gains should be monotonically increasing
        assert np.all(np.diff(ydata) >= 0)
        
        plt.close(fig)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
