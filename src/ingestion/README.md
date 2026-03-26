# BitoPro API Data Ingestion Layer

A fault-tolerant pipeline for fetching, storing, and processing data from the
BitoPro exchange API.  The package exposes five main components that can be
used individually or wired together through the `ingest_bitopro_data()`
orchestration function.

## Directory Structure

```
src/ingestion/
├── __init__.py          # Package exports
├── models.py            # Core data models, enums, and configurations
├── client.py            # BitoProAPIClient – HTTP client with retry & rate-limiting
├── storage.py           # RawDataStorage, S3Storage, LocalStorage
├── flattener.py         # JSONFlattener – nested JSON → flat dicts
├── inferencer.py        # SchemaInferencer – automatic type detection
├── fallback.py          # FallbackManager – graceful error handling
├── credentials.py       # get_bitopro_credentials – AWS Secrets Manager helper
├── logging_config.py    # SensitiveDataFilter – redacts secrets from logs
└── workflow.py          # ingest_bitopro_data() – end-to-end orchestration
```

---

## Quick Start

### 1. Basic Data Ingestion

The simplest way to ingest data is to call `ingest_bitopro_data()` directly.
It handles everything: fetching, storing, flattening, and schema inference.

```python
from src.ingestion import ingest_bitopro_data, HTTPMethod

storage_uri, schema_path = ingest_bitopro_data(
    endpoint="/v3/order-book/BTC_USDT",
    method=HTTPMethod.GET,
    storage_backend="local",   # write raw JSON to disk
    local_path="raw_data/",
    schema_output_path="schema.json",
)

print(f"Raw data stored at : {storage_uri}")
print(f"Schema written to  : {schema_path}")
```

---

### 2. Complete Workflow Example

For authenticated endpoints, pass credentials directly or retrieve them from
AWS Secrets Manager first (see section 5).

```python
from src.ingestion import ingest_bitopro_data, HTTPMethod, get_bitopro_credentials

# Retrieve credentials from AWS Secrets Manager
api_key, api_secret = get_bitopro_credentials("prod/bitopro/api-credentials")

# Run the full ingestion pipeline
storage_uri, schema_path = ingest_bitopro_data(
    endpoint="/v3/trading-history/BTC_USDT",
    method=HTTPMethod.GET,
    params={"limit": 1000},
    storage_backend="s3",
    s3_bucket="my-crypto-raw-data",
    api_key=api_key,
    api_secret=api_secret,
    schema_output_path="schemas/trading_history.json",
)

if storage_uri:
    print(f"Ingestion succeeded: {storage_uri}")
else:
    print("Ingestion failed – check logs for details")
```

The pipeline executes these steps automatically:

1. Initialise `BitoProAPIClient`, `RawDataStorage`, `JSONFlattener`,
   `SchemaInferencer`, and `FallbackManager`.
2. Fetch all pages from the endpoint (automatic pagination).
3. Store each raw response to S3 (or local disk) without modification.
4. Flatten every nested JSON structure into flat dictionaries.
5. Infer a schema from the flattened records.
6. Export the schema to a JSON file.
7. Return `(storage_uri, schema_path)`.

---

### 3. Nested JSON Handling

`JSONFlattener` converts arbitrarily nested structures into flat dictionaries
using a configurable key separator.

```python
from src.ingestion import JSONFlattener

flattener = JSONFlattener(
    separator="_",      # key separator (default)
    max_depth=10,       # stop recursing beyond this depth
    handle_lists="explode",  # "explode" | "index" | "json_string"
)

# Nested API response
raw = {
    "order": {
        "id": "ORD-001",
        "pair": "BTC_USDT",
        "price": {"amount": 45000.0, "currency": "USDT"},
    },
    "fills": [
        {"qty": 0.5, "fee": 0.001},
        {"qty": 0.3, "fee": 0.0006},
    ],
}

records = flattener.flatten(raw)
# With handle_lists="explode" each fill becomes a separate record:
# [
#   {"order_id": "ORD-001", "order_pair": "BTC_USDT",
#    "order_price_amount": 45000.0, "order_price_currency": "USDT",
#    "fills_qty": 0.5, "fills_fee": 0.001},
#   {"order_id": "ORD-001", "order_pair": "BTC_USDT",
#    "order_price_amount": 45000.0, "order_price_currency": "USDT",
#    "fills_qty": 0.3, "fills_fee": 0.0006},
# ]

# Lists of primitives are serialised as JSON strings (Req 6.4)
raw2 = {"tags": ["crypto", "spot", "BTC"]}
records2 = flattener.flatten(raw2)
# [{"tags": '["crypto", "spot", "BTC"]'}]
```

**List strategies**

| Strategy | Behaviour |
|---|---|
| `"explode"` (default) | Each dict in a list becomes a separate output record |
| `"index"` | List items are merged into one record with indexed keys (`field_0`, `field_1`, …) |
| `"json_string"` | The entire list is serialised as a JSON string |

---

### 4. Error Handling with FallbackManager

`FallbackManager` wraps any callable and ensures the pipeline never crashes.

```python
import logging
from src.ingestion import FallbackManager

logger = logging.getLogger(__name__)
fallback = FallbackManager(logger=logger)

# --- with_fallback: primary → fallback → default ---
result = fallback.with_fallback(
    primary_func=lambda: risky_operation(),
    fallback_func=lambda: safe_alternative(),
    default_value=[],
)

# --- handle_missing_field: returns default when key absent ---
record = {"price": 45000.0}
volume = fallback.handle_missing_field(record, "volume", default=0.0)
# volume == 0.0  (field missing → warning logged)

# --- handle_type_mismatch: coerces or returns default ---
price = fallback.handle_type_mismatch("45000.5", expected_type=float, default=0.0)
# price == 45000.5

bad = fallback.handle_type_mismatch("not-a-number", expected_type=int, default=-1)
# bad == -1  (conversion failed → error logged)
```

`FallbackManager` is used internally by `ingest_bitopro_data()` to wrap every
pipeline step, so a failure in one step (e.g. a storage write) does not abort
the entire run.

---

### 5. Credential Retrieval

`get_bitopro_credentials()` fetches API credentials from AWS Secrets Manager
and caches them in-process for 5 minutes to avoid repeated network calls.

```python
from src.ingestion import get_bitopro_credentials

api_key, api_secret = get_bitopro_credentials(
    secret_name="prod/bitopro/api-credentials",
    ttl_seconds=300,   # cache TTL (default: 5 minutes)
)

if api_key is None:
    print("Could not retrieve credentials – running unauthenticated")
```

The secret stored in AWS Secrets Manager must be a JSON object with either
`api_key` / `api_secret` or `apiKey` / `apiSecret` fields:

```json
{
  "api_key": "your-bitopro-api-key",
  "api_secret": "your-bitopro-api-secret"
}
```

---

### 6. Schema Inference Output

`SchemaInferencer` analyses flattened records and produces a `FieldSchema` for
every field, then exports the result to JSON.

```python
from src.ingestion import SchemaInferencer

inferencer = SchemaInferencer(
    sample_size=100,          # max values examined per field
    confidence_threshold=0.8, # threshold for downstream consumers
)

records = [
    {"order_id": "ORD-001", "price": 45000.0, "created_at": "2024-01-15T10:30:00"},
    {"order_id": "ORD-002", "price": 46500.5, "created_at": "2024-01-15T11:00:00"},
    {"order_id": "ORD-003", "price": None,     "created_at": "2024-01-15T11:30:00"},
]

schema = inferencer.infer_schema(records)
schema_path = inferencer.export_schema(schema, output_path="schema.json")
```

The exported `schema.json` looks like:

```json
{
  "order_id": {
    "name": "order_id",
    "inferred_type": "id_like",
    "nullable": false,
    "sample_values": ["ORD-001", "ORD-002", "ORD-003"],
    "null_count": 0,
    "total_count": 3,
    "confidence": 1.0
  },
  "price": {
    "name": "price",
    "inferred_type": "numeric",
    "nullable": true,
    "sample_values": [45000.0, 46500.5],
    "null_count": 1,
    "total_count": 3,
    "confidence": 1.0
  },
  "created_at": {
    "name": "created_at",
    "inferred_type": "datetime",
    "nullable": false,
    "sample_values": ["2024-01-15T10:30:00", "2024-01-15T11:00:00", "2024-01-15T11:30:00"],
    "null_count": 0,
    "total_count": 3,
    "confidence": 1.0
  }
}
```

**Supported field types**

| Type | Detection rule |
|---|---|
| `numeric` | `int`, `float`, or string parseable as `float` |
| `datetime` | ISO 8601, `YYYY-MM-DD`, `MM/DD/YYYY`, Unix timestamp (10 or 13 digits) |
| `id_like` | UUID, hex hash (≥ 32 chars), alphanumeric code (`AB1234`), or numeric field with ID keyword in name |
| `boolean` | Python `bool` values |
| `text` | Any string not matching the above patterns |
| `mixed` | Dominant type confidence < 60 % |
| `null` | All sampled values are `None` |

---

### 7. Sensitive Data Filtering

Attach `SensitiveDataFilter` to any logger to automatically redact API keys,
secrets, and tokens from log output.

```python
import logging
from src.ingestion import SensitiveDataFilter, configure_sensitive_logging

# Option A: attach to a specific logger
logger = logging.getLogger("src.ingestion")
logger.addFilter(SensitiveDataFilter())

# Option B: helper that attaches the filter and returns the logger
ingestion_logger = configure_sensitive_logging("src.ingestion")

# Any log message containing credentials is automatically sanitised:
ingestion_logger.info("api_key=supersecret123 connected")
# → logs: "api_key=[REDACTED] connected"
```

---

## Component Reference

| Class / Function | Module | Description |
|---|---|---|
| `BitoProAPIClient` | `client` | HTTP client with auth, retry, rate-limiting, pagination |
| `RawDataStorage` | `storage` | Stores raw responses via a pluggable backend |
| `S3Storage` | `storage` | AWS S3 backend (AES-256 server-side encryption) |
| `LocalStorage` | `storage` | Local filesystem backend |
| `StorageBackend` | `storage` | Abstract base class for custom backends |
| `JSONFlattener` | `flattener` | Flattens nested JSON into flat dicts |
| `SchemaInferencer` | `inferencer` | Infers field types from flattened records |
| `FallbackManager` | `fallback` | Graceful error handling and fallback execution |
| `ingest_bitopro_data` | `workflow` | End-to-end orchestration function |
| `get_bitopro_credentials` | `credentials` | AWS Secrets Manager credential retrieval |
| `SensitiveDataFilter` | `logging_config` | Logging filter that redacts sensitive values |
| `configure_sensitive_logging` | `logging_config` | Attaches `SensitiveDataFilter` to a logger |

### Data Models

| Model | Description |
|---|---|
| `HTTPMethod` | Enum: `GET`, `POST` |
| `FieldType` | Enum: `numeric`, `categorical`, `datetime`, `text`, `id_like`, `boolean`, `null`, `mixed` |
| `APIConfig` | Client configuration (base URL, timeout, retries, rate limit) |
| `APIRequest` | Validated API request descriptor |
| `APIResponse` | Validated API response descriptor |
| `FlattenedRecord` | Flat (depth-1) data record with provenance metadata |
| `FieldSchema` | Per-field schema with type, nullability, samples, and confidence |

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Unit tests only
python -m pytest tests/unit/ -v

# Property-based tests (Hypothesis)
python -m pytest tests/property/ -v

# Integration tests
python -m pytest tests/integration/ -v
```
