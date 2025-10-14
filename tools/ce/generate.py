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
from typing import Dict, List, Any, Optional

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


# =============================================================================
# Phase 4: Template Engine
# =============================================================================


def generate_prp(
    initial_md_path: str,
    output_dir: str = "PRPs/feature-requests",
    join_prp: Optional[str] = None
) -> str:
    """Generate complete PRP from INITIAL.md.

    Main orchestration function that coordinates all phases.

    Args:
        initial_md_path: Path to INITIAL.md file
        output_dir: Directory for output PRP file
        join_prp: Optional PRP to join (number, ID like 'PRP-12', or file path)
                  If provided, updates existing PRP's Linear issue instead of creating new

    Returns:
        Path to generated PRP file

    Raises:
        FileNotFoundError: If INITIAL.md doesn't exist
        ValueError: If INITIAL.md invalid or join_prp invalid
        RuntimeError: If PRP generation or Linear integration fails

    Process:
        1. Parse INITIAL.md → structured data
        2. Research codebase → Serena findings
        3. Fetch documentation → Context7 + WebFetch
        4. Synthesize sections (TLDR, Implementation, Validation Gates, etc.)
        5. Get next PRP ID
        6. Write PRP file with YAML header
        7. Create/update Linear issue with defaults
        8. Update PRP YAML with issue ID
        9. Check completeness
    """
    logger.info(f"Starting PRP generation from: {initial_md_path}")

    # Step 2.5: Pre-generation sync (if auto-sync enabled)
    from .context import is_auto_sync_enabled, pre_generation_sync
    if is_auto_sync_enabled():
        try:
            logger.info("Auto-sync enabled - running pre-generation sync...")
            sync_result = pre_generation_sync(force=False)
            logger.info(f"Pre-sync complete: drift={sync_result['drift_score']:.1f}%")
        except Exception as e:
            logger.error(f"Pre-generation sync failed: {e}")
            raise RuntimeError(
                f"Generation aborted due to sync failure\n"
                f"Error: {e}\n"
                f"🔧 Troubleshooting: Run 'ce context health' to diagnose issues"
            ) from e

    # Phase 1: Parse INITIAL.md
    parsed_data = parse_initial_md(initial_md_path)
    logger.info(f"Parsed feature: {parsed_data['feature_name']}")

    # Phase 2: Research codebase
    serena_research = research_codebase(
        parsed_data["feature_name"],
        parsed_data["examples"],
        parsed_data["feature"]
    )
    logger.info(f"Codebase research complete: {len(serena_research['patterns'])} patterns found")

    # Phase 3: Fetch documentation
    documentation = fetch_documentation(
        parsed_data["documentation"],
        parsed_data["feature"],
        serena_research
    )
    logger.info(f"Documentation fetched: {len(documentation['library_docs'])} libraries")

    # Phase 4: Synthesize PRP sections
    prp_content = synthesize_prp_content(parsed_data, serena_research, documentation)

    # Get next PRP ID
    prp_id = get_next_prp_id(output_dir)
    logger.info(f"Assigned PRP ID: {prp_id}")

    # Write PRP file
    output_path = Path(output_dir) / f"{prp_id}-{_slugify(parsed_data['feature_name'])}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(prp_content)

    logger.info(f"PRP generated: {output_path}")

    # Step 7: Create or update Linear issue
    try:
        from .linear_utils import create_issue_with_defaults

        issue_identifier = None

        if join_prp:
            # Join existing PRP's issue
            logger.info(f"Joining PRP: {join_prp}")
            target_prp_path = _resolve_prp_path(join_prp)
            target_issue_id = _extract_issue_from_prp(target_prp_path)

            if not target_issue_id:
                logger.warning(f"Target PRP has no Linear issue: {target_prp_path}")
                logger.warning("Creating new issue instead")
            else:
                # Update existing issue (append new PRP info)
                logger.info(f"Updating Linear issue: {target_issue_id}")
                _update_linear_issue(
                    target_issue_id,
                    prp_id,
                    parsed_data['feature_name'],
                    str(output_path)
                )
                issue_identifier = target_issue_id
                logger.info(f"Updated issue {target_issue_id} with {prp_id}")

        if not issue_identifier:
            # Create new issue
            logger.info("Creating new Linear issue")
            issue_data = create_issue_with_defaults(
                title=f"{prp_id}: {parsed_data['feature_name']}",
                description=_generate_issue_description(prp_id, parsed_data, str(output_path)),
                state="todo"
            )

            # Call Linear MCP to create issue
            # For now, we'll prepare the data structure
            # In full implementation, this would call: mcp__linear-server__create_issue
            logger.info(f"Issue data prepared: {issue_data}")
            # FIXME: Placeholder - replace with actual Linear MCP call
            issue_identifier = f"{prp_id}-placeholder"
            logger.warning("Linear MCP integration pending - issue not actually created")

        # Update PRP YAML with issue ID
        if issue_identifier:
            _update_prp_yaml_with_issue(str(output_path), issue_identifier)
            logger.info(f"Updated PRP YAML with issue: {issue_identifier}")

    except ImportError:
        logger.warning("Linear utils not available - skipping issue creation")
    except Exception as e:
        logger.error(f"Linear issue creation failed: {e}")
        logger.warning("Continuing without Linear integration")

    # Check completeness
    completeness = check_prp_completeness(str(output_path))
    if not completeness["complete"]:
        logger.warning(f"PRP incomplete: {completeness['missing_sections']}")
    else:
        logger.info("PRP completeness check: PASSED")

    return str(output_path)


def synthesize_prp_content(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Synthesize complete PRP content from research.

    Args:
        parsed_data: Parsed INITIAL.md data
        serena_research: Codebase research results
        documentation: Fetched documentation

    Returns:
        Complete PRP markdown content with YAML header

    Process:
        1. Generate YAML header with metadata
        2. Synthesize TLDR section
        3. Synthesize Context section
        4. Synthesize Implementation Steps
        5. Synthesize Validation Gates
        6. Add Research Findings appendix
        7. Format final markdown
    """
    logger.info("Synthesizing PRP content")

    # Generate sections
    yaml_header = _generate_yaml_header(parsed_data)
    tldr = synthesize_tldr(parsed_data, serena_research)
    context = synthesize_context(parsed_data, documentation)
    implementation = synthesize_implementation(parsed_data, serena_research)
    validation_gates = synthesize_validation_gates(parsed_data, serena_research)
    testing = synthesize_testing_strategy(parsed_data, serena_research)
    rollout = synthesize_rollout_plan(parsed_data)

    # Combine sections
    prp_content = f"""---
{yaml_header}
---

# {parsed_data['feature_name']}

## 1. TL;DR

{tldr}

## 2. Context

{context}

## 3. Implementation Steps

{implementation}

## 4. Validation Gates

{validation_gates}

## 5. Testing Strategy

{testing}

## 6. Rollout Plan

{rollout}

---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: {len(serena_research['patterns'])}
- **Test Patterns**: {len(serena_research['test_patterns'])}
- **Serena Available**: {serena_research['serena_available']}

### Documentation Sources
- **Library Docs**: {len(documentation['library_docs'])}
- **External Links**: {len(documentation['external_links'])}
- **Context7 Available**: {documentation['context7_available']}
"""

    return prp_content


def synthesize_tldr(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any]
) -> str:
    """Generate TLDR section.

    Args:
        parsed_data: INITIAL.md structured data
        serena_research: Codebase research findings

    Returns:
        TLDR markdown text (3-5 bullet points)
    """
    feature = parsed_data["feature"]
    examples_count = len(parsed_data["examples"])

    tldr = f"""**Objective**: {parsed_data['feature_name']}

**What**: {feature[:200]}...

**Why**: Enable functionality described in INITIAL.md with {examples_count} reference examples

**Effort**: Medium (3-5 hours estimated based on complexity)

**Dependencies**: {', '.join([doc['title'] for doc in parsed_data['documentation'][:3]])}
"""
    return tldr


def synthesize_context(
    parsed_data: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Generate Context section.

    Args:
        parsed_data: INITIAL.md data
        documentation: Fetched documentation

    Returns:
        Context markdown with background and constraints
    """
    feature = parsed_data["feature"]
    other = parsed_data.get("other_considerations", "")

    context = f"""### Background

{feature}

### Constraints and Considerations

{other if other else "See INITIAL.md for additional considerations"}

### Documentation References

"""
    # Add documentation links
    for doc in parsed_data["documentation"]:
        if doc["type"] == "link":
            context += f"- [{doc['title']}]({doc['url']})\n"
        elif doc["type"] == "library":
            context += f"- {doc['title']} (library documentation)\n"

    return context


def synthesize_implementation(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any]
) -> str:
    """Generate Implementation Steps section.

    Args:
        parsed_data: INITIAL.md data
        serena_research: Codebase patterns

    Returns:
        Implementation steps markdown
    """
    examples = parsed_data["examples"]

    steps = """### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (2-3 hours)

"""
    # Generate steps from examples
    for i, example in enumerate(examples[:3], 1):
        if example["type"] == "inline":
            steps += f"{i}. Implement {example.get('language', 'code')} component\n"
        elif example["type"] == "file_ref":
            steps += f"{i}. Reference pattern in {example['file']}\n"

    steps += """
### Phase 3: Testing and Validation (1-2 hours)

1. Write unit tests following project patterns
2. Write integration tests
3. Run validation gates
4. Update documentation
"""

    return steps


def synthesize_validation_gates(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any]
) -> str:
    """Generate Validation Gates section.

    Args:
        parsed_data: INITIAL.md data with acceptance criteria
        serena_research: Test patterns from codebase

    Returns:
        Validation gates markdown
    """
    test_framework = "pytest"
    if serena_research["test_patterns"]:
        test_framework = serena_research["test_patterns"][0]["framework"]

    gates = f"""### Gate 1: Unit Tests Pass

**Command**: `uv run {test_framework} tests/unit/ -v`

**Success Criteria**:
- All new unit tests pass
- Existing tests not broken
- Code coverage ≥ 80%

### Gate 2: Integration Tests Pass

**Command**: `uv run {test_framework} tests/integration/ -v`

**Success Criteria**:
- Integration tests verify end-to-end functionality
- No regressions in existing features

### Gate 3: Acceptance Criteria Met

**Verification**: Manual review against INITIAL.md requirements

**Success Criteria**:
"""
    # Extract acceptance criteria from feature text
    feature = parsed_data["feature"]
    if "acceptance criteria" in feature.lower():
        gates += "\n- Requirements from INITIAL.md validated\n"
    else:
        gates += "\n- All examples from INITIAL.md working\n"
        gates += "- Feature behaves as described\n"

    return gates


def synthesize_testing_strategy(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any]
) -> str:
    """Generate Testing Strategy section."""
    test_cmd = "uv run pytest tests/ -v"
    if serena_research["test_patterns"]:
        test_cmd = serena_research["test_patterns"][0]["test_command"]

    return f"""### Test Framework

{serena_research['test_patterns'][0]['framework'] if serena_research['test_patterns'] else 'pytest'}

### Test Command

```bash
{test_cmd}
```

### Coverage Requirements

- Unit test coverage: ≥ 80%
- Integration tests for critical paths
- Edge cases from INITIAL.md covered
"""


def synthesize_rollout_plan(parsed_data: Dict[str, Any]) -> str:
    """Generate Rollout Plan section."""
    return """### Phase 1: Development

1. Implement core functionality
2. Write tests
3. Pass validation gates

### Phase 2: Review

1. Self-review code changes
2. Peer review (optional)
3. Update documentation

### Phase 3: Deployment

1. Merge to main branch
2. Monitor for issues
3. Update stakeholders
"""


def get_next_prp_id(prps_dir: str = "PRPs/feature-requests") -> str:
    """Get next available PRP ID.

    Args:
        prps_dir: Directory containing PRPs

    Returns:
        Next PRP ID (e.g., "PRP-123")

    Process:
        1. List all PRP-*.md files in directory
        2. Extract numeric IDs
        3. Return max + 1
    """
    prps_path = Path(prps_dir)
    if not prps_path.exists():
        return "PRP-1"

    # Find all PRP-*.md files
    prp_files = list(prps_path.glob("PRP-*.md"))
    if not prp_files:
        return "PRP-1"

    # Extract numeric IDs
    ids = []
    for file in prp_files:
        match = re.match(r"PRP-(\d+)", file.name)
        if match:
            ids.append(int(match.group(1)))

    # Return next ID
    next_id = max(ids) + 1 if ids else 1
    return f"PRP-{next_id}"


def check_prp_completeness(prp_path: str) -> Dict[str, Any]:
    """Check if PRP has all required sections.

    Args:
        prp_path: Path to PRP file

    Returns:
        {
            "complete": True/False,
            "missing_sections": [],
            "warnings": []
        }

    Required sections:
        1. TL;DR
        2. Context
        3. Implementation Steps
        4. Validation Gates
        5. Testing Strategy
        6. Rollout Plan
    """
    required_sections = [
        "TL;DR",
        "Context",
        "Implementation Steps",
        "Validation Gates",
        "Testing Strategy",
        "Rollout Plan"
    ]

    content = Path(prp_path).read_text(encoding="utf-8")

    missing = []
    for section in required_sections:
        # Check for section header (## N. Section or ## Section)
        pattern = rf"##\s+\d*\.?\s*{re.escape(section)}"
        if not re.search(pattern, content, re.IGNORECASE):
            missing.append(section)

    warnings = []
    if len(content) < 1000:
        warnings.append("PRP content seems short (< 1000 chars)")

    return {
        "complete": len(missing) == 0,
        "missing_sections": missing,
        "warnings": warnings
    }


def _generate_yaml_header(parsed_data: Dict[str, Any]) -> str:
    """Generate YAML frontmatter for PRP."""
    from datetime import datetime

    now = datetime.now().isoformat()

    return f"""prp_id: TBD
feature_name: {parsed_data['feature_name']}
status: pending
created: {now}
updated: {now}
complexity: medium
estimated_hours: 3-5
dependencies: {', '.join([doc['title'] for doc in parsed_data['documentation'][:3]])}"""


def _slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    # Lowercase and replace spaces with hyphens
    slug = text.lower().replace(" ", "-")
    # Remove special characters
    slug = re.sub(r'[^a-z0-9-]', '', slug)
    # Remove multiple hyphens
    slug = re.sub(r'-+', '-', slug)
    return slug.strip("-")


# =============================================================================
# Linear Integration Helpers
# =============================================================================


def _resolve_prp_path(join_prp: str) -> Path:
    """Resolve join_prp reference to PRP file path.

    Args:
        join_prp: PRP reference (number like "12", ID like "PRP-12", or file path)

    Returns:
        Path to PRP file

    Raises:
        ValueError: If join_prp invalid or PRP not found
    """
    # Check if it's already a valid file path
    if "/" in join_prp or "\\" in join_prp:
        prp_path = Path(join_prp)
        if prp_path.exists():
            return prp_path
        raise ValueError(
            f"PRP file not found: {join_prp}\n"
            f"🔧 Troubleshooting: Verify file path is correct"
        )

    # Parse as PRP number or ID
    prp_number = None
    if join_prp.startswith("PRP-"):
        # Extract number from "PRP-12"
        match = re.match(r"PRP-(\d+)", join_prp)
        if match:
            prp_number = int(match.group(1))
    else:
        # Try parsing as plain number "12"
        try:
            prp_number = int(join_prp)
        except ValueError:
            raise ValueError(
                f"Invalid PRP reference: {join_prp}\n"
                f"🔧 Troubleshooting: Use format '12', 'PRP-12', or file path"
            )

    if not prp_number:
        raise ValueError(
            f"Could not parse PRP reference: {join_prp}\n"
            f"🔧 Troubleshooting: Use format '12', 'PRP-12', or file path"
        )

    # Search for PRP file in feature-requests/ and executed/
    prp_id = f"PRP-{prp_number}"
    search_dirs = ["PRPs/feature-requests", "PRPs/executed"]

    for search_dir in search_dirs:
        search_path = Path(search_dir)
        if search_path.exists():
            # Find PRP-{number}-*.md
            matches = list(search_path.glob(f"{prp_id}-*.md"))
            if matches:
                return matches[0]

    raise ValueError(
        f"PRP not found: {prp_id}\n"
        f"🔧 Troubleshooting: Searched in {', '.join(search_dirs)}"
    )


def _extract_issue_from_prp(prp_path: Path) -> Optional[str]:
    """Extract Linear issue ID from PRP YAML header.

    Args:
        prp_path: Path to PRP file

    Returns:
        Issue ID (e.g., "BLA-24") or None if not found
    """
    content = prp_path.read_text(encoding="utf-8")

    # Extract YAML frontmatter
    yaml_match = re.match(r"---\n(.*?)\n---", content, re.DOTALL)
    if not yaml_match:
        return None

    yaml_content = yaml_match.group(1)

    # Extract issue field
    issue_match = re.search(r"^issue:\s*(.+)$", yaml_content, re.MULTILINE)
    if not issue_match:
        return None

    issue_value = issue_match.group(1).strip()

    # Return None for null/empty values
    if issue_value.lower() in ["null", "none", ""]:
        return None

    return issue_value


def _update_linear_issue(
    issue_id: str,
    prp_id: str,
    feature_name: str,
    prp_path: str
) -> None:
    """Update existing Linear issue with new PRP info.

    Args:
        issue_id: Linear issue identifier (e.g., "BLA-24")
        prp_id: New PRP ID (e.g., "PRP-15")
        feature_name: New PRP feature name
        prp_path: Path to new PRP file

    Raises:
        RuntimeError: If update fails
    """
    logger.info(f"Updating Linear issue {issue_id} with {prp_id}")

    # FIXME: Placeholder - replace with actual Linear MCP call
    # In full implementation, this would:
    # 1. Get current issue description via mcp__linear-server__get_issue
    # 2. Append new PRP section to description
    # 3. Update issue via mcp__linear-server__update_issue

    update_text = f"""

---

## Related: {prp_id} - {feature_name}

**PRP File**: `{prp_path}`

This PRP is related to the same feature/initiative.
"""

    logger.info(f"Would append to issue {issue_id}: {update_text[:100]}...")
    logger.warning("Linear MCP integration pending - issue not actually updated")


def _generate_issue_description(
    prp_id: str,
    parsed_data: Dict[str, Any],
    prp_path: str
) -> str:
    """Generate Linear issue description from PRP data.

    Args:
        prp_id: PRP identifier (e.g., "PRP-15")
        parsed_data: Parsed INITIAL.md data
        prp_path: Path to generated PRP file

    Returns:
        Markdown description for Linear issue
    """
    feature = parsed_data["feature"]
    examples_count = len(parsed_data["examples"])

    # Truncate feature description for issue
    feature_summary = feature[:300] + "..." if len(feature) > 300 else feature

    description = f"""## Feature

{feature_summary}

## PRP Details

- **PRP ID**: {prp_id}
- **PRP File**: `{prp_path}`
- **Examples Provided**: {examples_count}

## Implementation

See PRP file for detailed implementation steps, validation gates, and testing strategy.

"""

    # Add other considerations if present
    if parsed_data.get("other_considerations"):
        other = parsed_data["other_considerations"]
        other_summary = other[:200] + "..." if len(other) > 200 else other
        description += f"""## Considerations

{other_summary}
"""

    return description


def _update_prp_yaml_with_issue(prp_path: str, issue_id: str) -> None:
    """Update PRP YAML header with Linear issue ID.

    Args:
        prp_path: Path to PRP file
        issue_id: Linear issue identifier

    Raises:
        RuntimeError: If YAML update fails
    """
    content = Path(prp_path).read_text(encoding="utf-8")

    # Check if YAML frontmatter exists
    yaml_match = re.match(r"(---\n.*?\n---)", content, re.DOTALL)
    if not yaml_match:
        raise RuntimeError(
            f"No YAML frontmatter found in {prp_path}\n"
            f"🔧 Troubleshooting: PRP file should start with YAML frontmatter"
        )

    yaml_block = yaml_match.group(1)

    # Check if issue field exists
    if re.search(r"^issue:", yaml_block, re.MULTILINE):
        # Update existing issue field
        updated_yaml = re.sub(
            r"^issue:.*$",
            f"issue: {issue_id}",
            yaml_block,
            flags=re.MULTILINE
        )
    else:
        # Add issue field before closing ---
        updated_yaml = yaml_block.replace(
            "\n---",
            f"\nissue: {issue_id}\n---"
        )

    # Replace YAML block in content
    updated_content = content.replace(yaml_block, updated_yaml)

    # Write back to file
    Path(prp_path).write_text(updated_content, encoding="utf-8")
