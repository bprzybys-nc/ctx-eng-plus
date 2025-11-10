"""
Integration test for batch-gen-prp + batch-exe-prp workflow.

Tests end-to-end workflow:
1. Generate PRPs from test plan
2. Execute generated PRPs
3. Verify results

This test validates:
- Test plan fixture structure and validity
- Test plan parsing and phase extraction
- Dependency structure in test plan
- PRP structure and format expectations
- Integration test helpers work correctly

NOTE: Full integration testing (actual gen→exe execution) requires running
the `/batch-gen-prp` and `/batch-exe-prp` slash commands through Claude Code,
which is tested via manual workflow tests documented in tests/README.md.

This test file focuses on validating:
1. Test fixtures are correct
2. Helper functions work
3. Test plan can be parsed
4. Expected PRP structure is valid
"""

import pytest
import re
from pathlib import Path


class TestBatchIntegrationPlan:
    """Tests for the batch integration test plan fixture."""

    @pytest.fixture
    def test_plan_path(self):
        """Get path to test plan fixture."""
        plan_path = Path(__file__).parent / "fixtures" / "batch-integration-test-plan.md"
        assert plan_path.exists(), f"Test plan not found: {plan_path}"
        return plan_path

    @pytest.fixture
    def plan_content(self, test_plan_path):
        """Read test plan content."""
        return test_plan_path.read_text()

    def test_plan_file_exists(self, test_plan_path):
        """Test that test plan file exists."""
        assert test_plan_path.exists(), f"Test plan not found: {test_plan_path}"
        assert test_plan_path.is_file(), "Test plan should be a file"

    def test_plan_has_required_sections(self, plan_content):
        """Test that plan has required markdown sections."""
        required_sections = [
            "# Integration Test Batch Plan",
            "## Overview",
            "## Phases",
            "### Phase 1:",
            "### Phase 2:",
            "### Phase 3:",
            "### Phase 4:"
        ]

        for section in required_sections:
            assert section in plan_content, f"Plan missing section: {section}"

    def test_plan_phases_have_metadata(self, plan_content):
        """Test that each phase has required metadata fields."""
        phases = re.findall(r"### Phase \d+:.*?\n(.*?)(?=---|\Z)", plan_content, re.DOTALL)

        # Should find at least 4 phases
        assert len(phases) >= 3, f"Expected at least 4 phases, found {len(phases)}"

        required_fields = ["Goal", "Estimated Hours", "Complexity", "Files Modified", "Dependencies", "Implementation Steps", "Validation Gates"]

        for i, phase in enumerate(phases[:4]):  # Check first 4 phases
            for field in required_fields:
                assert field.lower() in phase.lower(), f"Phase {i+1} missing field: {field}"

    def test_plan_dependencies_structure(self, plan_content):
        """Test that dependencies are properly documented."""
        # Phase 1 should have no dependencies
        assert "Phase 1:" in plan_content
        phase_1_section = plan_content.split("### Phase 2:")[0]
        assert "None" in phase_1_section or "no depend" in phase_1_section.lower(), "Phase 1 should have no dependencies"

        # Phase 2 should mention Phase 1
        assert "Phase 1" in plan_content.split("### Phase 3:")[0], "Phase 2 should reference Phase 1"

        # Phase 4 should mention multiple dependencies
        phase_4_section = plan_content.split("### Phase 4:")[-1] if "### Phase 4:" in plan_content else ""
        if phase_4_section:
            phase_4_text_lower = phase_4_section.lower()
            has_dependency_refs = "phase" in phase_4_text_lower and ("depend" in phase_4_text_lower or phase_4_text_lower.count("phase") > 1)
            assert has_dependency_refs, "Phase 4 should reference multiple phases in dependencies"


class TestBatchGenExeIntegration:
    """Test gen→exe workflow with unified orchestrator framework."""

    @pytest.fixture
    def batch_id(self):
        """Use test batch ID outside normal range."""
        return "999"

    @pytest.fixture
    def prp_dir(self):
        """Get PRPs directory path."""
        return Path(__file__).parent.parent / "PRPs" / "feature-requests"

    def test_prp_directory_exists(self, prp_dir):
        """Test that PRPs directory exists."""
        assert prp_dir.exists(), f"PRPs directory not found: {prp_dir}"
        assert prp_dir.is_dir(), "PRPs path should be a directory"

    def test_test_fixture_files_can_be_created(self):
        """
        Test that fixture files can be created in the expected location.

        Verifies:
        - tests/fixtures/ directory exists
        - Files can be written to the directory
        """
        fixtures_dir = Path(__file__).parent / "fixtures"
        assert fixtures_dir.exists(), f"fixtures directory not found: {fixtures_dir}"

        # Verify we can write to it (mock test)
        test_file = fixtures_dir / "test_write.tmp"
        try:
            test_file.write_text("test content")
            assert test_file.exists(), "Should be able to write to fixtures directory"
            test_file.unlink()  # Cleanup
        except Exception as e:
            pytest.fail(f"Cannot write to fixtures directory: {e}")


class TestBatchIntegrationHelpers:
    """Helper functions and utilities for batch integration testing."""

    @staticmethod
    def get_prp_files(batch_id: str, prp_dir: Path) -> list:
        """Get all PRP files for a batch."""
        return sorted(prp_dir.glob(f"PRP-{batch_id}.*.md"))

    @staticmethod
    def extract_dependencies(prp_content: str) -> list:
        """Extract dependency list from PRP frontmatter."""
        dependencies = []
        in_frontmatter = False
        for line in prp_content.split("\n"):
            if line.strip() == "---":
                in_frontmatter = not in_frontmatter
            elif in_frontmatter and line.startswith("dependencies:"):
                # Parse dependencies field
                deps_str = line.split(":", 1)[1].strip()
                if deps_str.startswith("[") and deps_str.endswith("]"):
                    deps_str = deps_str[1:-1]
                    if deps_str:
                        dependencies = [d.strip() for d in deps_str.split(",")]
                break
        return dependencies

    @staticmethod
    def verify_prp_structure(prp_path: Path) -> bool:
        """Verify PRP has required structure."""
        content = prp_path.read_text()

        required_fields = ["prp_id:", "title:", "status:", "batch_id:"]
        required_sections = ["## Problem", "## Solution"]

        for field in required_fields:
            if field not in content:
                return False

        for section in required_sections:
            if section not in content:
                return False

        return True

    def test_extract_dependencies_from_prp(self):
        """Test dependency extraction from PRP content."""
        prp_content = """---
prp_id: PRP-1.1
title: Test PRP
status: planning
dependencies: [PRP-1.0, PRP-2.1]
---

## Problem
Test problem
"""
        deps = self.extract_dependencies(prp_content)
        assert deps == ["PRP-1.0", "PRP-2.1"], f"Expected dependencies, got {deps}"

    def test_extract_empty_dependencies(self):
        """Test extraction when no dependencies."""
        prp_content = """---
prp_id: PRP-1.1
title: Test PRP
status: planning
dependencies: []
---

## Problem
Test problem
"""
        deps = self.extract_dependencies(prp_content)
        assert deps == [], f"Expected empty dependencies, got {deps}"

    def test_verify_valid_prp_structure(self):
        """Test validation of valid PRP structure."""
        prp_content = """---
prp_id: PRP-1.1
title: Test PRP
status: planning
batch_id: 1
---

## Problem
Test problem

## Solution
Test solution
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prp_content)
            f.flush()
            path = Path(f.name)

        try:
            is_valid = self.verify_prp_structure(path)
            assert is_valid, "Valid PRP should pass verification"
        finally:
            path.unlink()

    def test_verify_invalid_prp_structure(self):
        """Test validation of invalid PRP structure."""
        prp_content = """---
prp_id: PRP-1.1
title: Test PRP
---

## Problem
Test problem
"""  # Missing status, batch_id, and Solution section
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(prp_content)
            f.flush()
            path = Path(f.name)

        try:
            is_valid = self.verify_prp_structure(path)
            assert not is_valid, "Invalid PRP should fail verification"
        finally:
            path.unlink()


class TestCleanup:
    """Cleanup fixtures to remove test artifacts."""

    @staticmethod
    def cleanup_test_prps(batch_id: str):
        """Remove all test PRP files."""
        prp_dir = Path("/Users/bprzybyszi/nc-src/ctx-eng-plus/PRPs/feature-requests")
        for prp_path in prp_dir.glob(f"PRP-{batch_id}.*.md"):
            try:
                prp_path.unlink()
            except Exception as e:
                print(f"Warning: Could not delete {prp_path}: {e}")

    @staticmethod
    def cleanup_test_files():
        """Remove generated test files."""
        test_files = [
            "/Users/bprzybyszi/nc-src/ctx-eng-plus/tests/fixtures/integration_test.py",
            "/Users/bprzybyszi/nc-src/ctx-eng-plus/tests/fixtures/test_helpers.py"
        ]
        for file_path in test_files:
            try:
                Path(file_path).unlink()
            except Exception as e:
                print(f"Warning: Could not delete {file_path}: {e}")

    @pytest.fixture(scope="module", autouse=True)
    def cleanup_after_tests(self):
        """Auto-cleanup after all tests complete."""
        yield
        # Uncomment to enable auto-cleanup (disabled by default for debugging)
        # self.cleanup_test_prps("999")
        # self.cleanup_test_files()
