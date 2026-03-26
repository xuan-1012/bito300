# Utility Modules

This directory contains utility modules for the Crypto Suspicious Account Detection system.

## BitoPro API Client

The `bitopro_client.py` module provides a client for interacting with the BitoPro cryptocurrency exchange API.

### Features

- **Authentication**: Retrieves API credentials from AWS Secrets Manager
- **Retry Logic**: Implements exponential backoff retry (up to 3 attempts)
- **Error Handling**: Handles common API errors (timeout, rate limiting, authentication failures)
- **Time Range Filtering**: Fetches transactions within specified time ranges

### Usage Example

```python
from datetime import datetime, timedelta
from src.common.aws_clients import get_aws_clients
from src.utils.bitopro_client import BitoproClient

# Initialize AWS clients
aws_clients = get_aws_clients()

# Create BitoPro client (retrieves credentials from Secrets Manager)
client = BitoproClient(
    aws_clients=aws_clients,
    secret_id='bitopro-api-key',
    max_retries=3
)

# Fetch transactions for the last 24 hours
end_time = datetime.now()
start_time = end_time - timedelta(days=1)

transactions = client.fetch_transactions(
    start_time=start_time,
    end_time=end_time,
    limit=1000
)

print(f"Fetched {len(transactions)} transactions")
for txn in transactions[:5]:
    print(f"  - {txn['id']}: {txn['amount']} {txn['currency']}")
```

### Error Handling

The client handles various error scenarios:

- **Timeout**: Retries with exponential backoff
- **Rate Limiting (429)**: Raises `BitoproClientError` with retry-after information
- **Authentication (401)**: Raises `BitoproClientError` immediately (no retry)
- **API Errors**: Retries up to max_retries, then raises `BitoproClientError`

### Configuration

The client can be configured with the following parameters:

- `secret_id`: Secrets Manager secret ID (default: "bitopro-api-key")
- `base_url`: BitoPro API base URL (default: "https://api.bitopro.com/v3")
- `timeout`: Request timeout in seconds (default: 30)
- `max_retries`: Maximum retry attempts (default: 3)

### Secrets Manager Format

The API credentials in Secrets Manager should be stored as JSON:

```json
{
  "api_key": "your_api_key_here",
  "api_secret": "your_api_secret_here"
}
```

### Requirements Validation

This module validates the following requirements:

- **Requirement 1.1**: Retrieve BitoPro API key from Secrets Manager
- **Requirement 1.2**: Request transactions within specified time range
- **Requirement 1.5**: Retry with exponential backoff up to 3 attempts
- **Requirement 11.1**: Handle API errors with retry logic
