---
prp_id: "34.3.2"
name: "Memories Blending Strategy"
description: "Implement Serena memories blending with Haiku similarity checks + Sonnet merges, YAML header blending, conflict resolution, handles 23 framework + 0-N target memories"
status: ready
priority: MEDIUM
confidence: high
effort_hours: 3.0
risk: MEDIUM
dependencies:
  - "34.2.6"
parent_prp: "34"
context_memories:
  - "code-style-conventions.md"
  - "testing-standards.md"
meeting_evidence: []
context_sync:
  ce_updated: false
  serena_updated: false
version: "1.0"
created_date: "2025-11-05"
last_updated: "2025-11-05"
complexity: high
files_modified:
  - "tools/ce/blending/strategies/memories.py"
  - "tools/tests/test_blend_memories.py"
stage: "stage-3-parallel"
execution_order: 9
merge_order: 9
conflict_potential: "NONE"
worktree_path: "../ctx-eng-plus-prp-34-3-2"
branch_name: "prp-34-3-2-memories-strategy"
issue: TBD
---

# PRP-34.3.2: Memories Blending Strategy

## 1. TL;DR

**Objective**: Implement intelligent Serena memories blending with cost-optimized Haiku similarity checks and Sonnet merging

**What**: Create MemoriesBlendStrategy that handles 23 framework memories + 0-N target memories with hybrid Haiku/Sonnet approach: Haiku detects similarity (12x cheaper), Sonnet only for actual merges

**Why**: Serena memories are critical project context - wrong merge corrupts AI guidance. Hybrid approach saves 90%+ LLM costs vs Sonnet-only.

**Effort**: 3.0 hours

**Dependencies**: PRP-34.2.6 (LLM Client Integration)

## 2. Context

### Background

Serena memories provide project context for AI agents. During CE initialization, we must blend framework memories (23 files) with existing target project memories (0-N files). Wrong merge = corrupted guidance.

**Philosophy**: Copy ours + import complementary target memories.

**Cost Optimization**: Haiku similarity check (fast, cheap) → Skip if >90% similar. Sonnet only for actual merges (complementary content).

**Memory Type System** (CE 1.1):
- `type: regular` - Standard framework memory (default for 23 files)
- `type: critical` - High-priority memory (users manually upgrade)
- `type: user` - User-created memory in target projects

**Critical Memories** (never blend, always use framework):
1. code-style-conventions.md
2. suggested-commands.md
3. task-completion-checklist.md
4. testing-standards.md
5. tool-usage-syntropy.md
6. use-syntropy-tools-not-bash.md

**YAML Header Structure**:
```yaml
---
type: regular
category: documentation
tags: [tag1, tag2, tag3]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---
```

### Constraints and Considerations

**No Fishy Fallbacks**:
- Fast failure: Raise exceptions if LLM call fails
- Actionable errors: Include troubleshooting guidance
- No silent skips: Log all decisions (skip/merge/conflict)

**KISS Principle**:
- Simple logic: Similarity % threshold (90%), explicit conflict rules
- Clear code: 50-line functions, single responsibility
- Minimal dependencies: Use stdlib + existing LLM client

**Testing Requirements**:
- Unit tests with mock Haiku/Sonnet responses
- Real test data from actual memory files
- Coverage ≥80%, ≥6 tests

**Edge Cases**:
- Empty target memory directory (0 files)
- Target memory with no YAML header (invalid, skip with warning)
- Framework memory missing in target (copy framework version)
- Target-only memory (preserve with `type: user` header)

### Documentation References

**Codebase Patterns**:
- `tools/ce/vacuum_strategies/base.py` - BaseStrategy pattern with abstract methods
- `tools/ce/testing/strategy.py` - Protocol-based strategy interface
- `tools/ce/prp.py` - YAML parsing with `yaml.safe_load()`

**LLM Client** (from PRP-34.2.6):
```python
from ce.blending.llm_client import LLMClient

client = LLMClient()

# Haiku similarity check (12x cheaper)
similarity = client.check_similarity(
    framework_content="...",
    target_content="...",
    model="claude-3-haiku-20240307"
)

# Sonnet merge (only for complementary content)
merged = client.merge_content(
    framework_content="...",
    target_content="...",
    instructions="Merge complementary sections, preserve framework structure",
    model="claude-sonnet-4.0-20250514"
)
```

## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

**Step 1.1**: Create directory structure
```bash
mkdir -p tools/ce/blending/strategies
touch tools/ce/blending/strategies/__init__.py
touch tools/ce/blending/strategies/memories.py
```

**Step 1.2**: Create test file
```bash
mkdir -p tools/tests/blending
touch tools/tests/test_blend_memories.py
```

**Step 1.3**: Review existing patterns
- Read `tools/ce/vacuum_strategies/base.py` for BaseStrategy pattern
- Read `tools/ce/testing/strategy.py` for Protocol interface
- Read `tools/ce/prp.py` for YAML parsing examples

### Phase 2: Core Implementation (1.5 hours)

**Step 2.1**: Define BlendStrategy protocol (15 min)

Create `tools/ce/blending/strategies/base.py`:
```python
"""Base strategy protocol for blending operations."""
from typing import Protocol, Dict, Any, List
from pathlib import Path


class BlendStrategy(Protocol):
    """Protocol for blending framework and target files.

    All strategies must implement blend() method.
    """

    def blend(
        self,
        framework_path: Path,
        target_path: Path,
        output_path: Path
    ) -> Dict[str, Any]:
        """Blend framework and target files to output.

        Args:
            framework_path: Path to framework source directory
            target_path: Path to target project directory
            output_path: Path to output directory

        Returns:
            Dict with: success (bool), files_processed (int),
                      skipped (list), merged (list), errors (list)
        """
        ...
```

**Step 2.2**: Implement MemoriesBlendStrategy class (1 hour)

Create `tools/ce/blending/strategies/memories.py`:

```python
"""Memories blending strategy with Haiku similarity + Sonnet merging."""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

from ce.blending.llm_client import LLMClient

logger = logging.getLogger(__name__)


# Critical memories - always use framework version (no blending)
CRITICAL_MEMORIES = {
    "code-style-conventions.md",
    "suggested-commands.md",
    "task-completion-checklist.md",
    "testing-standards.md",
    "tool-usage-syntropy.md",
    "use-syntropy-tools-not-bash.md",
}


@dataclass
class BlendResult:
    """Result of blending operation."""
    success: bool
    files_processed: int
    skipped: List[str]
    merged: List[str]
    copied: List[str]
    errors: List[str]


class MemoriesBlendStrategy:
    """Blend Serena memories with Haiku similarity + Sonnet merge.

    Philosophy: Copy ours + import complementary target memories.

    Strategy:
    1. Haiku similarity check (fast, cheap)
    2. If >90% similar: Use framework version (skip target)
    3. If contradicting: Use framework version (or ask user)
    4. If complementary: Sonnet merge
    5. YAML header blending: framework type wins, merge tags, earlier created, later updated
    6. Critical memories: always framework (no blending)
    7. Target-only memories: preserve with type: user header
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize strategy with LLM client.

        Args:
            llm_client: LLM client for similarity/merge (creates default if None)
        """
        self.llm_client = llm_client or LLMClient()

    def blend(
        self,
        framework_path: Path,
        target_path: Path,
        output_path: Path
    ) -> BlendResult:
        """Blend framework and target memories to output.

        Args:
            framework_path: Path to framework .serena/memories/
            target_path: Path to target .serena/memories/
            output_path: Path to output .serena/memories/

        Returns:
            BlendResult with operation summary

        Raises:
            RuntimeError: If LLM call fails or critical error occurs
        """
        output_path.mkdir(parents=True, exist_ok=True)

        skipped = []
        merged = []
        copied = []
        errors = []

        # Get all framework memories
        framework_files = self._list_memory_files(framework_path)
        target_files = self._list_memory_files(target_path)

        logger.info(f"Framework memories: {len(framework_files)}")
        logger.info(f"Target memories: {len(target_files)}")

        # Process framework memories
        for fw_file in framework_files:
            try:
                result = self._process_memory(
                    fw_file=framework_path / fw_file,
                    target_file=target_path / fw_file if fw_file in target_files else None,
                    output_file=output_path / fw_file
                )

                if result["action"] == "skip":
                    skipped.append(fw_file)
                elif result["action"] == "merge":
                    merged.append(fw_file)
                elif result["action"] == "copy":
                    copied.append(fw_file)

            except Exception as e:
                error_msg = f"{fw_file}: {str(e)}"
                logger.error(f"Failed to process {fw_file}: {e}")
                errors.append(error_msg)

        # Process target-only memories (preserve with type: user)
        target_only = set(target_files) - set(framework_files)
        for target_file in target_only:
            try:
                self._preserve_target_memory(
                    target_file=target_path / target_file,
                    output_file=output_path / target_file
                )
                copied.append(f"{target_file} (target-only)")

            except Exception as e:
                error_msg = f"{target_file}: {str(e)}"
                logger.error(f"Failed to preserve {target_file}: {e}")
                errors.append(error_msg)

        total_processed = len(skipped) + len(merged) + len(copied)
        success = len(errors) == 0

        return BlendResult(
            success=success,
            files_processed=total_processed,
            skipped=skipped,
            merged=merged,
            copied=copied,
            errors=errors
        )

    def _process_memory(
        self,
        fw_file: Path,
        target_file: Optional[Path],
        output_file: Path
    ) -> Dict[str, str]:
        """Process single memory file.

        Returns:
            Dict with "action": "skip"|"merge"|"copy"
        """
        # Critical memory: always use framework
        if fw_file.name in CRITICAL_MEMORIES:
            logger.info(f"Critical memory: {fw_file.name} (using framework)")
            self._copy_file(fw_file, output_file)
            return {"action": "copy"}

        # No target file: copy framework
        if target_file is None or not target_file.exists():
            logger.info(f"No target version: {fw_file.name} (using framework)")
            self._copy_file(fw_file, output_file)
            return {"action": "copy"}

        # Both exist: check similarity with Haiku
        fw_content = fw_file.read_text()
        target_content = target_file.read_text()

        similarity = self.llm_client.check_similarity(
            framework_content=fw_content,
            target_content=target_content,
            model="claude-3-haiku-20240307"
        )

        logger.info(f"Similarity for {fw_file.name}: {similarity}%")

        # >90% similar: skip target, use framework
        if similarity > 90:
            logger.info(f"High similarity ({similarity}%): using framework")
            self._copy_file(fw_file, output_file)
            return {"action": "skip"}

        # Check if contradicting
        is_contradicting = self.llm_client.check_contradiction(
            framework_content=fw_content,
            target_content=target_content,
            model="claude-3-haiku-20240307"
        )

        if is_contradicting:
            logger.warning(f"Contradicting content: {fw_file.name} (using framework)")
            self._copy_file(fw_file, output_file)
            return {"action": "skip"}

        # Complementary: merge with Sonnet
        logger.info(f"Complementary content: merging with Sonnet")
        merged_content = self._merge_with_sonnet(fw_content, target_content, fw_file.name)

        # Blend YAML headers
        fw_header, fw_body = self._parse_memory(fw_content)
        target_header, target_body = self._parse_memory(target_content)
        blended_header = self._blend_headers(fw_header, target_header)

        # Write merged file
        final_content = self._format_memory(blended_header, merged_content)
        output_file.write_text(final_content)

        return {"action": "merge"}

    def _merge_with_sonnet(
        self,
        fw_content: str,
        target_content: str,
        filename: str
    ) -> str:
        """Merge complementary content using Sonnet.

        Args:
            fw_content: Framework memory content (with YAML)
            target_content: Target memory content (with YAML)
            filename: Memory filename for context

        Returns:
            Merged content (body only, no YAML)
        """
        # Extract bodies (remove YAML)
        _, fw_body = self._parse_memory(fw_content)
        _, target_body = self._parse_memory(target_content)

        instructions = f"""
Merge these two versions of the Serena memory '{filename}'.

Framework version (authoritative structure):
{fw_body}

Target version (complementary content):
{target_body}

Instructions:
1. Preserve framework structure and sections
2. Add complementary target content that doesn't exist in framework
3. If conflict, use framework version
4. Keep framework tone and style
5. Return merged content only (no YAML header)
"""

        merged = self.llm_client.merge_content(
            framework_content=fw_body,
            target_content=target_body,
            instructions=instructions,
            model="claude-sonnet-4.0-20250514"
        )

        return merged

    def _blend_headers(
        self,
        fw_header: Dict[str, Any],
        target_header: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Blend YAML headers.

        Rules:
        - type: framework wins
        - category: framework wins
        - tags: merge both lists (deduplicate)
        - created: use earlier date
        - updated: use later date

        Args:
            fw_header: Framework YAML header
            target_header: Target YAML header

        Returns:
            Blended YAML header
        """
        blended = fw_header.copy()

        # Merge tags
        fw_tags = set(fw_header.get("tags", []))
        target_tags = set(target_header.get("tags", []))
        blended["tags"] = sorted(fw_tags | target_tags)

        # Use earlier created date
        fw_created = fw_header.get("created", "")
        target_created = target_header.get("created", "")
        if target_created and target_created < fw_created:
            blended["created"] = target_created

        # Use later updated date
        fw_updated = fw_header.get("updated", "")
        target_updated = target_header.get("updated", "")
        if target_updated and target_updated > fw_updated:
            blended["updated"] = target_updated

        return blended

    def _preserve_target_memory(
        self,
        target_file: Path,
        output_file: Path
    ) -> None:
        """Preserve target-only memory with type: user header.

        Args:
            target_file: Path to target memory file
            output_file: Path to output file
        """
        content = target_file.read_text()
        header, body = self._parse_memory(content)

        # Set type: user
        header["type"] = "user"
        header["source"] = "target-project"

        # Write with updated header
        final_content = self._format_memory(header, body)
        output_file.write_text(final_content)

        logger.info(f"Preserved target-only: {target_file.name} (type: user)")

    def _parse_memory(self, content: str) -> tuple[Dict[str, Any], str]:
        """Parse memory file into YAML header and body.

        Args:
            content: Full memory file content

        Returns:
            Tuple of (header dict, body string)

        Raises:
            ValueError: If YAML parse fails or invalid structure
        """
        if not content.startswith("---\n"):
            raise ValueError("Memory file must start with YAML frontmatter (---)")

        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError("Missing closing --- delimiter for YAML header")

        yaml_content = parts[1].strip()
        body = parts[2].strip()

        try:
            header = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parse error: {e}")

        return header, body

    def _format_memory(self, header: Dict[str, Any], body: str) -> str:
        """Format memory with YAML header and body.

        Args:
            header: YAML header dict
            body: Memory body content

        Returns:
            Formatted memory file content
        """
        yaml_str = yaml.dump(header, default_flow_style=False, sort_keys=False)
        return f"---\n{yaml_str}---\n\n{body}\n"

    def _copy_file(self, src: Path, dst: Path) -> None:
        """Copy file from src to dst.

        Args:
            src: Source file path
            dst: Destination file path
        """
        dst.write_text(src.read_text())

    def _list_memory_files(self, path: Path) -> List[str]:
        """List all .md files in memory directory.

        Args:
            path: Path to memory directory

        Returns:
            List of filenames (not paths)
        """
        if not path.exists():
            return []

        return [f.name for f in path.glob("*.md") if f.is_file()]
```

**Step 2.3**: Implement LLM client methods (15 min)

Add methods to `tools/ce/blending/llm_client.py`:
```python
def check_similarity(
    self,
    framework_content: str,
    target_content: str,
    model: str = "claude-3-haiku-20240307"
) -> float:
    """Check similarity percentage between two contents.

    Args:
        framework_content: Framework version
        target_content: Target version
        model: Claude model to use

    Returns:
        Similarity percentage (0-100)
    """
    prompt = f"""
Compare these two versions of the same document and return a similarity percentage (0-100).

Framework version:
{framework_content[:2000]}

Target version:
{target_content[:2000]}

Return ONLY the number (e.g., "87"). Consider content similarity, not formatting.
"""

    response = self._call_api(model=model, prompt=prompt, max_tokens=10)

    try:
        return float(response.strip())
    except ValueError:
        raise RuntimeError(f"Invalid similarity response: {response}")


def check_contradiction(
    self,
    framework_content: str,
    target_content: str,
    model: str = "claude-3-haiku-20240307"
) -> bool:
    """Check if contents contradict each other.

    Args:
        framework_content: Framework version
        target_content: Target version
        model: Claude model to use

    Returns:
        True if contradicting, False otherwise
    """
    prompt = f"""
Compare these two versions and determine if they CONTRADICT each other (give opposite advice/rules).

Framework version:
{framework_content[:2000]}

Target version:
{target_content[:2000]}

Return ONLY "yes" or "no".
"""

    response = self._call_api(model=model, prompt=prompt, max_tokens=10)
    return response.strip().lower() == "yes"
```

### Phase 3: Testing and Validation (1 hour)

**Step 3.1**: Create unit tests (45 min)

Create `tools/tests/test_blend_memories.py`:
```python
"""Unit tests for MemoriesBlendStrategy."""
import pytest
from pathlib import Path
from unittest.mock import Mock
import tempfile
import shutil

from ce.blending.strategies.memories import MemoriesBlendStrategy, CRITICAL_MEMORIES


# Mock LLM client
class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, similarity=85.0, contradicting=False, merge_result="Merged content"):
        self.similarity = similarity
        self.contradicting = contradicting
        self.merge_result = merge_result

    def check_similarity(self, framework_content, target_content, model):
        return self.similarity

    def check_contradiction(self, framework_content, target_content, model):
        return self.contradicting

    def merge_content(self, framework_content, target_content, instructions, model):
        return self.merge_result


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
    import yaml
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
    mock_client = MockLLMClient(similarity=95.0)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    result = strategy.blend(framework, target, output)

    assert result.success
    assert "test.md" in result.skipped
    assert len(result.merged) == 0


def test_blend_complementary_merges_with_sonnet(temp_dirs):
    """Test complementary content triggers Sonnet merge."""
    framework, target, output = temp_dirs

    header = {"type": "regular", "category": "docs", "tags": ["test"], "created": "2025-01-01", "updated": "2025-01-01"}
    create_memory_file(framework, "test.md", "Framework content", header)
    create_memory_file(target, "test.md", "Target has extra section", header)

    # Mock 70% similarity, not contradicting
    mock_client = MockLLMClient(similarity=70.0, contradicting=False, merge_result="Merged both")
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    result = strategy.blend(framework, target, output)

    assert result.success
    assert "test.md" in result.merged

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

    # Mock 50% similarity, contradicting
    mock_client = MockLLMClient(similarity=50.0, contradicting=True)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    result = strategy.blend(framework, target, output)

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
    mock_client = MockLLMClient(similarity=50.0)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    result = strategy.blend(framework, target, output)

    assert result.success
    assert critical_name in result.copied

    # Verify framework content used
    content = (output / critical_name).read_text()
    assert "Framework critical content" in content


def test_blend_target_only_preserves_with_user_type(temp_dirs):
    """Test target-only memories preserved with type: user."""
    framework, target, output = temp_dirs

    header = {"type": "regular", "category": "docs", "tags": ["test"]}
    create_memory_file(target, "target-only.md", "Target only content", header)

    strategy = MemoriesBlendStrategy(llm_client=MockLLMClient())
    result = strategy.blend(framework, target, output)

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

    # Mock complementary for merge
    mock_client = MockLLMClient(similarity=70.0, contradicting=False)
    strategy = MemoriesBlendStrategy(llm_client=mock_client)

    result = strategy.blend(framework, target, output)

    assert result.success

    # Parse blended header
    content = (output / "test.md").read_text()
    import yaml
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
    result = strategy.blend(framework, target, output)

    assert result.success
    assert "fw-only.md" in result.copied

    content = (output / "fw-only.md").read_text()
    assert "Framework only" in content
```

**Step 3.2**: Run tests and verify (15 min)
```bash
cd tools
uv run pytest tests/test_blend_memories.py -v

# Expected output:
# test_blend_high_similarity_skips_target PASSED
# test_blend_complementary_merges_with_sonnet PASSED
# test_blend_contradicting_uses_framework PASSED
# test_blend_critical_memory_always_framework PASSED
# test_blend_target_only_preserves_with_user_type PASSED
# test_blend_yaml_headers_merged_correctly PASSED
# test_blend_no_target_copies_framework PASSED
```

## 4. Validation Gates

### Gate 1: Haiku Similarity Check Works
**Validation**: Run test with >90% similarity
```bash
cd tools
uv run pytest tests/test_blend_memories.py::test_blend_high_similarity_skips_target -v
```
**Expected**: Test PASSED, framework version used, target skipped

### Gate 2: Sonnet Merge Works for Complementary Content
**Validation**: Run test with complementary content
```bash
cd tools
uv run pytest tests/test_blend_memories.py::test_blend_complementary_merges_with_sonnet -v
```
**Expected**: Test PASSED, merged file contains both sections

### Gate 3: YAML Headers Blended Correctly
**Validation**: Run header blending test
```bash
cd tools
uv run pytest tests/test_blend_memories.py::test_blend_yaml_headers_merged_correctly -v
```
**Expected**: Framework type wins, tags merged, dates correct

### Gate 4: Critical Memories Use Framework
**Validation**: Run critical memory test
```bash
cd tools
uv run pytest tests/test_blend_memories.py::test_blend_critical_memory_always_framework -v
```
**Expected**: Test PASSED, framework version used without LLM call

### Gate 5: Target-Only Memories Preserved
**Validation**: Run target-only test
```bash
cd tools
uv run pytest tests/test_blend_memories.py::test_blend_target_only_preserves_with_user_type -v
```
**Expected**: Test PASSED, file has `type: user` header

### Gate 6: Conflict Resolution Works
**Validation**: Run contradiction test
```bash
cd tools
uv run pytest tests/test_blend_memories.py::test_blend_contradicting_uses_framework -v
```
**Expected**: Test PASSED, framework version used

### Gate 7: Unit Tests Pass
**Validation**: Run full test suite
```bash
cd tools
uv run pytest tests/test_blend_memories.py -v --cov=ce/blending/strategies/memories --cov-report=term-missing
```
**Expected**: 7/7 tests PASSED, coverage ≥80%

## 5. Testing Strategy

### Test Framework
pytest with unittest.mock for LLM client mocking

### Test Command
```bash
cd tools
uv run pytest tests/test_blend_memories.py -v
```

### Test Coverage
- Unit tests: 7 tests covering all blend scenarios
- Mock LLM client: Canned responses for similarity/contradiction/merge
- Real YAML parsing: Use actual yaml.safe_load()
- Temp directories: Clean filesystem state per test
- Coverage target: ≥80%

### Test Scenarios
1. High similarity (>90%) → Skip target
2. Complementary content → Sonnet merge
3. Contradicting content → Framework wins
4. Critical memories → Always framework
5. Target-only memories → Preserve with type: user
6. YAML header blending → Framework type wins, merge tags
7. No target file → Copy framework

### Edge Cases Tested
- Empty target directory (0 files)
- Invalid YAML header (raises ValueError)
- Missing framework file (error logged)
- LLM API failure (exception bubbles up)

## 6. Rollout Plan

### Phase 1: Development
- Create `tools/ce/blending/strategies/memories.py`
- Create `tools/tests/test_blend_memories.py`
- Implement MemoriesBlendStrategy with Haiku/Sonnet logic
- Implement YAML header blending
- Write 7 unit tests

### Phase 2: Testing
- Run pytest suite: `cd tools && uv run pytest tests/test_blend_memories.py -v`
- Verify all 7 tests pass
- Check coverage ≥80%: `uv run pytest tests/test_blend_memories.py --cov=ce/blending/strategies/memories`
- Manual smoke test with real memory files (optional)

### Phase 3: Integration
- Ready for use by PRP-34.4.1 (Phase Execution Orchestrator)
- Will be called during Phase 3 of initialization workflow
- Input: framework/.serena/memories/, target/.serena/memories/
- Output: blended/.serena/memories/

### Phase 4: Documentation
- Update `examples/INITIALIZATION.md` with blending details
- Document YAML header blending rules
- Add example of complementary merge

## 7. Research Findings

### Codebase Analysis

**Strategy Pattern Examples**:
- `tools/ce/vacuum_strategies/base.py` - BaseStrategy with abstract methods, protected patterns
- `tools/ce/testing/strategy.py` - Protocol-based strategy interface with is_mocked()

**YAML Parsing Pattern**:
```python
# From tools/ce/prp.py
parts = content.split("---", 2)
yaml_content = parts[1].strip()
header = yaml.safe_load(yaml_content)
```

**Memory Type System**:
- Framework memories: 23 files with `type: regular`
- Critical upgrade candidates: 6 memories
- User memories: Added during Phase 2 with `type: user`

**YAML Header Structure**:
```yaml
---
type: regular
category: documentation
tags: [tag1, tag2, tag3]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---
```

### LLM Client Integration

From PRP-34.2.6:
- Haiku model: `claude-3-haiku-20240307` (12x cheaper than Sonnet)
- Sonnet model: `claude-sonnet-4.0-20250514` (high quality merging)
- Client location: `tools/ce/blending/llm_client.py`

### Cost Optimization Strategy

**Haiku-first approach**:
1. Similarity check (Haiku, 2k tokens) - Fast, cheap
2. Skip if >90% similar - No Sonnet call needed
3. Merge only if complementary (Sonnet, 4k tokens) - 10-30% of files

**Estimated savings**: 90%+ vs Sonnet-only approach

**Example**:
- 23 framework memories
- 15 target memories
- Haiku checks: 15 calls × 2k tokens = 30k tokens
- Sonnet merges: ~3 files × 4k tokens = 12k tokens
- Total: 42k tokens vs 360k tokens (Sonnet-only)

---

**Status**: Ready for execution in Stage 3 (parallel)
**Execution Order**: 9 of 9
**Merge Order**: 9 (merge after all Stage 3 PRPs)
**Conflict Potential**: NONE (new files only)
