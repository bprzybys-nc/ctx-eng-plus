# GitButler `but` Command Reference

**Quick search index** - Jump to: [Init](#initialization) | [Status](#status--inspection) | [Branch](#branch-management) | [Commit](#committing) | [History](#operation-history) | [Advanced](#advanced-operations) | [Common Tasks](#common-task-patterns)

---

## Command Index by Category

### Initialization
- [`but init`](#but-init) - Initialize GitButler in repository

### Status & Inspection
- [`but status`](#but-status) - Show uncommitted changes and virtual branches
- [`but log`](#but-log) - Show commits on active branches

### Branch Management
- [`but branch new`](#but-branch-new) - Create new virtual branch
- [`but branch list`](#but-branch-list) - List all virtual branches
- [`but branch delete`](#but-branch-delete) - Delete virtual branch

### Committing
- [`but commit`](#but-commit) - Commit changes to specific branch

### Operation History
- [`but oplog`](#but-oplog) - Show operation history
- [`but undo`](#but-undo) - Undo last operation
- [`but restore`](#but-restore) - Restore to specific snapshot
- [`but snapshot`](#but-snapshot) - Create manual snapshot

---

## Initialization

### `but init`

**Initialize GitButler project from current git repository**

```bash
but init
```

**Output Example**:
```
Initialized GitButler project from /path/to/repo. The default target is origin/main
```

**When to Use**: First time setup, creates `.git/gitbutler/` directory

**See Also**: [GITBUTLER-INTEGRATION-GUIDE.md](../test-target/GITBUTLER-INTEGRATION-GUIDE.md#quick-start)

---

## Status & Inspection

### `but status`

**Show virtual branches and uncommitted changes**

```bash
but status
```

**Output Symbols**:
- `[Unassigned Changes]` - Files not yet committed
- `ua M` - Unassigned, modified
- `● commit` - Commit on branch
- `🔒 commit` - Conflict detected (work continues)

**With Directory Flag**: `but -C /path/to/repo status`

---

### `but log`

**Show commits on active branches**

```bash
but log
```

---

## Branch Management

### `but branch new`

**Create new virtual branch**

```bash
but branch new "prp-30-feature"
```

**Best Practice**: Use format `"prp-XX-description"`

**Note**: Does NOT switch branches (no `git checkout`)

---

### `but branch list`

**List all virtual branches**

```bash
but branch list
```

---

### `but branch delete`

**Delete virtual branch**

```bash
but branch delete "prp-30-feature"
```

**Warning**: Cannot be undone (unless via `but undo`)

---

## Committing

### `but commit`

**Commit changes to specific branch**

```bash
but commit <branch-name> -m "commit message"
but commit prp-30-feature -m "Add validation"
```

**Required**: Branch name (explicit targeting)

**Common Error**:
```bash
# ❌ Ambiguous
but commit -m "Add feature"

# ✅ Explicit
but commit prp-30-feature -m "Add feature"
```

**Options**:
- `-m <MESSAGE>` - Commit message (required)
- `-o, --only` - Only commit assigned files

---

## Operation History

### `but oplog`

**Show operation history (last 20 entries)**

```bash
but oplog
```

---

### `but undo`

**Undo last operation**

```bash
but undo
```

**Example**:
```bash
# Oops, wrong branch!
but commit wrong-branch -m "Feature"
but undo
but commit correct-branch -m "Feature"
```

---

### `but restore`

**Restore to specific snapshot**

```bash
but oplog                    # Find snapshot ID
but restore <snapshot-id>
```

---

### `but snapshot`

**Create manual snapshot**

```bash
but snapshot -m "Before refactor"
```

---

## Common Task Patterns

### Start New Feature
```bash
but branch new "prp-XX-feature"
# Make changes...
but status
but commit prp-XX-feature -m "Implement X"
```

### Multi-PRP Development
```bash
but branch new "prp-30-keyboard"
but commit prp-30-keyboard -m "Add cmd+v"

but branch new "prp-31-validation"  # No checkout!
but commit prp-31-validation -m "Add validation"

but status  # Both branches cleanly separated
```

### Fix Wrong Commit
```bash
but undo
but commit correct-branch -m "Message"
```

### Cleanup
```bash
but branch list
but branch delete "prp-30-feature"
but status
```

---

## Command Cheatsheet

```bash
# Setup
but init

# Daily workflow
but status
but branch new "prp-XX-feature"
but commit prp-XX-feature -m "Add feature"

# Cleanup
but branch delete "prp-XX-feature"

# History
but undo
but snapshot -m "Checkpoint"
```

---

## Troubleshooting

**"command not found: but"** → Install CLI via GitButler app (Settings → General)

**"Invalid selection"** → Always specify branch: `but commit <branch> -m "msg"`

**Conflicts (🔒)** → Not an error, work continues. Resolve in GitButler UI.

---

**Full Guide**: [GITBUTLER-INTEGRATION-GUIDE.md](../test-target/GITBUTLER-INTEGRATION-GUIDE.md)
**Claude Integration**: [CLAUDE.md § GitButler](../CLAUDE.md#gitbutler-integration-optional)
