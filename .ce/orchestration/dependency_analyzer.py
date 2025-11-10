#!/usr/bin/env python3
"""
Dependency Analyzer - Topological Sort & Cycle Detection

Analyzes phase dependencies to:
1. Detect circular dependencies
2. Assign stages for parallel execution
3. Identify file conflicts between parallel phases
4. Validate dependency graph before execution
"""

from typing import Dict, List, Set, Optional, Tuple
from collections import defaultdict, deque


class DependencyAnalyzer:
    """Analyzes dependencies and assigns execution stages"""

    def __init__(self, phases: List[Dict]) -> None:
        """
        Initialize analyzer with list of phases.

        Args:
            phases: List of phase dicts with 'name' and 'dependencies' keys
        """
        self.phases = phases
        self.phase_names = {p["name"] for p in phases}
        self.dependency_graph = self._build_graph()

    def _build_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph: phase_name -> list of dependencies"""
        graph = defaultdict(list)

        for phase in self.phases:
            name = phase["name"]
            dependencies = phase.get("dependencies", [])

            # Handle None or "None" string
            if dependencies is None or dependencies == [] or dependencies == "None":
                graph[name] = []
            elif isinstance(dependencies, str):
                # Parse comma-separated or single dependency
                deps = [d.strip() for d in dependencies.split(",") if d.strip()]
                graph[name] = deps
            else:
                graph[name] = dependencies

        return dict(graph)

    def detect_cycles(self) -> Optional[List[str]]:
        """
        Detect circular dependencies using DFS.

        Returns:
            None if no cycles, else list representing cycle path
            Example: ["Phase 1", "Phase 2", "Phase 3", "Phase 1"]
        """
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.dependency_graph.get(node, []):
                if neighbor not in visited:
                    result = dfs(neighbor, path.copy())
                    if result:
                        return result
                elif neighbor in rec_stack:
                    # Found cycle: return path up to start + cycle back
                    cycle_start_idx = path.index(neighbor)
                    return path[cycle_start_idx:] + [neighbor]

            rec_stack.remove(node)
            return None

        # Check all nodes (in case of disconnected components)
        for node in self.phase_names:
            if node not in visited:
                cycle = dfs(node, [])
                if cycle:
                    return cycle

        return None

    def topological_sort(self) -> List[str]:
        """
        Topological sort using Kahn's algorithm.

        Returns:
            List of phase names in topological order
            Raises ValueError if cycle detected
        """
        # Check for cycles first
        cycle = self.detect_cycles()
        if cycle:
            raise ValueError(
                f"Circular dependency detected: {' → '.join(cycle)}"
            )

        # Calculate in-degrees
        in_degree = {phase: 0 for phase in self.phase_names}
        for phase in self.phase_names:
            for dep in self.dependency_graph.get(phase, []):
                if dep in in_degree:
                    in_degree[phase] += 1

        # Find all nodes with no incoming edges
        queue = deque([phase for phase in self.phase_names if in_degree[phase] == 0])
        topo_order = []

        while queue:
            current = queue.popleft()
            topo_order.append(current)

            # For each dependent of current node
            for phase in self.phase_names:
                if current in self.dependency_graph.get(phase, []):
                    in_degree[phase] -= 1
                    if in_degree[phase] == 0:
                        queue.append(phase)

        if len(topo_order) != len(self.phase_names):
            raise ValueError("Topological sort failed - unreachable nodes")

        return topo_order

    def assign_stages(self) -> Dict[str, int]:
        """
        Assign execution stages to phases.

        Phases with no dependencies are Stage 1.
        Phases can run in same stage if they have no dependencies on each other.

        Returns:
            Dict mapping phase_name -> stage_number (1-indexed)
        """
        topo_order = self.topological_sort()
        stage_assignment = {}
        current_stage = 1

        while topo_order:
            # Find phases that can run in current stage (no deps on already-processed phases)
            available = []

            for phase in topo_order:
                deps = self.dependency_graph.get(phase, [])
                # Check if all dependencies have been assigned
                if all(dep in stage_assignment for dep in deps):
                    available.append(phase)

            if not available:
                raise ValueError("Cannot assign stages - dependency deadlock")

            # Assign all available phases to current stage
            for phase in available:
                stage_assignment[phase] = current_stage
                topo_order.remove(phase)

            current_stage += 1

        return stage_assignment

    def detect_file_conflicts(self) -> List[Dict]:
        """
        Detect when multiple phases modify the same file.

        Returns:
            List of conflict dicts: {"file": path, "phases": [phase1, phase2, ...]}
        """
        file_phases = defaultdict(list)

        for phase in self.phases:
            files = phase.get("files_modified", [])
            if isinstance(files, str):
                files = [f.strip() for f in files.split(",")]

            for file in files:
                file_phases[file].append(phase["name"])

        # Find conflicts (files with multiple phases)
        conflicts = []
        for file, phases in file_phases.items():
            if len(phases) > 1:
                conflicts.append({
                    "file": file,
                    "phases": phases,
                    "count": len(phases)
                })

        return conflicts

    def validate_dependencies(self) -> Dict[str, any]:
        """
        Comprehensive validation of dependency graph.

        Returns:
            Dict with validation results:
            {
                "valid": bool,
                "errors": [error messages],
                "warnings": [warning messages]
            }
        """
        errors = []
        warnings = []

        # Check for undefined dependencies
        for phase in self.phases:
            name = phase["name"]
            deps = self.dependency_graph.get(name, [])

            for dep in deps:
                if dep not in self.phase_names:
                    errors.append(f"Phase '{name}' depends on undefined phase '{dep}'")

        # Check for cycles
        cycle = self.detect_cycles()
        if cycle:
            errors.append(f"Circular dependency: {' → '.join(cycle)}")

        # Check for file conflicts
        conflicts = self.detect_file_conflicts()
        for conflict in conflicts:
            phases_str = ", ".join(conflict["phases"])
            warnings.append(
                f"File conflict: '{conflict['file']}' modified by {phases_str}"
            )

        # Check for phases with no dependents (possible dead code)
        dependents = defaultdict(int)
        for phase in self.phases:
            for dep in self.dependency_graph.get(phase["name"], []):
                dependents[dep] += 1

        for phase in self.phases:
            if phase["name"] not in dependents and len(self.phases) > 1:
                warnings.append(f"Phase '{phase['name']}' has no dependents (possibly unused)")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "conflict_count": len(conflicts),
            "conflicts": conflicts
        }

    def get_summary(self) -> Dict:
        """Get analysis summary"""
        topo_order = self.topological_sort()
        stage_assignment = self.assign_stages()
        max_stage = max(stage_assignment.values()) if stage_assignment else 0

        # Count phases per stage
        phases_per_stage = defaultdict(list)
        for phase, stage in stage_assignment.items():
            phases_per_stage[stage].append(phase)

        return {
            "total_phases": len(self.phases),
            "total_stages": max_stage,
            "topological_order": topo_order,
            "stage_assignment": stage_assignment,
            "phases_per_stage": dict(phases_per_stage),
            "parallelism": max(len(p) for p in phases_per_stage.values()) if phases_per_stage else 0,
        }


def analyze_plan_file(phases: List[Dict]) -> Dict:
    """
    Analyze a list of phases and return comprehensive report.

    Args:
        phases: List of phase dicts with 'name', 'dependencies', 'files_modified', etc.

    Returns:
        Analysis report dict
    """
    analyzer = DependencyAnalyzer(phases)

    validation = analyzer.validate_dependencies()
    if not validation["valid"]:
        return {
            "success": False,
            "errors": validation["errors"],
            "warnings": validation["warnings"]
        }

    summary = analyzer.get_summary()

    return {
        "success": True,
        "total_phases": summary["total_phases"],
        "total_stages": summary["total_stages"],
        "topological_order": summary["topological_order"],
        "stage_assignment": summary["stage_assignment"],
        "phases_per_stage": summary["phases_per_stage"],
        "max_parallelism": summary["parallelism"],
        "file_conflicts": validation["conflicts"],
        "warnings": validation["warnings"]
    }


if __name__ == "__main__":
    # Example usage
    test_phases = [
        {"name": "Phase 1", "dependencies": [], "files_modified": [".claude/orchestrators/base-orchestrator.md"]},
        {"name": "Phase 2a", "dependencies": ["Phase 1"], "files_modified": [".ce/orchestration/dependency_analyzer.py"]},
        {"name": "Phase 2b", "dependencies": ["Phase 1"], "files_modified": ["tests/test_dependency_analyzer.py"]},
        {"name": "Phase 3", "dependencies": ["Phase 2a", "Phase 2b"], "files_modified": [".claude/commands/batch-gen-prp.md"]},
    ]

    result = analyze_plan_file(test_phases)

    if result["success"]:
        print("✓ Dependency analysis successful")
        print(f"  Total phases: {result['total_phases']}")
        print(f"  Total stages: {result['total_stages']}")
        print(f"  Max parallelism: {result['max_parallelism']} phases/stage")
        print(f"\nPhases per stage:")
        for stage, phases in result["phases_per_stage"].items():
            print(f"  Stage {stage}: {', '.join(phases)}")
    else:
        print("✗ Dependency analysis failed:")
        for error in result["errors"]:
            print(f"  ERROR: {error}")
