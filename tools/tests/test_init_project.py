#!/usr/bin/env python3
"""
Unit tests for ce.init_project module.

Tests ProjectInitializer class with 4 phases:
- extract: Unpack repomix package
- blend: Merge framework + user files
- initialize: Install Python dependencies
- verify: Validate installation
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, Mock

import pytest

from ce.init_project import ProjectInitializer


@pytest.fixture
def temp_project():
    """Create temporary project directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def ctx_eng_root():
    """Get ctx-eng-plus root directory."""
    return Path(__file__).parent.parent.parent.resolve()


@pytest.fixture
def initializer(temp_project):
    """Create ProjectInitializer instance for testing."""
    return ProjectInitializer(temp_project, dry_run=False)


@pytest.fixture
def dry_run_initializer(temp_project):
    """Create ProjectInitializer instance in dry-run mode."""
    return ProjectInitializer(temp_project, dry_run=True)


class TestProjectInitializerInit:
    """Test ProjectInitializer initialization."""

    def test_init_creates_paths(self, temp_project):
        """Test that __init__ sets up correct paths."""
        init = ProjectInitializer(temp_project)

        assert init.target_project == temp_project.resolve()
        # Use resolve() to handle macOS /var vs /private/var symlink
        assert init.ce_dir.resolve() == (temp_project / ".ce").resolve()
        assert init.tools_dir.resolve() == (temp_project / ".ce" / "tools").resolve()
        assert init.dry_run is False

    def test_init_dry_run_mode(self, temp_project):
        """Test that dry_run flag is set correctly."""
        init = ProjectInitializer(temp_project, dry_run=True)
        assert init.dry_run is True

    def test_init_resolves_relative_paths(self):
        """Test that relative paths are resolved to absolute."""
        with tempfile.TemporaryDirectory() as tmpdir:
            rel_path = Path(tmpdir) / "subdir"
            rel_path.mkdir()

            init = ProjectInitializer(rel_path)
            assert init.target_project.is_absolute()


class TestProjectInitializerRun:
    """Test ProjectInitializer.run() orchestration method."""

    def test_run_all_phases(self, initializer):
        """Test that run('all') executes all 4 phases."""
        with patch.object(initializer, 'extract', return_value={"success": True}) as mock_extract, \
             patch.object(initializer, 'blend', return_value={"success": True}) as mock_blend, \
             patch.object(initializer, 'initialize', return_value={"success": True}) as mock_init, \
             patch.object(initializer, 'verify', return_value={"success": True}) as mock_verify:

            results = initializer.run(phase="all")

            assert "extract" in results
            assert "blend" in results
            assert "initialize" in results
            assert "verify" in results

            mock_extract.assert_called_once()
            mock_blend.assert_called_once()
            mock_init.assert_called_once()
            mock_verify.assert_called_once()

    def test_run_single_phase(self, initializer):
        """Test that run(<phase>) executes only specified phase."""
        with patch.object(initializer, 'extract', return_value={"success": True}) as mock_extract:
            results = initializer.run(phase="extract")

            assert "extract" in results
            assert len(results) == 1
            mock_extract.assert_called_once()

    def test_run_invalid_phase_raises_error(self, initializer):
        """Test that invalid phase raises ValueError."""
        with pytest.raises(ValueError, match="Invalid phase"):
            initializer.run(phase="invalid_phase")

    def test_run_accepts_all_valid_phases(self, initializer):
        """Test that all valid phases are accepted."""
        valid_phases = ["all", "extract", "blend", "initialize", "verify"]

        for phase in valid_phases:
            with patch.object(initializer, phase if phase != "all" else "extract", return_value={"success": True}), \
                 patch.object(initializer, "blend", return_value={"success": True}), \
                 patch.object(initializer, "initialize", return_value={"success": True}), \
                 patch.object(initializer, "verify", return_value={"success": True}):

                result = initializer.run(phase=phase)
                assert isinstance(result, dict)


class TestProjectInitializerExtract:
    """Test ProjectInitializer.extract() phase."""

    def test_extract_missing_infrastructure_xml(self, initializer):
        """Test extract fails gracefully when ce-infrastructure.xml not found."""
        # Mock missing infrastructure XML
        initializer.infrastructure_xml = Path("/nonexistent/ce-infrastructure.xml")

        result = initializer.extract()

        assert result["success"] is False
        assert "ce-infrastructure.xml not found" in result["message"]
        assert "🔧" in result["message"]

    def test_extract_dry_run_mode(self, dry_run_initializer, temp_project):
        """Test extract in dry-run mode doesn't modify files."""
        # Create a fake infrastructure XML for testing
        fake_xml = temp_project / "ce-infrastructure.xml"
        fake_xml.write_text("<files></files>")
        dry_run_initializer.infrastructure_xml = fake_xml

        result = dry_run_initializer.extract()

        assert result["success"] is True
        assert "[DRY-RUN]" in result["message"]
        assert not dry_run_initializer.ce_dir.exists()

    def test_extract_existing_ce_directory(self, initializer, temp_project):
        """Test extract warns when .ce/ already exists."""
        # Create a fake infrastructure XML
        fake_xml = temp_project / "ce-infrastructure.xml"
        fake_xml.write_text("<files></files>")
        initializer.infrastructure_xml = fake_xml

        # Create existing .ce/ directory
        initializer.ce_dir.mkdir(parents=True)

        result = initializer.extract()

        assert result["success"] is False
        assert "already exists" in result["message"]
        assert "🔧" in result["message"]

    @patch('ce.repomix_unpack.extract_files')
    def test_extract_success(self, mock_extract_files, initializer, temp_project):
        """Test successful extraction."""
        # Mock extract_files to return success
        mock_extract_files.return_value = 50

        # Create a fake infrastructure XML
        fake_xml = temp_project / "ce-infrastructure.xml"
        fake_xml.write_text("<files></files>")
        initializer.infrastructure_xml = fake_xml

        # Mock shutil operations to avoid actual file operations
        with patch('ce.init_project.shutil'):
            result = initializer.extract()

            assert result["success"] is True
            assert result["files_extracted"] == 50
            assert "✅" in result["message"]

    @patch('ce.repomix_unpack.extract_files')
    def test_extract_no_files_extracted(self, mock_extract_files, initializer, temp_project):
        """Test extract handles zero files extracted."""
        mock_extract_files.return_value = 0

        # Create a fake infrastructure XML
        fake_xml = temp_project / "ce-infrastructure.xml"
        fake_xml.write_text("<files></files>")
        initializer.infrastructure_xml = fake_xml

        result = initializer.extract()

        assert result["success"] is False
        assert "No files extracted" in result["message"]


class TestProjectInitializerBlend:
    """Test ProjectInitializer.blend() phase."""

    def test_blend_dry_run_mode(self, dry_run_initializer):
        """Test blend in dry-run mode shows command without executing."""
        result = dry_run_initializer.blend()

        assert result["success"] is True
        assert "[DRY-RUN]" in result["stdout"]
        assert "uv run ce blend" in result["stdout"]

    @patch('ce.init_project.subprocess.run')
    def test_blend_success(self, mock_run, initializer):
        """Test successful blend phase."""
        # Mock subprocess success
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Blend complete"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = initializer.blend()

        assert result["success"] is True
        assert "✅" in result["message"]
        mock_run.assert_called_once()

    @patch('ce.init_project.subprocess.run')
    def test_blend_failure(self, mock_run, initializer):
        """Test blend phase handles command failure."""
        # Mock subprocess failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Blend error"
        mock_run.return_value = mock_result

        result = initializer.blend()

        assert result["success"] is False
        assert "❌" in result["message"]
        assert "Blend phase failed" in result["message"]

    @patch('ce.init_project.subprocess.run')
    def test_blend_timeout(self, mock_run, initializer):
        """Test blend phase handles timeout."""
        # Mock subprocess timeout
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="uv", timeout=120)

        result = initializer.blend()

        assert result["success"] is False
        assert "timed out" in result["message"]

    @patch('ce.init_project.subprocess.run')
    def test_blend_uv_not_found(self, mock_run, initializer):
        """Test blend phase handles missing uv binary."""
        # Mock FileNotFoundError (uv not in PATH)
        mock_run.side_effect = FileNotFoundError()

        result = initializer.blend()

        assert result["success"] is False
        assert "uv not found" in result["message"]
        assert "🔧" in result["message"]


class TestProjectInitializerInitialize:
    """Test ProjectInitializer.initialize() phase."""

    def test_initialize_missing_tools_dir(self, initializer):
        """Test initialize fails when tools directory doesn't exist."""
        result = initializer.initialize()

        assert result["success"] is False
        assert "Tools directory not found" in result["message"]
        assert "🔧" in result["message"]

    def test_initialize_dry_run_mode(self, dry_run_initializer):
        """Test initialize in dry-run mode shows command without executing."""
        # Create tools directory
        dry_run_initializer.tools_dir.mkdir(parents=True)

        result = dry_run_initializer.initialize()

        assert result["success"] is True
        assert "[DRY-RUN]" in result["stdout"]
        assert "uv sync" in result["stdout"]

    @patch('ce.init_project.subprocess.run')
    def test_initialize_success(self, mock_run, initializer):
        """Test successful initialize phase."""
        # Create tools directory
        initializer.tools_dir.mkdir(parents=True)

        # Mock subprocess success
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Dependencies installed"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        result = initializer.initialize()

        assert result["success"] is True
        assert "✅" in result["message"]

    @patch('ce.init_project.subprocess.run')
    def test_initialize_failure(self, mock_run, initializer):
        """Test initialize phase handles uv sync failure."""
        initializer.tools_dir.mkdir(parents=True)

        # Mock subprocess failure
        mock_result = Mock()
        mock_result.returncode = 1
        mock_result.stdout = ""
        mock_result.stderr = "Dependency conflict"
        mock_run.return_value = mock_result

        result = initializer.initialize()

        assert result["success"] is False
        assert "UV sync failed" in result["message"]


class TestProjectInitializerVerify:
    """Test ProjectInitializer.verify() phase."""

    def test_verify_empty_project(self, initializer):
        """Test verify reports missing files on empty project."""
        result = initializer.verify()

        assert result["success"] is False
        assert len(result["warnings"]) > 0
        assert any("Missing" in w for w in result["warnings"])

    def test_verify_critical_files_present(self, initializer):
        """Test verify passes when critical files exist."""
        # Create critical files
        (initializer.ce_dir / "tools").mkdir(parents=True)
        (initializer.ce_dir / "tools" / "pyproject.toml").write_text("[project]\nname = 'ce'")

        (initializer.target_project / ".claude").mkdir(parents=True)
        (initializer.target_project / ".claude" / "settings.local.json").write_text("{}")

        (initializer.target_project / ".serena" / "memories").mkdir(parents=True)
        (initializer.ce_dir / "RULES.md").write_text("# Rules")

        result = initializer.verify()

        assert result["success"] is True
        assert len(result["checks"]) > 0
        assert "✅" in result["message"]

    def test_verify_invalid_json(self, initializer):
        """Test verify detects invalid JSON in settings.local.json."""
        # Create settings file with invalid JSON
        (initializer.target_project / ".claude").mkdir(parents=True)
        (initializer.target_project / ".claude" / "settings.local.json").write_text("{invalid json")

        result = initializer.verify()

        assert result["success"] is False
        assert any("Invalid JSON" in w for w in result["warnings"])

    def test_verify_checks_venv(self, initializer):
        """Test verify checks for Python virtual environment."""
        # Create .venv directory
        (initializer.tools_dir / ".venv").mkdir(parents=True)

        result = initializer.verify()

        assert any("virtual environment created" in c for c in result["checks"])

    def test_verify_dry_run_works(self, dry_run_initializer):
        """Test verify works in dry-run mode (read-only operation)."""
        result = dry_run_initializer.verify()

        # Verify should work the same in dry-run (it's read-only)
        assert isinstance(result, dict)
        assert "success" in result
        assert "checks" in result
        assert "warnings" in result


class TestProjectInitializerIntegration:
    """Integration tests for full pipeline."""

    def test_dry_run_full_pipeline(self, dry_run_initializer):
        """Test full pipeline in dry-run mode doesn't modify files."""
        results = dry_run_initializer.run(phase="all")

        assert "extract" in results
        assert "blend" in results
        assert "initialize" in results
        assert "verify" in results

        # Verify no files were created
        assert not dry_run_initializer.ce_dir.exists()

    @patch('ce.repomix_unpack.extract_files')
    @patch('ce.init_project.subprocess.run')
    @patch('ce.init_project.shutil')
    def test_full_pipeline_mocked(self, mock_shutil, mock_run, mock_extract, initializer, ctx_eng_root):
        """Test full pipeline with mocked external dependencies."""
        # FIXME: Using mocks for external dependencies - replace with real integration test

        # Setup mocks
        mock_extract.return_value = 50
        initializer.infrastructure_xml = ctx_eng_root / ".ce" / "ce-infrastructure.xml"

        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Success"
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        # Create minimal file structure for verify
        initializer.ce_dir.mkdir(parents=True)
        initializer.tools_dir.mkdir(parents=True)
        (initializer.ce_dir / "tools" / "pyproject.toml").write_text("[project]\nname = 'ce'")
        (initializer.target_project / ".claude").mkdir(parents=True)
        (initializer.target_project / ".claude" / "settings.local.json").write_text("{}")
        (initializer.target_project / ".serena" / "memories").mkdir(parents=True)
        (initializer.ce_dir / "RULES.md").write_text("# Rules")

        # Run full pipeline
        results = initializer.run(phase="all")

        # Verify all phases executed
        assert all(phase in results for phase in ["extract", "blend", "initialize", "verify"])


class TestProjectInitializerErrorHandling:
    """Test error handling and troubleshooting messages."""

    def test_extract_provides_troubleshooting(self, initializer):
        """Test extract provides actionable troubleshooting on failure."""
        initializer.infrastructure_xml = Path("/nonexistent/file.xml")
        result = initializer.extract()

        assert "🔧" in result["message"]
        assert "Ensure you're running from" in result["message"]

    def test_blend_provides_troubleshooting(self, initializer):
        """Test blend provides troubleshooting on failure."""
        with patch('ce.init_project.subprocess.run', side_effect=FileNotFoundError()):
            result = initializer.blend()

        assert "🔧" in result["message"]
        assert "Install UV" in result["message"]

    def test_initialize_provides_troubleshooting(self, initializer):
        """Test initialize provides troubleshooting on failure."""
        result = initializer.initialize()

        assert "🔧" in result["message"]
        assert "extract phase first" in result["message"]

    def test_verify_provides_troubleshooting(self, initializer):
        """Test verify provides troubleshooting on incomplete installation."""
        result = initializer.verify()

        if not result["success"]:
            assert "🔧" in result["message"]
            assert len(result["warnings"]) > 0
