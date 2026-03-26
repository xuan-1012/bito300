"""Learning curve generator for training set size analysis."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional

from ..core.models import ChartStyle
from ..styling.chart_styler import ChartStyler


class LearningCurveGenerator:
    """Generates learning curves for training set size analysis.
    
    Learning curves show how training and validation scores change as the
    training set size increases. This helps determine if the model is
    overfitting and whether adding more data would improve performance.
    
    The generator plots both training and validation scores on the same chart
    with distinct colors, includes optional variance bands (shaded regions),
    a legend, axis labels, and title.
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
    
    Example:
        >>> from model_evaluation_viz.generators.learning_curve import LearningCurveGenerator
        >>> from model_evaluation_viz.core.models import ChartStyle
        >>> 
        >>> # Create generator with default styling
        >>> generator = LearningCurveGenerator()
        >>> 
        >>> # Generate learning curve with variance bands
        >>> train_sizes = np.array([100, 200, 500, 1000, 2000])
        >>> train_scores = np.array([0.95, 0.92, 0.90, 0.88, 0.87])
        >>> val_scores = np.array([0.75, 0.80, 0.83, 0.85, 0.86])
        >>> train_std = np.array([0.02, 0.015, 0.01, 0.008, 0.005])
        >>> val_std = np.array([0.05, 0.04, 0.03, 0.02, 0.015])
        >>> fig = generator.generate(
        ...     train_sizes=train_sizes,
        ...     train_scores=train_scores,
        ...     val_scores=val_scores,
        ...     train_std=train_std,
        ...     val_std=val_std
        ... )
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the LearningCurveGenerator.
        
        Args:
            styler: Optional ChartStyler for custom styling. If None, uses
                   default ChartStyler with colorblind-accessible palette.
        """
        self.styler = styler or ChartStyler()
    
    def generate(
        self,
        train_sizes: np.ndarray,
        train_scores: np.ndarray,
        val_scores: np.ndarray,
        train_std: Optional[np.ndarray] = None,
        val_std: Optional[np.ndarray] = None
    ) -> Figure:
        """Generate learning curve chart.
        
        Creates a matplotlib figure showing training and validation scores
        across different training set sizes. The x-axis represents the
        training set size, and the y-axis represents the scores.
        
        If standard deviation arrays are provided, shaded variance bands
        are displayed around the mean scores to show score variability.
        
        Args:
            train_sizes: Array of training set sizes (x-axis).
            train_scores: Array of mean training scores corresponding to train_sizes.
            val_scores: Array of mean validation scores corresponding to train_sizes.
            train_std: Optional array of training score standard deviations.
                      If provided, displays shaded variance band around training curve.
            val_std: Optional array of validation score standard deviations.
                    If provided, displays shaded variance band around validation curve.
        
        Returns:
            Matplotlib Figure object containing the learning curve.
        
        Raises:
            ValueError: If train_sizes, train_scores, and val_scores have
                       different lengths, or if std arrays don't match score lengths.
        
        Example:
            >>> train_sizes = np.array([50, 100, 200, 500])
            >>> train_scores = np.array([0.90, 0.88, 0.86, 0.85])
            >>> val_scores = np.array([0.75, 0.80, 0.82, 0.83])
            >>> generator = LearningCurveGenerator()
            >>> fig = generator.generate(
            ...     train_sizes=train_sizes,
            ...     train_scores=train_scores,
            ...     val_scores=val_scores
            ... )
        """
        # Validate input lengths
        if not (len(train_sizes) == len(train_scores) == len(val_scores)):
            raise ValueError(
                f"train_sizes, train_scores, and val_scores must have the same length. "
                f"Got train_sizes: {len(train_sizes)}, train_scores: {len(train_scores)}, "
                f"val_scores: {len(val_scores)}"
            )
        
        # Validate std arrays if provided
        if train_std is not None and len(train_std) != len(train_scores):
            raise ValueError(
                f"train_std must have the same length as train_scores. "
                f"Got train_std: {len(train_std)}, train_scores: {len(train_scores)}"
            )
        
        if val_std is not None and len(val_std) != len(val_scores):
            raise ValueError(
                f"val_std must have the same length as val_scores. "
                f"Got val_std: {len(val_std)}, val_scores: {len(val_scores)}"
            )
        
        # Create figure with configured size and DPI
        fig, ax = plt.subplots(
            figsize=self.styler.style.figure_size,
            dpi=self.styler.style.dpi
        )
        
        # Apply base styling (grid, fonts, etc.)
        self.styler.apply_base_style(ax)
        
        # Get colors for training and validation curves
        train_color = self.styler.get_color(0)
        val_color = self.styler.get_color(1)
        
        # Plot training scores with variance band if provided
        ax.plot(
            train_sizes,
            train_scores,
            marker='o',
            linestyle='-',
            linewidth=self.styler.style.line_width,
            markersize=self.styler.style.marker_size,
            color=train_color,
            label='Training Score'
        )
        
        if train_std is not None:
            ax.fill_between(
                train_sizes,
                train_scores - train_std,
                train_scores + train_std,
                alpha=0.2,
                color=train_color
            )
        
        # Plot validation scores with variance band if provided
        ax.plot(
            train_sizes,
            val_scores,
            marker='s',
            linestyle='-',
            linewidth=self.styler.style.line_width,
            markersize=self.styler.style.marker_size,
            color=val_color,
            label='Validation Score'
        )
        
        if val_std is not None:
            ax.fill_between(
                train_sizes,
                val_scores - val_std,
                val_scores + val_std,
                alpha=0.2,
                color=val_color
            )
        
        # Format axis labels and title
        self.styler.format_axis_labels(
            ax=ax,
            xlabel='Training Set Size',
            ylabel='Score',
            title='Learning Curve'
        )
        
        # Add legend
        ax.legend(
            loc='best',
            fontsize=max(10, self.styler.style.font_size),
            framealpha=0.9
        )
        
        # Adjust layout to prevent label cutoff
        fig.tight_layout()
        
        return fig
