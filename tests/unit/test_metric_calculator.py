"""Unit tests for MetricCalculator class."""

import numpy as np
import pytest
import warnings
from src.model_evaluation_viz.core.metric_calculator import MetricCalculator


class TestMetricCalculator:
    """Test suite for MetricCalculator class."""
    
    def test_calculate_confusion_matrix_binary(self):
        """Test confusion matrix calculation for binary classification."""
        y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0])
        y_pred = np.array([0, 1, 0, 0, 1, 1, 1, 0])
        
        cm = MetricCalculator.calculate_confusion_matrix(y_true, y_pred)
        
        # Expected: TN=3, FP=1, FN=1, TP=3
        assert cm.shape == (2, 2)
        assert cm[0, 0] == 3  # TN
        assert cm[0, 1] == 1  # FP
        assert cm[1, 0] == 1  # FN
        assert cm[1, 1] == 3  # TP
    
    def test_calculate_classification_metrics_perfect_classifier(self):
        """Test metrics with perfect classifier."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 1, 0, 1])
        
        metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
        
        assert metrics['accuracy'] == 1.0
        assert metrics['precision'] == 1.0
        assert metrics['recall'] == 1.0
        assert metrics['f1_score'] == 1.0
    
    def test_calculate_classification_metrics_random_classifier(self):
        """Test metrics with known values."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 0, 1])
        
        metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
        
        # Accuracy: 4/5 = 0.8
        assert metrics['accuracy'] == 0.8
        # TP=2, FP=0, FN=1
        # Precision: 2/(2+0) = 1.0
        assert metrics['precision'] == 1.0
        # Recall: 2/(2+1) = 0.667
        assert abs(metrics['recall'] - 2/3) < 0.001
        # F1: 2 * (1.0 * 0.667) / (1.0 + 0.667) = 0.8
        assert abs(metrics['f1_score'] - 0.8) < 0.001
    
    def test_calculate_classification_metrics_division_by_zero(self):
        """Test division by zero handling."""
        # All predictions are negative, but there are positive labels
        y_true = np.array([1, 1, 1])
        y_pred = np.array([0, 0, 0])
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
            
            # Should warn about division by zero in precision
            assert len(w) >= 1
            assert "Division by zero" in str(w[0].message)
        
        # Precision should be nan (TP=0, FP=0)
        assert np.isnan(metrics['precision'])
        # Recall should be 0 (TP=0, FN=3)
        assert metrics['recall'] == 0.0
        # F1 should be nan
        assert np.isnan(metrics['f1_score'])
    
    def test_calculate_roc_curve(self):
        """Test ROC curve calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        fpr, tpr, auc_score, thresholds = MetricCalculator.calculate_roc_curve(y_true, y_proba)
        
        # Check return types
        assert isinstance(fpr, np.ndarray)
        assert isinstance(tpr, np.ndarray)
        assert isinstance(auc_score, float)
        assert isinstance(thresholds, np.ndarray)
        
        # AUC should be between 0 and 1
        assert 0 <= auc_score <= 1
        
        # For this perfect separation case, AUC should be 1.0
        assert auc_score == 1.0
        
        # FPR and TPR should have same length
        assert len(fpr) == len(tpr)
    
    def test_calculate_precision_recall_curve(self):
        """Test precision-recall curve calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        precision, recall, ap, thresholds = MetricCalculator.calculate_precision_recall_curve(y_true, y_proba)
        
        # Check return types
        assert isinstance(precision, np.ndarray)
        assert isinstance(recall, np.ndarray)
        assert isinstance(ap, float)
        assert isinstance(thresholds, np.ndarray)
        
        # Average precision should be between 0 and 1
        assert 0 <= ap <= 1
        
        # For this perfect separation case, AP should be 1.0
        assert ap == 1.0
    
    def test_calculate_threshold_metrics_default_thresholds(self):
        """Test threshold metrics with default thresholds."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        metrics = MetricCalculator.calculate_threshold_metrics(y_true, y_proba)
        
        # Check all keys present
        assert 'thresholds' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1_score' in metrics
        
        # Default should have 100 thresholds
        assert len(metrics['thresholds']) == 100
        assert len(metrics['precision']) == 100
        assert len(metrics['recall']) == 100
        assert len(metrics['f1_score']) == 100
    
    def test_calculate_threshold_metrics_custom_thresholds(self):
        """Test threshold metrics with custom thresholds."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        thresholds = np.array([0.3, 0.5, 0.7])
        
        metrics = MetricCalculator.calculate_threshold_metrics(y_true, y_proba, thresholds)
        
        # Should have 3 thresholds
        assert len(metrics['thresholds']) == 3
        assert len(metrics['precision']) == 3
        assert len(metrics['recall']) == 3
        assert len(metrics['f1_score']) == 3
        
        # All values should be between 0 and 1 (or nan)
        for i in range(3):
            assert np.isnan(metrics['precision'][i]) or (0 <= metrics['precision'][i] <= 1)
            assert np.isnan(metrics['recall'][i]) or (0 <= metrics['recall'][i] <= 1)
            assert np.isnan(metrics['f1_score'][i]) or (0 <= metrics['f1_score'][i] <= 1)
    
    def test_calculate_lift_curve(self):
        """Test lift curve calculation."""
        y_true = np.array([0, 1, 1, 0, 1])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        percentages, gains = MetricCalculator.calculate_lift_curve(y_true, y_proba)
        
        # Check return types
        assert isinstance(percentages, np.ndarray)
        assert isinstance(gains, np.ndarray)
        
        # Should have same length
        assert len(percentages) == len(gains)
        
        # Should have n+1 points (including 0)
        assert len(percentages) == len(y_true) + 1
        
        # Percentages should go from 0 to 100
        assert percentages[0] == 0
        assert percentages[-1] == 100
        
        # Gains should go from 0 to 100
        assert gains[0] == 0
        assert gains[-1] == 100
        
        # Gains should be monotonically increasing
        assert np.all(np.diff(gains) >= 0)
    
    def test_calculate_lift_curve_no_positives(self):
        """Test lift curve with no positive cases."""
        y_true = np.array([0, 0, 0, 0, 0])
        y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            percentages, gains = MetricCalculator.calculate_lift_curve(y_true, y_proba)
            
            # Should warn about no positive cases
            assert len(w) == 1
            assert "No positive cases" in str(w[0].message)
        
        # Gains should all be zero
        assert np.all(gains == 0)
    
    def test_calculate_roc_curve_perfect_separation(self):
        """Test ROC curve with perfect class separation."""
        y_true = np.array([0, 0, 0, 1, 1, 1])
        y_proba = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])
        
        fpr, tpr, auc_score, thresholds = MetricCalculator.calculate_roc_curve(y_true, y_proba)
        
        # Perfect separation should give AUC = 1.0
        assert auc_score == 1.0
    
    def test_calculate_roc_curve_random_classifier(self):
        """Test ROC curve with random-like predictions."""
        np.random.seed(42)
        y_true = np.random.randint(0, 2, 100)
        y_proba = np.random.random(100)
        
        fpr, tpr, auc_score, thresholds = MetricCalculator.calculate_roc_curve(y_true, y_proba)
        
        # Random classifier should have AUC around 0.5
        assert 0.3 <= auc_score <= 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
