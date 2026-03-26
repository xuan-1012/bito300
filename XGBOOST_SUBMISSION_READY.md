# BitoPro Competition - XGBoost提交文件準備完成

## ✅ 提交文件已準備好

**文件名**: `your_team_name_xgboost.csv`

## 📊 文件統計

- **總用戶數**: 12,753
- **預測可疑 (status=1)**: 1,754 (13.75%)
- **預測正常 (status=0)**: 10,999 (86.25%)
- **排序**: ✅ 已按user_id升序排列
- **格式**: ✅ CSV格式，包含user_id和status兩列

## 🎯 模型資訊

**使用模型**: XGBoost Classifier

**模型參數**:
```python
XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    subsample=0.8,
    colsample_bytree=0.8,
    scale_pos_weight=30.1 (自動計算),
    random_state=42,
    eval_metric='auc'
)
```

**性能指標**:
- AUC-ROC: 0.7838
- AUC-PR: 0.1723 (最高！)
- Recall: 49.39%
- Precision: 11.82%
- F1-Score: 0.1908

## 📈 為什麼選擇XGBoost？

1. **AUC-PR最高** (0.1723)
   - 在不平衡數據上表現最好
   - 這是金融風控最重要的指標

2. **平衡性最佳**
   - 能找到近一半的可疑用戶 (Recall: 49.39%)
   - 誤報率可接受 (Precision: 11.82%)

3. **預測比例合理**
   - 訓練數據可疑比例: 3.21%
   - XGBoost預測: 13.75% (約4.3倍)
   - 考慮到未標註數據可能有更多可疑用戶，這個比例是合理的

4. **業界標準**
   - Kaggle競賽最常用模型
   - 金融風控領域標準選擇

## 🔍 數據來源確認

所有預測基於真實API數據：

### 行為數據：
- ✅ 217,634筆 USDT/TWD交易記錄
- ✅ 239,958筆 加密貨幣轉帳記錄
- ✅ 195,601筆 TWD轉帳記錄
- ✅ 53,841筆 USDT交換記錄

### 用戶數據：
- ✅ 63,770筆 用戶資料（年齡、性別、KYC等級）

### 訓練標籤：
- ✅ 51,017筆 已標註訓練數據
- ✅ 可疑用戶: 1,640 (3.21%)
- ✅ 正常用戶: 49,377 (96.79%)

## 🎨 特徵工程

每個用戶提取了18個特徵：

### 交易行為特徵 (6個)：
1. trade_count - 交易次數
2. trade_amount_sum - 交易總金額
3. trade_amount_mean - 平均交易金額
4. trade_amount_std - 交易金額標準差
5. buy_ratio - 買入比例
6. market_order_ratio - 市價單比例

### 加密貨幣轉帳特徵 (4個)：
7. crypto_transfer_count - 轉帳次數
8. crypto_amount_sum - 轉帳總金額
9. crypto_amount_mean - 平均轉帳金額
10. unique_currencies - 使用的幣種數量

### TWD轉帳特徵 (3個)：
11. twd_transfer_count - TWD轉帳次數
12. twd_amount_sum - TWD轉帳總金額
13. twd_amount_mean - 平均TWD轉帳金額

### USDT交換特徵 (2個)：
14. swap_count - 交換次數
15. swap_twd_sum - 交換TWD總金額

### 用戶資料特徵 (3個)：
16. age - 年齡
17. sex - 性別 (M=1, F=0)
18. has_level2 - 是否完成Level 2 KYC

## 📋 文件預覽

前20筆預測：
```
user_id,status
3,0
10,0
98,0
139,0
185,0
218,0
241,0
276,0
373,0
397,1  ← 可疑
500,1  ← 可疑
505,0
506,0
572,0
577,0
778,1  ← 可疑
813,0
917,1  ← 可疑
935,0
1097,0
```

## 🆚 與其他模型比較

| 模型 | AUC-ROC | 預測可疑% | 優勢 |
|------|---------|----------|------|
| Gradient Boosting | 0.8004 | 0.73% | AUC最高但太保守 |
| LightGBM | 0.7856 | 15.20% | Recall高 |
| Random Forest | 0.7853 | 8.87% | 平衡 |
| **XGBoost** | **0.7838** | **13.75%** | **AUC-PR最高，平衡最佳** ⭐ |
| Logistic Regression | 0.7435 | 23.92% | 太激進 |

## 📝 提交步驟

1. **重命名文件**（如果需要）
   ```bash
   # 將文件重命名為您的隊伍名稱
   # 例如：Team_Alpha.csv
   ```

2. **驗證文件格式**
   - ✅ CSV格式
   - ✅ 包含header: user_id,status
   - ✅ 12,753行數據（不含header）
   - ✅ status只有0或1
   - ✅ 按user_id升序排列

3. **上傳到競賽平台**
   - 使用 `your_team_name_xgboost.csv`

## 🎯 預期結果

基於驗證集性能：
- 預計能正確識別約49%的可疑用戶
- 預計誤報率約11.82%
- 整體AUC-ROC約0.78

## 📚 相關文件

- `MODEL_COMPARISON_ANALYSIS.md` - 詳細模型比較分析
- `FINAL_MODEL_RECOMMENDATION.md` - 模型推薦說明
- `模型比較完成報告.md` - 中文完整報告
- `model_comparison_results.csv` - 所有模型性能指標
- `model_comparison_visualization.png` - 性能比較圖表
- `prediction_distribution_comparison.png` - 預測分布圖表

## ✅ 最終檢查清單

- [x] 使用真實API數據訓練
- [x] 使用XGBoost模型（AUC-PR最高）
- [x] 特徵工程完整（18個特徵）
- [x] 數據標準化處理
- [x] 處理類別不平衡（scale_pos_weight）
- [x] 預測結果已排序
- [x] CSV格式正確
- [x] 所有12,753個用戶都有預測

---

**生成時間**: 2026-03-26  
**模型訓練腳本**: `scripts/model_comparison.py`  
**提交文件**: `your_team_name_xgboost.csv`

## 🎉 準備完成！

您的XGBoost預測文件已經準備好提交了！

**文件**: `your_team_name_xgboost.csv`

祝您在競賽中取得好成績！🏆
