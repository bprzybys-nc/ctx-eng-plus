"""Tests for PRP checkpoint management functions."""
import pytest
import subprocess
from pathlib import Path
from ce.prp import (
    start_prp,
    end_prp,
    create_checkpoint,
    list_checkpoints,
    delete_intermediate_checkpoints,
    STATE_FILE,
    STATE_DIR,
)


@pytest.fixture(autouse=True)
def cleanup_state():
    """Clean up state file and test checkpoints before and after each test."""
    # Before test
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STATE_DIR.exists() and not any(STATE_DIR.iterdir()):
        STATE_DIR.rmdir()

    # Clean up any test checkpoints
    _cleanup_test_checkpoints()

    yield

    # After test
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    if STATE_DIR.exists() and not any(STATE_DIR.iterdir()):
        STATE_DIR.rmdir()
    _cleanup_test_checkpoints()


def _cleanup_test_checkpoints():
    """Remove all test checkpoints from git."""
    try:
        result = subprocess.run(
            ["git", "tag", "-l", "checkpoint-PRP-*"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0 and result.stdout.strip():
            tags = result.stdout.strip().split("\n")
            for tag in tags:
                subprocess.run(["git", "tag", "-d", tag], capture_output=True, check=False)
    except Exception:
        pass


def test_create_checkpoint_success():
    """Verify create_checkpoint creates git tag successfully."""
    start_prp("PRP-999")

    result = create_checkpoint("phase1", "Test checkpoint")

    assert result["success"] is True
    assert "checkpoint-PRP-999-phase1" in result["tag_name"]
    assert "commit_sha" in result
    assert result["message"] == "Test checkpoint"

    # Verify tag was created
    tags_result = subprocess.run(
        ["git", "tag", "-l", "checkpoint-PRP-999-*"],
        capture_output=True,
        text=True,
        check=True
    )
    assert "checkpoint-PRP-999-phase1" in tags_result.stdout


def test_create_checkpoint_no_active_prp():
    """Verify create_checkpoint fails when no active PRP."""
    with pytest.raises(RuntimeError, match="No active PRP session"):
        create_checkpoint("phase1")


def test_create_checkpoint_updates_state():
    """Verify create_checkpoint updates state file."""
    start_prp("PRP-999")

    result = create_checkpoint("phase1")

    # Check state file was updated
    import json
    state = json.loads(STATE_FILE.read_text())
    assert state["last_checkpoint"] == result["tag_name"]
    assert state["checkpoint_count"] == 1


def test_create_multiple_checkpoints():
    """Verify multiple checkpoints can be created."""
    start_prp("PRP-999")

    cp1 = create_checkpoint("phase1")
    cp2 = create_checkpoint("phase2")
    cp3 = create_checkpoint("final")

    # Verify all tags exist
    tags_result = subprocess.run(
        ["git", "tag", "-l", "checkpoint-PRP-999-*"],
        capture_output=True,
        text=True,
        check=True
    )
    tags = tags_result.stdout.strip().split("\n")
    assert len(tags) == 3
    assert any("phase1" in tag for tag in tags)
    assert any("phase2" in tag for tag in tags)
    assert any("final" in tag for tag in tags)


def test_list_checkpoints_empty():
    """Verify list_checkpoints returns empty list when no checkpoints."""
    checkpoints = list_checkpoints("PRP-999")
    assert checkpoints == []


def test_list_checkpoints_returns_all():
    """Verify list_checkpoints returns all checkpoints for PRP."""
    start_prp("PRP-999")

    create_checkpoint("phase1")
    create_checkpoint("phase2")
    create_checkpoint("final")

    checkpoints = list_checkpoints("PRP-999")

    assert len(checkpoints) == 3
    assert all(cp["prp_id"] == "PRP-999" for cp in checkpoints)
    phases = [cp["phase"] for cp in checkpoints]
    assert "phase1" in phases
    assert "phase2" in phases
    assert "final" in phases


def test_list_checkpoints_filter_by_prp():
    """Verify list_checkpoints filters by prp_id."""
    # Create checkpoints for different PRPs
    start_prp("PRP-1")
    create_checkpoint("phase1")
    end_prp("PRP-1")

    start_prp("PRP-2")
    create_checkpoint("phase1")
    end_prp("PRP-2")

    # List checkpoints for PRP-1 only
    checkpoints = list_checkpoints("PRP-1")

    assert len(checkpoints) == 1
    assert checkpoints[0]["prp_id"] == "PRP-1"


def test_list_checkpoints_all_prps():
    """Verify list_checkpoints(None) returns checkpoints for all PRPs."""
    start_prp("PRP-1")
    create_checkpoint("phase1")
    end_prp("PRP-1")

    start_prp("PRP-2")
    create_checkpoint("phase1")
    end_prp("PRP-2")

    checkpoints = list_checkpoints(None)

    assert len(checkpoints) == 2
    prp_ids = [cp["prp_id"] for cp in checkpoints]
    assert "PRP-1" in prp_ids
    assert "PRP-2" in prp_ids


def test_delete_intermediate_checkpoints_keep_final():
    """Verify delete_intermediate_checkpoints keeps final checkpoint."""
    start_prp("PRP-999")

    create_checkpoint("phase1")
    create_checkpoint("phase2")
    create_checkpoint("final")

    result = delete_intermediate_checkpoints("PRP-999", keep_final=True)

    assert result["success"] is True
    assert result["deleted_count"] == 2
    assert len(result["kept"]) == 1
    assert "final" in result["kept"][0]

    # Verify only final checkpoint remains
    checkpoints = list_checkpoints("PRP-999")
    assert len(checkpoints) == 1
    assert checkpoints[0]["phase"] == "final"


def test_delete_intermediate_checkpoints_delete_all():
    """Verify delete_intermediate_checkpoints deletes all when keep_final=False."""
    start_prp("PRP-999")

    create_checkpoint("phase1")
    create_checkpoint("phase2")
    create_checkpoint("final")

    result = delete_intermediate_checkpoints("PRP-999", keep_final=False)

    assert result["success"] is True
    assert result["deleted_count"] == 3
    assert result["kept"] == []

    # Verify no checkpoints remain
    checkpoints = list_checkpoints("PRP-999")
    assert len(checkpoints) == 0


def test_delete_intermediate_checkpoints_no_checkpoints():
    """Verify delete_intermediate_checkpoints handles no checkpoints gracefully."""
    result = delete_intermediate_checkpoints("PRP-999")

    assert result["success"] is True
    assert result["deleted_count"] == 0
    assert result["kept"] == []


def test_checkpoint_naming_convention():
    """Verify checkpoint names follow convention."""
    start_prp("PRP-999")

    result = create_checkpoint("phase1")

    # Format: checkpoint-{prp_id}-{phase}-{timestamp}
    tag_name = result["tag_name"]
    assert tag_name.startswith("checkpoint-PRP-999-phase1-")

    # Timestamp should be YYYYMMDD-HHMMSS format
    timestamp_part = tag_name.split("-", 3)[3]
    parts = timestamp_part.split("-")
    assert len(parts) == 2  # YYYYMMDD-HHMMSS
    assert len(parts[0]) == 8  # YYYYMMDD
    assert len(parts[1]) == 6  # HHMMSS


def test_checkpoint_metadata():
    """Verify checkpoint metadata is complete."""
    start_prp("PRP-999")

    result = create_checkpoint("phase1", "Phase 1 complete")

    checkpoints = list_checkpoints("PRP-999")
    assert len(checkpoints) == 1

    cp = checkpoints[0]
    assert cp["tag_name"] == result["tag_name"]
    assert cp["prp_id"] == "PRP-999"
    assert cp["phase"] == "phase1"
    assert cp["timestamp"]  # Should have ISO timestamp
    assert cp["commit_sha"]
    assert cp["message"] == "Phase 1 complete"
