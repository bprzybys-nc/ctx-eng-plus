"""Legacy file detection for CE initialization.

Scans multiple legacy locations for CE framework files, handles symlinks,
and filters garbage files.
"""

from pathlib import Path
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)

# Search patterns by domain
SEARCH_PATTERNS = {
    "prps": ["PRPs/", "context-engineering/PRPs/"],
    "examples": ["examples/", "context-engineering/examples/"],
    "claude_md": ["CLAUDE.md"],
    "settings": [".claude/settings.local.json"],
    "commands": [".claude/commands/"],
    "memories": [".serena/memories/"]
}

# Garbage filter patterns
GARBAGE_PATTERNS = [
    "REPORT", "INITIAL", "summary", "analysis",
    "PLAN", ".backup", "~", ".tmp", ".log"
]


class LegacyFileDetector:
    """Detect legacy CE files across multiple locations.

    Scans PRPs/, examples/, context-engineering/, .serena/, and .claude/
    directories for CE framework files. Includes smart filtering to exclude
    garbage files and proper symlink handling.

    Example:
        >>> detector = LegacyFileDetector(Path("/project/root"))
        >>> inventory = detector.scan_all()
        >>> print(f"Found {len(inventory['prps'])} PRPs")
    """

    def __init__(self, project_root: Path):
        """Initialize detector with project root.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root).resolve()
        self.visited_symlinks: Set[Path] = set()

    def scan_all(self) -> Dict[str, List[Path]]:
        """Scan all domains and return inventory.

        Returns:
            Dict with keys: prps, examples, claude_md, settings, commands, memories
            Each value is List[Path] of detected files

        Example:
            >>> inventory = detector.scan_all()
            >>> inventory.keys()
            dict_keys(['prps', 'examples', 'claude_md', 'settings', 'commands', 'memories'])
        """
        inventory = {domain: [] for domain in SEARCH_PATTERNS.keys()}

        for domain, patterns in SEARCH_PATTERNS.items():
            for pattern in patterns:
                search_path = self.project_root / pattern

                if not search_path.exists():
                    continue

                if search_path.is_file():
                    # Single file (e.g., CLAUDE.md)
                    resolved = self._resolve_symlink(search_path)
                    if resolved and not self._is_garbage(resolved):
                        inventory[domain].append(resolved)
                else:
                    # Directory - collect .md files
                    files = self._collect_files(search_path)
                    inventory[domain].extend(files)

        return inventory

    def _resolve_symlink(self, path: Path) -> Path | None:
        """Resolve symlink, detect circular references.

        Args:
            path: Path to resolve (may be symlink or regular file)

        Returns:
            Resolved path or None if circular/broken

        Example:
            >>> resolved = detector._resolve_symlink(Path("CLAUDE.md"))
            >>> resolved
            Path("/real/path/to/CLAUDE.md")
        """
        if not path.is_symlink():
            return path

        if path in self.visited_symlinks:
            logger.warning(f"Circular symlink detected: {path}")
            return None

        self.visited_symlinks.add(path)

        try:
            resolved = path.resolve(strict=True)
            return resolved
        except (OSError, RuntimeError) as e:
            logger.warning(f"Broken symlink: {path} - {e}")
            return None

    def _collect_files(self, directory: Path) -> List[Path]:
        """Recursively collect .md files from directory.

        Args:
            directory: Path to directory to scan

        Returns:
            List of .md file paths (garbage filtered)

        Example:
            >>> files = detector._collect_files(Path("PRPs/"))
            >>> len(files)
            23
        """
        files = []

        try:
            for item in directory.rglob("*.md"):
                if item.is_file() and not self._is_garbage(item):
                    resolved = self._resolve_symlink(item)
                    if resolved:
                        files.append(resolved)
        except PermissionError as e:
            logger.warning(f"Permission denied: {directory} - {e}")

        return files

    def _is_garbage(self, path: Path) -> bool:
        """Check if file matches garbage patterns.

        Args:
            path: Path to check

        Returns:
            True if file should be filtered out

        Example:
            >>> detector._is_garbage(Path("PRP-1-REPORT.md"))
            True
            >>> detector._is_garbage(Path("PRP-1-feature.md"))
            False
        """
        name = path.name
        return any(pattern in name for pattern in GARBAGE_PATTERNS)
