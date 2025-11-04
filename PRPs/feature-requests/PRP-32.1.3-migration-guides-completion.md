---
prp_id: PRP-32.1.3
title: Unified CE 1.1 Initialization Guide
status: feature_request
created: 2025-11-04
batch: 32
phase: 1
order: 3
estimated_hours: 3
complexity: medium
dependencies: []
files_modified:
  - examples/INITIALIZATION.md
  - examples/templates/PRP-0-CONTEXT-ENGINEERING.md
files_deleted:
  - examples/workflows/migration-greenfield.md
  - examples/workflows/migration-mature-project.md
  - examples/workflows/migration-existing-ce.md
  - examples/workflows/migration-partial-ce.md
  - examples/migration-integration-summary.md
risk_level: low
---

# PRP-32.1.3: Unified CE 1.1 Initialization Guide

## 📋 TL;DR

**Problem**: Multiple separate migration guides (4 guides: greenfield, mature-project, existing-ce, partial-ce) duplicate the same 5-phase workflow with slight variations, creating high maintenance burden and documentation drift risk.

**Impact**:
- 4x maintenance cost (changes must be synchronized across 4 files)
- Documentation drift (guides diverge over time)
- User confusion (which guide to choose?)

**Solution**: Create ONE unified CE 1.1 initialization guide based on 5-phase workflow from file-structure-of-ce-initial.md. Handle migration scenarios as variations within phases.

**Deliverables**:
1. `examples/INITIALIZATION.md` - Unified initialization guide (replaces 4 separate guides)
2. `examples/templates/PRP-0-CONTEXT-ENGINEERING.md` - CE installation documentation template (updated)
3. Delete 4 existing migration guides

**Effort**: 3 hours (2h unified guide creation + 30min file cleanup + 30min validation)

**Result**: Single source of truth, 60% less maintenance, clearer user experience.

---

## 🎯 Problem Statement

### Current State

**4 Separate Migration Guides** (created in earlier CE development):
```
examples/workflows/
├── migration-greenfield.md          (~11KB, 10 min workflow)
├── migration-mature-project.md      (~15KB, 45 min workflow)
├── migration-existing-ce.md         (~12KB, 40 min workflow)
└── migration-partial-ce.md          (~9KB, 15 min workflow)
```

**Issues**:
1. **Duplication**: All 4 guides follow same 5-phase workflow with minor variations
2. **Maintenance burden**: Changes require updating 4 files
3. **Drift risk**: Guides diverge over time (inconsistent commands, different validation)
4. **User confusion**: Users must read all 4 to understand differences

### Desired State

**ONE Unified Guide**:
```
examples/
└── INITIALIZATION.md                (~25KB, scenario-aware)
    ├── Phase 1: Bucket Collection
    ├── Phase 2: User Files Copy (scenario variations)
    ├── Phase 3: Repomix Package Handling
    ├── Phase 4: CLAUDE.md Blending
    └── Phase 5: Legacy Cleanup
```

**Benefits**:
- Single source of truth
- 60% less maintenance (1 file vs 4 files)
- Scenario handling via decision points within phases
- Consistent validation commands across all scenarios

---

## 🔍 Analysis

### Why Consolidation Works

**5-Phase Workflow is Universal**:
- Phase 1 (Bucket Collection): Same for all scenarios
- Phase 2 (User Files Copy): **Varies by scenario** (skip for greenfield, full for mature)
- Phase 3 (Repomix Handling): Same for all scenarios
- Phase 4 (CLAUDE.md Blending): Same for all scenarios
- Phase 5 (Legacy Cleanup): **Varies by scenario** (minimal for greenfield, aggressive for CE 1.0 upgrade)

**Scenario Variations are Minimal**:
- **Greenfield**: Skip Phase 2 (no user files)
- **Mature Project**: Full Phase 2 (all buckets), skip Phase 5 (no legacy)
- **CE 1.0 Upgrade**: Full Phase 2, aggressive Phase 5 (delete legacy structure)
- **Partial Install**: Selective Phase 2 (only missing components), selective Phase 3

**Implementation**: Add "Scenario Variations" subsections in Phase 2 and Phase 5

---

## 🛠️ Implementation

### Step 1: Create examples/INITIALIZATION.md (2 hours)

**Content Source**: `PRPs/feature-requests/file-structure-of-ce-initial.md` (5-phase workflow)

**Enhancements**:
1. Add scenario decision tree at beginning
2. Expand Phase 2 with user file migration (YAML headers for memories/PRPs)
3. Add validation commands for each phase
4. Include troubleshooting section
5. Add rollback procedure
6. Include scenario variations within phases (not separate sections)

**File Size Target**: ~25KB

**Structure**:

```markdown
# CE 1.1 Framework Initialization Guide

## Overview
- CE 1.1 architecture (/system/ organization)
- 5-phase workflow summary
- Migration scenario decision tree

## Scenario Decision Tree
```
START
├─ Has existing CE components?
│  ├─ NO → Greenfield (10 min)
│  │      Skip Phase 2, minimal Phase 5
│  └─ YES
│     ├─ CE 1.0 structure? → CE 1.0 Upgrade (40 min)
│     │                       Full Phase 2, aggressive Phase 5
│     ├─ Incomplete CE? → Partial Install (15 min)
│     │                    Selective Phase 2 & 3
│     └─ No CE, has docs? → Mature Project (45 min)
│                            Full Phase 2, skip Phase 5
```

## Phase 1: Bucket Collection (5-10 min)
[Universal workflow - no scenario variations]

- Staging area setup (tmp/syntropy-initialization/)
- Copy files to buckets (serena, examples, prps, claude-md, claude-dir)
- Validate bucket contents (mark .fake files)
- Bucket characteristics (KISS heuristics)

## Phase 2: User Files Copy (10-15 min)

### Scenario Variations

**Greenfield Projects**: Skip this phase entirely (no user files exist)

**All Other Scenarios**: Proceed with steps below

### Step 2.1: User Memory Migration
- Scan user memories in serena/ bucket
- Add YAML headers (type: user, source: target-project, created: date)
- Example user memory with header

### Step 2.2: User PRP Migration
- Scan user PRPs in prps/ bucket
- Add CE-compatible YAML headers (prp_id, title, status, created, source)
- Extract metadata from filenames
- Example user PRP with header

### Step 2.3: Copy Validated Files
- Copy non-.fake files to CE 1.1 destinations
- .serena/memories/ (user memories)
- .ce/PRPs/executed/ (user PRPs)
- .ce/examples/ (user examples)
- .claude/ (user commands/config)

### Scenario-Specific Handling

**Mature Project**: Copy all buckets (full migration)
**CE 1.0 Upgrade**: Copy all buckets + validate existing CE structure
**Partial Install**: Copy only buckets with missing components

## Phase 3: Repomix Package Handling (5 min)
[Universal workflow - no scenario variations except Partial Install]

### Step 3.1: Copy Workflow Package
- ce-workflow-docs.xml → .ce/examples/system/ (reference only)

### Step 3.2: Extract Infrastructure Package
- ce-infrastructure.xml extraction
- Creates /system/ subfolders automatically
- Framework file destinations:
  - .ce/examples/system/ (21 framework examples)
  - .serena/memories/system/ (23 framework memories)
  - .claude/commands/ (11 framework commands)
  - tools/ (33 tool source files)

**Partial Install Variation**: Extract only missing components

## Phase 4: CLAUDE.md Blending (10 min)
[Universal workflow - no scenario variations]

- Backup existing CLAUDE.md
- Merge framework + user sections
- Mark sections: [FRAMEWORK] vs [PROJECT]
- Denoise blended CLAUDE.md

## Phase 5: Legacy Cleanup (5 min)

### Scenario Variations

**Greenfield Projects**: Skip this phase (no legacy files)

**Mature Projects**: Skip this phase (no legacy CE structure)

**CE 1.0 Upgrade**: Aggressive cleanup
- Verify migration completed
- Archive legacy organization (backup)
- Delete legacy files:
  - PRPs/ directory → migrated to .ce/PRPs/
  - examples/ directory → migrated to .ce/examples/
  - .serena/memories/*.md → migrated to .serena/memories/system/
- Log cleanup summary
- Zero noise verification

**Partial Install**: Selective cleanup (only duplicate system files)

## Validation Checklist
- CE 1.1 structure verification
- File count checks (21 examples, 23 memories, 11 commands)
- Legacy file deletion confirmation (if applicable)
- No duplicate system memories
- Backup created (if cleanup performed)

## Troubleshooting
- Common issues during each phase
- Rollback procedure
- Conflict resolution
- Missing components

## Appendix: Scenario Summary

| Scenario | Phase 2 | Phase 3 | Phase 5 | Time |
|----------|---------|---------|---------|------|
| Greenfield | Skip | Full | Skip | 10 min |
| Mature Project | Full | Full | Skip | 45 min |
| CE 1.0 Upgrade | Full | Full | Aggressive | 40 min |
| Partial Install | Selective | Selective | Selective | 15 min |
```

**Validation**:
```bash
# Check file created
test -f examples/INITIALIZATION.md && echo "✓ INITIALIZATION.md created"

# Check size (~25KB)
wc -c examples/INITIALIZATION.md

# Verify 5 phase sections exist
grep "^## Phase [1-5]:" examples/INITIALIZATION.md | wc -l
# Expected: 5

# Verify scenario variations documented
grep -i "scenario" examples/INITIALIZATION.md | wc -l
# Expected: 10+ occurrences
```

---

### Step 2: Update PRP-0 Template (15 minutes)

**File**: `examples/templates/PRP-0-CONTEXT-ENGINEERING.md`

**Changes**:
1. Update "Migration Guide" references (lines ~221-224)
2. Remove scenario-specific guide references
3. Reference INITIALIZATION.md only

**OLD**:
```markdown
**Migration Guides**:
- `examples/INITIALIZATION.md` - Master initialization guide
- `examples/workflows/migration-{scenario}.md` - Scenario-specific guides
```

**NEW**:
```markdown
**Migration Guide**:
- `examples/INITIALIZATION.md` - Complete CE 1.1 initialization guide (5-phase workflow, scenario-aware)
```

**Validation**:
```bash
# Verify references updated
grep "INITIALIZATION.md" examples/templates/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ Reference updated"

# Verify no broken references
! grep "migration-.*\.md" examples/templates/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ No broken references"
```

---

### Step 3: Delete Obsolete Files (10 minutes)

**Files to Delete**:
```bash
# Delete 4 separate migration guides
rm examples/workflows/migration-greenfield.md
rm examples/workflows/migration-mature-project.md
rm examples/workflows/migration-existing-ce.md
rm examples/workflows/migration-partial-ce.md

# Delete planning document (replaced by INITIALIZATION.md)
rm examples/migration-integration-summary.md

echo "✓ Obsolete files deleted"
```

**Rationale**:
- migration-greenfield.md: Replaced by INITIALIZATION.md (Greenfield scenario variation)
- migration-mature-project.md: Replaced by INITIALIZATION.md (Mature Project scenario variation)
- migration-existing-ce.md: Replaced by INITIALIZATION.md (CE 1.0 Upgrade scenario variation)
- migration-partial-ce.md: Replaced by INITIALIZATION.md (Partial Install scenario variation)
- migration-integration-summary.md: Planning artifact, no longer needed

**Validation**:
```bash
# Verify files deleted
! test -f examples/workflows/migration-greenfield.md && echo "✓ greenfield deleted"
! test -f examples/workflows/migration-mature-project.md && echo "✓ mature-project deleted"
! test -f examples/workflows/migration-existing-ce.md && echo "✓ existing-ce deleted"
! test -f examples/workflows/migration-partial-ce.md && echo "✓ partial-ce deleted"
! test -f examples/migration-integration-summary.md && echo "✓ integration-summary deleted"
```

---

### Step 4: Update Cross-References (15 minutes)

**Files to Check**:
- `examples/INDEX.md` (if exists and references migration guides)
- `CLAUDE.md` (if references migration guides)
- Other PRP-32.x files

**Search and Update**:
```bash
# Find any references to deleted guides
grep -r "migration-greenfield\|migration-mature-project\|migration-existing-ce\|migration-partial-ce" \
  examples/ PRPs/ CLAUDE.md 2>/dev/null

# Update to reference INITIALIZATION.md instead
# (manual edits based on search results)
```

**Expected**: Most references should be in historical PRP documents (executed PRPs), which can remain as historical record.

---

### Step 5: Validate Integration (10 minutes)

```bash
# Verify INITIALIZATION.md exists
test -f examples/INITIALIZATION.md && echo "✓ Unified guide created"

# Check size (~25KB target)
FILE_SIZE=$(wc -c < examples/INITIALIZATION.md)
echo "File size: $((FILE_SIZE / 1024))KB"
test $FILE_SIZE -gt 20000 && test $FILE_SIZE -lt 30000 && echo "✓ Size appropriate"

# Verify 5 phases documented
PHASE_COUNT=$(grep -c "^## Phase [1-5]:" examples/INITIALIZATION.md)
test $PHASE_COUNT -eq 5 && echo "✓ All 5 phases documented"

# Verify scenario variations documented
SCENARIO_COUNT=$(grep -ci "scenario" examples/INITIALIZATION.md)
test $SCENARIO_COUNT -gt 10 && echo "✓ Scenarios documented"

# Verify obsolete files deleted
! test -f examples/workflows/migration-greenfield.md && echo "✓ Old guides deleted"

# Verify PRP-0 template updated
grep "INITIALIZATION.md" examples/templates/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ PRP-0 template updated"

# Check for broken references
BROKEN_REFS=$(grep -r "migration-.*\.md" examples/ PRPs/feature-requests/ 2>/dev/null | grep -v "INITIALIZATION.md" | grep -v "executed" | wc -l)
test $BROKEN_REFS -eq 0 && echo "✓ No broken references" || echo "⚠ Found $BROKEN_REFS broken references"
```

---

## ✅ Validation Gates

### Gate 1: INITIALIZATION.md Created and Complete

**Criteria**:
- File exists at `examples/INITIALIZATION.md`
- Size: 20-30KB
- Contains 5 phase sections
- Contains scenario decision tree
- Contains scenario variations in Phase 2 and Phase 5
- Contains validation checklist
- Contains troubleshooting section

**Command**:
```bash
test -f examples/INITIALIZATION.md && \
  test $(wc -c < examples/INITIALIZATION.md) -gt 20000 && \
  test $(grep -c "^## Phase [1-5]:" examples/INITIALIZATION.md) -eq 5 && \
  grep -q "Decision Tree" examples/INITIALIZATION.md && \
  grep -q "Scenario Variations" examples/INITIALIZATION.md && \
  echo "✓ Gate 1 passed" || echo "✗ Gate 1 failed"
```

---

### Gate 2: PRP-0 Template Updated

**Criteria**:
- File exists at `examples/templates/PRP-0-CONTEXT-ENGINEERING.md`
- References INITIALIZATION.md (not migration-*.md)
- No broken references to deleted guides

**Command**:
```bash
test -f examples/templates/PRP-0-CONTEXT-ENGINEERING.md && \
  grep -q "INITIALIZATION.md" examples/templates/PRP-0-CONTEXT-ENGINEERING.md && \
  ! grep "migration-greenfield\|migration-mature-project\|migration-existing-ce\|migration-partial-ce" \
    examples/templates/PRP-0-CONTEXT-ENGINEERING.md && \
  echo "✓ Gate 2 passed" || echo "✗ Gate 2 failed"
```

---

### Gate 3: Obsolete Files Deleted

**Criteria**:
- 4 migration guide files deleted
- migration-integration-summary.md deleted

**Command**:
```bash
! test -f examples/workflows/migration-greenfield.md && \
! test -f examples/workflows/migration-mature-project.md && \
! test -f examples/workflows/migration-existing-ce.md && \
! test -f examples/workflows/migration-partial-ce.md && \
! test -f examples/migration-integration-summary.md && \
  echo "✓ Gate 3 passed" || echo "✗ Gate 3 failed"
```

---

### Gate 4: No Broken Cross-References

**Criteria**:
- No references to deleted guides in examples/ or PRPs/feature-requests/
- Historical references in PRPs/executed/ are acceptable

**Command**:
```bash
BROKEN_REFS=$(grep -r "migration-greenfield\|migration-mature-project\|migration-existing-ce\|migration-partial-ce" \
  examples/ PRPs/feature-requests/ 2>/dev/null | grep -v "INITIALIZATION.md" | wc -l)
test $BROKEN_REFS -eq 0 && echo "✓ Gate 4 passed" || echo "⚠ Gate 4: $BROKEN_REFS broken references found"
```

---

## 🚀 Rollout Plan

### Phase 1: File Creation (2h)

**Tasks**:
1. Create `examples/INITIALIZATION.md` (2h)
   - Base on file-structure-of-ce-initial.md
   - Add scenario decision tree
   - Expand Phase 2 with user file migration
   - Add scenario variations in Phase 2 & 5
   - Add validation checklist
   - Add troubleshooting section

2. Update `examples/templates/PRP-0-CONTEXT-ENGINEERING.md` (15min)
   - Update migration guide references
   - Remove scenario-specific references

---

### Phase 2: File Cleanup (15min)

**Tasks**:
1. Delete 4 migration guides
2. Delete migration-integration-summary.md
3. Verify deletions

---

### Phase 3: Validation (30min)

**Tasks**:
1. Run all 4 validation gates
2. Check cross-references
3. Verify no broken links
4. Test scenario decision tree logic

---

### Phase 4: Commit (5min)

**Commit Message**:
```
Consolidate CE 1.1 migration guides into unified INITIALIZATION.md

- Create examples/INITIALIZATION.md (unified guide, scenario-aware)
- Update PRP-0 template to reference unified guide
- Delete 4 obsolete migration guides (greenfield, mature-project, existing-ce, partial-ce)
- Delete migration-integration-summary.md (planning artifact)
- 60% reduction in maintenance burden (1 file vs 4 files)

Resolves: PRP-32.1.3
```

---

## 📊 Success Metrics

1. **File Count**: 1 unified guide created, 5 obsolete files deleted
2. **Maintenance Reduction**: 60% less maintenance (1 file vs 4 files)
3. **Size**: INITIALIZATION.md ~25KB (comprehensive, scenario-aware)
4. **Coverage**: All 4 scenarios documented as variations
5. **Validation**: All 4 gates pass
6. **Cross-References**: No broken links in active documentation
7. **User Experience**: Single guide with clear scenario decision tree

---

## 🔗 Related PRPs

- **PRP-32.1.1** (Documentation Audit): Provides IsWorkflow classifications
- **PRP-32.1.2** (Repomix Configuration): Generates ce-infrastructure.xml referenced in guide
- **PRP-32.3.1** (Final Integration): Will reference INITIALIZATION.md in INDEX.md/CLAUDE.md

---

## 📝 Notes

### Critical Path Items

1. **Scenario Decision Tree**: Must be clear and actionable for users
2. **User File Migration**: Phase 2 must document YAML header addition (type: user for memories, source: target-project for PRPs)
3. **Scenario Variations**: Clearly marked within phases (not separate sections)
4. **PRP-32 Naive**: INITIALIZATION.md must NOT reference Batch 32 or PRP-32.x (framework-agnostic)

### PRP-32 Naive Requirement

**Deliverables Must NOT Reference**:
- Batch 32
- PRP-32.x numbers
- Context about "when this was created"
- Implementation details (use generic "framework installation" language)

**Rationale**: Distributed files should be framework-native, not tied to specific development batch.

**Example**:
- ❌ "Created in Batch 32, see PRP-32.1.2 for details"
- ✅ "Framework installation package (ce-infrastructure.xml)"

---

## 🎓 Lessons Learned

1. **Consolidation > Duplication**: Single source of truth reduces drift risk
2. **Scenario Variations**: Better handled as decision points within phases than separate guides
3. **Decision Trees**: Help users quickly identify their scenario without reading all documentation
4. **User File Migration**: Critical detail often overlooked in initialization guides (YAML headers)

---

**Created**: 2025-11-04
**Status**: Ready for execution
**Estimated Time**: 3 hours
