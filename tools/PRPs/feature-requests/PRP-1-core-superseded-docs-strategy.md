---
prp_id: TBD
feature_name: Core Superseded Docs Strategy
status: pending
created: 2025-11-16T15:26:04.447537
updated: 2025-11-16T15:26:04.447537
complexity: medium
estimated_hours: 3-5
dependencies: Fuzzy, File, YAML
issue: PRP-1-created
---

# Core Superseded Docs Strategy

## 1. TL;DR

**Objective**: Core Superseded Docs Strategy

**What**: Implement Python-based fuzzy matching to automatically detect feature-request documents that have been superseded by executed PRPs.

**Goal**: Reduce manual review by detecting superseded docs with 40...

**Why**: Enable functionality described in INITIAL.md with 6 reference examples

**Effort**: Medium (3-5 hours estimated based on complexity)

**Dependencies**: Fuzzy, File, YAML


## 2. Context

### Background

Implement Python-based fuzzy matching to automatically detect feature-request documents that have been superseded by executed PRPs.

**Goal**: Reduce manual review by detecting superseded docs with 40-85% confidence using deterministic Python analysis.

**Acceptance Criteria**:
1. Create `SupersededDocsStrategy` class extending `VacuumStrategy`
2. Extract titles from markdown headers for fuzzy matching
3. Implement fuzzy matching using `difflib.SequenceMatcher` (≥80% similarity threshold)
4. Parse YAML frontmatter to compare dates (feature-request must be older than PRP)
5. Detect explicit PRP references in content ("See PRP-42", "Implemented in PRP-42")
6. Implement related docs detection:
   - Scan all executed PRPs for .md filename mentions
   - Build reverse index: {filename: [PRPs that mention it]}
   - Boost confidence by +30% if feature-request mentioned in PRP
7. Return candidates with 40-85% confidence scores
8. Register strategy in `tools/ce/vacuum.py`

**Test Cases**:
- Should detect: `INIT-PROJECT-WORKFLOW-INITIAL.md` → matches PRP-42 (≥85%)
- Should NOT flag: `INITIAL-critical-memory-consolidation.md` (no matching PRP)

### Constraints and Considerations

**Security**:
- All file operations use pathlib (no shell execution)
- YAML parsing uses safe_load (prevents arbitrary code execution)

**Performance**:
- Fuzzy matching on titles only (not full content) - O(n*m) where n=feature-requests, m=executed PRPs
- Expected: ~50 feature-requests × ~45 executed PRPs = 2,250 comparisons
- SequenceMatcher is fast for short strings (< 1ms per comparison)
- Total scan time: < 3 seconds

**Edge Cases**:
1. **Missing YAML headers**: Fallback to filename-based date extraction (PRP-XX format implies order)
2. **Duplicate titles**: Use date comparison as tiebreaker (older doc is candidate)
3. **Partial matches**: Require ≥80% similarity to avoid false positives
4. **Self-references**: Ignore if feature-request mentions its own filename

**File Paths**:
- New file: `tools/ce/vacuum_strategies/superseded_docs.py`
- Modified: `tools/ce/vacuum.py` (import + register strategy)
- Tests: `tools/tests/test_vacuum_superseded.py` (new)

**Dependencies**:
- None (Phase 1 is standalone)
- Phase 2 will extend this class with LLM analysis

**Estimated Hours**: 2 hours
- 0.5h: Strategy skeleton + title extraction
- 0.5h: Fuzzy matching + date comparison
- 0.5h: Related docs detection (reverse index)
- 0.5h: Unit tests + integration

### Documentation References

- Fuzzy (library documentation)
- File (library documentation)
- YAML (library documentation)
- Regular (library documentation)
- Test (library documentation)
- Unit (library documentation)
- Init (library documentation)


## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (2-3 hours)

1. Implement python component
2. Implement python component
3. Implement python component

### Phase 3: Testing and Validation (1-2 hours)

1. Write unit tests following project patterns
2. Write integration tests
3. Run validation gates
4. Update documentation


## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**: `uv run pytest tests/unit/ -v`

**Success Criteria**:
- All new unit tests pass
- Existing tests not broken
- Code coverage ≥ 80%

### Gate 2: Integration Tests Pass

**Command**: `uv run pytest tests/integration/ -v`

**Success Criteria**:
- Integration tests verify end-to-end functionality
- No regressions in existing features

### Gate 3: Acceptance Criteria Met

**Verification**: Manual review against INITIAL.md requirements

**Success Criteria**:

- Requirements from INITIAL.md validated


## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
uv run pytest tests/ -v
```

### Coverage Requirements

- Unit test coverage: ≥ 80%
- Integration tests for critical paths
- Edge cases from INITIAL.md covered


## 6. Rollout Plan

### Phase 1: Development

1. Implement core functionality
2. Write tests
3. Pass validation gates

### Phase 2: Review

1. Self-review code changes
2. Peer review (optional)
3. Update documentation

### Phase 3: Deployment

1. Merge to main branch
2. Monitor for issues
3. Update stakeholders


---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: 0
- **Test Patterns**: 1
- **Serena Available**: False

### Documentation Sources
- **Library Docs**: 0
- **External Links**: 0
- **Context7 Available**: False
