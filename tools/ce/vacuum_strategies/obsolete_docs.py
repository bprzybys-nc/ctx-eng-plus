"""Strategy for finding obsolete documentation."""

import re
from pathlib import Path
from typing import List, Optional

from .base import BaseStrategy, CleanupCandidate

# Import NLP module for semantic similarity
try:
    from ce.nlp import DocumentSimilarity
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False


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

    # Temporary analysis doc prefixes (PRP execution artifacts)
    TEMP_DOC_PREFIXES = [
        "ANALYSIS-",
        "CHANGELIST-",
        "REPORT-",
        "IMPLEMENTATION-",
        "DEPLOYMENT",  # DEPLOYMENT.md, DEPLOYMENT_*.md
        "VERIFICATION-",
        "VALIDATION-",
        "DENOISE_",  # DENOISE_*.md artifacts
    ]

    # Temporary analysis doc suffixes
    TEMP_DOC_SUFFIXES = [
        "-PLAN",  # e.g., TOOL-PERMISSION-LOCKDOWN-PLAN.md
        "_SUMMARY",  # e.g., DEPLOYMENT_SUMMARY.md
        "_SOLUTION",  # e.g., CMD_V_IMAGE_PASTE_SOLUTION.md
    ]

    # Temporary analysis doc infix patterns (match anywhere in name)
    TEMP_DOC_INFIXES = [
        "-SUMMARY-",  # e.g., PEER-REVIEW-IMPROVEMENTS-SUMMARY-PRP-29-SERIES.md
        "-REPL",  # Matches REPLAN, REPLKAN, etc.
    ]

    # Content markers indicating temporary/analysis docs
    # Note: Avoid markers that are common in PRPs (like "**status**:")
    TEMP_CONTENT_MARKERS = [
        "temporary analysis",
        "work in progress",
        "wip",
        "draft",
        "todo:",
        "fixme:",
        "execution artifact",
        "analysis for prp-",
        "generated for prp-",
        "artifact from",
        "this document was created to",
        "planning document",
        "**status**: pending approval",  # More specific than just "**status**:"
        "**status**: ready for execution",
        "**status:** pending approval",
        "**completed**:",
        "**remaining work**:",
        "## 📋 executive summary",  # With emoji - more likely to be temp doc
        "## 🎯 execution summary",  # With emoji - more likely to be temp doc
        "**problem**:",
        "**solution**:",
        "## solution options",
        "source plan:",
        "**workflow:**",
        "## improvement statistics",
        "**date**: 20",  # Matches "**Date**: 2025-10-29" in root-level planning docs
        "**date:** 20",  # Matches "**Date:** 2025-10-22"
        "this plan addresses",
        "revised execution plan",
        "replkan",  # REPLAN/REPLKAN pattern
    ]

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
        """Find obsolete documentation files.

        Returns:
            List of CleanupCandidate objects with MEDIUM confidence (70%)
        """
        candidates = []

        # Check for root-level garbage files (all-caps, no extension)
        candidates.extend(self._find_root_garbage_files())

        # Find all markdown files
        for md_file in self.scan_path.glob("**/*.md"):
            if not md_file.exists() or md_file.is_dir():
                continue

            # Skip if protected
            if self.is_protected(md_file):
                continue

            stem = md_file.stem
            name = md_file.name

            # Check for temporary analysis docs (ANALYSIS-*, DEPLOYMENT*, etc.)
            temp_doc_match = self._is_temp_analysis_doc(name, stem)
            content_marker = None

            # If filename doesn't match, check content for temporary markers
            if not temp_doc_match:
                content_marker = self._check_doc_content(md_file)

            if temp_doc_match or content_marker:
                # Combine filename and content analysis
                reason_parts = []
                if temp_doc_match:
                    reason_parts.append(f"filename {temp_doc_match}")
                if content_marker:
                    reason_parts.append(f"content: {content_marker}")

                # Recently active files get lower confidence
                confidence = 70
                if self.is_recently_active(md_file, days=30):
                    confidence = 55

                # Apply NLP boost if high semantic similarity to executed PRPs
                if self.nlp and confidence < 100:
                    similarity = self._get_max_similarity_to_prps(md_file)
                    if similarity >= 0.7:
                        nlp_boost = 20  # +20% boost
                        confidence = min(100, confidence + nlp_boost)
                        reason_parts.append(f"NLP similarity {similarity:.2f}")

                reason = f"Temporary analysis doc: {', '.join(reason_parts)}"

                candidate = CleanupCandidate(
                    path=md_file,
                    reason=reason,
                    confidence=confidence,  # MEDIUM confidence
                    size_bytes=self.get_file_size(md_file),
                    last_modified=self.get_last_modified(md_file),
                    git_history=self.get_git_history(md_file),
                )
                candidates.append(candidate)
                continue

            # Check for versioned/obsolete suffixes
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

                    # Apply NLP boost if high semantic similarity to executed PRPs
                    if self.nlp and confidence < 100:
                        similarity = self._get_max_similarity_to_prps(md_file)
                        if similarity >= 0.7:
                            nlp_boost = 20
                            confidence = min(100, confidence + nlp_boost)
                            reason += f", NLP similarity {similarity:.2f}"

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

    def _is_temp_analysis_doc(self, name: str, stem: str) -> str | None:
        """Check if filename matches temporary analysis doc patterns.

        Args:
            name: Full filename (e.g., DEPLOYMENT.md)
            stem: Filename without extension (e.g., DEPLOYMENT)

        Returns:
            Pattern description if match, None otherwise
        """
        # Check prefixes
        for prefix in self.TEMP_DOC_PREFIXES:
            if stem.startswith(prefix):
                return f"prefix '{prefix}'"

        # Check suffixes
        for suffix in self.TEMP_DOC_SUFFIXES:
            if stem.endswith(suffix):
                return f"suffix '{suffix}'"

        # Check infixes (match anywhere in name)
        for infix in self.TEMP_DOC_INFIXES:
            if infix in stem:
                return f"infix '{infix}'"

        return None

    def _check_doc_content(self, file: Path) -> str | None:
        """Check document content for temporary markers.

        Reads first 20 lines and looks for markers like "WIP", "DRAFT", "TODO", etc.

        Args:
            file: Path to markdown file

        Returns:
            Marker description if found, None otherwise
        """
        try:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                # Read first 20 lines
                lines = []
                for i, line in enumerate(f):
                    if i >= 20:
                        break
                    lines.append(line.lower())

                content = " ".join(lines)

                # Check for temporary markers
                for marker in self.TEMP_CONTENT_MARKERS:
                    if marker in content:
                        return f"'{marker}' found"

        except Exception:
            # If we can't read the file, skip content check
            pass

        return None

    def _find_root_garbage_files(self) -> List[CleanupCandidate]:
        """Find garbage files in project root.

        Looks for:
        - All-caps files with no extension (e.g., VERSION)
        - Other temporary tracking files

        Returns:
            List of CleanupCandidate objects
        """
        candidates = []

        # Scan only project root (not subdirectories)
        for file in self.project_root.iterdir():
            if not file.is_file():
                continue

            # Skip if protected
            if self.is_protected(file):
                continue

            name = file.name
            stem = file.stem

            # Check for all-caps files with no extension
            if "." not in name and name.isupper() and len(name) > 1:
                # Skip known good all-caps files (should be in PROTECTED_PATTERNS but double-check)
                if name in ["LICENSE", "MAKEFILE", "VERSION"]:
                    continue

                confidence = 65  # MEDIUM confidence
                if self.is_recently_active(file, days=30):
                    confidence = 50

                candidate = CleanupCandidate(
                    path=file,
                    reason=f"Root-level all-caps file with no extension",
                    confidence=confidence,
                    size_bytes=self.get_file_size(file),
                    last_modified=self.get_last_modified(file),
                    git_history=self.get_git_history(file),
                )
                candidates.append(candidate)

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
