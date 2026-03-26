"""Unit tests for ThresholdAnalysisGenerator."""

import pytest
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from src.model_evaluation_viz.generators.threshold_analysis import ThresholdAnalysisGenerator
from src.model_evaluation_viz.core.models import ChartStyle
from src.model_evaluation_viz.styling.chart_styler import ChartStyler


class TestThresholdAnalysisGenerator:
    """Test suite for ThresholdAnalysisGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = ThresholdAnalysisGenerator()
        
        # Create sample binary classification data
        np.random.seed(42)
        self.y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1])
        self.y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15, 0.95, 0.7])
    
    def teardown_method(self):
        """Clean up after tests."""
        plt.close('all')
    
    def test_initialization_default_styler(self):
        """Test generator initializes with default styler."""
        generator = ThresholdAnalysisGenerator()
        assert generator.styler is not None
        assert generator.calculator is not None
    
    def test_initialization_custom_styler(self):
        """Test generator initializes with custom styler."""
        custom_style = ChartStyle(font_size=16, line_width=3.0)
        custom_styler = ChartStyler(custom_style)
        generator = ThresholdAnalysisGenerator(styler=custom_styler)
        
        assert generator.styler is custom_styler
        assert generator.styler.style.font_size == 16
        assert generator.styler.style.line_width == 3.0
    
    def test_generate_returns_figure(self):
        """Test generate returns a matplotlib Figure object."""
        fig = self.generator.generate(self.y_true, self.y_proba)
        
        assert isinstance(fig, Figure)
        assert len(fig.axes) == 1
    
    def test_generate_chart_completeness(self):
        """Test generated chart contains all required elements."""
        fig = self.generator.generate(self.y_true, self.y_proba)
        ax = fig.axes[0]
        
        # Check axis labels
        assert ax.get_xlabel() == 'Threshold'
        assert ax.get_ylabel() == 'Metric Value'
        
        # Check title
        assert ax.get_title() == 'Threshold Analysis'
        
        # Check legend exists
        legend = ax.get_legend()
        assert legend is not None
    
    def test_generate_three_metric_curves(self):
        """Test chart displays three metric curves (Precision, Recall, F1)."""
        fig = self.generator.generate(self.y_true, self.y_proba)
        ax = fig.axes[0]
        
        # Get all lines (should be 4: Precision, Recall, F1, and vertical line)
        lines = ax.get_lines()
        assert len(lines) >= 4
        
        # Check legend labels contain the three metrics
        legend = ax.get_legend()
        legend_texts = [text.get_text() for text in legend.get_texts()]
        
        assert any('Precision' in text for text in legend_texts)
        assert any('Recall' in text for text in legend_texts)
        assert any('F1 Score' in text for text in legend_texts)
    
    def test_generate_optimal_threshold_marking(self):
        """Test chart marks the optimal threshold with vertical line."""
        fig = self.generator.generate(self.y_true, self.y_proba)
        ax = fig.axes[0]
        
        # Check for vertical line in legend
        legend = ax.get_legend()
        legend_texts = [text.get_text() for text in legend.get_texts()]
        
        assert any('Optimal Threshold' in text for text in legend_texts)
        
        # Check for annotation
        annotations = [child for child in ax.get_children() 
                      if hasattr(child, 'get_text') and 'Max F1' in str(child.get_text())]
        assert len(annotations) > 0 or any('Max F1' in text for text in legend_texts)
    
    def test_generate_axis_ranges(self):
        """Test x-axis and y-axis have correct ranges [0, 1]."""
        fig = self.generator.generate(self.y_true, self.y_proba)
        ax = fig.axes[0]
        
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        
        assert xlim[0] == 0.0
        assert xlim[1] == 1.0
        assert ylim[0] == 0.0
        assert ylim[1] == 1.0
    
    def test_generate_distinct_colors(self):
        """Test three metric curves use distinct colors."""
        fig = self.generator.generate(self.y_true, self.y_proba)
        ax = fig.axes[0]
        
        lines = ax.get_lines()
        # Get colors of first three lines (Precision, Recall, F1)
        colors = [line.get_color() for line in lines[:3]]
        
        # All three colors should be different
        assert len(set(colors)) == 3
    
    def test_validation_length_mismatch(self):
        """Test ValueError raised when y_true and y_proba have different lengths."""
        y_true = np.array([0, 1, 1, 0])
        y_proba = np.array([0.1, 0.9, 0.8])
        
        with pytest.raises(ValueError, match="same length"):
            self.generator.generate(y_true, y_proba)
    
    def test_validation_non_binary_labels(self):
        """Test ValueError raised when y_true contains non-binary labels."""
        y_true = np.array([0, 1, 2, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85])
        
        with pytest.raises(ValueError, match="exactly 2 unique values"):
            self.generator.generate(y_true, y_proba)
    
    def test_validation_probability_out_of_range(self):
        """Test ValueError raised when y_proba contains values outside [0, 1]."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 1.5, 0.8, -0.2, 0.85])
        
        with pytest.raises(ValueError, match="range \\[0, 1\\]"):
            self.generator.generate(y_true, y_proba)
    
    def test_perfect_classifier(self):
        """Test threshold analysis with perfect classifier."""
        y_true = np.array([0, 0, 1, 1, 0, 1])
        y_proba = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 1.0])
        
        fig = self.generator.generate(y_true, y_proba)
        
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert ax.get_xlabel() == 'Threshold'
    
    def test_random_classifier(self):
        """Test threshold analysis with random classifier."""
        np.random.seed(123)
        y_true = np.random.randint(0, 2, 100)
        y_proba = np.random.random(100)
        
        fig = self.generator.generate(y_true, y_proba)
        
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert len(ax.get_lines()) >= 4
    
    def test_imbalanced_dataset(self):
        """Test threshold analysis with highly imbalanced dataset."""
        # 95% negative, 5% positive
        y_true = np.array([0] * 95 + [1] * 5)
        y_proba = np.random.random(100)
        
        fig = self.generator.generate(y_true, y_proba)
        
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert ax.get_title() == 'Threshold Analysis'
    
    def test_custom_styling_applied(self):
        """Test custom styling is applied to generated chart."""
        custom_style = ChartStyle(
            figure_size=(12, 8),
            dpi=150,
            font_size=14,
            line_width=3.0
        )
        custom_styler = ChartStyler(custom_style)
        generator = ThresholdAnalysisGenerator(styler=custom_styler)
        
        fig = generator.generate(self.y_true, self.y_proba)
        
        # Check figure size
        assert fig.get_figwidth() == 12
        assert fig.get_figheight() == 8
        
        # Check DPI
        assert fig.dpi == 150
        
        # Check line width
        ax = fig.axes[0]
        lines = ax.get_lines()
        for line in lines[:3]:  # Check first three lines (metrics)
            assert line.get_linewidth() == 3.0
    
    def test_minimum_font_size(self):
        """Test minimum font size of 10 points is enforced."""
        custom_style = ChartStyle(font_size=8)  # Below minimum
        custom_styler = ChartStyler(custom_style)
        generator = ThresholdAnalysisGenerator(styler=custom_styler)
        
        fig = generator.generate(self.y_true, self.y_proba)
        ax = fig.axes[0]
        
        # Font size should be at least 10
        xlabel_fontsize = ax.xaxis.label.get_fontsize()
        assert xlabel_fontsize >= 10
    
    def test_all_same_predictions(self):
        """Test threshold analysis when all predictions are the same."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        
        fig = self.generator.generate(y_true, y_proba)
        
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert ax.get_xlabel() == 'Threshold'
    
    def test_single_positive_class(self):
        """Test threshold analysis with only one positive sample."""
        y_true = np.array([0, 0, 0, 0, 1])
        y_proba = np.array([0.1, 0.2, 0.3, 0.4, 0.9])
        
        fig = self.generator.generate(y_true, y_proba)
        
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert len(ax.get_lines()) >= 4
    
    def test_large_dataset(self):
        """Test threshold analysis with large dataset."""
        np.random.seed(456)
        y_true = np.random.randint(0, 2, 1000)
        y_proba = np.random.random(1000)
        
        fig = self.generator.generate(y_true, y_proba)
        
        assert isinstance(fig, Figure)
        ax = fig.axes[0]
        assert ax.get_title() == 'Threshold Analysis'
