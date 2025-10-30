import pytest
from pathlib import Path
import sys
import importlib.util

# Add syntropy-mcp to path with robust error handling
PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNTROPY_SCRIPTS = PROJECT_ROOT / "syntropy-mcp" / "scripts"

if not SYNTROPY_SCRIPTS.exists():
    raise ImportError(
        f"syntropy-mcp/scripts directory not found at {SYNTROPY_SCRIPTS}\n"
        "🔧 Troubleshooting: Ensure syntropy-mcp/scripts/ exists in project root"
    )

# Load the module directly from file
spec = importlib.util.spec_from_file_location(
    "generate_tool_index",
    SYNTROPY_SCRIPTS / "generate-tool-index.py"
)
generate_tool_index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate_tool_index)

parse_tool_name = generate_tool_index.parse_tool_name
group_tools_by_server = generate_tool_index.group_tools_by_server
get_server_description = generate_tool_index.get_server_description


def test_parse_tool_name():
    """Test MCP tool name parsing."""
    assert parse_tool_name("mcp__serena__find_symbol") == ("serena", "find_symbol")
    assert parse_tool_name("mcp__git__git_status") == ("git", "git_status")
    assert parse_tool_name("invalid") is None


def test_group_tools_by_server():
    """Test tool grouping by server."""
    tools = {
        "mcp__serena__find_symbol",
        "mcp__serena__search_for_pattern",
        "mcp__git__git_status"
    }

    grouped = group_tools_by_server(tools)

    assert "serena" in grouped
    assert "git" in grouped
    assert len(grouped["serena"]) == 2
    assert len(grouped["git"]) == 1


def test_get_server_description():
    """Test server description lookup."""
    assert "Code Intelligence" in get_server_description("serena")
    assert "Version Control" in get_server_description("git")
    assert "MCP Tools" in get_server_description("unknown")
