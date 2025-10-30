"""Pipeline builder for creating testable pipelines with strategy pattern.

Provides Pipeline class for execution and PipelineBuilder for construction.
Supports topological sorting for DAG execution and observable mocking.
"""

from typing import Dict, Any, List, Tuple
from .strategy import NodeStrategy


class Pipeline:
    """Executable pipeline with nodes and edges.

    Pipeline executes nodes in topological order based on dependencies (edges).
    Supports linear pipelines and DAGs with cycle detection.

    Example:
        nodes = {"parse": ParserStrategy(), "research": MockSerenaStrategy()}
        edges = [("parse", "research")]
        pipeline = Pipeline(nodes, edges)
        result = pipeline.execute({"prp_path": "test.md"})
    """

    def __init__(self, nodes: Dict[str, NodeStrategy], edges: List[Tuple[str, str]]):
        """Initialize pipeline.

        Args:
            nodes: {node_name: strategy}
            edges: [(from_node, to_node)] defining dependencies
        """
        self.nodes = nodes
        self.edges = edges

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute pipeline from start to finish.

        Args:
            input_data: Initial input to first node

        Returns:
            Final output from last node

        Raises:
            RuntimeError: If pipeline has cycles or execution fails

        Process:
            1. Topologically sort nodes by edges
            2. Execute nodes in order
            3. Pass output from node to next node
            4. Return final output
        """
        # Simple linear execution (no parallelism in MVP)
        current_data = input_data

        for node_name in self._topological_sort():
            strategy = self.nodes[node_name]
            current_data = strategy.execute(current_data)

        return current_data

    def _topological_sort(self) -> List[str]:
        """Sort nodes by dependencies (edges).

        Returns:
            Ordered list of node names

        Raises:
            RuntimeError: If pipeline has circular dependencies
        """
        # Simple implementation: assume linear pipeline for MVP
        # Future: proper topological sort for DAGs
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
            # Identify which nodes are in the cycle
            nodes_in_cycle = set(self.nodes.keys()) - set(result)
            raise RuntimeError(
                f"Pipeline has circular dependencies involving: {', '.join(sorted(nodes_in_cycle))}\n"
                f"🔧 Troubleshooting: Check edges for cycles among these nodes:\n"
                f"   Edges: {self.edges}"
            )

        return result


class PipelineBuilder:
    """Builder for creating testable pipelines with strategy pattern.

    Fluent API for building pipelines with method chaining.
    Supports observable mocking (🎭 indicator for mocked nodes).

    Example:
        pipeline = (
            PipelineBuilder(mode="e2e")
            .add_node("parse", RealParserStrategy())
            .add_node("research", MockSerenaStrategy())
            .add_edge("parse", "research")
            .build()
        )
    """

    def __init__(self, mode: str = "e2e"):
        """Initialize builder.

        Args:
            mode: Test mode (unit/integration/e2e)
                - unit: Single node, all deps mocked
                - integration: Real nodes, some deps mocked
                - e2e: All external deps mocked, internal real
        """
        self.mode = mode
        self.nodes: Dict[str, NodeStrategy] = {}
        self.edges: List[Tuple[str, str]] = []

    def add_node(self, name: str, strategy: NodeStrategy) -> "PipelineBuilder":
        """Add node with execution strategy.

        Args:
            name: Node identifier
            strategy: Execution strategy (real or mock)

        Returns:
            Self for chaining
        """
        self.nodes[name] = strategy
        return self

    def add_edge(self, from_node: str, to_node: str) -> "PipelineBuilder":
        """Add dependency edge.

        Args:
            from_node: Source node name
            to_node: Destination node name

        Returns:
            Self for chaining

        Raises:
            ValueError: If from_node or to_node not in pipeline
        """
        if from_node not in self.nodes:
            raise ValueError(
                f"from_node '{from_node}' not in pipeline\n"
                f"🔧 Troubleshooting: Add node before creating edge"
            )
        if to_node not in self.nodes:
            raise ValueError(
                f"to_node '{to_node}' not in pipeline\n"
                f"🔧 Troubleshooting: Add node before creating edge"
            )

        self.edges.append((from_node, to_node))
        return self

    def build(self) -> Pipeline:
        """Build pipeline and log mocked nodes.

        Returns:
            Executable Pipeline instance
        """
        # Identify mocked nodes for observable mocking
        mocked = [
            name for name, strategy in self.nodes.items()
            if strategy.is_mocked()
        ]

        if mocked:
            print(f"🎭 MOCKED NODES: {', '.join(mocked)}")

        return Pipeline(self.nodes, self.edges)
