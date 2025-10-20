/**
 * MCP Client Manager - Spawns and manages connections to underlying MCP servers.
 *
 * Uses StdioClientTransport to spawn child processes and communicate via stdio.
 * Connection pooling: spawn on first use, reuse for subsequent calls.
 * Handles errors with troubleshooting guidance.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { ListToolsResultSchema } from "@modelcontextprotocol/sdk/types.js";
import fs from "fs";

/**
 * Production logging with structured output.
 */
class Logger {
  private prefix = "[Syntropy]";
  
  info(msg: string, data?: unknown) {
    console.error(`${this.prefix} INFO: ${msg}`, data ? JSON.stringify(data) : "");
  }
  
  warn(msg: string, data?: unknown) {
    console.error(`${this.prefix} WARN: ${msg}`, data ? JSON.stringify(data) : "");
  }
  
  error(msg: string, err?: unknown) {
    console.error(`${this.prefix} ERROR: ${msg}`, err ? String(err) : "");
  }
}

const logger = new Logger();

interface ServerConfig {
  command: string;
  args: string[];
  env: Record<string, string>;
  lazy?: boolean;  // NEW: default true (lazy initialization). Set to false for eager init on startup
}

interface ServerPool {
  config: ServerConfig;
  client?: Client;
  transport?: StdioClientTransport;
  connecting?: Promise<Client>;
  callCount: number;
  lastError?: Error;
}

/**
 * Manages MCP client connections to underlying servers.
 * Lazy initialization: spawns process on first tool call.
 * Eager initialization: optionally spawns critical servers on startup (configured via lazy: false in servers.json).
 */
class MCPClientManager {
  private serverPools: Map<string, ServerPool> = new Map();
  private serversConfigPath: string;
  private eagerInitPromise?: Promise<void>;  // NEW: Track eager init status

  constructor(serversConfigPath: string = "./servers.json") {
    this.serversConfigPath = serversConfigPath;
    this.loadServerConfigs();

    // NEW: Automatically start eager initialization based on server config
    // No parameter needed - determined by servers.json `lazy: false`
    this.eagerInitPromise = this.initializeEagerServersWithHealthCheck();
  }

  /**
   * Wait for eager servers to be fully initialized and healthy.
   * Call this to ensure all critical servers (lazy: false) are ready before proceeding.
   *
   * @returns Promise that resolves when all eager servers are initialized
   *
   * @example
   * const manager = new MCPClientManager("./servers.json");
   * await manager.waitForEagerInit();  // Wait for health verification
   * // All eager servers verified healthy
   */
  public async waitForEagerInit(): Promise<void> {
    if (this.eagerInitPromise) {
      await this.eagerInitPromise;
    }
  }

  /**
   * Load server configurations from servers.json.
   * @throws {Error} If config file not found or invalid
   */
  private loadServerConfigs(): void {
    if (!fs.existsSync(this.serversConfigPath)) {
      const msg = `MCP servers config not found: ${this.serversConfigPath}`;
      logger.error(msg);
      throw new Error(
        `${msg}\n` +
        `🔧 Troubleshooting: Create servers.json with MCP server configurations`
      );
    }

    try {
      const config = JSON.parse(
        fs.readFileSync(this.serversConfigPath, "utf-8")
      );

      for (const [serverName, serverConfig] of Object.entries(
        config.servers || {}
      )) {
        this.serverPools.set(serverName, {
          config: serverConfig as ServerConfig,
          callCount: 0,
        });
      }
      logger.info(`Loaded ${this.serverPools.size} MCP server configs`);
    } catch (error) {
      const msg = `Failed to load servers.json: ${error}`;
      logger.error(msg, error);
      throw new Error(
        `${msg}\n` +
        `🔧 Troubleshooting: Verify JSON syntax in servers.json`
      );
    }
  }

  /**
   * Get MCP client for a server, spawning if necessary.
   * @param server - Server name (e.g., "filesystem")
   * @returns MCP Client instance
   * @throws {Error} If server not configured or spawn fails
   */
  async getClient(server: string): Promise<Client> {
    const pool = this.serverPools.get(server);

    if (!pool) {
      const validServers = Array.from(this.serverPools.keys()).join(", ");
      const msg = `Unknown MCP server: ${server}`;
      logger.error(msg);
      throw new Error(
        `${msg}\n` +
        `Valid servers: ${validServers}\n` +
        `🔧 Troubleshooting: Check servers.json configuration`
      );
    }

    // Return existing client if available
    if (pool.client) {
      return pool.client;
    }

    // Return pending connection if in progress
    if (pool.connecting) {
      logger.info(`Waiting for pending connection: ${server}`);
      return pool.connecting;
    }

    // Start new connection
    logger.info(`Connecting to MCP server: ${server}`);
    pool.connecting = this.connectToServer(server, pool);
    try {
      pool.client = await pool.connecting;
      logger.info(`Connected to MCP server: ${server}`);
      return pool.client;
    } finally {
      pool.connecting = undefined;
    }
  }

  /**
   * Connect to MCP server by spawning child process.
   * @private
   */
  private async connectToServer(
    server: string,
    pool: ServerPool
  ): Promise<Client> {
    const { command, args, env } = pool.config;
    const startTime = Date.now();

    try {
      logger.info(`Spawning process for ${server}: ${command} ${args.join(" ")}`);
      
      // Create transport with command and args
      const transport = new StdioClientTransport({
        command: command,
        args: args,
        env: { ...Object.fromEntries(Object.entries(process.env).filter(([_, v]) => v !== undefined)), ...env } as Record<string, string>,
      });

      pool.transport = transport;

      // Create MCP client
      const client = new Client(
        {
          name: `syntropy-${server}`,
          version: "0.1.0",
        },
        {
          capabilities: {},
        }
      );

      await client.connect(transport);
      
      const duration = Date.now() - startTime;
      logger.info(`Connected to ${server} in ${duration}ms`);

      return client;
    } catch (error) {
      const duration = Date.now() - startTime;
      logger.error(`Failed to connect to ${server} after ${duration}ms: ${error}`);
      pool.lastError = error as Error;
      throw new Error(
        `Failed to connect to ${server} MCP server: ${error}\n` +
        `Command: ${command} ${args.join(" ")}\n` +
        `🔧 Troubleshooting: Ensure ${server} MCP server is available`
      );
    }
  }

  /**
   * Health check: Verify server is responding to MCP requests.
   * Uses tools/list introspection (available on all MCP servers).
   *
   * @param serverName - Server identifier
   * @param client - Connected MCP client
   * @returns true if server responds with tools list, false otherwise
   */
  private async healthCheckServer(serverName: string, client: Client): Promise<boolean> {
    try {
      // Call ListTools - lightweight introspection on all MCP servers
      const result = await client.request(
        { method: "tools/list" },
        ListToolsResultSchema
      );

      // Server is healthy if it responds with tools list
      logger.info(
        `✅ Health check passed for ${serverName}: ${result.tools.length} tools available`
      );
      return true;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : String(error);
      logger.warn(
        `❌ Health check failed for ${serverName}: ${errorMsg}\n` +
        `🔧 Troubleshooting: Server started but not responding to MCP requests. ` +
        `Check server logs, credentials, and network connectivity.`
      );
      return false;
    }
  }

  /**
   * Eagerly initialize all servers configured with lazy: false.
   * Spawns processes in parallel, verifies health, reports results.
   * Non-blocking: Failed servers don't prevent startup.
   *
   * @returns Promise that resolves when all eager servers initialized
   */
  private async initializeEagerServersWithHealthCheck(): Promise<void> {
    // Identify servers configured with lazy: false
    const eagerServers = Array.from(this.serverPools.entries())
      .filter(([_, pool]) => pool.config.lazy === false)
      .map(([serverName, _]) => serverName);

    // Early exit if no eager servers configured
    if (eagerServers.length === 0) {
      logger.info("ℹ️ No eager servers configured - all servers will lazy-load on demand");
      return;
    }

    // 🐛 DEBUG: Log eager server list
    logger.info(
      `🐛 DEBUG: Eager servers configured: ${eagerServers.join(", ")}\n` +
      `🐛 DEBUG: Starting parallel initialization...`
    );
    const startTime = Date.now();

    // Phase 1: Initialize all servers in parallel (spawn processes)
    logger.info(`🐛 DEBUG: Phase 1 - Spawning ${eagerServers.length} processes...`);
    const initResults = await Promise.allSettled(
      eagerServers.map(serverName => this.getClient(serverName))
    );

    // 🐛 DEBUG: Log spawn results
    const spawnTime = Date.now() - startTime;
    const spawnedCount = initResults.filter(r => r.status === "fulfilled").length;
    logger.info(
      `🐛 DEBUG: Phase 1 complete - ${spawnedCount}/${eagerServers.length} spawned in ${spawnTime}ms`
    );

    // Phase 2: Health check each server (verify responding)
    logger.info(`🐛 DEBUG: Phase 2 - Running health checks...`);
    const healthCheckResults = await Promise.allSettled(
      initResults.map(async (result, index) => {
        if (result.status === "rejected") {
          // Connection failed - can't health check
          throw new Error(`Failed to connect: ${result.reason}`);
        }
        // result.value is the Client - health check it
        return this.healthCheckServer(eagerServers[index], result.value);
      })
    );

    // Phase 3: Report results
    let successCount = 0;
    let failureCount = 0;

    healthCheckResults.forEach((result, index) => {
      if (result.status === "fulfilled" && result.value === true) {
        logger.info(`✅ ${eagerServers[index]} - Ready`);
        successCount++;
      } else {
        const reason = result.status === "rejected"
          ? (result.reason instanceof Error ? result.reason.message : String(result.reason))
          : "Health check failed";
        logger.warn(
          `⚠️ ${eagerServers[index]} - Failed (${reason})\n` +
          `🔧 Troubleshooting: Check server logs and configuration`
        );
        failureCount++;
      }
    });

    const duration = Date.now() - startTime;

    // 🐛 DEBUG: Final summary with timing breakdown
    logger.info(
      `🐛 DEBUG: Phase 2 complete - ${successCount} healthy, ${failureCount} failed\n` +
      `🎯 Eager init complete in ${duration}ms: ${successCount}/${eagerServers.length} servers healthy\n` +
      `   - Spawn time: ${spawnTime}ms\n` +
      `   - Health check time: ${duration - spawnTime}ms`
    );

    if (failureCount > 0) {
      logger.warn(
        `⚠️ ${failureCount} critical server(s) failed initialization\n` +
        `🔧 Some features may not work - check configuration and server logs`
      );
    }
  }

  /**
   * Call tool on underlying MCP server.
   * @param server - Server name
   * @param tool - Tool name
   * @param args - Tool arguments
   * @returns Tool call result
   * @throws {Error} If tool call fails
   */
  async callTool(
    server: string,
    tool: string,
    args: Record<string, unknown>
  ): Promise<unknown> {
    const pool = this.serverPools.get(server);
    const startTime = Date.now();
    
    try {
      const client = await this.getClient(server);
      if (pool) pool.callCount++;

      logger.info(`Calling tool: ${server}:${tool}`);
      
      // Call tool on underlying server
      const result = await client.callTool({
        name: tool,
        arguments: args,
      });

      const duration = Date.now() - startTime;
      logger.info(`Tool call completed: ${server}:${tool} (${duration}ms)`);
      
      return result;
    } catch (error) {
      const duration = Date.now() - startTime;
      if (pool) pool.lastError = error as Error;
      logger.error(`Tool call failed: ${server}:${tool} after ${duration}ms: ${error}`);
      throw new Error(
        `Tool call failed: ${server}:${tool}\n` +
        `Error: ${error}\n` +
        `🔧 Troubleshooting: Check tool name and arguments`
      );
    }
  }

  /**
   * Get health status of all servers.
   */
  getStatus(): Record<string, { connected: boolean; callCount: number; lastError?: string }> {
    const status: Record<string, { connected: boolean; callCount: number; lastError?: string }> = {};
    
    for (const [serverName, pool] of this.serverPools.entries()) {
      status[serverName] = {
        connected: !!pool.client,
        callCount: pool.callCount,
        lastError: pool.lastError?.message,
      };
    }
    
    return status;
  }

  /**
   * Close all connections and cleanup resources.
   */
  async closeAll(): Promise<void> {
    logger.info(`Closing ${this.serverPools.size} MCP server connections`);
    
    for (const [serverName, pool] of this.serverPools.entries()) {
      if (pool.client) {
        try {
          await pool.client.close();
          logger.info(`Closed connection: ${serverName}`);
        } catch (error) {
          logger.error(`Error closing ${serverName} client`, error);
        }
      }
    }

    this.serverPools.clear();
    logger.info("All MCP server connections closed");
  }
}

export { MCPClientManager, Logger };
export type { ServerConfig, ServerPool };
