# Requirements Document: Data Preprocessing Pipeline

## Introduction

資料前處理 pipeline 是一個健壯且靈活的資料轉換系統，負責將從 BitoPro API 接入層獲取的原始資料（JSON 或 CSV 格式）轉換為可用於機器學習模型訓練的乾淨資料集。系統設計遵循容錯優先原則，能夠處理欄位變動、缺失值、型態不一致等各種資料品質問題，確保 pipeline 穩定運行不中斷。

核心價值：
- 自動化資料清理與轉換流程
- 智能處理缺失值與異常值
- 靈活適應欄位增減變化
- 產出標準化的訓練資料集
- 支援 train/validation 資料分割

## Glossary

- **Pipeline**: 資料前處理流程，包含讀取、清理、轉換、輸出等步驟
- **Raw_Data**: 從 BitoPro API 接入層獲取的原始資料（JSON 或 CSV 格式）
- **Processed_Data**: 經過前處理後的乾淨資料，可直接用於模型訓練
- **Missing_Value**: 資料中的缺失值（null, NaN, empty string 等）
- **Categorical_Field**: 類別型欄位，包含有限個離散值（如 status, currency）
- **Numerical_Field**: 數值型欄位，包含連續或離散的數值（如 amount, count）
- **Datetime_Field**: 日期時間欄位，包含時間戳記或日期字串
- **ID_Like_Field**: 識別碼類欄位，如 transaction_id, user_id, UUID 等
- **Feature_Engineering**: 特徵工程，從原始欄位衍生新特徵（如從 datetime 提取 hour, day）
- **Scaling**: 數值標準化或正規化處理（如 StandardScaler, MinMaxScaler）
- **Encoding**: 類別欄位編碼（如 One-Hot Encoding, Label Encoding）
- **Train_Validation_Split**: 將資料分割為訓練集與驗證集
- **Schema**: 資料結構定義，包含欄位名稱、型態、處理規則等

## Requirements

### Requirement 1: 讀取原始資料

**User Story:** 作為資料科學家，我希望 pipeline 能夠讀取 JSON 或 CSV 格式的原始資料，以便進行後續處理。

#### Acceptance Criteria

1. WHEN 提供 JSON 檔案路徑，THE Pipeline SHALL 讀取 JSON 檔案並解析為資料結構
2. WHEN 提供 CSV 檔案路徑，THE Pipeline SHALL 讀取 CSV 檔案並解析為資料結構
3. IF 檔案不存在或無法讀取，THEN THE Pipeline SHALL 記錄錯誤訊息並返回描述性錯誤
4. WHEN JSON 資料包含 nested 結構，THE Pipeline SHALL 自動扁平化為單層結構
5. THE Pipeline SHALL 支援 UTF-8 編碼的檔案讀取
6. WHEN 讀取成功，THE Pipeline SHALL 返回包含所有原始欄位的資料結構

### Requirement 2: 缺失值處理

**User Story:** 作為資料科學家，我希望 pipeline 能夠智能處理缺失值，以確保資料完整性。

#### Acceptance Criteria

1. WHEN 數值欄位包含缺失值，THE Pipeline SHALL 使用該欄位的中位數填補缺失值
2. WHEN 類別欄位包含缺失值，THE Pipeline SHALL 使用該欄位的眾數填補缺失值
3. IF 欄位缺失值比例超過 80%，THEN THE Pipeline SHALL 記錄警告訊息但繼續處理
4. WHEN 整列資料完全缺失，THE Pipeline SHALL 移除該列資料
5. THE Pipeline SHALL 記錄每個欄位的缺失值數量與比例
6. WHEN 無法推斷適當的填補值，THE Pipeline SHALL 使用預設值（數值為 0，類別為 "unknown"）

### Requirement 3: 類別欄位編碼

**User Story:** 作為資料科學家，我希望類別欄位能夠被編碼為數值，以便模型訓練使用。

#### Acceptance Criteria

1. WHEN 類別欄位的唯一值數量小於等於 10，THE Pipeline SHALL 使用 One-Hot Encoding 編碼該欄位
2. WHEN 類別欄位的唯一值數量大於 10，THE Pipeline SHALL 使用 Label Encoding 編碼該欄位
3. THE Pipeline SHALL 保存編碼映射關係至 encoding_map.json 檔案
4. WHEN 遇到訓練時未見過的類別值，THE Pipeline SHALL 將其編碼為預設值（-1 或新增 "unknown" 類別）
5. THE Pipeline SHALL 在編碼前移除類別欄位中的前後空白字元
6. WHEN 類別欄位包含布林值，THE Pipeline SHALL 將其轉換為 0 和 1

### Requirement 4: Datetime 特徵提取

**User Story:** 作為資料科學家，我希望從 datetime 欄位提取有用的時間特徵，以增強模型表現。

#### Acceptance Criteria

1. WHEN 欄位被識別為 datetime 型態，THE Pipeline SHALL 從該欄位提取 hour 特徵（0-23）
2. WHEN 欄位被識別為 datetime 型態，THE Pipeline SHALL 從該欄位提取 day 特徵（1-31）
3. WHEN 欄位被識別為 datetime 型態，THE Pipeline SHALL 從該欄位提取 weekday 特徵（0-6，0 為星期一）
4. WHEN 欄位被識別為 datetime 型態，THE Pipeline SHALL 從該欄位提取 month 特徵（1-12）
5. THE Pipeline SHALL 移除原始 datetime 欄位，僅保留提取的時間特徵
6. IF datetime 欄位無法解析，THEN THE Pipeline SHALL 記錄警告並將該欄位視為文字欄位處理

### Requirement 5: 數值欄位處理

**User Story:** 作為資料科學家，我希望數值欄位保留原值，僅在必要時進行 scaling，以保持資料的可解釋性。

#### Acceptance Criteria

1. THE Pipeline SHALL 保留所有數值欄位的原始值
2. WHERE 使用者明確指定需要 scaling，THE Pipeline SHALL 對指定的數值欄位進行標準化處理
3. WHEN 進行 scaling，THE Pipeline SHALL 使用 StandardScaler（零均值、單位變異數）
4. THE Pipeline SHALL 保存 scaling 參數至 scaler_params.json 檔案
5. WHEN 數值欄位包含無限值或極端異常值，THE Pipeline SHALL 將其替換為該欄位的 99 百分位數值
6. THE Pipeline SHALL 記錄哪些欄位進行了 scaling 處理

### Requirement 6: 移除 ID-like 欄位

**User Story:** 作為資料科學家，我希望自動移除不具預測價值的 ID 類欄位，以簡化模型輸入。

#### Acceptance Criteria

1. WHEN 欄位名稱包含 "id", "uuid", "key", "hash", "token" 關鍵字，THE Pipeline SHALL 識別該欄位為 ID-like 欄位
2. WHEN 欄位值符合 UUID 格式，THE Pipeline SHALL 識別該欄位為 ID-like 欄位
3. WHEN 欄位值符合長字串 hash 格式（32+ 字元的十六進位字串），THE Pipeline SHALL 識別該欄位為 ID-like 欄位
4. THE Pipeline SHALL 移除所有識別為 ID-like 的欄位
5. THE Pipeline SHALL 記錄被移除的 ID-like 欄位清單至日誌
6. WHERE 使用者明確指定保留特定 ID 欄位，THE Pipeline SHALL 保留該欄位不移除

### Requirement 7: 產出 Processed CSV

**User Story:** 作為資料科學家，我希望 pipeline 產出標準格式的 CSV 檔案，以便後續模型訓練使用。

#### Acceptance Criteria

1. THE Pipeline SHALL 將處理後的資料輸出為 CSV 格式檔案
2. THE Pipeline SHALL 使用 UTF-8 編碼儲存 CSV 檔案
3. THE Pipeline SHALL 在 CSV 檔案中包含欄位標題列
4. THE Pipeline SHALL 確保 CSV 檔案中不包含索引欄位
5. WHEN 輸出路徑已存在同名檔案，THE Pipeline SHALL 覆寫該檔案並記錄警告訊息
6. THE Pipeline SHALL 在輸出檔案名稱中包含處理時間戳記（如 processed_20240101_120000.csv）

### Requirement 8: Train/Validation 資料分割

**User Story:** 作為資料科學家，我希望 pipeline 自動將資料分割為訓練集與驗證集，以便進行模型評估。

#### Acceptance Criteria

1. THE Pipeline SHALL 將處理後的資料分割為訓練集與驗證集
2. THE Pipeline SHALL 使用 80/20 的比例進行資料分割（80% 訓練，20% 驗證）
3. THE Pipeline SHALL 使用隨機分割方式，並設定固定的隨機種子以確保可重現性
4. THE Pipeline SHALL 輸出 train.csv 和 validation.csv 兩個檔案
5. WHERE 資料包含時間序列特性，THE Pipeline SHALL 支援按時間順序分割（較早資料為訓練集）
6. THE Pipeline SHALL 記錄訓練集與驗證集的資料筆數

### Requirement 9: 欄位變動容錯處理

**User Story:** 作為資料工程師，我希望 pipeline 能夠處理欄位增加或減少的情況，以確保系統穩定運行。

#### Acceptance Criteria

1. WHEN 新資料包含訓練時未見過的欄位，THE Pipeline SHALL 記錄新欄位資訊並根據型態進行相應處理
2. WHEN 新資料缺少訓練時存在的欄位，THE Pipeline SHALL 為缺少的欄位填補預設值
3. THE Pipeline SHALL 維護欄位處理規則的版本記錄
4. WHEN 欄位型態發生變化，THE Pipeline SHALL 嘗試型態轉換，若失敗則記錄錯誤並使用預設值
5. THE Pipeline SHALL 在處理完成後輸出欄位變動報告（新增、移除、型態變更的欄位清單）
6. THE Pipeline SHALL 支援載入先前保存的處理規則（schema, encoding_map, scaler_params）以確保一致性

### Requirement 10: Pipeline 穩定性保證

**User Story:** 作為資料工程師，我希望 pipeline 在任何情況下都不會中斷，以確保資料處理流程的可靠性。

#### Acceptance Criteria

1. THE Pipeline SHALL 捕捉所有處理過程中的例外狀況
2. WHEN 發生錯誤，THE Pipeline SHALL 記錄詳細錯誤訊息至日誌檔案
3. IF 單一欄位處理失敗，THEN THE Pipeline SHALL 跳過該欄位並繼續處理其他欄位
4. IF 單一資料列處理失敗，THEN THE Pipeline SHALL 跳過該列並繼續處理其他資料列
5. THE Pipeline SHALL 在處理完成後輸出處理摘要報告（成功筆數、失敗筆數、警告數量）
6. THE Pipeline SHALL 確保即使部分資料處理失敗，仍能產出可用的輸出檔案

### Requirement 11: 處理規則輸出

**User Story:** 作為資料科學家，我希望 pipeline 輸出詳細的處理規則文件，以便理解資料轉換過程。

#### Acceptance Criteria

1. THE Pipeline SHALL 輸出 preprocessing_rules.json 檔案，包含所有欄位的處理規則
2. THE Pipeline SHALL 在處理規則中記錄每個欄位的型態（numeric, categorical, datetime, text, id-like）
3. THE Pipeline SHALL 在處理規則中記錄每個欄位的處理方式（encoding, scaling, feature extraction, removal）
4. THE Pipeline SHALL 輸出 encoding_map.json 檔案，包含類別欄位的編碼映射關係
5. WHERE 進行了 scaling，THE Pipeline SHALL 輸出 scaler_params.json 檔案，包含 scaling 參數（mean, std）
6. THE Pipeline SHALL 在處理規則中記錄缺失值處理策略與填補值

### Requirement 12: 輸出檔案格式規範

**User Story:** 作為資料科學家，我希望所有輸出檔案遵循一致的格式規範，以便自動化處理。

#### Acceptance Criteria

1. THE Pipeline SHALL 將所有輸出檔案儲存至指定的輸出目錄
2. THE Pipeline SHALL 使用以下檔案命名規範：processed_{timestamp}.csv, train.csv, validation.csv
3. THE Pipeline SHALL 輸出 metadata.json 檔案，包含處理時間、輸入檔案路徑、輸出檔案路徑、資料筆數等資訊
4. THE Pipeline SHALL 確保所有 JSON 格式檔案使用縮排格式化（indent=2）以提高可讀性
5. THE Pipeline SHALL 在 metadata.json 中記錄 pipeline 版本號
6. THE Pipeline SHALL 輸出 processing_log.txt 檔案，包含詳細的處理日誌

### Requirement 13: 例外處理與錯誤報告

**User Story:** 作為資料工程師，我希望 pipeline 提供清晰的錯誤訊息與例外處理，以便快速定位問題。

#### Acceptance Criteria

1. WHEN 輸入檔案格式無效，THE Pipeline SHALL 返回描述性錯誤訊息並終止處理
2. WHEN 輸出目錄不存在，THE Pipeline SHALL 自動建立輸出目錄
3. WHEN 輸出目錄無寫入權限，THE Pipeline SHALL 返回權限錯誤訊息並終止處理
4. THE Pipeline SHALL 在日誌中記錄每個處理步驟的開始與結束時間
5. WHEN 處理過程中發生警告，THE Pipeline SHALL 在日誌中記錄警告訊息但繼續處理
6. THE Pipeline SHALL 在處理完成後輸出錯誤摘要報告，包含所有錯誤與警告的統計資訊
