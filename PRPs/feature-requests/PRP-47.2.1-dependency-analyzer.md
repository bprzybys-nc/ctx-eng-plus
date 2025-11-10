---
prp_id: PRP-47.2.1
title: Dependency Analyzer - Topological Sort & Cycle Detection
status: completed
type: feature
complexity: medium
estimated_hours: 2
priority: high
dependencies: [PRP-47.1.1]
batch_id: 47
stage: 2
completion_date: 2025-11-10
git_commit: 806d14c
notes: Implementation completed as part of PRP-47.1.1 foundation work
---

# PRP-47.2.1: Dependency Analyzer - Topological Sort & Cycle Detection

## Problem

Batch operations require dependency analysis to determine execution order and detect circular dependencies. Currently, this logic is reimplemented in each batch command with varying quality:

- /batch-gen-prp has basic stage assignment
- /batch-exe-prp lacks cycle detection
- No shared file conflict detection

Without a unified dependency analyzer, we risk:
- Circular dependency deadlocks
- Incorrect execution order
- File conflicts in parallel execution
- Code duplication across commands

## Solution

Create a reusable Python utility for dependency analysis with three core capabilities:

1. **Topological Sort**: Order items respecting dependencies
2. **Cycle Detection**: Find and report circular dependency paths
3. **Stage Assignment**: Group independent items for parallel execution
4. **File Conflict Detection**: Identify items modifying same files

The analyzer will be a standalone Python module using only stdlib (no external dependencies) and will integrate with the orchestrator template from PRP-47.1.1.

## Implementation

### Phase 1: Core Data Structures (30 minutes)

**Create**: `.ce/orchestration/dependency_analyzer.py`

**Initial Structure**:
```python
"""
Dependency analyzer for batch operations.

Provides topological sort, cycle detection, stage assignment,
and file conflict detection.
"""

from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict, deque


class DependencyNode:
    """Represents an item in the dependency graph."""

    def __init__(self, item_id: str, dependencies: List[str], files: List[str]):
        self.item_id = item_id
        self.dependencies = dependencies
        self.files = files
        self.stage = None  # Assigned during staging


class CycleDetectedError(Exception):
    """Raised when circular dependency detected."""

    def __init__(self, cycle_path: List[str]):
        self.cycle_path = cycle_path
        super().__init__(f"Circular dependency: {' -> '.join(cycle_path)}")


class FileConflictError(Exception):
    """Raised when multiple items modify same file."""

    def __init__(self, conflicts: Dict[str, List[str]]):
        self.conflicts = conflicts
        message = "\n".join(
            f"File {file}: {', '.join(items)}"
            for file, items in conflicts.items()
        )
        super().__init__(f"File conflicts detected:\n{message}")
```

**Lines**: ~40 lines

### Phase 2: Topological Sort (45 minutes)

**Add to dependency_analyzer.py**:

```python
class DependencyAnalyzer:
    """Analyzes dependencies for batch operations."""

    def __init__(self, nodes: List[DependencyNode]):
        self.nodes = {node.item_id: node for node in nodes}
        self.graph = self._build_graph()

    def _build_graph(self) -> Dict[str, List[str]]:
        """Build adjacency list from nodes."""
        graph = defaultdict(list)
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep in self.nodes:
                    graph[dep].append(node.item_id)
        return graph

    def topological_sort(self) -> List[str]:
        """
        Return items in topological order (dependencies first).

        Raises:
            CycleDetectedError: If circular dependency found

        Returns:
            List of item IDs in execution order
        """
        # Calculate in-degrees
        in_degree = {item_id: 0 for item_id in self.nodes}
        for node in self.nodes.values():
            for dep in node.dependencies:
                if dep in self.nodes:
                    in_degree[node.item_id] += 1

        # Kahn's algorithm
        queue = deque([item_id for item_id, deg in in_degree.items() if deg == 0])
        result = []

        while queue:
            item_id = queue.popleft()
            result.append(item_id)

            for neighbor in self.graph.get(item_id, []):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check for cycles
        if len(result) != len(self.nodes):
            cycle_path = self._find_cycle()
            raise CycleDetectedError(cycle_path)

        return result
```

**Lines**: ~50 lines

### Phase 3: Cycle Detection (30 minutes)

**Add to dependency_analyzer.py**:

```python
    def _find_cycle(self) -> List[str]:
        """
        Find and return a cycle path in the dependency graph.

        Uses DFS with recursion stack tracking.
        """
        visited = set()
        rec_stack = set()
        parent = {}

        def dfs(node_id: str) -> Optional[str]:
            """DFS helper. Returns cycle start node if found."""
            visited.add(node_id)
            rec_stack.add(node_id)

            for neighbor in self.graph.get(node_id, []):
                if neighbor not in visited:
                    parent[neighbor] = node_id
                    cycle_start = dfs(neighbor)
                    if cycle_start:
                        return cycle_start
                elif neighbor in rec_stack:
                    parent[neighbor] = node_id
                    return neighbor

            rec_stack.remove(node_id)
            return None

        # Try DFS from each unvisited node
        for node_id in self.nodes:
            if node_id not in visited:
                cycle_start = dfs(node_id)
                if cycle_start:
                    # Reconstruct cycle path
                    path = [cycle_start]
                    current = parent[cycle_start]
                    while current != cycle_start:
                        path.append(current)
                        current = parent[current]
                    path.append(cycle_start)
                    return list(reversed(path))

        return []
```

**Lines**: ~40 lines

### Phase 4: Stage Assignment (30 minutes)

**Add to dependency_analyzer.py**:

```python
    def assign_stages(self) -> Dict[int, List[str]]:
        """
        Assign items to stages for parallel execution.

        Items in same stage can run in parallel (no dependencies between them).

        Returns:
            Dict mapping stage number to list of item IDs
        """
        sorted_items = self.topological_sort()
        stages = defaultdict(list)
        stage_map = {}

        for item_id in sorted_items:
            node = self.nodes[item_id]

            # Stage is max(dependency stages) + 1
            max_dep_stage = 0
            for dep in node.dependencies:
                if dep in stage_map:
                    max_dep_stage = max(max_dep_stage, stage_map[dep])

            stage = max_dep_stage + 1
            stage_map[item_id] = stage
            stages[stage].append(item_id)
            node.stage = stage

        return dict(stages)
```

**Lines**: ~25 lines

### Phase 5: File Conflict Detection (30 minutes)

**Add to dependency_analyzer.py**:

```python
    def detect_file_conflicts(self, stages: Dict[int, List[str]]) -> Dict[str, List[str]]:
        """
        Detect items in same stage modifying same file.

        Args:
            stages: Output from assign_stages()

        Returns:
            Dict mapping file path to conflicting item IDs
            Empty dict if no conflicts
        """
        conflicts = defaultdict(list)

        for stage_num, item_ids in stages.items():
            file_to_items = defaultdict(list)

            for item_id in item_ids:
                node = self.nodes[item_id]
                for file_path in node.files:
                    file_to_items[file_path].append(item_id)

            # Record conflicts (multiple items touching same file)
            for file_path, items in file_to_items.items():
                if len(items) > 1:
                    conflicts[file_path] = items

        return dict(conflicts)

    def analyze(self) -> Dict:
        """
        Run complete analysis.

        Returns:
            Dict with sorted order, stages, and conflicts

        Raises:
            CycleDetectedError: If circular dependency found
        """
        sorted_order = self.topological_sort()
        stages = self.assign_stages()
        conflicts = self.detect_file_conflicts(stages)

        return {
            "sorted_order": sorted_order,
            "stages": stages,
            "file_conflicts": conflicts,
            "has_cycles": False,
            "has_conflicts": len(conflicts) > 0
        }
```

**Lines**: ~45 lines

### Phase 6: CLI Interface & Testing (30 minutes)

**Add to dependency_analyzer.py**:

```python
def main():
    """CLI interface for testing."""
    import json
    import sys

    if len(sys.argv) != 2:
        print("Usage: python dependency_analyzer.py <input.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)

    nodes = [
        DependencyNode(
            item_id=item["id"],
            dependencies=item.get("dependencies", []),
            files=item.get("files", [])
        )
        for item in data["items"]
    ]

    analyzer = DependencyAnalyzer(nodes)

    try:
        result = analyzer.analyze()
        print(json.dumps(result, indent=2))
    except CycleDetectedError as e:
        print(json.dumps({
            "error": "circular_dependency",
            "cycle_path": e.cycle_path
        }, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
```

**Lines**: ~30 lines

**Total**: ~230 lines

## Validation

### Pre-Implementation Checks
- [ ] Verify `.ce/orchestration/` directory exists (create if needed)
- [ ] Review PRP-47.1.1 orchestrator template for integration points
- [ ] Check Python version compatibility (Python 3.8+)

### Post-Implementation Checks
- [ ] Topological sort works correctly (test with 5+ test cases)
- [ ] Cycle detection returns cycle path (verify error message format)
- [ ] Stage assignment maximizes parallelism (independent items in same stage)
- [ ] File conflict detection accurate (detects all conflicts, no false positives)
- [ ] No dependencies on external packages (stdlib only)
- [ ] Code follows KISS principle (simple, readable)

### Algorithm Validation
- [ ] Kahn's algorithm implementation correct
- [ ] DFS cycle detection handles all graph shapes (linear, branching, complex)
- [ ] Stage assignment respects all dependencies
- [ ] File conflict detection checks all stages

## Acceptance Criteria

1. **Correctness**
   - Topological sort produces valid dependency order
   - Cycle detection finds all circular dependencies
   - Stage assignment groups all independent items
   - File conflict detection finds all conflicts

2. **Error Handling**
   - CycleDetectedError includes complete cycle path
   - FileConflictError lists all conflicting items
   - Invalid input handled gracefully

3. **Performance**
   - Handles batches with 20+ items efficiently (<1 second)
   - Memory usage scales linearly with graph size

4. **Integration**
   - CLI interface for standalone testing
   - Clean API for orchestrator integration
   - JSON input/output format

## Testing Strategy

### Unit Tests
Defer to PRP-47.2.2 (comprehensive unit test suite)

### Manual Testing
1. Create test JSON files with various dependency patterns:
   - Linear: A → B → C
   - Branching: A → B, A → C, B → D, C → D
   - Complex: 8-10 items with mixed dependencies
   - Cycle: A → B → C → A

2. Test CLI interface:
```bash
cd .ce/orchestration
python dependency_analyzer.py test-linear.json
python dependency_analyzer.py test-branching.json
python dependency_analyzer.py test-cycle.json
```

3. Verify outputs:
   - sorted_order respects dependencies
   - stages groups independent items
   - file_conflicts detected correctly
   - cycle_path shows complete cycle

### Integration Testing
- Defer to PRP-47.3.1 (first consumer: /batch-gen-prp)

## Risks & Mitigations

### Risk: Algorithm complexity too high
**Impact**: Slow performance on large batches (20+ items)
**Mitigation**: Use Kahn's algorithm (O(V+E)) - optimal for topological sort

### Risk: False positive file conflicts
**Impact**: Commands unnecessarily serialized
**Mitigation**: Exact file path matching, case-sensitive comparison

### Risk: Missing edge cases in cycle detection
**Impact**: Circular dependencies not caught, deadlock
**Mitigation**: Test with 5+ graph shapes (linear, branching, self-loop, multi-cycle)

### Risk: Integration issues with orchestrator
**Impact**: Refactoring PRPs blocked
**Mitigation**: Design clean API, provide JSON examples, coordinate with PRP-47.1.1

## Dependencies

- **PRP-47.1.1**: Base orchestrator template (defines integration contract)

## Related PRPs

- **Testing**: PRP-47.2.2 (unit tests for this module)
- **Consumers**: PRP-47.3.1 (gen), PRP-47.3.2 (exe), PRP-47.5.1 (review), PRP-47.5.2 (context-update)

## Files Modified

- `.ce/orchestration/dependency_analyzer.py` (create)

## Notes

- Keep implementation pure Python (no numpy, networkx, or other dependencies)
- Focus on correctness over optimization (batches are typically <20 items)
- Use descriptive variable names (readability > brevity)
- Include docstrings for all public methods
- CLI interface useful for debugging and testing
