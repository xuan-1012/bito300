"""
SchemaInferencer - Automatic schema inference from data samples.

Detects field types (numeric, categorical, datetime, text, id_like, boolean,
null, mixed) from flattened records and exports the resulting schema to JSON.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from src.ingestion.models import FieldSchema, FieldType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Datetime patterns (order matters – more specific first)
# ---------------------------------------------------------------------------
_DATETIME_PATTERNS = [
    re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),  # ISO 8601
    re.compile(r"^\d{4}-\d{2}-\d{2}"),                      # YYYY-MM-DD
    re.compile(r"^\d{2}/\d{2}/\d{4}"),                      # MM/DD/YYYY
    re.compile(r"^\d{13}$"),                                 # Unix ms (13 digits)
    re.compile(r"^\d{10}$"),                                 # Unix timestamp (10 digits)
]

# ID-like patterns
_UUID_PATTERN = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)
_HASH_PATTERN = re.compile(r"^[0-9a-f]{32,}$", re.IGNORECASE)
_ALPHANUM_ID_PATTERN = re.compile(r"^[A-Z]{2,5}\d{4,}$")

# Keywords that suggest a field is an identifier
_ID_KEYWORDS = {"id", "uuid", "key", "hash", "token", "code"}


class SchemaInferencer:
    """Infer field types from flattened data samples."""

    def __init__(
        self,
        sample_size: int = 100,
        confidence_threshold: float = 0.8,
    ) -> None:
        """
        Initialise the SchemaInferencer.

        Args:
            sample_size: Maximum number of values to examine per field.
            confidence_threshold: Minimum confidence to accept a type
                inference result (used for logging / downstream consumers).
        """
        if not isinstance(sample_size, int) or sample_size <= 0:
            raise ValueError("sample_size must be a positive integer")
        if not isinstance(confidence_threshold, (int, float)) or not (
            0.0 <= confidence_threshold <= 1.0
        ):
            raise ValueError("confidence_threshold must be a float between 0 and 1")

        self.sample_size = sample_size
        self.confidence_threshold = confidence_threshold

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def infer_schema(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, FieldSchema]:
        """
        Infer schema from a list of flattened dictionaries.

        Args:
            data: List of flattened records (no nested dicts).

        Returns:
            Mapping of field name → FieldSchema.
        """
        try:
            return self._infer_schema_impl(data)
        except Exception as exc:  # pragma: no cover – fallback path
            logger.error("Schema inference failed: %s. Creating minimal schema.", exc)
            return self._minimal_schema(data)

    def export_schema(
        self,
        schema: Dict[str, FieldSchema],
        output_path: str = "schema.json",
    ) -> str:
        """
        Serialise schema to a JSON file.

        Args:
            schema: Mapping returned by :meth:`infer_schema`.
            output_path: Destination file path.

        Returns:
            The resolved output path.
        """
        serialisable = {name: fs.to_dict() for name, fs in schema.items()}
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(serialisable, fh, indent=2, default=str)

        logger.info(
            "Schema exported: %d fields → %s", len(schema), output_path
        )
        return output_path

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _infer_schema_impl(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, FieldSchema]:
        """Core implementation (no try/except wrapper)."""
        if not data:
            return {}

        # Collect all field names across all records
        all_fields: Dict[str, List[Any]] = {}
        total_counts: Dict[str, int] = {}
        null_counts: Dict[str, int] = {}

        for record in data:
            for field, value in record.items():
                if field not in all_fields:
                    all_fields[field] = []
                    total_counts[field] = 0
                    null_counts[field] = 0
                total_counts[field] += 1
                if value is None:
                    null_counts[field] += 1
                else:
                    all_fields[field].append(value)

        schema: Dict[str, FieldSchema] = {}
        for field_name, values in all_fields.items():
            # Limit to sample_size non-null values
            sample = values[: self.sample_size]
            total = total_counts[field_name]
            null_count = null_counts[field_name]
            nullable = null_count > 0

            inferred_type, confidence = self._infer_field_type(
                sample, field_name=field_name
            )

            schema[field_name] = FieldSchema(
                name=field_name,
                inferred_type=inferred_type,
                nullable=nullable,
                sample_values=sample[:10],  # keep at most 10 for the schema
                null_count=null_count,
                total_count=total,
                confidence=confidence,
            )

        return schema

    def _infer_field_type(
        self,
        values: List[Any],
        field_name: str = "",
    ) -> Tuple[FieldType, float]:
        """
        Infer the dominant type from a list of non-null sample values.

        Args:
            values: Non-null sample values.
            field_name: Field name (used for ID-keyword heuristic).

        Returns:
            (FieldType, confidence) tuple.
        """
        if not values:
            return (FieldType.NULL, 1.0)

        numeric_count = 0
        datetime_count = 0
        id_like_count = 0
        boolean_count = 0
        text_count = 0

        total = len(values)

        for value in values:
            if isinstance(value, bool):
                # bool is a subclass of int – check first
                boolean_count += 1
            elif self._is_numeric(value):
                numeric_count += 1
            elif isinstance(value, str):
                if self._is_datetime(value):
                    datetime_count += 1
                elif self._is_id_like(value):
                    id_like_count += 1
                else:
                    text_count += 1
            else:
                text_count += 1

        type_scores = {
            FieldType.NUMERIC: numeric_count / total,
            FieldType.DATETIME: datetime_count / total,
            FieldType.ID_LIKE: id_like_count / total,
            FieldType.BOOLEAN: boolean_count / total,
            FieldType.TEXT: text_count / total,
        }

        dominant_type = max(type_scores, key=lambda t: type_scores[t])
        confidence = type_scores[dominant_type]

        # Low confidence → MIXED
        if confidence < 0.6:
            return (FieldType.MIXED, confidence)

        # Numeric field whose name hints at an identifier → prefer ID_LIKE
        if dominant_type == FieldType.NUMERIC and self.is_id_field_name(field_name):
            return (FieldType.ID_LIKE, confidence * 0.9)

        return (dominant_type, confidence)

    # ------------------------------------------------------------------
    # Type-detection helpers
    # ------------------------------------------------------------------

    def _is_numeric(self, value: Any) -> bool:
        """Return True if *value* is numeric (int/float or parseable as float)."""
        if isinstance(value, bool):
            return False  # booleans are not treated as numeric here
        if isinstance(value, (int, float)):
            return True
        if isinstance(value, str):
            try:
                float(value)
                return True
            except ValueError:
                return False
        return False

    def _is_datetime(self, value: Any) -> bool:
        """Return True if *value* matches a common datetime pattern."""
        if not isinstance(value, str):
            return False
        for pattern in _DATETIME_PATTERNS:
            if pattern.match(value):
                return True
        return False

    def _is_id_like(self, value: Any) -> bool:
        """Return True if *value* looks like an identifier (UUID, hash, alphanumeric code)."""
        if not isinstance(value, str):
            return False
        if _UUID_PATTERN.match(value):
            return True
        if _HASH_PATTERN.match(value):
            return True
        if _ALPHANUM_ID_PATTERN.match(value):
            return True
        return False

    @staticmethod
    def is_id_field_name(field_name: str) -> bool:
        """Return True if *field_name* contains an ID-related keyword."""
        if not field_name:
            return False
        field_lower = field_name.lower()
        return any(keyword in field_lower for keyword in _ID_KEYWORDS)

    # ------------------------------------------------------------------
    # Fallback helpers
    # ------------------------------------------------------------------

    def _minimal_schema(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, FieldSchema]:
        """Create a minimal schema when full inference fails."""
        schema: Dict[str, FieldSchema] = {}
        if not data:
            return schema
        for field_name in data[0].keys():
            schema[field_name] = FieldSchema(
                name=field_name,
                inferred_type=FieldType.TEXT,
                nullable=True,
                sample_values=[],
                null_count=0,
                total_count=len(data),
                confidence=0.0,
            )
        return schema
