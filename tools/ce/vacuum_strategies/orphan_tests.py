"""Strategy for finding orphaned test files."""

from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate


class OrphanTestStrategy(BaseStrategy):
    """Find test files whose corresponding module no longer exists."""

    def find_candidates(self) -> List[CleanupCandidate]:
        """Find orphaned test files.

        Returns:
            List of CleanupCandidate objects with MEDIUM confidence (60%)
        """
        candidates = []

        # Find all test files
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            return candidates

        for test_file in tests_dir.glob("**/test_*.py"):
            if not test_file.exists() or test_file.is_dir():
                continue

            # Skip if protected
            if self.is_protected(test_file):
                continue

            # Extract module name from test_foo.py -> foo
            module_name = test_file.stem.replace("test_", "")

            # Look for corresponding module in ce/
            module_candidates = [
                self.project_root / "tools" / "ce" / f"{module_name}.py",
                self.project_root / "ce" / f"{module_name}.py",
            ]

            # Check if any corresponding module exists
            module_exists = any(m.exists() for m in module_candidates)

            if not module_exists:
                # Recently active files might be integration tests
                confidence = 60
                if self.is_recently_active(test_file, days=30):
                    confidence = 40

                candidate = CleanupCandidate(
                    path=test_file,
                    reason=f"Orphaned test: no module '{module_name}.py' found",
                    confidence=confidence,  # MEDIUM confidence
                    size_bytes=self.get_file_size(test_file),
                    last_modified=self.get_last_modified(test_file),
                    git_history=self.get_git_history(test_file),
                )
                candidates.append(candidate)

        return candidates
