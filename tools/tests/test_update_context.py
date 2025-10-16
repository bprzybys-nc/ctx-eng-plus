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
    transform_drift_to_initial,
    detect_drift_violations,
    generate_drift_blueprint,
    display_drift_summary,
    generate_prp_yaml_header
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


# ======================================================================
# PRP-15.2: Blueprint Generation Workflow Tests
# ======================================================================

# detect_drift_violations() tests
def test_detect_drift_violations_with_violations():
    """Test successful drift detection with violations."""
    result = detect_drift_violations()

    assert "drift_score" in result
    assert "violations" in result
    assert "missing_examples" in result
    assert "has_drift" in result
    assert isinstance(result["drift_score"], (int, float))
    assert isinstance(result["violations"], list)
    assert isinstance(result["missing_examples"], list)
    assert isinstance(result["has_drift"], bool)


def test_detect_drift_violations_has_drift_logic():
    """Test has_drift calculated correctly (score >= 5 OR missing > 0)."""
    result = detect_drift_violations()

    # has_drift should be True if drift_score >= 5 OR missing_examples > 0
    if result["drift_score"] >= 5 or len(result["missing_examples"]) > 0:
        assert result["has_drift"] is True
    else:
        assert result["has_drift"] is False


# generate_drift_blueprint() tests
def test_generate_drift_blueprint_success(tmp_path):
    """Test successful blueprint generation."""
    import os
    original_cwd = os.getcwd()

    try:
        # Setup test environment
        os.chdir(tmp_path)

        # Create minimal drift result
        drift_result = {
            "violations": ["File test.py has issue: Fix it"],
            "drift_score": 10.0
        }
        missing = []

        # Generate blueprint
        blueprint_path = generate_drift_blueprint(drift_result, missing)

        # Verify
        assert blueprint_path.exists()
        assert blueprint_path.name == "DEDRIFT-INITIAL.md"
        assert blueprint_path.parent.name == "ce"
        assert blueprint_path.parent.parent.name == "tmp"

        # Verify content
        content = blueprint_path.read_text()
        assert "# Drift Remediation" in content
        assert "10.0%" in content

    finally:
        os.chdir(original_cwd)


def test_generate_drift_blueprint_creates_directory(tmp_path):
    """Test blueprint generation creates tmp/ce/ if missing."""
    import os
    original_cwd = os.getcwd()

    try:
        os.chdir(tmp_path)

        # Ensure tmp/ce/ doesn't exist
        tmp_ce_dir = tmp_path / "tmp" / "ce"
        assert not tmp_ce_dir.exists()

        drift_result = {
            "violations": ["File test.py has issue: Fix"],
            "drift_score": 8.0
        }

        blueprint_path = generate_drift_blueprint(drift_result, [])

        # Verify directory created
        assert tmp_ce_dir.exists()
        assert blueprint_path.exists()

    finally:
        os.chdir(original_cwd)


def test_generate_drift_blueprint_returns_path_object(tmp_path):
    """Test blueprint generation returns valid Path object."""
    import os
    original_cwd = os.getcwd()

    try:
        os.chdir(tmp_path)

        drift_result = {
            "violations": ["File test.py has issue: Fix"],
            "drift_score": 5.0
        }

        blueprint_path = generate_drift_blueprint(drift_result, [])

        # Verify return type
        assert isinstance(blueprint_path, Path)
        assert blueprint_path.is_absolute()

    finally:
        os.chdir(original_cwd)


def test_generate_drift_blueprint_from_tools_directory(tmp_path):
    """Test blueprint works from tools/ directory."""
    import os
    original_cwd = os.getcwd()

    try:
        # Create tools/ directory
        tools_dir = tmp_path / "tools"
        tools_dir.mkdir()
        os.chdir(tools_dir)

        drift_result = {
            "violations": ["File test.py has issue: Fix"],
            "drift_score": 7.0
        }

        blueprint_path = generate_drift_blueprint(drift_result, [])

        # Verify blueprint created in parent/tmp/ce/
        assert blueprint_path.exists()
        assert blueprint_path.parent.name == "ce"
        assert blueprint_path.parent.parent.name == "tmp"
        # Parent of tmp should be project root (tmp_path)
        assert blueprint_path.parent.parent.parent == tmp_path

    finally:
        os.chdir(original_cwd)


# display_drift_summary() tests
def test_display_drift_summary_output(capsys, tmp_path):
    """Test drift summary displays complete output."""
    violations = [
        "File tools/ce/foo.py has bare_except (violates examples/patterns/error-handling.py): Fix",
        "File tools/ce/bar.py has version_suffix (violates examples/patterns/naming.py): Fix"
    ]
    missing = [
        {"prp_id": "PRP-10", "feature_name": "Feature", "suggested_path": "ex.py", "rationale": "R"}
    ]

    blueprint_path = tmp_path / "DEDRIFT-INITIAL.md"
    blueprint_path.touch()

    display_drift_summary(12.5, violations, missing, blueprint_path)

    captured = capsys.readouterr()

    # Verify output structure
    assert "📊 Drift Summary" in captured.out
    assert "12.5%" in captured.out
    assert "Total Violations: 3" in captured.out  # 2 violations + 1 missing
    assert "Blueprint:" in captured.out
    assert str(blueprint_path) in captured.out


def test_display_drift_summary_categorizes_violations(capsys, tmp_path):
    """Test drift summary categorizes violations correctly."""
    violations = [
        "File a.py has bare_except (violates examples/patterns/error-handling.py): Fix",
        "File b.py has bare_except (violates examples/patterns/error-handling.py): Fix",
        "File c.py has version_suffix (violates examples/patterns/naming.py): Fix",
        "File d.py has deep nesting (violates examples/patterns/kiss.py): Fix"
    ]

    blueprint_path = tmp_path / "test.md"
    blueprint_path.touch()

    display_drift_summary(10.0, violations, [], blueprint_path)

    captured = capsys.readouterr()

    # Verify categorization (match actual output format)
    assert "Error Handling: 2 violations" in captured.out
    assert "Naming Conventions: 1 violation" in captured.out
    assert "KISS Violations: 1 violation" in captured.out


def test_display_drift_summary_drift_levels(capsys, tmp_path):
    """Test drift level display (WARNING vs CRITICAL)."""
    violations = ["File test.py has issue: Fix"]
    blueprint_path = tmp_path / "test.md"
    blueprint_path.touch()

    # WARNING level (5-15%)
    display_drift_summary(10.0, violations, [], blueprint_path)
    captured_warn = capsys.readouterr()
    assert "⚠️ WARNING" in captured_warn.out

    # CRITICAL level (15%+)
    display_drift_summary(20.0, violations, [], blueprint_path)
    captured_crit = capsys.readouterr()
    assert "🚨 CRITICAL" in captured_crit.out


# generate_prp_yaml_header() tests
def test_generate_prp_yaml_header_valid_yaml():
    """Test YAML header generation produces valid YAML."""
    import yaml

    header = generate_prp_yaml_header(5, 2, "20250116")

    # Remove YAML delimiters
    yaml_content = header.strip().replace("---\n", "").replace("\n---", "")

    # Parse YAML
    data = yaml.safe_load(yaml_content)

    # Verify structure
    assert "prp_id" in data
    assert "DEDRIFT-20250116" == data["prp_id"]
    assert "effort_hours" in data
    assert "risk" in data
    assert "status" in data
    assert data["status"] == "new"


def test_generate_prp_yaml_header_effort_calculation():
    """Test effort calculation accuracy."""
    # 8 violations * 0.25 = 2h
    # 4 missing * 0.5 = 2h
    # Total = 4h
    header = generate_prp_yaml_header(8, 4, "20250116")

    assert "effort_hours: 4" in header


def test_generate_prp_yaml_header_risk_categorization():
    """Test risk categorization (LOW/MEDIUM/HIGH)."""
    # LOW: < 5 items
    header_low = generate_prp_yaml_header(3, 1, "20250116")
    assert 'risk: "LOW"' in header_low

    # MEDIUM: 5-9 items
    header_medium = generate_prp_yaml_header(5, 2, "20250116")
    assert 'risk: "MEDIUM"' in header_medium

    # HIGH: 10+ items
    header_high = generate_prp_yaml_header(8, 5, "20250116")
    assert 'risk: "HIGH"' in header_high


def test_generate_prp_yaml_header_minimum_effort():
    """Test minimum effort is 1 hour."""
    # 1 violation = 0.25h, should round up to 1h
    header = generate_prp_yaml_header(1, 0, "20250116")

    assert "effort_hours: 1" in header


# Integration test
def test_blueprint_generation_workflow_e2e(tmp_path, capsys):
    """Test full workflow: detect → blueprint → display."""
    import os
    original_cwd = os.getcwd()

    try:
        os.chdir(tmp_path)

        # Phase 1: Detect drift
        drift_result = detect_drift_violations()

        # Only proceed if there's drift
        if drift_result["has_drift"]:
            # Phase 2: Generate blueprint
            blueprint_path = generate_drift_blueprint(
                drift_result,
                drift_result["missing_examples"]
            )

            # Verify blueprint exists
            assert blueprint_path.exists()

            # Verify blueprint content
            content = blueprint_path.read_text()
            assert "# Drift Remediation" in content
            assert f"{drift_result['drift_score']:.1f}%" in content

            # Phase 3: Display summary
            display_drift_summary(
                drift_result["drift_score"],
                drift_result["violations"],
                drift_result["missing_examples"],
                blueprint_path
            )

            # Verify display output
            captured = capsys.readouterr()
            assert "📊 Drift Summary" in captured.out
            assert f"{drift_result['drift_score']:.1f}%" in captured.out
        else:
            # No drift case - skip blueprint generation
            assert drift_result["drift_score"] < 5
            assert len(drift_result["missing_examples"]) == 0

    finally:
        os.chdir(original_cwd)
