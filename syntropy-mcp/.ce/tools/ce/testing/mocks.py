"""Mock strategy implementations for common external dependencies.

Provides pre-built mock strategies with canned data for typical use cases:
- MockSerenaStrategy: Codebase search operations
- MockContext7Strategy: Documentation fetching
- MockLLMStrategy: Text generation with templates
"""

from typing import List, Dict, Any
from .strategy import BaseMockStrategy


class MockSerenaStrategy(BaseMockStrategy):
    """Mock Serena MCP for codebase search operations.

    Returns canned search results instead of real MCP calls.
    Useful for testing pipelines without hitting Serena MCP server.

    Example:
        strategy = MockSerenaStrategy(canned_results=[
            {"file": "test.py", "match": "def test(): pass"}
        ])
        result = strategy.execute({"pattern": "def test"})
        # Returns: {"success": True, "results": [...], "method": "mock_serena"}
    """

    def __init__(self, canned_results: List[Dict[str, Any]]):
        """Initialize with canned data.

        Args:
            canned_results: List of search results to return
                Format: [{"file": "path/to/file.py", "match": "code snippet"}]
        """
        self.results = canned_results

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return canned search results.

        Args:
            input_data: Search request (pattern, path, etc.)
                Format: {"pattern": "regex", "path": "src/"}

        Returns:
            Mock search results
                Format: {"success": True, "results": [...], "method": "mock_serena"}
        """
        return {
            "success": True,
            "results": self.results,
            "method": "mock_serena"
        }


class MockContext7Strategy(BaseMockStrategy):
    """Mock Context7 MCP for documentation fetching.

    Returns cached documentation instead of API calls.
    Useful for testing without hitting Context7 API.

    Example:
        strategy = MockContext7Strategy(cached_docs="pytest fixtures...")
        result = strategy.execute({"library": "pytest", "topic": "fixtures"})
        # Returns: {"success": True, "docs": "...", "method": "mock_context7"}
    """

    def __init__(self, cached_docs: str):
        """Initialize with cached documentation.

        Args:
            cached_docs: Documentation text to return
        """
        self.docs = cached_docs

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return cached documentation.

        Args:
            input_data: Documentation request
                Format: {"library": "pytest", "topic": "fixtures"}

        Returns:
            Mock documentation
                Format: {"success": True, "docs": "...", "method": "mock_context7"}
        """
        return {
            "success": True,
            "docs": self.docs,
            "method": "mock_context7"
        }


class MockLLMStrategy(BaseMockStrategy):
    """Mock LLM for text generation (PRP generation, code synthesis).

    Returns template-based responses instead of LLM API calls.
    Useful for testing without consuming tokens.

    Example:
        strategy = MockLLMStrategy(template="# {title}\n\n{content}")
        result = strategy.execute({
            "prompt": "Generate PRP",
            "context": {"title": "PRP-1", "content": "Test feature"}
        })
        # Returns: {"success": True, "response": "# PRP-1\n\nTest feature", ...}
    """

    def __init__(self, template: str):
        """Initialize with response template.

        Args:
            template: Template string with {placeholders}
                Example: "# {title}\n\n{content}"
        """
        self.template = template

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response from template.

        Args:
            input_data: Generation request
                Format: {
                    "prompt": "Generate PRP",
                    "context": {"title": "PRP-1", "content": "..."}
                }

        Returns:
            Mock LLM response
                Format: {
                    "success": True,
                    "response": "...",
                    "method": "mock_llm",
                    "tokens_saved": 5000
                }

        Raises:
            RuntimeError: If template requires missing context keys
        """
        context = input_data.get("context", {})

        try:
            response = self.template.format(**context)
        except KeyError as e:
            # Provide helpful error for missing template variables
            missing_key = str(e).strip("'")
            raise RuntimeError(
                f"Template requires key '{missing_key}' but context is missing it\n"
                f"Template: {self.template[:100]}{'...' if len(self.template) > 100 else ''}\n"
                f"Context keys: {list(context.keys())}\n"
                f"🔧 Troubleshooting: Provide '{missing_key}' in input_data['context']"
            )

        return {
            "success": True,
            "response": response,
            "method": "mock_llm",
            "tokens_saved": 5000  # Estimated tokens saved vs real LLM
        }
