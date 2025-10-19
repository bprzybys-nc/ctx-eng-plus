# INITIAL: Syntropy MCP Server - Unified Tool Aggregation Layer

## Feature Name
Syntropy MCP Server: Unified Interface for Multi-MCP Tool Access

## Feature Description
Create a single MCP server that aggregates and wraps all existing MCP tools (serena, filesystem, git, context7, sequential-thinking, linear-server, repomix) under a unified `syntropy:` namespace. This provides centralized tool access, auto-generated documentation, and simplified configuration while preserving all original functionality.

**Current Challenge**:
```json
// Fragmented tool access across 8+ MCP servers
"allow": [
  "mcp__serena__find_symbol",
  "mcp__filesystem__read_file",
  "mcp__git__git_status",
  "mcp__context7__resolve-library-id",
  "mcp__sequential-thinking__sequentialthinking",
  "mcp__linear-server__create_issue",
  // ... 40+ more tools
]
```

**Proposed Solution**:
```typescript
// Unified namespace with hierarchical organization
syntropy:serena:find_symbol
syntropy:filesystem:read_file
syntropy:git:status
syntropy:context7:resolve-library-id
syntropy:thinking:sequential
syntropy:linear:create_issue
```

**Key Benefits**:
- **Unified Access**: Single MCP server instead of 8 separate connections
- **Auto Documentation**: tool-index.md generated from live MCP metadata
- **Namespace Clarity**: Hierarchical structure (syntropy:server:tool)
- **Zero Changes**: Existing MCP tools unchanged, just wrapped
- **Discovery**: Single point for tool browsing and documentation

## Examples from Codebase

### Current MCP Configuration

**File**: `.claude/settings.local.json`

**Allowed Tools** (46 total across 8 servers):

```json
{
  "permissions": {
    "allow": [
      // Serena MCP (7 tools)
      "mcp__serena__find_symbol",
      "mcp__serena__get_symbols_overview",
      "mcp__serena__search_for_pattern",
      "mcp__serena__find_referencing_symbols",
      "mcp__serena__write_memory",
      "mcp__serena__create_text_file",
      "mcp__serena__activate_project",
      "mcp__serena__list_dir",
      "mcp__serena__read_file",

      // Filesystem MCP (8 tools)
      "mcp__filesystem__read_file",
      "mcp__filesystem__read_text_file",
      "mcp__filesystem__list_directory",
      "mcp__filesystem__write_file",
      "mcp__filesystem__edit_file",
      "mcp__filesystem__search_files",
      "mcp__filesystem__directory_tree",
      "mcp__filesystem__get_file_info",
      "mcp__filesystem__list_allowed_directories",

      // Git MCP (5 tools)
      "mcp__git__git_status",
      "mcp__git__git_diff",
      "mcp__git__git_log",
      "mcp__git__git_add",
      "mcp__git__git_commit",

      // Context7 MCP (2 tools)
      "mcp__context7__resolve-library-id",
      "mcp__context7__get-library-docs",

      // Sequential Thinking MCP (1 tool)
      "mcp__sequential-thinking__sequentialthinking",

      // Linear MCP (5 tools)
      "mcp__linear-server__create_issue",
      "mcp__linear-server__get_issue",
      "mcp__linear-server__list_issues",
      "mcp__linear-server__update_issue",
      "mcp__linear-server__list_projects",

      // Repomix MCP (1 tool)
      "mcp__repomix__pack_codebase"
    ]
  }
}
```

### Proposed Syntropy Namespace Structure

**File**: `syntropy-mcp/tool-index.md` (auto-generated)

```markdown
# Syntropy MCP Tool Index

## syntropy:serena - Code Intelligence Tools
- `syntropy:serena:find_symbol` - Find code symbols by name path
- `syntropy:serena:get_symbols_overview` - Get file symbol overview
- `syntropy:serena:search_for_pattern` - Search codebase patterns
- `syntropy:serena:find_referencing_symbols` - Find symbol references
- `syntropy:serena:write_memory` - Store project context
- `syntropy:serena:create_text_file` - Create new file
- `syntropy:serena:activate_project` - Switch active project
- `syntropy:serena:list_dir` - List directory contents
- `syntropy:serena:read_file` - Read file contents

## syntropy:filesystem - File Operations
- `syntropy:filesystem:read_file` - Read file (deprecated, use read_text_file)
- `syntropy:filesystem:read_text_file` - Read text file
- `syntropy:filesystem:list_directory` - List directory
- `syntropy:filesystem:write_file` - Write/overwrite file
- `syntropy:filesystem:edit_file` - Line-based file edits
- `syntropy:filesystem:search_files` - Recursive file search
- `syntropy:filesystem:directory_tree` - JSON directory tree
- `syntropy:filesystem:get_file_info` - File metadata
- `syntropy:filesystem:list_allowed_directories` - Show allowed paths

## syntropy:git - Version Control
- `syntropy:git:status` - Repository status
- `syntropy:git:diff` - Show changes
- `syntropy:git:log` - Commit history
- `syntropy:git:add` - Stage files
- `syntropy:git:commit` - Create commit

## syntropy:context7 - Documentation
- `syntropy:context7:resolve-library-id` - Find library ID
- `syntropy:context7:get-library-docs` - Fetch library docs

## syntropy:thinking - Advanced Reasoning
- `syntropy:thinking:sequential` - Sequential thinking process

## syntropy:linear - Project Management
- `syntropy:linear:create_issue` - Create Linear issue
- `syntropy:linear:get_issue` - Get issue details
- `syntropy:linear:list_issues` - List issues
- `syntropy:linear:update_issue` - Update issue
- `syntropy:linear:list_projects` - List projects

## syntropy:repomix - Codebase Analysis
- `syntropy:repomix:pack_codebase` - Package codebase for AI
```

### Usage Comparison

**Before (Current)**:
```typescript
// Claude Code makes direct MCP calls
await mcp.call("mcp__serena__find_symbol", {
  name_path: "MyClass/method",
  relative_path: "src/main.py"
});

await mcp.call("mcp__filesystem__read_text_file", {
  path: "/path/to/file.txt"
});
```

**After (Syntropy)**:
```typescript
// Unified namespace, same functionality
await mcp.call("syntropy:serena:find_symbol", {
  name_path: "MyClass/method",
  relative_path: "src/main.py"
});

await mcp.call("syntropy:filesystem:read_text_file", {
  path: "/path/to/file.txt"
});
```

## Implementation Requirements

### Phase 1: Tool Index Generation Script

**File**: `syntropy-mcp/scripts/generate-tool-index.py`

Create script to extract all MCP tool metadata and generate documentation:

```python
#!/usr/bin/env python3
"""Generate tool-index.md from live MCP server metadata.

Connects to all configured MCP servers and extracts:
- Tool names and descriptions
- Parameter schemas
- Return types
- Usage examples

Output: syntropy-mcp/tool-index.md
"""

import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any

def load_mcp_config() -> Dict[str, Any]:
    """Load MCP server configuration from settings.local.json."""
    config_path = Path(".claude/settings.local.json")
    with open(config_path) as f:
        return json.load(f)

def extract_tool_metadata(server_name: str) -> List[Dict[str, Any]]:
    """Extract tool metadata from MCP server.

    Args:
        server_name: MCP server name (e.g., 'serena', 'filesystem')

    Returns:
        List of tool metadata dicts with: name, description, parameters
    """
    # Use MCP protocol to query server for tool list
    # Format: {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
    # FIXME: Implement actual MCP protocol communication
    # TODO: Research MCP server introspection API
    return []  # FIXME: Placeholder

def generate_markdown_docs(tools_by_server: Dict[str, List[Dict]]) -> str:
    """Generate markdown documentation from tool metadata.

    Args:
        tools_by_server: Dict mapping server name to list of tools

    Returns:
        Markdown formatted documentation string
    """
    lines = [
        "# Syntropy MCP Tool Index",
        "",
        "Auto-generated from live MCP server metadata.",
        f"Last updated: {datetime.now().isoformat()}",
        "",
    ]

    # Group tools by server
    for server, tools in sorted(tools_by_server.items()):
        lines.append(f"## syntropy:{server} - {get_server_description(server)}")
        lines.append("")

        for tool in sorted(tools, key=lambda t: t["name"]):
            # Tool name and description
            lines.append(f"### `syntropy:{server}:{tool['name']}`")
            lines.append("")
            lines.append(tool.get("description", "No description available"))
            lines.append("")

            # Parameters
            if tool.get("parameters"):
                lines.append("**Parameters:**")
                for param, schema in tool["parameters"].items():
                    required = " (required)" if schema.get("required") else ""
                    lines.append(f"- `{param}`: {schema.get('type', 'any')}{required} - {schema.get('description', '')}")
                lines.append("")

        lines.append("")

    return "\n".join(lines)

def main():
    """Generate tool index documentation."""
    print("Generating tool index from MCP servers...")

    # Load config
    config = load_mcp_config()

    # Extract tools from each server
    tools_by_server = {}
    servers = ["serena", "filesystem", "git", "context7",
               "sequential-thinking", "linear-server", "repomix"]

    for server in servers:
        print(f"  Extracting {server} tools...")
        tools_by_server[server] = extract_tool_metadata(server)

    # Generate markdown
    markdown = generate_markdown_docs(tools_by_server)

    # Write to file
    output_path = Path("syntropy-mcp/tool-index.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown)

    print(f"✅ Generated {output_path}")
    print(f"   Total tools: {sum(len(t) for t in tools_by_server.values())}")

if __name__ == "__main__":
    main()
```

**Usage**:
```bash
cd syntropy-mcp
python scripts/generate-tool-index.py
# Output: syntropy-mcp/tool-index.md
```

### Phase 2: Syntropy MCP Server Implementation

**File**: `syntropy-mcp/src/index.ts` (TypeScript MCP Server)

Create MCP server that routes tool calls to underlying servers:

```typescript
#!/usr/bin/env node
/**
 * Syntropy MCP Server - Unified Tool Aggregation Layer
 *
 * Routes tool calls in format syntropy:server:tool to underlying MCP servers.
 * Preserves all original functionality while providing unified namespace.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

// MCP server connection pool
const mcpServers: Map<string, any> = new Map();

// Server routing configuration
const SERVER_ROUTES = {
  "serena": { transport: "stdio", command: "serena" },
  "filesystem": { transport: "stdio", command: "filesystem" },
  "git": { transport: "stdio", command: "git" },
  "context7": { transport: "stdio", command: "context7" },
  "sequential-thinking": { transport: "stdio", command: "sequential-thinking" },
  "linear-server": { transport: "stdio", command: "linear-server" },
  "repomix": { transport: "stdio", command: "repomix" },
};

/**
 * Parse syntropy tool name into server and tool components.
 *
 * @param toolName - Format: syntropy:server:tool
 * @returns { server: string, tool: string } or null if invalid
 */
function parseSyntropyTool(toolName: string): { server: string; tool: string } | null {
  const match = toolName.match(/^syntropy:([^:]+):(.+)$/);
  if (!match) return null;

  const [, server, tool] = match;
  return { server, tool };
}

/**
 * Initialize connection to underlying MCP server.
 */
async function connectToServer(serverName: string): Promise<any> {
  if (mcpServers.has(serverName)) {
    return mcpServers.get(serverName);
  }

  const config = SERVER_ROUTES[serverName];
  if (!config) {
    throw new Error(`Unknown MCP server: ${serverName}`);
  }

  // FIXME: Implement actual MCP server connection
  // TODO: Use MCP SDK to spawn and connect to underlying server
  const connection = null; // FIXME: Placeholder

  mcpServers.set(serverName, connection);
  return connection;
}

/**
 * Forward tool call to underlying MCP server.
 */
async function forwardToolCall(
  server: string,
  tool: string,
  args: any
): Promise<any> {
  const connection = await connectToServer(server);

  // Forward call with original tool name (without syntropy prefix)
  const originalToolName = `mcp__${server}__${tool}`;

  // FIXME: Implement actual MCP protocol forwarding
  // TODO: Send CallToolRequest to underlying server
  return {}; // FIXME: Placeholder
}

// Create Syntropy MCP server
const server = new Server(
  {
    name: "syntropy",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Handle tool listing (aggregate from all servers)
server.setRequestHandler(ListToolsRequestSchema, async () => {
  const allTools: any[] = [];

  for (const [serverName] of Object.entries(SERVER_ROUTES)) {
    // FIXME: Query each server for its tool list
    // TODO: Transform tool names to syntropy:server:tool format
    // allTools.push(...serverTools);
  }

  return { tools: allTools };
});

// Handle tool calls (route to appropriate server)
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  // Parse syntropy tool name
  const parsed = parseSyntropyTool(name);
  if (!parsed) {
    throw new Error(
      `Invalid syntropy tool name: ${name}\n` +
      `Expected format: syntropy:server:tool\n` +
      `🔧 Troubleshooting: Use 'syntropy:serena:find_symbol' format`
    );
  }

  const { server: targetServer, tool } = parsed;

  // Forward to underlying server
  try {
    const result = await forwardToolCall(targetServer, tool, args);
    return result;
  } catch (error) {
    throw new Error(
      `Failed to forward call to ${targetServer}:${tool}\n` +
      `Error: ${error.message}\n` +
      `🔧 Troubleshooting: Verify ${targetServer} MCP server is running`
    );
  }
});

// Start server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Syntropy MCP Server running on stdio");
}

main().catch(console.error);
```

**File**: `syntropy-mcp/package.json`

```json
{
  "name": "syntropy-mcp",
  "version": "0.1.0",
  "description": "Unified MCP tool aggregation layer",
  "type": "module",
  "bin": {
    "syntropy": "./build/index.js"
  },
  "scripts": {
    "build": "tsc",
    "watch": "tsc --watch",
    "prepare": "npm run build"
  },
  "dependencies": {
    "@modelcontextprotocol/sdk": "^0.5.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
```

**File**: `syntropy-mcp/tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./build",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

**Build**:
```bash
cd syntropy-mcp
npm install
npm run build
```

### Phase 3: Configuration Integration

**File**: `.claude/mcp.json` (new file for MCP server config)

```json
{
  "mcpServers": {
    "syntropy": {
      "command": "node",
      "args": ["/path/to/ctx-eng-plus/syntropy-mcp/build/index.js"],
      "env": {}
    }
  }
}
```

**File**: `.claude/settings.local.json` (update)

Replace individual MCP tool permissions with syntropy namespace:

```json
{
  "permissions": {
    "allow": [
      // Syntropy tools (replaces 46 individual MCP tools)
      "syntropy:serena:*",
      "syntropy:filesystem:*",
      "syntropy:git:*",
      "syntropy:context7:*",
      "syntropy:thinking:*",
      "syntropy:linear:*",
      "syntropy:repomix:*",

      // Keep bash and other non-MCP tools unchanged
      "Bash(git:*)",
      "Bash(uv run:*)",
      // ... etc
    ],
    "deny": [
      // Deny access to underlying MCP servers (force syntropy usage)
      "mcp__serena__*",
      "mcp__filesystem__*",
      "mcp__git__*",
      // ... etc
    ]
  }
}
```

**Migration Path**:
1. Initially allow both syntropy:* and mcp__* patterns
2. Test all functionality via syntropy namespace
3. Once verified, deny direct mcp__* access (force syntropy)

## Testing Strategy

### 1. Tool Routing Tests

**File**: `syntropy-mcp/tests/test_routing.ts`

```typescript
import { expect } from 'chai';
import { parseSyntropyTool, forwardToolCall } from '../src/index';

describe('Syntropy Tool Routing', () => {
  it('should parse syntropy:serena:find_symbol correctly', () => {
    const parsed = parseSyntropyTool('syntropy:serena:find_symbol');
    expect(parsed).to.deep.equal({
      server: 'serena',
      tool: 'find_symbol'
    });
  });

  it('should reject invalid tool format', () => {
    const parsed = parseSyntropyTool('invalid:format');
    expect(parsed).to.be.null;
  });

  it('should forward call to serena server', async () => {
    const result = await forwardToolCall('serena', 'find_symbol', {
      name_path: 'TestClass',
      relative_path: 'test.py'
    });

    // Should get same result as direct mcp__serena__find_symbol call
    expect(result).to.have.property('symbols');
  });
});
```

### 2. Integration Tests

**File**: `syntropy-mcp/tests/test_integration.ts`

Test all 46 tools accessible via syntropy namespace:

```typescript
describe('Syntropy Integration', () => {
  // Serena tools (9 tests)
  it('syntropy:serena:find_symbol works', async () => { /* ... */ });
  it('syntropy:serena:get_symbols_overview works', async () => { /* ... */ });

  // Filesystem tools (9 tests)
  it('syntropy:filesystem:read_text_file works', async () => { /* ... */ });
  it('syntropy:filesystem:write_file works', async () => { /* ... */ });

  // Git tools (5 tests)
  it('syntropy:git:status works', async () => { /* ... */ });
  it('syntropy:git:diff works', async () => { /* ... */ });

  // ... etc for all 46 tools
});
```

### 3. Performance Tests

**File**: `syntropy-mcp/tests/test_performance.ts`

Measure latency overhead of syntropy layer:

```typescript
describe('Syntropy Performance', () => {
  it('should add <50ms latency overhead', async () => {
    const direct_start = Date.now();
    await directMcpCall('mcp__serena__find_symbol', args);
    const direct_duration = Date.now() - direct_start;

    const syntropy_start = Date.now();
    await syntropyCall('syntropy:serena:find_symbol', args);
    const syntropy_duration = Date.now() - syntropy_start;

    const overhead = syntropy_duration - direct_duration;
    expect(overhead).to.be.lessThan(50); // <50ms acceptable
  });
});
```

### 4. Documentation Generation Tests

**File**: `syntropy-mcp/tests/test_tool_index.py`

```python
import pytest
from pathlib import Path
from scripts.generate_tool_index import generate_markdown_docs

def test_tool_index_generation():
    """Ensure tool-index.md is generated correctly."""
    # Run generation script
    main()

    # Verify file exists
    index_path = Path("syntropy-mcp/tool-index.md")
    assert index_path.exists()

    # Verify content structure
    content = index_path.read_text()
    assert "# Syntropy MCP Tool Index" in content
    assert "## syntropy:serena" in content
    assert "## syntropy:filesystem" in content

    # Verify all 46 tools documented
    tool_count = content.count("###")
    assert tool_count >= 46

def test_tool_metadata_extraction():
    """Ensure metadata extracted from all servers."""
    tools = extract_tool_metadata("serena")

    # Verify structure
    assert len(tools) > 0
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "parameters" in tool
```

## Other Considerations

### Backward Compatibility

**Migration Strategy**:
1. **Phase 1**: Allow both syntropy:* and mcp__* (parallel access)
2. **Phase 2**: Test all workflows via syntropy namespace
3. **Phase 3**: Deny mcp__* access (force syntropy, opt-in)
4. **Phase 4**: Remove deny rules after full adoption

**No Breaking Changes**:
- All tools preserve exact same parameters
- Return types unchanged
- Error handling identical
- Performance impact minimal (<50ms overhead)

### Tool Discovery

**Auto-Generated Documentation**:
- `tool-index.md` updated from live MCP servers
- Regenerate on MCP server updates
- Include in version control for offline reference

**Search and Browse**:
```bash
# Find all filesystem tools
grep "syntropy:filesystem:" syntropy-mcp/tool-index.md

# Search for specific functionality
grep -i "read file" syntropy-mcp/tool-index.md
```

### Security Considerations

**Namespace Isolation**:
- Syntropy server validates tool format before forwarding
- Invalid formats rejected with clear error messages
- No shell metacharacters in tool names (enforced by MCP SDK)

**Access Control**:
- Permissions still enforced at syntropy level
- Can deny specific syntropy:server:tool patterns
- Underlying MCP servers still perform own validation

### Scalability

**Connection Pooling**:
- Syntropy maintains persistent connections to underlying servers
- Reuses connections across multiple tool calls
- Graceful degradation if server unavailable

**Future Extensions**:
- Add caching layer for read-only operations
- Implement batch tool calls (syntropy:batch:call)
- Support tool composition (syntropy:compose:pipeline)

### Documentation Maintenance

**Auto-Update Workflow**:
```bash
# Update tool index when MCP servers change
cd syntropy-mcp
python scripts/generate-tool-index.py

# Commit updated docs
git add tool-index.md
git commit -m "docs: update tool index from MCP servers"
```

**CI/CD Integration**:
```yaml
# .github/workflows/update-tool-index.yml
name: Update Tool Index
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Generate tool index
        run: |
          cd syntropy-mcp
          python scripts/generate-tool-index.py
      - name: Commit changes
        run: |
          git config user.name "github-actions"
          git commit -am "docs: auto-update tool index" || exit 0
          git push
```

## Validation Gates

### Pre-Implementation
- [x] MCP server inventory completed (8 servers, 46+ tools)
- [x] Namespace structure designed (syntropy:server:tool)
- [x] Tool routing logic planned
- [x] Documentation generation approach defined

### During Implementation (Phase 1: Tool Index)
- [ ] `generate-tool-index.py` script created
- [ ] MCP server introspection implemented
- [ ] tool-index.md generated successfully
- [ ] All 46+ tools documented with parameters
- [ ] Documentation tests pass

### During Implementation (Phase 2: MCP Server)
- [ ] Syntropy TypeScript MCP server scaffolded
- [ ] Tool name parsing implemented (syntropy:server:tool)
- [ ] Server routing logic working
- [ ] Connection pooling implemented
- [ ] Error handling with troubleshooting guidance
- [ ] Build succeeds (npm run build)

### During Implementation (Phase 3: Integration)
- [ ] mcp.json configuration created
- [ ] settings.local.json updated (parallel access mode)
- [ ] All 46 tools accessible via syntropy namespace
- [ ] Integration tests pass (100% tool coverage)
- [ ] Performance tests pass (<50ms overhead)

### Post-Implementation
- [ ] Full test suite passes (routing, integration, performance)
- [ ] Documentation complete (tool-index.md + README)
- [ ] Manual testing of all tool categories
- [ ] Migration guide written
- [ ] Performance benchmarks documented
- [ ] Code review approval
- [ ] Optional: Migrate to syntropy-only access (deny mcp__*)

## Success Criteria
- ✅ All 46+ MCP tools accessible via syntropy:* namespace
- ✅ tool-index.md auto-generated from live servers
- ✅ Zero functionality regression (all tools work identically)
- ✅ Performance overhead <50ms per tool call
- ✅ Clear namespace hierarchy (syntropy:server:tool)
- ✅ Comprehensive test coverage (routing, integration, performance)
- ✅ Documentation complete and up-to-date
- ✅ Migration path defined (backward compatible)

---

## Peer Review Notes

**Status**: Pending initial review

**Questions for Reviewer**:
1. TypeScript vs Python for MCP server implementation?
2. Should we support syntropy:batch:call for multiple tools in one request?
3. Connection pooling strategy - persistent vs on-demand?
4. Caching layer for read-only operations worth the complexity?
5. Migration timeline - how long to maintain parallel mcp__* access?

**Known Limitations**:
- Requires MCP SDK knowledge for server implementation
- Tool index generation needs MCP introspection API research
- Performance overhead depends on connection pooling efficiency
- Migration effort for existing workflows using mcp__* directly
