"""Permission validation utility - replaces jq/grep for settings checks."""
import json
from pathlib import Path
from typing import Dict, List


def load_settings() -> Dict:
    """Load .claude/settings.local.json

    Returns:
        Dict with permissions configuration

    Raises:
        FileNotFoundError: If settings file doesn't exist
        json.JSONDecodeError: If settings file is malformed
    """
    settings_path = Path(__file__).parent.parent.parent / ".claude/settings.local.json"

    if not settings_path.exists():
        raise FileNotFoundError(
            f"Settings file not found: {settings_path}\n"
            "🔧 Troubleshooting: Ensure .claude/settings.local.json exists"
        )

    return json.loads(settings_path.read_text())


def count_permissions() -> Dict[str, int]:
    """Count allow/deny tools.

    Returns:
        Dict with 'allow' and 'deny' counts
    """
    settings = load_settings()
    return {
        "allow": len(settings["permissions"]["allow"]),
        "deny": len(settings["permissions"]["deny"])
    }


def search_tool(pattern: str, permission_type: str = "allow") -> List[str]:
    """Search for tools matching pattern in allow/deny list.

    Args:
        pattern: String pattern to search for (case-sensitive)
        permission_type: Either "allow" or "deny"

    Returns:
        List of matching tool names
    """
    settings = load_settings()
    tools = settings["permissions"][permission_type]
    return [t for t in tools if pattern in t]


def verify_tool_exists(tool_name: str) -> Dict[str, bool]:
    """Check if tool exists in allow or deny list.

    Args:
        tool_name: Exact tool name to search for

    Returns:
        Dict with 'in_allow' and 'in_deny' boolean flags
    """
    settings = load_settings()
    return {
        "in_allow": tool_name in settings["permissions"]["allow"],
        "in_deny": tool_name in settings["permissions"]["deny"]
    }


def categorize_tools() -> Dict[str, List[str]]:
    """Group allowed tools by category.

    Returns:
        Dict mapping category names to lists of tool names
    """
    settings = load_settings()
    allowed = settings["permissions"]["allow"]

    categories = {
        "bash": [t for t in allowed if t.startswith("Bash(")],
        "serena": [t for t in allowed if t.startswith("mcp__serena__")],
        "filesystem": [t for t in allowed if t.startswith("mcp__filesystem__")],
        "git": [t for t in allowed if t.startswith("mcp__git__")],
        "context7": [t for t in allowed if t.startswith("mcp__context7__")],
        "sequential": [t for t in allowed if t.startswith("mcp__sequential-thinking__")],
        "linear": [t for t in allowed if t.startswith("mcp__linear-server__")],
        "repomix": [t for t in allowed if t.startswith("mcp__repomix__")],
        "special": [t for t in allowed if t.startswith(("Read(", "WebFetch(", "SlashCommand("))]
    }

    return categories


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python validate_permissions.py [count|search|verify|categorize]")
        print("\nCommands:")
        print("  count                    - Show allow/deny counts")
        print("  search <pattern> [type]  - Search for pattern in allow/deny list")
        print("  verify <tool_name>       - Check if tool is in allow/deny")
        print("  categorize               - Show tools grouped by category")
        sys.exit(1)

    action = sys.argv[1]

    try:
        if action == "count":
            counts = count_permissions()
            print(f"Allow: {counts['allow']}")
            print(f"Deny: {counts['deny']}")

        elif action == "search" and len(sys.argv) >= 3:
            pattern = sys.argv[2]
            perm_type = sys.argv[3] if len(sys.argv) >= 4 else "allow"
            matches = search_tool(pattern, perm_type)
            if matches:
                for match in matches:
                    print(match)
            else:
                print(f"No matches found for pattern '{pattern}' in {perm_type} list")

        elif action == "verify" and len(sys.argv) >= 3:
            tool = sys.argv[2]
            result = verify_tool_exists(tool)
            print(f"In allow: {result['in_allow']}")
            print(f"In deny: {result['in_deny']}")

        elif action == "categorize":
            cats = categorize_tools()
            total = sum(len(tools) for tools in cats.values())
            print(f"Total allowed tools: {total}\n")
            for cat, tools in cats.items():
                print(f"{cat.upper()} ({len(tools)}):")
                for tool in sorted(tools):
                    print(f"  - {tool}")
                print()

        else:
            print(f"Unknown action: {action}")
            print("Use: count, search, verify, or categorize")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
