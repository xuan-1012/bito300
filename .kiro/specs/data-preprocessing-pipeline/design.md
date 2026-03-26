# Design Document: Data Preprocessing Pipeline

## Overview

Data Preprocessing Pipeline 是一個以 Python 實作的資料轉換系統，負責將原始 JSON/CSV 資料轉換為可用於機器學習訓練的乾淨資料集。系統採用模組化設計，每個處理步驟獨立封裝，並以容錯優先原則確保 pipeline 穩定運行。

實作語言：**Python**（搭配 pandas、scikit-learn）

---

## Architecture

```
src/preprocessing/
├── __init__.py
├── pipeline.py          # 主 pipeline 協調器
├── reader.py            # 資料讀取（JSON/CSV）
├── cleaner.py           # 缺失值處理、異常值處理
├── encoder.py           # 類別欄位編碼
├── datetime_extractor.py # Datetime 特徵提取
├── scaler.py            # 數值 scaling
├── id_remover.py        # ID-like 欄位識別與移除
├── splitter.py          # Train/Validation 分割
├── writer.py            # 輸出 CSV 與 JSON 規則檔
├── schema.py            # Schema 定義與欄位型態推斷
└── models.py            # 資料模型（dataclasses）

tests/
├── unit/
│   ├── test_reader.py
│   ├── test_cleaner.py
│   ├── test_encoder.py
│   ├── test_datetime_extractor.py
│   ├── test_scaler.py
│   ├── test_id_remover.py
│   ├── test_splitter.py
│   └── test_writer.py
└── property/
    └── test_preprocessing_properties.py
```

---

## Component Design

### 1. Data Models (`models.py`)

```python
@dataclass
class FieldSchema:
    name: str
    field_type: str  # "numeric", "categorical", "datetime", "text", "id-like"
    processing_action: str  # "encode", "scale", "extract", "remove", "keep"
    missing_strategy: str
    fill_value: Any

@dataclass
class PipelineConfig:
    input_path: str
    output_dir: str
    scale_fields: list[str]       # 明確指定需要 scaling 的欄位
    keep_id_fields: list[str]     # 明確指定保留的 ID 欄位
    time_series_split: bool       # 是否按時間順序分割
    random_seed: int = 42
    train_ratio: float = 0.8

@dataclass
class PipelineResult:
    success: bool
    output_files: dict[str, str]
    processed_rows: int
    failed_rows: int
    warnings: list[str]
    errors: list[str]
    field_changes: dict           # 新增、移除、型態變更的欄位
```

### 2. Reader (`reader.py`)

**職責**：讀取 JSON 或 CSV 檔案，自動扁平化 nested JSON。

```python
def read_file(path: str) -> pd.DataFrame:
    # 根據副檔名選擇讀取方式
    # JSON: pd.read_json + json_normalize 扁平化
    # CSV: pd.read_csv with UTF-8 encoding
    # 失敗時 raise DescriptiveReadError

def flatten_json(data: dict | list) -> dict:
    # 遞迴扁平化 nested dict，key 以 "." 連接
```

### 3. Schema Inference (`schema.py`)

**職責**：推斷每個欄位的型態，產生 FieldSchema 清單。

```python
def infer_schema(df: pd.DataFrame) -> list[FieldSchema]:
    # 對每個欄位判斷型態：
    # - id-like: 名稱含關鍵字 or UUID/hash 格式
    # - datetime: 可解析為 datetime
    # - numeric: 數值型
    # - categorical: 字串且唯一值有限
    # - text: 其他字串

def is_id_like(series: pd.Series, name: str, keep_fields: list[str]) -> bool:
    # 檢查名稱關鍵字: id, uuid, key, hash, token
    # 檢查值格式: UUID regex, 32+ 字元十六進位

def is_datetime(series: pd.Series) -> bool:
    # 嘗試 pd.to_datetime 解析
```

### 4. Cleaner (`cleaner.py`)

**職責**：處理缺失值、無限值、完全空白列。

```python
def clean(df: pd.DataFrame, schema: list[FieldSchema]) -> tuple[pd.DataFrame, list[str]]:
    # 1. 移除完全空白列
    # 2. 對每個欄位：
    #    - numeric: 填補中位數（無法計算則填 0）
    #    - categorical: 填補眾數（無法計算則填 "unknown"）
    #    - 缺失比例 > 80%: 記錄警告
    # 3. 替換無限值為 99 百分位數
    # 返回 (cleaned_df, warnings)
```

### 5. Encoder (`encoder.py`)

**職責**：類別欄位 One-Hot 或 Label Encoding，保存映射。

```python
def encode(df: pd.DataFrame, schema: list[FieldSchema]) -> tuple[pd.DataFrame, dict]:
    # 對每個 categorical 欄位：
    # - strip 前後空白
    # - bool -> 0/1
    # - 唯一值 <= 10: One-Hot Encoding (pd.get_dummies)
    # - 唯一值 > 10: Label Encoding (sklearn LabelEncoder)
    # 返回 (encoded_df, encoding_map)

def apply_encoding_map(df: pd.DataFrame, encoding_map: dict) -> pd.DataFrame:
    # 使用已保存的 encoding_map 處理新資料
    # 未見過的類別值 -> -1 或 "unknown"
```

### 6. Datetime Extractor (`datetime_extractor.py`)

**職責**：從 datetime 欄位提取時間特徵，移除原始欄位。

```python
def extract_datetime_features(df: pd.DataFrame, schema: list[FieldSchema]) -> tuple[pd.DataFrame, list[str]]:
    # 對每個 datetime 欄位：
    # - 提取 {col}_hour, {col}_day, {col}_weekday, {col}_month
    # - 移除原始欄位
    # - 解析失敗: 記錄警告，視為 text 欄位
    # 返回 (df, warnings)
```

### 7. Scaler (`scaler.py`)

**職責**：對指定欄位進行 StandardScaler，保存參數。

```python
def scale(df: pd.DataFrame, scale_fields: list[str]) -> tuple[pd.DataFrame, dict]:
    # 對 scale_fields 中存在的欄位：
    # - 計算 mean, std
    # - 套用 (x - mean) / std
    # 返回 (scaled_df, scaler_params)

def apply_scaler_params(df: pd.DataFrame, scaler_params: dict) -> pd.DataFrame:
    # 使用已保存的 scaler_params 處理新資料
```

### 8. ID Remover (`id_remover.py`)

**職責**：移除 ID-like 欄位（除非使用者明確保留）。

```python
def remove_id_fields(df: pd.DataFrame, schema: list[FieldSchema]) -> tuple[pd.DataFrame, list[str]]:
    # 移除 field_type == "id-like" 的欄位
    # 返回 (df, removed_fields)
```

### 9. Splitter (`splitter.py`)

**職責**：將資料分割為 train/validation。

```python
def split(df: pd.DataFrame, config: PipelineConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    # time_series_split=True: 按順序分割（前 80% 為 train）
    # time_series_split=False: 隨機分割（random_seed 固定）
    # 返回 (train_df, validation_df)
```

### 10. Writer (`writer.py`)

**職責**：輸出所有檔案至指定目錄。

```python
def write_outputs(
    processed_df: pd.DataFrame,
    train_df: pd.DataFrame,
    validation_df: pd.DataFrame,
    output_dir: str,
    encoding_map: dict,
    scaler_params: dict,
    schema: list[FieldSchema],
    metadata: dict,
    log_lines: list[str],
) -> dict[str, str]:
    # 輸出：
    # - processed_{timestamp}.csv (UTF-8, no index, with header)
    # - train.csv, validation.csv
    # - preprocessing_rules.json (indent=2)
    # - encoding_map.json (indent=2)
    # - scaler_params.json (indent=2, 僅在有 scaling 時)
    # - metadata.json (indent=2)
    # - processing_log.txt
    # 自動建立輸出目錄
    # 覆寫已存在檔案時記錄警告
    # 返回 {filename: filepath} 映射
```

### 11. Pipeline Coordinator (`pipeline.py`)

**職責**：協調所有步驟，確保容錯執行。

```python
def run(config: PipelineConfig) -> PipelineResult:
    # 步驟順序：
    # 1. read_file
    # 2. infer_schema (含欄位變動偵測)
    # 3. remove_id_fields
    # 4. clean
    # 5. extract_datetime_features
    # 6. encode
    # 7. scale (僅對指定欄位)
    # 8. split
    # 9. write_outputs
    # 每步驟包裝在 try/except，失敗時記錄並繼續
    # 單一欄位/列失敗不中斷整體流程
```

---

## Data Flow

```
Input File (JSON/CSV)
        ↓
    reader.py  →  raw DataFrame
        ↓
    schema.py  →  FieldSchema list + field change report
        ↓
  id_remover.py  →  DataFrame (ID fields removed)
        ↓
   cleaner.py  →  DataFrame (missing values filled)
        ↓
datetime_extractor.py  →  DataFrame (time features added)
        ↓
   encoder.py  →  DataFrame (categoricals encoded) + encoding_map
        ↓
   scaler.py   →  DataFrame (specified fields scaled) + scaler_params
        ↓
   splitter.py →  train_df + validation_df
        ↓
   writer.py   →  Output files
```

---

## Output File Specification

| 檔案 | 格式 | 說明 |
|------|------|------|
| `processed_{timestamp}.csv` | CSV, UTF-8, no index | 完整處理後資料 |
| `train.csv` | CSV, UTF-8, no index | 訓練集（80%） |
| `validation.csv` | CSV, UTF-8, no index | 驗證集（20%） |
| `preprocessing_rules.json` | JSON, indent=2 | 每欄位處理規則 |
| `encoding_map.json` | JSON, indent=2 | 類別編碼映射 |
| `scaler_params.json` | JSON, indent=2 | Scaling 參數（mean, std） |
| `metadata.json` | JSON, indent=2 | 處理時間、路徑、筆數、版本 |
| `processing_log.txt` | Text | 詳細處理日誌 |

---

## Correctness Properties

以下屬性定義了系統的正確性保證，可用於 property-based testing：

**Property 1: 缺失值填補後無缺失值**
對任意 DataFrame，執行 `clean()` 後，所有欄位的缺失值數量應為 0（完全空白列已被移除）。

**Property 2: 編碼後無原始類別欄位**
對任意包含類別欄位的 DataFrame，執行 `encode()` 後，原始類別欄位不應存在於輸出 DataFrame 中。

**Property 3: Train/Validation 分割無資料遺失**
對任意 DataFrame，`split()` 後 `len(train) + len(validation) == len(original)`，且兩者無重疊列。

**Property 4: Datetime 提取後無原始 Datetime 欄位**
對任意包含 datetime 欄位的 DataFrame，執行 `extract_datetime_features()` 後，原始 datetime 欄位不應存在，且應新增對應的 `_hour`, `_day`, `_weekday`, `_month` 欄位。

**Property 5: ID-like 欄位移除後不存在**
對任意 DataFrame，執行 `remove_id_fields()` 後，所有被識別為 ID-like 的欄位（且不在 keep_fields 中）不應存在於輸出中。

**Property 6: Scaling 後均值接近 0、標準差接近 1**
對任意數值欄位執行 `scale()` 後，該欄位的均值應接近 0（|mean| < 1e-10），標準差應接近 1（|std - 1| < 1e-10）。

**Property 7: 輸出列數一致性**
`processed_{timestamp}.csv` 的列數應等於 `train.csv` 列數加上 `validation.csv` 列數。

**Property 8: JSON 輸出可重新載入**
所有輸出的 JSON 檔案（encoding_map, scaler_params, preprocessing_rules, metadata）應可被 `json.load()` 成功解析，且結構與寫入時一致。

---

## Error Handling Strategy

- **讀取失敗**：raise `PipelineReadError`，終止處理
- **輸出目錄無權限**：raise `PipelineWriteError`，終止處理
- **單一欄位處理失敗**：記錄錯誤，跳過該欄位，繼續
- **單一資料列處理失敗**：記錄錯誤，跳過該列，繼續
- **所有其他例外**：捕捉、記錄、繼續（確保 pipeline 不中斷）
