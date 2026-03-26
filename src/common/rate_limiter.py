"""
Rate limiter for Bedrock API calls.

This module provides a RateLimiter class to ensure compliance with
Bedrock API rate limits (< 1 request/second).
"""

import time
import logging
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter to ensure < 1 request/second for Bedrock API.
    
    This class enforces rate limiting by tracking the time between consecutive
    requests and waiting if necessary to maintain the minimum interval.
    Thread-safe using a lock to prevent race conditions.
    
    Attributes:
        max_rps: Maximum requests per second (must be < 1.0)
        min_interval: Minimum time interval between requests in seconds
        last_request_time: Timestamp of the last request
        request_count: Total number of requests processed
        lock: Threading lock for thread-safe operations
    """
    
    def __init__(self, max_requests_per_second: float = 0.9):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests_per_second: Maximum requests per second (default: 0.9)
        
        Raises:
            ValueError: If max_requests_per_second >= 1.0
        """
        if max_requests_per_second >= 1.0:
            raise ValueError(
                f"max_requests_per_second must be < 1.0, got {max_requests_per_second}"
            )
        
        self.max_rps = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0.0
        self.request_count = 0
        self.lock = Lock()  # Thread-safe locking mechanism
    
    def wait_if_needed(self) -> float:
        """
        Wait if necessary to maintain rate limit.
        
        This method ensures that the minimum interval between consecutive
        requests is maintained. If a request is made too soon, it will
        sleep until the minimum interval has elapsed.
        
        The wait time is logged to CloudWatch for monitoring purposes.
        Thread-safe using a lock to prevent race conditions.
        
        Returns:
            Actual wait time in seconds (0.0 if no wait was needed)
        """
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                logger.info(
                    f"Rate limit: waiting {sleep_time:.3f}s to maintain < 1 req/sec "
                    f"(min_interval={self.min_interval:.3f}s)"
                )
                time.sleep(sleep_time)
                self.last_request_time = time.time()
                self.request_count += 1
                
                logger.debug(
                    f"Rate limiter: request #{self.request_count}, "
                    f"waited {sleep_time:.3f}s"
                )
                return sleep_time
            else:
                self.last_request_time = current_time
                self.request_count += 1
                
                logger.debug(
                    f"Rate limiter: request #{self.request_count}, "
                    f"interval={time_since_last:.3f}s"
                )
                return 0.0
    
    def get_request_count(self) -> int:
        """
        Get the total number of requests processed.
        
        Returns:
            Total number of requests tracked by this rate limiter
        """
        return self.request_count
    
    def get_current_rate(self) -> float:
        """
        Get the current request frequency.
        
        Calculates the current rate based on the time elapsed since
        the last request. If no requests have been made yet, returns 0.0.
        
        Returns:
            Current request frequency in requests per second
        """
        with self.lock:
            if self.last_request_time == 0.0 or self.request_count == 0:
                return 0.0
            
            current_time = time.time()
            time_since_last = current_time - self.last_request_time
            
            # If time_since_last is 0, we just made a request
            if time_since_last == 0.0:
                # Return the configured max rate
                return self.max_rps
            
            # Calculate instantaneous rate (1 / time_since_last)
            # This represents how fast we could make the next request
            instantaneous_rate = 1.0 / (time_since_last + self.min_interval)
            
            # Cap at max_rps
            return min(instantaneous_rate, self.max_rps)
    
    def reset(self) -> None:
        """
        Reset the rate limiter state.
        
        This resets the last request time and request count.
        Useful for testing or when starting a new batch of requests.
        Thread-safe using a lock.
        """
        with self.lock:
            self.last_request_time = 0.0
            self.request_count = 0
            logger.info("Rate limiter reset")
