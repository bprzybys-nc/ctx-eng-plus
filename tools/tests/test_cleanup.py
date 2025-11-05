"""Tests for cleanup module (Phase D)."""

import pytest
from pathlib import Path
import shutil
from ce.blending.cleanup import cleanup_legacy_dirs, verify_migration_complete, find_unmigrated_files


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


def test_cleanup_multiple_directories(tmp_path):
    """Test cleanup handles multiple legacy directories."""
    # Setup PRPs
    prps_dir = tmp_path / "PRPs"
    prps_dir.mkdir()
    (prps_dir / "test1.md").write_text("# Test 1")

    # Setup examples
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "test2.py").write_text("# Test 2")

    # Setup context-engineering
    ce_old = tmp_path / "context-engineering"
    ce_old.mkdir()
    (ce_old / "test3.md").write_text("# Test 3")

    # Migrate all to .ce/
    ce_dir = tmp_path / ".ce"

    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "test1.md").write_text("# Test 1")

    ce_examples = ce_dir / "examples" / "user"
    ce_examples.mkdir(parents=True)
    (ce_examples / "test2.py").write_text("# Test 2")

    (ce_dir / "test3.md").write_text("# Test 3")

    # Run cleanup
    status = cleanup_legacy_dirs(tmp_path, dry_run=False)

    # Verify all removed
    assert not prps_dir.exists()
    assert not examples_dir.exists()
    assert not ce_old.exists()

    assert status["PRPs"] == True
    assert status["examples"] == True
    assert status["context-engineering"] == True


def test_cleanup_nested_files(tmp_path):
    """Test cleanup handles nested directory structures."""
    # Setup nested structure
    legacy_dir = tmp_path / "PRPs"
    executed_dir = legacy_dir / "executed"
    executed_dir.mkdir(parents=True)
    (executed_dir / "PRP-1.md").write_text("# PRP 1")
    (executed_dir / "PRP-2.md").write_text("# PRP 2")

    feature_requests_dir = legacy_dir / "feature-requests"
    feature_requests_dir.mkdir(parents=True)
    (feature_requests_dir / "PRP-3.md").write_text("# PRP 3")

    # Migrate to .ce/
    ce_dir = tmp_path / ".ce"
    ce_executed = ce_dir / "PRPs" / "executed"
    ce_executed.mkdir(parents=True)
    (ce_executed / "PRP-1.md").write_text("# PRP 1")
    (ce_executed / "PRP-2.md").write_text("# PRP 2")

    ce_feature = ce_dir / "PRPs" / "feature-requests"
    ce_feature.mkdir(parents=True)
    (ce_feature / "PRP-3.md").write_text("# PRP 3")

    # Run cleanup
    status = cleanup_legacy_dirs(tmp_path, dry_run=False)

    # Verify removed
    assert not legacy_dir.exists()
    assert status["PRPs"] == True


def test_find_unmigrated_files(tmp_path):
    """Test find_unmigrated_files function."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    (legacy_dir / "file1.md").write_text("# File 1")
    (legacy_dir / "file2.md").write_text("# File 2")
    (legacy_dir / "file3.md").write_text("# File 3")

    ce_dir = tmp_path / ".ce"
    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "file1.md").write_text("# File 1")
    (ce_prps / "file3.md").write_text("# File 3")
    # file2.md NOT migrated

    # Find unmigrated
    unmigrated = find_unmigrated_files(legacy_dir, ce_dir)

    assert len(unmigrated) == 1
    assert "file2.md" in unmigrated[0]


def test_find_unmigrated_files_empty_legacy(tmp_path):
    """Test find_unmigrated_files with non-existent legacy dir."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    ce_dir = tmp_path / ".ce"
    ce_dir.mkdir()

    # Find unmigrated
    unmigrated = find_unmigrated_files(legacy_dir, ce_dir)

    assert len(unmigrated) == 0


def test_cleanup_partial_failure(tmp_path):
    """Test cleanup aborts on first unmigrated directory."""
    # Setup first directory (will succeed)
    prps_dir = tmp_path / "PRPs"
    prps_dir.mkdir()
    (prps_dir / "test.md").write_text("# Test")

    ce_dir = tmp_path / ".ce"
    ce_prps = ce_dir / "PRPs"
    ce_prps.mkdir(parents=True)
    (ce_prps / "test.md").write_text("# Test")

    # Setup second directory (will fail - unmigrated)
    examples_dir = tmp_path / "examples"
    examples_dir.mkdir()
    (examples_dir / "unmigrated.py").write_text("# Unmigrated")
    # NOT migrated to .ce/

    # Run cleanup (should fail on examples)
    with pytest.raises(ValueError, match="unmigrated files detected"):
        cleanup_legacy_dirs(tmp_path, dry_run=False)

    # First directory was already removed before we hit the second one
    # This is expected behavior - cleanup processes directories sequentially
    assert not prps_dir.exists()
    # Second directory should still exist since it failed verification
    assert examples_dir.exists()


def test_verify_migration_complete_empty_legacy(tmp_path):
    """Test verify_migration_complete with empty legacy directory."""
    # Setup
    legacy_dir = tmp_path / "PRPs"
    legacy_dir.mkdir()
    # No files

    ce_dir = tmp_path / ".ce"
    ce_dir.mkdir()

    # Verify
    is_complete, unmigrated = verify_migration_complete(legacy_dir, tmp_path)

    assert is_complete == True
    assert len(unmigrated) == 0
