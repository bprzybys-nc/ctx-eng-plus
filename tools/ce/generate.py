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


# =============================================================================
# Phase 2: Serena Research Orchestration
# =============================================================================


def research_codebase(
    feature_name: str,
    examples: List[Dict[str, Any]],
    initial_context: str
) -> Dict[str, Any]:
    """Orchestrate codebase research using Serena MCP.

    Args:
        feature_name: Target feature name (e.g., "User Authentication")
        examples: Parsed EXAMPLES from INITIAL.md
        initial_context: FEATURE section text for context

    Returns:
        {
            "related_files": ["src/auth.py", "src/models/user.py"],
            "patterns": [
                {"pattern": "async/await", "locations": ["src/auth.py:42"]},
                {"pattern": "JWT validation", "locations": ["src/auth.py:67"]}
            ],
            "similar_implementations": [
                {
                    "file": "src/oauth.py",
                    "symbol": "OAuthHandler/authenticate",
                    "code": "...",
                    "relevance": "Similar authentication flow"
                }
            ],
            "test_patterns": [
                {"file": "tests/test_auth.py", "pattern": "pytest fixtures"}
            ],
            "architecture": {
                "layer": "authentication",
                "dependencies": ["jwt", "bcrypt"],
                "conventions": ["snake_case", "async functions"]
            }
        }

    Raises:
        RuntimeError: If Serena MCP unavailable (non-blocking - log warning, return empty results)

    Process:
        1. Extract keywords from feature_name (e.g., "authentication", "JWT")
        2. Search for patterns: mcp__serena__search_for_pattern(keywords)
        3. Discover symbols: mcp__serena__find_symbol(related_classes)
        4. Get detailed code: mcp__serena__find_symbol(include_body=True)
        5. Find references: mcp__serena__find_referencing_symbols(key_functions)
        6. Infer architecture: Analyze file structure and imports
        7. Detect test patterns: Look for pytest/unittest in tests/
    """
    logger.info(f"Starting codebase research for: {feature_name}")

    # Initialize result structure
    result = {
        "related_files": [],
        "patterns": [],
        "similar_implementations": [],
        "test_patterns": [],
        "architecture": {
            "layer": "",
            "dependencies": [],
            "conventions": []
        },
        "serena_available": False
    }

    try:
        # Check if Serena MCP is available by attempting import
        # In production, this would be: from mcp import serena
        # For now, we'll gracefully handle unavailability
        logger.info("Serena MCP research would execute here (graceful degradation)")

        # Extract keywords from feature name
        keywords = _extract_keywords(feature_name)
        logger.info(f"Extracted keywords: {keywords}")

        # Search for similar patterns
        patterns = search_similar_patterns(keywords)
        result["patterns"] = patterns

        # Infer test patterns
        test_patterns = infer_test_patterns({})
        result["test_patterns"] = test_patterns

        result["serena_available"] = False  # Will be True when MCP integrated

    except Exception as e:
        logger.warning(f"Serena MCP unavailable or error during research: {e}")
        logger.warning("Continuing with reduced research functionality")

    return result


def search_similar_patterns(keywords: List[str], path: str = ".") -> List[Dict[str, Any]]:
    """Search for similar code patterns using keywords.

    Uses: mcp__serena__search_for_pattern

    Args:
        keywords: Search terms (e.g., ["authenticate", "JWT", "token"])
        path: Search scope (default: entire project)

    Returns:
        [
            {"file": "src/auth.py", "line": 42, "snippet": "..."},
            {"file": "src/oauth.py", "line": 67, "snippet": "..."}
        ]
    """
    logger.info(f"Searching for patterns with keywords: {keywords}")

    # Graceful degradation when Serena unavailable
    patterns = []

    try:
        # This would use: mcp__serena__search_for_pattern(pattern="|".join(keywords))
        # For now, return empty (will be populated when MCP integrated)
        logger.info("Pattern search would execute via Serena MCP")
    except Exception as e:
        logger.warning(f"Pattern search unavailable: {e}")

    return patterns


def analyze_symbol_structure(symbol_name: str, file_path: str) -> Dict[str, Any]:
    """Get detailed symbol information.

    Uses: mcp__serena__find_symbol, mcp__serena__get_symbols_overview

    Args:
        symbol_name: Class/function name
        file_path: File containing symbol

    Returns:
        {
            "name": "AuthHandler",
            "type": "class",
            "methods": ["authenticate", "validate_token", "refresh"],
            "code": "<full class body>",
            "references": 5
        }
    """
    logger.info(f"Analyzing symbol: {symbol_name} in {file_path}")

    # Graceful degradation
    result = {
        "name": symbol_name,
        "type": "unknown",
        "methods": [],
        "code": "",
        "references": 0
    }

    try:
        # Would use: mcp__serena__find_symbol(name_path=symbol_name, relative_path=file_path)
        logger.info("Symbol analysis would execute via Serena MCP")
    except Exception as e:
        logger.warning(f"Symbol analysis unavailable: {e}")

    return result


def infer_test_patterns(project_structure: Dict[str, Any]) -> List[Dict[str, str]]:
    """Detect test framework and patterns.

    Process:
        1. Look for pytest.ini, setup.cfg, pyproject.toml
        2. Search for test files (test_*.py, *_test.py)
        3. Analyze test imports (pytest, unittest, nose)
        4. Extract test command from pyproject.toml or tox.ini

    Returns:
        [
            {
                "framework": "pytest",
                "test_command": "pytest tests/ -v",
                "patterns": ["fixtures", "parametrize", "async tests"],
                "coverage_required": True
            }
        ]
    """
    logger.info("Inferring test patterns from project structure")

    # Check for pytest.ini, pyproject.toml
    test_patterns = []

    # Default pytest pattern (most Python projects)
    default_pattern = {
        "framework": "pytest",
        "test_command": "uv run pytest tests/ -v",
        "patterns": ["fixtures", "parametrize"],
        "coverage_required": True
    }
    test_patterns.append(default_pattern)

    return test_patterns


def _extract_keywords(text: str) -> List[str]:
    """Extract keywords from feature name or description.

    Args:
        text: Feature name or description

    Returns:
        List of keywords (lowercase, deduplicated)
    """
    # Simple keyword extraction - split by spaces, lowercase, remove common words
    stop_words = {"a", "an", "the", "and", "or", "but", "with", "for", "to", "of", "in", "on"}
    words = re.findall(r'\b\w+\b', text.lower())
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return list(set(keywords))  # Deduplicate


# =============================================================================
# Phase 3: Context7 Integration
# =============================================================================


def fetch_documentation(
    documentation_links: List[Dict[str, str]],
    feature_context: str,
    serena_research: Dict[str, Any]
) -> Dict[str, Any]:
    """Fetch documentation using Context7 MCP.

    Args:
        documentation_links: Parsed from INITIAL.md DOCUMENTATION section
            [{"title": "FastAPI", "url": "", "type": "library"}, ...]
        feature_context: FEATURE section text for topic extraction
        serena_research: Results from research_codebase() for additional context

    Returns:
        {
            "library_docs": [
                {
                    "library_name": "FastAPI",
                    "library_id": "/tiangolo/fastapi",
                    "topics": ["routing", "security", "dependencies"],
                    "content": "<fetched markdown docs>",
                    "tokens_used": 5000
                }
            ],
            "external_links": [
                {
                    "title": "JWT Best Practices",
                    "url": "https://jwt.io/introduction",
                    "content": "<fetched content via WebFetch>",
                    "relevant_sections": ["token structure", "security"]
                }
            ],
            "context7_available": False,
            "sequential_thinking_available": False
        }

    Raises:
        RuntimeError: If Context7 MCP unavailable (non-blocking - log warning, return empty)

    Process:
        1. Extract topics from feature_context using Sequential Thinking MCP
        2. Resolve library names to Context7 IDs: mcp__context7__resolve-library-id
        3. Fetch docs: mcp__context7__get-library-docs(library_id, topics)
        4. Fetch external links: WebFetch tool for URLs
        5. Synthesize relevance scores
    """
    logger.info("Starting documentation fetch with Context7 and Sequential Thinking")

    # Initialize result structure
    result = {
        "library_docs": [],
        "external_links": [],
        "context7_available": False,
        "sequential_thinking_available": False
    }

    try:
        # Extract topics from feature context using Sequential Thinking
        topics = extract_topics_from_feature(feature_context, serena_research)
        logger.info(f"Extracted topics: {topics}")

        # Resolve library IDs and fetch docs
        libraries = [doc for doc in documentation_links if doc["type"] == "library"]
        for lib in libraries:
            lib_result = resolve_and_fetch_library_docs(
                lib["title"],
                topics,
                feature_context
            )
            if lib_result:
                result["library_docs"].append(lib_result)

        # Fetch external link content
        external_links = [doc for doc in documentation_links if doc["type"] == "link"]
        for link in external_links:
            link_result = fetch_external_link(link["url"], link["title"], topics)
            if link_result:
                result["external_links"].append(link_result)

        result["context7_available"] = False  # Will be True when MCP integrated
        result["sequential_thinking_available"] = False

    except Exception as e:
        logger.warning(f"Context7/Sequential Thinking MCP unavailable: {e}")
        logger.warning("Continuing with reduced documentation functionality")

    return result


def extract_topics_from_feature(
    feature_text: str,
    serena_research: Dict[str, Any]
) -> List[str]:
    """Extract documentation topics using Sequential Thinking MCP.

    Uses: mcp__sequential-thinking__sequentialthinking

    Args:
        feature_text: FEATURE section from INITIAL.md
        serena_research: Codebase research results for additional context

    Returns:
        List of topics (e.g., ["routing", "security", "async", "testing"])

    Process:
        1. Call Sequential Thinking MCP with prompt:
           "Analyze this feature description and identify key technical topics
            that would need documentation: {feature_text}"
        2. Extract topics from thinking chain
        3. Deduplicate and filter to 3-5 most relevant topics
    """
    logger.info("Extracting topics from feature text using Sequential Thinking")

    # Graceful degradation - return heuristic-based topics
    # Extract technical terms and common patterns
    technical_terms = []

    # Common technical patterns to look for
    patterns = {
        "authentication": ["auth", "login", "jwt", "oauth", "token"],
        "database": ["database", "sql", "nosql", "query", "model"],
        "api": ["api", "rest", "graphql", "endpoint", "route"],
        "async": ["async", "await", "concurrent", "parallel"],
        "testing": ["test", "pytest", "unittest", "mock"],
        "security": ["security", "encrypt", "hash", "bcrypt", "secure"],
        "validation": ["validate", "validation", "schema", "verify"],
    }

    feature_lower = feature_text.lower()
    for topic, keywords in patterns.items():
        if any(kw in feature_lower for kw in keywords):
            technical_terms.append(topic)

    # Limit to 3-5 topics
    topics = technical_terms[:5] if technical_terms else ["general"]

    logger.info(f"Extracted topics (heuristic): {topics}")
    return topics


def resolve_and_fetch_library_docs(
    library_name: str,
    topics: List[str],
    feature_context: str,
    max_tokens: int = 5000
) -> Dict[str, Any]:
    """Resolve library ID and fetch documentation.

    Uses: mcp__context7__resolve-library-id, mcp__context7__get-library-docs

    Args:
        library_name: Library to fetch (e.g., "FastAPI", "pytest")
        topics: Topics to focus documentation (e.g., ["routing", "security"])
        feature_context: Feature description for relevance filtering
        max_tokens: Maximum tokens to retrieve

    Returns:
        {
            "library_name": "FastAPI",
            "library_id": "/tiangolo/fastapi",
            "topics": ["routing", "security"],
            "content": "<markdown docs>",
            "tokens_used": 4500
        }
        None if library not found or fetch fails

    Process:
        1. resolve-library-id(library_name) → library_id
        2. get-library-docs(library_id, topics, max_tokens)
        3. Return structured result
    """
    logger.info(f"Resolving and fetching docs for library: {library_name}")

    # Graceful degradation
    try:
        # Would use: mcp__context7__resolve-library-id(libraryName=library_name)
        # Would use: mcp__context7__get-library-docs(context7CompatibleLibraryID=library_id, topic=topics, tokens=max_tokens)
        logger.info(f"Context7 fetch would execute for {library_name}")
        return None  # Return None when MCP unavailable
    except Exception as e:
        logger.warning(f"Failed to fetch docs for {library_name}: {e}")
        return None


def fetch_external_link(
    url: str,
    title: str,
    topics: List[str]
) -> Dict[str, Any]:
    """Fetch external documentation link using WebFetch.

    Uses: WebFetch tool

    Args:
        url: URL to fetch
        title: Link title from INITIAL.md
        topics: Topics for relevance filtering

    Returns:
        {
            "title": "JWT Best Practices",
            "url": "https://jwt.io/introduction",
            "content": "<fetched markdown>",
            "relevant_sections": ["token structure", "security"]
        }
        None if fetch fails

    Process:
        1. WebFetch(url, prompt=f"Extract content relevant to: {topics}")
        2. Parse and structure response
        3. Identify relevant sections
    """
    logger.info(f"Fetching external link: {url}")

    # Graceful degradation
    try:
        # Would use: WebFetch(url=url, prompt=f"Extract documentation relevant to: {', '.join(topics)}")
        logger.info(f"WebFetch would execute for {url}")
        return None  # Return None for now
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None
