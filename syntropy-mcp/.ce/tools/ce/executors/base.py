"""Base executor interface and utilities.

Provides protocol for platform-specific executors and shared utilities.
"""

from typing import Protocol, Dict, Any
import yaml


class PipelineExecutor(Protocol):
    """Interface for platform-specific pipeline executors.

    Executors render abstract pipeline definitions to platform-specific formats.
    Each platform (GitHub Actions, GitLab CI, Jenkins) has its own executor.

    Example:
        executor = GitHubActionsExecutor()
        yaml_output = executor.render(abstract_pipeline)
        Path(".github/workflows/ci.yml").write_text(yaml_output)
    """

    def render(self, pipeline: Dict[str, Any]) -> str:
        """Render abstract pipeline to platform-specific format.

        Args:
            pipeline: Abstract pipeline definition dict

        Returns:
            Platform-specific YAML/JSON string

        Raises:
            RuntimeError: If rendering fails

        Note: Output must be valid for target platform (validated before return).
        """
        ...

    def validate_output(self, output: str) -> Dict[str, Any]:
        """Validate rendered output for platform compatibility.

        Args:
            output: Rendered pipeline string

        Returns:
            Dict with: success (bool), errors (List[str])

        Note: Platform-specific validation (e.g., GitHub Actions schema).
        """
        ...

    def get_platform_name(self) -> str:
        """Return platform name (e.g., 'github-actions', 'gitlab-ci').

        Returns:
            Platform identifier string
        """
        ...


class BaseExecutor:
    """Base class for executors (optional, for code reuse).

    Provides common functionality like YAML formatting, error handling.
    """

    def format_yaml(self, data: Dict[str, Any]) -> str:
        """Format dict as YAML with consistent style.

        Args:
            data: Data to format

        Returns:
            Formatted YAML string
        """
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
