"""Context management: sync, health checks, pruning."""

from typing import Dict, Any, List
from .core import run_cmd, git_status, git_diff
from .validate import validate_level_1, validate_level_2


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
    total_result = run_cmd("git ls-files | wc -l", capture_output=True)
    if not total_result["success"]:
        raise RuntimeError(
            f"Failed to count tracked files: {total_result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure git is working correctly"
        )

    total_files = int(total_result["stdout"].strip())
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
        drift_score = sync_result["drift_score"]
        drift_level = sync_result["drift_level"]

        if drift_level == "HIGH":
            recommendations.append(
                f"High context drift ({drift_score:.1%}) - run: ce context sync"
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
        "drift_score": drift_score,
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
