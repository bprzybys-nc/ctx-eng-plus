"""Tests for executor interface and base classes."""

import pytest
from ce.executors.base import BaseExecutor
from ce.executors.mock import MockExecutor


def test_base_executor_format_yaml():
    """Test BaseExecutor formats YAML correctly."""
    executor = BaseExecutor()

    data = {
        "name": "test",
        "jobs": {
            "build": {"runs-on": "ubuntu-latest"}
        }
    }

    yaml_output = executor.format_yaml(data)

    assert "name: test" in yaml_output
    assert "jobs:" in yaml_output
    assert "build:" in yaml_output
    assert "runs-on: ubuntu-latest" in yaml_output


def test_mock_executor_success():
    """Test mock executor renders successfully."""
    executor = MockExecutor()

    pipeline = {
        "name": "test-pipeline",
        "stages": [
            {"name": "test", "nodes": [{"name": "run", "command": "pytest"}]}
        ]
    }

    result = executor.render(pipeline)

    assert "Mock pipeline: test-pipeline" in result
    assert "Stages: 1" in result
    assert len(executor.render_calls) == 1


def test_mock_executor_failure():
    """Test mock executor configured to fail raises error."""
    executor = MockExecutor(should_fail=True)

    pipeline = {
        "name": "test-pipeline",
        "stages": []
    }

    with pytest.raises(RuntimeError) as exc_info:
        executor.render(pipeline)

    assert "Mock executor configured to fail" in str(exc_info.value)
    assert "🔧 Troubleshooting" in str(exc_info.value)


def test_mock_executor_validate_output():
    """Test mock executor validation always succeeds."""
    executor = MockExecutor()

    result = executor.validate_output("any output")

    assert result["success"] is True
    assert len(result["errors"]) == 0


def test_mock_executor_platform_name():
    """Test mock executor returns correct platform name."""
    executor = MockExecutor()

    assert executor.get_platform_name() == "mock"


def test_mock_executor_tracks_calls():
    """Test mock executor tracks render calls."""
    executor = MockExecutor()

    pipeline1 = {"name": "p1", "stages": []}
    pipeline2 = {"name": "p2", "stages": []}

    executor.render(pipeline1)
    executor.render(pipeline2)

    assert len(executor.render_calls) == 2
    assert executor.render_calls[0]["name"] == "p1"
    assert executor.render_calls[1]["name"] == "p2"
