"""Tests for strategy interface and base classes."""

import pytest
from typing import Dict, Any

from ce.testing.strategy import NodeStrategy, BaseRealStrategy, BaseMockStrategy


class TestNodeStrategyProtocol:
    """Test NodeStrategy protocol interface."""

    def test_protocol_defines_execute_method(self):
        """Test protocol requires execute() method."""
        # Protocol doesn't enforce at runtime, but typing checks it
        # This test documents the interface contract
        assert hasattr(NodeStrategy, 'execute')
        assert hasattr(NodeStrategy, 'is_mocked')

    def test_real_strategy_implements_protocol(self):
        """Test real strategy implements NodeStrategy protocol."""
        class TestRealStrategy(BaseRealStrategy):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "real", "input": input_data}

        strategy = TestRealStrategy()
        result = strategy.execute({"test": "data"})

        assert result["result"] == "real"
        assert result["input"]["test"] == "data"
        assert strategy.is_mocked() is False

    def test_mock_strategy_implements_protocol(self):
        """Test mock strategy implements NodeStrategy protocol."""
        class TestMockStrategy(BaseMockStrategy):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": "mock", "input": input_data}

        strategy = TestMockStrategy()
        result = strategy.execute({"test": "data"})

        assert result["result"] == "mock"
        assert result["input"]["test"] == "data"
        assert strategy.is_mocked() is True


class TestBaseRealStrategy:
    """Test BaseRealStrategy base class."""

    def test_base_real_strategy_is_mocked_returns_false(self):
        """Test BaseRealStrategy.is_mocked() returns False."""
        class SimpleRealStrategy(BaseRealStrategy):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"success": True}

        strategy = SimpleRealStrategy()
        assert strategy.is_mocked() is False

    def test_base_real_strategy_can_be_extended(self):
        """Test BaseRealStrategy can be extended with custom logic."""
        class CustomRealStrategy(BaseRealStrategy):
            def __init__(self, multiplier: int):
                self.multiplier = multiplier

            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                value = input_data.get("value", 0)
                return {
                    "result": value * self.multiplier,
                    "success": True
                }

        strategy = CustomRealStrategy(multiplier=3)
        result = strategy.execute({"value": 5})

        assert result["result"] == 15
        assert result["success"] is True
        assert strategy.is_mocked() is False


class TestBaseMockStrategy:
    """Test BaseMockStrategy base class."""

    def test_base_mock_strategy_is_mocked_returns_true(self):
        """Test BaseMockStrategy.is_mocked() returns True."""
        class SimpleMockStrategy(BaseMockStrategy):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"success": True, "mocked": True}

        strategy = SimpleMockStrategy()
        assert strategy.is_mocked() is True

    def test_base_mock_strategy_can_be_extended(self):
        """Test BaseMockStrategy can be extended with canned data."""
        class CustomMockStrategy(BaseMockStrategy):
            def __init__(self, canned_data: Dict[str, Any]):
                self.canned_data = canned_data

            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {
                    "success": True,
                    "data": self.canned_data,
                    "method": "mock"
                }

        canned = {"users": ["alice", "bob"], "count": 2}
        strategy = CustomMockStrategy(canned_data=canned)
        result = strategy.execute({"query": "users"})

        assert result["success"] is True
        assert result["data"] == canned
        assert result["method"] == "mock"
        assert strategy.is_mocked() is True


class TestStrategyInteroperability:
    """Test strategies can be used interchangeably."""

    def test_strategies_with_same_interface_are_interchangeable(self):
        """Test real and mock strategies are interchangeable."""
        class RealAddStrategy(BaseRealStrategy):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                a = input_data.get("a", 0)
                b = input_data.get("b", 0)
                return {"result": a + b, "method": "real"}

        class MockAddStrategy(BaseMockStrategy):
            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                return {"result": 42, "method": "mock"}

        # Function that accepts any strategy
        def run_with_strategy(strategy: NodeStrategy, data: Dict[str, Any]) -> Dict[str, Any]:
            return strategy.execute(data)

        # Test with real strategy
        real_strategy = RealAddStrategy()
        real_result = run_with_strategy(real_strategy, {"a": 10, "b": 20})
        assert real_result["result"] == 30
        assert real_result["method"] == "real"

        # Test with mock strategy (same interface)
        mock_strategy = MockAddStrategy()
        mock_result = run_with_strategy(mock_strategy, {"a": 10, "b": 20})
        assert mock_result["result"] == 42
        assert mock_result["method"] == "mock"
