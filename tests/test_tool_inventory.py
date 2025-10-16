"""Tests for tool inventory validation."""

import yaml
from pathlib import Path


def test_tool_inventory_exists():
    """Verify tool inventory file exists."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    assert inventory_path.exists(), "Tool inventory file not found"


def test_tool_inventory_valid_yaml():
    """Verify tool inventory is valid YAML."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    with open(inventory_path) as f:
        data = yaml.safe_load(f)
    assert data is not None
    assert isinstance(data, dict)


def test_tool_inventory_has_required_sections():
    """Verify tool inventory has all required sections."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    with open(inventory_path) as f:
        data = yaml.safe_load(f)

    # Required top-level sections
    assert "optimization_rationale" in data
    assert "audit_date" in data
    assert "audit_method" in data
    assert "mcp_servers" in data
    assert "bash_commands" in data
    assert "recommendations" in data
    assert "metrics" in data


def test_recommendations_match_counts():
    """Verify recommendations section has correct counts."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    with open(inventory_path) as f:
        data = yaml.safe_load(f)

    recs = data["recommendations"]

    # Verify breakdown sums to total
    assert recs["allow_list_size"] == 30
    assert recs["deny_list_size"] == 126

    # Verify deny breakdown
    deny_breakdown = recs["deny_breakdown"]
    total_deny = sum(deny_breakdown.values())
    assert total_deny == 126, f"Deny breakdown sum {total_deny} != 126"

    # Verify allow list composition
    allow_composition = recs["allow_list_composition"]
    total_allow = sum(allow_composition.values())
    assert total_allow == 30, f"Allow composition sum {total_allow} != 30"


def test_mcp_servers_section():
    """Verify MCP servers section structure."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    with open(inventory_path) as f:
        data = yaml.safe_load(f)

    servers = data["mcp_servers"]

    # Verify key servers exist
    expected_servers = [
        "serena",
        "filesystem",
        "git",
        "context7",
        "sequential_thinking",
        "linear_server",
        "github",
        "playwright",
        "perplexity",
        "repomix",
        "ide"
    ]

    for server in expected_servers:
        assert server in servers, f"Missing server: {server}"


def test_bash_commands_analysis():
    """Verify bash commands analysis."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    with open(inventory_path) as f:
        data = yaml.safe_load(f)

    bash = data["bash_commands"]

    # Verify structure
    assert "total_usages_in_code" in bash
    assert "replaceable_with_python" in bash
    assert "replaceable_commands" in bash
    assert "essential_external_tools" in bash

    # Verify counts
    assert bash["total_usages_in_code"] >= 0
    assert bash["replaceable_with_python"] == 11
    assert len(bash["replaceable_commands"]) == 11


def test_metrics_before_after():
    """Verify metrics section has before/after data."""
    inventory_path = Path(__file__).parent.parent / ".ce" / "tool-inventory.yml"
    with open(inventory_path) as f:
        data = yaml.safe_load(f)

    metrics = data["metrics"]

    # Verify before metrics
    assert "before" in metrics
    assert "total_permissions" in metrics["before"]
    assert "bash_usages" in metrics["before"]

    # Verify after metrics
    assert "after" in metrics
    assert "total_allow_list" in metrics["after"]
    assert "total_deny_list" in metrics["after"]
    assert metrics["after"]["total_allow_list"] == 30
    assert metrics["after"]["total_deny_list"] == 126
