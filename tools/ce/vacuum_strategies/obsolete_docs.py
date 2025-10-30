"""Strategy for finding obsolete documentation."""

import re
from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class ObsoleteDocStrategy(BaseStrategy):
    """Find obsolete documentation files."""

    OBSOLETE_SUFFIXES = [
        "-v1",
        "-v2",
        "-old",
        "-deprecated",
        "-backup",
        ".old",
        ".bak",
    ]

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find obsolete documentation files.

        Returns:
            List of CleanupCandidate objects with MEDIUM confidence (70%)
        """
        candidates = []

        # Find all markdown files
        for md_file in self.project_root.glob("**/*.md"):
            if not md_file.exists() or md_file.is_dir():
                continue

            # Skip if protected
            if self.is_protected(md_file):
                continue

            # Check for versioned/obsolete suffixes
            stem = md_file.stem
            for suffix in self.OBSOLETE_SUFFIXES:
                if stem.endswith(suffix):
                    # Check if newer version exists
                    newer_version = self._find_newer_version(md_file, suffix)

                    # Recently active files get lower confidence
                    confidence = 70
                    if self.is_recently_active(md_file, days=30):
                        confidence = 50

                    reason = f"Versioned/obsolete doc: {suffix} suffix"
                    if newer_version:
                        reason += f" (newer: {newer_version.name})"

                    candidate = CleanupCandidate(
                        path=md_file,
                        reason=reason,
                        confidence=confidence,  # MEDIUM confidence
                        size_bytes=self.get_file_size(md_file),
                        last_modified=self.get_last_modified(md_file),
                        git_history=self.get_git_history(md_file),
                    )
                    candidates.append(candidate)
                    break

        return candidates

    def _find_newer_version(self, old_file: Path, suffix: str) -> Path | None:
        """Try to find newer version of file.

        Args:
            old_file: Path to old versioned file
            suffix: The version suffix (e.g., '-v1')

        Returns:
            Path to newer version if found, None otherwise
        """
        # Remove suffix to get base name
        base_name = old_file.stem.replace(suffix, "")
        parent = old_file.parent

        # Look for file without suffix
        newer_file = parent / f"{base_name}.md"
        if newer_file.exists() and newer_file != old_file:
            return newer_file

        # Look for higher version numbers
        if re.match(r".*-v\d+$", old_file.stem):
            current_version = int(re.search(r"-v(\d+)$", old_file.stem).group(1))
            for i in range(current_version + 1, current_version + 10):
                newer_file = parent / f"{base_name}-v{i}.md"
                if newer_file.exists():
                    return newer_file

        return None
