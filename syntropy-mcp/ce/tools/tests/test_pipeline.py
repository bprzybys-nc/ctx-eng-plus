"""Tests for pipeline validation module."""

import pytest
from pathlib import Path
from ce.pipeline import load_abstract_pipeline, validate_pipeline


def test_load_valid_pipeline(tmp_path):
    """Test loading valid abstract pipeline."""
    pipeline_file = tmp_path / "test.yml"
    pipeline_file.write_text("""
name: test-pipeline
description: Test pipeline
stages:
  - name: test
    nodes:
      - name: run-test
        command: pytest tests/ -v
    """)

    pipeline = load_abstract_pipeline(str(pipeline_file))

    assert pipeline["name"] == "test-pipeline"
    assert len(pipeline["stages"]) == 1
    assert pipeline["stages"][0]["name"] == "test"


def test_load_nonexistent_pipeline():
    """Test loading nonexistent pipeline raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError) as exc_info:
        load_abstract_pipeline("/nonexistent/pipeline.yml")

    assert "Pipeline file not found" in str(exc_info.value)
    assert "🔧 Troubleshooting" in str(exc_info.value)


def test_load_invalid_yaml(tmp_path):
    """Test loading invalid YAML raises RuntimeError."""
    pipeline_file = tmp_path / "bad.yml"
    pipeline_file.write_text("invalid: yaml: syntax:")

    with pytest.raises(RuntimeError) as exc_info:
        load_abstract_pipeline(str(pipeline_file))

    assert "Failed to parse pipeline YAML" in str(exc_info.value)


def test_validate_pipeline_success():
    """Test pipeline validation with valid structure."""
    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "build",
                "nodes": [{"name": "compile", "command": "make"}]
            }
        ]
    }

    result = validate_pipeline(pipeline)

    assert result["success"] is True
    assert len(result["errors"]) == 0


def test_validate_pipeline_missing_name():
    """Test validation catches missing name field."""
    pipeline = {
        "stages": [
            {
                "name": "test",
                "nodes": [{"name": "run", "command": "pytest"}]
            }
        ]
    }

    result = validate_pipeline(pipeline)

    assert result["success"] is False
    assert any("Schema validation failed" in err for err in result["errors"])


def test_validate_pipeline_missing_depends_on():
    """Test validation catches invalid depends_on references."""
    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "test",
                "nodes": [{"name": "run", "command": "pytest"}],
                "depends_on": ["nonexistent-stage"]
            }
        ]
    }

    result = validate_pipeline(pipeline)

    assert result["success"] is False
    assert any("nonexistent-stage" in err for err in result["errors"])
    assert any("🔧 Troubleshooting" in err for err in result["errors"])


def test_validate_pipeline_valid_depends_on():
    """Test validation passes with valid depends_on references."""
    pipeline = {
        "name": "test",
        "stages": [
            {
                "name": "build",
                "nodes": [{"name": "compile", "command": "make"}]
            },
            {
                "name": "test",
                "nodes": [{"name": "run", "command": "pytest"}],
                "depends_on": ["build"]
            }
        ]
    }

    result = validate_pipeline(pipeline)

    assert result["success"] is True
    assert len(result["errors"]) == 0


def test_validate_pipeline_with_optional_fields():
    """Test validation passes with optional fields like parallel, timeout."""
    pipeline = {
        "name": "test",
        "description": "Test with optional fields",
        "stages": [
            {
                "name": "test",
                "nodes": [
                    {
                        "name": "unit-tests",
                        "command": "pytest tests/unit/",
                        "timeout": 300,
                        "strategy": "real"
                    }
                ],
                "parallel": True
            }
        ]
    }

    result = validate_pipeline(pipeline)

    assert result["success"] is True
    assert len(result["errors"]) == 0


def test_load_example_validation_pipeline():
    """Test loading actual validation.yml example."""
    # This tests our real example file
    example_path = Path(__file__).parent.parent.parent / "ci" / "abstract" / "validation.yml"

    pipeline = load_abstract_pipeline(str(example_path))

    assert pipeline["name"] == "validation-pipeline"
    assert len(pipeline["stages"]) == 3
    assert pipeline["stages"][0]["name"] == "lint"
    assert pipeline["stages"][1]["name"] == "test"
    assert pipeline["stages"][2]["name"] == "validate"

    # Validate the example
    result = validate_pipeline(pipeline)
    assert result["success"] is True
