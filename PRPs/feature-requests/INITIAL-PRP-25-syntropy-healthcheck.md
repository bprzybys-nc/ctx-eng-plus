# Feature: Syntropy MCP Healthcheck Tool

## Problem Statement

Currently, there's no way to quickly verify if all MCP servers integrated through Syntropy are healthy and responding correctly. When tool calls fail, it's unclear whether the issue is with:
- Syntropy aggregation layer
- Individual MCP server connections
- Tool routing/forwarding logic
- Configuration issues

**Need**: A healthcheck tool that tests connectivity to all underlying MCP servers and reports their status.

## Desired Outcome

A `syntropy_healthcheck` tool that:
1. Tests Syntropy server itself (is it running, responding)
2. Tests each underlying MCP server (serena, filesystem, git, context7, thinking, linear, repomix, github, perplexity)
3. Reports health status for each server (✅ healthy, ⚠️ degraded, ❌ down)
4. Provides troubleshooting guidance for failures
5. Returns structured JSON output for automation

## Use Cases

1. **Debugging Tool Failures**: When a tool call fails, run healthcheck to identify which server is down
2. **System Monitoring**: Verify all MCP servers are healthy before starting work
3. **CI/CD Integration**: Check MCP infrastructure health in automated workflows
4. **Onboarding**: New developers can verify their MCP setup is correct

## Example Usage

```bash
# CLI usage
mcp__syntropy__syntropy_healthcheck

# Expected output
✅ Syntropy MCP Server: Healthy (v0.1.0)

MCP Server Status:
  ✅ serena         - Healthy (9 tools)
  ✅ filesystem     - Healthy (13 tools)
  ✅ git            - Healthy (5 tools)
  ✅ context7       - Healthy (2 tools)
  ✅ thinking       - Healthy (1 tool)
  ⚠️ linear         - Degraded (authentication required)
  ✅ repomix        - Healthy (1 tool)
  ✅ github         - Healthy (27 tools)
  ✅ perplexity     - Healthy (1 tool)

Total: 8/9 healthy, 1/9 degraded, 0/9 down
```

## Success Criteria

- [ ] Healthcheck tool accessible via `mcp__syntropy__syntropy_healthcheck`
- [ ] Tests Syntropy server itself
- [ ] Tests all 9 underlying MCP servers
- [ ] Returns structured JSON output (for automation)
- [ ] Provides clear status indicators (✅/⚠️/❌)
- [ ] Includes troubleshooting guidance for failures
- [ ] Completes within 5 seconds (parallel checks)
- [ ] Zero false positives (accurate health detection)

## Technical Considerations

1. **Health Check Methods**:
   - Syntropy: Verify server is running and responding
   - MCP Servers: Attempt ListTools request (lightweight, fast)
   - Tool-level: Optional detailed check (call specific test tools)

2. **Timeout Handling**:
   - Each server check: 2 second timeout
   - Overall healthcheck: 5 second limit
   - Run checks in parallel for speed

3. **Error Categories**:
   - **Healthy**: Server responding, tools available
   - **Degraded**: Server responding but some tools unavailable (e.g., auth required)
   - **Down**: Server not responding or connection failed

4. **Output Formats**:
   - Human-readable (colored output with emojis)
   - JSON (structured data for automation)

## Dependencies

- Existing Syntropy MCP server (PRP-24)
- MCP SDK client functionality (for testing server connections)
- TypeScript for server-side implementation

## Implementation Notes

- Add new tool definition to `syntropy-mcp/src/tools-definition.ts`
- Implement health check logic in `syntropy-mcp/src/health-checks.ts` (new file)
- Use MCP client to test ListTools on each server
- Cache results briefly (30 seconds) to avoid overwhelming servers
- Include server version info when available

## Related Work

- PRP-24: Syntropy MCP Server (foundation)
- Context Engineering healthcheck patterns
