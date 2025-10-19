/**
 * MCP Client Manager - Spawns and manages connections to underlying MCP servers.
 *
 * Uses StdioClientTransport to spawn child processes and communicate via stdio.
 * Connection pooling: spawn on first use, reuse for subsequent calls.
 * Handles errors with troubleshooting guidance.
 */

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
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
 */
class MCPClientManager {
  private serverPools: Map<string, ServerPool> = new Map();
  private serversConfigPath: string;

  constructor(serversConfigPath: string = "./servers.json") {
    this.serversConfigPath = serversConfigPath;
    this.loadServerConfigs();
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
