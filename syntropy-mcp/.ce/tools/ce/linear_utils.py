"""Linear integration utilities for Context Engineering.

Provides helpers for reading Linear defaults and creating issues with
project-specific configuration.

Configuration Priority (v1.0.0+):
1. config.yml profile.linear (RECOMMENDED)
2. linear-defaults.yml (DEPRECATED - fallback only)
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml
import warnings

from ce.config_utils import load_config, ConfigError, get_profile_value

logger = logging.getLogger(__name__)


def get_linear_defaults() -> Dict[str, Any]:
    """Read Linear defaults from config.yml profile section.

    Configuration Priority:
    1. .ce/config.yml profile.linear (RECOMMENDED)
    2. .ce/linear-defaults.yml (DEPRECATED - fallback)

    Returns:
        Dict with keys: project, assignee, team, default_labels

    Raises:
        ConfigError: If configuration invalid or missing
        RuntimeError: If fallback file parsing fails

    Example:
        defaults = get_linear_defaults()
        print(defaults["project"])  # "MyProject"
    """
    # Find project root (go up from tools/)
    project_root = Path(__file__).parent.parent.parent
    new_config_path = project_root / ".ce" / "config.yml"
    old_config_path = project_root / ".ce" / "linear-defaults.yml"

    # Try new config.yml first (RECOMMENDED)
    if new_config_path.exists():
        try:
            config = load_config(str(new_config_path))

            if "profile" in config and "linear" in config["profile"]:
                logger.debug("Using Linear config from config.yml profile.linear")
                return config["profile"]["linear"]
            else:
                # Config.yml exists but no profile.linear section
                logger.warning(
                    "config.yml missing profile.linear section. "
                    "Falling back to linear-defaults.yml"
                )
        except ConfigError as e:
            # Config validation failed - try fallback
            logger.warning(f"Config validation failed: {e}. Trying fallback.")

    # Fallback to old linear-defaults.yml (DEPRECATED)
    if old_config_path.exists():
        warnings.warn(
            "linear-defaults.yml is DEPRECATED. "
            "Migrate to config.yml profile.linear section. "
            "Run: cd tools && uv run ce migrate-config",
            DeprecationWarning,
            stacklevel=2
        )

        logger.info("Using DEPRECATED linear-defaults.yml (migrate to config.yml)")

        try:
            with open(old_config_path) as f:
                config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RuntimeError(
                f"Failed to parse Linear defaults: {e}\n"
                f"🔧 Troubleshooting: Check YAML syntax in {old_config_path}"
            ) from e

        # Validate required fields
        required_fields = ["project", "assignee", "team"]
        missing = [f for f in required_fields if f not in config]

        if missing:
            raise RuntimeError(
                f"Missing required fields in Linear defaults: {', '.join(missing)}\n"
                f"🔧 Troubleshooting: Add to {old_config_path} or migrate to config.yml"
            )

        return config

    # Neither config found
    raise ConfigError(
        "No Linear configuration found.\n"
        "🔧 Troubleshooting:\n"
        "   1. Run: cd tools && uv run ce init-project\n"
        "   2. Or manually add profile.linear section to .ce/config.yml\n"
        "   3. See CLAUDE.md for template"
    )


def create_issue_with_defaults(
    title: str,
    description: str,
    state: str = "todo",
    labels: Optional[list] = None,
    override_assignee: Optional[str] = None,
    override_project: Optional[str] = None
) -> Dict[str, Any]:
    """Create Linear issue using project defaults.

    Args:
        title: Issue title
        description: Issue description (markdown)
        state: Issue state (todo, in_progress, done)
        labels: Optional labels (merges with defaults)
        override_assignee: Optional assignee override
        override_project: Optional project override

    Returns:
        Linear API response with issue details

    Example:
        issue = create_issue_with_defaults(
            title="PRP-15: New Feature",
            description="Implement feature X",
            state="todo"
        )
        print(f"Created: {issue['identifier']}")
    """
    defaults = get_linear_defaults()

    # Merge labels
    final_labels = list(defaults.get("default_labels", []))
    if labels:
        final_labels.extend(labels)
    # Deduplicate
    final_labels = list(set(final_labels))

    # Prepare issue data
    issue_data = {
        "team": defaults["team"],
        "title": title,
        "description": description,
        "state": state,
        "labels": final_labels,
        "assignee": override_assignee or defaults["assignee"],
        "project": override_project or defaults["project"]
    }

    logger.info(f"Creating Linear issue with defaults: {title}")
    logger.debug(f"Issue data: {issue_data}")

    # Note: Actual MCP call would go here
    # For now, return the prepared data structure
    return issue_data


def get_default_assignee() -> str:
    """Get default assignee email from config.

    Returns:
        Assignee email address

    Example:
        assignee = get_default_assignee()
        # "blazej.przybyszewski@gmail.com"
    """
    defaults = get_linear_defaults()
    return defaults["assignee"]


def get_default_project() -> str:
    """Get default project name from config.

    Returns:
        Project name

    Example:
        project = get_default_project()
        # "Context Engineering"
    """
    defaults = get_linear_defaults()
    return defaults["project"]
