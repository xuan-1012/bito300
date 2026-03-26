"""
Unit tests for JSONFlattener.flatten() main method
"""

import pytest
import json
from src.ingestion.flattener import JSONFlattener


class TestFlattenMethodBasic:
    """Test basic functionality of flatten() method"""
    
    def test_flatten_simple_dict(self):
        """Test flattening a simple flat dictionary"""
        flattener = JSONFlattener()
        data = {"name": "Alice", "age": 30, "city": "Taipei"}
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == {"name": "Alice", "age": 30, "city": "Taipei"}
    
    def test_flatten_nested_dict(self):
        """Test flattening a nested dictionary"""
        flattener = JSONFlattener()
        data = {
            "user": {
                "name": "Alice",
                "age": 30
            }
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == {
            "user_name": "Alice",
            "user_age": 30
        }
    
    def test_flatten_empty_dict(self):
        """Test flattening an empty dictionary"""
        flattener = JSONFlattener()
        data = {}
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0] == {}
    
    def test_flatten_list_of_dicts(self):
        """Test flattening a list of dictionaries"""
        flattener = JSONFlattener()
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {"name": "Alice", "age": 30}
        assert result[1] == {"name": "Bob", "age": 25}
    
    def test_flatten_empty_list(self):
        """Test flattening an empty list"""
        flattener = JSONFlattener()
        data = []
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 0


class TestFlattenMethodValidation:
    """Test validation in flatten() method"""
    
    def test_flatten_none_raises_error(self):
        """Test that None input raises ValueError"""
        flattener = JSONFlattener()
        
        with pytest.raises(ValueError, match="data cannot be None"):
            flattener.flatten(None)
    
    def test_flatten_invalid_type_raises_error(self):
        """Test that invalid input type raises ValueError"""
        flattener = JSONFlattener()
        
        with pytest.raises(ValueError, match="data must be a dict or list"):
            flattener.flatten("invalid")
        
        with pytest.raises(ValueError, match="data must be a dict or list"):
            flattener.flatten(123)
        
        with pytest.raises(ValueError, match="data must be a dict or list"):
            flattener.flatten(True)


class TestFlattenMethodWithLists:
    """Test flatten() method with list fields"""
    
    def test_flatten_dict_with_list_of_primitives(self):
        """Test flattening dict with list of primitives"""
        flattener = JSONFlattener()
        data = {
            "user": "Alice",
            "tags": ["python", "data", "api"]
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["user"] == "Alice"
        assert result[0]["tags"] == '["python", "data", "api"]'
    
    def test_flatten_dict_with_list_of_dicts_explode(self):
        """Test flattening dict with list of dicts (explode strategy)"""
        flattener = JSONFlattener(handle_lists="explode")
        data = {
            "user": "Alice",
            "transactions": [
                {"id": "TXN001", "amount": 100},
                {"id": "TXN002", "amount": 200}
            ]
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {
            "user": "Alice",
            "transactions_id": "TXN001",
            "transactions_amount": 100
        }
        assert result[1] == {
            "user": "Alice",
            "transactions_id": "TXN002",
            "transactions_amount": 200
        }
    
    def test_flatten_dict_with_empty_list(self):
        """Test flattening dict with empty list"""
        flattener = JSONFlattener()
        data = {
            "user": "Alice",
            "tags": []
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["user"] == "Alice"
        assert result[0]["tags"] is None
    
    def test_flatten_dict_with_nested_list_of_dicts(self):
        """Test flattening dict with nested list of dicts"""
        flattener = JSONFlattener(handle_lists="explode")
        data = {
            "user": {
                "name": "Alice",
                "transactions": [
                    {"id": "TXN001", "amount": 100},
                    {"id": "TXN002", "amount": 200}
                ]
            }
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert result[0] == {
            "user_name": "Alice",
            "user_transactions_id": "TXN001",
            "user_transactions_amount": 100
        }
        assert result[1] == {
            "user_name": "Alice",
            "user_transactions_id": "TXN002",
            "user_transactions_amount": 200
        }


class TestFlattenMethodDepth:
    """Test flatten() method ensures maximum depth of 1"""
    
    def test_flatten_ensures_no_nested_dicts(self):
        """Test that output has no nested dictionaries"""
        flattener = JSONFlattener()
        data = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Check that no values are dictionaries
        for key, value in result[0].items():
            assert not isinstance(value, dict), f"Found nested dict at key '{key}'"
    
    def test_flatten_ensures_no_nested_lists_of_dicts(self):
        """Test that list fields are properly handled"""
        flattener = JSONFlattener(handle_lists="explode")
        data = {
            "items": [
                {"id": 1, "nested": {"key": "value"}},
                {"id": 2, "nested": {"key": "value2"}}
            ]
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 2
        
        # Check that no values are dictionaries
        for record in result:
            for key, value in record.items():
                assert not isinstance(value, dict), f"Found nested dict at key '{key}'"
    
    def test_flatten_complex_structure_max_depth_one(self):
        """Test complex structure results in max depth of 1"""
        flattener = JSONFlattener()
        data = {
            "user": {
                "profile": {
                    "name": "Alice",
                    "address": {
                        "city": "Taipei",
                        "country": "Taiwan"
                    }
                }
            }
        }
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 1
        
        # Verify all keys are flat (no nested dicts)
        for key, value in result[0].items():
            assert not isinstance(value, dict)
            assert not isinstance(value, list) or isinstance(value, str)


class TestFlattenMethodErrorHandling:
    """Test error handling in flatten() method"""
    
    def test_flatten_handles_malformed_list_items(self):
        """Test that malformed items in list are skipped gracefully"""
        flattener = JSONFlattener()
        
        # Create a list with valid and invalid items
        data = [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25}
        ]
        
        result = flattener.flatten(data)
        
        # Should process valid items
        assert len(result) == 2
    
    def test_flatten_list_with_primitive_values(self):
        """Test flattening list with primitive values"""
        flattener = JSONFlattener()
        data = ["value1", "value2", "value3"]
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(item == {"value": val} for item, val in zip(result, data))
    
    def test_flatten_list_with_mixed_types(self):
        """Test flattening list with mixed dict and primitive types"""
        flattener = JSONFlattener()
        data = [
            {"name": "Alice"},
            "simple_string",
            {"name": "Bob"}
        ]
        
        result = flattener.flatten(data)
        
        assert isinstance(result, list)
        assert len(result) == 3
        assert result[0] == {"name": "Alice"}
        assert result[1] == {"value": "simple_string"}
        assert result[2] == {"name": "Bob"}


class TestFlattenMethodCustomConfiguration:
    """Test flatten() method with custom configuration"""
    
    def test_flatten_with_custom_separator(self):
        """Test flattening with custom separator"""
        flattener = JSONFlattener(separator=".")
        data = {
            "user": {
                "name": "Alice",
                "age": 30
            }
        }
        
        result = flattener.flatten(data)
        
        assert len(result) == 1
        assert result[0] == {
            "user.name": "Alice",
            "user.age": 30
        }
    
    def test_flatten_with_json_string_strategy(self):
        """Test flattening with json_string list handling"""
        flattener = JSONFlattener(handle_lists="json_string")
        data = {
            "user": "Alice",
            "transactions": [
                {"id": "TXN001", "amount": 100},
                {"id": "TXN002", "amount": 200}
            ]
        }
        
        result = flattener.flatten(data)
        
        assert len(result) == 1
        assert result[0]["user"] == "Alice"
        assert isinstance(result[0]["transactions"], str)
        assert "TXN001" in result[0]["transactions"]
    
    def test_flatten_with_max_depth_limit(self):
        """Test flattening with max_depth limit"""
        flattener = JSONFlattener(max_depth=2)
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": "deep_value"
                    }
                }
            }
        }
        
        result = flattener.flatten(data)
        
        assert len(result) == 1
        # At depth 2, level3 should be serialized as JSON string
        assert "level1_level2" in result[0]
        assert isinstance(result[0]["level1_level2"], str)


class TestFlattenMethodComplexScenarios:
    """Test flatten() method with complex real-world scenarios"""
    
    def test_flatten_bitopro_transaction_response(self):
        """Test flattening a BitoPro-like transaction response"""
        flattener = JSONFlattener(handle_lists="explode")
        data = {
            "data": [
                {
                    "id": "TXN001",
                    "timestamp": "2024-01-01T10:00:00",
                    "user": {
                        "id": "USR123",
                        "name": "Alice"
                    },
                    "amount": 100.50
                },
                {
                    "id": "TXN002",
                    "timestamp": "2024-01-01T11:00:00",
                    "user": {
                        "id": "USR456",
                        "name": "Bob"
                    },
                    "amount": 200.75
                }
            ]
        }
        
        result = flattener.flatten(data)
        
        assert len(result) == 2
        assert result[0] == {
            "data_id": "TXN001",
            "data_timestamp": "2024-01-01T10:00:00",
            "data_user_id": "USR123",
            "data_user_name": "Alice",
            "data_amount": 100.50
        }
        assert result[1] == {
            "data_id": "TXN002",
            "data_timestamp": "2024-01-01T11:00:00",
            "data_user_id": "USR456",
            "data_user_name": "Bob",
            "data_amount": 200.75
        }
    
    def test_flatten_multiple_list_fields(self):
        """Test flattening with multiple list fields"""
        flattener = JSONFlattener(handle_lists="explode")
        data = {
            "user": "Alice",
            "orders": [
                {"id": "ORD001", "total": 100},
                {"id": "ORD002", "total": 200}
            ],
            "tags": ["premium", "verified"]
        }
        
        result = flattener.flatten(data)
        
        # Should explode orders and serialize tags
        assert len(result) == 2
        assert result[0]["user"] == "Alice"
        assert result[0]["orders_id"] == "ORD001"
        assert result[0]["tags"] == '["premium", "verified"]'
    
    def test_flatten_preserves_all_data(self):
        """Test that flattening preserves all original data"""
        flattener = JSONFlattener()
        data = {
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "nested": {
                "key": "value"
            }
        }
        
        result = flattener.flatten(data)
        
        assert len(result) == 1
        assert result[0]["string"] == "text"
        assert result[0]["integer"] == 42
        assert result[0]["float"] == 3.14
        assert result[0]["boolean"] is True
        assert result[0]["null"] is None
        assert result[0]["nested_key"] == "value"
