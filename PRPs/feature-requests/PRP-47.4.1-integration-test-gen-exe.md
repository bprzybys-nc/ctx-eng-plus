---
prp_id: PRP-47.4.1
title: Integration Test - Gen + Exe Workflow
status: planning
type: testing
complexity: low
estimated_hours: 2
priority: high
dependencies: [PRP-47.3.1, PRP-47.3.2]
batch_id: 47
stage: 5
---

# PRP-47.4.1: Integration Test - Gen + Exe Workflow

## Problem

After refactoring /batch-gen-prp (PRP-47.3.1) and /batch-exe-prp (PRP-47.3.2) to use the unified orchestrator framework, we need to verify:

- **End-to-end workflow**: Generate PRPs → Execute PRPs
- **Data flow**: Generator output → Executor input (PRP files)
- **Dependency chain**: Generated PRPs respect dependencies during execution
- **Integration points**: Orchestrator templates, subagents, dependency analyzer
- **No regressions**: Both commands work together as before

Without integration testing, we risk:
- Generated PRPs incompatible with executor expectations
- Dependency analysis inconsistencies between gen and exe
- Broken workflow requiring manual intervention
- Undiscovered edge cases

## Solution

Create comprehensive integration test suite that exercises the complete gen→exe workflow:

1. Create test batch plan (4-6 phases with dependencies)
2. Run /batch-gen-prp to generate PRPs
3. Verify generated PRPs structure and content
4. Run /batch-exe-prp to execute generated PRPs
5. Verify execution results and code changes
6. Validate end state (tests pass, no errors)

Test will use real commands (no mocks) and verify actual file system changes.

## Implementation

### Phase 1: Test Plan Creation (30 minutes)

**Create**: `tests/fixtures/batch-integration-test-plan.md`

**Content**:
```markdown
# Integration Test Batch Plan

## Overview
Test batch for validating gen→exe workflow with unified orchestrator framework.

## Phases

### Phase 1: Create Test Fixture
**Goal**: Create base test file for validation
**Estimated Hours**: 0.5
**Complexity**: low
**Files Modified**: tests/fixtures/integration_test.py
**Dependencies**: None
**Implementation Steps**:
1. Create tests/fixtures/ directory if not exists
2. Create integration_test.py with sample test function
3. Add docstring explaining purpose
4. Commit file

**Validation Gates**:
- [ ] File created at correct path
- [ ] Python syntax valid
- [ ] Imports work correctly

---

### Phase 2: Add Test Assertions
**Goal**: Add assertions to validate fixture functionality
**Estimated Hours**: 0.5
**Complexity**: low
**Files Modified**: tests/fixtures/integration_test.py
**Dependencies**: Phase 1
**Implementation Steps**:
1. Read integration_test.py
2. Add pytest test function
3. Add 3-5 assertions
4. Run pytest to verify test passes
5. Commit changes

**Validation Gates**:
- [ ] Test function follows pytest conventions
- [ ] All assertions pass
- [ ] Test output clear

---

### Phase 3: Create Helper Module
**Goal**: Create helper module for test utilities
**Estimated Hours**: 0.5
**Complexity**: low
**Files Modified**: tests/fixtures/test_helpers.py
**Dependencies**: Phase 1
**Implementation Steps**:
1. Create test_helpers.py
2. Add utility functions (file helpers, assertion helpers)
3. Add docstrings
4. Commit file

**Validation Gates**:
- [ ] Module imports successfully
- [ ] Helper functions work as expected
- [ ] No external dependencies

---

### Phase 4: Integration Test Suite
**Goal**: Create main integration test using fixtures
**Estimated Hours**: 1
**Complexity**: medium
**Files Modified**: tests/test_batch_integration_gen_exe.py
**Dependencies**: Phase 2, Phase 3
**Implementation Steps**:
1. Create test_batch_integration_gen_exe.py
2. Import fixtures from Phase 2 and Phase 3
3. Write test that uses both fixtures
4. Run test to verify integration
5. Commit test file

**Validation Gates**:
- [ ] Test imports both fixtures
- [ ] Test validates integration points
- [ ] Test passes
- [ ] Test time <5 minutes
```

**Lines**: ~90 lines

**Purpose**: This plan creates a simple 4-phase batch with dependencies that exercises:
- Sequential dependencies (Phase 1 → Phase 2)
- Parallel execution (Phase 2 and Phase 3 both depend on Phase 1)
- Multi-dependency (Phase 4 depends on Phase 2 and Phase 3)

### Phase 2: Integration Test Implementation (1 hour)

**Create**: `tests/test_batch_integration_gen_exe.py`

**Content**:
```python
"""
Integration test for batch-gen-prp + batch-exe-prp workflow.

Tests end-to-end workflow:
1. Generate PRPs from test plan
2. Execute generated PRPs
3. Verify results
"""

import pytest
import subprocess
import json
import os
from pathlib import Path


class TestBatchGenExeIntegration:
    """Test gen→exe workflow with unified orchestrator."""

    @pytest.fixture
    def test_plan_path(self, tmp_path):
        """Create test plan file."""
        plan_path = tmp_path / "test-plan.md"

        # Copy fixture plan
        fixture_plan = Path("tests/fixtures/batch-integration-test-plan.md")
        plan_path.write_text(fixture_plan.read_text())

        return plan_path

    @pytest.fixture
    def batch_id(self):
        """Use test batch ID."""
        return "999"  # Test batch ID

    def test_generate_prps(self, test_plan_path, batch_id):
        """
        Test PRP generation from plan.

        Verifies:
        - Command completes successfully
        - Correct number of PRPs generated
        - PRPs have correct structure
        - Dependencies linked correctly
        """
        # Run batch-gen-prp
        result = subprocess.run(
            ["claude", "code", f"/batch-gen-prp {test_plan_path}"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Generation failed: {result.stderr}"

        # Verify PRPs created
        prp_dir = Path(f"PRPs/feature-requests")
        generated_prps = list(prp_dir.glob(f"PRP-{batch_id}.*.md"))

        assert len(generated_prps) == 4, f"Expected 4 PRPs, got {len(generated_prps)}"

        # Verify PRP structure
        for prp_path in generated_prps:
            content = prp_path.read_text()

            # Check YAML frontmatter
            assert "prp_id:" in content
            assert "title:" in content
            assert "status: planning" in content
            assert "batch_id: 999" in content

            # Check sections
            assert "## Problem" in content
            assert "## Solution" in content
            assert "## Implementation" in content
            assert "## Validation" in content

        # Verify dependencies
        prp_1_1 = prp_dir / f"PRP-{batch_id}.1.1-create-test-fixture.md"
        prp_2_1 = prp_dir / f"PRP-{batch_id}.2.1-add-test-assertions.md"
        prp_2_2 = prp_dir / f"PRP-{batch_id}.2.2-create-helper-module.md"
        prp_3_1 = prp_dir / f"PRP-{batch_id}.3.1-integration-test-suite.md"

        # PRP-999.1.1 has no dependencies
        assert "dependencies: []" in prp_1_1.read_text()

        # PRP-999.2.1 depends on PRP-999.1.1
        assert "PRP-999.1.1" in prp_2_1.read_text()

        # PRP-999.2.2 depends on PRP-999.1.1
        assert "PRP-999.1.1" in prp_2_2.read_text()

        # PRP-999.3.1 depends on PRP-999.2.1 and PRP-999.2.2
        prp_3_1_content = prp_3_1.read_text()
        assert "PRP-999.2.1" in prp_3_1_content
        assert "PRP-999.2.2" in prp_3_1_content

    def test_execute_generated_prps(self, batch_id):
        """
        Test execution of generated PRPs.

        Verifies:
        - Command completes successfully
        - Correct execution order (dependencies respected)
        - Parallel execution in same stage
        - Checkpoint commits created
        - Validation passes
        """
        # Run batch-exe-prp
        result = subprocess.run(
            ["claude", "code", f"/batch-exe-prp --batch {batch_id}"],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Execution failed: {result.stderr}"

        # Verify checkpoint commits created
        git_log = subprocess.run(
            ["git", "log", "--oneline", "--grep", f"PRP-{batch_id}"],
            capture_output=True,
            text=True
        ).stdout

        # Should have commits for all phases
        assert f"PRP-{batch_id}.1.1" in git_log
        assert f"PRP-{batch_id}.2.1" in git_log
        assert f"PRP-{batch_id}.2.2" in git_log
        assert f"PRP-{batch_id}.3.1" in git_log

        # Verify files created
        assert Path("tests/fixtures/integration_test.py").exists()
        assert Path("tests/fixtures/test_helpers.py").exists()
        assert Path("tests/test_batch_integration_gen_exe.py").exists()

        # Verify validation passed (run tests)
        test_result = subprocess.run(
            ["pytest", "tests/fixtures/integration_test.py", "-v"],
            capture_output=True,
            text=True
        )

        assert test_result.returncode == 0, "Generated tests should pass"

    def test_full_workflow(self, test_plan_path, batch_id):
        """
        Test complete gen→exe workflow.

        This is the main integration test that runs both commands
        in sequence and verifies end-to-end behavior.
        """
        # Step 1: Generate PRPs
        gen_result = subprocess.run(
            ["claude", "code", f"/batch-gen-prp {test_plan_path}"],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes max
        )

        assert gen_result.returncode == 0, f"Generation failed: {gen_result.stderr}"
        print(f"Generation output:\n{gen_result.stdout}")

        # Step 2: Execute PRPs
        exe_result = subprocess.run(
            ["claude", "code", f"/batch-exe-prp --batch {batch_id}"],
            capture_output=True,
            text=True,
            timeout=1800  # 30 minutes max
        )

        assert exe_result.returncode == 0, f"Execution failed: {exe_result.stderr}"
        print(f"Execution output:\n{exe_result.stdout}")

        # Step 3: Verify final state
        # All PRPs should be status=completed
        prp_dir = Path("PRPs/feature-requests")
        for prp_path in prp_dir.glob(f"PRP-{batch_id}.*.md"):
            content = prp_path.read_text()
            assert "status: completed" in content, f"{prp_path.name} not marked completed"

        # All files should exist
        assert Path("tests/fixtures/integration_test.py").exists()
        assert Path("tests/fixtures/test_helpers.py").exists()

        # All tests should pass
        test_result = subprocess.run(
            ["pytest", "tests/fixtures/", "-v"],
            capture_output=True,
            text=True
        )

        assert test_result.returncode == 0, "All generated tests should pass"

        print("Integration test passed: gen→exe workflow working correctly")
```

**Lines**: ~180 lines

### Phase 3: Cleanup Utilities (20 minutes)

**Add to test_batch_integration_gen_exe.py**:

```python
    @pytest.fixture(scope="module", autouse=True)
    def cleanup(self):
        """Cleanup test artifacts after test run."""
        yield

        # Cleanup test PRPs
        prp_dir = Path("PRPs/feature-requests")
        for prp_path in prp_dir.glob("PRP-999.*.md"):
            prp_path.unlink()

        # Cleanup test files
        test_files = [
            "tests/fixtures/integration_test.py",
            "tests/fixtures/test_helpers.py"
        ]
        for file_path in test_files:
            if Path(file_path).exists():
                Path(file_path).unlink()

        # Cleanup git commits (optional, commented out by default)
        # subprocess.run(["git", "reset", "--hard", "HEAD~10"])
```

**Lines**: ~20 lines

### Phase 4: Documentation & Execution (10 minutes)

**Update**: `tests/README.md` (or create if not exists)

**Add section**:
```markdown
## Integration Tests

### Batch Gen + Exe Integration

Tests the complete workflow: generate PRPs from plan → execute PRPs.

**Test file**: `tests/test_batch_integration_gen_exe.py`

**Run**:
```bash
# Run integration test
pytest tests/test_batch_integration_gen_exe.py -v

# Run with output
pytest tests/test_batch_integration_gen_exe.py -v -s

# Run specific test
pytest tests/test_batch_integration_gen_exe.py::TestBatchGenExeIntegration::test_full_workflow -v
```

**What it tests**:
- PRP generation from test plan (4 phases)
- Dependency analysis and staging
- PRP structure and format
- Batch execution with dependencies
- Checkpoint commits
- Validation integration
- Final state verification

**Test duration**: ~5-10 minutes (generation + execution)

**Cleanup**: Test creates PRP-999.*.md files and test fixtures. Cleanup is automatic.
```

## Validation

### Pre-Implementation Checks
- [ ] PRP-47.3.1 completed (refactored /batch-gen-prp)
- [ ] PRP-47.3.2 completed (refactored /batch-exe-prp)
- [ ] pytest installed and configured
- [ ] Test fixtures directory exists

### Post-Implementation Checks
- [ ] Test plan generates 4 PRPs successfully
- [ ] All generated PRPs execute without errors
- [ ] Code changes match PRP requirements (files created)
- [ ] Tests pass for all executed PRPs (pytest success)
- [ ] No conflicts in batch merge
- [ ] Full workflow takes <10 minutes

### Test Quality Checks
- [ ] Test uses real commands (no mocks)
- [ ] Test verifies file system changes
- [ ] Test verifies git commits
- [ ] Test has cleanup (no artifacts left)
- [ ] Test output clear and informative

## Acceptance Criteria

1. **Test Coverage**
   - Tests PRP generation (structure, dependencies, format)
   - Tests PRP execution (order, checkpoints, validation)
   - Tests full gen→exe workflow
   - Tests cleanup

2. **Test Quality**
   - Uses real commands (subprocess calls)
   - Verifies actual file system changes
   - Checks git log for commits
   - Has meaningful assertions
   - Includes cleanup

3. **Test Reliability**
   - Passes consistently (no flakiness)
   - Uses isolated test batch ID (999)
   - Cleans up after itself
   - Has clear error messages

4. **Documentation**
   - README explains how to run tests
   - Test docstrings explain what's being tested
   - Output shows workflow progress

## Testing Strategy

### Unit Tests
- N/A (this PRP is the test)

### Integration Tests
- This PRP implements the integration test

### Manual Testing
```bash
# Run integration test
cd tests
pytest test_batch_integration_gen_exe.py -v -s

# Verify cleanup
ls PRPs/feature-requests/PRP-999.*.md  # Should be empty
ls tests/fixtures/integration_test.py   # Should not exist

# Run specific test
pytest test_batch_integration_gen_exe.py::TestBatchGenExeIntegration::test_full_workflow -v
```

## Risks & Mitigations

### Risk: Test takes too long (>15 minutes)
**Impact**: Slows down development, skipped frequently
**Mitigation**: Use simple 4-phase plan, parallel execution, timeout limits

### Risk: Test pollutes repository
**Impact**: Test artifacts left behind
**Mitigation**: Use unique test batch ID (999), implement cleanup fixture

### Risk: Test flakiness (intermittent failures)
**Impact**: False negatives, loss of confidence
**Mitigation**: Use deterministic test data, retry on timeout, clear assertions

### Risk: Test doesn't catch real issues
**Impact**: Bugs slip through
**Mitigation**: Verify actual file changes, check git log, run validation

### Risk: Commands change, test breaks
**Impact**: Test maintenance burden
**Mitigation**: Use stable command interface, document command format

## Dependencies

- **PRP-47.3.1**: Refactored /batch-gen-prp command
- **PRP-47.3.2**: Refactored /batch-exe-prp command

## Related PRPs

- **Tested Commands**: PRP-47.3.1 (gen), PRP-47.3.2 (exe)
- **Infrastructure**: PRP-47.1.1 (orchestrator), PRP-47.2.1 (analyzer)

## Files Modified

- `tests/fixtures/batch-integration-test-plan.md` (create)
- `tests/test_batch_integration_gen_exe.py` (create)
- `tests/README.md` (update or create)

## Notes

- Use batch ID 999 for tests (outside normal range)
- Test should be idempotent (can run multiple times)
- Cleanup is critical (don't pollute repository)
- Test duration target: <10 minutes
- This test validates entire PRP-47 Phase 1 work (foundation + refactoring)
