---
type: regular
category: pattern
tags: [linear, issues, automation]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Linear Issue Creation Pattern

## Working Example

Successfully created 5 MVP PRP issues (BLA-7 through BLA-11) in Linear.

## Key Parameters

```python
mcp__linear__create_issue(
    team="Blaise78",  # Team name, NOT "Context Engineering"
    title="PRP-X: Feature Name",
    description="# Markdown description...",
    priority=1,  # 1=Urgent, 2=High, 3=Medium, 4=Low
    labels=["prp", "mvp"],  # Array of label strings
    project="Context Engineering"  # Project name as string
)
```

## Description Format (From BLA-6 Reference)

```markdown
# PRP-X.Y: Title

**Status**: Ready/Executed  
**PRP File**: PRPs/PRP-X-filename.md

## Summary

Brief description

## Key Deliverables

✅ Item 1  
✅ Item 2

## Effort

* **Estimated**: Xh
* **Phases**: Phase1 (Xh), Phase2 (Yh)

## Files

* `path/to/file.py`

## Dependencies

PRP-X, PRP-Y
```

## PRP YAML Header Integration

After creating issue, update PRP file:

```yaml
issue: "BLA-X"  # Linear issue identifier
project: "Context Engineering"  # Linear project name
```

## Created Issues

- BLA-7: PRP-1 Level 4 Pattern Conformance (25h)
- BLA-8: PRP-2 State Management (17.5h)
- BLA-9: PRP-3 Command Automation (15h)
- BLA-10: PRP-4 Execute-PRP Orchestration (18h, URGENT)
- BLA-11: PRP-5 Context Sync Integration (12h)

All issues created in "Context Engineering" project with proper metadata.
