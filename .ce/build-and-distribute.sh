#!/bin/bash
set -e

echo "🔨 Regenerating CE framework packages..."

# Regenerate packages
npx repomix --config .ce/repomix-profile-workflow.json
npx repomix --config .ce/repomix-profile-infrastructure.json

echo "✅ Packages regenerated"

# Validate package integrity
WORKFLOW_SIZE=$(wc -c < ce-32/builds/ce-workflow-docs.xml)
INFRA_SIZE=$(wc -c < ce-32/builds/ce-infrastructure.xml)
TOTAL_SIZE=$((WORKFLOW_SIZE + INFRA_SIZE))

echo "📊 Package sizes:"
echo "  Workflow: $WORKFLOW_SIZE bytes"
echo "  Infrastructure: $INFRA_SIZE bytes"
echo "  Total: $TOTAL_SIZE bytes"

# Copy to syntropy-mcp boilerplate (optional)
SYNTROPY_MCP_DIR="../syntropy-mcp"
BOILERPLATE_DIR="$SYNTROPY_MCP_DIR/boilerplate/ce-framework"

if [ ! -d "$SYNTROPY_MCP_DIR" ]; then
  echo "⚠️  Syntropy MCP directory not found: $SYNTROPY_MCP_DIR"
  echo "   Skipping distribution step (packages built successfully)"
  exit 0
fi

mkdir -p "$BOILERPLATE_DIR"
cp ce-32/builds/ce-workflow-docs.xml "$BOILERPLATE_DIR/"
cp ce-32/builds/ce-infrastructure.xml "$BOILERPLATE_DIR/"

echo "✅ Packages distributed to syntropy-mcp"
