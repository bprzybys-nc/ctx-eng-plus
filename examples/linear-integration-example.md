# Linear MCP Integration - Example

Demonstrates Linear MCP integration using configuration defaults, Python utilities, and MCP tools for issue tracking in Context Engineering projects.

## Quick Start

### 1. Configuration

**File**: `.ce/linear-defaults.yml`

```yaml
project: "Context Engineering"
assignee: "blazej.przybyszewski@gmail.com"
team: "Blaise78"
default_labels:
  - "feature"
```

### 2. Create Issue with Defaults

```python
from ce.linear_utils import create_issue_with_defaults

# Auto-applies defaults from config
issue_data = create_issue_with_defaults(
    title="PRP-15: New Feature",
    description="""## Feature
Implement feature X for Context Engineering.

## Deliverables
✅ Core implementation
✅ Tests (≥80% coverage)
✅ Documentation
""",
    state="todo"
)

# Create via MCP
issue = mcp__linear__create_issue(**issue_data)
print(f"Created: {issue['identifier']}")  # "BLA-15"
```

### 3. Direct MCP Usage (Full Control)

```python
# When you need to override defaults
issue = mcp__linear__create_issue(
    team="Blaise78",
    title="PRP-16: Bug Fix",
    description="Fix authentication token handling",
    priority=1,  # 1=Urgent, 2=High, 3=Normal, 4=Low
    labels=["bug", "security"],
    project="Context Engineering",
    assignee="blazej.przybyszewski@gmail.com",
    state="in_progress"
)
```

## Troubleshooting MCP Connection

### Level 1: Check Status
```bash
/mcp
```

### Level 2: Restart
```bash
/mcp restart linear-server
```

### Level 3: Re-authenticate
```bash
rm -rf ~/.mcp-auth
mcp-remote https://mcp.linear.app/sse  # Opens browser

# Expected output (HTTP 404 is normal - uses SSE fallback):
# [PID] Received error: Error POSTing to endpoint (HTTP 404): Not Found
# [PID] Recursively reconnecting for reason: falling-back-to-alternate-transport
# [PID] Connected to remote server using SSEClientTransport
# [PID] Proxy established successfully ✅

# Restart Claude Code to activate
```

### Level 4: Reinstall
```bash
npm install -g mcp-remote
mcp-remote https://mcp.linear.app/sse
claude mcp add --transport sse linear-server https://mcp.linear.app/sse
```

## Anti-Patterns

```python
# ❌ BAD: Hardcoded values
issue = mcp__linear__create_issue(
    team="Blaise78",  # Hardcoded
    assignee="user@example.com",  # Hardcoded
    project="Context Engineering",  # Hardcoded
    labels=["feature"],  # Hardcoded
    title="...",
    description="..."
)

# ❌ BAD: Silent failures
try:
    issue = mcp__linear__create_issue(...)
    print("✅ Success")  # FAKE!
except:
    pass  # Silent failure
```

## Best Practices

```python
# ✅ GOOD: Use defaults helper
from ce.linear_utils import create_issue_with_defaults

issue_data = create_issue_with_defaults(
    title="...",
    description="..."
)
issue = mcp__linear__create_issue(**issue_data)

# ✅ GOOD: Explicit error handling
try:
    issue = mcp__linear__create_issue(**issue_data)
    print(f"✅ Created: {issue['identifier']}")
except Exception as e:
    print(f"❌ Failed: {e}")
    print(f"🔧 Troubleshooting:")
    print(f"   1. Check MCP status: /mcp")
    print(f"   2. Verify config: cat .ce/linear-defaults.yml")
    raise
```

## Integration with PRPs

### Workflow

```python
# 1. Create issue
issue = mcp__linear__create_issue(**issue_data)

# 2. Update PRP YAML header
# ---
# issue: "BLA-18"
# project: "Context Engineering"
# ---

# 3. Track progress
issue_details = mcp__linear__get_issue(id=issue['id'])
print(f"Status: {issue_details['status']}")
```

### Auto-Creation in /generate-prp

```bash
# Creates new Linear issue automatically
/generate-prp examples/feature-INITIAL.md

# Join existing PRP's issue
/generate-prp examples/feature-INITIAL.md --join-prp 12
```

## Available MCP Tools

**Core Functions**:
- `mcp__linear__create_issue` - Create new issue
- `mcp__linear__list_issues` - Query issues
- `mcp__linear__get_issue` - Get issue details
- `mcp__linear__update_issue` - Modify existing issue
- `mcp__linear__create_comment` - Add comment to issue

**Other Tools**: Projects, teams, labels, statuses (20+ total)

## Utility Helpers

**Module**: `tools/ce/linear_utils.py`

```python
from ce.linear_utils import (
    get_linear_defaults,       # Load config
    get_default_assignee,      # Get assignee email
    get_default_project,       # Get project name
    create_issue_with_defaults # Prepare issue data
)

defaults = get_linear_defaults()
# {"project": "...", "assignee": "...", "team": "...", "default_labels": [...]}
```

## Summary

- **Config**: `.ce/linear-defaults.yml` centralizes project settings
- **Utilities**: `ce.linear_utils` simplifies issue creation
- **MCP Tools**: Direct control when needed
- **Troubleshooting**: Multi-level resolution for connection issues
- **PRP Integration**: Auto-sync issue tracking with PRP workflow

**References**:
- Linear MCP: https://linear.app/docs/mcp
- Project docs: CLAUDE.md (Linear Integration section)
- Implementation: `tools/ce/linear_utils.py`
