# Implementation Plan: BitoPro API Data Ingestion Layer

## Overview

This implementation plan breaks down the BitoPro API Data Ingestion Layer into discrete coding tasks. The system includes five main components: BitoProAPIClient for API communication, RawDataStorage for data persistence, JSONFlattener for structure transformation, SchemaInferencer for type detection, and FallbackManager for error handling. The implementation follows a fault-tolerant design with comprehensive testing using Hypothesis for property-based tests.

## Tasks

- [x] 1. Set up project structure and core data models
  - Create directory structure for ingestion components
  - Define core data models (APIRequest, APIResponse, FlattenedRecord, FieldSchema)
  - Define enums (HTTPMethod, FieldType)
  - Set up configuration dataclasses (APIConfig)
  - _Requirements: 1.1, 1.2, 1.5, 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 10.4_

- [ ]* 1.1 Write property test for data model validation
  - Test that APIRequest validation rules are enforced
  - Test that APIResponse contains valid HTTP status codes
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

- [x] 2. Implement BitoProAPIClient core functionality
  - [x] 2.1 Implement HTTP client initialization and configuration
    - Initialize requests session with connection pooling
    - Configure base URL, timeout, and retry settings
    - Implement _build_headers() method with authentication
    - _Requirements: 1.1, 1.3, 1.4, 1.5, 10.1, 12.1, 12.2_

  - [x] 2.2 Implement _execute_request() with retry logic
    - Implement exponential backoff retry mechanism
    - Handle retryable errors (5xx, timeouts, network errors)
    - Log retry attempts with attempt numbers
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 11.2, 11.3_

  - [ ]* 2.3 Write property test for retry mechanism
    - Test that retry count never exceeds max_retries
    - Test that backoff delay increases exponentially
    - _Requirements: 2.1, 2.2_

  - [x] 2.4 Implement rate limiting logic
    - Calculate minimum interval between requests
    - Track last request timestamp
    - Enforce rate limit before each request
    - _Requirements: 4.1, 4.2, 4.3, 4.4_

  - [ ]* 2.5 Write property test for rate limiting
    - Test that time between requests respects rate limit
    - Test that rate limit is maintained across multiple requests
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 2.6 Implement pagination handling
    - Detect pagination information in responses
    - Automatically fetch subsequent pages
    - Aggregate all pages into single result list
    - Respect rate limiting between page fetches
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

  - [ ]* 2.7 Write unit tests for pagination
    - Test single page response
    - Test multi-page aggregation
    - Test pagination disabled mode
    - _Requirements: 3.1, 3.2, 3.5_

  - [x] 2.8 Implement fetch_data() main method
    - Validate input parameters
    - Build and execute HTTP requests
    - Handle pagination if enabled
    - Log request details and responses
    - _Requirements: 1.1, 1.2, 9.1, 9.2, 11.1_

- [x] 3. Checkpoint - Ensure BitoProAPIClient tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 4. Implement RawDataStorage component
  - [x] 4.1 Create StorageBackend abstract interface
    - Define save() and load() abstract methods
    - _Requirements: 5.1, 5.2_

  - [x] 4.2 Implement S3Storage backend
    - Initialize boto3 S3 client
    - Implement save() with encryption
    - Configure private bucket access
    - _Requirements: 5.3, 12.3_

  - [x] 4.3 Implement LocalStorage backend
    - Create directory structure if not exists
    - Implement save() to local filesystem
    - _Requirements: 5.4_

  - [x] 4.4 Implement RawDataStorage manager
    - Implement generate_key() with timestamp and endpoint
    - Implement store_raw_response() without modifications
    - Return storage URI after successful save
    - Log storage operations with URI and timestamp
    - _Requirements: 5.1, 5.2, 5.5, 9.6, 11.4_

  - [ ]* 4.5 Write property test for storage key generation
    - Test that keys are unique for different timestamps
    - Test that keys include endpoint information
    - _Requirements: 5.2_

  - [ ]* 4.6 Write unit tests for storage backends
    - Test S3 storage with mocked boto3
    - Test local storage with temporary directory
    - Test storage failure and retry
    - _Requirements: 5.3, 5.4, 8.6, 8.7_

- [x] 5. Implement JSONFlattener component
  - [x] 5.1 Implement JSONFlattener initialization
    - Configure separator, max_depth, and list handling strategy
    - Validate configuration parameters
    - _Requirements: 6.2, 6.5, 10.2_

  - [x] 5.2 Implement _flatten_dict() recursive method
    - Recursively flatten nested dictionaries
    - Concatenate parent and child keys with separator
    - Enforce max_depth limit to prevent infinite recursion
    - Serialize remaining nested structures as JSON strings at max depth
    - _Requirements: 6.1, 6.2, 6.5_

  - [x] 5.3 Implement _handle_list_field() method
    - Explode lists of dictionaries into multiple records
    - Serialize lists of primitives as JSON strings
    - Handle empty lists appropriately
    - _Requirements: 6.3, 6.4_

  - [x] 5.4 Implement flatten() main method
    - Handle both dict and list inputs
    - Ensure output has maximum depth of 1
    - Handle errors gracefully with FallbackManager
    - _Requirements: 6.1, 6.6, 8.4_

  - [x] 5.5 Write property test for flattening depth
    - Test that flattened output never exceeds depth 1
    - Test that all original data is preserved
    - _Requirements: 6.6_

  - [ ]* 5.6 Write unit tests for JSON flattening
    - Test nested dictionary flattening
    - Test list explosion
    - Test primitive list serialization
    - Test max depth enforcement
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [x] 6. Checkpoint - Ensure storage and flattening tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Implement SchemaInferencer component
  - [x] 7.1 Implement SchemaInferencer initialization
    - Configure sample_size and confidence_threshold
    - _Requirements: 7.1, 10.3_

  - [x] 7.2 Implement type detection helper methods
    - Implement _is_numeric() for numeric type detection
    - Implement _is_datetime() with pattern matching
    - Implement _is_id_like() with UUID, hash, and ID patterns
    - Implement is_id_field_name() for field name analysis
    - _Requirements: 7.3, 7.4, 7.5, 7.6_

  - [x] 7.3 Implement _infer_field_type() method
    - Analyze sample values to determine field type
    - Calculate confidence score for each type
    - Handle mixed types with low confidence
    - Prefer id_like for numeric fields with ID-related names
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.8_

  - [ ]* 7.4 Write property test for type inference consistency
    - Test that same input produces same inferred type
    - Test that confidence correlates with type purity
    - _Requirements: 7.2, 7.8_

  - [x] 7.5 Implement infer_schema() main method
    - Collect sample values for each field
    - Infer type for each field
    - Identify nullable fields and count nulls
    - Create FieldSchema objects for all fields
    - Handle errors with FallbackManager to create minimal schema
    - _Requirements: 7.1, 7.2, 7.7, 8.5_

  - [x] 7.6 Implement export_schema() method
    - Serialize schema to JSON format
    - Write to specified output path
    - Log schema export with field count and path
    - _Requirements: 7.9, 11.6_

  - [ ]* 7.7 Write unit tests for schema inference
    - Test numeric type detection
    - Test datetime pattern matching
    - Test ID-like pattern detection
    - Test mixed type handling
    - Test nullable field detection
    - _Requirements: 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8_

- [x] 8. Implement FallbackManager component
  - [x] 8.1 Implement FallbackManager initialization
    - Configure logger for error tracking
    - _Requirements: 11.5_

  - [x] 8.2 Implement with_fallback() method
    - Execute primary function with try-catch
    - Execute fallback function on error
    - Return default value if both fail
    - Call custom error handler if provided
    - _Requirements: 8.1, 8.2, 8.3_

  - [x] 8.3 Implement handle_missing_field() method
    - Check if field exists in data
    - Return default value if missing
    - Log warning for missing field
    - _Requirements: 8.1_

  - [x] 8.4 Implement handle_type_mismatch() method
    - Attempt type conversion
    - Return default value if conversion fails
    - Log error with type details
    - _Requirements: 8.2, 8.3_

  - [ ]* 8.5 Write property test for fallback behavior
    - Test that fallback always returns valid value
    - Test that errors are logged appropriately
    - _Requirements: 8.1, 8.2, 8.3_

  - [ ]* 8.6 Write unit tests for error handling
    - Test missing field handling
    - Test type mismatch handling
    - Test fallback function execution
    - Test default value return
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 9. Implement main ingestion workflow
  - [x] 9.1 Create ingest_bitopro_data() orchestration function
    - Initialize all components (client, storage, flattener, inferencer, fallback)
    - Fetch data with pagination and retry
    - Store raw responses to storage backend
    - Flatten JSON structures
    - Infer schema from flattened data
    - Export schema to JSON file
    - Return storage URI and schema path
    - _Requirements: 1.1, 2.1, 3.1, 5.1, 7.1, 7.9_

  - [ ]* 9.2 Write integration tests for complete workflow
    - Test end-to-end ingestion with mocked API
    - Test S3 storage integration
    - Test local storage integration
    - Test error recovery scenarios
    - _Requirements: 1.1, 2.1, 3.1, 5.1, 7.1, 8.4, 8.5_

- [x] 10. Implement security and configuration
  - [x] 10.1 Implement secure credential retrieval
    - Integrate with AWS Secrets Manager for API credentials
    - Implement credential caching with expiration
    - _Requirements: 12.1_

  - [x] 10.2 Implement input validation and sanitization
    - Validate all user inputs
    - Sanitize inputs to prevent injection attacks
    - _Requirements: 12.4_

  - [x] 10.3 Implement logging with sensitive data filtering
    - Configure logging to exclude API keys and secrets
    - Implement log message sanitization
    - _Requirements: 12.5_

  - [ ]* 10.4 Write unit tests for security features
    - Test credential retrieval from Secrets Manager
    - Test input validation
    - Test that sensitive data is not logged
    - _Requirements: 12.1, 12.4, 12.5_

- [x] 11. Final integration and documentation
  - [x] 11.1 Create usage examples and documentation
    - Document basic data ingestion example
    - Document complete workflow example
    - Document nested JSON handling example
    - Document error handling example
    - Document schema inference output example
    - _Requirements: All requirements_

  - [x] 11.2 Wire all components together
    - Ensure all components are properly integrated
    - Verify error handling flows between components
    - Validate configuration management across components
    - _Requirements: All requirements_

  - [ ]* 11.3 Write end-to-end integration tests
    - Test complete workflow with real BitoPro API sandbox
    - Test all error scenarios
    - Test performance with large datasets
    - _Requirements: All requirements_

- [x] 12. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties using Hypothesis
- Unit tests validate specific examples and edge cases
- The implementation uses Python as specified in the design document
- All components follow fault-tolerant design principles
- Security is integrated throughout (HTTPS, Secrets Manager, encryption)
