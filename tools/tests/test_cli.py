"""Tests for CLI interface."""

import subprocess
import pytest
import json
from pathlib import Path
from ce.cli_handlers import format_output


def test_cli_help():
    """Test CLI help output."""
    result = subprocess.run(
        ["uv", "run", "ce", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Context Engineering CLI Tools" in result.stdout
    assert "validate" in result.stdout
    assert "git" in result.stdout
    assert "context" in result.stdout


def test_cli_version():
    """Test CLI version output."""
    result = subprocess.run(
        ["uv", "run", "ce", "--version"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "0.1.0" in result.stdout


def test_cli_validate_help():
    """Test validate command help."""
    result = subprocess.run(
        ["uv", "run", "ce", "validate", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "level" in result.stdout


def test_cli_git_help():
    """Test git command help."""
    result = subprocess.run(
        ["uv", "run", "ce", "git", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "status" in result.stdout
    assert "checkpoint" in result.stdout
    assert "diff" in result.stdout


def test_cli_context_help():
    """Test context command help."""
    result = subprocess.run(
        ["uv", "run", "ce", "context", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "sync" in result.stdout
    assert "health" in result.stdout


def test_format_output_json():
    """Test JSON output formatting."""
    data = {"status": "ok", "count": 5}
    output = format_output(data, as_json=True)
    parsed = json.loads(output)
    assert parsed["status"] == "ok"
    assert parsed["count"] == 5


def test_format_output_nested_dict():
    """Test nested dict formatting."""
    data = {
        "metadata": {
            "version": "1.0",
            "author": "test"
        },
        "stats": {
            "files": 10,
            "errors": 0
        }
    }
    output = format_output(data, as_json=False)
    assert "metadata:" in output
    assert "version: 1.0" in output
    assert "author: test" in output
    assert "stats:" in output
    assert "files: 10" in output


def test_format_output_with_lists():
    """Test list formatting in output."""
    data = {
        "files": ["file1.py", "file2.py", "file3.py"],
        "count": 3
    }
    output = format_output(data, as_json=False)
    assert "files:" in output
    assert "- file1.py" in output
    assert "- file2.py" in output
    assert "- file3.py" in output
    assert "count: 3" in output


# =============================================================================
# PRP Generate CLI Tests
# =============================================================================


def test_cli_prp_generate_help():
    """Test prp generate command help."""
    result = subprocess.run(
        ["uv", "run", "ce", "prp", "generate", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "initial_md" in result.stdout
    assert "output" in result.stdout


def test_cli_prp_generate_end_to_end(tmp_path):
    """Test E2E PRP generation via CLI."""
    # Use sample_initial.md fixture
    sample_initial = Path(__file__).parent / "fixtures" / "sample_initial.md"
    output_dir = tmp_path / "prps"
    output_dir.mkdir()

    result = subprocess.run(
        ["uv", "run", "ce", "prp", "generate", str(sample_initial), "-o", str(output_dir)],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "PRP generated" in result.stdout

    # Verify file created
    prp_files = list(output_dir.glob("PRP-*.md"))
    assert len(prp_files) == 1

    # Verify content
    content = prp_files[0].read_text()
    assert "User Authentication System" in content
    assert "## 1. TL;DR" in content
    assert "## 2. Context" in content


def test_cli_prp_generate_json_output(tmp_path):
    """Test JSON output from prp generate."""
    sample_initial = Path(__file__).parent / "fixtures" / "sample_initial.md"
    output_dir = tmp_path / "prps"
    output_dir.mkdir()

    result = subprocess.run(
        ["uv", "run", "ce", "prp", "generate", str(sample_initial), "-o", str(output_dir), "--json"],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0

    # Parse JSON output
    output = json.loads(result.stdout)
    assert output["success"] is True
    assert "prp_path" in output
    assert Path(output["prp_path"]).exists()


def test_cli_prp_generate_missing_file():
    """Test error handling for missing INITIAL.md."""
    result = subprocess.run(
        ["uv", "run", "ce", "prp", "generate", "nonexistent.md"],
        capture_output=True,
        text=True
    )

    assert result.returncode != 0
    assert "not found" in result.stderr.lower() or "no such file" in result.stderr.lower()
