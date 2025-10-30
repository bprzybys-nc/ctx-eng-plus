"""GitHub Actions executor for rendering abstract pipelines.

Renders abstract pipeline definition to GitHub Actions workflow YAML.
"""

from typing import Dict, Any
from .base import BaseExecutor
import yaml


class GitHubActionsExecutor(BaseExecutor):
    """GitHub Actions executor for rendering abstract pipelines.

    Renders abstract pipeline definition to GitHub Actions workflow YAML.

    Example:
        executor = GitHubActionsExecutor()
        pipeline = load_abstract_pipeline("ci/abstract/validation.yml")
        workflow = executor.render(pipeline)
        Path(".github/workflows/validation.yml").write_text(workflow)
    """

    def render(self, pipeline: Dict[str, Any]) -> str:
        """Render abstract pipeline to GitHub Actions workflow YAML.

        Args:
            pipeline: Abstract pipeline definition

        Returns:
            GitHub Actions workflow YAML string

        Raises:
            RuntimeError: If rendering fails

        Mapping:
            - stages → jobs
            - nodes → steps
            - parallel → jobs run in parallel (no needs dependency)
            - depends_on → needs: [job-name]
        """
        workflow = {
            "name": pipeline["name"],
            "on": ["push", "pull_request"],
            "jobs": {}
        }

        for stage in pipeline["stages"]:
            job_name = self._sanitize_job_name(stage["name"])

            job = {
                "runs-on": "ubuntu-latest",
                "steps": []
            }

            # Add checkout step (required for all jobs)
            job["steps"].append({
                "name": "Checkout code",
                "uses": "actions/checkout@v4"
            })

            # Convert nodes to steps
            for node in stage["nodes"]:
                step = {
                    "name": node["name"],
                    "run": node["command"]
                }

                # Add timeout if specified
                if "timeout" in node:
                    step["timeout-minutes"] = node["timeout"] // 60

                job["steps"].append(step)

            # Add dependencies (depends_on → needs)
            if "depends_on" in stage:
                job["needs"] = [
                    self._sanitize_job_name(dep)
                    for dep in stage["depends_on"]
                ]

            workflow["jobs"][job_name] = job

        return self.format_yaml(workflow)

    def validate_output(self, output: str) -> Dict[str, Any]:
        """Validate GitHub Actions workflow YAML.

        Args:
            output: Rendered workflow YAML

        Returns:
            Dict with: success (bool), errors (List[str])

        Note: Basic validation - parse YAML and check required fields.
        """
        errors = []

        try:
            workflow = yaml.safe_load(output)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML: {e}")
            return {"success": False, "errors": errors}

        # Validate required fields
        if "name" not in workflow:
            errors.append("Missing 'name' field in workflow")
        # Note: YAML parses "on:" as True (boolean), so check for both
        if "on" not in workflow and True not in workflow:
            errors.append("Missing 'on' (trigger) field in workflow")
        if "jobs" not in workflow or not workflow["jobs"]:
            errors.append("Missing or empty 'jobs' field in workflow")

        return {
            "success": len(errors) == 0,
            "errors": errors
        }

    def get_platform_name(self) -> str:
        """Return 'github-actions'."""
        return "github-actions"

    def _sanitize_job_name(self, name: str) -> str:
        """Sanitize stage name for GitHub Actions job name.

        Args:
            name: Stage name

        Returns:
            Sanitized job name (lowercase, hyphens)

        Example:
            "Unit Tests" → "unit-tests"
        """
        return name.lower().replace(" ", "-").replace("_", "-")
