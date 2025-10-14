"""Pipeline Orchestration with Builder Pattern.

Pattern: Build testable DAG pipelines with topological execution.
Use Case: Orchestrate multi-step workflows with dependency management.
Benefits: Observable mocking, cycle detection, composable node graphs.

Source: PRP-11 Pipeline Testing Framework
Implementation: tools/ce/testing/builder.py
"""

from typing import Dict, Any, List, Tuple


# ============================================================================
# Pipeline Execution
# ============================================================================

class Pipeline:
    """Executable pipeline with nodes and edges.

    Executes nodes in topological order based on dependencies.
    Supports linear pipelines and DAGs with cycle detection.
    """

    def __init__(self, nodes: Dict[str, Any], edges: List[Tuple[str, str]]):
        self.nodes = nodes
        self.edges = edges

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline from start to finish.

        Process:
            1. Topologically sort nodes by edges
            2. Execute nodes in order
            3. Pass output from node to next node
        """
        current_data = input_data

        for node_name in self._topological_sort():
            strategy = self.nodes[node_name]
            current_data = strategy.execute(current_data)

        return current_data

    def _topological_sort(self) -> List[str]:
        """Sort nodes by dependencies using Kahn's algorithm."""
        if not self.edges:
            return list(self.nodes.keys())

        # Build adjacency list
        in_degree = {node: 0 for node in self.nodes}
        adj = {node: [] for node in self.nodes}

        for from_node, to_node in self.edges:
            adj[from_node].append(to_node)
            in_degree[to_node] += 1

        # Kahn's algorithm
        queue = [node for node in self.nodes if in_degree[node] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.nodes):
            nodes_in_cycle = set(self.nodes.keys()) - set(result)
            raise RuntimeError(
                f"Pipeline has circular dependencies: {', '.join(sorted(nodes_in_cycle))}"
            )

        return result


# ============================================================================
# Builder Pattern
# ============================================================================

class PipelineBuilder:
    """Fluent builder for creating testable pipelines.

    Features:
        - Method chaining for readability
        - Observable mocking (🎭 indicator)
        - Cycle detection before execution
    """

    def __init__(self, mode: str = "e2e"):
        """Initialize builder with test mode.

        Args:
            mode: Test mode (unit/integration/e2e)
        """
        self.mode = mode
        self.nodes = {}
        self.edges = []

    def add_node(self, name: str, strategy: Any) -> "PipelineBuilder":
        """Add node with execution strategy."""
        self.nodes[name] = strategy
        return self

    def add_edge(self, from_node: str, to_node: str) -> "PipelineBuilder":
        """Add dependency edge (from -> to)."""
        self.edges.append((from_node, to_node))
        return self

    def build(self) -> Pipeline:
        """Build pipeline and log mocked nodes."""
        # Observable mocking: Show which nodes are mocked
        mocked = [
            name for name, strategy in self.nodes.items()
            if strategy.is_mocked()
        ]

        if mocked:
            print(f"🎭 MOCKED NODES: {', '.join(mocked)}")

        return Pipeline(self.nodes, self.edges)


# ============================================================================
# Testing Pattern
# ============================================================================

def test_linear_pipeline():
    """E2E test: Linear pipeline with all mocks."""
    from strategy_testing import MockDatabaseStrategy

    pipeline = (
        PipelineBuilder(mode="e2e")
        .add_node("fetch", MockDatabaseStrategy([{"user_id": 1, "name": "Test"}]))
        .add_node("process", MockDatabaseStrategy([{"processed": True}]))
        .add_edge("fetch", "process")
        .build()
    )

    result = pipeline.execute({"user_id": 1})
    # Output: 🎭 MOCKED NODES: fetch, process
    assert result["processed"] is True


def test_dag_pipeline():
    """Integration test: DAG with parallel branches."""
    # DAG structure:
    #     parse
    #    /     \
    # research  docs
    #    \     /
    #    generate
    pass  # Simplified - shows pattern


# ============================================================================
# Key Insights
# ============================================================================

# 1. Topological Sort: Kahn's algorithm for DAG execution
# 2. Cycle Detection: Fail fast before execution
# 3. Observable Mocking: 🎭 indicator shows test mode
# 4. Fluent API: Method chaining improves readability
# 5. Composable: Build any graph structure with nodes + edges
