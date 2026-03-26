# Requirements Document: Crypto Suspicious Account Detection

## Introduction

本系統為黑客松設計的加密貨幣可疑帳號偵測與風控分析 MVP 系統，目標在 4 小時內完成可展示、可解釋、可落地的端到端解決方案。系統串接 BitoPro API 獲取交易資料，使用 AWS Bedrock 的基礎模型進行風險分析，產出風險評分、可疑帳號清單、解釋原因，以及完整的圖表與提案簡報素材。

核心價值主張：
- 快速部署：使用 AWS 無伺服器架構，無需管理基礎設施
- AI 驅動：利用 Bedrock 的 LLM 進行智能風險評估與解釋
- 合規優先：嚴格遵守比賽規範，所有資源皆為私有且安全
- 可視化：自動產生圖表與簡報素材，便於展示與決策

## Glossary

- **System**: 加密貨幣可疑帳號偵測系統
- **BitoPro_API**: BitoPro 加密貨幣交易所提供的 REST API
- **Transaction**: 加密貨幣交易記錄，包含發送方、接收方、金額、時間戳等資訊
- **Account**: 加密貨幣交易帳號，由唯一識別碼標識
- **Risk_Score**: 風險評分，範圍 0-100，數值越高表示風險越大
- **Risk_Level**: 風險等級，分為 LOW (0-25)、MEDIUM (26-50)、HIGH (51-75)、CRITICAL (76-100)
- **Feature**: 從交易資料中提取的統計特徵，用於風險評估
- **Bedrock**: Amazon Bedrock AI 服務，提供基礎語言模型進行風險分析
- **Data_Fetcher**: 負責從 BitoPro API 獲取交易資料的 Lambda 函數
- **Feature_Extractor**: 負責從原始交易資料中提取風險特徵的 Lambda 函數
- **Risk_Analyzer**: 負責使用 Bedrock 進行風險評估的 Lambda 函數
- **Report_Generator**: 負責產生視覺化報告和簡報素材的 Lambda 函數
- **S3_Bucket**: AWS S3 儲存桶，用於存放交易資料、特徵、風險評分和報告
- **DynamoDB_Table**: AWS DynamoDB 資料表，用於存放帳號風險檔案
- **Step_Functions**: AWS Step Functions 狀態機，用於協調整個分析流程
- **Rate_Limiter**: 速率限制器，確保 Bedrock API 呼叫頻率 < 1 次/秒
- **Secrets_Manager**: AWS Secrets Manager，用於安全存放 API 金鑰

## Requirements

### Requirement 1: Data Ingestion from BitoPro API

**User Story:** As a fraud detection analyst, I want to fetch transaction data from BitoPro API, so that I can analyze cryptocurrency transactions for suspicious patterns.

#### Acceptance Criteria

1. WHEN the Data_Fetcher is invoked with a time range, THE System SHALL retrieve the BitoPro API key from Secrets_Manager
2. WHEN the Data_Fetcher calls the BitoPro_API, THE System SHALL request transactions within the specified time range
3. WHEN the BitoPro_API returns transaction data, THE System SHALL validate each Transaction for required fields and data types
4. WHEN transaction data is validated, THE System SHALL store the raw data to a private S3_Bucket in JSON format
5. IF the BitoPro_API returns an error or times out, THEN THE System SHALL retry with exponential backoff up to 3 attempts
6. WHEN the Data_Fetcher completes, THE System SHALL log the operation details to CloudWatch without including sensitive information

### Requirement 2: Transaction Data Validation

**User Story:** As a system administrator, I want all transaction data to be validated, so that downstream processing operates on clean and consistent data.

#### Acceptance Criteria

1. THE System SHALL validate that each Transaction has a non-empty transaction_id
2. THE System SHALL validate that each Transaction has a valid timestamp
3. THE System SHALL validate that each Transaction has a positive amount value
4. THE System SHALL validate that each Transaction has valid from_account and to_account identifiers
5. THE System SHALL validate that each Transaction has a valid currency code
6. IF a Transaction fails validation, THEN THE System SHALL log the validation error and exclude the Transaction from further processing
7. WHEN validation completes, THE System SHALL include data quality metrics in the processing metadata

### Requirement 3: Feature Extraction from Transactions

**User Story:** As a fraud detection analyst, I want to extract risk-related features from transaction data, so that I can identify suspicious patterns and behaviors.

#### Acceptance Criteria

1. WHEN the Feature_Extractor receives raw transaction data, THE System SHALL group transactions by Account
2. WHEN transactions are grouped by Account, THE System SHALL calculate total_volume as the sum of all transaction amounts
3. WHEN transactions are grouped by Account, THE System SHALL calculate transaction_count as the number of transactions
4. WHEN transactions are grouped by Account, THE System SHALL calculate avg_transaction_size and max_transaction_size
5. WHEN transactions are grouped by Account, THE System SHALL identify unique_counterparties
6. WHEN transactions are grouped by Account, THE System SHALL calculate night_transaction_ratio as the proportion of transactions occurring between 00:00 and 06:00
7. WHEN transactions are grouped by Account, THE System SHALL calculate round_number_ratio as the proportion of transactions with round number amounts
8. WHEN transactions are grouped by Account, THE System SHALL calculate rapid_transaction_count as the number of transactions occurring within 5 minutes of each other
9. WHEN transactions are grouped by Account, THE System SHALL calculate concentration_score using the Herfindahl index for counterparty distribution
10. WHEN transactions are grouped by Account, THE System SHALL calculate velocity_score as the transaction frequency per hour
11. WHEN feature extraction completes, THE System SHALL store the extracted features to S3_Bucket

### Requirement 4: AI-Driven Risk Assessment

**User Story:** As a fraud detection analyst, I want AI-powered risk assessment with explanations, so that I can understand why an account is flagged as suspicious.

#### Acceptance Criteria

1. WHEN the Risk_Analyzer receives extracted features, THE System SHALL construct a prompt for Bedrock including all feature values
2. WHEN calling Bedrock, THE System SHALL use the Rate_Limiter to ensure request frequency is less than 1 request per second
3. WHEN Bedrock returns a response, THE System SHALL parse the response to extract risk_score, risk_level, risk_factors, explanation, and confidence
4. WHEN parsing the Bedrock response, THE System SHALL validate that risk_score is between 0 and 100
5. WHEN parsing the Bedrock response, THE System SHALL validate that risk_level matches the risk_score range
6. IF Bedrock is unavailable or returns an error, THEN THE System SHALL use fallback rule-based scoring
7. WHEN risk assessment completes, THE System SHALL store the risk assessment to S3_Bucket and DynamoDB_Table
8. WHEN using fallback scoring, THE System SHALL mark the assessment with lower confidence value

### Requirement 5: Rate Limiting for Bedrock API

**User Story:** As a system administrator, I want to enforce rate limiting on Bedrock API calls, so that I comply with competition rules and avoid throttling.

#### Acceptance Criteria

1. THE Rate_Limiter SHALL ensure the time interval between consecutive Bedrock requests is at least 1.0 seconds
2. WHEN a request is made before the minimum interval has elapsed, THE Rate_Limiter SHALL wait until the interval is satisfied
3. WHEN the Rate_Limiter waits, THE System SHALL log the wait time to CloudWatch
4. THE System SHALL track the number of Bedrock requests per time window for monitoring purposes

### Requirement 6: Fallback Rule-Based Risk Scoring

**User Story:** As a fraud detection analyst, I want a fallback risk scoring mechanism, so that the system continues to function when AI services are unavailable.

#### Acceptance Criteria

1. WHEN Bedrock is unavailable, THE System SHALL calculate risk_score using predefined rules based on feature thresholds
2. WHEN total_volume exceeds $100,000, THE System SHALL add 20 points to risk_score
3. WHEN night_transaction_ratio exceeds 0.3, THE System SHALL add 15 points to risk_score
4. WHEN round_number_ratio exceeds 0.5, THE System SHALL add 20 points to risk_score
5. WHEN concentration_score exceeds 0.7, THE System SHALL add 15 points to risk_score
6. WHEN rapid_transaction_count exceeds 10, THE System SHALL add 15 points to risk_score
7. WHEN velocity_score exceeds 10 transactions per hour, THE System SHALL add 15 points to risk_score
8. WHEN calculating fallback risk_score, THE System SHALL cap the total at 100
9. WHEN using fallback scoring, THE System SHALL set confidence to 0.7

### Requirement 7: Risk Level Classification

**User Story:** As a fraud detection analyst, I want accounts classified into risk levels, so that I can prioritize investigation efforts.

#### Acceptance Criteria

1. WHEN risk_score is between 0 and 25, THE System SHALL assign risk_level as LOW
2. WHEN risk_score is between 26 and 50, THE System SHALL assign risk_level as MEDIUM
3. WHEN risk_score is between 51 and 75, THE System SHALL assign risk_level as HIGH
4. WHEN risk_score is between 76 and 100, THE System SHALL assign risk_level as CRITICAL
5. THE System SHALL ensure risk_level always matches the risk_score range

### Requirement 8: Report Generation and Visualization

**User Story:** As a fraud detection analyst, I want comprehensive reports with visualizations, so that I can present findings to stakeholders and make informed decisions.

#### Acceptance Criteria

1. WHEN the Report_Generator receives risk assessments, THE System SHALL calculate total_accounts as the count of all assessed accounts
2. WHEN the Report_Generator receives risk assessments, THE System SHALL calculate risk_distribution as the count of accounts in each risk_level
3. WHEN the Report_Generator receives risk assessments, THE System SHALL calculate average_risk_score across all accounts
4. WHEN the Report_Generator receives risk assessments, THE System SHALL identify top_suspicious_accounts sorted by risk_score in descending order
5. WHEN generating visualizations, THE System SHALL create a risk distribution pie chart showing the proportion of each risk_level
6. WHEN generating visualizations, THE System SHALL create a risk score histogram showing the distribution of risk scores
7. WHEN generating visualizations, THE System SHALL store all charts to S3_Bucket
8. WHEN generating the report, THE System SHALL create an HTML presentation including summary statistics, charts, and top suspicious accounts
9. WHEN the report is complete, THE System SHALL store the report to S3_Bucket and return the S3 URI

### Requirement 9: Data Storage and Persistence

**User Story:** As a system administrator, I want all data securely stored and organized, so that I can audit the analysis process and retrieve historical data.

#### Acceptance Criteria

1. THE System SHALL store raw transaction data in S3_Bucket with path pattern `raw-data/{timestamp}.json`
2. THE System SHALL store extracted features in S3_Bucket with path pattern `features/{timestamp}.json`
3. THE System SHALL store risk assessments in S3_Bucket with path pattern `risk-scores/{timestamp}.json`
4. THE System SHALL store generated reports in S3_Bucket with path pattern `reports/{timestamp}/`
5. THE System SHALL store account risk profiles in DynamoDB_Table with account_id as the partition key
6. WHEN storing data to S3_Bucket, THE System SHALL use server-side encryption with AES-256
7. WHEN storing data to DynamoDB_Table, THE System SHALL enable encryption at rest

### Requirement 10: Workflow Orchestration

**User Story:** As a system administrator, I want automated workflow orchestration, so that the analysis process executes reliably without manual intervention.

#### Acceptance Criteria

1. WHEN Step_Functions is invoked, THE System SHALL execute the Data_Fetcher Lambda function first
2. WHEN the Data_Fetcher completes successfully, THE System SHALL execute the Feature_Extractor Lambda function
3. WHEN the Feature_Extractor completes successfully, THE System SHALL execute the Risk_Analyzer Lambda function
4. WHEN the Risk_Analyzer completes successfully, THE System SHALL execute the Report_Generator Lambda function
5. IF any Lambda function fails, THEN THE System SHALL retry with exponential backoff according to the retry policy
6. IF all retries fail for a Lambda function, THEN THE System SHALL transition to the FailState and log the error
7. WHEN all Lambda functions complete successfully, THE System SHALL transition to the SuccessState
8. WHEN Step_Functions executes, THE System SHALL log all state transitions to CloudWatch

### Requirement 11: Error Handling and Retry Logic

**User Story:** As a system administrator, I want robust error handling and retry logic, so that transient failures do not cause the entire analysis to fail.

#### Acceptance Criteria

1. WHEN the Data_Fetcher encounters an API error, THE System SHALL retry up to 3 times with exponential backoff
2. WHEN the Feature_Extractor encounters a processing error, THE System SHALL retry up to 3 times with exponential backoff
3. WHEN the Risk_Analyzer encounters a Bedrock error, THE System SHALL retry up to 2 times with exponential backoff
4. IF Bedrock continues to fail after retries, THEN THE System SHALL use fallback rule-based scoring
5. WHEN any Lambda function encounters an error, THE System SHALL log the error details to CloudWatch
6. WHEN S3 operations fail, THE System SHALL retry up to 3 times before failing
7. IF all retries are exhausted, THEN THE System SHALL send an alert notification

### Requirement 12: Security and Compliance

**User Story:** As a security officer, I want the system to comply with security best practices and competition rules, so that sensitive data is protected and regulations are met.

#### Acceptance Criteria

1. THE System SHALL store all S3_Buckets with public access blocked
2. THE System SHALL enable encryption at rest for all S3_Buckets using AES-256
3. THE System SHALL enable encryption at rest for DynamoDB_Table
4. THE System SHALL retrieve API keys from Secrets_Manager and never hardcode them in source code
5. THE System SHALL use IAM roles with least privilege permissions for all Lambda functions
6. THE System SHALL use TLS 1.2 or higher for all API communications
7. THE System SHALL not log sensitive information such as API keys or account identifiers in CloudWatch
8. THE System SHALL not create any publicly accessible resources such as EC2 instances with 0.0.0.0/0 security group rules
9. THE System SHALL not use publicly accessible RDS or EMR clusters

### Requirement 13: Monitoring and Logging

**User Story:** As a system administrator, I want comprehensive monitoring and logging, so that I can troubleshoot issues and track system performance.

#### Acceptance Criteria

1. WHEN any Lambda function executes, THE System SHALL log the start and end time to CloudWatch
2. WHEN any Lambda function encounters an error, THE System SHALL log the error message and stack trace to CloudWatch
3. WHEN the Data_Fetcher fetches transactions, THE System SHALL log the number of transactions retrieved
4. WHEN the Feature_Extractor processes accounts, THE System SHALL log the number of accounts processed
5. WHEN the Risk_Analyzer assesses risk, THE System SHALL log the number of accounts analyzed and the number of Bedrock API calls made
6. WHEN the Report_Generator creates reports, THE System SHALL log the report S3 URI
7. THE System SHALL create CloudWatch metrics for Lambda execution duration, error count, and Bedrock API call count
8. THE System SHALL not include sensitive data such as transaction amounts or account identifiers in logs

### Requirement 14: Performance and Scalability

**User Story:** As a system architect, I want the system to handle variable workloads efficiently, so that it can scale to process large volumes of transactions.

#### Acceptance Criteria

1. WHEN processing up to 10,000 transactions, THE System SHALL complete the entire workflow in less than 5 minutes
2. WHEN processing transactions, THE Feature_Extractor SHALL process at least 1,000 transactions in less than 10 seconds
3. WHEN generating reports, THE Report_Generator SHALL complete in less than 20 seconds
4. THE System SHALL support concurrent processing of multiple accounts during feature extraction
5. THE System SHALL use Lambda functions with at least 1024MB memory for optimal performance
6. WHEN storing data to S3, THE System SHALL use batch operations where possible to reduce API calls

### Requirement 15: Data Quality and Validation

**User Story:** As a fraud detection analyst, I want high-quality validated data, so that risk assessments are accurate and reliable.

#### Acceptance Criteria

1. THE System SHALL validate that all feature values are non-negative
2. THE System SHALL validate that all ratio features (night_transaction_ratio, round_number_ratio) are between 0 and 1
3. THE System SHALL validate that concentration_score is between 0 and 1
4. THE System SHALL validate that transaction_count matches the number of input transactions
5. THE System SHALL validate that total_volume equals the sum of all transaction amounts within a tolerance of 0.01
6. IF any feature validation fails, THEN THE System SHALL log the validation error and exclude the account from risk assessment
7. WHEN validation completes, THE System SHALL include validation statistics in the report metadata

### Requirement 16: Presentation and Demo Support

**User Story:** As a hackathon participant, I want presentation-ready outputs, so that I can effectively demonstrate the system to judges.

#### Acceptance Criteria

1. WHEN the Report_Generator creates an HTML presentation, THE System SHALL include an executive summary section
2. WHEN the Report_Generator creates an HTML presentation, THE System SHALL include embedded charts and visualizations
3. WHEN the Report_Generator creates an HTML presentation, THE System SHALL include a table of top 10 suspicious accounts with risk scores and explanations
4. WHEN the Report_Generator creates an HTML presentation, THE System SHALL use a clean and professional visual design
5. WHEN the report is generated, THE System SHALL create a pre-signed URL valid for 24 hours for easy sharing
6. THE System SHALL generate all outputs in a format suitable for inclusion in presentation slides

