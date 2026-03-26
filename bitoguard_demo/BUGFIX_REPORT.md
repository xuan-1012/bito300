# BitoGuard Demo - Bug 修復報告

## 問題描述

用戶在執行 BitoGuard Demo 時遇到 `IndexError: index 1 is out of bounds for axis 0 with size 1` 錯誤。

### 錯誤位置
```
File "bitoguard_demo\app.py", line 604, in <module>
    result = predict_risk_for_user(user_id, api_data)
File "bitoguard_demo\app.py", line 333, in predict_risk_for_user
    risk_score = model.predict_proba(X_scaled)[0][1]
```

## 根本原因

1. **模型訓練資料只有單一類別**：當訓練資料中只包含一個類別（全部為 0 或全部為 1）時，RandomForestClassifier 的 `predict_proba` 只會返回一個機率值
2. **API 端點錯誤**：`crypto_transfer` 和 `user_info` 端點返回 502 Bad Gateway 錯誤
3. **錯誤處理不足**：原代碼沒有處理單一類別的情況

## 修復方案

### 1. 改進 `train_model_if_needed` 函數

**修復內容**：
- 檢查訓練資料的類別分布
- 如果只有單一類別，自動添加模擬的另一類別資料
- 確保模型至少訓練兩個類別

```python
# 檢查類別分布
unique_classes = y.unique()
if len(unique_classes) < 2:
    st.warning(f"⚠️ 訓練資料只有一個類別 ({unique_classes[0]})，使用模擬資料補充")
    # 添加模擬資料...
```

### 2. 改進 `predict_risk_for_user` 函數

**修復內容**：
- 處理單一類別情況
- 處理兩個類別情況
- 添加異常處理和預設值
- 確保返回值類型正確

```python
# 處理不同類別情況
if len(model.classes_) == 1:
    # 只有一個類別
    if model.classes_[0] == 1:
        risk_score = proba[0]
        prediction = 1
    else:
        risk_score = 1 - proba[0]
        prediction = 0
elif len(model.classes_) == 2:
    # 有兩個類別（正常情況）
    if 1 in model.classes_:
        class_1_idx = list(model.classes_).index(1)
        risk_score = proba[class_1_idx]
    else:
        risk_score = 1 - proba[0]
    prediction = model.predict(X_scaled)[0]
```

### 3. 改進 API 錯誤處理

**修復內容**：
- 將 `st.error` 改為 `st.warning`，避免阻斷執行
- 處理 502 Bad Gateway 錯誤
- 處理超時錯誤
- 返回空 DataFrame 而不是拋出異常

```python
elif response.status_code == 502:
    st.warning(f"⚠️ API 暫時無法使用: {endpoint} (502 Bad Gateway) - 使用空資料")
    return pd.DataFrame()
```

### 4. 改進資料載入流程

**修復內容**：
- 添加進度顯示
- 顯示每個端點的載入狀態
- 檢查是否有足夠的資料
- 顯示資料載入摘要

```python
progress_text = st.empty()
progress_text.text('📊 載入 USDT/TWD 交易資料...')
usdt_twd = fetch_bitopro_data('usdt_twd_trading')
# ...
st.success(f"✅ 資料載入完成: ...")
```

## 測試結果

✅ 語法檢查通過
✅ 單一類別情況處理正確
✅ API 錯誤處理正確
✅ 異常處理完善

## 使用方式

### 方式 1：使用批次檔啟動
```bash
cd bitoguard_demo
run_fixed_demo.bat
```

### 方式 2：直接使用 Streamlit
```bash
cd bitoguard_demo
streamlit run app.py --server.port 8502
```

## 功能說明

### 搜尋功能
- 輸入 User ID（數字）進行查詢
- 使用真實 BitoPro API 資料
- 顯示用戶風險分數和詳細特徵

### 總覽功能
- 點擊「總覽」按鈕查看模擬資料
- 顯示所有帳號的風險分布
- 顯示可疑帳號列表

## 已知限制

1. **API 穩定性**：部分 BitoPro API 端點可能返回 502 錯誤
2. **訓練速度**：首次查詢需要訓練模型，可能需要等待
3. **資料完整性**：如果 API 端點失敗，某些特徵可能為空

## 建議

1. **生產環境**：建議使用預訓練模型，避免每次啟動都訓練
2. **錯誤監控**：添加日誌記錄，追蹤 API 錯誤
3. **快取策略**：增加快取時間，減少 API 請求
4. **備用方案**：當 API 完全失敗時，切換到 `app_v2.py`（穩定的模擬資料版本）

## 修復時間

2026-03-26 22:19

## 修復者

Kiro AI Assistant
