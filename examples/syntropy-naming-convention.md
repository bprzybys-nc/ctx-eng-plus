# Syntropy MCP Tool Naming - Quick Guide

## The Format (Copy This)

```
mcp__syntropy__<server>_<tool>
```

**Double underscores** after `mcp` and `syntropy`, **single underscore** between server and tool.

---

## Quick Examples

### Serena (Code Intelligence)
```
mcp__syntropy__serena_find_symbol
mcp__syntropy__serena_get_symbols_overview
mcp__syntropy__serena_search_for_pattern
```

### Sequential Thinking (Complex Reasoning)
```
mcp__syntropy__thinking_sequentialthinking
```

### Context7 (Library Docs)
```
mcp__syntropy__context7_get_library_docs
mcp__syntropy__context7_resolve_library_id
```

### Linear (Project Management)
```
mcp__syntropy__linear_create_issue
mcp__syntropy__linear_get_issue
mcp__syntropy__linear_update_issue
```

### Filesystem (File Operations)
```
mcp__syntropy__filesystem_read_file
mcp__syntropy__filesystem_write_file
mcp__syntropy__filesystem_list_directory
```

### Git (Version Control)
```
mcp__syntropy__git_git_status
mcp__syntropy__git_git_diff
mcp__syntropy__git_git_commit
```

---

## Where to Use This Format

### 1. Claude Code Settings (`.claude/settings.local.json`)

```json
{
  "allow": [
    "mcp__syntropy__serena_find_symbol",
    "mcp__syntropy__thinking_sequentialthinking"
  ],
  "deny": [
    "mcp__syntropy__filesystem_write_file"
  ]
}
```

### 2. Documentation (CLAUDE.md, READMEs, PRPs)

```markdown
Use `mcp__syntropy__serena_find_symbol` to locate code symbols.

Call `mcp__syntropy__thinking_sequentialthinking` for complex reasoning.
```

### 3. Serena Memories (`.serena/memories/*.md`)

```markdown
**Tool**: `mcp__syntropy__serena_find_symbol`
**Purpose**: Find symbol definitions in codebase
```

### 4. Commands (`.claude/commands/*.md`)

```markdown
Call the following tools:
- `mcp__syntropy__serena_activate_project`
- `mcp__syntropy__serena_get_symbols_overview`
```

---

## Common Mistakes

| ❌ Wrong | ✅ Right |
|---------|---------|
| `mcp__syntropy_serena_find_symbol` (single `_`) | `mcp__syntropy__serena_find_symbol` (double `__`) |
| `syntropy__serena_find_symbol` (missing `mcp`) | `mcp__syntropy__serena_find_symbol` |
| `mcp__serena__find_symbol` (missing `syntropy`) | `mcp__syntropy__serena_find_symbol` |
| `serena_find_symbol` (missing prefix) | `mcp__syntropy__serena_find_symbol` |

---

## Available Servers

| Server | Purpose | Example Tool |
|--------|---------|--------------|
| **serena** | Code intelligence | `mcp__syntropy__serena_find_symbol` |
| **thinking** | Complex reasoning | `mcp__syntropy__thinking_sequentialthinking` |
| **context7** | Library documentation | `mcp__syntropy__context7_get_library_docs` |
| **linear** | Project management | `mcp__syntropy__linear_create_issue` |
| **filesystem** | File operations | `mcp__syntropy__filesystem_read_file` |
| **git** | Version control | `mcp__syntropy__git_git_status` |
| **repomix** | Codebase packaging | `mcp__syntropy__repomix_pack_codebase` |
| **github** | GitHub operations | `mcp__syntropy__github_create_issue` |
| **perplexity** | Web search | `mcp__syntropy__perplexity_ask` |

---

## How to Find Available Tools

### Option 1: Read Tool Index
```bash
cat syntropy-mcp/tool-index.md
```

### Option 2: Health Check
```bash
/syntropy-health
```

### Option 3: Check Permissions
```bash
cat .claude/settings.local.json | grep "mcp__syntropy"
```

---

## Naming Pattern Breakdown

```
mcp__syntropy__thinking_sequentialthinking
│   │        │       │  └─ Tool name
│   │        │       └──── Separator (single underscore)
│   │        └────────── Server name
│   └───────────────────── Separator (double underscore)
└─────────────────────────── MCP prefix (double underscore)
```

---

## When to Use Which Tool

### Code Navigation & Intelligence
→ Use **serena** tools
```
mcp__syntropy__serena_find_symbol
mcp__syntropy__serena_get_symbols_overview
```

### Complex Problem Solving
→ Use **thinking** tool
```
mcp__syntropy__thinking_sequentialthinking
```

### Library Documentation Lookup
→ Use **context7** tools
```
mcp__syntropy__context7_get_library_docs
```

### Project Management
→ Use **linear** tools
```
mcp__syntropy__linear_create_issue
mcp__syntropy__linear_list_issues
```

### File Operations
→ Use native Claude Code tools (Read, Write, Edit, Glob, Grep)
- **Don't use**: `mcp__syntropy__filesystem_*` tools (denied by default)

### Version Control
→ Use `Bash(git:*)` commands
- **Don't use**: `mcp__syntropy__git_*` tools (denied by default)

---

## Tool State Management

**Location**: `~/.syntropy/tool-state.json`

**View current state**:
```bash
cat ~/.syntropy/tool-state.json
```

**Example state**:
```json
{
  "enabled": [
    "mcp__syntropy__serena_find_symbol"
  ],
  "disabled": [
    "mcp__syntropy__filesystem_read_file",
    "mcp__syntropy__git_git_status"
  ]
}
```

**Sync with settings**:
```bash
/sync-with-syntropy
```

---

## Troubleshooting

### Problem: Tool not found

**Solution**: Check the naming format

```bash
# Wrong (will fail)
mcp__syntropy_thinking_sequentialthinking

# Right (will work)
mcp__syntropy__thinking_sequentialthinking
```

### Problem: Permission denied

**Solution**: Check `.claude/settings.local.json`

```bash
# Add to "allow" array
grep "thinking" .claude/settings.local.json
```

### Problem: MCP server not connected

**Solution**: Reconnect
```bash
/mcp
```

### Problem: Tool disabled

**Solution**: Enable in tool state
```bash
# Check state
cat ~/.syntropy/tool-state.json

# Sync
/sync-with-syntropy
```

---

## Complete Reference

For full technical details, see:
- **Naming Convention Spec**: `syntropy-mcp/NAMING-CONVENTION.md`
- **Tool Index**: `syntropy-mcp/tool-index.md`
- **Syntropy README**: `syntropy-mcp/README.md`
