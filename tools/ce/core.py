"""Core operations: file, git, and shell utilities."""

import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any, Optional


def run_cmd(
    cmd: str,
    cwd: Optional[str] = None,
    timeout: int = 60,
    capture_output: bool = True
) -> Dict[str, Any]:
    """Execute shell command with timeout and error handling.

    Args:
        cmd: Shell command to execute
        cwd: Working directory (default: current)
        timeout: Command timeout in seconds
        capture_output: Whether to capture stdout/stderr

    Returns:
        Dict with: success (bool), stdout (str), stderr (str),
                   exit_code (int), duration (float)

    Raises:
        subprocess.TimeoutExpired: If command exceeds timeout

    Note: No fishy fallbacks - exceptions are thrown to troubleshoot quickly.
    """
    start = time.time()

    try:
        result = subprocess.run(
            cmd,
            shell=True,
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
        # Note: No fallback - exceptions thrown for troubleshooting
        raise TimeoutError(
            f"Command timed out after {timeout}s: {cmd}\n"
            f"🔧 Troubleshooting: Increase timeout or check for hanging process"
        ) from e

    except Exception as e:
        duration = time.time() - start
        # Note: No fallback - exceptions thrown for troubleshooting
        raise RuntimeError(
            f"Command failed: {cmd}\n"
            f"Error: {str(e)}\n"
            f"🔧 Troubleshooting: Check command syntax and permissions"
        ) from e


def read_file(path: str, encoding: str = "utf-8") -> str:
    """Read file with validation.

    Args:
        path: File path (absolute or relative)
        encoding: Text encoding (default: utf-8)

    Returns:
        File contents as string

    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file not readable
        UnicodeDecodeError: If encoding fails

    Note: No fishy fallbacks - exceptions thrown for debugging.
    """
    file_path = Path(path)

    if not file_path.exists():
        # Note: No fallback - exceptions thrown for debugging
        raise FileNotFoundError(
            f"File not found: {path}\n"
            f"🔧 Troubleshooting: Check path spelling and file existence"
        )

    if not file_path.is_file():
        raise ValueError(
            f"Path is not a file: {path}\n"
            f"🔧 Troubleshooting: Path points to directory, use different method"
        )

    try:
        return file_path.read_text(encoding=encoding)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding, e.object, e.start, e.end,
            f"Failed to decode {path} with {encoding} encoding\n"
            f"🔧 Troubleshooting: Try binary mode or different encoding"
        )


def write_file(path: str, content: str, encoding: str = "utf-8", create_dirs: bool = True) -> None:
    """Write file with security validation.

    Args:
        path: File path (absolute or relative)
        content: Content to write
        encoding: Text encoding (default: utf-8)
        create_dirs: Create parent directories if needed

    Raises:
        PermissionError: If file not writable
        ValueError: If sensitive data detected in content

    Note: Validates for sensitive patterns before writing.
    """
    file_path = Path(path)

    # Security check: detect sensitive data patterns
    sensitive_patterns = [
        ("API_KEY", "API keys should not be in code"),
        ("SECRET", "Secrets should not be in code"),
        ("PASSWORD", "Passwords should not be in code"),
        ("PRIVATE_KEY", "Private keys should not be in code")
    ]

    for pattern, message in sensitive_patterns:
        if pattern in content.upper():
            # Note: No fallback - exceptions thrown for security
            raise ValueError(
                f"Sensitive data detected: {message}\n"
                f"Pattern found: {pattern}\n"
                f"🔧 Troubleshooting: Use environment variables or secrets manager"
            )

    # Create parent directories if needed
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        file_path.write_text(content, encoding=encoding)
    except PermissionError as e:
        raise PermissionError(
            f"Cannot write to {path}\n"
            f"🔧 Troubleshooting: Check file permissions and directory access"
        ) from e


def git_status() -> Dict[str, Any]:
    """Get git repository status.

    Returns:
        Dict with: clean (bool), staged (List[str]),
                   unstaged (List[str]), untracked (List[str])

    Raises:
        RuntimeError: If not in git repository

    Note: Returns real git status - no mocked values.
    """
    # Check if in git repo
    check_result = run_cmd("git rev-parse --git-dir", capture_output=True)
    if not check_result["success"]:
        raise RuntimeError(
            "Not in a git repository\n"
            f"🔧 Troubleshooting: Run 'git init' or navigate to git repository"
        )

    # Get porcelain status
    result = run_cmd("git status --porcelain", capture_output=True)

    if not result["success"]:
        raise RuntimeError(
            f"Git status failed: {result['stderr']}\n"
            f"🔧 Troubleshooting: Check git repository integrity"
        )

    lines = result["stdout"].strip().split("\n") if result["stdout"].strip() else []

    staged = []
    unstaged = []
    untracked = []

    for line in lines:
        if not line:
            continue

        status = line[:2]
        filepath = line[3:]

        # Staged changes
        if status[0] != " " and status[0] != "?":
            staged.append(filepath)

        # Unstaged changes
        if status[1] != " " and status[1] != "?":
            unstaged.append(filepath)

        # Untracked files
        if status == "??":
            untracked.append(filepath)

    return {
        "clean": len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked
    }


def git_diff(since: str = "HEAD~5", name_only: bool = True) -> List[str]:
    """Get changed files since specified ref.

    Args:
        since: Git ref to diff against (default: HEAD~5)
        name_only: Return only filenames (default: True)

    Returns:
        List of changed file paths

    Raises:
        RuntimeError: If git diff fails

    Note: Returns real git diff output.
    """
    flag = "--name-only" if name_only else "--stat"
    result = run_cmd(f"git diff {flag} {since}", capture_output=True)

    if not result["success"]:
        raise RuntimeError(
            f"Git diff failed: {result['stderr']}\n"
            f"🔧 Troubleshooting: Check if ref '{since}' exists"
        )

    files = [f.strip() for f in result["stdout"].strip().split("\n") if f.strip()]
    return files


def git_checkpoint(message: str = "Context Engineering checkpoint") -> str:
    """Create git tag checkpoint for recovery.

    Args:
        message: Checkpoint message

    Returns:
        Checkpoint ID (tag name)

    Raises:
        RuntimeError: If checkpoint creation fails

    Note: Creates real git tag - no mocked checkpoint.
    """
    import datetime

    # Generate checkpoint ID with timestamp
    timestamp = int(datetime.datetime.now().timestamp())
    checkpoint_id = f"checkpoint-{timestamp}"

    # Create annotated tag
    result = run_cmd(
        f'git tag -a "{checkpoint_id}" -m "{message}"',
        capture_output=True
    )

    if not result["success"]:
        raise RuntimeError(
            f"Failed to create checkpoint: {result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure you have commits to tag"
        )

    return checkpoint_id
