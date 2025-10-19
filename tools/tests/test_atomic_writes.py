"""Tests for atomic file write operations (PRP-21 Phase 1.4).

Tests verify that file writes use temp file + rename pattern to prevent corruption.
"""

import pytest
from pathlib import Path
from ce.update_context import atomic_write


def test_atomic_write_creates_file(tmp_path):
    """Atomic write should create file with correct content."""
    test_file = tmp_path / "test.txt"
    content = "test content"

    atomic_write(test_file, content)

    assert test_file.exists()
    assert test_file.read_text() == content


def test_atomic_write_replaces_existing_file(tmp_path):
    """Atomic write should replace existing file atomically."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("old content")

    atomic_write(test_file, "new content")

    assert test_file.read_text() == "new content"


def test_atomic_write_no_temp_file_left_behind(tmp_path):
    """Atomic write should not leave temp files after success."""
    test_file = tmp_path / "test.txt"

    atomic_write(test_file, "content")

    # No .tmp files should exist
    tmp_files = list(tmp_path.glob("*.tmp"))
    assert len(tmp_files) == 0
