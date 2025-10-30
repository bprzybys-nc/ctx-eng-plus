"""Tests for Serena-based implementation verification (PRP-16)."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


# === Unit Tests ===

def test_verify_with_serena_all_found():
    """Test successful verification when all functions found."""
    from ce.update_context import verify_implementation_with_serena

    # Mock the module import
    mock_serena = MagicMock()
    mock_serena.find_symbol.side_effect = [
        [{"name": "func1", "kind": "Function"}],  # Found
        [{"name": "func2", "kind": "Function"}]   # Found
    ]

    with patch.dict('sys.modules', {'mcp__serena': mock_serena}):
        result = verify_implementation_with_serena(["func1", "func2"])

        assert result is True
        assert mock_serena.find_symbol.call_count == 2


def test_verify_with_serena_some_missing():
    """Test verification when some functions missing."""
    from ce.update_context import verify_implementation_with_serena

    # Mock the module import
    mock_serena = MagicMock()
    mock_serena.find_symbol.side_effect = [
        [{"name": "func1", "kind": "Function"}],  # Found
        []                                         # Not found
    ]

    with patch.dict('sys.modules', {'mcp__serena': mock_serena}):
        result = verify_implementation_with_serena(["func1", "missing_func"])

        assert result is False  # Not all found
        assert mock_serena.find_symbol.call_count == 2


def test_verify_with_serena_empty_list():
    """Test verification with no functions to verify."""
    from ce.update_context import verify_implementation_with_serena

    result = verify_implementation_with_serena([])

    assert result is True  # No functions = nothing to verify = success


def test_verify_serena_unavailable():
    """Test graceful degradation when Serena MCP unavailable."""
    from ce.update_context import verify_implementation_with_serena

    # Mock ImportError when trying to import mcp__serena
    # Set module to None to trigger ImportError
    import sys
    orig_module = sys.modules.get('mcp__serena')
    try:
        sys.modules['mcp__serena'] = None
        result = verify_implementation_with_serena(["some_function"])
        assert result is False  # Gracefully degrade
    finally:
        # Restore original state
        if orig_module is None:
            sys.modules.pop('mcp__serena', None)
        else:
            sys.modules['mcp__serena'] = orig_module


def test_verify_serena_query_exception():
    """Test handling of Serena query exceptions."""
    from ce.update_context import verify_implementation_with_serena

    # Mock the module import
    mock_serena = MagicMock()
    mock_serena.find_symbol.side_effect = RuntimeError("Connection lost")

    with patch.dict('sys.modules', {'mcp__serena': mock_serena}):
        result = verify_implementation_with_serena(["func1"])

        assert result is False  # Gracefully handle error


# === Integration Tests ===

@pytest.mark.integration
def test_sync_context_with_serena_verification(tmp_path):
    """Integration test: sync_context calls Serena verification."""
    from ce.update_context import sync_context

    # Create mock PRP file
    prp_path = tmp_path / "PRPs" / "feature-requests" / "PRP-TEST.md"
    prp_path.parent.mkdir(parents=True, exist_ok=True)
    prp_path.write_text("""---
name: "Test PRP"
prp_id: "PRP-TEST"
status: "new"
context_sync:
  ce_updated: false
  serena_updated: false
---

# Test PRP

Implementation:
```python
def test_function():
    pass
```
""")

    # Mock the module import
    mock_serena = MagicMock()
    mock_serena.find_symbol.return_value = [{"name": "test_function"}]

    with patch.dict('sys.modules', {'mcp__serena': mock_serena}), \
         patch("ce.update_context.verify_codebase_matches_examples", return_value={"violations": [], "drift_score": 0}), \
         patch("ce.update_context.detect_missing_examples_for_prps", return_value=[]):

        # Run sync with target PRP
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = sync_context(target_prp=str(prp_path))
        finally:
            os.chdir(original_cwd)

        # Verify sync completed
        assert result["success"] is True
        assert result["prps_scanned"] == 1
        assert result["serena_updated_count"] == 1


@pytest.mark.integration
def test_real_serena_verification():
    """Integration test with real Serena MCP (if available)."""
    from ce.update_context import verify_implementation_with_serena

    # Try verifying a known function in the codebase
    known_functions = ["sync_context", "read_prp_header"]

    try:
        result = verify_implementation_with_serena(known_functions)
        # Should be True if Serena available and functions found
        # Should be False if Serena unavailable (graceful degradation)
        assert isinstance(result, bool)
    except Exception:
        pytest.skip("Serena MCP not available")


# === E2E Test ===

@pytest.mark.e2e
def test_full_context_sync_with_verification(tmp_path):
    """E2E test: Full context sync workflow with Serena verification."""
    from ce.update_context import sync_context

    # Create test project structure
    prps_dir = tmp_path / "PRPs" / "executed"
    prps_dir.mkdir(parents=True, exist_ok=True)

    prp_file = prps_dir / "PRP-1-test.md"
    prp_file.write_text("""---
name: "Test Feature"
prp_id: "PRP-1"
status: "executed"
context_sync:
  ce_updated: false
  serena_updated: false
---

# Test Feature

Implements `calculate_score()` and `detect_violations()` functions.
""")

    # Mock the module import
    mock_serena = MagicMock()
    mock_serena.find_symbol.return_value = [{"name": "calculate_score"}]

    with patch.dict('sys.modules', {'mcp__serena': mock_serena}), \
         patch("ce.update_context.verify_codebase_matches_examples", return_value={"violations": [], "drift_score": 0}), \
         patch("ce.update_context.detect_missing_examples_for_prps", return_value=[]):

        # Run sync
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = sync_context()
        finally:
            os.chdir(original_cwd)

        # Verify results
        assert result["success"] is True
        assert result["prps_scanned"] >= 1

        # Check YAML headers updated
        from ce.update_context import read_prp_header
        metadata, _ = read_prp_header(prp_file)
        assert "context_sync" in metadata
        assert "last_sync" in metadata["context_sync"]
