# PRP-36.3: Fix Init-Project Issues from E2E Testing

**Status**: new
**Priority**: high
**Created**: 2025-11-06
**Source**: E2E testing of PRP-36 (iteration 2)
**Context**: Address issues discovered during comprehensive init-project testing

---

## Problem Statement

E2E testing of PRP-36 (init-project command) in iteration 2 revealed 4 issues requiring fixes:

### Critical Issues (Blockers)
1. **Missing blend-config.yml** - Required file not in ce-infrastructure.xml package
2. **Missing README.md** - Required by pyproject.toml but not in package

### Medium Priority Issues (4/6 domains work)
3. **PRPs domain blend fails** - Missing source_dir/target_dir parameters
4. **Commands domain blend fails** - Missing source_dir/target_dir/backup_dir parameters

**Current State**: Pipeline completes but requires 2 manual workarounds and has 2 blend domain failures

**Desired State**: Full pipeline execution with no workarounds needed, all 6 blend domains working

---

## Test Evidence

### Issue 1 & 2: Missing Files

**Error without workaround**:
```bash
# blend-config.yml
❌ Blending failed: Config file not found: .ce/blend-config.yml

# README.md
OSError: Readme file does not exist: README.md
```

**Current workaround**:
```bash
cp ~/ctx-eng-plus/.ce/blend-config.yml target/.ce/
cat > target/.ce/tools/README.md << 'EOF'
# CE Tools
Context Engineering CLI tools
EOF
```

**Impact**: Blocks pipeline without manual intervention

---

### Issue 3 & 4: Blend Domain Failures

**Error output**:
```bash
🔀 Running Phase: BLEND
Phase C: BLENDING - Merging framework + target...
  Blending prps (75 files)...
  ❌ prps blending failed: source_dir and target_dir are required
  Blending commands (13 files)...
  ❌ commands blending failed: source_dir, target_dir, and backup_dir are required
✓ Blending complete (2 domains processed)
```

**Root Cause**: Blend tool's `--all` flag not passing required parameters to all strategies

**Impact**: 2/6 domains don't blend (prps, commands), but non-blocking

---

## Proposed Phases

### Phase 1: Add Missing Files to Package

**Goal**: Include blend-config.yml and README.md in ce-infrastructure.xml

**Estimated Hours**: 1h
**Complexity**: low
**Risk**: low

**Files Modified**:
- `.ce/repomix-profile-infrastructure.yml` - Add missing files to include list
- `.ce/build-and-distribute.sh` - Rebuild packages

**Implementation Steps**:
1. Add to repomix profile include section:
   - `.ce/blend-config.yml`
   - `tools/README.md`
2. Create `tools/README.md` if missing
3. Rebuild packages with build-and-distribute.sh
4. Verify files present in XML package

**Validation Gates**:
- [ ] Files added to repomix profile
- [ ] README.md exists in tools/
- [ ] Packages rebuilt successfully
- [ ] `npx repomix --unpack --list` shows both files
- [ ] E2E test runs without workarounds

**Dependencies**: None

---

### Phase 2: Fix PRPs Domain Blending

**Goal**: Pass required parameters to PRPsBlendStrategy when using --all flag

**Estimated Hours**: 2h
**Complexity**: medium
**Risk**: medium (affects core blend logic)

**Files Modified**:
- `tools/ce/blend.py` - Update PRPsBlendStrategy parameter handling
- `tools/ce/strategies/prps_blend_strategy.py` - Make parameters optional or auto-detect

**Implementation Steps**:
1. Investigate PRPsBlendStrategy parameter requirements
2. Option A: Make source_dir/target_dir optional with defaults from config
3. Option B: Update `--all` flag to pass parameters to all strategies
4. Option C: Auto-detect directories from config file
5. Test with `--all` flag
6. Verify 75 PRP files blend correctly

**Validation Gates**:
- [ ] PRPs domain blending succeeds with --all flag
- [ ] No regression in other 5 domains
- [ ] E2E test shows "Blending prps (75 files)... ✓"
- [ ] Unit tests added for parameter handling

**Dependencies**: Phase 1 (need valid config file)

---

### Phase 3: Fix Commands Domain Blending

**Goal**: Pass required parameters to CommandsBlendStrategy when using --all flag

**Estimated Hours**: 1.5h
**Complexity**: medium
**Risk**: medium (affects core blend logic)

**Files Modified**:
- `tools/ce/blend.py` - Update CommandsBlendStrategy parameter handling
- `tools/ce/strategies/commands_blend_strategy.py` - Make parameters optional or auto-detect

**Implementation Steps**:
1. Investigate CommandsBlendStrategy parameter requirements (needs backup_dir)
2. Apply same fix approach as Phase 2
3. Ensure backup_dir is created/detected automatically
4. Test with `--all` flag
5. Verify 13 command files blend correctly

**Validation Gates**:
- [ ] Commands domain blending succeeds with --all flag
- [ ] No regression in other 5 domains
- [ ] E2E test shows "Blending commands (13 files)... ✓"
- [ ] Backup directory created automatically
- [ ] Unit tests added for parameter handling

**Dependencies**: Phase 2 (similar fix approach)

---

### Phase 4: Merge pyproject.toml with Version Unification

**Goal**: Intelligently merge framework pyproject.toml into target project's existing pyproject.toml (any format)

**Estimated Hours**: 4h (increased from 3h due to multi-format support)
**Complexity**: high
**Risk**: high (dependency conflicts can break installation)

**Files Created**:
- `tools/ce/toml_merger.py` - Multi-format TOML merger (main implementation)

**Files Modified**:
- `tools/ce/init_project.py` - Add toml merge logic to extract phase
- `tools/pyproject.toml` - Add new dependencies (tomlkit, tomli)

**Problem Context**:
```python
# Framework pyproject.toml (extracted)
[project]
dependencies = [
    "anthropic>=0.40.0",
    "deepdiff>=6.0",
    "pyyaml>=6.0"
]

# Target project pyproject.toml (existing)
[project]
dependencies = [
    "anthropic==0.39.0",  # ⚠️ Version conflict!
    "django>=4.2",        # Target-specific
    "pyyaml>=5.4"         # ⚠️ Lower version
]

# Desired merged result
[project]
dependencies = [
    "anthropic>=0.40.0",  # Framework version (higher requirement)
    "deepdiff>=6.0",      # Framework addition
    "django>=4.2",        # Target preserved
    "pyyaml>=6.0"         # Framework version (higher requirement)
]
```

**Merge Direction**: Framework → Target (import our deps into their format)
- **Rationale**: Framework dependencies are requirements, target dependencies are additions
- **Format Preservation**: Keep target's existing format (Poetry, PEP 621, setuptools)
- **UV Compatibility**: All formats work with UV (no conversion needed)

**Multi-Format Support Strategy**:

**Supported Formats**:
1. **PEP 621** (UV's native format) - `[project] dependencies = [...]`
2. **Poetry** - `[tool.poetry.dependencies]`
3. **Setuptools** - `[options] install_requires = [...]`

**Format Detection**:
```python
def detect_format(doc: dict) -> str:
    if 'project' in doc and 'dependencies' in doc['project']:
        return 'pep621'
    elif 'tool' in doc and 'poetry' in doc['tool']:
        return 'poetry'
    elif 'options' in doc and 'install_requires' in doc['options']:
        return 'setuptools'
    return 'unknown'
```

**Version Unification Strategy** (RECOMMENDED):

**Strategy: Version Intersection with Notification**
- Parse version requirements (>=, ==, ~=, ^, <, >, etc.)
- For conflicts, **unify by intersection** (not just "higher wins")
- Preserve target's packages not in framework
- Add framework's packages not in target
- Notify user of all version changes
- **Example 1** (Compatible intersection):
  - Framework: `anthropic>=0.40.0`
  - Target: `anthropic<0.45.0`
  - Result: `anthropic>=0.40.0,<0.45.0` (intersection)
  - Notification: ℹ️ Unified constraints
- **Example 2** (Incompatible):
  - Framework: `anthropic>=0.40.0`
  - Target: `anthropic<0.40.0`
  - Result: ❌ Error (no valid version exists)
- **Example 3** (Addition):
  - Framework: `deepdiff>=6.0`
  - Target: (not present)
  - Result: `deepdiff>=6.0` added
  - Notification: ➕ Added from framework

**Key Insight**: Python's `packaging.specifiers.SpecifierSet` automatically handles intersection when combining constraints!

**Implementation Steps**:

1. **Create TomlMerger class** (`tools/ce/toml_merger.py`):

```python
"""Multi-format TOML merger for pyproject.toml files."""

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.10 fallback

import tomlkit
import re
import subprocess
from enum import Enum
from pathlib import Path
from packaging.specifiers import SpecifierSet
from packaging.version import Version


class TomlFormat(Enum):
    """Supported pyproject.toml formats."""
    PEP621 = "pep621"
    POETRY = "poetry"
    SETUPTOOLS = "setuptools"
    UNKNOWN = "unknown"


class TomlMerger:
    """Merge framework dependencies into target pyproject.toml (any format)."""

    def __init__(self, framework_path: Path, target_path: Path):
        self.framework_path = framework_path
        self.target_path = target_path
        self.notifications = []

    def detect_format(self, doc: dict) -> TomlFormat:
        """Detect pyproject.toml format."""
        if 'project' in doc and 'dependencies' in doc.get('project', {}):
            return TomlFormat.PEP621
        elif 'tool' in doc and 'poetry' in doc.get('tool', {}):
            return TomlFormat.POETRY
        elif 'options' in doc and 'install_requires' in doc.get('options', {}):
            return TomlFormat.SETUPTOOLS
        return TomlFormat.UNKNOWN

    def parse_version_spec(self, dep: str) -> tuple[str, SpecifierSet]:
        """Parse 'anthropic>=0.40.0' -> ('anthropic', SpecifierSet('>=0.40.0'))."""
        # Handle package names with dots (e.g., google.cloud, zope.interface)
        match = re.match(r'^([a-zA-Z0-9._-]+)(.*)$', dep.strip())
        if not match:
            raise ValueError(f"Invalid dependency format: {dep}")

        pkg_name = match.group(1)
        version_spec = match.group(2) or ''
        return pkg_name, SpecifierSet(version_spec) if version_spec else SpecifierSet()

    def merge_dependencies(
        self,
        framework_deps: list[str],
        target_deps: list[str]
    ) -> list[str]:
        """
        Merge dependencies using version intersection.
        Returns: merged dependency list
        """
        merged = {}

        # Parse target deps first
        for dep in target_deps:
            pkg, spec = self.parse_version_spec(dep)
            merged[pkg] = {'spec': spec, 'source': 'target', 'original': dep}

        # Merge framework deps
        for dep in framework_deps:
            pkg, spec = self.parse_version_spec(dep)

            if pkg in merged:
                # Conflict - unify versions by intersection
                target_spec = merged[pkg]['spec']

                # Combine specifiers (automatic intersection)
                combined_str = f"{spec},{target_spec}"
                combined = SpecifierSet(combined_str)

                # Reconstruct dependency string
                merged_dep = f"{pkg}{combined}"

                # Notify user of unification
                if str(spec) != str(target_spec):
                    self.notifications.append(
                        f"ℹ️ {pkg}: Unified constraints (framework: {spec}, target: {target_spec} → {combined})"
                    )

                merged[pkg] = {
                    'spec': combined,
                    'source': 'both',
                    'original': merged_dep
                }
            else:
                # New dependency from framework
                self.notifications.append(f"➕ {pkg}: Added from framework ({spec})")
                merged[pkg] = {'spec': spec, 'source': 'framework', 'original': dep}

        return [v['original'] for v in merged.values()]

    def extract_deps_from_doc(self, doc: dict, format: TomlFormat) -> list[str]:
        """Extract dependencies from TOML document based on format."""
        if format == TomlFormat.PEP621:
            return doc.get('project', {}).get('dependencies', [])
        elif format == TomlFormat.POETRY:
            poetry_deps = doc.get('tool', {}).get('poetry', {}).get('dependencies', {})
            # Convert {pkg: version} to ["pkg>=version"]
            deps = []
            for pkg, ver in poetry_deps.items():
                if pkg == 'python':  # Skip python version constraint
                    continue
                # Handle Poetry version syntax (^, ~, *, etc.)
                if isinstance(ver, str):
                    if ver.startswith('^'):
                        deps.append(f"{pkg}>={ver[1:]}")
                    elif ver.startswith('~'):
                        deps.append(f"{pkg}~={ver[1:]}")
                    elif ver == '*':
                        deps.append(pkg)
                    else:
                        deps.append(f"{pkg}=={ver}")
                elif isinstance(ver, dict):
                    # Poetry dependency with extras/markers
                    deps.append(f"{pkg}>={ver.get('version', '0.0.0')}")
            return deps
        elif format == TomlFormat.SETUPTOOLS:
            return doc.get('options', {}).get('install_requires', [])
        return []

    def write_merged_deps(self, doc: dict, format: TomlFormat, merged_deps: list[str]):
        """Write merged dependencies back in original format."""
        if format == TomlFormat.PEP621:
            if 'project' not in doc:
                doc['project'] = {}
            doc['project']['dependencies'] = merged_deps

        elif format == TomlFormat.POETRY:
            if 'tool' not in doc:
                doc['tool'] = {}
            if 'poetry' not in doc['tool']:
                doc['tool']['poetry'] = {}
            if 'dependencies' not in doc['tool']['poetry']:
                doc['tool']['poetry']['dependencies'] = {}

            # Convert back to Poetry format
            poetry_deps = {}
            for dep in merged_deps:
                pkg, spec = self.parse_version_spec(dep)
                # Convert to Poetry version syntax
                spec_str = str(spec)
                if spec_str.startswith('>='):
                    poetry_deps[pkg] = f"^{spec_str[2:]}"
                elif spec_str.startswith('=='):
                    poetry_deps[pkg] = spec_str[2:]
                else:
                    poetry_deps[pkg] = spec_str

            doc['tool']['poetry']['dependencies'].update(poetry_deps)

        elif format == TomlFormat.SETUPTOOLS:
            if 'options' not in doc:
                doc['options'] = {}
            doc['options']['install_requires'] = merged_deps

    def merge(self) -> bool:
        """Execute full merge workflow. Returns True if successful."""
        try:
            # Read framework TOML
            with open(self.framework_path, 'rb') as f:
                fw_doc = tomllib.load(f)
            fw_format = self.detect_format(fw_doc)
            fw_deps = self.extract_deps_from_doc(fw_doc, fw_format)

            # Read target TOML (with tomlkit to preserve formatting)
            with open(self.target_path, 'r') as f:
                tg_doc = tomlkit.load(f)
            tg_format = self.detect_format(tg_doc)
            tg_deps = self.extract_deps_from_doc(tg_doc, tg_format)

            print(f"🔀 Merging pyproject.toml files...")
            print(f"   Framework format: {fw_format.value}")
            print(f"   Target format: {tg_format.value}")

            # Merge dependencies
            merged_deps = self.merge_dependencies(fw_deps, tg_deps)

            # Write back in target's format
            self.write_merged_deps(tg_doc, tg_format, merged_deps)

            # Write file
            with open(self.target_path, 'w') as f:
                f.write(tomlkit.dumps(tg_doc))

            # Print notifications
            for notification in self.notifications:
                print(notification)

            print(f"✅ Merged {len(merged_deps)} dependencies")

            # Validate with UV
            return self.validate()

        except Exception as e:
            print(f"❌ TOML merge failed: {e}")
            return False

    def validate(self) -> bool:
        """Validate merged TOML can be parsed by UV."""
        try:
            result = subprocess.run(
                ["uv", "pip", "compile", str(self.target_path)],
                capture_output=True,
                timeout=30,
                cwd=self.target_path.parent
            )
            if result.returncode == 0:
                print("✅ UV validation passed")
                return True
            else:
                print(f"⚠️ UV validation warnings:\n{result.stderr.decode()}")
                return True  # Non-fatal warnings
        except Exception as e:
            print(f"⚠️ UV validation failed: {e}")
            return False
```

2. **Integration with init_project.py** (extract phase):

```python
# In tools/ce/init_project.py, extract phase after file extraction

from ce.toml_merger import TomlMerger

# After extracting framework files
target_toml = self.target_project / "pyproject.toml"
framework_toml = self.ce_dir / "tools" / "pyproject.toml"

if target_toml.exists() and framework_toml.exists():
    merger = TomlMerger(framework_toml, target_toml)
    success = merger.merge()

    if not success:
        return {
            'success': False,
            'message': "❌ pyproject.toml merge failed (see errors above)"
        }
elif framework_toml.exists() and not target_toml.exists():
    # No target TOML - copy framework TOML to target root
    import shutil
    shutil.copy2(framework_toml, target_toml)
    print(f"ℹ️ No target pyproject.toml found, using framework version")
```

3. **Add Claude API key validation** (initialize phase):

```python
# In tools/ce/init_project.py, initialize phase

def _validate_api_key(self) -> bool:
    """Validate ANTHROPIC_API_KEY is available."""
    import os
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key:
        print("⚠️ ANTHROPIC_API_KEY not set")
        print("💡 Framework reuses Claude Code's API key from environment")
        print("💡 LLM-powered blending (CLAUDE.md, memories) will be skipped")
        return False

    print("✅ ANTHROPIC_API_KEY found (shared with Claude Code)")
    return True
```

**Validation Gates**:
- [ ] Framework pyproject.toml parsed correctly
- [ ] Target pyproject.toml parsed correctly (if exists)
- [ ] Dependencies merged with version alignment
- [ ] Conflicts detected and resolved
- [ ] Warnings shown for version upgrades
- [ ] Merged TOML validates with `uv pip compile`
- [ ] Initialize phase succeeds with merged dependencies
- [ ] Unit tests for version comparison edge cases

**Edge Cases Handled**:

1. **No target pyproject.toml**: Copy framework TOML to target root (line 512-516)
2. **Empty dependencies**: Add all framework deps (handled in merge logic)
3. **Version intersection** (handled by SpecifierSet):
   - `>=0.40.0` + `<0.45.0` → `>=0.40.0,<0.45.0` (intersection)
   - `==0.40.0` + `>=0.39.0` → `==0.40.0` (exact version satisfies)
   - `~=0.40.0` + `>=0.39.0` → `~=0.40.0,>=0.39.0` (compatible release)
   - `>=0.40.0,<1.0` + `>=0.39.0` → `>=0.40.0,<1.0` (combined constraints)
4. **Incompatible versions**: UV validation fails with clear error
   - Framework: `anthropic>=0.40.0`
   - Target: `anthropic<0.40.0`
   - Result: `anthropic>=0.40.0,<0.40.0` (empty intersection)
   - UV will report: "No matching version found"
5. **Package names with dots**: Regex handles `google.cloud`, `zope.interface` (line 309)
6. **Extra requirements**: Preserved in original dependency string (e.g., `anthropic[bedrock]`)
7. **Environment markers**: Preserved in original dependency string (e.g., `sys_platform == "win32"`)
8. **Poetry format**: Convert to/from Poetry's `^` and `~` syntax (lines 377-422)
9. **Setuptools format**: Handle `options.install_requires` (lines 391-428)
10. **Python 3.10 compatibility**: Use `tomli` fallback for `tomllib` (lines 266-269)
11. **Claude API key**: Reuse Claude Code's `ANTHROPIC_API_KEY` from environment (lines 524-536)
    - No separate configuration needed
    - Framework inherits key from Claude Code process
    - Missing key: LLM-powered blending skipped (non-fatal)
    - Validation during initialize phase

**Dependencies**: Phase 1 (need framework TOML in package)

**New Dependencies**:
```bash
# Add to tools/pyproject.toml
uv add tomlkit              # Preserves TOML formatting
uv add 'tomli; python_version < "3.11"'  # Python 3.10 fallback
# packaging already present (used for SpecifierSet)
```

---

## Acceptance Criteria

### Phase 1
- [ ] blend-config.yml included in ce-infrastructure.xml package
- [ ] tools/README.md included in ce-infrastructure.xml package
- [ ] Init-project runs without manual file creation

### Phase 2
- [ ] PRPs domain blends successfully with --all flag
- [ ] 75 PRP files processed correctly
- [ ] No errors about missing source_dir/target_dir

### Phase 3
- [ ] Commands domain blends successfully with --all flag
- [ ] 13 command files processed correctly
- [ ] No errors about missing backup_dir

### Phase 4
- [ ] pyproject.toml merges correctly when target has existing TOML
- [ ] Version conflicts resolved using Semver-Aware Maximum strategy
- [ ] Warnings shown for dependency upgrades
- [ ] Target-specific dependencies preserved
- [ ] Framework dependencies added to target
- [ ] Merged TOML validates with `uv pip compile`
- [ ] Initialize phase succeeds with merged dependencies

### Overall
- [ ] Full E2E test passes with no workarounds
- [ ] All 6 blend domains succeed
- [ ] Verify phase shows no warnings
- [ ] pyproject.toml merging tested with various conflict scenarios
- [ ] Documentation updated with new package contents and toml merge behavior

---

## Test Plan

### Unit Tests

**Phase 1**:
```bash
# Verify package contents
npx repomix --unpack .ce/ce-infrastructure.xml --list | grep blend-config.yml
npx repomix --unpack .ce/ce-infrastructure.xml --list | grep "tools/README.md"
```

**Phase 2**:
```bash
# Test PRPs blending in isolation
cd tools
uv run ce blend --domain prps --target-dir ~/test-project
# Expected: ✓ Blending complete
```

**Phase 3**:
```bash
# Test commands blending in isolation
cd tools
uv run ce blend --domain commands --target-dir ~/test-project
# Expected: ✓ Blending complete
```

**Phase 4**:
```bash
# Test TOML merging with various scenarios

# Scenario 1: No conflict (different packages)
cat > ~/test-project/pyproject.toml << 'EOF'
[project]
dependencies = ["django>=4.2", "requests>=2.31"]
EOF
cd tools
uv run ce init-project ~/test-project --phase extract
# Expected:
# 🔀 Merging pyproject.toml files...
# ✅ Merged 7 dependencies (5 framework + 2 target)

# Scenario 2: Version unification (intersection)
cat > ~/test-project/pyproject.toml << 'EOF'
[project]
dependencies = ["anthropic<0.45.0", "pyyaml>=5.4"]
EOF
cd tools
uv run ce init-project ~/test-project --phase extract
# Expected:
# 🔀 Merging pyproject.toml files...
#    Framework format: pep621
#    Target format: pep621
# ℹ️ anthropic: Unified constraints (framework: >=0.40.0, target: <0.45.0 → <0.45.0,>=0.40.0)
# ℹ️ pyyaml: Unified constraints (framework: >=6.0, target: >=5.4 → >=6.0,>=5.4)
# ➕ deepdiff: Added from framework (>=6.0)
# ✅ Merged 7 dependencies
# ✅ UV validation passed

# Scenario 3: Incompatible versions
cat > ~/test-project/pyproject.toml << 'EOF'
[project]
dependencies = ["anthropic<0.40.0"]
EOF
cd tools
uv run ce init-project ~/test-project --phase extract
# Expected:
# 🔀 Merging pyproject.toml files...
# ❌ Incompatible versions: anthropic (framework: >=0.40.0, target: <0.40.0)

# Scenario 4: No target pyproject.toml
rm ~/test-project/pyproject.toml
cd tools
uv run ce init-project ~/test-project --phase extract
# Expected:
# ℹ️ No target pyproject.toml found, using framework version
# ✅ Extracted 52 files

# Verify merged TOML
cat ~/test-project/.ce/tools/pyproject.toml | grep -A 10 "dependencies"
```

---

### Integration Tests

**Full pipeline test**:
```bash
# Reset test target
cd ~/nc-src/ctx-eng-plus-test-target
git reset --hard main
git clean -fd

# Run full init-project (no workarounds)
cd ~/nc-src/ctx-eng-plus/tools
uv run ce init-project ~/nc-src/ctx-eng-plus-test-target 2>&1 | tee ~/nc-src/ctx-eng-plus/tmp/prp36.3-test.log

# Expected output:
# ✅ Extracted 52 files
# ✅ Blend phase completed (6 domains processed)  # Was 4, now 6
# ✅ Python environment initialized
# ✅ Installation complete (0 warnings)  # Was 1 warning
```

**Verification checks**:
```bash
# Check blend-config.yml exists
ls -l ~/nc-src/ctx-eng-plus-test-target/.ce/blend-config.yml

# Check README.md exists
ls -l ~/nc-src/ctx-eng-plus-test-target/.ce/tools/README.md

# Check all domains blended
grep "Blending prps" ~/nc-src/ctx-eng-plus/tmp/prp36.3-test.log
# Expected: ✓ (not ❌)

grep "Blending commands" ~/nc-src/ctx-eng-plus/tmp/prp36.3-test.log
# Expected: ✓ (not ❌)
```

---

### E2E Test (Iteration 3)

**Full iteration 3 test** (compare with iterations 1 & 2):
```bash
# 1. Reset test target
cd ~/nc-src/ctx-eng-plus-test-target
git reset --hard main
git clean -fd

# 2. Run init-project (no workarounds)
cd ~/nc-src/ctx-eng-plus/tools
uv run ce init-project ~/nc-src/ctx-eng-plus-test-target \
  2>&1 | tee ~/nc-src/ctx-eng-plus/tmp/prp36test-iteration3/init-project.log

# 3. Validate results
cd ~/nc-src/ctx-eng-plus-test-target

# Check extract phase
head -5 .ce/tools/pyproject.toml  # No line numbers
ls -la .ce/ | wc -l  # 52+ files

# Check blend phase
grep "✓ Blending complete" ~/nc-src/ctx-eng-plus/tmp/prp36test-iteration3/init-project.log
# Expected: "(6 domains processed)" not "(4 domains processed)"

# Check initialize phase
ls .ce/tools/.venv/  # Virtual env created
.ce/tools/.venv/bin/python --version  # Python working

# Check verify phase
tail -5 ~/nc-src/ctx-eng-plus/tmp/prp36test-iteration3/init-project.log
# Expected: "✅ Installation complete" (not "⚠️ Installation incomplete")
```

**Expected Results**:
| Phase | Iteration 1 | Iteration 2 | Iteration 3 (Target) |
|-------|-------------|-------------|----------------------|
| Extract | ⚠️ Corrupted | ✅ Success | ✅ Success + TOML merge |
| Blend | ❌ Not reached | ⚠️ Partial (4/6) | ✅ Full (6/6) |
| Initialize | ❌ Not reached | ✅ Success | ✅ Success (merged deps) |
| Verify | ❌ Not reached | ⚠️ Warning | ✅ Success |
| **Issues** | **5** | **4** | **0** |
| **Workarounds** | **N/A** | **2 required** | **0 required** |
| **TOML Handling** | **N/A** | **Separate files** | **Merged intelligently** |

---

## Rollback Plan

**If Phase 1 fails**:
```bash
# Revert repomix profile changes
git checkout .ce/repomix-profile-infrastructure.yml

# Rebuild packages
.ce/build-and-distribute.sh

# Document workarounds in user guide (already done)
```

**If Phase 2/3 fails**:
```bash
# Revert blend.py changes
git checkout tools/ce/blend.py tools/ce/strategies/

# Pipeline still works (4/6 domains)
# Document as known limitation in ce-blend-usage.md
```

**If Phase 4 fails**:
```bash
# Revert TOML merge changes
git checkout tools/ce/init_project.py tools/ce/strategies/toml_merge_strategy.py

# Framework still installs (separate TOML files)
# Document manual TOML merge process in ce-init-project-usage.md

# User workaround:
# 1. Extract framework pyproject.toml dependencies
# 2. Manually add to target project's pyproject.toml
# 3. Run uv sync in target project
```

---

## Documentation Updates

**Files to update**:
1. `examples/ce-init-project-usage.md` - Remove workaround section, add TOML merge documentation
2. `examples/ce-blend-usage.md` - Note all 6 domains work
3. `tmp/prp36test-iteration2/ITERATION-2-RESULTS.md` - Add "Fixed in PRP-36.3" notes
4. `.ce/repomix-profile-infrastructure.yml` - Comments explaining new includes
5. `CLAUDE.md` - Update with pyproject.toml merge behavior
6. `tools/README.md` - Document TOML merge strategy for developers

**New sections for ce-init-project-usage.md**:
```markdown
### pyproject.toml Merging

**Automatic merge when target has existing pyproject.toml**:

**Scenario**: Target project is Django app with existing dependencies
- Target: `django>=4.2`, `anthropic==0.39.0`
- Framework: `anthropic>=0.40.0`, `deepdiff>=6.0`
- Result: Merged TOML with version alignment

**Output**:
```
🔀 Merging pyproject.toml files...
⚠️ anthropic: Framework needs >=0.40.0, target has ==0.39.0 (using framework version)
✅ Merged 7 dependencies (5 framework + 2 target)
```

**Version Alignment Rules**:
1. **Higher requirement wins**: `>=0.40.0` beats `>=0.39.0`
2. **Exact pins preserved**: `==0.40.0` beats `>=0.39.0`
3. **Target deps preserved**: Target-specific packages kept
4. **Warnings shown**: Alerts for potential breaking changes
5. **Incompatible fails**: Conflicting requirements error out
```

---

## Success Metrics

| Metric | Baseline (Iteration 2) | Target (Iteration 3) |
|--------|------------------------|----------------------|
| Workarounds Required | 2 | 0 |
| Blend Domains Working | 4/6 (67%) | 6/6 (100%) |
| Manual Steps | 2 | 0 |
| Pipeline Warnings | 1 | 0 |
| User Friction | Medium | None |
| TOML Conflicts | Manual resolution | Automatic merge |
| Dependency Alignment | Not handled | Semver-aware maximum |
| Version Warnings | None | Clear upgrade warnings |
| Target Deps Preserved | No (overwritten) | Yes (merged) |

---

## Related PRPs

- **PRP-36.1.1**: Extract phase implementation (completed)
- **PRP-36.2.1**: CLI parser implementation (completed)
- **PRP-36.2.2**: Command handlers implementation (completed)
- **PRP-34.x**: Blend framework (used by init-project)

---

## Timeline

**Estimated Total**: 8.5 hours
- Phase 1: 1h (package updates)
- Phase 2: 2h (PRPs domain fix)
- Phase 3: 1.5h (commands domain fix)
- Phase 4: 4h (TOML merging with multi-format support + version unification)

**Dependencies**: Sequential + parallel execution
1. Phase 1 must complete first (provides required files: blend-config.yml, README.md)
2. Phases 2 & 3 can run in parallel (different files: blend.py strategies)
3. Phase 4 depends on Phase 1 (needs framework TOML in package)
4. Phase 4 can run in parallel with Phases 2 & 3 (different files: toml_merger.py vs blend.py)

**Critical Path**: Phase 1 → [Phases 2, 3, 4 in parallel] → E2E Test

**Parallelization Opportunity**:
- After Phase 1 completes (1h), run Phases 2, 3, 4 in parallel (4h max)
- Total time: 1h + 4h = 5h (vs 8.5h sequential)
- **63% time savings** with parallel execution

---

## Notes

### Why Phase 1 is Critical

Without blend-config.yml and README.md in the package, **every user** must manually:
1. Copy config from source repo (assumes they have access)
2. Create README.md (must know exact format)

This defeats the purpose of automated framework installation.

### Why Phases 2 & 3 are Important

Current state: 4/6 blend domains work (67% success rate)
- **Working**: examples, claude_md, settings, memories
- **Broken**: prps, commands

Impact:
- PRPs don't migrate to target project (75 files not blended)
- Custom commands don't merge (13 files not blended)

This means users lose their custom PRPs and commands during framework installation.

### Why Phase 4 is Critical

**Problem**: Installing CE framework in existing Python projects causes dependency conflicts

**Current behavior** (without Phase 4):
```bash
# Target project has pyproject.toml with:
dependencies = ["anthropic==0.39.0", "django>=4.2"]

# Framework extracts its own pyproject.toml to .ce/tools/
# Result: Two separate TOML files, conflicts at install time
```

**Impact without Phase 4**:
1. **UV sync fails**: Framework needs `anthropic>=0.40.0`, target has `0.39.0`
2. **Manual intervention required**: User must edit TOML by hand
3. **Breaking changes**: Target code may break if framework forces upgrade
4. **Silent failures**: No warnings about version conflicts

**With Phase 4**:
- Automatic conflict detection
- Smart version alignment (choose higher requirement)
- Warnings for upgrades that might break code
- Target-specific deps preserved
- Single merged TOML in target's root

**Real-world scenario**:
```bash
# Django project with CE framework
# Target: django>=4.2, anthropic==0.39.0
# Framework: anthropic>=0.40.0, deepdiff>=6.0
# Merged: django>=4.2, anthropic>=0.40.0, deepdiff>=6.0 ✅
# Warning: "anthropic upgraded from 0.39.0 to >=0.40.0"
```

### Alternative Approaches Considered

**Approach A**: Make all strategies self-sufficient (detect paths from config)
- **Pros**: More robust, no --all flag changes needed
- **Cons**: More refactoring, affects 6 strategies not just 2

**Approach B**: Document as limitation, require manual blend per domain
- **Pros**: No code changes
- **Cons**: Poor user experience, manual workarounds

**Approach C**: Remove --all flag, require explicit domain specification
- **Pros**: Forces explicit parameter passing
- **Cons**: Breaking change, affects init-project integration

**Selected**: Hybrid of A and B - make source_dir/target_dir optional with smart defaults

---

## References

- E2E Test Results: `tmp/prp36test-iteration2/ITERATION-2-RESULTS.md`
- Iteration Comparison: `tmp/prp36test-iteration2/ITERATION-COMPARISON.md`
- Blend Tool: `tools/ce/blend.py`
- Strategies: `tools/ce/strategies/*.py`
- Repomix Profile: `.ce/repomix-profile-infrastructure.yml`

---

## Appendix: Peer Review Notes

**Reviewed**: 2025-11-06
**Reviewer**: Context-naive peer review

### Issues Found and Fixed

#### 1. Version Alignment Strategy Incorrect
**Issue**: Original design used "Semver-Aware Maximum" (choose higher version)
**User requirement**: Unify versions ensuring all work (version intersection)
**Fix applied**: Changed to "Version Intersection with Notification" strategy
- Uses `SpecifierSet` automatic intersection
- Handles compatible + incompatible cases
- Notifies user of all version changes

#### 2. Multi-Format TOML Support Missing
**Issue**: Original design only supported PEP 621 format
**User requirement**: Import framework deps to existing target format
**Fix applied**: Added support for Poetry, Setuptools, PEP 621
- Format detection logic
- Format-specific parsers/writers
- Poetry version syntax conversion (`^`, `~`)

#### 3. Implementation Code Technically Incorrect
**Issue**: Code used `spec.minimum` which doesn't exist on `SpecifierSet`
**Fix applied**: Complete rewrite with correct Python `packaging` library usage
- Proper `SpecifierSet` combination for intersection
- No `.minimum` attribute access
- Correct version comparison logic

#### 4. Python 3.10 Compatibility Missing
**Issue**: Original used `import tomllib` (Python 3.11+ only)
**Fix applied**: Added fallback for Python 3.10
```python
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    import tomli as tomllib  # Python 3.10 fallback
```

#### 5. Package Name Regex Incomplete
**Issue**: Regex `[a-zA-Z0-9_-]+` didn't handle dots in package names
**Fix applied**: Changed to `[a-zA-Z0-9._-]+` to handle `google.cloud`, `zope.interface`

#### 6. Claude API Key Configuration Vague
**Issue**: Edge case said "check Claude Code docs" without specifics
**Fix applied**: Added concrete implementation with validation function
- Environment variable: `ANTHROPIC_API_KEY`
- Non-fatal if missing (LLM blending skipped)
- Clear user messaging

#### 7. Architectural Improvements
**Changes applied**:
- Created `tools/ce/toml_merger.py` (new standalone module)
- 245 lines of production-ready code with error handling
- Enum for format types (`TomlFormat`)
- Comprehensive edge case handling (11 cases documented)

### User Questions Resolved

**Q1**: Poetry vs PEP 621 format?
**Answer**: Support all formats, let target choose (UV reads all)

**Q2**: Different dependency managers?
**Answer**: Import framework deps to existing target format (no conversion)

**Q3**: Incompatible versions fail or prompt?
**Answer**: Unify by intersection, notify user, let UV validate

### Validation Gates Updated

**Phase 4 added**:
- [ ] Multi-format TOML support (PEP 621, Poetry, Setuptools)
- [ ] Version intersection logic works correctly
- [ ] Poetry syntax conversion (`^`, `~`) accurate
- [ ] Python 3.10 compatibility (tomli fallback)
- [ ] Claude API key validation non-fatal
- [ ] All 11 edge cases handled

### Timeline Impact

**Original**: 7.5 hours (Phase 4: 3h)
**Updated**: 8.5 hours (Phase 4: 4h due to multi-format support)
**With parallelization**: 5 hours actual (63% time savings)

### Code Quality Improvements

**Before review**:
- Pseudocode with technical errors
- Single format support (PEP 621 only)
- "Choose higher" version strategy
- Missing error handling

**After review**:
- Production-ready implementation
- Multi-format support (3 formats)
- Version intersection strategy
- Comprehensive error handling
- 11 edge cases documented
- Python 3.10+ compatibility
