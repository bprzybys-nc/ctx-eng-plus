"""Real strategy implementations for existing operations.

Wraps existing CE functions in strategy interface for composable testing.
Real strategies call actual functionality (parse files, run commands, etc.).
"""

from typing import Dict, Any
from .strategy import BaseRealStrategy
from ..core import run_cmd
from ..execute import parse_blueprint


class RealParserStrategy(BaseRealStrategy):
    """Real PRP blueprint parser strategy.

    Wraps parse_blueprint() from execute.py in strategy interface.
    Parses PRP markdown files into structured phase data.

    Example:
        strategy = RealParserStrategy()
        result = strategy.execute({"prp_path": "PRPs/PRP-1.md"})
        # Returns: {"success": True, "phases": [...]}
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse PRP file into phases.

        Args:
            input_data: {"prp_path": "path/to/prp.md"}

        Returns:
            {"success": True, "phases": [...]} on success
            {"success": False, "error": "..."} on failure

        Raises:
            RuntimeError: If prp_path not provided in input_data
        """
        prp_path = input_data.get("prp_path")
        if not prp_path:
            raise RuntimeError(
                "Missing 'prp_path' in input_data\n"
                "🔧 Troubleshooting: Provide prp_path to parser strategy"
            )

        try:
            phases = parse_blueprint(prp_path)
            return {
                "success": True,
                "phases": phases
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "parse_error",
                "troubleshooting": "Check PRP file format and implementation blueprint section"
            }


class RealCommandStrategy(BaseRealStrategy):
    """Real shell command execution strategy.

    Wraps run_cmd() from core.py in strategy interface.
    Executes shell commands with timeout and error handling.

    Example:
        strategy = RealCommandStrategy()
        result = strategy.execute({"cmd": "pytest tests/ -v"})
        # Returns: {"success": True, "stdout": "...", "stderr": "...", ...}
    """

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute shell command.

        Args:
            input_data: {
                "cmd": "shell command to execute",
                "timeout": 60,  # optional
                "cwd": "/path/to/dir"  # optional
            }

        Returns:
            {"success": bool, "stdout": "...", "stderr": "...", "exit_code": int, "duration": float}
            On error: {"success": False, "error": "...", "error_type": "...", "troubleshooting": "..."}

        Raises:
            RuntimeError: If cmd not provided in input_data

        Note: Error responses follow standard format with troubleshooting guidance.
        """
        cmd = input_data.get("cmd")
        if not cmd:
            raise RuntimeError(
                "Missing 'cmd' in input_data\n"
                "🔧 Troubleshooting: Provide cmd to execute"
            )

        timeout = input_data.get("timeout", 60)
        cwd = input_data.get("cwd")

        try:
            return run_cmd(cmd, cwd=cwd, timeout=timeout)
        except TimeoutError as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "timeout_error",
                "troubleshooting": "Increase timeout or check for hanging process"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "error_type": "runtime_error",
                "troubleshooting": "Check command syntax and permissions"
            }
