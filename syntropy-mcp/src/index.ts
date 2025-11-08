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
import { runHealthCheck, formatHealthCheckText } from "./health-checker.js";
import { initProject } from "./tools/init.js";
import { getSystemDoc, getUserDoc, knowledgeSearch } from "./tools/knowledge.js";
import { getSyntropySummary } from "./tools/summary.js";
import { denoise } from "./tools/denoise.js";
import { ToolStateManager } from "./tool-manager.js";
// After SYNTROPY_TOOLS import
console.error(`[SYNTROPY DEBUG] Registering ${SYNTROPY_TOOLS.length} tools`);
console.error(`[SYNTROPY DEBUG] Tool 58: ${SYNTROPY_TOOLS[57]?.name || 'N/A'}`);
import path from "path";
import { fileURLToPath } from "url";

// Get the directory of this file for resolving servers.json
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize client manager for forwarding
const clientManager = new MCPClientManager(path.join(__dirname, "../servers.json"));

// Initialize tool state manager
const toolStateManager = new ToolStateManager();

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
  "syn-repomix": "mcp__repomix__",
  "syn-github": "mcp__github__",
  "syn-perplexity": "mcp__perplexity__"
};

/**
 * Parse syntropy tool name into server and tool components.
 *
 * Handles formats:
 * - mcp__syntropy_server_tool (from Claude Code: mcp__ + server name "syntropy" + tool name)
 * - server_tool (direct format for testing)
 */
function parseSyntropyTool(toolName: string): { server: string; tool: string } | null {
  // Handle format: mcp__syntropy__server_tool (double underscore - Claude Code actual behavior)
  // Claude Code transforms: "serena_find_symbol" -> "mcp__syntropy__serena_find_symbol"
  let match = toolName.match(/^mcp__syntropy__([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  // Handle legacy format: mcp__syntropy_server_tool (single underscore - for backwards compat)
  match = toolName.match(/^mcp__syntropy_([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  // Handle format: server_tool (direct, for testing)
  match = toolName.match(/^([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  return null;
}

/**
 * Match tool name against multiple variants (double underscore, single underscore, short form).
 * This elegant helper eliminates repetitive OR chains in conditionals.
 *
 * Example: matchesTool(name, "healthcheck") matches:
 * - mcp__syntropy__healthcheck (Claude Code standard)
 * - mcp__syntropy_healthcheck (legacy single underscore)
 * - syntropy_healthcheck (legacy prefix)
 * - healthcheck (short form)
 *
 * @param name - The tool name to check
 * @param shortName - The short form tool name (e.g., "healthcheck", "init_project")
 * @returns true if name matches any variant
 */
function matchesTool(name: string, shortName: string): boolean {
  return name === `mcp__syntropy__${shortName}` ||
         name === `mcp__syntropy_${shortName}` ||
         name === `syntropy_${shortName}` ||
         name === shortName;
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
 *
 * FILTERING: Tools are filtered by enabled state from ToolStateManager.
 * Default behavior: All tools enabled (empty enabled list = wildcard).
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  // Filter tools by enabled state
  const enabledTools = SYNTROPY_TOOLS.filter(tool => {
    const toolName = `mcp__syntropy__${tool.name}`;
    return toolStateManager.isEnabled(toolName);
  });

  // Add mcp__syntropy__ prefix to returned tool names so Claude Code can call them
  return {
    tools: enabledTools.map(tool => ({
      ...tool,
      name: `mcp__syntropy__${tool.name}`
    }))
  };
});

/**
 * Handle tool call request.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // DEBUG: Log the incoming tool name
  console.error(`[Syntropy] DEBUG: Received tool call: "${name}"`);
  console.error(`[Syntropy] DEBUG: Tool args:`, JSON.stringify(args));

  // Handle healthcheck tool (special case - direct implementation, no forwarding)
  if (matchesTool(name, "healthcheck")) {
    const detailed = (args as { detailed?: boolean }).detailed ?? false;
    const timeoutMs = (args as { timeout_ms?: number }).timeout_ms ?? 2000;

    try {
      const result = await runHealthCheck(clientManager, timeoutMs);

      if (detailed) {
        // Return full JSON for automation
        return {
          content: [
            {
              type: "text" as const,
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } else {
        // Return human-readable format
        return {
          content: [
            {
              type: "text" as const,
              text: formatHealthCheckText(result),
            },
          ],
        };
      }
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Health check failed: ${error}\n` +
        `🔧 Troubleshooting: Check Syntropy server logs`
      );
    }
  }

  // Handle init project tool (special case - direct implementation, no forwarding)
  if (matchesTool(name, "init_project")) {
    try {
      const result = await initProject(args as { project_root: string });
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Project initialization failed: ${error}\n` +
        `🔧 Troubleshooting: Check project path and permissions`
      );
    }
  }

  // Handle knowledge query tools (direct implementation, no forwarding)
  if (matchesTool(name, "get_system_doc")) {
    const result = await getSystemDoc(args as { project_root: string; doc_path: string });
    return {
      content: [{
        type: "text" as const,
        text: result.success ? result.content! : `Error: ${result.error}`
      }]
    };
  }

  if (matchesTool(name, "get_user_doc")) {
    const result = await getUserDoc(args as { project_root: string; doc_path: string });
    return {
      content: [{
        type: "text" as const,
        text: result.success ? result.content! : `Error: ${result.error}`
      }]
    };
  }

  if (matchesTool(name, "knowledge_search")) {
    const result = await knowledgeSearch(args as any);
    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify(result, null, 2)
      }]
    };
  }

  if (matchesTool(name, "get_summary")) {
    const result = await getSyntropySummary(args as any);
    return {
      content: [{
        type: "text" as const,
        text: result.success ? result.summary! : `Error: ${result.error}`
      }]
    };
  }

  if (matchesTool(name, "denoise")) {
    const result = await denoise(args as any);
    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify(result, null, 2)
      }]
    };
  }

  // Handle enable_tools command (dynamic tool management)
  if (matchesTool(name, "enable_tools")) {
    const { enable = [], disable = [] } = args as {
      enable?: string[];
      disable?: string[];
    };

    try {
      await toolStateManager.enableTools(enable, disable);
      const state = toolStateManager.getState();

      return {
        content: [{
          type: "text" as const,
          text: JSON.stringify({
            success: true,
            message: 'Tool state updated successfully',
            enabled_count: state.enabled.length,
            disabled_count: state.disabled.length,
            state_file: '~/.syntropy/tool-state.json'
          }, null, 2)
        }]
      };
    } catch (error) {
      throw new McpError(
        ErrorCode.InternalError,
        `Failed to update tool state: ${error}\n` +
        `🔧 Troubleshooting: Check ~/.syntropy/tool-state.json permissions`
      );
    }
  }

  // Handle list_all_tools command (show all tools with status)
  if (matchesTool(name, "list_all_tools")) {
    const allTools: Array<{
      name: string;
      description: string;
      status: 'enabled' | 'disabled';
    }> = [];

    // Add all tools from SYNTROPY_TOOLS with their status
    for (const tool of SYNTROPY_TOOLS) {
      const toolName = `mcp__syntropy__${tool.name}`;
      allTools.push({
        name: toolName,
        description: tool.description || '',
        status: toolStateManager.isEnabled(toolName) ? 'enabled' : 'disabled'
      });
    }

    return {
      content: [{
        type: "text" as const,
        text: JSON.stringify({
          total_tools: allTools.length,
          enabled_tools: allTools.filter(t => t.status === 'enabled').length,
          disabled_tools: allTools.filter(t => t.status === 'disabled').length,
          tools: allTools
        }, null, 2)
      }]
    };
  }

  // Parse syntropy tool name (format: mcp__syntropy_server_tool, added by Claude Code)
  const parsed = parseSyntropyTool(name);
  if (!parsed) {
    throw new McpError(
      ErrorCode.InvalidRequest,
      `Invalid syntropy tool name: ${name}\n` +
      `Expected format: mcp__syntropy_server_tool (e.g., mcp__syntropy_serena_find_symbol)\n` +
      `Tool name breakdown:\n` +
      `  mcp__ = Claude Code MCP prefix\n` +
      `  syntropy = MCP server name\n` +
      `  server = underlying server (serena, filesystem, git, context7, thinking, linear, repomix, github, perplexity)\n` +
      `  tool = tool name\n` +
      `🔧 Troubleshooting: Verify tool name format and that underlying server is configured`
    );
  }

  const { server: targetServer, tool } = parsed;

  // Convert to underlying MCP tool name (includes normalization)
  toMcpToolName(targetServer, tool);

  // Normalize tool name for servers that use different naming conventions
  const normalizedTool = normalizeToolName(targetServer, tool);

  // Forward to underlying MCP server using pool key
  const poolKey = getPoolKey(targetServer);
  try {
    const result = await clientManager.callTool(poolKey, normalizedTool, args as Record<string, unknown>);
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

  // Initialize tool state manager
  try {
    await toolStateManager.initialize();
    console.error("✅ Tool state manager initialized");
  } catch (error) {
    console.error(`⚠️ Tool state manager initialization failed: ${error}`);
    console.error("🔧 Continuing with default state (all tools enabled)");
  }

  // NEW: Wait for eager servers with 9-second timeout protection
  try {
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("Startup timeout (9s)")), 9000)
    );

    await Promise.race([
      clientManager.waitForEagerInit(),
      timeoutPromise
    ]);

    console.error("✅ All eager servers ready - MCP server starting");
  } catch (error) {
    console.error(
      `⚠️ Eager init timeout (${(error as Error).message})\n` +
      `🔧 Check servers.json - adjust lazy settings or increase timeout\n` +
      `Continuing with degraded functionality...`
    );
  }

  // Connect MCP server (lazy servers will init on demand)
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
