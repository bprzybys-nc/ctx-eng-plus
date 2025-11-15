---
prp_id: PRP-34.2.6
feature_name: LLM Client Integration
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
complexity: medium
estimated_hours: 1.5
dependencies: [PRP-34.1.1]
batch_id: 34
stage: stage-2-parallel
execution_order: 7
merge_order: 7
worktree_path: ../ctx-eng-plus-prp-34-2-6
branch_name: prp-34-2-6-llm-client
---

# PRP-34.2.6: LLM Client Integration

## 1. TL;DR

**Objective**: Create Claude SDK wrapper with Haiku + Sonnet hybrid support for intelligent blending operations.

**What**: BlendingLLM class that wraps Anthropic SDK to provide model-specific operations - Haiku for fast/cheap classification and similarity checks, Sonnet for high-quality document blending. Enables NL-based strategies for CLAUDE.md, Memories, and Examples domains.

**Why**: Phase C blending strategies need LLM capabilities for semantic understanding. Haiku provides fast, cost-effective classification and similarity scoring. Sonnet provides high-quality merging that understands framework philosophy. Hybrid approach optimizes for both speed and quality.

**Effort**: 1.5 hours

**Dependencies**: PRP-34.1.1 (Core Blending Framework) - requires BlendStrategy base class and orchestrator integration points

**Files Modified**:
- `tools/ce/blending/llm_client.py` (new)

## 2. Context

### Background

PRP-34.1.1 established the core blending framework with strategy pattern, backup/restore, and 4-phase pipeline. PRP-34.2.6 adds LLM capabilities needed by NL-based blending strategies.

**Current State**:
- Core framework exists (strategies, orchestrator, validation)
- No LLM integration for semantic operations
- Strategies marked as "nl-blend" or "dedupe" in config need LLM client
- Manual blending currently relies on human judgment

**Target State**:
- BlendingLLM class wraps Anthropic SDK
- Model selection by operation type (Haiku=speed, Sonnet=quality)
- Three core operations: blend_content(), check_similarity(), classify_file()
- Token usage tracking for quota management
- Graceful error handling with actionable messages

**Use Cases by Domain**:

1. **CLAUDE.md** (Sonnet blending):
   - Merge framework + target CLAUDE.md files
   - Respect framework rules, preserve user customizations
   - Understand section semantics, not just text concatenation

2. **Memories** (Haiku similarity + Sonnet merge):
   - Fast similarity scoring between framework and user memories
   - High-quality merging of similar memories (dedupe)
   - Preserve distinct memories, blend overlapping content

3. **Examples** (Haiku deduplication):
   - Fast semantic similarity checks between examples
   - Confidence scoring for duplicate detection
   - Cheap operation for potentially large example sets

4. **Classification** (Haiku validation):
   - Validate CE pattern compliance (Phase B)
   - Filter garbage files (reports, summaries, initials)
   - Fast confidence scoring (0.0-1.0)

### Model Selection Strategy

**Claude 3.5 Haiku** (`claude-3-5-haiku-20241022`):
- **Speed**: ~3-5x faster than Sonnet
- **Cost**: ~10x cheaper than Sonnet
- **Use Cases**: Classification, similarity scoring, validation, deduplication
- **Token Limit**: 200k context, 8k output

**Claude Sonnet 4.5** (`claude-sonnet-4-5-20250929`):
- **Quality**: Superior understanding of complex instructions
- **Use Cases**: Document blending, content merging, semantic integration
- **Token Limit**: 200k context, 16k output

**Hybrid Workflow Example** (Memories):
```
1. Haiku: Check similarity between 23 framework memories and 15 user memories
   → 345 comparisons, $0.50, 30 seconds
2. Sonnet: Merge 8 pairs with >0.9 similarity
   → 8 merge operations, $2.00, 60 seconds
Total: $2.50, 90 seconds vs Sonnet-only: $20, 240 seconds
```

### Constraints and Considerations

1. **KISS Principle**: Simple wrapper, no complex abstractions
2. **No Fishy Fallbacks**: API errors bubble up with troubleshooting
3. **Function Limits**: Target 50 lines max per function
4. **Real Functionality**: Actual API calls, no mocked responses
5. **UV Package Management**: Use `uv add anthropic` (done in PRP-34.1.1)
6. **Environment Variables**: Uses `ANTHROPIC_API_KEY` from environment
7. **Error Handling**: Retries with exponential backoff (rate limits)
8. **Token Tracking**: Return token counts for quota monitoring
9. **Prompt Engineering**: Enforce blending philosophy in system prompts
10. **Timeout Handling**: Configurable timeouts, fail fast on network issues

### Blending Philosophy Enforcement

All Sonnet blending operations include this system instruction:

```
Blending Philosophy: "Copy ours (framework), import theirs (target) where not contradictory"

Rules:
1. Framework content is authoritative - preserve all framework sections
2. Target customizations that don't contradict framework are preserved
3. When conflict exists, framework wins (with explanation comment)
4. Additive merging preferred - combine rather than replace
5. User-specific content (names, paths, project details) always preserved
```

### Documentation References

**Internal**:
- PRP-34 INITIAL: Complete blending system vision
- PRP-34.1.1: Core framework (depends on this PRP)
- `.ce/blend-config.yml`: LLM configuration (api_key_env, timeout, max_retries)
- `.ce/RULES.md`: Framework rules for blending context

**External**:
- Anthropic SDK: https://docs.anthropic.com/claude/reference/getting-started
- Messages API: https://docs.anthropic.com/claude/reference/messages
- Model comparison: https://docs.anthropic.com/claude/docs/models-overview
- Rate limiting: https://docs.anthropic.com/claude/reference/rate-limits

## 3. Implementation Steps

### Phase 1: Setup and Structure (15 min)

**Goal**: Create module structure and validate Anthropic SDK dependency

**Steps**:

1. **Verify Anthropic SDK installed**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "import anthropic; print(f'✓ Anthropic SDK {anthropic.__version__}')"
```

If not installed (PRP-34.1.1 should have added it):
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv add anthropic>=0.40.0
uv sync
```

2. **Create llm_client.py module**:
```bash
touch /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/llm_client.py
```

3. **Verify blending package exists** (from PRP-34.1.1):
```bash
ls -la /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/
# Expected: __init__.py, core.py, strategies/, validation.py
```

**Validation**: Module file exists, Anthropic SDK available

### Phase 2: BlendingLLM Class Core (30 min)

**Goal**: Implement class initialization and model configuration

**File**: `tools/ce/blending/llm_client.py`

**Implementation**:

```python
"""LLM client for blending operations with Haiku + Sonnet hybrid support."""

import os
import logging
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Model configurations
HAIKU_MODEL = "claude-3-5-haiku-20241022"
SONNET_MODEL = "claude-sonnet-4-5-20250929"

# Blending philosophy system prompt
BLENDING_PHILOSOPHY = """
Blending Philosophy: "Copy ours (framework), import theirs (target) where not contradictory"

Rules:
1. Framework content is authoritative - preserve all framework sections
2. Target customizations that don't contradict framework are preserved
3. When conflict exists, framework wins (with explanation comment)
4. Additive merging preferred - combine rather than replace
5. User-specific content (names, paths, project details) always preserved
"""


class BlendingLLM:
    """
    Claude SDK wrapper for blending operations.

    Provides hybrid model support:
    - Haiku: Fast/cheap classification and similarity checks
    - Sonnet: High-quality document blending

    Usage:
        >>> llm = BlendingLLM()
        >>> result = llm.blend_content(framework, target, rules)
        >>> similarity = llm.check_similarity(text1, text2)
        >>> classification = llm.classify_file(content)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize LLM client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            timeout: Request timeout in seconds (default: 60)
            max_retries: Max retry attempts for rate limits (default: 3)

        Raises:
            ValueError: If API key not provided and not in environment
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required\n"
                "🔧 Troubleshooting:\n"
                "  1. Set ANTHROPIC_API_KEY environment variable\n"
                "  2. Or pass api_key parameter to BlendingLLM()\n"
                "  3. Get key from: https://console.anthropic.com/settings/keys"
            )

        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize Anthropic client
        try:
            self.client = Anthropic(
                api_key=self.api_key,
                timeout=timeout,
                max_retries=max_retries
            )
            logger.debug("✓ BlendingLLM initialized")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Anthropic client: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Verify network connectivity\n"
                f"  3. Check Anthropic status: https://status.anthropic.com"
            ) from e

        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def get_token_usage(self) -> Dict[str, int]:
        """
        Get cumulative token usage.

        Returns:
            Dict with input_tokens, output_tokens, total_tokens
        """
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }

    def _track_tokens(self, usage: Any) -> None:
        """Track tokens from API response usage object."""
        if usage:
            self.total_input_tokens += getattr(usage, 'input_tokens', 0)
            self.total_output_tokens += getattr(usage, 'output_tokens', 0)
```

**Validation**:
- No syntax errors: `python3 -m py_compile tools/ce/blending/llm_client.py`
- Imports work: `python3 -c "from ce.blending.llm_client import BlendingLLM"`
- Initialization fails gracefully without API key

### Phase 3: blend_content() Method (20 min)

**Goal**: Implement Sonnet-based document blending

**Add to `llm_client.py`**:

```python
    def blend_content(
        self,
        framework_content: str,
        target_content: Optional[str],
        rules_content: Optional[str] = None,
        domain: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Blend framework and target content using Sonnet.

        Uses high-quality model for semantic understanding of blending philosophy.

        Args:
            framework_content: Framework version (authoritative)
            target_content: Target version (may be None)
            rules_content: Framework rules (e.g., RULES.md content)
            domain: Domain name for context (e.g., "claude_md", "memories")

        Returns:
            Dict with:
                - blended: Blended content (str)
                - model: Model used (str)
                - tokens: Token usage dict
                - confidence: Blend confidence 0.0-1.0 (float)

        Raises:
            RuntimeError: If API call fails after retries
        """
        logger.info(f"Blending {domain} content with Sonnet...")

        # Build prompt
        prompt_parts = [BLENDING_PHILOSOPHY]

        if rules_content:
            prompt_parts.append(f"\n## Framework Rules\n\n{rules_content}")

        prompt_parts.append(f"\n## Framework Content\n\n{framework_content}")

        if target_content:
            prompt_parts.append(f"\n## Target Content\n\n{target_content}")
        else:
            # No target content - just validate framework
            prompt_parts.append("\n## Target Content\n\n(No existing content)")

        prompt_parts.append(
            f"\n## Task\n\n"
            f"Blend the framework and target content for the '{domain}' domain. "
            f"Follow the blending philosophy above. Output ONLY the blended content, "
            f"no explanations or markdown code blocks."
        )

        prompt = "".join(prompt_parts)

        try:
            # Call Sonnet
            response = self.client.messages.create(
                model=SONNET_MODEL,
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Track tokens
            self._track_tokens(response.usage)

            # Extract blended content
            blended = response.content[0].text

            # Calculate confidence (heuristic: presence of both framework and target markers)
            confidence = 1.0
            if target_content and target_content.strip():
                # Check if blend includes elements from both
                has_framework = any(
                    marker in blended
                    for marker in ["## Core Principles", "## Quick Commands"]
                )
                has_target = len(blended) > len(framework_content) * 0.8
                confidence = 0.9 if (has_framework and has_target) else 0.7

            logger.info(
                f"✓ Blended {domain} "
                f"({response.usage.input_tokens} in, "
                f"{response.usage.output_tokens} out)"
            )

            return {
                "blended": blended,
                "model": SONNET_MODEL,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                },
                "confidence": confidence
            }

        except Exception as e:
            logger.error(f"❌ Blending failed: {e}")
            raise RuntimeError(
                f"Sonnet blend_content() failed for {domain}: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Check network connectivity\n"
                f"  3. Verify content size < 200k tokens\n"
                f"  4. Check rate limits: https://console.anthropic.com/settings/limits"
            ) from e
```

**Validation**:
- Method signature correct
- Returns expected dict structure
- Error handling includes troubleshooting

### Phase 4: check_similarity() Method (15 min)

**Goal**: Implement Haiku-based fast similarity comparison

**Add to `llm_client.py`**:

```python
    def check_similarity(
        self,
        text1: str,
        text2: str,
        threshold: float = 0.9
    ) -> Dict[str, Any]:
        """
        Check semantic similarity between two texts using Haiku.

        Fast, cheap operation for similarity scoring.

        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold 0.0-1.0 (default: 0.9)

        Returns:
            Dict with:
                - similar: Boolean (similarity >= threshold)
                - score: Similarity score 0.0-1.0 (float)
                - model: Model used (str)
                - tokens: Token usage dict

        Raises:
            RuntimeError: If API call fails after retries
        """
        logger.debug("Checking similarity with Haiku...")

        prompt = f"""Compare these two texts for semantic similarity.

Text 1:
{text1[:1000]}...

Text 2:
{text2[:1000]}...

Rate similarity on scale 0.0-1.0 where:
- 0.0 = Completely different topics/purposes
- 0.5 = Related but distinct content
- 0.9 = Very similar, likely duplicates
- 1.0 = Identical or nearly identical

Output ONLY a number between 0.0 and 1.0, nothing else."""

        try:
            response = self.client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Track tokens
            self._track_tokens(response.usage)

            # Parse similarity score
            score_text = response.content[0].text.strip()
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))  # Clamp to [0.0, 1.0]
            except ValueError:
                # Failed to parse - default to low similarity
                logger.warning(f"Failed to parse similarity score: {score_text}")
                score = 0.0

            similar = score >= threshold

            logger.debug(
                f"Similarity: {score:.2f} ({'similar' if similar else 'different'})"
            )

            return {
                "similar": similar,
                "score": score,
                "model": HAIKU_MODEL,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"❌ Similarity check failed: {e}")
            raise RuntimeError(
                f"Haiku check_similarity() failed: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Check network connectivity\n"
                f"  3. Verify text size reasonable (< 1000 chars per text)\n"
                f"  4. Check rate limits"
            ) from e
```

**Validation**:
- Returns similarity score 0.0-1.0
- Handles parse errors gracefully
- Logs debug info for troubleshooting

### Phase 5: classify_file() Method (15 min)

**Goal**: Implement Haiku-based pattern validation

**Add to `llm_client.py`**:

```python
    def classify_file(
        self,
        content: str,
        expected_patterns: List[str],
        file_path: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Classify file content for CE pattern compliance using Haiku.

        Fast validation for Phase B classification.

        Args:
            content: File content to classify
            expected_patterns: List of expected CE patterns (e.g., ["YAML header", "## sections"])
            file_path: File path for context

        Returns:
            Dict with:
                - valid: Boolean (passes CE pattern checks)
                - confidence: Confidence score 0.0-1.0 (float)
                - issues: List of validation issues (List[str])
                - model: Model used (str)
                - tokens: Token usage dict

        Raises:
            RuntimeError: If API call fails after retries
        """
        logger.debug(f"Classifying {file_path} with Haiku...")

        patterns_text = "\n".join(f"- {p}" for p in expected_patterns)

        prompt = f"""Validate this file against CE (Context Engineering) patterns.

File: {file_path}

Expected patterns:
{patterns_text}

Content (first 2000 chars):
{content[:2000]}...

Respond in this format:
VALID: yes/no
CONFIDENCE: 0.0-1.0
ISSUES: comma-separated list of issues (or "none")

Example:
VALID: yes
CONFIDENCE: 0.95
ISSUES: none"""

        try:
            response = self.client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Track tokens
            self._track_tokens(response.usage)

            # Parse classification result
            result_text = response.content[0].text.strip()

            valid = False
            confidence = 0.0
            issues = []

            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith('VALID:'):
                    valid = 'yes' in line.lower()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                        confidence = max(0.0, min(1.0, confidence))
                    except (ValueError, IndexError):
                        confidence = 0.5
                elif line.startswith('ISSUES:'):
                    issues_text = line.split(':', 1)[1].strip()
                    if issues_text.lower() != 'none':
                        issues = [i.strip() for i in issues_text.split(',')]

            logger.debug(
                f"Classification: {'valid' if valid else 'invalid'} "
                f"(confidence: {confidence:.2f})"
            )

            return {
                "valid": valid,
                "confidence": confidence,
                "issues": issues,
                "model": HAIKU_MODEL,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"❌ Classification failed: {e}")
            raise RuntimeError(
                f"Haiku classify_file() failed for {file_path}: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Check network connectivity\n"
                f"  3. Verify content size < 200k tokens\n"
                f"  4. Check rate limits"
            ) from e
```

**Validation**:
- Parses structured response correctly
- Handles malformed responses gracefully
- Returns expected dict structure

### Phase 6: Integration and Testing (15 min)

**Goal**: Add module to package, create basic tests

**Steps**:

1. **Update `__init__.py`** in blending package:

**File**: `tools/ce/blending/__init__.py`

```python
"""Blending framework for CE initialization."""

from .core import backup_context, BlendingOrchestrator
from .llm_client import BlendingLLM
from .validation import validate_all_domains

__all__ = [
    'backup_context',
    'BlendingOrchestrator',
    'BlendingLLM',
    'validate_all_domains'
]
```

2. **Create unit tests**:

**File**: `tools/tests/test_llm_client.py`

```python
"""Unit tests for LLM client."""

import pytest
import os
from ce.blending.llm_client import BlendingLLM


def test_blending_llm_requires_api_key():
    """Test BlendingLLM raises error without API key."""
    # Save and clear API key
    original_key = os.environ.get("ANTHROPIC_API_KEY")
    if "ANTHROPIC_API_KEY" in os.environ:
        del os.environ["ANTHROPIC_API_KEY"]

    try:
        with pytest.raises(ValueError, match="API key required"):
            BlendingLLM()
    finally:
        # Restore API key
        if original_key:
            os.environ["ANTHROPIC_API_KEY"] = original_key


def test_blending_llm_accepts_api_key_parameter():
    """Test BlendingLLM accepts API key as parameter."""
    llm = BlendingLLM(api_key="sk-test-key-123")
    assert llm.api_key == "sk-test-key-123"
    assert llm.timeout == 60
    assert llm.max_retries == 3


def test_blending_llm_tracks_token_usage():
    """Test token usage tracking."""
    llm = BlendingLLM(api_key="sk-test-key")

    # Initial state
    usage = llm.get_token_usage()
    assert usage["input_tokens"] == 0
    assert usage["output_tokens"] == 0
    assert usage["total_tokens"] == 0


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="Requires ANTHROPIC_API_KEY for live API test"
)
def test_check_similarity_live():
    """Test check_similarity with live API (integration test)."""
    llm = BlendingLLM()

    # Similar texts
    result = llm.check_similarity(
        "The quick brown fox jumps over the lazy dog",
        "A fast brown fox leaps over a sleepy dog"
    )

    assert "similar" in result
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0
    assert result["model"] == "claude-3-5-haiku-20241022"

    # Different texts
    result2 = llm.check_similarity(
        "Python programming language",
        "Chocolate cake recipe"
    )

    assert result2["score"] < 0.5  # Should be dissimilar


# Add more integration tests if ANTHROPIC_API_KEY available
```

3. **Run tests**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_llm_client.py -v
```

**Validation**: Tests pass (at least basic tests without API key)

## 4. Validation Gates

### Gate 1: Module Imports Successfully

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.llm_client import BlendingLLM; print('✓ BlendingLLM imports OK')"
```

**Expected**: "✓ BlendingLLM imports OK"

**On Failure**:
- Check llm_client.py has no syntax errors: `python3 -m py_compile ce/blending/llm_client.py`
- Verify Anthropic SDK installed: `uv run python -c "import anthropic"`
- Check __init__.py exports BlendingLLM

### Gate 2: BlendingLLM Initializes with ANTHROPIC_API_KEY

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
export ANTHROPIC_API_KEY="sk-test-key"
uv run python -c "from ce.blending.llm_client import BlendingLLM; llm = BlendingLLM(); print('✓ Initialization OK')"
```

**Expected**: "✓ Initialization OK"

**On Failure**:
- Check __init__ method implementation
- Verify api_key parameter or env var handling
- Check error message includes troubleshooting steps

### Gate 3: blend_content() Uses Sonnet Model

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.llm_client import BlendingLLM, SONNET_MODEL; print(f'Sonnet model: {SONNET_MODEL}')"
```

**Expected**: "Sonnet model: claude-sonnet-4-5-20250929"

**On Failure**:
- Check SONNET_MODEL constant value
- Verify blend_content() uses SONNET_MODEL in client.messages.create()

### Gate 4: check_similarity() Uses Haiku Model

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.llm_client import BlendingLLM, HAIKU_MODEL; print(f'Haiku model: {HAIKU_MODEL}')"
```

**Expected**: "Haiku model: claude-3-5-haiku-20241022"

**On Failure**:
- Check HAIKU_MODEL constant value
- Verify check_similarity() and classify_file() use HAIKU_MODEL

### Gate 5: API Errors Handled Gracefully

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
# Test with invalid API key
export ANTHROPIC_API_KEY="sk-invalid"
uv run python -c "from ce.blending.llm_client import BlendingLLM; llm = BlendingLLM(); llm.check_similarity('a', 'b')" 2>&1 | grep "🔧"
```

**Expected**: Output contains "🔧 Troubleshooting:" section

**On Failure**:
- Check RuntimeError messages include troubleshooting
- Verify try/except blocks catch API exceptions
- Check error messages are actionable

### Gate 6: Token Usage Tracked

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "
from ce.blending.llm_client import BlendingLLM
llm = BlendingLLM(api_key='sk-test')
usage = llm.get_token_usage()
assert 'input_tokens' in usage
assert 'output_tokens' in usage
assert 'total_tokens' in usage
print('✓ Token tracking OK')
"
```

**Expected**: "✓ Token tracking OK"

**On Failure**:
- Check get_token_usage() implementation
- Verify _track_tokens() updates counters
- Check all API calls invoke _track_tokens()

### Gate 7: Unit Tests Pass

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_llm_client.py -v
```

**Expected**: All tests pass (at least 3 tests)

**On Failure**:
- Run individual tests to isolate failure
- Check test output for specific assertion errors
- Verify test mocking doesn't interfere with real API key tests

### Gate 8: Prompt Templates Enforce Blending Philosophy

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.llm_client import BLENDING_PHILOSOPHY; assert 'Copy ours' in BLENDING_PHILOSOPHY; print('✓ Philosophy enforced')"
```

**Expected**: "✓ Philosophy enforced"

**On Failure**:
- Check BLENDING_PHILOSOPHY constant includes all 5 rules
- Verify blend_content() includes BLENDING_PHILOSOPHY in prompt
- Check prompt construction prepends philosophy to all blend requests

## 5. Testing Strategy

### Test Framework

**pytest** (existing in project)

### Test Files

- `tools/tests/test_llm_client.py` - LLM client tests (unit + integration)

### Test Categories

**Unit Tests** (no API calls):
- ✅ `test_blending_llm_requires_api_key` - API key validation
- ✅ `test_blending_llm_accepts_api_key_parameter` - Parameter handling
- ✅ `test_blending_llm_tracks_token_usage` - Token tracking

**Integration Tests** (requires ANTHROPIC_API_KEY):
- ✅ `test_check_similarity_live` - Live Haiku similarity check
- ✅ `test_blend_content_live` - Live Sonnet blending (optional, expensive)
- ✅ `test_classify_file_live` - Live Haiku classification (optional)

**Error Handling Tests**:
- ✅ Test invalid API key raises clear error
- ✅ Test network timeout handled gracefully
- ✅ Test malformed API responses parsed safely

### Test Command

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Run all tests (unit only if no API key)
uv run pytest tests/test_llm_client.py -v

# Run with coverage
uv run pytest tests/test_llm_client.py -v --cov=ce.blending.llm_client --cov-report=term-missing

# Run integration tests (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="sk-..."
uv run pytest tests/test_llm_client.py -v -m "not skipif"
```

**Coverage Target**: ≥80% for llm_client.py

### Testing Patterns

**Real Functionality**:
- Live API tests use actual Anthropic SDK (when API key available)
- No mocked HTTP responses (use pytest.mark.skipif for live tests)
- Token tracking validated with real usage objects

**Error Handling**:
- Test API key validation (missing, invalid)
- Test malformed API responses (parse errors)
- Test network timeouts (if configurable)

**Edge Cases**:
- Empty content strings
- Very long content (near token limits)
- Invalid similarity threshold values
- Missing expected_patterns in classify_file()

## 6. Rollout Plan

### Phase 1: Development (1 hour)

**Steps**:
1. ✅ Verify Anthropic SDK dependency (5 min)
2. ✅ Implement BlendingLLM core class (30 min)
3. ✅ Implement blend_content() method (20 min)
4. ✅ Implement check_similarity() method (15 min)
5. ✅ Implement classify_file() method (15 min)

**Validation**: All methods implement, no syntax errors, imports work

### Phase 2: Testing (30 min)

**Steps**:
1. ✅ Update package __init__.py (5 min)
2. ✅ Create unit tests (15 min)
3. ✅ Run tests and fix failures (10 min)

**Validation**: All unit tests pass, integration tests run if API key available

### Phase 3: Integration (SUBSEQUENT PRPs)

**Prerequisites**: This PRP (34.2.6) complete

**Next PRPs that use BlendingLLM**:
- **PRP-34.2.2**: Classification module (uses classify_file())
- **PRP-34.3.2**: CLAUDE.md strategy (uses blend_content())
- **PRP-34.3.3**: Memories strategy (uses check_similarity() + blend_content())
- **PRP-34.3.4**: Examples strategy (uses check_similarity())

**Integration**: Import BlendingLLM in strategy implementations, pass via context dict

### Phase 4: Deployment (NOT THIS PRP)

**Prerequisites**: All PRP-34.3.x strategies complete, E2E tests pass

**Steps**:
1. Merge all PRPs to main
2. Update INITIALIZATION.md to note LLM-powered blending
3. Document token costs and rate limits
4. Create troubleshooting guide for API errors

**Validation**: Full blending pipeline works end-to-end

---

## Research Findings

### Codebase Analysis

**Existing API Client Patterns** (from generate.py, drift_analyzer.py):
- Use of environment variables for API keys
- Timeout configuration via parameters
- Error handling with actionable troubleshooting messages
- Token tracking for quota management
- Retry logic with exponential backoff (implicit in Anthropic SDK)

**Logging Patterns** (from logging_config.py):
- Unicode symbols for visual clarity (✓, ✗, ⚠️, 🔧)
- Debug level for verbose operations
- Info level for major milestones
- Error level with troubleshooting sections

**Configuration Patterns** (from blend-config.yml):
- `llm.api_key_env: ANTHROPIC_API_KEY` - Environment variable name
- `llm.timeout: 60` - Default timeout
- `llm.max_retries: 3` - Default retry count

### External Documentation

**Anthropic SDK** (v0.40.0+):
- Client initialization: `Anthropic(api_key=..., timeout=..., max_retries=...)`
- Messages API: `client.messages.create(model=..., max_tokens=..., messages=[...])`
- Response structure: `response.content[0].text` for text output
- Usage tracking: `response.usage.input_tokens`, `response.usage.output_tokens`
- Rate limiting: SDK handles retries with exponential backoff automatically

**Model Specifications**:
- **Haiku**: 200k context, 8k output, ~$0.25/M input tokens, ~$1.25/M output tokens
- **Sonnet 4.5**: 200k context, 16k output, ~$3/M input tokens, ~$15/M output tokens
- **Cost comparison**: Haiku 10x cheaper, 3-5x faster than Sonnet

**Best Practices**:
1. Use Haiku for classification, scoring, validation tasks
2. Use Sonnet for complex reasoning, blending, merging tasks
3. Truncate content in prompts to reduce token costs
4. Track token usage for quota management
5. Include clear instructions in prompts (output format)
6. Handle API errors gracefully with retries

---

## Appendix: Usage Examples

### Example 1: Blend CLAUDE.md

```python
from ce.blending.llm_client import BlendingLLM
from pathlib import Path

# Initialize LLM client
llm = BlendingLLM()

# Load content
framework_md = Path(".ce/CLAUDE.md").read_text()
target_md = Path("CLAUDE.md").read_text()
rules = Path(".ce/RULES.md").read_text()

# Blend
result = llm.blend_content(
    framework_content=framework_md,
    target_content=target_md,
    rules_content=rules,
    domain="claude_md"
)

# Write blended output
Path("CLAUDE.md").write_text(result["blended"])

print(f"✓ Blended with {result['confidence']:.2f} confidence")
print(f"Tokens: {result['tokens']['input']} in, {result['tokens']['output']} out")
```

### Example 2: Check Memory Similarity

```python
from ce.blending.llm_client import BlendingLLM
from pathlib import Path

llm = BlendingLLM()

# Load memories
framework_memory = Path(".ce/.serena/memories/code-style-conventions.md").read_text()
user_memory = Path(".serena/memories/my-style-guide.md").read_text()

# Check similarity
result = llm.check_similarity(framework_memory, user_memory, threshold=0.9)

if result["similar"]:
    print(f"✓ Similar (score: {result['score']:.2f}) - should blend")
else:
    print(f"Different (score: {result['score']:.2f}) - keep separate")
```

### Example 3: Classify File

```python
from ce.blending.llm_client import BlendingLLM
from pathlib import Path

llm = BlendingLLM()

# Load file to classify
content = Path("PRPs/USER-42-feature.md").read_text()

# Classify
result = llm.classify_file(
    content=content,
    expected_patterns=[
        "YAML header with prp_id",
        "## sections (TL;DR, Context, Implementation Steps)",
        "Validation Gates with bash commands"
    ],
    file_path="PRPs/USER-42-feature.md"
)

if result["valid"]:
    print(f"✓ Valid CE PRP (confidence: {result['confidence']:.2f})")
else:
    print(f"❌ Invalid PRP: {', '.join(result['issues'])}")
```

### Example 4: Token Tracking

```python
from ce.blending.llm_client import BlendingLLM

llm = BlendingLLM()

# Perform multiple operations
llm.check_similarity("text1", "text2")
llm.check_similarity("text3", "text4")
llm.classify_file("content", ["pattern1"], "file.md")

# Get total usage
usage = llm.get_token_usage()
print(f"Total tokens: {usage['total_tokens']}")
print(f"  Input: {usage['input_tokens']}")
print(f"  Output: {usage['output_tokens']}")

# Estimate cost (Haiku: $0.25/M input, $1.25/M output)
cost_usd = (
    usage['input_tokens'] / 1_000_000 * 0.25 +
    usage['output_tokens'] / 1_000_000 * 1.25
)
print(f"Estimated cost: ${cost_usd:.4f}")
```

---

## Success Criteria Summary

✅ **BlendingLLM class** initializes with ANTHROPIC_API_KEY from env
✅ **blend_content() method** uses claude-sonnet-4-5-20250929 for high-quality blending
✅ **check_similarity() method** uses claude-3-5-haiku-20241022 for fast comparison
✅ **classify_file() method** uses Haiku for fast validation
✅ **API errors** handled gracefully with actionable troubleshooting messages
✅ **Token usage** tracked via get_token_usage() method
✅ **Prompt templates** enforce blending philosophy (5 rules in system prompt)
✅ **Unit tests** pass (≥3 tests, integration tests optional)
✅ **Documentation** complete with docstrings and usage examples
✅ **KISS principle** - simple wrapper, clear code, single responsibility methods
✅ **No fishy fallbacks** - exceptions bubble up with 🔧 troubleshooting

---

## Next Steps After This PRP

**Immediate Dependencies** (PRPs that use BlendingLLM):
1. **PRP-34.2.2**: Classification module - uses classify_file() for Phase B validation
2. **PRP-34.3.2**: CLAUDE.md strategy - uses blend_content() for Sonnet blending
3. **PRP-34.3.3**: Memories strategy - uses check_similarity() + blend_content() for hybrid workflow
4. **PRP-34.3.4**: Examples strategy - uses check_similarity() for semantic deduplication

**Integration Pattern**:
```python
# In strategy implementations
from ce.blending.llm_client import BlendingLLM

class ClaudeMdBlendStrategy(BlendStrategy):
    def blend(self, framework_content, target_content, context):
        llm = context.get("llm_client")  # Passed from orchestrator
        result = llm.blend_content(framework_content, target_content, ...)
        return result["blended"]
```

---

**END OF PRP-34.2.6**
