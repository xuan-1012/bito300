# Implementation Plan: AWS Model Risk Scoring

## Overview

This implementation plan breaks down the AWS Model Risk Scoring system into discrete coding tasks. The system is a Python-based AWS Lambda application using Amazon Bedrock, SageMaker, and supporting AWS services for cryptocurrency fraud detection. The implementation follows a bottom-up approach: core models → utilities → engines → service → integration → testing.

## MVP Scope

For hackathon deployment (< 4 hours), the MVP includes:
- ✅ Bedrock LLM inference (unsupervised mode)
- ✅ Fallback rule engine
- ✅ Rate limiter (< 1 req/sec)
- ✅ Feature validation
- ✅ Risk level classification
- ✅ S3 storage for results
- ✅ CloudWatch logging

**Deferred for post-MVP:**
- ❌ SageMaker Endpoint integration
- ❌ DynamoDB storage
- ❌ Feature normalization
- ❌ Batch inference optimization

## Tasks

- [ ] 1. Project setup and core models
  - [x] 1.1 Create project structure
    - Create directory structure: src/model_risk_scoring/{models, engines, utils, exceptions}
    - Create tests directory: tests/{unit, integration, property}
    - Set up Python virtual environment
    - Create requirements.txt with dependencies (boto3, pydantic, pytest, hypothesis)
    - _Requirements: 20.1, 20.2_
    - _Estimated: 15 min_

  - [x] 1.2 Define core data models
    - Create InferenceMode enum (SUPERVISED, UNSUPERVISED, FALLBACK)
    - Create RiskLevel enum (LOW, MEDIUM, HIGH, CRITICAL) with color codes
    - Create TransactionFeatures dataclass with all feature fields
    - Create RiskAssessment dataclass with score, level, factors, explanation, metadata
    - Create ModelConfig dataclass with Bedrock/SageMaker/Fallback configuration
    - Create FeatureConfig dataclass with feature names and validation rules
    - _Requirements: 1.1-1.10, 6.1-6.10, 12.1-12.10_
    - _Estimated: 15 min_

  - [x] 1.3 Define custom exceptions
    - Create ValidationError exception class
    - Create InferenceError exception class
    - Create BedrockError exception class
    - Create SageMakerError exception class
    - Create ParseError exception class
    - Create ConfigurationError exception class
    - _Requirements: 8.4, 8.5, 12.9_
    - _Estimated: 10 min_

- [ ] 2. Rate Limiter implementation
  - [x] 2.1 Implement RateLimiter class
    - Create RateLimiter with max_requests_per_second parameter (< 1.0)
    - Implement wait_if_needed() method with time tracking
    - Implement thread-safe locking mechanism
    - Calculate and enforce minimum interval between requests
    - Implement get_current_rate() method
    - _Requirements: 3.1-3.10_
    - _Estimated: 15 min_

  - [ ]* 2.2 Write unit tests for RateLimiter
    - Test initialization with valid/invalid rates
    - Test wait_if_needed() enforces >= 1.0 second interval
    - Test thread safety with concurrent calls
    - Test get_current_rate() returns correct frequency
    - _Requirements: 3.7, 18.3_

  - [ ]* 2.3 Write property test for rate limiting
    - **Property 3: Rate Limiting Guarantee**
    - Verify all consecutive requests have >= 1.0 second interval
    - _Requirements: 3.7_

- [ ] 3. Feature Processor implementation
  - [x] 3.1 Implement FeatureProcessor class
    - Create FeatureProcessor with optional scaler_params
    - Implement validate() method with all validation rules
    - Validate account_id is non-empty
    - Validate total_volume >= 0, transaction_count > 0
    - Validate ratios (night_transaction_ratio, round_number_ratio, concentration_score) in [0, 1]
    - Raise ValidationError with detailed messages on failure
    - _Requirements: 1.1-1.7_
    - _Estimated: 20 min_

  - [ ]* 3.2 Implement normalize() method
    - Implement Z-score normalization for numerical features
    - Use provided scaler_params if available
    - Return dictionary of normalized feature values
    - _Requirements: 1.8-1.10_

  - [ ]* 3.3 Implement to_vector() method
    - Convert TransactionFeatures to feature vector
    - Follow feature_config order for SageMaker compatibility
    - _Requirements: 4.3_

  - [x] 3.4 Write unit tests for FeatureProcessor
    - Test validation with valid features
    - Test validation failures for each constraint
    - Test ValidationError messages are descriptive
    - _Requirements: 1.1-1.7, 18.2_
    - _Estimated: 15 min_

  - [ ]* 3.5 Write property test for feature validation
    - **Property 4: Feature Validation Completeness**
    - Verify validated features satisfy all constraints
    - _Requirements: 1.1-1.7_

- [ ] 4. Fallback Rule Engine implementation
  - [x] 4.1 Implement FallbackRuleEngine class
    - Create FallbackRuleEngine with rule configuration
    - Define 6 rules with thresholds and scores
    - Implement calculate_risk_score() method
    - Apply all rules and accumulate scores
    - Cap maximum score at 100
    - Generate risk_factors list with triggered rules
    - Generate explanation text
    - Set confidence to 0.7
    - _Requirements: 5.1-5.12_
    - _Estimated: 30 min_

  - [x] 4.2 Implement rule definitions
    - Rule 1: total_volume > 100000 → +20 points
    - Rule 2: night_transaction_ratio > 0.3 → +15 points
    - Rule 3: round_number_ratio > 0.5 → +20 points
    - Rule 4: concentration_score > 0.7 → +15 points
    - Rule 5: rapid_transaction_count > 10 → +15 points
    - Rule 6: velocity_score > 10 → +15 points
    - _Requirements: 5.3-5.8_
    - _Estimated: Included in 4.1_

  - [x] 4.3 Write unit tests for FallbackRuleEngine
    - Test each rule triggers correctly
    - Test score accumulation and capping at 100
    - Test risk_factors includes all triggered rules
    - Test explanation generation
    - Test confidence is 0.7
    - _Requirements: 5.1-5.12, 18.4_
    - _Estimated: 15 min_

  - [ ]* 4.4 Write property test for fallback scoring
    - **Property 5: Fallback Availability**
    - Verify fallback always produces valid assessment
    - _Requirements: 5.1_

- [ ] 5. Risk Level Classifier implementation
  - [x] 5.1 Implement classify_risk_level() function
    - Create function accepting risk_score (0-100)
    - Return LOW for scores 0-25
    - Return MEDIUM for scores 26-50
    - Return HIGH for scores 51-75
    - Return CRITICAL for scores 76-100
    - _Requirements: 6.1-6.5_
    - _Estimated: 10 min_

  - [x] 5.2 Write unit tests for risk level classification
    - Test boundary values (0, 25, 26, 50, 51, 75, 76, 100)
    - Test mid-range values for each level
    - _Requirements: 6.1-6.5, 18.5_
    - _Estimated: 10 min_

  - [ ]* 5.3 Write property test for risk level consistency
    - **Property 2: Risk Level Consistency**
    - Verify risk_level always matches risk_score range
    - _Requirements: 6.5_

- [ ] 6. Bedrock Inference Engine implementation
  - [ ] 6.1 Implement BedrockInferenceEngine class
    - Create BedrockInferenceEngine with bedrock_client, model_id, rate_limiter
    - Set default model_id to "anthropic.claude-3-sonnet-20240229-v1:0"
    - _Requirements: 2.1, 2.3_
    - _Estimated: 45 min_

  - [ ] 6.2 Implement build_prompt() method
    - Create prompt template with all transaction features
    - Format features with proper units and precision
    - Include evaluation criteria in prompt
    - Request JSON response format
    - Use Traditional Chinese for explanations
    - _Requirements: 2.2, 11.3_
    - _Estimated: Included in 6.1_

  - [ ] 6.3 Implement infer() method
    - Call rate_limiter.wait_if_needed() before API call
    - Build prompt using build_prompt()
    - Call bedrock_client.invoke_model() with correct parameters
    - Set temperature=0.0, max_tokens=1024
    - Parse response and extract JSON
    - Validate response contains required fields
    - Return dict with risk_score, risk_level, risk_factors, explanation, confidence
    - _Requirements: 2.1-2.10_
    - _Estimated: Included in 6.1_

  - [ ] 6.4 Implement parse_response() method
    - Extract JSON from LLM response text
    - Parse JSON and validate structure
    - Validate risk_score in [0, 100]
    - Validate confidence in [0, 1]
    - Validate risk_level is valid enum value
    - Raise ParseError if parsing fails
    - _Requirements: 2.6, 2.7_
    - _Estimated: Included in 6.1_

  - [ ] 6.5 Implement error handling and retry
    - Wrap API call in try-except
    - Retry up to 2 times with exponential backoff
    - Use formula: base_delay * 2^(attempt-1)
    - Raise BedrockError after exhausting retries
    - _Requirements: 8.1, 8.2_
    - _Estimated: Included in 6.1_

  - [ ] 6.6 Write unit tests for BedrockInferenceEngine
    - Test build_prompt() generates correct format
    - Test parse_response() with valid JSON
    - Test parse_response() raises ParseError on invalid JSON
    - Test infer() with mocked Bedrock client
    - Test retry logic with mocked failures
    - _Requirements: 2.1-2.10, 18.6_
    - _Estimated: 20 min_

  - [ ]* 6.7 Write integration test with real Bedrock
    - Test end-to-end inference with real Bedrock API
    - Verify rate limiting is enforced
    - _Requirements: 2.10, 18.9_

- [ ]* 7. SageMaker Inference Engine implementation (Post-MVP)
  - [ ]* 7.1 Implement SageMakerInferenceEngine class
    - Create SageMakerInferenceEngine with sagemaker_client, endpoint_name, feature_config
    - _Requirements: 4.1, 4.4_

  - [ ]* 7.2 Implement prepare_input() method
    - Convert TransactionFeatures to CSV format
    - Follow feature_config order
    - _Requirements: 4.2, 4.3_

  - [ ]* 7.3 Implement infer() method
    - Call sagemaker_client.invoke_endpoint()
    - Set ContentType="text/csv", Accept="application/json"
    - Parse response and extract risk_probability
    - Validate risk_probability in [0, 1]
    - Extract feature_importance if available
    - _Requirements: 4.1-4.10_

  - [ ]* 7.4 Implement parse_output() method
    - Parse JSON response from SageMaker
    - Handle different model output formats (XGBoost, Random Forest)
    - Extract risk_probability and feature_importance
    - _Requirements: 4.7-4.9_

  - [ ]* 7.5 Write unit tests for SageMakerInferenceEngine
    - Test prepare_input() generates correct CSV
    - Test parse_output() with different formats
    - Test infer() with mocked SageMaker client
    - _Requirements: 4.1-4.10, 18.7_

  - [ ]* 7.6 Write integration test with mock SageMaker Endpoint
    - Test end-to-end inference with mocked endpoint
    - _Requirements: 18.7_

- [ ] 8. Model Service implementation
  - [ ] 8.1 Implement ModelService class initialization
    - Create ModelService with bedrock_client, sagemaker_client, rate_limiter, config
    - Validate ModelConfig on initialization
    - Initialize FeatureProcessor
    - Initialize BedrockInferenceEngine
    - Initialize FallbackRuleEngine
    - _Requirements: 12.1-12.10_
    - _Estimated: 30 min_

  - [ ] 8.2 Implement infer_risk() method
    - Validate features using FeatureProcessor
    - Select inference mode (UNSUPERVISED for MVP)
    - Call BedrockInferenceEngine.infer()
    - On error, trigger fallback if enabled
    - Classify risk level using classify_risk_level()
    - Create RiskAssessment object
    - Record metadata (inference_time_ms, inference_mode, model_id, fallback_used)
    - _Requirements: 2.1, 2.9, 5.1, 6.1-6.6, 10.1-10.10_
    - _Estimated: Included in 8.1_

  - [ ]* 8.3 Implement batch_infer() method (Post-MVP)
    - Process features_list sequentially
    - Apply rate limiting for Bedrock
    - Display progress information
    - Continue on individual errors
    - Return assessments in same order as input
    - Log total processing time
    - _Requirements: 7.1-7.10_

  - [ ] 8.4 Write unit tests for ModelService
    - Test infer_risk() with valid features
    - Test fallback trigger on Bedrock failure
    - Test ValidationError on invalid features
    - Test metadata recording
    - _Requirements: 2.1-2.10, 5.1-5.12, 10.1-10.10, 18.1_
    - _Estimated: 20 min_

  - [ ]* 8.5 Write property test for risk score range
    - **Property 1: Risk Score Range Guarantee**
    - Verify all assessments have risk_score in [0, 100]
    - _Requirements: 6.1-6.5_

  - [ ]* 8.6 Write property test for confidence range
    - **Property 6: Confidence Range**
    - Verify all assessments have confidence in [0, 1]
    - _Requirements: 10.8_

- [ ] 9. S3 Storage implementation
  - [ ] 9.1 Implement store_to_s3() function
    - Create function accepting RiskAssessment and bucket_name
    - Generate S3 key: "risk-scores/{account_id}/{timestamp}.json"
    - Serialize RiskAssessment to JSON
    - Call s3_client.put_object() with ServerSideEncryption='AES256'
    - Retry up to 3 times on failure
    - Log success/failure
    - _Requirements: 9.1-9.4, 9.8-9.10, 14.1_
    - _Estimated: 20 min_

  - [ ] 9.2 Write unit tests for S3 storage
    - Test store_to_s3() with mocked S3 client
    - Test key format generation
    - Test encryption is enabled
    - Test retry logic
    - _Requirements: 9.1-9.4, 9.8-9.10_
    - _Estimated: 15 min_

  - [ ]* 9.3 Write integration test with real S3
    - Test end-to-end storage with real S3 bucket
    - Verify encryption is enabled
    - _Requirements: 9.1-9.4, 18.9_

- [ ]* 10. DynamoDB Storage implementation (Post-MVP)
  - [ ]* 10.1 Implement store_to_dynamodb() function
    - Create function accepting RiskAssessment and table_name
    - Use account_id as partition key
    - Call dynamodb_client.put_item()
    - Enable encryption at rest
    - Retry up to 3 times on failure
    - _Requirements: 9.5-9.10, 14.2_

  - [ ]* 10.2 Write unit tests for DynamoDB storage
    - Test store_to_dynamodb() with mocked DynamoDB client
    - Test partition key usage
    - Test retry logic
    - _Requirements: 9.5-9.10_

- [ ] 11. CloudWatch Logging implementation
  - [ ] 11.1 Implement logging utilities
    - Create logger with CloudWatch handler
    - Implement log_inference() function
    - Log inference_time_ms, inference_mode, model_id
    - Log fallback_used flag
    - Anonymize account_id in logs (use hash)
    - Do NOT log transaction amounts
    - _Requirements: 2.10, 10.1-10.10, 14.3-14.4_
    - _Estimated: 15 min_

  - [ ]* 11.2 Implement CloudWatch Metrics
    - Implement publish_metric() function
    - Publish InferenceCount, InferenceLatency metrics
    - Publish FallbackRate, BedrockAPICallCount metrics
    - Publish RateLimitWaitTime, ErrorRate metrics
    - Use namespace "CryptoFraudDetection/ModelLayer"
    - _Requirements: 13.1-13.10_

  - [ ] 11.3 Write unit tests for logging
    - Test log_inference() with mocked logger
    - Test account_id anonymization
    - Test sensitive data is not logged
    - _Requirements: 14.3-14.4_
    - _Estimated: 10 min_

- [ ] 12. Lambda Handler implementation
  - [ ] 12.1 Implement Lambda handler
    - Create lambda_handler(event, context) function
    - Initialize AWS clients (bedrock, sagemaker, s3) once (outside handler)
    - Initialize RateLimiter once
    - Initialize ModelService once
    - Parse features from event payload
    - Call model_service.infer_risk()
    - Store result to S3
    - Return 200 with RiskAssessment JSON on success
    - Return 400 on ValidationError
    - Return 500 on InferenceError
    - Log execution details
    - _Requirements: 15.1-15.10_
    - _Estimated: 20 min_

  - [ ] 12.2 Write unit tests for Lambda handler
    - Test handler with valid event
    - Test handler with invalid event (400 response)
    - Test handler with inference failure (500 response)
    - Test cold start initialization
    - _Requirements: 15.1-15.10_
    - _Estimated: 15 min_

  - [ ]* 12.3 Write integration test for Lambda
    - Test end-to-end Lambda invocation
    - Verify response format
    - _Requirements: 15.9, 18.9_

- [ ] 13. Configuration and deployment
  - [ ] 13.1 Create requirements.txt
    - Add boto3>=1.28.0
    - Add botocore>=1.31.0
    - Add pydantic>=2.0.0
    - Add python-dateutil>=2.8.0
    - _Requirements: Dependencies_
    - _Estimated: 5 min_

  - [ ] 13.2 Create SAM template or CloudFormation
    - Define Lambda function resource
    - Set Runtime: python3.11
    - Set Timeout: 900 seconds
    - Set MemorySize: 1024 MB
    - Define IAM role with Bedrock, S3, CloudWatch permissions
    - Define S3 bucket for risk scores
    - Set environment variables (BEDROCK_MODEL_ID, INFERENCE_MODE, FALLBACK_ENABLED)
    - _Requirements: 15.7-15.8_
    - _Estimated: 20 min_

  - [ ] 13.3 Create deployment script
    - Create deploy.sh script
    - Package Lambda function
    - Deploy using SAM or CloudFormation
    - _Requirements: 20.10_
    - _Estimated: 10 min_

- [ ] 14. Documentation
  - [ ] 14.1 Create README.md
    - Write overview of system
    - Document architecture
    - Document MVP scope
    - Include setup instructions
    - Include usage examples
    - _Requirements: 19.1-19.3_
    - _Estimated: 15 min_

  - [ ] 14.2 Create API documentation
    - Document ModelService.infer_risk() method
    - Document TransactionFeatures structure
    - Document RiskAssessment structure
    - Document ModelConfig options
    - Include code examples
    - _Requirements: 19.2-19.7_
    - _Estimated: 10 min_

  - [ ] 14.3 Add docstrings to all functions
    - Add docstrings to all public methods
    - Include parameter descriptions
    - Include return value descriptions
    - Include exception descriptions
    - _Requirements: 19.10_
    - _Estimated: 15 min_

- [ ] 15. Testing and validation
  - [ ] 15.1 Run all unit tests
    - Execute pytest for all unit tests
    - Verify >= 80% code coverage
    - Fix any failing tests
    - _Requirements: 18.1_
    - _Estimated: 10 min_

  - [ ]* 15.2 Run property-based tests
    - Execute hypothesis tests
    - Verify all properties hold
    - _Requirements: 18.8_

  - [ ]* 15.3 Run integration tests
    - Execute integration tests with real AWS services
    - Use test AWS account
    - _Requirements: 18.9_

  - [ ] 15.4 Generate coverage report
    - Run pytest with coverage
    - Generate HTML coverage report
    - Verify >= 80% coverage
    - _Requirements: 18.10_
    - _Estimated: 5 min_

- [ ] 16. Final checkpoint and demo preparation
  - [ ] 16.1 End-to-end testing
    - Test complete inference flow
    - Test with various feature combinations
    - Test fallback mechanism
    - Test error handling
    - _Estimated: 15 min_

  - [ ] 16.2 Prepare demo script
    - Create example TransactionFeatures
    - Create demo invocation script
    - Prepare visualization of results
    - _Requirements: 19.4-19.6_
    - _Estimated: 10 min_

  - [ ] 16.3 Performance validation
    - Verify Bedrock inference < 3 seconds
    - Verify Fallback inference < 50 ms
    - Verify rate limiting is enforced
    - _Estimated: 10 min_

## Notes

- Tasks marked with `*` are optional (post-MVP) and can be deferred
- Each task references specific requirements for traceability
- MVP can be completed in ~3 hours 40 minutes (estimated)
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- All tests should run with `pytest` or `pytest --cov`
- The implementation uses Python 3.11 with type hints throughout
- AWS services are accessed via boto3 with proper IAM roles
- Rate limiting is strictly enforced (< 1 req/sec) for Bedrock API calls

## MVP Implementation Order

For fastest MVP deployment, follow this order:
1. Tasks 1-2: Setup and Rate Limiter (30 min)
2. Task 3: Feature Processor (35 min)
3. Task 4: Fallback Engine (45 min)
4. Task 5: Risk Classifier (20 min)
5. Task 6: Bedrock Engine (65 min)
6. Task 8: Model Service (50 min)
7. Task 9: S3 Storage (35 min)
8. Task 11: Logging (25 min)
9. Task 12: Lambda Handler (35 min)
10. Task 13: Deployment (35 min)
11. Task 14: Documentation (40 min)
12. Task 15-16: Testing and Demo (40 min)

**Total MVP Time: ~3 hours 55 minutes**
