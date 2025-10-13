"""Tests for real strategy implementations."""

import pytest
from pathlib import Path

from ce.testing.real_strategies import RealParserStrategy, RealCommandStrategy


class TestRealParserStrategy:
    """Test RealParserStrategy for PRP parsing."""

    def test_real_parser_parses_valid_prp(self, tmp_path):
        """Test RealParserStrategy parses valid PRP file."""
        # Create test PRP file with valid blueprint
        prp_file = tmp_path / "test.md"
        prp_file.write_text("""
# Test PRP

## 🔧 Implementation Blueprint

### Phase 1: Core Implementation (4 hours)

**Goal**: Implement core functionality

**Approach**: Class-based design

**Files to Create**:
- `src/core.py` - Core module

**Key Functions**:
```python
def main():
    pass
```

**Validation Command**: `pytest tests/ -v`

**Checkpoint**: `git commit -m "feat: core"`

## Validation Gates
""")

        strategy = RealParserStrategy()
        result = strategy.execute({"prp_path": str(prp_file)})

        assert result["success"] is True
        assert "phases" in result
        assert len(result["phases"]) == 1
        assert result["phases"][0]["phase_name"] == "Core Implementation"
        assert result["phases"][0]["hours"] == 4.0

    def test_real_parser_is_mocked_returns_false(self):
        """Test RealParserStrategy.is_mocked() returns False."""
        strategy = RealParserStrategy()
        assert strategy.is_mocked() is False

    def test_real_parser_raises_error_for_missing_prp_path(self):
        """Test RealParserStrategy raises error when prp_path missing."""
        strategy = RealParserStrategy()

        with pytest.raises(RuntimeError) as exc_info:
            strategy.execute({})

        error_msg = str(exc_info.value)
        assert "Missing 'prp_path'" in error_msg
        assert "🔧 Troubleshooting" in error_msg

    def test_real_parser_returns_error_for_nonexistent_file(self):
        """Test RealParserStrategy returns error dict for nonexistent file."""
        strategy = RealParserStrategy()
        result = strategy.execute({"prp_path": "/nonexistent/file.md"})

        assert result["success"] is False
        assert "error" in result
        assert "error_type" in result
        assert result["error_type"] == "parse_error"

    def test_real_parser_returns_error_for_malformed_prp(self, tmp_path):
        """Test RealParserStrategy returns error for malformed PRP."""
        # Create PRP without implementation blueprint
        prp_file = tmp_path / "malformed.md"
        prp_file.write_text("# Just a heading\n\nNo blueprint here.")

        strategy = RealParserStrategy()
        result = strategy.execute({"prp_path": str(prp_file)})

        assert result["success"] is False
        assert "error" in result
        assert "troubleshooting" in result


class TestRealCommandStrategy:
    """Test RealCommandStrategy for command execution."""

    def test_real_command_executes_simple_command(self):
        """Test RealCommandStrategy executes simple command."""
        strategy = RealCommandStrategy()
        result = strategy.execute({"cmd": "echo 'test'"})

        assert result["success"] is True
        assert "stdout" in result
        assert "test" in result["stdout"]
        assert result["exit_code"] == 0

    def test_real_command_is_mocked_returns_false(self):
        """Test RealCommandStrategy.is_mocked() returns False."""
        strategy = RealCommandStrategy()
        assert strategy.is_mocked() is False

    def test_real_command_raises_error_for_missing_cmd(self):
        """Test RealCommandStrategy raises error when cmd missing."""
        strategy = RealCommandStrategy()

        with pytest.raises(RuntimeError) as exc_info:
            strategy.execute({})

        error_msg = str(exc_info.value)
        assert "Missing 'cmd'" in error_msg
        assert "🔧 Troubleshooting" in error_msg

    def test_real_command_returns_error_for_failed_command(self):
        """Test RealCommandStrategy captures failed command."""
        strategy = RealCommandStrategy()
        result = strategy.execute({"cmd": "exit 1"})

        assert result["success"] is False
        assert result["exit_code"] == 1

    def test_real_command_with_timeout_parameter(self):
        """Test RealCommandStrategy accepts timeout parameter."""
        strategy = RealCommandStrategy()
        result = strategy.execute({
            "cmd": "echo 'quick'",
            "timeout": 5
        })

        assert result["success"] is True
        assert result["duration"] < 5.0

    def test_real_command_with_cwd_parameter(self, tmp_path):
        """Test RealCommandStrategy accepts cwd parameter."""
        # Create a test file in tmp directory
        test_file = tmp_path / "marker.txt"
        test_file.write_text("found")

        strategy = RealCommandStrategy()
        result = strategy.execute({
            "cmd": "ls marker.txt",
            "cwd": str(tmp_path)
        })

        assert result["success"] is True
        assert "marker.txt" in result["stdout"]


class TestRealStrategiesInteroperability:
    """Test real strategies work with base strategy interface."""

    def test_all_real_strategies_implement_is_mocked(self):
        """Test all real strategies implement is_mocked()."""
        parser = RealParserStrategy()
        command = RealCommandStrategy()

        assert parser.is_mocked() is False
        assert command.is_mocked() is False

    def test_all_real_strategies_implement_execute(self):
        """Test all real strategies implement execute()."""
        parser = RealParserStrategy()
        command = RealCommandStrategy()

        # Both should have execute method
        assert hasattr(parser, 'execute')
        assert hasattr(command, 'execute')
        assert callable(parser.execute)
        assert callable(command.execute)
