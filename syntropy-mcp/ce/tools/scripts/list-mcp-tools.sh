#!/bin/bash
# List all allowed MCP tools from settings.local.json
# Usage: ./list-mcp-tools.sh

SETTINGS_FILE="$(git rev-parse --show-toplevel 2>/dev/null)/.claude/settings.local.json"

if [[ ! -f "$SETTINGS_FILE" ]]; then
  echo "❌ Settings file not found: $SETTINGS_FILE"
  exit 1
fi

echo "📋 Available MCP Tools (Syntropy Aggregator)"
echo "=============================================="
echo ""
echo "⚠️  Naming Pattern: mcp__syntropy__syntropy_{server}_{function}"
echo "⚠️  Permissions show: mcp__syntropy_{server}_{function}"
echo "⚠️  Actual callable: mcp__syntropy__syntropy_{server}_{function}"
echo ""

# Extract allowed tools, filter MCP tools, group by server
jq -r '.permissions.allow[] | select(startswith("mcp__syntropy_"))' "$SETTINGS_FILE" | \
  sed 's/^mcp__syntropy_//' | \
  sort | \
  awk -F'_' '
  {
    server = $1
    # Extract function name (everything after first underscore)
    func = $0
    sub(/^[^_]+_/, "", func)

    if (last_server != server && last_server != "") {
      print ""
    }

    if (last_server != server) {
      # Capitalize first letter
      display_name = toupper(substr(server, 1, 1)) substr(server, 2)
      print "## " display_name
    }

    print "  - " func
    last_server = server
  }'

# Count total
TOTAL=$(jq -r '.permissions.allow[] | select(startswith("mcp__syntropy_"))' "$SETTINGS_FILE" | wc -l | tr -d ' ')
echo "=============================================="
echo "Total: $TOTAL MCP tools available"
