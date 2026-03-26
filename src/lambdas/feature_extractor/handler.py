"""
Feature Extractor Lambda Handler

Extracts risk features from raw transaction data grouped by account.

Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11,
              15.1, 15.2, 15.3, 15.4, 15.5
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from src.common.models import Transaction, TransactionFeatures
from src.common.validators import validate_features
from src.common.aws_clients import get_aws_clients

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def is_round_number(amount: float, threshold: float = 0.01) -> bool:
    """
    Check if an amount is suspiciously round (e.g., 1000.00, 5000.00).

    Rounds to the nearest 100 and checks if the difference is within threshold.

    Preconditions:
        - amount > 0
        - threshold > 0

    Postconditions:
        - Returns bool

    Args:
        amount: Transaction amount
        threshold: Maximum allowed deviation from a round number (default 0.01)

    Returns:
        True if amount is close to a multiple of 100, False otherwise
    """
    rounded = round(amount, -2)  # Round to nearest 100
    return abs(amount - rounded) < threshold


def calculate_concentration(transactions: List[Transaction], account_id: str) -> float:
    """
    Calculate the Herfindahl concentration index for counterparty distribution.

    A higher score indicates more concentration (potentially suspicious).

    Preconditions:
        - transactions is non-empty

    Postconditions:
        - Returns value between 0 and 1

    Args:
        transactions: List of transactions for the account
        account_id: The account whose counterparties are being measured

    Returns:
        Herfindahl index (float between 0 and 1)
    """
    counterparty_counts: Dict[str, int] = {}
    for txn in transactions:
        cp = txn.to_account if txn.from_account == account_id else txn.from_account
        counterparty_counts[cp] = counterparty_counts.get(cp, 0) + 1

    total = len(transactions)
    herfindahl = sum((count / total) ** 2 for count in counterparty_counts.values())

    # Clamp to [0, 1] to guard against floating-point edge cases
    return max(0.0, min(1.0, herfindahl))


def extract_features(transactions: List[Transaction]) -> TransactionFeatures:
    """
    Extract risk features from a list of transactions belonging to one account.

    Preconditions:
        - transactions is a non-empty list
        - All transactions belong to the same account (from_account)
        - All transactions have valid timestamps and positive amounts

    Postconditions:
        - Returns a valid TransactionFeatures object
        - All feature values are non-negative
        - Ratio features are between 0 and 1

    Args:
        transactions: List of Transaction objects for a single account

    Returns:
        TransactionFeatures with all computed risk features
    """
    assert len(transactions) > 0, "transactions must be non-empty"

    account_id = transactions[0].from_account
    transaction_count = len(transactions)

    # Sort by timestamp for temporal analysis
    sorted_txns = sorted(transactions, key=lambda t: t.timestamp)

    # Accumulators
    total_volume = 0.0
    amounts: List[float] = []
    counterparties: set = set()
    night_transactions = 0
    rapid_transaction_count = 0
    round_numbers = 0

    for i, txn in enumerate(sorted_txns):
        # Requirement 3.2: total_volume
        total_volume += txn.amount
        amounts.append(txn.amount)

        # Requirement 3.5: unique counterparties
        cp = txn.to_account if txn.from_account == account_id else txn.from_account
        counterparties.add(cp)

        # Requirement 3.6: night transaction ratio (00:00–06:00)
        if 0 <= txn.timestamp.hour < 6:
            night_transactions += 1

        # Requirement 3.7: round number ratio
        if is_round_number(txn.amount):
            round_numbers += 1

        # Requirement 3.8: rapid transaction count (< 5 minutes apart)
        if i > 0:
            time_diff = (txn.timestamp - sorted_txns[i - 1].timestamp).total_seconds()
            if time_diff < 300:  # 5 minutes = 300 seconds
                rapid_transaction_count += 1

    # Requirement 3.3 & 3.4: basic statistics
    avg_transaction_size = total_volume / transaction_count
    max_transaction_size = max(amounts)

    # Requirement 3.5: unique counterparties count
    unique_counterparties = len(counterparties)

    # Requirement 3.6: night transaction ratio
    night_transaction_ratio = night_transactions / transaction_count

    # Requirement 3.7: round number ratio
    round_number_ratio = round_numbers / transaction_count

    # Requirement 3.9: concentration score (Herfindahl index)
    concentration_score = calculate_concentration(transactions, account_id)

    # Requirement 3.10: velocity score (transactions per hour)
    time_span_seconds = (
        sorted_txns[-1].timestamp - sorted_txns[0].timestamp
    ).total_seconds()
    time_span_hours = time_span_seconds / 3600
    velocity_score = transaction_count / time_span_hours if time_span_hours > 0 else 0.0

    features = TransactionFeatures(
        account_id=account_id,
        total_volume=total_volume,
        transaction_count=transaction_count,
        avg_transaction_size=avg_transaction_size,
        max_transaction_size=max_transaction_size,
        unique_counterparties=unique_counterparties,
        night_transaction_ratio=night_transaction_ratio,
        rapid_transaction_count=rapid_transaction_count,
        round_number_ratio=round_number_ratio,
        concentration_score=concentration_score,
        velocity_score=velocity_score,
    )

    assert validate_features(features), f"Feature validation failed for account {account_id}"
    return features


def _parse_s3_uri(s3_uri: str):
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


def _read_transactions_from_s3(aws_clients, s3_uri: str) -> List[Dict[str, Any]]:
    """
    Read raw transaction JSON from S3.

    Args:
        aws_clients: AWSClients instance
        s3_uri: S3 URI of the raw transaction data

    Returns:
        List of raw transaction dictionaries
    """
    bucket, key = _parse_s3_uri(s3_uri)
    logger.info(f"Reading raw transactions from s3://{bucket}/{key}")
    response = aws_clients.s3.get_object(Bucket=bucket, Key=key)
    body = response["Body"].read().decode("utf-8")
    return json.loads(body)


def _dict_to_transaction(raw: Dict[str, Any]) -> Optional[Transaction]:
    """
    Convert a raw transaction dictionary to a Transaction object.

    Returns None if conversion fails.
    """
    try:
        timestamp_val = raw.get("timestamp")
        if isinstance(timestamp_val, str):
            timestamp = datetime.fromisoformat(timestamp_val.replace("Z", "+00:00"))
        elif isinstance(timestamp_val, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp_val / 1000)
        else:
            timestamp = datetime.now()

        return Transaction(
            transaction_id=raw.get("transaction_id", raw.get("id", "")),
            timestamp=timestamp,
            from_account=raw.get("from_account", raw.get("from", "")),
            to_account=raw.get("to_account", raw.get("to", "")),
            amount=float(raw.get("amount", 0)),
            currency=raw.get("currency", raw.get("symbol", "")),
            transaction_type=raw.get("transaction_type", raw.get("type", "transfer")),
            status=raw.get("status", "completed"),
            fee=float(raw.get("fee", 0)),
            metadata=raw.get("metadata"),
        )
    except Exception as e:
        logger.error(f"Failed to convert transaction dict to Transaction: {e}")
        return None


def _store_features_to_s3(
    aws_clients,
    bucket: str,
    key: str,
    features_list: List[Dict[str, Any]],
) -> str:
    """
    Store extracted features to S3 with AES256 encryption.

    **Validates: Requirements 3.11, 9.2, 9.6**

    Args:
        aws_clients: AWSClients instance
        bucket: S3 bucket name
        key: S3 object key
        features_list: List of feature dictionaries

    Returns:
        S3 URI of stored features
    """
    json_data = json.dumps(features_list, default=str, indent=2)
    aws_clients.s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json_data,
        ContentType="application/json",
        ServerSideEncryption="AES256",
    )
    s3_uri = f"s3://{bucket}/{key}"
    logger.info(f"Stored features to {s3_uri}")
    return s3_uri


def lambda_handler(event, context):
    """
    Lambda handler for extracting features from transaction data.

    Reads raw transaction data from S3, groups by account, extracts features
    for each account, validates them, and stores the results back to S3.

    **Validates: Requirements 3.1, 3.11, 13.1, 13.4, 15.1, 15.2, 15.3, 15.4, 15.5**

    Args:
        event: Lambda event containing:
            - s3_uri: S3 URI of raw transaction data (or nested under 'body')
        context: Lambda context

    Returns:
        dict: Response with S3 URI of extracted features
    """
    # Requirement 13.1: Log start time
    start_execution = datetime.now()
    logger.info(f"Feature Extractor Lambda invoked at {start_execution.isoformat()}")
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

        # Read raw transactions from S3
        raw_transactions = _read_transactions_from_s3(aws_clients, s3_uri)
        logger.info(f"Read {len(raw_transactions)} raw transactions from S3")

        # Requirement 3.1: Group transactions by account (from_account field)
        accounts: Dict[str, List[Transaction]] = {}
        conversion_errors = 0
        for raw in raw_transactions:
            txn = _dict_to_transaction(raw)
            if txn is None:
                conversion_errors += 1
                continue
            account_id = txn.from_account
            if account_id not in accounts:
                accounts[account_id] = []
            accounts[account_id].append(txn)

        if conversion_errors:
            logger.warning(f"Failed to convert {conversion_errors} transactions")

        # Requirement 13.4: Log number of accounts to be processed
        logger.info(f"Grouped transactions into {len(accounts)} accounts")

        # Extract and validate features for each account
        features_output: List[Dict[str, Any]] = []
        skipped_accounts = 0

        for account_id, txns in accounts.items():
            try:
                # Requirement 3.1–3.10: Extract features
                features = extract_features(txns)

                # Requirements 15.1–15.5: Validate features
                if not validate_features(features, input_transactions=txns):
                    logger.error(
                        f"Feature validation failed for account, skipping"
                    )
                    skipped_accounts += 1
                    continue

                features_output.append({
                    "account_id": features.account_id,
                    "total_volume": features.total_volume,
                    "transaction_count": features.transaction_count,
                    "avg_transaction_size": features.avg_transaction_size,
                    "max_transaction_size": features.max_transaction_size,
                    "unique_counterparties": features.unique_counterparties,
                    "night_transaction_ratio": features.night_transaction_ratio,
                    "rapid_transaction_count": features.rapid_transaction_count,
                    "round_number_ratio": features.round_number_ratio,
                    "concentration_score": features.concentration_score,
                    "velocity_score": features.velocity_score,
                })

            except Exception as e:
                logger.error(
                    f"Error extracting features for account: {e}", exc_info=True
                )
                skipped_accounts += 1

        # Requirement 13.4: Log number of accounts processed
        processed_count = len(features_output)
        logger.info(
            f"Feature extraction complete: {processed_count} accounts processed, "
            f"{skipped_accounts} skipped"
        )

        # Requirement 3.11 / 9.2: Store features to S3 with path features/{timestamp}.json
        bucket_name = os.environ.get("FEATURES_BUCKET", "crypto-detection-features")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        s3_key = f"features/{timestamp}.json"

        features_s3_uri = _store_features_to_s3(
            aws_clients=aws_clients,
            bucket=bucket_name,
            key=s3_key,
            features_list=features_output,
        )

        # Requirement 13.1: Log end time
        end_execution = datetime.now()
        execution_duration = (end_execution - start_execution).total_seconds()
        logger.info(
            f"Feature Extractor completed in {execution_duration:.2f}s. "
            f"Features stored at {features_s3_uri}"
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "s3_uri": features_s3_uri,
                "accounts_processed": processed_count,
                "accounts_skipped": skipped_accounts,
                "execution_duration_seconds": execution_duration,
            }),
        }

    except Exception as e:
        logger.error(f"Unexpected error in Feature Extractor: {str(e)}", exc_info=True)
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal error",
                "message": str(e),
            }),
        }
