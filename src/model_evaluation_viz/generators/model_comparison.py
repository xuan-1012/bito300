"""Model comparison table generator for evaluating multiple models."""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Dict, Optional, List

from ..core.models import ChartStyle
from ..styling.chart_styler import ChartStyler


class ModelComparisonTableGenerator:
    """Generates model comparison tables for evaluating multiple models.
    
    Model comparison tables visualize the performance of multiple model versions
    by displaying core metrics (Accuracy, Precision, Recall, F1 Score, AUC,
    Average Precision) in a clean tabular format. The table highlights the best
    value in each metric column to facilitate model selection.
    
    The generator creates a professional visualization with:
    - Models as rows, metrics as columns
    - Numeric values formatted to 4 decimal places
    - Best value in each column highlighted with bold text and background color
    - Clean table design suitable for presentations
    - Support for export as image or CSV
    
    Attributes:
        styler: ChartStyler instance for consistent visual styling.
    
    Example:
        >>> from model_evaluation_viz.generators.model_comparison import ModelComparisonTableGenerator
        >>> 
        >>> # Create generator with default styling
        >>> generator = ModelComparisonTableGenerator()
        >>> 
        >>> # Define model metrics
        >>> models_data = {
        ...     'Model_V1': {
        ...         'Accuracy': 0.8500,
        ...         'Precision': 0.8200,
        ...         'Recall': 0.8800,
        ...         'F1 Score': 0.8500,
        ...         'AUC': 0.9000,
        ...         'Average Precision': 0.8700
        ...     },
        ...     'Model_V2': {
        ...         'Accuracy': 0.8700,
        ...         'Precision': 0.8500,
        ...         'Recall': 0.8900,
        ...         'F1 Score': 0.8700,
        ...         'AUC': 0.9200,
        ...         'Average Precision': 0.8900
        ...     }
        ... }
        >>> fig = generator.generate(models_data=models_data)
        >>> plt.show()
    """
    
    def __init__(self, styler: Optional[ChartStyler] = None):
        """Initialize the ModelComparisonTableGenerator.
        
        Args:
            styler: Optional ChartStyler for custom styling. If None, uses
                   default ChartStyler with colorblind-accessible palette.
        """
        self.styler = styler or ChartStyler()
    
    def generate(
        self,
        models_data: Dict[str, Dict[str, float]]
    ) -> Figure:
        """Generate model comparison table visualization.
        
        Creates a matplotlib figure showing a comparison table with models as
        rows and metrics as columns. The best value in each metric column is
        highlighted with bold text and a background color.
        
        Args:
            models_data: Dictionary mapping model names to their metrics.
                        Each model should have a dictionary of metric names
                        to values. Example:
                        {
                            'Model_V1': {'Accuracy': 0.85, 'Precision': 0.82, ...},
                            'Model_V2': {'Accuracy': 0.87, 'Precision': 0.85, ...}
                        }
        
        Returns:
            Matplotlib Figure object containing the comparison table.
        
        Raises:
            ValueError: If models_data is empty, or if models have inconsistent
                       metric sets, or if any metric value is not numeric.
        
        Example:
            >>> models_data = {
            ...     'Model_V1': {'Accuracy': 0.85, 'AUC': 0.90},
            ...     'Model_V2': {'Accuracy': 0.87, 'AUC': 0.92}
            ... }
            >>> generator = ModelComparisonTableGenerator()
            >>> fig = generator.generate(models_data=models_data)
        """
        # Validate input
        if not models_data:
            raise ValueError("models_data cannot be empty")
        
        # Get model names and metrics
        model_names = list(models_data.keys())
        
        # Validate that all models have the same metrics
        first_model_metrics = set(models_data[model_names[0]].keys())
        for model_name in model_names[1:]:
            model_metrics = set(models_data[model_name].keys())
            if model_metrics != first_model_metrics:
                missing = first_model_metrics - model_metrics
                extra = model_metrics - first_model_metrics
                error_msg = f"All models must have the same metrics. Model '{model_name}' "
                if missing:
                    error_msg += f"is missing: {missing}"
                if extra:
                    error_msg += f"has extra: {extra}"
                raise ValueError(error_msg)
        
        # Define standard metric order (if present)
        standard_metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC', 'Average Precision']
        
        # Get metrics in standard order, then any additional metrics
        all_metrics = list(first_model_metrics)
        metric_names = []
        for metric in standard_metrics:
            if metric in all_metrics:
                metric_names.append(metric)
        for metric in all_metrics:
            if metric not in metric_names:
                metric_names.append(metric)
        
        # Validate that all values are numeric
        for model_name, metrics in models_data.items():
            for metric_name, value in metrics.items():
                if not isinstance(value, (int, float, np.number)):
                    raise ValueError(
                        f"All metric values must be numeric. "
                        f"Model '{model_name}', metric '{metric_name}' has type {type(value)}"
                    )
                if np.isnan(value) or np.isinf(value):
                    raise ValueError(
                        f"Metric values must be finite. "
                        f"Model '{model_name}', metric '{metric_name}' is {value}"
                    )
        
        # Build table data
        n_models = len(model_names)
        n_metrics = len(metric_names)
        
        # Create data matrix
        data_matrix = np.zeros((n_models, n_metrics))
        for i, model_name in enumerate(model_names):
            for j, metric_name in enumerate(metric_names):
                data_matrix[i, j] = models_data[model_name][metric_name]
        
        # Find best value in each column (maximum for all these metrics)
        best_indices = np.argmax(data_matrix, axis=0)
        
        # Create figure with appropriate size
        # Adjust figure size based on table dimensions
        fig_width = max(10, 2 + n_metrics * 1.5)
        fig_height = max(6, 2 + n_models * 0.6)
        
        fig, ax = plt.subplots(
            figsize=(fig_width, fig_height),
            dpi=self.styler.style.dpi
        )
        
        # Hide axes
        ax.axis('off')
        
        # Format cell data with 4 decimal places
        cell_text = []
        for i, model_name in enumerate(model_names):
            row = [model_name]
            for j, metric_name in enumerate(metric_names):
                value = data_matrix[i, j]
                row.append(f'{value:.4f}')
            cell_text.append(row)
        
        # Create table
        # Column labels include empty string for model name column
        col_labels = ['Model'] + metric_names
        
        table = ax.table(
            cellText=cell_text,
            colLabels=col_labels,
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        
        # Style the table
        table.auto_set_font_size(False)
        table.set_fontsize(max(10, self.styler.style.font_size))
        
        # Style header row
        for j in range(n_metrics + 1):
            cell = table[(0, j)]
            cell.set_facecolor('#4472C4')  # Professional blue
            cell.set_text_props(
                weight='bold',
                color='white',
                fontsize=max(10, self.styler.style.font_size),
                fontfamily=self.styler.style.font_family
            )
            cell.set_height(0.08)
        
        # Style data cells and highlight best values
        for i in range(n_models):
            # Model name column (first column)
            cell = table[(i + 1, 0)]
            cell.set_facecolor('#E7E6E6')  # Light gray for model names
            cell.set_text_props(
                weight='bold',
                fontsize=max(10, self.styler.style.font_size),
                fontfamily=self.styler.style.font_family
            )
            cell.set_height(0.06)
            
            # Metric columns
            for j in range(n_metrics):
                cell = table[(i + 1, j + 1)]
                
                # Highlight best value in each column
                if i == best_indices[j]:
                    cell.set_facecolor('#C6E0B4')  # Light green for best values
                    cell.set_text_props(
                        weight='bold',
                        fontsize=max(10, self.styler.style.font_size),
                        fontfamily=self.styler.style.font_family
                    )
                else:
                    cell.set_facecolor('white')
                    cell.set_text_props(
                        fontsize=max(10, self.styler.style.font_size),
                        fontfamily=self.styler.style.font_family
                    )
                
                cell.set_height(0.06)
        
        # Add title
        title_text = 'Model Comparison'
        fig.suptitle(
            title_text,
            fontsize=max(10, self.styler.style.title_font_size),
            fontfamily=self.styler.style.font_family,
            fontweight='bold',
            y=0.98
        )
        
        # Adjust layout
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        
        return fig
    
    def export_to_csv(
        self,
        models_data: Dict[str, Dict[str, float]],
        filepath: str
    ) -> None:
        """Export model comparison data to CSV file.
        
        Saves the model comparison data as a CSV file with models as rows
        and metrics as columns. Values are formatted to 4 decimal places.
        
        Args:
            models_data: Dictionary mapping model names to their metrics.
            filepath: Path where the CSV file should be saved.
        
        Raises:
            ValueError: If models_data is empty or has inconsistent metrics.
            IOError: If the file cannot be written.
        
        Example:
            >>> models_data = {
            ...     'Model_V1': {'Accuracy': 0.85, 'AUC': 0.90},
            ...     'Model_V2': {'Accuracy': 0.87, 'AUC': 0.92}
            ... }
            >>> generator = ModelComparisonTableGenerator()
            >>> generator.export_to_csv(models_data, 'comparison.csv')
        """
        # Validate input (reuse validation logic)
        if not models_data:
            raise ValueError("models_data cannot be empty")
        
        model_names = list(models_data.keys())
        first_model_metrics = set(models_data[model_names[0]].keys())
        
        for model_name in model_names[1:]:
            model_metrics = set(models_data[model_name].keys())
            if model_metrics != first_model_metrics:
                raise ValueError(
                    f"All models must have the same metrics. "
                    f"Model '{model_name}' has inconsistent metrics."
                )
        
        # Define standard metric order
        standard_metrics = ['Accuracy', 'Precision', 'Recall', 'F1 Score', 'AUC', 'Average Precision']
        all_metrics = list(first_model_metrics)
        metric_names = []
        for metric in standard_metrics:
            if metric in all_metrics:
                metric_names.append(metric)
        for metric in all_metrics:
            if metric not in metric_names:
                metric_names.append(metric)
        
        # Write CSV file
        try:
            with open(filepath, 'w') as f:
                # Write header
                f.write('Model,' + ','.join(metric_names) + '\n')
                
                # Write data rows
                for model_name in model_names:
                    row = [model_name]
                    for metric_name in metric_names:
                        value = models_data[model_name][metric_name]
                        row.append(f'{value:.4f}')
                    f.write(','.join(row) + '\n')
        except Exception as e:
            raise IOError(f"Failed to write CSV file to {filepath}: {str(e)}")
