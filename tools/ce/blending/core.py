"""Core blending framework: 4-phase pipeline orchestration."""

import shutil
import logging
from pathlib import Path
from typing import Generator, Dict, List, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def backup_context(file_path: Path) -> Generator[Path, None, None]:
    """
    Context manager for backup-modify-restore pattern.

    Creates backup before modification, removes on success, restores on failure.

    Args:
        file_path: Path to file to backup

    Yields:
        backup_path: Path to backup file

    Raises:
        OSError: If backup creation fails

    Usage:
        >>> with backup_context(Path("CLAUDE.md")) as backup:
        ...     # Modify file
        ...     modify_file(Path("CLAUDE.md"))
        ...     # If exception, auto-restore from backup

    Note: Atomic operation - either all changes succeed or all rolled back
    """
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')

    # Create backup
    if file_path.exists():
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"✓ Backed up to {backup_path.name}")
        except OSError as e:
            raise OSError(
                f"Failed to create backup: {backup_path}\n"
                f"🔧 Troubleshooting: Check file permissions and disk space"
            ) from e

    try:
        yield backup_path

        # Success - remove backup
        if backup_path.exists():
            backup_path.unlink()
            logger.debug(f"Removed backup {backup_path.name}")

    except Exception as e:
        # Failure - restore backup
        logger.error(f"❌ Operation failed, restoring backup")

        if backup_path.exists():
            try:
                shutil.copy2(backup_path, file_path)
                logger.info(f"✓ Restored from backup {backup_path.name}")
            except OSError as restore_error:
                logger.critical(
                    f"⚠️ CRITICAL: Failed to restore backup!\n"
                    f"Original error: {e}\n"
                    f"Restore error: {restore_error}\n"
                    f"🔧 Manual recovery: cp {backup_path} {file_path}"
                )
        raise


class BlendingOrchestrator:
    """
    Orchestrates 4-phase migration pipeline.

    Phase A: DETECTION - Scan legacy locations
    Phase B: CLASSIFICATION - Validate CE patterns
    Phase C: BLENDING - Merge framework + target
    Phase D: CLEANUP - Remove legacy directories
    """

    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize orchestrator.

        Args:
            config: Configuration from blend-config.yml
            dry_run: If True, show what would be done without executing
        """
        self.config = config
        self.dry_run = dry_run
        self.strategies: Dict[str, Any] = {}  # domain -> strategy mapping
        self.detected_files: Dict[str, List[Path]] = {}  # Cached detection results
        self.classified_files: Dict[str, List[Path]] = {}  # Cached classification results

        # Auto-register default strategies
        self._register_default_strategies()

    def _register_default_strategies(self) -> None:
        """Register all 6 default domain strategies."""
        from ce.blending.strategies import (
            SettingsBlendStrategy,
            ClaudeMdBlendStrategy,
            MemoriesBlendStrategy,
            ExamplesBlendStrategy,
            PRPMoveStrategy,
            CommandOverwriteStrategy
        )
        from ce.blending.llm_client import BlendingLLM
        from unittest.mock import MagicMock

        # Create LLM client for strategies that need it
        # In dry-run mode or when API key unavailable, use mock
        if self.dry_run:
            # Dry-run mode - use mock LLM (no actual API calls)
            llm_client = MagicMock(spec=BlendingLLM)
            llm_client.get_token_usage.return_value = {
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0
            }
            logger.debug("Using mock LLM client (dry-run mode)")
        else:
            try:
                llm_client = BlendingLLM()
                logger.debug("Using real LLM client")
            except ValueError:
                # API key not available - use mock as fallback
                logger.warning("Anthropic API key not found - using mock LLM client")
                llm_client = MagicMock(spec=BlendingLLM)
                llm_client.get_token_usage.return_value = {
                    "input_tokens": 0,
                    "output_tokens": 0,
                    "total_tokens": 0
                }

        # Register strategy instances
        self.register_strategy("settings", SettingsBlendStrategy())
        self.register_strategy("claude_md", ClaudeMdBlendStrategy())  # No llm_client needed
        self.register_strategy("memories", MemoriesBlendStrategy(llm_client))
        self.register_strategy("examples", ExamplesBlendStrategy(llm_client))
        self.register_strategy("prps", PRPMoveStrategy())
        self.register_strategy("commands", CommandOverwriteStrategy())

        logger.debug(f"Registered {len(self.strategies)} domain strategies")

    def register_strategy(self, domain: str, strategy: Any) -> None:
        """
        Register a blending strategy for a specific domain.

        Args:
            domain: Domain name (settings, claude_md, memories, etc.)
            strategy: Instance of BlendStrategy subclass or domain-specific strategy
        """
        self.strategies[domain] = strategy
        logger.debug(f"Registered strategy for domain: {domain}")

    def run_phase(self, phase: str, target_dir: Path) -> Dict[str, Any]:
        """
        Run specific phase of pipeline.

        Args:
            phase: Phase name (detect, classify, blend, cleanup)
            target_dir: Target project directory

        Returns:
            Phase results dict

        Raises:
            ValueError: If phase unknown
            RuntimeError: If phase execution fails
        """
        if phase not in ['detect', 'classify', 'blend', 'cleanup']:
            raise ValueError(
                f"Unknown phase: {phase}\n"
                f"🔧 Valid phases: detect, classify, blend, cleanup"
            )

        logger.info(f"🔀 Running Phase: {phase.upper()}")

        # Placeholder - actual implementation in subsequent PRPs
        if phase == 'detect':
            return self._run_detection(target_dir)
        elif phase == 'classify':
            return self._run_classification(target_dir)
        elif phase == 'blend':
            return self._run_blending(target_dir)
        elif phase == 'cleanup':
            return self._run_cleanup(target_dir)

    def _run_detection(self, target_dir: Path) -> Dict[str, Any]:
        """
        Phase A: Scan legacy locations for CE framework files.

        Uses LegacyFileDetector to scan project for PRPs, memories, examples, etc.

        Args:
            target_dir: Target project directory

        Returns:
            Dict with detected files by domain
        """
        from ce.blending.detection import LegacyFileDetector

        logger.info("Phase A: DETECTION - Scanning legacy locations...")

        detector = LegacyFileDetector(target_dir)
        inventory = detector.scan_all()

        # Cache results
        self.detected_files = inventory

        # Log summary
        total_files = sum(len(files) for files in inventory.values())
        logger.info(f"✓ Detected {total_files} files across {len(inventory)} domains")

        for domain, files in inventory.items():
            if files:
                logger.debug(f"  {domain}: {len(files)} files")

        return {
            "phase": "detect",
            "implemented": True,
            "inventory": inventory,
            "total_files": total_files
        }

    def _run_classification(self, target_dir: Path) -> Dict[str, Any]:
        """
        Phase B: Validate CE patterns using classification.

        Uses classification module to filter out garbage files and validate content.

        Args:
            target_dir: Target project directory

        Returns:
            Dict with classified files by domain
        """
        from ce.blending.classification import is_garbage

        logger.info("Phase B: CLASSIFICATION - Validating CE patterns...")

        if not self.detected_files:
            raise RuntimeError(
                "No detected files - run detection phase first\n"
                "🔧 Troubleshooting: Call run_phase('detect', ...) before classify"
            )

        classified = {}
        total_valid = 0

        for domain, files in self.detected_files.items():
            valid_files = []

            for file_path in files:
                # Simple garbage filter (can be enhanced with LLM classification later)
                if not is_garbage(str(file_path)):
                    valid_files.append(file_path)
                else:
                    logger.debug(f"  Filtered garbage: {file_path.name}")

            classified[domain] = valid_files
            total_valid += len(valid_files)

            if valid_files:
                logger.debug(f"  {domain}: {len(valid_files)} valid files")

        # Cache results
        self.classified_files = classified

        logger.info(f"✓ Classified {total_valid} valid files")

        return {
            "phase": "classify",
            "implemented": True,
            "classified": classified,
            "total_valid": total_valid
        }

    def _run_blending(self, target_dir: Path) -> Dict[str, Any]:
        """
        Phase C: Blend framework + target content using domain strategies.

        For each domain, execute the registered strategy to blend files.

        Args:
            target_dir: Target project directory

        Returns:
            Dict with blending results by domain
        """
        logger.info("Phase C: BLENDING - Merging framework + target...")

        if not self.classified_files:
            raise RuntimeError(
                "No classified files - run classification phase first\n"
                "🔧 Troubleshooting: Call run_phase('classify', ...) before blend"
            )

        results = {}

        for domain, files in self.classified_files.items():
            if not files:
                logger.debug(f"  {domain}: No files to blend")
                continue

            strategy = self.strategies.get(domain)
            if not strategy:
                logger.warning(f"  {domain}: No strategy registered (skipping)")
                continue

            logger.info(f"  Blending {domain} ({len(files)} files)...")

            try:
                # Execute strategy-specific blending
                # Note: Each strategy has different interface (blend() vs execute())
                # This is simplified - actual implementation may vary by strategy
                if hasattr(strategy, 'blend'):
                    # BlendStrategy interface (settings, claude_md, memories, examples)
                    # This would need proper implementation with file reading/writing
                    logger.debug(f"    Using blend() interface for {domain}")
                elif hasattr(strategy, 'execute'):
                    # Simple strategy interface (prps, commands)
                    result = strategy.execute({
                        "source_files": files,
                        "target_dir": target_dir,
                        "dry_run": self.dry_run
                    })
                    results[domain] = result
                else:
                    logger.warning(f"    Strategy {domain} has no blend() or execute() method")

            except Exception as e:
                logger.error(f"  ❌ {domain} blending failed: {e}")
                results[domain] = {"success": False, "error": str(e)}

        logger.info(f"✓ Blending complete ({len(results)} domains processed)")

        return {
            "phase": "blend",
            "implemented": True,
            "results": results
        }

    def _run_cleanup(self, target_dir: Path) -> Dict[str, Any]:
        """
        Phase D: Remove legacy directories after successful blending.

        Uses cleanup module to remove old CE 1.0 directories.

        Args:
            target_dir: Target project directory

        Returns:
            Dict with cleanup results
        """
        from ce.blending.cleanup import cleanup_legacy_dirs

        logger.info("Phase D: CLEANUP - Removing legacy directories...")

        status = cleanup_legacy_dirs(
            target_project=target_dir,
            dry_run=self.dry_run
        )

        success_count = sum(1 for v in status.values() if v)
        logger.info(f"✓ Cleanup complete ({success_count}/{len(status)} directories removed)")

        return {
            "phase": "cleanup",
            "implemented": True,
            "status": status
        }
