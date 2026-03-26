"""ID-like field removal module for the preprocessing pipeline.

Removes columns identified as id-like in the schema, unless they are
explicitly listed in keep_fields.
"""

from __future__ import annotations

import logging
from typing import List, Optional, Tuple

import pandas as pd

from .models import FieldSchema

logger = logging.getLogger(__name__)


def remove_id_fields(
    df: pd.DataFrame,
    schemas: List[FieldSchema],
    keep_fields: Optional[List[str]] = None,
) -> Tuple[pd.DataFrame, List[FieldSchema], List[str]]:
    """Remove columns whose schema field_type is "id-like", except those in keep_fields.

    Args:
        df: Input DataFrame.
        schemas: List of FieldSchema objects describing each column.
        keep_fields: Column names that should NOT be removed even if id-like.
                     Defaults to an empty list when None.

    Returns:
        A tuple of:
        - df_without_id_cols: DataFrame with id-like columns removed.
        - updated_schemas: List of FieldSchema objects with id-like schemas removed.
        - removed_col_names: List of column names that were removed.
    """
    if keep_fields is None:
        keep_fields = []

    keep_set = set(keep_fields)

    removed_col_names: List[str] = [
        s.name
        for s in schemas
        if s.field_type == "id-like" and s.name not in keep_set
    ]

    if removed_col_names:
        logger.info("Removing id-like columns: %s", removed_col_names)
    else:
        logger.debug("No id-like columns to remove.")

    cols_to_drop = [c for c in removed_col_names if c in df.columns]
    df_without_id_cols = df.drop(columns=cols_to_drop)

    updated_schemas = [
        s for s in schemas
        if not (s.field_type == "id-like" and s.name not in keep_set)
    ]

    return df_without_id_cols, updated_schemas, removed_col_names
