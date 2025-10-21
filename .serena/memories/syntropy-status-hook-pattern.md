# Syntropy Status Hook - Cache-Based Architecture

## Pattern: SessionStart Hook with MCP Data via Cache

**Location**: `tools/scripts/session-startup.sh`, `tools/scripts/syntropy-status.py`, `tools/scripts/cache-syntropy-health.py`

**Problem Solved**: SessionStart hooks can't directly call MCP tools (execution context limitation), but need to display real MCP healthcheck data.

**Solution**: Cache-based architecture where Claude Code updates cache, hooks read from cache.

## Architecture

```
Claude Code (MCP access)
  → mcp__syntropy__syntropy_healthcheck
  → cache-syntropy-health.py (writes JSON)
  → .ce/syntropy-health-cache.json

SessionStart Hook (no MCP access)
  → session-startup.sh
  → syntropy-status.py (reads cache)
  → Display real healthcheck data
```

## Key Files

1. **session-startup.sh**: Unified startup hook
   - Runs context drift check
   - Calls syntropy-status.py for MCP health
   - Lists available MCP tools
   - Timeout: 12s (sufficient for all checks)

2. **syntropy-status.py**: Cache reader + formatter
   - Reads `.ce/syntropy-health-cache.json`
   - Displays server status with emojis
   - Shows stale cache warnings (>5 min)
   - Error guidance if cache missing

3. **cache-syntropy-health.py**: Cache updater
   - Accepts healthcheck JSON via stdin
   - Writes to `.ce/syntropy-health-cache.json`
   - Adds cache metadata (timestamp)

## Benefits

1. **Fast**: ~200ms cache read vs 2-3s MCP call
2. **Real data**: No hardcoded fallbacks (violates "No Fishy Fallbacks" policy)
3. **Graceful degradation**: Stale/missing cache shows errors with troubleshooting
4. **Single hook**: Consolidated from 3 separate hooks (better timeout management)

## Benefits Over Previous Implementation

**Before (PRP-27 identified issues)**:
- ❌ Hardcoded static data (FIXME: "Static data from recent healthcheck")
- ❌ Silent failures on session resume (5s timeout too short)
- ❌ No real MCP integration
- ❌ Multiple separate hooks (timeout fragility)

**After (PRP-27 solution)**:
- ✅ Real MCP healthcheck data via cache
- ✅ 12s timeout (sufficient margin for all checks)
- ✅ Graceful error handling with troubleshooting
- ✅ Single unified hook script

## Usage Pattern

**Refresh cache** (from Claude Code session):
```bash
# The healthcheck is called automatically and cached
# Manual refresh if needed:
mcp__syntropy__syntropy_healthcheck(detailed=True)
# Results written to .ce/syntropy-health-cache.json
```

**Hook configuration** (`.claude/settings.local.json`):
```json
{
  "hooks": {
    "SessionStart": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "PROJECT_ROOT=$(git rev-parse --show-toplevel) && cd \"$PROJECT_ROOT/tools\" && bash scripts/session-startup.sh",
        "timeout": 12
      }]
    }]
  }
}
```

## Cache File Format

`.ce/syntropy-health-cache.json`:
```json
{
  "cached_at": "2025-10-21T07:20:22.324Z",
  "data": {
    "syntropy": {"version": "0.1.0", "status": "healthy"},
    "servers": [
      {"server": "serena", "status": "healthy", "connected": true},
      ...
    ],
    "summary": {"total": 9, "healthy": 9, "degraded": 0, "down": 0}
  }
}
```

**TTL**: 5 minutes (after which status displays stale warning)

## Error Handling Examples

**Missing cache**:
```
❌ Syntropy health cache not found
🔧 Run this in Claude Code to refresh:
   Call mcp__syntropy__syntropy_healthcheck and pipe to cache-syntropy-health.py
```

**Stale cache** (>5 minutes):
```
⚠️ Cache is stale (>5 minutes old)
🔧 Consider refreshing healthcheck
[still displays data]
```

## Anti-Patterns Avoided

❌ **Static hardcoded data**: Old script had FIXME with fake server list
❌ **Silent failures**: Hooks timing out without user feedback
❌ **Multiple hooks racing**: 3 separate 5s hooks (timeout fragility)
❌ **Direct MCP calls in hooks**: Not possible, would fail
❌ **Fishy fallbacks**: No fake success when real data unavailable

## Implementation Notes

**Why cache instead of direct MCP call?**
- SessionStart hooks run in shell context (no MCP access)
- MCP tools only callable from Claude Code execution context
- Cache provides fast reads (~200ms) vs slow MCP calls (2-3s)
- Cache survives across sessions (shows last known state)

**Timeout calculation** (12s total):
- uv venv initialization: ~2-3s
- Context drift check: ~1-2s
- Syntropy status (cache read): ~200ms
- MCP tools list: ~500ms
- Buffer for slow systems: ~6-7s

## Related Files

- **Policy**: CLAUDE.md "No Fishy Fallbacks" (line 47)
- **PRP**: PRPs/executed/PRP-27-syntropy-status-hook.md
- **Example**: examples/syntropy-status-hook-system.md
- **Tests**: Validated via manual testing (Gates 1-4 passed)

## Testing Strategy

**Gate 1**: Architecture verification
- Single unified hook ✅
- Clear error boundaries ✅
- Timeout margin verified ✅

**Gate 2**: MCP integration
- No hardcoded data ✅
- Real healthcheck via cache ✅
- Error messages with guidance ✅

**Gate 3**: Functional testing
- Fresh session shows all checks ✅
- Cache read displays real data ✅
- Missing cache shows error ✅

**Gate 4**: Error handling
- Missing cache: actionable guidance ✅
- Stale cache: warning displayed ✅
- Graceful degradation ✅
