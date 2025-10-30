# Syntropy MCP Server - Quick Start

## 30-Second Setup

```bash
# 1. Build
npm run build

# 2. Test
npm test  # Verify 17/17 pass

# 3. Run
npm start
```

Server runs on stdio, ready for tool calls.

## Using the Server

### Tool Call Format

```
syntropy:server:tool
```

**Examples**:
- `syntropy:filesystem:read_text_file` - Read file
- `syntropy:git:git_status` - Git status
- `syntropy:serena:find_symbol` - Find code symbol
- `syntropy:context7:get-library-docs` - Get documentation
- `syntropy:thinking:sequentialthinking` - Sequential thinking

### Tool Arguments

Pass as JSON object:

```javascript
// Read file
{
  "name": "syntropy:filesystem:read_text_file",
  "arguments": {
    "path": "/path/to/file.txt"
  }
}

// Find git status
{
  "name": "syntropy:git:git_status",
  "arguments": {
    "repo_path": "/path/to/repo"
  }
}

// Find code symbol
{
  "name": "syntropy:serena:find_symbol",
  "arguments": {
    "name_path": "MyClass/method",
    "relative_path": "src/file.ts",
    "include_body": true
  }
}
```

## Available Servers

| Server | Type | Package |
|--------|------|---------|
| syn-serena | Code navigation | git+https://github.com/oraios/serena |
| syn-filesystem | File operations | @modelcontextprotocol/server-filesystem |
| syn-git | Git operations | mcp-server-git |
| syn-context7 | Library docs | @upstash/context7-mcp |
| syn-thinking | Reasoning | @modelcontextprotocol/server-sequential-thinking |
| syn-repomix | Codebase packaging | repomix |

## Features

### ✅ Connection Pooling
- Lazy initialization (spawn on first use)
- Reuse connections for efficiency
- Automatic cleanup

### ✅ Error Handling
- Clear error messages with troubleshooting
- Fast failure on validation errors
- Structured logging

### ✅ Graceful Shutdown
- Handle SIGINT/SIGTERM
- Close all connections properly
- Clean resource cleanup

### ✅ Production Ready
- 17/17 tests passing
- 6 health checks validating connectivity
- Structured logging for monitoring

## Monitoring

Watch server logs:

```bash
npm start 2>&1 | grep "\[Syntropy\]"
```

**Sample Output**:
```
[Syntropy] INFO: Loaded 6 MCP server configs
[Syntropy] INFO: Connecting to MCP server: syn-filesystem
[Syntropy] INFO: Connected to syn-filesystem in 2191ms
[Syntropy] INFO: Calling tool: syn-filesystem:read_text_file
[Syntropy] INFO: Tool call completed: syn-filesystem:read_text_file (145ms)
```

## Troubleshooting

### Tests Failing
```bash
npm run build && npm test
```
Verify all 17 tests pass. If not, check:
- Node.js version (14+)
- npx/uvx availability
- servers.json configuration

### Server Won't Start
```bash
# Check logs
npm start 2>&1 | head -50

# Verify dependencies
which npx && which uvx
```

### Tool Not Found
- Verify tool name format: `syntropy:server:tool`
- Check server documentation for available tools
- Run health checks: `npm test`

## Configuration

Edit `servers.json` to:
- Add/remove servers
- Change spawn commands
- Set environment variables

**Example**: Add custom environment for context7:
```json
"syn-context7": {
  "command": "npx",
  "args": ["-y", "@upstash/context7-mcp@latest"],
  "env": {"DEFAULT_MINIMUM_TOKENS": "5000"}
}
```

## Development

### Run Tests
```bash
npm test              # All 17 tests
npm run build         # TypeScript → JavaScript
npm start             # Run server
```

### View Code
- `src/index.ts` - Main server
- `src/client-manager.ts` - Connection management
- `src/health-checks.test.ts` - Server validation

### Modify Tools
Edit `src/index.ts` ListToolsRequestSchema handler to add/remove tools.

## Next Steps

1. **Integrate with Claude**: Use as MCP server in Claude API
2. **Monitor**: Set up logging to observability platform
3. **Scale**: Add load balancing if needed
4. **Extend**: Add more MCP servers as needed

## Performance

**Connection Times**:
- First call: 400-2000ms (includes spawn)
- Subsequent calls: < 50ms (reused)
- Tool forwarding: < 5ms

**Concurrency**:
- Handles multiple simultaneous tool calls
- Connection pooling prevents duplicate spawns
- Graceful degradation if server unavailable

## Support

See `DEPLOYMENT.md` for:
- Architecture details
- Configuration reference
- Troubleshooting guide
- Monitoring setup
- Security considerations
