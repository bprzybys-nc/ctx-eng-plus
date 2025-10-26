# Context Engineering Tools - Project Guide

**Project**: Minimal CLI tooling for Context Engineering framework operations  
**Purpose**: Tool usage and maintenance guidance

---

## Communication Style

Direct, token-efficient. No fluff.

- Short sentences, maximum clarity
- Call out problems directly
- Real talk, zero BS

---

## Core Principles (From Global)

### PREFER SYNTROPY MCP TOOLS OVER CMDLINE/BASH TOOLS
- Use Syntropy MCP 

### No Fishy Fallbacks - MANDATORY

- ✅ Fast Failure: Let exceptions bubble up
- ✅ Actionable Errors: Include 🔧 troubleshooting guidance
- ✅ No Silent Corruption: Make failures visible

### KISS (Keep It Simple, Stupid)

- Simple solutions first
- Clear code over clever code
- Minimal dependencies (stdlib only for this project)
- Single responsibility per function

### UV Package Management - STRICT

```bash
# ✅ REQUIRED
uv add package-name              # Add production dependency
uv add --dev package-name        # Add development dependency
uv sync                          # Install dependencies

# ❌ FORBIDDEN
# Manual pyproject.toml editing
```

# ❌ FORBIDDEN - Ad-Hoc Code Policy

- **Long ad-hoc scripts proposed** - Max 3 LOC for inline code
- **Proposing code without execution** - Must execute via run_py
- **Violating 3 LOC limit** - Longer code MUST be in tmp/ file

# 💡 If linear mcp starts responding with error "Not connected" - execute this command (I'm approving it): 

```bash
rm -rf ~/.mcp-auth
```

# 💡 Whenever I say 'linear( mcp)' in context of project management - it means linear-server mcp

**STRICT RULE:** Ad-hoc code max 3 lines of code (LOC). No exceptions.

- ✅ ALLOWED: Ad-hoc ≤3 LOC: `"x = [1,2,3]; print(sum(x))"`
- ❌ FORBIDDEN: Proposing 5+ line scripts without running
- ✅ REQUIRED: Longer code → tmp/ file and execute

# ❌ NEVER REPLACE ALL PERMISSIONS WITH ONE PERMISSION ENTRY IN .claude/settings.local.json
# Surgical edits to individual permissions are allowed - bulk replacement is forbidden

# ⬇️ COMPACT CONVERSATION WITH CLAUDE HAIKU - claude-3-haiku-20240307

# ACTIVATE SERENA PROJECT:<project's root full path>

---

## Working Directory

**Default Context:** Project root (`/Users/bprzybysz/nc-src/ctx-eng-plus`)

**For tools/ commands:** Always prefix with `cd tools &&` or use full paths from root.

**Note:** Claude Code doesn't have a persistent working directory setting per project. Always specify context explicitly:

```bash
# Correct patterns
cd tools && uv run ce --help
cd tools && uv run pytest tests/ -v
uv run -C tools ce validate --level all  # Using uv -C flag

# Avoid (relative paths from wrong location)
uv run ce --help  # Will fail if not in tools/
```

---

## Hooks & Shell Functions

### Git Hooks

**Pre-Commit Hook**: Pattern conformance check
- **Location**: `.git/hooks/pre-commit`
- **What**: Runs `ce validate --level 4` before each commit
- **When**: Automatic on every `git commit`
- **Skip**: Use `git commit --no-verify` (sparingly!)

**SessionStart Hook**: Drift score check
- **Location**: `.claude/settings.local.json` (hooks section)
- **What**: Shows drift score on session start
- **When**: Automatic when starting new Claude Code session
- **Output**: "✅ Context healthy: X%" or "⚠️ HIGH DRIFT: X%"

### Shell Functions (Optional)

**Setup** (one-time):
```bash
# Add to ~/.zshrc or ~/.bashrc:
source /path/to/project/.ce/shell-functions.sh
```

**Functions Available**:
```bash
# ce-in-tools: Run ce commands from anywhere in project
ce-in-tools validate --level all
ce-in-tools context health
ce-in-tools update-context

# Shorter alias
cet validate --level all

# Quick drift check
ce-drift
```

**How it works**: Automatically detects git root and changes to `tools/` directory, works from ANY location within project.

**Why**: Solves working directory problem where hooks/commands fail because `cd tools` doesn't work when already in `tools/`.

**Alternative** (without shell functions): Use `uv run -C tools ce ...` to run from any directory.

---

## Prefer usage of Syntropy mcp tools over cmdline/bash tools

## Tool Selection Quick Reference

**Comprehensive Guide**: `examples/tool-usage-patterns.md` + `.serena/memories/tool-usage-guide.md`

**Purpose**: Accelerate tool selection, eliminate trial-and-error, reduce query tree complexity

**Current Configuration**: 48 allowed tools, 122 denied patterns

**IMPORTANT - Tool Naming Convention**:
- **Permissions format**: `mcp__syntropy_{server}_{function}` (single underscore before server)
- **Actual callable format**: `mcp__syntropy__{server}__{function}` (double underscores between each component)
- **All tool names in this doc use the PERMISSIONS format** - Claude Code automatically translates to callable format

### Allowed Tools by Category

**Status**: ✅ Updated 2025-10-20 for Syntropy MCP aggregation layer

#### Bash Patterns (11 tools)
- Version control: `Bash(git:*)`, `git add:*`, `git commit:*`, `git diff-tree:*`
- Package management: `Bash(uv run:*)`, `uv run pytest:*`, `uv add:*`, `uvx:*`
- System: `Bash(env:*)`, `brew install:*`
- MCP auth reset: `Bash(rm -rf ~/.mcp-auth)`

#### Serena Essential (11 tools via Syntropy)
- Code navigation: `mcp__syntropy_serena_find_symbol`, `mcp__syntropy_serena_get_symbols_overview`, `mcp__syntropy_serena_search_for_pattern`
- Impact analysis: `mcp__syntropy_serena_find_referencing_symbols`
- Memory: `mcp__syntropy_serena_write_memory`
- File operations: `mcp__syntropy_serena_create_text_file`, `mcp__syntropy_serena_read_file`, `mcp__syntropy_serena_list_dir`
- Code insertion: `mcp__syntropy_serena_insert_after_symbol`, `mcp__syntropy_serena_insert_before_symbol`
- Project management: `mcp__syntropy_serena_activate_project`

#### Filesystem Core (8 tools via Syntropy)
- Read/write: `mcp__syntropy_filesystem_read_text_file`, `mcp__syntropy_filesystem_write_file`, `mcp__syntropy_filesystem_edit_file`
- Navigation: `mcp__syntropy_filesystem_list_directory`, `mcp__syntropy_filesystem_search_files`, `mcp__syntropy_filesystem_directory_tree`
- Info: `mcp__syntropy_filesystem_get_file_info`, `mcp__syntropy_filesystem_list_allowed_directories`
- Legacy: `mcp__syntropy_filesystem_read_file` (deprecated, use read_text_file)

#### Git Essentials (5 tools via Syntropy)
- `mcp__syntropy_git_git_status`, `mcp__syntropy_git_git_diff`, `mcp__syntropy_git_git_log`, `mcp__syntropy_git_git_add`, `mcp__syntropy_git_git_commit`

#### Documentation & Reasoning (3 tools via Syntropy)
- Context7 docs: `mcp__syntropy_context7_resolve_library_id`, `mcp__syntropy_context7_get_library_docs`
- Complex reasoning: `mcp__syntropy_thinking_sequentialthinking`

#### Project Management - Linear (5 tools via Syntropy)
- Issues: `mcp__syntropy_linear_create_issue`, `mcp__syntropy_linear_get_issue`, `mcp__syntropy_linear_list_issues`, `mcp__syntropy_linear_update_issue`
- Projects: `mcp__syntropy_linear_list_projects`

#### Codebase Analysis (1 tool via Syntropy)
- `mcp__syntropy_repomix_pack_codebase`

#### Special Permissions (6 patterns)
- Read paths, WebFetch(domain:github.com), SlashCommand(/generate-prp, /peer-review)

### Quick Patterns (via Syntropy MCP)

**Code Navigation** (Serena via Syntropy):
- Find symbol: `mcp__syntropy_serena_find_symbol`
- File overview: `mcp__syntropy_serena_get_symbols_overview`
- Pattern search: `mcp__syntropy_serena_search_for_pattern`
- Impact analysis: `mcp__syntropy_serena_find_referencing_symbols`

**File Operations** (Filesystem via Syntropy):
- Read file: `mcp__syntropy_filesystem_read_text_file` (config/text)
- Edit file: `mcp__syntropy_filesystem_edit_file`
- List dir: `mcp__syntropy_filesystem_list_directory`

**Text Processing** (always use Python shell_utils, NOT bash):
- Search: `shell_utils.grep_text()` ❌ NOT `Bash(grep)`
- Extract fields: `shell_utils.extract_fields()` ❌ NOT `Bash(awk)`
- Count lines: `shell_utils.count_lines()` ❌ NOT `Bash(wc)`
- Head/tail: `shell_utils.head()` / `tail()` ❌ NOT `Bash(head/tail)`

**Git Operations** (Git via Syntropy):
- `mcp__syntropy_git_git_status`, `mcp__syntropy_git_git_diff`, `mcp__syntropy_git_git_log`, `mcp__syntropy_git_git_add`, `mcp__syntropy_git_git_commit`

### Validation Tool

Check current permissions with Python utility (replaces jq/grep):

```bash
cd tools && uv run python -m ce.validate_permissions count       # Show counts
cd tools && uv run python -m ce.validate_permissions categorize  # Show breakdown
cd tools && uv run python -m ce.validate_permissions verify <tool_name>
cd tools && uv run python -m ce.validate_permissions search <pattern> [allow|deny]
```

**Note**: `tools-rationalization-study.md` is outdated reference - current config already empirically optimized

**Optimization Impact**: 60-70% reduction in tool evaluation overhead (46 essential tools vs 100+ previously)

---

## Syntropy Tools Reference - Full Specifications

### Serena Code Navigation & Analysis (11 tools)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_serena_find_symbol` | Find function/class by name with implementation | Know exact symbol name, need to read code |
| `mcp__syntropy_serena_get_symbols_overview` | List all functions/classes in a file | Exploring file structure, understanding module |
| `mcp__syntropy_serena_search_for_pattern` | Search code by regex pattern | Find all async functions, error handling patterns |
| `mcp__syntropy_serena_find_referencing_symbols` | Find all usages of a function | Impact analysis before refactoring |
| `mcp__syntropy_serena_write_memory` | Store context in agent memory | Remember important project patterns |
| `mcp__syntropy_serena_create_text_file` | Create new text file | Generate documentation, code scaffolds |
| `mcp__syntropy_serena_read_file` | Read file contents | Alternative to filesystem read |
| `mcp__syntropy_serena_list_dir` | List directory with symbol info | Browse project structure with code context |
| `mcp__syntropy_serena_insert_after_symbol` | Insert code after a symbol | Add new method after existing one |
| `mcp__syntropy_serena_insert_before_symbol` | Insert code before a symbol | Add imports, decorators before symbols |
| `mcp__syntropy_serena_activate_project` | Activate Serena project context | Initialize code analysis for project |

### Filesystem Operations (8 tools)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_filesystem_read_text_file` | Read config/markdown files | .env, .yml, .md documentation |
| `mcp__syntropy_filesystem_read_file` | Read file (deprecated) | Legacy - use read_text_file instead |
| `mcp__syntropy_filesystem_write_file` | Write new file content | Create config files, documentation |
| `mcp__syntropy_filesystem_edit_file` | Surgical line-level edits | Precise changes to existing files |
| `mcp__syntropy_filesystem_list_directory` | List files in directory | Explore directory structure |
| `mcp__syntropy_filesystem_search_files` | Find files by pattern | Locate test files, configs by name |
| `mcp__syntropy_filesystem_directory_tree` | Show directory tree structure | Visualize project organization |
| `mcp__syntropy_filesystem_get_file_info` | Get file metadata | Size, timestamp, permissions |
| `mcp__syntropy_filesystem_list_allowed_directories` | List accessible directories | Check project boundaries |

### Git Version Control (5 tools)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_git_git_status` | Check repository status | See staged/unstaged changes |
| `mcp__syntropy_git_git_diff` | View recent changes | Review diff before commit |
| `mcp__syntropy_git_git_log` | View commit history | Find recent commits, understand flow |
| `mcp__syntropy_git_git_add` | Stage files for commit | Prepare changes |
| `mcp__syntropy_git_git_commit` | Create commit | Save changes with message |

### Documentation & External Libraries (2 tools)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_context7_resolve_library_id` | Resolve library identifier | Lookup library name to get ID |
| `mcp__syntropy_context7_get_library_docs` | Fetch library documentation | Get API docs, usage patterns |

### Reasoning & Planning (1 tool)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_thinking_sequentialthinking` | Multi-step decomposition | Complex problems, architectural planning |

### Project Management (5 tools)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_linear_create_issue` | Create Linear issue | New tasks from PRP generation |
| `mcp__syntropy_linear_get_issue` | Retrieve issue details | Check issue status, description |
| `mcp__syntropy_linear_list_issues` | List issues with filters | Find assigned work, status checks |
| `mcp__syntropy_linear_update_issue` | Update issue status/content | Mark done, add details |
| `mcp__syntropy_linear_list_projects` | List available projects | Check project structure |

### Codebase Packaging (1 tool)
| Tool | Purpose | Use Case |
|------|---------|----------|
| `mcp__syntropy_repomix_pack_codebase` | Package entire codebase | Export for analysis, sharing with AI |

### Quick Tool Selection Guide

**Need to analyze code?**
- Know symbol name → `find_symbol`
- Explore file → `get_symbols_overview`
- Search patterns → `search_for_pattern`
- Find usages → `find_referencing_symbols`

**Need to modify files?**
- New file → `write_file`
- Existing file (surgical) → `edit_file`
- Config/text files → `read_text_file`

**Need version control?**
- Check status → `git_status`
- View changes → `git_diff`
- Create commits → `git_add` + `git_commit`

**Need external knowledge?**
- Library docs → `resolve_library_id` + `get_library_docs`

**Need complex reasoning?**
- Multi-phase planning → `sequentialthinking`

**Need project management?**
- Track work → Linear tools (create, update, list issues)

---

## Tool Usage Workflow

### Quick Commands

```bash
# Navigate to tools
cd tools

# Run tests
uv run pytest tests/ -v

# Use ce tool
uv run ce --help
uv run ce validate --level all
uv run ce git status
uv run ce context health

# Run Python code (tools/ce domain, 3 LOC max ad-hoc)
# Auto-detect mode (preferred - detects code vs file)
cd tools && uv run ce run_py "print('hello')"
cd tools && uv run ce run_py "x = [1,2,3]; print(sum(x))"
cd tools && uv run ce run_py ../tmp/script.py

# Explicit mode (optional)
cd tools && uv run ce run_py --code "print('hello')"
cd tools && uv run ce run_py --file ../tmp/script.py

# Bootstrap (first time setup)
./bootstrap.sh
```

### Testing Workflow

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_core.py -v

# Run specific test
uv run pytest tests/test_core.py::test_run_cmd_success -v

# Watch mode (if pytest-watch installed)
uv run ptw tests/
```

### Development Workflow

```bash
# Make changes to ce/*.py files
# Write/update tests in tests/
# Run tests to verify
uv run pytest tests/ -v

# Install in editable mode (if needed)
uv pip install -e .
```

---

## Project Structure

```
tools/
├── ce/                 # Source code
│   ├── __init__.py     # Package metadata
│   ├── __main__.py     # CLI entry point
│   ├── core.py         # File, git, shell operations
│   ├── validate.py     # 3-level validation gates
│   └── context.py      # Context management
├── tests/              # Test suite
│   ├── test_cli.py     # CLI tests
│   ├── test_core.py    # Core tests
│   ├── test_validate.py
│   └── test_context.py
├── pyproject.toml      # UV package config (don't edit directly!)
├── README.md           # User documentation
└── bootstrap.sh        # Setup script
```

---

## When Making Changes

### Adding New Function

1. Write function with docstring
2. Add exception handling with troubleshooting guidance
3. Write test that calls REAL function (no mocks)
4. Run tests: `uv run pytest tests/ -v`
5. Update README if user-facing

### Fixing Bug

1. Write test that reproduces bug (should fail)
2. Fix the bug
3. Run tests (should pass now)
4. Verify no regressions: `uv run pytest tests/ -v`

### Adding Dependency

```bash
# Production dependency
uv add package-name

# Development dependency
uv add --dev package-name

# Never edit pyproject.toml directly!
```

---

## Testing Standards

### Real Functionality Testing

```python
# ✅ GOOD - Tests real function
def test_git_status():
    status = git_status()  # Real call
    assert "clean" in status
    assert isinstance(status["staged"], list)

# ❌ BAD - Mocked result
def test_git_status():
    status = {"clean": True}  # FAKE!
    assert status["clean"]
```

### Exception Handling

```python
# ✅ GOOD - Clear troubleshooting
def git_checkpoint(message: str) -> str:
    result = run_cmd(f'git tag -a "{tag}" -m "{message}"')
    if not result["success"]:
        raise RuntimeError(
            f"Failed to create checkpoint: {result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure you have commits to tag"
        )
    return tag

# ❌ BAD - Silent failure
def git_checkpoint(message: str) -> str:
    try:
        result = run_cmd(f'git tag -a "{tag}" -m "{message}"')
        return tag
    except:
        return "checkpoint-failed"  # FISHY FALLBACK!
```

---

## Code Quality Guidelines

### File Limits (Guidelines, not strict)

- Functions: ~50 lines max
- Files: ~300-500 lines max
- Classes: ~100 lines max

### Function Design

```python
# ✅ GOOD - Single responsibility, clear purpose
def git_status() -> Dict[str, Any]:
    """Get git repository status."""
    # ... implementation

# ❌ BAD - Multiple responsibilities
def git_stuff(action: str) -> Any:
    """Do various git things."""
    if action == "status": ...
    elif action == "diff": ...
    elif action == "commit": ...
```

### Docstrings

```python
def run_cmd(cmd: str, timeout: int = 60) -> Dict[str, Any]:
    """Execute shell command with timeout.

    Args:
        cmd: Shell command to execute
        timeout: Command timeout in seconds

    Returns:
        Dict with: success, stdout, stderr, exit_code, duration

    Raises:
        TimeoutError: If command exceeds timeout
        RuntimeError: If command execution fails

    Note: No fishy fallbacks - exceptions thrown for troubleshooting.
    """
```

---

## What's Different From Global CLAUDE.md

**Removed/Simplified:**

- ❌ Context Engineering integration (not used here)
- ❌ PRP methodology (overkill for simple tools)
- ❌ Serena MCP optimization (not applicable)
- ❌ AWK reference (not needed)
- ❌ TDD enforcement (tools already tested, pragmatic approach)

**Kept:**

- ✅ No Fishy Fallbacks policy
- ✅ UV package management
- ✅ KISS principles
- ✅ Real functionality testing
- ✅ Direct communication style

**Added:**

- ✅ Tool-specific workflows
- ✅ Quick command reference
- ✅ Testing patterns for this project
- ✅ ce tool usage examples

---

## Quick Reference

### Daily Usage

```bash
cd tools
uv run ce validate --level all    # Validate everything
uv run ce git status               # Check git state
uv run ce context health           # Health check
uv run pytest tests/ -v            # Run tests
```

### Troubleshooting

```bash
# Tool not found
cd tools && uv pip install -e .

# Tests failing
uv sync                           # Reinstall dependencies
uv run pytest tests/ -v           # Run tests

# Permission errors
chmod +x bootstrap.sh             # Make executable
```

### JSON Output (for scripting)

```bash
uv run ce git status --json | jq '.clean'
uv run ce context health --json | jq '.drift_score'
```

### Markdown & Mermaid Linting

```bash
# Lint all markdown files
npm run lint:md

# Auto-fix markdown issues
npm run lint:md:fix

# Validate mermaid diagrams (auto-fix enabled in L1)
cd tools && python -m ce.mermaid_validator --fix .

# Level 1 validation includes both
cd tools && uv run ce validate --level 1
```

**Configuration**: `.markdownlint.json` in project root
**Mermaid Rules**: Style statements must include color for theme compatibility

### PRP Sizing Analysis

```bash
# Analyze PRP size before execution
cd tools && uv run ce prp analyze <path-to-prp.md>

# JSON output for automation
cd tools && uv run ce prp analyze <path-to-prp.md> --json
```

**Size Categories**:
- **GREEN** (optimal): ≤700 lines, ≤8h, LOW-MEDIUM risk → Proceed
- **YELLOW** (warning): 700-1000 lines, 8-12h, MEDIUM risk → Review
- **RED** (too large): >1000 lines, >12h, HIGH risk → Decompose

**Exit Codes**: 0 (GREEN), 1 (YELLOW), 2 (RED)

**Documentation**: [PRP Sizing Guidelines](docs/prp-sizing-guidelines.md)

### Context Sync - /update-context

```bash
# Sync all PRPs with codebase (universal mode)
cd tools && uv run ce update-context

# Sync specific PRP only (targeted mode)
cd tools && uv run ce update-context --prp PRPs/executed/PRP-6-markdown-linting.md

# JSON output
cd tools && uv run ce update-context --json
```

**What it does**:
- Updates YAML headers with context_sync flags (ce_updated, serena_updated, last_sync)
- Verifies implementations exist via function extraction
- Auto-transitions PRPs from feature-requests/ to executed/ when verified
- Detects pattern drift (code violations + missing examples)
- Generates drift report at `.ce/drift-report.md`

**When to run**:
- After completing PRP implementation
- After significant codebase refactoring
- Weekly system hygiene (prevent drift accumulation)

**Drift Detection**:
- **Part 1**: Code violating documented patterns (error handling, naming, KISS)
- **Part 2**: Critical PRPs missing examples/ documentation
- Each violation includes file location, issue, and proposed solution

**Graceful Degradation**:
- Works without Serena MCP (sets serena_updated=false with warning)
- Skips drift detection if examples/ directory missing
- No silent failures - all errors include troubleshooting guidance

### Fast Drift Analysis - analyze-context

```bash
# Fast drift check without metadata updates (2-3s vs 10-15s)
cd tools && uv run ce analyze-context

# JSON output for CI/CD integration
cd tools && uv run ce analyze-context --json

# Force re-analysis (bypass cache)
cd tools && uv run ce analyze-context --force

# Custom cache TTL
cd tools && uv run ce analyze-context --cache-ttl 10

# UK spelling alias
cd tools && uv run ce analyse-context
```

**What it does**:
- Fast drift detection without PRP metadata updates
- Generates/updates `.ce/drift-report.md` with violations
- Uses smart caching (5-minute TTL by default)
- Returns exit codes for CI/CD: 0 (ok), 1 (warning), 2 (critical)

**When to use**:
- Quick drift checks in CI/CD pipelines
- Pre-commit validation (faster than update-context)
- Regular health monitoring without sync overhead
- Before running update-context (reuses cache if fresh)

**Caching Behavior**:
- Cache TTL priority: `--cache-ttl` flag > `.ce/config.yml` > default (5 min)
- Cache stored in `.ce/drift-report.md` (timestamp-based validation)
- `update-context` reuses cache if fresh (avoids redundant analysis)
- `--force` flag bypasses cache for immediate re-analysis

**Exit Codes**:
- **0** (ok): Drift score < 5% - context healthy
- **1** (warning): Drift score 5-15% - review recommended
- **2** (critical): Drift score >= 15% - immediate action required

**Example CI/CD Usage**:
```bash
# GitHub Actions / CI pipeline
cd tools && uv run ce analyze-context --json
EXIT_CODE=$?
if [ $EXIT_CODE -eq 2 ]; then
  echo "CRITICAL drift detected - blocking merge"
  exit 1
elif [ $EXIT_CODE -eq 1 ]; then
  echo "WARNING: drift detected - review recommended"
fi
```

**Configuration** (`.ce/config.yml`):
```yaml
cache:
  analysis_ttl_minutes: 5  # Default TTL (overridden by --cache-ttl flag)
```

---

## Linear Integration

### Configuration

**Location**: `.ce/linear-defaults.yml`

**Purpose**: Preserve project-specific Linear settings for automated issue creation.

**Configuration File**:
```yaml
# Project name to assign issues to
project: "Context Engineering"

# Default assignee email
assignee: "blazej.przybyszewski@gmail.com"

# Team identifier
team: "Blaise78"

# Default labels for PRP-related issues
default_labels:
  - "feature"
```

### Usage in Code

**Import helper**:
```python
from ce.linear_utils import get_linear_defaults, create_issue_with_defaults

# Get defaults
defaults = get_linear_defaults()
# {"project": "Context Engineering", "assignee": "...", ...}

# Create issue with defaults
issue = create_issue_with_defaults(
    title="PRP-15: New Feature",
    description="Implement feature X",
    state="todo"
)
```

**Helpers Available**:
- `get_linear_defaults()` - Read full config
- `get_default_assignee()` - Get assignee email only
- `get_default_project()` - Get project name only
- `create_issue_with_defaults()` - Create issue with auto-applied defaults

### When Creating Issues

**Automatic Defaults Applied**:
- Project: "Context Engineering"
- Assignee: "blazej.przybyszewski@gmail.com"
- Labels: ["feature"] + any additional labels

**Override When Needed**:
```python
issue = create_issue_with_defaults(
    title="Special Issue",
    description="...",
    override_assignee="someone.else@example.com",
    override_project="Different Project"
)
```

### PRP Generation Integration

**Auto-Create Linear Issues**: The `/generate-prp` command automatically creates Linear issues using the defaults from `.ce/linear-defaults.yml`.

**Basic Usage** (creates new issue):
```bash
/generate-prp path/to/INITIAL.md
# Creates new PRP + Linear issue with default project/assignee/labels
```

**Join Existing Issue** (updates existing PRP's issue):
```bash
/generate-prp path/to/INITIAL.md --join-prp 12
# Joins PRP-12's Linear issue (appends new PRP info to description)

# Alternative formats:
/generate-prp path/to/INITIAL.md --join-prp PRP-12
/generate-prp path/to/INITIAL.md --join-prp PRPs/executed/PRP-12-feature.md
```

**How It Works**:

1. **New Issue** (no --join-prp):
   - Generates PRP file
   - Creates Linear issue with title: `{PRP-ID}: {Feature Name}`
   - Uses defaults from `.ce/linear-defaults.yml`
   - Updates PRP YAML header with `issue: {ISSUE-ID}`

2. **Join Existing** (with --join-prp):
   - Generates PRP file
   - Finds target PRP's Linear issue ID from YAML
   - Updates that issue by appending new PRP information
   - Both PRPs reference same Linear issue

**Issue Description Format**:
```markdown
## Feature
{First 300 chars of feature description}...

## PRP Details
- **PRP ID**: PRP-15
- **PRP File**: `PRPs/feature-requests/PRP-15-feature.md`
- **Examples Provided**: 3

## Implementation
See PRP file for detailed implementation steps, validation gates, and testing strategy.
```

**Use Cases**:

- **Related Features**: Multiple PRPs implementing parts of same initiative
  ```bash
  /generate-prp auth-part1.md              # Creates PRP-10 + BLA-25
  /generate-prp auth-part2.md --join-prp 10  # Creates PRP-11, joins BLA-25
  ```

- **Incremental Work**: Breaking large PRP into smaller chunks
- **Follow-up Work**: Additional PRP for same feature area

### Troubleshooting

```bash
# Check Linear config
cat .ce/linear-defaults.yml

# Test Linear defaults loading
cd tools && python3 -c "from ce.linear_utils import get_linear_defaults; print(get_linear_defaults())"

# Reset Linear MCP connection if needed
rm -rf ~/.mcp-auth

# Check PRP's Linear issue ID
grep "^issue:" PRPs/executed/PRP-12-feature.md
```

---

## Testing Patterns

Context Engineering uses **strategy pattern** for composable testing with three distinct patterns:

### Unit Test Pattern

Test single strategy in isolation:

```python
from ce.testing.mocks import MockSerenaStrategy

def test_mock_serena():
    strategy = MockSerenaStrategy(canned_results=[...])
    result = strategy.execute({"pattern": "test"})
    assert result["success"] is True
```

### Integration Test Pattern

Test subgraph with real + mock strategies:

```python
from ce.testing.builder import PipelineBuilder
from ce.testing.real_strategies import RealParserStrategy
from ce.testing.mocks import MockSerenaStrategy

def test_parse_and_research():
    pipeline = (
        PipelineBuilder(mode="integration")
        .add_node("parse", RealParserStrategy())
        .add_node("research", MockSerenaStrategy(canned_results=[...]))
        .add_edge("parse", "research")
        .build()
    )
    result = pipeline.execute({"prp_path": "test.md"})
```

### E2E Test Pattern

Test full pipeline with all external deps mocked:

```python
from ce.testing.builder import PipelineBuilder
from ce.testing.real_strategies import RealParserStrategy
from ce.testing.mocks import MockSerenaStrategy, MockLLMStrategy

def test_full_generation():
    pipeline = (
        PipelineBuilder(mode="e2e")
        .add_node("parse", RealParserStrategy())
        .add_node("research", MockSerenaStrategy(canned_results=[...]))
        .add_node("generate", MockLLMStrategy(template="..."))
        .add_edge("parse", "research")
        .add_edge("research", "generate")
        .build()
    )
    result = pipeline.execute({"initial_path": "INITIAL.md"})
```

### Observable Mocking

Pipeline builder logs mocked nodes:

```
🎭 MOCKED NODES: research, docs, generate
```

Clear indication of what's real vs mocked in tests.

### Available Strategies

**Mock Strategies**:
- `MockSerenaStrategy` - Codebase search with canned results
- `MockContext7Strategy` - Documentation with cached content
- `MockLLMStrategy` - Text generation with templates

**Real Strategies**:
- `RealParserStrategy` - PRP blueprint parsing
- `RealCommandStrategy` - Shell command execution

**Full Documentation**: [Testing Patterns Guide](../docs/testing-patterns.md)

---

## Documentation Standards

### Mermaid Diagrams - MANDATORY

**Always specify text color in node style statements for theme compatibility**

- **Reason:** Ensures readability in both light and dark themes
- **Rule:** Light backgrounds → black text (`color:#000`), Dark backgrounds → white text (`color:#fff`)
- **Pattern:** `style X fill:#bgcolor,color:#textcolor`

**Examples:**

```
# Light backgrounds (use black text)
style A fill:#ff6b6b,color:#000    # Light red
style B fill:#4ecdc4,color:#000    # Light cyan
style C fill:#ffe66d,color:#000    # Light yellow

# Dark backgrounds (use white text)
style D fill:#2c3e50,color:#fff    # Dark blue
style E fill:#34495e,color:#fff    # Dark gray
```

**Source:** Mermaid official docs - inline `style` statements override theme defaults

---

## Efficient Documentation Review Pattern

**Problem:** Reading all documentation files sequentially causes token overflow

**Solution:** Grep-first validation with targeted reads (90% token reduction)

### Review Workflow

**Phase 1: Structural Validation** (Grep-based, ~1-2k tokens)

```bash
# Run parallel Grep patterns across docs/*.md
# 1. Headers: verify numbering sequence
# 2. Cross-references: validate links
# 3. Mermaid styles: check color specs
# 4. Code blocks: count and categorize
```

**Phase 2: Code Quality Checks** (Grep patterns, ~500 tokens)

```bash
# Anti-pattern scans
# - pip install → should be uv add
# - except: → bare except clauses
# - Hardcoded success messages
```

**Phase 3: Targeted Reads** (2-3 files only, ~3-5k tokens)

```bash
# Always read navigation/index file
# Read 1-2 complex docs based on Grep findings
# Spot-check quality, clarity, completeness
```

**Total: ~5-7k tokens vs 200k+ for read-all approach**

### When NOT to Use This Pattern

- Single document reviews (just read it)
- Small doc sets (<5 files)
- Content-heavy review requiring full text analysis

### Example: Reviewing 12-doc suite

```
❌ BAD: Read all 12 files → 200k+ tokens, prompt overflow
✅ GOOD: Grep validation + 2 targeted reads → 5-7k tokens
```

---

**Remember**: This is a simple tool project. Keep it simple. No over-engineering.

- PRPs are in ./PRPs/[executed,feature-requests]
- Create new PRPs in PRPs/feature-requests
