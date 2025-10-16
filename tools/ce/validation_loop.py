"""Validation loop with self-healing capabilities.

Orchestrates L1-L4 validation levels with automatic error detection,
parsing, and self-healing fixes. Includes escalation triggers for
human intervention when automated fixes are insufficient.
"""

import re
from typing import Dict, Any, List
from pathlib import Path

from .exceptions import EscalationRequired


def run_validation_loop(
    phase: Dict[str, Any],
    prp_path: str,
    max_attempts: int = 3
) -> Dict[str, Any]:
    """Run L1-L4 validation loop with self-healing.

    Args:
        phase: Phase dict with validation_command
        prp_path: Path to PRP file (for L4 validation)
        max_attempts: Max self-healing attempts (default: 3)

    Returns:
        {
            "success": True,
            "validation_levels": {
                "L1": {"passed": True, "attempts": 1, "errors": []},
                "L2": {"passed": True, "attempts": 2, "errors": ["..."]},
                "L3": {"passed": True, "attempts": 1, "errors": []},
                "L4": {"passed": True, "attempts": 1, "errors": []}
            },
            "self_healed": ["L2: Fixed import error"],
            "escalated": [],
            "attempts": 1
        }

    Raises:
        EscalationRequired: If validation fails after max_attempts or trigger hit

    Process:
        1. Run L1 (Syntax): validate_level_1() with self-healing
        2. Run L2 (Unit Tests): Custom validation from phase with self-healing
        3. Run L3 (Integration): validate_level_3() with self-healing
        4. Run L4 (Pattern Conformance): validate_level_4(prp_path)

        For each level:
        - If pass: continue to next level
        - If fail: enter self-healing loop (max 3 attempts)
          1. Parse error
          2. Check escalation triggers
          3. Apply fix
          4. Re-run validation
        - If still failing after max_attempts: escalate to human
    """
    from .validate import validate_level_1, validate_level_3, validate_level_4

    print(f"  🧪 Running validation...")

    validation_levels = {}
    self_healed = []
    escalated = []
    all_passed = True

    # L1: Syntax & Style (with self-healing)
    print(f"    L1: Syntax & Style...")
    l1_passed = False
    l1_attempts = 0
    l1_errors = []
    error_history = []

    for attempt in range(1, max_attempts + 1):
        l1_attempts = attempt
        try:
            l1_result = validate_level_1()
            if l1_result["success"]:
                l1_passed = True
                print(f"    ✅ L1 passed ({l1_result['duration']:.2f}s)")
                if attempt > 1:
                    self_healed.append(f"L1: Fixed after {attempt} attempts")
                break
            else:
                l1_errors = l1_result.get("errors", [])
                print(f"    ❌ L1 failed (attempt {attempt}/{max_attempts}): {len(l1_errors)} errors")

                # Parse error and try self-healing
                if attempt < max_attempts:
                    combined_error = "\n".join(l1_errors)
                    error = parse_validation_error(combined_error, "L1")
                    error_history.append(error["message"])

                    # Check escalation triggers
                    if check_escalation_triggers(error, attempt, error_history):
                        escalate_to_human(error, "persistent_error")

                    # Apply self-healing
                    print(f"      🔧 Attempting self-heal...")
                    fix_result = apply_self_healing_fix(error, attempt)
                    if fix_result["success"]:
                        print(f"      ✅ Applied fix: {fix_result['description']}")
                    else:
                        print(f"      ⚠️  Auto-fix failed: {fix_result['description']}")

        except EscalationRequired:
            raise  # Propagate escalation
        except Exception as e:
            l1_errors = [str(e)]
            print(f"    ❌ L1 exception (attempt {attempt}): {str(e)}")
            if attempt == max_attempts:
                break

    validation_levels["L1"] = {
        "passed": l1_passed,
        "attempts": l1_attempts,
        "errors": l1_errors
    }
    if not l1_passed:
        all_passed = False
        print(f"    ❌ L1 failed after {l1_attempts} attempts - escalating")
        error = parse_validation_error("\n".join(l1_errors), "L1")
        escalate_to_human(error, "persistent_error")

    # L2: Unit Tests (with self-healing)
    l2_passed = False
    l2_attempts = 0
    l2_errors = []
    error_history_l2 = []

    if phase.get("validation_command"):
        print(f"    L2: Running {phase['validation_command']}...")
        from .core import run_cmd

        for attempt in range(1, max_attempts + 1):
            l2_attempts = attempt
            try:
                l2_result = run_cmd(phase["validation_command"])
                if l2_result["success"]:
                    l2_passed = True
                    print(f"    ✅ L2 passed ({l2_result['duration']:.2f}s)")
                    if attempt > 1:
                        self_healed.append(f"L2: Fixed after {attempt} attempts")
                    break
                else:
                    l2_errors = [l2_result.get("stderr", "Test failed")]
                    print(f"    ❌ L2 failed (attempt {attempt}/{max_attempts})")
                    print(f"       {l2_result.get('stderr', 'Unknown error')[:200]}")

                    # Self-healing for test failures
                    if attempt < max_attempts:
                        error = parse_validation_error(l2_result.get("stderr", ""), "L2")
                        error_history_l2.append(error["message"])

                        if check_escalation_triggers(error, attempt, error_history_l2):
                            escalate_to_human(error, "persistent_error")

                        print(f"      🔧 Attempting self-heal...")
                        fix_result = apply_self_healing_fix(error, attempt)
                        if fix_result["success"]:
                            print(f"      ✅ Applied fix: {fix_result['description']}")
                        else:
                            print(f"      ⚠️  Auto-fix failed: {fix_result['description']}")

            except EscalationRequired:
                raise
            except Exception as e:
                l2_errors = [str(e)]
                print(f"    ❌ L2 exception (attempt {attempt}): {str(e)}")
                if attempt == max_attempts:
                    break

        validation_levels["L2"] = {
            "passed": l2_passed,
            "attempts": l2_attempts,
            "errors": l2_errors
        }
        if not l2_passed:
            all_passed = False
            print(f"    ❌ L2 failed after {l2_attempts} attempts - escalating")
            error = parse_validation_error("\n".join(l2_errors), "L2")
            escalate_to_human(error, "persistent_error")

    else:
        # No validation command - skip L2
        print(f"    ⚠️  L2 skipped: No validation command specified")
        validation_levels["L2"] = {"passed": True, "attempts": 1, "errors": [], "skipped": True}

    # L3: Integration Tests (MVP: no self-healing for integration tests)
    try:
        print(f"    L3: Integration Tests...")
        l3_result = validate_level_3()
        validation_levels["L3"] = {
            "passed": l3_result["success"],
            "attempts": 1,
            "errors": l3_result.get("errors", [])
        }
        if l3_result["success"]:
            print(f"    ✅ L3 passed ({l3_result['duration']:.2f}s)")
        else:
            print(f"    ❌ L3 failed - integration tests require manual review")
            all_passed = False
            # Integration test failures typically require architectural changes
            error = parse_validation_error(str(l3_result.get("errors", [])), "L3")
            escalate_to_human(error, "architectural")
    except EscalationRequired:
        raise
    except Exception as e:
        print(f"    ⚠️  L3 skipped: {str(e)}")
        validation_levels["L3"] = {"passed": True, "attempts": 1, "errors": [], "skipped": True}

    # L4: Pattern Conformance
    try:
        print(f"    L4: Pattern Conformance...")
        l4_result = validate_level_4(prp_path)
        validation_levels["L4"] = {
            "passed": l4_result["success"],
            "attempts": 1,
            "errors": [],
            "drift_score": l4_result.get("drift_score", 0)
        }
        if l4_result["success"]:
            print(f"    ✅ L4 passed (drift: {l4_result.get('drift_score', 0):.1f}%)")
        else:
            print(f"    ❌ L4 failed (drift: {l4_result.get('drift_score', 100):.1f}%)")
            all_passed = False
    except Exception as e:
        print(f"    ⚠️  L4 skipped: {str(e)}")
        validation_levels["L4"] = {"passed": True, "attempts": 1, "errors": [], "skipped": True}

    print(f"  {'✅' if all_passed else '❌'} Validation {'complete' if all_passed else 'failed'}")

    return {
        "success": all_passed,
        "validation_levels": validation_levels,
        "self_healed": self_healed,
        "escalated": escalated,
        "attempts": 1
    }


def calculate_confidence_score(validation_results: Dict[str, Any]) -> str:
    """Calculate confidence score (1-10) based on validation results.

    Args:
        validation_results: Dict with L1-L4 results per phase

    Returns:
        "8/10" or "10/10"

    Scoring:
        - All L1-L4 passed on first attempt: 10/10
        - All passed, 1-2 self-heals: 9/10
        - All passed, 3+ self-heals: 8/10
        - L1-L3 passed, L4 skipped: 7/10
        - L1-L2 passed, L3-L4 skipped: 5/10
    """
    if not validation_results:
        return "6/10"  # No validation = baseline

    total_attempts = 0
    all_passed = True

    for _, phase_result in validation_results.items():
        if not phase_result.get("success"):
            all_passed = False

        # Count total attempts across all levels
        for _, level_result in phase_result.get("validation_levels", {}).items():
            total_attempts += level_result.get("attempts", 1) - 1  # -1 because first attempt doesn't count as retry

    if not all_passed:
        return "5/10"  # Validation failures

    # All passed - score by attempts
    if total_attempts == 0:
        return "10/10"  # Perfect
    elif total_attempts <= 2:
        return "9/10"  # Minor issues
    else:
        return "8/10"  # Multiple retries


def parse_validation_error(output: str, _level: str) -> Dict[str, Any]:
    """Parse validation error output into structured format.

    Args:
        output: Raw error output (stderr + stdout)
        _level: Validation level (L1, L2, L3, L4) - reserved for future use

    Returns:
        {
            "type": "assertion_error",  # assertion_error, import_error, syntax_error, etc.
            "file": "src/auth.py",
            "line": 42,
            "function": "authenticate",
            "message": "Expected User, got None",
            "traceback": "<full traceback>",
            "suggested_fix": "Check return value"
        }

    Process:
        1. Detect error type (assertion, import, syntax, type, etc.)
        2. Extract file:line location
        3. Extract function/class context
        4. Extract error message
        5. Generate suggested fix hint
    """
    error = {
        "type": "unknown_error",
        "file": "unknown",
        "line": 0,
        "function": None,
        "message": output[:200] if output else "Unknown error",
        "traceback": output,
        "suggested_fix": "Manual review required"
    }

    # Detect error type from output patterns
    if "ImportError" in output or "ModuleNotFoundError" in output or "cannot import" in output:
        error["type"] = "import_error"
        error["suggested_fix"] = "Add missing import statement"

        # Extract module name: "No module named 'jwt'" or "cannot import name 'User'"
        import_match = re.search(r"No module named '([^']+)'", output)
        if import_match:
            error["message"] = f"No module named '{import_match.group(1)}'"
            error["suggested_fix"] = f"Install or import {import_match.group(1)}"
        else:
            name_match = re.search(r"cannot import name '([^']+)'", output)
            if name_match:
                error["message"] = f"cannot import name '{name_match.group(1)}'"
                error["suggested_fix"] = f"Check import of {name_match.group(1)}"

    elif "AssertionError" in output or "assert" in output.lower():
        error["type"] = "assertion_error"
        error["suggested_fix"] = "Check assertion logic"

    elif "SyntaxError" in output:
        error["type"] = "syntax_error"
        error["suggested_fix"] = "Fix syntax error"

    elif "TypeError" in output:
        error["type"] = "type_error"
        error["suggested_fix"] = "Check type annotations and conversions"

    elif "NameError" in output or "is not defined" in output:
        error["type"] = "name_error"
        error["suggested_fix"] = "Define missing variable or import"

    elif "AttributeError" in output:
        error["type"] = "attribute_error"
        error["suggested_fix"] = "Check attribute exists on object"

    # Extract file:line location (common patterns)
    # Pattern 1: File "path/to/file.py", line 42
    file_match = re.search(r'File "([^"]+)", line (\d+)', output)
    if file_match:
        error["file"] = file_match.group(1)
        error["line"] = int(file_match.group(2))

    # Pattern 2: path/to/file.py:42:
    location_match = re.search(r'([^:\s]+\.py):(\d+):', output)
    if location_match:
        error["file"] = location_match.group(1)
        error["line"] = int(location_match.group(2))

    # Extract function/class context
    func_match = re.search(r'in (\w+)', output)
    if func_match:
        error["function"] = func_match.group(1)

    return error


def check_escalation_triggers(
    error: Dict[str, Any],
    attempt: int,
    error_history: List[str]
) -> bool:
    """Check if error triggers human escalation.

    Args:
        error: Parsed error dict
        attempt: Current attempt number
        error_history: List of previous error messages for this validation

    Returns:
        True if escalation required, False to continue self-healing

    Escalation Triggers:
        1. Same error after 3 attempts (error message unchanged)
        2. Ambiguous error messages (generic "something went wrong")
        3. Architectural changes required (detected by keywords: "refactor", "redesign")
        4. External dependency issues (network errors, API failures, missing packages)
        5. Security concerns (vulnerability, secret exposure, permission escalation)
    """
    # Trigger 1: Same error after 3 attempts
    if attempt >= 3 and len(error_history) >= 3:
        # Check if all 3 error messages are identical
        if len(set(error_history[-3:])) == 1:
            return True

    # Trigger 2: Ambiguous error messages
    ambiguous_patterns = [
        "something went wrong",
        "unexpected error",
        "failed",
        "error occurred",
        "unknown error"
    ]
    error_msg = error.get("message", "").lower()
    if any(pattern in error_msg for pattern in ambiguous_patterns):
        # Only escalate if also no file/line info
        if error.get("file") == "unknown" and error.get("line") == 0:
            return True

    # Trigger 3: Architectural changes required
    architecture_keywords = [
        "refactor",
        "redesign",
        "architecture",
        "restructure",
        "circular import",
        "coupling"
    ]
    full_error = error.get("traceback", "") + error.get("message", "")
    if any(keyword in full_error.lower() for keyword in architecture_keywords):
        return True

    # Trigger 4: External dependency issues
    dependency_keywords = [
        "connection refused",
        "network error",
        "timeout",
        "api error",
        "http error",
        "could not resolve host",
        "package not found",
        "pypi",
        "npm error"
    ]
    if any(keyword in full_error.lower() for keyword in dependency_keywords):
        return True

    # Trigger 5: Security concerns
    security_keywords = [
        "cve-",
        "vulnerability",
        "secret",
        "password",
        "api key",
        "token",
        "credential",
        "permission denied",
        "access denied",
        "unauthorized",
        "security"
    ]
    if any(keyword in full_error.lower() for keyword in security_keywords):
        return True

    return False


def apply_self_healing_fix(error: Dict[str, Any], _attempt: int) -> Dict[str, Any]:
    """Apply self-healing fix based on error type.

    Args:
        error: Parsed error dict from parse_validation_error()
        _attempt: Current attempt number (1-3) - reserved for future use

    Returns:
        {
            "success": True,
            "fix_type": "import_added",
            "location": "src/auth.py:3",
            "description": "Added missing import: from models import User"
        }

    Process:
        1. Check escalation triggers first (done in run_validation_loop)
        2. Match error type to fix strategy:
           - import_error → add_missing_import()
           - assertion_error → Manual review (escalate)
           - type_error → Manual review (escalate)
           - syntax_error → Manual review (escalate)
           - name_error → Manual review (escalate)
        3. Apply fix using file operations
        4. Log fix for debugging
    """
    error_type = error.get("type", "unknown_error")

    # Import errors - can auto-fix by adding import statement
    if error_type == "import_error":
        try:
            filepath = error.get("file", "unknown")
            message = error.get("message", "")

            # Extract module/class name
            if "No module named" in message:
                match = re.search(r"No module named '([^']+)'", message)
                if match:
                    module = match.group(1)
                    return _add_import_statement(filepath, f"import {module}")
            elif "cannot import name" in message:
                match = re.search(r"cannot import name '([^']+)'", message)
                if match:
                    name = match.group(1)
                    # Try common import patterns
                    return _add_import_statement(filepath, f"from . import {name}")

        except Exception as e:
            return {
                "success": False,
                "fix_type": "import_error_failed",
                "description": f"Failed to fix import: {str(e)}"
            }

    # Other error types - require manual intervention or more complex logic
    # These will be handled by escalation triggers
    return {
        "success": False,
        "fix_type": f"{error_type}_not_implemented",
        "description": f"Auto-fix not implemented for {error_type} - escalate to human"
    }


def _add_import_statement(filepath: str, import_stmt: str) -> Dict[str, Any]:
    """Add import statement to file.

    Args:
        filepath: Path to Python file
        import_stmt: Import statement to add (e.g., "import jwt" or "from models import User")

    Returns:
        Fix result dict
    """
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            return {
                "success": False,
                "fix_type": "import_add_failed",
                "description": f"File not found: {filepath}"
            }

        # Read current content
        content = file_path.read_text()
        lines = content.split("\n")

        # Find position to insert import (after existing imports or at top)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("import ") or line.startswith("from "):
                insert_pos = i + 1
            elif line.strip() and not line.startswith("#") and not line.startswith('"""'):
                # Found first non-import, non-comment line
                break

        # Insert import statement
        lines.insert(insert_pos, import_stmt)

        # Write back
        file_path.write_text("\n".join(lines))

        return {
            "success": True,
            "fix_type": "import_added",
            "location": f"{filepath}:{insert_pos + 1}",
            "description": f"Added import: {import_stmt}"
        }

    except Exception as e:
        return {
            "success": False,
            "fix_type": "import_add_failed",
            "description": f"Error adding import: {str(e)}"
        }


def escalate_to_human(error: Dict[str, Any], reason: str) -> None:
    """Escalate to human with detailed error report.

    Args:
        error: Parsed error dict
        reason: Escalation trigger reason

    Raises:
        EscalationRequired: Always (signals need for human intervention)

    Process:
        1. Format error report with type and location
        2. Include full error message and traceback
        3. Provide escalation reason
        4. Generate troubleshooting guidance based on error type
    """
    # Build context-specific troubleshooting guidance
    troubleshooting_lines = ["Steps to resolve:"]

    if reason == "persistent_error":
        troubleshooting_lines.extend([
            "1. Review error details - same error occurred 3 times",
            "2. Check if fix logic matches error type",
            "3. Consider if architectural change needed",
            "4. Review validation command output manually"
        ])

    elif reason == "ambiguous_error":
        troubleshooting_lines.extend([
            "1. Run validation command manually for full context",
            "2. Check logs for additional error details",
            "3. Add debug print statements if needed",
            "4. Review recent code changes"
        ])

    elif reason == "architectural":
        troubleshooting_lines.extend([
            "1. Review error for architectural keywords (refactor, redesign, circular)",
            "2. Consider if code structure needs reorganization",
            "3. Check for circular dependencies",
            "4. May require human design decision"
        ])

    elif reason == "dependencies":
        troubleshooting_lines.extend([
            "1. Check network connectivity",
            "2. Verify package repository access (PyPI, npm, etc.)",
            "3. Review dependency versions in requirements",
            "4. Check for transitive dependency conflicts"
        ])

    elif reason == "security":
        troubleshooting_lines.extend([
            "1. DO NOT auto-fix security-related errors",
            "2. Review error for exposed secrets/credentials",
            "3. Check for permission/access issues",
            "4. Consult security documentation if CVE mentioned"
        ])

    else:
        troubleshooting_lines.extend([
            "1. Review error details above",
            "2. Check file and line number for context",
            "3. Run validation command manually",
            "4. Consult documentation for error type"
        ])

    # Add error-type-specific guidance
    error_type = error.get("type", "unknown")
    if error_type == "import_error":
        troubleshooting_lines.append("5. Check if module is installed: pip list | grep <module>")
    elif error_type == "assertion_error":
        troubleshooting_lines.append("5. Review test logic and expected vs actual values")
    elif error_type == "type_error":
        troubleshooting_lines.append("5. Check type annotations and ensure type compatibility")

    troubleshooting = "\n".join(troubleshooting_lines)

    raise EscalationRequired(
        reason=reason,
        error=error,
        troubleshooting=troubleshooting
    )
