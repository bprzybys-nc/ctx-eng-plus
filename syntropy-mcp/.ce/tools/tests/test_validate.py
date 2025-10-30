"""Tests for validation module."""

import pytest
from pathlib import Path
from ce.validate import validate_level_1, validate_level_2, validate_level_3, validate_level_4, validate_all, calculate_confidence


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
    result = validate_level_4(prp_path="/nonexistent/prp.md", implementation_paths=["dummy.py"])
    assert result["success"] is False
    assert "error" in result


def test_validate_level_4_no_implementation_files():
    """Test L4 validation with no implementation files."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    prp_path = str(fixtures_dir / "sample_prp_low_drift.md")

    result = validate_level_4(prp_path=prp_path, implementation_paths=["/nonexistent.py"])

    assert result["success"] is False
    assert "error" in result


def test_calculate_confidence_all_pass():
    """Test confidence calculation with all levels passing."""
    results = {
        1: {"success": True},
        2: {"success": True, "coverage": 0.85},
        3: {"success": True},
        4: {"success": True, "drift_score": 8.0}
    }
    assert calculate_confidence(results) == 10


def test_calculate_confidence_without_l4():
    """Test confidence calculation without L4."""
    results = {
        1: {"success": True},
        2: {"success": True, "coverage": 0.85},
        3: {"success": True}
    }
    # 6 + 1 (L1) + 2 (L2 with coverage) + 1 (L3) = 10
    # Without L4 passing, max is still 10 from L1+L2+L3
    assert calculate_confidence(results) == 10


def test_calculate_confidence_baseline():
    """Test confidence calculation baseline (no passes)."""
    results = {
        1: {"success": False},
        2: {"success": False},
        3: {"success": False}
    }
    assert calculate_confidence(results) == 6
