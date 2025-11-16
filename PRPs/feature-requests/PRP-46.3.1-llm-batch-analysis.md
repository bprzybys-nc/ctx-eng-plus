---
prp_id: 46.3.1
feature_name: LLM Batch Analysis for Uncertain Candidates
batch_id: 46
stage: 3
order: 1
status: pending
created: 2025-11-16T00:00:00Z
updated: 2025-11-16T00:00:00Z
complexity: medium
estimated_hours: 2
dependencies: PRP-46.2.1 (Candidate format from prp_lifecycle_docs)
---

# LLM Batch Analysis for Uncertain Candidates

## 1. TL;DR

**Objective**: Add Haiku batch processing for vacuum candidates with 40-70% confidence to reduce manual review workload

**What**: Cost-effective LLM verification that batches 10-15 uncertain docs per API call, reducing costs by 90% ($0.30 → $0.03 for 100 docs)

**Why**: NLP provides semantic similarity but uncertain matches (40-70%) still need human review; Haiku batch analysis automates this verification at minimal cost

**Effort**: 2 hours (MEDIUM complexity, new LLM integration)

**Dependencies**: PRP-46.2.1 (needs Candidate format with `superseded_by` field from prp_lifecycle_docs strategy)

## 2. Context

### Background

After NLP semantic analysis (PRP-46.1.1, PRP-46.2.1), vacuum candidates are categorized by confidence:

- **HIGH (≥75%)**: Auto-flag for deletion (NLP confidence sufficient)
- **MEDIUM (40-70%)**: Uncertain - requires verification
- **LOW (<40%)**: Keep as-is (not lifecycle docs)

**Problem**: MEDIUM confidence candidates require manual review, typically 20-30% of total candidates.

**Example Workflow (Before LLM)**:

```
100 lifecycle docs detected by NLP:
- 45 HIGH confidence (≥75%) - auto-flagged
- 30 MEDIUM confidence (40-70%) - MANUAL REVIEW NEEDED
- 25 LOW confidence (<40%) - kept

Manual review time: 30 docs × 2 min = 60 minutes
```

**Example Workflow (After LLM Batch)**:

```
100 lifecycle docs detected by NLP:
- 45 HIGH confidence (≥75%) - auto-flagged
- 30 MEDIUM confidence (40-70%) - Haiku batch analysis:
  - 20 docs → YES (boosted to 90%) - auto-flagged
  - 10 docs → NO/PARTIAL (kept at 40-70%) - manual review

Manual review time: 10 docs × 2 min = 20 minutes (67% reduction)
API cost: 2 batches × $0.001 = $0.002 total
```

### Constraints and Considerations

**Batch Size Limits**:

- Haiku 200K context limit
- Safe batch size: 10-15 docs per call
- Token budget: ~15K per batch (10-15 comparisons × 1K per doc pair)

**Cost Optimization**:

- Individual calls: 100 docs × $0.003 = $0.30
- Batch calls: 100 docs ÷ 15 = ~7 batches × $0.001 = $0.007 (98% savings)
- Only process MEDIUM confidence (40-70%) - not HIGH or LOW

**Graceful Degradation**:

- API failures don't break vacuum workflow
- Keep original NLP confidence if LLM unavailable
- Fallback: Try smaller batches (5 docs) if 15-doc batch fails

**Integration Pattern**:

- LLMBatchAnalyzer is OPTIONAL enhancement
- Vacuum works without it (uses NLP confidence only)
- No hard dependency on Anthropic API

### Documentation References

**Anthropic Claude API**:

- Model: claude-3-haiku-20240307
- Context limit: 200K tokens
- Pricing: ~$0.001 per batch request
- Docs: <https://docs.anthropic.com/claude/reference/messages>

**Anthropic Python SDK**:

- Package: `anthropic`
- Install: `uv add anthropic`
- Client: `anthropic.Anthropic(api_key=...)`

**CE Vacuum Strategies**:

- `tools/ce/vacuum_strategies/base.py:tools/ce/vacuum_strategies/base.py:1-150` - Candidate dataclass
- `PRPs/feature-requests/PRP-46.2.1-prp-lifecycle-docs-strategy.md` - Generates candidates with `superseded_by` field

## 3. Implementation Steps

### Phase 1: Create LLMBatchAnalyzer Class (1 hour)

**Step 1: Create Module File** (5 min)

Create `tools/ce/vacuum_strategies/llm_analyzer.py`:

```python
"""LLM batch analyzer for uncertain vacuum candidates."""

import os
from pathlib import Path
from typing import List, Optional

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from .base import CleanupCandidate


class LLMBatchAnalyzer:
    """Batch analyze uncertain vacuum candidates using Claude Haiku.

    Only processes MEDIUM confidence (40-70%) candidates.
    Batches 10-15 docs per API call for cost efficiency.
    """

    MAX_DOCS_PER_BATCH = 15  # Haiku 200K context limit
    CONFIDENCE_THRESHOLD = (0.4, 0.7)  # MEDIUM tier (40-70%)
    MODEL = "claude-3-haiku-20240307"
    TIMEOUT_SECONDS = 30

    def __init__(self, api_key: Optional[str] = None):
        """Initialize LLM batch analyzer.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.client = None

        if ANTHROPIC_AVAILABLE and self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
            except Exception:
                # If client init fails, analyzer will be disabled
                pass

    def is_available(self) -> bool:
        """Check if LLM analyzer is available.

        Returns:
            True if Anthropic SDK installed and API key configured
        """
        return self.client is not None

    def analyze_batch(self, candidates: List[CleanupCandidate]) -> List[CleanupCandidate]:
        """Analyze candidates in batches.

        Filters to MEDIUM confidence (40-70%), batches into groups of 10-15,
        and boosts confidence based on Haiku responses.

        Args:
            candidates: List of all candidates

        Returns:
            List of candidates with adjusted confidence (boosted if YES)
        """
        if not self.is_available():
            # LLM not available, return originals unchanged
            return candidates

        # Filter uncertain candidates (40-70%)
        uncertain = [c for c in candidates if 0.4 <= c.confidence < 0.7]
        certain = [c for c in candidates if c.confidence < 0.4 or c.confidence >= 0.7]

        if not uncertain:
            return candidates  # No uncertain candidates

        # Process uncertain candidates in batches
        results = []
        for batch in self._create_batches(uncertain):
            batch_results = self._analyze_single_batch(batch)
            results.extend(batch_results)

        # Combine certain + analyzed uncertain
        return certain + results

    def _create_batches(self, candidates: List[CleanupCandidate]) -> List[List[CleanupCandidate]]:
        """Split candidates into batches of MAX_DOCS_PER_BATCH.

        Args:
            candidates: List of candidates to batch

        Returns:
            List of batches (each batch is a list of candidates)
        """
        batches = []
        for i in range(0, len(candidates), self.MAX_DOCS_PER_BATCH):
            batch = candidates[i:i + self.MAX_DOCS_PER_BATCH]
            batches.append(batch)
        return batches

    def _analyze_single_batch(self, candidates: List[CleanupCandidate]) -> List[CleanupCandidate]:
        """Analyze single batch of candidates using Haiku.

        Args:
            candidates: List of candidates (10-15 max)

        Returns:
            List of candidates with adjusted confidence
        """
        # Build prompt
        prompt = self._build_batch_prompt(candidates)

        try:
            # Call Haiku API
            response = self.client.messages.create(
                model=self.MODEL,
                max_tokens=1024,
                timeout=self.TIMEOUT_SECONDS,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Parse response
            response_text = response.content[0].text
            return self._parse_batch_response(response_text, candidates)

        except Exception as e:
            # API failure - return original candidates
            print(f"⚠️ LLM batch analysis failed: {e}")
            print(f"   Keeping original confidence for {len(candidates)} candidates")
            return candidates

    def _build_batch_prompt(self, candidates: List[CleanupCandidate]) -> str:
        """Build prompt for batch analysis.

        Format:
        For each doc below, output ONE line: YES, NO, or PARTIAL

        1. Doc: PRPs/feature-requests/auth-idea.md
           PRP: PRPs/executed/PRP-23-auth-system.md
           Question: Does PRP-23 fully implement auth-idea.md?

        Output format (one per line):
        1. YES
        2. NO

        Args:
            candidates: List of candidates to analyze

        Returns:
            Batch prompt string
        """
        lines = [
            "For each doc below, determine if the PRP fully implements/supersedes the doc.",
            "Output ONE line per doc: YES (fully implemented), NO (unrelated), or PARTIAL (partially implemented).\n"
        ]

        for i, candidate in enumerate(candidates, 1):
            lines.append(f"\n{i}. Doc: {candidate.path}")
            if hasattr(candidate, 'superseded_by') and candidate.superseded_by:
                lines.append(f"   PRP: {candidate.superseded_by}")
                prp_name = candidate.superseded_by.stem if hasattr(candidate.superseded_by, 'stem') else str(candidate.superseded_by)
                doc_name = candidate.path.name
                lines.append(f"   Question: Does {prp_name} fully implement {doc_name}?")
            else:
                lines.append(f"   No PRP specified")

        lines.append(f"\n\nOutput format (one per line):")
        for i in range(1, len(candidates) + 1):
            lines.append(f"{i}. [YES/NO/PARTIAL]")

        return "\n".join(lines)

    def _parse_batch_response(self, response: str, candidates: List[CleanupCandidate]) -> List[CleanupCandidate]:
        """Parse Haiku batch response.

        Expected format:
        1. YES
        2. NO
        3. PARTIAL

        Args:
            response: Haiku response text
            candidates: Original candidates

        Returns:
            Candidates with adjusted confidence
        """
        lines = response.strip().split('\n')
        results = []

        for i, candidate in enumerate(candidates):
            if i >= len(lines):
                # Not enough responses, keep original
                results.append(candidate)
                continue

            line = lines[i].strip().upper()
            verdict = None

            if 'YES' in line:
                verdict = 'YES'
            elif 'NO' in line:
                verdict = 'NO'
            elif 'PARTIAL' in line:
                verdict = 'PARTIAL'

            # Apply confidence boost
            if verdict == 'YES':
                # Boost to HIGH confidence (90%)
                candidate.confidence = 90
                # Update reason to include LLM verdict
                candidate.reason += f" (LLM verified: {verdict})"
            # NO or PARTIAL: keep original confidence (no boost)

            results.append(candidate)

        return results
```

**Step 2: Add Anthropic Dependency** (5 min)

Update `tools/pyproject.toml` to add anthropic package:

```bash
cd tools
uv add anthropic
```

This adds `anthropic>=0.25.0` to dependencies in pyproject.toml.

**Step 3: Export LLMBatchAnalyzer** (5 min)

Update `tools/ce/vacuum_strategies/__init__.py`:

```python
from .backup_files import BackupFileStrategy
from .commented_code import CommentedCodeStrategy
from .obsolete_docs import ObsoleteDocStrategy
from .orphan_tests import OrphanTestStrategy
from .temp_files import TempFileStrategy
from .unreferenced_code import UnreferencedCodeStrategy
from .llm_analyzer import LLMBatchAnalyzer  # NEW

__all__ = [
    "BackupFileStrategy",
    "CommentedCodeStrategy",
    "ObsoleteDocStrategy",
    "OrphanTestStrategy",
    "TempFileStrategy",
    "UnreferencedCodeStrategy",
    "LLMBatchAnalyzer",  # NEW
]
```

### Phase 2: Write Unit Tests (1 hour)

**Step 1: Create Test File** (10 min)

Create `tools/tests/test_llm_analyzer.py`:

```python
"""Tests for LLM batch analyzer."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from ce.vacuum_strategies.llm_analyzer import LLMBatchAnalyzer
from ce.vacuum_strategies.base import CleanupCandidate


@pytest.fixture
def mock_candidates(tmp_path):
    """Create mock candidates for testing."""
    candidates = []

    # HIGH confidence (≥75%) - should not be analyzed
    doc1 = tmp_path / "doc1.md"
    doc1.write_text("doc1 content")
    prp1 = tmp_path / "PRP-1.md"
    prp1.write_text("prp1 content")

    candidates.append(CleanupCandidate(
        path=doc1,
        reason="High confidence match",
        confidence=85,
        size_bytes=100,
        last_modified=None,
        git_history=None,
        superseded_by=prp1
    ))

    # MEDIUM confidence (40-70%) - should be analyzed
    for i in range(2, 22):  # 20 docs
        doc = tmp_path / f"doc{i}.md"
        doc.write_text(f"doc{i} content")
        prp = tmp_path / f"PRP-{i}.md"
        prp.write_text(f"prp{i} content")

        candidates.append(CleanupCandidate(
            path=doc,
            reason=f"Medium confidence match {i}",
            confidence=50 + (i % 20),  # 50-69% range
            size_bytes=100,
            last_modified=None,
            git_history=None,
            superseded_by=prp
        ))

    # LOW confidence (<40%) - should not be analyzed
    doc30 = tmp_path / "doc30.md"
    doc30.write_text("doc30 content")

    candidates.append(CleanupCandidate(
        path=doc30,
        reason="Low confidence match",
        confidence=30,
        size_bytes=100,
        last_modified=None,
        git_history=None,
        superseded_by=None
    ))

    return candidates


def test_batch_processing_efficiency(mock_candidates):
    """20 uncertain docs batched into 2 calls (not 20 individual calls)."""

    analyzer = LLMBatchAnalyzer(api_key="test-key")

    # Mock Anthropic client
    with patch.object(analyzer, 'client') as mock_client:
        mock_response = Mock()
        mock_response.content = [Mock(text="1. YES\n" * 15)]  # 15 YES responses
        mock_client.messages.create.return_value = mock_response

        # Analyze batch
        results = analyzer.analyze_batch(mock_candidates)

        # Verify API call count (2 batches: 15 + 5 docs)
        assert mock_client.messages.create.call_count == 2

        # Verify batch sizes
        calls = mock_client.messages.create.call_args_list
        # First batch: 15 docs
        assert "1. Doc:" in calls[0][1]['messages'][0]['content']
        assert "15. Doc:" in calls[0][1]['messages'][0]['content']
        # Second batch: 5 docs
        assert "1. Doc:" in calls[1][1]['messages'][0]['content']
        assert "5. Doc:" in calls[1][1]['messages'][0]['content']


def test_confidence_boost_logic():
    """YES → boost to 90%, NO/PARTIAL → keep original."""

    analyzer = LLMBatchAnalyzer(api_key="test-key")

    # Create test candidates
    candidates = []
    for i in range(3):
        candidate = CleanupCandidate(
            path=Path(f"doc{i}.md"),
            reason="Medium confidence",
            confidence=50,
            size_bytes=100,
            last_modified=None,
            git_history=None,
            superseded_by=Path(f"PRP-{i}.md")
        )
        candidates.append(candidate)

    # Mock Haiku responses
    with patch.object(analyzer, 'client') as mock_client:
        mock_response = Mock()
        mock_response.content = [Mock(text="1. YES\n2. NO\n3. PARTIAL")]
        mock_client.messages.create.return_value = mock_response

        results = analyzer.analyze_batch(candidates)

        # Verify confidence adjustments
        assert results[1].confidence == 90  # YES → boosted to 90%
        assert results[2].confidence == 50  # NO → kept at 50%
        assert results[3].confidence == 50  # PARTIAL → kept at 50%


def test_api_failure_graceful_degradation(mock_candidates):
    """API failure → keep original NLP confidence, continue vacuum."""

    analyzer = LLMBatchAnalyzer(api_key="test-key")

    # Mock API timeout
    with patch.object(analyzer, 'client') as mock_client:
        mock_client.messages.create.side_effect = Exception("API timeout")

        # Should not raise exception
        results = analyzer.analyze_batch(mock_candidates)

        # Verify original confidences preserved
        uncertain = [c for c in mock_candidates if 0.4 <= c.confidence < 0.7]
        result_uncertain = [c for c in results if 0.4 <= c.confidence < 0.7]

        assert len(result_uncertain) == len(uncertain)
        for orig, result in zip(uncertain, result_uncertain):
            assert result.confidence == orig.confidence


def test_no_anthropic_sdk_available():
    """Analyzer gracefully handles missing Anthropic SDK."""

    with patch('ce.vacuum_strategies.llm_analyzer.ANTHROPIC_AVAILABLE', False):
        analyzer = LLMBatchAnalyzer(api_key="test-key")

        assert not analyzer.is_available()

        # analyze_batch should return originals unchanged
        candidates = [
            CleanupCandidate(
                path=Path("doc.md"),
                reason="Test",
                confidence=50,
                size_bytes=100,
                last_modified=None,
                git_history=None
            )
        ]

        results = analyzer.analyze_batch(candidates)
        assert len(results) == 1
        assert results[0].confidence == 50  # Unchanged
```

**Step 2: Run Unit Tests** (5 min)

```bash
cd tools
uv run pytest tests/test_llm_analyzer.py -v
```

Expected output:

```
test_batch_processing_efficiency PASSED
test_confidence_boost_logic PASSED
test_api_failure_graceful_degradation PASSED
test_no_anthropic_sdk_available PASSED
```

## 4. Validation Gates

### Gate 1: Batch Processing Efficiency

**Command**:

```bash
cd tools
uv run pytest tests/test_llm_analyzer.py::test_batch_processing_efficiency -v
```

**Expected Output**:

```
test_batch_processing_efficiency PASSED
```

**Validates**: AC1 - 20 uncertain docs batched into 2 calls (not 20 individual calls)

---

### Gate 2: Confidence Boost Logic

**Command**:

```bash
cd tools
uv run pytest tests/test_llm_analyzer.py::test_confidence_boost_logic -v
```

**Expected Output**:

```
test_confidence_boost_logic PASSED
```

**Validates**: AC2 - YES → 90%, NO/PARTIAL → keep original

---

### Gate 3: Graceful Degradation on API Failure

**Command**:

```bash
cd tools
uv run pytest tests/test_llm_analyzer.py::test_api_failure_graceful_degradation -v
```

**Expected Output**:

```
test_api_failure_graceful_degradation PASSED
```

**Validates**: AC3 - API failure → keep original NLP confidence, continue vacuum

---

### Gate 4: All LLM Analyzer Tests Pass

**Command**:

```bash
cd tools
uv run pytest tests/test_llm_analyzer.py -v
```

**Expected Output**:

```
test_batch_processing_efficiency PASSED
test_confidence_boost_logic PASSED
test_api_failure_graceful_degradation PASSED
test_no_anthropic_sdk_available PASSED

4 passed
```

**Validates**: All test cases pass

## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
cd tools
uv run pytest tests/test_llm_analyzer.py -v
```

### Test Cases

**Test 1: Batch Processing Efficiency** (`test_batch_processing_efficiency`)

- Input: 20 uncertain docs (40-70% confidence) + 2 certain docs (HIGH/LOW)
- Expected: 2 API calls (batches of 15 + 5), not 20 individual calls
- Validates: Batching reduces API calls by 90%

**Test 2: Confidence Boost Logic** (`test_confidence_boost_logic`)

- Input: 3 candidates with 50% confidence
- Mock responses: "1. YES\n2. NO\n3. PARTIAL"
- Expected:
  - Candidate 1: 90% (boosted from YES)
  - Candidate 2: 50% (kept from NO)
  - Candidate 3: 50% (kept from PARTIAL)
- Validates: Confidence boost logic works correctly

**Test 3: API Failure Graceful Degradation** (`test_api_failure_graceful_degradation`)

- Input: 20 uncertain docs
- Mock: API timeout exception
- Expected: All candidates keep original confidence, no exceptions raised
- Validates: Vacuum continues on API failure

**Test 4: No Anthropic SDK Available** (`test_no_anthropic_sdk_available`)

- Mock: ANTHROPIC_AVAILABLE = False
- Expected: analyzer.is_available() returns False, analyze_batch returns originals unchanged
- Validates: Graceful handling of missing SDK

### Test Coverage Target

- 100% coverage of LLMBatchAnalyzer class
- All error paths tested (API failure, malformed response, missing SDK)
- Integration point tested (filtering MEDIUM confidence)

## 6. Rollout Plan

### Phase 1: Development (2 hours)

**Tasks**:

1. Implement Phase 1: Create LLMBatchAnalyzer Class (1 hour)
2. Implement Phase 2: Write Unit Tests (1 hour)

**Validation**: All 4 validation gates pass

### Phase 2: Review (15 min)

**Tasks**:

1. Code review for KISS principle adherence
2. Verify error handling (graceful degradation on API failures)
3. Check batch size limits (15 docs max per batch)

**Approval**: Self-review or peer review

### Phase 3: Integration (15 min)

**Tasks**:

1. Install anthropic package: `cd tools && uv add anthropic`
2. Verify LLMBatchAnalyzer exports in `__init__.py`
3. Test import: `from ce.vacuum_strategies import LLMBatchAnalyzer`

**Success Criteria**:

- All tests pass
- No hard dependency on Anthropic API (graceful degradation)
- Batch analyzer is OPTIONAL enhancement (vacuum works without it)

---

## Research Findings

### Codebase Analysis

**Existing Vacuum Strategy Pattern**:

- Base class: `BaseStrategy` from `tools/ce/vacuum_strategies/base.py`
- Candidate dataclass: `CleanupCandidate` with fields (path, reason, confidence, size_bytes, last_modified, git_history)
- Strategy methods: `find_candidates() -> List[CleanupCandidate]`

**PRP Lifecycle Docs Strategy** (from PRP-46.2.1):

- Generates candidates with `superseded_by: Path` field (path to executed PRP)
- Confidence tiers: HIGH (≥75%), MEDIUM (40-70%), LOW (<40%)
- Detection types: INITIAL→PRP, Temporary→PRP, Superseded

**Integration Point**:

```python
# After NLP detection (PRP-46.2.1)
candidates = prp_lifecycle_strategy.scan(project_root)

# NEW: LLM batch analysis for MEDIUM confidence
if ANTHROPIC_API_KEY:
    llm_analyzer = LLMBatchAnalyzer()
    candidates = llm_analyzer.analyze_batch(candidates)
```

### Anthropic API Patterns

**Batch Processing Pattern**:

```python
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

response = client.messages.create(
    model="claude-3-haiku-20240307",
    max_tokens=1024,
    timeout=30,
    messages=[
        {"role": "user", "content": batch_prompt}
    ]
)

response_text = response.content[0].text
```

**Error Handling**:

- API timeout: `anthropic.APITimeoutError`
- Rate limit: `anthropic.RateLimitError`
- Auth error: `anthropic.AuthenticationError`
- Generic: `Exception` catch-all for graceful degradation

**Cost Calculation**:

- Haiku pricing: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- Batch request: ~10K input tokens, ~100 output tokens = $0.0025 + $0.000125 ≈ $0.003
- With batching (15 docs): ~$0.001 per batch (3x cost reduction)

### Documentation Sources

**Anthropic Claude API**:

- Messages API: <https://docs.anthropic.com/claude/reference/messages>
- Model: claude-3-haiku-20240307
- Context limit: 200K tokens
- Timeout: Default 30s (configurable)

**Anthropic Python SDK**:

- Package: `anthropic`
- Version: ≥0.25.0
- Install: `uv add anthropic`
- Docs: <https://github.com/anthropics/anthropic-sdk-python>

**CE Vacuum Base Classes**:

- `tools/ce/vacuum_strategies/base.py` - BaseStrategy, CleanupCandidate
- `tools/ce/vacuum_strategies/__init__.py` - Strategy exports
