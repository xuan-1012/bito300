"""
Unit tests for scaler module
"""

import pytest
import pandas as pd
import numpy as np
from src.preprocessing.scaler import scale, apply_scaler_params, inverse_transform


class TestScale:
    """Test scale() function"""
    
    def test_scale_basic(self):
        """Test basic scaling functionality"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0],
            'b': [10.0, 20.0, 30.0, 40.0, 50.0],
            'c': ['x', 'y', 'z', 'x', 'y']  # Non-numeric column
        })
        
        scaled_df, params = scale(df, ['a', 'b'])
        
        # Check that scaling was applied
        assert 'a' in params
        assert 'b' in params
        assert 'mean' in params['a']
        assert 'std' in params['a']
        
        # Check that scaled values have mean ≈ 0 and std ≈ 1
        assert abs(scaled_df['a'].mean()) < 1e-10
        assert abs(scaled_df['a'].std() - 1.0) < 1e-10
        assert abs(scaled_df['b'].mean()) < 1e-10
        assert abs(scaled_df['b'].std() - 1.0) < 1e-10
        
        # Check that non-numeric column is unchanged
        assert (scaled_df['c'] == df['c']).all()
    
    def test_scale_with_provided_params(self):
        """Test scaling with pre-computed parameters"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        provided_params = {
            'a': {'mean': 3.0, 'std': 2.0}
        }
        
        scaled_df, params = scale(df, ['a'], scaler_params=provided_params)
        
        # Check that provided params were used
        assert params['a']['mean'] == 3.0
        assert params['a']['std'] == 2.0
        
        # Check scaling: (1 - 3) / 2 = -1.0
        assert scaled_df['a'].iloc[0] == -1.0
        # Check scaling: (5 - 3) / 2 = 1.0
        assert scaled_df['a'].iloc[4] == 1.0
    
    def test_scale_zero_std(self):
        """Test scaling with constant column (zero std)"""
        df = pd.DataFrame({
            'a': [5.0, 5.0, 5.0, 5.0, 5.0]  # Constant column
        })
        
        scaled_df, params = scale(df, ['a'])
        
        # Check that scaled values are 0
        assert (scaled_df['a'] == 0.0).all()
        assert params['a']['mean'] == 5.0
        assert params['a']['std'] == 1.0  # Fallback to 1.0
    
    def test_scale_missing_column(self):
        """Test scaling with missing column"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0]
        })
        
        scaled_df, params = scale(df, ['a', 'b'])  # 'b' doesn't exist
        
        # Check that only 'a' was scaled
        assert 'a' in params
        assert 'b' not in params
    
    def test_scale_preserves_original(self):
        """Test that original DataFrame is not modified"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        original_values = df['a'].copy()
        
        scaled_df, params = scale(df, ['a'])
        
        # Check that original DataFrame is unchanged
        assert (df['a'] == original_values).all()


class TestApplyScalerParams:
    """Test apply_scaler_params() function"""
    
    def test_apply_scaler_params_basic(self):
        """Test applying scaler parameters"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        params = {
            'a': {'mean': 3.0, 'std': 2.0}
        }
        
        scaled_df = apply_scaler_params(df, params)
        
        # Check scaling: (1 - 3) / 2 = -1.0
        assert scaled_df['a'].iloc[0] == -1.0
        # Check scaling: (5 - 3) / 2 = 1.0
        assert scaled_df['a'].iloc[4] == 1.0
    
    def test_apply_scaler_params_missing_column(self):
        """Test applying params to missing column"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0]
        })
        
        params = {
            'a': {'mean': 2.0, 'std': 1.0},
            'b': {'mean': 10.0, 'std': 5.0}  # 'b' doesn't exist
        }
        
        scaled_df = apply_scaler_params(df, params)
        
        # Check that 'a' was scaled
        assert abs(scaled_df['a'].mean()) < 1e-10
    
    def test_apply_scaler_params_zero_std(self):
        """Test applying params with zero std"""
        df = pd.DataFrame({
            'a': [1.0, 2.0, 3.0]
        })
        
        params = {
            'a': {'mean': 2.0, 'std': 0.0}  # Zero std
        }
        
        scaled_df = apply_scaler_params(df, params)
        
        # Check that scaled values are 0
        assert (scaled_df['a'] == 0.0).all()


class TestInverseTransform:
    """Test inverse_transform() function"""
    
    def test_inverse_transform_basic(self):
        """Test inverse transformation"""
        # Original data
        df_original = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        # Scale
        df_scaled, params = scale(df_original, ['a'])
        
        # Inverse transform
        df_recovered = inverse_transform(df_scaled, params)
        
        # Check that recovered values match original
        np.testing.assert_array_almost_equal(
            df_recovered['a'].values,
            df_original['a'].values,
            decimal=10
        )
    
    def test_inverse_transform_round_trip(self):
        """Test scale -> inverse_transform round trip"""
        df = pd.DataFrame({
            'a': [10.0, 20.0, 30.0, 40.0, 50.0],
            'b': [100.0, 200.0, 300.0, 400.0, 500.0]
        })
        
        # Scale
        df_scaled, params = scale(df, ['a', 'b'])
        
        # Inverse transform
        df_recovered = inverse_transform(df_scaled, params)
        
        # Check round trip
        np.testing.assert_array_almost_equal(
            df_recovered['a'].values,
            df['a'].values,
            decimal=10
        )
        np.testing.assert_array_almost_equal(
            df_recovered['b'].values,
            df['b'].values,
            decimal=10
        )


class TestScalerIntegration:
    """Integration tests for scaler module"""
    
    def test_train_test_consistency(self):
        """Test that train and test data are scaled consistently"""
        # Training data
        df_train = pd.DataFrame({
            'a': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        
        # Test data (different values)
        df_test = pd.DataFrame({
            'a': [6.0, 7.0, 8.0]
        })
        
        # Scale training data
        df_train_scaled, params = scale(df_train, ['a'])
        
        # Apply same params to test data
        df_test_scaled = apply_scaler_params(df_test, params)
        
        # Check that test data uses training mean and std
        # Training mean = 3.0, std ≈ 1.58
        # Test value 6.0 should be scaled as: (6 - 3) / 1.58 ≈ 1.90
        expected_scaled = (6.0 - params['a']['mean']) / params['a']['std']
        assert abs(df_test_scaled['a'].iloc[0] - expected_scaled) < 1e-10
