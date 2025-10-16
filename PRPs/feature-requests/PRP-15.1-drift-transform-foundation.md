---
name: "Drift Transform Foundation - Report to INITIAL.md Conversion"
description: "Pure transformation function converting drift detection results (violations + missing examples + drift score) into INITIAL.md blueprint format. Foundation for PRP-15.2 remediation workflow."
prp_id: "PRP-15.1"
status: "new"
created_date: "2025-10-15T00:00:00Z"
last_updated: "2025-10-15T00:00:00Z"
updated_by: "generate-prp"
issue: null
context_sync:
  ce_updated: false
  serena_updated: false
  last_sync: null
version: 1
priority: "MEDIUM"
effort_hours: 1.5
risk: "LOW"
dependencies: []
---

# PRP-15.1: Drift Transform Foundation

## 🎯 TL;DR

**Problem**: Drift detection outputs `.ce/drift-report.md` (markdown report format). Future remediation workflow (PRP-15.2) needs INITIAL.md blueprint format for `/generate-prp` integration. Need transformation layer between detection → remediation.

**Solution**: Create `transform_drift_to_initial()` pure function converting violation list + missing examples + drift score → INITIAL.md format. No I/O, no workflow logic - just data transformation following INITIAL.md structure.

**Impact**: Enables automated blueprint generation from drift violations. Foundation for complete remediation workflow. Clear separation of concerns: transform (15.1) → generate PRP (15.2) → workflow automation (15.3).

**Risk**: LOW - Pure function, no side effects, comprehensive tests, isolated from workflow

**Effort**: 1.5h (Transform: 45min, Tests: 30min, Edge cases: 15min)

**Non-Goals**:
- ❌ File I/O operations (caller handles)
- ❌ Drift detection logic (uses existing)
- ❌ PRP generation (PRP-15.2)
- ❌ Workflow integration (PRP-15.3)

---

## 📋 Pre-Execution Context Rebuild

**Complete before implementation:**

- [ ] **Review documentation**:
  - `tmp/INITIAL-15.1-drift-transform.md` (this feature spec)
  - `tools/ce/update_context.py` lines 536-646 (`generate_drift_report` function)
  - `tools/ce/generate.py` lines 29-108 (`parse_initial_md` function)
  - `tools/ce/prp_analyzer.py` lines 85-129 (complexity categorization logic)
  - `PRPs/feature-requests/PRP-15-drift-remediation-workflow.md` (parent PRP)

- [ ] **Verify codebase state**:
  - File exists: `tools/ce/update_context.py` (drift detection + report generation)
  - File exists: `tools/ce/generate.py` (INITIAL.md parsing for reference)
  - File exists: `tools/ce/prp_analyzer.py` (complexity/risk calculation patterns)
  - Directory exists: `tools/tests/` (for unit tests)
  - Example INITIAL files: `tmp/PRP-*-INITIAL.md` (format reference)

- [ ] **Git baseline**: Current branch `feat/context-sync`

- [ ] **Dependencies installed**: `cd tools && uv sync`

---

## 📖 Context

**Related Work**:
- **PRP-1**: Drift detection and DRIFT_JUSTIFICATION format
- **PRP-10**: Drift history tracking and comprehensive testing
- **PRP-15**: Parent PRP for complete remediation workflow
- **Existing drift tooling**: `generate_drift_report()` in `update_context.py`
- **INITIAL.md format**: Defined by `/generate-prp` slash command

**Current State**:
- ✅ Drift detection: `verify_codebase_matches_examples()` returns violations
- ✅ Report generation: `generate_drift_report()` creates markdown
- ✅ Output location: `.ce/drift-report.md` (hidden directory)
- ❌ **Transform missing**: No function to convert report → INITIAL.md
- ❌ **Remediation gap**: Manual interpretation required

**Current Report Format** (from `generate_drift_report()`):

```markdown
## Context Drift Report - Examples/ Patterns

**Drift Score**: 23.4% (⚠️ WARNING)
**Violations Found**: 12
**Missing Examples**: 3

### Part 1: Code Violating Documented Patterns
1. File tools/ce/foo.py has bare_except (violates examples/patterns/error-handling.py): Use specific exception types
2. File tools/ce/bar.py has version_suffix in function name (get_v2_data) (violates examples/patterns/naming.py): Use descriptive names, not versions

### Part 2: Missing Pattern Documentation
1. **PRP-10**: Drift History Tracking
   **Complexity**: high
   **Missing Example**: error_recovery
   **Suggested Path**: examples/patterns/error-recovery.py
   **Rationale**: Complex error recovery logic should be documented
```

**Desired INITIAL.md Format** (for `/generate-prp`):

```markdown
# Drift Remediation - 2025-10-15

## Feature

Address 12 drift violations detected in codebase scan on 2025-10-15.

**Drift Score**: 23.4% (⚠️ WARNING)

**Violations Breakdown**:
- Error Handling: 5
- Naming Conventions: 4
- KISS Violations: 2
- Missing Examples: 3

## Context

Context Engineering drift detection found violations between documented patterns (CLAUDE.md, examples/) and actual implementation.

**Root Causes**:
1. New code written without pattern awareness
2. Missing examples for critical PRPs
3. Pattern evolution without documentation updates

**Impact**:
- Code quality inconsistency
- Reduced onboarding effectiveness
- Pattern erosion over time

## Examples

### Violation 1
File tools/ce/foo.py has bare_except (violates examples/patterns/error-handling.py): Use specific exception types

### Violation 2
File tools/ce/bar.py has version_suffix in function name (get_v2_data) (violates examples/patterns/naming.py): Use descriptive names, not versions

### Missing Examples

**PRP-10**: Drift History Tracking
- **Missing**: `examples/patterns/error-recovery.py`
- **Rationale**: Complex error recovery logic should be documented

## Acceptance Criteria

- [ ] All HIGH priority violations resolved
- [ ] Missing examples created for critical PRPs
- [ ] L4 validation passes (ce validate --level 4)
- [ ] Drift score < 5% after remediation
- [ ] Pattern documentation updated if intentional drift

## Technical Notes

**Files Affected**: 8
**Estimated Effort**: 3h based on violation count
**Complexity**: MEDIUM

**Violation Summary**:
- File tools/ce/foo.py has bare_except
- File tools/ce/bar.py has version_suffix in function name

**Missing Examples Summary**:
- PRP-10: examples/patterns/error-recovery.py
```

**Why This Matters**:
- Foundation for PRP-15.2 automated remediation workflow
- Enables `/generate-prp` integration (takes INITIAL.md as input)
- Clear data transformation without side effects
- Testable in isolation (pure function)

---

## 🔧 Implementation Blueprint

### Phase 1: Transform Function Implementation (45 min)

**Goal**: Create pure transformation function with no I/O or side effects

**Approach**: Single function ~60 lines following KISS guidelines

---

#### Step 1.1: Core Transform Function (30 min)

**Files to Modify**:
- `tools/ce/update_context.py` - Add transformation function

**Implementation**:

```python
def transform_drift_to_initial(
    violations: List[str],
    drift_score: float,
    missing_examples: List[Dict[str, Any]]
) -> str:
    """Transform drift report → INITIAL.md blueprint format.

    Args:
        violations: List of violation messages with format:
                   "File {path} has {issue} (violates {pattern}): {fix}"
        drift_score: Percentage score (0-100)
        missing_examples: List of PRPs missing examples with metadata:
                         [{"prp_id": "PRP-10", "feature_name": "...",
                           "suggested_path": "...", "rationale": "..."}]

    Returns:
        INITIAL.md formatted string with:
        - Feature: Drift summary with breakdown
        - Context: Root causes and impact
        - Examples: Top 5 violations + up to 3 missing examples
        - Acceptance Criteria: Standard remediation checklist
        - Technical Notes: File count, effort estimate, complexity

    Raises:
        ValueError: If violations empty and missing_examples empty
                   If drift_score invalid (not 0-100)

    Example:
        >>> violations = ["File tools/ce/foo.py has bare_except: Use specific"]
        >>> missing = [{"prp_id": "PRP-10", "suggested_path": "ex.py",
        ...            "feature_name": "Feature", "rationale": "Important"}]
        >>> result = transform_drift_to_initial(violations, 12.5, missing)
        >>> assert "# Drift Remediation" in result
        >>> assert "12.5%" in result
        >>> assert "PRP-10" in result
    """
    # NOTE: Import at module level in actual implementation
    from datetime import datetime, timezone

    # Validation
    if not violations and not missing_examples:
        raise ValueError(
            "Cannot generate INITIAL.md: no violations and no missing examples\n"
            "🔧 Troubleshooting: Drift detection returned empty results"
        )

    if not (0 <= drift_score <= 100):
        raise ValueError(
            f"Invalid drift_score: {drift_score} (must be 0-100)\n"
            "🔧 Troubleshooting: Check drift calculation returns percentage"
        )

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Count violations by category (extract pattern from violation string)
    # Pattern format: "(violates examples/patterns/{category}.py)"
    error_handling = len([v for v in violations if "error-handling.py" in v or "error_handling.py" in v])
    naming = len([v for v in violations if "naming.py" in v])
    kiss = len([v for v in violations if "kiss.py" in v or "nesting" in v.lower()])

    # Categorize drift level
    if drift_score < 5:
        drift_level = "✅ OK"
    elif drift_score < 15:
        drift_level = "⚠️ WARNING"
    else:
        drift_level = "🚨 CRITICAL"

    # Calculate effort estimate (15 min per violation + 30 min per missing example)
    effort_hours = (len(violations) * 0.25) + (len(missing_examples) * 0.5)
    effort_hours = max(1, round(effort_hours))  # Minimum 1 hour

    # Calculate complexity
    total_items = len(violations) + len(missing_examples)
    if total_items < 5:
        complexity = "LOW"
    elif total_items < 15:
        complexity = "MEDIUM"
    else:
        complexity = "HIGH"

    # Extract unique file paths for count
    # Expected format: "File {path} has {issue} (violates {pattern}): {fix}"
    files_affected = set()
    for v in violations:
        if "File " in v and " has " in v:
            # Extract file path: "File tools/ce/foo.py has ..."
            try:
                file_part = v.split(" has ")[0].replace("File ", "").strip()
                if file_part:  # Only add non-empty paths
                    files_affected.add(file_part)
            except (IndexError, AttributeError):
                # Malformed violation string, skip gracefully
                continue

    # Build INITIAL.md content
    initial = f"""# Drift Remediation - {now}

## Feature

Address {len(violations)} drift violations detected in codebase scan on {now}.

**Drift Score**: {drift_score:.1f}% ({drift_level})

**Violations Breakdown**:
- Error Handling: {error_handling}
- Naming Conventions: {naming}
- KISS Violations: {kiss}
- Missing Examples: {len(missing_examples)}

## Context

Context Engineering drift detection found violations between documented patterns (CLAUDE.md, examples/) and actual implementation.

**Root Causes**:
1. New code written without pattern awareness
2. Missing examples for critical PRPs
3. Pattern evolution without documentation updates

**Impact**:
- Code quality inconsistency
- Reduced onboarding effectiveness
- Pattern erosion over time

## Examples

"""

    # Add top 5 violations
    for i, violation in enumerate(violations[:5], 1):
        initial += f"### Violation {i}\n\n"
        initial += f"{violation}\n\n"

    # Add missing examples (up to 3)
    if missing_examples:
        initial += "### Missing Examples\n\n"
        for missing in missing_examples[:3]:
            initial += f"**{missing['prp_id']}**: {missing['feature_name']}\n"
            initial += f"- **Missing**: `{missing['suggested_path']}`\n"
            initial += f"- **Rationale**: {missing['rationale']}\n\n"

    # Add Acceptance Criteria
    initial += """## Acceptance Criteria

- [ ] All HIGH priority violations resolved
- [ ] Missing examples created for critical PRPs
- [ ] L4 validation passes (ce validate --level 4)
- [ ] Drift score < 5% after remediation
- [ ] Pattern documentation updated if intentional drift

"""

    # Add Technical Notes with high-level summary
    # Note: Full details already in Examples section, avoid duplication
    initial += f"""## Technical Notes

**Files Affected**: {len(files_affected)}
**Estimated Effort**: {effort_hours}h based on violation count
**Complexity**: {complexity}
**Total Items**: {len(violations)} violations + {len(missing_examples)} missing examples

**Priority Focus**:
- Address HIGH priority violations first
- Create missing examples for critical PRPs
- Run L4 validation after each fix
"""

    return initial
```

**Validation Command**: `cd tools && uv run pytest tests/test_update_context.py::test_transform_drift_to_initial -v`

**Checkpoint**: `git add tools/ce/update_context.py && git commit -m "feat(PRP-15.1): transform drift report to INITIAL.md format"`

---

#### Step 1.2: Input Validation & Edge Cases (15 min)

**Test Cases to Handle**:

1. **Empty violations + empty missing examples**: Should raise ValueError
2. **Invalid drift_score**: Should raise ValueError
3. **Very large violation list**: Should truncate to top 5
4. **Very large missing examples**: Should truncate to top 3
5. **No file paths in violations**: Should handle gracefully
6. **Special characters in paths**: Should preserve as-is

**Enhancement to function** (add at start):

```python
# Additional validation examples in docstring
"""
Edge Cases:
    - Empty violations + empty missing: Raises ValueError
    - drift_score outside 0-100: Raises ValueError
    - More than 5 violations: Shows top 5 only
    - More than 3 missing examples: Shows top 3 only
    - No file paths extractable: files_affected = 0
"""
```

---

### Phase 2: Unit Tests (30 min)

**Goal**: Comprehensive test coverage for transformation function

**Approach**: Test valid input, edge cases, error conditions

---

#### Step 2.1: Core Tests (15 min)

**Files to Create/Modify**:
- `tools/tests/test_update_context.py` - Add transform tests

**Test Implementation**:

```python
def test_transform_drift_to_initial_valid_input():
    """Test drift report → INITIAL.md transformation with valid data."""
    violations = [
        "File tools/ce/foo.py has bare_except (violates examples/patterns/error-handling.py): Use specific exception types",
        "File tools/ce/bar.py has version_suffix in function name (get_v2_data) (violates examples/patterns/naming.py): Use descriptive names"
    ]
    missing = [
        {
            "prp_id": "PRP-10",
            "feature_name": "Drift History Tracking",
            "suggested_path": "examples/patterns/error-recovery.py",
            "rationale": "Critical pattern for context management"
        }
    ]

    result = transform_drift_to_initial(violations, 12.5, missing)

    # Structure checks
    assert "# Drift Remediation" in result
    assert "## Feature" in result
    assert "## Context" in result
    assert "## Examples" in result
    assert "## Acceptance Criteria" in result
    assert "## Technical Notes" in result

    # Content checks
    assert "12.5%" in result
    assert "Address 2 drift violations" in result
    assert "PRP-10" in result
    assert "Drift History Tracking" in result
    assert "examples/patterns/error-recovery.py" in result

    # Breakdown checks
    assert "Error Handling: 1" in result  # error-handling.py pattern
    assert "Naming Conventions: 1" in result  # naming.py pattern

    # Technical notes
    assert "Files Affected: 2" in result  # foo.py and bar.py
    assert "Estimated Effort:" in result
    assert "Complexity:" in result
    assert "Total Items:" in result


def test_transform_structure_sections():
    """Test all required INITIAL.md sections present."""
    violations = ["File test.py has issue: Fix it"]
    result = transform_drift_to_initial(violations, 5.0, [])

    required_sections = [
        "# Drift Remediation",
        "## Feature",
        "## Context",
        "## Examples",
        "## Acceptance Criteria",
        "## Technical Notes"
    ]

    for section in required_sections:
        assert section in result, f"Missing section: {section}"


def test_transform_violation_formatting():
    """Test violation formatting in Examples section."""
    violations = [
        "File a.py has error: Fix A",
        "File b.py has warning: Fix B"
    ]
    result = transform_drift_to_initial(violations, 10.0, [])

    assert "### Violation 1" in result
    assert "File a.py has error: Fix A" in result
    assert "### Violation 2" in result
    assert "File b.py has warning: Fix B" in result


def test_transform_missing_examples_formatting():
    """Test missing examples formatting."""
    missing = [
        {
            "prp_id": "PRP-5",
            "feature_name": "Test Feature",
            "suggested_path": "examples/test.py",
            "rationale": "Important pattern"
        }
    ]
    result = transform_drift_to_initial([], 0.0, missing)

    assert "### Missing Examples" in result
    assert "**PRP-5**: Test Feature" in result
    assert "**Missing**: `examples/test.py`" in result
    assert "**Rationale**: Important pattern" in result
```

**Validation Command**: `cd tools && uv run pytest tests/test_update_context.py::test_transform_drift_to_initial -v`

**Checkpoint**: `git add tools/tests/test_update_context.py && git commit -m "test(PRP-15.1): transform function core tests"`

---

#### Step 2.2: Edge Case Tests (15 min)

**Test Cases**:

```python
def test_transform_empty_inputs_raises():
    """Test transform raises ValueError with empty inputs."""
    with pytest.raises(ValueError) as exc:
        transform_drift_to_initial([], 0.0, [])

    assert "no violations and no missing examples" in str(exc.value)
    assert "🔧 Troubleshooting" in str(exc.value)


def test_transform_invalid_drift_score():
    """Test transform raises ValueError with invalid score."""
    violations = ["File test.py has issue: Fix"]

    # Test negative score
    with pytest.raises(ValueError) as exc:
        transform_drift_to_initial(violations, -5.0, [])
    assert "must be 0-100" in str(exc.value)

    # Test score > 100
    with pytest.raises(ValueError) as exc:
        transform_drift_to_initial(violations, 105.0, [])
    assert "must be 0-100" in str(exc.value)


def test_transform_truncates_violations():
    """Test transform shows top 5 violations only."""
    violations = [f"File test{i}.py has issue{i}: Fix{i}" for i in range(10)]
    result = transform_drift_to_initial(violations, 10.0, [])

    # Should have exactly 5 violations
    assert result.count("### Violation") == 5
    assert "### Violation 1" in result
    assert "### Violation 5" in result
    assert "### Violation 6" not in result

    # Technical notes shows total count
    assert "Address 10 drift violations" in result
    assert "Total Items: 10 violations + 0 missing examples" in result


def test_transform_truncates_missing_examples():
    """Test transform shows top 3 missing examples only."""
    missing = [
        {
            "prp_id": f"PRP-{i}",
            "feature_name": f"Feature {i}",
            "suggested_path": f"examples/test{i}.py",
            "rationale": f"Reason {i}"
        }
        for i in range(6)
    ]
    result = transform_drift_to_initial([], 0.0, missing)

    # Should have exactly 3 missing examples in Examples section
    examples_section = result.split("## Examples")[1].split("## Acceptance")[0]
    assert examples_section.count("**PRP-") == 3

    # Technical Notes shows total count, not individual items
    assert "Total Items: 0 violations + 6 missing examples" in result


def test_transform_effort_calculation():
    """Test effort estimation formula."""
    # 4 violations = 4 * 0.25 = 1h
    # 2 missing examples = 2 * 0.5 = 1h
    # Total = 2h
    violations = [f"File test{i}.py has issue: Fix" for i in range(4)]
    missing = [
        {"prp_id": "PRP-1", "feature_name": "F1", "suggested_path": "e1.py", "rationale": "R1"},
        {"prp_id": "PRP-2", "feature_name": "F2", "suggested_path": "e2.py", "rationale": "R2"}
    ]
    result = transform_drift_to_initial(violations, 10.0, missing)

    assert "Estimated Effort: 2h" in result


def test_transform_complexity_categorization():
    """Test complexity calculation."""
    # LOW: < 5 items
    violations_low = ["File test.py has issue: Fix"]
    result_low = transform_drift_to_initial(violations_low, 5.0, [])
    assert "Complexity: LOW" in result_low

    # MEDIUM: 5-14 items
    violations_medium = [f"File test{i}.py has issue: Fix" for i in range(8)]
    result_medium = transform_drift_to_initial(violations_medium, 10.0, [])
    assert "Complexity: MEDIUM" in result_medium

    # HIGH: 15+ items
    violations_high = [f"File test{i}.py has issue: Fix" for i in range(16)]
    result_high = transform_drift_to_initial(violations_high, 20.0, [])
    assert "Complexity: HIGH" in result_high


def test_transform_drift_level_categories():
    """Test drift level categorization."""
    violations = ["File test.py has issue: Fix"]

    # OK: < 5%
    result_ok = transform_drift_to_initial(violations, 3.0, [])
    assert "✅ OK" in result_ok

    # WARNING: 5-15%
    result_warn = transform_drift_to_initial(violations, 10.0, [])
    assert "⚠️ WARNING" in result_warn

    # CRITICAL: 15%+
    result_crit = transform_drift_to_initial(violations, 20.0, [])
    assert "🚨 CRITICAL" in result_crit


def test_transform_file_count_extraction():
    """Test files_affected count from violation strings."""
    violations = [
        "File tools/ce/foo.py has issue1: Fix",
        "File tools/ce/foo.py has issue2: Fix",  # Same file
        "File tools/ce/bar.py has issue3: Fix"
    ]
    result = transform_drift_to_initial(violations, 10.0, [])

    # Should count unique files only
    assert "Files Affected: 2" in result


def test_transform_no_file_paths():
    """Test graceful handling when violations have no file paths."""
    violations = ["Generic violation without file path"]
    result = transform_drift_to_initial(violations, 5.0, [])

    # Should not crash, files_affected = 0
    assert "Files Affected: 0" in result
```

**Validation Command**: `cd tools && uv run pytest tests/test_update_context.py::test_transform -v`

**Checkpoint**: `git add tools/tests/test_update_context.py && git commit -m "test(PRP-15.1): transform edge case tests"`

---

## ✅ Success Criteria

### Functional Requirements
- [ ] **Transform Function**: `transform_drift_to_initial()` implemented in `update_context.py`
- [ ] **Input Validation**: Raises ValueError for invalid inputs with troubleshooting
- [ ] **INITIAL.md Format**: All 6 required sections present (Feature, Context, Examples, Acceptance Criteria, Technical Notes)
- [ ] **Violation Display**: Shows top 5 violations with clear formatting
- [ ] **Missing Examples**: Shows up to 3 missing examples with metadata
- [ ] **Effort Calculation**: Formula: `violations * 0.25 + missing_examples * 0.5`, min 1h
- [ ] **Complexity Categorization**: LOW (<5), MEDIUM (<15), HIGH (15+) based on total items
- [ ] **Drift Level Labels**: OK (<5%), WARNING (<15%), CRITICAL (15%+)
- [ ] **File Count**: Extracts unique file paths from violations
- [ ] **Function Size**: ≤60 lines following KISS guidelines

### Edge Cases
- [ ] **Empty inputs**: Raises ValueError with troubleshooting
- [ ] **Invalid drift_score**: Raises ValueError for scores outside 0-100
- [ ] **Large violation lists**: Truncates to top 5 in Examples, shows all in Technical Notes
- [ ] **Large missing examples**: Truncates to top 3 in Examples, shows all in Technical Notes
- [ ] **No file paths**: Handles gracefully, files_affected = 0
- [ ] **Special characters**: Preserves paths as-is

### Quality Requirements
- [ ] **Error Messages**: All exceptions include 🔧 troubleshooting guidance
- [ ] **No Fishy Fallbacks**: All errors thrown, not masked
- [ ] **Pure Function**: No I/O, no side effects, no global state
- [ ] **Type Hints**: Proper typing for all parameters and return value
- [ ] **Docstring**: Comprehensive with Args, Returns, Raises, Examples

### Testing Requirements
- [ ] **Core Tests**: Valid input, structure checks, content checks (5 tests)
- [ ] **Edge Case Tests**: Empty inputs, invalid score, truncation, calculation (8 tests)
- [ ] **All Tests Pass**: `pytest tests/test_update_context.py::test_transform -v`
- [ ] **Test Coverage**: ≥90% for `transform_drift_to_initial()` function

---

## 🔍 Validation Gates

### Gate 1: Transform Function (After Step 1.1)

```bash
cd tools && uv run pytest tests/test_update_context.py::test_transform_drift_to_initial_valid_input -v
```

**Expected**: Test passes, INITIAL.md format correct

### Gate 2: Edge Cases (After Step 2.2)

```bash
cd tools && uv run pytest tests/test_update_context.py::test_transform -v
```

**Expected**: All 13 transform tests pass

### Gate 3: Manual Format Check

```bash
cd tools && python3 -c "
from ce.update_context import transform_drift_to_initial
violations = ['File test.py has error: Fix']
missing = [{'prp_id': 'PRP-1', 'feature_name': 'Test', 'suggested_path': 'ex.py', 'rationale': 'Important'}]
print(transform_drift_to_initial(violations, 10.0, missing))
" | head -20
```

**Expected**: Valid INITIAL.md format with all sections

---

## 📚 References

**Existing Code**:
- `tools/ce/update_context.py` lines 536-646 - `generate_drift_report()` function (format reference)
- `tools/ce/generate.py` lines 29-108 - `parse_initial_md()` function (INITIAL.md structure)
- `tools/ce/prp_analyzer.py` lines 85-129 - Complexity/risk calculation patterns

**Related PRPs**:
- PRP-1: Drift detection and DRIFT_JUSTIFICATION format
- PRP-10: Drift history tracking (validation pattern)
- PRP-15: Parent PRP for complete remediation workflow

**INITIAL.md Examples**:
- `tmp/PRP-11-INITIAL.md`
- `tmp/PRP-12-INITIAL.md`
- `tmp/PRP-13-INITIAL.md`

---

## 🎯 Definition of Done

- [ ] `transform_drift_to_initial()` function implemented (~60 lines)
- [ ] Input validation with troubleshooting guidance
- [ ] All 6 INITIAL.md sections generated correctly
- [ ] Top 5 violations displayed with formatting
- [ ] Up to 3 missing examples displayed
- [ ] Effort calculation: `violations * 0.25 + missing * 0.5`, min 1h
- [ ] Complexity categorization: LOW/MEDIUM/HIGH
- [ ] Drift level labeling: OK/WARNING/CRITICAL
- [ ] File count extraction from violation strings
- [ ] 13 unit tests pass (5 core + 8 edge cases)
- [ ] Test coverage ≥90% for transform function
- [ ] No fishy fallbacks - all errors thrown
- [ ] Pure function - no I/O or side effects
- [ ] Comprehensive docstring with examples
- [ ] Git commits: 2 logical commits (function + tests)

**Estimated Total Effort**: 1.5h (Transform: 45min, Tests: 30min, Edge cases: 15min)

**Deferred to PRP-15.2**:
- File I/O operations (`tmp/ce/DEDRIFT-INITIAL.md` writing)
- PRP generation integration
- Workflow orchestration

**Deferred to PRP-15.3**:
- CLI flag integration (`--remediate`)
- Approval gate logic
- Auto-execution

---

## 📝 Appendix: Review History

### Peer Review #1 - Document Quality (2025-10-16T19:30:00Z)

**Reviewer**: Context-Naive Peer Review Agent

**Issues Found & Fixed**:
1. ✅ **YAML Header**: Added missing `last_sync: null` to `context_sync` block
2. ✅ **Categorization Logic**: Changed from naive string matching to pattern file detection (`error-handling.py`, `naming.py`)
3. ✅ **Import Location**: Added note to move `datetime` import to module level
4. ✅ **File Path Extraction**: Added try-except for malformed violation strings, prevents crashes
5. ✅ **Test Assertion**: Fixed `"2 drift violations"` → `"Address 2 drift violations"` to match template
6. ✅ **Technical Notes Duplication**: Removed redundant violation/example lists, replaced with high-level summary
7. ✅ **Updated Tests**: All 13 tests updated to match new Technical Notes format

**Quality Assessment**: HIGH - Comprehensive implementation with clear separation of concerns, excellent testing coverage, realistic effort estimates.

**Ready for Execution**: ✅ YES

---

**PRP-15.1 Ready for Execution** ✅
