---
prp_id: PRP-34.3.3
feature_name: Examples NL-Dedupe Strategy
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
complexity: high
estimated_hours: 3.0
dependencies: [PRP-34.2.6]
batch_id: 34
stage: stage-3-parallel
execution_order: 10
merge_order: 10
worktree_path: ../ctx-eng-plus-prp-34-3-3
branch_name: prp-34-3-3-examples-strategy
---

# PRP-34.3.3: Examples NL-Dedupe Strategy

## 1. TL;DR

**Objective**: Implement semantic deduplication of examples using Haiku for fast comparison.

**What**: ExamplesBlendStrategy that copies framework examples + skips if target has >90% similar examples. Uses Haiku for cheap, fast similarity checks. Handles 13 framework examples + 0-N target examples with hash-based identity check before semantic comparison.

**Why**: Examples directory can accumulate duplicates during initialization. Semantic deduplication prevents redundant examples while preserving unique user content. Haiku provides cost-effective comparison (12x cheaper than Sonnet, ~3-5x faster).

**Effort**: 3.0 hours

**Dependencies**: PRP-34.2.6 (LLM Client Integration) - requires BlendingLLM with check_similarity() method

**Files Modified**:
- `tools/ce/blending/strategies/examples.py` (new)
- `tools/tests/test_blend_examples.py` (new)

## 2. Context

### Background

PRP-34.1.1 established the core blending framework with strategy pattern. PRP-34.2.6 added LLM capabilities via BlendingLLM. PRP-34.3.3 implements the Examples domain strategy using Haiku-powered semantic deduplication.

**Current State**:
- No examples blending strategy exists
- Framework has 13 reference examples in `.ce/examples/`
- Target projects may have 0-N examples
- Manual initialization risks duplicate examples

**Target State**:
- ExamplesBlendStrategy class extends BlendStrategy
- Hash deduplication for exact matches (O(1) lookup)
- Haiku semantic similarity for near-duplicates (>90% threshold)
- Philosophy: "Copy ours + skip if target has equivalent"
- Preserves unique target examples (imported separately, not part of this strategy)

**Example Scenario**:
```
Framework: 13 examples (INITIALIZATION.md, TOOL-USAGE-GUIDE.md, etc.)
Target: 8 examples (3 identical hash, 2 similar >90%, 3 unique)

Process:
1. Hash check: Skip 3 framework examples (exact duplicates)
2. Similarity check: Skip 2 framework examples (>90% similar)
3. Copy: 8 framework examples (new to target)
Result: 8 + 3 unique target examples = 11 total
```

### Constraints and Considerations

1. **KISS Principle**: Simple hash + semantic check, no complex clustering
2. **No Fishy Fallbacks**: API errors bubble up with troubleshooting
3. **Function Limits**: Target 50 lines max per function
4. **Real Functionality**: Actual Haiku API calls, no mocked similarity
5. **Haiku-Only Operations**: All comparisons use Haiku (classification + similarity)
6. **Hash First Strategy**: Check exact duplicates before expensive LLM calls
7. **Threshold**: 0.9 similarity = duplicate (configurable via blend-config.yml)
8. **Comparison Scope**: Title + description + code snippets (not full file)
9. **Token Optimization**: Truncate content to first 1500 chars per example
10. **Error Handling**: Continue on single comparison failure (log warning)

### Blending Philosophy

**"Copy ours (framework), import theirs (target) where not contradictory"**

For Examples domain:
- Framework examples are authoritative reference documentation
- Target examples that are >90% similar are considered duplicates (skip framework)
- Unique target examples are preserved (imported via user-files strategy)
- Additive merging: Combine framework + unique target examples

### Documentation References

**Internal**:
- PRP-34 INITIAL: Complete blending system vision
- PRP-34.1.1: Core framework (BlendStrategy base class)
- PRP-34.2.6: LLM client (check_similarity() method)
- `.ce/blend-config.yml`: Similarity threshold configuration
- `examples/INITIALIZATION.md`: Reference example for comparison

**External**:
- Anthropic Haiku: https://docs.anthropic.com/claude/docs/models-overview#claude-3-5-haiku
- Semantic similarity: https://en.wikipedia.org/wiki/Semantic_similarity
- Hash deduplication: https://en.wikipedia.org/wiki/Hash_function

## 3. Implementation Steps

### Phase 1: Setup and Structure (20 min)

**Goal**: Create module structure and validate dependencies

**Steps**:

1. **Verify BlendingLLM available** (from PRP-34.2.6):
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.llm_client import BlendingLLM; print('✓ BlendingLLM available')"
```

2. **Create strategies directory** (if not exists from PRP-34.1.1):
```bash
mkdir -p /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/strategies
touch /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/strategies/__init__.py
```

3. **Create examples.py module**:
```bash
touch /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/strategies/examples.py
```

4. **Verify framework examples exist**:
```bash
ls -la /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/*.md | head -5
# Expected: INITIALIZATION.md, TOOL-USAGE-GUIDE.md, templates/, etc.
```

**Validation**: Module file exists, BlendingLLM importable, framework examples found

### Phase 2: ExamplesBlendStrategy Core (40 min)

**Goal**: Implement strategy class with hash deduplication

**File**: `tools/ce/blending/strategies/examples.py`

**Implementation**:

```python
"""Examples blending strategy with semantic deduplication."""

import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Set, Optional

from ce.blending.llm_client import BlendingLLM

logger = logging.getLogger(__name__)


class ExamplesBlendStrategy:
    """
    Blend framework and target examples with semantic deduplication.

    Philosophy: "Copy ours + skip if target has equivalent"

    Process:
    1. Hash deduplication: Skip framework examples with identical hash
    2. Semantic deduplication: Skip framework examples >90% similar to target
    3. Copy remaining framework examples to target

    Usage:
        >>> strategy = ExamplesBlendStrategy(llm_client)
        >>> result = strategy.blend(framework_examples_dir, target_examples_dir, context)
    """

    def __init__(self, llm_client: BlendingLLM, similarity_threshold: float = 0.9):
        """
        Initialize examples blending strategy.

        Args:
            llm_client: BlendingLLM instance for semantic comparison
            similarity_threshold: Similarity threshold 0.0-1.0 (default: 0.9)
        """
        self.llm = llm_client
        self.threshold = similarity_threshold
        logger.debug(f"ExamplesBlendStrategy initialized (threshold={self.threshold})")

    def blend(
        self,
        framework_dir: Path,
        target_dir: Path,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Blend framework and target examples.

        Args:
            framework_dir: Framework examples directory (.ce/examples/)
            target_dir: Target examples directory (examples/)
            context: Optional context dict (backup_dir, dry_run, etc.)

        Returns:
            Dict with:
                - copied: List of copied example files
                - skipped_hash: List of examples skipped (exact duplicate)
                - skipped_similar: List of examples skipped (>threshold similar)
                - errors: List of error messages
                - token_usage: Dict with total input/output tokens

        Raises:
            ValueError: If framework_dir or target_dir invalid
        """
        if not framework_dir.is_dir():
            raise ValueError(f"Framework examples dir not found: {framework_dir}")

        # Create target dir if not exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Get all framework examples
        framework_examples = self._get_examples(framework_dir)
        target_examples = self._get_examples(target_dir)

        logger.info(
            f"Blending examples: {len(framework_examples)} framework, "
            f"{len(target_examples)} target"
        )

        # Track results
        copied = []
        skipped_hash = []
        skipped_similar = []
        errors = []

        # Build target hash set for O(1) lookup
        target_hashes = self._build_hash_set(target_examples)

        # Process each framework example
        for fw_example in framework_examples:
            try:
                # Phase 1: Hash deduplication
                fw_hash = self._hash_file(fw_example)
                if fw_hash in target_hashes:
                    logger.debug(f"Skip {fw_example.name} (exact duplicate)")
                    skipped_hash.append(fw_example.name)
                    continue

                # Phase 2: Semantic deduplication
                is_duplicate, similar_file = self._check_semantic_similarity(
                    fw_example, target_examples
                )
                if is_duplicate:
                    logger.debug(
                        f"Skip {fw_example.name} (similar to {similar_file})"
                    )
                    skipped_similar.append(fw_example.name)
                    continue

                # Phase 3: Copy framework example
                target_path = target_dir / fw_example.name
                if context and context.get("dry_run"):
                    logger.info(f"[DRY RUN] Would copy {fw_example.name}")
                else:
                    target_path.write_text(fw_example.read_text())
                    logger.info(f"✓ Copied {fw_example.name}")
                copied.append(fw_example.name)

            except Exception as e:
                error_msg = f"Failed to process {fw_example.name}: {e}"
                logger.warning(error_msg)
                errors.append(error_msg)
                # Continue processing remaining examples

        # Get token usage
        token_usage = self.llm.get_token_usage()

        logger.info(
            f"Examples blending complete: {len(copied)} copied, "
            f"{len(skipped_hash)} hash-skipped, {len(skipped_similar)} similarity-skipped"
        )

        return {
            "copied": copied,
            "skipped_hash": skipped_hash,
            "skipped_similar": skipped_similar,
            "errors": errors,
            "token_usage": token_usage
        }

    def _get_examples(self, examples_dir: Path) -> List[Path]:
        """Get all .md files in examples directory (non-recursive)."""
        if not examples_dir.exists():
            return []
        return [f for f in examples_dir.iterdir() if f.suffix == ".md" and f.is_file()]

    def _hash_file(self, file_path: Path) -> str:
        """Compute SHA256 hash of file content."""
        content = file_path.read_bytes()
        return hashlib.sha256(content).hexdigest()

    def _build_hash_set(self, examples: List[Path]) -> Set[str]:
        """Build set of file hashes for O(1) lookup."""
        return {self._hash_file(ex) for ex in examples}
```

**Validation**:
- No syntax errors: `python3 -m py_compile tools/ce/blending/strategies/examples.py`
- Imports work: `python3 -c "from ce.blending.strategies.examples import ExamplesBlendStrategy"`
- Class instantiates with LLM client

### Phase 3: Semantic Similarity Method (40 min)

**Goal**: Implement Haiku-based similarity check with comparison prompt

**Add to `examples.py`**:

```python
    def _check_semantic_similarity(
        self,
        framework_example: Path,
        target_examples: List[Path]
    ) -> tuple[bool, Optional[str]]:
        """
        Check if framework example is semantically similar to any target example.

        Uses Haiku for fast, cheap comparison.

        Args:
            framework_example: Framework example file
            target_examples: List of target example files

        Returns:
            Tuple of (is_duplicate, similar_file_name)
            - is_duplicate: True if any target example >threshold similar
            - similar_file_name: Name of similar file (or None)
        """
        if not target_examples:
            return (False, None)

        # Extract comparison content from framework example
        fw_content = self._extract_comparison_content(framework_example)

        # Compare against each target example
        for target_example in target_examples:
            target_content = self._extract_comparison_content(target_example)

            # Call Haiku via BlendingLLM
            try:
                result = self.llm.check_similarity(
                    fw_content, target_content, threshold=self.threshold
                )

                if result["similar"]:
                    logger.debug(
                        f"{framework_example.name} similar to {target_example.name} "
                        f"(score: {result['score']:.2f})"
                    )
                    return (True, target_example.name)

            except Exception as e:
                # Log warning but continue (fail open, copy framework example)
                logger.warning(
                    f"Similarity check failed for {framework_example.name} vs "
                    f"{target_example.name}: {e}"
                )
                # Continue to next target example

        # No similar examples found
        return (False, None)

    def _extract_comparison_content(self, example_file: Path) -> str:
        """
        Extract comparison content from example file.

        Returns first 1500 chars (title + description + code snippets).
        This optimizes token usage while preserving semantic meaning.

        Args:
            example_file: Example markdown file

        Returns:
            Comparison content (truncated to 1500 chars)
        """
        content = example_file.read_text()

        # Truncate to 1500 chars for token optimization
        # This typically includes: title, description, first code snippet
        comparison_content = content[:1500]

        # If truncated mid-code-block, add closing fence
        if comparison_content.count("```") % 2 != 0:
            comparison_content += "\n```"

        return comparison_content
```

**Validation**:
- Method signature correct
- Returns tuple (bool, Optional[str])
- Truncation handles code blocks gracefully

### Phase 4: Unit Tests (60 min)

**Goal**: Create comprehensive test suite with mock LLM responses

**File**: `tools/tests/test_blend_examples.py`

**Implementation**:

```python
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


def test_comparison_content_truncation():
    """Test _extract_comparison_content truncates to 1500 chars."""
    strategy = ExamplesBlendStrategy(MagicMock())

    # Create file with >1500 chars
    tmp_file = Path("/tmp/test_example.md")
    long_content = "# Title\n\n" + ("x" * 2000)
    tmp_file.write_text(long_content)

    comparison = strategy._extract_comparison_content(tmp_file)

    assert len(comparison) <= 1500 + 10  # Allow for closing code fence
    tmp_file.unlink()


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
```

**Validation**: All tests pass

### Phase 5: Integration and Documentation (20 min)

**Goal**: Add to package exports, update config

**Steps**:

1. **Update strategies `__init__.py`**:

**File**: `tools/ce/blending/strategies/__init__.py`

```python
"""Blending strategies for CE domains."""

from .examples import ExamplesBlendStrategy

__all__ = ["ExamplesBlendStrategy"]
```

2. **Update blend-config.yml** (add examples domain):

**File**: `.ce/blend-config.yml` (if not exists from PRP-34.1.1, create it)

```yaml
# Examples domain configuration
domains:
  examples:
    strategy: nl-dedupe
    llm_model: haiku
    similarity_threshold: 0.9
    source: .ce/examples/
    target: examples/
```

3. **Run tests**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py -v
```

**Validation**: All tests pass, module exports correctly

## 4. Validation Gates

### Gate 1: Module Imports Successfully

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.strategies.examples import ExamplesBlendStrategy; print('✓ ExamplesBlendStrategy imports OK')"
```

**Expected**: "✓ ExamplesBlendStrategy imports OK"

**On Failure**:
- Check examples.py has no syntax errors: `python3 -m py_compile ce/blending/strategies/examples.py`
- Verify BlendingLLM available: `python3 -c "from ce.blending.llm_client import BlendingLLM"`
- Check strategies/__init__.py exports ExamplesBlendStrategy

### Gate 2: Hash Deduplication Works

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py::test_hash_deduplication_skips_exact_duplicates -v
```

**Expected**: Test passes

**On Failure**:
- Check _hash_file() implementation (SHA256 of bytes)
- Verify _build_hash_set() creates set correctly
- Check blend() method uses target_hashes for O(1) lookup

### Gate 3: Semantic Similarity Check Works

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py::test_semantic_deduplication_skips_similar_examples -v
```

**Expected**: Test passes

**On Failure**:
- Check _check_semantic_similarity() calls llm.check_similarity()
- Verify threshold parameter passed correctly
- Check return value (tuple of bool, Optional[str])

### Gate 4: Empty Target Copies All Framework Examples

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py::test_empty_target_copies_all_framework_examples -v
```

**Expected**: Test passes

**On Failure**:
- Check blend() handles empty target_examples list
- Verify _get_examples() returns empty list if dir doesn't exist
- Check copy logic executes when no duplicates found

### Gate 5: All Duplicates Handled (No Copies)

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py::test_all_duplicates_copies_nothing -v
```

**Expected**: Test passes

**On Failure**:
- Check hash deduplication runs before semantic check
- Verify all framework examples skipped when hash matches
- Check result["copied"] empty when all duplicates

### Gate 6: Comparison Prompt Returns Valid Response

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py::test_comparison_content_truncation -v
```

**Expected**: Test passes

**On Failure**:
- Check _extract_comparison_content() truncates to 1500 chars
- Verify code block closing (``` count even)
- Check truncation doesn't break markdown

### Gate 7: Unit Tests Pass (≥5 tests, ≥80% coverage)

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py -v --cov=ce.blending.strategies.examples --cov-report=term-missing
```

**Expected**: All tests pass, coverage ≥80%

**On Failure**:
- Run individual tests to isolate failure
- Check coverage report for untested branches
- Add tests for missing coverage areas

### Gate 8: Error Handling Continues on Failure

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_examples.py::test_error_handling_continues_on_failure -v
```

**Expected**: Test passes

**On Failure**:
- Check try/except in blend() method
- Verify errors logged but don't stop processing
- Check fail-open behavior (copy when comparison fails)

## 5. Testing Strategy

### Test Framework

**pytest** (existing in project)

### Test Files

- `tools/tests/test_blend_examples.py` - Examples strategy tests (unit)

### Test Categories

**Unit Tests** (with mock LLM):
- ✅ `test_examples_strategy_initialization` - Strategy initialization
- ✅ `test_hash_deduplication_skips_exact_duplicates` - Hash deduplication
- ✅ `test_semantic_deduplication_skips_similar_examples` - Semantic similarity
- ✅ `test_empty_target_copies_all_framework_examples` - Empty target handling
- ✅ `test_all_duplicates_copies_nothing` - All duplicates scenario
- ✅ `test_comparison_content_truncation` - Content truncation
- ✅ `test_dry_run_mode` - Dry run mode
- ✅ `test_error_handling_continues_on_failure` - Error handling
- ✅ `test_token_usage_returned` - Token tracking

**Edge Cases**:
- Empty framework examples directory
- Target directory doesn't exist (created)
- Very long example files (>1500 chars)
- Malformed markdown (missing code fences)
- LLM API errors during comparison

### Test Command

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Run all tests
uv run pytest tests/test_blend_examples.py -v

# Run with coverage
uv run pytest tests/test_blend_examples.py -v --cov=ce.blending.strategies.examples --cov-report=term-missing

# Run specific test
uv run pytest tests/test_blend_examples.py::test_hash_deduplication_skips_exact_duplicates -v
```

**Coverage Target**: ≥80% for examples.py

### Testing Patterns

**Mock Strategy**:
- Mock BlendingLLM.check_similarity() to control similarity scores
- Mock BlendingLLM.get_token_usage() for token tracking tests
- Use pytest tmp_path fixture for filesystem operations

**Real Functionality**:
- Actual file I/O (read, write, hash)
- Real hash computation (SHA256)
- Real path operations (pathlib.Path)

**No Integration Tests** (LLM client tested in PRP-34.2.6)

## 6. Rollout Plan

### Phase 1: Development (2 hours)

**Steps**:
1. ✅ Verify dependencies and create module (20 min)
2. ✅ Implement ExamplesBlendStrategy core (40 min)
3. ✅ Implement semantic similarity method (40 min)
4. ✅ Integration and documentation (20 min)

**Validation**: Module imports, methods implemented, no syntax errors

### Phase 2: Testing (1 hour)

**Steps**:
1. ✅ Create unit tests (60 min)
2. ✅ Run tests and fix failures (included above)

**Validation**: All tests pass, coverage ≥80%

### Phase 3: Integration (SUBSEQUENT PRPs)

**Prerequisites**: This PRP (34.3.3) complete

**Next PRPs that use ExamplesBlendStrategy**:
- **PRP-34.4.x**: Orchestrator integration (call examples strategy in Phase D)
- **PRP-34.5.x**: E2E initialization testing (validate examples blending)

**Integration**: Import ExamplesBlendStrategy in orchestrator, instantiate with LLM client

### Phase 4: Deployment (NOT THIS PRP)

**Prerequisites**: All PRP-34.x complete, E2E tests pass

**Steps**:
1. Merge all PRPs to main
2. Update INITIALIZATION.md to document examples deduplication
3. Test with real framework examples (13 files)
4. Measure token usage and cost for typical scenario

**Validation**: Full blending pipeline works end-to-end, examples deduplication confirmed

---

## Research Findings

### Codebase Analysis

**Framework Examples** (13 files in `.ce/examples/`):
- INITIALIZATION.md (~150 lines) - Main initialization guide
- TOOL-USAGE-GUIDE.md (~300 lines) - Tool selection guide
- templates/ subdirectory (PRP templates, memory templates)
- Other guides (batch execution, testing, validation)

**Typical Comparison Scenario**:
- Framework: 13 examples (~3000 lines total)
- Target: 0-10 examples (varies)
- Hash duplicates: 0-3 (common: INITIALIZATION.md, TOOL-USAGE-GUIDE.md)
- Semantic duplicates: 0-2 (custom guides similar to framework)
- Unique target: 0-5 (project-specific examples)

**Token Cost Estimate** (worst case: 13 fw × 10 target = 130 comparisons):
- Comparison content: 1500 chars ≈ 375 tokens per example
- Per comparison: 750 tokens input (2 examples)
- Total: 130 comparisons × 750 tokens = 97,500 tokens ≈ $0.024 (Haiku)
- Typical case (13 fw × 3 target = 39 comparisons): $0.007

**Hash Deduplication Benefit**:
- Eliminates exact duplicates in O(1) time
- Typical savings: 20-30% of comparisons (hash hits)
- No LLM cost for hash duplicates

### External Documentation

**Semantic Similarity**:
- Definition: Measure of how similar two texts are in meaning
- Range: 0.0 (completely different) to 1.0 (identical)
- Threshold: 0.9 chosen as "very similar, likely duplicates"

**Hash Deduplication**:
- SHA256: Cryptographic hash (collision-resistant)
- Use case: Exact duplicate detection
- Performance: O(1) lookup in hash set

**Haiku Performance** (from Anthropic docs):
- Speed: ~3-5x faster than Sonnet
- Cost: ~12x cheaper than Sonnet
- Context: 200k tokens (sufficient for examples)
- Output: 8k tokens (sufficient for similarity score)

---

## Appendix: Usage Examples

### Example 1: Blend Framework Examples

```python
from pathlib import Path
from ce.blending.llm_client import BlendingLLM
from ce.blending.strategies.examples import ExamplesBlendStrategy

# Initialize LLM client
llm = BlendingLLM()

# Initialize examples strategy
strategy = ExamplesBlendStrategy(llm, similarity_threshold=0.9)

# Define directories
framework_dir = Path("/Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/examples")
target_dir = Path("/Users/bprzybyszi/target-project/examples")

# Blend examples
result = strategy.blend(framework_dir, target_dir)

# Print summary
print(f"Copied: {len(result['copied'])} examples")
print(f"Skipped (hash): {len(result['skipped_hash'])} examples")
print(f"Skipped (similar): {len(result['skipped_similar'])} examples")
print(f"Errors: {len(result['errors'])}")
print(f"Token usage: {result['token_usage']['total_tokens']} tokens")
```

### Example 2: Dry Run Mode

```python
# Preview what would be copied without making changes
result = strategy.blend(
    framework_dir,
    target_dir,
    context={"dry_run": True}
)

print("Would copy:")
for example in result["copied"]:
    print(f"  - {example}")
```

### Example 3: Custom Similarity Threshold

```python
# Use stricter threshold (0.95) for deduplication
strict_strategy = ExamplesBlendStrategy(llm, similarity_threshold=0.95)

result = strict_strategy.blend(framework_dir, target_dir)

# More examples likely to be copied (fewer marked as duplicates)
```

---

## Success Criteria Summary

✅ **ExamplesBlendStrategy class** extends BlendStrategy pattern
✅ **Hash deduplication** skips exact duplicates (O(1) lookup)
✅ **Haiku similarity** checks semantic similarity (>90% threshold)
✅ **Framework examples** copied when <90% similar to target
✅ **Empty target** handled (copies all framework examples)
✅ **All duplicates** handled (skips all framework examples)
✅ **Comparison prompt** returns valid similarity score 0.0-1.0
✅ **Unit tests** pass (≥9 tests, ≥80% coverage)
✅ **Error handling** continues on single comparison failure
✅ **Token tracking** returned in result dict
✅ **KISS principle** - simple hash + semantic check, no complex clustering
✅ **No fishy fallbacks** - API errors bubble up, fail-open on comparison failure

---

## Next Steps After This PRP

**Immediate Dependencies** (PRPs that use ExamplesBlendStrategy):
1. **PRP-34.4.x**: Orchestrator integration - call examples strategy in Phase D
2. **PRP-34.5.x**: E2E initialization testing - validate examples blending

**Integration Pattern**:
```python
# In orchestrator (PRP-34.4.x)
from ce.blending.strategies.examples import ExamplesBlendStrategy

class BlendingOrchestrator:
    def blend_phase_d(self):
        # Initialize examples strategy
        examples_strategy = ExamplesBlendStrategy(
            self.llm_client,
            similarity_threshold=self.config["examples"]["similarity_threshold"]
        )

        # Blend examples
        result = examples_strategy.blend(
            framework_dir=Path(".ce/examples"),
            target_dir=Path("examples"),
            context={"dry_run": self.dry_run}
        )

        # Log results
        self.log_blending_result("examples", result)
```

---

**END OF PRP-34.3.3**
