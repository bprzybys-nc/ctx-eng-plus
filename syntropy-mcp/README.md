# Syntropy MCP Server

**A unified tool aggregation layer for Claude via the Model Context Protocol (MCP)**

Syntropy routes tool calls to multiple underlying MCP servers using a standardized `syntropy:server:tool` naming convention. It provides connection pooling, graceful shutdown, structured logging, and production-ready error handling.

## Status

✅ **Phase 2b Complete - Production Ready**

- Tool call forwarding to 6 MCP servers
- 17/17 tests passing
- Connection pooling with lazy initialization
- Graceful shutdown and signal handling
- Structured logging for monitoring
- Health monitoring with parallel checks

## Quick Start

```bash
# Setup and verify
npm install
npm run build
npm test  # 17/17 passing

# Run server
npm start
```

See [QUICKSTART.md](QUICKSTART.md) for usage examples.

## Architecture

Syntropy aggregates multiple MCP servers under a unified interface:

```
Claude API
    ↓
syntropy:server:tool (e.g., syntropy:filesystem:read_file)
    ↓
Syntropy MCP Server
    ↓
MCPClientManager (connection pooling, lifecycle)
    ↓
Underlying MCP Servers (6 servers, lazy spawned)
    ↓
Tool Results
```

## Features

### 🔌 Unified Tool Interface

Call tools via standardized naming:

```
syntropy:server:tool

Examples:
- syntropy:filesystem:read_text_file
- syntropy:git:git_commit
- syntropy:serena:find_symbol
- syntropy:context7:get-library-docs
- syntropy:thinking:sequentialthinking
- syntropy:repomix:pack_codebase
```

### 🚀 Connection Pooling

- **Lazy initialization**: Servers spawn on first tool call
- **Connection reuse**: Subsequent calls use existing connections
- **Concurrent request handling**: Prevents duplicate spawns
- **Automatic cleanup**: Closes connections on shutdown

### ⚙️ Lifecycle Management

- **Graceful shutdown**: SIGINT/SIGTERM handling
- **Resource cleanup**: Closes all connections properly
- **Signal forwarding**: Propagates signals to child processes
- **Error recovery**: Clear error messages with troubleshooting

### 📊 Structured Logging

```
[Syntropy] INFO: Loaded 6 MCP server configs
[Syntropy] INFO: Connecting to MCP server: syn-filesystem
[Syntropy] INFO: Connected to syn-filesystem in 2191ms
[Syntropy] INFO: Calling tool: syn-filesystem:read_text_file
[Syntropy] INFO: Tool call completed: syn-filesystem:read_text_file (145ms)
```

### ✅ Error Handling

All errors include actionable troubleshooting guidance:

```
Failed to connect to syn-filesystem MCP server:
Command: npx -y @modelcontextprotocol/server-filesystem .
🔧 Troubleshooting: Ensure syn-filesystem MCP server is available
```

## Supported Servers

| Server | Purpose | Command |
|--------|---------|---------| | syn-serena | Code navigation, symbol search | uvx git+https://github.com/oraios/serena |
| syn-filesystem | File read/write operations | npx @modelcontextprotocol/server-filesystem |
| syn-git | Git operations (status, diff, log, commit) | uvx mcp-server-git |
| syn-context7 | Library documentation lookup | npx @upstash/context7-mcp |
| syn-thinking | Sequential thinking process | npx @modelcontextprotocol/server-sequential-thinking |
| syn-repomix | Codebase packaging and analysis | npx repomix --mcp |

All servers configured in `servers.json` with lazy initialization (spawn on first use).

## Testing

```bash
# Run all 17 tests
npm test

# Build
npm run build

# Run with output
npm start
```

**Test Coverage**:
- **9 Unit tests**: Tool parsing and conversion validation
- **6 Health checks**: Server connectivity (isolated timeouts)
- **2 POC tests**: End-to-end tool forwarding

**Current**: 17/17 passing in ~23 seconds

## Configuration

### servers.json

```json
{
  "servers": {
    "syn-filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {}
    }
  }
}
```

**Keys**:
- `command`: `npx` (Node.js) or `uvx` (Python)
- `args`: Command arguments as array
- `env`: Environment variables to pass to process

Edit to add/remove servers or change spawn commands.

## Usage

### Tool Call Format

```javascript
{
  "name": "syntropy:server:tool",
  "arguments": { /* tool-specific args */ }
}
```

### Example: Read File

```javascript
{
  "name": "syntropy:filesystem:read_text_file",
  "arguments": {
    "path": "/path/to/file.txt"
  }
}
```

### Example: Find Code Symbol

```javascript
{
  "name": "syntropy:serena:find_symbol",
  "arguments": {
    "name_path": "MyClass/method",
    "relative_path": "src/file.ts",
    "include_body": true
  }
}
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for complete tool reference.

### Project Initialization

**New in PRP-29.1**: Initialize Context Engineering projects with boilerplate and framework structure.

```javascript
{
  "name": "syntropy:syntropy:init_project",
  "arguments": {
    "project_root": "/path/to/project"
  }
}
```

Initializes:
- ✅ Copy boilerplate from `syntropy/ce/` to `.ce/`
- ✅ Create user directories: `PRPs/`, `examples/`, `.serena/memories/`
- ✅ Generate `CLAUDE.md` project guide
- ✅ Upsert slash commands: `generate-prp`, `execute-prp`, `update-context`, `peer-review`

See [PRP-29.1](../PRPs/executed/PRP-29.1-syntropy-docs-init.md) for implementation details.

## Performance

### Connection Times

| Server | Time | Type |
|--------|------|------|
| syn-filesystem | ~2000ms | npx (first call) |
| syn-git | ~400ms | uvx (first call) |
| syn-serena | ~1700ms | uvx git+https (first call) |
| syn-context7 | ~2000ms | npx (first call) |
| syn-thinking | ~1800ms | npx (first call) |
| syn-repomix | ~400ms | npx (first call) |

**Subsequent calls**: < 50ms (connection reused)

### Resource Usage

- **Memory**: Minimal when no connections active
- **Processes**: One per active server (lazy spawned)
- **File descriptors**: 2-3 per connection

## Development

### Project Structure

```
syntropy-mcp/
├── src/
│   ├── index.ts              # Main MCP server
│   ├── client-manager.ts     # Connection pooling
│   ├── health-checker.ts     # Health monitoring
│   ├── tools-definition.ts   # Tool definitions
│   ├── index.test.ts         # Unit tests
│   ├── health-checks.test.ts # Server connectivity
│   ├── health-checker.test.ts # Health checker tests
│   └── poc.test.ts           # End-to-end forwarding
├── build/                    # Compiled JavaScript
├── servers.json              # Server configuration
├── package.json              # Dependencies
├── tsconfig.json             # TypeScript config
├── QUICKSTART.md             # Quick start guide
├── DEPLOYMENT.md             # Production guide
└── README.md                 # This file
```

### Commands

```bash
npm run build                 # TypeScript → JavaScript
npm test                      # Run all 17 tests
npm start                     # Run server
npm run clean                 # Remove build artifacts
```

### Code Quality

- **TypeScript**: Full type safety
- **Error handling**: All errors include troubleshooting
- **Logging**: Structured output to stderr
- **Testing**: 100% coverage of core functionality

## Health Monitoring

Check the status of all MCP servers:

```bash
# Via Claude Code
mcp__syntropy_healthcheck

# Example output
✅ Syntropy MCP Server: Healthy (v0.1.0)

MCP Server Status:
  ✅ serena         - Healthy (250ms)
  ✅ filesystem     - Healthy (120ms)
  ✅ git            - Healthy (180ms)
  ✅ context7       - Healthy (300ms)
  ✅ thinking       - Healthy (500ms)
  ⚠️ linear         - Degraded (authentication required)
  ✅ repomix        - Healthy (150ms)
  ✅ github         - Healthy (200ms)
  ✅ perplexity     - Healthy (220ms)

Total: 8/9 healthy, 1/9 degraded, 0/9 down
```

### Detailed Output

For automation/monitoring, use detailed JSON output:

```bash
mcp__syntropy_healthcheck(detailed=true)
```

Returns:

```json
{
  "syntropy": { "version": "0.1.0", "status": "healthy" },
  "servers": [
    {
      "server": "filesystem",
      "status": "healthy",
      "connected": true,
      "callCount": 0,
      "checkDuration": 120
    }
  ],
  "summary": { "total": 9, "healthy": 8, "degraded": 1, "down": 0 },
  "timestamp": "2025-01-20T14:30:00Z"
}
```

### Custom Timeout

```bash
mcp__syntropy_healthcheck(timeout_ms=1000)
```

Use shorter timeout for faster checks on slower networks.

### Troubleshooting Status

| Status | Meaning | Action |
|--------|---------|--------|
| ✅ Healthy | Server connected and responsive | No action needed |
| ⚠️ Degraded | Server responsive but authentication/config issue | Check environment variables (API keys) |
| ❌ Down | Server not responding or failed to start | Verify installation and servers.json config |

## Monitoring

### View Logs

```bash
npm start 2>&1 | grep "\[Syntropy\]"
```

### Health Status

Get connection status programmatically:

```typescript
const status = clientManager.getStatus();
// {
//   "syn-filesystem": { connected: true, callCount: 42, lastError: null },
//   "syn-git": { connected: false, callCount: 0, lastError: null },
//   ...
// }
```

### Metrics

Track from logs:
- Server connection times
- Tool call durations
- Failed tool calls
- Shutdown completion

## Troubleshooting

### Tests Failing

```bash
npm run build && npm test
```

If not 17/17:
- Check Node.js version (14+)
- Verify npx/uvx: `which npx && which uvx`
- Review servers.json

### Server Won't Connect

```bash
npm start 2>&1 | head -50
```

- Check error message for specific server
- Verify spawn command: `npx -y @package/name --help`
- Review servers.json

### Tool Not Found

- Verify format: `syntropy:server:tool`
- Check MCP server documentation
- Run health checks: `npm test`

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting.

## Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for:

- Production running
- Graceful shutdown
- Monitoring and observability
- Security considerations
- Performance optimization
- Troubleshooting guide

## Next Steps

- [Phase 3](../PRPs/executed/PRP-24-syntropy-mcp.md): Integration testing with Claude API
- Load testing with concurrent requests
- Performance profiling and optimization
- Advanced caching layer
- Custom MCP server integration

## License

MIT

## Support

1. Check [QUICKSTART.md](QUICKSTART.md) for common usage
2. See [DEPLOYMENT.md](DEPLOYMENT.md) for production details
3. Run tests: `npm test` to verify setup
4. Review logs: `npm start 2>&1` for diagnostics
5. Check health: `mcp__syntropy_healthcheck` for server status
