"""Drift history tracking and analysis.

Provides tools for querying and analyzing architectural drift decisions
across PRPs, creating an audit trail for pattern conformance validation.
"""

import yaml
import re
import logging
from glob import glob
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def parse_drift_justification(prp_path: str) -> Optional[Dict[str, Any]]:
    """Extract DRIFT_JUSTIFICATION from PRP YAML header.

    Args:
        prp_path: Path to PRP markdown file

    Returns:
        {
            "prp_id": "PRP-001",
            "prp_name": "Level 4 Pattern Conformance",
            "drift_decision": {
                "score": 45.2,
                "action": "accepted",
                "justification": "...",
                "timestamp": "2025-10-12T15:30:00Z",
                "category_breakdown": {...},
                "reviewer": "human"
            }
        }
        Returns None if no drift_decision found

    Raises:
        FileNotFoundError: If PRP file doesn't exist
        ValueError: If YAML header malformed
    """
    path = Path(prp_path)
    if not path.exists():
        raise FileNotFoundError(
            f"PRP file not found: {prp_path}\n"
            f"🔧 Troubleshooting: Check PRP path and ensure file exists"
        )

    try:
        with open(path, 'r') as f:
            content = f.read()

        # Extract YAML header (between --- markers)
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            raise ValueError(f"No YAML header found in {prp_path}")

        yaml_content = yaml_match.group(1)
        header = yaml.safe_load(yaml_content)

        # Check if drift_decision exists
        if "drift_decision" not in header:
            return None

        return {
            "prp_id": header.get("prp_id", "UNKNOWN"),
            "prp_name": header.get("name", "Unknown PRP"),
            "drift_decision": header["drift_decision"]
        }

    except Exception as e:
        raise ValueError(
            f"Failed to parse PRP YAML: {str(e)}\n"
            f"🔧 Troubleshooting: Verify YAML syntax in {prp_path}"
        ) from e


def get_drift_history(
    last_n: Optional[int] = None,
    prp_id: Optional[str] = None,
    action_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Query drift decision history across all PRPs.

    Args:
        last_n: Return only last N decisions (by timestamp)
        prp_id: Filter by specific PRP ID
        action_filter: Filter by action (accepted, rejected, examples_updated)

    Returns:
        List of drift decisions sorted by timestamp (newest first)

    Example:
        >>> history = get_drift_history(last_n=3)
        >>> history[0]["drift_decision"]["score"]
        45.2
    """
    prp_dirs = ["PRPs/executed", "PRPs/feature-requests"]
    all_decisions = []

    for prp_dir in prp_dirs:
        dir_path = Path(prp_dir)
        if not dir_path.exists():
            continue

        # Find all PRP markdown files
        for prp_file in dir_path.glob("PRP-*.md"):
            try:
                decision = parse_drift_justification(str(prp_file))
                if decision:
                    all_decisions.append(decision)
            except Exception as e:
                logger.warning(f"Skipping {prp_file}: {e}")

    # Apply filters
    if prp_id:
        all_decisions = [d for d in all_decisions if d["prp_id"] == prp_id]

    if action_filter:
        all_decisions = [
            d for d in all_decisions
            if d["drift_decision"]["action"] == action_filter
        ]

    # Sort by timestamp (newest first)
    all_decisions.sort(
        key=lambda d: d["drift_decision"].get("timestamp", ""),
        reverse=Trueafter
    )

    # Apply limit
    if last_n:
        all_decisions = all_decisions[:last_n]

    return all_decisions


def drift_summary() -> Dict[str, Any]:
    """Generate aggregate statistics for all drift decisions.

    Returns:
        {
            "total_prps": 15,
            "prps_with_drift": 8,
            "decisions": {
                "accepted": 5,
                "rejected": 2,
                "examples_updated": 1
            },
            "avg_drift_score": 23.7,
            "score_distribution": {
                "low": 3,      # 0-10%
                "medium": 4,   # 10-30%
                "high": 1      # 30%+
            },
            "category_breakdown": {
                "code_structure": {"avg": 25.0, "count": 8},
                "error_handling": {"avg": 15.0, "count": 8},
                "naming_conventions": {"avg": 30.0, "count": 8}
            },
            "reviewer_breakdown": {
                "human": 6,
                "auto_accept": 2,
                "auto_fix": 0
            }
        }
    """
    history = get_drift_history()

    if not history:
        return {
            "total_prps": 0,
            "prps_with_drift": 0,
            "decisions": {},
            "avg_drift_score": 0.0,
            "score_distribution": {},
            "category_breakdown": {},
            "reviewer_breakdown": {}
        }

    # Count decisions by action
    decisions = {}
    for h in history:
        action = h["drift_decision"]["action"]
        decisions[action] = decisions.get(action, 0) + 1

    # Calculate average drift score
    scores = [h["drift_decision"]["score"] for h in history]
    avg_drift = sum(scores) / len(scores)

    # Score distribution
    score_dist = {"low": 0, "medium": 0, "high": 0}
    for score in scores:
        if score <= 10:
            score_dist["low"] += 1
        elif score <= 30:
            score_dist["medium"] += 1
        else:
            score_dist["high"] += 1

    # Category breakdown
    categories = {}
    for h in history:
        breakdown = h["drift_decision"].get("category_breakdown", {})
        for cat, score in breakdown.items():
            if cat not in categories:
                categories[cat] = {"total": 0, "count": 0}
            categories[cat]["total"] += score
            categories[cat]["count"] += 1

    category_breakdown = {
        cat: {
            "avg": data["total"] / data["count"],
            "count": data["count"]
        }
        for cat, data in categories.items()
    }

    # Reviewer breakdown
    reviewers = {}
    for h in history:
        reviewer = h["drift_decision"].get("reviewer", "unknown")
        reviewers[reviewer] = reviewers.get(reviewer, 0) + 1

    return {
        "total_prps": len(history),
        "prps_with_drift": len(history),
        "decisions": decisions,
        "avg_drift_score": round(avg_drift, 2),
        "score_distribution": score_dist,
        "category_breakdown": category_breakdown,
        "reviewer_breakdown": reviewers
    }


def show_drift_decision(prp_id: str) -> Dict[str, Any]:
    """Display detailed drift decision for specific PRP.

    Args:
        prp_id: PRP identifier (e.g., "PRP-001")

    Returns:
        Full drift decision with metadata

    Raises:
        ValueError: If PRP not found or has no drift decision
    """
    history = get_drift_history(prp_id=prp_id)

    if not history:
        raise ValueError(
            f"No drift decision found for {prp_id}\n"
            f"🔧 Troubleshooting: Verify PRP ID and check if drift decision exists in YAML header"
        )

    return history[0]


def compare_drift_decisions(prp_id_1: str, prp_id_2: str) -> Dict[str, Any]:
    """Compare drift decisions between two PRPs.

    Args:
        prp_id_1: First PRP ID
        prp_id_2: Second PRP ID

    Returns:
        {
            "prp_1": {...},
            "prp_2": {...},
            "comparison": {
                "score_diff": 12.5,
                "same_action": True,
                "common_categories": ["code_structure", "naming_conventions"],
                "divergent_categories": ["error_handling"]
            }
        }

    Raises:
        ValueError: If either PRP not found or missing drift decision
    """
    decision_1 = show_drift_decision(prp_id_1)
    decision_2 = show_drift_decision(prp_id_2)

    # Calculate comparison
    score_diff = abs(
        decision_1["drift_decision"]["score"] -
        decision_2["drift_decision"]["score"]
    )

    same_action = (
        decision_1["drift_decision"]["action"] ==
        decision_2["drift_decision"]["action"]
    )

    # Category comparison
    cat_1 = set(decision_1["drift_decision"].get("category_breakdown", {}).keys())
    cat_2 = set(decision_2["drift_decision"].get("category_breakdown", {}).keys())

    common_categories = list(cat_1 & cat_2)
    divergent_categories = list(cat_1 ^ cat_2)

    return {
        "prp_1": decision_1,
        "prp_2": decision_2,
        "comparison": {
            "score_diff": round(score_diff, 2),
            "same_action": same_action,
            "common_categories": common_categories,
            "divergent_categories": divergent_categories
        }
    }
