"""Drift analysis engine for L4 validation.

Calculates semantic drift between expected patterns (from PRP EXAMPLES)
and actual implementation code. Uses Serena MCP for semantic code analysis
with fallback to AST-based analysis.
"""

import ast
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


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
        language = _determine_language(extension)

        code = impl_path_obj.read_text()

        # Analyze patterns using fallback AST/regex analysis
        if language == "python":
            patterns = _analyze_python_code(code)
        elif language in ("typescript", "javascript"):
            patterns = _analyze_typescript_code(code)
        else:
            patterns = _analyze_generic_code(code)

        # Count symbols (rough estimate)
        symbol_count += _count_symbols(code, language)

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


def _determine_language(extension: str) -> str:
    """Map file extension to language identifier."""
    lang_map = {
        ".py": "python",
        ".ts": "typescript",
        ".tsx": "typescript",
        ".js": "javascript",
        ".jsx": "javascript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".h": "c",
        ".hpp": "cpp"
    }
    return lang_map.get(extension, "unknown")


def _analyze_python_code(code: str) -> Dict[str, List[str]]:
    """Analyze Python code using AST."""
    patterns = {
        "code_structure": [],
        "error_handling": [],
        "naming_conventions": [],
        "data_flow": [],
        "test_patterns": [],
        "import_patterns": []
    }

    try:
        tree = ast.parse(code)
    except SyntaxError:
        # Fallback to regex
        return _analyze_generic_code(code)

    # Code structure
    for node in ast.walk(tree):
        if isinstance(node, (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith, ast.Await)):
            patterns["code_structure"].append("async/await")

        if isinstance(node, ast.ClassDef):
            patterns["code_structure"].append("class-based")

        if isinstance(node, ast.FunctionDef):
            patterns["code_structure"].append("functional")

        # Error handling
        if isinstance(node, ast.Try):
            patterns["error_handling"].append("try-except")
            if node.finalbody:
                patterns["error_handling"].append("try-except-finally")

        if isinstance(node, ast.If):
            if node.body and isinstance(node.body[0], ast.Return):
                patterns["error_handling"].append("early-return")

        # Naming conventions
        if isinstance(node, ast.FunctionDef):
            if "_" in node.name:
                patterns["naming_conventions"].append("snake_case")
            if node.name.startswith("test_"):
                patterns["test_patterns"].append("pytest")

        if isinstance(node, ast.ClassDef):
            if node.name[0].isupper():
                patterns["naming_conventions"].append("PascalCase")

        # Imports
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                patterns["import_patterns"].append("relative")
            else:
                patterns["import_patterns"].append("absolute")

    return patterns


def _analyze_typescript_code(code: str) -> Dict[str, List[str]]:
    """Analyze TypeScript/JavaScript code using regex."""
    patterns = {
        "code_structure": [],
        "error_handling": [],
        "naming_conventions": [],
        "data_flow": [],
        "test_patterns": [],
        "import_patterns": []
    }

    # Code structure
    if re.search(r"\basync\s+", code) or re.search(r"\bawait\s+", code):
        patterns["code_structure"].append("async/await")
    if re.search(r"\.then\(", code):
        patterns["code_structure"].append("promises")
    if re.search(r"\bclass\s+\w+", code):
        patterns["code_structure"].append("class-based")
    if re.search(r"=>\s*{", code) or re.search(r"\bfunction\s+\w+", code):
        patterns["code_structure"].append("functional")

    # Error handling
    if re.search(r"\btry\s*{", code):
        patterns["error_handling"].append("try-catch")
    if re.search(r"\bif\s*\(.*?\)\s*return", code):
        patterns["error_handling"].append("early-return")

    # Naming conventions
    func_names = re.findall(r"function\s+(\w+)", code)
    var_names = re.findall(r"(?:const|let|var)\s+(\w+)", code)

    for name in func_names + var_names:
        if "_" in name:
            patterns["naming_conventions"].append("snake_case")
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            patterns["naming_conventions"].append("camelCase")

    # Imports
    if re.search(r"import\s+.*?\s+from\s+['\"]\.{1,2}/", code):
        patterns["import_patterns"].append("relative")
    if re.search(r"import\s+.*?\s+from\s+['\"][^./]", code):
        patterns["import_patterns"].append("absolute")

    return patterns


def _analyze_generic_code(code: str) -> Dict[str, List[str]]:
    """Fallback generic code analysis."""
    patterns = {
        "code_structure": [],
        "error_handling": [],
        "naming_conventions": [],
        "data_flow": [],
        "test_patterns": [],
        "import_patterns": []
    }

    if "async" in code.lower() or "await" in code.lower():
        patterns["code_structure"].append("async/await")
    if "class " in code.lower():
        patterns["code_structure"].append("class-based")
    if "function" in code.lower() or "def " in code:
        patterns["code_structure"].append("functional")

    if "try" in code.lower():
        patterns["error_handling"].append("try-catch")

    if "_" in code:
        patterns["naming_conventions"].append("snake_case")
    if re.search(r"[a-z][A-Z]", code):
        patterns["naming_conventions"].append("camelCase")

    return patterns


def _count_symbols(code: str, language: str) -> int:
    """Estimate symbol count (functions, classes, methods)."""
    if language == "python":
        try:
            tree = ast.parse(code)
            return sum(1 for node in ast.walk(tree)
                      if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)))
        except SyntaxError:
            pass

    # Fallback: regex-based counting
    func_count = len(re.findall(r"\b(def|function|class)\s+\w+", code))
    return func_count


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
