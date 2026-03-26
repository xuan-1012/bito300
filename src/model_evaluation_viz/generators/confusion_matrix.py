"""Confusion matrix generator for classification model evaluation."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Optional, List

from ..core.models import ChartStyle
from ..core.metric_calculator import MetricCalculator
from ..styling.chart_styler import ChartStyler


class ConfusionMatrixGenerator:
    """Generates confusion matrix heatmaps for classification models.
    
    Confusion matrices visualize the performance of classification models by
    showing the counts of true positives, false positives, true negatives,
    and false negatives. The matrix is displayed as a heatmap with color
    intensity representing counts, and numeric values shown within each cell.
    
    The generator creates a professional visualization with rows labeled as
    "Actual" and columns as "Predicted", includes class labels, and uses a
    clear color scheme suitable for presentations.
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
        calculator: MetricCalculator instance for computing confusion matrix.
    
    Example:
        >>> from model_evaluation_viz.generators.confusion_matrix import ConfusionMatrixGenerator
        >>> import numpy as np
        >>> 
        >>> # Create generator with default styling
        >>> generator = ConfusionMatrixGenerator()
        >>> 
        >>> # Generate confusion matrix
        >>> y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        >>> y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0])
        >>> fig = generator.generate(
        ...     y_true=y_true,
        ...     y_pred=y_pred,
        ...     class_labels=['Negative', 'Positive']
        ... )
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the ConfusionMatrixGenerator.
        
        Args:
            styler: Optional ChartStyler for custom styling. If None, uses
                   default ChartStyler with colorblind-accessible palette.
        """
        self.styler = styler or ChartStyler()
        self.calculator = MetricCalculator()
    
    def generate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        class_labels: Optional[List[str]] = None
    ) -> Figure:
        """Generate confusion matrix visualization.
        
        Creates a matplotlib figure showing the confusion matrix as a heatmap.
        The matrix displays counts of predictions for each true/predicted class
        combination. Rows represent actual classes, columns represent predicted
        classes.
        
        Args:
            y_true: Array of true labels.
            y_pred: Array of predicted labels.
            class_labels: Optional list of class label names. If None, uses
                         numeric labels from the unique values in y_true.
                         The order should match the sorted unique values.
        
        Returns:
            Matplotlib Figure object containing the confusion matrix heatmap.
        
        Raises:
            ValueError: If y_true and y_pred have different lengths, or if
                       class_labels length doesn't match number of classes.
        
        Example:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_pred = np.array([0, 1, 0, 0, 1])
            >>> generator = ConfusionMatrixGenerator()
            >>> fig = generator.generate(
            ...     y_true=y_true,
            ...     y_pred=y_pred,
            ...     class_labels=['Class 0', 'Class 1']
            ... )
        """
        # Validate input lengths
        if len(y_true) != len(y_pred):
            raise ValueError(
                f"y_true and y_pred must have the same length. "
                f"Got y_true: {len(y_true)}, y_pred: {len(y_pred)}"
            )
        
        # Calculate confusion matrix
        cm = self.calculator.calculate_confusion_matrix(y_true, y_pred)
        
        # Determine class labels
        unique_classes = np.unique(np.concatenate([y_true, y_pred]))
        n_classes = len(unique_classes)
        
        if class_labels is None:
            # Use numeric labels
            class_labels = [str(cls) for cls in unique_classes]
        else:
            # Validate provided class labels
            if len(class_labels) != n_classes:
                raise ValueError(
                    f"class_labels length ({len(class_labels)}) must match "
                    f"number of unique classes ({n_classes})"
                )
        
        # Create figure with configured size and DPI
        fig, ax = plt.subplots(
            figsize=self.styler.style.figure_size,
            dpi=self.styler.style.dpi
        )
        
        # Apply base styling
        self.styler.apply_base_style(ax)
        
        # Create heatmap using imshow
        # Use Blues colormap for professional appearance
        im = ax.imshow(cm, interpolation='nearest', cmap='Blues', aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label(
            'Count',
            fontsize=max(10, self.styler.style.font_size),
            fontfamily=self.styler.style.font_family
        )
        
        # Set tick positions and labels
        tick_marks = np.arange(n_classes)
        ax.set_xticks(tick_marks)
        ax.set_yticks(tick_marks)
        ax.set_xticklabels(class_labels, fontsize=max(10, self.styler.style.font_size))
        ax.set_yticklabels(class_labels, fontsize=max(10, self.styler.style.font_size))
        
        # Rotate x-axis labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', rotation_mode='anchor')
        
        # Add text annotations showing counts in each cell
        # Use white text for dark cells, black for light cells
        thresh = cm.max() / 2.0
        for i in range(n_classes):
            for j in range(n_classes):
                text_color = 'white' if cm[i, j] > thresh else 'black'
                ax.text(
                    j, i, format(cm[i, j], 'd'),
                    ha='center',
                    va='center',
                    color=text_color,
                    fontsize=max(10, self.styler.style.font_size),
                    fontfamily=self.styler.style.font_family
                )
        
        # Format axis labels and title
        self.styler.format_axis_labels(
            ax=ax,
            xlabel='Predicted',
            ylabel='Actual',
            title='Confusion Matrix'
        )
        
        # Adjust layout to prevent label cutoff
        fig.tight_layout()
        
        return fig

