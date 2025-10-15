# Linear MCP Integration - Pattern Example

## Quick Reference

**Config**: `.ce/linear-defaults.yml` - Project defaults (team, assignee, labels)
**Utilities**: `tools/ce/linear_utils.py` - Helper functions
**MCP Tools**: `mcp__linear__*` - Direct Linear API access

## Core Patterns

### 1. Configuration-Driven

```yaml
# .ce/linear-defaults.yml
project: "Context Engineering"
assignee: "blazej.przybyszewski@gmail.com"
team: "Blaise78"
default_labels: ["feature"]
```

### 2. Python Utilities (Recommended)

```python
from ce.linear_utils import create_issue_with_defaults

# Auto-applies config defaults
issue_data = create_issue_with_defaults(
    title="PRP-15: Feature",
    description="...",
    state="todo"
)
issue = mcp__linear__create_issue(**issue_data)
```

### 3. Direct MCP (Full Control)

```python
# Override defaults when needed
issue = mcp__linear__create_issue(
    team="Blaise78",
    title="...",
    priority=1,  # Urgent
    labels=["bug", "security"],
    project="...",
    assignee="...",
    state="in_progress"
)
```

## Troubleshooting Flow

**L1**: `/mcp` (check status)
**L2**: `/mcp restart linear-server`
**L3**: `rm -rf ~/.mcp-auth && mcp-remote https://mcp.linear.app/sse`
  - **Expected**: HTTP 404 error during connection (normal!)
  - `mcp-remote` tries HTTP first, fails with 404, falls back to SSE
  - Final message: "Proxy established successfully" = ✅ working
**L4**: Reinstall MCP tools

## Anti-Patterns

❌ Hardcoded team/project/assignee values
❌ Silent exception handling
❌ Manual YAML editing without parsing

## Best Practices

✅ Use `create_issue_with_defaults()` helper
✅ Explicit error handling with troubleshooting steps
✅ Proper YAML parsing for header updates
✅ Test MCP connection before batch operations

## PRP Integration

**Auto-creation**: `/generate-prp` creates Linear issues automatically
**Joining**: `--join-prp 12` appends to existing issue
**Tracking**: YAML header `issue: "BLA-18"` field

## Available Tools

**Issues**: create, list, get, update
**Comments**: create, list
**Projects/Teams/Labels**: list, get, create
**Documentation**: search_documentation

20+ MCP tools available with `mcp__linear__` prefix.

## MCP Connection Notes

**Transport Strategy**: Linear MCP uses SSE (Server-Sent Events)
**HTTP 404 on connect**: Normal - `mcp-remote` tries HTTP first, then falls back to SSE
**OAuth Flow**: Browser-based authentication, stored in `~/.mcp-auth`
**Connection Stability**: Early tech - may need multiple attempts

## File Locations

- Config: `.ce/linear-defaults.yml`
- Utilities: `tools/ce/linear_utils.py`
- Example: `examples/linear-integration-example.md`
- Docs: CLAUDE.md (Linear Integration section)
