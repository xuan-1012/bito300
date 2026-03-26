"""
Model Evaluation Visualization System

A comprehensive suite of tools for evaluating and visualizing machine learning model performance.
Provides publication-quality charts and metrics for model assessment.
"""

# Note: ChartGenerator import commented out until it's implemented
# from .core.chart_generator import ChartGenerator
from .core.models import (
    ChartStyle,
    MetricResult,
    ROCResult,
    PrecisionRecallResult,
    BatchGenerationResult,
    ValidationError,
    ChartGenerationError,
)

__version__ = "0.1.0"

__all__ = [
    # "ChartGenerator",  # Commented out until implemented
    "ChartStyle",
    "MetricResult",
    "ROCResult",
    "PrecisionRecallResult",
    "BatchGenerationResult",
    "ValidationError",
    "ChartGenerationError",
]
