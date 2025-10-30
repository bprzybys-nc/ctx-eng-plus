"""Tests for contextual error messages (PRP-21 Phase 3.3).

Tests verify that error messages include 🔧 troubleshooting guidance.
"""

import pytest
from pathlib import Path
from ce.update_context import read_prp_header


def test_file_not_found_has_troubleshooting():
    """FileNotFoundError should include troubleshooting guidance."""
    nonexistent = Path("/tmp/nonexistent_prp_123456.md")

    with pytest.raises(FileNotFoundError) as exc:
        read_prp_header(nonexistent)

    error_msg = str(exc.value)
    assert "🔧 Troubleshooting" in error_msg
    assert "ls" in error_msg.lower()


def test_invalid_yaml_has_troubleshooting(tmp_path):
    """ValueError for invalid YAML should include troubleshooting."""
    bad_yaml = tmp_path / "bad.md"
    bad_yaml.write_text("""---
invalid: [yaml: syntax
---
""")

    with pytest.raises(ValueError) as exc:
        read_prp_header(bad_yaml)

    error_msg = str(exc.value)
    assert "🔧 Troubleshooting" in error_msg
    assert "YAML" in error_msg
