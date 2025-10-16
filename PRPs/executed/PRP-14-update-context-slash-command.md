---
completed: '2025-10-14T12:20:00+00:00'
complexity: medium
context_sync:
  ce_updated: true
  last_sync: '2025-10-16T20:03:32.171848+00:00'
  serena_updated: false
created: 2025-10-14 16:00:00+00:00
dependencies: frontmatter, Serena MCP (optional)
estimated_hours: 5-6
feature_name: /update-context Slash Command Implementation
issue: BLA-24
prp_id: PRP-14
status: executed
updated: '2025-10-16T20:03:32.171854+00:00'
updated_by: update-context-command
---

# /update-context Slash Command Implementation

## 1. TL;DR

**Objective**: Implement the /update-context slash command for maintaining alignment between CE/Serena knowledge systems and codebase evolution

**What**: Universal command that scans PRPs, updates YAML headers with context_sync flags, verifies implementations via Serena MCP, manages PRP status transitions, organizes PRP files, and maintains CE examples. **Detects drift between codebase and examples/** patterns, generating formalized structured reports with solution proposals when drift is detected.** Supports both universal sync (all PRPs) and targeted sync (single PRP via --prp flag).

**Why**: Critical system hygiene command that prevents documentation drift and maintains bidirectional sync between knowledge systems and actual codebase. Without this command, drift accumulates and knowledge systems become stale.

**Effort**: Medium (5-6 hours estimated based on complexity - includes drift detection & reporting)

**Dependencies**: frontmatter library for YAML manipulation, Serena MCP for codebase cross-reference (optional - graceful degradation)

## 2. Context

### Background

The /update-context command is the hygiene mechanism for the entire Context Engineering system. It systematically:

1. **Updates PRP YAML Headers**: Sets `context_sync.ce_updated` and `context_sync.serena_updated` flags, adds `last_sync` timestamps
2. **Verifies Implementations**: Uses Serena MCP to verify that PRP specifications match actual codebase implementations
3. **Manages PRP Status**: Auto-transitions PRPs from `feature-requests` to `executed` when implementations are verified
4. **Organizes Files**: Moves PRPs to correct directories (`PRPs/executed/`, `PRPs/archived/`) based on status
5. **Detects Pattern Drift**: Identifies codebase violations of documented examples/ patterns with structured reporting
6. **Detects Missing Examples**: Identifies critical PRPs missing corresponding examples/ documentation
7. **Detects Archives**: Identifies superseded or deprecated PRPs for archival

**Note**: CE Examples Management (upsert/remove patterns) is future work (not in this PRP scope)

Currently referenced in workflow-patterns.md but not implemented. This feature is crucial for preventing the "documentation rot" problem in large projects.

### Constraints and Considerations

**Technical Constraints**:
- Must handle missing Serena MCP gracefully (log warning, continue with partial sync)
- YAML header manipulation must preserve formatting and comments
- File moves must be atomic (use pathlib rename, not shell mv)
- Must validate PRP ID format before processing
- No fishy fallbacks - clear errors with troubleshooting guidance

**KISS Principles**:
- Use frontmatter library instead of manual YAML parsing
- Single module (tools/ce/update_context.py) with focused responsibility
- Import existing functions from context.py for drift detection
- Batch file operations to minimize I/O

**Quality Standards**:
- No hardcoded success messages - real verification only
- Fast failure - let exceptions bubble up with actionable guidance
- Proper logging at each step (logger.info, logger.warning, logger.error)
- All YAML updates must be verifiable (read-back check)

**Edge Cases**:
- PRP files without YAML headers (skip with warning)
- PRPs with status already `executed` (update sync flags only, no move)
- Serena MCP unavailable (set serena_updated=false, log warning)
- Function implementations partially complete (ce_updated=false)
- Concurrent file modifications (atomic operations only)
- examples/ directory missing (skip drift detection with info log)
- Functions referenced in PRP deleted from codebase (mark ce_updated=false, log warning with function names)
- Multiple PRPs reference same functions (all get ce_updated=true if function exists)
- YAML comments preservation (frontmatter library preserves comments automatically)
- Permission errors on file moves (raise RuntimeError with troubleshooting, don't corrupt state)

### Documentation References

- **Existing Patterns**:
  - YAML header handling: `tools/ce/prp.py:32-80` (validate_prp_yaml function)
  - Context sync: `tools/ce/context.py:12-51` (sync function)
  - PRP status management: `tools/ce/prp.py:222-285` (start_prp, end_prp)
  - File operations: `tools/ce/core.py` (git operations, shell commands)

- **Libraries**:
  - `frontmatter` - YAML frontmatter manipulation (https://pypi.org/project/python-frontmatter/)
  - `pathlib` - File path operations (stdlib)
  - `yaml` - Already used in prp.py for validation

- **Slash Command Pattern**:
  - `.claude/commands/generate-prp.md` - Example slash command structure
  - `.claude/commands/execute-prp.md` - Command invocation pattern

## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

1. Install frontmatter library for YAML manipulation:
   ```bash
   cd tools
   uv add python-frontmatter
   ```

2. Create slash command file `.claude/commands/update-context.md` with command specification

3. Research existing code patterns:
   - Review PRP YAML schema in prp.py
   - Study context sync patterns in context.py
   - Analyze file organization in PRPs/ directory

### Phase 2: Core Implementation - YAML Operations (60 min)

1. Create `tools/ce/update_context.py` module

2. Implement YAML header operations:
   ```python
   def read_prp_header(file_path: Path) -> Tuple[Dict[str, Any], str]:
       """Read PRP YAML header using frontmatter library."""

   def update_context_sync_flags(
       file_path: Path,
       ce_updated: bool,
       serena_updated: bool
   ) -> None:
       """Update context_sync flags in PRP YAML header."""

   def get_prp_status(file_path: Path) -> str:
       """Extract status field from PRP YAML header."""
   ```

3. Implement PRP discovery:
   ```python
   def discover_prps(target_prp: Optional[str] = None) -> List[Path]:
       """Scan PRPs/ directory recursively for markdown files."""
   ```

### Phase 3: Core Implementation - Codebase Cross-Reference (90 min)

1. Implement function extraction from PRP content:
   ```python
   def extract_expected_functions(content: str) -> List[str]:
       """Extract function/class names from PRP content using regex."""
       # Pattern: `function_name()` or `class ClassName`
       # Also check code blocks for def/class definitions
   ```

2. Implement Serena MCP verification (with graceful degradation):
   ```python
   def verify_implementation_with_serena(
       expected_functions: List[str]
   ) -> bool:
       """Use Serena MCP find_symbol to verify implementations exist."""
       # Try Serena MCP
       # If unavailable, log warning and return False
       # If available, check each function exists
       # Return True only if ALL functions found
   ```

3. Implement status transition logic:
   ```python
   def should_transition_to_executed(file_path: Path) -> bool:
       """Check if PRP should transition from feature-requests to executed."""
       # Rules:
       # - Current status must be "new" or "in_progress"
       # - ce_updated must be True (implementation verified)
       # - File must be in feature-requests/ directory
   ```

### Phase 4: File Organization (45 min)

1. Implement file move operations:
   ```python
   def move_prp_to_executed(file_path: Path) -> Path:
       """Move PRP from feature-requests/ to executed/."""
       # Use pathlib rename (atomic operation)
       # Create target directory if needed
       # Return new path

   def move_prp_to_archived(file_path: Path) -> Path:
       """Move PRP to archived/ directory."""
   ```

2. Implement archive detection:
   ```python
   def detect_archived_prps() -> List[Path]:
       """Identify superseded/deprecated PRPs for archival."""
       # Look for status == "archived" in YAML
       # Check for "superseded_by" field
       # Return list of PRPs to move
   ```

### Phase 5: Drift Detection & Reporting (60 min)

**Scope**: Two-way drift detection:
1. **Code violates documented patterns**: Detect violations in examples/ (error handling, naming, KISS)
2. **Missing pattern documentation**: Detect critical PRP implementations without corresponding examples/

**Focus Categories**:
- Error handling (bare except, missing troubleshooting)
- Naming conventions (versioned suffixes like `_v2`)
- KISS violations (overcomplicated implementations)
- Missing examples (critical PRPs without pattern documentation)

**Note**: Automated fixes (`/fix-drift`) are **out of scope** for this PRP - report only.

1. Define pattern detection rules:
   ```python
   # Patterns to detect from examples/ (start with these 3)
   PATTERN_FILES = {
       "error_handling": "examples/patterns/error-handling.py",
       "no_fishy_fallbacks": "examples/patterns/no-fishy-fallbacks.py",
       "naming_conventions": "examples/patterns/naming.py"
   }

   PATTERN_CHECKS = {
       "error_handling": [
           ("bare_except", r"except:\s*$", "Use specific exception types"),
           ("missing_troubleshooting", r'raise \w+Error\([^🔧]+\)$', "Add 🔧 Troubleshooting guidance")
       ],
       "naming_conventions": [
           ("version_suffix", r"def \w+_v\d+", "Use descriptive names, not versions"),
       ],
       "kiss_violations": [
           ("deep_nesting", r"    " * 5, "Reduce nesting depth (max 4 levels)")
       ]
   }
   ```

2. Implement pattern loading:
   ```python
   def load_pattern_checks() -> Dict[str, List[Tuple[str, str, str]]]:
       """Load pattern checks from PATTERN_CHECKS.

       Returns:
           {
               "error_handling": [
                   ("bare_except", "regex", "fix description"),
                   ...
               ]
           }
       """
       return PATTERN_CHECKS
   ```

3. Implement codebase pattern verification:
   ```python
   def verify_codebase_matches_examples() -> Dict[str, List[str]]:
       """Check if codebase follows patterns documented in examples/**.

       Returns:
           {
               "violations": [
                   "File tools/ce/foo.py uses bare except (violates examples/patterns/error-handling.py)",
                   "Function bar() missing troubleshooting in error message (violates examples/patterns/no-fishy-fallbacks.py)"
               ],
               "drift_score": 15.3  # Percentage of files violating patterns
           }
       """
       # Scan examples/** for documented patterns
       # Search codebase for violations using Serena MCP
       # Calculate drift percentage
       # Return structured violations list
   ```

3b. Implement missing example detection:
   ```python
   def detect_missing_examples_for_prps() -> List[Dict[str, Any]]:
       """Detect executed PRPs missing corresponding examples/ documentation.

       Returns:
           [
               {
                   "prp_id": "PRP-13",
                   "feature_name": "Production Hardening",
                   "complexity": "high",
                   "missing_example": "error_recovery",
                   "suggested_path": "examples/patterns/error-recovery.py",
                   "rationale": "Complex error recovery logic should be documented"
               },
               ...
           ]
       """
       # Scan executed PRPs with complexity >= medium or risk >= MEDIUM
       # Check if corresponding example exists in examples/
       # Pattern matching: PRP mentions "error handling" → check examples/patterns/error-handling.py
       # Return list of PRPs needing example documentation
   ```

4. Implement drift report generation:
   ```python
   def generate_drift_report(violations: List[str], drift_score: float) -> str:
       """Generate formalized structured drift report with solution proposals.

       Returns markdown report:
           ## Context Drift Report - Examples/** Patterns

           **Drift Score**: 15.3% (⚠️ WARNING)
           **Generated**: 2025-10-14T16:30:00Z
           **Violations Found**: 8
           **Missing Examples**: 3

           ### Part 1: Code Violating Documented Patterns

           #### Violations by Category

           #### Error Handling (3 violations)
           1. **File**: tools/ce/foo.py:42
              **Issue**: Bare except clause without exception type
              **Pattern**: examples/patterns/error-handling.py
              **Solution**: Replace `except:` with `except Exception as e:`

           2. **File**: tools/ce/bar.py:156
              **Issue**: Missing troubleshooting guidance in RuntimeError
              **Pattern**: examples/patterns/no-fishy-fallbacks.py
              **Solution**: Add 🔧 Troubleshooting section to error message

           ### Part 2: Missing Pattern Documentation

           **Critical PRPs Without Examples**:

           1. **PRP-13**: Production Hardening & Comprehensive Documentation
              **Complexity**: high
              **Missing Example**: error_recovery
              **Suggested Path**: examples/patterns/error-recovery.py
              **Rationale**: Complex error recovery with retry logic should be documented
              **Action**: Create example showing resilience patterns

           2. **PRP-11**: Pipeline Testing Framework
              **Complexity**: medium
              **Missing Example**: strategy_pattern_testing
              **Suggested Path**: examples/patterns/strategy-testing.py
              **Rationale**: Strategy pattern with mocks is reusable pattern
              **Action**: Extract testing pattern as example

           ### Proposed Solutions Summary

           1. **Code Violations** (manual review):
              - Review tools/ce/foo.py:42 - Replace bare except with specific exception
              - Review tools/ce/bar.py:156 - Add troubleshooting guidance
              - Review 6 other files listed in Part 1

           2. **Missing Examples** (documentation needed):
              - Create examples/patterns/error-recovery.py (from PRP-13)
              - Create examples/patterns/strategy-testing.py (from PRP-11)
              - Create 1 other example listed in Part 2

           3. **Prevention**:
              - Add pre-commit hook: ce validate --level 4 (pattern conformance)
              - Run /update-context weekly to detect drift early
              - Update CLAUDE.md when new patterns emerge

           ### Next Steps
           1. Review violations in Part 1 and fix manually
           2. Create missing examples from Part 2
           3. Validate: ce validate --level 4
           4. Update patterns if codebase evolution is intentional
           5. Re-run /update-context to verify drift resolved
       """
       # Format violations by category
       # Classify as automated vs manual fixes
       # Generate solution proposals (automated, manual, prevention)
       # Return markdown report
   ```

4. Integrate drift detection into sync workflow:
   ```python
   # In sync_context() function, add:

   # After updating PRPs, check examples drift
   drift_result = verify_codebase_matches_examples()

   if drift_result["violations"]:
       report = generate_drift_report(
           drift_result["violations"],
           drift_result["drift_score"]
       )

       # Save report
       report_path = Path(".ce/drift-report.md")
       report_path.write_text(report)

       # Log warning
       logger.warning(
           f"Examples drift detected: {drift_result['drift_score']:.1f}%\n"
           f"📊 Report saved: {report_path}\n"
           f"🔧 Review and apply fixes: cat {report_path}"
       )

       # Display summary
       print(f"\n⚠️  Examples Drift Detected: {drift_result['drift_score']:.1f}%")
       print(f"   Violations: {len(drift_result['violations'])}")
       print(f"   Report: {report_path}")
   ```

### Phase 6: Integration & CLI (60 min)

1. Create main sync function:
   ```python
   def sync_context(target_prp: Optional[str] = None) -> Dict[str, Any]:
       """Execute context sync workflow.

       Args:
           target_prp: Optional PRP file path for targeted sync

       Returns:
           {
               "success": True,
               "prps_scanned": 15,
               "prps_updated": 8,
               "prps_moved": 2,
               "ce_updated_count": 8,
               "serena_updated_count": 5,
               "errors": []
           }
       """
       # 1. Discover PRPs
       # 2. For each PRP:
       #    - Read YAML header
       #    - Extract expected functions
       #    - Verify with Serena (if available)
       #    - Update context_sync flags
       #    - Check status transition
       #    - Move file if needed
       # 3. Return summary
   ```

2. Add CLI command handler in `tools/ce/__main__.py`:
   ```python
   def cmd_update_context(args):
       """Handle /update-context command."""
       from .update_context import sync_context

       result = sync_context(target_prp=args.prp if hasattr(args, 'prp') else None)

       # Format output
       print(f"✅ Context sync completed")
       print(f"   PRPs scanned: {result['prps_scanned']}")
       print(f"   PRPs updated: {result['prps_updated']}")
       print(f"   CE updated: {result['ce_updated_count']}")
       print(f"   Serena updated: {result['serena_updated_count']}")

       if result['errors']:
           print(f"\n⚠️  Errors encountered:")
           for error in result['errors']:
               print(f"   - {error}")
   ```

3. Register command in argparse:
   ```python
   # In main() function
   parser_update = subparsers.add_parser('update-context',
       help='Sync CE/Serena with codebase changes')
   parser_update.add_argument('--prp', help='Target specific PRP file')
   parser_update.set_defaults(func=cmd_update_context)
   ```

### Phase 7: Testing and Validation (45 min)

1. Write unit tests in `tools/tests/test_update_context.py`:
   - Test YAML header reading/writing
   - Test function extraction from PRP content
   - Test status transition logic
   - Test file move operations
   - Test error handling (missing files, invalid YAML)

2. Write integration test with real PRP file:
   - Create test PRP in feature-requests/
   - Run sync
   - Verify YAML updated correctly
   - Verify status transition
   - Verify file moved to executed/

3. Test graceful degradation (Serena unavailable):
   - Mock Serena MCP failure
   - Verify sync continues with warnings
   - Verify serena_updated=false set correctly

## 4. Validation Gates

### Gate 1: YAML Operations Work

**Command**:
```bash
cd tools
python3 -c "
import frontmatter
from pathlib import Path

# Test read with frontmatter library
prp_path = Path('../PRPs/executed/PRP-6-markdown-linting.md')
post = frontmatter.load(prp_path)

# Verify structure
assert 'prp_id' in post.metadata, 'Missing prp_id'
assert 'context_sync' in post.metadata, 'Missing context_sync'
assert 'ce_updated' in post.metadata['context_sync'], 'Missing ce_updated'

print(f'✅ YAML operations working - Read PRP {post.metadata[\"prp_id\"]}')
print(f'   context_sync: {post.metadata[\"context_sync\"]}')
"
```

**Success Criteria**:
- Can read YAML headers from real PRP files using frontmatter
- Can parse context_sync section
- No exceptions thrown
- Assertions pass

### Gate 2: Unit Tests Pass

**Command**: `uv run pytest tests/test_update_context.py -v`

**Success Criteria**:
- All unit tests pass
- YAML manipulation tests pass
- Function extraction tests pass
- File move tests pass (using tmp directory)
- Code coverage ≥ 80%

### Gate 3: Integration Test - Full Sync

**Command**: `cd tools && uv run ce update-context`

**Success Criteria**:
- Scans all PRPs/ directories
- Updates context_sync flags correctly
- Transitions appropriate PRPs to executed/
- Moves files atomically
- Logs clear progress messages
- Returns valid summary dict

### Gate 4: Targeted Sync Works

**Command**: `cd tools && uv run ce update-context --prp PRPs/executed/PRP-6-markdown-linting.md`

**Success Criteria**:
- Only processes specified PRP
- Updates YAML correctly
- Returns summary for single PRP

### Gate 5: Drift Detection Works

**Command**: `cd tools && uv run pytest tests/test_update_context.py::test_drift_detection -v`

**Success Criteria**:
- Detects pattern violations (bare except, missing troubleshooting)
- Detects missing examples for critical PRPs
- Calculates drift score correctly
- Generates markdown report with Parts 1 & 2
- Saves report to `.ce/drift-report.md`
- No false positives on valid code

## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
cd tools
uv run pytest tests/test_update_context.py -v
```

### Coverage Requirements

- Unit test coverage: ≥ 80%
- Integration tests for critical paths:
  - Full universal sync
  - Targeted single-PRP sync
  - Graceful degradation (Serena unavailable)
  - File organization (feature-requests → executed)
- Edge cases:
  - Invalid YAML headers
  - Missing files
  - Permission errors
  - Concurrent modifications

### Test Data

Create test PRPs in `tools/tests/fixtures/`:
- `test-prp-new.md` - Status "new", no implementations
- `test-prp-implemented.md` - Status "new", has implementations
- `test-prp-executed.md` - Status "executed", already in executed/

## 6. Rollout Plan

### Phase 1: Development

1. Install dependencies (frontmatter)
2. Implement core YAML operations
3. Implement codebase cross-reference
4. Implement file organization
5. Write unit tests
6. Pass validation gates

### Phase 2: Integration

1. Create slash command file `.claude/commands/update-context.md`
2. Add CLI command handler
3. Test with real PRPs (backup first!)
4. Verify no data corruption
5. Test graceful degradation

### Phase 3: Documentation

1. Update CLAUDE.md with /update-context usage
2. Document in tools/README.md
3. Add examples of command usage
4. Document status transition rules

---

## Research Findings

### Serena Codebase Analysis

**Patterns Found**: 15

1. **YAML Header Handling**: `tools/ce/prp.py:32-80`
   - Uses `yaml.safe_load()` for parsing
   - Validates required fields
   - Pattern: Split content on `---` delimiters

2. **Context Sync**: `tools/ce/context.py:12-51`
   - `sync()` function calculates drift score
   - Returns reindexed_count, files list, drift_score
   - Pattern: Git diff-based file change detection

3. **PRP State Management**: `tools/ce/prp.py:222-358`
   - `start_prp()`, `end_prp()`, `get_active_prp()`
   - Uses `.ce/active_prp_session` state file
   - Pattern: JSON state file with atomic writes

4. **File Operations**: Use `pathlib` throughout codebase
   - `Path.rename()` for atomic moves
   - `Path.exists()` for existence checks
   - Pattern: pathlib over shell commands

5. **Error Handling**: Consistent pattern across modules
   - Raise RuntimeError with troubleshooting guidance
   - Format: `f"Error message\n🔧 Troubleshooting: {guidance}"`
   - No fishy fallbacks - fast failure

6. **Logging**: Standard logging module
   - `logger.info()`, `logger.warning()`, `logger.error()`
   - Pattern: Log at entry/exit of major functions

7. **Serena MCP Integration**: Placeholder functions exist
   - `sync_serena_context()` in context.py:458-486
   - Currently logs warning and continues
   - Pattern: Graceful degradation when MCP unavailable

8. **CLI Command Pattern**: `tools/ce/__main__.py`
   - Subparsers for each command
   - `cmd_*` functions as handlers
   - `set_defaults(func=cmd_*)` for dispatch

9. **Test Patterns**: `tools/tests/`
   - pytest framework
   - Real function calls, no mocks (per CLAUDE.md)
   - Pattern: fixtures in tests/fixtures/

10. **Slash Command Pattern**: `.claude/commands/*.md`
    - Markdown files with command descriptions
    - Usage, examples, implementation details
    - Pattern: User-facing documentation style

11. **YAML Schema**: Consistent across all PRPs
    - Required: prp_id, feature_name, status, created, updated
    - context_sync: {ce_updated, serena_updated, last_sync}
    - Pattern: YAML frontmatter with `---` delimiters

12. **PRP Directory Structure**:
    - `PRPs/feature-requests/` - New/in-progress
    - `PRPs/executed/` - Completed implementations
    - `PRPs/archived/` - Deprecated/superseded
    - Pattern: Status-based file organization

13. **Function Discovery**: Need to implement
    - Regex patterns for `def function_name`, `class ClassName`
    - Check code blocks in PRP content
    - Pattern: AST parsing or regex extraction

14. **Status Transitions**: Inferred from directory structure
    - new → in_progress → executed
    - executed → archived (when superseded)
    - Pattern: Status field + file location must match

15. **Frontmatter Library**: Not currently used
    - Need to add: `uv add python-frontmatter`
    - Provides cleaner API than manual YAML parsing
    - Pattern: `frontmatter.load()`, `frontmatter.dump()`

### Documentation Sources

**Library Docs**: 2
1. python-frontmatter: https://pypi.org/project/python-frontmatter/
   - Clean API for markdown with YAML frontmatter
   - `frontmatter.load(file)` returns post object
   - `post.metadata` dict, `post.content` string

2. pathlib documentation (stdlib)
   - `Path.rename(target)` for atomic moves
   - `Path.read_text()`, `Path.write_text()`

**External Links**: 1
1. Workflow patterns reference: `docs/research/06-workflow-patterns.md:1770`
   - Documents `/update-context [--prp <file>]` command
   - Expected behavior: "Sync CE with codebase"
   - Timing: "After significant changes"

**Context7 Available**: False (not needed - internal tool implementation)

**Serena Available**: True (MCP integration exists, optional for this feature)

---

## Implementation Notes

### KISS Compliance

- Single module: `tools/ce/update_context.py` (~450-500 lines with drift detection)
- Reuse existing functions from context.py and prp.py
- Simple regex for function extraction and pattern detection (no AST complexity)
- Batch operations to minimize I/O
- Modular design: YAML ops, codebase verification, drift detection as separate functions

### No Fishy Fallbacks

```python
# ❌ BAD
try:
    update_yaml(file)
except:
    return {"success": True}  # FISHY!

# ✅ GOOD
try:
    update_yaml(file)
except YAMLError as e:
    raise RuntimeError(
        f"Failed to update YAML in {file}: {e}\n"
        f"🔧 Troubleshooting: Check YAML syntax with: ce prp validate {file}"
    ) from e
```

### Real Functionality Testing

```python
# ✅ GOOD - Test real functions
def test_update_context_sync_flags():
    # Create test PRP file
    test_prp = tmp_path / "test.md"
    test_prp.write_text(VALID_PRP_YAML)

    # Call real function
    update_context_sync_flags(test_prp, ce_updated=True, serena_updated=False)

    # Verify real result
    header, _ = read_prp_header(test_prp)
    assert header["context_sync"]["ce_updated"] is True
    assert header["context_sync"]["serena_updated"] is False
    assert "last_sync" in header["context_sync"]
```

### Error Messages with Troubleshooting

Every exception must include actionable guidance:

```python
if not file_path.exists():
    raise FileNotFoundError(
        f"PRP file not found: {file_path}\n"
        f"🔧 Troubleshooting:\n"
        f"   - Verify file path is correct\n"
        f"   - Check if file was moved or renamed\n"
        f"   - Use: ls {file_path.parent} to list directory"
    )
```

---

## Expected Deliverables

1. **Module**: `tools/ce/update_context.py` (~450-500 lines with drift detection)
2. **Slash Command**: `.claude/commands/update-context.md`
3. **Tests**: `tools/tests/test_update_context.py` (≥25 tests including drift detection, 80% coverage)
4. **CLI Integration**: Updated `tools/ce/__main__.py` with command handler
5. **Documentation**: Updated CLAUDE.md and tools/README.md with usage examples
6. **Drift Report Template**: `.ce/drift-report.md` (generated on first violation detection)

---

## Success Metrics

✅ **Functionality**:
- Universal sync: Updates all PRPs in <10 seconds
- Targeted sync: Updates single PRP in <1 second
- YAML headers: 100% preservation of formatting/comments
- File moves: 100% atomic (no data loss)

✅ **Quality**:
- Test coverage: ≥80%
- No fishy fallbacks: 100% compliance
- Error messages: 100% include troubleshooting
- Logging: Info/warning/error at all major steps

✅ **Integration**:
- Works with Serena MCP when available
- Graceful degradation when Serena unavailable
- Compatible with existing PRP workflow
- No breaking changes to YAML schema

---

## Appendix: Peer Review - Document (2025-10-14)

### Executive Summary

⚠️ **GOOD WITH MODERATE SCOPE ISSUES** - Document quality is excellent, but scope clarifications needed.

**Review Mode**: Context-naive (read as standalone artifact)
**Reviewer**: Claude (Sonnet 4.5)
**Review Date**: 2025-10-14T16:45:00Z

### Strengths Identified

✅ **Excellent Technical Depth**:
- Specific function signatures with clear docstrings
- 7 implementation phases with time estimates
- Comprehensive research findings (15 patterns documented)
- Strong alignment with project quality standards

✅ **Clear Validation Strategy**:
- 5 executable validation gates
- Measurable success criteria
- Good test coverage requirements (≥80%)

✅ **Good Edge Case Coverage**:
- 10 edge cases documented
- Graceful degradation patterns
- Error handling with troubleshooting guidance

### Issues Found and Resolved

#### 1. Scope Clarity (RESOLVED)

**Issue**: "CE Examples Management" mentioned in background but not implemented
- **Fix Applied**: Added note clarifying this is future work, out of scope for PRP-14
- **Location**: Line 44

**Issue**: Drift detection mentioned automated fixes (`/fix-drift`) that don't exist
- **Fix Applied**: Removed all `/fix-drift` references, clarified report is detection-only
- **Locations**: Lines 203, 343-363

#### 2. Specification Completeness (RESOLVED)

**Issue**: Pattern extraction lacked concrete specification
- **Fix Applied**: Added PATTERN_FILES and PATTERN_CHECKS with specific regex patterns
- **Location**: Lines 205-226

**Issue**: No specification for detecting missing examples
- **Fix Applied**: Added `detect_missing_examples_for_prps()` function with clear logic
- **Location**: Lines 269-291

#### 3. Validation Gaps (RESOLVED)

**Issue**: Gate 1 had incomplete/non-functional Python snippet
- **Fix Applied**: Rewrote with functional frontmatter-based code and assertions
- **Location**: Lines 486-511

**Issue**: No validation gate for drift detection feature
- **Fix Applied**: Added Gate 5 with specific drift detection success criteria
- **Location**: Lines 545-555

#### 4. Size Estimates (RESOLVED)

**Issue**: Module size estimate (~300 lines) too low for drift detection scope
- **Fix Applied**: Updated to ~450-500 lines
- **Locations**: Lines 728, 791

**Issue**: Test count underestimated
- **Fix Applied**: Updated from ≥20 to ≥25 tests
- **Location**: Line 793

#### 5. Edge Cases (RESOLVED)

**Missing Edge Cases Added**:
- examples/ directory missing → skip drift detection with info log
- Functions deleted from codebase → mark ce_updated=false
- Multiple PRPs reference same functions → all get ce_updated=true if exists
- YAML comments preservation → frontmatter handles automatically
- Permission errors on file moves → raise RuntimeError with troubleshooting

**Location**: Lines 75-79

#### 6. Two-Way Drift Detection (ADDED)

**User Request**: Detect both code violations AND missing examples for critical PRPs
- **Fix Applied**: Added `detect_missing_examples_for_prps()` function
- **Fix Applied**: Updated drift report template with Part 2 for missing examples
- **Locations**: Lines 198-200, 269-291, 323-339

### Recommendations Not Applied

None - All recommendations were successfully applied.

### Quality Assessment

**Completeness**: ✅ EXCELLENT (all sections detailed, no gaps)
**Clarity**: ✅ EXCELLENT (technical requirements unambiguous after fixes)
**Feasibility**: ✅ GOOD (5-6 hours reasonable with clarifications)
**Testability**: ✅ EXCELLENT (5 gates with executable commands)
**Edge Cases**: ✅ EXCELLENT (10 cases documented)

### Final Verdict

**Status**: ✅ **APPROVED FOR EXECUTION**

This PRP is now ready for implementation. All scope issues resolved, specifications complete, validation strategy sound. The drift detection feature is well-scoped (detection-only, no automated fixes) and has clear success criteria.

**Estimated Effort**: 5-6 hours (appropriate for scope)
**Complexity**: Medium (appropriate rating)
**Risk**: Low (well-researched, clear implementation path)