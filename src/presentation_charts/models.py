"""Data models for presentation chart generation."""

from dataclasses import dataclass, field
from typing import Dict, Optional
from datetime import datetime


@dataclass
class PresentationConfig:
    """Configuration for presentation chart generation."""
    
    output_dir: str = "presentation_charts"
    aspect_ratio: tuple = (16, 9)  # 16:9 presentation format
    dpi: int = 300  # High resolution
    style: str = "aws_fintech"  # AWS/FinTech style
    color_scheme: str = "professional_blue"
    font_family: str = "Arial"
    title_font_size: int = 18
    label_font_size: int = 14
    export_mermaid: bool = True
    export_png: bool = True


@dataclass
class ChartMetadata:
    """Metadata for a generated chart."""
    
    chart_type: str
    title: str
    description: str
    filepath: str
    mermaid_source: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class BatchGenerationResult:
    """Result of batch chart generation."""
    
    generated_charts: Dict[str, ChartMetadata] = field(default_factory=dict)
    failed_charts: Dict[str, str] = field(default_factory=dict)
    output_directory: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    mermaid_file: Optional[str] = None
