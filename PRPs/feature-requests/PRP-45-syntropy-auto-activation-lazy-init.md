---
prp_id: PRP-45
title: Syntropy MCP Auto-Activation and Lazy Server Initialization
status: initial
created: 2025-11-16
estimated_hours: 3-4
complexity: medium
priority: medium
---

# PRP-45: Syntropy MCP Auto-Activation and Lazy Server Initialization

## Overview

Enhance syntropy-mcp startup performance and UX by:
1. **Auto-activating Serena** on session start (eliminates manual activation step)
2. **Lazy-loading filesystem and git servers** (only initialize when tools are called)

## Problem Statement

**Current UX Issues**:
1. Users must manually call `serena_activate_project()` after every session start
2. All 9 MCP servers initialize on startup (even rarely-used ones)
3. Startup time includes unnecessary server connections
4. Serena tools fail until project is activated

**Current Workflow**:
```
Claude Code starts
  ├─> Syntropy connects (9 servers)
  ├─> User must manually: serena_activate_project("/path")
  └─> Only then: Serena tools work
```

**Desired Workflow**:
```
Claude Code starts
  ├─> Syntropy connects (7 core servers)
  ├─> Auto-activate Serena (async)
  ├─> Lazy-load filesystem/git on first use
  └─> Serena tools immediately available
```

## Proposed Solution

### Feature 1: Serena Auto-Activation

**Trigger Event**: Session start (after core servers connected)

**Implementation**:
```typescript
// syntropy-mcp/src/index.ts
async function onSessionStart() {
  try {
    if (!serenaClient) return; // Skip if Serena not available

    // Auto-detect project root
    const projectRoot = await detectProjectRoot();

    // Activate Serena asynchronously
    await serenaClient.callTool('activate_project', {
      project: projectRoot
    });

    console.log(`✓ Serena activated: ${projectRoot}`);
  } catch (error) {
    console.warn(`⚠️ Serena auto-activation failed: ${error.message}`);
    // Don't throw - session continues
  }
}

async function detectProjectRoot(): Promise<string> {
  // Priority order:
  // 1. Workspace root (if multiple projects open)
  // 2. Git root (most projects)
  // 3. process.cwd() (fallback)

  // If VS Code workspace with multiple folders, use workspace root
  if (process.env.VSCODE_WORKSPACE_ROOT) {
    return process.env.VSCODE_WORKSPACE_ROOT;
  }

  const gitRoot = await findGitRoot(process.cwd());
  return gitRoot || process.cwd();
}
```

**Configuration** (optional opt-out):
```json
// ~/.claude/settings.json
{
  "serena": {
    "autoActivate": true  // default
  }
}
```

### Feature 2: Lazy Server Initialization

**Servers to Lazy-Load**:
- `filesystem` (3ms startup) - Mostly denied, native tools preferred
- `git` (3ms startup) - Mostly denied, native Bash(git:*) preferred

**Core Servers** (initialize on startup):
- `serena` - Auto-activated, frequently used
- `linear` - Project management integration
- `context7` - Library documentation
- `thinking` - Complex reasoning
- `repomix` - Package management
- `github` - Repository operations
- `perplexity` - Web search

**Implementation**:
```typescript
// syntropy-mcp/src/index.ts
const lazyServers = new Map<string, Promise<MCPClient>>();
const coreServers = ['serena', 'linear', 'context7', 'thinking', 'repomix', 'github', 'perplexity'];
const lazyServerNames = ['filesystem', 'git'];

async function initializeCoreServers() {
  for (const name of coreServers) {
    await connectToServer(name);
  }
}

async function getLazyServer(name: string): Promise<MCPClient> {
  if (!lazyServers.has(name)) {
    console.log(`Lazy-loading ${name} server...`);
    lazyServers.set(name, connectToServer(name));
  }
  return lazyServers.get(name)!;
}

// On tool call routing
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const [serverName, toolName] = parseToolName(request.params.name);

  let client;
  if (lazyServerNames.includes(serverName)) {
    client = await getLazyServer(serverName); // Lazy-load on first use
  } else {
    client = getConnectedServer(serverName); // Already connected
  }

  return client.callTool(toolName, request.params.arguments);
});
```

## Benefits

### UX Improvements
- ✅ No manual Serena activation needed
- ✅ Serena tools work immediately after session start
- ✅ Faster startup (lazy-load low-priority servers)
- ✅ Servers only loaded when actually used

### Performance Metrics
- **Startup time**: Reduced by ~6ms + connection overhead for lazy servers
- **Memory footprint**: Lower (filesystem/git only loaded if used)
- **Session readiness**: Serena available without user action

### Developer Experience
- No breaking changes to MCP protocol
- Backward compatible (config opt-out)
- Graceful degradation (errors don't block session)
- Clear logging for debugging

## Implementation Plan

### Phase 1: Serena Auto-Activation (2 hours)

**1.1 Implement Project Detection**
- Add `findGitRoot()` utility
- Add `detectProjectRoot()` with fallback chain
- Handle edge cases (monorepos, non-git projects)

**1.2 Add Session Start Hook**
- Call after core servers connected
- Async activation (don't block session)
- Error handling and logging

**1.3 Add Configuration Support**
- Read settings from ~/.claude/settings.json
- Support opt-out via `serena.autoActivate: false`
- Default to enabled

### Phase 2: Lazy Server Initialization (1-2 hours)

**2.1 Separate Core vs Lazy Servers**
- Define core server list (7 servers)
- Define lazy server list (filesystem, git)
- Update initialization logic

**2.2 Implement Lazy Loading**
- Add `getLazyServer()` function
- Modify tool call routing
- Cache lazy-loaded servers

**2.3 Update Health Check**
- Mark lazy servers as "not loaded" vs "unhealthy"
- Show lazy server status separately
- Update healthcheck output

### Phase 3: Testing and Validation (1 hour)

**3.1 Test Auto-Activation**
- Test git repos (standard case)
- Test non-git projects (fallback)
- Test monorepos (edge case)
- Test opt-out configuration

**3.2 Test Lazy Loading**
- Verify lazy servers don't load on startup
- Verify lazy servers load on first tool call
- Verify subsequent calls use cached client
- Verify health check shows correct status

**3.3 Integration Testing**
- Test full session lifecycle
- Test error scenarios (Serena unavailable, git detection fails)
- Test performance impact (measure startup time)

## Edge Cases and Error Handling

### Auto-Activation Edge Cases

1. **Serena not connected**
   - Skip activation silently
   - Log debug message
   - Don't block session

2. **Project detection fails**
   - Fall back to process.cwd()
   - Log warning
   - Continue with best-effort path

3. **Multiple workspace folders (VS Code workspace)**
   - Use workspace root (process.env.VSCODE_WORKSPACE_ROOT)
   - Serena will index entire workspace
   - Single activation covers all projects

4. **Activation fails (network, permissions)**
   - Log warning with error details
   - Session continues normally
   - User can manually activate if needed

### Lazy Loading Edge Cases

1. **Lazy server connection fails**
   - Cache error, don't retry on every call
   - Return clear error to user
   - Log troubleshooting info

2. **Concurrent first calls**
   - Use Promise to handle race condition
   - Only initialize once
   - Subsequent calls wait for same Promise

3. **Health check timing**
   - Don't initialize lazy servers for health check
   - Mark as "lazy (not loaded)" in status
   - Only check if already loaded

## Files to Modify

### syntropy-mcp Repository

**src/index.ts** (main changes)
- Add `onSessionStart()` hook
- Add `detectProjectRoot()` utility
- Add `findGitRoot()` utility
- Separate core vs lazy server initialization
- Add `getLazyServer()` function
- Update tool call routing

**src/config.ts** (new file)
- Read settings from ~/.claude/settings.json
- Support serena.autoActivate flag
- Provide configuration defaults

**src/health.ts** (update)
- Handle lazy server status
- Distinguish "not loaded" vs "unhealthy"
- Update healthcheck output format

### Configuration Files

**~/.claude/settings.json** (user config, optional)
```json
{
  "serena": {
    "autoActivate": true
  }
}
```

## Testing Strategy

### Unit Tests
- ✅ Test `detectProjectRoot()` with various project structures
- ✅ Test `findGitRoot()` with nested directories
- ✅ Test lazy server caching logic
- ✅ Test configuration loading

### Integration Tests
- ✅ Test full session start with auto-activation
- ✅ Test lazy server first-call initialization
- ✅ Test error scenarios (server unavailable, git not found)
- ✅ Test opt-out configuration

### Manual Testing
- ✅ Start Claude Code, verify Serena auto-activates
- ✅ Call filesystem tool, verify lazy-load
- ✅ Run healthcheck, verify status display
- ✅ Test with/without git repo
- ✅ Test opt-out configuration

## Risks and Mitigations

### Risk 1: Auto-activation fails for some projects
**Mitigation**: Graceful degradation, clear error messages, manual activation still works

### Risk 2: Lazy loading breaks existing workflows
**Mitigation**: Only lazy-load denied tools (filesystem, git), no workflow impact expected

### Risk 3: Performance regression
**Mitigation**: Measure startup time before/after, async activation doesn't block session

### Risk 4: Configuration compatibility
**Mitigation**: Use standard settings.json location, default=enabled requires no config

## Success Metrics

### UX Metrics
- [ ] Users never need to call `serena_activate_project()` manually
- [ ] Serena tools work in first interaction after session start
- [ ] No user-reported issues with auto-activation

### Performance Metrics
- [ ] Startup time reduced by ≥5ms (lazy server savings)
- [ ] Serena activation completes within 2 seconds (async)
- [ ] No increase in memory usage for typical sessions

### Code Quality Metrics
- [ ] All tests pass
- [ ] No regressions in existing functionality
- [ ] Clear error messages and logging
- [ ] Documentation updated

## Follow-up Work

### Potential Enhancements
1. **Smart project detection** - Use package.json, pyproject.toml for project boundaries
2. **Multi-project support** - Activate multiple Serena instances for monorepos
3. **More lazy servers** - Evaluate github, perplexity for lazy-loading
4. **Activation progress** - Show Serena indexing progress notification
5. **Configuration UI** - Add settings panel for auto-activation config

### Related PRPs
- PRP-44: Init-project bug fixes (deployed via repomix packages)
- Future: Serena performance optimizations (indexing speed)

## Notes

**Why lazy-load filesystem and git specifically?**
- Both mostly denied in CE framework (94% of tools denied)
- Native Claude Code tools preferred (Read/Write/Edit for filesystem, Bash(git:*) for git)
- Rarely used in typical CE workflows
- Easy wins for startup performance

**Why auto-activate Serena?**
- Most frequently used MCP server in CE framework
- Tools fail without activation (bad UX)
- Project path is deterministic (git root or cwd)
- No security/privacy concerns (local code analysis)

**Backward compatibility**:
- No breaking changes to MCP protocol
- Opt-out available via config
- Manual activation still works if auto-activation fails
- Lazy servers load transparently on first use
