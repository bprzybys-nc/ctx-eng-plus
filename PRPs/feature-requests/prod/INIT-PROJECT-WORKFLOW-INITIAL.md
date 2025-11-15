# Feature: Init Project Workflow Overhaul

## FEATURE

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
6. Expected file count validation (87 files)
7. Init completes in 2-3 minutes (vs 10-45 minutes manual)
8. Zero silent failures

**4-Phase Pipeline:**
- **PHASE 1: PREFLIGHT** - Validate prerequisites, backup existing .ce/
- **PHASE 2: EXTRACT** - Unpack package to staging, validate 87 files extracted
- **PHASE 3: BLEND** - Merge settings/CLAUDE.md, validate JSON/Markdown
- **PHASE 4: FINALIZE** - Install deps, verify commands work, cleanup staging

## EXAMPLES

**Current TypeScript implementation** (syntropy-mcp/src/tools/init.ts):
```typescript
export async function initProject(args: InitProjectArgs): Promise<InitProjectResult> {
  // 733 lines total
  await copyBoilerplate(projectRoot, layout);  // Copies from filesystem
  await scaffoldUserStructure(projectRoot, layout);
  await blendRulesIntoCLAUDEmd(projectRoot, layout);
  await upsertSlashCommands(projectRoot, layout);
  await activateSerenaProject(projectRoot);  // Non-fatal
  await buildKnowledgeIndex(projectRoot);    // Non-fatal
  await generateSummary(projectRoot);        // Non-fatal
}
```

**Current Python implementation** (tools/ce/init_project.py):
```python
class ProjectInitializer:
    def run(self, phase: str = "all") -> Dict:
        # 410 lines total
        results["extract"] = self.extract()      # Unpacks repomix package
        results["blend"] = self.blend()          # Calls blend command
        results["initialize"] = self.initialize()  # Runs uv sync
        results["verify"] = self.verify()        # Checks files exist
        return results
```

**Proposed unified architecture** (Python primary, TypeScript wrapper):
```python
class ProjectInitializer:
    def run(self) -> Dict:
        # ~200 lines total
        self.preflight()   # GATE 1: Validate prerequisites
        self.extract()     # GATE 2: Extract + validate 87 files
        self.blend()       # GATE 3: Blend + validate JSON/MD
        self.finalize()    # GATE 4: Install + verify commands
```

**Validation gate example:**
```python
def gate2_extraction(staging: Path) -> ValidationResult:
    expected = {"tools": 33, "memories": 23, "commands": 11, "total": 87}
    actual = count_files(staging)
    if actual["total"] != expected["total"]:
        return ValidationResult(
            success=False,
            message=f"❌ GATE 2 FAILED: Expected {expected['total']} files, got {actual['total']}",
            troubleshooting="🔧 Extraction incomplete - check package integrity"
        )
    return ValidationResult(success=True)
```

**Streaming output example:**
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

**Rollback on failure:**
```python
def extract(self) -> Dict:
    backup = self.ce_dir.parent / f".ce.backup-{timestamp}"
    shutil.move(self.ce_dir, backup)  # Backup before extraction

    try:
        extract_to_staging()
        validate_staging()  # GATE 2
        copy_staging_to_target()
        shutil.rmtree(backup)  # Success - delete backup
    except Exception as e:
        shutil.move(backup, self.ce_dir)  # Rollback
        raise
```

See:
- syntropy-mcp/src/tools/init.ts:72-151 (current TypeScript)
- tools/ce/init_project.py:49-383 (current Python)
- PRPs/feature-requests/INIT-PROJECT-WORKFLOW-ROOT-CAUSE-ANALYSIS.md (failure analysis)

## DOCUMENTATION

**Repomix Package Structure:**
- Current: Extracts files to wrong locations (tools/ → needs move to .ce/tools/)
- Proposed: Pre-organized framework/ and blendable/ directories for direct copy

**Package Reorganization:**
```
ce-infrastructure.xml:
  framework/              # Ready for direct copy
    .ce/tools/
    .ce/PRPs/system/
    .serena/memories/     # Copy to /system/ subdir
    .claude/commands/
  blendable/              # Needs merging
    CLAUDE.md             # Framework sections to append
    settings.json         # Framework permissions to merge
```

**Error Logging:**
- Log file: `.ce/init-{timestamp}.log`
- Contains: Phase timestamps, file operations, gate results, errors
- Example: `.ce/init-20251113-143000.log`

**Success Marker:**
- File: `.ce/INIT-SUCCESS`
- Created after GATE 4 passes
- Contains: version, timestamp, file count

**Tools:**
- UV package manager for Python deps
- Repomix CLI for package extraction
- Serena MCP for project activation

## OTHER CONSIDERATIONS

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
