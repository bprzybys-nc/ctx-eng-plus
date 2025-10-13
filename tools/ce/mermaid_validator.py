"""Mermaid diagram validator with auto-fix for unquoted special characters."""

import re
from pathlib import Path
from typing import Dict, Any, List, Tuple


def validate_mermaid_diagrams(file_path: str, auto_fix: bool = False) -> Dict[str, Any]:
    r"""Validate mermaid diagrams in markdown file.

    Args:
        file_path: Path to markdown file
        auto_fix: If True, auto-fix issues by renaming nodes or adding quotes

    Returns:
        Dict with: success (bool), errors (List[str]), fixes_applied (List[str])

    Validation rules:
    1. Node text with special chars must be quoted or use simple node IDs
    2. Node IDs should be simple (A, B, C1, etc.) if text has special chars
    3. Text with <>[]{}()!?/\ should be in quotes or node renamed
    4. Style statements should always specify color for theme compatibility

    Auto-fix strategies:
    - Strategy 1: Rename nodes with special chars (A, B, C, D1, D2, etc.)
    - Strategy 2: Quote text if short and quotes not present
    - Strategy 3: Check style statements have color specified
    """
    content = Path(file_path).read_text()
    errors = []
    fixes_applied = []

    # Extract all mermaid blocks
    mermaid_blocks = re.findall(
        r'```mermaid\n(.*?)```',
        content,
        re.DOTALL
    )

    if not mermaid_blocks:
        return {
            "success": True,
            "errors": [],
            "fixes_applied": [],
            "diagrams_checked": 0
        }

    for i, block in enumerate(mermaid_blocks):
        block_errors, block_fixes = _validate_mermaid_block(block, i + 1)
        errors.extend(block_errors)

        if auto_fix and block_fixes:
            # Apply fixes to content
            fixed_block = _apply_fixes_to_block(block, block_fixes)
            content = content.replace(f'```mermaid\n{block}```', f'```mermaid\n{fixed_block}```')
            fixes_applied.extend([f"Diagram {i+1}: {fix}" for fix in block_fixes])

    # Write back if fixes applied
    if auto_fix and fixes_applied:
        Path(file_path).write_text(content)

    return {
        "success": len(errors) == 0 or (auto_fix and len(fixes_applied) > 0),
        "errors": errors,
        "fixes_applied": fixes_applied,
        "diagrams_checked": len(mermaid_blocks)
    }


def _validate_mermaid_block(block: str, diagram_num: int) -> Tuple[List[str], List[str]]:
    r"""Validate single mermaid block.

    Returns:
        (errors, fix_suggestions) tuple
    """
    errors = []
    fixes = []

    # Check 1: Node definitions with special chars but no quotes
    # Pattern: NodeID[Text with special chars] or NodeID{Text with special chars}
    node_pattern = r'([A-Z0-9]+)[\[\{]([^\]\}]+)[\]\}]'
    nodes = re.findall(node_pattern, block)

    for node_id, node_text in nodes:
        if _has_unquoted_special_chars(node_text):
            errors.append(
                f"Diagram {diagram_num}: Node '{node_id}' has unquoted special chars in text: '{node_text}'"
            )
            fixes.append(f"Rename node '{node_id}' or quote text '{node_text}'")

    # Check 2: Style statements missing color specification
    style_pattern = r'style\s+([A-Z0-9]+)\s+fill:(#[0-9a-fA-F]{6}|#[0-9a-fA-F]{3})(?!.*color:)'
    styles_missing_color = re.findall(style_pattern, block)

    for node_id in styles_missing_color:
        errors.append(
            f"Diagram {diagram_num}: Style for node '{node_id}' missing color specification"
        )
        fixes.append(f"Add color:#000 or color:#fff to style {node_id}")

    # Check 3: Line breaks in node text without <br/> tag
    linebreak_pattern = r'[\[\{]([^\]\}]*\n[^\]\}]*)[\]\}]'
    linebreaks = re.findall(linebreak_pattern, block)

    for text in linebreaks:
        if '<br/>' not in text:
            errors.append(
                f"Diagram {diagram_num}: Multiline text without <br/> tag: '{text[:50]}...'"
            )
            fixes.append("Replace newlines with <br/> in node text")

    return errors, fixes


def _has_unquoted_special_chars(text: str) -> bool:
    """Check if text has special chars that need quoting.

    Special chars that ACTUALLY break mermaid rendering:
    - Parentheses: () - used for node shape syntax
    - Brackets: [] - used for node shape syntax
    - Curly braces: {} - used for node shape syntax
    - Pipes: | - used for subgraph syntax
    - Unbalanced quotes: "' - break parsing

    Characters that are SAFE in mermaid node text:
    - Colons: : - commonly used, safe
    - Question marks: ? - safe
    - Exclamation marks: ! - safe
    - Slashes: / \\ - safe
    - HTML tags: <br/>, <sub>, <sup> - explicitly allowed

    Note: HTML tags like <br/> are allowed unquoted in mermaid.
    """
    # If already quoted, it's fine
    if (text.startswith('"') and text.endswith('"')) or \
       (text.startswith("'") and text.endswith("'")):
        return False

    # Exclude HTML tags from special char check
    # HTML tags like <br/>, <sub>, <sup> are valid mermaid syntax
    text_without_html = re.sub(r'<[^>]+>', '', text)

    # Only check for truly problematic chars that break mermaid syntax
    # Removed: : ? ! / \\ (these are safe in mermaid node text)
    special_chars = r'[\[\]\{\}\(\)\|\'"]'
    return bool(re.search(special_chars, text_without_html))


def _apply_fixes_to_block(block: str, fixes: List[str]) -> str:
    """Apply fixes to mermaid block.

    Fix strategies:
    1. Rename nodes with special chars to simple IDs
    2. Add color to style statements
    3. Convert newlines to <br/> in node text
    """
    fixed_block = block

    # Fix 1: Rename problematic nodes
    node_pattern = r'([A-Z0-9]+)[\[\{]([^\]\}]+)[\]\}]'
    nodes = re.findall(node_pattern, fixed_block)
    node_mapping = {}  # old_id -> new_id
    next_id = 1

    for node_id, node_text in nodes:
        if _has_unquoted_special_chars(node_text):
            # Generate new simple ID
            new_id = f"N{next_id}"
            next_id += 1
            node_mapping[node_id] = new_id

            # Replace all occurrences of old node ID
            # Pattern: node_id at word boundary (not part of another word)
            fixed_block = re.sub(
                rf'\b{node_id}\b',
                new_id,
                fixed_block
            )

    # Fix 2: Add color to style statements missing it
    style_pattern = r'(style\s+[A-Z0-9]+\s+fill:#[0-9a-fA-F]{3,6})(?!.*color:)'

    def add_color(match):
        style_stmt = match.group(1)
        # Determine text color based on background lightness
        fill_match = re.search(r'fill:(#[0-9a-fA-F]{3,6})', style_stmt)
        if fill_match:
            bg_color = fill_match.group(1)
            text_color = _determine_text_color(bg_color)
            return f"{style_stmt},color:{text_color}"
        return style_stmt

    fixed_block = re.sub(style_pattern, add_color, fixed_block)

    # Fix 3: Convert multiline text to <br/>
    def fix_linebreaks(match):
        bracket_type = match.group(1)
        close_bracket = ']' if bracket_type == '[' else '}'
        content = match.group(2)
        fixed_content = content.replace('\n', '<br/>')
        return f"{bracket_type}{fixed_content}{close_bracket}"

    fixed_block = re.sub(
        r'([\[\{])([^\]\}]*\n[^\]\}]*)([\]\}])',
        fix_linebreaks,
        fixed_block
    )

    return fixed_block


def _determine_text_color(bg_color: str) -> str:
    """Determine text color (#000 or #fff) based on background lightness.

    Uses relative luminance formula:
    L = 0.2126 * R + 0.7152 * G + 0.0722 * B

    Args:
        bg_color: Hex color (#RGB or #RRGGBB)

    Returns:
        '#000' for light backgrounds, '#fff' for dark backgrounds
    """
    # Expand shorthand hex (#RGB -> #RRGGBB)
    if len(bg_color) == 4:  # #RGB
        bg_color = f"#{bg_color[1]*2}{bg_color[2]*2}{bg_color[3]*2}"

    # Extract RGB components
    r = int(bg_color[1:3], 16) / 255.0
    g = int(bg_color[3:5], 16) / 255.0
    b = int(bg_color[5:7], 16) / 255.0

    # Apply sRGB gamma correction
    def gamma_correct(c):
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r = gamma_correct(r)
    g = gamma_correct(g)
    b = gamma_correct(b)

    # Calculate relative luminance
    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b

    # Return black for light backgrounds, white for dark
    return '#000' if luminance > 0.5 else '#fff'


def lint_all_markdown_mermaid(directory: str = ".", auto_fix: bool = False) -> Dict[str, Any]:
    """Lint mermaid diagrams in all markdown files.

    Args:
        directory: Root directory to search (default: current)
        auto_fix: Apply fixes automatically

    Returns:
        Dict with aggregated results
    """
    md_files = list(Path(directory).rglob("*.md"))
    all_errors = []
    all_fixes = []
    files_with_issues = []
    total_diagrams = 0

    for md_file in md_files:
        result = validate_mermaid_diagrams(str(md_file), auto_fix=auto_fix)
        total_diagrams += result["diagrams_checked"]

        if result["errors"]:
            files_with_issues.append(str(md_file))
            all_errors.extend([f"{md_file}: {err}" for err in result["errors"]])

        if result["fixes_applied"]:
            all_fixes.extend([f"{md_file}: {fix}" for fix in result["fixes_applied"]])

    return {
        "success": len(all_errors) == 0 or (auto_fix and len(all_fixes) > 0),
        "files_checked": len(md_files),
        "diagrams_checked": total_diagrams,
        "files_with_issues": len(files_with_issues),
        "errors": all_errors,
        "fixes_applied": all_fixes
    }


if __name__ == "__main__":
    import sys

    # CLI usage: python mermaid_validator.py [--fix] [path]
    auto_fix = "--fix" in sys.argv
    path = sys.argv[-1] if len(sys.argv) > 1 and not sys.argv[-1].startswith("--") else "."

    result = lint_all_markdown_mermaid(path, auto_fix=auto_fix)

    print(f"\n{'='*80}")
    print(f"Mermaid Diagram Validation")
    print(f"{'='*80}")
    print(f"Files checked: {result['files_checked']}")
    print(f"Diagrams checked: {result['diagrams_checked']}")
    print(f"Files with issues: {result['files_with_issues']}")

    if result['errors']:
        print(f"\n{'='*80}")
        print("ERRORS:")
        print(f"{'='*80}")
        for error in result['errors']:
            print(f"❌ {error}")

    if result['fixes_applied']:
        print(f"\n{'='*80}")
        print("FIXES APPLIED:")
        print(f"{'='*80}")
        for fix in result['fixes_applied']:
            print(f"✅ {fix}")

    print(f"\n{'='*80}")
    print(f"Result: {'✅ PASS' if result['success'] else '❌ FAIL'}")
    print(f"{'='*80}\n")

    sys.exit(0 if result['success'] else 1)
