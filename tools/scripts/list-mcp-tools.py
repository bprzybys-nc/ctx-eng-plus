#!/usr/bin/env python3
"""List all allowed MCP tools from settings.local.json"""

import json
import subprocess
from pathlib import Path
from collections import defaultdict

def get_git_root():
    """Get git repository root."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout.strip() if result.returncode == 0 else str(Path.cwd())

def main():
    # Find settings file
    git_root = Path(get_git_root())
    settings_file = git_root / ".claude" / "settings.local.json"

    if not settings_file.exists():
        print(f"❌ Settings file not found: {settings_file}")
        return 1

    # Load and parse
    with open(settings_file) as f:
        settings = json.load(f)

    # Extract MCP tools
    allowed = settings.get("permissions", {}).get("allow", [])
    mcp_tools = [t for t in allowed if t.startswith("mcp__syntropy_")]

    # Group by server
    grouped = defaultdict(list)
    for tool in sorted(mcp_tools):
        # Remove mcp__syntropy_ prefix
        tool_name = tool.replace("mcp__syntropy_", "")
        # Extract server (first segment before underscore)
        parts = tool_name.split("_", 1)
        if len(parts) == 2:
            server, function = parts
            grouped[server].append(function)

    # Print header
    print("📋 Available MCP Tools (Syntropy Aggregator)")
    print("=" * 60)
    print()
    print("⚠️  Naming Pattern: mcp__syntropy__syntropy_{server}_{function}")
    print("⚠️  Permissions show: mcp__syntropy_{server}_{function}")
    print("⚠️  Actual callable: mcp__syntropy__syntropy_{server}_{function}")
    print()

    # Print tools by server
    for server in sorted(grouped.keys()):
        print(f"## {server.capitalize()}")
        for func in grouped[server]:
            print(f"  - {func}")
        print()

    print("=" * 60)
    print(f"Total: {len(mcp_tools)} MCP tools available")

    return 0

if __name__ == "__main__":
    exit(main())
