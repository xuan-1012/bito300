"""
BitoPro API Client

This module provides a client for interacting with the BitoPro cryptocurrency
exchange API. It handles authentication, rate limiting, and error recovery
with exponential backoff retry logic.

**Validates: Requirements 1.1, 1.2, 1.5, 11.1**
"""

import time
import logging
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class BitoproClientError(Exception):
    """Custom exception for BitoPro API client errors."""
    pass


class BitoproClient:
    """
    Client for BitoPro cryptocurrency exchange API.
    
    This client handles:
    - API authentication using API key from AWS Secrets Manager
    - Transaction data retrieval with time range filtering
    - Exponential backoff retry logic (up to 3 attempts)
    - Common API error handling (timeout, rate limiting, authentication)
    
    Attributes:
        base_url: BitoPro API base URL
        api_key: API key for authentication
        api_secret: API secret for request signing
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """
    
    def __init__(
        self,
        aws_clients,
        secret_id: str = "bitopro-api-key",
        base_url: str = "https://api.bitopro.com/v3",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """
        Initialize BitoPro API client.
        
        Args:
            aws_clients: AWSClients instance for accessing Secrets Manager
            secret_id: Secrets Manager secret ID containing API credentials
            base_url: BitoPro API base URL
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Raises:
            BitoproClientError: If API credentials cannot be retrieved
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Retrieve API credentials from Secrets Manager
        try:
            secret = aws_clients.get_secret(secret_id)
            self.api_key = secret.get('api_key')
            self.api_secret = secret.get('api_secret')
            
            if not self.api_key or not self.api_secret:
                raise BitoproClientError(
                    "API credentials missing 'api_key' or 'api_secret' fields"
                )
            
            logger.info(
                f"BitoPro client initialized with secret_id={secret_id}, "
                f"base_url={base_url}, timeout={timeout}s, max_retries={max_retries}"
            )
            
        except (ClientError, Exception) as e:
            error_msg = f"Failed to retrieve BitoPro API credentials: {str(e)}"
            logger.error(error_msg)
            raise BitoproClientError(error_msg) from e
    
    def fetch_transactions(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch transactions from BitoPro API with retry logic.
        
        This method retrieves transaction data within the specified time range.
        It implements exponential backoff retry logic to handle transient failures.
        
        Args:
            start_time: Start of time range (optional, defaults to 24 hours ago)
            end_time: End of time range (optional, defaults to now)
            limit: Maximum number of transactions to fetch (default: 1000)
            
        Returns:
            List of transaction dictionaries
            
        Raises:
            BitoproClientError: If all retry attempts fail
        """
        # Set default time range if not provided
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            from datetime import timedelta
            start_time = end_time - timedelta(days=1)
        
        logger.info(
            f"Fetching transactions from {start_time.isoformat()} to "
            f"{end_time.isoformat()}, limit={limit}"
        )
        
        # Build request parameters
        params = {
            'startTime': int(start_time.timestamp() * 1000),  # Convert to milliseconds
            'endTime': int(end_time.timestamp() * 1000),
            'limit': limit
        }
        
        # Retry with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                transactions = self._make_request(
                    endpoint='/transactions',
                    params=params
                )
                
                logger.info(
                    f"Successfully fetched {len(transactions)} transactions "
                    f"(attempt {attempt}/{self.max_retries})"
                )
                
                return transactions
                
            except requests.exceptions.Timeout as e:
                logger.warning(
                    f"Request timeout on attempt {attempt}/{self.max_retries}: {str(e)}"
                )
                if attempt < self.max_retries:
                    self._exponential_backoff(attempt)
                else:
                    raise BitoproClientError(
                        f"Request timed out after {self.max_retries} attempts"
                    ) from e
            
            except requests.exceptions.RequestException as e:
                logger.warning(
                    f"Request failed on attempt {attempt}/{self.max_retries}: {str(e)}"
                )
                if attempt < self.max_retries:
                    self._exponential_backoff(attempt)
                else:
                    raise BitoproClientError(
                        f"Request failed after {self.max_retries} attempts: {str(e)}"
                    ) from e
            
            except BitoproClientError as e:
                # Don't retry on authentication errors
                if "authentication" in str(e).lower() or "unauthorized" in str(e).lower():
                    logger.error(f"Authentication error: {str(e)}")
                    raise
                
                # Retry on other BitoPro errors
                logger.warning(
                    f"BitoPro API error on attempt {attempt}/{self.max_retries}: {str(e)}"
                )
                if attempt < self.max_retries:
                    self._exponential_backoff(attempt)
                else:
                    raise
        
        # Should never reach here, but just in case
        raise BitoproClientError(
            f"Failed to fetch transactions after {self.max_retries} attempts"
        )
    
    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        method: str = 'GET'
    ) -> List[Dict[str, Any]]:
        """
        Make an authenticated request to BitoPro API.
        
        Args:
            endpoint: API endpoint (e.g., '/transactions')
            params: Query parameters
            method: HTTP method (default: GET)
            
        Returns:
            API response data
            
        Raises:
            BitoproClientError: If request fails or returns error
        """
        url = f"{self.base_url}{endpoint}"
        
        # Build headers with authentication
        headers = {
            'X-BITOPRO-APIKEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                params=params,
                headers=headers,
                timeout=self.timeout
            )
            
            # Log request details (without sensitive data)
            logger.debug(
                f"Request: {method} {url}, "
                f"params={params}, "
                f"status_code={response.status_code}"
            )
            
            # Handle rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise BitoproClientError(
                    f"Rate limit exceeded. Retry after {retry_after} seconds"
                )
            
            # Handle authentication errors (401 Unauthorized)
            if response.status_code == 401:
                raise BitoproClientError(
                    "Authentication failed. Check API key and secret"
                )
            
            # Handle other HTTP errors
            response.raise_for_status()
            
            # Parse JSON response
            try:
                data = response.json()
            except (json.JSONDecodeError, ValueError) as e:
                error_msg = f"Failed to parse JSON response: {str(e)}"
                logger.error(error_msg)
                raise BitoproClientError(error_msg) from e
            
            # Check for API-level errors
            if isinstance(data, dict) and 'error' in data:
                raise BitoproClientError(
                    f"API error: {data.get('error', 'Unknown error')}"
                )
            
            # Return data (assuming it's a list of transactions)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                logger.warning(f"Unexpected response format: {type(data)}")
                return []
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {str(e)}")
            raise
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise
    
    def _exponential_backoff(self, attempt: int) -> None:
        """
        Wait with exponential backoff before retry.
        
        Args:
            attempt: Current attempt number (1-indexed)
        """
        # Calculate backoff time: 2^attempt seconds (2s, 4s, 8s, ...)
        backoff_time = 2 ** attempt
        
        logger.info(
            f"Waiting {backoff_time}s before retry (attempt {attempt})"
        )
        
        time.sleep(backoff_time)
