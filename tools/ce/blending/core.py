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
        self.strategies: List[Any] = []  # Registered blend strategies

    def register_strategy(self, strategy: Any) -> None:
        """
        Register a blending strategy.

        Args:
            strategy: Instance of BlendStrategy subclass
        """
        self.strategies.append(strategy)
        logger.debug(f"Registered strategy: {strategy.get_domain_name()}")

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
        """Phase A: Scan legacy locations (stub for PRP-34.2.1)."""
        logger.info("Detection phase not yet implemented (PRP-34.2.1)")
        return {"phase": "detect", "implemented": False}

    def _run_classification(self, target_dir: Path) -> Dict[str, Any]:
        """Phase B: Validate CE patterns (stub for PRP-34.2.2)."""
        logger.info("Classification phase not yet implemented (PRP-34.2.2)")
        return {"phase": "classify", "implemented": False}

    def _run_blending(self, target_dir: Path) -> Dict[str, Any]:
        """Phase C: Blend content (stub for PRP-34.3.x)."""
        logger.info("Blending phase not yet implemented (PRP-34.3.x)")
        return {"phase": "blend", "implemented": False}

    def _run_cleanup(self, target_dir: Path) -> Dict[str, Any]:
        """Phase D: Remove legacy dirs (stub for PRP-34.2.3)."""
        logger.info("Cleanup phase not yet implemented (PRP-34.2.3)")
        return {"phase": "cleanup", "implemented": False}
