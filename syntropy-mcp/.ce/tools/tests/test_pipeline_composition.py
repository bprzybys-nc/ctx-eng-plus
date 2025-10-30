"""Exemplar tests demonstrating unit/integration/E2E patterns.

These tests demonstrate the three testing patterns enabled by the strategy framework:
1. Unit: Single node in isolation
2. Integration: Subgraph with real + mock components
3. E2E: Full pipeline with all external deps mocked
"""

import pytest
from pathlib import Path

from ce.testing.builder import PipelineBuilder
from ce.testing.mocks import MockSerenaStrategy, MockLLMStrategy, MockContext7Strategy
from ce.testing.real_strategies import RealParserStrategy, RealCommandStrategy


class TestUnitPattern:
    """Unit tests: Single node in isolation with mocked dependencies."""

    def test_mock_serena_returns_canned_data(self):
        """Unit test: Mock strategy returns expected data."""
        strategy = MockSerenaStrategy(canned_results=[
            {"file": "test.py", "match": "def test(): pass"}
        ])

        result = strategy.execute({"pattern": "def test"})

        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["file"] == "test.py"
        assert strategy.is_mocked() is True

    def test_mock_context7_returns_cached_docs(self):
        """Unit test: Mock Context7 returns cached documentation."""
        strategy = MockContext7Strategy(cached_docs="pytest fixtures allow...")

        result = strategy.execute({"library": "pytest", "topic": "fixtures"})

        assert result["success"] is True
        assert result["docs"] == "pytest fixtures allow..."
        assert strategy.is_mocked() is True

    def test_real_parser_parses_blueprint(self, tmp_path):
        """Unit test: Real parser with fixture PRP file."""
        # Create test PRP file
        prp_file = tmp_path / "test.md"
        prp_file.write_text("""
## 🔧 Implementation Blueprint

### Phase 1: Test Phase (2 hours)

**Goal**: Test implementation

**Approach**: Simple approach

**Files to Create**:
- `test.py` - Test file

**Key Functions**:
```python
def test(): pass
```

**Validation Command**: `pytest test.py -v`

**Checkpoint**: `git commit -m "test"`
        """)

        strategy = RealParserStrategy()
        result = strategy.execute({"prp_path": str(prp_file)})

        assert result["success"] is True
        assert len(result["phases"]) == 1
        assert result["phases"][0]["phase_name"] == "Test Phase"
        assert result["phases"][0]["hours"] == 2.0


class TestIntegrationPattern:
    """Integration tests: Subgraph with real + mock components."""

    def test_parse_and_mock_research(self, tmp_path, capsys):
        """Integration: Real parser → Mock Serena."""
        # Create test PRP
        prp_file = tmp_path / "test.md"
        prp_file.write_text("""
## 🔧 Implementation Blueprint

### Phase 1: Implementation (3 hours)

**Goal**: Implement feature

**Approach**: Class-based

**Files to Create**:
- `feature.py` - Main file

**Key Functions**:
```python
def main(): pass
```

**Validation Command**: `pytest tests/ -v`

**Checkpoint**: `git commit -m "feat"`
        """)

        # Build pipeline: Real parser + Mock research
        pipeline = (
            PipelineBuilder(mode="integration")
            .add_node("parse", RealParserStrategy())
            .add_node("research", MockSerenaStrategy(canned_results=[
                {"file": "similar.py", "pattern": "class Feature"}
            ]))
            .add_edge("parse", "research")
            .build()
        )

        # Verify observable mocking
        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES: research" in captured.out

        # Execute pipeline
        result = pipeline.execute({"prp_path": str(prp_file)})

        assert result["success"] is True
        assert "results" in result
        assert len(result["results"]) == 1

    def test_real_command_with_mock_llm_processing(self, capsys):
        """Integration: Real command → Mock LLM processing."""
        # Custom mock that uses command output
        class ProcessCommandOutputStrategy:
            def is_mocked(self):
                return True

            def execute(self, input_data):
                stdout = input_data.get("stdout", "")
                return {
                    "success": True,
                    "response": f"Processed: {stdout.strip()}",
                    "method": "mock_process"
                }

        # Build pipeline: Real command + Mock LLM
        pipeline = (
            PipelineBuilder(mode="integration")
            .add_node("command", RealCommandStrategy())
            .add_node("process", ProcessCommandOutputStrategy())
            .add_edge("command", "process")
            .build()
        )

        # Verify observable mocking
        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES: process" in captured.out

        # Execute: run echo command, then mock-process output
        result = pipeline.execute({
            "cmd": "echo 'test output'"
        })

        assert result["success"] is True
        assert "response" in result
        assert "Processed: test output" in result["response"]


class TestE2EPattern:
    """E2E tests: Full pipeline with all external deps mocked."""

    def test_full_prp_generation_pipeline(self, tmp_path, capsys):
        """E2E: Parser → Serena → Context7 → LLM (all mocked except parser)."""
        # Create test initial PRP file
        initial_file = tmp_path / "INITIAL.md"
        initial_file.write_text("""
## 🔧 Implementation Blueprint

### Phase 1: Research (2 hours)

**Goal**: Research existing patterns

**Approach**: Search codebase

**Files to Create**:
- `research.md` - Findings

**Key Functions**:
```python
def research(): pass
```

**Validation Command**: `pytest tests/ -v`

**Checkpoint**: `git commit -m "research"`
        """)

        # Custom mock LLM that uses phases data
        class MockPRPGenerator:
            def is_mocked(self):
                return True

            def execute(self, input_data):
                # Use docs from previous node
                docs = input_data.get("docs", "")
                return {
                    "success": True,
                    "response": f"# PRP-XX\n\nGenerated from docs: {docs[:20]}...",
                    "method": "mock_llm",
                    "tokens_saved": 5000
                }

        # Build E2E pipeline with mocks
        pipeline = (
            PipelineBuilder(mode="e2e")
            .add_node("parse", RealParserStrategy())
            .add_node("research", MockSerenaStrategy(canned_results=[
                {"file": "test.py", "match": "def test(): pass"}
            ]))
            .add_node("docs", MockContext7Strategy(cached_docs="pytest fixtures..."))
            .add_node("generate", MockPRPGenerator())
            .add_edge("parse", "research")
            .add_edge("research", "docs")
            .add_edge("docs", "generate")
            .build()
        )

        # Verify observable mocking
        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES:" in captured.out
        assert "research" in captured.out
        assert "docs" in captured.out
        assert "generate" in captured.out

        # Execute full pipeline
        result = pipeline.execute({
            "prp_path": str(initial_file)
        })

        assert result["success"] is True
        assert "response" in result
        assert "# PRP-" in result["response"]
        assert "tokens_saved" in result
        assert result["tokens_saved"] == 5000

    def test_e2e_validation_pipeline(self, tmp_path, capsys):
        """E2E: Parse → Command (mocked) → LLM analysis (mocked)."""
        # Create test PRP
        prp_file = tmp_path / "test.md"
        prp_file.write_text("""
## 🔧 Implementation Blueprint

### Phase 1: Validation (1 hour)

**Goal**: Run tests

**Approach**: Pytest

**Files to Create**:
- `tests/test_feature.py` - Tests

**Key Functions**:
```python
def test_feature(): pass
```

**Validation Command**: `pytest tests/ -v`

**Checkpoint**: `git commit -m "tests"`
        """)

        # Mock command strategy that simulates test run
        class MockCommandStrategy:
            def is_mocked(self):
                return True

            def execute(self, input_data):
                return {
                    "success": True,
                    "stdout": "5 passed",
                    "stderr": "",
                    "exit_code": 0
                }

        # Mock analyzer that uses command output
        class MockAnalyzer:
            def is_mocked(self):
                return True

            def execute(self, input_data):
                stdout = input_data.get("stdout", "")
                return {
                    "success": True,
                    "response": f"Analysis: {stdout}",
                    "method": "mock_llm"
                }

        # Build E2E validation pipeline
        pipeline = (
            PipelineBuilder(mode="e2e")
            .add_node("parse", RealParserStrategy())
            .add_node("validate", MockCommandStrategy())
            .add_node("analyze", MockAnalyzer())
            .add_edge("parse", "validate")
            .add_edge("validate", "analyze")
            .build()
        )

        # Verify observable mocking
        captured = capsys.readouterr()
        assert "🎭 MOCKED NODES:" in captured.out

        # Execute pipeline
        result = pipeline.execute({
            "prp_path": str(prp_file)
        })

        assert result["success"] is True
        assert "response" in result
        assert "Analysis: 5 passed" in result["response"]


class TestCompositionFlexibility:
    """Test composition patterns can be mixed and matched."""

    def test_switch_between_real_and_mock_strategies(self, tmp_path):
        """Test same pipeline can use real or mock strategies interchangeably."""
        prp_file = tmp_path / "test.md"
        prp_file.write_text("""
## 🔧 Implementation Blueprint

### Phase 1: Test (1 hour)

**Goal**: Test

**Approach**: Simple

**Files to Create**:
- `test.py` - Test

**Key Functions**:
```python
def test(): pass
```

**Validation Command**: `pytest test.py`

**Checkpoint**: `git commit -m "test"`
        """)

        # Real command strategy wrapper
        class RealCommandWithContext:
            def is_mocked(self):
                return False

            def execute(self, input_data):
                # Use simple echo command that will always succeed
                cmd = "echo 'real command executed'"

                from ce.core import run_cmd
                return run_cmd(cmd)

        # Pipeline with real command
        real_pipeline = (
            PipelineBuilder(mode="integration")
            .add_node("parse", RealParserStrategy())
            .add_node("command", RealCommandWithContext())
            .add_edge("parse", "command")
            .build()
        )

        # Pipeline with mock command (same structure)
        class MockCommand:
            def is_mocked(self):
                return True

            def execute(self, input_data):
                return {"success": True, "stdout": "mocked output", "method": "mock"}

        mock_pipeline = (
            PipelineBuilder(mode="e2e")
            .add_node("parse", RealParserStrategy())
            .add_node("command", MockCommand())
            .add_edge("parse", "command")
            .build()
        )

        # Both should execute successfully with same input structure
        real_result = real_pipeline.execute({
            "prp_path": str(prp_file)
        })
        assert real_result["success"] is True
        assert "stdout" in real_result
        assert "real command executed" in real_result["stdout"]

        mock_result = mock_pipeline.execute({
            "prp_path": str(prp_file)
        })
        assert mock_result["success"] is True
        assert mock_result["method"] == "mock"
        assert "mocked output" in mock_result["stdout"]

        # Verify strategies are interchangeable (same interface)
        assert hasattr(RealCommandWithContext(), 'execute')
        assert hasattr(RealCommandWithContext(), 'is_mocked')
        assert hasattr(MockCommand(), 'execute')
        assert hasattr(MockCommand(), 'is_mocked')
