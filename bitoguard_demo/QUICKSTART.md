# BitoGuard Demo - 快速啟動指南

## 🚀 3 步驟啟動 Demo

### 步驟 1: 安裝依賴

```bash
cd bitoguard_demo
pip install -r requirements.txt
```

### 步驟 2: 測試環境

```bash
python test_demo.py
```

應該看到：
```
✅ All tests passed! Demo is ready to run.
```

### 步驟 3: 啟動 Demo

**方法 A: 使用啟動腳本 (推薦)**

Windows:
```bash
run_demo.bat
```

Linux/Mac:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

**方法 B: 直接啟動**

```bash
streamlit run app.py
```

Demo 將自動在瀏覽器開啟：`http://localhost:8501`

## 📱 使用 Demo

### 1. 點擊「開始分析」
- 選擇「使用範例資料」
- 點擊「🚀 開始分析」按鈕
- 等待 2-3 秒載入完成

### 2. 查看分析結果
- 查看 KPI 卡片（總帳號數、可疑帳號等）
- 查看風險分布圖
- 查看特徵重要性圖

### 3. 選擇帳號深入分析
- 在「可疑帳號列表」區塊向下滾動
- 在「帳號詳細分析」選擇一個帳號
- 查看異常原因和交易時間軸

### 4. 查看風控建議
- 向下滾動到最底部
- 查看系統提供的處置建議

## 🎬 5分鐘展示流程

詳細展示腳本請參考 `DEMO_GUIDE.md`

簡要流程：
1. 開場介紹 (30秒)
2. 資料載入與分析 (1分鐘)
3. 整體風險概況 (1分鐘)
4. 風險分析圖表 (1分鐘)
5. 深入案例分析 (1.5分鐘) ⭐
6. 風控建議與總結 (30秒)

## ⚙️ 側邊欄功能

### 調整風險閾值
- 使用滑桿調整閾值（0.0 - 1.0）
- 預設值：0.5
- 調整後會影響風險判定

### 重新載入資料
- 點擊「🔄 重新載入資料」
- 會生成新的隨機資料
- 用於展示不同情境

## 🔧 常見問題

### Q: Demo 無法啟動？
A: 確認已安裝所有依賴：
```bash
pip install streamlit pandas numpy plotly
```

### Q: 瀏覽器沒有自動開啟？
A: 手動開啟瀏覽器，訪問：
```
http://localhost:8501
```

### Q: 如何停止 Demo？
A: 在終端機按 `Ctrl + C`

### Q: 如何更改埠號？
A: 使用以下命令：
```bash
streamlit run app.py --server.port 8502
```

### Q: 如何上傳自己的資料？
A: 
1. 選擇「上傳 CSV 檔案」
2. 準備 CSV 檔案，包含以下欄位：
   - account_id
   - total_transactions
   - total_volume
   - avg_transaction_size
   - unique_counterparties
   - night_transaction_ratio
   - large_transaction_ratio
   - velocity_score
   - risk_score
   - prediction
   - label

## 📊 範例資料說明

### 資料規模
- 總帳號數：100
- 正常帳號：85 (85%)
- 異常帳號：15 (15%)

### 特徵說明
- **total_transactions**: 總交易筆數
- **total_volume**: 總交易量（美元）
- **avg_transaction_size**: 平均交易額
- **unique_counterparties**: 交易對手數量
- **night_transaction_ratio**: 夜間交易比例（0-1）
- **large_transaction_ratio**: 大額交易比例（0-1）
- **velocity_score**: 交易速度分數（0-1）
- **risk_score**: 風險分數（0-1）

### 異常特徵
異常帳號通常具有：
- 夜間交易比例 > 40%
- 大額交易比例 > 35%
- 交易速度分數 > 0.6
- 交易對手數量 > 100
- 總交易量 > $100,000

## 🎯 展示技巧

### 語速控制
- 開場和結尾：稍慢
- 中間部分：正常
- 重點內容：放慢強調

### 重點強調
- KPI 數字
- 風險警示框
- 異常原因列表
- 風控建議

### 時間控制
- 目標：4分30秒 - 4分50秒
- 預留 10-30 秒給評審提問

## 📞 需要幫助？

- 查看完整文件：`README.md`
- 查看展示指南：`DEMO_GUIDE.md`
- 執行測試：`python test_demo.py`

---

**準備好了嗎？開始展示吧！** 🚀
