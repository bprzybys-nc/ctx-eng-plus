"""Tests for validation module."""

import pytest
from ce.validate import validate_level_1, validate_level_2, validate_level_3, validate_all


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
