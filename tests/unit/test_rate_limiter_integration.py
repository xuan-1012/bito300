"""
Integration tests for RateLimiter class.

These tests demonstrate the RateLimiter in realistic usage scenarios.
"""

import time
import pytest
from src.common.rate_limiter import RateLimiter


class TestRateLimiterIntegration:
    """Integration tests for RateLimiter."""
    
    def test_simulated_bedrock_api_calls(self):
        """
        Simulate multiple Bedrock API calls with rate limiting.
        
        This test simulates a realistic scenario where multiple accounts
        need to be analyzed using Bedrock API, ensuring rate limits are
        maintained throughout.
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # Simulate analyzing 5 accounts
        accounts = ["account_1", "account_2", "account_3", "account_4", "account_5"]
        results = []
        
        start_time = time.time()
        
        for account_id in accounts:
            # Wait if needed to maintain rate limit
            limiter.wait_if_needed()
            
            # Simulate Bedrock API call (instant for testing)
            result = {
                "account_id": account_id,
                "timestamp": time.time(),
                "risk_score": 50.0
            }
            results.append(result)
        
        total_time = time.time() - start_time
        
        # Verify all accounts were processed
        assert len(results) == len(accounts)
        
        # Verify rate limit was maintained (should take at least 4 * min_interval)
        expected_min_time = (len(accounts) - 1) * limiter.min_interval
        assert total_time >= expected_min_time * 0.9  # Allow 10% tolerance
        
        # Verify request count
        assert limiter.get_request_count() == len(accounts)
        
        # Verify intervals between consecutive requests
        for i in range(1, len(results)):
            interval = results[i]["timestamp"] - results[i-1]["timestamp"]
            assert interval >= 1.0, f"Interval {interval}s violates < 1 req/sec rule"
    
    def test_rate_limiter_with_error_retry(self):
        """
        Test rate limiter behavior with error retry logic.
        
        This simulates a scenario where an API call fails and needs to be
        retried, ensuring rate limits are still maintained.
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        attempts = []
        max_retries = 3
        
        for attempt in range(max_retries):
            limiter.wait_if_needed()
            attempts.append(time.time())
        
        # Verify all attempts were tracked
        assert limiter.get_request_count() == max_retries
        
        # Verify intervals
        for i in range(1, len(attempts)):
            interval = attempts[i] - attempts[i-1]
            assert interval >= 1.0
    
    def test_rate_limiter_reset_and_reuse(self):
        """
        Test resetting and reusing the rate limiter.
        
        This simulates processing multiple batches of accounts with
        rate limiter reset between batches.
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # First batch
        for _ in range(3):
            limiter.wait_if_needed()
        
        assert limiter.get_request_count() == 3
        
        # Reset for second batch
        limiter.reset()
        assert limiter.get_request_count() == 0
        
        # Second batch
        for _ in range(2):
            limiter.wait_if_needed()
        
        assert limiter.get_request_count() == 2
    
    def test_concurrent_rate_limiter_instances(self):
        """
        Test that multiple rate limiter instances work independently.
        
        This verifies that different components can use separate rate
        limiters without interference.
        """
        limiter1 = RateLimiter(max_requests_per_second=0.9)
        limiter2 = RateLimiter(max_requests_per_second=0.8)
        
        # Use limiter1
        limiter1.wait_if_needed()
        limiter1.wait_if_needed()
        
        # Use limiter2
        limiter2.wait_if_needed()
        
        # Verify independent tracking
        assert limiter1.get_request_count() == 2
        assert limiter2.get_request_count() == 1
        assert limiter1.min_interval != limiter2.min_interval
