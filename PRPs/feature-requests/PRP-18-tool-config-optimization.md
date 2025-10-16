# PRP-18: MCP Tool Configuration & Usage Mapping Optimization

```yaml
---
name: "MCP Tool Configuration & Usage Mapping Optimization"
description: "Reduce context overhead 30-50% through granular MCP tool permissions, tool usage mapping guide, and Python-based bash replacements"
prp_id: "PRP-18"
status: "feature-request"
created_date: "2025-01-16T00:00:00Z"
last_updated: "2025-01-16T00:00:00Z"
updated_by: "generate-prp-command"
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
estimated_hours: 25
complexity: "medium"
risk_level: "medium"
dependencies: []
tags: ["optimization", "configuration", "performance", "developer-experience"]
---
```

## 1. FEATURE SUMMARY

### Overview

Optimize tool configuration to reduce context overhead by 30-50% and accelerate agent tool selection through:

1. **Granular MCP tool permissions** - Explicit allow/deny lists at tool function level
2. **Tool usage mapping guide** - Quick reference for agents to select correct tools
3. **Python-based bash replacements** - Efficient alternatives to bash utilities (cat, grep, awk, sed)

### Problem Statement

**Context bloat** (45+ broad permissions):
- Wildcard permissions (`mcp__serena__*`) load ALL tools from MCP servers into context
- 45+ broad permissions in `.claude/settings.local.json`
- No deny list = unused tools consume context space

**Query tree complexity** (100+ tools to evaluate):
- Agent must evaluate 100+ tools for each decision
- No usage guide = trial-and-error tool selection
- Slower decision-making due to large tool inventory

**Bash inefficiency** (34 subprocess calls in ce modules):
- Subprocess overhead for simple text operations (cat, grep, awk)
- 34 Bash/run_cmd usages replaceable with Python
- No shell utilities module for common operations

### Success Metrics

- **Context reduction**: 30-50% (measured in tokens)
- **Query tree simplification**: 60-70% fewer tools to evaluate
- **Bash reduction**: From 45+ permissions to 3 (git, uv only)
- **Performance**: Python utilities 10-50x faster than bash subprocess
- **Agent clarity**: Tool mapping guide eliminates trial-and-error

---

## 2. CONTEXT & RESEARCH

### Current State Analysis

**MCP Tool Usage** (from codebase grep):
- 23 MCP tool calls in `tools/ce/*.py`
- 34 Bash/run_cmd calls in `tools/ce/*.py`
- Current permissions: 45+ entries in `.claude/settings.local.json`

**Current Configuration** (`.claude/settings.local.json`):
```json
{
  "permissions": {
    "allow": [
      "Bash(uv run pytest:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Read(//Users/bprzybysz/nc-src/**)",
      "mcp__sequential-thinking__sequentialthinking",
      "Bash(uv run:*)",
      "mcp__serena__get_symbols_overview",
      "mcp__serena__find_symbol",
      "mcp__serena__search_for_pattern",
      "mcp__serena__list_dir",
      "mcp__serena__activate_project",
      "mcp__serena__read_file",
      // ... 39 more entries
    ],
    "deny": [],  // EMPTY - No efficiency optimization
    "ask": []
  }
}
```

**Issues identified**:
1. No wildcards but still broad scope
2. Empty deny list = all unused tools in context
3. No tool usage guide for agent decision-making
4. Heavy bash usage (34 calls) for simple text ops

### Reference Documentation

**MCP Tool Inventory**:
- `docs/research/10-tooling-configuration.md` - Tool matrix (sections 2.1-2.2)
  - 14 total tools across 4 categories
  - Tier-1 Essential: Serena, Filesystem, Context7, Sequential Thinking, GitHub
- `docs/research/03-mcp-orchestration.md` - MCP command reference (section 4)
  - Serena MCP: 12 commands documented
  - Filesystem MCP: 13 commands documented
  - Git MCP: 11 commands documented

**Existing Patterns**:
- `tools/ce/core.py` - run_cmd() for shell execution
- `tools/ce/mcp_adapter.py` - MCP availability detection pattern
- `tools/ce/execute.py` - Validation loop with subprocess calls

**Python Standard Library**:
- `pathlib.Path` - File operations (`read_text()`, `write_text()`)
- `re` module - Regex matching (grep alternative)
- String methods - `replace()`, `split()` (sed/awk alternatives)

###

 Similar Patterns in Codebase

**MCP Adapter Pattern** (`tools/ce/mcp_adapter.py:1-50`):
```python
def _import_serena_mcp():
    """Import Serena MCP with availability detection."""
    try:
        import mcp.client.stdio  # type: ignore
        return True
    except ImportError:
        return False

# Graceful degradation pattern
if serena_available():
    result = mcp__serena__find_symbol(...)
else:
    result = fallback_implementation(...)
```

**Shell Command Pattern** (`tools/ce/core.py:45-80`):
```python
def run_cmd(cmd: str, timeout: int = 60) -> Dict[str, Any]:
    """Execute shell command with timeout."""
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        timeout=timeout
    )
    return {
        "success": result.returncode == 0,
        "stdout": result.stdout.decode(),
        "stderr": result.stderr.decode()
    }
```

---

## 3. IMPLEMENTATION BLUEPRINT

### Phase 1: MCP Tool Usage Audit (5h)

**Goal**: Identify which MCP tools are actually used vs unused

**Tasks**:
1. Create `.ce/tool-inventory.yml` structure
2. Grep codebase for all `mcp__*` calls
3. Categorize by MCP server (serena, filesystem, git, etc.)
4. Count usage frequency per tool
5. Identify unused tools for deny list

**Validation Command**:
```bash
cd tools && uv run pytest tests/test_tool_inventory.py -v
```

**Files to create/modify**:
- CREATE: `.ce/tool-inventory.yml`
- CREATE: `tools/ce/tool_auditor.py` (audit automation script)
- CREATE: `tools/tests/test_tool_inventory.py`

**Expected output** (`.ce/tool-inventory.yml`):
```yaml
optimization_rationale: "Query tree simplification + context reduction"

audit_date: "2025-01-16"
audit_method: "grep -r 'mcp__' tools/ce/*.py"

mcp_servers:
  serena:
    total_available: 30
    used_in_workflow: 10
    usage_breakdown:
      find_symbol: 12
      get_symbols_overview: 5
      search_for_pattern: 3
      list_dir: 2
      read_file: 1
      # ... 5 more
    unused_in_workflow: 20  # → DENY

  filesystem:
    total_available: 20
    used_in_workflow: 8
    unused_in_workflow: 12

  git:
    total_available: 15
    used_in_workflow: 5
    unused_in_workflow: 10

bash_commands:
  total_usages: 34
  replaceable_with_python: 31  # cat, grep, awk, sed, etc.
  keep_external_tools: 3        # git, uv, pytest

recommendations:
  allow_list_size: 31  # MCP tools
  deny_list_size: 52   # 50 MCP + 11 bash
  context_reduction: "60-70%"
```

---

### Phase 2: Granular Configuration Update (3h)

**Goal**: Replace broad permissions with explicit allow/deny lists

**Tasks**:
1. Backup current `.claude/settings.local.json`
2. Create new allow list (31 MCP tools)
3. Create deny list (50+ unused MCP tools)
4. Add ask list (2 sensitive operations)
5. Remove replaceable bash commands

**Validation Command**:
```bash
cd tools && uv run ce validate --level 1
```

**Files to modify**:
- MODIFY: `.claude/settings.local.json`

**New structure**:
```json
{
  "permissions": {
    "allow": [
      // SERENA (10 tools - based on audit)
      "mcp__serena__find_symbol",
      "mcp__serena__get_symbols_overview",
      "mcp__serena__search_for_pattern",
      "mcp__serena__list_dir",
      "mcp__serena__read_file",
      "mcp__serena__activate_project",
      "mcp__serena__find_referencing_symbols",
      "mcp__serena__insert_after_symbol",
      "mcp__serena__replace_regex",
      "mcp__serena__execute_shell_command",

      // FILESYSTEM (8 tools)
      "mcp__filesystem__read_text_file",
      "mcp__filesystem__list_directory",
      "mcp__filesystem__write_file",
      "mcp__filesystem__edit_file",
      "mcp__filesystem__search_files",
      "mcp__filesystem__directory_tree",
      "mcp__filesystem__get_file_info",
      "mcp__filesystem__list_allowed_directories",

      // GIT (5 tools)
      "mcp__git__git_status",
      "mcp__git__git_diff",
      "mcp__git__git_log",
      "mcp__git__git_add",
      "mcp__git__git_commit",

      // CONTEXT7 (2 tools)
      "mcp__context7__resolve-library-id",
      "mcp__context7__get-library-docs",

      // SEQUENTIAL THINKING (1 tool)
      "mcp__sequential-thinking__sequentialthinking",

      // LINEAR (5 tools)
      "mcp__linear-server__create_issue",
      "mcp__linear-server__get_issue",
      "mcp__linear-server__list_issues",
      "mcp__linear-server__update_issue",
      "mcp__linear-server__list_projects",

      // BASH (3 external tools only)
      "Bash(git:*)",
      "Bash(uv run:*)",
      "Bash(uv add:*)"
    ],

    "deny": [
      // SERENA unused (~20 tools)
      "mcp__serena__delete_memory",
      "mcp__serena__rename_symbol",
      "mcp__serena__create_text_file",
      "mcp__serena__switch_modes",
      "mcp__serena__prepare_for_new_conversation",
      "mcp__serena__write_memory",
      "mcp__serena__check_onboarding_performed",
      "mcp__serena__onboarding",
      "mcp__serena__think_about_collected_information",
      "mcp__serena__think_about_task_adherence",
      "mcp__serena__think_about_whether_you_are_done",

      // FILESYSTEM unused (~12 tools)
      "mcp__filesystem__read_file",
      "mcp__filesystem__read_media_file",
      "mcp__filesystem__read_multiple_files",
      "mcp__filesystem__create_directory",
      "mcp__filesystem__move_file",
      "mcp__filesystem__list_directory_with_sizes",

      // GIT unused (~10 tools)
      "mcp__git__git_branch",
      "mcp__git__git_checkout",
      "mcp__git__git_show",
      "mcp__git__git_create_branch",
      "mcp__git__git_reset",
      "mcp__git__git_diff_staged",
      "mcp__git__git_diff_unstaged",

      // Entire unused MCP servers
      "mcp__github__*",
      "mcp__playwright__*",
      "mcp__perplexity__*",
      "mcp__repomix__*",
      "mcp__ide__*",

      // BASH - Replaceable with Python (11 commands)
      "Bash(cat:*)",
      "Bash(head:*)",
      "Bash(tail:*)",
      "Bash(find:*)",
      "Bash(grep:*)",
      "Bash(wc:*)",
      "Bash(awk:*)",
      "Bash(sed:*)",
      "Bash(echo:*)",
      "Bash(python:*)",
      "Bash(python3:*)"
    ],

    "ask": [
      // Manual confirmation for sensitive ops
      "mcp__git__git_push",
      "mcp__filesystem__delete_file"
    ]
  },
  "hooks": {
    // Keep existing hooks
  }
}
```

---

### Phase 3: Tool Usage Mapping Guide (4h)

**Goal**: Create quick reference guide for agent tool selection

**Tasks**:
1. Create `examples/tool-usage-patterns.md`
2. Document common tasks and which tools to use
3. Add anti-patterns (what NOT to use)
4. Copy to `.serena/memories/tool-usage-guide.md`
5. Update CLAUDE.md to reference guide

**Validation Command**:
```bash
test -f examples/tool-usage-patterns.md && test -f .serena/memories/tool-usage-guide.md && echo "✅ Guide created"
```

**Files to create/modify**:
- CREATE: `examples/tool-usage-patterns.md`
- CREATE: `.serena/memories/tool-usage-guide.md` (copy)
- MODIFY: `CLAUDE.md` (add reference to guide)

**Guide structure** (`examples/tool-usage-patterns.md`):
```markdown
# Tool Usage Patterns - Quick Reference

**Purpose**: Fast agent tool selection without trial-and-error

## Code Navigation & Analysis

### Find function/class definition
**USE**: `mcp__serena__find_symbol`
```python
find_symbol(name_path="authenticate_user", include_body=True)
```

### Understand file structure
**USE**: `mcp__serena__get_symbols_overview`
```python
get_symbols_overview(path="src/auth.py")
```

### Search for pattern in codebase
**USE**: `mcp__serena__search_for_pattern`
```python
search_for_pattern(pattern="async def.*authenticate", path="src/")
```

### Find all usages of function
**USE**: `mcp__serena__find_referencing_symbols`
```python
find_referencing_symbols(name_path="validate_token", path="src/auth.py")
```

## File Operations

### Read file contents
**USE**:
- `mcp__filesystem__read_text_file` (non-code files, configs)
- `mcp__serena__read_file` (Python/code files - indexed)

### List directory contents
**USE**: `mcp__filesystem__list_directory`

### Find files by pattern
**USE**: `mcp__filesystem__search_files`

### Edit file with line-based changes
**USE**: `mcp__filesystem__edit_file`

### Insert code after specific symbol
**USE**: `mcp__serena__insert_after_symbol`

## Version Control

### Check git status
**USE**: `mcp__git__git_status`

### View recent changes
**USE**: `mcp__git__git_diff`

### See commit history
**USE**: `mcp__git__git_log`

## Text Processing (Python shell_utils)

### Search text with regex
**USE**: `shell_utils.grep_text()` (NOT bash grep)

### Count lines in file
**USE**: `shell_utils.count_lines()` (NOT bash wc)

### Read first/last N lines
**USE**: `shell_utils.head()` / `tail()` (NOT bash)

### Extract fields from text
**USE**: `shell_utils.extract_fields()` (NOT bash awk)

### Sum column
**USE**: `shell_utils.sum_column()` (NOT bash awk)

### Pattern match + extract field
**USE**: `shell_utils.filter_and_extract()` (NOT bash awk)

## Documentation Lookup

### Get library documentation
**USE**: `mcp__context7__resolve-library-id` + `get-library-docs`

## Complex Reasoning

### Multi-step problem decomposition
**USE**: `mcp__sequential-thinking__sequentialthinking`

## Project Management

### Create/update Linear issue
**USE**: `mcp__linear-server__create_issue` / `update_issue`

---

## Anti-Patterns (DON'T USE)

❌ **Bash(cat file.py)** → Use `filesystem__read_text_file` or `serena__read_file`
❌ **Bash(find . -name "*.py")** → Use `filesystem__search_files` or `shell_utils.find_files()`
❌ **Bash(grep "pattern" file)** → Use `shell_utils.grep_text()`
❌ **Bash(head -n 10 file)** → Use `shell_utils.head(file, 10)`
❌ **Bash(awk '{print $1}')** → Use `shell_utils.extract_fields(text, [1])`

✅ **Bash(git status)** → OK (external tool)
✅ **Bash(uv run pytest)** → OK (external tool)
```

---

### Phase 4: Python Shell Utilities Module (5h)

**Goal**: Replace bash subprocess calls with efficient Python functions

**Tasks**:
1. Create `tools/ce/shell_utils.py` module
2. Implement 8 utility functions
3. Write comprehensive unit tests
4. Document each function with "Replaces: bash command"
5. Add docstrings with usage examples

**Validation Command**:
```bash
cd tools && uv run pytest tests/test_shell_utils.py -v --cov=ce.shell_utils --cov-report=term-missing
```

**Files to create**:
- CREATE: `tools/ce/shell_utils.py` (8 functions)
- CREATE: `tools/tests/test_shell_utils.py` (100% coverage)

**Implementation** (`tools/ce/shell_utils.py`):
```python
"""Python alternatives to bash utilities for efficiency.

This module provides pure Python implementations of common bash utilities,
eliminating subprocess overhead and improving performance 10-50x.
"""

from typing import List, Optional
import re
from pathlib import Path


def grep_text(pattern: str, text: str, context_lines: int = 0) -> List[str]:
    """Search text with regex, optional context lines.

    Replaces: bash grep -C<n>

    Args:
        pattern: Regex pattern to search for
        text: Input text to search
        context_lines: Number of lines before/after to include

    Returns:
        List of matching lines (with context if specified)

    Example:
        >>> text = "line1\\nerror here\\nline3"
        >>> grep_text("error", text, context_lines=1)
        ['line1', 'error here', 'line3']
    """
    lines = text.split('\n')
    regex = re.compile(pattern)
    matches = []
    matched_indices = set()

    for i, line in enumerate(lines):
        if regex.search(line):
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            matched_indices.update(range(start, end))

    return [lines[i] for i in sorted(matched_indices)]


def count_lines(file_path: str) -> int:
    """Count lines in file.

    Replaces: bash wc -l

    Args:
        file_path: Path to file

    Returns:
        Number of lines in file

    Example:
        >>> count_lines("config.yml")
        42
    """
    return len(Path(file_path).read_text().split('\n'))


def head(file_path: str, n: int = 10) -> List[str]:
    """Read first N lines.

    Replaces: bash head -n

    Args:
        file_path: Path to file
        n: Number of lines to read

    Returns:
        First N lines as list

    Example:
        >>> head("log.txt", n=5)
        ['Line 1', 'Line 2', 'Line 3', 'Line 4', 'Line 5']
    """
    return Path(file_path).read_text().split('\n')[:n]


def tail(file_path: str, n: int = 10) -> List[str]:
    """Read last N lines.

    Replaces: bash tail -n

    Args:
        file_path: Path to file
        n: Number of lines to read

    Returns:
        Last N lines as list

    Example:
        >>> tail("log.txt", n=5)
        ['Line 96', 'Line 97', 'Line 98', 'Line 99', 'Line 100']
    """
    return Path(file_path).read_text().split('\n')[-n:]


def find_files(root: str, pattern: str, exclude: Optional[List[str]] = None) -> List[str]:
    """Find files by glob pattern recursively.

    Replaces: bash find . -name "*.py"

    Args:
        root: Root directory to search from
        pattern: Glob pattern (e.g., "*.py", "**/*.md")
        exclude: Optional list of patterns to exclude

    Returns:
        List of matching file paths

    Example:
        >>> find_files("src", "*.py", exclude=["__pycache__"])
        ['src/main.py', 'src/utils.py']
    """
    exclude = exclude or []
    results = []

    for path in Path(root).rglob(pattern):
        if not any(ex in str(path) for ex in exclude):
            results.append(str(path))

    return sorted(results)


def extract_fields(
    text: str,
    field_indices: List[int],
    delimiter: Optional[str] = None
) -> List[List[str]]:
    """Extract specific fields from each line.

    Replaces: awk '{print $1, $3}'

    Args:
        text: Input text
        field_indices: 1-based field indices (like awk $1, $2)
        delimiter: Field separator (None = whitespace)

    Returns:
        List of extracted field lists per line

    Example:
        >>> text = "user1 100 active\\nuser2 200 inactive"
        >>> extract_fields(text, field_indices=[1, 3])
        [['user1', 'active'], ['user2', 'inactive']]
    """
    lines = text.strip().split('\n')
    results = []

    for line in lines:
        if not line.strip():
            continue
        fields = line.split(delimiter) if delimiter else line.split()
        extracted = []
        for i in field_indices:
            if i <= len(fields):
                extracted.append(fields[i-1])
        if extracted:
            results.append(extracted)

    return results


def sum_column(text: str, column: int, delimiter: Optional[str] = None) -> float:
    """Sum numeric column.

    Replaces: awk '{sum += $1} END {print sum}'

    Args:
        text: Input text
        column: 1-based column index
        delimiter: Field separator (None = whitespace)

    Returns:
        Sum of numeric values in column

    Example:
        >>> text = "item1 100\\nitem2 200\\nitem3 300"
        >>> sum_column(text, column=2)
        600.0
    """
    lines = text.strip().split('\n')
    total = 0.0

    for line in lines:
        if not line.strip():
            continue
        fields = line.split(delimiter) if delimiter else line.split()
        if column <= len(fields):
            try:
                total += float(fields[column-1])
            except ValueError:
                continue

    return total


def filter_and_extract(
    text: str,
    pattern: str,
    field_index: int,
    delimiter: Optional[str] = None
) -> List[str]:
    """Pattern match + field extract.

    Replaces: awk '/pattern/ {print $2}'

    Args:
        text: Input text
        pattern: Regex pattern to match
        field_index: 1-based field to extract
        delimiter: Field separator (None = whitespace)

    Returns:
        List of extracted fields from matching lines

    Example:
        >>> text = "ERROR user1\\nINFO user2\\nERROR user3"
        >>> filter_and_extract(text, "ERROR", field_index=2)
        ['user1', 'user3']
    """
    matching_lines = grep_text(pattern, text, context_lines=0)
    results = []

    for line in matching_lines:
        if not line.strip():
            continue
        fields = line.split(delimiter) if delimiter else line.split()
        if field_index <= len(fields):
            results.append(fields[field_index-1])

    return results
```

**Unit tests** (`tools/tests/test_shell_utils.py`):
```python
"""Tests for shell_utils module - 100% coverage target."""

import pytest
from pathlib import Path
from ce.shell_utils import (
    grep_text,
    count_lines,
    head,
    tail,
    find_files,
    extract_fields,
    sum_column,
    filter_and_extract
)


def test_grep_text_basic():
    text = "line1\nerror here\nline3"
    result = grep_text("error", text)
    assert result == ["error here"]

def test_grep_text_with_context():
    text = "line1\nerror here\nline3"
    result = grep_text("error", text, context_lines=1)
    assert result == ["line1", "error here", "line3"]

def test_extract_fields_basic():
    text = "user1 100 active\nuser2 200 inactive"
    result = extract_fields(text, field_indices=[1, 3])
    assert result == [["user1", "active"], ["user2", "inactive"]]

def test_extract_fields_with_delimiter():
    text = "user1:100:active\nuser2:200:inactive"
    result = extract_fields(text, field_indices=[1, 3], delimiter=":")
    assert result == [["user1", "active"], ["user2", "inactive"]]

def test_sum_column():
    text = "item1 100\nitem2 200\nitem3 300"
    total = sum_column(text, column=2)
    assert total == 600.0

def test_sum_column_with_non_numeric():
    text = "item1 100\nitem2 abc\nitem3 300"
    total = sum_column(text, column=2)
    assert total == 400.0  # Skips non-numeric

def test_filter_and_extract():
    text = "ERROR user1\nINFO user2\nERROR user3"
    result = filter_and_extract(text, "ERROR", field_index=2)
    assert result == ["user1", "user3"]

# ... 10+ more tests for edge cases
```

---

### Phase 5: Refactor CE Modules (4h)

**Goal**: Replace Bash() calls with Python shell_utils

**Tasks**:
1. Grep for all `run_cmd()` and `Bash()` calls
2. Replace with `shell_utils` equivalents
3. Update imports
4. Test each refactored module
5. Verify all tests still pass

**Validation Command**:
```bash
cd tools && uv run pytest tests/ -v
```

**Files to modify**:
- MODIFY: `tools/ce/core.py` - Replace file read ops
- MODIFY: `tools/ce/execute.py` - Replace log parsing
- MODIFY: `tools/ce/validate.py` - Keep only git/pytest bash
- MODIFY: `tools/ce/drift.py` - Replace file analysis

**Example refactoring** (`tools/ce/execute.py`):
```python
# Before
def parse_validation_log(log_file: str) -> List[str]:
    result = run_cmd(f"awk '/ERROR/ {{print $2}}' {log_file}")
    return result["stdout"].strip().split('\n')

# After
from ce.shell_utils import filter_and_extract

def parse_validation_log(log_file: str) -> List[str]:
    log_text = Path(log_file).read_text()
    return filter_and_extract(log_text, "ERROR", field_index=2)
```

---

### Phase 6: Documentation & Metrics (4h)

**Goal**: Update documentation and measure improvements

**Tasks**:
1. Update CLAUDE.md with tool guide reference
2. Update `docs/research/10-tooling-configuration.md`
3. Measure context size (before/after)
4. Run performance benchmarks (Python vs bash)
5. Update tool inventory with final stats

**Validation Command**:
```bash
cd tools && uv run pytest tests/ -v && echo "✅ All tests pass"
```

**Files to modify**:
- MODIFY: `CLAUDE.md` - Add tool mapping reference
- MODIFY: `docs/research/10-tooling-configuration.md` - Update tool matrix
- CREATE: `benchmarks/tool_performance.py` - Performance comparison

**CLAUDE.md update**:
```markdown
## Tool Selection Quick Reference

**See**: `examples/tool-usage-patterns.md` for comprehensive tool mapping guide
**Agent memory**: `.serena/memories/tool-usage-guide.md` (auto-loaded)

### Quick patterns:
- **Find code**: `mcp__serena__find_symbol`
- **Read file**: `mcp__filesystem__read_text_file` or `mcp__serena__read_file`
- **Search text**: Python `shell_utils.grep_text()` (NOT bash grep)
- **Extract fields**: Python `shell_utils.extract_fields()` (NOT bash awk)
```

**Performance benchmark** (`benchmarks/tool_performance.py`):
```python
"""Benchmark Python shell_utils vs bash subprocess calls."""

import time
import subprocess
from ce.shell_utils import grep_text, extract_fields

def benchmark_grep():
    text = "test\n" * 10000 + "error\n" + "test\n" * 10000

    # Bash grep
    start = time.time()
    subprocess.run("echo 'text' | grep 'error'", shell=True, capture_output=True)
    bash_time = time.time() - start

    # Python grep_text
    start = time.time()
    grep_text("error", text)
    python_time = time.time() - start

    print(f"Bash grep: {bash_time*1000:.2f}ms")
    print(f"Python grep: {python_time*1000:.2f}ms")
    print(f"Speedup: {bash_time/python_time:.1f}x")

if __name__ == "__main__":
    benchmark_grep()
    # Expected: Python 10-50x faster
```

---

## 4. VALIDATION GATES

### Level 1: Syntax & Style
```bash
cd tools && uv run ce validate --level 1
```
- Linting passes (ruff, mypy)
- Type checking passes
- No syntax errors in shell_utils.py

### Level 2: Unit Tests
```bash
cd tools && uv run pytest tests/test_shell_utils.py -v --cov=ce.shell_utils --cov-report=term-missing
```
- 100% coverage for shell_utils module
- All utility functions tested with edge cases
- Performance benchmarks show 10-50x improvement

### Level 3: Integration Tests
```bash
cd tools && uv run pytest tests/ -v
```
- All ce module tests pass with refactored code
- Configuration changes don't break existing functionality
- Tool mapping guide accessible and accurate

### Level 4: Context Measurement
```bash
# Measure token reduction
echo "Context size before: [baseline tokens]"
echo "Context size after: [optimized tokens]"
echo "Reduction: [percentage]%"
```
- Context reduction: 30-50% achieved
- Query tree: 60-70% fewer tools
- Bash usage: Reduced from 45+ to 3 commands

---

## 5. ACCEPTANCE CRITERIA

- [ ] **MCP tool audit completed**: `.ce/tool-inventory.yml` created with usage stats
- [ ] **Allow list optimized**: ~31 specific MCP tools (explicit, no wildcards)
- [ ] **Deny list populated**: 50+ unused MCP tools + 11 bash commands
- [ ] **Tool usage guide created**: `examples/tool-usage-patterns.md`
- [ ] **Serena memory populated**: `.serena/memories/tool-usage-guide.md`
- [ ] **Python shell_utils implemented**: 8 functions (grep, wc, head, tail, find, awk×3)
- [ ] **Unit tests**: 100% coverage for shell_utils module
- [ ] **CE modules refactored**: Bash usage reduced from 34 to ~3 calls
- [ ] **Context reduction measured**: 30-50% improvement documented
- [ ] **Query tree optimized**: 60-70% fewer tools in evaluation
- [ ] **Performance validated**: Python utilities 10-50x faster than bash
- [ ] **Documentation updated**: CLAUDE.md, tool matrix, all 5 files synced
- [ ] **All tests pass**: Integration tests pass with new configuration

---

## 6. RISK ASSESSMENT

### Medium Risks

**Risk**: Breaking existing workflows with deny list
- **Impact**: Agent can't access tools it previously used
- **Mitigation**: Comprehensive audit before deny list creation
- **Contingency**: Keep backup of old config, easy rollback

**Risk**: Performance regression in edge cases
- **Impact**: Python utilities slower than bash for some scenarios
- **Mitigation**: Benchmark before/after, optimize hot paths
- **Contingency**: Keep bash for performance-critical operations

### Low Risks

**Risk**: Incomplete tool mapping guide
- **Impact**: Agent still uses trial-and-error for some tasks
- **Mitigation**: Iterate on guide based on usage patterns
- **Contingency**: Guide is additive, can expand post-launch

---

## 7. ESTIMATED EFFORT

- **Phase 1** (Audit): 5 hours
- **Phase 2** (Configuration): 3 hours
- **Phase 3** (Tool mapping): 4 hours
- **Phase 4** (Shell utils): 5 hours
- **Phase 5** (Refactoring): 4 hours
- **Phase 6** (Documentation): 4 hours

**Total**: 25 hours

---

## 8. NOTES & LEARNINGS

### Key Decisions

**Decision 1**: Deny list for efficiency, not security
- **Rationale**: Unused tools bloat context but aren't security risks
- **Alternative considered**: Remove MCP servers entirely (too aggressive)

**Decision 2**: Python over bash for text processing
- **Rationale**: 10-50x performance improvement, no subprocess overhead
- **Alternative considered**: Keep bash (rejected due to inefficiency)

**Decision 3**: Tool mapping guide in examples/ + Serena memory
- **Rationale**: Agent needs instant access without searching docs
- **Alternative considered**: Only in docs/ (rejected, too slow for agent)

### Implementation Patterns

**Pattern 1**: MCP availability detection (from `mcp_adapter.py`)
```python
try:
    import mcp.client.stdio
    serena_available = True
except ImportError:
    serena_available = False
```

**Pattern 2**: Graceful degradation
```python
if tool_available():
    result = optimal_implementation()
else:
    result = fallback_implementation()
```

**Pattern 3**: Python utility docstrings
```python
def utility():
    """Description.

    Replaces: bash command
    """
```

### Future Enhancements

1. **Auto-update tool inventory**: Script to re-audit on codebase changes
2. **Tool usage analytics**: Track which tools most frequently used
3. **Dynamic deny list**: Auto-deny tools with 0 usage over time
4. **Performance dashboard**: Real-time context size monitoring
