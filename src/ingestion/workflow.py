"""
Main ingestion workflow orchestration.

Provides the `ingest_bitopro_data()` function that ties together all
ingestion components: API client, raw storage, JSON flattener, schema
inferencer, and fallback manager.
"""

import logging
from typing import Any, Dict, Optional

from src.ingestion.client import BitoProAPIClient
from src.ingestion.fallback import FallbackManager
from src.ingestion.flattener import JSONFlattener
from src.ingestion.inferencer import SchemaInferencer
from src.ingestion.models import HTTPMethod
from src.ingestion.storage import LocalStorage, RawDataStorage, S3Storage

logger = logging.getLogger(__name__)


def ingest_bitopro_data(
    endpoint: str,
    method: HTTPMethod = HTTPMethod.GET,
    params: Optional[Dict[str, Any]] = None,
    storage_backend: str = "local",  # "s3" or "local"
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    s3_bucket: Optional[str] = None,
    local_path: str = "raw_data/",
    schema_output_path: str = "schema.json",
) -> tuple:
    """
    Main data ingestion workflow.

    Orchestrates the full pipeline:
    1. Initialise all components
    2. Fetch data from the BitoPro API (with pagination and retry)
    3. Store each raw response to the configured storage backend
    4. Flatten all JSON structures
    5. Infer schema from the flattened data
    6. Export the schema to a JSON file
    7. Return (storage_uri, schema_path)

    Args:
        endpoint: BitoPro API endpoint path (e.g. "/v1/transactions").
        method: HTTP method to use (GET or POST).
        params: Query parameters (GET) or request body (POST).
        storage_backend: "local" for local filesystem, "s3" for AWS S3.
        api_key: Optional BitoPro API key for authenticated endpoints.
        api_secret: Optional BitoPro API secret for authenticated endpoints.
        s3_bucket: S3 bucket name (required when storage_backend="s3").
        local_path: Base directory for local storage (default: "raw_data/").
        schema_output_path: Output path for the inferred schema JSON file.

    Returns:
        Tuple of (storage_uri, schema_path).  Returns ("", "") on complete
        failure so callers can detect the error without an exception.

    Requirements: 1.1, 2.1, 3.1, 5.1, 7.1, 7.9
    """
    # ------------------------------------------------------------------
    # Step 0: Validate and sanitize inputs (Requirement 12.4)
    # ------------------------------------------------------------------
    if not endpoint or not isinstance(endpoint, str):
        logger.error("ingest_bitopro_data: endpoint must be a non-empty string")
        return ("", "")

    if not isinstance(method, HTTPMethod):
        logger.error("ingest_bitopro_data: method must be an HTTPMethod enum value")
        return ("", "")

    # Sanitize endpoint: reject path-traversal sequences
    if ".." in endpoint:
        logger.error(
            "ingest_bitopro_data: endpoint contains path traversal sequence: %s",
            endpoint,
        )
        return ("", "")

    # Sanitize endpoint: allow only safe URL characters
    import re as _re
    if not _re.match(r'^[A-Za-z0-9/_\-\.%~]*$', endpoint):
        logger.error(
            "ingest_bitopro_data: endpoint contains invalid characters: %s",
            endpoint,
        )
        return ("", "")

    # Validate params dict values for injection patterns
    if params is not None:
        if not isinstance(params, dict):
            logger.error("ingest_bitopro_data: params must be a dict or None")
            return ("", "")
        _INJECTION_PATTERN = _re.compile(
            r'[<>\'";]|--|\bOR\b|\bAND\b|\bDROP\b|\bSELECT\b|\bINSERT\b',
            _re.IGNORECASE,
        )
        for key, value in params.items():
            if isinstance(value, str) and _INJECTION_PATTERN.search(value):
                logger.error(
                    "ingest_bitopro_data: params value for key '%s' contains "
                    "potentially unsafe content",
                    key,
                )
                return ("", "")

    fallback_mgr = FallbackManager(logger=logger)

    # ------------------------------------------------------------------
    # Step 1: Initialise components
    # ------------------------------------------------------------------
    try:
        client = BitoProAPIClient(api_key=api_key, api_secret=api_secret)

        if storage_backend == "s3":
            if not s3_bucket:
                raise ValueError(
                    "s3_bucket must be provided when storage_backend='s3'"
                )
            backend = S3Storage(bucket_name=s3_bucket)
        else:
            backend = LocalStorage(base_path=local_path)

        storage = RawDataStorage(backend=backend)
        flattener = JSONFlattener()
        inferencer = SchemaInferencer()
    except Exception as exc:
        logger.error(
            "Failed to initialise ingestion components: %s", exc, exc_info=True
        )
        return ("", "")

    # ------------------------------------------------------------------
    # Step 2: Fetch data with pagination and retry
    # ------------------------------------------------------------------
    raw_responses = fallback_mgr.with_fallback(
        primary_func=lambda: client.fetch_data(
            endpoint=endpoint,
            method=method,
            params=params,
            paginate=True,
        ),
        default_value=[],
    )

    if not raw_responses:
        logger.error(
            "No data returned from endpoint '%s'. Aborting ingestion.", endpoint
        )
        return ("", "")

    # ------------------------------------------------------------------
    # Step 3: Store raw responses (complete, unmodified)
    # ------------------------------------------------------------------
    storage_uris = []
    for response in raw_responses:
        uri = fallback_mgr.with_fallback(
            primary_func=lambda r=response: storage.store_raw_response(
                response=r,
                endpoint=endpoint,
            ),
            default_value=None,
        )
        if uri:
            storage_uris.append(uri)

    # ------------------------------------------------------------------
    # Step 4: Flatten JSON structures
    # ------------------------------------------------------------------
    flattened_data = []
    for response in raw_responses:
        data_payload = response.get("data", response)
        records = fallback_mgr.with_fallback(
            primary_func=lambda d=data_payload: flattener.flatten(d),
            default_value=[],
        )
        flattened_data.extend(records)

    # ------------------------------------------------------------------
    # Step 5 & 6: Infer schema and export to JSON
    # ------------------------------------------------------------------
    schema_path = ""
    try:
        schema = inferencer.infer_schema(flattened_data)
        schema_path = inferencer.export_schema(schema, output_path=schema_output_path)
    except Exception as exc:
        logger.error("Schema inference/export failed: %s", exc, exc_info=True)

    # ------------------------------------------------------------------
    # Step 7: Return results
    # ------------------------------------------------------------------
    first_uri = storage_uris[0] if storage_uris else ""
    logger.info(
        "Ingestion complete: storage_uri=%s, schema_path=%s",
        first_uri,
        schema_path,
    )
    return (first_uri, schema_path)
