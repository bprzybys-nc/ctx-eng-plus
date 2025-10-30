"""Mock executor for testing pipeline structure.

Validates structure but doesn't render real platform output.
Used in tests to verify pipeline definition correctness.
"""

from typing import Dict, Any
from .base import BaseExecutor


class MockExecutor(BaseExecutor):
    """Mock executor for testing pipeline structure.

    Validates structure but doesn't render real platform output.
    Used in tests to verify pipeline definition correctness.

    Example:
        executor = MockExecutor()
        pipeline = load_abstract_pipeline("test.yml")
        result = executor.render(pipeline)  # Returns mock success
    """

    def __init__(self, should_fail: bool = False):
        """Initialize mock executor.

        Args:
            should_fail: If True, render() raises error (for testing failure cases)
        """
        self.should_fail = should_fail
        self.render_calls = []

    def render(self, pipeline: Dict[str, Any]) -> str:
        """Mock render - validates structure and returns mock output.

        Args:
            pipeline: Abstract pipeline definition

        Returns:
            Mock YAML string

        Raises:
            RuntimeError: If should_fail=True
        """
        self.render_calls.append(pipeline)

        if self.should_fail:
            raise RuntimeError(
                "Mock executor configured to fail\n"
                "🔧 Troubleshooting: Set should_fail=False for success"
            )

        # Return mock output
        return f"# Mock pipeline: {pipeline['name']}\n# Stages: {len(pipeline['stages'])}"

    def validate_output(self, output: str) -> Dict[str, Any]:
        """Mock validation - always succeeds."""
        return {"success": True, "errors": []}

    def get_platform_name(self) -> str:
        """Return 'mock'."""
        return "mock"
