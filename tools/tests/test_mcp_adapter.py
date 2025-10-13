"""Tests for MCP adapter layer with graceful fallback."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

from ce.mcp_adapter import (
    is_mcp_available,
    create_file_with_mcp,
    insert_code_with_mcp,
    get_mcp_status
)


class TestIsMcpAvailable:
    """Test MCP availability detection."""

    def test_mcp_available_all_functions_present(self):
        """Test MCP detected as available when all functions present."""
        # Create mock Serena module
        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock()
        mock_serena.insert_after_symbol = Mock()

        with patch('importlib.import_module', return_value=mock_serena):
            result = is_mcp_available()

        assert result is True

    def test_mcp_unavailable_import_error(self):
        """Test MCP detected as unavailable when import fails."""
        with patch('importlib.import_module', side_effect=ImportError("No module named 'mcp__serena'")):
            result = is_mcp_available()

        assert result is False

    def test_mcp_unavailable_missing_function(self):
        """Test MCP detected as unavailable when required function missing."""
        # Create mock with only some functions (spec limits attributes)
        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        # Missing: get_symbols_overview and insert_after_symbol
        # Delete them explicitly to simulate missing attributes
        del mock_serena.get_symbols_overview
        del mock_serena.insert_after_symbol

        with patch('importlib.import_module', return_value=mock_serena):
            result = is_mcp_available()

        assert result is False


class TestCreateFileWithMcp:
    """Test file creation with MCP fallback."""

    def test_create_file_with_mcp_success(self, tmp_path):
        """Test file creation succeeds with MCP when available."""
        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock()
        mock_serena.insert_after_symbol = Mock()

        filepath = str(tmp_path / "test.py")
        content = "def test(): pass"

        with patch('importlib.import_module', return_value=mock_serena):
            result = create_file_with_mcp(filepath, content)

        assert result["success"] is True
        assert result["method"] == "mcp"
        assert result["filepath"] == filepath
        mock_serena.create_text_file.assert_called_once_with(filepath, content)

    def test_create_file_mcp_unavailable_fallback(self, tmp_path):
        """Test file creation falls back to filesystem when MCP unavailable."""
        filepath = str(tmp_path / "test.py")
        content = "def test(): pass"

        with patch('importlib.import_module', side_effect=ImportError()):
            result = create_file_with_mcp(filepath, content)

        assert result["success"] is True
        assert result["method"] == "filesystem"
        assert result["filepath"] == filepath
        assert Path(filepath).exists()
        assert Path(filepath).read_text() == content

    def test_create_file_mcp_fails_fallback(self, tmp_path):
        """Test file creation falls back when MCP call fails."""
        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock(side_effect=RuntimeError("MCP error"))
        mock_serena.get_symbols_overview = Mock()
        mock_serena.insert_after_symbol = Mock()

        filepath = str(tmp_path / "test.py")
        content = "def test(): pass"

        with patch('importlib.import_module', return_value=mock_serena):
            with patch('builtins.print'):  # Suppress warning output
                result = create_file_with_mcp(filepath, content)

        assert result["success"] is True
        assert result["method"] == "filesystem"
        assert Path(filepath).exists()

    def test_create_file_creates_parent_dirs(self, tmp_path):
        """Test file creation creates parent directories if needed."""
        filepath = str(tmp_path / "subdir" / "nested" / "test.py")
        content = "def test(): pass"

        with patch('importlib.import_module', side_effect=ImportError()):
            result = create_file_with_mcp(filepath, content)

        assert result["success"] is True
        assert Path(filepath).exists()
        assert Path(filepath).parent.exists()


class TestInsertCodeWithMcp:
    """Test code insertion with symbol awareness."""

    def test_insert_code_symbol_aware_success(self, tmp_path):
        """Test code insertion uses symbol-aware MCP when available."""
        # Create test file
        filepath = str(tmp_path / "test.py")
        Path(filepath).write_text("def first(): pass\n\ndef second(): pass\n")

        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock(return_value=[
            {"name_path": "first"},
            {"name_path": "second"}
        ])
        mock_serena.insert_after_symbol = Mock()

        code = "def third(): pass"

        with patch('importlib.import_module', return_value=mock_serena):
            result = insert_code_with_mcp(filepath, code, mode="after_last_symbol")

        assert result["success"] is True
        assert result["method"] == "mcp_symbol_aware"
        assert result["symbol"] == "second"
        mock_serena.insert_after_symbol.assert_called_once_with("second", filepath, code)

    def test_insert_code_no_symbols_fallback_append(self, tmp_path):
        """Test code insertion falls back to append when no symbols found."""
        filepath = str(tmp_path / "test.py")
        Path(filepath).write_text("# Just a comment\n")

        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock(return_value=[])  # No symbols
        mock_serena.insert_after_symbol = Mock()

        code = "def first(): pass"

        with patch('importlib.import_module', return_value=mock_serena):
            with patch('builtins.print'):  # Suppress warning
                result = insert_code_with_mcp(filepath, code, mode="after_last_symbol")

        assert result["success"] is True
        assert result["method"] == "filesystem_append"
        assert Path(filepath).exists()
        content = Path(filepath).read_text()
        assert "def first(): pass" in content

    def test_insert_code_mcp_unavailable_append(self, tmp_path):
        """Test code insertion uses append when MCP unavailable."""
        filepath = str(tmp_path / "test.py")
        Path(filepath).write_text("def first(): pass\n")

        code = "def second(): pass"

        with patch('importlib.import_module', side_effect=ImportError()):
            result = insert_code_with_mcp(filepath, code, mode="after_last_symbol")

        assert result["success"] is True
        assert result["method"] == "filesystem_append"
        content = Path(filepath).read_text()
        assert "def second(): pass" in content

    def test_insert_code_append_mode_uses_filesystem(self, tmp_path):
        """Test code insertion uses filesystem when mode is 'append'."""
        filepath = str(tmp_path / "test.py")
        Path(filepath).write_text("def first(): pass\n")

        mock_serena = MagicMock()
        code = "def second(): pass"

        # Even with MCP available, append mode should use filesystem
        with patch('importlib.import_module', return_value=mock_serena):
            result = insert_code_with_mcp(filepath, code, mode="append")

        assert result["success"] is True
        assert result["method"] == "filesystem_append"
        # MCP should not be called in append mode
        mock_serena.get_symbols_overview.assert_not_called()

    def test_insert_code_before_first_symbol(self, tmp_path):
        """Test code insertion before first symbol."""
        filepath = str(tmp_path / "test.py")
        Path(filepath).write_text("def first(): pass\n")

        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock(return_value=[
            {"name_path": "first"}
        ])
        mock_serena.insert_before_symbol = Mock()

        code = "# Header comment"

        with patch('importlib.import_module', return_value=mock_serena):
            result = insert_code_with_mcp(filepath, code, mode="before_first_symbol")

        assert result["success"] is True
        assert result["method"] == "mcp_symbol_aware"
        assert result["symbol"] == "first"
        mock_serena.insert_before_symbol.assert_called_once()

    def test_insert_code_file_not_exists_raises_error(self, tmp_path):
        """Test code insertion raises error when file doesn't exist."""
        filepath = str(tmp_path / "nonexistent.py")
        code = "def test(): pass"

        with patch('importlib.import_module', side_effect=ImportError()):
            with pytest.raises(RuntimeError) as exc_info:
                insert_code_with_mcp(filepath, code, mode="after_last_symbol")

        assert "does not exist" in str(exc_info.value)
        assert "🔧 Troubleshooting" in str(exc_info.value)


class TestGetMcpStatus:
    """Test MCP status diagnostics."""

    def test_get_mcp_status_available(self):
        """Test MCP status reports available when MCP present."""
        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock()
        mock_serena.insert_after_symbol = Mock()

        # Add some callable attributes
        mock_serena.some_function = Mock()

        with patch('importlib.import_module', return_value=mock_serena):
            result = get_mcp_status()

        assert result["available"] is True
        assert result["context"] == "mcp"
        assert isinstance(result["capabilities"], list)

    def test_get_mcp_status_unavailable(self):
        """Test MCP status reports unavailable when MCP missing."""
        with patch('importlib.import_module', side_effect=ImportError()):
            result = get_mcp_status()

        assert result["available"] is False
        assert result["context"] == "standalone"
        assert result["version"] is None
        assert result["capabilities"] == []

    def test_get_mcp_status_handles_exceptions_gracefully(self):
        """Test MCP status handles exceptions during capability detection."""
        mock_serena = MagicMock()
        mock_serena.read_file = Mock()
        mock_serena.create_text_file = Mock()
        mock_serena.get_symbols_overview = Mock()
        mock_serena.insert_after_symbol = Mock()

        with patch('importlib.import_module', return_value=mock_serena):
            # Should not raise even if capability detection has issues
            result = get_mcp_status()

        # Verify it returns a valid structure
        assert result["available"] is True
        assert result["context"] == "mcp"
        assert "capabilities" in result
        assert isinstance(result["capabilities"], list)
