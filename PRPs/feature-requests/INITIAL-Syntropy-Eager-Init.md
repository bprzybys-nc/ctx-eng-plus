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

### Changes to MCPClientManager

```typescript
class MCPClientManager {
  constructor(serversConfigPath: string = "./servers.json", eagerInit: boolean = true) {
    this.serversConfigPath = serversConfigPath;
    this.loadServerConfigs();

    if (eagerInit) {
      this.initializeEagerServers();
    }
  }

  private async initializeEagerServers(): Promise<void> {
    const eagerServers = [
      "syn-serena",      // Code analysis
      "syn-filesystem",  // File operations
      "syn-git",         // Version control
      "syn-thinking",    // Reasoning
      "syn-linear"       // Issue tracking
    ];

    const results = await Promise.allSettled(
      eagerServers.map(serverName => this.getClient(serverName))
    );

    results.forEach((result, index) => {
      if (result.status === "rejected") {
        logger.warn(
          `⚠️ Failed to initialize ${eagerServers[index]}: ${result.reason}\n` +
          `🔧 Troubleshooting: Check server configuration and credentials`
        );
      } else {
        logger.info(`✅ Initialized ${eagerServers[index]}`);
      }
    });
  }
}
```

### Initialization in index.ts

```typescript
// At startup
const clientManager = new MCPClientManager(
  "./servers.json",
  true  // Enable eager initialization
);

// Wait for startup (in main or during server init)
await clientManager.waitForEagerInit?.();  // Optional explicit wait
```

## Benefits

✅ **Better UX**: No startup latency on first tool use
✅ **Fail-Fast**: Catch misconfiguration immediately
✅ **Predictable Performance**: Subsequent calls fast
✅ **Graceful Degradation**: Non-critical servers can fail silently
✅ **Parallel Init**: All 4 servers initialize concurrently (~500ms total vs 1400ms sequential)

## Tradeoffs

| Aspect | Current (Lazy) | With Eager | Decision |
|--------|---|---|---|
| Startup latency | 0ms | ~1.8s total (parallel) | Accept (justified) |
| First tool call | Slow (~200-500ms) | Fast (~50ms) | Better overall UX |
| Failed config | Discovered on use | On startup | Better visibility |
| Resource usage | Minimal until needed | Predictable | Acceptable |
| Critical servers | 5 core servers | Initialize all 5 | Efficient parallelization |
| Non-critical | Never init if unused | 4 servers lazy | Minimal overhead |

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

✅ All 4 critical servers initialize on startup
✅ Parallel initialization completes in <1 second
✅ Failed server initialization doesn't block startup
✅ Non-critical servers still lazy-load on demand
✅ First tool call has no perceptible startup latency
✅ Configuration errors reported immediately (not on first use)

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
