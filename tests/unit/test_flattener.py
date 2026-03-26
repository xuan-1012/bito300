"""
Unit tests for JSONFlattener component.

Covers:
- Initialization and configuration validation
- Nested dictionary flattening
- List explosion (list of dicts → multiple records)
- Primitive list serialization as JSON strings
- Max depth enforcement
- Empty / edge-case inputs
"""

import json
import pytest
from src.ingestion.flattener import JSONFlattener


# ---------------------------------------------------------------------------
# Initialization tests (Task 5.1)
# ---------------------------------------------------------------------------

class TestJSONFlattenerInit:
    def test_default_initialization(self):
        f = JSONFlattener()
        assert f.separator == "_"
        assert f.max_depth == 10
        assert f.handle_lists == "explode"

    def test_custom_separator(self):
        f = JSONFlattener(separator=".")
        assert f.separator == "."

    def test_custom_max_depth(self):
        f = JSONFlattener(max_depth=3)
        assert f.max_depth == 3

    def test_custom_handle_lists(self):
        f = JSONFlattener(handle_lists="json_string")
        assert f.handle_lists == "json_string"

    def test_invalid_separator_empty(self):
        with pytest.raises(ValueError, match="separator"):
            JSONFlattener(separator="")

    def test_invalid_separator_non_string(self):
        with pytest.raises(ValueError, match="separator"):
            JSONFlattener(separator=123)

    def test_invalid_max_depth_zero(self):
        with pytest.raises(ValueError, match="max_depth"):
            JSONFlattener(max_depth=0)

    def test_invalid_max_depth_negative(self):
        with pytest.raises(ValueError, match="max_depth"):
            JSONFlattener(max_depth=-1)

    def test_invalid_handle_lists(self):
        with pytest.raises(ValueError, match="handle_lists"):
            JSONFlattener(handle_lists="unknown_strategy")


# ---------------------------------------------------------------------------
# _flatten_dict tests (Task 5.2)
# ---------------------------------------------------------------------------

class TestFlattenDict:
    def setup_method(self):
        self.f = JSONFlattener(separator="_")

    def test_flat_dict_unchanged(self):
        data = {"a": 1, "b": "hello"}
        result = self.f._flatten_dict(data)
        assert result == {"a": 1, "b": "hello"}

    def test_one_level_nesting(self):
        data = {"user": {"name": "Alice", "age": 30}}
        result = self.f._flatten_dict(data)
        assert result == {"user_name": "Alice", "user_age": 30}

    def test_two_level_nesting(self):
        data = {"a": {"b": {"c": 42}}}
        result = self.f._flatten_dict(data)
        assert result == {"a_b_c": 42}

    def test_custom_separator(self):
        f = JSONFlattener(separator=".")
        data = {"a": {"b": 1}}
        result = f._flatten_dict(data)
        assert result == {"a.b": 1}

    def test_max_depth_serializes_remaining(self):
        f = JSONFlattener(max_depth=1)
        data = {"a": {"b": {"c": 1}}}
        result = f._flatten_dict(data)
        # At depth 1 the nested dict {"b": {"c": 1}} should be JSON-serialized
        assert "a" in result
        parsed = json.loads(result["a"])
        assert parsed == {"b": {"c": 1}}

    def test_max_depth_at_root(self):
        f = JSONFlattener(max_depth=1)
        # depth=0 is fine, but depth=1 triggers serialization
        data = {"x": 1}
        result = f._flatten_dict(data, depth=1)
        assert "_raw" in result or list(result.values())[0] == json.dumps({"x": 1})

    def test_primitive_values_preserved(self):
        data = {"int": 1, "float": 3.14, "bool": True, "none": None, "str": "hi"}
        result = self.f._flatten_dict(data)
        assert result["int"] == 1
        assert result["float"] == 3.14
        assert result["bool"] is True
        assert result["none"] is None
        assert result["str"] == "hi"

    def test_empty_dict(self):
        result = self.f._flatten_dict({})
        assert result == {}

    def test_primitive_list_serialized_as_json(self):
        data = {"tags": ["a", "b", "c"]}
        result = self.f._flatten_dict(data)
        assert result["tags"] == json.dumps(["a", "b", "c"])

    def test_empty_list_becomes_none(self):
        data = {"items": []}
        result = self.f._flatten_dict(data)
        assert result["items"] is None


# ---------------------------------------------------------------------------
# _handle_list_field tests (Task 5.3)
# ---------------------------------------------------------------------------

class TestHandleListField:
    def setup_method(self):
        self.f = JSONFlattener(handle_lists="explode")

    def test_empty_list_returns_none(self):
        result = self.f._handle_list_field("items", [])
        assert result == {"items": None}

    def test_list_of_dicts_explode(self):
        items = [{"id": 1}, {"id": 2}]
        result = self.f._handle_list_field("items", items)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_list_of_primitives_json_string(self):
        result = self.f._handle_list_field("tags", ["a", "b"])
        assert result == {"tags": json.dumps(["a", "b"])}

    def test_json_string_strategy(self):
        f = JSONFlattener(handle_lists="json_string")
        items = [{"id": 1}, {"id": 2}]
        result = f._handle_list_field("items", items)
        assert isinstance(result, dict)
        assert "items" in result
        parsed = json.loads(result["items"])
        assert len(parsed) == 2

    def test_index_strategy(self):
        f = JSONFlattener(handle_lists="index")
        items = [{"id": 1}, {"id": 2}]
        result = f._handle_list_field("items", items)
        assert isinstance(result, dict)
        # Should have indexed keys like items_id_0, items_id_1
        assert any("_0" in k for k in result)
        assert any("_1" in k for k in result)


# ---------------------------------------------------------------------------
# flatten() main method tests (Task 5.4)
# ---------------------------------------------------------------------------

class TestFlatten:
    def setup_method(self):
        self.f = JSONFlattener()

    def test_flat_dict_input(self):
        data = {"a": 1, "b": 2}
        result = self.f.flatten(data)
        assert result == [{"a": 1, "b": 2}]

    def test_nested_dict_input(self):
        data = {"user": {"name": "Alice", "age": 30}}
        result = self.f.flatten(data)
        assert len(result) == 1
        assert result[0]["user_name"] == "Alice"
        assert result[0]["user_age"] == 30

    def test_list_of_dicts_input(self):
        data = [{"id": 1}, {"id": 2}]
        result = self.f.flatten(data)
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert result[1]["id"] == 2

    def test_list_field_explodes_into_multiple_records(self):
        data = {
            "name": "Alice",
            "orders": [
                {"order_id": "O1", "amount": 100},
                {"order_id": "O2", "amount": 200},
            ],
        }
        result = self.f.flatten(data)
        assert len(result) == 2
        for rec in result:
            assert rec["name"] == "Alice"
            assert "orders_order_id" in rec
            assert "orders_amount" in rec

    def test_output_has_no_nested_dicts(self):
        data = {"a": {"b": {"c": {"d": 1}}}}
        result = self.f.flatten(data)
        for rec in result:
            for v in rec.values():
                assert not isinstance(v, dict), f"Found nested dict: {v}"

    def test_empty_dict_input(self):
        result = self.f.flatten({})
        assert result == [{}]

    def test_empty_list_input(self):
        result = self.f.flatten([])
        assert result == []

    def test_primitive_list_field_serialized(self):
        data = {"tags": [1, 2, 3]}
        result = self.f.flatten(data)
        assert len(result) == 1
        assert result[0]["tags"] == json.dumps([1, 2, 3])

    def test_deeply_nested_respects_max_depth(self):
        f = JSONFlattener(max_depth=2)
        data = {"a": {"b": {"c": {"d": 1}}}}
        result = f.flatten(data)
        assert len(result) == 1
        rec = result[0]
        # No value should be a dict
        for v in rec.values():
            assert not isinstance(v, dict)

    def test_design_example(self):
        """Verify the design doc example produces expected output."""
        data = {
            "user": {
                "id": "USR123",
                "profile": {
                    "name": "Alice",
                    "address": {
                        "city": "Taipei",
                        "country": "Taiwan",
                    },
                },
            },
            "transactions": [
                {"id": "TXN001", "amount": 100.0},
                {"id": "TXN002", "amount": 200.0},
            ],
        }
        result = self.f.flatten(data)
        assert len(result) == 2
        for rec in result:
            assert rec["user_id"] == "USR123"
            assert rec["user_profile_name"] == "Alice"
            assert rec["user_profile_address_city"] == "Taipei"
            assert rec["user_profile_address_country"] == "Taiwan"
        ids = {rec["transactions_id"] for rec in result}
        assert ids == {"TXN001", "TXN002"}

    def test_scalar_top_level_input(self):
        result = self.f.flatten(42)
        assert result == [{"value": 42}]
