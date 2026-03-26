"""Validation curve generator for hyperparameter tuning visualization."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional

from ..core.models import ChartStyle
from ..styling.chart_styler import ChartStyler


class ValidationCurveGenerator:
    """Generates validation curves for hyperparameter tuning.
    
    Validation curves show how training and validation scores change as a
    hyperparameter varies. This helps identify overfitting and select optimal
    hyperparameter values.
    
    The generator plots both training and validation scores on the same chart
    with distinct colors, includes a legend, axis labels, and title, and
    supports logarithmic scale for hyperparameters spanning multiple orders
    of magnitude.
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
    
    Example:
        >>> from model_evaluation_viz.generators.validation_curve import ValidationCurveGenerator
        >>> from model_evaluation_viz.core.models import ChartStyle
        >>> 
        >>> # Create generator with default styling
        >>> generator = ValidationCurveGenerator()
        >>> 
        >>> # Generate validation curve
        >>> param_values = np.array([0.001, 0.01, 0.1, 1.0, 10.0])
        >>> train_scores = np.array([0.95, 0.92, 0.88, 0.85, 0.82])
        >>> val_scores = np.array([0.75, 0.82, 0.85, 0.84, 0.80])
        >>> fig = generator.generate(
        ...     param_values=param_values,
        ...     train_scores=train_scores,
        ...     val_scores=val_scores,
        ...     param_name='C (Regularization)',
        ...     log_scale=True
        ... )
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the ValidationCurveGenerator.
        
        Args:
            styler: Optional ChartStyler for custom styling. If None, uses
                   default ChartStyler with colorblind-accessible palette.
        """
        self.styler = styler or ChartStyler()
    
    def generate(
        self,
        param_values: np.ndarray,
        train_scores: np.ndarray,
        val_scores: np.ndarray,
        param_name: str,
        log_scale: bool = False
    ) -> Figure:
        """Generate validation curve chart.
        
        Creates a matplotlib figure showing training and validation scores
        across different hyperparameter values. The x-axis represents the
        hyperparameter values, and the y-axis represents the scores.
        
        Args:
            param_values: Array of hyperparameter values (x-axis).
            train_scores: Array of training scores corresponding to param_values.
            val_scores: Array of validation scores corresponding to param_values.
            param_name: Name of the hyperparameter for axis label.
            log_scale: If True, use logarithmic scale for x-axis. Useful when
                      hyperparameter values span multiple orders of magnitude.
        
        Returns:
            Matplotlib Figure object containing the validation curve.
        
        Raises:
            ValueError: If param_values, train_scores, and val_scores have
                       different lengths.
        
        Example:
            >>> param_values = np.array([1, 10, 100, 1000])
            >>> train_scores = np.array([0.85, 0.90, 0.92, 0.93])
            >>> val_scores = np.array([0.82, 0.88, 0.87, 0.84])
            >>> generator = ValidationCurveGenerator()
            >>> fig = generator.generate(
            ...     param_values=param_values,
            ...     train_scores=train_scores,
            ...     val_scores=val_scores,
            ...     param_name='max_depth',
            ...     log_scale=False
            ... )
        """
        # Validate input lengths
        if not (len(param_values) == len(train_scores) == len(val_scores)):
            raise ValueError(
                f"All arrays must have the same length. Got param_values: {len(param_values)}, "
                f"train_scores: {len(train_scores)}, val_scores: {len(val_scores)}"
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
        
        # Plot training scores
        ax.plot(
            param_values,
            train_scores,
            marker='o',
            linestyle='-',
            linewidth=self.styler.style.line_width,
            markersize=self.styler.style.marker_size,
            color=train_color,
            label='Training Score'
        )
        
        # Plot validation scores
        ax.plot(
            param_values,
            val_scores,
            marker='s',
            linestyle='-',
            linewidth=self.styler.style.line_width,
            markersize=self.styler.style.marker_size,
            color=val_color,
            label='Validation Score'
        )
        
        # Apply logarithmic scale if requested
        if log_scale:
            ax.set_xscale('log')
        
        # Format axis labels and title
        self.styler.format_axis_labels(
            ax=ax,
            xlabel=param_name,
            ylabel='Score',
            title=f'Validation Curve: {param_name}'
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
