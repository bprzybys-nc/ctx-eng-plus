# Migration Guide: Existing CE Installation (Upgrade)

**Scenario**: Legacy CE installation, upgrading to CE 1.1
**Difficulty**: Complex
**Time**: ~30 minutes
**Risk**: Medium (conflict resolution required, backup mandatory)

---

## Overview

This guide covers upgrading an existing Context Engineering installation from legacy format to modern CE 1.1.

**You should use this guide if**:
- Project has `.claude/commands/` with CE commands
- Project has `.serena/memories/` or Serena integration
- CLAUDE.md exists with CE content
- PRPs/ directory with executed PRPs
- **No `.ce/` directory** (legacy structure)

**Real-world examples**:
- **certinia pattern**: 15 commands, 23 memories, 8KB settings
- **mlx-trading pattern**: 2 commands, PRPs/, examples/, no Serena

---

## Pre-Upgrade Requirements

**Mandatory**:
1. **Full backup**: Git commit or backup branch
2. **Clean working directory**: No uncommitted changes
3. **Tests passing**: Existing functionality validated
4. **Version check**: Confirm current CE version (if trackable)

```bash
# Create backup
git checkout -b pre-upgrade-backup
git add -A
git commit -m "Backup before CE 1.1 upgrade"
git push origin pre-upgrade-backup

# Return to main
git checkout main

# Or use git worktree
git worktree add ../project-ce-upgrade -b ce-upgrade
cd ../project-ce-upgrade
```

---

## Conflict Resolution Rules

### Rule 1: Commands - Framework Wins (OVERWRITE)

```bash
# Framework commands in .claude/commands/
FRAMEWORK_COMMANDS=(
  "generate-prp.md"
  "execute-prp.md"
  "batch-gen-prp.md"
  "batch-exe-prp.md"
  "vacuum.md"
  "update-context.md"
  "sync-with-syntropy.md"
)

# Backup existing commands
mkdir -p .claude/commands/.backup
for cmd in "${FRAMEWORK_COMMANDS[@]}"; do
  if [ -f ".claude/commands/$cmd" ]; then
    cp ".claude/commands/$cmd" ".claude/commands/.backup/$cmd.$(date +%Y%m%d)"
  fi
done

# Framework versions will overwrite during upgrade
# Custom commands (not in list above) are preserved
```

### Rule 2: Settings - MERGE

```bash
# Strategy: Framework defaults + Project overrides

# Backup original settings
cp .claude/settings.local.json .claude/settings.pre-upgrade.json

# Merge will combine:
# - Framework: ~80 allow patterns, ~15 ask patterns, MCP config
# - Project: Your custom patterns, overrides, additions

# After upgrade, verify merge:
jq '.bash.permissions.allow | length' .claude/settings.local.json
# Expected: ≥80 patterns (framework + your additions)
```

### Rule 3: PRPs - SEPARATE

```bash
# Legacy: PRPs/ at root with all PRPs
# Modern: .ce/PRPs/ for framework, PRPs/ for project

# Strategy:
# 1. Framework PRPs (PRP-0, templates) → .ce/PRPs/
# 2. Project PRPs (your work) → PRPs/executed/
# 3. No duplication, clear separation
```

### Rule 4: Examples - SEPARATE

```bash
# Legacy: examples/ mixed (framework + project)
# Modern: .ce/examples/ for framework, examples/ for project

# Strategy:
# 1. Classify existing examples/
# 2. Framework docs → .ce/examples/
# 3. Project docs → examples/
# 4. Update cross-references
```

### Rule 5: Memories - CLASSIFY (Add Type Headers)

```bash
# Legacy: All memories equal, no type headers
# Modern: YAML front matter with type: critical|regular|feat

# Strategy:
# 1. Add YAML headers to existing memories
# 2. Classify framework memories as type: critical
# 3. Classify project memories as type: regular
# 4. Keep all memories (no deletion during upgrade)
```

### Rule 6: CLAUDE.md - MERGE_SECTIONS

```bash
# Legacy: CLAUDE.md may be heavily customized
# Modern: CLAUDE.md with [FRAMEWORK] and [PROJECT] sections

# Strategy:
# 1. Parse existing CLAUDE.md sections
# 2. Identify framework sections (by content matching)
# 3. Identify project sections (custom content)
# 4. Merge: Update framework sections, preserve project sections
# 5. Mark sections clearly: ## [FRAMEWORK] or ## [PROJECT]
```

---

## Upgrade Steps

### Step 1: Detect Current Installation (5 minutes)

```bash
# Auto-detect installation type
cat > detect-ce.sh << 'EOF'
#!/bin/bash
HAS_COMMANDS=$([ -d .claude/commands ] && ls .claude/commands/*.md 2>/dev/null | wc -l || echo 0)
HAS_SERENA=$([ -d .serena/memories ] && ls .serena/memories/*.md 2>/dev/null | wc -l || echo 0)
HAS_PRPS=$([ -d PRPs ] && echo 1 || echo 0)
HAS_CE_DIR=$([ -d .ce ] && echo 1 || echo 0)

echo "Commands: $HAS_COMMANDS"
echo "Memories: $HAS_SERENA"
echo "PRPs: $HAS_PRPS"
echo ".ce/: $HAS_CE_DIR"

# Classify
if [ $HAS_CE_DIR -eq 1 ]; then
  echo "Type: MODERN (already CE 1.1)"
elif [ $HAS_COMMANDS -ge 10 ] && [ $HAS_SERENA -ge 15 ]; then
  echo "Type: LEGACY_FULL (certinia pattern)"
elif [ $HAS_COMMANDS -ge 1 ] && [ $HAS_PRPS -eq 1 ]; then
  echo "Type: LEGACY_MEDIUM (mlx-trading pattern)"
else
  echo "Type: PARTIAL or MINIMAL"
fi
EOF

chmod +x detect-ce.sh
./detect-ce.sh
```

### Step 2: Create Upgrade Backup (2 minutes)

```bash
# Full backup to .ce/backups/
BACKUP_DIR=".ce/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup components
cp -r .claude "$BACKUP_DIR/" 2>/dev/null || true
cp -r .serena "$BACKUP_DIR/" 2>/dev/null || true
cp -r PRPs "$BACKUP_DIR/" 2>/dev/null || true
cp -r examples "$BACKUP_DIR/" 2>/dev/null || true
cp CLAUDE.md "$BACKUP_DIR/" 2>/dev/null || true

# Create manifest
cat > "$BACKUP_DIR/MANIFEST.json" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "ce_version_before": "legacy",
  "ce_version_after": "1.1",
  "components_backed_up": [
    ".claude/",
    ".serena/",
    "PRPs/",
    "examples/",
    "CLAUDE.md"
  ]
}
EOF

echo "Backup created: $BACKUP_DIR"
```

### Step 3: Unpack CE 1.1 with Upgrade Mode (5 minutes)

```bash
# Upgrade mode: Preserves project content, updates framework
repomix --unpack /path/to/ce-workflow-docs.xml --target ./ --upgrade

# What happens:
# - Creates .ce/ (new structure)
# - Classifies existing memories (adds type: headers)
# - Merges settings (framework + project)
# - Overwrites framework commands
# - Preserves custom commands
# - Separates PRPs (framework → .ce/, project → PRPs/)
# - Separates examples (framework → .ce/, project → examples/)
```

### Step 4: Classify Memories (5 minutes)

```bash
# Add type: headers to existing memories
cd .serena/memories

for memory in *.md; do
  # Check if already has YAML header
  if ! head -n 1 "$memory" | grep -q "^---"; then
    # Determine type (heuristic)
    if grep -qi "architecture\|security\|core principle" "$memory"; then
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
created: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
updated: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
---

$(cat "$memory")
EOF
    mv "${memory}.tmp" "$memory"
  fi
done

echo "Classified $(ls *.md | wc -l) memories"
```

### Step 5: Merge Settings (3 minutes)

```bash
# Verify settings merged correctly
jq empty .claude/settings.local.json && echo "✓ Valid JSON"

# Compare before/after
echo "Before: $(jq '.bash.permissions.allow | length' .claude/settings.pre-upgrade.json)"
echo "After: $(jq '.bash.permissions.allow | length' .claude/settings.local.json)"

# Check custom settings preserved
jq '.bash.permissions.allow[]' .claude/settings.pre-upgrade.json | \
  while read -r pattern; do
    if ! jq '.bash.permissions.allow[]' .claude/settings.local.json | grep -q "$pattern"; then
      echo "⚠️  Custom pattern missing: $pattern"
    fi
  done
```

### Step 6: Create PRP-UPGRADE Record (3 minutes)

```bash
# Document the upgrade
cat > PRPs/executed/PRP-UPGRADE-1.1.md << 'EOF'
---
issue: null
prp_id: PRP-UPGRADE-1.1
phase: upgrade
status: executed
executed_at: $(date -u +%Y-%m-%dT%H:%M:%SZ)
from_version: legacy
to_version: 1.1
---

# PRP-UPGRADE: Context Engineering Framework Legacy → 1.1

## Objective
Upgrade CE framework from legacy format to modern CE 1.1 structure.

## Migration Summary

### Components Upgraded
- **Commands**: 7 framework commands updated
- **Examples**: 25 framework examples moved to .ce/
- **Memories**: $(ls .serena/memories/*.md | wc -l) memories classified with type: headers
- **Settings**: Merged (framework + project)
- **Structure**: Created .ce/ directory for framework components

### Project Content Preserved
- **PRPs**: All project PRPs in PRPs/executed/
- **Custom Commands**: Preserved in .claude/commands/
- **Project Examples**: Preserved in examples/
- **Custom Settings**: Merged into settings.local.json

## Changes in 1.1
- Memory type system (critical/regular/feat)
- Repomix-based distribution
- PRP-0 bootstrap pattern
- Enhanced validation (Level 4)
- Parallel PRP execution
- Git worktree support

## Validation Results
- ✅ Framework files installed
- ✅ Project files preserved
- ✅ Settings merged
- ✅ Memories classified
- ✅ Context drift: <10%

## Rollback
Backup: .ce/backups/$(date +%Y%m%d)_*
Command: `cp -r .ce/backups/BACKUP_DIR/* ./`
EOF
```

### Step 7: Validate Upgrade (5 minutes)

```bash
cd tools
uv sync
uv run ce validate --level 4

# Check drift
uv run ce analyze-context
# Expected: <10% (may be higher due to new framework content)

# Run your project tests
pytest  # or npm test, go test, etc.
# Expected: All tests still pass
```

---

## Validation Checklist

- [ ] Backup created in .ce/backups/
- [ ] .ce/ directory created with framework
- [ ] Framework commands updated (7 commands)
- [ ] Custom commands preserved
- [ ] Settings merged (valid JSON)
- [ ] Memories classified (all have type: headers)
- [ ] PRPs separated (.ce/PRPs/ vs PRPs/)
- [ ] Examples separated (.ce/examples/ vs examples/)
- [ ] PRP-UPGRADE record created
- [ ] Validation level 4 passes
- [ ] Project tests pass
- [ ] Context drift <15%

---

## Rollback Procedure

If upgrade fails or causes issues:

```bash
# Step 1: Identify backup
BACKUP_DIR=$(ls -dt .ce/backups/* | head -n 1)
echo "Rolling back to: $BACKUP_DIR"

# Step 2: Restore components
rm -rf .claude .serena PRPs examples CLAUDE.md
cp -r "$BACKUP_DIR/.claude" ./
cp -r "$BACKUP_DIR/.serena" ./
cp -r "$BACKUP_DIR/PRPs" ./
cp -r "$BACKUP_DIR/examples" ./
cp "$BACKUP_DIR/CLAUDE.md" ./

# Step 3: Remove .ce/
rm -rf .ce

# Step 4: Verify restoration
git status
# Check that restored files match pre-upgrade state

# Step 5: Test
pytest  # or your test command
```

---

## Post-Upgrade Tasks

### Update Documentation

```bash
# Add upgrade note to CLAUDE.md
cat >> CLAUDE.md << 'EOF'

## Framework Version

**Current**: CE 1.1
**Upgraded**: $(date -u +%Y-%m-%d)
**From**: Legacy CE format
**See**: PRPs/executed/PRP-UPGRADE-1.1.md for details
EOF
```

### Clean Up Backups

```bash
# After successful upgrade (1 week+), clean old command backups
rm -rf .claude/commands/.backup

# Keep upgrade backup in .ce/backups/ for audit trail
```

---

## Real-World Examples

### Example 1: certinia Pattern (Full Legacy)

**Before**:
- 15 commands
- 23 memories (no types)
- 8KB settings
- No .ce/

**Upgrade Steps**:
1. Backup: 15 min (large command set)
2. Unpack: 5 min
3. Classify 23 memories: 10 min
4. Merge settings: 5 min
5. Validate: 5 min

**Total**: 40 minutes

**After**:
- .ce/ created
- 22 commands (15 custom + 7 framework)
- 23 memories (6 critical, 17 regular)
- 9KB settings (merged)

### Example 2: mlx-trading Pattern (Medium Legacy)

**Before**:
- 2 commands
- 0 memories
- 198B settings
- PRPs/, examples/ exist

**Upgrade Steps**:
1. Backup: 5 min
2. Unpack: 5 min
3. Add Serena (optional): 5 min
4. Merge settings: 2 min
5. Separate examples: 3 min
6. Validate: 3 min

**Total**: 23 minutes

**After**:
- .ce/ created
- 9 commands (2 custom + 7 framework)
- 23 memories (if Serena added)
- 8KB settings

---

## Related Guides

- **Overview**: [../INITIALIZATION.md](../INITIALIZATION.md)
- **Greenfield**: [migration-greenfield.md](migration-greenfield.md)
- **Mature Project**: [migration-mature-project.md](migration-mature-project.md)
- **Partial CE**: [migration-partial-ce.md](migration-partial-ce.md)

---

**Critical**: Always create backup before upgrade. Rollback mechanism tested and documented above.
