"""Tests for mock strategy implementations."""

import pytest
from typing import Dict, Any

from ce.testing.mocks import MockSerenaStrategy, MockContext7Strategy, MockLLMStrategy


class TestMockSerenaStrategy:
    """Test MockSerenaStrategy for codebase search mocking."""

    def test_mock_serena_returns_canned_results(self):
        """Test MockSerenaStrategy returns canned search results."""
        canned_results = [
            {"file": "test.py", "match": "def test(): pass"},
            {"file": "util.py", "match": "def helper(): pass"}
        ]
        strategy = MockSerenaStrategy(canned_results=canned_results)

        result = strategy.execute({"pattern": "def test"})

        assert result["success"] is True
        assert result["method"] == "mock_serena"
        assert result["results"] == canned_results
        assert len(result["results"]) == 2

    def test_mock_serena_is_mocked_returns_true(self):
        """Test MockSerenaStrategy.is_mocked() returns True."""
        strategy = MockSerenaStrategy(canned_results=[])
        assert strategy.is_mocked() is True

    def test_mock_serena_with_empty_results(self):
        """Test MockSerenaStrategy handles empty results list."""
        strategy = MockSerenaStrategy(canned_results=[])
        result = strategy.execute({"pattern": "nonexistent"})

        assert result["success"] is True
        assert result["results"] == []

    def test_mock_serena_ignores_input_data(self):
        """Test MockSerenaStrategy returns same data regardless of input."""
        canned = [{"file": "fixed.py", "match": "fixed"}]
        strategy = MockSerenaStrategy(canned_results=canned)

        # Different inputs should return same canned data
        result1 = strategy.execute({"pattern": "test1"})
        result2 = strategy.execute({"pattern": "test2"})

        assert result1["results"] == result2["results"]
        assert result1["results"] == canned


class TestMockContext7Strategy:
    """Test MockContext7Strategy for documentation mocking."""

    def test_mock_context7_returns_cached_docs(self):
        """Test MockContext7Strategy returns cached documentation."""
        cached_docs = "pytest fixtures allow test setup and teardown..."
        strategy = MockContext7Strategy(cached_docs=cached_docs)

        result = strategy.execute({"library": "pytest", "topic": "fixtures"})

        assert result["success"] is True
        assert result["method"] == "mock_context7"
        assert result["docs"] == cached_docs

    def test_mock_context7_is_mocked_returns_true(self):
        """Test MockContext7Strategy.is_mocked() returns True."""
        strategy = MockContext7Strategy(cached_docs="test docs")
        assert strategy.is_mocked() is True

    def test_mock_context7_with_empty_docs(self):
        """Test MockContext7Strategy handles empty documentation."""
        strategy = MockContext7Strategy(cached_docs="")
        result = strategy.execute({"library": "unknown"})

        assert result["success"] is True
        assert result["docs"] == ""

    def test_mock_context7_ignores_input_data(self):
        """Test MockContext7Strategy returns same docs regardless of input."""
        cached = "Fixed documentation content"
        strategy = MockContext7Strategy(cached_docs=cached)

        # Different inputs should return same cached docs
        result1 = strategy.execute({"library": "pytest", "topic": "fixtures"})
        result2 = strategy.execute({"library": "django", "topic": "models"})

        assert result1["docs"] == result2["docs"]
        assert result1["docs"] == cached


class TestMockLLMStrategy:
    """Test MockLLMStrategy for LLM mocking."""

    def test_mock_llm_generates_from_template(self):
        """Test MockLLMStrategy generates response from template."""
        template = "# {title}\n\n{content}"
        strategy = MockLLMStrategy(template=template)

        result = strategy.execute({
            "prompt": "Generate PRP",
            "context": {
                "title": "PRP-42",
                "content": "Test feature implementation"
            }
        })

        assert result["success"] is True
        assert result["method"] == "mock_llm"
        assert result["response"] == "# PRP-42\n\nTest feature implementation"
        assert "tokens_saved" in result
        assert result["tokens_saved"] == 5000

    def test_mock_llm_is_mocked_returns_true(self):
        """Test MockLLMStrategy.is_mocked() returns True."""
        strategy = MockLLMStrategy(template="test")
        assert strategy.is_mocked() is True

    def test_mock_llm_raises_error_for_missing_context_key(self):
        """Test MockLLMStrategy raises error when template key missing."""
        template = "# {title}\n\n{content}"
        strategy = MockLLMStrategy(template=template)

        # Missing 'content' key
        with pytest.raises(RuntimeError) as exc_info:
            strategy.execute({
                "prompt": "Generate",
                "context": {"title": "Test"}  # Missing 'content'
            })

        error_msg = str(exc_info.value)
        assert "requires key 'content'" in error_msg
        assert "🔧 Troubleshooting" in error_msg
        assert "Context keys: ['title']" in error_msg

    def test_mock_llm_with_empty_context(self):
        """Test MockLLMStrategy with no context placeholders."""
        template = "Static response with no placeholders"
        strategy = MockLLMStrategy(template=template)

        result = strategy.execute({
            "prompt": "Generate",
            "context": {}
        })

        assert result["success"] is True
        assert result["response"] == "Static response with no placeholders"

    def test_mock_llm_with_multiple_placeholders(self):
        """Test MockLLMStrategy with multiple template variables."""
        template = "User: {username}, Email: {email}, Role: {role}"
        strategy = MockLLMStrategy(template=template)

        result = strategy.execute({
            "prompt": "Format user",
            "context": {
                "username": "alice",
                "email": "alice@example.com",
                "role": "admin"
            }
        })

        assert result["success"] is True
        assert result["response"] == "User: alice, Email: alice@example.com, Role: admin"

    def test_mock_llm_with_no_input_context(self):
        """Test MockLLMStrategy when input_data has no 'context' key."""
        template = "Static template"
        strategy = MockLLMStrategy(template=template)

        result = strategy.execute({"prompt": "Generate"})

        assert result["success"] is True
        assert result["response"] == "Static template"


class TestMockStrategyInteroperability:
    """Test mock strategies work interchangeably with common interface."""

    def test_all_mock_strategies_have_is_mocked(self):
        """Test all mock strategies implement is_mocked()."""
        serena = MockSerenaStrategy(canned_results=[])
        context7 = MockContext7Strategy(cached_docs="test")
        llm = MockLLMStrategy(template="test")

        assert serena.is_mocked() is True
        assert context7.is_mocked() is True
        assert llm.is_mocked() is True

    def test_all_mock_strategies_have_execute(self):
        """Test all mock strategies implement execute()."""
        serena = MockSerenaStrategy(canned_results=[{"file": "test.py"}])
        context7 = MockContext7Strategy(cached_docs="docs")
        llm = MockLLMStrategy(template="{title}")

        # All should execute without error
        serena_result = serena.execute({"pattern": "test"})
        context7_result = context7.execute({"library": "test"})
        llm_result = llm.execute({"context": {"title": "test"}})

        assert serena_result["success"] is True
        assert context7_result["success"] is True
        assert llm_result["success"] is True

    def test_all_mock_strategies_return_method_field(self):
        """Test all mock strategies include 'method' field in response."""
        serena = MockSerenaStrategy(canned_results=[])
        context7 = MockContext7Strategy(cached_docs="test")
        llm = MockLLMStrategy(template="test")

        assert serena.execute({})["method"] == "mock_serena"
        assert context7.execute({})["method"] == "mock_context7"
        assert llm.execute({"context": {}})["method"] == "mock_llm"
