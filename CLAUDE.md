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
