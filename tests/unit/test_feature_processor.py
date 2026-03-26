"""
Unit tests for FeatureProcessor.

Tests validation rules, normalization, and feature vector conversion.
"""

import pytest

from src.model_risk_scoring.exceptions import ValidationError
from src.model_risk_scoring.models.data_models import TransactionFeatures
from src.model_risk_scoring.utils import FeatureProcessor


class TestFeatureProcessorValidation:
    """Test FeatureProcessor validation rules."""
    
    def test_validate_valid_features(self):
        """Test validation passes for valid features."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        assert processor.validate(features) is True
    
    def test_validate_empty_account_id(self):
        """Test validation fails for empty account_id."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "account_id must be non-empty" in str(exc_info.value)
        assert exc_info.value.field == "account_id"
    
    def test_validate_whitespace_account_id(self):
        """Test validation fails for whitespace-only account_id."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="   ",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "account_id must be non-empty" in str(exc_info.value)
    
    def test_validate_negative_total_volume(self):
        """Test validation fails for negative total_volume."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=-1000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "total_volume must be >= 0" in str(exc_info.value)
        assert exc_info.value.field == "total_volume"
    
    def test_validate_zero_total_volume(self):
        """Test validation passes for zero total_volume."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=0.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        assert processor.validate(features) is True
    
    def test_validate_zero_transaction_count(self):
        """Test validation fails for zero transaction_count."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=0,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "transaction_count must be > 0" in str(exc_info.value)
        assert exc_info.value.field == "transaction_count"
    
    def test_validate_negative_transaction_count(self):
        """Test validation fails for negative transaction_count."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=-5,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "transaction_count must be > 0" in str(exc_info.value)
    
    def test_validate_night_transaction_ratio_below_zero(self):
        """Test validation fails for night_transaction_ratio < 0."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=-0.1,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "night_transaction_ratio must be between 0 and 1" in str(exc_info.value)
        assert exc_info.value.field == "night_transaction_ratio"
    
    def test_validate_night_transaction_ratio_above_one(self):
        """Test validation fails for night_transaction_ratio > 1."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=1.5,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "night_transaction_ratio must be between 0 and 1" in str(exc_info.value)
    
    def test_validate_night_transaction_ratio_boundary_values(self):
        """Test validation passes for night_transaction_ratio at boundaries (0 and 1)."""
        processor = FeatureProcessor()
        
        # Test 0
        features_zero = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.0,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        assert processor.validate(features_zero) is True
        
        # Test 1
        features_one = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=1.0,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        assert processor.validate(features_one) is True
    
    def test_validate_round_number_ratio_below_zero(self):
        """Test validation fails for round_number_ratio < 0."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=-0.2,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "round_number_ratio must be between 0 and 1" in str(exc_info.value)
        assert exc_info.value.field == "round_number_ratio"
    
    def test_validate_round_number_ratio_above_one(self):
        """Test validation fails for round_number_ratio > 1."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=1.1,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "round_number_ratio must be between 0 and 1" in str(exc_info.value)
    
    def test_validate_concentration_score_below_zero(self):
        """Test validation fails for concentration_score < 0."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=-0.1,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "concentration_score must be between 0 and 1" in str(exc_info.value)
        assert exc_info.value.field == "concentration_score"
    
    def test_validate_concentration_score_above_one(self):
        """Test validation fails for concentration_score > 1."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=1.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError) as exc_info:
            processor.validate(features)
        
        assert "concentration_score must be between 0 and 1" in str(exc_info.value)


class TestFeatureProcessorNormalization:
    """Test FeatureProcessor normalization."""
    
    def test_normalize_without_scaler_params(self):
        """Test normalization returns raw values when no scaler_params provided."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        normalized = processor.normalize(features)
        
        assert normalized["total_volume"] == 50000.0
        assert normalized["transaction_count"] == 100.0
        assert normalized["avg_transaction_size"] == 500.0
        assert normalized["night_transaction_ratio"] == 0.2
    
    def test_normalize_with_scaler_params(self):
        """Test normalization applies Z-score when scaler_params provided."""
        scaler_params = {
            "total_volume": {"mean": 50000.0, "std": 10000.0},
            "transaction_count": {"mean": 100.0, "std": 20.0}
        }
        processor = FeatureProcessor(scaler_params=scaler_params)
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=60000.0,  # (60000 - 50000) / 10000 = 1.0
            transaction_count=120,  # (120 - 100) / 20 = 1.0
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        normalized = processor.normalize(features)
        
        assert normalized["total_volume"] == 1.0
        assert normalized["transaction_count"] == 1.0
        # Features without scaler params should remain unchanged
        assert normalized["avg_transaction_size"] == 500.0
    
    def test_normalize_handles_zero_std(self):
        """Test normalization handles zero standard deviation."""
        scaler_params = {
            "total_volume": {"mean": 50000.0, "std": 0.0}
        }
        processor = FeatureProcessor(scaler_params=scaler_params)
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=60000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        normalized = processor.normalize(features)
        
        # Should return 0.0 when std is 0 to avoid division by zero
        assert normalized["total_volume"] == 0.0
    
    def test_normalize_validates_features_first(self):
        """Test normalization validates features before normalizing."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="",  # Invalid
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError):
            processor.normalize(features)


class TestFeatureProcessorToVector:
    """Test FeatureProcessor to_vector conversion."""
    
    def test_to_vector_returns_correct_order(self):
        """Test to_vector returns features in correct order."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        vector = processor.to_vector(features)
        
        expected = [
            50000.0,  # total_volume
            100.0,    # transaction_count
            500.0,    # avg_transaction_size
            5000.0,   # max_transaction_size
            20.0,     # unique_counterparties
            0.2,      # night_transaction_ratio
            5.0,      # rapid_transaction_count
            0.3,      # round_number_ratio
            0.5,      # concentration_score
            2.5       # velocity_score
        ]
        
        assert vector == expected
    
    def test_to_vector_validates_features_first(self):
        """Test to_vector validates features before conversion."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=-1000.0,  # Invalid
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        with pytest.raises(ValidationError):
            processor.to_vector(features)
    
    def test_to_vector_converts_integers_to_floats(self):
        """Test to_vector converts integer features to floats."""
        processor = FeatureProcessor()
        features = TransactionFeatures(
            account_id="ACC123",
            total_volume=50000.0,
            transaction_count=100,
            avg_transaction_size=500.0,
            max_transaction_size=5000.0,
            unique_counterparties=20,
            night_transaction_ratio=0.2,
            rapid_transaction_count=5,
            round_number_ratio=0.3,
            concentration_score=0.5,
            velocity_score=2.5
        )
        
        vector = processor.to_vector(features)
        
        # All values should be floats
        assert all(isinstance(v, float) for v in vector)
