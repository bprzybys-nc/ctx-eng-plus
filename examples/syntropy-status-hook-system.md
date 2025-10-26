# Syntropy Status Hook System

## Overview

The session startup hook displays real Syntropy MCP healthcheck status using a cache-based architecture:

1. **Cache File**: `.ce/syntropy-health-cache.json` - Contains recent healthcheck results
2. **Display Script**: `syntropy-status.py` - Reads from cache and displays status
3. **Cache Script**: `cache-syntropy-health.py` - Updates cache with fresh healthcheck data
4. **Unified Hook**: `session-startup.sh` - Runs all startup checks (drift + syntropy + tools)

## How It Works

### Session Startup Flow

```
SessionStart Hook → session-startup.sh
                    ├── Context drift check
                    ├── Syntropy status (from cache)
                    └── MCP tools list
```

### Cache Update Flow

```
Claude Code → mcp__syntropy__healthcheck
            → cache-syntropy-health.py (via stdin)
            → .ce/syntropy-health-cache.json
```

## Updating the Cache

The cache should be refreshed whenever you want fresh healthcheck data displayed on next session start.

**Manual refresh** (run in Claude Code session):

1. Call the healthcheck MCP tool
2. The results will be automatically cached

**Programmatic refresh** (from shell):

```bash
# Generate fresh healthcheck JSON and pipe to cache script
echo '{"syntropy": {...}, "servers": [...], "summary": {...}}' | \
  uv run python tools/scripts/cache-syntropy-health.py
```

## Cache Behavior

- **TTL**: 5 minutes (after this, status display shows "⚠️ Cache is stale")
- **Missing cache**: Error message with instructions to refresh
- **Stale cache**: Warning message but still displays data
- **Fresh cache**: Normal status display

## File Locations

```
.ce/syntropy-health-cache.json          # Cache file (gitignored)
tools/scripts/syntropy-status.py        # Display script (runs in hook)
tools/scripts/cache-syntropy-health.py  # Cache updater (called by Claude)
tools/scripts/session-startup.sh        # Unified startup hook script
.claude/settings.local.json             # Hook configuration
```

## Architecture Benefits

1. **Fast startup**: No MCP calls during hook execution (~200ms vs 2-3s)
2. **Real data**: Shows actual healthcheck results (no hardcoded fallbacks)
3. **Graceful degradation**: Stale cache shows warning, missing cache shows error
4. **Zero silent failures**: All errors print troubleshooting guidance

## Hook Configuration

**Current setup** (`.claude/settings.local.json`):

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd) && cd \"$PROJECT_ROOT/tools\" && bash scripts/session-startup.sh",
            "timeout": 12
          }
        ]
      }
    ]
  }
}
```

**Why 12s timeout?**
- Context drift calculation: ~1-2s
- Syntropy status (cache read): ~200ms
- MCP tools list: ~500ms
- uv venv initialization: ~2-3s
- Buffer for slow systems: ~6-7s
- **Total**: Completes in ~4-6s, 12s provides safe margin

## Troubleshooting

### "❌ Syntropy health cache not found"

**Cause**: Cache file doesn't exist
**Fix**: Refresh the cache (see "Updating the Cache" above)

### "⚠️ Cache is stale (>5 minutes old)"

**Cause**: Cache older than 5 minutes
**Fix**: Refresh for latest data (optional - still displays)

### Hook doesn't fire on session start

**Cause**: Timeout too short or script error
**Debug**:
```bash
# Test script manually
cd tools && bash scripts/session-startup.sh

# Check execution time
time bash scripts/session-startup.sh
```

### Displays wrong data

**Cause**: Stale cache
**Fix**: Refresh cache with current healthcheck

## Migration from Old System

**Old approach** (removed):
- Hardcoded static data (FIXME comments)
- Multiple separate hooks (5s each)
- No real MCP integration

**New approach** (current):
- Real healthcheck data via cache
- Single unified hook (12s)
- Fast reads from cache file
- Clear error handling

## Related Files

- `PRP-27-syntropy-status-hook.md` - Implementation blueprint
- `.ce/drift-report.md` - Context drift analysis
- `CLAUDE.md` - "No Fishy Fallbacks" policy
