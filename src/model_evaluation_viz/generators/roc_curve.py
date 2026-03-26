"""ROC curve generator for binary classification model evaluation."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional

from ..core.models import ChartStyle
from ..core.metric_calculator import MetricCalculator
from ..styling.chart_styler import ChartStyler


class ROCCurveGenerator:
    """Generates ROC curves with AUC scores for binary classification.
    
    ROC (Receiver Operating Characteristic) curves visualize the trade-off
    between True Positive Rate (TPR) and False Positive Rate (FPR) across
    different classification thresholds. The Area Under the Curve (AUC)
    provides a single metric summarizing the classifier's performance.
    
    The generator creates a professional visualization with:
    - ROC curve showing TPR vs FPR
    - AUC score displayed in the legend
    - Diagonal reference line representing random classifier performance
    - Clear axis labels and title
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
        calculator: MetricCalculator instance for computing ROC metrics.
    
    Example:
        >>> from model_evaluation_viz.generators.roc_curve import ROCCurveGenerator
        >>> import numpy as np
        >>> 
        >>> # Create generator with default styling
        >>> generator = ROCCurveGenerator()
        >>> 
        >>> # Generate ROC curve
        >>> y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85, 0.3, 0.75, 0.15])
        >>> fig = generator.generate(y_true=y_true, y_proba=y_proba)
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the ROCCurveGenerator.
        
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
        """Generate ROC curve visualization.
        
        Creates a matplotlib figure showing the ROC curve with AUC score.
        The curve plots True Positive Rate (sensitivity) against False
        Positive Rate (1 - specificity) for various classification thresholds.
        A diagonal reference line represents random classifier performance.
        
        Args:
            y_true: Array of true binary labels (0 or 1).
            y_proba: Array of predicted probabilities for the positive class.
                    Values should be in the range [0, 1].
        
        Returns:
            Matplotlib Figure object containing the ROC curve.
        
        Raises:
            ValueError: If y_true and y_proba have different lengths, or if
                       y_proba contains values outside [0, 1], or if y_true
                       doesn't contain exactly two unique values.
        
        Example:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.85])
            >>> generator = ROCCurveGenerator()
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
        
        # Calculate ROC curve metrics
        fpr, tpr, auc_score, thresholds = self.calculator.calculate_roc_curve(
            y_true, y_proba
        )
        
        # Create figure with configured size and DPI
        fig, ax = plt.subplots(
            figsize=self.styler.style.figure_size,
            dpi=self.styler.style.dpi
        )
        
        # Apply base styling
        self.styler.apply_base_style(ax)
        
        # Plot ROC curve
        ax.plot(
            fpr,
            tpr,
            color=self.styler.get_color(0),
            linewidth=self.styler.style.line_width,
            label=f'ROC Curve (AUC = {auc_score:.3f})'
        )
        
        # Plot diagonal reference line (random classifier)
        ax.plot(
            [0, 1],
            [0, 1],
            color='gray',
            linestyle='--',
            linewidth=self.styler.style.line_width * 0.8,
            label='Random Classifier'
        )
        
        # Set axis limits
        ax.set_xlim([0.0, 1.0])
        ax.set_ylim([0.0, 1.0])
        
        # Format axis labels and title
        self.styler.format_axis_labels(
            ax=ax,
            xlabel='False Positive Rate',
            ylabel='True Positive Rate',
            title='ROC Curve'
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
