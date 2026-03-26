# BitoGuard Live Demo - 異常交易偵測系統

## 🎯 Demo 目標

這是一個專業的風控系統展示介面，展示 **BitoGuard 如何捕捉異常交易**的完整流程。

## ✨ 主要功能

### 1. 資料載入 (步驟 1)
- 使用範例資料或上傳 CSV
- 一鍵開始分析

### 2. 系統分析結果 (步驟 2)
- **KPI 卡片**：總帳號數、可疑帳號數、平均風險分數、高風險帳號數
- **風險警示**：自動顯示風險警告訊息

### 3. 風險分析圖表 (步驟 3)
- **風險分數分布圖**：展示正常 vs 異常帳號的分數分布
- **特徵重要性圖**：顯示模型判斷的關鍵特徵

### 4. 可疑帳號列表 (步驟 4)
- 可疑帳號排序（風險分數、交易量、交易速度）
- 表格顯示關鍵指標
- 風險等級標示（高/中/低）

### 5. 帳號詳細分析 (步驟 5)
- **基本資訊**：帳號ID、風險分數、風險等級
- **交易統計**：總交易量、交易筆數、平均交易額
- **行為特徵**：夜間交易比例、大額交易比例、交易速度
- **異常原因分析**：列出所有異常特徵
- **交易時間軸**：30天交易量趨勢圖

### 6. 風控建議 (步驟 6)
- 根據風險等級提供不同的處置建議
- 高風險：立即凍結、身份驗證、調查報告
- 中風險：加強監控、設定通知
- 低風險：常規監控

## 🚀 快速開始

### 安裝依賴

```bash
cd bitoguard_demo
pip install -r requirements.txt
```

### 啟動 Demo

```bash
streamlit run app.py
```

Demo 將在瀏覽器中自動開啟：`http://localhost:8501`

## 📊 Demo 流程

1. **點擊「開始分析」** - 載入範例資料（100個帳號，15%異常）
2. **查看 KPI 卡片** - 了解整體風險狀況
3. **查看風險分布圖** - 理解模型如何區分正常/異常
4. **瀏覽可疑帳號列表** - 查看排序後的高風險帳號
5. **選擇帳號深入分析** - 了解為什麼被判定為異常
6. **查看風控建議** - 獲得具體的處置建議

## 🎨 UI 設計特色

### 專業金融風格
- 清晰的區塊劃分
- 專業的配色方案（藍色主調）
- 醒目的風險標示（紅/橙/綠）

### 流程導向設計
- 步驟指示器（步驟 1-6）
- 漸進式資訊揭露
- 清楚的操作引導

### 互動性強
- 即時資料更新
- 可選擇帳號查看詳情
- 可調整風險閾值
- 可切換排序方式

## 📁 檔案結構

```
bitoguard_demo/
├── app.py              # 主程式
├── requirements.txt    # Python 依賴
└── README.md          # 說明文件
```

## 🔧 客製化選項

### 調整風險閾值
在側邊欄可以調整風險判定閾值（預設 0.5）

### 資料來源
- **範例資料**：自動生成 100 個帳號（15% 異常）
- **上傳 CSV**：支援自訂資料格式

### 必要欄位（CSV 格式）
```
account_id, total_transactions, total_volume, avg_transaction_size,
unique_counterparties, night_transaction_ratio, large_transaction_ratio,
velocity_score, risk_score, prediction, label
```

## 🎯 比賽展示建議

### 展示重點
1. **開場**：介紹 BitoGuard 系統目標
2. **資料載入**：展示一鍵分析功能
3. **整體概況**：說明 KPI 卡片的意義
4. **風險分布**：解釋模型如何區分正常/異常
5. **案例分析**：選擇一個高風險帳號深入說明
6. **風控建議**：展示系統提供的處置建議

### 時間分配（5分鐘展示）
- 系統介紹：30秒
- 資料載入與分析：30秒
- KPI 與圖表說明：1分鐘
- 可疑帳號列表：1分鐘
- 詳細案例分析：1.5分鐘
- 風控建議與總結：30秒

## 🔄 後續整合

### 整合真實資料
將 `generate_mock_data()` 替換為實際的資料載入邏輯：

```python
def load_real_data():
    # 從資料庫或 API 載入
    df = pd.read_sql(query, connection)
    # 或從 S3 載入
    df = pd.read_csv('s3://bucket/data.csv')
    return df
```

### 整合模型預測
將模擬的風險分數替換為實際模型預測：

```python
from src.model_risk_scoring import RiskScorer

scorer = RiskScorer()
predictions = scorer.predict(df)
df['risk_score'] = predictions
```

### 整合圖表生成器
使用已實作的圖表生成器：

```python
from src.model_evaluation_viz.core.chart_generator import ChartGenerator

generator = ChartGenerator()
fig = generator.generate_roc_curve(y_true, y_proba, save=False)
st.plotly_chart(fig)
```

## 💡 進階功能建議

### 即時監控
- WebSocket 連接即時更新
- 自動刷新最新交易資料

### 歷史追蹤
- 查看帳號歷史風險分數變化
- 比較不同時間點的行為模式

### 批次處理
- 上傳大量帳號進行批次分析
- 匯出分析報告

### 警報系統
- 設定自動警報規則
- Email/SMS 通知

## 📞 技術支援

如有問題或建議，請聯繫開發團隊。

---

**BitoGuard Team** © 2024
