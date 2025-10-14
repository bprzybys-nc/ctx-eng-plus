"""Tests for update_context module."""

import pytest
from pathlib import Path
from datetime import datetime, timezone
from ce.update_context import (
    read_prp_header,
    update_context_sync_flags,
    get_prp_status,
    discover_prps,
    extract_expected_functions,
    should_transition_to_executed,
    verify_codebase_matches_examples,
    detect_missing_examples_for_prps,
    generate_drift_report,
    load_pattern_checks
)


# Test YAML operations
def test_read_prp_header_success():
    """Test reading PRP YAML header from real file."""
    prp_path = Path("../PRPs/executed/PRP-6-markdown-linting.md")
    metadata, content = read_prp_header(prp_path)

    assert "prp_id" in metadata
    assert metadata["prp_id"] == "PRP-6"
    assert "context_sync" in metadata
    assert isinstance(content, str)
    assert len(content) > 0


def test_read_prp_header_nonexistent():
    """Test reading nonexistent file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        read_prp_header(Path("nonexistent.md"))

    assert "not found" in str(exc_info.value)
    assert "🔧 Troubleshooting" in str(exc_info.value)


def test_get_prp_status():
    """Test extracting status from PRP."""
    prp_path = Path("../PRPs/executed/PRP-6-markdown-linting.md")
    status = get_prp_status(prp_path)

    assert status in ["new", "in_progress", "executed", "archived"]


def test_update_context_sync_flags(tmp_path):
    """Test updating context_sync flags in PRP."""
    # Create test PRP with valid YAML
    test_prp = tmp_path / "test-prp.md"
    test_content = """---
prp_id: TEST-1
feature_name: Test Feature
status: new
created: 2025-01-01
updated: 2025-01-01
context_sync:
  ce_updated: false
  serena_updated: false
---

# Test PRP

Test content here.
"""
    test_prp.write_text(test_content)

    # Update flags
    update_context_sync_flags(test_prp, ce_updated=True, serena_updated=False)

    # Read back and verify
    metadata, content = read_prp_header(test_prp)

    assert metadata["context_sync"]["ce_updated"] is True
    assert metadata["context_sync"]["serena_updated"] is False
    assert "last_sync" in metadata["context_sync"]
    assert metadata["updated_by"] == "update-context-command"


# Test PRP discovery
def test_discover_prps_universal():
    """Test discovering all PRPs in universal mode."""
    import os
    original_cwd = os.getcwd()
    try:
        # Change to project root
        os.chdir(Path(original_cwd).parent)
        prps = discover_prps()

        assert len(prps) > 0
        assert all(p.suffix == ".md" for p in prps)
    finally:
        os.chdir(original_cwd)


def test_discover_prps_targeted():
    """Test discovering specific PRP."""
    import os
    original_cwd = os.getcwd()
    try:
        # Change to project root
        os.chdir(Path(original_cwd).parent)
        prps = discover_prps(target_prp="PRPs/executed/PRP-6-markdown-linting.md")

        assert len(prps) == 1
        assert prps[0].name == "PRP-6-markdown-linting.md"
    finally:
        os.chdir(original_cwd)


def test_discover_prps_targeted_nonexistent():
    """Test targeting nonexistent PRP raises error."""
    with pytest.raises(FileNotFoundError) as exc_info:
        discover_prps(target_prp="nonexistent.md")

    assert "not found" in str(exc_info.value)
    assert "🔧 Troubleshooting" in str(exc_info.value)


# Test function extraction
def test_extract_expected_functions():
    """Test extracting function names from PRP content."""
    content = """
# Implementation

Create these functions:
- `read_prp_header()`
- `update_context_sync_flags()`

Also implement:
```python
def sync_context(target_prp: str):
    pass

class PRPAnalyzer:
    pass
```
"""
    functions = extract_expected_functions(content)

    assert "read_prp_header" in functions
    assert "update_context_sync_flags" in functions
    assert "sync_context" in functions
    assert "PRPAnalyzer" in functions


def test_extract_expected_functions_empty():
    """Test extracting from content with no functions."""
    functions = extract_expected_functions("No functions here")

    assert len(functions) == 0


# Test status transition
def test_should_transition_to_executed_yes(tmp_path):
    """Test PRP that should transition to executed."""
    # Create test PRP in feature-requests with ce_updated=true
    feature_requests_dir = tmp_path / "PRPs" / "feature-requests"
    feature_requests_dir.mkdir(parents=True)

    test_prp = feature_requests_dir / "test-prp.md"
    test_content = """---
prp_id: TEST-1
status: new
context_sync:
  ce_updated: true
  serena_updated: false
---
# Test
"""
    test_prp.write_text(test_content)

    # Change to tmp_path for relative path checks
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = should_transition_to_executed(test_prp)
        assert result is True
    finally:
        os.chdir(original_cwd)


def test_should_transition_to_executed_no_ce_updated(tmp_path):
    """Test PRP with ce_updated=false should not transition."""
    feature_requests_dir = tmp_path / "PRPs" / "feature-requests"
    feature_requests_dir.mkdir(parents=True)

    test_prp = feature_requests_dir / "test-prp.md"
    test_content = """---
prp_id: TEST-1
status: new
context_sync:
  ce_updated: false
  serena_updated: false
---
# Test
"""
    test_prp.write_text(test_content)

    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        result = should_transition_to_executed(test_prp)
        assert result is False
    finally:
        os.chdir(original_cwd)


# Test drift detection
def test_load_pattern_checks():
    """Test loading pattern checks."""
    checks = load_pattern_checks()

    assert "error_handling" in checks
    assert "naming_conventions" in checks
    assert "kiss_violations" in checks
    assert isinstance(checks["error_handling"], list)


def test_verify_codebase_matches_examples():
    """Test drift detection returns violations."""
    result = verify_codebase_matches_examples()

    assert "violations" in result
    assert "drift_score" in result
    assert isinstance(result["violations"], list)
    assert isinstance(result["drift_score"], float)
    assert 0 <= result["drift_score"] <= 100


def test_detect_missing_examples_for_prps():
    """Test detecting PRPs missing examples."""
    missing = detect_missing_examples_for_prps()

    assert isinstance(missing, list)
    # Each entry should have required fields
    for item in missing:
        assert "prp_id" in item
        assert "feature_name" in item
        assert "complexity" in item
        assert "missing_example" in item
        assert "suggested_path" in item


def test_generate_drift_report():
    """Test generating drift report markdown."""
    violations = [
        "File tools/ce/foo.py uses bare except (violates examples/patterns/error-handling.py): Use specific exception types"
    ]
    missing_examples = [
        {
            "prp_id": "PRP-13",
            "feature_name": "Production Hardening",
            "complexity": "high",
            "missing_example": "error_recovery",
            "suggested_path": "examples/patterns/error-recovery.py",
            "rationale": "Complex error recovery logic should be documented"
        }
    ]

    report = generate_drift_report(violations, 10.0, missing_examples)

    assert "Context Drift Report" in report
    assert "10.0%" in report
    assert "Part 1: Code Violating Documented Patterns" in report
    assert "Part 2: Missing Pattern Documentation" in report
    assert "PRP-13" in report
    assert "Proposed Solutions Summary" in report


def test_generate_drift_report_no_violations():
    """Test drift report with no violations."""
    report = generate_drift_report([], 0.0, [])

    assert "0.0%" in report
    assert "No violations detected" in report
    assert "All critical PRPs have corresponding examples" in report


# Test file operations
def test_move_prp_to_executed(tmp_path):
    """Test moving PRP from feature-requests to executed."""
    from ce.update_context import move_prp_to_executed

    # Setup directories
    feature_requests_dir = tmp_path / "PRPs" / "feature-requests"
    feature_requests_dir.mkdir(parents=True)

    # Create test PRP
    test_prp = feature_requests_dir / "test-prp.md"
    test_prp.write_text("---\nprp_id: TEST-1\n---\n# Test")

    # Change to tmp_path
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        new_path = move_prp_to_executed(test_prp)

        # Verify move
        assert not test_prp.exists()
        assert new_path.exists()
        assert "executed" in str(new_path)
    finally:
        os.chdir(original_cwd)


# Integration test
def test_sync_context_targeted(tmp_path):
    """Test targeted sync with single PRP."""
    from ce.update_context import sync_context

    # Setup directory structure
    feature_requests_dir = tmp_path / "PRPs" / "feature-requests"
    feature_requests_dir.mkdir(parents=True)

    # Create test PRP
    test_prp = feature_requests_dir / "test-prp.md"
    test_content = """---
prp_id: TEST-1
feature_name: Test Feature
status: new
created: 2025-01-01
updated: 2025-01-01
context_sync:
  ce_updated: false
  serena_updated: false
---

# Test PRP

Implement `test_function()` and `class TestClass`.
"""
    test_prp.write_text(test_content)

    # Change to tmp_path
    import os
    original_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)

        # Run targeted sync
        result = sync_context(target_prp="PRPs/feature-requests/test-prp.md")

        # Verify results
        assert result["prps_scanned"] == 1
        assert result["prps_updated"] == 1
        assert result["ce_updated_count"] >= 0  # May be 0 or 1 depending on function detection

        # Verify YAML was updated (check both original location and executed/)
        # PRP may have been moved if ce_updated=true
        if test_prp.exists():
            metadata, _ = read_prp_header(test_prp)
        else:
            # Check executed directory
            executed_path = tmp_path / "PRPs" / "executed" / "test-prp.md"
            assert executed_path.exists(), "PRP not found in original or executed location"
            metadata, _ = read_prp_header(executed_path)

        assert "last_sync" in metadata["context_sync"]
        assert metadata["updated_by"] == "update-context-command"

    finally:
        os.chdir(original_cwd)
