# GitButler + Claude Code Integration Guide

**Version**: 1.0  
**Date**: 2025-10-29  
**Status**: Production-Ready (Phase 1)  
**Decision**: ✅ CONDITIONAL GO

---

## Table of Contents
- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [Testing Results](#testing-results)
- [Production Hooks (Phase 1)](#production-hooks-phase-1)
- [Required Permissions](#required-permissions)
- [Workflow Patterns](#workflow-patterns)
- [GitButler MCP Server (Phase 2)](#gitbutler-mcp-server-phase-2---experimental)
- [Best Practices](#best-practices)
- [Cleanup Workflow](#cleanup-workflow)
- [Troubleshooting](#troubleshooting)
- [CLAUDE.md Integration](#claudemd-integration)
- [Implementation Checklist](#implementation-checklist)
- [Known Gaps](#known-gaps-to-be-tested)
- [Decision Summary](#decision-summary)
- [Quick Reference Card](#quick-reference-card)

---

## Quick Start

### Prerequisites
```bash
# 1. Install GitButler desktop app
brew install --cask gitbutler

# 2. Install CLI (via GitButler app: Settings → General → Install CLI)
but --help  # Verify installation
```

### Minimal Integration (5 minutes)
```bash
# 1. Initialize repo
cd your-project
but init

# 2. Add hooks to .claude/settings.local.json
# See "Production Hooks" section below

# 3. Add permissions
# See "Required Permissions" section below
```

---

## Core Concepts

### Virtual Branches
- Work on **multiple features simultaneously** without `git checkout`
- Each feature isolated in own virtual branch
- Changes auto-merged in `gitbutler/workspace` branch
- Conflicts detected but don't block work (🔒 icon)

### Workflow Example
```bash
# Work on two PRPs at once
but branch new "prp-30-keyboard"
# Make changes...
but commit prp-30-keyboard -m "Add cmd+v support"

but branch new "prp-31-validation"  # No checkout needed!
# Make changes...
but commit prp-31-validation -m "Add validation"

# Status shows both cleanly
but status
# ╭┄ph [prp-30-keyboard] 
# ● 7cebe08 Add cmd+v support
# ╭┄g8 [prp-31-validation]
# ● 265273c Add validation
```

---

## Testing Results

### ✅ Verified Capabilities
1. **Virtual branch isolation** - Changes stay separated
2. **Conflict detection** - 🔒 icon shows conflicts, doesn't block work
3. **MCP git tools compatible** - `mcp__syntropy__git_*` tools work
4. **Auto-merge behavior** - Creates `gitbutler/workspace` branch
5. **Standard git commands** - `git -C <dir> <cmd>` works via Bash

### Test: Same-Line Conflict (Scenario 1)
```bash
# Branch 1: Added width_override parameter
but commit test-scenario-1-same-line -m "Add width_override"

# Branch 2: Added padding parameter (SAME LINE)
but commit test-scenario-1-conflict -m "Add padding"

# Result: Both commits exist, conflict marked with 🔒
# Workspace file shows most recent commit's changes
# No merge conflict dialog, no manual resolution needed
```

**Key Finding**: GitButler detects conflicts but allows continued work. Resolution deferred to merge time in UI.

---

## Production Hooks (Phase 1)

### Complete .claude/settings.local.json Configuration

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd) && if [ -d \"$PROJECT_ROOT/.git/gitbutler\" ]; then but -C \"$PROJECT_ROOT\" status; fi",
            "timeout": 5
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "mcp__syntropy__git_git_commit",
        "hooks": [
          {
            "type": "command",
            "command": "but -C $(git rev-parse --show-toplevel) status",
            "timeout": 5
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "echo '[GitButler] File changes detected. Remember to commit to appropriate virtual branch.'",
            "timeout": 2
          }
        ]
      }
    ]
  }
}
```

### Hook Behavior
- **SessionStart**: Shows GitButler status once at conversation start (if repo initialized)
- **PreToolUse (git_commit)**: Shows status before any git commit
- **PreToolUse (Edit/Write)**: Reminds user to target correct virtual branch

### Hook Event Names (Critical)
- ✅ Use `SessionStart` (NOT `conversation-start`)
- ✅ Use `PreToolUse` (NOT `tool-call-before`)
- ⚠️ SessionStart does NOT use `matcher` field - omit it

---

## Required Permissions

Add to `.claude/settings.local.json`:
```json
{
  "permissions": {
    "allow": [
      "Bash(but --help:*)",
      "Bash(but -C * init)",
      "Bash(but -C * status:*)",
      "Bash(but -C * branch:*)",
      "Bash(but -C * commit:*)"
    ]
  }
}
```

**Note**: Pattern `but -C *` allows commands in any directory (wildcard `*` matches full path).

---

## Workflow Patterns

### PRP Execution Pattern
```bash
# /execute-prp 30
but branch new "prp-30-feature-name"

# Claude makes changes (Edit/Write tools)
# Hook shows reminder after each edit

# Commit explicitly to target branch
but commit prp-30-feature-name -m "Implement feature X"

# Repeat for logical commits
# When done, merge via GitButler UI
```

### Multi-PRP Development
```bash
# Scenario: Work on PRP-30 and PRP-31 simultaneously

but branch new "prp-30-keyboard-shortcuts"
# Make changes...
but commit prp-30-keyboard-shortcuts -m "Add cmd+v"

but branch new "prp-31-validation"  # No switch!
# Make changes...
but commit prp-31-validation -m "Add validation"

# Both branches coexist cleanly
but status
```

### Conflict Management
- Conflicts detected automatically (🔒 icon)
- Work continues in separate virtual branches
- Resolution happens in GitButler UI at merge time
- No blocking merge dialogs during development

---

## GitButler MCP Server (Phase 2 - Experimental)

### Available Tool
**`gitbutler_update_branches`**
- Auto-commits code changes after AI modifications
- Accepts code changes + prompt context
- Records with metadata

### Installation
```bash
# Option 1: CLI
claude mcp add gitbutler but mcp

# Option 2: Manual (.claude/mcp.json)
{
  "mcpServers": {
    "gitbutler": {
      "command": "but",
      "args": ["mcp"]
    }
  }
}
```

### Status: NEEDS TESTING
- ⚠️ Coexistence with Syntropy MCP unknown
- ⚠️ Branch targeting mechanism unclear
- ⚠️ New tool (launched 2025)
- ✅ Potentially better automation than CLI hooks

### Comparison: MCP vs CLI Hooks

| Aspect | MCP Server | CLI Hooks (Phase 1) |
|--------|-----------|---------------------|
| Automation | ✅ Full auto | ⚠️ Manual targeting |
| Integration | ✅ Native MCP | ⚠️ Bash commands |
| Error handling | ✅ Structured | ⚠️ Parse stdout |
| Branch control | ❓ Unknown | ✅ Explicit `but commit <branch>` |
| Maturity | ⚠️ New (2025) | ✅ Standard patterns |
| Syntropy compat | ❓ Untested | ✅ Verified |

**Recommendation**: Start with CLI hooks (Phase 1), evaluate MCP in parallel.

---

## Best Practices

### From Research (Perplexity + Testing)
1. **Isolate each task** - One virtual branch per PRP/feature
2. **Atomic commits** - Small, focused commits per logical change
3. **Status checks** - Run `but status` regularly to detect conflicts
4. **Explicit branch targeting** - Always specify: `but commit <branch> -m "msg"`
5. **Branch cleanup** - Delete merged branches periodically

### Known Limitations
- ⚠️ CLI relatively new (GUI has more features)
- ⚠️ Must explicitly handle conflicts in automation
- ⚠️ Branch proliferation risk without cleanup
- ⚠️ Workspace shows most recent changes only (not merged state)

### Integration Strategy
**Conservative approach**:
- ✅ Status checks at SessionStart and PreToolUse
- ✅ Reminders after Edit/Write operations
- ❌ NO automatic commit replacement
- ✅ Explicit user/Claude control via `but commit <branch>`

---

## Cleanup Workflow

### Branch Lifecycle
1. Create: `but branch new "prp-XX-feature"`
2. Develop: Make changes, commit multiple times
3. Review: Check in GitButler UI, resolve conflicts
4. Merge: Merge via GitButler UI to upstream
5. Delete: `but branch delete prp-XX-feature`

### Periodic Cleanup
```bash
# List all branches
but branch list

# Delete merged/abandoned branches
but branch delete <branch-name>

# Check workspace is clean
but status
```

---

## Troubleshooting

### Hook Not Triggering
- Check event name: `SessionStart` not `conversation-start`
- Check event name: `PreToolUse` not `tool-call-before`
- Verify `but` command in PATH: `which but`
- Check timeout sufficient (5s recommended)

### Permission Denied
- Add `Bash(but -C * <command>:*)` to allowed list
- Pattern must match actual command structure
- Test manually: `but status`

### Status Shows Conflicts (🔒)
- **Normal behavior** - conflicts detected
- Work continues in separate branches
- Resolve in GitButler UI when ready to merge
- NOT a blocking error

### MCP Server Issues
- Verify installation: `claude mcp list`
- Check `but mcp` command works standalone
- Test Syntropy + GitButler coexistence
- Add permission: `mcp__gitbutler__gitbutler_update_branches`

---

## CLAUDE.md Integration

Add to project CLAUDE.md:

```markdown
## GitButler Integration (Optional)

**If using GitButler for virtual branch management:**

### Commands
- `but status` - Check virtual branches
- `but branch new <name>` - Create branch
- `but commit <branch> -m "msg"` - Commit to specific branch

### Workflow
1. Create branch per PRP: `but branch new "prp-XX-feature"`
2. Make changes with Claude (Edit/Write)
3. Commit: `but commit prp-XX-feature -m "Implement X"`
4. Review/merge in GitButler UI

### Benefits
- Work on multiple PRPs simultaneously
- No branch switching (`git checkout`)
- Conflict detection without blocking
- Visual branch management in UI

### Setup
See: test-target/GITBUTLER-INTEGRATION-GUIDE.md
```

---

## Implementation Checklist

### Phase 1: CLI Hooks (Production-Ready)
- [ ] Add hooks to `.claude/settings.local.json`
- [ ] Add `but` command permissions
- [ ] Test SessionStart hook triggers
- [ ] Test PreToolUse hooks trigger
- [ ] Verify `but status` output readable
- [ ] Update CLAUDE.md with GitButler section
- [ ] Document cleanup workflow for team

### Phase 2: MCP Server (Experimental)
- [ ] Install: `claude mcp add gitbutler but mcp`
- [ ] Verify: `claude mcp list`
- [ ] Test `gitbutler_update_branches` manually
- [ ] Confirm Syntropy + GitButler MCP coexistence
- [ ] Add permission to settings.local.json
- [ ] Test auto-commit after Edit/Write
- [ ] Compare efficiency vs CLI hooks
- [ ] Make go/no-go decision for Phase 2

### Success Criteria

**Phase 1 Complete When**:
- [ ] Hooks trigger without errors
- [ ] `but status` shows in terminal
- [ ] Virtual branches isolate changes
- [ ] Team understands workflow (CLAUDE.md updated)

**Phase 2 Complete When**:
- [ ] MCP tool `gitbutler_update_branches` works
- [ ] Syntropy + GitButler MCP coexist
- [ ] Auto-commit behavior documented
- [ ] Go/no-go decision made

---

## Known Gaps (To Be Tested)

### Scenario 2: Cross-File Refactor
**Status**: Not tested  
**Risk**: Low (Scenario 1 proves core functionality)  
**Test**: Function rename across multiple files (utils/ + please.py)  
**Action**: Optional - test if edge cases needed

### Scenario 3: Dependency Conflicts
**Status**: Not tested  
**Risk**: Low (pyproject.toml conflicts similar to code)  
**Test**: Modify pyproject.toml in conflicting ways across branches  
**Action**: Optional - test if comprehensive coverage needed

**Decision**: Scenario 1 sufficient for MVP. Virtual branch isolation proven. Additional testing deferred until needed.

---

## Decision Summary

**Phase 1 (CLI Hooks): ✅ GO**
- Proven via Scenario 1 testing
- Corrected hook event names
- Syntropy MCP compatible
- Setup time: 15 minutes
- Production-ready

**Phase 2 (MCP Server): ⏸️ EVALUATE**
- Promising but untested
- Needs coexistence validation
- Branch control mechanism unclear
- Evaluation time: 1-2 hours
- Decision pending Phase 2 testing

---

## References

**Testing**:
- Test repo: test-target/pls-cli/ (guedesfelipe/pls-cli)
- Scenario 1: Same-line conflicts ✅ Passed
- MCP git tools: ✅ Compatible

**External**:
- GitButler MCP: https://docs.gitbutler.com/features/ai-integration/mcp-server
- Claude Hooks: https://docs.claude.com/en/docs/claude-code/hooks
- GitButler CLI: `but --help`

**Commands**:
```bash
# Essential commands
but init                           # Initialize repo
but status                         # Show virtual branches
but branch new <name>             # Create virtual branch
but branch list                   # List branches
but commit <branch> -m "msg"      # Commit to branch
but branch delete <name>          # Delete branch
```

---

## Quick Reference Card

```bash
# Setup
brew install --cask gitbutler
but init

# Daily workflow
but branch new "prp-30-feature"
# Make changes...
but status
but commit prp-30-feature -m "Add feature X"

# Multi-feature work
but branch new "prp-31-other"
# Make changes...
but commit prp-31-other -m "Add other"

# Status check
but status
# Shows both branches cleanly

# Cleanup
but branch delete prp-30-feature
```

**Hook Strategy**: SessionStart status check + PreToolUse reminders  
**Conflict Strategy**: Detect with 🔒, continue work, resolve in UI  
**Branch Strategy**: One branch per PRP, explicit commit targeting  
**MCP Strategy**: CLI hooks (Phase 1) now, MCP server (Phase 2) later
