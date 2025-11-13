/**
 * Health Checker for Syntropy MCP Server
 *
 * Tests connectivity to all underlying MCP servers and reports status.
 * Runs checks in parallel with timeout protection.
 *
 * Exports:
 * - runHealthCheck() - Main entry point for health checking
 * - formatHealthCheckText() - Format results as human-readable text
 * - ServerHealth, HealthCheckResult - TypeScript interfaces
 */

import type { MCPClientManager } from "./client-manager.js";
import { BUILD_TIME, VERSION } from "./build-info.js";

export interface ServerHealth {
  server: string;
  status: "healthy" | "degraded" | "down";
  connected: boolean;
  callCount: number;
  lastError?: string;
  checkDuration?: number;
}

export interface HealthCheckResult {
  syntropy: {
    version: string;
    status: "healthy";
    buildTime: string;
  };
  servers: ServerHealth[];
  summary: {
    total: number;
    healthy: number;
    degraded: number;
    down: number;
  };
  timestamp: string;
}

/**
 * Determine status based on error characteristics.
 */
function determineStatus(error: Error | unknown): "degraded" | "down" {
  const msg = error instanceof Error ? error.message.toLowerCase() : String(error).toLowerCase();

  // Authentication issues = degraded (server works, just needs config)
  if (
    msg.includes("auth") ||
    msg.includes("token") ||
    msg.includes("unauthorized") ||
    msg.includes("forbidden")
  ) {
    return "degraded";
  }

  // Everything else = down (server not working)
  return "down";
}

/**
 * Check health of a single MCP server with timeout.
 */
async function checkServerHealth(
  manager: MCPClientManager,
  serverKey: string,
  timeoutMs: number = 2000
): Promise<ServerHealth> {
  const startTime = Date.now();
  const serverName = serverKey.replace(/^syn-/, ""); // syn-filesystem -> filesystem

  try {
    // Attempt connection with timeout
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(() => reject(new Error("Timeout")), timeoutMs)
    );

    const connectPromise = manager.getClient(serverKey);
    await Promise.race([connectPromise, timeoutPromise]);

    const duration = Date.now() - startTime;

    // Get actual call count from manager status
    const currentStatus = manager.getStatus();
    const poolStatus = currentStatus[serverKey];

    return {
      server: serverName,
      status: "healthy",
      connected: true,
      callCount: poolStatus?.callCount || 0,
      checkDuration: duration,
    };
  } catch (error) {
    const duration = Date.now() - startTime;
    const errorMsg = error instanceof Error ? error.message : String(error);

    // Get call count even on failure
    const currentStatus = manager.getStatus();
    const poolStatus = currentStatus[serverKey];

    return {
      server: serverName,
      status: determineStatus(error),
      connected: false,
      callCount: poolStatus?.callCount || 0,
      lastError: errorMsg,
      checkDuration: duration,
    };
  }
}

/**
 * Run health checks on all MCP servers in parallel.
 */
export async function runHealthCheck(
  manager: MCPClientManager,
  timeoutMs: number = 2000
): Promise<HealthCheckResult> {
  // Get server list from manager's status
  const currentStatus = manager.getStatus();
  const serverKeys = Object.keys(currentStatus);

  // Run checks in parallel
  const healthChecks = serverKeys.map((serverKey) =>
    checkServerHealth(manager, serverKey, timeoutMs)
  );

  const servers = await Promise.all(healthChecks);

  // Calculate summary
  const summary = {
    total: servers.length,
    healthy: servers.filter((s) => s.status === "healthy").length,
    degraded: servers.filter((s) => s.status === "degraded").length,
    down: servers.filter((s) => s.status === "down").length,
  };

  return {
    syntropy: {
      version: VERSION,
      status: "healthy",
      buildTime: BUILD_TIME,
    },
    servers,
    summary,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Format health check result as human-readable text.
 */
export function formatHealthCheckText(result: HealthCheckResult): string {
  const lines: string[] = [];

  // Syntropy server status
  lines.push(`✅ Syntropy MCP Server: Healthy (v${result.syntropy.version})`);
  lines.push(`   Build: ${result.syntropy.buildTime}\n`);

  // Server statuses
  lines.push("MCP Server Status:");
  for (const server of result.servers) {
    const icon = server.status === "healthy" ? "✅" : server.status === "degraded" ? "⚠️" : "❌";
    const name = server.server.padEnd(15);
    const duration = server.checkDuration ? `(${server.checkDuration}ms)` : "";

    if (server.status === "healthy") {
      lines.push(`  ${icon} ${name} - Healthy ${duration}`);
    } else if (server.status === "degraded") {
      lines.push(`  ${icon} ${name} - Degraded (${server.lastError})`);
    } else {
      lines.push(`  ${icon} ${name} - Down (${server.lastError})`);
    }
  }

  // Summary
  const { total, healthy, degraded, down } = result.summary;
  lines.push(`\nTotal: ${healthy}/${total} healthy, ${degraded}/${total} degraded, ${down}/${total} down`);

  // Troubleshooting for failures
  if (degraded > 0 || down > 0) {
    lines.push("\n🔧 Troubleshooting:");
    if (degraded > 0) {
      lines.push("  - Degraded servers may require authentication (check environment variables)");
    }
    if (down > 0) {
      lines.push("  - Down servers may not be installed or configured correctly");
      lines.push("  - Check servers.json configuration and ensure dependencies are installed");
    }
  }

  return lines.join("\n");
}
