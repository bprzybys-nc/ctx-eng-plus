---
name: "Add Git Status Summary Command"
description: "Simple CLI command to display formatted git repository status with branch info and file counts"
prp_id: "PRP-2.1"
task_id: ""
status: "ready"
priority: "LOW"
confidence: "8/10"
effort_hours: 2.0
risk: "LOW"
dependencies: []
parent_prp: null
context_memories: []
meeting_evidence: []
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
created_date: "2025-01-15T10:00:00Z"
last_updated: "2025-01-15T10:00:00Z"
---

# PRP-2.1: Add Git Status Summary Command

## 🎯 TL;DR

**Problem**: Users need a quick way to see git status without verbose output.

**Solution**: Add `ce git summary` command that shows:
- Current branch
- Clean/dirty status
- Count of staged/unstaged/untracked files

**Impact**:
- Faster git status checks (formatted output)
- Easier integration into scripts (JSON output option)

**Risk**: LOW (read-only git operation)
**Effort**: 2 hours (1h implementation, 1h testing)

---

## 📋 Context

### Problem Statement

Current `ce git status` returns full git status dict. Users want a quick summary view.

**Current State**:
```python
status = git_status()
# Returns: {'clean': False, 'staged': [...], 'unstaged': [...], ...}
# User must parse dict manually
```

**Desired State**:
```bash
$ ce git summary
Branch: main
Status: Clean working tree
```

---

## 🎯 Goals & Success Criteria

### Primary Goal
Add human-readable git status summary command

### Success Criteria
1. ✅ Command displays branch name
2. ✅ Command shows clean/dirty status
3. ✅ Command counts staged/unstaged/untracked files
4. ✅ Supports `--json` flag for scripting

---

## 🛠️ Implementation Plan

### Phase 1: Add Command Function

**File**: [ce/git.py](ce/git.py)

```python
def git_summary() -> Dict[str, Any]:
    """Get formatted git status summary.

    Returns:
        Dict with: branch, clean, counts (staged/unstaged/untracked)
    """
    status = git_status()
    return {
        "branch": status["branch"],
        "clean": status["clean"],
        "counts": {
            "staged": len(status["staged"]),
            "unstaged": len(status["unstaged"]),
            "untracked": len(status["untracked"])
        }
    }
```

**Validation**: Run `uv run pytest tests/test_git.py::test_git_summary -v`

### Phase 2: Add CLI Command

**File**: [ce/__main__.py](ce/__main__.py)

```python
@git_group.command(name="summary")
def git_summary_cmd():
    """Display git status summary."""
    summary = git_summary()
    if summary["clean"]:
        click.echo(f"Branch: {summary['branch']}")
        click.echo("Status: Clean working tree")
    else:
        click.echo(f"Branch: {summary['branch']}")
        click.echo("Status: Uncommitted changes")
        counts = summary["counts"]
        if counts["staged"]:
            click.echo(f"  Staged: {counts['staged']}")
        if counts["unstaged"]:
            click.echo(f"  Unstaged: {counts['unstaged']}")
        if counts["untracked"]:
            click.echo(f"  Untracked: {counts['untracked']}")
```

**Validation**: Run `cd tools && uv run ce git summary`

---

## 🧪 Validation Strategy

### Level 1: Unit Tests
```bash
cd tools && uv run pytest tests/test_git.py -v
```
**Expected**: New test `test_git_summary` passes

### Level 2: CLI Manual Test
```bash
cd tools && uv run ce git summary
```
**Expected**: Formatted output displays correctly

### Level 3: JSON Output
```bash
cd tools && uv run ce git summary --json
```
**Expected**: Valid JSON output

---

## 📁 Files to Modify

- `tools/ce/git.py` - Add `git_summary()` function
- `tools/ce/__main__.py` - Add `git summary` CLI command
- `tools/tests/test_git.py` - Add test coverage

---

## ✅ Completion Checklist

- [ ] `git_summary()` function added
- [ ] CLI command added
- [ ] Tests passing
- [ ] Manual validation complete
- [ ] JSON output tested
- [ ] Committed to git
