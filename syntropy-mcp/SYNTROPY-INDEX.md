# Syntropy MCP - Complete Index

**Version**: 1.0
**Last Updated**: 2025-11-08
**Purpose**: Single source of truth for all Syntropy MCP documentation

---

## Quick Navigation

- **[NAMING-CONVENTION.md](../examples/syntropy-mcp-naming-convention.md)** → Canonical naming spec (use this for all tool references)
- **[MINIMAL-FIX-PLAN.md](./MINIMAL-FIX-PLAN.md)** → Current issue diagnosis and fix plan
- **[README.md](./README.md)** → Project overview and architecture
- **[QUICKSTART.md](./QUICKSTART.md)** → Setup and usage examples
- **[tool-index.md](./tool-index.md)** → Complete list of available tools
- **[../examples/syntropy-naming-convention.md](../examples/syntropy-naming-convention.md)** → User-facing guide

---

## The One Naming Convention

**Format**: `mcp__syntropy__<server>_<tool>`

**Example**: `mcp__syntropy__thinking_sequentialthinking`

**Rule**: Use this format EVERYWHERE - no exceptions.

**Details**: See [NAMING-CONVENTION.md](../examples/syntropy-mcp-naming-convention.md)

---

## Current Status

### What's Working ✅
- Serena tools (code intelligence)
- Context7 tools (library docs)
- Linear tools (project management)
- Filesystem tools (denied by default, working when enabled)
- Git tools (denied by default, working when enabled)
- Tool state management (`~/.syntropy/tool-state.json`)
- Connection pooling and lazy initialization
- Health monitoring

### Known Issues ⚠️
- **Sequential Thinking tool fails intermittently**
  - Symptom: "No such tool available" error
  - Frequency: ~50% of the time ("every second time")
  - Root cause: Likely eager initialization timing issue
  - Fix: See [MINIMAL-FIX-PLAN.md](./MINIMAL-FIX-PLAN.md)

---

## Architecture Overview

```
Claude Code (User)
        ↓
.claude/settings.local.json (permissions)
        ↓
mcp__syntropy__<server>_<tool> (standard format)
        ↓
Syntropy MCP Server (aggregator)
        ↓
syntropy-mcp/src/tools-definition.ts (registry)
        ↓
syntropy-mcp/src/index.ts (routing)
        ↓
syntropy-mcp/src/client-manager.ts (pooling)
        ↓
Underlying MCP Servers (9 servers)
        ↓
Tool Results
```

**Key Files**:
1. `servers.json` → MCP server process configuration
2. `src/tools-definition.ts` → Tool registry (58 tools)
3. `src/index.ts` → Server routes and normalization
4. `src/client-manager.ts` → Connection lifecycle
5. `.claude/settings.local.json` → Permission management

---

## Server Configuration

### Eager Initialization (lazy: false)
Servers that start immediately on Syntropy startup:

1. **syn-serena** (code intelligence)
2. **syn-filesystem** (file operations)
3. **syn-git** (version control)
4. **syn-thinking** (sequential reasoning) ⚠️ *Intermittent failures*
5. **syn-linear** (project management)

### Lazy Initialization (lazy: true)
Servers that start on first tool call:

6. **syn-context7** (library docs)
7. **syn-repomix** (codebase packaging)
8. **syn-github** (GitHub operations)
9. **syn-perplexity** (web search)

---

## Tool Categories

### Code Intelligence (13 tools)
**Server**: `serena`
**Status**: ✅ Working
**Examples**:
- `mcp__syntropy__serena_find_symbol`
- `mcp__syntropy__serena_get_symbols_overview`
- `mcp__syntropy__serena_search_for_pattern`

### Complex Reasoning (1 tool)
**Server**: `thinking`
**Status**: ⚠️ Intermittent
**Tool**: `mcp__syntropy__thinking_sequentialthinking`

### Library Documentation (2 tools)
**Server**: `context7`
**Status**: ✅ Working
**Examples**:
- `mcp__syntropy__context7_get_library_docs`
- `mcp__syntropy__context7_resolve_library_id`

### Project Management (9 tools)
**Server**: `linear`
**Status**: ✅ Working
**Examples**:
- `mcp__syntropy__linear_create_issue`
- `mcp__syntropy__linear_get_issue`
- `mcp__syntropy__linear_list_issues`

### File Operations (8 tools - DENIED)
**Server**: `filesystem`
**Status**: ✅ Working (when enabled)
**Default**: Denied (use native Read/Write/Edit instead)

### Version Control (5 tools - DENIED)
**Server**: `git`
**Status**: ✅ Working (when enabled)
**Default**: Denied (use native Bash(git:*) instead)

### Codebase Packaging (4 tools - DENIED)
**Server**: `repomix`
**Status**: ✅ Working (when enabled)
**Default**: Denied (use incremental Grep/Glob/Read instead)

### GitHub Operations (26 tools - DENIED)
**Server**: `github`
**Status**: ✅ Working (when enabled)
**Default**: Denied (use native Bash(gh:*) instead)

### Web Search (1 tool - DENIED)
**Server**: `perplexity`
**Status**: ✅ Working (when enabled)
**Default**: Denied (use native WebSearch instead)

---

## Tool State Management

**File**: `~/.syntropy/tool-state.json`

**Format**:
```json
{
  "enabled": ["mcp__syntropy__serena_find_symbol"],
  "disabled": ["mcp__syntropy__filesystem_read_file"]
}
```

**Commands**:
- `/sync-with-syntropy` → Sync `.claude/settings.local.json` ↔ `tool-state.json`
- `/syntropy-health` → Check server connections and tool availability

---

## Naming Conventions by File

### 1. User-Facing (Full Format)
**Files**: `.claude/settings.local.json`, CLAUDE.md, PRPs, Serena memories

**Format**: `mcp__syntropy__<server>_<tool>`

**Example**:
```json
{
  "allow": [
    "mcp__syntropy__serena_find_symbol",
    "mcp__syntropy__thinking_sequentialthinking"
  ]
}
```

### 2. Internal Registry (Server_Tool Format)
**File**: `syntropy-mcp/src/tools-definition.ts`

**Format**: `<server>_<tool>`

**Example**:
```typescript
{
  name: "thinking_sequentialthinking",
  description: "Sequential thinking process",
  inputSchema: { ... }
}
```

### 3. Server Routes (Pool Key → MCP Prefix)
**File**: `syntropy-mcp/src/index.ts` (SERVER_ROUTES)

**Format**: `syn-<server>` → `mcp__<server>__` prefix

**Example**:
```typescript
const SERVER_ROUTES: Record<string, string> = {
  "syn-thinking": "mcp__sequential-thinking__",
  "syn-serena": "mcp__serena__"
};
```

### 4. Process Configuration (Pool Keys)
**File**: `syntropy-mcp/servers.json`

**Format**: `syn-<server>`

**Example**:
```json
{
  "servers": {
    "syn-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"]
    }
  }
}
```

---

## Tool Name Normalization Rules

### Default (Most Servers)
Keep tool name as-is (with underscores)

**Servers**: serena, filesystem, git, linear, repomix, github, perplexity
**Example**: `serena_find_symbol` → forwards as `find_symbol`

### Context7 (Hyphens)
Replace underscores with hyphens

**Server**: context7
**Example**: `context7_get_library_docs` → forwards as `get-library-docs`

### Sequential Thinking (No Change)
Return tool name as-is

**Server**: thinking
**Example**: `thinking_sequentialthinking` → forwards as `sequentialthinking`

---

## Troubleshooting Guide

### Error: "No such tool available"

**Possible Causes**:
1. Tool name mismatch (check [NAMING-CONVENTION.md](../examples/syntropy-mcp-naming-convention.md))
2. Server not connected (run `/syntropy-health`)
3. Tool disabled in `~/.syntropy/tool-state.json`
4. Permission denied in `.claude/settings.local.json`

**Debug Steps**:
```bash
# 1. Check server health
/syntropy-health

# 2. Reconnect MCP
/mcp

# 3. Check tool state
cat ~/.syntropy/tool-state.json

# 4. Check permissions
grep "thinking" .claude/settings.local.json

# 5. Test direct server connection
npx -y @modelcontextprotocol/server-sequential-thinking
```

### Error: Intermittent failures

**Symptom**: Tool works sometimes, fails other times
**Likely Cause**: Eager initialization timing issue
**Fix**: See [MINIMAL-FIX-PLAN.md](./MINIMAL-FIX-PLAN.md)

### Error: Permission denied

**Cause**: Tool in deny list
**Fix**:
```bash
# Remove from deny list in .claude/settings.local.json
# Then sync
/sync-with-syntropy
```

---

## Development Workflow

### Adding a New MCP Server

1. **Add to `servers.json`**:
```json
{
  "syn-newserver": {
    "command": "npx",
    "args": ["-y", "@scope/mcp-server-name"],
    "lazy": true
  }
}
```

2. **Add to `SERVER_ROUTES` in `src/index.ts`**:
```typescript
const SERVER_ROUTES: Record<string, string> = {
  "syn-newserver": "mcp__newserver__",
  // ... other routes
};
```

3. **Add tools to `SYNTROPY_TOOLS` in `src/tools-definition.ts`**:
```typescript
{
  name: "newserver_tool_name",
  description: "Tool description",
  inputSchema: { ... }
}
```

4. **Add normalization if needed** in `normalizeToolName()`:
```typescript
if (server === "newserver") {
  return tool.replace(/_/g, "-");  // if server uses hyphens
}
```

5. **Update permissions** in `.claude/settings.local.json`:
```json
{
  "allow": [
    "mcp__syntropy__newserver_tool_name"
  ]
}
```

6. **Test**:
```bash
cd syntropy-mcp
npm run build
npm test
```

### Updating an Existing Tool

1. Modify `src/tools-definition.ts`
2. Rebuild: `npm run build`
3. Restart Syntropy: `/mcp`
4. Test: Call the tool

---

## Testing

### Unit Tests
```bash
cd syntropy-mcp
npm test
```

### Integration Tests
```bash
# Start Syntropy
npm start

# In another terminal, test tool call
# (via Claude Code or direct MCP client)
```

### Health Check
```bash
/syntropy-health
```

---

## Related Documentation

### Core Docs
- [README.md](./README.md) - Project overview
- [NAMING-CONVENTION.md](../examples/syntropy-mcp-naming-convention.md) - Canonical naming spec
- [QUICKSTART.md](./QUICKSTART.md) - Setup guide
- [tool-index.md](./tool-index.md) - Complete tool list

### Implementation Docs
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Production deployment
- [PRODUCTION_READINESS.md](./PRODUCTION_READINESS.md) - Production checklist
- [EAGER_INIT_VERIFICATION.md](./EAGER_INIT_VERIFICATION.md) - Eager init testing
- [SYNTROPY_HEALTH_SETUP.md](./SYNTROPY_HEALTH_SETUP.md) - Health monitoring setup

### Issue-Specific Docs
- [MINIMAL-FIX-PLAN.md](./MINIMAL-FIX-PLAN.md) - Sequential thinking fix plan
- [DENOISE_IMPLEMENTATION.md](./DENOISE_IMPLEMENTATION.md) - Denoise tool
- [DENOISE_DEPLOYMENT.md](./DENOISE_DEPLOYMENT.md) - Denoise deployment
- [DENOISE_VALIDATION.md](./DENOISE_VALIDATION.md) - Denoise testing

### User Guides
- [../examples/syntropy-naming-convention.md](../examples/syntropy-naming-convention.md) - User-facing guide
- [../CLAUDE.md](../CLAUDE.md) - Project-level integration guide

---

## Version History

- **v1.0** (2025-11-08): Initial index creation
  - Established single naming convention
  - Documented current issues
  - Created comprehensive reference

---

## Maintenance

**Update Frequency**: On every Syntropy MCP change

**Update Checklist**:
- [ ] Update [NAMING-CONVENTION.md](../examples/syntropy-mcp-naming-convention.md) if convention changes
- [ ] Update tool-index.md when tools added/removed
- [ ] Update this index when new docs created
- [ ] Update MINIMAL-FIX-PLAN.md when issues resolved
- [ ] Rebuild and test after changes

---

## Support

**Issues**: File in project repo
**Questions**: See CLAUDE.md for project integration
**MCP Spec**: https://modelcontextprotocol.io/specification/

