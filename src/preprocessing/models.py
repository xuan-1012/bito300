"""Core data models for the data preprocessing pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional


# Field type literals
FieldType = Literal["numeric", "categorical", "datetime", "text", "id-like"]

# Processing action literals
ProcessingAction = Literal[
    "encoding", "scaling", "feature_extraction", "removal", "keep", "impute"
]


class PipelineReadError(Exception):
    """Raised when the pipeline fails to read or parse an input file."""


@dataclass
class FieldSchema:
    """Schema definition for a single data field.

    Attributes:
        name: Column name in the dataset.
        field_type: Inferred or declared type of the field.
        processing: The processing action applied to this field.
        missing_count: Number of missing values detected.
        missing_ratio: Ratio of missing values (0.0 – 1.0).
        fill_value: Value used to impute missing entries (if any).
    """

    name: str
    field_type: FieldType = "text"
    processing: ProcessingAction = "keep"
    missing_count: int = 0
    missing_ratio: float = 0.0
    fill_value: Optional[object] = None


@dataclass
class PipelineConfig:
    """Configuration for a pipeline run.

    Attributes:
        input_path: Path to the input JSON or CSV file.
        output_dir: Directory where all output files will be written.
        keep_fields: ID-like fields that should NOT be removed.
        scale_fields: Numeric fields that should be scaled with StandardScaler.
        random_seed: Seed for reproducible train/validation splits.
        train_ratio: Fraction of data used for training (default 0.8).
        time_series_split: If True, split by order instead of randomly.
        schema_path: Path to a previously saved preprocessing_rules.json.
        encoding_map_path: Path to a previously saved encoding_map.json.
        scaler_params_path: Path to a previously saved scaler_params.json.
    """

    input_path: str
    output_dir: str
    keep_fields: List[str] = field(default_factory=list)
    scale_fields: List[str] = field(default_factory=list)
    random_seed: int = 42
    train_ratio: float = 0.8
    time_series_split: bool = False
    schema_path: Optional[str] = None
    encoding_map_path: Optional[str] = None
    scaler_params_path: Optional[str] = None


@dataclass
class FieldChangeReport:
    """Report of field-level changes detected between runs.

    Attributes:
        added: Fields present in new data but absent in saved schema.
        removed: Fields present in saved schema but absent in new data.
        type_changed: Mapping of field name → (old_type, new_type).
    """

    added: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)
    type_changed: Dict[str, tuple] = field(default_factory=dict)


@dataclass
class ProcessingSummary:
    """Summary statistics for a pipeline run.

    Attributes:
        success_count: Number of rows successfully processed.
        failure_count: Number of rows skipped due to errors.
        warning_count: Number of warnings raised during processing.
        errors: List of error messages collected during the run.
    """

    success_count: int = 0
    failure_count: int = 0
    warning_count: int = 0
    errors: List[str] = field(default_factory=list)


@dataclass
class PipelineResult:
    """Result returned after a pipeline run completes.

    Attributes:
        output_files: Paths of all files written by the pipeline.
        summary: High-level processing statistics.
        field_changes: Report of field additions, removals, and type changes.
    """

    output_files: List[str] = field(default_factory=list)
    summary: ProcessingSummary = field(default_factory=ProcessingSummary)
    field_changes: FieldChangeReport = field(default_factory=FieldChangeReport)
