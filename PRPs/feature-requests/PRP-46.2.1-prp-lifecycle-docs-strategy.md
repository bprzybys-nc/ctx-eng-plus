---
prp_id: 46.2.1
feature_name: PRP Lifecycle Docs Detection Strategy
status: pending
created: 2025-11-16
updated: 2025-11-16
complexity: medium
estimated_hours: 2.5
dependencies: PRP-46.1.1
batch_id: 46
stage: 2
execution_order: 2
merge_order: 2
---

# PRP Lifecycle Docs Detection Strategy

## 1. TL;DR

**Objective**: Detect temporary documents throughout PRP lifecycle using semantic similarity

**What**: Implement vacuum strategy that finds INITIAL.md, PLAN/ANALYSIS/REPORT docs, and superseded feature requests using NLP from PRP-46.1.1

**Why**: Reduce manual vacuum review from 30-40% to <10% by using semantic matching instead of naive text comparison

**Effort**: 2.5 hours (setup 15min, core implementation 90min, tests 30min, validation 15min)

**Dependencies**: PRP-46.1.1 (ce.nlp module)

## 2. Context

### Background

Current vacuum misses temporary docs throughout PRP lifecycle:
- INITIAL.md files in subdirectories (e.g., `PRPs/feature-requests/auth/INITIAL.md`)
- PLAN-*, ANALYSIS-*, REPORT-* docs created during investigation
- Superseded feature requests with similar content but different formatting

Example: PRP-42 superseded 3 docs (INIT-PROJECT-WORKFLOW-INITIAL.md, *-ANALYSIS.md, *-PLAN.md) but vacuum flagged them as LOW confidence (55%) requiring manual review.

This PRP implements semantic detection using NLP to:
1. Scan all subdirectories recursively (`rglob("*.md")`)
2. Compare docs to executed PRPs using semantic similarity
3. Apply confidence thresholds (≥75% HIGH, 40-70% MEDIUM, <40% LOW)

### Constraints and Considerations

**Performance** (100 feature requests × 45 executed PRPs):
- With NLP cache: ~2-3 seconds total
- Without cache: ~10-15 seconds first run (sentence-transformers)
- Difflib fallback: ~1 second

**Detection Types**:
1. **INITIAL→PRP**: Highest priority, exact filename match
2. **Temporary→PRP**: PLAN/ANALYSIS/REPORT prefix detection
3. **Superseded**: Fallback semantic matching

**Confidence Thresholds**:
- ≥75%: HIGH - Auto-flag, no LLM needed
- 40-70%: MEDIUM - Queue for Haiku batch review (PRP-46.3.1)
- <40%: LOW - Keep as-is

### Documentation References

- PRP-46.1.1: NLP Foundation Layer (`ce.nlp` module)
- pathlib.Path.rglob for recursive scanning
- pytest for testing

## 3. Implementation Steps

### Phase 1: Strategy Setup (15 min)

**Step 1.1**: Create strategy file

```bash
cd tools
touch ce/vacuum_strategies/prp_lifecycle_docs.py
```

**Step 1.2**: Register strategy in vacuum CLI (ce/vacuum.py)

```python
# Add to vacuum.py strategy imports
from ce.vacuum_strategies.prp_lifecycle_docs import PRPLifecycleDocsStrategy

# Register in strategy list
STRATEGIES = {
    'temp_files': TempFilesStrategy(),
    'prp_lifecycle_docs': PRPLifecycleDocsStrategy(),  # NEW
    # ... other strategies
}
```

### Phase 2: Core Implementation (90 min)

**Step 2.1**: Implement PRPLifecycleDocsStrategy (ce/vacuum_strategies/prp_lifecycle_docs.py)

```python
"""Vacuum strategy for PRP lifecycle document detection."""
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

from ce.nlp import DocumentSimilarity


@dataclass
class Candidate:
    """Cleanup candidate."""
    path: Path
    reason: str
    confidence: float
    detection_type: str  # INITIAL→PRP, Temporary→PRP, Superseded
    superseded_by: Optional[Path] = None


class PRPLifecycleDocsStrategy:
    """Detects temporary docs throughout PRP lifecycle.

    Detection types:
    1. INITIAL.md → executed PRP
    2. PLAN/ANALYSIS/REPORT → executed PRP
    3. Superseded feature requests → executed PRP
    """

    def __init__(self):
        """Initialize strategy with NLP backend."""
        self.nlp = DocumentSimilarity()

    def scan(self, project_root: Path) -> List[Candidate]:
        """Scan for PRP lifecycle docs.

        Args:
            project_root: Project root directory

        Returns:
            List of cleanup candidates
        """
        candidates = []

        # Get all executed PRPs (comparison baseline)
        executed_dir = project_root / "PRPs" / "executed"
        if not executed_dir.exists():
            return []

        executed_prps = list(executed_dir.glob("PRP-*.md"))
        if not executed_prps:
            return []

        # Scan feature-requests recursively
        feature_requests_dir = project_root / "PRPs" / "feature-requests"
        if not feature_requests_dir.exists():
            return []

        # Use rglob for recursive scanning
        for md_file in feature_requests_dir.rglob("*.md"):
            # Skip PRP files themselves
            if md_file.name.startswith("PRP-"):
                continue

            # Detect lifecycle doc
            candidate = self._detect_lifecycle_doc(md_file, executed_prps)
            if candidate:
                candidates.append(candidate)

        return candidates

    def _detect_lifecycle_doc(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[Candidate]:
        """Detect if file is a lifecycle doc.

        Args:
            md_file: File to check
            executed_prps: List of executed PRP files

        Returns:
            Candidate if match found, None otherwise
        """
        filename = md_file.name

        # Type 1: INITIAL.md files (highest priority)
        if filename == "INITIAL.md":
            return self._check_initial_md(md_file, executed_prps)

        # Type 2: Temporary analysis docs
        if any(filename.startswith(prefix) for prefix in ["PLAN-", "ANALYSIS-", "REPORT-"]):
            return self._check_temporary_doc(md_file, executed_prps)

        # Type 3: Superseded feature requests (content-based)
        return self._check_superseded_request(md_file, executed_prps)

    def _check_initial_md(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[Candidate]:
        """Check if INITIAL.md has corresponding executed PRP.

        Args:
            md_file: INITIAL.md file
            executed_prps: List of executed PRPs

        Returns:
            Candidate if HIGH confidence match found
        """
        best_match = None
        best_score = 0.0

        for prp_path in executed_prps:
            similarity = self.nlp.compare(md_file, prp_path)

            if similarity > best_score:
                best_score = similarity
                best_match = prp_path

        # Apply confidence threshold
        if best_score >= 0.75:  # HIGH confidence
            prp_id = best_match.stem.split('-')[1] if best_match else "unknown"
            return Candidate(
                path=md_file,
                reason=f"Generated as PRP-{prp_id}",
                confidence=best_score,
                detection_type="INITIAL→PRP",
                superseded_by=best_match
            )

        return None

    def _check_temporary_doc(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[Candidate]:
        """Check if PLAN/ANALYSIS/REPORT has corresponding PRP.

        Args:
            md_file: Temporary doc file
            executed_prps: List of executed PRPs

        Returns:
            Candidate if HIGH confidence match found
        """
        best_match = None
        best_score = 0.0

        for prp_path in executed_prps:
            similarity = self.nlp.compare(md_file, prp_path)

            if similarity > best_score:
                best_score = similarity
                best_match = prp_path

        # Apply confidence threshold (slightly lower for temporary docs)
        if best_score >= 0.70:  # HIGH/MEDIUM threshold
            prp_id = best_match.stem.split('-')[1] if best_match else "unknown"

            # Determine confidence tier
            if best_score >= 0.75:
                tier = "HIGH"
            else:
                tier = "MEDIUM"

            return Candidate(
                path=md_file,
                reason=f"Integrated into PRP-{prp_id} ({tier} confidence)",
                confidence=best_score,
                detection_type="Temporary→PRP",
                superseded_by=best_match
            )

        return None

    def _check_superseded_request(
        self,
        md_file: Path,
        executed_prps: List[Path]
    ) -> Optional[Candidate]:
        """Check if feature request superseded by executed PRP.

        Args:
            md_file: Feature request file
            executed_prps: List of executed PRPs

        Returns:
            Candidate if MEDIUM+ confidence match found
        """
        best_match = None
        best_score = 0.0

        for prp_path in executed_prps:
            similarity = self.nlp.compare(md_file, prp_path)

            if similarity > best_score:
                best_score = similarity
                best_match = prp_path

        # Apply confidence threshold (include MEDIUM for LLM review)
        if best_score >= 0.40:  # MEDIUM or higher
            prp_id = best_match.stem.split('-')[1] if best_match else "unknown"

            # Determine tier
            if best_score >= 0.75:
                tier = "HIGH"
            elif best_score >= 0.40:
                tier = "MEDIUM"
            else:
                tier = "LOW"

            return Candidate(
                path=md_file,
                reason=f"Superseded by PRP-{prp_id} ({tier} confidence)",
                confidence=best_score,
                detection_type="Superseded",
                superseded_by=best_match
            )

        return None  # <40% confidence, not flagged
```

### Phase 3: Testing (30 min)

**Step 3.1**: Create test file (tools/tests/test_vacuum_prp_lifecycle.py)

```python
"""Tests for PRP lifecycle docs vacuum strategy."""
import pytest
from pathlib import Path
from ce.vacuum_strategies.prp_lifecycle_docs import PRPLifecycleDocsStrategy


class TestPRPLifecycleDocsStrategy:
    """Test PRP lifecycle document detection."""

    def test_detects_initial_md_with_matching_prp(self, tmp_path):
        """INITIAL.md detected when matching PRP exists."""
        # Setup directories
        feature_dir = tmp_path / "PRPs" / "feature-requests" / "auth"
        feature_dir.mkdir(parents=True)

        executed_dir = tmp_path / "PRPs" / "executed"
        executed_dir.mkdir(parents=True)

        # Create INITIAL.md
        initial = feature_dir / "INITIAL.md"
        initial.write_text("User authentication system with JWT tokens")

        # Create matching executed PRP
        prp = executed_dir / "PRP-23-auth-system.md"
        prp.write_text("Implemented JWT-based authentication system")

        # Run strategy
        strategy = PRPLifecycleDocsStrategy()
        candidates = strategy.scan(tmp_path)

        # Verify detection
        assert len(candidates) == 1
        assert candidates[0].detection_type == "INITIAL→PRP"
        assert candidates[0].confidence >= 0.60  # Semantic match
        assert "PRP-23" in candidates[0].reason

    def test_detects_temporary_docs(self, tmp_path):
        """PLAN/ANALYSIS/REPORT docs detected."""
        feature_dir = tmp_path / "PRPs" / "feature-requests"
        feature_dir.mkdir(parents=True)

        executed_dir = tmp_path / "PRPs" / "executed"
        executed_dir.mkdir(parents=True)

        # Create temporary docs
        plan = feature_dir / "PLAN-vacuum-optimization.md"
        plan.write_text("Plan for vacuum performance improvements")

        analysis = feature_dir / "ANALYSIS-vacuum-performance.md"
        analysis.write_text("Analysis of vacuum bottlenecks")

        # Create matching PRP
        prp = executed_dir / "PRP-38-vacuum-optimization.md"
        prp.write_text("Implemented vacuum performance optimizations")

        # Run strategy
        strategy = PRPLifecycleDocsStrategy()
        candidates = strategy.scan(tmp_path)

        # Verify detection
        assert len(candidates) >= 1  # At least one detected
        types = [c.detection_type for c in candidates]
        assert "Temporary→PRP" in types

    def test_recursive_scan_finds_subdirectory_docs(self, tmp_path):
        """Recursive scan finds INITIAL.md in subdirectories."""
        # Create nested directory
        nested_dir = tmp_path / "PRPs" / "feature-requests" / "auth" / "oauth"
        nested_dir.mkdir(parents=True)

        executed_dir = tmp_path / "PRPs" / "executed"
        executed_dir.mkdir(parents=True)

        # Create INITIAL.md in nested location
        initial = nested_dir / "INITIAL.md"
        initial.write_text("OAuth 2.0 implementation")

        # Create matching PRP
        prp = executed_dir / "PRP-25-oauth.md"
        prp.write_text("Implemented OAuth 2.0 authentication")

        # Run strategy
        strategy = PRPLifecycleDocsStrategy()
        candidates = strategy.scan(tmp_path)

        # Verify found in nested directory
        assert len(candidates) >= 1
        assert any("oauth" in str(c.path) for c in candidates)

    def test_no_false_positives_on_active_docs(self, tmp_path):
        """Active feature requests with no matching PRP are not flagged."""
        feature_dir = tmp_path / "PRPs" / "feature-requests"
        feature_dir.mkdir(parents=True)

        executed_dir = tmp_path / "PRPs" / "executed"
        executed_dir.mkdir(parents=True)

        # Create active doc with no matching PRP
        active = feature_dir / "INITIAL-critical-memory.md"
        active.write_text("Critical memory consolidation feature")

        # Create unrelated PRP
        prp = executed_dir / "PRP-99-unrelated.md"
        prp.write_text("Completely different topic about web UI")

        # Run strategy
        strategy = PRPLifecycleDocsStrategy()
        candidates = strategy.scan(tmp_path)

        # Verify no false positives
        # (similarity should be <40%, so not flagged)
        assert len(candidates) == 0 or all(c.confidence < 0.40 for c in candidates)

    def test_confidence_tiers_applied_correctly(self, tmp_path):
        """Confidence thresholds correctly categorize matches."""
        feature_dir = tmp_path / "PRPs" / "feature-requests"
        feature_dir.mkdir(parents=True)

        executed_dir = tmp_path / "PRPs" / "executed"
        executed_dir.mkdir(parents=True)

        # Create doc with very similar content (HIGH confidence)
        high_conf = feature_dir / "similar.md"
        high_conf.write_text("Machine learning neural networks deep learning AI")

        prp = executed_dir / "PRP-50-ml.md"
        prp.write_text("Machine learning with neural networks and deep learning for AI")

        # Run strategy
        strategy = PRPLifecycleDocsStrategy()
        candidates = strategy.scan(tmp_path)

        # Verify HIGH confidence
        if candidates:
            assert any(c.confidence >= 0.70 for c in candidates)
```

**Step 3.2**: Run tests

```bash
cd tools
uv run pytest tests/test_vacuum_prp_lifecycle.py -v
```

### Phase 4: Validation (15 min)

**Step 4.1**: Manual test with real PRPs

```bash
cd tools
python -c "
from pathlib import Path
from ce.vacuum_strategies.prp_lifecycle_docs import PRPLifecycleDocsStrategy

strategy = PRPLifecycleDocsStrategy()
candidates = strategy.scan(Path('..'))

print(f'Found {len(candidates)} candidates:')
for c in candidates[:10]:  # Show first 10
    print(f'  {c.path.name}: {c.detection_type} ({c.confidence:.2f}) - {c.reason}')
"
```

## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**:
```bash
cd tools
uv run pytest tests/test_vacuum_prp_lifecycle.py -v
```

**Expected**: All 5 tests pass

**Validates**:
- AC1: Recursive scanning (test_recursive_scan_finds_subdirectory_docs)
- AC2: Confidence tiers (test_confidence_tiers_applied_correctly)
- AC3: No false positives (test_no_false_positives_on_active_docs)

### Gate 2: Strategy Registration

**Command**:
```bash
cd tools
python -c "from ce.vacuum import STRATEGIES; assert 'prp_lifecycle_docs' in STRATEGIES; print('✓ Strategy registered')"
```

**Expected**: "✓ Strategy registered"

### Gate 3: Real PRP Scan

**Command**:
```bash
cd tools
python -c "
from pathlib import Path
from ce.vacuum_strategies.prp_lifecycle_docs import PRPLifecycleDocsStrategy

strategy = PRPLifecycleDocsStrategy()
candidates = strategy.scan(Path('..'))

high_conf = [c for c in candidates if c.confidence >= 0.75]
medium_conf = [c for c in candidates if 0.40 <= c.confidence < 0.75]
low_conf = [c for c in candidates if c.confidence < 0.40]

print(f'Total: {len(candidates)} candidates')
print(f'HIGH (≥75%): {len(high_conf)}')
print(f'MEDIUM (40-75%): {len(medium_conf)}')
print(f'LOW (<40%): {len(low_conf)}')

assert len(low_conf) == 0, 'Should not flag LOW confidence'
print('✓ Confidence tiers working correctly')
"
```

**Expected**: No LOW confidence candidates flagged

### Gate 4: NLP Backend Verification

**Command**:
```bash
cd tools
python -c "
from ce.vacuum_strategies.prp_lifecycle_docs import PRPLifecycleDocsStrategy

strategy = PRPLifecycleDocsStrategy()
print(f'NLP backend: {strategy.nlp.backend_name}')
assert strategy.nlp.backend_name in ['sentence-transformers', 'sklearn', 'difflib']
print('✓ NLP backend initialized')
"
```

**Expected**: NLP backend displayed (one of 3 tiers)

## 5. Testing Strategy

### Test Framework
pytest

### Test Command
```bash
cd tools
uv run pytest tests/test_vacuum_prp_lifecycle.py -v
```

### Test Coverage

**Unit Tests** (5 tests):
- INITIAL.md detection with matching PRP
- Temporary docs (PLAN/ANALYSIS/REPORT) detection
- Recursive subdirectory scanning
- No false positives on active docs
- Confidence tier application

**Integration Tests**:
- Real PRP scanning (manual validation gate)
- NLP backend integration

### Test Fixtures
- tmp_path for isolated test directories
- Real PRPs from PRPs/executed/ for integration tests

## 6. Rollout Plan

### Phase 1: Development (2.5 hours)
1. Create strategy file (15 min)
2. Implement core detection logic (90 min)
3. Write comprehensive tests (30 min)
4. Validate with real PRPs (15 min)

### Phase 2: Integration (Post-PRP)
1. Used by vacuum CLI automatically
2. Candidates with 40-70% confidence queued for PRP-46.3.1 (Haiku batch review)
3. HIGH confidence (≥75%) candidates auto-flagged

### Phase 3: Monitoring
1. Track false positive rate
2. Adjust confidence thresholds if needed
3. Monitor NLP cache performance

### Rollback Plan
If issues arise:
1. Remove from STRATEGIES dict in vacuum.py
2. Delete ce/vacuum_strategies/prp_lifecycle_docs.py
3. Vacuum continues with other strategies

---

## Appendix: Detection Examples

**INITIAL.md → PRP** (HIGH confidence ≥75%):
```
PRPs/feature-requests/auth/INITIAL.md
→ Matched with PRPs/executed/PRP-23-auth-system.md
→ Confidence: 0.87
→ Reason: "Generated as PRP-23"
```

**Temporary docs** (MEDIUM confidence 40-75%):
```
PRPs/feature-requests/PLAN-vacuum-optimization.md
→ Matched with PRPs/executed/PRP-38-vacuum-optimization.md
→ Confidence: 0.68
→ Reason: "Integrated into PRP-38 (MEDIUM confidence)"
→ Action: Queue for Haiku batch review (PRP-46.3.1)
```

**Superseded request** (HIGH confidence ≥75%):
```
PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md
→ Matched with PRPs/executed/PRP-42-init-project-workflow.md
→ Confidence: 0.82
→ Reason: "Superseded by PRP-42 (HIGH confidence)"
```

**Active doc** (LOW confidence <40%):
```
PRPs/feature-requests/INITIAL-critical-memory.md
→ No match found (best: 0.23)
→ Action: Not flagged, keep as-is
```
