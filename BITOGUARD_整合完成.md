# BitoGuard Demo - 真實 API 整合完成 ✅

## 完成內容

已成功將 BitoGuard Demo 從模擬資料升級為整合真實 BitoPro API 的版本。

### 主要改進

1. **真實 API 整合** ✅
   - 從 BitoPro API 獲取真實用戶資料
   - 支援 6 個資料端點（交易、轉帳、用戶資訊等）
   - 實作資料快取機制（1 小時）

2. **機器學習模型** ✅
   - Random Forest 分類器
   - 18+ 個真實特徵
   - 自動特徵工程
   - 即時風險評分

3. **保持原有設計** ✅
   - 台北城市儀表板風格
   - 深色主題、緊湊卡片
   - 專業金融風格

## 使用方法

### 快速啟動

```bash
cd bitoguard_demo
pip install -r requirements.txt
streamlit run app.py
```

或使用啟動腳本：
- Windows: `run_real_api_demo.bat`
- Linux/Mac: `./run_real_api_demo.sh`

### 查詢用戶

1. 在搜尋框輸入 User ID（例如：`12345`）
2. 點擊「🔍 查詢」按鈕
3. 等待載入（首次約 30-60 秒）
4. 查看風險分析結果

### 測試 API

```bash
python test_real_api.py
```

## 功能特色

### 真實資料分析
- ✅ 從 BitoPro API 獲取真實交易資料
- ✅ 計算 18+ 個風險特徵
- ✅ 使用機器學習模型評分
- ✅ 顯示詳細特徵分析

### 風險評估
- 🟢 **低風險** (0.0-0.5): 正常用戶
- 🟡 **中風險** (0.5-0.7): 需要監控
- 🔴 **高風險** (0.7-1.0): 需要調查

### 特徵類別
- **交易特徵**: 交易筆數、金額、買入比例等
- **轉帳特徵**: 加密貨幣轉帳、TWD 轉帳、幣種數量
- **兌換特徵**: USDT 兌換次數和金額
- **用戶特徵**: 年齡、性別、KYC Level 2 狀態

## 檔案說明

### 核心檔案
- `app.py` - 主程式（已更新）
- `requirements.txt` - 依賴套件（已更新）

### 文件
- `README_REAL_API.md` - 完整使用說明
- `QUICK_START_REAL_API.md` - 快速開始指南
- `BITOGUARD_REAL_API_INTEGRATION.md` - 詳細整合報告

### 工具
- `test_real_api.py` - API 連線測試
- `run_real_api_demo.bat` - Windows 啟動腳本
- `run_real_api_demo.sh` - Linux/Mac 啟動腳本

## 技術架構

```
用戶輸入 User ID
    ↓
載入 BitoPro API 資料（快取 1 小時）
    ↓
特徵工程（18+ 特徵）
    ↓
標準化（StandardScaler）
    ↓
Random Forest 模型預測
    ↓
風險分數 + 等級 + 建議
```

## 效能說明

- **首次查詢**: 30-60 秒（載入資料 + 訓練模型）
- **後續查詢**: 2-5 秒（使用快取）
- **快取時間**: 1 小時

## 注意事項

1. ✅ 需要網路連線（存取 BitoPro API）
2. ✅ 首次啟動較慢（只需一次）
3. ✅ 資料會快取 1 小時
4. ✅ 輸入純數字 User ID

## 測試範例

試試這些 User ID：
- `12345`
- `67890`
- `11111`
- `99999`

## 問題排解

### API 連線失敗
```bash
python test_real_api.py
```

### 找不到用戶
- 確認輸入純數字 User ID
- 嘗試其他 User ID
- 檢查網路連線

### 速度太慢
- 首次載入需要時間（正常）
- 後續查詢會快很多
- 可修改程式碼減少訓練樣本

## 總結

✅ **完成項目**:
- 真實 API 整合
- 機器學習模型
- 18+ 個特徵
- 完整文件
- 測試工具

✅ **保持原有**:
- 台北城市儀表板風格
- 緊湊卡片設計
- 專業金融風格

🚀 **準備就緒**: 可以開始使用和演示！

---

**版本**: 2.0 (Real API Integration)
**狀態**: ✅ 完成
**日期**: 2026-03-26
