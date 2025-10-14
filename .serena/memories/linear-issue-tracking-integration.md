# Linear Issue Tracking Integration Pattern

## Overview

Pattern for integrating Linear issue tracking with PRP (Product Requirements Proposal) YAML headers, enabling bi-directional sync between PRPs and Linear project management.

## Implementation Pattern

### 1. PRP Discovery and Analysis

Use Python to parse PRP YAML headers and identify which PRPs lack Linear issue tracking:

```python
import re
from pathlib import Path

def extract_yaml_header(file_path):
    """Extract YAML header from markdown file."""
    with open(file_path, 'r') as f:
        content = f.read()
    match = re.search(r'^---\n(.*?)\n---', content, re.DOTALL | re.MULTILINE)
    return match.group(1) if match else None

def has_linear_tracking(yaml_content):
    """Check if PRP has Linear issue tracking."""
    if not yaml_content:
        return False
    # Check for issue, task_id, or linear_issue fields
    return bool(re.search(r'(issue|task_id|linear_issue):\s*\S+', yaml_content))
```

### 2. Linear Issue Creation

Use Linear MCP server to create issues with PRP metadata:

```python
# Create Linear issue
issue_result = mcp__linear-server__create_issue(
    team="team-key",  # e.g., "Blaise78"
    title=prp_title,
    description=prp_description,
    # Optional: labels, priority, assignee
)

# Extract issue details
issue_id = issue_result["id"]  # UUID for updates
issue_number = issue_result["number"]  # Display number (e.g., 17)
issue_key = issue_result["identifier"]  # Full key (e.g., "BLA-17")
```

### 3. YAML Header Update

Update PRP files with issue tracking information:

```python
# Add issue field to YAML header
Edit(
    file_path=prp_path,
    old_string="prp_id: PRP-X\nfeature_name: ...",
    new_string="prp_id: PRP-X\nfeature_name: ...\nissue: BLA-17"
)
```

### 4. Issue Assignment and Project Management

```python
# Assign to user
mcp__linear-server__update_issue(
    id=issue_uuid,  # IMPORTANT: Use UUID, not issue_number
    assignee="user@example.com"
)

# Add to project
mcp__linear-server__update_issue(
    id=issue_uuid,
    project="project-uuid"  # Get from list_projects
)
```

### 5. Bulk Updates

For updating multiple issues, use parallel tool calls:

```python
# Get project ID first
projects = mcp__linear-server__list_projects()
project_id = next(p["id"] for p in projects if p["name"] == "Context Engineering")

# Batch update all issues in parallel
for issue in issues:
    mcp__linear-server__update_issue(
        id=issue["id"],
        assignee="user@example.com",
        project=project_id
    )
```

## Key Learnings

### Linear API Behavior

1. **UUID vs Issue Number**: The `update_issue` tool requires the UUID `id` parameter, NOT `issue_number`. Always use the UUID from `create_issue` response.

2. **Project and User Assignment**: Both can be done in same update call or separately.

3. **Issue Identifiers**: 
   - `id`: UUID for API calls (e.g., "fd201036-0eb4-4822-a9d8-c03cd56ab9e6")
   - `number`: Display number (e.g., 17)
   - `identifier`: Team key + number (e.g., "BLA-17")

### PRP YAML Structure

Standard PRP YAML header with Linear tracking:

```yaml
---
prp_id: PRP-13
feature_name: Production Hardening & Comprehensive Documentation
status: partial
issue: BLA-23
created: 2025-10-13
updated: 2025-10-14T15:30:00Z
context_sync:
  ce_updated: true
  serena_updated: true
  last_sync: 2025-10-14T15:30:00Z
updated_by: context-sync
---
```

## Error Handling

### Common Errors

1. **Invalid Arguments - Missing 'id' field**:
   ```
   MCP error -32602: Invalid arguments for tool update_issue
   ```
   **Fix**: Use UUID `id` parameter instead of `issue_number`

2. **Team Not Found**:
   Ensure team key matches exactly (case-sensitive)

3. **Project Not Found**:
   Use `list_projects` to get exact project UUID

## Workflow Example

Complete workflow for creating Linear issues for untracked PRPs:

```python
# 1. Discover PRPs without issues
prp_files = Path("PRPs").rglob("*.md")
untracked_prps = []

for prp_file in prp_files:
    yaml_header = extract_yaml_header(prp_file)
    if not has_linear_tracking(yaml_header):
        untracked_prps.append(prp_file)

# 2. Extract titles using bash/awk
for prp_file in untracked_prps:
    title = extract_h1_title(prp_file)
    # awk '/^---$/{p++; next} p==2 && /^#[^#]/{print; exit}' file

# 3. Create Linear issues
created_issues = []
for prp_file, title in zip(untracked_prps, titles):
    issue = mcp__linear-server__create_issue(
        team="Blaise78",
        title=title
    )
    created_issues.append((prp_file, issue))

# 4. Update PRP YAML headers
for prp_file, issue in created_issues:
    Edit(prp_file, add_issue_field(issue["identifier"]))

# 5. Assign and organize
project_id = get_project_id("Context Engineering")
for _, issue in created_issues:
    mcp__linear-server__update_issue(
        id=issue["id"],  # UUID
        assignee="user@example.com",
        project=project_id
    )
```

## Context Sync Integration

After updating PRPs with Linear tracking, update context_sync flags:

```yaml
context_sync:
  ce_updated: true
  serena_updated: true
  last_sync: 2025-10-14T15:30:00Z
updated_by: context-sync
```

This ensures drift tracking recognizes the changes as intentional.

## Related Documentation

- Linear MCP Server: Uses `mcp__linear-server__*` tools
- PRP Model: See PRPs/Model.md for YAML header specification
- Context Sync: See /update-context command for drift management

---

Last updated: 2025-10-14
Pattern validated: 7 PRPs successfully integrated with Linear tracking
