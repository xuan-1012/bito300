"""
Numerical Feature Scaling Module

Implements StandardScaler for numerical feature normalization.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def scale(
    df: pd.DataFrame,
    numeric_columns: List[str],
    scaler_params: Optional[Dict[str, Dict[str, float]]] = None
) -> tuple[pd.DataFrame, Dict[str, Dict[str, float]]]:
    """
    Apply StandardScaler (Z-score normalization) to specified numerical columns.
    
    StandardScaler formula: z = (x - mean) / std
    
    Args:
        df: Input DataFrame
        numeric_columns: List of column names to scale
        scaler_params: Optional pre-computed scaler parameters (mean, std) for each column.
                      If provided, uses these parameters instead of computing from data.
    
    Returns:
        Tuple of (scaled_df, scaler_params_dict)
        - scaled_df: DataFrame with scaled numerical columns
        - scaler_params_dict: Dictionary mapping column names to {'mean': float, 'std': float}
    
    Requirements: 5.2, 5.3, 5.4, 5.6
    """
    df_scaled = df.copy()
    computed_params = {}
    
    for col in numeric_columns:
        if col not in df.columns:
            logger.warning(f"Column '{col}' not found in DataFrame, skipping scaling")
            continue
        
        # Use provided parameters or compute from data
        if scaler_params and col in scaler_params:
            mean = scaler_params[col]['mean']
            std = scaler_params[col]['std']
            logger.info(f"Using provided scaler params for '{col}': mean={mean:.4f}, std={std:.4f}")
        else:
            mean = df[col].mean()
            std = df[col].std()
            logger.info(f"Computed scaler params for '{col}': mean={mean:.4f}, std={std:.4f}")
        
        # Handle zero standard deviation (constant column)
        if std == 0 or pd.isna(std):
            logger.warning(f"Column '{col}' has zero or NaN std, setting scaled values to 0")
            df_scaled[col] = 0.0
            computed_params[col] = {'mean': mean, 'std': 1.0}  # Use std=1.0 to avoid division by zero
        else:
            # Apply StandardScaler: z = (x - mean) / std
            df_scaled[col] = (df[col] - mean) / std
            computed_params[col] = {'mean': mean, 'std': std}
    
    logger.info(f"Scaled {len(computed_params)} numerical columns")
    return df_scaled, computed_params


def apply_scaler_params(
    df: pd.DataFrame,
    scaler_params: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Apply pre-computed scaler parameters to a DataFrame.
    
    This is used during inference to apply the same scaling as training data.
    
    Args:
        df: Input DataFrame
        scaler_params: Dictionary mapping column names to {'mean': float, 'std': float}
    
    Returns:
        DataFrame with scaled numerical columns
    
    Requirements: 5.4, 5.6
    """
    df_scaled = df.copy()
    
    for col, params in scaler_params.items():
        if col not in df.columns:
            logger.warning(f"Column '{col}' not found in DataFrame, skipping scaling")
            continue
        
        mean = params['mean']
        std = params['std']
        
        # Apply StandardScaler
        if std == 0 or pd.isna(std):
            df_scaled[col] = 0.0
        else:
            df_scaled[col] = (df[col] - mean) / std
    
    logger.info(f"Applied scaler params to {len(scaler_params)} columns")
    return df_scaled


def inverse_transform(
    df: pd.DataFrame,
    scaler_params: Dict[str, Dict[str, float]]
) -> pd.DataFrame:
    """
    Inverse transform scaled data back to original scale.
    
    Formula: x = z * std + mean
    
    Args:
        df: Scaled DataFrame
        scaler_params: Dictionary mapping column names to {'mean': float, 'std': float}
    
    Returns:
        DataFrame with original scale
    """
    df_original = df.copy()
    
    for col, params in scaler_params.items():
        if col not in df.columns:
            continue
        
        mean = params['mean']
        std = params['std']
        
        # Inverse transform: x = z * std + mean
        df_original[col] = df[col] * std + mean
    
    return df_original
