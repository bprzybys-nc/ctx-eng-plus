---
context_sync:
  ce_updated: true
  last_sync: '2025-10-17T10:44:01.088936+00:00'
  serena_updated: false
created_date: '2025-10-16T00:00:00Z'
dependencies:
- PRP-15.1
description: Create blueprint generation system that detects drift violations, generates
  DEDRIFT-INITIAL.md in tmp/ce/ directory, and creates system PRP YAML headers. Foundation
  for PRP-15.3 workflow automation.
effort_hours: 2
issue: null
last_updated: '2025-10-16T00:00:00Z'
name: Drift Blueprint Generation - Detection to File Creation
priority: MEDIUM
prp_id: PRP-15.2
risk: LOW
status: new
updated: '2025-10-17T10:44:01.088939+00:00'
updated_by: update-context-command
version: 1
---

# PRP-15.2: Drift Blueprint Generation

## 🎯 TL;DR

**Problem**: Drift detection runs in `update_context.py` but produces only markdown reports (`.ce/drift-report.md`). No automation for creating remediation blueprints (DEDRIFT-INITIAL.md files) or generating system PRP metadata. Manual copy-paste required to start remediation workflow.

**Solution**: Implement 4 focused functions (~25-40 lines each) for drift blueprint generation:
- `detect_drift_violations()` - Wrapper for drift detection with error handling
- `generate_drift_blueprint()` - Create `tmp/ce/DEDRIFT-INITIAL.md` file using PRP-15.1 transform
- `display_drift_summary()` - Show drift breakdown with direct output (no box-drawing)
- `generate_prp_yaml_header()` - Create metadata for system PRPs with effort/risk estimates

**Impact**: Enables automated remediation workflows (PRP-15.3). Makes drift blueprints discoverable in `tmp/ce/`. Provides effort estimation for system PRPs. Clear separation: detection → blueprint → workflow.

**Risk**: LOW - Simple file generation, uses proven patterns from existing codebase, comprehensive tests

**Effort**: 2h (Functions: 1h, Tests: 45min, Integration: 15min)

**Non-Goals**:
- ❌ Workflow orchestration (PRP-15.3)
- ❌ CLI integration (PRP-15.3)
- ❌ Approval gates (PRP-15.3)
- ❌ PRP file generation (PRP-15.3)
- ❌ Execution automation (PRP-15.3)

---

## 📋 Pre-Execution Context Rebuild

**Complete before implementation:**

- [ ] **Review documentation**:
  - `tmp/INITIAL-15.2-blueprint-generation.md` (this feature spec)
  - `PRPs/feature-requests/PRP-15.1-drift-transform-foundation.md` (dependency - transform function)
  - `tools/ce/update_context.py` lines 403-533 (drift detection functions)
  - `tools/ce/update_context.py` lines 536-646 (`generate_drift_report` function)
  - `PRPs/executed/PRP-14-update-context-slash-command.md` (drift detection context)

- [ ] **Verify codebase state**:
  - File exists: `tools/ce/update_context.py` (target implementation file)
  - Functions exist: `verify_codebase_matches_examples()`, `detect_missing_examples_for_prps()`
  - Directory exists: `tools/tests/` (for unit tests)
  - Test file: `tools/tests/test_update_context.py` (add new tests here)
  - PRP-15.1 status: Verify `transform_drift_to_initial()` function is implemented

- [ ] **Git baseline**: Current branch `feat/context-sync`

- [ ] **Dependencies installed**: `cd tools && uv sync`

- [ ] **PRP-15.1 verification**:
  ```bash
  cd tools && python3 -c "from ce.update_context import transform_drift_to_initial; print('✅ PRP-15.1 ready')" || echo "❌ PRP-15.1 missing - implement first"
  ```

---

## 📖 Context

**Related Work**:
- **PRP-15.1**: Provides `transform_drift_to_initial()` function (REQUIRED dependency)
- **PRP-14**: Implemented `/update-context` command with drift detection
- **PRP-10**: Drift history tracking and comprehensive testing patterns
- **PRP-1**: Original drift detection and DRIFT_JUSTIFICATION format

**Current State**:
- ✅ Drift detection: `verify_codebase_matches_examples()` returns structured violations
- ✅ Missing examples detection: `detect_missing_examples_for_prps()` identifies gaps
- ✅ Report generation: `generate_drift_report()` creates markdown reports
- ✅ Output location: `.ce/drift-report.md` (hidden directory, markdown format)
- ❌ **Blueprint automation missing**: No function to generate DEDRIFT-INITIAL.md files
- ❌ **Visibility gap**: Blueprints not discoverable in tmp/ directory
- ❌ **Metadata missing**: System PRPs lack effort/risk estimates

**Current Drift Detection Output** (from `verify_codebase_matches_examples()`):

```python
{
    "violations": [
        "File tools/ce/foo.py has bare_except (violates examples/patterns/error-handling.py): Use specific exception types",
        "File tools/ce/bar.py has version_suffix in function name (get_v2_data): Use descriptive names"
    ],
    "drift_score": 23.4  # Percentage of files violating patterns
}
```

**Current Missing Examples Output** (from `detect_missing_examples_for_prps()`):

```python
[
    {
        "prp_id": "PRP-10",
        "feature_name": "Drift History Tracking",
        "complexity": "high",
        "missing_example": "error_recovery",
        "suggested_path": "examples/patterns/error-recovery.py",
        "rationale": "Complex error recovery logic should be documented"
    }
]
```

**Target INITIAL.md Format** (PRP-15.1 output):

```markdown
# Drift Remediation - Context Pattern Alignment

## Feature

Address drift violations detected in codebase scan. Restore alignment between codebase and documented patterns in examples/ directory.

## Context

**Drift Score**: 23.4% (⚠️ WARNING)
**Total Items**: 5 violations + 2 missing examples = 7 items

### Code Violations
1. Error Handling: tools/ce/foo.py - bare_except
2. Naming: tools/ce/bar.py - version_suffix

### Missing Documentation
1. PRP-10: error_recovery example missing
2. PRP-13: strategy_pattern example missing

## Examples

[Generated solution examples for each violation]

## Acceptance Criteria

- [ ] All code violations fixed
- [ ] All missing examples created
- [ ] ce validate --level 4 passes
- [ ] Drift score < 5%
```

**Why Blueprint Generation Matters**:

1. **Automation Foundation**: Enables PRP-15.3 workflow automation
2. **Discoverability**: `tmp/ce/` location makes blueprints visible (unlike hidden `.ce/` reports)
3. **Standardization**: INITIAL.md format works with existing `/generate-prp` command
4. **Effort Estimation**: YAML headers enable resource planning for system PRPs
5. **Clear Separation**: Detection (PRP-14) → Blueprint (PRP-15.2) → Workflow (PRP-15.3)

---

## 🏗️ Implementation Blueprint

### Phase 1: Drift Detection Wrapper (~25 lines, 20 min)

**Function**: `detect_drift_violations()`

**Location**: `tools/ce/update_context.py`

**Purpose**: Wrap existing drift detection with error handling and structured output

**Implementation Pattern** (from codebase):

```python
def detect_drift_violations() -> Dict[str, Any]:
    """Run drift detection and return structured results.

    Returns:
        {
            "drift_score": 12.5,
            "violations": ["file.py:42 - Error", "util.py:15 - Naming"],
            "missing_examples": [{"prp_id": "PRP-10", ...}],
            "has_drift": True
        }

    Raises:
        RuntimeError: If detection fails with troubleshooting guidance

    Example:
        >>> result = detect_drift_violations()
        >>> assert "drift_score" in result
        >>> assert isinstance(result["violations"], list)
    """
    logger.info("Running drift detection...")
    try:
        # Call existing detection functions
        drift_result = verify_codebase_matches_examples()
        missing_examples = detect_missing_examples_for_prps()

        drift_score = drift_result["drift_score"]
        violations = drift_result["violations"]
        has_drift = drift_score >= 5 or len(missing_examples) > 0

        return {
            "drift_score": drift_score,
            "violations": violations,
            "missing_examples": missing_examples,
            "has_drift": has_drift
        }
    except Exception as e:
        raise RuntimeError(
            f"Drift detection failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Ensure examples/ directory exists\n"
            f"   - Check PRPs have valid YAML headers\n"
            f"   - Verify tools/ce/ directory is accessible\n"
            f"   - Run: cd tools && uv run ce validate --level 1"
        )
```

**Key Patterns from Codebase**:
- Error handling pattern from `read_prp_header()` (lines 37-69)
- Project root detection from `verify_codebase_matches_examples()` (lines 415-419)
- Structured return dict from `sync_context()` (lines 649-665)

**Validation Gates**:
- [ ] Function returns dict with all required keys
- [ ] `has_drift` correctly calculated (score >= 5 OR missing_examples > 0)
- [ ] RuntimeError includes troubleshooting guidance
- [ ] No fishy fallbacks (let exceptions propagate)
- [ ] Unit test: successful detection
- [ ] Unit test: detection failure with helpful error

---

### Phase 2: Blueprint File Generation (~35 lines, 20 min)

**Function**: `generate_drift_blueprint()`

**Location**: `tools/ce/update_context.py`

**Purpose**: Create `tmp/ce/DEDRIFT-INITIAL.md` using PRP-15.1 transform function

**Implementation Pattern**:

```python
def generate_drift_blueprint(drift_result: Dict, missing_examples: List) -> Path:
    """Generate DEDRIFT-INITIAL.md blueprint in tmp/ce/.

    Args:
        drift_result: Detection results from detect_drift_violations()
        missing_examples: List of PRPs missing examples

    Returns:
        Path to generated blueprint file

    Raises:
        RuntimeError: If blueprint generation fails

    Example:
        >>> drift = detect_drift_violations()
        >>> missing = drift["missing_examples"]
        >>> path = generate_drift_blueprint(drift, missing)
        >>> assert path.exists()
        >>> assert "DEDRIFT-INITIAL.md" in path.name
    """
    logger.info("Generating remediation blueprint...")
    try:
        # Use PRP-15.1 transform function
        blueprint = transform_drift_to_initial(
            drift_result["violations"],
            drift_result["drift_score"],
            missing_examples
        )

        # Determine project root
        current_dir = Path.cwd()
        if current_dir.name == "tools":
            project_root = current_dir.parent
        else:
            project_root = current_dir

        # Create tmp/ce/ directory
        tmp_ce_dir = project_root / "tmp" / "ce"
        tmp_ce_dir.mkdir(parents=True, exist_ok=True)

        # Write blueprint
        blueprint_path = tmp_ce_dir / "DEDRIFT-INITIAL.md"
        blueprint_path.write_text(blueprint)

        logger.info(f"Blueprint generated: {blueprint_path}")
        return blueprint_path

    except Exception as e:
        raise RuntimeError(
            f"Blueprint generation failed: {e}\n"
            f"🔧 Troubleshooting:\n"
            f"   - Check tmp/ce/ directory permissions\n"
            f"   - Verify transform_drift_to_initial() is available (PRP-15.1)\n"
            f"   - Check disk space: df -h\n"
            f"   - Run: ls -la {project_root / 'tmp'}"
        )
```

**Key Patterns from Codebase**:
- Directory creation: `mkdir(parents=True, exist_ok=True)` (standard Python pattern)
- Project root detection: from `verify_codebase_matches_examples()` (lines 415-419)
- Path return pattern: from `move_prp_to_executed()` (returns new Path)
- File writing: `path.write_text()` (standard Python pathlib)

**Validation Gates**:
- [ ] Creates `tmp/ce/` directory if missing
- [ ] Generates `DEDRIFT-INITIAL.md` file
- [ ] Returns Path object to generated file
- [ ] Works from both project root and tools/ directory
- [ ] RuntimeError includes troubleshooting guidance
- [ ] No silent failures
- [ ] Unit test: successful generation
- [ ] Unit test: directory creation
- [ ] Unit test: permission errors handled

---

### Phase 3: Drift Summary Display (~32 lines, 15 min)

**Function**: `display_drift_summary()`

**Location**: `tools/ce/update_context.py`

**Purpose**: Display drift breakdown with direct output (no box-drawing characters)

**Implementation Pattern**:

```python
def display_drift_summary(drift_score: float, violations: List[str],
                          missing_examples: List[Dict], blueprint_path: Path):
    """Display drift summary with direct output (no box-drawing).

    Args:
        drift_score: Percentage score (0-100)
        violations: List of violation messages
        missing_examples: List of PRPs missing examples
        blueprint_path: Path to generated blueprint

    Example:
        >>> display_drift_summary(12.5, violations, missing, path)
        # Prints:
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # 📊 Drift Summary
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # Drift Score: 12.5% (⚠️ WARNING)
        # Total Violations: 5
        # ...
    """
    print("\n" + "━" * 60)
    print("📊 Drift Summary")
    print("━" * 60)

    # Drift level indicator
    level = "⚠️ WARNING" if drift_score < 15 else "🚨 CRITICAL"
    print(f"Drift Score: {drift_score:.1f}% ({level})")
    print(f"Total Violations: {len(violations) + len(missing_examples)}")
    print()

    # Breakdown by category
    # NOTE: Extract pattern from violation string format: "(violates examples/patterns/{category}.py)"
    print("Breakdown:")
    if violations:
        # Categorize violations using pattern file detection (consistent with PRP-15.1)
        error_count = len([v for v in violations if "error-handling.py" in v or "error_handling.py" in v])
        naming_count = len([v for v in violations if "naming.py" in v])
        kiss_count = len([v for v in violations if "kiss.py" in v or "nesting" in v.lower()])

        if error_count > 0:
            print(f"  • Error Handling: {error_count} violation{'s' if error_count != 1 else ''}")
        if naming_count > 0:
            print(f"  • Naming Conventions: {naming_count} violation{'s' if naming_count != 1 else ''}")
        if kiss_count > 0:
            print(f"  • KISS Violations: {kiss_count} violation{'s' if kiss_count != 1 else ''}")

    if missing_examples:
        print(f"  • Missing Examples: {len(missing_examples)} PRP{'s' if len(missing_examples) != 1 else ''}")

    print()
    print(f"Blueprint: {blueprint_path}")
    print("━" * 60)
    print()
```

**Key Patterns from Codebase**:
- Direct print output (no box-drawing): Simple, reliable, works everywhere
- Unicode separators: `"━" * 60` (clean visual separation)
- Emoji indicators: `⚠️` `🚨` `📊` (visual clarity)
- Categorization logic: from `generate_drift_report()` (lines 566-586)
- Pluralization: `{'s' if count != 1 else ''}` (grammatically correct)

**Validation Gates**:
- [ ] Direct print statements (no box-drawing characters)
- [ ] Shows drift score with level indicator
- [ ] Breakdown by violation categories (error, naming, kiss)
- [ ] Missing examples count displayed
- [ ] Blueprint path shown
- [ ] Clean visual separation with Unicode
- [ ] Integration test: full display output
- [ ] Test: categorization accuracy

---

### Phase 4: System PRP YAML Header Generation (~40 lines, 15 min)

**Function**: `generate_prp_yaml_header()`

**Location**: `tools/ce/update_context.py`

**Purpose**: Generate metadata for DEDRIFT system PRPs with effort/risk estimates

**Implementation Pattern**:

```python
def generate_prp_yaml_header(violation_count: int, missing_count: int, timestamp: str) -> str:
    """Generate YAML header for DEDRIFT maintenance PRP.

    Args:
        violation_count: Number of code violations
        missing_count: Number of missing examples
        timestamp: Formatted timestamp for PRP ID (e.g., "20251015-120530")

    Returns:
        YAML header string with metadata

    Example:
        >>> header = generate_prp_yaml_header(5, 2, "20251015-120530")
        >>> assert "prp_id:" in header
        >>> assert "DEDRIFT-20251015-120530" in header
        >>> assert "effort_hours:" in header
    """
    # NOTE: Import at module level in actual implementation
    from datetime import datetime

    total_items = violation_count + missing_count

    # Effort estimation: 15 min per violation + 30 min per missing example
    # NOTE: Same formula as PRP-15.1 transform function for consistency
    effort_hours = (violation_count * 0.25) + (missing_count * 0.5)
    effort_hours = max(1, round(effort_hours))  # Minimum 1 hour

    # Risk assessment based on item count
    if total_items < 5:
        risk = "LOW"
    elif total_items < 10:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    now = datetime.now().isoformat()

    return f"""---
name: "Drift Remediation - {timestamp}"
description: "Address drift violations detected in codebase scan"
prp_id: "DEDRIFT-{timestamp}"
status: "new"
created_date: "{now}Z"
last_updated: "{now}Z"
updated_by: "drift-remediation-workflow"
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
priority: "MEDIUM"
effort_hours: {effort_hours}
risk: "{risk}"
---

"""
```

**Key Patterns from Codebase**:
- YAML header format: from executed PRPs (e.g., PRP-10, PRP-14)
- Effort estimation: 15 min/violation + 30 min/example (pragmatic estimates)
- Risk categorization: Item-based thresholds (LOW < 5 < MEDIUM < 10 < HIGH)
- Timestamp format: ISO 8601 with Z suffix (UTC timezone)
- System PRP prefix: `DEDRIFT-` (distinguishes from feature PRPs)

**Effort Estimation Rationale**:
- Code violation fix: 15 minutes (identify, fix, test)
- Missing example creation: 30 minutes (extract pattern, write example, test)
- Minimum 1 hour (setup + context switching overhead)
- Rounds to nearest hour (realistic planning)

**Risk Assessment Rationale**:
- LOW (<5 items): Quick fixes, low complexity
- MEDIUM (5-9 items): Moderate effort, some interdependencies
- HIGH (10+ items): Significant work, high risk of breaking changes

**Validation Gates**:
- [ ] Generates valid YAML structure
- [ ] Calculates effort: violations*0.25 + missing*0.5 (min 1h)
- [ ] Determines risk: LOW (<5), MEDIUM (<10), HIGH (10+)
- [ ] Uses DEDRIFT-{timestamp} format for PRP ID
- [ ] ISO 8601 timestamp with Z suffix
- [ ] All required YAML fields present
- [ ] Unit test: effort calculation accuracy
- [ ] Unit test: risk categorization logic
- [ ] Unit test: YAML validity

---

## 🧪 Testing Strategy

### Unit Tests (~30 min)

**File**: `tools/tests/test_update_context.py`

**Test Cases**:

1. **detect_drift_violations()**
   - ✅ Successful detection with violations
   - ✅ Successful detection with no violations
   - ✅ Detection failure raises RuntimeError with troubleshooting
   - ✅ `has_drift` calculated correctly (score >= 5 OR missing > 0)

2. **generate_drift_blueprint()**
   - ✅ Successful blueprint generation
   - ✅ Creates tmp/ce/ directory if missing
   - ✅ Returns valid Path object
   - ✅ Works from project root
   - ✅ Works from tools/ directory
   - ✅ Permission errors handled with troubleshooting

3. **display_drift_summary()**
   - ✅ Displays complete summary (capture stdout)
   - ✅ Categorizes violations correctly
   - ✅ Shows correct drift level (WARNING vs CRITICAL)
   - ✅ Pluralization works (1 violation vs 2 violations)

4. **generate_prp_yaml_header()**
   - ✅ Generates valid YAML
   - ✅ Effort calculation: 2 violations = 0.5h → rounds to 1h
   - ✅ Effort calculation: 5 violations + 2 missing = 2.25h → rounds to 2h
   - ✅ Risk: 3 items → LOW
   - ✅ Risk: 7 items → MEDIUM
   - ✅ Risk: 12 items → HIGH
   - ✅ YAML parseable by frontmatter library

**Test Pattern** (from codebase):

```python
def test_detect_drift_violations_success():
    """Test successful drift detection."""
    result = detect_drift_violations()
    assert "drift_score" in result
    assert "violations" in result
    assert "missing_examples" in result
    assert "has_drift" in result
    assert isinstance(result["violations"], list)
    assert isinstance(result["missing_examples"], list)

def test_generate_prp_yaml_header_effort_calculation():
    """Test effort estimation accuracy."""
    # 2 violations * 0.25 = 0.5h → rounds to 1h
    header = generate_prp_yaml_header(2, 0, "20251016-120530")
    assert "effort_hours: 1" in header

    # 5 violations * 0.25 + 2 missing * 0.5 = 2.25h → rounds to 2h
    header = generate_prp_yaml_header(5, 2, "20251016-120530")
    assert "effort_hours: 2" in header
```

---

### Integration Tests (~15 min)

**Test Cases**:

1. **Full workflow: detect → blueprint → display**
   - ✅ Run detection
   - ✅ Generate blueprint file
   - ✅ Display summary
   - ✅ Verify blueprint file exists
   - ✅ Verify blueprint content has YAML header

2. **Edge cases**:
   - ✅ No drift detected (score = 0, no missing examples)
   - ✅ High drift (score > 15, many violations)
   - ✅ Missing examples only (no code violations)

**Integration Test Pattern**:

```python
def test_full_blueprint_workflow():
    """Test complete drift → blueprint → display workflow."""
    # Phase 1: Detect
    drift = detect_drift_violations()

    # Phase 2: Generate blueprint
    if drift["has_drift"]:
        blueprint_path = generate_drift_blueprint(drift, drift["missing_examples"])
        assert blueprint_path.exists()
        assert "DEDRIFT-INITIAL.md" in blueprint_path.name

        # Phase 3: Display
        display_drift_summary(
            drift["drift_score"],
            drift["violations"],
            drift["missing_examples"],
            blueprint_path
        )

        # Verify blueprint content
        content = blueprint_path.read_text()
        assert content.startswith("---")  # YAML header present
        assert "## Feature" in content
        assert "## Context" in content
        assert "## Acceptance Criteria" in content
```

---

### Test Coverage Target

- **Unit test coverage**: ≥85% of new functions
- **Integration test coverage**: Full workflow (detect → blueprint → display)
- **Edge case coverage**: No drift, high drift, missing examples only

**Validation Command**:

```bash
cd tools && uv run pytest tests/test_update_context.py -v --cov=ce.update_context --cov-report=term-missing
```

---

## ✅ Success Criteria

### Functional Requirements

- [ ] `detect_drift_violations()` function implemented (~25 lines)
- [ ] Wraps existing drift detection with error handling
- [ ] Returns structured dict with score, violations, missing examples
- [ ] Raises RuntimeError with troubleshooting on failure
- [ ] `generate_drift_blueprint()` function implemented (~35 lines)
- [ ] Creates tmp/ce/ directory if missing
- [ ] Writes DEDRIFT-INITIAL.md using PRP-15.1 transform function
- [ ] Returns Path object to generated file
- [ ] `display_drift_summary()` function implemented (~32 lines)
- [ ] Direct print statements (no box-drawing characters)
- [ ] Shows drift score with level indicator
- [ ] Breakdown by violation categories
- [ ] Blueprint path displayed
- [ ] `generate_prp_yaml_header()` function implemented (~40 lines)
- [ ] Calculates effort: violations*0.25 + missing*0.5 (min 1h)
- [ ] Determines risk: LOW (<5), MEDIUM (<10), HIGH (10+)
- [ ] Generates timestamp-based PRP ID
- [ ] All functions under 50 lines (KISS compliant)

### Testing Requirements

- [ ] Unit tests for each function
- [ ] Integration test: detect → blueprint → display
- [ ] Edge case tests: no drift, high drift, missing only
- [ ] Test coverage ≥85%
- [ ] All tests pass: `uv run pytest tests/test_update_context.py -v`

### Quality Requirements

- [ ] Error handling with troubleshooting guidance
- [ ] No fishy fallbacks (let exceptions propagate)
- [ ] No silent failures
- [ ] Functions follow KISS principles
- [ ] Code follows patterns from existing codebase
- [ ] Docstrings with examples for all functions
- [ ] Type hints for all function signatures

### Integration Requirements

- [ ] Works from both project root and tools/ directory
- [ ] Compatible with existing drift detection functions
- [ ] PRP-15.1 dependency verified (transform function available)
- [ ] Blueprint file discoverable in tmp/ce/ directory
- [ ] Ready for PRP-15.3 workflow integration

---

## 📊 Definition of Done

### Implementation Complete

- [ ] All 4 functions implemented in `tools/ce/update_context.py`
- [ ] Functions 25-40 lines each (no function exceeds 50 lines)
- [ ] All docstrings include usage examples
- [ ] Type hints on all function signatures

### Testing Complete

- [ ] Unit tests written for all 4 functions
- [ ] Integration test for full workflow
- [ ] Edge case tests for no drift, high drift, missing only
- [ ] Test coverage ≥85% verified
- [ ] All tests pass locally

### Quality Gates Passed

- [ ] `cd tools && uv run pytest tests/test_update_context.py -v` → all pass
- [ ] `cd tools && uv run ce validate --level 1` → pass (markdown/mermaid)
- [ ] Manual verification: Generate blueprint from real drift
- [ ] Peer review: Code follows codebase patterns
- [ ] No fishy fallbacks confirmed
- [ ] Error messages include troubleshooting guidance

### Documentation Updated

- [ ] Function docstrings complete with examples
- [ ] This PRP updated with any implementation deviations
- [ ] CLAUDE.md updated if new patterns emerged

### Ready for Next Phase

- [ ] PRP-15.2 marked as executed
- [ ] PRP-15.3 unblocked (blueprint generation available)
- [ ] Blueprint generation manually tested
- [ ] tmp/ce/ directory structure documented

---

## 🔗 Dependencies

### Required (Blocking)

- **PRP-15.1**: `transform_drift_to_initial()` function must be implemented
  - Verify: `cd tools && python3 -c "from ce.update_context import transform_drift_to_initial; print('✅')"`
  - Status: Must be completed before PRP-15.2 implementation

### Existing (Available)

- **PRP-14**: `/update-context` command with drift detection functions
  - `verify_codebase_matches_examples()` - Code violation detection
  - `detect_missing_examples_for_prps()` - Missing example detection
  - `generate_drift_report()` - Report generation (reference only)

### Enables (Future Work)

- **PRP-15.3**: Workflow automation (uses blueprint generation functions)
  - Will orchestrate: detect → approve → blueprint → generate-prp → execute

---

## 🚀 Implementation Notes

### Working Directory Handling

**Pattern**: Always detect project root, work from absolute paths

```python
current_dir = Path.cwd()
if current_dir.name == "tools":
    project_root = current_dir.parent
else:
    project_root = current_dir
```

**Rationale**: Functions must work whether called from project root or tools/ directory

---

### Error Handling Philosophy

**Pattern**: Fast failure with actionable troubleshooting

```python
try:
    # Operation
except Exception as e:
    raise RuntimeError(
        f"Operation failed: {e}\n"
        f"🔧 Troubleshooting:\n"
        f"   - Check X\n"
        f"   - Verify Y\n"
        f"   - Run: command"
    )
```

**No Fishy Fallbacks**: Let exceptions propagate for rapid troubleshooting

---

### Directory Creation

**Pattern**: Always use `parents=True, exist_ok=True`

```python
tmp_ce_dir.mkdir(parents=True, exist_ok=True)
```

**Rationale**: Idempotent, safe, handles missing parent directories

---

### Output Location

**Blueprint Location**: `tmp/ce/DEDRIFT-INITIAL.md`

**Why Not `.ce/`**:
- `tmp/` is visible (not hidden)
- Discoverable in file listings
- Standard location for generated files
- Clear separation from system config (`.ce/`)

---

### YAML Header Format

**Standard Fields** (from executed PRPs):
- `name`, `description`, `prp_id`, `status`
- `created_date`, `last_updated`, `updated_by`
- `context_sync` with `ce_updated`, `serena_updated`
- `version`, `priority`, `effort_hours`, `risk`

**System PRP Specifics**:
- `prp_id`: `DEDRIFT-{timestamp}` format
- `updated_by`: "drift-remediation-workflow"
- `priority`: Always "MEDIUM" (maintenance work)

---

## 📝 Example Usage

### Manual Testing After Implementation

```bash
# Verify PRP-15.1 dependency
cd tools
python3 -c "from ce.update_context import transform_drift_to_initial; print('✅ PRP-15.1 ready')"

# Test detection wrapper
python3 -c "
from ce.update_context import detect_drift_violations
result = detect_drift_violations()
print(f'Drift Score: {result[\"drift_score\"]}%')
print(f'Has Drift: {result[\"has_drift\"]}')
"

# Test full workflow
python3 -c "
from ce.update_context import detect_drift_violations, generate_drift_blueprint, display_drift_summary
drift = detect_drift_violations()
if drift['has_drift']:
    path = generate_drift_blueprint(drift, drift['missing_examples'])
    display_drift_summary(drift['drift_score'], drift['violations'], drift['missing_examples'], path)
    print(f'Blueprint: {path}')
"

# Verify blueprint file
ls -la ../tmp/ce/DEDRIFT-INITIAL.md
head -n 30 ../tmp/ce/DEDRIFT-INITIAL.md
```

---

## 🎓 Lessons Learned (Post-Implementation)

_To be filled after execution_

### What Went Well

-

### What Could Be Improved

-

### Patterns to Reuse

-

### Patterns to Avoid

-

---

## 📚 References

**Codebase Files**:
- `tools/ce/update_context.py` (lines 37-69): `read_prp_header()` error handling
- `tools/ce/update_context.py` (lines 403-465): `verify_codebase_matches_examples()`
- `tools/ce/update_context.py` (lines 468-533): `detect_missing_examples_for_prps()`
- `tools/ce/update_context.py` (lines 536-646): `generate_drift_report()`

**Related PRPs**:
- `PRPs/feature-requests/PRP-15.1-drift-transform-foundation.md`
- `PRPs/feature-requests/PRP-15-drift-remediation-workflow.md`
- `PRPs/executed/PRP-14-update-context-slash-command.md`
- `PRPs/executed/PRP-10-drift-history-tracking.md`

**Documentation**:
- `tmp/INITIAL-15.2-blueprint-generation.md` (original feature spec)
- `CLAUDE.md` (project standards)
- `.claude/CLAUDE.md` (global standards)

---

## 📝 Appendix: Review History

### Peer Review #1 - Document Quality (2025-10-16T19:35:00Z)

**Reviewer**: Context-Naive Peer Review Agent

**Issues Found & Fixed**:
1. ✅ **YAML Header**: Added missing `last_sync: null` to `context_sync` block
2. ✅ **Categorization Logic**: Changed display function from naive string matching to pattern file detection (`error-handling.py`, `naming.py`) - consistent with PRP-15.1
3. ✅ **Import Location**: Added note to move `datetime` import to module level
4. ✅ **Effort Formula Note**: Added comment referencing PRP-15.1 for consistency
5. ✅ **Test Assertion**: Added YAML header check (`assert content.startswith("---")`)
6. ✅ **Function Length Claims**: Corrected from "~40 lines each" to "~25-40 lines each" (actual: 25/35/32/39 lines)

**Quality Assessment**: HIGH - Well-structured implementation with clear phases, comprehensive testing, excellent documentation of patterns and rationale.

**Ready for Execution**: ✅ YES (after PRP-15.1 completion)