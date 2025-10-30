"""Error Recovery and Graceful Degradation Patterns.

Pattern: Handle failures without breaking core functionality.
Use Case: External dependencies unavailable, partial success scenarios.
Benefits: Robust systems, clear user feedback, actionable troubleshooting.

Source: PRP-14 /update-context Implementation
Implementation: tools/ce/update_context.py
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


# ============================================================================
# Pattern 1: Graceful Degradation (Log + Continue)
# ============================================================================

def verify_with_external_service(functions: List[str]) -> bool:
    """Verify implementations with external service (e.g., Serena MCP).

    Graceful Degradation: If service unavailable, log warning and return False
    rather than crashing entire operation.

    Args:
        functions: List of function names to verify

    Returns:
        True if all verified, False if service unavailable or verification fails
    """
    if not functions:
        # No functions to verify - consider it success
        return True

    try:
        # Attempt to use external service
        # service = get_mcp_client()
        # results = service.find_symbols(functions)

        # For now, graceful degradation
        logger.warning(
            "External service verification not yet implemented\n"
            "🔧 Troubleshooting: Feature degrades gracefully, returns False until service ready"
        )
        return False

    except Exception as e:
        # Service unavailable - don't crash, just log
        logger.warning(f"External service unavailable: {e}")
        return False


# ============================================================================
# Pattern 2: Partial Success Handling (Track + Report)
# ============================================================================

def process_items_with_tracking(items: List[str]) -> Dict[str, Any]:
    """Process multiple items, track failures, continue on errors.

    Pattern: Don't let one failure block all work.
    Track errors for reporting while processing rest.

    Args:
        items: List of items to process

    Returns:
        {
            "success": bool,  # True only if ALL succeeded
            "processed": int,
            "failed": int,
            "errors": List[str]
        }
    """
    processed = 0
    errors = []

    for item in items:
        try:
            # Process item
            # result = process_single_item(item)
            processed += 1

        except Exception as e:
            # Track error but continue
            error_msg = f"Failed to process {item}: {e}"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

    return {
        "success": len(errors) == 0,
        "processed": processed,
        "failed": len(errors),
        "errors": errors
    }


# ============================================================================
# Pattern 3: Actionable Error Messages (Context + Guidance)
# ============================================================================

def validate_file_exists(file_path: str) -> None:
    """Validate file exists with actionable error message.

    Pattern: Exceptions include 🔧 Troubleshooting guidance for user.

    Args:
        file_path: Path to validate

    Raises:
        FileNotFoundError: With troubleshooting steps
    """
    from pathlib import Path

    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Verify path is correct\n"
            f"   - Check if file was moved or renamed\n"
            f"   - Use: ls {path.parent} to list directory"
        )


# ============================================================================
# Pattern 4: Cleanup with Logging (Best-Effort Cleanup)
# ============================================================================

def operation_with_cleanup(resource_id: str) -> Dict[str, Any]:
    """Execute operation with best-effort cleanup on failure.

    Pattern: If main operation fails, attempt cleanup but don't hide
    original error. Log cleanup failures instead of re-raising.

    Args:
        resource_id: Resource identifier

    Returns:
        Operation result

    Raises:
        RuntimeError: Original operation error (not cleanup error)
    """
    try:
        # Main operation
        # result = perform_operation(resource_id)
        return {"success": True}

    except Exception as e:
        # Main operation failed - try cleanup
        try:
            # cleanup_resource(resource_id)
            pass
        except Exception as cleanup_error:
            # Log cleanup failure but don't hide original error
            logger.warning(f"Cleanup failed for {resource_id}: {cleanup_error}")

        # Re-raise original error
        raise


# ============================================================================
# Pattern 5: Feature Flags (Gradual Rollout)
# ============================================================================

def use_new_feature_if_available(data: Dict[str, Any]) -> Dict[str, Any]:
    """Use new feature if available, fallback to stable implementation.

    Pattern: Allow partial feature rollout with graceful fallback.

    Args:
        data: Input data

    Returns:
        Processed data
    """
    USE_NEW_FEATURE = False  # Feature flag

    if USE_NEW_FEATURE:
        try:
            # New experimental feature
            # return new_implementation(data)
            return data
        except Exception as e:
            # New feature failed - fallback to stable
            logger.warning(f"New feature failed, using fallback: {e}")
            # Fall through to stable implementation

    # Stable implementation
    return data


# ============================================================================
# Key Insights
# ============================================================================

# 1. Graceful Degradation: Log + continue, don't crash entire operation
# 2. Partial Success: Track failures, report details, continue processing
# 3. Actionable Errors: Include 🔧 Troubleshooting guidance in exceptions
# 4. Best-Effort Cleanup: Log cleanup failures, don't hide original error
# 5. Feature Flags: Enable gradual rollout with safe fallbacks
#
# ANTI-PATTERN: Silent failures, bare except, swallowing errors
# CORRECT PATTERN: Explicit logging, specific exceptions, actionable guidance
