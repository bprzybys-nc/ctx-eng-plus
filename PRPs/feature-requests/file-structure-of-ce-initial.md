# CE Framework - File Structure & Initialization Workflow

**Purpose**: Define official CE framework organization and initialization workflow for target projects

**Version**: 1.0 (Draft)

**Date**: 2025-11-04

---

## 1. Official CE Framework Organization

### Directory Structure

```
target-project/
├── .ce/                          # Framework system docs
│   ├── examples/
│   │   ├── system/               # Framework examples (extracted from ce-infrastructure.xml)
│   │   │   ├── *.md              # Framework example files
│   │   │   └── ce-workflow-docs.xml  # Reference package (not extracted)
│   │   └── *.md                  # User project examples (if any)
│   └── PRPs/
│       ├── system/               # Framework PRPs (from ce-infrastructure.xml)
│       │   └── executed/
│       ├── executed/             # User project PRPs (executed)
│       ├── feature-requests/     # User project PRPs (pending)
│       └── archived/             # User project PRPs (archived)
├── .serena/
│   └── memories/
│       ├── system/               # Framework memories (6 critical + 17 regular)
│       └── *.md                  # User project memories (if any)
├── .claude/                      # Commands & configuration
│   ├── commands/                 # 11 framework slash commands
│   └── settings.local.json       # Permissions & config
└── CLAUDE.md                     # Project guide (framework + user, blended)
```

**Key Principles**:
- **System docs** live in `/system/` subfolders (framework-provided, read-only)
- **User docs** live in parent directories (project-specific, editable)
- **Separation** prevents conflicts during framework upgrades
- **CLAUDE.md** is blended (framework sections + user sections, marked)
- **Zero noise** - Legacy organization files deleted after migration (Phase 5 cleanup)

---

## 2. Five Data Layer Model

When Syntropy initialization tools scan target projects, they identify 5 data layers:

### Layer 1: Serena Memories
- **Pattern**: Path contains `.serena/` directory
- **Files**: `*.md` in `.serena/memories/`
- **Destination**: `.serena/memories/system/` (framework) or `.serena/memories/` (user)

### Layer 2: Examples
- **Pattern**: `*.md` where path contains `examples` or `patterns` directory
- **Files**: Documentation, patterns, workflows
- **Destination**: `.ce/examples/system/` (framework) or `.ce/examples/` (user)

### Layer 3: PRPs
- **Pattern**: All `*.md` where path contains `PRPs` (case-insensitive)
- **Files**: PRP documents (executed, feature-requests, archived)
- **Destination**: `.ce/PRPs/system/` (framework) or `.ce/PRPs/` (user)

### Layer 4: CLAUDE.md
- **Pattern**: `CLAUDE.md` in project root (can be symlink)
- **Type**: File
- **Destination**: `CLAUDE.md` (blended framework + user)

### Layer 5: Claude Commands
- **Pattern**: `.claude/` in project root (can be symlink)
- **Type**: Directory containing commands, settings, config
- **Destination**: `.claude/` (framework commands + user commands)

---

## 3. Initialization Workflow

**Goal**: Migrate target project from legacy CE 1.0 (or no CE) to clean CE 1.1 structure with **zero noise**.

**5-Phase Process**:
1. **Bucket Collection** - Stage files for validation
2. **Framework Destination Copy** - Copy validated files to CE 1.1 structure
3. **Repomix Package Handling** - Extract framework packages
4. **CLAUDE.md Blending** - Merge framework + user sections
5. **Legacy Cleanup** - Delete duplicate legacy files → **Zero noise**

**Final State**: Clean project with `.ce/` structure, no legacy `PRPs/` or `examples/` directories.

---

### Phase 1: Bucket Collection (Staging)

**Create staging area**:
```bash
tmp/syntropy-initialization/
├── serena/
├── examples/
├── prps/
├── claude-md/
└── claude-dir/
```

**Step 1.1: Copy to Buckets**
```bash
# Copy files from target project to staging buckets
# Preserve directory organization during copy

# Example:
cp -R /path/to/project/.serena/memories/*.md tmp/syntropy-initialization/serena/
cp -R /path/to/project/examples/*.md tmp/syntropy-initialization/examples/
# ... etc for all 5 layers
```

**Step 1.2: Validate Bucket Contents**

Review files in each bucket to verify they match bucket characteristics:

- **serena bucket**: Must be `.md` files with memory content (YAML headers optional)
- **examples bucket**: Must be `.md` files with example/pattern documentation
- **prps bucket**: Must be `.md` files with PRP structure (YAML headers + sections)
- **claude-md bucket**: Must be `CLAUDE.md` file with project guide content
- **claude-dir bucket**: Must contain `commands/` and/or `settings.local.json`

**Mark non-matching files**:
```bash
# Files that don't match bucket characteristics get `.fake` extension
mv tmp/syntropy-initialization/examples/not-an-example.md \
   tmp/syntropy-initialization/examples/not-an-example.md.fake
```

**Research Task**: Extract optimized characteristics for each bucket by analyzing:
- `nc-src/certinia/`
- `nc-src/mlx-trading/`
- `nc-src/conti-intro/`
- `nc-src/ctx-eng-plus/`

Use KISS principles: simple, robust characteristics.

---

### Phase 2: User Files Copy

**Purpose**: Copy validated USER files from target project to CE 1.1 user directories (not `/system/`).

**Note**: Framework files come from Phase 3 (repomix extraction), not Phase 2.

**Step 2.1: Copy Non-Fake Files**

Copy validated (non-`.fake`) USER files from buckets to CE user destinations:

```bash
# Bucket 1: Serena
cp -R tmp/syntropy-initialization/serena/*.md .serena/memories/

# Bucket 2: Examples
cp -R tmp/syntropy-initialization/examples/*.md .ce/examples/

# Bucket 3: PRPs
cp -R tmp/syntropy-initialization/prps/*.md .ce/PRPs/

# Bucket 4: CLAUDE.md (special handling - see Phase 3)
# Bucket 5: Claude Dir
cp -R tmp/syntropy-initialization/claude-dir/* .claude/
```

**Preserve directory organization** from staging area.

---

### Phase 3: Repomix Package Handling

**Step 3.1: Copy ce-workflow-docs.xml**

```bash
# Create system directory if needed
mkdir -p .ce/examples/system/

# Copy ONLY the workflow documentation package XML file to system folder
cp ce-workflow-docs.xml .ce/examples/system/

# Notify in CLAUDE.md (lowercase "repomix xml", not caps)
echo "Framework workflow docs available at .ce/examples/system/ce-workflow-docs.xml (repomix xml)" >> CLAUDE.md
```

**Note**:
- `ce-workflow-docs.xml` is stored as-is (XML file) for reference/distribution
- The actual framework files (examples, PRPs, memories) are extracted from `ce-infrastructure.xml`
- Both packages serve different purposes:
  - `ce-workflow-docs.xml` = Lightweight workflow examples package (reference only)
  - `ce-infrastructure.xml` = Complete framework with `/system/` organization (extracted)

**Step 3.2: Extract ce-infrastructure.xml**

```bash
# Extract infrastructure package to root
# Package already organized with /system/ subfolders
repomix --unpack ce-infrastructure.xml --target ./

# Creates:
# - .ce/PRPs/system/          (framework PRPs)
# - .ce/examples/system/      (framework examples)
# - .serena/memories/system/  (framework memories)
# - CLAUDE.md                 (framework sections)
# - .claude/                  (framework commands)
```

**Important**: `ce-infrastructure.xml` must be organized with:
- `.ce/PRPs/system/` - Framework PRPs
- `.ce/examples/system/` - Framework examples
- `.serena/memories/system/` - Framework memories (6 critical + 17 regular)

While these remain at root:
- `CLAUDE.md` → `CLAUDE.md`
- `.claude/` → `.claude/`

---

### Phase 4: CLAUDE.md Blending

**Step 4.1: Backup Existing CLAUDE.md**

```bash
# Backup user's existing CLAUDE.md
cp CLAUDE.md CLAUDE.md.backup-$(date +%Y%m%d-%H%M%S)
```

**Step 4.2: Blend Framework + User Sections**

```bash
# Merge framework CLAUDE.md sections with user sections
# Mark sections: [FRAMEWORK] vs [PROJECT]

# Example structure:
# ## [FRAMEWORK] Communication
# ## [PROJECT] Project-Specific Commands
# ## [FRAMEWORK] Core Principles
# ## [PROJECT] Team Conventions
```

**Step 4.3: Denoise Blended CLAUDE.md**

```bash
# Run denoise command to clean up redundancies
/denoise CLAUDE.md

# Output: Denoised CLAUDE.md with no duplicate sections
```

---

### Phase 5: Legacy Organization Cleanup

**Purpose**: Remove files from legacy CE 1.0 organization after successful migration to CE 1.1 structure.

**Step 5.1: Verify Migration Completed**

```bash
# Verify all files copied to new CE 1.1 structure
test -d .ce/PRPs/system && echo "✓ System PRPs migrated"
test -d .ce/examples/system && echo "✓ System examples migrated"
test -d .serena/memories/system && echo "✓ System memories migrated"

# Check initialization report for any errors
cat tmp/syntropy-initialization/report.txt | grep -i error
# Expected: No errors
```

**Step 5.2: Archive Legacy Organization**

```bash
# Create archive of legacy files before deletion (safety backup)
mkdir -p tmp/syntropy-initialization/legacy-backup/
tar -czf tmp/syntropy-initialization/legacy-backup/pre-ce-1.1-$(date +%Y%m%d-%H%M%S).tar.gz \
  PRPs/ \
  examples/ \
  .serena/memories/*.md \
  2>/dev/null || true

echo "✓ Legacy files archived"
```

**Step 5.3: Delete Legacy Organization Files**

```bash
# Delete legacy PRPs directory (now in .ce/PRPs/)
if [ -d PRPs/ ]; then
  rm -rf PRPs/
  echo "✓ Deleted legacy PRPs/"
fi

# Delete legacy examples directory (now in .ce/examples/)
if [ -d examples/ ]; then
  rm -rf examples/
  echo "✓ Deleted legacy examples/"
fi

# Delete legacy .serena/memories/*.md (now in .serena/memories/system/)
# Keep user memories (non-system)
if [ -d .serena/memories/ ]; then
  # Only delete files that were migrated to /system/
  # User memories (not in system/) are preserved
  find .serena/memories/ -maxdepth 1 -name "*.md" -type f | while read file; do
    basename=$(basename "$file")
    if [ -f .serena/memories/system/"$basename" ]; then
      rm -f "$file"
      echo "✓ Deleted legacy .serena/memories/$basename (migrated to system/)"
    fi
  done
fi
```

**Step 5.4: Log Cleanup Summary**

```bash
# Log cleanup actions to initialization report
cat >> tmp/syntropy-initialization/report.txt <<EOF

## Legacy Organization Cleanup

Deleted legacy CE 1.0 organization files:
- PRPs/ → Migrated to .ce/PRPs/
- examples/ → Migrated to .ce/examples/
- .serena/memories/*.md → Migrated to .serena/memories/system/

Backup created: tmp/syntropy-initialization/legacy-backup/pre-ce-1.1-*.tar.gz

CE 1.1 structure fully migrated.
EOF

echo "✓ Cleanup complete - CE 1.1 structure active"
```

**Safety Notes**:

- **Archive created**: Legacy files backed up to `tmp/syntropy-initialization/legacy-backup/` before deletion
- **Verification required**: Step 5.1 validates migration succeeded before any deletions
- **User files preserved**: Only legacy files that were migrated to `/system/` are deleted
- **Rollback possible**: Backup tarball can restore legacy organization if needed

**Rollback Procedure** (if needed):

```bash
# Extract backup to restore legacy organization
cd /path/to/project
tar -xzf tmp/syntropy-initialization/legacy-backup/pre-ce-1.1-*.tar.gz

# Remove CE 1.1 structure
rm -rf .ce/

echo "✓ Rolled back to legacy CE 1.0 organization"
```

---

## 4. Validation Checklist

After initialization (including Phase 5 cleanup), validate:

```bash
# Check CE 1.1 structure exists
test -d .ce/examples/system && echo "✓ System examples"
test -d .ce/PRPs/system && echo "✓ System PRPs"
test -d .serena/memories/system && echo "✓ System memories"

# Check framework packages
test -f .ce/examples/system/ce-workflow-docs.xml && echo "✓ Workflow package"

# Check commands installed
test -d .claude/commands && echo "✓ Commands directory"
ls .claude/commands/*.md | wc -l  # Expected: 11 framework commands

# Check CLAUDE.md blended
grep -q "\[FRAMEWORK\]" CLAUDE.md && echo "✓ CLAUDE.md blended"

# Check memories loaded
serena_list_memories | grep -c "system/" # Expected: 23 system memories

# ===== VERIFY NO LEGACY FILES (NO NOISE) =====

# Verify legacy directories deleted (should not exist)
! test -d PRPs && echo "✓ Legacy PRPs/ removed" || echo "✗ WARNING: Legacy PRPs/ still exists"
! test -d examples && echo "✓ Legacy examples/ removed" || echo "✗ WARNING: Legacy examples/ still exists"

# Verify legacy memories migrated (only user memories remain at root level)
LEGACY_SYSTEM_MEMORIES=$(find .serena/memories/ -maxdepth 1 -name "*.md" -type f | while read f; do
  basename=$(basename "$f")
  test -f .serena/memories/system/"$basename" && echo "$f"
done | wc -l)
test "$LEGACY_SYSTEM_MEMORIES" -eq 0 && echo "✓ No duplicate system memories" || echo "✗ WARNING: $LEGACY_SYSTEM_MEMORIES duplicate system memories found"

# Verify backup created
test -f tmp/syntropy-initialization/legacy-backup/pre-ce-1.1-*.tar.gz && echo "✓ Legacy backup exists" || echo "⚠ No legacy backup (may be fresh install)"

# Final check: Clean project (no noise)
echo ""
echo "=== Project Cleanliness Check ==="
test ! -d PRPs && test ! -d examples && echo "✅ Project is clean - no legacy noise" || echo "❌ Project has legacy noise - cleanup failed"
```

---

## 5. Key Design Decisions

### System vs User Separation

**Rationale**: Prevents conflicts during framework upgrades.

- **System docs** (`.../system/`): Framework-provided, read-only, upgraded atomically
- **User docs** (parent dir): Project-specific, editable, preserved during upgrades

**Example Conflict Scenario**:
```
# Before separation (conflicts possible):
.serena/memories/
├── code-style-conventions.md     # Framework memory
└── code-style-conventions.md     # User memory (CONFLICT!)

# After separation (no conflicts):
.serena/memories/
├── system/
│   └── code-style-conventions.md  # Framework memory
└── code-style-conventions.md      # User memory (no conflict)
```

### Bucket Validation (`.fake` Extension)

**Rationale**: Prevents copying non-CE files to framework destinations.

**Example**:
```bash
# File in examples/ that's not actually an example
tmp/syntropy-initialization/examples/random-notes.md

# After validation:
tmp/syntropy-initialization/examples/random-notes.md.fake

# Result: Not copied to .ce/examples/
```

### CLAUDE.md Blending

**Rationale**: Single source of truth for project guide, clearly marked sections.

**Format**:
```markdown
# [FRAMEWORK] Communication
Direct, token-efficient. No fluff.

# [PROJECT] Project-Specific Communication
Use Slack for urgent issues, email for updates.

# [FRAMEWORK] Core Principles
- Syntropy MCP First
- No Fishy Fallbacks
```

---

## 6. Design Decisions (Resolved)

### 1. Bucket Validation Characteristics ✅

**Approach**: Analyze existing CE projects to extract KISS heuristics for each bucket.

**Projects to Analyze**:
- `nc-src/certinia/`
- `nc-src/mlx-trading-pipeline-context-engineering/`
- `nc-src/conti-intro/`
- `nc-src/ctx-eng-plus/`

**Extract Common Patterns**:
- **Serena bucket**: Files in `.serena/memories/*.md` with YAML headers (optional) and memory-like content
- **Examples bucket**: Files in `examples/` or `patterns/` directories with documentation structure
- **PRPs bucket**: Files in `PRPs/` with PRP-ID pattern in filename or YAML header

**Implementation**: Research task in initialization workflow to validate bucket contents using extracted heuristics.

### 2. Symlink Handling ✅

**Decision**: **Follow symlink and copy target content**

**Rationale**: Ensures framework files are actually copied to target project, not just symlink references.

**Implementation**:
```bash
# For symlinked .claude/ directory
cp -RL /path/to/.claude/ target/.claude/

# For symlinked CLAUDE.md file
cp -L /path/to/CLAUDE.md target/CLAUDE.md
```

**Note**: `-L` flag follows symlinks and copies the actual file content.

### 3. Conflict Resolution ✅

**Decision**: **Suffix conflicting framework files with `-ce-system` and report**

**Rationale**: Preserves both user and framework files, explicit conflict resolution logged.

**Implementation**:
```bash
# If .ce/examples/system/pattern-foo.md already exists
# Framework file becomes: .ce/examples/system/pattern-foo-ce-system.md

# Include in initialization report:
echo "CONFLICT: .ce/examples/system/pattern-foo.md existed, framework version saved as pattern-foo-ce-system.md" >> tmp/syntropy-initialization/report.txt
```

**User Action Required**: Review conflicts in initialization report and manually merge if needed.

### 4. Version Compatibility ✅

**Decision**: **No migration guide or backward compatibility**

**Approach**: Simply update version numbers where needed

**Rationale**: CE 1.1 is breaking change, users adopt new structure explicitly

**Implementation**:
- Update version in YAML headers: `ce_version: "1.1"`
- Update version in CLAUDE.md: `**CE Version**: 1.1`
- Update version in repomix manifest: `"framework_version": "1.1"`

**No Upgrade Path**: CE 1.0 → CE 1.1 requires fresh initialization (not in-place upgrade)

---

## 7. Related Documentation Needed

### Doc 1: CE Framework Organization Guide

**Path**: `examples/ce-framework-organization.md`

**Content**:
- Directory structure diagram
- System vs user docs explanation
- File naming conventions
- Location lookup table (where to find what)
- Upgrade process (how system docs get updated)

### Doc 2: Initialization Workflow Guide

**Path**: `examples/workflows/initialization-workflow.md`

**Content**:
- Step-by-step initialization process
- Bucket validation examples
- CLAUDE.md blending examples
- Troubleshooting common issues
- Validation commands with expected outputs

---

## 8. Impact on PRP-32.x

This design affects:

- **PRP-32.1.1** (Documentation Audit): Must classify docs as system vs user
- **PRP-32.1.2** (Repomix Configuration): Must organize ce-infrastructure.xml with `/system/` subfolders
- **PRP-32.1.3** (Migration Guide): Must document this initialization workflow
- **PRP-32.2.1** (Documentation Refinement): System docs consolidation
- **PRP-32.3.1** (Final Integration): Regenerate repomix with new organization

**Recommendation**: Update PRP-32.x after finalizing this design doc.
