"""Markdown linting utilities using markdownlint-cli2.

Provides markdown validation and auto-fixing capabilities.
"""

import subprocess
from pathlib import Path
from typing import Dict, Any


def lint_markdown(auto_fix: bool = False) -> Dict[str, Any]:
    """Lint markdown files using markdownlint-cli2.

    Args:
        auto_fix: If True, attempt to auto-fix issues

    Returns:
        Dict with success, errors, output, fixed_count

    Raises:
        RuntimeError: If markdownlint-cli2 is not installed

    Note: No fishy fallbacks - exceptions thrown for troubleshooting.
    """
    # Check if markdownlint-cli2 is available
    check_cmd = ["which", "markdownlint-cli2"]
    check_result = subprocess.run(
        check_cmd,
        capture_output=True,
        text=True
    )

    if check_result.returncode != 0:
        raise RuntimeError(
            "markdownlint-cli2 not found\n"
            "🔧 Troubleshooting: Install with 'npm install --save-dev markdownlint-cli2'"
        )

    # Patterns for markdown files to lint
    patterns = [
        "docs/**/*.md",
        "PRPs/**/*.md",
        "examples/**/*.md",
        "*.md"
    ]

    cmd = ["markdownlint-cli2"]
    if auto_fix:
        cmd.append("--fix")
    cmd.extend(patterns)

    # Run from project root
    project_root = Path(__file__).parent.parent.parent

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=project_root
    )

    # Parse output
    output_lines = result.stdout.strip().split("\n") if result.stdout else []
    error_lines = result.stderr.strip().split("\n") if result.stderr else []

    # Count fixes if auto-fix was enabled
    fixed_count = 0
    if auto_fix:
        for line in output_lines:
            if "Fixed:" in line:
                fixed_count += 1

    return {
        "success": result.returncode == 0,
        "errors": [line for line in error_lines if line],
        "output": [line for line in output_lines if line],
        "fixed_count": fixed_count,
        "exit_code": result.returncode
    }


def run_markdown_validation(auto_fix: bool = True) -> Dict[str, Any]:
    """Run markdown validation with optional auto-fix.

    Args:
        auto_fix: If True, attempt to auto-fix issues before reporting

    Returns:
        Dict with success, message, details
    """
    try:
        # First try to auto-fix if requested
        if auto_fix:
            fix_result = lint_markdown(auto_fix=True)
            if fix_result["fixed_count"] > 0:
                # Re-run validation to check if all issues were fixed
                validation_result = lint_markdown(auto_fix=False)
                return {
                    "success": validation_result["success"],
                    "message": f"Fixed {fix_result['fixed_count']} issues, validation {'passed' if validation_result['success'] else 'has remaining issues'}",
                    "details": {
                        "fixed_count": fix_result["fixed_count"],
                        "remaining_errors": validation_result["errors"]
                    }
                }

        # Run validation without auto-fix
        result = lint_markdown(auto_fix=False)

        if result["success"]:
            return {
                "success": True,
                "message": "All markdown files validated successfully",
                "details": result
            }
        else:
            return {
                "success": False,
                "message": f"Markdown validation found {len(result['errors'])} issues",
                "details": result
            }

    except Exception as e:
        raise RuntimeError(
            f"Markdown validation failed: {str(e)}\n"
            f"🔧 Troubleshooting: Ensure markdownlint-cli2 is installed via npm"
        )
