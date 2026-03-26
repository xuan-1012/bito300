# BitoPro Competition - 模型比較分析報告

## 執行摘要

測試了5個不同的機器學習模型，使用相同的特徵工程和訓練數據。

## 模型性能排名（按AUC-ROC）

| 排名 | 模型 | AUC-ROC | AUC-PR | Precision | Recall | F1-Score |
|------|------|---------|--------|-----------|--------|----------|
| 🥇 1 | **Gradient Boosting** | **0.8004** | 0.1371 | 0.2784 | 0.0823 | 0.1271 |
| 🥈 2 | LightGBM | 0.7856 | 0.1670 | 0.1075 | 0.5091 | 0.1776 |
| 🥉 3 | Random Forest | 0.7853 | 0.1605 | 0.1377 | 0.3750 | 0.2015 |
| 4 | XGBoost | 0.7838 | 0.1723 | 0.1182 | 0.4939 | 0.1908 |
| 5 | Logistic Regression | 0.7435 | 0.1070 | 0.0748 | 0.5518 | 0.1317 |

## 關鍵發現

### 1. AUC-ROC 最佳：Gradient Boosting (0.8004)
- ✅ **最高的AUC-ROC分數**
- ✅ 最高的Precision (27.84%)
- ✅ 最少的False Positives (70個)
- ⚠️ 但Recall較低 (8.23%)
- ⚠️ 預測可疑用戶最保守 (僅0.73%)

### 2. Recall 最佳：Logistic Regression (55.18%)
- ✅ 能找到最多的可疑用戶
- ❌ 但AUC最低 (0.7435)
- ❌ Precision最低 (7.48%)
- ❌ 大量False Positives (2,239個)

### 3. 平衡性最佳：LightGBM & XGBoost
- LightGBM: Recall 50.91%, Precision 10.75%
- XGBoost: Recall 49.39%, Precision 11.82%
- 在找到可疑用戶和減少誤報之間取得較好平衡

### 4. Random Forest (原始模型)
- AUC: 0.7853 (第3名)
- Recall: 37.50% (中等)
- Precision: 13.77% (中等)
- 預測可疑用戶: 8.87%

## 預測結果比較

| 模型 | 預測可疑用戶數 | 可疑比例 | 預測正常用戶數 | 正常比例 |
|------|---------------|---------|---------------|---------|
| Gradient Boosting | 93 | 0.73% | 12,660 | 99.27% |
| Random Forest | 1,131 | 8.87% | 11,622 | 91.13% |
| XGBoost | 1,754 | 13.75% | 10,999 | 86.25% |
| LightGBM | 1,938 | 15.20% | 10,815 | 84.80% |
| Logistic Regression | 3,050 | 23.92% | 9,703 | 76.08% |

**訓練數據可疑比例**: 3.21% (1,640/51,017)

## 詳細分析

### Gradient Boosting（最高AUC）
**優點**:
- 最高的AUC-ROC (0.8004)，表示整體分類能力最強
- 最高的Precision (27.84%)，預測為可疑的用戶中有28%是真的可疑
- 最少的False Positives，不會誤判太多正常用戶

**缺點**:
- Recall很低 (8.23%)，只能找到8%的可疑用戶
- 預測可疑用戶數量太少 (93人，0.73%)，遠低於訓練數據的3.21%
- 可能過於保守，會漏掉很多真正的可疑用戶

**適用場景**: 當誤報成本很高時（例如：不想錯誤封鎖正常用戶）

### XGBoost（平衡性好）
**優點**:
- AUC-PR最高 (0.1723)，在不平衡數據上表現好
- Recall接近50%，能找到一半的可疑用戶
- 預測可疑比例 (13.75%) 接近訓練數據的3-4倍，較為合理

**缺點**:
- AUC-ROC略低於Gradient Boosting
- Precision較低 (11.82%)

**適用場景**: 需要在找到可疑用戶和減少誤報之間取得平衡

### LightGBM（Recall高）
**優點**:
- AUC-ROC第二高 (0.7856)
- Recall超過50%，能找到一半以上的可疑用戶
- 訓練速度快

**缺點**:
- Precision較低 (10.75%)
- 預測可疑比例 (15.20%) 較高

**適用場景**: 當漏報成本很高時（寧可多抓一些，不要漏掉可疑用戶）

### Random Forest（原始模型）
**優點**:
- AUC-ROC第三高 (0.7853)
- Recall和Precision都在中等水平
- 預測可疑比例 (8.87%) 較為合理

**缺點**:
- 沒有特別突出的優勢
- 各項指標都不是最佳

**適用場景**: 通用場景，不確定業務需求時的安全選擇

## 建議

### 情境1: 追求最高準確度（推薦）
**選擇**: **Gradient Boosting**
- 文件: `predictions_gradient_boosting.csv`
- 理由: AUC-ROC最高 (0.8004)，整體分類能力最強
- 風險: 可能漏掉較多可疑用戶

### 情境2: 平衡準確度和召回率
**選擇**: **XGBoost** 或 **LightGBM**
- 文件: `predictions_xgboost.csv` 或 `predictions_lightgbm.csv`
- 理由: 在找到可疑用戶和減少誤報之間取得較好平衡
- XGBoost略優於LightGBM (AUC-PR更高)

### 情境3: 不想漏掉可疑用戶
**選擇**: **Logistic Regression**
- 文件: `predictions_logistic_regression.csv`
- 理由: Recall最高 (55.18%)，能找到最多可疑用戶
- 風險: 會有大量誤報

## 為什麼status=1變多了？

您之前的Random Forest模型預測了8.87%的用戶為可疑，這是合理的，因為：

1. **訓練數據可疑比例**: 3.21%
2. **Random Forest預測**: 8.87% (約2.8倍)
3. **XGBoost預測**: 13.75% (約4.3倍)
4. **LightGBM預測**: 15.20% (約4.7倍)

不同模型的預測比例差異很大，這是因為：
- **Gradient Boosting**: 過於保守，只預測0.73%
- **Random Forest**: 較為平衡，預測8.87%
- **XGBoost/LightGBM**: 較為激進，預測13-15%
- **Logistic Regression**: 非常激進，預測23.92%

## 最終建議

根據AUC-ROC指標，**Gradient Boosting是最準確的模型**，但它預測的可疑用戶數量太少。

如果您想要：
1. **最高準確度**: 使用 `predictions_gradient_boosting.csv`
2. **平衡性能**: 使用 `predictions_xgboost.csv` ⭐ **推薦**
3. **原始結果**: 使用 `predictions_random_forest.csv` (your_team_name_new.csv)

**我的推薦**: **XGBoost** - 它在AUC-ROC、Recall和Precision之間取得了最好的平衡，預測的可疑比例也較為合理。

## 生成的文件

1. `predictions_random_forest.csv` - Random Forest預測 (8.87%可疑)
2. `predictions_xgboost.csv` - XGBoost預測 (13.75%可疑) ⭐
3. `predictions_lightgbm.csv` - LightGBM預測 (15.20%可疑)
4. `predictions_gradient_boosting.csv` - Gradient Boosting預測 (0.73%可疑)
5. `predictions_logistic_regression.csv` - Logistic Regression預測 (23.92%可疑)
6. `model_comparison_results.csv` - 詳細比較結果

---
**生成時間**: 2026-03-26
**腳本**: `scripts/model_comparison.py`
