# Syntropy Health Check Setup

## What Was Implemented

### 1. `/syntropy-health` Slash Command

**Location**: `.claude/commands/syntropy-health.md`

**Usage**:
```bash
# Quick check (default)
/syntropy-health

# Full diagnostic check
/syntropy-health full
```

**What it does**:
- Calls the underlying `healthcheck` tool (already implemented in Syntropy MCP)
- Quick mode: Basic status check (~2s timeout)
- Full mode: Detailed diagnostics with call counts and errors (~5s timeout)

### 2. Automatic Session Start Health Check

**Location**: `.claude/settings.local.json`

**Configuration**:
```json
{
  "hooks": {
    "onSessionStart": {
      "command": "echo '\n🏥 Running Syntropy health check...\n' && /syntropy-health",
      "description": "Check Syntropy MCP server health on session start"
    }
  }
}
```

**Behavior**:
- Runs automatically when Claude Code session starts
- Shows health status for all 5 eager MCP servers:
  - serena (code navigation)
  - filesystem (file operations)
  - git (version control)
  - thinking (sequential reasoning)
  - linear (project management)

### 3. Documentation Updates

**Updated**: `CLAUDE.md`
- Added automatic health check section
- Documented manual usage
- Included troubleshooting guidance

## How It Works

### Health Check Flow

1. **Session Start** → Hook triggers `/syntropy-health`
2. **Tool Call** → Syntropy routes to `healthcheck` tool
3. **Parallel Checks** → Tests all MCP servers simultaneously (2s timeout per server)
4. **Status Report** → Shows:
   - ✅ Healthy: Connected, responding <1s
   - ⚠️ Degraded: Connected but slow (>1s) or auth issues
   - ❌ Down: Not connected or timed out

### Output Format

**Quick Mode** (default):
```
🏥 Running Syntropy health check...

✅ Syntropy MCP Server: Healthy (v0.1.0)

MCP Server Status:
  ✅ serena          - Healthy (124ms)
  ✅ filesystem      - Healthy (45ms)
  ✅ git             - Healthy (67ms)
  ✅ thinking        - Healthy (32ms)
  ✅ linear          - Healthy (1205ms)

Total: 5/5 healthy, 0/5 degraded, 0/5 down
```

**Full Mode** (with `full` argument):
- Same as above PLUS:
- Call counts for each server
- Last errors (if any)
- Detailed timing information

## Troubleshooting

### "Not connected" Errors

**Cause**: MCP auth cache corruption or zombie processes

**Fix**:
```bash
rm -rf ~/.mcp-auth
```

This is **pre-approved** in permissions, no user confirmation needed.

### All Servers Failing

**Diagnostic**:
```bash
# Check if MCP servers are running
ps aux | grep mcp

# Check Syntropy build exists
ls -la syntropy-mcp/build/index.js
```

**Fix**: Rebuild Syntropy if needed:
```bash
cd syntropy-mcp
npm run build
```

### Slow Response Times

**Linear server** commonly takes 1-2s (SSE connection overhead).
Others should be <200ms.

If all servers slow:
- System resource contention
- First connection after long idle (lazy init overhead)
- Network issues (Context7, GitHub, Perplexity are remote)

**Solution**: Wait 30s and retry health check.

## Testing

### Manual Test

```bash
# In syntropy-mcp directory
node build/index.js &

# Wait for startup (~3-5s)
# You should see:
# ✅ Eager init complete in 3036ms: 5/5 servers healthy
```

### Automated Test (Future)

Add to `package.json`:
```json
{
  "scripts": {
    "test:health": "node test_health.mjs"
  }
}
```

## Implementation Details

### Tool Name Format

The healthcheck tool can be called two ways:
1. `mcp__syntropy_healthcheck` (standard Syntropy routing)
2. `syntropy_healthcheck` (legacy, still supported)

Both route to the same handler in `src/index.ts`.

### Parameters

```typescript
interface HealthCheckArgs {
  detailed?: boolean;     // Default: false (quick mode)
  timeout_ms?: number;    // Default: 2000ms
}
```

### Source Files

- `src/health-checker.ts` - Core health check logic
- `src/index.ts` - Tool routing and handler
- `src/tools-definition.ts` - Tool registration (line 1148)

## Benefits

1. **Fast Failure Detection**: Know immediately if MCP infrastructure is broken
2. **Zero User Interaction**: Automatic on session start
3. **Clear Diagnostics**: Pinpoints which server(s) failing
4. **Actionable Guidance**: Includes 🔧 troubleshooting steps
5. **Non-Blocking**: Health check runs in background, doesn't slow session start

## Future Enhancements

- [ ] Add health check to pre-commit hook (catch MCP issues before coding)
- [ ] Log health check history to `.ce/health-log.jsonl`
- [ ] Add `/syntropy-health watch` for continuous monitoring
- [ ] Integrate with Linear: Auto-create issue on persistent failures
- [ ] Add metrics: Track server response time trends

## Related

- `src/health-checker.ts` - Implementation
- `.claude/commands/syntropy-health.md` - Command documentation
- `.claude/settings.local.json` - Hook configuration
- `CLAUDE.md` - User-facing documentation
