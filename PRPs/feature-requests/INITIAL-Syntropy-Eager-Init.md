---
title: "Syntropy Eager Initialization - Critical Servers on Startup"
type: feature-request
status: initial
priority: HIGH
created: 2025-10-20
version: 1
---

# Syntropy Eager Initialization - Critical Servers on Startup

## Problem Statement

**Current Behavior (Lazy Init)**:
- Servers initialized on first tool call (`getClient()`)
- First call has startup latency (process spawn + connection)
- User sees delay on first operation
- Can mask connection issues until tool is actually used

**Issues**:
- ❌ Poor UX: First operation slower than expected
- ❌ Silent failures: Server misconfiguration not detected until first call
- ❌ Unpredictable performance: Cold start on first use

## Proposed Solution

**Eager Initialization on Syntropy Startup**:
- Initialize critical servers immediately when `MCPClientManager` created
- Non-blocking: Use `Promise.all()` to initialize in parallel
- Fail-fast: Report connection issues at startup, not during tool use
- Only initialize essential servers (reduce overhead)

## Configuration-Driven Approach

### servers.json Schema Update

Add `lazy` parameter (boolean, default: true) to each server configuration:

```json
{
  "servers": {
    "syn-serena": {
      "command": "uvx",
      "args": ["serena", "--stdio"],
      "env": { "SOME_VAR": "value" },
      "lazy": false  // Eager: initialize on startup
    },
    "syn-filesystem": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-filesystem", "."],
      "env": {},
      "lazy": false  // Eager: initialize on startup
    },
    "syn-git": {
      "command": "uvx",
      "args": ["mcp-git-server"],
      "env": {},
      "lazy": false  // Eager: initialize on startup
    },
    "syn-thinking": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-sequential-thinking"],
      "env": {},
      "lazy": false  // Eager: initialize on startup
    },
    "syn-linear": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-linear"],
      "env": { "LINEAR_API_KEY": "..." },
      "lazy": false  // Eager: initialize on startup
    },
    "syn-context7": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-context7"],
      "env": {},
      "lazy": true  // (default) Lazy: initialize on demand
    },
    "syn-repomix": {
      "command": "npx",
      "args": ["repomix-mcp"],
      "env": {},
      "lazy": true  // (default) Lazy: rarely used
    },
    "syn-github": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "..." },
      "lazy": true  // (default) Lazy: external API
    },
    "syn-perplexity": {
      "command": "npx",
      "args": ["@modelcontextprotocol/server-perplexity"],
      "env": { "PERPLEXITY_API_KEY": "..." },
      "lazy": true  // (default) Lazy: external API
    }
  }
}
```

### Why Configuration-Driven?

✅ **Flexible**: Change eager/lazy without code changes
✅ **Future-Proof**: Easy to adjust as usage patterns evolve
✅ **Per-Deployment**: Different settings for dev/prod
✅ **Discoverable**: Self-documenting via JSON config
✅ **Auditable**: Track which servers are critical

## Design

### Health Check Pattern

Before marking a server as initialized, verify it's actually running and responding:

```typescript
/**
 * Health check: Call a simple tool to verify server is responding.
 * Each server has a lightweight introspection tool.
 */
private async healthCheckServer(serverName: string, client: Client): Promise<boolean> {
  try {
    // Call ListTools - lightweight introspection available on all MCP servers
    const tools = await client.request(
      { method: "tools/list" },
      ListToolsResultSchema
    );

    // Server is healthy if it responds with tools list
    logger.info(`✅ Health check passed for ${serverName}: ${tools.tools.length} tools available`);
    return true;
  } catch (error) {
    logger.warn(
      `❌ Health check failed for ${serverName}: ${error}\n` +
      `🔧 Troubleshooting: Server started but not responding to requests`
    );
    return false;
  }
}
```

### Changes to MCPClientManager

```typescript
interface ServerConfig {
  command: string;
  args: string[];
  env: Record<string, string>;
  lazy?: boolean;  // NEW: default true (lazy initialization)
}

class MCPClientManager {
  private eagerInitPromise?: Promise<void>;

  constructor(serversConfigPath: string = "./servers.json") {
    this.serversConfigPath = serversConfigPath;
    this.loadServerConfigs();

    // Automatically start eager initialization based on server config
    // No eagerInit parameter - determined by servers.json `lazy: false`
    this.eagerInitPromise = this.initializeEagerServersWithHealthCheck();
  }

  /**
   * Wait for eager servers to be fully initialized and healthy.
   * Call this to ensure all critical servers (lazy: false) are ready before proceeding.
   */
  public async waitForEagerInit(): Promise<void> {
    if (this.eagerInitPromise) {
      await this.eagerInitPromise;
    }
  }

  private async initializeEagerServersWithHealthCheck(): Promise<void> {
    // Identify servers configured with lazy: false
    const eagerServers = Array.from(this.serverPools.entries())
      .filter(([_, pool]) => pool.config.lazy === false)
      .map(([serverName, _]) => serverName);

    logger.info(`🚀 Starting eager initialization of ${eagerServers.length} critical servers...`);
    const startTime = Date.now();

    // Phase 1: Initialize all servers in parallel (spawn processes)
    const initResults = await Promise.allSettled(
      eagerServers.map(serverName => this.getClient(serverName))
    );

    // Phase 2: Health check each server (verify responding)
    const healthCheckResults = await Promise.allSettled(
      initResults.map(async (result, index) => {
        if (result.status === "rejected") {
          throw new Error(`Failed to connect: ${result.reason}`);
        }
        // result.value is the Client
        return this.healthCheckServer(eagerServers[index], result.value);
      })
    );

    // Phase 3: Report results
    let successCount = 0;
    let failureCount = 0;

    healthCheckResults.forEach((result, index) => {
      if (result.status === "fulfilled" && result.value) {
        logger.info(`✅ ${eagerServers[index]} - Ready`);
        successCount++;
      } else {
        logger.warn(
          `⚠️ ${eagerServers[index]} - Failed health check\n` +
          `🔧 Troubleshooting: Check server logs and configuration`
        );
        failureCount++;
      }
    });

    const duration = Date.now() - startTime;
    logger.info(
      `🎯 Eager init complete in ${duration}ms: ` +
      `${successCount}/${eagerServers.length} servers healthy`
    );

    if (failureCount > 0) {
      logger.warn(
        `⚠️ ${failureCount} critical server(s) failed initialization\n` +
        `🔧 Some features may not work - check configuration`
      );
    }
  }
}
```

### Initialization in index.ts

**Option 1: Fire-and-Forget (Non-blocking)**
```typescript
// Configuration-driven: servers.json determines lazy/eager behavior
const clientManager = new MCPClientManager("./servers.json");

// MCP server starts immediately
// Eager servers (lazy: false) initialize in parallel in background
// Tools available once servers ready (no startup latency)
server.connect(transport);
```

**Option 2: Wait for Ready (Blocking - Recommended)**
```typescript
// Create manager - automatically starts eager init based on servers.json
const clientManager = new MCPClientManager("./servers.json");

// Wait for all eager servers (lazy: false) to be healthy before starting
try {
  await clientManager.waitForEagerInit();
  console.log("✅ All eager servers ready - MCP server starting");

  // All eager tools immediately available
  server.connect(transport);
} catch (error) {
  console.error(
    "❌ Some eager servers failed health check\n" +
    "🔧 Check servers.json `lazy` settings and server logs"
  );
  // Decision: retry, continue anyway, or abort
}
```

**Option 3: With 9-Second Timeout (Safe Blocking - Recommended for Prod)**
```typescript
const clientManager = new MCPClientManager("./servers.json");

// Wait with 9s timeout - allows adequate startup time, prevents hanging
try {
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error("Startup timeout (9s)")), 9000)
  );

  await Promise.race([
    clientManager.waitForEagerInit(),
    timeoutPromise
  ]);

  console.log("✅ All eager servers ready in time");
} catch (error) {
  console.warn(
    `⚠️ Eager init timeout (${error.message})\n` +
    `🔧 Check servers.json - adjust lazy settings or increase timeout`
  );
}

// MCP server starts regardless - lazy servers will init on demand
server.connect(transport);
```

### Configuration-Driven Benefits

**Zero code changes to adjust eager/lazy behavior:**

```bash
# Before: syn-linear is eager, syn-context7 is lazy
# To swap them - just edit servers.json:

{
  "syn-linear": { "lazy": true },  # Changed from false
  "syn-context7": { "lazy": false }  # Changed from true
}

# Restart Syntropy - new config applies automatically
```

## Benefits

✅ **Zero Cold-Start**: No latency on first tool use (servers pre-warmed)
✅ **Verified Ready**: Health checks confirm servers are actually responding
✅ **Fail-Fast**: Configuration/connection issues detected at startup, not on tool call
✅ **Predictable Performance**: All subsequent calls fast (~50ms vs 200-500ms cold start)
✅ **Graceful Degradation**: Non-critical servers lazy-load; critical ones healthy on startup
✅ **Parallel Health Checks**: All 5 servers checked concurrently (~1.8-2.2s total)
✅ **Flexible Options**: Non-blocking, blocking, or timeout-protected initialization strategies

## Tradeoffs

| Aspect | Current (Lazy) | With Eager + Health | Decision |
|--------|---|---|---|
| Startup latency | 0ms | ~1.8-2.2s | Accept (justified by UX) |
| First tool call | Slow (200-500ms) | Fast (~50ms) | ✅ Better overall UX |
| Server health verified | No (until first use) | Yes (health check) | ✅ More reliable |
| Failed config | On first tool call | On startup | ✅ Better visibility |
| Tools immediately ready | No (cold start wait) | Yes (pre-warmed) | ✅ Instant response |
| Graceful degradation | Basic (lazy) | Advanced (fallback) | ✅ Multiple strategies |
| Resource usage | Minimal startup | Predictable peak | ✅ Acceptable tradeoff |

## Effort Estimate

- **Implementation**: 2-3 hours
  - Modify `MCPClientManager` constructor: 30 min
  - Add `initializeEagerServers()` method: 30 min
  - Update `index.ts` initialization: 15 min
  - Add error handling + logging: 30 min
  - Tests: 30 min

- **Testing**: 1 hour
  - Startup latency measurement
  - Error handling verification
  - Integration tests

**Total**: 3-4 hours

## Success Criteria

✅ Configuration-driven: `lazy: false` determines eager servers (from servers.json)
✅ All eager servers (lazy: false) initialize on startup
✅ Health checks verify servers responding (tools/list introspection)
✅ Parallel initialization + health checks complete in <9 seconds
✅ Failed eager server initialization reported but doesn't block startup (graceful degradation)
✅ Non-eager servers still lazy-load on demand (lazy: true or default)
✅ First tool call has no perceptible startup latency for eager servers (<100ms)
✅ Configuration errors reported immediately at startup (not on first use)
✅ `waitForEagerInit()` async/await API works correctly
✅ Three initialization strategies (fire-and-forget, blocking, 9s timeout) all functional
✅ Health check failures logged with troubleshooting guidance
✅ Zero code changes needed to adjust eager/lazy behavior (just edit servers.json)

## Implementation Plan

1. **Phase 1**: Modify `MCPClientManager` (1-1.5 hours)
2. **Phase 2**: Update startup flow in `index.ts` (30 min)
3. **Phase 3**: Add tests & verify (1-1.5 hours)
4. **Phase 4**: Performance benchmarking (30 min)

## References

- `syntropy-mcp/src/client-manager.ts` - Current lazy init implementation
- `syntropy-mcp/src/index.ts` - Server initialization entry point
- `syntropy-mcp/servers.json` - Server configuration

---

**Next Step**: Generate full PRP with comprehensive implementation details and test scenarios.
