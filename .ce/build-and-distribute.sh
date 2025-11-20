#!/bin/bash
set -e

echo "🔨 Regenerating CE framework packages..."

# Regenerate packages
npx repomix --config .ce/repomix-profile-workflow.json
npx repomix --config .ce/repomix-profile-infrastructure.json

# WORKAROUND: Repomix v1.9.1 bug - manually inject missing files
# See: .serena/memories/repomix-glob-pattern-file-permissions-issue.md
echo "🔧 Patching missing files (repomix v1.9.1 bug workaround)..."
python3 .ce/repomix-patch-missing-files.py

echo "✅ Packages regenerated"

# Validate packages were built to syntropy-mcp
SYNTROPY_MCP_DIR="../syntropy-mcp"
BOILERPLATE_DIR="$SYNTROPY_MCP_DIR/boilerplate/ce-framework"

if [ ! -d "$SYNTROPY_MCP_DIR" ]; then
  echo "⚠️  Syntropy MCP directory not found: $SYNTROPY_MCP_DIR"
  echo "   Packages built but not distributed (development mode)"
  exit 0
fi

# Create boilerplate directory if it doesn't exist
mkdir -p "$BOILERPLATE_DIR"

# Copy Python initialization scripts
echo "📦 Distributing Python initialization scripts..."
cp tools/ce/init_project.py "$BOILERPLATE_DIR/"
cp tools/ce/repomix_unpack.py "$BOILERPLATE_DIR/"
echo "✅ Python scripts distributed"

if [ ! -f "$BOILERPLATE_DIR/ce-infrastructure.xml" ] || [ ! -f "$BOILERPLATE_DIR/ce-workflow-docs.xml" ]; then
  echo "❌ Packages not found in syntropy-mcp boilerplate"
  echo "   Expected: $BOILERPLATE_DIR/*.xml"
  exit 1
fi

if [ ! -f "$BOILERPLATE_DIR/init_project.py" ] || [ ! -f "$BOILERPLATE_DIR/repomix_unpack.py" ]; then
  echo "❌ Python scripts not found in syntropy-mcp boilerplate"
  echo "   Expected: $BOILERPLATE_DIR/{init_project.py,repomix_unpack.py}"
  exit 1
fi

# Validate package integrity
WORKFLOW_SIZE=$(wc -c < "$BOILERPLATE_DIR/ce-workflow-docs.xml")
INFRA_SIZE=$(wc -c < "$BOILERPLATE_DIR/ce-infrastructure.xml")
INIT_PY_SIZE=$(wc -c < "$BOILERPLATE_DIR/init_project.py")
REPOMIX_PY_SIZE=$(wc -c < "$BOILERPLATE_DIR/repomix_unpack.py")
TOTAL_SIZE=$((WORKFLOW_SIZE + INFRA_SIZE + INIT_PY_SIZE + REPOMIX_PY_SIZE))

echo "📊 Distribution sizes:"
echo "  Workflow XML: $WORKFLOW_SIZE bytes"
echo "  Infrastructure XML: $INFRA_SIZE bytes"
echo "  init_project.py: $INIT_PY_SIZE bytes"
echo "  repomix_unpack.py: $REPOMIX_PY_SIZE bytes"
echo "  Total: $TOTAL_SIZE bytes"

echo "✅ All resources distributed to syntropy-mcp boilerplate"
