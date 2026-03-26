#!/usr/bin/env python3
"""
Quick comparison of predictions across all models
"""
import pandas as pd

print("=" * 80)
print("Prediction Comparison Across All Models")
print("=" * 80)

# Load all prediction files
models = {
    'Random Forest': 'predictions_random_forest.csv',
    'XGBoost': 'predictions_xgboost.csv',
    'LightGBM': 'predictions_lightgbm.csv',
    'Gradient Boosting': 'predictions_gradient_boosting.csv',
    'Logistic Regression': 'predictions_logistic_regression.csv'
}

predictions = {}
for model_name, filename in models.items():
    df = pd.read_csv(filename)
    predictions[model_name] = df.set_index('user_id')['status']

# Combine all predictions
combined = pd.DataFrame(predictions)
combined.columns = ['RF', 'XGB', 'LGB', 'GB', 'LR']

print("\n📊 Summary Statistics:")
print("=" * 80)
for model_name, col in zip(models.keys(), combined.columns):
    suspicious = (combined[col] == 1).sum()
    pct = (suspicious / len(combined)) * 100
    print(f"{model_name:25s} ({col}): {suspicious:5d} suspicious ({pct:5.2f}%)")

print("\n" + "=" * 80)
print("🔍 Agreement Analysis:")
print("=" * 80)

# All models agree
all_agree_suspicious = combined[(combined == 1).all(axis=1)]
all_agree_normal = combined[(combined == 0).all(axis=1)]

print(f"\nAll 5 models agree SUSPICIOUS: {len(all_agree_suspicious):5d} users")
print(f"All 5 models agree NORMAL:     {len(all_agree_normal):5d} users")

# Majority vote
combined['majority_vote'] = (combined.sum(axis=1) >= 3).astype(int)
majority_suspicious = (combined['majority_vote'] == 1).sum()
print(f"\nMajority vote (≥3 models) SUSPICIOUS: {majority_suspicious:5d} users")

# Model agreement matrix
print("\n" + "=" * 80)
print("📈 Pairwise Agreement:")
print("=" * 80)

agreement_matrix = pd.DataFrame(index=combined.columns[:-1], columns=combined.columns[:-1])
for col1 in combined.columns[:-1]:
    for col2 in combined.columns[:-1]:
        if col1 == col2:
            agreement_matrix.loc[col1, col2] = 100.0
        else:
            agreement = ((combined[col1] == combined[col2]).sum() / len(combined)) * 100
            agreement_matrix.loc[col1, col2] = f"{agreement:.1f}%"

print(agreement_matrix.to_string())

# Show examples where models disagree
print("\n" + "=" * 80)
print("🎯 Examples of Disagreement (first 20):")
print("=" * 80)

disagreement = combined[combined.nunique(axis=1) > 1].head(20)
if len(disagreement) > 0:
    print(disagreement.to_string())
else:
    print("All models agree on all predictions!")

# Show users flagged by XGBoost but not Random Forest
print("\n" + "=" * 80)
print("🔴 Users flagged by XGBoost but NOT by Random Forest (first 20):")
print("=" * 80)

xgb_only = combined[(combined['XGB'] == 1) & (combined['RF'] == 0)].head(20)
print(f"Total: {len(combined[(combined['XGB'] == 1) & (combined['RF'] == 0)])} users")
if len(xgb_only) > 0:
    print(xgb_only.to_string())

# Show users flagged by Random Forest but not XGBoost
print("\n" + "=" * 80)
print("🟢 Users flagged by Random Forest but NOT by XGBoost (first 20):")
print("=" * 80)

rf_only = combined[(combined['RF'] == 1) & (combined['XGB'] == 0)].head(20)
print(f"Total: {len(combined[(combined['RF'] == 1) & (combined['XGB'] == 0)])} users")
if len(rf_only) > 0:
    print(rf_only.to_string())

# Save combined predictions
combined.to_csv('all_model_predictions_combined.csv')
print("\n" + "=" * 80)
print("✓ Combined predictions saved to: all_model_predictions_combined.csv")
print("=" * 80)
