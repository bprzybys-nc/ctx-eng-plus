"""Base strategy for vacuum cleanup operations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
import subprocess


@dataclass
class CleanupCandidate:
    """Represents a file candidate for cleanup.

    Attributes:
        path: Path to file candidate
        reason: Human-readable reason for flagging
        confidence: Confidence score (0.0-1.0 float or 0-100 int, both supported)
        size_bytes: File size in bytes
        last_modified: Last modification timestamp
        git_history: Git history summary
        superseded_by: Path to PRP that supersedes this doc (NLP feature, batch 46)
        detection_type: Detection category (NLP feature, batch 46)
            - "INITIAL→PRP": INITIAL.md that became formal PRP
            - "Temporary→PRP": PLAN/ANALYSIS/REPORT integrated into PRP
            - "Superseded": Feature request superseded by executed PRP
    """

    path: Path
    reason: str
    confidence: float  # Changed from int to float (supports 0.0-1.0 and 0-100 ranges)
    size_bytes: int
    last_modified: Optional[datetime]
    git_history: Optional[str]

    # NEW fields for NLP-powered detection (batch 46)
    superseded_by: Optional[Path] = None
    detection_type: Optional[str] = None


class BaseStrategy(ABC):
    """Abstract base class for cleanup strategies."""

    # Patterns that should NEVER be deleted
    PROTECTED_PATTERNS = [
        ".ce/**",
        ".claude/**",  # Protect ALL Claude Code configuration
        ".serena/**",  # Protect Serena memories and configuration
        "syntropy-mcp/**",  # Protect syntropy MCP server directory
        # Note: tmp/** files are conditionally protected by age (see is_protected_by_age)
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

    def __init__(self, project_root: Path, scan_path: Path = None):
        """Initialize strategy with project root.

        Args:
            project_root: Path to project root directory
            scan_path: Optional path to scan (defaults to project_root)
        """
        self.project_root = project_root
        self.scan_path = scan_path if scan_path else project_root

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

        # Special case: tmp/ files - protect if modified less than 2 days ago
        if relative_str.startswith("tmp/"):
            # Files < 2 days old (by filesystem mtime) are protected
            if not self.is_recently_modified(path, days=2):
                # File is older than 2 days - not protected
                return False
            # File is recent (< 2 days) - protected
            return True

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

    def get_last_modified(self, path: Path) -> Optional[datetime]:
        """Get last modified timestamp.

        Args:
            path: Path to file or directory

        Returns:
            datetime object or None if error
        """
        try:
            timestamp = path.stat().st_mtime
            return datetime.fromtimestamp(timestamp)
        except Exception:
            return None

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

    def is_recently_modified(self, path: Path, days: int = 30) -> bool:
        """Check if file was modified recently (filesystem mtime).

        Args:
            path: Path to file
            days: Number of days to consider recent

        Returns:
            True if file was modified in last N days (based on filesystem mtime)
        """
        from datetime import datetime, timedelta

        try:
            mtime = datetime.fromtimestamp(path.stat().st_mtime)
            cutoff = datetime.now() - timedelta(days=days)
            return mtime > cutoff
        except Exception:
            return False
