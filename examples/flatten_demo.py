"""
Demonstration of JSONFlattener.flatten() method

This script demonstrates the main flatten() method functionality
with various input scenarios.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ingestion.flattener import JSONFlattener
import json


def demo_simple_dict():
    """Demo: Flatten a simple dictionary"""
    print("=" * 60)
    print("Demo 1: Simple Dictionary")
    print("=" * 60)
    
    flattener = JSONFlattener()
    data = {"name": "Alice", "age": 30, "city": "Taipei"}
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


def demo_nested_dict():
    """Demo: Flatten a nested dictionary"""
    print("=" * 60)
    print("Demo 2: Nested Dictionary")
    print("=" * 60)
    
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
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


def demo_list_of_dicts():
    """Demo: Flatten a list of dictionaries"""
    print("=" * 60)
    print("Demo 3: List of Dictionaries")
    print("=" * 60)
    
    flattener = JSONFlattener()
    data = [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25}
    ]
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


def demo_dict_with_list_explode():
    """Demo: Flatten dict with list of dicts (explode strategy)"""
    print("=" * 60)
    print("Demo 4: Dict with List of Dicts (Explode)")
    print("=" * 60)
    
    flattener = JSONFlattener(handle_lists="explode")
    data = {
        "user": "Alice",
        "transactions": [
            {"id": "TXN001", "amount": 100},
            {"id": "TXN002", "amount": 200}
        ]
    }
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


def demo_bitopro_response():
    """Demo: Flatten a BitoPro-like API response"""
    print("=" * 60)
    print("Demo 5: BitoPro-like Transaction Response")
    print("=" * 60)
    
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
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


def demo_custom_separator():
    """Demo: Flatten with custom separator"""
    print("=" * 60)
    print("Demo 6: Custom Separator (dot notation)")
    print("=" * 60)
    
    flattener = JSONFlattener(separator=".")
    data = {
        "user": {
            "name": "Alice",
            "age": 30
        }
    }
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


def demo_max_depth():
    """Demo: Flatten with max depth limit"""
    print("=" * 60)
    print("Demo 7: Max Depth Limit (depth=2)")
    print("=" * 60)
    
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
    
    print(f"Input: {json.dumps(data, indent=2)}")
    result = flattener.flatten(data)
    print(f"Output: {json.dumps(result, indent=2)}")
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("JSONFlattener.flatten() Method Demonstration")
    print("*" * 60)
    print("\n")
    
    demo_simple_dict()
    demo_nested_dict()
    demo_list_of_dicts()
    demo_dict_with_list_explode()
    demo_bitopro_response()
    demo_custom_separator()
    demo_max_depth()
    
    print("*" * 60)
    print("All demonstrations completed successfully!")
    print("*" * 60)
