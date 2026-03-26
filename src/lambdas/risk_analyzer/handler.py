"""
Risk Analyzer Lambda Handler

Analyzes cryptocurrency account risk using AWS Bedrock (Claude) with rate limiting,
and falls back to rule-based scoring when Bedrock is unavailable.

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 5.1, 5.2,
              6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9
"""

import json
import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

from src.common.models import TransactionFeatures, RiskAssessment, RiskLevel
from src.common.validators import validate_features, validate_risk_assessment
from src.common.rate_limiter import RateLimiter
from src.common.aws_clients import get_aws_clients

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Bedrock model ID
BEDROCK_MODEL_ID = "anthropic.claude-3-sonnet-20240229-v1:0"

# Task 6.1: Bedrock prompt template
# Requirements: 4.1
RISK_ANALYSIS_PROMPT = """You are a cryptocurrency fraud detection expert. Analyze the following account features and provide a risk assessment.

Account Features:
- Total Volume: {total_volume} USD
- Transaction Count: {transaction_count}
- Average Transaction Size: {avg_transaction_size} USD
- Max Transaction Size: {max_transaction_size} USD
- Unique Counterparties: {unique_counterparties}
- Night Transaction Ratio: {night_transaction_ratio:.2%}
- Rapid Transaction Count: {rapid_transaction_count}
- Round Number Ratio: {round_number_ratio:.2%}
- Concentration Score: {concentration_score:.4f}
- Velocity Score: {velocity_score:.2f} transactions/hour

Provide your assessment in the following JSON format:
{{
  "risk_score": <integer 0-100>,
  "risk_level": "<low|medium|high|critical>",
  "risk_factors": ["factor1", "factor2", ...],
  "explanation": "Detailed explanation of the risk assessment",
  "confidence": <float 0.0-1.0>
}}

Respond with only the JSON object, no additional text."""


# Task 6.2: Bedrock risk analysis function
# Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 5.1, 5.2
def analyze_risk_with_bedrock(
    features: TransactionFeatures,
    rate_limiter: RateLimiter,
    bedrock_client=None
) -> RiskAssessment:
    """
    Analyze account risk using Amazon Bedrock (Claude) with rate limiting.

    Builds a structured prompt from the account features, calls the Bedrock API
    while respecting the rate limit (< 1 req/sec), then parses and validates the
    LLM response.

    Args:
        features: Extracted transaction features for the account.
        rate_limiter: RateLimiter instance to enforce < 1 req/sec.
        bedrock_client: Optional pre-initialized Bedrock Runtime client.
                        If None, the shared AWSClients singleton is used.

    Returns:
        RiskAssessment with risk_score, risk_level, risk_factors, explanation,
        and confidence populated from the LLM response.

    Raises:
        Falls back to fallback_risk_scoring() on any Bedrock error.
    """
    assert validate_features(features), f"Invalid features for account {features.account_id}"

    # Build prompt from template (Requirement 4.1)
    prompt = RISK_ANALYSIS_PROMPT.format(
        total_volume=features.total_volume,
        transaction_count=features.transaction_count,
        avg_transaction_size=features.avg_transaction_size,
        max_transaction_size=features.max_transaction_size,
        unique_counterparties=features.unique_counterparties,
        night_transaction_ratio=features.night_transaction_ratio,
        rapid_transaction_count=features.rapid_transaction_count,
        round_number_ratio=features.round_number_ratio,
        concentration_score=features.concentration_score,
        velocity_score=features.velocity_score,
    )

    # Enforce rate limit before calling Bedrock (Requirements 4.2, 5.1, 5.2)
    rate_limiter.wait_if_needed()

    if bedrock_client is None:
        bedrock_client = get_aws_clients().bedrock_runtime

    try:
        response = bedrock_client.invoke_model(
            modelId=BEDROCK_MODEL_ID,
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1024,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            }),
        )

        response_body = json.loads(response["body"].read())
        llm_output = response_body["content"][0]["text"]
        logger.info(f"Bedrock response received for account {features.account_id}")

        # Parse and validate LLM response (Requirements 4.3, 4.4, 4.5)
        risk_data = _parse_llm_response(llm_output)

        assessment = RiskAssessment(
            account_id=features.account_id,
            risk_score=risk_data["risk_score"],
            risk_level=RiskLevel(risk_data["risk_level"]),
            risk_factors=risk_data["risk_factors"],
            explanation=risk_data["explanation"],
            confidence=risk_data["confidence"],
            timestamp=datetime.now(),
        )

        assert validate_risk_assessment(assessment), (
            f"Invalid risk assessment for account {features.account_id}"
        )
        return assessment

    except Exception as e:
        logger.warning(
            f"Bedrock analysis failed for account {features.account_id}: {e}. "
            "Falling back to rule-based scoring."
        )
        return fallback_risk_scoring(features)


def _parse_llm_response(response_text: str) -> Dict[str, Any]:
    """
    Extract and validate the JSON risk assessment from the LLM response text.

    Args:
        response_text: Raw text returned by the LLM.

    Returns:
        Dictionary with keys: risk_score, risk_level, risk_factors,
        explanation, confidence.

    Raises:
        ValueError: If the JSON cannot be parsed or required fields are invalid.
    """
    # Extract JSON block (handles cases where the model adds surrounding text)
    json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if not json_match:
        raise ValueError(f"No JSON object found in LLM response: {response_text!r}")

    risk_data = json.loads(json_match.group())

    # Validate required fields
    required_keys = {"risk_score", "risk_level", "risk_factors", "explanation", "confidence"}
    missing = required_keys - risk_data.keys()
    if missing:
        raise ValueError(f"LLM response missing required fields: {missing}")

    # Requirement 4.4: risk_score must be in [0, 100]
    risk_score = float(risk_data["risk_score"])
    if not 0 <= risk_score <= 100:
        raise ValueError(f"risk_score {risk_score} is not in [0, 100]")
    risk_data["risk_score"] = risk_score

    # Requirement 4.5: risk_level must match risk_score range
    risk_level_str = str(risk_data["risk_level"]).lower()
    valid_levels = {rl.value for rl in RiskLevel}
    if risk_level_str not in valid_levels:
        raise ValueError(f"Invalid risk_level '{risk_level_str}'")

    expected_level = RiskLevel.from_score(risk_score)
    if risk_level_str != expected_level.value:
        logger.warning(
            f"LLM risk_level '{risk_level_str}' does not match score {risk_score} "
            f"(expected '{expected_level.value}'). Correcting."
        )
        risk_data["risk_level"] = expected_level.value
    else:
        risk_data["risk_level"] = risk_level_str

    # Validate risk_factors is a non-empty list
    if not isinstance(risk_data["risk_factors"], list) or not risk_data["risk_factors"]:
        raise ValueError("risk_factors must be a non-empty list")

    # Validate confidence is in [0, 1]
    confidence = float(risk_data["confidence"])
    if not 0 <= confidence <= 1:
        raise ValueError(f"confidence {confidence} is not in [0, 1]")
    risk_data["confidence"] = confidence

    return risk_data


# Task 6.3: Fallback rule-based scoring
# Requirements: 4.6, 4.8, 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 6.8, 6.9
def fallback_risk_scoring(features: TransactionFeatures) -> RiskAssessment:
    """
    Rule-based risk scoring used when Bedrock is unavailable.

    Applies threshold-based rules to compute a risk score, determines the
    corresponding risk level, and returns a RiskAssessment with confidence 0.7
    to indicate lower certainty compared to AI-driven analysis.

    Scoring rules (Requirements 6.1 – 6.7):
        - total_volume > 100,000          → +20 pts  (Req 6.2)
        - night_transaction_ratio > 0.3   → +15 pts  (Req 6.3)
        - round_number_ratio > 0.5        → +20 pts  (Req 6.4)
        - concentration_score > 0.7       → +15 pts  (Req 6.5)
        - rapid_transaction_count > 10    → +15 pts  (Req 6.6)
        - velocity_score > 10             → +15 pts  (Req 6.7)
        - Score capped at 100             (Req 6.8)

    Risk level ranges (Requirement 7.1 – 7.5):
        - LOW:      0 – 25
        - MEDIUM:  26 – 50
        - HIGH:    51 – 75
        - CRITICAL: 76 – 100

    Args:
        features: Extracted transaction features for the account.

    Returns:
        RiskAssessment with confidence=0.7 (Requirement 4.8 / 6.9).
    """
    risk_score = 0.0
    risk_factors: List[str] = []

    # Requirement 6.2: High transaction volume
    if features.total_volume > 100_000:
        risk_score += 20
        risk_factors.append("High transaction volume")

    # Requirement 6.3: Frequent night transactions
    if features.night_transaction_ratio > 0.3:
        risk_score += 15
        risk_factors.append("Frequent night transactions")

    # Requirement 6.4: Suspicious round number amounts
    if features.round_number_ratio > 0.5:
        risk_score += 20
        risk_factors.append("Suspicious round number amounts")

    # Requirement 6.5: High counterparty concentration
    if features.concentration_score > 0.7:
        risk_score += 15
        risk_factors.append("High counterparty concentration")

    # Requirement 6.6: Rapid successive transactions
    if features.rapid_transaction_count > 10:
        risk_score += 15
        risk_factors.append("Rapid successive transactions")

    # Requirement 6.7: High transaction velocity
    if features.velocity_score > 10:
        risk_score += 15
        risk_factors.append("High transaction velocity")

    # Requirement 6.8: Cap at 100
    risk_score = min(risk_score, 100.0)

    # Determine risk level from score (Requirements 7.1 – 7.5)
    risk_level = RiskLevel.from_score(risk_score)

    # Provide a default risk factor when no rules triggered
    if not risk_factors:
        risk_factors = ["No significant risk indicators detected"]

    explanation = (
        f"Rule-based assessment identified {len(risk_factors)} risk factor(s): "
        + ", ".join(risk_factors)
        + "."
    )

    # Requirement 4.8 / 6.9: Lower confidence for fallback scoring
    return RiskAssessment(
        account_id=features.account_id,
        risk_score=risk_score,
        risk_level=risk_level,
        risk_factors=risk_factors,
        explanation=explanation,
        confidence=0.7,
        timestamp=datetime.now(),
    )


def _parse_s3_uri(s3_uri: str) -> Tuple[str, str]:
    """
    Parse an S3 URI into bucket and key components.

    Args:
        s3_uri: S3 URI in the format s3://bucket/key

    Returns:
        Tuple of (bucket, key)

    Raises:
        ValueError: If the URI format is invalid
    """
    if not s3_uri.startswith("s3://"):
        raise ValueError(f"Invalid S3 URI: {s3_uri}")
    path = s3_uri[len("s3://"):]
    bucket, _, key = path.partition("/")
    if not bucket or not key:
        raise ValueError(f"Invalid S3 URI (missing bucket or key): {s3_uri}")
    return bucket, key


def _read_features_from_s3(aws_clients, s3_uri: str) -> List[Dict[str, Any]]:
    """
    Read extracted features JSON from S3.

    Args:
        aws_clients: AWSClients instance
        s3_uri: S3 URI of the features data

    Returns:
        List of feature dictionaries
    """
    bucket, key = _parse_s3_uri(s3_uri)
    logger.info(f"Reading features from s3://{bucket}/{key}")
    response = aws_clients.s3.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read().decode("utf-8")
    return json.loads(body)


def _dict_to_transaction_features(raw: Dict[str, Any]) -> Optional[TransactionFeatures]:
    """
    Convert a raw feature dictionary to a TransactionFeatures object.

    Returns None if conversion fails.
    """
    try:
        return TransactionFeatures(
            account_id=raw["account_id"],
            total_volume=float(raw["total_volume"]),
            transaction_count=int(raw["transaction_count"]),
            avg_transaction_size=float(raw["avg_transaction_size"]),
            max_transaction_size=float(raw["max_transaction_size"]),
            unique_counterparties=int(raw["unique_counterparties"]),
            night_transaction_ratio=float(raw["night_transaction_ratio"]),
            rapid_transaction_count=int(raw["rapid_transaction_count"]),
            round_number_ratio=float(raw["round_number_ratio"]),
            concentration_score=float(raw["concentration_score"]),
            velocity_score=float(raw["velocity_score"]),
        )
    except Exception as e:
        logger.error(f"Failed to convert feature dict to TransactionFeatures: {e}")
        return None


def _store_risk_assessments_to_s3(
    aws_clients,
    bucket: str,
    key: str,
    assessments: List[Dict[str, Any]],
) -> str:
    """
    Store risk assessments to S3 with AES256 server-side encryption.

    Requirements: 9.3, 9.6

    Args:
        aws_clients: AWSClients instance
        bucket: S3 bucket name
        key: S3 object key
        assessments: List of risk assessment dictionaries

    Returns:
        S3 URI of stored assessments
    """
    json_data = json.dumps(assessments, default=str, indent=2)
    aws_clients.s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json_data,
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )
    s3_uri = f"s3://{bucket}/{key}"
    logger.info(f"Stored risk assessments to {s3_uri}")
    return s3_uri


def _store_assessment_to_dynamodb(aws_clients, table_name: str, assessment: RiskAssessment) -> None:
    """
    Store a single risk assessment to DynamoDB with account_id as partition key.

    Requirements: 4.7, 9.5

    Args:
        aws_clients: AWSClients instance
        table_name: DynamoDB table name
        assessment: RiskAssessment to store
    """
    table = aws_clients.dynamodb.Table(table_name)
    table.put_item(
        Item={
            "account_id": assessment.account_id,
            "risk_score": str(assessment.risk_score),
            "risk_level": assessment.risk_level.value,
            "risk_factors": assessment.risk_factors,
            "explanation": assessment.explanation,
            "confidence": str(assessment.confidence),
            "timestamp": assessment.timestamp.isoformat(),
        }
    )


def lambda_handler(event, context):
    """
    Lambda handler for analyzing risk using Bedrock.

    Reads extracted features from S3, analyzes risk for each account using
    Amazon Bedrock (with rate limiting), stores results to S3 and DynamoDB,
    and logs Bedrock API call counts.

    Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 5.1, 5.2, 5.3,
                  9.3, 9.5, 11.3, 11.4, 13.1, 13.5

    Args:
        event: Lambda event containing:
            - s3_uri: S3 URI of extracted features (or nested under 'body')
        context: Lambda context

    Returns:
        dict: Response with S3 URI of risk assessments
    """
    # Requirement 13.1: Log start time
    start_execution = datetime.now()
    logger.info(f"Risk Analyzer Lambda invoked at {start_execution.isoformat()}")
    logger.info(f"Event: {json.dumps(event, default=str)}")

    try:
        # Resolve s3_uri from event (may be top-level or nested in 'body')
        s3_uri = event.get("s3_uri")
        if not s3_uri:
            body = event.get("body", {})
            if isinstance(body, str):
                body = json.loads(body)
            s3_uri = body.get("s3_uri")

        if not s3_uri:
            raise ValueError("s3_uri not found in event")

        aws_clients = get_aws_clients()

        # Read features from S3
        raw_features_list = _read_features_from_s3(aws_clients, s3_uri)
        logger.info(f"Read features for {len(raw_features_list)} accounts from S3")

        # Requirement 5.1, 5.2: Initialize rate limiter (< 1 req/sec)
        rate_limiter = RateLimiter(max_requests_per_second=0.9)

        # Analyze risk for each account
        assessments_output: List[Dict[str, Any]] = []
        bedrock_call_count = 0
        fallback_call_count = 0
        skipped_accounts = 0

        table_name = os.environ.get("DYNAMODB_TABLE", "crypto-detection-accounts")

        for raw_features in raw_features_list:
            account_id = raw_features.get("account_id", "unknown")
            try:
                features = _dict_to_transaction_features(raw_features)
                if features is None:
                    logger.error(f"Failed to parse features for account, skipping")
                    skipped_accounts += 1
                    continue

                # Analyze risk with Bedrock (rate limited); falls back internally on error
                assessment = analyze_risk_with_bedrock(
                    features=features,
                    rate_limiter=rate_limiter,
                )

                # Track whether Bedrock or fallback was used (confidence < 1.0 for fallback)
                # Fallback always sets confidence=0.7; Bedrock responses typically differ
                if assessment.confidence == 0.7 and assessment.explanation.startswith("Rule-based"):
                    fallback_call_count += 1
                else:
                    bedrock_call_count += 1

                # Requirement 4.7 / 9.5: Store to DynamoDB
                try:
                    _store_assessment_to_dynamodb(aws_clients, table_name, assessment)
                except Exception as ddb_err:
                    logger.error(
                        f"Failed to store assessment to DynamoDB for account: {ddb_err}"
                    )

                assessments_output.append({
                    "account_id": assessment.account_id,
                    "risk_score": assessment.risk_score,
                    "risk_level": assessment.risk_level.value,
                    "risk_factors": assessment.risk_factors,
                    "explanation": assessment.explanation,
                    "confidence": assessment.confidence,
                    "timestamp": assessment.timestamp.isoformat(),
                })

            except Exception as e:
                logger.error(
                    f"Error analyzing risk for account: {e}", exc_info=True
                )
                skipped_accounts += 1

        # Requirement 13.5: Log number of accounts analyzed and Bedrock API call count
        analyzed_count = len(assessments_output)
        logger.info(
            f"Risk analysis complete: {analyzed_count} accounts analyzed, "
            f"{bedrock_call_count} Bedrock API calls, "
            f"{fallback_call_count} fallback scoring calls, "
            f"{skipped_accounts} accounts skipped"
        )
        # Requirement 5.3: Log wait times (already logged inside rate_limiter.wait_if_needed)
        logger.info(
            f"Rate limiter stats: {rate_limiter.get_request_count()} total requests tracked"
        )

        # Requirement 9.3: Store risk assessments to S3 with path risk-scores/{timestamp}.json
        bucket_name = os.environ.get("RISK_SCORES_BUCKET", "crypto-detection-risk-scores")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"risk-scores/{timestamp}.json"

        risk_scores_s3_uri = _store_risk_assessments_to_s3(
            aws_clients=aws_clients,
            bucket=bucket_name,
            key=s3_key,
            assessments=assessments_output,
        )

        # Requirement 13.1: Log end time
        end_execution = datetime.now()
        execution_duration = (end_execution - start_execution).total_seconds()
        logger.info(
            f"Risk Analyzer completed in {execution_duration:.2f}s. "
            f"Risk scores stored at {risk_scores_s3_uri}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "s3_uri": risk_scores_s3_uri,
                "accounts_analyzed": analyzed_count,
                "bedrock_api_calls": bedrock_call_count,
                "fallback_calls": fallback_call_count,
                "accounts_skipped": skipped_accounts,
                "execution_duration_seconds": execution_duration,
            }),
        }

    except Exception as e:
        logger.error(f"Unexpected error in Risk Analyzer: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal error",
                "message": str(e),
            }),
        }
