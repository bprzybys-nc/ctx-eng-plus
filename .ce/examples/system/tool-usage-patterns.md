# Tool Usage Patterns - Quick Reference

**Purpose**: Fast agent tool selection without trial-and-error

**Target Audience**: AI agents working with Context Engineering codebase

**Last Updated**: 2025-10-20
**Status**: ✅ Updated for Syntropy MCP aggregation layer

---

## Code Navigation & Analysis

### Find function/class definition

**USE**: `mcp__syntropy_serena_find_symbol`

```python
# Find function by name
find_symbol(name_path="authenticate_user", include_body=True)

# Find method in class
find_symbol(name_path="UserAuth/validate", include_body=True)
```

**When**: You know the symbol name and want to see its implementation

### Understand file structure

**USE**: `mcp__syntropy_serena_get_symbols_overview`

```python
# Get top-level overview
get_symbols_overview(path="src/auth.py")
```

**When**: First time exploring a file, want to see all classes/functions

### Search for pattern in codebase

**USE**: `mcp__syntropy_serena_search_for_pattern`

```python
# Find async functions
search_for_pattern(pattern="async def.*authenticate", path="src/")

# Find specific error handling
search_for_pattern(pattern="except.*ValueError", path="src/")
```

**When**: Searching for code patterns, not specific symbol names

### Find all usages of function

**USE**: `mcp__syntropy_serena_find_referencing_symbols`

```python
# Find everywhere validate_token is called
find_referencing_symbols(name_path="validate_token", path="src/auth.py")
```

**When**: Understanding dependencies, impact analysis before changes

---

## File Operations

### Read file contents

**USE**:
- `mcp__syntropy_filesystem_read_text_file` - For config files, markdown, non-code
- `mcp__syntropy_serena_read_file` - For Python/code files (indexed by LSP)

```python
# Read config file
read_text_file(path=".ce/tool-inventory.yml")

# Read Python module
read_file(relative_path="ce/core.py")
```

**When**: Need to read entire file contents

### List directory contents

**USE**: `mcp__syntropy_filesystem_list_directory`

```python
list_directory(path="examples/")
```

**When**: Exploring directory structure, finding files

### Find files by pattern

**USE**: `mcp__syntropy_filesystem_search_files`

```python
# Find all test files
search_files(path="tests", pattern="test_*.py")
```

**When**: Finding files matching specific naming pattern

### Edit file with line-based changes

**USE**: `mcp__syntropy_filesystem_edit_file`

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

**USE**: `mcp__syntropy_serena_insert_after_symbol`

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

**USE**: `mcp__syntropy_git_git_status`

```python
git_status(repo_path=".")
```

**When**: Check working directory status before commits

### View recent changes

**USE**: `mcp__syntropy_git_git_diff`

```python
git_diff(repo_path=".", target="HEAD")
```

**When**: Review changes before committing

### See commit history

**USE**: `mcp__syntropy_git_git_log`

```python
git_log(repo_path=".", max_count=10)
```

**When**: Understanding recent commits, finding commit messages

### Stage and commit changes

**USE**: `mcp__syntropy_git_git_add` + `mcp__syntropy_git_git_commit`

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

**USE**: `mcp__syntropy_context7_resolve_library_id` + `mcp__syntropy_context7_get_library_docs`

```python
# Step 1: Resolve library ID
lib_id = mcp__syntropy_context7_resolve_library_id(libraryName="pytest")

# Step 2: Get docs
docs = mcp__syntropy_context7_get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="fixtures"
)
```

**When**: Need external library documentation, API references

---

## Complex Reasoning

### Multi-step problem decomposition

**USE**: `mcp__syntropy_thinking_sequentialthinking`

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

**USE**: `mcp__syntropy_linear_create_issue` / `mcp__syntropy_linear_update_issue`

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

**USE**: `mcp__syntropy_linear_list_issues`

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
| `Bash(cat file.py)` | `mcp__syntropy_filesystem_read_text_file` | No subprocess overhead |
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
├─ Know symbol name? → mcp__syntropy_serena_find_symbol
├─ Exploring file? → mcp__syntropy_serena_get_symbols_overview
├─ Pattern search? → mcp__syntropy_serena_search_for_pattern
└─ Find usages? → mcp__syntropy_serena_find_referencing_symbols

Need to read file?
├─ Code file? → mcp__syntropy_serena_read_file
└─ Config/text? → mcp__syntropy_filesystem_read_text_file

Need text processing?
└─ Always use shell_utils (grep_text, extract_fields, etc.)

Need git operation?
└─ Use mcp__syntropy_git_* tools (status, diff, log, add, commit)

Need external docs?
└─ Use `mcp__syntropy_context7_resolve_library_id` + `mcp__syntropy_context7_get_library_docs`

Need complex reasoning?
└─ Use mcp__syntropy_thinking_sequentialthinking

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
**After optimization**: Agent quickly selects from 30 essential tools

**Deny list (126 tools)**: Removes unused tools from context
**This guide**: Maps tasks to specific tools, eliminates trial-and-error

**Result**: 60-70% reduction in tool evaluation overhead

---

## Critical Workflow Tools - Why Preserved in Syntropy Format

#### Linear Integration (5 tools via `mcp__syntropy_linear_*`)

**Tools**:
- `mcp__syntropy_linear_create_issue` - Create new Linear issues
- `mcp__syntropy_linear_get_issue` - Retrieve issue details
- `mcp__syntropy_linear_list_issues` - List issues with filtering
- `mcp__syntropy_linear_update_issue` - Update issue status/content
- `mcp__syntropy_linear_list_projects` - List available projects

**Why Preserved**:
- The `/generate-prp` command automatically creates Linear issues to track implementation
- Essential for documented PRP workflow (see CLAUDE.md lines 498-554)
- Enables complete feature tracking from conception to completion
- **Without these**: Issue tracking breaks, implementation blueprints untracked

**Example Usage**:
```python
# Auto-create issue from PRP generation
mcp__syntropy_linear_create_issue(
    team="Blaise78",
    title="PRP-25: Feature Implementation",
    description="Detailed feature from PRP blueprint",
    assignee="blazej.przybyszewski@gmail.com"
)
```

---

#### Context7 Documentation (2 tools via `mcp__syntropy_context7_*`)

**Tools**:
- `mcp__syntropy_context7_resolve_library_id` - Resolve library identifiers
- `mcp__syntropy_context7_get_library_docs` - Fetch library documentation

**Why Preserved**:
- Documentation lookup essential for external libraries (FastAPI, pytest, SQLAlchemy)
- Enables knowledge-grounded PRPs with real API references
- Required for accurate framework integration patterns
- **Without these**: External library integration impossible, PRPs lack real-world docs

**Example Usage**:
```python
# Fetch framework documentation for integration planning
lib_id = mcp__syntropy_context7_resolve_library_id(
    libraryName="FastAPI"
)
docs = mcp__syntropy_context7_get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="dependency_injection"
)
```

---

#### Sequential Thinking (1 tool via `mcp__syntropy_thinking_*`)

**Tool**:
- `mcp__syntropy_thinking_sequentialthinking` - Multi-step problem decomposition

**Why Preserved**:
- Complex reasoning for PRP generation and multi-phase implementations
- Enables structured decomposition of large features into manageable parts
- Essential for architectural decision-making
- **Without this**: Complex problems can't be systematically decomposed

**Example Usage**:
```python
# Structure complex architectural planning
mcp__syntropy_thinking_sequentialthinking(
    thought="Step 1: Analyze current architecture and identify service boundaries",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)
```

---

### Historical Context

**`PRPs/feature-requests/tools-rationalization-study.md`**:
- Recommended denying Linear, Context7, and Sequential-thinking tools
- Empirical testing proved this recommendation was incorrect
- These tools are essential for documented workflows
- Study marked as outdated historical reference
- Current configuration is production-tested and validated

---

## Quick Reference: Common Violations

**All violations from tools-misuse-test-report.md with immediate remedies**

| Denied Pattern | ❌ Problem | ✅ Allowed Alternative | Performance Gain | Example |
|----------------|-----------|------------------------|-----------------|----------|
| `Bash(cat file)` | Subprocess fork overhead | `read_text_file(path)` | 10-50x faster | `read_text_file('log.txt')` |
| `Bash(head -n 10 file)` | Subprocess + piping | `Read(limit=10)` or `shell_utils.head()` | 10-50x faster | `head('file.py', 10)` |
| `Bash(tail -n 10 file)` | Subprocess + piping | `Read(offset=-10)` or `shell_utils.tail()` | 10-50x faster | `tail('log.txt', 10)` |
| `Bash(grep pattern file)` | Regex fragile, no type safety | `shell_utils.grep_text()` or `Grep()` tool | 10-50x faster | `grep_text('ERROR', text)` |
| `Bash(awk '{print $1}')` | Complex piping, hard to test | `shell_utils.extract_fields()` | 10-50x faster | `extract_fields(text, [1])` |
| `Bash(wc -l file)` | Subprocess overhead | `shell_utils.count_lines()` | 10-50x faster | `count_lines('file.py')` |
| `Bash(python script.py)` | Wrong env (no venv activation) | `uv run ce run_py script.py` | Proper env mgmt | `Bash(uv run:*)` |
| `mcp__serena__replace_symbol_body` | Permission denied (elevated access) | Read + Edit or `edit_file()` | Same speed, more control | See "Workarounds" below |

---

## Troubleshooting: Permission Denied Errors

### Error: "Permission denied - mcp__serena__replace_symbol_body or replace_regex"

**Cause**: Symbol mutation tools (replace_symbol_body, replace_regex) are DENIED - require elevated permissions not available in this project

**Note**: `insert_after_symbol` and `insert_before_symbol` are NOW ALLOWED for code insertion

**Immediate Fixes**:

1. **For full function replacement** → Use Claude Code's Edit tool (Read + Edit pattern)
   ```python
   # Read file first, then use Edit tool
   Read(file_path="path/to/file.py")
   # Then use Edit with old_string/new_string containing full function
   ```

2. **For line-level changes** → Use `mcp_syntropy_filesystem_edit_file()`
   ```python
   # Surgical edit within a function
   mcp_syntropy_filesystem_edit_file(
       path="path/to/file.py",
       edits=[{
           "oldText": "    x = old_value",
           "newText": "    x = new_value"
       }]
   )
   ```

3. **For adding new methods** → Use `mcp_syntropy_serena_insert_after_symbol()` ✅ NOW ALLOWED
   ```python
   mcp_syntropy_serena_insert_after_symbol(
       name_path="ClassName/existing_method",
       relative_path="path/to/file.py",
       body="    def new_method(self):\n        pass"
   )
   ```

### Error: "Permission denied - Bash(cat:*), Bash(grep:*), etc"

**Cause**: Text processing via bash is inefficient and denied by policy

**Immediate Fixes**:

| Error | Remedy | How |
|-------|--------|-----|
| `Bash(cat file)` denied | Use `read_text_file()` | Direct file read, no subprocess |
| `Bash(grep pattern)` denied | Use `grep_text()` or `Grep()` | Python stdlib or MCP tool |
| `Bash(head -n 10)` denied | Use `head(file, 10)` | Python stdlib wrapper |
| `Bash(tail -n 10)` denied | Use `tail(file, 10)` | Python stdlib wrapper |
| `Bash(awk '{...}')` denied | Use `extract_fields()` | Type-safe field extraction |
| `Bash(python script.py)` denied | Use `uv run ce run_py script.py` | Proper environment activation |

**Quick Fix Template**:
```python
# ❌ DENIED - Will get permission error
Bash(grep "ERROR" log.txt)

# ✅ ALLOWED - Works immediately
from ce.shell_utils import grep_text
text = read_text_file("log.txt")
matches = grep_text("ERROR", text, context_lines=2)
```

---

## Real Production Examples (From tools-misuse-test-report.md)

### Example 1: Bash head anti-pattern

**❌ DETECTED VIOLATION**:
```bash
Bash(head -n 20 file.py)
```

**Problem**: 
- Subprocess fork overhead
- No type safety
- Hard to compose with other operations

**✅ CORRECTED**:
```python
from ce.shell_utils import head
first_lines = head("file.py", n=20)
```

**Impact**: 10-50x faster (no subprocess fork)

---

### Example 2: Bash grep anti-pattern

**❌ DETECTED VIOLATION**:
```bash
Bash(grep "pattern" file.log | grep "ERROR")
```

**Problem**:
- Multiple subprocess forks
- Fragile piping
- Error handling unclear

**✅ CORRECTED**:
```python
from ce.shell_utils import grep_text
text = read_text_file("file.log")
errors = grep_text("pattern", text, context_lines=2)
error_matches = [line for line in errors if "ERROR" in line]
```

**Impact**: 10-50x faster, type-safe filtering

---

### Example 3: Python subprocess anti-pattern

**❌ DETECTED VIOLATION**:
```bash
Bash(python3 -c "print('hello')")
```

**Problem**:
- Wrong Python environment (no venv activation)
- Subprocess overhead
- Hard to pass complex code

**✅ CORRECTED**:
```bash
Bash(uv run ce run_py --code "print('hello')")
# Or for files:
Bash(uv run ce run_py script.py)
```

**Impact**: Proper environment management, correct dependencies

---

### Example 4: Symbol body replacement anti-pattern

**❌ DETECTED VIOLATION**:
```python
mcp__serena__replace_symbol_body(
    name_path="validate_token",
    relative_path="src/auth.py",
    body="def validate_token():\n    return True"
)
# Error: Permission denied
```

**Problem**: Symbol mutation tools (replace_symbol_body, replace_regex) are DENIED

**✅ CORRECTED** (Option 1 - Read + Edit pattern):
```python
# Read file first to see full function
Read(file_path="src/auth.py")
# Then use Edit tool with full old_string/new_string
Edit(
    file_path="src/auth.py",
    old_string="def validate_token():\n    return False",
    new_string="def validate_token():\n    return True"
)
```

**✅ CORRECTED** (Option 2 - Surgical edit with filesystem):
```python
mcp_syntropy_filesystem_edit_file(
    path="src/auth.py",
    edits=[{
        "oldText": "    return False",
        "newText": "    return True"
    }]
)
```

**Impact**: Same speed, more control, no permission errors

---

## Performance Benchmarks

### Measured Improvements (tools-misuse-test-report.md)

| Operation | Bash Approach | Python Approach | Speedup | Reason |
|-----------|---------------|-----------------|---------|--------|
| Read file (100KB) | `Bash(cat)` | `read_text_file()` | 20-40x | No subprocess fork |
| Search text (1000 lines) | `Bash(grep)` | `grep_text()` | 15-50x | No piping overhead |
| Extract fields (10k rows) | `Bash(awk)` | `extract_fields()` | 10-30x | Python loop vs regex |
| Count lines | `Bash(wc)` | `count_lines()` | 10-25x | No subprocess |
| Head/tail (N lines) | `Bash(head/tail)` | Python function | 10-50x | No piping |

### Token Usage Impact

| Approach | Tokens | Notes |
|----------|--------|-------|
| Bash subprocess call | 50-100 | Overhead from shell parsing |
| Python native function | 10-20 | Direct execution, no fork |
| **Savings** | **60-80%** | Per operation |

### When to Check Performance Metrics

- **High-volume operations** (>1000 items): Use Python (10-50x gain)
- **Low-volume operations** (<10 items): Either approach (difference negligible)
- **Complex filtering**: Always use Python (type safety matters more than speed)
- **Production code**: Never use Bash for text processing (unmaintainable)

---

## Automation Patterns - Drift Remediation

### --remediate Flag (YOLO Mode)

**Use Case**: Automate drift fixing in CI/CD or batch scenarios

**When to Use**:
- ✅ CI/CD pipelines with automated drift fixing
- ✅ Batch remediation of known violations
- ✅ Non-interactive contexts (scripts, automation)
- ✅ Development environments with trusted detection

**When NOT to Use**:
- ❌ First-time drift detection (review first)
- ❌ Production systems without manual review
- ❌ Unfamiliar violation patterns

**Example**:
```bash
# CI/CD pipeline usage
cd tools && uv run ce update-context --remediate
# Auto-generates PRP, displays /execute-prp command
```

**Workflow**:
```bash
# Step 1: Detect drift
cd tools && uv run ce analyze-context
# Output: Drift score: 8.5% (review recommendations)

# Step 2: Remediate automatically
cd tools && uv run ce update-context --remediate
# Auto-generates PRP file, shows execution command

# Step 3: Execute the generated PRP
/execute-prp path/to/generated-PRP.md
```

---

## Compositional Patterns - Pipeline API

**Purpose**: Chain shell_utils operations without subprocess overhead

**Performance**: 10-50x faster than bash equivalents

### Basic Usage

```python
from ce.shell_utils import Pipeline

# Create pipeline from file
result = Pipeline.from_file("log.txt").grep("ERROR").count()
print(f"Found {result} ERROR lines")

# Create pipeline from text
text = "a\nb\nc"
first = Pipeline.from_text(text).head(2).text()
print(first)  # Output: "a\nb"
```

### Real-World Example 1: Log Analysis

```python
# Count ERROR lines and extract user IDs
errors = (
    Pipeline.from_file("app.log")
    .grep("ERROR")
    .extract_fields([2])  # Extract user ID (2nd field)
    .lines()
)
print(f"Affected users: {len(errors)}")

# Performance: ~10-50x faster than:
# Bash(grep "ERROR" app.log | awk '{print $2}' | wc -l)
```

### Real-World Example 2: Data Processing

```python
# Sum column values, filtering by criteria
total = (
    Pipeline.from_file("sales.csv")
    .grep(r"COMPLETED")  # Only completed sales
    .sum_column(3)  # Sum 3rd column (amount)
)
print(f"Total sales: ${total}")

# Performance: ~10-50x faster than:
# Bash(grep "COMPLETED" sales.csv | awk '{sum += $3} END {print sum}')
```

### When to Use Pipeline vs Standalone Functions

| Scenario | Use Pipeline | Use Standalone | Reason |
|----------|--------------|----------------|--------|
| Single operation (grep only) | ❌ | ✅ | Simpler code |
| 2+ chained operations | ✅ | ❌ | Avoids intermediate variables |
| Complex filtering logic | ✅ | ❌ | Cleaner readable syntax |
| File processing loop | ❌ | ✅ | Standalone functions faster |

### Pipeline Methods Reference

```python
# Creation
Pipeline.from_file("path.txt")       # Load from file
Pipeline.from_text("multi\nline")    # Load from string
Pipeline(["a", "b", "c"])            # Load from list

# Filtering
.grep("pattern", context_lines=1)     # Filter by regex
.head(n=10)                           # Keep first N lines
.tail(n=10)                           # Keep last N lines

# Extraction
.extract_fields([1, 3])               # Extract columns
.sum_column(2, delimiter=":" )        # Sum numeric column

# Terminal operations (return values, not Pipeline)
.count()                              # Return line count
.text()                               # Return as string
.lines()                              # Return as list
.first()                              # Return first line
.last()                               # Return last line
```

### Performance Comparison

**Bash approach** (subprocess overhead):
```bash
grep "ERROR" log.txt | awk '{print $2}' | wc -l
# ~100-200ms for 1M lines (includes shell parsing, piping)
```

**Pipeline approach** (Python native):
```python
Pipeline.from_file("log.txt").grep("ERROR").extract_fields([2]).count()
# ~5-20ms for 1M lines (direct Python, no shell)
```

**Speedup**: 10-50x faster with Pipeline

---

## Implementation Roadmap

### Phase 1: Policy Enforcement ✅ COMPLETE
- Deny list configured in `.claude/settings.local.json`
- All violations blocked at source
- Serena MCP restrictions documented

### Phase 2: Documentation & Guidance ✅ IN PROGRESS
- Quick Reference table added (this section)
- Troubleshooting guide added (this section)
- Real production examples added (this section)
- Performance benchmarks documented (this section)

### Phase 3: Auto-Remediation (PENDING)
- Create `.ce/tool-alternatives.yml` (structured metadata)
- Integrate with `tools-misuse-scan` command
- Add `--remediate` mode for automatic fixes
- Link to CI/CD validation pipeline

### Phase 4: Continuous Monitoring (FUTURE)
- Pre-commit hook to catch violations early
- Agent training feedback loop
- Quarterly policy review
