"""Tests for config_utils module.

Tests validation logic, error handling, and configuration loading.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from ce.config_utils import (
    load_config,
    validate_config,
    get_nested_value,
    get_profile_value,
    ConfigError,
    clear_config_cache
)


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create temporary .ce directory for testing."""
    ce_dir = tmp_path / ".ce"
    ce_dir.mkdir()
    return ce_dir


@pytest.fixture
def valid_config():
    """Return valid configuration dictionary."""
    return {
        "profile": {
            "project_name": "test-project",
            "description": "Test project description",
            "linear": {
                "project": "TestProject",
                "assignee": "test@example.com",
                "team": "TEST123",
                "default_labels": ["feature"]
            },
            "git": {
                "author_name": "",
                "author_email": ""
            },
            "repository": {
                "url": "",
                "main_branch": "main"
            }
        },
        "cache": {
            "analysis_ttl_minutes": 5
        },
        "_validation": {
            "required_fields": [
                "profile.project_name",
                "profile.linear.project",
                "profile.linear.assignee",
                "profile.linear.team"
            ],
            "schema_version": "1.0.0"
        }
    }


def test_load_config_success(temp_config_dir, valid_config):
    """Test loading valid configuration."""
    config_path = temp_config_dir / "config.yml"
    with open(config_path, 'w') as f:
        yaml.safe_dump(valid_config, f)

    config = load_config(str(config_path))

    assert config["profile"]["project_name"] == "test-project"
    assert config["profile"]["linear"]["project"] == "TestProject"


def test_load_config_file_not_found():
    """Test loading non-existent config file."""
    with pytest.raises(ConfigError) as excinfo:
        load_config("/nonexistent/config.yml")

    assert "Configuration not found" in str(excinfo.value)
    assert "Troubleshooting" in str(excinfo.value)


def test_load_config_invalid_yaml(temp_config_dir):
    """Test loading config with invalid YAML syntax."""
    config_path = temp_config_dir / "config.yml"
    with open(config_path, 'w') as f:
        f.write("invalid: yaml: syntax:\n  - broken")

    with pytest.raises(ConfigError) as excinfo:
        load_config(str(config_path))

    assert "Invalid YAML syntax" in str(excinfo.value)


def test_load_config_empty_file(temp_config_dir):
    """Test loading empty config file."""
    config_path = temp_config_dir / "config.yml"
    config_path.touch()  # Create empty file

    with pytest.raises(ConfigError) as excinfo:
        load_config(str(config_path))

    assert "Empty configuration" in str(excinfo.value)


def test_validate_config_missing_validation_section(valid_config):
    """Test validation fails when _validation section missing."""
    config = valid_config.copy()
    del config["_validation"]

    with pytest.raises(ConfigError) as excinfo:
        validate_config(config, "test.yml")

    assert "missing _validation section" in str(excinfo.value)


def test_validate_config_missing_required_fields(valid_config):
    """Test validation fails when required fields are <missing>."""
    config = valid_config.copy()
    config["profile"]["project_name"] = "<missing>"
    config["profile"]["linear"]["assignee"] = "<missing>"

    with pytest.raises(ConfigError) as excinfo:
        validate_config(config, "test.yml")

    error_msg = str(excinfo.value)
    assert "profile.project_name" in error_msg
    assert "profile.linear.assignee" in error_msg
    assert "Troubleshooting" in error_msg


def test_validate_config_empty_string_treated_as_missing(valid_config):
    """Test validation fails for empty string in required fields."""
    config = valid_config.copy()
    config["profile"]["project_name"] = ""

    with pytest.raises(ConfigError) as excinfo:
        validate_config(config, "test.yml")

    assert "profile.project_name" in str(excinfo.value)


def test_validate_config_none_treated_as_missing(valid_config):
    """Test validation fails for None in required fields."""
    config = valid_config.copy()
    config["profile"]["linear"]["team"] = None

    with pytest.raises(ConfigError) as excinfo:
        validate_config(config, "test.yml")

    assert "profile.linear.team" in str(excinfo.value)


def test_validate_config_no_required_fields(valid_config):
    """Test validation passes when no required_fields defined."""
    config = valid_config.copy()
    config["_validation"]["required_fields"] = []

    # Should not raise
    validate_config(config, "test.yml")


def test_get_nested_value_simple():
    """Test getting nested value with dot notation."""
    data = {"a": {"b": {"c": "value"}}}

    assert get_nested_value(data, "a.b.c") == "value"


def test_get_nested_value_top_level():
    """Test getting top-level value."""
    data = {"key": "value"}

    assert get_nested_value(data, "key") == "value"


def test_get_nested_value_missing_path():
    """Test getting value with non-existent path."""
    data = {"a": {"b": "value"}}

    assert get_nested_value(data, "a.c.d") is None


def test_get_nested_value_partial_path():
    """Test getting value where path exists partially."""
    data = {"a": {"b": "value"}}

    assert get_nested_value(data, "a.b.c") is None


def test_get_profile_value_success(temp_config_dir, valid_config):
    """Test getting value from profile section."""
    config_path = temp_config_dir / "config.yml"
    with open(config_path, 'w') as f:
        yaml.safe_dump(valid_config, f)

    # Clear cache to force reload
    clear_config_cache()

    value = get_profile_value("project_name", str(config_path))
    assert value == "test-project"

    value = get_profile_value("linear.assignee", str(config_path))
    assert value == "test@example.com"


def test_get_profile_value_no_profile_section(temp_config_dir):
    """Test getting profile value when profile section missing."""
    config_path = temp_config_dir / "config.yml"
    config = {
        "_validation": {
            "required_fields": [],
            "schema_version": "1.0.0"
        }
    }
    with open(config_path, 'w') as f:
        yaml.safe_dump(config, f)

    clear_config_cache()

    with pytest.raises(ConfigError) as excinfo:
        get_profile_value("project_name", str(config_path))

    assert "No profile section" in str(excinfo.value)


def test_get_profile_value_key_not_found(temp_config_dir, valid_config):
    """Test getting non-existent profile key."""
    config_path = temp_config_dir / "config.yml"
    with open(config_path, 'w') as f:
        yaml.safe_dump(valid_config, f)

    clear_config_cache()

    with pytest.raises(ConfigError) as excinfo:
        get_profile_value("nonexistent.key", str(config_path))

    assert "Profile key not found" in str(excinfo.value)
