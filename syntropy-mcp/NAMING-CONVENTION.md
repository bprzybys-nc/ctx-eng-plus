# Syntropy MCP Tool Naming Convention

**Version**: 1.0
**Status**: CANONICAL - Single source of truth
**Last Updated**: 2025-11-08

---

## THE Convention (Use This Everywhere)

```
mcp__syntropy__<server>_<tool>
```

### Examples

```
mcp__syntropy__serena_find_symbol
mcp__syntropy__thinking_sequentialthinking
mcp__syntropy__context7_get_library_docs
mcp__syntropy__linear_create_issue
```

---

## Architecture Layers

### Layer 1: Claude Code Permission Names (User-Facing)

**Format**: `mcp__syntropy__<server>_<tool>`

**Location**: `.claude/settings.local.json`

**Example**:
```json
{
  "allow": [
    "mcp__syntropy__serena_find_symbol",
    "mcp__syntropy__thinking_sequentialthinking"
  ]
}
```

### Layer 2: Syntropy Tool Definitions (Internal Registry)

**Format**: `<server>_<tool>`

**Location**: `syntropy-mcp/src/tools-definition.ts`

**Example**:
```typescript
{
  name: "thinking_sequentialthinking",  // Format: SERVER_TOOL
  description: "Sequential thinking process",
  inputSchema: { ... }
}
```

### Layer 3: MCP Server Routes (Connection Mapping)

**Format**: `syn-<server>` → `mcp__<server>__` prefix

**Location**: `syntropy-mcp/src/index.ts` (SERVER_ROUTES)

**Example**:
```typescript
const SERVER_ROUTES: Record<string, string> = {
  "syn-thinking": "mcp__sequential-thinking__",  // Pool key → MCP prefix
  "syn-serena": "mcp__serena__",
  "syn-context7": "mcp__context7__"
};
```

### Layer 4: Underlying MCP Server Tool Names (Actual Tools)

**Format**: Varies by server (no prefix)

**Examples**:
- Sequential Thinking Server: `sequentialthinking`
- Serena Server: `find_symbol`, `get_symbols_overview`
- Context7 Server: `get-library-docs` (hyphens)

---

## Data Flow Example (Sequential Thinking)

```
User calls: mcp__syntropy__thinking_sequentialthinking
           ↓
Syntropy parses: server="thinking", tool="sequentialthinking"
           ↓
Maps to pool key: "syn-thinking"
           ↓
Normalizes tool: "sequentialthinking" (no change for thinking server)
           ↓
Forwards to MCP server: sequentialthinking
           ↓
Sequential Thinking Server executes tool
```

---

## Naming Rules by Server

### 1. Serena
- **Tool pattern**: `serena_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `serena_find_symbol` → forwards as `find_symbol`

### 2. Sequential Thinking
- **Tool pattern**: `thinking_sequentialthinking`
- **Normalization**: No change
- **Example**: `thinking_sequentialthinking` → forwards as `sequentialthinking`

### 3. Context7
- **Tool pattern**: `context7_<tool_name>`
- **Normalization**: Replace underscores with hyphens
- **Example**: `context7_get_library_docs` → forwards as `get-library-docs`

### 4. Linear
- **Tool pattern**: `linear_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `linear_create_issue` → forwards as `create_issue`

### 5. Filesystem
- **Tool pattern**: `filesystem_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `filesystem_read_file` → forwards as `read_file`

### 6. Git
- **Tool pattern**: `git_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `git_git_status` → forwards as `git_status`

### 7. Repomix
- **Tool pattern**: `repomix_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `repomix_pack_codebase` → forwards as `pack_codebase`

### 8. GitHub
- **Tool pattern**: `github_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `github_create_issue` → forwards as `create_issue`

### 9. Perplexity
- **Tool pattern**: `perplexity_<tool_name>`
- **Normalization**: Keep underscores
- **Example**: `perplexity_ask` → forwards as `ask`

---

## Files Using This Convention

### Configuration Files
1. **`.claude/settings.local.json`**
   - Uses: `mcp__syntropy__<server>_<tool>`
   - Purpose: Permission management

2. **`syntropy-mcp/servers.json`**
   - Uses: `syn-<server>` (pool keys)
   - Purpose: MCP server process configuration

### Source Code Files
1. **`syntropy-mcp/src/tools-definition.ts`**
   - Uses: `<server>_<tool>`
   - Purpose: Tool registry

2. **`syntropy-mcp/src/index.ts`**
   - Uses: `SERVER_ROUTES` mapping
   - Purpose: Route tool calls to correct MCP server

3. **`syntropy-mcp/src/client-manager.ts`**
   - Uses: `syn-<server>` (pool keys)
   - Purpose: MCP client lifecycle management

### Documentation Files
1. **`syntropy-mcp/README.md`**
   - Should use: `mcp__syntropy__<server>_<tool>` in examples

2. **`syntropy-mcp/tool-index.md`**
   - Should use: `mcp__syntropy__<server>_<tool>` in examples

3. **`CLAUDE.md`**
   - Should use: `mcp__syntropy__<server>_<tool>` when referencing tools

4. **`.serena/memories/tool-usage-syntropy.md`**
   - Should use: `mcp__syntropy__<server>_<tool>` in examples

---

## Common Mistakes (DO NOT DO)

❌ **Wrong**: `mcp__syntropy_thinking_sequentialthinking` (single underscore after syntropy)
✅ **Right**: `mcp__syntropy__thinking_sequentialthinking` (double underscore)

❌ **Wrong**: `syntropy__thinking__sequentialthinking` (missing mcp prefix)
✅ **Right**: `mcp__syntropy__thinking_sequentialthinking`

❌ **Wrong**: `mcp__thinking__sequentialthinking` (missing syntropy)
✅ **Right**: `mcp__syntropy__thinking_sequentialthinking`

❌ **Wrong**: `thinking_sequentialthinking` (in permissions file)
✅ **Right**: `mcp__syntropy__thinking_sequentialthinking` (in permissions file)

---

## Tool State File

**Location**: `~/.syntropy/tool-state.json`

**Format**:
```json
{
  "enabled": ["mcp__syntropy__serena_find_symbol"],
  "disabled": ["mcp__syntropy__filesystem_read_file"]
}
```

**Rule**: Always use full `mcp__syntropy__<server>_<tool>` format in this file.

---

## Validation Checklist

When adding a new MCP server:

- [ ] Add entry to `syntropy-mcp/servers.json` with key `syn-<server>`
- [ ] Add mapping to `SERVER_ROUTES` in `syntropy-mcp/src/index.ts`
- [ ] Add tools to `SYNTROPY_TOOLS` in `syntropy-mcp/src/tools-definition.ts` using `<server>_<tool>` format
- [ ] Add normalization rule to `normalizeToolName()` if server uses hyphens or special naming
- [ ] Update `.claude/settings.local.json` with `mcp__syntropy__<server>_<tool>` patterns
- [ ] Document tools in `syntropy-mcp/tool-index.md`
- [ ] Test tool call end-to-end

---

## Troubleshooting

### Error: "No such tool available"

**Possible Causes**:
1. Tool name mismatch (check normalizeToolName() rules)
2. MCP server not connected (check `syntropy-mcp/servers.json` lazy/eager settings)
3. Tool disabled in `~/.syntropy/tool-state.json`
4. Permission denied in `.claude/settings.local.json`

**Debug Steps**:
```bash
# 1. Check health
/syntropy-health

# 2. Check tool state
cat ~/.syntropy/tool-state.json

# 3. Check permissions
grep "thinking" .claude/settings.local.json

# 4. Reconnect MCP
/mcp
```

### Error: "Invalid syntropy tool name"

**Cause**: Tool name doesn't match expected format.

**Fix**: Ensure using `mcp__syntropy__<server>_<tool>` format everywhere.

---

## Best Practices

1. **Always use double underscores** after `mcp` and `syntropy`
2. **Use single underscore** between server and tool name
3. **Keep server names consistent** across all files
4. **Document new tools** immediately after adding them
5. **Test end-to-end** before committing

---

## References

- MCP Specification: https://modelcontextprotocol.io/specification/
- SEP-986 (Tool Name Format): https://github.com/modelcontextprotocol/modelcontextprotocol/issues/986
- Syntropy MCP README: ./README.md
- Tool Index: ./tool-index.md
