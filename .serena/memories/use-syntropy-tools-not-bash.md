---
type: regular
category: documentation
tags: [syntropy, tools, guidelines]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Use Syntropy MCP Tools Instead of Bash Commands

## Core Principle

**ALWAYS prefer Syntropy MCP tools over bash commands** - they provide the same functionality with better error handling, permissions management, and context awareness.

## Common Replacements

### File Operations

❌ **DON'T USE BASH:**
```bash
cat file.txt
ls -la directory/
find . -name "*.py"
mkdir new_dir
mv file1.txt file2.txt
```

✅ **USE SYNTROPY:**
```python
# Read file
mcp__syntropy_filesystem_read_text_file(path="file.txt")

# List directory
mcp__syntropy_filesystem_list_directory(path="directory/")

# Search files
mcp__syntropy_filesystem_search_files(pattern="*.py")

# Get directory tree
mcp__syntropy_filesystem_directory_tree(path=".", max_depth=3)

# Get file info
mcp__syntropy_filesystem_get_file_info(path="file.txt")
```

### Git Operations

❌ **DON'T USE BASH:**
```bash
git status
git diff
git log -5
git add file.txt
git commit -m "message"
```

✅ **USE SYNTROPY:**
```python
# Git status
mcp__syntropy_git_git_status(repo_path="/path/to/repo")

# Git diff
mcp__syntropy_git_git_diff(repo_path="/path/to/repo", staged=False)

# Git log
mcp__syntropy_git_git_log(repo_path="/path/to/repo", max_count=5)

# Git add
mcp__syntropy_git_git_add(repo_path="/path/to/repo", paths=["file.txt"])

# Git commit
mcp__syntropy_git_git_commit(repo_path="/path/to/repo", message="message")
```

### Code Navigation

❌ **DON'T USE BASH:**
```bash
grep -r "function_name" .
find . -name "class_name"
```

✅ **USE SYNTROPY:**
```python
# Find symbol by name
mcp__syntropy_serena_find_symbol(name_path="ClassName.method_name", include_body=True)

# Search for pattern
mcp__syntropy_serena_search_for_pattern(pattern="def function_.*", file_glob="**/*.py")

# Get file structure
mcp__syntropy_serena_get_symbols_overview(relative_path="module/file.py")

# Find references
mcp__syntropy_serena_find_referencing_symbols(name_path="function_name")
```

## Why Syntropy Tools Are Better

1. **Permissions**: Already approved in settings.local.json
2. **Error Handling**: Consistent error responses with context
3. **Type Safety**: Structured JSON responses vs parsing text
4. **Performance**: Optimized for Claude Code integration
5. **Cross-Platform**: Works identically on macOS/Linux/Windows
6. **No Bash Approval**: Bash commands require explicit permission patterns

## Allowed Bash Commands (Exceptions)

**ONLY use bash for these specific patterns:**

1. **UV package management**:
   - `uv run`, `uv add`, `uvx`, `uv run pytest`

2. **Environment variables**:
   - `env`, `export`

3. **Git operations covered by permissions**:
   - `git diff-tree` (specific case)

4. **System utilities**:
   - `brew install` (package installation)
   - `ps` (process listing)

5. **MCP auth reset**:
   - `rm -rf ~/.mcp-auth` (specific permission)

6. **Text utilities** (when no alternative):
   - `head`, `tail`, `cat`, `grep`, `wc`, `echo`

## Migration Examples

### Example 1: Check Git Status

**Before:**
```bash
cd /path/to/repo && git status
```

**After:**
```python
mcp__syntropy_git_git_status(repo_path="/path/to/repo")
```

### Example 2: List Directory

**Before:**
```bash
ls -la /path/to/dir
```

**After:**
```python
mcp__syntropy_filesystem_list_directory(path="/path/to/dir")
```

### Example 3: Find Code Pattern

**Before:**
```bash
grep -r "def process_" tools/ce/
```

**After:**
```python
mcp__syntropy_serena_search_for_pattern(
    pattern="def process_",
    file_glob="tools/ce/**/*.py"
)
```

### Example 4: Read File

**Before:**
```bash
cat /path/to/file.txt
```

**After:**
```python
mcp__syntropy_filesystem_read_text_file(path="/path/to/file.txt")
```

## Implementation Priority

**For PRP-27 follow-up work:**

1. Replace all `ls` with `mcp__syntropy_filesystem_list_directory`
2. Replace all `cat` with `mcp__syntropy_filesystem_read_text_file`
3. Replace all `git status/diff/log` with Syntropy git tools
4. Replace all `grep -r` with Serena search tools
5. Keep only approved bash patterns (uv, env, specific git, brew)

## Benefits Demonstrated in PRP-27

The cache-based architecture for Syntropy status hook **proves this pattern works**:

- Fast execution (~200ms vs 2-3s for bash equivalents)
- Structured JSON responses (no parsing needed)
- Consistent error handling (no shell exit code guessing)
- Works in hook context (bash has permission issues)

## Related

- **PRP**: PRPs/executed/PRP-27-syntropy-status-hook.md
- **Policy**: CLAUDE.md (project guidelines)
- **Permissions**: .claude/settings.local.json (lines 31-90)
- **Tool Reference**: CLAUDE.md "Syntropy Tools Reference" section
