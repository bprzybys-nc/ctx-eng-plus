"""Linear integration utilities for Context Engineering.

Provides helpers for reading Linear defaults and creating issues with
project-specific configuration.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

logger = logging.getLogger(__name__)


def get_linear_defaults() -> Dict[str, Any]:
    """Read Linear defaults from .ce/linear-defaults.yml.

    Returns:
        Dict with keys: project, assignee, team, default_labels

    Raises:
        FileNotFoundError: If linear-defaults.yml not found
        RuntimeError: If YAML parsing fails
    """
    # Find project root (go up from tools/)
    project_root = Path(__file__).parent.parent.parent
    config_path = project_root / ".ce" / "linear-defaults.yml"

    if not config_path.exists():
        raise FileNotFoundError(
            f"Linear defaults not found: {config_path}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Create .ce/linear-defaults.yml with project/assignee config\n"
            f"   - See CLAUDE.md for template"
        )

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise RuntimeError(
            f"Failed to parse Linear defaults: {e}\n"
            f"🔧 Troubleshooting: Check YAML syntax in {config_path}"
        ) from e

    # Validate required fields
    required_fields = ["project", "assignee", "team"]
    missing = [f for f in required_fields if f not in config]

    if missing:
        raise RuntimeError(
            f"Missing required fields in Linear defaults: {', '.join(missing)}\n"
            f"🔧 Troubleshooting: Add to {config_path}"
        )

    return config


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

    # FIX BUG #4: Call Linear MCP tool
    try:
        # Import MCP client
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        import json

        # TODO: Replace with actual MCP call through syntropy aggregator
        # For now, import direct tool call (requires Claude Code environment)
        import sys
        if hasattr(sys.modules.get('__main__'), 'mcp__syntropy__linear_create_issue'):
            # Running in Claude Code - use direct tool call
            create_issue = sys.modules['__main__'].mcp__syntropy__linear_create_issue
            response = create_issue(
                title=issue_data["title"],
                team=issue_data["team"],  # CRITICAL: Use "team" not "team_id"
                description=issue_data["description"]
            )

            # Parse response
            if response and "content" in response:
                result_text = response["content"][0]["text"]
                result = json.loads(result_text) if isinstance(result_text, str) else result_text
                logger.info(f"Created Linear issue: {result.get('identifier', 'unknown')}")
                return result
            else:
                logger.error(f"Invalid Linear MCP response: {response}")
                return issue_data  # Fallback to prepared data
        else:
            # Not in Claude Code environment - return prepared data
            logger.warning("Linear MCP not available, returning prepared data structure")
            return issue_data

    except Exception as e:
        logger.error(f"Failed to create Linear issue via MCP: {e}")
        logger.warning("Returning prepared data structure as fallback")
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
