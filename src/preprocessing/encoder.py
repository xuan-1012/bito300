"""Categorical field encoding module for the preprocessing pipeline.

Handles:
- Stripping whitespace from string values (Req 3.5)
- Converting bool values to 0/1 (Req 3.6)
- One-Hot Encoding for columns with ≤10 unique values (Req 3.1)
- Label Encoding for columns with >10 unique values (Req 3.2)
- Unknown category values encoded as -1 or "unknown" column (Req 3.4)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import pandas as pd

from .models import FieldSchema

logger = logging.getLogger(__name__)

_ONEHOT_THRESHOLD = 10


def encode(
    df: pd.DataFrame,
    schemas: List[FieldSchema],
) -> Tuple[pd.DataFrame, List[FieldSchema], Dict[str, Any]]:
    """Encode categorical columns using One-Hot or Label Encoding.

    For each categorical field:
    1. Strip leading/trailing whitespace from string values.
    2. Convert bool values to 0 (False) and 1 (True).
    3. Count unique values after normalisation.
    4. If n_unique <= 10: apply One-Hot Encoding via pd.get_dummies.
    5. If n_unique > 10: apply Label Encoding (integer 0..n-1).

    Args:
        df: Input DataFrame.
        schemas: List of FieldSchema objects describing each column.

    Returns:
        A tuple of:
        - encoded_df: DataFrame with categorical columns replaced/expanded.
        - updated_schemas: Updated list of FieldSchema objects.
        - encoding_map: Dict mapping column name to encoding metadata.
    """
    df = df.copy()
    encoding_map: Dict[str, Any] = {}
    new_schemas: List[FieldSchema] = []

    for schema in schemas:
        col = schema.name

        if schema.field_type != "categorical" or col not in df.columns:
            new_schemas.append(schema)
            continue

        # --- Normalise values ---
        series = _normalise_series(df[col], col)
        df[col] = series

        categories = sorted(series.dropna().unique().tolist(), key=str)
        n_unique = len(categories)

        if n_unique <= _ONEHOT_THRESHOLD:
            df, dummy_schemas = _apply_onehot(df, col, categories)
            encoding_map[col] = {
                "type": "onehot",
                "categories": categories,
                "mapping": {cat: f"{col}_{cat}" for cat in categories},
            }
            new_schemas.extend(dummy_schemas)
            logger.debug(
                "Column '%s': One-Hot Encoding with %d categories.", col, n_unique
            )
        else:
            mapping = {cat: idx for idx, cat in enumerate(categories)}
            df[col] = series.map(mapping).fillna(-1).astype(int)
            schema.field_type = "numeric"
            schema.processing = "keep"
            new_schemas.append(schema)
            encoding_map[col] = {
                "type": "label",
                "categories": categories,
                "mapping": mapping,
            }
            logger.debug(
                "Column '%s': Label Encoding with %d categories.", col, n_unique
            )

    return df, new_schemas, encoding_map


def apply_encoding_map(
    df: pd.DataFrame,
    schemas: List[FieldSchema],
    encoding_map: Dict[str, Any],
) -> Tuple[pd.DataFrame, List[FieldSchema]]:
    """Apply a previously saved encoding_map to new data.

    For onehot columns: create one dummy column per known category, fill
    missing categories with 0, then drop the original column.

    For label columns: map values using the saved mapping; unknown values
    are encoded as -1.

    Args:
        df: Input DataFrame.
        schemas: List of FieldSchema objects describing each column.
        encoding_map: Encoding metadata produced by a previous ``encode()`` call.

    Returns:
        A tuple of (encoded_df, updated_schemas).
    """
    df = df.copy()
    new_schemas: List[FieldSchema] = []

    schema_map = {s.name: s for s in schemas}

    # Collect columns not touched by the encoding map
    encoded_cols = set(encoding_map.keys())

    for schema in schemas:
        col = schema.name

        if col not in encoding_map:
            new_schemas.append(schema)
            continue

        info = encoding_map[col]
        enc_type = info["type"]
        categories = info["categories"]
        mapping = info["mapping"]

        # Normalise before applying
        series = _normalise_series(df[col], col) if col in df.columns else pd.Series(
            dtype=object, name=col
        )

        if enc_type == "onehot":
            for cat in categories:
                dummy_col = f"{col}_{cat}"
                if col in df.columns:
                    df[dummy_col] = (series == cat).astype(int)
                else:
                    df[dummy_col] = 0
                new_schemas.append(
                    FieldSchema(name=dummy_col, field_type="numeric", processing="keep")
                )
            if col in df.columns:
                df = df.drop(columns=[col])
            logger.debug("Column '%s': applied One-Hot Encoding from map.", col)

        elif enc_type == "label":
            if col in df.columns:
                df[col] = series.map(mapping).fillna(-1).astype(int)
            else:
                df[col] = -1
            schema.field_type = "numeric"
            schema.processing = "keep"
            new_schemas.append(schema)
            logger.debug("Column '%s': applied Label Encoding from map.", col)

    return df, new_schemas


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _normalise_series(series: pd.Series, col: str) -> pd.Series:
    """Strip whitespace from strings and convert bools to 0/1."""
    series = series.copy()

    # Convert bool values to int (True→1, False→0) before any string ops
    # Use element-wise check to handle mixed-type object columns
    bool_mask = series.apply(lambda x: isinstance(x, bool))
    if bool_mask.any():
        series = series.where(~bool_mask, series.map(lambda x: int(x) if isinstance(x, bool) else x))
        logger.debug("Column '%s': converted bool values to 0/1.", col)

    # Strip whitespace from string values
    str_mask = series.apply(lambda x: isinstance(x, str))
    if str_mask.any():
        series = series.where(~str_mask, series.map(lambda x: x.strip() if isinstance(x, str) else x))
        logger.debug("Column '%s': stripped whitespace from string values.", col)

    return series


def _apply_onehot(
    df: pd.DataFrame,
    col: str,
    categories: List[Any],
) -> Tuple[pd.DataFrame, List[FieldSchema]]:
    """Apply One-Hot Encoding for a column with known categories.

    Creates one binary column per category, drops the original column.
    """
    dummy_schemas: List[FieldSchema] = []

    for cat in categories:
        dummy_col = f"{col}_{cat}"
        df[dummy_col] = (df[col] == cat).astype(int)
        dummy_schemas.append(
            FieldSchema(name=dummy_col, field_type="numeric", processing="keep")
        )

    df = df.drop(columns=[col])
    return df, dummy_schemas
