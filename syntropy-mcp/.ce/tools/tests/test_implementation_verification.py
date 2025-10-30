"""Tests for AST-based implementation verification (PRP-21 Phase 1.2).

Tests verify that function existence is checked via AST parsing, not just
whether functions are mentioned in PRP.
"""

import pytest
from pathlib import Path
from ce.update_context import verify_function_exists_ast


def test_verify_function_exists_finds_real_function(tmp_path):
    """AST verification should find function that actually exists."""
    # Create a Python file with a function
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def sync_context(target_prp=None):
    \"\"\"Sync context.\"\"\"
    return {"success": True}
""")

    result = verify_function_exists_ast("sync_context", tmp_path)
    assert result is True


def test_verify_function_exists_returns_false_when_not_found(tmp_path):
    """AST verification should return False for non-existent function."""
    # Create a Python file without the target function
    test_file = tmp_path / "test.py"
    test_file.write_text("""
def other_function():
    pass
""")

    result = verify_function_exists_ast("sync_context", tmp_path)
    assert result is False


def test_verify_function_exists_handles_nonexistent_dir():
    """AST verification should raise error for non-existent directory."""
    nonexistent_dir = Path("/fake/nonexistent/dir")

    with pytest.raises(RuntimeError, match="Search directory not found"):
        verify_function_exists_ast("sync_context", nonexistent_dir)
