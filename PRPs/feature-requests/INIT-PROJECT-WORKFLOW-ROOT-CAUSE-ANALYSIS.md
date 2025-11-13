# Init-Project Workflow: Root Cause Analysis

**Date**: 2025-11-13
**Status**: DOCUMENTED
**Severity**: CRITICAL (blocks framework setup)
**Commits**: c8f44d5, dc9c158 (recovery iterations)

---

## Problem

`npx syntropy-mcp init ce-framework` (Nov 12, 14:32) **silently failed at Phase 3** leaving broken state:

```text
.ce/tools/
├── .venv/           ✅ Present
├── ce/              ❌ MISSING
├── tests/           ❌ MISSING
├── pyproject.toml   ❌ MISSING
```

Result: All CE commands unusable

```bash
$ uv run ce validate --level all
Error: Could not find 'ce' in pyproject.toml
```

---

## Root Cause Chain

### Primary: Repomix Extraction Incomplete

- `ce-infrastructure.xml` (206KB) extraction failed/skipped
- Only virtualenv created (by `uv sync`)
- Source code files never reached filesystem

### Secondary: No Phase Validation

- Init had no error handling between phases
- Partial state left in `.ce/` without warning
- Process marked as "complete" despite missing files

### Tertiary: No Error Streaming

- Error messages output during init but no intermediate status
- User sees no indication of failure
- Subsequent operations fail mysteriously

---

## Changes Needed to Fix Init Workflow

### 1. Phase-Level Validation

After each phase, validate expected files exist:

```python
# Phase 3 (Tools Extraction)
expected_files = [
    ".ce/tools/ce/core.py",
    ".ce/tools/ce/validate.py",
    ".ce/tools/pyproject.toml",
    ".ce/tools/bootstrap.sh"
]

for file in expected_files:
    if not path.exists(file):
        fail(f"Phase 3 failed: {file} not extracted")
```

### 2. Persistent Error Logging

Create `.ce/init-[timestamp].log` during init:

```text
[14:31:00] Phase 1: Bucket collection - OK
[14:31:15] Phase 2: User files - OK
[14:31:45] Phase 3: Tools extraction - FAILED
  Error: Repomix unpacking incomplete
  Missing: .ce/tools/ce/ directory
  See: .ce/init-20251112-143100.log
```

### 3. Pre-Flight Checks

Before Phase 3:

- Verify `ce-infrastructure.xml` exists and readable
- Check disk space available (206KB + buffer)
- Verify git status clean

### 4. Post-Init Validation

After all phases complete:

- Test file structure (gates 1-5 in INIT-RECOVERY-1)
- Run `uv run ce --help` (command smoke test)
- Create `.ce/INIT-SUCCESS.marker` on completion

### 5. Smart Rollback

On phase failure:

- Create backup: `.ce.failed-phase-3/`
- Offer restore option before cleanup
- Never silently continue

---

## Implementation Details

| Item | File | Changes |
|------|------|---------|
| **Phase validation** | `init_project.py` | Add `validate_phase()` calls |
| **Error logging** | `init_project.py` | Log to `.ce/init-[timestamp].log` |
| **Pre-flight checks** | `init_project.py` | Add `preflight_checks()` |
| **Smoke tests** | `init_project.py` | Add `validate_installation()` |
| **Repomix handling** | `init_project.py` or wrapper | Add retry + timeout handling |

---

## Validation Gates (from INIT-RECOVERY-1)

### Gate 2: Extraction Success (POST-EXTRACTION)

- `✓` `.ce/tools/ce/core.py` exists
- `✓` `.ce/tools/pyproject.toml` valid TOML
- `✓` `.ce/tools/tests/` is directory

### Gate 3: Environment (POST-UVSYNC)

- `✓` `uv sync` succeeds in `.ce/tools/`
- `✓` `.ce/tools/uv.lock` created/updated

### Gate 4: Commands (POST-VALIDATION)

- `✓` `uv run ce --help` shows commands
- `✓` `uv run ce validate --level 1` succeeds
- `✓` `uv run ce context health` works

---

## Dynamics Specific to This Init

| Factor | Why It Matters | Fix |
|--------|---|---|
| **206KB monolithic package** | Extraction prone to timeout/network issues | Add streaming status + retry |
| **Virtualenv created first** | `.venv/` succeeds even if source fails | Validate source exists BEFORE .venv |
| **No intermediate checkpoints** | Can't identify which phase broke | Add phase IDs to all log messages |
| **Silent failure on missing files** | User assumes init succeeded | Require explicit validation confirmation |

---

## Recovery Evidence

**Commit c8f44d5** (`PRE INIT-RECOVERY`) created:

- `ITERATION-EXECUTION-SUMMARY.md` - Full analysis + 3 recovery PRPs
- `context-engineering/PRPs/INIT-RECOVERY-1-restore-ce-tools.md` - Recovery playbook with 6 validation gates

Manual recovery required:

1. Re-extract from `ce-infrastructure.xml`
2. Restore missing source files to `.ce/tools/`
3. Re-sync UV environment
4. Validate all commands work

---

## PRP Template for Prevention

**Goal**: Add phase-level validation + error logging to init procedure

**Scope**:

- Add validation gates after phases 1-4
- Create persistent log file
- Add pre-flight checks
- Add smoke tests

**Effort**: 2-3 hours
**Complexity**: MEDIUM (logging + error handling)
**Files**: `init_project.py`, new module `init_validation.py`

---

## Success Criteria

- `✓` Init command shows phase progress
- `✓` Error logged to `.ce/init-[timestamp].log` if phase fails
- `✓` Post-init validation runs before marking complete
- `✓` Smoke tests pass (CE commands work)
- `✓` No silent partial states
