# PRP-36: CE Framework Project Initializer CLI

**Created**: 2025-11-06
**Status**: Planning
**Complexity**: Medium
**Estimated Effort**: 4-6 hours

---

## PROBLEM STATEMENT

Currently, CE framework initialization requires either:
1. **Syntropy MCP** (external dependency): `npx syntropy-mcp init ce-framework`
2. **Manual process**: 5-phase workflow documented in INITIALIZATION.md

**Pain Points**:
- No native Python CLI for initialization
- Can't test initialization on target projects without Syntropy MCP
- No way to re-run initialization or partial updates
- Difficult to debug initialization failures

**Need**: Native `ce init-project <path>` command that orchestrates complete CE framework installation on any target project.

---

## SOLUTION OVERVIEW

Create `tools/ce/init_project.py` module with CLI command:

```bash
# Initialize CE framework on target project
uv run ce init-project /path/to/target-project

# Dry-run mode (show what would be done)
uv run ce init-project /path/to/target --dry-run

# Re-initialize (blend only, skip extraction)
uv run ce init-project /path/to/target --blend-only

# Partial initialization (specific phases)
uv run ce init-project /path/to/target --phase extract
uv run ce init-project /path/to/target --phase blend
```

### Architecture: 4-Phase Pipeline

```
Phase 1: EXTRACT (Python)
  └─ Extract ce-infrastructure.xml to target project
  └─ Reorganize tools/ to .ce/tools/
  └─ Copy ce-workflow-docs.xml

Phase 2: BLEND (Delegation to blend tool)
  └─ Call: ce blend --all --target-dir <target>
  └─ Handles: settings, CLAUDE.md, memories, examples, PRPs, commands

Phase 3: INITIALIZE (Python)
  └─ Run: uv sync in .ce/tools/
  └─ Verify: uv run ce --version

Phase 4: VERIFY (Python)
  └─ Check: Critical files exist
  └─ Validate: settings.local.json is valid JSON
  └─ Report: Installation summary
```

---

## IMPLEMENTATION PLAN

### Phase 1: Core Module (`tools/ce/init_project.py`)

```python
"""CE Framework project initializer."""

from pathlib import Path
from typing import Dict, Any

class ProjectInitializer:
    """Orchestrates CE framework installation on target project."""

    def __init__(self, target_project: Path, dry_run: bool = False):
        self.target = target_project
        self.dry_run = dry_run

    def run(self, phase: str = "all") -> Dict[str, Any]:
        """Run initialization phases."""
        if phase == "all":
            self.extract()
            self.blend()
            self.initialize()
            self.verify()
        elif phase == "extract":
            self.extract()
        elif phase == "blend":
            self.blend()
        elif phase == "initialize":
            self.initialize()
        elif phase == "verify":
            self.verify()
        else:
            raise ValueError(f"Unknown phase: {phase}")

    def extract(self):
        """Phase 1: Extract infrastructure package."""
        # 1. Extract ce-infrastructure.xml
        # 2. Reorganize tools/ to .ce/tools/
        # 3. Copy ce-workflow-docs.xml

    def blend(self):
        """Phase 2: Blend framework + target files."""
        # Delegate to blend tool
        # subprocess.run(["uv", "run", "ce", "blend", "--all", "--target-dir", str(self.target)])

    def initialize(self):
        """Phase 3: Initialize tools."""
        # 1. cd .ce/tools
        # 2. uv sync
        # 3. uv run ce --version

    def verify(self):
        """Phase 4: Verify installation."""
        # Check critical files
        # Validate JSON files
        # Report summary
```

### Phase 2: CLI Integration (`tools/ce/__main__.py`)

Add subcommand:

```python
# === INIT-PROJECT COMMAND ===
init_parser = subparsers.add_parser(
    "init-project",
    help="Initialize CE framework on target project"
)
init_parser.add_argument(
    "target_dir",
    help="Target project directory"
)
init_parser.add_argument(
    "--dry-run",
    action="store_true",
    help="Show what would be done without executing"
)
init_parser.add_argument(
    "--phase",
    choices=["extract", "blend", "initialize", "verify", "all"],
    default="all",
    help="Run specific phase (default: all)"
)
init_parser.add_argument(
    "--blend-only",
    action="store_true",
    help="Skip extraction (blend only, for re-initialization)"
)
```

### Phase 3: Handler (`tools/ce/cli_handlers.py`)

```python
def cmd_init_project(args) -> int:
    """Handle init-project command."""
    from ce.init_project import ProjectInitializer

    target = Path(args.target_dir).resolve()
    if not target.exists():
        print(f"❌ Target directory not found: {target}")
        return 1

    initializer = ProjectInitializer(target, dry_run=args.dry_run)

    if args.blend_only:
        initializer.blend()
    else:
        initializer.run(phase=args.phase)

    return 0
```

---

## FILES MODIFIED

1. **NEW**: `tools/ce/init_project.py` (main module)
2. **NEW**: `tools/tests/test_init_project.py` (unit tests)
3. **MODIFY**: `tools/ce/__main__.py` (add init-project subcommand)
4. **MODIFY**: `tools/ce/cli_handlers.py` (add cmd_init_project handler)

---

## ACCEPTANCE CRITERIA

1. ✅ `ce init-project <path>` extracts infrastructure package to target
2. ✅ `ce init-project <path> --dry-run` shows plan without execution
3. ✅ `ce init-project <path> --phase extract` runs extraction only
4. ✅ `ce init-project <path> --phase blend` runs blending only
5. ✅ `ce init-project <path> --blend-only` skips extraction (for updates)
6. ✅ Extraction reorganizes tools/ to .ce/tools/
7. ✅ Blending delegates to `ce blend --all`
8. ✅ Initialization runs `uv sync` in .ce/tools/
9. ✅ Verification checks critical files and reports summary
10. ✅ Error handling with actionable messages (🔧 troubleshooting)

---

## TESTING STRATEGY

### Unit Tests

```python
def test_project_initializer_dry_run():
    """Test dry-run mode doesn't modify files."""

def test_extract_phase_creates_structure():
    """Test extraction creates .ce/tools/ structure."""

def test_blend_phase_delegates_correctly():
    """Test blend phase calls ce blend command."""

def test_verify_phase_checks_critical_files():
    """Test verification checks framework files."""
```

### Integration Tests

```bash
# Create test target project
mkdir -p /tmp/test-target
cd /tmp/test-target
git init

# Run initialization
uv run ce init-project /tmp/test-target

# Verify structure
ls .ce/tools/ce/
ls .claude/commands/
ls .serena/memories/

# Verify tools work
cd .ce/tools && uv run ce --version
```

---

## DEPENDENCIES

- Batch 34 (blending tool) - COMPLETED ✅
- repomix_unpack.py - EXISTS ✅

---

## RISKS & MITIGATIONS

1. **Risk**: Target project already has CE files
   - **Mitigation**: Detect existing installation, prompt user (overwrite/merge/abort)

2. **Risk**: UV not installed on system
   - **Mitigation**: Check for `uv` binary, provide install instructions

3. **Risk**: ce-infrastructure.xml not found
   - **Mitigation**: Check for package in `.ce/ce-infrastructure.xml`, error with troubleshooting

4. **Risk**: Blend phase fails
   - **Mitigation**: Catch errors, preserve backups, rollback if needed

---

## VALIDATION GATES

```bash
# Gate 1: CLI integration
uv run ce init-project --help
# Expected: Shows usage with all flags

# Gate 2: Dry-run mode
uv run ce init-project /tmp/test --dry-run
# Expected: Shows plan, no files created

# Gate 3: Full initialization
uv run ce init-project /tmp/test-target
# Expected: Complete CE structure created

# Gate 4: Partial phase
uv run ce init-project /tmp/test-target --phase extract
# Expected: Only extraction runs

# Gate 5: Verification
cd /tmp/test-target/.ce/tools && uv run ce --version
# Expected: CE version displayed
```

---

## SUCCESS METRICS

- ✅ Native Python CLI for initialization (no external dependencies)
- ✅ Can initialize any target project from ctx-eng-plus repo
- ✅ Supports dry-run for safety
- ✅ Supports partial re-initialization
- ✅ Clear error messages with troubleshooting

---

## EXAMPLE USAGE

```bash
# Scenario 1: Fresh project initialization
cd /Users/bprzybysz/nc-src/ctx-eng-plus
uv run ce init-project /path/to/new-project
# Output:
# 📦 Initializing CE framework on: /path/to/new-project
# Phase 1: EXTRACT ✓ (50 files extracted)
# Phase 2: BLEND ✓ (6 domains blended)
# Phase 3: INITIALIZE ✓ (tools ready)
# Phase 4: VERIFY ✓ (all checks passed)
# ✅ CE framework installed successfully!

# Scenario 2: Dry-run (planning mode)
uv run ce init-project /path/to/project --dry-run
# Output: Shows what would be done, no changes

# Scenario 3: Re-blend after manual changes
uv run ce init-project /path/to/project --blend-only
# Output: Skips extraction, re-runs blending only

# Scenario 4: Partial initialization (extract only)
uv run ce init-project /path/to/project --phase extract
# Output: Extracts files, stops before blending
```

---

## NOTES

- This tool makes CE framework testable on any project
- Enables rapid testing of initialization workflows
- Foundation for future features:
  - `ce upgrade-project` (CE 1.0 → CE 1.1)
  - `ce repair-project` (fix broken installations)
  - `ce sync-project` (update framework files only)
