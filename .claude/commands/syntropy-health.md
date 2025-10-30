# /syntropy-health - Syntropy MCP Health Check

Check health status of Syntropy MCP server and all underlying servers.

## Usage

```bash
# Quick check (default - fast, essential servers only)
/syntropy-health

# Full diagnostic check (all servers, detailed info)
/syntropy-health full
```

## What It Checks

**Quick Mode** (default):
- Essential servers: Serena, Filesystem, Git, Linear, Thinking
- Response times for each server
- Connection status
- Tool call counts (if available)

**Full Mode**:
- All 9 MCP servers (including lazy-loaded: Context7, Repomix, GitHub, Perplexity)
- Detailed diagnostics
- Last errors (if any)
- Call statistics

## Output Format

```
🏥 Syntropy MCP Health Check

✅ serena: 124ms (15 calls)
✅ filesystem: 45ms (8 calls)
✅ git: 67ms (3 calls)
⚠️  linear: 1205ms (2 calls) - SLOW
❌ github: Not connected

Overall: 4/5 servers healthy
```

## Troubleshooting

### "Not connected" errors

Clear MCP auth cache and restart:
```bash
rm -rf ~/.mcp-auth
```

### Slow response times (>1s)

Server may be starting up or overloaded. Wait 30s and retry.

### All servers failing

Check if MCP servers are running:
```bash
ps aux | grep mcp
```

## When to Use

**Recommended on session start** to verify MCP infrastructure:
- After Claude Code restart
- When seeing unexpected tool failures
- Before starting major work (PRPs, refactoring)
- After clearing auth cache

## Implementation

This command calls the `healthcheck` tool with appropriate parameters:
- Default: `{"detailed": false, "timeout_ms": 2000}`
- Full: `{"detailed": true, "timeout_ms": 5000}`

## Related

- `/update-context` - Updates project context (requires healthy Serena)
- `/generate-prp` - Requires healthy Serena + Filesystem
- `/execute-prp` - Requires multiple healthy servers
