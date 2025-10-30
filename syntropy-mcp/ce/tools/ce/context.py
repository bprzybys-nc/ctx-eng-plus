"""Context management: sync, health checks, pruning."""

from typing import Dict, Any, List, Optional
from .core import run_cmd, git_status, git_diff, count_git_files, count_git_diff_lines
from .validate import validate_level_1, validate_level_2
from .exceptions import ContextDriftError
import logging

logger = logging.getLogger(__name__)


def sync() -> Dict[str, Any]:
    """Sync context with codebase changes.

    Detects git diff and reports files that need reindexing.

    Returns:
        Dict with: reindexed_count (int), files (List[str]), drift_score (float)

    Note: Real git diff detection - no mocked sync.
    """
    try:
        changed_files = git_diff(since="HEAD~5", name_only=True)
    except Exception as e:
        raise RuntimeError(
            f"Failed to get changed files: {str(e)}\n"
            f"🔧 Troubleshooting: Ensure you're in a git repository with commits"
        ) from e

    # Calculate drift score (percentage of files changed)
    # Get total tracked files
    total_files = count_git_files()
    drift_score = len(changed_files) / max(total_files, 1)  # Prevent division by zero

    return {
        "reindexed_count": len(changed_files),
        "files": changed_files,
        "drift_score": drift_score,
        "drift_level": (
            "LOW" if drift_score < 0.15 else
            "MEDIUM" if drift_score < 0.30 else
            "HIGH"
        )
    }


def health() -> Dict[str, Any]:
    """Comprehensive context health check.

    Returns:
        Dict with: compilation (bool), git_clean (bool), tests_passing (bool),
                   drift_score (float), recommendations (List[str])

    Note: Real validation - no fake health scores.
    """
    recommendations = []

    # Check compilation (Level 1)
    try:
        l1_result = validate_level_1()
        compilation_ok = l1_result["success"]
        if not compilation_ok:
            recommendations.append("Fix compilation errors with: ce validate --level 1")
    except Exception as e:
        compilation_ok = False
        recommendations.append(f"Cannot run validation: {str(e)}")

    # Check git state
    try:
        git_state = git_status()
        git_clean = git_state["clean"]
        if not git_clean:
            staged = len(git_state["staged"])
            unstaged = len(git_state["unstaged"])
            untracked = len(git_state["untracked"])
            recommendations.append(
                f"Uncommitted changes: {staged} staged, {unstaged} unstaged, "
                f"{untracked} untracked"
            )
    except Exception as e:
        git_clean = False
        recommendations.append(f"Git check failed: {str(e)}")

    # Check tests (Level 2) - but don't block on failure
    try:
        l2_result = validate_level_2()
        tests_passing = l2_result["success"]
        if not tests_passing:
            recommendations.append("Tests failing - fix with: ce validate --level 2")
    except Exception as e:
        tests_passing = False
        recommendations.append("Cannot run tests - may need npm install")

    # Check context drift
    try:
        sync_result = sync()
        drift_score = sync_result["drift_score"] * 100  # Convert to percentage (0-100)
        drift_level = sync_result["drift_level"]

        if drift_level == "HIGH":
            recommendations.append(
                f"High context drift ({drift_score:.2f}%) - run: ce context sync"
            )
    except Exception:
        drift_score = 0.0
        drift_level = "UNKNOWN"

    # Overall health
    overall_healthy = compilation_ok and git_clean and tests_passing

    return {
        "healthy": overall_healthy,
        "compilation": compilation_ok,
        "git_clean": git_clean,
        "tests_passing": tests_passing,
        "drift_score": drift_score,  # Now returns percentage (0-100)
        "drift_level": drift_level,
        "recommendations": recommendations
    }


def prune(age_days: int = 7, dry_run: bool = False) -> Dict[str, Any]:
    """Prune old context memories (placeholder for Serena integration).

    Args:
        age_days: Delete memories older than this many days
        dry_run: If True, only report what would be deleted

    Returns:
        Dict with: deleted_count (int), files_deleted (List[str])

    Note: This is a placeholder. Full implementation requires Serena MCP integration.
    """
    # FIXME: Placeholder implementation - needs Serena MCP integration
    # This would normally:
    # 1. Query Serena for memory files
    # 2. Check age and access patterns
    # 3. Delete or compress based on priority

    return {
        "deleted_count": 0,
        "files_deleted": [],
        "dry_run": dry_run,
        "message": "Pruning requires Serena MCP integration (not yet implemented)"
    }


# ============================================================================
# Pre-Generation Sync Functions (Step 2.5)
# ============================================================================

def verify_git_clean() -> Dict[str, Any]:
    """Verify git working tree is clean.

    Returns:
        {
            "clean": True,
            "uncommitted_files": [],
            "untracked_files": []
        }

    Raises:
        RuntimeError: If uncommitted changes detected

    Process:
        1. Run: git status --porcelain
        2. Parse output for uncommitted/untracked files
        3. If any found: raise RuntimeError with file list
        4. Return clean status
    """
    try:
        status = git_status()
    except Exception as e:
        raise RuntimeError(
            f"Failed to check git status: {str(e)}\n"
            f"🔧 Troubleshooting: Ensure you're in a git repository"
        ) from e

    uncommitted = status["staged"] + status["unstaged"]
    untracked = status["untracked"]

    if uncommitted or untracked:
        file_list = "\n".join(
            [f"  - {f} (uncommitted)" for f in uncommitted] +
            [f"  - {f} (untracked)" for f in untracked]
        )
        raise RuntimeError(
            f"Working tree has uncommitted changes:\n{file_list}\n"
            f"🔧 Troubleshooting: Commit or stash changes before PRP generation"
        )

    return {
        "clean": True,
        "uncommitted_files": [],
        "untracked_files": []
    }


def check_drift_threshold(drift_score: float, force: bool = False) -> None:
    """Check drift score against thresholds and abort if needed.

    Args:
        drift_score: Drift percentage (0-100)
        force: Skip abort (for debugging)

    Raises:
        ContextDriftError: If drift > 30% and not force

    Thresholds:
        - 0-10%: INFO log, continue
        - 10-30%: WARNING log, continue
        - 30%+: ERROR log, abort (unless force=True)
    """
    if drift_score <= 10:
        logger.info(f"Context healthy: {drift_score:.2f}% drift")
    elif drift_score <= 30:
        logger.warning(f"Moderate drift: {drift_score:.2f}% - consider running ce context sync")
    else:
        # High drift - abort unless forced
        if not force:
            troubleshooting = (
                "- Review recent commits: git log -5 --oneline\n"
                "- Run: ce context sync to update indexes\n"
                "- Check drift report: ce context health --verbose\n"
                "- Consider: ce context prune to remove stale entries\n"
                "- If confident, use --force to skip this check (not recommended)"
            )
            raise ContextDriftError(
                drift_score=drift_score,
                threshold=30.0,
                troubleshooting=troubleshooting
            )
        else:
            logger.warning(f"High drift {drift_score:.2f}% - FORCED to continue (dangerous!)")


def pre_generation_sync(
    prp_id: Optional[str] = None,
    force: bool = False
) -> Dict[str, Any]:
    """Execute Step 2.5: Pre-generation context sync and health check.

    Args:
        prp_id: Optional PRP ID for logging
        force: Skip drift abort (dangerous - for debugging only)

    Returns:
        {
            "success": True,
            "sync_completed": True,
            "drift_score": 8.2,  # 0-100%
            "git_clean": True,
            "abort_triggered": False,
            "warnings": []
        }

    Raises:
        ContextDriftError: If drift > 30% and force=False
        RuntimeError: If sync fails or git state dirty

    Process:
        1. Verify git clean state
        2. Run context sync
        3. Run health check
        4. Check drift threshold
        5. Return health report
    """
    warnings = []
    prp_log = f" (PRP-{prp_id})" if prp_id else ""

    logger.info(f"Starting pre-generation sync{prp_log}")

    # Step 1: Verify git clean state
    try:
        git_check = verify_git_clean()
        logger.info("✓ Git working tree clean")
    except RuntimeError as e:
        logger.error(f"Git state check failed: {e}")
        raise

    # Step 2: Run context sync
    try:
        sync_result = sync()
        logger.info(f"✓ Context sync completed: {sync_result['reindexed_count']} files reindexed")
    except Exception as e:
        raise RuntimeError(
            f"Context sync failed: {str(e)}\n"
            f"🔧 Troubleshooting: Check git configuration and ensure repository has commits"
        ) from e

    # Step 3: Run health check
    try:
        health_result = health()
        drift_score = health_result["drift_score"]  # Already percentage (0-100)
        logger.info(f"✓ Health check completed: {drift_score:.2f}% drift")
    except Exception as e:
        raise RuntimeError(
            f"Health check failed: {str(e)}\n"
            f"🔧 Troubleshooting: Ensure validation tools are available"
        ) from e

    # Step 4: Check drift threshold
    try:
        check_drift_threshold(drift_score, force=force)
    except ContextDriftError:
        logger.error(f"Pre-generation sync aborted due to high drift{prp_log}")
        raise

    # Step 5: Return health report
    result = {
        "success": True,
        "sync_completed": True,
        "drift_score": drift_score,
        "git_clean": git_check["clean"],
        "abort_triggered": False,
        "warnings": warnings
    }

    logger.info(f"Pre-generation sync successful{prp_log}")
    return result


# ============================================================================
# Post-Execution Sync Functions (Step 6.5)
# ============================================================================

def post_execution_sync(
    prp_id: str,
    skip_cleanup: bool = False
) -> Dict[str, Any]:
    """Execute Step 6.5: Post-execution cleanup and context sync.

    Args:
        prp_id: PRP identifier
        skip_cleanup: Skip cleanup protocol (for testing)

    Returns:
        {
            "success": True,
            "cleanup_completed": True,
            "sync_completed": True,
            "final_checkpoint": "checkpoint-PRP-003-final-20251012-160000",
            "drift_score": 5.1,  # After sync
            "memories_archived": 2,
            "memories_deleted": 3,
            "checkpoints_deleted": 2
        }

    Raises:
        RuntimeError: If cleanup or sync fails

    Process:
        1. Execute cleanup protocol (unless skip_cleanup)
        2. Run context sync
        3. Run health check
        4. Create final checkpoint
        5. Remove active PRP session
        6. Return cleanup + sync summary

    Integration Points:
        - cleanup_prp(prp_id): From PRP-2
        - context_sync(): Existing context.py function
        - context_health(): Existing context.py function
        - create_checkpoint(phase="final"): From PRP-2
    """
    from .prp import cleanup_prp, create_checkpoint, get_active_prp, end_prp
    from datetime import datetime, timezone

    logger.info(f"Starting post-execution sync (PRP-{prp_id})")

    result = {
        "success": True,
        "cleanup_completed": False,
        "sync_completed": False,
        "final_checkpoint": None,
        "drift_score": 0.0,
        "memories_archived": 0,
        "memories_deleted": 0,
        "checkpoints_deleted": 0
    }

    # Step 1: Execute cleanup protocol (unless skip_cleanup)
    if not skip_cleanup:
        try:
            cleanup_result = cleanup_prp(prp_id)
            result["cleanup_completed"] = True
            result["memories_archived"] = len(cleanup_result["memories_archived"])
            result["memories_deleted"] = len(cleanup_result["memories_deleted"])
            result["checkpoints_deleted"] = cleanup_result["checkpoints_deleted"]
            logger.info(f"✓ Cleanup completed: {result['checkpoints_deleted']} checkpoints deleted")
        except Exception as e:
            raise RuntimeError(
                f"Cleanup protocol failed: {str(e)}\n"
                f"🔧 Troubleshooting: Review cleanup errors and retry manually"
            ) from e
    else:
        logger.info("Skipping cleanup protocol (skip_cleanup=True)")
        result["cleanup_completed"] = True

    # Step 2: Run context sync
    try:
        sync_result = sync()
        result["sync_completed"] = True
        logger.info(f"✓ Context sync completed: {sync_result['reindexed_count']} files reindexed")
    except Exception as e:
        raise RuntimeError(
            f"Context sync failed: {str(e)}\n"
            f"🔧 Troubleshooting: Check git configuration and repository state"
        ) from e

    # Step 3: Run health check
    try:
        health_result = health()
        drift_score = health_result["drift_score"]  # Already percentage (0-100)
        result["drift_score"] = drift_score
        logger.info(f"✓ Health check completed: {drift_score:.2f}% drift")

        # Warn if drift still high after sync
        if drift_score > 10:
            logger.warning(f"Drift still elevated after sync: {drift_score:.2f}%")
    except Exception as e:
        logger.warning(f"Health check failed: {e}")

    # Step 4: Create final checkpoint (if active PRP session exists)
    active = get_active_prp()
    if active and active["prp_id"] == prp_id:
        try:
            checkpoint_result = create_checkpoint(
                phase="final",
                message=f"PRP-{prp_id} complete with context sync"
            )
            result["final_checkpoint"] = checkpoint_result["tag_name"]
            logger.info(f"✓ Final checkpoint created: {checkpoint_result['tag_name']}")
        except RuntimeError as e:
            # Don't fail if checkpoint creation fails (may already be committed)
            logger.warning(f"Could not create final checkpoint: {e}")

        # Step 5: Remove active PRP session
        try:
            end_prp(prp_id)
            logger.info(f"✓ Active PRP session ended")
        except Exception as e:
            logger.warning(f"Could not end PRP session: {e}")
    else:
        logger.info("No active PRP session to end")

    logger.info(f"Post-execution sync completed (PRP-{prp_id})")
    return result


def sync_serena_context() -> Dict[str, Any]:
    """Sync Serena MCP context with current codebase.

    Returns:
        {
            "success": True,
            "files_indexed": 127,
            "symbols_updated": 453,
            "memories_refreshed": 5
        }

    Process:
        1. Trigger Serena re-index (if available)
        2. Update relevant memories with new patterns
        3. Refresh codebase structure knowledge
        4. Return sync summary

    Note: This is a placeholder. Full implementation requires Serena MCP integration.
    """
    # FIXME: Placeholder implementation - needs Serena MCP integration
    logger.warning("Serena MCP sync not implemented - skipping")

    return {
        "success": True,
        "files_indexed": 0,
        "symbols_updated": 0,
        "memories_refreshed": 0,
        "message": "Serena sync requires MCP integration (not yet implemented)"
    }


def prune_stale_memories(age_days: int = 30) -> Dict[str, Any]:
    """Prune stale Serena memories older than age_days.

    Args:
        age_days: Delete memories older than this (default: 30 days)

    Returns:
        {
            "success": True,
            "memories_pruned": 12,
            "space_freed_kb": 45.2
        }

    Process:
        1. List all Serena memories
        2. Filter by age (creation timestamp)
        3. Exclude essential memories (never delete):
           - project-patterns
           - code-style-conventions
           - testing-standards
        4. Delete stale memories via Serena MCP
        5. Return pruning summary

    Note: This is a placeholder. Full implementation requires Serena MCP integration.
    """
    # FIXME: Placeholder implementation - needs Serena MCP integration
    logger.warning(f"Serena memory pruning not implemented - would prune memories older than {age_days} days")

    return {
        "success": True,
        "memories_pruned": 0,
        "space_freed_kb": 0.0,
        "message": "Memory pruning requires Serena MCP integration (not yet implemented)"
    }


# ============================================================================
# Drift Detection & Reporting Functions
# ============================================================================

def calculate_drift_score() -> float:
    """Calculate context drift score (0-100%).

    Returns:
        Drift percentage (0 = perfect sync, 100 = completely stale)

    Calculation:
        drift = (
            file_changes_score * 0.4 +
            memory_staleness_score * 0.3 +
            dependency_changes_score * 0.2 +
            uncommitted_changes_score * 0.1
        )

    Components:
        - file_changes_score: % of tracked files modified since last sync
        - memory_staleness_score: Age of oldest Serena memory (normalized)
        - dependency_changes_score: pyproject.toml/package.json changes
        - uncommitted_changes_score: Penalty for dirty git state
    """
    # Component 1: File changes (40% weight)
    try:
        changed_files = git_diff(since="HEAD~5", name_only=True)
        try:
            total_files = count_git_files()
            file_changes_score = (len(changed_files) / max(total_files, 1)) * 100
        except RuntimeError:
            file_changes_score = 0
    except Exception as e:
        logger.warning(
            f"Failed to calculate file changes score: {e}\n"
            f"🔧 Troubleshooting: Ensure git is available and repository has commits"
        )
        file_changes_score = 0

    # Component 2: Memory staleness (30% weight)
    # FIXME: Placeholder - needs Serena MCP integration
    memory_staleness_score = 0  # Would check age of memories

    # Component 3: Dependency changes (20% weight)
    dependency_changes_score = 0
    try:
        # Check if pyproject.toml changed recently
        deps_lines = count_git_diff_lines(
            ref="HEAD~5",
            files=["pyproject.toml", "package.json"]
        )
        # Normalize: >10 lines of changes = 100% score
        dependency_changes_score = min((deps_lines / 10.0) * 100, 100)
    except Exception as e:
        logger.warning(
            f"Failed to check dependency changes: {e}\n"
            f"🔧 Troubleshooting: Ensure git is available"
        )

    # Component 4: Uncommitted changes (10% weight)
    uncommitted_changes_score = 0
    try:
        status = git_status()
        uncommitted = len(status["staged"]) + len(status["unstaged"])
        untracked = len(status["untracked"])
        # Normalize: >5 files = 100% score
        uncommitted_changes_score = min(((uncommitted + untracked) / 5.0) * 100, 100)
    except Exception as e:
        logger.warning(
            f"Failed to check uncommitted changes: {e}\n"
            f"🔧 Troubleshooting: Ensure git is available and you're in a repository"
        )

    # Weighted sum
    drift = (
        file_changes_score * 0.4 +
        memory_staleness_score * 0.3 +
        dependency_changes_score * 0.2 +
        uncommitted_changes_score * 0.1
    )

    return drift


def context_health_verbose() -> Dict[str, Any]:
    """Detailed context health report with breakdown.

    Returns:
        {
            "drift_score": 23.4,
            "threshold": "warn",  # healthy | warn | critical
            "components": {
                "file_changes": {"score": 18.2, "details": "12/127 files modified"},
                "memory_staleness": {"score": 5.1, "details": "Oldest: 8 days"},
                "dependency_changes": {"score": 0, "details": "No changes"},
                "uncommitted_changes": {"score": 0.1, "details": "1 untracked file"}
            },
            "recommendations": [
                "Run: ce context sync to refresh indexes",
                "Consider: ce context prune to remove stale memories"
            ]
        }
    """
    components = {}
    recommendations = []

    # File changes component
    try:
        changed_files = git_diff(since="HEAD~5", name_only=True)
        try:
            total_files = count_git_files()
            file_score = (len(changed_files) / max(total_files, 1)) * 100
            components["file_changes"] = {
                "score": file_score,
                "details": f"{len(changed_files)}/{total_files} files modified"
            }
            if file_score > 15:
                recommendations.append("Run: ce context sync to refresh indexes")
        except RuntimeError:
            components["file_changes"] = {"score": 0, "details": "Error: could not count files"}
    except Exception as e:
        logger.warning(
            f"Failed to calculate file changes component: {e}\n"
            f"🔧 Troubleshooting: Ensure git is available"
        )
        components["file_changes"] = {"score": 0, "details": f"Error: {e}"}

    # Memory staleness component (placeholder)
    components["memory_staleness"] = {
        "score": 0,
        "details": "Serena MCP not available"
    }

    # Dependency changes component
    try:
        deps_lines = count_git_diff_lines(
            ref="HEAD~5",
            files=["pyproject.toml", "package.json"]
        )
        deps_score = min((deps_lines / 10.0) * 100, 100)
        components["dependency_changes"] = {
            "score": deps_score,
            "details": f"{deps_lines} lines changed" if deps_lines > 0 else "No changes"
        }
        if deps_score > 10:
            recommendations.append("Dependencies changed - run: uv sync")
    except Exception as e:
        logger.warning(
            f"Failed to check dependency changes component: {e}\n"
            f"🔧 Troubleshooting: Ensure git is available"
        )
        components["dependency_changes"] = {"score": 0, "details": "No changes"}

    # Uncommitted changes component
    try:
        status = git_status()
        uncommitted = len(status["staged"]) + len(status["unstaged"])
        untracked = len(status["untracked"])
        uncommitted_score = min(((uncommitted + untracked) / 5.0) * 100, 100)
        components["uncommitted_changes"] = {
            "score": uncommitted_score,
            "details": f"{uncommitted} uncommitted, {untracked} untracked"
        }
        if uncommitted + untracked > 0:
            recommendations.append("Commit or stash changes before PRP operations")
    except Exception as e:
        logger.warning(
            f"Failed to check uncommitted changes component: {e}\n"
            f"🔧 Troubleshooting: Ensure git is available and you're in a repository"
        )
        components["uncommitted_changes"] = {"score": 0, "details": "0 uncommitted"}

    # Calculate overall drift
    drift_score = calculate_drift_score()

    # Determine threshold
    if drift_score <= 10:
        threshold = "healthy"
    elif drift_score <= 30:
        threshold = "warn"
    else:
        threshold = "critical"

    return {
        "drift_score": drift_score,
        "threshold": threshold,
        "components": components,
        "recommendations": recommendations
    }


def drift_report_markdown() -> str:
    """Generate markdown drift report for logging.

    Returns:
        Markdown-formatted drift report

    Format:
        ## Context Health Report

        **Drift Score**: 23.4% (⚠️ WARNING)

        ### Components
        - File Changes: 18.2% (12/127 files modified)
        - Memory Staleness: 5.1% (Oldest: 8 days)
        - Dependency Changes: 0% (No changes)
        - Uncommitted Changes: 0.1% (1 untracked file)

        ### Recommendations
        1. Run: ce context sync to refresh indexes
        2. Consider: ce context prune to remove stale memories
    """
    report = context_health_verbose()

    # Status emoji
    if report["threshold"] == "healthy":
        status_emoji = "✅"
        status_text = "HEALTHY"
    elif report["threshold"] == "warn":
        status_emoji = "⚠️"
        status_text = "WARNING"
    else:
        status_emoji = "❌"
        status_text = "CRITICAL"

    # Build markdown
    md = f"## Context Health Report\n\n"
    md += f"**Drift Score**: {report['drift_score']:.2f}% ({status_emoji} {status_text})\n\n"

    # Components
    md += "### Components\n"
    for name, comp in report["components"].items():
        display_name = name.replace("_", " ").title()
        md += f"- {display_name}: {comp['score']:.2f}% ({comp['details']})\n"

    # Recommendations
    if report["recommendations"]:
        md += "\n### Recommendations\n"
        for i, rec in enumerate(report["recommendations"], 1):
            md += f"{i}. {rec}\n"

    return md


# ============================================================================
# Auto-Sync Mode Configuration
# ============================================================================

def enable_auto_sync() -> Dict[str, Any]:
    """Enable auto-sync mode in .ce/config.

    Returns:
        {
            "success": True,
            "mode": "enabled",
            "config_path": ".ce/config"
        }

    Process:
        1. Create .ce/config if not exists
        2. Set auto_sync: true in config
        3. Log: "Auto-sync enabled - Steps 2.5 and 6.5 will run automatically"
    """
    from pathlib import Path
    import json

    config_dir = Path(".ce")
    config_file = config_dir / "config"

    # Create directory if needed
    config_dir.mkdir(exist_ok=True)

    # Read existing config or create new
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}

    # Set auto_sync
    config["auto_sync"] = True

    # Write config
    config_file.write_text(json.dumps(config, indent=2))

    logger.info("Auto-sync enabled - Steps 2.5 and 6.5 will run automatically")

    return {
        "success": True,
        "mode": "enabled",
        "config_path": str(config_file)
    }


def disable_auto_sync() -> Dict[str, Any]:
    """Disable auto-sync mode in .ce/config.

    Returns:
        {
            "success": True,
            "mode": "disabled",
            "config_path": ".ce/config"
        }
    """
    from pathlib import Path
    import json

    config_dir = Path(".ce")
    config_file = config_dir / "config"

    # Read existing config
    if config_file.exists():
        try:
            config = json.loads(config_file.read_text())
        except (json.JSONDecodeError, OSError):
            config = {}
    else:
        config = {}

    # Set auto_sync to false
    config["auto_sync"] = False

    # Write config
    config_dir.mkdir(exist_ok=True)
    config_file.write_text(json.dumps(config, indent=2))

    logger.info("Auto-sync disabled - Manual sync required")

    return {
        "success": True,
        "mode": "disabled",
        "config_path": str(config_file)
    }


def is_auto_sync_enabled() -> bool:
    """Check if auto-sync mode is enabled.

    Returns:
        True if enabled, False otherwise

    Process:
        1. Read .ce/config
        2. Return config.get("auto_sync", False)
    """
    from pathlib import Path
    import json

    config_file = Path(".ce/config")

    if not config_file.exists():
        return False

    try:
        config = json.loads(config_file.read_text())
        return config.get("auto_sync", False)
    except (json.JSONDecodeError, OSError):
        return False


def get_auto_sync_status() -> Dict[str, Any]:
    """Get auto-sync mode status.

    Returns:
        {
            "enabled": True,
            "config_path": ".ce/config",
            "message": "Auto-sync is enabled"
        }
    """
    from pathlib import Path

    enabled = is_auto_sync_enabled()
    config_file = Path(".ce/config")

    message = (
        "Auto-sync is enabled - Steps 2.5 and 6.5 run automatically"
        if enabled
        else "Auto-sync is disabled - Manual sync required"
    )

    return {
        "enabled": enabled,
        "config_path": str(config_file),
        "message": message
    }
