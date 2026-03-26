#!/usr/bin/env python3
"""
測試預測問題：檢查為什麼所有預測都是 1
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import requests
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

print("=" * 80)
print("BitoGuard Demo - 預測問題診斷")
print("=" * 80)

# 載入真實資料
print("\n步驟 1: 載入 BitoPro API 資料...")
def fetch_data(endpoint):
    url = f'https://aws-event-api.bitopro.com/{endpoint}'
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            df = pd.DataFrame(r.json())
            print(f"  ✓ {endpoint}: {len(df)} 筆")
            return df
        else:
            print(f"  ✗ {endpoint}: 錯誤 {r.status_code}")
            return pd.DataFrame()
    except Exception as e:
        print(f"  ✗ {endpoint}: {str(e)}")
        return pd.DataFrame()

train_labels = fetch_data('train_label')

if train_labels.empty:
    print("\n❌ 無法載入訓練標籤")
    sys.exit(1)

# 檢查訓練標籤分布
print(f"\n步驟 2: 檢查訓練標籤分布")
print(f"  總數: {len(train_labels)}")
print(f"  類別分布:")
print(train_labels['status'].value_counts())
print(f"  類別 0 (Normal): {(train_labels['status'] == 0).sum()} ({(train_labels['status'] == 0).mean()*100:.1f}%)")
print(f"  類別 1 (Suspicious): {(train_labels['status'] == 1).sum()} ({(train_labels['status'] == 1).mean()*100:.1f}%)")

# 模擬訓練過程
print(f"\n步驟 3: 模擬訓練過程")
# 創建簡單的特徵（模擬）
np.random.seed(42)
n_samples = min(100, len(train_labels))
X = np.random.rand(n_samples, 5)
y = train_labels['status'].values[:n_samples]

print(f"  訓練樣本數: {n_samples}")
print(f"  訓練類別分布: {np.unique(y, return_counts=True)}")

# 訓練模型
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=10,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)
model.fit(X_scaled, y)

print(f"  模型訓練完成")
print(f"  模型類別: {model.classes_}")

# 測試預測
print(f"\n步驟 4: 測試預測")
test_samples = 10
X_test = np.random.rand(test_samples, 5)
X_test_scaled = scaler.transform(X_test)

predictions = model.predict(X_test_scaled)
probas = model.predict_proba(X_test_scaled)

print(f"  測試樣本數: {test_samples}")
print(f"  預測結果:")
for i in range(test_samples):
    pred = predictions[i]
    proba = probas[i]
    
    # 計算風險分數（與 app.py 相同的邏輯）
    if len(model.classes_) == 2 and 1 in model.classes_:
        class_1_idx = list(model.classes_).index(1)
        risk_score = proba[class_1_idx]
    else:
        risk_score = proba[0]
    
    label = 'Suspicious' if pred == 1 else 'Normal'
    print(f"    樣本 {i+1}: 預測={pred}, 標籤={label}, 風險分數={risk_score:.3f}, 機率={proba}")

# 統計預測結果
print(f"\n步驟 5: 統計預測結果")
print(f"  預測為 0 (Normal): {(predictions == 0).sum()} ({(predictions == 0).mean()*100:.1f}%)")
print(f"  預測為 1 (Suspicious): {(predictions == 1).sum()} ({(predictions == 1).mean()*100:.1f}%)")

# 檢查是否所有預測都是 1
if (predictions == 1).all():
    print(f"\n⚠️ 警告：所有預測都是 1 (Suspicious)")
    print(f"  可能原因：")
    print(f"    1. 訓練資料不平衡（類別 1 佔比過高）")
    print(f"    2. 特徵工程問題（所有特徵都指向異常）")
    print(f"    3. 模型參數問題（class_weight='balanced' 可能過度補償）")
elif (predictions == 0).all():
    print(f"\n⚠️ 警告：所有預測都是 0 (Normal)")
else:
    print(f"\n✅ 預測結果正常（有 0 也有 1）")

print("\n" + "=" * 80)
print("診斷完成")
print("=" * 80)
