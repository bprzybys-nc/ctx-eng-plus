import { test, describe } from "node:test";
import { strict as assert } from "node:assert";
import { runHealthCheck, formatHealthCheckText, type HealthCheckResult, type ServerHealth } from "./health-checker.js";
import { MCPClientManager } from "./client-manager.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe("Health Checker", () => {
  test("runHealthCheck returns structured result with all required fields", async () => {
    const manager = new MCPClientManager(path.join(__dirname, "../servers.json"));
    try {
      const result = await runHealthCheck(manager, 5000);

      // Verify syntropy status
      assert.ok(result.syntropy, "Should include syntropy status");
      assert.equal(result.syntropy.status, "healthy", "Syntropy should be healthy");
      assert.ok(result.syntropy.version, "Should include version");

      // Verify servers array
      assert.ok(Array.isArray(result.servers), "servers should be array");
      assert.ok(result.servers.length > 0, "Should have servers");

      // Verify summary
      assert.ok(result.summary, "Should include summary");
      assert.ok(typeof result.summary.total === "number", "summary.total should be number");
      assert.ok(typeof result.summary.healthy === "number", "summary.healthy should be number");
      assert.ok(typeof result.summary.degraded === "number", "summary.degraded should be number");
      assert.ok(typeof result.summary.down === "number", "summary.down should be number");

      // Verify timestamp
      assert.ok(result.timestamp, "Should include timestamp");
      assert.doesNotThrow(() => new Date(result.timestamp), "timestamp should be valid ISO date");
    } finally {
      await manager.closeAll();
    }
  });

  test("each server in result has required fields", async () => {
    const manager = new MCPClientManager(path.join(__dirname, "../servers.json"));
    try {
      const result = await runHealthCheck(manager, 5000);

      for (const server of result.servers) {
        assert.ok(server.server, "server.server should exist");
        assert.ok(["healthy", "degraded", "down"].includes(server.status), "server.status should be one of healthy/degraded/down");
        assert.ok(typeof server.connected === "boolean", "server.connected should be boolean");
        assert.ok(typeof server.callCount === "number", "server.callCount should be number");
        assert.ok(typeof server.checkDuration === "number", "server.checkDuration should be number");

        // Only failed servers have lastError
        if (server.status !== "healthy") {
          assert.ok(server.lastError, "Failed servers should have lastError");
        }
      }
    } finally {
      await manager.closeAll();
    }
  });

  test("summary counts match servers array", async () => {
    const manager = new MCPClientManager(path.join(__dirname, "../servers.json"));
    try {
      const result = await runHealthCheck(manager, 5000);

      const healthyCount = result.servers.filter((s) => s.status === "healthy").length;
      const degradedCount = result.servers.filter((s) => s.status === "degraded").length;
      const downCount = result.servers.filter((s) => s.status === "down").length;

      assert.equal(result.summary.healthy, healthyCount, "summary.healthy should match count");
      assert.equal(result.summary.degraded, degradedCount, "summary.degraded should match count");
      assert.equal(result.summary.down, downCount, "summary.down should match count");
      assert.equal(result.summary.total, result.servers.length, "summary.total should match servers.length");
    } finally {
      await manager.closeAll();
    }
  });

  test("formatHealthCheckText produces readable output with status icons", () => {
    const mockResult: HealthCheckResult = {
      syntropy: { version: "0.1.0", status: "healthy" },
      servers: [
        {
          server: "filesystem",
          status: "healthy",
          connected: true,
          callCount: 0,
          checkDuration: 150,
        },
        {
          server: "git",
          status: "degraded",
          connected: false,
          callCount: 0,
          lastError: "Authentication required",
          checkDuration: 2000,
        },
        {
          server: "serena",
          status: "down",
          connected: false,
          callCount: 0,
          lastError: "Connection refused",
          checkDuration: 2000,
        },
      ],
      summary: { total: 3, healthy: 1, degraded: 1, down: 1 },
      timestamp: "2025-01-20T00:00:00Z",
    };

    const text = formatHealthCheckText(mockResult);

    // Check for required components
    assert.ok(text.includes("✅ Syntropy MCP Server: Healthy"), "Should include Syntropy status");
    assert.ok(text.includes("MCP Server Status:"), "Should include server status header");
    assert.ok(text.includes("✅ filesystem"), "Should show healthy filesystem with ✅");
    assert.ok(text.includes("⚠️ git"), "Should show degraded git with ⚠️");
    assert.ok(text.includes("❌ serena"), "Should show down serena with ❌");
    assert.ok(text.includes("1/3 healthy"), "Should show correct counts");
    assert.ok(text.includes("1/3 degraded"), "Should show degraded count");
    assert.ok(text.includes("1/3 down"), "Should show down count");
    assert.ok(text.includes("🔧 Troubleshooting:"), "Should include troubleshooting section");
  });

  test("formatHealthCheckText shows correct troubleshooting for failures", () => {
    const mockResultWithDegraded: HealthCheckResult = {
      syntropy: { version: "0.1.0", status: "healthy" },
      servers: [
        {
          server: "github",
          status: "degraded",
          connected: false,
          callCount: 0,
          lastError: "Unauthorized",
          checkDuration: 100,
        },
      ],
      summary: { total: 1, healthy: 0, degraded: 1, down: 0 },
      timestamp: "2025-01-20T00:00:00Z",
    };

    const text = formatHealthCheckText(mockResultWithDegraded);
    assert.ok(text.includes("Degraded servers may require authentication"), "Should mention auth for degraded");

    const mockResultWithDown: HealthCheckResult = {
      syntropy: { version: "0.1.0", status: "healthy" },
      servers: [
        {
          server: "serena",
          status: "down",
          connected: false,
          callCount: 0,
          lastError: "Connection refused",
          checkDuration: 2000,
        },
      ],
      summary: { total: 1, healthy: 0, degraded: 0, down: 1 },
      timestamp: "2025-01-20T00:00:00Z",
    };

    const text2 = formatHealthCheckText(mockResultWithDown);
    assert.ok(text2.includes("Down servers may not be installed"), "Should mention installation for down");
    assert.ok(text2.includes("servers.json"), "Should mention servers.json config");
  });

  test("formatHealthCheckText shows healthy status without troubleshooting", () => {
    const mockResultHealthy: HealthCheckResult = {
      syntropy: { version: "0.1.0", status: "healthy" },
      servers: [
        {
          server: "filesystem",
          status: "healthy",
          connected: true,
          callCount: 5,
          checkDuration: 100,
        },
        {
          server: "git",
          status: "healthy",
          connected: true,
          callCount: 3,
          checkDuration: 150,
        },
      ],
      summary: { total: 2, healthy: 2, degraded: 0, down: 0 },
      timestamp: "2025-01-20T00:00:00Z",
    };

    const text = formatHealthCheckText(mockResultHealthy);
    assert.ok(!text.includes("🔧 Troubleshooting"), "Should not show troubleshooting for healthy systems");
    assert.ok(text.includes("2/2 healthy"), "Should show all healthy");
  });

  test("health check respects timeout parameter", async () => {
    const manager = new MCPClientManager(path.join(__dirname, "../servers.json"));
    const startTime = Date.now();

    try {
      // Use 1 second timeout
      await runHealthCheck(manager, 1000);

      const duration = Date.now() - startTime;
      // Should complete within reasonable time (parallel checks with 1s timeout each)
      // Allow up to 5 seconds for slow networks/systems
      assert.ok(duration < 5000, `Health check took ${duration}ms (expected <5000ms)`);
    } finally {
      await manager.closeAll();
    }
  });

  test("health check includes call counts from manager status", async () => {
    const manager = new MCPClientManager(path.join(__dirname, "../servers.json"));
    try {
      const result = await runHealthCheck(manager, 5000);

      // All servers should have callCount as number (even if 0)
      for (const server of result.servers) {
        assert.ok(typeof server.callCount === "number", `${server.server} should have numeric callCount`);
        assert.ok(server.callCount >= 0, `${server.server} callCount should be >= 0`);
      }
    } finally {
      await manager.closeAll();
    }
  });

  test("health check determines status correctly for different error types", async () => {
    const manager = new MCPClientManager(path.join(__dirname, "../servers.json"));
    try {
      const result = await runHealthCheck(manager, 5000);

      // Verify status classification logic
      for (const server of result.servers) {
        if (server.status === "degraded") {
          // Degraded should have auth-related errors
          assert.ok(server.lastError, "degraded servers should have error message");
          const msg = server.lastError.toLowerCase();
          assert.ok(
            msg.includes("auth") ||
            msg.includes("token") ||
            msg.includes("unauthorized") ||
            msg.includes("forbidden"),
            `degraded error should be auth-related: ${server.lastError}`
          );
        } else if (server.status === "down") {
          // Down should have non-auth errors or timeout
          assert.ok(server.lastError, "down servers should have error message");
        }
      }
    } finally {
      await manager.closeAll();
    }
  });

  test("formatHealthCheckText truncates long server names correctly", () => {
    const mockResult: HealthCheckResult = {
      syntropy: { version: "0.1.0", status: "healthy" },
      servers: [
        {
          server: "very_long_server_name_that_exceeds_padding",
          status: "healthy",
          connected: true,
          callCount: 0,
          checkDuration: 100,
        },
      ],
      summary: { total: 1, healthy: 1, degraded: 0, down: 0 },
      timestamp: "2025-01-20T00:00:00Z",
    };

    const text = formatHealthCheckText(mockResult);
    // Should still include the full server name even if it exceeds padding
    assert.ok(text.includes("very_long_server_name_that_exceeds_padding"), "Should include full server name");
  });
});
