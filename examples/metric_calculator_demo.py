"""Demo script for MetricCalculator class.

This script demonstrates the usage of the MetricCalculator class
for calculating various classification metrics.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from src.model_evaluation_viz.core import MetricCalculator

# Set random seed for reproducibility
np.random.seed(42)

print("=" * 70)
print("MetricCalculator Demo")
print("=" * 70)

# Example 1: Binary classification with good performance
print("\n1. Binary Classification - Good Performance")
print("-" * 70)
y_true = np.array([0, 1, 1, 0, 1, 0, 1, 0, 1, 1])
y_pred = np.array([0, 1, 1, 0, 1, 0, 1, 0, 0, 1])
y_proba = np.array([0.1, 0.9, 0.85, 0.2, 0.95, 0.15, 0.88, 0.25, 0.45, 0.92])

# Calculate confusion matrix
cm = MetricCalculator.calculate_confusion_matrix(y_true, y_pred)
print(f"Confusion Matrix:\n{cm}")

# Calculate classification metrics
metrics = MetricCalculator.calculate_classification_metrics(y_true, y_pred)
print(f"\nClassification Metrics:")
print(f"  Accuracy:  {metrics['accuracy']:.3f}")
print(f"  Precision: {metrics['precision']:.3f}")
print(f"  Recall:    {metrics['recall']:.3f}")
print(f"  F1 Score:  {metrics['f1_score']:.3f}")

# Calculate ROC curve
fpr, tpr, auc_score, thresholds = MetricCalculator.calculate_roc_curve(y_true, y_proba)
print(f"\nROC Curve:")
print(f"  AUC Score: {auc_score:.3f}")
print(f"  Number of thresholds: {len(thresholds)}")

# Calculate Precision-Recall curve
precision, recall, ap, pr_thresholds = MetricCalculator.calculate_precision_recall_curve(y_true, y_proba)
print(f"\nPrecision-Recall Curve:")
print(f"  Average Precision: {ap:.3f}")
print(f"  Number of thresholds: {len(pr_thresholds)}")

# Calculate threshold metrics
threshold_metrics = MetricCalculator.calculate_threshold_metrics(
    y_true, y_proba, thresholds=np.array([0.3, 0.5, 0.7, 0.9])
)
print(f"\nThreshold Analysis:")
for i, thresh in enumerate(threshold_metrics['thresholds']):
    print(f"  Threshold {thresh:.1f}: "
          f"Precision={threshold_metrics['precision'][i]:.3f}, "
          f"Recall={threshold_metrics['recall'][i]:.3f}, "
          f"F1={threshold_metrics['f1_score'][i]:.3f}")

# Calculate lift curve
percentages, gains = MetricCalculator.calculate_lift_curve(y_true, y_proba)
print(f"\nLift Curve:")
print(f"  At 20% of samples: {gains[int(len(gains)*0.2)]:.1f}% of positives captured")
print(f"  At 50% of samples: {gains[int(len(gains)*0.5)]:.1f}% of positives captured")
print(f"  At 80% of samples: {gains[int(len(gains)*0.8)]:.1f}% of positives captured")

# Example 2: Perfect classifier
print("\n\n2. Perfect Classifier")
print("-" * 70)
y_true_perfect = np.array([0, 0, 0, 1, 1, 1])
y_pred_perfect = np.array([0, 0, 0, 1, 1, 1])
y_proba_perfect = np.array([0.1, 0.2, 0.3, 0.7, 0.8, 0.9])

metrics_perfect = MetricCalculator.calculate_classification_metrics(y_true_perfect, y_pred_perfect)
print(f"Classification Metrics:")
print(f"  Accuracy:  {metrics_perfect['accuracy']:.3f}")
print(f"  Precision: {metrics_perfect['precision']:.3f}")
print(f"  Recall:    {metrics_perfect['recall']:.3f}")
print(f"  F1 Score:  {metrics_perfect['f1_score']:.3f}")

fpr_perfect, tpr_perfect, auc_perfect, _ = MetricCalculator.calculate_roc_curve(y_true_perfect, y_proba_perfect)
print(f"\nROC AUC Score: {auc_perfect:.3f}")

# Example 3: Imbalanced dataset
print("\n\n3. Imbalanced Dataset (10% positive class)")
print("-" * 70)
n_samples = 100
n_positive = 10
y_true_imb = np.array([1] * n_positive + [0] * (n_samples - n_positive))
# Shuffle
np.random.shuffle(y_true_imb)
# Generate predictions with some noise
y_proba_imb = np.where(y_true_imb == 1, 
                       np.random.uniform(0.6, 1.0, n_samples),
                       np.random.uniform(0.0, 0.4, n_samples))
y_pred_imb = (y_proba_imb >= 0.5).astype(int)

metrics_imb = MetricCalculator.calculate_classification_metrics(y_true_imb, y_pred_imb)
print(f"Classification Metrics:")
print(f"  Accuracy:  {metrics_imb['accuracy']:.3f}")
print(f"  Precision: {metrics_imb['precision']:.3f}")
print(f"  Recall:    {metrics_imb['recall']:.3f}")
print(f"  F1 Score:  {metrics_imb['f1_score']:.3f}")

_, _, auc_imb, _ = MetricCalculator.calculate_roc_curve(y_true_imb, y_proba_imb)
_, _, ap_imb, _ = MetricCalculator.calculate_precision_recall_curve(y_true_imb, y_proba_imb)
print(f"\nROC AUC Score: {auc_imb:.3f}")
print(f"Average Precision: {ap_imb:.3f}")

print("\n" + "=" * 70)
print("Demo completed successfully!")
print("=" * 70)
