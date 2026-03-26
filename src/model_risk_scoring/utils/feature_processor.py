"""
Feature processor for validating and normalizing transaction features.

This module provides the FeatureProcessor class for validating transaction features,
normalizing numerical values, and preparing features for model inference.
"""

from typing import Dict, List, Optional

from ..exceptions import ValidationError
from ..models.data_models import TransactionFeatures


class FeatureProcessor:
    """
    Feature processor for validating and normalizing transaction features.
    
    This class validates that transaction features meet all requirements
    (non-negative values, ratios in [0,1], etc.) and provides normalization
    capabilities for model inference.
    
    Attributes:
        scaler_params: Optional normalization parameters (mean, std) for each feature
    """
    
    def __init__(self, scaler_params: Optional[Dict[str, Dict[str, float]]] = None):
        """
        Initialize feature processor.
        
        Args:
            scaler_params: Optional dictionary mapping feature names to
                          normalization parameters with 'mean' and 'std' keys.
                          Example: {"total_volume": {"mean": 50000, "std": 20000}}
        """
        self.scaler_params = scaler_params
    
    def validate(self, features: TransactionFeatures) -> bool:
        """
        Validate transaction features.
        
        Validates that all feature values meet requirements:
        - account_id is non-empty
        - total_volume >= 0
        - transaction_count > 0
        - night_transaction_ratio in [0, 1]
        - round_number_ratio in [0, 1]
        - concentration_score in [0, 1]
        
        Args:
            features: Transaction features to validate
            
        Returns:
            True if all validations pass
            
        Raises:
            ValidationError: If any validation fails, with detailed error message
        """
        # Validate account_id is non-empty
        if not features.account_id or features.account_id.strip() == "":
            raise ValidationError(
                "account_id must be non-empty",
                field="account_id"
            )
        
        # Validate total_volume >= 0
        if features.total_volume < 0:
            raise ValidationError(
                f"total_volume must be >= 0, got {features.total_volume}",
                field="total_volume"
            )
        
        # Validate transaction_count > 0
        if features.transaction_count <= 0:
            raise ValidationError(
                f"transaction_count must be > 0, got {features.transaction_count}",
                field="transaction_count"
            )
        
        # Validate night_transaction_ratio in [0, 1]
        if not 0 <= features.night_transaction_ratio <= 1:
            raise ValidationError(
                f"night_transaction_ratio must be between 0 and 1, got {features.night_transaction_ratio}",
                field="night_transaction_ratio"
            )
        
        # Validate round_number_ratio in [0, 1]
        if not 0 <= features.round_number_ratio <= 1:
            raise ValidationError(
                f"round_number_ratio must be between 0 and 1, got {features.round_number_ratio}",
                field="round_number_ratio"
            )
        
        # Validate concentration_score in [0, 1]
        if not 0 <= features.concentration_score <= 1:
            raise ValidationError(
                f"concentration_score must be between 0 and 1, got {features.concentration_score}",
                field="concentration_score"
            )
        
        return True
    
    def normalize(self, features: TransactionFeatures) -> Dict[str, float]:
        """
        Normalize numerical features using Z-score normalization.
        
        If scaler_params are provided, uses them for normalization:
        normalized_value = (value - mean) / std
        
        If scaler_params are not provided, returns raw feature values.
        
        Args:
            features: Transaction features to normalize
            
        Returns:
            Dictionary mapping feature names to normalized values
        """
        # First validate features
        self.validate(features)
        
        # Extract feature values as dictionary
        feature_dict = {
            "total_volume": features.total_volume,
            "transaction_count": float(features.transaction_count),
            "avg_transaction_size": features.avg_transaction_size,
            "max_transaction_size": features.max_transaction_size,
            "unique_counterparties": float(features.unique_counterparties),
            "night_transaction_ratio": features.night_transaction_ratio,
            "rapid_transaction_count": float(features.rapid_transaction_count),
            "round_number_ratio": features.round_number_ratio,
            "concentration_score": features.concentration_score,
            "velocity_score": features.velocity_score
        }
        
        # If no scaler params, return raw values
        if not self.scaler_params:
            return feature_dict
        
        # Apply Z-score normalization
        normalized = {}
        for feature_name, value in feature_dict.items():
            if feature_name in self.scaler_params:
                params = self.scaler_params[feature_name]
                mean = params.get("mean", 0.0)
                std = params.get("std", 1.0)
                
                # Avoid division by zero
                if std == 0:
                    normalized[feature_name] = 0.0
                else:
                    normalized[feature_name] = (value - mean) / std
            else:
                # If no params for this feature, use raw value
                normalized[feature_name] = value
        
        return normalized
    
    def to_vector(self, features: TransactionFeatures) -> List[float]:
        """
        Convert transaction features to feature vector.
        
        Converts features to a list of float values in a consistent order,
        suitable for model inference (e.g., SageMaker endpoints).
        
        Args:
            features: Transaction features to convert
            
        Returns:
            List of feature values in consistent order
        """
        # First validate features
        self.validate(features)
        
        # Return features in consistent order
        return [
            features.total_volume,
            float(features.transaction_count),
            features.avg_transaction_size,
            features.max_transaction_size,
            float(features.unique_counterparties),
            features.night_transaction_ratio,
            float(features.rapid_transaction_count),
            features.round_number_ratio,
            features.concentration_score,
            features.velocity_score
        ]
