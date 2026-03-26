"""
Unit tests for core data models.
"""

import pytest
from datetime import datetime
from src.model_risk_scoring.models import (
    InferenceMode,
    RiskLevel,
    TransactionFeatures,
    RiskAssessment,
    ModelConfig,
    FeatureConfig,
)


class TestInferenceMode:
    """Tests for InferenceMode enum."""
    
    def test_inference_mode_values(self):
        """Test that InferenceMode has correct values."""
        assert InferenceMode.SUPERVISED.value == "supervised"
        assert InferenceMode.UNSUPERVISED.value == "unsupervised"
        assert InferenceMode.FALLBACK.value == "fallback"
    
    def test_inference_mode_members(self):
        """Test that all expected members exist."""
        modes = [mode.value for mode in InferenceMode]
        assert "supervised" in modes
        assert "unsupervised" in modes
        assert "fallback" in modes


class TestRiskLevel:
    """Tests for RiskLevel enum."""
    
    def test_risk_level_values(self):
        """Test that RiskLevel has correct level values."""
        assert RiskLevel.LOW.level == "low"
        assert RiskLevel.MEDIUM.level == "medium"
        assert RiskLevel.HIGH.level == "high"
        assert RiskLevel.CRITICAL.level == "critical"
    
    def test_risk_level_colors(self):
        """Test that RiskLevel has correct color codes."""
        assert RiskLevel.LOW.color == "#16a34a"  # Green
        assert RiskLevel.MEDIUM.color == "#ca8a04"  # Yellow
        assert RiskLevel.HIGH.color == "#ea580c"  # Orange
        assert RiskLevel.CRITICAL.color == "#dc2626"  # Red
    
    def test_risk_level_members(self):
        """Test that all expected risk levels exist."""
        levels = [level.level for level in RiskLevel]
        assert "low" in levels
        assert "medium" in levels
        assert "high" in levels
        assert "critical" in levels


class TestTransactionFeatures:
    """Tests for TransactionFeatures dataclass."""
    
    def test_create_transaction_features(self):
        """Test creating TransactionFeatures with valid data."""
        features = TransactionFeatures(
            account_id="account_123",
            total_volume=150000.0,
            transaction_count=50,
            avg_transaction_size=3000.0,
            max_transaction_size=25000.0,
            unique_counterparties=5,
            night_transaction_ratio=0.4,
            rapid_transaction_count=15,
            round_number_ratio=0.6,
            concentration_score=0.8,
            velocity_score=12.5
        )
        
        assert features.account_id == "account_123"
        assert features.total_volume == 150000.0
        assert features.transaction_count == 50
        assert features.avg_transaction_size == 3000.0
        assert features.max_transaction_size == 25000.0
        assert features.unique_counterparties == 5
        assert features.night_transaction_ratio == 0.4
        assert features.rapid_transaction_count == 15
        assert features.round_number_ratio == 0.6
        assert features.concentration_score == 0.8
        assert features.velocity_score == 12.5
    
    def test_transaction_features_all_fields_required(self):
        """Test that all fields are required."""
        with pytest.raises(TypeError):
            TransactionFeatures(account_id="account_123")


class TestRiskAssessment:
    """Tests for RiskAssessment dataclass."""
    
    def test_create_risk_assessment(self):
        """Test creating RiskAssessment with required fields."""
        assessment = RiskAssessment(
            account_id="account_123",
            risk_score=75.5,
            risk_level=RiskLevel.HIGH,
            risk_factors=["High volume", "Night transactions"],
            explanation="Account shows suspicious patterns",
            confidence=0.85,
            inference_mode=InferenceMode.UNSUPERVISED
        )
        
        assert assessment.account_id == "account_123"
        assert assessment.risk_score == 75.5
        assert assessment.risk_level == RiskLevel.HIGH
        assert assessment.risk_factors == ["High volume", "Night transactions"]
        assert assessment.explanation == "Account shows suspicious patterns"
        assert assessment.confidence == 0.85
        assert assessment.inference_mode == InferenceMode.UNSUPERVISED
    
    def test_risk_assessment_default_values(self):
        """Test that optional fields have correct defaults."""
        assessment = RiskAssessment(
            account_id="account_123",
            risk_score=50.0,
            risk_level=RiskLevel.MEDIUM,
            risk_factors=["Test"],
            explanation="Test explanation",
            confidence=0.8,
            inference_mode=InferenceMode.FALLBACK
        )
        
        assert assessment.model_id is None
        assert assessment.inference_time_ms == 0.0
        assert assessment.fallback_used is False
        assert assessment.feature_importance is None
        assert isinstance(assessment.timestamp, datetime)
    
    def test_risk_assessment_with_optional_fields(self):
        """Test creating RiskAssessment with optional fields."""
        feature_importance = {"total_volume": 0.3, "night_ratio": 0.2}
        
        assessment = RiskAssessment(
            account_id="account_123",
            risk_score=80.0,
            risk_level=RiskLevel.CRITICAL,
            risk_factors=["Critical risk"],
            explanation="Very high risk",
            confidence=0.9,
            inference_mode=InferenceMode.SUPERVISED,
            model_id="xgboost-endpoint",
            inference_time_ms=250.5,
            fallback_used=False,
            feature_importance=feature_importance
        )
        
        assert assessment.model_id == "xgboost-endpoint"
        assert assessment.inference_time_ms == 250.5
        assert assessment.fallback_used is False
        assert assessment.feature_importance == feature_importance


class TestModelConfig:
    """Tests for ModelConfig dataclass."""
    
    def test_create_model_config_unsupervised(self):
        """Test creating ModelConfig for unsupervised mode."""
        config = ModelConfig(
            inference_mode=InferenceMode.UNSUPERVISED
        )
        
        assert config.inference_mode == InferenceMode.UNSUPERVISED
        assert config.bedrock_model_id == "anthropic.claude-3-sonnet-20240229-v1:0"
        assert config.bedrock_max_tokens == 1024
        assert config.bedrock_temperature == 0.0
        assert config.max_requests_per_second == 0.9
        assert config.fallback_enabled is True
        assert config.fallback_confidence == 0.7
    
    def test_create_model_config_supervised(self):
        """Test creating ModelConfig for supervised mode."""
        config = ModelConfig(
            inference_mode=InferenceMode.SUPERVISED,
            sagemaker_endpoint_name="fraud-detection-endpoint"
        )
        
        assert config.inference_mode == InferenceMode.SUPERVISED
        assert config.sagemaker_endpoint_name == "fraud-detection-endpoint"
        assert config.sagemaker_content_type == "text/csv"
        assert config.sagemaker_accept == "application/json"
    
    def test_model_config_validation_max_rps(self):
        """Test that max_requests_per_second must be < 1.0."""
        with pytest.raises(ValueError, match="max_requests_per_second must be < 1.0"):
            ModelConfig(
                inference_mode=InferenceMode.UNSUPERVISED,
                max_requests_per_second=1.0
            )
        
        with pytest.raises(ValueError, match="max_requests_per_second must be < 1.0"):
            ModelConfig(
                inference_mode=InferenceMode.UNSUPERVISED,
                max_requests_per_second=1.5
            )
    
    def test_model_config_validation_temperature(self):
        """Test that bedrock_temperature must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="bedrock_temperature must be between 0.0 and 1.0"):
            ModelConfig(
                inference_mode=InferenceMode.UNSUPERVISED,
                bedrock_temperature=-0.1
            )
        
        with pytest.raises(ValueError, match="bedrock_temperature must be between 0.0 and 1.0"):
            ModelConfig(
                inference_mode=InferenceMode.UNSUPERVISED,
                bedrock_temperature=1.5
            )
    
    def test_model_config_validation_fallback_confidence(self):
        """Test that fallback_confidence must be between 0.0 and 1.0."""
        with pytest.raises(ValueError, match="fallback_confidence must be between 0.0 and 1.0"):
            ModelConfig(
                inference_mode=InferenceMode.FALLBACK,
                fallback_confidence=-0.1
            )
        
        with pytest.raises(ValueError, match="fallback_confidence must be between 0.0 and 1.0"):
            ModelConfig(
                inference_mode=InferenceMode.FALLBACK,
                fallback_confidence=1.5
            )
    
    def test_model_config_validation_supervised_requires_endpoint(self):
        """Test that SUPERVISED mode requires sagemaker_endpoint_name."""
        with pytest.raises(ValueError, match="sagemaker_endpoint_name is required"):
            ModelConfig(
                inference_mode=InferenceMode.SUPERVISED,
                sagemaker_endpoint_name=None
            )
    
    def test_model_config_with_scaler_params(self):
        """Test creating ModelConfig with scaler parameters."""
        scaler_params = {
            "total_volume": {"mean": 50000.0, "std": 25000.0},
            "transaction_count": {"mean": 30.0, "std": 15.0}
        }
        
        config = ModelConfig(
            inference_mode=InferenceMode.SUPERVISED,
            sagemaker_endpoint_name="endpoint",
            feature_scaling_enabled=True,
            scaler_params=scaler_params
        )
        
        assert config.feature_scaling_enabled is True
        assert config.scaler_params == scaler_params


class TestFeatureConfig:
    """Tests for FeatureConfig dataclass."""
    
    def test_create_feature_config_defaults(self):
        """Test creating FeatureConfig with default values."""
        config = FeatureConfig()
        
        assert len(config.feature_names) == 10
        assert "total_volume" in config.feature_names
        assert "transaction_count" in config.feature_names
        assert "night_transaction_ratio" in config.feature_names
        assert config.scaler_params is None
        assert len(config.validation_rules) > 0
    
    def test_feature_config_validation_rules(self):
        """Test that validation rules are correctly defined."""
        config = FeatureConfig()
        
        # Check numeric features have min >= 0
        assert config.validation_rules["total_volume"]["min"] == 0
        assert config.validation_rules["transaction_count"]["min"] == 1
        
        # Check ratio features have min=0, max=1
        assert config.validation_rules["night_transaction_ratio"]["min"] == 0
        assert config.validation_rules["night_transaction_ratio"]["max"] == 1
        assert config.validation_rules["round_number_ratio"]["min"] == 0
        assert config.validation_rules["round_number_ratio"]["max"] == 1
        assert config.validation_rules["concentration_score"]["min"] == 0
        assert config.validation_rules["concentration_score"]["max"] == 1
    
    def test_feature_config_custom_feature_names(self):
        """Test creating FeatureConfig with custom feature names."""
        custom_names = ["feature1", "feature2", "feature3"]
        config = FeatureConfig(feature_names=custom_names)
        
        assert config.feature_names == custom_names
    
    def test_feature_config_with_scaler_params(self):
        """Test creating FeatureConfig with scaler parameters."""
        scaler_params = {
            "total_volume": {"mean": 50000.0, "std": 25000.0},
            "transaction_count": {"mean": 30.0, "std": 15.0}
        }
        
        config = FeatureConfig(scaler_params=scaler_params)
        
        assert config.scaler_params == scaler_params
    
    def test_feature_config_feature_order(self):
        """Test that feature names are in expected order."""
        config = FeatureConfig()
        
        expected_order = [
            "total_volume",
            "transaction_count",
            "avg_transaction_size",
            "max_transaction_size",
            "unique_counterparties",
            "night_transaction_ratio",
            "rapid_transaction_count",
            "round_number_ratio",
            "concentration_score",
            "velocity_score"
        ]
        
        assert config.feature_names == expected_order
