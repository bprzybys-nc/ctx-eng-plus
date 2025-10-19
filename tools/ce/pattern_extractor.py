"""Pattern extraction from PRP EXAMPLES sections for L4 validation.

This module extracts semantic code patterns from PRP markdown files to enable
architectural drift detection. Uses shared code_analyzer module for actual
pattern detection logic.
"""

import re
from typing import Dict, List, Any
from pathlib import Path

from .code_analyzer import analyze_code_patterns


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
        raise FileNotFoundError(
            f"PRP file not found: {prp_path}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Verify file path is correct\n"
            f"   - Check if file was moved or renamed\n"
            f"   - Use: ls {prp_path_obj.parent} to list directory"
        )

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

        # Use shared code analyzer
        patterns = analyze_code_patterns(code, language)

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
    # Use shared code analyzer and extract just code_structure
    patterns = analyze_code_patterns(code, language)
    return patterns.get("code_structure", [])



