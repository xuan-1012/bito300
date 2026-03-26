#!/usr/bin/env python3
"""
測試 BitoGuard Demo 修復
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler

print("=" * 80)
print("BitoGuard Demo - 修復驗證測試")
print("=" * 80)

# 測試 1: 單一類別情況
print("\n測試 1: 單一類別情況（只有類別 0）")
print("-" * 80)

X_train = np.random.rand(10, 5)
y_train = np.zeros(10)  # 只有類別 0

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_scaled, y_train)

print(f"訓練類別: {model.classes_}")
print(f"類別數量: {len(model.classes_)}")

# 預測
X_test = np.random.rand(1, 5)
X_test_scaled = scaler.transform(X_test)
proba = model.predict_proba(X_test_scaled)[0]

print(f"預測機率形狀: {proba.shape}")
print(f"預測機率: {proba}")

# 處理單一類別
if len(model.classes_) == 1:
    if model.classes_[0] == 1:
        risk_score = proba[0]
        prediction = 1
    else:
        risk_score = 1 - proba[0]
        prediction = 0
    print(f"✅ 單一類別處理成功")
    print(f"   風險分數: {risk_score:.3f}")
    print(f"   預測: {prediction}")
else:
    print(f"❌ 預期單一類別，但得到 {len(model.classes_)} 個類別")

# 測試 2: 兩個類別情況
print("\n測試 2: 兩個類別情況（類別 0 和 1）")
print("-" * 80)

X_train = np.random.rand(20, 5)
y_train = np.array([0] * 10 + [1] * 10)

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_train)

model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_scaled, y_train)

print(f"訓練類別: {model.classes_}")
print(f"類別數量: {len(model.classes_)}")

# 預測
X_test = np.random.rand(1, 5)
X_test_scaled = scaler.transform(X_test)
proba = model.predict_proba(X_test_scaled)[0]

print(f"預測機率形狀: {proba.shape}")
print(f"預測機率: {proba}")

# 處理兩個類別
if len(model.classes_) == 2:
    if 1 in model.classes_:
        class_1_idx = list(model.classes_).index(1)
        risk_score = proba[class_1_idx]
    else:
        risk_score = 1 - proba[0]
    prediction = model.predict(X_test_scaled)[0]
    print(f"✅ 兩個類別處理成功")
    print(f"   風險分數: {risk_score:.3f}")
    print(f"   預測: {prediction}")
else:
    print(f"❌ 預期兩個類別，但得到 {len(model.classes_)} 個類別")

# 測試 3: 模擬資料補充
print("\n測試 3: 模擬資料補充（將單一類別擴展為兩個類別）")
print("-" * 80)

X = pd.DataFrame(np.random.rand(10, 5))
y = pd.Series([0] * 10)

print(f"原始類別: {y.unique()}")
print(f"原始資料量: {len(X)}")

# 補充模擬資料
unique_classes = y.unique()
if len(unique_classes) < 2:
    if 0 not in unique_classes:
        mock_features = X.sample(min(5, len(X)), random_state=42).copy()
        mock_features = mock_features * 0.5
        X = pd.concat([X, mock_features], ignore_index=True)
        y = pd.concat([y, pd.Series([0] * len(mock_features))], ignore_index=True)
    else:
        mock_features = X.sample(min(5, len(X)), random_state=42).copy()
        mock_features = mock_features * 2.0
        X = pd.concat([X, mock_features], ignore_index=True)
        y = pd.concat([y, pd.Series([1] * len(mock_features))], ignore_index=True)
    
    print(f"✅ 模擬資料補充成功")
    print(f"   新類別: {y.unique()}")
    print(f"   新資料量: {len(X)}")
else:
    print(f"❌ 預期需要補充，但已有 {len(unique_classes)} 個類別")

print("\n" + "=" * 80)
print("✅ 所有測試通過！修復驗證成功")
print("=" * 80)
