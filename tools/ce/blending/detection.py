"""Legacy file detection for CE initialization.

Scans multiple legacy locations for CE framework files, handles symlinks,
and filters garbage files. Uses config-driven path resolution.
"""

from pathlib import Path
from typing import Dict, List, Set, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Garbage filter patterns
GARBAGE_PATTERNS = [
    "REPORT", "INITIAL", "summary", "analysis",
    "PLAN", ".backup", "~", ".tmp", ".log"
]

# Domain search patterns (compatible with test suite)
SEARCH_PATTERNS = {
    "prps": ["**/*.md"],
    "examples": ["**/*.md", "**/*.py"],
    "claude_md": ["CLAUDE.md"],
    "settings": ["settings.local.json"],
    "commands": ["**/*.md"],
    "memories": ["**/*.md"]
}


class LegacyFileDetector:
    """Detect legacy CE files across multiple locations.

    Scans PRPs/, examples/, context-engineering/, .serena/, and .claude/
    directories for CE framework files. Includes smart filtering to exclude
    garbage files and proper symlink handling. Uses config-driven search patterns.

    Example:
        >>> from ce.config_loader import BlendConfig
        >>> config = BlendConfig(Path(".ce/blend-config.yml"))
        >>> detector = LegacyFileDetector(Path("/project/root"), config)
        >>> inventory = detector.scan_all()
        >>> print(f"Found {len(inventory['prps'])} PRPs")
    """

    def __init__(self, project_root: Path, config: Optional[Any] = None):
        """Initialize detector with project root and config.

        Args:
            project_root: Path to project root directory
            config: BlendConfig instance with directory paths (optional for backward compatibility)
        """
        self.project_root = Path(project_root).resolve()
        self.config = config
        self.visited_symlinks: Set[Path] = set()

    def scan_all(self) -> Dict[str, List[Path]]:
        """Scan all domains and return inventory.

        Uses config-driven search patterns if config available, otherwise uses
        sensible defaults for backward compatibility. Deduplicates results to avoid
        finding same file via multiple paths (e.g., via context-engineering/ and
        context-engineering/PRPs/).

        Returns:
            Dict with keys: prps, examples, claude_md, settings, commands, memories
            Each value is List[Path] of detected files (deduplicated)

        Example:
            >>> from ce.config_loader import BlendConfig
            >>> config = BlendConfig(Path(".ce/blend-config.yml"))
            >>> detector = LegacyFileDetector(Path("/project/root"), config)
            >>> inventory = detector.scan_all()
            >>> inventory.keys()
            dict_keys(['prps', 'examples', 'claude_md', 'settings', 'commands', 'memories'])
        """
        # Domains to scan
        domains = ["prps", "examples", "claude_md", "settings", "commands", "memories"]
        inventory = {domain: [] for domain in domains}

        for domain in domains:
            patterns = self._get_domain_search_paths(domain)
            seen_paths = set()  # Track paths to deduplicate

            for pattern in patterns:
                search_path = self.project_root / pattern

                if not search_path.exists():
                    continue

                if search_path.is_file():
                    # Single file (e.g., CLAUDE.md)
                    resolved = self._resolve_symlink(search_path)
                    if resolved and not self._is_garbage(resolved):
                        resolved_abs = resolved.resolve()
                        if resolved_abs not in seen_paths:
                            seen_paths.add(resolved_abs)
                            inventory[domain].append(resolved)
                else:
                    # Directory - collect .md files
                    files = self._collect_files(search_path)
                    for file in files:
                        file_abs = file.resolve()
                        if file_abs not in seen_paths:
                            seen_paths.add(file_abs)
                            inventory[domain].append(file)

        return inventory

    def _get_domain_search_paths(self, domain: str) -> List[Path]:
        """Get search paths for domain from config or defaults.

        Args:
            domain: Domain name (prps, examples, claude_md, settings, commands, memories)

        Returns:
            List of Path objects to search for the domain
        """
        # If config available, use domain-specific sources
        if self.config:
            try:
                sources = self.config.get_domain_legacy_sources(domain)
                if sources:
                    return sources
            except (KeyError, ValueError):
                pass

        # Fallback to defaults for backward compatibility
        # Note: All paths are specified in config.yml. These defaults ensure
        # backward compatibility if config.yml is unavailable.
        # CRITICAL: Include bare context-engineering/ to detect root-level files
        defaults = {
            "prps": [Path("PRPs/"), Path("context-engineering/PRPs/"), Path("context-engineering/")],
            "examples": [Path("examples/"), Path("context-engineering/examples/"), Path("context-engineering/")],
            "claude_md": [Path("CLAUDE.md")],
            "settings": [Path(".claude/settings.local.json")],
            "commands": [Path(".claude/commands/")],
            "memories": [Path(".serena/memories/")]
        }
        return defaults.get(domain, [])

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
