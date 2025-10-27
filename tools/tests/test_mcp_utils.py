"""Tests for MCP utility functions."""

import pytest
from ce.mcp_utils import (
    call_syntropy_mcp,
    is_mcp_available,
    call_sequential_thinking
)


def test_call_syntropy_mcp_raises_not_implemented():
    """Test MCP call raises until implemented."""
    with pytest.raises(RuntimeError, match="not yet implemented"):
        call_syntropy_mcp("thinking", "sequentialthinking", {})


def test_is_mcp_available_returns_false():
    """Test availability check returns False until implemented."""
    assert is_mcp_available("thinking") is False
    assert is_mcp_available("serena") is False


def test_call_sequential_thinking_returns_none():
    """Test sequential thinking wrapper returns None gracefully."""
    result = call_sequential_thinking("Test prompt")
    assert result is None
