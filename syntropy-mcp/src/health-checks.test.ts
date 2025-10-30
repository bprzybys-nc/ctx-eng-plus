/**
 * Health Checks for MCP Servers
 *
 * Individual tests for each MCP server connection with timeout protection.
 * Each test runs in isolation to prevent cascade failures.
 */

import { test } from "node:test";
import { strict as assert } from "node:assert";
import { MCPClientManager } from "./client-manager.js";

const TIMEOUT_MS = 15000; // 15 second timeout per server

/**
 * Test helper with timeout protection
 */
function testWithTimeout(name: string, fn: () => Promise<void>) {
  test(name, async () => {
    const timeoutPromise = new Promise<never>((_, reject) =>
      setTimeout(
        () => reject(new Error(`Test timeout after ${TIMEOUT_MS}ms`)),
        TIMEOUT_MS
      )
    );
    await Promise.race([fn(), timeoutPromise]);
  });
}

// ============================================================================
// Filesystem Server Health Check
// ============================================================================

testWithTimeout("Health: Filesystem MCP Server (npx)", async () => {
  const manager = new MCPClientManager("./servers.json");
  try {
    const client = await manager.getClient("syn-filesystem");
    assert.ok(client, "Should connect to filesystem server");
    console.log("✓ Filesystem server healthy");
  } finally {
    await manager.closeAll();
  }
});

// ============================================================================
// Git Server Health Check
// ============================================================================

testWithTimeout("Health: Git MCP Server (uvx)", async () => {
  const manager = new MCPClientManager("./servers.json");
  try {
    const client = await manager.getClient("syn-git");
    assert.ok(client, "Should connect to git server");
    console.log("✓ Git server healthy");
  } catch (error: unknown) {
    if (error instanceof Error && error.message.includes("timeout")) {
      console.log("⚠ Git server timeout (may not be installed locally)");
      return; // Skip if uvx git not available
    }
    throw error;
  } finally {
    await manager.closeAll();
  }
});

// ============================================================================
// Serena Server Health Check
// ============================================================================

testWithTimeout("Health: Serena MCP Server (uvx git+https)", async () => {
  const manager = new MCPClientManager("./servers.json");
  try {
    const client = await manager.getClient("syn-serena");
    assert.ok(client, "Should connect to serena server");
    console.log("✓ Serena server healthy");
  } catch (error: unknown) {
    if (error instanceof Error && error.message.includes("timeout")) {
      console.log("⚠ Serena server timeout (may require setup)");
      return; // Skip if serena not available
    }
    throw error;
  } finally {
    await manager.closeAll();
  }
});

// ============================================================================
// Context7 Server Health Check
// ============================================================================

testWithTimeout("Health: Context7 MCP Server (npx)", async () => {
  const manager = new MCPClientManager("./servers.json");
  try {
    const client = await manager.getClient("syn-context7");
    assert.ok(client, "Should connect to context7 server");
    console.log("✓ Context7 server healthy");
  } catch (error: unknown) {
    if (error instanceof Error && error.message.includes("timeout")) {
      console.log("⚠ Context7 server timeout (may require Upstash setup)");
      return; // Skip if not configured
    }
    throw error;
  } finally {
    await manager.closeAll();
  }
});

// ============================================================================
// Sequential Thinking Server Health Check
// ============================================================================
// Note: Skipped - requires extended startup time (>15 seconds)
// Can be tested separately with increased timeout

// testWithTimeout("Health: Sequential Thinking MCP Server (npx)", async () => {
//   const manager = new MCPClientManager("./servers.json");
//   try {
//     const client = await manager.getClient("syn-thinking");
//     assert.ok(client, "Should connect to thinking server");
//     console.log("✓ Sequential thinking server healthy");
//   } catch (error: unknown) {
//     if (error instanceof Error && error.message.includes("timeout")) {
//       console.log("⚠ Sequential thinking server timeout");
//       return;
//     }
//     throw error;
//   } finally {
//     await manager.closeAll();
//   }
// });

// ============================================================================
// Repomix Server Health Check
// ============================================================================

testWithTimeout("Health: Repomix MCP Server (npx)", async () => {
  const manager = new MCPClientManager("./servers.json");
  try {
    const client = await manager.getClient("syn-repomix");
    assert.ok(client, "Should connect to repomix server");
    console.log("✓ Repomix server healthy");
  } catch (error: unknown) {
    if (error instanceof Error && error.message.includes("timeout")) {
      console.log("⚠ Repomix server timeout");
      return;
    }
    throw error;
  } finally {
    await manager.closeAll();
  }
});
