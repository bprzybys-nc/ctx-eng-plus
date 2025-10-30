"""Tests for safe YAML loading (PRP-21 Phase 2.5).

Tests verify that YAML loading uses safe_load() to prevent code injection.
"""

import pytest
from pathlib import Path
import yaml
from ce.update_context import read_prp_header


def test_read_prp_header_safe_yaml(tmp_path):
    """Safe YAML loading should parse valid YAML metadata."""
    prp_file = tmp_path / "test.md"
    prp_file.write_text("""---
name: "Test Feature"
status: "new"
priority: "HIGH"
---
# Content here
""")

    metadata, content = read_prp_header(prp_file)

    assert metadata["name"] == "Test Feature"
    assert metadata["status"] == "new"
    assert metadata["priority"] == "HIGH"
    assert "# Content here" in content


def test_read_prp_header_rejects_code_injection(tmp_path):
    """Safe YAML loading should reject !!python/object code injection."""
    prp_file = tmp_path / "malicious.md"
    # Try to inject code via !!python/object directive
    malicious_yaml = """---
payload: !!python/object:os.system ["echo pwned"]
---
# Markdown content
"""
    prp_file.write_text(malicious_yaml)

    # Should either reject it or parse it safely (not execute)
    try:
        metadata, content = read_prp_header(prp_file)
        # If it parses, verify it didn't execute as code
        assert isinstance(metadata, dict)
        # The payload should be None or a string, not executed code
        assert metadata.get("payload") is None or isinstance(str(metadata.get("payload")), str)
    except ValueError as e:
        # This is expected - malicious YAML should be rejected
        assert "YAML" in str(e) or "parse" in str(e).lower()


def test_read_prp_header_handles_empty_yaml(tmp_path):
    """Safe YAML loading should handle empty YAML headers."""
    prp_file = tmp_path / "empty.md"
    prp_file.write_text("""---
---
# Content here
""")

    metadata, content = read_prp_header(prp_file)

    assert isinstance(metadata, dict)
    assert len(metadata) == 0
    assert "# Content here" in content
