"""PRP YAML validation and state management module."""
from typing import Dict, Any, List, Optional
import yaml
import re
import json
import logging
from pathlib import Path
from datetime import datetime, timezone

# Required fields schema
REQUIRED_FIELDS = [
    "name", "description", "prp_id", "status", "priority",
    "confidence", "effort_hours", "risk", "dependencies",
    "parent_prp", "context_memories", "meeting_evidence",
    "context_sync", "version", "created_date", "last_updated"
]

# Valid enum values
VALID_STATUS = ["ready", "in_progress", "executed", "validated", "archived"]
VALID_PRIORITY = ["HIGH", "MEDIUM", "LOW"]
VALID_RISK = ["LOW", "MEDIUM", "HIGH"]
VALID_PHASES = ["planning", "implementation", "testing", "validation", "complete"]

# State file paths
STATE_DIR = Path(".ce")
STATE_FILE = STATE_DIR / "active_prp_session"

# Configure logging
logger = logging.getLogger(__name__)


def validate_prp_yaml(file_path: str) -> Dict[str, Any]:
    """Validate PRP YAML header against schema.

    Args:
        file_path: Path to PRP markdown file

    Returns:
        Dict with: success (bool), errors (list), warnings (list), header (dict)

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parse fails
    """
    errors = []
    warnings = []

    # Check file exists
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(
            f"PRP file not found: {file_path}\n"
            f"🔧 Troubleshooting: Verify file path is correct"
        )

    # Read file
    content = path.read_text()

    # Check YAML delimiters
    if not content.startswith("---\n"):
        errors.append("Missing YAML front matter: file must start with '---'")
        return {"success": False, "errors": errors, "warnings": warnings, "header": None}

    # Extract YAML header
    parts = content.split("---", 2)
    if len(parts) < 3:
        errors.append("Missing closing '---' delimiter for YAML header")
        return {"success": False, "errors": errors, "warnings": warnings, "header": None}

    yaml_content = parts[1].strip()

    # Parse YAML
    try:
        header = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        errors.append(f"YAML parse error: {str(e)}")
        return {"success": False, "errors": errors, "warnings": warnings, "header": None}

    # Validate schema
    return validate_schema(header, errors, warnings)


def validate_schema(header: Dict[str, Any], errors: List[str], warnings: List[str]) -> Dict[str, Any]:
    """Validate YAML header against schema."""

    # Check required fields
    missing_fields = [f for f in REQUIRED_FIELDS if f not in header]
    if missing_fields:
        errors.append(f"Missing required fields: {', '.join(missing_fields)}")

    # Validate PRP ID format
    if "prp_id" in header:
        error = validate_prp_id_format(header["prp_id"])
        if error:
            errors.append(error)

    # Validate date formats
    for date_field in ["created_date", "last_updated"]:
        if date_field in header:
            error = validate_date_format(header[date_field], date_field)
            if error:
                errors.append(error)

    # Validate status enum
    if "status" in header and header["status"] not in VALID_STATUS:
        errors.append(
            f"Invalid status: '{header['status']}' (must be one of: {', '.join(VALID_STATUS)})"
        )

    # Validate priority enum
    if "priority" in header and header["priority"] not in VALID_PRIORITY:
        errors.append(
            f"Invalid priority: '{header['priority']}' (must be one of: {', '.join(VALID_PRIORITY)})"
        )

    # Validate risk enum
    if "risk" in header and header["risk"] not in VALID_RISK:
        errors.append(
            f"Invalid risk: '{header['risk']}' (must be one of: {', '.join(VALID_RISK)})"
        )

    # Validate confidence format (X/10)
    if "confidence" in header:
        conf_str = str(header["confidence"])
        if not re.match(r'^\d{1,2}/10$', conf_str):
            errors.append(f"Invalid confidence format: '{conf_str}' (expected: X/10 where X is 1-10)")

    # Validate effort_hours is numeric
    if "effort_hours" in header:
        try:
            float(header["effort_hours"])
        except (ValueError, TypeError):
            errors.append(f"Invalid effort_hours: '{header['effort_hours']}' (must be numeric)")

    # Validate dependencies is list
    if "dependencies" in header and not isinstance(header["dependencies"], list):
        errors.append(f"Invalid dependencies: must be a list, got {type(header['dependencies']).__name__}")

    # Validate context_memories is list
    if "context_memories" in header and not isinstance(header["context_memories"], list):
        errors.append(f"Invalid context_memories: must be a list, got {type(header['context_memories']).__name__}")

    # Warnings for optional fields
    if not header.get("task_id"):
        warnings.append("Optional field 'task_id' is empty (consider linking to issue tracker)")

    success = len(errors) == 0
    return {
        "success": success,
        "errors": errors,
        "warnings": warnings,
        "header": header
    }


def validate_prp_id_format(prp_id: str) -> Optional[str]:
    """Validate PRP ID format (PRP-X.Y or PRP-X.Y.Z).

    Returns:
        Error message if invalid, None if valid
    """
    # Pattern: PRP-X.Y or PRP-X.Y.Z (no leading zeros)
    pattern = r'^PRP-([1-9]\d*)(\.(0|[1-9]\d*))?(\.(0|[1-9]\d*))?$'
    if not re.match(pattern, prp_id):
        return f"Invalid PRP ID format: '{prp_id}' (expected: PRP-X.Y or PRP-X.Y.Z, no leading zeros)"
    return None


def validate_date_format(date_str: str, field_name: str) -> Optional[str]:
    """Validate ISO 8601 date format.

    Returns:
        Error message if invalid, None if valid
    """
    pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
    if not re.match(pattern, date_str):
        return f"Invalid date format for '{field_name}': '{date_str}' (expected: YYYY-MM-DDTHH:MM:SSZ)"
    return None


def format_validation_result(result: Dict[str, Any]) -> str:
    """Format validation result for human-readable output."""
    if result["success"]:
        output = "✅ YAML validation passed\n\n"
        output += f"PRP ID: {result['header']['prp_id']}\n"
        output += f"Name: {result['header']['name']}\n"
        output += f"Status: {result['header']['status']}\n"
        output += f"Effort: {result['header']['effort_hours']}h\n"

        if result["warnings"]:
            output += "\n⚠️  Warnings:\n"
            for warning in result["warnings"]:
                output += f"  - {warning}\n"
    else:
        output = "❌ YAML validation failed\n\n"
        output += "Errors:\n"
        for error in result["errors"]:
            output += f"  ❌ {error}\n"

        if result["warnings"]:
            output += "\nWarnings:\n"
            for warning in result["warnings"]:
                output += f"  ⚠️  {warning}\n"

        output += "\n🔧 Troubleshooting: Review docs/prp-yaml-schema.md for schema reference"

    return output


# ============================================================================
# PRP State Management Functions
# ============================================================================

def _write_state(state: Dict[str, Any]) -> None:
    """Write state to file using atomic write pattern."""
    STATE_DIR.mkdir(exist_ok=True)
    temp_file = STATE_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(STATE_FILE)


def start_prp(prp_id: str, prp_name: Optional[str] = None) -> Dict[str, Any]:
    """Initialize PRP execution context.

    Creates .ce/active_prp_session file and initializes state tracking.

    Args:
        prp_id: PRP identifier (e.g., "PRP-003")
        prp_name: Optional PRP name for display

    Returns:
        {
            "success": True,
            "prp_id": "PRP-003",
            "started_at": "2025-10-12T14:30:00Z",
            "message": "PRP-003 context initialized"
        }

    Raises:
        RuntimeError: If another PRP is active (call cleanup first)
        ValueError: If prp_id format invalid
    """
    # Validate PRP ID format
    error = validate_prp_id_format(prp_id)
    if error:
        raise ValueError(
            f"{error}\n"
            f"🔧 Troubleshooting: Use format PRP-X or PRP-X.Y"
        )

    # Check if another PRP is active
    active = get_active_prp()
    if active:
        raise RuntimeError(
            f"Another PRP is active: {active['prp_id']}\n"
            f"🔧 Troubleshooting: Run 'ce prp cleanup {active['prp_id']}' or 'ce prp end {active['prp_id']}' first"
        )

    # Initialize state
    started_at = datetime.now(timezone.utc).isoformat()
    state = {
        "prp_id": prp_id,
        "prp_name": prp_name or prp_id,
        "started_at": started_at,
        "phase": "planning",
        "last_checkpoint": None,
        "checkpoint_count": 0,
        "validation_attempts": {
            "L1": 0,
            "L2": 0,
            "L3": 0,
            "L4": 0
        },
        "serena_memories": []
    }

    _write_state(state)
    logger.info(f"Started {prp_id} execution context")

    return {
        "success": True,
        "prp_id": prp_id,
        "started_at": started_at,
        "message": f"{prp_id} context initialized"
    }


def get_active_prp() -> Optional[Dict[str, Any]]:
    """Get current active PRP session.

    Returns:
        State dict if PRP active, None if no active session

    Example:
        >>> state = get_active_prp()
        >>> if state:
        ...     print(f"Active: {state['prp_id']}")
        ... else:
        ...     print("No active PRP")
    """
    if not STATE_FILE.exists():
        return None

    try:
        return json.loads(STATE_FILE.read_text())
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to read state file: {e}")
        return None


def end_prp(prp_id: str) -> Dict[str, Any]:
    """End PRP execution context (without cleanup).

    Removes .ce/active_prp_session file. Use cleanup_prp() for full cleanup.

    Args:
        prp_id: PRP identifier to end

    Returns:
        {
            "success": True,
            "duration": "2h 15m",
            "checkpoints_created": 3
        }

    Raises:
        RuntimeError: If prp_id doesn't match active PRP
    """
    active = get_active_prp()
    if not active:
        raise RuntimeError(
            f"No active PRP session\n"
            f"🔧 Troubleshooting: Use 'ce prp status' to check current state"
        )

    if active["prp_id"] != prp_id:
        raise RuntimeError(
            f"PRP ID mismatch: active={active['prp_id']}, requested={prp_id}\n"
            f"🔧 Troubleshooting: End the active PRP first: 'ce prp end {active['prp_id']}'"
        )

    # Calculate duration
    started = datetime.fromisoformat(active["started_at"])
    ended = datetime.now(timezone.utc)
    duration_seconds = (ended - started).total_seconds()
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    duration = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"

    # Remove state file
    STATE_FILE.unlink(missing_ok=True)
    logger.info(f"Ended {prp_id} execution context")

    return {
        "success": True,
        "duration": duration,
        "checkpoints_created": active["checkpoint_count"]
    }


def update_prp_phase(phase: str) -> Dict[str, Any]:
    """Update current PRP phase in state file.

    Args:
        phase: Phase name (e.g., "implementation", "testing", "validation")
               Valid phases: planning, implementation, testing, validation, complete

    Returns:
        Updated state dict

    Raises:
        RuntimeError: If no active PRP session
        ValueError: If phase not in valid phases list
    """
    if phase not in VALID_PHASES:
        raise ValueError(
            f"Invalid phase: '{phase}' (must be one of: {', '.join(VALID_PHASES)})\n"
            f"🔧 Troubleshooting: Use a valid phase name"
        )

    active = get_active_prp()
    if not active:
        raise RuntimeError(
            f"No active PRP session\n"
            f"🔧 Troubleshooting: Start a PRP first with 'ce prp start PRP-XXX'"
        )

    active["phase"] = phase
    _write_state(active)
    logger.info(f"Updated {active['prp_id']} phase to: {phase}")

    return active
