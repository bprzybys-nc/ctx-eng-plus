---
prp_id: PRP-38-INITIAL
title: Fix Blend Orchestrator Domain Execution (E2E Test Findings)
status: planning
created: 2025-11-07
complexity: high
estimated_hours: 8.0
batch_context: "Iteration 3 E2E test revealed critical blend execution gaps"
---

# Fix Blend Orchestrator Domain Execution (E2E Test Findings)

## Executive Summary

E2E testing (PRP-36 Iteration 3) revealed that BlendingOrchestrator._run_blending() only processes 2/6 domains successfully. The `blend()` interface strategies (settings, claude_md, memories, examples) have **no implementation** - just debug logging. The `execute()` interface strategies (prps, commands) receive correct parameters (PRP-37.2.1) but fail silently due to missing error propagation.

**Impact**: CRITICAL - Blend phase appears to run but silently fails to migrate 4/6 domains, leaving 133 files unmigrated.

---

## Problem Analysis

### Issue #1: blend() Interface Not Implemented ❌

**File**: `tools/ce/blending/core.py:322-326`

**Current Code**:
```python
if hasattr(strategy, 'blend'):
    # BlendStrategy interface (settings, claude_md, memories, examples)
    # This would need proper implementation with file reading/writing
    logger.debug(f"    Using blend() interface for {domain}")
```

**Problem**:
- Only logs debug message
- **Never calls `strategy.blend(...)`**
- **Never adds to `results` dict**
- Silently skips 4 domains (settings, claude_md, memories, examples)

**Affected Domains**:
- ✅ settings (SettingsBlendStrategy.blend)
- ✅ claude_md (ClaudeMdBlendStrategy.blend)
- ✅ memories (MemoriesBlendStrategy.blend)
- ✅ examples (ExamplesBlendStrategy.blend)

**Evidence from E2E test log (line 316)**:
```
✓ Blending complete (2 domains processed)
```
Only 2/6 domains added to `results`.

---

### Issue #2: execute() Strategies Fail Silently ⚠️

**File**: `tools/ce/blending/core.py:356-357`

**Current Code**:
```python
logger.debug(f"    Executing {domain} with params: {params}")
result = strategy.execute(params)
results[domain] = result
```

**Problem**:
- Parameters correct (PRP-37.2.1/37.3.1 fixes applied)
- `execute()` called but returns failure
- Exception handling (lines 361-363) catches errors but **doesn't propagate them**
- Phase continues even when domains fail

**Affected Domains**:
- ⚠️ prps (PRPMoveStrategy.execute) - 79 files NOT moved
- ⚠️ commands (CommandOverwriteStrategy.execute) - 11 files NOT copied

**Evidence from E2E test**:
```
🔍 Verifying PRPs/ migration...
❌ PRPs/ - Migration incomplete!
   Unmigrated files: 67
```

---

### Issue #3: No Error Propagation to init_project ❌

**File**: `tools/ce/init_project.py:237-240`

**Current Code**:
```python
if not status["success"]:
    status["message"] = (
        f"❌ Blend phase failed (exit code {result.returncode})\n"
        f"🔧 Check blend tool output:\n{result.stderr}"
    )
```

**Problem**:
- Blend command returns exit code 1 (from cleanup failure)
- But blend orchestrator returns exit 0 even when domains fail
- Cleanup failure masks actual blend failures
- User sees "blend failed" but unclear which domains

---

### Issue #4: Cleanup Validation Too Strict ⚠️

**Evidence**:
```
❌ Blending failed: Cannot cleanup PRPs/: 67 unmigrated files detected.
```

**Problem**:
- Cleanup requires 100% migration
- Blocks even when blend phase partially succeeds
- Doesn't distinguish between "not run" vs "failed"
- Should be warning, not error (or fix blend first)

---

## Root Cause Summary

1. **Incomplete Implementation**: `blend()` interface never implemented in orchestrator
2. **Silent Failures**: Exception handling swallows errors without reporting
3. **Poor Error Reporting**: Exit codes don't reflect actual blend failures
4. **Validation Confusion**: Cleanup failures mask blend execution issues

---

## Proposed Solution - Multi-Phase Fix

### Phase 1: Implement blend() Interface (3 hours)

**Goal**: Call actual blend() methods for 4 missing domains

**Changes to `tools/ce/blending/core.py:322-326`**:

```python
if hasattr(strategy, 'blend'):
    # BlendStrategy interface (settings, claude_md, memories, examples)
    logger.debug(f"    Using blend() interface for {domain}")

    # Read framework and target content
    framework_content = self._read_domain_content(domain, "framework")
    target_content = self._read_domain_content(domain, "target")

    # Call blend strategy
    blended_result = strategy.blend(
        framework_content=framework_content,
        target_content=target_content,
        target_dir=target_dir
    )

    # Write blended content
    self._write_domain_content(domain, blended_result, target_dir)

    results[domain] = {
        "success": True,
        "files_processed": 1,  # Or actual count
        "message": f"✓ {domain} blended successfully"
    }
```

**Helper Methods to Add**:
- `_read_domain_content(domain, source)` - Read files for domain
- `_write_domain_content(domain, content, target_dir)` - Write blended output
- Handle domain-specific file locations (settings.json, CLAUDE.md, etc.)

---

### Phase 2: Improve Error Handling (2 hours)

**Goal**: Propagate errors properly, fail fast on critical issues

**Changes to exception handling**:

```python
except Exception as e:
    error_msg = f"❌ {domain} blending failed: {e}"
    logger.error(error_msg)
    results[domain] = {
        "success": False,
        "error": str(e),
        "message": error_msg
    }

    # Fail fast for critical domains
    if domain in ["settings", "claude_md"]:
        raise RuntimeError(
            f"Critical domain '{domain}' failed - cannot continue\n"
            f"Error: {e}\n"
            f"🔧 Fix {domain} blending before proceeding"
        )
```

**Changes to orchestrator return**:

```python
# Check for failures
failed_domains = [d for d, r in results.items() if not r.get("success", False)]

return {
    "phase": "blend",
    "implemented": True,
    "results": results,
    "success": len(failed_domains) == 0,
    "failed_domains": failed_domains,
    "message": self._format_blend_summary(results)
}
```

---

### Phase 3: Fix Blend Command Exit Codes (1 hour)

**Goal**: Return correct exit codes based on actual blend success

**Changes to `tools/ce/blend.py`** (command entrypoint):

```python
# After running orchestrator
if blend_results.get("success", False):
    sys.exit(0)
else:
    failed = blend_results.get("failed_domains", [])
    print(f"❌ Blend failed for domains: {', '.join(failed)}")
    sys.exit(1)
```

---

### Phase 4: Debug execute() Strategies (2 hours)

**Goal**: Fix prps/commands execution or identify root cause

**Investigation Steps**:
1. Add verbose logging to PRPMoveStrategy.execute()
2. Check if source_dir/target_dir paths are correct
3. Verify file permissions
4. Check if files actually exist at source_dir
5. Test execute() in isolation with mock data

**Potential Issues**:
- Source paths incorrect (detection phase output vs actual files)
- Target directories don't exist (need mkdir)
- File move operations failing silently
- Hash deduplication logic broken

---

## Testing Strategy

### Unit Tests

**File**: `tools/tests/test_blend_orchestrator_execution.py` (new)

**Test Cases**:
1. `test_blend_interface_strategies_called()` - Verify blend() called for 4 domains
2. `test_execute_interface_strategies_called()` - Verify execute() called for 2 domains
3. `test_all_domains_add_to_results()` - Check results dict has 6 entries
4. `test_failed_domain_propagates_error()` - Exception handling works
5. `test_critical_domain_failure_stops_blend()` - settings/claude_md failures block
6. `test_blend_exit_code_reflects_failures()` - Exit code 1 when domains fail

### Integration Tests

**File**: `tools/tests/test_e2e_blend_complete.py` (new)

**Test Scenario**: Full blend pipeline with real files
1. Create test target with sample files (settings, CLAUDE.md, PRPs, etc.)
2. Run blend with all 6 domains
3. Verify all files migrated to correct locations
4. Check results dict shows 6 successes
5. Confirm exit code 0

### E2E Validation

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce init-project /Users/bprzybyszi/nc-src/ctx-eng-plus-test-target

# Expected output:
# Phase: blend
# ✅ Blend phase completed
#   ✓ settings (1 file)
#   ✓ claude_md (1 file)
#   ✓ memories (24 files)
#   ✓ examples (17 files)
#   ✓ prps (79 files)
#   ✓ commands (11 files)
```

---

## Validation Gates

### Gate 1: blend() Interface Implementation
**Command**: Read core.py lines 322-340
**Criteria**:
- ✓ `strategy.blend()` called
- ✓ Content read from framework/target
- ✓ Result written to target
- ✓ Results dict updated

### Gate 2: All 6 Domains Process
**Command**: Run E2E test, check log
**Criteria**:
- ✓ Output shows "6 domains processed" (not 2)
- ✓ No "unmigrated files" errors
- ✓ All domain directories exist in target

### Gate 3: Error Propagation Works
**Test**: Inject failure in settings strategy
**Criteria**:
- ✓ Error logged
- ✓ Blend phase returns exit code 1
- ✓ init_project shows clear error message

### Gate 4: PRPs/Commands Execute
**Command**: Check `.ce/PRPs/` directory after blend
**Criteria**:
- ✓ 79 PRP files moved to `.ce/PRPs/`
- ✓ 11 command files in `.claude/commands/`
- ✓ No "unmigrated" warnings

---

## Rollout Plan

### Step 1: Implement blend() Interface (Phase 1)
- Add helper methods
- Call strategy.blend() for 4 domains
- Update results dict
- Test with unit tests

### Step 2: Fix Error Handling (Phase 2)
- Improve exception handling
- Add fail-fast for critical domains
- Return proper status from orchestrator
- Test error propagation

### Step 3: Fix Exit Codes (Phase 3)
- Update blend.py command
- Return exit code based on results
- Test with init_project

### Step 4: Debug execute() Strategies (Phase 4)
- Add verbose logging
- Test PRPMoveStrategy in isolation
- Fix any path/permission issues
- Validate with E2E test

### Step 5: E2E Validation
- Run full init-project on clean target
- Verify all 6 domains process
- Check all files migrated
- Validate exit codes

---

## Success Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Domains Processed | 2/6 (33%) | 6/6 (100%) |
| Files Migrated | ~20/133 (15%) | 133/133 (100%) |
| Error Reporting | Silent failures | Clear error messages |
| Exit Code Accuracy | Incorrect (0 when failed) | Correct (1 on failure) |

---

## Risk Analysis

### Risk 1: blend() Interface Complexity
**Description**: Each domain needs custom content reading/writing logic
**Mitigation**:
- Start with simple domains (settings, claude_md - single files)
- Abstract common patterns into helpers
- Test incrementally

### Risk 2: Breaking Existing Blend Behavior
**Description**: Changes might break currently working domains
**Mitigation**:
- Comprehensive unit tests before changes
- Keep execute() path unchanged initially
- Test both interfaces separately

### Risk 3: execute() Strategy Root Cause Unknown
**Description**: May spend time on orchestrator when issue is in strategies
**Mitigation**:
- Add verbose logging first
- Test strategies in isolation
- If strategies broken, file separate PRP for fixes

---

## Dependencies

**Blocks**:
- Init-project E2E validation
- Batch 37 validation (PRP-37.2.1, 37.3.1 not fully tested)
- Production deployment of init-project

**Depends On**:
- PRP-37.5 (extraction logic fixed) ✅
- blend-config.yml in package ✅
- All strategies implemented ✅

---

## Estimated Timeline

- **Phase 1**: 3 hours (blend() implementation)
- **Phase 2**: 2 hours (error handling)
- **Phase 3**: 1 hour (exit codes)
- **Phase 4**: 2 hours (execute() debug)
- **Total**: 8 hours

**Complexity**: HIGH (touches core orchestration logic, affects all domains)

---

## Related PRPs

- **PRP-36.3**: Init-project E2E testing (discovered issues)
- **PRP-37.2.1**: Fix PRPs domain blending (parameters correct, execution broken)
- **PRP-37.3.1**: Fix Commands domain blending (parameters correct, execution broken)
- **PRP-37.5**: Fix extraction logic (blend-config.yml now extracted)
- **PRP-34**: Original blend tool implementation (orchestrator foundation)

---

## Appendix: E2E Test Evidence

**Test Run**: 2025-11-07 Iteration 3
**Log**: `tools/.tmp/prp36test-iteration3.log`

**Key Findings** (lines 300-435):
```
Phase C: BLENDING - Merging framework + target...
  Blending prps (79 files)...          # Detected but NOT processed
  Blending examples (17 files)...      # Detected but NOT processed
  Blending claude_md (1 files)...      # Detected but NOT processed
  Blending settings (1 files)...       # Detected but NOT processed
  Blending commands (11 files)...      # Detected but NOT processed
  Blending memories (24 files)...      # Detected but NOT processed
✓ Blending complete (2 domains processed)  # ❌ ONLY 2/6!
```

**Cleanup Validation**:
```
❌ PRPs/ - Migration incomplete!
   Unmigrated files: 67
```

**Extraction Phase**: ✅ SUCCESS (55 files)
**Initialize Phase**: ✅ SUCCESS (UV sync worked)
**Overall Status**: ⚠️ PARTIAL SUCCESS (blend broken)

---

## Next Actions

1. Create this PRP in PRPs/feature-requests/
2. Break into sub-PRPs if needed:
   - PRP-38.1: Implement blend() interface
   - PRP-38.2: Fix error propagation
   - PRP-38.3: Debug execute() strategies
3. Prioritize Phase 1 (biggest impact - 4 domains)
4. Run E2E test after each phase
5. Update batch 37 review once validated
