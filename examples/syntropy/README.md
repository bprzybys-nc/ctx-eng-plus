# Syntropy MCP Integration Examples

Comprehensive examples for using Syntropy MCP tools within the Context Engineering framework.

## Purpose

Syntropy MCP is an aggregation server that provides unified access to multiple MCP servers (Serena, Context7, Thinking, Linear, etc.) through a single connection. These examples demonstrate how to effectively use Syntropy tools for code analysis, documentation fetching, complex reasoning, and project management.

## Available Syntropy Servers

| Server | Tools | Purpose |
|--------|-------|---------|
| **Serena** | 11 tools | Code symbol navigation, memory management, file operations |
| **Context7** | 2 tools | Library documentation fetching and resolution |
| **Thinking** | 1 tool | Sequential reasoning for complex problems |
| **Linear** | 9 tools | Issue tracking and project management |
| **Filesystem** | 8 tools | File operations (mostly denied, use native tools) |
| **Git** | 5 tools | Git operations (denied, use Bash(git:*)) |
| **GitHub** | 26 tools | GitHub operations (denied, use Bash(gh:*)) |

**Note**: Many Syntropy tools are denied in favor of native Claude Code tools for better performance and token efficiency. See [TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) for the complete tool selection strategy.

## Tool Naming Convention

All Syntropy tools follow this format:

```
mcp__syntropy__{server}__{function}
```

**Examples**:

- `mcp__syntropy__serena__find_symbol` - Find symbol definitions
- `mcp__syntropy__context7__get_library_docs` - Fetch library documentation
- `mcp__syntropy__thinking__sequentialthinking` - Sequential reasoning
- `mcp__syntropy__linear__create_issue` - Create Linear issue

**Important**: Use double underscores (`__`) between components, not single underscores.

## When to Use Syntropy Tools vs Native Tools

### ✅ Use Syntropy Tools For

| Task | Syntropy Tool | Why |
|------|---------------|-----|
| Find symbol definition | `serena_find_symbol` | Semantic code understanding |
| Get file symbols | `serena_get_symbols_overview` | AST-based symbol extraction |
| Search code patterns | `serena_search_for_pattern` | Regex + semantic search |
| Find symbol references | `serena_find_referencing_symbols` | Cross-file reference tracking |
| Manage memories | `serena_write_memory`, `serena_read_memory` | Persistent knowledge storage |
| Fetch library docs | `context7_get_library_docs` | Official docs with context |
| Complex reasoning | `thinking_sequentialthinking` | Multi-step thought process |
| Linear integration | `linear_create_issue`, etc. | Project management |

### ❌ Use Native Tools Instead

| Task | Native Tool | Why |
|------|-------------|-----|
| Read files | `Read` | Faster, no MCP overhead |
| Edit files | `Edit` | Surgical changes, better control |
| Write files | `Write` | Direct file creation |
| Search files | `Grep` | Native ripgrep, very fast |
| Find files | `Glob` | Pattern matching, instant |
| Git operations | `Bash(git:*)` | Direct git CLI access |
| GitHub operations | `Bash(gh:*)` | GitHub CLI, full features |

**Rule of Thumb**: Use Syntropy when you need **semantic understanding** or **specialized integrations**. Use native tools for **file operations** and **shell commands**.

## Examples in This Directory

1. **[serena-symbol-search.md](serena-symbol-search.md)** - Symbol navigation patterns
2. **[context7-docs-fetch.md](context7-docs-fetch.md)** - Library documentation fetching
3. **[thinking-sequential.md](thinking-sequential.md)** - Complex reasoning patterns
4. **[linear-integration.md](linear-integration.md)** - Issue tracking integration
5. **[memory-management.md](memory-management.md)** - Serena memory usage

## Quick Start

```python
# Find a symbol in the codebase
result = mcp__syntropy__serena__find_symbol(name_path="MyClass.my_method")

# Fetch library documentation
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="routing"
)

# Use sequential thinking for complex problems
mcp__syntropy__thinking__sequentialthinking(
    thought="Need to analyze the trade-offs between approach A and B",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Create a Linear issue
issue = mcp__syntropy__linear__create_issue(
    title="Fix authentication bug",
    team_id="TEAM-123",
    description="Users unable to login after recent update"
)
```

## Configuration

### Syntropy MCP Server

- **Location**: `~/.syntropy/` or project-specific configuration
- **Tool State**: `~/.syntropy/tool-state.json` (enabled/disabled tools)
- **Health Check**: `/syntropy-health` slash command

### Tool Permissions

Tools can be enabled/disabled dynamically via:

```bash
# Via Syntropy tool
mcp__syntropy__enable_tools(
    enable=["serena_find_symbol"],
    disable=["filesystem_read_file"]
)

# Sync with Claude Code settings
/sync-with-syntropy
```

See [../config/slash-command-template.md](../config/slash-command-template.md) for more on slash commands.

## Troubleshooting

### Issue: "Tool not found" or "Tool denied"

**Solution**: Check if tool is in deny list

```bash
# Check tool permissions
grep "mcp__syntropy__" .claude/settings.local.json

# See denied tools list
cat examples/TOOL-USAGE-GUIDE.md
```

### Issue: Syntropy MCP not responding

**Solution**: Check server health

```bash
# Via slash command
/syntropy-health

# Via CLI
cd tools && uv run ce context health
```

### Issue: "Connection refused" errors

**Solution**: Reconnect MCP servers

1. Restart Claude Code
2. Run `/mcp` to reconnect servers
3. Verify with `/syntropy-health`

## Performance Considerations

### Token Usage

Syntropy tools add overhead compared to native tools:

- **Serena tools**: ~200-500 tokens per call (symbol search, overview)
- **Context7 tools**: ~1000-5000 tokens per call (docs fetching)
- **Thinking tool**: ~500-1000 tokens per thought step
- **Linear tools**: ~100-300 tokens per call

**Optimization**: Use Syntropy tools strategically, not for every operation. Combine with native tools for efficiency.

### Response Time

- **Serena**: 100-500ms (local code analysis)
- **Context7**: 1-3s (external API calls)
- **Thinking**: 500ms-1s per thought
- **Linear**: 500ms-2s (API calls)

**Tip**: Batch operations where possible (e.g., read multiple memories in one session).

## Related Documentation

- [TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - Complete tool selection guide
- [SystemModel.md](../model/SystemModel.md) - Framework architecture
- [workflows/](../workflows/) - Workflow examples using Syntropy tools
- `.claude/commands/syntropy-health.md` - Health check command
- `.claude/commands/sync-with-syntropy.md` - Tool sync command

## Contributing

When adding new Syntropy examples:

1. Follow the content template (see PRP-32)
2. Include Purpose, Prerequisites, Examples, Common Patterns, Anti-Patterns, Related
3. Add 3-4 concrete code examples with input/output
4. Update INDEX.md with new entry
5. Cross-link with related examples

## Resources

- **Syntropy MCP Docs**: See project `.ce/SYNTROPY-SUMMARY.md`
- **MCP Protocol**: https://modelcontextprotocol.io
- **Claude Code Docs**: https://docs.claude.com/claude-code
