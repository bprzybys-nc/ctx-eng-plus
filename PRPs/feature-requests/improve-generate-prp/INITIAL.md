# Feature: Improve /generate-prp Implementation Quality

## FEATURE

Address gaps identified in generate-prp code review to improve robustness and maintainability.

**Objective**: Close implementation gaps in PRP generation tool (tools/ce/generate.py)

**What to Build**:
1. Comprehensive test suite (15+ test cases covering all phases)
2. Code cleanup (remove deprecated functions, resolve TODOs)
3. Documentation clarity (linting ownership, heartbeat status)

**Acceptance Criteria**:
1. Test suite exists at `tools/tests/test_generate.py` with 15+ passing tests
2. All deprecated code removed (`_update_linear_issue()`)
3. All TODO/FIXME comments resolved or documented
4. Linting workflow clearly documented (Python vs Claude Code responsibility)
5. Solo heartbeat status clarified in documentation
6. All tests pass: `uv run pytest tests/test_generate.py -v`

**Priority**: P1 (Critical) - Core tool needs test coverage

**Effort Estimate**: 4-6 hours

## EXAMPLES

**Test Structure** (similar to existing test patterns):

```python
# tests/test_generate.py
import pytest
from ce.generate import (
    parse_initial_md,
    extract_code_examples,
    research_codebase,
    synthesize_prp_content,
    check_prp_completeness
)

def test_parse_initial_md_complete():
    """Test parsing complete INITIAL.md with all sections."""
    result = parse_initial_md("fixtures/complete-initial.md")
    assert result["feature_name"] == "User Authentication System"
    assert "FEATURE" in result
    assert len(result["examples"]) > 0

def test_parse_initial_md_missing_required():
    """Test parsing fails when FEATURE section missing."""
    with pytest.raises(ValueError, match="Required FEATURE section missing"):
        parse_initial_md("fixtures/missing-feature.md")

def test_research_codebase_serena_unavailable():
    """Test graceful degradation when Serena MCP unavailable."""
    # Mock Serena failure
    result = research_codebase("Feature Name", [], "Feature text")
    assert result["patterns"] == []
    assert result["status"] == "degraded"

def test_completeness_validation():
    """Test PRP completeness check identifies missing sections."""
    result = check_prp_completeness("fixtures/incomplete-prp.md")
    assert not result["complete"]
    assert "Implementation Steps" in result["missing_sections"]
```

**Cleanup Example**:

```python
# BEFORE (deprecated function at L1763-1799)
def _update_linear_issue(...):
    """DEPRECATED: Use _update_linear_issue_with_resilience instead."""
    # FIXME: Placeholder - replace with actual Linear MCP call
    ...

# AFTER
# Delete entire function - not called anywhere
```

**Documentation Fix**:

```markdown
<!-- BEFORE (.claude/commands/generate-prp.md) -->
## Implementation Details
- **Tests**: `tools/tests/test_generate.py` (24 tests)

<!-- AFTER -->
## Implementation Details
- **Module**: `tools/ce/generate.py` (1896 lines)
- **Tests**: `tools/tests/test_generate.py` (15+ tests covering all phases)
- **Linting**: Performed by Claude Code (not Python), see "Linting Workflow" section
- **Solo Heartbeat**: Not implemented (batch mode only)
```

## DOCUMENTATION

**Testing References**:
- [pytest documentation](https://docs.pytest.org/)
- Existing test patterns: `tools/tests/test_init_project.py`
- Mocking guide: `tools/tests/test_prp.py` (for mock strategies)

**Code Quality Standards** (from CLAUDE.md):
- Functions: 50 lines max
- Files: 500 lines max
- KISS principle
- Fast failure with actionable errors

**Related Files**:
- `tools/ce/generate.py` (1896 lines - main implementation)
- `.claude/commands/generate-prp.md` (452 lines - slash command docs)
- `tools/ce/linear_mcp_resilience.py` (resilience layer)

## OTHER CONSIDERATIONS

**Testing Challenges**:
- **MCP Integration**: Need to mock Serena, Context7, Linear, Sequential Thinking
- **File I/O**: Need fixtures for INITIAL.md variations
- **External Dependencies**: WebFetch calls need mocking

**Breaking Changes**:
- None - all changes are internal improvements
- No API changes to `generate_prp()` function signature

**Security**:
- No new security concerns (cleanup only)
- Ensure test fixtures don't leak credentials

**Performance**:
- Tests should complete in <10s total
- Use mocks to avoid actual MCP calls

**Edge Cases**:
- INITIAL.md with Unicode characters
- Very large INITIAL.md files (>100KB)
- Malformed YAML in existing PRPs
- Linear auth failures during tests

**Rollback Plan**:
- Tests are additive (no risk)
- Deprecated code removal can be reverted if needed (unlikely)
