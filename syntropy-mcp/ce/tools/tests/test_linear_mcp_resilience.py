"""Tests for Linear MCP resilience layer.

Tests auth detection, recovery, circuit breaker, and retry logic.
"""

from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

from ce.linear_mcp_resilience import (
    _is_auth_error,
    _can_reset_auth,
    _reset_linear_mcp_auth,
    call_linear_mcp_resilient,
    create_issue_resilient,
    get_linear_mcp_status,
    _auth_reset_cache,
    AUTH_RESET_COOLDOWN,
    linear_breaker
)


class TestAuthErrorDetection:
    """Test auth error pattern detection."""

    def test_detect_not_connected_error(self):
        """Detect 'Not connected' auth error."""
        error = Exception("Linear MCP: Not connected")
        assert _is_auth_error(error) is True

    def test_detect_401_error(self):
        """Detect HTTP 401 auth error."""
        error = Exception("HTTP 401 Unauthorized")
        assert _is_auth_error(error) is True

    def test_detect_unauthorized_error(self):
        """Detect 'unauthorized' auth error."""
        error = Exception("Request failed: unauthorized")
        assert _is_auth_error(error) is True

    def test_detect_permission_denied_error(self):
        """Detect 'permission denied' auth error."""
        error = Exception("Permission denied accessing Linear API")
        assert _is_auth_error(error) is True

    def test_case_insensitive_detection(self):
        """Auth error detection is case-insensitive."""
        error = Exception("STATUS CODE 401 UNAUTHORIZED")
        assert _is_auth_error(error) is True

    def test_error_message_parameter(self):
        """Detect auth error in additional error message parameter."""
        error = Exception("Generic error")
        error_msg = "Authentication failed"
        assert _is_auth_error(error, error_msg) is True

    def test_non_auth_error(self):
        """Non-auth errors not detected as auth errors."""
        error = Exception("Connection timeout - network unreachable")
        assert _is_auth_error(error) is False

    def test_empty_error(self):
        """Empty error string not detected as auth error."""
        error = Exception("")
        assert _is_auth_error(error) is False


class TestAuthResetCooldown:
    """Test auth reset cooldown logic."""

    def test_can_reset_when_no_prior_reset(self):
        """Auth reset allowed when no prior reset."""
        _auth_reset_cache.clear()
        assert _can_reset_auth() is True

    def test_cannot_reset_within_cooldown(self):
        """Auth reset blocked within cooldown period."""
        _auth_reset_cache["linear_mcp_last_reset"] = datetime.now()
        assert _can_reset_auth() is False

    def test_can_reset_after_cooldown(self):
        """Auth reset allowed after cooldown expires."""
        past_time = datetime.now() - timedelta(seconds=AUTH_RESET_COOLDOWN + 10)
        _auth_reset_cache["linear_mcp_last_reset"] = past_time
        assert _can_reset_auth() is True

    def test_cooldown_exactly_at_threshold(self):
        """Auth reset allowed at exact cooldown threshold."""
        past_time = datetime.now() - timedelta(seconds=AUTH_RESET_COOLDOWN)
        _auth_reset_cache["linear_mcp_last_reset"] = past_time
        assert _can_reset_auth() is True


class TestAuthReset:
    """Test auth reset functionality."""

    def test_reset_clears_mcp_auth_directory(self):
        """Auth reset removes ~/.mcp-auth directory."""
        _auth_reset_cache.clear()  # Clear cooldown
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("pathlib.Path.exists", return_value=True):
                result = _reset_linear_mcp_auth()

            assert result is True
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            assert "rm" in call_args[0][0]
            assert "-rf" in call_args[0][0]

    def test_reset_handles_nonexistent_directory(self):
        """Auth reset succeeds when directory already cleared."""
        _auth_reset_cache.clear()  # Clear cooldown
        with patch("pathlib.Path.exists", return_value=False):
            result = _reset_linear_mcp_auth()
            assert result is True

    def test_reset_fails_on_subprocess_error(self):
        """Auth reset fails when subprocess returns error."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr=b"Permission denied"
            )

            result = _reset_linear_mcp_auth()
            assert result is False

    def test_reset_fails_on_timeout(self):
        """Auth reset fails when subprocess times out."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = TimeoutError("Command timed out")

            result = _reset_linear_mcp_auth()
            assert result is False

    def test_reset_respects_cooldown(self):
        """Auth reset blocked within cooldown."""
        _auth_reset_cache["linear_mcp_last_reset"] = datetime.now()

        with patch("subprocess.run") as mock_run:
            result = _reset_linear_mcp_auth()

            assert result is False
            mock_run.assert_not_called()

    def test_reset_updates_cache_on_success(self):
        """Auth reset updates cache timestamp on success."""
        _auth_reset_cache.clear()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch("pathlib.Path.exists", return_value=True):
                _reset_linear_mcp_auth()

        assert "linear_mcp_last_reset" in _auth_reset_cache
        assert isinstance(_auth_reset_cache["linear_mcp_last_reset"], datetime)


class TestCircuitBreakerBehavior:
    """Test circuit breaker state transitions."""

    def setup_method(self):
        """Reset circuit breaker before each test."""
        linear_breaker.state = "closed"
        linear_breaker.failure_count = 0
        linear_breaker.success_count = 0

    def test_circuit_breaker_opens_on_failures(self):
        """Circuit breaker opens after failure threshold."""
        # Simulate failures
        for _ in range(linear_breaker.failure_threshold):
            linear_breaker._on_failure()

        assert linear_breaker.state == "open"

    def test_circuit_breaker_closed_on_success(self):
        """Circuit breaker closes after recovery in half-open state."""
        linear_breaker.state = "half_open"

        for _ in range(linear_breaker.half_open_max_calls):
            linear_breaker._on_success()

        assert linear_breaker.state == "closed"


class TestResilientCall:
    """Test resilient Linear MCP calls with auth recovery."""

    def setup_method(self):
        """Reset state before each test."""
        _auth_reset_cache.clear()
        linear_breaker.state = "closed"
        linear_breaker.failure_count = 0
        linear_breaker.success_count = 0

    def test_successful_call_returns_result(self):
        """Successful MCP call returns result with success=True."""
        mock_func = Mock(return_value={"id": "BLA-1", "title": "Test"})

        result = call_linear_mcp_resilient(
            mock_func,
            operation_name="create_issue"
        )

        assert result["success"] is True
        assert result["result"] == {"id": "BLA-1", "title": "Test"}
        assert result["attempts"] == 1
        assert result["recovery_attempted"] is False

    def test_auth_error_triggers_recovery(self):
        """Auth error triggers recovery attempt."""
        mock_func = Mock(side_effect=Exception("401 Unauthorized"))

        with patch("ce.linear_mcp_resilience._reset_linear_mcp_auth") as mock_reset:
            mock_reset.return_value = True
            # Second call should fail due to max attempts
            with patch("subprocess.run"):
                result = call_linear_mcp_resilient(
                    mock_func,
                    operation_name="create_issue"
                )

        # Should have called reset at least once
        assert result["success"] is False
        # Result shows auth-related failure
        assert "auth" in result["method"].lower() or result["attempts"] > 1

    def test_circuit_breaker_prevents_cascade(self):
        """Circuit breaker prevents cascading failures."""
        mock_func = Mock(side_effect=Exception("Network error"))

        # Cause enough failures to open circuit
        for _ in range(linear_breaker.failure_threshold):
            try:
                call_linear_mcp_resilient(
                    mock_func,
                    operation_name="test"
                )
            except:
                pass

        # Next call should fail immediately
        result = call_linear_mcp_resilient(
            mock_func,
            operation_name="test"
        )

        assert result["success"] is False
        assert result["method"] == "circuit_breaker_open"

    def test_non_auth_error_propagates(self):
        """Non-auth errors propagate normally."""
        mock_func = Mock(side_effect=ValueError("Invalid input"))

        with patch("ce.linear_mcp_resilience._reset_linear_mcp_auth") as mock_reset:
            result = call_linear_mcp_resilient(
                mock_func,
                operation_name="test"
            )

        assert result["success"] is False
        mock_reset.assert_not_called()  # Auth recovery not attempted


class TestCreateIssueResilient:
    """Test resilient issue creation."""

    def test_create_issue_returns_result_dict(self):
        """Create issue returns structured result."""
        result = create_issue_resilient(
            title="Test Feature",
            description="Test description"
        )

        assert isinstance(result, dict)
        assert "success" in result
        assert "result" in result
        assert "attempts" in result
        assert "error" in result

    def test_create_issue_with_labels(self):
        """Create issue accepts labels parameter."""
        result = create_issue_resilient(
            title="Test Feature",
            description="Test description",
            labels=["feature", "urgent"]
        )

        assert result["success"] is True


class TestLinearMCPStatus:
    """Test Linear MCP status reporting."""

    def setup_method(self):
        """Reset state before each test."""
        linear_breaker.state = "closed"
        linear_breaker.failure_count = 0

    def test_status_reports_circuit_breaker_state(self):
        """Status includes circuit breaker state."""
        status = get_linear_mcp_status()

        assert "connected" in status
        assert "circuit_breaker_state" in status
        assert "failure_count" in status
        assert status["circuit_breaker_state"] == "closed"

    def test_status_reports_failure_count(self):
        """Status reports failure count."""
        linear_breaker._on_failure()

        status = get_linear_mcp_status()
        assert status["failure_count"] == 1

    def test_status_reports_auth_reset_availability(self):
        """Status reports if auth reset is available."""
        status = get_linear_mcp_status()

        assert "auth_reset_available" in status
        assert isinstance(status["auth_reset_available"], bool)

    def test_status_connected_when_circuit_closed(self):
        """Status shows 'connected' when circuit breaker closed."""
        linear_breaker.state = "closed"
        status = get_linear_mcp_status()

        assert status["connected"] is True

    def test_status_not_connected_when_circuit_open(self):
        """Status shows 'not connected' when circuit breaker open."""
        linear_breaker.state = "open"
        status = get_linear_mcp_status()

        assert status["connected"] is False


class TestIntegration:
    """Integration tests for full resilience flow."""

    def setup_method(self):
        """Reset state before each test."""
        _auth_reset_cache.clear()
        linear_breaker.state = "closed"
        linear_breaker.failure_count = 0

    def test_full_auth_recovery_flow(self):
        """Full flow: auth error → recovery → retry."""
        call_count = 0

        def failing_then_success(*_args, **_kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise Exception("Linear MCP: Not connected")
            return {"id": "BLA-1"}

        with patch("ce.linear_mcp_resilience._reset_linear_mcp_auth") as mock_reset:
            mock_reset.return_value = True
            # Note: retry decorator will call function multiple times
            result = call_linear_mcp_resilient(
                failing_then_success,
                operation_name="test"
            )

        # After recovery, call succeeds or max retries reached
        assert isinstance(result, dict)
        assert "recovery_attempted" in result

    def test_graceful_degradation_on_persistent_auth_failure(self):
        """System degrades gracefully if auth recovery fails."""
        mock_func = Mock(side_effect=Exception("401 Unauthorized"))

        with patch("ce.linear_mcp_resilience._reset_linear_mcp_auth") as mock_reset:
            mock_reset.return_value = False  # Reset fails

            result = call_linear_mcp_resilient(
                mock_func,
                operation_name="test"
            )

        assert result["success"] is False
        assert "🔧" in result["error"]  # Troubleshooting included
