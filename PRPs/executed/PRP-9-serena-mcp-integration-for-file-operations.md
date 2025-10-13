---
prp_id: PRP-9
feature_name: Serena MCP Integration for File Operations
status: executed
created: 2025-10-13T02:33:42.661509
updated: 2025-10-13T12:15:00Z
completed: 2025-10-13T12:15:00Z
complexity: medium
estimated_hours: 3-5
actual_hours: 2.5
dependencies:
updated_by: execute-prp-command
context_sync:
  ce_updated: true
  serena_updated: false
---

# Serena MCP Integration for File Operations

## 1. TL;DR

**Objective**: Serena MCP Integration for File Operations

**What**: Replace local filesystem stubs in PRP-4 implementation with real Serena MCP operations for file creation and symbol-aware code insertion. Includes research phase for MCP availability detection, gracef...

**Why**: Enable functionality described in INITIAL.md with 7 reference examples

**Effort**: Medium (3-5 hours estimated based on complexity)

**Dependencies**:

## 2. Context

### Background

Replace local filesystem stubs in PRP-4 implementation with real Serena MCP operations for file creation and symbol-aware code insertion. Includes research phase for MCP availability detection, graceful fallback strategy, testing infrastructure, and architectural decision documentation.

**Type**: Architectural Enhancement
**Priority**: MEDIUM
**Effort**: 8-12 hours
**Risk**: MEDIUM

### Problem

PRP-4 implementation uses local filesystem stubs instead of Serena MCP for file operations. This was marked as acceptable for MVP but creates technical debt:

```python
# CURRENT (tools/ce/execute.py:530-536)
# FIXME: Placeholder implementation - using local filesystem instead of Serena MCP
# TODO: Replace with mcp__serena__create_text_file(filepath, content) when in MCP context
from pathlib import Path
file_path = Path(filepath)
file_path.parent.mkdir(parents=True, exist_ok=True)
file_path.write_text(content)  # FIXME: Hardcoded local file write
```

**Issues with Current Approach**:

1. ❌ **No code analysis**: Bypasses Serena's semantic understanding
2. ❌ **No symbol awareness**: Naive append instead of intelligent insertion
3. ❌ **Context-dependent**: Won't work in MCP-only environments
4. ❌ **Error handling**: Different failure modes than MCP operations
5. ❌ **Testing complexity**: Can't test MCP-dependent behavior

### Solution

**Research-driven integration strategy**:

1. Investigate Serena MCP availability detection
2. Define graceful fallback behavior when MCP unavailable
3. Implement MCP-based file operations with fallback
4. Create testing strategy for MCP-dependent code
5. Document architectural decision and migration path

**Key Decision Points**:

- When is Serena MCP available? (MCP-only vs standalone CLI)
- Should we auto-detect and fall back to filesystem?
- What's the performance impact of MCP operations?
- How do we test code that requires Serena MCP?
- What's the migration path from current stubs?

### Impact

- ✅ **Code quality**: Leverage Serena's semantic code understanding
- ✅ **Symbol awareness**: Proper insertion after/before symbols
- ✅ **MCP compatibility**: Work in Claude Code and MCP-only contexts
- ✅ **Future-proof**: Align with Context Engineering architecture
- ⚠️ **Complexity**: More sophisticated error handling required
- ⚠️ **Testing**: Need MCP mock/stub infrastructure

## CONTEXT

### Current State

- **execute_phase()**: Uses `Path().write_text()` directly
- **_add_functions_to_file()**: Naive append to end of file
- **Testing**: Works with local filesystem only
- **Status**: All FIXME comments in place, documented as MVP limitation

### Serena MCP Tools Available

```python
# File Operations
mcp__serena__create_text_file(relative_path: str, content: str)
mcp__serena__read_file(relative_path: str) -> str

# Symbol Operations (More sophisticated than current implementation)
mcp__serena__replace_symbol_body(name_path: str, relative_path: str, body: str)
mcp__serena__insert_after_symbol(name_path: str, relative_path: str, body: str)
mcp__serena__insert_before_symbol(name_path: str, relative_path: str, body: str)

# Code Understanding
mcp__serena__find_symbol(name_path: str) -> Dict
mcp__serena__get_symbols_overview(relative_path: str) -> Dict
```

### Research Questions

**1. MCP Availability Detection**

- How to detect if Serena MCP is available at runtime?
- Is there a standard MCP capability check?
- What happens when MCP call fails? (exception type, error message)

**2. Fallback Strategy**

- Should we fall back to filesystem automatically?
- Or fail fast and require MCP for execution?
- What about mixed mode (some MCP, some filesystem)?

**3. Performance Implications**

- Overhead of MCP calls vs direct file operations?
- Batch operations possible? (multiple edits in one call)
- Impact on large file operations?

**4. Testing Strategy**

- How to mock Serena MCP in tests?
- Should we create a Serena MCP stub/fake for testing?
- Can we test real MCP integration in CI?

**5. Error Handling**

- MCP-specific errors vs filesystem errors
- Retry logic for transient MCP failures?
- User-facing error messages for MCP issues

## TECHNICAL REQUIREMENTS

### Phase 1: Research & Architecture (3 hours)

**Deliverables**:

- `docs/decisions/ADR-001-serena-mcp-integration.md`
- MCP availability detection POC
- Fallback strategy decision
- Testing approach specification

**Investigation Tasks**:

1. **MCP Availability Check**:

   ```python
   def is_serena_mcp_available() -> bool:
       """Check if Serena MCP is available in current context."""
       try:
           # Attempt to import MCP tools
           from mcp__serena import read_file
           # Try a minimal operation
           # ... test code ...
           return True
       except (ImportError, Exception):
           return False
   ```

2. **Fallback Decision Matrix**:

   | Context | Serena Available? | Behavior |
   |---------|-------------------|----------|
   | Claude Code (MCP) | Yes | Use Serena MCP |
   | Standalone CLI | No | Fallback to filesystem |
   | Test Suite | Mocked | Use MCP mock/fake |
   | CI/CD | Configurable | ENV var control |

3. **Performance Baseline**:
   - Benchmark: Create 10 files with MCP vs filesystem
   - Benchmark: Insert 10 functions with MCP vs naive append
   - Measure: MCP call latency distribution
   - Decision: Is performance acceptable?

4. **Testing Strategy Options**:
   - **Option A**: Mock MCP tools in tests (fast, no real MCP needed)
   - **Option B**: Serena MCP fake/stub (more realistic, still fast)
   - **Option C**: Real Serena MCP in test environment (slow, accurate)
   - **Decision**: Hybrid approach (mocks for unit, real for E2E?)

### Phase 2: MCP Detection & Fallback Infrastructure (2 hours)

**Goal**: Implement runtime detection and graceful fallback

**Files to Modify**:

- `tools/ce/execute.py` - Add MCP detection functions
- `tools/ce/mcp_adapter.py` - Create MCP abstraction layer (NEW)

**Key Functions**:

```python
# tools/ce/mcp_adapter.py (NEW)
def is_mcp_available() -> bool:
    """Detect if Serena MCP is available at runtime."""

def create_file_with_mcp(filepath: str, content: str) -> Dict[str, Any]:
    """Create file using Serena MCP or fallback to filesystem."""

def insert_code_with_mcp(
    filepath: str,
    code: str,
    mode: str = "append"  # append | before_symbol | after_symbol
) -> Dict[str, Any]:
    """Insert code using Serena MCP symbol operations or fallback."""

def get_mcp_status() -> Dict[str, Any]:
    """Get MCP availability status for diagnostics."""
```

**Fallback Logic**:

```python
def create_file_with_mcp(filepath: str, content: str) -> Dict[str, Any]:
    if is_mcp_available():
        try:
            mcp__serena__create_text_file(filepath, content)
            return {"success": True, "method": "mcp", "filepath": filepath}
        except Exception as e:
            # Log warning but don't fail
            print(f"⚠️  MCP call failed, falling back to filesystem: {e}")

    # Fallback to filesystem
    from pathlib import Path
    file_path = Path(filepath)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content)
    return {"success": True, "method": "filesystem", "filepath": filepath}
```

### Phase 3: Replace File Creation Stubs (1.5 hours)

**Goal**: Replace `execute_phase()` file creation with MCP adapter

**Changes**:

```python
# BEFORE (execute.py:527-536)
content = _generate_file_content(filepath, description, phase)
# FIXME: Placeholder implementation - using local filesystem instead of Serena MCP
from pathlib import Path
file_path = Path(filepath)
file_path.parent.mkdir(parents=True, exist_ok=True)
file_path.write_text(content)  # FIXME: Hardcoded local file write
files_created.append(filepath)

# AFTER
content = _generate_file_content(filepath, description, phase)
result = create_file_with_mcp(filepath, content)
if not result["success"]:
    raise RuntimeError(f"Failed to create {filepath}: {result.get('error')}")
files_created.append(filepath)
print(f"  📝 Created via {result['method']}: {filepath}")
```

### Phase 4: Replace Function Insertion Stubs (2 hours)

**Goal**: Replace naive append with Serena MCP symbol operations

**Strategy**: Use `mcp__serena__insert_after_symbol` for intelligent insertion

**Changes**:

```python
# BEFORE (_add_functions_to_file, execute.py:648-651)
for func_entry in functions:
    full_code = func_entry.get("full_code", "")
    if full_code:
        new_content += "\n\n" + full_code  # FIXME: Naive append

# AFTER
for func_entry in functions:
    full_code = func_entry.get("full_code", "")
    if full_code:
        # Use Serena MCP to insert intelligently
        result = insert_code_with_mcp(
            filepath=filepath,
            code=full_code,
            mode="after_last_symbol"  # Insert after last function/class
        )
        if not result["success"]:
            # Fallback: naive append if MCP fails
            new_content += "\n\n" + full_code
```

**Symbol Detection Logic**:

```python
def insert_code_with_mcp(filepath: str, code: str, mode: str) -> Dict[str, Any]:
    if not is_mcp_available():
        return {"success": False, "method": "fallback_required"}

    try:
        # Get file symbols to find insertion point
        symbols = mcp__serena__get_symbols_overview(filepath)
        if symbols and len(symbols) > 0:
            last_symbol = symbols[-1]["name_path"]
            mcp__serena__insert_after_symbol(last_symbol, filepath, code)
            return {"success": True, "method": "mcp_symbol_aware"}
        else:
            # No symbols found, append to end
            current = mcp__serena__read_file(filepath)
            mcp__serena__create_text_file(filepath, current + "\n\n" + code)
            return {"success": True, "method": "mcp_append"}

    except Exception as e:
        return {"success": False, "error": str(e), "method": "mcp_failed"}
```

### Phase 5: Testing Infrastructure (2.5 hours)

**Goal**: Enable testing of MCP-dependent code

**Approach**: Create MCP fake for testing

```python
# tools/tests/mcp_fake.py (NEW)
class SerenaFake:
    """Fake Serena MCP implementation for testing."""

    def __init__(self):
        self.files = {}  # In-memory file storage

    def create_text_file(self, relative_path: str, content: str):
        self.files[relative_path] = content

    def read_file(self, relative_path: str) -> str:
        if relative_path not in self.files:
            raise FileNotFoundError(f"{relative_path} not found")
        return self.files[relative_path]

    def get_symbols_overview(self, relative_path: str) -> List[Dict]:
        # Parse content for symbols (simple Python parser)
        content = self.read_file(relative_path)
        # ... symbol extraction logic ...
        return symbols

    def insert_after_symbol(self, name_path: str, relative_path: str, body: str):
        # Insert code after specified symbol
        content = self.read_file(relative_path)
        # ... insertion logic ...
        self.files[relative_path] = new_content

@pytest.fixture
def serena_fake():
    """Provide Serena MCP fake for testing."""
    fake = SerenaFake()
    # Monkey-patch MCP imports
    sys.modules['mcp__serena'] = fake
    yield fake
    del sys.modules['mcp__serena']
```

**Tests to Add**:

```python
def test_execute_phase_with_mcp_available(serena_fake):
    """Test execute_phase uses MCP when available."""

def test_execute_phase_fallback_when_mcp_unavailable():
    """Test execute_phase falls back to filesystem when MCP unavailable."""

def test_insert_code_symbol_aware(serena_fake):
    """Test code insertion uses symbol awareness."""

def test_mcp_failure_graceful_fallback(serena_fake):
    """Test graceful fallback when MCP operation fails."""
```

### Phase 6: Documentation & Rollout (1.5 hours)

**Deliverables**:

- ADR-001 finalized with decision rationale
- Update execute.py docstrings with MCP behavior
- Update CLAUDE.md with MCP integration patterns
- Create migration guide for other file operations

## IMPLEMENTATION PLAN

1. **Phase 1: Research** (3h) → ADR-001 document + decisions
2. **Phase 2: Infrastructure** (2h) → mcp_adapter.py + detection
3. **Phase 3: File Creation** (1.5h) → Replace create_text_file stubs
4. **Phase 4: Symbol Insertion** (2h) → Replace function insertion
5. **Phase 5: Testing** (2.5h) → MCP fake + test coverage
6. **Phase 6: Documentation** (1.5h) → Finalize ADR + docs

**Total**: 12.5 hours

## ACCEPTANCE CRITERIA

- [ ] ADR-001 document created with architectural decision rationale
- [ ] MCP availability detection works correctly
- [ ] Graceful fallback to filesystem when MCP unavailable
- [ ] File creation uses `mcp__serena__create_text_file`
- [ ] Function insertion uses `mcp__serena__insert_after_symbol`
- [ ] Symbol-aware insertion (not naive append)
- [ ] All FIXME comments removed from execute.py
- [ ] Serena MCP fake created for testing
- [ ] Tests pass with and without MCP availability
- [ ] Performance acceptable (<100ms overhead per MCP call)
- [ ] Error messages user-friendly for MCP failures
- [ ] Documentation updated (ADR, docstrings, CLAUDE.md)

## RISKS

**Risk**: MEDIUM

**Challenges**:

1. **MCP availability detection**: May not work in all environments
2. **Fallback complexity**: Managing two code paths increases maintenance
3. **Testing**: MCP fake may not match real MCP behavior exactly
4. **Performance**: MCP calls slower than direct filesystem operations
5. **Error handling**: Different failure modes for MCP vs filesystem

**Mitigation**:

- Start with simple detection (try/catch import)
- Document fallback behavior clearly
- Compare MCP fake behavior with real MCP in E2E tests
- Benchmark performance early, optimize if needed
- Unified error handling layer (mcp_adapter.py)

## NON-GOALS

- ❌ Full MCP feature parity (only file/symbol operations needed)
- ❌ MCP abstraction for other CE tools (scope limited to execute.py)
- ❌ Real-time MCP availability monitoring (check once at startup)
- ❌ MCP-specific optimizations (accept performance trade-off)
- ❌ Backward compatibility with pre-MCP code (breaking change acceptable)

## OPEN QUESTIONS

1. Should MCP be required or optional for PRP execution?
   - **Option A**: Required (fail fast if unavailable)
   - **Option B**: Optional (fallback to filesystem)
   - **Recommendation**: Optional for MVP, required in future

2. What's the performance SLA for MCP operations?
   - **Target**: <100ms per operation
   - **Fallback**: If >200ms, use filesystem for that operation

3. How to handle MCP version incompatibilities?
   - **Strategy**: Check MCP API version, error if incompatible

4. Should we log MCP usage for analytics?
   - **Recommendation**: Yes, track MCP vs filesystem usage ratio

### Constraints and Considerations

See INITIAL.md for additional considerations

### Documentation References

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
