---
prp_id: PRP-32.3.1
batch_id: 32
stage: 3
order: 1
feature_name: Memory Type System & Final Integration
status: pending
created: 2025-11-04T17:30:00Z
updated: 2025-11-04T17:30:00Z
complexity: medium
estimated_hours: 2-3
dependencies: PRP-32.1.1, PRP-32.2.1, PRP-32.2.2
issue: TBD
---

# Memory Type System & Final Integration

**Phase**: 5 of 5 - Memory Type System & Final Integration
**Batch**: 32 (Syntropy MCP 1.1 Release Finalization)
**Stage**: 3 (Final integration after Stage 1 and 2 complete)

## 1. TL;DR

**Objective**: Complete final integration phase for Syntropy MCP 1.1 release by implementing memory type system, unifying documentation updates, and regenerating repomix packages with all refinements

**What**: Add YAML type headers to all 23 Serena memories, unify INDEX.md and CLAUDE.md updates (collecting changes from Phase 1, 3, 4), regenerate repomix packages with Phase 4 consolidated docs, create final integration report, and update CHANGELOG.md for 1.1 release

**Why**: Finalize all documentation and infrastructure changes from Phase 1-4 in a single integration step to ensure consistency, avoid merge conflicts, and prepare framework for production distribution

**Effort**: 2-3 hours (memory updates 45 min, unification 1 hour, repomix 15 min, reports 30 min)

**Dependencies**: PRP-32.1.1 (classification report), PRP-32.2.1 (migration guides), PRP-32.2.2 (doc consolidation)

## 2. Context

### Background

This is the FINAL integration phase of the 5-phase Syntropy MCP 1.1 release finalization plan. Previous phases have:

**Phase 1 (PRP-32.1.1)**: Audited documentation, generated classification report identifying:
- 25 examples in INDEX.md (13 missing, 12 found)
- 23 Serena memories to classify
- Consolidation opportunities for Phase 4

**Phase 3 (PRP-32.2.1)**: Created 5 migration guides for deprecated MCP tools:
- migrate-repomix-to-serena.md
- migrate-github-mcp.md
- migrate-git-mcp.md
- migrate-filesystem-mcp.md
- migrate-perplexity-mcp.md

**Phase 4 (PRP-32.2.2)**: Consolidated overlapping documentation:
- Created examples/INITIALIZATION.md (unified initialization guide)
- Consolidated 3 command docs into workflow guides
- Total: 4 new/updated files

**Phase 5 (THIS PRP)**: Final integration:
- Implement memory type system (YAML headers for all 23 memories)
- Unify INDEX.md updates (collect all Phase 1, 3, 4 changes in single write)
- Unify CLAUDE.md updates (add initialization section + migration references)
- Regenerate repomix packages (with Phase 4 refined docs + memory headers)
- Create final integration report (summary of all 5 phases)
- Update CHANGELOG.md (1.1 release notes)

### Current State

**Memory Files** (23 files in `.serena/memories/`):
- **6 critical memories**: code-style-conventions, suggested-commands, task-completion-checklist, testing-standards, tool-usage-syntropy, use-syntropy-tools-not-bash
- **17 regular memories**: All other framework memories
- No YAML front matter currently
- All default to `type: regular` (users upgrade to `critical` manually during target project initialization)
- Need category, tags, timestamps
- **Note**: User memories in target projects get `type: user` during initialization (Phase 2 user file migration)

**INDEX.md** (`examples/INDEX.md`):
- Needs Phase 1 classification updates (file status corrections)
- Needs Phase 3 migration guide section (5 new files)
- Needs Phase 4 consolidated doc updates (4 files)
- Needs statistics update (file counts changed)

**CLAUDE.md** (root `CLAUDE.md`):
- Needs "Framework Initialization" section
- Needs migration guide references (link to examples/migration-guides/)
- Needs repomix usage documentation

**Repomix Packages**:
- Workflow package (`.ce/ce-workflow-docs.xml`): Currently includes outdated docs
- Infrastructure package (`.ce/ce-infrastructure.xml`): Missing memory type headers
- Need regeneration with Phase 4 refinements

**CHANGELOG.md**: Needs 1.1 release entry

### Constraints and Considerations

**Single Write Strategy**:
- INDEX.md and CLAUDE.md updated ONLY ONCE in this PRP
- Prevents conflicts with parallel PRPs (PRP-32.2.1, PRP-32.2.2 already complete)
- Collects ALL changes from dependencies before writing

**Memory Type Defaults**:
- All 23 memories default to `type: regular`
- Users manually upgrade to `type: critical` later (not in this PRP)
- Category assigned based on content analysis (documentation/pattern/troubleshooting/etc)

**Repomix Token Limits**:
- Workflow package must stay <55KB (target: 50-52KB after Phase 4 consolidation)
- Infrastructure package must stay <45KB (target: 42-44KB with memory headers)
- Combined <100KB

**Dependency Validation**:
- Must verify PRP-32.1.1 classification report exists (docs/classification-report.md)
- Must verify PRP-32.2.1 migration guides exist (5 files in examples/migration-guides/)
- Must verify PRP-32.2.2 consolidated docs exist (examples/INITIALIZATION.md + 3 updated files)
- Fail fast with actionable errors if dependencies missing

### Documentation References

**Related PRPs**:
- PRP-32.1.1: Documentation Index & Classification Audit (Phase 1)
- PRP-32.2.1: Migration Guide Creation (Phase 3)
- PRP-32.2.2: Documentation Consolidation (Phase 4)

**Memory Type System Design**:
```yaml
---
type: regular|critical
category: pattern|documentation|configuration|troubleshooting|architecture
tags: [relevant, topic, keywords]
created: "2025-11-04T00:00:00Z"
updated: "2025-11-04T00:00:00Z"
---
```

**Repomix Configuration**:
- Workflow: `.ce/repomix/workflow.config.json`
- Infrastructure: `.ce/repomix/infrastructure.config.json`

**Tools**:
- Repomix: `uvx repomix --config <config> -o <output>`
- Validation: `cd tools && uv run ce validate --level 4`
- Context health: `cd tools && uv run ce context health`

## 3. Implementation Steps

### Phase 0: ce-32/ Workspace Setup (5 minutes)

**Goal**: Create centralized workspace for PRP-32 processing artifacts

**Steps**:
```bash
# Create ce-32/ folder structure
mkdir -p ce-32/docs
mkdir -p ce-32/cache
mkdir -p ce-32/builds
mkdir -p ce-32/validation

echo "✓ ce-32/ workspace created"
```

**Folder Structure**:
- **ce-32/docs/**: Processed documentation (classification reports, integration reports)
- **ce-32/cache/**: Temporary cache files during processing
- **ce-32/builds/**: Repomix package builds (ce-workflow-docs.xml, ce-infrastructure.xml)
- **ce-32/validation/**: Validation outputs and test extractions

**Purpose**: Centralize all PRP-32 development artifacts in one location (not distributed to target projects)

**Validation**:
```bash
test -d ce-32/docs && \
test -d ce-32/cache && \
test -d ce-32/builds && \
test -d ce-32/validation && \
echo "✓ ce-32/ workspace complete" || echo "✗ Workspace incomplete"
```

### Phase 1: Dependency Verification (15 minutes)

**Goal**: Verify all dependency outputs exist before proceeding

**Steps**:
1. Check PRP-32.1.1 classification report:
   ```bash
   test -f /Users/bprzybyszi/nc-src/ctx-eng-plus/docs/classification-report.md && echo "✓ Found" || echo "✗ Missing"
   ```

2. Check PRP-32.2.1 migration guides (5 files):
   ```bash
   for guide in migrate-repomix-to-serena migrate-github-mcp migrate-git-mcp migrate-filesystem-mcp migrate-perplexity-mcp; do
     test -f /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/migration-guides/${guide}.md && echo "✓ $guide" || echo "✗ $guide MISSING"
   done
   ```

3. Check PRP-32.2.2 consolidated docs:
   ```bash
   test -f /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/INITIALIZATION.md && echo "✓ INITIALIZATION.md" || echo "✗ Missing"
   ```

**Validation**: All dependency files must exist, or fail with error message:
```
ERROR: Missing dependency outputs from Phase [N]
Please execute PRP-32.[N] before continuing with PRP-32.3.1
```

### Phase 2: Memory Type System Implementation (45 minutes)

**Goal**: Add YAML type headers to all 23 Serena memory files

**Steps**:
1. Discover all memory files:
   ```bash
   find /Users/bprzybyszi/nc-src/ctx-eng-plus/.serena/memories -name "*.md" -type f | sort
   ```

2. For each memory file:
   - Read file to analyze content
   - Determine category (documentation/pattern/troubleshooting/architecture/configuration)
   - Extract relevant tags (max 3-5 tags)
   - Set created/updated timestamps to 2025-11-04T17:30:00Z
   - Prepend YAML front matter with `type: regular`

3. YAML Header Template:
   ```yaml
   ---
   type: regular
   category: [documentation|pattern|troubleshooting|architecture|configuration]
   tags: [tag1, tag2, tag3]
   created: "2025-11-04T17:30:00Z"
   updated: "2025-11-04T17:30:00Z"
   ---

   [existing content unchanged]
   ```

4. Category Assignment Logic:
   - **documentation**: Guides, references, how-tos (e.g., "tool-usage-patterns.md")
   - **pattern**: Code patterns, best practices (e.g., "batch-prp-patterns.md")
   - **troubleshooting**: Error resolution, debugging (e.g., "linear-mcp-troubleshooting.md")
   - **architecture**: System design, structure (e.g., "system-architecture.md")
   - **configuration**: Setup, config files (e.g., "syntropy-config.md")

5. Update `.serena/memories/README.md`:
   - Add "Memory Type System" section
   - Document type: regular vs critical
   - Explain category taxonomy
   - Show upgrade path (regular → critical)

**Output**: All 23 memory files with YAML headers

**Validation**:
```bash
# Verify all 23 files have YAML headers
grep -l "^---$" /Users/bprzybyszi/nc-src/ctx-eng-plus/.serena/memories/*.md | wc -l
# Expected: 23 (excluding README.md)
```

### Phase 2.5: User File Migration Documentation (10 minutes)

**Goal**: Document how user files get YAML headers during target project initialization

**Background**:
- Framework memories (23 files) get `type: regular` in ctx-eng-plus (this PRP)
- User memories/PRPs in target projects get `type: user` during Phase 2 of INITIALIZATION.md workflow

**Documentation Updates**:

Add to examples/INITIALIZATION.md Phase 2 section:

**User Memory YAML Headers**:
```yaml
---
type: user
source: target-project
created: "2025-11-04T00:00:00Z"
updated: "2025-11-04T00:00:00Z"
---

[existing user memory content]
```

**User PRP YAML Headers**:
```yaml
---
prp_id: USER-001
title: User Feature Implementation
status: completed
created: "2025-11-04"
source: target-project
type: user
---

[existing user PRP content]
```

**Key Points**:
- Framework files: `type: regular` or `type: critical` (ctx-eng-plus)
- User files: `type: user` (target projects during initialization)
- Source: `target-project` (distinguishes from framework source)

**Validation**:
```bash
# Verify INITIALIZATION.md documents user file migration
grep "type: user" examples/INITIALIZATION.md && echo "✓ User migration documented"
```

### Phase 3: INDEX.md Unified Update (30 minutes)

**Goal**: Collect all changes from Phase 1, 3, 4 and apply to INDEX.md in single write

**Steps**:
1. Read current INDEX.md:
   ```bash
   cat /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/INDEX.md
   ```

2. Collect Phase 1 changes (from classification report):
   - Mark missing files as (DEPRECATED) or (MISSING)
   - Update file status for found files
   - Correct file counts in statistics

3. Collect Phase 3 changes (migration guides):
   - Add new "Migration & Initialization" section
   - List 5 migration guide files:
     - migrate-repomix-to-serena.md
     - migrate-github-mcp.md
     - migrate-git-mcp.md
     - migrate-filesystem-mcp.md
     - migrate-perplexity-mcp.md

4. Collect Phase 4 changes (consolidated docs):
   - Add examples/INITIALIZATION.md (NEW)
   - Update any file paths that changed during consolidation

5. Update statistics:
   - Recalculate total file count (examples/)
   - Recalculate total line count (Serena memories unchanged: 23 files, ~3,621 lines)
   - Add migration guide count (5 files)

6. Write unified INDEX.md update (single Edit operation)

**Output**: Updated INDEX.md with all Phase 1, 3, 4 changes

**Validation**:
```bash
# Verify migration section exists
grep -q "Migration & Initialization" /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/INDEX.md && echo "✓ Migration section added"

# Verify file counts updated
grep "Total Examples:" /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/INDEX.md
```

### Phase 4: CLAUDE.md Integration (20 minutes)

**Goal**: Add framework initialization section and migration guide references

**Steps**:
1. Read current CLAUDE.md structure:
   ```bash
   grep "^## " /Users/bprzybyszi/nc-src/ctx-eng-plus/CLAUDE.md
   ```

2. Add new "Framework Initialization" section after "Quick Commands":
   ```markdown
   ## Framework Initialization

   **First-time setup**: See [examples/INITIALIZATION.md](examples/INITIALIZATION.md) for complete initialization guide.

   **Key steps**:
   1. Activate Serena with project root path
   2. Load workflow context via repomix
   3. Verify MCP connections (`/syntropy-health`)
   4. Run context health check (`cd tools && uv run ce context health`)

   **Repomix Usage** (manual context loading):
   ```bash
   # Load workflow docs (commands, validation, PRP patterns)
   cat .ce/ce-workflow-docs.xml

   # Load infrastructure docs (memories, rules, system architecture)
   cat .ce/ce-infrastructure.xml
   ```

   **Migration from deprecated tools**: See [examples/migration-guides/](examples/migration-guides/) for tool-specific migration paths:
   - [Repomix → Serena](examples/migration-guides/migrate-repomix-to-serena.md)
   - [GitHub MCP → gh CLI](examples/migration-guides/migrate-github-mcp.md)
   - [Git MCP → native git](examples/migration-guides/migrate-git-mcp.md)
   - [Filesystem MCP → native tools](examples/migration-guides/migrate-filesystem-mcp.md)
   - [Perplexity MCP → WebSearch](examples/migration-guides/migrate-perplexity-mcp.md)
   ```

3. Write unified CLAUDE.md update (single Edit operation)

**Output**: Updated CLAUDE.md with initialization section

**Validation**:
```bash
grep -q "Framework Initialization" /Users/bprzybyszi/nc-src/ctx-eng-plus/CLAUDE.md && echo "✓ Initialization section added"
```

### Phase 5: Repomix Package Regeneration with /system/ Organization (20 minutes)

**Goal**: Regenerate workflow and infrastructure packages with Phase 4 refined docs, memory type headers, and CE 1.1 /system/ organization

**Steps**:

**Step 5.1: Regenerate Workflow Package** (no changes from CE 1.0)
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
npx repomix --config .ce/repomix-profile-workflow.yml
# Output: .ce/ce-workflow-docs.xml (reference package, NOT extracted)
```

**Step 5.2: Regenerate Infrastructure Package with /system/ Structure**

```bash
# Generate infrastructure package
npx repomix --config .ce/repomix-profile-infrastructure.yml

# Run post-processing to add /system/ organization
bash .ce/reorganize-infrastructure.sh

# Validation: Verify /system/ structure
npx repomix --unpack .ce/ce-infrastructure.xml --target .tmp/validation/
test -d .tmp/validation/.ce/examples/system && echo "✓ /system/ structure"
test -d .tmp/validation/.ce/PRPs/system && echo "✓ PRPs /system/ structure"
test -d .tmp/validation/.serena/memories/system && echo "✓ Memories /system/ structure"

# Move packages to ce-32/builds/
mkdir -p ce-32/builds/
mv .ce/ce-workflow-docs.xml ce-32/builds/
mv .ce/ce-infrastructure.xml ce-32/builds/
echo "✓ Packages moved to ce-32/builds/"
```

**Purpose**: Centralize repomix builds in ce-32/ folder for organized PRP-32 processing

**Note**: ce-32/ is ctx-eng-plus development artifact, not distributed to target projects

**Step 5.3: Validate Package Organization**

```bash
# Extract and verify structure
mkdir -p .tmp/final-validation/
npx repomix --unpack .ce/ce-infrastructure.xml --target .tmp/final-validation/

# Verify directory structure matches CE 1.1 design
test -d .tmp/final-validation/.ce/examples/system && echo "✓ System examples dir"
test -d .tmp/final-validation/.ce/PRPs/system && echo "✓ System PRPs dir"
test -d .tmp/final-validation/.serena/memories/system && echo "✓ System memories dir"

# Verify file counts
EXAMPLES=$(find .tmp/final-validation/.ce/examples/system/ -name "*.md" | wc -l)
MEMORIES=$(find .tmp/final-validation/.serena/memories/system/ -name "*.md" | wc -l)
COMMANDS=$(find .tmp/final-validation/.claude/commands/ -name "*.md" | wc -l)

echo "Framework files:"
echo "  Examples: $EXAMPLES (expected: 21)"
echo "  Memories: $MEMORIES (expected: 23)"
echo "  Commands: $COMMANDS (expected: 11)"
```

**Step 5.4: Check Token Counts**

```bash
# Workflow package (target <60KB)
wc -c /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-workflow-docs.xml

# Infrastructure package (target <150KB)
wc -c /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-infrastructure.xml

# Combined total (target <210KB)
total_size=$(( $(wc -c < .ce/ce-workflow-docs.xml) + $(wc -c < .ce/ce-infrastructure.xml) ))
echo "Combined size: ${total_size} bytes ($(( total_size / 1024 )) KB)"
```

**Step 5.5: Generate Markdown Mirrors**

```bash
npx repomix --config .ce/repomix-profile-workflow.yml --style markdown --output .ce/ce-workflow-docs.md
npx repomix --config .ce/repomix-profile-infrastructure.yml --style markdown --output .ce/ce-infrastructure.md
```

**Step 5.6: Update Package Manifest**

Update `.ce/repomix-manifest.yml`:
- Record new package sizes
- Update last_generated timestamp
- Confirm /system/ organization structure
- Update file counts (21 examples, 23 memories, 11 commands)

**Output**: Regenerated repomix packages (<210KB combined) with CE 1.1 /system/ organization

**Validation**:
```bash
# Verify both packages exist and are <210KB combined
total_size=$(( $(wc -c < /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-workflow-docs.xml) + $(wc -c < /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-infrastructure.xml) ))
echo "Combined size: ${total_size} bytes ($(( total_size / 1024 )) KB)"
[[ $total_size -lt 215040 ]] && echo "✓ Within token limit (<210KB)" || echo "✗ Exceeds 210KB limit"

# Verify /system/ organization in infrastructure package
npx repomix --unpack .ce/ce-infrastructure.xml --target .tmp/quick-check/
test -d .tmp/quick-check/.ce/examples/system && \
test -d .tmp/quick-check/.serena/memories/system && \
echo "✓ /system/ organization verified" || echo "✗ Missing /system/ structure"

# Cleanup validation directories
rm -rf .tmp/validation/ .tmp/final-validation/ .tmp/quick-check/
```

### Phase 6: Final Integration Report (30 minutes)

**Goal**: Create comprehensive summary of all 5 phases

**Steps**:
1. Create `docs/final-integration-report.md` with structure:
   ```markdown
   # Syntropy MCP 1.1 Release - Final Integration Report

   **Generated**: 2025-11-04T17:30:00Z
   **Total Phases**: 5

   ## Executive Summary

   [High-level overview of release finalization]

   ## Phase 1: Documentation Index & Classification Audit

   **PRP**: PRP-32.1.1
   **Status**: Complete
   **Key Outputs**:
   - Classification report (docs/classification-report.md)
   - 13 missing files identified
   - 23 Serena memories ready for type system

   ## Phase 2: [Skipped - No PRP-32.2]

   ## Phase 3: Migration Guide Creation

   **PRP**: PRP-32.2.1
   **Status**: Complete
   **Key Outputs**:
   - 5 migration guides created (examples/migration-guides/)
   - Tool transition paths documented

   ## Phase 4: Documentation Consolidation

   **PRP**: PRP-32.2.2
   **Status**: Complete
   **Key Outputs**:
   - INITIALIZATION.md created (unified 3 docs)
   - Token reduction: [X]KB

   ## Phase 5: Memory Type System & Final Integration

   **PRP**: PRP-32.3.1 (THIS PRP)
   **Status**: Complete
   **Key Outputs**:
   - 23 memories with YAML type headers
   - INDEX.md unified update (Phase 1+3+4 changes)
   - CLAUDE.md initialization section added
   - Repomix packages regenerated ([X]KB + [Y]KB = [Z]KB total)

   ## Production Readiness Checklist

   - [ ] All 23 memories have type: headers
   - [ ] INDEX.md updated with migration guides section
   - [ ] CLAUDE.md has initialization section
   - [ ] Repomix packages <100KB combined
   - [ ] Full validation suite passes (ce validate --level 4)
   - [ ] Context health check passes (ce context health)
   - [ ] CHANGELOG.md updated for 1.1 release

   ## Token Usage Summary

   **Before Optimization**:
   - Workflow package: [X]KB
   - Infrastructure package: [Y]KB
   - Total: [Z]KB

   **After Optimization** (Phase 4 + Phase 5):
   - Workflow package: [X]KB (Δ [reduction])
   - Infrastructure package: [Y]KB (Δ [increase for headers])
   - Total: [Z]KB (Δ [net change])

   ## Next Steps

   1. Manual review of memory type classifications (upgrade regular → critical)
   2. User testing of initialization workflow
   3. Final validation sweep (`ce validate --level 4`)
   4. Syntropy MCP 1.1 release deployment
   ```

2. Populate report with actual data from dependency outputs

3. Calculate token usage deltas

**Output**: docs/final-integration-report.md

### Phase 7: CHANGELOG.md Update (10 minutes)

**Goal**: Add 1.1 release entry with all changes

**Steps**:
1. Read current CHANGELOG.md:
   ```bash
   head -20 /Users/bprzybyszi/nc-src/ctx-eng-plus/CHANGELOG.md
   ```

2. Add new entry at top:
   ```markdown
   ## [1.1.0] - 2025-11-04

   ### Added

   **CE 1.1 Framework Initialization**
   - 5-phase initialization workflow (bucket collection, user files, repomix, blending, cleanup)
   - /system/ organization for framework files (separation from user files)
   - 4 migration scenarios: Greenfield, Mature Project, CE 1.0 Upgrade, Partial Installation
   - PRP-0 convention: Document framework installation in meta-PRP
   - Zero noise guarantee: Legacy files cleaned up after migration

   **Migration Guides**
   - `examples/INITIALIZATION.md` - Master initialization guide
   - `examples/workflows/migration-greenfield.md` - New project (10 min)
   - `examples/workflows/migration-mature-project.md` - Add CE to existing code (45 min)
   - `examples/workflows/migration-existing-ce.md` - Upgrade CE 1.0 → CE 1.1 (40 min)
   - `examples/workflows/migration-partial-ce.md` - Complete partial installation (15 min)

   **Templates**
   - `examples/templates/PRP-0-CONTEXT-ENGINEERING.md` - CE installation documentation template

   **Memory Type System**
   - YAML headers for all 23 Serena memories (type: critical/regular)
   - Category taxonomy (documentation/pattern/troubleshooting/architecture/configuration)
   - Upgrade path documentation (regular → critical)

   ### Changed

   **Directory Structure**
   - Framework files moved to `/system/` subfolders (`.ce/examples/system/`, `.serena/memories/system/`)
   - User files remain in parent directories (`.ce/examples/`, `.serena/memories/`)
   - CLAUDE.md structure: Framework sections (marked) + user sections

   **Repomix Packages**
   - ce-workflow-docs.xml: <60KB (reference package, stored not extracted)
   - ce-infrastructure.xml: <150KB with /system/ organization (all framework files)
   - Combined total: <210KB (increased from <100KB for complete framework)
   - Post-processing script adds /system/ subdirectories
   - Development artifacts centralized in ce-32/ folder (docs, cache, builds, validation)

   **Memory Type System**
   - All 23 framework memories have YAML type headers
   - 6 critical memories: code-style-conventions, suggested-commands, task-completion-checklist, testing-standards, tool-usage-syntropy, use-syntropy-tools-not-bash
   - 17 regular memories: All other framework memories
   - User memories in target projects get `type: user` during initialization

   **User File Migration**
   - YAML headers added to user memories and PRPs during target project initialization
   - User memory header: `type: user`, `source: target-project`
   - User PRP header: `prp_id`, `title`, `status`, `source: target-project`, `type: user`
   - Documented in examples/INITIALIZATION.md Phase 2

   **INDEX.md & CLAUDE.md**
   - Added "Framework Initialization" section to CLAUDE.md
   - Added migration guide references
   - Updated file counts and statistics
   - Corrected broken path references

   ### Fixed
   - INDEX.md broken references (workflows/, config/, syntropy/ directories)
   - Documentation gaps from Phase 1 audit
   - Missing migration scenarios (partial CE installation)

   ### Deprecated
   - CE 1.0 flat organization (no `/system/` subfolders)
   - Root-level `PRPs/` directory (use `.ce/PRPs/` instead)
   - Root-level `examples/` directory (use `.ce/examples/` instead)

   ### Documentation
   - Final integration report (docs/final-integration-report.md)
   - Classification report (docs/classification-report.md)
   - Migration integration summary (examples/migration-integration-summary.md)
   ```

3. Write CHANGELOG.md update (single Edit operation)

**Output**: Updated CHANGELOG.md

**Validation**:
```bash
grep -q "## \[1.1.0\]" /Users/bprzybyszi/nc-src/ctx-eng-plus/CHANGELOG.md && echo "✓ 1.1 entry added"
```

### Phase 8: Final Validation (10 minutes)

**Goal**: Verify all changes pass validation suite

**Steps**:
1. Run full validation:
   ```bash
   cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
   uv run ce validate --level 4
   ```

2. Run context health check:
   ```bash
   cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
   uv run ce context health
   ```

3. Verify git status (all files tracked):
   ```bash
   cd /Users/bprzybyszi/nc-src/ctx-eng-plus
   git status
   ```

**Validation**: All commands exit with status 0

**Failure Handling**: If validation fails:
1. Document specific failures in final-integration-report.md
2. Add troubleshooting section with resolution steps
3. Do NOT commit changes until validation passes

## 4. Validation Gates

### Gate 1: Dependency Verification

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
test -f docs/classification-report.md && \
  test -f examples/migration-guides/migrate-repomix-to-serena.md && \
  test -f examples/INITIALIZATION.md && \
  echo "✓ All dependencies present" || echo "✗ Missing dependencies"
```

**Expected**: All 3 dependency outputs exist
**On Failure**: Fail fast with error message listing missing files

### Gate 2: Memory Type Headers

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
# Count files with YAML headers (excluding README.md)
yaml_count=$(grep -l "^---$" .serena/memories/*.md | grep -v README.md | wc -l)
echo "YAML headers: ${yaml_count}/23"
[[ $yaml_count -eq 23 ]] && echo "✓ All memories have headers" || echo "✗ Missing headers"
```

**Expected**: 23 files with YAML front matter
**On Failure**: List files missing headers, re-run Phase 2

### Gate 3: INDEX.md Update

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
grep -q "Migration & Initialization" examples/INDEX.md && \
  grep -q "migrate-repomix-to-serena.md" examples/INDEX.md && \
  echo "✓ INDEX.md updated" || echo "✗ INDEX.md missing updates"
```

**Expected**: Migration section present with 5 guide references
**On Failure**: Re-run Phase 3

### Gate 4: CLAUDE.md Update

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
grep -q "Framework Initialization" CLAUDE.md && \
  grep -q "examples/INITIALIZATION.md" CLAUDE.md && \
  echo "✓ CLAUDE.md updated" || echo "✗ CLAUDE.md missing updates"
```

**Expected**: Initialization section present with repomix usage docs
**On Failure**: Re-run Phase 4

### Gate 5: Repomix Package Sizes

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
workflow_size=$(wc -c < .ce/ce-workflow-docs.xml)
infra_size=$(wc -c < .ce/ce-infrastructure.xml)
total_size=$(( workflow_size + infra_size ))
workflow_kb=$(( workflow_size / 1024 ))
infra_kb=$(( infra_size / 1024 ))
total_kb=$(( total_size / 1024 ))

echo "Workflow: ${workflow_kb}KB (limit: 55KB)"
echo "Infrastructure: ${infra_kb}KB (limit: 45KB)"
echo "Total: ${total_kb}KB (limit: 100KB)"

[[ $workflow_size -lt 56320 ]] && [[ $infra_size -lt 46080 ]] && [[ $total_size -lt 102400 ]] && \
  echo "✓ Within token limits" || echo "✗ Exceeds limits"
```

**Expected**: Workflow <55KB, Infrastructure <45KB, Total <100KB
**On Failure**: Analyze package contents, identify bloat, suggest manual optimization

### Gate 6: Full Validation Suite

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce validate --level 4
```

**Expected**: Exit code 0, all checks pass
**On Failure**: Document failures in final-integration-report.md, resolve before commit

### Gate 7: Context Health Check

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce context health
```

**Expected**: All MCP connections healthy, no drift detected
**On Failure**: Run `/syntropy-health` for detailed diagnostics

### Gate 8: Final Integration Report

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
test -f docs/final-integration-report.md && \
  grep -q "Production Readiness Checklist" docs/final-integration-report.md && \
  echo "✓ Final report complete" || echo "✗ Report missing or incomplete"
```

**Expected**: Report exists with all sections populated
**On Failure**: Re-run Phase 6

### Gate 9: CHANGELOG.md Update

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
grep -q "## \[1.1.0\]" CHANGELOG.md && \
  grep -q "Memory type system" CHANGELOG.md && \
  echo "✓ CHANGELOG updated" || echo "✗ CHANGELOG missing entry"
```

**Expected**: 1.1.0 entry with all changes documented
**On Failure**: Re-run Phase 7

## 5. Testing Strategy

### Test Framework

**Validation**: pytest (existing `ce validate` command)
**Context Health**: `ce context health` (MCP connection checks)
**Manual**: File inspection, git diff review

### Test Command

```bash
# Full validation suite (level 4 = all checks)
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce validate --level 4

# Context health check
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce context health

# Repomix package validation (manual)
cat /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-workflow-docs.xml | wc -c
cat /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-infrastructure.xml | wc -c
```

### Test Coverage

**Memory Type System**:
- [ ] All 23 memory files have YAML headers
- [ ] All headers have required fields (type, category, tags, created, updated)
- [ ] All type values are "regular" (default)
- [ ] All category values are valid (documentation/pattern/troubleshooting/architecture/configuration)
- [ ] README.md updated with type system docs

**INDEX.md Update**:
- [ ] Migration & Initialization section added
- [ ] 5 migration guides listed
- [ ] INITIALIZATION.md referenced
- [ ] File counts updated (statistics)
- [ ] Phase 1 missing file status corrected

**CLAUDE.md Update**:
- [ ] Framework Initialization section added
- [ ] Repomix usage documented
- [ ] Migration guide links present (5 files)
- [ ] examples/INITIALIZATION.md referenced

**Repomix Packages**:
- [ ] Workflow package exists (.ce/ce-workflow-docs.xml)
- [ ] Infrastructure package exists (.ce/ce-infrastructure.xml)
- [ ] Workflow package <55KB
- [ ] Infrastructure package <45KB
- [ ] Combined <100KB
- [ ] Markdown mirrors generated (.md files)

**Final Integration Report**:
- [ ] docs/final-integration-report.md exists
- [ ] All 5 phases documented
- [ ] Production Readiness Checklist complete
- [ ] Token usage summary included
- [ ] Next steps section present

**CHANGELOG.md**:
- [ ] 1.1.0 entry added
- [ ] Added/Changed/Fixed/Documentation sections populated
- [ ] All Phase 1-5 changes documented

### Edge Cases

**Missing Dependencies**:
- Test: Delete dependency file, verify fail-fast behavior
- Expected: Clear error message listing missing file + PRP to execute

**Invalid YAML Headers**:
- Test: Manually corrupt YAML header syntax
- Expected: Validation catches syntax errors

**Repomix Package Too Large**:
- Test: Check if combined size >100KB
- Expected: Report token counts, suggest optimization (manual intervention required)

**Validation Failures**:
- Test: Introduce deliberate error (e.g., invalid file path)
- Expected: Gate 6 fails, error documented in final report

## 6. Rollout Plan

### Phase 1: Development (2-3 hours)

**Steps**:
1. Execute PRP-32.3.1 implementation phases (Phase 1-8)
2. Run all validation gates (Gate 1-9)
3. Review git diff for all changes
4. Commit changes with message:
   ```
   PRP-32.3.1: Memory type system & final integration (Syntropy MCP 1.1)

   - Add YAML type headers to 23 Serena memories (type: regular)
   - Update INDEX.md with migration guides + Phase 1/4 changes
   - Add Framework Initialization section to CLAUDE.md
   - Regenerate repomix packages with Phase 4 refined docs
   - Create final integration report (docs/final-integration-report.md)
   - Update CHANGELOG.md for 1.1 release

   Token usage: Workflow <55KB, Infrastructure <45KB, Total <100KB

   Batch: 32, Stage: 3, Dependencies: PRP-32.1.1, PRP-32.2.1, PRP-32.2.2
   ```

**Success Criteria**: All validation gates pass (exit code 0)

### Phase 2: Review (30 minutes)

**Steps**:
1. Manual review of final-integration-report.md
2. Verify production readiness checklist complete
3. Review CHANGELOG.md for accuracy
4. Test initialization workflow (examples/INITIALIZATION.md)
5. Spot-check migration guides for completeness

**Success Criteria**: No critical issues found, documentation accurate

### Phase 3: Merge & Release (15 minutes)

**Steps**:
1. Push branch to remote:
   ```bash
   git push origin prp-32.3.1-memory-type-final-integration
   ```

2. Create PR with summary:
   - Title: "PRP-32.3.1: Memory Type System & Final Integration (Syntropy MCP 1.1)"
   - Body: Link to final-integration-report.md, summarize 5 phases
   - Reviewers: Assign maintainer

3. Merge to main after approval

4. Tag release:
   ```bash
   git tag -a v1.1.0 -m "Syntropy MCP 1.1 Release"
   git push origin v1.1.0
   ```

**Success Criteria**: PR merged, release tagged, CI passes

### Phase 4: Post-Release (1 hour)

**Steps**:
1. Monitor CI/CD pipeline
2. Verify production deployment (if applicable)
3. Update Linear issue with completion notes
4. Archive batch 32 PRPs to PRPs/executed/
5. Announce 1.1 release (internal/external)

**Success Criteria**: Release stable, no rollback needed

---

## 7. Success Metrics

### Implementation Completeness

1. **ce-32/ Folder Structure**
   - ✅ Phase 0 documented in Implementation Steps
   - ✅ 4 subdirectories: docs, cache, builds, validation
   - ✅ Purpose: Centralize PRP-32 development artifacts
   - ✅ Note: Not distributed to target projects

2. **Memory Type System**
   - ✅ All 23 framework memories have YAML headers
   - ✅ Memory type split clarified: 6 critical + 17 regular
   - ✅ Critical memories explicitly listed (code-style-conventions, suggested-commands, task-completion-checklist, testing-standards, tool-usage-syntropy, use-syntropy-tools-not-bash)
   - ✅ User memories get `type: user` in target projects

3. **Repomix Package Management**
   - ✅ Packages moved to ce-32/builds/ (Phase 5, Step 5.2)
   - ✅ ce-32/builds/ce-workflow-docs.xml (<60KB)
   - ✅ ce-32/builds/ce-infrastructure.xml (<150KB)
   - ✅ /system/ organization verified (validation commands)

4. **User File Migration**
   - ✅ Phase 2.5 added to Implementation Steps
   - ✅ User memory YAML header template documented
   - ✅ User PRP YAML header template documented
   - ✅ INITIALIZATION.md Phase 2 references user file migration

5. **Documentation Updates**
   - ✅ INDEX.md unified update (Phase 3)
   - ✅ CLAUDE.md Framework Initialization section (Phase 4)
   - ✅ CHANGELOG.md 1.1 release entry with ce-32/, memory types, user migration

### Validation Coverage

- **9 validation gates**: Dependency verification, memory headers, INDEX/CLAUDE updates, package sizes, full validation, context health, final report, CHANGELOG
- **All phases have validation commands**: Clear pass/fail criteria
- **Token limits enforced**: <60KB workflow, <150KB infrastructure, <210KB total

### Cross-PRP Consistency

- ✅ File counts match PRP-32.1.2: 21 examples, 23 memories (6 critical + 17 regular), 11 commands
- ✅ ce-32/builds/ path consistent across PRP-32.1.2 and PRP-32.3.1
- ✅ /system/ organization consistent with PRP-32.1.3
- ✅ Memory type split documented consistently

---

## Research Findings

### Serena Codebase Analysis

**Memory Files** (23 files discovered):
```bash
find /Users/bprzybyszi/nc-src/ctx-eng-plus/.serena/memories -name "*.md" -type f
```

Expected categories:
- **documentation**: 8-10 files (guides, references)
- **pattern**: 5-7 files (code patterns, best practices)
- **troubleshooting**: 3-5 files (error resolution)
- **architecture**: 2-3 files (system design)
- **configuration**: 2-3 files (setup, config)

### Documentation Sources

**Phase 1 Classification Report** (PRP-32.1.1 output):
- Location: `docs/classification-report.md`
- Contains: INDEX.md gap analysis, file status corrections, consolidation opportunities

**Phase 3 Migration Guides** (PRP-32.2.1 output):
- Location: `examples/migration-guides/`
- Files: 5 migration guides (Repomix, GitHub MCP, Git MCP, Filesystem MCP, Perplexity MCP)

**Phase 4 Consolidated Docs** (PRP-32.2.2 output):
- Location: `examples/INITIALIZATION.md` + 3 updated files
- Token reduction: ~[X]KB from consolidation

**Repomix Configurations**:
- Workflow: `.ce/repomix/workflow.config.json`
- Infrastructure: `.ce/repomix/infrastructure.config.json`

### External References

- Memory type system design pattern (inspired by metadata headers in Jekyll, Hugo)
- YAML front matter standard (YAML 1.2 spec)
- Repomix documentation: https://github.com/yamadashy/repomix
- Token optimization strategies (consolidation, deduplication, structural improvements)

---

## Batch Generation Metadata

**Generated by**: Sonnet 4.5 subagent (batch mode)
**Parent coordinator**: /batch-gen-prp
**Heartbeat**: .tmp/batch-gen/PRP-32.3.1.status (15s polling)
**Batch ID**: 32
**Stage**: 3 (Final integration)
**Parallel PRPs**: None (sequential after Stage 1 and 2)

**Execution Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
/execute-prp PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md
```
