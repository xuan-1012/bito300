"""Data reading module for the preprocessing pipeline.

Supports JSON (with nested flattening) and CSV file formats, UTF-8 encoding.
Raises PipelineReadError on missing files or invalid formats.
"""

from __future__ import annotations

import csv
import json
import logging
import os
from typing import Any

import pandas as pd

from .models import PipelineReadError

logger = logging.getLogger(__name__)


def flatten_json(record: dict, sep: str = "_") -> dict:
    """Recursively flatten a nested dict into a single-level dict.

    Args:
        record: The dict to flatten.
        sep: Separator used when joining nested keys.

    Returns:
        A flat dict with no nested dicts as values.

    Example:
        >>> flatten_json({"a": {"b": 1, "c": 2}, "d": 3})
        {'a_b': 1, 'a_c': 2, 'd': 3}
    """
    result: dict[str, Any] = {}

    def _flatten(obj: Any, prefix: str) -> None:
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_key = f"{prefix}{sep}{key}" if prefix else key
                _flatten(value, new_key)
        else:
            result[prefix] = obj

    _flatten(record, "")
    return result


def read_file(path: str) -> pd.DataFrame:
    """Read a JSON or CSV file and return a pandas DataFrame.

    File type is detected by extension (.json or .csv).
    For JSON, if the top-level value is a list of dicts, each record is
    flattened individually. If it is a single dict, it is wrapped in a list
    before flattening.

    Args:
        path: Filesystem path to the input file.

    Returns:
        A DataFrame containing all fields from the file.

    Raises:
        PipelineReadError: If the file does not exist, cannot be read,
            has an unsupported extension, or contains invalid content.
    """
    if not os.path.exists(path):
        msg = f"File not found: {path}"
        logger.error(msg)
        raise PipelineReadError(msg)

    ext = os.path.splitext(path)[1].lower()

    if ext == ".json":
        return _read_json(path)
    elif ext == ".csv":
        return _read_csv(path)
    else:
        msg = f"Unsupported file extension '{ext}'. Expected .json or .csv."
        logger.error(msg)
        raise PipelineReadError(msg)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _read_json(path: str) -> pd.DataFrame:
    """Read and parse a JSON file, flattening nested structures."""
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, IOError) as exc:
        msg = f"Cannot read file '{path}': {exc}"
        logger.error(msg)
        raise PipelineReadError(msg) from exc
    except json.JSONDecodeError as exc:
        msg = f"Invalid JSON in '{path}': {exc}"
        logger.error(msg)
        raise PipelineReadError(msg) from exc

    if isinstance(data, list):
        if not data:
            logger.warning("JSON file '%s' contains an empty list.", path)
            return pd.DataFrame()
        records = [flatten_json(r) if isinstance(r, dict) else {"value": r} for r in data]
    elif isinstance(data, dict):
        records = [flatten_json(data)]
    else:
        msg = f"JSON file '{path}' must contain an object or array, got {type(data).__name__}."
        logger.error(msg)
        raise PipelineReadError(msg)

    logger.info("Read %d record(s) from JSON file '%s'.", len(records), path)
    return pd.DataFrame(records)


def _read_csv(path: str) -> pd.DataFrame:
    """Read a CSV file with UTF-8 encoding."""
    try:
        df = pd.read_csv(path, encoding="utf-8")
    except (OSError, IOError) as exc:
        msg = f"Cannot read file '{path}': {exc}"
        logger.error(msg)
        raise PipelineReadError(msg) from exc
    except Exception as exc:
        msg = f"Invalid CSV in '{path}': {exc}"
        logger.error(msg)
        raise PipelineReadError(msg) from exc

    logger.info("Read %d record(s) from CSV file '%s'.", len(df), path)
    return df
