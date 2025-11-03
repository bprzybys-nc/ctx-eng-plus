# Linear Integration for Issue Tracking

Examples for using Linear MCP tools to create, update, and manage issues directly from Context Engineering workflows.

## Purpose

Linear MCP provides programmatic access to Linear issue tracking, enabling:

- **PRP-to-issue linking**: Auto-create Linear issues during PRP generation
- **Status synchronization**: Update issue status as PRPs progress
- **Query and reporting**: Fetch issue data for sprint planning and retrospectives
- **Team coordination**: Assign issues, set priorities, link to projects

**When to Use**:

- Auto-create issues during `/batch-gen-prp` or manual PRP generation
- Update issue status after PRP execution completes
- Query issues for sprint planning or progress tracking
- Link PRPs to existing Linear issues for traceability

**When NOT to Use**:

- Manual issue management in Linear UI is faster for one-off tasks
- Complex queries requiring Linear's full query language → Use Linear API directly
- Bulk operations across many issues → Use Linear CSV import/export

## Prerequisites

- Linear MCP server active (`/syntropy-health` to verify)
- Linear API key configured (`~/.mcp-auth` or environment variables)
- Team ID and project ID available
- Configuration file: `.ce/linear-defaults.yml`

## Configuration

### `.ce/linear-defaults.yml`

```yaml
# Linear integration defaults
project: "Context Engineering"
team_id: "Blaise78"
assignee: "blazej.przybyszewski@gmail.com"
default_status: "Todo"
default_priority: 3  # 1=Urgent, 2=High, 3=Medium, 4=Low
```

### Troubleshooting Auth

```bash
# If Linear shows "Not connected"
rm -rf ~/.mcp-auth

# Reconnect MCP servers
/mcp

# Verify connection
/syntropy-health
```

## Examples

### Example 1: Create Issue

**Use Case**: Create a Linear issue manually for a new PRP.

```python
# Create issue with minimal info
issue = mcp__syntropy__linear__create_issue(
    title="Implement user authentication",
    team_id="Blaise78",
    description="Add JWT-based authentication system"
)
```

**Output**:

```json
{
  "id": "CTX-123",
  "title": "Implement user authentication",
  "url": "https://linear.app/yourteam/issue/CTX-123",
  "status": "Todo",
  "assignee": null,
  "priority": 3
}
```

**With Full Details**:

```python
# Create issue with all metadata
issue = mcp__syntropy__linear__create_issue(
    title="Implement user authentication",
    team_id="Blaise78",
    description="## Summary\nAdd JWT-based authentication system\n\n## Acceptance Criteria\n- [ ] User login endpoint\n- [ ] Token validation middleware\n- [ ] Refresh token rotation",
    priority=2,  # High priority
    assignee_id="user_abc123",
    project_id="proj_xyz456",
    label_ids=["label_auth", "label_backend"]
)
```

### Example 2: Get Issue Details

**Use Case**: Fetch issue data to check status before updating.

```python
# Get issue by ID
issue = mcp__syntropy__linear__get_issue(
    issue_id="CTX-123"
)
```

**Output**:

```json
{
  "id": "CTX-123",
  "title": "Implement user authentication",
  "status": "In Progress",
  "assignee": {
    "id": "user_abc123",
    "name": "Blazej Przybyszewski",
    "email": "blazej.przybyszewski@gmail.com"
  },
  "priority": 2,
  "project": {
    "id": "proj_xyz456",
    "name": "Context Engineering"
  },
  "created_at": "2025-11-03T12:00:00Z",
  "updated_at": "2025-11-03T14:30:00Z",
  "url": "https://linear.app/yourteam/issue/CTX-123"
}
```

### Example 3: Update Issue Status

**Use Case**: Mark issue as "In Progress" when PRP execution starts, "Done" when complete.

```python
# Update issue status to In Progress
result = mcp__syntropy__linear__update_issue(
    issue_id="CTX-123",
    updates={
        "status": "In Progress",
        "assignee_id": "user_abc123"
    }
)

# Later: Mark as Done
result = mcp__syntropy__linear__update_issue(
    issue_id="CTX-123",
    updates={
        "status": "Done"
    }
)
```

**Output**:

```json
{
  "success": true,
  "issue_id": "CTX-123",
  "updated_fields": ["status", "assignee_id"]
}
```

### Example 4: List Issues

**Use Case**: Query issues for sprint planning or progress tracking.

```python
# List all issues in Todo status
issues = mcp__syntropy__linear__list_issues(
    team_id="Blaise78",
    status="Todo"
)

# List all issues (no filter)
all_issues = mcp__syntropy__linear__list_issues()
```

**Output**:

```json
{
  "issues": [
    {
      "id": "CTX-123",
      "title": "Implement user authentication",
      "status": "Todo",
      "priority": 2,
      "assignee": "Blazej Przybyszewski"
    },
    {
      "id": "CTX-124",
      "title": "Add rate limiting",
      "status": "Todo",
      "priority": 3,
      "assignee": null
    }
  ],
  "total": 2
}
```

### Example 5: List Teams

**Use Case**: Find team ID for issue creation.

```python
# List all teams
teams = mcp__syntropy__linear__list_teams()
```

**Output**:

```json
{
  "teams": [
    {
      "id": "Blaise78",
      "name": "Engineering",
      "key": "ENG"
    },
    {
      "id": "team_abc",
      "name": "Design",
      "key": "DES"
    }
  ]
}
```

### Example 6: PRP-to-Issue Linking

**Use Case**: Store Linear issue ID in PRP frontmatter for traceability.

```python
# Step 1: Create issue
issue = mcp__syntropy__linear__create_issue(
    title="PRP-32: Examples Completion & Index Creation",
    team_id="Blaise78",
    description="Complete examples directory with Syntropy integration"
)

# Step 2: Store issue ID in PRP frontmatter
# (Done automatically by /batch-gen-prp or /generate-prp)
# Frontmatter format:
# ---
# prp_id: 32
# issue: CTX-123
# status: pending
# ---

# Step 3: Update issue when PRP execution completes
result = mcp__syntropy__linear__update_issue(
    issue_id="CTX-123",
    updates={"status": "Done"}
)
```

### Example 7: Batch Issue Creation

**Use Case**: Create issues for all PRPs in a batch generation workflow.

```python
# During batch PRP generation
prps = [
    ("PRP-43.1.1", "Implement validation gates"),
    ("PRP-43.2.1", "Add error recovery"),
    ("PRP-43.2.2", "Create test suite")
]

issue_ids = {}
for prp_id, title in prps:
    issue = mcp__syntropy__linear__create_issue(
        title=f"{prp_id}: {title}",
        team_id="Blaise78",
        description=f"Auto-generated for {prp_id}"
    )
    issue_ids[prp_id] = issue['id']
    # Write issue ID to PRP frontmatter
```

**Output**: 3 Linear issues created, each linked to corresponding PRP.

## Common Patterns

### Pattern 1: PRP Lifecycle Integration

Track PRP progress through Linear issue status:

```python
# 1. PRP Generation: Create issue
issue = mcp__syntropy__linear__create_issue(
    title=f"PRP-{prp_id}: {feature_name}",
    team_id=team_id,
    description=prp_summary
)

# 2. PRP Execution Start: Update status
mcp__syntropy__linear__update_issue(
    issue_id=issue['id'],
    updates={"status": "In Progress"}
)

# 3. PRP Execution Complete: Mark done
mcp__syntropy__linear__update_issue(
    issue_id=issue['id'],
    updates={"status": "Done"}
)

# 4. Validation Failure: Add comment
mcp__syntropy__linear__update_issue(
    issue_id=issue['id'],
    updates={
        "status": "Todo",
        "comment": "Validation L3 failed: Integration tests failing"
    }
)
```

### Pattern 2: Sprint Planning Workflow

Query issues for sprint planning:

```python
# 1. Fetch all Todo issues
todo_issues = mcp__syntropy__linear__list_issues(
    team_id="Blaise78",
    status="Todo"
)

# 2. Group by priority
high_priority = [i for i in todo_issues['issues'] if i['priority'] <= 2]
medium_priority = [i for i in todo_issues['issues'] if i['priority'] == 3]

# 3. Assign to sprint
for issue in high_priority[:5]:  # Top 5 high-priority
    mcp__syntropy__linear__update_issue(
        issue_id=issue['id'],
        updates={
            "assignee_id": "user_abc123",
            "project_id": "sprint_2025_11"
        }
    )
```

### Pattern 3: Batch PRP Auto-Linking

During batch PRP generation, auto-create and link Linear issues:

```bash
# /batch-gen-prp uses this pattern internally:
```

```python
# 1. Parse plan document
phases = parse_plan_document(plan_path)

# 2. Create Linear issues for each phase
for phase in phases:
    issue = mcp__syntropy__linear__create_issue(
        title=f"PRP-{batch_id}.{stage}.{order}: {phase['name']}",
        team_id=defaults['team_id'],
        description=phase['summary']
    )

    # 3. Write issue ID to PRP frontmatter
    prp_content = f"""---
prp_id: {batch_id}.{stage}.{order}
issue: {issue['id']}
status: pending
---

# {phase['name']}
...
"""
    Write(file_path=prp_path, content=prp_content)
```

### Pattern 4: Issue Query for Reporting

Generate progress reports by querying Linear:

```python
# 1. Fetch all issues for project
all_issues = mcp__syntropy__linear__list_issues()

# 2. Filter by project
project_issues = [
    i for i in all_issues['issues']
    if i.get('project', {}).get('name') == "Context Engineering"
]

# 3. Group by status
report = {
    "Todo": [i for i in project_issues if i['status'] == 'Todo'],
    "In Progress": [i for i in project_issues if i['status'] == 'In Progress'],
    "Done": [i for i in project_issues if i['status'] == 'Done']
}

# 4. Output summary
print(f"Total: {len(project_issues)}")
print(f"Todo: {len(report['Todo'])}")
print(f"In Progress: {len(report['In Progress'])}")
print(f"Done: {len(report['Done'])}")
```

### Pattern 5: Error Recovery with Issue Comments

When PRP execution fails, update issue with diagnostic info:

```python
try:
    # Execute PRP
    result = execute_prp(prp_path)
except ValidationError as e:
    # Update Linear issue with error details
    mcp__syntropy__linear__update_issue(
        issue_id=prp_issue_id,
        updates={
            "status": "Todo",
            "comment": f"Validation failed:\n```\n{e.details}\n```\n\n🔧 Next steps:\n- Review validation output\n- Fix failing tests\n- Re-run validation"
        }
    )
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Creating Issues Without Team ID

**Bad**:

```python
# DON'T create issue without team_id
issue = mcp__syntropy__linear__create_issue(
    title="Fix bug"
    # Missing team_id → Will fail
)
```

**Good**:

```python
# DO specify team_id (required)
issue = mcp__syntropy__linear__create_issue(
    title="Fix bug",
    team_id="Blaise78"  # Always required
)
```

**Why**: `team_id` is required by Linear API. Use `list_teams()` to find your team ID.

### ❌ Anti-Pattern 2: Not Checking Issue ID Before Update

**Bad**:

```python
# DON'T assume issue ID format
issue_id = "123"  # Wrong format
mcp__syntropy__linear__update_issue(
    issue_id=issue_id,
    updates={"status": "Done"}
)
# Will fail: Invalid issue ID
```

**Good**:

```python
# DO use full issue ID from creation or get_issue
issue = mcp__syntropy__linear__create_issue(...)
issue_id = issue['id']  # "CTX-123" format

mcp__syntropy__linear__update_issue(
    issue_id=issue_id,
    updates={"status": "Done"}
)
```

**Why**: Linear issue IDs have specific format (team key + number). Always use the ID returned by API.

### ❌ Anti-Pattern 3: Hardcoding Team/Project IDs

**Bad**:

```python
# DON'T hardcode IDs in code
issue = mcp__syntropy__linear__create_issue(
    title="New feature",
    team_id="Blaise78",  # Hardcoded
    project_id="proj_xyz456"  # Hardcoded
)
```

**Good**:

```python
# DO use configuration file
import yaml

with open(".ce/linear-defaults.yml") as f:
    config = yaml.safe_load(f)

issue = mcp__syntropy__linear__create_issue(
    title="New feature",
    team_id=config['team_id'],
    project_id=config.get('project_id')
)
```

**Why**: Team/project IDs change across environments. Use config file for portability.

## Related Examples

- [serena-symbol-search.md](serena-symbol-search.md) - Code navigation for PRP implementation
- [context7-docs-fetch.md](context7-docs-fetch.md) - Documentation for issue descriptions
- [../workflows/batch-prp-generation.md](../workflows/batch-prp-generation.md) - Auto-issue creation during batch gen
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - When to use Linear vs manual issue management

## Troubleshooting

### Issue: "Linear not connected" error

**Cause**: MCP auth token missing or expired

**Solution**:

```bash
# Clear auth cache
rm -rf ~/.mcp-auth

# Reconnect MCP servers
/mcp

# Verify Linear connection
/syntropy-health
```

### Issue: "Team not found" error

**Symptom**: Create issue fails with "Team ID not found"

**Solution**: Verify team ID with `list_teams()`:

```python
# List all teams
teams = mcp__syntropy__linear__list_teams()

# Find your team
for team in teams['teams']:
    print(f"{team['name']}: {team['id']}")
```

### Issue: Issue status not updating

**Symptom**: `update_issue()` succeeds but status unchanged

**Cause**: Status name mismatch (e.g., "Done" vs "Completed")

**Solution**: Check team's status names in Linear UI, use exact match:

```python
# Check current status first
issue = mcp__syntropy__linear__get_issue(issue_id="CTX-123")
print(f"Current status: {issue['status']}")

# Use exact status name from your team's workflow
mcp__syntropy__linear__update_issue(
    issue_id="CTX-123",
    updates={"status": "Done"}  # Must match team's status name exactly
)
```

## Performance Tips

1. **Batch issue creation**: Create all issues upfront during batch PRP generation
2. **Cache team/project IDs**: Query once, reuse across session
3. **Use defaults file**: Store team_id, project_id in `.ce/linear-defaults.yml`
4. **Update minimally**: Only update fields that changed (not entire issue)
5. **Query with filters**: Use `status` parameter in `list_issues()` to reduce result size

## Resources

- Linear API Documentation: https://developers.linear.app/docs/graphql/working-with-the-graphql-api
- Linear MCP Server: Syntropy aggregator integration
- Configuration: `.ce/linear-defaults.yml`
- Syntropy Health: `/syntropy-health` slash command
