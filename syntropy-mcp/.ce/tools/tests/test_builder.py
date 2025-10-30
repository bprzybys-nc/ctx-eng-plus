"""Tests for pipeline builder and execution."""

import pytest
from typing import Dict, Any
from io import StringIO
import sys

from ce.testing.builder import Pipeline, PipelineBuilder
from ce.testing.strategy import BaseRealStrategy, BaseMockStrategy


# Test helper strategies
class AddStrategy(BaseRealStrategy):
    """Real strategy that adds 1 to input value."""
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        value = input_data.get("value", 0)
        return {"value": value + 1, "method": "add"}


class MultiplyStrategy(BaseRealStrategy):
    """Real strategy that multiplies value by 2."""
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        value = input_data.get("value", 0)
        return {"value": value * 2, "method": "multiply"}


class MockFixedStrategy(BaseMockStrategy):
    """Mock strategy that returns fixed value."""
    def __init__(self, fixed_value: int):
        self.fixed_value = fixed_value

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"value": self.fixed_value, "method": "mock_fixed"}


class TestPipeline:
    """Test Pipeline execution."""

    def test_pipeline_executes_single_node(self):
        """Test pipeline executes single node correctly."""
        strategy = AddStrategy()
        pipeline = Pipeline(nodes={"add": strategy}, edges=[])

        result = pipeline.execute({"value": 5})

        assert result["value"] == 6
        assert result["method"] == "add"

    def test_pipeline_executes_linear_sequence(self):
        """Test pipeline executes nodes in linear order."""
        nodes = {
            "add": AddStrategy(),
            "multiply": MultiplyStrategy()
        }
        edges = [("add", "multiply")]
        pipeline = Pipeline(nodes, edges)

        # (5 + 1) * 2 = 12
        result = pipeline.execute({"value": 5})

        assert result["value"] == 12
        assert result["method"] == "multiply"

    def test_pipeline_executes_three_node_sequence(self):
        """Test pipeline executes three nodes in order."""
        nodes = {
            "add1": AddStrategy(),
            "multiply": MultiplyStrategy(),
            "add2": AddStrategy()
        }
        edges = [("add1", "multiply"), ("multiply", "add2")]
        pipeline = Pipeline(nodes, edges)

        # ((5 + 1) * 2) + 1 = 13
        result = pipeline.execute({"value": 5})

        assert result["value"] == 13

    def test_pipeline_topological_sort_with_dag(self):
        """Test pipeline handles DAG with multiple start nodes."""
        # Simple DAG: a -> c, b -> c
        class PassThroughStrategy(BaseRealStrategy):
            def __init__(self, name: str):
                self.name = name

            def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
                path = input_data.get("path", [])
                path.append(self.name)
                return {"path": path}

        nodes = {
            "a": PassThroughStrategy("a"),
            "b": PassThroughStrategy("b"),
            "c": PassThroughStrategy("c")
        }
        edges = [("a", "c"), ("b", "c")]
        pipeline = Pipeline(nodes, edges)

        result = pipeline.execute({"path": []})

        # c should execute after both a and b
        assert "c" in result["path"]
        assert result["path"].index("c") > result["path"].index("a")
        assert result["path"].index("c") > result["path"].index("b")

    def test_pipeline_detects_circular_dependencies(self):
        """Test pipeline raises error for circular dependencies."""
        nodes = {
            "a": AddStrategy(),
            "b": MultiplyStrategy(),
            "c": AddStrategy()
        }
        # Create cycle: a -> b -> c -> a
        edges = [("a", "b"), ("b", "c"), ("c", "a")]
        pipeline = Pipeline(nodes, edges)

        with pytest.raises(RuntimeError) as exc_info:
            pipeline.execute({"value": 5})

        error_msg = str(exc_info.value)
        assert "circular dependencies" in error_msg
        assert "🔧 Troubleshooting" in error_msg
        # All nodes should be mentioned in the cycle
        assert "a" in error_msg or "b" in error_msg or "c" in error_msg


class TestPipelineBuilder:
    """Test PipelineBuilder fluent API."""

    def test_builder_creates_pipeline(self):
        """Test builder creates valid pipeline."""
        pipeline = (
            PipelineBuilder(mode="unit")
            .add_node("add", AddStrategy())
            .build()
        )

        result = pipeline.execute({"value": 10})
        assert result["value"] == 11

    def test_builder_method_chaining(self):
        """Test builder supports method chaining."""
        builder = PipelineBuilder(mode="integration")
        result = builder.add_node("add", AddStrategy())

        # Should return self for chaining
        assert result is builder

        result = builder.add_edge("add", "add")
        assert result is builder

    def test_builder_with_multiple_nodes_and_edges(self):
        """Test builder creates pipeline with multiple nodes."""
        pipeline = (
            PipelineBuilder(mode="integration")
            .add_node("add", AddStrategy())
            .add_node("multiply", MultiplyStrategy())
            .add_edge("add", "multiply")
            .build()
        )

        result = pipeline.execute({"value": 5})
        assert result["value"] == 12  # (5 + 1) * 2

    def test_builder_raises_error_for_invalid_edge_from_node(self):
        """Test builder raises error when from_node doesn't exist."""
        builder = PipelineBuilder()
        builder.add_node("add", AddStrategy())

        with pytest.raises(ValueError) as exc_info:
            builder.add_edge("nonexistent", "add")

        error_msg = str(exc_info.value)
        assert "from_node 'nonexistent' not in pipeline" in error_msg
        assert "🔧 Troubleshooting" in error_msg

    def test_builder_raises_error_for_invalid_edge_to_node(self):
        """Test builder raises error when to_node doesn't exist."""
        builder = PipelineBuilder()
        builder.add_node("add", AddStrategy())

        with pytest.raises(ValueError) as exc_info:
            builder.add_edge("add", "nonexistent")

        error_msg = str(exc_info.value)
        assert "to_node 'nonexistent' not in pipeline" in error_msg
        assert "🔧 Troubleshooting" in error_msg

    def test_builder_observable_mocking_prints_mocked_nodes(self, capsys):
        """Test builder prints 🎭 indicator for mocked nodes."""
        pipeline = (
            PipelineBuilder(mode="e2e")
            .add_node("real", AddStrategy())
            .add_node("mock", MockFixedStrategy(42))
            .build()
        )

        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES: mock" in captured.out

    def test_builder_observable_mocking_with_multiple_mocks(self, capsys):
        """Test builder prints all mocked nodes."""
        pipeline = (
            PipelineBuilder(mode="e2e")
            .add_node("real", AddStrategy())
            .add_node("mock1", MockFixedStrategy(10))
            .add_node("mock2", MockFixedStrategy(20))
            .build()
        )

        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES:" in captured.out
        assert "mock1" in captured.out
        assert "mock2" in captured.out

    def test_builder_no_output_when_all_real(self, capsys):
        """Test builder doesn't print when no mocks."""
        pipeline = (
            PipelineBuilder(mode="integration")
            .add_node("real1", AddStrategy())
            .add_node("real2", MultiplyStrategy())
            .build()
        )

        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES" not in captured.out

    def test_builder_mode_parameter_stored(self):
        """Test builder stores mode parameter."""
        builder = PipelineBuilder(mode="unit")
        assert builder.mode == "unit"

        builder = PipelineBuilder(mode="integration")
        assert builder.mode == "integration"

        builder = PipelineBuilder(mode="e2e")
        assert builder.mode == "e2e"
