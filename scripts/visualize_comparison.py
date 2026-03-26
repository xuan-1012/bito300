#!/usr/bin/env python3
"""
Visualize Model Comparison Results
"""
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Read comparison results
df = pd.read_csv('model_comparison_results.csv')

# Create figure with subplots
fig, axes = plt.subplots(2, 2, figsize=(15, 12))
fig.suptitle('BitoPro Competition - Model Comparison', fontsize=16, fontweight='bold')

# 1. AUC-ROC Comparison
ax1 = axes[0, 0]
colors = ['#2ecc71' if i == 0 else '#3498db' for i in range(len(df))]
bars1 = ax1.barh(df['Model'], df['AUC-ROC'], color=colors)
ax1.set_xlabel('AUC-ROC Score', fontsize=12)
ax1.set_title('AUC-ROC Comparison (Higher is Better)', fontsize=13, fontweight='bold')
ax1.set_xlim(0.7, 0.82)
for i, (model, score) in enumerate(zip(df['Model'], df['AUC-ROC'])):
    ax1.text(score + 0.002, i, f'{score:.4f}', va='center', fontsize=10)
ax1.grid(axis='x', alpha=0.3)

# 2. Precision vs Recall
ax2 = axes[0, 1]
scatter = ax2.scatter(df['Recall'], df['Precision'], s=200, c=df['AUC-ROC'], 
                     cmap='RdYlGn', edgecolors='black', linewidth=2, alpha=0.7)
for i, model in enumerate(df['Model']):
    ax2.annotate(model, (df['Recall'].iloc[i], df['Precision'].iloc[i]), 
                xytext=(5, 5), textcoords='offset points', fontsize=9)
ax2.set_xlabel('Recall (Sensitivity)', fontsize=12)
ax2.set_ylabel('Precision', fontsize=12)
ax2.set_title('Precision vs Recall Trade-off', fontsize=13, fontweight='bold')
ax2.grid(True, alpha=0.3)
plt.colorbar(scatter, ax=ax2, label='AUC-ROC')

# 3. F1-Score Comparison
ax3 = axes[1, 0]
colors3 = ['#e74c3c' if f1 < 0.15 else '#f39c12' if f1 < 0.18 else '#2ecc71' 
           for f1 in df['F1-Score']]
bars3 = ax3.barh(df['Model'], df['F1-Score'], color=colors3)
ax3.set_xlabel('F1-Score', fontsize=12)
ax3.set_title('F1-Score Comparison', fontsize=13, fontweight='bold')
for i, (model, score) in enumerate(zip(df['Model'], df['F1-Score'])):
    ax3.text(score + 0.005, i, f'{score:.4f}', va='center', fontsize=10)
ax3.grid(axis='x', alpha=0.3)

# 4. Confusion Matrix Metrics
ax4 = axes[1, 1]
x = np.arange(len(df))
width = 0.2

tp_bars = ax4.bar(x - 1.5*width, df['TP'], width, label='True Positive', color='#2ecc71')
fp_bars = ax4.bar(x - 0.5*width, df['FP'], width, label='False Positive', color='#e74c3c')
tn_bars = ax4.bar(x + 0.5*width, df['TN']/10, width, label='True Negative (÷10)', color='#3498db')
fn_bars = ax4.bar(x + 1.5*width, df['FN'], width, label='False Negative', color='#f39c12')

ax4.set_xlabel('Model', fontsize=12)
ax4.set_ylabel('Count', fontsize=12)
ax4.set_title('Confusion Matrix Breakdown', fontsize=13, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels(df['Model'], rotation=45, ha='right')
ax4.legend()
ax4.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('model_comparison_visualization.png', dpi=300, bbox_inches='tight')
print("✓ Visualization saved to: model_comparison_visualization.png")

# Create prediction distribution comparison
fig2, ax = plt.subplots(figsize=(12, 6))

# Read prediction files
predictions = {}
model_files = {
    'Random Forest': 'predictions_random_forest.csv',
    'XGBoost': 'predictions_xgboost.csv',
    'LightGBM': 'predictions_lightgbm.csv',
    'Gradient Boosting': 'predictions_gradient_boosting.csv',
    'Logistic Regression': 'predictions_logistic_regression.csv'
}

suspicious_counts = []
normal_counts = []
model_names = []

for model_name, filename in model_files.items():
    try:
        pred_df = pd.read_csv(filename)
        suspicious = (pred_df['status'] == 1).sum()
        normal = (pred_df['status'] == 0).sum()
        suspicious_counts.append(suspicious)
        normal_counts.append(normal)
        model_names.append(model_name)
    except:
        pass

x = np.arange(len(model_names))
width = 0.35

bars1 = ax.bar(x - width/2, normal_counts, width, label='Normal (0)', color='#3498db')
bars2 = ax.bar(x + width/2, suspicious_counts, width, label='Suspicious (1)', color='#e74c3c')

ax.set_xlabel('Model', fontsize=12)
ax.set_ylabel('Number of Users', fontsize=12)
ax.set_title('Prediction Distribution Comparison (12,753 total users)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(model_names, rotation=45, ha='right')
ax.legend()
ax.grid(axis='y', alpha=0.3)

# Add percentage labels
for i, (normal, suspicious) in enumerate(zip(normal_counts, suspicious_counts)):
    total = normal + suspicious
    susp_pct = (suspicious / total) * 100
    ax.text(i + width/2, suspicious + 200, f'{susp_pct:.1f}%', 
            ha='center', va='bottom', fontsize=10, fontweight='bold')

# Add training data reference line
ax.axhline(y=51017 * 0.0321, color='green', linestyle='--', linewidth=2, 
           label='Training Data Suspicious Rate (3.21%)')
ax.text(len(model_names)-0.5, 51017 * 0.0321 + 100, 'Training: 3.21%', 
        fontsize=10, color='green', fontweight='bold')

plt.tight_layout()
plt.savefig('prediction_distribution_comparison.png', dpi=300, bbox_inches='tight')
print("✓ Distribution visualization saved to: prediction_distribution_comparison.png")

print("\n" + "="*80)
print("Visualization Complete!")
print("="*80)
print("\nGenerated files:")
print("  1. model_comparison_visualization.png")
print("  2. prediction_distribution_comparison.png")
