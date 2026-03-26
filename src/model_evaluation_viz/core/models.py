"""Data models and exceptions for model evaluation visualization."""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import numpy as np


# Custom Exceptions
class ValidationError(ValueError):
    """Raised when input validation fails."""
    pass


class ChartGenerationError(Exception):
    """Raised when chart generation fails."""
    pass


# Data Models
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
    color_palette: List[str] = None
    background_color: str = 'white'
    text_color: str = 'black'

    def __post_init__(self):
        """Set default color palette if not provided."""
        if self.color_palette is None:
            self.color_palette = [
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


@dataclass
class BatchGenerationResult:
    """Result of batch chart generation."""
    generated_charts: Dict[str, str] = field(default_factory=dict)
    failed_charts: Dict[str, str] = field(default_factory=dict)
    output_directory: str = ""
    timestamp: str = ""

    def get_summary(self) -> str:
        """Generate summary report."""
        summary = []
        summary.append(f"Batch Generation Summary")
        summary.append(f"Output Directory: {self.output_directory}")
        summary.append(f"Timestamp: {self.timestamp}")
        summary.append(f"\nGenerated Charts ({len(self.generated_charts)}):")
        for chart_type, filepath in self.generated_charts.items():
            summary.append(f"  - {chart_type}: {filepath}")
        
        if self.failed_charts:
            summary.append(f"\nFailed Charts ({len(self.failed_charts)}):")
            for chart_type, error in self.failed_charts.items():
                summary.append(f"  - {chart_type}: {error}")
        
        return "\n".join(summary)
