"""
Unit tests for RateLimiter class.
"""

import time
import pytest
from unittest.mock import patch, MagicMock
from src.common.rate_limiter import RateLimiter


class TestRateLimiterInitialization:
    """Test RateLimiter initialization."""
    
    def test_init_with_default_max_rps(self):
        """Test initialization with default max_requests_per_second."""
        limiter = RateLimiter()
        assert limiter.max_rps == 0.9
        assert limiter.min_interval == pytest.approx(1.0 / 0.9, rel=1e-6)
        assert limiter.last_request_time == 0.0
        assert limiter.request_count == 0
    
    def test_init_with_custom_max_rps(self):
        """Test initialization with custom max_requests_per_second."""
        limiter = RateLimiter(max_requests_per_second=0.5)
        assert limiter.max_rps == 0.5
        assert limiter.min_interval == pytest.approx(2.0, rel=1e-6)
        assert limiter.last_request_time == 0.0
        assert limiter.request_count == 0
    
    def test_init_with_invalid_max_rps(self):
        """Test initialization fails when max_requests_per_second >= 1.0."""
        with pytest.raises(ValueError, match="must be < 1.0"):
            RateLimiter(max_requests_per_second=1.0)
        
        with pytest.raises(ValueError, match="must be < 1.0"):
            RateLimiter(max_requests_per_second=1.5)


class TestRateLimiterWaitIfNeeded:
    """Test RateLimiter wait_if_needed method."""
    
    def test_first_request_no_wait(self):
        """Test that first request does not wait."""
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        # First request should not wait
        assert elapsed < 0.1
        assert limiter.request_count == 1
        assert limiter.last_request_time > 0
    
    def test_second_request_waits_if_too_soon(self):
        """Test that second request waits if made too soon."""
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # First request
        limiter.wait_if_needed()
        
        # Second request immediately after
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        # Should wait approximately min_interval seconds
        expected_wait = limiter.min_interval
        assert elapsed >= expected_wait * 0.9  # Allow 10% tolerance
        assert limiter.request_count == 2
    
    def test_second_request_no_wait_if_enough_time_passed(self):
        """Test that second request does not wait if enough time has passed."""
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # First request
        limiter.wait_if_needed()
        
        # Wait for min_interval
        time.sleep(limiter.min_interval + 0.1)
        
        # Second request
        start_time = time.time()
        limiter.wait_if_needed()
        elapsed = time.time() - start_time
        
        # Should not wait
        assert elapsed < 0.1
        assert limiter.request_count == 2
    
    @patch('src.common.rate_limiter.logger')
    def test_logs_wait_time(self, mock_logger):
        """Test that wait time is logged to CloudWatch."""
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # First request
        limiter.wait_if_needed()
        
        # Second request immediately after (should wait)
        limiter.wait_if_needed()
        
        # Check that info log was called with wait time
        assert mock_logger.info.called
        log_message = mock_logger.info.call_args[0][0]
        assert "Rate limit: waiting" in log_message
        assert "req/sec" in log_message
    
    def test_multiple_requests_maintain_rate_limit(self):
        """Test that multiple requests maintain rate limit."""
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        start_time = time.time()
        num_requests = 5
        
        for _ in range(num_requests):
            limiter.wait_if_needed()
        
        elapsed = time.time() - start_time
        
        # Total time should be at least (num_requests - 1) * min_interval
        expected_min_time = (num_requests - 1) * limiter.min_interval
        assert elapsed >= expected_min_time * 0.9  # Allow 10% tolerance
        assert limiter.request_count == num_requests


class TestRateLimiterRequestCount:
    """Test RateLimiter request count tracking."""
    
    def test_get_request_count_initial(self):
        """Test get_request_count returns 0 initially."""
        limiter = RateLimiter()
        assert limiter.get_request_count() == 0
    
    def test_get_request_count_after_requests(self):
        """Test get_request_count returns correct count after requests."""
        limiter = RateLimiter(max_requests_per_second=0.5)
        
        for i in range(3):
            limiter.wait_if_needed()
            assert limiter.get_request_count() == i + 1


class TestRateLimiterReset:
    """Test RateLimiter reset functionality."""
    
    def test_reset_clears_state(self):
        """Test that reset clears the rate limiter state."""
        limiter = RateLimiter()
        
        # Make some requests
        limiter.wait_if_needed()
        limiter.wait_if_needed()
        
        assert limiter.request_count > 0
        assert limiter.last_request_time > 0
        
        # Reset
        limiter.reset()
        
        assert limiter.request_count == 0
        assert limiter.last_request_time == 0.0
    
    @patch('src.common.rate_limiter.logger')
    def test_reset_logs_message(self, mock_logger):
        """Test that reset logs a message."""
        limiter = RateLimiter()
        limiter.reset()
        
        mock_logger.info.assert_called_with("Rate limiter reset")


class TestRateLimiterCompliance:
    """Test RateLimiter compliance with requirements."""
    
    def test_ensures_less_than_one_request_per_second(self):
        """
        Test that rate limiter ensures < 1 request/second.
        
        **Validates: Requirements 3.1, 3.7**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        timestamps = []
        for _ in range(3):
            limiter.wait_if_needed()
            timestamps.append(time.time())
        
        # Check intervals between consecutive requests
        for i in range(1, len(timestamps)):
            interval = timestamps[i] - timestamps[i-1]
            assert interval >= 1.0, f"Interval {interval}s is less than 1.0s"
    
    def test_waits_until_minimum_interval_satisfied(self):
        """
        Test that rate limiter waits until minimum interval is satisfied.
        
        **Validates: Requirements 3.2, 3.3**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # First request
        limiter.wait_if_needed()
        first_time = limiter.last_request_time
        
        # Second request immediately (should wait)
        limiter.wait_if_needed()
        second_time = limiter.last_request_time
        
        # Verify minimum interval was satisfied
        interval = second_time - first_time
        assert interval >= limiter.min_interval * 0.99  # Allow small tolerance
    
    @patch('src.common.rate_limiter.logger')
    def test_logs_wait_time_to_cloudwatch(self, mock_logger):
        """
        Test that wait time is logged to CloudWatch.
        
        **Validates: Requirements 3.9**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # First request
        limiter.wait_if_needed()
        
        # Second request (should wait and log)
        limiter.wait_if_needed()
        
        # Verify logging occurred
        assert mock_logger.info.called
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        wait_logs = [log for log in log_calls if "Rate limit: waiting" in log]
        assert len(wait_logs) > 0, "No wait time logged"
    
    def test_tracks_number_of_requests(self):
        """
        Test that rate limiter tracks number of requests.
        
        **Validates: Requirements 3.5**
        """
        limiter = RateLimiter(max_requests_per_second=0.5)
        
        num_requests = 4
        for _ in range(num_requests):
            limiter.wait_if_needed()
        
        assert limiter.get_request_count() == num_requests


class TestRateLimiterThreadSafety:
    """Test RateLimiter thread safety."""
    
    def test_thread_safe_locking_mechanism(self):
        """
        Test that rate limiter uses thread-safe locking.
        
        **Validates: Requirements 3.6**
        """
        import threading
        
        limiter = RateLimiter(max_requests_per_second=0.5)
        timestamps = []
        lock = threading.Lock()
        
        def make_request():
            limiter.wait_if_needed()
            with lock:
                timestamps.append(time.time())
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests were processed
        assert len(timestamps) == 3
        assert limiter.get_request_count() == 3
        
        # Verify intervals between consecutive requests
        sorted_timestamps = sorted(timestamps)
        for i in range(1, len(sorted_timestamps)):
            interval = sorted_timestamps[i] - sorted_timestamps[i-1]
            assert interval >= 1.0, f"Interval {interval}s is less than 1.0s"
    
    def test_concurrent_wait_if_needed_calls(self):
        """
        Test that concurrent wait_if_needed calls are handled safely.
        
        **Validates: Requirements 3.6**
        """
        import threading
        
        limiter = RateLimiter(max_requests_per_second=0.9)
        results = []
        lock = threading.Lock()
        
        def make_requests(num_requests):
            for _ in range(num_requests):
                wait_time = limiter.wait_if_needed()
                with lock:
                    results.append({
                        'thread': threading.current_thread().name,
                        'wait_time': wait_time,
                        'timestamp': time.time()
                    })
        
        # Create two threads making requests concurrently
        threads = [
            threading.Thread(target=make_requests, args=(2,), name='Thread-1'),
            threading.Thread(target=make_requests, args=(2,), name='Thread-2')
        ]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all requests were processed
        assert len(results) == 4
        assert limiter.get_request_count() == 4


class TestRateLimiterGetCurrentRate:
    """Test RateLimiter get_current_rate method."""
    
    def test_get_current_rate_initial(self):
        """
        Test get_current_rate returns 0.0 initially.
        
        **Validates: Requirements 3.10**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        assert limiter.get_current_rate() == 0.0
    
    def test_get_current_rate_after_request(self):
        """
        Test get_current_rate returns correct rate after request.
        
        **Validates: Requirements 3.10**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # Make a request
        limiter.wait_if_needed()
        
        # Immediately check rate (should be at max)
        rate = limiter.get_current_rate()
        assert rate <= limiter.max_rps
        assert rate >= 0.0
    
    def test_get_current_rate_after_waiting(self):
        """
        Test get_current_rate returns correct rate after waiting.
        
        **Validates: Requirements 3.10**
        """
        limiter = RateLimiter(max_requests_per_second=0.9)
        
        # Make a request
        limiter.wait_if_needed()
        
        # Wait some time
        time.sleep(2.0)
        
        # Check rate (should be lower since time has passed)
        rate = limiter.get_current_rate()
        assert rate <= limiter.max_rps
        assert rate >= 0.0
    
    def test_get_current_rate_thread_safe(self):
        """
        Test get_current_rate is thread-safe.
        
        **Validates: Requirements 3.6, 3.10**
        """
        import threading
        
        limiter = RateLimiter(max_requests_per_second=0.9)
        rates = []
        lock = threading.Lock()
        
        def check_rate():
            limiter.wait_if_needed()
            rate = limiter.get_current_rate()
            with lock:
                rates.append(rate)
        
        # Create multiple threads
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=check_rate)
            threads.append(thread)
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all rates are valid
        assert len(rates) == 3
        for rate in rates:
            assert 0.0 <= rate <= limiter.max_rps
