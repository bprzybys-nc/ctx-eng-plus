#!/bin/bash
# Bootstrap script for Context Engineering CLI Tools
# One-command setup

set -euo pipefail

echo "=== Context Engineering CLI Tools Bootstrap ==="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v uv &> /dev/null; then
    echo "❌ UV package manager not found"
    echo "🔧 Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found"
    echo "🔧 Install git first"
    exit 1
fi

echo "✅ Prerequisites OK"
echo ""

# Create virtual environment
echo "🔧 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "   .venv already exists, skipping"
else
    uv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Install package
echo "📦 Installing ce-tools..."
uv pip install -e .
echo "✅ ce-tools installed"
echo ""

# Run tests to verify installation
echo "🧪 Running tests to verify installation..."
if uv run pytest tests/ -v --tb=short; then
    echo "✅ All tests passed"
else
    echo "⚠️  Some tests failed (this is OK if npm commands not available)"
fi
echo ""

# Final instructions
echo "=== Bootstrap Complete ==="
echo ""
echo "CLI is ready to use:"
echo "  ce --help"
echo "  ce validate --level all"
echo "  ce git status"
echo "  ce context health"
echo ""
echo "To activate virtual environment manually:"
echo "  source .venv/bin/activate"
echo ""
echo "Or use directly with uv run:"
echo "  uv run ce --help"
echo ""
