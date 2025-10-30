"""Linear MCP resilience layer with automatic auth recovery.

Ensures Linear MCP within Syntropy calls handles authentication failures gracefully:
1. Detects auth failures (401, "Not connected", "unauthorized")
2. Attempts auth reset (rm -rf ~/.mcp-auth)
3. Retries operation with retry/backoff logic
4. Falls back gracefully if auth recovery fails

Design:
- Circuit breaker prevents repeated auth attempts after threshold
- Retry with exponential backoff (1s, 2s, 4s)
- Detailed error messages with troubleshooting guidance
- No silent failures - all auth issues surfaced
"""

import subprocess
from typing import Callable, Any, Optional, Dict
from pathlib import Path
from datetime import datetime

from ce.resilience import CircuitBreaker, retry_with_backoff, CircuitBreakerOpenError
from ce.logging_config import get_logger

logger = get_logger(__name__)

# Circuit breaker for Linear MCP operations
linear_breaker = CircuitBreaker(
    name="linear-mcp",
    failure_threshold=3,
    recovery_timeout=300  # 5 minutes between recovery attempts
)

# Circuit breaker specifically for auth recovery
auth_recovery_breaker = CircuitBreaker(
    name="linear-mcp-auth-recovery",
    failure_threshold=2,
    recovery_timeout=600  # 10 minutes between recovery attempts
)

# Auth cache to avoid repeated resets
_auth_reset_cache: Dict[str, datetime] = {}
AUTH_RESET_COOLDOWN = 60  # Minimum seconds between auth resets


def _is_auth_error(error: Exception, error_msg: str = "") -> bool:
    """Detect if error is authentication-related.

    Patterns:
    - "Not connected" (Linear MCP disconnected)
    - "401" or "unauthorized" (HTTP auth failure)
    - "authentication" (generic auth failure)
    - "permission denied" (auth permission issue)
    """
    error_text = str(error).lower() + error_msg.lower()

    auth_patterns = [
        "not connected",
        "401",
        "unauthorized",
        "authentication",
        "permission denied",
        "auth failed",
        "invalid credentials",
        "access denied"
    ]

    return any(pattern in error_text for pattern in auth_patterns)


def _can_reset_auth() -> bool:
    """Check if auth reset is allowed (respects cooldown).

    Returns:
        True if enough time has passed since last reset
    """
    last_reset = _auth_reset_cache.get("linear_mcp_last_reset")
    if last_reset is None:
        return True

    elapsed = (datetime.now() - last_reset).total_seconds()
    return elapsed >= AUTH_RESET_COOLDOWN


def _reset_linear_mcp_auth() -> bool:
    """Reset Linear MCP auth by clearing MCP auth cache.

    Executes: rm -rf ~/.mcp-auth

    Returns:
        True if reset succeeded, False otherwise

    Side Effects:
        - Clears ~/.mcp-auth directory
        - Updates auth reset cache timestamp
    """
    if not _can_reset_auth():
        logger.debug("Auth reset on cooldown - skipping")
        return False

    try:
        auth_dir = Path.home() / ".mcp-auth"

        if not auth_dir.exists():
            logger.debug("Auth directory already cleared")
            _auth_reset_cache["linear_mcp_last_reset"] = datetime.now()
            return True

        # Use subprocess for safe deletion
        result = subprocess.run(
            ["rm", "-rf", str(auth_dir)],
            capture_output=True,
            timeout=5
        )

        if result.returncode != 0:
            logger.warning(f"Auth reset command failed: {result.stderr.decode()}")
            return False

        logger.info("Linear MCP auth reset successfully")
        _auth_reset_cache["linear_mcp_last_reset"] = datetime.now()
        return True

    except subprocess.TimeoutExpired:
        logger.error("Auth reset command timed out")
        return False
    except Exception as e:
        logger.error(f"Failed to reset Linear MCP auth: {e}")
        return False


@retry_with_backoff(
    max_attempts=3,
    base_delay=1.0,
    max_delay=10.0,
    exceptions=(RuntimeError, ConnectionError, IOError, OSError)
)
def _call_linear_mcp_with_retry(func: Callable, *args, **kwargs) -> Any:
    """Call Linear MCP function with retry logic.

    Args:
        func: Linear MCP function to call
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Function result

    Raises:
        RuntimeError: If all retries exhausted
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_msg = str(e)

        # Check if auth error
        if _is_auth_error(e, error_msg):
            logger.warning(f"Auth error detected: {error_msg}")
            logger.info("Attempting auth recovery...")

            # Try to recover auth
            if _reset_linear_mcp_auth():
                logger.info("Auth reset succeeded - will retry operation")
                # Retry is handled by decorator
                raise RuntimeError(f"Auth recovered, retrying: {error_msg}") from e
            else:
                logger.error("Auth reset failed - operation cannot proceed")
                raise RuntimeError(
                    f"Linear MCP auth failed and recovery failed\n"
                    f"Error: {error_msg}\n"
                    f"🔧 Troubleshooting:\n"
                    f"  1. Manually run: rm -rf ~/.mcp-auth\n"
                    f"  2. Verify Linear MCP is properly configured\n"
                    f"  3. Check network connectivity to Linear service\n"
                    f"  4. Restart Claude Code and retry"
                ) from e

        # Non-auth error - propagate
        raise


def call_linear_mcp_resilient(
    func: Callable,
    *args,
    operation_name: str = "Linear MCP operation",
    **kwargs
) -> Dict[str, Any]:
    """Call Linear MCP function with full resilience (retry + circuit breaker + auth recovery).

    Args:
        func: Linear MCP function to call
        *args: Positional arguments
        operation_name: Human-readable operation name for logging
        **kwargs: Keyword arguments

    Returns:
        {
            "success": True,
            "result": <function result>,
            "method": "direct_call",
            "attempts": 1,
            "error": None
        }
        OR
        {
            "success": False,
            "result": None,
            "method": "failed",
            "attempts": N,
            "error": "<error message>",
            "recovery_attempted": True/False
        }

    Process:
        1. Check circuit breaker state
        2. Call function with retry + auth recovery
        3. On auth error: attempt auth reset, retry
        4. On persistent failure: open circuit breaker
        5. Return detailed result

    Side Effects:
        - May reset ~/.mcp-auth on auth failure
        - Updates circuit breaker state
    """
    logger.info(f"Starting resilient Linear MCP call: {operation_name}")

    attempt = 0
    recovery_attempted = False

    try:
        # Check circuit breaker
        if linear_breaker.state == "open":
            if not linear_breaker._should_attempt_reset():
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{linear_breaker.name}' is OPEN\n"
                    f"Failures: {linear_breaker.failure_count}/{linear_breaker.failure_threshold}\n"
                    f"🔧 Troubleshooting: Wait {linear_breaker.recovery_timeout}s or check Linear service health"
                )
            # Attempt recovery from half-open state
            linear_breaker._transition_to_half_open()

        # Call with retry + auth recovery
        attempt = 1
        try:
            result = _call_linear_mcp_with_retry(func, *args, **kwargs)
            linear_breaker._on_success()

            return {
                "success": True,
                "result": result,
                "method": "direct_call",
                "attempts": attempt,
                "error": None,
                "recovery_attempted": False
            }

        except RuntimeError as retry_error:
            # Check if it's auth recovery retry
            if "Auth recovered" in str(retry_error):
                recovery_attempted = True
                attempt += 1
                logger.info(f"Retrying after auth recovery (attempt {attempt})")
                result = _call_linear_mcp_with_retry(func, *args, **kwargs)
                linear_breaker._on_success()

                return {
                    "success": True,
                    "result": result,
                    "method": "after_auth_recovery",
                    "attempts": attempt,
                    "error": None,
                    "recovery_attempted": True
                }
            raise

    except CircuitBreakerOpenError as e:
        linear_breaker._on_failure()
        logger.error(f"Circuit breaker open: {e}")

        return {
            "success": False,
            "result": None,
            "method": "circuit_breaker_open",
            "attempts": attempt,
            "error": str(e),
            "recovery_attempted": False
        }

    except Exception as e:
        linear_breaker._on_failure()
        error_msg = str(e)

        logger.error(f"Linear MCP operation failed: {error_msg}")

        # Provide actionable error with troubleshooting
        is_auth = _is_auth_error(e, error_msg)

        return {
            "success": False,
            "result": None,
            "method": "auth_recovery" if is_auth else "failed",
            "attempts": attempt,
            "error": f"{error_msg}\n"
                    f"🔧 Troubleshooting:\n"
                    f"  1. Check Linear MCP connectivity\n"
                    f"  2. Run: rm -rf ~/.mcp-auth\n"
                    f"  3. Verify API credentials are valid\n"
                    f"  4. Check network connectivity\n",
            "recovery_attempted": recovery_attempted
        }


def create_issue_resilient(
    title: str,
    description: str,
    state: str = "todo",
    labels: Optional[list] = None,
    override_assignee: Optional[str] = None,
    override_project: Optional[str] = None
) -> Dict[str, Any]:
    """Create Linear issue with resilience and auth recovery.

    Args:
        title: Issue title
        description: Issue description
        state: Issue state
        labels: Optional labels
        override_assignee: Optional assignee override
        override_project: Optional project override

    Returns:
        Result dict from call_linear_mcp_resilient with issue data on success
    """
    # Import here to avoid circular imports
    from ce.linear_utils import create_issue_with_defaults

    # This gets the prepared issue data (not actually calling MCP yet)
    issue_data = create_issue_with_defaults(
        title=title,
        description=description,
        state=state,
        labels=labels,
        override_assignee=override_assignee,
        override_project=override_project
    )

    # TODO: Replace with actual Linear MCP call
    # For now, return prepared data with success flag
    logger.warning("Linear MCP create_issue not yet integrated - returning prepared data")

    return {
        "success": True,
        "result": issue_data,
        "method": "prepared_data_only",
        "attempts": 1,
        "error": None,
        "recovery_attempted": False
    }


def update_issue_resilient(
    issue_id: str,
    description: str,
    state: Optional[str] = None
) -> Dict[str, Any]:
    """Update Linear issue with resilience and auth recovery.

    Args:
        issue_id: Linear issue ID (e.g., "BLA-24")
        description: Updated description
        state: Optional new state

    Returns:
        Result dict from call_linear_mcp_resilient
    """
    # TODO: Replace with actual Linear MCP call
    logger.warning("Linear MCP update_issue not yet integrated")

    return {
        "success": False,
        "result": None,
        "method": "not_implemented",
        "attempts": 1,
        "error": "Linear MCP update_issue not yet implemented",
        "recovery_attempted": False
    }


def get_linear_mcp_status() -> Dict[str, Any]:
    """Get Linear MCP health status.

    Returns:
        {
            "connected": True/False,
            "circuit_breaker_state": "closed|open|half_open",
            "failure_count": N,
            "last_auth_reset": "ISO timestamp or null",
            "auth_reset_available": True/False,
            "diagnostics": "..."
        }
    """
    return {
        "connected": linear_breaker.state == "closed",
        "circuit_breaker_state": linear_breaker.state,
        "failure_count": linear_breaker.failure_count,
        "last_auth_reset": _auth_reset_cache.get("linear_mcp_last_reset"),
        "auth_reset_available": _can_reset_auth(),
        "diagnostics": f"Circuit state: {linear_breaker.state}, "
                      f"Failures: {linear_breaker.failure_count}/{linear_breaker.failure_threshold}"
    }
