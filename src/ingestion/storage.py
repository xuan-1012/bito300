"""
RawDataStorage - Storage management for raw API responses

This module provides storage backends for raw API responses.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import json
import logging
from pathlib import Path
from botocore.exceptions import ClientError
from src.common.aws_clients import get_aws_clients

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """
    Abstract base class for storage backends.
    
    This interface defines the contract for storage implementations
    (S3Storage and LocalStorage).
    
    **Validates: Requirements 5.1, 5.2**
    """
    
    @abstractmethod
    def save(self, data: Dict[str, Any], key: str) -> str:
        """
        Save raw data and return storage URI.
        
        Args:
            data: Raw data to store (must be JSON-serializable)
            key: Storage key/path for the data
            
        Returns:
            Storage URI indicating where the data was saved
            
        Raises:
            ValueError: If data is not JSON-serializable
            IOError: If storage operation fails
        """
        pass
    
    @abstractmethod
    def load(self, key: str) -> Dict[str, Any]:
        """
        Load raw data from storage.
        
        Args:
            key: Storage key/path to load from
            
        Returns:
            Loaded data as dictionary
            
        Raises:
            KeyError: If key does not exist
            IOError: If storage operation fails
        """
        pass


class S3Storage(StorageBackend):
    """
    S3 storage backend for raw API responses.
    
    This implementation stores data in AWS S3 with server-side encryption
    and private bucket access. It uses the AWSClients utility for boto3
    client management.
    
    **Validates: Requirements 5.3, 12.3**
    """
    
    def __init__(self, bucket_name: str, prefix: str = "raw_data/"):
        """
        Initialize S3 storage backend.
        
        Args:
            bucket_name: S3 bucket name (must be private with encryption)
            prefix: Key prefix for organization (default: "raw_data/")
            
        Raises:
            ValueError: If bucket_name is empty
        """
        if not bucket_name:
            raise ValueError("bucket_name cannot be empty")
        
        self.bucket_name = bucket_name
        self.prefix = prefix.rstrip('/') + '/' if prefix else ''
        
        # Initialize S3 client using AWSClients utility
        aws_clients = get_aws_clients()
        self._s3_client = aws_clients.s3
        
        logger.info(
            f"S3Storage initialized: bucket={bucket_name}, prefix={self.prefix}"
        )
    
    def save(self, data: Dict[str, Any], key: str) -> str:
        """
        Save raw data to S3 with server-side encryption.
        
        Args:
            data: Raw data to store (must be JSON-serializable)
            key: Storage key/path for the data
            
        Returns:
            Storage URI in format: s3://bucket_name/prefix/key
            
        Raises:
            ValueError: If data is not JSON-serializable
            IOError: If S3 operation fails
        """
        # Validate data is JSON-serializable
        try:
            json_data = json.dumps(data)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Data is not JSON-serializable: {e}")
        
        # Build full S3 key with prefix
        full_key = f"{self.prefix}{key}"
        
        try:
            # Upload to S3 with server-side encryption (AES256)
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=full_key,
                Body=json_data,
                ServerSideEncryption='AES256',
                ContentType='application/json'
            )
            
            uri = f"s3://{self.bucket_name}/{full_key}"
            logger.info(f"Data saved to S3: {uri}")
            return uri
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            error_msg = f"Failed to save to S3: {error_code} - {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error saving to S3: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
    
    def load(self, key: str) -> Dict[str, Any]:
        """
        Load raw data from S3.
        
        Args:
            key: Storage key/path to load from
            
        Returns:
            Loaded data as dictionary
            
        Raises:
            KeyError: If key does not exist in S3
            IOError: If S3 operation fails
        """
        # Build full S3 key with prefix
        full_key = f"{self.prefix}{key}"
        
        try:
            # Download from S3
            response = self._s3_client.get_object(
                Bucket=self.bucket_name,
                Key=full_key
            )
            
            # Read and parse JSON data
            json_data = response['Body'].read().decode('utf-8')
            data = json.loads(json_data)
            
            logger.info(f"Data loaded from S3: s3://{self.bucket_name}/{full_key}")
            return data
            
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            
            # Handle NoSuchKey as KeyError
            if error_code == 'NoSuchKey':
                error_msg = f"Key not found in S3: {full_key}"
                logger.error(error_msg)
                raise KeyError(error_msg) from e
            
            # Other errors as IOError
            error_msg = f"Failed to load from S3: {error_code} - {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON data in S3 key {full_key}: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error loading from S3: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e



class LocalStorage(StorageBackend):
    """
    Local filesystem storage backend for raw API responses.
    
    This implementation stores data in the local filesystem with automatic
    directory creation. Files are stored as JSON with proper organization.
    
    **Validates: Requirements 5.4**
    """
    
    def __init__(self, base_path: str = "raw_data/"):
        """
        Initialize local file storage backend.
        
        Args:
            base_path: Base directory for raw data (default: "raw_data/")
            
        Raises:
            ValueError: If base_path is None
        """
        if base_path is None:
            raise ValueError("base_path cannot be None")
        
        self.base_path = Path(base_path)
        
        logger.info(
            f"LocalStorage initialized: base_path={self.base_path}"
        )
    
    def save(self, data: Dict[str, Any], key: str) -> str:
        """
        Save raw data to local filesystem.
        
        Creates directory structure if it doesn't exist. Saves data as JSON
        file with proper formatting.
        
        Args:
            data: Raw data to store (must be JSON-serializable)
            key: Storage key/path for the data
            
        Returns:
            Storage URI in format: file://absolute_path
            
        Raises:
            ValueError: If data is not JSON-serializable
            IOError: If filesystem operation fails
        """
        # Validate data is JSON-serializable
        try:
            json_data = json.dumps(data, indent=2)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Data is not JSON-serializable: {e}")
        
        # Build full file path
        file_path = self.base_path / key
        
        try:
            # Create directory structure if not exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON data to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(json_data)
            
            # Get absolute path for URI (use forward slashes for cross-platform compatibility)
            absolute_path = file_path.resolve()
            uri = "file://" + absolute_path.as_posix()
            logger.info(f"Data saved to local filesystem: {uri}")
            return uri
            
        except OSError as e:
            error_msg = f"Failed to save to local filesystem: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
        except Exception as e:
            error_msg = f"Unexpected error saving to local filesystem: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
    
    def load(self, key: str) -> Dict[str, Any]:
        """
        Load raw data from local filesystem.
        
        Args:
            key: Storage key/path to load from
            
        Returns:
            Loaded data as dictionary
            
        Raises:
            KeyError: If key does not exist in filesystem
            IOError: If filesystem operation fails
        """
        # Build full file path
        file_path = self.base_path / key
        
        try:
            # Check if file exists
            if not file_path.exists():
                error_msg = f"Key not found in local filesystem: {key}"
                logger.error(error_msg)
                raise KeyError(error_msg)
            
            # Read and parse JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            absolute_path = file_path.resolve()
            logger.info(f"Data loaded from local filesystem: file://{absolute_path}")
            return data
            
        except KeyError:
            # Re-raise KeyError as-is
            raise
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON data in file {key}: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
            
        except OSError as e:
            error_msg = f"Failed to load from local filesystem: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error loading from local filesystem: {str(e)}"
            logger.error(error_msg)
            raise IOError(error_msg) from e


class RawDataStorage:
    """
    Manager for storing raw API responses without modification.

    Wraps a StorageBackend to provide key generation, validation,
    and logging for raw data persistence.

    **Validates: Requirements 5.1, 5.2, 5.5, 9.6, 11.4**
    """

    def __init__(self, backend: StorageBackend):
        """
        Initialize raw data storage manager.

        Args:
            backend: Storage backend (S3Storage or LocalStorage)

        Raises:
            ValueError: If backend is None
        """
        if backend is None:
            raise ValueError("backend cannot be None")

        self.backend = backend
        logger.info(
            f"RawDataStorage initialized with backend: {type(backend).__name__}"
        )

    def generate_key(self, endpoint: str, timestamp) -> str:
        """
        Generate a unique storage key based on endpoint and timestamp.

        The key format is: ``{sanitized_endpoint}/{timestamp_iso}.json``

        Endpoint sanitization replaces leading slashes and any non-alphanumeric
        characters (except ``-``) with underscores so the key is safe for both
        S3 and local filesystem paths.

        Args:
            endpoint: API endpoint path (e.g. "/v1/transactions")
            timestamp: datetime object used for versioning

        Returns:
            Storage key string, e.g. "v1_transactions/2024-01-01T10:00:00.json"

        Raises:
            ValueError: If endpoint is empty or timestamp is None
        """
        if not endpoint or not isinstance(endpoint, str):
            raise ValueError("endpoint must be a non-empty string")
        if timestamp is None:
            raise ValueError("timestamp cannot be None")

        import re
        # Strip leading slash, then replace non-alphanumeric chars (except -) with _
        sanitized = endpoint.lstrip("/")
        sanitized = re.sub(r"[^a-zA-Z0-9\-/]", "_", sanitized)
        # Collapse consecutive underscores/slashes
        sanitized = re.sub(r"_+", "_", sanitized).strip("_")

        # Replace colons in ISO timestamp so the key is safe on all filesystems
        timestamp_iso = timestamp.isoformat().replace(":", "-")
        key = f"{sanitized}/{timestamp_iso}.json"
        return key

    def store_raw_response(
        self,
        response: Dict[str, Any],
        endpoint: str,
        timestamp=None,
    ) -> str:
        """
        Store a raw API response without any modification.

        Args:
            response: Complete, unmodified API response dictionary
            endpoint: API endpoint used to organise the storage key
            timestamp: Optional datetime for versioning; defaults to now

        Returns:
            Storage URI indicating where the data was saved

        Raises:
            ValueError: If response is not JSON-serializable
            IOError: If the storage operation fails
        """
        from datetime import datetime as _datetime, timezone as _timezone

        if timestamp is None:
            timestamp = _datetime.now(_timezone.utc)

        # Req 9.6 – validate JSON-serializability before storing
        try:
            json.dumps(response)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Response is not JSON-serializable: {exc}") from exc

        key = self.generate_key(endpoint, timestamp)

        # Req 5.1 – store without modification
        uri = self.backend.save(response, key)

        # Req 11.4 – log URI and timestamp
        logger.info(
            f"Raw response stored: uri={uri}, endpoint={endpoint}, "
            f"timestamp={timestamp.isoformat()}"
        )

        return uri
