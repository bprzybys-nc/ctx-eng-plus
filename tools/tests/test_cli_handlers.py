"""Tests for CLI handlers."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace

from ce.cli_handlers import cmd_init_project


# =============================================================================
# cmd_init_project Tests
# =============================================================================


def test_cmd_init_project_nonexistent_directory(tmp_path, capsys):
    """Test cmd_init_project with non-existent target directory."""
    args = Namespace(
        target_dir="/non/existent/path",
        dry_run=False,
        blend_only=False,
        phase="all",
        json=False
    )

    exit_code = cmd_init_project(args)

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Target directory not found" in captured.err
    assert "🔧 Troubleshooting" in captured.err


def test_cmd_init_project_blend_only_success(tmp_path):
    """Test cmd_init_project with --blend-only flag."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=True,
        phase="all",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.blend.return_value = {
            "success": True,
            "message": "✅ Blend phase completed",
            "stdout": "",
            "stderr": ""
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 0
        MockInitializer.assert_called_once_with(target_dir, dry_run=False)
        mock_instance.blend.assert_called_once()
        mock_instance.run.assert_not_called()


def test_cmd_init_project_blend_only_failure(tmp_path):
    """Test cmd_init_project with --blend-only flag and blend failure."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=True,
        phase="all",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.blend.return_value = {
            "success": False,
            "message": "❌ Blend phase failed",
            "stdout": "",
            "stderr": "Error details"
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 2


def test_cmd_init_project_specific_phase(tmp_path):
    """Test cmd_init_project with --phase flag."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=False,
        phase="extract",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.run.return_value = {
            "extract": {
                "success": True,
                "message": "✅ Extracted 50 files",
                "files_extracted": 50
            }
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 0
        mock_instance.run.assert_called_once_with(phase="extract")


def test_cmd_init_project_all_phases_success(tmp_path):
    """Test cmd_init_project running all phases successfully."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=False,
        phase="all",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.run.return_value = {
            "extract": {"success": True, "message": "✅ Extraction complete"},
            "blend": {"success": True, "message": "✅ Blend complete"},
            "initialize": {"success": True, "message": "✅ Initialize complete"},
            "verify": {"success": True, "message": "✅ Verification complete"}
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 0
        mock_instance.run.assert_called_once_with(phase="all")


def test_cmd_init_project_partial_failure(tmp_path):
    """Test cmd_init_project with one phase failing."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=False,
        phase="all",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.run.return_value = {
            "extract": {"success": True, "message": "✅ Extraction complete"},
            "blend": {"success": False, "message": "❌ Blend failed"},
            "initialize": {"success": True, "message": "✅ Initialize complete"},
            "verify": {"success": True, "message": "✅ Verification complete"}
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 2


def test_cmd_init_project_dry_run(tmp_path):
    """Test cmd_init_project in dry-run mode."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=True,
        blend_only=False,
        phase="all",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.run.return_value = {
            "extract": {"success": True, "message": "[DRY-RUN] Would extract files"}
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 0
        MockInitializer.assert_called_once_with(target_dir, dry_run=True)


def test_cmd_init_project_json_output(tmp_path, capsys):
    """Test cmd_init_project with JSON output."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=False,
        phase="all",
        json=True
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.run.return_value = {
            "extract": {"success": True, "message": "✅ Extraction complete"}
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "{" in captured.out
        assert "extract" in captured.out


def test_cmd_init_project_invalid_phase(tmp_path, capsys):
    """Test cmd_init_project with invalid phase."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=False,
        phase="invalid_phase",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.run.side_effect = ValueError("Invalid phase 'invalid_phase'")

        exit_code = cmd_init_project(args)

        assert exit_code == 1
        captured = capsys.readouterr()
        assert "Invalid phase" in captured.err
        assert "🔧 Troubleshooting" in captured.err


def test_cmd_init_project_exception_handling(tmp_path, capsys):
    """Test cmd_init_project exception handling."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=False,
        phase="all",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        MockInitializer.side_effect = RuntimeError("Unexpected error")

        exit_code = cmd_init_project(args)

        assert exit_code == 2
        captured = capsys.readouterr()
        assert "Initialization failed" in captured.err
        assert "🔧 Troubleshooting" in captured.err


def test_cmd_init_project_blend_only_takes_precedence(tmp_path):
    """Test that --blend-only takes precedence over --phase."""
    target_dir = tmp_path / "target-project"
    target_dir.mkdir()

    args = Namespace(
        target_dir=str(target_dir),
        dry_run=False,
        blend_only=True,
        phase="extract",
        json=False
    )

    with patch("ce.cli_handlers.ProjectInitializer") as MockInitializer:
        mock_instance = MockInitializer.return_value
        mock_instance.blend.return_value = {
            "success": True,
            "message": "✅ Blend phase completed"
        }

        exit_code = cmd_init_project(args)

        assert exit_code == 0
        mock_instance.blend.assert_called_once()
        mock_instance.run.assert_not_called()
