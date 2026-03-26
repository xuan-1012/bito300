"""
Persistence layer for the Explainability Module.

Stores Explanation objects to S3 (full JSON) and indexes them in DynamoDB
for fast retrieval by account_id and timestamp range.

Requirements: 10.1–10.7, 16.4
"""

import json
import logging
import os
from datetime import datetime
from typing import List

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from src.common.aws_clients import get_aws_clients
from src.common.models import RiskLevel
from src.explainability.formatters import OutputFormatters
from src.explainability.models import Explanation, FeatureContribution

logger = logging.getLogger(__name__)

# Environment-configurable resource names
_S3_BUCKET = os.environ.get("EXPLANATIONS_S3_BUCKET", "explanations-bucket")
_DYNAMODB_TABLE = os.environ.get("EXPLANATIONS_DYNAMODB_TABLE", "explanations")


class ExplanationPersistence:
    """
    Stores and retrieves Explanation objects using S3 and DynamoDB.

    S3 path pattern: explanations/{account_id}/{timestamp_iso}.json
    DynamoDB schema:
        - Partition key: account_id (String)
        - Sort key:      timestamp  (String ISO)
        - Attributes:    risk_score, risk_level, reason_codes, s3_uri

    CloudWatch audit logs record the S3 URI and DynamoDB key but do NOT
    include account identifiers or transaction amounts (Requirement 16.7).
    """

    def __init__(
        self,
        bucket_name: str = _S3_BUCKET,
        table_name: str = _DYNAMODB_TABLE,
    ) -> None:
        """
        Initialize persistence with S3 bucket and DynamoDB table names.

        Args:
            bucket_name: S3 bucket for explanation JSON storage.
            table_name:  DynamoDB table name for the explanation index.
        """
        if not bucket_name:
            raise ValueError("bucket_name cannot be empty")
        if not table_name:
            raise ValueError("table_name cannot be empty")

        self._bucket_name = bucket_name
        self._table_name = table_name
        self._formatters = OutputFormatters()

        aws = get_aws_clients()
        self._s3 = aws.s3
        self._dynamodb = aws.dynamodb
        self._table = self._dynamodb.Table(table_name)

        logger.info(
            "ExplanationPersistence initialized: "
            "bucket=%s, table=%s",
            bucket_name,
            table_name,
        )

    # ------------------------------------------------------------------
    # store()
    # ------------------------------------------------------------------

    def store(self, explanation: Explanation) -> str:
        """
        Persist an Explanation to S3 and index it in DynamoDB.

        The full JSON is written to S3 at:
            explanations/{account_id}/{timestamp_iso}.json
        with AES-256 server-side encryption.

        A lightweight index record is written to DynamoDB with:
            account_id, timestamp, risk_score, risk_level,
            reason_codes, s3_uri

        Args:
            explanation: The Explanation object to persist.

        Returns:
            The S3 URI where the explanation was stored.

        Raises:
            IOError: If the S3 or DynamoDB operation fails.
        """
        timestamp_iso = explanation.generated_at.isoformat()
        s3_key = (
            f"explanations/{explanation.account_id}/{timestamp_iso}.json"
        )

        # --- S3 write (AES-256 SSE) ---
        json_body = self._formatters.to_json(explanation)
        try:
            self._s3.put_object(
                Bucket=self._bucket_name,
                Key=s3_key,
                Body=json_body.encode("utf-8"),
                ServerSideEncryption="AES256",
                ContentType="application/json",
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            msg = f"S3 put_object failed: {code} — {exc}"
            logger.error(msg)
            raise IOError(msg) from exc

        s3_uri = f"s3://{self._bucket_name}/{s3_key}"

        # --- DynamoDB index write ---
        try:
            self._table.put_item(
                Item={
                    "account_id": explanation.account_id,
                    "timestamp": timestamp_iso,
                    "risk_score": str(explanation.risk_score),   # DynamoDB Number stored as Decimal-safe str
                    "risk_level": explanation.risk_level.value,
                    "reason_codes": explanation.reason_codes,
                    "s3_uri": s3_uri,
                }
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            msg = f"DynamoDB put_item failed: {code} — {exc}"
            logger.error(msg)
            raise IOError(msg) from exc

        # --- CloudWatch audit log (no account identifiers or amounts) ---
        # Requirement 16.4: log S3 URI and DynamoDB key
        # Requirement 16.7: do NOT log account_id or transaction amounts
        logger.info(
            "Explanation stored: s3_uri=%s, dynamo_key=timestamp=%s, "
            "risk_level=%s",
            s3_uri,
            timestamp_iso,
            explanation.risk_level.value,
        )

        return s3_uri

    # ------------------------------------------------------------------
    # get_latest()
    # ------------------------------------------------------------------

    def get_latest(self, account_id: str) -> Explanation:
        """
        Retrieve the most recent Explanation for an account.

        Queries DynamoDB for the latest record (sort key descending, limit 1)
        then fetches the full JSON from S3.

        Args:
            account_id: The account identifier to look up.

        Returns:
            The most recent Explanation for the account.

        Raises:
            KeyError: If no explanation exists for the account.
            IOError:  If a DynamoDB or S3 operation fails.
        """
        try:
            response = self._table.query(
                KeyConditionExpression=Key("account_id").eq(account_id),
                ScanIndexForward=False,   # descending by sort key (timestamp)
                Limit=1,
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            msg = f"DynamoDB query failed: {code} — {exc}"
            logger.error(msg)
            raise IOError(msg) from exc

        items = response.get("Items", [])
        if not items:
            raise KeyError(f"No explanation found for account (hash omitted)")

        s3_uri = items[0]["s3_uri"]
        return self._fetch_from_s3(s3_uri)

    # ------------------------------------------------------------------
    # get_range()
    # ------------------------------------------------------------------

    def get_range(
        self,
        account_id: str,
        start: datetime,
        end: datetime,
    ) -> List[Explanation]:
        """
        Retrieve all Explanations for an account within a timestamp range.

        Queries DynamoDB using the timestamp sort key between start and end
        (inclusive), then fetches each full JSON from S3.

        Args:
            account_id: The account identifier to look up.
            start:      Range start (inclusive).
            end:        Range end (inclusive).

        Returns:
            List of Explanation objects ordered by timestamp ascending.

        Raises:
            IOError: If a DynamoDB or S3 operation fails.
        """
        start_iso = start.isoformat()
        end_iso = end.isoformat()

        try:
            response = self._table.query(
                KeyConditionExpression=(
                    Key("account_id").eq(account_id)
                    & Key("timestamp").between(start_iso, end_iso)
                ),
                ScanIndexForward=True,   # ascending by timestamp
            )
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            msg = f"DynamoDB query failed: {code} — {exc}"
            logger.error(msg)
            raise IOError(msg) from exc

        explanations: List[Explanation] = []
        for item in response.get("Items", []):
            s3_uri = item["s3_uri"]
            explanations.append(self._fetch_from_s3(s3_uri))

        return explanations

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _fetch_from_s3(self, s3_uri: str) -> Explanation:
        """
        Download and deserialize an Explanation from S3.

        Args:
            s3_uri: Full S3 URI, e.g. s3://bucket/key.

        Returns:
            Deserialized Explanation object.

        Raises:
            KeyError: If the S3 object does not exist.
            IOError:  If the S3 operation or JSON parsing fails.
        """
        # Parse bucket and key from URI
        if not s3_uri.startswith("s3://"):
            raise IOError(f"Invalid S3 URI format: {s3_uri}")
        without_scheme = s3_uri[len("s3://"):]
        slash_idx = without_scheme.index("/")
        bucket = without_scheme[:slash_idx]
        key = without_scheme[slash_idx + 1:]

        try:
            response = self._s3.get_object(Bucket=bucket, Key=key)
            body = response["Body"].read().decode("utf-8")
        except ClientError as exc:
            code = exc.response.get("Error", {}).get("Code", "Unknown")
            if code == "NoSuchKey":
                raise KeyError(f"S3 object not found: {s3_uri}") from exc
            msg = f"S3 get_object failed: {code} — {exc}"
            logger.error(msg)
            raise IOError(msg) from exc

        try:
            data = json.loads(body)
        except json.JSONDecodeError as exc:
            msg = f"Invalid JSON in S3 object {s3_uri}: {exc}"
            logger.error(msg)
            raise IOError(msg) from exc

        return self._deserialize(data, s3_uri)

    @staticmethod
    def _deserialize(data: dict, s3_uri: str) -> Explanation:
        """
        Reconstruct an Explanation dataclass from a JSON dict.

        Args:
            data:    Parsed JSON dictionary.
            s3_uri:  The S3 URI the data was loaded from (stored on the object).

        Returns:
            Explanation instance.
        """
        top_features = [
            FeatureContribution(
                feature_name=fc["feature_name"],
                contribution=fc["contribution"],
                raw_value=fc.get("raw_value"),
                context_label=fc.get("context_label", ""),
            )
            for fc in data.get("top_features", [])
        ]

        generated_at_raw = data.get("generated_at", "")
        try:
            generated_at = datetime.fromisoformat(generated_at_raw)
        except (ValueError, TypeError):
            generated_at = datetime.utcnow()

        return Explanation(
            account_id=data["account_id"],
            risk_score=float(data["risk_score"]),
            risk_level=RiskLevel(data["risk_level"]),
            reason_codes=data.get("reason_codes", []),
            top_features=top_features,
            feature_contributions=data.get("feature_contributions", {}),
            natural_language_summary=data.get("natural_language_summary", ""),
            language=data.get("language", "en"),
            is_fallback=bool(data.get("is_fallback", False)),
            is_validated=bool(data.get("is_validated", False)),
            generated_at=generated_at,
            generation_time_ms=float(data.get("generation_time_ms", 0.0)),
            s3_uri=s3_uri,
        )
