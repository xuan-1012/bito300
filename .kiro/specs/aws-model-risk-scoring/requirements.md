# Requirements Document: AWS Model Risk Scoring

## Introduction

AWS 模型層與風險評分層是加密貨幣可疑帳戶偵測系統的核心推論引擎，負責將前處理後的交易特徵轉換為可操作的風險評分。本系統完全基於 AWS 原生服務（Amazon Bedrock、SageMaker），確保符合黑客松規範，不依賴外部模型服務。

核心價值主張：
- **AWS 原生優先**：使用 Bedrock Foundation Models 或 SageMaker JumpStart 預訓練模型
- **穩定推論保證**：實作 rate limiting、fallback 機制、錯誤處理
- **可解釋性**：提供風險因子分析與自然語言解釋
- **彈性架構**：支援有標籤（監督式）與無標籤（規則+LLM）兩種模式
- **成本優化**：優先使用 Bedrock on-demand，避免昂貴的模型訓練

## Glossary

- **ModelService**: 統一的模型推論服務，協調不同推論路徑
- **BedrockInferenceEngine**: 使用 Amazon Bedrock Foundation Models 進行無標籤風險評估的引擎
- **SageMakerInferenceEngine**: 使用 SageMaker Endpoint 進行有標籤風險評估的引擎
- **FallbackRuleEngine**: 當 Bedrock 或 SageMaker 不可用時的降級規則引擎
- **RateLimiter**: 速率限制器，確保 Bedrock API 呼叫頻率 < 1 req/sec
- **FeatureProcessor**: 特徵處理器，負責驗證、標準化、編碼特徵
- **TransactionFeatures**: 交易特徵資料結構，包含帳戶的交易行為特徵
- **RiskAssessment**: 風險評估結果，包含風險分數、等級、因子、解釋
- **InferenceMode**: 推論模式，包含 SUPERVISED（有標籤）、UNSUPERVISED（無標籤）、FALLBACK（降級）
- **RiskLevel**: 風險等級，分為 LOW、MEDIUM、HIGH、CRITICAL
- **Bedrock**: Amazon Bedrock，AWS 的 Foundation Model 服務
- **SageMaker**: Amazon SageMaker，AWS 的機器學習平台
- **LLM**: Large Language Model，大型語言模型
- **Rate Limiting**: 速率限制，控制 API 呼叫頻率

## Requirements

### Requirement 1: 特徵驗證與標準化

**User Story:** As a data scientist, I want the system to validate and normalize transaction features before inference, so that invalid data is rejected early and model inputs are consistent.

#### Acceptance Criteria

1. WHEN TransactionFeatures is provided, THE FeatureProcessor SHALL validate that account_id is non-empty
2. WHEN TransactionFeatures is provided, THE FeatureProcessor SHALL validate that total_volume >= 0
3. WHEN TransactionFeatures is provided, THE FeatureProcessor SHALL validate that transaction_count > 0
4. WHEN TransactionFeatures is provided, THE FeatureProcessor SHALL validate that night_transaction_ratio is between 0 and 1
5. WHEN TransactionFeatures is provided, THE FeatureProcessor SHALL validate that round_number_ratio is between 0 and 1
6. WHEN TransactionFeatures is provided, THE FeatureProcessor SHALL validate that concentration_score is between 0 and 1
7. WHEN validation fails, THE FeatureProcessor SHALL raise ValidationError with detailed error message
8. WHEN features are valid, THE FeatureProcessor SHALL normalize numerical features using Z-score normalization
9. WHEN scaler_params are provided, THE FeatureProcessor SHALL use them for normalization
10. WHEN features are normalized, THE FeatureProcessor SHALL return a dictionary of normalized feature values

### Requirement 2: Bedrock LLM 推論（無標籤模式）

**User Story:** As a system operator, I want to use Amazon Bedrock LLM for risk assessment when labeled data is not available, so that I can quickly deploy the system without training data.

#### Acceptance Criteria

1. WHEN inference mode is UNSUPERVISED, THE ModelService SHALL use BedrockInferenceEngine for risk assessment
2. WHEN BedrockInferenceEngine is called, THE System SHALL build a prompt containing all transaction features
3. WHEN calling Bedrock API, THE System SHALL use model ID "anthropic.claude-3-sonnet-20240229-v1:0"
4. WHEN calling Bedrock API, THE System SHALL set temperature to 0.0 for deterministic output
5. WHEN calling Bedrock API, THE System SHALL set max_tokens to 1024
6. WHEN Bedrock returns response, THE System SHALL parse JSON output containing risk_score, risk_level, risk_factors, explanation, confidence
7. WHEN parsing fails, THE System SHALL raise ParseError with original response for debugging
8. WHEN Bedrock API call succeeds, THE System SHALL return risk assessment with confidence >= 0.8
9. WHEN Bedrock API call fails, THE System SHALL trigger fallback mechanism if enabled
10. WHEN Bedrock is used, THE System SHALL log inference time and model ID to CloudWatch

### Requirement 3: Rate Limiting 保證

**User Story:** As a compliance officer, I want the system to enforce rate limiting on Bedrock API calls (< 1 req/sec), so that we comply with hackathon requirements and avoid API throttling.

#### Acceptance Criteria

1. WHEN RateLimiter is initialized, THE System SHALL set max_requests_per_second < 1.0
2. WHEN wait_if_needed is called, THE RateLimiter SHALL calculate time since last request
3. WHEN time since last request < min_interval, THE RateLimiter SHALL sleep for remaining time
4. WHEN time since last request >= min_interval, THE RateLimiter SHALL return immediately with wait_time = 0
5. WHEN wait_if_needed completes, THE RateLimiter SHALL update last_request_time to current time
6. WHEN multiple threads call wait_if_needed, THE RateLimiter SHALL use lock for thread safety
7. WHEN any two consecutive Bedrock API calls occur, THE time interval SHALL be >= 1.0 seconds
8. WHEN batch inference is performed, THE System SHALL apply rate limiting to each request
9. WHEN rate limiting causes delay, THE System SHALL log wait time to CloudWatch
10. WHEN get_current_rate is called, THE RateLimiter SHALL return current request frequency

### Requirement 4: SageMaker 推論（有標籤模式）

**User Story:** As a data scientist, I want to use SageMaker Endpoint for risk assessment when labeled training data is available, so that I can achieve higher accuracy with supervised learning.

#### Acceptance Criteria

1. WHEN inference mode is SUPERVISED, THE ModelService SHALL use SageMakerInferenceEngine for risk assessment
2. WHEN SageMakerInferenceEngine is called, THE System SHALL prepare input in CSV format
3. WHEN preparing input, THE System SHALL convert TransactionFeatures to feature vector following feature_config order
4. WHEN calling SageMaker Endpoint, THE System SHALL use configured endpoint_name
5. WHEN calling SageMaker Endpoint, THE System SHALL set ContentType to "text/csv"
6. WHEN calling SageMaker Endpoint, THE System SHALL set Accept to "application/json"
7. WHEN SageMaker returns response, THE System SHALL parse risk_probability from output
8. WHEN risk_probability is parsed, THE System SHALL validate it is between 0 and 1
9. WHEN SageMaker output contains feature_importance, THE System SHALL extract and return it
10. WHEN SageMaker Endpoint call fails, THE System SHALL trigger fallback mechanism if enabled

### Requirement 5: Fallback 規則引擎

**User Story:** As a system administrator, I want a rule-based fallback mechanism when Bedrock or SageMaker is unavailable, so that the system remains operational even when AI services fail.

#### Acceptance Criteria

1. WHEN Bedrock or SageMaker fails AND fallback_enabled is true, THE System SHALL use FallbackRuleEngine
2. WHEN FallbackRuleEngine calculates risk score, THE System SHALL apply all defined rules
3. WHEN total_volume > 100000, THE FallbackRuleEngine SHALL add 20 points to risk score
4. WHEN night_transaction_ratio > 0.3, THE FallbackRuleEngine SHALL add 15 points to risk score
5. WHEN round_number_ratio > 0.5, THE FallbackRuleEngine SHALL add 20 points to risk score
6. WHEN concentration_score > 0.7, THE FallbackRuleEngine SHALL add 15 points to risk score
7. WHEN rapid_transaction_count > 10, THE FallbackRuleEngine SHALL add 15 points to risk score
8. WHEN velocity_score > 10, THE FallbackRuleEngine SHALL add 15 points to risk score
9. WHEN calculating risk score, THE FallbackRuleEngine SHALL cap maximum score at 100
10. WHEN rules are triggered, THE FallbackRuleEngine SHALL include triggered rule names in risk_factors
11. WHEN fallback is used, THE System SHALL set confidence to 0.7
12. WHEN fallback is used, THE System SHALL set fallback_used flag to true

### Requirement 6: 風險等級分類

**User Story:** As a risk analyst, I want risk scores to be classified into clear risk levels (LOW/MEDIUM/HIGH/CRITICAL), so that I can quickly identify high-priority accounts for investigation.

#### Acceptance Criteria

1. WHEN risk_score is between 0 and 25, THE System SHALL classify risk_level as LOW
2. WHEN risk_score is between 26 and 50, THE System SHALL classify risk_level as MEDIUM
3. WHEN risk_score is between 51 and 75, THE System SHALL classify risk_level as HIGH
4. WHEN risk_score is between 76 and 100, THE System SHALL classify risk_level as CRITICAL
5. WHEN risk_level is classified, THE System SHALL ensure consistency with risk_score range
6. WHEN RiskAssessment is created, THE System SHALL include both risk_score and risk_level
7. WHEN risk_level is LOW, THE System SHALL use green color code (#16a34a) for visualization
8. WHEN risk_level is MEDIUM, THE System SHALL use yellow color code (#ca8a04) for visualization
9. WHEN risk_level is HIGH, THE System SHALL use orange color code (#ea580c) for visualization
10. WHEN risk_level is CRITICAL, THE System SHALL use red color code (#dc2626) for visualization

### Requirement 7: 批次推論處理

**User Story:** As a system operator, I want to perform batch inference on multiple accounts efficiently, so that I can process large volumes of accounts in a single operation.

#### Acceptance Criteria

1. WHEN batch_infer is called with a list of features, THE ModelService SHALL process each feature sequentially
2. WHEN processing batch with Bedrock, THE System SHALL apply rate limiting between each request
3. WHEN processing batch with SageMaker, THE System SHALL process requests without rate limiting
4. WHEN batch inference is in progress, THE System SHALL display progress information
5. WHEN batch inference completes, THE System SHALL return list of RiskAssessment in same order as input
6. WHEN batch inference encounters error for one account, THE System SHALL continue processing remaining accounts
7. WHEN batch inference completes, THE System SHALL log total processing time
8. WHEN batch size > 100, THE System SHALL log warning about long processing time
9. WHEN batch inference uses Bedrock, THE System SHALL estimate completion time based on rate limiting
10. WHEN batch inference completes, THE System SHALL return assessments list with length equal to input list length

### Requirement 8: 錯誤處理與重試

**User Story:** As a system administrator, I want robust error handling and retry logic for API calls, so that transient failures don't cause system downtime.

#### Acceptance Criteria

1. WHEN Bedrock API call fails, THE System SHALL retry up to 2 times with exponential backoff
2. WHEN retry delay is calculated, THE System SHALL use formula: base_delay * 2^(attempt-1)
3. WHEN all retries are exhausted, THE System SHALL trigger fallback if enabled
4. WHEN fallback is not enabled, THE System SHALL raise InferenceError with detailed message
5. WHEN SageMaker Endpoint is not found, THE System SHALL raise EndpointNotFoundError
6. WHEN SageMaker Endpoint status is not InService, THE System SHALL trigger fallback if enabled
7. WHEN any error occurs, THE System SHALL log error details to CloudWatch
8. WHEN error is logged, THE System SHALL include error message, stack trace, and context
9. WHEN ParseError occurs, THE System SHALL log original LLM response for debugging
10. WHEN network error occurs, THE System SHALL include error type in log message

### Requirement 9: 結果儲存與追蹤

**User Story:** As a data analyst, I want inference results to be stored in S3 and DynamoDB, so that I can track historical risk assessments and perform analysis.

#### Acceptance Criteria

1. WHEN inference completes successfully, THE System SHALL store RiskAssessment to S3
2. WHEN storing to S3, THE System SHALL use bucket name "risk-scores-bucket"
3. WHEN storing to S3, THE System SHALL use key format: "risk-scores/{account_id}/{timestamp}.json"
4. WHEN storing to S3, THE System SHALL enable server-side encryption (AES-256)
5. WHEN inference completes successfully, THE System SHALL update DynamoDB risk profile
6. WHEN updating DynamoDB, THE System SHALL use table name "risk-profiles-table"
7. WHEN updating DynamoDB, THE System SHALL use account_id as partition key
8. WHEN S3 or DynamoDB write fails, THE System SHALL retry up to 3 times
9. WHEN storage fails after retries, THE System SHALL log error but still return RiskAssessment
10. WHEN storage succeeds, THE System SHALL log success message with storage location

### Requirement 10: 推論元資料記錄

**User Story:** As a system operator, I want detailed metadata about each inference operation, so that I can monitor performance and troubleshoot issues.

#### Acceptance Criteria

1. WHEN inference completes, THE System SHALL record inference_time_ms
2. WHEN inference completes, THE System SHALL record inference_mode used
3. WHEN Bedrock is used, THE System SHALL record bedrock_model_id
4. WHEN SageMaker is used, THE System SHALL record sagemaker_endpoint_name
5. WHEN fallback is used, THE System SHALL set fallback_used flag to true
6. WHEN inference completes, THE System SHALL record timestamp
7. WHEN feature_importance is available, THE System SHALL include it in RiskAssessment
8. WHEN confidence score is calculated, THE System SHALL include it in RiskAssessment
9. WHEN metadata is recorded, THE System SHALL publish metrics to CloudWatch
10. WHEN inference fails, THE System SHALL record error type and message in metadata

### Requirement 11: 可解釋性輸出

**User Story:** As a compliance officer, I want clear explanations for risk assessments, so that I can understand why an account was flagged and justify decisions to regulators.

#### Acceptance Criteria

1. WHEN risk assessment is generated, THE System SHALL include non-empty explanation text
2. WHEN risk assessment is generated, THE System SHALL include at least one risk_factor
3. WHEN Bedrock generates explanation, THE System SHALL use natural language in Traditional Chinese
4. WHEN fallback generates explanation, THE System SHALL list all triggered rules
5. WHEN risk_factors are provided, THE System SHALL include specific contribution percentages
6. WHEN explanation is generated, THE System SHALL mention key feature values that contributed to risk
7. WHEN risk_level is HIGH or CRITICAL, THE explanation SHALL highlight most significant risk factors
8. WHEN risk_level is LOW, THE explanation SHALL confirm normal behavior patterns
9. WHEN confidence is low (< 0.7), THE explanation SHALL mention uncertainty
10. WHEN multiple risk factors exist, THE explanation SHALL prioritize top 3 factors by contribution

### Requirement 12: 配置管理

**User Story:** As a system administrator, I want flexible configuration options for model service, so that I can adjust behavior without code changes.

#### Acceptance Criteria

1. WHEN ModelService is initialized, THE System SHALL accept ModelConfig parameter
2. WHEN ModelConfig is provided, THE System SHALL validate inference_mode is valid enum value
3. WHEN ModelConfig is provided, THE System SHALL validate max_requests_per_second < 1.0
4. WHEN ModelConfig is provided, THE System SHALL validate bedrock_temperature is between 0 and 1
5. WHEN ModelConfig is provided, THE System SHALL validate fallback_confidence is between 0 and 1
6. WHEN inference_mode is SUPERVISED, THE System SHALL require sagemaker_endpoint_name to be non-null
7. WHEN feature_scaling_enabled is true, THE System SHALL apply normalization before inference
8. WHEN scaler_params are provided, THE System SHALL use them for feature normalization
9. WHEN configuration is invalid, THE System SHALL raise ConfigurationError with specific issue
10. WHEN configuration changes, THE System SHALL log configuration update to CloudWatch

### Requirement 13: 效能監控

**User Story:** As a system operator, I want comprehensive performance monitoring, so that I can identify bottlenecks and optimize system performance.

#### Acceptance Criteria

1. WHEN inference completes, THE System SHALL publish InferenceCount metric to CloudWatch
2. WHEN inference completes, THE System SHALL publish InferenceLatency metric to CloudWatch
3. WHEN fallback is used, THE System SHALL publish FallbackRate metric to CloudWatch
4. WHEN Bedrock API is called, THE System SHALL publish BedrockAPICallCount metric to CloudWatch
5. WHEN rate limiting causes delay, THE System SHALL publish RateLimitWaitTime metric to CloudWatch
6. WHEN error occurs, THE System SHALL publish ErrorRate metric to CloudWatch
7. WHEN metrics are published, THE System SHALL use namespace "CryptoFraudDetection/ModelLayer"
8. WHEN metrics are published, THE System SHALL include timestamp
9. WHEN batch inference is performed, THE System SHALL publish BatchSize metric
10. WHEN SageMaker is used, THE System SHALL publish SageMakerLatency metric separately

### Requirement 14: 安全性與合規

**User Story:** As a security officer, I want the system to handle sensitive data securely and comply with data protection regulations, so that we protect user privacy and meet compliance requirements.

#### Acceptance Criteria

1. WHEN storing data to S3, THE System SHALL enable encryption at rest (AES-256)
2. WHEN storing data to DynamoDB, THE System SHALL enable encryption at rest
3. WHEN logging to CloudWatch, THE System SHALL NOT include real account_id values
4. WHEN logging to CloudWatch, THE System SHALL NOT include transaction amounts
5. WHEN calling AWS services, THE System SHALL use IAM Role instead of API keys
6. WHEN Bedrock prompt is built, THE System SHALL use anonymized account identifiers
7. WHEN accessing S3 buckets, THE System SHALL verify bucket is private
8. WHEN accessing DynamoDB tables, THE System SHALL use least privilege IAM permissions
9. WHEN API calls are made, THE System SHALL enable CloudTrail logging
10. WHEN sensitive data is processed, THE System SHALL ensure data is not cached in logs

### Requirement 15: Lambda 函數整合

**User Story:** As a developer, I want the model service to integrate seamlessly with AWS Lambda, so that it can be deployed as a serverless function.

#### Acceptance Criteria

1. WHEN Lambda function is initialized, THE System SHALL create Bedrock and SageMaker clients once
2. WHEN Lambda function is initialized, THE System SHALL create RateLimiter instance once
3. WHEN Lambda handler is invoked, THE System SHALL parse features from event payload
4. WHEN Lambda handler receives invalid event, THE System SHALL return 400 status code with error message
5. WHEN inference succeeds, THE Lambda handler SHALL return 200 status code with RiskAssessment JSON
6. WHEN inference fails, THE Lambda handler SHALL return 500 status code with error message
7. WHEN Lambda function runs, THE System SHALL complete within 900 seconds timeout
8. WHEN Lambda function uses 1024 MB memory, THE System SHALL not exceed memory limit
9. WHEN Lambda function is invoked, THE System SHALL log execution details to CloudWatch
10. WHEN Lambda cold start occurs, THE System SHALL complete initialization within 10 seconds

### Requirement 16: 成本優化

**User Story:** As a finance manager, I want the system to optimize costs while maintaining quality, so that we can operate within budget constraints.

#### Acceptance Criteria

1. WHEN processing low-risk accounts (obvious cases), THE System SHALL use fallback rules instead of AI
2. WHEN processing high-risk accounts (obvious cases), THE System SHALL use fallback rules instead of AI
3. WHEN processing medium-risk accounts, THE System SHALL use Bedrock or SageMaker
4. WHEN Bedrock usage exceeds threshold, THE System SHALL log cost warning
5. WHEN SageMaker Endpoint is idle, THE System SHALL recommend using Serverless Inference
6. WHEN batch processing is needed, THE System SHALL recommend SageMaker Batch Transform
7. WHEN cost estimation is requested, THE System SHALL calculate Bedrock cost per 1000 requests
8. WHEN cost estimation is requested, THE System SHALL calculate SageMaker cost per hour
9. WHEN fallback is used, THE System SHALL log cost savings compared to AI inference
10. WHEN monthly costs exceed budget, THE System SHALL trigger cost alert

### Requirement 17: 健康檢查與可用性

**User Story:** As a DevOps engineer, I want health checks for all dependencies, so that I can detect and respond to service outages quickly.

#### Acceptance Criteria

1. WHEN health check is performed, THE System SHALL verify Bedrock service is accessible
2. WHEN health check is performed, THE System SHALL verify SageMaker Endpoint status is InService
3. WHEN health check is performed, THE System SHALL verify S3 bucket is accessible
4. WHEN health check is performed, THE System SHALL verify DynamoDB table exists
5. WHEN SageMaker Endpoint is OutOfService, THE System SHALL log warning and use fallback
6. WHEN Bedrock is unavailable, THE System SHALL log warning and use fallback
7. WHEN health check fails, THE System SHALL publish HealthCheckFailure metric
8. WHEN health check succeeds, THE System SHALL cache result for 5 minutes
9. WHEN system starts, THE System SHALL perform health check before accepting requests
10. WHEN health check detects issue, THE System SHALL send SNS notification

### Requirement 18: 測試與驗證

**User Story:** As a QA engineer, I want comprehensive test coverage for all components, so that I can ensure system reliability and correctness.

#### Acceptance Criteria

1. WHEN unit tests are run, THE System SHALL achieve >= 80% code coverage
2. WHEN FeatureProcessor is tested, THE tests SHALL verify all validation rules
3. WHEN RateLimiter is tested, THE tests SHALL verify rate limiting is enforced
4. WHEN FallbackRuleEngine is tested, THE tests SHALL verify all rules are applied correctly
5. WHEN risk level classification is tested, THE tests SHALL verify all score ranges
6. WHEN Bedrock integration is tested, THE tests SHALL use mock responses
7. WHEN SageMaker integration is tested, THE tests SHALL use mock endpoints
8. WHEN property-based tests are run, THE tests SHALL verify universal properties hold
9. WHEN integration tests are run, THE tests SHALL use real AWS services in test account
10. WHEN tests complete, THE System SHALL generate coverage report

### Requirement 19: 文件與範例

**User Story:** As a new developer, I want clear documentation and usage examples, so that I can quickly understand and use the model service.

#### Acceptance Criteria

1. WHEN documentation is provided, THE System SHALL include README with overview
2. WHEN documentation is provided, THE System SHALL include API reference for all public methods
3. WHEN documentation is provided, THE System SHALL include configuration examples
4. WHEN documentation is provided, THE System SHALL include usage examples for unsupervised mode
5. WHEN documentation is provided, THE System SHALL include usage examples for supervised mode
6. WHEN documentation is provided, THE System SHALL include usage examples for batch inference
7. WHEN documentation is provided, THE System SHALL include error handling examples
8. WHEN documentation is provided, THE System SHALL include deployment guide
9. WHEN documentation is provided, THE System SHALL include troubleshooting section
10. WHEN code is written, THE System SHALL include docstrings for all functions and classes

### Requirement 20: MVP 快速部署

**User Story:** As a hackathon participant, I want to deploy a minimum viable product quickly (< 4 hours), so that I can demonstrate the system within time constraints.

#### Acceptance Criteria

1. WHEN MVP is deployed, THE System SHALL include Bedrock LLM inference (unsupervised mode)
2. WHEN MVP is deployed, THE System SHALL include Fallback rule engine
3. WHEN MVP is deployed, THE System SHALL include Rate limiter (< 1 req/sec)
4. WHEN MVP is deployed, THE System SHALL include Feature validation
5. WHEN MVP is deployed, THE System SHALL include Risk level classification
6. WHEN MVP is deployed, THE System SHALL include S3 storage for results
7. WHEN MVP is deployed, THE System SHALL include CloudWatch logging
8. WHEN MVP is deployed, THE System SHALL skip SageMaker integration (can add later)
9. WHEN MVP is deployed, THE System SHALL skip DynamoDB storage (use S3 only)
10. WHEN MVP is deployed, THE System SHALL complete deployment in < 4 hours total time
