"""Examples blending strategy with semantic deduplication."""

import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional

from ce.blending.llm_client import BlendingLLM

logger = logging.getLogger(__name__)


class ExamplesBlendStrategy:
    """
    Blend framework and target examples with semantic deduplication.

    Philosophy: "Copy ours + skip if target has equivalent"

    Process:
    1. Hash deduplication: Skip framework examples with identical hash
    2. Semantic deduplication: Skip framework examples >90% similar to target
    3. Copy remaining framework examples to target

    Usage:
        >>> strategy = ExamplesBlendStrategy(llm_client)
        >>> result = strategy.blend(framework_examples_dir, target_examples_dir, context)
    """

    def __init__(self, llm_client: BlendingLLM, similarity_threshold: float = 0.9):
        """
        Initialize examples blending strategy.

        Args:
            llm_client: BlendingLLM instance for semantic comparison
            similarity_threshold: Similarity threshold 0.0-1.0 (default: 0.9)
        """
        self.llm = llm_client
        self.threshold = similarity_threshold
        logger.debug(f"ExamplesBlendStrategy initialized (threshold={self.threshold})")

    def blend(
        self,
        framework_dir: Path,
        target_dir: Path,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Blend framework and target examples.

        Args:
            framework_dir: Framework examples directory (.ce/examples/)
            target_dir: Target examples directory (examples/)
            context: Optional context dict (backup_dir, dry_run, etc.)

        Returns:
            Dict with:
                - copied: List of copied example files
                - skipped_hash: List of examples skipped (exact duplicate)
                - skipped_similar: List of examples skipped (>threshold similar)
                - errors: List of error messages
                - token_usage: Dict with total input/output tokens

        Raises:
            ValueError: If framework_dir or target_dir invalid
        """
        if not framework_dir.is_dir():
            raise ValueError(f"Framework examples dir not found: {framework_dir}")

        # Create target dir if not exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Get all framework examples
        framework_examples = self._get_examples(framework_dir)
        target_examples = self._get_examples(target_dir)

        logger.info(
            f"Blending examples: {len(framework_examples)} framework, "
            f"{len(target_examples)} target"
        )

        # Track results
        copied = []
        skipped_hash = []
        skipped_similar = []
        errors = []

        # Build target hash set for O(1) lookup
        target_hashes = self._build_hash_set(target_examples)

        # Process each framework example
        for fw_example in framework_examples:
            try:
                # Phase 1: Hash deduplication
                fw_hash = self._hash_file(fw_example)
                if fw_hash in target_hashes:
                    logger.debug(f"Skip {fw_example.name} (exact duplicate)")
                    skipped_hash.append(fw_example.name)
                    continue

                # Phase 2: Semantic deduplication
                is_duplicate, similar_file = self._check_semantic_similarity(
                    fw_example, target_examples
                )
                if is_duplicate:
                    logger.debug(
                        f"Skip {fw_example.name} (similar to {similar_file})"
                    )
                    skipped_similar.append(fw_example.name)
                    continue

                # Phase 3: Copy framework example
                target_path = target_dir / fw_example.name
                if context and context.get("dry_run"):
                    logger.info(f"[DRY RUN] Would copy {fw_example.name}")
                else:
                    target_path.write_text(fw_example.read_text())
                    logger.info(f"✓ Copied {fw_example.name}")
                copied.append(fw_example.name)

            except Exception as e:
                error_msg = f"Failed to process {fw_example.name}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
                # Continue processing remaining examples

        # Get token usage
        token_usage = self.llm.get_token_usage()

        logger.info(
            f"Examples blending complete: {len(copied)} copied, "
            f"{len(skipped_hash)} hash-skipped, {len(skipped_similar)} similarity-skipped"
        )

        return {
            "copied": copied,
            "skipped_hash": skipped_hash,
            "skipped_similar": skipped_similar,
            "errors": errors,
            "token_usage": token_usage
        }

    def _get_examples(self, examples_dir: Path) -> List[Path]:
        """Get all .md files in examples directory (non-recursive)."""
        if not examples_dir.exists():
            return []
        return [f for f in examples_dir.iterdir() if f.suffix == ".md" and f.is_file()]

    def _hash_file(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def _build_hash_set(self, examples: List[Path]) -> Set[str]:
        """Build set of file hashes for O(1) lookup."""
        return {self._hash_file(ex) for ex in examples}

    def _check_semantic_similarity(
        self,
        framework_example: Path,
        target_examples: List[Path]
    ) -> tuple:
        """
        Check if framework example is semantically similar to any target example.

        Uses Haiku for fast, cheap comparison.

        Args:
            framework_example: Framework example file
            target_examples: List of target example files

        Returns:
            Tuple of (is_duplicate, similar_file_name)
            - is_duplicate: True if any target example >threshold similar
            - similar_file_name: Name of similar file (or None)
        """
        if not target_examples:
            return (False, None)

        # Extract comparison content from framework example
        fw_content = self._extract_comparison_content(framework_example)

        # Compare against each target example
        for target_example in target_examples:
            target_content = self._extract_comparison_content(target_example)

            # Call Haiku via BlendingLLM
            try:
                result = self.llm.check_similarity(
                    fw_content, target_content, threshold=self.threshold
                )

                if result["similar"]:
                    logger.debug(
                        f"{framework_example.name} similar to {target_example.name} "
                        f"(score: {result['score']:.2f})"
                    )
                    return (True, target_example.name)

            except Exception as e:
                # Log warning but continue (fail open, copy framework example)
                logger.warning(
                    f"Similarity check failed for {framework_example.name} vs "
                    f"{target_example.name}: {e}"
                )
                # Continue to next target example

        # No similar examples found
        return (False, None)

    def _extract_comparison_content(self, example_file: Path) -> str:
        """
        Extract comparison content from example file.

        Returns first 1500 chars (title + description + code snippets).
        This optimizes token usage while preserving semantic meaning.

        Args:
            example_file: Example markdown file

        Returns:
            Comparison content (truncated to 1500 chars)
        """
        content = example_file.read_text()

        # Truncate to 1500 chars for token optimization
        # This typically includes: title, description, first code snippet
        comparison_content = content[:1500]

        # If truncated mid-code-block, add closing fence
        if comparison_content.count("```") % 2 != 0:
            comparison_content += "\n```"

        return comparison_content
