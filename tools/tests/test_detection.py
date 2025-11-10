"""Tests for legacy file detection module."""

import pytest
from pathlib import Path
from ce.blending.detection import LegacyFileDetector, SEARCH_PATTERNS, GARBAGE_PATTERNS


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project structure for testing."""
    project = tmp_path / "project"
    project.mkdir()

    # Create directories
    (project / "PRPs").mkdir()
    (project / "examples").mkdir()
    (project / ".claude" / "commands").mkdir(parents=True)
    (project / ".serena" / "memories").mkdir(parents=True)

    return project


@pytest.fixture
def detector(temp_project):
    """Create detector instance for testing."""
    return LegacyFileDetector(temp_project)


def test_empty_project(detector):
    """Test detection on empty project (greenfield)."""
    inventory = detector.scan_all()

    # Should return all 6 domain keys
    assert set(inventory.keys()) == set(SEARCH_PATTERNS.keys())

    # All domains should be empty lists
    for domain, files in inventory.items():
        assert isinstance(files, list)
        assert len(files) == 0


def test_detect_prps(temp_project, detector):
    """Test detection of PRPs in multiple locations."""
    # Create PRPs in legacy location
    (temp_project / "PRPs" / "executed").mkdir()
    (temp_project / "PRPs" / "executed" / "PRP-1-feature.md").write_text("# PRP-1")
    (temp_project / "PRPs" / "feature-requests").mkdir()
    (temp_project / "PRPs" / "feature-requests" / "PRP-2-next.md").write_text("# PRP-2")

    inventory = detector.scan_all()

    assert len(inventory["prps"]) == 2
    names = [p.name for p in inventory["prps"]]
    assert "PRP-1-feature.md" in names
    assert "PRP-2-next.md" in names


def test_detect_examples(temp_project, detector):
    """Test detection of examples in multiple locations."""
    # Create examples
    (temp_project / "examples" / "example-1.md").write_text("# Example 1")
    (temp_project / "examples" / "templates").mkdir()
    (temp_project / "examples" / "templates" / "template-1.md").write_text("# Template")

    inventory = detector.scan_all()

    assert len(inventory["examples"]) == 2
    names = [p.name for p in inventory["examples"]]
    assert "example-1.md" in names
    assert "template-1.md" in names


def test_detect_ce_10_structure(temp_project, detector):
    """Test detection of CE 1.0 context-engineering/ structure."""
    # Create CE 1.0 structure
    ce_root = temp_project / "context-engineering"
    (ce_root / "PRPs" / "executed").mkdir(parents=True)
    (ce_root / "PRPs" / "executed" / "PRP-OLD-1.md").write_text("# Old PRP")
    (ce_root / "examples").mkdir()
    (ce_root / "examples" / "old-example.md").write_text("# Old Example")

    inventory = detector.scan_all()

    # Should detect both PRPs and examples from CE 1.0
    assert len(inventory["prps"]) == 1
    assert inventory["prps"][0].name == "PRP-OLD-1.md"
    assert len(inventory["examples"]) == 1
    assert inventory["examples"][0].name == "old-example.md"


def test_resolve_symlinks(temp_project, detector):
    """Test CLAUDE.md symlink resolution."""
    # Create real file
    real_file = temp_project / "real-claude.md"
    real_file.write_text("# Real CLAUDE.md")

    # Create symlink
    symlink = temp_project / "CLAUDE.md"
    symlink.symlink_to(real_file)

    inventory = detector.scan_all()

    # Should resolve symlink to real file
    assert len(inventory["claude_md"]) == 1
    assert inventory["claude_md"][0].resolve() == real_file.resolve()


def test_circular_symlinks(temp_project, detector):
    """Test circular symlink detection."""
    # Create circular symlinks
    symlink_a = temp_project / "link-a.md"
    symlink_b = temp_project / "link-b.md"

    # Create initial symlink
    symlink_a.write_text("temp")
    symlink_b.symlink_to(symlink_a)

    # Make circular by replacing symlink_a with link to symlink_b
    symlink_a.unlink()
    symlink_a.symlink_to(symlink_b)

    # Should not crash on circular symlinks
    result = detector._resolve_symlink(symlink_a)
    # Result should be None (circular detected)
    assert result is None or result.exists()


def test_broken_symlinks(temp_project, detector):
    """Test broken symlink handling."""
    # Create broken symlink
    symlink = temp_project / "CLAUDE.md"
    symlink.symlink_to(temp_project / "nonexistent.md")

    inventory = detector.scan_all()

    # Should handle broken symlink gracefully (skip it)
    assert len(inventory["claude_md"]) == 0


def test_garbage_filtering_reports(temp_project, detector):
    """Test filtering of REPORT files."""
    (temp_project / "PRPs" / "PRP-1-feature.md").write_text("# PRP-1")
    (temp_project / "PRPs" / "PRP-1-REPORT.md").write_text("# Report")
    (temp_project / "PRPs" / "INITIAL-REPORT.md").write_text("# Initial")

    inventory = detector.scan_all()

    # Should only include real PRP, not reports
    assert len(inventory["prps"]) == 1
    assert inventory["prps"][0].name == "PRP-1-feature.md"


def test_garbage_filtering_summaries(temp_project, detector):
    """Test filtering of summary and analysis files."""
    (temp_project / "PRPs" / "PRP-1-feature.md").write_text("# PRP-1")
    (temp_project / "PRPs" / "PRP-1-summary.md").write_text("# Summary")
    (temp_project / "PRPs" / "project-analysis.md").write_text("# Analysis")
    (temp_project / "PRPs" / "PLAN-feature.md").write_text("# Plan")

    inventory = detector.scan_all()

    # Should only include real PRP
    assert len(inventory["prps"]) == 1
    assert inventory["prps"][0].name == "PRP-1-feature.md"


def test_backup_filtering(temp_project, detector):
    """Test filtering of backup files."""
    (temp_project / "PRPs" / "PRP-1-feature.md").write_text("# PRP-1")
    (temp_project / "PRPs" / "PRP-1-feature.md.backup").write_text("# Backup")
    (temp_project / "PRPs" / "PRP-2~").write_text("# Temp")
    (temp_project / "PRPs" / "PRP-3.tmp").write_text("# Tmp")

    inventory = detector.scan_all()

    # Should only include real PRP
    assert len(inventory["prps"]) == 1
    assert inventory["prps"][0].name == "PRP-1-feature.md"


def test_full_scan_integration(temp_project, detector):
    """Test full end-to-end scan with mixed content."""
    # Create diverse content
    (temp_project / "PRPs" / "PRP-1.md").write_text("# PRP-1")
    (temp_project / "PRPs" / "PRP-2-REPORT.md").write_text("# Report")
    (temp_project / "examples" / "example-1.md").write_text("# Example")
    (temp_project / ".claude" / "commands" / "test-cmd.md").write_text("# Command")
    (temp_project / ".serena" / "memories" / "memory-1.md").write_text("# Memory")

    # Create CLAUDE.md as regular file
    (temp_project / "CLAUDE.md").write_text("# Project Guide")

    # Create settings file
    (temp_project / ".claude" / "settings.local.json").write_text("{}")

    inventory = detector.scan_all()

    # Verify all domains have correct counts
    assert len(inventory["prps"]) == 1  # PRP-1 only (report filtered)
    assert len(inventory["examples"]) == 1  # example-1
    assert len(inventory["claude_md"]) == 1  # CLAUDE.md
    assert len(inventory["settings"]) == 1  # settings.local.json
    assert len(inventory["commands"]) == 1  # test-cmd.md
    assert len(inventory["memories"]) == 1  # memory-1.md

    # Verify no duplicates
    all_files = []
    for files in inventory.values():
        all_files.extend(files)
    assert len(all_files) == len(set(all_files))


def test_missing_directories(temp_project, detector):
    """Test graceful handling of missing directories."""
    # Remove all directories
    for item in temp_project.iterdir():
        if item.is_dir():
            import shutil
            shutil.rmtree(item)

    inventory = detector.scan_all()

    # Should return empty inventory without crashing
    assert all(len(files) == 0 for files in inventory.values())


def test_permission_denied(temp_project, detector, monkeypatch):
    """Test handling of permission errors."""
    # Create directory with file
    (temp_project / "PRPs" / "PRP-1.md").write_text("# PRP-1")

    # Mock rglob to raise PermissionError
    original_rglob = Path.rglob

    def mock_rglob(self, pattern):
        raise PermissionError("Access denied")

    monkeypatch.setattr(Path, "rglob", mock_rglob)

    # Should handle permission error gracefully
    inventory = detector.scan_all()
    # Will return empty due to mocked error
    assert len(inventory["prps"]) == 0


def test_is_garbage_method():
    """Test _is_garbage method directly."""
    detector = LegacyFileDetector(Path("/tmp"))

    # Valid files
    assert not detector._is_garbage(Path("PRP-1-feature.md"))
    assert not detector._is_garbage(Path("example-1.md"))
    assert not detector._is_garbage(Path("memory-1.md"))

    # Garbage files
    assert detector._is_garbage(Path("PRP-1-REPORT.md"))
    assert detector._is_garbage(Path("INITIAL-setup.md"))
    assert detector._is_garbage(Path("project-summary.md"))
    assert detector._is_garbage(Path("code-analysis.md"))
    assert detector._is_garbage(Path("PLAN-feature.md"))
    assert detector._is_garbage(Path("file.backup"))
    assert detector._is_garbage(Path("file~"))
    assert detector._is_garbage(Path("file.tmp"))
    assert detector._is_garbage(Path("file.log"))


def test_detector_initialization():
    """Test detector initialization with path resolution."""
    # Test with relative path
    detector = LegacyFileDetector(Path("."))
    assert detector.project_root.is_absolute()

    # Test with absolute path
    abs_path = Path("/tmp/test")
    detector = LegacyFileDetector(abs_path)
    assert detector.project_root.is_absolute()
    assert detector.visited_symlinks == set()


def test_detect_bare_context_engineering_with_config(temp_project):
    """Test detection of bare context-engineering/ root-level files with config."""
    from ce.config_loader import BlendConfig
    import tempfile
    import yaml

    # Create a config that includes bare context-engineering/ for prps
    config_content = {
        "detection": {
            "domains": {
                "prps": {
                    "legacy_paths": [
                        "PRPs/",
                        "context-engineering/PRPs/",
                        "context-engineering/"
                    ],
                    "search_patterns": ["**/*.md"]
                },
                "examples": {
                    "legacy_paths": [
                        "examples/",
                        "context-engineering/examples/"
                    ],
                    "search_patterns": ["**/*.md", "**/*.py"]
                },
                "claude_md": {"legacy_paths": ["CLAUDE.md"]},
                "settings": {"legacy_paths": [".claude/settings.local.json"]},
                "commands": {"legacy_paths": [".claude/commands/"]},
                "memories": {"legacy_paths": [".serena/memories/"]}
            }
        },
        # Minimal directories section required for config validation
        "directories": {
            "output": {},
            "framework": {},
            "legacy": []
        }
    }

    # Write config to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
        yaml.dump(config_content, f)
        config_path = f.name

    try:
        config = BlendConfig(Path(config_path))
        detector = LegacyFileDetector(temp_project, config)

        # Create bare context-engineering/ file (not in subdirectory)
        ce_root = temp_project / "context-engineering"
        ce_root.mkdir()
        project_master = ce_root / "PROJECT_MASTER.md"
        project_master.write_text("# Project Master")

        # Also create subdirectory files
        (ce_root / "PRPs").mkdir()
        (ce_root / "PRPs" / "PRP-1.md").write_text("# PRP-1")
        (ce_root / "examples").mkdir()
        (ce_root / "examples" / "example-1.md").write_text("# Example")

        inventory = detector.scan_all()

        # Should detect bare context-engineering/ files (PROJECT_MASTER.md)
        # plus subdirectory files (PRP-1.md, example-1.md)
        assert len(inventory["prps"]) >= 2
        assert len(inventory["examples"]) == 1

        # Verify specific files were found
        prp_names = [p.name for p in inventory["prps"]]
        assert "PROJECT_MASTER.md" in prp_names
        assert "PRP-1.md" in prp_names

    finally:
        # Clean up
        import os
        os.unlink(config_path)
