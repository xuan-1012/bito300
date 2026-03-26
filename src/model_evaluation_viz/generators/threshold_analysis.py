"""Threshold analysis generator for binary classification model evaluation."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional

from ..core.models import ChartStyle
from ..core.metric_calculator import MetricCalculator
from ..styling.chart_styler import ChartStyler


class ThresholdAnalysisGenerator:
    """Generates threshold analysis plots for binary classification.
    
    Threshold analysis plots visualize how Precision, Recall, and F1 Score
    vary across different classification thresholds from 0 to 1. This
    visualization helps data scientists select the optimal threshold by
    comparing the trade-offs between these metrics.
    
    The generator creates a professional visualization with:
    - Three curves showing Precision, Recall, and F1 Score vs threshold
    - Each metric displayed with a distinct color
    - Vertical line marking the threshold that maximizes F1 Score
    - Clear axis labels and legend
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
        calculator: MetricCalculator instance for computing threshold metrics.
    
    Example:
        >>> from model_evaluation_viz.generators.threshold_analysis import ThresholdAnalysisGenerator
        >>> import numpy as np
        >>> 
        >>> # Create generator with default styling
        >>> generator = ThresholdAnalysisGenerator()
        >>> 
        >>> # Generate threshold analysis plot
        >>> y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15])
        >>> fig = generator.generate(y_true=y_true, y_proba=y_proba)
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the ThresholdAnalysisGenerator.
        
        Args:
            styler: Optional ChartStyler for custom styling. If None, uses
                   default ChartStyler with colorblind-accessible palette.
        """
        self.styler = styler or ChartStyler()
        self.calculator = MetricCalculator()
    
    def generate(
        self,
        y_true: np.ndarray,
        y_proba: np.ndarray
    ) -> Figure:
        """Generate threshold analysis plot visualization.
        
        Creates a matplotlib figure showing Precision, Recall, and F1 Score
        as functions of classification threshold. The plot includes a vertical
        line marking the threshold that maximizes F1 Score, helping identify
        the optimal operating point.
        
        Args:
            y_true: Array of true binary labels (0 or 1).
            y_proba: Array of predicted probabilities for the positive class.
                    Values should be in the range [0, 1].
        
        Returns:
            Matplotlib Figure object containing the threshold analysis plot.
        
        Raises:
            ValueError: If y_true and y_proba have different lengths, or if
                       y_proba contains values outside [0, 1], or if y_true
                       doesn't contain exactly two unique values.
        
        Example:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85])
            >>> generator = ThresholdAnalysisGenerator()
            >>> fig = generator.generate(y_true=y_true, y_proba=y_proba)
        """
        # Validate input lengths
        if len(y_true) != len(y_proba):
            raise ValueError(
                f"y_true and y_proba must have the same length. "
                f"Got y_true: {len(y_true)}, y_proba: {len(y_proba)}"
            )
        
        # Validate binary labels
        unique_labels = np.unique(y_true)
        if len(unique_labels) != 2:
            raise ValueError(
                f"y_true must contain exactly 2 unique values for binary classification. "
                f"Got {len(unique_labels)} unique values: {unique_labels}"
            )
        
        # Validate probability range
        if np.any(y_proba < 0) or np.any(y_proba > 1):
            raise ValueError(
                f"y_proba must contain values in the range [0, 1]. "
                f"Got min: {y_proba.min():.4f}, max: {y_proba.max():.4f}"
            )
        
        # Calculate threshold metrics from 0 to 1
        threshold_metrics = self.calculator.calculate_threshold_metrics(
            y_true, y_proba, thresholds=None  # Uses default np.linspace(0, 1, 100)
        )
        
        thresholds = threshold_metrics['thresholds']
        precision = threshold_metrics['precision']
        recall = threshold_metrics['recall']
        f1_score = threshold_metrics['f1_score']
        
        # Find threshold that maximizes F1 Score (ignoring NaN values)
        valid_f1_mask = ~np.isnan(f1_score)
        if np.any(valid_f1_mask):
            best_f1_idx = np.nanargmax(f1_score)
            best_threshold = thresholds[best_f1_idx]
            best_f1 = f1_score[best_f1_idx]
        else:
            # If all F1 scores are NaN, use threshold 0.5 as default
            best_threshold = 0.5
            best_f1 = np.nan
        
        # Create figure with configured size and DPI
        fig, ax = plt.subplots(
            figsize=self.styler.style.figure_size,
            dpi=self.styler.style.dpi
        )
        
        # Apply base styling
        self.styler.apply_base_style(ax)
        
        # Plot Precision curve
        ax.plot(
            thresholds,
            precision,
            color=self.styler.get_color(0),
            linewidth=self.styler.style.line_width,
            label='Precision'
        )
        
        # Plot Recall curve
        ax.plot(
            thresholds,
            recall,
            color=self.styler.get_color(1),
            linewidth=self.styler.style.line_width,
            label='Recall'
        )
        
        # Plot F1 Score curve
        ax.plot(
            thresholds,
            f1_score,
            color=self.styler.get_color(2),
            linewidth=self.styler.style.line_width,
            label='F1 Score'
        )
        
        # Mark threshold that maximizes F1 Score with vertical line
        ax.axvline(
            x=best_threshold,
            color='gray',
            linestyle='--',
            linewidth=self.styler.style.line_width * 0.8,
            label=f'Optimal Threshold = {best_threshold:.3f}'
        )
        
        # Add annotation for optimal threshold
        if not np.isnan(best_f1):
            ax.annotate(
                f'Max F1 = {best_f1:.3f}',
                xy=(best_threshold, best_f1),
                xytext=(10, 10),
                textcoords='offset points',
                fontsize=max(10, self.styler.style.font_size),
                bbox=dict(boxstyle='round,pad=0.5', facecolor='white', alpha=0.7),
                arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0')
            )
        
        # Set axis limits
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.0])
        
        # Format axis labels and title
        self.styler.format_axis_labels(
            ax=ax,
            xlabel='Threshold',
            ylabel='Metric Value',
            title='Threshold Analysis'
        )
        
        # Add legend
        ax.legend(
            loc='best',
            fontsize=max(10, self.styler.style.font_size),
            frameon=True,
            fancybox=True,
            shadow=False
        )
        
        # Adjust layout to prevent label cutoff
        fig.tight_layout()
        
        return fig
