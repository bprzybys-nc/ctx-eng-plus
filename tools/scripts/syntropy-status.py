#!/usr/bin/env python3
"""Display Syntropy MCP aggregator health status.

Reads from cache file (.ce/syntropy-health-cache.json) written by cache-syntropy-health.py.
Cache is updated by Claude Code calling mcp__syntropy__healthcheck.
"""

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta


def get_git_root():
    """Get git repository root."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False
    )
    return result.stdout.strip() if result.returncode == 0 else str(Path.cwd())


def get_status_emoji(status: str) -> str:
    """Get emoji for server status."""
    return {
        "healthy": "✅",
        "degraded": "⚠️",
        "down": "❌",
    }.get(status, "❓")


def load_cached_health():
    """Load healthcheck from cache file.

    Returns:
        Tuple of (data, is_stale) where is_stale indicates cache age > 5 minutes
    """
    git_root = Path(get_git_root())
    cache_file = git_root / ".ce" / "syntropy-health-cache.json"

    if not cache_file.exists():
        return None, False

    try:
        with open(cache_file) as f:
            cache = json.load(f)

        # Check cache age
        cached_at = datetime.fromisoformat(cache["cached_at"])
        now = datetime.now(timezone.utc)
        age = now - cached_at
        is_stale = age > timedelta(minutes=5)

        return cache["data"], is_stale
    except Exception as e:
        print(f"⚠️ Error reading cache: {e}")
        return None, False


def main():
    """Display Syntropy status from cache.

    Reads from .ce/syntropy-health-cache.json (real MCP healthcheck data).
    If cache missing/stale, prints error with troubleshooting guidance.
    """
    # Try to load from cache
    data, is_stale = load_cached_health()

    if data is None:
        print("❌ Syntropy health cache not found")
        print("🔧 Run this in Claude Code to refresh:")
        print("   Call mcp__syntropy__healthcheck and pipe to cache-syntropy-health.py")
        return 1

    if is_stale:
        print("⚠️ Cache is stale (>5 minutes old)")
        print("🔧 Consider refreshing healthcheck")

    # Header
    print("🔧 Syntropy MCP Status")
    print("=" * 60)

    # Summary
    summary = data.get("summary", {})
    total = summary.get("total", 0)
    healthy = summary.get("healthy", 0)
    degraded = summary.get("degraded", 0)
    down = summary.get("down", 0)

    print(f"Total: {total} | ✅ {healthy} | ⚠️ {degraded} | ❌ {down}")
    print()

    # Server details
    servers = data.get("servers", [])
    if servers:
        print("Servers:")
        for server in servers:
            name = server.get("server", "unknown")
            status = server.get("status", "unknown")
            connected = server.get("connected", False)

            emoji = get_status_emoji(status)
            conn_status = "connected" if connected else "disconnected"

            print(f"  {emoji} {name:15} [{conn_status:12}]")

    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
