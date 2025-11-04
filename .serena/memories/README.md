# Serena Memories - Memory Type System

**Last Updated**: 2025-11-04
**Version**: CE 1.1

---

## Overview

This directory contains 23 framework memory files that provide context for AI agents working with the Context Engineering codebase. All memories use YAML front matter to categorize and classify content.

## Memory Type System

### Type Classification

All framework memories have a `type` field in their YAML header:

```yaml
---
type: regular
category: documentation
tags: [tag1, tag2, tag3]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---
```

### Type Values

- **`type: regular`**: Standard framework memory (default for all 23 memories in ctx-eng-plus)
- **`type: critical`**: High-priority memory (users manually upgrade during target project initialization)
- **`type: user`**: User-created memory in target projects (added during Phase 2 of INITIALIZATION.md)

### Critical Memories (Upgrade Candidates)

The following 6 memories are typically upgraded to `type: critical` during target project initialization:

1. **code-style-conventions.md** - Core coding standards and conventions
2. **suggested-commands.md** - Essential CLI commands and workflows
3. **task-completion-checklist.md** - Quality gates and completion criteria
4. **testing-standards.md** - Testing philosophy and TDD approach
5. **tool-usage-syntropy.md** - Tool selection reference
6. **use-syntropy-tools-not-bash.md** - Tool usage guidelines

**Note**: In ctx-eng-plus (framework repo), all memories default to `type: regular`. Users manually upgrade to `critical` during target project initialization based on their specific needs.

## Category Taxonomy

### documentation (13 files)
Documentation, guides, how-tos, and reference materials.

**Files**:
- code-style-conventions.md
- suggested-commands.md
- testing-standards.md
- task-completion-checklist.md
- tool-usage-syntropy.md
- use-syntropy-tools-not-bash.md
- linear-mcp-integration-example.md
- linear-mcp-integration.md
- linear-issue-tracking-integration.md
- l4-validation-usage.md
- project-overview.md

### pattern (5 files)
Code patterns, best practices, and workflow templates.

**Files**:
- prp-2-implementation-patterns.md
- PRP-15-remediation-workflow-implementation.md
- serena-implementation-verification-pattern.md
- syntropy-status-hook-pattern.md
- linear-issue-creation-pattern.md

### architecture (2 files)
System design, structure, and architectural specifications.

**Files**:
- codebase-structure.md
- system-model-specification.md

### configuration (4 files)
Setup instructions, configuration management, and system state.

**Files**:
- prp-structure-initialized.md
- serena-mcp-tool-restrictions.md
- tool-config-optimization-completed.md
- prp-backlog-system.md

### troubleshooting (1 file)
Error resolution, debugging guides, and fixes.

**Files**:
- cwe78-prp22-newline-escape-issue.md

## Upgrade Path

### From Regular to Critical

During target project initialization (see `examples/INITIALIZATION.md`), users can upgrade memories to `critical`:

```bash
# Edit memory file YAML header
vim .serena/memories/code-style-conventions.md
```

Change:
```yaml
type: regular
```

To:
```yaml
type: critical
```

### User Memory Creation

When creating user-specific memories in target projects, use:

```yaml
---
type: user
source: target-project
created: "2025-11-04T00:00:00Z"
updated: "2025-11-04T00:00:00Z"
---

[User memory content]
```

## Tags

Tags provide additional context for memory categorization. Common tags include:

- **Tool-related**: `syntropy`, `mcp`, `tools`, `serena`
- **Workflow**: `prp`, `workflow`, `automation`, `validation`
- **Code quality**: `code-style`, `testing`, `standards`, `tdd`
- **Integration**: `linear`, `tracking`, `issues`, `github`
- **Architecture**: `structure`, `architecture`, `design`, `system-model`

## File Count

**Framework memories**: 23 files (all `type: regular` by default)
**Symlinks**: 1 (TOOL-USAGE-GUIDE.md → examples/TOOL-USAGE-GUIDE.md)

## Usage

### Serena MCP Integration

All memories are automatically loaded by Serena MCP when the project root is activated:

```python
# Serena automatically indexes memories on activation
serena_activate(project_root="/Users/bprzybysz/nc-src/ctx-eng-plus")
```

### Memory Queries

Use Serena MCP to search and retrieve memories:

```python
# Read specific memory
serena_read_memory(name="code-style-conventions")

# List all memories
serena_list_memories()

# Search memories by tag
serena_search_memories(tags=["prp", "workflow"])
```

## Maintenance

### Adding New Memories

When creating new framework memories:

1. Create file in `.serena/memories/`
2. Add YAML front matter with `type: regular`
3. Choose appropriate category (documentation/pattern/architecture/configuration/troubleshooting)
4. Add 3-5 relevant tags
5. Update this README.md with file count and category breakdown

### Updating Existing Memories

When modifying memories:

1. Update `updated` timestamp in YAML header
2. Preserve `type` and `category` (unless reclassifying)
3. Add/remove tags as needed
4. Maintain consistent formatting

## See Also

- `examples/INITIALIZATION.md` - Framework initialization guide (includes memory type upgrade workflow)
- `examples/TOOL-USAGE-GUIDE.md` - Tool selection reference
- `CLAUDE.md` - Project-specific guidance
