"""Unit tests for InputValidator class."""

import pytest
import numpy as np
from src.model_evaluation_viz.validation import InputValidator
from src.model_evaluation_viz.core.models import ValidationError


class TestValidateLabelsAndPredictions:
    """Tests for validate_labels_and_predictions method."""

    def test_valid_same_length_arrays(self):
        """Test that validation passes for arrays of same length."""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 1])
        # Should not raise
        InputValidator.validate_labels_and_predictions(y_true, y_pred)

    def test_different_length_arrays_raises_error(self):
        """Test that validation fails for arrays of different lengths."""
        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 1])
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_labels_and_predictions(y_true, y_pred)
        
        assert "Length mismatch" in str(exc_info.value)
        assert "4 elements" in str(exc_info.value)
        assert "3 elements" in str(exc_info.value)

    def test_empty_arrays_same_length(self):
        """Test that validation passes for empty arrays of same length."""
        y_true = np.array([])
        y_pred = np.array([])
        # Should not raise
        InputValidator.validate_labels_and_predictions(y_true, y_pred)


class TestValidateBinaryLabels:
    """Tests for validate_binary_labels method."""

    def test_valid_binary_labels(self):
        """Test that validation passes for exactly 2 unique values."""
        y_true = np.array([0, 1, 0, 1, 1, 0])
        # Should not raise
        InputValidator.validate_binary_labels(y_true)

    def test_single_unique_value_raises_error(self):
        """Test that validation fails for only 1 unique value."""
        y_true = np.array([1, 1, 1, 1])
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_binary_labels(y_true)
        
        assert "exactly 2 unique label values" in str(exc_info.value)
        assert "found 1 unique values" in str(exc_info.value)

    def test_three_unique_values_raises_error(self):
        """Test that validation fails for 3 unique values."""
        y_true = np.array([0, 1, 2, 0, 1, 2])
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_binary_labels(y_true)
        
        assert "exactly 2 unique label values" in str(exc_info.value)
        assert "found 3 unique values" in str(exc_info.value)

    def test_binary_labels_with_strings(self):
        """Test that validation works with string labels."""
        y_true = np.array(['cat', 'dog', 'cat', 'dog'])
        # Should not raise
        InputValidator.validate_binary_labels(y_true)


class TestValidateProbabilities:
    """Tests for validate_probabilities method."""

    def test_valid_probabilities(self):
        """Test that validation passes for probabilities in [0, 1]."""
        y_proba = np.array([0.0, 0.5, 0.8, 1.0, 0.3])
        # Should not raise
        InputValidator.validate_probabilities(y_proba)

    def test_negative_probability_raises_error(self):
        """Test that validation fails for negative probabilities."""
        y_proba = np.array([0.5, -0.1, 0.8])
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_probabilities(y_proba)
        
        assert "must be in the range [0, 1]" in str(exc_info.value)
        assert "-0.1" in str(exc_info.value)

    def test_probability_greater_than_one_raises_error(self):
        """Test that validation fails for probabilities > 1."""
        y_proba = np.array([0.5, 1.2, 0.8])
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_probabilities(y_proba)
        
        assert "must be in the range [0, 1]" in str(exc_info.value)
        assert "1.2" in str(exc_info.value)

    def test_all_zeros(self):
        """Test that validation passes for all zeros."""
        y_proba = np.array([0.0, 0.0, 0.0])
        # Should not raise
        InputValidator.validate_probabilities(y_proba)

    def test_all_ones(self):
        """Test that validation passes for all ones."""
        y_proba = np.array([1.0, 1.0, 1.0])
        # Should not raise
        InputValidator.validate_probabilities(y_proba)


class TestValidateScores:
    """Tests for validate_scores method."""

    def test_valid_same_length_scores(self):
        """Test that validation passes for scores of same length."""
        train_scores = np.array([0.8, 0.85, 0.9])
        val_scores = np.array([0.75, 0.78, 0.82])
        # Should not raise
        InputValidator.validate_scores(train_scores, val_scores)

    def test_different_length_scores_raises_error(self):
        """Test that validation fails for scores of different lengths."""
        train_scores = np.array([0.8, 0.85, 0.9])
        val_scores = np.array([0.75, 0.78])
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_scores(train_scores, val_scores)
        
        assert "Length mismatch" in str(exc_info.value)
        assert "train_scores has 3 elements" in str(exc_info.value)
        assert "val_scores has 2 elements" in str(exc_info.value)

    def test_empty_scores_same_length(self):
        """Test that validation passes for empty scores of same length."""
        train_scores = np.array([])
        val_scores = np.array([])
        # Should not raise
        InputValidator.validate_scores(train_scores, val_scores)


class TestValidateModelComparisonData:
    """Tests for validate_model_comparison_data method."""

    def test_valid_consistent_metrics(self):
        """Test that validation passes for models with same metrics."""
        models_data = {
            'model1': {'accuracy': 0.9, 'precision': 0.85, 'recall': 0.88},
            'model2': {'accuracy': 0.92, 'precision': 0.87, 'recall': 0.90},
            'model3': {'accuracy': 0.88, 'precision': 0.83, 'recall': 0.86}
        }
        # Should not raise
        InputValidator.validate_model_comparison_data(models_data)

    def test_missing_metric_raises_error(self):
        """Test that validation fails when a model is missing a metric."""
        models_data = {
            'model1': {'accuracy': 0.9, 'precision': 0.85, 'recall': 0.88},
            'model2': {'accuracy': 0.92, 'precision': 0.87}  # Missing 'recall'
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_model_comparison_data(models_data)
        
        assert "Metric inconsistency" in str(exc_info.value)
        assert "model2" in str(exc_info.value)
        assert "Missing metrics" in str(exc_info.value)
        assert "recall" in str(exc_info.value)

    def test_extra_metric_raises_error(self):
        """Test that validation fails when a model has an extra metric."""
        models_data = {
            'model1': {'accuracy': 0.9, 'precision': 0.85},
            'model2': {'accuracy': 0.92, 'precision': 0.87, 'f1_score': 0.89}  # Extra metric
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_model_comparison_data(models_data)
        
        assert "Metric inconsistency" in str(exc_info.value)
        assert "model2" in str(exc_info.value)
        assert "Extra metrics" in str(exc_info.value)
        assert "f1_score" in str(exc_info.value)

    def test_empty_models_data_raises_error(self):
        """Test that validation fails for empty models_data."""
        models_data = {}
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_model_comparison_data(models_data)
        
        assert "cannot be empty" in str(exc_info.value)

    def test_single_model_valid(self):
        """Test that validation passes for a single model."""
        models_data = {
            'model1': {'accuracy': 0.9, 'precision': 0.85}
        }
        # Should not raise
        InputValidator.validate_model_comparison_data(models_data)

    def test_different_metric_names_raises_error(self):
        """Test that validation fails when models have completely different metrics."""
        models_data = {
            'model1': {'accuracy': 0.9, 'precision': 0.85},
            'model2': {'recall': 0.88, 'f1_score': 0.87}
        }
        
        with pytest.raises(ValidationError) as exc_info:
            InputValidator.validate_model_comparison_data(models_data)
        
        assert "Metric inconsistency" in str(exc_info.value)
        assert "model2" in str(exc_info.value)
