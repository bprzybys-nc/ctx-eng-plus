---
prp_id: 46.2.2
feature_name: Batch Optimization
status: pending
created: 2025-11-16
updated: 2025-11-16
complexity: low
estimated_hours: 2
dependencies: [46.2.1]
stage: 2
execution_order: 3
merge_order: 3
batch_id: 46
---

# PRP-46.2.2: Batch Optimization

## 1. Overview

**Objective**: Process multiple uncertain candidates (40-70% confidence) in a single LLM call to reduce API costs and latency.

**Problem**: Individual LLM calls for 10-20 uncertain docs results in:
- High API costs (10-20 calls × $0.001 = $0.01-0.02 per vacuum run)
- Poor latency (10-20 × 2s = 20-40s total)
- Sequential bottleneck (no parallelization benefit)

**Solution**: Batch all uncertain candidates into one LLM call with structured prompt format.

**Scope**:
- Batch mode for LLM analyzer (collects 40-70% confidence docs)
- Batch prompt design (multiple doc comparisons in single call)
- Batch response parsing (extract per-doc decisions)
- Fallback to individual calls if batch fails

**Out of Scope**:
- Batch mode for high-confidence docs (no LLM needed)
- Parallel batch processing (single batch sufficient for <20 docs)

## 2. Technical Design

### Architecture

```
VacuumCommand
    ↓
LLMAnalyzerStrategy
    ↓
├─ analyze_batch(candidates: List[DocCandidate]) → Dict[str, Decision]
│   ├─ Build batch prompt (all docs in one message)
│   ├─ Call LLM once
│   ├─ Parse structured response
│   └─ Return {doc_id: Decision, ...}
│
└─ analyze_single(candidate: DocCandidate) → Decision (fallback)
```

### Batch Prompt Format

**Design**: Numbered list with structured response format

```
You are analyzing documentation supersession candidates in a Context Engineering project.

For each pair below, determine if doc A supersedes doc B:

---
[1] A: PRPs/executed/PRP-42-automated-init.md (2025-11-15, 450 lines)
    Title: Automated CE Framework Initialization
    Keywords: init_project, mcp tool, automated setup

    B: examples/INITIALIZATION.md (2025-11-04, 800 lines)
    Title: Manual CE Framework Setup Guide
    Keywords: manual initialization, 5-phase workflow

    Confidence: 55% (newer, smaller, similar topic)

---
[2] A: .serena/memories/tool-usage-syntropy.md (2025-11-10)
    Title: Syntropy MCP Tool Patterns
    Keywords: mcp tools, serena, context7

    B: examples/TOOL-USAGE-GUIDE.md (2025-11-09)
    Title: Comprehensive Tool Selection Guide
    Keywords: decision tree, tool patterns

    Confidence: 42% (similar topic, B more comprehensive)

---
[... 8 more pairs ...]

RESPONSE FORMAT (one line per pair):
[N] DECISION | REASONING

DECISION: YES | NO | PARTIAL(keep_sections)
REASONING: 1-2 sentence explanation

Example:
[1] YES | A provides automated approach, B's manual steps obsolete
[2] NO | B is comprehensive guide, A is narrow pattern collection
[3] PARTIAL(Troubleshooting,Advanced Patterns) | A covers basics, B's advanced sections still unique
```

### Batch Response Parsing

**Pattern**: Line-based extraction with fallback

```python
def parse_batch_response(response: str, candidates: List[DocCandidate]) -> Dict[str, Decision]:
    """Parse LLM batch response into per-doc decisions.

    Format: "[N] DECISION | REASONING"

    Returns:
        {doc_id: Decision(action, confidence, reasoning)}
    """
    results = {}
    lines = response.strip().split('\n')

    for line in lines:
        # Match: "[1] YES | A supersedes B completely"
        match = re.match(r'\[(\d+)\]\s+(YES|NO|PARTIAL\([^)]+\))\s+\|\s+(.+)', line)
        if not match:
            continue

        idx = int(match.group(1)) - 1  # 1-indexed → 0-indexed
        decision_str = match.group(2)
        reasoning = match.group(3)

        if idx >= len(candidates):
            continue

        candidate = candidates[idx]

        # Parse decision
        if decision_str == 'YES':
            action = 'DELETE'
            confidence = 0.9
        elif decision_str == 'NO':
            action = 'KEEP'
            confidence = 0.9
        elif decision_str.startswith('PARTIAL'):
            action = 'KEEP'
            confidence = 0.7
            # Extract sections from PARTIAL(Troubleshooting,Advanced)
            reasoning = f"{reasoning} | Keep sections: {decision_str}"

        results[candidate.superseded.path] = Decision(
            action=action,
            confidence=confidence,
            reasoning=reasoning,
            superseded_by=candidate.superseding.path if action == 'DELETE' else None
        )

    return results
```

### Fallback Strategy

**Trigger**: Batch parsing fails (malformed response, missing entries)

```python
def analyze_with_fallback(self, candidates: List[DocCandidate]) -> Dict[str, Decision]:
    """Batch analysis with individual fallback."""

    # Try batch first
    try:
        results = self.analyze_batch(candidates)

        # Verify completeness (all candidates have results)
        if len(results) == len(candidates):
            return results

        # Partial success: Fill gaps with individual calls
        missing = [c for c in candidates if c.superseded.path not in results]
        for candidate in missing:
            results[candidate.superseded.path] = self.analyze_single(candidate)

        return results

    except Exception as e:
        # Batch failed: Fall back to individual calls
        logger.warning(f"Batch analysis failed: {e}, falling back to individual calls")
        return {
            c.superseded.path: self.analyze_single(c)
            for c in candidates
        }
```

### Integration with VacuumCommand

**Modification**: Group candidates by confidence tier

```python
# In VacuumCommand.execute()

# Tier 1: High confidence (>70%) - Auto-decide, no LLM
high_confidence = [c for c in candidates if c.confidence > 0.7]
for candidate in high_confidence:
    results[candidate.superseded.path] = Decision(
        action='DELETE',
        confidence=candidate.confidence,
        reasoning="High-confidence automated decision",
        superseded_by=candidate.superseding.path
    )

# Tier 2: Uncertain (40-70%) - Batch LLM analysis
uncertain = [c for c in candidates if 0.4 <= c.confidence <= 0.7]
if uncertain:
    llm_results = llm_strategy.analyze_with_fallback(uncertain)
    results.update(llm_results)

# Tier 3: Low confidence (<40%) - Keep (too uncertain to delete)
low_confidence = [c for c in candidates if c.confidence < 0.4]
for candidate in low_confidence:
    results[candidate.superseded.path] = Decision(
        action='KEEP',
        confidence=candidate.confidence,
        reasoning="Confidence too low for deletion"
    )
```

## 3. Implementation Steps

### Step 1: Add Batch Mode to LLMAnalyzerStrategy

**File**: `tools/ce/vacuum_strategies/llm_analyzer.py`

**Changes**:
1. Add `analyze_batch()` method (builds batch prompt, calls LLM)
2. Add `parse_batch_response()` helper
3. Add `analyze_with_fallback()` orchestrator
4. Keep existing `analyze_single()` for fallback

**Estimated Time**: 45 minutes

### Step 2: Design Batch Prompt Template

**File**: `tools/ce/vacuum_strategies/llm_analyzer.py`

**Changes**:
1. Create `BATCH_PROMPT_TEMPLATE` constant
2. Format numbered list with doc metadata
3. Include response format instructions
4. Add examples for YES/NO/PARTIAL

**Estimated Time**: 30 minutes

### Step 3: Implement Response Parsing

**File**: `tools/ce/vacuum_strategies/llm_analyzer.py`

**Changes**:
1. Regex pattern for `[N] DECISION | REASONING`
2. Extract decision type (YES/NO/PARTIAL)
3. Parse PARTIAL sections if present
4. Handle malformed lines gracefully

**Estimated Time**: 30 minutes

### Step 4: Add Fallback Logic

**File**: `tools/ce/vacuum_strategies/llm_analyzer.py`

**Changes**:
1. Try batch mode first
2. Check completeness (all candidates covered)
3. Fill gaps with individual calls if needed
4. Full fallback on batch failure

**Estimated Time**: 15 minutes

## 4. Testing Strategy

### Unit Tests

**File**: `tests/test_vacuum_llm_batch.py`

```python
def test_batch_analysis_10_docs():
    """Batch mode analyzes 10 uncertain docs in single call."""
    strategy = LLMAnalyzerStrategy()
    candidates = [create_mock_candidate(confidence=0.5) for _ in range(10)]

    results = strategy.analyze_batch(candidates)

    assert len(results) == 10
    assert all(isinstance(r, Decision) for r in results.values())

def test_parse_batch_response_yes():
    """Parse YES decision from batch response."""
    response = "[1] YES | A supersedes B completely"
    candidates = [create_mock_candidate()]

    results = parse_batch_response(response, candidates)

    assert results[candidates[0].superseded.path].action == 'DELETE'
    assert results[candidates[0].superseded.path].confidence == 0.9

def test_parse_batch_response_partial():
    """Parse PARTIAL decision with sections."""
    response = "[1] PARTIAL(Troubleshooting,Advanced) | Keep advanced sections"
    candidates = [create_mock_candidate()]

    results = parse_batch_response(response, candidates)

    assert results[candidates[0].superseded.path].action == 'KEEP'
    assert 'Keep sections' in results[candidates[0].superseded.path].reasoning

def test_fallback_on_incomplete_batch():
    """Falls back to individual calls if batch missing entries."""
    strategy = LLMAnalyzerStrategy()
    candidates = [create_mock_candidate() for _ in range(10)]

    # Mock batch returns only 8/10 results
    with patch.object(strategy, 'analyze_batch', return_value={...8 results...}):
        results = strategy.analyze_with_fallback(candidates)

    assert len(results) == 10  # Filled gaps with individual calls

def test_fallback_on_batch_exception():
    """Falls back to individual calls if batch fails."""
    strategy = LLMAnalyzerStrategy()
    candidates = [create_mock_candidate() for _ in range(5)]

    with patch.object(strategy, 'analyze_batch', side_effect=ValueError("Batch failed")):
        results = strategy.analyze_with_fallback(candidates)

    assert len(results) == 5  # All via individual fallback
```

### Integration Tests

**File**: `tests/test_vacuum_integration.py`

```python
def test_batch_reduces_api_calls():
    """Batch mode reduces API calls by 90% for 10 uncertain docs."""
    strategy = LLMAnalyzerStrategy()
    candidates = [create_mock_candidate(confidence=0.5) for _ in range(10)]

    with patch('ce.vacuum_strategies.llm_analyzer.call_llm') as mock_llm:
        strategy.analyze_with_fallback(candidates)

    # Batch mode: 1 call instead of 10
    assert mock_llm.call_count == 1

def test_batch_latency_under_5_seconds():
    """Batch analysis completes in <5 seconds for 10 docs."""
    strategy = LLMAnalyzerStrategy()
    candidates = [create_mock_candidate(confidence=0.5) for _ in range(10)]

    start = time.time()
    results = strategy.analyze_with_fallback(candidates)
    duration = time.time() - start

    assert duration < 5.0
    assert len(results) == 10
```

### Performance Benchmarking

**Approach**: Compare batch vs individual mode

```python
def benchmark_batch_vs_individual():
    """Measure API calls and latency for batch vs individual mode."""
    candidates = [create_mock_candidate(confidence=0.5) for _ in range(10)]

    # Individual mode
    start = time.time()
    individual_results = [analyze_single(c) for c in candidates]
    individual_time = time.time() - start
    individual_calls = 10

    # Batch mode
    start = time.time()
    batch_results = analyze_batch(candidates)
    batch_time = time.time() - start
    batch_calls = 1

    print(f"Individual: {individual_calls} calls, {individual_time:.2f}s")
    print(f"Batch: {batch_calls} calls, {batch_time:.2f}s")
    print(f"Reduction: {(1 - batch_calls/individual_calls)*100:.0f}% calls, {(1 - batch_time/individual_time)*100:.0f}% latency")

    # Expected: 90% reduction in calls, 80%+ reduction in latency
```

## 5. Validation Gates

**Gate 1: Unit Tests Pass**
- All 5 unit tests pass
- Batch parsing handles YES/NO/PARTIAL correctly
- Fallback logic covers incomplete/failed batches

**Command**: `cd tools && uv run pytest tests/test_vacuum_llm_batch.py -v`

**Gate 2: Integration Tests Pass**
- Batch mode reduces API calls by 90%+ (1 call vs 10)
- Latency <5 seconds for 10 docs
- Results match individual mode (same decisions)

**Command**: `cd tools && uv run pytest tests/test_vacuum_integration.py -k batch -v`

**Gate 3: Performance Benchmark**
- Run benchmark script on real LLM calls
- Verify 90% call reduction
- Verify 80%+ latency reduction

**Command**: `cd tools && uv run python tests/benchmark_batch.py`

**Gate 4: Manual Validation**
- Run vacuum on test repo with 10-15 uncertain candidates
- Verify batch analysis produces correct decisions
- Check fallback triggers correctly on malformed response

**Command**: `cd tools && uv run ce vacuum --dry-run`

## 6. Rollout Plan

### Phase 1: Implementation (1 hour)
1. Add batch methods to LLMAnalyzerStrategy (45 min)
2. Implement response parsing (30 min)
3. Add fallback logic (15 min)

### Phase 2: Testing (45 minutes)
1. Write unit tests (30 min)
2. Write integration tests (15 min)

### Phase 3: Validation (15 minutes)
1. Run test suite (5 min)
2. Manual testing with dry-run (5 min)
3. Performance benchmark (5 min)

### Phase 4: Documentation (15 minutes)
1. Update LLM analyzer docstrings
2. Add batch mode example to vacuum docs
3. Document fallback behavior

**Total Estimated Time**: 2 hours

### Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| LLM returns malformed batch response | Batch fails, fallback to individual | Robust parsing with fallback logic |
| Batch response missing some entries | Incomplete results | Detect gaps, fill with individual calls |
| Batch prompt too long for LLM context | API error | Limit batch size to 20 docs max |
| Batch decisions differ from individual | Inconsistent results | Validate batch vs individual on test set |

### Success Metrics

- API call reduction: ≥90% (10 calls → 1 call)
- Latency reduction: ≥80% (20s → <5s)
- Decision accuracy: ≥95% match with individual mode
- Fallback coverage: 100% (all failure modes handled)

---

**Dependencies**: PRP-46.2.1 (LLM Analyzer Strategy)

**Next Phase**: PRP-46.3.1 (Integration Testing)
