# Implementation Plan: Explainability Module

## Overview

Implement the Explainability Module under `src/explainability/` following the layered, class-based pattern of the existing codebase. The module transforms `RiskAssessment` objects into structured `Explanation` objects with natural language summaries, feature contributions, reason codes, and multi-format output. Tests live in `tests/unit/`, `tests/property/`, and `tests/integration/`.

## Tasks

- [x] 1. Create data models and constants
  - Create `src/explainability/__init__.py` and `src/explainability/models.py`
  - Define `FeatureContribution`, `RuleContribution`, `Explanation`, and `BatchResult` dataclasses
  - Define feature contextualization threshold constants and reason code mapping constants
  - _Requirements: 1.1, 3.1, 4.1, 6.6, 7.2, 9.4, 12.1_

- [x] 2. Implement FeatureContributionCalculator
  - [x] 2.1 Implement `src/explainability/feature_contribution.py`
    - Write `calculate()` to handle SHAP values, model feature importance, and rule weights
    - Write `get_top_features()` with 0.05 threshold and top-5 fallback
    - Write `contextualize()` to apply threshold labels from models.py constants
    - _Requirements: 1.3, 1.6, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 12.1–12.9_

  - [ ]* 2.2 Write property test for feature contribution normalization
    - **Property 1: Feature Contribution Normalization**
    - **Validates: Requirements 1.4, 3.5, 3.6**

  - [ ]* 2.3 Write property test for top feature selection threshold
    - **Property 4: Top Feature Selection Threshold**
    - **Validates: Requirements 3.7, 3.8**

  - [ ]* 2.4 Write property test for feature contextualization labels
    - **Property 15: Feature Contextualization Labels**
    - **Validates: Requirements 12.1–12.8**

- [x] 3. Implement ReasonCodeAssigner
  - [x] 3.1 Implement `src/explainability/reason_codes.py`
    - Write `assign()` to map risk factor strings to standardized `ReasonCode` values
    - Return `OTHER` for unrecognized patterns
    - _Requirements: 4.1–4.9_

  - [ ]* 3.2 Write property test for reason code completeness
    - **Property 3: Every Risk Factor Gets a Reason Code**
    - **Validates: Requirements 1.8, 4.2–4.9**

- [x] 4. Implement NaturalLanguageGenerator
  - [x] 4.1 Implement `src/explainability/nlg.py`
    - Write template-based generation for all four risk levels in English and Traditional Chinese
    - Write Bedrock LLM path with prompt construction (risk_score, risk_level, risk_factors, top features, language instruction)
    - Apply rate limiting (< 1 req/s) reusing `RateLimiter` from `src/common/`
    - Fall back to templates on Bedrock `ClientError`, timeout, or empty response; set `is_fallback=True`
    - _Requirements: 2.1–2.9, 8.1–8.8, 11.1–11.8, 14.1–14.8_

  - [ ]* 4.2 Write property test for template fallback produces non-empty summary
    - **Property 10: Template Fallback Produces Non-Empty Summary**
    - **Validates: Requirements 2.9, 11.1, 11.2, 11.7, 11.8**

  - [ ]* 4.3 Write property test for template substitution round trip
    - **Property 11: Template Substitution Round Trip**
    - **Validates: Requirements 11.3–11.7**

  - [ ]* 4.4 Write property test for Bedrock prompt contains required fields
    - **Property 17: Bedrock Prompt Contains Required Fields**
    - **Validates: Requirements 2.7, 8.2**

  - [ ]* 4.5 Write property test for multilingual language fallback
    - **Property 18: Multilingual Language Fallback**
    - **Validates: Requirements 14.7**

- [x] 5. Implement RuleExplainer
  - [x] 5.1 Implement rule decomposition logic in `src/explainability/rule_explainer.py`
    - Extract triggered rules, score contributions, and trigger conditions from rule-based `RiskAssessment`
    - Calculate percentage contribution per rule; mark rules with percentage > 0.20 as `is_major=True`
    - Sort rules by score contribution descending
    - _Requirements: 7.1–7.7_

  - [ ]* 5.2 Write property test for rule contribution percentages sum to 1.0
    - **Property 16: Rule Contribution Percentages Sum to 1.0**
    - **Validates: Requirements 7.3, 7.6**

- [x] 6. Implement OutputFormatters
  - [x] 6.1 Implement `src/explainability/formatters.py`
    - Write `to_json()` including all required fields
    - Write `to_text()` as human-readable paragraphs
    - Write `to_html()` with risk-level color coding and HTML-escaped content
    - Write `to_ui_summary()` with risk-level prefix, score, primary factor, and 200-char truncation
    - _Requirements: 5.1–5.8, 9.1–9.8_

  - [ ]* 6.2 Write property test for UI summary length constraint
    - **Property 5: UI Summary Length Constraint**
    - **Validates: Requirements 5.1, 5.8**

  - [ ]* 6.3 Write property test for UI summary risk level prefix
    - **Property 6: UI Summary Risk Level Prefix**
    - **Validates: Requirements 5.2–5.5**

  - [ ]* 6.4 Write property test for UI summary contains score and primary factor
    - **Property 7: UI Summary Contains Score and Primary Factor**
    - **Validates: Requirements 5.6, 5.7**

  - [ ]* 6.5 Write property test for JSON output contains all required fields
    - **Property 12: JSON Output Contains All Required Fields**
    - **Validates: Requirements 9.1, 9.4**

  - [ ]* 6.6 Write property test for output escaping prevents injection
    - **Property 13: Output Escaping Prevents Injection**
    - **Validates: Requirements 9.8**

- [x] 7. Implement ExplanationValidator
  - [x] 7.1 Implement `src/explainability/validator.py`
    - Define `ExplanationValidationError` custom exception
    - Write `validate()` checking all structural invariants: non-empty account_id, score in [0,100], risk_level matches score, summary >= 20 chars, at least one reason code, contributions sum to 1.0 ± 0.01
    - Mark `Explanation.is_validated = True` on success
    - _Requirements: 13.1–13.8_

  - [ ]* 7.2 Write property test for explanation validation invariants
    - **Property 14: Explanation Validation Invariants**
    - **Validates: Requirements 13.1–13.8**

- [x] 8. Implement ExplanationPersistence
  - [x] 8.1 Implement `src/explainability/persistence.py`
    - Write `store()` to save JSON to S3 at `explanations/{account_id}/{timestamp_iso}.json` with AES-256 SSE, reusing `S3Storage`
    - Write DynamoDB index write with required attributes (account_id, timestamp, risk_score, risk_level, reason_codes, s3_uri)
    - Write `get_latest()` querying DynamoDB by account_id and fetching from S3
    - Write `get_range()` querying DynamoDB with timestamp sort key range
    - Log S3 URI and DynamoDB key to CloudWatch audit log
    - _Requirements: 10.1–10.7, 16.4_

- [x] 9. Checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 10. Implement ExplainabilityModule orchestrator
  - [x] 10.1 Implement `src/explainability/explainability_module.py`
    - Wire `FeatureContributionCalculator`, `ReasonCodeAssigner`, `NaturalLanguageGenerator`, `RuleExplainer`, `OutputFormatters`, `ExplanationValidator`, and `ExplanationPersistence`
    - Implement `explain()`: validate risk_score range, compute contributions, assign reason codes, generate NLG, build `Explanation`, validate, persist, log to CloudWatch
    - Implement `explain_batch()`: iterate sequentially, catch per-account errors into `BatchResult.errors`, preserve input order, return `BatchResult` with counts
    - Apply rate limiting for Bedrock batch calls (< 1 req/s)
    - Log generation event, method used (Bedrock vs template), generation_time_ms, and model_id/token count to CloudWatch; do not log account identifiers or amounts
    - _Requirements: 1.1–1.9, 6.1–6.7, 8.1–8.8, 15.1–15.7, 16.1–16.8_

  - [ ]* 10.2 Write property test for top features sorted descending
    - **Property 2: Top Features Are Sorted Descending**
    - **Validates: Requirements 1.7, 7.4**

  - [ ]* 10.3 Write property test for batch output completeness and order
    - **Property 8: Batch Output Completeness and Order**
    - **Validates: Requirements 6.2, 6.3, 6.5, 6.6**

  - [ ]* 10.4 Write property test for batch resilience — single failure does not abort
    - **Property 9: Batch Resilience — Single Failure Does Not Abort**
    - **Validates: Requirements 6.4**

- [ ] 11. Write unit tests
  - [ ]* 11.1 Write unit tests in `tests/unit/test_explainability.py`
    - Test specific reason code mappings for all seven predefined codes and `OTHER`
    - Test template substitution for each risk level × language combination
    - Test HTML color coding for each risk level
    - Test Bedrock prompt construction with known inputs
    - Test DynamoDB/S3 key format
    - Test `RiskLevel` boundary values (0, 25, 26, 50, 51, 75, 76, 100)
    - Test validation error messages for each failure mode
    - _Requirements: 2.2–2.5, 4.2–4.8, 5.2–5.5, 8.3, 9.7, 11.3–11.6, 13.1–13.7, 14.3–14.6_

- [ ] 12. Write integration tests
  - [ ]* 12.1 Write integration tests in `tests/integration/test_explainability_workflow.py`
    - End-to-end: `RiskAssessment` → `explain()` → `Explanation` → `validate()`
    - Batch with one invalid assessment: verify `BatchResult` counts and error recording
    - Persistence round trip: `store()` then `get_latest()` by account_id
    - _Requirements: 1.1–1.9, 6.1–6.7, 10.1–10.7_

- [x] 13. Final checkpoint — Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- All property tests go in `tests/property/test_explainability_property.py` using Hypothesis `@given` with `@settings(max_examples=100)`
- Each property test must include a comment: `# Feature: explainability-module, Property N: <property_text>`
- Reuse `RateLimiter`, `S3Storage`, and `get_aws_clients()` from `src/common/` — do not reimplement
- CloudWatch audit logs must not contain account identifiers or transaction amounts (Requirement 16.7)
- Explanations are retained for at least 90 days per Requirement 16.8 (configure at infrastructure level)
