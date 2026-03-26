# Implementation Plan: Crypto Suspicious Account Detection

## Overview

This implementation plan converts the design into actionable coding tasks for a 4-hour hackathon MVP. The system fetches cryptocurrency transaction data from BitoPro API, extracts risk features, uses AWS Bedrock for AI-driven risk assessment, and generates comprehensive reports with visualizations.

Key constraints:
- 4-hour time limit
- AWS serverless architecture (Lambda, S3, DynamoDB, Step Functions, Bedrock)
- Bedrock rate limit: < 1 request/second
- All resources must be private and secure
- Python implementation

## Tasks

- [x] 1. Infrastructure Setup and AWS Configuration
  - Create private S3 buckets with encryption for raw data, features, risk scores, and reports
  - Create DynamoDB table for account risk profiles with encryption at rest
  - Set up AWS Secrets Manager entry for BitoPro API credentials
  - Configure IAM roles with least privilege policies for each Lambda function
  - Set up CloudWatch log groups for monitoring
  - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7_

- [x] 2. Implement Common Utilities and Data Models
  - [x] 2.1 Create data models (Transaction, TransactionFeatures, RiskAssessment, AnalysisReport)
    - Define dataclasses with validation in `src/common/models.py`
    - Implement RiskLevel enum (LOW, MEDIUM, HIGH, CRITICAL)
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 7.1, 7.2, 7.3, 7.4, 7.5_

  - [x] 2.2 Write property test for data model validation
    - **Property 1: Transaction validation ensures positive amounts and valid fields**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5**

  - [x] 2.3 Create validators module
    - Implement `validate_transaction()` function
    - Implement `validate_features()` function
    - Implement `validate_risk_assessment()` function
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 15.1, 15.2, 15.3, 15.4, 15.5, 15.6_

  - [x] 2.4 Implement rate limiter class
    - Create `RateLimiter` class in `src/common/rate_limiter.py`
    - Implement `wait_if_needed()` method to enforce < 1 req/sec
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 2.5 Write property test for rate limiter
    - **Property 4: Time between consecutive requests is always ≥ 1.0 seconds**
    - **Validates: Requirements 5.1, 5.2**

  - [x] 2.6 Create AWS clients utility module
    - Initialize boto3 clients for S3, DynamoDB, Bedrock, Secrets Manager
    - Implement connection pooling and error handling
    - _Requirements: 1.1, 12.6_

- [x] 3. Implement Data Fetcher Lambda
  - [x] 3.1 Create BitoPro API client
    - Implement `fetch_transactions()` method in `src/utils/bitopro_client.py`
    - Handle API authentication with API key from Secrets Manager
    - Implement retry logic with exponential backoff
    - _Requirements: 1.1, 1.2, 1.5, 11.1_

  - [x] 3.2 Implement Data Fetcher Lambda handler
    - Create `handler.py` in `src/lambdas/data_fetcher/`
    - Retrieve BitoPro API key from Secrets Manager
    - Fetch transactions for specified time range
    - Validate each transaction
    - Store raw data to S3 in JSON format
    - Log operation details to CloudWatch
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 9.1, 13.1, 13.3_

  - [x] 3.3 Write unit tests for Data Fetcher
    - Test API key retrieval from Secrets Manager
    - Test transaction validation logic
    - Test S3 storage with mocked boto3
    - Test retry logic on API failures
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 4. Checkpoint - Verify data ingestion works
  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. Implement Feature Extractor Lambda
  - [x] 5.1 Implement feature extraction algorithms
    - Create `extract_features()` function in `src/lambdas/feature_extractor/handler.py`
    - Calculate basic statistics: total_volume, transaction_count, avg_transaction_size, max_transaction_size
    - Calculate unique_counterparties count
    - Calculate night_transaction_ratio (00:00-06:00)
    - Calculate round_number_ratio using `is_round_number()` helper
    - Calculate rapid_transaction_count (< 5 minutes apart)
    - Calculate concentration_score using Herfindahl index
    - Calculate velocity_score (transactions per hour)
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

  - [x] 5.2 Implement Feature Extractor Lambda handler
    - Read raw transaction data from S3
    - Group transactions by account
    - Extract features for each account
    - Validate extracted features
    - Store features to S3
    - _Requirements: 3.1, 3.11, 15.1, 15.2, 15.3, 15.4, 15.5_

  - [x] 5.3 Write property test for feature extraction
    - **Property 2: Feature ratios are always between 0 and 1**
    - **Validates: Requirements 3.6, 3.7, 3.9, 15.2**

  - [x] 5.4 Write property test for total volume calculation
    - **Property 2: Total volume equals sum of transaction amounts**
    - **Validates: Requirements 3.2, 15.5**

  - [x] 5.5 Write unit tests for feature extraction
    - Test single transaction feature extraction
    - Test multiple transactions aggregation
    - Test night transaction ratio calculation
    - Test round number detection
    - Test concentration score calculation
    - Test edge cases (single transaction, all to same counterparty)
    - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10_

- [x] 6. Implement Risk Analyzer Lambda
  - [x] 6.1 Create Bedrock prompt template
    - Define `RISK_ANALYSIS_PROMPT` template in `src/lambdas/risk_analyzer/handler.py`
    - Include all feature values in structured format
    - Specify expected JSON response format
    - _Requirements: 4.1_

  - [x] 6.2 Implement Bedrock risk analysis function
    - Create `analyze_risk_with_bedrock()` function
    - Build prompt from features using template
    - Call Bedrock API with rate limiting
    - Parse LLM response to extract risk_score, risk_level, risk_factors, explanation, confidence
    - Validate parsed response
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2_

  - [x] 6.3 Implement fallback rule-based scoring
    - Create `fallback_risk_scoring()` function
    - Implement scoring rules based on feature thresholds
    - Calculate risk_score from weighted features
    - Determine risk_level from risk_score
    - Mark with lower confidence (0.7)
    - _Requirements: 4.6, 4.8, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9_

  - [x] 6.4 Implement Risk Analyzer Lambda handler
    - Read features from S3
    - Initialize rate limiter
    - Analyze risk for each account with rate limiting
    - Handle Bedrock errors with fallback scoring
    - Store risk assessments to S3 and DynamoDB
    - Log Bedrock API call count and wait times
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3, 9.3, 9.5, 11.3, 11.4, 13.5_

  - [x] 6.5 Write property test for risk assessment
    - **Property 3: Risk score is always between 0 and 100**
    - **Validates: Requirements 4.4, 7.1, 7.2, 7.3, 7.4**

  - [x] 6.6 Write property test for risk level matching
    - **Property 3: Risk level always matches risk score range**
    - **Validates: Requirements 4.5, 7.1, 7.2, 7.3, 7.4, 7.5**

  - [x] 6.7 Write unit tests for risk analysis
    - Test Bedrock prompt construction
    - Test LLM response parsing
    - Test fallback scoring with various feature combinations
    - Test risk level classification
    - Test rate limiter integration
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8_

- [x] 7. Checkpoint - Verify risk analysis works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 8. Implement Report Generator Lambda
  - [x] 8.1 Implement summary statistics calculation
    - Create `generate_summary_report()` function in `src/lambdas/report_generator/handler.py`
    - Calculate total_accounts, total_transactions
    - Calculate risk_distribution by risk_level
    - Calculate average_risk_score
    - Identify top_suspicious_accounts sorted by risk_score
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 8.2 Implement chart generation
    - Create `generate_risk_distribution_chart()` function using matplotlib
    - Create `generate_risk_score_histogram()` function
    - Store charts to S3
    - _Requirements: 8.5, 8.6, 8.7_

  - [x] 8.3 Implement HTML presentation generator
    - Create `generate_presentation_slides()` function
    - Include executive summary section
    - Embed charts and visualizations
    - Include table of top 10 suspicious accounts with explanations
    - Use clean and professional design
    - _Requirements: 8.8, 16.1, 16.2, 16.3, 16.4_

  - [x] 8.4 Implement Report Generator Lambda handler
    - Read risk assessments from S3 and DynamoDB
    - Generate summary statistics
    - Generate all charts
    - Generate HTML presentation
    - Store all outputs to S3
    - Generate pre-signed URL for report (24-hour expiry)
    - Return report S3 URI
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8, 8.9, 9.4, 13.6, 16.5_

  - [x] 8.5 Write property test for report generation
    - **Property 5: Report total_accounts equals number of risk assessments**
    - **Validates: Requirements 8.1**

  - [x] 8.6 Write property test for risk distribution
    - **Property 5: Sum of risk_distribution values equals total_accounts**
    - **Validates: Requirements 8.2**

  - [x] 8.7 Write unit tests for report generation
    - Test summary statistics calculation
    - Test chart generation with matplotlib
    - Test HTML presentation generation
    - Test top suspicious accounts sorting
    - Test edge cases (no suspicious accounts, all high risk)
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_

- [ ] 9. Implement Step Functions Orchestration
  - [x] 9.1 Create Step Functions state machine definition
    - Define state machine in `infrastructure/state_machine.json`
    - Configure sequential execution: DataFetcher → FeatureExtractor → RiskAnalyzer → ReportGenerator
    - Add retry policies with exponential backoff for each state
    - Add error handling with Catch blocks
    - Define SuccessState and FailState
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8, 11.1, 11.2, 11.3_

  - [x] 9.2 Deploy Step Functions state machine
    - Use AWS SAM or CloudFormation to deploy state machine
    - Configure IAM role for Step Functions to invoke Lambda functions
    - _Requirements: 10.1, 10.8_

  - [x] 9.3 Write integration test for Step Functions
    - Test complete workflow execution with mock data
    - Test error handling and retries
    - Test state transitions
    - Verify execution history in CloudWatch
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_

- [ ] 10. Integration and End-to-End Testing
  - [x] 10.1 Create SAM template for deployment
    - Define all Lambda functions in `infrastructure/template.yaml`
    - Define S3 buckets with encryption and private access
    - Define DynamoDB table with encryption
    - Define IAM roles and policies
    - Configure environment variables for Lambda functions
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 9.6, 9.7_

  - [x] 10.2 Wire all components together
    - Ensure Lambda functions can communicate via S3 and DynamoDB
    - Configure Step Functions to pass data between states
    - Test data flow from ingestion to report generation
    - _Requirements: 10.1, 10.2, 10.3, 10.4_

  - [x] 10.3 Write end-to-end integration test
    - Test complete workflow with mock BitoPro API and Bedrock
    - Verify all intermediate data stored correctly in S3
    - Verify risk assessments stored in DynamoDB
    - Verify final report contains expected data
    - Use LocalStack for local AWS service testing
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 3.1, 3.11, 4.1, 4.7, 8.1, 8.9, 9.1, 9.2, 9.3, 9.4, 9.5_

  - [x] 10.4 Deploy to AWS
    - Deploy using AWS SAM CLI: `sam build && sam deploy`
    - Verify all resources created successfully
    - Test with real BitoPro API (if available) or mock data
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5_

- [ ] 11. Final Checkpoint - Verify complete system
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 12. Demo Preparation and Documentation
  - [ ] 12.1 Prepare demo data and test execution
    - Create sample transaction data for demo
    - Execute Step Functions workflow with demo data
    - Verify report generation with charts and explanations
    - _Requirements: 16.1, 16.2, 16.3, 16.4_

  - [ ] 12.2 Create presentation materials
    - Document problem statement and solution overview
    - Prepare technical highlights and architecture diagrams
    - Create demo script with step-by-step walkthrough
    - Prepare Q&A responses for judges
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_

  - [ ] 12.3 Verify compliance checklist
    - Confirm all S3 buckets are private with encryption
    - Confirm no public EC2 security groups
    - Confirm Bedrock rate limiting < 1 req/sec
    - Confirm all secrets in Secrets Manager
    - Confirm CloudWatch logging without sensitive data
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.8, 12.9, 13.8_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP delivery
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation and allow for user feedback
- Property tests validate universal correctness properties from the design document
- Unit tests validate specific examples and edge cases
- The 4-hour time constraint requires focus on core functionality first, with testing as optional
- All Lambda functions use Python 3.11 runtime
- Use AWS SAM for local testing and deployment
- Bedrock rate limiting is critical for compliance - must be < 1 request/second
- All resources must be private and encrypted per competition rules
