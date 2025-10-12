"""PRP generation from INITIAL.md.

This module automates PRP (Product Requirements Prompt) generation by:
1. Parsing INITIAL.md structure (FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS)
2. Orchestrating MCP tools (Serena, Context7, Sequential Thinking) for research
3. Synthesizing comprehensive PRP with all 6 sections

Usage:
    from ce.generate import generate_prp
    result = generate_prp("feature-requests/auth/INITIAL.md")
"""

import re
import logging
from pathlib import Path
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Section markers for INITIAL.md parsing
SECTION_MARKERS = {
    "feature": r"^##\s*FEATURE\s*$",
    "examples": r"^##\s*EXAMPLES\s*$",
    "documentation": r"^##\s*DOCUMENTATION\s*$",
    "other": r"^##\s*OTHER\s+CONSIDERATIONS\s*$"
}


def parse_initial_md(filepath: str) -> Dict[str, Any]:
    """Parse INITIAL.md into structured sections.

    Args:
        filepath: Path to INITIAL.md file

    Returns:
        {
            "feature_name": "User Authentication System",
            "feature": "Build user auth with JWT tokens...",
            "examples": [
                {"type": "inline", "language": "python", "code": "..."},
                {"type": "file_ref", "file": "src/auth.py", "lines": "42-67"}
            ],
            "documentation": [
                {"title": "JWT Guide", "url": "https://...", "type": "link"},
                {"title": "pytest", "url": "", "type": "library"}
            ],
            "other_considerations": "Security: Hash passwords with bcrypt...",
            "raw_content": "<full file content>"
        }

    Raises:
        FileNotFoundError: If INITIAL.md doesn't exist
        ValueError: If required sections missing (FEATURE, EXAMPLES)

    Process:
        1. Read file content
        2. Extract feature name from first heading
        3. Split content by section markers (## FEATURE, ## EXAMPLES, etc.)
        4. Parse EXAMPLES for code block references
        5. Parse DOCUMENTATION for URL links
        6. Validate FEATURE and EXAMPLES present (minimum required)
    """
    # Check file exists
    file_path = Path(filepath)
    if not file_path.exists():
        raise FileNotFoundError(
            f"INITIAL.md not found: {filepath}\n"
            f"🔧 Troubleshooting: Verify file path is correct and file exists"
        )

    # Read content
    content = file_path.read_text(encoding="utf-8")

    # Extract feature name from first heading (# Feature: <name>)
    feature_name_match = re.search(r"^#\s+Feature:\s+(.+)$", content, re.MULTILINE)
    if not feature_name_match:
        raise ValueError(
            f"Feature name not found in {filepath}\n"
            f"🔧 Troubleshooting: First line must be '# Feature: <name>'"
        )
    feature_name = feature_name_match.group(1).strip()

    # Split content by section markers
    sections = {}
    lines = content.split("\n")
    current_section = None
    section_content = []

    for line in lines:
        # Check if line is a section marker
        matched_section = None
        for section_key, pattern in SECTION_MARKERS.items():
            if re.match(pattern, line.strip()):
                # Save previous section if exists
                if current_section and section_content:
                    sections[current_section] = "\n".join(section_content).strip()
                    section_content = []
                current_section = section_key
                matched_section = section_key
                break

        # If not a section marker and we're in a section, accumulate content
        if not matched_section and current_section:
            section_content.append(line)

    # Save last section
    if current_section and section_content:
        sections[current_section] = "\n".join(section_content).strip()

    # Validate required sections
    if "feature" not in sections:
        raise ValueError(
            f"Required FEATURE section missing in {filepath}\n"
            f"🔧 Troubleshooting: Add '## FEATURE' section with feature description"
        )
    if "examples" not in sections:
        raise ValueError(
            f"Required EXAMPLES section missing in {filepath}\n"
            f"🔧 Troubleshooting: Add '## EXAMPLES' section with code examples"
        )

    # Parse subsections
    return {
        "feature_name": feature_name,
        "feature": sections.get("feature", ""),
        "examples": extract_code_examples(sections.get("examples", "")),
        "documentation": extract_documentation_links(sections.get("documentation", "")),
        "other_considerations": sections.get("other", ""),
        "raw_content": content
    }


def extract_code_examples(examples_text: str) -> List[Dict[str, Any]]:
    """Extract code examples from EXAMPLES section.

    Patterns supported:
        - Inline code blocks with language tags
        - File references (e.g., "See src/auth.py:42-67")
        - Natural language descriptions

    Returns:
        [
            {"type": "inline", "language": "python", "code": "..."},
            {"type": "file_ref", "file": "src/auth.py", "lines": "42-67"},
            {"type": "description", "text": "Uses async/await pattern"}
        ]
    """
    if not examples_text:
        return []

    examples = []

    # Pattern 1: Inline code blocks with language tag
    # Matches: ```python\ncode\n```
    code_block_pattern = r"```(\w+)\n(.*?)```"
    for match in re.finditer(code_block_pattern, examples_text, re.DOTALL):
        language = match.group(1)
        code = match.group(2).strip()
        examples.append({
            "type": "inline",
            "language": language,
            "code": code
        })

    # Pattern 2: File references
    # Matches: "See src/auth.py:42-67", "src/auth.py lines 42-67", etc.
    file_ref_pattern = r"(?:See\s+)?([a-zA-Z0-9_/.-]+\.py)(?::|\s+lines?\s+)(\d+-\d+)"
    for match in re.finditer(file_ref_pattern, examples_text):
        file_path = match.group(1)
        line_range = match.group(2)
        examples.append({
            "type": "file_ref",
            "file": file_path,
            "lines": line_range
        })

    # Pattern 3: Natural language descriptions (paragraphs without code/file refs)
    # Extract paragraphs not containing code blocks or file references
    # Remove code blocks and file references from text
    text_without_code = re.sub(code_block_pattern, "", examples_text, flags=re.DOTALL)
    text_without_refs = re.sub(file_ref_pattern, "", text_without_code)

    # Split into paragraphs and filter non-empty
    paragraphs = [p.strip() for p in text_without_refs.split("\n\n") if p.strip()]
    for paragraph in paragraphs:
        # Skip very short paragraphs (likely headers or fragments)
        if len(paragraph) > 20:
            examples.append({
                "type": "description",
                "text": paragraph
            })

    return examples


def extract_documentation_links(docs_text: str) -> List[Dict[str, str]]:
    """Extract documentation URLs from DOCUMENTATION section.

    Patterns supported:
        - Markdown links: [Title](url)
        - Plain URLs: https://...
        - Library names: "FastAPI", "pytest"

    Returns:
        [
            {"title": "FastAPI Docs", "url": "https://...", "type": "link"},
            {"title": "pytest", "url": "", "type": "library"}
        ]
    """
    if not docs_text:
        return []

    doc_links = []

    # Pattern 1: Markdown links [Title](url)
    markdown_link_pattern = r"\[([^\]]+)\]\(([^\)]+)\)"
    for match in re.finditer(markdown_link_pattern, docs_text):
        title = match.group(1).strip()
        url = match.group(2).strip()
        doc_links.append({
            "title": title,
            "url": url,
            "type": "link"
        })

    # Pattern 2: Plain URLs (https://... or http://...)
    plain_url_pattern = r"(https?://[^\s\)]+)"
    # Only extract URLs not already captured by markdown links
    text_without_markdown = re.sub(markdown_link_pattern, "", docs_text)
    for match in re.finditer(plain_url_pattern, text_without_markdown):
        url = match.group(1).strip()
        # Use domain as title
        domain = url.split("/")[2]
        doc_links.append({
            "title": domain,
            "url": url,
            "type": "link"
        })

    # Pattern 3: Library names (words in quotes or standalone)
    # Matches: "FastAPI", "pytest", FastAPI, pytest
    # This is heuristic - captures quoted words or capitalized words likely to be library names
    library_pattern = r"[\"']([A-Za-z0-9_-]+)[\"']|(?:^|\s)([A-Z][a-zA-Z0-9_-]+)(?:\s|$)"
    text_without_urls = re.sub(plain_url_pattern, "", text_without_markdown)
    for match in re.finditer(library_pattern, text_without_urls):
        library_name = match.group(1) or match.group(2)
        if library_name:
            # Only add if not already in doc_links
            if not any(lib["title"] == library_name for lib in doc_links):
                doc_links.append({
                    "title": library_name,
                    "url": "",
                    "type": "library"
                })

    return doc_links
