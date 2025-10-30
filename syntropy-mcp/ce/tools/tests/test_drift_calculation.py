"""Tests for drift score calculation (PRP-21 Phase 1.1).

Tests verify that drift score is violation-based, not file-based.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from ce.update_context import verify_codebase_matches_examples


def test_drift_score_violation_based():
    """Drift score should be based on violation count, not file count.

    Example: 30 violations across 30 files with 3 checks each:
    - Total checks = 30 files * 3 checks = 90
    - Drift score = (30 violations / 90) * 100 = 33.3%

    This is correct because it reflects actual violation density.
    File-based would incorrectly give 100% (all files have violations).
    """
    # Mock pattern checks (3 checks per category)
    pattern_checks = {
        "error_handling": ["check1", "check2", "check3"]
    }

    # Mock 30 Python files
    python_files = [Path(f"file_{i}.py") for i in range(30)]

    # Mock 30 violations (1 per file)
    violations = [f"violation_{i}" for i in range(30)]

    # Mock check_file_for_violations to return violations
    with patch('ce.update_context.load_pattern_checks', return_value=pattern_checks):
        with patch('pathlib.Path.cwd', return_value=Path('/fake/tools')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.glob', return_value=python_files):
                    with patch('ce.pattern_detectors.check_file_for_violations') as mock_check:
                        # Each file returns 1 violation
                        mock_check.side_effect = [
                            ([f"violation_{i}"], True) for i in range(30)
                        ]

                        result = verify_codebase_matches_examples()

                        # Total checks = 30 files * 3 checks = 90
                        # Violations = 30
                        # Expected drift = (30 / 90) * 100 = 33.3%
                        assert abs(result["drift_score"] - 33.3) < 0.1


def test_drift_score_handles_no_violations():
    """Drift score should be 0% when no violations exist."""
    pattern_checks = {
        "error_handling": ["check1", "check2", "check3"]
    }

    python_files = [Path(f"file_{i}.py") for i in range(10)]

    with patch('ce.update_context.load_pattern_checks', return_value=pattern_checks):
        with patch('pathlib.Path.cwd', return_value=Path('/fake/tools')):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.glob', return_value=python_files):
                    with patch('ce.pattern_detectors.check_file_for_violations') as mock_check:
                        # No violations
                        mock_check.return_value = ([], False)

                        result = verify_codebase_matches_examples()

                        assert result["drift_score"] == 0.0
                        assert len(result["violations"]) == 0
