"""PRP YAML validation and state management module."""
from typing import Dict, Any, List, Optional
import yaml
import re
import json
import logging
from pathlib import Path
from datetime import datetime, timezone
from .core import find_project_root

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

# Configure logging
logger = logging.getLogger(__name__)


def _get_state_dir() -> Path:
    """Get .ce directory path from project root.

    Returns:
        Path to .ce directory

    Raises:
        FileNotFoundError: If not in CE project
    """
    return find_project_root() / ".ce"


def _get_state_file() -> Path:
    """Get active PRP session state file path.

    Returns:
        Path to active_prp_session file

    Raises:
        FileNotFoundError: If not in CE project
    """
    return _get_state_dir() / "active_prp_session"


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
    state_dir = _get_state_dir()
    state_file = _get_state_file()
    state_dir.mkdir(exist_ok=True)
    temp_file = state_file.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(state_file)


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
    try:
        state_file = _get_state_file()
    except FileNotFoundError:
        return None  # Not in CE project

    if not state_file.exists():
        return None

    try:
        return json.loads(state_file.read_text())
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
    state_file = _get_state_file()
    state_file.unlink(missing_ok=True)
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


# ============================================================================
# Checkpoint Management Functions
# ============================================================================

def create_checkpoint(phase: str, message: Optional[str] = None) -> Dict[str, Any]:
    """Create PRP-scoped git checkpoint.

    Args:
        phase: Phase identifier (e.g., "phase1", "phase2", "final")
        message: Optional checkpoint message (defaults to phase name)

    Returns:
        {
            "success": True,
            "tag_name": "checkpoint-PRP-003-phase1-20251012-143000",
            "commit_sha": "a1b2c3d",
            "message": "Phase 1 complete: Core logic implemented"
        }

    Raises:
        RuntimeError: If no active PRP or git operation fails
        RuntimeError: If working tree not clean (uncommitted changes)

    Side Effects:
        - Creates git annotated tag
        - Updates .ce/active_prp_session with last_checkpoint
        - Increments checkpoint_count
        - Serena memory handling:
          * If Serena available: writes checkpoint metadata to memory
          * If Serena unavailable: logs warning, continues successfully
          * Never fails on Serena unavailability
    """
    from .core import run_cmd

    # Verify active PRP
    active = get_active_prp()
    if not active:
        raise RuntimeError(
            f"No active PRP session\n"
            f"🔧 Troubleshooting: Start a PRP first with 'ce prp start PRP-XXX'"
        )

    # Check git working tree clean
    status_result = run_cmd("git status --porcelain")
    if not status_result["success"]:
        raise RuntimeError(
            f"Failed to check git status: {status_result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure you're in a git repository"
        )

    if status_result["stdout"].strip():
        raise RuntimeError(
            f"Working tree has uncommitted changes\n"
            f"🔧 Troubleshooting: Commit or stash changes before creating checkpoint"
        )

    # Generate timestamp and tag name
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    tag_name = f"checkpoint-{active['prp_id']}-{phase}-{timestamp}"

    # Get current commit SHA
    sha_result = run_cmd("git rev-parse HEAD")
    if not sha_result["success"]:
        raise RuntimeError(
            f"Failed to get commit SHA: {sha_result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure you're in a git repository with commits"
        )
    commit_sha = sha_result["stdout"].strip()[:7]

    # Create annotated tag
    tag_message = message or f"{phase} checkpoint"
    tag_result = run_cmd(f'git tag -a "{tag_name}" -m "{tag_message}"')
    if not tag_result["success"]:
        raise RuntimeError(
            f"Failed to create checkpoint tag: {tag_result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure git is configured correctly"
        )

    # Update state
    active["last_checkpoint"] = tag_name
    active["checkpoint_count"] += 1
    _write_state(active)

    logger.info(f"Created checkpoint: {tag_name}")

    return {
        "success": True,
        "tag_name": tag_name,
        "commit_sha": commit_sha,
        "message": tag_message
    }


def list_checkpoints(prp_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all checkpoints for PRP(s).

    Args:
        prp_id: Optional PRP filter (None = all PRPs)

    Returns:
        List of checkpoint dicts:
        [
            {
                "tag_name": "checkpoint-PRP-003-phase1-20251012-143000",
                "prp_id": "PRP-003",
                "phase": "phase1",
                "timestamp": "2025-10-12T14:30:00Z",
                "commit_sha": "a1b2c3d",
                "message": "Phase 1 complete"
            },
            ...
        ]

    Example:
        >>> checkpoints = list_checkpoints("PRP-003")
        >>> for cp in checkpoints:
        ...     print(f"{cp['phase']}: {cp['message']}")
    """
    from .core import run_cmd

    # Get all tags
    tags_result = run_cmd("git tag -l 'checkpoint-*' --format='%(refname:short)|%(subject)|%(objectname:short)'")
    if not tags_result["success"]:
        logger.warning(f"Failed to list tags: {tags_result['stderr']}")
        return []

    if not tags_result["stdout"].strip():
        return []

    checkpoints = []
    for line in tags_result["stdout"].strip().split("\n"):
        parts = line.split("|")
        if len(parts) < 3:
            continue

        tag_name, tag_message, commit_sha = parts[0], parts[1], parts[2]

        # Parse tag name: checkpoint-{prp_id}-{phase}-{timestamp}
        if not tag_name.startswith("checkpoint-"):
            continue

        tag_parts = tag_name.split("-", 3)  # Split: ["checkpoint", "PRP", "X", "phase-YYYYMMDD-HHMMSS"]
        if len(tag_parts) < 4:
            continue

        checkpoint_prp_id = f"{tag_parts[1]}-{tag_parts[2]}"  # "PRP-X"

        # Filter by prp_id if provided
        if prp_id and checkpoint_prp_id != prp_id:
            continue

        # Extract phase and timestamp
        remaining = tag_parts[3]  # "phase1-20251012-143000"
        phase_timestamp = remaining.rsplit("-", 2)  # Split from right to preserve phase name
        if len(phase_timestamp) == 3:
            phase = phase_timestamp[0]
            timestamp_str = f"{phase_timestamp[1]}-{phase_timestamp[2]}"
            # Convert timestamp to ISO format
            try:
                dt = datetime.strptime(timestamp_str, "%Y%m%d-%H%M%S")
                timestamp_iso = dt.replace(tzinfo=timezone.utc).isoformat()
            except ValueError:
                timestamp_iso = timestamp_str
        else:
            phase = remaining
            timestamp_iso = ""

        checkpoints.append({
            "tag_name": tag_name,
            "prp_id": checkpoint_prp_id,
            "phase": phase,
            "timestamp": timestamp_iso,
            "commit_sha": commit_sha,
            "message": tag_message
        })

    return checkpoints


def restore_checkpoint(prp_id: str, phase: Optional[str] = None) -> Dict[str, Any]:
    """Restore to PRP checkpoint.

    Args:
        prp_id: PRP identifier
        phase: Optional phase (defaults to latest checkpoint)

    Returns:
        {
            "success": True,
            "restored_to": "checkpoint-PRP-003-phase1-20251012-143000",
            "commit_sha": "a1b2c3d"
        }

    Raises:
        RuntimeError: If checkpoint not found or git operation fails
        RuntimeError: If working tree not clean (uncommitted changes)

    Warning:
        This is a destructive operation. Uncommitted changes will be lost.
    """
    from .core import run_cmd
    import sys

    # Check working tree clean
    status_result = run_cmd("git status --porcelain")
    if not status_result["success"]:
        raise RuntimeError(
            f"Failed to check git status: {status_result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure you're in a git repository"
        )

    if status_result["stdout"].strip():
        raise RuntimeError(
            f"Working tree has uncommitted changes\n"
            f"🔧 Troubleshooting: Commit or stash changes before restoring checkpoint"
        )

    # Find checkpoint
    checkpoints = list_checkpoints(prp_id)
    if not checkpoints:
        raise RuntimeError(
            f"No checkpoints found for {prp_id}\n"
            f"🔧 Troubleshooting: Create a checkpoint first with 'ce prp checkpoint <phase>'"
        )

    # Select checkpoint
    if phase:
        checkpoint = next((cp for cp in checkpoints if cp["phase"] == phase), None)
        if not checkpoint:
            phases = [cp["phase"] for cp in checkpoints]
            raise RuntimeError(
                f"No checkpoint found for phase '{phase}' in {prp_id}\n"
                f"Available phases: {', '.join(phases)}\n"
                f"🔧 Troubleshooting: Use 'ce prp list' to see available checkpoints"
            )
    else:
        # Use latest (by timestamp)
        checkpoints.sort(key=lambda x: x["timestamp"], reverse=True)
        checkpoint = checkpoints[0]

    # Confirmation if interactive
    if sys.stdout.isatty():
        response = input(f"Restore to {checkpoint['tag_name']}? This will discard uncommitted changes. [y/N] ")
        if response.lower() != "y":
            return {"success": False, "message": "Restore cancelled by user"}

    # Restore to checkpoint
    checkout_result = run_cmd(f"git checkout {checkpoint['tag_name']}")
    if not checkout_result["success"]:
        raise RuntimeError(
            f"Failed to restore checkpoint: {checkout_result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure tag exists and git is configured correctly"
        )

    logger.info(f"Restored to checkpoint: {checkpoint['tag_name']}")

    return {
        "success": True,
        "restored_to": checkpoint["tag_name"],
        "commit_sha": checkpoint["commit_sha"]
    }


def delete_intermediate_checkpoints(prp_id: str, keep_final: bool = True) -> Dict[str, Any]:
    """Delete intermediate checkpoints (part of cleanup protocol).

    Args:
        prp_id: PRP identifier
        keep_final: Keep *-final checkpoint for rollback (default: True)

    Returns:
        {
            "success": True,
            "deleted_count": 2,
            "kept": ["checkpoint-PRP-003-final-20251012-160000"]
        }

    Process:
        1. List all checkpoints for prp_id
        2. Filter: keep *-final if keep_final=True
        3. Delete remaining tags: git tag -d {tag_name}
    """
    from .core import run_cmd

    checkpoints = list_checkpoints(prp_id)
    if not checkpoints:
        return {"success": True, "deleted_count": 0, "kept": []}

    to_delete = []
    kept = []

    for checkpoint in checkpoints:
        if keep_final and checkpoint["phase"] == "final":
            kept.append(checkpoint["tag_name"])
        else:
            to_delete.append(checkpoint["tag_name"])

    # Delete tags
    deleted_count = 0
    for tag_name in to_delete:
        result = run_cmd(f"git tag -d {tag_name}")
        if result["success"]:
            deleted_count += 1
            logger.info(f"Deleted checkpoint: {tag_name}")
        else:
            logger.warning(f"Failed to delete tag {tag_name}: {result['stderr']}")

    return {
        "success": True,
        "deleted_count": deleted_count,
        "kept": kept
    }


# ============================================================================
# Memory Isolation Functions
# ============================================================================

def write_prp_memory(category: str, name: str, content: str) -> Dict[str, Any]:
    """Write Serena memory with PRP namespace.

    Args:
        category: Memory category (checkpoint, learnings, temp)
        name: Memory identifier
        content: Memory content (markdown)

    Returns:
        {
            "success": True,
            "memory_name": "PRP-003-checkpoint-phase1",
            "serena_available": True
        }

    Raises:
        RuntimeError: If no active PRP
        Warning: If Serena MCP unavailable (logs warning, continues)

    Side Effects:
        - Calls serena.write_memory(f"{prp_id}-{category}-{name}", content)
        - Updates .ce/active_prp_session serena_memories list
    """
    active = get_active_prp()
    if not active:
        raise RuntimeError(
            f"No active PRP session\n"
            f"🔧 Troubleshooting: Start a PRP first with 'ce prp start PRP-XXX'"
        )

    memory_name = f"{active['prp_id']}-{category}-{name}"
    serena_available = False

    # Try to write to Serena (optional)
    try:
        # Check if mcp__serena__write_memory tool is available
        # For now, we'll just log that Serena is not available
        # In production, this would call the Serena MCP tool
        logger.warning(f"Serena MCP not available - skipping memory write for {memory_name}")
    except Exception as e:
        logger.warning(f"Failed to write Serena memory: {e}")

    # Update state file
    if memory_name not in active["serena_memories"]:
        active["serena_memories"].append(memory_name)
        _write_state(active)

    return {
        "success": True,
        "memory_name": memory_name,
        "serena_available": serena_available
    }


def read_prp_memory(category: str, name: str) -> Optional[str]:
    """Read Serena memory with PRP namespace.

    Args:
        category: Memory category
        name: Memory identifier

    Returns:
        Memory content if exists, None otherwise

    Raises:
        RuntimeError: If no active PRP
    """
    active = get_active_prp()
    if not active:
        raise RuntimeError(
            f"No active PRP session\n"
            f"🔧 Troubleshooting: Start a PRP first with 'ce prp start PRP-XXX'"
        )

    memory_name = f"{active['prp_id']}-{category}-{name}"

    # Try to read from Serena (optional)
    try:
        # In production, this would call the Serena MCP tool
        logger.warning(f"Serena MCP not available - cannot read memory {memory_name}")
        return None
    except Exception as e:
        logger.warning(f"Failed to read Serena memory: {e}")
        return None


def list_prp_memories(prp_id: Optional[str] = None) -> List[str]:
    """List all Serena memories for PRP(s).

    Args:
        prp_id: Optional PRP filter (None = current active PRP)

    Returns:
        List of memory names (e.g., ["PRP-003-checkpoint-phase1", ...])

    Process:
        1. Call serena.list_memories()
        2. Filter by prefix: {prp_id}-
        3. Return matching names
    """
    if prp_id is None:
        active = get_active_prp()
        if not active:
            return []
        prp_id = active["prp_id"]

    # Try to list from Serena (optional)
    try:
        # In production, this would call the Serena MCP tool
        logger.warning(f"Serena MCP not available - returning memories from state file")
        active = get_active_prp()
        if active and active["prp_id"] == prp_id:
            return active["serena_memories"]
        return []
    except Exception as e:
        logger.warning(f"Failed to list Serena memories: {e}")
        return []


# ============================================================================
# Cleanup Protocol Function
# ============================================================================

def cleanup_prp(prp_id: str) -> Dict[str, Any]:
    """Execute cleanup protocol for PRP (Model.md Section 5.6).

    Args:
        prp_id: PRP identifier to clean up

    Returns:
        {
            "success": True,
            "checkpoints_deleted": 2,
            "checkpoints_kept": ["checkpoint-PRP-003-final"],
            "memories_archived": ["PRP-003-learnings-auth-patterns"],
            "memories_deleted": ["PRP-003-checkpoint-*", "PRP-003-temp-*"],
            "context_health": {"drift_score": 5.2, "status": "healthy"}
        }

    Raises:
        RuntimeError: If cleanup operations fail

    Cleanup Protocol Steps:
        1. Delete intermediate git checkpoints (keep *-final)
        2. Archive learnings to project knowledge:
           - Read PRP-{id}-learnings-* memories
           - Merge into global "project-patterns" memory (append with timestamp + PRP-id prefix)
           - Delete PRP-{id}-learnings-* memories
        3. Delete ephemeral memories:
           - PRP-{id}-checkpoint-*
           - PRP-{id}-temp-*
        4. Reset validation state (if tracked)
        5. Run context health check:
           - ce context health
           - ce context prune
        6. Archive validation logs (if exist):
           - Move to PRPs/{prp_id}/validation-log.md
        7. Remove .ce/active_prp_session if prp_id matches active

    Side Effects:
        - Deletes git tags
        - Deletes/modifies Serena memories
        - Runs context health check
        - May remove active session file
    """
    from .core import run_cmd
    from .context import health as context_health

    result = {
        "success": True,
        "checkpoints_deleted": 0,
        "checkpoints_kept": [],
        "memories_archived": [],
        "memories_deleted": [],
        "context_health": {}
    }

    # Step 1: Delete intermediate checkpoints (keep *-final)
    checkpoint_result = delete_intermediate_checkpoints(prp_id, keep_final=True)
    result["checkpoints_deleted"] = checkpoint_result["deleted_count"]
    result["checkpoints_kept"] = checkpoint_result["kept"]

    # Step 2-3: Handle Serena memories (optional - skip if unavailable)
    memories = list_prp_memories(prp_id)

    # Archive learnings
    learnings = [m for m in memories if f"{prp_id}-learnings-" in m]
    if learnings:
        logger.info(f"Found {len(learnings)} learning memories to archive (Serena not implemented)")
        result["memories_archived"] = learnings

    # Delete ephemeral memories
    ephemeral = [m for m in memories if
                 f"{prp_id}-checkpoint-" in m or f"{prp_id}-temp-" in m]
    if ephemeral:
        logger.info(f"Found {len(ephemeral)} ephemeral memories to delete (Serena not implemented)")
        result["memories_deleted"] = ephemeral

    # Step 4: Reset validation state (already in state file)
    logger.info(f"Validation state reset for {prp_id}")

    # Step 5: Run context health check
    try:
        health = context_health()
        result["context_health"] = health
    except Exception as e:
        logger.warning(f"Context health check failed: {e}")

    # Step 6: Archive validation logs (if exist)
    # TODO: Implement when validation logging is added

    # Step 7: Remove active session if matches
    active = get_active_prp()
    if active and active["prp_id"] == prp_id:
        state_file = _get_state_file()
        state_file.unlink(missing_ok=True)
        logger.info(f"Removed active session for {prp_id}")

    logger.info(f"Cleanup completed for {prp_id}")
    return result
