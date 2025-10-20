# Tool Usage Patterns - Quick Reference

**Purpose**: Fast agent tool selection without trial-and-error

**Target Audience**: AI agents working with Context Engineering codebase

**Last Updated**: 2025-10-17

---

## Code Navigation & Analysis

### Find function/class definition

**USE**: `mcp__syntropy__serena__find_symbol`

```python
# Find function by name
find_symbol(name_path="authenticate_user", include_body=True)

# Find method in class
find_symbol(name_path="UserAuth/validate", include_body=True)
```

**When**: You know the symbol name and want to see its implementation

### Understand file structure

**USE**: `mcp__syntropy__serena__get_symbols_overview`

```python
# Get top-level overview
get_symbols_overview(path="src/auth.py")
```

**When**: First time exploring a file, want to see all classes/functions

### Search for pattern in codebase

**USE**: `mcp__syntropy__serena__search_for_pattern`

```python
# Find async functions
search_for_pattern(pattern="async def.*authenticate", path="src/")

# Find specific error handling
search_for_pattern(pattern="except.*ValueError", path="src/")
```

**When**: Searching for code patterns, not specific symbol names

### Find all usages of function

**USE**: `mcp__syntropy__serena__find_referencing_symbols`

```python
# Find everywhere validate_token is called
find_referencing_symbols(name_path="validate_token", path="src/auth.py")
```

**When**: Understanding dependencies, impact analysis before changes

---

## File Operations

### Read file contents

**USE**:
- `mcp__syntropy__filesystem__read_text_file` - For config files, markdown, non-code
- `mcp__syntropy__serena__read_file` - For Python/code files (indexed by LSP)

```python
# Read config file
read_text_file(path=".ce/tool-inventory.yml")

# Read Python module
read_file(relative_path="ce/core.py")
```

**When**: Need to read entire file contents

### List directory contents

**USE**: `mcp__syntropy__filesystem__list_directory`

```python
list_directory(path="examples/")
```

**When**: Exploring directory structure, finding files

### Find files by pattern

**USE**: `mcp__syntropy__filesystem__search_files`

```python
# Find all test files
search_files(path="tests", pattern="test_*.py")
```

**When**: Finding files matching specific naming pattern

### Edit file with line-based changes

**USE**: `mcp__syntropy__filesystem__edit_file`

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

### Insert code after specific symbol

**USE**: `mcp__syntropy__serena__insert_after_symbol`

```python
# Add new method after existing one
insert_after_symbol(
    name_path="UserAuth/login",
    relative_path="src/auth.py",
    body="    def logout(self):\n        pass"
)
```

**When**: Adding new code adjacent to existing symbols

---

## Version Control

### Check git status

**USE**: `mcp__syntropy__git__git_status`

```python
git_status(repo_path=".")
```

**When**: Check working directory status before commits

### View recent changes

**USE**: `mcp__syntropy__git__git_diff`

```python
git_diff(repo_path=".", target="HEAD")
```

**When**: Review changes before committing

### See commit history

**USE**: `mcp__syntropy__git__git_log`

```python
git_log(repo_path=".", max_count=10)
```

**When**: Understanding recent commits, finding commit messages

### Stage and commit changes

**USE**: `mcp__syntropy__git__git_add` + `mcp__syntropy__git__git_commit`

```python
# Stage files
git_add(repo_path=".", files=["ce/core.py", "tests/test_core.py"])

# Commit with message
git_commit(repo_path=".", message="feat: add new feature")
```

**When**: Creating commits during implementation

---

## Text Processing (Python shell_utils)

**IMPORTANT**: Always prefer Python shell_utils over bash subprocess calls

### Search text with regex

**USE**: `shell_utils.grep_text()`

❌ **NOT**: `Bash(grep "pattern" file)`

```python
from ce.shell_utils import grep_text

# Search with context
text = Path("log.txt").read_text()
matches = grep_text("ERROR", text, context_lines=2)
```

**When**: Searching text content, filtering log files

### Count lines in file

**USE**: `shell_utils.count_lines()`

❌ **NOT**: `Bash(wc -l file)`

```python
from ce.shell_utils import count_lines

line_count = count_lines("ce/core.py")
```

**When**: Getting file statistics, size checks

### Read first/last N lines

**USE**: `shell_utils.head()` / `shell_utils.tail()`

❌ **NOT**: `Bash(head -n 10 file)` or `Bash(tail -n 10 file)`

```python
from ce.shell_utils import head, tail

# First 10 lines
first_lines = head("log.txt", n=10)

# Last 20 lines
last_lines = tail("log.txt", n=20)
```

**When**: Inspecting file beginnings/endings without full read

### Extract fields from text

**USE**: `shell_utils.extract_fields()`

❌ **NOT**: `Bash(awk '{print $1, $3}' file)`

```python
from ce.shell_utils import extract_fields

text = "user1 100 active\nuser2 200 inactive"
# Extract columns 1 and 3
fields = extract_fields(text, field_indices=[1, 3])
# Result: [['user1', 'active'], ['user2', 'inactive']]
```

**When**: Parsing structured text, extracting columns

### Sum numeric column

**USE**: `shell_utils.sum_column()`

❌ **NOT**: `Bash(awk '{sum += $1} END {print sum}' file)`

```python
from ce.shell_utils import sum_column

text = "item1 100\nitem2 200\nitem3 300"
total = sum_column(text, column=2)
# Result: 600.0
```

**When**: Calculating totals from tabular data

### Pattern match + extract field

**USE**: `shell_utils.filter_and_extract()`

❌ **NOT**: `Bash(awk '/pattern/ {print $2}' file)`

```python
from ce.shell_utils import filter_and_extract

text = "ERROR user1\nINFO user2\nERROR user3"
errors = filter_and_extract(text, "ERROR", field_index=2)
# Result: ['user1', 'user3']
```

**When**: Filtering and extracting in one operation

### Find files recursively

**USE**: `shell_utils.find_files()`

❌ **NOT**: `Bash(find . -name "*.py")`

```python
from ce.shell_utils import find_files

# Find all Python files
py_files = find_files("src", "*.py", exclude=["__pycache__"])
```

**When**: Finding files by pattern, excluding directories

---

## Documentation Lookup

### Get library documentation

**USE**: `mcp__syntropy__context7__resolve-library-id` + `mcp__syntropy__context7__get-library-docs`

```python
# Step 1: Resolve library ID
lib_id = resolve_library_id(libraryName="pytest")

# Step 2: Get docs
docs = get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="fixtures"
)
```

**When**: Need external library documentation, API references

---

## Complex Reasoning

### Multi-step problem decomposition

**USE**: `mcp__syntropy__thinking__sequentialthinking`

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

## Project Management

### Create/update Linear issue

**USE**: `mcp__syntropy__linear__create_issue` / `mcp__syntropy__linear__update_issue`

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

**USE**: `mcp__syntropy__linear__list_issues`

```python
list_issues(
    team="Blaise78",
    assignee="me",
    state="in_progress"
)
```

**When**: Finding assigned work, checking project status

---

## Anti-Patterns (DON'T USE)

### ❌ Bash Text Processing

| Instead of... | Use... | Reason |
|---------------|--------|---------|
| `Bash(cat file.py)` | `mcp__syntropy__filesystem__read_text_file` | No subprocess overhead |
| `Bash(grep "pattern" file)` | `shell_utils.grep_text()` | 10-50x faster |
| `Bash(head -n 10 file)` | `shell_utils.head(file, 10)` | Python stdlib, no fork |
| `Bash(tail -n 10 file)` | `shell_utils.tail(file, 10)` | Python stdlib, no fork |
| `Bash(find . -name "*.py")` | `shell_utils.find_files()` | Python stdlib, cleaner |
| `Bash(awk '{print $1}')` | `shell_utils.extract_fields()` | Type-safe, faster |
| `Bash(wc -l file)` | `shell_utils.count_lines()` | Simple Python |
| `Bash(echo "text")` | `print()` or direct string | No subprocess needed |
| `Bash(python script.py)` | `uv run ce run_py script.py` | Proper env management |
| `Bash(python3 -c "code")` | `uv run ce run_py --code "code"` | Proper env management |

### ✅ Bash Allowed (External Tools Only)

| Command | Use Case | Why Allowed |
|---------|----------|-------------|
| `Bash(git:*)` | Version control | Git is external tool |
| `Bash(uv run:*)` | Python execution | UV is external tool |
| `Bash(uv add:*)` | Package management | UV is external tool |
| `Bash(uvx:*)` | UV executor | UV is external tool |
| `Bash(env:*)` | Environment vars | System command |
| `Bash(brew install:*)` | Package install | System package manager |

---

## Performance Considerations

### Python shell_utils vs Bash subprocess

**Benchmark Results** (from inventory):
- **10-50x faster**: Python utilities eliminate subprocess overhead
- **No fork penalty**: Python runs in same process
- **Type-safe**: Python functions have proper types, errors caught early
- **Testable**: Unit tests for Python utilities, hard to test bash pipes

### When to use Bash

**ONLY use Bash for**:
1. External tools (git, uv, pytest)
2. System commands (env, brew)
3. Operations requiring shell features (pipes, redirection)

**Example - Bash OK**:
```bash
Bash(git status)  # ✅ External tool
Bash(uv run pytest tests/)  # ✅ External tool
```

**Example - Bash NOT OK**:
```bash
Bash(cat file.py | grep "def")  # ❌ Use shell_utils.grep_text()
Bash(find . -name "*.py" | wc -l)  # ❌ Use shell_utils.find_files() + len()
```

---

## Tool Selection Decision Tree

```
Need to work with code?
├─ Know symbol name? → mcp__syntropy__serena__find_symbol
├─ Exploring file? → mcp__syntropy__serena__get_symbols_overview
├─ Pattern search? → mcp__syntropy__serena__search_for_pattern
└─ Find usages? → mcp__syntropy__serena__find_referencing_symbols

Need to read file?
├─ Code file? → mcp__syntropy__serena__read_file
└─ Config/text? → mcp__syntropy__filesystem__read_text_file

Need text processing?
└─ Always use shell_utils (grep_text, extract_fields, etc.)

Need git operation?
└─ Use mcp__syntropy__git__* tools (status, diff, log, add, commit)

Need external docs?
└─ Use mcp__syntropy__context7__* tools

Need complex reasoning?
└─ Use mcp__syntropy__thinking__sequentialthinking

Need bash?
└─ ONLY for external tools (git, uv, pytest)
```

---

## Quick Command Reference

### Most Common Operations

```python
# 1. Find and read code
find_symbol("function_name", include_body=True)
get_symbols_overview("path/to/file.py")

# 2. Search codebase
search_for_pattern("pattern", path="src/")

# 3. Read files
read_text_file("config.yml")  # Config/text
read_file("code.py")  # Python code

# 4. Text processing
grep_text("ERROR", log_text, context_lines=2)
extract_fields(text, [1, 3])  # Columns 1 and 3

# 5. Git operations
git_status(".")
git_diff(".", "HEAD")
git_log(".", max_count=10)

# 6. File system
list_directory("examples/")
search_files("tests", "test_*.py")
```

---

## Context Overhead Optimization

This guide exists to **reduce query tree complexity** and **accelerate tool selection**.

**Before optimization**: Agent evaluates 100+ tools for each decision
**After optimization**: Agent quickly selects from 46 essential tools

**Deny list (124 tools)**: Removes unused tools from context
**This guide**: Maps tasks to specific tools, eliminates trial-and-error

**Result**: 60-70% reduction in tool evaluation overhead

---

## Current Permission Configuration

**Last Verified**: 2025-10-20
**Source**: `.claude/settings.local.json`
**Status**: ✅ Updated for Syntropy MCP (Oct 20)

### Allow List - Syntropy Forwarded Tools

**All tools now route through Syntropy MCP with unified `mcp__syntropy__<server>__<tool>` format**:

```
mcp__syntropy__serena__*            # Serena tools (8)
mcp__syntropy__filesystem__*        # Filesystem tools (8)
mcp__syntropy__git__*               # Git tools (5)
mcp__syntropy__context7__*          # Context7 documentation (2)
mcp__syntropy__thinking__*          # Sequential thinking (1)
mcp__syntropy__linear__*            # Linear integration (5)
mcp__syntropy__repomix__*           # Codebase packaging (1)
```

**Benefits of Syntropy Aggregation**:
- ✅ Single MCP server manages 6 underlying servers
- ✅ Connection pooling reduces overhead
- ✅ Lazy initialization (servers spawn on first use)
- ✅ Automatic resource cleanup
- ✅ Unified error handling with troubleshooting guidance

### Deny List (124 tools)

**Major Categories**:
- **Serena advanced**: 13 (symbol mutations, thinking tools, modes, memories)
- **Filesystem redundant**: 6 (read variants, move, sizes)
- **Git advanced**: 6 (branch, checkout, show, reset, diff variants)
- **GitHub MCP**: 26 (all GitHub operations - use git CLI instead)
- **Playwright**: 31 (web automation not needed)
- **Perplexity**: 1 (redundant with web search)
- **Repomix partial**: 4 (remote repo, read/grep output, file system ops)
- **IDE**: 2 (diagnostics, executeCode)
- **Linear extended**: 14 (comments, cycles, docs, labels, statuses, teams, users)
- **Bash text processing**: 11 (cat, head, tail, find, grep, wc, awk, sed, echo, python)

### Rationale - Critical Workflow Tools

**Why Linear tools preserved** (5 tools via `mcp__syntropy__linear__*`):
- The `/generate-prp` command automatically creates Linear issues to track implementation
- Essential for documented PRP workflow (see CLAUDE.md lines 498-554)
- Enables complete feature tracking from conception to completion
- Without these: Issue tracking breaks, implementation blueprints untracked

**Why Context7 preserved** (2 tools via `mcp__syntropy__context7__*`):
- Documentation lookup essential for external libraries (FastAPI, pytest, etc.)
- Enables knowledge-grounded PRPs with real API references
- Required for accurate framework integration patterns
- Without these: External library integration impossible, PRPs lack real-world docs

**Why Sequential-thinking preserved** (1 tool via `mcp__syntropy__thinking__*`):
- Complex reasoning for PRP generation and multi-phase implementations
- Enables structured decomposition of large features into manageable parts
- Essential for architectural decision-making
- Without this: Complex problems can't be systematically decomposed

**Why find_referencing_symbols preserved**:
- Impact analysis before code changes prevents breaking dependencies
- Identifies all call sites when refactoring functions
- Reduces bugs from missed references

**Why edit_file preserved**:
- Primary tool for surgical code edits with line-level precision
- Safer than regex replacements for small, targeted changes
- Workaround for denied symbol mutation tools

**Historical note**: `PRPs/feature-requests/tools-rationalization-study.md` recommended 31-tool config but missed critical workflow tools (Linear, Context7, reasoning) and recommended already-denied tools (symbol mutations, read_memory). Current configuration is empirically validated and production-tested.

### Validation Tool

Check current permissions with Python utility (replaces forbidden jq/grep):

```bash
# Count tools (replaces: jq '.permissions.allow | length')
cd tools && uv run python -m ce.validate_permissions count
# Output: Allow: 46, Deny: 124

# Show categorized breakdown
cd tools && uv run python -m ce.validate_permissions categorize

# Verify critical tool exists (replaces: grep -F "tool_name")
cd tools && uv run python -m ce.validate_permissions verify mcp__linear-server__create_issue
# Output: In allow: True, In deny: False

# Search for pattern (replaces: jq '.permissions.allow[] | select(contains("pattern"))')
cd tools && uv run python -m ce.validate_permissions search linear allow
# Output: All 5 Linear tools listed
```
