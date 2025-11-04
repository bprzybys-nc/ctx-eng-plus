---
type: regular
category: pattern
tags: [serena, verification, testing]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Serena Implementation Verification Pattern

## Overview
Pattern for using Serena MCP to verify PRP implementations exist in codebase through semantic code understanding (PRP-16).

## Core Function
**Location**: `tools/ce/update_context.py:798-879`  
**Function**: `verify_implementation_with_serena(expected_functions: List[str]) -> bool`

## Purpose
Replace regex-based verification with semantic symbol lookup:
- Query Serena MCP's `find_symbol` for each expected function/class
- Return `True` only if ALL implementations found
- Graceful degradation when Serena unavailable

## Implementation Pattern

### Direct Serena Import
```python
import mcp__serena as serena
```

**Why direct import**: 
- `mcp_adapter.py` provides file operations, not symbol queries
- `find_symbol` is Serena MCP tool, not wrapped
- Simpler for read-only queries

### Symbol Query Pattern
```python
result = serena.find_symbol(
    name_path="function_name",
    relative_path="tools/ce/",
    include_body=False
)

# Check result
if result and isinstance(result, list) and len(result) > 0:
    # Implementation found
    verified = True
```

### Response Structure
```python
# Success
[{"name_path": "func_name", "kind": "Function", "body_location": {...}}]

# Not found
[]
```

### Graceful Degradation
```python
try:
    import mcp__serena as serena
    # ... verification logic
except (ImportError, ModuleNotFoundError):
    logger.warning("Serena MCP not available - skipping verification")
    return False
```

## Integration Point
Called in `sync_context()` workflow (~line 613):
```python
serena_verified = verify_implementation_with_serena(expected_functions)
```

## Test Coverage
**File**: `tools/tests/test_serena_verification.py`

**Unit Tests** (5):
- All functions found → returns True
- Some missing → returns False  
- Empty list → returns True (nothing to verify)
- Serena unavailable → returns False
- Query exception → returns False

**Integration Tests** (2):
- sync_context integration
- Real Serena MCP (if available)

**E2E Test** (1):
- Full context sync workflow

## Known Limitations
**Hardcoded path**: `relative_path="tools/ce/"`
- Works for 95% of implementations
- Future enhancement: path inference from PRP content

## Usage in Context Sync

### YAML Header Updates
```yaml
context_sync:
  ce_updated: true
  serena_updated: true    # Set when all implementations found
  last_sync: "2025-10-16T14:30:00Z"
  verified_implementations:
    - function_name_1
    - function_name_2
```

### Workflow
1. Extract function names from PRP content
2. Query Serena for each function
3. Update YAML header with results
4. Log verification status

## Error Handling
All errors include 🔧 troubleshooting guidance:
```python
logger.warning(
    "Serena MCP not available - skipping verification\n"
    "🔧 Troubleshooting: Ensure Serena MCP server is configured and running"
)
```

## Related PRPs
- **PRP-9**: Serena MCP Integration (infrastructure)
- **PRP-14**: Update-Context Command (workflow)
- **PRP-15**: Drift Remediation (uses context sync)

## Example Output
```bash
cd tools && uv run ce update-context --prp PRPs/feature-requests/PRP-16-serena-verification.md

# Output:
# ✓ Verified: verify_implementation_with_serena
# Serena verification complete: 1/1 implementations found
# ✅ Context sync completed
```

## Best Practices
1. **Import directly**: Use `import mcp__serena as serena`
2. **Check response type**: Verify `isinstance(result, list)`
3. **Graceful degradation**: Catch ImportError/ModuleNotFoundError
4. **Clear logging**: Debug/info/warning at appropriate levels
5. **All or nothing**: Return True only if ALL functions found
6. **No silent failures**: Log missing implementations with names
