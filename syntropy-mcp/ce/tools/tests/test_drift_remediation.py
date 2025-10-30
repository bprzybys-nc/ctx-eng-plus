"""E2E tests for PRP-15.3: Drift Remediation Workflow.

Tests the complete workflow:
  detect_drift_violations → transform → generate_drift_blueprint →
  approval gate → generate_maintenance_prp
"""

import pytest
from unittest.mock import patch
from pathlib import Path


@pytest.fixture
def mock_drift_result():
    """Mock drift detection result with violations."""
    return {
        "has_drift": True,
        "drift_score": 25.5,
        "violations": [
            {
                "file": "tools/ce/core.py",
                "line": 42,
                "issue": "Missing error handling",
                "solution": "Add try-except with troubleshooting"
            }
        ],
        "missing_examples": ["error-handling-pattern.md"]
    }


@pytest.fixture
def mock_no_drift_result():
    """Mock drift detection result with no violations."""
    return {
        "has_drift": False,
        "drift_score": 5.0,
        "violations": [],
        "missing_examples": []
    }


@pytest.fixture
def mock_blueprint_path(tmp_path):
    """Mock blueprint file path."""
    return tmp_path / "DEDRIFT-INITIAL.md"


@pytest.fixture
def mock_prp_path(tmp_path):
    """Mock PRP file path."""
    return tmp_path / "PRPs" / "system" / "DEDRIFT_PRP-20250116-120000.md"


# === E2E Test 1: YOLO Mode with Drift ===

def test_remediate_drift_workflow_yolo_with_drift(
    mock_drift_result,
    mock_blueprint_path,
    mock_prp_path
):
    """E2E Test 1: YOLO mode detects drift, generates blueprint, creates PRP."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect, \
         patch("ce.update_context.generate_drift_blueprint") as mock_blueprint, \
         patch("ce.update_context.display_drift_summary"), \
         patch("ce.update_context.generate_maintenance_prp") as mock_prp:

        # Setup mocks
        mock_detect.return_value = mock_drift_result
        mock_blueprint.return_value = mock_blueprint_path
        mock_prp.return_value = mock_prp_path

        # Execute YOLO mode
        result = remediate_drift_workflow(yolo_mode=True)

        # Assertions
        assert result["success"] is True
        assert result["prp_path"] == mock_prp_path
        assert result["blueprint_path"] == mock_blueprint_path
        assert result["errors"] == []

        # Verify workflow steps
        mock_detect.assert_called_once()
        mock_blueprint.assert_called_once_with(
            mock_drift_result,
            mock_drift_result["missing_examples"]
        )
        mock_prp.assert_called_once_with(mock_blueprint_path)


# === E2E Test 2: YOLO Mode with No Drift ===

def test_remediate_drift_workflow_yolo_no_drift(mock_no_drift_result):
    """E2E Test 2: YOLO mode detects no drift, exits early."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect:
        mock_detect.return_value = mock_no_drift_result

        # Execute YOLO mode
        result = remediate_drift_workflow(yolo_mode=True)

        # Assertions: early exit
        assert result["success"] is True
        assert result["prp_path"] is None
        assert result["blueprint_path"] is None
        assert result["errors"] == []


# === E2E Test 3: Vanilla Mode with Approval ===

def test_remediate_drift_workflow_vanilla_approval(
    mock_drift_result,
    mock_blueprint_path,
    mock_prp_path
):
    """E2E Test 3: Vanilla mode with user approval generates PRP."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect, \
         patch("ce.update_context.generate_drift_blueprint") as mock_blueprint, \
         patch("ce.update_context.display_drift_summary"), \
         patch("ce.update_context.generate_maintenance_prp") as mock_prp, \
         patch("builtins.input", return_value="yes"):

        # Setup mocks
        mock_detect.return_value = mock_drift_result
        mock_blueprint.return_value = mock_blueprint_path
        mock_prp.return_value = mock_prp_path

        # Execute vanilla mode
        result = remediate_drift_workflow(yolo_mode=False)

        # Assertions
        assert result["success"] is True
        assert result["prp_path"] == mock_prp_path
        assert result["blueprint_path"] == mock_blueprint_path


# === E2E Test 4: Vanilla Mode with Rejection ===

def test_remediate_drift_workflow_vanilla_rejection(
    mock_drift_result,
    mock_blueprint_path
):
    """E2E Test 4: Vanilla mode with user rejection skips PRP generation."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect, \
         patch("ce.update_context.generate_drift_blueprint") as mock_blueprint, \
         patch("ce.update_context.display_drift_summary"), \
         patch("ce.update_context.generate_maintenance_prp") as mock_prp, \
         patch("builtins.input", return_value="no"):

        # Setup mocks
        mock_detect.return_value = mock_drift_result
        mock_blueprint.return_value = mock_blueprint_path

        # Execute vanilla mode
        result = remediate_drift_workflow(yolo_mode=False)

        # Assertions
        assert result["success"] is True
        assert result["prp_path"] is None
        assert result["blueprint_path"] == mock_blueprint_path
        mock_prp.assert_not_called()


# === E2E Test 5: Error Handling - Detection Failure ===

def test_remediate_drift_workflow_detection_error():
    """E2E Test 5: Detection failure returns error result."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect:
        mock_detect.side_effect = RuntimeError("Serena MCP not connected")

        # Execute workflow
        result = remediate_drift_workflow(yolo_mode=True)

        # Assertions
        assert result["success"] is False
        assert result["prp_path"] is None
        assert result["blueprint_path"] is None
        assert len(result["errors"]) == 1


# === E2E Test 6: Error Handling - Blueprint Failure ===

def test_remediate_drift_workflow_blueprint_error(mock_drift_result):
    """E2E Test 6: Blueprint generation failure returns error."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect, \
         patch("ce.update_context.generate_drift_blueprint") as mock_blueprint:

        mock_detect.return_value = mock_drift_result
        mock_blueprint.side_effect = RuntimeError("Template not found")

        # Execute workflow
        result = remediate_drift_workflow(yolo_mode=True)

        # Assertions
        assert result["success"] is False
        assert result["prp_path"] is None
        assert result["blueprint_path"] is None


# === E2E Test 7: Error Handling - PRP Generation Failure ===

def test_remediate_drift_workflow_prp_generation_error(
    mock_drift_result,
    mock_blueprint_path
):
    """E2E Test 7: PRP generation failure returns error."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect, \
         patch("ce.update_context.generate_drift_blueprint") as mock_blueprint, \
         patch("ce.update_context.display_drift_summary"), \
         patch("ce.update_context.generate_maintenance_prp") as mock_prp:

        mock_detect.return_value = mock_drift_result
        mock_blueprint.return_value = mock_blueprint_path
        mock_prp.side_effect = RuntimeError("Disk full")

        # Execute workflow
        result = remediate_drift_workflow(yolo_mode=True)

        # Assertions
        assert result["success"] is False
        assert result["prp_path"] is None
        assert result["blueprint_path"] == mock_blueprint_path
        assert "PRP generation failed" in result["errors"][0]


# === E2E Test 8: JSON Output Validation ===

def test_remediate_drift_workflow_json_structure(
    mock_drift_result,
    mock_blueprint_path,
    mock_prp_path
):
    """E2E Test 8: Validate JSON output structure."""
    from ce.update_context import remediate_drift_workflow

    with patch("ce.update_context.detect_drift_violations") as mock_detect, \
         patch("ce.update_context.generate_drift_blueprint") as mock_blueprint, \
         patch("ce.update_context.display_drift_summary"), \
         patch("ce.update_context.generate_maintenance_prp") as mock_prp:

        mock_detect.return_value = mock_drift_result
        mock_blueprint.return_value = mock_blueprint_path
        mock_prp.return_value = mock_prp_path

        # Execute workflow
        result = remediate_drift_workflow(yolo_mode=True)

        # Validate JSON structure
        assert isinstance(result, dict)
        assert "success" in result
        assert "prp_path" in result
        assert "blueprint_path" in result
        assert "errors" in result
        assert isinstance(result["errors"], list)


# === Unit Test: generate_maintenance_prp ===

def test_generate_maintenance_prp(tmp_path, mock_blueprint_path):
    """Test generate_maintenance_prp() creates PRP file with YAML header."""
    from ce.update_context import generate_maintenance_prp

    # Create mock blueprint file
    mock_blueprint_path.parent.mkdir(parents=True, exist_ok=True)
    mock_blueprint_path.write_text("""# Drift Remediation Blueprint

### Violation 1
**File**: tools/ce/core.py:42
**Issue**: Missing error handling
**Solution**: Add try-except

### Violation 2
**File**: tools/ce/validate.py:100
**Issue**: Bare except clause
**Solution**: Catch specific exceptions

**Missing**: error-handling-pattern.md
""")

    with patch("ce.update_context.datetime") as mock_datetime, \
         patch("ce.update_context.generate_prp_yaml_header") as mock_yaml:

        mock_datetime.now.return_value.strftime.return_value = "20250116-120000"
        mock_yaml.return_value = "---\nid: DEDRIFT_PRP-20250116-120000\n---\n\n"

        # Change to tmp_path to simulate project root
        import os
        original_cwd = os.getcwd()
        os.chdir(tmp_path)

        try:
            # Execute function
            prp_path = generate_maintenance_prp(mock_blueprint_path)

            # Assertions
            assert prp_path.exists()
            assert prp_path.name == "DEDRIFT_PRP-20250116-120000.md"
            assert prp_path.parent.name == "system"

            content = prp_path.read_text()
            assert "---" in content  # YAML header
            assert "Violation 1" in content  # Blueprint content
            assert "Violation 2" in content

        finally:
            os.chdir(original_cwd)


# === Unit Test: generate_maintenance_prp Error Handling ===

def test_generate_maintenance_prp_error_handling():
    """Test generate_maintenance_prp() error handling with troubleshooting."""
    from ce.update_context import generate_maintenance_prp

    with pytest.raises(RuntimeError) as exc_info:
        generate_maintenance_prp(Path("/nonexistent/blueprint.md"))

    # Verify troubleshooting guidance
    error_msg = str(exc_info.value)
    assert "🔧 Troubleshooting" in error_msg
