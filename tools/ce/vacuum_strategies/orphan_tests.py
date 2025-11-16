"""Strategy for finding orphaned test files."""

from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate

# Import NLP module for semantic similarity
try:
    from ce.nlp import DocumentSimilarity
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False


class OrphanTestStrategy(BaseStrategy):
    """Find test files whose corresponding module no longer exists."""

    def __init__(self, project_root: Path, scan_path: Path = None):
        """Initialize strategy with NLP support.

        Args:
            project_root: Project root directory
            scan_path: Optional scan path (defaults to project_root)
        """
        super().__init__(project_root, scan_path)

        # Initialize NLP for semantic similarity (if available)
        self.nlp = None
        if NLP_AVAILABLE:
            try:
                self.nlp = DocumentSimilarity()
            except Exception:
                # If NLP init fails, continue without it
                pass

        # Cache executed PRPs for similarity comparison
        self._executed_prps = None

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

                reason = f"Orphaned test: no module '{module_name}.py' found"

                # Apply NLP boost if high semantic similarity to executed PRPs
                if self.nlp and confidence < 100:
                    similarity = self._get_max_similarity_to_prps(test_file)
                    if similarity >= 0.7:
                        nlp_boost = 20
                        confidence = min(100, confidence + nlp_boost)
                        reason += f", NLP similarity {similarity:.2f}"

                candidate = CleanupCandidate(
                    path=test_file,
                    reason=reason,
                    confidence=confidence,  # MEDIUM confidence
                    size_bytes=self.get_file_size(test_file),
                    last_modified=self.get_last_modified(test_file),
                    git_history=self.get_git_history(test_file),
                )
                candidates.append(candidate)

        return candidates

    def _get_executed_prps(self) -> List[Path]:
        """Get list of executed PRPs (cached).

        Returns:
            List of paths to executed PRPs
        """
        if self._executed_prps is None:
            executed_dir = self.project_root / "PRPs" / "executed"
            if executed_dir.exists():
                self._executed_prps = list(executed_dir.glob("PRP-*.md"))
            else:
                self._executed_prps = []
        return self._executed_prps

    def _get_max_similarity_to_prps(self, doc_path: Path) -> float:
        """Compute maximum semantic similarity to executed PRPs.

        Args:
            doc_path: Path to document to check

        Returns:
            Maximum similarity score (0.0-1.0), or 0.0 if NLP unavailable
        """
        if not self.nlp:
            return 0.0

        executed_prps = self._get_executed_prps()
        if not executed_prps:
            return 0.0

        max_similarity = 0.0
        for prp_path in executed_prps:
            try:
                similarity = self.nlp.compare(doc_path, prp_path)
                if similarity > max_similarity:
                    max_similarity = similarity
            except Exception:
                # Skip if comparison fails
                continue

        return max_similarity
