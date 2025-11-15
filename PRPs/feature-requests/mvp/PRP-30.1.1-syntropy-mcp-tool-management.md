---
prp_id: 30.1.1
feature_name: Syntropy MCP - Tool Management Commands
status: pending
created: 2025-10-30T00:00:00Z
updated: 2025-10-30T00:00:00Z
complexity: medium
estimated_hours: 2.5
dependencies: []
batch_id: 30
stage: stage-1-sequential
execution_order: 1
merge_order: 1
conflict_potential: NONE
worktree_path: ../ctx-eng-plus-prp-30-1-1
branch_name: prp-30-1-1-syntropy-mcp-tool-management
issue: BLA-46
---

# Syntropy MCP - Tool Management Commands

## 1. TL;DR

**Objective**: Implement dynamic tool management commands in Syntropy MCP server to enable/disable tools without restart

**What**: Add `enable_tools` and `list_all_tools` commands with persistent state management in `~/.syntropy/tool-state.json`

**Why**: Current tool filtering requires MCP server restart. Dynamic management allows real-time tool control for different contexts (e.g., enable 10 tools for quick tasks, enable all 87 for deep analysis)

**Effort**: 2.5 hours (medium complexity)

**Dependencies**: None (standalone feature in syntropy-mcp repository)

**Plan Context**: Part of Dynamic Tool Management for Syntropy MCP initiative (Batch 30)

## 2. Context

### Background

The Syntropy MCP server currently aggregates tools from multiple downstream MCP servers (Serena, Linear, Context7, GitHub, etc.). Tool filtering is static - configured at startup via deny/allow lists in `.claude/settings.local.json`. Changing the tool set requires restarting the MCP server.

This PRP implements dynamic tool management to:
1. Enable/disable tools at runtime without restart
2. Persist tool state across sessions
3. Provide visibility into all available tools and their status

### Current State

**syntropy-mcp/src/index.ts**:
- Handles `tools/list` request by aggregating tools from connected servers
- No state management for enabled/disabled tools
- Returns all tools from all servers (filtered only by static deny list)

**Tool Filtering**: Handled by Claude Code's `.claude/settings.local.json`:
```json
{
  "mcpServers": {
    "syntropy": {
      "command": "node",
      "args": ["/path/to/syntropy-mcp/dist/index.js"],
      "deny": ["mcp__syntropy__git_git_status", ...]
    }
  }
}
```

### Target State

**New Commands**:
1. `mcp__syntropy__enable_tools` - Enable/disable specific tools
2. `mcp__syntropy__list_all_tools` - List all aggregated tools with status

**State Persistence**: `~/.syntropy/tool-state.json`:
```json
{
  "enabled": ["mcp__syntropy__serena_find_symbol", ...],
  "disabled": ["mcp__syntropy__github_create_issue", ...]
}
```

**Runtime Behavior**:
- `tools/list` filters by enabled state before returning to client
- State loads on server startup
- State updates persist immediately to disk

### Constraints and Considerations

**Technical Constraints**:
- Must work with existing MCP protocol (no protocol changes)
- State file must be JSON (readable, editable by users)
- Tool names use full MCP format: `mcp__syntropy__<server>_<tool>`

**Design Decisions**:
- State stored in `~/.syntropy/` (user-level, not project-level)
- Default state: All tools enabled (backward compatible)
- `enable_tools` command takes both `enable` and `disable` arrays (atomic update)

**Edge Cases**:
- Nonexistent tool names in enable/disable arrays → Log warning, skip
- State file corrupted → Reset to default (all enabled), log error
- State file missing → Create with default state

**Security**: No sensitive data in state file (only tool names)

### Documentation References

- [MCP Protocol Spec - Tools](https://modelcontextprotocol.io/docs/concepts/tools)
- [TypeScript JSON File I/O](https://nodejs.org/docs/latest/api/fs.html)
- Node.js `fs.promises` for async file operations

## 3. Implementation Steps

### Phase 1: Create ToolStateManager Class (45 min)

**File**: `syntropy-mcp/src/tool-manager.ts` (new file)

**Implementation**:

```typescript
import { promises as fs } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

interface ToolState {
  enabled: string[];
  disabled: string[];
}

export class ToolStateManager {
  private stateFile: string;
  private state: ToolState;

  constructor() {
    this.stateFile = join(homedir(), '.syntropy', 'tool-state.json');
    this.state = { enabled: [], disabled: [] };
  }

  async initialize(): Promise<void> {
    try {
      await fs.mkdir(join(homedir(), '.syntropy'), { recursive: true });
      const data = await fs.readFile(this.stateFile, 'utf-8');
      this.state = JSON.parse(data);
    } catch (error) {
      // File doesn't exist or is corrupted → use default (all enabled)
      console.warn(`Tool state file missing or corrupted, using defaults: ${error}`);
      this.state = { enabled: [], disabled: [] };
      await this.persist();
    }
  }

  async enableTools(toolsToEnable: string[], toolsToDisable: string[]): Promise<void> {
    // Add to enabled set, remove from disabled set
    const enabledSet = new Set(this.state.enabled);
    const disabledSet = new Set(this.state.disabled);

    for (const tool of toolsToEnable) {
      enabledSet.add(tool);
      disabledSet.delete(tool);
    }

    for (const tool of toolsToDisable) {
      disabledSet.add(tool);
      enabledSet.delete(tool);
    }

    this.state.enabled = Array.from(enabledSet);
    this.state.disabled = Array.from(disabledSet);

    await this.persist();
  }

  isEnabled(toolName: string): boolean {
    // If in disabled list → disabled
    if (this.state.disabled.includes(toolName)) {
      return false;
    }
    // If enabled list is empty → all enabled (default)
    // If in enabled list → enabled
    return this.state.enabled.length === 0 || this.state.enabled.includes(toolName);
  }

  getState(): ToolState {
    return { ...this.state };
  }

  private async persist(): Promise<void> {
    try {
      await fs.writeFile(
        this.stateFile,
        JSON.stringify(this.state, null, 2),
        'utf-8'
      );
    } catch (error) {
      console.error(`Failed to persist tool state: ${error}`);
      throw new Error(`Tool state persistence failed: ${error}`);
    }
  }
}
```

**Key Features**:
- Default state: All tools enabled (empty enabled list = wildcard)
- Atomic updates: Both enable and disable in single transaction
- Fast failure: Throws on persist error (no silent corruption)
- Actionable errors: Includes error context in messages

### Phase 2: Add enable_tools Command (30 min)

**File**: `syntropy-mcp/src/index.ts`

**Add to tool definitions**:

```typescript
{
  name: 'mcp__syntropy__enable_tools',
  description: 'Enable or disable specific tools dynamically without restart. Changes persist across sessions.',
  inputSchema: {
    type: 'object',
    properties: {
      enable: {
        type: 'array',
        items: { type: 'string' },
        description: 'Tool names to enable (full MCP format: mcp__syntropy__<server>_<tool>)',
        default: []
      },
      disable: {
        type: 'array',
        items: { type: 'string' },
        description: 'Tool names to disable (full MCP format: mcp__syntropy__<server>_<tool>)',
        default: []
      }
    }
  }
}
```

**Add handler**:

```typescript
import { ToolStateManager } from './tool-manager.js';

// Global state manager instance
const toolStateManager = new ToolStateManager();

// In server initialization
await toolStateManager.initialize();

// In tools/call handler
if (params.name === 'mcp__syntropy__enable_tools') {
  const { enable = [], disable = [] } = params.arguments as {
    enable?: string[];
    disable?: string[];
  };

  await toolStateManager.enableTools(enable, disable);

  const state = toolStateManager.getState();
  return {
    content: [{
      type: 'text',
      text: JSON.stringify({
        success: true,
        message: 'Tool state updated successfully',
        enabled_count: state.enabled.length,
        disabled_count: state.disabled.length,
        state_file: '~/.syntropy/tool-state.json'
      }, null, 2)
    }]
  };
}
```

### Phase 3: Add list_all_tools Command (30 min)

**Add to tool definitions**:

```typescript
{
  name: 'mcp__syntropy__list_all_tools',
  description: 'List all tools from all connected MCP servers with their enabled/disabled status',
  inputSchema: {
    type: 'object',
    properties: {}
  }
}
```

**Add handler**:

```typescript
if (params.name === 'mcp__syntropy__list_all_tools') {
  // Aggregate tools from all servers
  const allTools: Array<{
    name: string;
    description: string;
    server: string;
    status: 'enabled' | 'disabled';
  }> = [];

  for (const [serverName, client] of Object.entries(mcpClients)) {
    try {
      const response = await client.request(
        { method: 'tools/list' },
        ListToolsResultSchema
      );

      for (const tool of response.tools) {
        const toolName = `mcp__syntropy__${serverName}_${tool.name}`;
        allTools.push({
          name: toolName,
          description: tool.description || '',
          server: serverName,
          status: toolStateManager.isEnabled(toolName) ? 'enabled' : 'disabled'
        });
      }
    } catch (error) {
      console.error(`Failed to fetch tools from ${serverName}: ${error}`);
      // Continue with other servers (graceful degradation)
    }
  }

  return {
    content: [{
      type: 'text',
      text: JSON.stringify({
        total_tools: allTools.length,
        enabled_tools: allTools.filter(t => t.status === 'enabled').length,
        disabled_tools: allTools.filter(t => t.status === 'disabled').length,
        tools: allTools
      }, null, 2)
    }]
  };
}
```

### Phase 4: Modify tools/list Handler (15 min)

**File**: `syntropy-mcp/src/index.ts`

**Update existing handler**:

```typescript
// In tools/list handler
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const aggregatedTools: Tool[] = [];

  for (const [serverName, client] of Object.entries(mcpClients)) {
    try {
      const response = await client.request(
        { method: 'tools/list' },
        ListToolsResultSchema
      );

      for (const tool of response.tools) {
        const toolName = `mcp__syntropy__${serverName}_${tool.name}`;

        // Filter by enabled state
        if (!toolStateManager.isEnabled(toolName)) {
          continue;
        }

        aggregatedTools.push({
          name: toolName,
          description: tool.description,
          inputSchema: tool.inputSchema
        });
      }
    } catch (error) {
      console.error(`Failed to aggregate tools from ${serverName}:`, error);
    }
  }

  return { tools: aggregatedTools };
});
```

### Phase 5: Update package.json and Build (15 min)

**File**: `syntropy-mcp/package.json`

**Verify build script**:
```json
{
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch"
  }
}
```

**Build and test**:
```bash
cd syntropy-mcp
npm run build
node dist/index.js
```

### Phase 6: Integration Testing (15 min)

**Test state persistence**:
```bash
# Test 1: Enable 3 tools, disable 2 tools
echo '{"enable": ["mcp__syntropy__serena_find_symbol", "mcp__syntropy__linear_create_issue", "mcp__syntropy__context7_get_library_docs"], "disable": ["mcp__syntropy__github_create_issue", "mcp__syntropy__git_git_status"]}' > test-enable.json

# Test 2: Verify state file created
cat ~/.syntropy/tool-state.json
# Expected: {"enabled": [...], "disabled": [...]}

# Test 3: Restart MCP server, verify state persists
# Kill and restart, then check tools/list output
```

## 4. Validation Gates

### Gate 1: ToolStateManager Unit Tests

**Command**: Create test file `syntropy-mcp/src/tool-manager.test.ts`

**Tests**:
```typescript
import { ToolStateManager } from './tool-manager';
import { promises as fs } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

describe('ToolStateManager', () => {
  let manager: ToolStateManager;
  const testStateFile = join(homedir(), '.syntropy', 'tool-state.json');

  beforeEach(async () => {
    manager = new ToolStateManager();
    await manager.initialize();
  });

  afterEach(async () => {
    // Cleanup test state file
    try {
      await fs.unlink(testStateFile);
    } catch {}
  });

  test('initialize creates default state', async () => {
    const state = manager.getState();
    expect(state.enabled).toEqual([]);
    expect(state.disabled).toEqual([]);
  });

  test('enableTools updates state', async () => {
    await manager.enableTools(
      ['tool1', 'tool2'],
      ['tool3']
    );

    const state = manager.getState();
    expect(state.enabled).toContain('tool1');
    expect(state.enabled).toContain('tool2');
    expect(state.disabled).toContain('tool3');
  });

  test('isEnabled returns true for enabled tools', async () => {
    await manager.enableTools(['tool1'], []);
    expect(manager.isEnabled('tool1')).toBe(true);
  });

  test('isEnabled returns false for disabled tools', async () => {
    await manager.enableTools([], ['tool1']);
    expect(manager.isEnabled('tool1')).toBe(false);
  });

  test('state persists across instances', async () => {
    await manager.enableTools(['tool1'], ['tool2']);

    const newManager = new ToolStateManager();
    await newManager.initialize();

    expect(newManager.isEnabled('tool1')).toBe(true);
    expect(newManager.isEnabled('tool2')).toBe(false);
  });
});
```

**Run**: `npm test`

**Success Criteria**: All tests pass

### Gate 2: enable_tools Command Integration Test

**Setup**:
```bash
cd syntropy-mcp
npm run build
node dist/index.js &
MCP_PID=$!
```

**Test Commands**:
```bash
# Test enable_tools command
echo '{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "mcp__syntropy__enable_tools",
    "arguments": {
      "enable": ["mcp__syntropy__serena_find_symbol", "mcp__syntropy__linear_create_issue"],
      "disable": ["mcp__syntropy__github_create_issue"]
    }
  },
  "id": 1
}' | nc localhost 3000

# Expected response:
# {
#   "jsonrpc": "2.0",
#   "result": {
#     "content": [{
#       "type": "text",
#       "text": "{\"success\": true, \"enabled_count\": 2, \"disabled_count\": 1, ...}"
#     }]
#   },
#   "id": 1
# }
```

**Verify state file**:
```bash
cat ~/.syntropy/tool-state.json
# Expected:
# {
#   "enabled": [
#     "mcp__syntropy__serena_find_symbol",
#     "mcp__syntropy__linear_create_issue"
#   ],
#   "disabled": [
#     "mcp__syntropy__github_create_issue"
#   ]
# }
```

**Success Criteria**: State file matches expected output, command returns success

### Gate 3: list_all_tools Command Test

**Test Command**:
```bash
echo '{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "mcp__syntropy__list_all_tools",
    "arguments": {}
  },
  "id": 2
}' | nc localhost 3000

# Expected response includes:
# {
#   "total_tools": 87,
#   "enabled_tools": 2,
#   "disabled_tools": 85,
#   "tools": [
#     {"name": "mcp__syntropy__serena_find_symbol", "status": "enabled", ...},
#     {"name": "mcp__syntropy__linear_create_issue", "status": "enabled", ...},
#     {"name": "mcp__syntropy__github_create_issue", "status": "disabled", ...},
#     ...
#   ]
# }
```

**Success Criteria**:
- All tools from all servers listed
- Status matches state file
- Counts are accurate

### Gate 4: State Persistence Across Restarts

**Test Steps**:
```bash
# 1. Enable 3 tools, disable 2
# (use enable_tools command from Gate 2)

# 2. Kill MCP server
kill $MCP_PID

# 3. Restart MCP server
node dist/index.js &
NEW_PID=$!

# 4. Call tools/list
echo '{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 3
}' | nc localhost 3000

# Expected: Only 3 enabled tools returned
```

**Success Criteria**:
- State persists after restart
- tools/list reflects persisted state

### Gate 5: tools/list Filtering

**Test Command**:
```bash
# After enabling only 3 tools in Gate 2
echo '{
  "jsonrpc": "2.0",
  "method": "tools/list",
  "params": {},
  "id": 4
}' | nc localhost 3000

# Expected response:
# {
#   "jsonrpc": "2.0",
#   "result": {
#     "tools": [
#       {"name": "mcp__syntropy__serena_find_symbol", ...},
#       {"name": "mcp__syntropy__linear_create_issue", ...},
#       {"name": "mcp__syntropy__enable_tools", ...},
#       {"name": "mcp__syntropy__list_all_tools", ...}
#     ]
#   },
#   "id": 4
# }
```

**Success Criteria**:
- Only enabled tools returned (plus the 2 new management commands)
- Disabled tools NOT in response

### Gate 6: State File Format Validation

**Check JSON validity**:
```bash
cat ~/.syntropy/tool-state.json | jq .
# Should parse without errors

# Verify structure
cat ~/.syntropy/tool-state.json | jq 'has("enabled") and has("disabled")'
# Expected: true
```

**Success Criteria**:
- Valid JSON format
- Contains `enabled` and `disabled` arrays
- Human-readable (2-space indentation)

## 5. Testing Strategy

### Test Framework

**Unit Tests**: Jest (TypeScript)
**Integration Tests**: Manual MCP protocol testing via `nc` (netcat)

### Test Command

```bash
# Unit tests
cd syntropy-mcp
npm test

# Build and manual integration tests
npm run build
node dist/index.js &
# Run validation gate commands above
```

### Test Coverage Requirements

**Unit Tests** (tool-manager.test.ts):
- State initialization (default state)
- Enable/disable operations
- isEnabled logic (enabled/disabled/default)
- State persistence
- Error handling (corrupted file, missing file)

**Integration Tests** (manual):
- enable_tools command end-to-end
- list_all_tools command end-to-end
- tools/list filtering
- State persistence across restarts
- State file format validation

### Edge Cases to Test

1. **Empty enable/disable arrays**: Should succeed with no state change
2. **Nonexistent tool names**: Log warning, skip invalid names
3. **Duplicate tool names in arrays**: Handle gracefully (use Set for deduplication)
4. **Corrupted state file**: Reset to default, log error
5. **State file permissions error**: Throw with actionable error message

## 6. Rollout Plan

### Phase 1: Development (2.5 hours)

**Tasks**:
1. Create `tool-manager.ts` with ToolStateManager class
2. Add `enable_tools` command to `index.ts`
3. Add `list_all_tools` command to `index.ts`
4. Modify `tools/list` handler to filter by state
5. Write unit tests for ToolStateManager
6. Build and run integration tests

**Milestone**: All validation gates pass

### Phase 2: Code Review (30 min)

**Checklist**:
- [ ] Code follows TypeScript best practices
- [ ] Error messages are actionable (include troubleshooting)
- [ ] No silent failures (exceptions bubble up)
- [ ] State file location documented in code comments
- [ ] Functions under 50 lines each
- [ ] File under 500 lines

### Phase 3: Documentation Update (15 min)

**Update**: `syntropy-mcp/README.md`

**Add section**:
```markdown
## Dynamic Tool Management

### Commands

#### enable_tools
Enable or disable tools at runtime without restart.

**Parameters**:
- `enable: string[]` - Tool names to enable
- `disable: string[]` - Tool names to disable

**Example**:
\`\`\`typescript
await client.request({
  method: 'tools/call',
  params: {
    name: 'mcp__syntropy__enable_tools',
    arguments: {
      enable: ['mcp__syntropy__serena_find_symbol'],
      disable: ['mcp__syntropy__github_create_issue']
    }
  }
});
\`\`\`

#### list_all_tools
List all tools from all connected servers with status.

**Returns**: Array of tools with name, description, server, status

### State File

Tool state persists to `~/.syntropy/tool-state.json`:
\`\`\`json
{
  "enabled": ["tool1", "tool2"],
  "disabled": ["tool3"]
}
\`\`\`

Default behavior: All tools enabled (empty lists).
```

### Phase 4: Deployment (5 min)

**Steps**:
```bash
# Build production bundle
cd syntropy-mcp
npm run build

# Update Claude Code config (no changes needed - same server)
# Restart Claude Code to reload MCP server

# Verify commands available
# Use list_all_tools to confirm
```

**Verification**: Run Gate 2-6 tests in production environment

### Rollback Plan

**If issues occur**:
1. Revert `index.ts` changes (remove new command handlers)
2. Delete `tool-manager.ts`
3. Rebuild: `npm run build`
4. Restart MCP server

**State File Cleanup** (if needed):
```bash
rm ~/.syntropy/tool-state.json
```

---

## Batch Execution Metadata

**Batch ID**: 30
**Stage**: stage-1-sequential
**Execution Order**: 1 (first in stage)
**Merge Order**: 1 (merge first)
**Conflict Potential**: NONE

**Worktree Path**: `../ctx-eng-plus-prp-30-1-1`
**Branch Name**: `prp-30-1-1-syntropy-mcp-tool-management`

**Files Modified**:
- `syntropy-mcp/src/index.ts` (add commands and handlers)
- `syntropy-mcp/src/tool-manager.ts` (new file)
- `syntropy-mcp/package.json` (verify build scripts)
- `~/.syntropy/tool-state.json` (state file, created at runtime)

**Conflict Notes**: None (separate repository from ctx-eng-plus)

**Plan Context**: Part of Dynamic Tool Management for Syntropy MCP initiative. This PRP enables the foundation for dynamic tool filtering, which subsequent PRPs will build upon for context-aware tool selection and performance optimization.
