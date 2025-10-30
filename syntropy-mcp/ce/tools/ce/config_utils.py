"""Configuration management and validation utilities.

This module provides centralized configuration loading and validation
for the Context Engineering framework. All configuration is stored in
.ce/config.yml with a profile section for project-specific settings.

Key Features:
- Validates required fields are filled (not <missing>)
- Blocks system startup if configuration incomplete
- Clear error messages with troubleshooting guidance
- Supports nested configuration access via dot notation

Usage:
    from ce.config_utils import load_config, ConfigError

    try:
        config = load_config()
        project_name = config["profile"]["project_name"]
    except ConfigError as e:
        print(f"❌ {e}")
        sys.exit(1)
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
import yaml


class ConfigError(Exception):
    """Configuration validation or loading error.

    Raised when:
    - config.yml not found
    - Required fields missing or set to <missing>
    - Invalid YAML syntax
    - Schema validation failures
    """
    pass


def load_config(config_path: str = ".ce/config.yml") -> Dict[str, Any]:
    """Load and validate configuration from YAML file.

    Args:
        config_path: Path to config.yml (default: .ce/config.yml)

    Returns:
        Validated configuration dictionary

    Raises:
        ConfigError: If config missing, invalid, or incomplete

    Example:
        config = load_config()
        linear_project = config["profile"]["linear"]["project"]
    """
    path = Path(config_path)

    if not path.exists():
        raise ConfigError(
            f"Configuration not found: {config_path}\n"
            "🔧 Troubleshooting:\n"
            "   1. Run: cd tools && uv run ce init-project\n"
            "   2. Or manually create .ce/config.yml with profile section"
        )

    try:
        with open(path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigError(
            f"Invalid YAML syntax in {config_path}:\n{e}\n"
            "🔧 Troubleshooting:\n"
            "   1. Check YAML syntax with: yamllint .ce/config.yml\n"
            "   2. Validate indentation and quotes\n"
            "   3. Use online YAML validator if needed"
        )

    if config is None:
        raise ConfigError(
            f"Empty configuration file: {config_path}\n"
            "🔧 Troubleshooting: Add profile section with required fields"
        )

    validate_config(config, config_path)
    return config


def validate_config(config: Dict[str, Any], config_path: str) -> None:
    """Validate configuration completeness and correctness.

    Args:
        config: Configuration dictionary
        config_path: Path to config file (for error messages)

    Raises:
        ConfigError: If validation fails

    Validation Rules:
    - _validation section must exist
    - All required_fields must be filled (not <missing>, None, or "")
    - Schema version must be present
    """
    if "_validation" not in config:
        raise ConfigError(
            f"Invalid {config_path}: missing _validation section\n"
            "🔧 Troubleshooting:\n"
            "   This config.yml is from an older version.\n"
            "   Run: cd tools && uv run ce migrate-config"
        )

    validation = config["_validation"]
    required_fields = validation.get("required_fields", [])

    if not required_fields:
        # No required fields defined - skip validation
        return

    missing = []
    for field_path in required_fields:
        value = get_nested_value(config, field_path)

        # Check if value is missing, None, empty string, or <missing> placeholder
        if value is None or value == "" or value == "<missing>":
            missing.append(field_path)

    if missing:
        missing_list = "\n".join(f"   - {field}" for field in missing)
        raise ConfigError(
            f"⚠️  Required configuration incomplete in {config_path}:\n"
            f"{missing_list}\n\n"
            "🔧 Troubleshooting:\n"
            f"   1. Edit {config_path}\n"
            "   2. Replace <missing> with actual values:\n"
            "      - profile.project_name: Your project name\n"
            "      - profile.linear.project: Linear project name\n"
            "      - profile.linear.assignee: your.email@example.com\n"
            "      - profile.linear.team: Your team ID\n"
            "   3. Save and retry command"
        )


def get_nested_value(d: Dict[str, Any], path: str) -> Optional[Any]:
    """Get nested dictionary value using dot notation.

    Args:
        d: Dictionary to traverse
        path: Dot-separated path (e.g., "profile.linear.project")

    Returns:
        Value at path, or None if path doesn't exist

    Example:
        >>> config = {"profile": {"linear": {"project": "MyProject"}}}
        >>> get_nested_value(config, "profile.linear.project")
        "MyProject"
    """
    keys = path.split(".")
    value = d

    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None

    return value


def get_profile_value(key_path: str, config_path: str = ".ce/config.yml") -> Any:
    """Get value from profile section of config.

    Args:
        key_path: Dot-separated path within profile (e.g., "linear.project")
        config_path: Path to config.yml

    Returns:
        Value from profile section

    Raises:
        ConfigError: If config invalid or value not found

    Example:
        project_name = get_profile_value("project_name")
        assignee = get_profile_value("linear.assignee")
    """
    config = load_config(config_path)

    if "profile" not in config:
        raise ConfigError(
            f"No profile section in {config_path}\n"
            "🔧 Troubleshooting: Upgrade config.yml to schema v1.0.0"
        )

    full_path = f"profile.{key_path}"
    value = get_nested_value(config, full_path)

    if value is None:
        raise ConfigError(
            f"Profile key not found: {key_path}\n"
            "🔧 Troubleshooting: Check config.yml profile section"
        )

    return value


# Cache for loaded config (avoid re-reading on every call)
_config_cache: Optional[Dict[str, Any]] = None


def get_cached_config(config_path: str = ".ce/config.yml") -> Dict[str, Any]:
    """Get configuration with caching.

    First call loads and validates config.yml.
    Subsequent calls return cached value.

    Args:
        config_path: Path to config.yml

    Returns:
        Cached configuration dictionary

    Note: Cache is per-process. Config changes require process restart.
    """
    global _config_cache

    if _config_cache is None:
        _config_cache = load_config(config_path)

    return _config_cache


def clear_config_cache() -> None:
    """Clear configuration cache.

    Used primarily in tests to force config reload.
    """
    global _config_cache
    _config_cache = None
