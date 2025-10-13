"""CLI integration tests for pipeline commands."""

import pytest
import subprocess
from pathlib import Path


def test_pipeline_validate_success(tmp_path):
    """Test pipeline validate command with valid pipeline."""
    pipeline_file = tmp_path / "test.yml"
    pipeline_file.write_text("""
name: test-pipeline
stages:
  - name: test
    nodes:
      - name: run
        command: pytest
    """)

    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "validate", str(pipeline_file)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "✅ Pipeline validation passed" in result.stdout


def test_pipeline_validate_invalid(tmp_path):
    """Test pipeline validate command with invalid pipeline."""
    pipeline_file = tmp_path / "bad.yml"
    pipeline_file.write_text("""
name: bad-pipeline
stages:
  - name: test
    nodes:
      - name: run
        command: pytest
    depends_on: [nonexistent]
    """)

    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "validate", str(pipeline_file)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert "❌ Pipeline validation failed" in result.stdout
    assert "nonexistent" in result.stdout


def test_pipeline_render_to_stdout(tmp_path):
    """Test pipeline render command outputs to stdout."""
    pipeline_file = tmp_path / "test.yml"
    pipeline_file.write_text("""
name: test-pipeline
stages:
  - name: build
    nodes:
      - name: compile
        command: make
    """)

    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "render", str(pipeline_file),
         "--executor", "github-actions"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "name: test-pipeline" in result.stdout
    assert "jobs:" in result.stdout
    assert "build:" in result.stdout


def test_pipeline_render_to_file(tmp_path):
    """Test pipeline render command writes to file."""
    pipeline_file = tmp_path / "test.yml"
    pipeline_file.write_text("""
name: test-pipeline
stages:
  - name: test
    nodes:
      - name: run
        command: pytest
    """)

    output_file = tmp_path / "workflow.yml"

    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "render", str(pipeline_file),
         "--executor", "github-actions",
         "-o", str(output_file)],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "✅ Rendered to" in result.stdout
    assert output_file.exists()

    content = output_file.read_text()
    assert "name: test-pipeline" in content
    assert "jobs:" in content


def test_pipeline_render_mock_executor(tmp_path):
    """Test pipeline render with mock executor."""
    pipeline_file = tmp_path / "test.yml"
    pipeline_file.write_text("""
name: test-pipeline
stages:
  - name: test
    nodes:
      - name: run
        command: pytest
    """)

    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "render", str(pipeline_file),
         "--executor", "mock"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "Mock pipeline: test-pipeline" in result.stdout
    assert "Stages: 1" in result.stdout


def test_pipeline_validate_nonexistent_file():
    """Test pipeline validate with nonexistent file."""
    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "validate", "/nonexistent/file.yml"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 1
    assert "❌ Validation error" in result.stderr
    assert "Pipeline file not found" in result.stderr


def test_pipeline_render_example_validation():
    """Test rendering the actual validation.yml example."""
    example_path = Path(__file__).parent.parent.parent / "ci" / "abstract" / "validation.yml"

    result = subprocess.run(
        ["uv", "run", "ce", "pipeline", "render", str(example_path),
         "--executor", "github-actions"],
        cwd=Path(__file__).parent.parent,
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert "name: validation-pipeline" in result.stdout
    assert "lint:" in result.stdout
    assert "test:" in result.stdout
    assert "validate:" in result.stdout
