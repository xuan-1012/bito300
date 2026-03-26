"""
Property-based tests for JSONFlattener.

**Property: Flattened output never exceeds depth 1 (no nested dicts)**
**Property: All original primitive data is preserved in the output**
**Validates: Requirements 6.6**
"""

import json
import pytest
from hypothesis import given, strategies as st, settings, assume
from src.ingestion.flattener import JSONFlattener


# ---------------------------------------------------------------------------
# Hypothesis strategies
# ---------------------------------------------------------------------------

# A strategy for JSON-serializable primitive values
json_primitives = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(min_value=-1_000_000, max_value=1_000_000),
    st.floats(allow_nan=False, allow_infinity=False, min_value=-1e9, max_value=1e9),
    st.text(max_size=20),
)

# A strategy for flat dicts (no nesting)
flat_dict = st.dictionaries(
    keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8),
    values=json_primitives,
    max_size=5,
)

# A strategy for one level of nesting
nested_dict_1 = st.dictionaries(
    keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8),
    values=st.one_of(json_primitives, flat_dict),
    max_size=4,
)

# A strategy for two levels of nesting
nested_dict_2 = st.dictionaries(
    keys=st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=8),
    values=st.one_of(json_primitives, flat_dict, nested_dict_1),
    max_size=4,
)

# A strategy for lists of flat dicts (for list-explosion testing)
list_of_flat_dicts = st.lists(flat_dict, min_size=1, max_size=4)


def _max_depth(obj, current=0) -> int:
    """Compute the maximum nesting depth of a Python object."""
    if isinstance(obj, dict):
        if not obj:
            return current
        return max(_max_depth(v, current + 1) for v in obj.values())
    if isinstance(obj, list):
        if not obj:
            return current
        return max(_max_depth(v, current) for v in obj)
    return current


def _collect_primitives(obj) -> list:
    """Recursively collect all primitive (non-container) values from a structure."""
    primitives = []
    if isinstance(obj, dict):
        for v in obj.values():
            primitives.extend(_collect_primitives(v))
    elif isinstance(obj, list):
        for item in obj:
            primitives.extend(_collect_primitives(item))
    else:
        primitives.append(obj)
    return primitives


# ---------------------------------------------------------------------------
# Property 1: Output depth never exceeds 1
# **Validates: Requirements 6.6**
# ---------------------------------------------------------------------------

class TestFlatteningDepthProperty:
    """
    Property: Flattened output never exceeds depth 1 (no nested dicts).
    **Validates: Requirements 6.6**
    """

    @given(nested_dict_2)
    @settings(max_examples=200, deadline=None)
    def test_flattened_output_has_no_nested_dicts(self, data):
        """
        Property: For any nested dict input, every value in every flattened
        record is NOT a dict (i.e. max depth = 1).

        **Validates: Requirements 6.6**
        """
        flattener = JSONFlattener()
        records = flattener.flatten(data)

        assert isinstance(records, list), "flatten() must return a list"
        for rec in records:
            assert isinstance(rec, dict), "Each record must be a dict"
            for key, value in rec.items():
                assert not isinstance(value, dict), (
                    f"Found nested dict at key '{key}' in record {rec!r}. "
                    f"Input was: {data!r}"
                )

    @given(st.lists(nested_dict_1, min_size=1, max_size=5))
    @settings(max_examples=100, deadline=None)
    def test_list_input_flattened_output_has_no_nested_dicts(self, data):
        """
        Property: For a list of nested dicts, every value in every flattened
        record is NOT a dict.

        **Validates: Requirements 6.6**
        """
        flattener = JSONFlattener()
        records = flattener.flatten(data)

        for rec in records:
            for key, value in rec.items():
                assert not isinstance(value, dict), (
                    f"Found nested dict at key '{key}'. Input was: {data!r}"
                )

    @given(nested_dict_2, st.integers(min_value=1, max_value=5))
    @settings(max_examples=100, deadline=None)
    def test_depth_property_holds_for_various_max_depths(self, data, max_depth):
        """
        Property: The no-nested-dict guarantee holds regardless of max_depth
        configuration.

        **Validates: Requirements 6.6**
        """
        flattener = JSONFlattener(max_depth=max_depth)
        records = flattener.flatten(data)

        for rec in records:
            for key, value in rec.items():
                assert not isinstance(value, dict), (
                    f"Found nested dict at key '{key}' with max_depth={max_depth}. "
                    f"Input was: {data!r}"
                )


# ---------------------------------------------------------------------------
# Property 2: All original primitive data is preserved
# **Validates: Requirements 6.6**
# ---------------------------------------------------------------------------

class TestDataPreservationProperty:
    """
    Property: All original primitive values are preserved in the flattened output.
    **Validates: Requirements 6.6**
    """

    @given(flat_dict)
    @settings(max_examples=200, deadline=None)
    def test_flat_dict_all_values_preserved(self, data):
        """
        Property: For a flat (non-nested) dict, all values appear unchanged
        in the single flattened record.

        **Validates: Requirements 6.6**
        """
        flattener = JSONFlattener()
        records = flattener.flatten(data)

        assert len(records) == 1
        rec = records[0]
        for key, value in data.items():
            assert key in rec, f"Key '{key}' missing from flattened record"
            assert rec[key] == value, (
                f"Value for key '{key}' changed: expected {value!r}, got {rec[key]!r}"
            )

    @given(nested_dict_1)
    @settings(max_examples=200, deadline=None)
    def test_nested_dict_primitives_preserved(self, data):
        """
        Property: All primitive values from a nested dict appear somewhere in
        the flattened output (possibly under a different key due to concatenation).

        **Validates: Requirements 6.6**
        """
        flattener = JSONFlattener()
        records = flattener.flatten(data)

        # Collect all primitive values from the original data
        original_primitives = _collect_primitives(data)

        # Collect all primitive values from the flattened output.
        # String values that look like JSON arrays/objects may be serialized
        # lists – parse only those (starts with '[' or '{') to recover their
        # original primitives.  Plain strings are kept as-is.
        output_primitives = []
        for rec in records:
            for v in rec.values():
                if isinstance(v, str) and (v.startswith("[") or v.startswith("{")):
                    try:
                        parsed = json.loads(v)
                        output_primitives.extend(_collect_primitives(parsed))
                    except (json.JSONDecodeError, ValueError):
                        output_primitives.append(v)
                else:
                    output_primitives.append(v)

        # Every original primitive should appear in the output
        for prim in original_primitives:
            assert prim in output_primitives, (
                f"Primitive value {prim!r} from input {data!r} not found in "
                f"flattened output primitives: {output_primitives!r}"
            )
