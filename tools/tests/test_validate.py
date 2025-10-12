"""Tests for validation module."""

import pytest
from pathlib import Path
from ce.validate import validate_level_1, validate_level_2, validate_level_3, validate_level_4, validate_all


def test_validate_level_1_structure():
    """Test Level 1 validation returns correct structure."""
    try:
        result = validate_level_1()
        assert isinstance(result, dict)
        assert "success" in result
        assert "errors" in result
        assert "duration" in result
        assert "level" in result
        assert result["level"] == 1
    except RuntimeError:
        # npm commands not available - skip
        pytest.skip("npm commands not available")


def test_validate_level_2_structure():
    """Test Level 2 validation returns correct structure."""
    try:
        result = validate_level_2()
        assert isinstance(result, dict)
        assert "success" in result
        assert "errors" in result
        assert "duration" in result
        assert "level" in result
        assert result["level"] == 2
    except RuntimeError:
        pytest.skip("npm test command not available")


def test_validate_all_structure():
    """Test validate_all returns correct structure."""
    result = validate_all()
    assert isinstance(result, dict)
    assert "success" in result
    assert "results" in result
    assert "total_duration" in result
    assert isinstance(result["results"], dict)
    assert 1 in result["results"]
    assert 2 in result["results"]
    assert 3 in result["results"]


def test_validate_level_4_low_drift():
    """Test L4 validation with low drift sample."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    prp_path = str(fixtures_dir / "sample_prp_low_drift.md")
    impl_path = str(fixtures_dir / "sample_implementation_low.py")

    result = validate_level_4(prp_path=prp_path, implementation_paths=[impl_path])

    assert isinstance(result, dict)
    assert "success" in result
    assert "drift_score" in result
    assert "threshold_action" in result
    assert "level" in result
    assert result["level"] == 4
    assert result["drift_score"] < 30.0  # Should have low-medium drift
    assert result["threshold_action"] in ["auto_accept", "auto_fix"]


def test_validate_level_4_missing_prp():
    """Test L4 validation with missing PRP file."""
    with pytest.raises(FileNotFoundError):
        validate_level_4(prp_path="/nonexistent/prp.md", implementation_paths=["dummy.py"])


def test_validate_level_4_no_implementation_files():
    """Test L4 validation with no implementation files."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    prp_path = str(fixtures_dir / "sample_prp_low_drift.md")

    result = validate_level_4(prp_path=prp_path, implementation_paths=["/nonexistent.py"])

    assert result["success"] is False
    assert "error" in result
