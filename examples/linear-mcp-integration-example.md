# Linear Integration Example

This example demonstrates how to create Linear issues for PRPs and link them in YAML headers.

## Step 1: Create Linear Issue

```python
# Using Linear MCP tool
mcp__linear__create_issue(
    team="Blaise78",  # Your team name (NOT project name)
    title="PRP-1: Level 4 Pattern Conformance Validation",
    description="""# PRP-1: Level 4 Pattern Conformance Validation

**Status**: Ready
**PRP File**: PRPs/PRP-1-level-4-pattern-conformance.md

## Summary

Automated validation comparing implementation vs PRP EXAMPLES to detect architectural drift.

## Key Deliverables

✅ AST-based pattern extraction from EXAMPLES
✅ Serena MCP integration for code analysis
✅ Drift scoring (0-10% accept, 10-30% warn, 30%+ abort)
✅ CLI: `ce validate --level 4`

## Effort

* **Estimated**: 25.0h
* **Phases**: Research (5h), Core (12h), CLI (4h), Testing (4h)

## Files

* `tools/ce/validate.py` - Level 4 logic
* `tools/tests/test_validate_l4.py`

## Dependencies

None (foundation for validation pipeline)""",
    priority=2,  # 1=Urgent, 2=High, 3=Medium, 4=Low
    labels=["prp", "validation", "mvp"],
    project="Context Engineering"  # Project name as string
)
```

**Returns:**

```json
{
  "id": "eb0bd8b1-f5a5-4436-9297-9b40e64b411e",
  "identifier": "BLA-7",
  "title": "PRP-1: Level 4 Pattern Conformance Validation",
  "url": "https://linear.app/blaise78/issue/BLA-7/prp-1-level-4-pattern-conformance-validation",
  "status": "Backlog",
  "priority": {"value": 2, "name": "High"},
  "project": "Context Engineering",
  "projectId": "93db57b1-61c2-4a72-bf1d-d1140a09c2d9",
  "team": "Blaise78",
  "teamId": "4fd57d03-0b1f-4417-8428-827615de8f04"
}
```

## Step 2: Update PRP YAML Header

Add the Linear issue identifier to your PRP's YAML header:

```yaml
---
name: "Level 4 Pattern Conformance Validation"
description: "Automated validation comparing implementation vs PRP EXAMPLES to detect architectural drift"
prp_id: "PRP-1"
task_id: ""
status: "ready"
priority: "HIGH"
confidence: "9/10"
effort_hours: 25.0
risk: "MEDIUM"
dependencies: []
parent_prp: null
context_memories: []
context_sync:
  ce_updated: false
  serena_updated: false
issue: "BLA-7"                      # Linear issue identifier
project: "Context Engineering"      # Linear project name
version: 1
created_date: "2025-10-12T00:00:00Z"
last_updated: "2025-10-12T00:00:00Z"
---
```

## Step 3: List Issues in Project

```python
# Get all issues in Context Engineering project
mcp__linear__list_issues(
    team="Blaise78",
    project="Context Engineering"
)
```

## Step 4: Get Specific Issue Details

```python
# Using issue identifier from list_issues
mcp__linear__get_issue(
    id="eb0bd8b1-f5a5-4436-9297-9b40e64b411e"
)
```

## Common Parameters

### Priority Values

- `1` = Urgent (critical path, blockers)
- `2` = High (MVP features)
- `3` = Medium (nice-to-have)
- `4` = Low (future enhancements)

### Labels

Standard PRP labels:

- `"prp"` - All PRP issues
- `"mvp"` - MVP superstage
- `"validation"` - Validation-related
- `"automation"` - Automation features
- `"mcp"` - MCP integration
- `"orchestration"` - Workflow orchestration
- `"self-healing"` - Self-healing features

### Issue Description Format

Follow this markdown structure for consistency:

```markdown
# PRP-X[.Y]: Title

**Status**: Ready/In Progress/Executed
**PRP File**: PRPs/PRP-X-filename.md
**Parent**: PRP-XXX (if applicable)

## Summary

1-2 sentence overview

## Key Deliverables

✅ Deliverable 1
✅ Deliverable 2
✅ Deliverable 3

## Effort

* **Estimated**: XXh
* **Actual**: XXh (update during execution)
* **Phases**: Phase1 (Xh), Phase2 (Yh)

## Files

* `path/to/file1.py` - Purpose
* `path/to/file2.py` - Purpose

## Dependencies

PRP-X, PRP-Y (or "None" if foundation)

## References (optional)

* Command: `ce command --help`
* Documentation: [Link](url)
```

## Real-World Example: 5 MVP PRPs

Created in session 2025-10-12:

| Issue | PRP | Title | Effort | Priority | Status |
|-------|-----|-------|--------|----------|--------|
| BLA-7 | PRP-1 | Level 4 Pattern Conformance | 25.0h | High | Backlog |
| BLA-8 | PRP-2 | State Management & Isolation | 17.5h | High | Backlog |
| BLA-9 | PRP-3 | Command Automation | 15.0h | High | Backlog |
| BLA-10 | PRP-4 | Execute-PRP Orchestration | 18.0h | Urgent | Backlog |
| BLA-11 | PRP-5 | Context Sync Integration | 12.0h | High | Backlog |

**Total Effort**: 87.5 hours

## Troubleshooting

### Error: "Argument Validation Error"

- Check `team` parameter - use team name (e.g., "Blaise78"), not project name
- Verify `project` exists: `mcp__linear__list_projects()`

### Error: Team not found

- List available teams: `mcp__linear__list_teams()`
- Use exact team name from list

### Missing Issue After Creation

- Check issue `status` - may be in "Backlog" not "Todo"
- Filter by project: `mcp__linear__list_issues(project="Context Engineering")`

## Automation Pattern

```python
# Batch create issues for all PRPs
prps = [
    {"prp_id": "PRP-1", "title": "...", "effort": 25.0, ...},
    {"prp_id": "PRP-2", "title": "...", "effort": 17.5, ...},
]

for prp in prps:
    issue = mcp__linear__create_issue(
        team="Blaise78",
        title=f"{prp['prp_id']}: {prp['title']}",
        description=generate_description(prp),
        priority=prp.get('priority', 2),
        labels=["prp", "mvp"],
        project="Context Engineering"
    )

    # Update PRP file with issue ID
    update_prp_yaml(prp['prp_id'], issue['identifier'])
```

## See Also

- [Linear MCP Documentation](https://github.com/trutohq/mcp-linear)
- [PRP Template](../PRPs/templates/prp-base-template.md)
- Serena memory: `linear-issue-creation-pattern`
