---
confidence: 10/10
context_memories: []
context_sync:
  ce_updated: true
  last_sync: '2025-10-15T07:54:37.614318+00:00'
  serena_updated: false
created_date: '2025-10-12T00:00:00Z'
dependencies: []
description: Implement architectural consistency validation against INITIAL.md EXAMPLES
  to prevent drift and ensure implementations match specification patterns
effort_hours: 25.0
issue: BLA-7
last_updated: '2025-10-12T18:45:00Z'
name: Level 4 Pattern Conformance Validation
parent_prp: null
priority: HIGH
project: Context Engineering
prp_id: PRP-1
risk: MEDIUM
status: executed
task_id: ''
updated: '2025-10-15T07:54:37.614320+00:00'
updated_by: update-context-command
version: 1
---

# PRP-1: Level 4 Pattern Conformance Validation

## 🎯 TL;DR

**Problem**: No automated validation exists to detect architectural drift between PRP specifications (INITIAL.md EXAMPLES) and actual implementations, leading to inconsistent code patterns and technical debt accumulation.

**Solution**: Implement Level 4 validation gate that extracts patterns from INITIAL.md EXAMPLES, compares against implementation using Serena MCP semantic analysis, calculates drift score (0-100%), and enforces threshold-based escalation (0-10% auto-accept, 10-30% auto-fix, 30%+ escalate to user).

**Impact**: Prevents architectural drift, ensures pattern consistency across features, enables 10/10 confidence scoring for production-ready code, and creates audit trail of drift decisions for PRP-6 historical tracking.

**Risk**: MEDIUM - Pattern matching algorithm complexity requires iterative refinement; high drift cases need clear user escalation flow.

**Effort**: 25.0h (Research: 5h, Core Implementation: 12h, CLI Integration: 4h, Testing: 4h)

**Non-Goals**:

- ❌ Style-level validation (covered by L1: linters)
- ❌ Functional correctness testing (covered by L2: unit tests, L3: integration tests)
- ❌ Historical drift aggregation across PRPs (handled by PRP-6)
- ❌ Automatic pattern refactoring (only detects and optionally suggests fixes)

---

## 📋 Pre-Execution Context Rebuild

**Complete before implementation:**

- [ ] **Review documentation**:
  - `PRPs/Model.md` Section 3.3.3 (Pattern Conformance specification)
  - `PRPs/Model.md` Section 7.1.4 (L4 validation details)
  - `PRPs/GRAND-PLAN.md` lines 64-113 (PRP-1 specification)
  - `docs/research/01-prp-system.md` (PRP structure and EXAMPLES format)
  - `docs/research/08-validation-testing.md` (Validation framework)

- [ ] **Verify codebase state**:
  - File exists: `tools/ce/validate.py` (L1-L3 implementations)
  - File exists: `tools/ce/__main__.py` (CLI entry point)
  - File exists: `tools/ce/core.py` (run_cmd utility)
  - Tests exist: `tools/tests/test_validate.py`

- [ ] **Git baseline**: Clean working tree (run `git status`)

- [ ] **Dependencies installed**: `cd tools && uv sync`

---

## 📖 Context

**Related Work**:

- **Existing validation**: L1-L3 implemented in `tools/ce/validate.py` (syntax, unit tests, integration tests)
- **Confidence scoring**: Model.md Section 7.3.1 currently achieves 9/10 max; L4 enables 10/10
- **Parent system**: Context Engineering Management System (Model.md)

**Current State**:

- ✅ L1 validation exists: `validate_level_1()` runs linters and type-checkers
- ✅ L2 validation exists: `validate_level_2()` runs unit tests
- ✅ L3 validation exists: `validate_level_3()` runs integration tests
- ❌ L4 validation missing: No pattern conformance checking
- ❌ No drift tracking: Cannot detect architectural divergence from specifications
- ❌ Confidence ceiling at 9/10: L4 required for production-ready status

**INITIAL.md Format** (Expected Input for L4):

- PRPs reference `INITIAL.md` files containing feature specifications
- **Location**: `context-engineering/feature-requests/INITIAL.md` (per-feature) or embedded in PRP under `## EXAMPLES` section
- **Structure**:

  ```markdown
  ## FEATURE
  [What to build - 2-3 sentences]

  ## EXAMPLES
  [Code patterns to follow - 1-3 code blocks showing similar implementations]

  ```python
  # Example: Existing validation pattern
  async def validate_data(data: Dict) -> ValidationResult:
      try:
          # Pattern: async/await, try-except, snake_case
          result = await schema.validate(data)
          return ValidationResult(success=True, data=result)
      except ValidationError as e:
          return ValidationResult(success=False, error=str(e))
  ```

  ## DOCUMENTATION

  [Links to library docs, API references]

  ## OTHER CONSIDERATIONS

  [Gotchas, constraints, edge cases]

  ```
- **L4 Parses**: `## EXAMPLES` section to extract patterns from code blocks

**Desired State**:

- ✅ L4 validation functional: `validate_level_4(prp_path)` analyzes pattern conformance
- ✅ Drift score calculation: Quantifies divergence (0-100%) with clear methodology
- ✅ Threshold-based escalation: Auto-accept (0-10%), auto-fix (10-30%), user decision (30%+)
- ✅ DRIFT_JUSTIFICATION persistence: Stored in PRP YAML header for PRP-6 aggregation
- ✅ CLI integration: `ce validate --level 4 --prp PRP-X.md`
- ✅ Confidence scoring updated: L4 pass adds +1 to achieve 10/10

**Why Now**: Foundation for PRP execution workflow (PRP-4 depends on L4); blocks MVP completion; enables production-ready code confidence.

---

## 🔧 Implementation Blueprint

### Phase 1: Pattern Extraction Engine (5 hours)

**Goal**: Parse INITIAL.md EXAMPLES section and extract semantic patterns

**Approach**: Regex + AST-based pattern extraction from markdown code blocks (Python: `ast` module, others: regex fallback)

**Files to Create**:

- `tools/ce/pattern_extractor.py` - Pattern extraction logic

**Key Functions**:

```python
def extract_patterns_from_prp(prp_path: str) -> Dict[str, Any]:
    """Extract patterns from PRP's INITIAL.md EXAMPLES section.

    Args:
        prp_path: Path to PRP markdown file

    Returns:
        {
            "code_structure": ["async/await", "class-based", "functional"],
            "error_handling": ["try-except", "early-return", "null-checks"],
            "naming_conventions": ["snake_case", "camelCase", "PascalCase"],
            "data_flow": ["props", "state", "context", "closure"],
            "test_patterns": ["pytest", "unittest", "fixtures"],
            "import_patterns": ["relative", "absolute"],
            "raw_examples": [{"language": "python", "code": "..."}]
        }

    Raises:
        ValueError: If EXAMPLES section not found or malformed
    """
    pass
```

```python
def parse_code_structure(code: str, language: str) -> List[str]:
    """Identify structural patterns in code example.

    Detects:
    - async/await vs callbacks vs synchronous
    - class-based vs functional vs procedural
    - decorator usage patterns
    - context manager patterns

    Args:
        code: Source code string
        language: Programming language (python, typescript, etc.)

    Returns:
        List of detected structural patterns
    """
    pass
```

**Pattern Categories**:

1. **Code Structure**:
   - Async patterns: `async/await`, `callbacks`, `promises`, `generators`
   - Organization: `class-based`, `functional`, `procedural`, `modular`
   - Decorators: `@staticmethod`, `@property`, `@dataclass`

2. **Error Handling**:
   - Exception patterns: `try-except`, `try-except-finally`, `contextlib.suppress`
   - Guard clauses: `early-return`, `guard-if`, `null-checks`
   - Error types: `custom-exceptions`, `builtin-exceptions`

3. **Naming Conventions**:
   - Case styles: `snake_case`, `camelCase`, `PascalCase`, `SCREAMING_SNAKE_CASE`
   - Prefixes: `_private`, `__dunder__`, `get_`, `set_`, `is_`, `has_`

4. **Data Flow**:
   - State management: `props`, `state`, `context`, `global`, `closure`
   - Immutability: `frozen-dataclass`, `tuple-return`, `copy-on-write`

5. **Test Patterns**:
   - Frameworks: `pytest`, `unittest`, `doctest`
   - Structure: `fixtures`, `parametrize`, `mocks`, `integration-tests`

**Validation Command**: `cd tools && uv run pytest tests/test_pattern_extractor.py -v`

**Checkpoint**: `git add tools/ce/pattern_extractor.py tests/test_pattern_extractor.py && git commit -m "feat(L4): pattern extraction engine"`

---

### Phase 2: Implementation Analysis Engine (6 hours)

**Goal**: Analyze implementation code and calculate drift score

**MVP Limitation**: Auto-fix suggestions displayed only, no automatic code modification  
**Future Enhancement**: Apply fixes automatically using Serena edit operations

**Approach**: Use Serena MCP `find_symbol`, `get_symbols_overview`, `read_file` to analyze implementation structure

**Files to Create**:

- `tools/ce/drift_analyzer.py` - Drift calculation logic

**Key Functions**:

```python
def analyze_implementation(
    prp_path: str,
    implementation_paths: List[str]
) -> Dict[str, Any]:
    """Analyze implementation code structure using Serena MCP.

    Args:
        prp_path: Path to PRP file (for extracting expected patterns)
        implementation_paths: Paths to implementation files to analyze

    Returns:
        {
            "detected_patterns": {
                "code_structure": ["async/await", "class-based"],
                "error_handling": ["try-except"],
                "naming_conventions": ["snake_case"],
                ...
            },
            "files_analyzed": ["src/validate.py", "src/core.py"],
            "symbol_count": 42,
            "analysis_duration": 2.5,
            "serena_available": True
        }

    Uses (if Serena MCP available):
        - serena.get_symbols_overview(file) for structure
        - serena.find_symbol(name) for detailed analysis
        - serena.read_file(file) for pattern matching

    Fallback (if Serena unavailable):
        - Python ast module for Python files
        - Regex-based pattern detection for other languages
        - Log warning: "Serena MCP unavailable - using fallback analysis (reduced accuracy)"

    Raises:
        RuntimeError: If neither Serena nor fallback analysis succeeds
    """
    pass
```

```python
def calculate_drift_score(
    expected_patterns: Dict[str, Any],
    detected_patterns: Dict[str, Any]
) -> Dict[str, Any]:
    """Calculate drift score between expected and detected patterns.

    Scoring methodology:
    - Each category (code_structure, error_handling, etc.) weighted equally
    - Within category: count mismatches / total expected patterns
    - Overall drift = average across all categories * 100

    Args:
        expected_patterns: From extract_patterns_from_prp()
        detected_patterns: From analyze_implementation()

    Returns:
        {
            "drift_score": 23.5,  # 0-100%, lower is better
            "category_scores": {
                "code_structure": 10.0,
                "error_handling": 0.0,
                "naming_conventions": 50.0,
                ...
            },
            "mismatches": [
                {
                    "category": "naming_conventions",
                    "expected": "snake_case",
                    "detected": "camelCase",
                    "severity": "medium",
                    "affected_symbols": ["processData", "handleError"]
                }
            ],
            "threshold_action": "auto_fix"  # auto_accept | auto_fix | escalate
        }
    """
    pass
```

**Drift Score Formula**:

```
drift_score = Σ(category_weight_i * category_mismatch_i) / Σ(category_weight_i) * 100

where:
  category_mismatch_i = count(mismatches_i) / count(expected_patterns_i)
  category_weight_i = 1.0 (equal weighting for MVP)

**Example Calculation**:
Given:
- code_structure: 1 mismatch / 2 expected = 50% mismatch
- error_handling: 0 mismatches / 1 expected = 0% mismatch
- naming_conventions: 3 mismatches / 5 expected = 60% mismatch

drift_score = (50% + 0% + 60%) / 3 = 36.7%
→ threshold_action = "escalate" (>30%)
```

**Threshold Logic**:

- **0-10% drift**: `auto_accept` - Continue execution, log info message
- **10-30% drift**: `auto_fix` - Log warning with recommended fixes (manual application in MVP; automated refactoring deferred to future enhancement)
- **30%+ drift**: `escalate` - HALT execution, prompt user for decision

**Auto-Fix Strategy** (MVP: Suggestions Only):

```python
def get_auto_fix_suggestions(mismatches: List[Dict]) -> List[str]:
    """Generate fix suggestions for 10-30% drift (MVP: display only, no auto-apply).

    Future enhancement: Apply fixes automatically using Serena edit operations.

    Returns:
        List of actionable fix suggestions (e.g., "Rename processData → process_data")
    """
    suggestions = []
    for mismatch in mismatches:
        if mismatch["category"] == "naming_conventions":
            for symbol in mismatch["affected_symbols"]:
                expected_name = convert_to_convention(symbol, mismatch["expected"])
                suggestions.append(f"Rename {symbol} → {expected_name} in {mismatch['file']}")
    return suggestions
```

**Validation Command**: `cd tools && uv run pytest tests/test_drift_analyzer.py -v`

**Checkpoint**: `git add tools/ce/drift_analyzer.py tests/test_drift_analyzer.py && git commit -m "feat(L4): drift analysis engine"`

---

### Phase 3: User Escalation Flow (4 hours)

**Goal**: Interactive CLI for high-drift cases requiring human decision

**Approach**: Rich CLI with diff display, colored output, and persistent decision logging

**Files to Modify**:

- `tools/ce/validate.py` - Add `validate_level_4()` function
- `tools/ce/__main__.py` - Add CLI command `ce validate --level 4`

**User Interaction Flow**:

```
🚨 HIGH DRIFT DETECTED: 45.2%

PRP: PRP-003 (User Authentication System)
Implementation: src/auth/validator.py

DRIFT BREAKDOWN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Category              Expected       Detected      Drift
─────────────────────────────────────────────────────
Code Structure        async/await    callbacks     50.0%
Error Handling        try-except     early-return  30.0%
Naming Conventions    snake_case     camelCase     80.0%
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

AFFECTED SYMBOLS:
• processData → Expected: process_data (snake_case)
• handleError → Expected: handle_error (snake_case)
• validateInput → Expected: validate_input (snake_case)

OPTIONS:
[A] Accept drift (add DRIFT_JUSTIFICATION to PRP)
[R] Reject and halt (requires manual refactoring)
[U] Update EXAMPLES in PRP (update specification)
[Q] Quit without saving

Your choice (A/R/U/Q): _
```

**DRIFT_JUSTIFICATION Format** (persisted to PRP YAML):

```yaml
drift_decision:
  score: 45.2
  action: "accepted"  # accepted | rejected | examples_updated
  justification: "Legacy callback API required for third-party library compatibility"
  timestamp: "2025-10-12T15:30:00Z"
  category_breakdown:
    code_structure: 50.0
    error_handling: 30.0
    naming_conventions: 80.0
  reviewer: "human"  # human | auto_accept | auto_fix
```

**Key Functions**:

```python
def validate_level_4(
    prp_path: str,
    implementation_paths: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Run Level 4 validation: Pattern Conformance.

    Args:
        prp_path: Path to PRP markdown file
        implementation_paths: Files to analyze; auto-detected if None via:
            1. Parse PRP IMPLEMENTATION BLUEPRINT for file references
               (searches for patterns: "Modify: path/file.py", "Create: path/file.py")
            2. Fallback: git diff --name-only main...HEAD
            3. Fallback: Interactive prompt for user to specify files

    Returns:
        {
            "success": bool,
            "drift_score": float,
            "threshold_action": str,  # auto_accept | auto_fix | escalate
            "decision": Optional[str],  # if escalated: accepted | rejected | examples_updated
            "justification": Optional[str],
            "duration": float,
            "level": 4
        }

    Raises:
        RuntimeError: If PRP parsing fails or Serena MCP unavailable

    Process:
        1. Extract patterns from PRP EXAMPLES
        2. Analyze implementation with Serena MCP
        3. Calculate drift score
        4. Apply threshold logic (auto-accept/fix/escalate)
        5. If escalated: prompt user, persist decision
        6. Return validation result
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_validate.py::test_level_4_validation -v`

**Checkpoint**: `git add tools/ce/validate.py tools/ce/__main__.py tests/test_validate.py && git commit -m "feat(L4): user escalation flow"`

---

### Phase 4: Confidence Scoring Integration (3 hours)

**Goal**: Update confidence scoring to require L4 pass for 10/10

**Approach**: Modify existing `calculate_confidence()` function (if exists) or create new scoring module

**Files to Modify**:

- `tools/ce/validate.py` - Add confidence scoring logic
- `tools/ce/__main__.py` - Display confidence score in validation output

**Confidence Scoring Logic**:

```python
def calculate_confidence(results: Dict[int, Dict[str, Any]]) -> int:
    """Calculate confidence score (1-10) based on validation results.

    Scoring breakdown:
    - Baseline: 6 (untested code)
    - Level 1 (Syntax & Style): +1
    - Level 2 (Unit Tests): +2
    - Level 3 (Integration): +1
    - Level 4 (Pattern Conformance): +1 (NEW)
    - Max: 10/10 (production-ready)

    Requirements for +1 from L4:
    - drift_score < 10% (auto-accept threshold)
    - OR drift_score < 30% AND decision = "accepted" with justification

    Args:
        results: Dict mapping level (1-4) to validation results

    Returns:
        Confidence score 1-10

    Examples:
        >>> results = {1: {"success": True}, 2: {"success": True, "coverage": 0.85}}
        >>> calculate_confidence(results)
        9  # Without L3, L4

        >>> results = {
        ...     1: {"success": True},
        ...     2: {"success": True, "coverage": 0.85},
        ...     3: {"success": True},
        ...     4: {"success": True, "drift_score": 8.5}
        ... }
        >>> calculate_confidence(results)
        10  # All gates pass
    """
    score = 6  # Baseline

    if results.get(1, {}).get("success"):
        score += 1

    if results.get(2, {}).get("success") and results.get(2, {}).get("coverage", 0) > 0.8:
        score += 2

    if results.get(3, {}).get("success"):
        score += 1

    # Level 4: Pattern conformance (NEW)
    l4_result = results.get(4, {})
    if l4_result.get("success"):
        drift_score = l4_result.get("drift_score", 100)
        decision = l4_result.get("decision")

        # Pass L4 if:
        # 1. drift < 10% (auto-accept)
        # 2. drift < 30% AND explicitly accepted with justification
        if drift_score < 10.0 or (drift_score < 30.0 and decision == "accepted"):
            score += 1

    return min(score, 10)
```

**CLI Output Example**:

```
✅ VALIDATION COMPLETE

Results:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Level 1: Syntax & Style          ✅ PASS (12s)
Level 2: Unit Tests              ✅ PASS (45s, 87% coverage)
Level 3: Integration Tests       ✅ PASS (2m 15s)
Level 4: Pattern Conformance     ✅ PASS (1m 30s, 8.3% drift)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 CONFIDENCE SCORE: 10/10 (PRODUCTION-READY)

Total Duration: 4m 12s
```

**Validation Command**: `cd tools && uv run pytest tests/test_validate.py::test_confidence_scoring -v`

**Checkpoint**: `git add tools/ce/validate.py tools/ce/__main__.py tests/test_validate.py && git commit -m "feat(L4): confidence scoring integration"`

---

### Phase 5: Testing & Documentation (4 hours)

**Goal**: Comprehensive test coverage and usage documentation

**Test Coverage Requirements**:

- Unit tests: Pattern extraction, drift calculation, threshold logic
- Integration tests: Full L4 validation with sample PRPs
- E2E test: User escalation flow simulation

**Files to Create**:

- `tools/tests/test_pattern_extractor.py`
- `tools/tests/test_drift_analyzer.py`
- `tools/tests/fixtures/sample_prp_high_drift.md` (PRP with 45%+ drift examples)
- `tools/tests/fixtures/sample_prp_low_drift.md` (PRP with <10% drift examples)
- `tools/tests/fixtures/sample_implementation.py` (Mock implementation for testing)

**Test Cases**:

```python
def test_pattern_extraction_from_prp():
    """Verify pattern extraction from PRP EXAMPLES section."""
    patterns = extract_patterns_from_prp("tests/fixtures/sample_prp.md")
    assert "code_structure" in patterns
    assert "async/await" in patterns["code_structure"]
    assert len(patterns["raw_examples"]) > 0

def test_drift_calculation_low_drift():
    """Verify low drift (< 10%) triggers auto-accept."""
    expected = {"code_structure": ["async/await"], "naming_conventions": ["snake_case"]}
    detected = {"code_structure": ["async/await"], "naming_conventions": ["snake_case"]}
    result = calculate_drift_score(expected, detected)
    assert result["drift_score"] < 10.0
    assert result["threshold_action"] == "auto_accept"

def test_drift_calculation_high_drift():
    """Verify high drift (> 30%) triggers escalation."""
    expected = {"code_structure": ["async/await"], "naming_conventions": ["snake_case"]}
    detected = {"code_structure": ["callbacks"], "naming_conventions": ["camelCase"]}
    result = calculate_drift_score(expected, detected)
    assert result["drift_score"] > 30.0
    assert result["threshold_action"] == "escalate"

def test_validate_level_4_success():
    """Verify L4 validation succeeds with low drift."""
    result = validate_level_4("tests/fixtures/sample_prp_low_drift.md")
    assert result["success"] is True
    assert result["drift_score"] < 10.0
    assert result["level"] == 4
```

**Documentation Updates**:

- `tools/README.md`: Add L4 validation usage examples
- `PRPs/Model.md`: Update Section 4.1.2 (ce CLI) with L4 command
- `docs/research/08-validation-testing.md`: Add L4 validation details

**Validation Command**: `cd tools && uv run pytest tests/ -v --cov=ce --cov-report=term-missing`

**Final Checkpoint**: `git add -A && git commit -m "feat(L4): testing and documentation complete"`

---

## ✅ Success Criteria

- [ ] **Pattern Extraction**: `extract_patterns_from_prp()` detects 90%+ of pattern categories (code structure, error handling, naming, data flow, test patterns)
- [ ] **Drift Calculation**: `calculate_drift_score()` produces consistent scores ±5% on repeated runs
- [ ] **Threshold Logic**: Auto-accept (0-10%), auto-fix (10-30%), escalate (30%+) working correctly
- [ ] **User Escalation**: Interactive CLI displays diff, accepts user decision, persists DRIFT_JUSTIFICATION to PRP YAML header
- [ ] **Serena Integration**: Uses `find_symbol`, `get_symbols_overview`, `read_file` for implementation analysis
- [ ] **Confidence Scoring**: L4 pass adds +1 to confidence score, enabling 10/10
- [ ] **CLI Command**: `ce validate --level 4 --prp PRP-X.md` functional
- [ ] **Cross-PRP Linkage**: DRIFT_JUSTIFICATION stored in PRP YAML for PRP-6 aggregation
- [ ] **Test Coverage**: ≥80% code coverage with unit, integration, and E2E tests
- [ ] **Documentation**: Usage examples in README, Model.md updated, validation docs complete
- [ ] **Performance**: L4 validation completes in <2 minutes for typical PRPs (~500 LOC implementation, 3 EXAMPLES in PRP)

---

## 🔍 Validation Gates

### Gate 1: Unit Tests (After Each Phase)

```bash
cd tools && uv run pytest tests/ -v -k "pattern_extractor or drift_analyzer"
```

**Expected**: All tests pass, no failures

### Gate 2: Integration Tests (After Phase 3)

```bash
cd tools && uv run pytest tests/test_validate.py::test_level_4_integration -v
```

**Expected**: Full L4 validation flow works with sample PRP

### Gate 3: E2E Test (After Phase 4)

```bash
cd tools && uv run ce validate --level 4 --prp tests/fixtures/sample_prp_high_drift.md
```

**Expected**: User escalation flow triggers, accepts input, persists decision

### Gate 4: Coverage Check (After Phase 5)

```bash
cd tools && uv run pytest tests/ --cov=ce --cov-report=term-missing --cov-fail-under=80
```

**Expected**: ≥80% coverage across all new modules

---

## 📚 References

**Model.md Sections**:

- Section 3.3.3: Pattern Conformance Validation (drift detection, thresholds)
- Section 7.1.4: Level 4 Validation Gate (L4 specification)
- Section 7.3.1: Confidence Scoring (10/10 calculation with L4)
- Section 5.2: Workflow Step 6 (L1-L4 validation loop)

**GRAND-PLAN.md**:

- Lines 64-113: PRP-1 specification (this PRP)
- Lines 117-169: PRP-2 (checkpoint integration for L4 gates)
- Lines 241-317: PRP-4 (L4 validation loop integration)

**Research Docs**:

- `docs/research/01-prp-system.md`: PRP structure, EXAMPLES format
- `docs/research/08-validation-testing.md`: Validation framework overview
- `docs/research/04-self-healing-framework.md`: Auto-fix patterns for 10-30% drift

**Existing Code**:

- `tools/ce/validate.py`: L1-L3 validation implementations (lines 7-149)
- `tools/ce/core.py`: `run_cmd()` utility for subprocess execution
- `tools/ce/__main__.py`: CLI entry point and command routing

**External References**:

- Serena MCP documentation: Symbol analysis, pattern detection
- Context7 MCP: Library documentation fetching (not used in L4)
- GitHub Copilot research: 35-45% baseline for comparison

---

## 🎯 Definition of Done

- [ ] All 5 phases implemented and tested
- [ ] L4 validation functional: `ce validate --level 4` works
- [ ] Drift score calculation accurate and consistent
- [ ] User escalation flow tested with sample PRPs
- [ ] DRIFT_JUSTIFICATION persistence verified
- [ ] Confidence scoring updated (10/10 achievable)
- [ ] Test coverage ≥80%
- [ ] Documentation complete (README, Model.md, validation docs)
- [ ] Git checkpoints created after each phase
- [ ] No fishy fallbacks or silent failures
- [ ] All validation commands succeed

**Note**: Check items during execution only

---

**PRP-1 Ready for Peer Review and Execution** ✅