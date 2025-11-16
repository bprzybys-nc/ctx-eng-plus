---
prp_id: 46.0.1
feature_name: CleanupCandidate Base Class Updates for NLP Support
batch_id: 46
stage: 0
order: 1
status: completed
created: 2025-11-16T00:00:00Z
updated: 2025-11-16T12:00:00Z
completed: 2025-11-16T12:00:00Z
commit: 7957f49
complexity: low
estimated_hours: 0.5
dependencies: None (must execute FIRST before batch 46)
---

# CleanupCandidate Base Class Updates for NLP Support

## 1. TL;DR

**Objective**: Update `CleanupCandidate` dataclass in base.py to support NLP-powered vacuum features

**What**: Add 2 new optional fields (`superseded_by`, `detection_type`) and change `confidence` type from `int` to `float`

**Why**: Batch 46 PRPs (46.1.1-46.4.1) depend on these fields but base class doesn't define them, causing runtime failures

**Effort**: 0.5 hours (LOW complexity, simple dataclass update + test verification)

**Dependencies**: NONE - This PRP MUST execute FIRST before any other batch 46 PRP

## 2. Context

### Background

Current `CleanupCandidate` dataclass (from `tools/ce/vacuum_strategies/base.py`):

```python
@dataclass
class CleanupCandidate:
    """Represents a file candidate for cleanup."""

    path: Path
    reason: str
    confidence: int  # 0-100 percentage
    size_bytes: int
    last_modified: Optional[datetime]
    git_history: Optional[str]
```

**Problems**:

1. **Missing `superseded_by` field**: PRP-46.2.1 (PRPLifecycleDocsStrategy) and PRP-46.3.1 (LLMBatchAnalyzer) check `if hasattr(candidate, 'superseded_by')` but field doesn't exist in base class
2. **Missing `detection_type` field**: PRP-46.2.1 sets detection_type ("INITIAL→PRP", "Temporary→PRP", "Superseded") but field not in base class
3. **Type mismatch for `confidence`**: PRP-46.3.1 uses float ranges (0.4-0.7) but base class defines `int`, causing type inconsistencies

### Constraints and Considerations

**Backward Compatibility**:
- Existing strategies use `confidence` as int (0-100)
- New strategies use `confidence` as float (0.0-1.0)
- Python's duck typing allows both, but should standardize

**Testing Requirements**:
- All existing vacuum tests must pass after changes
- No regression in existing strategies (TempFileStrategy, BackupFileStrategy, etc.)

### Documentation References

**Base Class Location**:
- `tools/ce/vacuum_strategies/base.py` (lines 10-25)

**Dependent PRPs**:
- PRP-46.2.1: PRPLifecycleDocsStrategy (uses `superseded_by`, `detection_type`)
- PRP-46.3.1: LLMBatchAnalyzer (uses float confidence, checks `superseded_by`)
- PRP-46.4.1: Integration tests (assumes these fields exist)

## 3. Implementation Steps

### Phase 1: Update CleanupCandidate Dataclass (15 min)

**Step 1: Read Current Base Class**

```bash
cat tools/ce/vacuum_strategies/base.py
```

**Step 2: Update Dataclass Definition**

Modify `tools/ce/vacuum_strategies/base.py` (around line 10-25):

```python
@dataclass
class CleanupCandidate:
    """Represents a file candidate for cleanup.

    Attributes:
        path: Path to file candidate
        reason: Human-readable reason for flagging
        confidence: Confidence score (0.0-1.0 float or 0-100 int, both supported)
        size_bytes: File size in bytes
        last_modified: Last modification timestamp
        git_history: Git history summary
        superseded_by: Path to PRP that supersedes this doc (NLP feature, batch 46)
        detection_type: Detection category (NLP feature, batch 46)
            - "INITIAL→PRP": INITIAL.md that became formal PRP
            - "Temporary→PRP": PLAN/ANALYSIS/REPORT integrated into PRP
            - "Superseded": Feature request superseded by executed PRP
    """

    path: Path
    reason: str
    confidence: float  # Changed from int to float (supports 0.0-1.0 and 0-100 ranges)
    size_bytes: int
    last_modified: Optional[datetime]
    git_history: Optional[str]

    # NEW fields for NLP-powered detection (batch 46)
    superseded_by: Optional[Path] = None  # Path to PRP that supersedes this doc
    detection_type: Optional[str] = None  # "INITIAL→PRP", "Temporary→PRP", "Superseded"
```

### Phase 2: Verify Existing Strategies (15 min)

**Step 3: Check Confidence Type Usage in Existing Strategies**

Run grep to find all confidence assignments:

```bash
cd tools
grep -n "confidence=" ce/vacuum_strategies/*.py
```

Expected results:
- Most strategies use integer values (50, 60, 70, 80, 90, 100)
- These will auto-convert to float (50 → 50.0)
- No code changes needed for existing strategies

**Step 4: Run Existing Tests**

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py -v
```

Expected: All tests PASS (confidence int→float conversion is transparent)

### Phase 3: Update Related Tests (10 min)

**Step 5: Update Test Fixtures if Needed**

Check if any test fixtures create CleanupCandidate with positional args (would break):

```bash
cd tools
grep -n "CleanupCandidate(" tests/test_vacuum_strategies.py
```

If found, update to use keyword arguments:

```python
# Before (positional args - BREAKS with new fields)
candidate = CleanupCandidate(path, reason, 70, size, mtime, history)

# After (keyword args - SAFE)
candidate = CleanupCandidate(
    path=path,
    reason=reason,
    confidence=70,  # Auto-converts to 70.0
    size_bytes=size,
    last_modified=mtime,
    git_history=history
)
```

## 4. Validation Gates

### Gate 1: Dataclass Fields Added

**Command**:

```bash
cd tools
python3 -c "from ce.vacuum_strategies.base import CleanupCandidate; import inspect; print([f.name for f in inspect.signature(CleanupCandidate).parameters.values()])"
```

**Expected Output**:

```
['path', 'reason', 'confidence', 'size_bytes', 'last_modified', 'git_history', 'superseded_by', 'detection_type']
```

**Validates**: AC1 - All 8 fields present (6 original + 2 new)

---

### Gate 2: Confidence Type is Float

**Command**:

```bash
cd tools
python3 -c "from ce.vacuum_strategies.base import CleanupCandidate; import inspect; sig = inspect.signature(CleanupCandidate); print(sig.parameters['confidence'].annotation)"
```

**Expected Output**:

```
<class 'float'>
```

**Validates**: AC2 - Confidence type changed from int to float

---

### Gate 3: Existing Tests Pass

**Command**:

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py -v
```

**Expected Output**:

```
All tests PASSED (no regressions)
```

**Validates**: AC3 - No breaking changes to existing strategies

---

### Gate 4: New Fields Are Optional

**Command**:

```bash
cd tools
python3 -c "from ce.vacuum_strategies.base import CleanupCandidate; from pathlib import Path; c = CleanupCandidate(path=Path('test.md'), reason='test', confidence=50.0, size_bytes=100, last_modified=None, git_history=None); print(f'superseded_by={c.superseded_by}, detection_type={c.detection_type}')"
```

**Expected Output**:

```
superseded_by=None, detection_type=None
```

**Validates**: AC4 - New fields default to None (optional)

## 5. Testing Strategy

### Test Framework

pytest + manual Python REPL verification

### Test Command

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py -v
```

### Test Cases

**Test 1: Backward Compatibility with Int Confidence** (manual)

```python
from ce.vacuum_strategies.base import CleanupCandidate
from pathlib import Path

# Old style: int confidence
c = CleanupCandidate(
    path=Path("test.md"),
    reason="test",
    confidence=70,  # int, auto-converts to 70.0
    size_bytes=100,
    last_modified=None,
    git_history=None
)

assert isinstance(c.confidence, float)
assert c.confidence == 70.0
print("✓ Int confidence auto-converts to float")
```

**Test 2: New Fields Optional** (manual)

```python
from ce.vacuum_strategies.base import CleanupCandidate
from pathlib import Path

# Create candidate without new fields
c = CleanupCandidate(
    path=Path("test.md"),
    reason="test",
    confidence=50.0,
    size_bytes=100,
    last_modified=None,
    git_history=None
)

assert c.superseded_by is None
assert c.detection_type is None
print("✓ New fields default to None")
```

**Test 3: New Fields Can Be Set** (manual)

```python
from ce.vacuum_strategies.base import CleanupCandidate
from pathlib import Path

# Create candidate with new fields
c = CleanupCandidate(
    path=Path("test.md"),
    reason="test",
    confidence=85.0,
    size_bytes=100,
    last_modified=None,
    git_history=None,
    superseded_by=Path("PRP-23.md"),
    detection_type="INITIAL→PRP"
)

assert c.superseded_by == Path("PRP-23.md")
assert c.detection_type == "INITIAL→PRP"
print("✓ New fields can be set")
```

**Test 4: Existing Tests Still Pass** (pytest)

```bash
cd tools
uv run pytest tests/test_vacuum_strategies.py -v
```

Expected: All tests PASS

### Test Coverage Target

- 100% backward compatibility with existing strategies
- All 4 validation gates pass
- Manual tests confirm new fields work correctly

## 6. Rollout Plan

### Phase 1: Development (0.5 hours)

**Tasks**:

1. Update `tools/ce/vacuum_strategies/base.py` (15 min)
2. Run existing tests to verify no regressions (15 min)
3. Manual REPL tests for new fields (10 min)

**Validation**: All 4 validation gates pass

### Phase 2: Verification (10 min)

**Tasks**:

1. Verify all existing strategies still work
2. Check test fixtures for positional arg usage
3. Run full vacuum test suite

**Success Criteria**:

- All tests pass
- No code changes needed in existing strategies
- New fields available for batch 46 PRPs

### Phase 3: Execution Order (5 min)

**Tasks**:

1. Commit changes with message: "PRP-46.0.1: Update CleanupCandidate for NLP support"
2. Verify batch 46 PRPs can now access new fields

**Next Steps**:

- Execute PRP-46.1.1 (NLP Foundation)
- Execute PRP-46.2.1 (PRP Lifecycle Docs) - uses new fields
- Execute PRP-46.2.2 (Enhance Strategies)
- Execute PRP-46.3.1 (LLM Batch) - uses float confidence
- Execute PRP-46.4.1 (Integration)

---

## Research Findings

### Current Base Class Structure

From `tools/ce/vacuum_strategies/base.py` (lines 10-25):

```python
@dataclass
class CleanupCandidate:
    """Represents a file candidate for cleanup."""

    path: Path
    reason: str
    confidence: int
    size_bytes: int
    last_modified: Optional[datetime]
    git_history: Optional[str]
```

### Existing Strategies Confidence Usage

**TempFileStrategy**: Uses int (50, 90, 95)
**BackupFileStrategy**: Uses int (80, 95)
**ObsoleteDocStrategy**: Uses int (55, 70)
**OrphanTestStrategy**: Uses int (40, 60)

All will auto-convert to float without code changes.

### Python Dataclass Field Defaults

Adding optional fields with defaults is safe:

```python
# Before
@dataclass
class Foo:
    a: int
    b: str

# After (backward compatible)
@dataclass
class Foo:
    a: int
    b: str
    c: Optional[str] = None  # NEW field, optional
```

Old code: `Foo(a=1, b="x")` still works (c defaults to None)
New code: `Foo(a=1, b="x", c="y")` also works

### Type Compatibility

Python's duck typing allows `confidence: float` to accept both int and float:

```python
c = CleanupCandidate(confidence=70)  # int → auto-converts to 70.0
c = CleanupCandidate(confidence=0.85)  # float → stays 0.85
```

No breaking changes for existing code.
