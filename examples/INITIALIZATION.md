# CE 1.1 Framework Initialization Guide

**Purpose**: Complete guide for installing and configuring the Context Engineering (CE) 1.1 framework across all project scenarios

**Version**: 1.1

**Last Updated**: 2025-11-04

---

## Overview

This guide covers the complete process of installing the Context Engineering framework into target projects using a unified 5-phase workflow. The process adapts to your specific scenario while maintaining consistent structure and validation.

### What is CE 1.1?

Context Engineering is a framework for managing project context, documentation, and workflows through:

- **Structured knowledge base** (Serena memories)
- **Automated workflows** (slash commands)
- **PRP-based development** (Plan-Review-Produce pattern)
- **Tool integration** (Syntropy MCP, Linear, UV)
- **System/user separation** (framework vs project docs)

### Key Benefits

- **Zero noise**: Clean separation of framework and project files
- **Consistent validation**: Multi-level validation gates
- **Automated workflows**: 11 framework commands for common tasks
- **Knowledge persistence**: 23 framework memories + your project memories
- **Easy upgrades**: System docs updated independently

---

## Quick Start: Choose Your Scenario

Use this decision tree to identify your installation scenario:

```
START: What's your project's current state?
│
├─ NO CE components exist
│  │
│  ├─ New project (empty or minimal code)
│  │  └─→ SCENARIO 1: Greenfield (~10 min)
│  │
│  └─ Existing codebase with working code
│     └─→ SCENARIO 2: Mature Project (~45 min)
│
└─ Has CE components
   │
   ├─ Has .ce/ directory (CE 1.1)
   │  └─→ SCENARIO 4: Partial Install (~15 min)
   │
   └─ No .ce/ directory (CE 1.0 or legacy)
      └─→ SCENARIO 3: CE 1.0 Upgrade (~40 min)
```

### Scenario Descriptions

| Scenario | When to Use | Phases | Time |
|----------|-------------|--------|------|
| **Greenfield** | New project, no CE components | 1, 3, 4 (skip 2, 5) | 10 min |
| **Mature Project** | Existing code, no CE | 1, 2, 3, 4 (skip 5) | 45 min |
| **CE 1.0 Upgrade** | Legacy CE installation | 1, 2, 3, 4, 5 (all) | 40 min |
| **Partial Install** | Missing CE components | 1, 3, 4 (selective) | 15 min |

---

## Prerequisites

### Required for All Scenarios

- **Repomix CLI**: `npm install -g repomix`
- **CE framework packages**:
  - `ce-infrastructure.xml` (complete framework)
  - `ce-workflow-docs.xml` (reference documentation)
- **Git repository**: Project initialized with git
- **Project directory**: Write access to target directory

### Optional (Recommended)

- **Backup branch**: `git checkout -b pre-ce-backup`
- **Linear account**: For issue tracking integration
- **Syntropy MCP**: For tool integration
- **UV package manager**: For CE CLI tools

### Before You Begin

```bash
# Verify prerequisites
which repomix && echo "✓ Repomix installed"
which git && echo "✓ Git installed"
test -f ce-infrastructure.xml && echo "✓ Framework package available"

# Create backup (recommended)
git checkout -b pre-ce-backup
git push origin pre-ce-backup
git checkout main
```

---

## The 5-Phase Workflow

### Phase Overview

1. **Bucket Collection** (5-10 min) - Stage files for validation
2. **User Files Copy** (0-15 min) - Migrate project-specific files
3. **Repomix Package Handling** (5 min) - Extract framework packages
4. **CLAUDE.md Blending** (10 min) - Merge framework + project guide
5. **Legacy Cleanup** (0-5 min) - Remove duplicate legacy files

**Note**: Not all scenarios execute all phases. See scenario-specific instructions below.

---

## Phase 1: Bucket Collection (Universal)

**Duration**: 5-10 minutes
**Applies to**: All scenarios

### Purpose

Create a staging area to organize and validate files before copying to CE 1.1 destinations.

### Step 1.1: Create Staging Area

```bash
# Create bucket directories
mkdir -p tmp/syntropy-initialization/{serena,examples,prps,claude-md,claude-dir}

# Verify structure
ls -d tmp/syntropy-initialization/*/
# Expected:
# tmp/syntropy-initialization/serena/
# tmp/syntropy-initialization/examples/
# tmp/syntropy-initialization/prps/
# tmp/syntropy-initialization/claude-md/
# tmp/syntropy-initialization/claude-dir/
```

### Step 1.2: Copy Files to Buckets

**Bucket 1: Serena Memories**

```bash
# Copy existing Serena memories (if any)
if [ -d .serena/memories ]; then
  cp -R .serena/memories/*.md tmp/syntropy-initialization/serena/ 2>/dev/null || true
  echo "Serena files: $(ls tmp/syntropy-initialization/serena/*.md 2>/dev/null | wc -l)"
fi
```

**Bucket 2: Examples**

```bash
# Copy existing examples (if any)
if [ -d examples ]; then
  find examples -name "*.md" -exec cp {} tmp/syntropy-initialization/examples/ \; 2>/dev/null || true
  echo "Example files: $(ls tmp/syntropy-initialization/examples/*.md 2>/dev/null | wc -l)"
fi
```

**Bucket 3: PRPs**

```bash
# Copy existing PRPs (if any)
if [ -d PRPs ]; then
  find PRPs -name "*.md" -exec cp {} tmp/syntropy-initialization/prps/ \; 2>/dev/null || true
  echo "PRP files: $(ls tmp/syntropy-initialization/prps/*.md 2>/dev/null | wc -l)"
fi
```

**Bucket 4: CLAUDE.md**

```bash
# Copy existing CLAUDE.md (if any)
if [ -f CLAUDE.md ]; then
  cp CLAUDE.md tmp/syntropy-initialization/claude-md/
  echo "✓ CLAUDE.md copied"
fi
```

**Bucket 5: Claude Directory**

```bash
# Copy existing .claude directory (if any)
if [ -d .claude ]; then
  cp -R .claude/* tmp/syntropy-initialization/claude-dir/ 2>/dev/null || true
  echo "Claude files: $(ls tmp/syntropy-initialization/claude-dir/ 2>/dev/null | wc -l)"
fi
```

### Step 1.3: Validate Bucket Contents

Review files in each bucket to verify they match bucket characteristics:

**Serena Bucket Validation**

```bash
cd tmp/syntropy-initialization/serena/

for file in *.md 2>/dev/null; do
  # Check for memory-like content
  if ! grep -qi "memory\|pattern\|guide" "$file" 2>/dev/null; then
    mv "$file" "$file.fake"
    echo "⚠ Marked $file as fake (not a memory)"
  fi
done
```

**Examples Bucket Validation**

```bash
cd tmp/syntropy-initialization/examples/

for file in *.md 2>/dev/null; do
  # Check for example/pattern structure
  if ! grep -qi "example\|pattern\|workflow\|guide" "$file" 2>/dev/null; then
    mv "$file" "$file.fake"
    echo "⚠ Marked $file as fake (not an example)"
  fi
done
```

**PRPs Bucket Validation**

```bash
cd tmp/syntropy-initialization/prps/

for file in *.md 2>/dev/null; do
  # Check for PRP structure (YAML header or PRP-ID in filename)
  if ! grep -q "^---" "$file" 2>/dev/null && ! echo "$file" | grep -qi "prp-"; then
    mv "$file" "$file.fake"
    echo "⚠ Marked $file as fake (not a PRP)"
  fi
done
```

### Step 1.4: Bucket Summary

```bash
# Return to project root
cd /path/to/your/project

# Generate bucket report
cat > tmp/syntropy-initialization/bucket-report.txt << 'EOF'
# Bucket Collection Report

## Serena Bucket
Valid: $(ls tmp/syntropy-initialization/serena/*.md 2>/dev/null | grep -v ".fake" | wc -l)
Fake: $(ls tmp/syntropy-initialization/serena/*.fake 2>/dev/null | wc -l)

## Examples Bucket
Valid: $(ls tmp/syntropy-initialization/examples/*.md 2>/dev/null | grep -v ".fake" | wc -l)
Fake: $(ls tmp/syntropy-initialization/examples/*.fake 2>/dev/null | wc -l)

## PRPs Bucket
Valid: $(ls tmp/syntropy-initialization/prps/*.md 2>/dev/null | grep -v ".fake" | wc -l)
Fake: $(ls tmp/syntropy-initialization/prps/*.fake 2>/dev/null | wc -l)

## CLAUDE.md Bucket
Valid: $(ls tmp/syntropy-initialization/claude-md/CLAUDE.md 2>/dev/null | wc -l)

## Claude Dir Bucket
Files: $(ls tmp/syntropy-initialization/claude-dir/ 2>/dev/null | wc -l)
EOF

# Display report
cat tmp/syntropy-initialization/bucket-report.txt
```

**Phase 1 Complete**: Files staged and validated. Proceed to Phase 2 (or skip if Greenfield).

---

## Phase 2: User Files Copy

**Duration**: 0-15 minutes
**Applies to**: Mature Project, CE 1.0 Upgrade, Partial Install
**Skip for**: Greenfield

### Scenario Variations

**Skip this phase if**:
- **Greenfield**: No user files exist yet

**Full migration if**:
- **Mature Project**: Copy all validated files from buckets
- **CE 1.0 Upgrade**: Copy all validated files + classify existing files

**Selective migration if**:
- **Partial Install**: Copy only missing components

### Step 2.1: User Memory Migration

**For Mature Project and CE 1.0 Upgrade**:

```bash
# Copy validated user memories (non-.fake files)
find tmp/syntropy-initialization/serena -name "*.md" ! -name "*.fake" -exec cp {} .serena/memories/ \; 2>/dev/null || true

# Add YAML headers to memories without them
cd .serena/memories/

for memory in *.md 2>/dev/null; do
  # Skip if already has YAML header
  if head -n 1 "$memory" | grep -q "^---"; then
    continue
  fi

  # Determine type (heuristic based on content)
  if grep -qi "architecture\|security\|core principle\|critical" "$memory"; then
    TYPE="critical"
  else
    TYPE="regular"
  fi

  # Add YAML header
  cat > "${memory}.tmp" << EOF
---
type: $TYPE
priority: normal
category: guide
tags: []
source: target-project
created: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
updated: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

$(cat "$memory")
EOF
  mv "${memory}.tmp" "$memory"
  echo "✓ Added YAML header to $memory (type: $TYPE)"
done

cd ../..
```

### Step 2.2: User PRP Migration

**For Mature Project and CE 1.0 Upgrade**:

```bash
# Create PRP directories if needed
mkdir -p .ce/PRPs/{executed,feature-requests,archived}

# Copy validated user PRPs (non-.fake files)
find tmp/syntropy-initialization/prps -name "*.md" ! -name "*.fake" -exec sh -c '
  for prp; do
    # Determine destination based on filename or content
    if echo "$prp" | grep -qi "executed"; then
      cp "$prp" .ce/PRPs/executed/
    elif echo "$prp" | grep -qi "feature\|request"; then
      cp "$prp" .ce/PRPs/feature-requests/
    else
      cp "$prp" .ce/PRPs/executed/
    fi
  done
' sh {} +

echo "✓ User PRPs migrated to .ce/PRPs/"
```

### Step 2.3: User Examples Migration

**For Mature Project and CE 1.0 Upgrade**:

```bash
# Create examples directory if needed
mkdir -p .ce/examples

# Copy validated user examples (non-.fake files)
find tmp/syntropy-initialization/examples -name "*.md" ! -name "*.fake" -exec cp {} .ce/examples/ \; 2>/dev/null || true

echo "✓ User examples migrated to .ce/examples/"
```

### Step 2.4: User Commands/Settings Migration

**For all scenarios with existing .claude/ content**:

```bash
# Copy custom commands (preserve existing)
if [ -d tmp/syntropy-initialization/claude-dir/commands ]; then
  mkdir -p .claude/commands
  cp -n tmp/syntropy-initialization/claude-dir/commands/*.md .claude/commands/ 2>/dev/null || true
  echo "✓ User commands preserved"
fi

# Backup existing settings (will be merged in Phase 3)
if [ -f tmp/syntropy-initialization/claude-dir/settings.local.json ]; then
  mkdir -p .claude
  cp tmp/syntropy-initialization/claude-dir/settings.local.json .claude/settings.pre-ce.json
  echo "✓ Existing settings backed up"
fi
```

### Step 2.5: Migration Summary

```bash
# Generate migration report
cat > tmp/syntropy-initialization/phase2-report.txt << EOF
# Phase 2: User Files Migration Report

## Memories Migrated
User memories: $(find .serena/memories -maxdepth 1 -name "*.md" 2>/dev/null | wc -l)
Headers added: $(grep -l "^type:" .serena/memories/*.md 2>/dev/null | wc -l)

## PRPs Migrated
Executed: $(ls .ce/PRPs/executed/*.md 2>/dev/null | wc -l)
Feature requests: $(ls .ce/PRPs/feature-requests/*.md 2>/dev/null | wc -l)

## Examples Migrated
User examples: $(ls .ce/examples/*.md 2>/dev/null | wc -l)

## Commands/Settings
Custom commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l)
Settings backed up: $(test -f .claude/settings.pre-ce.json && echo "yes" || echo "no")
EOF

cat tmp/syntropy-initialization/phase2-report.txt
```

**Phase 2 Complete**: User files migrated with YAML headers. Proceed to Phase 3.

---

## Phase 3: Repomix Package Handling (Universal)

**Duration**: 5 minutes
**Applies to**: All scenarios

### Purpose

Extract framework packages to install system documentation, memories, examples, commands, and tools.

### Step 3.1: Copy Workflow Package

```bash
# Create system directory
mkdir -p .ce/examples/system/

# Copy workflow documentation package (reference only, not extracted)
cp ce-workflow-docs.xml .ce/examples/system/

echo "✓ Workflow package copied to .ce/examples/system/ce-workflow-docs.xml"
```

**Note**: `ce-workflow-docs.xml` is stored as-is for reference and redistribution. The actual framework files come from `ce-infrastructure.xml` extraction below.

### Step 3.2: Extract Infrastructure Package

```bash
# Extract complete framework infrastructure
# This creates /system/ subdirectories automatically
repomix --unpack ce-infrastructure.xml --target ./

# Verify extraction
echo "Framework files extracted:"
echo "  System memories: $(ls .serena/memories/system/*.md 2>/dev/null | wc -l)"
echo "  System examples: $(ls .ce/examples/system/*.md 2>/dev/null | wc -l)"
echo "  Framework commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l)"
echo "  Tool files: $(find tools -name "*.py" 2>/dev/null | wc -l)"
```

**What gets extracted**:

```
.ce/examples/system/          # 21 framework example files
.serena/memories/system/      # 23 framework memories (6 critical + 17 regular)
.claude/commands/             # 11 framework commands
.claude/settings.local.json   # Framework settings (merged with existing)
tools/                        # 33 tool source files
CLAUDE.md                     # Framework sections (merged with existing)
```

### Step 3.3: Validate Framework Installation

```bash
# Check system memories (expected: 23)
SYSTEM_MEMORIES=$(ls .serena/memories/system/*.md 2>/dev/null | wc -l)
test $SYSTEM_MEMORIES -eq 23 && echo "✓ All 23 system memories installed" || echo "⚠ Only $SYSTEM_MEMORIES system memories found"

# Check system examples (expected: 21)
SYSTEM_EXAMPLES=$(ls .ce/examples/system/*.md 2>/dev/null | wc -l)
test $SYSTEM_EXAMPLES -eq 21 && echo "✓ All 21 system examples installed" || echo "⚠ Only $SYSTEM_EXAMPLES system examples found"

# Check framework commands (expected: 11)
FRAMEWORK_COMMANDS=$(ls .claude/commands/*.md 2>/dev/null | wc -l)
test $FRAMEWORK_COMMANDS -ge 11 && echo "✓ All 11 framework commands installed" || echo "⚠ Only $FRAMEWORK_COMMANDS commands found"

# Check tool files (expected: 33)
TOOL_FILES=$(find tools -name "*.py" 2>/dev/null | wc -l)
test $TOOL_FILES -ge 33 && echo "✓ Tool source files installed" || echo "⚠ Only $TOOL_FILES tool files found"

# Check settings merged
test -f .claude/settings.local.json && jq empty .claude/settings.local.json && echo "✓ Settings valid JSON" || echo "⚠ Settings invalid"
```

### Step 3.4: Initialize CE Tools

```bash
# Install CE CLI tools
cd tools
./bootstrap.sh

# Verify installation
uv run ce --version
# Expected: ce version 1.1.0

# Run basic validation
uv run ce validate --level 1
# Expected: Structure validation passes

cd ..
```

**Phase 3 Complete**: Framework installed with /system/ organization. Proceed to Phase 4.

---

## Phase 4: CLAUDE.md Blending (Universal)

**Duration**: 10 minutes
**Applies to**: All scenarios

### Purpose

Merge framework CLAUDE.md sections with project-specific sections, creating a single unified project guide.

### Step 4.1: Backup Existing CLAUDE.md

```bash
# Backup user's CLAUDE.md (if exists)
if [ -f CLAUDE.md ]; then
  cp CLAUDE.md "CLAUDE.md.backup-$(date +%Y%m%d-%H%M%S)"
  echo "✓ CLAUDE.md backed up"
else
  echo "ℹ No existing CLAUDE.md (fresh installation)"
fi
```

### Step 4.2: Identify Framework vs Project Sections

Framework sections (from ce-infrastructure.xml):
- Communication
- Core Principles
- UV Package Management
- Ad-Hoc Code Policy
- Quick Commands
- Tool Naming Convention
- Allowed Tools Summary
- Command Permissions
- Quick Tool Selection
- Project Structure
- Testing Standards
- Code Quality
- Context Commands
- Syntropy MCP Tool Sync
- Linear Integration
- Batch PRP Generation
- PRP Sizing
- Testing Patterns
- Documentation Standards
- Efficient Doc Review
- Resources
- Keyboard Shortcuts
- Git Worktree
- Troubleshooting

Project sections (user-defined) are any sections not in framework list.

### Step 4.3: Blend Sections

**Manual Blending** (recommended for first installation):

```bash
# Edit CLAUDE.md to mark sections
vim CLAUDE.md

# Add [FRAMEWORK] or [PROJECT] markers to section headers:
# ## [FRAMEWORK] Communication
# ## [PROJECT] Project-Specific Communication
# ## [FRAMEWORK] Core Principles
# ## [PROJECT] Team Conventions
```

**Automated Blending** (if framework provides blending tool):

```bash
# Use denoise command to merge sections
/denoise CLAUDE.md

# Review merged output
less CLAUDE.md
```

### Step 4.4: Validate Blended CLAUDE.md

```bash
# Check for framework markers
grep -c "\[FRAMEWORK\]" CLAUDE.md
# Expected: Multiple framework sections marked

# Check for project markers (if any)
grep -c "\[PROJECT\]" CLAUDE.md
# Expected: 0+ (depending on scenario)

# Verify key framework sections present
for section in "Communication" "Core Principles" "Quick Commands" "Tool Naming Convention"; do
  grep -q "## .*$section" CLAUDE.md && echo "✓ $section section present" || echo "⚠ $section section missing"
done
```

### Step 4.5: Add Project-Specific Sections

**For Mature Project and CE 1.0 Upgrade**:

Add project-specific sections to CLAUDE.md:

```bash
cat >> CLAUDE.md << 'EOF'

---

## [PROJECT] Project-Specific Information

### Project Structure

**Architecture**: [Your architecture description]

**Key Components**:
- Component 1: [Description]
- Component 2: [Description]

### Development Workflow

**Branch Strategy**: [Your branching model]

**Code Review Process**: [Your review process]

### Testing Standards

**Test Coverage**: [Your coverage requirements]

**Test Frameworks**: [Your test tools]

### Deployment Process

**CI/CD Pipeline**: [Your pipeline description]

**Deployment Stages**: [Your stages]

---

EOF
```

**Phase 4 Complete**: CLAUDE.md blended with framework + project sections. Proceed to Phase 5 (if applicable).

---

## Phase 5: Legacy Cleanup

**Duration**: 0-5 minutes
**Applies to**: CE 1.0 Upgrade only
**Skip for**: Greenfield, Mature Project, Partial Install

### Scenario Variations

**Skip this phase if**:
- **Greenfield**: No legacy files (new project)
- **Mature Project**: No legacy CE files (first CE installation)
- **Partial Install**: Selective cleanup only

**Full cleanup if**:
- **CE 1.0 Upgrade**: Aggressive cleanup of legacy CE 1.0 structure

### Step 5.1: Verify Migration Completed

```bash
# Verify all files migrated to CE 1.1 structure
test -d .ce/PRPs/system && echo "✓ System PRPs migrated"
test -d .ce/examples/system && echo "✓ System examples migrated"
test -d .serena/memories/system && echo "✓ System memories migrated"

# Check for errors in migration
if [ -f tmp/syntropy-initialization/phase2-report.txt ]; then
  grep -i error tmp/syntropy-initialization/phase2-report.txt
  # Expected: No errors
fi
```

### Step 5.2: Archive Legacy Organization

```bash
# Create archive of legacy files before deletion (safety backup)
mkdir -p tmp/syntropy-initialization/legacy-backup/

# Archive legacy directories
tar -czf "tmp/syntropy-initialization/legacy-backup/pre-ce-1.1-$(date +%Y%m%d-%H%M%S).tar.gz" \
  PRPs/ \
  examples/ \
  .serena/memories/*.md \
  2>/dev/null || true

echo "✓ Legacy files archived"

# Verify archive created
ARCHIVE_FILE=$(ls -t tmp/syntropy-initialization/legacy-backup/*.tar.gz | head -n 1)
test -f "$ARCHIVE_FILE" && echo "✓ Archive: $ARCHIVE_FILE" || echo "⚠ Archive not created"
```

### Step 5.3: Delete Legacy Organization Files

**Delete legacy PRPs directory** (now in .ce/PRPs/):

```bash
if [ -d PRPs/ ]; then
  # Count files before deletion
  LEGACY_PRPS=$(find PRPs -name "*.md" | wc -l)

  # Delete directory
  rm -rf PRPs/

  echo "✓ Deleted legacy PRPs/ ($LEGACY_PRPS files migrated to .ce/PRPs/)"
fi
```

**Delete legacy examples directory** (now in .ce/examples/):

```bash
if [ -d examples/ ]; then
  # Count files before deletion
  LEGACY_EXAMPLES=$(find examples -name "*.md" | wc -l)

  # Delete directory
  rm -rf examples/

  echo "✓ Deleted legacy examples/ ($LEGACY_EXAMPLES files migrated to .ce/examples/)"
fi
```

**Delete legacy memories** (now in .serena/memories/system/):

```bash
# Delete only memories that were migrated to /system/
# Preserve user memories (not in system/)
if [ -d .serena/memories/ ]; then
  find .serena/memories/ -maxdepth 1 -name "*.md" -type f | while read file; do
    basename=$(basename "$file")
    if [ -f .serena/memories/system/"$basename" ]; then
      rm -f "$file"
      echo "✓ Deleted legacy .serena/memories/$basename (migrated to system/)"
    fi
  done
fi
```

### Step 5.4: Log Cleanup Summary

```bash
# Log cleanup actions to initialization report
cat > tmp/syntropy-initialization/phase5-report.txt << EOF
# Phase 5: Legacy Organization Cleanup Report

## Deleted Legacy Files

**PRPs Directory**: $(test ! -d PRPs && echo "Deleted" || echo "Still exists")
**Examples Directory**: $(test ! -d examples && echo "Deleted" || echo "Still exists")
**Legacy Memories**: $(find .serena/memories -maxdepth 1 -name "*.md" 2>/dev/null | wc -l) remaining at root level

## Backup

**Archive Created**: $(ls tmp/syntropy-initialization/legacy-backup/*.tar.gz | head -n 1)
**Archive Size**: $(du -h tmp/syntropy-initialization/legacy-backup/*.tar.gz | head -n 1 | cut -f1)

## Verification

**CE 1.1 Structure Active**: $(test -d .ce/PRPs/system && test -d .ce/examples/system && test -d .serena/memories/system && echo "Yes" || echo "No")
**Zero Noise**: $(test ! -d PRPs && test ! -d examples && echo "Yes - Clean project" || echo "No - Legacy files remain")

EOF

cat tmp/syntropy-initialization/phase5-report.txt
```

### Step 5.5: Zero Noise Verification

```bash
# Final verification: No legacy noise
echo ""
echo "=== Zero Noise Verification ==="

# Check legacy directories deleted
! test -d PRPs && echo "✅ PRPs/ removed" || echo "❌ PRPs/ still exists"
! test -d examples && echo "✅ examples/ removed" || echo "❌ examples/ still exists"

# Check no duplicate system memories
DUPLICATE_SYSTEM_MEMORIES=$(find .serena/memories/ -maxdepth 1 -name "*.md" -type f | while read f; do
  basename=$(basename "$f")
  test -f .serena/memories/system/"$basename" && echo "$f"
done | wc -l)

test "$DUPLICATE_SYSTEM_MEMORIES" -eq 0 && echo "✅ No duplicate system memories" || echo "❌ $DUPLICATE_SYSTEM_MEMORIES duplicate system memories found"

# Final status
if [ ! -d PRPs ] && [ ! -d examples ] && [ "$DUPLICATE_SYSTEM_MEMORIES" -eq 0 ]; then
  echo ""
  echo "✅ PROJECT IS CLEAN - Zero noise achieved"
else
  echo ""
  echo "⚠ PROJECT HAS LEGACY NOISE - Manual cleanup required"
fi
```

**Phase 5 Complete**: Legacy files removed, CE 1.1 structure clean. Installation complete.

---

## Scenario-Specific Workflows

### Scenario 1: Greenfield Project

**Use when**: New project with no existing CE components

**Phases**: 1, 3, 4 (skip 2, 5)

**Duration**: ~10 minutes

#### Quick Steps

```bash
# Phase 1: Bucket Collection (will be empty)
mkdir -p tmp/syntropy-initialization/{serena,examples,prps,claude-md,claude-dir}
echo "✓ Buckets created (empty for greenfield)"

# Phase 2: SKIP (no user files)
echo "⏭ Skipping Phase 2 (no user files)"

# Phase 3: Repomix Package Handling
repomix --unpack ce-infrastructure.xml --target ./
cd tools && ./bootstrap.sh && cd ..
echo "✓ Framework installed"

# Phase 4: CLAUDE.md Blending (framework only)
grep -q "## Communication" CLAUDE.md && echo "✓ Framework CLAUDE.md installed"

# Phase 5: SKIP (no legacy files)
echo "⏭ Skipping Phase 5 (no legacy files)"

# Validate
cd tools && uv run ce validate --level 4 && cd ..
echo "✅ Greenfield installation complete"
```

---

### Scenario 2: Mature Project (No CE)

**Use when**: Existing codebase with no CE components

**Phases**: 1, 2, 3, 4 (skip 5)

**Duration**: ~45 minutes

---

### Scenario 3: CE 1.0 Upgrade

**Use when**: Existing CE installation, no .ce/ directory (legacy structure)

**Phases**: 1, 2, 3, 4, 5 (all phases)

**Duration**: ~40 minutes

---

### Scenario 4: Partial Install (Completion)

**Use when**: Project has some CE components but missing others

**Phases**: 1, 3, 4 (selective)

**Duration**: ~15 minutes

---

## Validation Checklist

### Structure Validation

```bash
# Check CE 1.1 directory structure
test -d .ce/examples/system && echo "✅ .ce/examples/system/"
test -d .ce/PRPs/system && echo "✅ .ce/PRPs/system/"
test -d .serena/memories/system && echo "✅ .serena/memories/system/"
test -d .claude/commands && echo "✅ .claude/commands/"
test -f CLAUDE.md && echo "✅ CLAUDE.md"
```

### Component Counts

```bash
# Expected file counts
echo "System memories: $(ls .serena/memories/system/*.md 2>/dev/null | wc -l) (expected: 23)"
echo "System examples: $(ls .ce/examples/system/*.md 2>/dev/null | wc -l) (expected: 21)"
echo "Framework commands: $(ls .claude/commands/*.md 2>/dev/null | wc -l) (expected: 11+)"
```

---

## Troubleshooting

### Issue: Repomix command not found

**Solution**:

```bash
# Install repomix globally
npm install -g repomix

# Or use npx
npx repomix --unpack ce-infrastructure.xml --target ./
```

### Issue: Bootstrap script fails

**Solution**:

```bash
cd tools

# Install UV manually
curl -LsSf https://astral.sh/uv/install.sh | sh

# Retry bootstrap
./bootstrap.sh

# Or install dependencies directly
uv sync
```

---

## Success Criteria

Your installation is complete when:

- ✅ All CE 1.1 directories created (`.ce/`, `.serena/`, `.claude/`)
- ✅ System files installed (23 memories, 21 examples, 11 commands)
- ✅ CLAUDE.md present with framework sections
- ✅ Settings JSON valid and merged
- ✅ CE tools installed (`ce --version` works)
- ✅ Validation level 4 passes
- ✅ Context drift <5%
- ✅ Zero noise (no legacy directories for CE 1.0 upgrades)
- ✅ Serena memories loaded
- ✅ Linear configured (if using)
- ✅ First PRP created successfully

---

## Related Documentation

- **Framework Rules**: `.ce/RULES.md`
- **Tool Usage Guide**: `.ce/examples/system/TOOL-USAGE-GUIDE.md`
- **PRP-0 Template**: `.ce/examples/system/templates/PRP-0-CONTEXT-ENGINEERING.md`
- **Validation Levels**: `.serena/memories/system/validation-levels.md`
- **Testing Standards**: `.serena/memories/system/testing-standards.md`

---

**Installation Guide Version**: 1.1
**Last Updated**: 2025-11-04
**Framework Version**: CE 1.1
