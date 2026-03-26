# Model Evaluation Visualization

A comprehensive suite of tools for evaluating and visualizing machine learning model performance.

## Overview

This module provides publication-quality charts and metrics for model assessment, including:

- Validation Curves
- Learning Curves
- Confusion Matrices
- ROC Curves
- Precision-Recall Curves
- Threshold Analysis
- Lift Curves
- Model Comparison Tables

## Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Module Structure

```
model_evaluation_viz/
├── __init__.py                 # Package exports
├── core/                       # Core components
│   ├── __init__.py
│   ├── chart_generator.py     # Main ChartGenerator class
│   ├── metric_calculator.py   # Metric calculations
│   └── models.py              # Data models and exceptions
├── generators/                 # Chart-specific generators
│   ├── __init__.py
│   ├── validation_curve.py
│   ├── learning_curve.py
│   ├── confusion_matrix.py
│   ├── roc_curve.py
│   ├── precision_recall.py
│   ├── threshold_analysis.py
│   ├── lift_curve.py
│   └── model_comparison.py
├── styling/                    # Styling components
│   ├── __init__.py
│   ├── chart_styler.py
│   └── color_palettes.py
├── validation/                 # Input validation
│   ├── __init__.py
│   └── input_validator.py
├── export/                     # Export functionality
│   ├── __init__.py
│   └── image_exporter.py
└── utils/                      # Utility functions
    ├── __init__.py
    └── helpers.py
```

## Quick Start

```python
from src.model_evaluation_viz import ChartGenerator

# Initialize generator
generator = ChartGenerator(output_dir='./charts')

# Generate charts (to be implemented)
# fig = generator.generate_roc_curve(y_true, y_proba)
# fig = generator.generate_confusion_matrix(y_true, y_pred)
```

## Data Models

### ChartStyle

Configuration for chart appearance:

```python
from src.model_evaluation_viz import ChartStyle

style = ChartStyle(
    figure_size=(10, 6),
    dpi=300,
    font_size=12,
    color_palette=['#1f77b4', '#ff7f0e', '#2ca02c']
)
```

### MetricResult

Container for evaluation metrics:

```python
from src.model_evaluation_viz import MetricResult

metrics = MetricResult(
    accuracy=0.85,
    precision=0.82,
    recall=0.88,
    f1_score=0.85
)
```

### ROCResult

Container for ROC curve data:

```python
from src.model_evaluation_viz import ROCResult

roc = ROCResult(
    fpr=fpr_array,
    tpr=tpr_array,
    auc=0.90,
    thresholds=threshold_array
)
```

### PrecisionRecallResult

Container for precision-recall curve data:

```python
from src.model_evaluation_viz import PrecisionRecallResult

pr = PrecisionRecallResult(
    precision=precision_array,
    recall=recall_array,
    average_precision=0.88,
    thresholds=threshold_array
)
```

### BatchGenerationResult

Result of batch chart generation:

```python
from src.model_evaluation_viz import BatchGenerationResult

result = BatchGenerationResult(
    generated_charts={'roc': 'path/to/roc.png'},
    failed_charts={},
    output_directory='./charts',
    timestamp='2024-01-01T12:00:00'
)

print(result.get_summary())
```

## Exceptions

### ValidationError

Raised when input validation fails:

```python
from src.model_evaluation_viz import ValidationError

try:
    # Some operation
    pass
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### ChartGenerationError

Raised when chart generation fails:

```python
from src.model_evaluation_viz import ChartGenerationError

try:
    # Generate chart
    pass
except ChartGenerationError as e:
    print(f"Chart generation failed: {e}")
```

## Development Status

This module is currently under development. Core data models and project structure are complete.
Chart generation functionality will be implemented in subsequent tasks.

## Requirements

- Python 3.8+
- numpy >= 1.20.0
- matplotlib >= 3.5.0
- scikit-learn >= 1.0.0
- pytest >= 7.0.0 (for testing)
- hypothesis >= 6.0.0 (for property-based testing)

## License

Part of the Financial Risk Analysis System.
