"""LLM batch analyzer for uncertain vacuum candidates."""

import os
from pathlib import Path
from typing import List, Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import CleanupCandidate


class LLMBatchAnalyzer:
    """Batch analyze uncertain vacuum candidates using Claude Haiku.

    Only processes MEDIUM confidence (40-70) candidates.
    Batches 10-15 docs per API call for cost efficiency.
    """

    MAX_DOCS_PER_BATCH = 15  # Haiku 200K context limit
    CONFIDENCE_THRESHOLD = (40, 70)  # MEDIUM tier (40-70 out of 100)
    MODEL = "claude-3-haiku-20240307"
    TIMEOUT_SECONDS = 30

    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM batch analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception:
                # If client init fails, analyzer will be disabled
                pass

    def is_available(self) -> bool:
        """Check if LLM analyzer is available.

        Returns:
            True if Anthropic SDK installed and API key configured
        """
        return self.client is not None

    def analyze_batch(self, candidates: List[CleanupCandidate]) -> List[CleanupCandidate]:
        """Analyze candidates in batches.

        Filters to MEDIUM confidence (40-70), batches into groups of 10-15,
        and boosts confidence based on Haiku responses.

        Args:
            candidates: List of all candidates

        Returns:
            List of candidates with adjusted confidence (boosted if YES)
        """
        if not self.is_available():
            # LLM not available, return originals unchanged
            return candidates

        # Filter uncertain candidates (40-70)
        min_conf, max_conf = self.CONFIDENCE_THRESHOLD
        uncertain = [c for c in candidates if min_conf <= c.confidence < max_conf]
        certain = [c for c in candidates if c.confidence < min_conf or c.confidence >= max_conf]

        if not uncertain:
            return candidates  # No uncertain candidates

        # Process uncertain candidates in batches
        results = []
        for batch in self._create_batches(uncertain):
            batch_results = self._analyze_single_batch(batch)
            results.extend(batch_results)

        # Combine certain + analyzed uncertain
        return certain + results

    def _create_batches(self, candidates: List[CleanupCandidate]) -> List[List[CleanupCandidate]]:
        """Split candidates into batches of MAX_DOCS_PER_BATCH.

        Args:
            candidates: List of candidates to batch

        Returns:
            List of batches (each batch is a list of candidates)
        """
        batches = []
        for i in range(0, len(candidates), self.MAX_DOCS_PER_BATCH):
            batch = candidates[i:i + self.MAX_DOCS_PER_BATCH]
            batches.append(batch)
        return batches

    def _analyze_single_batch(self, candidates: List[CleanupCandidate]) -> List[CleanupCandidate]:
        """Analyze single batch of candidates using Haiku.

        Args:
            candidates: List of candidates (10-15 max)

        Returns:
            List of candidates with adjusted confidence
        """
        # Build prompt
        prompt = self._build_batch_prompt(candidates)

        try:
            # Call Haiku API
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=1024,
                timeout=self.TIMEOUT_SECONDS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text
            return self._parse_batch_response(response_text, candidates)

        except Exception as e:
            # API failure - return original candidates
            print(f"⚠️ LLM batch analysis failed: {e}")
            print(f"   Keeping original confidence for {len(candidates)} candidates")
            return candidates

    def _build_batch_prompt(self, candidates: List[CleanupCandidate]) -> str:
        """Build prompt for batch analysis.

        Format:
        For each doc below, output ONE line: YES, NO, or PARTIAL

        1. Doc: PRPs/feature-requests/auth-idea.md
           PRP: PRPs/executed/PRP-23-auth-system.md
           Question: Does PRP-23 fully implement auth-idea.md?

        Output format (one per line):
        1. YES
        2. NO

        Args:
            candidates: List of candidates to analyze

        Returns:
            Batch prompt string
        """
        lines = [
            "For each doc below, determine if the PRP fully implements/supersedes the doc.",
            "Output ONE line per doc: YES (fully implemented), NO (unrelated), or PARTIAL (partially implemented).\n"
        ]

        for i, candidate in enumerate(candidates, 1):
            lines.append(f"\n{i}. Doc: {candidate.path}")
            if hasattr(candidate, 'superseded_by') and candidate.superseded_by:
                lines.append(f"   PRP: {candidate.superseded_by}")
                prp_name = candidate.superseded_by.stem if hasattr(candidate.superseded_by, 'stem') else str(candidate.superseded_by)
                doc_name = candidate.path.name
                lines.append(f"   Question: Does {prp_name} fully implement {doc_name}?")
            else:
                lines.append(f"   No PRP specified")

        lines.append(f"\n\nOutput format (one per line):")
        for i in range(1, len(candidates) + 1):
            lines.append(f"{i}. [YES/NO/PARTIAL]")

        return "\n".join(lines)

    def _parse_batch_response(self, response: str, candidates: List[CleanupCandidate]) -> List[CleanupCandidate]:
        """Parse Haiku batch response.

        Expected format:
        1. YES
        2. NO
        3. PARTIAL

        Args:
            response: Haiku response text
            candidates: Original candidates

        Returns:
            Candidates with adjusted confidence
        """
        lines = response.strip().split('\n')
        results = []

        for i, candidate in enumerate(candidates):
            if i >= len(lines):
                # Not enough responses, keep original
                results.append(candidate)
                continue

            line = lines[i].strip().upper()
            verdict = None

            if 'YES' in line:
                verdict = 'YES'
            elif 'NO' in line:
                verdict = 'NO'
            elif 'PARTIAL' in line:
                verdict = 'PARTIAL'

            # Apply confidence boost
            if verdict == 'YES':
                # Boost to HIGH confidence (90)
                candidate.confidence = 90.0
                # Update reason to include LLM verdict
                candidate.reason += f" (LLM verified: {verdict})"
            # NO or PARTIAL: keep original confidence (no boost)

            results.append(candidate)

        return results
