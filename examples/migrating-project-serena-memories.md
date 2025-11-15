# CE 1.1 Migration Planning - Resolved Questions

**Purpose**: Document resolved questions about CE 1.1 framework migration and file organization

**Date**: 2025-11-04

**Status**: ✅ All questions resolved, ready for PRP-32.x updates

---

## Questions & Answers

### Q1: Framework Memory Typing ✅

**Question**: Should all framework memories be `type: critical` or keep the split?

**Answer**: **Keep current split**
- **6 critical memories**: code-style-conventions, suggested-commands, task-completion-checklist, testing-standards, tool-usage-syntropy, use-syntropy-tools-not-bash
- **17 regular memories**: All other framework memories

**Rationale**: Critical memories are essential for correct tool usage and code quality. Regular memories provide supplementary guidance but aren't blocking.

**Implementation**: Update PRP-32.3.1 to maintain 6/17 split in YAML headers.

---

### Q2: ce-32/ Folder Structure ✅

**Question**: Where to organize PRP-32 doc processing, cache, and repomix builds?

**Answer**: **Use ce-32/ folder with 4 subfolders**

```
ce-32/
├── docs/          # Processed documentation (consolidated, refined)
├── cache/         # Cache files (analysis, validation results)
├── builds/        # Repomix package builds (ce-infrastructure.xml, ce-workflow-docs.xml)
└── validation/    # Validation outputs (unpacked packages, file counts)
```

**Integration Point**: During Syntropy MCP initialize tool execution, extract from ce-32/builds/ to target project.

**Cleanup**: ce-32/ directory remains in ctx-eng-plus (development), not distributed to target projects.

---

### Q3: Migration Guide Consolidation ✅

**Question**: Keep 4 separate migration guides or consolidate into one?

**Answer**: **CONSOLIDATE into ONE unified guide** based on file-structure-of-ce-initial.md's 5-phase workflow

**New Structure**:
```
examples/
└── INITIALIZATION.md    # Master guide (replaces 4 separate guides)
    ├── Phase 1: Bucket Collection
    ├── Phase 2: User Files Copy
    ├── Phase 3: Repomix Package Handling
    ├── Phase 4: CLAUDE.md Blending
    └── Phase 5: Legacy Cleanup
```

**Migration Scenarios** (handled as variations within unified guide):
- **Greenfield**: Skip Phase 2 (no user files), full Phase 3 extraction
- **Mature Project**: Full Phase 2 (copy user files), full Phase 3 extraction
- **CE 1.0 Upgrade**: Full Phase 2 (migrate existing CE files), Phase 5 aggressive cleanup
- **Partial Install**: Selective Phase 3 (only missing components)

**Rationale**: Single source of truth, less maintenance, clearer workflow.

**Impact**:
- **DELETE**: examples/workflows/migration-greenfield.md
- **DELETE**: examples/workflows/migration-mature-project.md
- **DELETE**: examples/workflows/migration-existing-ce.md
- **DELETE**: examples/workflows/migration-partial-ce.md
- **CREATE**: examples/INITIALIZATION.md (comprehensive, scenario-aware)

**Implementation**: Update PRP-32.1.3 to reflect ONE unified guide instead of 4 separate guides.

---

### Q4: User Files Migration (Memories + PRPs) ✅

**Question**: How to handle pre-existing user memories/PRPs during migration?

**Answer**: **Add YAML headers during Phase 2 (User Files Copy)**

#### User Memories

**Step 2.1: Classify User Memories**

Scan user memories in staging bucket:
```bash
for file in tmp/syntropy-initialization/serena/*.md; do
  # Check if already has YAML header
  if ! head -1 "$file" | grep -q "^---$"; then
    # Add YAML header for user memory
    cat > "$file.tmp" <<EOF
---
type: user
source: target-project
created: $(date -r "$file" +%Y-%m-%d)
---

$(cat "$file")
EOF
    mv "$file.tmp" "$file"
  fi
done
```

**YAML Header Format** (user memories):
```yaml
---
type: user
source: target-project
created: YYYY-MM-DD
---
```

**Copy to Destination**:
```bash
cp -R tmp/syntropy-initialization/serena/*.md .serena/memories/
```

**Result**:
```
.serena/memories/
├── system/
│   ├── code-style-conventions.md       # type: critical (framework)
│   ├── suggested-commands.md           # type: critical (framework)
│   ├── batch-generation-patterns.md    # type: regular (framework)
│   └── ... (21 more framework memories)
├── custom-team-conventions.md          # type: user (target project)
└── project-api-patterns.md             # type: user (target project)
```

#### User PRPs

**Step 2.2: Update User PRP Headers**

Scan user PRPs in staging bucket:
```bash
for file in tmp/syntropy-initialization/prps/*.md; do
  # Check if already has CE-compatible YAML header
  if ! grep -q "^prp_id:" "$file"; then
    # Extract title from filename (e.g., PRP-12-feature.md → feature)
    title=$(basename "$file" .md | sed 's/^PRP-[0-9]*-//' | tr '-' ' ')

    # Add CE-compatible YAML header
    cat > "$file.tmp" <<EOF
---
prp_id: $(basename "$file" .md | grep -o '^PRP-[0-9]*' || echo "PRP-LEGACY-$(date +%s)")
title: $title
status: executed
created: $(date -r "$file" +%Y-%m-%d)
source: target-project
---

$(cat "$file")
EOF
    mv "$file.tmp" "$file"
  fi
done
```

**YAML Header Format** (user PRPs):
```yaml
---
prp_id: PRP-12
title: Feature name
status: executed
created: YYYY-MM-DD
source: target-project
---
```

**Copy to Destination**:
```bash
cp -R tmp/syntropy-initialization/prps/*.md .ce/PRPs/executed/
```

**Result**:
```
.ce/PRPs/
├── system/
│   └── executed/
│       └── (framework PRPs, if any)
├── executed/
│   ├── PRP-12-user-feature.md       # source: target-project
│   └── PRP-15-bug-fix.md            # source: target-project
└── feature-requests/
    └── PRP-20-new-feature.md        # source: target-project
```

**Rationale**:
- User memories get `type: user` to distinguish from framework (critical/regular)
- User PRPs get CE-compatible headers for tooling compatibility
- Source tracking (`source: target-project`) identifies origin

---

### Q5: Other Buckets Migration ✅

**Question**: Do user examples and commands need metadata migration?

**Answer**: **NO - Only memories + PRPs**

**Rationale**:
- **User examples**: No standardized metadata format, copy as-is
- **User commands**: Slash commands are self-describing, no headers needed
- **Memories + PRPs**: Structured data requiring YAML headers for classification/tooling

**Implementation**: Phase 2 migration only adds YAML headers to memories and PRPs.

---

### Q6: /system/ Organization Clarification ✅

**Question**: What did "at syntropy initialize tool rework" mean?

**Answer**: **/system/ subfolders** as described in file-structure-of-ce-initial.md

**Clarification**:
- `/system/` = subfolders for framework files (`.ce/examples/system/`, `.serena/memories/system/`, `.ce/PRPs/system/`)
- NOT referring to a separate "syntropy initialize tool" rework
- ce-32/builds/ packages already organized with /system/ structure
- Extraction during initialization creates /system/ subfolders automatically

**Implementation**: PRP-32.1.2 ce-infrastructure.xml already includes /system/ organization via post-processing script.

---

## Impact on PRP-32.x

### PRP-32.1.1 (Documentation Audit)
**Status**: ✅ Already updated with system/user classification
**No changes needed**

### PRP-32.1.2 (Repomix Configuration)
**Status**: ✅ Already updated with ce-infrastructure.xml and /system/ organization
**Minor addition**: Document ce-32/builds/ output directory
```yaml
output:
  workflow: ce-32/builds/ce-workflow-docs.xml
  infrastructure: ce-32/builds/ce-infrastructure.xml
```

### PRP-32.1.3 (Migration Guides)
**Status**: ⚠️ MAJOR REVISION REQUIRED
**Changes**:
1. **DELETE** all 4 separate migration guide specifications:
   - migration-greenfield.md
   - migration-mature-project.md
   - migration-existing-ce.md
   - migration-partial-ce.md

2. **CREATE** ONE unified guide specification:
   - examples/INITIALIZATION.md (based on file-structure-of-ce-initial.md)
   - Include scenario variations within single workflow
   - Add Phase 2 details for user file YAML header addition

3. **UPDATE** PRP-0 template:
   - Reference examples/INITIALIZATION.md (not migration-*.md)
   - Remove scenario-specific guide references

4. **UPDATE** migration-integration-summary.md:
   - Single guide instead of 4 guides
   - Update INDEX.md/CLAUDE.md integration tasks

### PRP-32.2.1 (Documentation Refinement)
**Status**: ✅ Already scoped to system docs only
**No changes needed**

### PRP-32.3.1 (Final Integration)
**Status**: ⚠️ MINOR UPDATES REQUIRED
**Changes**:
1. **Add ce-32/ folder usage**:
   - Document processing: ce-32/docs/
   - Cache files: ce-32/cache/
   - Repomix builds: ce-32/builds/
   - Validation: ce-32/validation/

2. **Clarify memory type split**:
   - Keep 6 critical + 17 regular split
   - Document type field values: critical, regular, user

3. **Add user file migration**:
   - Phase 2 includes YAML header addition for user memories/PRPs
   - Document type: user classification for user memories

---

## Summary

**Resolved Questions**: 6/6 ✅

**Next Steps**:
1. Update PRP-32.1.2 (minor: add ce-32/builds/ output)
2. Revise PRP-32.1.3 (major: consolidate to one guide)
3. Update PRP-32.3.1 (minor: add ce-32/ usage, clarify memory types)
4. Execute updated PRPs to finalize CE 1.1 framework

**Key Decisions**:
- Keep 6 critical + 17 regular framework memory split
- Use ce-32/ folder for all PRP-32 processing
- Consolidate 4 migration guides → 1 unified guide
- Add YAML headers to user memories (type: user) and PRPs during Phase 2
- Only migrate memories + PRPs (not examples/commands)
- /system/ = subfolders for framework files (already implemented)

---

**Last Updated**: 2025-11-04
**Status**: Ready for PRP-32.x updates
