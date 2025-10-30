---
description: Check health of Syntropy MCP tools and underlying servers
---

# Syntropy Health Check

Check the health and availability of Syntropy MCP aggregation layer and all underlying MCP servers.

## Usage

```bash
/syntropy-health [mode]
```

**Modes:**
- `quick` (default): Fast check of critical tools (3 servers, <5s)
- `full`: Comprehensive check of all servers with detailed diagnostics

## Task

You must execute a health check of Syntropy MCP infrastructure using the `mcp__syntropy__healthcheck` tool.

### Quick Mode (Default)

Test 3 critical servers with 1 tool each:

```typescript
// Call healthcheck tool
const result = await mcp__syntropy__healthcheck({
  detailed: false,
  timeout_ms: 3000
});

// Parse and format output
// Expected servers to test: syn-serena, syn-filesystem, syn-git
```

**Quick mode criteria:**
- Test only critical servers: `syn-serena`, `syn-filesystem`, `syn-git`
- Single representative tool call per server
- Timeout: 3s per server
- Log level: INFO for success, ERROR for failures
- Report: connection status, response time

### Full Mode

Test all 9 servers with detailed diagnostics:

```typescript
const result = await mcp__syntropy__healthcheck({
  detailed: true,
  timeout_ms: 5000
});

// Parse full diagnostics:
// - All server pool stats
// - Call counts per server
// - Last errors if any
// - Response time percentiles
```

**Full mode criteria:**
- Test all servers: syn-serena, syn-filesystem, syn-git, syn-thinking, syn-linear, syn-context7, syn-github, syn-repomix, syn-perplexity
- Multiple tool calls to verify health
- Timeout: 5s per server
- Log levels: INFO (healthy), WARN (slow >1s), ERROR (failed)
- Report: detailed stats, call history, error traces

## Output Format

Present results in this format:

```
🏥 SYNTROPY HEALTH CHECK [QUICK/FULL]
=====================================

[For each server tested:]

✅ syn-serena (Serena MCP)
   Status: Connected
   Response: 245ms
   Test: activate_project ✓
   INFO: Serena MCP responding normally

⚠️  syn-linear (Linear MCP)
   Status: Connected  
   Response: 1203ms (SLOW)
   Test: list_projects ✓
   WARN: High latency detected - response time >1s

❌ syn-github (GitHub MCP)
   Status: Connection failed
   Error: Authentication timeout
   ERROR: Failed to connect to GitHub MCP
   🔧 Troubleshooting: Run `rm -rf ~/.mcp-auth` to reset connection cache

SUMMARY
-------
✅ Healthy: 7/9 servers (78%)
⚠️  Warnings: 1 server (slow response)
❌ Failed: 1 server (connection error)

Overall Status: DEGRADED
```

## Logging Requirements

Use these log levels in output:

- **INFO**: Normal operations, successful health checks
  - Example: `INFO: Serena MCP responding normally (245ms)`
  
- **WARN**: Performance issues, non-critical problems
  - Example: `WARN: Linear MCP slow response (1.2s) - check network`
  
- **ERROR**: Connection failures, critical issues
  - Example: `ERROR: GitHub MCP connection failed - authentication required`

## Health Status Icons

- ✅ Healthy: Response <1s, all tools working
- ⚠️ Warning: Response 1-3s, or minor issues
- ❌ Failed: Connection error, timeout, or tool failures

## When to Use

- **Session start**: Quick health check before working
- **After `rm -rf ~/.mcp-auth`**: Verify servers reconnected
- **Debugging MCP issues**: Full mode for diagnostics
- **Performance problems**: Identify slow servers

## Common Issues & Solutions

**Authentication errors:**
```bash
rm -rf ~/.mcp-auth
```
Then restart Claude Code session.

**Slow response (>1s):**
- WARN level logged
- Check network connection
- Consider restarting specific server

**Connection failures:**
- ERROR level logged
- Check server process running
- Verify configuration in `.ce/servers.json`
- Check logs in `~/.mcp/logs/`

## Implementation Notes

1. Call `mcp__syntropy__healthcheck` tool with appropriate params
2. Parse JSON response from healthcheck
3. Format output with proper log levels
4. Report summary statistics
5. Include troubleshooting for failed servers
6. Return exit code: 0 (healthy), 1 (warnings), 2 (failures)
