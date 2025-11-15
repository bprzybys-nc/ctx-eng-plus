#!/bin/bash
set -e

echo "🔨 Regenerating CE framework packages..."

# Regenerate packages
npx repomix --config .ce/repomix-profile-workflow.json
npx repomix --config .ce/repomix-profile-infrastructure.json

echo "✅ Packages regenerated"

# Validate packages were built to syntropy-mcp
SYNTROPY_MCP_DIR="../syntropy-mcp"
BOILERPLATE_DIR="$SYNTROPY_MCP_DIR/boilerplate/ce-framework"

if [ ! -d "$SYNTROPY_MCP_DIR" ]; then
  echo "⚠️  Syntropy MCP directory not found: $SYNTROPY_MCP_DIR"
  echo "   Packages built but not distributed (development mode)"
  exit 0
fi

if [ ! -f "$BOILERPLATE_DIR/ce-infrastructure.xml" ] || [ ! -f "$BOILERPLATE_DIR/ce-workflow-docs.xml" ]; then
  echo "❌ Packages not found in syntropy-mcp boilerplate"
  echo "   Expected: $BOILERPLATE_DIR/*.xml"
  exit 1
fi

# Validate package integrity
WORKFLOW_SIZE=$(wc -c < "$BOILERPLATE_DIR/ce-workflow-docs.xml")
INFRA_SIZE=$(wc -c < "$BOILERPLATE_DIR/ce-infrastructure.xml")
TOTAL_SIZE=$((WORKFLOW_SIZE + INFRA_SIZE))

echo "📊 Package sizes:"
echo "  Workflow: $WORKFLOW_SIZE bytes"
echo "  Infrastructure: $INFRA_SIZE bytes"
echo "  Total: $TOTAL_SIZE bytes"

echo "✅ Packages built to syntropy-mcp boilerplate"
