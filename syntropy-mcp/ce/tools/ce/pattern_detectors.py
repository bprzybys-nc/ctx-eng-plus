"""Pattern detection helpers for reducing nesting depth in analysis functions.

Extracted from code_analyzer.py and update_context.py to reduce nesting from 7/5 levels to 4 max.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Tuple, Set
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# AST Pattern Detection (from code_analyzer.py)
# ============================================================================

def process_class_node(node: ast.ClassDef, patterns: Dict[str, List[str]]) -> None:
    """Process class node for patterns (reduces nesting in _analyze_python).

    Args:
        node: AST ClassDef node
        patterns: Pattern dict to update
    """
    patterns["code_structure"].append("class-based")

    # Check for decorators
    if node.decorator_list:
        process_class_decorators(node, patterns)

    # Check naming
    if node.name[0].isupper():
        patterns["naming_conventions"].append("PascalCase")


def process_class_decorators(node: ast.ClassDef, patterns: Dict[str, List[str]]) -> None:
    """Process class decorators (extracted to reduce nesting).

    Args:
        node: AST ClassDef node
        patterns: Pattern dict to update
    """
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "dataclass":
            patterns["code_structure"].append("dataclass")


def process_function_node(node: ast.FunctionDef, patterns: Dict[str, List[str]]) -> None:
    """Process function node for patterns (reduces nesting in _analyze_python).

    Args:
        node: AST FunctionDef node
        patterns: Pattern dict to update
    """
    patterns["code_structure"].append("functional")

    # Naming conventions
    if "_" in node.name:
        patterns["naming_conventions"].append("snake_case")
    if node.name.startswith("_") and not node.name.startswith("__"):
        patterns["naming_conventions"].append("_private")

    # Test patterns
    if node.name.startswith("test_"):
        patterns["test_patterns"].append("pytest")

    # Decorators
    if node.decorator_list:
        process_function_decorators(node, patterns)


def process_function_decorators(node: ast.FunctionDef, patterns: Dict[str, List[str]]) -> None:
    """Process function decorators (extracted to reduce nesting).

    Args:
        node: AST FunctionDef node
        patterns: Pattern dict to update
    """
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name):
            if dec.id in ("staticmethod", "classmethod", "property"):
                patterns["code_structure"].append(f"decorator-{dec.id}")
            elif dec.id == "pytest":
                patterns["test_patterns"].append("pytest")


def process_try_node(node: ast.Try, patterns: Dict[str, List[str]]) -> None:
    """Process try/except node for error handling patterns.

    Args:
        node: AST Try node
        patterns: Pattern dict to update
    """
    patterns["error_handling"].append("try-except")
    if node.finalbody:
        patterns["error_handling"].append("try-except-finally")


def process_if_node(node: ast.If, patterns: Dict[str, List[str]]) -> None:
    """Process if node for guard clause detection.

    Args:
        node: AST If node
        patterns: Pattern dict to update
    """
    # Detect guard clauses (early return)
    if node.body and isinstance(node.body[0], ast.Return):
        patterns["error_handling"].append("early-return")


def process_import_node(node: ast.ImportFrom, patterns: Dict[str, List[str]]) -> None:
    """Process import node for import patterns.

    Args:
        node: AST ImportFrom node
        patterns: Pattern dict to update
    """
    if node.level > 0:
        patterns["import_patterns"].append("relative")
    else:
        patterns["import_patterns"].append("absolute")


# ============================================================================
# Drift Detection Pattern Checking (from update_context.py)
# ============================================================================

def check_file_for_violations(
    py_file: Path,
    pattern_checks: Dict[str, List[Tuple[str, str, str]]],
    project_root: Path
) -> Tuple[List[str], bool]:
    """Check single file for pattern violations (reduces nesting in verify_codebase_matches_examples).

    Args:
        py_file: Path to Python file to check
        pattern_checks: Dict of pattern categories to check tuples
        project_root: Project root path for relative path calculation

    Returns:
        Tuple of (violations list, has_violations flag)
    """
    violations = []
    has_violations = False

    try:
        content = py_file.read_text()

        # Check each pattern category
        for category, checks in pattern_checks.items():
            category_violations = check_pattern_category(
                content, checks, py_file, project_root, category
            )
            if category_violations:
                violations.extend(category_violations)
                has_violations = True

    except Exception as e:
        logger.warning(f"Skipping {py_file.name} - read error: {e}")

    return violations, has_violations


def check_pattern_category(
    content: str,
    checks: List[Tuple[str, str, str]],
    py_file: Path,
    project_root: Path,
    category: str
) -> List[str]:
    """Check file content against pattern category checks using AST.

    Args:
        content: File content string
        checks: List of (check_name, regex, fix_desc) tuples
        py_file: Path to file being checked
        project_root: Project root for relative paths
        category: Pattern category name

    Returns:
        List of violation messages

    Note: Uses AST parsing instead of regex to avoid false positives from
    comments/docstrings and to handle multiline code properly.
    """
    from .update_context import PATTERN_FILES

    violations = []

    try:
        tree = ast.parse(content, filename=str(py_file))
    except SyntaxError:
        # Fallback to regex for files with syntax errors
        logger.warning(f"Syntax error in {py_file}, using regex fallback")
        return _check_pattern_category_regex(content, checks, py_file, project_root, category)

    for check_name, regex, fix_desc in checks:
        # Use AST-based checks for known patterns
        if check_name == "missing_troubleshooting":
            if _check_missing_troubleshooting_ast(tree, content):
                violations.append(
                    f"File {py_file.relative_to(project_root)} has {check_name} "
                    f"(violates {PATTERN_FILES.get(category, 'pattern')}): {fix_desc}"
                )
        elif check_name == "bare_except":
            if _check_bare_except_ast(tree):
                violations.append(
                    f"File {py_file.relative_to(project_root)} has {check_name} "
                    f"(violates {PATTERN_FILES.get(category, 'pattern')}): {fix_desc}"
                )
        else:
            # Fallback to regex for other patterns
            matches = re.findall(regex, content, re.MULTILINE | re.DOTALL)
            if matches:
                violations.append(
                    f"File {py_file.relative_to(project_root)} has {check_name} "
                    f"(violates {PATTERN_FILES.get(category, 'pattern')}): {fix_desc}"
                )

    return violations


def _check_missing_troubleshooting_ast(tree: ast.AST, content: str) -> bool:
    """Check for raise statements missing 🔧 troubleshooting using AST.

    Args:
        tree: Parsed AST tree
        content: File content (for emoji check)

    Returns:
        True if violations found, False otherwise
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Raise):
            # Get the line where raise occurs
            if hasattr(node, 'lineno'):
                # Check if 🔧 appears in the raise message
                # We need to look at the actual source for multiline strings
                raise_line = node.lineno
                # Check 5 lines around the raise statement
                lines = content.split('\n')
                start = max(0, raise_line - 2)
                end = min(len(lines), raise_line + 3)
                context = '\n'.join(lines[start:end])

                # If this is a raise with an exception instance
                if node.exc and not ('🔧' in context):
                    return True

    return False


def _check_bare_except_ast(tree: ast.AST) -> bool:
    """Check for bare except clauses using AST.

    Args:
        tree: Parsed AST tree

    Returns:
        True if bare except found, False otherwise
    """
    for node in ast.walk(tree):
        if isinstance(node, ast.Try):
            for handler in node.handlers:
                # Bare except has no type specified
                if handler.type is None:
                    return True

    return False


def _check_pattern_category_regex(
    content: str,
    checks: List[Tuple[str, str, str]],
    py_file: Path,
    project_root: Path,
    category: str
) -> List[str]:
    """Regex fallback for files with syntax errors.

    Args:
        content: File content string
        checks: List of (check_name, regex, fix_desc) tuples
        py_file: Path to file being checked
        project_root: Project root for relative paths
        category: Pattern category name

    Returns:
        List of violation messages
    """
    from .update_context import PATTERN_FILES

    violations = []

    for check_name, regex, fix_desc in checks:
        matches = re.findall(regex, content, re.MULTILINE | re.DOTALL)
        if matches:
            violations.append(
                f"File {py_file.relative_to(project_root)} has {check_name} "
                f"(violates {PATTERN_FILES.get(category, 'pattern')}): {fix_desc}"
            )

    return violations


def check_prp_for_missing_examples(
    prp_path: Path,
    project_root: Path,
    keywords_to_examples: Dict[str, Tuple[str, str, str]]
) -> List[Dict[str, any]]:
    """Check single PRP for missing examples (reduces nesting in detect_missing_examples_for_prps).

    Args:
        prp_path: Path to PRP file
        project_root: Project root path
        keywords_to_examples: Mapping of keywords to example info tuples

    Returns:
        List of missing example dicts
    """
    from .update_context import read_prp_header

    missing_examples = []

    try:
        metadata, content = read_prp_header(prp_path)

        # Check complexity/risk
        complexity = metadata.get("complexity", "unknown")
        if complexity not in ["medium", "high"]:
            return []

        # Check each keyword pattern
        for keyword, (example_name, suggested_path, rationale) in keywords_to_examples.items():
            if keyword.lower() in content.lower():
                example_path = project_root / suggested_path
                if not example_path.exists():
                    missing_examples.append({
                        "prp_id": metadata.get("prp_id", "unknown"),
                        "feature_name": metadata.get("feature_name", "unknown"),
                        "complexity": complexity,
                        "missing_example": example_name,
                        "suggested_path": suggested_path,
                        "rationale": rationale
                    })

    except Exception as e:
        logger.warning(f"Skipping {prp_path.name} - read error: {e}")

    return missing_examples
