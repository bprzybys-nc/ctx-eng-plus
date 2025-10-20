#!/usr/bin/env node
/**
 * Syntropy MCP Server - Unified Tool Aggregation Layer
 *
 * Routes tool calls in format syntropy:server:tool to underlying MCP servers.
 * Preserves all original functionality while providing unified namespace.
 *
 * Architecture:
 * 1. Parse syntropy:server:tool format
 * 2. Validate tool names
 * 3. Forward to underlying MCP server
 *
 * Error Handling:
 * - Invalid tool format → Clear error with troubleshooting
 * - Validation errors → Fast failure
 * - Connection errors → Graceful fallback with logging
 *
 * Production Features:
 * - Structured logging with timestamps
 * - Graceful shutdown on signals
 * - Connection pooling and lifecycle management
 * - Health status monitoring
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError
} from "@modelcontextprotocol/sdk/types.js";
import { MCPClientManager } from "./client-manager.js";
import { SYNTROPY_TOOLS } from "./tools-definition.js";
import path from "path";
import { fileURLToPath } from "url";

// Get the directory of this file for resolving servers.json
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize client manager for forwarding
const clientManager = new MCPClientManager(path.join(__dirname, "../servers.json"));

// Tool routing configuration
// CRITICAL: Keys MUST match servers.json pool keys (syn-XXXX)
// Maps: syn-XXXX (pool key) -> mcp__XXXX__ (tool name prefix)
const SERVER_ROUTES: Record<string, string> = {
  "syn-serena": "mcp__serena__",
  "syn-filesystem": "mcp__filesystem__",
  "syn-git": "mcp__git__",
  "syn-context7": "mcp__context7__",
  "syn-thinking": "mcp__sequential-thinking__",
  "syn-linear": "mcp__linear-server__",
  "syn-repomix": "mcp__repomix__"
};

/**
 * Parse syntropy tool name into server and tool components.
 *
 * Handles formats:
 * - mcp__syntropy_server_tool (from Claude Code after prefix is added)
 * - syntropy_server_tool (direct format for testing)
 */
function parseSyntropyTool(toolName: string): { server: string; tool: string } | null {
  // Handle format: mcp__syntropy_server_tool
  let match = toolName.match(/^mcp__syntropy_([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  // Handle format: syntropy_server_tool (direct)
  match = toolName.match(/^syntropy_([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  return null;
}

/**
 * Map short server name to pool key.
 * Example: "filesystem" -> "syn-filesystem"
 */
function getPoolKey(shortServer: string): string {
  return `syn-${shortServer}`;
}

/**
 * Map tool names that use hyphens in actual server but underscores in our definitions.
 * Example: resolve_library_id -> resolve-library-id for Context7
 */
function normalizeToolName(server: string, tool: string): string {
  // Context7 tools use hyphens instead of underscores
  if (server === "context7") {
    return tool.replace(/_/g, "-");
  }
  // Sequential Thinking uses no separators
  if (server === "thinking") {
    return tool;
  }
  return tool;
}

/**
 * Convert syntropy tool name to underlying MCP tool name.
 */
function toMcpToolName(server: string, tool: string): string {
  const poolKey = getPoolKey(server);
  const prefix = SERVER_ROUTES[poolKey];

  if (!prefix) {
    const validServers = Object.keys(SERVER_ROUTES)
      .map(k => k.replace(/^syn-/, ""))
      .join(", ");
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Unknown syntropy server: ${server}\n` +
      `Valid servers: ${validServers}\n` +
      `🔧 Troubleshooting: Use format syntropy:<server>:<tool>`
    );
  }

  // Normalize tool name based on server (handles hyphens, etc.)
  const normalizedTool = normalizeToolName(server, tool);
  return `${prefix}${normalizedTool}`;
}

/**
 * Convert MCP tool name to syntropy format.
 */
function toSyntropyToolName(mcpToolName: string): string | null {
  const match = mcpToolName.match(/^mcp__([^_]+)__(.+)$/);
  if (!match) return null;

  const [, serverPrefix, tool] = match;

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
        listChanged: false
      },
    },
  }
);

/**
 * Handle tool listing request.
 *
 * CRITICAL: Each tool must include inputSchema to be properly registered by Claude Code.
 * The inputSchema defines the parameters a tool accepts, which is ESSENTIAL for:
 * 1. Tool discovery and registration
 * 2. Parameter validation
 * 3. Claude Code MCP integration
 *
 * Tools are exposed in proper MCP format with full JSON Schema definitions.
 * This ensures compatibility with all MCP clients including Claude Code, Claude Desktop,
 * and other integrations.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  // Use tool definitions with proper inputSchema from tools-definition.ts
  return { tools: SYNTROPY_TOOLS };
});

/**
 * Handle tool call request.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // DEBUG: Log the incoming tool name
  console.error(`[Syntropy] DEBUG: Received tool call: "${name}"`);
  console.error(`[Syntropy] DEBUG: Tool args:`, JSON.stringify(args));

  // Parse syntropy tool name (format: mcp__syntropy_server_tool, added by Claude Code)
  const parsed = parseSyntropyTool(name);
  if (!parsed) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Invalid syntropy tool name: ${name}\n` +
      `Expected format: mcp__syntropy_server_tool (e.g., mcp__syntropy_serena_find_symbol)\n` +
      `Tool name breakdown:\n` +
      `  mcp__ = Claude Code prefix\n` +
      `  syntropy = server name\n` +
      `  server = underlying server (serena, filesystem, git, context7, thinking, linear, repomix)\n` +
      `  tool = tool name\n` +
      `🔧 Troubleshooting: Verify tool name format and that underlying server is configured`
    );
  }

  const { server: targetServer, tool } = parsed;

  // Convert to underlying MCP tool name (validation only)
  toMcpToolName(targetServer, tool);

  // Forward to underlying MCP server using pool key
  const poolKey = getPoolKey(targetServer);
  try {
    const result = await clientManager.callTool(poolKey, tool, args as Record<string, unknown>);
    // Return result in MCP ToolResultBlockParam format
    return {
      content: [
        {
          type: "text" as const,
          text: typeof result === "string" ? result : JSON.stringify(result),
        },
      ],
    };
  } catch (error) {
    throw new McpError(
      ErrorCode.InternalError,
      `Failed to forward tool call: ${name}
` +
      `Error: ${error}
` +
      `🔧 Troubleshooting: Check server configuration and tool arguments`
    );
  }
});

// Start server only when not running tests
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Syntropy MCP Server running on stdio");

  // Handle graceful shutdown
  const shutdown = async (signal: string) => {
    console.error(`[Syntropy] Received ${signal}, shutting down gracefully...`);
    try {
      await clientManager.closeAll();
      console.error("[Syntropy] Cleanup complete");
      process.exit(0);
    } catch (error) {
      console.error("[Syntropy] Error during shutdown:", error);
      process.exit(1);
    }
  };

  // Register signal handlers
  process.on("SIGINT", () => shutdown("SIGINT"));
  process.on("SIGTERM", () => shutdown("SIGTERM"));
  
  // Log server startup
  console.error(`[Syntropy] Server initialized with ${Object.keys(SERVER_ROUTES).length} supported MCP servers`);
}

// Only start server when run directly (not imported for testing)
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error("[Syntropy] Fatal error:", error);
    process.exit(1);
  });
}

// Export for testing
export { parseSyntropyTool, toMcpToolName, toSyntropyToolName };
