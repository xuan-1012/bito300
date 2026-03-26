"""Main ChartGenerator API class for model evaluation visualization.

This module provides the primary interface for generating all types of
model evaluation charts through a unified API.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, List
from matplotlib.figure import Figure

from .models import ChartStyle, BatchGenerationResult
from ..validation.input_validator import InputValidator
from ..core.metric_calculator import MetricCalculator
from ..styling.chart_styler import ChartStyler
from ..export.image_exporter import ImageExporter
from ..generators.validation_curve import ValidationCurveGenerator
from ..generators.learning_curve import LearningCurveGenerator
from ..generators.confusion_matrix import ConfusionMatrixGenerator
from ..generators.roc_curve import ROCCurveGenerator
from ..generators.precision_recall import PrecisionRecallCurveGenerator
from ..generators.threshold_analysis import ThresholdAnalysisGenerator
from ..generators.lift_curve import LiftCurveGenerator
from ..generators.model_comparison import ModelComparisonTableGenerator


class ChartGenerator:
    """Main API class for generating model evaluation charts.
    
    ChartGenerator provides a unified interface for creating all types of
    model evaluation visualizations. It handles input validation, metric
    calculation, chart generation, and optional export to image files.
    
    The class initializes all necessary components (validators, calculators,
    stylers, exporters, and specific chart generators) and provides methods
    for generating each chart type with consistent styling and error handling.
    
    Attributes:
        output_dir: Directory where charts will be saved.
        validator: InputValidator for data validation.
        calculator: MetricCalculator for metric computations.
        styler: ChartStyler for consistent visual styling.
        exporter: ImageExporter for saving charts to files.
        validation_curve_gen: Generator for validation curves.
        learning_curve_gen: Generator for learning curves.
        confusion_matrix_gen: Generator for confusion matrices.
        roc_curve_gen: Generator for ROC curves.
        pr_curve_gen: Generator for precision-recall curves.
        threshold_analysis_gen: Generator for threshold analysis.
        lift_curve_gen: Generator for lift curves.
        model_comparison_gen: Generator for model comparison tables.
    
    Example:
        >>> from model_evaluation_viz import ChartGenerator
        >>> 
        >>> # Create generator with default settings
        >>> generator = ChartGenerator(output_dir='charts')
        >>> 
        >>> # Generate ROC curve
        >>> fig = generator.generate_roc_curve(
        ...     y_true=y_true,
        ...     y_proba=y_proba,
        ...     save=True
        ... )
        >>> 
        >>> # Generate confusion matrix
        >>> fig = generator.generate_confusion_matrix(
        ...     y_true=y_true,
        ...     y_pred=y_pred,
        ...     class_labels=['Normal', 'Suspicious'],
        ...     save=True
        ... )
    """
    
    def __init__(
        self,
        output_dir: str = 'output',
        style: Optional[ChartStyle] = None
    ):
        """Initialize the ChartGenerator.
        
        Args:
            output_dir: Directory where charts will be saved. Created if it
                       doesn't exist. Defaults to 'output'.
            style: Optional ChartStyle for custom styling. If None, uses
                  default styling with colorblind-accessible palette.
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize core components
        self.validator = InputValidator()
        self.calculator = MetricCalculator()
        self.styler = ChartStyler(style)
        self.exporter = ImageExporter(output_dir)
        
        # Initialize all chart generators with consistent styling
        self.validation_curve_gen = ValidationCurveGenerator(self.styler)
        self.learning_curve_gen = LearningCurveGenerator(self.styler)
        self.confusion_matrix_gen = ConfusionMatrixGenerator(self.styler)
        self.roc_curve_gen = ROCCurveGenerator(self.styler)
        self.pr_curve_gen = PrecisionRecallCurveGenerator(self.styler)
        self.threshold_analysis_gen = ThresholdAnalysisGenerator(self.styler)
        self.lift_curve_gen = LiftCurveGenerator(self.styler)
        self.model_comparison_gen = ModelComparisonTableGenerator(self.styler)
    
    def generate_validation_curve(
        self,
        param_values,
        train_scores,
        val_scores,
        param_name: str,
        log_scale: bool = False,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate validation curve showing hyperparameter tuning results.
        
        Args:
            param_values: Array of hyperparameter values tested.
            train_scores: Array of training scores for each parameter value.
            val_scores: Array of validation scores for each parameter value.
            param_name: Name of the hyperparameter being tuned.
            log_scale: Whether to use logarithmic scale for x-axis.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the validation curve.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths or
                           invalid values.
        """
        # Validate inputs
        self.validator.validate_scores(train_scores, val_scores)
        
        # Generate chart
        fig = self.validation_curve_gen.generate(
            param_values=param_values,
            train_scores=train_scores,
            val_scores=val_scores,
            param_name=param_name,
            log_scale=log_scale
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('validation_curve')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_learning_curve(
        self,
        train_sizes,
        train_scores,
        val_scores,
        train_std=None,
        val_std=None,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate learning curve showing training set size analysis.
        
        Args:
            train_sizes: Array of training set sizes.
            train_scores: Array of training scores for each size.
            val_scores: Array of validation scores for each size.
            train_std: Optional array of training score standard deviations.
            val_std: Optional array of validation score standard deviations.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the learning curve.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths or
                           invalid values.
        """
        # Validate inputs
        self.validator.validate_scores(train_scores, val_scores)
        
        # Generate chart
        fig = self.learning_curve_gen.generate(
            train_sizes=train_sizes,
            train_scores=train_scores,
            val_scores=val_scores,
            train_std=train_std,
            val_std=val_std
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('learning_curve')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_confusion_matrix(
        self,
        y_true,
        y_pred,
        class_labels: Optional[List[str]] = None,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate confusion matrix heatmap.
        
        Args:
            y_true: Array of true labels.
            y_pred: Array of predicted labels.
            class_labels: Optional list of class label names.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the confusion matrix.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths or
                           invalid values.
        """
        # Validate inputs
        self.validator.validate_labels_and_predictions(y_true, y_pred)
        
        # Generate chart
        fig = self.confusion_matrix_gen.generate(
            y_true=y_true,
            y_pred=y_pred,
            class_labels=class_labels
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('confusion_matrix')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_roc_curve(
        self,
        y_true,
        y_proba,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate ROC curve with AUC score.
        
        Args:
            y_true: Array of true binary labels.
            y_proba: Array of predicted probabilities for positive class.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the ROC curve.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths,
                           non-binary labels, or invalid probabilities.
        """
        # Validate inputs
        self.validator.validate_labels_and_predictions(y_true, y_proba)
        self.validator.validate_binary_labels(y_true)
        self.validator.validate_probabilities(y_proba)
        
        # Generate chart
        fig = self.roc_curve_gen.generate(
            y_true=y_true,
            y_proba=y_proba
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('roc_curve')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_precision_recall_curve(
        self,
        y_true,
        y_proba,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate precision-recall curve with average precision.
        
        Args:
            y_true: Array of true binary labels.
            y_proba: Array of predicted probabilities for positive class.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the precision-recall curve.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths,
                           non-binary labels, or invalid probabilities.
        """
        # Validate inputs
        self.validator.validate_labels_and_predictions(y_true, y_proba)
        self.validator.validate_binary_labels(y_true)
        self.validator.validate_probabilities(y_proba)
        
        # Generate chart
        fig = self.pr_curve_gen.generate(
            y_true=y_true,
            y_proba=y_proba
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('precision_recall_curve')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_threshold_analysis(
        self,
        y_true,
        y_proba,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate threshold analysis plot for optimal threshold selection.
        
        Args:
            y_true: Array of true binary labels.
            y_proba: Array of predicted probabilities for positive class.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the threshold analysis.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths,
                           non-binary labels, or invalid probabilities.
        """
        # Validate inputs
        self.validator.validate_labels_and_predictions(y_true, y_proba)
        self.validator.validate_binary_labels(y_true)
        self.validator.validate_probabilities(y_proba)
        
        # Generate chart
        fig = self.threshold_analysis_gen.generate(
            y_true=y_true,
            y_proba=y_proba
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('threshold_analysis')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_lift_curve(
        self,
        y_true,
        y_proba,
        save: bool = False,
        filename: Optional[str] = None
    ) -> Figure:
        """Generate lift curve for ranking quality assessment.
        
        Args:
            y_true: Array of true binary labels.
            y_proba: Array of predicted probabilities for positive class.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
        
        Returns:
            Matplotlib Figure object containing the lift curve.
        
        Raises:
            ValidationError: If input arrays have mismatched lengths,
                           non-binary labels, or invalid probabilities.
        """
        # Validate inputs
        self.validator.validate_labels_and_predictions(y_true, y_proba)
        self.validator.validate_binary_labels(y_true)
        self.validator.validate_probabilities(y_proba)
        
        # Generate chart
        fig = self.lift_curve_gen.generate(
            y_true=y_true,
            y_proba=y_proba
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('lift_curve')
            self.exporter.export(fig, filename)
        
        return fig
    
    def generate_model_comparison(
        self,
        models_data: Dict[str, Dict[str, float]],
        save: bool = False,
        filename: Optional[str] = None,
        export_csv: bool = False
    ) -> Figure:
        """Generate model comparison table.
        
        Args:
            models_data: Dictionary mapping model names to their metrics.
                        Each model should have a dictionary of metric names
                        to values.
            save: Whether to save the chart to a file.
            filename: Optional custom filename. If None, auto-generates.
            export_csv: Whether to also export data as CSV file.
        
        Returns:
            Matplotlib Figure object containing the comparison table.
        
        Raises:
            ValidationError: If models_data is empty or has inconsistent
                           metric sets.
        """
        # Validate inputs
        self.validator.validate_model_comparison_data(models_data)
        
        # Generate chart
        fig = self.model_comparison_gen.generate(
            models_data=models_data
        )
        
        # Save if requested
        if save:
            if filename is None:
                filename = self.exporter.generate_filename('model_comparison')
            self.exporter.export(fig, filename)
            
            # Also export CSV if requested
            if export_csv:
                csv_filename = filename.replace('.png', '.csv')
                csv_path = os.path.join(self.output_dir, csv_filename)
                self.model_comparison_gen.export_to_csv(models_data, csv_path)
        
        return fig

    
    def batch_generate(
        self,
        y_true,
        y_pred,
        y_proba,
        class_labels: Optional[List[str]] = None,
        prefix: str = ""
    ) -> BatchGenerationResult:
        """Generate all applicable charts in batch mode.
        
        This method generates all classification charts that can be created
        from the provided data: confusion matrix, ROC curve, precision-recall
        curve, threshold analysis, and lift curve. All charts are saved to
        the output directory with consistent naming.
        
        The method is error-resilient: if one chart fails to generate, it
        logs the error and continues with the remaining charts. A summary
        report is generated listing all successful and failed charts.
        
        Args:
            y_true: Array of true binary labels.
            y_pred: Array of predicted labels.
            y_proba: Array of predicted probabilities for positive class.
            class_labels: Optional list of class label names for confusion matrix.
            prefix: Optional prefix for all generated filenames.
        
        Returns:
            BatchGenerationResult containing:
                - generated_charts: Dict mapping chart type to filepath
                - failed_charts: Dict mapping chart type to error message
                - output_directory: Path to output directory
                - timestamp: Generation timestamp
        
        Example:
            >>> generator = ChartGenerator(output_dir='charts')
            >>> result = generator.batch_generate(
            ...     y_true=y_true,
            ...     y_pred=y_pred,
            ...     y_proba=y_proba,
            ...     class_labels=['Normal', 'Suspicious'],
            ...     prefix='model_v1'
            ... )
            >>> print(result.get_summary())
        """
        # Initialize result
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result = BatchGenerationResult(
            output_directory=self.output_dir,
            timestamp=timestamp
        )
        
        # Configure logging
        logger = logging.getLogger(__name__)
        
        # Define charts to generate
        charts_to_generate = [
            ('confusion_matrix', lambda: self.generate_confusion_matrix(
                y_true=y_true,
                y_pred=y_pred,
                class_labels=class_labels,
                save=True,
                filename=f"{prefix}confusion_matrix_{timestamp}.png" if prefix else None
            )),
            ('roc_curve', lambda: self.generate_roc_curve(
                y_true=y_true,
                y_proba=y_proba,
                save=True,
                filename=f"{prefix}roc_curve_{timestamp}.png" if prefix else None
            )),
            ('precision_recall_curve', lambda: self.generate_precision_recall_curve(
                y_true=y_true,
                y_proba=y_proba,
                save=True,
                filename=f"{prefix}precision_recall_{timestamp}.png" if prefix else None
            )),
            ('threshold_analysis', lambda: self.generate_threshold_analysis(
                y_true=y_true,
                y_proba=y_proba,
                save=True,
                filename=f"{prefix}threshold_analysis_{timestamp}.png" if prefix else None
            )),
            ('lift_curve', lambda: self.generate_lift_curve(
                y_true=y_true,
                y_proba=y_proba,
                save=True,
                filename=f"{prefix}lift_curve_{timestamp}.png" if prefix else None
            ))
        ]
        
        # Generate each chart with error handling
        for chart_type, generate_func in charts_to_generate:
            try:
                generate_func()
                
                # Construct filepath
                if prefix:
                    filename = f"{prefix}{chart_type}_{timestamp}.png"
                else:
                    filename = f"{chart_type}_{timestamp}.png"
                filepath = os.path.join(self.output_dir, filename)
                
                result.generated_charts[chart_type] = filepath
                logger.info(f"Successfully generated {chart_type}")
                
            except Exception as e:
                error_msg = f"{type(e).__name__}: {str(e)}"
                result.failed_charts[chart_type] = error_msg
                logger.error(f"Failed to generate {chart_type}: {error_msg}")
        
        # Generate summary report
        summary_filename = f"{prefix}batch_summary_{timestamp}.txt" if prefix else f"batch_summary_{timestamp}.txt"
        summary_path = os.path.join(self.output_dir, summary_filename)
        
        try:
            with open(summary_path, 'w') as f:
                f.write(result.get_summary())
            logger.info(f"Summary report saved to {summary_path}")
        except Exception as e:
            logger.error(f"Failed to save summary report: {str(e)}")
        
        return result
