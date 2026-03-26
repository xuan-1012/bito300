"""Unit tests for PrecisionRecallCurveGenerator class."""

import numpy as np
import pytest
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.model_evaluation_viz.generators.precision_recall import PrecisionRecallCurveGenerator
from src.model_evaluation_viz.styling.chart_styler import ChartStyler


class TestPrecisionRecallCurveGenerator:
    """Test suite for PrecisionRecallCurveGenerator class."""
    
    def test_initialization_default_styler(self):
        """Test generator initialization with default styler."""
        generator = PrecisionRecallCurveGenerator()
        
        assert generator.styler is not None
        assert isinstance(generator.styler, ChartStyler)
        assert generator.calculator is not None
    
    def test_initialization_custom_styler(self):
        """Test generator initialization with custom styler."""
        custom_styler = ChartStyler()
        generator = PrecisionRecallCurveGenerator(styler=custom_styler)
        
        assert generator.styler is custom_styler
    
    def test_generate_returns_figure(self):
        """Test that generate returns a matplotlib Figure."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        
        assert isinstance(fig, Figure)
        plt.close(fig)
    
    def test_generate_with_perfect_classifier(self):
        """Test PR curve generation with perfect classifier."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        
        assert isinstance(fig, Figure)
        
        # Check that figure has axes
        axes = fig.get_axes()
        assert len(axes) == 1
        
        ax = axes[0]
        
        # Check axis labels
        assert ax.get_xlabel() == 'Recall'
        assert ax.get_ylabel() == 'Precision'
        assert 'Precision-Recall Curve' in ax.get_title()
        
        # Check axis limits
        assert ax.get_xlim() == (0.0, 1.0)
        assert ax.get_ylim() == (0.0, 1.0)
        
        # Check that there are lines plotted
        lines = ax.get_lines()
        assert len(lines) >= 2  # PR curve + baseline
        
        # Check legend exists
        legend = ax.get_legend()
        assert legend is not None
        
        # Check legend contains AP score
        legend_texts = [text.get_text() for text in legend.get_texts()]
        assert any('AP' in text for text in legend_texts)
        
        plt.close(fig)
    
    def test_generate_axis_mapping(self):
        """Test that x-axis is Recall and y-axis is Precision."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Get the PR curve line (first line)
        lines = ax.get_lines()
        pr_line = lines[0]
        
        xdata = pr_line.get_xdata()
        ydata = pr_line.get_ydata()
        
        # X-axis should be Recall (0 to 1)
        assert np.all(xdata >= 0) and np.all(xdata <= 1)
        # Y-axis should be Precision (0 to 1)
        assert np.all(ydata >= 0) and np.all(ydata <= 1)
        
        plt.close(fig)
    
    def test_generate_baseline_reference_line(self):
        """Test that baseline reference line is included."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Check that there are at least 2 lines (PR curve + baseline)
        lines = ax.get_lines()
        assert len(lines) >= 2
        
        # The baseline should be a horizontal line
        baseline = lines[1]
        ydata = baseline.get_ydata()
        
        # Baseline should be constant (horizontal line)
        assert len(np.unique(ydata)) == 1 or np.allclose(ydata, ydata[0])
        
        # Baseline should be the proportion of positive class
        expected_baseline = y_true.sum() / len(y_true)
        assert np.allclose(ydata[0], expected_baseline, atol=0.01)
        
        plt.close(fig)
    
    def test_generate_average_precision_display(self):
        """Test that Average Precision score is displayed."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        ax = fig.get_axes()[0]
        
        # Check legend contains AP
        legend = ax.get_legend()
        legend_texts = [text.get_text() for text in legend.get_texts()]
        
        # Should contain "AP" or "Average Precision"
        ap_found = any('AP' in text for text in legend_texts)
        assert ap_found, f"AP not found in legend texts: {legend_texts}"
        
        # Should contain a numeric value
        ap_text = [text for text in legend_texts if 'AP' in text][0]
        assert any(char.isdigit() for char in ap_text)
        
        plt.close(fig)
    
    def test_generate_validates_input_length(self):
        """Test that generator validates input array lengths."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8])  # Different length
        
        with pytest.raises(ValueError, match="must have the same length"):
            generator.generate(y_true=y_true, y_proba=y_proba)
    
    def test_generate_validates_binary_labels(self):
        """Test that generator validates binary labels."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 2, 0, 1])  # Three classes
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        with pytest.raises(ValueError, match="exactly 2 unique values"):
            generator.generate(y_true=y_true, y_proba=y_proba)
    
    def test_generate_validates_probability_range(self):
        """Test that generator validates probability range."""
        generator = PrecisionRecallCurveGenerator()
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 1.5, 0.8, 0.2, 0.7])  # Value > 1
        
        with pytest.raises(ValueError, match="must contain values in the range"):
            generator.generate(y_true=y_true, y_proba=y_proba)
    
    def test_generate_with_imbalanced_data(self):
        """Test PR curve with imbalanced dataset."""
        generator = PrecisionRecallCurveGenerator()
        # 90% negative, 10% positive
        y_true = np.array([0] * 90 + [1] * 10)
        y_proba = np.random.random(100)
        
        fig = generator.generate(y_true=y_true, y_proba=y_proba)
        
        assert isinstance(fig, Figure)
        
        # Baseline should be around 0.1 (10% positive)
        ax = fig.get_axes()[0]
        lines = ax.get_lines()
        baseline = lines[1]
        ydata = baseline.get_ydata()
        
        assert np.allclose(ydata[0], 0.1, atol=0.01)
        
        plt.close(fig)
    
    def test_generate_chart_completeness(self):
        """Test that generated chart contains all required elements."""
        generator = PrecisionRecallCurveGenerator()
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
        generator = PrecisionRecallCurveGenerator()
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
