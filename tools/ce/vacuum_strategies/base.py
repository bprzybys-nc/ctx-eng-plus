"""Base strategy for vacuum cleanup operations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List
import subprocess


@dataclass
class CleanupCandidate:
    """Represents a file/directory candidate for cleanup."""

    path: Path
    reason: str
    confidence: int  # 0-100
    size_bytes: int
    last_modified: str
    git_history: str = ""
    references: List[str] = None
    report_only: bool = False  # If True, never delete (only report)

    def __post_init__(self):
        if self.references is None:
            self.references = []


class BaseStrategy(ABC):
    """Abstract base class for cleanup strategies."""

    # Patterns that should NEVER be deleted
    PROTECTED_PATTERNS = [
        ".ce/**",
        ".claude/**",  # Protect ALL Claude Code configuration
        "syntropy-mcp/**",  # Protect syntropy MCP server directory
        # Note: PRP files are protected by PRP naming convention check in is_protected()
        "pyproject.toml",
        "README.md",
        "CLAUDE.md",
        "WARP.md",
        "examples/**",
        "**/__init__.py",
        "**/cli.py",
        "**/__main__.py",
        "**/bootstrap.sh",
    ]

    def __init__(self, project_root: Path):
        """Initialize strategy with project root.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root

    @abstractmethod
    def find_candidates(self) -> List[CleanupCandidate]:
        """Find cleanup candidates using this strategy.

        Returns:
            List of CleanupCandidate objects
        """
        pass

    def is_protected(self, path: Path) -> bool:
        """Check if path matches protected patterns.

        Args:
            path: Path to check

        Returns:
            True if path is protected, False otherwise
        """
        relative_path = path.relative_to(self.project_root)
        relative_str = str(relative_path)

        # Special case: Markdown files in PRPs/ - check if they have YAML header
        # Match both "/PRPs/" and "PRPs/" (start of path)
        if (("/PRPs/" in relative_str or relative_str.startswith("PRPs/")) and path.suffix == ".md"):
            if self._has_yaml_frontmatter(path):
                return True
            # If in PRPs/ but no YAML header, not a real PRP - can be cleaned
            return False

        for pattern in self.PROTECTED_PATTERNS:
            # Simple glob-like matching
            if self._matches_pattern(relative_str, pattern):
                return True

        return False

    def _has_yaml_frontmatter(self, path: Path) -> bool:
        """Check if markdown file has YAML frontmatter header.

        Args:
            path: Path to markdown file

        Returns:
            True if file starts with YAML frontmatter (---), False otherwise
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                return first_line == "---"
        except Exception:
            return False

    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """Simple pattern matching for protected paths.

        Args:
            path: Path string to check
            pattern: Pattern with ** and * wildcards

        Returns:
            True if path matches pattern
        """
        from fnmatch import fnmatch

        # Handle ** for recursive directory matching
        if "**" in pattern:
            pattern_parts = pattern.split("**")
            if len(pattern_parts) == 2:
                prefix, suffix = pattern_parts
                prefix = prefix.rstrip("/")
                suffix = suffix.lstrip("/")

                if prefix and not path.startswith(prefix):
                    return False
                if suffix and not fnmatch(path, f"*{suffix}"):
                    return False
                return True

        return fnmatch(path, pattern)

    def get_file_size(self, path: Path) -> int:
        """Get file or directory size in bytes.

        Args:
            path: Path to file or directory

        Returns:
            Size in bytes
        """
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())
        return 0

    def get_last_modified(self, path: Path) -> str:
        """Get last modified timestamp.

        Args:
            path: Path to file or directory

        Returns:
            ISO format timestamp string
        """
        from datetime import datetime

        timestamp = path.stat().st_mtime
        return datetime.fromtimestamp(timestamp).isoformat()

    def get_git_history(self, path: Path, days: int = 30) -> str:
        """Get git history summary for file.

        Args:
            path: Path to file
            days: Number of days to look back

        Returns:
            Git history summary or empty string
        """
        try:
            relative_path = path.relative_to(self.project_root)
            result = subprocess.run(
                ["git", "log", "--oneline", f"--since={days} days ago", "--", str(relative_path)],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                return f"{len(lines)} commits in last {days} days"
            return f"No commits in last {days} days"

        except Exception:
            return "Git history unavailable"

    def is_recently_active(self, path: Path, days: int = 30) -> bool:
        """Check if file has recent git activity.

        Args:
            path: Path to file
            days: Number of days to consider recent

        Returns:
            True if file has commits in last N days
        """
        history = self.get_git_history(path, days)
        return "commits in last" in history and not history.startswith("0 commits")
