"""Tests for GitHub Actions executor."""

import pytest
import yaml
from ce.executors.github_actions import GitHubActionsExecutor


def test_github_actions_platform_name():
    """Test GitHub Actions executor returns correct platform name."""
    executor = GitHubActionsExecutor()

    assert executor.get_platform_name() == "github-actions"


def test_github_actions_render_basic():
    """Test GitHub Actions renders basic pipeline."""
    executor = GitHubActionsExecutor()

    pipeline = {
        "name": "test-pipeline",
        "stages": [
            {
                "name": "build",
                "nodes": [
                    {"name": "compile", "command": "make"}
                ]
            }
        ]
    }

    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    assert workflow["name"] == "test-pipeline"
    assert "on" in workflow
    assert "jobs" in workflow
    assert "build" in workflow["jobs"]
    assert workflow["jobs"]["build"]["runs-on"] == "ubuntu-latest"


def test_github_actions_render_with_checkout():
    """Test GitHub Actions adds checkout step to all jobs."""
    executor = GitHubActionsExecutor()

    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "test",
                "nodes": [{"name": "run-test", "command": "pytest"}]
            }
        ]
    }

    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    steps = workflow["jobs"]["test"]["steps"]
    assert len(steps) == 2  # checkout + actual step
    assert steps[0]["name"] == "Checkout code"
    assert steps[0]["uses"] == "actions/checkout@v4"


def test_github_actions_render_with_timeout():
    """Test GitHub Actions converts timeout seconds to minutes."""
    executor = GitHubActionsExecutor()

    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "test",
                "nodes": [
                    {
                        "name": "long-test",
                        "command": "pytest",
                        "timeout": 600  # 10 minutes in seconds
                    }
                ]
            }
        ]
    }

    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    steps = workflow["jobs"]["test"]["steps"]
    test_step = steps[1]  # Second step (after checkout)
    assert test_step["timeout-minutes"] == 10


def test_github_actions_render_with_depends_on():
    """Test GitHub Actions converts depends_on to needs."""
    executor = GitHubActionsExecutor()

    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "build",
                "nodes": [{"name": "compile", "command": "make"}]
            },
            {
                "name": "test",
                "nodes": [{"name": "run-test", "command": "pytest"}],
                "depends_on": ["build"]
            }
        ]
    }

    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    assert "needs" in workflow["jobs"]["test"]
    assert workflow["jobs"]["test"]["needs"] == ["build"]


def test_github_actions_render_multiple_dependencies():
    """Test GitHub Actions handles multiple dependencies."""
    executor = GitHubActionsExecutor()

    pipeline = {
        "name": "test",
        "stages": [
            {"name": "lint", "nodes": [{"name": "l", "command": "lint"}]},
            {"name": "build", "nodes": [{"name": "b", "command": "build"}]},
            {
                "name": "test",
                "nodes": [{"name": "t", "command": "test"}],
                "depends_on": ["lint", "build"]
            }
        ]
    }

    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    assert workflow["jobs"]["test"]["needs"] == ["lint", "build"]


def test_github_actions_sanitize_job_name():
    """Test job name sanitization."""
    executor = GitHubActionsExecutor()

    assert executor._sanitize_job_name("Unit Tests") == "unit-tests"
    assert executor._sanitize_job_name("Build_Project") == "build-project"
    assert executor._sanitize_job_name("DEPLOY") == "deploy"


def test_github_actions_validate_output_success():
    """Test validation passes for valid workflow YAML."""
    executor = GitHubActionsExecutor()

    valid_workflow = """
name: test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test
        run: pytest
    """

    result = executor.validate_output(valid_workflow)

    assert result["success"] is True
    assert len(result["errors"]) == 0


def test_github_actions_validate_output_missing_name():
    """Test validation catches missing name field."""
    executor = GitHubActionsExecutor()

    invalid_workflow = """
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    """

    result = executor.validate_output(invalid_workflow)

    assert result["success"] is False
    assert any("Missing 'name'" in err for err in result["errors"])


def test_github_actions_validate_output_invalid_yaml():
    """Test validation catches invalid YAML syntax."""
    executor = GitHubActionsExecutor()

    invalid_yaml = "invalid: yaml: syntax:"

    result = executor.validate_output(invalid_yaml)

    assert result["success"] is False
    assert any("Invalid YAML" in err for err in result["errors"])


def test_github_actions_render_multiple_nodes():
    """Test GitHub Actions renders multiple nodes as steps."""
    executor = GitHubActionsExecutor()

    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "test",
                "nodes": [
                    {"name": "unit-tests", "command": "pytest tests/unit/"},
                    {"name": "integration-tests", "command": "pytest tests/integration/"}
                ]
            }
        ]
    }

    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    steps = workflow["jobs"]["test"]["steps"]
    assert len(steps) == 3  # checkout + 2 test steps
    assert steps[1]["name"] == "unit-tests"
    assert steps[2]["name"] == "integration-tests"


def test_github_actions_render_example_validation_pipeline():
    """Test rendering the actual validation.yml example."""
    from pathlib import Path
    from ce.pipeline import load_abstract_pipeline

    example_path = Path(__file__).parent.parent.parent / "ci" / "abstract" / "validation.yml"
    pipeline = load_abstract_pipeline(str(example_path))

    executor = GitHubActionsExecutor()
    output = executor.render(pipeline)
    workflow = yaml.safe_load(output)

    # Verify structure
    assert workflow["name"] == "validation-pipeline"
    assert len(workflow["jobs"]) == 3
    assert "lint" in workflow["jobs"]
    assert "test" in workflow["jobs"]
    assert "validate" in workflow["jobs"]

    # Verify dependencies
    assert "needs" in workflow["jobs"]["test"]
    assert workflow["jobs"]["test"]["needs"] == ["lint"]
    assert "needs" in workflow["jobs"]["validate"]
    assert workflow["jobs"]["validate"]["needs"] == ["test"]

    # Validate output
    result = executor.validate_output(output)
    assert result["success"] is True
