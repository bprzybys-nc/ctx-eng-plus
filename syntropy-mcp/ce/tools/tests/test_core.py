"""Tests for core operations."""

import pytest
import tempfile
from pathlib import Path
from ce.core import run_cmd, read_file, write_file, git_status, git_checkpoint


def test_run_cmd_success():
    """Test successful command execution."""
    result = run_cmd("echo 'test'")
    assert result["success"] is True
    assert result["exit_code"] == 0
    assert "test" in result["stdout"]
    assert result["duration"] >= 0


def test_run_cmd_failure():
    """Test failed command execution."""
    result = run_cmd("false")
    assert result["success"] is False
    assert result["exit_code"] != 0


def test_read_file():
    """Test file reading."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        temp_path = f.name

    try:
        content = read_file(temp_path)
        assert content == "test content"
    finally:
        Path(temp_path).unlink()


def test_read_file_not_found():
    """Test reading non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_file("/nonexistent/file.txt")


def test_write_file():
    """Test file writing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.txt"
        write_file(str(filepath), "test content")

        assert filepath.exists()
        assert filepath.read_text() == "test content"


def test_write_file_sensitive_data():
    """Test sensitive data detection - API_KEY pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.txt"

        with pytest.raises(ValueError, match="Sensitive data detected"):
            write_file(str(filepath), "API_KEY=secret123")


def test_write_file_sensitive_secret():
    """Test sensitive data detection - SECRET pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.txt"

        with pytest.raises(ValueError, match="Sensitive data detected"):
            write_file(str(filepath), "MY_SECRET=confidential")


def test_write_file_sensitive_password():
    """Test sensitive data detection - PASSWORD pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.txt"

        with pytest.raises(ValueError, match="Sensitive data detected"):
            write_file(str(filepath), "DATABASE_PASSWORD=pass123")


def test_write_file_sensitive_private_key():
    """Test sensitive data detection - PRIVATE_KEY pattern."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "test.txt"

        with pytest.raises(ValueError, match="Sensitive data detected"):
            write_file(str(filepath), "PRIVATE_KEY=-----BEGIN")


def test_git_status_real():
    """Test real git status (assumes we're in a git repo)."""
    try:
        status = git_status()
        assert isinstance(status, dict)
        assert "clean" in status
        assert "staged" in status
        assert "unstaged" in status
        assert "untracked" in status
    except RuntimeError:
        # Not in a git repo - skip test
        pytest.skip("Not in a git repository")


def test_git_checkpoint_creates_tag():
    """Test git checkpoint tag creation."""
    try:
        # Create a checkpoint
        checkpoint_id = git_checkpoint("Test checkpoint")
        assert checkpoint_id.startswith("checkpoint-")
        assert len(checkpoint_id) > 11  # "checkpoint-" + timestamp

        # Clean up - delete the tag
        run_cmd(f'git tag -d "{checkpoint_id}"')
    except RuntimeError:
        pytest.skip("Not in a git repository or no commits")


def test_write_file_unicode():
    """Test writing unicode content."""
    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "unicode_test.txt"
        unicode_content = "Hello 世界 🌍 Привет"

        write_file(str(filepath), unicode_content)
        assert filepath.exists()
        assert filepath.read_text(encoding="utf-8") == unicode_content


def test_read_file_unicode():
    """Test reading unicode content."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        unicode_content = "Testing 日本語 العربية 한글"
        f.write(unicode_content)
        temp_path = f.name

    try:
        content = read_file(temp_path)
        assert content == unicode_content
    finally:
        Path(temp_path).unlink()


def test_write_file_creates_nested_dirs():
    """Test automatic directory creation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        nested_path = Path(tmpdir) / "level1" / "level2" / "level3" / "test.txt"

        write_file(str(nested_path), "nested content")
        assert nested_path.exists()
        assert nested_path.read_text() == "nested content"
