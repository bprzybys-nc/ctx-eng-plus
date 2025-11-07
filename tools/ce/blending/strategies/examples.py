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
        Blend or migrate examples based on framework availability.

        Dual-Mode Operation:
        - Blend Mode: Framework exists → semantic dedup + copy framework→target
        - Migration Mode: Framework missing → migrate target→.ce/examples/user/

        Args:
            framework_dir: Framework examples directory (.ce/examples/)
            target_dir: Target examples directory (examples/)
            context: Optional context dict (backup_dir, dry_run, target_dir, etc.)

        Returns:
            Dict with blend mode keys (copied, skipped_hash, skipped_similar) OR
            migration mode keys (migrated, skipped, errors, success)
        """
        # Check if framework examples exist
        if not framework_dir.exists() or not framework_dir.is_dir():
            logger.info(f"Framework examples not found - switching to migration mode")
            return self._migrate_user_examples(target_dir, context)

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

    def _migrate_user_examples(
        self,
        source_dir: Path,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Migrate user examples from source to .ce/examples/user/.

        Similar to PRPMoveStrategy but for examples.
        Supports recursive file discovery and all file types.

        Args:
            source_dir: Source examples directory (examples/)
            context: Context dict with target_dir, dry_run, etc.

        Returns:
            Dict with:
                - migrated: Count of migrated files
                - skipped: Count of skipped files (hash duplicate)
                - errors: List of error messages
                - success: True if no errors
                - files_processed: Count for compatibility
        """
        if not source_dir.exists():
            logger.info(f"Source examples directory not found: {source_dir}")
            return {
                "migrated": 0,
                "skipped": 0,
                "errors": [],
                "success": True,
                "files_processed": 0
            }

        # Get target base directory from context
        if not context or "target_dir" not in context:
            raise ValueError("context['target_dir'] required for migration mode")

        target_base = context["target_dir"] / ".ce" / "examples" / "user"
        target_base.mkdir(parents=True, exist_ok=True)

        migrated = 0
        skipped = 0
        errors = []

        # Find all example files recursively (all file types)
        example_files = list(source_dir.rglob("*"))
        example_files = [f for f in example_files if f.is_file()]

        logger.info(f"Migrating {len(example_files)} example files from {source_dir}")

        for source_file in example_files:
            try:
                # Preserve subdirectory structure
                relative_path = source_file.relative_to(source_dir)
                target_file = target_base / relative_path

                # Create parent directories
                target_file.parent.mkdir(parents=True, exist_ok=True)

                # Hash-based deduplication
                if target_file.exists():
                    source_hash = self._hash_file(source_file)
                    target_hash = self._hash_file(target_file)
                    if source_hash == target_hash:
                        logger.debug(f"Skip {source_file.name} (hash duplicate)")
                        skipped += 1
                        continue

                # Copy to target
                if context and context.get("dry_run"):
                    logger.info(f"[DRY RUN] Would migrate {relative_path}")
                else:
                    target_file.write_bytes(source_file.read_bytes())
                    logger.debug(f"✓ Migrated {relative_path}")
                migrated += 1

            except Exception as e:
                error_msg = f"Error processing {source_file.name}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)

        logger.info(
            f"Examples migration complete: {migrated} migrated, {skipped} skipped"
        )

        return {
            "migrated": migrated,
            "skipped": skipped,
            "errors": errors,
            "success": len(errors) == 0,
            "files_processed": migrated
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
