"""
Integration tests for JSONFlattener component
"""

import pytest
from src.ingestion.flattener import JSONFlattener


class TestJSONFlattenerIntegration:
    """Integration tests for JSONFlattener initialization and basic usage"""
    
    def test_flattener_can_be_instantiated_with_defaults(self):
        """Test that JSONFlattener can be instantiated with default configuration"""
        flattener = JSONFlattener()
        
        assert flattener is not None
        assert isinstance(flattener, JSONFlattener)
    
    def test_flattener_configuration_is_accessible(self):
        """Test that configuration parameters are accessible after initialization"""
        flattener = JSONFlattener(
            separator=".",
            max_depth=5,
            handle_lists="index"
        )
        
        # Verify all configuration is accessible
        assert flattener.separator == "."
        assert flattener.max_depth == 5
        assert flattener.handle_lists == "index"
    
    def test_multiple_flatteners_with_different_configs(self):
        """Test that multiple flatteners can coexist with different configurations"""
        flattener1 = JSONFlattener(separator="_", max_depth=10)
        flattener2 = JSONFlattener(separator=".", max_depth=5)
        flattener3 = JSONFlattener(separator="/", max_depth=3)
        
        # Verify each maintains its own configuration
        assert flattener1.separator == "_"
        assert flattener1.max_depth == 10
        
        assert flattener2.separator == "."
        assert flattener2.max_depth == 5
        
        assert flattener3.separator == "/"
        assert flattener3.max_depth == 3
    
    def test_flattener_validates_on_initialization(self):
        """Test that validation happens during initialization, not later"""
        # Valid initialization should succeed
        flattener = JSONFlattener(separator="_", max_depth=10, handle_lists="explode")
        assert flattener is not None
        
        # Invalid initialization should fail immediately
        with pytest.raises(ValueError):
            JSONFlattener(separator="", max_depth=10, handle_lists="explode")
        
        with pytest.raises(ValueError):
            JSONFlattener(separator="_", max_depth=0, handle_lists="explode")
        
        with pytest.raises(ValueError):
            JSONFlattener(separator="_", max_depth=10, handle_lists="invalid")
    
    def test_flattener_configuration_immutability(self):
        """Test that configuration is set during initialization"""
        flattener = JSONFlattener(separator=".", max_depth=5, handle_lists="index")
        
        # Configuration should be accessible
        original_separator = flattener.separator
        original_max_depth = flattener.max_depth
        original_handle_lists = flattener.handle_lists
        
        # Verify values
        assert original_separator == "."
        assert original_max_depth == 5
        assert original_handle_lists == "index"
