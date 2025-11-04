# Migration Guide: Partial CE Installation Completion

**Scenario**: Project has incomplete Context Engineering installation (some components missing)
**Difficulty**: Easy-Medium
**Time**: ~15 minutes
**Risk**: Low (filling gaps, not replacing)

---

## Overview

This guide covers completing a partial CE framework installation where some components exist but others are missing.

**You should use this guide if**:
- Project has `.serena/` directory but missing some memories
- Project has `.claude/commands/` but not all 11 framework commands
- Project has `examples/` but missing workflow documentation
- CLAUDE.md exists but missing framework sections

**If your project has NO CE components**, see [migration-greenfield.md](migration-greenfield.md) instead.

**If your project has CE 1.0 (legacy structure)**, see [migration-existing-ce.md](migration-existing-ce.md) instead.

---

## Prerequisites

**Required**:
- Repomix CLI installed (`npm install -g repomix`)
- CE framework infrastructure package (`ce-infrastructure.xml`)
- Project with partial CE installation
- Git initialized

**Optional**:
- Backup before completion (`git branch backup-pre-completion`)

---

## Completion Steps

### Step 1: Analyze Current Installation (3 minutes)

**Check Serena Memories**:
```bash
# Count existing memories
MEMORY_COUNT=$(find .serena/memories -name "*.md" 2>/dev/null | wc -l)
echo "Existing memories: $MEMORY_COUNT (expected: 23 system + N user)"

# Check for /system/ organization (CE 1.1)
test -d .serena/memories/system && echo "✓ CE 1.1 structure" || echo "⚠ CE 1.0 structure (upgrade needed)"
```

**Check Commands**:
```bash
# Count existing commands
COMMAND_COUNT=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)
echo "Existing commands: $COMMAND_COUNT (expected: 11 framework + N user)"

# List framework commands
cat .claude/commands/*.md | grep '^#' | head -11
```

**Check Examples**:
```bash
# Check for examples directory
test -d .ce/examples && echo "✓ .ce/examples/ exists" || echo "⚠ Missing .ce/examples/"
test -d .ce/examples/system && echo "✓ CE 1.1 /system/ organization" || echo "⚠ CE 1.0 organization"

# Count examples
EXAMPLE_COUNT=$(find .ce/examples -name "*.md" 2>/dev/null | wc -l)
echo "Existing examples: $EXAMPLE_COUNT (expected: 21 system + N user)"
```

**Check CLAUDE.md**:
```bash
# Check for CLAUDE.md
test -f CLAUDE.md && echo "✓ CLAUDE.md exists" || echo "⚠ Missing CLAUDE.md"

# Check for framework sections (sample check)
grep -q "## Core Principles" CLAUDE.md && echo "✓ Framework sections present" || echo "⚠ Missing framework sections"
```

**Analysis Output Example**:
```
✓ Serena memories: 15 found (missing 8)
✓ Commands: 7 found (missing 4)
⚠ Examples: 0 found (missing 21)
✓ CLAUDE.md exists (framework sections unknown)
⚠ CE 1.0 organization (needs /system/ upgrade)
```

---

### Step 2: Extract Missing Components (5 minutes)

**Option A: Extract Specific Components** (targeted approach)

If you know what's missing, extract only those components:

```bash
# Extract infrastructure package to temp directory
mkdir -p tmp/ce-completion
npx repomix --unpack /path/to/ce-infrastructure.xml --target tmp/ce-completion/

# Copy missing memories
rsync -av tmp/ce-completion/.serena/memories/system/ .serena/memories/system/

# Copy missing commands
rsync -av tmp/ce-completion/.claude/commands/ .claude/commands/

# Copy missing examples
rsync -av tmp/ce-completion/.ce/examples/system/ .ce/examples/system/

# Cleanup temp
rm -rf tmp/ce-completion
```

**Option B: Full Re-extraction** (comprehensive approach)

If unsure what's missing, re-extract everything (existing files preserved):

```bash
# Extract infrastructure package to project root
# Note: This preserves existing files, only adds missing ones
npx repomix --unpack /path/to/ce-infrastructure.xml --target ./ --no-overwrite

# Verify /system/ structure created
ls -d .ce/examples/system .serena/memories/system
```

---

### Step 3: Validate Completion (3 minutes)

**Run Completion Checklist**:

```bash
# Serena memories (23 system + N user)
SYSTEM_MEMORIES=$(find .serena/memories/system -name "*.md" 2>/dev/null | wc -l)
test $SYSTEM_MEMORIES -eq 23 && echo "✓ All 23 system memories present" || echo "⚠ Missing $(( 23 - SYSTEM_MEMORIES )) memories"

# Commands (11 framework)
FRAMEWORK_COMMANDS=$(find .claude/commands -name "*.md" 2>/dev/null | wc -l)
test $FRAMEWORK_COMMANDS -ge 11 && echo "✓ All 11 framework commands present" || echo "⚠ Missing $(( 11 - FRAMEWORK_COMMANDS )) commands"

# Examples (21 system)
SYSTEM_EXAMPLES=$(find .ce/examples/system -name "*.md" 2>/dev/null | wc -l)
test $SYSTEM_EXAMPLES -eq 21 && echo "✓ All 21 system examples present" || echo "⚠ Missing $(( 21 - SYSTEM_EXAMPLES )) examples"

# /system/ organization
test -d .ce/examples/system && test -d .serena/memories/system && echo "✓ CE 1.1 /system/ organization" || echo "⚠ CE 1.0 organization"

# CLAUDE.md framework sections
grep -q "## Core Principles" CLAUDE.md && grep -q "## Quick Commands" CLAUDE.md && echo "✓ CLAUDE.md framework sections" || echo "⚠ Missing framework sections in CLAUDE.md"
```

**Expected Output** (all checks pass):
```
✓ All 23 system memories present
✓ All 11 framework commands present
✓ All 21 system examples present
✓ CE 1.1 /system/ organization
✓ CLAUDE.md framework sections
```

---

### Step 4: Document Installation (2 minutes)

Create PRP-0 to track completion:

```bash
# Copy PRP-0 template
cp .ce/examples/templates/PRP-0-CONTEXT-ENGINEERING.md .ce/PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Edit PRP-0 with installation details
# Fill in:
# - CE Version: 1.1
# - Installation Date: $(date +%Y-%m-%d)
# - Installation Method: Partial Completion
# - Components Added: [list of added components]
```

---

### Step 5: Commit Changes (2 minutes)

```bash
# Stage all new components
git add .serena/memories/system/
git add .claude/commands/
git add .ce/examples/system/
git add .ce/PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Commit
git commit -m "Complete partial CE 1.1 installation

- Add missing Serena memories to .serena/memories/system/
- Add missing framework commands to .claude/commands/
- Add missing framework examples to .ce/examples/system/
- Document completion in PRP-0

Components completed: [X memories, Y commands, Z examples]
Completion method: ce-infrastructure.xml extraction"

# Push (optional)
git push origin main
```

---

## Troubleshooting

### Issue: "Existing files conflict with extraction"

**Symptom**: `npx repomix --unpack` fails with "file already exists"

**Cause**: Existing files have same name as framework files

**Solution**:
```bash
# Option 1: Backup and replace
mv .serena/memories/system/conflicting-file.md .serena/memories/system/conflicting-file.md.backup
npx repomix --unpack /path/to/ce-infrastructure.xml --target ./

# Option 2: Manual merge
# Extract to temp, manually merge conflicts
mkdir tmp/ce-extraction
npx repomix --unpack /path/to/ce-infrastructure.xml --target tmp/ce-extraction/
# Manually copy non-conflicting files
```

---

### Issue: "Cannot determine what's missing"

**Symptom**: Don't know which components are incomplete

**Solution**: Compare against ce-infrastructure.xml manifest
```bash
# Extract manifest
npx repomix --unpack /path/to/ce-infrastructure.xml --target tmp/manifest-check/

# Compare directories
diff -qr .serena/memories/system/ tmp/manifest-check/.serena/memories/system/
diff -qr .claude/commands/ tmp/manifest-check/.claude/commands/
diff -qr .ce/examples/system/ tmp/manifest-check/.ce/examples/system/

# Output shows missing files:
# Only in tmp/manifest-check/.serena/memories/system/: missing-memory.md
```

---

### Issue: "CE 1.0 organization (no /system/ folders)"

**Symptom**: Memories in `.serena/memories/`, not `.serena/memories/system/`

**Solution**: Upgrade to CE 1.1 structure first
```bash
# See migration-existing-ce.md for CE 1.0 → CE 1.1 upgrade
# Then return to this guide for completion
```

---

## Success Criteria

- [ ] All 23 framework memories in `.serena/memories/system/`
- [ ] All 11 framework commands in `.claude/commands/`
- [ ] All 21 framework examples in `.ce/examples/system/`
- [ ] CLAUDE.md contains all framework sections
- [ ] CE 1.1 /system/ organization structure
- [ ] PRP-0 created in `.ce/PRPs/executed/`
- [ ] Changes committed to git

---

## Next Steps

After completing partial installation:

1. **Configure tools**: `cd tools && uv sync` (if tools/ directory exists)
2. **Test commands**: `/generate-prp`, `/execute-prp`, `/vacuum`
3. **Create first user PRP**: Document first feature/fix
4. **Add user memories**: Project-specific patterns to `.serena/memories/` (not /system/)

---

## Related Guides

- **Greenfield**: [migration-greenfield.md](migration-greenfield.md) - Start from scratch
- **Mature Project**: [migration-mature-project.md](migration-mature-project.md) - Add CE to existing code
- **Existing CE**: [migration-existing-ce.md](migration-existing-ce.md) - Upgrade CE 1.0 → CE 1.1
- **Master Guide**: [../INITIALIZATION.md](../INITIALIZATION.md) - 5-phase initialization workflow

---

**Version**: 1.0
**Last Updated**: 2025-11-04
**Part of**: Batch 32 (Syntropy MCP 1.1 Release)
