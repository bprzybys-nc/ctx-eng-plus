---
prp_id: PRP-47.2.2
title: Unit Tests for Dependency Analyzer
status: planning
type: testing
complexity: low
estimated_hours: 2
priority: high
dependencies: [PRP-47.2.1]
batch_id: 47
stage: 3
---

# PRP-47.2.2: Unit Tests for Dependency Analyzer

## Problem

The dependency analyzer (PRP-47.2.1) implements critical algorithms for batch operations:
- Topological sort (execution order)
- Cycle detection (avoid deadlocks)
- Stage assignment (parallel execution)
- File conflict detection (prevent race conditions)

Without comprehensive unit tests, we risk:
- Undetected edge cases causing production failures
- Regression when modifying algorithms
- Lack of confidence in correctness
- Debugging difficulty when issues arise

## Solution

Create a comprehensive unit test suite covering all dependency analyzer functionality with >90% code coverage. Tests will use real scenarios (no mocks) and validate both success cases and error handling.

Test suite will cover:
1. Topological sort (5+ graph shapes)
2. Cycle detection (4+ cycle patterns)
3. Stage assignment (4+ parallelization scenarios)
4. File conflict detection (3+ conflict patterns)
5. Edge cases (empty input, single item, self-loops)

## Implementation

### Phase 1: Test Setup & Utilities (30 minutes)

**Create**: `tests/test_dependency_analyzer.py`

**Initial Structure**:
```python
"""
Unit tests for dependency analyzer.

Tests topological sort, cycle detection, stage assignment,
and file conflict detection.
"""

import pytest
from typing import List

import sys
sys.path.insert(0, '../.ce/orchestration')

from dependency_analyzer import (
    DependencyNode,
    DependencyAnalyzer,
    CycleDetectedError,
    FileConflictError
)


def create_nodes(items: List[dict]) -> List[DependencyNode]:
    """Helper to create test nodes from dict specs."""
    return [
        DependencyNode(
            item_id=item["id"],
            dependencies=item.get("deps", []),
            files=item.get("files", [])
        )
        for item in items
    ]
```

**Lines**: ~30 lines

### Phase 2: Topological Sort Tests (30 minutes)

**Add to test_dependency_analyzer.py**:

```python
class TestTopologicalSort:
    """Test topological sort functionality."""

    def test_linear_dependency_chain(self):
        """A → B → C should sort to [A, B, C]."""
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["B"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.topological_sort()

        assert result == ["A", "B", "C"]

    def test_branching_dependencies(self):
        """
        A → B
        A → C
        B → D
        C → D

        Valid orders: [A, B, C, D] or [A, C, B, D]
        """
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["A"]},
            {"id": "D", "deps": ["B", "C"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.topological_sort()

        # Verify order respects dependencies
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("C") < result.index("D")

    def test_complex_dependencies(self):
        """
        Test 8-item graph with mixed dependencies.

        A → B → D → F
        A → C → E → G
        B → E
        D → G → H
        """
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["A"]},
            {"id": "D", "deps": ["B"]},
            {"id": "E", "deps": ["B", "C"]},
            {"id": "F", "deps": ["D"]},
            {"id": "G", "deps": ["E", "D"]},
            {"id": "H", "deps": ["G"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.topological_sort()

        # Verify all dependency constraints
        assert result.index("A") < result.index("B")
        assert result.index("A") < result.index("C")
        assert result.index("B") < result.index("D")
        assert result.index("B") < result.index("E")
        assert result.index("C") < result.index("E")
        assert result.index("D") < result.index("F")
        assert result.index("E") < result.index("G")
        assert result.index("D") < result.index("G")
        assert result.index("G") < result.index("H")

    def test_no_dependencies(self):
        """All items independent should allow any order."""
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": []},
            {"id": "C", "deps": []}
        ])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.topological_sort()

        assert set(result) == {"A", "B", "C"}
        assert len(result) == 3

    def test_single_item(self):
        """Single item with no deps."""
        nodes = create_nodes([{"id": "A", "deps": []}])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.topological_sort()

        assert result == ["A"]
```

**Lines**: ~90 lines

### Phase 3: Cycle Detection Tests (30 minutes)

**Add to test_dependency_analyzer.py**:

```python
class TestCycleDetection:
    """Test cycle detection functionality."""

    def test_simple_cycle(self):
        """A → B → A should detect cycle."""
        nodes = create_nodes([
            {"id": "A", "deps": ["B"]},
            {"id": "B", "deps": ["A"]}
        ])
        analyzer = DependencyAnalyzer(nodes)

        with pytest.raises(CycleDetectedError) as exc_info:
            analyzer.topological_sort()

        cycle_path = exc_info.value.cycle_path
        assert len(cycle_path) == 3  # A → B → A
        assert cycle_path[0] == cycle_path[-1]

    def test_three_node_cycle(self):
        """A → B → C → A should detect cycle."""
        nodes = create_nodes([
            {"id": "A", "deps": ["C"]},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["B"]}
        ])
        analyzer = DependencyAnalyzer(nodes)

        with pytest.raises(CycleDetectedError) as exc_info:
            analyzer.topological_sort()

        cycle_path = exc_info.value.cycle_path
        assert len(cycle_path) == 4  # A → B → C → A
        assert cycle_path[0] == cycle_path[-1]

    def test_self_loop(self):
        """A → A should detect cycle."""
        nodes = create_nodes([
            {"id": "A", "deps": ["A"]}
        ])
        analyzer = DependencyAnalyzer(nodes)

        with pytest.raises(CycleDetectedError) as exc_info:
            analyzer.topological_sort()

        cycle_path = exc_info.value.cycle_path
        assert cycle_path == ["A", "A"]

    def test_cycle_in_larger_graph(self):
        """
        A → B → C
        D → E → F → D (cycle)
        G

        Should detect F → D cycle even with other valid paths.
        """
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["B"]},
            {"id": "D", "deps": ["F"]},
            {"id": "E", "deps": ["D"]},
            {"id": "F", "deps": ["E"]},
            {"id": "G", "deps": []}
        ])
        analyzer = DependencyAnalyzer(nodes)

        with pytest.raises(CycleDetectedError) as exc_info:
            analyzer.topological_sort()

        # Cycle should be D → E → F → D
        cycle_path = exc_info.value.cycle_path
        assert "D" in cycle_path
        assert "E" in cycle_path
        assert "F" in cycle_path
```

**Lines**: ~70 lines

### Phase 4: Stage Assignment Tests (30 minutes)

**Add to test_dependency_analyzer.py**:

```python
class TestStageAssignment:
    """Test stage assignment for parallel execution."""

    def test_linear_stages(self):
        """A → B → C should assign to stages 1, 2, 3."""
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["B"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()

        assert stages == {
            1: ["A"],
            2: ["B"],
            3: ["C"]
        }

    def test_parallel_items_same_stage(self):
        """
        A → B
        A → C

        B and C should be in same stage (both depend only on A).
        """
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["A"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()

        assert stages[1] == ["A"]
        assert set(stages[2]) == {"B", "C"}

    def test_complex_parallelization(self):
        """
        A, B (stage 1)
        C → A (stage 2)
        D → B (stage 2)
        E → C, D (stage 3)
        """
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": []},
            {"id": "C", "deps": ["A"]},
            {"id": "D", "deps": ["B"]},
            {"id": "E", "deps": ["C", "D"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()

        assert set(stages[1]) == {"A", "B"}
        assert set(stages[2]) == {"C", "D"}
        assert stages[3] == ["E"]

    def test_all_independent_single_stage(self):
        """All independent items in stage 1."""
        nodes = create_nodes([
            {"id": "A", "deps": []},
            {"id": "B", "deps": []},
            {"id": "C", "deps": []},
            {"id": "D", "deps": []}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()

        assert len(stages) == 1
        assert set(stages[1]) == {"A", "B", "C", "D"}
```

**Lines**: ~70 lines

### Phase 5: File Conflict Detection Tests (20 minutes)

**Add to test_dependency_analyzer.py**:

```python
class TestFileConflictDetection:
    """Test file conflict detection."""

    def test_no_conflicts(self):
        """Items modifying different files."""
        nodes = create_nodes([
            {"id": "A", "deps": [], "files": ["file1.py"]},
            {"id": "B", "deps": [], "files": ["file2.py"]},
            {"id": "C", "deps": [], "files": ["file3.py"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()
        conflicts = analyzer.detect_file_conflicts(stages)

        assert conflicts == {}

    def test_conflict_same_stage(self):
        """Two items in same stage modifying same file."""
        nodes = create_nodes([
            {"id": "A", "deps": [], "files": ["file1.py"]},
            {"id": "B", "deps": [], "files": ["file1.py"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()
        conflicts = analyzer.detect_file_conflicts(stages)

        assert "file1.py" in conflicts
        assert set(conflicts["file1.py"]) == {"A", "B"}

    def test_no_conflict_different_stages(self):
        """Two items in different stages can modify same file."""
        nodes = create_nodes([
            {"id": "A", "deps": [], "files": ["file1.py"]},
            {"id": "B", "deps": ["A"], "files": ["file1.py"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()
        conflicts = analyzer.detect_file_conflicts(stages)

        assert conflicts == {}

    def test_multiple_file_conflicts(self):
        """Multiple files with conflicts."""
        nodes = create_nodes([
            {"id": "A", "deps": [], "files": ["file1.py", "file2.py"]},
            {"id": "B", "deps": [], "files": ["file1.py"]},
            {"id": "C", "deps": [], "files": ["file2.py"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        stages = analyzer.assign_stages()
        conflicts = analyzer.detect_file_conflicts(stages)

        assert "file1.py" in conflicts
        assert set(conflicts["file1.py"]) == {"A", "B"}
        assert "file2.py" in conflicts
        assert set(conflicts["file2.py"]) == {"A", "C"}
```

**Lines**: ~60 lines

### Phase 6: Edge Cases & Integration (20 minutes)

**Add to test_dependency_analyzer.py**:

```python
class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_input(self):
        """Empty node list."""
        nodes = create_nodes([])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.topological_sort()

        assert result == []

    def test_analyze_full_pipeline(self):
        """Test analyze() method with valid graph."""
        nodes = create_nodes([
            {"id": "A", "deps": [], "files": ["a.py"]},
            {"id": "B", "deps": ["A"], "files": ["b.py"]},
            {"id": "C", "deps": ["A"], "files": ["c.py"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        result = analyzer.analyze()

        assert "sorted_order" in result
        assert "stages" in result
        assert "file_conflicts" in result
        assert result["has_cycles"] is False
        assert result["has_conflicts"] is False

    def test_missing_dependency_reference(self):
        """Item references non-existent dependency (should skip)."""
        nodes = create_nodes([
            {"id": "A", "deps": ["Z"]},  # Z doesn't exist
            {"id": "B", "deps": ["A"]}
        ])
        analyzer = DependencyAnalyzer(nodes)
        # Should not crash, just ignore missing dep
        result = analyzer.topological_sort()

        assert "A" in result
        assert "B" in result
```

**Lines**: ~40 lines

### Phase 7: Coverage Report (10 minutes)

**Run tests with coverage**:
```bash
cd tests
pytest test_dependency_analyzer.py -v --cov=../. ce/orchestration/dependency_analyzer --cov-report=term-missing
```

**Expected coverage**: >90%

## Validation

### Pre-Implementation Checks
- [ ] PRP-47.2.1 completed (dependency_analyzer.py exists)
- [ ] pytest installed (`uv add --dev pytest pytest-cov`)
- [ ] Python path configured correctly (can import from .ce/orchestration)

### Post-Implementation Checks
- [ ] All test functions pass (pytest exit code 0)
- [ ] Coverage >90% (pytest-cov report)
- [ ] Test output clearly shows each scenario
- [ ] Error handling tested (CycleDetectedError, edge cases)
- [ ] No mock data - real test cases only

### Test Quality Checks
- [ ] Each test has descriptive docstring
- [ ] Test names follow pattern: test_<scenario>
- [ ] Assertions use meaningful messages
- [ ] Complex graphs documented with ASCII diagrams

## Acceptance Criteria

1. **Test Coverage**
   - >90% code coverage for dependency_analyzer.py
   - All public methods tested
   - All error paths tested

2. **Test Scenarios**
   - 5+ topological sort cases (linear, branching, complex, no deps, single item)
   - 4+ cycle detection cases (simple, multi-node, self-loop, cycle in larger graph)
   - 4+ stage assignment cases (linear, parallel, complex, all independent)
   - 3+ file conflict cases (no conflict, same stage conflict, different stage)
   - 3+ edge cases (empty, missing dep, full pipeline)

3. **Test Quality**
   - Clear test names and docstrings
   - No test data mocks (use real DependencyNode objects)
   - Assertions verify correctness, not implementation details

4. **Documentation**
   - README or docstring explains how to run tests
   - Coverage report included in test output
   - Test scenarios documented

## Testing Strategy

### Unit Tests (This PRP)
All tests in test_dependency_analyzer.py

### Integration Tests
- Defer to PRP-47.4.1 (gen + exe integration test)

### Manual Testing
```bash
# Run all tests
cd tests
pytest test_dependency_analyzer.py -v

# Run with coverage
pytest test_dependency_analyzer.py -v --cov=../.ce/orchestration/dependency_analyzer --cov-report=term-missing

# Run specific test class
pytest test_dependency_analyzer.py::TestTopologicalSort -v

# Run specific test
pytest test_dependency_analyzer.py::TestCycleDetection::test_simple_cycle -v
```

## Risks & Mitigations

### Risk: Test scenarios miss critical edge cases
**Impact**: Production failures not caught by tests
**Mitigation**: Review PRP-47.2.1 implementation, cover all branches and error paths

### Risk: False positive tests (pass when code is wrong)
**Impact**: Bugs slip through
**Mitigation**: Test assertions verify correctness (e.g., dependency order), not just execution success

### Risk: Test data too simplistic
**Impact**: Complex production graphs fail
**Mitigation**: Include 8-10 node complex graph test case

### Risk: Low coverage (<90%)
**Impact**: Untested code paths
**Mitigation**: Use pytest-cov to identify missing coverage, add targeted tests

## Dependencies

- **PRP-47.2.1**: Dependency analyzer implementation

## Related PRPs

- **Tested Code**: PRP-47.2.1 (dependency_analyzer.py)
- **Integration Tests**: PRP-47.4.1 (gen + exe)

## Files Modified

- `tests/test_dependency_analyzer.py` (create)

## Notes

- Use pytest for test runner (already in dev dependencies)
- Use pytest-cov for coverage reporting
- Keep test cases realistic (mirror actual batch scenarios)
- Document complex test graphs with ASCII diagrams
- Run tests before every commit to PRP-47 batch
