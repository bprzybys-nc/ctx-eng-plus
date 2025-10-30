#!/bin/bash
# Shell functions for Context Engineering tools
# Source this file in your ~/.zshrc or ~/.bashrc:
#   source /path/to/project/.ce/shell-functions.sh

# ce-in-tools: Run ce command from anywhere in project
# Automatically detects project root and changes to tools/ directory
#
# Usage:
#   ce-in-tools validate --level all
#   ce-in-tools context health
#   ce-in-tools update-context
#
# This function works from ANY directory within the project:
#   - If in project root: cd tools/ and run
#   - If already in tools/: run directly
#   - If in subdirectory: detect root, then cd tools/
ce-in-tools() {
    local project_root
    project_root=$(git rev-parse --show-toplevel 2>/dev/null)

    if [ -z "$project_root" ]; then
        echo "⚠️  Not in a git repository"
        return 1
    fi

    # Run in subshell to avoid changing user's working directory
    (cd "$project_root/tools" && uv run ce "$@")
}

# Alias for shorter typing
alias cet='ce-in-tools'

# ce-drift: Quick drift score check
ce-drift() {
    ce-in-tools context health --json | jq -r \
        '(.drift_score | . * 100 | round / 100) as $rounded |
         if .drift_score > 30 then
             "🚨 HIGH DRIFT: " + ($rounded | tostring) + "% - Run: ce-in-tools update-context"
         elif .drift_score > 10 then
             "⚠️  Moderate drift: " + ($rounded | tostring) + "%"
         else
             "✅ Context healthy: " + ($rounded | tostring) + "%"
         end'
}
