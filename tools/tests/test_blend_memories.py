"""Unit tests for MemoriesBlendStrategy."""

import pytest
from pathlib import Path
from unittest.mock import Mock
import tempfile
import shutil
import yaml

from ce.blending.strategies.memories import MemoriesBlendStrategy, CRITICAL_MEMORIES, BlendResult


# Mock LLM client
class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, similarity_score=0.85, merge_result="Merged content"):
        self.similarity_score = similarity_score
        self.merge_result = merge_result
        self.check_similarity_calls = []
        self.blend_content_calls = []

    def check_similarity(self, text1, text2, threshold=0.9):
        """Mock similarity check."""
        self.check_similarity_calls.append({"text1": text1, "text2": text2, "threshold": threshold})
        return {
            "similar": self.similarity_score >= threshold,
            "score": self.similarity_score,
            "model": "claude-3-5-haiku-20241022",
            "tokens": {"input": 100, "output": 10}
        }

    def blend_content(self, framework_content, target_content, rules_content, domain):
        """Mock content blending."""
        self.blend_content_calls.append({
            "framework_content": framework_content,
            "target_content": target_content,
            "domain": domain
        })
        return {
            "blended": self.merge_result,
            "model": "claude-sonnet-4-5-20250929",
            "tokens": {"input": 200, "output": 50},
            "confidence": 0.9
        }


# Test fixtures
@pytest.fixture
def temp_dirs():
    """Create temp directories for testing."""
    framework = Path(tempfile.mkdtemp()) / ".serena/memories"
    target = Path(tempfile.mkdtemp()) / ".serena/memories"
    output = Path(tempfile.mkdtemp()) / ".serena/memories"

    framework.mkdir(parents=True)
    target.mkdir(parents=True)
    output.mkdir(parents=True)

    yield framework, target, output

    # Cleanup
    shutil.rmtree(framework.parent.parent)
    shutil.rmtree(target.parent.parent)
    shutil.rmtree(output.parent.parent)


def create_memory_file(path: Path, name: str, content: str, header: dict):
    """Helper to create memory file with YAML header."""
    yaml_str = yaml.dump(header, default_flow_style=False, sort_keys=False)
    full_content = f"---\n{yaml_str}---\n\n{content}\n"
    (path / name).write_text(full_content)


# Tests
def test_blend_high_similarity_skips_target(temp_dirs):
    """Test >90% similarity uses framework version."""
    framework, target, output = temp_dirs

    # Create identical files
    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(framework, "test.md", "Framework content", header)
    create_memory_file(target, "test.md", "Framework content (minor diff)", header)

    # Mock 95% similarity
    mock_client = MockLLMClient(similarity_score=0.95)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success
    assert "test.md" in result.skipped
    assert len(result.merged) == 0
    assert len(mock_client.blend_content_calls) == 0  # No Sonnet merge for high similarity


def test_blend_complementary_merges_with_sonnet(temp_dirs):
    """Test complementary content triggers Sonnet merge."""
    framework, target, output = temp_dirs

    header = {
        "type": "regular",
        "category": "docs",
        "tags": ["test"],
        "created": "2025-01-01",
        "updated": "2025-01-01"
    }
    create_memory_file(framework, "test.md", "Framework content", header)
    create_memory_file(target, "test.md", "Target has extra section", header)

    # Mock 70% similarity, not contradicting (>0.3)
    mock_client = MockLLMClient(similarity_score=0.70, merge_result="Merged both")
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success
    assert "test.md" in result.merged
    assert len(mock_client.blend_content_calls) == 1  # Sonnet merge called

    # Verify merged content
    merged_file = output / "test.md"
    assert merged_file.exists()
    content = merged_file.read_text()
    assert "Merged both" in content


def test_blend_contradicting_uses_framework(temp_dirs):
    """Test contradicting content uses framework version."""
    framework, target, output = temp_dirs

    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(framework, "test.md", "Use approach A", header)
    create_memory_file(target, "test.md", "Use approach B (opposite)", header)

    # Mock 20% similarity (< 0.3 = contradicting)
    mock_client = MockLLMClient(similarity_score=0.20)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success
    assert "test.md" in result.skipped

    # Verify framework content used
    content = (output / "test.md").read_text()
    assert "Use approach A" in content


def test_blend_critical_memory_always_framework(temp_dirs):
    """Test critical memories always use framework version."""
    framework, target, output = temp_dirs

    # Use first critical memory
    critical_name = list(CRITICAL_MEMORIES)[0]

    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(framework, critical_name, "Framework critical content", header)
    create_memory_file(target, critical_name, "Target modified content", header)

    # Mock shouldn't be called for critical memories
    mock_client = MockLLMClient(similarity_score=0.50)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success
    assert critical_name in result.copied
    assert len(mock_client.check_similarity_calls) == 0  # No LLM calls for critical

    # Verify framework content used
    content = (output / critical_name).read_text()
    assert "Framework critical content" in content


def test_blend_target_only_preserves_with_user_type(temp_dirs):
    """Test target-only memories preserved with type: user."""
    framework, target, output = temp_dirs

    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(target, "target-only.md", "Target only content", header)

    strategy = MemoriesBlendStrategy(llm_client=MockLLMClient())

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success
    assert "target-only.md (target-only)" in result.copied

    # Verify type: user header
    content = (output / "target-only.md").read_text()
    assert "type: user" in content
    assert "source: target-project" in content


def test_blend_yaml_headers_merged_correctly(temp_dirs):
    """Test YAML header blending rules."""
    framework, target, output = temp_dirs

    fw_header = {
        "type": "regular",
        "category": "docs",
        "tags": ["fw1", "fw2"],
        "created": "2025-01-15",
        "updated": "2025-01-20"
    }
    target_header = {
        "type": "critical",  # Should be ignored
        "category": "other",  # Should be ignored
        "tags": ["target1", "fw1"],  # Should merge
        "created": "2025-01-10",  # Earlier, should win
        "updated": "2025-01-25"  # Later, should win
    }

    create_memory_file(framework, "test.md", "Framework", fw_header)
    create_memory_file(target, "test.md", "Target", target_header)

    # Mock complementary for merge (>0.3 but <0.9)
    mock_client = MockLLMClient(similarity_score=0.70, merge_result="Merged content")
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success

    # Parse blended header
    content = (output / "test.md").read_text()
    parts = content.split("---", 2)
    blended_header = yaml.safe_load(parts[1])

    # Verify blending rules
    assert blended_header["type"] == "regular"  # Framework wins
    assert blended_header["category"] == "docs"  # Framework wins
    assert set(blended_header["tags"]) == {"fw1", "fw2", "target1"}  # Merged
    assert blended_header["created"] == "2025-01-10"  # Earlier date
    assert blended_header["updated"] == "2025-01-25"  # Later date


def test_blend_no_target_copies_framework(temp_dirs):
    """Test missing target files copy framework version."""
    framework, target, output = temp_dirs

    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(framework, "fw-only.md", "Framework only", header)

    strategy = MemoriesBlendStrategy(llm_client=MockLLMClient())

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    assert result.success
    assert "fw-only.md" in result.copied

    content = (output / "fw-only.md").read_text()
    assert "Framework only" in content


def test_blend_no_target_directory(temp_dirs):
    """Test blending when target directory doesn't exist."""
    framework, target, output = temp_dirs

    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(framework, "test.md", "Framework content", header)

    # Don't remove target directory, just pass None to simulate missing target
    strategy = MemoriesBlendStrategy(llm_client=MockLLMClient())

    context = {"output_path": output}
    # Pass None as target_content since it doesn't exist
    result = strategy.blend(framework, None, context)

    assert result.success
    assert "test.md" in result.copied
    assert len(result.merged) == 0


def test_blend_invalid_yaml_raises_error(temp_dirs):
    """Test that invalid YAML in memory file raises error."""
    framework, target, output = temp_dirs

    # Create framework file with valid YAML
    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(framework, "test.md", "Framework content", header)

    # Create target file with invalid YAML (triggers parsing during merge)
    invalid_content = "---\ninvalid: yaml: content:\n---\n\nBody"
    (target / "test.md").write_text(invalid_content)

    # Mock low similarity to trigger merge path (where parsing happens)
    mock_client = MockLLMClient(similarity_score=0.70)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    context = {"output_path": output}
    result = strategy.blend(framework, target, context)

    # Should fail with error during YAML parsing
    assert not result.success
    assert len(result.errors) > 0
    assert "test.md" in result.errors[0]


def test_validate_method(temp_dirs):
    """Test validate method works correctly."""
    framework, target, output = temp_dirs

    strategy = MemoriesBlendStrategy(llm_client=MockLLMClient())

    # Valid result
    valid_result = BlendResult(
        success=True,
        files_processed=5,
        skipped=[],
        merged=[],
        copied=["test.md"],
        errors=[]
    )
    assert strategy.validate(valid_result, {}) is True

    # Invalid result (has errors)
    invalid_result = BlendResult(
        success=False,
        files_processed=5,
        skipped=[],
        merged=[],
        copied=[],
        errors=["test.md: error"]
    )
    assert strategy.validate(invalid_result, {}) is False

    # Wrong type
    assert strategy.validate("not a BlendResult", {}) is False


def test_can_handle_method():
    """Test can_handle method returns True for memories domain."""
    strategy = MemoriesBlendStrategy(llm_client=MockLLMClient())

    assert strategy.can_handle("memories") is True
    assert strategy.can_handle("settings") is False
    assert strategy.can_handle("claude_md") is False
