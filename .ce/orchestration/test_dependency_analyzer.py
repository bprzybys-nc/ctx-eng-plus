#!/usr/bin/env python3
"""
Unit Tests for Dependency Analyzer

Test coverage:
- Topological sort (linear, branching, complex)
- Cycle detection (single, multi-node)
- Stage assignment (sequential, parallel, mixed)
- File conflict detection
- Edge cases (empty, single item)
"""

import pytest
from dependency_analyzer import DependencyAnalyzer, analyze_plan_file


class TestTopologicalSort:
    """Test topological sorting algorithm"""

    def test_linear_dependencies(self):
        """Test linear chain: 1 -> 2 -> 3"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 2"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == ["Phase 1", "Phase 2", "Phase 3"]

    def test_branching_dependencies(self):
        """Test branching: 1 -> [2, 3] -> 4"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 1"]},
            {"name": "Phase 4", "dependencies": ["Phase 2", "Phase 3"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()

        # Verify order constraints
        assert result.index("Phase 1") < result.index("Phase 2")
        assert result.index("Phase 1") < result.index("Phase 3")
        assert result.index("Phase 2") < result.index("Phase 4")
        assert result.index("Phase 3") < result.index("Phase 4")

    def test_complex_dependencies(self):
        """Test complex graph with multiple paths"""
        phases = [
            {"name": "A", "dependencies": []},
            {"name": "B", "dependencies": ["A"]},
            {"name": "C", "dependencies": ["A"]},
            {"name": "D", "dependencies": ["B"]},
            {"name": "E", "dependencies": ["B", "C"]},
            {"name": "F", "dependencies": ["D", "E"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()

        # Verify all constraints
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("B") < result.index("E")
        assert result.index("C") < result.index("E")
        assert result.index("D") < result.index("F")
        assert result.index("E") < result.index("F")

    def test_independent_phases(self):
        """Test phases with no dependencies (all independent)"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": []},
            {"name": "Phase 3", "dependencies": []},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert len(result) == 3
        assert set(result) == {"Phase 1", "Phase 2", "Phase 3"}

    def test_single_phase(self):
        """Test with single phase"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == ["Phase 1"]


class TestCycleDetection:
    """Test cycle detection algorithm"""

    def test_no_cycle(self):
        """Test that valid DAG returns None"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 2"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        cycle = analyzer.detect_cycles()
        assert cycle is None

    def test_simple_cycle_two_nodes(self):
        """Test 2-node cycle: A -> B -> A"""
        phases = [
            {"name": "Phase A", "dependencies": ["Phase B"]},
            {"name": "Phase B", "dependencies": ["Phase A"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        cycle = analyzer.detect_cycles()
        assert cycle is not None
        # Cycle should contain both phases
        assert "Phase A" in cycle
        assert "Phase B" in cycle
        # Should start and end at same node
        assert cycle[0] == cycle[-1]

    def test_simple_cycle_three_nodes(self):
        """Test 3-node cycle: A -> B -> C -> A"""
        phases = [
            {"name": "A", "dependencies": ["C"]},
            {"name": "B", "dependencies": ["A"]},
            {"name": "C", "dependencies": ["B"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        cycle = analyzer.detect_cycles()
        assert cycle is not None
        assert "A" in cycle
        assert "B" in cycle
        assert "C" in cycle

    def test_self_dependency(self):
        """Test self-loop: A -> A"""
        phases = [
            {"name": "Phase A", "dependencies": ["Phase A"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        cycle = analyzer.detect_cycles()
        assert cycle is not None
        assert cycle[0] == cycle[-1]

    def test_no_cycle_with_diamond(self):
        """Test diamond dependency (not a cycle): A -> [B, C] -> D"""
        phases = [
            {"name": "A", "dependencies": []},
            {"name": "B", "dependencies": ["A"]},
            {"name": "C", "dependencies": ["A"]},
            {"name": "D", "dependencies": ["B", "C"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        cycle = analyzer.detect_cycles()
        assert cycle is None


class TestStageAssignment:
    """Test execution stage assignment"""

    def test_linear_stages(self):
        """Test linear chain gets sequential stages: 1, 2, 3"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 2"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        stages = analyzer.assign_stages()

        assert stages["Phase 1"] == 1
        assert stages["Phase 2"] == 2
        assert stages["Phase 3"] == 3

    def test_parallel_stages(self):
        """Test parallel phases get same stage: 1 -> [2, 3] -> 4"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 1"]},
            {"name": "Phase 4", "dependencies": ["Phase 2", "Phase 3"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        stages = analyzer.assign_stages()

        # Phase 1 alone in stage 1
        assert stages["Phase 1"] == 1
        # Phase 2 and 3 both depend on 1 only, so same stage
        assert stages["Phase 2"] == stages["Phase 3"] == 2
        # Phase 4 depends on both, so next stage
        assert stages["Phase 4"] == 3

    def test_independent_phases_same_stage(self):
        """Test independent phases get stage 1"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": []},
            {"name": "Phase 3", "dependencies": []},
        ]
        analyzer = DependencyAnalyzer(phases)
        stages = analyzer.assign_stages()

        assert stages["Phase 1"] == 1
        assert stages["Phase 2"] == 1
        assert stages["Phase 3"] == 1

    def test_complex_stage_assignment(self):
        """Test complex graph: A -> [B, C] -> [D, E] -> F"""
        phases = [
            {"name": "A", "dependencies": []},
            {"name": "B", "dependencies": ["A"]},
            {"name": "C", "dependencies": ["A"]},
            {"name": "D", "dependencies": ["B"]},
            {"name": "E", "dependencies": ["C"]},
            {"name": "F", "dependencies": ["D", "E"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        stages = analyzer.assign_stages()

        # Verify stage constraints
        assert stages["A"] < stages["B"]
        assert stages["A"] < stages["C"]
        assert stages["B"] < stages["D"]
        assert stages["C"] < stages["E"]
        assert stages["D"] < stages["F"]
        assert stages["E"] < stages["F"]
        # Verify parallelism
        assert stages["B"] == stages["C"]  # Both depend only on A
        assert stages["D"] == stages["E"]  # Both depend on sibling only


class TestFileConflicts:
    """Test file conflict detection"""

    def test_no_conflicts(self):
        """Test phases with different files have no conflicts"""
        phases = [
            {"name": "Phase 1", "dependencies": [], "files_modified": ["file1.txt"]},
            {"name": "Phase 2", "dependencies": [], "files_modified": ["file2.txt"]},
            {"name": "Phase 3", "dependencies": [], "files_modified": ["file3.txt"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        conflicts = analyzer.detect_file_conflicts()
        assert len(conflicts) == 0

    def test_single_conflict(self):
        """Test two phases modifying same file"""
        phases = [
            {"name": "Phase 1", "dependencies": [], "files_modified": ["shared.txt", "file1.txt"]},
            {"name": "Phase 2", "dependencies": [], "files_modified": ["shared.txt", "file2.txt"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        conflicts = analyzer.detect_file_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]["file"] == "shared.txt"
        assert set(conflicts[0]["phases"]) == {"Phase 1", "Phase 2"}

    def test_multiple_conflicts(self):
        """Test multiple files with conflicts"""
        phases = [
            {"name": "Phase 1", "dependencies": [], "files_modified": ["shared1.txt", "shared2.txt"]},
            {"name": "Phase 2", "dependencies": [], "files_modified": ["shared1.txt", "shared2.txt"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        conflicts = analyzer.detect_file_conflicts()

        assert len(conflicts) == 2
        conflict_files = {c["file"] for c in conflicts}
        assert conflict_files == {"shared1.txt", "shared2.txt"}

    def test_triple_conflict(self):
        """Test file modified by 3 phases"""
        phases = [
            {"name": "Phase 1", "dependencies": [], "files_modified": ["triple.txt"]},
            {"name": "Phase 2", "dependencies": [], "files_modified": ["triple.txt"]},
            {"name": "Phase 3", "dependencies": [], "files_modified": ["triple.txt"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        conflicts = analyzer.detect_file_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]["count"] == 3

    def test_comma_separated_files(self):
        """Test parsing comma-separated file lists"""
        phases = [
            {"name": "Phase 1", "dependencies": [], "files_modified": "file1.txt, file2.txt"},
            {"name": "Phase 2", "dependencies": [], "files_modified": "file2.txt, file3.txt"},
        ]
        analyzer = DependencyAnalyzer(phases)
        conflicts = analyzer.detect_file_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]["file"] == "file2.txt"


class TestValidation:
    """Test comprehensive validation"""

    def test_valid_graph(self):
        """Test valid dependency graph passes validation"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        validation = analyzer.validate_dependencies()

        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_undefined_dependency(self):
        """Test error for undefined dependency"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["NonExistent"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        validation = analyzer.validate_dependencies()

        assert validation["valid"] is False
        assert len(validation["errors"]) > 0
        assert "undefined" in validation["errors"][0].lower()

    def test_circular_dependency_detected(self):
        """Test error for circular dependency"""
        phases = [
            {"name": "A", "dependencies": ["B"]},
            {"name": "B", "dependencies": ["A"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        validation = analyzer.validate_dependencies()

        assert validation["valid"] is False
        assert any("circular" in e.lower() for e in validation["errors"])

    def test_file_conflict_warning(self):
        """Test warning for file conflicts"""
        phases = [
            {"name": "Phase 1", "dependencies": [], "files_modified": ["shared.txt"]},
            {"name": "Phase 2", "dependencies": [], "files_modified": ["shared.txt"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        validation = analyzer.validate_dependencies()

        assert validation["valid"] is True  # Still valid, just warning
        assert len(validation["warnings"]) > 0
        assert "conflict" in validation["warnings"][0].lower()


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_phases_list(self):
        """Test handling empty phases list"""
        phases = []
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == []

    def test_phase_with_none_dependencies(self):
        """Test phase with None dependencies"""
        phases = [
            {"name": "Phase 1", "dependencies": None},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == ["Phase 1", "Phase 2"]

    def test_phase_with_string_none(self):
        """Test phase with string 'None' as dependency"""
        phases = [
            {"name": "Phase 1", "dependencies": "None"},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == ["Phase 1", "Phase 2"]

    def test_phase_with_empty_list(self):
        """Test phase with empty dependency list"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == ["Phase 1", "Phase 2"]

    def test_phase_missing_dependencies_key(self):
        """Test phase without dependencies key"""
        phases = [
            {"name": "Phase 1"},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        result = analyzer.topological_sort()
        assert result == ["Phase 1", "Phase 2"]


class TestHelperFunctions:
    """Test helper/convenience functions"""

    def test_analyze_plan_file_success(self):
        """Test analyze_plan_file helper function"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 2"]},
        ]
        result = analyze_plan_file(phases)

        assert result["success"] is True
        assert result["total_phases"] == 3
        assert result["total_stages"] == 3
        assert result["max_parallelism"] == 1

    def test_analyze_plan_file_with_error(self):
        """Test analyze_plan_file with cycle error"""
        phases = [
            {"name": "A", "dependencies": ["B"]},
            {"name": "B", "dependencies": ["A"]},
        ]
        result = analyze_plan_file(phases)

        assert result["success"] is False
        assert len(result["errors"]) > 0

    def test_get_summary(self):
        """Test get_summary method"""
        phases = [
            {"name": "Phase 1", "dependencies": []},
            {"name": "Phase 2", "dependencies": ["Phase 1"]},
            {"name": "Phase 3", "dependencies": ["Phase 1"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        summary = analyzer.get_summary()

        assert summary["total_phases"] == 3
        assert summary["total_stages"] == 2
        assert summary["max_parallelism"] == 2  # Phase 2 and 3 parallel


class TestRealWorldScenarios:
    """Test realistic scenarios"""

    def test_real_batch_structure(self):
        """Test realistic 10-phase batch like PRP-47"""
        phases = [
            {"name": "Phase 1: Foundation", "dependencies": [], "files_modified": [".claude/orchestrators/base-orchestrator.md"]},
            {"name": "Phase 2a: Analyzer", "dependencies": ["Phase 1: Foundation"], "files_modified": [".ce/orchestration/dependency_analyzer.py"]},
            {"name": "Phase 2b: Tests", "dependencies": ["Phase 2a: Analyzer"], "files_modified": ["tests/test_dependency_analyzer.py"]},
            {"name": "Phase 3a: Gen Refactor", "dependencies": ["Phase 1: Foundation", "Phase 2a: Analyzer"], "files_modified": [".claude/commands/batch-gen-prp.md"]},
            {"name": "Phase 3b: Exe Refactor", "dependencies": ["Phase 1: Foundation", "Phase 2a: Analyzer"], "files_modified": [".claude/commands/batch-exe-prp.md"]},
            {"name": "Phase 4: Integration Test", "dependencies": ["Phase 3a: Gen Refactor", "Phase 3b: Exe Refactor"], "files_modified": ["tests/test_batch_integration.py"]},
            {"name": "Phase 5a: Review Refactor", "dependencies": ["Phase 1: Foundation"], "files_modified": [".claude/commands/batch-peer-review.md"]},
            {"name": "Phase 5b: Context Refactor", "dependencies": ["Phase 1: Foundation"], "files_modified": [".claude/commands/batch-update-context.md"]},
            {"name": "Phase 6: Documentation", "dependencies": ["Phase 3a: Gen Refactor", "Phase 3b: Exe Refactor", "Phase 5a: Review Refactor"], "files_modified": ["PRPs/feature-requests/PRP-47-USAGE-GUIDE.md"]},
            {"name": "Phase 7: Metrics", "dependencies": ["Phase 3a: Gen Refactor"], "files_modified": [".ce/scripts/analyze-batch.py"]},
        ]

        result = analyze_plan_file(phases)

        assert result["success"] is True
        assert result["total_phases"] == 10
        assert result["total_stages"] <= 6  # Should be able to parallelize some
        assert result["max_parallelism"] >= 2  # Some phases should run in parallel

    def test_file_conflict_real_scenario(self):
        """Test file conflict detection in realistic batch"""
        phases = [
            {"name": "Phase A", "dependencies": [], "files_modified": [".claude/orchestrators/base-orchestrator.md", "shared.py"]},
            {"name": "Phase B", "dependencies": [], "files_modified": ["shared.py"]},
        ]
        analyzer = DependencyAnalyzer(phases)
        conflicts = analyzer.detect_file_conflicts()

        assert len(conflicts) == 1
        assert conflicts[0]["file"] == "shared.py"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
