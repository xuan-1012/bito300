"""
Unit tests for risk level classification.

Tests the classify_risk_level function with boundary values and mid-range values.
"""

import pytest
from src.model_risk_scoring.models.data_models import RiskLevel
from src.model_risk_scoring.utils.risk_classifier import classify_risk_level


class TestClassifyRiskLevel:
    """Test suite for classify_risk_level function."""
    
    # Test boundary values for LOW level (0-25)
    def test_classify_risk_level_boundary_0(self):
        """Test lower boundary of LOW level (0)."""
        assert classify_risk_level(0) == RiskLevel.LOW
    
    def test_classify_risk_level_boundary_25(self):
        """Test upper boundary of LOW level (25)."""
        assert classify_risk_level(25) == RiskLevel.LOW
    
    # Test boundary values for MEDIUM level (26-50)
    def test_classify_risk_level_boundary_26(self):
        """Test lower boundary of MEDIUM level (26)."""
        assert classify_risk_level(26) == RiskLevel.MEDIUM
    
    def test_classify_risk_level_boundary_50(self):
        """Test upper boundary of MEDIUM level (50)."""
        assert classify_risk_level(50) == RiskLevel.MEDIUM
    
    # Test boundary values for HIGH level (51-75)
    def test_classify_risk_level_boundary_51(self):
        """Test lower boundary of HIGH level (51)."""
        assert classify_risk_level(51) == RiskLevel.HIGH
    
    def test_classify_risk_level_boundary_75(self):
        """Test upper boundary of HIGH level (75)."""
        assert classify_risk_level(75) == RiskLevel.HIGH
    
    # Test boundary values for CRITICAL level (76-100)
    def test_classify_risk_level_boundary_76(self):
        """Test lower boundary of CRITICAL level (76)."""
        assert classify_risk_level(76) == RiskLevel.CRITICAL
    
    def test_classify_risk_level_boundary_100(self):
        """Test upper boundary of CRITICAL level (100)."""
        assert classify_risk_level(100) == RiskLevel.CRITICAL
    
    # Test mid-range values for each level
    def test_classify_risk_level_mid_low(self):
        """Test mid-range value for LOW level."""
        assert classify_risk_level(12) == RiskLevel.LOW
        assert classify_risk_level(13) == RiskLevel.LOW
    
    def test_classify_risk_level_mid_medium(self):
        """Test mid-range value for MEDIUM level."""
        assert classify_risk_level(38) == RiskLevel.MEDIUM
        assert classify_risk_level(40) == RiskLevel.MEDIUM
    
    def test_classify_risk_level_mid_high(self):
        """Test mid-range value for HIGH level."""
        assert classify_risk_level(63) == RiskLevel.HIGH
        assert classify_risk_level(65) == RiskLevel.HIGH
    
    def test_classify_risk_level_mid_critical(self):
        """Test mid-range value for CRITICAL level."""
        assert classify_risk_level(88) == RiskLevel.CRITICAL
        assert classify_risk_level(90) == RiskLevel.CRITICAL
    
    # Test invalid inputs
    def test_classify_risk_level_negative(self):
        """Test that negative scores raise ValueError."""
        with pytest.raises(ValueError, match="risk_score must be between 0 and 100"):
            classify_risk_level(-1)
    
    def test_classify_risk_level_above_100(self):
        """Test that scores above 100 raise ValueError."""
        with pytest.raises(ValueError, match="risk_score must be between 0 and 100"):
            classify_risk_level(101)
    
    def test_classify_risk_level_float_values(self):
        """Test that float values work correctly."""
        # 25.5 is less than 26, so it's LOW
        assert classify_risk_level(25.5) == RiskLevel.LOW
        # 50.9 is between 26 and 51, so it's MEDIUM
        assert classify_risk_level(50.9) == RiskLevel.MEDIUM
        # 75.1 is between 51 and 76, so it's HIGH
        assert classify_risk_level(75.1) == RiskLevel.HIGH
        # 99.9 is >= 76, so it's CRITICAL
        assert classify_risk_level(99.9) == RiskLevel.CRITICAL
    
    # Test edge cases near boundaries
    def test_classify_risk_level_near_boundaries(self):
        """Test values very close to boundaries."""
        assert classify_risk_level(25.9) == RiskLevel.LOW
        assert classify_risk_level(26.1) == RiskLevel.MEDIUM
        assert classify_risk_level(50.9) == RiskLevel.MEDIUM
        assert classify_risk_level(51.1) == RiskLevel.HIGH
        assert classify_risk_level(75.9) == RiskLevel.HIGH
        assert classify_risk_level(76.1) == RiskLevel.CRITICAL
