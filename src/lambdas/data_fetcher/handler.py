"""
Data Fetcher Lambda Handler
Fetches transaction data from BitoPro API and stores to S3

**Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 9.1, 13.1, 13.3**
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from src.common.aws_clients import get_aws_clients
from src.common.validators import validate_transaction
from src.common.models import Transaction
from src.utils.bitopro_client import BitoproClient, BitoproClientError

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for fetching transaction data from BitoPro API
    
    **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 9.1, 13.1, 13.3**
    
    Args:
        event: Lambda event containing:
            - start_time (optional): ISO format datetime string
            - end_time (optional): ISO format datetime string
            - limit (optional): Maximum number of transactions (default: 1000)
        context: Lambda context
        
    Returns:
        dict: Response with:
            - statusCode: HTTP status code
            - body: JSON string containing:
                - s3_uri: S3 URI of stored data
                - transaction_count: Number of transactions fetched
                - valid_count: Number of valid transactions
                - invalid_count: Number of invalid transactions
                - start_time: Start time used
                - end_time: End time used
    """
    # Requirement 13.1: Log start time
    start_execution = datetime.now()
    logger.info(f"Data Fetcher Lambda invoked at {start_execution.isoformat()}")
    logger.info(f"Event: {json.dumps(event, default=str)}")
    
    try:
        # Parse event parameters
        start_time, end_time, limit = _parse_event_parameters(event)
        
        # Requirement 1.1: Retrieve BitoPro API key from Secrets Manager
        logger.info("Initializing AWS clients and BitoPro client")
        aws_clients = get_aws_clients()
        
        secret_id = os.environ.get('BITOPRO_SECRET_ID', 'bitopro-api-key')
        bitopro_client = BitoproClient(
            aws_clients=aws_clients,
            secret_id=secret_id
        )
        
        # Requirement 1.2: Fetch transactions for specified time range
        # Requirement 1.5: Retry with exponential backoff (handled in BitoproClient)
        logger.info(
            f"Fetching transactions from {start_time.isoformat()} to "
            f"{end_time.isoformat()}, limit={limit}"
        )
        
        raw_transactions = bitopro_client.fetch_transactions(
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        
        # Requirement 13.3: Log number of transactions retrieved
        logger.info(f"Fetched {len(raw_transactions)} transactions from BitoPro API")
        
        # Requirement 1.3: Validate each transaction
        valid_transactions = []
        invalid_count = 0
        
        for raw_txn in raw_transactions:
            try:
                # Convert raw transaction dict to Transaction object
                transaction = _convert_to_transaction(raw_txn)
                
                # Validate transaction
                if validate_transaction(transaction):
                    valid_transactions.append(raw_txn)
                else:
                    invalid_count += 1
                    # Requirement 2.6: Log validation error (already logged in validator)
                    
            except Exception as e:
                invalid_count += 1
                logger.error(
                    f"Failed to convert/validate transaction: {e}",
                    exc_info=False  # Don't log full stack trace for validation errors
                )
        
        logger.info(
            f"Validation complete: {len(valid_transactions)} valid, "
            f"{invalid_count} invalid transactions"
        )
        
        # Requirement 1.4: Store raw data to S3 in JSON format
        # Requirement 9.1: Store with path pattern raw-data/{timestamp}.json
        bucket_name = os.environ.get('RAW_DATA_BUCKET', 'crypto-detection-raw-data')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        s3_key = f"raw-data/{timestamp}.json"
        
        logger.info(f"Storing {len(valid_transactions)} valid transactions to S3")
        s3_uri = _store_to_s3(
            aws_clients=aws_clients,
            bucket=bucket_name,
            key=s3_key,
            data=valid_transactions
        )
        
        # Requirement 13.1: Log end time and operation details
        end_execution = datetime.now()
        execution_duration = (end_execution - start_execution).total_seconds()
        
        logger.info(
            f"Data Fetcher completed successfully in {execution_duration:.2f}s"
        )
        logger.info(f"S3 URI: {s3_uri}")
        logger.info(
            f"Summary: {len(valid_transactions)} valid, {invalid_count} invalid "
            f"transactions from {start_time.isoformat()} to {end_time.isoformat()}"
        )
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                's3_uri': s3_uri,
                'transaction_count': len(raw_transactions),
                'valid_count': len(valid_transactions),
                'invalid_count': invalid_count,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'execution_duration_seconds': execution_duration
            })
        }
        
    except BitoproClientError as e:
        # Requirement 11.1: Handle API errors (already retried in BitoproClient)
        logger.error(f"BitoPro API error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'BitoPro API error',
                'message': str(e)
            })
        }
        
    except Exception as e:
        # Requirement 1.6, 13.2: Log error details
        logger.error(f"Unexpected error in Data Fetcher: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Internal error',
                'message': str(e)
            })
        }


def _parse_event_parameters(event: Dict[str, Any]) -> tuple:
    """
    Parse event parameters for time range and limit
    
    Args:
        event: Lambda event dictionary
        
    Returns:
        Tuple of (start_time, end_time, limit)
    """
    # Parse time range (default to last 24 hours)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=1)
    
    if 'start_time' in event:
        try:
            start_time = datetime.fromisoformat(event['start_time'])
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid start_time format, using default: {e}")
    
    if 'end_time' in event:
        try:
            end_time = datetime.fromisoformat(event['end_time'])
        except (ValueError, TypeError) as e:
            logger.warning(f"Invalid end_time format, using default: {e}")
    
    # Parse limit (default to 1000)
    limit = event.get('limit', 1000)
    try:
        limit = int(limit)
        if limit <= 0:
            logger.warning(f"Invalid limit {limit}, using default 1000")
            limit = 1000
    except (ValueError, TypeError):
        logger.warning(f"Invalid limit format, using default 1000")
        limit = 1000
    
    return start_time, end_time, limit


def _convert_to_transaction(raw_txn: Dict[str, Any]) -> Transaction:
    """
    Convert raw transaction dictionary to Transaction object
    
    Args:
        raw_txn: Raw transaction dictionary from BitoPro API
        
    Returns:
        Transaction object
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Parse timestamp
    timestamp_str = raw_txn.get('timestamp')
    if isinstance(timestamp_str, str):
        timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    elif isinstance(timestamp_str, (int, float)):
        timestamp = datetime.fromtimestamp(timestamp_str / 1000)  # Assume milliseconds
    else:
        timestamp = datetime.now()
    
    return Transaction(
        transaction_id=raw_txn.get('transaction_id', raw_txn.get('id', '')),
        timestamp=timestamp,
        from_account=raw_txn.get('from_account', raw_txn.get('from', '')),
        to_account=raw_txn.get('to_account', raw_txn.get('to', '')),
        amount=float(raw_txn.get('amount', 0)),
        currency=raw_txn.get('currency', raw_txn.get('symbol', '')),
        transaction_type=raw_txn.get('transaction_type', raw_txn.get('type', 'transfer')),
        status=raw_txn.get('status', 'completed'),
        fee=float(raw_txn.get('fee', 0)),
        metadata=raw_txn.get('metadata')
    )


def _store_to_s3(
    aws_clients,
    bucket: str,
    key: str,
    data: List[Dict[str, Any]]
) -> str:
    """
    Store transaction data to S3
    
    **Validates: Requirements 1.4, 9.1**
    
    Args:
        aws_clients: AWSClients instance
        bucket: S3 bucket name
        key: S3 object key
        data: List of transaction dictionaries
        
    Returns:
        S3 URI of stored data
        
    Raises:
        Exception: If S3 operation fails
    """
    try:
        # Convert data to JSON
        json_data = json.dumps(data, default=str, indent=2)
        
        # Store to S3 with server-side encryption (Requirement 9.6)
        aws_clients.s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=json_data,
            ContentType='application/json',
            ServerSideEncryption='AES256'
        )
        
        s3_uri = f"s3://{bucket}/{key}"
        logger.info(f"Successfully stored data to {s3_uri}")
        
        return s3_uri
        
    except Exception as e:
        logger.error(f"Failed to store data to S3: {str(e)}")
        raise
