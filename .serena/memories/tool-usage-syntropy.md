---
type: regular
category: documentation
tags: [syntropy, mcp, tools]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Syntropy MCP Tool Usage - Updated Reference

**Purpose**: Fast agent tool selection using Syntropy MCP aggregation layer

**Target Audience**: AI agents working with Context Engineering codebase

**Last Updated**: 2025-10-20

**Status**: ✅ ACTIVE - All legacy tools now routed through Syntropy unified interface

---

## Overview: Syntropy Tool Aggregation

**What changed**: All MCP tools now route through Syntropy MCP server with unified interface

**Permissions Format**: `mcp__syntropy__<server>_<tool>` (for settings.local.json)
**Actual Callable**: `mcp__syntropy___<server>__<tool>` (double underscores between components)

**Examples**:
- `mcp__syntropy__serena_find_symbol` (was: `mcp__serena__find_symbol`)
- `mcp__syntropy__filesystem_read_text_file` (was: `mcp__filesystem__read_text_file`)
- `mcp__syntropy__git_git_status` (was: `mcp__git__git_status`)

**Benefit**: Single MCP server managing 6 underlying servers with connection pooling and lifecycle management

---

## Code Navigation & Analysis

### Find function/class definition

**USE**: `mcp__syntropy__serena_find_symbol`

```python
# Find function by name
find_symbol(name_path="authenticate_user", include_body=True)

# Find method in class
find_symbol(name_path="UserAuth/validate", include_body=True)
```

**When**: You know the symbol name and want to see its implementation

### Understand file structure

**USE**: `mcp__syntropy__serena_get_symbols_overview`

```python
# Get top-level overview
get_symbols_overview(path="src/auth.py")
```

**When**: First time exploring a file, want to see all classes/functions

### Search for pattern in codebase

**USE**: `mcp__syntropy__serena_search_for_pattern`

```python
# Find async functions
search_for_pattern(pattern="async def.*authenticate", path="src/")

# Find specific error handling
search_for_pattern(pattern="except.*ValueError", path="src/")
```

**When**: Searching for code patterns, not specific symbol names

### Find all usages of function

**USE**: `mcp__syntropy__serena_find_referencing_symbols`

```python
# Find everywhere validate_token is called
find_referencing_symbols(name_path="validate_token", path="src/auth.py")
```

**When**: Understanding dependencies, impact analysis before changes

---

## File Operations

### Read file contents

**USE**:
- `mcp__syntropy__filesystem_read_text_file` - For config files, markdown, non-code
- `mcp__syntropy__serena_read_file` - For Python/code files (indexed by LSP)

```python
# Read config file
read_text_file(path=".ce/tool-inventory.yml")

# Read Python module
read_file(relative_path="ce/core.py")
```

**When**: Need to read entire file contents

### List directory contents

**USE**: `mcp__syntropy__filesystem_list_directory`

```python
list_directory(path="examples/")
```

**When**: Exploring directory structure, finding files

### Find files by pattern

**USE**: `mcp__syntropy__filesystem_search_files`

```python
# Find all test files
search_files(path="tests", pattern="test_*.py")
```

**When**: Finding files matching specific naming pattern

### Edit file with line-based changes

**USE**: `mcp__syntropy__filesystem_edit_file`

```python
edit_file(
    path="ce/config.py",
    edits=[{
        "oldText": "debug = False",
        "newText": "debug = True"
    }]
)
```

**When**: Making precise line-by-line edits to existing files

### Write new file

**USE**: `mcp__syntropy__serena_create_text_file`

```python
create_text_file(
    relative_path="new_module.py",
    body="# New module\ndef hello():\n    pass"
)
```

**When**: Creating new files in the project

---

## Version Control

### Check git status

**USE**: `mcp__syntropy__git_git_status`

```python
git_status(repo_path=".")
```

**When**: Check working directory status before commits

### View recent changes

**USE**: `mcp__syntropy__git_git_diff`

```python
git_diff(repo_path=".", target="HEAD")
```

**When**: Review changes before committing

### See commit history

**USE**: `mcp__syntropy__git_git_log`

```python
git_log(repo_path=".", max_count=10)
```

**When**: Understanding recent commits, finding commit messages

### Stage and commit changes

**USE**: `mcp__syntropy__git_git_add` + `mcp__syntropy__git_git_commit`

```python
# Stage files
git_add(repo_path=".", files=["ce/core.py", "tests/test_core.py"])

# Commit with message
git_commit(repo_path=".", message="feat: add new feature")
```

**When**: Creating commits during implementation

---

## Documentation Lookup

### Get library documentation

**USE**: `mcp__syntropy__context7_resolve_library_id` + `mcp__syntropy__context7_get_library_docs`

```python
# Step 1: Resolve library ID
lib_id = mcp__syntropy__context7_resolve_library_id(libraryName="pytest")

# Step 2: Get docs
docs = mcp__syntropy__context7_get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="fixtures"
)
```

**When**: Need external library documentation, API references

---

## Complex Reasoning

### Multi-step problem decomposition

**USE**: `mcp__syntropy__thinking_sequentialthinking`

```python
sequentialthinking(
    thought="First, I need to understand the authentication flow",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)
```

**When**: Complex problems requiring step-by-step reasoning

---

## Codebase Packaging

### Pack entire codebase for AI

**USE**: `mcp__syntropy__repomix_pack_codebase`

```python
pack_codebase(
    output="codebase.txt"
)
```

**When**: Need to package entire codebase for analysis, sharing with other AI systems

---

## Project Management

### Create/update Linear issue

**USE**: `mcp__syntropy__linear_create_issue` / `mcp__syntropy__linear_update_issue`

```python
# Create issue
create_issue(
    team="Blaise78",
    title="PRP-18: Tool Configuration",
    description="Optimize tool usage...",
    assignee="blazej.przybyszewski@gmail.com"
)

# Update issue
update_issue(
    issue_number="BLA-123",
    state="in_progress"
)
```

**When**: Creating tasks, updating issue status

### List issues

**USE**: `mcp__syntropy__linear_list_issues`

```python
list_issues(
    team="Blaise78",
    assignee="me",
    state="in_progress"
)
```

**When**: Finding assigned work, checking project status

---

## Syntropy-Specific Benefits

### Single Connection Point

Instead of managing 6 separate MCP server connections:
- ✅ Single Syntropy server manages all connections
- ✅ Connection pooling reduces overhead
- ✅ Lazy initialization spawns servers on first use
- ✅ Automatic cleanup on session end

### Unified Error Handling

All tool calls include:
- ✅ Structured logging with timing
- ✅ Clear error messages with troubleshooting
- ✅ Consistent exception handling across all servers

### Extensible Architecture

New MCP servers can be added by:
1. Adding server config to `/syntropy-mcp/servers.json`
2. Updating tool list in `/syntropy-mcp/src/index.ts`
3. No Claude Code configuration changes needed!

---

## Tool Selection Decision Tree

```
Need to work with code?
├─ Know symbol name? → mcp__syntropy__serena_find_symbol
├─ Exploring file? → mcp__syntropy__serena_get_symbols_overview
├─ Pattern search? → mcp__syntropy__serena_search_for_pattern
└─ Find usages? → mcp__syntropy__serena_find_referencing_symbols

Need to read file?
├─ Code file? → mcp__syntropy__serena_read_file
└─ Config/text? → mcp__syntropy__filesystem_read_text_file

Need to write/edit?
├─ Create file? → mcp__syntropy__serena_create_text_file
└─ Edit existing? → mcp__syntropy__filesystem_edit_file

Need git operation?
└─ Use mcp__syntropy__git_* tools (status, diff, log, add, commit)

Need external docs?
└─ Use mcp__syntropy__context7_* tools

Need complex reasoning?
└─ Use mcp__syntropy__thinking_sequentialthinking

Need project management?
└─ Use mcp__syntropy__linear_* tools

Need codebase packaging?
└─ Use mcp__syntropy__repomix_pack_codebase
```

---

## Migration from Legacy Tools

| Old Tool | New Tool (Syntropy) | Notes |
|----------|-------------------|-------|
| `mcp__serena__find_symbol` | `mcp__syntropy__serena_find_symbol` | Same functionality, unified MCP |
| `mcp__filesystem__read_text_file` | `mcp__syntropy__filesystem_read_text_file` | Same functionality, unified MCP |
| `mcp__git__git_status` | `mcp__syntropy__git_git_status` | Same functionality, unified MCP |
| `mcp__context7__get_library_docs` | `mcp__syntropy__context7_get_library_docs` | Same functionality, unified MCP |
| `mcp__sequential-thinking__sequentialthinking` | `mcp__syntropy__thinking_sequentialthinking` | Same functionality, unified MCP |
| `mcp__linear-server__create_issue` | `mcp__syntropy__linear_create_issue` | Same functionality, unified MCP |
| `mcp__repomix__pack_codebase` | `mcp__syntropy__repomix_pack_codebase` | Same functionality, unified MCP |

**All tools now route through Syntropy MCP server for unified management and connection pooling.**

---

## Performance & Reliability

### Connection Pooling Benefits
- First call: ~1-2 seconds (server spawn)
- Subsequent calls: <50ms (connection reused)
- Automatic cleanup on session end
- No resource leaks

### Error Handling
- All errors include troubleshooting guidance
- Graceful fallback on connection failure
- Structured logging for debugging
- Clear error messages with context

---

## Current Permission Configuration

**Status**: Updated for Syntropy MCP (2025-10-20)

### Allow List - Syntropy Tools
```
mcp__syntropy__serena_*
mcp__syntropy__filesystem_*
mcp__syntropy__git_*
mcp__syntropy__context7_*
mcp__syntropy__thinking_*
mcp__syntropy__linear_*
mcp__syntropy__repomix_*
```

All legacy `mcp__*` permissions replaced with Syntropy unified interface.

---

## Support & Troubleshooting

### Tool Not Found
- Restart Claude Code to refresh tool list
- Check Syntropy MCP server is connected (visible in `/mcp` menu)
- Verify tool name format: `mcp__syntropy__<server>_<tool>` (permissions)

### Connection Timeout
- First connection may take 1-2 seconds (server spawn)
- Subsequent calls should be <50ms
- If timeout persists, check server configuration in `/syntropy-mcp/servers.json`

### Server Configuration
- Located at: `/Users/bprzybysz/nc-src/ctx-eng-plus/syntropy-mcp/servers.json`
- Spawn command format: `npx` or `uvx`
- All servers use lazy initialization (spawn on first use)
