---
prp_id: PRP-42
feature_name: Init Project Workflow Overhaul
status: pending
created: 2025-11-13T16:11:53.996835
updated: 2025-11-13T16:11:53.996835
complexity: high
estimated_hours: 10
dependencies: UV, Repomix CLI, Python 3.11+, TypeScript, ce-infrastructure.xml
issue: TBD
---

# Init Project Workflow Overhaul

## 1. TL;DR

**Objective**: Init Project Workflow Overhaul

**What**: Redesign init-project workflow to eliminate dual implementations, add validation gates, and provide atomic installation with rollback.

**Current Problems:**
1. Dual implementations (TypeScript 733 lines + Python 410 lines) doing same work
2. Two sources of truth (filesystem boilerplate vs repomix package)
3. Zero validation gates - silent failures leave broken state
4. Certinia project failure: Phase 3 extraction failed silently, left .venv/ but no source files

**Why**: Eliminate silent failures causing broken installs in production (Certinia project), reduce dual-implementation maintenance burden (1143 → 250 lines, 78% reduction), ensure reliable 2-3 minute init vs 10-45 minute manual workflow

**Effort**: High (10 hours / 1.5 days - package reorg, dual codebase changes, validation gates)

**Dependencies**: UV, Repomix CLI, Python 3.11+, TypeScript, ce-infrastructure.xml


## 2. Context

### Background

Redesign init-project workflow to eliminate dual implementations, add validation gates, and provide atomic installation with rollback.

**Current Problems:**
1. Dual implementations (TypeScript 733 lines + Python 410 lines) doing same work
2. Two sources of truth (filesystem boilerplate vs repomix package)
3. Zero validation gates - silent failures leave broken state
4. Phase 3 extraction failure leaves .venv/ but missing source files

**Solution:**
Unified 4-phase pipeline with validation gates, single source (repomix package), atomic rollback.

**Acceptance Criteria:**
1. Single implementation (Python ~200 lines, TypeScript wrapper ~50 lines)
2. Single source of truth (ce-infrastructure.xml package only)
3. 4 validation gates (PREFLIGHT, EXTRACT, BLEND, FINALIZE)
4. Streaming progress output with persistent log
5. Atomic rollback on any gate failure
6. Expected file count validation (87 files ±5 tolerance, fail if >10 difference)
7. Init completes in 2-3 minutes (vs 10-45 minutes manual)
8. Zero silent failures

**4-Phase Pipeline:**
- **PHASE 1: PREFLIGHT** - Validate prerequisites, backup existing .ce/
- **PHASE 2: EXTRACT** - Unpack package to staging, validate 87 files extracted
- **PHASE 3: BLEND** - Merge settings/CLAUDE.md, validate JSON/Markdown
- **PHASE 4: FINALIZE** - Install deps, verify commands work, cleanup staging

### Constraints and Considerations

**Security:**
- Validate package integrity before extraction
- Check disk space before extraction (300MB minimum)
- Never overwrite user files (framework files go to /system/ subdirs)

**Breaking Changes:**
- None - API stays same: `npx syntropy-mcp init ce-framework`
- Backward compatible

**Files Modified:**
1. `.ce/repomix-profile-infrastructure.yml` (package structure)
2. `tools/ce/init_project.py` (add gates + logging)
3. `syntropy-mcp/src/tools/init.ts` (simplify to wrapper)
4. `examples/INITIALIZATION.md` (update guide)

**Files Deleted (After Migration Verified):**
- `syntropy-mcp/ce/` boilerplate directory
- Legacy TypeScript functions: `copyBoilerplate()`, `scaffoldUserStructure()`, `blendRulesIntoCLAUDEmd()`, `findBoilerplatePath()`
- Legacy boilerplate search logic in init.ts (lines ~160-280)

**Risks:**
1. Package reorganization breaks builds → Test new structure first
2. Python subprocess fails on some systems → Add fallback to direct import
3. Validation gates too strict → Make file count flexible (±5 files)
4. Rollback fails → Create backup BEFORE modifications

**Estimated Effort:**
- Phase 1 (Package reorganization): 2 hours
- Phase 2 (Python implementation): 4 hours
- Phase 3 (TypeScript simplification): 1 hour
- Phase 4 (Documentation): 1 hour
- Phase 5 (Testing): 2 hours
- **Total**: 10 hours (1.5 days)

**Testing Strategy:**
1. Greenfield project (empty directory)
2. Existing project with .claude/ settings
3. Existing project with CLAUDE.md
4. Failed extraction (corrupted package)
5. Failed blend (invalid JSON)
6. Failed finalization (uv not installed)
7. Rollback on failure

**Success Criteria:**
- ✅ Code reduced by 78% (1143 → ~250 lines)
- ✅ 4 validation gates implemented
- ✅ Persistent error logging
- ✅ Atomic rollback
- ✅ Init completes in 2-3 minutes
- ✅ All test cases pass
- ✅ Zero silent failures
- ✅ Legacy cleanup complete:
  - syntropy-mcp/ce/ directory removed
  - Old TypeScript functions deleted
  - No dead code references remaining

### Documentation References

- UV Package Manager: https://docs.astral.sh/uv/
- Repomix CLI: https://github.com/yamadashy/repomix
- Python pathlib: https://docs.python.org/3/library/pathlib.html
- Python shutil: https://docs.python.org/3/library/shutil.html
- Serena MCP documentation
- TypeScript subprocess execution
- pytest testing framework


## 3. Implementation Steps

### Phase 1: Package Reorganization (2 hours)

1. Update `.ce/repomix-profile-infrastructure.yml` to new structure

**Current ce-infrastructure.xml (flat structure)**:
```
tools/ce/*.py              # 33 files - must move to .ce/tools/
.serena/memories/*.md      # 23 files - must organize to /system/
.claude/commands/*.md      # 11 files - ready to copy
.ce/PRPs/system/PRP-0*.md  # 1 file - ready to copy
CLAUDE.md                  # Must blend with target
settings.local.json        # Must merge with target
```

**Proposed ce-infrastructure.xml (organized structure)**:
```
framework/                 # Ready for direct copy (no blending)
  .ce/
    tools/ce/*.py          # 33 files
    PRPs/system/PRP-0*.md  # 1 file
  .serena/
    memories/*.md          # 23 files (copy to /system/ subdir)
  .claude/
    commands/*.md          # 11 files

blendable/                 # Needs merging with target files
  CLAUDE.md                # Framework sections to append
  settings.json            # Framework permissions to merge
```

2. Create `framework/` directory with ready-to-copy files:
   - framework/.ce/tools/
   - framework/.ce/PRPs/system/
   - framework/.serena/memories/
   - framework/.claude/commands/
3. Create `blendable/` directory with files needing merge:
   - blendable/CLAUDE.md (framework sections)
   - blendable/settings.json (framework permissions)
4. Rebuild package: `.ce/build-and-distribute.sh`
5. Test extraction to staging area
6. Verify 87 files extracted correctly (33 tools + 23 memories + 11 commands + 1 PRP-0 + config files)

### Phase 2: Python Implementation (4 hours)

**Pre-implementation: Serena Code Analysis**

Use Serena MCP to understand existing implementation:

```python
# 1. Get overview of init_project.py structure
mcp__syntropy__serena_get_symbols_overview(
    relative_path="tools/ce/init_project.py"
)

# 2. Find ProjectInitializer class definition
mcp__syntropy__serena_find_symbol(
    name_path="ProjectInitializer",
    include_body=True
)

# 3. Find all references to extract/blend/initialize methods
mcp__syntropy__serena_find_referencing_symbols(
    name_path="ProjectInitializer.extract"
)

# 4. Search for existing validation patterns
mcp__syntropy__serena_search_for_pattern(
    pattern="ValidationResult|validate_.*|gate_",
    file_glob="tools/ce/*.py"
)
```

**Analysis Goals**:
- Understand current method signatures (extract, blend, initialize, verify)
- Identify validation patterns already in codebase
- Find similar gate/validation logic to reuse
- Map dependencies between methods

1. Add `PhaseValidator` class with 4 gate methods

**Example gate implementation pattern**:
```python
class ValidationResult:
    def __init__(self, success: bool, message: str = "", troubleshooting: str = ""):
        self.success = success
        self.message = message
        self.troubleshooting = troubleshooting

class PhaseValidator:
    def gate2_extraction(self, staging: Path) -> ValidationResult:
        """Validate extraction file count with tolerance"""
        expected = {"tools": 33, "memories": 23, "commands": 11, "total": 87}
        actual = self._count_files(staging)

        # Fail if >10 difference
        if abs(actual["total"] - expected["total"]) > 10:
            return ValidationResult(
                success=False,
                message=f"❌ GATE 2 FAILED: Expected {expected['total']} files, got {actual['total']}",
                troubleshooting="🔧 Extraction incomplete - check package integrity"
            )

        # Warn if within tolerance (5-10 difference)
        if actual["total"] != expected["total"]:
            print(f"⚠️  File count {actual['total']} differs from expected {expected['total']} (within tolerance)")

        return ValidationResult(success=True)

    def _count_files(self, staging: Path) -> Dict[str, int]:
        """Count files by category"""
        tools = len(list(staging.glob("tools/ce/*.py")))
        memories = len(list(staging.glob(".serena/memories/*.md")))
        commands = len(list(staging.glob(".claude/commands/*.md")))
        return {"tools": tools, "memories": memories, "commands": commands, "total": tools + memories + commands}
```

2. Add `ErrorLogger` class for persistent logging (`.ce/init-{timestamp}.log`)
3. Update `preflight()` method - GATE 1:
   - Validate target directory writable
   - Check ce-infrastructure.xml exists and readable
   - Verify disk space ≥ 300MB
   - Create backup: `.ce.backup-{timestamp}/`
4. Update `extract()` method - GATE 2:
   - Extract to tmp/ce-staging/ (not target root)
   - Validate file count: 87 files (33 tools, 23 memories, 11 commands)
   - All files readable and non-zero size
5. Update `blend()` method - GATE 3:
   - Merge settings.local.json (framework + target permissions)
   - Append CLAUDE.md sections (framework + target)
   - Validate JSON/Markdown syntax
   - Copy framework files to final locations
6. Update `finalize()` method - GATE 4:
   - Run uv sync in .ce/tools/
   - Create .ce/INIT-SUCCESS marker
   - Verify: `uv run ce --version` works
   - Cleanup staging + backup
7. Add `rollback()` method for gate failures
8. Add streaming console output with timestamps

### Phase 3: TypeScript Simplification (1 hour)

**Pre-implementation: Serena Code Analysis**

Use Serena MCP to identify functions to delete and their usage:

```python
# 1. Get overview of init.ts structure
mcp__syntropy__serena_get_symbols_overview(
    relative_path="syntropy-mcp/src/tools/init.ts"
)

# 2. Find initProject function to understand call flow
mcp__syntropy__serena_find_symbol(
    name_path="initProject",
    include_body=True
)

# 3. Find legacy functions to be deleted
for func in ["copyBoilerplate", "scaffoldUserStructure", "blendRulesIntoCLAUDEmd", "findBoilerplatePath"]:
    mcp__syntropy__serena_find_symbol(
        name_path=func,
        include_body=False  # Just need location, not full body
    )

# 4. Find all references to legacy functions (ensure safe deletion)
mcp__syntropy__serena_find_referencing_symbols(
    name_path="copyBoilerplate"
)

# 5. Search for subprocess/exec patterns (to understand how to call Python)
mcp__syntropy__serena_search_for_pattern(
    pattern="exec|spawn|subprocess|child_process",
    file_glob="syntropy-mcp/src/**/*.ts"
)
```

**Analysis Goals**:
- Locate exact positions of functions to delete
- Verify functions only called from initProject (safe to delete)
- Find existing subprocess execution patterns to reuse
- Identify any helper functions that also need deletion

1. Delete legacy functions (search by name, delete entire function block):
   - `copyBoilerplate()` - Copies from filesystem boilerplate
   - `scaffoldUserStructure()` - Creates user directories
   - `blendRulesIntoCLAUDEmd()` - Merges RULES.md into CLAUDE.md
   - `findBoilerplatePath()` - Searches for boilerplate location

**After Serena analysis, use function boundaries** (not line numbers):
```typescript
// Serena will show exact function locations
// Delete entire function blocks from opening { to closing }
// Verify no other references before deletion
```

2. Replace with subprocess call: `uv run ce init-project --target ${projectRoot}`
3. Keep post-processing calls:
   - `activateSerenaProject()` (non-fatal)
   - `buildKnowledgeIndex()` (non-fatal)
   - `generateSummary()` (non-fatal)
4. Update error handling to surface Python errors

### Phase 4: Documentation (1 hour)

1. Update `examples/INITIALIZATION.md`:
   - Simplify from 5-phase manual → 4-phase automated workflow
   - Remove bucket collection phase (obsolete)
   - Remove user files migration phase (automated)
   - Add validation gate descriptions
   - Update expected file counts
2. Add troubleshooting section for gate failures

### Phase 5: Testing (2 hours)

1. **Test Greenfield**: Empty directory → Init → Verify 87 files + INIT-SUCCESS
2. **Test Existing Settings**: Project with .claude/settings.local.json → Verify merge
3. **Test Existing CLAUDE.md**: Project with CLAUDE.md → Verify append
4. **Test Failed Extraction**: Corrupt package → Verify rollback
5. **Test Failed Blend**: Invalid target JSON → Verify rollback
6. **Test Failed Finalize**: UV not installed → Verify error message
7. **Test Rollback** (detailed scenario):
   - Setup: Create project with existing .ce/ containing 5 test files
   - Action: Start init, force Gate 2 failure (corrupt package with only 40 files)
   - Verify rollback triggered:
     - Console shows "♻️ Rolling back to pre-init state..."
     - .ce/ restored with original 5 files (verify content matches)
     - File count: `ls .ce/ | wc -l` returns 5
     - Content hash: Compare checksums of restored files vs original
   - Verify staging cleanup:
     - tmp/ce-staging/ deleted
     - No orphaned files in tmp/
   - Verify error logged:
     - .ce/init-{timestamp}.log contains Gate 2 failure details
8. **Test Legacy Cleanup**: After success, verify syntropy-mcp/ce/ deleted


## 4. Validation Gates

These are **runtime gates** during init execution (not test gates):

**Error Output Format** (consistent across all gates):
```
[HH:MM:SS] ❌ GATE X FAILED: <specific error>
[HH:MM:SS] 🔧 Troubleshooting: <actionable steps>
[HH:MM:SS] 📄 Full log: .ce/init-{timestamp}.log
[HH:MM:SS] ♻️  Rolling back to pre-init state...
[HH:MM:SS] ✓ Rollback complete
[HH:MM:SS] ❌ Initialization aborted
```

**Example**:
```
[14:30:05] ❌ GATE 2 FAILED: Expected 87 files, got 45
[14:30:05] 🔧 Troubleshooting: Extraction incomplete - check package integrity
[14:30:05] 📄 Full log: .ce/init-20251113-143000.log
[14:30:06] ♻️  Rolling back to pre-init state...
[14:30:07] ✓ Rollback complete (restored .ce/ from backup)
[14:30:07] ❌ Initialization aborted
```

### Gate 1: PREFLIGHT Validation

**When**: Before extraction begins
**Built into**: Python init workflow (automatic)

**Success Criteria**:
- Target directory exists and writable
- ce-infrastructure.xml exists and readable
- Disk space ≥ 300MB available
- Backup created: `.ce.backup-{timestamp}/` (if .ce/ exists)
- Git repository initialized (warning only)

**On Failure**: Abort with error message and troubleshooting steps

### Gate 2: EXTRACT Validation

**When**: After package extraction to staging
**Built into**: Python init workflow (automatic)

**Success Criteria**:
- Staging directory contains exactly 87 files:
  - 33 tool files (.py in tools/ce/)
  - 23 memory files (.md in .serena/memories/)
  - 11 command files (.md in .claude/commands/)
  - 1 PRP-0 template (.ce/PRPs/system/)
  - Other config files
- All files readable and non-zero size
- File count tolerance: ±5 files (warn if different, fail if >10 difference)

**On Failure**: Rollback (restore .ce.backup/), cleanup staging, abort with error

### Gate 3: BLEND Validation

**When**: After blending framework + target files
**Built into**: Python init workflow (automatic)

**Success Criteria**:
- settings.local.json is valid JSON (test with `json.load()`)
- CLAUDE.md is valid Markdown (basic syntax check)
- No framework files at target root (all in .ce/ or /system/ subdirs)
- Blended settings contains both framework and target permissions

**On Failure**: Rollback (restore .ce.backup/), cleanup staging, abort with error

### Gate 4: FINALIZE Validation

**When**: After installation completes
**Manual verification**: `uv run ce --version && test -f .ce/INIT-SUCCESS`

**Success Criteria**:
- `uv run ce --version` returns version number (non-zero exit = fail)
- `.ce/INIT-SUCCESS` marker file exists
- Commands work: `uv run ce validate --level 1` passes (non-fatal warning if fails)
- Staging directory deleted
- Backup directory deleted (on success)

**On Failure**: Leave backup intact, warn user to manually restore if needed


## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
uv run pytest tests/ -v
```

### Coverage Requirements

- Unit test coverage: ≥ 80%
- Integration tests for critical paths
- Edge cases from INITIAL.md covered


## 6. Rollout Plan

### Phase 1: Development

1. Implement core functionality
2. Write tests
3. Pass validation gates

### Phase 2: Review

1. Self-review code changes
2. Peer review (optional)
3. Update documentation

### Phase 3: Deployment

1. Merge to main branch
2. Monitor for issues
3. Update stakeholders


---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: 0
- **Test Patterns**: 1
- **Serena Available**: False

### Documentation Sources
- **Library Docs**: 0
- **External Links**: 0
- **Context7 Available**: False

---

## Peer Review Notes

**Reviewed**: 2025-11-13T20:30:00Z
**Review Type**: Context-naive document review
**Reviewer**: Claude (Sonnet 4.5)

### Issues Found and Fixed

1. ✅ **AC #6 Tolerance**: Added "±5 tolerance, fail if >10 difference" clarification
2. ✅ **Error Format**: Added consistent error output format template with example
3. ✅ **Package Structure**: Added before/after directory tree diagrams for reorganization
4. ✅ **Gate Pattern**: Added code snippet showing ValidationResult and PhaseValidator pattern
5. ✅ **Function Deletion**: Replaced brittle line numbers with function name search pattern
6. ✅ **Rollback Testing**: Expanded Test #7 with detailed verification steps
7. ✅ **Serena Analysis**: Added pre-implementation Serena MCP usage for:
   - Phase 2 (Python): Analyze existing init_project.py structure and validation patterns
   - Phase 3 (TypeScript): Identify functions to delete and verify safe deletion
8. ✅ **TL;DR "Why"**: Replaced generic template text with specific motivation:
   - References Certinia project production failure
   - Quantifies maintenance burden reduction (78%)
   - States time improvement (2-3 min vs 10-45 min)

### Assessment

**Quality**: ★★★★★ (5/5 after fixes)
- Clear problem statement with measurable outcomes
- Detailed implementation phases with code examples
- Comprehensive validation gates with error handling
- Thorough testing strategy with rollback verification
- **Follows CLAUDE.md "Syntropy MCP First" principle**: Uses Serena for code analysis before refactoring

**Ready for Execution**: ✅ YES
- All blocking issues resolved
- Package reorganization structure clear
- Gate implementation pattern provided
- Rollback verification detailed
- Serena analysis steps ensure safe refactoring

**Risk Level**: MEDIUM (dual codebase, package reorg, but well-specified with Serena guidance)
