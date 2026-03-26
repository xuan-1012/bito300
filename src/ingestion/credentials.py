"""
Secure credential retrieval for BitoPro API.

Retrieves API credentials from AWS Secrets Manager with in-process caching
to avoid repeated network calls.

Requirements: 12.1
"""

import json
import logging
import time
from typing import Optional, Tuple

import boto3
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

# Cache entry: (api_key, api_secret, expiry_timestamp)
_credential_cache: dict = {}
_CACHE_TTL_SECONDS: int = 300  # 5 minutes


def get_bitopro_credentials(
    secret_name: str,
    ttl_seconds: int = _CACHE_TTL_SECONDS,
    _secrets_client=None,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Retrieve BitoPro API credentials from AWS Secrets Manager.

    Credentials are cached in-process for *ttl_seconds* to avoid repeated
    Secrets Manager calls.  On any retrieval failure the function logs the
    error and returns (None, None) so callers can degrade gracefully.

    Args:
        secret_name: The Secrets Manager secret name or ARN.
        ttl_seconds: How long (in seconds) to cache the credentials.
        _secrets_client: Optional pre-built boto3 secretsmanager client
            (used in tests to inject a mock).

    Returns:
        Tuple of (api_key, api_secret).  Both values are None when the
        secret cannot be retrieved.

    Requirements: 12.1
    """
    now = time.monotonic()

    # Return cached credentials if still valid
    cached = _credential_cache.get(secret_name)
    if cached is not None:
        api_key, api_secret, expiry = cached
        if now < expiry:
            logger.debug("Returning cached credentials for secret '%s'", secret_name)
            return api_key, api_secret
        else:
            logger.debug("Cached credentials for secret '%s' have expired", secret_name)
            del _credential_cache[secret_name]

    # Fetch from Secrets Manager
    try:
        client = _secrets_client or boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_name)
        secret_string = response.get("SecretString")
        if not secret_string:
            logger.error(
                "Secret '%s' has no SecretString value", secret_name
            )
            return None, None

        secret_data = json.loads(secret_string)
        api_key = secret_data.get("api_key") or secret_data.get("apiKey")
        api_secret = secret_data.get("api_secret") or secret_data.get("apiSecret")

        if not api_key or not api_secret:
            logger.error(
                "Secret '%s' is missing 'api_key' or 'api_secret' fields", secret_name
            )
            return None, None

        # Store in cache
        _credential_cache[secret_name] = (api_key, api_secret, now + ttl_seconds)
        logger.info("Credentials for secret '%s' retrieved and cached", secret_name)
        return api_key, api_secret

    except (ClientError, BotoCoreError) as exc:
        logger.error(
            "Failed to retrieve credentials from Secrets Manager for secret '%s': %s",
            secret_name,
            exc,
        )
        return None, None
    except (json.JSONDecodeError, TypeError) as exc:
        logger.error(
            "Failed to parse credentials JSON for secret '%s': %s", secret_name, exc
        )
        return None, None
    except Exception as exc:  # pragma: no cover – unexpected errors
        logger.error(
            "Unexpected error retrieving credentials for secret '%s': %s",
            secret_name,
            exc,
        )
        return None, None


def clear_credential_cache(secret_name: Optional[str] = None) -> None:
    """
    Clear the in-process credential cache.

    Args:
        secret_name: If provided, clear only this secret's entry.
                     If None, clear the entire cache.
    """
    if secret_name is None:
        _credential_cache.clear()
        logger.debug("Entire credential cache cleared")
    else:
        _credential_cache.pop(secret_name, None)
        logger.debug("Credential cache cleared for secret '%s'", secret_name)
