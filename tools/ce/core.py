"""Core operations: file, git, and shell utilities."""

import subprocess
import time
import shlex
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


def find_project_root(start_path: Optional[Path] = None) -> Path:
    """Find project root by walking up to find .ce/ directory.

    Args:
        start_path: Starting path (defaults to current working directory)

    Returns:
        Path to project root (where .ce/ exists)

    Raises:
        FileNotFoundError: If .ce/ not found in any parent directory

    Example:
        >>> root = find_project_root()
        >>> config = root / ".ce" / "config.yml"
    """
    current = start_path or Path.cwd()

    # Check current directory and all parents
    for parent in [current] + list(current.parents):
        if (parent / ".ce").exists():
            return parent

    raise FileNotFoundError(
        f"Not in a Context Engineering project (.ce/ not found)\n"
        f"Searched from: {current}\n"
        f"🔧 Troubleshooting: Run from within a CE project directory"
    )


def run_cmd(
    cmd: Union[str, List[str]],
    cwd: Optional[str] = None,
    timeout: int = 60,
    capture_output: bool = True
) -> Dict[str, Any]:
    """Execute shell command with timeout and error handling.

    Args:
        cmd: Shell command (str will be safely split) or list of args
        cwd: Working directory (default: current)
        timeout: Command timeout in seconds
        capture_output: Whether to capture stdout/stderr

    Returns:
        Dict with: success (bool), stdout (str), stderr (str),
                   exit_code (int), duration (float)

    Raises:
        ValueError: If command is empty
        subprocess.TimeoutExpired: If command exceeds timeout

    Security: Uses shell=False to prevent command injection (CWE-78).
              String commands are safely parsed with shlex.split().
    
    Note: No fishy fallbacks - exceptions are thrown to troubleshoot quickly.
    """
    start = time.time()

    # Convert string to safe list
    if isinstance(cmd, str):
        cmd_list = shlex.split(cmd)  # Safe parsing with proper escaping
    else:
        cmd_list = cmd

    # Handle empty command
    if not cmd_list:
        raise ValueError(
            "Empty command provided\n"
            "🔧 Troubleshooting: Provide a valid command string or list"
        )

    try:
        result = subprocess.run(
            cmd_list,  # ✅ List format
            shell=False,  # ✅ SAFE - no shell interpretation (CWE-78 fix)
            cwd=cwd,
            timeout=timeout,
            capture_output=capture_output,
            text=True
        )

        duration = time.time() - start

        return {
            "success": result.returncode == 0,
            "stdout": result.stdout if capture_output else "",
            "stderr": result.stderr if capture_output else "",
            "exit_code": result.returncode,
            "duration": duration
        }

    except subprocess.TimeoutExpired as e:
        duration = time.time() - start
        raise TimeoutError(
            f"Command timed out after {timeout}s: {' '.join(cmd_list)}\n"
            f"🔧 Troubleshooting: Increase timeout or check for hanging process"
        ) from e

    except Exception as e:
        duration = time.time() - start
        raise RuntimeError(
            f"Command failed: {' '.join(cmd_list)}\n"
            f"Error: {str(e)}\n"
            f"🔧 Troubleshooting: Check command syntax and permissions"
        ) from e


def count_git_files() -> int:
    """Count total tracked files in git repository.

    Replaces shell pattern: git ls-files | wc -l

    Returns:
        Number of tracked files

    Raises:
        RuntimeError: If not in git repository

    Security: Uses subprocess.run with shell=False (CWE-78 safe).
    """
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True,
            text=True,
            shell=False,  # ✅ SAFE
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(
                "Failed to list git files\n"
                "🔧 Troubleshooting: Ensure you're in a git repository"
            )

        files = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return len(files)

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Git ls-files timed out\n"
            "🔧 Troubleshooting: Repository may be too large"
        )


def count_git_diff_lines(
    ref: str = "HEAD~5",
    files: Optional[List[str]] = None
) -> int:
    """Count lines changed in git diff.

    Replaces shell pattern: git diff HEAD~5 -- file1 file2 | wc -l

    Args:
        ref: Git reference to diff against (default: HEAD~5)
        files: Optional list of files to diff

    Returns:
        Number of changed lines

    Security: Uses subprocess.run with shell=False (CWE-78 safe).
    Note: Returns 0 on error (graceful degradation for health checks).
    """
    cmd = ["git", "diff", ref]
    if files:
        cmd.extend(["--"] + files)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=False,  # ✅ SAFE
            timeout=30
        )

        if result.returncode != 0:
            return 0

        return len(result.stdout.split('\n')) if result.stdout else 0

    except subprocess.TimeoutExpired:
        return 0


def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read file with validation."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {path}\n🔧 Troubleshooting: Check path spelling")
    if not file_path.is_file():
        raise ValueError(f"Path is not a file: {path}\n🔧 Troubleshooting: Use different method")
    return file_path.read_text(encoding=encoding)


def write_file(path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> None:
    """Write file with security validation."""
    file_path = Path(path)
    sensitive_patterns = [("API_KEY", "API keys"), ("SECRET", "Secrets"), ("PASSWORD", "Passwords")]
    for pattern, msg in sensitive_patterns:
        if pattern in content.upper():
            raise ValueError(f"Sensitive data: {msg}\n🔧 Use environment variables")
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding=encoding)


def git_status() -> Dict[str, Any]:
    """Get git repository status."""
    check_result = run_cmd("git rev-parse --git-dir", capture_output=True)
    if not check_result["success"]:
        raise RuntimeError("Not in git repository\n🔧 Troubleshooting: Check inputs and system state")
    result = run_cmd("git status --porcelain", capture_output=True)
    if not result["success"]:
        raise RuntimeError(f"Git status failed: {result['stderr']}\n🔧 Troubleshooting: Check inputs and system state")
    
    staged, unstaged, untracked = [], [], []
    lines = result["stdout"].strip().split("\n") if result["stdout"].strip() else []
    
    for line in lines:
        if not line:
            continue
        status, filepath = line[:2], line[3:]
        if status[0] != " " and status[0] != "?":
            staged.append(filepath)
        if status[1] != " " and status[1] != "?":
            unstaged.append(filepath)
        if status == "??":
            untracked.append(filepath)
    
    return {"clean": len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0,
            "staged": staged, "unstaged": unstaged, "untracked": untracked}


def git_diff(since: str = "HEAD~5", name_only: bool = True) -> List[str]:
    """Get changed files since specified ref."""
    flag = "--name-only" if name_only else "--stat"
    result = run_cmd(f"git diff {flag} {since}", capture_output=True)
    if not result["success"]:
        raise RuntimeError(f"Git diff failed: {result['stderr']}\n🔧 Troubleshooting: Check inputs and system state")
    return [f.strip() for f in result["stdout"].strip().split("\n") if f.strip()]


def git_checkpoint(message: str = "Context Engineering checkpoint") -> str:
    """Create git tag checkpoint for recovery."""
    import datetime
    timestamp = int(datetime.datetime.now().timestamp())
    checkpoint_id = f"checkpoint-{timestamp}"
    result = run_cmd(["git", "tag", "-a", checkpoint_id, "-m", message], capture_output=True)
    if not result["success"]:
        raise RuntimeError(f"Failed to create checkpoint: {result['stderr']}\n🔧 Troubleshooting: Check inputs and system state")
    return checkpoint_id


def run_py(code: Optional[str] = None, file: Optional[str] = None, args: str = "", auto: Optional[str] = None) -> Dict[str, Any]:
    """Execute Python code using uv with strict LOC limits."""
    if auto is not None:
        if code is not None or file is not None:
            raise ValueError("Cannot use 'auto' with 'code' or 'file'\n🔧 Troubleshooting: Check inputs and system state")
        file = auto if "/" in auto or auto.endswith(".py") else None
        code = auto if file is None else None

    if code is None and file is None:
        raise ValueError("Either 'code', 'file', or 'auto' must be provided")
    if code is not None and file is not None:
        raise ValueError("Cannot provide both 'code' and 'file'\n🔧 Troubleshooting: Check inputs and system state")

    if code is not None:
        lines = [line for line in code.split('\n') if line.strip()]
        if len(lines) > 3:
            raise ValueError(f"Ad-hoc code exceeds 3 LOC limit\n🔧 Troubleshooting: Check inputs and system state")
        cmd = ["uv", "run", "python", "-c", code]
        if args:
            cmd.extend(args.split())
        return run_cmd(cmd, timeout=120)

    if file is not None:
        file_path = Path(file)
        if not any(part == "tmp" for part in file_path.parts):
            raise ValueError(f"File must be in tmp/ folder")
        if not file_path.exists():
            raise FileNotFoundError(f"Python file not found: {file}\n🔧 Troubleshooting: Check inputs and system state")
        cmd = ["uv", "run", "python", file]
        if args:
            cmd.extend(args.split())
        return run_cmd(cmd, timeout=300)
