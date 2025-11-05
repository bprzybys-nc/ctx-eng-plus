"""
Unit tests for classification module (Phase B - Bucket Initialization).
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from ce.blending.classification import (
    ClassificationResult,
    is_garbage,
    validate_prp,
    validate_example,
    validate_memory,
    classify_with_haiku,
    classify_file,
    main
)


class TestGarbageFilter:
    """Tests for is_garbage() function."""

    def test_is_garbage_filters_report_files(self):
        """Test that *REPORT*.md files are classified as garbage."""
        assert is_garbage("/tmp/STATUS-REPORT.md") is True
        assert is_garbage("/tmp/analysis-report.md") is True
        assert is_garbage("/tmp/REPORT-2024.md") is True

    def test_is_garbage_filters_initial_files(self):
        """Test that *INITIAL*.md files are classified as garbage."""
        assert is_garbage("/tmp/INITIAL-SETUP.md") is True
        assert is_garbage("/tmp/project-initial.md") is True

    def test_is_garbage_filters_summary_files(self):
        """Test that *summary*.md files are classified as garbage."""
        assert is_garbage("/tmp/project-summary.md") is True
        assert is_garbage("/tmp/SUMMARY.md") is True

    def test_is_garbage_filters_analysis_files(self):
        """Test that *analysis*.md files are classified as garbage."""
        assert is_garbage("/tmp/code-analysis.md") is True
        assert is_garbage("/tmp/ANALYSIS-REPORT.md") is True

    def test_is_garbage_filters_plan_files(self):
        """Test that *PLAN*.md files are classified as garbage."""
        assert is_garbage("/tmp/PROJECT-PLAN.md") is True
        assert is_garbage("/tmp/feature-plan.md") is True

    def test_is_garbage_filters_todo_files(self):
        """Test that *TODO*.md files are classified as garbage."""
        assert is_garbage("/tmp/TODO.md") is True
        assert is_garbage("/tmp/project-todo.md") is True

    def test_is_garbage_passes_normal_files(self):
        """Test that normal files are not classified as garbage."""
        assert is_garbage("/tmp/PRP-1.md") is False
        assert is_garbage("/tmp/example-feature.md") is False
        assert is_garbage("/tmp/memory-content.md") is False


class TestPRPValidation:
    """Tests for validate_prp() function."""

    def test_validate_prp_with_yaml_header(self, tmp_path):
        """Test PRP with YAML header passes validation."""
        prp_file = tmp_path / "PRP-1.md"
        prp_file.write_text("""---
prp_id: "1"
status: pending
---

# PRP-1: Test Feature

## TL;DR
Build feature.

## Context
Background info.

## Implementation
Steps to implement.

## Validation
How to test.
""")

        result = validate_prp(str(prp_file))

        assert result.valid is True
        assert result.confidence >= 0.8  # Base + YAML + sections
        assert result.file_type == "prp"

    def test_validate_prp_without_yaml_header(self, tmp_path):
        """Test PRP without YAML header still validates if has PRP ID."""
        prp_file = tmp_path / "PRP-99.md"
        prp_file.write_text("""# PRP-99: Old Feature

## Implementation
Build it.

## Validation
Test it.
""")

        result = validate_prp(str(prp_file))

        assert result.valid is True
        assert result.confidence >= 0.6  # Base confidence
        assert result.confidence < 0.8  # No YAML bonus
        assert "No YAML header" in str(result.issues)
        assert result.file_type == "prp"

    def test_validate_prp_no_prp_id(self, tmp_path):
        """Test file without PRP ID fails validation."""
        prp_file = tmp_path / "random.md"
        prp_file.write_text("""# Random Document

Some content here.
""")

        result = validate_prp(str(prp_file))

        assert result.valid is False
        assert "No PRP ID found" in str(result.issues)
        assert result.file_type == "unknown"

    def test_validate_prp_garbage_file(self, tmp_path):
        """Test garbage file is rejected immediately."""
        prp_file = tmp_path / "STATUS-REPORT.md"
        prp_file.write_text("""# Status Report

PRP-1 is done.
""")

        result = validate_prp(str(prp_file))

        assert result.valid is False
        assert result.file_type == "garbage"
        assert "garbage pattern" in str(result.issues)

    def test_validate_prp_read_error(self, tmp_path):
        """Test read error is handled gracefully."""
        prp_file = tmp_path / "nonexistent.md"

        result = validate_prp(str(prp_file))

        assert result.valid is False
        assert "Failed to read file" in str(result.issues)


class TestExampleValidation:
    """Tests for validate_example() function."""

    def test_validate_example_with_code_blocks(self, tmp_path):
        """Test example with code blocks passes validation."""
        example_file = tmp_path / "example-feature.md"
        example_file.write_text("""# Feature Implementation

## Overview
How to implement the feature.

## Code Example

```python
def hello():
    print("Hello")
```

## Usage

```bash
python hello.py
```
""")

        result = validate_example(str(example_file))

        assert result.valid is True
        assert result.confidence >= 0.89  # Base + H2 + code (no length bonus for short content)
        assert result.file_type == "example"

    def test_validate_example_no_h1_title(self, tmp_path):
        """Test example without H1 title fails validation."""
        example_file = tmp_path / "example-no-title.md"
        example_file.write_text("""## Section 1

Some content.
""")

        result = validate_example(str(example_file))

        assert result.valid is False
        assert "No H1 title" in str(result.issues)

    def test_validate_example_garbage_file(self, tmp_path):
        """Test garbage file is rejected immediately."""
        example_file = tmp_path / "example-summary.md"
        example_file.write_text("""# Summary

This is a summary.
""")

        result = validate_example(str(example_file))

        assert result.valid is False
        assert result.file_type == "garbage"

    def test_validate_example_minimal_content(self, tmp_path):
        """Test example with minimal content has lower confidence."""
        example_file = tmp_path / "example-minimal.md"
        example_file.write_text("""# Example

Short.
""")

        result = validate_example(str(example_file))

        assert result.valid is True
        assert result.confidence < 0.7  # Base only, no bonuses
        assert "No code blocks" in str(result.issues)
        assert "Short content" in str(result.issues)


class TestMemoryValidation:
    """Tests for validate_memory() function."""

    def test_validate_memory_with_valid_yaml(self, tmp_path):
        """Test memory with valid YAML passes validation."""
        memory_file = tmp_path / "test-memory.md"
        memory_file.write_text("""---
type: regular
category: documentation
tags: [test]
created: "2025-11-05T00:00:00Z"
updated: "2025-11-05T00:00:00Z"
---

# Test Memory

This is a test memory.
""")

        result = validate_memory(str(memory_file))

        assert result.valid is True
        assert result.confidence >= 0.9  # Base + type + timestamps + category
        assert result.file_type == "memory"

    def test_validate_memory_user_type(self, tmp_path):
        """Test memory with type:user validates correctly."""
        memory_file = tmp_path / "user-memory.md"
        memory_file.write_text("""---
type: user
source: target-project
created: "2025-11-05T00:00:00Z"
---

# User Memory

User-specific memory.
""")

        result = validate_memory(str(memory_file))

        assert result.valid is True
        assert result.file_type == "memory"

    def test_validate_memory_critical_type(self, tmp_path):
        """Test memory with type:critical validates correctly."""
        memory_file = tmp_path / "critical-memory.md"
        memory_file.write_text("""---
type: critical
category: code-standards
created: "2025-11-05T00:00:00Z"
updated: "2025-11-05T00:00:00Z"
---

# Critical Memory

Important memory.
""")

        result = validate_memory(str(memory_file))

        assert result.valid is True
        assert result.file_type == "memory"

    def test_validate_memory_no_yaml(self, tmp_path):
        """Test memory without YAML fails validation."""
        memory_file = tmp_path / "no-yaml.md"
        memory_file.write_text("""# Memory Without YAML

No frontmatter.
""")

        result = validate_memory(str(memory_file))

        assert result.valid is False
        assert "No YAML frontmatter" in str(result.issues)

    def test_validate_memory_invalid_type(self, tmp_path):
        """Test memory with invalid type field fails validation."""
        memory_file = tmp_path / "invalid-type.md"
        memory_file.write_text("""---
type: invalid
---

# Memory

Invalid type.
""")

        result = validate_memory(str(memory_file))

        assert result.valid is False
        assert "No valid type field" in str(result.issues)

    def test_validate_memory_missing_type(self, tmp_path):
        """Test memory without type field fails validation."""
        memory_file = tmp_path / "missing-type.md"
        memory_file.write_text("""---
category: documentation
---

# Memory

Missing type field.
""")

        result = validate_memory(str(memory_file))

        assert result.valid is False
        assert "No valid type field" in str(result.issues)


class TestHaikuClassification:
    """Tests for classify_with_haiku() function."""

    @patch('ce.blending.classification.anthropic.Anthropic')
    def test_classify_with_haiku_prp(self, mock_anthropic, tmp_path):
        """Test Haiku classification for PRP returns valid JSON."""
        prp_file = tmp_path / "test-prp.md"
        prp_file.write_text("""# PRP-1: Feature

## Implementation
Build it.
""")

        # Mock Haiku API response
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text='{"valid": true, "confidence": 0.85, "issues": []}')]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        result = classify_with_haiku(str(prp_file), "prp")

        assert result.valid is True
        assert result.confidence == 0.85
        assert result.file_type == "prp"

    @patch('ce.blending.classification.anthropic.Anthropic')
    def test_classify_with_haiku_api_error(self, mock_anthropic, tmp_path):
        """Test Haiku API error is handled gracefully."""
        prp_file = tmp_path / "test-prp.md"
        prp_file.write_text("""# PRP-1: Feature

Build it.
""")

        # Mock API error
        mock_client = Mock()
        mock_client.messages.create.side_effect = Exception("API Error")
        mock_anthropic.return_value = mock_client

        result = classify_with_haiku(str(prp_file), "prp")

        assert result.valid is False
        assert result.confidence == 0.5
        assert "Classification error" in str(result.issues)

    @patch('ce.blending.classification.anthropic.Anthropic')
    def test_classify_with_haiku_invalid_json(self, mock_anthropic, tmp_path):
        """Test Haiku returns invalid JSON is handled."""
        prp_file = tmp_path / "test-prp.md"
        prp_file.write_text("""# PRP-1: Feature

Build it.
""")

        # Mock invalid JSON response
        mock_client = Mock()
        mock_message = Mock()
        mock_message.content = [Mock(text='This is not JSON')]
        mock_client.messages.create.return_value = mock_message
        mock_anthropic.return_value = mock_client

        result = classify_with_haiku(str(prp_file), "prp")

        assert result.valid is False
        assert "invalid JSON" in str(result.issues)


class TestClassifyFile:
    """Tests for classify_file() main interface function."""

    def test_classify_file_prp_high_confidence(self, tmp_path):
        """Test classify_file with high confidence doesn't call Haiku."""
        prp_file = tmp_path / "PRP-1.md"
        prp_file.write_text("""---
prp_id: "1"
---

# PRP-1: Feature

## TL;DR
Build feature.

## Context
Background.

## Implementation
Steps.

## Validation
Tests.
""")

        with patch('ce.blending.classification.classify_with_haiku') as mock_haiku:
            result = classify_file(str(prp_file))

            assert result.valid is True
            assert result.file_type == "prp"
            mock_haiku.assert_not_called()  # High confidence, no Haiku

    @patch('ce.blending.classification.classify_with_haiku')
    def test_classify_file_prp_low_confidence(self, mock_haiku, tmp_path):
        """Test classify_file with low confidence triggers Haiku."""
        prp_file = tmp_path / "PRP-99.md"
        prp_file.write_text("""# PRP-99: Old Feature

## Implementation
Build it.
""")

        # Mock Haiku result
        mock_haiku.return_value = ClassificationResult(
            valid=True,
            confidence=0.8,
            issues=["Haiku classified as valid"],
            file_type="prp"
        )

        result = classify_file(str(prp_file))

        assert result.valid is True
        assert result.file_type == "prp"
        mock_haiku.assert_called_once()  # Low confidence, Haiku called

    def test_classify_file_infers_type_from_path(self, tmp_path):
        """Test classify_file infers type from file path."""
        # PRP path
        prp_file = tmp_path / "PRPs" / "PRP-1.md"
        prp_file.parent.mkdir()
        prp_file.write_text("""---
prp_id: "1"
---

# PRP-1: Feature

## Implementation
Build.

## Validation
Test.
""")

        result = classify_file(str(prp_file))
        assert result.file_type == "prp"

        # Example path
        example_file = tmp_path / "examples" / "feature.md"
        example_file.parent.mkdir()
        example_file.write_text("""# Feature Example

## Code

```python
code()
```
""")

        result = classify_file(str(example_file))
        assert result.file_type == "example"

        # Memory path
        memory_file = tmp_path / ".serena" / "memories" / "memory.md"
        memory_file.parent.mkdir(parents=True)
        memory_file.write_text("""---
type: regular
created: "2025-11-05"
---

# Memory
""")

        result = classify_file(str(memory_file))
        assert result.file_type == "memory"

    def test_classify_file_garbage_immediate_return(self, tmp_path):
        """Test garbage file returns immediately without Haiku."""
        garbage_file = tmp_path / "STATUS-REPORT.md"
        garbage_file.write_text("""# Status Report

PRP-1 done.
""")

        with patch('ce.blending.classification.classify_with_haiku') as mock_haiku:
            result = classify_file(str(garbage_file))

            assert result.valid is False
            assert result.file_type == "garbage"
            mock_haiku.assert_not_called()  # Garbage immediate return


class TestMainCLI:
    """Tests for main() CLI interface."""

    def test_main_cli_interface(self, tmp_path, capsys):
        """Test CLI returns JSON and correct exit code."""
        prp_file = tmp_path / "PRP-1.md"
        prp_file.write_text("""---
prp_id: "1"
---

# PRP-1: Feature

## TL;DR
Build.

## Context
Background.

## Implementation
Steps.

## Validation
Test.
""")

        import sys
        sys.argv = ["classification.py", str(prp_file), "prp"]

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 0  # Valid file, exit code 0

        captured = capsys.readouterr()
        import json
        output = json.loads(captured.out)

        assert output["valid"] is True
        assert output["file_type"] == "prp"

    def test_main_cli_invalid_file(self, tmp_path, capsys):
        """Test CLI returns exit code 1 for invalid file."""
        invalid_file = tmp_path / "invalid.md"
        invalid_file.write_text("""# Random Doc

No PRP ID.
""")

        import sys
        sys.argv = ["classification.py", str(invalid_file), "prp"]

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1  # Invalid file, exit code 1

    def test_main_cli_no_arguments(self, capsys):
        """Test CLI with no arguments shows usage."""
        import sys
        sys.argv = ["classification.py"]

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

        captured = capsys.readouterr()
        assert "Usage:" in captured.out
