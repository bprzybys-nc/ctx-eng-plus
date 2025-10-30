"""Strategy interface for pipeline node execution.

Defines Protocol-based interface for interchangeable node implementations.
Real strategies call actual external APIs/services.
Mock strategies return canned data for testing.
"""

from typing import Protocol, Any, Dict


class NodeStrategy(Protocol):
    """Interface for pipeline node execution strategies.

    Strategies are interchangeable implementations of node logic.
    Real strategies call actual external APIs/services.
    Mock strategies return canned data for testing.

    Example:
        # Real strategy
        class RealParserStrategy(BaseRealStrategy):
            def execute(self, input_data):
                return parse_blueprint(input_data["prp_path"])

        # Mock strategy
        class MockParserStrategy(BaseMockStrategy):
            def execute(self, input_data):
                return {"phases": [...]}  # Canned data
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute node logic with input data.

        Args:
            input_data: Node input (from previous node or pipeline start)

        Returns:
            Node output (passed to next node or returned as result)

        Raises:
            RuntimeError: If node execution fails
        """
        ...

    def is_mocked(self) -> bool:
        """Return True if this is a mock strategy.

        Used for observable mocking (🎭 indicator in logs).

        Returns:
            True if mock strategy, False if real strategy
        """
        ...


class BaseRealStrategy:
    """Base class for real strategies (optional, for code reuse).

    Real strategies execute actual logic (call external APIs, run commands, etc.).
    Use this base class to avoid implementing is_mocked() in every strategy.

    Example:
        class RealCommandStrategy(BaseRealStrategy):
            def execute(self, input_data):
                cmd = input_data["cmd"]
                return run_cmd(cmd)
    """

    def is_mocked(self) -> bool:
        """Return False (this is a real strategy)."""
        return False


class BaseMockStrategy:
    """Base class for mock strategies (optional, for code reuse).

    Mock strategies return canned data instead of calling external services.
    Use this base class to avoid implementing is_mocked() in every strategy.

    Example:
        class MockSerenaStrategy(BaseMockStrategy):
            def __init__(self, canned_results):
                self.results = canned_results

            def execute(self, input_data):
                return {"success": True, "results": self.results}
    """

    def is_mocked(self) -> bool:
        """Return True (this is a mock strategy)."""
        return True
