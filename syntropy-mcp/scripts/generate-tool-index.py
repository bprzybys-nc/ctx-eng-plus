#!/usr/bin/env python3
"""Generate tool-index.md from MCP server configuration.

Approach:
1. Parse settings.local.json for allowed tools
2. Group tools by MCP server
3. Generate markdown with tool descriptions
4. Save to syntropy-mcp/tool-index.md

Note: This initial version uses static metadata from config.
Future enhancement: Query live MCP servers for real-time metadata.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set


def load_allowed_tools() -> Set[str]:
    """Load allowed MCP tools from settings.local.json.

    Returns:
        Set of allowed tool names (e.g., 'mcp__serena__find_symbol')
    """
    config_path = Path(".claude/settings.local.json")

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "🔧 Troubleshooting: Run from project root directory"
        )

    with open(config_path) as f:
        config = json.load(f)

    allowed = config.get("permissions", {}).get("allow", [])

    # Filter for MCP tools only (start with mcp__)
    mcp_tools = {tool for tool in allowed if tool.startswith("mcp__")}

    if not mcp_tools:
        raise ValueError(
            "No MCP tools found in configuration\n"
            "🔧 Troubleshooting: Check permissions.allow in settings.local.json"
        )

    return mcp_tools


def parse_tool_name(tool: str) -> tuple[str, str] | None:
    """Parse MCP tool name into server and tool components.

    Args:
        tool: MCP tool name (e.g., 'mcp__serena__find_symbol')

    Returns:
        Tuple of (server, tool_name) or None if invalid format

    Example:
        >>> parse_tool_name('mcp__serena__find_symbol')
        ('serena', 'find_symbol')
    """
    match = re.match(r'^mcp__([^_]+)__(.+)$', tool)
    if not match:
        return None

    server, tool_name = match.groups()
    return (server, tool_name)


def group_tools_by_server(tools: Set[str]) -> Dict[str, List[str]]:
    """Group MCP tools by server name.

    Args:
        tools: Set of MCP tool names

    Returns:
        Dict mapping server name to list of tool names

    Example:
        >>> group_tools_by_server({'mcp__serena__find_symbol', 'mcp__git__git_status'})
        {'serena': ['find_symbol'], 'git': ['git_status']}
    """
    grouped: Dict[str, List[str]] = {}

    for tool in tools:
        parsed = parse_tool_name(tool)
        if not parsed:
            continue

        server, tool_name = parsed

        if server not in grouped:
            grouped[server] = []

        grouped[server].append(tool_name)

    # Sort tools within each server
    for server in grouped:
        grouped[server].sort()

    return grouped


def get_server_description(server: str) -> str:
    """Get human-readable description for MCP server.

    Args:
        server: MCP server name

    Returns:
        Description string
    """
    descriptions = {
        "serena": "Code Intelligence Tools",
        "filesystem": "File Operations",
        "git": "Version Control",
        "context7": "Documentation",
        "sequential-thinking": "Advanced Reasoning",
        "linear-server": "Project Management",
        "repomix": "Codebase Analysis"
    }

    return descriptions.get(server, "MCP Tools")


def generate_tool_entry(server: str, tool: str) -> List[str]:
    """Generate markdown entry for a tool.

    Args:
        server: MCP server name
        tool: Tool name

    Returns:
        List of markdown lines
    """
    return [
        f"### `syntropy:{server}:{tool}`",
        "",
        f"**Original**: `mcp__{server}__{tool}`",
        "",
        "**Description**: *(Auto-generated from MCP metadata)*",
        "",
        "**Parameters**: *(See MCP server documentation)*",
        "",
    ]


def generate_markdown(grouped_tools: Dict[str, List[str]]) -> str:
    """Generate markdown documentation from grouped tools.

    Args:
        grouped_tools: Dict mapping server to list of tools

    Returns:
        Markdown formatted string
    """
    lines = [
        "# Syntropy MCP Tool Index",
        "",
        "Auto-generated from MCP server configuration.",
        f"Last updated: {datetime.now().isoformat()}",
        "",
        "## Overview",
        "",
        f"Total servers: {len(grouped_tools)}",
        f"Total tools: {sum(len(tools) for tools in grouped_tools.values())}",
        "",
    ]

    # Generate entry for each server
    for server in sorted(grouped_tools.keys()):
        tools = grouped_tools[server]
        description = get_server_description(server)

        lines.append(f"## syntropy:{server} - {description}")
        lines.append("")
        lines.append(f"**Tool Count**: {len(tools)}")
        lines.append("")

        # List each tool
        for tool in tools:
            lines.extend(generate_tool_entry(server, tool))

    # Add usage examples
    lines.extend([
        "---",
        "",
        "## Usage Examples",
        "",
        "### Before (Direct MCP)",
        "```typescript",
        'await mcp.call("mcp__serena__find_symbol", {',
        '  name_path: "MyClass/method",',
        '  relative_path: "src/main.py"',
        "});",
        "```",
        "",
        "### After (Syntropy)",
        "```typescript",
        'await mcp.call("syntropy:serena:find_symbol", {',
        '  name_path: "MyClass/method",',
        '  relative_path: "src/main.py"',
        "});",
        "```",
        "",
    ])

    return "\n".join(lines)


def main():
    """Generate tool index documentation."""
    print("Generating Syntropy MCP tool index...")

    try:
        # Load and parse tools
        tools = load_allowed_tools()
        print(f"  Found {len(tools)} MCP tools")

        grouped = group_tools_by_server(tools)
        print(f"  Grouped into {len(grouped)} servers")

        # Generate markdown
        markdown = generate_markdown(grouped)

        # Write to file
        output_path = Path("syntropy-mcp/tool-index.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown)

        print(f"✅ Generated {output_path}")
        print(f"   Servers: {', '.join(sorted(grouped.keys()))}")

    except Exception as e:
        print(f"❌ Failed to generate tool index: {e}")
        raise


if __name__ == "__main__":
    main()
