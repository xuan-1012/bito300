"""Datetime feature extraction module for the preprocessing pipeline.

Extracts hour, day, weekday, and month features from datetime columns,
then drops the original datetime column. If parsing fails, the column
is treated as a text field instead.
"""

from __future__ import annotations

import logging
from typing import List, Tuple

import pandas as pd

from .models import FieldSchema

logger = logging.getLogger(__name__)


def extract_datetime_features(
    df: pd.DataFrame,
    schemas: List[FieldSchema],
) -> Tuple[pd.DataFrame, List[FieldSchema]]:
    """Extract time features from datetime columns and drop the originals.

    For each schema with ``field_type == "datetime"``:

    - Attempt to parse the column with ``pd.to_datetime(..., errors="coerce")``.
    - If all values become NaT (parsing failed), log a warning and update the
      schema to ``field_type="text", processing="keep"`` — the column is kept
      as-is.
    - Otherwise, add four derived columns:
        - ``{col}_hour``    – hour of day (0–23)
        - ``{col}_day``     – day of month (1–31)
        - ``{col}_weekday`` – day of week (0 = Monday, 6 = Sunday)
        - ``{col}_month``   – month of year (1–12)
      Then drop the original datetime column and replace its schema entry with
      four new ``FieldSchema`` objects (``field_type="numeric"``,
      ``processing="keep"``).

    Args:
        df: Input DataFrame.
        schemas: List of FieldSchema objects describing each column.

    Returns:
        A tuple of (updated_df, updated_schemas).
    """
    df = df.copy()
    updated_schemas: List[FieldSchema] = []

    for schema in schemas:
        if schema.field_type != "datetime":
            updated_schemas.append(schema)
            continue

        col = schema.name

        # Attempt to parse the column as datetime
        parsed = pd.to_datetime(df[col], errors="coerce")

        # Check if parsing completely failed (all NaT)
        if parsed.isna().all():
            logger.warning(
                "Column '%s' could not be parsed as datetime; treating as text field.",
                col,
            )
            schema.field_type = "text"
            schema.processing = "keep"
            updated_schemas.append(schema)
            continue

        # Extract the four time features
        df[f"{col}_hour"] = parsed.dt.hour
        df[f"{col}_day"] = parsed.dt.day
        df[f"{col}_weekday"] = parsed.dt.weekday
        df[f"{col}_month"] = parsed.dt.month

        # Drop the original datetime column
        df.drop(columns=[col], inplace=True)

        logger.debug(
            "Column '%s': extracted hour/day/weekday/month features and dropped original.",
            col,
        )

        # Add a FieldSchema for each extracted feature
        for suffix in ("hour", "day", "weekday", "month"):
            updated_schemas.append(
                FieldSchema(
                    name=f"{col}_{suffix}",
                    field_type="numeric",
                    processing="keep",
                )
            )

    return df, updated_schemas
