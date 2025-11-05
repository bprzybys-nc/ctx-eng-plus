"""Tests for SettingsBlendStrategy.

Tests 3 blending rules:
1. CE deny removes from target allow
2. Merge CE entries to target lists (dedupe)
3. Ensure tool appears in ONE list only
"""

import json
import pytest
from ce.blending.strategies.settings import SettingsBlendStrategy


def test_can_handle_settings_domain():
    """Test can_handle() returns True for 'settings' domain."""
    strategy = SettingsBlendStrategy()
    assert strategy.can_handle("settings") is True
    assert strategy.can_handle("claude-md") is False
    assert strategy.can_handle("commands") is False


def test_rule1_ce_deny_removes_from_target_allow():
    """Test Rule 1: CE deny entries remove from target allow."""
    strategy = SettingsBlendStrategy()

    ce_settings = {
        "allow": [],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": []
    }

    target_settings = {
        "allow": ["mcp__syntropy__filesystem_read_file", "Write(//)"],
        "deny": [],
        "ask": []
    }

    result = strategy.blend(ce_settings, target_settings, {})

    # mcp__syntropy__filesystem_read_file should be removed from allow
    assert "mcp__syntropy__filesystem_read_file" not in result["allow"]
    assert "Write(//)" in result["allow"]
    assert "mcp__syntropy__filesystem_read_file" in result["deny"]


def test_rule2_merge_ce_entries_dedupe():
    """Test Rule 2: CE entries added to target lists (deduplicated)."""
    strategy = SettingsBlendStrategy()

    ce_settings = {
        "allow": ["Bash(git:*)", "Read(//)"],
        "deny": [],
        "ask": ["Bash(rm:*)"]
    }

    target_settings = {
        "allow": ["Read(//)", "Write(//)"],  # Read(//) duplicate
        "deny": [],
        "ask": []
    }

    result = strategy.blend(ce_settings, target_settings, {})

    # All CE entries added, deduplicated
    assert "Bash(git:*)" in result["allow"]
    assert "Read(//)" in result["allow"]
    assert "Write(//)" in result["allow"]
    assert result["allow"].count("Read(//)")  == 1  # No duplicate
    assert "Bash(rm:*)" in result["ask"]


def test_rule3_ce_entries_single_membership():
    """Test Rule 3: CE entries only in one list (CE list takes precedence)."""
    strategy = SettingsBlendStrategy()

    ce_settings = {
        "allow": ["Bash(git:*)"],
        "deny": ["mcp__syntropy__git_status"],
        "ask": []
    }

    target_settings = {
        "allow": ["mcp__syntropy__git_status"],  # Conflicts with CE deny
        "deny": ["Bash(git:*)"],  # Conflicts with CE allow
        "ask": []
    }

    result = strategy.blend(ce_settings, target_settings, {})

    # CE allow entry should only be in allow
    assert "Bash(git:*)" in result["allow"]
    assert "Bash(git:*)" not in result["deny"]

    # CE deny entry should only be in deny
    assert "mcp__syntropy__git_status" in result["deny"]
    assert "mcp__syntropy__git_status" not in result["allow"]


def test_blend_empty_target_settings():
    """Test blending with empty target settings."""
    strategy = SettingsBlendStrategy()

    ce_settings = {
        "allow": ["Read(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)"]
    }

    target_settings = None

    result = strategy.blend(ce_settings, target_settings, {})

    # CE settings copied as-is
    assert result["allow"] == ["Read(//)"]
    assert result["deny"] == ["mcp__syntropy__filesystem_read_file"]
    assert result["ask"] == ["Bash(rm:*)"]


def test_blend_with_json_strings():
    """Test blending with JSON string inputs."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({
        "allow": ["Bash(git:*)"],
        "deny": [],
        "ask": []
    })

    target_settings = json.dumps({
        "allow": ["Write(//)"],
        "deny": [],
        "ask": []
    })

    result = strategy.blend(ce_settings, target_settings, {})

    # Result should be dict
    assert isinstance(result, dict)
    assert "Bash(git:*)" in result["allow"]
    assert "Write(//)" in result["allow"]


def test_blend_malformed_ce_settings():
    """Test blend() raises on malformed CE settings."""
    strategy = SettingsBlendStrategy()

    ce_settings = "{ invalid json"
    target_settings = {"allow": [], "deny": [], "ask": []}

    with pytest.raises(ValueError, match="CE settings JSON invalid"):
        strategy.blend(ce_settings, target_settings, {})


def test_blend_malformed_target_settings():
    """Test blend() raises on malformed target settings."""
    strategy = SettingsBlendStrategy()

    ce_settings = {"allow": [], "deny": [], "ask": []}
    target_settings = "{ invalid json"

    with pytest.raises(ValueError, match="Target settings JSON invalid"):
        strategy.blend(ce_settings, target_settings, {})


def test_validate_valid_settings():
    """Test validate() passes for valid settings."""
    strategy = SettingsBlendStrategy()

    valid_settings = {
        "allow": ["Read(//)", "Write(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)"]
    }

    assert strategy.validate(valid_settings, {}) is True


def test_validate_with_json_string():
    """Test validate() accepts JSON string."""
    strategy = SettingsBlendStrategy()

    valid_settings = json.dumps({
        "allow": ["Read(//)", "Write(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)"]
    })

    assert strategy.validate(valid_settings, {}) is True


def test_validate_missing_list():
    """Test validate() raises if list missing."""
    strategy = SettingsBlendStrategy()

    invalid_settings = {
        "allow": [],
        "deny": []
        # Missing "ask" list
    }

    with pytest.raises(ValueError, match="Missing 'ask' list"):
        strategy.validate(invalid_settings, {})


def test_validate_duplicate_entries():
    """Test validate() raises if duplicate entries across lists."""
    strategy = SettingsBlendStrategy()

    invalid_settings = {
        "allow": ["Read(//)", "Write(//)"],
        "deny": ["Read(//)", "mcp__syntropy__filesystem_read_file"],  # Duplicate "Read(//)"
        "ask": []
    }

    with pytest.raises(ValueError, match="Duplicate entries across lists"):
        strategy.validate(invalid_settings, {})


def test_comprehensive_blend_scenario():
    """Test comprehensive scenario from PRP-33 documentation."""
    strategy = SettingsBlendStrategy()

    ce_settings = {
        "allow": ["Bash(git:*)", "Read(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)", "Bash(mv:*)"]
    }

    target_settings = {
        "allow": ["mcp__syntropy__filesystem_read_file", "Write(//)"],
        "deny": ["Bash(cp:*)"],
        "ask": []
    }

    result = strategy.blend(ce_settings, target_settings, {})

    # Verify expected output
    expected_allow = sorted(["Write(//)", "Bash(git:*)", "Read(//)"])
    expected_deny = sorted(["Bash(cp:*)", "mcp__syntropy__filesystem_read_file"])
    expected_ask = sorted(["Bash(rm:*)", "Bash(mv:*)"])

    assert result["allow"] == expected_allow
    assert result["deny"] == expected_deny
    assert result["ask"] == expected_ask

    # Validate result
    assert strategy.validate(result, {}) is True


def test_blend_target_empty_string():
    """Test blending with empty string target."""
    strategy = SettingsBlendStrategy()

    ce_settings = {
        "allow": ["Read(//)"],
        "deny": [],
        "ask": []
    }

    target_settings = ""

    result = strategy.blend(ce_settings, target_settings, {})

    assert result["allow"] == ["Read(//)"]
    assert result["deny"] == []
    assert result["ask"] == []


def test_blend_invalid_ce_type():
    """Test blend() raises on invalid CE settings type."""
    strategy = SettingsBlendStrategy()

    ce_settings = ["not", "a", "dict"]  # Invalid type
    target_settings = {"allow": [], "deny": [], "ask": []}

    with pytest.raises(ValueError, match="CE settings must be dict or JSON string"):
        strategy.blend(ce_settings, target_settings, {})


def test_blend_invalid_target_type():
    """Test blend() raises on invalid target settings type."""
    strategy = SettingsBlendStrategy()

    ce_settings = {"allow": [], "deny": [], "ask": []}
    target_settings = ["not", "a", "dict"]  # Invalid type

    with pytest.raises(ValueError, match="Target settings must be dict or JSON string"):
        strategy.blend(ce_settings, target_settings, {})


def test_validate_invalid_type():
    """Test validate() raises on invalid type."""
    strategy = SettingsBlendStrategy()

    invalid_settings = ["not", "a", "dict"]  # Invalid type

    with pytest.raises(ValueError, match="Blended content must be dict or JSON string"):
        strategy.validate(invalid_settings, {})


def test_validate_list_not_list():
    """Test validate() raises if list is not a list."""
    strategy = SettingsBlendStrategy()

    invalid_settings = {
        "allow": "not a list",  # Should be list
        "deny": [],
        "ask": []
    }

    with pytest.raises(ValueError, match="'allow' must be a list"):
        strategy.validate(invalid_settings, {})
