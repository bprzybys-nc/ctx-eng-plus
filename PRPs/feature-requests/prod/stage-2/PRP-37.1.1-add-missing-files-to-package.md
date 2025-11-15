---
prp_id: PRP-37.1.1
feature_name: Add Missing Files to Package
status: pending
created: 2025-11-06T00:00:00Z
updated: 2025-11-06T00:00:00Z
complexity: low
estimated_hours: 1.0
dependencies: []
batch_id: 37
stage: stage-1-sequential
execution_order: 1
merge_order: 1
conflict_potential: low
---

# Add Missing Files to Package

## 1. TL;DR

**Objective**: Include blend-config.yml and README.md in ce-infrastructure.xml package

**What**: Add two missing files to the repomix profile so they're included in the infrastructure package during framework initialization

**Why**: E2E testing revealed that .ce/blend-config.yml and tools/README.md are required during initialization but not present in the package, forcing manual workarounds

**Effort**: 1 hour

**Dependencies**: None (foundation phase)

## 2. Context

### Background

From PRP-36.3 E2E testing of the init-project flow, two files were found missing from the ce-infrastructure.xml package:

1. **`.ce/blend-config.yml`**: Blending configuration file that defines rules for merging framework and user files (settings, CLAUDE.md, memories, examples, PRPs, commands). Required by Phase 4 (Blending) of initialization.

2. **`tools/README.md`**: CLI tools documentation that explains all ce commands, validation gates, context management, and development workflows. Should be extracted to `.ce/tools/README.md` in target projects.

Currently, both files exist in the ctx-eng-plus repository but are not included in the repomix-profile-infrastructure.yml configuration, causing them to be omitted from the package build.

### Current State

**Repomix Profile** (`.ce/repomix-profile-infrastructure.yml`):
- Includes: PRP-0 template, 23 framework memories + README, 11 commands, tool source code (ce/*.py), CLAUDE.md
- Missing: blend-config.yml, tools/README.md

**Build Script** (`.ce/build-and-distribute.sh`):
- Regenerates both packages (workflow + infrastructure)
- Validates sizes and copies to syntropy-mcp boilerplate

### Constraints and Considerations

**File Paths in Target Projects**:
- Source (ctx-eng-plus): `.ce/blend-config.yml`, `tools/README.md`
- Extracted (target project): `.ce/blend-config.yml`, `.ce/tools/README.md`
- Repomix preserves directory structure relative to profile location

**Package Size Impact**:
- Current infrastructure package: ~206KB
- blend-config.yml: ~2KB (83 lines)
- tools/README.md: ~10KB (459 lines)
- New total: ~218KB (well under 300KB combined limit)

**Blending Strategy Usage**:
The blend-config.yml file defines 6 domain strategies:
1. Settings (rule-based merge)
2. CLAUDE.md (NL-blend with Sonnet)
3. Memories (NL-blend with Haiku+Sonnet)
4. Examples (dedupe-copy with Haiku)
5. PRPs (move-all with hash dedupe)
6. Commands (overwrite)

### Documentation References

**Related Files**:
- `.ce/repomix-profile-infrastructure.yml` - Package configuration
- `.ce/blend-config.yml` - Blending rules (to be included)
- `tools/README.md` - CLI documentation (to be included)
- `.ce/build-and-distribute.sh` - Build script
- `examples/INITIALIZATION.md` - Complete CE 1.1 initialization guide

**Related PRPs**:
- PRP-34: Implement blend tool and strategies
- PRP-36.3: Fix Init-Project Issues from E2E Testing (parent)

## 3. Implementation Steps

### Phase 1: Update Repomix Profile (15 min)

**File**: `.ce/repomix-profile-infrastructure.yml`

**Action**: Add missing files to include section

**Location**: After CLAUDE.md section (line 68), add:

```yaml
  # Blending Configuration -> .ce/
  - ".ce/blend-config.yml"

  # Tool Documentation -> tools/ (extracted to .ce/tools/ in target project)
  - "tools/README.md"
```

**Validation**:
```bash
# Verify YAML syntax
cat .ce/repomix-profile-infrastructure.yml | grep -A2 "blend-config"
cat .ce/repomix-profile-infrastructure.yml | grep -A2 "tools/README.md"
```

### Phase 2: Verify Files Exist (5 min)

**Check files are present**:
```bash
# Both should exist in ctx-eng-plus
ls -lh .ce/blend-config.yml
ls -lh tools/README.md
```

**Expected output**:
- `.ce/blend-config.yml`: ~2KB, 83 lines
- `tools/README.md`: ~10KB, 459 lines

### Phase 3: Rebuild Packages (15 min)

**Run build script**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
.ce/build-and-distribute.sh
```

**Expected output**:
```
🔨 Regenerating CE framework packages...
✅ Packages regenerated
📊 Package sizes:
  Workflow: ~85KB
  Infrastructure: ~218KB (increased from ~206KB)
  Total: ~303KB
```

**Validation**:
```bash
# Verify files present in XML
npx repomix --config .ce/repomix-profile-infrastructure.yml --unpack ce-32/builds/ce-infrastructure.xml --list | grep -E "(blend-config|README)"
```

Expected matches:
- `.ce/blend-config.yml`
- `tools/README.md`

### Phase 4: Test Package Extraction (15 min)

**Create test directory**:
```bash
mkdir -p .tmp/package-test
cd .tmp/package-test
```

**Extract package**:
```bash
npx repomix --unpack ../../ce-32/builds/ce-infrastructure.xml --target extracted/
```

**Verify files extracted**:
```bash
ls -lh extracted/.ce/blend-config.yml
ls -lh extracted/tools/README.md
```

**Cleanup**:
```bash
cd ../..
rm -rf .tmp/package-test
```

### Phase 5: Update Distribution (10 min)

**Verify syntropy-mcp distribution** (if available):
```bash
# Script already copies to ../syntropy-mcp/boilerplate/ce-framework/
# Verify files present there
ls -lh ../syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
```

**If syntropy-mcp not available**:
- Build script will skip distribution with warning
- Manual distribution required when syncing with syntropy-mcp repo

## 4. Validation Gates

### Gate 1: Repomix Profile Updated
**Command**:
```bash
grep -E "(blend-config|tools/README)" .ce/repomix-profile-infrastructure.yml
```

**Expected output**:
```
  - ".ce/blend-config.yml"
  - "tools/README.md"
```

**Success criteria**: Both files present in include section

### Gate 2: Files Exist in Repository
**Command**:
```bash
ls -lh .ce/blend-config.yml tools/README.md
```

**Expected output**:
```
-rw-r--r--  1 user  staff   2.0K  .ce/blend-config.yml
-rw-r--r--  1 user  staff   10K   tools/README.md
```

**Success criteria**: Both files exist with expected sizes

### Gate 3: Packages Rebuilt Successfully
**Command**:
```bash
.ce/build-and-distribute.sh
```

**Expected output**:
```
✅ Packages regenerated
📊 Package sizes:
  Infrastructure: ~218KB
```

**Success criteria**: Build completes without errors, infrastructure size increased by ~12KB

### Gate 4: Files Present in XML Package
**Command**:
```bash
npx repomix --config .ce/repomix-profile-infrastructure.yml --unpack ce-32/builds/ce-infrastructure.xml --list | grep -E "(blend-config|README)"
```

**Expected output**:
```
.ce/blend-config.yml
tools/README.md
```

**Success criteria**: Both files listed in package contents

### Gate 5: E2E Test Runs Without Workarounds
**Command**:
```bash
cd tools
uv run pytest tests/test_e2e_init_project.py -v
```

**Expected result**: Test passes without manual file copying workarounds

**Success criteria**: No manual file operations needed during initialization

## 5. Testing Strategy

### Test Framework
pytest (existing test suite)

### Test Command
```bash
cd tools
uv run pytest tests/test_e2e_init_project.py -v
```

### Test Cases

**Unit Tests** (new):
```python
# tests/test_repomix_profile.py
def test_blend_config_in_profile():
    """Verify blend-config.yml listed in repomix profile"""
    profile = yaml.safe_load(open(".ce/repomix-profile-infrastructure.yml"))
    assert ".ce/blend-config.yml" in profile["include"]

def test_tools_readme_in_profile():
    """Verify tools/README.md listed in repomix profile"""
    profile = yaml.safe_load(open(".ce/repomix-profile-infrastructure.yml"))
    assert "tools/README.md" in profile["include"]
```

**Integration Tests** (existing):
```python
# tests/test_e2e_init_project.py (updated)
def test_blend_config_extracted():
    """Phase 3: Verify blend-config.yml extracted"""
    assert (target_dir / ".ce" / "blend-config.yml").exists()

def test_tools_readme_extracted():
    """Phase 3: Verify tools/README.md extracted"""
    assert (target_dir / ".ce" / "tools" / "README.md").exists()
```

### Coverage Target
- Unit tests: 100% (2 new tests)
- Integration: Covered by existing E2E test

### Test Data
- Real repomix profile: `.ce/repomix-profile-infrastructure.yml`
- Real config file: `.ce/blend-config.yml`
- Real README: `tools/README.md`

## 6. Rollout Plan

### Phase 1: Development (1 hour)
1. Update repomix profile (15 min)
2. Rebuild packages (15 min)
3. Verify extraction (15 min)
4. Add unit tests (15 min)

### Phase 2: Review (15 min)
- Manual review of package contents
- Verify no unintended files included
- Check package size within limits

### Phase 3: Deployment (5 min)
- Commit changes to main branch
- Distribute to syntropy-mcp (if available)
- Update E2E test to verify files present

### Rollback Plan
If package becomes corrupted:
1. Revert changes to repomix profile
2. Rebuild packages with `build-and-distribute.sh`
3. Re-run validation gates

### Monitoring
- Package size (should be ~218KB)
- E2E test success rate
- Initialization errors in target projects

### Risks & Mitigations

**Risk 1: YAML Parsing Errors**
- **Description**: Invalid YAML syntax in repomix profile breaks package build
- **Mitigation**: Validate YAML with `cat .ce/repomix-profile-infrastructure.yml | grep -A2 "blend-config"` before rebuild
- **Likelihood**: Low (simple file path additions)

**Risk 2: File Not Found During Build**
- **Description**: Listed files don't exist at specified paths
- **Mitigation**: Verify files exist with `ls -lh .ce/blend-config.yml tools/README.md` before updating profile
- **Likelihood**: Low (files already exist in repo)

**Risk 3: Package Size Exceeds Limit**
- **Description**: Combined package size >300KB (workflow + infrastructure)
- **Mitigation**: Monitor size during build (~218KB + 85KB = 303KB, within limit)
- **Likelihood**: Low (only +12KB added)

**Risk 4: Distribution Failures**
- **Description**: Copy to syntropy-mcp fails if directory doesn't exist
- **Mitigation**: Build script checks for ../syntropy-mcp/ and skips gracefully with warning
- **Likelihood**: Medium (syntropy-mcp may not be cloned)

**Risk 5: Package Extraction Errors**
- **Description**: Files not extracted correctly in target projects
- **Mitigation**: Gate 4 validates with `repomix --list`, E2E test verifies extraction
- **Likelihood**: Low (repomix handles directory structure)

---

## Research Findings

### Package Structure Analysis

**Current Infrastructure Package** (ce-infrastructure.xml):
- PRP-0 template (1 file)
- Framework memories (24 files: 23 memories + README)
- Commands (11 files)
- Tool source code (6 files: ce/*.py)
- pyproject.toml + bootstrap.sh (2 files)
- CLAUDE.md (1 file)
- **Total**: 45 files, ~206KB

**After This PRP**:
- All above files
- blend-config.yml (1 file, ~2KB)
- tools/README.md (1 file, ~10KB)
- **Total**: 47 files, ~218KB

### Extraction Behavior

Repomix preserves directory structure:
- Source: `tools/README.md` → Extracted: `tools/README.md`
- Init script moves to: `.ce/tools/README.md`

### Blending Configuration Content

The blend-config.yml defines:
1. **6 domain strategies**: settings, claude_md, memories, examples, prps, commands
2. **LLM models**: Sonnet for quality (CLAUDE.md, memories merge), Haiku for speed (similarity checks, deduplication)
3. **Backup behavior**: Enabled for settings, CLAUDE.md, memories, commands
4. **Conflict resolution**: Ask user for memory conflicts
5. **Global settings**: Legacy directory handling, standard locations

This configuration is critical for Phase 4 (Blending) of the initialization workflow.

---

**Batch Context**: Part of PRP-36.3 fix for init-project issues. This is stage-1-sequential (foundation phase) with no dependencies or conflicts. Enables subsequent stages by providing required configuration files.
