"""Strategy for finding temporary files."""

from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class TempFileStrategy(BaseStrategy):
    """Find temporary files that can be safely deleted."""

    TEMP_PATTERNS = [
        "**/*.pyc",
        "**/__pycache__",
        "**/.DS_Store",
        "**/*.swp",
        "**/*.swo",
        "**/.pytest_cache",
        "**/.coverage",
        "**/*.log",
        "**/*.tmp",
    ]

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find all temporary files.

        Returns:
            List of CleanupCandidate objects with HIGH confidence (100%)
        """
        candidates = []

        for pattern in self.TEMP_PATTERNS:
            for path in self.scan_path.glob(pattern):
                if not path.exists():
                    continue

                # Skip if protected (shouldn't happen but safety check)
                if self.is_protected(path):
                    continue

                candidate = CleanupCandidate(
                    path=path,
                    reason=f"Temporary file: {pattern}",
                    confidence=100,  # HIGH confidence - safe to delete
                    size_bytes=self.get_file_size(path),
                    last_modified=self.get_last_modified(path),
                    git_history=self.get_git_history(path),
                )
                candidates.append(candidate)

        return candidates
