"""Strategy Pattern for Composable Testing.

Pattern: Define interchangeable strategies (real/mock) for pipeline nodes.
Use Case: Test complex workflows with mix of real + mock external dependencies.
Benefits: Test any subgraph without full integration setup.

Source: PRP-11 Pipeline Testing Framework
Implementation: tools/ce/testing/
"""

from typing import Protocol, Any, Dict


# ============================================================================
# Strategy Interface (Protocol-based for flexibility)
# ============================================================================

class NodeStrategy(Protocol):
    """Interface for pipeline node execution strategies.

    Real strategies call actual external APIs/services.
    Mock strategies return canned data for testing.
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute node logic with input data."""
        ...

    def is_mocked(self) -> bool:
        """Return True if this is a mock strategy."""
        ...


# ============================================================================
# Base Classes (Optional - Avoid boilerplate)
# ============================================================================

class BaseRealStrategy:
    """Base for real strategies - implements is_mocked() as False."""
    def is_mocked(self) -> bool:
        return False


class BaseMockStrategy:
    """Base for mock strategies - implements is_mocked() as True."""
    def is_mocked(self) -> bool:
        return True


# ============================================================================
# Example: Real Strategy
# ============================================================================

class RealDatabaseStrategy(BaseRealStrategy):
    """Real strategy: Hits actual database."""

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        # Real implementation calls actual DB
        user_id = input_data["user_id"]
        # user = db.query(User).filter_by(id=user_id).first()
        return {"user_id": user_id, "name": "John Doe"}  # Simplified


# ============================================================================
# Example: Mock Strategy
# ============================================================================

class MockDatabaseStrategy(BaseMockStrategy):
    """Mock strategy: Returns canned data."""

    def __init__(self, canned_users: list):
        self.users = {user["user_id"]: user for user in canned_users}

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = input_data["user_id"]
        return self.users.get(user_id, {"error": "User not found"})


# ============================================================================
# Testing Pattern
# ============================================================================

def test_unit_with_mock():
    """Unit test: Test single node with mock dependency."""
    strategy = MockDatabaseStrategy(canned_users=[
        {"user_id": 123, "name": "Test User"}
    ])

    result = strategy.execute({"user_id": 123})

    assert result["name"] == "Test User"
    assert strategy.is_mocked() is True  # Observable mocking


def test_integration_mixed():
    """Integration test: Mix real + mock strategies."""
    # In real pipeline: parser is real, database is mocked
    # parser = RealParserStrategy()
    database = MockDatabaseStrategy(canned_users=[...])

    # Test subgraph without full stack
    assert database.is_mocked() is True


# ============================================================================
# Key Insights
# ============================================================================

# 1. Protocol-based interface: No inheritance required
# 2. Base classes: Optional convenience, avoid boilerplate
# 3. Observable mocking: is_mocked() makes test mode explicit
# 4. Composable: Mix real + mock strategies freely
# 5. Test any subgraph: Don't need full integration setup
