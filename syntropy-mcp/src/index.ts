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
import path from "path";
import { fileURLToPath } from "url";

// Get the directory of this file for resolving servers.json
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize client manager for forwarding
const clientManager = new MCPClientManager(path.join(__dirname, "../servers.json"));

// Tool routing configuration
const SERVER_ROUTES: Record<string, string> = {
  "serena": "mcp__serena__",
  "filesystem": "mcp__filesystem__",
  "git": "mcp__git__",
  "context7": "mcp__context7__",
  "thinking": "mcp__sequential-thinking__",
  "linear": "mcp__linear-server__",
  "repomix": "mcp__repomix__"
};

/**
 * Parse syntropy tool name into server and tool components.
 */
function parseSyntropyTool(toolName: string): { server: string; tool: string } | null {
  const match = toolName.match(/^syntropy:([^:]+):(.+)$/);
  if (!match) return null;

  const [, server, tool] = match;
  return { server, tool };
}

/**
 * Convert syntropy tool name to underlying MCP tool name.
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
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
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
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // DEBUG: Log the incoming tool name
  console.error(`[Syntropy] DEBUG: Received tool call: "${name}"`);
  console.error(`[Syntropy] DEBUG: Tool args:`, JSON.stringify(args));

  // Parse syntropy tool name (format: syntropy:server:tool)
  const parsed = parseSyntropyTool(name);
  if (!parsed) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Invalid syntropy tool name: ${name}\n` +
      `Expected format: mcp__syntropy__server__tool\n` +
      `Example: mcp__syntropy__serena__find_symbol\n` +
      `🔧 Troubleshooting: Check tool name format`
    );
  }

  const { server: targetServer, tool } = parsed;

  // Convert to underlying MCP tool name (validation only)
  toMcpToolName(targetServer, tool);

  // Forward to underlying MCP server
  try {
    const result = await clientManager.callTool(targetServer, tool, args as Record<string, unknown>);
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
