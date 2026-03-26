"""Demo script to showcase InputValidator functionality."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
from src.model_evaluation_viz.validation import InputValidator
from src.model_evaluation_viz.core.models import ValidationError


def demo_validate_labels_and_predictions():
    """Demonstrate validate_labels_and_predictions."""
    print("=" * 60)
    print("Demo: validate_labels_and_predictions")
    print("=" * 60)
    
    # Valid case
    y_true = np.array([0, 1, 0, 1, 1])
    y_pred = np.array([0, 1, 1, 1, 0])
    try:
        InputValidator.validate_labels_and_predictions(y_true, y_pred)
        print("✓ Valid: Arrays with same length (5 elements)")
    except ValidationError as e:
        print(f"✗ Error: {e}")
    
    # Invalid case
    y_true = np.array([0, 1, 0, 1])
    y_pred = np.array([0, 1, 1])
    try:
        InputValidator.validate_labels_and_predictions(y_true, y_pred)
        print("✓ Valid: Arrays with different lengths")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    print()


def demo_validate_binary_labels():
    """Demonstrate validate_binary_labels."""
    print("=" * 60)
    print("Demo: validate_binary_labels")
    print("=" * 60)
    
    # Valid case
    y_true = np.array([0, 1, 0, 1, 1, 0])
    try:
        InputValidator.validate_binary_labels(y_true)
        print("✓ Valid: Binary labels with 2 unique values [0, 1]")
    except ValidationError as e:
        print(f"✗ Error: {e}")
    
    # Invalid case - 3 classes
    y_true = np.array([0, 1, 2, 0, 1, 2])
    try:
        InputValidator.validate_binary_labels(y_true)
        print("✓ Valid: Multi-class labels")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    print()


def demo_validate_probabilities():
    """Demonstrate validate_probabilities."""
    print("=" * 60)
    print("Demo: validate_probabilities")
    print("=" * 60)
    
    # Valid case
    y_proba = np.array([0.0, 0.3, 0.5, 0.8, 1.0])
    try:
        InputValidator.validate_probabilities(y_proba)
        print("✓ Valid: Probabilities in range [0, 1]")
    except ValidationError as e:
        print(f"✗ Error: {e}")
    
    # Invalid case - negative
    y_proba = np.array([0.5, -0.1, 0.8])
    try:
        InputValidator.validate_probabilities(y_proba)
        print("✓ Valid: Probabilities with negative values")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    
    # Invalid case - > 1
    y_proba = np.array([0.5, 1.2, 0.8])
    try:
        InputValidator.validate_probabilities(y_proba)
        print("✓ Valid: Probabilities > 1")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    print()


def demo_validate_scores():
    """Demonstrate validate_scores."""
    print("=" * 60)
    print("Demo: validate_scores")
    print("=" * 60)
    
    # Valid case
    train_scores = np.array([0.8, 0.85, 0.9, 0.92])
    val_scores = np.array([0.75, 0.78, 0.82, 0.85])
    try:
        InputValidator.validate_scores(train_scores, val_scores)
        print("✓ Valid: Training and validation scores with same length (4)")
    except ValidationError as e:
        print(f"✗ Error: {e}")
    
    # Invalid case
    train_scores = np.array([0.8, 0.85, 0.9])
    val_scores = np.array([0.75, 0.78])
    try:
        InputValidator.validate_scores(train_scores, val_scores)
        print("✓ Valid: Scores with different lengths")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    print()


def demo_validate_model_comparison_data():
    """Demonstrate validate_model_comparison_data."""
    print("=" * 60)
    print("Demo: validate_model_comparison_data")
    print("=" * 60)
    
    # Valid case
    models_data = {
        'model_v1': {'accuracy': 0.90, 'precision': 0.85, 'recall': 0.88},
        'model_v2': {'accuracy': 0.92, 'precision': 0.87, 'recall': 0.90},
        'model_v3': {'accuracy': 0.88, 'precision': 0.83, 'recall': 0.86}
    }
    try:
        InputValidator.validate_model_comparison_data(models_data)
        print("✓ Valid: 3 models with consistent metrics (accuracy, precision, recall)")
    except ValidationError as e:
        print(f"✗ Error: {e}")
    
    # Invalid case - missing metric
    models_data = {
        'model_v1': {'accuracy': 0.90, 'precision': 0.85, 'recall': 0.88},
        'model_v2': {'accuracy': 0.92, 'precision': 0.87}  # Missing 'recall'
    }
    try:
        InputValidator.validate_model_comparison_data(models_data)
        print("✓ Valid: Models with inconsistent metrics")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    
    # Invalid case - extra metric
    models_data = {
        'model_v1': {'accuracy': 0.90, 'precision': 0.85},
        'model_v2': {'accuracy': 0.92, 'precision': 0.87, 'f1_score': 0.89}
    }
    try:
        InputValidator.validate_model_comparison_data(models_data)
        print("✓ Valid: Model with extra metric")
    except ValidationError as e:
        print(f"✗ Expected Error: {e}")
    print()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("InputValidator Demonstration")
    print("=" * 60 + "\n")
    
    demo_validate_labels_and_predictions()
    demo_validate_binary_labels()
    demo_validate_probabilities()
    demo_validate_scores()
    demo_validate_model_comparison_data()
    
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
