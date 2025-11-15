---
name: Cleanup Module (Phase D)
description: Implement safe legacy directory removal after migration verification
prp_id: PRP-34.2.3
status: new
created_date: '2025-11-05T00:00:00.000000'
last_updated: '2025-11-05T00:00:00.000000'
batch: 34
stage: stage-2-parallel
execution_order: 4
merge_order: 4
dependencies:
- PRP-34.1.1
estimated_hours: 1.0
complexity: low
risk_level: low
conflict_potential: NONE
worktree_path: ../ctx-eng-plus-prp-34-2-3
branch_name: prp-34-2-3-cleanup-module
---

# PRP-34.2.3: Cleanup Module (Phase D)

## TL;DR

**What**: Implement safe legacy directory removal after migration verification

**Why**: After CE 1.1 initialization, legacy directories (PRPs/, examples/, context-engineering/) should be safely removed to complete migration

**How**: Create cleanup module with verification checks to ensure migration complete before removal

**Impact**: 1.0 hour, low complexity, low risk

---

## Feature Overview

**Context:** This is Phase D of the 4-phase CE 1.1 initialization pipeline. After buckets are collected (Phase A), user files migrated (Phase B), and infrastructure extracted/blended (Phase C), legacy directories must be cleaned up to complete the migration.

**Problem:**
- Legacy directories remain after migration (PRPs/, examples/, context-engineering/)
- No automated cleanup after CE 1.1 initialization
- Risk of data loss if cleanup runs before migration complete
- Manual cleanup error-prone and time-consuming
- No dry-run mode to preview cleanup actions

**Solution:**
Implement cleanup module that:
1. Verifies migration complete before cleanup
2. Safely removes legacy directories: PRPs/, examples/, context-engineering/
3. Preserves standard locations: .claude/, .serena/, CLAUDE.md, .ce/
4. Warns on unmigrated files (aborts cleanup)
5. Supports dry-run mode (show actions without deleting)
6. Returns status dict for each directory

**Expected Outcome:**
- Safe cleanup after CE 1.1 initialization complete
- Zero data loss (verification before deletion)
- Clear dry-run output for preview
- Clean target project structure (only .ce/, .serena/, .claude/, CLAUDE.md remain)

---

## Implementation Blueprint

### Phase 1: Cleanup Module Core (30 minutes)

**Goal:** Create cleanup.py module with safe removal logic

**File:** `tools/ce/blending/cleanup.py`

**Core Function:**

```python
from pathlib import Path
from typing import Dict, List, Optional
import shutil


def cleanup_legacy_dirs(
    target_project: Path,
    dry_run: bool = True
) -> Dict[str, bool]:
    """
    Remove legacy directories after CE 1.1 migration.

    Args:
        target_project: Target project root path
        dry_run: If True, show actions without deleting (default: True)

    Returns:
        Dict[dir_path, cleanup_success]: Status for each directory

    Raises:
        ValueError: If migration not complete (unmigrated files detected)
    """
    legacy_dirs = [
        "PRPs",
        "examples",
        "context-engineering"
    ]

    status: Dict[str, bool] = {}

    print("\n🧹 Legacy Directory Cleanup")
    print("=" * 60)

    if dry_run:
        print("⚠️  DRY-RUN MODE: No files will be deleted")
        print()

    for legacy_dir in legacy_dirs:
        legacy_path = target_project / legacy_dir

        # Skip if directory doesn't exist
        if not legacy_path.exists():
            print(f"⏭️  {legacy_dir}/ - Not found (skipping)")
            status[legacy_dir] = True
            continue

        # Verify migration complete
        print(f"🔍 Verifying {legacy_dir}/ migration...")
        is_migrated, unmigrated = verify_migration_complete(
            legacy_path,
            target_project
        )

        if not is_migrated:
            print(f"❌ {legacy_dir}/ - Migration incomplete!")
            print(f"   Unmigrated files: {len(unmigrated)}")
            for file in unmigrated[:5]:  # Show first 5
                print(f"     - {file}")
            if len(unmigrated) > 5:
                print(f"     ... and {len(unmigrated) - 5} more")

            raise ValueError(
                f"Cannot cleanup {legacy_dir}/: {len(unmigrated)} unmigrated files detected. "
                f"Run migration again or manually verify."
            )

        # Safe to remove
        if dry_run:
            print(f"✓ {legacy_dir}/ - Would remove (verified complete)")
            status[legacy_dir] = True
        else:
            try:
                shutil.rmtree(legacy_path)
                print(f"✅ {legacy_dir}/ - Removed successfully")
                status[legacy_dir] = True
            except Exception as e:
                print(f"❌ {legacy_dir}/ - Removal failed: {e}")
                status[legacy_dir] = False

    print()
    print("=" * 60)

    if dry_run:
        print("ℹ️  Dry-run complete. Run with --execute to perform cleanup.")
    else:
        success_count = sum(1 for v in status.values() if v)
        print(f"✅ Cleanup complete: {success_count}/{len(status)} directories removed")

    return status
```

**Verification Function:**

```python
def verify_migration_complete(
    legacy_dir: Path,
    target_project: Path
) -> tuple[bool, List[str]]:
    """
    Verify all files in legacy_dir have been migrated.

    Args:
        legacy_dir: Legacy directory path (e.g., PRPs/)
        target_project: Target project root

    Returns:
        (is_complete, unmigrated_files): Migration status + list of unmigrated files
    """
    ce_dir = target_project / ".ce"

    # Find all files in legacy dir
    legacy_files = list(legacy_dir.rglob("*"))
    legacy_files = [f for f in legacy_files if f.is_file()]

    # Map to expected .ce/ locations
    unmigrated: List[str] = []

    for legacy_file in legacy_files:
        relative_path = legacy_file.relative_to(target_project)

        # Check if migrated to .ce/
        # PRPs/executed/PRP-1.md → .ce/PRPs/executed/PRP-1.md
        # examples/pattern.py → .ce/examples/user/pattern.py

        # For PRPs: direct mapping
        if legacy_file.parts[0] == "PRPs":
            ce_path = ce_dir / relative_path
        # For examples: user subdirectory
        elif legacy_file.parts[0] == "examples":
            ce_path = ce_dir / "examples" / "user" / "/".join(legacy_file.parts[1:])
        # For context-engineering: .ce/ itself
        elif legacy_file.parts[0] == "context-engineering":
            ce_path = ce_dir / "/".join(legacy_file.parts[1:])
        else:
            # Unknown legacy structure
            ce_path = ce_dir / relative_path

        # Check if migrated file exists
        if not ce_path.exists():
            unmigrated.append(str(relative_path))

    is_complete = len(unmigrated) == 0

    return is_complete, unmigrated


def find_unmigrated_files(
    legacy_dir: Path,
    ce_dir: Path
) -> List[str]:
    """
    Find files in legacy_dir not present in ce_dir.

    Args:
        legacy_dir: Legacy directory path
        ce_dir: .ce/ directory path

    Returns:
        List of unmigrated file paths (relative to legacy_dir)
    """
    unmigrated: List[str] = []

    if not legacy_dir.exists():
        return unmigrated

    for legacy_file in legacy_dir.rglob("*"):
        if not legacy_file.is_file():
            continue

        # Calculate relative path
        relative_path = legacy_file.relative_to(legacy_dir)

        # Check if exists in .ce/
        ce_file = ce_dir / legacy_dir.name / relative_path

        if not ce_file.exists():
            unmigrated.append(str(relative_path))

    return unmigrated
```

**Success Criteria:**
- cleanup_legacy_dirs() implemented with dry_run parameter
- verify_migration_complete() checks migration status
- find_unmigrated_files() detects unmigrated files
- Preserves .claude/, .serena/, CLAUDE.md, .ce/
- Returns Dict[dir, status] for each directory

---

### Phase 2: CLI Integration (15 minutes)

**Goal:** Add cleanup command to CE CLI

**File:** `tools/ce/__main__.py`

**Add Command:**

```python
@click.command()
@click.option(
    "--dry-run",
    is_flag=True,
    default=True,
    help="Show what would be removed without deleting (default: True)"
)
@click.option(
    "--execute",
    is_flag=True,
    default=False,
    help="Execute cleanup (remove legacy directories)"
)
def cleanup(dry_run: bool, execute: bool):
    """Remove legacy directories after CE 1.1 migration."""
    from ce.blending.cleanup import cleanup_legacy_dirs

    # If --execute provided, turn off dry_run
    if execute:
        dry_run = False

    try:
        target_project = Path.cwd()

        status = cleanup_legacy_dirs(
            target_project=target_project,
            dry_run=dry_run
        )

        # Exit with success if all cleanups succeeded
        if all(status.values()):
            sys.exit(0)
        else:
            sys.exit(1)

    except ValueError as e:
        # Migration incomplete
        click.echo(f"❌ {e}", err=True)
        sys.exit(2)
    except Exception as e:
        click.echo(f"❌ Cleanup failed: {e}", err=True)
        sys.exit(1)
```

**Register Command:**

```python
cli.add_command(cleanup)
```

**Usage:**

```bash
# Dry-run (default)
cd tools && uv run ce cleanup

# Execute cleanup
cd tools && uv run ce cleanup --execute

# Explicit dry-run
cd tools && uv run ce cleanup --dry-run
```

**Success Criteria:**
- `ce cleanup` command available
- Default behavior is dry-run
- --execute flag removes directories
- Exit codes: 0 (success), 1 (partial failure), 2 (migration incomplete)

---

### Phase 3: Testing (15 minutes)

**Goal:** Test cleanup with various scenarios

**File:** `tools/tests/test_cleanup.py`

**Test Cases:**

```python
import pytest
from pathlib import Path
import shutil
from ce.blending.cleanup import cleanup_legacy_dirs, verify_migration_complete


def test_cleanup_dry_run(tmp_path):
    """Test dry-run mode doesn't delete files."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    (legacy_dir / "test.md").write_text("# Test PRP")

    # Create .ce/ with migrated file
    ce_dir = tmp_path / ".ce"
    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "test.md").write_text("# Test PRP")

    # Run cleanup (dry-run)
    status = cleanup_legacy_dirs(tmp_path, dry_run=True)

    # Verify directory still exists
    assert legacy_dir.exists()
    assert status["PRPs"] == True


def test_cleanup_execute(tmp_path):
    """Test execute mode removes directories."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    (legacy_dir / "test.md").write_text("# Test PRP")

    # Create .ce/ with migrated file
    ce_dir = tmp_path / ".ce"
    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "test.md").write_text("# Test PRP")

    # Run cleanup (execute)
    status = cleanup_legacy_dirs(tmp_path, dry_run=False)

    # Verify directory removed
    assert not legacy_dir.exists()
    assert status["PRPs"] == True


def test_cleanup_migration_incomplete(tmp_path):
    """Test cleanup aborts when migration incomplete."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    (legacy_dir / "test.md").write_text("# Test PRP")
    (legacy_dir / "unmigrated.md").write_text("# Unmigrated")

    # Create .ce/ with only one migrated file
    ce_dir = tmp_path / ".ce"
    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "test.md").write_text("# Test PRP")
    # unmigrated.md NOT migrated

    # Run cleanup (should fail)
    with pytest.raises(ValueError, match="unmigrated files detected"):
        cleanup_legacy_dirs(tmp_path, dry_run=False)

    # Verify directory still exists
    assert legacy_dir.exists()


def test_verify_migration_complete(tmp_path):
    """Test migration verification."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    (legacy_dir / "file1.md").write_text("# File 1")
    (legacy_dir / "file2.md").write_text("# File 2")

    ce_dir = tmp_path / ".ce"
    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "file1.md").write_text("# File 1")
    # file2.md NOT migrated

    # Verify
    is_complete, unmigrated = verify_migration_complete(legacy_dir, tmp_path)

    assert is_complete == False
    assert len(unmigrated) == 1
    assert "PRPs/file2.md" in unmigrated[0]


def test_cleanup_skips_missing_dirs(tmp_path):
    """Test cleanup skips directories that don't exist."""
    # No legacy dirs created
    ce_dir = tmp_path / ".ce"
    ce_dir.mkdir()

    # Run cleanup
    status = cleanup_legacy_dirs(tmp_path, dry_run=False)

    # Should skip all (not fail)
    assert status["PRPs"] == True
    assert status["examples"] == True
    assert status["context-engineering"] == True


def test_cleanup_preserves_standard_locations(tmp_path):
    """Test cleanup doesn't touch .claude/, .serena/, CLAUDE.md, .ce/."""
    # Create standard locations
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".serena").mkdir()
    (tmp_path / ".ce").mkdir()
    (tmp_path / "CLAUDE.md").write_text("# Project Guide")

    # Create legacy dir
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    (legacy_dir / "test.md").write_text("# Test")

    # Migrate
    ce_prps = tmp_path / ".ce" / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "test.md").write_text("# Test")

    # Run cleanup
    cleanup_legacy_dirs(tmp_path, dry_run=False)

    # Verify standard locations preserved
    assert (tmp_path / ".claude").exists()
    assert (tmp_path / ".serena").exists()
    assert (tmp_path / ".ce").exists()
    assert (tmp_path / "CLAUDE.md").exists()
```

**Run Tests:**

```bash
cd tools
uv run pytest tests/test_cleanup.py -v
```

**Success Criteria:**
- All 7 test cases passing
- Dry-run doesn't delete
- Execute mode removes directories
- Migration verification works
- Unmigrated files abort cleanup
- Missing dirs skipped gracefully
- Standard locations preserved

---

## Acceptance Criteria

**Must Have:**
- [ ] cleanup_legacy_dirs() function with dry_run parameter
- [ ] verify_migration_complete() checks migration status
- [ ] find_unmigrated_files() detects unmigrated files
- [ ] Removes legacy dirs: PRPs/, examples/, context-engineering/
- [ ] Preserves: .claude/, .serena/, CLAUDE.md, .ce/
- [ ] Dry-run mode shows actions without deleting
- [ ] Warns on unmigrated files (aborts cleanup)
- [ ] Returns Dict[dir, status] for each directory
- [ ] CLI command: `ce cleanup`
- [ ] All tests passing (7 test cases)

**Nice to Have:**
- [ ] Interactive mode: prompt before each removal
- [ ] Backup option: move to .tmp/ instead of delete
- [ ] Progress bars for large directories

**Out of Scope:**
- File-level migration tracking (this PRP does directory-level only)
- Rollback mechanism (manual restore from git)
- Cross-platform path handling beyond Path() (Windows/Linux/macOS already covered)

---

## Testing Strategy

### Unit Tests
- cleanup_legacy_dirs() with dry_run=True
- cleanup_legacy_dirs() with dry_run=False
- verify_migration_complete() with complete migration
- verify_migration_complete() with incomplete migration
- find_unmigrated_files() detection
- Missing directory handling
- Standard location preservation

### Integration Tests
```bash
# Create test project
mkdir -p /tmp/test-cleanup/{PRPs,examples,.ce}
echo "# Test" > /tmp/test-cleanup/PRPs/test.md

# Test dry-run
cd /tmp/test-cleanup
uv run -C /Users/bprzybysz/nc-src/ctx-eng-plus/tools ce cleanup --dry-run

# Verify no deletion
test -d PRPs && echo "✅ Dry-run preserved directory"

# Migrate file
mkdir -p .ce/PRPs
cp PRPs/test.md .ce/PRPs/

# Test execute
uv run -C /Users/bprzybysz/nc-src/ctx-eng-plus/tools ce cleanup --execute

# Verify deletion
! test -d PRPs && echo "✅ Execute removed directory"
```

### Error Cases
- Migration incomplete → ValueError raised
- Permission denied → Status dict shows failure
- Partial cleanup failure → Exit code 1

---

## Dependencies

**Internal:**
- PRP-34.1.1: Bucket collection (prerequisite)
- Phase B (user file migration) must be complete
- Phase C (extraction/blending) must be complete

**External:**
- Python 3.10+ (pathlib, shutil)
- click (CLI framework)
- pytest (testing)

**Files Modified:**
- `tools/ce/blending/cleanup.py` (new)
- `tools/ce/__main__.py` (add cleanup command)
- `tools/tests/test_cleanup.py` (new)

---

## Risks & Mitigations

**Risk 1: Data loss if migration incomplete**
- **Mitigation:** verify_migration_complete() aborts on unmigrated files
- **Safeguard:** Default dry_run=True (user must explicitly --execute)

**Risk 2: Partial cleanup failure**
- **Mitigation:** Continue cleanup for other dirs, return status dict
- **Safeguard:** Exit code 1 on partial failure

**Risk 3: Accidental removal of standard locations**
- **Mitigation:** Hardcoded legacy_dirs list (only PRPs/, examples/, context-engineering/)
- **Testing:** Explicit test case for preservation

**Risk 4: Permission errors**
- **Mitigation:** Try-except around shutil.rmtree(), status dict tracks failures
- **User guidance:** Clear error messages

---

## References

**Python Documentation:**
- pathlib: https://docs.python.org/3/library/pathlib.html
- shutil: https://docs.python.org/3/library/shutil.html

**Related PRPs:**
- PRP-34.1.1: Bucket Collection (Phase A)
- PRP-34.2.1: User Files Migration (Phase B)
- PRP-34.2.2: Repomix Package Extraction (Phase C)
- PRP-34.2.4: Blending Module (Phase D prerequisite)

**CE 1.1 Initialization:**
- examples/INITIALIZATION.md: 5-phase workflow documentation

---

## Success Metrics

**Implementation:**
- Time to implement: 1.0 hour (estimated)
- Code coverage: 90%+ for cleanup module
- All 7 test cases passing

**Safety:**
- Zero data loss (migration verification)
- Default dry-run prevents accidents
- Clear error messages on failures

**User Experience:**
- Single command: `ce cleanup --execute`
- Preview actions with `ce cleanup --dry-run`
- Clear status output for each directory
