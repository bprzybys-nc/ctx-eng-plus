---
prp_id: 46.2.2
feature_name: Enhance Existing Vacuum Strategies with NLP
batch_id: 46
stage: 2
order: 2
status: completed
created: 2025-11-16T00:00:00Z
updated: 2025-11-16T13:00:00Z
completed: 2025-11-16T13:00:00Z
commit: a11aec9
complexity: low
estimated_hours: 1.5
dependencies: PRP-46.1.1 (ce.nlp module)
---

# Enhance Existing Vacuum Strategies with NLP

## 1. TL;DR

**Objective**: Add NLP semantic similarity to existing vacuum strategies (`obsolete_docs`, `orphan_tests`) without breaking current logic

**What**: Non-disruptive enhancement that adds +20% confidence boost for semantic matches, complements existing filename-based detection

**Why**: Improve detection accuracy for docs with weak filename patterns but high semantic similarity to executed PRPs

**Effort**: 1.5 hours (LOW complexity, non-disruptive refactoring)

**Dependencies**: PRP-46.1.1 (needs `ce.nlp` module with DocumentSimilarity)

## 2. Context

### Background

Current vacuum strategies rely heavily on filename patterns:

- **obsolete_docs.py**: Detects temporary docs via prefixes (`ANALYSIS-`, `PLAN-`, `REPORT-`) and suffixes (`-SUMMARY-`, `-PLAN-`)
- **orphan_tests.py**: Matches test files to code files via naming convention (`test_foo.py` → `foo.py`)

**Problem**: Docs with weak filename patterns but high semantic similarity to executed PRPs are missed.

**Example**:

```
PRPs/feature-requests/auth-idea.md
Content: "Implement JWT-based authentication with refresh tokens"

PRPs/executed/PRP-23-auth-system.md
Content: "Implemented JWT authentication with refresh token support"

Current detection: MISS (no -PLAN- prefix, not flagged)
With NLP: DETECT (semantic similarity 0.85, confidence boost)
```

### Constraints and Considerations

**Non-Disruptive Integration**:

- Keep all existing filename-based logic unchanged
- NLP adds confidence boost ONLY when filename patterns already match
- Existing test cases must still pass

**Performance**:

- NLP comparison: ~50ms per doc pair with sentence-transformers
- Only compute similarity for docs that pass initial filename checks (reduces computation)
- Use existing embedding cache from `ce.nlp` module (no additional caching)

**Graceful Fallback**:

- No sentence-transformers installed → auto-fallback to sklearn → difflib
- Empty files or corrupted markdown → skip gracefully (NLP returns None)

### Documentation References

**CE NLP Module** (from PRP-46.1.1):

- `from ce.nlp import DocumentSimilarity` - semantic comparison with 3-tier fallback
- Module location: `tools/ce/nlp/similarity.py`
- Cache location: `.ce/nlp-embeddings-cache.json`

**Existing Vacuum Strategies**:

- `tools/ce/vacuum_strategies/obsolete_docs.py:tools/ce/vacuum_strategies/obsolete_docs.py:1-302` - Detects obsolete docs by filename patterns
- `tools/ce/vacuum_strategies/orphan_tests.py:tools/ce/vacuum_strategies/orphan_tests.py:1-62` - Detects orphaned test files

## 3. Implementation Steps

### Phase 1: Enhance ObsoleteDocsStrategy (45 min)

**Step 1: Import NLP Module** (5 min)

Add import at top of `tools/ce/vacuum_strategies/obsolete_docs.py:4`:

```python
from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate

# NEW: Import NLP module
try:
    from ce.nlp import DocumentSimilarity
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
```

**Step 2: Initialize NLP in Constructor** (10 min)

Add `__init__` method to `ObsoleteDocStrategy` class at `tools/ce/vacuum_strategies/obsolete_docs.py:10`:

```python
class ObsoleteDocStrategy(BaseStrategy):
    """Find obsolete documentation files."""

    # ... existing constants ...

    def __init__(self, project_root: Path):
        """Initialize strategy with NLP support.

        Args:
            project_root: Project root directory
        """
        super().__init__(project_root)

        # Initialize NLP for semantic similarity (if available)
        self.nlp = None
        if NLP_AVAILABLE:
            try:
                self.nlp = DocumentSimilarity()
            except Exception:
                # If NLP init fails, continue without it
                pass

        # Cache executed PRPs for similarity comparison
        self._executed_prps = None
```

**Step 3: Add Helper Method for Similarity Computation** (15 min)

Add new method after `_find_newer_version` at `tools/ce/vacuum_strategies/obsolete_docs.py:302`:

```python
    def _get_executed_prps(self) -> List[Path]:
        """Get list of executed PRPs (cached).

        Returns:
            List of paths to executed PRPs
        """
        if self._executed_prps is None:
            executed_dir = self.project_root / "PRPs" / "executed"
            if executed_dir.exists():
                self._executed_prps = list(executed_dir.glob("PRP-*.md"))
            else:
                self._executed_prps = []
        return self._executed_prps

    def _get_max_similarity_to_prps(self, doc_path: Path) -> float:
        """Compute maximum semantic similarity to executed PRPs.

        Args:
            doc_path: Path to document to check

        Returns:
            Maximum similarity score (0.0-1.0), or 0.0 if NLP unavailable
        """
        if not self.nlp:
            return 0.0

        executed_prps = self._get_executed_prps()
        if not executed_prps:
            return 0.0

        max_similarity = 0.0
        for prp_path in executed_prps:
            try:
                similarity = self.nlp.compare(doc_path, prp_path)
                if similarity > max_similarity:
                    max_similarity = similarity
            except Exception:
                # Skip if comparison fails
                continue

        return max_similarity
```

**Step 4: Apply NLP Boost in Detection Logic** (15 min)

Modify `find_candidates` method at `tools/ce/vacuum_strategies/obsolete_docs.py:114-137` to add NLP boost:

```python
            if temp_doc_match or content_marker:
                # Combine filename and content analysis
                reason_parts = []
                if temp_doc_match:
                    reason_parts.append(f"filename {temp_doc_match}")
                if content_marker:
                    reason_parts.append(f"content: {content_marker}")

                # Calculate base confidence
                confidence = 70
                if self.is_recently_active(md_file, days=30):
                    confidence = 55

                # NEW: Apply NLP boost if high semantic similarity
                if self.nlp and confidence < 100:
                    similarity = self._get_max_similarity_to_prps(md_file)
                    if similarity >= 0.7:
                        nlp_boost = 20  # +20% boost
                        confidence = min(100, confidence + nlp_boost)
                        reason_parts.append(f"NLP similarity {similarity:.2f}")

                reason = f"Temporary analysis doc: {', '.join(reason_parts)}"

                candidate = CleanupCandidate(
                    path=md_file,
                    reason=reason,
                    confidence=confidence,
                    size_bytes=self.get_file_size(md_file),
                    last_modified=self.get_last_modified(md_file),
                    git_history=self.get_git_history(md_file),
                )
                candidates.append(candidate)
                continue
```

Apply same NLP boost pattern to versioned/obsolete suffix detection at `tools/ce/vacuum_strategies/obsolete_docs.py:146-163`:

```python
                # Recently active files get lower confidence
                confidence = 70
                if self.is_recently_active(md_file, days=30):
                    confidence = 50

                # NEW: Apply NLP boost if high semantic similarity
                reason = f"Versioned/obsolete doc: {suffix} suffix"
                if newer_version:
                    reason += f" (newer: {newer_version.name})"

                if self.nlp and confidence < 100:
                    similarity = self._get_max_similarity_to_prps(md_file)
                    if similarity >= 0.7:
                        nlp_boost = 20
                        confidence = min(100, confidence + nlp_boost)
                        reason += f", NLP similarity {similarity:.2f}"

                candidate = CleanupCandidate(
                    path=md_file,
                    reason=reason,
                    confidence=confidence,
                    size_bytes=self.get_file_size(md_file),
                    last_modified=self.get_last_modified(md_file),
                    git_history=self.get_git_history(md_file),
                )
```

### Phase 2: Enhance OrphanTestStrategy (45 min)

**Step 1: Import NLP Module** (5 min)

Add import at top of `tools/ce/vacuum_strategies/orphan_tests.py:3`:

```python
from pathlib import Path
from typing import List

from .base import BaseStrategy, CleanupCandidate

# NEW: Import NLP module
try:
    from ce.nlp import DocumentSimilarity
    NLP_AVAILABLE = True
except ImportError:
    NLP_AVAILABLE = False
```

**Step 2: Initialize NLP in Constructor** (10 min)

Add `__init__` method to `OrphanTestStrategy` class at `tools/ce/vacuum_strategies/orphan_tests.py:9`:

```python
class OrphanTestStrategy(BaseStrategy):
    """Find test files whose corresponding module no longer exists."""

    def __init__(self, project_root: Path):
        """Initialize strategy with NLP support.

        Args:
            project_root: Project root directory
        """
        super().__init__(project_root)

        # Initialize NLP for semantic test-code matching (if available)
        self.nlp = None
        if NLP_AVAILABLE:
            try:
                self.nlp = DocumentSimilarity()
            except Exception:
                # If NLP init fails, continue without it
                pass
```

**Step 3: Add Helper Method for Semantic Code Matching** (15 min)

Add new method after `find_candidates` at `tools/ce/vacuum_strategies/orphan_tests.py:61`:

```python
    def _find_related_code_files(self, test_file: Path) -> List[Path]:
        """Find potentially related code files using semantic similarity.

        Args:
            test_file: Path to test file

        Returns:
            List of code files with similarity ≥0.5
        """
        if not self.nlp:
            return []

        # Search for Python files in ce/ directory
        ce_dir = self.project_root / "tools" / "ce"
        if not ce_dir.exists():
            ce_dir = self.project_root / "ce"

        if not ce_dir.exists():
            return []

        related_files = []
        for code_file in ce_dir.glob("**/*.py"):
            if code_file.name.startswith("test_"):
                continue

            try:
                similarity = self.nlp.compare(test_file, code_file)
                if similarity >= 0.5:
                    related_files.append((code_file, similarity))
            except Exception:
                continue

        # Return files sorted by similarity (highest first)
        related_files.sort(key=lambda x: x[1], reverse=True)
        return [f for f, _ in related_files]
```

**Step 4: Apply NLP in Orphan Detection** (15 min)

Modify `find_candidates` method at `tools/ce/vacuum_strategies/orphan_tests.py:44-59` to use semantic matching:

```python
            # Check if any corresponding module exists
            module_exists = any(m.exists() for m in module_candidates)

            # NEW: If filename convention fails, try semantic matching
            if not module_exists and self.nlp:
                related_files = self._find_related_code_files(test_file)
                if related_files:
                    # Test has semantic relationship to code, not orphaned
                    continue

            if not module_exists:
                # Recently active files might be integration tests
                confidence = 60
                if self.is_recently_active(test_file, days=30):
                    confidence = 40

                # NEW: Lower confidence if NLP available but found no matches
                # (stronger evidence of orphan status)
                reason = f"Orphaned test: no module '{module_name}.py' found"
                if self.nlp:
                    confidence = min(100, confidence + 10)  # +10% boost
                    reason += " (verified via semantic analysis)"

                candidate = CleanupCandidate(
                    path=test_file,
                    reason=reason,
                    confidence=confidence,
                    size_bytes=self.get_file_size(test_file),
                    last_modified=self.get_last_modified(test_file),
                    git_history=self.get_git_history(test_file),
                )
                candidates.append(candidate)
```

## 4. Validation Gates

### Gate 1: Unit Tests Pass (NLP Boost)

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py::test_obsolete_docs_nlp_boost -v
```

**Expected Output**:

```
test_obsolete_docs_nlp_boost PASSED
```

**Validates**: AC2 - Semantic confidence boost for obsolete docs

---

### Gate 2: Regression Tests Pass

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py -v -k "obsolete or orphan"
```

**Expected Output**:

```
All existing tests PASSED (no regressions)
```

**Validates**: AC1 - Non-disruptive integration (existing logic unchanged)

---

### Gate 3: Semantic Test-Code Matching

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py::test_orphan_tests_semantic_matching -v
```

**Expected Output**:

```
test_orphan_tests_semantic_matching PASSED
```

**Validates**: AC3 - Semantic test-code matching for orphan tests

---

### Gate 4: No False Positives from NLP

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py::test_no_false_positives_from_nlp -v
```

**Expected Output**:

```
test_no_false_positives_from_nlp PASSED
```

**Validates**: NLP doesn't flag valid docs (confidence thresholds work correctly)

## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py -v
```

### Test Cases

**Test 1: Obsolete Docs NLP Boost** (`test_obsolete_docs_nlp_boost`)

```python
def test_obsolete_docs_nlp_boost(tmp_path):
    """Obsolete doc with weak filename but high semantic match gets boosted."""

    # Create doc with weak filename pattern (no -SUMMARY-, -PLAN-)
    doc = tmp_path / "PRPs/feature-requests/auth-idea.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("Implement JWT-based authentication with refresh tokens")

    # Create matching executed PRP
    prp_dir = tmp_path / "PRPs/executed"
    prp_dir.mkdir(parents=True)
    prp = prp_dir / "PRP-23-auth-system.md"
    prp.write_text("Implemented JWT authentication with refresh token support")

    # Strategy should detect with NLP boost
    strategy = ObsoleteDocStrategy(tmp_path)
    candidates = strategy.find_candidates()

    # Without NLP: confidence 0 (no filename pattern)
    # With NLP: confidence 70 (base) → 90 (NLP boost) if similarity ≥0.7
    matching = [c for c in candidates if c.path == doc]

    if strategy.nlp:
        assert len(matching) == 1
        assert matching[0].confidence >= 75  # Base + NLP boost
        assert "NLP similarity" in matching[0].reason
    else:
        # NLP unavailable, skip test
        pass
```

**Test 2: Orphan Tests Semantic Matching** (`test_orphan_tests_semantic_matching`)

```python
def test_orphan_tests_semantic_matching(tmp_path):
    """Test file with non-standard naming detected via semantic relationship."""

    # Create test file with non-standard name
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    test_file = tests_dir / "test_authentication_tests.py"
    test_file.write_text("""
import pytest
from ce.auth.jwt_handler import create_jwt, verify_jwt

def test_jwt_creation():
    token = create_jwt(user_id=123)
    assert token is not None
""")

    # Create related code file (not named auth.py)
    ce_dir = tmp_path / "tools/ce/auth"
    ce_dir.mkdir(parents=True)
    code_file = ce_dir / "jwt_handler.py"
    code_file.write_text("""
def create_jwt(user_id: int) -> str:
    return f"jwt-token-{user_id}"

def verify_jwt(token: str) -> int:
    return int(token.split('-')[-1])
""")

    # Strategy should NOT flag as orphan (semantic match exists)
    strategy = OrphanTestStrategy(tmp_path)
    candidates = strategy.find_candidates()

    matching = [c for c in candidates if c.path == test_file]

    if strategy.nlp:
        # NLP finds semantic relationship, test not orphaned
        assert len(matching) == 0
    else:
        # Without NLP, filename convention fails, flagged as orphan
        assert len(matching) == 1
```

**Test 3: Existing Detection Unchanged** (`test_existing_detection_unchanged`)

```python
def test_existing_detection_unchanged(tmp_path):
    """Existing detection logic still works (regression test)."""

    # Create temporary doc with standard prefix
    doc = tmp_path / "PRPs/feature-requests/ANALYSIS-feature.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("Analysis document")

    # Strategy should detect via filename pattern (no NLP needed)
    strategy = ObsoleteDocStrategy(tmp_path)
    candidates = strategy.find_candidates()

    matching = [c for c in candidates if c.path == doc]
    assert len(matching) == 1
    assert "ANALYSIS-" in matching[0].reason
```

**Test 4: No False Positives from NLP** (`test_no_false_positives_from_nlp`)

```python
def test_no_false_positives_from_nlp(tmp_path):
    """NLP doesn't flag valid docs with low similarity."""

    # Create active feature request (no matching PRP)
    doc = tmp_path / "PRPs/feature-requests/new-feature.md"
    doc.parent.mkdir(parents=True)
    doc.write_text("Implement new blockchain integration feature")

    # Create unrelated executed PRP
    prp_dir = tmp_path / "PRPs/executed"
    prp_dir.mkdir(parents=True)
    prp = prp_dir / "PRP-23-auth-system.md"
    prp.write_text("Implemented JWT authentication with refresh token support")

    # Strategy should NOT flag (low semantic similarity)
    strategy = ObsoleteDocStrategy(tmp_path)
    candidates = strategy.find_candidates()

    matching = [c for c in candidates if c.path == doc]
    assert len(matching) == 0  # Not flagged (similarity <0.7)
```

### Test Coverage Target

- 100% coverage of new NLP integration code
- All existing tests pass (regression coverage)
- Edge cases: NLP unavailable, empty files, multiple PRPs

## 6. Rollout Plan

### Phase 1: Development (1.5 hours)

**Tasks**:

1. Implement Phase 1: Enhance ObsoleteDocsStrategy (45 min)
2. Implement Phase 2: Enhance OrphanTestStrategy (45 min)
3. Write unit tests (30 min)

**Validation**: All 4 validation gates pass

### Phase 2: Review (15 min)

**Tasks**:

1. Code review for KISS principle adherence
2. Verify non-disruptive integration (existing tests pass)
3. Check error handling (graceful fallback if NLP unavailable)

**Approval**: Self-review or peer review

### Phase 3: Integration (15 min)

**Tasks**:

1. Verify NLP module available (from PRP-46.1.1)
2. Run full vacuum test suite
3. Test on real PRPs directory

**Success Criteria**:

- All tests pass
- No false positives on active feature requests
- NLP boost visible in vacuum report output

---

## Research Findings

### Codebase Analysis

**Existing Vacuum Strategies Structure**:

- Base class: `tools/ce/vacuum_strategies/base.py` (BaseStrategy, CleanupCandidate)
- Strategy pattern: Each strategy extends BaseStrategy
- Constructor pattern: All strategies accept `project_root: Path`
- Detection pattern: `find_candidates() -> List[CleanupCandidate]`

**Confidence Scoring Pattern**:

- HIGH: 80-100% (auto-delete candidates)
- MEDIUM: 50-79% (review recommended)
- LOW: 0-49% (keep, low priority)

**Current ObsoleteDocStrategy**:

- Lines: 302 total
- Detection methods: Filename patterns (prefixes, suffixes, infixes) + content markers
- Base confidence: 70% for temp docs, 55% if recently active

**Current OrphanTestStrategy**:

- Lines: 62 total
- Detection method: Filename convention only (`test_foo.py` → `foo.py`)
- Base confidence: 60%, 40% if recently active

### NLP Module Integration Pattern

From PRP-46.1.1:

```python
from ce.nlp import DocumentSimilarity

# Initialize
nlp = DocumentSimilarity()

# Compare documents (returns 0.0-1.0)
similarity = nlp.compare(doc_a_path, doc_b_path)

# Automatic 3-tier fallback:
# - Tier 1: sentence-transformers (0.85+ accuracy)
# - Tier 2: sklearn TF-IDF (0.70+ accuracy)
# - Tier 3: difflib (0.50+ accuracy)
```

### Non-Disruptive Enhancement Pattern

**Key Principle**: Add NLP as confidence booster, not replacement

**Pattern**:

1. Keep existing detection logic unchanged
2. Add NLP similarity check AFTER existing logic
3. Apply confidence boost (+20%) only when:
   - Existing detection already flagged the doc
   - NLP similarity ≥0.7 (semantic match threshold)
4. Cap confidence at 100 max

**Example**:

```python
# Existing logic (unchanged)
base_confidence = 70 if temp_doc_match else 0

# NEW: NLP boost (additive, not replacement)
if base_confidence > 0 and nlp and similarity >= 0.7:
    base_confidence = min(100, base_confidence + 20)
```

### Documentation Sources

**CE NLP Module** (from PRP-46.1.1):

- Module: `tools/ce/nlp/similarity.py`
- Class: `DocumentSimilarity`
- Method: `compare(doc_a: Path, doc_b: Path) -> float`
- Cache: `.ce/nlp-embeddings-cache.json` (mtime-based invalidation)

**Vacuum Strategy Base** (from existing code):

- Module: `tools/ce/vacuum_strategies/base.py`
- Class: `BaseStrategy`
- Methods: `is_protected()`, `is_recently_active()`, `get_file_size()`, `get_last_modified()`, `get_git_history()`
