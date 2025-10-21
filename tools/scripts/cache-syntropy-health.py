#!/usr/bin/env python3
"""Cache Syntropy MCP healthcheck results for fast startup hook access.

This script is called BY Claude Code (which has MCP access) to cache healthcheck results.
The session startup hook then reads from this cache for fast, reliable status display.

Usage:
    Called automatically by Claude Code when mcp__syntropy__syntropy_healthcheck is invoked.
    Cache written to: .ce/syntropy-health-cache.json
    TTL: 5 minutes (stale cache triggers warning, not failure)
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess


def get_git_root():
    """Get git repository root."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout.strip() if result.returncode == 0 else str(Path.cwd())


def write_cache(data: dict) -> None:
    """Write healthcheck results to cache file."""
    git_root = Path(get_git_root())
    cache_dir = git_root / ".ce"
    cache_dir.mkdir(exist_ok=True)

    cache_file = cache_dir / "syntropy-health-cache.json"

    # Add cache metadata
    cache_data = {
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "data": data
    }

    with open(cache_file, "w") as f:
        json.dump(cache_data, f, indent=2)

    print(f"✅ Cached Syntropy health to: {cache_file}")


def main():
    """
    Expects healthcheck JSON on stdin (piped from Claude Code MCP call).
    Writes cache file for fast session startup access.
    """
    if sys.stdin.isatty():
        print("❌ Error: Expected healthcheck JSON on stdin")
        print("🔧 Usage: echo '{...healthcheck json...}' | python cache-syntropy-health.py")
        return 1

    try:
        # Read healthcheck data from stdin
        data = json.load(sys.stdin)

        # Validate structure
        if "servers" not in data or "summary" not in data:
            print("❌ Error: Invalid healthcheck data (missing servers/summary)")
            return 1

        # Write to cache
        write_cache(data)
        return 0

    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON input: {e}")
        return 1
    except Exception as e:
        print(f"❌ Error: Failed to cache healthcheck: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
