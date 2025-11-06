# CE Init-Project Command - Usage Examples

**Command**: `ce init-project`
**Purpose**: Initialize CE Framework in target project with 4-phase pipeline
**PRP**: PRP-36 (Project Initializer)

---

## Overview

The `init-project` command automates complete CE framework installation using a 4-phase pipeline:

1. **EXTRACT**: Unpack framework files from ce-infrastructure.xml
2. **BLEND**: Merge framework + user customizations
3. **INITIALIZE**: Install Python dependencies with uv
4. **VERIFY**: Validate installation and report status

---

## Basic Usage

### Initialize Current Directory

```bash
cd tools
uv run ce init-project ~/projects/my-app
```

### With Dry Run

```bash
# See what would be done without executing
uv run ce init-project ~/projects/my-app --dry-run

# Output shows planned actions:
# [DRY-RUN] Extract: Would extract 52 files
# [DRY-RUN] Blend: Would run ce blend --all
# [DRY-RUN] Initialize: Would run uv sync
# [DRY-RUN] Verify: Would check installation
```

---

## Common Scenarios

### Scenario 1: Fresh Project Setup (Greenfield)

**Goal**: Install CE framework in new project with no existing .ce/

```bash
cd tools
uv run ce init-project ~/projects/new-app

# Expected output:
# ============================================================
# Phase: extract
# ============================================================
# ✅ Extracted 52 files to /Users/you/projects/new-app/.ce
#
# ============================================================
# Phase: blend
# ============================================================
# ✅ Blend phase completed
#
# ============================================================
# Phase: initialize
# ============================================================
# ✅ Python environment initialized (.ce/tools/.venv created)
#
# ============================================================
# Phase: verify
# ============================================================
# ✅ Installation complete
```

**Result**: Full CE framework installed and ready to use

---

### Scenario 2: Existing .ce/ Directory

**Goal**: Upgrade CE framework without losing customizations

```bash
cd tools
uv run ce init-project ~/projects/existing-app

# Expected output:
# ============================================================
# Phase: extract
# ============================================================
# ℹ️  Renamed existing .ce/ to .ce.old/
# 💡 .ce.old/ will be included as additional context source during blend
# ✅ Extracted 52 files to /Users/you/projects/existing-app/.ce
#
# ============================================================
# Phase: blend
# ============================================================
# ✅ Blend phase completed
# 💡 Note: .ce.old/ detected - blend tool will include it as additional source
```

**Result**:
- Old `.ce/` preserved as `.ce.old/`
- New framework extracted
- Blend merges `.ce.old/` customizations with new framework

---

### Scenario 3: Phase-Specific Execution

**Goal**: Run only specific phase (e.g., re-blend after manual changes)

```bash
# Run only extract phase
uv run ce init-project ~/projects/app --phase extract

# Run only blend phase
uv run ce init-project ~/projects/app --phase blend

# Run only initialize phase
uv run ce init-project ~/projects/app --phase initialize

# Run only verify phase
uv run ce init-project ~/projects/app --phase verify
```

**Use Cases**:
- `--phase extract`: Re-extract after framework update
- `--phase blend`: Re-blend after editing .ce.old/ files
- `--phase initialize`: Reinstall Python deps after adding packages
- `--phase verify`: Quick health check

---

### Scenario 4: Blend-Only Mode (Re-initialization)

**Goal**: Skip extraction, only re-blend existing files

```bash
# You already have .ce/ directory with framework files
# Just want to re-blend with customizations
uv run ce init-project ~/projects/app --blend-only

# Skips: extract, initialize phases
# Runs: blend, verify phases
```

**Use Case**: After manually editing framework files in `.ce/`, want to re-merge with target project

---

## Phase Details

### Phase 1: Extract

**What it does**:
1. Checks for ce-infrastructure.xml package
2. Renames existing `.ce/` → `.ce.old/` (if exists)
3. Extracts 52 framework files to `.ce/`
4. Reorganizes: `tools/` → `.ce/tools/`
5. Copies ce-workflow-docs.xml reference package

**Files Extracted**:
- System directories: `.serena/memories/`, `.claude/commands/`, `examples/`
- Tool files: `.ce/tools/ce/*.py`, `pyproject.toml`, `bootstrap.sh`
- Config files: `.claude/settings.local.json`, `.ce/config.yml`

**Output Example**:
```
✅ Extracted 52 files to /Users/you/projects/app/.ce

Directory structure:
  .ce/
  ├── PRPs/
  ├── tools/ce/
  ├── tools/pyproject.toml
  └── .serena/memories/
```

---

### Phase 2: Blend

**What it does**:
1. Runs `ce blend --all --target-dir <target>`
2. Merges framework files with target project
3. Includes `.ce.old/` as additional source (if exists)
4. Applies domain-specific strategies

**Blended Domains**:
- CLAUDE.md: Section-level merge
- Memories: YAML + content merge
- Examples: Semantic deduplication
- Settings: JSON deep merge
- Commands: File-level merge
- PRPs: Migration to `.ce/PRPs/`

**Output Example**:
```
✅ Blend phase completed
💡 Note: .ce.old/ detected - blend tool will include it as additional source

Blended:
  - CLAUDE.md: 5 sections merged
  - memories: 23 framework + 5 user
  - settings: 12 keys added
```

---

### Phase 3: Initialize

**What it does**:
1. Navigates to `.ce/tools/`
2. Runs `uv sync` to install Python dependencies
3. Creates `.venv` virtual environment
4. Installs ce-tools package in editable mode

**Dependencies Installed** (from `pyproject.toml`):
- anthropic>=0.40.0
- deepdiff>=6.0
- jsonschema>=4.25.1
- python-frontmatter>=1.1.0
- pyyaml>=6.0

**Output Example**:
```
✅ Python environment initialized (.ce/tools/.venv created)

Installed packages:
  - anthropic 0.40.0
  - deepdiff 6.0
  - pyyaml 6.0
  ... (8 packages total)
```

---

### Phase 4: Verify

**What it does**:
1. Checks critical files exist
2. Validates JSON files (settings.local.json)
3. Verifies Python environment
4. Reports installation summary

**Verification Checks**:
- ✅ `.ce/tools/` exists
- ✅ `.venv/` created
- ✅ `ce` command available
- ✅ Critical memories present
- ✅ settings.local.json valid JSON

**Output Example**:
```
✅ Installation complete

Summary:
  Framework files: 52
  Python packages: 8
  Commands available: 15
  Memories loaded: 28
```

---

## Advanced Usage

### Custom Package Location

If ce-infrastructure.xml is in non-standard location:

```bash
# init-project expects packages in ctx-eng-plus/.ce/
# If in different location, copy first:
cp ~/custom-location/*.xml ~/ctx-eng-plus/.ce/
uv run ce init-project ~/projects/app
```

---

### Handling Existing .ce.old/

If you already have `.ce.old/` from previous run:

```bash
# Old .ce.old/ will be deleted automatically
# New .ce/ → .ce.old/, then fresh extract
uv run ce init-project ~/projects/app

# To preserve multiple backups:
mv .ce.old .ce.backup-$(date +%Y%m%d)
uv run ce init-project ~/projects/app
```

---

### Troubleshooting Failed Phases

If a phase fails, you can re-run from that point:

```bash
# Example: Blend failed due to missing config
# Fix: Add config file
cp ~/ctx-eng-plus/.ce/blend-config.yml .ce/

# Re-run from blend phase
uv run ce init-project ~/projects/app --phase blend

# Or continue with full pipeline
uv run ce init-project ~/projects/app
```

---

## Integration with Other Commands

### Before init-project: Build Packages

```bash
# Ensure you have latest framework packages
cd ~/ctx-eng-plus
.ce/build-and-distribute.sh

# Verify packages exist
ls -lh .ce/*.xml

# Now run init-project
cd tools
uv run ce init-project ~/projects/app
```

---

### After init-project: Verify Installation

```bash
# Navigate to target project
cd ~/projects/app

# Verify ce command works
cd .ce/tools
uv run ce --help

# Check framework files
ls -la ~/.ce/PRPs/
ls -la ~/.ce/.serena/memories/
```

---

### With Git Workflow

```bash
# Initialize project on feature branch
git checkout -b feature/add-ce-framework
cd tools
uv run ce init-project ~/projects/app

# Review changes in target project
cd ~/projects/app
git status
git diff CLAUDE.md

# Commit framework installation
git add .ce/ CLAUDE.md .serena/ .claude/
git commit -m "Add CE framework via init-project"
```

---

## Error Handling

### Error 1: Missing XML Packages

```
❌ ce-infrastructure.xml not found at /Users/you/ctx-eng-plus/.ce/ce-infrastructure.xml
🔧 Ensure you're running from ctx-eng-plus repo root
```

**Solution**:
```bash
cd ~/ctx-eng-plus
.ce/build-and-distribute.sh
cp ce-32/builds/*.xml .ce/
```

---

### Error 2: Blend Config Not Found

```
❌ Blending failed: Config file not found: .ce/blend-config.yml
🔧 Create .ce/blend-config.yml (see PRP-34.1.1)
```

**Solution**:
```bash
# In target project
cp ~/ctx-eng-plus/.ce/blend-config.yml .ce/
uv run ce init-project . --phase blend
```

---

### Error 3: UV Not Installed

```
❌ uv not found in PATH
🔧 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Solution**:
```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Retry initialize
uv run ce init-project ~/projects/app --phase initialize
```

---

### Error 4: Corrupted Extracted Files

```
❌ UV sync failed (exit code 2)
TOML parse error at line 1, column 5
  1 |  1: [project]
```

**Cause**: Line numbers not stripped during extraction (fixed in latest version)

**Solution**:
```bash
# Update to latest ctx-eng-plus (includes fix)
cd ~/ctx-eng-plus
git pull

# Re-extract
uv run ce init-project ~/projects/app --phase extract
```

---

## Best Practices

### 1. Always Run from ctx-eng-plus/tools/

```bash
# ✅ Good: Run from tools/ directory
cd ~/ctx-eng-plus/tools
uv run ce init-project ~/projects/app

# ❌ Avoid: Running from other locations
cd ~/projects/app
uv run ce init-project .  # May not find packages
```

---

### 2. Use Dry Run for First Time

```bash
# See what will happen before committing
uv run ce init-project ~/projects/app --dry-run

# Review output, then execute
uv run ce init-project ~/projects/app
```

---

### 3. Commit .ce.old/ for Rollback

```bash
# Before major upgrade
cd ~/projects/app
git add .ce.old/
git commit -m "Backup CE before upgrade"

# Now upgrade
uv run ce init-project . --phase all

# Rollback if needed
git checkout HEAD~1 -- .ce.old/
```

---

### 4. Verify After Each Phase

```bash
# Run phase by phase with verification
uv run ce init-project ~/projects/app --phase extract
ls -la ~/projects/app/.ce/  # Check files

uv run ce init-project ~/projects/app --phase blend
git diff ~/projects/app/CLAUDE.md  # Check merge

uv run ce init-project ~/projects/app --phase initialize
source ~/projects/app/.ce/tools/.venv/bin/activate
which ce  # Check command

uv run ce init-project ~/projects/app --phase verify
# Final check
```

---

## Exit Codes

- `0`: All phases successful
- `1`: User error (invalid directory, missing files)
- `2`: Initialization error (phase failed)

---

## Performance

**Timing** (typical project):
- Extract: ~5 seconds (52 files)
- Blend: ~30 seconds (6 domains)
- Initialize: ~20 seconds (8 packages)
- Verify: ~2 seconds

**Total**: ~1 minute for full initialization

---

## Related Commands

- `ce blend` - Manual blending (called by init-project)
- `ce update-context` - Updates context after installation
- `ce validate` - Validates installed framework

---

## See Also

- [INITIALIZATION.md](INITIALIZATION.md) - Complete CE setup guide (manual process)
- [ce-blend-usage.md](ce-blend-usage.md) - Blend command details
- [PRP-36-INITIAL.md](../PRPs/feature-requests/PRP-36-INITIAL.md) - Init-project design
- `tmp/prp36test/PRP-36-TEST-SUMMARY.md` - E2E test results and known issues
