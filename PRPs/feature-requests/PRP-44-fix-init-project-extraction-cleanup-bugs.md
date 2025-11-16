---
prp_id: PRP-44
feature_name: Fix Init-Project Extraction and Cleanup Bugs
status: pending
created: 2025-11-16T12:30:00Z
updated: 2025-11-16T12:30:00Z
complexity: medium
estimated_hours: 5-7
dependencies: PRP-42, pytest
issue: BLA-57
---

# Fix Init-Project Extraction and Cleanup Bugs

## 1. TL;DR

**Objective**: Fix 3 critical bugs in init-project + Linear MCP integration

**What**: Apply code fixes to:
1. `tools/ce/init_project.py` - Fix 3 extraction/cleanup bugs
2. `tools/ce/linear_utils.py` - Implement actual MCP tool call
3. Documentation - Update tool usage examples

**Init-Project Bugs**:
1. Nested `.ce/.ce/` directory duplication (Bug #1)
2. Orphaned `.ce/.serena/` temporary directory (Bug #2)
3. Missing `.ce/PRPs/feature-requests/` directory (Bug #3)

**Linear MCP Bug**:
4. `create_issue_with_defaults()` doesn't call MCP tool (just returns data)

**Why**: Iteration 8 testing showed 4/7 validation gates failing (57% success rate). These bugs were documented in `tmp/INITIAL-init-project-fixes.md` but never implemented. PRP-42 added validation gates that detect the bugs, but didn't fix the root causes.

**Effort**: 5-7 hours (3h implementation + 2h testing + 1-2h iteration 9 validation)

**Dependencies**: PRP-42 (validation gates), pytest

## 2. Context

### Background

**Problem**: init-project creates broken CE framework installations due to extraction/cleanup bugs

**Evidence from Iteration 8** (2025-11-16):
- Gate 1 FAILED: `.ce/.ce/` nested directory exists
- Gate 3 FAILED: `.ce/PRPs/feature-requests/` missing
- Gate 4 FAILED: `.ce/.serena/` not cleaned up after blending
- Gates 2, 5, 6, 7 PASSED: Examples, memories, config, target preservation working

**Timeline**:
1. Iteration 7 (2025-11-15): Identified 5 bugs, documented in `tmp/INITIAL-init-project-fixes.md`
2. PRP-42 executed: Added 4 validation gates, but didn't fix bugs
3. Iteration 8 (2025-11-16): Same bugs persist, 3/7 gates still failing

**Root Causes**:
1. **Bug #1** (lines 525-548): Extraction moves `.ce/` contents to target `.ce/`, then moves `.ce/` directory itself → creates `.ce/.ce/` duplication
2. **Bug #2** (after blend): Blend phase merges memories but doesn't cleanup `.ce/.serena/` temporary staging directory
3. **Bug #3** (after extraction): Only creates `executed/` subdirectory, never creates `feature-requests/`

### Constraints and Considerations

**Security**:
- No changes to validation gates or package structure
- Surgical fixes only (3 small code changes)
- No impact on rollback or error handling

**Breaking Changes**:
- None - internal bug fixes only
- No API changes
- Backward compatible

**Files Modified**:
1. `tools/ce/init_project.py` - Three surgical fixes:
   - Lines 525-548: Delete `.ce/` after moving contents (Bug #1)
   - After blend: Cleanup `.ce/.serena/` directory (Bug #2)
   - After extraction: Create `feature-requests/` directory (Bug #3)

2. `tools/ce/linear_utils.py` - Implement MCP tool call:
   - Lines 111-113: Replace stub with actual `mcp__syntropy__linear_create_issue` call
   - Add proper error handling and response parsing

3. `tools/tests/test_init_project.py` - Unit tests for init-project fixes

4. `tools/tests/test_init_project_integration.py` - Integration test on clean target

5. `tools/tests/test_linear_utils.py` - Unit tests for Linear MCP integration

6. `CLAUDE.md` or `.serena/memories/linear-mcp-integration.md` - Update examples with correct `team` parameter

**Risks**:
1. Cleanup might delete user files → Mitigated: Only delete framework temp directories
2. Tests might not catch edge cases → Mitigated: Full iteration 9 validation
3. Regression in existing functionality → Mitigated: All 7 gates must pass

### Documentation References

**Related Documents**:
- `tmp/INITIAL-init-project-fixes.md` - Original bug documentation with detailed analysis
- `tmp/iteration-8-report.md` - Post-mortem showing 3/7 gates failed
- `PRPs/executed/PRP-42-init-project-workflow-overhaul.md` - Added gates, not bug fixes
- `.claude/commands/iteration.md` - 7 validation gates definition

**Testing Standards**:
- Follow `testing-standards.md` memory pattern
- TDD: Write tests first → fail → implement → refactor
- Real functionality: No mocks in production code

## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

**Step 1.1**: Verify current state
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus

# Check iteration 8 evidence
ls -la tmp/iteration-8-report.md
ls -la tmp/gate-1-framework-structure-result.json
ls -la tmp/gate-3-prps-migration-result.json
ls -la tmp/gate-4-blended-memories-result.json

# Read current init_project.py code
cat tools/ce/init_project.py | grep -A 30 "First, move .ce/"
```

**Step 1.2**: Read related code sections
```python
# Read extraction logic (Bug #1)
Read(file_path="tools/ce/init_project.py", offset=525, limit=30)

# Read blend logic (Bug #2)
Read(file_path="tools/ce/init_project.py", offset=629, limit=50)

# Search for PRP directory creation
Grep(pattern="PRPs.*mkdir", path="tools/ce/init_project.py", output_mode="content")
```

**Step 1.3**: Review test structure
```bash
# Check existing tests
ls -la tools/tests/test_init_project.py
grep "def test_" tools/tests/test_init_project.py
```

### Phase 2: Implement Bug Fixes (2 hours)

**Step 2.1**: Fix Bug #1 - Delete `.ce/` after moving contents

**File**: `tools/ce/init_project.py`
**Lines**: 525-548

**Current code**:
```python
# First, move .ce/ contents to target/.ce/
ce_extracted = temp_extract / ".ce"
if ce_extracted.exists():
    for item in ce_extracted.iterdir():
        dest = self.ce_dir / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(dest))

# Then, move other extracted directories to target/.ce/
for item in temp_extract.iterdir():
    if item.name == ".ce":
        continue  # Already processed
    # ... rest of code
```

**Fixed code**:
```python
# First, move .ce/ contents to target/.ce/
ce_extracted = temp_extract / ".ce"
if ce_extracted.exists():
    for item in ce_extracted.iterdir():
        dest = self.ce_dir / item.name
        if dest.exists():
            if dest.is_dir():
                shutil.rmtree(dest)
            else:
                dest.unlink()
        shutil.move(str(item), str(dest))

    # FIX BUG #1: Delete empty .ce/ directory after moving contents
    shutil.rmtree(ce_extracted)
    self.error_logger.info("Cleaned up extracted .ce/ directory")

# Then, move other extracted directories to target/.ce/
# (no .ce check needed - already deleted above)
for item in temp_extract.iterdir():
    dest = self.ce_dir / item.name
    if dest.exists():
        if dest.is_dir():
            shutil.rmtree(dest)
        else:
            dest.unlink()
    shutil.move(str(item), str(dest))
```

**Changes**:
1. Add `shutil.rmtree(ce_extracted)` after moving .ce/ contents
2. Add logging: `self.error_logger.info("Cleaned up extracted .ce/ directory")`
3. Remove unnecessary `.ce` skip check in second loop (already deleted)

**Step 2.2**: Fix Bug #2 - Cleanup `.ce/.serena/` after blending

**File**: `tools/ce/init_project.py`
**Lines**: After 637 (after existing cleanup)

**Current code** (lines 629-637):
```python
# Cleanup: Remove framework .claude/ and CLAUDE.md from .ce/ after blending
ce_claude = self.ce_dir / ".claude"
ce_claude_md = self.ce_dir / "CLAUDE.md"

if ce_claude.exists():
    shutil.rmtree(ce_claude)
if ce_claude_md.exists():
    ce_claude_md.unlink()
```

**Fixed code**:
```python
# Cleanup: Remove framework .claude/ and CLAUDE.md from .ce/ after blending
ce_claude = self.ce_dir / ".claude"
ce_claude_md = self.ce_dir / "CLAUDE.md"
ce_serena = self.ce_dir / ".serena"  # ADD THIS

if ce_claude.exists():
    shutil.rmtree(ce_claude)
if ce_claude_md.exists():
    ce_claude_md.unlink()

# FIX BUG #2: Cleanup temporary framework memories after blending
if ce_serena.exists():
    shutil.rmtree(ce_serena)
    if self.error_logger:
        self.error_logger.info("Cleaned up temporary framework memories (.ce/.serena/)")
```

**Changes**:
1. Add `ce_serena = self.ce_dir / ".serena"` variable
2. Add cleanup block after existing cleanup
3. Add logging

**Step 2.3**: Fix Bug #3 - Create `feature-requests/` directory

**File**: `tools/ce/init_project.py`
**Lines**: After 548 (after file reorganization)

**Add after line 548**:
```python
# FIX BUG #3: Ensure complete PRP directory structure
prps_dir = self.ce_dir / "PRPs"
(prps_dir / "executed").mkdir(parents=True, exist_ok=True)
(prps_dir / "feature-requests").mkdir(parents=True, exist_ok=True)
self.error_logger.info("Created PRP directory structure (executed + feature-requests)")
```

**Changes**:
1. Create both `executed/` and `feature-requests/` subdirectories
2. Use `mkdir(parents=True, exist_ok=True)` for idempotency
3. Add logging

**Step 2.4**: Fix Bug #4 - Implement Linear MCP tool call

**File**: `tools/ce/linear_utils.py`
**Lines**: 111-113

**Current code** (stub):
```python
logger.info(f"Creating Linear issue with defaults: {title}")
logger.debug(f"Issue data: {issue_data}")

# Note: Actual MCP call would go here
# For now, return the prepared data structure
return issue_data
```

**Fixed code**:
```python
logger.info(f"Creating Linear issue with defaults: {title}")
logger.debug(f"Issue data: {issue_data}")

# Call Linear MCP tool
try:
    # Import at runtime to avoid circular dependency
    import anthropic_mcp

    response = anthropic_mcp.call_tool(
        "mcp__syntropy__linear_create_issue",
        {
            "title": issue_data["title"],
            "team": issue_data["team"],  # CRITICAL: Use "team" not "team_id"
            "description": issue_data["description"]
        }
    )

    # Parse response
    if response and "content" in response:
        result = json.loads(response["content"][0]["text"])
        logger.info(f"Created Linear issue: {result.get('identifier', 'unknown')}")
        return result
    else:
        logger.error(f"Invalid Linear MCP response: {response}")
        return issue_data  # Fallback to prepared data

except Exception as e:
    logger.error(f"Failed to create Linear issue via MCP: {e}")
    logger.warning("Returning prepared data structure as fallback")
    return issue_data
```

**Changes**:
1. Replace stub with actual `mcp__syntropy__linear_create_issue` call
2. Use correct parameter name: `team` (not `team_id`)
3. Add error handling with fallback to prepared data
4. Parse JSON response and extract issue details
5. Log success/failure

### Phase 3: Write Tests (2 hours)

**Step 3.1**: Unit test for Bug #1 (nested .ce/ cleanup)

**File**: `tools/tests/test_init_project.py`

```python
def test_extraction_no_nested_ce(tmp_path):
    """Ensure .ce/.ce/ duplication doesn't occur (Bug #1)."""
    # Setup: Create temp extraction with .ce/ dir
    temp_extract = tmp_path / "extraction"
    (temp_extract / ".ce" / "examples").mkdir(parents=True)
    (temp_extract / "examples").mkdir(parents=True)

    # Create test files
    (temp_extract / ".ce" / "examples" / "test.md").write_text("framework example")
    (temp_extract / "examples" / "test.md").write_text("for blending")

    # Mock ProjectInitializer with minimal setup
    target = tmp_path / "target"
    target.mkdir()

    initializer = ProjectInitializer(
        target_project=target,
        ctx_eng_root=Path.cwd().parent
    )
    initializer.ce_dir = target / ".ce"
    initializer.ce_dir.mkdir()
    initializer.error_logger = ErrorLogger(target)

    # Simulate extraction reorganization (lines 525-548 logic)
    ce_extracted = temp_extract / ".ce"
    if ce_extracted.exists():
        for item in ce_extracted.iterdir():
            dest = initializer.ce_dir / item.name
            if dest.exists():
                shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
            shutil.move(str(item), str(dest))

        # THIS IS THE FIX
        shutil.rmtree(ce_extracted)

    for item in temp_extract.iterdir():
        dest = initializer.ce_dir / item.name
        if dest.exists():
            shutil.rmtree(dest) if dest.is_dir() else dest.unlink()
        shutil.move(str(item), str(dest))

    # Assert .ce/.ce/ does NOT exist
    assert not (initializer.ce_dir / ".ce").exists(), \
        "Nested .ce/.ce/ directory should not exist after extraction"

    # Assert .ce/examples/ exists (not .ce/.ce/examples/)
    assert (initializer.ce_dir / "examples").exists(), \
        ".ce/examples/ should exist at correct location"

    # Assert framework example file exists
    assert (initializer.ce_dir / "examples" / "test.md").exists()
```

**Step 3.2**: Unit test for Bug #2 (.ce/.serena/ cleanup)

```python
def test_blend_cleanup_temp_serena(tmp_path):
    """Ensure .ce/.serena/ cleaned up after blending (Bug #2)."""
    # Setup: Create .ce/.serena/ with framework memories
    target = tmp_path / "target"
    target.mkdir()

    ce_dir = target / ".ce"
    ce_serena = ce_dir / ".serena" / "memories"
    ce_serena.mkdir(parents=True)

    # Create framework memory files
    (ce_serena / "code-style-conventions.md").write_text("# Framework memory")
    (ce_serena / "testing-standards.md").write_text("# Testing standards")

    # Simulate blend cleanup (lines 629-643 logic)
    ce_serena_parent = ce_dir / ".serena"
    if ce_serena_parent.exists():
        shutil.rmtree(ce_serena_parent)

    # Assert .ce/.serena/ does NOT exist after cleanup
    assert not (ce_dir / ".serena").exists(), \
        ".ce/.serena/ should be deleted after blending"
```

**Step 3.3**: Unit test for Bug #3 (feature-requests/ directory)

```python
def test_prps_directory_structure(tmp_path):
    """Ensure both PRP subdirectories created (Bug #3)."""
    # Setup
    target = tmp_path / "target"
    ce_dir = target / ".ce"
    ce_dir.mkdir(parents=True)

    # Simulate PRP directory creation (new code after line 548)
    prps_dir = ce_dir / "PRPs"
    (prps_dir / "executed").mkdir(parents=True, exist_ok=True)
    (prps_dir / "feature-requests").mkdir(parents=True, exist_ok=True)

    # Assert both subdirectories exist
    assert (ce_dir / "PRPs" / "executed").exists(), \
        ".ce/PRPs/executed/ should exist"
    assert (ce_dir / "PRPs" / "feature-requests").exists(), \
        ".ce/PRPs/feature-requests/ should exist"
```

**Step 3.4**: Integration test (full init-project)

**File**: `tools/tests/test_init_project_integration.py` (create if needed)

```python
import subprocess
import shutil
from pathlib import Path
import pytest

@pytest.mark.slow
def test_full_init_on_clean_target(tmp_path):
    """Full init-project run on clean target, verify all 7 gates pass."""
    # Clone certinia-test-target to temp dir
    target = tmp_path / "test-target"
    shutil.copytree(
        "/Users/bprzybyszi/nc-src/certinia-test-target",
        target,
        symlinks=False,
        ignore_dangling_symlinks=True
    )

    # Reset to origin/main HEAD
    subprocess.run(["git", "reset", "--hard", "origin/main"], cwd=target, check=True)
    subprocess.run(["git", "clean", "-fdx"], cwd=target, check=True)

    # Run init-project
    result = subprocess.run(
        ["uv", "run", "ce", "init-project", str(target)],
        cwd=Path.cwd().parent / "tools",
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, \
        f"init-project failed: {result.stderr}"

    # Verify Bug #1 fixed: No nested .ce/.ce/
    assert not (target / ".ce" / ".ce").exists(), \
        "Nested .ce/.ce/ should not exist"

    # Verify Bug #2 fixed: No orphaned .ce/.serena/
    assert not (target / ".ce" / ".serena").exists(), \
        ".ce/.serena/ should be deleted after blending"

    # Verify Bug #3 fixed: feature-requests/ exists
    assert (target / ".ce" / "PRPs" / "feature-requests").exists(), \
        ".ce/PRPs/feature-requests/ should exist"

    # Verify core structure correct
    assert (target / ".ce" / "examples").exists()
    assert (target / ".serena" / "memories").exists()
    assert (target / ".claude" / "commands").exists()

    # Verify target project preserved
    assert (target / "src").exists()
    assert (target / "tests").exists()
```

### Phase 4: Run Tests and Iterate (1 hour)

**Step 4.1**: Run unit tests
```bash
cd tools

# Run specific test file
uv run pytest tests/test_init_project.py::test_extraction_no_nested_ce -v
uv run pytest tests/test_init_project.py::test_blend_cleanup_temp_serena -v
uv run pytest tests/test_init_project.py::test_prps_directory_structure -v

# Run all init_project tests
uv run pytest tests/test_init_project.py -v
```

**Expected output**:
```
tests/test_init_project.py::test_extraction_no_nested_ce PASSED
tests/test_init_project.py::test_blend_cleanup_temp_serena PASSED
tests/test_init_project.py::test_prps_directory_structure PASSED
```

**Step 4.2**: Run integration test
```bash
# Warning: Takes ~3-5 minutes (full init-project run)
uv run pytest tests/test_init_project_integration.py::test_full_init_on_clean_target -v -s
```

**Step 4.3**: Fix any test failures

If tests fail:
1. Review error messages
2. Check if fix was applied correctly
3. Adjust code or tests as needed
4. Re-run tests

### Phase 5: Iteration 9 Validation (1-2 hours)

**Step 5.1**: Run iteration 9 on certinia-test-target
```bash
# From ctx-eng-plus root
/iteration certinia-test-target
```

**Step 5.2**: Verify all 7 gates pass
```bash
# Check gate results
cat tmp/gate-1-framework-structure-result.json
cat tmp/gate-3-prps-migration-result.json
cat tmp/gate-4-blended-memories-result.json
cat tmp/gate-2-examples-migration-result.json
cat tmp/gate-5-critical-memories-result.json
cat tmp/gate-6-configuration-completeness-result.json
cat tmp/gate-7-target-project-preservation-result.json

# All should show "status": "PASS"
```

**Step 5.3**: Review iteration 9 report
```bash
cat tmp/iteration-9-report.md
```

**Expected results**:
- Gates Passed: 7/7 (vs 4/7 in iteration 8)
- Overall Status: ✅ SUCCESS (vs ⚠️ PARTIAL SUCCESS)
- No directory duplication issues
- Clean structure validation

## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**:
```bash
cd tools
uv run pytest tests/test_init_project.py -v
```

**Success Criteria**:
- All 3 new tests pass (nested_ce, temp_serena, prps_structure)
- No regressions in existing tests
- Test coverage ≥90% on modified code

### Gate 2: Integration Test Passes

**Command**:
```bash
cd tools
uv run pytest tests/test_init_project_integration.py::test_full_init_on_clean_target -v
```

**Success Criteria**:
- init-project completes successfully
- All 3 bugs verified fixed
- Target project structure intact

### Gate 3: Iteration 9 Validates All Fixes

**Command**:
```bash
/iteration certinia-test-target
```

**Success Criteria**:
- 7/7 validation gates pass (vs 4/7 in iteration 8)
- Gate 1: Framework structure preserved ✅
- Gate 3: PRPs migration complete ✅
- Gate 4: Blended memories clean ✅
- Gates 2, 5, 6, 7: Continue to pass ✅

### Gate 4: Manual Verification

**Commands**:
```bash
cd /Users/bprzybyszi/nc-src/certinia-test-target

# Verify no duplication
ls -la .ce/.ce          # Should NOT exist
ls -la .ce/.serena      # Should NOT exist

# Verify correct structure
ls -la .ce/examples/    # Should exist with files
ls -la .serena/memories/  # Should exist with blended files

# Verify PRP structure
ls -la .ce/PRPs/executed/          # Should exist
ls -la .ce/PRPs/feature-requests/  # Should exist (FIX)

# Verify target preserved
ls -la src/     # Should exist
ls -la tests/   # Should exist
```

**Success Criteria**:
- No nested directories
- Complete PRP structure
- Target project intact

## 5. Testing Strategy

### Test Framework

**Primary**: pytest (existing framework)
**Coverage tool**: pytest-cov

### Test Commands

```bash
# Unit tests only (fast)
cd tools
uv run pytest tests/test_init_project.py -v

# Integration test (slow, ~3-5 min)
uv run pytest tests/test_init_project_integration.py -v -s

# All tests with coverage
uv run pytest tests/test_init_project*.py -v --cov=ce.init_project --cov-report=term-missing

# Iteration validation (comprehensive, ~2 min)
/iteration certinia-test-target
```

### Test Coverage Targets

- **Unit tests**: ≥90% coverage on `init_project.py` modified sections
- **Integration test**: 100% coverage of bug fix scenarios
- **Iteration test**: All 7 validation gates pass

### Test Data

**Unit tests**: Use `tmp_path` fixtures (pytest built-in)
**Integration test**: Clone certinia-test-target to temp directory
**Iteration test**: Run on actual certinia-test-target project

### Edge Cases

1. **Empty .ce/ directory**: Should not crash, just skip
2. **Missing PRPs/ directory**: Should create with both subdirectories
3. **Existing feature-requests/**: Should not fail (idempotent)
4. **No .serena/ to cleanup**: Should not fail (check exists first)

## 6. Rollout Plan

### Phase 1: Development

**Duration**: 4 hours

**Tasks**:
1. Implement 3 bug fixes in `init_project.py`
2. Write 3 unit tests
3. Write 1 integration test
4. Run all tests, verify passing

**Validation**: All tests pass, no regressions

### Phase 2: Iteration Testing

**Duration**: 1 hour

**Tasks**:
1. Run `/iteration certinia-test-target`
2. Verify 7/7 gates pass
3. Review iteration-9-report.md
4. Manual verification of directory structure

**Validation**: Iteration 9 shows ✅ SUCCESS status

### Phase 3: Code Review

**Duration**: 30 min

**Tasks**:
1. Review all code changes (3 fixes)
2. Verify tests are comprehensive
3. Check for any edge cases missed
4. Ensure error messages are actionable

**Validation**: Code review approved

### Phase 4: Merge and Deploy

**Duration**: 30 min

**Tasks**:
1. Commit changes with message referencing PRP-44
2. Update PRP status to "completed"
3. Update Linear issue (if created)
4. Document in changelog

**Validation**: Changes merged to main branch

### Phase 5: Verification

**Duration**: 30 min

**Tasks**:
1. Run init-project on different target project (mlx-trading-pipeline)
2. Verify clean installation
3. Run all 7 gates
4. Confirm no regressions

**Validation**: Clean installation on new target

---

## Research Findings

### Codebase Analysis

**File**: `tools/ce/init_project.py`

**Key Methods**:
- `extract()` (lines 393-588): Contains Bug #1 and Bug #3
- `blend()` (lines 590-685): Contains Bug #2 cleanup location

**Current Structure**:
```
ProjectInitializer
├── extract()      # Extraction + file reorganization
│   ├── Gate 1: Preflight checks
│   ├── Gate 2: File count validation
│   └── File reorganization (BUGS #1, #3)
├── blend()        # Blending framework + user files
│   ├── Subprocess call to blend command
│   ├── Cleanup .claude/ and CLAUDE.md (existing)
│   └── Gate 3: Blend validation (BUG #2)
├── initialize()   # Python environment setup
└── verify()       # Final validation
```

**Related Files**:
- `tools/ce/blending/` - Blend logic (external to init_project.py)
- `.claude/commands/iteration.md` - 7 validation gate definitions
- `PRPs/executed/PRP-42-init-project-workflow-overhaul.md` - Added gates

### Testing Patterns

**Existing tests** in `tools/tests/test_init_project.py`:
- Test file count: ~200 lines
- Uses pytest fixtures
- Tests extraction, blending, initialization phases
- No tests for cleanup logic (gap!)

**Test pattern to follow**:
```python
def test_something(tmp_path):
    """Test description."""
    # Setup
    target = tmp_path / "target"
    target.mkdir()

    # Execute
    result = some_function(target)

    # Assert
    assert result is True
    assert (target / "expected").exists()
```

### Evidence from Iteration 8

**Gate 1 Result** (`tmp/gate-1-framework-structure-result.json`):
```json
{
  "gate": 1,
  "name": "Framework Structure Preserved",
  "status": "FAIL",
  "checks": {
    "ce_examples_exists": true,
    "ce_prps_exists": true,
    "ce_nested_ce_not_exists": false,  ← BUG #1
    "ce_nested_serena_not_exists": false,  ← BUG #2
    "ce_memories_not_exists": true
  }
}
```

**Gate 3 Result**:
```json
{
  "gate": 3,
  "name": "PRPs Migration",
  "status": "FAIL",
  "checks": {
    "ce_prps_exists": true,
    "executed_dir_exists": true,
    "feature_requests_dir_exists": false,  ← BUG #3
    "prp_file_count": 1,
    "root_prps_not_exists": true
  }
}
```

**Gate 4 Result**:
```json
{
  "gate": 4,
  "name": "Blended Memories",
  "status": "FAIL",
  "checks": {
    "serena_memories_exists": true,
    "serena_old_not_exists": true,
    "ce_serena_not_exists": false,  ← BUG #2
    "memory_file_count": 47
  }
}
```

### Success Metrics from Iteration 8 Report

**Current** (Iteration 8):
- Gates Passed: 4/7 (57%)
- Confidence Score: 5/10

**Target** (Iteration 9):
- Gates Passed: 7/7 (100%)
- Confidence Score: 10/10
- Clean directory structure
- No manual cleanup required
