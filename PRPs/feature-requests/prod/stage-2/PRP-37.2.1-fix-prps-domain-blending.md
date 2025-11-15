---
prp_id: "37.2.1"
feature_name: Fix PRPs Domain Blending
status: pending
created: "2025-11-06T00:00:00Z"
updated: "2025-11-06T00:00:00Z"
complexity: medium
estimated_hours: 2.0
dependencies: ["37.1.1"]
batch_id: 37
stage: 2
execution_order: 2
merge_order: 2
conflict_potential: medium
files_modified:
  - tools/ce/blending/core.py
---

# Fix PRPs Domain Blending

## 1. TL;DR

**Objective**: Fix PRPs domain blending failure when using `--all` flag

**What**: Pass required `source_dir` and `target_dir` parameters to PRPMoveStrategy when using `--all` flag in blend command

**Why**: Currently PRPs domain blending fails because BlendingOrchestrator passes `source_files` but PRPMoveStrategy expects `source_dir` and `target_dir` parameters

**Effort**: 2 hours (parameter interface alignment + testing)

**Dependencies**: PRP-37.1.1 (Create E2E Initialization Test)

**Part of**: PRP-36.3 (Fix Init-Project Issues from E2E Testing) - Fixes 2/6 broken domains

## 2. Context

### Background

E2E testing revealed that PRPs domain blending fails during initialization:

```
Phase C: BLENDING
  Blending settings (1 files)... ✓
  Blending claude_md (1 files)... ✓
  Blending memories (23 files)... ✓
  Blending examples (3 files)... ✓
  Blending prps (75 files)... ❌ FAILED
  Blending commands (14 files)... ✓
```

**Root Cause**: Parameter mismatch between BlendingOrchestrator and PRPMoveStrategy

**Current Flow**:
1. `BlendingOrchestrator._run_blending()` passes: `{"source_files": files, "target_dir": target_dir}`
2. `PRPMoveStrategy.execute()` expects: `{"source_dir": Path, "target_dir": Path}`
3. Strategy fails because `source_dir` is None

**Impact**: 75 PRP files not blended during initialization, leaving user with broken CE structure

### Constraints and Considerations

**Design Decisions**:
1. **Option A**: Make source_dir/target_dir optional with defaults from config
2. **Option B**: Update --all flag to pass parameters to all strategies (CHOSEN)
3. **Option C**: Auto-detect directories from config file

**Chosen Approach**: Option B
- **Rationale**: Consistent with other strategies (MemoriesBlendStrategy, ExamplesBlendStrategy use blend() interface)
- **Trade-off**: Requires orchestrator to derive source_dir from classified files
- **Benefit**: No strategy interface changes needed

**File Conflict Analysis**:
- PRP-37.2.1 modifies `tools/ce/blending/core.py` (line 328-332)
- PRP-37.3.1 modifies `tools/ce/blend.py` (line 84-91)
- No direct conflict (different files), but sequential execution recommended

### Code Quality Standards

- Functions: 50 lines max (single responsibility)
- Files: 300-500 lines (logical modules)
- KISS: Simple solutions first
- Fast failure: Let exceptions bubble up with actionable errors
- No silent corruption: All errors logged

### Documentation References

**Internal**:
- `tools/ce/blending/core.py:75-378` - BlendingOrchestrator implementation
- `tools/ce/blending/strategies/simple.py:22-189` - PRPMoveStrategy implementation
- `PRPs/executed/PRP-34.3.3-examples-blend-strategy.md` - Similar blend strategy pattern

**External**:
- None (pure Python implementation)

## 3. Implementation Steps

### Phase 1: Analysis and Design (30 min)

**Step 1.1**: Analyze parameter requirements across all strategies
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
grep -n "def execute" tools/ce/blending/strategies/*.py
grep -n "def blend" tools/ce/blending/strategies/*.py
```

**Expected Output**:
- PRPMoveStrategy: expects `source_dir`, `target_dir`
- CommandOverwriteStrategy: expects `source_dir`, `target_dir`, `backup_dir`
- Other strategies: use `blend()` interface with framework/user content

**Step 1.2**: Review BlendingOrchestrator._run_blending() logic

**Current Code** (`tools/ce/blending/core.py:318-332`):
```python
if hasattr(strategy, 'blend'):
    # BlendStrategy interface (settings, claude_md, memories, examples)
    logger.debug(f"    Using blend() interface for {domain}")
elif hasattr(strategy, 'execute'):
    # Simple strategy interface (prps, commands)
    result = strategy.execute({
        "source_files": files,
        "target_dir": target_dir,
        "dry_run": self.dry_run
    })
    results[domain] = result
```

**Problem**: `source_files` passed but `source_dir` expected

**Step 1.3**: Design solution

**Approach**: Derive `source_dir` from classified files
- For PRPs: Detect common parent directory from file paths
- For Commands: Use config to determine source directory

### Phase 2: Core Implementation (1 hour)

**Step 2.1**: Update BlendingOrchestrator._run_blending() for PRPs domain

**File**: `tools/ce/blending/core.py`

**Before** (lines 326-332):
```python
elif hasattr(strategy, 'execute'):
    # Simple strategy interface (prps, commands)
    result = strategy.execute({
        "source_files": files,
        "target_dir": target_dir,
        "dry_run": self.dry_run
    })
    results[domain] = result
```

**After**:
```python
elif hasattr(strategy, 'execute'):
    # Simple strategy interface (prps, commands)
    # Derive source_dir from classified files
    if files:
        source_dir = files[0].parent
    else:
        logger.warning(f"    No files for {domain}, skipping")
        continue

    # Domain-specific parameters
    if domain == 'prps':
        params = {
            "source_dir": source_dir,
            "target_dir": target_dir / ".ce" / "PRPs"
        }
    elif domain == 'commands':
        params = {
            "source_dir": source_dir,
            "target_dir": target_dir / ".claude" / "commands",
            "backup_dir": target_dir / ".claude" / "commands.backup"
        }
    else:
        # Fallback for unknown strategies
        params = {
            "source_files": files,
            "target_dir": target_dir,
            "dry_run": self.dry_run
        }

    result = strategy.execute(params)
    results[domain] = result
```

**Rationale**:
- Detects source_dir from first file in list
- Builds domain-specific parameter dict
- Preserves backward compatibility with fallback

**Step 2.2**: Add error handling for empty file lists

**Add before source_dir derivation**:
```python
if not files:
    logger.debug(f"  {domain}: No files to blend")
    continue
```

**Step 2.3**: Update logging for better debugging

**Add after parameter construction**:
```python
logger.debug(f"    Executing {domain} with params: {params}")
```

### Phase 3: Testing and Validation (30 min)

**Step 3.1**: Add unit test for parameter derivation

**File**: `tools/tests/test_blend_orchestrator.py` (create if not exists)

```python
def test_prps_strategy_receives_correct_parameters():
    """Test that PRPMoveStrategy receives source_dir and target_dir."""
    from pathlib import Path
    from unittest.mock import MagicMock
    from ce.blending.core import BlendingOrchestrator

    # Setup
    config = {"domains": {"prps": {}}}
    orchestrator = BlendingOrchestrator(config)

    # Mock PRPs strategy
    mock_strategy = MagicMock()
    mock_strategy.execute.return_value = {
        "prps_moved": 75,
        "prps_skipped": 0,
        "errors": []
    }
    orchestrator.strategies["prps"] = mock_strategy

    # Setup classified files
    prp_files = [
        Path("/tmp/source/PRP-1.md"),
        Path("/tmp/source/PRP-2.md")
    ]
    orchestrator.classified_files = {"prps": prp_files}

    # Execute
    target_dir = Path("/tmp/target")
    result = orchestrator._run_blending(target_dir)

    # Verify execute() called with correct params
    mock_strategy.execute.assert_called_once()
    call_args = mock_strategy.execute.call_args[0][0]

    assert "source_dir" in call_args
    assert call_args["source_dir"] == Path("/tmp/source")
    assert call_args["target_dir"] == target_dir / ".ce" / "PRPs"
```

**Step 3.2**: Run unit tests

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_orchestrator.py::test_prps_strategy_receives_correct_parameters -v
```

**Expected Output**:
```
test_blend_orchestrator.py::test_prps_strategy_receives_correct_parameters PASSED
```

**Step 3.3**: Run E2E test (requires PRP-37.1.1 completion)

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_init_project_e2e.py::test_init_project_full_pipeline -v
```

**Expected Output**:
```
Phase C: BLENDING
  Blending settings (1 files)... ✓
  Blending claude_md (1 files)... ✓
  Blending memories (23 files)... ✓
  Blending examples (3 files)... ✓
  Blending prps (75 files)... ✓  <-- NOW PASSES
  Blending commands (14 files)... ✓
```

## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_orchestrator.py::test_prps_strategy_receives_correct_parameters -v
```

**Success Criteria**:
- Test passes showing correct parameters passed to PRPMoveStrategy
- source_dir derived from first file in classified list
- target_dir constructed as `{target_dir}/.ce/PRPs`

### Gate 2: E2E Test Shows PRPs Blending Success

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_init_project_e2e.py::test_init_project_full_pipeline -v
```

**Success Criteria**:
- All 6 domains blend successfully (6/6 pass)
- Output shows: `Blending prps (75 files)... ✓`
- No regression in other 5 domains

### Gate 3: Manual Blend Test

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
# Create test directory with PRPs
mkdir -p /tmp/test-blend/PRPs
echo "# Test PRP" > /tmp/test-blend/PRPs/PRP-1.md

# Run blend
uv run ce blend --config ../examples/blend-config.yml --target-dir /tmp/test-blend --phase blend -v
```

**Success Criteria**:
- PRPs domain blends without error
- Logs show: `Blending prps (1 files)... ✓`
- File copied to `/tmp/test-blend/.ce/PRPs/`

### Gate 4: Code Quality Checks

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce validate --level 4
```

**Success Criteria**:
- All validation checks pass
- No fishy fallbacks introduced
- Error messages include troubleshooting guidance

## 5. Testing Strategy

### Test Framework

pytest (existing test suite)

### Test Command

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_orchestrator.py -v
```

### Test Coverage

**Unit Tests** (tools/tests/test_blend_orchestrator.py):
1. `test_prps_strategy_receives_correct_parameters` - Parameter derivation
2. `test_commands_strategy_receives_correct_parameters` - Commands domain
3. `test_empty_files_list_skipped` - Empty list handling
4. `test_source_dir_derived_from_first_file` - Source dir detection

**Integration Tests** (tools/tests/test_init_project_e2e.py):
1. `test_init_project_full_pipeline` - E2E blend with all 6 domains
2. `test_prps_domain_blending` - Isolated PRPs domain test

### Mock Strategy

**Real**: BlendingOrchestrator, PRPMoveStrategy
**Mock**: File system (use tmp directories), LLM client (dry-run mode)

### Edge Cases

1. **Empty PRPs list**: Should skip domain gracefully
2. **Single PRP file**: Should derive source_dir from parent
3. **Mixed directory PRPs**: Should detect common parent
4. **Missing target directory**: Should create with mkdir(parents=True)

## 6. Rollout Plan

### Phase 1: Development

1. Implement parameter derivation logic in BlendingOrchestrator
2. Add unit tests for parameter passing
3. Run local validation: `uv run pytest tests/test_blend_orchestrator.py -v`

### Phase 2: Review

1. Code review: Check parameter derivation logic
2. Test review: Verify edge cases covered
3. Documentation review: Update CLAUDE.md if needed

### Phase 3: Merge

1. Merge PRP-37.1.1 first (E2E test dependency)
2. Merge PRP-37.2.1 (this PRP)
3. Verify E2E test passes with both PRPs merged

### Phase 4: Verification

1. Run full test suite: `uv run pytest tests/ -v`
2. Run E2E test: `uv run pytest tests/test_init_project_e2e.py -v`
3. Manual smoke test: `uv run ce blend --all --config ../examples/blend-config.yml --target-dir /tmp/test`

---

## Research Findings

### Codebase Analysis

**PRPMoveStrategy Interface** (`tools/ce/blending/strategies/simple.py:42-58`):
```python
def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute PRP move strategy.

    Args:
        input_data: {
            "source_dir": Path to source PRPs directory,
            "target_dir": Path to target .ce/PRPs directory
        }
    """
    source_dir = input_data.get("source_dir")
    target_dir = input_data.get("target_dir")

    if not source_dir or not target_dir:
        raise ValueError("source_dir and target_dir are required")
```

**BlendingOrchestrator Call** (`tools/ce/blending/core.py:326-332`):
```python
result = strategy.execute({
    "source_files": files,  # <-- WRONG: should be source_dir
    "target_dir": target_dir,
    "dry_run": self.dry_run
})
```

**Mismatch**: orchestrator passes `source_files`, strategy expects `source_dir`

### Similar Strategy Patterns

**CommandOverwriteStrategy** (`tools/ce/blending/strategies/simple.py:210-232`):
- Also uses `execute()` interface
- Also expects `source_dir` parameter
- Has same issue (not called by orchestrator yet)

**MemoriesBlendStrategy** (`tools/ce/blending/strategies/memories.py`):
- Uses `blend()` interface (different pattern)
- Receives content directly, not file paths

### Detection Phase Output

**Detection** (`tools/ce/blending/detection.py`):
- Returns: `Dict[str, List[Path]]` (domain -> file paths)
- Example: `{"prps": [Path("/tmp/PRPs/PRP-1.md"), Path("/tmp/PRPs/PRP-2.md")]}`

**Classification** (`tools/ce/blending/core.py:256-267`):
- Filters garbage files
- Preserves same structure: `Dict[str, List[Path]]`

**Blending** (current issue):
- Receives: `files = [Path("/tmp/PRPs/PRP-1.md"), ...]`
- Needs: `source_dir = Path("/tmp/PRPs")`
- Solution: Derive parent from first file

---

## Conflict Notes

**File Modified**: `tools/ce/blending/core.py`

**Conflict Potential**: Medium
- PRP-37.3.1 modifies different file (`tools/ce/blend.py`)
- No direct line-level conflict expected
- Sequential execution in Stage 3 ensures clean merge

**Resolution Strategy**: Execute PRP-37.2.1 in Stage 2, PRP-37.3.1 in Stage 3

---

## Linear Integration

**Issue Created**: To be populated by /generate-prp
**Project**: Context Engineering
**Assignee**: blazej.przybyszewski@gmail.com
**Team**: Blaise78
**Labels**: batch-37, stage-2, domain-blending, bug-fix
