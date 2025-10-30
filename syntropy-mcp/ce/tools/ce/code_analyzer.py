"""Shared code analysis module for pattern detection across languages.

This module provides unified code analysis functions used by both pattern_extractor
and drift_analyzer to eliminate duplication and maintain a single source of truth
for pattern detection logic.
"""

import ast
import re
from typing import Dict, List


def analyze_code_patterns(code: str, language: str) -> Dict[str, List[str]]:
    """Analyze code and extract semantic patterns.

    Args:
        code: Source code string
        language: Programming language (python, typescript, javascript, etc.)

    Returns:
        Dict mapping pattern categories to detected patterns:
        {
            "code_structure": ["async/await", "class-based", ...],
            "error_handling": ["try-except", "early-return", ...],
            "naming_conventions": ["snake_case", "camelCase", ...],
            "data_flow": ["props", "state", ...],
            "test_patterns": ["pytest", "jest", ...],
            "import_patterns": ["relative", "absolute"]
        }
    """
    if language.lower() in ("python", "py"):
        return _analyze_python(code)
    elif language.lower() in ("typescript", "ts", "javascript", "js"):
        return _analyze_typescript(code)
    else:
        return _analyze_generic(code)


def _analyze_python(code: str) -> Dict[str, List[str]]:
    """Analyze Python code using AST for accurate pattern detection.

    Falls back to regex-based analysis if AST parsing fails.
    Refactored to reduce nesting depth from 7 to 4 levels.
    """
    from .pattern_detectors import (
        process_class_node,
        process_function_node,
        process_try_node,
        process_if_node,
        process_import_node
    )

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
        # Fallback to regex if AST parsing fails
        return _analyze_generic(code)

    # Code structure analysis using extracted pattern detectors
    for node in ast.walk(tree):
        # Async patterns
        if isinstance(node, (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith, ast.Await)):
            patterns["code_structure"].append("async/await")

        # Class-based (delegated to reduce nesting)
        elif isinstance(node, ast.ClassDef):
            process_class_node(node, patterns)

        # Function-based (delegated to reduce nesting)
        elif isinstance(node, ast.FunctionDef):
            process_function_node(node, patterns)

        # Error handling
        elif isinstance(node, ast.Try):
            process_try_node(node, patterns)

        elif isinstance(node, ast.If):
            process_if_node(node, patterns)

        # Import patterns
        elif isinstance(node, ast.ImportFrom):
            process_import_node(node, patterns)

    return patterns


def _analyze_typescript(code: str) -> Dict[str, List[str]]:
    """Analyze TypeScript/JavaScript code using regex patterns."""
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
    class_names = re.findall(r"class\s+(\w+)", code)

    for name in func_names + var_names + class_names:
        if "_" in name:
            patterns["naming_conventions"].append("snake_case")
        elif name[0].islower() and any(c.isupper() for c in name[1:]):
            patterns["naming_conventions"].append("camelCase")
        elif name[0].isupper():
            patterns["naming_conventions"].append("PascalCase")

    # Test patterns
    if re.search(r"\bdescribe\(", code) or re.search(r"\bit\(", code):
        patterns["test_patterns"].append("jest")
    if re.search(r"\btest\(", code):
        patterns["test_patterns"].append("jest")

    # Import patterns
    if re.search(r"import\s+.*?\s+from\s+['\"]\.{1,2}/", code):
        patterns["import_patterns"].append("relative")
    if re.search(r"import\s+.*?\s+from\s+['\"][^./]", code):
        patterns["import_patterns"].append("absolute")

    return patterns


def _analyze_generic(code: str) -> Dict[str, List[str]]:
    """Fallback regex-based pattern detection for any language."""
    patterns = {
        "code_structure": [],
        "error_handling": [],
        "naming_conventions": [],
        "data_flow": [],
        "test_patterns": [],
        "import_patterns": []
    }

    # Basic structure detection
    if "async" in code.lower() or "await" in code.lower():
        patterns["code_structure"].append("async/await")
    if "class " in code.lower():
        patterns["code_structure"].append("class-based")
    if "function" in code.lower() or "def " in code:
        patterns["code_structure"].append("functional")

    # Error handling
    if "try" in code.lower():
        patterns["error_handling"].append("try-catch")
    if re.search(r"\breturn\b.*?(?:if|when)", code, re.IGNORECASE):
        patterns["error_handling"].append("early-return")

    # Naming patterns (simple heuristic)
    if "_" in code:
        patterns["naming_conventions"].append("snake_case")
    if re.search(r"[a-z][A-Z]", code):
        patterns["naming_conventions"].append("camelCase")

    return patterns


def determine_language(file_extension: str) -> str:
    """Map file extension to language identifier.

    Args:
        file_extension: File extension including dot (e.g., ".py", ".ts")

    Returns:
        Language identifier string
    """
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
    return lang_map.get(file_extension.lower(), "unknown")


def count_code_symbols(code: str, language: str) -> int:
    """Estimate symbol count (functions, classes, methods) in code.

    Args:
        code: Source code string
        language: Programming language

    Returns:
        Estimated count of code symbols
    """
    if language.lower() in ("python", "py"):
        try:
            tree = ast.parse(code)
            return sum(1 for node in ast.walk(tree)
                      if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)))
        except SyntaxError:
            pass

    # Fallback: regex-based counting
    func_count = len(re.findall(r"\b(def|function|class)\s+\w+", code))
    return func_count
