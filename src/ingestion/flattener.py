"""
JSONFlattener - JSON structure flattening component

Transforms nested JSON structures into flat dictionaries suitable for
tabular analysis. Supports configurable separator, max depth, and list
handling strategies.
"""

import json
import logging
from typing import Any, Dict, List, Union

logger = logging.getLogger(__name__)


class JSONFlattener:
    """
    Flattens nested JSON structures into flat dictionaries.

    Supports:
    - Recursive dict flattening with configurable key separator
    - List explosion (each dict item becomes a separate record)
    - Primitive list serialization as JSON strings
    - Max depth enforcement to prevent infinite recursion
    - Graceful error handling via FallbackManager (if available)
    """

    VALID_LIST_STRATEGIES = ("explode", "index", "json_string")

    def __init__(
        self,
        separator: str = "_",
        max_depth: int = 10,
        handle_lists: str = "explode",
    ):
        """
        Initialize JSON flattener.

        Args:
            separator: Separator for concatenating nested keys (e.g. "user_address_city")
            max_depth: Maximum recursion depth; deeper structures are serialized as JSON
            handle_lists: Strategy for list fields ("explode", "index", "json_string")

        Raises:
            ValueError: If any configuration parameter is invalid
        """
        if not isinstance(separator, str) or not separator:
            raise ValueError("separator must be a non-empty string")
        if not isinstance(max_depth, int) or max_depth < 1:
            raise ValueError("max_depth must be a positive integer")
        if handle_lists not in self.VALID_LIST_STRATEGIES:
            raise ValueError(
                f"handle_lists must be one of {self.VALID_LIST_STRATEGIES}"
            )

        self.separator = separator
        self.max_depth = max_depth
        self.handle_lists = handle_lists

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def flatten(
        self,
        data: Union[Dict[str, Any], List[Dict[str, Any]]],
    ) -> List[Dict[str, Any]]:
        """
        Flatten nested JSON structure into a list of flat dicts.

        Args:
            data: Nested JSON data (dict or list of dicts)

        Returns:
            List of flattened dictionaries (each has max depth 1)
        """
        try:
            if isinstance(data, dict):
                records = self._flatten_single(data)
            elif isinstance(data, list):
                records = []
                for item in data:
                    if isinstance(item, dict):
                        records.extend(self._flatten_single(item))
                    else:
                        # Primitive item in top-level list – wrap it
                        records.append({"value": item})
            else:
                # Scalar at top level
                records = [{"value": data}]

            return records

        except Exception as exc:  # pragma: no cover – fallback path
            logger.error("JSONFlattener.flatten() error: %s", exc, exc_info=True)
            # Return empty list so callers can continue processing
            return []

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _flatten_single(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Flatten a single dict record, potentially producing multiple records
        when list fields are exploded.

        Returns a list of flat dicts.
        """
        # Start with one "base" record
        base = self._flatten_dict(record, parent_key="", depth=0)

        # Collect any list-of-dicts fields that need to be exploded
        list_fields = {
            k: v for k, v in base.items() if isinstance(v, list)
        }

        if not list_fields:
            return [base]

        # Remove list fields from base; they will be merged back after explosion
        for k in list_fields:
            del base[k]

        # Explode each list field in turn, cross-joining with existing records
        result_records: List[Dict[str, Any]] = [base]

        for field_key, list_value in list_fields.items():
            exploded = self._handle_list_field(field_key, list_value)

            if isinstance(exploded, dict):
                # Single dict result – merge into every existing record
                new_records = []
                for rec in result_records:
                    merged = {**rec, **exploded}
                    new_records.append(merged)
                result_records = new_records
            elif isinstance(exploded, list):
                # Multiple records – cross-join
                new_records = []
                for rec in result_records:
                    for exp_rec in exploded:
                        merged = {**rec, **exp_rec}
                        new_records.append(merged)
                result_records = new_records

        return result_records

    def _flatten_dict(
        self,
        nested_dict: Dict[str, Any],
        parent_key: str = "",
        depth: int = 0,
    ) -> Dict[str, Any]:
        """
        Recursively flatten a dictionary.

        Args:
            nested_dict: Dictionary to flatten
            parent_key: Accumulated key prefix from parent levels
            depth: Current recursion depth

        Returns:
            Partially-flattened dictionary (list-of-dict values are kept as
            raw lists so that _flatten_single() can explode them later)
        """
        # At max depth, serialize the whole dict as a JSON string
        if depth >= self.max_depth:
            key = parent_key if parent_key else "_raw"
            return {key: json.dumps(nested_dict)}

        result: Dict[str, Any] = {}

        for key, value in nested_dict.items():
            new_key = f"{parent_key}{self.separator}{key}" if parent_key else key

            if isinstance(value, dict):
                # Recurse into nested dict
                nested_flat = self._flatten_dict(value, parent_key=new_key, depth=depth + 1)
                result.update(nested_flat)

            elif isinstance(value, list):
                if not value:
                    # Empty list → None
                    result[new_key] = None
                elif all(isinstance(v, (str, int, float, bool, type(None))) for v in value):
                    # List of primitives → JSON string (Req 6.4)
                    result[new_key] = json.dumps(value)
                else:
                    # List of dicts (or mixed) → keep as raw list for explosion
                    # Flatten each dict item first so nested keys are resolved
                    flattened_items = []
                    for item in value:
                        if isinstance(item, dict):
                            flat_item = self._flatten_dict(item, parent_key=new_key, depth=depth + 1)
                            flattened_items.append(flat_item)
                        else:
                            flattened_items.append({new_key: item})
                    result[new_key] = flattened_items  # kept as list for explosion

            else:
                # Primitive value
                result[new_key] = value

        return result

    def _handle_list_field(
        self,
        key: str,
        value: List[Any],
    ) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Handle a list field according to the configured strategy.

        Args:
            key: The flattened key name for this list field
            value: The list value (already partially flattened dicts or primitives)

        Returns:
            Either a single dict or a list of dicts
        """
        if not value:
            return {key: None}

        # Check if items are already-flattened dicts (from _flatten_dict)
        if all(isinstance(item, dict) for item in value):
            if self.handle_lists == "json_string":
                return {key: json.dumps(value)}
            elif self.handle_lists == "index":
                result: Dict[str, Any] = {}
                for i, item in enumerate(value):
                    for k, v in item.items():
                        result[f"{k}{self.separator}{i}"] = v
                return result
            else:  # "explode" (default)
                # Each dict becomes a separate record
                return value  # list of dicts

        # List of primitives → JSON string (Req 6.4)
        return {key: json.dumps(value)}
