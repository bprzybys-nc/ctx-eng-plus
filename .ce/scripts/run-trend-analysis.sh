#!/bin/bash

# Trend Analysis Launcher
# Usage: ./run-trend-analysis.sh [--recent N | --all | --recent 5]
#
# Runs trend analysis on batch metrics with recovery after system restart
# Safe to call multiple times - checks for metrics and handles missing files gracefully

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
METRICS_DIR="$PROJECT_ROOT/.ce/completed-batches"
ANALYSIS_SCRIPT="$SCRIPT_DIR/trend-analysis.py"

# Default: analyze last 5 batches
LIMIT=5
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --recent)
            LIMIT="${2:-5}"
            shift 2
            ;;
        --all)
            LIMIT="all"
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            cat << EOF
Trend Analysis Launcher

Usage: $0 [OPTIONS]

Options:
  --recent N      Analyze last N batches (default: 5)
  --all           Analyze all completed batches
  --verbose       Show detailed output
  --help          Show this help message

Examples:
  $0                    # Last 5 batches
  $0 --recent 10        # Last 10 batches
  $0 --all              # All batches since Phase 1
  $0 --recent 5 --verbose

Outputs:
  - Trend report with bottleneck analysis
  - Duration statistics (mean, median, stdev)
  - Token usage and cost trends
  - Phase 2 recommendations (prioritized)

Metrics Location: $METRICS_DIR

For more info, see: .claude/commands/batch-trend-analysis.md
EOF
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if metrics directory exists
if [ ! -d "$METRICS_DIR" ]; then
    echo "⚠️  Metrics directory not found: $METRICS_DIR"
    echo ""
    echo "This is expected if no batches have been executed yet."
    echo "Metrics will be created after running a batch:"
    echo ""
    echo "  /batch-gen-prp PRPs/feature-requests/TEST-PLAN.md"
    echo ""
    exit 1
fi

# Check if analysis script exists
if [ ! -f "$ANALYSIS_SCRIPT" ]; then
    echo "❌ Analysis script not found: $ANALYSIS_SCRIPT"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Make script executable if needed
if [ ! -x "$ANALYSIS_SCRIPT" ]; then
    chmod +x "$ANALYSIS_SCRIPT"
fi

# Run trend analysis with appropriate arguments
cd "$PROJECT_ROOT"

echo "📊 Running trend analysis..."
echo "   Metrics directory: $METRICS_DIR"

if [ "$LIMIT" = "all" ]; then
    echo "   Scope: All completed batches"
    python3 "$ANALYSIS_SCRIPT" --all
else
    echo "   Scope: Last $LIMIT batches"
    python3 "$ANALYSIS_SCRIPT" --recent "$LIMIT"
fi

if [ "$VERBOSE" = true ]; then
    echo ""
    echo "📁 Available metrics:"
    ls -lh "$METRICS_DIR" 2>/dev/null | tail -n +2 || echo "   (none yet)"
fi

echo ""
echo "✅ Trend analysis complete"
