"""Tests for context management."""

import pytest
from ce.context import sync, health, prune


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
