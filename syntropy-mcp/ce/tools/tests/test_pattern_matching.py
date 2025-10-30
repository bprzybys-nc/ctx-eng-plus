"""Tests for AST-based pattern matching (PRP-21 Phase 1.3).

Tests verify that pattern detection uses AST parsing instead of regex,
avoiding false positives/negatives from multiline code and comments.
"""

import pytest
from pathlib import Path
from ce.pattern_detectors import (
    check_pattern_category,
    _check_bare_except_ast,
    _check_missing_troubleshooting_ast
)
import ast


def test_ast_detects_bare_except(tmp_path):
    """AST should detect bare except clauses."""
    code = """
try:
    risky_operation()
except:
    pass
"""
    tree = ast.parse(code)
    result = _check_bare_except_ast(tree)
    assert result is True


def test_ast_ignores_specific_except(tmp_path):
    """AST should not flag specific exception types."""
    code = """
try:
    risky_operation()
except ValueError:
    pass
"""
    tree = ast.parse(code)
    result = _check_bare_except_ast(tree)
    assert result is False


def test_ast_detects_missing_troubleshooting(tmp_path):
    """AST should detect raise without 🔧 troubleshooting."""
    code = """
def func():
    if error:
        raise RuntimeError("Something failed")
"""
    tree = ast.parse(code)
    result = _check_missing_troubleshooting_ast(tree, code)
    assert result is True


def test_ast_ignores_raise_with_troubleshooting(tmp_path):
    """AST should not flag raise statements with 🔧."""
    code = """
def func():
    if error:
        raise RuntimeError(
            "Something failed\\n"
            "🔧 Troubleshooting: Check configuration"
        )
"""
    tree = ast.parse(code)
    result = _check_missing_troubleshooting_ast(tree, code)
    assert result is False
