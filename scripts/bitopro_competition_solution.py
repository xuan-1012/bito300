"""
BitoPro AWS Event 競賽完整解決方案
Complete solution for BitoPro AWS Event Competition

要求:
1. 從 Swagger API 獲取1個月去識別化數據
2. 調用 train_label API 獲取標註結果 (status: 1=黑名單, 0=正常)
3. 結合行為數據與 train_label 進行模型訓練
4. 對 predict_label 列表進行預測
5. 生成 CSV 提交文件 (檔名=隊伍名稱, 內容=user_id與status)
"""

import requests
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, f1_score
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# 配置
# ============================================================================
API_BASE_URL = "https://aws-event-api.bitopro.com"
TEAM_NAME = "your_team_name"  # 請替換為你的隊伍名稱

print("=" * 80)
print("BitoPro AWS Event - 可疑帳戶檢測競賽解決方案")
print("=" * 80)
print(f"API端點: {API_BASE_URL}")
print(f"隊伍名稱: {TEAM_NAME}")

# ============================================================================
# 步驟 1: 數據獲取
# ============================================================================
print("\n" + "=" * 80)
print("步驟 1: 從 API 獲取數據")
print("=" * 80)

def fetch_api_data(endpoint, description):
    """通用API數據獲取函數"""
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        print(f"\n正在獲取 {description}...")
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        df = pd.DataFrame(data)
        print(f"✓ 成功: {len(df)} 筆記錄")
        return df
        
    except requests.exceptions.RequestException as e:
        print(f"✗ API請求失敗: {e}")
        return None
    except Exception as e:
        print(f"✗ 數據處理失敗: {e}")
        return None

# 獲取行為數據
behavior_df = fetch_api_data("behavior_data", "行為數據 (1個月去識別化數據)")

# 獲取訓練標籤
train_labels_df = fetch_api_data("train_label", "訓練標籤 (已標註結果)")

# 獲取預測列表
predict_labels_df = fetch_api_data("predict_label", "預測列表 (需預測的user_id)")

# 檢查數據是否成功獲取
if behavior_df is None or train_labels_df is None or predict_labels_df is None:
    print("\n⚠️  API數據獲取失敗，請檢查:")
    print("  1. API端點是否正確")
    print("  2. 網路連接是否正常")
    print("  3. API是否需要認證")
    print("\n使用本地數據或模擬數據繼續演示...")
    
    # 這裡可以載入本地CSV文件
    # behavior_df = pd.read_csv('behavior_data.csv')
    # train_labels_df = pd.read_csv('train_label.csv')
    # predict_labels_df = pd.read_csv('predict_label.csv')
    
    raise SystemExit("請先成功獲取API數據後再繼續")

# ============================================================================
# 步驟 2: 數據探索與預處理
# ============================================================================
print("\n" + "=" * 80)
print("步驟 2: 數據探索與預處理")
print("=" * 80)

print("\n行為數據概覽:")
print(f"  總用戶數: {len(behavior_df)}")
print(f"  特徵數量: {len(behavior_df.columns)}")
print(f"  特徵列表: {list(behavior_df.columns)}")

print("\n訓練標籤概覽:")
print(f"  標註用戶數: {len(train_labels_df)}")
if 'status' in train_labels_df.columns:
    print(f"  黑名單用戶: {train_labels_df['status'].sum()} ({train_labels_df['status'].mean()*100:.2f}%)")
    print(f"  正常用戶: {(train_labels_df['status']==0).sum()} ({(1-train_labels_df['status'].mean())*100:.2f}%)")

print("\n預測列表概覽:")
print(f"  需預測用戶數: {len(predict_labels_df)}")

# 合併訓練數據
train_df = behavior_df.merge(train_labels_df, on='user_id', how='inner')
print(f"\n✓ 訓練數據合併完成: {len(train_df)} 個用戶")

# 檢查類別平衡
if 'status' in train_df.columns:
    class_distribution = train_df['status'].value_counts()
    print(f"\n類別分布:")
    print(f"  正常用戶 (0): {class_distribution.get(0, 0)}")
    print(f"  黑名單 (1): {class_distribution.get(1, 0)}")
    
    if class_distribution.get(1, 0) == 0:
        print("\n⚠️  警告: 訓練數據中沒有黑名單樣本！")
        print("  這可能導致模型無法學習黑名單特徵")

# 準備預測數據
predict_df = behavior_df.merge(predict_labels_df, on='user_id', how='inner')
print(f"✓ 預測數據準備完成: {len(predict_df)} 個用戶")

# 識別特徵列（排除user_id和status）
feature_columns = [col for col in behavior_df.columns if col not in ['user_id', 'status']]
print(f"\n特徵列 ({len(feature_columns)} 個):")
for i, col in enumerate(feature_columns, 1):
    print(f"  {i}. {col}")

# ============================================================================
# 步驟 3: 特徵工程
# ============================================================================
print("\n" + "=" * 80)
print("步驟 3: 特徵工程")
print("=" * 80)

# 處理缺失值
print("\n檢查缺失值...")
missing_counts = train_df[feature_columns].isnull().sum()
if missing_counts.sum() > 0:
    print("發現缺失值:")
    print(missing_counts[missing_counts > 0])
    print("使用中位數填充...")
    for col in feature_columns:
        if train_df[col].isnull().sum() > 0:
            median_val = train_df[col].median()
            train_df[col].fillna(median_val, inplace=True)
            predict_df[col].fillna(median_val, inplace=True)
else:
    print("✓ 無缺失值")

# 處理異常值
print("\n處理異常值...")
for col in feature_columns:
    if train_df[col].dtype in ['float64', 'int64']:
        Q1 = train_df[col].quantile(0.01)
        Q3 = train_df[col].quantile(0.99)
        train_df[col] = train_df[col].clip(Q1, Q3)
        predict_df[col] = predict_df[col].clip(Q1, Q3)

print("✓ 異常值處理完成")

# ============================================================================
# 步驟 4: 模型訓練
# ============================================================================
print("\n" + "=" * 80)
print("步驟 4: 模型訓練")
print("=" * 80)

# 準備訓練數據
X = train_df[feature_columns]
y = train_df['status']

# 檢查是否有足夠的正負樣本
if y.nunique() < 2:
    print("\n⚠️  錯誤: 訓練數據只有一個類別，無法訓練分類模型")
    print("  請確認 train_label API 返回的數據包含黑名單樣本 (status=1)")
    raise SystemExit("訓練數據類別不足")

# 分割訓練集和驗證集
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n數據分割:")
print(f"  訓練集: {len(X_train)} 樣本")
print(f"  驗證集: {len(X_val)} 樣本")

# 特徵標準化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)

# 訓練模型
print("\n訓練模型...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)
print("✓ 模型訓練完成")

# ============================================================================
# 步驟 5: 模型評估
# ============================================================================
print("\n" + "=" * 80)
print("步驟 5: 模型評估")
print("=" * 80)

# 驗證集預測
y_val_pred = model.predict(X_val_scaled)
y_val_proba = model.predict_proba(X_val_scaled)[:, 1]

# 計算指標
auc = roc_auc_score(y_val, y_val_proba)
f1 = f1_score(y_val, y_val_pred)

print(f"\n驗證集性能:")
print(f"  AUC Score: {auc:.4f}")
print(f"  F1 Score: {f1:.4f}")

print("\n分類報告:")
print(classification_report(y_val, y_val_pred, target_names=['正常', '黑名單']))

print("\n混淆矩陣:")
cm = confusion_matrix(y_val, y_val_pred)
print(f"              預測正常  預測黑名單")
print(f"實際正常      {cm[0,0]:6d}    {cm[0,1]:6d}")
print(f"實際黑名單    {cm[1,0]:6d}    {cm[1,1]:6d}")

# ============================================================================
# 步驟 6: 生成預測結果
# ============================================================================
print("\n" + "=" * 80)
print("步驟 6: 生成預測結果")
print("=" * 80)

# 準備預測數據
X_predict = predict_df[feature_columns]
X_predict_scaled = scaler.transform(X_predict)

# 進行預測
predictions = model.predict(X_predict_scaled)

# 創建提交文件
submission_df = pd.DataFrame({
    'user_id': predict_df['user_id'],
    'status': predictions
})

# 保存CSV
output_filename = f"{TEAM_NAME}.csv"
submission_df.to_csv(output_filename, index=False)

print(f"\n✓ 預測完成:")
print(f"  總用戶數: {len(submission_df)}")
print(f"  預測為黑名單: {predictions.sum()} ({predictions.mean()*100:.2f}%)")
print(f"  預測為正常: {(predictions==0).sum()} ({(1-predictions.mean())*100:.2f}%)")

print(f"\n✓ 提交文件已生成: {output_filename}")

# 顯示樣本
print("\n預測結果樣本 (前20個):")
print(submission_df.head(20).to_string(index=False))

# 驗證提交文件格式
print("\n" + "=" * 80)
print("提交文件驗證")
print("=" * 80)

# 檢查格式
print(f"\n✓ 檔名: {output_filename}")
print(f"✓ 格式: CSV")
print(f"✓ 欄位: {list(submission_df.columns)}")
print(f"✓ user_id 數量: {len(submission_df)}")
print(f"✓ status 值: {sorted(submission_df['status'].unique())}")

# 檢查 user_id 是否一致
if set(submission_df['user_id']) == set(predict_labels_df['user_id']):
    print(f"✓ user_id 與 predict_label 名單一致")
else:
    print(f"⚠️  user_id 與 predict_label 名單不一致")
    missing = set(predict_labels_df['user_id']) - set(submission_df['user_id'])
    if missing:
        print(f"  缺少的 user_id: {len(missing)} 個")

# 檢查 status 值
if set(submission_df['status'].unique()).issubset({0, 1}):
    print(f"✓ status 值正確 (0 或 1)")
else:
    print(f"⚠️  status 值異常: {submission_df['status'].unique()}")

print("\n" + "=" * 80)
print("完成！")
print("=" * 80)
print(f"\n請提交文件: {output_filename}")
print(f"確認事項:")
print(f"  ✓ 檔名為隊伍名稱")
print(f"  ✓ 包含 user_id 和 status 兩欄")
print(f"  ✓ user_id 與 predict_label 名單一致")
print(f"  ✓ status 值為 0 (正常) 或 1 (黑名單)")
print("=" * 80)
