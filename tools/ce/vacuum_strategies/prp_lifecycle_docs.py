"""Vacuum strategy for PRP lifecycle document detection."""
from pathlib import Path
from typing import List, Optional

from ce.nlp import DocumentSimilarity
from .base import BaseStrategy, CleanupCandidate


class PRPLifecycleDocsStrategy(BaseStrategy):
    """Detects temporary docs throughout PRP lifecycle.

    Detection types:
    1. INITIAL.md → executed PRP
    2. PLAN/ANALYSIS/REPORT → executed PRP
    3. Superseded feature requests → executed PRP
    """

    def __init__(self, project_root: Path, scan_path: Path = None):
        """Initialize strategy with NLP backend.

        Args:
            project_root: Project root directory
            scan_path: Optional scan path (defaults to project_root)
        """
        super().__init__(project_root, scan_path)
        self.nlp = DocumentSimilarity()

    def find_candidates(self) -> List[CleanupCandidate]:
        """Scan for PRP lifecycle docs.

        Returns:
            List of cleanup candidates
        """
        candidates = []

        # Get all executed PRPs (comparison baseline)
        executed_dir = self.project_root / "PRPs" / "executed"
        if not executed_dir.exists():
            return []

        executed_prps = list(executed_dir.glob("PRP-*.md"))
        if not executed_prps:
            return []

        # Scan feature-requests recursively
        feature_requests_dir = self.project_root / "PRPs" / "feature-requests"
        if not feature_requests_dir.exists():
            return []

        # Use rglob for recursive scanning
        for md_file in feature_requests_dir.rglob("*.md"):
            # Skip PRP files themselves
            if md_file.name.startswith("PRP-"):
                continue

            # Skip if protected
            if self.is_protected(md_file):
                continue

            # Detect lifecycle doc
            candidate = self._detect_lifecycle_doc(md_file, executed_prps)
            if candidate:
                candidates.append(candidate)

        return candidates

    def _detect_lifecycle_doc(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[CleanupCandidate]:
        """Detect if file is a lifecycle doc.

        Args:
            md_file: File to check
            executed_prps: List of executed PRP files

        Returns:
            CleanupCandidate if match found, None otherwise
        """
        filename = md_file.name

        # Type 1: INITIAL.md files (highest priority)
        if filename == "INITIAL.md":
            return self._check_initial_md(md_file, executed_prps)

        # Type 2: Temporary analysis docs
        if any(filename.startswith(prefix) for prefix in ["PLAN-", "ANALYSIS-", "REPORT-"]):
            return self._check_temporary_doc(md_file, executed_prps)

        # Type 3: Superseded feature requests (content-based)
        return self._check_superseded_request(md_file, executed_prps)

    def _check_initial_md(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[CleanupCandidate]:
        """Check if INITIAL.md has corresponding executed PRP.

        Args:
            md_file: INITIAL.md file
            executed_prps: List of executed PRPs

        Returns:
            CleanupCandidate if HIGH confidence match found
        """
        best_match = None
        best_score = 0.0

        for prp_path in executed_prps:
            similarity = self.nlp.compare(md_file, prp_path)

            if similarity > best_score:
                best_score = similarity
                best_match = prp_path

        # Apply confidence threshold
        if best_score >= 0.75:  # HIGH confidence
            prp_id = best_match.stem.split('-')[1] if best_match else "unknown"
            return CleanupCandidate(
                path=md_file,
                reason=f"Generated as PRP-{prp_id} (NLP similarity: {best_score:.2f})",
                confidence=best_score * 100,  # Convert 0.0-1.0 to 0-100
                size_bytes=self.get_file_size(md_file),
                last_modified=self.get_last_modified(md_file),
                git_history=self.get_git_history(md_file),
                detection_type="INITIAL→PRP",
                superseded_by=best_match
            )

        return None

    def _check_temporary_doc(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[CleanupCandidate]:
        """Check if PLAN/ANALYSIS/REPORT has corresponding PRP.

        Args:
            md_file: Temporary doc file
            executed_prps: List of executed PRPs

        Returns:
            CleanupCandidate if HIGH confidence match found
        """
        best_match = None
        best_score = 0.0

        for prp_path in executed_prps:
            similarity = self.nlp.compare(md_file, prp_path)

            if similarity > best_score:
                best_score = similarity
                best_match = prp_path

        # Apply confidence threshold (slightly lower for temporary docs)
        if best_score >= 0.70:  # HIGH/MEDIUM threshold
            prp_id = best_match.stem.split('-')[1] if best_match else "unknown"

            # Determine confidence tier
            if best_score >= 0.75:
                tier = "HIGH"
            else:
                tier = "MEDIUM"

            return CleanupCandidate(
                path=md_file,
                reason=f"Integrated into PRP-{prp_id} ({tier} confidence, NLP similarity: {best_score:.2f})",
                confidence=best_score * 100,  # Convert 0.0-1.0 to 0-100
                size_bytes=self.get_file_size(md_file),
                last_modified=self.get_last_modified(md_file),
                git_history=self.get_git_history(md_file),
                detection_type="Temporary→PRP",
                superseded_by=best_match
            )

        return None

    def _check_superseded_request(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[CleanupCandidate]:
        """Check if feature request superseded by executed PRP.

        Args:
            md_file: Feature request file
            executed_prps: List of executed PRPs

        Returns:
            CleanupCandidate if MEDIUM+ confidence match found
        """
        best_match = None
        best_score = 0.0

        for prp_path in executed_prps:
            similarity = self.nlp.compare(md_file, prp_path)

            if similarity > best_score:
                best_score = similarity
                best_match = prp_path

        # Apply confidence threshold (include MEDIUM for LLM review)
        if best_score >= 0.40:  # MEDIUM or higher
            prp_id = best_match.stem.split('-')[1] if best_match else "unknown"

            # Determine tier
            if best_score >= 0.75:
                tier = "HIGH"
            elif best_score >= 0.40:
                tier = "MEDIUM"
            else:
                tier = "LOW"

            return CleanupCandidate(
                path=md_file,
                reason=f"Superseded by PRP-{prp_id} ({tier} confidence, NLP similarity: {best_score:.2f})",
                confidence=best_score * 100,  # Convert 0.0-1.0 to 0-100
                size_bytes=self.get_file_size(md_file),
                last_modified=self.get_last_modified(md_file),
                git_history=self.get_git_history(md_file),
                detection_type="Superseded",
                superseded_by=best_match
            )

        return None  # <40% confidence, not flagged
