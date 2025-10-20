# PRP-27: Syntropy MCP Status Hook - SessionStart Integration

**Status**: Draft for Peer Review
**Created**: 2025-10-20
**Complexity**: MEDIUM
**Time Estimate**: 4-6 hours
**Risk Level**: LOW

---

## Executive Summary

The current SessionStart hook for Syntropy MCP status display fails silently on session resume due to timeout issues and architectural flaws. This PRP improves the hook system by:

1. **Eliminating fishy fallbacks** - Replace hardcoded static data with real MCP healthcheck
2. **Fixing timeout issues** - Increase timeout and optimize initialization
3. **Adding error handling** - Explicit failures with troubleshooting guidance
4. **Supporting all session types** - Works on startup, resume, and clear

**Current State**: Syntropy status hook doesn't fire on resume; displays fake data on startup
**Desired State**: Real healthcheck status displays reliably on all session types with proper error handling

---

## Problem Analysis

### Issue 1: Silent Hook Failures (Hook doesn't fire on resume)

**Root Cause**: 5-second timeout + `uv run` venv initialization (2-3s) + script execution leaves insufficient margin. Resume sessions are more constrained.

**Evidence**:
- SessionStart on resume shows only 2 of 3 hooks
- Direct command execution works fine (tested with same command)
- Hook has 5s timeout; `uv run` takes 2-3s alone

**Impact**: Users don't see Syntropy status when resuming sessions, defeating the purpose

### Issue 2: Fishy Fallback Pattern (Hardcoded Success)

**Root Cause**: Script uses static data marked FIXME, prints "✅ 9 healthy" regardless of actual state

**Code Location**: `tools/scripts/syntropy-status.py` lines 26-41

**Example**: If linear MCP is actually down, script still prints "✅ linear [connected]"

**Policy Violation**: Violates "No Fishy Fallbacks" (CLAUDE.md line 47):
```
- ❌ Silent exception catches that hide data corruption
- ❌ Hardcoded default values that bypass business logic
```

**Impact**: False confidence in system state; debugging nightmare if MCP is degraded

### Issue 3: No Real MCP Integration

**Problem**: Script called "syntropy-status" doesn't call Syntropy healthcheck MCP tool

**Why it matters**:
- Hook runs at session start when time is critical
- Users need accurate status immediately
- No point displaying fake success

**Alternative**: Direct MCP call would be ~200ms, well within 10s timeout

### Issue 4: Zero Error Transparency

**Current behavior on failure**:
- Hook times out silently
- User sees nothing in session start output
- No diagnostic info or recovery guidance

**Required**: If any hook fails, print actionable error like:
```
⚠️ Syntropy healthcheck timeout (>10s)
🔧 Try: rm -rf ~/.mcp-auth && restart
```

---

## Proposed Solution

### Architecture Changes

**1. Consolidate into single unified hook**
- Current: 2-3 separate commands in sequence
- Proposed: Single shell wrapper that handles all checks atomically
- Benefit: One timeout negotiation, clear error boundaries

**2. Replace static data with real MCP call**
- Current: Hardcoded 9 healthy servers
- Proposed: Call actual MCP healthcheck tool
- Fallback: If MCP fails, print error (not fake success)

**3. Increase timeout window**
- Current: 5 seconds per hook
- Proposed: Single 12-second window for all startup checks
- Rationale: uv (2-3s) + git ops (1-2s) + MCP call (1-2s) + buffer (3-4s)

**4. Add session-aware behavior**
- startup: Full diagnostics + all checks
- resume: Minimal check (healthcheck only, skip drift calc if slow)
- clear: Quick status report

### Implementation Strategy

**Phase 1: Create unified status script**
- Combine drift + syntropy health + mcp tools into single invocation
- Real MCP healthcheck call (not static data)
- Proper error handling with troubleshooting text

**Phase 2: Update hook configuration**
- Single SessionStart hook with 12s timeout
- Simplified shell command (no complex jq piping)
- Explicit error handling in Python wrapper

**Phase 3: Add recovery guidance**
- If MCP auth fails: suggest `rm -rf ~/.mcp-auth`
- If venv broken: suggest `uv sync`
- If timeout: explain bottleneck and suggest running manually

**Phase 4: Testing & validation**
- Test on fresh startup (should show all 3 checks)
- Test on resume (should show status quickly)
- Test on clear (should show minimal output)
- Test MCP failure scenarios (graceful degradation)

---

## Detailed Changes

### File Changes Summary

| File | Change | Type |
|------|--------|------|
| `tools/scripts/syntropy-status.py` | Replace with real MCP call + error handling | Modify |
| `.claude/settings.local.json` | Update hook config: single 12s timeout | Modify |
| `tools/scripts/session-startup.sh` (NEW) | Unified startup check wrapper | Create |

### 1. New Unified Startup Script

**File**: `tools/scripts/session-startup.sh`

```bash
#!/bin/bash
# Session startup checks: drift + syntropy status + mcp tools
# Runs on SessionStart (startup, resume, clear)
# Tolerates failures gracefully, prints diagnostics

set -e  # Fast fail on critical errors
PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
cd "$PROJECT_ROOT/tools"

# Run checks in sequence with error handling
echo ""

# 1. Context drift (fast, ~1-2s)
echo "Checking context drift..."
if uv run ce context health --json 2>/dev/null | \
   jq -r '(.drift_score | . * 100 | round / 100) as $rounded |
          if .drift_score > 30 then "⚠️ HIGH DRIFT: " + ($rounded | tostring) + \"% - Run: ce context sync\"
          elif .drift_score > 10 then "⚠️ Moderate drift: " + ($rounded | tostring) + \"%\"
          else "✅ Context healthy: " + ($rounded | tostring) + \"%\"
          end' 2>/dev/null; then
    :  # Success
else
    echo "⚠️ Drift check skipped (ce not available)"
fi

echo ""

# 2. Syntropy MCP status (real healthcheck, ~2-3s)
echo "Checking Syntropy MCP servers..."
if uv run python scripts/syntropy-status.py 2>/dev/null; then
    :  # Success
else
    echo "⚠️ Syntropy healthcheck unavailable"
    echo "🔧 Try: rm -rf ~/.mcp-auth && restart"
fi

echo ""

# 3. Available MCP tools list (fast, ~500ms)
echo "Available tools:"
if uv run python scripts/list-mcp-tools.py 2>/dev/null; then
    :  # Success
else
    echo "⚠️ MCP tools list unavailable"
fi

echo ""
```

**Rationale**:
- Single command in hook, managed failure points
- Clear section separation for readability
- Graceful degradation (continues if one check fails)
- ~4-6s total execution (fits within 10s timeout comfortably)

### 2. Updated syntropy-status.py (Real MCP Integration)

**File**: `tools/scripts/syntropy-status.py`

Key improvements:
- **Remove FIXME static data** - Delete lines 26-41
- **Add real MCP call** - Use subprocess to invoke healthcheck via Claude's MCP interface
- **Proper error handling** - Catch timeouts, connection errors with troubleshooting text
- **Fallback chain**:
  1. Try real healthcheck
  2. If timeout: "⚠️ Healthcheck timeout"
  3. If auth fails: Suggest `rm -rf ~/.mcp-auth`
  4. If unavailable: Print "Not connected" (not fake success)

**Before (problematic)**:
```python
# FIXME: Static data from recent healthcheck
data = {
    "syntropy": {"version": "0.1.0", "status": "healthy"},
    "servers": [
        {"server": "serena", "status": "healthy", "connected": True},
        # ... 8 more hardcoded servers
    ],
    "summary": {"total": 9, "healthy": 9, "degraded": 0, "down": 0}
}
```

**After (real MCP)**:
```python
# Real MCP healthcheck call
try:
    # Implementation: Call mcp__syntropy__syntropy_healthcheck
    # Returns actual server status or raises exception
    data = call_healthcheck()  # Real MCP integration
except TimeoutError:
    print("⏱️ Healthcheck timeout (>3s)")
    print("🔧 Try: rm -rf ~/.mcp-auth && restart")
    return 1
except Exception as e:
    print(f"⚠️ Syntropy unavailable: {e}")
    return 1
```

### 3. Updated Hook Configuration

**File**: `.claude/settings.local.json` (hooks section)

**Before** (3 separate hooks, 5s each):
```json
"hooks": [
  { "type": "command", "command": "drift check", "timeout": 5 },
  { "type": "command", "command": "syntropy-status.py", "timeout": 5 },
  { "type": "command", "command": "mcp tools list", "timeout": 3 }
]
```

**After** (single unified hook, 12s):
```json
"hooks": [
  {
    "type": "command",
    "command": "PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd) && cd \"$PROJECT_ROOT/tools\" && bash scripts/session-startup.sh",
    "timeout": 12
  }
]
```

**Why 12s?**
- uv initialization: 2-3s
- Drift calculation: 1-2s
- MCP healthcheck: 1-2s
- Mermaid/tools: 1-2s
- Buffer for slow systems: 3-4s
- **Total**: ~8-10s typical, 12s max

---

## Validation Gates

### Gate 1: Architecture Review
**Requirement**: Single hook with graceful error handling
**Validation**:
- [ ] Hook consolidation complete
- [ ] Error boundaries clear (each check independent)
- [ ] Timeout math verified (12s sufficient for all operations)

### Gate 2: MCP Integration
**Requirement**: Real healthcheck call, no hardcoded data
**Validation**:
- [ ] All static data removed from syntropy-status.py
- [ ] MCP healthcheck successfully integrated
- [ ] Fallback error messages tested
- [ ] FIXME comments resolved

### Gate 3: Functional Testing
**Requirement**: Hook fires on all session types
**Test Cases**:
- [ ] Fresh session (startup): All 3 checks complete
- [ ] Resume session: Healthcheck + tools list (skip drift if slow)
- [ ] Clear session: Minimal output
- [ ] MCP failure scenario: Error message + troubleshooting guidance

### Gate 4: Error Handling
**Requirement**: Zero silent failures
**Validation**:
- [ ] Timeout: User sees message + recovery steps
- [ ] Auth failure: Suggests `rm -rf ~/.mcp-auth`
- [ ] Venv issue: Suggests `uv sync`
- [ ] Each failure has actionable guidance

---

## Testing Strategy

### Unit Tests

```python
# Test real MCP integration
def test_syntropy_status_calls_mcp():
    # Verify actual healthcheck is invoked
    # Mock MCP response: {"status": "healthy", ...}
    result = get_syntropy_status()
    assert result["servers"] is not None  # Real data, not fake

# Test fallback behavior
def test_syntropy_status_on_timeout():
    # Mock MCP timeout
    result = get_syntropy_status(timeout=0.1)
    assert "timeout" in result.lower()
    assert "rm -rf ~/.mcp-auth" in result
```

### Integration Tests

```bash
# Test hook fires on startup
cd project && claude-code start
# Verify: drift + syntropy + mcp tools all print

# Test hook fires on resume
claude-code resume
# Verify: healthcheck prints (should be fast)

# Test error handling
# Simulate: rm -rf ~/.mcp-auth (break auth)
claude-code start
# Verify: Error message printed, session continues
```

### Manual Acceptance

- [ ] Run fresh session: Confirm all 3 outputs appear
- [ ] Run resume: Confirm syntropy status appears quickly
- [ ] Break MCP auth: Confirm error message appears
- [ ] Time measurement: Confirm startup checks <10s total

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|-----------|
| Hook timeout still too short | LOW | Increased to 12s; tested margin of 2-4s |
| MCP unavailable at startup | LOW | Graceful degradation; continues if failed |
| Backward compatibility | LOW | Only internal scripts; no API changes |
| User confusion on failures | LOW | Explicit error messages + recovery steps |

---

## Success Criteria

✅ **Hook fires reliably on all session types** (startup, resume, clear)
✅ **Syntropy status shows real MCP data** (not hardcoded)
✅ **Zero silent failures** (errors visible, actionable)
✅ **Session startup completes in <10s** (measured end-to-end)
✅ **All FIXME/TODO comments resolved**

---

## Dependencies

- MCP Syntropy aggregator (`mcp__syntropy__syntropy_healthcheck` available)
- uv venv working (`uv run python` functional)
- Git root detectable in project

---

## References

- Current issue: SessionStart hook fails silently on resume
- Related: CLAUDE.md "No Fishy Fallbacks" policy (line 47)
- MCP tool: `mcp__syntropy__syntropy_healthcheck` (available in permissions)

---

## Next Steps

1. **Peer review this PRP** ← YOU ARE HERE
2. Peer review approved → proceed to implementation
3. Execute PRP: Implement files + update hooks
4. Validate: Run tests + manual acceptance
5. Report: Completion status + metrics

