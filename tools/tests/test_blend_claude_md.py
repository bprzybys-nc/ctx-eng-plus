"""Tests for ClaudeMdBlendStrategy.

Tests section parsing, categorization, blending logic, and validation.
Uses mock LLM responses for fast, deterministic tests.
"""

import pytest
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy


class MockLLM:
    """Mock BlendingLLM for testing."""

    def blend_content(self, framework_content, target_content, rules_content=None, domain="unknown"):
        """Mock blend_content that returns simple merge."""
        # Simple mock: append target to framework
        blended = framework_content
        if target_content and target_content.strip():
            blended += f"\n\n<!-- Target additions -->\n{target_content}"

        return {
            "blended": blended,
            "model": "mock-sonnet",
            "tokens": {"input": 100, "output": 50},
            "confidence": 0.95
        }


def test_can_handle_claude_md_domain():
    """Test can_handle() returns True for 'claude_md' domain."""
    strategy = ClaudeMdBlendStrategy()
    assert strategy.can_handle("claude_md") is True
    assert strategy.can_handle("settings") is False
    assert strategy.can_handle("commands") is False


def test_parse_sections_splits_by_h2():
    """Test parse_sections() splits content by H2 headers."""
    strategy = ClaudeMdBlendStrategy()

    content = """# CLAUDE.md

## Core Principles

Principle 1
Principle 2

## Testing Standards

Standard 1
Standard 2

## Project Structure

Structure info
"""

    sections = strategy.parse_sections(content)

    assert len(sections) == 3
    assert "Core Principles" in sections
    assert "Testing Standards" in sections
    assert "Project Structure" in sections
    assert "Principle 1" in sections["Core Principles"]


def test_parse_sections_empty_content():
    """Test parse_sections() handles empty content."""
    strategy = ClaudeMdBlendStrategy()

    sections = strategy.parse_sections("")
    assert sections == {}

    sections = strategy.parse_sections("   ")
    assert sections == {}


def test_categorize_section_framework():
    """Test categorize_section() identifies framework sections."""
    strategy = ClaudeMdBlendStrategy()

    assert strategy.categorize_section("Core Principles") == "framework"
    assert strategy.categorize_section("Testing Standards") == "framework"
    assert strategy.categorize_section("Code Quality") == "framework"


def test_categorize_section_hybrid():
    """Test categorize_section() identifies hybrid sections."""
    strategy = ClaudeMdBlendStrategy()

    assert strategy.categorize_section("Quick Commands") == "hybrid"
    assert strategy.categorize_section("Command Permissions") == "hybrid"
    assert strategy.categorize_section("Resources") == "hybrid"


def test_categorize_section_project():
    """Test categorize_section() defaults to project for unknown."""
    strategy = ClaudeMdBlendStrategy()

    assert strategy.categorize_section("Project Structure") == "project"
    assert strategy.categorize_section("Custom Section") == "project"
    assert strategy.categorize_section("Team Info") == "project"


def test_blend_requires_llm_client():
    """Test blend() raises if llm_client not in context."""
    strategy = ClaudeMdBlendStrategy()

    with pytest.raises(ValueError, match="LLM client required"):
        strategy.blend("## Test", "## Test", context={})

    with pytest.raises(ValueError, match="LLM client required"):
        strategy.blend("## Test", "## Test", context=None)


def test_blend_framework_sections_copied():
    """Test blend() copies framework sections as-is."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principle 1
Framework principle 2

## Testing Standards

Framework standard 1
"""

    target = """## Core Principles

Target principle 1

## Custom Section

Target custom info
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, target, context)

    # Framework sections should be copied (not merged)
    assert "Framework principle 1" in result
    assert "Framework principle 2" in result
    # Target changes to framework sections should NOT appear
    assert "Target principle 1" not in result


def test_blend_hybrid_sections_merged():
    """Test blend() merges hybrid sections with Sonnet."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Quick Commands

Framework command 1

## Resources

Framework resource 1
"""

    target = """## Quick Commands

Target command 1

## Resources

Target resource 1
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, target, context)

    # Hybrid sections should be merged (MockLLM appends)
    sections = strategy.parse_sections(result)
    assert "Quick Commands" in sections
    # The blended section should contain both framework and target content
    # MockLLM appends target to framework with a comment marker
    assert "Framework command 1" in result or "Target command 1" in result
    # Verify the section was processed (contains target additions marker from MockLLM)
    assert "Target additions" in sections["Quick Commands"] or "Target command 1" in sections["Quick Commands"]


def test_blend_target_only_sections_imported():
    """Test blend() imports target-only project sections."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principles
"""

    target = """## Core Principles

Target principles

## Project Structure

Target project structure
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, target, context)

    # Target-only project section should be imported
    assert "Project Structure" in result
    assert "Target project structure" in result


def test_blend_empty_target():
    """Test blend() handles empty target content."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principles

## Testing Standards

Framework standards
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, "", context)

    # Framework sections should be present
    assert "Core Principles" in result
    assert "Testing Standards" in result
    assert "Framework principles" in result


def test_blend_none_target():
    """Test blend() handles None target content."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principles

## Testing Standards

Framework standards
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, None, context)

    # Framework sections should be present
    assert "Core Principles" in result
    assert "Testing Standards" in result
    assert "Framework principles" in result


def test_validate_valid_claude_md():
    """Test validate() passes for valid CLAUDE.md."""
    strategy = ClaudeMdBlendStrategy()

    valid_content = """## Core Principles

Principles

## Framework Initialization

Init info

## Testing Standards

Standards
"""

    assert strategy.validate(valid_content, {}) is True


def test_validate_missing_required_section():
    """Test validate() raises if required section missing."""
    strategy = ClaudeMdBlendStrategy()

    invalid_content = """## Core Principles

Principles

## Custom Section

Custom info
"""

    with pytest.raises(ValueError, match="Missing required framework sections"):
        strategy.validate(invalid_content, {})


def test_validate_duplicate_sections():
    """Test validate() raises if duplicate H2 sections."""
    strategy = ClaudeMdBlendStrategy()

    invalid_content = """## Core Principles

Principles 1

## Framework Initialization

Init

## Testing Standards

Standards

## Core Principles

Principles 2 (duplicate)
"""

    with pytest.raises(ValueError, match="Duplicate H2 sections"):
        strategy.validate(invalid_content, {})


def test_validate_empty_content():
    """Test validate() raises on empty content."""
    strategy = ClaudeMdBlendStrategy()

    with pytest.raises(ValueError, match="empty"):
        strategy.validate("", {})

    with pytest.raises(ValueError, match="empty"):
        strategy.validate("   ", {})


def test_validate_no_sections():
    """Test validate() raises if no H2 sections."""
    strategy = ClaudeMdBlendStrategy()

    invalid_content = """# Title

Some content but no H2 sections
"""

    with pytest.raises(ValueError, match="No H2 sections found"):
        strategy.validate(invalid_content, {})


def test_reassemble_preserves_framework_order():
    """Test _reassemble_sections() preserves framework section order."""
    strategy = ClaudeMdBlendStrategy()

    # Create framework with specific order
    framework = """## Core Principles

Framework principles

## Testing Standards

Framework standards

## Code Quality

Framework code quality
"""

    target = """## Project Structure

Target structure
"""

    framework_sections = strategy.parse_sections(framework)
    target_sections = strategy.parse_sections(target)

    # Simulate blend
    blended_sections = {}
    blended_sections.update(framework_sections)
    blended_sections.update(target_sections)

    # Reassemble
    result = strategy._reassemble_sections(blended_sections, framework_sections)

    # Framework sections should appear before target sections
    core_idx = result.find("## Core Principles")
    testing_idx = result.find("## Testing Standards")
    code_idx = result.find("## Code Quality")
    project_idx = result.find("## Project Structure")

    assert core_idx < testing_idx < code_idx < project_idx


def test_blend_with_rules_content():
    """Test blend() passes rules_content to LLM."""
    strategy = ClaudeMdBlendStrategy()

    class VerifyLLM:
        """LLM that verifies rules_content is passed."""
        def blend_content(self, framework_content, target_content, rules_content=None, domain="unknown"):
            # Verify rules_content is passed
            assert rules_content is not None
            assert "Framework Rules" in rules_content
            return {
                "blended": framework_content,
                "model": "verify-llm",
                "tokens": {"input": 100, "output": 50},
                "confidence": 0.95
            }

    framework = """## Quick Commands

Framework commands
"""

    context = {
        "llm_client": VerifyLLM(),
        "rules_content": "# Framework Rules\n\nTest rules"
    }

    result = strategy.blend(framework, "", context)
    assert "Framework commands" in result
