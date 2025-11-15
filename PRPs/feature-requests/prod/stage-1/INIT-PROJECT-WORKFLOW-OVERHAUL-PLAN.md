# Init-Project Workflow: Complete Overhaul Plan

**Date**: 2025-11-13
**Status**: PLANNED
**Priority**: CRITICAL
**Complexity**: HIGH

---

## Executive Summary

**Problem**: Init workflow has dual implementations (TypeScript + Python), no validation gates, silent failures, and package/filesystem source conflicts.

**Solution**: Unified 4-phase pipeline with validation gates, atomic rollback, streaming feedback, single source of truth (repomix package).

**Impact**:
- Reduce code: 1143 lines → ~250 lines (78% reduction)
- Eliminate: Dual implementations, filesystem boilerplate, manual phases
- Add: 4 validation gates, error logging, atomic rollback
- Time: 2-3 minutes automated (vs 10-45 minutes manual)

---

## Root Cause Analysis

### Issue 1: Dual Implementations (Conflict)

**TypeScript** (`syntropy-mcp/src/tools/init.ts` - 733 lines):
- Copies from filesystem boilerplate (`syntropy-mcp/ce/`)
- 7 phases: copyBoilerplate, scaffoldUserStructure, blendRules, upsertCommands, activateSerena, buildIndex, generateSummary
- No validation gates
- No error logging

**Python** (`tools/ce/init_project.py` - 410 lines):
- Extracts from repomix package (`ce-infrastructure.xml`)
- 4 phases: extract, blend, initialize, verify
- Basic validation
- Basic error handling

**Conflict**: Two different sources for same content. Package built but not used by primary path. Filesystem becomes source of truth, package becomes stale.

### Issue 2: No Validation Gates

Current workflow has ZERO validation between phases:
- No check if extraction succeeded
- No check if expected files exist
- No check if blending produced valid output
- Silent failures leave partial state

Example: Phase 3 extraction fails → .venv/ created → source files missing → all commands broken → user confused

### Issue 3: No Error Feedback

- No persistent log file
- No streaming progress
- Errors output to stderr but not captured
- User sees "complete" even when failed

### Issue 4: Package Not Ready for Direct Install

Current `ce-infrastructure.xml` extracts to:
```
tools/              → Must move to .ce/tools/
.serena/memories/   → Must organize to /system/
CLAUDE.md           → Must blend with existing
settings.local.json → Must merge with existing
```

Post-processing required. Files land at wrong locations.

---

## Proposed Architecture

### Principle 1: ONE Source of Truth

**SINGLE SOURCE**: `ce-infrastructure.xml` repomix package
**ELIMINATE**: `syntropy-mcp/ce/` filesystem boilerplate directory

**Benefits**:
- Portable (one file to distribute)
- Versioned (complete framework at specific version)
- Atomic (all-or-nothing extraction)
- No filesystem dependencies
- Easy to validate (checksum)

### Principle 2: ONE Workflow

**4-PHASE PIPELINE** with validation gates:

```
PHASE 1: PREFLIGHT
  ├─ Validate target directory
  ├─ Check ce-infrastructure.xml exists
  ├─ Verify prerequisites (git, uv, disk space)
  ├─ Backup existing .ce/ → .ce.backup-{timestamp}/
  └─ GATE 1: All checks pass OR abort

PHASE 2: EXTRACT
  ├─ Extract package to tmp/ce-staging/
  ├─ Validate staging contains expected files
  └─ GATE 2: File count matches (87 files) OR abort + rollback

PHASE 3: BLEND
  ├─ Merge settings.local.json (framework + target)
  ├─ Append CLAUDE.md sections (framework + target)
  ├─ Copy framework files to final locations
  └─ GATE 3: Blended files valid JSON/Markdown OR abort + rollback

PHASE 4: FINALIZE
  ├─ Run uv sync in .ce/tools/
  ├─ Create .ce/INIT-SUCCESS marker
  ├─ Activate Serena (non-fatal)
  ├─ Build knowledge index (non-fatal)
  ├─ Delete staging + backup
  └─ GATE 4: ce --version works OR warn (non-fatal)
```

**Total time**: 2-3 minutes

### Principle 3: ONE Implementation

**PRIMARY**: Python (`tools/ce/init_project.py`)
- Implements 4-phase pipeline
- Validation gates
- Error logging
- File operations

**WRAPPER**: TypeScript (`syntropy-mcp/src/tools/init.ts`)
- Validates target directory
- Downloads package if needed
- Calls: `uv run ce init-project --target <path>`
- Streams output to user
- Reports final status

**Benefits**:
- Python for heavy lifting (pathlib, shutil)
- TypeScript for MCP coordination
- Single implementation to maintain
- Clear separation of concerns

### Principle 4: Atomic Installation

**STAGING-BASED APPROACH**:
1. Backup existing .ce/ → .ce.backup-{timestamp}/
2. Extract to tmp/ce-staging/ (NOT target root)
3. Validate staging (GATE 2)
4. Blend in staging (NOT target yet)
5. Validate blended content (GATE 3)
6. Copy staging → target atomically
7. Validate installation (GATE 4)
8. On success: Delete staging + backup
9. On failure: Restore from backup, delete staging

**Result**: Either complete success OR clean rollback. No partial state.

### Principle 5: Streaming Feedback

**CONSOLE OUTPUT** during init:
```
[14:30:00] 🚀 Starting CE framework initialization...
[14:30:01] ✓ GATE 1: Pre-flight checks passed
[14:30:02] → Extracting ce-infrastructure.xml (206KB)...
[14:30:05] ✓ Extracted 87 files to staging
[14:30:05] ✓ GATE 2: Extraction validated
[14:30:06] → Blending settings.local.json...
[14:30:07] → Blending CLAUDE.md...
[14:30:08] ✓ GATE 3: Blending completed
[14:30:09] → Installing Python dependencies...
[14:30:45] ✓ GATE 4: Installation verified
[14:30:45] ✅ CE framework initialized successfully
```

**ERROR EXAMPLE**:
```
[14:30:05] ❌ GATE 2 FAILED: tools/ce/core.py not found
[14:30:05] 🔧 Troubleshooting: Extraction incomplete (expected 87 files, got 45)
[14:30:05] 📄 Full log: .ce/init-20251113-143000.log
[14:30:05] ♻️  Rolling back to pre-init state...
[14:30:06] ✓ Rollback complete
[14:30:06] ❌ Initialization aborted
```

**PERSISTENT LOG**: `.ce/init-{timestamp}.log`
- Phase start/end timestamps
- Each file operation
- Validation gate results
- Error messages with troubleshooting
- Final summary

---

## Package Reorganization

### Current Structure (PROBLEM)
```
ce-infrastructure.xml:
  tools/              → Extracts to target/tools/ (wrong location)
  .serena/memories/   → Extracts to target/.serena/memories/ (needs /system/)
  CLAUDE.md           → Extracts to target/CLAUDE.md (needs blending)
  settings.local.json → Extracts to target/.claude/settings.local.json (needs merging)
```

### Improved Structure (SOLUTION)
```
ce-infrastructure.xml:
  framework/
    .ce/
      tools/              → Ready for direct copy
      PRPs/system/        → Ready for direct copy
    .serena/
      memories/           → Ready for direct copy to /system/ subdir
    .claude/
      commands/           → Ready for direct copy

  blendable/
    CLAUDE.md            → Framework sections to append
    settings.json        → Framework permissions to merge
    .gitignore           → Patterns to append
```

### Extraction Logic
1. Extract `framework/` → Copy directly to target (no post-processing)
2. Extract `blendable/` → Blend with target files, then write

**Benefit**: Only 3 files need blending logic. Everything else is direct copy.

---

## Implementation Plan

### Phase 1: Package Reorganization (2 hours)

**Update**: `.ce/repomix-profile-infrastructure.yml` or build script

**Changes**:
1. Create `framework/` directory structure
2. Move tools/ → framework/.ce/tools/
3. Move .serena/memories/ → framework/.serena/memories/ (will copy to /system/)
4. Move .claude/commands/ → framework/.claude/commands/
5. Move PRPs/system/ → framework/.ce/PRPs/system/
6. Create `blendable/` directory
7. Extract CLAUDE.md sections → blendable/CLAUDE.md
8. Extract settings permissions → blendable/settings.json
9. Rebuild package: `.ce/build-and-distribute.sh`

**Validation**:
```bash
# Verify new package structure
npx repomix --unpack ce-infrastructure.xml --target tmp/test-extract/
ls tmp/test-extract/framework/.ce/tools/
ls tmp/test-extract/blendable/CLAUDE.md
```

### Phase 2: Python Implementation (4 hours)

**Update**: `tools/ce/init_project.py`

**Changes**:
1. Add `PhaseValidator` class with 4 gate methods
2. Add `ErrorLogger` class for persistent logging
3. Update `extract()` method:
   - Extract to staging (not target root)
   - Validate file count (GATE 2)
   - Return structured status
4. Update `blend()` method:
   - Blend in staging first
   - Validate JSON/Markdown (GATE 3)
   - Copy to target only after validation
5. Add `preflight()` method (GATE 1)
6. Update `verify()` method (GATE 4)
7. Add `rollback()` method
8. Add streaming console output
9. Add progress indicators

**New Classes**:
```python
class PhaseValidator:
    def gate1_preflight(target: Path) -> ValidationResult
    def gate2_extraction(staging: Path) -> ValidationResult
    def gate3_blending(staging: Path) -> ValidationResult
    def gate4_finalization(target: Path) -> ValidationResult

class ErrorLogger:
    def __init__(log_file: Path)
    def log_phase_start(phase: str)
    def log_phase_end(phase: str, success: bool)
    def log_operation(operation: str, status: str)
    def log_error(error: str, troubleshooting: str)
```

**Expected file count validation**:
```python
EXPECTED_FILES = {
    "tools": 33,  # .py files in tools/ce/
    "memories": 23,  # framework memories
    "commands": 11,  # framework commands
    "prps": 1,  # PRP-0
    "total": 87  # Total expected files
}
```

### Phase 3: TypeScript Simplification (1 hour)

**Update**: `syntropy-mcp/src/tools/init.ts`

**Changes**:
1. Remove `copyBoilerplate()` function (733 lines → ~50 lines)
2. Remove `scaffoldUserStructure()` (handled by Python)
3. Remove `blendRulesIntoCLAUDEmd()` (handled by Python)
4. Remove `upsertSlashCommands()` (handled by Python)
5. Keep `activateSerenaProject()` (call after Python succeeds)
6. Keep `buildKnowledgeIndex()` (call after Python succeeds)
7. Keep `generateSummary()` (call after Python succeeds)
8. Add subprocess call to Python:
   ```typescript
   const result = await execSync(
     `uv run ce init-project --target ${projectRoot}`,
     { encoding: 'utf-8', stdio: 'inherit' }
   );
   ```

**New workflow**:
```typescript
export async function initProject(args: InitProjectArgs): Promise<InitProjectResult> {
  // 1. Validate target
  await validateProjectRoot(projectRoot);

  // 2. Check if already initialized
  if (await isAlreadyInitialized(projectRoot)) {
    return { success: true, message: "Already initialized" };
  }

  // 3. Call Python for heavy lifting
  const result = await callPythonInit(projectRoot);
  if (!result.success) {
    return result;
  }

  // 4. Post-processing (non-fatal)
  await activateSerenaProject(projectRoot);
  await buildKnowledgeIndex(projectRoot);
  await generateSummary(projectRoot);

  return { success: true, message: "Initialized successfully" };
}
```

### Phase 4: Documentation Update (1 hour)

**Update**: `examples/INITIALIZATION.md`

**Changes**:
1. Simplify from 5-phase manual workflow → 4-phase automated workflow
2. Remove bucket collection phase (obsolete)
3. Remove user files migration phase (automated)
4. Remove legacy cleanup phase (not needed for clean installs)
5. Update automated installation section
6. Add validation gate descriptions
7. Add error troubleshooting examples
8. Update expected file counts

**New structure**:
```markdown
## Quick Start: Automated Installation (RECOMMENDED)

npx syntropy-mcp init ce-framework

This command automatically:
1. PREFLIGHT: Validates prerequisites
2. EXTRACT: Unpacks ce-infrastructure.xml to staging
3. BLEND: Merges framework + target files
4. FINALIZE: Installs dependencies and verifies

Time: 2-3 minutes
```

### Phase 5: Testing (2 hours)

**Test Cases**:
1. Greenfield project (empty directory)
2. Existing project with .claude/ settings
3. Existing project with CLAUDE.md
4. Failed extraction (corrupted package)
5. Failed blend (invalid JSON)
6. Failed finalization (uv not installed)
7. Rollback on failure

**Test Script**:
```bash
# Test 1: Greenfield
rm -rf test-project
mkdir test-project
cd test-project
git init
npx syntropy-mcp init ce-framework
# Verify: .ce/INIT-SUCCESS exists

# Test 2: With existing settings
echo '{"permissions": {"allow": ["custom"]}}' > .claude/settings.local.json
npx syntropy-mcp init ce-framework
# Verify: settings.local.json contains both "custom" and CE permissions

# Test 3: Rollback on failure
# Corrupt package, run init, verify rollback
```

---

## Success Criteria

- ✅ Single implementation (Python primary, TypeScript wrapper)
- ✅ Single source (ce-infrastructure.xml package)
- ✅ 4 validation gates implemented
- ✅ Persistent error logging (`.ce/init-{timestamp}.log`)
- ✅ Streaming progress output
- ✅ Atomic rollback on failure
- ✅ Expected file counts validated
- ✅ Init completes in 2-3 minutes
- ✅ All test cases pass
- ✅ Code reduced by 78% (1143 → ~250 lines)
- ✅ Zero silent failures
- ✅ Documentation updated

---

## Migration Impact

### Breaking Changes
- None (API stays same: `npx syntropy-mcp init ce-framework`)

### Files Modified
1. `.ce/repomix-profile-infrastructure.yml` (package structure)
2. `tools/ce/init_project.py` (add gates + logging)
3. `syntropy-mcp/src/tools/init.ts` (simplify to wrapper)
4. `examples/INITIALIZATION.md` (update guide)

### Files Deleted
- `syntropy-mcp/ce/` boilerplate directory (after package verified)

### Backward Compatibility
- Existing installations unaffected
- New installations use improved workflow
- Old manual workflow still documented (for reference)

---

## Risks and Mitigations

### Risk 1: Package Reorganization Breaks Existing Builds
**Mitigation**: Test new package structure before deleting old boilerplate directory. Run init on test project first.

### Risk 2: Python subprocess fails on some systems
**Mitigation**: Add fallback to direct Python import if subprocess fails. Check uv installed before calling.

### Risk 3: Validation gates too strict (false failures)
**Mitigation**: Make file count validation flexible (±5 files). Log warnings for non-critical missing files.

### Risk 4: Rollback fails, leaves corrupt state
**Mitigation**: Create backup BEFORE any modifications. Test rollback logic independently.

---

## Estimated Effort

- Phase 1 (Package reorganization): 2 hours
- Phase 2 (Python implementation): 4 hours
- Phase 3 (TypeScript simplification): 1 hour
- Phase 4 (Documentation): 1 hour
- Phase 5 (Testing): 2 hours

**Total**: 10 hours (1.5 days)

**Complexity**: HIGH (multi-language, packaging, error handling)
**Risk**: MEDIUM (well-scoped, reversible changes)

---

## Next Steps

1. Review this plan with sequential thinking output
2. Generate PRP from this plan
3. Create feature branch: `init-workflow-overhaul`
4. Implement Phase 1 (package reorganization)
5. Test Phase 1 extraction
6. Implement Phase 2 (Python gates + logging)
7. Test Phase 2 validation
8. Implement Phase 3 (TypeScript wrapper)
9. Test end-to-end workflow
10. Update documentation
11. Create PR with full test results

---

**Plan Version**: 1.0
**Last Updated**: 2025-11-13
