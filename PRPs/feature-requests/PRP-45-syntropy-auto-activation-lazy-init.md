---
prp_id: PRP-45
feature_name: Syntropy MCP Auto-Activation and Lazy Server Initialization
status: pending
created: 2025-11-16T00:00:00Z
updated: 2025-11-16T00:00:00Z
complexity: medium
estimated_hours: 3-4
dependencies: syntropy-mcp, serena-mcp
issue: BLA-58
---

# PRP-45: Syntropy MCP Auto-Activation and Lazy Server Initialization

## 1. TL;DR

**Objective**: Eliminate manual Serena activation and improve syntropy-mcp startup performance

**What**:
- Auto-activate Serena on session start (workspace root → git root → cwd detection)
- Lazy-load filesystem and git servers (initialize on first use only)

**Why**:
- Users currently must manually call `serena_activate_project()` every session
- All 9 servers initialize on startup (even rarely-used filesystem/git servers)
- Poor UX: Serena tools fail until manual activation

**Effort**: 3-4 hours

**Dependencies**:
- syntropy-mcp server (TypeScript implementation)
- serena-mcp (activate_project tool)

## 2. Context

### Background

**Current Workflow**:
```
Claude Code starts
  ├─> Syntropy connects (9 servers)
  ├─> User must manually: serena_activate_project("/path")
  └─> Only then: Serena tools work
```

**Issues**:
- Manual activation step every session
- All 9 servers connect on startup (unnecessary for filesystem/git)
- Serena tools fail until activated

**Desired Workflow**:
```
Claude Code starts
  ├─> Syntropy connects (7 core servers)
  ├─> Auto-activate Serena (async)
  ├─> Lazy-load filesystem/git on first use
  └─> Serena tools immediately available
```

### Constraints and Considerations

**Multi-Project Handling**:
- Workspace with multiple projects → use workspace root (VSCODE_WORKSPACE_ROOT)
- Single project → git root or cwd
- Serena indexes entire workspace in multi-project scenarios

**Performance Impact**:
- Lazy-loading saves ~6ms + connection overhead
- Auto-activation runs async (doesn't block session start)
- Serena indexing takes 5-30s for large projects (runs in background)

**Backward Compatibility**:
- Manual activation still works (fallback if auto-activation fails)
- Opt-out via config: `serena.autoActivate: false`
- No breaking changes to MCP protocol

### Documentation References

- MCP Protocol Specification: Session lifecycle events
- Syntropy-mcp architecture: Server connection patterns
- Serena MCP: activate_project tool documentation

## 3. Implementation Steps

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

**3.1 Write Tests**
- Unit tests for `detectProjectRoot()` (git, workspace, cwd fallback)
- Unit tests for `getLazyServer()` caching
- Integration tests for auto-activation
- Integration tests for lazy-loading

**3.2 Manual Testing**
- Test git repos, non-git projects, monorepos
- Test workspace multi-project detection
- Test opt-out configuration
- Measure startup time improvement

## 4. Validation Gates

### Gate 1: Auto-Activation Works

**Command**:
```bash
# Start Claude Code, check Serena activated
mcp__syntropy__healthcheck(detailed=true) | grep serena
# Expected: serena shows as healthy with project path
```

**Success Criteria**:
- Serena automatically activates on session start
- No manual `serena_activate_project()` call needed
- Serena tools work in first interaction

### Gate 2: Lazy Loading Works

**Command**:
```bash
# Check filesystem server not loaded on startup
mcp__syntropy__healthcheck(detailed=true) | grep filesystem
# Expected: filesystem shows "lazy (not loaded)"

# Call filesystem tool
mcp__syntropy__filesystem_read_file(path="/tmp/test.txt")

# Check filesystem now loaded
mcp__syntropy__healthcheck(detailed=true) | grep filesystem
# Expected: filesystem shows "healthy"
```

**Success Criteria**:
- Filesystem and git servers don't load on startup
- Lazy servers load on first tool call
- Subsequent calls use cached client

### Gate 3: Performance Improvement

**Command**:
```bash
# Measure startup time before/after
time claude-code --version  # Proxy for session start
```

**Success Criteria**:
- Startup time reduced by ≥5ms
- No regressions in session initialization
- Memory usage not increased

### Gate 4: Graceful Degradation

**Command**:
```bash
# Test with Serena unavailable
# Temporarily disable Serena, start Claude Code
# Session should start normally with warning
```

**Success Criteria**:
- Session starts even if Serena unavailable
- Clear warning logged (not error)
- Manual activation still works

## 5. Testing Strategy

### Test Framework

**Unit Tests**: Jest/Mocha (TypeScript)
**Integration Tests**: Manual testing + MCP protocol tests

### Test Command

```bash
cd syntropy-mcp
npm test
```

### Test Coverage

**Unit Tests** (15-20 tests):
- `detectProjectRoot()` with git repos, workspace, cwd
- `findGitRoot()` edge cases (nested dirs, no git)
- `getLazyServer()` caching logic
- Configuration loading (opt-out)

**Integration Tests** (5-10 tests):
- Full session start with auto-activation
- Lazy server first-call initialization
- Error scenarios (server unavailable, git not found)
- Multi-project workspace detection

### Edge Cases and Error Handling

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

## 6. Rollout Plan

### Phase 1: Development

**Duration**: 3-4 hours

**Tasks**:
1. Implement auto-activation (Phase 1 from Implementation Steps)
2. Implement lazy loading (Phase 2 from Implementation Steps)
3. Write unit tests (15-20 tests)
4. Write integration tests (5-10 tests)

**Deliverables**:
- Updated syntropy-mcp code (src/index.ts, config.ts, health.ts)
- Test suite passing
- Documentation updated

### Phase 2: Review and Testing

**Duration**: 1 hour

**Tasks**:
1. Code review (self-review against PRP checklist)
2. Manual testing (git repos, workspaces, edge cases)
3. Performance measurement (startup time before/after)
4. Validation gates verification (all 4 gates pass)

**Deliverables**:
- All validation gates passing
- Performance metrics documented
- Edge cases tested

### Phase 3: Deployment

**Duration**: 30 minutes

**Tasks**:
1. Bump syntropy-mcp version (0.1.3 → 0.1.4)
2. Build and publish npm package
3. Update healthcheck cache
4. Reconnect MCP (`/mcp` command)

**Verification**:
```bash
# Verify version
mcp__syntropy__healthcheck() | grep version
# Expected: 0.1.4

# Verify auto-activation
# Start new session, Serena should auto-activate

# Verify lazy loading
mcp__syntropy__healthcheck(detailed=true) | grep filesystem
# Expected: "lazy (not loaded)"
```

**Rollback Plan**:
- If issues found: Revert to 0.1.3
- Manual activation still works as fallback
- No data loss or breaking changes

---

## Files to Modify

**syntropy-mcp/src/index.ts** (~100 lines changed)
- Add session start hook
- Project detection utilities
- Lazy server initialization
- Tool call routing updates

**syntropy-mcp/src/config.ts** (new file, ~50 lines)
- Configuration loading from ~/.claude/settings.json
- Default values

**syntropy-mcp/src/health.ts** (~30 lines changed)
- Lazy server status handling
- Health check output updates

**~/.claude/settings.json** (optional, user config)
- Opt-out configuration support

---

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
