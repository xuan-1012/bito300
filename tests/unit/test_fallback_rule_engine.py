"""
Unit tests for FallbackRuleEngine.

Tests verify that all rules trigger correctly, scores accumulate properly,
and the maximum score is capped at 100.
"""

import pytest
from src.model_risk_scoring.engines.fallback_rule_engine import FallbackRuleEngine
from src.model_risk_scoring.models.data_models import TransactionFeatures


class TestFallbackRuleEngine:
    """Test suite for FallbackRuleEngine."""
    
    @pytest.fixture
    def engine(self):
        """Create a FallbackRuleEngine instance."""
        return FallbackRuleEngine()
    
    @pytest.fixture
    def base_features(self):
        """Create base transaction features with no rules triggered."""
        return TransactionFeatures(
            account_id="test_account",
            total_volume=50000,  # Below 100000 threshold
            transaction_count=10,
            avg_transaction_size=5000,
            max_transaction_size=10000,
            unique_counterparties=5,
            night_transaction_ratio=0.1,  # Below 0.3 threshold
            rapid_transaction_count=5,  # Below 10 threshold
            round_number_ratio=0.2,  # Below 0.5 threshold
            concentration_score=0.5,  # Below 0.7 threshold
            velocity_score=5  # Below 10 threshold
        )
    
    def test_no_rules_triggered(self, engine, base_features):
        """Test that no rules are triggered for normal behavior."""
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 0
        assert result["risk_factors"] == []
        assert result["confidence"] == 0.7
        assert "未發現明顯風險因子" in result["explanation"]
    
    def test_high_volume_rule(self, engine, base_features):
        """Test Rule 1: total_volume > 100000 → +20 points."""
        base_features.total_volume = 150000
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 20
        assert "high_volume" in result["risk_factors"]
        assert "總交易量超過 $100,000" in result["explanation"]
        assert result["confidence"] == 0.7
    
    def test_night_transactions_rule(self, engine, base_features):
        """Test Rule 2: night_transaction_ratio > 0.3 → +15 points."""
        base_features.night_transaction_ratio = 0.4
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 15
        assert "night_transactions" in result["risk_factors"]
        assert "深夜交易比例超過 30%" in result["explanation"]
        assert result["confidence"] == 0.7
    
    def test_round_numbers_rule(self, engine, base_features):
        """Test Rule 3: round_number_ratio > 0.5 → +20 points."""
        base_features.round_number_ratio = 0.6
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 20
        assert "round_numbers" in result["risk_factors"]
        assert "整數金額比例超過 50%" in result["explanation"]
        assert result["confidence"] == 0.7
    
    def test_high_concentration_rule(self, engine, base_features):
        """Test Rule 4: concentration_score > 0.7 → +15 points."""
        base_features.concentration_score = 0.8
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 15
        assert "high_concentration" in result["risk_factors"]
        assert "交易對手集中度過高" in result["explanation"]
        assert result["confidence"] == 0.7
    
    def test_rapid_transactions_rule(self, engine, base_features):
        """Test Rule 5: rapid_transaction_count > 10 → +15 points."""
        base_features.rapid_transaction_count = 15
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 15
        assert "rapid_transactions" in result["risk_factors"]
        assert "短時間內大量交易" in result["explanation"]
        assert result["confidence"] == 0.7
    
    def test_high_velocity_rule(self, engine, base_features):
        """Test Rule 6: velocity_score > 10 → +15 points."""
        base_features.velocity_score = 12
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 15
        assert "high_velocity" in result["risk_factors"]
        assert "交易速度超過 10 筆/小時" in result["explanation"]
        assert result["confidence"] == 0.7
    
    def test_multiple_rules_triggered(self, engine, base_features):
        """Test that multiple rules accumulate scores correctly."""
        # Trigger 3 rules: high_volume (20), night_transactions (15), round_numbers (20)
        base_features.total_volume = 150000
        base_features.night_transaction_ratio = 0.4
        base_features.round_number_ratio = 0.6
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 55  # 20 + 15 + 20
        assert len(result["risk_factors"]) == 3
        assert "high_volume" in result["risk_factors"]
        assert "night_transactions" in result["risk_factors"]
        assert "round_numbers" in result["risk_factors"]
        assert result["confidence"] == 0.7
    
    def test_score_capped_at_100(self, engine, base_features):
        """Test that risk score is capped at 100 even if rules exceed it."""
        # Trigger all 6 rules: total = 20 + 15 + 20 + 15 + 15 + 15 = 100
        base_features.total_volume = 150000
        base_features.night_transaction_ratio = 0.4
        base_features.round_number_ratio = 0.6
        base_features.concentration_score = 0.8
        base_features.rapid_transaction_count = 15
        base_features.velocity_score = 12
        
        result = engine.calculate_risk_score(base_features)
        
        assert result["risk_score"] == 100
        assert len(result["risk_factors"]) == 6
        assert result["confidence"] == 0.7
    
    def test_apply_rules_returns_correct_format(self, engine, base_features):
        """Test that apply_rules returns correct tuple format."""
        base_features.total_volume = 150000
        
        triggered = engine.apply_rules(base_features)
        
        assert len(triggered) == 1
        assert isinstance(triggered[0], tuple)
        assert len(triggered[0]) == 3
        
        name, score, reason = triggered[0]
        assert name == "high_volume"
        assert score == 20
        assert isinstance(reason, str)
        assert len(reason) > 0
    
    def test_explanation_includes_all_triggered_rules(self, engine, base_features):
        """Test that explanation includes all triggered rules."""
        # Trigger 2 rules
        base_features.total_volume = 150000
        base_features.velocity_score = 12
        
        result = engine.calculate_risk_score(base_features)
        
        explanation = result["explanation"]
        assert "觸發 2 項風險規則" in explanation
        assert "總交易量超過 $100,000" in explanation
        assert "交易速度超過 10 筆/小時" in explanation
        assert "+20 分" in explanation
        assert "+15 分" in explanation
    
    def test_confidence_always_0_7(self, engine, base_features):
        """Test that confidence is always 0.7 regardless of score."""
        # Test with no rules triggered
        result1 = engine.calculate_risk_score(base_features)
        assert result1["confidence"] == 0.7
        
        # Test with some rules triggered
        base_features.total_volume = 150000
        result2 = engine.calculate_risk_score(base_features)
        assert result2["confidence"] == 0.7
        
        # Test with all rules triggered
        base_features.night_transaction_ratio = 0.4
        base_features.round_number_ratio = 0.6
        base_features.concentration_score = 0.8
        base_features.rapid_transaction_count = 15
        base_features.velocity_score = 12
        result3 = engine.calculate_risk_score(base_features)
        assert result3["confidence"] == 0.7
    
    def test_boundary_values(self, engine, base_features):
        """Test boundary values for rule thresholds."""
        # Test exactly at threshold (should not trigger)
        base_features.total_volume = 100000
        result1 = engine.calculate_risk_score(base_features)
        assert "high_volume" not in result1["risk_factors"]
        
        # Test just above threshold (should trigger)
        base_features.total_volume = 100001
        result2 = engine.calculate_risk_score(base_features)
        assert "high_volume" in result2["risk_factors"]
        
        # Test night_transaction_ratio at threshold
        base_features.total_volume = 50000  # Reset
        base_features.night_transaction_ratio = 0.3
        result3 = engine.calculate_risk_score(base_features)
        assert "night_transactions" not in result3["risk_factors"]
        
        # Test just above threshold
        base_features.night_transaction_ratio = 0.31
        result4 = engine.calculate_risk_score(base_features)
        assert "night_transactions" in result4["risk_factors"]
