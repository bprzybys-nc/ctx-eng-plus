#!/usr/bin/env python3
"""Add YAML headers to Serena memory files."""

import os
from pathlib import Path
from datetime import datetime

# Memory file categorization based on content analysis
MEMORY_CATEGORIES = {
    # Documentation memories
    "code-style-conventions.md": ("documentation", ["code-style", "conventions", "standards"]),
    "suggested-commands.md": ("documentation", ["commands", "cli", "reference"]),
    "testing-standards.md": ("documentation", ["testing", "standards", "tdd"]),
    "task-completion-checklist.md": ("documentation", ["checklist", "workflow", "quality"]),
    "tool-usage-syntropy.md": ("documentation", ["syntropy", "mcp", "tools"]),
    "use-syntropy-tools-not-bash.md": ("documentation", ["syntropy", "tools", "guidelines"]),
    "codebase-structure.md": ("architecture", ["structure", "organization", "modules"]),
    "system-model-specification.md": ("architecture", ["system-model", "architecture", "design"]),

    # Pattern memories
    "prp-2-implementation-patterns.md": ("pattern", ["prp", "implementation", "workflow"]),
    "PRP-15-remediation-workflow-implementation.md": ("pattern", ["prp", "remediation", "workflow"]),
    "serena-implementation-verification-pattern.md": ("pattern", ["serena", "verification", "testing"]),
    "syntropy-status-hook-pattern.md": ("pattern", ["syntropy", "hooks", "status"]),
    "linear-issue-creation-pattern.md": ("pattern", ["linear", "issues", "automation"]),

    # Configuration memories
    "prp-structure-initialized.md": ("configuration", ["prp", "structure", "setup"]),
    "serena-mcp-tool-restrictions.md": ("configuration", ["serena", "mcp", "permissions"]),
    "tool-config-optimization-completed.md": ("configuration", ["tools", "optimization", "config"]),
    "prp-backlog-system.md": ("configuration", ["prp", "backlog", "tracking"]),

    # Integration/troubleshooting memories
    "linear-mcp-integration-example.md": ("documentation", ["linear", "mcp", "integration"]),
    "linear-mcp-integration.md": ("documentation", ["linear", "mcp", "setup"]),
    "linear-issue-tracking-integration.md": ("documentation", ["linear", "tracking", "workflow"]),
    "l4-validation-usage.md": ("documentation", ["validation", "testing", "l4"]),

    # Project-specific memories
    "project-overview.md": ("documentation", ["overview", "project", "context"]),
    "cwe78-prp22-newline-escape-issue.md": ("troubleshooting", ["security", "cwe78", "fix"]),
}

def add_yaml_header(file_path: Path) -> None:
    """Add YAML header to memory file."""
    filename = file_path.name

    if filename not in MEMORY_CATEGORIES:
        print(f"⚠️  No category mapping for {filename}")
        return

    category, tags = MEMORY_CATEGORIES[filename]

    # Read existing content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if already has YAML header
    if content.startswith('---'):
        print(f"⏭️  {filename} already has YAML header, skipping")
        return

    # Create YAML header
    timestamp = "2025-11-04T17:30:00Z"
    tags_str = ", ".join(tags)

    yaml_header = f"""---
type: regular
category: {category}
tags: [{tags_str}]
created: "{timestamp}"
updated: "{timestamp}"
---

"""

    # Prepend header
    new_content = yaml_header + content

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"✅ Added header to {filename}")

def main():
    """Process all memory files."""
    memories_dir = Path("/Users/bprzybyszi/nc-src/ctx-eng-plus/.serena/memories")

    # Find all .md files except README.md
    memory_files = sorted([
        f for f in memories_dir.glob("*.md")
        if f.name != "README.md"
    ])

    print(f"Found {len(memory_files)} memory files\n")

    for file_path in memory_files:
        add_yaml_header(file_path)

    print(f"\n✨ Processed {len(memory_files)} files")

if __name__ == "__main__":
    main()
