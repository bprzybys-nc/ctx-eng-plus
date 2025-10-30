# Syntropy MCP Server - Production Deployment Guide

## Overview

Syntropy MCP Server is a unified tool aggregation layer that routes tool calls to underlying MCP servers using a `syntropy:server:tool` naming convention.

**Status**: Phase 2b Complete - Production Ready
- ✅ Tool forwarding implemented
- ✅ Connection pooling and lifecycle management
- ✅ Graceful shutdown and signal handling
- ✅ Structured logging for monitoring
- ✅ 17/17 tests passing

## Architecture

```
Claude API Call
        ↓
syntropy:server:tool (e.g., syntropy:filesystem:read_file)
        ↓
Syntropy MCP Server
        ↓
MCPClientManager (connection pooling)
        ↓
Underlying MCP Servers (spawned on first use)
        ↓
Tool Result
```

## Configuration

### servers.json

Located at project root, defines all managed MCP servers:

```json
{
  "servers": {
    "syn-serena": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"],
      "env": {}
    },
    "syn-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {}
    },
    "syn-git": {
      "command": "uvx",
      "args": ["mcp-server-git"],
      "env": {}
    },
    "syn-context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp@latest"],
      "env": {"DEFAULT_MINIMUM_TOKENS": "10000"}
    },
    "syn-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {}
    },
    "syn-repomix": {
      "command": "npx",
      "args": ["-y", "repomix", "--mcp"],
      "env": {}
    }
  }
}
```

**Notes**:
- `syn-` prefix prevents naming conflicts
- Linear excluded (uses hosted remote MCP at https://mcp.linear.app/sse)
- Environment variables (env) passed to spawned processes
- All servers support lazy initialization (spawn on first use)

## Running the Server

### Development

```bash
npm run build
npm test  # Verify 17/17 tests pass
npm start # Run server
```

### Production

```bash
npm run build
NODE_ENV=production node build/index.js
```

## Logging

### Structured Output

Server logs to stderr with `[Syntropy]` prefix:

```
[Syntropy] INFO: Loaded 6 MCP server configs
[Syntropy] INFO: Connecting to MCP server: syn-filesystem
[Syntropy] INFO: Spawning process for syn-filesystem: npx -y @modelcontextprotocol/server-filesystem .
[Syntropy] INFO: Connected to syn-filesystem in 2191ms
[Syntropy] INFO: Calling tool: syn-filesystem:read_text_file
[Syntropy] INFO: Tool call completed: syn-filesystem:read_text_file (145ms)
```

### Log Levels

- **INFO**: Server lifecycle events, tool calls, durations
- **WARN**: Non-critical issues (unused)
- **ERROR**: Connection failures, tool call failures, shutdown errors

### Monitoring

Track these metrics:
- Server connection times (should be < 5s)
- Tool call durations
- Failed tool calls
- Graceful shutdown completion

## Tool Interface

### Tool Naming Convention

```
syntropy:server:tool

Examples:
- syntropy:serena:find_symbol
- syntropy:filesystem:read_text_file
- syntropy:git:git_commit
- syntropy:context7:get-library-docs
- syntropy:thinking:sequentialthinking
- syntropy:repomix:pack_codebase
```

### Error Handling

All errors include troubleshooting guidance:

```
Invalid syntropy tool name: syntropy:unknown:tool
Expected format: syntropy:server:tool
Example: syntropy:serena:find_symbol
🔧 Troubleshooting: Check tool name format
```

### Tool Call Forwarding

Tool calls are forwarded with:
1. **Validation**: Ensure format matches `syntropy:server:tool`
2. **Routing**: Convert to underlying MCP tool name (e.g., `mcp__filesystem__read_text_file`)
3. **Execution**: Call tool on underlying MCP server
4. **Return**: Results formatted as MCP ToolResultBlockParam

## Connection Management

### Lifecycle

1. **Lazy Initialization**: Servers spawn on first tool call
2. **Connection Pooling**: Reuse connections for subsequent calls
3. **Pending Connection Tracking**: Prevent duplicate spawns during concurrent requests
4. **Graceful Closure**: closeAll() closes all connections on shutdown

### Resource Usage

- **Memory**: Minimal - only active connections consume resources
- **Processes**: One child process per active server
- **File Descriptors**: 2-3 per connection (stdin/stdout/stderr)

## Graceful Shutdown

### Signal Handling

Server handles SIGINT and SIGTERM:

```
[Syntropy] Received SIGINT, shutting down gracefully...
[Syntropy] INFO: Closing 6 MCP server connections
[Syntropy] INFO: Closed connection: syn-filesystem
[Syntropy] INFO: Closed connection: syn-git
[Syntropy] INFO: All MCP server connections closed
[Syntropy] Cleanup complete
```

### Shutdown Sequence

1. Catch SIGINT/SIGTERM signal
2. Close all active MCP connections
3. Cleanup resources
4. Exit with code 0

## Testing

### Run All Tests

```bash
npm test
```

**Test Coverage**:
- 9 Unit tests: Tool parsing and conversion
- 6 Health checks: Server connectivity validation
- 2 POC tests: End-to-end tool forwarding

**Current Status**: 17/17 passing in ~23 seconds

### Health Checks

Verify server connectivity:

```bash
npm test 2>&1 | grep "Health:"
```

Each server has isolated timeout (15s):
- syn-serena
- syn-filesystem
- syn-git
- syn-context7
- syn-thinking
- syn-repomix

## Deployment Checklist

- [ ] `servers.json` configured with correct spawn commands
- [ ] All MCP servers available (npx/uvx can find packages)
- [ ] 17/17 tests passing
- [ ] Environment variables set (if needed)
- [ ] Logging configured for monitoring
- [ ] Signal handlers working (graceful shutdown)
- [ ] Resource limits set (if containerized)

## Troubleshooting

### Server Not Connecting

```
Failed to connect to syn-filesystem MCP server:
Command: npx -y @modelcontextprotocol/server-filesystem .
🔧 Troubleshooting: Ensure syn-filesystem MCP server is available
```

**Solutions**:
1. Verify npx/uvx is installed: `which npx` / `which uvx`
2. Check package exists: `npx -y @modelcontextprotocol/server-filesystem --help`
3. Review servers.json configuration

### Tool Call Failures

```
Tool call failed: syn-serena:find_symbol
Error: Tool not found
🔧 Troubleshooting: Check tool name and arguments
```

**Solutions**:
1. Verify tool name format: `syntropy:server:tool`
2. Confirm server has tool: Check MCP server documentation
3. Review tool arguments

### Connection Timeouts

**Problem**: Tests hang or timeout

**Solutions**:
1. Increase timeout in health-checks.test.ts (currently 15s)
2. Check if server process spawned: `ps aux | grep <server>`
3. Verify network connectivity (if remote)

## Performance

### Observed Metrics

From 17/17 test run (~23 seconds total):

| Server | Connection Time | Type |
|--------|-----------------|------|
| syn-filesystem | 2076ms | npx (official) |
| syn-git | 428ms | uvx (Python) |
| syn-serena | 1714ms | uvx (git+https) |
| syn-context7 | 1974ms | npx (official) |
| syn-thinking | 1822ms | npx (official) |
| syn-repomix | 423ms | npx (official) |

**Observations**:
- First connection: 400-2000ms (includes process spawn)
- Subsequent calls: < 50ms (connection reused)
- Tool forwarding overhead: < 5ms
- Shutdown: ~100-200ms for all connections

## Monitoring & Observability

### Metrics to Track

```javascript
// Get current status
const status = clientManager.getStatus();
// Returns: { "syn-filesystem": { connected: true, callCount: 42, lastError: null }, ... }
```

**Key Metrics**:
- `connected`: Is server ready for tool calls
- `callCount`: Total tool calls through this server
- `lastError`: Last error message (if any)

### Logging Integration

Send logs to your monitoring system:

```bash
npm start 2>&1 | tee logs/syntropy-$(date +%Y%m%d-%H%M%S).log
```

Parse structured logs:
- Extract `[Syntropy]` prefixed lines
- Match INFO/ERROR levels
- Extract timing information

## Security

### Process Isolation

- Each MCP server runs as separate process
- Stdio communication (no network exposure)
- Runs with user privileges (not root)

### Error Information

- Error messages include troubleshooting guidance
- No sensitive data in logs (filter if needed)
- Stack traces only in DEBUG mode

## Next Steps

### Phase 3 (Future)

- Integration testing with Claude API
- Performance benchmarking
- Load testing with concurrent requests
- Advanced monitoring and alerting
- Caching layer for repeated calls

## Support

For issues or questions:
1. Check logs: `[Syntropy]` prefixed messages
2. Run tests: `npm test` to verify setup
3. Review configuration: Check servers.json
4. Consult troubleshooting section above
