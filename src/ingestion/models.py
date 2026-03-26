"""
Core data models for BitoPro API Data Ingestion Layer

This module defines all core data models, enums, and configuration classes
used throughout the ingestion system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class HTTPMethod(Enum):
    """HTTP methods supported by the API client"""
    GET = "GET"
    POST = "POST"


class FieldType(Enum):
    """Field types for schema inference"""
    NUMERIC = "numeric"
    CATEGORICAL = "categorical"
    DATETIME = "datetime"
    TEXT = "text"
    ID_LIKE = "id_like"
    BOOLEAN = "boolean"
    NULL = "null"
    MIXED = "mixed"


@dataclass
class APIConfig:
    """Configuration for BitoPro API client"""
    base_url: str = "https://aws-event-api.bitopro.com/"
    timeout: int = 30
    max_retries: int = 3
    retry_backoff: float = 2.0
    rate_limit_per_second: float = 0.9

    def __post_init__(self):
        """Validate configuration parameters"""
        if not self.base_url:
            raise ValueError("base_url must be non-empty")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if self.retry_backoff <= 0:
            raise ValueError("retry_backoff must be positive")
        if self.rate_limit_per_second <= 0:
            raise ValueError("rate_limit_per_second must be positive")


@dataclass
class APIRequest:
    """Represents an API request with validation"""
    endpoint: str
    method: HTTPMethod
    params: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None
    timeout: int = 30
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        """Validate request parameters"""
        # Validate endpoint
        if not self.endpoint or not isinstance(self.endpoint, str):
            raise ValueError("endpoint must be a non-empty string")
        
        # Validate method
        if not isinstance(self.method, HTTPMethod):
            raise ValueError("method must be HTTPMethod.GET or HTTPMethod.POST")
        
        # Validate timeout
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        
        # Validate retry_count
        if self.retry_count < 0:
            raise ValueError("retry_count must be non-negative")
        
        # Validate max_retries
        if self.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        
        # Validate retry_count does not exceed max_retries
        if self.retry_count > self.max_retries:
            raise ValueError("retry_count must not exceed max_retries")


@dataclass
class APIResponse:
    """Represents an API response"""
    status_code: int
    data: Dict[str, Any]
    headers: Dict[str, str]
    timestamp: datetime
    request_id: str
    pagination_info: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Validate response parameters"""
        # Validate status_code is a valid HTTP status code (100-599)
        if not isinstance(self.status_code, int) or not (100 <= self.status_code <= 599):
            raise ValueError("status_code must be a valid HTTP status code (100-599)")
        
        # Validate data is a dictionary
        if not isinstance(self.data, dict):
            raise ValueError("data must be a dictionary")
        
        # Validate headers is a dictionary
        if not isinstance(self.headers, dict):
            raise ValueError("headers must be a dictionary")
        
        # Validate timestamp is a datetime
        if not isinstance(self.timestamp, datetime):
            raise ValueError("timestamp must be a datetime object")
        
        # Validate request_id is non-empty
        if not self.request_id or not isinstance(self.request_id, str):
            raise ValueError("request_id must be a non-empty string")


@dataclass
class FlattenedRecord:
    """Represents a flattened data record"""
    record_id: str
    source_endpoint: str
    flattened_data: Dict[str, Any]
    original_structure: Dict[str, Any]
    flatten_timestamp: datetime

    def __post_init__(self):
        """Validate flattened record"""
        # Validate record_id
        if not self.record_id or not isinstance(self.record_id, str):
            raise ValueError("record_id must be a non-empty string")
        
        # Validate source_endpoint
        if not self.source_endpoint or not isinstance(self.source_endpoint, str):
            raise ValueError("source_endpoint must be a non-empty string")
        
        # Validate flattened_data is a dictionary
        if not isinstance(self.flattened_data, dict):
            raise ValueError("flattened_data must be a dictionary")
        
        # Validate flattened_data has no nested structures (max depth of 1)
        for key, value in self.flattened_data.items():
            if isinstance(value, dict):
                raise ValueError(
                    f"flattened_data must have no nested structures, "
                    f"but found nested dict at key '{key}'"
                )
        
        # Validate original_structure is a dictionary
        if not isinstance(self.original_structure, dict):
            raise ValueError("original_structure must be a dictionary")
        
        # Validate flatten_timestamp
        if not isinstance(self.flatten_timestamp, datetime):
            raise ValueError("flatten_timestamp must be a datetime object")


@dataclass
class FieldSchema:
    """Schema information for a single field"""
    name: str
    inferred_type: FieldType
    nullable: bool
    sample_values: List[Any]
    null_count: int
    total_count: int
    confidence: float

    def __post_init__(self):
        """Validate field schema"""
        # Validate name
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")
        
        # Validate inferred_type
        if not isinstance(self.inferred_type, FieldType):
            raise ValueError("inferred_type must be a FieldType enum")
        
        # Validate nullable is boolean
        if not isinstance(self.nullable, bool):
            raise ValueError("nullable must be a boolean")
        
        # Validate sample_values is a list
        if not isinstance(self.sample_values, list):
            raise ValueError("sample_values must be a list")
        
        # Validate null_count
        if not isinstance(self.null_count, int) or self.null_count < 0:
            raise ValueError("null_count must be a non-negative integer")
        
        # Validate total_count
        if not isinstance(self.total_count, int) or self.total_count < 0:
            raise ValueError("total_count must be a non-negative integer")
        
        # Validate null_count does not exceed total_count
        if self.null_count > self.total_count:
            raise ValueError("null_count must not exceed total_count")
        
        # Validate confidence is between 0 and 1
        if not isinstance(self.confidence, (int, float)) or not (0 <= self.confidence <= 1):
            raise ValueError("confidence must be a number between 0 and 1")

    def to_dict(self) -> Dict[str, Any]:
        """Convert FieldSchema to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "inferred_type": self.inferred_type.value,
            "nullable": self.nullable,
            "sample_values": self.sample_values,
            "null_count": self.null_count,
            "total_count": self.total_count,
            "confidence": self.confidence,
        }
