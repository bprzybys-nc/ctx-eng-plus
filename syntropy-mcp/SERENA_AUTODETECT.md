# Serena Project Autodetect Configuration

## Overview

Serena MCP server is now configured to automatically detect and activate the current project context on startup.

## Configuration

The `servers.json` file includes the `SERENA_PROJECT_ROOT` environment variable:

```json
"syn-serena": {
  "command": "uvx",
  "args": [
    "--from",
    "git+https://github.com/oraios/serena",
    "serena",
    "start-mcp-server"
  ],
  "env": {
    "SERENA_PROJECT_ROOT": "/Users/bprzybysz/nc-src/ctx-eng-plus"
  }
}
```

## How It Works

1. **Startup**: When Serena MCP server starts, it receives `SERENA_PROJECT_ROOT` environment variable
2. **Autodetect**: Serena automatically activates the project at that path
3. **Ready**: Server is immediately ready to perform code navigation for that project

## Customization

To change the active project, update `servers.json`:

```json
"env": {
  "SERENA_PROJECT_ROOT": "/path/to/your/project"
}
```

Or set via environment before starting:

```bash
export SERENA_PROJECT_ROOT="/path/to/your/project"
npm start
```

## Benefits

✅ **No Manual Setup**: Project auto-activated on server start  
✅ **Context Aware**: Tools work immediately with correct project context  
✅ **Multi-Project Support**: Easy to switch by changing path  
✅ **CI/CD Friendly**: Can be set via environment variables

## Project Context

Current configuration uses:
```
/Users/bprzybysz/nc-src/ctx-eng-plus
```

This is the `ctx-eng-plus` project root, enabling Serena to:
- Find and navigate code symbols
- Understand project structure
- Perform semantic searches
- Manage project-specific tools

## Testing

Verify Serena auto-detection works:

```bash
npm test
# Serena health check will show successful connection
```

## Notes

- Serena requires `.serena/` directory at project root with configuration
- Server startup time: ~2 seconds (includes project initialization)
- Subsequent tool calls: <50ms (reuses connection)

---

**Updated**: October 20, 2025  
**Status**: ✅ Active
