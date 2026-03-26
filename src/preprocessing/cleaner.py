"""Missing value cleaning module for the preprocessing pipeline.

Handles:
- Removal of fully-null rows (Req 2.4)
- Numeric field imputation with median, fallback 0 (Req 2.1, 2.6)
- Categorical field imputation with mode, fallback "unknown" (Req 2.2, 2.6)
- Warning when missing ratio > 80% (Req 2.3)
- Logging of missing counts and ratios (Req 2.5)
- Replacement of inf/-inf and extreme outliers with 99th percentile (Req 5.5)
"""

from __future__ import annotations

import logging
import math
from typing import List, Tuple

import numpy as np
import pandas as pd

from .models import FieldSchema

logger = logging.getLogger(__name__)

_HIGH_MISSING_THRESHOLD = 0.80


def clean(
    df: pd.DataFrame,
    schemas: List[FieldSchema],
) -> Tuple[pd.DataFrame, List[FieldSchema]]:
    """Clean a DataFrame by removing null rows and imputing missing values.

    Processing order for numeric fields:
    1. Replace inf/-inf with NaN
    2. Replace values > 99th percentile with the 99th percentile value
    3. Fill remaining NaN with median (fallback: 0)

    For categorical fields:
    - Fill NaN with mode (fallback: "unknown")

    Args:
        df: Input DataFrame.
        schemas: List of FieldSchema objects describing each column.

    Returns:
        A tuple of (cleaned_df, updated_schemas) where updated_schemas have
        missing_count, missing_ratio, and fill_value populated.
    """
    df = df.copy()

    # Req 2.4 – remove fully-null rows
    before_rows = len(df)
    df = df.dropna(how="all")
    removed = before_rows - len(df)
    if removed:
        logger.info("Removed %d fully-null row(s).", removed)

    schema_map = {s.name: s for s in schemas}

    for schema in schemas:
        col = schema.name
        if col not in df.columns:
            continue

        series = df[col]
        total = len(series)

        # Req 2.5 – record missing stats (before imputation)
        missing_count = int(series.isna().sum())
        missing_ratio = missing_count / total if total > 0 else 0.0
        schema.missing_count = missing_count
        schema.missing_ratio = missing_ratio

        # Req 2.3 – warn if high missing ratio
        if missing_ratio > _HIGH_MISSING_THRESHOLD:
            logger.warning(
                "Column '%s' has %.1f%% missing values (threshold: %.0f%%).",
                col,
                missing_ratio * 100,
                _HIGH_MISSING_THRESHOLD * 100,
            )

        if schema.field_type == "numeric":
            df[col] = _clean_numeric(df[col], col, schema)
        elif schema.field_type == "categorical":
            df[col] = _clean_categorical(df[col], col, schema)
        # datetime, text, id-like: no imputation applied here

    return df, schemas


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _clean_numeric(series: pd.Series, col: str, schema: FieldSchema) -> pd.Series:
    """Clean a numeric series: handle inf, cap outliers, impute NaN."""
    series = series.copy()

    # Step 1 – replace inf/-inf with NaN (Req 5.5)
    series = series.replace([np.inf, -np.inf], np.nan)

    # Step 2 – cap values above 99th percentile (Req 5.5)
    non_null = series.dropna()
    if not non_null.empty:
        p99 = float(np.nanpercentile(non_null.values, 99))
        series = series.where(series <= p99, other=p99)
    else:
        p99 = None

    # Step 3 – fill NaN with median, fallback 0 (Req 2.1, 2.6)
    non_null_after = series.dropna()
    if not non_null_after.empty:
        fill_value = float(non_null_after.median())
    else:
        fill_value = 0.0
        logger.debug("Column '%s': no valid values for median, using fallback 0.", col)

    series = series.fillna(fill_value)
    schema.fill_value = fill_value
    logger.debug("Column '%s' (numeric): fill_value=%.4g, p99=%s", col, fill_value, p99)
    return series


def _clean_categorical(series: pd.Series, col: str, schema: FieldSchema) -> pd.Series:
    """Clean a categorical series: impute NaN with mode, fallback 'unknown'."""
    series = series.copy()

    non_null = series.dropna()
    if not non_null.empty:
        mode_result = non_null.mode()
        fill_value = mode_result.iloc[0] if not mode_result.empty else "unknown"
    else:
        fill_value = "unknown"
        logger.debug("Column '%s': no valid values for mode, using fallback 'unknown'.", col)

    series = series.fillna(fill_value)
    schema.fill_value = fill_value
    logger.debug("Column '%s' (categorical): fill_value=%r", col, fill_value)
    return series
