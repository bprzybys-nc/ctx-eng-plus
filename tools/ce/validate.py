"""Validation gates: 3-level validation system."""

from typing import Dict, Any, List
from .core import run_cmd


def validate_level_1() -> Dict[str, Any]:
    """Run Level 1 validation: Syntax & Style (lint + type-check).

    Returns:
        Dict with: success (bool), errors (List[str]), duration (float)

    Raises:
        RuntimeError: If validation commands fail to execute

    Note: Real validation - no mocked results.
    """
    errors = []
    total_duration = 0.0

    # Run lint
    lint_result = run_cmd("npm run lint", capture_output=True)
    total_duration += lint_result["duration"]

    if not lint_result["success"]:
        errors.append(f"Lint failed:\n{lint_result['stderr']}")

    # Run type-check
    typecheck_result = run_cmd("npm run type-check", capture_output=True)
    total_duration += typecheck_result["duration"]

    if not typecheck_result["success"]:
        errors.append(f"Type-check failed:\n{typecheck_result['stderr']}")

    return {
        "success": len(errors) == 0,
        "errors": errors,
        "duration": total_duration,
        "level": 1
    }


def validate_level_2() -> Dict[str, Any]:
    """Run Level 2 validation: Unit Tests.

    Returns:
        Dict with: success (bool), errors (List[str]), duration (float)

    Raises:
        RuntimeError: If test command fails to execute

    Note: Real test execution - no mocked test pass.
    """
    result = run_cmd("npm test", capture_output=True)

    errors = []
    if not result["success"]:
        errors.append(f"Unit tests failed:\n{result['stderr']}")

    return {
        "success": result["success"],
        "errors": errors,
        "duration": result["duration"],
        "level": 2
    }


def validate_level_3() -> Dict[str, Any]:
    """Run Level 3 validation: Integration Tests.

    Returns:
        Dict with: success (bool), errors (List[str]), duration (float)

    Raises:
        RuntimeError: If integration test command fails to execute

    Note: Real integration test execution.
    """
    result = run_cmd("npm run test:integration", capture_output=True)

    errors = []
    if not result["success"]:
        errors.append(f"Integration tests failed:\n{result['stderr']}")

    return {
        "success": result["success"],
        "errors": errors,
        "duration": result["duration"],
        "level": 3
    }


def validate_all() -> Dict[str, Any]:
    """Run all validation levels sequentially.

    Returns:
        Dict with: success (bool), results (Dict[int, Dict]),
                   total_duration (float)

    Note: Runs all levels even if early ones fail (for comprehensive report).
    """
    results = {}
    total_duration = 0.0

    # Level 1
    try:
        results[1] = validate_level_1()
        total_duration += results[1]["duration"]
    except Exception as e:
        results[1] = {
            "success": False,
            "errors": [f"Level 1 exception: {str(e)}"],
            "duration": 0.0,
            "level": 1
        }

    # Level 2
    try:
        results[2] = validate_level_2()
        total_duration += results[2]["duration"]
    except Exception as e:
        results[2] = {
            "success": False,
            "errors": [f"Level 2 exception: {str(e)}"],
            "duration": 0.0,
            "level": 2
        }

    # Level 3
    try:
        results[3] = validate_level_3()
        total_duration += results[3]["duration"]
    except Exception as e:
        results[3] = {
            "success": False,
            "errors": [f"Level 3 exception: {str(e)}"],
            "duration": 0.0,
            "level": 3
        }

    # Overall success: all levels must pass
    overall_success = all(r["success"] for r in results.values())

    return {
        "success": overall_success,
        "results": results,
        "total_duration": total_duration
    }
