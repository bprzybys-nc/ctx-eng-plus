"""Strategy for finding dead links in documentation."""

import re
from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class DeadLinkStrategy(BaseStrategy):
    """Find dead links in markdown documentation."""

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find markdown files with dead links.

        Note: This strategy reports files with dead links but doesn't
        suggest deleting them - just flagging for manual review.

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

            # Find dead links in this file
            dead_links = self._find_dead_links(md_file)

            if dead_links:
                candidate = CleanupCandidate(
                    path=md_file,
                    reason=f"Contains {len(dead_links)} dead link(s)",
                    confidence=70,  # MEDIUM confidence - report only
                    size_bytes=self.get_file_size(md_file),
                    last_modified=self.get_last_modified(md_file),
                    git_history=self.get_git_history(md_file),
                    references=dead_links,
                )
                candidates.append(candidate)

        return candidates

    def _find_dead_links(self, md_file: Path) -> List[str]:
        """Find dead links in markdown file.

        Args:
            md_file: Path to markdown file

        Returns:
            List of dead link paths
        """
        dead_links = []

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            return dead_links

        # Match markdown links: [text](path)
        link_pattern = r"\[([^\]]+)\]\(([^)]+)\)"
        matches = re.finditer(link_pattern, content)

        for match in matches:
            link_path = match.group(2)

            # Skip URLs (http://, https://, mailto:, etc.)
            if "://" in link_path or link_path.startswith("#"):
                continue

            # Resolve relative path
            target = (md_file.parent / link_path).resolve()

            # Check if target exists
            if not target.exists():
                dead_links.append(link_path)

        return dead_links
