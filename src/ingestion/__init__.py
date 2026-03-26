"""
BitoPro API Data Ingestion Layer

Public API for the ingestion package.  Import everything you need from here:

    from src.ingestion import ingest_bitopro_data, BitoProAPIClient, JSONFlattener
"""

# Core data models and enums
from src.ingestion.models import (
    HTTPMethod,
    FieldType,
    APIConfig,
    APIRequest,
    APIResponse,
    FlattenedRecord,
    FieldSchema,
)

# HTTP client
from src.ingestion.client import BitoProAPIClient

# Storage components
from src.ingestion.storage import (
    StorageBackend,
    S3Storage,
    LocalStorage,
    RawDataStorage,
)

# JSON flattening
from src.ingestion.flattener import JSONFlattener

# Schema inference
from src.ingestion.inferencer import SchemaInferencer

# Error handling / fallback
from src.ingestion.fallback import FallbackManager

# Credential retrieval
from src.ingestion.credentials import get_bitopro_credentials

# Sensitive-data logging helpers
from src.ingestion.logging_config import SensitiveDataFilter, configure_sensitive_logging

# End-to-end orchestration
from src.ingestion.workflow import ingest_bitopro_data

__all__ = [
    # Models
    "HTTPMethod",
    "FieldType",
    "APIConfig",
    "APIRequest",
    "APIResponse",
    "FlattenedRecord",
    "FieldSchema",
    # Client
    "BitoProAPIClient",
    # Storage
    "StorageBackend",
    "S3Storage",
    "LocalStorage",
    "RawDataStorage",
    # Flattener
    "JSONFlattener",
    # Inferencer
    "SchemaInferencer",
    # Fallback
    "FallbackManager",
    # Credentials
    "get_bitopro_credentials",
    # Logging
    "SensitiveDataFilter",
    "configure_sensitive_logging",
    # Workflow
    "ingest_bitopro_data",
]
