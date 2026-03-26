#!/usr/bin/env python3
"""
生成 XGBoost 模型的詳細性能圖表
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import matplotlib.font_manager as fm

# 設置中文字體和樣式
def setup_chinese_font():
    """設置中文字體，避免方框問題"""
    # 嘗試多種中文字體
    chinese_fonts = [
        'Microsoft JhengHei',  # 微軟正黑體 (Windows)
        'Microsoft YaHei',     # 微軟雅黑 (Windows)
        'SimHei',              # 黑體 (Windows)
        'Arial Unicode MS',    # Mac
        'PingFang TC',         # Mac
        'Heiti TC',            # Mac
        'WenQuanYi Zen Hei',   # Linux
        'DejaVu Sans'          # Fallback
    ]
    
    # 找到系統中可用的字體
    available_fonts = [f.name for f in fm.fontManager.ttflist]
    
    for font in chinese_fonts:
        if font in available_fonts:
            plt.rcParams['font.sans-serif'] = [font]
            print(f"✅ 使用字體: {font}")
            break
    else:
        # 如果沒有找到中文字體，使用英文
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        print("⚠️  未找到中文字體，使用英文字體")
    
    plt.rcParams['axes.unicode_minus'] = False

setup_chinese_font()
sns.set_style("whitegrid")
sns.set_palette("husl")

def load_model_results():
    """載入模型比較結果"""
    df = pd.read_csv('model_comparison_results.csv')
    return df

def create_xgboost_performance_chart(df):
    """Create XGBoost Performance Chart"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('XGBoost Model Performance Analysis', fontsize=20, fontweight='bold', y=0.995)
    
    # Get XGBoost data
    xgb_data = df[df['Model'] == 'XGBoost'].iloc[0]
    
    # 1. Main metrics bar chart
    ax1 = axes[0, 0]
    metrics = ['AUC-ROC', 'AUC-PR', 'Precision', 'Recall', 'F1-Score']
    values = [xgb_data['AUC-ROC'], xgb_data['AUC-PR'], 
              xgb_data['Precision'], xgb_data['Recall'], xgb_data['F1-Score']]
    colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12', '#9b59b6']
    
    bars = ax1.bar(metrics, values, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax1.set_title('XGBoost Key Performance Metrics', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 1)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # 2. Confusion Matrix
    ax2 = axes[0, 1]
    confusion_matrix = np.array([
        [xgb_data['TN'], xgb_data['FP']],
        [xgb_data['FN'], xgb_data['TP']]
    ])
    
    sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues', 
                cbar_kws={'label': 'Count'}, ax=ax2, 
                xticklabels=['Pred Normal', 'Pred Suspicious'],
                yticklabels=['Actual Normal', 'Actual Suspicious'],
                annot_kws={'size': 14, 'weight': 'bold'})
    ax2.set_title('XGBoost Confusion Matrix', fontsize=14, fontweight='bold')
    
    # 3. F1-Score comparison with other models
    ax3 = axes[0, 2]
    models = df['Model'].tolist()
    f1_scores = df['F1-Score'].tolist()
    colors_f1 = ['#e74c3c' if model == 'XGBoost' else '#95a5a6' for model in models]
    
    bars = ax3.barh(models, f1_scores, color=colors_f1, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax3.set_xlabel('F1-Score', fontsize=12, fontweight='bold')
    ax3.set_title('F1-Score Model Comparison (XGBoost in Red)', fontsize=14, fontweight='bold')
    ax3.set_xlim(0, max(f1_scores) * 1.1)
    ax3.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for bar, value in zip(bars, f1_scores):
        width = bar.get_width()
        ax3.text(width, bar.get_y() + bar.get_height()/2.,
                f' {value:.4f}',
                ha='left', va='center', fontsize=10, fontweight='bold', 
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # 4. AUC metrics comparison
    ax4 = axes[1, 0]
    x = np.arange(len(models))
    width = 0.35
    
    bars1 = ax4.bar(x - width/2, df['AUC-ROC'], width, label='AUC-ROC', 
                    color='#3498db', alpha=0.8, edgecolor='black', linewidth=1.5)
    bars2 = ax4.bar(x + width/2, df['AUC-PR'], width, label='AUC-PR', 
                    color='#e74c3c', alpha=0.8, edgecolor='black', linewidth=1.5)
    
    ax4.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax4.set_title('AUC Metrics Comparison (All Models)', fontsize=14, fontweight='bold')
    ax4.set_xticks(x)
    ax4.set_xticklabels(models, rotation=45, ha='right')
    ax4.legend(fontsize=11)
    ax4.grid(axis='y', alpha=0.3)
    ax4.set_ylim(0, 1)
    
    # 5. Precision vs Recall scatter plot
    ax5 = axes[1, 1]
    for idx, row in df.iterrows():
        if row['Model'] == 'XGBoost':
            ax5.scatter(row['Recall'], row['Precision'], s=500, 
                       color='#e74c3c', marker='*', edgecolor='black', 
                       linewidth=2, label=row['Model'], zorder=5)
        else:
            ax5.scatter(row['Recall'], row['Precision'], s=200, 
                       alpha=0.6, edgecolor='black', linewidth=1.5, 
                       label=row['Model'])
    
    ax5.set_xlabel('Recall', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Precision', fontsize=12, fontweight='bold')
    ax5.set_title('Precision vs Recall (XGBoost Starred)', fontsize=14, fontweight='bold')
    ax5.legend(fontsize=9, loc='best')
    ax5.grid(True, alpha=0.3)
    ax5.set_xlim(0, 0.6)
    ax5.set_ylim(0, 0.3)
    
    # 6. XGBoost key statistics
    ax6 = axes[1, 2]
    ax6.axis('off')
    
    stats_text = f"""
    XGBoost Model Statistics
    ========================
    
    Core Performance:
    * F1-Score: {xgb_data['F1-Score']:.4f}
    * AUC-ROC: {xgb_data['AUC-ROC']:.4f}
    * AUC-PR: {xgb_data['AUC-PR']:.4f} (Highest)
    
    Classification Metrics:
    * Precision: {xgb_data['Precision']:.4f} (11.82%)
    * Recall: {xgb_data['Recall']:.4f} (49.39%)
    
    Confusion Matrix:
    * True Positives (TP): {int(xgb_data['TP'])}
    * False Positives (FP): {int(xgb_data['FP'])}
    * True Negatives (TN): {int(xgb_data['TN'])}
    * False Negatives (FN): {int(xgb_data['FN'])}
    
    Total Predictions: {int(xgb_data['TP'] + xgb_data['FP'] + xgb_data['TN'] + xgb_data['FN'])}
    """
    
    ax6.text(0.1, 0.5, stats_text, fontsize=11, verticalalignment='center',
            family='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    return fig

def create_f1_score_detail_chart(df):
    """Create F1-Score Detail Analysis Chart"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle('XGBoost F1-Score Detailed Analysis', fontsize=18, fontweight='bold')
    
    xgb_data = df[df['Model'] == 'XGBoost'].iloc[0]
    
    # 1. F1-Score composition analysis
    ax1 = axes[0]
    precision = xgb_data['Precision']
    recall = xgb_data['Recall']
    f1 = xgb_data['F1-Score']
    
    # Calculate F1 harmonic mean formula
    components = ['Precision', 'Recall', 'F1-Score\n(Harmonic Mean)']
    values = [precision, recall, f1]
    colors = ['#3498db', '#e74c3c', '#2ecc71']
    
    bars = ax1.bar(components, values, color=colors, alpha=0.8, 
                   edgecolor='black', linewidth=2)
    ax1.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax1.set_title('F1-Score Composition Analysis', fontsize=14, fontweight='bold')
    ax1.set_ylim(0, 0.6)
    ax1.grid(axis='y', alpha=0.3)
    
    # Add values and formula
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{value:.4f}\n({value*100:.2f}%)',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Add F1 formula
    formula_text = f'F1 = 2 * (P * R) / (P + R)\n= 2 * ({precision:.4f} * {recall:.4f}) / ({precision:.4f} + {recall:.4f})\n= {f1:.4f}'
    ax1.text(0.5, 0.95, formula_text, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top', horizontalalignment='center',
            bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.3),
            family='monospace')
    
    # 2. All models F1-Score ranking
    ax2 = axes[1]
    df_sorted = df.sort_values('F1-Score', ascending=True)
    models = df_sorted['Model'].tolist()
    f1_scores = df_sorted['F1-Score'].tolist()
    
    colors_rank = ['#e74c3c' if model == 'XGBoost' else '#95a5a6' for model in models]
    
    bars = ax2.barh(models, f1_scores, color=colors_rank, alpha=0.8, 
                    edgecolor='black', linewidth=2)
    ax2.set_xlabel('F1-Score', fontsize=12, fontweight='bold')
    ax2.set_title('F1-Score Ranking (Low to High)', fontsize=14, fontweight='bold')
    ax2.grid(axis='x', alpha=0.3)
    
    # Add ranking and values
    for idx, (bar, value, model) in enumerate(zip(bars, f1_scores, models)):
        width = bar.get_width()
        rank = len(models) - idx
        label = f'#{rank} - {value:.4f}'
        
        ax2.text(width, bar.get_y() + bar.get_height()/2.,
                f'  {label}',
                ha='left', va='center', fontsize=11, fontweight='bold',
                bbox=dict(boxstyle='round,pad=0.4', 
                         facecolor='white' if model != 'XGBoost' else 'yellow', 
                         alpha=0.8))
    
    plt.tight_layout()
    return fig

def main():
    """Main function"""
    print("🎨 Generating XGBoost Performance Charts...")
    
    # Load data
    df = load_model_results()
    print(f"✅ Loaded results for {len(df)} models")
    
    # Create output directory
    output_dir = Path('xgboost_charts')
    output_dir.mkdir(exist_ok=True)
    
    # Generate Chart 1: Comprehensive Performance Analysis
    print("\n📊 Generating Chart 1: XGBoost Comprehensive Performance Analysis...")
    fig1 = create_xgboost_performance_chart(df)
    output_path1 = output_dir / 'xgboost_performance_analysis.png'
    fig1.savefig(output_path1, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path1}")
    
    # Generate Chart 2: F1-Score Detailed Analysis
    print("\n📊 Generating Chart 2: F1-Score Detailed Analysis...")
    fig2 = create_f1_score_detail_chart(df)
    output_path2 = output_dir / 'xgboost_f1_score_analysis.png'
    fig2.savefig(output_path2, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✅ Saved: {output_path2}")
    
    # Display summary
    xgb_data = df[df['Model'] == 'XGBoost'].iloc[0]
    print("\n" + "="*60)
    print("📈 XGBoost Model Performance Summary")
    print("="*60)
    print(f"F1-Score:    {xgb_data['F1-Score']:.4f} (19.08%)")
    print(f"AUC-ROC:     {xgb_data['AUC-ROC']:.4f}")
    print(f"AUC-PR:      {xgb_data['AUC-PR']:.4f} ⭐ (Highest among all models)")
    print(f"Precision:   {xgb_data['Precision']:.4f} (11.82%)")
    print(f"Recall:      {xgb_data['Recall']:.4f} (49.39%)")
    print("="*60)
    print(f"\n✅ All charts saved to: {output_dir}/")
    print("\nGenerated Charts:")
    print(f"  1. xgboost_performance_analysis.png - Comprehensive Performance (6 subplots)")
    print(f"  2. xgboost_f1_score_analysis.png - F1-Score Detailed Analysis")
    
    plt.show()

if __name__ == '__main__':
    main()
