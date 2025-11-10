"""Centralized configuration loader for init-project.

Loads blend-config.yml and provides typed access to directory paths.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import logging

logger = logging.getLogger(__name__)


class BlendConfig:
    """Configuration container with path resolution.

    Provides centralized access to directory locations and blending strategies
    defined in blend-config.yml. Validates config structure and ensures all
    required sections are present.
    """

    def __init__(self, config_path: Path):
        """Load and validate configuration.

        Args:
            config_path: Path to blend-config.yml

        Raises:
            ValueError: If config invalid or missing required fields
            FileNotFoundError: If config file doesn't exist
        """
        config_path = Path(config_path).resolve()

        if not config_path.exists():
            raise ValueError(
                f"Config file not found: {config_path}\n"
                f"🔧 Troubleshooting: Ensure blend-config.yml exists"
            )

        try:
            with open(config_path) as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(
                f"Invalid YAML in config: {e}\n"
                f"🔧 Troubleshooting: Check blend-config.yml syntax"
            )

        if self._config is None:
            self._config = {}

        # Load directories from separate file if needed (repomix workaround)
        self._load_directories_fallback(config_path)

        self._validate()

    def _load_directories_fallback(self, config_path: Path) -> None:
        """Load directories from separate file if needed (repomix workaround).

        If directories section is None/missing in blend-config.yml, try loading
        from directories.yml in the same directory.
        """
        try:
            # Check if directories section is None
            if self._config.get("directories") is None:
                directories_path = config_path.parent / "directories.yml"
                if directories_path.exists():
                    with open(directories_path) as f:
                        directories_data = yaml.safe_load(f)
                    if directories_data:
                        self._config["directories"] = directories_data
        except Exception:
            pass  # If fallback fails, proceed with validation error

    def _validate(self) -> None:
        """Validate config structure.

        Raises:
            ValueError: If required sections missing
        """
        required_sections = ["domains"]
        for section in required_sections:
            if section not in self._config:
                raise ValueError(
                    f"Missing required section: {section}\n"
                    f"🔧 Troubleshooting: Add to blend-config.yml"
                )

        # Validate directories section if present (optional for backward compatibility)
        if "directories" in self._config and self._config["directories"] is not None:
            dir_config = self._config["directories"]
            required_subsections = ["output", "framework", "legacy"]
            for subsection in required_subsections:
                if subsection not in dir_config:
                    raise ValueError(
                        f"Missing directories.{subsection} in config\n"
                        f"🔧 Troubleshooting: Add to blend-config.yml"
                    )

    def get_output_path(self, domain: str) -> Path:
        """Get output path for domain.

        Args:
            domain: Domain name (settings, memories, examples, prps, claude_dir, claude_md, serena_memories)

        Returns:
            Path object for output location (relative to project root)

        Raises:
            ValueError: If domain not found in config
            KeyError: If directories section missing

        Example:
            >>> config.get_output_path("claude_dir")
            Path(".claude")
        """
        if "directories" not in self._config:
            raise KeyError(
                "directories section not found in config\n"
                f"🔧 Troubleshooting: Add directories section to blend-config.yml"
            )

        output_config = self._config["directories"]["output"]
        if domain not in output_config:
            raise ValueError(
                f"Unknown output domain: {domain}\n"
                f"🔧 Troubleshooting: Valid domains: {list(output_config.keys())}"
            )
        return Path(output_config[domain])

    def get_framework_path(self, domain: str) -> Path:
        """Get framework source path for domain.

        Args:
            domain: Domain name (serena_memories, examples, prps, commands, settings)

        Returns:
            Path object for framework source location

        Raises:
            ValueError: If domain not found
            KeyError: If directories section missing
        """
        if "directories" not in self._config:
            raise KeyError(
                "directories section not found in config\n"
                f"🔧 Troubleshooting: Add directories section to blend-config.yml"
            )

        fw_config = self._config["directories"]["framework"]
        if domain not in fw_config:
            raise ValueError(f"Unknown framework domain: {domain}")
        return Path(fw_config[domain])

    def get_legacy_paths(self) -> List[Path]:
        """Get all legacy search paths.

        Returns:
            List of Path objects for legacy directories to search

        Raises:
            KeyError: If directories section missing
        """
        if "directories" not in self._config:
            raise KeyError(
                "directories section not found in config\n"
                f"🔧 Troubleshooting: Add directories section to blend-config.yml"
            )

        legacy_list = self._config["directories"]["legacy"]
        return [Path(p) for p in legacy_list]

    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        """Get full domain configuration.

        Args:
            domain: Domain name (settings, memories, examples, prps, commands, claude_md)

        Returns:
            Dictionary with domain-specific config (strategy, source, etc.)
        """
        return self._config["domains"].get(domain, {})

    def get_domain_legacy_sources(self, domain: str) -> List[Path]:
        """Get legacy sources specific to a domain.

        Args:
            domain: Domain name

        Returns:
            List of Path objects for domain-specific legacy locations
        """
        domain_config = self.get_domain_config(domain)

        # Get sources from domain config
        sources = []
        if "legacy_source" in domain_config:
            sources.append(Path(domain_config["legacy_source"]))
        if "legacy_sources" in domain_config:
            sources.extend([Path(s) for s in domain_config["legacy_sources"]])

        return sources
