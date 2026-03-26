# Design Document: Model Evaluation Visualization

## Overview

The Model Evaluation Visualization system provides a comprehensive suite of tools for evaluating and visualizing machine learning model performance. The system generates publication-quality charts and metrics for model assessment, including validation curves, learning curves, confusion matrices, ROC curves, precision-recall curves, threshold analysis, lift curves, and model comparison tables.

The system is designed as a Python library built on matplotlib and scikit-learn, providing both individual chart generation functions and batch processing capabilities. All charts are optimized for presentations and technical documentation with high-resolution output, professional styling, and clear visual design.

Key design principles:
- **Modularity**: Separate concerns for metric calculation, chart generation, and export
- **Extensibility**: Easy to add new chart types or metrics
- - **Usability**: Simple API with sensible defaults and comprehensive customization
- **Quality**: Publication-ready output with professional styling
- **Performance**: Efficient processing of large datasets with vectorized operations

## Architecture

The system follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────────────────┐
│                    Public API Layer                      │
│  (ChartGenerator, batch_generate, export functions)     │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                 Chart Generation Layer                   │
│  (ValidationCurveGenerator, ROCCurveGenerator, etc.)    │
└─────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────┬──────────────────────────────────┐
│  Metric Calculation  │     Styling & Configuration      │
│      Layer           │            Layer                  │
│  (MetricCalculator)  │  (ChartStyler, ColorPalette)     │
└──────────────────────┴──────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│                   Export Layer                           │
│              (ImageExporter, FileManager)                │
└─────────────────────────────────────────────────────────┘
```

### Component Responsibilities

1. **Public API Layer**: Provides user-facing functions with input validation and error handling
2. **Chart Generation Layer**: Implements specific chart types with matplotlib
3. **Metric Calculation Layer**: Computes evaluation metrics using vectorized operations
4. **Styling Layer**: Manages visual appearance and consistency across charts
5. **Export Layer**: Handles file I/O and format conversion

## Components and Interfaces

### 1. MetricCalculator

Responsible for calculating all evaluation metrics from labels and predictions.

```python
class MetricCalculator:
    """Calculates evaluation metrics for classification models."""
    
    @staticmethod
    def calculate_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Calculate confusion matrix from true and predicted labels."""
        pass
    
    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate accuracy, precision, recall, F1 score."""
        pass
    
    @staticmethod
    def calculate_roc_curve(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Calculate TPR, FPR, and AUC for ROC curve."""
        pass
    
    @staticmethod
    def calculate_precision_recall_curve(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """Calculate precision, recall, and average precision."""
        pass
    
    @staticmethod
    def calculate_threshold_metrics(y_true: np.ndarray, y_proba: np.ndarray, 
                                   thresholds: np.ndarray) -> Dict[str, np.ndarray]:
        """Calculate precision, recall, F1 for multiple thresholds."""
        pass
    
    @staticmethod
    def calculate_lift_curve(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate cumulative gains for lift curve."""
        pass
```

### 2. ChartStyler

Manages visual styling and configuration for all charts.

```python
@dataclass
class ChartStyle:
    """Configuration for chart appearance."""
    figure_size: Tuple[int, int] = (10, 6)
    dpi: int = 300
    font_family: str = 'sans-serif'
    font_size: int = 12
    title_font_size: int = 14
    line_width: float = 2.0
    grid: bool = True
    grid_alpha: float = 0.3
    color_palette: List[str] = None
    
class ChartStyler:
    """Applies consistent styling to matplotlib figures."""
    
    def __init__(self, style: ChartStyle = None):
        self.style = style or ChartStyle()
    
    def apply_base_style(self, ax: plt.Axes) -> None:
        """Apply base styling to axes."""
        pass
    
    def get_color(self, index: int) -> str:
        """Get color from palette by index."""
        pass
    
    def format_axis_labels(self, ax: plt.Axes, xlabel: str, ylabel: str, title: str) -> None:
        """Format axis labels and title."""
        pass
```

### 3. InputValidator

Validates input data before chart generation.

```python
class InputValidator:
    """Validates input data for chart generation."""
    
    @staticmethod
    def validate_labels_and_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """Validate that labels and predictions have same length."""
        pass
    
    @staticmethod
    def validate_binary_labels(y_true: np.ndarray) -> None:
        """Validate that labels contain exactly two unique values."""
        pass
    
    @staticmethod
    def validate_probabilities(y_proba: np.ndarray) -> None:
        """Validate that probabilities are in [0, 1] range."""
        pass
    
    @staticmethod
    def validate_scores(train_scores: np.ndarray, val_scores: np.ndarray) -> None:
        """Validate that training and validation scores have same length."""
        pass
    
    @staticmethod
    def validate_model_comparison_data(models_data: Dict[str, Dict[str, float]]) -> None:
        """Validate that all models have same metrics."""
        pass
```

### 4. Chart Generator Classes

Each chart type has a dedicated generator class:

```python
class ValidationCurveGenerator:
    """Generates validation curves for hyperparameter tuning."""
    
    def __init__(self, styler: ChartStyler = None):
        self.styler = styler or ChartStyler()
    
    def generate(self, param_values: np.ndarray, train_scores: np.ndarray, 
                val_scores: np.ndarray, param_name: str, 
                log_scale: bool = False) -> plt.Figure:
        """Generate validation curve chart."""
        pass

class LearningCurveGenerator:
    """Generates learning curves for training set size analysis."""
    
    def generate(self, train_sizes: np.ndarray, train_scores: np.ndarray,
                val_scores: np.ndarray, train_std: np.ndarray = None,
                val_std: np.ndarray = None) -> plt.Figure:
        """Generate learning curve chart."""
        pass

class ConfusionMatrixGenerator:
    """Generates confusion matrix heatmaps."""
    
    def generate(self, y_true: np.ndarray, y_pred: np.ndarray,
                class_labels: List[str] = None) -> plt.Figure:
        """Generate confusion matrix visualization."""
        pass

class ROCCurveGenerator:
    """Generates ROC curves with AUC scores."""
    
    def generate(self, y_true: np.ndarray, y_proba: np.ndarray) -> plt.Figure:
        """Generate ROC curve chart."""
        pass

class PrecisionRecallCurveGenerator:
    """Generates precision-recall curves."""
    
    def generate(self, y_true: np.ndarray, y_proba: np.ndarray) -> plt.Figure:
        """Generate precision-recall curve chart."""
        pass

class ThresholdAnalysisGenerator:
    """Generates threshold analysis plots."""
    
    def generate(self, y_true: np.ndarray, y_proba: np.ndarray) -> plt.Figure:
        """Generate threshold analysis chart."""
        pass

class LiftCurveGenerator:
    """Generates lift curves."""
    
    def generate(self, y_true: np.ndarray, y_proba: np.ndarray) -> plt.Figure:
        """Generate lift curve chart."""
        pass

class ModelComparisonTableGenerator:
    """Generates model comparison tables."""
    
    def generate(self, models_data: Dict[str, Dict[str, float]]) -> plt.Figure:
        """Generate model comparison table."""
        pass
```

### 5. ImageExporter

Handles exporting charts to various file formats.

```python
class ImageExporter:
    """Exports matplotlib figures to image files."""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, fig: plt.Figure, filename: str, 
              format: str = 'png', dpi: int = 300,
              transparent: bool = False) -> str:
        """Export figure to file and return file path."""
        pass
    
    def export_multiple_formats(self, fig: plt.Figure, base_filename: str,
                               formats: List[str] = ['png', 'svg']) -> List[str]:
        """Export figure to multiple formats."""
        pass
    
    def generate_filename(self, chart_type: str, timestamp: bool = True) -> str:
        """Generate descriptive filename for chart."""
        pass
```

### 6. ChartGenerator (Main API)

The main user-facing class that orchestrates chart generation.

```python
class ChartGenerator:
    """Main interface for generating evaluation charts."""
    
    def __init__(self, output_dir: str = "./output", style: ChartStyle = None):
        self.validator = InputValidator()
        self.calculator = MetricCalculator()
        self.styler = ChartStyler(style)
        self.exporter = ImageExporter(output_dir)
        
        # Initialize specific generators
        self.validation_curve_gen = ValidationCurveGenerator(self.styler)
        self.learning_curve_gen = LearningCurveGenerator(self.styler)
        self.confusion_matrix_gen = ConfusionMatrixGenerator(self.styler)
        self.roc_curve_gen = ROCCurveGenerator(self.styler)
        self.pr_curve_gen = PrecisionRecallCurveGenerator(self.styler)
        self.threshold_gen = ThresholdAnalysisGenerator(self.styler)
        self.lift_curve_gen = LiftCurveGenerator(self.styler)
        self.comparison_gen = ModelComparisonTableGenerator(self.styler)
    
    def generate_validation_curve(self, param_values: np.ndarray, 
                                  train_scores: np.ndarray,
                                  val_scores: np.ndarray, 
                                  param_name: str,
                                  save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save validation curve."""
        pass
    
    def generate_learning_curve(self, train_sizes: np.ndarray,
                               train_scores: np.ndarray,
                               val_scores: np.ndarray,
                               save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save learning curve."""
        pass
    
    def generate_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray,
                                 class_labels: List[str] = None,
                                 save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save confusion matrix."""
        pass
    
    def generate_roc_curve(self, y_true: np.ndarray, y_proba: np.ndarray,
                          save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save ROC curve."""
        pass
    
    def generate_precision_recall_curve(self, y_true: np.ndarray, y_proba: np.ndarray,
                                       save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save precision-recall curve."""
        pass
    
    def generate_threshold_analysis(self, y_true: np.ndarray, y_proba: np.ndarray,
                                   save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save threshold analysis plot."""
        pass
    
    def generate_lift_curve(self, y_true: np.ndarray, y_proba: np.ndarray,
                           save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save lift curve."""
        pass
    
    def generate_model_comparison(self, models_data: Dict[str, Dict[str, float]],
                                 save: bool = True, **kwargs) -> plt.Figure:
        """Generate and optionally save model comparison table."""
        pass
    
    def batch_generate(self, y_true: np.ndarray, y_pred: np.ndarray,
                      y_proba: np.ndarray = None) -> Dict[str, str]:
        """Generate all applicable charts and return file paths."""
        pass
```

## Data Models

### ChartStyle

Configuration object for chart appearance:

```python
@dataclass
class ChartStyle:
    """Configuration for chart visual appearance."""
    figure_size: Tuple[int, int] = (10, 6)
    dpi: int = 300
    font_family: str = 'sans-serif'
    font_size: int = 12
    title_font_size: int = 14
    line_width: float = 2.0
    marker_size: float = 6.0
    grid: bool = True
    grid_alpha: float = 0.3
    grid_style: str = '--'
    color_palette: List[str] = None  # Defaults to professional palette
    background_color: str = 'white'
    text_color: str = 'black'
```

### MetricResult

Container for calculated metrics:

```python
@dataclass
class MetricResult:
    """Container for evaluation metrics."""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            'accuracy': self.accuracy,
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score
        }

@dataclass
class ROCResult:
    """Container for ROC curve data."""
    fpr: np.ndarray
    tpr: np.ndarray
    auc: float
    thresholds: np.ndarray

@dataclass
class PrecisionRecallResult:
    """Container for precision-recall curve data."""
    precision: np.ndarray
    recall: np.ndarray
    average_precision: float
    thresholds: np.ndarray
```

### BatchGenerationResult

Result object for batch generation:

```python
@dataclass
class BatchGenerationResult:
    """Result of batch chart generation."""
    generated_charts: Dict[str, str]  # chart_type -> file_path
    failed_charts: Dict[str, str]  # chart_type -> error_message
    output_directory: str
    timestamp: str
    
    def get_summary(self) -> str:
        """Generate summary report."""
        pass
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

Before defining the correctness properties, I'll analyze each acceptance criterion to determine testability.


### Property 1: Chart Completeness

*For any* generated chart, the figure should contain all required elements: axis labels (xlabel and ylabel), a title, and a legend when multiple data series are present.

**Validates: Requirements 1.4, 1.5, 2.5, 2.6, 4.5, 5.5, 6.4, 6.6, 7.5**

### Property 2: High-Resolution Export

*For any* chart exported to a raster format (PNG, JPEG), the saved image file should have a resolution of at least 300 DPI and the file should exist at the specified path with non-zero size.

**Validates: Requirements 1.6, 2.7, 3.7, 4.7, 5.7, 6.7, 7.7, 9.4**

### Property 3: Multi-Curve Color Distinction

*For any* chart displaying multiple data series (training vs validation, multiple metrics), each series should be rendered with a distinct color to ensure visual differentiation.

**Validates: Requirements 1.3, 2.3, 6.3**

### Property 4: Validation Curve Axis Mapping

*For any* validation curve with hyperparameter values and scores, the x-axis data should match the hyperparameter values and the y-axis data should match the score values.

**Validates: Requirements 1.2**

### Property 5: Logarithmic Scale Support

*For any* validation curve where log_scale is enabled, the x-axis should use a logarithmic scale.

**Validates: Requirements 1.7**

### Property 6: Learning Curve Variance Visualization

*For any* learning curve where standard deviation arrays are provided, the figure should contain filled polygon regions representing the variance bands around the mean scores.

**Validates: Requirements 2.4**

### Property 7: Learning Curve Axis Mapping

*For any* learning curve with training sizes and scores, the x-axis data should match the training sizes and the y-axis data should match the score values.

**Validates: Requirements 2.2**

### Property 8: Confusion Matrix Heatmap Values

*For any* confusion matrix generated from true and predicted labels, the heatmap cell values should match the calculated TP, FP, TN, FN counts.

**Validates: Requirements 3.2, 3.3**

### Property 9: Confusion Matrix Class Labels

*For any* confusion matrix with provided class labels, the tick labels on both axes should match the provided class labels in the correct order.

**Validates: Requirements 3.5**

### Property 10: ROC Curve Axis Mapping

*For any* ROC curve, the x-axis data should represent False Positive Rate and the y-axis data should represent True Positive Rate, both ranging from 0 to 1.

**Validates: Requirements 4.2**

### Property 11: ROC Curve AUC Display

*For any* ROC curve, the legend or title should contain the text "AUC" followed by a numeric value between 0 and 1 formatted to a reasonable precision.

**Validates: Requirements 4.3**

### Property 12: ROC Curve Diagonal Reference

*For any* ROC curve, the figure should contain a diagonal reference line from (0,0) to (1,1) representing random classifier performance.

**Validates: Requirements 4.4**

### Property 13: Precision-Recall Curve Axis Mapping

*For any* precision-recall curve, the x-axis data should represent Recall and the y-axis data should represent Precision, both ranging from 0 to 1.

**Validates: Requirements 5.2**

### Property 14: Precision-Recall Average Precision Display

*For any* precision-recall curve, the legend or title should contain the text "AP" or "Average Precision" followed by a numeric value between 0 and 1.

**Validates: Requirements 5.3**

### Property 15: Precision-Recall Baseline Reference

*For any* precision-recall curve, the figure should contain a horizontal reference line representing the baseline precision (proportion of positive class).

**Validates: Requirements 5.4**

### Property 16: Threshold Analysis Axis Mapping

*For any* threshold analysis plot, the x-axis data should represent threshold values ranging from 0 to 1, and the y-axis should represent metric values.

**Validates: Requirements 6.2**

### Property 17: Threshold Analysis Optimal Marking

*For any* threshold analysis plot, the figure should contain a vertical line or annotation marking the threshold value that maximizes the F1 score.

**Validates: Requirements 6.5**

### Property 18: Lift Curve Axis Ranges

*For any* lift curve, both the x-axis (percentage of samples) and y-axis (cumulative percentage of positives) should range from 0 to 100 or 0 to 1, representing percentages.

**Validates: Requirements 7.2**

### Property 19: Lift Curve Reference Line

*For any* lift curve, the figure should contain a diagonal reference line representing random selection performance.

**Validates: Requirements 7.3**

### Property 20: Lift Curve Percentile Annotations

*For any* lift curve, the figure should display lift values at specific percentiles either as annotations on the chart or in the legend.

**Validates: Requirements 7.4**

### Property 21: Model Comparison Table Structure

*For any* model comparison table with N models and M metrics, the table should have N rows (one per model) and M columns (one per metric), with proper row and column labels.

**Validates: Requirements 8.1, 8.5**

### Property 22: Model Comparison Metric Inclusion

*For any* model comparison table, the column headers should include the standard metrics: Accuracy, Precision, Recall, F1 Score, AUC, and Average Precision.

**Validates: Requirements 8.2**

### Property 23: Model Comparison Number Formatting

*For any* model comparison table, all numeric metric values should be formatted to exactly 4 decimal places.

**Validates: Requirements 8.3**

### Property 24: Model Comparison Best Value Highlighting

*For any* model comparison table, the best (maximum) value in each metric column should have distinct visual styling (color, bold, or background) to highlight it.

**Validates: Requirements 8.4**

### Property 25: Multi-Format Export Support

*For any* chart, the image exporter should successfully save the chart in PNG, JPEG, and SVG formats when requested, with each file existing at the expected path.

**Validates: Requirements 9.1, 9.2, 9.3**

### Property 26: PNG Transparency Support

*For any* chart exported to PNG format with transparent=True, the saved image should have a transparent background (alpha channel).

**Validates: Requirements 9.1**

### Property 27: Custom Dimensions Support

*For any* chart exported with custom width and height specifications, the resulting figure should have dimensions matching the specified values.

**Validates: Requirements 9.5**

### Property 28: Descriptive Filename Generation

*For any* exported chart, the filename should contain the chart type identifier and a timestamp, making it unique and descriptive.

**Validates: Requirements 9.6**

### Property 29: Output Directory Consistency

*For any* set of charts generated in a single session, all exported files should be saved to the same designated output directory.

**Validates: Requirements 9.7**

### Property 30: Consistent Color Palette

*For any* set of charts generated with the same ChartGenerator instance, all charts should use colors from the same color palette, ensuring visual consistency.

**Validates: Requirements 10.1**

### Property 31: Minimum Font Size

*For any* generated chart, all text elements (labels, titles, tick labels, legend) should have a font size of at least 10 points to ensure readability.

**Validates: Requirements 10.2**

### Property 32: Grid Line Presence

*For any* generated chart where grid is enabled (default), the axes should display grid lines to improve readability.

**Validates: Requirements 10.3**

### Property 33: Minimum Line Width

*For any* generated chart, all plotted lines should have a line width of at least 1.0 points to ensure visibility.

**Validates: Requirements 10.4**

### Property 34: Anti-Aliasing Enabled

*For any* generated chart, matplotlib's anti-aliasing should be enabled to ensure smooth rendering of all chart elements.

**Validates: Requirements 10.7**

### Property 35: Array Length Validation

*For any* chart generation function receiving paired arrays (y_true and y_pred, train_scores and val_scores), the function should raise a descriptive ValueError if the arrays have different lengths.

**Validates: Requirements 12.1, 12.4, 12.5**

### Property 36: Binary Label Validation

*For any* binary classification chart (ROC, Precision-Recall), the function should raise a descriptive ValueError if the true labels contain more or fewer than two unique values.

**Validates: Requirements 12.2, 12.5**

### Property 37: Probability Range Validation

*For any* chart generation function receiving predicted probabilities, the function should raise a descriptive ValueError if any probability value is outside the range [0, 1].

**Validates: Requirements 12.3, 12.5**

### Property 38: Numeric Value Validation

*For any* chart generation function receiving hyperparameter values or other numeric inputs, the function should raise a descriptive TypeError if any value is not numeric.

**Validates: Requirements 12.6, 12.5**

### Property 39: Metric Consistency Validation

*For any* model comparison table generation, the function should raise a descriptive ValueError if different models have different sets of metrics.

**Validates: Requirements 12.7, 12.5**

### Property 40: Batch Generation Completeness

*For any* batch generation request with true labels, predicted labels, and predicted probabilities, the system should generate at least the four core charts: Confusion Matrix, ROC Curve, Precision-Recall Curve, and Threshold Analysis Plot.

**Validates: Requirements 13.1, 13.2**

### Property 41: Batch Generation Directory Consistency

*For any* batch generation operation, all generated chart files should be saved to the same output directory.

**Validates: Requirements 13.3**

### Property 42: Batch Generation Naming Convention

*For any* batch generation operation, all generated filenames should follow a consistent naming pattern (e.g., prefix_charttype_timestamp.ext).

**Validates: Requirements 13.4**

### Property 43: Batch Generation Return Value

*For any* batch generation operation, the function should return a dictionary or list mapping chart types to their file paths for all successfully generated charts.

**Validates: Requirements 13.5**

### Property 44: Batch Generation Error Resilience

*For any* batch generation operation where one chart fails to generate, the system should continue generating the remaining charts and include error information in the result.

**Validates: Requirements 13.6**

### Property 45: Batch Generation Summary Report

*For any* completed batch generation operation, the system should return or create a summary report listing all generated charts, their file paths, and any errors encountered.

**Validates: Requirements 13.7**

### Property 46: Custom Color Palette Application

*For any* chart generated with a custom color palette specified, the chart should use colors from the specified palette rather than the default palette.

**Validates: Requirements 14.1**

### Property 47: Custom Font Application

*For any* chart generated with custom font family and size specified, all text elements should use the specified font properties.

**Validates: Requirements 14.2**

### Property 48: Custom Figure Size Application

*For any* chart generated with custom figure size specified, the resulting figure should have the specified width and height.

**Validates: Requirements 14.3**

### Property 49: Grid Toggle Functionality

*For any* chart generated with grid explicitly disabled, the axes should not display grid lines.

**Validates: Requirements 14.4**

### Property 50: Custom Axis Limits Application

*For any* chart generated with custom axis limits specified, the axes should have the specified minimum and maximum values.

**Validates: Requirements 14.5**

### Property 51: Custom Annotation Support

*For any* chart generated with custom annotations specified, the figure should contain text objects at the specified positions with the specified text content.

**Validates: Requirements 14.6**

### Property 52: Default Value Fallback

*For any* chart generated without custom styling options, the system should successfully generate the chart using default values for all styling parameters.

**Validates: Requirements 14.7**

### Property 53: Docstring Completeness

*For any* public function or class in the system, the object should have a non-empty docstring containing parameter descriptions and return value descriptions.

**Validates: Requirements 15.1, 15.2, 15.7**

### Property 54: Single Chart Performance

*For any* single chart generation with up to 10,000 data points, the operation should complete in less than 2 seconds.

**Validates: Requirements 16.1**

### Property 55: Batch Generation Performance

*For any* batch generation operation with up to 10,000 data points, all charts should be generated in less than 10 seconds total.

**Validates: Requirements 16.2**

### Property 56: Calculation Efficiency

*For any* batch generation operation using the same input data, metric calculations (confusion matrix, ROC curve data, etc.) should be performed only once and reused across multiple charts.

**Validates: Requirements 16.4**

### Property 57: Memory Management

*For any* sequence of 100 chart generation operations, the memory usage should not grow unboundedly, indicating proper resource cleanup after each operation.

**Validates: Requirements 16.6**

### Property 58: Progress Indication

*For any* batch generation operation or operation with large datasets, the system should provide progress feedback through callbacks or progress indicators.

**Validates: Requirements 16.7**


## Error Handling

The system implements comprehensive error handling at multiple layers:

### Input Validation Errors

All chart generation functions validate inputs before processing:

```python
class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass

class ChartGenerationError(Exception):
    """Raised when chart generation fails."""
    pass
```

**Validation Error Scenarios:**

1. **Array Length Mismatch**: When y_true and y_pred have different lengths
   - Error: `ValidationError("Arrays must have the same length: y_true has {len1}, y_pred has {len2}")`

2. **Invalid Binary Labels**: When binary classification requires exactly 2 unique values
   - Error: `ValidationError("Binary classification requires exactly 2 unique label values, found {n}")`

3. **Probability Out of Range**: When probabilities are not in [0, 1]
   - Error: `ValidationError("Probabilities must be in range [0, 1], found values in range [{min}, {max}]")`

4. **Non-Numeric Values**: When numeric arrays contain non-numeric values
   - Error: `TypeError("All values must be numeric, found type {type}")`

5. **Inconsistent Metrics**: When models in comparison have different metric sets
   - Error: `ValidationError("All models must have the same metrics. Model '{name}' is missing: {missing}")`

### Metric Calculation Errors

Metric calculations handle edge cases gracefully:

1. **Division by Zero**: When precision/recall calculations encounter zero denominators
   - Behavior: Return `np.nan` for that metric
   - Warning: Log warning message indicating which metric returned NaN

2. **Empty Arrays**: When input arrays are empty
   - Error: `ValidationError("Input arrays cannot be empty")`

3. **All Same Class**: When all predictions are the same class
   - Behavior: Calculate metrics normally (some may be 0 or undefined)
   - Warning: Log warning about potential data quality issue

### File I/O Errors

Export operations handle file system errors:

1. **Directory Creation Failure**: When output directory cannot be created
   - Error: `IOError("Failed to create output directory: {path}")`

2. **File Write Failure**: When chart cannot be saved
   - Error: `IOError("Failed to save chart to {path}: {reason}")`

3. **Insufficient Permissions**: When lacking write permissions
   - Error: `PermissionError("No write permission for directory: {path}")`

### Batch Generation Error Handling

Batch operations are resilient to individual failures:

```python
def batch_generate(self, y_true, y_pred, y_proba=None):
    results = {
        'generated': {},
        'failed': {}
    }
    
    for chart_type, generator_func in self.chart_generators.items():
        try:
            filepath = generator_func(y_true, y_pred, y_proba)
            results['generated'][chart_type] = filepath
        except Exception as e:
            logger.error(f"Failed to generate {chart_type}: {str(e)}")
            results['failed'][chart_type] = str(e)
            # Continue with next chart
    
    return BatchGenerationResult(**results)
```

### Matplotlib Errors

Handle matplotlib-specific issues:

1. **Figure Creation Failure**: When matplotlib cannot create figure
   - Error: `ChartGenerationError("Failed to create matplotlib figure")`

2. **Rendering Errors**: When chart rendering fails
   - Error: `ChartGenerationError("Failed to render chart: {reason}")`

3. **Backend Issues**: When matplotlib backend is not available
   - Error: `RuntimeError("Matplotlib backend not available. Install GUI backend or use 'Agg'")`

### Error Recovery Strategies

1. **Graceful Degradation**: If optional features fail (e.g., variance bands), generate chart without them
2. **Logging**: All errors are logged with full context for debugging
3. **User Feedback**: Error messages are descriptive and actionable
4. **Cleanup**: Resources (figures, file handles) are cleaned up even when errors occur using context managers

## Testing Strategy

The system employs a dual testing approach combining unit tests and property-based tests for comprehensive coverage.

### Unit Testing

Unit tests focus on specific examples, edge cases, and integration points:

**Test Organization:**
```
tests/
├── unit/
│   ├── test_metric_calculator.py
│   ├── test_chart_generators.py
│   ├── test_input_validator.py
│   ├── test_image_exporter.py
│   ├── test_chart_styler.py
│   └── test_integration.py
├── property/
│   ├── test_chart_properties.py
│   ├── test_metric_properties.py
│   ├── test_validation_properties.py
│   └── test_export_properties.py
└── fixtures/
    ├── sample_data.py
    └── expected_outputs/
```

**Unit Test Coverage:**

1. **Metric Calculations** (test_metric_calculator.py):
   - Test accuracy calculation with known inputs
   - Test precision/recall with known confusion matrix
   - Test F1 score calculation
   - Test AUC calculation with known ROC curve
   - Test average precision calculation
   - Test division by zero handling (edge case)
   - Test empty array handling (edge case)

2. **Chart Generation** (test_chart_generators.py):
   - Test each chart type generates without errors
   - Test chart contains expected elements (legend, labels, title)
   - Test specific examples (e.g., perfect classifier ROC curve)
   - Test edge cases (single data point, all same class)

3. **Input Validation** (test_input_validator.py):
   - Test length mismatch detection
   - Test binary label validation
   - Test probability range validation
   - Test numeric type validation
   - Test error message content

4. **Image Export** (test_image_exporter.py):
   - Test PNG export creates file
   - Test JPEG export creates file
   - Test SVG export creates file
   - Test transparent PNG option
   - Test custom dimensions
   - Test filename generation

5. **Integration Tests** (test_integration.py):
   - Test end-to-end chart generation and export
   - Test batch generation workflow
   - Test custom styling application
   - Test error recovery in batch mode

### Property-Based Testing

Property tests verify universal properties across randomized inputs using Hypothesis:

**Configuration:**
```python
from hypothesis import given, settings, strategies as st

# Configure for thorough testing
@settings(max_examples=100, deadline=None)
```

**Property Test Coverage:**

1. **Chart Completeness Properties** (test_chart_properties.py):

```python
@given(
    y_true=st.lists(st.integers(0, 1), min_size=10, max_size=1000),
    y_proba=st.lists(st.floats(0, 1), min_size=10, max_size=1000)
)
@settings(max_examples=100)
def test_roc_curve_completeness(y_true, y_proba):
    """
    Feature: model-evaluation-visualization, Property 1: Chart Completeness
    For any generated ROC curve, the figure should contain xlabel, ylabel, title, and legend.
    """
    # Ensure same length
    assume(len(y_true) == len(y_proba))
    assume(len(set(y_true)) == 2)  # Binary labels
    
    generator = ChartGenerator()
    fig = generator.generate_roc_curve(
        np.array(y_true), 
        np.array(y_proba), 
        save=False
    )
    
    ax = fig.axes[0]
    assert ax.get_xlabel() != ""
    assert ax.get_ylabel() != ""
    assert ax.get_title() != ""
    assert ax.get_legend() is not None
    
    plt.close(fig)
```

2. **Validation Properties** (test_validation_properties.py):

```python
@given(
    y_true=st.lists(st.integers(0, 1), min_size=10, max_size=100),
    y_pred=st.lists(st.integers(0, 1), min_size=10, max_size=100)
)
@settings(max_examples=100)
def test_array_length_validation(y_true, y_pred):
    """
    Feature: model-evaluation-visualization, Property 35: Array Length Validation
    For any paired arrays with different lengths, should raise ValueError.
    """
    assume(len(y_true) != len(y_pred))
    
    generator = ChartGenerator()
    with pytest.raises(ValidationError, match="same length"):
        generator.generate_confusion_matrix(
            np.array(y_true), 
            np.array(y_pred)
        )
```

3. **Metric Properties** (test_metric_properties.py):

```python
@given(
    y_true=st.lists(st.integers(0, 1), min_size=10, max_size=1000),
    y_pred=st.lists(st.integers(0, 1), min_size=10, max_size=1000)
)
@settings(max_examples=100)
def test_accuracy_range(y_true, y_pred):
    """
    Feature: model-evaluation-visualization, Property: Accuracy in [0,1]
    For any true and predicted labels, accuracy should be between 0 and 1.
    """
    assume(len(y_true) == len(y_pred))
    
    calculator = MetricCalculator()
    metrics = calculator.calculate_classification_metrics(
        np.array(y_true), 
        np.array(y_pred)
    )
    
    assert 0 <= metrics['accuracy'] <= 1
```

4. **Export Properties** (test_export_properties.py):

```python
@given(
    chart_type=st.sampled_from(['roc', 'pr', 'confusion', 'threshold']),
    format=st.sampled_from(['png', 'jpg', 'svg'])
)
@settings(max_examples=100)
def test_export_creates_file(chart_type, format, tmp_path):
    """
    Feature: model-evaluation-visualization, Property 2: High-Resolution Export
    For any chart and format, export should create a file at the specified path.
    """
    # Generate sample data
    y_true = np.random.randint(0, 2, 100)
    y_proba = np.random.random(100)
    
    generator = ChartGenerator(output_dir=str(tmp_path))
    
    # Generate appropriate chart
    if chart_type == 'roc':
        fig = generator.generate_roc_curve(y_true, y_proba, save=False)
    # ... other chart types
    
    # Export
    filepath = generator.exporter.export(fig, f"test_{chart_type}", format=format)
    
    assert Path(filepath).exists()
    assert Path(filepath).stat().st_size > 0
    
    plt.close(fig)
```

5. **Styling Properties** (test_chart_properties.py):

```python
@given(
    colors=st.lists(
        st.text(alphabet='0123456789ABCDEF', min_size=6, max_size=6),
        min_size=3,
        max_size=10,
        unique=True
    )
)
@settings(max_examples=100)
def test_custom_color_palette(colors):
    """
    Feature: model-evaluation-visualization, Property 46: Custom Color Palette Application
    For any custom color palette, charts should use colors from that palette.
    """
    color_palette = ['#' + c for c in colors]
    style = ChartStyle(color_palette=color_palette)
    generator = ChartGenerator(style=style)
    
    y_true = np.random.randint(0, 2, 100)
    y_proba = np.random.random(100)
    
    fig = generator.generate_threshold_analysis(y_true, y_proba, save=False)
    
    # Check that lines use colors from palette
    ax = fig.axes[0]
    lines = ax.get_lines()
    for i, line in enumerate(lines[:len(color_palette)]):
        assert line.get_color() in color_palette
    
    plt.close(fig)
```

### Test Data Strategy

1. **Synthetic Data Generation**:
   - Use numpy.random for generating test data
   - Use Hypothesis strategies for property tests
   - Create fixtures for common test scenarios

2. **Known Ground Truth**:
   - Perfect classifier (all correct predictions)
   - Random classifier (50% accuracy)
   - Specific confusion matrices with known metrics

3. **Edge Cases**:
   - Single data point
   - All same class
   - Perfectly balanced classes
   - Highly imbalanced classes (99:1 ratio)
   - Empty arrays (should error)

### Performance Testing

Performance tests verify timing requirements:

```python
def test_single_chart_performance():
    """Verify single chart generation completes in < 2 seconds."""
    y_true = np.random.randint(0, 2, 10000)
    y_proba = np.random.random(10000)
    
    generator = ChartGenerator()
    
    start = time.time()
    fig = generator.generate_roc_curve(y_true, y_proba, save=False)
    elapsed = time.time() - start
    
    assert elapsed < 2.0, f"Chart generation took {elapsed:.2f}s, expected < 2s"
    plt.close(fig)

def test_batch_generation_performance():
    """Verify batch generation completes in < 10 seconds."""
    y_true = np.random.randint(0, 2, 10000)
    y_pred = np.random.randint(0, 2, 10000)
    y_proba = np.random.random(10000)
    
    generator = ChartGenerator()
    
    start = time.time()
    results = generator.batch_generate(y_true, y_pred, y_proba)
    elapsed = time.time() - start
    
    assert elapsed < 10.0, f"Batch generation took {elapsed:.2f}s, expected < 10s"
```

### Testing Tools and Libraries

- **pytest**: Test framework and runner
- **Hypothesis**: Property-based testing library (minimum 100 iterations per test)
- **pytest-cov**: Code coverage measurement
- **numpy.testing**: Numerical assertion helpers
- **matplotlib.testing**: Chart comparison utilities
- **pytest-mock**: Mocking for external dependencies

### Coverage Goals

- **Line Coverage**: Minimum 90%
- **Branch Coverage**: Minimum 85%
- **Property Test Iterations**: Minimum 100 per property
- **Critical Paths**: 100% coverage (metric calculations, validation, export)

### Continuous Integration

Tests run automatically on:
- Every commit (fast unit tests)
- Pull requests (full test suite including property tests)
- Nightly builds (extended property tests with 1000 iterations)


## Implementation Notes

### Technology Stack

**Core Dependencies:**
- **Python**: 3.8+
- **NumPy**: 1.20+ (vectorized operations, array handling)
- **Matplotlib**: 3.5+ (chart generation and rendering)
- **scikit-learn**: 1.0+ (metric calculations, curve generation)

**Development Dependencies:**
- **pytest**: 7.0+ (testing framework)
- **hypothesis**: 6.0+ (property-based testing)
- **pytest-cov**: 3.0+ (coverage reporting)

**Optional Dependencies:**
- **Pillow**: For advanced image processing
- **pandas**: For model comparison table export to CSV

### Module Structure

```
model_evaluation_viz/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── chart_generator.py      # Main ChartGenerator class
│   ├── metric_calculator.py    # MetricCalculator class
│   └── models.py                # Data models (ChartStyle, MetricResult, etc.)
├── generators/
│   ├── __init__.py
│   ├── validation_curve.py
│   ├── learning_curve.py
│   ├── confusion_matrix.py
│   ├── roc_curve.py
│   ├── precision_recall.py
│   ├── threshold_analysis.py
│   ├── lift_curve.py
│   └── model_comparison.py
├── styling/
│   ├── __init__.py
│   ├── chart_styler.py
│   └── color_palettes.py
├── validation/
│   ├── __init__.py
│   └── input_validator.py
├── export/
│   ├── __init__.py
│   └── image_exporter.py
└── utils/
    ├── __init__.py
    └── helpers.py
```

### Key Implementation Considerations

1. **Memory Efficiency**:
   - Use `plt.close(fig)` after saving to release memory
   - Implement context managers for figure lifecycle
   - Avoid storing large arrays unnecessarily

2. **Vectorization**:
   - Use NumPy vectorized operations for all metric calculations
   - Avoid Python loops over large arrays
   - Leverage scikit-learn's optimized implementations

3. **Matplotlib Best Practices**:
   - Use `plt.subplots()` for figure creation
   - Apply `fig.tight_layout()` to prevent label overlap
   - Set DPI at figure creation: `plt.figure(dpi=300)`
   - Use appropriate backends (Agg for non-interactive)

4. **Thread Safety**:
   - Matplotlib is not thread-safe; use locks if multi-threading
   - Consider using separate processes for parallel chart generation

5. **Extensibility**:
   - Each chart generator is a separate class
   - New chart types can be added without modifying existing code
   - Plugin architecture for custom chart types

### Default Color Palette

Professional color palette optimized for presentations and colorblind accessibility:

```python
DEFAULT_PALETTE = [
    '#1f77b4',  # Blue
    '#ff7f0e',  # Orange
    '#2ca02c',  # Green
    '#d62728',  # Red
    '#9467bd',  # Purple
    '#8c564b',  # Brown
    '#e377c2',  # Pink
    '#7f7f7f',  # Gray
    '#bcbd22',  # Olive
    '#17becf'   # Cyan
]
```

This palette is:
- Distinguishable in color and grayscale
- Accessible for common color vision deficiencies
- Professional appearance for business presentations

### Performance Optimization Strategies

1. **Lazy Calculation**:
   - Calculate metrics only when needed
   - Cache calculated metrics for reuse in batch mode

2. **Efficient File I/O**:
   - Use buffered I/O for file operations
   - Batch file writes when possible

3. **Smart Defaults**:
   - Use reasonable default figure sizes (10x6 inches)
   - Default DPI of 300 balances quality and file size

4. **Progress Reporting**:
   - Implement callback-based progress reporting
   - Use tqdm for progress bars in batch operations

### Example Usage

```python
from model_evaluation_viz import ChartGenerator, ChartStyle

# Basic usage with defaults
generator = ChartGenerator(output_dir='./charts')

# Generate individual charts
fig = generator.generate_roc_curve(y_true, y_proba)
fig = generator.generate_confusion_matrix(y_true, y_pred)

# Batch generation
results = generator.batch_generate(y_true, y_pred, y_proba)
print(f"Generated {len(results.generated_charts)} charts")
print(f"Failed: {len(results.failed_charts)} charts")

# Custom styling
custom_style = ChartStyle(
    figure_size=(12, 8),
    dpi=300,
    font_size=14,
    color_palette=['#FF6B6B', '#4ECDC4', '#45B7D1']
)
generator = ChartGenerator(output_dir='./charts', style=custom_style)

# Model comparison
models_data = {
    'Model_V1': {'accuracy': 0.85, 'precision': 0.82, 'recall': 0.88, 'f1_score': 0.85, 'auc': 0.90},
    'Model_V2': {'accuracy': 0.87, 'precision': 0.85, 'recall': 0.89, 'f1_score': 0.87, 'auc': 0.92},
    'Model_V3': {'accuracy': 0.89, 'precision': 0.87, 'recall': 0.91, 'f1_score': 0.89, 'auc': 0.94}
}
fig = generator.generate_model_comparison(models_data)
```

## Security Considerations

1. **File Path Validation**:
   - Validate output directory paths to prevent directory traversal attacks
   - Sanitize filenames to prevent injection attacks

2. **Resource Limits**:
   - Limit maximum array sizes to prevent memory exhaustion
   - Implement timeouts for long-running operations

3. **Input Sanitization**:
   - Validate all numeric inputs are finite (not NaN or Inf)
   - Check for malicious input patterns

4. **Dependency Security**:
   - Pin dependency versions to avoid supply chain attacks
   - Regularly update dependencies for security patches

## Deployment Considerations

1. **Package Distribution**:
   - Distribute as Python package via PyPI
   - Include all necessary dependencies in setup.py
   - Provide wheels for common platforms

2. **Documentation**:
   - Host documentation on Read the Docs
   - Include API reference, tutorials, and examples
   - Provide gallery of example outputs

3. **Versioning**:
   - Follow semantic versioning (MAJOR.MINOR.PATCH)
   - Maintain backward compatibility within major versions
   - Document breaking changes in CHANGELOG

4. **Environment Requirements**:
   - Specify Python version requirements
   - Document system dependencies (e.g., GUI libraries for interactive backends)
   - Provide Docker image for reproducible environments

## Future Enhancements

Potential features for future versions:

1. **Interactive Charts**:
   - Support for Plotly/Bokeh for interactive visualizations
   - Hover tooltips with detailed information
   - Zoom and pan capabilities

2. **Additional Chart Types**:
   - Calibration curves
   - Feature importance plots
   - Residual plots for regression
   - Partial dependence plots

3. **Report Generation**:
   - Generate complete HTML/PDF reports
   - Include multiple charts and summary statistics
   - Template-based report customization

4. **Real-time Monitoring**:
   - Live updating charts for model monitoring
   - Integration with MLflow/Weights & Biases
   - Streaming data support

5. **Advanced Customization**:
   - Theme system (dark mode, corporate themes)
   - Custom chart templates
   - Annotation tools for presentations

