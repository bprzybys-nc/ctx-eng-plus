---
confidence: 9/10
context_memories: []
context_sync:
  ce_updated: false
  last_sync: null
  serena_updated: false
created_date: '2025-11-04T00:00:00Z'
dependencies: []
description: Create repomix configurations for 2 distribution packages - workflow documentation and infrastructure files
effort_hours: 3.5
last_updated: '2025-11-04T00:00:00Z'
meeting_evidence: []
name: Repomix Configuration & Profile Creation
parent_prp: null
priority: HIGH
prp_id: PRP-32.1.2
batch_id: 32
stage: 1
order: 2
risk: LOW-MEDIUM
status: pending
task_id: null
updated: '2025-11-04T00:00:00Z'
updated_by: batch-gen-prp
version: 1
---

# PRP-32.1.2: Repomix Configuration & Profile Creation

## 🎯 TL;DR

**Problem**: CE framework documentation is scattered across 25+ files with no consolidated distribution format. Users need both workflow documentation (examples) and infrastructure files (memories, commands, tools) but currently must manually collect them.

**Solution**: Create 2 repomix configuration profiles that generate XML packages:
1. **Workflow Documentation Package** (21 workflow examples + CLAUDE.md sections) → .ce/ce-workflow-docs.xml (<60KB)
2. **Infrastructure Package** (6 universal memories + 11 commands + tools/*.py) → .ce/ce-infrastructure.xml (<40KB)

**Impact**:
- Enables one-command distribution of CE framework components
- Reduces token usage for new projects (consolidated XML vs scattered files)
- Provides human-readable mirrors (.md format) alongside XML
- Foundation for Syntropy MCP 1.1 release packages

**Risk**: LOW-MEDIUM
- File inclusion paths must be precise (wrong paths = missing content)
- Token size estimation critical (oversized packages defeat purpose)
- Phase 5 will regenerate with refined docs from Phase 4

**Effort**: 3.5h
- Repomix profile creation: 1h
- Dry-run validation + size tuning: 1h
- Documentation (manifest + README): 1h
- Testing both packages: 0.5h

**Non-Goals**:
- ❌ Creating new documentation content (use existing docs as-is)
- ❌ Modifying existing files (Phase 4 handles doc refinement)
- ❌ Implementing automated regeneration (Phase 5 task)
- ❌ Distribution/upload mechanisms (out of scope)

---

## 📋 Pre-Execution Context Rebuild

**Complete before implementation:**

- [ ] **Review documentation**:
  - examples/INDEX.md (workflow example catalog)
  - .serena/memories/*.md (identify universal vs project-specific)
  - .claude/commands/*.md (command documentation)

- [ ] **Verify file structure**:
  - Directory exists: examples/
  - Directory exists: .serena/memories/
  - Directory exists: .claude/commands/
  - Directory exists: tools/ce/
  - File exists: CLAUDE.md

- [ ] **Check repomix availability**:
  - Command exists: `which repomix` or `npx repomix --version`
  - Understanding of repomix YAML config format

- [ ] **Git baseline**: Clean working tree

---

## 📖 Context

**Related Work**:
- **Batch 32 Overview**: Syntropy MCP 1.1 Release finalization (5-phase plan)
- **Stage 1 Siblings**:
  - PRP-32.1.1 (Documentation Audit) - runs in parallel
  - PRP-32.1.3 (System Model Update) - runs in parallel
- **Phase Dependencies**: Phase 5 (PRP-32.5.1) will regenerate packages with refined docs from Phase 4

**Current State**:
- 25+ documentation files scattered across examples/, .serena/memories/, .claude/commands/
- No consolidated distribution format
- Manual file collection required for new projects
- Token counting manual and error-prone
- examples/INDEX.md contains IsWorkflow classification (21 Yes, 4 No)

**Desired State**:
- 2 repomix YAML profiles: .ce/repomix-profile-workflow.yml, .ce/repomix-profile-infrastructure.yml
- Generated XML packages: .ce/ce-workflow-docs.xml, .ce/ce-infrastructure.xml
- Human-readable mirrors: .ce/ce-workflow-docs.md, .ce/ce-infrastructure.md
- Manifest documentation: .ce/repomix-manifest.yml (documents what's in each package)
- Usage guide: .ce/README-REPOMIX.md (how to use packages)
- All packages <100KB total (<60KB + <40KB)

**Why Now**:
- Foundation for Syntropy MCP 1.1 release
- Stage 1 task (can run parallel with doc audit and system model update)
- Uses current docs as-is (no dependency on Phase 4 doc refinement)

---

## 🔍 Logic Flow

### Repomix Package Generation Pipeline

```mermaid
graph TB
    A[Create Workflow Profile] --> B[Create Infrastructure Profile]
    B --> C[Dry-Run Workflow Package]
    C --> D[Dry-Run Infrastructure Package]
    D --> E{Token Counts OK?}
    E -->|No| F[Adjust Include/Exclude Patterns]
    F --> C
    E -->|Yes| G[Generate Final XML Files]
    G --> H[Generate MD Mirrors]
    H --> I[Create Manifest]
    I --> J[Create README]
    J --> K[Validation Complete]

    style A fill:#e1f5ff,color:#000
    style B fill:#e1f5ff,color:#000
    style G fill:#d4edda,color:#000
    style K fill:#d4edda,color:#000
    style F fill:#fff3cd,color:#000
```

### File Selection Logic

**Workflow Package Decision Tree**:
```
examples/**/*.md → Check INDEX.md IsWorkflow?
  ├─ Yes → Include
  ├─ No → Exclude
  └─ Not Listed → Exclude (safe default)

CLAUDE.md → Extract sections:
  ├─ Include: Quick Commands, PRP Sizing, Testing Patterns
  ├─ Include: Batch PRP Generation, Git Worktree
  └─ Exclude: Installation, Troubleshooting (project-specific)
```

**Infrastructure Package Decision Tree**:
```
.serena/memories/*.md → Universal or project-specific?
  ├─ Universal (6 files):
  │   ├─ code-style-conventions.md
  │   ├─ suggested-commands.md
  │   ├─ task-completion-checklist.md
  │   ├─ testing-standards.md
  │   ├─ tool-usage-syntropy.md
  │   └─ use-syntropy-tools-not-bash.md
  └─ Project-specific → Exclude

.claude/commands/*.md → Framework commands only (all 7 included)

tools/ce/*.py → All source files + pyproject.toml
tools/tests/ → Excluded (too large, users can write own tests)
```

---

## 🛠️ Implementation Steps

### Phase 1: Workflow Documentation Package (1.5h)

**Step 1.1: Create Workflow Profile (.ce/repomix-profile-workflow.yml)**

```yaml
# Repomix Configuration: CE Framework Workflow Documentation
# Output: .ce/ce-workflow-docs.xml
# Target Size: <60KB
# Description: Workflow examples and patterns from CE framework

output:
  filePath: .ce/ce-workflow-docs.xml
  style: xml
  topFilesLength: 5
  showLineNumbers: true
  copyToClipboard: false
  instructionFilePath: null

include:
  # Workflow examples (IsWorkflow=Yes from INDEX.md)
  - "examples/patterns/*.md"
  - "examples/*.md"
  - "!examples/README.md"  # Exclude (redundant with INDEX.md)

  # CLAUDE.md workflow sections only (extract manually if needed)
  - "CLAUDE.md"

exclude:
  # Project-specific examples (IsWorkflow=No)
  - "examples/model/SystemModel.md"
  - "examples/example.setting.local.md"
  - "examples/linear-integration-example.md"
  - "examples/tmp-directory-convention.md"

  # System files
  - ".git"
  - ".tmp"
  - "node_modules"
  - "__pycache__"

ignore:
  customPatterns: []

security:
  enableSecurityCheck: true
```

**Validation**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
npx repomix --config .ce/repomix-profile-workflow.yml --dry-run
# Expected: ~21 files included, <60KB estimated size
```

**Step 1.2: Generate Workflow Package**

```bash
npx repomix --config .ce/repomix-profile-workflow.yml
# Output: .ce/ce-workflow-docs.xml

# Verify token count (rough estimate: 1 token ≈ 4 chars)
wc -c .ce/ce-workflow-docs.xml
# Expected: <240,000 characters (~60KB tokens)

# Create human-readable mirror
npx repomix --config .ce/repomix-profile-workflow.yml --style markdown --output .ce/ce-workflow-docs.md
```

---

### Phase 2: Infrastructure Package (1.5h)

**Step 2.1: Create Infrastructure Profile (.ce/repomix-profile-infrastructure.yml)**

```yaml
# Repomix Configuration: CE Framework Infrastructure Files
# Output: .ce/ce-infrastructure.xml
# Target Size: <40KB
# Description: Universal memories, framework commands, and tool source code

output:
  filePath: .ce/ce-infrastructure.xml
  style: xml
  topFilesLength: 5
  showLineNumbers: true
  copyToClipboard: false
  instructionFilePath: null

include:
  # Universal memories (explicit 6-file list)
  - ".serena/memories/code-style-conventions.md"
  - ".serena/memories/suggested-commands.md"
  - ".serena/memories/task-completion-checklist.md"
  - ".serena/memories/testing-standards.md"
  - ".serena/memories/tool-usage-syntropy.md"
  - ".serena/memories/use-syntropy-tools-not-bash.md"

  # Framework commands (all 7)
  - ".claude/commands/*.md"

  # Tool source code
  - "tools/ce/*.py"
  - "tools/pyproject.toml"

exclude:
  # Project-specific memories
  - ".serena/memories/codebase-structure.md"
  - ".serena/memories/project-overview.md"
  - ".serena/memories/PRP-*.md"
  - ".serena/memories/*-pattern.md"
  - ".serena/memories/*-implementation*.md"
  - ".serena/memories/TOOL-USAGE-GUIDE.md"  # Symlink, included via examples

  # Test files (too large, users write own)
  - "tools/tests"

  # System files
  - ".git"
  - ".tmp"
  - "__pycache__"
  - "*.pyc"

ignore:
  customPatterns: []

security:
  enableSecurityCheck: true
```

**Validation**:
```bash
npx repomix --config .ce/repomix-profile-infrastructure.yml --dry-run
# Expected: 6 memories + 11 commands + ~30 .py files = ~47 files, <40KB
```

**Step 2.2: Generate Infrastructure Package**

```bash
npx repomix --config .ce/repomix-profile-infrastructure.yml
# Output: .ce/ce-infrastructure.xml

# Verify token count
wc -c .ce/ce-infrastructure.xml
# Expected: <160,000 characters (~40KB tokens)

# Create human-readable mirror
npx repomix --config .ce/repomix-profile-infrastructure.yml --style markdown --output .ce/ce-infrastructure.md
```

---

### Phase 3: Documentation (1h)

**Step 3.1: Create Manifest (.ce/repomix-manifest.yml)**

```yaml
# CE Framework Repomix Packages Manifest
# Documents contents of distribution packages

version: "1.0.0"
generated: "2025-11-04T00:00:00Z"
batch: 32
phase: 1

packages:
  workflow_docs:
    file: .ce/ce-workflow-docs.xml
    mirror: .ce/ce-workflow-docs.md
    profile: .ce/repomix-profile-workflow.yml
    description: "Workflow examples and patterns from CE framework"
    target_size: "<60KB"
    contents:
      - type: "examples"
        count: 21
        filter: "IsWorkflow=Yes from examples/INDEX.md"
        files:
          - "examples/patterns/*.md"
          - "examples/TOOL-USAGE-GUIDE.md"
          - "examples/prp-decomposition-patterns.md"
          - "examples/syntropy-status-hook-system.md"
          # ... (full list)
      - type: "documentation"
        count: 1
        filter: "Workflow sections only"
        files:
          - "CLAUDE.md (Quick Commands, PRP Sizing, Batch PRP Generation, Git Worktree)"

    excluded:
      - "examples/model/SystemModel.md (IsWorkflow=No)"
      - "examples/example.setting.local.md (project-specific)"
      - "examples/linear-integration-example.md (project-specific)"
      - "examples/tmp-directory-convention.md (project-specific)"

    use_cases:
      - "New project onboarding (workflow patterns)"
      - "PRP generation reference (decomposition patterns)"
      - "Command usage examples (slash commands, ce tools)"

  infrastructure:
    file: .ce/ce-infrastructure.xml
    mirror: .ce/ce-infrastructure.md
    profile: .ce/repomix-profile-infrastructure.yml
    description: "Universal memories, framework commands, and tool source code"
    target_size: "<40KB"
    contents:
      - type: "memories"
        count: 6
        filter: "Universal only (not project-specific)"
        files:
          - ".serena/memories/code-style-conventions.md"
          - ".serena/memories/suggested-commands.md"
          - ".serena/memories/task-completion-checklist.md"
          - ".serena/memories/testing-standards.md"
          - ".serena/memories/tool-usage-syntropy.md"
          - ".serena/memories/use-syntropy-tools-not-bash.md"

      - type: "commands"
        count: 11
        filter: "All framework commands"
        files:
          - ".claude/commands/batch-exe-prp.md"
          - ".claude/commands/batch-gen-prp.md"
          - ".claude/commands/denoise.md"
          - ".claude/commands/execute-prp.md"
          - ".claude/commands/generate-prp.md"
          - ".claude/commands/peer-review.md"
          - ".claude/commands/sync-with-syntropy.md"
          - ".claude/commands/syntropy-health.md"
          - ".claude/commands/tools-misuse-scan.md"
          - ".claude/commands/update-context.md"
          - ".claude/commands/vacuum.md"

      - type: "tools"
        count: 33
        filter: "All CE tool source code"
        files:
          - "tools/ce/*.py (all modules)"
          - "tools/pyproject.toml"

    excluded:
      - ".serena/memories/*-pattern.md (project-specific patterns)"
      - ".serena/memories/PRP-*.md (implementation memories)"
      - ".serena/memories/project-overview.md (project-specific)"
      - "tools/tests/ (users write own tests)"

    use_cases:
      - "Framework installation (tool source code)"
      - "Serena memory initialization (universal memories)"
      - "Command reference (slash command documentation)"

regeneration:
  schedule: "Phase 5 (after Phase 4 doc refinement)"
  trigger: "Documentation updates in Phase 4"
  automated: false
  notes: "Manual regeneration in Phase 5 after doc audit/refinement complete"
```

**Step 3.2: Create README (.ce/README-REPOMIX.md)**

```markdown
# CE Framework Repomix Packages

Distribution packages for Context Engineering framework components.

## Overview

Two consolidated XML packages containing CE framework documentation and infrastructure:

1. **Workflow Documentation** (.ce/ce-workflow-docs.xml)
   - 21 workflow examples (IsWorkflow=Yes)
   - CLAUDE.md workflow sections
   - Target: <60KB tokens

2. **Infrastructure Files** (.ce/ce-infrastructure.xml)
   - 6 universal Serena memories
   - 11 framework slash commands
   - 33 CE tool source files
   - Target: <40KB tokens

**Total Size**: <100KB tokens (both packages combined)

## Package Contents

See [.ce/repomix-manifest.yml](.ce/repomix-manifest.yml) for detailed contents and file lists.

## Usage

### Generate Packages

```bash
# Workflow documentation package
npx repomix --config .ce/repomix-profile-workflow.yml

# Infrastructure package
npx repomix --config .ce/repomix-profile-infrastructure.yml

# Both packages
npx repomix --config .ce/repomix-profile-workflow.yml && \
npx repomix --config .ce/repomix-profile-infrastructure.yml
```

### Verify Token Counts

```bash
# Workflow package (expect <60KB)
wc -c .ce/ce-workflow-docs.xml

# Infrastructure package (expect <40KB)
wc -c .ce/ce-infrastructure.xml

# Total (expect <100KB)
wc -c .ce/ce-*.xml
```

### View Human-Readable Versions

```bash
# Markdown mirrors generated alongside XML
cat .ce/ce-workflow-docs.md
cat .ce/ce-infrastructure.md
```

## Use Cases

### New Project Onboarding

```bash
# Copy workflow examples to new project
cp .ce/ce-workflow-docs.xml /path/to/new-project/docs/

# Initialize with infrastructure
cp .ce/ce-infrastructure.xml /path/to/new-project/docs/
```

### Distribution

```bash
# Upload to documentation site
aws s3 cp .ce/ce-workflow-docs.xml s3://docs/ce-framework/
aws s3 cp .ce/ce-infrastructure.xml s3://docs/ce-framework/

# Or attach to GitHub release
gh release upload v1.1 .ce/ce-workflow-docs.xml .ce/ce-infrastructure.xml
```

### Token Analysis

```bash
# Estimate token usage (rough: 1 token ≈ 4 chars)
echo "Workflow: $(($(wc -c < .ce/ce-workflow-docs.xml) / 4)) tokens"
echo "Infrastructure: $(($(wc -c < .ce/ce-infrastructure.xml) / 4)) tokens"
```

## Profiles

### Workflow Profile (.ce/repomix-profile-workflow.yml)

- **Includes**: examples/patterns/*.md, CLAUDE.md (workflow sections)
- **Excludes**: Project-specific examples (IsWorkflow=No in INDEX.md)
- **Output**: .ce/ce-workflow-docs.xml, .ce/ce-workflow-docs.md

### Infrastructure Profile (.ce/repomix-profile-infrastructure.yml)

- **Includes**: 6 universal memories, 7 commands, tools/ce/*.py
- **Excludes**: Project-specific memories, tests/
- **Output**: .ce/ce-infrastructure.xml, .ce/ce-infrastructure.md

## Regeneration

Packages are regenerated in **Phase 5** (PRP-32.5.1) after documentation refinement in Phase 4.

**Trigger**: Documentation updates from Phase 4 audit/refinement

**Process**:
1. Phase 4 completes doc refinement
2. Phase 5 reruns repomix with updated profiles
3. New packages incorporate refined documentation
4. Manifest updated with new file counts/sizes

## Notes

- **Phase 1 Generation**: Uses current docs as-is (no modifications)
- **Phase 5 Regeneration**: Uses refined docs from Phase 4
- **Size Monitoring**: If packages exceed targets, adjust include/exclude patterns
- **Validation**: Dry-run before generating to verify file counts and sizes

## Troubleshooting

### Package Too Large

```bash
# Check file sizes
npx repomix --config .ce/repomix-profile-workflow.yml --dry-run
npx repomix --config .ce/repomix-profile-infrastructure.yml --dry-run

# Adjust exclude patterns in profiles to remove large files
```

### Missing Files

```bash
# Verify include patterns match files
find examples -name "*.md" | grep -v "examples/model"
find .serena/memories -name "*.md" | grep -E "(code-style|suggested-commands|task-completion|testing-standards|tool-usage-syntropy|use-syntropy)"
```

### Repomix Not Found

```bash
# Install repomix globally
npm install -g repomix

# Or use npx (no install needed)
npx repomix --version
```

---

**Generated**: Batch 32, Phase 1, PRP-32.1.2
**Version**: 1.0.0
**Last Updated**: 2025-11-04
```

---

### Phase 4: Testing & Validation (0.5h)

**Step 4.1: Dry-Run Validation**

```bash
# Test workflow profile
npx repomix --config .ce/repomix-profile-workflow.yml --dry-run > /tmp/workflow-dryrun.txt
cat /tmp/workflow-dryrun.txt
# Verify: ~21 files, no errors

# Test infrastructure profile
npx repomix --config .ce/repomix-profile-infrastructure.yml --dry-run > /tmp/infra-dryrun.txt
cat /tmp/infra-dryrun.txt
# Verify: 6 memories + 7 commands + ~30 .py files = ~43 files
```

**Step 4.2: Generate Both Packages**

```bash
# Generate workflow package
npx repomix --config .ce/repomix-profile-workflow.yml
npx repomix --config .ce/repomix-profile-workflow.yml --style markdown --output .ce/ce-workflow-docs.md

# Generate infrastructure package
npx repomix --config .ce/repomix-profile-infrastructure.yml
npx repomix --config .ce/repomix-profile-infrastructure.yml --style markdown --output .ce/ce-infrastructure.md
```

**Step 4.3: Token Count Verification**

```bash
# Character counts (1 token ≈ 4 chars)
WORKFLOW_CHARS=$(wc -c < .ce/ce-workflow-docs.xml)
INFRA_CHARS=$(wc -c < .ce/ce-infrastructure.xml)
TOTAL_CHARS=$((WORKFLOW_CHARS + INFRA_CHARS))

WORKFLOW_TOKENS=$((WORKFLOW_CHARS / 4))
INFRA_TOKENS=$((INFRA_CHARS / 4))
TOTAL_TOKENS=$((TOTAL_CHARS / 4))

echo "Workflow: $WORKFLOW_TOKENS tokens (target <60K)"
echo "Infrastructure: $INFRA_TOKENS tokens (target <40K)"
echo "Total: $TOTAL_TOKENS tokens (target <100K)"

# Validation
test $WORKFLOW_TOKENS -lt 60000 && echo "✓ Workflow size OK" || echo "✗ Workflow too large"
test $INFRA_TOKENS -lt 40000 && echo "✓ Infrastructure size OK" || echo "✗ Infrastructure too large"
test $TOTAL_TOKENS -lt 100000 && echo "✓ Total size OK" || echo "✗ Total too large"
```

**Step 4.4: Content Verification**

```bash
# Verify workflow package contains workflow examples
grep -c "examples/patterns" .ce/ce-workflow-docs.xml
# Expected: 21+ occurrences

# Verify infrastructure package contains exactly 6 memories
grep -c ".serena/memories" .ce/ce-infrastructure.xml
# Expected: 6 occurrences

# Verify infrastructure package contains 11 commands
grep -c ".claude/commands" .ce/ce-infrastructure.xml
# Expected: 11+ occurrences

# Verify infrastructure package contains tool source
grep -c "tools/ce" .ce/ce-infrastructure.xml
# Expected: 33+ occurrences
```

---

## ✅ Validation Gates

### Gate 1: Profile Syntax Valid

**Command**:
```bash
# Workflow profile
npx repomix --config .ce/repomix-profile-workflow.yml --dry-run

# Infrastructure profile
npx repomix --config .ce/repomix-profile-infrastructure.yml --dry-run
```

**Expected Output**: "Dry run completed successfully" (no YAML parse errors)

**On Failure**: Review YAML syntax, fix indentation/formatting

---

### Gate 2: File Inclusion Correct

**Workflow Package**:
```bash
npx repomix --config .ce/repomix-profile-workflow.yml --dry-run | grep "Files to process:"
# Expected: 21+ files (workflow examples + CLAUDE.md)
```

**Infrastructure Package**:
```bash
npx repomix --config .ce/repomix-profile-infrastructure.yml --dry-run | grep "Files to process:"
# Expected: 47+ files (6 memories + 11 commands + 30+ .py files)
```

**On Failure**: Adjust include/exclude patterns in profiles

---

### Gate 3: XML Generation Success

**Command**:
```bash
# Generate both packages
npx repomix --config .ce/repomix-profile-workflow.yml
npx repomix --config .ce/repomix-profile-infrastructure.yml

# Verify files exist
ls -lh .ce/ce-workflow-docs.xml
ls -lh .ce/ce-infrastructure.xml
```

**Expected Output**: Both .xml files exist, non-zero size

**On Failure**: Check repomix error messages, verify file paths

---

### Gate 4: Token Counts Within Target

**Command**:
```bash
# Run token count script (from Step 4.3)
WORKFLOW_TOKENS=$(( $(wc -c < .ce/ce-workflow-docs.xml) / 4 ))
INFRA_TOKENS=$(( $(wc -c < .ce/ce-infrastructure.xml) / 4 ))
echo "Workflow: $WORKFLOW_TOKENS tokens (<60K target)"
echo "Infrastructure: $INFRA_TOKENS tokens (<40K target)"
```

**Expected Output**:
- Workflow: <60,000 tokens
- Infrastructure: <40,000 tokens
- Total: <100,000 tokens

**On Failure**:
- Too large → Add more exclude patterns (remove large files)
- Too small → Verify all intended files included

---

### Gate 5: Markdown Mirrors Generated

**Command**:
```bash
ls -lh .ce/ce-workflow-docs.md
ls -lh .ce/ce-infrastructure.md
```

**Expected Output**: Both .md files exist, non-zero size

**On Failure**: Regenerate with `--style markdown` flag

---

### Gate 6: Documentation Complete

**Command**:
```bash
# Verify manifest exists
test -f .ce/repomix-manifest.yml && echo "✓ Manifest exists" || echo "✗ Manifest missing"

# Verify README exists
test -f .ce/README-REPOMIX.md && echo "✓ README exists" || echo "✗ README missing"

# Verify manifest contains both packages
grep -q "workflow_docs:" .ce/repomix-manifest.yml && echo "✓ Workflow documented" || echo "✗ Workflow missing"
grep -q "infrastructure:" .ce/repomix-manifest.yml && echo "✓ Infrastructure documented" || echo "✗ Infrastructure missing"
```

**Expected Output**: All checks pass (✓)

**On Failure**: Create missing documentation files (Steps 3.1-3.2)

---

## 🧪 Testing Strategy

### Test Framework
Manual validation (no automated tests for repomix configs)

### Test Commands

```bash
# Full validation pipeline
cd /Users/bprzybyszi/nc-src/ctx-eng-plus

# 1. Dry-run both profiles
npx repomix --config .ce/repomix-profile-workflow.yml --dry-run
npx repomix --config .ce/repomix-profile-infrastructure.yml --dry-run

# 2. Generate packages
npx repomix --config .ce/repomix-profile-workflow.yml
npx repomix --config .ce/repomix-profile-infrastructure.yml

# 3. Generate markdown mirrors
npx repomix --config .ce/repomix-profile-workflow.yml --style markdown --output .ce/ce-workflow-docs.md
npx repomix --config .ce/repomix-profile-infrastructure.yml --style markdown --output .ce/ce-infrastructure.md

# 4. Verify token counts
WORKFLOW_TOKENS=$(( $(wc -c < .ce/ce-workflow-docs.xml) / 4 ))
INFRA_TOKENS=$(( $(wc -c < .ce/ce-infrastructure.xml) / 4 ))
TOTAL_TOKENS=$((WORKFLOW_TOKENS + INFRA_TOKENS))
echo "Workflow: $WORKFLOW_TOKENS tokens"
echo "Infrastructure: $INFRA_TOKENS tokens"
echo "Total: $TOTAL_TOKENS tokens"

# 5. Content verification
grep -c "examples/patterns" .ce/ce-workflow-docs.xml  # Expect 21+
grep -c ".serena/memories" .ce/ce-infrastructure.xml   # Expect 6
grep -c ".claude/commands" .ce/ce-infrastructure.xml   # Expect 11

# 6. Documentation verification
test -f .ce/repomix-manifest.yml && echo "✓ Manifest" || echo "✗ Manifest"
test -f .ce/README-REPOMIX.md && echo "✓ README" || echo "✗ README"
```

### Test Scenarios

**Scenario 1: Workflow Package Too Large**
- **Cause**: Too many files included or large CLAUDE.md sections
- **Resolution**: Add more exclude patterns, reduce CLAUDE.md extraction
- **Verification**: Rerun dry-run, verify new token count

**Scenario 2: Missing Universal Memories**
- **Cause**: Typo in memory file paths or wrong exclusion
- **Resolution**: Fix paths in infrastructure profile, verify with `ls .serena/memories/*.md`
- **Verification**: Rerun infrastructure package generation, grep for memory count

**Scenario 3: Commands Not Included**
- **Cause**: Incorrect glob pattern or exclusion
- **Resolution**: Fix `.claude/commands/*.md` pattern, ensure no conflicting excludes
- **Verification**: Grep for command count in infrastructure package

---

## 🚀 Rollout Plan

### Phase 1: Development (Local)

**Step 1**: Create repomix profiles in .ce/ directory
**Step 2**: Dry-run validation for both profiles
**Step 3**: Generate XML packages and markdown mirrors
**Step 4**: Create manifest and README documentation

**Validation**: All 6 validation gates pass

---

### Phase 2: Review

**Step 1**: Review generated packages for completeness
- Workflow package contains 21 workflow examples
- Infrastructure package contains exactly 6 universal memories, 11 commands
- Token counts within targets (<60KB, <40KB)

**Step 2**: Review documentation
- Manifest documents all included/excluded files
- README provides clear usage instructions

**Step 3**: Test package usability
- Can workflow package be loaded into Claude?
- Can infrastructure package be extracted and used?

---

### Phase 3: Commit & Merge

**Step 1**: Commit new files to repository
```bash
git add .ce/repomix-profile-*.yml
git add .ce/ce-workflow-docs.*
git add .ce/ce-infrastructure.*
git add .ce/repomix-manifest.yml
git add .ce/README-REPOMIX.md
git commit -m "PRP-32.1.2: Add repomix configuration profiles

- Create workflow documentation package profile
- Create infrastructure package profile
- Generate XML packages and markdown mirrors
- Add manifest and usage documentation
- Token counts: workflow <60KB, infrastructure <40KB"
```

**Step 2**: Push to main branch
```bash
git push origin main
```

**Step 3**: Phase 5 Regeneration Preparation
- Packages ready for regeneration after Phase 4 doc refinement
- Profiles can be reused with updated documentation
- Manifest documents regeneration schedule

---

## 📊 Success Metrics

1. **Package Count**: 2 repomix profiles created (.ce/repomix-profile-*.yml)
2. **Generated Files**: 4 output files (2 XML + 2 MD mirrors)
3. **Token Efficiency**: Combined <100KB (workflow <60KB, infrastructure <40KB)
4. **File Coverage**:
   - Workflow: 21+ workflow examples included
   - Infrastructure: 6 universal memories, 11 commands, 30+ tool files
5. **Documentation**: 2 doc files (manifest + README)
6. **Validation**: All 6 gates pass

---

## 🔗 Related PRPs

- **PRP-32.1.1** (Documentation Audit): Parallel task, identifies IsWorkflow classifications
- **PRP-32.1.3** (System Model Update): Parallel task, updates model documentation
- **PRP-32.5.1** (Package Regeneration): Phase 5 task, regenerates packages with refined docs from Phase 4

---

## 📝 Notes

### Critical Path Items

1. **Explicit Memory List**: Infrastructure profile uses exact 6-file list (not glob patterns) to avoid errors
2. **CLAUDE.md Extraction**: May need manual section extraction if full file too large
3. **Token Size Monitoring**: Track sizes during generation, adjust exclude patterns if needed
4. **Phase 5 Regeneration**: Profiles designed for reuse in Phase 5 after doc refinement

### Known Limitations

1. **Manual Regeneration**: Phase 5 requires manual rerun (no automation yet)
2. **Token Estimation**: Uses rough 1 token ≈ 4 chars heuristic (may vary by tokenizer)
3. **IsWorkflow Classification**: Relies on examples/INDEX.md accuracy (validated in PRP-32.1.1)
4. **No RULES.md**: .ce/RULES.md does not exist (excluded by design)

### Future Enhancements (Out of Scope)

- Automated regeneration trigger on doc updates
- Token counting integration (precise vs estimated)
- Distribution automation (upload to S3/GitHub releases)
- Package versioning and changelog

---

## 🎓 Lessons Learned

*(To be filled after execution)*

---

## 📚 References

- **Repomix Documentation**: https://github.com/yamadashy/repomix
- **examples/INDEX.md**: Workflow classification source
- **Phase 32 Overview**: .tmp/batch-gen/PLAN-32-syntropy-mcp-1.1-release.md (if exists)
