"""Tests for PRP cleanup protocol."""
import pytest
from ce.prp import (
    start_prp,
    create_checkpoint,
    cleanup_prp,
    write_prp_memory,
    list_prp_memories,
    get_active_prp,
    STATE_FILE,
    STATE_DIR,
)


@pytest.fixture(autouse=True)
def cleanup_state():
    """Clean up state file before and after each test."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STATE_DIR.exists() and not any(STATE_DIR.iterdir()):
        STATE_DIR.rmdir()
    yield
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STATE_DIR.exists() and not any(STATE_DIR.iterdir()):
        STATE_DIR.rmdir()


def test_write_prp_memory_success():
    """Verify write_prp_memory creates memory entry in state."""
    start_prp("PRP-999")

    result = write_prp_memory("checkpoint", "phase1", "Test content")

    assert result["success"] is True
    assert result["memory_name"] == "PRP-999-checkpoint-phase1"
    assert result["serena_available"] is False  # Serena not implemented

    # Verify memory tracked in state
    state = get_active_prp()
    assert "PRP-999-checkpoint-phase1" in state["serena_memories"]


def test_write_prp_memory_no_active_prp():
    """Verify write_prp_memory fails when no active PRP."""
    with pytest.raises(RuntimeError, match="No active PRP session"):
        write_prp_memory("checkpoint", "phase1", "content")


def test_list_prp_memories():
    """Verify list_prp_memories returns memories from state."""
    start_prp("PRP-999")
    write_prp_memory("checkpoint", "phase1", "content1")
    write_prp_memory("learnings", "auth", "content2")

    memories = list_prp_memories("PRP-999")

    assert len(memories) == 2
    assert "PRP-999-checkpoint-phase1" in memories
    assert "PRP-999-learnings-auth" in memories


def test_cleanup_prp_removes_session():
    """Verify cleanup_prp removes active session."""
    start_prp("PRP-999")
    assert STATE_FILE.exists()

    result = cleanup_prp("PRP-999")

    assert result["success"] is True
    assert not STATE_FILE.exists()


def test_cleanup_prp_archives_learnings():
    """Verify cleanup_prp identifies learnings for archiving."""
    start_prp("PRP-999")
    write_prp_memory("learnings", "auth-patterns", "Auth learnings")
    write_prp_memory("checkpoint", "phase1", "Checkpoint")
    write_prp_memory("temp", "scratch", "Temp data")

    result = cleanup_prp("PRP-999")

    assert result["success"] is True
    assert "PRP-999-learnings-auth-patterns" in result["memories_archived"]


def test_cleanup_prp_identifies_ephemeral():
    """Verify cleanup_prp identifies ephemeral memories."""
    start_prp("PRP-999")
    write_prp_memory("checkpoint", "phase1", "Checkpoint")
    write_prp_memory("temp", "scratch", "Temp")

    result = cleanup_prp("PRP-999")

    assert "PRP-999-checkpoint-phase1" in result["memories_deleted"]
    assert "PRP-999-temp-scratch" in result["memories_deleted"]


def test_cleanup_prp_with_checkpoints():
    """Verify cleanup_prp deletes intermediate checkpoints."""
    start_prp("PRP-999")

    create_checkpoint("phase1")
    create_checkpoint("phase2")
    create_checkpoint("final")

    result = cleanup_prp("PRP-999")

    assert result["success"] is True
    assert result["checkpoints_deleted"] == 2
    # Multiple final checkpoints may exist from previous test runs
    assert len(result["checkpoints_kept"]) >= 1
    assert all("final" in cp for cp in result["checkpoints_kept"])


def test_cleanup_prp_context_health():
    """Verify cleanup_prp runs context health check."""
    start_prp("PRP-999")

    result = cleanup_prp("PRP-999")

    assert result["success"] is True
    assert "context_health" in result
