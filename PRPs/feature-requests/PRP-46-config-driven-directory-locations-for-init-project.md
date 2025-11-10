---
prp_id: PRP-46
feature_name: Config-Driven Directory Locations for init-project
status: pending
created: 2025-11-08T19:21:56.271715
updated: 2025-11-08T19:30:00.000000
complexity: medium
estimated_hours: 4-6
dependencies: blend-config.yml, detection.py, 6 blending strategies
issue: TBD
---

# Config-Driven Directory Locations for init-project

## 🎯 Goal (GOLD Framework)

**G**oal: Eliminate all hardcoded directory paths from init-project codebase (16 files) by centralizing location decisions in `blend-config.yml`.

**O**utput:
- New config loader module (`tools/ce/config_loader.py`) with typed path access
- Updated `blend-config.yml` with `directories` section (3 subsections: output, framework, legacy)
- 16 Python files refactored to read paths from config (zero hardcoded strings)

**L**imits:
- **IN scope**: tools/ce/blending/* and tools/ce/init_project.py only
- **OUT of scope**: Changing directory structure itself (only making it configurable)
- **Time budget**: 4-6 hours
- **Test coverage**: 80%+ for config_loader.py

**D**ata: See "Current Architecture" section below for existing code structure

**E**valuation: See "Validation Gates" section (4 gates with copy-paste commands)

---

## 1. TL;DR

**Problem**: init-project creates `.claude/` at project root instead of user's preferred location because directory paths are hardcoded in 16+ files. Bug discovered in PRP-41 iteration testing.

**Solution**: Add `directories` section to `blend-config.yml` defining all paths. Create `config_loader.py` module. Refactor all 16 files to read from config instead of hardcoded strings.

**Why**: Single source of truth for directory locations enables users to customize structure (e.g., `.claude/` at root vs `.ce/.claude/`) without code changes.

**Effort**: Medium (4-6 hours) - Config loader (1h) + 16 file refactors (3h) + tests (2h)

**Dependencies**:
- `blend-config.yml` (exists)
- `pyyaml` (already in dependencies)
- `pathlib` (Python stdlib)

---

## 2. Context

### Current Architecture

**Problem Root Cause**: Directory paths hardcoded in 16 files:

**Example 1**: `tools/ce/blending/detection.py:14-21`
```python
# ❌ HARDCODED PATHS
SEARCH_PATTERNS = {
    "prps": ["PRPs/", "context-engineering/PRPs/"],
    "examples": ["examples/", "context-engineering/examples/"],
    "claude_md": ["CLAUDE.md"],
    "settings": [".claude/settings.local.json"],      # HARDCODED
    "commands": [".claude/commands/"],                # HARDCODED
    "memories": [".serena/memories/"]                 # HARDCODED
}
```

**Example 2**: `tools/ce/blending/core.py` (lines vary)
```python
# Multiple references like:
framework_dir = project_root / ".ce" / ".serena" / "memories"  # HARDCODED
output_dir = project_root / ".serena" / "memories"             # HARDCODED
```

**Impact**: User wants `.claude/` at root, but code creates it at `.ce/.claude/` (or vice versa).

### Desired Architecture

**blend-config.yml** - Add new `directories` section:

```yaml
# Domain configurations (existing, unchanged)
domains:
  settings:
    strategy: rule-based
    # ... existing config ...

  # ... other domains ...

# NEW: Directory configuration (single source of truth)
directories:
  # Output locations (where blended content goes in target project)
  output:
    claude_dir: .claude/                  # Commands + settings (configurable!)
    claude_md: CLAUDE.md                  # Project documentation
    serena_memories: .serena/memories/    # Canonical memories
    examples: .ce/examples/               # Framework examples
    prps: .ce/PRPs/                       # Framework PRPs

  # Framework locations (where to read from .ce/ extraction)
  framework:
    serena_memories: .ce/.serena/memories/
    examples: .ce/examples/
    prps: .ce/PRPs/
    commands: .ce/.claude/commands/
    settings: .ce/.claude/settings.local.json

  # Legacy locations (where to search in un-migrated projects)
  legacy:
    - PRPs/
    - examples/
    - context-engineering/
    - .serena.old/
```

**config_loader.py** - New module:

```python
"""Centralized configuration loader for init-project.

Loads blend-config.yml and provides typed access to directory paths.
"""

from pathlib import Path
from typing import Dict, List
import yaml
import logging

logger = logging.getLogger(__name__)


class BlendConfig:
    """Configuration container with path resolution."""

    def __init__(self, config_path: Path):
        """Load and validate configuration.

        Args:
            config_path: Path to blend-config.yml

        Raises:
            ValueError: If config invalid or missing required fields
        """
        if not config_path.exists():
            raise ValueError(
                f"Config file not found: {config_path}\n"
                f"🔧 Troubleshooting: Ensure blend-config.yml exists"
            )

        with open(config_path) as f:
            self._config = yaml.safe_load(f)

        self._validate()

    def _validate(self) -> None:
        """Validate config structure.

        Raises:
            ValueError: If required sections missing
        """
        required_sections = ["domains", "directories"]
        for section in required_sections:
            if section not in self._config:
                raise ValueError(
                    f"Missing required section: {section}\n"
                    f"🔧 Troubleshooting: Add to blend-config.yml"
                )

        # Validate directories subsections
        dir_config = self._config["directories"]
        required_subsections = ["output", "framework", "legacy"]
        for subsection in required_subsections:
            if subsection not in dir_config:
                raise ValueError(
                    f"Missing directories.{subsection} in config\n"
                    f"🔧 Troubleshooting: Add to blend-config.yml"
                )

    def get_output_path(self, domain: str) -> Path:
        """Get output path for domain.

        Args:
            domain: Domain name (settings, memories, examples, prps, claude_dir)

        Returns:
            Path object for output location (relative to project root)

        Example:
            >>> config.get_output_path("claude_dir")
            Path(".claude")
        """
        output_config = self._config["directories"]["output"]
        if domain not in output_config:
            raise ValueError(
                f"Unknown domain: {domain}\n"
                f"🔧 Troubleshooting: Valid domains: {list(output_config.keys())}"
            )
        return Path(output_config[domain])

    def get_framework_path(self, domain: str) -> Path:
        """Get framework source path for domain."""
        fw_config = self._config["directories"]["framework"]
        if domain not in fw_config:
            raise ValueError(f"Unknown framework domain: {domain}")
        return Path(fw_config[domain])

    def get_legacy_paths(self) -> List[Path]:
        """Get all legacy search paths."""
        legacy_list = self._config["directories"]["legacy"]
        return [Path(p) for p in legacy_list]

    def get_domain_config(self, domain: str) -> Dict:
        """Get full domain configuration."""
        return self._config["domains"].get(domain, {})
```

**detection.py** - Refactored to use config:

```python
# BEFORE (tools/ce/blending/detection.py:14-21)
SEARCH_PATTERNS = {
    "prps": ["PRPs/", "context-engineering/PRPs/"],
    "settings": [".claude/settings.local.json"],      # ❌ HARDCODED
    # ...
}

# AFTER (config-driven)
class LegacyFileDetector:
    def __init__(self, project_root: Path, config: BlendConfig):
        """Initialize with project root and config.

        Args:
            project_root: Path to project root
            config: BlendConfig instance with directory paths
        """
        self.project_root = Path(project_root).resolve()
        self.config = config

    def scan_all(self) -> Dict[str, List[Path]]:
        """Scan using config-defined paths (not hardcoded)."""
        inventory = {}

        # Get search patterns from config
        for domain in ["settings", "commands", "memories", "prps", "examples"]:
            # Use config to get legacy and framework paths
            legacy_paths = self._get_domain_search_paths(domain)
            inventory[domain] = []

            for pattern in legacy_paths:
                search_path = self.project_root / pattern
                if search_path.exists():
                    files = self._collect_files(search_path)
                    inventory[domain].extend(files)

        return inventory

    def _get_domain_search_paths(self, domain: str) -> List[Path]:
        """Get search paths for domain from config (not hardcoded)."""
        # Read from config instead of SEARCH_PATTERNS constant
        domain_config = self.config.get_domain_config(domain)
        legacy_source = domain_config.get("legacy_source")
        legacy_sources = domain_config.get("legacy_sources", [])

        paths = []
        if legacy_source:
            paths.append(Path(legacy_source))
        paths.extend([Path(p) for p in legacy_sources])

        # Fallback to global legacy paths if domain doesn't specify
        if not paths:
            paths = self.config.get_legacy_paths()

        return paths
```

### Acceptance Criteria

1. **Single Source of Truth**: All directory locations defined in `blend-config.yml` ✅
2. **Zero Hardcoded Paths**: No `".claude/"`, `".serena/memories/"`, `".ce/PRPs/"` strings in code ✅
3. **Config Validation**: Config loader validates all required paths present ✅
4. **Default Structure**: Config defaults to user's preferred layout ✅
5. **Backward Compatibility**: Existing blend-config.yml works with sensible defaults ✅

### Files Requiring Changes (16 total)

**Core Config**:
1. `.ce/blend-config.yml` - Add `directories` section (30 lines)
2. `tools/ce/config_loader.py` - NEW: Config loader module (150 lines)

**Detection & Classification**:
3. `tools/ce/blending/detection.py` - Replace SEARCH_PATTERNS with config calls
4. `tools/ce/blending/classification.py` - Use config for validation paths

**Blending Strategies** (6 files):
5. `tools/ce/blending/strategies/settings.py` - Read output path from config
6. `tools/ce/blending/strategies/claude_md.py` - Read output path from config
7. `tools/ce/blending/strategies/memories.py` - Read output/framework paths from config
8. `tools/ce/blending/strategies/examples.py` - Read output/framework paths from config
9. `tools/ce/blending/strategies/simple.py` (PRPs) - Read output path from config
10. `tools/ce/blending/strategies/base.py` (CommandOverwriteStrategy) - Read paths from config

**Core Blending**:
11. `tools/ce/blending/core.py` - Pass config to strategies, replace hardcoded paths
12. `tools/ce/blending/cleanup.py` - Use config.get_legacy_paths()
13. `tools/ce/blending/validation.py` - Use config for validation paths

**CLI & Utils**:
14. `tools/ce/init_project.py` - Load config at entry point, pass to all phases
15. `tools/ce/cli_handlers.py` - Pass config through pipeline
16. `tools/ce/update_context.py` - Use config.get_output_path("serena_memories")

---

## 3. Implementation Steps

### Phase 1: Config Loader Foundation (1-1.5 hours)

**Step 1.1**: Create config loader module

**File**: `tools/ce/config_loader.py` (NEW)

**Action**: Create file with BlendConfig class (see "Desired Architecture" section above for full code)

**Key methods**:
- `__init__(config_path)` - Load YAML
- `_validate()` - Check required sections
- `get_output_path(domain)` - Return Path for domain
- `get_framework_path(domain)` - Return framework source Path
- `get_legacy_paths()` - Return List[Path] of legacy dirs

**Step 1.2**: Update blend-config.yml

**File**: `.ce/blend-config.yml`

**Action**: Add `directories` section after `domains` section (see "Desired Architecture" for structure)

**Validation**: Config must load without errors:
```bash
cd tools
python3 -c "from ce.config_loader import BlendConfig; BlendConfig('../.ce/blend-config.yml')"
```

### Phase 2: Refactor Detection & Core (1.5-2 hours)

**Step 2.1**: Update detection.py

**File**: `tools/ce/blending/detection.py`

**Changes**:
1. Remove SEARCH_PATTERNS constant (lines 14-21)
2. Add `config: BlendConfig` parameter to `__init__` (line 43)
3. Replace hardcoded patterns with `self.config.get_domain_config(domain)`
4. Add `_get_domain_search_paths()` helper method (see "Desired Architecture")

**Step 2.2**: Update classification.py

**File**: `tools/ce/blending/classification.py`

**Changes**: Add `config` parameter, use for validation path lookups

**Step 2.3**: Update core.py

**File**: `tools/ce/blending/core.py`

**Changes**:
1. Add `config: BlendConfig` to BlendingOrchestrator.__init__
2. Replace hardcoded `.ce/.serena/memories/` with `config.get_framework_path("serena_memories")`
3. Replace hardcoded `.serena/memories/` with `config.get_output_path("serena_memories")`
4. Pass config to all strategy instances

### Phase 3: Refactor 6 Blending Strategies (1.5-2 hours)

**For each strategy** (`settings.py`, `claude_md.py`, `memories.py`, `examples.py`, `simple.py`, `base.py`):

**Pattern**:
```python
# BEFORE
def blend(self, framework_content, target_content, context):
    output_path = context["project_root"] / ".claude" / "settings.local.json"  # ❌ HARDCODED

# AFTER
def blend(self, framework_content, target_content, context):
    config = context["config"]  # BlendConfig instance
    output_path = context["project_root"] / config.get_output_path("claude_dir") / "settings.local.json"  # ✅ CONFIG
```

**Changes per file**:
1. Extract `config` from context dict
2. Replace all hardcoded paths with `config.get_output_path(domain)`
3. Replace framework paths with `config.get_framework_path(domain)`

**Specific files**:
- `settings.py`: Use `config.get_output_path("claude_dir")` for `.claude/`
- `claude_md.py`: Use `config.get_output_path("claude_md")` for `CLAUDE.md`
- `memories.py`: Use `config.get_output_path("serena_memories")`
- `examples.py`: Use `config.get_output_path("examples")`
- `simple.py`: Use `config.get_output_path("prps")`
- `base.py` (CommandOverwriteStrategy): Use `config.get_output_path("claude_dir")`

### Phase 4: Update CLI Entry Points (30 min)

**Step 4.1**: Load config in init_project.py

**File**: `tools/ce/init_project.py`

**Changes**:
```python
# Add near top
from ce.config_loader import BlendConfig

# In main() or run() function:
config_path = project_root / ".ce" / "blend-config.yml"
config = BlendConfig(config_path)

# Pass to all phases
detector = LegacyFileDetector(project_root, config)  # Add config param
orchestrator = BlendingOrchestrator(config, dry_run=False)  # Add config param
```

**Step 4.2**: Update cli_handlers.py

**File**: `tools/ce/cli_handlers.py`

**Changes**: Pass config through to init-project call

**Step 4.3**: Update update_context.py

**File**: `tools/ce/update_context.py`

**Changes**:
```python
# Replace hardcoded .serena/memories/
memories_dir = config.get_output_path("serena_memories")
```

### Phase 5: Testing & Validation (1-2 hours)

**Step 5.1**: Write config loader tests

**File**: `tools/tests/test_config_loader.py` (NEW)

**Test cases** (minimum 8 tests):
1. `test_load_valid_config()` - Loads successfully
2. `test_missing_config_file()` - Raises ValueError
3. `test_missing_directories_section()` - Raises ValueError
4. `test_missing_output_subsection()` - Raises ValueError
5. `test_get_output_path_valid_domain()` - Returns Path
6. `test_get_output_path_invalid_domain()` - Raises ValueError
7. `test_get_framework_path()` - Returns Path
8. `test_get_legacy_paths()` - Returns List[Path]

**Step 5.2**: Write integration tests

**File**: `tools/tests/test_init_project_config.py` (NEW)

**Test cases** (minimum 3 tests):
1. `test_detection_uses_config_paths()` - Verify no hardcoded paths
2. `test_blending_uses_config_output_paths()` - Verify output locations
3. `test_custom_directory_structure()` - Full init with non-default paths

**Step 5.3**: Run validation gates (see section 4)

---

## 4. Validation Gates

### Gate 1: Zero Hardcoded Paths

**Command**:
```bash
cd tools/ce
grep -r "\.claude/" --include="*.py" . | grep -v "config_loader.py" | grep -v "test_" | wc -l
```

**Expected**: `0` (zero matches)

**Success Criteria**: PASS if output is 0, FAIL otherwise

**Troubleshooting**: If > 0, check each match and replace with `config.get_output_path()`

### Gate 2: Config Validation Tests Pass

**Command**:
```bash
cd tools
uv run pytest tests/test_config_loader.py -v
```

**Expected**: All 8+ tests pass

**Success Criteria**:
- `test_load_valid_config` - PASSED
- `test_missing_config_file` - PASSED (ValueError raised)
- `test_missing_directories_section` - PASSED (ValueError raised)
- `test_get_output_path_valid_domain` - PASSED
- `test_get_output_path_invalid_domain` - PASSED (ValueError raised)
- All other tests - PASSED

**FAIL conditions**: Any test fails or errors

### Gate 3: Integration Tests Pass

**Command**:
```bash
cd tools
uv run pytest tests/test_init_project_config.py -v
```

**Expected**: All integration tests pass

**Success Criteria**:
- Detection phase uses config paths (not hardcoded)
- Blending strategies use config output paths
- Custom directory structure works end-to-end

### Gate 4: Backward Compatibility

**Command**:
```bash
cd tools
# Run init-project with EXISTING blend-config.yml (no directories section)
uv run ce init-project /tmp/test-project-legacy-config
```

**Expected**: Either:
- **Option A**: Graceful defaults applied (preferred)
- **Option B**: Clear error message with troubleshooting (acceptable)

**Success Criteria**: No cryptic errors, clear path forward for users

**Validation**:
```bash
# Check if .claude/ created at expected location
ls -la /tmp/test-project-legacy-config/.claude/
```

---

## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
cd tools
uv run pytest tests/test_config_loader.py tests/test_init_project_config.py -v --cov=ce.config_loader --cov=ce.blending
```

### Coverage Requirements

- **Config loader**: ≥ 80% (all branches tested)
- **Integration**: 3+ end-to-end tests
- **Edge cases**:
  - Missing config file
  - Missing directories section
  - Invalid domain names
  - Custom directory structure

### Test Matrix

| Test Case | Config State | Expected Outcome |
|-----------|-------------|------------------|
| Valid config | All sections present | Load successfully |
| Missing file | Config doesn't exist | ValueError with troubleshooting |
| Missing directories | Old config format | Defaults or clear error |
| Invalid domain | get_output_path("foo") | ValueError with valid domains |
| Custom paths | Non-default structure | Blending uses custom paths |

---

## 6. Rollout Plan

### Phase 1: Development

1. **Implement config loader** (1h) - Create config_loader.py + tests
2. **Update blend-config.yml** (15min) - Add directories section
3. **Refactor detection** (30min) - Remove hardcoded SEARCH_PATTERNS
4. **Refactor strategies** (2h) - Update 6 strategy files
5. **Update entry points** (30min) - Load config in init_project.py
6. **Write tests** (1.5h) - Config + integration tests
7. **Pass validation gates** (30min) - All 4 gates

**Total**: 4-6 hours

### Phase 2: Review

1. **Self-review code** - Check for missed hardcoded paths
2. **Run full test suite** - `uv run pytest tests/ -v`
3. **Test on real project** - Run iteration test on ctx-eng-plus-test-target
4. **Update documentation** - Add config structure to INITIALIZATION.md

### Phase 3: Deployment

1. **Commit changes** - Git commit with PRP reference
2. **Update context** - Run `uv run ce update-context --prp PRPs/feature-requests/PRP-1.md`
3. **Monitor** - Watch for issues in next init-project runs
4. **Document** - Add to CHANGELOG or release notes

---

## Research Findings

### Codebase Analysis

**Hardcoded Path Locations Found** (manual grep analysis):

1. `tools/ce/blending/detection.py:14-21` - SEARCH_PATTERNS dict
2. `tools/ce/blending/core.py` - Multiple `.ce/.serena/memories/` references
3. `tools/ce/blending/strategies/settings.py` - `.claude/settings.local.json`
4. `tools/ce/blending/strategies/claude_md.py` - `CLAUDE.md`
5. `tools/ce/blending/strategies/memories.py` - `.serena/memories/`
6. `tools/ce/blending/strategies/examples.py` - `.ce/examples/`
7. `tools/ce/blending/strategies/simple.py` - `.ce/PRPs/`
8. `tools/ce/blending/strategies/base.py` - `.claude/commands/`
9. `tools/ce/blending/cleanup.py` - Legacy directory list
10. `tools/ce/blending/validation.py` - Validation path checks
11. `tools/ce/init_project.py` - Entry point
12. `tools/ce/cli_handlers.py` - CLI integration
13. `tools/ce/update_context.py` - `.serena/memories/` for context updates

**Existing Config Structure** (.ce/blend-config.yml):
- Has `domains` section with per-domain strategy config
- Missing `directories` section
- Strategy configs have `source` fields (legacy paths) but inconsistent

**Related PRPs**:
- PRP-40: Examples domain migration (similar config-driven approach)
- PRP-41: Iteration testing (discovered this bug)
- PRP-33: 3-rule blending (settings strategy reference)

### External References

- **YAML Configuration**: PyYAML already in dependencies
- **pathlib**: Python stdlib (no new dependency)
- **Testing**: pytest already in use

---

## Appendix: Haiku-Ready Checklist

✅ **Goal**: Exact end state in 1 sentence? YES - "Eliminate all hardcoded directory paths"
✅ **Output**: Exact file paths and line numbers? YES - 16 files listed with specifics
✅ **Limits**: Scope boundaries explicit? YES - IN: tools/ce/blending/*, OUT: directory structure itself
✅ **Data**: All context inline? YES - Before/after code, file paths, config structure
✅ **Evaluation**: Copy-paste bash commands? YES - 4 gates with exact commands
✅ **Decisions**: All made? YES - Use BlendConfig class, YAML config structure defined
✅ **Code Snippets**: Before/after examples? YES - detection.py, settings.py, config structure
✅ **Testing**: Expected outputs documented? YES - Test matrix, validation criteria
✅ **Edge Cases**: Specific handling? YES - Missing config, invalid domains, backward compatibility
✅ **No Vague Language**: Checked? YES - No "appropriate", "suitable", etc.

**Status**: ✅ HAIKU-READY

---

## Peer Review Notes

**Reviewed**: 2025-11-08T19:30:00Z
**Reviewer**: Context-Naive Peer Review (automated)

**Applied Improvements**:
1. Restructured to follow GOLD framework
2. Added detailed before/after code examples with line numbers
3. Replaced vague implementation steps with concrete file:line changes
4. Added binary validation gates with copy-paste commands
5. Included complete config_loader.py implementation
6. Added test matrix and coverage requirements
7. Fixed documentation references
8. Added Haiku-Ready checklist verification

**Result**: PRP now executable by Claude 4.5 Haiku without additional decision-making.
