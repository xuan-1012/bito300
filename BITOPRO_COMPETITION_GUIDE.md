<<<<<<< HEAD
# BitoPro AWS Event 競賽完整指南

## 📋 競賽要求

### 1. 數據獲取
- **API文檔**: https://aws-event-docs.bitopro.com/
- **API端點**: https://aws-event-api.bitopro.com/

需要獲取三個數據集:
1. **行為數據** (`/behavior_data`): 1個月的去識別化用戶行為數據
2. **訓練標籤** (`/train_label`): 已標註的用戶狀態 (status: 1=黑名單, 0=正常)
3. **預測列表** (`/predict_label`): 需要預測的 user_id 列表

### 2. 任務要求
- 結合行為數據與 train_label 進行模型訓練
- 對 predict_label 列表中的用戶進行預測
- 生成 CSV 提交文件

### 3. 提交格式
- **檔名**: 隊伍名稱.csv
- **內容**: 必須包含 `user_id` 與 `status` (0 或 1)
- **要求**: user_id 必須與 predict_label 名單一致

---

## 🚀 快速開始

### 步驟 1: 環境準備

```bash
# 安裝依賴
pip install requests pandas numpy scikit-learn joblib

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 步驟 2: 配置隊伍名稱

編輯 `scripts/bitopro_competition_solution.py`:

```python
TEAM_NAME = "your_team_name"  # 替換為你的隊伍名稱
```

### 步驟 3: 執行完整流程

```bash
python scripts/bitopro_competition_solution.py
```

這將自動完成:
1. ✅ 從 API 獲取數據
2. ✅ 數據預處理與特徵工程
3. ✅ 模型訓練與評估
4. ✅ 生成預測結果
5. ✅ 輸出提交文件 `{隊伍名稱}.csv`

---

## 📊 系統架構

### 完整流程圖

```
┌─────────────────────────────────────────────────────────────┐
│                    BitoPro API                              │
│  https://aws-event-api.bitopro.com/                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ├─── /behavior_data
                           ├─── /train_label
                           └─── /predict_label
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 1: 數據獲取與合併                          │
│  - 行為數據 (1個月去識別化數據)                             │
│  - 訓練標籤 (status: 0=正常, 1=黑名單)                      │
│  - 預測列表 (需預測的 user_id)                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 2: 數據預處理                              │
│  - 缺失值處理 (中位數填充)                                  │
│  - 異常值處理 (1%-99% 分位數裁剪)                           │
│  - 特徵標準化 (StandardScaler)                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 3: 模型訓練                                │
│  - 算法: Random Forest / Gradient Boosting                  │
│  - 類別平衡: class_weight='balanced'                        │
│  - 交叉驗證: 5-fold Stratified CV                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 4: 模型評估                                │
│  - AUC Score                                                │
│  - F1 Score                                                 │
│  - Confusion Matrix                                         │
│  - Classification Report                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 5: 預測與提交                              │
│  - 對 predict_label 進行預測                                │
│  - 生成 CSV: {隊伍名稱}.csv                                 │
│  - 格式: user_id, status                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 技術實現

### 1. API 數據獲取

```python
import requests
import pandas as pd

API_BASE_URL = "https://aws-event-api.bitopro.com"

# 獲取行為數據
response = requests.get(f"{API_BASE_URL}/behavior_data")
behavior_df = pd.DataFrame(response.json())

# 獲取訓練標籤
response = requests.get(f"{API_BASE_URL}/train_label")
train_labels_df = pd.DataFrame(response.json())

# 獲取預測列表
response = requests.get(f"{API_BASE_URL}/predict_label")
predict_labels_df = pd.DataFrame(response.json())
```

### 2. 數據合併

```python
# 合併訓練數據
train_df = behavior_df.merge(train_labels_df, on='user_id', how='inner')

# 準備預測數據
predict_df = behavior_df.merge(predict_labels_df, on='user_id', how='inner')
```

### 3. 特徵工程

```python
from sklearn.preprocessing import StandardScaler

# 識別特徵列
feature_columns = [col for col in behavior_df.columns 
                   if col not in ['user_id', 'status']]

# 標準化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_df[feature_columns])
X_predict_scaled = scaler.transform(predict_df[feature_columns])
```

### 4. 模型訓練

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',  # 處理類別不平衡
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)
```

### 5. 預測與提交

```python
# 預測
predictions = model.predict(X_predict_scaled)

# 生成提交文件
submission_df = pd.DataFrame({
    'user_id': predict_df['user_id'],
    'status': predictions
})

# 保存 CSV
submission_df.to_csv(f"{TEAM_NAME}.csv", index=False)
```

---

## 📈 模型性能優化

### 1. 處理類別不平衡

```python
# 方法 1: 使用 class_weight
model = RandomForestClassifier(class_weight='balanced')

# 方法 2: 使用 SMOTE 過採樣
from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# 方法 3: 調整閾值
threshold = 0.3  # 降低閾值以提高召回率
predictions = (model.predict_proba(X_test)[:, 1] >= threshold).astype(int)
```

### 2. 特徵重要性分析

```python
# 獲取特徵重要性
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

# 選擇 Top K 特徵
top_features = feature_importance.head(20)['feature'].tolist()
```

### 3. 超參數調優

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 15, 20],
    'min_samples_split': [5, 10, 15],
    'min_samples_leaf': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1
)

grid_search.fit(X_train_scaled, y_train)
best_model = grid_search.best_estimator_
```

### 4. 模型集成

```python
from sklearn.ensemble import VotingClassifier

# 創建多個模型
rf = RandomForestClassifier(n_estimators=200, random_state=42)
gb = GradientBoostingClassifier(n_estimators=200, random_state=42)
xgb = XGBClassifier(n_estimators=200, random_state=42)

# 投票集成
ensemble = VotingClassifier(
    estimators=[('rf', rf), ('gb', gb), ('xgb', xgb)],
    voting='soft'
)

ensemble.fit(X_train_scaled, y_train)
```

---

## ✅ 提交檢查清單

在提交前，請確認:

- [ ] **檔名正確**: 檔名為隊伍名稱 (例如: `team_awesome.csv`)
- [ ] **格式正確**: CSV 格式，包含 `user_id` 和 `status` 兩欄
- [ ] **欄位正確**: 
  - `user_id`: 整數，與 predict_label 一致
  - `status`: 0 (正常) 或 1 (黑名單)
- [ ] **數量一致**: user_id 數量與 predict_label 完全一致
- [ ] **無缺失值**: 所有 user_id 都有對應的 status
- [ ] **無重複值**: 每個 user_id 只出現一次

### 驗證腳本

```python
import pandas as pd

# 讀取提交文件
submission = pd.read_csv(f"{TEAM_NAME}.csv")

# 檢查
print("檢查項目:")
print(f"✓ 欄位: {list(submission.columns)}")
print(f"✓ 數量: {len(submission)}")
print(f"✓ status 值: {sorted(submission['status'].unique())}")
print(f"✓ 缺失值: {submission.isnull().sum().sum()}")
print(f"✓ 重複值: {submission['user_id'].duplicated().sum()}")
```

---

## 🎯 評分標準 (預期)

競賽可能使用以下指標評分:

1. **AUC Score** (主要指標)
   - 衡量模型區分黑名單和正常用戶的能力
   - 範圍: 0.5 (隨機) ~ 1.0 (完美)

2. **F1 Score**
   - 平衡精確率和召回率
   - 適合類別不平衡的場景

3. **Precision / Recall**
   - Precision: 預測為黑名單中真正是黑名單的比例
   - Recall: 實際黑名單中被正確識別的比例

---

## 🐛 常見問題

### Q1: API 請求失敗怎麼辦?

```python
# 添加錯誤處理和重試機制
import time

def fetch_with_retry(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"嘗試 {i+1}/{max_retries} 失敗: {e}")
            if i < max_retries - 1:
                time.sleep(2 ** i)  # 指數退避
            else:
                raise
```

### Q2: 訓練數據類別極度不平衡?

```python
# 使用 SMOTE 或調整 class_weight
from imblearn.over_sampling import SMOTE

smote = SMOTE(sampling_strategy=0.3, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

### Q3: 模型性能不佳?

嘗試:
1. 增加特徵工程 (交互特徵、多項式特徵)
2. 嘗試不同算法 (XGBoost, LightGBM)
3. 調整超參數
4. 使用模型集成

### Q4: 預測結果全是 0 或全是 1?

檢查:
1. 訓練數據是否包含兩個類別
2. 模型是否過擬合
3. 閾值是否需要調整

---

## 📚 相關資源

### 文檔
- [Swagger API 文檔](https://aws-event-docs.bitopro.com/)
- [Scikit-learn 文檔](https://scikit-learn.org/)
- [Pandas 文檔](https://pandas.pydata.org/)

### 本項目文件
- `scripts/bitopro_competition_solution.py` - 完整解決方案
- `scripts/fetch_and_train.py` - 數據獲取與訓練
- `examples/process_user_list.py` - 批次處理示例
- `EXECUTION_DATA_SUMMARY.md` - 執行數據總結
- `TECHNICAL_DOCUMENTATION.md` - 技術文檔

---

## 🎉 成功案例

### 預期輸出

```
================================================================================
BitoPro AWS Event - 可疑帳戶檢測競賽解決方案
================================================================================

步驟 1: 從 API 獲取數據
✓ 成功獲取行為數據: 10000 筆記錄
✓ 成功獲取訓練標籤: 8000 個用戶
✓ 成功獲取預測列表: 2000 個用戶

步驟 2: 數據探索與預處理
✓ 訓練數據合併完成: 8000 個用戶
  - 黑名單用戶: 800 (10.00%)
  - 正常用戶: 7200 (90.00%)

步驟 3: 特徵工程
✓ 無缺失值
✓ 異常值處理完成

步驟 4: 模型訓練
✓ 模型訓練完成

步驟 5: 模型評估
  AUC Score: 0.9234
  F1 Score: 0.8567

步驟 6: 生成預測結果
✓ 預測完成: 2000 個用戶
✓ 提交文件已生成: team_awesome.csv

提交文件驗證
✓ 檔名: team_awesome.csv
✓ 格式: CSV
✓ user_id 與 predict_label 名單一致
✓ status 值正確 (0 或 1)

完成！
================================================================================
```

---

**祝你在 BitoPro AWS Event 競賽中取得好成績！** 🏆
=======
# BitoPro AWS Event 競賽完整指南

## 📋 競賽要求

### 1. 數據獲取
- **API文檔**: https://aws-event-docs.bitopro.com/
- **API端點**: https://aws-event-api.bitopro.com/

需要獲取三個數據集:
1. **行為數據** (`/behavior_data`): 1個月的去識別化用戶行為數據
2. **訓練標籤** (`/train_label`): 已標註的用戶狀態 (status: 1=黑名單, 0=正常)
3. **預測列表** (`/predict_label`): 需要預測的 user_id 列表

### 2. 任務要求
- 結合行為數據與 train_label 進行模型訓練
- 對 predict_label 列表中的用戶進行預測
- 生成 CSV 提交文件

### 3. 提交格式
- **檔名**: 隊伍名稱.csv
- **內容**: 必須包含 `user_id` 與 `status` (0 或 1)
- **要求**: user_id 必須與 predict_label 名單一致

---

## 🚀 快速開始

### 步驟 1: 環境準備

```bash
# 安裝依賴
pip install requests pandas numpy scikit-learn joblib

# 或使用 requirements.txt
pip install -r requirements.txt
```

### 步驟 2: 配置隊伍名稱

編輯 `scripts/bitopro_competition_solution.py`:

```python
TEAM_NAME = "your_team_name"  # 替換為你的隊伍名稱
```

### 步驟 3: 執行完整流程

```bash
python scripts/bitopro_competition_solution.py
```

這將自動完成:
1. ✅ 從 API 獲取數據
2. ✅ 數據預處理與特徵工程
3. ✅ 模型訓練與評估
4. ✅ 生成預測結果
5. ✅ 輸出提交文件 `{隊伍名稱}.csv`

---

## 📊 系統架構

### 完整流程圖

```
┌─────────────────────────────────────────────────────────────┐
│                    BitoPro API                              │
│  https://aws-event-api.bitopro.com/                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           ├─── /behavior_data
                           ├─── /train_label
                           └─── /predict_label
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 1: 數據獲取與合併                          │
│  - 行為數據 (1個月去識別化數據)                             │
│  - 訓練標籤 (status: 0=正常, 1=黑名單)                      │
│  - 預測列表 (需預測的 user_id)                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 2: 數據預處理                              │
│  - 缺失值處理 (中位數填充)                                  │
│  - 異常值處理 (1%-99% 分位數裁剪)                           │
│  - 特徵標準化 (StandardScaler)                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 3: 模型訓練                                │
│  - 算法: Random Forest / Gradient Boosting                  │
│  - 類別平衡: class_weight='balanced'                        │
│  - 交叉驗證: 5-fold Stratified CV                           │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 4: 模型評估                                │
│  - AUC Score                                                │
│  - F1 Score                                                 │
│  - Confusion Matrix                                         │
│  - Classification Report                                    │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              步驟 5: 預測與提交                              │
│  - 對 predict_label 進行預測                                │
│  - 生成 CSV: {隊伍名稱}.csv                                 │
│  - 格式: user_id, status                                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 技術實現

### 1. API 數據獲取

```python
import requests
import pandas as pd

API_BASE_URL = "https://aws-event-api.bitopro.com"

# 獲取行為數據
response = requests.get(f"{API_BASE_URL}/behavior_data")
behavior_df = pd.DataFrame(response.json())

# 獲取訓練標籤
response = requests.get(f"{API_BASE_URL}/train_label")
train_labels_df = pd.DataFrame(response.json())

# 獲取預測列表
response = requests.get(f"{API_BASE_URL}/predict_label")
predict_labels_df = pd.DataFrame(response.json())
```

### 2. 數據合併

```python
# 合併訓練數據
train_df = behavior_df.merge(train_labels_df, on='user_id', how='inner')

# 準備預測數據
predict_df = behavior_df.merge(predict_labels_df, on='user_id', how='inner')
```

### 3. 特徵工程

```python
from sklearn.preprocessing import StandardScaler

# 識別特徵列
feature_columns = [col for col in behavior_df.columns 
                   if col not in ['user_id', 'status']]

# 標準化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(train_df[feature_columns])
X_predict_scaled = scaler.transform(predict_df[feature_columns])
```

### 4. 模型訓練

```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    max_depth=15,
    min_samples_split=10,
    min_samples_leaf=5,
    class_weight='balanced',  # 處理類別不平衡
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_scaled, y_train)
```

### 5. 預測與提交

```python
# 預測
predictions = model.predict(X_predict_scaled)

# 生成提交文件
submission_df = pd.DataFrame({
    'user_id': predict_df['user_id'],
    'status': predictions
})

# 保存 CSV
submission_df.to_csv(f"{TEAM_NAME}.csv", index=False)
```

---

## 📈 模型性能優化

### 1. 處理類別不平衡

```python
# 方法 1: 使用 class_weight
model = RandomForestClassifier(class_weight='balanced')

# 方法 2: 使用 SMOTE 過採樣
from imblearn.over_sampling import SMOTE
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)

# 方法 3: 調整閾值
threshold = 0.3  # 降低閾值以提高召回率
predictions = (model.predict_proba(X_test)[:, 1] >= threshold).astype(int)
```

### 2. 特徵重要性分析

```python
# 獲取特徵重要性
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

# 選擇 Top K 特徵
top_features = feature_importance.head(20)['feature'].tolist()
```

### 3. 超參數調優

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [10, 15, 20],
    'min_samples_split': [5, 10, 15],
    'min_samples_leaf': [2, 5, 10]
}

grid_search = GridSearchCV(
    RandomForestClassifier(random_state=42),
    param_grid,
    cv=5,
    scoring='roc_auc',
    n_jobs=-1
)

grid_search.fit(X_train_scaled, y_train)
best_model = grid_search.best_estimator_
```

### 4. 模型集成

```python
from sklearn.ensemble import VotingClassifier

# 創建多個模型
rf = RandomForestClassifier(n_estimators=200, random_state=42)
gb = GradientBoostingClassifier(n_estimators=200, random_state=42)
xgb = XGBClassifier(n_estimators=200, random_state=42)

# 投票集成
ensemble = VotingClassifier(
    estimators=[('rf', rf), ('gb', gb), ('xgb', xgb)],
    voting='soft'
)

ensemble.fit(X_train_scaled, y_train)
```

---

## ✅ 提交檢查清單

在提交前，請確認:

- [ ] **檔名正確**: 檔名為隊伍名稱 (例如: `team_awesome.csv`)
- [ ] **格式正確**: CSV 格式，包含 `user_id` 和 `status` 兩欄
- [ ] **欄位正確**: 
  - `user_id`: 整數，與 predict_label 一致
  - `status`: 0 (正常) 或 1 (黑名單)
- [ ] **數量一致**: user_id 數量與 predict_label 完全一致
- [ ] **無缺失值**: 所有 user_id 都有對應的 status
- [ ] **無重複值**: 每個 user_id 只出現一次

### 驗證腳本

```python
import pandas as pd

# 讀取提交文件
submission = pd.read_csv(f"{TEAM_NAME}.csv")

# 檢查
print("檢查項目:")
print(f"✓ 欄位: {list(submission.columns)}")
print(f"✓ 數量: {len(submission)}")
print(f"✓ status 值: {sorted(submission['status'].unique())}")
print(f"✓ 缺失值: {submission.isnull().sum().sum()}")
print(f"✓ 重複值: {submission['user_id'].duplicated().sum()}")
```

---

## 🎯 評分標準 (預期)

競賽可能使用以下指標評分:

1. **AUC Score** (主要指標)
   - 衡量模型區分黑名單和正常用戶的能力
   - 範圍: 0.5 (隨機) ~ 1.0 (完美)

2. **F1 Score**
   - 平衡精確率和召回率
   - 適合類別不平衡的場景

3. **Precision / Recall**
   - Precision: 預測為黑名單中真正是黑名單的比例
   - Recall: 實際黑名單中被正確識別的比例

---

## 🐛 常見問題

### Q1: API 請求失敗怎麼辦?

```python
# 添加錯誤處理和重試機制
import time

def fetch_with_retry(url, max_retries=3):
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"嘗試 {i+1}/{max_retries} 失敗: {e}")
            if i < max_retries - 1:
                time.sleep(2 ** i)  # 指數退避
            else:
                raise
```

### Q2: 訓練數據類別極度不平衡?

```python
# 使用 SMOTE 或調整 class_weight
from imblearn.over_sampling import SMOTE

smote = SMOTE(sampling_strategy=0.3, random_state=42)
X_resampled, y_resampled = smote.fit_resample(X_train, y_train)
```

### Q3: 模型性能不佳?

嘗試:
1. 增加特徵工程 (交互特徵、多項式特徵)
2. 嘗試不同算法 (XGBoost, LightGBM)
3. 調整超參數
4. 使用模型集成

### Q4: 預測結果全是 0 或全是 1?

檢查:
1. 訓練數據是否包含兩個類別
2. 模型是否過擬合
3. 閾值是否需要調整

---

## 📚 相關資源

### 文檔
- [Swagger API 文檔](https://aws-event-docs.bitopro.com/)
- [Scikit-learn 文檔](https://scikit-learn.org/)
- [Pandas 文檔](https://pandas.pydata.org/)

### 本項目文件
- `scripts/bitopro_competition_solution.py` - 完整解決方案
- `scripts/fetch_and_train.py` - 數據獲取與訓練
- `examples/process_user_list.py` - 批次處理示例
- `EXECUTION_DATA_SUMMARY.md` - 執行數據總結
- `TECHNICAL_DOCUMENTATION.md` - 技術文檔

---

## 🎉 成功案例

### 預期輸出

```
================================================================================
BitoPro AWS Event - 可疑帳戶檢測競賽解決方案
================================================================================

步驟 1: 從 API 獲取數據
✓ 成功獲取行為數據: 10000 筆記錄
✓ 成功獲取訓練標籤: 8000 個用戶
✓ 成功獲取預測列表: 2000 個用戶

步驟 2: 數據探索與預處理
✓ 訓練數據合併完成: 8000 個用戶
  - 黑名單用戶: 800 (10.00%)
  - 正常用戶: 7200 (90.00%)

步驟 3: 特徵工程
✓ 無缺失值
✓ 異常值處理完成

步驟 4: 模型訓練
✓ 模型訓練完成

步驟 5: 模型評估
  AUC Score: 0.9234
  F1 Score: 0.8567

步驟 6: 生成預測結果
✓ 預測完成: 2000 個用戶
✓ 提交文件已生成: team_awesome.csv

提交文件驗證
✓ 檔名: team_awesome.csv
✓ 格式: CSV
✓ user_id 與 predict_label 名單一致
✓ status 值正確 (0 或 1)

完成！
================================================================================
```

---

**祝你在 BitoPro AWS Event 競賽中取得好成績！** 🏆
>>>>>>> 3ed03a3 (Initial commit)
