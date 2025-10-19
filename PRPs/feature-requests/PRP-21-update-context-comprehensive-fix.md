---
name: "update-context Comprehensive Reliability & Correctness Fix"
description: "Fix 30+ critical bugs, logic errors, and design flaws in tools/ce/update_context.py to make context synchronization actually reliable and accurate"
prp_id: "PRP-21"
status: "new"
created_date: "2025-10-19T00:00:00Z"
last_updated: "2025-10-19T00:00:00Z"
updated_by: "generate-prp-command"
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
priority: "HIGH"
confidence: 7
effort_hours: 50
risk: "HIGH"
dependencies: []
parent_prp: null
context_memories: []
meeting_evidence: false
---

# update-context Comprehensive Reliability & Correctness Fix

## Problem Statement

`tools/ce/update_context.py` has 30+ critical issues that make drift detection unreliable and remediation non-functional. Current issues:

- **Drift Score Wrong**: Uses file count instead of violation count (misleading metrics)
- **Verification Broken**: Serena MCP disabled, ce_verified doesn't check actual existence
- **Pattern Matching Fails**: Regex doesn't handle multiline code (false positives/negatives)
- **File Corruption Risk**: No atomic writes (fails mid-write = corrupted PRP)
- **Remediation Half-Baked**: --remediate only generates PRP, doesn't execute it

**Impact**: False drift scores, wasted effort chasing phantom violations, silent failures, data corruption risk.

## Implementation Blueprint

### Phase 1: Fix CRITICAL Issues (20-25 hours)

#### 1.1 Drift Score Calculation (4 hours)

**Current Problem** (Line 1044):
```python
# WRONG: Uses file count
drift_score = (len(files_with_violations) / len(python_files)) * 100
# 1 file with 30 violations = 3.3% drift (misleading!)
```

**Fix**:
```python
def calculate_drift_score(violations: List[str], python_files: List[Path],
                          pattern_checks: Dict) -> float:
    """Calculate drift score based on violation count, not file count.

    Args:
        violations: List of all violations found
        python_files: List of Python files scanned
        pattern_checks: Dict of pattern checks applied

    Returns:
        Drift score as percentage (0-100)
    """
    total_violations = len(violations)
    total_checks = len(python_files) * sum(len(checks) for checks in pattern_checks.values())

    if total_checks == 0:
        return 0.0

    return (total_violations / total_checks) * 100
```

**Test**:
```python
def test_drift_score_violation_based():
    """Test drift score uses violation count, not file count."""
    violations = [f"violation_{i}" for i in range(30)]
    files = [Path(f"file_{i}.py") for i in range(30)]
    checks = {"error_handling": ["check1", "check2", "check3"]}

    score = calculate_drift_score(violations, files, checks)

    # 30 violations / (30 files * 3 checks) = 33.3%
    assert abs(score - 33.3) < 0.1

def test_drift_score_one_file_many_violations():
    """Test 1 file with 30 violations shows high drift."""
    violations = [f"file1_violation_{i}" for i in range(30)]
    files = [Path("file1.py")] + [Path(f"file_{i}.py") for i in range(2, 31)]
    checks = {"error_handling": ["check1"]}

    score = calculate_drift_score(violations, files, checks)

    # 30 violations / (30 files * 1 check) = 100%
    assert abs(score - 100.0) < 0.1
```

**Integration**: Update `verify_codebase_matches_examples()` line 1044-1045

---

#### 1.2 Implementation Verification - AST Parsing (6 hours)

**Current Problem** (Line 1524):
```python
# Serena disabled - always False
serena_verified = False
# Only checks if PRP mentions functions, not if they exist!
ce_verified = len(expected_functions) > 0
```

**Fix** (Use AST parsing - simpler than fixing Serena MCP):
```python
import ast
from pathlib import Path
from typing import List, Set

def verify_functions_exist_ast(expected: List[str]) -> bool:
    """Check if functions/classes actually exist in tools/ce/ using AST.

    Args:
        expected: List of function/class names to verify

    Returns:
        True if all expected symbols found, False otherwise
    """
    tools_ce = Path("tools/ce")
    found_symbols = set()

    for py_file in tools_ce.glob("*.py"):
        try:
            tree = ast.parse(py_file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    found_symbols.add(node.name)
                elif isinstance(node, ast.AsyncFunctionDef):
                    found_symbols.add(node.name)
                elif isinstance(node, ast.ClassDef):
                    found_symbols.add(node.name)
                    # Add methods
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            found_symbols.add(item.name)
        except (SyntaxError, OSError) as e:
            logger.warning(f"Failed to parse {py_file}: {e}")
            continue

    missing = [func for func in expected if func not in found_symbols]

    if missing:
        logger.warning(f"Missing expected functions: {missing}")
        return False

    return True
```

**Test**:
```python
def test_verify_functions_exist_ast():
    """Test AST-based function verification."""
    # Test with real functions
    assert verify_functions_exist_ast(["sync_context", "analyze_context_drift"])

    # Test with non-existent functions
    assert not verify_functions_exist_ast(["fake_function_12345"])

    # Test with mix
    result = verify_functions_exist_ast(["sync_context", "fake_function"])
    assert not result

def test_verify_functions_handles_classes():
    """Test verification finds classes and their methods."""
    # Test with class name
    assert verify_functions_exist_ast(["SyncTransaction"])  # If we add this class

    # Test with method name
    assert verify_functions_exist_ast(["verify_codebase_matches_examples"])
```

**Integration**: Update `sync_context()` line 1524

---

#### 1.3 Pattern Matching - Multiline Support (4 hours)

**Current Problem** (Line 39):
```python
# FAILS on multiline raises
("missing_troubleshooting", r'raise \w+Error\([^🔧]+\)$', "Add 🔧")
# $ anchor requires end of line - multiline raises missed!
```

**Fix** (Use AST parsing to avoid regex issues):
```python
import ast
from typing import List, Tuple

def find_raises_without_troubleshooting(code: str, file_path: Path) -> List[str]:
    """Find raise statements missing troubleshooting using AST.

    Args:
        code: Python source code
        file_path: Path to file being checked

    Returns:
        List of violation strings with file:line format
    """
    violations = []

    try:
        tree = ast.parse(code)
        lines = code.split('\n')

        for node in ast.walk(tree):
            if isinstance(node, ast.Raise):
                line_num = node.lineno
                # Get context (5 lines after raise)
                context_start = line_num - 1
                context_end = min(len(lines), line_num + 5)
                context = '\n'.join(lines[context_start:context_end])

                # Check if troubleshooting guidance present
                if '🔧' not in context and 'Troubleshooting' not in context:
                    error_type = "UnknownError"
                    if isinstance(node.exc, ast.Call):
                        if isinstance(node.exc.func, ast.Name):
                            error_type = node.exc.func.id

                    violations.append(
                        f"File {file_path} line {line_num} raises {error_type} "
                        f"without troubleshooting guidance (violates examples/patterns/error-handling.py)"
                    )

    except SyntaxError as e:
        logger.debug(f"Skipping {file_path} - syntax error: {e}")

    return violations
```

**Test**:
```python
def test_multiline_raise_detection():
    """Test pattern matching handles multiline raises correctly."""
    code_with_troubleshooting = '''
raise RuntimeError(
    f"Error message\\n"
    f"🔧 Troubleshooting: Fix this"
)
'''
    code_without = '''
raise RuntimeError(
    f"Error message\\n"
    f"No guidance here"
)
'''

    violations_with = find_raises_without_troubleshooting(
        code_with_troubleshooting, Path("test.py")
    )
    violations_without = find_raises_without_troubleshooting(
        code_without, Path("test.py")
    )

    assert len(violations_with) == 0  # Has troubleshooting
    assert len(violations_without) == 1  # Missing troubleshooting

def test_docstring_raises_ignored():
    """Test raises in docstrings are not flagged."""
    code_with_docstring = '''
def foo():
    """Example:
    
    raise RuntimeError("example")
    """
    pass
'''
    violations = find_raises_without_troubleshooting(code_with_docstring, Path("test.py"))
    
    # Docstring examples should not be flagged
    # AST doesn't parse docstrings as executable code
    assert len(violations) == 0
```

**Integration**: Update `pattern_detectors.py` to use AST-based checking

---

#### 1.4 Atomic File Operations (3 hours)

**Current Problem** (Line 753):
```python
# Direct write - corruption risk!
with open(file_path, 'w') as f:
    f.write(frontmatter.dumps(post))
# If killed mid-write: CORRUPTED FILE
```

**Fix** (Reuse pattern from `prp.py:215-219`):
```python
import tempfile
import os
from pathlib import Path

def atomic_write(file_path: Path, content: str):
    """Write file atomically using temp file + rename.

    Prevents corruption if process killed mid-write.

    Args:
        file_path: Target file path
        content: Content to write

    Raises:
        RuntimeError: If write fails
    """
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
    except Exception as e:
        # Clean up temp file on failure
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise RuntimeError(
            f"Atomic write failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check disk space: df -h\n"
            f"   - Verify permissions: ls -la {file_path.parent}\n"
            f"   - File path: {file_path}"
        ) from e

# Usage in update_context_sync_flags:
def update_context_sync_flags(file_path: Path, ce_verified: bool, serena_verified: bool):
    """Update context_sync flags using atomic write."""
    metadata, content = read_prp_header(file_path)

    # Update flags
    if "context_sync" not in metadata:
        metadata["context_sync"] = {}

    metadata["context_sync"]["ce_updated"] = ce_verified
    metadata["context_sync"]["serena_updated"] = serena_verified
    metadata["context_sync"]["last_sync"] = datetime.now(timezone.utc).isoformat()
    metadata["updated_by"] = "update-context-command"

    # Atomic write
    post = frontmatter.Post(content, **metadata)
    atomic_write(file_path, frontmatter.dumps(post))
```

**Test**:
```python
def test_atomic_write_success(tmp_path):
    """Test atomic write completes successfully."""
    test_file = tmp_path / "test.md"
    content = "test content"

    atomic_write(test_file, content)

    assert test_file.read_text() == content

def test_atomic_write_disk_full(tmp_path, monkeypatch):
    """Test atomic write handles disk full gracefully."""
    test_file = tmp_path / "test.md"

    def mock_fsync(fd):
        raise OSError("No space left on device")

    monkeypatch.setattr(os, "fsync", mock_fsync)

    with pytest.raises(RuntimeError) as exc:
        atomic_write(test_file, "content")

    assert "Atomic write failed" in str(exc.value)
    assert "🔧 Troubleshooting" in str(exc.value)
    # Original file should not exist (temp cleaned up)
    assert not test_file.exists()

def test_atomic_write_no_partial_corruption(tmp_path):
    """Test atomic write never leaves partial content."""
    test_file = tmp_path / "test.md"
    test_file.write_text("original content")

    # Simulate failure mid-write
    def mock_replace(src, dst):
        raise OSError("Simulated failure")

    import os as os_module
    original_replace = os_module.replace
    
    try:
        os_module.replace = mock_replace
        with pytest.raises(RuntimeError):
            atomic_write(test_file, "new content")
    finally:
        os_module.replace = original_replace

    # Original content should be intact
    assert test_file.read_text() == "original content"
```

**Integration**: Replace all `open(file_path, 'w')` calls with `atomic_write()`

---

#### 1.5 True Remediation Automation (3 hours)

**Current Problem** (Line 483):
```python
# Flag says "remediate" but only generates PRP!
def remediate_drift_workflow(yolo_mode: bool = False):
    # ... generate PRP ...
    print(f"Run: /execute-prp {prp_path}")  # Manual step required!
    return {"success": True, "prp_path": prp_path}
```

**Fix** (Make --remediate actually remediate):
```python
from .execute import execute_prp

def remediate_drift_workflow(yolo_mode: bool = False, auto_execute: bool = False):
    """Generate and optionally execute remediation PRP.

    Args:
        yolo_mode: Skip confirmation prompts
        auto_execute: Actually execute PRP (not just generate)

    Returns:
        {"success": bool, "prp_path": str, "executed": bool, "fixes": List}
    """
    # ... detect drift ...
    # ... generate blueprint ...
    # ... generate PRP ...

    if auto_execute:
        logger.info(f"Executing remediation PRP: {prp_path}")
        
        try:
            result = execute_prp(prp_path)

            if not result["success"]:
                raise RuntimeError(
                    f"Remediation failed: {result.get('error')}\n"
                    f"🔧 Troubleshooting:\n"
                    f"   - Check PRP: {prp_path}\n"
                    f"   - Review errors above\n"
                    f"   - Try manual execution: /execute-prp {prp_path}"
                )

            return {
                "success": True,
                "prp_path": prp_path,
                "executed": True,
                "fixes": result.get("fixes", [])
            }
        except Exception as e:
            logger.error(f"Auto-execution failed: {e}")
            raise

    print(f"Run: /execute-prp {prp_path}")
    return {"success": True, "prp_path": prp_path, "executed": False}
```

**CLI Update**:
```python
@click.command()
@click.option("--remediate", is_flag=True, help="Generate remediation PRP")
@click.option("--auto-execute", is_flag=True, help="Execute remediation automatically")
def update_context_cli(remediate, auto_execute):
    """Sync context and optionally remediate drift."""
    if remediate:
        result = remediate_drift_workflow(auto_execute=auto_execute)
        if result["executed"]:
            print(f"✅ Remediation executed: {len(result['fixes'])} fixes applied")
        else:
            print(f"📄 Remediation PRP generated: {result['prp_path']}")
```

**Test**:
```python
def test_remediate_auto_execute(tmp_path, monkeypatch):
    """Test --remediate --auto-execute actually fixes violations."""
    # Mock execute_prp to return success
    def mock_execute(prp_path):
        return {
            "success": True,
            "fixes": ["Fixed violation 1", "Fixed violation 2"]
        }

    monkeypatch.setattr("ce.update_context.execute_prp", mock_execute)

    # Run remediation with auto-execute
    result = remediate_drift_workflow(auto_execute=True)

    assert result["executed"] is True
    assert result["success"] is True
    assert len(result["fixes"]) == 2

def test_remediate_without_auto_execute():
    """Test --remediate without auto-execute only generates PRP."""
    result = remediate_drift_workflow(auto_execute=False)

    assert result["executed"] is False
    assert result["success"] is True
    assert "prp_path" in result
```

**Integration**: Update CLI and remediate function

---

### Phase 2: Fix HIGH Priority Issues (15-20 hours)

#### 2.1 Cache TTL Consistency (2 hours)

**Problem**: `get_cache_ttl()` exists but `sync_context()` hardcodes 5 minutes (Line 1546).

**Fix**:
```python
# Line 1546 - Update sync_context()
def sync_context(target_prp: Optional[str] = None, cache_ttl: Optional[int] = None):
    """Sync context with configurable cache TTL."""
    
    # Get cache TTL from config/CLI
    ttl = get_cache_ttl(cache_ttl)
    
    # Check cache
    cached = get_cached_analysis()
    if cached and is_cache_valid(cached, ttl_minutes=ttl):
        logger.info(f"Using cached drift analysis (TTL: {ttl}min)")
        return cached
    
    # ... rest of sync logic ...
```

**Test**:
```python
def test_cache_ttl_respected(tmp_path, monkeypatch):
    """Test cache TTL uses config value, not hardcoded."""
    # Create config with custom TTL
    config_path = tmp_path / ".ce" / "config.yml"
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text("cache:\n  analysis_ttl_minutes: 15")

    monkeypatch.chdir(tmp_path)

    ttl = get_cache_ttl()
    assert ttl == 15  # Uses config value, not default 5

def test_cache_ttl_cli_override():
    """Test CLI flag overrides config TTL."""
    ttl = get_cache_ttl(cli_ttl=30)
    assert ttl == 30  # CLI takes priority
```

**Integration**: Update `sync_context()` line 1546

---

#### 2.2 AST-Based Function Extraction (3 hours)

**Problem**: `extract_expected_functions()` regex misses decorators, async, classmethods (Lines 882-906).

**Fix**:
```python
import ast
import re
from typing import List

def extract_expected_functions_ast(content: str) -> List[str]:
    """Extract ALL callable names from PRP using AST.

    Handles:
    - Regular functions (def)
    - Async functions (async def)
    - Classes and their methods
    - Classmethods, staticmethods
    - Decorated functions

    Args:
        content: PRP markdown content

    Returns:
        List of function/class names found in code blocks
    """
    functions = set()

    # Extract Python code blocks
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

**Test**:
```python
def test_extract_functions_ast_comprehensive():
    """Test AST extraction handles all function types."""
    content = """
```python
@property
def foo():
    pass

async def bar():
    pass

class Baz:
    @classmethod
    def qux(cls):
        pass

    @staticmethod
    def quux():
        pass
```
    """

    functions = extract_expected_functions_ast(content)

    assert "foo" in functions
    assert "bar" in functions
    assert "Baz" in functions
    assert "qux" in functions
    assert "quux" in functions

def test_extract_functions_handles_malformed_code():
    """Test extraction continues despite syntax errors."""
    content = """
```python
def valid_function():
    pass
```

```python
def invalid syntax here:
    pass
```

```python
def another_valid():
    pass
```
    """

    functions = extract_expected_functions_ast(content)

    assert "valid_function" in functions
    assert "another_valid" in functions
    # invalid syntax block skipped, no crash
```

**Integration**: Replace `extract_expected_functions()` at lines 882-906

---

#### 2.3 Config-Based Pattern Checks (4 hours)

**Problem**: `PATTERN_CHECKS` hardcoded - can't add custom patterns without code edit (Lines 32-45).

**Fix**:
```python
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

DEFAULT_PATTERN_CHECKS = {
    "error_handling": [
        ("bare_except", r"except:\s*$", "Use specific exception types"),
        ("missing_troubleshooting", r'raise\s+\w+Error', "Add 🔧 Troubleshooting guidance"),
    ],
    "naming_conventions": [
        ("version_suffix", r"def\s+\w+_v\d+", "Use descriptive names, not versions"),
    ],
    "kiss_violations": [
        ("deep_nesting", r"^\s{16,}", "Reduce nesting depth"),
    ]
}

def load_pattern_checks_from_config() -> Dict[str, List[Tuple[str, str, str]]]:
    """Load pattern checks from .ce/pattern-checks.yml.

    Falls back to DEFAULT_PATTERN_CHECKS if config missing.

    Returns:
        Dict of pattern checks with enabled checks only

    Example config (.ce/pattern-checks.yml):
        version: 1
        patterns:
          error_handling:
            - name: bare_except
              regex: "except:\\s*$"
              severity: high
              fix: "Use specific exception types"
              enabled: true
    """
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    config_path = project_root / ".ce" / "pattern-checks.yml"

    if config_path.exists():
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)

            # Filter enabled checks
            enabled_patterns = {}
            for category, checks in config.get("patterns", {}).items():
                enabled = [
                    (c["name"], c["regex"], c["fix"])
                    for c in checks
                    if c.get("enabled", True)
                ]
                if enabled:
                    enabled_patterns[category] = enabled

            logger.info(f"Loaded {len(enabled_patterns)} pattern categories from config")
            return enabled_patterns

        except Exception as e:
            logger.warning(f"Failed to load pattern config: {e}, using defaults")

    # Fallback to hardcoded defaults
    return DEFAULT_PATTERN_CHECKS

# Update load_pattern_checks to use config:
def load_pattern_checks() -> Dict[str, List[Tuple[str, str, str]]]:
    """Load pattern checks from config or defaults."""
    return load_pattern_checks_from_config()
```

**Test**:
```python
def test_load_patterns_from_config(tmp_path, monkeypatch):
    """Test loading custom patterns from config file."""
    config_content = """
version: 1
patterns:
  error_handling:
    - name: bare_except
      regex: "except:\\s*$"
      severity: high
      fix: "Use specific exceptions"
      enabled: true
    
    - name: disabled_check
      regex: "test"
      severity: low
      fix: "This is disabled"
      enabled: false
  
  custom_category:
    - name: custom_check
      regex: "TODO:"
      severity: medium
      fix: "Remove TODOs"
      enabled: true
"""
    config_path = tmp_path / ".ce" / "pattern-checks.yml"
    config_path.parent.mkdir(exist_ok=True)
    config_path.write_text(config_content)

    monkeypatch.chdir(tmp_path)

    patterns = load_pattern_checks_from_config()

    assert "error_handling" in patterns
    assert "custom_category" in patterns
    
    # Check enabled filtering
    assert len(patterns["error_handling"]) == 1  # disabled_check excluded
    assert patterns["error_handling"][0][0] == "bare_except"

def test_load_patterns_fallback_to_defaults():
    """Test fallback to defaults when config missing."""
    patterns = load_pattern_checks_from_config()

    # Should use DEFAULT_PATTERN_CHECKS
    assert "error_handling" in patterns
    assert isinstance(patterns["error_handling"], list)
```

**Integration**: Update `load_pattern_checks()` at lines 32-45

---

#### 2.4 Transaction-Based Sync with Rollback (4 hours)

**Problem**: If updating 100 PRPs and #50 fails, first 49 modified with no rollback (Lines 1492-1578).

**Fix**:
```python
from typing import Dict, Any, List
from pathlib import Path

class SyncTransaction:
    """Transaction manager for PRP sync operations."""

    def __init__(self):
        self.modifications: List[Dict[str, Any]] = []

    def record_update(self, prp_path: Path, old_metadata: Dict):
        """Record a PRP update for rollback."""
        self.modifications.append({
            "type": "update",
            "path": prp_path,
            "old_metadata": old_metadata.copy()
        })

    def record_move(self, from_path: Path, to_path: Path):
        """Record a PRP move for rollback."""
        self.modifications.append({
            "type": "move",
            "from": from_path,
            "to": to_path
        })

    def rollback(self):
        """Rollback all modifications in reverse order."""
        logger.warning(f"Rolling back {len(self.modifications)} modifications")
        
        for mod in reversed(self.modifications):
            try:
                if mod["type"] == "update":
                    # Restore old metadata using atomic write
                    metadata = mod["old_metadata"]
                    content = mod["path"].read_text().split('---\n', 2)[2]
                    post = frontmatter.Post(content, **metadata)
                    atomic_write(mod["path"], frontmatter.dumps(post))
                    logger.info(f"Restored metadata: {mod['path']}")
                    
                elif mod["type"] == "move":
                    # Move back
                    if mod["to"].exists():
                        mod["to"].rename(mod["from"])
                        logger.info(f"Restored move: {mod['to']} → {mod['from']}")
                        
            except Exception as e:
                logger.error(f"Rollback failed for {mod}: {e}")

def sync_context_transactional(target_prp: Optional[str] = None):
    """Sync with transaction support - all or nothing."""
    transaction = SyncTransaction()

    try:
        prp_files = discover_prps(target_prp)

        for prp_path in prp_files:
            # Read current state before modification
            metadata, content = read_prp_header(prp_path)
            transaction.record_update(prp_path, metadata)

            # Extract and verify functions
            expected_functions = extract_expected_functions_ast(content)
            ce_verified = verify_functions_exist_ast(expected_functions)

            # Make modification (atomic write)
            update_context_sync_flags(prp_path, ce_verified, serena_verified=False)

            # Check if should transition
            if should_transition_to_executed(prp_path):
                new_path = move_prp_to_executed(prp_path)
                transaction.record_move(prp_path, new_path)

        # All succeeded - commit (no action needed, changes already applied)
        logger.info(f"Successfully synced {len(prp_files)} PRPs")
        return {"success": True, "synced_count": len(prp_files)}

    except Exception as e:
        # Rollback all modifications
        logger.error(f"Sync failed: {e}")
        transaction.rollback()

        raise RuntimeError(
            f"Sync failed and rolled back {len(transaction.modifications)} changes: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check disk space: df -h\n"
            f"   - Verify permissions: ls -la PRPs/\n"
            f"   - Review error above\n"
            f"   - All changes have been rolled back"
        ) from e
```

**Test**:
```python
def test_sync_transaction_rollback_on_failure(tmp_path):
    """Test transaction rollback restores original state."""
    # Create test PRPs
    prp1 = tmp_path / "PRP-1.md"
    prp1.write_text("---\nstatus: new\n---\nContent 1")
    
    prp2 = tmp_path / "PRP-2.md"
    prp2.write_text("---\nstatus: new\n---\nContent 2")

    transaction = SyncTransaction()

    # Record modifications
    meta1, _ = read_prp_header(prp1)
    transaction.record_update(prp1, meta1)

    # Modify PRP-1
    update_context_sync_flags(prp1, True, False)

    # Simulate failure before PRP-2 modified
    transaction.rollback()

    # Verify PRP-1 restored to original
    restored_meta, _ = read_prp_header(prp1)
    assert restored_meta["status"] == "new"
    assert "context_sync" not in restored_meta

def test_sync_transaction_rollback_moves(tmp_path):
    """Test transaction rollback reverses file moves."""
    feature_dir = tmp_path / "feature-requests"
    executed_dir = tmp_path / "executed"
    feature_dir.mkdir()
    executed_dir.mkdir()

    prp = feature_dir / "PRP-1.md"
    prp.write_text("---\nstatus: executed\n---\nContent")

    transaction = SyncTransaction()

    # Move file
    new_path = executed_dir / "PRP-1.md"
    prp.rename(new_path)
    transaction.record_move(prp, new_path)

    # Rollback
    transaction.rollback()

    # Verify file restored to original location
    assert prp.exists()
    assert not new_path.exists()
```

**Integration**: Replace `sync_context()` with `sync_context_transactional()` at lines 1492-1578

---

#### 2.5 YAML Safe Loading (1 hour)

**Problem**: Using `frontmatter.load()` without sanitization - YAML injection possible (Line 753).

**Fix**:
```python
import yaml
from typing import Tuple, Dict, Any
from pathlib import Path

def read_prp_header_safe(file_path: Path) -> Tuple[Dict[str, Any], str]:
    """Read PRP YAML header using SAFE loader (prevents code execution).

    Args:
        file_path: Path to PRP file

    Returns:
        (metadata_dict, markdown_content)

    Raises:
        ValueError: If YAML format invalid
        FileNotFoundError: If file missing
    """
    if not file_path.exists():
        raise FileNotFoundError(
            f"PRP file not found: {file_path}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Verify file path is correct\n"
            f"   - Check if file was moved or renamed\n"
            f"   - Use: ls {file_path.parent} to list directory"
        )

    content = file_path.read_text()

    # Split on YAML delimiters
    parts = content.split('---\n')
    if len(parts) < 3:
        raise ValueError(
            f"Invalid PRP format - missing YAML frontmatter\n"
            f"🔧 Troubleshooting:\n"
            f"   - File must start with: ---\\n\n"
            f"   - YAML header must end with: ---\\n\n"
            f"   - Reference: examples/system-prps/ for format"
        )

    yaml_content = parts[1]
    markdown_content = '---\n'.join(parts[2:])

    # Use SAFE loader (prevents !!python/object code execution)
    try:
        metadata = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise ValueError(
            f"Invalid YAML syntax: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check YAML indentation\n"
            f"   - Verify quotes are balanced\n"
            f"   - Use: yamllint {file_path}"
        ) from e

    return metadata, markdown_content

# Replace read_prp_header with safe version
read_prp_header = read_prp_header_safe
```

**Test**:
```python
def test_yaml_safe_loading_prevents_injection(tmp_path):
    """Test safe loading prevents YAML code execution."""
    # Malicious PRP with code injection
    malicious_content = """---
name: "Evil PRP"
status: "new"
malicious: !!python/object/apply:os.system
  args: ['echo "EXPLOIT!"']
---
# Content
"""
    prp_path = tmp_path / "evil.md"
    prp_path.write_text(malicious_content)

    # Safe loader should FAIL to parse !!python/object
    with pytest.raises(yaml.YAMLError):
        metadata, _ = read_prp_header_safe(prp_path)

def test_yaml_safe_loading_normal_content(tmp_path):
    """Test safe loading works with normal PRP content."""
    normal_content = """---
name: "Normal PRP"
status: "new"
prp_id: "PRP-1"
---
# Content
"""
    prp_path = tmp_path / "normal.md"
    prp_path.write_text(normal_content)

    metadata, content = read_prp_header_safe(prp_path)

    assert metadata["name"] == "Normal PRP"
    assert metadata["status"] == "new"
    assert "# Content" in content
```

**Integration**: Replace `read_prp_header()` usage throughout `update_context.py`

---

### Phase 3: Fix MEDIUM Issues (10-15 hours)

#### 3.1 discover_prps() Include "system" Folder (1 hour)

**Problem**: Only scans ["feature-requests", "executed", "archived"], misses "system" folder (Lines 779-817).

**Current Code**:
```python
for subdir in ["feature-requests", "executed", "archived"]:
    subdir_path = prps_dir / subdir
    if subdir_path.exists():
        prp_files.extend(subdir_path.glob("*.md"))
```

**Fix**:
```python
# Option 1: Scan ALL subdirectories (recommended)
def discover_prps(target_prp: Optional[str] = None) -> List[Path]:
    """Discover all PRP files in PRPs/ directory.

    Scans all subdirectories to find PRPs, not just hardcoded folders.

    Args:
        target_prp: Optional specific PRP to find

    Returns:
        List of PRP file paths
    """
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    prps_dir = project_root / "PRPs"
    prp_files = []

    if target_prp:
        # Handle specific PRP
        target_path = Path(target_prp)
        if not target_path.is_absolute():
            target_path = project_root / target_path
        
        if not target_path.exists():
            raise FileNotFoundError(
                f"Target PRP not found: {target_prp}\n"
                f"🔧 Troubleshooting:\n"
                f"   - Check path is relative to project root\n"
                f"   - Use: ls PRPs/executed/ to list available PRPs\n"
                f"   - Verify file extension is .md"
            )
        return [target_path]

    # Scan ALL subdirectories for PRPs
    for subdir_path in prps_dir.iterdir():
        if subdir_path.is_dir():
            prp_files.extend(subdir_path.glob("PRP-*.md"))

    return prp_files
```

**Test**:
```python
def test_discover_prps_includes_system_folder(tmp_path, monkeypatch):
    """Test discover_prps() finds PRPs in system/ folder."""
    # Create test structure
    prps_dir = tmp_path / "PRPs"
    system_dir = prps_dir / "system"
    system_dir.mkdir(parents=True)
    
    # Create test PRPs
    (system_dir / "PRP-DEDRIFT-1.md").write_text("# Dedrift PRP")
    
    feature_dir = prps_dir / "feature-requests"
    feature_dir.mkdir()
    (feature_dir / "PRP-10.md").write_text("# Feature PRP")

    monkeypatch.chdir(tmp_path)

    # Discover PRPs
    prps = discover_prps()

    # Verify both folders scanned
    system_prps = [p for p in prps if "system" in str(p)]
    feature_prps = [p for p in prps if "feature-requests" in str(p)]
    
    assert len(system_prps) == 1
    assert len(feature_prps) == 1

def test_discover_prps_handles_new_folders(tmp_path, monkeypatch):
    """Test discover_prps() works with future folder additions."""
    prps_dir = tmp_path / "PRPs"
    
    # Create new folder not in hardcoded list
    custom_dir = prps_dir / "custom-category"
    custom_dir.mkdir(parents=True)
    (custom_dir / "PRP-100.md").write_text("# Custom PRP")

    monkeypatch.chdir(tmp_path)

    prps = discover_prps()

    custom_prps = [p for p in prps if "custom-category" in str(p)]
    assert len(custom_prps) == 1
```

**Integration**: Replace `discover_prps()` at lines 779-817

---

#### 3.2 Robust Path Matching (2 hours)

**Problem**: String matching fails with symlinks, relative paths, Windows paths (Line 832).

**Current Code**:
```python
if "feature-requests" not in str(file_path):
    return False
```

**Fix**:
```python
def is_in_feature_requests(file_path: Path) -> bool:
    """Check if PRP is in feature-requests using proper path comparison.

    Handles:
    - Symlinks (resolves to real path)
    - Windows paths (backslash separators)
    - Relative paths (converts to absolute)

    Args:
        file_path: Path to PRP file

    Returns:
        True if file is in feature-requests/ directory
    """
    # Resolve to absolute path (follows symlinks)
    abs_path = file_path.resolve()

    # Get project root
    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    feature_requests_dir = (project_root / "PRPs" / "feature-requests").resolve()

    # Check if file is child of feature-requests directory
    try:
        abs_path.relative_to(feature_requests_dir)
        return True
    except ValueError:
        return False

def is_in_directory(file_path: Path, directory_name: str) -> bool:
    """Generic path matching for any PRP directory.

    Args:
        file_path: Path to check
        directory_name: Directory name (e.g., "executed", "archived")

    Returns:
        True if file is in specified directory
    """
    abs_path = file_path.resolve()

    current_dir = Path.cwd()
    if current_dir.name == "tools":
        project_root = current_dir.parent
    else:
        project_root = current_dir

    target_dir = (project_root / "PRPs" / directory_name).resolve()

    try:
        abs_path.relative_to(target_dir)
        return True
    except ValueError:
        return False
```

**Test**:
```python
def test_path_matching_handles_symlinks(tmp_path):
    """Test path matching works with symlinked directories."""
    # Create real directory
    real_dir = tmp_path / "real_prps" / "feature-requests"
    real_dir.mkdir(parents=True)
    prp_file = real_dir / "PRP-10.md"
    prp_file.write_text("# Test")

    # Create symlink
    symlink_dir = tmp_path / "PRPs"
    symlink_dir.symlink_to(tmp_path / "real_prps")

    # Test with symlink path
    symlink_path = symlink_dir / "feature-requests" / "PRP-10.md"
    assert is_in_feature_requests(symlink_path)

def test_path_matching_handles_relative_paths(tmp_path, monkeypatch):
    """Test path matching works with relative paths."""
    # Create structure
    feature_dir = tmp_path / "PRPs" / "feature-requests"
    feature_dir.mkdir(parents=True)
    prp_file = feature_dir / "PRP-10.md"
    prp_file.write_text("# Test")

    monkeypatch.chdir(tmp_path)

    # Test with relative path
    relative_path = Path("PRPs/feature-requests/PRP-10.md")
    assert is_in_feature_requests(relative_path)

def test_path_matching_rejects_wrong_directory(tmp_path, monkeypatch):
    """Test path matching correctly rejects files in other directories."""
    # Create structure
    executed_dir = tmp_path / "PRPs" / "executed"
    executed_dir.mkdir(parents=True)
    prp_file = executed_dir / "PRP-10.md"
    prp_file.write_text("# Test")

    monkeypatch.chdir(tmp_path)

    # File in executed/ should not match feature-requests/
    assert not is_in_feature_requests(prp_file)
    assert is_in_directory(prp_file, "executed")
```

**Integration**: Replace string matching at line 832 and `should_transition_to_executed()` usage

---

#### 3.3 Improved Error Messages with Full Context (2 hours)

**Problem**: Generic error messages don't include execution context (Line 807).

**Fix**:
```python
from typing import Type, Dict, Any

def create_contextual_error(
    error_type: Type[Exception],
    message: str,
    context: Dict[str, Any]
) -> Exception:
    """Create error with full execution context.

    Args:
        error_type: Exception class to raise
        message: Error message
        context: Dict with command, expected, actual, cwd, suggestion

    Returns:
        Exception instance with formatted message
    """
    troubleshooting = [
        f"🔧 Troubleshooting:",
        f"   - Command: {context.get('command', 'N/A')}",
        f"   - Expected: {context.get('expected', 'N/A')}",
        f"   - Actual: {context.get('actual', 'N/A')}",
        f"   - Current directory: {context.get('cwd', Path.cwd())}",
    ]

    if 'suggestion' in context:
        troubleshooting.append(f"   - Suggestion: {context['suggestion']}")

    if 'list_command' in context:
        troubleshooting.append(f"   - List available: {context['list_command']}")

    full_message = f"{message}\n" + "\n".join(troubleshooting)
    return error_type(full_message)

# Usage example - replace generic errors:
def discover_prps(target_prp: Optional[str] = None) -> List[Path]:
    """Discover PRPs with contextual error messages."""
    # ... discovery logic ...

    if target_prp:
        target_path = Path(target_prp)
        if not target_path.is_absolute():
            target_path = project_root / target_path

        if not target_path.exists():
            raise create_contextual_error(
                FileNotFoundError,
                f"Target PRP not found: {target_prp}",
                {
                    "command": f"ce update-context --prp {target_prp}",
                    "expected": str(target_path),
                    "actual": "Path does not exist",
                    "cwd": Path.cwd(),
                    "suggestion": "Use absolute path or run from project root",
                    "list_command": f"ls {project_root / 'PRPs/executed'}"
                }
            )
```

**Test**:
```python
def test_contextual_error_includes_all_info():
    """Test error messages include execution context."""
    error = create_contextual_error(
        FileNotFoundError,
        "File not found",
        {
            "command": "ce validate",
            "expected": "/path/to/file",
            "actual": "Does not exist",
            "cwd": "/home/user",
            "suggestion": "Check file path"
        }
    )

    error_str = str(error)
    assert "🔧 Troubleshooting" in error_str
    assert "ce validate" in error_str
    assert "/path/to/file" in error_str
    assert "/home/user" in error_str
    assert "Check file path" in error_str

def test_contextual_error_optional_fields():
    """Test error works with minimal context."""
    error = create_contextual_error(
        ValueError,
        "Invalid value",
        {
            "command": "ce sync",
            "expected": "valid input",
            "actual": "invalid input"
        }
    )

    error_str = str(error)
    assert "Invalid value" in error_str
    assert "ce sync" in error_str
```

**Integration**: Apply to all error raising throughout `update_context.py` (Lines 807, and ~10 other locations)

---

#### 3.4 Parallel File I/O for Performance (3 hours)

**Problem**: Sequential file processing slow for large PRP sets.

**Fix**:
```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Any
import logging

def process_prps_parallel(
    prp_files: List[Path],
    processor: Callable[[Path], Any],
    max_workers: int = 4
) -> List[Any]:
    """Process PRP files in parallel using thread pool.

    Args:
        prp_files: List of PRP paths to process
        processor: Function to apply to each PRP
        max_workers: Max parallel workers (default: 4)

    Returns:
        List of results from processor function
    """
    results = []
    errors = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_prp = {
            executor.submit(processor, prp): prp
            for prp in prp_files
        }

        # Collect results as they complete
        for future in as_completed(future_to_prp):
            prp = future_to_prp[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process {prp}: {e}")
                errors.append((prp, e))

    if errors:
        logger.warning(f"Processing completed with {len(errors)} errors")

    return results

# Usage in sync_context:
def sync_context_parallel(target_prp: Optional[str] = None):
    """Sync context with parallel file I/O."""
    prp_files = discover_prps(target_prp)

    def process_single_prp(prp_path: Path) -> Dict[str, Any]:
        """Process single PRP (thread-safe operation)."""
        metadata, content = read_prp_header(prp_path)
        expected_functions = extract_expected_functions_ast(content)
        ce_verified = verify_functions_exist_ast(expected_functions)

        # Atomic write is thread-safe
        update_context_sync_flags(prp_path, ce_verified, False)

        return {"path": prp_path, "verified": ce_verified}

    # Process in parallel
    results = process_prps_parallel(prp_files, process_single_prp, max_workers=4)

    return {"success": True, "processed": len(results)}
```

**Test**:
```python
import time

def test_parallel_processing_faster_than_sequential(tmp_path):
    """Test parallel processing improves performance."""
    # Create 20 test PRPs
    prps = []
    for i in range(20):
        prp = tmp_path / f"PRP-{i}.md"
        prp.write_text(f"---\nstatus: new\n---\nContent {i}")
        prps.append(prp)

    def slow_processor(prp_path: Path):
        time.sleep(0.1)  # Simulate I/O delay
        return prp_path.name

    # Sequential processing
    start = time.time()
    seq_results = [slow_processor(p) for p in prps]
    seq_duration = time.time() - start

    # Parallel processing
    start = time.time()
    par_results = process_prps_parallel(prps, slow_processor, max_workers=4)
    par_duration = time.time() - start

    # Parallel should be significantly faster
    assert par_duration < seq_duration * 0.6  # At least 40% faster

def test_parallel_processing_handles_errors(tmp_path):
    """Test parallel processing continues despite errors."""
    prps = [tmp_path / f"PRP-{i}.md" for i in range(5)]
    for prp in prps:
        prp.write_text("---\nstatus: new\n---\nContent")

    def failing_processor(prp_path: Path):
        if "3" in prp_path.name:
            raise ValueError("Simulated failure")
        return prp_path.name

    results = process_prps_parallel(prps, failing_processor)

    # Should have 4 successful results (5 total - 1 failure)
    assert len(results) == 4
```

**Integration**: Add as option to `sync_context()` with flag `--parallel`

---

#### 3.5 Edge Case Handling (2-3 hours)

**Problem**: No handling for NaN, Infinity, empty lists in drift calculations.

**Fix**:
```python
import math
from typing import List

def safe_drift_calculation(violations: List[str], total_checks: int) -> float:
    """Calculate drift score with edge case handling.

    Args:
        violations: List of violations
        total_checks: Total number of checks performed

    Returns:
        Drift score (0-100), handling edge cases safely
    """
    # Handle empty inputs
    if total_checks == 0:
        logger.warning("No checks performed - drift score defaults to 0%")
        return 0.0

    if not violations:
        return 0.0

    # Calculate score
    score = (len(violations) / total_checks) * 100

    # Handle mathematical edge cases
    if math.isnan(score):
        logger.error("Drift score is NaN - defaulting to 0%")
        return 0.0

    if math.isinf(score):
        logger.error("Drift score is infinite - capping at 100%")
        return 100.0

    # Clamp to valid range
    return max(0.0, min(100.0, score))

def safe_cache_age_check(generated_at: str, ttl_minutes: int) -> bool:
    """Check cache age with edge case handling.

    Args:
        generated_at: ISO timestamp string
        ttl_minutes: Cache TTL in minutes

    Returns:
        True if cache valid, False otherwise
    """
    try:
        # Handle malformed timestamps
        if not generated_at:
            return False

        generated_dt = datetime.fromisoformat(generated_at.replace("+00:00", "+00:00"))

        # Handle timezone-naive datetimes
        if generated_dt.tzinfo is None:
            generated_dt = generated_dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        age_minutes = (now - generated_dt).total_seconds() / 60

        # Handle negative age (clock skew)
        if age_minutes < 0:
            logger.warning(f"Cache timestamp in future (clock skew?): {generated_at}")
            return False

        # Handle extreme values
        if math.isinf(age_minutes) or math.isnan(age_minutes):
            logger.error(f"Invalid cache age calculation: {age_minutes}")
            return False

        return age_minutes < ttl_minutes

    except Exception as e:
        logger.error(f"Cache age check failed: {e}")
        return False
```

**Test**:
```python
def test_drift_calculation_handles_zero_checks():
    """Test drift calculation with zero checks."""
    score = safe_drift_calculation([], 0)
    assert score == 0.0

def test_drift_calculation_handles_empty_violations():
    """Test drift calculation with no violations."""
    score = safe_drift_calculation([], 100)
    assert score == 0.0

def test_drift_calculation_clamps_to_range():
    """Test drift score clamped to 0-100 range."""
    # Should never exceed 100%
    score = safe_drift_calculation(["v"] * 200, 100)
    assert score == 100.0

def test_cache_age_handles_malformed_timestamp():
    """Test cache age check with invalid timestamp."""
    assert not safe_cache_age_check("invalid-timestamp", 5)

def test_cache_age_handles_future_timestamp():
    """Test cache age check with future timestamp (clock skew)."""
    future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    assert not safe_cache_age_check(future_time, 5)

def test_cache_age_handles_empty_timestamp():
    """Test cache age check with empty timestamp."""
    assert not safe_cache_age_check("", 5)
```

**Integration**: Apply safe calculations throughout `update_context.py`

---

### Phase 4: Testing & Validation (8-12 hours)

**Unit Tests** (5-7 hours):
```bash
# Create test files for each fix
tools/tests/test_drift_calculation.py       # Phase 1.1
tools/tests/test_implementation_verification.py  # Phase 1.2
tools/tests/test_pattern_matching.py        # Phase 1.3
tools/tests/test_atomic_writes.py           # Phase 1.4
tools/tests/test_remediation.py             # Phase 1.5
tools/tests/test_cache_ttl.py               # Phase 2.1
tools/tests/test_function_extraction.py     # Phase 2.2
tools/tests/test_config_patterns.py         # Phase 2.3
tools/tests/test_transaction_rollback.py    # Phase 2.4
tools/tests/test_yaml_safety.py             # Phase 2.5
tools/tests/test_discover_prps.py           # Phase 3.1
tools/tests/test_path_matching.py           # Phase 3.2
tools/tests/test_contextual_errors.py       # Phase 3.3
tools/tests/test_parallel_processing.py     # Phase 3.4
tools/tests/test_edge_cases.py              # Phase 3.5
```

**Integration Tests** (3-5 hours):
```bash
# Test full workflows
def test_full_sync_workflow():
    """Test complete sync workflow end-to-end."""
    # Vanilla sync
    result = sync_context()
    assert result["success"]
    assert "drift_score" in result

def test_remediation_workflow_full():
    """Test remediation from detection to execution."""
    result = remediate_drift_workflow(auto_execute=True)
    assert result["executed"]
    assert len(result["fixes"]) > 0

def test_transaction_rollback_integration(tmp_path):
    """Test full transaction with rollback."""
    # Create test PRPs
    # Simulate failure mid-sync
    # Verify all changes rolled back
    pass
```

---

### Phase 5: Documentation & Rollout (2-3 hours)

**Update Docs**:
- `docs/update-context-fix-log.md` - Changelog of all fixes
- `CLAUDE.md` - Update usage examples
- `examples/` - Add atomic write pattern example

**Beta Testing**:
```bash
# Run on real codebase
cd tools && uv run ce update-context
# Verify no PRPs corrupted
# Verify drift score reasonable
```

---

## Validation Gates

### L1: Unit Tests Pass
```bash
cd tools && uv run pytest tests/test_drift_calculation.py -v
cd tools && uv run pytest tests/test_implementation_verification.py -v
cd tools && uv run pytest tests/test_pattern_matching.py -v
cd tools && uv run pytest tests/test_atomic_writes.py -v
cd tools && uv run pytest tests/test_remediation.py -v
cd tools && uv run pytest tests/test_cache_ttl.py -v
cd tools && uv run pytest tests/test_function_extraction.py -v
cd tools && uv run pytest tests/test_config_patterns.py -v
cd tools && uv run pytest tests/test_transaction_rollback.py -v
cd tools && uv run pytest tests/test_yaml_safety.py -v
cd tools && uv run pytest tests/test_discover_prps.py -v
cd tools && uv run pytest tests/test_path_matching.py -v
cd tools && uv run pytest tests/test_contextual_errors.py -v
cd tools && uv run pytest tests/test_parallel_processing.py -v
cd tools && uv run pytest tests/test_edge_cases.py -v
```

### L2: Integration Tests Pass
```bash
cd tools && uv run pytest tests/test_update_context_integration.py -v
```

### L3: Manual Validation
```bash
# Test on real PRPs
cd tools && uv run ce update-context
# Check drift score is reasonable (10-15%)
# Verify no false positives in drift report
# Confirm no PRPs corrupted
```

### L4: Pattern Conformance
```bash
cd tools && uv run ce validate --level 4
# All new code follows documented patterns
```

---

## Success Criteria

### CRITICAL (Must Pass)
- [ ] Drift score calculation correct (violation-based, not file-based)
- [ ] Implementation verification works (AST-based)
- [ ] Pattern matching handles multiline code (no false positives)
- [ ] Atomic writes prevent file corruption (tested with kill signal)
- [ ] --remediate actually remediates (auto-execute works)

### HIGH (Should Pass)
- [ ] Cache TTL respected across all functions
- [ ] Function extraction handles decorators/async/classmethods
- [ ] Pattern checks loadable from .ce/pattern-checks.yml
- [ ] Transaction rollback works on partial failures
- [ ] YAML safe loading prevents code injection

### MEDIUM (Nice to Have)
- [ ] discover_prps() includes "system" folder
- [ ] Path matching robust (symlinks, Windows paths)
- [ ] Error messages include full context
- [ ] Parallel processing improves performance
- [ ] Edge cases handled (NaN, Infinity, empty lists)

---

## Risk Mitigation

**HIGH RISK**: Changes affect all users of update-context

**Mitigation**:
1. **Feature Flag**: `CE_NEW_DRIFT_CALC=1` for gradual rollout
2. **Extensive Tests**: 30+ test cases before merge
3. **Beta Testing**: Run on sample PRPs first
4. **Rollback Plan**: Keep old implementation for fallback

---

## References

**Codebase Patterns**:
- `tools/ce/prp.py:215-219` - Atomic write pattern (temp file + rename)
- `tools/ce/pattern_detectors.py:6` - AST parsing example
- `tools/tests/test_update_context.py` - Testing conventions

**Related PRPs**:
- PRP-14: /update-context Implementation (original)
- PRP-15: Drift Detection (added drift analysis)
- PRP-17: Extract Drift Analysis (refactored)
- PRP-20: Error Handling Drift (exposed these issues)

**External Docs**:
- Python AST module: https://docs.python.org/3/library/ast.html
- Atomic file writes: https://danluu.com/file-consistency/
- YAML security: https://en.wikipedia.org/wiki/YAML#Security

---

## Confidence Assessment

**Confidence: 7/10**

**Why Not Higher**:
- Large scope (30+ issues) increases integration risk
- Drift score change is breaking change (metrics will differ)
- Transaction rollback adds complexity

**Why This High**:
- Atomic write pattern already exists in codebase
- AST parsing already used successfully
- Test patterns well-established
- Clear validation strategy with L1-L4 gates
- All phases fully detailed with implementation + tests

**One-Pass Success Probability**: 70% (with careful testing and validation)
