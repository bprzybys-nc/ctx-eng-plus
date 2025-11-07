"""Core blending framework: 4-phase pipeline orchestration."""

import shutil
import json
import logging
from pathlib import Path
from typing import Generator, Dict, List, Any, Optional
from contextlib import contextmanager

from ce.blending.llm_client import BlendingLLM

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
                    logger.debug(f"    Using blend() interface for {domain}")

                    # Domain-specific I/O and blending
                    if domain == 'settings':
                        # Read JSON files
                        framework_file = target_dir / ".ce" / ".claude" / "settings.local.json"
                        target_file = target_dir / ".claude" / "settings.local.json"

                        if not framework_file.exists():
                            logger.warning(f"  {domain}: Framework file not found: {framework_file}")
                            continue

                        with open(framework_file) as f:
                            framework_content = json.load(f)

                        target_content = None
                        if target_file.exists():
                            with open(target_file) as f:
                                target_content = json.load(f)

                        # Call strategy
                        blended = strategy.blend(
                            framework_content=framework_content,
                            target_content=target_content,
                            context={"target_dir": target_dir, "llm_client": BlendingLLM()}
                        )

                        # Write result
                        target_file.parent.mkdir(parents=True, exist_ok=True)
                        with open(target_file, 'w') as f:
                            json.dump(blended, f, indent=2)

                        results[domain] = {
                            "success": True,
                            "files_processed": 1,
                            "message": f"✓ {domain} blended successfully"
                        }

                    elif domain == 'claude_md':
                        # Read markdown files
                        framework_file = target_dir / ".ce" / "CLAUDE.md"
                        target_file = target_dir / "CLAUDE.md"

                        if not framework_file.exists():
                            logger.warning(f"  {domain}: Framework file not found")
                            continue

                        framework_content = framework_file.read_text()
                        target_content = target_file.read_text() if target_file.exists() else None

                        # Call strategy (needs LLM client)
                        blended = strategy.blend(
                            framework_content=framework_content,
                            target_content=target_content,
                            context={"target_dir": target_dir, "llm_client": BlendingLLM()}
                        )

                        # Write result
                        target_file.write_text(blended)

                        results[domain] = {
                            "success": True,
                            "files_processed": 1,
                            "message": f"✓ {domain} blended successfully"
                        }

                    elif domain in ['memories', 'examples']:
                        # Path-based strategies (handle their own I/O)
                        framework_dir = target_dir / ".ce" / domain

                        # Construct target directory path
                        if domain == "memories":
                            target_domain_dir = target_dir / ".serena" / "memories"
                        else:
                            target_domain_dir = target_dir / domain

                        if not framework_dir.exists():
                            logger.warning(f"  {domain}: Framework directory not found: {framework_dir}")
                            continue

                        # Call strategy with paths (memories expects output_path in context + LLM client)
                        if domain == "memories":
                            result = strategy.blend(
                                framework_content=framework_dir,
                                target_content=target_domain_dir if target_domain_dir.exists() else None,
                                context={"output_path": target_domain_dir, "target_dir": target_dir, "llm_client": BlendingLLM()}
                            )
                        else:  # examples
                            result = strategy.blend(
                                framework_dir=framework_dir,
                                target_dir=target_domain_dir,
                                context={"target_dir": target_dir}
                            )

                        results[domain] = {
                            "success": result.get("success", True),
                            "files_processed": result.get("files_processed", 0),
                            "message": f"✓ {domain} blended successfully"
                        }

                    else:
                        logger.warning(f"  {domain}: Unknown blend() domain")
                        continue
                elif hasattr(strategy, 'execute'):
                    # Simple strategy interface (prps, commands)
                    # Derive source_dir from classified files
                    if not files:
                        logger.debug(f"  {domain}: No files to blend")
                        continue

                    # Find common root directory for all files
                    # For PRPs: files could be in PRPs/, PRPs/executed/, PRPs/feature-requests/, etc.
                    # We need to find the common ancestor (PRPs/)
                    file_paths = [Path(f) for f in files]
                    source_dir = self._find_common_ancestor(file_paths)

                    # Domain-specific parameters
                    if domain == 'prps':
                        params = {
                            "source_dir": source_dir,
                            "target_dir": target_dir / ".ce" / "PRPs"
                        }
                    elif domain == 'commands':
                        params = {
                            "source_dir": source_dir,
                            "target_dir": target_dir / ".claude" / "commands",
                            "backup_dir": target_dir / ".claude" / "commands.backup"
                        }
                    else:
                        # Fallback for unknown strategies
                        params = {
                            "source_files": files,
                            "target_dir": target_dir,
                            "dry_run": self.dry_run
                        }

                    logger.debug(f"    Executing {domain} with params: {params}")
                    result = strategy.execute(params)
                    results[domain] = result
                else:
                    logger.warning(f"    Strategy {domain} has no blend() or execute() method")

            except Exception as e:
                error_msg = f"❌ {domain} blending failed: {e}"
                logger.error(f"  {error_msg}")
                results[domain] = {
                    "success": False,
                    "error": str(e),
                    "message": error_msg
                }

                # Fail fast for critical domains
                if domain in ["settings", "claude_md"]:
                    raise RuntimeError(
                        f"Critical domain '{domain}' failed - cannot continue\n"
                        f"Error: {e}\n"
                        f"🔧 Fix {domain} blending before proceeding"
                    )

        # Check for failures
        failed_domains = [d for d, r in results.items() if not r.get("success", False)]

        if failed_domains:
            logger.warning(f"⚠️  Blending complete with failures ({len(results)} domains processed, {len(failed_domains)} failed)")
        else:
            logger.info(f"✓ Blending complete ({len(results)} domains processed)")

        return {
            "phase": "blend",
            "implemented": True,
            "results": results,
            "success": len(failed_domains) == 0,
            "failed_domains": failed_domains,
            "message": self._format_blend_summary(results)
        }

    def _format_blend_summary(self, results: Dict[str, Any]) -> str:
        """
        Format a summary message for blend results.

        Args:
            results: Dictionary of blend results per domain

        Returns:
            Formatted summary string
        """
        success_count = sum(1 for r in results.values() if r.get("success", False))
        total = len(results)
        failed = [d for d, r in results.items() if not r.get("success", False)]

        summary_parts = []
        for domain, result in results.items():
            if result.get("success", False):
                files = result.get("files_processed", 0)
                summary_parts.append(f"  ✓ {domain} ({files} file{'s' if files != 1 else ''})")
            else:
                error = result.get("error", "Unknown error")
                summary_parts.append(f"  ❌ {domain}: {error}")

        summary = "\n".join(summary_parts)

        if failed:
            header = f"⚠️  Blend completed with failures: {success_count}/{total} domains succeeded\n"
        else:
            header = f"✅ Blend completed successfully: {success_count}/{total} domains\n"

        return header + summary

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

    def _find_common_ancestor(self, paths: List[Path]) -> Path:
        """
        Find common ancestor directory for a list of paths.

        For PRPs in subdirectories (PRPs/executed/, PRPs/feature-requests/),
        returns the common root (PRPs/).

        Args:
            paths: List of file paths

        Returns:
            Common ancestor directory

        Example:
            >>> paths = [Path("PRPs/executed/PRP-1.md"), Path("PRPs/feature-requests/PRP-2.md")]
            >>> _find_common_ancestor(paths)
            Path("PRPs")
        """
        if not paths:
            raise ValueError("Cannot find common ancestor of empty path list")

        # Convert all paths to absolute for comparison
        abs_paths = [p.resolve() for p in paths]

        # Start with first path's parents
        common = abs_paths[0].parent

        # Find common ancestor by checking each parent
        while not all(common in p.parents or p.parent == common for p in abs_paths):
            common = common.parent

            # Safety check - don't go above project root
            if common.parent == common:
                raise RuntimeError(f"Could not find common ancestor for paths: {paths}")

        return common
