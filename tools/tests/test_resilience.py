"""Tests for resilience module - retry logic and circuit breaker."""

import pytest
import time
from unittest.mock import Mock
from ce.resilience import (
    retry_with_backoff,
    CircuitBreaker,
    CircuitBreakerOpenError
)


class TestRetryWithBackoff:
    """Test retry decorator with exponential backoff."""

    def test_success_on_first_attempt(self):
        """Test that successful call on first attempt returns immediately."""
        mock_func = Mock(return_value="success")
        decorated = retry_with_backoff(max_attempts=3)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_success_on_second_attempt(self):
        """Test that function retries once before succeeding."""
        mock_func = Mock(side_effect=[ConnectionError("fail"), "success"])
        decorated = retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            exceptions=(ConnectionError,)
        )(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_failure_after_max_attempts(self):
        """Test that function fails after exhausting retries."""
        mock_func = Mock(side_effect=ConnectionError("persistent failure"))
        decorated = retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            exceptions=(ConnectionError,)
        )(mock_func)

        with pytest.raises(RuntimeError) as exc_info:
            decorated()

        assert "Failed after 3 attempts" in str(exc_info.value)
        assert "persistent failure" in str(exc_info.value)
        assert mock_func.call_count == 3

    def test_exponential_backoff_timing(self):
        """Test that backoff delay increases exponentially."""
        mock_func = Mock(side_effect=[
            ConnectionError("fail1"),
            ConnectionError("fail2"),
            "success"
        ])

        start_time = time.time()
        decorated = retry_with_backoff(
            max_attempts=3,
            base_delay=0.1,
            exponential_base=2.0,
            exceptions=(ConnectionError,)
        )(mock_func)

        result = decorated()
        elapsed = time.time() - start_time

        assert result == "success"
        # Should wait: 0.1s (first retry) + 0.2s (second retry) = ~0.3s
        assert 0.25 < elapsed < 0.4

    def test_non_retryable_exception_propagates_immediately(self):
        """Test that exceptions not in retry list propagate immediately."""
        mock_func = Mock(side_effect=ValueError("not retryable"))
        decorated = retry_with_backoff(
            max_attempts=3,
            base_delay=0.01,
            exceptions=(ConnectionError,)
        )(mock_func)

        with pytest.raises(ValueError) as exc_info:
            decorated()

        assert "not retryable" in str(exc_info.value)
        assert mock_func.call_count == 1  # No retries

    def test_max_delay_cap(self):
        """Test that backoff delay is capped at max_delay."""
        mock_func = Mock(side_effect=[
            ConnectionError("fail1"),
            ConnectionError("fail2"),
            "success"
        ])

        start_time = time.time()
        decorated = retry_with_backoff(
            max_attempts=3,
            base_delay=1.0,
            max_delay=0.15,  # Cap at 150ms
            exponential_base=2.0,
            exceptions=(ConnectionError,)
        )(mock_func)

        result = decorated()
        elapsed = time.time() - start_time

        assert result == "success"
        # Both retries should use max_delay (0.15s each) = ~0.3s
        assert 0.25 < elapsed < 0.4


class TestCircuitBreaker:
    """Test circuit breaker state machine."""

    def test_closed_state_allows_calls(self):
        """Test that closed circuit allows normal operation."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)
        mock_func = Mock(return_value="success")
        decorated = breaker.call(mock_func)

        result = decorated()

        assert result == "success"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0

    def test_circuit_opens_after_threshold_failures(self):
        """Test that circuit opens after failure threshold exceeded."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)
        mock_func = Mock(side_effect=ConnectionError("fail"))
        decorated = breaker.call(mock_func)

        # Trigger failures up to threshold
        for _ in range(3):
            with pytest.raises(ConnectionError):
                decorated()

        assert breaker.state == "open"
        assert breaker.failure_count == 3

    def test_open_circuit_fails_fast(self):
        """Test that open circuit rejects calls immediately."""
        breaker = CircuitBreaker(name="test", failure_threshold=2)
        mock_func = Mock(side_effect=ConnectionError("fail"))
        decorated = breaker.call(mock_func)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ConnectionError):
                decorated()

        # Next call should fail fast without calling function
        call_count_before = mock_func.call_count
        with pytest.raises(CircuitBreakerOpenError) as exc_info:
            decorated()

        assert mock_func.call_count == call_count_before  # No additional call
        assert "Circuit breaker 'test' is OPEN" in str(exc_info.value)

    def test_half_open_transition_after_timeout(self):
        """Test that circuit transitions to half-open after recovery timeout."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=2,
            recovery_timeout=1  # 1 second timeout
        )
        mock_func = Mock(side_effect=[
            ConnectionError("fail1"),
            ConnectionError("fail2"),
            "recovered"  # This will be called in half-open state
        ])
        decorated = breaker.call(mock_func)

        # Open the circuit
        for _ in range(2):
            with pytest.raises(ConnectionError):
                decorated()

        assert breaker.state == "open"

        # Wait for recovery timeout
        time.sleep(1.1)

        # Next call should transition to half-open and succeed
        result = decorated()
        assert result == "recovered"
        assert breaker.state == "half_open"

    def test_successful_half_open_closes_circuit(self):
        """Test that successful calls in half-open state close circuit."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=2,
            recovery_timeout=1,
            half_open_max_calls=2
        )
        mock_func = Mock(side_effect=[
            ConnectionError("fail1"),
            ConnectionError("fail2"),
            "success1",
            "success2"  # Second success closes circuit
        ])
        decorated = breaker.call(mock_func)

        # Open circuit
        for _ in range(2):
            with pytest.raises(ConnectionError):
                decorated()

        # Wait and test recovery
        time.sleep(1.1)

        # First success in half-open
        result1 = decorated()
        assert result1 == "success1"
        assert breaker.state == "half_open"

        # Second success closes circuit
        result2 = decorated()
        assert result2 == "success2"
        assert breaker.state == "closed"
        assert breaker.failure_count == 0

    def test_failed_half_open_reopens_circuit(self):
        """Test that failure in half-open state reopens circuit."""
        breaker = CircuitBreaker(
            name="test",
            failure_threshold=2,
            recovery_timeout=1
        )
        mock_func = Mock(side_effect=[
            ConnectionError("fail1"),
            ConnectionError("fail2"),
            ConnectionError("still failing")  # Fail in half-open
        ])
        decorated = breaker.call(mock_func)

        # Open circuit
        for _ in range(2):
            with pytest.raises(ConnectionError):
                decorated()

        # Wait and attempt recovery
        time.sleep(1.1)

        # Failure in half-open reopens circuit
        with pytest.raises(ConnectionError):
            decorated()

        assert breaker.state == "open"

    def test_circuit_resets_on_success_in_closed_state(self):
        """Test that success resets failure count in closed state."""
        breaker = CircuitBreaker(name="test", failure_threshold=3)
        mock_func = Mock(side_effect=[
            ConnectionError("fail"),
            "success",
            ConnectionError("fail again")
        ])
        decorated = breaker.call(mock_func)

        # First failure
        with pytest.raises(ConnectionError):
            decorated()
        assert breaker.failure_count == 1

        # Success resets count
        decorated()
        assert breaker.failure_count == 0

        # Failure starts counting again from 0
        with pytest.raises(ConnectionError):
            decorated()
        assert breaker.failure_count == 1
        assert breaker.state == "closed"  # Still below threshold


class TestIntegration:
    """Test retry + circuit breaker integration."""

    def test_retry_with_circuit_breaker(self):
        """Test that retry and circuit breaker work together."""
        breaker = CircuitBreaker(name="integration-test", failure_threshold=3)

        @breaker.call
        @retry_with_backoff(max_attempts=2, base_delay=0.01, exceptions=(ConnectionError,))
        def flaky_operation():
            """Simulates flaky operation."""
            return "success"

        # Should succeed
        result = flaky_operation()
        assert result == "success"
        assert breaker.state == "closed"

    def test_circuit_opens_despite_retries(self):
        """Test that circuit opens when retries exhausted multiple times."""
        breaker = CircuitBreaker(name="integration-test", failure_threshold=2)
        call_count = {"value": 0}

        @breaker.call
        @retry_with_backoff(max_attempts=2, base_delay=0.01, exceptions=(ConnectionError,))
        def always_fail():
            """Always fails even with retries."""
            call_count["value"] += 1
            raise ConnectionError("persistent failure")

        # First attempt: 2 retries, then RuntimeError
        with pytest.raises(RuntimeError):
            always_fail()
        assert breaker.failure_count == 1

        # Second attempt: 2 retries, then RuntimeError
        with pytest.raises(RuntimeError):
            always_fail()
        assert breaker.failure_count == 2

        # Circuit should now be open
        assert breaker.state == "open"

        # Next attempt fails fast (no retries)
        call_count_before = call_count["value"]
        with pytest.raises(CircuitBreakerOpenError):
            always_fail()
        assert call_count["value"] == call_count_before  # No additional calls
