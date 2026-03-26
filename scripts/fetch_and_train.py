"""
BitoPro AWS Event - 完整數據獲取與模型訓練流程
Complete data fetching and model training pipeline for BitoPro AWS Event

API文檔: https://aws-event-docs.bitopro.com/
API端點: https://aws-event-api.bitopro.com/
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime

# API配置
API_BASE_URL = "https://aws-event-api.bitopro.com"
TEAM_NAME = "your_team_name"  # 請替換為你的隊伍名稱

print("=" * 80)
print("BitoPro AWS Event - 可疑帳戶檢測系統")
print("=" * 80)

# ============================================================================
# 步驟 1: 從 Swagger API 獲取數據
# ============================================================================
print("\n步驟 1: 獲取去識別化數據集...")
print("-" * 80)

def fetch_behavior_data():
    """獲取1個月的去識別化行為數據"""
    try:
        response = requests.get(f"{API_BASE_URL}/behavior_data")
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        print(f"✓ 成功獲取行為數據: {len(df)} 筆記錄")
        return df
    except Exception as e:
        print(f"✗ 獲取行為數據失敗: {e}")
        print("  使用模擬數據進行演示...")
        return generate_mock_behavior_data()

def fetch_train_labels():
    """獲取訓練標籤 (status: 1=黑名單, 0=正常)"""
    try:
        response = requests.get(f"{API_BASE_URL}/train_label")
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        print(f"✓ 成功獲取訓練標籤: {len(df)} 個用戶")
        return df
    except Exception as e:
        print(f"✗ 獲取訓練標籤失敗: {e}")
        print("  使用模擬數據進行演示...")
        return generate_mock_train_labels()

def fetch_predict_labels():
    """獲取需要預測的用戶列表"""
    try:
        response = requests.get(f"{API_BASE_URL}/predict_label")
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        print(f"✓ 成功獲取預測列表: {len(df)} 個用戶")
        return df
    except Exception as e:
        print(f"✗ 獲取預測列表失敗: {e}")
        print("  使用模擬數據進行演示...")
        return generate_mock_predict_labels()

def generate_mock_behavior_data():
    """生成模擬行為數據（用於演示）"""
    np.random.seed(42)
    n_users = 1000
    
    data = []
    for user_id in range(1, n_users + 1):
        # 10% 黑名單用戶有異常行為
        is_suspicious = np.random.random() < 0.1
        
        if is_suspicious:
            record = {
                'user_id': user_id,
                'total_volume': np.random.uniform(200000, 1000000),
                'transaction_count': np.random.randint(150, 500),
                'avg_transaction_size': np.random.uniform(2000, 5000),
                'max_transaction_size': np.random.uniform(20000, 100000),
                'unique_counterparties': np.random.randint(1, 5),
                'night_transaction_ratio': np.random.uniform(0.6, 0.95),
                'rapid_transaction_count': np.random.randint(30, 100),
                'round_number_ratio': np.random.uniform(0.7, 0.95),
                'concentration_score': np.random.uniform(0.8, 1.0),
                'velocity_score': np.random.uniform(15, 30)
            }
        else:
            record = {
                'user_id': user_id,
                'total_volume': np.random.uniform(5000, 80000),
                'transaction_count': np.random.randint(10, 100),
                'avg_transaction_size': np.random.uniform(200, 1500),
                'max_transaction_size': np.random.uniform(1000, 8000),
                'unique_counterparties': np.random.randint(5, 25),
                'night_transaction_ratio': np.random.uniform(0.0, 0.3),
                'rapid_transaction_count': np.random.randint(0, 10),
                'round_number_ratio': np.random.uniform(0.0, 0.4),
                'concentration_score': np.random.uniform(0.0, 0.6),
                'velocity_score': np.random.uniform(0.5, 8.0)
            }
        data.append(record)
    
    return pd.DataFrame(data)

def generate_mock_train_labels():
    """生成模擬訓練標籤"""
    np.random.seed(42)
    train_users = list(range(1, 801))  # 前800個用戶用於訓練
    
    labels = []
    for user_id in train_users:
        # 基於user_id生成一致的標籤
        np.random.seed(user_id)
        status = 1 if np.random.random() < 0.1 else 0
        labels.append({'user_id': user_id, 'status': status})
    
    return pd.DataFrame(labels)

def generate_mock_predict_labels():
    """生成模擬預測列表"""
    predict_users = list(range(801, 1001))  # 後200個用戶用於預測
    return pd.DataFrame({'user_id': predict_users})

# 獲取數據
behavior_df = fetch_behavior_data()
train_labels_df = fetch_train_labels()
predict_labels_df = fetch_predict_labels()

# ============================================================================
# 步驟 2: 數據合併與特徵工程
# ============================================================================
print("\n步驟 2: 數據合併與特徵工程...")
print("-" * 80)

# 合併訓練數據
train_df = behavior_df.merge(train_labels_df, on='user_id', how='inner')
print(f"✓ 訓練數據: {len(train_df)} 個用戶")
print(f"  - 黑名單用戶: {train_df['status'].sum()} 個 ({train_df['status'].mean()*100:.1f}%)")
print(f"  - 正常用戶: {(train_df['status']==0).sum()} 個 ({(1-train_df['status'].mean())*100:.1f}%)")

# 準備預測數據
predict_df = behavior_df.merge(predict_labels_df, on='user_id', how='inner')
print(f"✓ 預測數據: {len(predict_df)} 個用戶")

# 特徵列
feature_columns = [
    'total_volume', 'transaction_count', 'avg_transaction_size',
    'max_transaction_size', 'unique_counterparties', 'night_transaction_ratio',
    'rapid_transaction_count', 'round_number_ratio', 'concentration_score',
    'velocity_score'
]

# ============================================================================
# 步驟 3: 模型訓練
# ============================================================================
print("\n步驟 3: 模型訓練...")
print("-" * 80)

# 準備訓練數據
X_train_full = train_df[feature_columns]
y_train_full = train_df['status']

# 分割訓練集和驗證集
X_train, X_val, y_train, y_val = train_test_split(
    X_train_full, y_train_full, test_size=0.2, random_state=42, stratify=y_train_full
)

# 特徵標準化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

print(f"訓練集: {len(X_train)} 個樣本")
print(f"驗證集: {len(X_val)} 個樣本")

# 訓練多個模型
models = {
    'RandomForest': RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_split=10,
        min_samples_leaf=5,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    ),
    'GradientBoosting': GradientBoostingClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        random_state=42
    )
}

best_model = None
best_score = 0
best_model_name = ""

for model_name, model in models.items():
    print(f"\n訓練 {model_name}...")
    model.fit(X_train_scaled, y_train)
    
    # 驗證集評估
    y_val_pred = model.predict(X_val_scaled)
    y_val_proba = model.predict_proba(X_val_scaled)[:, 1]
    
    auc_score = roc_auc_score(y_val, y_val_proba)
    print(f"  AUC Score: {auc_score:.4f}")
    
    # 交叉驗證
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='roc_auc')
    print(f"  CV AUC: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")
    
    if auc_score > best_score:
        best_score = auc_score
        best_model = model
        best_model_name = model_name

print(f"\n✓ 最佳模型: {best_model_name} (AUC: {best_score:.4f})")

# ============================================================================
# 步驟 4: 模型評估
# ============================================================================
print("\n步驟 4: 模型評估...")
print("-" * 80)

y_val_pred = best_model.predict(X_val_scaled)
y_val_proba = best_model.predict_proba(X_val_scaled)[:, 1]

print("\n分類報告:")
print(classification_report(y_val, y_val_pred, target_names=['正常', '黑名單']))

print("\n混淆矩陣:")
cm = confusion_matrix(y_val, y_val_pred)
print(cm)
print(f"  TN: {cm[0,0]}, FP: {cm[0,1]}")
print(f"  FN: {cm[1,0]}, TP: {cm[1,1]}")

# 特徵重要性
if hasattr(best_model, 'feature_importances_'):
    print("\n特徵重要性 (Top 5):")
    feature_importance = pd.DataFrame({
        'feature': feature_columns,
        'importance': best_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(5).iterrows():
        print(f"  {row['feature']:30s}: {row['importance']:.4f}")

# ============================================================================
# 步驟 5: 預測並生成提交文件
# ============================================================================
print("\n步驟 5: 生成預測結果...")
print("-" * 80)

# 準備預測數據
X_predict = predict_df[feature_columns]
X_predict_scaled = scaler.transform(X_predict)

# 進行預測
predictions = best_model.predict(X_predict_scaled)
prediction_proba = best_model.predict_proba(X_predict_scaled)[:, 1]

# 創建提交文件
submission_df = pd.DataFrame({
    'user_id': predict_df['user_id'],
    'status': predictions
})

# 保存為CSV
output_filename = f"{TEAM_NAME}.csv"
submission_df.to_csv(output_filename, index=False)

print(f"✓ 預測完成: {len(submission_df)} 個用戶")
print(f"  - 預測為黑名單: {predictions.sum()} 個 ({predictions.mean()*100:.1f}%)")
print(f"  - 預測為正常: {(predictions==0).sum()} 個 ({(1-predictions.mean())*100:.1f}%)")
print(f"\n✓ 提交文件已生成: {output_filename}")

# 顯示預測結果樣本
print("\n預測結果樣本 (前10個):")
print(submission_df.head(10).to_string(index=False))

# 保存模型
model_filename = f"model_{TEAM_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
joblib.dump({
    'model': best_model,
    'scaler': scaler,
    'feature_columns': feature_columns,
    'model_name': best_model_name,
    'auc_score': best_score
}, model_filename)
print(f"\n✓ 模型已保存: {model_filename}")

# ============================================================================
# 總結
# ============================================================================
print("\n" + "=" * 80)
print("處理完成！")
print("=" * 80)
print(f"\n提交文件: {output_filename}")
print(f"格式: CSV (user_id, status)")
print(f"狀態值: 0 = 正常用戶, 1 = 黑名單用戶")
print(f"\n請確認:")
print(f"  ✓ user_id 與 predict_label 名單一致")
print(f"  ✓ status 值為 0 或 1")
print(f"  ✓ 檔名為隊伍名稱")
print("\n" + "=" * 80)
