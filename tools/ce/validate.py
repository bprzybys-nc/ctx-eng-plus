"""Validation gates: 4-level validation system."""

import sys
import re
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime, timezone

from .core import run_cmd
from .pattern_extractor import extract_patterns_from_prp
from .drift_analyzer import analyze_implementation, calculate_drift_score, get_auto_fix_suggestions


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


def validate_level_4(
    prp_path: str,
    implementation_paths: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Run Level 4 validation: Pattern Conformance.

    Args:
        prp_path: Path to PRP markdown file
        implementation_paths: Files to analyze; auto-detected if None via:
            1. Parse PRP IMPLEMENTATION BLUEPRINT for file references
               (searches for patterns: "Modify: path/file.py", "Create: path/file.py")
            2. Fallback: git diff --name-only main...HEAD
            3. Fallback: Interactive prompt for user to specify files

    Returns:
        {
            "success": bool,
            "drift_score": float,
            "threshold_action": str,  # auto_accept | auto_fix | escalate
            "decision": Optional[str],  # if escalated: accepted | rejected | examples_updated
            "justification": Optional[str],
            "duration": float,
            "level": 4
        }

    Raises:
        RuntimeError: If PRP parsing fails or Serena MCP unavailable

    Process:
        1. Extract patterns from PRP EXAMPLES
        2. Analyze implementation with Serena MCP
        3. Calculate drift score
        4. Apply threshold logic (auto-accept/fix/escalate)
        5. If escalated: prompt user, persist decision
        6. Return validation result
    """
    start_time = time.time()

    try:
        # Step 1: Auto-detect implementation paths if not provided
        if implementation_paths is None:
            implementation_paths = _auto_detect_implementation_paths(prp_path)

        # Step 2: Extract expected patterns from PRP
        expected_patterns = extract_patterns_from_prp(prp_path)

        # Step 3: Analyze implementation
        analysis_result = analyze_implementation(prp_path, implementation_paths)
        detected_patterns = analysis_result["detected_patterns"]

        # Step 4: Calculate drift score
        drift_result = calculate_drift_score(expected_patterns, detected_patterns)
        drift_score = drift_result["drift_score"]
        threshold_action = drift_result["threshold_action"]

        # Step 5: Handle based on threshold
        decision = None
        justification = None

        if threshold_action == "auto_accept":
            # Drift < 10%: Auto-accept
            success = True
        elif threshold_action == "auto_fix":
            # Drift 10-30%: Display suggestions (MVP: no auto-apply)
            success = True
            suggestions = get_auto_fix_suggestions(drift_result["mismatches"])
            print("\n⚠️  MODERATE DRIFT DETECTED - SUGGESTIONS:")
            for suggestion in suggestions:
                print(f"   {suggestion}")
            print()
        else:
            # Drift >= 30%: Escalate to user
            success, decision, justification = _handle_user_escalation(
                prp_path,
                drift_result,
                implementation_paths
            )

            # Persist decision to PRP if user decided
            if decision:
                _persist_drift_decision(prp_path, drift_result, decision, justification)

        duration = time.time() - start_time

        return {
            "success": success,
            "drift_score": drift_score,
            "threshold_action": threshold_action,
            "decision": decision,
            "justification": justification,
            "duration": round(duration, 2),
            "level": 4,
            "files_analyzed": analysis_result["files_analyzed"],
            "category_scores": drift_result["category_scores"]
        }

    except Exception as e:
        duration = time.time() - start_time
        return {
            "success": False,
            "drift_score": 100.0,
            "threshold_action": "escalate",
            "decision": None,
            "justification": None,
            "duration": round(duration, 2),
            "level": 4,
            "error": str(e)
        }


def _auto_detect_implementation_paths(prp_path: str) -> List[str]:
    """Auto-detect implementation file paths from PRP or git."""
    # Strategy 1: Parse PRP IMPLEMENTATION BLUEPRINT
    paths = _parse_prp_blueprint_paths(prp_path)
    if paths:
        return paths

    # Strategy 2: Git diff (changed files)
    result = run_cmd("git diff --name-only main...HEAD", capture_output=True)
    if result["success"] and result["stdout"].strip():
        paths = [p.strip() for p in result["stdout"].strip().split("\n")]
        # Filter for code files only
        code_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java"}
        paths = [p for p in paths if Path(p).suffix in code_extensions]
        if paths:
            return paths

    # Strategy 3: Interactive prompt
    print("\n🔍 Unable to auto-detect implementation files.")
    print("Please specify file paths to analyze (comma-separated):")
    user_input = input("> ").strip()
    if user_input:
        return [p.strip() for p in user_input.split(",")]

    raise RuntimeError(
        "No implementation files specified\n"
        "🔧 Troubleshooting: Specify --files flag or add file references to PRP"
    )


def _parse_prp_blueprint_paths(prp_path: str) -> List[str]:
    """Parse implementation file paths from PRP IMPLEMENTATION BLUEPRINT section."""
    content = Path(prp_path).read_text()

    # Find IMPLEMENTATION BLUEPRINT section
    blueprint_match = re.search(
        r"##\s+.*?IMPLEMENTATION\s+BLUEPRINT.*?\n(.*?)(?=\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not blueprint_match:
        return []

    blueprint_text = blueprint_match.group(1)

    # Extract file paths from patterns like "Modify: path/file.py", "Create: path/file.py"
    file_patterns = re.findall(
        r"(?:Modify|Create|Update|Add):\s*([`]?)([a-zA-Z0-9_/\.\-]+\.(py|ts|tsx|js|jsx|go|rs|java))\1",
        blueprint_text,
        re.IGNORECASE
    )

    paths = [match[1] for match in file_patterns]
    return list(set(paths))  # Deduplicate


def _handle_user_escalation(
    prp_path: str,
    drift_result: Dict[str, Any],
    implementation_paths: List[str]
) -> tuple[bool, Optional[str], Optional[str]]:
    """Interactive CLI for high-drift cases requiring human decision.

    Returns:
        (success, decision, justification) tuple
    """
    drift_score = drift_result["drift_score"]
    category_scores = drift_result["category_scores"]
    mismatches = drift_result["mismatches"]

    print("\n" + "=" * 80)
    print(f"🚨 HIGH DRIFT DETECTED: {drift_score:.1f}%")
    print("=" * 80)
    print(f"\nPRP: {prp_path}")
    print(f"Implementation: {', '.join(implementation_paths)}")
    print("\nDRIFT BREAKDOWN:")
    print("━" * 80)
    print(f"{'Category':<25} {'Expected':<20} {'Detected':<20} {'Drift':<10}")
    print("─" * 80)

    for category, score in category_scores.items():
        print(f"{category:<25} {'(see PRP)':<20} {'(varies)':<20} {score:.1f}%")

    print("━" * 80)

    # Show affected patterns
    if mismatches:
        print("\nAFFECTED PATTERNS:")
        for mismatch in mismatches[:5]:  # Show first 5
            expected = mismatch["expected"]
            detected = mismatch.get("detected", "None")
            category = mismatch["category"]
            print(f"• {category}: Expected '{expected}', Detected {detected}")

    print("\nOPTIONS:")
    print("[A] Accept drift (add DRIFT_JUSTIFICATION to PRP)")
    print("[R] Reject and halt (requires manual refactoring)")
    print("[U] Update EXAMPLES in PRP (update specification)")
    print("[Q] Quit without saving")
    print()

    while True:
        choice = input("Your choice (A/R/U/Q): ").strip().upper()

        if choice == "A":
            justification = input("Justification for accepting drift: ").strip()
            if not justification:
                print("⚠️  Justification required. Try again.")
                continue
            return (True, "accepted", justification)

        elif choice == "R":
            print("\n❌ L4 validation REJECTED - Manual refactoring required")
            return (False, "rejected", "User rejected high drift")

        elif choice == "U":
            print("\nℹ️  Update EXAMPLES section in PRP manually, then re-run validation")
            return (False, "examples_updated", "User chose to update PRP EXAMPLES")

        elif choice == "Q":
            print("\n❌ L4 validation aborted")
            return (False, None, None)

        else:
            print("⚠️  Invalid choice. Please enter A, R, U, or Q.")


def _persist_drift_decision(
    prp_path: str,
    drift_result: Dict[str, Any],
    decision: str,
    justification: Optional[str]
):
    """Persist DRIFT_JUSTIFICATION to PRP YAML header."""
    content = Path(prp_path).read_text()

    # Build drift decision YAML
    drift_yaml = f"""drift_decision:
  score: {drift_result['drift_score']}
  action: "{decision}"
  justification: "{justification or 'N/A'}"
  timestamp: "{datetime.now(timezone.utc).isoformat()}"
  category_breakdown:
"""

    for category, score in drift_result["category_scores"].items():
        drift_yaml += f"    {category}: {score}\n"

    drift_yaml += f'  reviewer: "human"\n'

    # Insert into YAML header (after last YAML field before ---)
    yaml_end_match = re.search(r"(---\s*\n)", content)
    if yaml_end_match:
        # Insert before closing ---
        insert_pos = yaml_end_match.start()
        new_content = content[:insert_pos] + drift_yaml + content[insert_pos:]
        Path(prp_path).write_text(new_content)
        print(f"\n✅ Drift decision persisted to {prp_path}")
    else:
        print(f"\n⚠️  Warning: Could not find YAML header in {prp_path}")


def calculate_confidence(results: Dict[int, Dict[str, Any]]) -> int:
    """Calculate confidence score (1-10) based on validation results.

    Scoring breakdown:
    - Baseline: 6 (untested code)
    - Level 1 (Syntax & Style): +1
    - Level 2 (Unit Tests): +2 (with >80% coverage)
    - Level 3 (Integration): +1
    - Level 4 (Pattern Conformance): +1 (NEW)
    - Max: 10/10 (production-ready)

    Requirements for +1 from L4:
    - drift_score < 10% (auto-accept threshold)
    - OR drift_score < 30% AND decision = "accepted" with justification

    Args:
        results: Dict mapping level (1-4) to validation results

    Returns:
        Confidence score 1-10

    Examples:
        >>> results = {1: {"success": True}, 2: {"success": True, "coverage": 0.85}}
        >>> calculate_confidence(results)
        9  # Without L3, L4

        >>> results = {
        ...     1: {"success": True},
        ...     2: {"success": True, "coverage": 0.85},
        ...     3: {"success": True},
        ...     4: {"success": True, "drift_score": 8.5}
        ... }
        >>> calculate_confidence(results)
        10  # All gates pass
    """
    score = 6  # Baseline

    if results.get(1, {}).get("success"):
        score += 1

    if results.get(2, {}).get("success") and results.get(2, {}).get("coverage", 0) > 0.8:
        score += 2

    if results.get(3, {}).get("success"):
        score += 1

    # Level 4: Pattern conformance (NEW)
    l4_result = results.get(4, {})
    if l4_result.get("success"):
        drift_score = l4_result.get("drift_score", 100)
        decision = l4_result.get("decision")

        # Pass L4 if:
        # 1. drift < 10% (auto-accept)
        # 2. drift < 30% AND explicitly accepted with justification
        if drift_score < 10.0 or (drift_score < 30.0 and decision == "accepted"):
            score += 1

    return min(score, 10)


def validate_all() -> Dict[str, Any]:
    """Run all validation levels sequentially.

    Returns:
        Dict with: success (bool), results (Dict[int, Dict]),
                   total_duration (float), confidence_score (int)

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

    # Calculate confidence score
    confidence_score = calculate_confidence(results)

    return {
        "success": overall_success,
        "results": results,
        "total_duration": total_duration,
        "confidence_score": confidence_score
    }
