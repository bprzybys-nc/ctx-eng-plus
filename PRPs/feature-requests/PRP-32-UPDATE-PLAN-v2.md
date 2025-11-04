# PRP-32.x Update Plan v2

**Purpose**: Detailed plan for updating PRP-32.x files based on resolved questions in migrating-project-serena-memories.md

**Date**: 2025-11-04

**Status**: Ready for execution

---

## Overview

Based on resolved questions, 3 out of 5 PRP-32.x files require updates:
- **PRP-32.1.1**: ✅ No changes needed
- **PRP-32.1.2**: ⚠️ Minor update (ce-32/builds/ output)
- **PRP-32.1.3**: 🔴 MAJOR revision (consolidate 4 guides → 1)
- **PRP-32.2.1**: ✅ No changes needed
- **PRP-32.3.1**: ⚠️ Minor updates (ce-32/ folder, memory types, user migration)

---

## Session 1: PRP-32.1.2 Minor Update (5 minutes)

### Changes Required

**File**: `PRPs/feature-requests/PRP-32.1.2-repomix-configuration-profile-creation.md`

**Change 1: Add ce-32/builds/ Output Directory**

**Location**: After line 369 (Step 3.3: Check Token Counts)

**Add new section**:
```markdown
**Step 3.4: Move Packages to ce-32/builds/**

```bash
# Create builds directory
mkdir -p ce-32/builds/

# Move generated packages to builds folder
mv .ce/ce-workflow-docs.xml ce-32/builds/
mv .ce/ce-infrastructure.xml ce-32/builds/

echo "✓ Packages moved to ce-32/builds/"
```

**Purpose**: Centralize repomix builds in ce-32/ folder for PRP-32 processing

**Note**: ce-32/ is ctx-eng-plus development artifact, not distributed to target projects
```

**Change 2: Update Validation Commands**

**Location**: Lines 654-663 (Step 4.4: Check Token Counts)

**OLD**:
```bash
# Workflow package (expect <60KB)
wc -c /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-workflow-docs.xml

# Infrastructure package (expect <150KB)
wc -c /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/ce-infrastructure.xml
```

**NEW**:
```bash
# Workflow package (expect <60KB)
wc -c /Users/bprzybyszi/nc-src/ctx-eng-plus/ce-32/builds/ce-workflow-docs.xml

# Infrastructure package (expect <150KB)
wc -c /Users/bprzybyszi/nc-src/ctx-eng-plus/ce-32/builds/ce-infrastructure.xml
```

**Change 3: Update Success Criteria**

**Location**: Lines 1090-1096 (Success Criteria section)

**Add to checklist**:
```markdown
- [ ] Packages moved to ce-32/builds/
  - ce-32/builds/ce-workflow-docs.xml
  - ce-32/builds/ce-infrastructure.xml
```

### Validation

After changes:
```bash
# Verify ce-32/builds/ references added
grep -n "ce-32/builds/" PRPs/feature-requests/PRP-32.1.2-repomix-configuration-profile-creation.md
# Expected: 3-5 occurrences
```

---

## Session 2: PRP-32.1.3 MAJOR Revision (60 minutes)

### Overview

**Goal**: Replace 4 separate migration guides with ONE unified guide based on file-structure-of-ce-initial.md

**Key Changes**:
1. Delete specifications for 4 separate guides (migration-greenfield.md, etc.)
2. Create specification for ONE unified guide (examples/INITIALIZATION.md)
3. Update PRP-0 template specification
4. Delete migration-integration-summary.md (replaced by unified guide)

### Changes Required

**File**: `PRPs/feature-requests/PRP-32.1.3-migration-guides-completion.md`

**Change 1: Update TL;DR Section (lines 17-30)**

**OLD**:
```markdown
**What**: Create 3 missing migration/initialization files to complete CE 1.1 documentation set

**Why**: PRP-32 Batch 1 created greenfield/mature-project/existing-ce guides, but 2 files are missing:
1. `migration-partial-ce.md` - 4th migration scenario (incomplete CE installation)
2. `PRP-0-CONTEXT-ENGINEERING.md` - Template for documenting CE installation
3. `migration-integration-summary.md` - Planning doc for Phase 5 INDEX.md/CLAUDE.md integration
```

**NEW**:
```markdown
**What**: Create unified CE 1.1 initialization guide and PRP-0 template

**Why**: Replace 4 separate migration guides with ONE comprehensive guide based on 5-phase workflow from file-structure-of-ce-initial.md. Reduces maintenance burden, provides single source of truth.

**Deliverables**:
1. `examples/INITIALIZATION.md` - Unified initialization guide (replaces 4 separate guides)
2. `examples/templates/PRP-0-CONTEXT-ENGINEERING.md` - CE installation documentation template
3. Delete 4 existing migration guides (greenfield, mature-project, existing-ce, partial-ce)
```

**Change 2: Replace Files to Create Section (lines 32-69)**

**Delete entire section "Files to Create"**

**Replace with**:
```markdown
## Files to Create/Update

### File 1: examples/INITIALIZATION.md (NEW - Primary Deliverable)

**Purpose**: Comprehensive CE 1.1 framework initialization guide using 5-phase workflow

**Size**: ~25KB (comprehensive, scenario-aware)

**Structure**:
```markdown
# CE 1.1 Framework Initialization Guide

## Overview
- CE 1.1 architecture (/system/ organization)
- 5-phase workflow summary
- Migration scenario decision tree

## Phase 1: Bucket Collection (5-10 min)
- Staging area setup (tmp/syntropy-initialization/)
- Copy files to buckets (serena, examples, prps, claude-md, claude-dir)
- Validate bucket contents (mark .fake files)
- Bucket characteristics (KISS heuristics)

## Phase 2: User Files Copy (10-15 min)
### Step 2.1: User Memory Migration
- Add YAML headers (type: user)
- Preserve directory structure
- Example: User memory with header

### Step 2.2: User PRP Migration
- Add CE-compatible YAML headers
- Extract metadata from filenames
- Example: User PRP with header

### Step 2.3: Copy Validated Files
- Copy non-.fake files to CE 1.1 destinations
- .serena/memories/ (user memories)
- .ce/PRPs/executed/ (user PRPs)
- .ce/examples/ (user examples)
- .claude/ (user commands/config)

**Scenario Variations**:
- **Greenfield**: Skip Phase 2 (no user files)
- **Mature Project**: Full Phase 2 (all buckets)
- **CE 1.0 Upgrade**: Full Phase 2 + validate existing CE structure
- **Partial Install**: Selective Phase 2 (only missing buckets)

## Phase 3: Repomix Package Handling (5 min)
### Step 3.1: Copy Workflow Package
- ce-workflow-docs.xml → .ce/examples/system/ (reference only)

### Step 3.2: Extract Infrastructure Package
- ce-infrastructure.xml extraction
- Creates /system/ subfolders automatically
- Framework file destinations

## Phase 4: CLAUDE.md Blending (10 min)
- Backup existing CLAUDE.md
- Merge framework + user sections
- Mark sections: [FRAMEWORK] vs [PROJECT]
- Denoise blended CLAUDE.md

## Phase 5: Legacy Cleanup (5 min)
- Verify migration completed
- Archive legacy organization (backup)
- Delete legacy files (PRPs/, examples/, duplicate memories)
- Log cleanup summary
- Zero noise verification

## Validation Checklist
- CE 1.1 structure verification
- File count checks (21 examples, 23 memories, 11 commands)
- Legacy file deletion confirmation
- No duplicate system memories
- Backup created

## Troubleshooting
- Common issues during each phase
- Rollback procedure
- Conflict resolution

## Appendix: Scenario Decision Tree
```
START
├─ Has existing CE components?
│  ├─ NO → Greenfield (10 min)
│  └─ YES
│     ├─ CE 1.0 structure? → CE 1.0 Upgrade (40 min)
│     ├─ Incomplete CE? → Partial Install (15 min)
│     └─ No CE, has project docs? → Mature Project (45 min)
```
```
```

**Key Features**:
- **Single workflow**: All scenarios handled as variations
- **User file migration**: Phase 2 includes YAML header addition
- **Scenario branches**: Decision points within phases
- **Complete examples**: Bash scripts with real commands
- **Zero noise guarantee**: Phase 5 cleanup verification

### File 2: examples/templates/PRP-0-CONTEXT-ENGINEERING.md (UPDATE)

**Purpose**: Update PRP-0 template to reference unified guide

**Changes**:
1. Remove references to migration-*.md files
2. Update "Migration Guides" section to reference INITIALIZATION.md only
3. Update "Next Steps" to use unified guide

**Location**: Lines 221-224

**OLD**:
```markdown
**Migration Guides**:
- `examples/INITIALIZATION.md` - Master initialization guide
- `examples/workflows/migration-{scenario}.md` - Scenario-specific guides
```

**NEW**:
```markdown
**Migration Guide**:
- `examples/INITIALIZATION.md` - Complete CE 1.1 initialization guide (5-phase workflow)
```

### File 3: Delete Existing Migration Guides

**Action**: Delete 4 files created in original PRP-32.1.3

```bash
rm examples/workflows/migration-greenfield.md
rm examples/workflows/migration-mature-project.md
rm examples/workflows/migration-existing-ce.md
rm examples/workflows/migration-partial-ce.md
```

**Rationale**: Replaced by examples/INITIALIZATION.md unified guide

### File 4: Delete migration-integration-summary.md

**Action**: Delete planning document (no longer needed)

```bash
rm examples/migration-integration-summary.md
```

**Rationale**: Phase 5 integration tasks now documented in INITIALIZATION.md

**Change 3: Update Implementation Section (lines 71+)**

**Replace entire "Implementation" section** with:

```markdown
## Implementation

### Step 1: Create examples/INITIALIZATION.md (45 minutes)

**Content source**: PRPs/feature-requests/file-structure-of-ce-initial.md (5-phase workflow)

**Enhancements**:
1. Add scenario decision tree at beginning
2. Expand Phase 2 with user file migration (YAML headers for memories/PRPs)
3. Add validation commands for each phase
4. Include troubleshooting section
5. Add rollback procedure

**File size target**: ~25KB

**Validation**:
```bash
# Check file created
test -f examples/INITIALIZATION.md && echo "✓ INITIALIZATION.md created"

# Check size (~25KB)
wc -c examples/INITIALIZATION.md

# Verify 5 phase sections exist
grep "^## Phase [1-5]:" examples/INITIALIZATION.md | wc -l
# Expected: 5
```

### Step 2: Update PRP-0 Template (5 minutes)

**File**: `examples/templates/PRP-0-CONTEXT-ENGINEERING.md`

**Changes**:
1. Update "Migration Guides" section (line 221)
2. Remove scenario-specific references
3. Reference INITIALIZATION.md only

### Step 3: Delete Obsolete Files (2 minutes)

```bash
# Delete 4 separate migration guides
rm examples/workflows/migration-greenfield.md
rm examples/workflows/migration-mature-project.md
rm examples/workflows/migration-existing-ce.md
rm examples/workflows/migration-partial-ce.md

# Delete planning document
rm examples/migration-integration-summary.md

echo "✓ Obsolete files deleted"
```

### Step 4: Update Cross-References (5 minutes)

**Files to check**:
- `examples/INDEX.md` (if exists)
- `CLAUDE.md` (if references migration guides)
- Other PRP-32.x files

**Search and replace**:
```bash
# Find any references to deleted guides
grep -r "migration-greenfield\|migration-mature-project\|migration-existing-ce\|migration-partial-ce" \
  examples/ PRPs/ CLAUDE.md 2>/dev/null

# Update to reference INITIALIZATION.md instead
```

### Step 5: Validate Integration (3 minutes)

```bash
# Verify INITIALIZATION.md exists
test -f examples/INITIALIZATION.md && echo "✓ Unified guide created"

# Verify obsolete files deleted
! test -f examples/workflows/migration-greenfield.md && echo "✓ Old guides deleted"

# Verify PRP-0 template updated
grep "INITIALIZATION.md" examples/templates/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ PRP-0 template updated"

# Check for broken references
grep -r "migration-.*\.md" examples/ PRPs/ | grep -v "INITIALIZATION.md"
# Expected: No matches (or only historical references in executed PRPs)
```
```

**Change 4: Update Success Criteria (lines 400+)**

**OLD**:
```markdown
- [ ] All 4 migration scenarios documented and tested
- [ ] migration-partial-ce.md complete (9.1KB)
- [ ] PRP-0 template complete with all placeholders defined
- [ ] migration-integration-summary.md complete (11KB)
```

**NEW**:
```markdown
- [ ] examples/INITIALIZATION.md created (~25KB)
- [ ] 5-phase workflow documented with scenario variations
- [ ] User file migration (YAML headers) documented in Phase 2
- [ ] PRP-0 template updated to reference INITIALIZATION.md
- [ ] 4 obsolete migration guides deleted
- [ ] migration-integration-summary.md deleted
- [ ] No broken cross-references to deleted files
```

### Validation

After changes:
```bash
# Verify unified guide approach documented
grep -n "INITIALIZATION.md" PRPs/feature-requests/PRP-32.1.3-migration-guides-completion.md
# Expected: 10+ occurrences

# Verify obsolete files deletion documented
grep -n "rm examples/workflows/migration" PRPs/feature-requests/PRP-32.1.3-migration-guides-completion.md
# Expected: 1+ occurrences
```

---

## Session 3: PRP-32.3.1 Minor Updates (15 minutes)

### Changes Required

**File**: `PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md`

**Change 1: Add ce-32/ Folder Documentation**

**Location**: After line 114 (Phase 1 section)

**Add new section**:
```markdown
### Phase 0: Setup ce-32/ Working Directory (2 minutes)

**Purpose**: Create organized workspace for PRP-32 processing, cache, and builds

**Step 0.1: Create ce-32/ Structure**

```bash
# Create ce-32/ directory structure
mkdir -p ce-32/{docs,cache,builds,validation}

# Verify structure
tree -L 1 ce-32/
# Expected:
# ce-32/
# ├── docs/        (processed documentation)
# ├── cache/       (analysis, validation results)
# ├── builds/      (repomix packages)
# └── validation/  (unpacked packages, file counts)
```

**Step 0.2: Initialize Build Manifest**

```bash
cat > ce-32/builds/manifest.txt <<EOF
# CE 1.1 Repomix Packages
# Generated: $(date)
# Batch: 32

Packages:
- ce-workflow-docs.xml (target: <60KB)
- ce-infrastructure.xml (target: <150KB)

Total target: <210KB
EOF

echo "✓ ce-32/ workspace initialized"
```

**Note**: ce-32/ is ctx-eng-plus development artifact, not distributed to target projects

**Output**: Organized workspace for all PRP-32 operations
```

**Change 2: Update Phase 5 Repomix Generation**

**Location**: Lines 316-414 (Phase 5 section)

**Find and update** "Step 5.2: Regenerate Infrastructure Package with /system/ Structure"

**Add** after package generation (around line 340):
```bash
# Generate infrastructure package
npx repomix --config .ce/repomix-profile-infrastructure.yml

# Run post-processing to add /system/ organization
bash .ce/reorganize-infrastructure.sh

# Move packages to ce-32/builds/
mkdir -p ce-32/builds/
mv .ce/ce-workflow-docs.xml ce-32/builds/
mv .ce/ce-infrastructure.xml ce-32/builds/

echo "✓ Packages moved to ce-32/builds/"
```

**Change 3: Add Memory Type Clarification**

**Location**: Lines 58-68 (Proposed Changes section)

**OLD**:
```markdown
**Memory Files** (23 files in `.serena/memories/`):
- Implement memory type system (YAML headers for all 23 memories)
```

**NEW**:
```markdown
**Memory Files** (23 files in `.serena/memories/`):
- Implement memory type system (YAML headers for all 23 memories)
  - **6 critical**: code-style-conventions, suggested-commands, task-completion-checklist, testing-standards, tool-usage-syntropy, use-syntropy-tools-not-bash
  - **17 regular**: All other framework memories
- Add migration support for user memories (type: user) in target projects
```

**Change 4: Add User File Migration Documentation**

**Location**: After line 164 (Phase 2 section)

**Add new subsection**:
```markdown
### Phase 2.5: User File Migration Preparation (5 minutes)

**Purpose**: Document user file migration process for target projects during initialization

**Step 2.5.1: Document User Memory Migration**

User memories in target projects need YAML headers during Phase 2 of initialization:

```bash
# Example: Add YAML header to user memory
cat > user-memory-example.md <<'EOF'
---
type: user
source: target-project
created: 2025-11-04
---

# Custom Team Conventions

Project-specific conventions for team...
EOF
```

**Step 2.5.2: Document User PRP Migration**

User PRPs in target projects need CE-compatible headers:

```bash
# Example: Add YAML header to user PRP
cat > user-prp-example.md <<'EOF'
---
prp_id: PRP-12
title: User Feature Implementation
status: executed
created: 2025-11-04
source: target-project
---

# PRP-12: User Feature Implementation

User-specific PRP content...
EOF
```

**Reference**: See examples/INITIALIZATION.md Phase 2 for complete user file migration workflow

**Output**: User file migration documented for target project initialization
```

**Change 5: Update CHANGELOG.md Template**

**Location**: Lines 516-577 (CHANGELOG.md section)

**Find** "### Changed" section and **update**:

**OLD**:
```markdown
### Changed

**Directory Structure**
- Framework files moved to `/system/` subfolders (`.ce/examples/system/`, `.serena/memories/system/`)
- User files remain in parent directories (`.ce/examples/`, `.serena/memories/`)
```

**NEW**:
```markdown
### Changed

**Directory Structure**
- Framework files moved to `/system/` subfolders (`.ce/examples/system/`, `.serena/memories/system/`)
- User files remain in parent directories (`.ce/examples/`, `.serena/memories/`)
- Development artifacts organized in `ce-32/` (docs, cache, builds, validation)

**Memory Type System**
- Framework memories: 6 critical + 17 regular (YAML type headers)
- User memories: type: user (added during target project initialization)

**User File Migration**
- YAML headers added to user memories during Phase 2 (type: user)
- CE-compatible headers added to user PRPs (source: target-project)
- Only memories + PRPs migrated (examples/commands copied as-is)
```

**Change 6: Update Success Criteria**

**Location**: Lines 460-480 (Success Criteria)

**Add to checklist**:
```markdown
- [ ] ce-32/ folder structure documented (docs, cache, builds, validation)
- [ ] Phase 0 ce-32/ setup documented
- [ ] Repomix packages moved to ce-32/builds/
- [ ] Memory type split clarified (6 critical + 17 regular + user)
- [ ] User file migration documented (YAML headers for memories/PRPs)
```

### Validation

After changes:
```bash
# Verify ce-32/ references added
grep -n "ce-32/" PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md
# Expected: 15+ occurrences

# Verify memory type split documented
grep -n "6 critical.*17 regular\|17 regular.*6 critical" PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md
# Expected: 3+ occurrences

# Verify user file migration documented
grep -n "type: user" PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md
# Expected: 5+ occurrences
```

---

## Execution Order

Execute sessions sequentially:

1. **Session 1**: PRP-32.1.2 update (5 min) - Quick wins, no dependencies
2. **Session 2**: PRP-32.1.3 revision (60 min) - Major change, creates INITIALIZATION.md
3. **Session 3**: PRP-32.3.1 updates (15 min) - References INITIALIZATION.md from Session 2

**Total Time**: ~80 minutes

---

## Validation Checklist

After all sessions:

```bash
# Session 1 validation
grep "ce-32/builds/" PRPs/feature-requests/PRP-32.1.2-repomix-configuration-profile-creation.md
# Expected: 3-5 matches

# Session 2 validation
grep "INITIALIZATION.md" PRPs/feature-requests/PRP-32.1.3-migration-guides-completion.md
# Expected: 10+ matches

grep "rm examples/workflows/migration" PRPs/feature-requests/PRP-32.1.3-migration-guides-completion.md
# Expected: 1+ matches

# Session 3 validation
grep "ce-32/" PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md
# Expected: 15+ matches

grep "type: user" PRPs/feature-requests/PRP-32.3.1-memory-type-system-final-integration.md
# Expected: 5+ matches

# Cross-PRP validation
grep -h "21.*examples\|23.*memories\|11.*commands" PRPs/feature-requests/PRP-32.*.md | sort -u
# Expected: Consistent file counts across all PRPs
```

---

## Success Criteria

- [ ] PRP-32.1.2 updated with ce-32/builds/ references
- [ ] PRP-32.1.3 revised with unified INITIALIZATION.md approach
- [ ] PRP-32.3.1 updated with ce-32/ folder, memory types, user migration
- [ ] All cross-references validated (no broken links)
- [ ] File counts consistent (21/23/11) across all PRPs
- [ ] Token targets consistent (<60KB/<150KB/<210KB) across all PRPs
- [ ] User file migration documented (YAML headers for memories/PRPs)
- [ ] /system/ organization consistent across all PRPs

---

## Next Steps After Update

1. Execute PRP-32.1.2 (generate repomix packages to ce-32/builds/)
2. Execute PRP-32.1.3 (create examples/INITIALIZATION.md, delete obsolete guides)
3. Execute PRP-32.3.1 (add memory type headers, final integration)
4. Validate CE 1.1 framework complete (all packages in ce-32/builds/)
5. Test initialization workflow on sample target project

---

**Created**: 2025-11-04
**Based on**: migrating-project-serena-memories.md (resolved questions)
**Status**: Ready for execution
