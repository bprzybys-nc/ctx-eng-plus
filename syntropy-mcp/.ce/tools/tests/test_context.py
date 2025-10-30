"""Tests for context management."""

import pytest
from pathlib import Path
from ce.context import (
    sync, health, prune,
    pre_generation_sync, post_execution_sync,
    verify_git_clean, check_drift_threshold,
    context_health_verbose, drift_report_markdown,
    calculate_drift_score,
    enable_auto_sync, disable_auto_sync, is_auto_sync_enabled, get_auto_sync_status
)
from ce.exceptions import ContextDriftError


def test_sync_structure():
    """Test sync returns correct structure."""
    try:
        result = sync()
        assert isinstance(result, dict)
        assert "reindexed_count" in result
        assert "files" in result
        assert "drift_score" in result
        assert "drift_level" in result
        assert result["drift_level"] in ["LOW", "MEDIUM", "HIGH"]
    except RuntimeError:
        pytest.skip("Not in a git repository")


def test_health_structure():
    """Test health check returns correct structure."""
    result = health()
    assert isinstance(result, dict)
    assert "healthy" in result
    assert "compilation" in result
    assert "git_clean" in result
    assert "tests_passing" in result
    assert "drift_score" in result
    assert "drift_level" in result
    assert "recommendations" in result
    assert isinstance(result["recommendations"], list)


def test_prune_placeholder():
    """Test prune placeholder implementation."""
    result = prune(age_days=7, dry_run=True)
    assert isinstance(result, dict)
    assert "deleted_count" in result
    assert "files_deleted" in result
    assert "dry_run" in result
    assert result["dry_run"] is True


# ============================================================================
# Pre-Generation Sync Tests (Phase 1)
# ============================================================================

def test_verify_git_clean():
    """Test git clean state verification."""
    try:
        result = verify_git_clean()
        assert isinstance(result, dict)
        assert "clean" in result
        assert "uncommitted_files" in result
        assert "untracked_files" in result
    except RuntimeError:
        # Expected if repo has uncommitted changes
        pytest.skip("Repository has uncommitted changes (expected)")


def test_check_drift_threshold_healthy():
    """Test drift check passes for healthy drift score."""
    # Should not raise for drift <= 10%
    check_drift_threshold(5.0, force=False)
    check_drift_threshold(10.0, force=False)


def test_check_drift_threshold_warn():
    """Test drift check warns for moderate drift."""
    # Should not raise for drift 10-30%
    check_drift_threshold(15.0, force=False)
    check_drift_threshold(30.0, force=False)


def test_check_drift_threshold_critical():
    """Test drift check aborts for high drift."""
    # Should raise for drift > 30%
    with pytest.raises(ContextDriftError) as exc:
        check_drift_threshold(35.0, force=False)
    assert "35" in str(exc.value)
    assert "troubleshooting" in str(exc.value).lower()


def test_check_drift_threshold_force():
    """Test drift check can be forced."""
    # Should not raise even with high drift if forced
    check_drift_threshold(50.0, force=True)


def test_pre_generation_sync_structure():
    """Test pre-generation sync returns correct structure."""
    try:
        result = pre_generation_sync(force=True)  # Force to skip potential drift abort
        assert isinstance(result, dict)
        assert "success" in result
        assert "sync_completed" in result
        assert "drift_score" in result
        assert "git_clean" in result
        assert "abort_triggered" in result
        assert "warnings" in result
    except RuntimeError:
        pytest.skip("Git or validation not available")


# ============================================================================
# Post-Execution Sync Tests (Phase 2)
# ============================================================================

def test_post_execution_sync_structure():
    """Test post-execution sync returns correct structure."""
    # Test with skip_cleanup to avoid PRP state dependencies
    result = post_execution_sync("PRP-TEST", skip_cleanup=True)
    assert isinstance(result, dict)
    assert "success" in result
    assert "cleanup_completed" in result
    assert "sync_completed" in result
    assert "drift_score" in result


# ============================================================================
# Drift Detection & Reporting Tests (Phase 3)
# ============================================================================

def test_calculate_drift_score():
    """Test drift score calculation."""
    drift = calculate_drift_score()
    assert isinstance(drift, float)
    assert 0 <= drift <= 100


def test_context_health_verbose():
    """Test verbose health report structure."""
    result = context_health_verbose()
    assert isinstance(result, dict)
    assert "drift_score" in result
    assert "threshold" in result
    assert result["threshold"] in ["healthy", "warn", "critical"]
    assert "components" in result
    assert "recommendations" in result

    # Check components
    components = result["components"]
    assert "file_changes" in components
    assert "memory_staleness" in components
    assert "dependency_changes" in components
    assert "uncommitted_changes" in components

    # Each component has score and details
    for comp in components.values():
        assert "score" in comp
        assert "details" in comp


def test_drift_report_markdown():
    """Test markdown drift report generation."""
    report = drift_report_markdown()
    assert isinstance(report, str)
    assert "Context Health Report" in report
    assert "Drift Score" in report
    assert "Components" in report


# ============================================================================
# Auto-Sync Mode Tests (Phase 4)
# ============================================================================

def test_auto_sync_enable_disable():
    """Test enabling and disabling auto-sync mode."""
    # Clean up any existing config
    config_file = Path(".ce/config")
    if config_file.exists():
        config_file.unlink()

    # Should start disabled
    assert is_auto_sync_enabled() is False

    # Enable
    result = enable_auto_sync()
    assert result["success"] is True
    assert result["mode"] == "enabled"
    assert is_auto_sync_enabled() is True

    # Disable
    result = disable_auto_sync()
    assert result["success"] is True
    assert result["mode"] == "disabled"
    assert is_auto_sync_enabled() is False

    # Clean up
    if config_file.exists():
        config_file.unlink()


def test_get_auto_sync_status():
    """Test auto-sync status check."""
    # Clean up any existing config
    config_file = Path(".ce/config")
    if config_file.exists():
        config_file.unlink()

    # Should be disabled initially
    status = get_auto_sync_status()
    assert status["enabled"] is False
    assert "message" in status

    # Enable and check again
    enable_auto_sync()
    status = get_auto_sync_status()
    assert status["enabled"] is True

    # Clean up
    if config_file.exists():
        config_file.unlink()


def test_auto_sync_config_persistence():
    """Test auto-sync config persists across calls."""
    config_file = Path(".ce/config")
    if config_file.exists():
        config_file.unlink()

    # Enable
    enable_auto_sync()

    # Check it persists
    assert is_auto_sync_enabled() is True

    # Disable and check
    disable_auto_sync()
    assert is_auto_sync_enabled() is False

    # Clean up
    if config_file.exists():
        config_file.unlink()
