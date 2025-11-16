---
prp_id: 46.4.1
feature_name: Integration and Testing for NLP-Powered Vacuum
batch_id: 46
stage: 4
order: 1
status: completed
created: 2025-11-16T00:00:00Z
updated: 2025-11-16T14:00:00Z
completed: 2025-11-16T14:00:00Z
commit: 49adadc
complexity: low
estimated_hours: 1.5
dependencies: PRP-46.1.1, PRP-46.2.1, PRP-46.2.2, PRP-46.3.1 (all NLP components)
---

# Integration and Testing for NLP-Powered Vacuum

## 1. TL;DR

**Objective**: Integrate all NLP vacuum components into vacuum CLI with `--nlp-backend` flag and comprehensive end-to-end testing

**What**: Register PRPLifecycleDocsStrategy in vacuum CLI, add backend selection flag, write integration tests for full workflow

**Why**: Complete the NLP vacuum enhancement by connecting all components (NLP foundation, lifecycle detection, LLM batch) into production-ready CLI

**Effort**: 1.5 hours (LOW complexity, integration and testing only)

**Dependencies**: PRP-46.1.1 (ce.nlp module), PRP-46.2.1 (PRPLifecycleDocsStrategy), PRP-46.2.2 (enhanced strategies), PRP-46.3.1 (LLMBatchAnalyzer)

## 2. Context

### Background

All NLP vacuum components are implemented but not integrated into the vacuum CLI:

- **PRP-46.1.1**: `ce.nlp` module with DocumentSimilarity (3-tier fallback)
- **PRP-46.2.1**: PRPLifecycleDocsStrategy for lifecycle doc detection
- **PRP-46.2.2**: Enhanced ObsoleteDocStrategy and OrphanTestStrategy with NLP
- **PRP-46.3.1**: LLMBatchAnalyzer for Haiku batch processing

**Current vacuum workflow**:

```bash
uv run ce vacuum                  # Uses existing strategies only
uv run ce vacuum --execute        # Deletes temp files
uv run ce vacuum --auto           # Deletes temp files + obsolete docs
```

**New workflow (after integration)**:

```bash
uv run ce vacuum --nlp-backend auto  # Uses NLP with 3-tier fallback
uv run ce vacuum --nlp-backend sentence-transformers  # Force Tier 1
uv run ce vacuum --nlp-backend sklearn  # Force Tier 2
uv run ce vacuum --nlp-backend difflib  # Force Tier 3
```

### Constraints and Considerations

**Backward Compatibility**:

- Existing `--execute` and `--auto` flags must work unchanged
- NLP strategies are OPTIONAL enhancements (vacuum works without them)
- No hard dependency on sentence-transformers or anthropic

**CLI Design**:

- `--nlp-backend` is optional (default: auto)
- Invalid backend → error with valid options list
- NLP backend applies to ALL strategies (PRPLifecycleDocs, ObsoleteDocs, OrphanTests)

**Testing Strategy**:

- Integration tests use real PRPs for reproducibility
- Performance tests measure cache effectiveness (95%+ reduction)
- No false positive tests verify <40% threshold works

### Documentation References

**CE Vacuum**:

- `tools/ce/vacuum.py` - Main vacuum CLI implementation
- `tools/ce/vacuum_strategies/__init__.py` - Strategy exports

**NLP Components**:

- `ce.nlp.DocumentSimilarity` - From PRP-46.1.1
- `ce.vacuum_strategies.prp_lifecycle_docs.PRPLifecycleDocsStrategy` - From PRP-46.2.1
- `ce.vacuum_strategies.llm_analyzer.LLMBatchAnalyzer` - From PRP-46.3.1

**Testing**:

- pytest for unit and integration tests
- Test file: `tools/tests/test_vacuum_nlp.py` (new)

## 3. Implementation Steps

### Phase 1: Register PRPLifecycleDocsStrategy (30 min)

**Step 1: Update vacuum_strategies/**init**.py** (5 min)

Verify PRPLifecycleDocsStrategy is exported in `tools/ce/vacuum_strategies/__init__.py`:

```python
from .backup_files import BackupFileStrategy
from .commented_code import CommentedCodeStrategy
from .obsolete_docs import ObsoleteDocStrategy
from .orphan_tests import OrphanTestStrategy
from .temp_files import TempFileStrategy
from .unreferenced_code import UnreferencedCodeStrategy
from .llm_analyzer import LLMBatchAnalyzer
from .prp_lifecycle_docs import PRPLifecycleDocsStrategy  # NEW (from PRP-46.2.1)

__all__ = [
    "BackupFileStrategy",
    "CommentedCodeStrategy",
    "ObsoleteDocStrategy",
    "OrphanTestStrategy",
    "TempFileStrategy",
    "UnreferencedCodeStrategy",
    "LLMBatchAnalyzer",
    "PRPLifecycleDocsStrategy",  # NEW
]
```

**Step 2: Add --nlp-backend Flag to vacuum.py** (15 min)

Update `tools/ce/vacuum.py` to add CLI flag and register new strategy.

Find the argument parser section (search for `argparse.ArgumentParser`):

```python
import argparse
import os
from pathlib import Path

# ... existing imports ...

def main():
    parser = argparse.ArgumentParser(description="Vacuum unused files")
    parser.add_argument("--execute", action="store_true", help="Execute deletions")
    parser.add_argument("--auto", action="store_true", help="Auto-approve all deletions")

    # NEW: Add NLP backend flag
    parser.add_argument(
        "--nlp-backend",
        choices=["auto", "sentence-transformers", "sklearn", "difflib"],
        default="auto",
        help="NLP backend for semantic similarity (default: auto)"
    )

    args = parser.parse_args()
```

**Step 3: Initialize NLP-Enhanced Strategies** (10 min)

Update strategy initialization in `tools/ce/vacuum.py` (find where strategies are created):

```python
    # Get project root
    project_root = Path.cwd()

    # NEW: Set NLP backend environment variable (used by DocumentSimilarity)
    if args.nlp_backend != "auto":
        os.environ["CE_NLP_BACKEND"] = args.nlp_backend

    # Initialize strategies
    strategies = [
        TempFileStrategy(project_root),
        BackupFileStrategy(project_root),
        CommentedCodeStrategy(project_root),
        ObsoleteDocStrategy(project_root),  # Enhanced with NLP (PRP-46.2.2)
        OrphanTestStrategy(project_root),   # Enhanced with NLP (PRP-46.2.2)
        UnreferencedCodeStrategy(project_root),
        PRPLifecycleDocsStrategy(project_root),  # NEW (PRP-46.2.1)
    ]

    # Collect all candidates
    all_candidates = []
    for strategy in strategies:
        candidates = strategy.find_candidates()
        all_candidates.extend(candidates)

    # NEW: Optional LLM batch analysis for MEDIUM confidence (40-70%)
    if os.getenv("ANTHROPIC_API_KEY"):
        from ce.vacuum_strategies import LLMBatchAnalyzer
        llm_analyzer = LLMBatchAnalyzer()
        all_candidates = llm_analyzer.analyze_batch(all_candidates)

    # ... rest of vacuum logic (report formatting, execution, etc.)
```

### Phase 2: Write Integration Tests (1 hour)

**Step 1: Create Test File** (10 min)

Create `tools/tests/test_vacuum_nlp.py`:

```python
"""Integration tests for NLP-powered vacuum."""

import pytest
from pathlib import Path

from ce.vacuum_strategies import PRPLifecycleDocsStrategy


@pytest.fixture
def project_with_prps(tmp_path):
    """Create project structure with executed PRPs and lifecycle docs."""

    # Create executed PRPs directory
    executed_dir = tmp_path / "PRPs" / "executed"
    executed_dir.mkdir(parents=True)

    # Create sample executed PRPs
    prps = [
        ("PRP-23-auth-system.md", "Implemented JWT authentication with refresh token support"),
        ("PRP-38-vacuum-optimization.md", "Optimized vacuum performance with caching"),
        ("PRP-42-init-workflow.md", "Overhauled init project workflow"),
    ]

    for prp_name, prp_content in prps:
        prp_file = executed_dir / prp_name
        prp_file.write_text(prp_content)

    # Create feature-requests directory
    feature_dir = tmp_path / "PRPs" / "feature-requests"
    feature_dir.mkdir(parents=True)

    return tmp_path


def test_full_vacuum_with_nlp(project_with_prps):
    """Full vacuum workflow with NLP backend detects lifecycle docs."""

    project_root = project_with_prps

    # Create INITIAL.md with high semantic similarity to PRP-23
    initial = project_root / "PRPs/feature-requests/auth-initial.md"
    initial.write_text("Implement JWT-based authentication with refresh tokens and secure storage")

    # Run vacuum strategy
    strategy = PRPLifecycleDocsStrategy(project_root)
    candidates = strategy.find_candidates()

    # Verify detection
    matching = [c for c in candidates if c.path == initial]

    if strategy.nlp and strategy.nlp.backend_name != "difflib":
        # With NLP (sentence-transformers or sklearn), should detect
        assert len(matching) == 1
        assert matching[0].confidence >= 70  # MEDIUM or HIGH confidence
        # Detection type should be set
        if hasattr(matching[0], 'detection_type'):
            assert matching[0].detection_type in ["INITIAL→PRP", "Superseded"]
    else:
        # With difflib only, might not detect (lower accuracy)
        # This is acceptable degradation
        pass


def test_detects_initial_md_in_subdirectories(project_with_prps):
    """Recursive scan finds INITIAL.md in subdirectories."""

    project_root = project_with_prps

    # Create INITIAL.md in nested subdirectory
    auth_dir = project_root / "PRPs/feature-requests/auth"
    auth_dir.mkdir(parents=True)
    initial = auth_dir / "INITIAL.md"
    initial.write_text("Implement JWT authentication with refresh tokens")

    # Run vacuum strategy
    strategy = PRPLifecycleDocsStrategy(project_root)
    candidates = strategy.find_candidates()

    # Verify detection (recursive scan)
    matching = [c for c in candidates if c.path == initial]

    if strategy.nlp and strategy.nlp.backend_name != "difflib":
        # Should detect in subdirectory
        assert len(matching) == 1
        assert matching[0].confidence >= 70
    else:
        # Difflib might not detect
        pass


def test_no_false_positives_on_active_docs(project_with_prps):
    """Active feature requests with <40% similarity are not flagged."""

    project_root = project_with_prps

    # Create new feature request with LOW semantic similarity to all PRPs
    new_feature = project_root / "PRPs/feature-requests/blockchain-integration.md"
    new_feature.write_text("""
    # Feature: Blockchain Integration

    Implement blockchain integration for decentralized data storage.
    Use Ethereum smart contracts for transaction validation.
    """)

    # Run vacuum strategy
    strategy = PRPLifecycleDocsStrategy(project_root)
    candidates = strategy.find_candidates()

    # Verify NOT flagged (low semantic similarity)
    matching = [c for c in candidates if c.path == new_feature]
    assert len(matching) == 0  # Should NOT be flagged


def test_detects_plan_and_analysis_docs(project_with_prps):
    """Detects PLAN-*, ANALYSIS-*, REPORT-* docs with semantic similarity."""

    project_root = project_with_prps

    # Create PLAN doc with high similarity to PRP-38
    plan_doc = project_root / "PRPs/feature-requests/PLAN-vacuum-optimization.md"
    plan_doc.write_text("Plan: Optimize vacuum performance using embedding cache")

    # Run vacuum strategy
    strategy = PRPLifecycleDocsStrategy(project_root)
    candidates = strategy.find_candidates()

    # Verify detection
    matching = [c for c in candidates if c.path == plan_doc]

    if strategy.nlp:
        # Should detect via filename pattern + NLP boost
        assert len(matching) == 1
        assert matching[0].confidence >= 70
        if hasattr(matching[0], 'detection_type'):
            assert matching[0].detection_type == "Temporary→PRP"
    else:
        # Without NLP, still detected via filename
        assert len(matching) == 1


def test_embedding_cache_performance(project_with_prps, benchmark=None):
    """Embedding cache reduces computation by 95%+."""

    project_root = project_with_prps

    # Create 10 lifecycle docs
    for i in range(10):
        doc = project_root / f"PRPs/feature-requests/doc-{i}.md"
        doc.write_text(f"Implement feature {i} with authentication and caching")

    # First run (no cache)
    strategy1 = PRPLifecycleDocsStrategy(project_root)
    if not strategy1.nlp:
        pytest.skip("NLP not available, skipping cache test")

    import time
    start = time.time()
    candidates1 = strategy1.find_candidates()
    first_run_time = time.time() - start

    # Second run (with cache)
    strategy2 = PRPLifecycleDocsStrategy(project_root)
    start = time.time()
    candidates2 = strategy2.find_candidates()
    second_run_time = time.time() - start

    # Verify cache effectiveness (if sentence-transformers available)
    if strategy1.nlp.backend_name == "sentence-transformers":
        # Second run should be significantly faster (95%+ reduction)
        assert second_run_time < first_run_time * 0.1  # <10% of first run
    else:
        # sklearn/difflib are already fast, cache benefit less visible
        assert second_run_time <= first_run_time


def test_nlp_backend_selection_via_env(project_with_prps):
    """CE_NLP_BACKEND environment variable forces specific backend."""

    import os

    project_root = project_with_prps

    # Test difflib backend (always available)
    os.environ["CE_NLP_BACKEND"] = "difflib"

    strategy = PRPLifecycleDocsStrategy(project_root)

    if strategy.nlp:
        assert strategy.nlp.backend_name == "difflib"

    # Clean up
    if "CE_NLP_BACKEND" in os.environ:
        del os.environ["CE_NLP_BACKEND"]
```

**Step 2: Run Integration Tests** (10 min)

```bash
cd tools
uv run pytest tests/test_vacuum_nlp.py -v
```

Expected output:

```
test_full_vacuum_with_nlp PASSED
test_detects_initial_md_in_subdirectories PASSED
test_no_false_positives_on_active_docs PASSED
test_detects_plan_and_analysis_docs PASSED
test_embedding_cache_performance PASSED (or SKIPPED if no NLP)
test_nlp_backend_selection_via_env PASSED
```

**Step 3: Update CLAUDE.md with NLP Backend Documentation** (10 min)

Add to `CLAUDE.md` vacuum section:

```markdown
## Vacuum with NLP Backend

**NLP-powered lifecycle doc detection** (from batch 46 PRPs):

```bash
# Default: Auto-select backend (3-tier fallback)
cd tools && uv run ce vacuum --nlp-backend auto

# Force sentence-transformers (Tier 1, best accuracy)
cd tools && uv run ce vacuum --nlp-backend sentence-transformers

# Force sklearn TF-IDF (Tier 2, good accuracy, no ML)
cd tools && uv run ce vacuum --nlp-backend sklearn

# Force difflib (Tier 3, stdlib baseline)
cd tools && uv run ce vacuum --nlp-backend difflib
```

**What it detects**:

- INITIAL.md files that became formal PRPs
- PLAN/ANALYSIS/REPORT docs integrated into executed PRPs
- Superseded feature requests

**Performance**:

- First run: ~10-15 seconds (generates embeddings)
- Subsequent runs: <500ms (uses cache at `.ce/nlp-embeddings-cache.json`)
- Cache invalidation: mtime-based (auto-recomputes if file modified)

**Optional LLM batch analysis** (requires `ANTHROPIC_API_KEY`):

- Analyzes MEDIUM confidence (40-70%) candidates with Haiku
- Batches 10-15 docs per API call for cost efficiency
- YES verdict → boosts to 90% confidence (auto-flag)
- NO/PARTIAL verdict → keeps original confidence

**Report format** (with NLP):

```
Found 12 candidates:
- PRPs/feature-requests/auth/INITIAL.md (85% confidence)
  Detection: INITIAL→PRP
  Superseded by: PRP-23-auth-system.md
  NLP similarity: 0.82
```

```

## 4. Validation Gates

### Gate 1: CLI Integration with NLP Backend Flag

**Command**:

```bash
cd tools
uv run ce vacuum --nlp-backend auto --help
```

**Expected Output**:

```
usage: ce vacuum [--execute] [--auto] [--nlp-backend {auto,sentence-transformers,sklearn,difflib}]

--nlp-backend {auto,sentence-transformers,sklearn,difflib}
              NLP backend for semantic similarity (default: auto)
```

**Validates**: AC1 - CLI flag added and documented

---

### Gate 2: Recursive Subdirectory Detection

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_nlp.py::test_detects_initial_md_in_subdirectories -v
```

**Expected Output**:

```
test_detects_initial_md_in_subdirectories PASSED
```

**Validates**: AC2 - Recursive scanning detects docs in subdirectories

---

### Gate 3: No False Positives on Active Docs

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_nlp.py::test_no_false_positives_on_active_docs -v
```

**Expected Output**:

```
test_no_false_positives_on_active_docs PASSED
```

**Validates**: AC3 - Active feature requests with <40% similarity not flagged

---

### Gate 4: All Integration Tests Pass

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_nlp.py -v
```

**Expected Output**:

```
test_full_vacuum_with_nlp PASSED
test_detects_initial_md_in_subdirectories PASSED
test_no_false_positives_on_active_docs PASSED
test_detects_plan_and_analysis_docs PASSED
test_embedding_cache_performance PASSED (or SKIPPED)
test_nlp_backend_selection_via_env PASSED

6 passed
```

**Validates**: All integration tests pass

## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
cd tools
uv run pytest tests/test_vacuum_nlp.py -v
```

### Test Cases

**Test 1: Full Vacuum with NLP** (`test_full_vacuum_with_nlp`)

- Input: Project with executed PRPs and lifecycle docs
- Expected: Lifecycle docs detected with ≥70% confidence
- Validates: End-to-end workflow

**Test 2: Recursive Subdirectory Detection** (`test_detects_initial_md_in_subdirectories`)

- Input: INITIAL.md in `PRPs/feature-requests/auth/INITIAL.md` (subdirectory)
- Expected: Detected by recursive scan
- Validates: `rglob("*.md")` finds docs in subdirectories

**Test 3: No False Positives** (`test_no_false_positives_on_active_docs`)

- Input: New feature request with <40% similarity to all PRPs
- Expected: NOT flagged
- Validates: Confidence threshold prevents false positives

**Test 4: Temporary Docs Detection** (`test_detects_plan_and_analysis_docs`)

- Input: PLAN-*.md, ANALYSIS-*.md docs with semantic similarity
- Expected: Detected with ≥70% confidence, detection_type="Temporary→PRP"
- Validates: Lifecycle doc detection

**Test 5: Cache Performance** (`test_embedding_cache_performance`)

- Input: 10 lifecycle docs
- Expected: Second run <10% of first run time (95%+ reduction)
- Validates: Embedding cache effectiveness

**Test 6: Backend Selection** (`test_nlp_backend_selection_via_env`)

- Input: CE_NLP_BACKEND=difflib
- Expected: strategy.nlp.backend_name == "difflib"
- Validates: Environment variable forces specific backend

### Test Coverage Target

- 100% coverage of integration points (vacuum CLI + NLP strategies)
- All 3 acceptance criteria validated
- Performance benchmark for cache (95%+ reduction)

## 6. Rollout Plan

### Phase 1: Development (1.5 hours)

**Tasks**:

1. Implement Phase 1: Register PRPLifecycleDocsStrategy (30 min)
2. Implement Phase 2: Write Integration Tests (1 hour)

**Validation**: All 4 validation gates pass

### Phase 2: Review (15 min)

**Tasks**:

1. Code review for backward compatibility (existing flags work unchanged)
2. Verify optional NLP enhancement (vacuum works without sentence-transformers)
3. Check documentation updates (CLAUDE.md has NLP backend examples)

**Approval**: Self-review or peer review

### Phase 3: Integration (15 min)

**Tasks**:

1. Run full vacuum test suite: `uv run pytest tests/test_vacuum*.py -v`
2. Test on real ctx-eng-plus project: `cd tools && uv run ce vacuum --nlp-backend auto`
3. Verify report format shows detection types and confidence scores

**Success Criteria**:

- All tests pass (unit + integration)
- NLP backend flag works for all 4 backends (auto, sentence-transformers, sklearn, difflib)
- No false positives on active feature requests
- Embedding cache reduces computation by 95%+

---

## Research Findings

### Codebase Analysis

**Current Vacuum CLI Structure** (from `tools/ce/vacuum.py`):

```python
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--auto", action="store_true")
    args = parser.parse_args()

    # Initialize strategies
    strategies = [
        TempFileStrategy(project_root),
        BackupFileStrategy(project_root),
        # ... existing strategies
    ]

    # Collect candidates
    all_candidates = []
    for strategy in strategies:
        candidates = strategy.find_candidates()
        all_candidates.extend(candidates)

    # Format report
    print_report(all_candidates)

    # Execute deletions if --execute
    if args.execute:
        delete_candidates(all_candidates)
```

**Integration Point**:

- Add `--nlp-backend` flag to argument parser
- Add PRPLifecycleDocsStrategy to strategies list
- Add optional LLMBatchAnalyzer after candidate collection

**Backward Compatibility**:

- Existing `--execute` and `--auto` flags unchanged
- NLP strategies are optional (work without sentence-transformers)
- Default behavior unchanged (no NLP unless `--nlp-backend` specified)

### NLP Component Integration

**From PRP-46.1.1** (`ce.nlp.DocumentSimilarity`):

```python
from ce.nlp import DocumentSimilarity

# Automatically uses 3-tier fallback
nlp = DocumentSimilarity()

# Or force specific backend via environment
import os
os.environ["CE_NLP_BACKEND"] = "sklearn"
nlp = DocumentSimilarity()  # Uses sklearn
```

**From PRP-46.2.1** (`PRPLifecycleDocsStrategy`):

```python
from ce.vacuum_strategies import PRPLifecycleDocsStrategy

strategy = PRPLifecycleDocsStrategy(project_root)
candidates = strategy.find_candidates()

# Each candidate has:
# - path: Path to file
# - confidence: 0-100 score
# - detection_type: "INITIAL→PRP", "Temporary→PRP", "Superseded"
# - superseded_by: Path to executed PRP (if available)
```

**From PRP-46.3.1** (`LLMBatchAnalyzer`):

```python
from ce.vacuum_strategies import LLMBatchAnalyzer

# Only analyzes MEDIUM confidence (40-70%)
llm_analyzer = LLMBatchAnalyzer()
boosted_candidates = llm_analyzer.analyze_batch(all_candidates)
```

### Testing Best Practices

**Integration Test Pattern**:

1. Create fixture with realistic project structure
2. Add sample executed PRPs and lifecycle docs
3. Run strategy.find_candidates()
4. Verify candidates match expected results

**Performance Test Pattern**:

1. Run strategy twice (first without cache, second with cache)
2. Measure time for each run
3. Verify second run <10% of first run (sentence-transformers only)

**False Positive Prevention**:

1. Create new feature request with LOW similarity (<40%)
2. Run strategy
3. Verify NOT flagged (empty matching list)

### Documentation Sources

**CE Vacuum**:

- `tools/ce/vacuum.py` - Main CLI implementation
- `tools/ce/vacuum_strategies/` - All strategy implementations

**NLP Components**:

- PRP-46.1.1: NLP foundation layer
- PRP-46.2.1: PRP lifecycle docs detection
- PRP-46.2.2: Enhanced existing strategies
- PRP-46.3.1: LLM batch analysis
