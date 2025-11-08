# Syntropy MCP Tool Naming - Minimal Fix Plan

**Issue**: `mcp__syntropy__thinking_sequentialthinking` returns "No such tool available"

**Date**: 2025-11-08

---

## Current State Analysis

### What's Working
- All other MCP servers (serena, context7, linear, etc.)
- Server connection pooling
- Tool forwarding logic

### What's Broken
- Sequential thinking tool fails intermittently
- Error: "No such tool available: mcp__syntropy__thinking_sequentialthinking"

---

## Root Cause

**Tool name mismatch** between what Syntropy expects and what the actual MCP server exposes.

### Current Flow
```
User calls: mcp__syntropy__thinking_sequentialthinking
         ↓
Syntropy parses: server="thinking", tool="sequentialthinking"
         ↓
Forwards to MCP server: "sequentialthinking"
         ↓
Sequential Thinking Server: ??? (unknown tool name)
```

### Issue
We don't know the **actual tool name** that `@modelcontextprotocol/server-sequential-thinking` exposes.

---

## Hypothesis

The sequential-thinking MCP server likely exposes tool as:
- **Option A**: `think` (not `sequentialthinking`)
- **Option B**: `sequentialThinking` (camelCase)
- **Option C**: `sequential-thinking` (with hyphen)

---

## Minimal Fix Options

### Option 1: Query the Server Directly (RECOMMENDED)

**Test what tool name the server actually exposes**:

```bash
# Start server and query tools list
cd syntropy-mcp
npm run test -- --grep "thinking"
```

**Then update** `src/tools-definition.ts` if needed.

### Option 2: Add Tool Name Mapping

**If the actual tool is `think`**, add mapping in `normalizeToolName()`:

```typescript
// src/index.ts
function normalizeToolName(server: string, tool: string): string {
  if (server === "context7") {
    return tool.replace(/_/g, "-");
  }
  if (server === "thinking") {
    // Map our internal name to actual MCP server tool name
    if (tool === "sequentialthinking") {
      return "think";  // <-- ADD THIS
    }
    return tool;
  }
  return tool;
}
```

### Option 3: Update Tool Definition

**If we're using wrong name**, update `src/tools-definition.ts`:

```typescript
// Current (line 536)
{
  name: "thinking_sequentialthinking",
  ...
}

// Change to
{
  name: "thinking_think",  // <-- IF actual tool is "think"
  ...
}
```

---

## Files to Check

1. **`syntropy-mcp/src/tools-definition.ts:536`**
   - Current: `name: "thinking_sequentialthinking"`
   - Verify this matches actual MCP server tool name

2. **`syntropy-mcp/src/index.ts:144-146`**
   - Current: `normalizeToolName()` returns tool as-is for "thinking"
   - May need mapping if actual tool name differs

3. **`syntropy-mcp/servers.json:43-50`**
   - Current: `syn-thinking` with `lazy: false` (eager init)
   - Verify server is actually starting

---

## Validation Steps

### Step 1: Verify Server Connection
```bash
cd syntropy-mcp
npm start &
# Check logs for "syn-thinking" connection
```

### Step 2: Query Available Tools
```bash
# In another terminal, list tools from thinking server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | npx -y @modelcontextprotocol/server-sequential-thinking
```

### Step 3: Test Direct Tool Call
```bash
# Call the tool directly to see actual name
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"think","arguments":{}}}' | npx -y @modelcontextprotocol/server-sequential-thinking
```

---

## Action Items

- [ ] **Immediate**: Query sequential-thinking server for actual tool name
- [ ] **Fix**: Update either `tools-definition.ts` or `normalizeToolName()`
- [ ] **Test**: Call `mcp__syntropy__thinking_sequentialthinking` successfully
- [ ] **Document**: Update tool-index.md with confirmed tool name
- [ ] **Commit**: Single atomic commit with minimal changes

---

## Expected Outcome

After fix:
```bash
# This should work
/mcp
mcp__syntropy__thinking_sequentialthinking(problem="Test")
# Returns: thinking process output
```

---

## Rollback Plan

If fix breaks other tools:
```bash
cd syntropy-mcp
git revert HEAD
npm run build
npm start
```

---

## Next Steps

1. Run validation Step 2 above to get actual tool name
2. Apply minimal fix (Option 2 or 3)
3. Test end-to-end
4. Update documentation
5. Commit

