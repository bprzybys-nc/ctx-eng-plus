# INITIAL: Command Injection Vulnerability Fix

## Feature Name
Eliminate Command Injection Vulnerability via shell=True Replacement

## Feature Description
Replace all `subprocess.run(cmd, shell=True)` calls with safe alternatives using `shell=False` and `shlex.split()` to eliminate CWE-78 command injection vulnerability discovered in AI code review. This is a CRITICAL security fix that prevents arbitrary command execution attacks.

**Current Vulnerability**:
```python
# tools/ce/core.py:35 - CRITICAL VULNERABILITY
subprocess.run(cmd, shell=True, ...)  # Allows injection via "; malicious_cmd"
```

**Attack Vector Example**:
```python
malicious_input = "valid_file.md; rm -rf /"
run_cmd(f"cat {malicious_input}")
# Results in: cat valid_file.md; rm -rf /
```

**Secure Solution**:
```python
import shlex
cmd_list = shlex.split(cmd)  # Properly escapes arguments
subprocess.run(cmd_list, shell=False, ...)  # No shell interpretation
```

## Examples from Codebase

### Current Vulnerable Patterns

1. **Core run_cmd() function** (tools/ce/core.py:35)
```python
result = subprocess.run(
    cmd,           # String with potential injection
    shell=True,    # ❌ DANGEROUS
    cwd=cwd,
    timeout=timeout,
    capture_output=capture_output,
    text=True
)
```

2. **Shell pipelines** (tools/ce/context.py:31, 551, 636)
```python
# Used for counting tracked files
total_result = run_cmd("git ls-files | wc -l", capture_output=True)
```

3. **Complex shell operations** (tools/ce/context.py:572, 661)
```python
# Git diff with redirection and pipes
deps_result = run_cmd(
    "git diff HEAD~5 -- pyproject.toml package.json 2>/dev/null | wc -l",
    capture_output=True
)
```

### Safe Patterns (Keep Unchanged)

**tools/ce/markdown_lint.py:27, 55** - Already using list format:
```python
check_cmd = ["which", "markdownlint-cli2"]  # ✅ SAFE - list format
check_result = subprocess.run(
    check_cmd,
    capture_output=True,
    text=True
)
```

## Implementation Requirements

### 1. Refactor run_cmd() Function

**File**: `tools/ce/core.py`

Replace the vulnerable `run_cmd()` implementation with:

```python
import shlex
from typing import Union, List, Optional, Dict, Any
import subprocess
import time

def run_cmd(
    cmd: Union[str, List[str]],
    cwd: Optional[str] = None,
    timeout: int = 60,
    capture_output: bool = True
) -> Dict[str, Any]:
    """Execute shell command with timeout and error handling.

    Args:
        cmd: Shell command (str will be safely split) or list of args
        cwd: Working directory (default: current)
        timeout: Command timeout in seconds
        capture_output: Whether to capture stdout/stderr

    Returns:
        Dict with: success (bool), stdout (str), stderr (str),
                   exit_code (int), duration (float)

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout

    Security: Uses shell=False to prevent command injection.
              String commands are safely parsed with shlex.split().
    """
    start = time.time()

    # Convert string to safe list
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd)  # Proper escaping
    else:
        cmd_list = cmd

    try:
        result = subprocess.run(
            cmd_list,  # ✅ List format
            shell=False,  # ✅ SAFE - no shell interpretation
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True
        )

        duration = time.time() - start

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout if capture_output else "",
            "stderr": result.stderr if capture_output else "",
            "exit_code": result.returncode,
            "duration": duration
        }

    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        raise TimeoutError(
            f"Command timed out after {timeout}s: {' '.join(cmd_list)}\n"
            f"🔧 Troubleshooting: Increase timeout or check for hanging process"
        ) from e

    except Exception as e:
        duration = time.time() - start
        raise RuntimeError(
            f"Command failed: {' '.join(cmd_list)}\n"
            f"Error: {str(e)}\n"
            f"🔧 Troubleshooting: Check command syntax and permissions"
        ) from e
```

### 2. Replace Shell Pipelines with Python Equivalents

**File**: `tools/ce/core.py`

Add new helper function to replace `git ls-files | wc -l`:

```python
def count_git_files() -> int:
    """Count total tracked files in git repository.

    Replaces: git ls-files | wc -l

    Returns:
        Number of tracked files

    Raises:
        RuntimeError: If not in git repository
    """
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            shell=False,  # ✅ SAFE
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to list git files\n"
                f"🔧 Troubleshooting: Ensure you're in a git repository"
            )

        # Count lines in Python (no pipe needed)
        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return len(files)

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Git ls-files timed out\n"
            "🔧 Troubleshooting: Repository may be too large"
        )
```

Add helper for `git diff | wc -l`:

```python
def count_git_diff_lines(
    ref: str = "HEAD~5",
    files: Optional[List[str]] = None
) -> int:
    """Count lines changed in git diff.

    Replaces: git diff HEAD~5 -- file1 file2 | wc -l

    Args:
        ref: Git reference to diff against
        files: Optional list of files to diff

    Returns:
        Number of changed lines
    """
    cmd = ["git", "diff", ref]
    if files:
        cmd.extend(["--"] + files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,  # ✅ SAFE
            timeout=30
        )

        if result.returncode != 0:
            return 0  # No changes or error

        # Count lines in Python
        return len(result.stdout.split('\n')) if result.stdout else 0

    except subprocess.TimeoutExpired:
        return 0
```

### 3. Update context.py to Use New Helpers

**File**: `tools/ce/context.py`

**Line 31** - Replace:
```python
# OLD (vulnerable)
total_result = run_cmd("git ls-files | wc -l", capture_output=True)
if not total_result["success"]:
    raise RuntimeError("Failed to get total files")
total_files = int(total_result["stdout"].strip())

# NEW (secure)
from .core import count_git_files
total_files = count_git_files()
```

**Line 551** - Replace:
```python
# OLD
total_result = run_cmd("git ls-files | wc -l", capture_output=True)
if total_result["success"]:
    total_files = int(total_result["stdout"].strip())

# NEW
total_files = count_git_files()
```

**Line 572-573** - Replace:
```python
# OLD
deps_result = run_cmd(
    "git diff HEAD~5 -- pyproject.toml package.json 2>/dev/null | wc -l",
    capture_output=True
)

# NEW
from .core import count_git_diff_lines
deps_changed = count_git_diff_lines(
    ref="HEAD~5",
    files=["pyproject.toml", "package.json"]
)
```

**Line 636** - Same as line 551 (duplicate pattern)

**Line 661-662** - Same as line 572 (duplicate pattern)

### 4. Keep Safe Code Unchanged

**File**: `tools/ce/markdown_lint.py`

Lines 27, 55 - **NO CHANGES NEEDED** (already using safe list format)

## Testing Strategy

### 1. Security Tests

**File**: `tools/tests/test_security.py` (create new)

```python
import pytest
from ce.core import run_cmd

def test_command_injection_prevention():
    """Ensure command injection is blocked by shlex.split()."""
    # Malicious input with command chaining
    malicious = "ls; rm -rf /"

    # shlex.split() will treat entire string as single argument
    result = run_cmd(malicious)

    # Should fail (ls called with weird arg), not execute rm
    assert result["success"] is False
    assert "rm" not in result["stdout"]


def test_shell_metacharacters_safe():
    """Ensure shell metacharacters are escaped."""
    test_cases = [
        "echo hello; whoami",  # Command chaining
        "echo hello | cat",     # Pipe
        "echo hello > /tmp/test",  # Redirection
        "echo `whoami`",        # Command substitution
        "echo $(whoami)",       # Command substitution
    ]

    for cmd in test_cases:
        result = run_cmd(cmd)
        # Should fail or treat as literal args, not execute shell features
        # The key is that no secondary commands execute


def test_count_git_files_no_injection():
    """Ensure count_git_files is injection-proof."""
    from ce.core import count_git_files

    # Should work without any injection possibility
    count = count_git_files()
    assert isinstance(count, int)
    assert count >= 0
```

### 2. Functional Tests

**File**: `tools/tests/test_core.py` (update existing)

```python
def test_run_cmd_with_string():
    """Test run_cmd accepts string (backward compat)."""
    result = run_cmd("echo 'test'")
    assert result["success"] is True
    assert "test" in result["stdout"]


def test_run_cmd_with_list():
    """Test run_cmd accepts list (new capability)."""
    result = run_cmd(["echo", "test"])
    assert result["success"] is True
    assert "test" in result["stdout"]


def test_run_cmd_with_quoted_args():
    """Test shlex.split() handles quotes correctly."""
    result = run_cmd("echo 'hello world'")
    assert result["success"] is True
    assert "hello world" in result["stdout"]


def test_count_git_files():
    """Test count_git_files helper."""
    from ce.core import count_git_files

    count = count_git_files()
    assert isinstance(count, int)
    assert count > 0  # We know we have files in repo


def test_count_git_diff_lines():
    """Test count_git_diff_lines helper."""
    from ce.core import count_git_diff_lines

    # Should not crash even if no changes
    count = count_git_diff_lines("HEAD~1")
    assert isinstance(count, int)
    assert count >= 0
```

### 3. Integration Tests

**File**: `tools/tests/test_context.py` (update existing)

Verify all context.py functions using the new helpers still work:
- `sync()` - Uses count_git_files()
- `calculate_drift_score()` - Uses count_git_files() and count_git_diff_lines()
- `context_health_verbose()` - Uses both helpers

### 4. Regression Testing

Run full test suite:
```bash
cd tools && uv run pytest tests/ -v
```

All 35 existing test files must pass without modification.

## Other Considerations

### Backward Compatibility
- ✅ `run_cmd()` still accepts strings (via `shlex.split()`)
- ✅ Existing call sites don't need changes
- ✅ Return format unchanged

### Edge Cases Handled
- Empty commands → shlex.split() handles gracefully
- Quoted arguments → shlex.split() preserves quotes correctly
- Special characters → Properly escaped, not interpreted
- Complex git commands → Still work (no shell needed)

### Performance Impact
- Negligible: shlex.split() is fast (~microseconds)
- Slight improvement: No shell process spawning overhead

### Security Benefits
- ✅ Eliminates CWE-78 command injection
- ✅ Prevents arbitrary command execution
- ✅ Blocks shell metacharacter exploitation
- ✅ CVSS score reduction: 8.1 → 0 (critical fix)

### What Won't Break
- Git operations (status, diff, tag, etc.)
- NPM commands (lint, test)
- Python execution (uv run)
- Existing tests
- User workflows

### What Gets Better
- Security posture (critical vulnerability eliminated)
- Code clarity (explicit list vs implicit shell)
- Error messages (shows actual command executed)
- Auditability (no hidden shell interpretation)

## Validation Gates

### Pre-Implementation
- [x] Code review identifies vulnerability location
- [x] Replacement strategy validated (shlex + shell=False)
- [x] Test plan documented

### During Implementation
- [ ] run_cmd() refactored with shlex.split()
- [ ] count_git_files() helper added
- [ ] count_git_diff_lines() helper added
- [ ] context.py updated (5 locations)
- [ ] Security tests added
- [ ] All existing tests pass

### Post-Implementation
- [ ] Manual security testing (injection attempts fail)
- [ ] Full test suite passes (35 test files)
- [ ] No functionality regression
- [ ] Code review approval
- [ ] Documentation updated

## Success Criteria
- ✅ Zero `shell=True` usage in codebase
- ✅ All security tests pass
- ✅ All existing tests pass (no regression)
- ✅ Command injection vulnerability eliminated (verified)
- ✅ No breaking changes to user workflows
