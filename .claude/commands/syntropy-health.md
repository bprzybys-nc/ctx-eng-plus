# Syntropy Health Check Command

**Purpose**: Check health status of Syntropy MCP server and all underlying servers

**Target**: AI agents working with Context Engineering codebase

**Status**: ✅ IMPLEMENTED - Restart Claude Code to use

**Last Updated**: 2025-10-27

---

## 🔄 Restart Required

**Tool is NOW WORKING** - Fixed in syntropy-mcp/src/index.ts:205

**To use**:
1. Exit Claude Code
2. Restart Claude Code
3. Run `/syntropy-health`

**What changed**: Handler now accepts `mcp__syntropy__healthcheck` (double underscore) format

---

## Command Usage

```bash
/syntropy-health [--detailed]
```

**What it does**:
- Check Syntropy MCP server status
- Validate all underlying MCP servers (Serena, Filesystem, Git, GitHub, Linear, etc.)
- Report connection status, call counts, and recent errors
- Provide troubleshooting guidance for failed servers

---

## Quick Health Check

**Default mode** (fast, summary only):
```bash
/syntropy-health
```

**Expected output**:
```
✅ Syntropy MCP: Healthy
✅ Serena: Healthy
✅ Filesystem: Healthy
✅ Git: Healthy
✅ GitHub: Healthy
✅ Linear: Healthy
✅ Context7: Healthy
✅ Thinking: Healthy
✅ Repomix: Healthy
```

---

## Detailed Diagnostics

**Detailed mode** (includes call counts, errors):
```bash
/syntropy-health --detailed
```

**Expected output**:
```
✅ Syntropy MCP: Healthy
  - Uptime: 2h 45m
  - Total calls: 1,247

✅ Serena: Healthy
  - Calls: 342
  - Last success: 2s ago
  - Active project: /Users/bprzybysz/nc-src/ctx-eng-plus

✅ Filesystem: Healthy
  - Calls: 567
  - Last success: 1s ago

⚠️ Linear: Degraded
  - Calls: 12
  - Last error: "Not connected to Linear" (5m ago)
  - 🔧 Troubleshooting: Run `rm -rf ~/.mcp-auth` then retry
```

---

## Error Detection Patterns

### Connection Failures

**Pattern**: Server unreachable or not responding
```
❌ <Server>: Unreachable
  - Error: Connection timeout
  - 🔧 Troubleshooting: Check MCP server config in .claude/mcp.json
```

### Authentication Issues

**Pattern**: Auth token invalid or expired
```
❌ Linear: Authentication failed
  - Error: Invalid token
  - 🔧 Troubleshooting: Run `rm -rf ~/.mcp-auth` to reset credentials
```

### Configuration Problems

**Pattern**: Server misconfigured or missing dependencies
```
❌ Serena: Configuration error
  - Error: Project not activated
  - 🔧 Troubleshooting: Run `mcp__syntropy__serena_activate_project` with project root
```

---

## Implementation Instructions (For Future Development)

**⚠️ This tool is NOT YET IMPLEMENTED**

When the MCP tool is implemented, this command will:

1. **Execute health check**:
   ```python
   # Tool name: mcp__syntropy_healthcheck (single underscore before healthcheck)
   result = mcp__syntropy_healthcheck(
       detailed=True if "--detailed" in args else False,
       timeout_ms=2000
   )
   ```

2. **Parse response**:
   - Extract server statuses
   - Identify healthy vs degraded vs failed servers
   - Collect error messages and timestamps

3. **Format output**:
   - ✅ Healthy: Green status, basic info
   - ⚠️ Degraded: Yellow status, warning details
   - ❌ Failed: Red status, error details + troubleshooting

4. **Add troubleshooting guidance**:
   - Connection failures → Check MCP config
   - Auth failures → Clear auth cache
   - Config errors → Verify server settings

---

## Common Issues & Remediation

| Issue | Detection | Remediation |
|-------|-----------|-------------|
| Linear "Not connected" | Error contains "Not connected" | `rm -rf ~/.mcp-auth` |
| Serena "No active project" | Error contains "activate_project" | Run `serena_activate_project` with full path |
| GitHub rate limit | Error contains "rate limit" | Wait or use auth token |
| Filesystem permission denied | Error contains "EACCES" | Check file permissions |

---

## Exit Codes

- **0**: All servers healthy
- **1**: One or more servers degraded (warnings)
- **2**: One or more servers failed (critical)

---

## Quality Checks

**Before finalizing report**:

- ✅ All servers checked
- ✅ Status accurately reported
- ✅ Errors include troubleshooting
- ✅ Timestamps are recent
- ✅ Performance metrics included (detailed mode)

---

## Example Output

### Healthy System
```
## Syntropy Health Check

**Status**: ✅ All systems healthy
**Checked**: 9 servers
**Timestamp**: 2025-10-27 14:23:45

✅ Syntropy MCP: Healthy
✅ Serena: Healthy
✅ Filesystem: Healthy
✅ Git: Healthy
✅ GitHub: Healthy
✅ Linear: Healthy
✅ Context7: Healthy
✅ Thinking: Healthy
✅ Repomix: Healthy
```

### Degraded System
```
## Syntropy Health Check

**Status**: ⚠️ 1 server degraded
**Checked**: 9 servers
**Timestamp**: 2025-10-27 14:23:45

✅ Syntropy MCP: Healthy
✅ Serena: Healthy (342 calls)
✅ Filesystem: Healthy (567 calls)
✅ Git: Healthy (89 calls)
✅ GitHub: Healthy (23 calls)
⚠️ Linear: Degraded
  - Error: "Not connected to Linear" (5m ago)
  - 🔧 Run: `rm -rf ~/.mcp-auth`
✅ Context7: Healthy (12 calls)
✅ Thinking: Healthy (5 calls)
✅ Repomix: Healthy (2 calls)
```

---

## References

- **PRP-25**: `.ce/PRPs/system/executed/PRP-25-syntropy-healthcheck.md` (design)
- **PRP-27**: `.ce/PRPs/system/executed/PRP-27-syntropy-status-hook.md` (cache workaround)
- **Cache File**: `.ce/syntropy-health-cache.json`
- **MCP Config**: `.claude/mcp.json`
- **CLAUDE.md**: Syntropy MCP tool naming conventions

---

## Implementation Tracking

**Design Complete**: ✅ PRP-25 (TypeScript interfaces, validation checklist)
**Implementation**: 🔜 Deferred to post-1.0 (4-6 hours estimated)
**Workaround**: ✅ PRP-27 cache-based status hook

**To Implement**:
1. Add `syntropy_healthcheck` tool definition to `tools-definition.ts`
2. Create `health-checker.ts` with `runHealthCheck()` function
3. Add healthcheck handler in `index.ts`
4. Write integration tests

**Priority**: LOW (cache workaround sufficient for now)

---

## Notes

- Default timeout: 2000ms per server (when implemented)
- Cached results valid for 30s (current workaround)
- Run after MCP config changes
- Use detailed mode for debugging (when implemented)
