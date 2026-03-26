# BitoGuard Demo - 真實 API 整合版

## 概述

這個版本的 BitoGuard Demo 整合了真實的 BitoPro API 資料，可以：

1. **查詢真實用戶**: 輸入 User ID 查詢真實的 BitoPro 用戶資料
2. **即時風險評估**: 使用機器學習模型進行即時風險評分
3. **特徵工程**: 從多個 API 端點提取並計算風險特徵
4. **台北城市儀表板風格**: 緊湊、專業的深色主題設計

## 功能特色

### 1. 真實 API 整合
- 從 BitoPro API 獲取真實交易資料
- 支援多個資料端點：
  - USDT/TWD 交易
  - 加密貨幣轉帳
  - TWD 轉帳
  - USDT 兌換
  - 用戶資訊

### 2. 機器學習風險評估
- 使用 Random Forest 分類器
- 自動特徵工程（18+ 個特徵）
- 即時風險分數計算
- 風險等級分類（低/中/高）

### 3. 美觀的 UI 設計
- 參考台北城市儀表板設計
- 深色主題 (#0f1419 背景)
- 緊湊卡片式佈局
- 即時更新指示器

## 安裝

```bash
# 安裝依賴
pip install -r requirements.txt

# 額外需要的套件
pip install scikit-learn requests
```

## 使用方法

### 1. 啟動 Demo

```bash
# Windows
cd bitoguard_demo
streamlit run app.py

# Linux/Mac
cd bitoguard_demo
streamlit run app.py
```

### 2. 測試 API 連線

```bash
python test_real_api.py
```

### 3. 查詢用戶

1. 在搜尋框輸入 User ID（例如：12345）
2. 點擊「🔍 查詢」按鈕
3. 系統會：
   - 從 API 獲取用戶資料
   - 進行特徵工程
   - 計算風險分數
   - 顯示詳細分析結果

### 4. 查看總覽

點擊「📊 總覽」按鈕查看模擬資料的統計總覽（包含圖表和可疑帳號列表）

## 特徵說明

系統會從以下維度分析用戶行為：

### 交易特徵
- `trade_count`: 交易筆數
- `trade_amount_sum`: 交易總額
- `trade_amount_mean`: 平均交易金額
- `trade_amount_std`: 交易金額標準差
- `buy_ratio`: 買入比例
- `market_order_ratio`: 市價單比例

### 轉帳特徵
- `crypto_transfer_count`: 加密貨幣轉帳次數
- `crypto_amount_sum`: 加密貨幣轉帳總額
- `crypto_amount_mean`: 平均轉帳金額
- `unique_currencies`: 使用的幣種數量
- `twd_transfer_count`: TWD 轉帳次數
- `twd_amount_sum`: TWD 轉帳總額
- `twd_amount_mean`: 平均 TWD 轉帳金額

### 兌換特徵
- `swap_count`: USDT 兌換次數
- `swap_twd_sum`: USDT 兌換總額

### 用戶資訊
- `age`: 年齡
- `sex`: 性別（M=1, F=0）
- `has_level2`: 是否完成 Level 2 KYC

## 風險等級

- **低風險** (0.0 - 0.5): 🟢 正常用戶，維持常規監控
- **中風險** (0.5 - 0.7): 🟡 需要加強監控，設定即時通知
- **高風險** (0.7 - 1.0): 🔴 建議立即凍結並進行調查

## 技術架構

```
用戶輸入 User ID
    ↓
載入 API 資料 (快取 1 小時)
    ↓
特徵工程 (18+ 特徵)
    ↓
標準化 (StandardScaler)
    ↓
模型預測 (Random Forest)
    ↓
風險分數 + 建議
```

## 注意事項

1. **首次載入**: 第一次查詢時需要載入 API 資料並訓練模型，可能需要 30-60 秒
2. **快取機制**: API 資料會快取 1 小時，減少重複請求
3. **模型訓練**: 為了加快速度，只使用前 1000 個訓練樣本
4. **網路需求**: 需要穩定的網路連線來存取 BitoPro API

## 疑難排解

### API 連線失敗
```bash
# 測試 API 連線
python test_real_api.py
```

### 模型訓練太慢
- 減少訓練樣本數量（修改 `train_model_if_needed` 函數中的 `[:1000]`）
- 使用更簡單的模型（減少 `n_estimators`）

### 記憶體不足
- 限制 API 資料的 limit 參數
- 清除快取：重新啟動 Streamlit

## 開發者資訊

- **版本**: 2.0 (Real API Integration)
- **框架**: Streamlit + Scikit-learn
- **API**: BitoPro AWS Event API
- **設計風格**: 台北城市儀表板

## 授權

MIT License
