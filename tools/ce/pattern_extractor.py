"""Pattern extraction from PRP EXAMPLES sections for L4 validation.

This module extracts semantic code patterns from PRP markdown files to enable
architectural drift detection. Patterns are categorized into:
- Code structure (async/await, class-based, functional)
- Error handling (try-except, early-return, null-checks)
- Naming conventions (snake_case, camelCase, PascalCase)
- Data flow (props, state, context, closure)
- Test patterns (pytest, unittest, fixtures)
"""

import ast
import re
from typing import Dict, List, Any, Optional
from pathlib import Path


def extract_patterns_from_prp(prp_path: str) -> Dict[str, Any]:
    """Extract patterns from PRP's EXAMPLES section or INITIAL.md.

    Args:
        prp_path: Path to PRP markdown file

    Returns:
        {
            "code_structure": ["async/await", "class-based", "functional"],
            "error_handling": ["try-except", "early-return", "null-checks"],
            "naming_conventions": ["snake_case", "camelCase", "PascalCase"],
            "data_flow": ["props", "state", "context", "closure"],
            "test_patterns": ["pytest", "unittest", "fixtures"],
            "import_patterns": ["relative", "absolute"],
            "raw_examples": [{"language": "python", "code": "..."}]
        }

    Raises:
        ValueError: If EXAMPLES section not found or malformed
        FileNotFoundError: If PRP file doesn't exist
    """
    prp_path_obj = Path(prp_path)
    if not prp_path_obj.exists():
        raise FileNotFoundError(f"PRP file not found: {prp_path}")

    content = prp_path_obj.read_text()

    # Extract EXAMPLES section (both standalone and embedded in PRP)
    examples_match = re.search(
        r"##\s+EXAMPLES\s*\n(.*?)(?=\n##|\Z)",
        content,
        re.DOTALL | re.IGNORECASE
    )

    if not examples_match:
        raise ValueError(
            f"No EXAMPLES section found in {prp_path}\n"
            f"🔧 Troubleshooting: Ensure PRP contains '## EXAMPLES' section "
            f"with code blocks showing patterns to follow"
        )

    examples_text = examples_match.group(1)

    # Extract code blocks
    code_blocks = re.findall(
        r"```(\w+)?\n(.*?)```",
        examples_text,
        re.DOTALL
    )

    if not code_blocks:
        raise ValueError(
            f"No code blocks found in EXAMPLES section of {prp_path}\n"
            f"🔧 Troubleshooting: Add code examples using ```language markers"
        )

    raw_examples = []
    all_patterns = {
        "code_structure": [],
        "error_handling": [],
        "naming_conventions": [],
        "data_flow": [],
        "test_patterns": [],
        "import_patterns": [],
        "raw_examples": []
    }

    for language, code in code_blocks:
        language = language or "python"  # Default to Python
        raw_examples.append({"language": language, "code": code.strip()})

        # Parse patterns based on language
        if language.lower() in ("python", "py"):
            patterns = _parse_python_patterns(code)
        elif language.lower() in ("typescript", "ts", "javascript", "js"):
            patterns = _parse_typescript_patterns(code)
        else:
            # Fallback: regex-based detection
            patterns = _parse_generic_patterns(code)

        # Merge patterns
        for category, values in patterns.items():
            if category in all_patterns:
                all_patterns[category].extend(values)

    # Deduplicate patterns
    for category in all_patterns:
        if category != "raw_examples":
            all_patterns[category] = list(set(all_patterns[category]))

    all_patterns["raw_examples"] = raw_examples

    return all_patterns


def parse_code_structure(code: str, language: str) -> List[str]:
    """Identify structural patterns in code example.

    Detects:
    - async/await vs callbacks vs synchronous
    - class-based vs functional vs procedural
    - decorator usage patterns
    - context manager patterns

    Args:
        code: Source code string
        language: Programming language (python, typescript, etc.)

    Returns:
        List of detected structural patterns
    """
    if language.lower() in ("python", "py"):
        return _parse_python_structure(code)
    elif language.lower() in ("typescript", "ts", "javascript", "js"):
        return _parse_typescript_structure(code)
    else:
        return _parse_generic_structure(code)


def _parse_python_patterns(code: str) -> Dict[str, List[str]]:
    """Parse Python code using AST for accurate pattern detection."""
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
        return _parse_generic_patterns(code)

    # Code structure
    for node in ast.walk(tree):
        # Async patterns
        if isinstance(node, (ast.AsyncFunctionDef, ast.AsyncFor, ast.AsyncWith)):
            patterns["code_structure"].append("async/await")
        if isinstance(node, ast.Await):
            patterns["code_structure"].append("async/await")

        # Class-based
        if isinstance(node, ast.ClassDef):
            patterns["code_structure"].append("class-based")

        # Function-based
        if isinstance(node, ast.FunctionDef):
            if not any(isinstance(p, ast.ClassDef) for p in ast.walk(tree)):
                patterns["code_structure"].append("functional")

        # Decorators
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.decorator_list:
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name):
                    if dec.id in ("staticmethod", "classmethod", "property"):
                        patterns["code_structure"].append(f"decorator-{dec.id}")
                    elif dec.id == "dataclass":
                        patterns["code_structure"].append("dataclass")

        # Error handling
        if isinstance(node, ast.Try):
            patterns["error_handling"].append("try-except")
            if node.finalbody:
                patterns["error_handling"].append("try-except-finally")

        if isinstance(node, ast.If):
            # Detect guard clauses (early return)
            if isinstance(node.body[0] if node.body else None, ast.Return):
                patterns["error_handling"].append("early-return")

        # Naming conventions
        if isinstance(node, ast.FunctionDef):
            if "_" in node.name:
                patterns["naming_conventions"].append("snake_case")
            if node.name.startswith("_") and not node.name.startswith("__"):
                patterns["naming_conventions"].append("_private")

        if isinstance(node, ast.ClassDef):
            if node.name[0].isupper():
                patterns["naming_conventions"].append("PascalCase")

        # Test patterns
        if isinstance(node, ast.FunctionDef):
            if node.name.startswith("test_"):
                patterns["test_patterns"].append("pytest")
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == "pytest":
                    patterns["test_patterns"].append("pytest")

        # Import patterns
        if isinstance(node, ast.ImportFrom):
            if node.level > 0:
                patterns["import_patterns"].append("relative")
            else:
                patterns["import_patterns"].append("absolute")

    return patterns


def _parse_python_structure(code: str) -> List[str]:
    """Parse Python-specific code structure."""
    structure = []

    if "async " in code or "await " in code:
        structure.append("async/await")
    if re.search(r"^class\s+\w+", code, re.MULTILINE):
        structure.append("class-based")
    if re.search(r"^def\s+\w+", code, re.MULTILINE):
        structure.append("functional")
    if "@" in code:
        structure.append("decorators")
    if "with " in code:
        structure.append("context-manager")

    return structure


def _parse_typescript_patterns(code: str) -> Dict[str, List[str]]:
    """Parse TypeScript/JavaScript patterns using regex."""
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


def _parse_typescript_structure(code: str) -> List[str]:
    """Parse TypeScript-specific code structure."""
    structure = []

    if "async " in code or "await " in code:
        structure.append("async/await")
    if ".then(" in code:
        structure.append("promises")
    if re.search(r"\bclass\s+\w+", code):
        structure.append("class-based")
    if "=>" in code or re.search(r"\bfunction\s+\w+", code):
        structure.append("functional")

    return structure


def _parse_generic_patterns(code: str) -> Dict[str, List[str]]:
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


def _parse_generic_structure(code: str) -> List[str]:
    """Generic structure parsing for unknown languages."""
    structure = []

    if "async" in code.lower():
        structure.append("async/await")
    if "class" in code.lower():
        structure.append("class-based")
    if "function" in code.lower() or "def " in code:
        structure.append("functional")

    return structure
