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
    load_pattern_checks,
    transform_drift_to_initial
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


def test_read_prp_header_file_not_found():
    """Test read_prp_header with missing file."""
    with pytest.raises(FileNotFoundError) as exc:
        read_prp_header(Path("nonexistent.md"))

    assert "PRP file not found" in str(exc.value)
    assert "🔧 Troubleshooting" in str(exc.value)


def test_update_context_sync_flags(tmp_path):
    """Test updating context_sync flags in PRP YAML."""
    # Create test PRP
    prp_content = """---
prp_id: "TEST-1"
status: "new"
---

# Test PRP
"""
    prp_path = tmp_path / "test.md"
    prp_path.write_text(prp_content)

    # Update flags
    update_context_sync_flags(prp_path, True, False)

    # Verify
    metadata, _ = read_prp_header(prp_path)
    assert metadata["context_sync"]["ce_updated"] is True
    assert metadata["context_sync"]["serena_updated"] is False
    assert "last_sync" in metadata["context_sync"]
    assert metadata["updated_by"] == "update-context-command"


def test_get_prp_status():
    """Test extracting status from PRP YAML."""
    prp_path = Path("../PRPs/executed/PRP-6-markdown-linting.md")
    status = get_prp_status(prp_path)

    assert status in ["new", "executed", "archived", "reviewed"]


def test_discover_prps():
    """Test discovering PRPs in directory."""
    prp_files = discover_prps()

    assert len(prp_files) > 0
    assert all(p.suffix == ".md" for p in prp_files)
    assert all(p.exists() for p in prp_files)


def test_extract_expected_functions():
    """Test extracting function names from PRP content."""
    content = """
Some text with `validate_level_1()` and `GitStatus` class.

```python
def helper_function():
    pass

class TestClass:
    pass
```
    """

    functions = extract_expected_functions(content)

    assert "validate_level_1" in functions
    assert "GitStatus" in functions
    assert "helper_function" in functions
    assert "TestClass" in functions


def test_should_transition_to_executed():
    """Test PRP transition logic."""
    prp_path = Path("../PRPs/executed/PRP-6-markdown-linting.md")
    result = should_transition_to_executed(prp_path)

    # Already in executed/, should return False
    assert result is False


def test_verify_codebase_matches_examples():
    """Test drift detection against examples/."""
    result = verify_codebase_matches_examples()

    assert "drift_score" in result
    assert "violations" in result
    assert isinstance(result["drift_score"], (int, float))
    assert isinstance(result["violations"], list)


def test_detect_missing_examples_for_prps():
    """Test detection of PRPs missing examples."""
    missing = detect_missing_examples_for_prps()

    assert isinstance(missing, list)
    # Each item should have required keys
    for item in missing:
        assert "prp_id" in item
        assert "suggested_path" in item


def test_generate_drift_report():
    """Test drift report generation."""
    violations = [
        "File tools/ce/test.py has bare_except (violates examples/patterns/error-handling.py): Use specific exception types"
    ]
    missing = [
        {
            "prp_id": "PRP-TEST",
            "feature_name": "Test Feature",
            "complexity": "medium",
            "missing_example": "error_recovery",
            "suggested_path": "examples/patterns/error-recovery.py",
            "rationale": "Important pattern"
        }
    ]

    report = generate_drift_report(violations, 10.5, missing)

    assert "Context Drift Report" in report
    assert "10.5%" in report
    assert "PRP-TEST" in report
    assert "error-recovery.py" in report


def test_load_pattern_checks():
    """Test loading pattern check rules."""
    checks = load_pattern_checks()

    assert isinstance(checks, dict)
    assert "error_handling" in checks or "naming_conventions" in checks


# ======================================================================
# PRP-15.1: Transform Drift to INITIAL.md Tests
# ======================================================================

# Core Tests
def test_transform_drift_to_initial_valid_input():
    """Test drift report → INITIAL.md transformation with valid data."""
    violations = [
        "File tools/ce/foo.py has bare_except (violates examples/patterns/error-handling.py): Use specific exception types",
        "File tools/ce/bar.py has version_suffix in function name (get_v2_data) (violates examples/patterns/naming.py): Use descriptive names"
    ]
    missing = [
        {
            "prp_id": "PRP-10",
            "feature_name": "Drift History Tracking",
            "suggested_path": "examples/patterns/error-recovery.py",
            "rationale": "Critical pattern for context management"
        }
    ]

    result = transform_drift_to_initial(violations, 12.5, missing)

    # Structure checks
    assert "# Drift Remediation" in result
    assert "## Feature" in result
    assert "## Context" in result
    assert "## Examples" in result
    assert "## Acceptance Criteria" in result
    assert "## Technical Notes" in result

    # Content checks
    assert "12.5%" in result
    assert "Address 2 drift violations" in result
    assert "PRP-10" in result
    assert "Drift History Tracking" in result
    assert "examples/patterns/error-recovery.py" in result

    # Breakdown checks
    assert "Error Handling: 1" in result  # error-handling.py pattern
    assert "Naming Conventions: 1" in result  # naming.py pattern

    # Technical notes
    assert "**Files Affected**: 2" in result  # foo.py and bar.py
    assert "**Estimated Effort**:" in result
    assert "**Complexity**:" in result
    assert "**Total Items**:" in result


def test_transform_structure_sections():
    """Test all required INITIAL.md sections present."""
    violations = ["File test.py has issue: Fix it"]
    result = transform_drift_to_initial(violations, 5.0, [])

    required_sections = [
        "# Drift Remediation",
        "## Feature",
        "## Context",
        "## Examples",
        "## Acceptance Criteria",
        "## Technical Notes"
    ]

    for section in required_sections:
        assert section in result, f"Missing section: {section}"


def test_transform_violation_formatting():
    """Test violation formatting in Examples section."""
    violations = [
        "File a.py has error: Fix A",
        "File b.py has warning: Fix B"
    ]
    result = transform_drift_to_initial(violations, 10.0, [])

    assert "### Violation 1" in result
    assert "File a.py has error: Fix A" in result
    assert "### Violation 2" in result
    assert "File b.py has warning: Fix B" in result


def test_transform_missing_examples_formatting():
    """Test missing examples formatting."""
    missing = [
        {
            "prp_id": "PRP-5",
            "feature_name": "Test Feature",
            "suggested_path": "examples/test.py",
            "rationale": "Important pattern"
        }
    ]
    result = transform_drift_to_initial([], 0.0, missing)

    assert "### Missing Examples" in result
    assert "**PRP-5**: Test Feature" in result
    assert "**Missing**: `examples/test.py`" in result
    assert "**Rationale**: Important pattern" in result


# Edge Case Tests
def test_transform_empty_inputs_raises():
    """Test transform raises ValueError with empty inputs."""
    with pytest.raises(ValueError) as exc:
        transform_drift_to_initial([], 0.0, [])

    assert "no violations and no missing examples" in str(exc.value)
    assert "🔧 Troubleshooting" in str(exc.value)


def test_transform_invalid_drift_score():
    """Test transform raises ValueError with invalid score."""
    violations = ["File test.py has issue: Fix"]

    # Test negative score
    with pytest.raises(ValueError) as exc:
        transform_drift_to_initial(violations, -5.0, [])
    assert "must be 0-100" in str(exc.value)

    # Test score > 100
    with pytest.raises(ValueError) as exc:
        transform_drift_to_initial(violations, 105.0, [])
    assert "must be 0-100" in str(exc.value)


def test_transform_truncates_violations():
    """Test transform shows top 5 violations only."""
    violations = [f"File test{i}.py has issue{i}: Fix{i}" for i in range(10)]
    result = transform_drift_to_initial(violations, 10.0, [])

    # Should have exactly 5 violations
    assert result.count("### Violation") == 5
    assert "### Violation 1" in result
    assert "### Violation 5" in result
    assert "### Violation 6" not in result

    # Technical notes shows total count
    assert "Address 10 drift violations" in result
    assert "**Total Items**: 10 violations + 0 missing examples" in result


def test_transform_truncates_missing_examples():
    """Test transform shows top 3 missing examples only."""
    missing = [
        {
            "prp_id": f"PRP-{i}",
            "feature_name": f"Feature {i}",
            "suggested_path": f"examples/test{i}.py",
            "rationale": f"Reason {i}"
        }
        for i in range(6)
    ]
    result = transform_drift_to_initial([], 0.0, missing)

    # Should have exactly 3 missing examples in Examples section
    examples_section = result.split("## Examples")[1].split("## Acceptance")[0]
    assert examples_section.count("**PRP-") == 3

    # Technical Notes shows total count, not individual items
    assert "**Total Items**: 0 violations + 6 missing examples" in result


def test_transform_effort_calculation():
    """Test effort estimation formula."""
    # 4 violations = 4 * 0.25 = 1h
    # 2 missing examples = 2 * 0.5 = 1h
    # Total = 2h
    violations = [f"File test{i}.py has issue: Fix" for i in range(4)]
    missing = [
        {"prp_id": "PRP-1", "feature_name": "F1", "suggested_path": "e1.py", "rationale": "R1"},
        {"prp_id": "PRP-2", "feature_name": "F2", "suggested_path": "e2.py", "rationale": "R2"}
    ]
    result = transform_drift_to_initial(violations, 10.0, missing)

    assert "**Estimated Effort**: 2h" in result


def test_transform_complexity_categorization():
    """Test complexity calculation."""
    # LOW: < 5 items
    violations_low = ["File test.py has issue: Fix"]
    result_low = transform_drift_to_initial(violations_low, 5.0, [])
    assert "**Complexity**: LOW" in result_low

    # MEDIUM: 5-14 items
    violations_medium = [f"File test{i}.py has issue: Fix" for i in range(8)]
    result_medium = transform_drift_to_initial(violations_medium, 10.0, [])
    assert "**Complexity**: MEDIUM" in result_medium

    # HIGH: 15+ items
    violations_high = [f"File test{i}.py has issue: Fix" for i in range(16)]
    result_high = transform_drift_to_initial(violations_high, 20.0, [])
    assert "**Complexity**: HIGH" in result_high


def test_transform_drift_level_categories():
    """Test drift level categorization."""
    violations = ["File test.py has issue: Fix"]

    # OK: < 5%
    result_ok = transform_drift_to_initial(violations, 3.0, [])
    assert "✅ OK" in result_ok

    # WARNING: 5-15%
    result_warn = transform_drift_to_initial(violations, 10.0, [])
    assert "⚠️ WARNING" in result_warn

    # CRITICAL: 15%+
    result_crit = transform_drift_to_initial(violations, 20.0, [])
    assert "🚨 CRITICAL" in result_crit


def test_transform_file_count_extraction():
    """Test files_affected count from violation strings."""
    violations = [
        "File tools/ce/foo.py has issue1: Fix",
        "File tools/ce/foo.py has issue2: Fix",  # Same file
        "File tools/ce/bar.py has issue3: Fix"
    ]
    result = transform_drift_to_initial(violations, 10.0, [])

    # Should count unique files only
    assert "**Files Affected**: 2" in result


def test_transform_no_file_paths():
    """Test graceful handling when violations have no file paths."""
    violations = ["Generic violation without file path"]
    result = transform_drift_to_initial(violations, 5.0, [])

    # Should not crash, files_affected = 0
    assert "**Files Affected**: 0" in result


# Integration test with sync_context workflow
import os
def test_sync_context_e2e(tmp_path):
    """Test end-to-end sync_context workflow."""
    original_cwd = os.getcwd()

    try:
        # Setup test environment
        os.chdir(tmp_path)

        prps_dir = tmp_path / "PRPs" / "feature-requests"
        prps_dir.mkdir(parents=True)

        prp_content = """---
prp_id: "TEST-SYNC"
status: "new"
context_sync:
  ce_updated: false
  serena_updated: false
---

# Test PRP

## Implementation

`test_function()`
"""
        prp_path = prps_dir / "test-prp.md"
        prp_path.write_text(prp_content)

        # Run sync - should update flags
        from ce.update_context import sync_context
        result = sync_context()

        assert result["success"] is True
        assert result["prps_scanned"] > 0

        # Verify flags updated
        metadata, _ = read_prp_header(prp_path)

        # Check if still in feature-requests or moved to executed
        if not prp_path.exists():
            # Check executed directory
            executed_path = tmp_path / "PRPs" / "executed" / "test-prp.md"
            assert executed_path.exists(), "PRP not found in original or executed location"
            metadata, _ = read_prp_header(executed_path)

        assert "last_sync" in metadata["context_sync"]
        assert metadata["updated_by"] == "update-context-command"

    finally:
        os.chdir(original_cwd)
