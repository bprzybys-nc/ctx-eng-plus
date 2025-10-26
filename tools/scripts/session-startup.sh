#!/bin/bash
# Session startup checks: drift + syntropy status + mcp tools
# Runs on SessionStart (startup, resume, clear)
# Tolerates failures gracefully, prints diagnostics

# Remove set -e to prevent hook failures during early session init
set +e  # Continue on errors (graceful degradation)
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$PROJECT_ROOT/tools"

# Run checks in sequence with error handling
echo ""

# 1. Context drift (fast, ~1-2s)
echo "Checking context drift..."
if uv run ce context health --json 2>/dev/null | \
   jq -r '(.drift_score | . * 100 | round / 100) as $rounded |
          if .drift_score > 30 then "⚠️ HIGH DRIFT: " + ($rounded | tostring) + "% - Run: ce context sync"
          elif .drift_score > 10 then "⚠️ Moderate drift: " + ($rounded | tostring) + "%"
          else "✅ Context healthy: " + ($rounded | tostring) + "%"
          end' 2>/dev/null; then
    :  # Success
else
    echo "⚠️ Drift check skipped (ce not available)"
fi

echo ""

# 2. Syntropy MCP status (real healthcheck, ~2-3s)
echo "Checking Syntropy MCP servers..."
if uv run python scripts/syntropy-status.py 2>/dev/null; then
    :  # Success
else
    echo "⚠️ Syntropy healthcheck unavailable"
    echo "🔧 Try: rm -rf ~/.mcp-auth && restart"
fi

echo ""

# 3. Available MCP tools list (fast, ~500ms)
echo "Available tools:"
if uv run python scripts/list-mcp-tools.py 2>/dev/null; then
    :  # Success
else
    echo "⚠️ MCP tools list unavailable"
fi

echo ""
