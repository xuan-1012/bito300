# Requirements Document: Explainability Module

## Introduction

可解釋性模組 (Explainability Module) 是加密貨幣可疑帳號偵測系統的關鍵元件，負責將風險評估結果轉換為人類可讀、可展示、可操作的解釋。本模組支援單筆帳號解釋與批次帳號解釋，產出包含風險原因、貢獻特徵、自然語言摘要等多種格式的輸出，滿足不同使用場景（UI 展示、報告產生、稽核追蹤）的需求。

核心價值主張：
- 可讀性：將技術指標轉換為業務人員可理解的自然語言
- 可展示性：提供 UI 友善的簡短摘要與結構化資料
- 可追溯性：記錄完整的判斷依據與特徵貢獻度
- 彈性支援：同時支援 AI 模型解釋與規則引擎解釋

## Glossary

- **Explainability_Module**: 可解釋性模組，負責產生風險評估的解釋
- **Risk_Assessment**: 風險評估結果，包含風險分數、等級、因子等資訊
- **Explanation**: 解釋物件，包含判斷原因、特徵貢獻、自然語言摘要
- **Feature_Contribution**: 特徵貢獻度，表示每個特徵對風險分數的影響程度
- **Reason_Code**: 原因代碼，標準化的風險因子識別碼
- **Natural_Language_Summary**: 自然語言摘要，人類可讀的風險解釋
- **Top_Contributing_Features**: 最高貢獻特徵，對風險分數影響最大的前 N 個特徵
- **Explanation_Generator**: 解釋產生器，負責建構解釋物件
- **Rule_Explainer**: 規則解釋器，解釋規則引擎的判斷邏輯
- **Model_Explainer**: 模型解釋器，解釋 AI 模型的判斷邏輯
- **UI_Formatter**: UI 格式化器，產生 UI 友善的簡短摘要
- **Report_Formatter**: 報告格式化器，產生完整的報告格式
- **Bedrock_LLM**: Amazon Bedrock 語言模型，用於產生自然語言解釋
- **SHAP_Values**: SHAP 值，用於解釋模型預測的特徵重要性

## Requirements

### Requirement 1: Single Account Explanation Generation

**User Story:** As a fraud analyst, I want to view a detailed explanation for a single suspicious account, so that I can understand why it was flagged and decide on further actions.

#### Acceptance Criteria

1. WHEN the Explainability_Module receives a Risk_Assessment for a single account, THE System SHALL extract the account_id, risk_score, risk_level, and risk_factors
2. WHEN extracting risk information, THE System SHALL validate that risk_score is between 0 and 100
3. WHEN the Risk_Assessment includes feature data, THE System SHALL calculate Feature_Contribution for each feature
4. WHEN calculating Feature_Contribution, THE System SHALL normalize contribution values to sum to 1.0
5. WHEN the Risk_Assessment is from a rule-based system, THE System SHALL identify which rules were triggered and their score contributions
6. WHEN the Risk_Assessment is from an AI model, THE System SHALL extract feature importance or SHAP_Values if available
7. WHEN generating the explanation, THE System SHALL identify Top_Contributing_Features sorted by contribution in descending order
8. WHEN generating the explanation, THE System SHALL assign Reason_Code for each identified risk factor
9. WHEN the explanation is complete, THE System SHALL return an Explanation object containing all extracted information

### Requirement 2: Natural Language Explanation Generation

**User Story:** As a compliance officer, I want to read a natural language explanation of why an account is suspicious, so that I can communicate findings to non-technical stakeholders.

#### Acceptance Criteria

1. WHEN the Explainability_Module generates an explanation, THE System SHALL create a Natural_Language_Summary describing the risk assessment
2. WHEN the risk_level is CRITICAL, THE System SHALL include urgent language in the Natural_Language_Summary
3. WHEN the risk_level is HIGH, THE System SHALL include warning language in the Natural_Language_Summary
4. WHEN the risk_level is MEDIUM, THE System SHALL include cautionary language in the Natural_Language_Summary
5. WHEN the risk_level is LOW, THE System SHALL include reassuring language in the Natural_Language_Summary
6. WHEN Top_Contributing_Features are identified, THE System SHALL mention the top 3 features in the Natural_Language_Summary
7. WHEN using Bedrock_LLM for explanation generation, THE System SHALL construct a prompt including risk_score, risk_factors, and feature values
8. WHEN Bedrock_LLM returns a response, THE System SHALL extract the natural language explanation text
9. IF Bedrock_LLM is unavailable, THEN THE System SHALL use template-based natural language generation

### Requirement 3: Feature Contribution Calculation

**User Story:** As a data scientist, I want to see which features contributed most to the risk score, so that I can validate the model behavior and identify key risk indicators.

#### Acceptance Criteria

1. WHEN the Risk_Assessment includes feature importance data, THE System SHALL use those values as Feature_Contribution
2. WHEN the Risk_Assessment includes SHAP_Values, THE System SHALL convert SHAP values to Feature_Contribution percentages
3. WHEN the Risk_Assessment is from a rule-based system, THE System SHALL calculate Feature_Contribution based on rule weights
4. WHEN calculating rule-based Feature_Contribution, THE System SHALL assign contribution proportional to the score added by each triggered rule
5. WHEN Feature_Contribution values are calculated, THE System SHALL normalize them to sum to 1.0
6. WHEN Feature_Contribution values are normalized, THE System SHALL validate that all values are between 0 and 1
7. WHEN identifying Top_Contributing_Features, THE System SHALL select features with contribution greater than 0.05
8. WHEN no features exceed the 0.05 threshold, THE System SHALL select the top 5 features by contribution

### Requirement 4: Reason Code Assignment

**User Story:** As a system administrator, I want standardized reason codes for risk factors, so that I can categorize and track suspicious patterns consistently.

#### Acceptance Criteria

1. THE System SHALL define a standard set of Reason_Code values for common risk factors
2. WHEN a risk factor indicates high transaction volume, THE System SHALL assign Reason_Code "HIGH_VOLUME"
3. WHEN a risk factor indicates night transactions, THE System SHALL assign Reason_Code "NIGHT_ACTIVITY"
4. WHEN a risk factor indicates round number amounts, THE System SHALL assign Reason_Code "ROUND_AMOUNTS"
5. WHEN a risk factor indicates high counterparty concentration, THE System SHALL assign Reason_Code "HIGH_CONCENTRATION"
6. WHEN a risk factor indicates rapid transactions, THE System SHALL assign Reason_Code "RAPID_TRANSACTIONS"
7. WHEN a risk factor indicates high velocity, THE System SHALL assign Reason_Code "HIGH_VELOCITY"
8. WHEN a risk factor does not match predefined patterns, THE System SHALL assign Reason_Code "OTHER"
9. WHEN assigning Reason_Code, THE System SHALL include the code in the Explanation object

### Requirement 5: UI-Friendly Short Summary

**User Story:** As a UI developer, I want a short, formatted summary suitable for display in the user interface, so that users can quickly understand the risk without reading lengthy explanations.

#### Acceptance Criteria

1. WHEN the UI_Formatter generates a summary, THE System SHALL limit the text to 200 characters or fewer
2. WHEN the risk_level is CRITICAL, THE System SHALL prefix the summary with "🚨 CRITICAL:"
3. WHEN the risk_level is HIGH, THE System SHALL prefix the summary with "⚠️ HIGH RISK:"
4. WHEN the risk_level is MEDIUM, THE System SHALL prefix the summary with "⚡ MEDIUM RISK:"
5. WHEN the risk_level is LOW, THE System SHALL prefix the summary with "✓ LOW RISK:"
6. WHEN generating the short summary, THE System SHALL mention the primary risk factor
7. WHEN generating the short summary, THE System SHALL include the risk_score value
8. WHEN the summary exceeds 200 characters, THE System SHALL truncate and append "..."

### Requirement 6: Batch Account Explanation Generation

**User Story:** As a fraud analyst, I want to generate explanations for multiple accounts in batch, so that I can efficiently review a large number of flagged accounts.

#### Acceptance Criteria

1. WHEN the Explainability_Module receives a list of Risk_Assessment objects, THE System SHALL process each assessment sequentially
2. WHEN processing batch explanations, THE System SHALL generate an Explanation object for each Risk_Assessment
3. WHEN generating batch explanations, THE System SHALL maintain the order of input Risk_Assessment objects
4. WHEN batch processing encounters an error for one account, THE System SHALL log the error and continue processing remaining accounts
5. WHEN batch processing completes, THE System SHALL return a list of Explanation objects
6. WHEN batch processing completes, THE System SHALL include a summary indicating the number of successful and failed explanations
7. WHEN using Bedrock_LLM for batch processing, THE System SHALL apply rate limiting to ensure less than 1 request per second

### Requirement 7: Rule-Based Explanation Decomposition

**User Story:** As a compliance officer, I want to see which specific rules were triggered and their individual contributions, so that I can understand the rule-based scoring logic.

#### Acceptance Criteria

1. WHEN the Risk_Assessment is from a rule-based system, THE Rule_Explainer SHALL identify all triggered rules
2. WHEN a rule is triggered, THE Rule_Explainer SHALL extract the rule name, score contribution, and trigger condition
3. WHEN extracting rule information, THE Rule_Explainer SHALL calculate the percentage contribution of each rule to the total risk_score
4. WHEN multiple rules are triggered, THE Rule_Explainer SHALL sort rules by score contribution in descending order
5. WHEN generating the explanation, THE Rule_Explainer SHALL include a list of triggered rules with their contributions
6. WHEN a rule contributes more than 20% of the total score, THE Rule_Explainer SHALL mark it as a major contributor
7. WHEN generating Natural_Language_Summary for rule-based assessments, THE System SHALL mention the top 2 triggered rules

### Requirement 8: AI Model Explanation with Bedrock

**User Story:** As a fraud analyst, I want AI-generated natural language explanations for model predictions, so that I can understand complex risk patterns in plain language.

#### Acceptance Criteria

1. WHEN the Risk_Assessment is from an AI model, THE Model_Explainer SHALL use Bedrock_LLM to generate natural language explanations
2. WHEN constructing the Bedrock prompt, THE Model_Explainer SHALL include risk_score, risk_level, risk_factors, and top feature values
3. WHEN calling Bedrock_LLM, THE System SHALL use a temperature setting of 0.3 for consistent explanations
4. WHEN calling Bedrock_LLM, THE System SHALL limit the response to 500 tokens
5. WHEN Bedrock_LLM returns a response, THE System SHALL extract the explanation text and validate it is non-empty
6. WHEN Bedrock_LLM returns a response, THE System SHALL include the explanation in the Natural_Language_Summary field
7. IF Bedrock_LLM fails or times out, THEN THE System SHALL fall back to template-based explanation generation
8. WHEN using Bedrock_LLM, THE System SHALL apply rate limiting to ensure less than 1 request per second

### Requirement 9: Explanation Output Formats

**User Story:** As a system integrator, I want explanations available in multiple formats, so that I can use them in different contexts (UI, reports, APIs, logs).

#### Acceptance Criteria

1. THE System SHALL provide explanation output in JSON format
2. THE System SHALL provide explanation output in plain text format
3. THE System SHALL provide explanation output in HTML format for reports
4. WHEN generating JSON format, THE System SHALL include all fields: account_id, risk_score, risk_level, reason_codes, top_features, natural_language_summary, and feature_contributions
5. WHEN generating plain text format, THE System SHALL format the explanation as human-readable paragraphs
6. WHEN generating HTML format, THE System SHALL include styled sections for risk level, reason codes, and feature contributions
7. WHEN generating HTML format, THE System SHALL use color coding for risk levels (red for CRITICAL, orange for HIGH, yellow for MEDIUM, green for LOW)
8. WHEN generating any format, THE System SHALL ensure all text is properly escaped to prevent injection attacks

### Requirement 10: Explanation Persistence and Retrieval

**User Story:** As a compliance officer, I want explanations stored and retrievable for audit purposes, so that I can review historical risk assessments and their justifications.

#### Acceptance Criteria

1. WHEN an Explanation is generated, THE System SHALL store it to S3 with path pattern `explanations/{account_id}/{timestamp}.json`
2. WHEN storing to S3, THE System SHALL use server-side encryption with AES-256
3. WHEN an Explanation is generated, THE System SHALL store a reference in DynamoDB with account_id as partition key and timestamp as sort key
4. WHEN storing to DynamoDB, THE System SHALL include fields: account_id, timestamp, risk_score, risk_level, reason_codes, and s3_uri
5. WHEN retrieving an explanation by account_id, THE System SHALL query DynamoDB and return the most recent explanation
6. WHEN retrieving explanations for a time range, THE System SHALL query DynamoDB using the timestamp sort key
7. WHEN retrieving an explanation, THE System SHALL fetch the full explanation data from S3 using the stored s3_uri

### Requirement 11: Template-Based Fallback Explanation

**User Story:** As a system administrator, I want a reliable fallback explanation mechanism, so that the system continues to provide explanations even when AI services are unavailable.

#### Acceptance Criteria

1. WHEN Bedrock_LLM is unavailable, THE System SHALL use template-based Natural_Language_Summary generation
2. WHEN using template-based generation, THE System SHALL select a template based on risk_level
3. WHEN using template-based generation for CRITICAL risk, THE System SHALL use the template: "This account shows critical risk (score: {score}) due to {primary_factor}. Immediate review recommended."
4. WHEN using template-based generation for HIGH risk, THE System SHALL use the template: "This account shows high risk (score: {score}) primarily due to {primary_factor}. Review recommended."
5. WHEN using template-based generation for MEDIUM risk, THE System SHALL use the template: "This account shows moderate risk (score: {score}) with {primary_factor} as the main concern."
6. WHEN using template-based generation for LOW risk, THE System SHALL use the template: "This account shows low risk (score: {score}) with normal activity patterns."
7. WHEN using templates, THE System SHALL substitute placeholders with actual values from the Risk_Assessment
8. WHEN template-based generation is used, THE System SHALL set a flag indicating fallback mode in the Explanation object

### Requirement 12: Feature Value Contextualization

**User Story:** As a fraud analyst, I want to see not just feature values but also context about whether they are normal or abnormal, so that I can better assess the risk.

#### Acceptance Criteria

1. WHEN the Explainability_Module processes a feature value, THE System SHALL compare it against predefined thresholds
2. WHEN total_volume exceeds $100,000, THE System SHALL mark it as "significantly above normal"
3. WHEN night_transaction_ratio exceeds 0.3, THE System SHALL mark it as "unusually high"
4. WHEN round_number_ratio exceeds 0.5, THE System SHALL mark it as "suspicious pattern detected"
5. WHEN concentration_score exceeds 0.7, THE System SHALL mark it as "highly concentrated"
6. WHEN rapid_transaction_count exceeds 10, THE System SHALL mark it as "abnormally frequent"
7. WHEN velocity_score exceeds 10, THE System SHALL mark it as "extremely high velocity"
8. WHEN a feature value is within normal range, THE System SHALL mark it as "within normal range"
9. WHEN generating Natural_Language_Summary, THE System SHALL include contextualization for Top_Contributing_Features

### Requirement 13: Explanation Validation and Quality Assurance

**User Story:** As a quality assurance engineer, I want all generated explanations to be validated for completeness and correctness, so that users receive reliable and accurate information.

#### Acceptance Criteria

1. WHEN an Explanation is generated, THE System SHALL validate that account_id is non-empty
2. WHEN an Explanation is generated, THE System SHALL validate that risk_score is between 0 and 100
3. WHEN an Explanation is generated, THE System SHALL validate that risk_level matches the risk_score range
4. WHEN an Explanation is generated, THE System SHALL validate that Natural_Language_Summary is non-empty and at least 20 characters long
5. WHEN an Explanation is generated, THE System SHALL validate that at least one Reason_Code is assigned
6. WHEN an Explanation is generated, THE System SHALL validate that Feature_Contribution values sum to 1.0 within a tolerance of 0.01
7. IF any validation fails, THEN THE System SHALL log the validation error and raise an exception
8. WHEN validation completes successfully, THE System SHALL mark the Explanation as validated

### Requirement 14: Multilingual Explanation Support

**User Story:** As an international user, I want explanations available in my preferred language, so that I can understand risk assessments in my native language.

#### Acceptance Criteria

1. THE System SHALL support Natural_Language_Summary generation in English and Traditional Chinese
2. WHEN generating an explanation, THE System SHALL accept a language parameter with values "en" or "zh-TW"
3. WHEN the language parameter is "en", THE System SHALL generate Natural_Language_Summary in English
4. WHEN the language parameter is "zh-TW", THE System SHALL generate Natural_Language_Summary in Traditional Chinese
5. WHEN using Bedrock_LLM for multilingual explanations, THE System SHALL include language instructions in the prompt
6. WHEN using template-based generation, THE System SHALL select templates in the requested language
7. WHEN the requested language is not supported, THE System SHALL default to English and log a warning
8. WHEN generating Reason_Code values, THE System SHALL keep them in English regardless of language setting

### Requirement 15: Explanation Performance and Scalability

**User Story:** As a system architect, I want explanation generation to be fast and scalable, so that it does not become a bottleneck in the risk assessment pipeline.

#### Acceptance Criteria

1. WHEN generating a single explanation without Bedrock_LLM, THE System SHALL complete in less than 100 milliseconds
2. WHEN generating a single explanation with Bedrock_LLM, THE System SHALL complete in less than 2 seconds
3. WHEN processing batch explanations, THE System SHALL support concurrent processing of up to 10 accounts
4. WHEN using Bedrock_LLM for batch processing, THE System SHALL apply rate limiting to maintain less than 1 request per second
5. WHEN generating explanations, THE System SHALL cache template strings to avoid repeated parsing
6. WHEN calculating Feature_Contribution, THE System SHALL use vectorized operations where possible for efficiency
7. WHEN storing explanations to S3, THE System SHALL use batch operations for multiple accounts

### Requirement 16: Explanation Audit Trail

**User Story:** As a compliance officer, I want a complete audit trail of all generated explanations, so that I can demonstrate regulatory compliance and track system behavior over time.

#### Acceptance Criteria

1. WHEN an Explanation is generated, THE System SHALL log the generation event to CloudWatch with timestamp and account_id
2. WHEN an Explanation is generated, THE System SHALL record whether Bedrock_LLM or template-based generation was used
3. WHEN an Explanation is generated, THE System SHALL record the generation time in milliseconds
4. WHEN an Explanation is stored, THE System SHALL record the S3 URI and DynamoDB key in the audit log
5. WHEN Bedrock_LLM is used, THE System SHALL log the model_id and token count
6. WHEN template-based fallback is used, THE System SHALL log the reason for fallback
7. THE System SHALL not log sensitive information such as account identifiers or transaction amounts in CloudWatch
8. WHEN audit logs are written, THE System SHALL ensure they are retained for at least 90 days

