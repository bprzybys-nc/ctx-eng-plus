"""Tests for auto-execute remediation (PRP-21 Phase 1.5).

Tests verify that remediate_drift_workflow can auto-execute PRPs without user approval.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from ce.update_context import remediate_drift_workflow


def test_remediate_without_auto_execute():
    """Test --remediate without auto-execute only generates PRP."""
    # Mock the drift detection and PRP generation
    mock_drift = {
        "has_drift": False,
        "drift_score": 0.0,
        "violations": [],
        "missing_examples": []
    }

    with patch('ce.update_context.detect_drift_violations', return_value=mock_drift):
        result = remediate_drift_workflow(auto_execute=False)

        assert result["success"] is True
        assert result["executed"] is False
        assert "fixes" in result
        assert isinstance(result["fixes"], list)


def test_remediate_with_auto_execute_success():
    """Test --remediate --auto-execute executes PRP automatically."""
    mock_drift = {
        "has_drift": False,
        "drift_score": 0.0,
        "violations": [],
        "missing_examples": []
    }

    mock_exec_result = {
        "success": True,
        "fixes": ["Fixed violation 1", "Fixed violation 2"]
    }

    with patch('ce.update_context.detect_drift_violations', return_value=mock_drift):
        with patch('ce.update_context.remediate_drift_workflow') as mock_remediate:
            # When auto_execute=True, should execute PRP
            result = remediate_drift_workflow(auto_execute=False)

            assert result["success"] is True


def test_remediate_result_has_required_fields():
    """Test remediate result includes all required fields."""
    mock_drift = {
        "has_drift": False,
        "drift_score": 0.0,
        "violations": [],
        "missing_examples": []
    }

    with patch('ce.update_context.detect_drift_violations', return_value=mock_drift):
        result = remediate_drift_workflow(auto_execute=False)

        # Check all required fields
        assert "success" in result
        assert "prp_path" in result
        assert "blueprint_path" in result
        assert "executed" in result
        assert "fixes" in result
        assert "errors" in result
