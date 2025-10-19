# update-context Comprehensive Reliability & Correctness Fix

## Feature

Fix 30+ critical bugs, logic errors, and design flaws in `tools/ce/update_context.py` to make context synchronization actually reliable and accurate.

**Current State**: update-context has fundamental issues:
- Drift scores are calculated incorrectly (wrong algorithm)
- Implementation verification is broken (disabled, always returns false)
- Pattern matching fails on multiline code (false negatives)
- File operations are not atomic (corruption risk)
- --remediate flag doesn't actually remediate (just generates PRP)

**Desired State**: Reliable, accurate context sync with:
- Correct drift calculation (violation-based, not file-based)
- Working implementation verification (AST parsing or MCP fix)
- Robust pattern matching (handles multiline, edge cases)
- Atomic file operations (safe on failure)
- True remediation automation (--remediate actually fixes issues)

## Context

### Problem Discovery

During PRP-20 execution and subsequent analysis, discovered that `update-context` has fundamental reliability issues that make drift detection unreliable and remediation non-functional.

**Evidence**:
1. PRP-20 showed "phantom violations" in drift report even after manual verification confirmed compliance
2. Drift score of 6.7% with only 2 actual violations (calculation is wrong)
3. Serena MCP verification permanently disabled with no fallback
4. --remediate generates PRP but doesn't execute it (misleading flag name)

### Root Causes

1. **Wrong Algorithm**: Drift score uses file count instead of violation count
2. **Disabled Feature**: Serena verification disabled due to MCP architecture (no fallback implemented)
3. **Regex Limitations**: Pattern matching uses single-line regex without DOTALL flag
4. **No Atomicity**: File writes use direct I/O without atomic rename
5. **Half-Baked Automation**: --remediate workflow stops at PRP generation

### Impact

- **User Trust**: False drift scores undermine confidence in tooling
- **Wasted Effort**: Developers chase phantom violations that don't exist
- **Silent Failures**: Disabled verification means PRPs marked "verified" when code doesn't exist
- **Data Corruption Risk**: Non-atomic writes can corrupt PRP YAML headers
- **Misleading UX**: --remediate flag doesn't do what users expect

## Examples

### CRITICAL Issue #1: Drift Score Calculation Wrong

**File**: `tools/ce/update_context.py`
**Line**: 1044

**Current Code**:
```python
# Calculate drift score
drift_score = 0.0
if python_files:
    drift_score = (len(files_with_violations) / len(python_files)) * 100
```

**Problem**:
- Uses **file count** (how many files have violations)
- Should use **violation count** (how many total violations found)

**Real-world example**:
```python
# Scenario 1: 1 file with 30 violations
files_with_violations = 1
python_files = 30
drift_score = (1 / 30) * 100 = 3.3%  # Shows as "OK" but should be CRITICAL

# Scenario 2: 30 files with 1 violation each
files_with_violations = 30
python_files = 30
drift_score = (30 / 30) * 100 = 100%  # Shows as CRITICAL but is just widespread

# Both scenarios should have similar scores!
```

**Correct Algorithm**:
```python
# Count total violations across all files
total_violations = len(violations)  # e.g., 30
total_checks = len(python_files) * len(all_pattern_checks)  # e.g., 30 files * 5 checks = 150
drift_score = (total_violations / total_checks) * 100  # 30 / 150 = 20%

# Or with weighting by severity:
severity_weights = {"bare_except": 10, "missing_troubleshooting": 5, "deep_nesting": 3}
weighted_violations = sum(severity_weights.get(v.type, 1) for v in violations)
max_score = total_checks * max(severity_weights.values())
drift_score = (weighted_violations / max_score) * 100
```

---

### CRITICAL Issue #2: Implementation Verification Broken

**File**: `tools/ce/update_context.py`
**Line**: 1524

**Current Code**:
```python
# Serena verification disabled (subprocess cannot access parent's stdio MCP)
serena_verified = False

# For now, mark CE as updated if functions found
ce_verified = len(expected_functions) > 0
```

**Problem**:
1. `serena_verified` is **always False** (feature completely disabled)
2. `ce_verified` only checks if **PRP mentions functions**, not if they **actually exist in codebase**

**Impact**:
```python
# PRP mentions: sync_context(), analyze_drift()
expected_functions = ["sync_context", "analyze_drift"]
ce_verified = True  # ✅ Marked as verified

# But what if those functions DON'T EXIST in tools/ce/?
# Current code doesn't check! FALSE POSITIVE!
```

**Root Cause**: MCP architecture limitation - Python subprocess can't access parent process's stdio MCP servers

**Solutions**:

**Option A**: Fix MCP integration (complex)
```python
# Use mcp-client library directly instead of subprocess
from mcp import Client
client = Client("serena")  # Connect to existing MCP server
result = client.call("find_symbol", {"name": "sync_context"})
serena_verified = result["success"]
```

**Option B**: Use AST parsing (simpler, no MCP needed)
```python
import ast
from pathlib import Path

def verify_functions_exist(expected: List[str]) -> bool:
    """Check if functions actually exist in tools/ce/ using AST."""
    tools_ce = Path("tools/ce")
    found_functions = set()

    for py_file in tools_ce.glob("*.py"):
        tree = ast.parse(py_file.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                found_functions.add(node.name)
            elif isinstance(node, ast.ClassDef):
                found_functions.add(node.name)

    return all(func in found_functions for func in expected)

# Usage:
ce_verified = verify_functions_exist(expected_functions)
```

---

### CRITICAL Issue #3: Pattern Regex Fails on Multiline

**File**: `tools/ce/update_context.py`
**Line**: 39

**Current Code**:
```python
PATTERN_CHECKS = {
    "error_handling": [
        ("bare_except", r"except:\s*$", "Use specific exception types"),
        ("missing_troubleshooting", r'raise \w+Error\([^🔧]+\)$', "Add 🔧 Troubleshooting guidance")
    ],
    # ...
}
```

**Problem**:
- `$` anchor requires **end of line** - fails on multiline raises
- `[^🔧]+` doesn't properly handle emoji in character class
- No `re.DOTALL` flag - dot doesn't match newlines

**False Negative Example**:
```python
# This error message HAS troubleshooting but regex MISSES it:
raise FileNotFoundError(
    f"File not found: {path}\n"
    f"🔧 Troubleshooting:\n"
    f"   - Check path is correct"
)
# Regex fails because:
# 1. $ expects end of line, but this continues on next line
# 2. [^🔧]+ stops at first line, doesn't look ahead to next lines
```

**False Positive Example**:
```python
# In docstring/comment - should NOT be flagged:
"""
Example of bad error handling:
    raise RuntimeError("No troubleshooting")
"""
# But regex MATCHES this and flags it as violation!
```

**Correct Regex**:
```python
import re

# Use re.DOTALL and proper multiline handling
pattern = r'raise\s+\w+Error\s*\([^)]*\)'  # Match the raise statement
# Then check if 🔧 appears anywhere in next 10 lines
def check_has_troubleshooting(code: str, match_pos: int) -> bool:
    lines = code[match_pos:].split('\n')[:10]  # Check next 10 lines
    return any('🔧' in line or 'Troubleshooting' in line for line in lines)

# Or use AST parsing to avoid docstrings:
def find_raises_without_troubleshooting(code: str) -> List[int]:
    tree = ast.parse(code)
    violations = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            # Check if exception message contains 🔧
            # (proper AST traversal, ignores comments/docstrings)
            pass
    return violations
```

---

### CRITICAL Issue #4: No Atomic File Operations

**File**: `tools/ce/update_context.py`
**Line**: 753

**Current Code**:
```python
# Write back
try:
    post = frontmatter.Post(content, **metadata)
    with open(file_path, 'w') as f:
        f.write(frontmatter.dumps(post))
```

**Problem**: Direct write to file - if process is killed mid-write, file is **corrupted**

**Failure Scenarios**:
```python
# Scenario 1: Disk full mid-write
with open("PRP-10.md", 'w') as f:
    f.write("---\nname: Foo\n")  # ✅ Written
    f.write("status: executed\n")  # ❌ DISK FULL - exception raised
# Result: PRP-10.md has incomplete YAML header - CORRUPTED

# Scenario 2: Process killed (SIGKILL)
with open("PRP-10.md", 'w') as f:
    f.write("---\nname: Foo\n")  # ✅ Written
    # Process killed here
# Result: PRP-10.md has incomplete content - CORRUPTED
```

**Atomic Write Solution**:
```python
import tempfile
import shutil
from pathlib import Path

def atomic_write(file_path: Path, content: str):
    """Write file atomically using temp file + rename."""
    # Write to temp file first
    temp_fd, temp_path = tempfile.mkstemp(
        dir=file_path.parent,
        prefix=f".{file_path.name}.",
        text=True
    )

    try:
        with os.fdopen(temp_fd, 'w') as f:
            f.write(content)
            f.flush()
            os.fsync(f.fileno())  # Force write to disk

        # Atomic rename (OS-level atomic operation)
        os.replace(temp_path, file_path)
    except:
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise

# Usage:
post = frontmatter.Post(content, **metadata)
atomic_write(file_path, frontmatter.dumps(post))
```

---

### CRITICAL Issue #5: --remediate Doesn't Actually Remediate

**File**: `tools/ce/update_context.py`
**Lines**: 408-485

**Current Code**:
```python
def remediate_drift_workflow(yolo_mode: bool = False):
    # ... detect drift ...
    # ... generate blueprint ...
    # ... generate PRP ...

    # Print next step (manual execution required!)
    print(f"Run: /execute-prp {prp_path}")
    return {"success": True, "prp_path": prp_path}
```

**Problem**: Flag is called `--remediate` but it **doesn't remediate**! It only generates a PRP.

**User Expectation** vs **Reality**:
```bash
# What user expects when running:
$ cd tools && uv run ce update-context --remediate
# Expected: Automatically FIX all drift violations
# Reality: Just creates a PRP file, still needs manual /execute-prp

# This is misleading! It's "half-automated"
```

**Impact**:
- **Misleading CLI**: Flag name suggests full automation
- **Manual Work Required**: User must still run /execute-prp separately
- **CI/CD Incompatible**: Can't use in automated pipelines

**Solution Options**:

**Option A**: Make --remediate actually remediate (full automation)
```python
def remediate_drift_workflow(yolo_mode: bool = False):
    # ... detect drift ...
    # ... generate PRP ...

    # ACTUALLY EXECUTE THE PRP
    from .execute import execute_prp
    result = execute_prp(prp_path)

    if not result["success"]:
        raise RuntimeError("Remediation failed")

    return {"success": True, "fixed_violations": result["fixes"]}
```

**Option B**: Rename flag to match behavior (documentation fix)
```bash
# Rename --remediate to --generate-remediation-prp
$ cd tools && uv run ce update-context --generate-remediation-prp
# Now expectations match reality
```

---

### HIGH Issue #6: Cache TTL Inconsistency

**Files**: `tools/ce/update_context.py`
**Lines**: 1278-1307 (get_cache_ttl function exists), 1546 (hardcoded 5 in sync_context)

**Problem**: Cache TTL is configurable via `get_cache_ttl()` but `sync_context()` hardcodes 5 minutes

**Code**:
```python
# Line 1278: Function exists to get configurable TTL
def get_cache_ttl(cli_ttl: Optional[int] = None) -> int:
    """Get cache TTL from CLI arg, config, or default."""
    if cli_ttl is not None:
        return cli_ttl
    # Check .ce/config.yml ...
    return 5  # Default

# Line 1546: But sync_context() ignores it!
if cached and is_cache_valid(cached, ttl_minutes=5):  # ❌ Hardcoded!
```

**Fix**:
```python
# In sync_context():
cache_ttl = get_cache_ttl()  # Respect config
if cached and is_cache_valid(cached, ttl_minutes=cache_ttl):
```

---

### HIGH Issue #7: extract_expected_functions() Incomplete

**File**: `tools/ce/update_context.py`
**Lines**: 882-906

**Missing Patterns**:
```python
# Current patterns:
# ✅ `function_name()` - backtick references
# ✅ def function_name() - function definitions
# ✅ class ClassName - class definitions

# ❌ MISSING:
# 1. Decorators
@property
def foo():
    pass

# 2. Async functions
async def fetch_data():
    pass

# 3. Class methods
class Foo:
    @classmethod
    def bar(cls):
        pass

# 4. Static methods
class Foo:
    @staticmethod
    def baz():
        pass

# 5. Generator functions
def process():
    yield item

# 6. Lambda functions
handler = lambda x: x * 2

# 7. Nested functions
def outer():
    def inner():
        pass
```

**Solution**: Use AST parsing instead of regex

```python
import ast

def extract_expected_functions_ast(content: str) -> List[str]:
    """Extract ALL callable names from PRP using AST."""
    functions = set()

    # Parse markdown code blocks
    code_blocks = re.findall(r'```python\n(.*?)```', content, re.DOTALL)

    for code in code_blocks:
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                # Functions
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.add(node.name)
                # Classes
                elif isinstance(node, ast.ClassDef):
                    functions.add(node.name)
                    # Add methods
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            functions.add(item.name)
        except SyntaxError:
            continue  # Skip malformed code blocks

    return sorted(list(functions))
```

---

### HIGH Issue #8: PATTERN_CHECKS Hardcoded

**File**: `tools/ce/update_context.py`
**Lines**: 32-45

**Problem**: Pattern checks are hardcoded dict - can't add custom patterns without code edit

**Current**:
```python
PATTERN_CHECKS = {
    "error_handling": [
        ("bare_except", r"except:\s*$", "Use specific exception types"),
        # ... hardcoded ...
    ]
}
```

**Impact**:
- **Not Extensible**: Adding new pattern requires code change
- **No Per-Project Config**: Every project must use same patterns
- **No Pattern Versioning**: Can't have different rules for different files

**Solution**: Load from config file

```python
# .ce/pattern-checks.yml
version: 1
patterns:
  error_handling:
    - name: bare_except
      regex: "except:\\s*$"
      severity: high
      fix: "Use specific exception types"
      enabled: true

    - name: missing_troubleshooting
      regex: 'raise\s+\w+Error\([^)]*\)(?!.*🔧)'
      severity: medium
      fix: "Add 🔧 Troubleshooting guidance"
      enabled: true
      multiline: true  # Enable re.DOTALL

  naming_conventions:
    - name: version_suffix
      regex: "def\s+\w+_v\d+"
      severity: low
      fix: "Use descriptive names, not versions"
      enabled: false  # Can disable per-project

# Code:
def load_pattern_checks() -> Dict:
    """Load pattern checks from config file."""
    config_path = Path(".ce/pattern-checks.yml")
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
        return config["patterns"]
    return DEFAULT_PATTERN_CHECKS  # Fallback
```

---

### HIGH Issue #9: No Rollback on Partial Failures

**File**: `tools/ce/update_context.py`
**Lines**: 1492-1578 (sync_context function)

**Problem**: If updating 100 PRPs and #50 fails, first 49 are modified with no rollback

**Current Code**:
```python
for prp_path in prp_files:
    try:
        # Read PRP
        # Extract functions
        # Update context_sync flags  # ⚠️ FILE MODIFIED
        # Check transition
        # Move PRP if needed  # ⚠️ FILE MOVED
    except Exception as e:
        errors.append(error_msg)
        continue  # ❌ Previous PRPs already modified!
```

**Failure Scenario**:
```python
# Processing 100 PRPs
# PRPs 1-49: Successfully updated ✅
# PRP 50: Disk full - write fails ❌
# PRPs 51-100: Skipped due to early exit

# Result: Inconsistent state - first 49 modified, rest unchanged
# No way to rollback!
```

**Solution**: Transaction pattern

```python
def sync_context_transactional(target_prp: Optional[str] = None):
    """Sync with transaction support - all or nothing."""

    # Track all modifications
    modifications = []

    try:
        for prp_path in prp_files:
            # Record what we're about to do
            modifications.append({
                "type": "update_flags",
                "path": prp_path,
                "old_metadata": read_prp_header(prp_path)[0].copy()
            })

            # Make modification
            update_context_sync_flags(prp_path, ce_verified, serena_verified)

            if should_transition:
                modifications.append({
                    "type": "move",
                    "from": prp_path,
                    "to": new_path
                })
                new_path = move_prp_to_executed(prp_path)

        # All succeeded - commit
        return {"success": True}

    except Exception as e:
        # Rollback all modifications
        logger.error(f"Sync failed, rolling back {len(modifications)} changes")
        for mod in reversed(modifications):
            if mod["type"] == "update_flags":
                # Restore old metadata
                write_prp_header(mod["path"], mod["old_metadata"])
            elif mod["type"] == "move":
                # Move back
                mod["to"].rename(mod["from"])

        raise RuntimeError(
            f"Sync failed and rolled back: {e}\n"
            f"🔧 Troubleshooting: Check disk space and permissions"
        ) from e
```

---

### HIGH Issue #10: YAML Injection Vulnerability

**File**: `tools/ce/update_context.py`
**Line**: 753

**Problem**: Using frontmatter library without sanitization - YAML injection possible

**Attack Vector**:
```python
# Malicious PRP with YAML injection:
# PRPs/feature-requests/PRP-EVIL.md
---
name: "Normal Feature"
status: "new"
malicious: !!python/object/apply:os.system
  args: ['rm -rf /']  # ⚠️ CODE EXECUTION!
---
# Rest of PRP content

# When update-context reads this PRP:
metadata, content = read_prp_header("PRP-EVIL.md")
# frontmatter.load() executes the YAML code!
# Result: rm -rf / is executed 💀
```

**Solution**: Safe YAML loading

```python
import yaml

def read_prp_header(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """Read PRP YAML header using SAFE loader."""
    content = file_path.read_text()

    # Split on YAML delimiters
    parts = content.split('---\n')
    if len(parts) < 3:
        raise ValueError("Invalid PRP format")

    yaml_content = parts[1]
    markdown_content = '---\n'.join(parts[2:])

    # Use SAFE loader (prevents code execution)
    metadata = yaml.safe_load(yaml_content)  # ✅ SAFE

    return metadata, markdown_content
```

---

### MEDIUM Issue #11: discover_prps() Incomplete

**File**: `tools/ce/update_context.py`
**Lines**: 779-817

**Problem**: Only scans ["feature-requests", "executed", "archived"], misses "system" folder

**Current Code**:
```python
for subdir in ["feature-requests", "executed", "archived"]:
    subdir_path = prps_dir / subdir
    if subdir_path.exists():
        prp_files.extend(subdir_path.glob("*.md"))
```

**Missing**: PRPs in `PRPs/system/` (like DEDRIFT PRPs)

**Fix**:
```python
# Scan ALL subdirectories
for subdir_path in (prps_dir).iterdir():
    if subdir_path.is_dir():
        prp_files.extend(subdir_path.glob("*.md"))

# Or explicitly add "system":
for subdir in ["feature-requests", "executed", "archived", "system"]:
```

---

### MEDIUM Issue #12: Fragile Path Matching

**File**: `tools/ce/update_context.py`
**Line**: 832

**Current Code**:
```python
if "feature-requests" not in str(file_path):
    return False
```

**Problem**: String matching fails with symlinks, relative paths, Windows paths

**Failure Cases**:
```python
# Case 1: Symlink
/home/user/project/PRPs -> /mnt/nas/project-prps/
file_path = "/mnt/nas/project-prps/feature-requests/PRP-10.md"
"feature-requests" in str(file_path)  # ✅ True

# But after resolution:
file_path.resolve() = "/home/user/project/PRPs/feature-requests/PRP-10.md"
# Might not match if using relative path comparisons

# Case 2: Windows paths
file_path = "C:\\project\\PRPs\\feature-requests\\PRP-10.md"
"feature-requests" in str(file_path)  # ✅ True
# But path separator is \ not / - could cause issues

# Case 3: Relative path
file_path = Path("../PRPs/feature-requests/PRP-10.md")
# String matching unreliable
```

**Robust Solution**:
```python
def is_in_feature_requests(file_path: Path) -> bool:
    """Check if PRP is in feature-requests using proper path comparison."""
    # Resolve to absolute path
    abs_path = file_path.resolve()

    # Get project root
    project_root = get_project_root()
    feature_requests_dir = (project_root / "PRPs" / "feature-requests").resolve()

    # Check if file is child of feature-requests directory
    try:
        abs_path.relative_to(feature_requests_dir)
        return True
    except ValueError:
        return False
```

---

### MEDIUM Issue #13: Error Messages Lack Context

**Example**: Line 807

**Current**:
```python
raise FileNotFoundError(
    f"Target PRP not found: {target_prp}\n"
    f"🔧 Troubleshooting:\n"
    f"   - Check path is relative to project root\n"
    f"   - Use: ls PRPs/executed/ to list available PRPs\n"
    f"   - Verify file extension is .md"
)
```

**Problem**: Generic guidance, no context about WHAT the user was trying to do

**Better**:
```python
raise FileNotFoundError(
    f"Target PRP not found: {target_prp}\n"
    f"🔧 Troubleshooting:\n"
    f"   - Context: Running 'ce update-context --prp {target_prp}'\n"
    f"   - Expected: File at {project_root / target_prp}\n"
    f"   - Actual: Path does not exist\n"
    f"   - Suggestion: Use absolute path or run from project root\n"
    f"   - List available: ls {project_root / 'PRPs/executed'}\n"
    f"   - Current directory: {Path.cwd()}"
)
```

---

## Acceptance Criteria

### CRITICAL Fixes (Must Pass)

- [ ] **Drift Score Calculation**:
  - Implement violation-based scoring (not file-based)
  - Test: 1 file with 30 violations shows ~20% drift (not 3%)
  - Test: 30 files with 1 violation each shows ~20% drift (not 100%)
  - Validation: `uv run pytest tests/test_drift_calculation.py -v`

- [ ] **Implementation Verification**:
  - Implement AST-based function verification OR fix Serena MCP integration
  - Test: PRP mentioning non-existent function is marked ce_updated=False
  - Test: PRP mentioning existing function is marked ce_updated=True
  - Validation: `uv run pytest tests/test_implementation_verification.py -v`

- [ ] **Pattern Matching Multiline**:
  - Fix regex to handle multiline error messages
  - Test: Multiline raise with 🔧 troubleshooting NOT flagged
  - Test: Single-line raise without 🔧 IS flagged
  - Test: Docstring examples NOT flagged (false positives eliminated)
  - Validation: `uv run pytest tests/test_pattern_matching.py -v`

- [ ] **Atomic File Operations**:
  - Implement atomic write using temp file + rename
  - Test: Disk full mid-write doesn't corrupt PRP
  - Test: Process killed mid-write doesn't corrupt PRP
  - Validation: `uv run pytest tests/test_atomic_writes.py -v`

- [ ] **True Remediation**:
  - Make --remediate actually fix violations (not just generate PRP)
  - OR rename to --generate-remediation-prp to match behavior
  - Test: `ce update-context --remediate` runs to completion automatically
  - Validation: Manual test in CI/CD pipeline

### HIGH Priority Fixes (Should Pass)

- [ ] Cache TTL consistency across all functions
- [ ] AST-based function extraction (handles decorators, async, classmethods)
- [ ] Pattern checks loaded from config file (.ce/pattern-checks.yml)
- [ ] Transaction-based sync with rollback on failure
- [ ] YAML safe loading (prevent code injection)
- [ ] discover_prps() includes "system" folder
- [ ] Robust path matching (handles symlinks, Windows, relative paths)

### MEDIUM Priority Fixes (Nice to Have)

- [ ] Improved error messages with full context
- [ ] Performance: parallel file I/O
- [ ] Consistent logging levels
- [ ] Input validation for all public functions
- [ ] Edge case handling (NaN, Infinity, empty lists)

### Integration Tests

```bash
# Test full workflow end-to-end
cd tools

# Test 1: Vanilla sync
uv run ce update-context
# Expected: All PRPs scanned, correct drift score reported

# Test 2: Targeted sync
uv run ce update-context --prp PRPs/executed/PRP-20.md
# Expected: Only PRP-20 processed

# Test 3: Remediation workflow (if Option A chosen)
uv run ce update-context --remediate
# Expected: Violations automatically fixed, no manual /execute-prp needed

# Test 4: Cache behavior
uv run ce update-context
uv run ce update-context  # Run again immediately
# Expected: Second run uses cache, completes in <1s

# Test 5: Drift detection accuracy
# Create test file with known violations
echo 'raise ValueError("test")' > test_violations.py
uv run ce update-context
# Expected: Drift report shows this specific violation
```

## Technical Notes

### Estimated Effort

**By Severity**:
- CRITICAL issues (5): 20-25 hours
  - Drift score: 4h (algorithm redesign + tests)
  - Verification: 6h (AST parser + integration)
  - Pattern regex: 4h (multiline support + AST option)
  - Atomic writes: 3h (implement + test)
  - Remediation: 3h (execute PRP automatically)

- HIGH issues (10): 15-20 hours
  - Cache consistency: 2h
  - Function extraction AST: 3h
  - Config-based patterns: 4h
  - Transactions: 4h
  - YAML safety: 1h
  - Path robustness: 2h
  - Other HIGH: 4h

- MEDIUM issues (15+): 10-15 hours
  - Error messages: 3h
  - Performance: 4h
  - Edge cases: 3h
  - Other fixes: 5h

**Total**: 45-60 hours

### Complexity

**VERY HIGH** because:
1. Touches core sync logic (high risk of regressions)
2. Requires algorithm redesign (drift scoring)
3. Multiple architectural changes (atomicity, transactions)
4. Extensive test coverage needed (30+ issues to validate)

### Risk Assessment

**HIGH RISK**:
- Changes affect ALL users of update-context
- Drift score change will show different numbers (breaking change for alerts/dashboards)
- File operation changes could introduce subtle corruption bugs
- Performance changes might impact CI/CD pipelines

**Mitigation**:
1. Feature flag for new drift calculation (allow gradual rollout)
2. Extensive test coverage BEFORE merge
3. Beta testing with sample PRPs
4. Rollback plan if issues found in production

### Dependencies

- Python 3.9+ (for ast module enhancements)
- PyYAML (already installed)
- pytest (for new test suite)
- Optional: mcp-client library (if fixing Serena integration)

### Validation Strategy

**Phase 1**: Unit tests for each issue
```bash
# Run tests for each category
uv run pytest tests/test_drift_calculation.py -v
uv run pytest tests/test_pattern_matching.py -v
uv run pytest tests/test_atomic_writes.py -v
# etc...
```

**Phase 2**: Integration tests
```bash
# Test real PRPs
uv run pytest tests/test_update_context_integration.py -v
```

**Phase 3**: Manual validation
```bash
# Run on actual codebase
cd tools && uv run ce update-context
# Verify drift score is reasonable
# Check no PRPs corrupted
```

**Phase 4**: Beta rollout
```bash
# Enable feature flag
export CE_NEW_DRIFT_CALC=1
cd tools && uv run ce update-context
# Compare old vs new drift scores
```

## Alternatives Considered

### Alternative 1: Incremental Fixes (Rejected)

Fix issues one at a time over multiple PRPs.

**Pros**: Lower risk per PR, easier to review
**Cons**: Takes weeks/months, users suffer from bugs in meantime, testing overhead

**Decision**: REJECTED - Too many critical issues to fix incrementally

### Alternative 2: Rewrite from Scratch (Rejected)

Throw away update_context.py and start fresh.

**Pros**: Clean slate, no technical debt
**Cons**: VERY high risk, loses institutional knowledge, months of work

**Decision**: REJECTED - Too risky, current code is mostly fixable

### Alternative 3: This PRP - Comprehensive Fix (CHOSEN)

Fix all 30+ issues in one coordinated effort.

**Pros**:
- Addresses all issues systematically
- Proper test coverage
- Users get all fixes at once
- Can redesign algorithms properly

**Cons**:
- Large effort (45-60h)
- Higher review burden
- Must be very careful with testing

**Decision**: ACCEPTED - Best balance of risk/reward

## References

### Code Files
- `tools/ce/update_context.py` - Main file with all issues
- `tools/ce/pattern_detectors.py` - Helper functions
- `.ce/drift-report.md` - Example drift report
- `examples/patterns/error-recovery.py` - Pattern reference

### Related PRPs
- PRP-14: /update-context Implementation (original implementation)
- PRP-15: Drift Detection (added drift analysis)
- PRP-17: Extract Drift Analysis (refactored drift logic)
- PRP-20: Error Handling Drift Remediation (exposed these issues)

### External Documentation
- Python AST module: https://docs.python.org/3/library/ast.html
- Atomic file writes: https://danluu.com/file-consistency/
- YAML security: https://en.wikipedia.org/wiki/YAML#Security

---

**Total Issues Documented**: 30+
**Severity Breakdown**: 5 CRITICAL, 10 HIGH, 15+ MEDIUM
**Estimated Effort**: 45-60 hours
**Complexity**: VERY HIGH
**Risk**: HIGH (with mitigation strategies)
