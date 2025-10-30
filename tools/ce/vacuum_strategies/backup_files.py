"""Strategy for finding backup files."""

from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class BackupFileStrategy(BaseStrategy):
    """Find backup files from editors and git."""

    BACKUP_PATTERNS = [
        "**/*.bak",
        "**/*~",
        "**/*.orig",
        "**/*.rej",
    ]

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find all backup files.

        Returns:
            List of CleanupCandidate objects with HIGH confidence (100%)
        """
        candidates = []

        for pattern in self.BACKUP_PATTERNS:
            for path in self.project_root.glob(pattern):
                if not path.exists():
                    continue

                # Skip if protected
                if self.is_protected(path):
                    continue

                candidate = CleanupCandidate(
                    path=path,
                    reason=f"Backup file: {pattern}",
                    confidence=100,  # HIGH confidence - safe to delete
                    size_bytes=self.get_file_size(path),
                    last_modified=self.get_last_modified(path),
                    git_history=self.get_git_history(path),
                )
                candidates.append(candidate)

        return candidates
