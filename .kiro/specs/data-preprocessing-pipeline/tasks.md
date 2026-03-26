# Implementation Plan: Data Preprocessing Pipeline

## Overview

以 Python 實作模組化的資料前處理 pipeline，依序建立資料模型、各處理元件、主協調器，最後整合輸出。

## Tasks

- [x] 1. 建立專案結構與核心資料模型
  - 建立 `src/preprocessing/` 目錄結構與 `__init__.py`
  - 在 `models.py` 中實作 `FieldSchema`、`PipelineConfig`、`PipelineResult` dataclasses
  - _Requirements: 11.1, 11.2, 11.3, 12.3, 12.5_

- [x] 2. 實作資料讀取模組
  - [x] 2.1 實作 `reader.py` 中的 `read_file()` 與 `flatten_json()`
    - 支援 JSON（含 nested 扁平化）與 CSV 讀取，UTF-8 編碼
    - 檔案不存在或格式無效時 raise `PipelineReadError`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_
  - [ ]* 2.2 撰寫 `reader.py` 的單元測試
    - 測試 JSON/CSV 讀取、nested 扁平化、錯誤處理
    - _Requirements: 1.3, 1.4_

- [x] 3. 實作 Schema 推斷模組
  - [x] 3.1 實作 `schema.py` 中的 `infer_schema()`、`is_id_like()`、`is_datetime()`
    - 推斷欄位型態：id-like、datetime、numeric、categorical、text
    - ID-like 判斷：名稱關鍵字（id/uuid/key/hash/token）、UUID regex、32+ 字元十六進位
    - _Requirements: 6.1, 6.2, 6.3, 9.1, 9.2, 9.4_
  - [ ]* 3.2 撰寫 `schema.py` 的單元測試
    - 測試各型態推斷邏輯與邊界條件
    - _Requirements: 6.1, 6.2, 6.3_

- [x] 4. 實作缺失值清理模組
  - [x] 4.1 實作 `cleaner.py` 中的 `clean()`
    - 移除完全空白列（Requirement 2.4）
    - 數值欄位填補中位數，類別欄位填補眾數，無法計算時使用預設值
    - 缺失比例 > 80% 時記錄警告
    - 替換無限值與極端異常值為 99 百分位數
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 5.5_
  - [ ]* 4.2 撰寫 Property 1 的 property-based test
    - **Property 1: 缺失值填補後無缺失值**
    - **Validates: Requirements 2.1, 2.2, 2.4, 2.6**
  - [ ]* 4.3 撰寫 `cleaner.py` 的單元測試
    - 測試各填補策略、警告觸發、無限值替換
    - _Requirements: 2.1, 2.2, 2.3, 2.5, 2.6_

- [x] 5. 實作 ID-like 欄位移除模組
  - [x] 5.1 實作 `id_remover.py` 中的 `remove_id_fields()`
    - 移除 schema 中標記為 id-like 的欄位（keep_fields 中的欄位除外）
    - 記錄被移除的欄位清單
    - _Requirements: 6.4, 6.5, 6.6_
  - [ ]* 5.2 撰寫 Property 5 的 property-based test
    - **Property 5: ID-like 欄位移除後不存在**
    - **Validates: Requirements 6.4, 6.6**
  - [ ]* 5.3 撰寫 `id_remover.py` 的單元測試
    - 測試移除邏輯與 keep_fields 保留行為
    - _Requirements: 6.4, 6.5, 6.6_

- [x] 6. 實作 Datetime 特徵提取模組
  - [x] 6.1 實作 `datetime_extractor.py` 中的 `extract_datetime_features()`
    - 提取 `{col}_hour`、`{col}_day`、`{col}_weekday`、`{col}_month`
    - 移除原始 datetime 欄位
    - 解析失敗時記錄警告並視為 text 欄位
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_
  - [ ]* 6.2 撰寫 Property 4 的 property-based test
    - **Property 4: Datetime 提取後無原始 Datetime 欄位**
    - **Validates: Requirements 4.5**
  - [ ]* 6.3 撰寫 `datetime_extractor.py` 的單元測試
    - 測試特徵提取值範圍、原始欄位移除、解析失敗處理
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.6_

- [x] 7. 實作類別欄位編碼模組
  - [x] 7.1 實作 `encoder.py` 中的 `encode()` 與 `apply_encoding_map()`
    - strip 前後空白、bool 轉 0/1
    - 唯一值 ≤ 10 使用 One-Hot Encoding，> 10 使用 Label Encoding
    - 未見過的類別值編碼為 -1 或 "unknown"
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6_
  - [ ]* 7.2 撰寫 Property 2 的 property-based test
    - **Property 2: 編碼後無原始類別欄位**
    - **Validates: Requirements 3.1, 3.2**
  - [ ]* 7.3 撰寫 `encoder.py` 的單元測試
    - 測試 One-Hot/Label 選擇邏輯、未知類別處理、bool 轉換
    - _Requirements: 3.1, 3.2, 3.4, 3.5, 3.6_

- [x] 8. 實作數值 Scaling 模組
  - [x] 8.1 實作 `scaler.py` 中的 `scale()` 與 `apply_scaler_params()`
    - 對指定欄位計算 mean/std 並套用 StandardScaler
    - 返回 scaler_params dict
    - _Requirements: 5.2, 5.3, 5.4, 5.6_
  - [ ]* 8.2 撰寫 Property 6 的 property-based test
    - **Property 6: Scaling 後均值接近 0、標準差接近 1**
    - **Validates: Requirements 5.3**
  - [ ]* 8.3 撰寫 `scaler.py` 的單元測試
    - 測試 scaling 結果、參數保存、未指定欄位不受影響
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6_

- [~] 9. Checkpoint — 確認所有元件測試通過
  - 確保所有單元測試與 property tests 通過，如有問題請提出。

- [~] 10. 實作 Train/Validation 分割模組
  - [~] 10.1 實作 `splitter.py` 中的 `split()`
    - 隨機分割（固定 random_seed）與時間序列分割（按順序）
    - 預設 80/20 比例
    - _Requirements: 8.1, 8.2, 8.3, 8.5_
  - [ ]* 10.2 撰寫 Property 3 的 property-based test
    - **Property 3: Train/Validation 分割無資料遺失**
    - **Validates: Requirements 8.1, 8.2**
  - [ ]* 10.3 撰寫 `splitter.py` 的單元測試
    - 測試比例正確性、隨機種子可重現性、時間序列分割順序
    - _Requirements: 8.2, 8.3, 8.5, 8.6_

- [~] 11. 實作輸出寫入模組
  - [~] 11.1 實作 `writer.py` 中的 `write_outputs()`
    - 輸出 processed_{timestamp}.csv、train.csv、validation.csv（UTF-8, no index）
    - 輸出 preprocessing_rules.json、encoding_map.json、scaler_params.json、metadata.json（indent=2）
    - 輸出 processing_log.txt
    - 自動建立輸出目錄，覆寫時記錄警告
    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 11.1, 11.4, 11.5, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 13.2_
  - [ ]* 11.2 撰寫 Property 7 的 property-based test
    - **Property 7: 輸出列數一致性（processed = train + validation）**
    - **Validates: Requirements 7.1, 8.1**
  - [ ]* 11.3 撰寫 Property 8 的 property-based test
    - **Property 8: JSON 輸出可重新載入**
    - **Validates: Requirements 11.4, 12.4**
  - [ ]* 11.4 撰寫 `writer.py` 的單元測試
    - 測試檔案建立、目錄自動建立、覆寫警告、JSON 格式
    - _Requirements: 7.2, 7.4, 7.5, 12.4, 13.2, 13.3_

- [~] 12. 實作主 Pipeline 協調器
  - [~] 12.1 實作 `pipeline.py` 中的 `run()`
    - 依序執行所有步驟：read → infer_schema → remove_id → clean → extract_datetime → encode → scale → split → write
    - 每步驟包裝在 try/except，單一欄位/列失敗不中斷整體流程
    - 偵測欄位變動（新增、移除、型態變更）並輸出報告
    - 支援載入先前保存的 schema/encoding_map/scaler_params
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 13.1, 13.4, 13.5, 13.6_
  - [ ]* 12.2 撰寫 `pipeline.py` 的整合測試
    - 測試完整 pipeline 執行、容錯行為、欄位變動偵測
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [~] 13. Final Checkpoint — 確認所有測試通過
  - 確保所有單元測試、property tests 與整合測試通過，如有問題請提出。

## Notes

- 標記 `*` 的子任務為選填，可跳過以加速 MVP 開發
- 每個任務均對應需求文件中的具體驗收條件
- Property tests 使用 Hypothesis 框架撰寫
- Checkpoints 確保每個階段的增量驗證
