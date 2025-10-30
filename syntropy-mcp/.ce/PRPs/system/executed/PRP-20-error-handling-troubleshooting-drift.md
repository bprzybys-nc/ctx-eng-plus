---
author: Blazej Przybyszewski
category: code-quality
context_sync:
  ce_updated: false
  last_sync: '2025-10-19T14:38:50.170954+00:00'
  serena_updated: false
created_date: '2025-10-17T15:00:00Z'
description: "Add \U0001F527 Troubleshooting guidance to all error messages across
  16 files missing actionable error recovery instructions"
issue: BLA-33
last_updated: '2025-10-17T18:00:00Z'
name: Error Handling Troubleshooting Guidance Drift Remediation
priority: high
prp_id: PRP-20
status: executed
updated: '2025-10-19T14:38:50.171199+00:00'
updated_by: update-context-command
version: 1
---

# PRP-20: Error Handling Troubleshooting Guidance Drift Remediation

## Executive Summary

**Drift Score**: 16.7% (🚨 CRITICAL)

Context Engineering drift detection found **30+ violations** across **16 files** where error messages lack 🔧 Troubleshooting guidance per documented pattern (`examples/patterns/error-recovery.py`).

**Pattern Violation**: Errors raised without actionable troubleshooting steps.

**Impact**: Users face cryptic errors without recovery guidance, increasing debugging time and support burden.

**Solution**: Systematically add 🔧 Troubleshooting guidance to all `raise` statements following established pattern.

## Problem Statement

### Current State

**Drift Detection Results** (2025-10-17):
- **Files Affected**: 16 (`blueprint_parser.py`, `context.py`, `pipeline.py`, `pattern_extractor.py`, `resilience.py`, `core.py`, `execute.py`, `drift.py`, `linear_utils.py`, `metrics.py`, `prp.py`, `mcp_adapter.py`, `markdown_lint.py`, `update_context.py`, `testing/builder.py`, `testing/mocks.py`)
- **Total Violations**: 30+ error messages missing troubleshooting guidance
- **Drift Score**: 16.7% (CRITICAL - threshold is 5%)

### Pattern Standard (from `examples/patterns/error-recovery.py`)

**Required Pattern**:
```python
raise FileNotFoundError(
    f"File not found: {file_path}\n"
    f"🔧 Troubleshooting:\n"
    f"   - Verify path is correct\n"
    f"   - Check if file was moved or renamed\n"
    f"   - Use: ls {path.parent} to list directory"
)
```

**Current Anti-Pattern** (found in codebase):
```python
# ❌ Missing troubleshooting guidance
raise RuntimeError(
    f"Command failed: {cmd}\n"
    f"Error: {str(e)}\n"
)
```

### Impact

1. **User Experience**: Cryptic errors without recovery steps
2. **Support Burden**: Repeated questions about same errors
3. **Pattern Erosion**: New code follows bad examples
4. **Drift Accumulation**: 16.7% drift violates <5% policy

## Solution Overview

### Approach

Systematic file-by-file remediation adding 🔧 Troubleshooting guidance to all `raise` statements.

**Strategy**:
1. **Phase 1**: High-priority files (blueprint_parser, context, execute) - 14 violations
2. **Phase 2**: Medium-priority files (pipeline, resilience, core, prp) - 8 violations
3. **Phase 3**: Low-priority files (remaining 9 files) - 8+ violations
4. **Phase 4**: Validation and drift verification

**Pattern Application**:
- Add 🔧 emoji marker for visibility
- Include 2-3 actionable troubleshooting steps
- Reference relevant commands/paths when applicable
- Keep guidance concise (1-3 lines max per step)

## 🛠️ Implementation Blueprint

### Phase 1: High-Priority Files (3 hours)

**Goal**: Fix error handling in core execution path files

**Approach**: Add troubleshooting guidance to `blueprint_parser.py`, `context.py`, `execute.py`

**Files to Modify**:
- `tools/ce/blueprint_parser.py` - 4 violations (lines 88, 100, 171-177 partially done)
- `tools/ce/context.py` - 6 violations (lines 26, 182, 294, 305, 400, 414)
- `tools/ce/execute.py` - 7 violations (lines 132, 173, 184, 315, 359, 434, 451)
- Total: 14 violations

**Violations Fixed**:

#### blueprint_parser.py
```python
# Line 88 - Missing troubleshooting
raise BlueprintParseError(
    prp_path,
    "Missing '## 🛠️ Implementation Blueprint' section"
)
# ✅ Fix: Add guidance
raise BlueprintParseError(
    prp_path,
    "Missing '## 🛠️ Implementation Blueprint' section\n"
    "🔧 Troubleshooting:\n"
    "   - Ensure PRP file contains Implementation Blueprint section\n"
    "   - Check section header format (must include 🛠️ emoji)\n"
    "   - Reference: examples/system-prps/ for correct format"
)

# Line 100 - Missing troubleshooting
raise BlueprintParseError(
    prp_path,
    "No phases found (expected '### Phase N: Name (X hours)' format)"
)
# ✅ Fix: Add guidance
raise BlueprintParseError(
    prp_path,
    "No phases found (expected '### Phase N: Name (X hours)' format)\n"
    "🔧 Troubleshooting:\n"
    "   - Add phase sections: ### Phase 1: Name (X hours)\n"
    "   - Ensure phases are numbered sequentially\n"
    "   - Reference: examples/system-prps/example-simple-feature.md"
)
```

#### context.py
```python
# Lines 26, 182, 294, 305, 400, 414 - Missing troubleshooting
# Pattern: Add specific recovery steps for each error type
```

#### execute.py
```python
# Lines 132, 173, 184, 315, 359, 434, 451 - Missing troubleshooting
# Pattern: Reference specific commands/files for recovery
```

**Validation Command**: `cd tools && uv run pytest tests/ -v`

**Checkpoint**: `git add tools/ce/blueprint_parser.py tools/ce/context.py tools/ce/execute.py && git commit -m "fix(drift): add troubleshooting to phase 1 files"`

### Phase 2: Medium-Priority Files (2 hours)

**Goal**: Fix error handling in pipeline and resilience modules

**Approach**: Add troubleshooting guidance to `pipeline.py`, `resilience.py`, `core.py`

**Files to Modify**:
- `tools/ce/pipeline.py` - 1 violation (line 90)
- `tools/ce/resilience.py` - 2 violations (lines 46, 77)
- `tools/ce/core.py` - 2 violations (lines 66, 351)
- `tools/ce/prp.py` - 3 violations (lines 377, 626)
- Total: 8 violations

**Validation Command**: `cd tools && uv run ce validate --level 4`

**Checkpoint**: `git add tools/ce/pipeline.py tools/ce/resilience.py tools/ce/core.py tools/ce/prp.py && git commit -m "fix(drift): add troubleshooting to phase 2 files"`

### Phase 3: Remaining Files (2 hours)

**Goal**: Complete drift remediation for all remaining files

**Approach**: Add troubleshooting guidance to remaining 9 files

**Files to Modify**:
- `tools/ce/pattern_extractor.py` - 1 violation (line 38)
- `tools/ce/drift.py` - 1 violation (line 77)
- `tools/ce/linear_utils.py` - 1 violation (line 52)
- `tools/ce/metrics.py` - 1 violation (line 215)
- `tools/ce/mcp_adapter.py` - 2 violations (lines 164, 299)
- `tools/ce/markdown_lint.py` - 1 violation (line 125)
- `tools/ce/testing/builder.py` - 1 violation (line 100)
- `tools/ce/testing/mocks.py` - 1 violation (line 146)
- `tools/ce/update_context.py` - 1 violation (line 131)
- Total: 9 violations (8 explicit + potential additional violations)

**Validation Command**: `cd tools && uv run ce update-context --dry-run`

**Checkpoint**: `git add tools/ce/*.py tools/ce/testing/*.py && git commit -m "fix(drift): complete troubleshooting guidance for all files"`

### Phase 4: Validation & Verification (1 hour)

**Goal**: Verify drift score < 5% and all validation gates pass

**Approach**: Run comprehensive validation suite

**Validation Steps**:
1. Run L4 validation: `cd tools && uv run ce validate --level 4`
2. Run context sync: `cd tools && uv run ce update-context`
3. Check drift report: `cat .ce/drift-report.md`
4. Verify drift score: Should be < 5%

**Success Criteria**:
- All 30+ violations resolved
- Drift score < 5% (target: 0%)
- L4 validation passes
- No new violations introduced

**Validation Command**: `cd tools && uv run ce update-context && cd tools && uv run ce validate --level 4`

**Checkpoint**: `git add .ce/drift-report.md && git commit -m "chore(drift): verify 0% drift after remediation"`

## Validation Gates

### Gate 1: File-Level Validation
```bash
# After each phase, verify no syntax errors
cd tools && uv run pytest tests/ -k "test_" -v
```
**Expected**: All tests pass

### Gate 2: Pattern Conformance (L4)
```bash
# Verify pattern compliance
cd tools && uv run ce validate --level 4
```
**Expected**: No error handling violations

### Gate 3: Drift Score Check
```bash
# Run drift analysis
cd tools && uv run ce update-context
cat .ce/drift-report.md
```
**Expected**: Drift score < 5%

### Gate 4: Integration Test
```bash
# Verify error messages in real execution
cd tools && uv run ce execute invalid-prp.md 2>&1 | grep "🔧"
```
**Expected**: Error messages contain troubleshooting guidance

## Examples

### Example 1: FileNotFoundError Pattern

**Before** (blueprint_parser.py:38):
```python
raise FileNotFoundError(f"PRP file not found: {prp_path}")
```

**After**:
```python
raise FileNotFoundError(
    f"PRP file not found: {prp_path}\n"
    f"🔧 Troubleshooting:\n"
    f"   - Verify file path is correct\n"
    f"   - Check if file exists: ls {Path(prp_path).parent}\n"
    f"   - Use absolute path or run from project root"
)
```

### Example 2: RuntimeError Pattern

**Before** (context.py:26):
```python
raise RuntimeError(
    f"Failed to get changed files: {str(e)}\n"
)
```

**After**:
```python
raise RuntimeError(
    f"Failed to get changed files: {str(e)}\n"
    f"🔧 Troubleshooting:\n"
    f"   - Verify git repository is initialized\n"
    f"   - Check git status: git status\n"
    f"   - Ensure working directory is inside git repo"
)
```

### Example 3: ValueError Pattern

**Before** (core.py:351):
```python
raise ValueError(
    f"Ad-hoc code exceeds 3 LOC limit (found {len(lines)} lines)\n"
)
```

**After**:
```python
raise ValueError(
    f"Ad-hoc code exceeds 3 LOC limit (found {len(lines)} lines)\n"
    f"🔧 Troubleshooting:\n"
    f"   - Move code to tmp/ file: tmp/script.py\n"
    f"   - Run with: uv run ce run_py tmp/script.py\n"
    f"   - Policy: Ad-hoc max 3 LOC, use files for longer code"
)
```

## Success Criteria

- [ ] **All HIGH priority violations resolved** (Phase 1: 14 violations)
- [ ] **All MEDIUM priority violations resolved** (Phase 2: 8 violations)
- [ ] **All LOW priority violations resolved** (Phase 3: 8+ violations)
- [ ] **L4 validation passes** (`ce validate --level 4`)
- [ ] **Drift score < 5%** (target: 0%)
- [ ] **Pattern documentation updated** (if pattern evolved)
- [ ] **All tests pass** (`uv run pytest tests/ -v`)
- [ ] **No regressions** (existing functionality unchanged)

## Testing Strategy

### Test 1: Unit Tests
```bash
# Verify no syntax errors or broken imports
cd tools && uv run pytest tests/ -v
```
**Expected**: All tests pass

### Test 2: Error Message Validation
```bash
# Trigger known errors and verify guidance present
cd tools && uv run ce execute nonexistent.md 2>&1 | grep -c "🔧"
```
**Expected**: Count > 0 (errors have troubleshooting)

### Test 3: Drift Scan
```bash
# Run full drift analysis
cd tools && uv run ce update-context
```
**Expected**: Drift score 0% (all violations fixed)

### Test 4: L4 Validation
```bash
# Pattern conformance check
cd tools && uv run ce validate --level 4
```
**Expected**: No error handling violations

## Technical Notes

**Files Affected**: 16
**Estimated Effort**: 8 hours (3 + 2 + 2 + 1)
**Complexity**: MEDIUM (repetitive but straightforward)
**Total Violations**: 30+

**Pattern Reference**: `examples/patterns/error-recovery.py` (lines 104-126)

**Priority Focus**:
1. Core execution files (blueprint_parser, context, execute)
2. Pipeline and resilience (pipeline, resilience, core)
3. Remaining utilities and tests
4. Comprehensive validation

**Risk**: Low - additive changes only, no behavior modification

## Rationale

### Why This Matters

1. **User Experience**: Clear recovery steps reduce frustration
2. **Support Reduction**: Self-service troubleshooting cuts support tickets
3. **Pattern Enforcement**: Models correct pattern for new code
4. **Drift Prevention**: Establishes <5% drift as baseline

### Why Now

- **Critical Drift**: 16.7% exceeds 5% policy threshold
- **Pattern Documented**: `error-recovery.py` provides clear reference
- **High Impact**: Affects all error scenarios across codebase
- **Quick Wins**: Repetitive pattern application, high ROI

## Deliverables

### Updated Files (16)
1. ✅ `tools/ce/blueprint_parser.py`
2. ✅ `tools/ce/context.py`
3. ✅ `tools/ce/execute.py`
4. ✅ `tools/ce/pipeline.py`
5. ✅ `tools/ce/resilience.py`
6. ✅ `tools/ce/core.py`
7. ✅ `tools/ce/prp.py`
8. ✅ `tools/ce/pattern_extractor.py`
9. ✅ `tools/ce/drift.py`
10. ✅ `tools/ce/linear_utils.py`
11. ✅ `tools/ce/metrics.py`
12. ✅ `tools/ce/mcp_adapter.py`
13. ✅ `tools/ce/markdown_lint.py`
14. ✅ `tools/ce/testing/builder.py`
15. ✅ `tools/ce/testing/mocks.py`
16. ✅ `tools/ce/update_context.py`

### Verification Outputs
```bash
# Drift score after remediation
Drift Score: 0.0% (✅ HEALTHY)

# L4 validation
✅ All patterns conform to documented standards

# Test suite
✅ All tests pass (0 failures)
```

## Non-Goals

- ❌ **Changing error types** (ValueError → RuntimeError, etc.)
- ❌ **Modifying error logic** (when/where errors raised)
- ❌ **Refactoring error handling** (keep existing structure)
- ❌ **Adding new error types** (scope: troubleshooting only)

## Dependencies

- ✅ `examples/patterns/error-recovery.py` (pattern reference)
- ✅ `ce validate --level 4` (validation tool)
- ✅ `ce update-context` (drift detection)
- ✅ Git for checkpointing

## Risks & Mitigation

**Risk**: Verbose error messages increase output size

**Mitigation**: Keep guidance concise (2-3 steps max), use consistent format

**Risk**: Pattern evolution without documentation update

**Mitigation**: Update `error-recovery.py` if pattern changes during implementation

**Risk**: Missing violations in complex files

**Mitigation**: Run drift scan after each phase to catch regressions

## Alternative Approaches Considered

### Option 1: Automated Pattern Application ❌
**Pros**: Fast, consistent
**Cons**: Hard to generate contextual troubleshooting, requires AI/templates
**Decision**: REJECTED - Manual review ensures quality guidance

### Option 2: Gradual Remediation (1-2 files per week) ❌
**Pros**: Low effort per iteration
**Cons**: Drift persists for weeks, pattern erosion continues
**Decision**: REJECTED - Critical drift requires immediate action

### Option 3: Systematic File-by-File (This PRP) ✅ **CHOSEN**
**Pros**: Comprehensive, phased approach, validated at each step
**Cons**: 8-hour time investment
**Decision**: ACCEPTED - Best balance of speed and quality

## References

### Pattern Documentation
- `examples/patterns/error-recovery.py` - Error handling patterns (lines 104-126)
- `.ce/drift-report.md` - Drift scan results (generated 2025-10-17)
- `CLAUDE.md` - No Fishy Fallbacks policy

### Validation Tools
- `ce validate --level 4` - Pattern conformance check
- `ce update-context` - Drift detection and scoring

### Related PRPs
- PRP-14: `/update-context` Implementation (introduced error-recovery pattern)
- PRP-17: Extract Drift Analysis (created drift detection)
- PRP-19: Tool Permission Documentation (similar systematic documentation update)

## Lessons Learned

1. **Drift Detection Works**: L4 validation caught 30+ violations automatically
2. **Pattern Documentation Critical**: `error-recovery.py` provides clear reference
3. **Phased Approach Essential**: 13 files × 30 violations = manageable with phases
4. **Validation Gates Necessary**: Catch regressions early, verify progress
5. **Troubleshooting ROI High**: Small effort (🔧 + 2-3 steps) = big UX improvement

## Future Enhancements

1. **Pre-commit Hook**: Run `ce validate --level 4` to prevent new violations
2. **Error Message Templates**: Standardized guidance for common error types
3. **Automated Troubleshooting**: Link to docs/runbooks automatically
4. **Error Analytics**: Track most common errors, improve guidance over time
5. **Pattern Linter**: Custom AST-based linter for error message patterns

## Metadata

**Effort Estimate**: 8 hours (3 + 2 + 2 + 1 per phase)
**Complexity**: MEDIUM (repetitive, straightforward)
**Impact**: HIGH (affects all error scenarios)
**Confidence Score**: 9/10 (Clear pattern, systematic approach)
**Implementation Date**: TBD
**Implementation Quality**: TBD (validate after execution)