"""Schema inference module for the preprocessing pipeline.

Infers field types (id-like, datetime, numeric, categorical, text) from
a DataFrame and returns a list of FieldSchema objects.
"""

from __future__ import annotations

import logging
import re
from typing import List

import pandas as pd

from .models import FieldSchema

logger = logging.getLogger(__name__)

# Keywords that indicate an ID-like column name (case-insensitive)
_ID_KEYWORDS = {"id", "uuid", "key", "hash", "token"}

# UUID v1-v5 pattern
_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

# 32+ hex characters (MD5 / SHA hashes, etc.)
_HEX_HASH_RE = re.compile(r"^[0-9a-f]{32,}$", re.IGNORECASE)

# Maximum sample size used for heuristic checks
_SAMPLE_SIZE = 100


def is_id_like(col_name: str, series: pd.Series) -> bool:
    """Return True if the column looks like an identifier field.

    Detection rules (any one is sufficient):
    1. Column name contains an ID keyword (id, uuid, key, hash, token).
    2. A majority (>50%) of non-null string values match UUID format.
    3. A majority (>50%) of non-null string values are 32+ hex characters.

    Args:
        col_name: Name of the column.
        series: The column data as a pandas Series.

    Returns:
        True if the column is considered ID-like, False otherwise.
    """
    # Rule 1 – name-based check
    # Split on non-alphanumeric separators (_, -, space, etc.) to get tokens
    name_tokens = set(re.split(r"[^a-z0-9]+", col_name.lower()))
    for keyword in _ID_KEYWORDS:
        if keyword in name_tokens:
            logger.debug("Column '%s' identified as id-like by name keyword '%s'.", col_name, keyword)
            return True

    # Rules 2 & 3 – value-based checks (string columns only)
    str_vals = series.dropna().astype(str)
    if str_vals.empty:
        return False

    sample = str_vals.iloc[:_SAMPLE_SIZE]
    total = len(sample)

    uuid_matches = sample.apply(lambda v: bool(_UUID_RE.match(v))).sum()
    if uuid_matches / total > 0.5:
        logger.debug("Column '%s' identified as id-like by UUID pattern.", col_name)
        return True

    hex_matches = sample.apply(lambda v: bool(_HEX_HASH_RE.match(v))).sum()
    if hex_matches / total > 0.5:
        logger.debug("Column '%s' identified as id-like by hex-hash pattern.", col_name)
        return True

    return False


def is_datetime(series: pd.Series) -> bool:
    """Return True if more than 50% of a sample can be parsed as datetimes.

    Args:
        series: The column data as a pandas Series.

    Returns:
        True if the column is likely a datetime column, False otherwise.
    """
    # Already a datetime dtype – no need to parse
    if pd.api.types.is_datetime64_any_dtype(series):
        return True

    # Only attempt parsing on string/object columns
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return False

    non_null = series.dropna()
    if non_null.empty:
        return False

    sample = non_null.iloc[:_SAMPLE_SIZE]
    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            parsed = pd.to_datetime(sample, errors="coerce")
    except Exception:
        return False

    success_ratio = parsed.notna().sum() / len(sample)
    return success_ratio > 0.5


def infer_schema(df: pd.DataFrame) -> List[FieldSchema]:
    """Infer a FieldSchema for every column in *df*.

    Type inference priority:
    1. id-like  → processing = "removal"
    2. datetime → processing = "feature_extraction"
    3. numeric  → processing = "scaling"
    4. categorical (object with ≤50% unique ratio OR ≤20 unique values)
                → processing = "encoding"
    5. text     → processing = "keep"  (fallback)

    Args:
        df: Input DataFrame whose columns will be inspected.

    Returns:
        A list of FieldSchema objects, one per column.
    """
    schemas: List[FieldSchema] = []

    for col in df.columns:
        series = df[col]
        missing_count = int(series.isna().sum())
        missing_ratio = missing_count / len(series) if len(series) > 0 else 0.0

        field_type, processing = _infer_field_type(col, series)

        schema = FieldSchema(
            name=col,
            field_type=field_type,
            processing=processing,
            missing_count=missing_count,
            missing_ratio=missing_ratio,
        )
        schemas.append(schema)
        logger.debug(
            "Column '%s': type=%s, processing=%s, missing=%d (%.1f%%)",
            col, field_type, processing, missing_count, missing_ratio * 100,
        )

    return schemas


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _infer_field_type(col_name: str, series: pd.Series):
    """Return (field_type, processing) for a single column."""

    # 1. ID-like
    if is_id_like(col_name, series):
        return "id-like", "removal"

    # 2. Datetime
    if is_datetime(series):
        return "datetime", "feature_extraction"

    # 3. Numeric
    if pd.api.types.is_numeric_dtype(series):
        return "numeric", "scaling"

    # Try coercing object/string columns to numeric
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series):
        coerced = pd.to_numeric(series, errors="coerce")
        non_null = series.dropna()
        if len(non_null) > 0 and coerced.notna().sum() / len(non_null) > 0.9:
            return "numeric", "scaling"

    # 4. Categorical
    if pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series) or pd.api.types.is_categorical_dtype(series):
        n_unique = series.nunique(dropna=True)
        n_total = len(series.dropna())
        unique_ratio = n_unique / n_total if n_total > 0 else 1.0
        if unique_ratio <= 0.5 or n_unique <= 20:
            return "categorical", "encoding"

    # 5. Text (fallback)
    return "text", "keep"
