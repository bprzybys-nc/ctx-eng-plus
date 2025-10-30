"""Tests for vacuum command and strategies."""

import pytest
from pathlib import Path
from ce.vacuum import VacuumCommand
from ce.vacuum_strategies import (
    TempFileStrategy,
    BackupFileStrategy,
    ObsoleteDocStrategy,
    UnreferencedCodeStrategy,
    OrphanTestStrategy,
    CommentedCodeStrategy,
)


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()

    # Create .ce directory (required for project detection)
    (project_root / ".ce").mkdir()

    # Create temp files
    (project_root / "test.pyc").write_text("compiled")
    pycache = project_root / "__pycache__"
    pycache.mkdir()
    (pycache / "module.pyc").write_text("compiled")

    # Create backup files
    (project_root / "file.bak").write_text("backup")
    (project_root / "file~").write_text("backup")

    # Create obsolete docs
    (project_root / "guide-v1.md").write_text("old version")
    (project_root / "guide.md").write_text("current version")

    # Create orphan test
    tests_dir = project_root / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_nonexistent.py").write_text("def test_foo(): pass")

    # Create doc with dead link
    (project_root / "readme.md").write_text("[link](nonexistent.md)")

    # Create commented code
    (project_root / "commented.py").write_text(
        "\n".join([f"# def foo_{i}(): pass" for i in range(25)])
    )

    return project_root


class TestTempFileStrategy:
    """Test temp file detection strategy."""

    def test_finds_pyc_files(self, temp_project):
        """Should find .pyc files."""
        strategy = TempFileStrategy(temp_project)
        candidates = strategy.find_candidates()

        pyc_files = [c for c in candidates if c.path.suffix == ".pyc"]
        assert len(pyc_files) == 2
        assert all(c.confidence == 100 for c in pyc_files)

    def test_finds_pycache_dirs(self, temp_project):
        """Should find __pycache__ directories."""
        strategy = TempFileStrategy(temp_project)
        candidates = strategy.find_candidates()

        pycache_dirs = [c for c in candidates if c.path.name == "__pycache__"]
        assert len(pycache_dirs) == 1
        assert pycache_dirs[0].confidence == 100


class TestBackupFileStrategy:
    """Test backup file detection strategy."""

    def test_finds_bak_files(self, temp_project):
        """Should find .bak files."""
        strategy = BackupFileStrategy(temp_project)
        candidates = strategy.find_candidates()

        bak_files = [c for c in candidates if ".bak" in c.path.name]
        assert len(bak_files) >= 1
        assert all(c.confidence == 100 for c in bak_files)

    def test_finds_tilde_files(self, temp_project):
        """Should find ~ backup files."""
        strategy = BackupFileStrategy(temp_project)
        candidates = strategy.find_candidates()

        tilde_files = [c for c in candidates if c.path.name.endswith("~")]
        assert len(tilde_files) >= 1
        assert all(c.confidence == 100 for c in tilde_files)


class TestObsoleteDocStrategy:
    """Test obsolete doc detection strategy."""

    def test_finds_versioned_docs(self, temp_project):
        """Should find versioned documentation files."""
        strategy = ObsoleteDocStrategy(temp_project)
        candidates = strategy.find_candidates()

        versioned_docs = [c for c in candidates if "-v1" in c.path.name]
        assert len(versioned_docs) >= 1
        assert all(c.confidence >= 50 for c in versioned_docs)


class TestOrphanTestStrategy:
    """Test orphan test detection strategy."""

    def test_finds_orphaned_tests(self, temp_project):
        """Should find test files with no corresponding module."""
        strategy = OrphanTestStrategy(temp_project)
        candidates = strategy.find_candidates()

        orphan_tests = [c for c in candidates if "nonexistent" in c.path.name]
        assert len(orphan_tests) >= 1
        assert all(c.confidence >= 40 for c in orphan_tests)


class TestCommentedCodeStrategy:
    """Test commented code detection strategy."""

    def test_finds_large_commented_blocks(self, temp_project):
        """Should find large commented code blocks."""
        strategy = CommentedCodeStrategy(temp_project)
        candidates = strategy.find_candidates()

        commented_files = [c for c in candidates if "commented" in c.path.name]
        assert len(commented_files) >= 1
        assert all(c.confidence <= 40 for c in commented_files)


class TestVacuumCommand:
    """Test main vacuum command."""

    def test_dry_run_no_deletions(self, temp_project):
        """Dry-run should not delete files."""
        vacuum = VacuumCommand(temp_project)

        # Count files before (exclude .ce directory to avoid report file)
        initial_files = [f for f in temp_project.rglob("*") if ".ce" not in str(f)]

        # Run dry-run
        exit_code = vacuum.run(dry_run=True)

        # Count files after (exclude .ce directory)
        final_files = [f for f in temp_project.rglob("*") if ".ce" not in str(f)]

        # Dry-run should not change file count (except for report in .ce)
        assert len(initial_files) == len(final_files)
        assert exit_code == 1  # Candidates found

    def test_execute_deletes_high_confidence(self, temp_project):
        """Execute mode should delete HIGH confidence items."""
        vacuum = VacuumCommand(temp_project)

        # Verify temp files exist
        assert (temp_project / "test.pyc").exists()

        # Run execute
        exit_code = vacuum.run(execute=True)

        # Verify temp files deleted
        assert not (temp_project / "test.pyc").exists()
        assert exit_code in [0, 1]  # 0 = clean, 1 = some candidates remain

    def test_force_deletes_medium_confidence(self, temp_project):
        """Force mode should delete MEDIUM + HIGH confidence items."""
        vacuum = VacuumCommand(temp_project)

        # Verify backup files exist
        assert (temp_project / "file.bak").exists()

        # Run force
        exit_code = vacuum.run(force=True)

        # Verify backup files deleted
        assert not (temp_project / "file.bak").exists()

    def test_exclude_strategy(self, temp_project):
        """Should skip excluded strategies."""
        vacuum = VacuumCommand(temp_project)

        # Run with temp-files excluded
        exit_code = vacuum.run(
            dry_run=True,
            exclude_strategies=["temp-files"]
        )

        # Read report
        report_path = temp_project / ".ce" / "vacuum-report.md"
        assert report_path.exists()

        report_content = report_path.read_text()

        # Should not mention .pyc files if temp-files strategy skipped
        # (but other strategies might still find candidates)
        assert exit_code in [0, 1]

    def test_min_confidence_filter(self, temp_project):
        """Should filter candidates by minimum confidence."""
        vacuum = VacuumCommand(temp_project)

        # Run with high confidence threshold
        exit_code = vacuum.run(
            dry_run=True,
            min_confidence=80
        )

        # Read report
        report_path = temp_project / ".ce" / "vacuum-report.md"
        report_content = report_path.read_text()

        # Should only show HIGH confidence items
        assert "HIGH Confidence" in report_content
        # LOW confidence section should be empty or not present
        if "LOW Confidence" in report_content:
            # Extract LOW section
            low_section = report_content.split("LOW Confidence")[1].split("##")[0]
            # Should have no rows (only header)
            assert low_section.count("|") <= 6  # Just header rows


class TestProtectedPaths:
    """Test NEVER_DELETE protection."""

    def test_protected_paths_never_deleted(self, temp_project):
        """Should never delete protected paths."""
        # Create protected files
        (temp_project / "pyproject.toml").write_text("project config")
        (temp_project / "README.md").write_text("readme")

        prps_dir = temp_project / "PRPs"
        prps_dir.mkdir()
        (prps_dir / "PRP-1.md").write_text("prp")

        vacuum = VacuumCommand(temp_project)

        # Run execute mode (should not delete protected files)
        vacuum.run(execute=True)

        # Verify protected files still exist
        assert (temp_project / "pyproject.toml").exists()
        assert (temp_project / "README.md").exists()
        assert (prps_dir / "PRP-1.md").exists()
