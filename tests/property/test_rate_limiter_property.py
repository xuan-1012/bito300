"""
Property-based tests for RateLimiter class.

**Property 4: Time between consecutive requests is always ≥ 1.0 seconds**
**Validates: Requirements 5.1, 5.2**

This module tests the RateLimiter using property-based testing with Hypothesis
to ensure rate limiting is maintained across a wide range of request patterns.
"""

import time
import pytest
from hypothesis import given, strategies as st, settings
from src.common.rate_limiter import RateLimiter


class TestRateLimiterProperties:
    """
    Property-based tests for RateLimiter.
    
    **Property 4: Time between consecutive requests is always ≥ 1.0 seconds**
    **Validates: Requirements 5.1, 5.2**
    """
    
    @given(st.integers(min_value=2, max_value=10))
    @settings(deadline=None)  # Disable deadline since we're testing timing
    def test_time_between_consecutive_requests_always_at_least_one_second(self, num_requests):
        """
        Property: Time between consecutive requests is always ≥ 1.0 seconds.
        
        This property test verifies that regardless of how many requests are made
        or how quickly they are attempted, the RateLimiter always ensures that
        at least 1.0 seconds elapses between consecutive requests.
        
        **Validates: Requirements 5.1, 5.2**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        timestamps = []
        
        # Make multiple requests as fast as possible
        for _ in range(num_requests):
            limiter.wait_if_needed()
            timestamps.append(time.time())
        
        # Verify that all consecutive request intervals are >= 1.0 seconds
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            assert interval >= 1.0, (
                f"Interval between request {i-1} and {i} was {interval:.6f}s, "
                f"which is less than 1.0s (violates Requirements 5.1, 5.2)"
            )
    
    @given(
        st.integers(min_value=2, max_value=8),
        st.floats(min_value=0.5, max_value=0.99)
    )
    @settings(deadline=None)
    def test_time_between_requests_with_various_max_rps(self, num_requests, max_rps):
        """
        Property: Time between consecutive requests is always ≥ 1.0 seconds
        for any valid max_requests_per_second value.
        
        This test verifies that the property holds regardless of the configured
        max_requests_per_second value (as long as it's < 1.0).
        
        **Validates: Requirements 5.1, 5.2**
        """
        limiter = RateLimiter(max_requests_per_second=max_rps)
        
        timestamps = []
        
        for _ in range(num_requests):
            limiter.wait_if_needed()
            timestamps.append(time.time())
        
        # Verify all intervals are >= 1.0 seconds
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            assert interval >= 1.0, (
                f"With max_rps={max_rps:.3f}, interval between request {i-1} and {i} "
                f"was {interval:.6f}s, which is less than 1.0s"
            )
    
    @given(st.lists(st.floats(min_value=0.0, max_value=0.5), min_size=1, max_size=5))
    @settings(deadline=None)
    def test_time_between_requests_with_variable_delays(self, delays):
        """
        Property: Time between consecutive requests is always ≥ 1.0 seconds
        even when requests are made with variable delays between them.
        
        This simulates a more realistic scenario where requests aren't made
        immediately one after another, but with some variable delays.
        
        **Validates: Requirements 5.1, 5.2**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        timestamps = []
        
        # First request
        limiter.wait_if_needed()
        timestamps.append(time.time())
        
        # Subsequent requests with delays
        for delay in delays:
            time.sleep(delay)
            limiter.wait_if_needed()
            timestamps.append(time.time())
        
        # Verify all intervals are >= 1.0 seconds
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            assert interval >= 1.0, (
                f"Interval between request {i-1} and {i} was {interval:.6f}s, "
                f"which is less than 1.0s"
            )
    
    @given(st.integers(min_value=2, max_value=6))
    @settings(deadline=None)
    def test_minimum_interval_enforced_after_reset(self, num_requests):
        """
        Property: Time between consecutive requests is always ≥ 1.0 seconds
        even after resetting the rate limiter.
        
        This verifies that the property holds across rate limiter resets.
        
        **Validates: Requirements 5.1, 5.2**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        all_timestamps = []
        
        # First batch of requests
        batch1_size = num_requests // 2
        for _ in range(batch1_size):
            limiter.wait_if_needed()
            all_timestamps.append(time.time())
        
        # Reset the limiter
        limiter.reset()
        
        # Second batch of requests
        batch2_size = num_requests - batch1_size
        for _ in range(batch2_size):
            limiter.wait_if_needed()
            all_timestamps.append(time.time())
        
        # Verify intervals within each batch
        # Note: We don't check interval across reset boundary since reset
        # allows immediate first request
        
        # Check batch 1 intervals
        for i in range(1, batch1_size):
            interval = all_timestamps[i] - all_timestamps[i-1]
            assert interval >= 1.0, (
                f"Batch 1: Interval between request {i-1} and {i} was {interval:.6f}s"
            )
        
        # Check batch 2 intervals
        for i in range(batch1_size + 1, len(all_timestamps)):
            interval = all_timestamps[i] - all_timestamps[i-1]
            assert interval >= 1.0, (
                f"Batch 2: Interval between request {i-1} and {i} was {interval:.6f}s"
            )
