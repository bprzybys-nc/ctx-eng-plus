# CE Blend Command - Usage Examples

**Command**: `ce blend`
**Purpose**: Merge CE framework files with target project files using intelligent blending strategies
**PRP**: PRP-34 (Blending Framework)

---

## Overview

The `blend` command implements a 4-phase pipeline to merge Context Engineering framework with target project customizations:

1. **DETECT**: Scan target project for existing CE files
2. **CLASSIFY**: Validate CE patterns and file structure
3. **BLEND**: Apply domain-specific merge strategies
4. **CLEANUP**: Remove legacy directories after migration

---

## Basic Usage

### Blend All Domains

```bash
cd tools
uv run ce blend --all
```

Blends all 6 domains: PRPs, examples, CLAUDE.md, settings, commands, memories

### Blend Specific Domain

```bash
# Blend only CLAUDE.md
uv run ce blend --claude-md

# Blend only memories
uv run ce blend --memories

# Blend multiple domains
uv run ce blend --settings --commands
```

### Target Different Project

```bash
# Blend into different project directory
uv run ce blend --all --target-dir ~/projects/my-app

# With custom config
uv run ce blend --all --target-dir ~/projects/my-app --config ~/.ce/custom-blend-config.yml
```

---

## Common Scenarios

### Scenario 1: Initial Framework Installation

**Goal**: Install CE framework in new project

```bash
cd tools
uv run ce blend --all --target-dir ~/projects/new-project

# Expected output:
# 🔀 Running Phase: DETECT
# ✓ Detected 0 files (new installation)
# 🔀 Running Phase: BLEND
# ✓ Blending complete (6 domains processed)
```

**Result**: Framework files copied to target project

---

### Scenario 2: Update Existing Installation

**Goal**: Update CE framework in project with customizations

```bash
cd tools
uv run ce blend --all --target-dir ~/projects/existing-project

# Expected output:
# 🔀 Running Phase: DETECT
# ✓ Detected 134 files across 6 domains
# 🔀 Running Phase: CLASSIFY
# ✓ Classified 128 valid files
# 🔀 Running Phase: BLEND
#   Blending claude_md (1 files)...
#   ✓ Merged 5 sections, preserved 3 custom sections
#   Blending memories (24 files)...
#   ✓ Merged 23 framework + 5 user memories
# ✓ Blending complete
```

**Result**: Framework updated, user customizations preserved

---

### Scenario 3: Re-blend After Framework Changes

**Goal**: Re-apply blending after updating memories/examples

```bash
# 1. Update framework files
vim .serena/memories/new-pattern.md

# 2. Rebuild packages
.ce/build-and-distribute.sh

# 3. Re-blend
cd tools
uv run ce blend --all
```

---

## Domain-Specific Blending

### CLAUDE.md Blending

**Strategy**: Section-level merge with Sonnet LLM

```bash
uv run ce blend --claude-md

# Behavior:
# - Detects framework sections (## Communication, ## Core Principles)
# - Detects user sections (## Project-Specific Notes)
# - Merges overlapping sections using Sonnet
# - Preserves user-only sections verbatim
```

**Example Output**:
```
Blending claude_md (1 files)...
  ✓ Merged section: Core Principles (framework + user changes)
  ✓ Preserved section: Project-Specific Notes (user only)
  ✓ Added section: New Framework Section
```

---

### Memories Blending

**Strategy**: YAML header merge + Haiku similarity check

```bash
uv run ce blend --memories

# Behavior:
# - Merges YAML headers (tags, categories)
# - Checks content similarity with Haiku
# - Merges if >80% similar, keeps separate otherwise
# - Preserves user memories (type: user)
```

**Example Output**:
```
Blending memories (24 files)...
  ✓ Merged: code-style-conventions.md (framework + user tags)
  ✓ Kept separate: my-project-patterns.md (user only)
  ✓ 23 framework + 5 user memories = 28 total
```

---

### Settings Blending

**Strategy**: JSON deep merge with conflict resolution

```bash
uv run ce blend --settings

# Behavior:
# - Deep merges .claude/settings.local.json
# - Preserves user customizations
# - Adds new framework keys
# - Conflict resolution: user value wins
```

**Example**:
```json
// Framework: {"allow": ["Bash(git:*)"]}
// User: {"allow": ["Bash(npm:*)"], "custom_key": "value"}
// Result: {"allow": ["Bash(git:*)", "Bash(npm:*)"], "custom_key": "value"}
```

---

### Examples Blending

**Strategy**: Semantic deduplication with natural language similarity

```bash
uv run ce blend --examples

# Behavior:
# - Compares examples by content similarity (not filename)
# - Deduplicates if >85% similar
# - Preserves both if semantically different
```

---

## Advanced Usage

### Dry Run Mode

```bash
# See what would be blended without executing
uv run ce blend --all --dry-run

# Output shows planned actions:
# [DRY-RUN] Would blend:
#   - CLAUDE.md: 5 sections to merge
#   - memories: 23 framework + 5 user
#   - settings: 12 keys to add
```

### Verbose Output

```bash
# See detailed blending decisions
uv run ce blend --all --verbose

# Shows:
# - File-by-file processing
# - Similarity scores
# - Merge decisions
# - Conflict resolutions
```

### Custom Configuration

```bash
# Use custom blend config
uv run ce blend --all --config ~/.ce/my-blend-config.yml
```

**Config Structure** (`.ce/blend-config.yml`):
```yaml
strategies:
  claude_md:
    model: sonnet
    temperature: 0.3
  memories:
    similarity_threshold: 0.8
  examples:
    dedupe_threshold: 0.85
```

---

## Troubleshooting

### Issue: "Config file not found"

```bash
# Error: Config file not found: .ce/blend-config.yml

# Solution: Copy default config
cp ~/ctx-eng-plus/.ce/blend-config.yml .ce/
```

---

### Issue: "Cannot cleanup PRPs/: 87 unmigrated files"

```bash
# Error during cleanup phase

# Cause: Old PRPs not yet migrated to .ce/PRPs/
# Solution: Run migration or skip cleanup
uv run ce blend --all --skip-cleanup
```

---

### Issue: "LLM call failed"

```bash
# Error: Anthropic API error

# Cause: Missing ANTHROPIC_API_KEY
# Solution: Set environment variable
export ANTHROPIC_API_KEY=your-key-here
uv run ce blend --all
```

---

## Integration with Other Commands

### With init-project

```bash
# init-project automatically calls blend
uv run ce init-project ~/projects/target

# Internally runs:
# 1. Extract framework files
# 2. uv run ce blend --all --target-dir ~/projects/target
# 3. Initialize Python environment
# 4. Verify installation
```

### With update-context

```bash
# After updating memories, blend automatically triggers
uv run ce update-context

# If framework files changed:
# 1. Updates context sync
# 2. Rebuilds repomix packages
# 3. Auto-blends (if configured)
```

---

## Best Practices

### 1. Always Use --all for Initial Setup

```bash
# ✅ Good: Blend all domains at once
uv run ce blend --all

# ❌ Avoid: Blending domains piecemeal
uv run ce blend --claude-md
uv run ce blend --memories
# ... (easy to miss domains)
```

### 2. Backup Before Major Updates

```bash
# Before major framework update
cp -r .ce .ce.backup
uv run ce blend --all

# Rollback if needed
rm -rf .ce
mv .ce.backup .ce
```

### 3. Use Dry Run First

```bash
# See impact before committing
uv run ce blend --all --dry-run

# Review output, then execute
uv run ce blend --all
```

### 4. Review Merged Sections

```bash
# After blending CLAUDE.md
git diff CLAUDE.md

# Check for:
# - Preserved custom sections
# - Correct merge of overlapping sections
# - No lost user content
```

---

## Exit Codes

- `0`: Blend successful
- `1`: Blend failed (check error output)
- `2`: Cleanup failed (partial success)

---

## Related Commands

- `ce init-project` - Full framework initialization (includes blend)
- `ce update-context` - Auto-triggers blend if framework files changed
- `ce vacuum` - Cleanup temporary blend artifacts

---

## See Also

- [INITIALIZATION.md](INITIALIZATION.md) - Full CE framework setup guide
- [PRP-34-INITIAL.md](../PRPs/feature-requests/PRP-34-INITIAL.md) - Blend tool design
- `.ce/blend-config.yml` - Blend configuration reference
