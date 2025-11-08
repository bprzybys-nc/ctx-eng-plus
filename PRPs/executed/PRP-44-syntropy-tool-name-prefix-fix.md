# PRP-44-INITIAL: Fix Syntropy MCP Tool Name Prefix Registration

**Status**: initial
**Created**: 2025-11-08
**Estimated Hours**: 2-3h
**Complexity**: low
**Tags**: [mcp, syntropy, bug-fix, tool-registration]

---

## TL;DR

Syntropy MCP tools show as available but fail when called with "No such tool available". Root cause: `ListToolsRequestSchema` handler returns tools WITHOUT the `mcp__syntropy__` prefix, causing naming mismatch.

**Fix**: Add prefix to tool names in ListTools response + simplify SERVER_ROUTES.

---

## Problem Statement

### Current Behavior

```bash
# Hook shows 28 tools available
✅ thinking_sequentialthinking (listed)
✅ serena_activate_project (listed)
✅ healthcheck (listed)

# But all calls fail
❌ mcp__syntropy__thinking_sequentialthinking → "No such tool available"
❌ mcp__syntropy__serena_activate_project → "No such tool available"
❌ mcp__syntropy__healthcheck → "No such tool available"
```

### Root Cause

**ListToolsRequestSchema handler returns unprefixed tool names**:

```typescript
// Current (WRONG)
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const enabledTools = SYNTROPY_TOOLS.filter(tool => {
    const toolName = `mcp__syntropy__${tool.name}`;
    return toolStateManager.isEnabled(toolName);
  });
  return { tools: enabledTools };  // ❌ Returns "thinking_sequentialthinking"
});
```

Claude Code registers tools as `thinking_sequentialthinking` but expects calls to `mcp__syntropy__thinking_sequentialthinking`.

---

## Correct Naming Convention

Per user specification:

```
mcp__syntropy__{server}_{function}
```

**Examples**:
- `mcp__syntropy__thinking_sequentialthinking` (double __ after syntropy, single _ between parts)
- `mcp__syntropy__serena_find_symbol`
- `mcp__syntropy__healthcheck` (syntropy's own function)

---

## Proposed Solution

### Fix 1: Add Prefix in ListTools Handler

**File**: `syntropy-mcp/src/index.ts` (line ~223)

```typescript
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const enabledTools = SYNTROPY_TOOLS.filter(tool => {
    const toolName = `mcp__syntropy__${tool.name}`;
    return toolStateManager.isEnabled(toolName);
  });

  // ✅ ADD PREFIX TO RETURNED TOOLS
  return {
    tools: enabledTools.map(tool => ({
      ...tool,
      name: `mcp__syntropy__${tool.name}`
    }))
  };
});
```

### Fix 2: Verify parseSyntropyTool Pattern

**File**: `syntropy-mcp/src/index.ts` (line ~79)

```typescript
function parseSyntropyTool(toolName: string) {
  // ✅ Correct pattern: mcp__syntropy__{server}_{tool}
  let match = toolName.match(/^mcp__syntropy__([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  // Legacy fallback (can remove later)
  match = toolName.match(/^mcp__syntropy_([^_]+)_(.+)$/);
  if (match) {
    const [, server, tool] = match;
    return { server, tool };
  }

  return null;
}
```

**Note**: Pattern already correct - no changes needed.

### Fix 3: Update Documentation

**File**: `syntropy-mcp/NAMING-CONVENTION.md`

Update to clarify:
- ListTools MUST return prefixed names
- Tool definitions in `tools-definition.ts` use unprefixed format
- Prefix added during registration

---

## Implementation Steps

### Step 1: Update ListTools Handler (30 min)

1. Read `syntropy-mcp/src/index.ts`
2. Find `ListToolsRequestSchema` handler (~line 223)
3. Add `.map()` to prefix tool names
4. Save file

### Step 2: Rebuild (5 min)

```bash
cd syntropy-mcp
npm run build
```

### Step 3: Test Locally (15 min)

```bash
# Start server
npm start

# In another terminal, test direct call
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node build/index.js
# Should see: "mcp__syntropy__thinking_sequentialthinking" (WITH prefix)
```

### Step 4: Deploy to Claude Code (10 min)

1. Quit Claude Code
2. Reopen Claude Code
3. Test tool call

### Step 5: Validate All Tools (30 min)

Test representative tools from each server:
- `mcp__syntropy__thinking_sequentialthinking`
- `mcp__syntropy__serena_activate_project`
- `mcp__syntropy__context7_get_library_docs`
- `mcp__syntropy__linear_create_issue`
- `mcp__syntropy__healthcheck`

### Step 6: Update Documentation (30 min)

Update:
- `syntropy-mcp/NAMING-CONVENTION.md`
- `tmp/mcp-issue/naming-analysis.md` (mark as resolved)
- `examples/syntropy-naming-convention.md`

---

## Validation Gates

- [ ] ListTools returns prefixed tool names (`mcp__syntropy__{server}_{function}`)
- [ ] `parseSyntropyTool()` correctly parses prefixed names
- [ ] All 28 syntropy tools callable without errors
- [ ] Thinking tool works (test for intermittent failures fix)
- [ ] Serena tools work
- [ ] System tools (healthcheck, list_all_tools, enable_tools) work
- [ ] No regressions in tool forwarding to underlying servers
- [ ] Build succeeds without errors
- [ ] Documentation updated

---

## Testing Strategy

### Unit Tests

```typescript
// Test parseSyntropyTool
describe('parseSyntropyTool', () => {
  it('parses mcp__syntropy__{server}_{tool} format', () => {
    const result = parseSyntropyTool('mcp__syntropy__thinking_sequentialthinking');
    expect(result).toEqual({ server: 'thinking', tool: 'sequentialthinking' });
  });

  it('parses mcp__syntropy__{function} format', () => {
    const result = parseSyntropyTool('mcp__syntropy__healthcheck');
    expect(result).toEqual({ server: 'syntropy', tool: 'healthcheck' });
  });
});
```

### Integration Tests

```bash
# Test via Claude Code
mcp__syntropy__thinking_sequentialthinking({
  thought: "Integration test",
  thoughtNumber: 1,
  totalThoughts: 1,
  nextThoughtNeeded: false
})
# Expected: Success with sequential thinking output
```

### End-to-End Tests

Test all 9 MCP servers:
1. serena (code intelligence) - `serena_find_symbol`
2. thinking (sequential reasoning) - `thinking_sequentialthinking`
3. context7 (library docs) - `context7_get_library_docs`
4. linear (project management) - `linear_list_issues`
5. filesystem (file ops) - `filesystem_read_file` (if enabled)
6. git (version control) - `git_git_status` (if enabled)
7. repomix (codebase) - `repomix_pack_codebase` (if enabled)
8. github (GitHub ops) - `github_create_issue` (if enabled)
9. perplexity (web search) - `perplexity_ask` (if enabled)

---

## Risks & Mitigations

### Risk 1: Breaking Existing Calls

**Impact**: If any code directly calls unprefixed tool names

**Mitigation**:
- Tool definitions unchanged (`thinking_sequentialthinking`)
- Only ListTools response changes
- All documented examples use prefixed format

**Likelihood**: Low (tools weren't working anyway)

### Risk 2: Tool State Filter Mismatch

**Impact**: `toolStateManager.isEnabled()` checks might fail

**Mitigation**:
- Filter logic already uses prefixed names
- No change needed to filtering

**Likelihood**: None (already correct)

### Risk 3: Parsing Regression

**Impact**: `parseSyntropyTool()` might fail on new format

**Mitigation**:
- Pattern already correct: `/^mcp__syntropy__([^_]+)_(.+)$/`
- Add unit tests to verify

**Likelihood**: Low (pattern already handles this)

---

## Success Criteria

### Functional

- ✅ All 28 syntropy tools callable without errors
- ✅ Tool names match across all layers (definition → registration → call)
- ✅ No "No such tool available" errors
- ✅ Tool forwarding to underlying MCP servers works correctly

### Technical

- ✅ ListTools returns tools with `mcp__syntropy__` prefix
- ✅ parseSyntropyTool correctly parses all formats
- ✅ Build succeeds without TypeScript errors
- ✅ No breaking changes to tool definitions

### User Experience

- ✅ Users can call tools using documented format
- ✅ Error messages clear when tool calls fail
- ✅ Hook shows correct tool count and names
- ✅ MCP panel in Claude Code shows correct tool list

---

## Rollback Plan

If fix causes issues:

```bash
cd syntropy-mcp
git revert HEAD
npm run build
# Restart Claude Code
```

Worst case: Tools remain broken (same as before fix).

---

## Related PRPs/Issues

- **PRP-43**: Batch PRP generation for Task-based architecture (separate concern)
- **Sequential thinking lazy init**: Fixed in previous commit (05bb6b9)
- **Naming convention docs**: Created in NAMING-CONVENTION.md

---

## Files Modified

1. `syntropy-mcp/src/index.ts` (ListToolsRequestSchema handler)
2. `syntropy-mcp/NAMING-CONVENTION.md` (documentation update)
3. `tmp/mcp-issue/naming-analysis.md` (mark as resolved)

**Total**: 3 files, ~10 lines of code changed

---

## Estimated Timeline

- **Step 1 (Code fix)**: 30 min
- **Step 2 (Build)**: 5 min
- **Step 3 (Local test)**: 15 min
- **Step 4 (Deploy)**: 10 min
- **Step 5 (Validate)**: 30 min
- **Step 6 (Docs)**: 30 min

**Total**: 2 hours

---

## Next Steps

1. **Review this PRP** - validate approach
2. **Execute fix** - implement ListTools change
3. **Test thoroughly** - all 28 tools
4. **Document** - update naming convention docs
5. **Close issue** - verify no "No such tool available" errors

---

## Notes

### Why This Happens

MCP protocol requires servers to return tool names exactly as they should be called. Syntropy was returning unprefixed internal names (`thinking_sequentialthinking`) but expecting prefixed calls (`mcp__syntropy__thinking_sequentialthinking`).

### Why Simple Fix

Only need to add `.map()` in one handler - prefix is added during tool registration, not throughout the codebase.

### Verification Method

Check ListTools output directly:
```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | node build/index.js | jq '.result.tools[0].name'
# Before: "thinking_sequentialthinking"
# After:  "mcp__syntropy__thinking_sequentialthinking"
```

---

## References

- Analysis doc: `tmp/mcp-issue/naming-analysis.md`
- Naming convention: `syntropy-mcp/NAMING-CONVENTION.md`
- MCP Specification: https://modelcontextprotocol.io/specification/2025-06-18/basic/tools/
