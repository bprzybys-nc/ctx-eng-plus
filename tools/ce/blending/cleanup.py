"""Phase D: Cleanup module for safe legacy directory removal."""

import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


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

    print("\n" + "=" * 60)
    print("🧹 Legacy Directory Cleanup")
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


def verify_migration_complete(
    legacy_dir: Path,
    target_project: Path
) -> Tuple[bool, List[str]]:
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
        if relative_path.parts[0] == "PRPs":
            ce_path = ce_dir / relative_path
        # For examples: user subdirectory
        elif relative_path.parts[0] == "examples":
            ce_path = ce_dir / "examples" / "user" / "/".join(relative_path.parts[1:])
        # For context-engineering: .ce/ itself
        elif relative_path.parts[0] == "context-engineering":
            ce_path = ce_dir / "/".join(relative_path.parts[1:])
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
