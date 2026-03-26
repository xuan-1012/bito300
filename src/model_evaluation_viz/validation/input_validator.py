"""Input validation for chart generation."""

import numpy as np
from typing import Dict, Any
from ..core.models import ValidationError


class InputValidator:
    """Validates input data for chart generation."""

    @staticmethod
    def validate_labels_and_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> None:
        """
        Validate that labels and predictions have the same length.
        
        Args:
            y_true: True labels array
            y_pred: Predicted labels or probabilities array
            
        Raises:
            ValidationError: If arrays have different lengths
        """
        if len(y_true) != len(y_pred):
            raise ValidationError(
                f"Length mismatch: y_true has {len(y_true)} elements but "
                f"y_pred has {len(y_pred)} elements. Both arrays must have the same length."
            )

    @staticmethod
    def validate_binary_labels(y_true: np.ndarray) -> None:
        """
        Validate that labels contain exactly two unique values.
        
        Args:
            y_true: True labels array
            
        Raises:
            ValidationError: If labels don't contain exactly 2 unique values
        """
        unique_values = np.unique(y_true)
        n_unique = len(unique_values)
        
        if n_unique != 2:
            raise ValidationError(
                f"Binary classification requires exactly 2 unique label values, "
                f"but found {n_unique} unique values: {unique_values}. "
                f"Please ensure labels contain only two distinct classes."
            )

    @staticmethod
    def validate_probabilities(y_proba: np.ndarray) -> None:
        """
        Validate that probabilities are in the [0, 1] range.
        
        Args:
            y_proba: Predicted probabilities array
            
        Raises:
            ValidationError: If any probability is outside [0, 1] range
        """
        min_val = np.min(y_proba)
        max_val = np.max(y_proba)
        
        if min_val < 0 or max_val > 1:
            raise ValidationError(
                f"Probabilities must be in the range [0, 1], but found values "
                f"in range [{min_val:.6f}, {max_val:.6f}]. "
                f"Please ensure all probability values are between 0 and 1."
            )

    @staticmethod
    def validate_scores(train_scores: np.ndarray, val_scores: np.ndarray) -> None:
        """
        Validate that training and validation scores have the same length.
        
        Args:
            train_scores: Training scores array
            val_scores: Validation scores array
            
        Raises:
            ValidationError: If arrays have different lengths
        """
        if len(train_scores) != len(val_scores):
            raise ValidationError(
                f"Length mismatch: train_scores has {len(train_scores)} elements but "
                f"val_scores has {len(val_scores)} elements. "
                f"Both score arrays must have the same length."
            )

    @staticmethod
    def validate_model_comparison_data(models_data: Dict[str, Dict[str, float]]) -> None:
        """
        Validate that all models have the same set of metrics.
        
        Args:
            models_data: Dictionary mapping model names to their metrics
                        (e.g., {'model1': {'accuracy': 0.9, 'precision': 0.85}, ...})
            
        Raises:
            ValidationError: If models have inconsistent metrics
        """
        if not models_data:
            raise ValidationError(
                "models_data cannot be empty. Please provide at least one model with metrics."
            )
        
        # Get the metric keys from the first model
        model_names = list(models_data.keys())
        first_model = model_names[0]
        expected_metrics = set(models_data[first_model].keys())
        
        # Check all other models have the same metrics
        for model_name in model_names[1:]:
            model_metrics = set(models_data[model_name].keys())
            
            if model_metrics != expected_metrics:
                missing = expected_metrics - model_metrics
                extra = model_metrics - expected_metrics
                
                error_parts = [
                    f"Metric inconsistency detected for model '{model_name}'. "
                    f"Expected metrics: {sorted(expected_metrics)}. "
                    f"Found metrics: {sorted(model_metrics)}."
                ]
                
                if missing:
                    error_parts.append(f"Missing metrics: {sorted(missing)}.")
                if extra:
                    error_parts.append(f"Extra metrics: {sorted(extra)}.")
                
                raise ValidationError(" ".join(error_parts))
