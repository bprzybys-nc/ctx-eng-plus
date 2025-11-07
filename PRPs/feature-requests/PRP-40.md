---
prp_id: PRP-40
title: Fix Examples Domain Migration and Blending
status: pending
created: 2025-11-07
complexity: medium
estimated_hours: 2.0
discovered_in: PRP-39 E2E testing (iteration 5)
---

# Fix Examples Domain Migration and Blending

## Executive Summary

ExamplesBlendStrategy fails when framework .ce/examples/ directory doesn't exist in package, and only processes non-recursive .md files. Need to:
1. Handle missing framework directory gracefully
2. Support recursive file discovery (patterns/ subdirectory)
3. Migrate target examples/ → .ce/examples/user/ (similar to PRPMoveStrategy)

**Impact**: MEDIUM - 20/21 examples files not migrated, cleanup fails

---

## Problem Analysis

### Current Behavior

**File**: `tools/ce/blending/strategies/examples.py:66-67`

```python
if not framework_dir.is_dir():
    raise ValueError(f"Framework examples dir not found: {framework_dir}")
```

**Issues**:
1. **Missing Framework Dir**: Raises error if .ce/examples/ not in package (it isn't)
2. **Non-Recursive**: Line 143-146 only processes `examples/*.md`, not subdirectories
3. **Wrong Direction**: Copies framework→target, but should migrate target→.ce
4. **File Type Limitation**: Only processes .md files (misses .py examples)

### Evidence from E2E Test (Iteration 5)

**Source Structure**:
```
examples/
├── *.md (3 files)                    # Only these would be processed
├── patterns/*.py (8 files)           # ❌ Skipped (subdirectory)
├── patterns/*.md (10 files)          # ❌ Skipped (subdirectory)
└── README.md                         # Would be processed
```

**Result**:
- Files detected: 21
- Files classified: 17 (4 garbage-filtered)
- Files blended: 0 (framework dir not found)
- Files migrated: 0/21 (0%)
- Cleanup failure: "20 unmigrated files detected"

### Expected Behavior

ExamplesBlendStrategy should:
1. Handle missing framework directory (skip framework blending, focus on migration)
2. Recursively find all example files (.md, .py, etc.)
3. Migrate target examples/ → .ce/examples/user/
4. Preserve subdirectory structure (patterns/, templates/, etc.)

---

## Root Cause

**Multiple Issues**:
1. **Assumption**: Strategy assumes framework examples always exist
2. **Non-Recursive**: `iterdir()` only gets immediate children
3. **Architecture Mismatch**: Should use execute() interface like PRPs, not blend()

---

## Proposed Solution

### Option A: Dual-Mode Strategy (RECOMMENDED)

Make ExamplesBlendStrategy handle both:
- **Blend Mode**: Framework exists → semantic dedup + copy
- **Migration Mode**: Framework missing → migrate user examples

**Changes to `tools/ce/blending/strategies/examples.py`**:

```python
def blend(
    self,
    framework_dir: Path,
    target_dir: Path,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Blend or migrate examples based on framework availability."""

    # Check if framework examples exist
    if not framework_dir.exists() or not framework_dir.is_dir():
        logger.info(f"Framework examples not found - migration mode")
        return self._migrate_user_examples(target_dir, context)

    # Framework exists - blend mode (semantic dedup)
    return self._blend_framework_examples(framework_dir, target_dir, context)

def _migrate_user_examples(
    self,
    source_dir: Path,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Migrate user examples from source to .ce/examples/user/.

    Similar to PRPMoveStrategy but for examples.
    """
    if not source_dir.exists():
        return {"migrated": 0, "skipped": 0, "errors": []}

    target_base = context.get("target_dir") / ".ce" / "examples" / "user"
    target_base.mkdir(parents=True, exist_ok=True)

    migrated = 0
    skipped = 0
    errors = []

    # Find all example files recursively (*.md, *.py, etc.)
    example_files = list(source_dir.rglob("*"))
    example_files = [f for f in example_files if f.is_file()]

    for source_file in example_files:
        try:
            # Preserve subdirectory structure
            relative_path = source_file.relative_to(source_dir)
            target_file = target_base / relative_path

            # Create parent directories
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Hash-based deduplication
            if target_file.exists():
                if self._hash_file(source_file) == self._hash_file(target_file):
                    skipped += 1
                    continue

            # Copy to target
            target_file.write_text(source_file.read_text())
            migrated += 1

        except Exception as e:
            errors.append(f"Error processing {source_file.name}: {e}")

    return {
        "migrated": migrated,
        "skipped": skipped,
        "errors": errors,
        "success": len(errors) == 0
    }
```

### Option B: Separate ExamplesMoveStrategy (Alternative)

Create separate strategy like PRPMoveStrategy, use execute() interface.

**Less preferred** because:
- Duplicates code
- Breaks existing blend() interface
- More complex orchestrator changes

---

## Implementation Plan

### Phase 1: Add Migration Mode (1 hour)

**Goal**: Support missing framework directory, migrate user examples

**Estimated Hours**: 1.0

**Complexity**: medium

**Files Modified**:
- tools/ce/blending/strategies/examples.py

**Dependencies**: None

**Implementation Steps**:
1. Add _migrate_user_examples() method
2. Modify blend() to detect framework presence
3. Use rglob("*") for recursive file discovery
4. Add hash-based deduplication
5. Preserve subdirectory structure (patterns/, etc.)

**Validation Gates**:
- [ ] Framework missing → migration mode activates
- [ ] All file types supported (.md, .py, etc.)
- [ ] Subdirectories preserved
- [ ] Hash deduplication works

### Phase 2: Add Unit Tests (30 minutes)

**Goal**: Test both blend and migration modes

**Estimated Hours**: 0.5

**Complexity**: low

**Files Modified**:
- tools/tests/test_examples_blend_strategy.py (new)

**Dependencies**: Phase 1

**Implementation Steps**:
1. Test migration mode (framework missing)
2. Test blend mode (framework exists)
3. Test recursive file discovery
4. Test subdirectory preservation
5. Test file type variety (.md, .py)
6. Test hash deduplication

**Validation Gates**:
- [ ] All tests pass
- [ ] Coverage for both modes
- [ ] Edge cases handled

### Phase 3: E2E Validation (30 minutes)

**Goal**: Verify 100% examples migration in init-project

**Estimated Hours**: 0.5

**Complexity**: low

**Files Modified**: None (testing only)

**Dependencies**: Phase 1, Phase 2

**Implementation Steps**:
1. Reset test target
2. Run init-project
3. Verify examples/ → .ce/examples/user/ migration
4. Verify subdirectory structure
5. Verify cleanup succeeds

**Validation Gates**:
- [ ] 20/20 examples migrated (100%)
- [ ] Subdirectories preserved (patterns/)
- [ ] Cleanup phase passes
- [ ] No unmigrated files warning

---

## Edge Cases

### Case 1: Mixed File Types

**Scenario**: examples/ contains .md, .py, .json, etc.
**Resolution**: Process all file types, not just .md

### Case 2: Framework Exists + User Examples

**Scenario**: Both framework and user examples present
**Resolution**: Blend framework first, then migrate user (no conflicts due to /user/ subdirectory)

### Case 3: Deep Nesting

**Scenario**: examples/patterns/advanced/deep/file.py
**Resolution**: Preserve full relative path

---

## Validation Gates

### Gate 1: Migration Mode Works
**Test**: Run with missing framework dir
**Criteria**: 20/20 files migrated, no errors

### Gate 2: Structure Preserved
**Test**: Check target after migration
**Criteria**: .ce/examples/user/patterns/ has all files

### Gate 3: Cleanup Succeeds
**Test**: Run full init-project
**Criteria**: No "unmigrated files" error for examples/

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Examples Migrated | 0/21 (0%) | 20/21 (95%+) |
| Subdirectories Preserved | 0/1 | 1/1 |
| File Types Supported | .md only | All types |
| Cleanup Success | ❌ FAIL | ✅ PASS |

---

## Risk Analysis

### Risk 1: Breaking Existing Blend Mode

**Description**: Changes might break framework→target blending
**Mitigation**: Keep blend mode logic unchanged, add migration mode separately
**Testing**: Test both modes

### Risk 2: Name Collisions

**Description**: examples/foo.md + patterns/foo.md → collision
**Mitigation**: Preserve subdirectory in target path
**Testing**: Unit test with duplicate names

---

## Dependencies

**Blocks**: Init-project E2E validation, PRP-38 complete validation

**Depends On**:
- PRP-39 ✅ (provides pattern for migration strategy)
- PRP-38 ✅ (blend orchestrator working)

---

## Related PRPs

- **PRP-39**: Fix PRPMoveStrategy subdirectory handling (similar pattern)
- **PRP-38**: Fix Blend Orchestrator (discovered examples issue)
- **PRP-34.3.3**: Examples NL dedupe strategy (original semantic dedupe implementation)

---

## Estimated Timeline

- **Phase 1**: 1.0 hour (migration mode implementation)
- **Phase 2**: 0.5 hours (unit tests)
- **Phase 3**: 0.5 hours (E2E validation)
- **Total**: 2.0 hours

**Complexity**: MEDIUM (need to support dual modes, but PRP-39 provides pattern)

---

## Next Actions

1. Implement migration mode in ExamplesBlendStrategy
2. Add recursive file discovery (rglob)
3. Add unit tests for both modes
4. Run E2E test to verify 100% migration
5. Update cleanup validation to pass for examples/
