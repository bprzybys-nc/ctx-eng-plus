"""Tests for PRP generation from INITIAL.md."""
import pytest
import re
from pathlib import Path
from ce.generate import (
    parse_initial_md,
    extract_code_examples,
    extract_documentation_links,
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
