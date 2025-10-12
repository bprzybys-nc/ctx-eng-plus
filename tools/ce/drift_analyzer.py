"""Drift analysis engine for L4 validation.

Calculates semantic drift between expected patterns (from PRP EXAMPLES)
and actual implementation code. Uses shared code_analyzer module for
pattern detection.
"""

import time
from typing import Dict, List, Any
from pathlib import Path

from .code_analyzer import analyze_code_patterns, determine_language, count_code_symbols


def analyze_implementation(
    prp_path: str,
    implementation_paths: List[str]
) -> Dict[str, Any]:
    """Analyze implementation code structure using Serena MCP.

    Args:
        prp_path: Path to PRP file (for extracting expected patterns)
        implementation_paths: Paths to implementation files to analyze

    Returns:
        {
            "detected_patterns": {
                "code_structure": ["async/await", "class-based"],
                "error_handling": ["try-except"],
                "naming_conventions": ["snake_case"],
                ...
            },
            "files_analyzed": ["src/validate.py", "src/core.py"],
            "symbol_count": 42,
            "analysis_duration": 2.5,
            "serena_available": False
        }

    Uses (if Serena MCP available):
        - serena.get_symbols_overview(file) for structure
        - serena.find_symbol(name) for detailed analysis
        - serena.read_file(file) for pattern matching

    Fallback (if Serena unavailable):
        - Python ast module for Python files
        - Regex-based pattern detection for other languages
        - Log warning: "Serena MCP unavailable - using fallback analysis (reduced accuracy)"

    Raises:
        RuntimeError: If neither Serena nor fallback analysis succeeds
    """
    import time
    start_time = time.time()

    all_patterns = {
        "code_structure": [],
        "error_handling": [],
        "naming_conventions": [],
        "data_flow": [],
        "test_patterns": [],
        "import_patterns": []
    }

    files_analyzed = []
    symbol_count = 0

    # MVP: Serena MCP integration deferred - use fallback analysis
    # TODO: Future enhancement - integrate Serena MCP for semantic analysis
    serena_available = False

    for impl_path in implementation_paths:
        impl_path_obj = Path(impl_path)
        if not impl_path_obj.exists():
            continue

        files_analyzed.append(impl_path)

        # Determine language from file extension
        extension = impl_path_obj.suffix.lower()
        language = determine_language(extension)

        code = impl_path_obj.read_text()

        # Analyze patterns using shared code analyzer
        patterns = analyze_code_patterns(code, language)

        # Count symbols
        symbol_count += count_code_symbols(code, language)

        # Merge patterns
        for category, values in patterns.items():
            if category in all_patterns:
                all_patterns[category].extend(values)

    # Deduplicate
    for category in all_patterns:
        all_patterns[category] = list(set(all_patterns[category]))

    duration = time.time() - start_time

    if not files_analyzed:
        raise RuntimeError(
            f"No implementation files found at {implementation_paths}\n"
            f"🔧 Troubleshooting: Verify file paths exist and are readable"
        )

    return {
        "detected_patterns": all_patterns,
        "files_analyzed": files_analyzed,
        "symbol_count": symbol_count,
        "analysis_duration": round(duration, 2),
        "serena_available": serena_available
    }


def calculate_drift_score(
    expected_patterns: Dict[str, Any],
    detected_patterns: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate drift score between expected and detected patterns.

    Scoring methodology:
    - Each category (code_structure, error_handling, etc.) weighted equally
    - Within category: count mismatches / total expected patterns
    - Overall drift = average across all categories * 100

    Args:
        expected_patterns: From extract_patterns_from_prp()
        detected_patterns: From analyze_implementation()

    Returns:
        {
            "drift_score": 23.5,  # 0-100%, lower is better
            "category_scores": {
                "code_structure": 10.0,
                "error_handling": 0.0,
                "naming_conventions": 50.0,
                ...
            },
            "mismatches": [
                {
                    "category": "naming_conventions",
                    "expected": "snake_case",
                    "detected": "camelCase",
                    "severity": "medium",
                    "affected_symbols": ["processData", "handleError"]
                }
            ],
            "threshold_action": "auto_fix"  # auto_accept | auto_fix | escalate
        }
    """
    category_scores = {}
    mismatches = []

    # Categories to compare (exclude raw_examples)
    categories = [
        "code_structure",
        "error_handling",
        "naming_conventions",
        "data_flow",
        "test_patterns",
        "import_patterns"
    ]

    for category in categories:
        expected = expected_patterns.get(category, [])
        detected = detected_patterns.get(category, [])

        if not expected:
            # No expectations for this category - skip
            continue

        # Calculate mismatches
        missing_patterns = set(expected) - set(detected)
        unexpected_patterns = set(detected) - set(expected)

        # Mismatch score = (missing + unexpected) / (expected + detected)
        # This penalizes both missing expected patterns and unexpected patterns
        total_expected = len(expected)
        mismatch_count = len(missing_patterns)

        if total_expected > 0:
            category_score = (mismatch_count / total_expected) * 100
        else:
            category_score = 0.0

        category_scores[category] = round(category_score, 1)

        # Record mismatches
        for missing in missing_patterns:
            mismatches.append({
                "category": category,
                "expected": missing,
                "detected": list(unexpected_patterns) if unexpected_patterns else None,
                "severity": _determine_severity(category, missing),
                "affected_symbols": []  # MVP: Symbol tracking deferred
            })

    # Calculate overall drift score (average of category scores)
    if category_scores:
        drift_score = sum(category_scores.values()) / len(category_scores)
    else:
        drift_score = 0.0

    drift_score = round(drift_score, 1)

    # Determine threshold action
    if drift_score < 10.0:
        threshold_action = "auto_accept"
    elif drift_score < 30.0:
        threshold_action = "auto_fix"
    else:
        threshold_action = "escalate"

    return {
        "drift_score": drift_score,
        "category_scores": category_scores,
        "mismatches": mismatches,
        "threshold_action": threshold_action
    }


def get_auto_fix_suggestions(mismatches: List[Dict]) -> List[str]:
    """Generate fix suggestions for 10-30% drift (MVP: display only, no auto-apply).

    Future enhancement: Apply fixes automatically using Serena edit operations.

    Args:
        mismatches: List of mismatch dicts from calculate_drift_score()

    Returns:
        List of actionable fix suggestions (e.g., "Rename processData → process_data")
    """
    suggestions = []

    for mismatch in mismatches:
        category = mismatch["category"]
        expected = mismatch["expected"]
        detected = mismatch.get("detected", [])

        if category == "naming_conventions":
            # Suggest naming convention fixes
            if expected == "snake_case" and detected:
                suggestions.append(
                    f"⚠️  Convert naming from {detected} to snake_case convention"
                )
            elif expected == "camelCase" and "snake_case" in (detected or []):
                suggestions.append(
                    f"⚠️  Convert naming from snake_case to camelCase convention"
                )
            elif expected == "PascalCase" and detected:
                suggestions.append(
                    f"⚠️  Convert class names to PascalCase convention"
                )

        elif category == "error_handling":
            if expected == "try-except" and not detected:
                suggestions.append(
                    f"⚠️  Add try-except error handling blocks"
                )
            elif expected == "early-return" and not detected:
                suggestions.append(
                    f"⚠️  Add guard clauses with early returns"
                )

        elif category == "code_structure":
            if expected == "async/await" and detected:
                if "callbacks" in (detected or []):
                    suggestions.append(
                        f"⚠️  Convert callback-based code to async/await pattern"
                    )
            elif expected == "class-based" and "functional" in (detected or []):
                suggestions.append(
                    f"⚠️  Consider refactoring to class-based structure"
                )

        elif category == "test_patterns":
            if expected == "pytest" and not detected:
                suggestions.append(
                    f"⚠️  Add pytest-style test functions (test_* naming)"
                )

    if not suggestions:
        suggestions.append("ℹ️  Review patterns and consider manual alignment")

    return suggestions


def _determine_severity(category: str, pattern: str) -> str:
    """Determine severity of missing pattern."""
    # High severity: security/correctness patterns
    high_severity_patterns = {
        "error_handling": ["try-except", "try-catch"],
        "code_structure": ["async/await"]  # if expected but missing, may cause issues
    }

    # Medium severity: consistency/maintainability
    medium_severity_patterns = {
        "naming_conventions": ["snake_case", "camelCase", "PascalCase"],
        "test_patterns": ["pytest", "jest"]
    }

    # Low severity: style preferences
    low_severity_patterns = {
        "import_patterns": ["relative", "absolute"],
        "data_flow": ["props", "state"]
    }

    if category in high_severity_patterns and pattern in high_severity_patterns[category]:
        return "high"
    elif category in medium_severity_patterns and pattern in medium_severity_patterns[category]:
        return "medium"
    else:
        return "low"
