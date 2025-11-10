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

        Supports both optimized config.yml format (directories.paths)
        and legacy blend-config.yml format (directories.output/framework).

        Raises:
            ValueError: If required sections missing
        """
        # If domains is null (repomix issue), it's OK as long as we have directories from fallback
        if (self._config.get("domains") is None and
            (self._config.get("directories") is None or self._config.get("directories") == {})):
            raise ValueError(
                f"Missing required configuration: both 'domains' and 'directories' are null/empty\n"
                f"🔧 Troubleshooting: Check .ce/config.yml is valid"
            )

        # Validate directories section if present (optional for backward compatibility)
        if "directories" in self._config and self._config["directories"] is not None:
            dir_config = self._config["directories"]

            # Check for optimized format (paths + legacy)
            has_optimized = "paths" in dir_config and "legacy" in dir_config

            # Check for legacy format (output + framework + legacy)
            has_legacy = (
                "output" in dir_config and
                "framework" in dir_config and
                "legacy" in dir_config
            )

            # At least one format must be present
            if not (has_optimized or has_legacy):
                raise ValueError(
                    f"Missing required directories configuration\n"
                    f"Expected either: directories.paths + directories.legacy (optimized)\n"
                    f"Or: directories.output + directories.framework + directories.legacy (legacy)\n"
                    f"🔧 Troubleshooting: Check .ce/config.yml structure"
                )

    def get_output_path(self, domain: str) -> Path:
        """Get output path for domain.

        Supports both optimized config.yml (directories.paths)
        and legacy blend-config.yml (directories.output).

        Args:
            domain: Domain name (settings, memories, examples, prps, claude_dir, claude_md, serena_memories, etc.)

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
                f"🔧 Troubleshooting: Add directories section to config"
            )

        dirs_config = self._config["directories"]

        # Try optimized format first (directories.paths)
        if "paths" in dirs_config and domain in dirs_config["paths"]:
            return Path(dirs_config["paths"][domain])

        # Fall back to legacy format (directories.output)
        if "output" in dirs_config and domain in dirs_config["output"]:
            return Path(dirs_config["output"][domain])

        raise ValueError(
            f"Unknown output domain: {domain}\n"
            f"🔧 Troubleshooting: Valid domains: {list(dirs_config.get('paths', {}).keys()) or list(dirs_config.get('output', {}).keys())}"
        )

    def get_framework_path(self, domain: str) -> Path:
        """Get framework source path for domain.

        Supports both optimized config.yml (directories.paths)
        and legacy blend-config.yml (directories.framework).

        Args:
            domain: Domain name (serena_memories, examples, prps, commands, settings, etc.)

        Returns:
            Path object for framework source location

        Raises:
            ValueError: If domain not found
            KeyError: If directories section missing
        """
        if "directories" not in self._config:
            raise KeyError(
                "directories section not found in config\n"
                f"🔧 Troubleshooting: Add directories section to config"
            )

        dirs_config = self._config["directories"]

        # Try optimized format first (directories.paths)
        if "paths" in dirs_config and domain in dirs_config["paths"]:
            return Path(dirs_config["paths"][domain])

        # Fall back to legacy format (directories.framework)
        if "framework" in dirs_config and domain in dirs_config["framework"]:
            return Path(dirs_config["framework"][domain])

        raise ValueError(f"Unknown framework domain: {domain}")

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

    def get_dir_path(self, dir_key: str) -> Path:
        """Get a directory path from optimized config.

        Supports both optimized config.yml (directories.paths.X)
        and legacy format (directories.output.X or directories.framework.X).

        Args:
            dir_key: Directory key (claude, claude_commands, serena, serena_memories, examples, prps, tools, etc.)

        Returns:
            Path object for the directory

        Raises:
            KeyError: If directories not found
            ValueError: If dir_key not found in config
        """
        if "directories" not in self._config:
            raise KeyError("directories section not found in config")

        dirs_config = self._config["directories"]

        # Try optimized config format first (single "paths" dict)
        if "paths" in dirs_config and dir_key in dirs_config["paths"]:
            return Path(dirs_config["paths"][dir_key])

        # Fall back to legacy format (separate "output" and "framework" dicts)
        if "output" in dirs_config and dir_key in dirs_config["output"]:
            return Path(dirs_config["output"][dir_key])

        if "framework" in dirs_config and dir_key in dirs_config["framework"]:
            return Path(dirs_config["framework"][dir_key])

        raise ValueError(f"Unknown directory key: {dir_key}")

    def get_domain_config(self, domain: str) -> Dict[str, Any]:
        """Get full domain configuration.

        Supports both legacy blend-config.yml structure (domains at top level)
        and new unified config.yml structure (detection.domains).

        Args:
            domain: Domain name (settings, memories, examples, prps, commands, claude_md)

        Returns:
            Dictionary with domain-specific config (strategy, source, etc.)
        """
        # Try unified config.yml structure first (detection.domains)
        if "detection" in self._config and "domains" in self._config.get("detection", {}):
            detection_domains = self._config["detection"]["domains"]
            if domain in detection_domains:
                return detection_domains[domain]

        # Fall back to legacy blend-config.yml structure (domains at top level)
        if self._config.get("domains") is None:
            return {}  # Return empty dict if domains is null (repomix issue)
        return self._config["domains"].get(domain, {})

    def get_domain_legacy_sources(self, domain: str) -> List[Path]:
        """Get legacy sources specific to a domain.

        Supports both optimized config.yml (paths key) and legacy blend-config.yml (legacy_paths key).

        Args:
            domain: Domain name

        Returns:
            List of Path objects for domain-specific legacy locations
        """
        domain_config = self.get_domain_config(domain)

        # Get sources from domain config - supports multiple key names for backward compatibility
        sources = []

        # Optimized config.yml format: "paths" key
        if "paths" in domain_config:
            sources.extend([Path(s) for s in domain_config["paths"]])

        # Legacy blend-config.yml format: "legacy_paths" key
        if "legacy_paths" in domain_config:
            sources.extend([Path(s) for s in domain_config["legacy_paths"]])

        # Single source variants (backward compatibility)
        if "legacy_source" in domain_config:
            sources.append(Path(domain_config["legacy_source"]))
        if "legacy_sources" in domain_config:
            sources.extend([Path(s) for s in domain_config["legacy_sources"]])

        return sources if sources else []
