# Linear MCP Integration Guide

## Overview
Claude Code integrates with Linear via MCP (Model Context Protocol) for issue tracking automation.

## Setup (Already Configured)
Linear MCP is centrally hosted and uses OAuth 2.1 authentication.

**Configuration**:
```json
{
  "mcpServers": {
    "linear": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://mcp.linear.app/sse"]
    }
  }
}
```

**Authentication**: Run `/mcp` in Claude Code session to authenticate via OAuth flow.

## Available Tools (Prefix: mcp__linear__)

### Issues
- `list_issues` - List/filter issues (assignee, status, project, team, labels, etc.)
- `get_issue` - Get detailed issue info by ID
- `create_issue` - Create new issue (title, description, team, assignee, labels, etc.)
- `update_issue` - Update existing issue fields

### Projects
- `list_projects` - List/filter projects (team, member, state, etc.)
- `get_project` - Get project details
- `create_project` - Create new project
- `update_project` - Update project fields
- `list_project_labels` - List project labels

### Teams
- `list_teams` - List workspace teams
- `get_team` - Get team details by ID/key/name

### Comments
- `list_comments` - List issue comments
- `create_comment` - Add comment to issue

### Cycles
- `list_cycles` - Get team cycles (current/previous/next)

### Documents
- `list_documents` - List workspace documents
- `get_document` - Get document by ID/slug

### Issue Management
- `list_issue_statuses` - List available issue statuses for team
- `get_issue_status` - Get status details by name/ID
- `list_issue_labels` - List workspace/team labels
- `create_issue_label` - Create new label

### Users
- `list_users` - List workspace users
- `get_user` - Get user details (supports "me" for current user)

### Documentation
- `search_documentation` - Search Linear docs for features/usage

## Common Patterns

### Create Issue
```python
mcp__linear__create_issue(
    title="Feature title",
    description="Markdown description",
    team="team-key-or-id",
    assignee="me",  # or user ID/name/email
    priority=2,  # 0=None, 1=Urgent, 2=High, 3=Normal, 4=Low
    labels=["label-name-or-id"],
    project="project-name-or-id"
)
```

### List My Issues
```python
mcp__linear__list_issues(
    assignee="me",
    state="In Progress",
    orderBy="updatedAt",
    limit=50
)
```

### Update Issue
```python
mcp__linear__update_issue(
    id="issue-id",
    state="Done",
    description="Updated description"
)
```

## Troubleshooting
- **"Not connected" error**: Run `/mcp` to authenticate
- **Connection failures**: Try restarting Claude Code or disable/re-enable Linear MCP
- **Early tech**: Remote MCP connections may require multiple attempts

## Permission Configuration
All Linear tools require explicit permission in Claude Code settings:
- Pattern: `mcp__linear__*` for all tools
- Or individually: `mcp__linear__create_issue`, `mcp__linear__list_issues`, etc.

## References
- Linear MCP Docs: https://linear.app/docs/mcp
- MCP Integration: https://docs.claude.com/en/docs/claude-code/mcp
- OAuth Flow: Server-Sent Events (SSE) transport with OAuth 2.1
