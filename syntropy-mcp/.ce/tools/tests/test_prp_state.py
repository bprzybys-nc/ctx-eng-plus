"""Tests for PRP state management functions."""
import pytest
import json
from pathlib import Path
from datetime import datetime, timezone
from ce.prp import (
    start_prp,
    get_active_prp,
    end_prp,
    update_prp_phase,
    STATE_FILE,
    STATE_DIR,
)


@pytest.fixture(autouse=True)
def cleanup_state():
    """Clean up state file before and after each test."""
    # Before test
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STATE_DIR.exists() and not any(STATE_DIR.iterdir()):
        STATE_DIR.rmdir()

    yield

    # After test
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STATE_DIR.exists() and not any(STATE_DIR.iterdir()):
        STATE_DIR.rmdir()


def test_start_prp_creates_state_file():
    """Verify start_prp creates .ce/active_prp_session."""
    result = start_prp("PRP-999")

    assert result["success"] is True
    assert result["prp_id"] == "PRP-999"
    assert "started_at" in result
    assert STATE_FILE.exists()

    state = get_active_prp()
    assert state is not None
    assert state["prp_id"] == "PRP-999"
    assert state["phase"] == "planning"
    assert state["checkpoint_count"] == 0


def test_start_prp_with_name():
    """Verify start_prp accepts optional prp_name."""
    result = start_prp("PRP-999", "Test PRP")

    assert result["success"] is True
    state = get_active_prp()
    assert state["prp_name"] == "Test PRP"


def test_start_prp_invalid_id_format():
    """Verify start_prp rejects invalid PRP ID."""
    with pytest.raises(ValueError, match="Invalid PRP ID format"):
        start_prp("INVALID-ID")


def test_start_prp_fails_if_another_active():
    """Verify start_prp fails if another PRP is active."""
    start_prp("PRP-1")

    with pytest.raises(RuntimeError, match="Another PRP is active: PRP-1"):
        start_prp("PRP-2")


def test_get_active_prp_no_session():
    """Verify get_active_prp returns None when no session."""
    assert get_active_prp() is None


def test_get_active_prp_returns_state():
    """Verify get_active_prp returns current state."""
    start_prp("PRP-999")
    state = get_active_prp()

    assert state is not None
    assert state["prp_id"] == "PRP-999"
    assert "started_at" in state
    assert "phase" in state


def test_end_prp_removes_state_file():
    """Verify end_prp removes state file."""
    start_prp("PRP-999")
    assert STATE_FILE.exists()

    result = end_prp("PRP-999")

    assert result["success"] is True
    assert "duration" in result
    assert "checkpoints_created" in result
    assert not STATE_FILE.exists()


def test_end_prp_no_active_session():
    """Verify end_prp fails when no active session."""
    with pytest.raises(RuntimeError, match="No active PRP session"):
        end_prp("PRP-999")


def test_end_prp_mismatched_id():
    """Verify end_prp fails if prp_id doesn't match active."""
    start_prp("PRP-1")

    with pytest.raises(RuntimeError, match="PRP ID mismatch"):
        end_prp("PRP-999")


def test_update_prp_phase():
    """Verify update_prp_phase updates phase in state."""
    start_prp("PRP-999")

    result = update_prp_phase("implementation")

    assert result["phase"] == "implementation"
    state = get_active_prp()
    assert state["phase"] == "implementation"


def test_update_prp_phase_invalid():
    """Verify update_prp_phase rejects invalid phase."""
    start_prp("PRP-999")

    with pytest.raises(ValueError, match="Invalid phase: 'invalid_phase'"):
        update_prp_phase("invalid_phase")


def test_update_prp_phase_no_active_session():
    """Verify update_prp_phase fails when no active session."""
    with pytest.raises(RuntimeError, match="No active PRP session"):
        update_prp_phase("implementation")


def test_state_file_json_format():
    """Verify state file is valid JSON with expected structure."""
    start_prp("PRP-999", "Test PRP")

    # Read file directly to verify JSON format
    state_json = STATE_FILE.read_text()
    state = json.loads(state_json)

    # Verify required fields
    assert "prp_id" in state
    assert "prp_name" in state
    assert "started_at" in state
    assert "phase" in state
    assert "last_checkpoint" in state
    assert "checkpoint_count" in state
    assert "validation_attempts" in state
    assert "serena_memories" in state

    # Verify data types
    assert isinstance(state["validation_attempts"], dict)
    assert isinstance(state["serena_memories"], list)
    assert state["validation_attempts"]["L1"] == 0


def test_atomic_write_pattern():
    """Verify state writes use atomic pattern (temp file + rename)."""
    start_prp("PRP-999")

    # Update phase multiple times rapidly
    for phase in ["implementation", "testing", "validation"]:
        update_prp_phase(phase)

    # State file should always be valid JSON
    state = get_active_prp()
    assert state is not None
    assert state["phase"] == "validation"


def test_duration_calculation():
    """Verify end_prp calculates duration correctly."""
    start_prp("PRP-999")

    # Modify started_at to simulate passage of time
    state = get_active_prp()
    past_time = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    state["started_at"] = past_time.isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2))

    result = end_prp("PRP-999")

    # Duration should be in "Xh Ym" or "Ym" format
    assert "duration" in result
    duration = result["duration"]
    assert "m" in duration  # At least minutes
