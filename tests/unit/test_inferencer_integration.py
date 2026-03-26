"""
Integration tests for SchemaInferencer initialization
"""

import pytest
from src.ingestion.inferencer import SchemaInferencer, FieldType, FieldSchema


class TestSchemaInferencerIntegration:
    """Integration tests for SchemaInferencer"""
    
    def test_inferencer_can_be_instantiated_with_defaults(self):
        """Test that SchemaInferencer can be created with default settings"""
        inferencer = SchemaInferencer()
        
        # Verify it's properly initialized
        assert isinstance(inferencer, SchemaInferencer)
        assert inferencer.sample_size > 0
        assert 0 <= inferencer.confidence_threshold <= 1
    
    def test_inferencer_configuration_is_accessible(self):
        """Test that configuration parameters are accessible after initialization"""
        sample_size = 150
        confidence = 0.85
        
        inferencer = SchemaInferencer(
            sample_size=sample_size,
            confidence_threshold=confidence
        )
        
        # Verify configuration is stored and accessible
        assert inferencer.sample_size == sample_size
        assert inferencer.confidence_threshold == confidence
    
    def test_multiple_inferencers_with_different_configs(self):
        """Test that multiple SchemaInferencer instances can coexist with different configs"""
        inferencer1 = SchemaInferencer(sample_size=50, confidence_threshold=0.7)
        inferencer2 = SchemaInferencer(sample_size=200, confidence_threshold=0.9)
        
        # Verify they maintain independent configurations
        assert inferencer1.sample_size == 50
        assert inferencer1.confidence_threshold == 0.7
        assert inferencer2.sample_size == 200
        assert inferencer2.confidence_threshold == 0.9
    
    def test_field_type_enum_is_usable(self):
        """Test that FieldType enum can be used in FieldSchema"""
        schema = FieldSchema(
            name="test",
            inferred_type=FieldType.NUMERIC,
            nullable=False,
            sample_values=[1, 2, 3],
            null_count=0,
            total_count=3,
            confidence=0.95
        )
        
        assert schema.inferred_type == FieldType.NUMERIC
        assert schema.inferred_type.value == "numeric"
    
    def test_all_field_types_are_accessible(self):
        """Test that all FieldType enum values are accessible"""
        field_types = [
            FieldType.NUMERIC,
            FieldType.CATEGORICAL,
            FieldType.DATETIME,
            FieldType.TEXT,
            FieldType.ID_LIKE,
            FieldType.BOOLEAN,
            FieldType.NULL,
            FieldType.MIXED
        ]
        
        # Verify all types are unique and accessible
        assert len(field_types) == len(set(field_types))
        assert all(isinstance(ft, FieldType) for ft in field_types)
