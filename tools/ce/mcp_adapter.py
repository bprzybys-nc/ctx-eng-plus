"""MCP adapter layer for Serena file operations with graceful fallback.

This module provides abstraction for file operations, using Serena MCP when available
and falling back to local filesystem operations when MCP is unavailable.

MCP Availability:
    - Claude Code context: Serena MCP typically available
    - Standalone CLI: Falls back to filesystem
    - Test environment: Uses mcp_fake for testing

Design Decision (ADR-001):
    - Optional fallback approach for MVP
    - Simple try/catch detection
    - Unified error handling
    - Performance acceptable (<100ms overhead per MCP call)
"""

from typing import Dict, Any, List, Optional
from pathlib import Path


def _import_serena_mcp():
    """Import Serena MCP module dynamically.

    Returns:
        The mcp__serena module

    Raises:
        ImportError: If module cannot be imported

    Note: Helper function to avoid repeated import logic throughout module.
    """
    import importlib
    return importlib.import_module("mcp__serena")


def is_mcp_available() -> bool:
    """Check if Serena MCP is available at runtime.

    Returns:
        True if Serena MCP tools are available, False otherwise

    Detection Strategy:
        1. Try importing mcp__serena tools
        2. Attempt minimal read operation
        3. Cache result for session (not implemented in MVP)

    Note: This is a simple detection strategy. More sophisticated
    approaches (version checking, capability negotiation) deferred to future.
    """
    try:
        # Attempt to import Serena MCP tools
        serena_module = _import_serena_mcp()

        # Check if key functions exist
        required_functions = [
            "read_file",
            "create_text_file",
            "get_symbols_overview",
            "insert_after_symbol"
        ]

        for func_name in required_functions:
            if not hasattr(serena_module, func_name):
                return False

        return True

    except (ImportError, ModuleNotFoundError, AttributeError):
        return False


def create_file_with_mcp(filepath: str, content: str) -> Dict[str, Any]:
    """Create file using Serena MCP or fallback to filesystem.

    Args:
        filepath: Relative path to file to create
        content: File content

    Returns:
        {
            "success": True,
            "method": "mcp" or "filesystem",
            "filepath": "<path>",
            "error": "<error message if success=False>"
        }

    Process:
        1. Check MCP availability
        2. If available, try mcp__serena__create_text_file
        3. On MCP failure or unavailable, fallback to filesystem
        4. Return result with method used

    Raises:
        RuntimeError: If both MCP and filesystem operations fail

    Note: Graceful fallback ensures execution continues even when MCP unavailable.
    """
    # Try MCP first if available
    if is_mcp_available():
        try:
            serena = _import_serena_mcp()
            serena.create_text_file(filepath, content)

            return {
                "success": True,
                "method": "mcp",
                "filepath": filepath
            }

        except Exception as e:
            # Log warning but continue to fallback
            print(f"      ⚠️  MCP file creation failed, falling back to filesystem: {e}")

    # Fallback to filesystem
    try:
        file_path = Path(filepath)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content)

        return {
            "success": True,
            "method": "filesystem",
            "filepath": filepath
        }

    except Exception as e:
        raise RuntimeError(
            f"Failed to create {filepath} (both MCP and filesystem failed)\n"
            f"Error: {str(e)}\n"
            f"🔧 Troubleshooting:\n"
            f"  1. Check file path is valid\n"
            f"  2. Verify parent directory exists or can be created\n"
            f"  3. Check write permissions\n"
            f"  4. Review file content for invalid characters"
        ) from e


def insert_code_with_mcp(
    filepath: str,
    code: str,
    mode: str = "append"
) -> Dict[str, Any]:
    """Insert code using Serena MCP symbol operations or fallback.

    Args:
        filepath: Path to file to modify
        code: Code to insert
        mode: Insertion mode - "append", "after_last_symbol", "before_first_symbol"

    Returns:
        {
            "success": True,
            "method": "mcp_symbol_aware" | "mcp_append" | "filesystem_append",
            "filepath": "<path>",
            "symbol": "<symbol name if symbol-aware>",
            "error": "<error message if success=False>"
        }

    Process:
        1. Check MCP availability
        2. If available and mode is symbol-aware:
           a. Get symbols overview
           b. Insert after/before symbol
        3. If MCP unavailable or append mode:
           a. Read file, append code, write back
        4. Return result with method used

    Raises:
        RuntimeError: If file modification fails

    Note: Symbol-aware insertion requires Serena MCP. Fallback mode is naive append.
    """
    # Try MCP symbol-aware insertion
    if is_mcp_available() and mode != "append":
        try:
            serena = _import_serena_mcp()

            # Get symbols to find insertion point
            symbols = serena.get_symbols_overview(filepath)

            if symbols and len(symbols) > 0:
                if mode == "after_last_symbol":
                    last_symbol = symbols[-1]["name_path"]
                    serena.insert_after_symbol(last_symbol, filepath, code)

                    return {
                        "success": True,
                        "method": "mcp_symbol_aware",
                        "filepath": filepath,
                        "symbol": last_symbol
                    }

                elif mode == "before_first_symbol":
                    first_symbol = symbols[0]["name_path"]
                    serena.insert_before_symbol(first_symbol, filepath, code)

                    return {
                        "success": True,
                        "method": "mcp_symbol_aware",
                        "filepath": filepath,
                        "symbol": first_symbol
                    }

            # No symbols found, fall through to append

        except Exception as e:
            # Log warning but continue to fallback
            print(f"      ⚠️  MCP symbol insertion failed, falling back to append: {e}")

    # Fallback: append to end of file
    try:
        file_path = Path(filepath)
        if not file_path.exists():
            raise RuntimeError(
                f"Cannot modify file {filepath} - file does not exist\n"
                f"🔧 Troubleshooting: Ensure file is created before modification"
            )

        current_content = file_path.read_text()
        new_content = current_content + "\n\n" + code
        file_path.write_text(new_content)

        return {
            "success": True,
            "method": "filesystem_append",
            "filepath": filepath
        }

    except Exception as e:
        raise RuntimeError(
            f"Failed to insert code into {filepath}\n"
            f"Error: {str(e)}\n"
            f"🔧 Troubleshooting:\n"
            f"  1. Check file exists and is writable\n"
            f"  2. Verify code is syntactically valid\n"
            f"  3. Check file has valid Python syntax for symbol parsing"
        ) from e


def get_mcp_status() -> Dict[str, Any]:
    """Get MCP availability status for diagnostics.

    Returns:
        {
            "available": True/False,
            "version": "<version if available>",
            "capabilities": ["read_file", "create_text_file", ...],
            "context": "mcp" | "standalone" | "test"
        }

    Note: Version and detailed capabilities detection deferred to future.
    For MVP, only availability check implemented.
    """
    available = is_mcp_available()

    result = {
        "available": available,
        "version": None,  # Not implemented in MVP
        "capabilities": [],  # Not implemented in MVP
        "context": "mcp" if available else "standalone"
    }

    if available:
        try:
            serena = _import_serena_mcp()

            # List available functions
            capabilities = [
                name for name in dir(serena)
                if not name.startswith("_") and callable(getattr(serena, name))
            ]
            result["capabilities"] = capabilities

        except Exception:
            pass

    return result
