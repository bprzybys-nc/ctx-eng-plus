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

## Implementation Scope

### Critical Servers (Initialize Always)

1. **Serena** (`syn-serena`)
   - Core code analysis capability
   - Always needed by context engineering
   - 🔧 Python binary startup: ~500ms

2. **Filesystem** (`syn-filesystem`)
   - File operations required for context sync
   - Foundation for other operations
   - 🔧 Node.js startup: ~200ms

3. **Git** (`syn-git`)
   - Version control operations
   - Required for drift detection
   - 🔧 Python binary startup: ~400ms

4. **Thinking** (`syn-thinking`)
   - Sequential reasoning for complex tasks
   - Often used in analysis workflows
   - 🔧 Node.js startup: ~300ms

5. **Linear** (`syn-linear`)
   - Issue tracking integration
   - Used in PRP generation workflow
   - 🔧 Node.js startup with API: ~400ms

### Non-Critical Servers (Keep Lazy)

- **Context7**: Documentation lookup, can defer (~300ms)
- **Repomix**: Codebase packaging, rarely used (~200ms)
- **GitHub**: External API, high overhead (~400ms)
- **Perplexity**: External API, high overhead (~400ms)

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
class MCPClientManager {
  private eagerInitPromise?: Promise<void>;

  constructor(serversConfigPath: string = "./servers.json", eagerInit: boolean = true) {
    this.serversConfigPath = serversConfigPath;
    this.loadServerConfigs();

    if (eagerInit) {
      // Start initialization but don't await - callers can await if needed
      this.eagerInitPromise = this.initializeEagerServersWithHealthCheck();
    }
  }

  /**
   * Wait for eager servers to be fully initialized and healthy.
   * Call this to ensure all critical servers are ready before proceeding.
   */
  public async waitForEagerInit(): Promise<void> {
    if (this.eagerInitPromise) {
      await this.eagerInitPromise;
    }
  }

  private async initializeEagerServersWithHealthCheck(): Promise<void> {
    const eagerServers = [
      "syn-serena",      // Code analysis
      "syn-filesystem",  // File operations
      "syn-git",         // Version control
      "syn-thinking",    // Reasoning
      "syn-linear"       // Issue tracking
    ];

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
// Start initialization in background
const clientManager = new MCPClientManager(
  "./servers.json",
  true  // Enable eager initialization (spawns in background)
);

// Server continues immediately - tools will work after servers start
// Non-critical for immediate startup, but first tool call will still wait
```

**Option 2: Wait for Ready (Blocking - Recommended)**
```typescript
// Explicit initialization with health checks
const clientManager = new MCPClientManager(
  "./servers.json",
  true  // Enable eager initialization
);

// Wait for all critical servers to be healthy before starting MCP server
try {
  await clientManager.waitForEagerInit();
  console.log("✅ All critical servers ready - MCP server starting");

  // Now start MCP server - all tools immediately available
  server.connect(transport);
} catch (error) {
  console.error(
    "❌ Eager init failed (non-blocking)\n" +
    "🔧 Continue with degraded functionality or abort?"
  );
  // Decision: retry, continue anyway, or abort
}
```

**Option 3: With Timeout (Safe Blocking)**
```typescript
const clientManager = new MCPClientManager(
  "./servers.json",
  true  // Enable eager initialization
);

// Wait with timeout - don't block forever if servers slow to start
try {
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error("Startup timeout")), 10000)
  );

  await Promise.race([
    clientManager.waitForEagerInit(),
    timeoutPromise
  ]);

  console.log("✅ Servers ready");
} catch (error) {
  console.warn(
    `⚠️ Eager init timeout (${error.message})\n` +
    `🔧 Continuing with lazy initialization for unavailable servers`
  );
}

// MCP server starts regardless - degraded start is acceptable
server.connect(transport);
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

✅ All 5 critical servers initialize on startup
✅ Health checks verify servers are responding (tools/list introspection)
✅ Parallel initialization + health checks complete in <2.5 seconds
✅ Failed server initialization reported but doesn't block startup (graceful degradation)
✅ Non-critical servers still lazy-load on demand
✅ First tool call has no perceptible startup latency (<100ms)
✅ Configuration errors reported immediately at startup (not on first use)
✅ `waitForEagerInit()` async/await API works correctly
✅ Three initialization strategies (fire-and-forget, blocking, timeout) all functional
✅ Health check failures logged with troubleshooting guidance

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
