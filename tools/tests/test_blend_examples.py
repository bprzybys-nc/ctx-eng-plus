"""Unit tests for examples blending strategy."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from ce.blending.strategies.examples import ExamplesBlendStrategy
from ce.blending.llm_client import BlendingLLM


@pytest.fixture
def mock_llm():
    """Create mock LLM client."""
    llm = MagicMock(spec=BlendingLLM)
    llm.get_token_usage.return_value = {
        "input_tokens": 100,
        "output_tokens": 50,
        "total_tokens": 150
    }
    return llm


@pytest.fixture
def framework_examples(tmp_path):
    """Create framework examples directory with test files."""
    fw_dir = tmp_path / "framework"
    fw_dir.mkdir()

    # Create 3 framework examples
    (fw_dir / "example1.md").write_text("# Example 1\n\nFramework example 1 content")
    (fw_dir / "example2.md").write_text("# Example 2\n\nFramework example 2 content")
    (fw_dir / "example3.md").write_text("# Example 3\n\nFramework example 3 content")

    return fw_dir


@pytest.fixture
def target_examples(tmp_path):
    """Create target examples directory with test files."""
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Create 1 target example (exact duplicate of example1)
    (target_dir / "example1.md").write_text("# Example 1\n\nFramework example 1 content")

    return target_dir


def test_examples_strategy_initialization(mock_llm):
    """Test ExamplesBlendStrategy initializes with LLM client."""
    strategy = ExamplesBlendStrategy(mock_llm, similarity_threshold=0.9)

    assert strategy.llm == mock_llm
    assert strategy.threshold == 0.9


def test_hash_deduplication_skips_exact_duplicates(
    mock_llm, framework_examples, target_examples
):
    """Test hash deduplication skips exact duplicates."""
    strategy = ExamplesBlendStrategy(mock_llm)

    # example1.md is exact duplicate (same hash)
    result = strategy.blend(framework_examples, target_examples)

    # Should skip example1 (hash match), copy example2 and example3
    assert "example1.md" in result["skipped_hash"]
    assert "example2.md" in result["copied"]
    assert "example3.md" in result["copied"]
    assert len(result["copied"]) == 2
    assert len(result["skipped_hash"]) == 1


def test_semantic_deduplication_skips_similar_examples(
    mock_llm, framework_examples, tmp_path
):
    """Test semantic deduplication skips >90% similar examples."""
    # Target has similar (not exact) example
    target_dir = tmp_path / "target_similar"
    target_dir.mkdir()
    (target_dir / "my-example.md").write_text(
        "# Example 1\n\nThis is very similar to framework example 1"
    )

    # Mock LLM to return high similarity for example1
    def mock_check_similarity(text1, text2, threshold):
        if "Example 1" in text1 and "Example 1" in text2:
            return {"similar": True, "score": 0.95}
        return {"similar": False, "score": 0.3}

    mock_llm.check_similarity.side_effect = mock_check_similarity

    strategy = ExamplesBlendStrategy(mock_llm, similarity_threshold=0.9)
    result = strategy.blend(framework_examples, target_dir)

    # Should skip example1 (similar), copy example2 and example3
    assert "example1.md" in result["skipped_similar"]
    assert "example2.md" in result["copied"]
    assert "example3.md" in result["copied"]
    assert len(result["skipped_similar"]) == 1


def test_empty_target_copies_all_framework_examples(mock_llm, framework_examples, tmp_path):
    """Test empty target directory copies all framework examples."""
    target_dir = tmp_path / "target_empty"
    target_dir.mkdir()

    # Mock LLM to return no similarity (no target examples to compare)
    mock_llm.check_similarity.return_value = {"similar": False, "score": 0.0}

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(framework_examples, target_dir)

    # Should copy all 3 framework examples
    assert len(result["copied"]) == 3
    assert "example1.md" in result["copied"]
    assert "example2.md" in result["copied"]
    assert "example3.md" in result["copied"]
    assert len(result["skipped_hash"]) == 0
    assert len(result["skipped_similar"]) == 0


def test_all_duplicates_copies_nothing(mock_llm, framework_examples, target_examples):
    """Test all framework examples are duplicates (hash or semantic)."""
    # Add example2 and example3 as exact duplicates
    (target_examples / "example2.md").write_text("# Example 2\n\nFramework example 2 content")
    (target_examples / "example3.md").write_text("# Example 3\n\nFramework example 3 content")

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(framework_examples, target_examples)

    # Should skip all (hash duplicates)
    assert len(result["copied"]) == 0
    assert len(result["skipped_hash"]) == 3


def test_comparison_content_truncation(tmp_path):
    """Test _extract_comparison_content truncates to 1500 chars."""
    strategy = ExamplesBlendStrategy(MagicMock())

    # Create file with >1500 chars
    tmp_file = tmp_path / "test_example.md"
    long_content = "# Title\n\n" + ("x" * 2000)
    tmp_file.write_text(long_content)

    comparison = strategy._extract_comparison_content(tmp_file)

    assert len(comparison) <= 1500 + 10  # Allow for closing code fence


def test_dry_run_mode(mock_llm, framework_examples, tmp_path):
    """Test dry_run mode logs actions without copying files."""
    target_dir = tmp_path / "target_dry"
    target_dir.mkdir()

    mock_llm.check_similarity.return_value = {"similar": False, "score": 0.0}

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {"dry_run": True}
    result = strategy.blend(framework_examples, target_dir, context)

    # Should report copied, but not actually write files
    assert len(result["copied"]) == 3
    assert not (target_dir / "example1.md").exists()
    assert not (target_dir / "example2.md").exists()


def test_error_handling_continues_on_failure(mock_llm, framework_examples, tmp_path):
    """Test continues processing on single comparison failure."""
    target_dir = tmp_path / "target_error"
    target_dir.mkdir()

    # Mock LLM to raise error for first comparison, succeed for rest
    call_count = [0]

    def mock_check_similarity(text1, text2, threshold):
        call_count[0] += 1
        if call_count[0] == 1:
            raise RuntimeError("API error")
        return {"similar": False, "score": 0.0}

    mock_llm.check_similarity.side_effect = mock_check_similarity

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(framework_examples, target_dir)

    # Should log error but continue (copy all examples)
    assert len(result["errors"]) == 0  # Errors in similarity check don't stop blending
    assert len(result["copied"]) == 3  # All examples copied (fail-open behavior)


def test_token_usage_returned(mock_llm, framework_examples, tmp_path):
    """Test token usage included in result."""
    target_dir = tmp_path / "target_tokens"
    target_dir.mkdir()

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(framework_examples, target_dir)

    assert "token_usage" in result
    assert result["token_usage"]["input_tokens"] == 100
    assert result["token_usage"]["output_tokens"] == 50


def test_invalid_framework_dir_switches_to_migration(mock_llm, tmp_path):
    """Test migration mode activates when framework_dir doesn't exist."""
    strategy = ExamplesBlendStrategy(mock_llm)

    invalid_dir = tmp_path / "nonexistent"
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "example.md").write_text("# Example")

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    context = {"target_dir": target_dir}

    # Should switch to migration mode, not raise error
    result = strategy.blend(invalid_dir, source_dir, context)

    assert result["success"] is True
    assert result["migrated"] == 1


def test_target_dir_created_if_not_exists(mock_llm, framework_examples, tmp_path):
    """Test target directory is created if it doesn't exist."""
    target_dir = tmp_path / "new_target"

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(framework_examples, target_dir)

    assert target_dir.exists()
    assert target_dir.is_dir()
    assert len(result["copied"]) == 3


def test_code_fence_closing_in_truncation(tmp_path):
    """Test code fence is properly closed when truncating."""
    strategy = ExamplesBlendStrategy(MagicMock())

    tmp_file = tmp_path / "code_example.md"
    # Content with code fence that will be cut off
    content = "# Example\n\n```python\n" + ("x" * 1500)
    tmp_file.write_text(content)

    comparison = strategy._extract_comparison_content(tmp_file)

    # Should have even number of code fences
    assert comparison.count("```") % 2 == 0


def test_mixed_duplicates_hash_and_semantic(mock_llm, framework_examples, tmp_path):
    """Test mixed scenario with both hash and semantic duplicates."""
    target_dir = tmp_path / "target_mixed"
    target_dir.mkdir()

    # Exact duplicate of example1
    (target_dir / "example1.md").write_text("# Example 1\n\nFramework example 1 content")

    # Similar to example2
    (target_dir / "similar-to-2.md").write_text("# Example 2\n\nVery similar to example 2")

    # Mock LLM to return similarity for example2 only
    def mock_check_similarity(text1, text2, threshold):
        if "Example 2" in text1 and "Example 2" in text2:
            return {"similar": True, "score": 0.92}
        return {"similar": False, "score": 0.1}

    mock_llm.check_similarity.side_effect = mock_check_similarity

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(framework_examples, target_dir)

    # example1 skipped (hash), example2 skipped (semantic), example3 copied
    assert len(result["skipped_hash"]) == 1
    assert len(result["skipped_similar"]) == 1
    assert len(result["copied"]) == 1
    assert "example3.md" in result["copied"]


def test_non_md_files_ignored(mock_llm, tmp_path):
    """Test non-.md files are ignored in examples directory."""
    fw_dir = tmp_path / "framework"
    fw_dir.mkdir()

    # Create mix of .md and non-.md files
    (fw_dir / "example.md").write_text("# Example")
    (fw_dir / "README.txt").write_text("Text file")
    (fw_dir / "config.json").write_text("{}")

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    strategy = ExamplesBlendStrategy(mock_llm)
    result = strategy.blend(fw_dir, target_dir)

    # Only .md file should be processed
    assert len(result["copied"]) == 1
    assert "example.md" in result["copied"]


# Migration mode tests

def test_migration_mode_when_framework_missing(mock_llm, tmp_path):
    """Test migration mode activates when framework dir missing."""
    # Source directory (user examples)
    source_dir = tmp_path / "source_examples"
    source_dir.mkdir()
    (source_dir / "user-example.md").write_text("# User Example")
    (source_dir / "user-guide.md").write_text("# User Guide")

    # Target directory (will have .ce created)
    target_dir = tmp_path / "target"
    target_dir.mkdir()

    # Framework dir doesn't exist
    framework_dir = tmp_path / "nonexistent_framework"

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {"target_dir": target_dir}

    result = strategy.blend(framework_dir, source_dir, context)

    # Migration mode results
    assert result["success"] is True
    assert result["migrated"] == 2
    assert result["skipped"] == 0

    # Files migrated to .ce/examples/user/
    user_dir = target_dir / ".ce" / "examples" / "user"
    assert (user_dir / "user-example.md").exists()
    assert (user_dir / "user-guide.md").exists()


def test_migration_preserves_subdirectories(mock_llm, tmp_path):
    """Test migration preserves subdirectory structure."""
    source_dir = tmp_path / "source_examples"
    source_dir.mkdir()

    # Create subdirectory structure
    patterns_dir = source_dir / "patterns"
    patterns_dir.mkdir()
    (patterns_dir / "pattern1.md").write_text("# Pattern 1")
    (patterns_dir / "pattern2.py").write_text("# Pattern code")

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    framework_dir = tmp_path / "nonexistent"

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {"target_dir": target_dir}

    result = strategy.blend(framework_dir, source_dir, context)

    # Check subdirectory preserved
    user_patterns = target_dir / ".ce" / "examples" / "user" / "patterns"
    assert user_patterns.exists()
    assert (user_patterns / "pattern1.md").exists()
    assert (user_patterns / "pattern2.py").exists()
    assert result["migrated"] == 2


def test_migration_hash_deduplication(mock_llm, tmp_path):
    """Test migration skips files with identical hashes."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "example.md").write_text("# Example content")

    target_dir = tmp_path / "target"
    user_dir = target_dir / ".ce" / "examples" / "user"
    user_dir.mkdir(parents=True)

    # Pre-existing file with same content
    (user_dir / "example.md").write_text("# Example content")

    framework_dir = tmp_path / "nonexistent"

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {"target_dir": target_dir}

    result = strategy.blend(framework_dir, source_dir, context)

    # Should skip duplicate
    assert result["migrated"] == 0
    assert result["skipped"] == 1


def test_migration_all_file_types(mock_llm, tmp_path):
    """Test migration handles all file types, not just .md."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "example.md").write_text("# MD file")
    (source_dir / "script.py").write_text("# Python file")
    (source_dir / "config.json").write_text("{}")
    (source_dir / "data.txt").write_text("Text")

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    framework_dir = tmp_path / "nonexistent"

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {"target_dir": target_dir}

    result = strategy.blend(framework_dir, source_dir, context)

    # All file types migrated
    assert result["migrated"] == 4
    user_dir = target_dir / ".ce" / "examples" / "user"
    assert (user_dir / "example.md").exists()
    assert (user_dir / "script.py").exists()
    assert (user_dir / "config.json").exists()
    assert (user_dir / "data.txt").exists()


def test_migration_empty_source_directory(mock_llm, tmp_path):
    """Test migration handles empty source directory gracefully."""
    source_dir = tmp_path / "empty_source"
    source_dir.mkdir()

    target_dir = tmp_path / "target"
    target_dir.mkdir()

    framework_dir = tmp_path / "nonexistent"

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {"target_dir": target_dir}

    result = strategy.blend(framework_dir, source_dir, context)

    # No files to migrate
    assert result["success"] is True
    assert result["migrated"] == 0
    assert result["skipped"] == 0


def test_migration_requires_target_dir_in_context(mock_llm, tmp_path):
    """Test migration raises error if context missing target_dir."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "example.md").write_text("# Example")

    framework_dir = tmp_path / "nonexistent"

    strategy = ExamplesBlendStrategy(mock_llm)
    context = {}  # Missing target_dir

    with pytest.raises(ValueError, match="target_dir"):
        strategy.blend(framework_dir, source_dir, context)
