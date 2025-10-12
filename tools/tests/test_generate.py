"""Tests for PRP generation from INITIAL.md."""
import pytest
import re
from pathlib import Path
from ce.generate import (
    parse_initial_md,
    extract_code_examples,
    extract_documentation_links,
    research_codebase,
    infer_test_patterns,
    _extract_keywords,
    fetch_documentation,
    extract_topics_from_feature,
    SECTION_MARKERS,
)


# Fixtures path
FIXTURES_DIR = Path(__file__).parent / "fixtures"
SAMPLE_INITIAL = FIXTURES_DIR / "sample_initial.md"


def test_parse_initial_md_complete():
    """Test parsing complete INITIAL.md with all sections."""
    result = parse_initial_md(str(SAMPLE_INITIAL))

    # Feature name
    assert result["feature_name"] == "User Authentication System"

    # Feature section
    assert "feature" in result
    assert "JWT-based user authentication" in result["feature"]

    # Examples
    assert len(result["examples"]) >= 1

    # Documentation
    assert len(result["documentation"]) >= 1

    # Raw content
    assert len(result["raw_content"]) > 100


# =============================================================================
# Phase 2: Serena Research Orchestration Tests
# =============================================================================


def test_extract_keywords():
    """Test keyword extraction with stop word filtering."""
    # Test basic extraction
    keywords = _extract_keywords("User Authentication System")
    assert "user" in keywords
    assert "authentication" in keywords
    assert "system" in keywords

    # Test stop word filtering
    keywords = _extract_keywords("Build a new authentication with JWT tokens")
    assert "build" in keywords
    assert "authentication" in keywords
    assert "jwt" in keywords
    assert "tokens" in keywords
    # Stop words should be filtered
    assert "a" not in keywords
    assert "with" not in keywords

    # Test deduplication
    keywords = _extract_keywords("auth auth authentication")
    assert keywords.count("auth") == 1
    assert "authentication" in keywords


def test_infer_test_patterns():
    """Test pytest pattern detection."""
    patterns = infer_test_patterns({})

    # Should return default pytest configuration
    assert len(patterns) == 1
    pattern = patterns[0]

    assert pattern["framework"] == "pytest"
    assert "uv run pytest" in pattern["test_command"]
    assert "fixtures" in pattern["patterns"]
    assert "parametrize" in pattern["patterns"]
    assert pattern["coverage_required"] is True


def test_research_codebase():
    """Test codebase research orchestration."""
    feature_name = "User Authentication System"
    examples = [
        {"type": "inline", "language": "python", "code": "def auth(): pass"}
    ]
    initial_context = "Build JWT-based authentication"

    result = research_codebase(feature_name, examples, initial_context)

    # Verify structure
    assert "related_files" in result
    assert "patterns" in result
    assert "similar_implementations" in result
    assert "test_patterns" in result
    assert "architecture" in result
    assert "serena_available" in result

    # Verify types
    assert isinstance(result["related_files"], list)
    assert isinstance(result["patterns"], list)
    assert isinstance(result["similar_implementations"], list)
    assert isinstance(result["test_patterns"], list)
    assert isinstance(result["architecture"], dict)

    # Verify test patterns populated
    assert len(result["test_patterns"]) > 0
    assert result["test_patterns"][0]["framework"] == "pytest"

    # Serena not available yet
    assert result["serena_available"] is False


# =============================================================================
# Phase 3: Context7 Integration Tests
# =============================================================================


def test_extract_topics_from_feature():
    """Test topic extraction from feature text."""
    feature_text = """
    Build a JWT-based user authentication system with:
    - User registration with email/password
    - Login with JWT token generation
    - Async/await for non-blocking operations
    - pytest for testing
    """

    serena_research = {}  # Empty for now

    topics = extract_topics_from_feature(feature_text, serena_research)

    # Should extract relevant topics
    assert isinstance(topics, list)
    assert len(topics) > 0
    assert len(topics) <= 5  # Limited to 5 topics

    # Should identify authentication-related topics
    assert any(t in ["authentication", "async", "testing", "security"] for t in topics)


def test_fetch_documentation():
    """Test documentation fetch orchestration."""
    documentation_links = [
        {"title": "FastAPI", "url": "", "type": "library"},
        {"title": "pytest", "url": "", "type": "library"},
        {"title": "JWT Best Practices", "url": "https://jwt.io/introduction", "type": "link"}
    ]

    feature_context = "Build JWT-based authentication with FastAPI"
    serena_research = {"patterns": [], "test_patterns": []}

    result = fetch_documentation(documentation_links, feature_context, serena_research)

    # Verify structure
    assert "library_docs" in result
    assert "external_links" in result
    assert "context7_available" in result
    assert "sequential_thinking_available" in result

    # Verify types
    assert isinstance(result["library_docs"], list)
    assert isinstance(result["external_links"], list)

    # MCP not available yet
    assert result["context7_available"] is False
    assert result["sequential_thinking_available"] is False


def test_extract_topics_multiple_patterns():
    """Test topic extraction identifies multiple technical patterns."""
    feature_text = """
    Build a REST API with database integration:
    - GraphQL endpoint for queries
    - SQL database with models
    - Schema validation
    - Security with bcrypt hashing
    """

    topics = extract_topics_from_feature(feature_text, {})

    # Should identify multiple patterns
    assert len(topics) >= 3
    assert "api" in topics
    assert "database" in topics
    assert "security" in topics or "validation" in topics
