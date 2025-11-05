"""Unit tests for LLM client."""

import pytest
import os
from ce.blending.llm_client import BlendingLLM, HAIKU_MODEL, SONNET_MODEL


def test_blending_llm_requires_api_key():
    """Test BlendingLLM raises error without API key."""
    # Save and clear API key
    original_key = os.environ.get("ANTHROPIC_API_KEY")
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]

    try:
        with pytest.raises(ValueError, match="API key required"):
            BlendingLLM()
    finally:
        # Restore API key
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key


def test_blending_llm_accepts_api_key_parameter():
    """Test BlendingLLM accepts API key as parameter."""
    llm = BlendingLLM(api_key="sk-test-key-123")
    assert llm.api_key == "sk-test-key-123"
    assert llm.timeout == 60
    assert llm.max_retries == 3


def test_blending_llm_accepts_custom_timeout():
    """Test BlendingLLM accepts custom timeout and retries."""
    llm = BlendingLLM(api_key="sk-test-key", timeout=120, max_retries=5)
    assert llm.timeout == 120
    assert llm.max_retries == 5


def test_blending_llm_tracks_token_usage():
    """Test token usage tracking."""
    llm = BlendingLLM(api_key="sk-test-key")

    # Initial state
    usage = llm.get_token_usage()
    assert usage["input_tokens"] == 0
    assert usage["output_tokens"] == 0
    assert usage["total_tokens"] == 0


def test_model_constants():
    """Test model constants are correct."""
    assert HAIKU_MODEL == "claude-3-5-haiku-20241022"
    assert SONNET_MODEL == "claude-sonnet-4-5-20250929"


def test_blending_philosophy_enforced():
    """Test blending philosophy is included in prompts."""
    from ce.blending.llm_client import BLENDING_PHILOSOPHY

    assert "Copy ours" in BLENDING_PHILOSOPHY
    assert "Framework content is authoritative" in BLENDING_PHILOSOPHY
    assert "Target customizations" in BLENDING_PHILOSOPHY
    assert "Additive merging preferred" in BLENDING_PHILOSOPHY


def test_token_tracking_initialization():
    """Test token counters are initialized to zero."""
    llm = BlendingLLM(api_key="sk-test-key")

    assert llm.total_input_tokens == 0
    assert llm.total_output_tokens == 0


def test_error_message_includes_troubleshooting():
    """Test error messages include troubleshooting section."""
    try:
        BlendingLLM()  # No API key
    except ValueError as e:
        error_msg = str(e)
        assert "🔧 Troubleshooting:" in error_msg
        assert "ANTHROPIC_API_KEY" in error_msg
        assert "https://console.anthropic.com" in error_msg


# Integration tests (require ANTHROPIC_API_KEY)

@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_check_similarity_live():
    """Test check_similarity with live API (integration test)."""
    llm = BlendingLLM()

    # Similar texts
    result = llm.check_similarity(
        "The quick brown fox jumps over the lazy dog",
        "A fast brown fox leaps over a sleepy dog"
    )

    assert "similar" in result
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert result["model"] == HAIKU_MODEL
    assert "tokens" in result
    assert result["tokens"]["input"] > 0
    assert result["tokens"]["output"] > 0

    # Verify token tracking
    usage = llm.get_token_usage()
    assert usage["input_tokens"] > 0
    assert usage["output_tokens"] > 0


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_check_similarity_dissimilar_texts():
    """Test check_similarity with dissimilar texts."""
    llm = BlendingLLM()

    # Different texts
    result = llm.check_similarity(
        "Python programming language documentation",
        "Recipe for chocolate cake with frosting"
    )

    assert result["score"] < 0.5  # Should be dissimilar
    assert not result["similar"]  # Default threshold is 0.9


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_classify_file_live():
    """Test classify_file with live API (integration test)."""
    llm = BlendingLLM()

    # Valid CE PRP content
    content = """---
prp_id: PRP-123
status: pending
---

# PRP-123: Test Feature

## TL;DR

Test feature implementation

## Context

Background information

## Implementation Steps

Steps to implement"""

    result = llm.classify_file(
        content=content,
        expected_patterns=[
            "YAML header with prp_id",
            "## sections",
            "Implementation Steps"
        ],
        file_path="test.md"
    )

    assert "valid" in result
    assert "confidence" in result
    assert "issues" in result
    assert "model" in result
    assert result["model"] == HAIKU_MODEL
    assert 0.0 <= result["confidence"] <= 1.0


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_blend_content_live():
    """Test blend_content with live API (integration test - expensive)."""
    llm = BlendingLLM()

    framework_content = """# Framework CLAUDE.md

## Core Principles

- Use Syntropy MCP first
- No fishy fallbacks
- KISS principle"""

    target_content = """# Project Guide

## My Custom Section

Project-specific customizations here.

## Core Principles

- Custom principle 1
- Custom principle 2"""

    result = llm.blend_content(
        framework_content=framework_content,
        target_content=target_content,
        domain="test_domain"
    )

    assert "blended" in result
    assert "model" in result
    assert result["model"] == SONNET_MODEL
    assert "tokens" in result
    assert "confidence" in result
    assert 0.0 <= result["confidence"] <= 1.0
    assert "## Core Principles" in result["blended"]  # Framework section preserved


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_blend_content_no_target():
    """Test blend_content with no target content."""
    llm = BlendingLLM()

    framework_content = """# Framework Content

## Section 1

Framework rules"""

    result = llm.blend_content(
        framework_content=framework_content,
        target_content=None,
        domain="test_domain"
    )

    assert "blended" in result
    assert result["confidence"] == 1.0  # No target, just framework


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_cumulative_token_tracking():
    """Test token tracking across multiple operations."""
    llm = BlendingLLM()

    # Perform multiple operations
    llm.check_similarity("text1", "text2")
    llm.check_similarity("text3", "text4")

    # Check cumulative usage
    usage = llm.get_token_usage()
    assert usage["total_tokens"] > 0
    assert usage["input_tokens"] > 0
    assert usage["output_tokens"] > 0
    assert usage["total_tokens"] == usage["input_tokens"] + usage["output_tokens"]


# Error handling tests

def test_blend_content_error_message_format():
    """Test blend_content error messages include troubleshooting."""
    llm = BlendingLLM(api_key="sk-invalid-key-123")

    # This will fail with invalid API key
    try:
        llm.blend_content(
            framework_content="test",
            target_content="test",
            domain="test"
        )
    except RuntimeError as e:
        error_msg = str(e)
        assert "🔧 Troubleshooting:" in error_msg
        assert "API key" in error_msg.lower() or "network" in error_msg.lower()


def test_check_similarity_error_message_format():
    """Test check_similarity error messages include troubleshooting."""
    llm = BlendingLLM(api_key="sk-invalid-key-123")

    try:
        llm.check_similarity("text1", "text2")
    except RuntimeError as e:
        error_msg = str(e)
        assert "🔧 Troubleshooting:" in error_msg


def test_classify_file_error_message_format():
    """Test classify_file error messages include troubleshooting."""
    llm = BlendingLLM(api_key="sk-invalid-key-123")

    try:
        llm.classify_file("content", ["pattern1"], "test.md")
    except RuntimeError as e:
        error_msg = str(e)
        assert "🔧 Troubleshooting:" in error_msg
