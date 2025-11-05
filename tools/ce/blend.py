"""Blending operations module."""

import sys
import logging
from pathlib import Path
from typing import Dict, Any

from .blending.core import BlendingOrchestrator

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s'
    )


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load blend configuration from YAML.

    Args:
        config_path: Path to blend-config.yml

    Returns:
        Configuration dict

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"🔧 Create .ce/blend-config.yml (see PRP-34.1.1)"
        )

    import yaml

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if not config or 'domains' not in config:
            raise ValueError("Config missing 'domains' section")

        return config

    except yaml.YAMLError as e:
        raise ValueError(
            f"Invalid YAML config: {e}\n"
            f"🔧 Check syntax: {config_path}"
        ) from e


def run_blend(args) -> int:
    """
    Execute blending operation.

    Args:
        args: Parsed CLI arguments (from argparse.Namespace)

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    # Setup logging first
    setup_logging(getattr(args, 'verbose', False))

    try:
        # Load configuration
        config_path = Path(args.config)
        config = load_config(config_path)

        # Initialize orchestrator
        orchestrator = BlendingOrchestrator(
            config=config,
            dry_run=args.dry_run
        )

        # Determine target directory
        target_dir = Path(args.target_dir).resolve()
        if not target_dir.exists():
            raise ValueError(
                f"Target directory not found: {target_dir}\n"
                f"🔧 Provide valid project directory"
            )

        # Run phases
        if args.all:
            # Run all 4 phases
            phases = ['detect', 'classify', 'blend']
            if not args.skip_cleanup:
                phases.append('cleanup')

            for phase in phases:
                result = orchestrator.run_phase(phase, target_dir)
                logger.info(f"✓ Phase {phase} complete")

                # Interactive mode - ask before next phase
                if args.interactive and phase != phases[-1]:
                    response = input(f"Continue to {phases[phases.index(phase) + 1]}? [Y/n] ")
                    if response.lower() == 'n':
                        logger.info("Stopped by user")
                        return 0

        elif args.phase:
            # Run specific phase
            result = orchestrator.run_phase(args.phase, target_dir)
            logger.info(f"✓ Phase {args.phase} complete")

        elif args.cleanup_only:
            # Run cleanup only (requires prior blend)
            result = orchestrator.run_phase('cleanup', target_dir)
            logger.info("✓ Cleanup complete")

        elif args.rollback:
            # Restore backups
            logger.info("🔄 Rolling back blending operations...")
            # Stub - implement in validation.py (PRP-34.1.1)
            logger.warning("Rollback not yet fully implemented")
            return 1

        else:
            logger.error("No operation specified (use --all, --phase, --cleanup-only, or --rollback)")
            return 1

        logger.info("✅ Blending complete!")
        return 0

    except Exception as e:
        logger.error(f"❌ Blending failed: {e}")
        if getattr(args, 'verbose', False):
            logger.exception("Full traceback:")
        return 1
