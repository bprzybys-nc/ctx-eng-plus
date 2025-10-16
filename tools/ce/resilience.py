"""Resilience module - retry logic and circuit breaker for error recovery.

Provides decorators and utilities for handling transient failures and
preventing cascading failures in production systems.
"""

import time
import functools
from typing import Callable, Any, Type, Tuple
from datetime import datetime, timedelta


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Backoff multiplier (default: 2.0)
        exceptions: Tuple of exception types to retry (default: all)

    Returns:
        Decorator function

    Example:
        @retry_with_backoff(max_attempts=5, base_delay=2.0)
        def fetch_data():
            return api.get("/data")

    Note: Only retries on specified exceptions. Non-retryable errors propagate immediately.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    is_final_attempt = (attempt == max_attempts - 1)
                    if is_final_attempt:
                        _raise_retry_error(func, max_attempts, e)

                    # Backoff and retry
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    time.sleep(delay)

            raise RuntimeError("Retry logic error - should not reach here")

        return wrapper
    return decorator


def _raise_retry_error(func: Callable, max_attempts: int, last_error: Exception) -> None:
    """Raise detailed retry error after exhausting attempts."""
    func_name = getattr(func, '__name__', repr(func))
    raise RuntimeError(
        f"Failed after {max_attempts} attempts: {func_name}\n"
        f"Last error: {str(last_error)}\n"
        f"🔧 Troubleshooting: Check network connectivity, API rate limits"
    ) from last_error


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures.

    State machine: CLOSED → OPEN → HALF_OPEN → CLOSED
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests fail fast
    - HALF_OPEN: Testing recovery, limited requests pass through

    Example:
        breaker = CircuitBreaker(name="serena-mcp", failure_threshold=5)

        @breaker.call
        def call_serena():
            return serena.read_file("test.py")

    Attributes:
        state: Current circuit state (closed/open/half_open)
        failure_count: Consecutive failure count
        last_failure_time: Timestamp of last failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        """Initialize circuit breaker.

        Args:
            name: Circuit breaker identifier
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds to wait before half-open attempt
            half_open_max_calls: Max calls in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        # State
        self.state = "closed"  # closed, open, half_open
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None

    def call(self, func: Callable) -> Callable:
        """Decorator to protect function with circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Protected function

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Check circuit state
            if self.state == "open":
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN\n"
                        f"Failures: {self.failure_count}/{self.failure_threshold}\n"
                        f"🔧 Troubleshooting: Wait {self.recovery_timeout}s or check service health"
                    )

            # Execute function
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _transition_to_half_open(self):
        """Transition from open to half-open state."""
        self.state = "half_open"
        self.half_open_calls = 0

    def _on_success(self):
        """Handle successful call."""
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                # Recovered - close circuit
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
        else:
            # Reset failure count on success in closed state
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == "half_open":
            # Failed in half-open - reopen circuit
            self.state = "open"
            self.success_count = 0
        elif self.failure_count >= self.failure_threshold:
            # Threshold exceeded - open circuit
            self.state = "open"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
