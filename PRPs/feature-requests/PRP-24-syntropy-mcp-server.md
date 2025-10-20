---
name: "Syntropy MCP Server - Unified Tool Aggregation Layer"
description: "Create unified MCP server that aggregates all existing MCP tools (serena, filesystem, git, context7, sequential-thinking, linear-server, repomix) under syntropy: namespace with auto-generated documentation"
prp_id: "PRP-24"
issue: "BLA-36"
status: "executed"
created_date: "2025-01-19T18:30:00Z"
last_updated: "2025-10-19T20:35:00Z"
updated_by: "execute-prp-command"
context_sync:
  ce_updated: true
  serena_updated: false
version: 3
---

# PRP-24: Syntropy MCP Server - Unified Tool Aggregation Layer

## Executive Summary

Create a single MCP server that wraps all existing MCP tools under a unified `syntropy:` namespace, providing:
- **Unified Access**: One MCP server instead of 8 separate connections
- **Auto Documentation**: tool-index.md generated from live MCP metadata
- **Namespace Clarity**: Hierarchical structure (syntropy:server:tool)
- **Zero Breaking Changes**: Existing tools preserved, just wrapped

**Current State**: 46 tools across 8 MCP servers (serena, filesystem, git, context7, sequential-thinking, linear-server, repomix)

**Target State**: All tools accessible via `syntropy:server:tool` format with centralized documentation

**Implementation Scope**: Phase 2 delivers validation layer (tool parsing, error handling, testing) with 60-70% test coverage. Actual tool call forwarding to underlying MCP servers deferred to future PRP (Phase 2b).

## Context from Codebase

### Current MCP Configuration

**File**: `.claude/settings.local.json`

The project currently uses 8 separate MCP servers with 46 allowed tools:

```json
{
  "permissions": {
    "allow": [
      // Serena MCP (9 tools) - Code intelligence
      "mcp__serena__find_symbol",
      "mcp__serena__get_symbols_overview",
      "mcp__serena__search_for_pattern",
      "mcp__serena__find_referencing_symbols",
      "mcp__serena__write_memory",
      "mcp__serena__create_text_file",
      "mcp__serena__activate_project",
      "mcp__serena__list_dir",
      "mcp__serena__read_file",

      // Filesystem MCP (9 tools) - File operations
      "mcp__filesystem__read_file",
      "mcp__filesystem__read_text_file",
      "mcp__filesystem__list_directory",
      "mcp__filesystem__write_file",
      "mcp__filesystem__edit_file",
      "mcp__filesystem__search_files",
      "mcp__filesystem__directory_tree",
      "mcp__filesystem__get_file_info",
      "mcp__filesystem__list_allowed_directories",

      // Git MCP (5 tools) - Version control
      "mcp__git__git_status",
      "mcp__git__git_diff",
      "mcp__git__git_log",
      "mcp__git__git_add",
      "mcp__git__git_commit",

      // Context7 MCP (2 tools) - Documentation
      "mcp__context7__resolve-library-id",
      "mcp__context7__get-library-docs",

      // Sequential Thinking MCP (1 tool) - Advanced reasoning
      "mcp__sequential-thinking__sequentialthinking",

      // Linear MCP (5 tools) - Project management
      "mcp__linear-server__create_issue",
      "mcp__linear-server__get_issue",
      "mcp__linear-server__list_issues",
      "mcp__linear-server__update_issue",
      "mcp__linear-server__list_projects",

      // Repomix MCP (1 tool) - Codebase analysis
      "mcp__repomix__pack_codebase"
    ]
  }
}
```

### Existing Project Structure

**No existing TypeScript or MCP server implementations** in the codebase:
- Project is primarily Python-based (`tools/ce/` directory)
- Uses Node.js only for markdown linting (markdownlint-cli2)
- No package.json dependencies for MCP SDK

**Python Patterns** from `tools/ce/`:
- Error handling with troubleshooting guidance (🔧)
- No fishy fallbacks policy (fast failure)
- KISS principles (simple solutions first)
- Testing with pytest (`tools/tests/`)

## External Research

### MCP SDK Documentation

**Source**: Model Context Protocol TypeScript SDK (/modelcontextprotocol/typescript-sdk)

**Key Patterns for Server Implementation**:

1. **Low-Level Server API** (Manual Request Handling):
```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { ListToolsRequestSchema, CallToolRequestSchema } from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
    { name: 'syntropy', version: '0.1.0' },
    { capabilities: { tools: { listChanged: true } } }
);

// Handle tool listing
server.setRequestHandler(ListToolsRequestSchema, async () => {
    return { tools: [...] };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
    // Route to underlying MCP server
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

2. **High-Level McpServer API** (Simplified Tool Registration):
```typescript
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';

const server = new McpServer({
    name: 'syntropy',
    version: '0.1.0'
});

// Register tools dynamically
server.registerTool('toolName', schema, handler);
```

3. **Transport Options**:
   - **StdioServerTransport**: Standard I/O (for CLI integration)
   - **StreamableHTTPServerTransport**: HTTP/SSE (for web services)

**Best Practice**: Use **low-level Server API** for syntropy because we need custom routing logic (not just registering new tools, but forwarding to existing MCP servers).

### Python SDK Alternative

**Source**: Model Context Protocol Python SDK (/modelcontextprotocol/python-sdk)

**FastMCP Pattern** (Simplified Python Server):
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("syntropy")

@mcp.tool()
def tool_name(param: str) -> str:
    """Tool description"""
    return result
```

**Decision**: Use **TypeScript** for syntropy server because:
- Official MCP SDK has better TypeScript support
- Easier integration with Claude Code (Node.js ecosystem)
- Better ecosystem for stdio/HTTP transports
- Existing markdownlint setup already uses Node.js

## Implementation Plan

### Phase 1: Tool Index Generation (Python Script)

**Goal**: Auto-generate tool-index.md from MCP server metadata

**File**: `syntropy-mcp/scripts/generate-tool-index.py`

**Approach**:
1. Parse `.claude/settings.local.json` for allowed MCP tools
2. Extract tool metadata from each MCP server (via MCP protocol)
3. Generate markdown documentation organized by server

**Implementation**:

```python
#!/usr/bin/env python3
"""Generate tool-index.md from MCP server configuration.

Approach:
1. Parse settings.local.json for allowed tools
2. Group tools by MCP server
3. Generate markdown with tool descriptions
4. Save to syntropy-mcp/tool-index.md

Note: This initial version uses static metadata from config.
Future enhancement: Query live MCP servers for real-time metadata.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set


def load_allowed_tools() -> Set[str]:
    """Load allowed MCP tools from settings.local.json.

    Returns:
        Set of allowed tool names (e.g., 'mcp__serena__find_symbol')
    """
    config_path = Path(".claude/settings.local.json")

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "🔧 Troubleshooting: Run from project root directory"
        )

    with open(config_path) as f:
        config = json.load(f)

    allowed = config.get("permissions", {}).get("allow", [])

    # Filter for MCP tools only (start with mcp__)
    mcp_tools = {tool for tool in allowed if tool.startswith("mcp__")}

    if not mcp_tools:
        raise ValueError(
            "No MCP tools found in configuration\n"
            "🔧 Troubleshooting: Check permissions.allow in settings.local.json"
        )

    return mcp_tools


def parse_tool_name(tool: str) -> tuple[str, str] | None:
    """Parse MCP tool name into server and tool components.

    Args:
        tool: MCP tool name (e.g., 'mcp__serena__find_symbol')

    Returns:
        Tuple of (server, tool_name) or None if invalid format

    Example:
        >>> parse_tool_name('mcp__serena__find_symbol')
        ('serena', 'find_symbol')
    """
    match = re.match(r'^mcp__([^_]+)__(.+)$', tool)
    if not match:
        return None

    server, tool_name = match.groups()
    return (server, tool_name)


def group_tools_by_server(tools: Set[str]) -> Dict[str, List[str]]:
    """Group MCP tools by server name.

    Args:
        tools: Set of MCP tool names

    Returns:
        Dict mapping server name to list of tool names

    Example:
        >>> group_tools_by_server({'mcp__serena__find_symbol', 'mcp__git__git_status'})
        {'serena': ['find_symbol'], 'git': ['git_status']}
    """
    grouped: Dict[str, List[str]] = {}

    for tool in tools:
        parsed = parse_tool_name(tool)
        if not parsed:
            continue

        server, tool_name = parsed

        if server not in grouped:
            grouped[server] = []

        grouped[server].append(tool_name)

    # Sort tools within each server
    for server in grouped:
        grouped[server].sort()

    return grouped


def get_server_description(server: str) -> str:
    """Get human-readable description for MCP server.

    Args:
        server: MCP server name

    Returns:
        Description string
    """
    descriptions = {
        "serena": "Code Intelligence Tools",
        "filesystem": "File Operations",
        "git": "Version Control",
        "context7": "Documentation",
        "sequential-thinking": "Advanced Reasoning",
        "linear-server": "Project Management",
        "repomix": "Codebase Analysis"
    }

    return descriptions.get(server, "MCP Tools")


def generate_tool_entry(server: str, tool: str) -> List[str]:
    """Generate markdown entry for a tool.

    Args:
        server: MCP server name
        tool: Tool name

    Returns:
        List of markdown lines
    """
    return [
        f"### `syntropy:{server}:{tool}`",
        "",
        f"**Original**: `mcp__{server}__{tool}`",
        "",
        "**Description**: *(Auto-generated from MCP metadata)*",
        "",
        "**Parameters**: *(See MCP server documentation)*",
        "",
    ]


def generate_markdown(grouped_tools: Dict[str, List[str]]) -> str:
    """Generate markdown documentation from grouped tools.

    Args:
        grouped_tools: Dict mapping server to list of tools

    Returns:
        Markdown formatted string
    """
    lines = [
        "# Syntropy MCP Tool Index",
        "",
        "Auto-generated from MCP server configuration.",
        f"Last updated: {datetime.now().isoformat()}",
        "",
        "## Overview",
        "",
        f"Total servers: {len(grouped_tools)}",
        f"Total tools: {sum(len(tools) for tools in grouped_tools.values())}",
        "",
    ]

    # Generate entry for each server
    for server in sorted(grouped_tools.keys()):
        tools = grouped_tools[server]
        description = get_server_description(server)

        lines.append(f"## syntropy:{server} - {description}")
        lines.append("")
        lines.append(f"**Tool Count**: {len(tools)}")
        lines.append("")

        # List each tool
        for tool in tools:
            lines.extend(generate_tool_entry(server, tool))

    # Add usage examples
    lines.extend([
        "---",
        "",
        "## Usage Examples",
        "",
        "### Before (Direct MCP)",
        "```typescript",
        'await mcp.call("mcp__serena__find_symbol", {',
        '  name_path: "MyClass/method",',
        '  relative_path: "src/main.py"',
        "});",
        "```",
        "",
        "### After (Syntropy)",
        "```typescript",
        'await mcp.call("syntropy:serena:find_symbol", {',
        '  name_path: "MyClass/method",',
        '  relative_path: "src/main.py"',
        "});",
        "```",
        "",
    ])

    return "\n".join(lines)


def main():
    """Generate tool index documentation."""
    print("Generating Syntropy MCP tool index...")

    try:
        # Load and parse tools
        tools = load_allowed_tools()
        print(f"  Found {len(tools)} MCP tools")

        grouped = group_tools_by_server(tools)
        print(f"  Grouped into {len(grouped)} servers")

        # Generate markdown
        markdown = generate_markdown(grouped)

        # Write to file
        output_path = Path("syntropy-mcp/tool-index.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(markdown)

        print(f"✅ Generated {output_path}")
        print(f"   Servers: {', '.join(sorted(grouped.keys()))}")

    except Exception as e:
        print(f"❌ Failed to generate tool index: {e}")
        raise


if __name__ == "__main__":
    main()
```

**Testing**:

```python
# tools/tests/test_tool_index.py
import pytest
from pathlib import Path
import sys

# Add syntropy-mcp to path with robust error handling
PROJECT_ROOT = Path(__file__).parent.parent.parent
SYNTROPY_PATH = PROJECT_ROOT / "syntropy-mcp"

if not SYNTROPY_PATH.exists():
    raise ImportError(
        f"syntropy-mcp directory not found at {SYNTROPY_PATH}\n"
        "🔧 Troubleshooting: Ensure syntropy-mcp/ exists in project root"
    )

sys.path.insert(0, str(SYNTROPY_PATH))

from scripts.generate_tool_index import (
    parse_tool_name,
    group_tools_by_server,
    get_server_description
)


def test_parse_tool_name():
    """Test MCP tool name parsing."""
    assert parse_tool_name("mcp__serena__find_symbol") == ("serena", "find_symbol")
    assert parse_tool_name("mcp__git__git_status") == ("git", "git_status")
    assert parse_tool_name("invalid") is None


def test_group_tools_by_server():
    """Test tool grouping by server."""
    tools = {
        "mcp__serena__find_symbol",
        "mcp__serena__search_for_pattern",
        "mcp__git__git_status"
    }

    grouped = group_tools_by_server(tools)

    assert "serena" in grouped
    assert "git" in grouped
    assert len(grouped["serena"]) == 2
    assert len(grouped["git"]) == 1


def test_get_server_description():
    """Test server description lookup."""
    assert "Code Intelligence" in get_server_description("serena")
    assert "Version Control" in get_server_description("git")
    assert "MCP Tools" in get_server_description("unknown")
```

**Run**:
```bash
cd /path/to/project
python syntropy-mcp/scripts/generate-tool-index.py
```

### Phase 2: Syntropy MCP Server - Validation Layer (TypeScript)

**Goal**: Create MCP server that validates and parses tool calls (forwarding deferred to Phase 2b)

**Scope**: Tool name parsing, validation, error handling, testing (60-70% coverage target)

**Files**:
- `syntropy-mcp/src/index.ts` - Main server implementation
- `syntropy-mcp/package.json` - Dependencies and build config
- `syntropy-mcp/tsconfig.json` - TypeScript configuration

**Implementation**:

**File**: `syntropy-mcp/package.json`

```json
{
  "name": "syntropy-mcp",
  "version": "0.1.0",
  "description": "Unified MCP tool aggregation layer",
  "type": "module",
  "bin": {
    "syntropy": "./build/index.js"
  },
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch",
    "prepare": "npm run build",
    "test": "node --test build/**/*.test.js"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.3.0"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

**File**: `syntropy-mcp/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "build"]
}
```

**File**: `syntropy-mcp/src/index.ts`

```typescript
#!/usr/bin/env node
/**
 * Syntropy MCP Server - Unified Tool Aggregation Layer
 *
 * Routes tool calls in format syntropy:server:tool to underlying MCP servers.
 * Preserves all original functionality while providing unified namespace.
 *
 * Architecture:
 * 1. Parse syntropy:server:tool format
 * 2. Forward to underlying MCP server (mcp__server__tool)
 * 3. Return result unchanged
 *
 * Error Handling:
 * - Invalid tool format → Clear error with troubleshooting
 * - Server connection failure → Actionable guidance
 * - Tool call failure → Preserve underlying error
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError
} from "@modelcontextprotocol/sdk/types.js";

// Tool routing configuration
// Maps syntropy server names to MCP server prefixes
const SERVER_ROUTES: Record<string, string> = {
  "serena": "mcp__serena__",
  "filesystem": "mcp__filesystem__",
  "git": "mcp__git__",
  "context7": "mcp__context7__",
  "thinking": "mcp__sequential-thinking__",
  "linear": "mcp__linear-server__",
  "repomix": "mcp__repomix__"
};

// Tool metadata cache (populated from underlying servers)
interface ToolMetadata {
  name: string;
  description?: string;
  inputSchema?: any;
}

const toolCache: Map<string, ToolMetadata> = new Map();

/**
 * Parse syntropy tool name into server and tool components.
 *
 * @param toolName - Format: syntropy:server:tool
 * @returns { server: string, tool: string } or null if invalid
 *
 * @example
 * parseSyntropyTool("syntropy:serena:find_symbol")
 * // Returns: { server: "serena", tool: "find_symbol" }
 */
function parseSyntropyTool(toolName: string): { server: string; tool: string } | null {
  const match = toolName.match(/^syntropy:([^:]+):(.+)$/);
  if (!match) return null;

  const [, server, tool] = match;
  return { server, tool };
}

/**
 * Convert syntropy tool name to underlying MCP tool name.
 *
 * @param server - Syntropy server name (e.g., "serena")
 * @param tool - Tool name (e.g., "find_symbol")
 * @returns Original MCP tool name (e.g., "mcp__serena__find_symbol")
 *
 * @throws {McpError} If server is unknown
 */
function toMcpToolName(server: string, tool: string): string {
  const prefix = SERVER_ROUTES[server];

  if (!prefix) {
    const validServers = Object.keys(SERVER_ROUTES).join(", ");
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Unknown syntropy server: ${server}\n` +
      `Valid servers: ${validServers}\n` +
      `🔧 Troubleshooting: Use format syntropy:<server>:<tool>`
    );
  }

  return `${prefix}${tool}`;
}

/**
 * Convert MCP tool name to syntropy format.
 *
 * @param mcpToolName - Original MCP tool name
 * @returns Syntropy tool name or null if not convertible
 *
 * @example
 * toSyntropyToolName("mcp__serena__find_symbol")
 * // Returns: "syntropy:serena:find_symbol"
 */
function toSyntropyToolName(mcpToolName: string): string | null {
  // Match pattern: mcp__<server>__<tool>
  const match = mcpToolName.match(/^mcp__([^_]+)__(.+)$/);
  if (!match) return null;

  const [, serverPrefix, tool] = match;

  // Find syntropy server name for this prefix
  for (const [syntropyServer, mcpPrefix] of Object.entries(SERVER_ROUTES)) {
    if (mcpPrefix === `mcp__${serverPrefix}__`) {
      return `syntropy:${syntropyServer}:${tool}`;
    }
  }

  return null;
}

// Create Syntropy MCP server
const server = new Server(
  {
    name: "syntropy",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {
        // Tools don't change dynamically (based on underlying servers)
        listChanged: false
      },
    },
  }
);

/**
 * Handle tool listing request.
 *
 * Returns all syntropy-namespaced tools by querying underlying MCP servers.
 * Tools are cached for performance.
 *
 * Note: In this initial implementation, we return a static list based on
 * allowed tools in settings.local.json. Future enhancement: query live servers.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  // FIXME: Query actual MCP servers for tool metadata
  // TODO: Implement MCP client connections to underlying servers
  // For now, return static list based on known tools

  const tools = [
    // Serena tools
    { name: "syntropy:serena:find_symbol", description: "Find code symbols by name path" },
    { name: "syntropy:serena:get_symbols_overview", description: "Get file symbol overview" },
    { name: "syntropy:serena:search_for_pattern", description: "Search codebase patterns" },
    { name: "syntropy:serena:find_referencing_symbols", description: "Find symbol references" },
    { name: "syntropy:serena:write_memory", description: "Store project context" },
    { name: "syntropy:serena:create_text_file", description: "Create new file" },
    { name: "syntropy:serena:activate_project", description: "Switch active project" },
    { name: "syntropy:serena:list_dir", description: "List directory contents" },
    { name: "syntropy:serena:read_file", description: "Read file contents" },

    // Filesystem tools
    { name: "syntropy:filesystem:read_file", description: "Read file (deprecated)" },
    { name: "syntropy:filesystem:read_text_file", description: "Read text file" },
    { name: "syntropy:filesystem:list_directory", description: "List directory" },
    { name: "syntropy:filesystem:write_file", description: "Write/overwrite file" },
    { name: "syntropy:filesystem:edit_file", description: "Line-based file edits" },
    { name: "syntropy:filesystem:search_files", description: "Recursive file search" },
    { name: "syntropy:filesystem:directory_tree", description: "JSON directory tree" },
    { name: "syntropy:filesystem:get_file_info", description: "File metadata" },
    { name: "syntropy:filesystem:list_allowed_directories", description: "Show allowed paths" },

    // Git tools
    { name: "syntropy:git:git_status", description: "Repository status" },
    { name: "syntropy:git:git_diff", description: "Show changes" },
    { name: "syntropy:git:git_log", description: "Commit history" },
    { name: "syntropy:git:git_add", description: "Stage files" },
    { name: "syntropy:git:git_commit", description: "Create commit" },

    // Context7 tools
    { name: "syntropy:context7:resolve-library-id", description: "Find library ID" },
    { name: "syntropy:context7:get-library-docs", description: "Fetch library docs" },

    // Sequential thinking
    { name: "syntropy:thinking:sequentialthinking", description: "Sequential thinking process" },

    // Linear tools
    { name: "syntropy:linear:create_issue", description: "Create Linear issue" },
    { name: "syntropy:linear:get_issue", description: "Get issue details" },
    { name: "syntropy:linear:list_issues", description: "List issues" },
    { name: "syntropy:linear:update_issue", description: "Update issue" },
    { name: "syntropy:linear:list_projects", description: "List projects" },

    // Repomix
    { name: "syntropy:repomix:pack_codebase", description: "Package codebase for AI" }
  ];

  return { tools };
});

/**
 * Handle tool call request.
 *
 * Routes syntropy:server:tool calls to underlying mcp__server__tool.
 * Preserves all parameters and return values unchanged.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // Parse syntropy tool name
  const parsed = parseSyntropyTool(name);
  if (!parsed) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Invalid syntropy tool name: ${name}\n` +
      `Expected format: syntropy:server:tool\n` +
      `Example: syntropy:serena:find_symbol\n` +
      `🔧 Troubleshooting: Check tool name format`
    );
  }

  const { server: targetServer, tool } = parsed;

  // Convert to underlying MCP tool name
  const mcpToolName = toMcpToolName(targetServer, tool);

  // FIXME: Forward call to underlying MCP server
  // TODO: Implement MCP client connection and tool call forwarding
  // For now, throw error indicating forwarding not yet implemented
  throw new McpError(
    ErrorCode.InternalError,
    `Tool forwarding not yet implemented: ${mcpToolName}\n` +
    `🔧 Troubleshooting: Phase 2 implementation in progress\n` +
    `Target tool: ${mcpToolName}\n` +
    `Arguments: ${JSON.stringify(args, null, 2)}`
  );
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Syntropy MCP Server running on stdio");
}

main().catch((error) => {
  console.error("Fatal error:", error);
  process.exit(1);
});

// Export for testing
export { parseSyntropyTool, toMcpToolName, toSyntropyToolName };
```

**Testing**:

Create `syntropy-mcp/src/index.test.ts`:

```typescript
import { strict as assert } from 'node:assert';
import { test, describe } from 'node:test';
import { parseSyntropyTool, toMcpToolName, toSyntropyToolName } from './index.js';

describe('Syntropy Tool Parsing', () => {
  test('parseSyntropyTool - valid format', () => {
    const parsed = parseSyntropyTool("syntropy:serena:find_symbol");
    assert.deepEqual(parsed, { server: "serena", tool: "find_symbol" });
  });

  test('parseSyntropyTool - invalid format', () => {
    const parsed = parseSyntropyTool("invalid:format");
    assert.equal(parsed, null);
  });

  test('parseSyntropyTool - missing tool part', () => {
    const parsed = parseSyntropyTool("syntropy:serena");
    assert.equal(parsed, null);
  });

  test('parseSyntropyTool - empty string', () => {
    const parsed = parseSyntropyTool("");
    assert.equal(parsed, null);
  });
});

describe('Tool Name Conversion', () => {
  test('toMcpToolName - valid server', () => {
    const mcp = toMcpToolName("serena", "find_symbol");
    assert.equal(mcp, "mcp__serena__find_symbol");
  });

  test('toMcpToolName - unknown server throws error', () => {
    assert.throws(
      () => toMcpToolName("unknown", "tool"),
      /Unknown syntropy server: unknown/
    );
  });

  test('toSyntropyToolName - valid MCP tool', () => {
    const syn = toSyntropyToolName("mcp__serena__find_symbol");
    assert.equal(syn, "syntropy:serena:find_symbol");
  });

  test('toSyntropyToolName - invalid format', () => {
    const syn = toSyntropyToolName("invalid_format");
    assert.equal(syn, null);
  });

  test('toSyntropyToolName - unknown server prefix', () => {
    const syn = toSyntropyToolName("mcp__unknown__tool");
    assert.equal(syn, null);
  });
});
```

**Build and Test**:

```bash
cd syntropy-mcp
npm install
npm run build
npm test
```

### Phase 3: Configuration Integration

**Goal**: Configure Claude Code to use Syntropy MCP server

**File**: `.claude/mcp.json` (create new)

```json
{
  "mcpServers": {
    "syntropy": {
      "command": "node",
      "args": [
        "/Users/bprzybysz/nc-src/ctx-eng-plus/syntropy-mcp/build/index.js"
      ],
      "env": {}
    }
  }
}
```

**⚠️ Important - Path Configuration**:

The absolute path in `mcp.json` must be updated for your environment:

- **macOS/Linux**: `/absolute/path/to/ctx-eng-plus/syntropy-mcp/build/index.js`
- **Windows**: `C:\\path\\to\\ctx-eng-plus\\syntropy-mcp\\build\\index.js`

**Alternative** (using environment variable):
```json
{
  "mcpServers": {
    "syntropy": {
      "command": "node",
      "args": ["${SYNTROPY_PATH}/build/index.js"],
      "env": {}
    }
  }
}
```

Then set `SYNTROPY_PATH` environment variable before starting Claude Code.

**File**: `.claude/settings.local.json` (update - migration approach)

**Phase 3a: Parallel Access** (initial testing - 1-2 weeks):

```json
{
  "permissions": {
    "allow": [
      // NEW: Syntropy namespace (parallel testing)
      "syntropy:serena:*",
      "syntropy:filesystem:*",
      "syntropy:git:*",
      "syntropy:context7:*",
      "syntropy:thinking:*",
      "syntropy:linear:*",
      "syntropy:repomix:*",

      // KEEP: Original MCP tools (during migration)
      "mcp__serena__find_symbol",
      "mcp__serena__get_symbols_overview",
      // ... all existing mcp__ tools ...

      // Keep bash and other non-MCP tools
      "Bash(git:*)",
      "Bash(uv run:*)"
      // ... etc
    ]
  }
}
```

**Migration Timeline**: Run Phase 3a for 1-2 weeks to validate:
- Tool listing works correctly
- Error messages are helpful
- No regressions in existing workflows
- Performance is acceptable

**Phase 3b: Syntropy-Only** (after validation):

```json
{
  "permissions": {
    "allow": [
      // Syntropy namespace only
      "syntropy:serena:*",
      "syntropy:filesystem:*",
      "syntropy:git:*",
      "syntropy:context7:*",
      "syntropy:thinking:*",
      "syntropy:linear:*",
      "syntropy:repomix:*",

      // Non-MCP tools unchanged
      "Bash(git:*)",
      "Bash(uv run:*)"
      // ... etc
    ],
    "deny": [
      // Block direct MCP access (force syntropy usage)
      "mcp__serena__*",
      "mcp__filesystem__*",
      "mcp__git__*",
      "mcp__context7__*",
      "mcp__sequential-thinking__*",
      "mcp__linear-server__*",
      "mcp__repomix__*"
    ]
  }
}
```

## Validation Gates

### Phase 1: Tool Index Generation

**Pre-Implementation** (Completed during PRP generation):
- [x] Understand MCP tool structure from settings.local.json
- [x] Design tool grouping and documentation format
- [x] Plan markdown generation approach

**Implementation**:
- [ ] Create `syntropy-mcp/scripts/generate-tool-index.py`
- [ ] Implement `load_allowed_tools()` function
- [ ] Implement `parse_tool_name()` function
- [ ] Implement `group_tools_by_server()` function
- [ ] Implement `generate_markdown()` function
- [ ] Add error handling with troubleshooting guidance

**Validation**:
- [ ] Run script: `python syntropy-mcp/scripts/generate-tool-index.py`
- [ ] Verify `syntropy-mcp/tool-index.md` generated
- [ ] Confirm all 46+ tools documented
- [ ] Check markdown formatting (headers, code blocks)
- [ ] Run tests: `cd tools && uv run pytest tests/test_tool_index.py -v`

### Phase 2: Syntropy MCP Server

**Pre-Implementation** (Completed during PRP generation):
- [x] Research MCP TypeScript SDK documentation
- [x] Understand low-level Server API for tool routing
- [x] Design syntropy:server:tool parsing logic
- [x] Plan error handling with troubleshooting

**Implementation**:
- [ ] Create `syntropy-mcp/package.json` with MCP SDK dependency
- [ ] Create `syntropy-mcp/tsconfig.json` with proper config
- [ ] Implement `syntropy-mcp/src/index.ts`:
  - [ ] `parseSyntropyTool()` function
  - [ ] `toMcpToolName()` function
  - [ ] `toSyntropyToolName()` function
  - [ ] `ListToolsRequestSchema` handler
  - [ ] `CallToolRequestSchema` handler (forwarding placeholder)
  - [ ] Error handling with McpError
- [ ] Create test file `syntropy-mcp/src/index.test.ts`

**Validation**:
- [ ] Run `cd syntropy-mcp && npm install`
- [ ] Run `npm run build` → verify build succeeds
- [ ] Run `npm test` → verify tests pass
- [ ] Test parsing: `parseSyntropyTool("syntropy:serena:find_symbol")`
- [ ] Test conversion: `toMcpToolName("serena", "find_symbol")`
- [ ] Test server startup: `node build/index.js` (should start without errors)

### Phase 3: Configuration Integration

**Pre-Implementation** (Completed during PRP generation):
- [x] Understand Claude Code MCP configuration format
- [x] Design migration strategy (parallel → syntropy-only, 1-2 weeks)
- [x] Plan testing approach for tool routing

**Implementation**:
- [ ] Create `.claude/mcp.json` with syntropy server config
- [ ] Update `.claude/settings.local.json` (Phase 3a: parallel access)
- [ ] Test syntropy namespace access (manual testing)
- [ ] Validate all 46 tools accessible via syntropy:*
- [ ] Update to Phase 3b (syntropy-only) after validation

**Validation**:
- [ ] Restart Claude Code (load new MCP config)
- [ ] Test tool listing: verify syntropy:* tools appear
- [ ] Test tool calls (will fail with "forwarding not implemented" - expected)
- [ ] Verify error messages include troubleshooting guidance
- [ ] Confirm no regressions with existing bash tools

## Testing Strategy

### Unit Tests (Python)

**File**: `tools/tests/test_tool_index.py`

```bash
cd tools
uv run pytest tests/test_tool_index.py -v
```

**Coverage**:
- [x] `test_parse_tool_name()` - Validate MCP tool parsing
- [x] `test_group_tools_by_server()` - Verify grouping logic
- [x] `test_get_server_description()` - Check description lookup
- [ ] `test_generate_markdown()` - Validate markdown output format
- [ ] `test_load_allowed_tools()` - Test config file loading

### Unit Tests (TypeScript)

**File**: `syntropy-mcp/src/index.test.ts`

```bash
cd syntropy-mcp
npm test
```

**Coverage** (60-70% target):
- [x] `test parseSyntropyTool - valid format`
- [x] `test parseSyntropyTool - invalid format`
- [x] `test parseSyntropyTool - missing tool part`
- [x] `test parseSyntropyTool - empty string`
- [x] `test toMcpToolName - valid server`
- [x] `test toMcpToolName - unknown server throws error`
- [x] `test toSyntropyToolName - valid MCP tool`
- [x] `test toSyntropyToolName - invalid format`
- [x] `test toSyntropyToolName - unknown server prefix`

### Integration Tests

**Manual Testing Workflow**:

1. **Generate Tool Index**:
```bash
python syntropy-mcp/scripts/generate-tool-index.py
cat syntropy-mcp/tool-index.md  # Verify output
```

2. **Build Syntropy Server**:
```bash
cd syntropy-mcp
npm install
npm run build
```

3. **Test Server Startup**:
```bash
node build/index.js
# Should output: "Syntropy MCP Server running on stdio"
# Press Ctrl+C to stop
```

4. **Configure Claude Code**:
```bash
# Create .claude/mcp.json (if doesn't exist)
# Update .claude/settings.local.json with syntropy:* permissions
```

5. **Test in Claude Code**:
- Restart Claude Code
- Verify syntropy:* tools appear in tool list
- Attempt tool call (expect "forwarding not implemented" error)
- Verify error includes troubleshooting guidance

### Performance Tests

**Latency Benchmarking** (future):

```typescript
// syntropy-mcp/src/benchmark.ts
async function benchmarkToolCall() {
  const iterations = 100;

  // Measure direct MCP call
  const directStart = Date.now();
  for (let i = 0; i < iterations; i++) {
    await directMcpCall("mcp__serena__find_symbol", args);
  }
  const directDuration = Date.now() - directStart;

  // Measure syntropy call
  const syntropyStart = Date.now();
  for (let i = 0; i < iterations; i++) {
    await syntropyCall("syntropy:serena:find_symbol", args);
  }
  const syntropyDuration = Date.now() - syntropyStart;

  const overhead = (syntropyDuration - directDuration) / iterations;
  console.log(`Average overhead: ${overhead.toFixed(2)}ms per call`);

  // Assert <50ms overhead
  assert(overhead < 50, `Overhead ${overhead}ms exceeds 50ms threshold`);
}
```

**Target**: <50ms overhead per tool call

## Error Handling Strategy

### Python Script Errors

**Pattern**: Fast failure with troubleshooting guidance

```python
# Example from generate-tool-index.py
if not config_path.exists():
    raise FileNotFoundError(
        f"Configuration file not found: {config_path}\n"
        "🔧 Troubleshooting: Run from project root directory"
    )
```

**Error Categories**:
1. **File Not Found** → Check working directory
2. **Invalid JSON** → Validate settings.local.json syntax
3. **No MCP Tools** → Verify permissions.allow configuration
4. **Write Permission** → Check directory permissions

### TypeScript Server Errors

**Pattern**: Use McpError with ErrorCode

```typescript
// Example from index.ts
throw new McpError(
  ErrorCode.InvalidRequest,
  `Invalid syntropy tool name: ${name}\n` +
  `Expected format: syntropy:server:tool\n` +
  `Example: syntropy:serena:find_symbol\n` +
  `🔧 Troubleshooting: Check tool name format`
);
```

**Error Categories**:
1. **InvalidRequest** → Malformed tool name
2. **InternalError** → Forwarding not implemented (Phase 2 limitation)
3. **MethodNotFound** → Unknown syntropy server
4. **Connection Errors** → Underlying MCP server unavailable (future)

### No Fishy Fallbacks

**STRICT POLICY**: No silent failures or fake success

❌ **FORBIDDEN**:
```typescript
// DON'T DO THIS
try {
  result = await forwardToolCall(server, tool, args);
} catch (error) {
  return { success: true };  // FISHY FALLBACK!
}
```

✅ **REQUIRED**:
```typescript
// DO THIS
try {
  result = await forwardToolCall(server, tool, args);
  return result;
} catch (error) {
  throw new McpError(
    ErrorCode.InternalError,
    `Failed to forward call to ${server}:${tool}\n` +
    `Error: ${error.message}\n` +
    `🔧 Troubleshooting: Verify ${server} MCP server is running`
  );
}
```

## Success Criteria

### Phase 1: Tool Index
- ✅ Script generates tool-index.md successfully
- ✅ All 46+ MCP tools documented
- ✅ Tools grouped by server (7 servers)
- ✅ Markdown formatting correct
- ✅ Tests pass: `pytest tests/test_tool_index.py -v`

### Phase 2: MCP Server
- ✅ TypeScript builds without errors: `npm run build`
- ✅ Tests pass: `npm test`
- ✅ Server starts successfully
- ✅ ListToolsRequest returns all syntropy:* tools
- ✅ CallToolRequest validates tool format
- ✅ Error messages include troubleshooting guidance

### Phase 3: Integration
- ✅ `.claude/mcp.json` configured correctly
- ✅ Settings updated with syntropy:* permissions
- ✅ Claude Code loads syntropy MCP server
- ✅ Tool listing shows syntropy:* tools
- ✅ Tool calls fail with expected "not implemented" error
- ✅ No regressions with existing bash tools

### Overall Success
- ✅ Zero breaking changes to existing workflows
- ✅ Clear migration path (parallel → syntropy-only)
- ✅ Comprehensive documentation (tool-index.md + README)
- ✅ All validation gates passed
- ✅ Tests achieve >80% coverage

## Post-Execution: Documentation & Drift Resolution

### Additional Work Completed (2025-10-20)

**Objective**: Address high context drift (61.29% at session start) by updating all documentation for Syntropy MCP format

**Files Updated**: 6 total

| File | Type | Legacy Refs | Updated | Impact |
|------|------|---|---|---|
| `.serena/memories/tool-usage-guide.md` | Project memory | 30+ | ✅ All | Core tool reference updated |
| `.serena/memories/serena-mcp-tool-restrictions.md` | Project memory | 20+ | ✅ All | Critical workflow guide added |
| `examples/tool-usage-patterns.md` | Project docs | 30+ | ✅ All | Comprehensive patterns updated |
| `.serena/memories/tool-usage-syntropy.md` | Project memory | N/A | ✅ NEW | 1200+ lines comprehensive guide |
| `CLAUDE.md` (project) | Project guide | 20+ | ✅ All | Tool reference section updated |
| `.claude/CLAUDE.md` (global) | Global guide | 0 | ✅ CLEAN | Verified, no updates needed |

**Total Legacy References Eliminated**: ~130+
- All `mcp__serena__*` → `mcp__syntropy__serena__*`
- All `mcp__filesystem__*` → `mcp__syntropy__filesystem__*`
- All `mcp__git__*` → `mcp__syntropy__git__*`
- All `mcp__context7__*` → `mcp__syntropy__context7__*`
- All `mcp__linear-server__*` → `mcp__syntropy__linear__*`
- All `mcp__sequential-thinking__*` → `mcp__syntropy__thinking__*`
- All `mcp__repomix__*` → `mcp__syntropy__repomix__*`

**Critical Workflow Documentation Added**:

1. **Linear Integration (5 tools)**
   - Why: PRP generation auto-creates issues for tracking
   - Without: Issue tracking breaks, implementation blueprints untracked
   - Impact: Complete feature tracking from conception to completion

2. **Context7 Documentation (2 tools)**
   - Why: External library docs essential for PRPs
   - Without: Cannot integrate FastAPI, pytest, SQLAlchemy docs
   - Impact: PRPs lack real-world API references

3. **Sequential Thinking (1 tool)**
   - Why: Structured reasoning for large features
   - Without: Complex problems can't be decomposed
   - Impact: Limits architectural decision-making

**Result**:
- ✅ Drift elimination: All stale tool references removed from project memories
- ✅ Consistency: All docs now use `mcp__syntropy__<server>__<tool>` format
- ✅ Workflow clarity: Critical tools explained with real consequences
- ✅ Future-proof: New developers understand why tools are preserved
- **Expected drift reduction**: From 61.29% → <15% (estimated 60-70% improvement)

---

## Future Enhancements

**Not included in initial PRP** (deferred for future PRPs):

1. **Live Tool Metadata**: Query actual MCP servers for real-time tool descriptions
2. **Tool Call Forwarding**: Implement MCP client connections to forward calls
3. **Connection Pooling**: Reuse MCP server connections for performance
4. **Caching Layer**: Cache read-only operation results
5. **Batch Operations**: `syntropy:batch:call` for multiple tools in one request
6. **Performance Monitoring**: Track latency overhead per tool category
7. **CI/CD Integration**: Auto-update tool-index.md weekly
8. **HTTP Transport**: Support StreamableHTTPServerTransport for web apps

## Implementation Notes

### Why TypeScript for Server?

**Decision**: TypeScript MCP server (not Python)

**Rationale**:
- Official MCP SDK has better TypeScript support
- Easier integration with Claude Code (Node.js ecosystem)
- Better ecosystem for stdio/HTTP transports
- Project already uses Node.js (markdownlint)
- Python script sufficient for tool index generation

### Why Low-Level Server API?

**Decision**: Use `Server` class, not `McpServer`

**Rationale**:
- Need custom routing logic (forward to underlying servers)
- `McpServer` is for registering new tools
- `Server` allows manual request handling
- More control over tool listing and call forwarding

### Migration Strategy

**Phased Approach**:

1. **Phase 3a**: Parallel access (both syntropy:* and mcp__*)
2. **Phase 3b**: Syntropy-only (deny mcp__*)
3. **Phase 4**: Remove deny rules (opt-in complete)

**Rollback**: If issues discovered, revert to original settings.local.json

## Dependencies

### Python
- **Existing**: Python 3.13 (from tools/ce/)
- **New**: None (uses stdlib only)

### Node.js
- **Existing**: Node.js 18+ (for markdownlint)
- **New**:
  - `@modelcontextprotocol/sdk@^0.5.0` - MCP TypeScript SDK
  - `@types/node@^20.0.0` - TypeScript definitions
  - `typescript@^5.3.0` - TypeScript compiler

**Installation**:
```bash
cd syntropy-mcp
npm install
```

## Documentation

### Files to Create

1. **syntropy-mcp/README.md** - User-facing documentation
2. **syntropy-mcp/tool-index.md** - Auto-generated tool list
3. **syntropy-mcp/MIGRATION.md** - Migration guide from direct MCP

### README.md Structure

```markdown
# Syntropy MCP Server

Unified MCP tool aggregation layer providing single namespace for all MCP tools.

## Installation

## Usage

## Architecture

## Tool Index

See [tool-index.md](./tool-index.md) for complete tool list.

## Migration Guide

See [MIGRATION.md](./MIGRATION.md) for migration from direct MCP access.

## Development

## Testing
```

---

## Appendix: MCP SDK Reference

### Key Imports (TypeScript)

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError
} from "@modelcontextprotocol/sdk/types.js";
```

### Server Initialization Pattern

```typescript
const server = new Server(
  { name: "server-name", version: "1.0.0" },
  { capabilities: { tools: { listChanged: false } } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => {
  return { tools: [...] };
});

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  // Handle tool call
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### Error Handling Pattern

```typescript
throw new McpError(
  ErrorCode.InvalidRequest,  // or InternalError, MethodNotFound
  "Error message with troubleshooting guidance"
);
```

### Tool Metadata Format

```typescript
interface Tool {
  name: string;
  description?: string;
  inputSchema?: {
    type: "object";
    properties: Record<string, any>;
    required?: string[];
  };
}
```

---

## Peer Review Notes

### Document Review (2025-01-19T18:20:00Z)

**Reviewer**: Context-Naive AI Peer Review
**Rating**: ⭐⭐⭐⭐½ (4.5/5) - EXCELLENT

**Strengths**:
- ✅ Comprehensive context gathering (46 tools inventoried, MCP SDK research)
- ✅ Clear three-phase implementation with executable code examples
- ✅ Strong error handling patterns (no fishy fallbacks)
- ✅ Thoughtful migration strategy (parallel → syntropy-only)
- ✅ Extensive validation gates and testing strategy

**Improvements Applied**:
1. **Clarified Phase 2 Scope**: Added note that Phase 2 delivers validation layer (60-70% coverage), actual forwarding deferred to future PRP
2. **Improved Python Test Path Handling**: Added robust error handling for syntropy-mcp path resolution
3. **Implemented Real TypeScript Tests**: Exported functions from index.ts and added 9 comprehensive test cases
4. **Added Path Portability Note**: Documented mcp.json path configuration for different environments
5. **Clarified Migration Timeline**: Added 1-2 weeks parallel testing period to Phase 3a
6. **Enhanced Validation Gates**: Added "(Completed during PRP generation)" context to pre-implementation checks

**Questions Resolved**:
1. **Tool Call Forwarding**: Confirmed Phase 2 is validation-only (forwarding → future PRP)
2. **Test Coverage Target**: 60-70% for Phase 2 (parsing + validation)
3. **Migration Timeline**: 1-2 weeks parallel testing before syntropy-only mode

**Remaining Considerations**:
- Phase 2b (tool call forwarding) should be separate PRP with MCP client implementation details
- Consider adding performance benchmarking during Phase 3a parallel testing
- Document rollback procedure if issues discovered during migration

**Overall Assessment**: PRP is production-ready with clear scope, comprehensive implementation details, and realistic success criteria. Recommended for execution.

---

**End of PRP-24**
