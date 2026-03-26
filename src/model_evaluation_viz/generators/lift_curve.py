"""Lift curve generator for binary classification model evaluation."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional

from ..core.models import ChartStyle
from ..core.metric_calculator import MetricCalculator
from ..styling.chart_styler import ChartStyler


class LiftCurveGenerator:
    """Generates lift curves for binary classification model evaluation.
    
    Lift curves visualize the model's ability to rank high-risk samples by
    showing the cumulative percentage of positive cases captured as a function
    of the percentage of samples examined (sorted by predicted probability).
    This demonstrates the model's effectiveness compared to random selection.
    
    The generator creates a professional visualization with:
    - Model curve showing cumulative percentage of positives vs sample percentage
    - Diagonal reference line representing random selection
    - Lift values at specific percentiles displayed in annotations/legend
    - Clear axis labels and title
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
        calculator: MetricCalculator instance for computing lift metrics.
    
    Example:
        >>> from model_evaluation_viz.generators.lift_curve import LiftCurveGenerator
        >>> import numpy as np
        >>> 
        >>> # Create generator with default styling
        >>> generator = LiftCurveGenerator()
        >>> 
        >>> # Generate lift curve
        >>> y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15])
        >>> fig = generator.generate(y_true=y_true, y_proba=y_proba)
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the LiftCurveGenerator.
        
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
        """Generate lift curve visualization.
        
        Creates a matplotlib figure showing the lift curve. Samples are sorted
        by predicted probability in descending order, and the cumulative
        percentage of positive cases is plotted against the percentage of
        samples examined. A diagonal reference line shows random selection
        performance for comparison.
        
        Args:
            y_true: Array of true binary labels (0 or 1).
            y_proba: Array of predicted probabilities for the positive class.
                    Values should be in the range [0, 1].
        
        Returns:
            Matplotlib Figure object containing the lift curve.
        
        Raises:
            ValueError: If y_true and y_proba have different lengths, or if
                       y_proba contains values outside [0, 1], or if y_true
                       doesn't contain exactly two unique values.
        
        Example:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85])
            >>> generator = LiftCurveGenerator()
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
        
        # Calculate lift curve using MetricCalculator
        percentages, cumulative_gains = self.calculator.calculate_lift_curve(
            y_true, y_proba
        )
        
        # Calculate lift values at specific percentiles (10%, 20%, 30%, 50%)
        percentile_points = [10, 20, 30, 50]
        lift_values = {}
        
        for percentile in percentile_points:
            # Find the index closest to this percentile
            idx = int(len(percentages) * percentile / 100)
            if idx < len(cumulative_gains):
                # Lift = (cumulative % of positives) / (% of samples)
                # This represents how much better than random selection
                if percentile > 0:
                    lift = cumulative_gains[idx] / percentile
                    lift_values[percentile] = lift
        
        # Create figure with configured size and DPI
        fig, ax = plt.subplots(
            figsize=self.styler.style.figure_size,
            dpi=self.styler.style.dpi
        )
        
        # Apply base styling
        self.styler.apply_base_style(ax)
        
        # Plot model lift curve
        ax.plot(
            percentages,
            cumulative_gains,
            color=self.styler.get_color(0),
            linewidth=self.styler.style.line_width,
            label='Model'
        )
        
        # Plot diagonal reference line (random selection)
        ax.plot(
            [0, 100],
            [0, 100],
            color='gray',
            linestyle='--',
            linewidth=self.styler.style.line_width * 0.8,
            label='Random Selection'
        )
        
        # Add lift value annotations at specific percentiles
        for percentile in percentile_points:
            idx = int(len(percentages) * percentile / 100)
            if idx < len(cumulative_gains) and percentile in lift_values:
                lift = lift_values[percentile]
                # Add annotation showing lift value
                ax.annotate(
                    f'{percentile}%: Lift={lift:.2f}x',
                    xy=(percentages[idx], cumulative_gains[idx]),
                    xytext=(10, -10),
                    textcoords='offset points',
                    fontsize=max(9, self.styler.style.font_size - 2),
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7, edgecolor='gray'),
                    arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='gray', lw=1)
                )
        
        # Set axis limits
        ax.set_xlim([0.0, 100.0])
        ax.set_ylim([0.0, 100.0])
        
        # Format axis labels and title
        self.styler.format_axis_labels(
            ax=ax,
            xlabel='Percentage of Samples (%)',
            ylabel='Cumulative Percentage of Positives (%)',
            title='Lift Curve'
        )
        
        # Add legend
        ax.legend(
            loc='lower right',
            fontsize=max(10, self.styler.style.font_size),
            frameon=True,
            fancybox=True,
            shadow=False
        )
        
        # Adjust layout to prevent label cutoff
        fig.tight_layout()
        
        return fig
