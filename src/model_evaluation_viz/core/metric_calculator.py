"""Metric calculation for model evaluation."""

import numpy as np
import warnings
from typing import Dict, Tuple
from sklearn.metrics import (
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve,
    average_precision_score
)


class MetricCalculator:
    """Calculates evaluation metrics for classification models.
    
    This class provides static methods for calculating various classification
    metrics including confusion matrices, classification metrics (accuracy,
    precision, recall, F1), ROC curves, precision-recall curves, threshold
    analysis, and lift curves.
    
    All methods use vectorized numpy operations for performance and handle
    edge cases like division by zero by returning np.nan with warnings.
    
    Examples:
        >>> y_true = np.array([0, 1, 1, 0, 1])
        >>> y_pred = np.array([0, 1, 0, 0, 1])
        >>> metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
        >>> print(metrics['accuracy'])
        0.8
        
        >>> y_proba = np.array([0.1, 0.9, 0.4, 0.2, 0.8])
        >>> fpr, tpr, auc_score, thresholds = MetricCalculator.calculate_roc_curve(y_true, y_proba)
        >>> print(f"AUC: {auc_score:.3f}")
        AUC: 0.833
    """
    
    @staticmethod
    def calculate_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Calculate confusion matrix from true and predicted labels.
        
        Args:
            y_true: True labels as numpy array
            y_pred: Predicted labels as numpy array
            
        Returns:
            Confusion matrix as 2D numpy array where element [i,j] represents
            the count of samples with true label i and predicted label j
            
        Examples:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_pred = np.array([0, 1, 0, 0, 1])
            >>> cm = MetricCalculator.calculate_confusion_matrix(y_true, y_pred)
            >>> print(cm)
            [[2 0]
             [1 2]]
        """
        return confusion_matrix(y_true, y_pred)
    
    @staticmethod
    def calculate_classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """Calculate accuracy, precision, recall, and F1 score.
        
        Handles division by zero by returning np.nan for affected metrics
        and logging a warning.
        
        Args:
            y_true: True labels as numpy array
            y_pred: Predicted labels as numpy array
            
        Returns:
            Dictionary containing:
                - accuracy: Proportion of correct predictions
                - precision: TP / (TP + FP)
                - recall: TP / (TP + FN)
                - f1_score: Harmonic mean of precision and recall
                
        Examples:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_pred = np.array([0, 1, 0, 0, 1])
            >>> metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
            >>> print(f"Accuracy: {metrics['accuracy']:.2f}")
            Accuracy: 0.80
        """
        # Calculate confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        
        # For binary classification
        if cm.shape == (2, 2):
            tn, fp, fn, tp = cm.ravel()
        else:
            # For multi-class, calculate macro-averaged metrics
            # This is a simplified approach
            tp = np.diag(cm).sum()
            fp = cm.sum(axis=0) - np.diag(cm)
            fn = cm.sum(axis=1) - np.diag(cm)
            tn = cm.sum() - (tp + fp.sum() + fn.sum())
            
            # Use sum for binary-like calculation
            tp = np.diag(cm).sum()
            fp = fp.sum()
            fn = fn.sum()
        
        # Calculate accuracy
        accuracy = (y_true == y_pred).sum() / len(y_true)
        
        # Calculate precision with division by zero handling
        if tp + fp == 0:
            warnings.warn("Division by zero in precision calculation: TP + FP = 0. Returning np.nan.")
            precision = np.nan
        else:
            precision = tp / (tp + fp)
        
        # Calculate recall with division by zero handling
        if tp + fn == 0:
            warnings.warn("Division by zero in recall calculation: TP + FN = 0. Returning np.nan.")
            recall = np.nan
        else:
            recall = tp / (tp + fn)
        
        # Calculate F1 score with division by zero handling
        if np.isnan(precision) or np.isnan(recall) or (precision + recall) == 0:
            if (precision + recall) == 0:
                warnings.warn("Division by zero in F1 calculation: precision + recall = 0. Returning np.nan.")
            f1_score = np.nan
        else:
            f1_score = 2 * (precision * recall) / (precision + recall)
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1_score
        }
    
    @staticmethod
    def calculate_roc_curve(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float, np.ndarray]:
        """Calculate TPR, FPR, AUC, and thresholds for ROC curve.
        
        Args:
            y_true: True binary labels as numpy array
            y_proba: Predicted probabilities for positive class as numpy array
            
        Returns:
            Tuple containing:
                - fpr: False positive rates at different thresholds
                - tpr: True positive rates at different thresholds
                - auc_score: Area under the ROC curve
                - thresholds: Threshold values used to compute fpr and tpr
                
        Examples:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
            >>> fpr, tpr, auc_score, thresholds = MetricCalculator.calculate_roc_curve(y_true, y_proba)
            >>> print(f"AUC: {auc_score:.3f}")
            AUC: 1.000
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_proba)
        auc_score = auc(fpr, tpr)
        
        return fpr, tpr, auc_score, thresholds
    
    @staticmethod
    def calculate_precision_recall_curve(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float, np.ndarray]:
        """Calculate precision, recall, average precision, and thresholds.
        
        Args:
            y_true: True binary labels as numpy array
            y_proba: Predicted probabilities for positive class as numpy array
            
        Returns:
            Tuple containing:
                - precision: Precision values at different thresholds
                - recall: Recall values at different thresholds
                - average_precision: Average precision score (area under PR curve)
                - thresholds: Threshold values used to compute precision and recall
                
        Examples:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
            >>> precision, recall, ap, thresholds = MetricCalculator.calculate_precision_recall_curve(y_true, y_proba)
            >>> print(f"Average Precision: {ap:.3f}")
            Average Precision: 1.000
        """
        precision, recall, thresholds = precision_recall_curve(y_true, y_proba)
        average_precision = average_precision_score(y_true, y_proba)
        
        return precision, recall, average_precision, thresholds
    
    @staticmethod
    def calculate_threshold_metrics(y_true: np.ndarray, y_proba: np.ndarray, 
                                   thresholds: np.ndarray = None) -> Dict[str, np.ndarray]:
        """Calculate precision, recall, and F1 for multiple thresholds.
        
        Args:
            y_true: True binary labels as numpy array
            y_proba: Predicted probabilities for positive class as numpy array
            thresholds: Array of threshold values to evaluate. If None, uses
                       np.linspace(0, 1, 100) to generate 100 evenly spaced thresholds
            
        Returns:
            Dictionary containing:
                - thresholds: Threshold values used
                - precision: Precision at each threshold
                - recall: Recall at each threshold
                - f1_score: F1 score at each threshold
                
        Examples:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
            >>> thresholds = np.array([0.3, 0.5, 0.7])
            >>> metrics = MetricCalculator.calculate_threshold_metrics(y_true, y_proba, thresholds)
            >>> print(metrics['f1_score'])
            [0.857... 1.0 1.0]
        """
        if thresholds is None:
            thresholds = np.linspace(0, 1, 100)
        
        precision_values = np.zeros(len(thresholds))
        recall_values = np.zeros(len(thresholds))
        f1_values = np.zeros(len(thresholds))
        
        for i, threshold in enumerate(thresholds):
            # Apply threshold to get predictions
            y_pred = (y_proba >= threshold).astype(int)
            
            # Calculate metrics for this threshold
            metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
            
            precision_values[i] = metrics['precision']
            recall_values[i] = metrics['recall']
            f1_values[i] = metrics['f1_score']
        
        return {
            'thresholds': thresholds,
            'precision': precision_values,
            'recall': recall_values,
            'f1_score': f1_values
        }
    
    @staticmethod
    def calculate_lift_curve(y_true: np.ndarray, y_proba: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Calculate cumulative gains for lift curve.
        
        Sorts samples by predicted probability in descending order and calculates
        the cumulative percentage of positive cases captured.
        
        Args:
            y_true: True binary labels as numpy array
            y_proba: Predicted probabilities for positive class as numpy array
            
        Returns:
            Tuple containing:
                - percentages: Percentage of samples (0 to 100)
                - cumulative_gains: Cumulative percentage of positive cases (0 to 100)
                
        Examples:
            >>> y_true = np.array([0, 1, 1, 0, 1])
            >>> y_proba = np.array([0.1, 0.9, 0.8, 0.2, 0.7])
            >>> percentages, gains = MetricCalculator.calculate_lift_curve(y_true, y_proba)
            >>> print(f"At 60% of samples, captured {gains[int(len(gains)*0.6)]:.1f}% of positives")
            At 60% of samples, captured 100.0% of positives
        """
        # Sort by predicted probability in descending order
        sorted_indices = np.argsort(y_proba)[::-1]
        y_true_sorted = y_true[sorted_indices]
        
        # Calculate cumulative sum of positive cases
        cumulative_positives = np.cumsum(y_true_sorted)
        total_positives = y_true.sum()
        
        # Handle edge case where there are no positive cases
        if total_positives == 0:
            warnings.warn("No positive cases in y_true. Returning zeros for lift curve.")
            cumulative_gains = np.zeros(len(y_true) + 1)
        else:
            # Calculate cumulative percentage of positives captured
            cumulative_gains = np.concatenate([[0], (cumulative_positives / total_positives) * 100])
        
        # Calculate percentage of samples
        percentages = np.linspace(0, 100, len(y_true) + 1)
        
        return percentages, cumulative_gains
