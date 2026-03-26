# Component Wiring Documentation

## Overview

This document describes how all components of the Crypto Suspicious Account Detection system are wired together, including data flow, communication patterns, and integration points.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AWS Step Functions                                  │
│                     (Orchestration & Workflow Control)                       │
│                                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐    │
│  │   Data     │───▶│  Feature   │───▶│    Risk    │───▶│   Report   │    │
│  │  Fetcher   │    │ Extractor  │    │  Analyzer  │    │ Generator  │    │
│  └────────────┘    └────────────┘    └────────────┘    └────────────┘    │
│        │                  │                  │                  │           │
└────────┼──────────────────┼──────────────────┼──────────────────┼───────────┘
         │                  │                  │                  │
         ▼                  ▼                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Storage Layer                                     │
│                                                                              │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐      ┌──────────┐       │
│  │   Raw    │      │ Features │      │   Risk   │      │ Reports  │       │
│  │   Data   │      │   Data   │      │  Scores  │      │  & Charts│       │
│  │   (S3)   │      │   (S3)   │      │   (S3)   │      │   (S3)   │       │
│  └──────────┘      └──────────┘      └──────────┘      └──────────┘       │
│                                                                              │
│                          ┌──────────────────┐                               │
│                          │   DynamoDB       │                               │
│                          │  Risk Profiles   │                               │
│                          └──────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
         ▲                                      ▲
         │                                      │
┌────────┴────────┐                    ┌───────┴────────┐
│ Secrets Manager │                    │  AWS Bedrock   │
│  (API Keys)     │                    │  (Claude 3)    │
└─────────────────┘                    └────────────────┘
```

## Data Flow

### 1. Data Fetcher → Feature Extractor

**Communication Method:** S3 (Asynchronous)

**Data Format:** JSON

**Flow:**
1. Data Fetcher fetches transactions from BitoPro API
2. Data Fetcher stores raw transactions to S3 (`RawDataBucket`)
3. Data Fetcher returns S3 URI in Step Functions output
4. Step Functions passes S3 URI to Feature Extractor
5. Feature Extractor reads raw data from S3

**Output Schema (Data Fetcher):**
```json
{
  "raw_data_s3_uri": "s3://bucket/raw-data/YYYY-MM-DD/transactions.json",
  "transaction_count": 1000,
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "fetch_timestamp": "2024-01-31T23:59:59Z"
}
```

**Input Schema (Feature Extractor):**
```json
{
  "dataFetcherResult": {
    "raw_data_s3_uri": "s3://bucket/raw-data/YYYY-MM-DD/transactions.json",
    "transaction_count": 1000
  }
}
```

**S3 Object Structure (Raw Data):**
```json
{
  "transactions": [
    {
      "transaction_id": "tx_123",
      "account_id": "acc_456",
      "amount": 1000.50,
      "currency": "BTC",
      "timestamp": "2024-01-01T12:00:00Z",
      "counterparty": "acc_789",
      "transaction_type": "transfer"
    }
  ],
  "metadata": {
    "fetch_time": "2024-01-31T23:59:59Z",
    "total_count": 1000
  }
}
```

### 2. Feature Extractor → Risk Analyzer

**Communication Method:** S3 (Asynchronous)

**Data Format:** JSON

**Flow:**
1. Feature Extractor reads raw data from S3
2. Feature Extractor extracts risk features for each account
3. Feature Extractor stores features to S3 (`FeaturesBucket`)
4. Feature Extractor returns S3 URI in Step Functions output
5. Step Functions passes S3 URI to Risk Analyzer
6. Risk Analyzer reads features from S3

**Output Schema (Feature Extractor):**
```json
{
  "features_s3_uri": "s3://bucket/features/YYYY-MM-DD/features.json",
  "account_count": 100,
  "feature_names": [
    "total_volume",
    "transaction_count",
    "avg_transaction_size",
    "max_transaction_size",
    "unique_counterparties",
    "night_transaction_ratio",
    "round_number_ratio",
    "rapid_transaction_count",
    "concentration_score",
    "velocity_score"
  ],
  "extraction_timestamp": "2024-01-31T23:59:59Z"
}
```

**Input Schema (Risk Analyzer):**
```json
{
  "featureExtractorResult": {
    "features_s3_uri": "s3://bucket/features/YYYY-MM-DD/features.json",
    "account_count": 100
  }
}
```

**S3 Object Structure (Features):**
```json
{
  "features": [
    {
      "account_id": "acc_456",
      "total_volume": 50000.0,
      "transaction_count": 50,
      "avg_transaction_size": 1000.0,
      "max_transaction_size": 5000.0,
      "unique_counterparties": 10,
      "night_transaction_ratio": 0.2,
      "round_number_ratio": 0.3,
      "rapid_transaction_count": 5,
      "concentration_score": 0.4,
      "velocity_score": 0.6
    }
  ],
  "metadata": {
    "extraction_time": "2024-01-31T23:59:59Z",
    "total_accounts": 100
  }
}
```

### 3. Risk Analyzer → Report Generator

**Communication Method:** S3 + DynamoDB (Hybrid)

**Data Format:** JSON (S3), Items (DynamoDB)

**Flow:**
1. Risk Analyzer reads features from S3
2. Risk Analyzer analyzes risk using AWS Bedrock (with rate limiting)
3. Risk Analyzer stores risk assessments to S3 (`RiskScoresBucket`)
4. Risk Analyzer stores risk assessments to DynamoDB (`RiskProfilesTable`)
5. Risk Analyzer returns S3 URI in Step Functions output
6. Step Functions passes S3 URI to Report Generator
7. Report Generator reads risk assessments from S3 and DynamoDB

**Output Schema (Risk Analyzer):**
```json
{
  "risk_scores_s3_uri": "s3://bucket/risk-scores/YYYY-MM-DD/assessments.json",
  "assessed_accounts": 100,
  "bedrock_api_calls": 95,
  "fallback_assessments": 5,
  "average_risk_score": 35.5,
  "high_risk_accounts": 15,
  "analysis_timestamp": "2024-01-31T23:59:59Z"
}
```

**Input Schema (Report Generator):**
```json
{
  "riskAnalyzerResult": {
    "risk_scores_s3_uri": "s3://bucket/risk-scores/YYYY-MM-DD/assessments.json",
    "assessed_accounts": 100
  }
}
```

**S3 Object Structure (Risk Assessments):**
```json
{
  "assessments": [
    {
      "account_id": "acc_456",
      "risk_score": 75,
      "risk_level": "HIGH",
      "risk_factors": [
        "High night transaction ratio",
        "Unusual concentration score"
      ],
      "explanation": "Account shows suspicious patterns...",
      "confidence": 0.85,
      "assessment_method": "bedrock",
      "timestamp": "2024-01-31T23:59:59Z"
    }
  ],
  "metadata": {
    "analysis_time": "2024-01-31T23:59:59Z",
    "total_assessments": 100,
    "bedrock_calls": 95,
    "fallback_calls": 5
  }
}
```

**DynamoDB Item Structure:**
```json
{
  "account_id": "acc_456",
  "timestamp": 1706745599,
  "risk_score": 75,
  "risk_level": "HIGH",
  "risk_factors": ["High night transaction ratio", "Unusual concentration score"],
  "explanation": "Account shows suspicious patterns...",
  "confidence": 0.85,
  "assessment_method": "bedrock",
  "features": {
    "total_volume": 50000.0,
    "transaction_count": 50,
    "night_transaction_ratio": 0.2
  }
}
```

### 4. Report Generator → Final Output

**Communication Method:** S3 (Asynchronous)

**Data Format:** HTML, PNG, JSON

**Flow:**
1. Report Generator reads risk assessments from S3 and DynamoDB
2. Report Generator generates summary statistics
3. Report Generator creates visualizations (charts)
4. Report Generator generates HTML presentation
5. Report Generator stores all outputs to S3 (`ReportsBucket`)
6. Report Generator generates pre-signed URL for report access
7. Report Generator returns report URI and pre-signed URL

**Output Schema (Report Generator):**
```json
{
  "report_s3_uri": "s3://bucket/reports/YYYY-MM-DD/report.html",
  "charts_s3_uris": [
    "s3://bucket/reports/YYYY-MM-DD/risk_distribution.png",
    "s3://bucket/reports/YYYY-MM-DD/risk_histogram.png"
  ],
  "presigned_url": "https://bucket.s3.amazonaws.com/reports/...",
  "presigned_url_expiry": "2024-02-01T23:59:59Z",
  "summary": {
    "total_accounts": 100,
    "total_transactions": 1000,
    "risk_distribution": {
      "LOW": 60,
      "MEDIUM": 25,
      "HIGH": 10,
      "CRITICAL": 5
    },
    "average_risk_score": 35.5,
    "top_suspicious_accounts": [
      {
        "account_id": "acc_456",
        "risk_score": 95,
        "risk_level": "CRITICAL"
      }
    ]
  },
  "generation_timestamp": "2024-01-31T23:59:59Z"
}
```

## Component Integration Points

### Data Fetcher Integration

**Dependencies:**
- AWS Secrets Manager (BitoPro API credentials)
- S3 (Raw data storage)
- CloudWatch Logs (Logging)

**Environment Variables:**
```python
RAW_DATA_BUCKET = os.environ["RAW_DATA_BUCKET"]
BITOPRO_SECRET_NAME = os.environ["BITOPRO_SECRET_NAME"]
```

**Code Integration:**
```python
# src/lambdas/data_fetcher/handler.py

from src.utils.bitopro_client import BitoproClient
from src.common.aws_clients import get_secrets_manager_client, get_s3_client

def lambda_handler(event, context):
    # Get API credentials from Secrets Manager
    secrets_client = get_secrets_manager_client()
    api_key = secrets_client.get_secret_value(
        SecretId=os.environ["BITOPRO_SECRET_NAME"]
    )
    
    # Fetch transactions
    bitopro_client = BitoproClient(api_key)
    transactions = bitopro_client.fetch_transactions(
        start_time=event["time_range"]["start"],
        end_time=event["time_range"]["end"]
    )
    
    # Store to S3
    s3_client = get_s3_client()
    s3_uri = store_to_s3(s3_client, transactions)
    
    return {
        "raw_data_s3_uri": s3_uri,
        "transaction_count": len(transactions)
    }
```

### Feature Extractor Integration

**Dependencies:**
- S3 (Read raw data, write features)
- CloudWatch Logs (Logging)

**Environment Variables:**
```python
RAW_DATA_BUCKET = os.environ["RAW_DATA_BUCKET"]
FEATURES_BUCKET = os.environ["FEATURES_BUCKET"]
```

**Code Integration:**
```python
# src/lambdas/feature_extractor/handler.py

from src.common.aws_clients import get_s3_client

def lambda_handler(event, context):
    # Get S3 URI from previous step
    raw_data_uri = event["dataFetcherResult"]["raw_data_s3_uri"]
    
    # Read raw data from S3
    s3_client = get_s3_client()
    transactions = read_from_s3(s3_client, raw_data_uri)
    
    # Extract features
    features = extract_features(transactions)
    
    # Store features to S3
    features_uri = store_to_s3(s3_client, features)
    
    return {
        "features_s3_uri": features_uri,
        "account_count": len(features)
    }
```

### Risk Analyzer Integration

**Dependencies:**
- S3 (Read features, write risk scores)
- DynamoDB (Write risk profiles)
- AWS Bedrock (Risk analysis)
- CloudWatch Logs (Logging)

**Environment Variables:**
```python
FEATURES_BUCKET = os.environ["FEATURES_BUCKET"]
RISK_SCORES_BUCKET = os.environ["RISK_SCORES_BUCKET"]
RISK_PROFILES_TABLE = os.environ["RISK_PROFILES_TABLE"]
```

**Code Integration:**
```python
# src/lambdas/risk_analyzer/handler.py

from src.common.aws_clients import get_s3_client, get_dynamodb_client, get_bedrock_client
from src.common.rate_limiter import RateLimiter

def lambda_handler(event, context):
    # Get S3 URI from previous step
    features_uri = event["featureExtractorResult"]["features_s3_uri"]
    
    # Read features from S3
    s3_client = get_s3_client()
    features = read_from_s3(s3_client, features_uri)
    
    # Initialize rate limiter for Bedrock
    rate_limiter = RateLimiter(max_requests_per_second=0.9)
    
    # Analyze risk for each account
    bedrock_client = get_bedrock_client()
    assessments = []
    
    for account_features in features:
        rate_limiter.wait_if_needed()
        assessment = analyze_risk_with_bedrock(bedrock_client, account_features)
        assessments.append(assessment)
    
    # Store to S3
    risk_scores_uri = store_to_s3(s3_client, assessments)
    
    # Store to DynamoDB
    dynamodb_client = get_dynamodb_client()
    store_to_dynamodb(dynamodb_client, assessments)
    
    return {
        "risk_scores_s3_uri": risk_scores_uri,
        "assessed_accounts": len(assessments)
    }
```

### Report Generator Integration

**Dependencies:**
- S3 (Read risk scores, write reports)
- DynamoDB (Read risk profiles)
- CloudWatch Logs (Logging)

**Environment Variables:**
```python
RISK_SCORES_BUCKET = os.environ["RISK_SCORES_BUCKET"]
REPORTS_BUCKET = os.environ["REPORTS_BUCKET"]
RISK_PROFILES_TABLE = os.environ["RISK_PROFILES_TABLE"]
```

**Code Integration:**
```python
# src/lambdas/report_generator/handler.py

from src.common.aws_clients import get_s3_client, get_dynamodb_client

def lambda_handler(event, context):
    # Get S3 URI from previous step
    risk_scores_uri = event["riskAnalyzerResult"]["risk_scores_s3_uri"]
    
    # Read risk scores from S3
    s3_client = get_s3_client()
    assessments = read_from_s3(s3_client, risk_scores_uri)
    
    # Generate summary statistics
    summary = generate_summary(assessments)
    
    # Generate charts
    charts = generate_charts(assessments)
    
    # Generate HTML presentation
    html_report = generate_html_presentation(summary, charts, assessments)
    
    # Store to S3
    report_uri = store_to_s3(s3_client, html_report)
    
    # Generate pre-signed URL
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': os.environ["REPORTS_BUCKET"], 'Key': report_key},
        ExpiresIn=86400  # 24 hours
    )
    
    return {
        "report_s3_uri": report_uri,
        "presigned_url": presigned_url,
        "summary": summary
    }
```

## Step Functions Orchestration

### State Machine Configuration

**Definition File:** `infrastructure/state_machine.json`

**State Transitions:**
```
DataFetcher → FeatureExtractor → RiskAnalyzer → ReportGenerator → SuccessState
     ↓              ↓                  ↓                ↓
  FailState      FailState          FailState       FailState
```

**Data Passing:**
- Each state stores its output in a separate path (e.g., `$.dataFetcherResult`)
- Subsequent states access previous outputs via input path
- Error information stored in `$.error` path

**Example Execution Input:**
```json
{
  "time_range": {
    "start": "2024-01-01T00:00:00Z",
    "end": "2024-01-31T23:59:59Z"
  },
  "account_ids": ["acc_1", "acc_2"]
}
```

**Example Execution Output:**
```json
{
  "time_range": {...},
  "account_ids": [...],
  "dataFetcherResult": {
    "raw_data_s3_uri": "s3://...",
    "transaction_count": 1000
  },
  "featureExtractorResult": {
    "features_s3_uri": "s3://...",
    "account_count": 100
  },
  "riskAnalyzerResult": {
    "risk_scores_s3_uri": "s3://...",
    "assessed_accounts": 100
  },
  "reportGeneratorResult": {
    "report_s3_uri": "s3://...",
    "presigned_url": "https://...",
    "summary": {...}
  }
}
```

## Error Handling and Retry Logic

### Retry Configuration

Each Lambda function has retry logic:
- **Max Attempts:** 3 (DataFetcher, FeatureExtractor, ReportGenerator), 2 (RiskAnalyzer)
- **Backoff Rate:** 2.0 (exponential)
- **Interval:** 2-5 seconds

### Error Propagation

1. Lambda function throws exception
2. Step Functions catches error
3. Step Functions retries with exponential backoff
4. If all retries exhausted, transition to FailState
5. Error details stored in `$.error` path

### Fallback Mechanisms

**Risk Analyzer Fallback:**
- If Bedrock API fails, use rule-based scoring
- Mark assessment with lower confidence
- Continue processing remaining accounts

## Monitoring and Logging

### CloudWatch Logs

Each component logs to its own log group:
- `/aws/lambda/crypto-suspicious-detection-data-fetcher`
- `/aws/lambda/crypto-suspicious-detection-feature-extractor`
- `/aws/lambda/crypto-suspicious-detection-risk-analyzer`
- `/aws/lambda/crypto-suspicious-detection-report-generator`
- `/aws/states/crypto-suspicious-detection-workflow`

### Log Format

```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info(f"Processing {len(transactions)} transactions")
logger.error(f"Failed to fetch data: {error}")
```

### Metrics

Track the following metrics:
- Transaction count
- Feature extraction time
- Bedrock API call count
- Fallback assessment count
- Report generation time

## Testing Integration

### Unit Tests

Test each component in isolation with mocked dependencies:
```python
@mock_aws
def test_data_fetcher():
    # Mock S3 and Secrets Manager
    # Test data fetcher logic
    pass
```

### Integration Tests

Test component interactions:
```python
def test_data_flow():
    # Test DataFetcher → FeatureExtractor flow
    # Verify S3 data format
    # Verify data consistency
    pass
```

### End-to-End Tests

Test complete workflow:
```python
def test_complete_workflow():
    # Start Step Functions execution
    # Wait for completion
    # Verify final report
    pass
```

## Deployment Checklist

- [ ] Deploy SAM template
- [ ] Update BitoPro API credentials in Secrets Manager
- [ ] Enable Bedrock model access
- [ ] Verify S3 buckets are private
- [ ] Verify DynamoDB table encryption
- [ ] Test Step Functions execution
- [ ] Verify CloudWatch logs
- [ ] Generate test report

## Troubleshooting

### Issue: Data Fetcher fails

**Check:**
1. BitoPro API credentials in Secrets Manager
2. S3 bucket permissions
3. CloudWatch logs for error details

### Issue: Risk Analyzer times out

**Check:**
1. Bedrock rate limiting (< 1 req/sec)
2. Number of accounts being processed
3. Increase timeout in SAM template

### Issue: Report Generator fails

**Check:**
1. S3 read permissions for risk scores
2. DynamoDB query permissions
3. matplotlib dependencies installed

## Conclusion

All components are properly wired together with:
- ✅ Clear data flow paths
- ✅ Proper error handling
- ✅ Rate limiting for Bedrock
- ✅ Comprehensive logging
- ✅ Retry mechanisms
- ✅ Fallback strategies

The system is ready for deployment and testing.
