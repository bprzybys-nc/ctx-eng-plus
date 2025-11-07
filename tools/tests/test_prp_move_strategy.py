"""Unit tests for PRPMoveStrategy recursive glob behavior.

Tests PRP-39: Fix PRPMoveStrategy to Handle Subdirectories
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from ce.blending.strategies.simple import PRPMoveStrategy


@pytest.fixture
def temp_dirs():
    """Create temporary source and target directories."""
    source = Path(tempfile.mkdtemp(prefix="prp_source_"))
    target = Path(tempfile.mkdtemp(prefix="prp_target_"))

    yield source, target

    # Cleanup
    shutil.rmtree(source, ignore_errors=True)
    shutil.rmtree(target, ignore_errors=True)


def create_prp_file(path: Path, status: str = "completed"):
    """Create a PRP file with given status."""
    content = f"""---
prp_id: TEST-1
title: Test PRP
status: {status}
---

# Test PRP

Test content.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_recursive_glob(temp_dirs):
    """Test that glob(**/*.md) finds files in subdirectories."""
    source, target = temp_dirs

    # Create PRPs in nested structure
    create_prp_file(source / "PRP-1.md")
    create_prp_file(source / "executed" / "PRP-2.md", status="completed")
    create_prp_file(source / "feature-requests" / "PRP-3.md", status="pending")
    create_prp_file(source / "system" / "PRP-4.md", status="completed")

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True
    assert result["prps_moved"] == 4, "All 4 PRPs should be moved"
    assert result["prps_skipped"] == 0


def test_preserve_structure(temp_dirs):
    """Test that executed/ and feature-requests/ subdirectories are preserved."""
    source, target = temp_dirs

    # Create PRPs in standard subdirectories
    create_prp_file(source / "executed" / "PRP-1.md", status="completed")
    create_prp_file(source / "feature-requests" / "PRP-2.md", status="pending")
    create_prp_file(source / "system" / "PRP-3.md", status="completed")

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True

    # Verify structure preserved
    assert (target / "executed" / "PRP-1.md").exists(), "executed/ should be preserved"
    assert (target / "feature-requests" / "PRP-2.md").exists(), "feature-requests/ should be preserved"
    assert (target / "system" / "PRP-3.md").exists(), "system/ should be preserved"


def test_mixed_structure(temp_dirs):
    """Test that both root-level and subdirectory PRPs are processed."""
    source, target = temp_dirs

    # Mix of root and subdirectory PRPs
    create_prp_file(source / "PRP-root.md", status="completed")
    create_prp_file(source / "executed" / "PRP-subdir.md", status="completed")

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True
    assert result["prps_moved"] == 2

    # Root-level PRP classified by content
    assert (target / "executed" / "PRP-root.md").exists(), "Root PRP should be classified by status"

    # Subdirectory PRP preserves structure
    assert (target / "executed" / "PRP-subdir.md").exists(), "Subdir PRP should preserve structure"


def test_subdirectory_overrides_content(temp_dirs):
    """Test that subdirectory name takes precedence over content status."""
    source, target = temp_dirs

    # PRP in executed/ but content says "pending" (feature-requests)
    prp_path = source / "executed" / "PRP-conflict.md"
    content = """---
prp_id: TEST-CONFLICT
title: Test Conflict
status: pending
---

# Test

Should go to executed/ (trust subdirectory, not content status).
"""
    prp_path.parent.mkdir(parents=True, exist_ok=True)
    prp_path.write_text(content)

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True

    # Should be in executed/ (subdirectory wins)
    assert (target / "executed" / "PRP-conflict.md").exists(), "Subdirectory should override content"
    assert not (target / "feature-requests" / "PRP-conflict.md").exists(), "Should not be in feature-requests/"


def test_hash_deduplication(temp_dirs):
    """Test that identical PRPs are skipped (hash-based dedupe)."""
    source, target = temp_dirs

    content = """---
prp_id: TEST-DUP
title: Test Duplicate
status: completed
---

# Test

Same content.
"""

    # Create identical PRP in source
    (source / "executed").mkdir(parents=True, exist_ok=True)
    (source / "executed" / "PRP-dup.md").write_text(content)

    # Pre-populate target with identical content
    (target / "executed").mkdir(parents=True, exist_ok=True)
    (target / "executed" / "PRP-dup.md").write_text(content)

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True
    assert result["prps_moved"] == 0, "Identical PRP should not be moved"
    assert result["prps_skipped"] == 1, "Identical PRP should be skipped"


def test_deeply_nested_prps(temp_dirs):
    """Test that deeply nested PRPs (>1 level) are handled correctly."""
    source, target = temp_dirs

    # Create deeply nested PRP: PRPs/2024/Q4/executed/PRP-1.md
    deep_path = source / "2024" / "Q4" / "executed" / "PRP-deep.md"
    create_prp_file(deep_path, status="completed")

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True
    assert result["prps_moved"] == 1

    # Should flatten to target/executed/PRP-deep.md (parent is "executed")
    assert (target / "executed" / "PRP-deep.md").exists(), "Deep nesting should flatten to executed/"


def test_error_handling(temp_dirs):
    """Test that errors are captured without crashing."""
    source, target = temp_dirs

    # Create a valid PRP
    create_prp_file(source / "PRP-valid.md", status="completed")

    # Create an invalid PRP (unreadable file - will fail on read)
    invalid_path = source / "PRP-invalid.md"
    invalid_path.parent.mkdir(parents=True, exist_ok=True)
    invalid_path.write_text("invalid content")
    invalid_path.chmod(0o000)  # Make unreadable

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    # Should continue processing despite error
    assert len(result["errors"]) > 0, "Should capture error"
    assert "PRP-invalid.md" in str(result["errors"][0]), "Error should mention problematic file"

    # Cleanup
    invalid_path.chmod(0o644)


def test_user_header_addition(temp_dirs):
    """Test that PRPs without YAML headers get 'type: user' added."""
    source, target = temp_dirs

    # Create PRP without YAML header
    prp_path = source / "executed" / "PRP-no-header.md"
    prp_path.parent.mkdir(parents=True, exist_ok=True)
    prp_path.write_text("# PRP without header\n\nSome content.")

    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    assert result["success"] is True

    # Check that target file has user header
    target_content = (target / "executed" / "PRP-no-header.md").read_text()
    assert target_content.startswith("---"), "Should have YAML header"
    assert "type: user" in target_content, "Should have 'type: user'"
    assert "source: target-project" in target_content, "Should have source annotation"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
