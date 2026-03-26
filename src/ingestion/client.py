"""
BitoProAPIClient - HTTP client for BitoPro API communication

This module provides the HTTP client for communicating with the BitoPro API,
including authentication, retry logic, rate limiting, and pagination handling.
"""

import logging
from typing import Dict, List, Any, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .models import APIConfig, HTTPMethod


logger = logging.getLogger(__name__)


class BitoProAPIClient:
    """
    HTTP client for BitoPro API communication
    
    Handles authentication, retry logic, rate limiting, and pagination.
    Uses HTTPS exclusively for security (Requirement 12.2).
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        config: Optional[APIConfig] = None
    ):
        """
        Initialize BitoPro API client
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            config: API configuration (uses defaults if not provided)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.config = config or APIConfig()
        
        # Initialize requests session with connection pooling
        self.session = self._create_session()
        
        # Rate limiting: track last request timestamp
        self._last_request_time: Optional[float] = None
        
        logger.info(
            f"BitoProAPIClient initialized with base_url={self.config.base_url}, "
            f"timeout={self.config.timeout}s, max_retries={self.config.max_retries}, "
            f"rate_limit={self.config.rate_limit_per_second} req/s"
        )
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with connection pooling and retry configuration
        
        Returns:
            Configured requests.Session with connection pooling
        """
        session = requests.Session()
        
        # Configure connection pooling and retry strategy
        # HTTPAdapter provides connection pooling automatically
        adapter = HTTPAdapter(
            pool_connections=10,  # Number of connection pools to cache
            pool_maxsize=10,      # Maximum number of connections to save in the pool
            max_retries=0         # We handle retries manually in _execute_request
        )
        
        # Mount adapter for both HTTP and HTTPS
        # Note: We only use HTTPS in practice (Requirement 12.2)
        session.mount("https://", adapter)
        session.mount("http://", adapter)
        
        return session
    
    def _build_headers(
        self,
        custom_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Build HTTP headers with authentication
        
        Args:
            custom_headers: Additional HTTP headers to include
            
        Returns:
            Dictionary of HTTP headers including authentication
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        # Add authentication headers if credentials are provided
        if self.api_key:
            headers["X-BITOPRO-APIKEY"] = self.api_key
        
        if self.api_secret:
            headers["X-BITOPRO-APISECRET"] = self.api_secret
        
        # Merge custom headers (they can override defaults)
        if custom_headers:
            headers.update(custom_headers)
        
        return headers
    
    def _enforce_rate_limit(self):
        """
        Enforce rate limiting before making a request
        
        Calculates the minimum interval between requests based on
        rate_limit_per_second and waits if necessary to maintain compliance.
        
        For example:
        - rate_limit_per_second = 0.9 => minimum interval = 1.11 seconds
        - rate_limit_per_second = 1.0 => minimum interval = 1.0 seconds
        - rate_limit_per_second = 2.0 => minimum interval = 0.5 seconds
        
        Requirements: 4.1, 4.2, 4.3, 4.4
        """
        import time
        
        # Calculate minimum interval between requests (in seconds)
        min_interval = 1.0 / self.config.rate_limit_per_second
        
        # If this is not the first request, check if we need to wait
        if self._last_request_time is not None:
            current_time = time.time()
            elapsed = current_time - self._last_request_time
            
            # If not enough time has passed, wait for the remaining time
            if elapsed < min_interval:
                wait_time = min_interval - elapsed
                logger.debug(
                    f"Rate limit: waiting {wait_time:.3f}s "
                    f"(min_interval={min_interval:.3f}s, elapsed={elapsed:.3f}s)"
                )
                time.sleep(wait_time)
        
        # Update last request timestamp
        self._last_request_time = time.time()
    
    def _detect_pagination_info(self, response: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Detect pagination information in API response
        
        Supports common pagination patterns:
        - next_page / next / nextPage field
        - page/total_pages fields
        - offset/limit fields
        - cursor-based pagination
        
        Args:
            response: API response dictionary
            
        Returns:
            Dictionary with pagination info, or None if no pagination detected
        """
        # Check for common pagination field names
        pagination_keys = [
            'pagination', 'paging', 'page_info', 'pageInfo',
            'next_page', 'next', 'nextPage', 'next_url',
            'has_more', 'hasMore'
        ]
        
        # Look for pagination info in response
        for key in pagination_keys:
            if key in response:
                return {
                    'type': 'field',
                    'key': key,
                    'value': response[key]
                }
        
        # Check for page/total_pages pattern
        if 'page' in response and 'total_pages' in response:
            current_page = response.get('page', 0)
            total_pages = response.get('total_pages', 0)
            has_next = current_page < total_pages
            return {
                'type': 'page_total',
                'current_page': current_page,
                'total_pages': total_pages,
                'has_next': has_next
            }
        
        # Check for offset/limit pattern
        if 'offset' in response and 'limit' in response and 'total' in response:
            offset = response.get('offset', 0)
            limit = response.get('limit', 0)
            total = response.get('total', 0)
            has_next = (offset + limit) < total
            return {
                'type': 'offset_limit',
                'offset': offset,
                'limit': limit,
                'total': total,
                'has_next': has_next,
                'next_offset': offset + limit if has_next else None
            }
        
        # No pagination detected
        return None
    
    def _has_next_page(self, pagination_info: Optional[Dict[str, Any]]) -> bool:
        """
        Check if there is a next page based on pagination info
        
        Args:
            pagination_info: Pagination information from _detect_pagination_info
            
        Returns:
            True if there is a next page, False otherwise
        """
        if not pagination_info:
            return False
        
        pagination_type = pagination_info.get('type')
        
        if pagination_type == 'field':
            value = pagination_info.get('value')
            # Check if value indicates more pages
            if isinstance(value, bool):
                return value
            elif isinstance(value, str):
                return bool(value)  # Non-empty string means next page exists
            elif isinstance(value, dict):
                # Check for has_more or similar fields
                return value.get('has_more', False) or value.get('hasMore', False)
            return False
        
        elif pagination_type == 'page_total':
            return pagination_info.get('has_next', False)
        
        elif pagination_type == 'offset_limit':
            return pagination_info.get('has_next', False)
        
        return False
    
    def _update_params_for_next_page(
        self,
        params: Optional[Dict[str, Any]],
        pagination_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update request parameters for fetching the next page
        
        Args:
            params: Current request parameters
            pagination_info: Pagination information from _detect_pagination_info
            
        Returns:
            Updated parameters for next page request
        """
        next_params = params.copy() if params else {}
        pagination_type = pagination_info.get('type')
        
        if pagination_type == 'field':
            value = pagination_info.get('value')
            key = pagination_info.get('key')
            
            if isinstance(value, str):
                # Direct URL or token
                next_params['next_page'] = value
            elif isinstance(value, dict):
                # Extract next page info from dict
                if 'next_page' in value:
                    next_params['page'] = value['next_page']
                elif 'next' in value:
                    next_params['page'] = value['next']
                elif 'cursor' in value:
                    next_params['cursor'] = value['cursor']
        
        elif pagination_type == 'page_total':
            current_page = pagination_info.get('current_page', 0)
            next_params['page'] = current_page + 1
        
        elif pagination_type == 'offset_limit':
            next_offset = pagination_info.get('next_offset')
            if next_offset is not None:
                next_params['offset'] = next_offset
        
        return next_params
    
    def fetch_data(
        self,
        endpoint: str,
        method: HTTPMethod = HTTPMethod.GET,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        paginate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Fetch data from BitoPro API with retry and pagination
        
        Main entry point for fetching data from BitoPro API. Orchestrates
        header building, request execution, and pagination handling.
        
        Args:
            endpoint: API endpoint path (e.g., "/v1/transactions")
            method: HTTP method (GET or POST)
            params: Query parameters (GET) or request body (POST)
            headers: Additional HTTP headers
            paginate: Whether to automatically handle pagination
            
        Returns:
            List of response data (aggregated if paginated)
            
        Requirements: 1.1, 1.2, 9.1, 9.2, 11.1
        """
        # Validate input parameters (Requirement 9.1, 9.2)
        if not endpoint or not isinstance(endpoint, str):
            logger.error("Invalid endpoint: must be non-empty string")
            return []
        
        if not isinstance(method, HTTPMethod):
            logger.error(f"Invalid HTTP method: {method}")
            return []
        
        # Log request details (Requirement 11.1)
        logger.info(
            f"fetch_data called: endpoint={endpoint}, method={method.value}, "
            f"paginate={paginate}, params={params}"
        )
        
        # Build full URL
        url = f"{self.config.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Build headers with authentication (Requirement 1.1, 1.3)
        request_headers = self._build_headers(custom_headers=headers)
        
        # Initialize results list
        all_results = []
        current_params = params.copy() if params else {}
        page_count = 0
        
        # Fetch data with pagination handling
        while True:
            page_count += 1
            
            # Log request details (Requirement 11.1)
            logger.info(
                f"Executing request: url={url}, method={method.value}, "
                f"page={page_count}, params={current_params}"
            )
            
            # Execute HTTP request with retry logic (Requirement 1.2)
            response_data = self._execute_request(
                url=url,
                method=method,
                headers=request_headers,
                params=current_params
            )
            
            # Check if request failed (empty response)
            if not response_data:
                logger.warning(
                    f"Request to {endpoint} returned empty response on page {page_count}. "
                    f"Stopping pagination."
                )
                break
            
            # Log response (Requirement 11.1)
            logger.info(
                f"Received response from {endpoint}: page={page_count}, "
                f"data_keys={list(response_data.keys())}"
            )
            
            # Add response to results
            all_results.append(response_data)
            
            # Handle pagination if enabled (Requirement 3.1, 3.2, 3.3, 3.4, 3.5)
            if not paginate:
                logger.info("Pagination disabled, returning first page only")
                break
            
            # Detect pagination information
            pagination_info = self._detect_pagination_info(response_data)
            
            if pagination_info:
                logger.debug(f"Pagination info detected: {pagination_info}")
            
            # Check if there's a next page
            if not self._has_next_page(pagination_info):
                logger.info(
                    f"No more pages available. Total pages fetched: {page_count}"
                )
                break
            
            # Update parameters for next page
            current_params = self._update_params_for_next_page(
                current_params,
                pagination_info
            )
            
            logger.info(
                f"Fetching next page with updated params: {current_params}"
            )
        
        # Log final summary (Requirement 11.1)
        logger.info(
            f"fetch_data completed: endpoint={endpoint}, "
            f"total_pages={page_count}, total_responses={len(all_results)}"
        )
        
        return all_results
    
    def _execute_request(
        self,
        url: str,
        method: HTTPMethod,
        headers: Dict[str, str],
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with retry logic
        
        Implements exponential backoff retry mechanism for retryable errors:
        - 5xx status codes (server errors)
        - Timeouts (requests.Timeout)
        - Network errors (requests.ConnectionError, requests.RequestException)
        
        Args:
            url: Full URL to request
            method: HTTP method
            headers: HTTP headers
            params: Query parameters (GET) or request body (POST)
            
        Returns:
            Response data as dictionary, or empty dict if all retries exhausted
        """
        import time
        
        for attempt in range(self.config.max_retries + 1):
            try:
                # Enforce rate limiting before making the request
                self._enforce_rate_limit()
                
                # Execute the HTTP request
                if method == HTTPMethod.GET:
                    response = self.session.get(
                        url,
                        headers=headers,
                        params=params,
                        timeout=self.config.timeout
                    )
                elif method == HTTPMethod.POST:
                    response = self.session.post(
                        url,
                        headers=headers,
                        json=params,
                        timeout=self.config.timeout
                    )
                else:
                    logger.error(f"Unsupported HTTP method: {method}")
                    return {}
                
                # Check for 5xx errors (retryable)
                if 500 <= response.status_code < 600:
                    if attempt < self.config.max_retries:
                        # Calculate exponential backoff delay
                        delay = self.config.retry_backoff ** attempt
                        logger.warning(
                            f"Request to {url} failed with status {response.status_code}. "
                            f"Retry attempt {attempt + 1}/{self.config.max_retries}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        time.sleep(delay)
                        continue
                    else:
                        # All retries exhausted
                        logger.error(
                            f"Request to {url} failed with status {response.status_code}. "
                            f"All {self.config.max_retries} retry attempts exhausted. "
                            f"Returning empty result."
                        )
                        return {}
                
                # Success - return response data
                response.raise_for_status()  # Raise for 4xx errors (non-retryable)
                return response.json()
                
            except requests.Timeout:
                # Timeout is retryable
                if attempt < self.config.max_retries:
                    delay = self.config.retry_backoff ** attempt
                    logger.warning(
                        f"Request to {url} timed out after {self.config.timeout}s. "
                        f"Retry attempt {attempt + 1}/{self.config.max_retries}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"Request to {url} timed out. "
                        f"All {self.config.max_retries} retry attempts exhausted. "
                        f"Returning empty result."
                    )
                    return {}
            
            except requests.HTTPError as e:
                # 4xx errors are not retryable - fail immediately
                logger.error(
                    f"Request to {url} failed with HTTP error: {str(e)}. "
                    f"Status code: {e.response.status_code}. "
                    f"Not retrying (client error)."
                )
                return {}
                    
            except (requests.ConnectionError, requests.RequestException) as e:
                # Network errors are retryable
                if attempt < self.config.max_retries:
                    delay = self.config.retry_backoff ** attempt
                    logger.warning(
                        f"Request to {url} failed with network error: {str(e)}. "
                        f"Retry attempt {attempt + 1}/{self.config.max_retries}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    time.sleep(delay)
                    continue
                else:
                    logger.error(
                        f"Request to {url} failed with network error: {str(e)}. "
                        f"All {self.config.max_retries} retry attempts exhausted. "
                        f"Returning empty result."
                    )
                    return {}
            
            except Exception as e:
                # Unexpected errors - log and return empty
                logger.error(
                    f"Request to {url} failed with unexpected error: {str(e)}. "
                    f"Not retrying."
                )
                return {}
        
        # Should not reach here, but return empty dict as fallback
        return {}
    
    def close(self):
        """Close the HTTP session and release resources"""
        if self.session:
            self.session.close()
            logger.info("BitoProAPIClient session closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close session"""
        self.close()
