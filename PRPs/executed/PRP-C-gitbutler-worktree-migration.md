---
prp_id: PRP-C
feature_name: GitButler to Worktree Migration
status: executed
created: 2025-10-29T00:00:00Z
updated: 2025-10-30T00:00:00Z
executed: 2025-10-29T00:00:00Z
execution_commit: 920edd4
complexity: medium
estimated_hours: 0.42-0.50
dependencies: none
stage: stage-1-parallel
worktree_path: ../ctx-eng-plus-prp-c
branch_name: prp-c-worktree-migration
execution_order: 3
merge_order: 3
files_modified: CLAUDE.md, .claude/settings.local.json, archive/ (new dir)
conflict_potential: LOW (different sections than A, different files than B)
---

# GitButler to Worktree Migration

## 1. TL;DR

**Objective**: Replace GitButler virtual branch workflow with git worktree parallel PRP development

**What**: Remove GitButler integration (docs, hooks), add comprehensive git worktree documentation with conflict resolution procedures, archive old docs

**Why**: GitButler is abstraction over standard git; native git worktrees provide same parallel development capability without additional tooling

**Effort**: 25-30 minutes

**Dependencies**: None (stage-1-parallel, independent execution)

---

## 2. Context

### Background
- GitButler provides virtual branches for parallel development
- Adds complexity: custom CLI (`but`), hooks, UI abstraction
- Git worktrees provide identical capability natively
- Standard git is more universal, predictable, and flexible

### Parallel Execution Context
- **Stage**: stage-1-parallel (can run with PRP-A, PRP-B)
- **Worktree**: `../ctx-eng-plus-prp-c`
- **Branch**: `prp-c-worktree-migration`
- **Files**: `CLAUDE.md` (GitButler section), `.claude/settings.local.json` (hooks), `archive/` (new dir)
- **Conflicts**: LOW (different sections/files than A and B)

### Constraints and Considerations
- Must document git worktree constraints (same branch limitation)
- Must include complete conflict resolution procedures
- Must provide migration path from GitButler commands
- Documentation must be comprehensive (users rely on this for parallel development)
- Hooks removal affects workflow (must not break existing patterns)

### Documentation References
- Source: TOOL-PERMISSION-LOCKDOWN-PLAN.md Section 3
- Git worktree commands: add, list, remove, prune
- Conflict resolution: Read + Edit tools
- Current GitButler docs: CLAUDE.md, test-target/GITBUTLER-INTEGRATION-GUIDE.md, examples/

---

## 3. Implementation Steps

### Phase 1: Preparation and Archive (5 min)

**Step 1**: Create archive directory
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
mkdir -p archive/gitbutler
```

**Step 2**: Archive GitButler documentation
```bash
# Move docs to archive
mv test-target/GITBUTLER-INTEGRATION-GUIDE.md archive/gitbutler/
mv examples/GITBUTLER-REFERENCE.md archive/gitbutler/
mv examples/gitbutler-test-automation.py archive/gitbutler/

# Create archive index
cat > archive/gitbutler/README.md << 'EOF'
# GitButler Integration Archive

**Status**: ARCHIVED (2025-10-29)
**Replaced By**: Git worktrees (see CLAUDE.md "Parallel PRP Development")

These files document the previous GitButler virtual branch integration.
Archived for historical reference.

## Files
- GITBUTLER-INTEGRATION-GUIDE.md - Full integration guide
- GITBUTLER-REFERENCE.md - Command reference
- gitbutler-test-automation.py - Test automation with Serena

## Migration
See CLAUDE.md section "Parallel PRP Development with Git Worktrees" for replacement workflow.
EOF
```

**Step 3**: Read current GitButler section location
```bash
# Find GitButler section in CLAUDE.md
grep -n "## GitButler" CLAUDE.md
# Note: Section starts around line 200-250 (approximate)
```

### Phase 2: Remove GitButler Content (8 min)

**Step 4**: Remove GitButler section from CLAUDE.md
- Use Read to identify exact section boundaries
- Section title: "## GitButler Integration"
- Includes: Quick Start, Commands, Workflow, Hooks, Benefits, Example
- Estimated: ~150-200 lines
- Use Edit to remove entire section

**Step 5**: Remove GitButler hooks from settings
File: `.claude/settings.local.json`

Remove these hooks:
```json
// In SessionStart hooks array
{
  "type": "command",
  "command": "PROJECT_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd) && if [ -d \"$PROJECT_ROOT/.git/gitbutler\" ]; then but -C \"$PROJECT_ROOT\" status; fi",
  "timeout": 5
}

// In PreToolUse hooks array
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
```

**Step 6**: Remove GitButler bash permission
In `.claude/settings.local.json`, remove:
```json
"Bash(but:*)",
```

### Phase 3: Add Git Worktree Documentation (12 min)

**Step 7**: Add new section to CLAUDE.md

Insert after "Quick Commands" section (before "Working Directory"):

```markdown
## Parallel PRP Development with Git Worktrees

**Use git worktrees for parallel multi-PRP development**

### Quick Start

```bash
# Create worktree for new PRP
git worktree add ../ctx-eng-plus-prp-30 -b prp-30-feature

# Work in worktree
cd ../ctx-eng-plus-prp-30
# Make changes with Claude (Edit/Write)
git add .
git commit -m "Implement feature X"
git push -u origin prp-30-feature

# Create PR
gh pr create --title "PRP-30: Feature" --base main

# When done, remove worktree
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git worktree remove ../ctx-eng-plus-prp-30
```

### ⚠️ Constraints

**CRITICAL**: Cannot check out same branch in multiple worktrees simultaneously

**This FAILS**:
```bash
# Main repo on 'main' branch
git worktree add ../ctx-eng-plus-prp-30 main  # ❌ ERROR
# Error: 'main' is already checked out at '/Users/.../ctx-eng-plus'
```

**Rules**:
- Main repo should stay on `gitbutler/workspace` or a dedicated branch
- Each PRP worktree MUST use unique branch name
- Always create new branch: `git worktree add ../path -b new-branch-name`

**Disk Space**:
- Each worktree = full working directory copy
- Main repo: ~500MB
- 3 PRP worktrees: ~1.5GB additional
- Monitor: `du -sh ../ctx-eng-plus*`

### Commands

**Create worktree**:
```bash
git worktree add ../ctx-eng-plus-prp-30 -b prp-30-feature
# Creates new branch and worktree
```

**List worktrees**:
```bash
git worktree list
# Shows all worktrees and their branches
```

**Remove worktree**:
```bash
git worktree remove ../ctx-eng-plus-prp-30
# Or force if uncommitted changes:
git worktree remove ../ctx-eng-plus-prp-30 --force
```

**Prune stale worktrees**:
```bash
git worktree prune
# Cleans up worktree metadata
```

### Conflict Resolution

**Scenario 1: Conflicts during PR merge**
```bash
# Update PRP branch with latest main
cd ../ctx-eng-plus-prp-30
git fetch origin
git merge origin/main

# If conflicts occur:
git status                    # See conflicted files
# Use Read tool to view conflict markers:
# <<<<<<< HEAD
# Your changes
# =======
# Their changes
# >>>>>>> origin/main

# Use Edit tool to resolve conflicts
git add <resolved-files>
git commit -m "Merge main, resolve conflicts"
git push
```

**Scenario 2: Conflicts between multiple PRPs**
```bash
# Work on PRP-30 and PRP-31 independently (no conflicts during work)

# When merging PRP-30 to main (first):
cd ../ctx-eng-plus-prp-30
gh pr merge <pr-number>       # Merges cleanly

# When merging PRP-31 to main (second):
cd ../ctx-eng-plus-prp-31
git fetch origin
git merge origin/main         # May conflict with PRP-30 changes

# Resolve as above
git status
# Use Read + Edit tools
git add <resolved-files>
git commit -m "Merge main after PRP-30, resolve conflicts"
git push
gh pr merge <pr-number>
```

**Scenario 3: Early conflict detection**
```bash
# Periodically sync with main to catch conflicts early
cd ../ctx-eng-plus-prp-30
git fetch origin
git merge origin/main --no-commit --no-ff

# If conflicts, resolve immediately
# If clean, commit
git commit -m "Sync with main"
git push
```

### Best Practices

1. **Read conflicts first**: Use Read tool to see conflict markers
2. **Resolve with Edit tool**: Remove markers, keep correct changes
3. **Verify resolution**:
   ```bash
   cd tools && uv run pytest tests/ -v
   cd tools && uv run ce validate --level all
   ```
4. **Commit resolution**: Clear message explaining resolution

### Workflow Comparison

| Task | GitButler | Git Worktree |
|------|-----------|--------------|
| Create PRP workspace | `but branch new prp-30` | `git worktree add ../ctx-eng-plus-prp-30 -b prp-30` |
| Switch context | Automatic (virtual) | `cd ../ctx-eng-plus-prp-30` |
| Commit changes | `but commit prp-30 -m "msg"` | `git commit -m "msg"` (in worktree) |
| View status | `but status` | `git worktree list` |
| Detect conflicts | UI indicator (🔒) | `git merge --no-commit` (manual) |
| Remove workspace | `but branch delete prp-30` | `git worktree remove ../ctx-eng-plus-prp-30` |

### Advantages

1. **Standard git**: No additional tools required
2. **Universal**: Works everywhere git works
3. **Isolated directories**: Each PRP has clean workspace
4. **No abstraction**: Direct git commands
5. **Better IDE support**: Each worktree opens as separate project
6. **Natural conflicts**: Only at merge time (expected)

### Multi-PRP Example

```bash
# Work on 3 PRPs simultaneously
git worktree add ../ctx-eng-plus-prp-30 -b prp-30-auth
git worktree add ../ctx-eng-plus-prp-31 -b prp-31-api
git worktree add ../ctx-eng-plus-prp-32 -b prp-32-ui

# Develop in parallel (separate Claude sessions or sequential)
cd ../ctx-eng-plus-prp-30 && # work on auth
cd ../ctx-eng-plus-prp-31 && # work on API
cd ../ctx-eng-plus-prp-32 && # work on UI

# Merge in sequence
cd ../ctx-eng-plus-prp-30 && gh pr create && gh pr merge <num>
cd ../ctx-eng-plus-prp-31 && git merge origin/main && gh pr create && gh pr merge <num>
cd ../ctx-eng-plus-prp-32 && git merge origin/main && gh pr create && gh pr merge <num>

# Cleanup
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git worktree remove ../ctx-eng-plus-prp-30
git worktree remove ../ctx-eng-plus-prp-31
git worktree remove ../ctx-eng-plus-prp-32
```
```

### Phase 4: Validation (5 min)

**Step 8**: Verify GitButler references removed
```bash
# Search for GitButler mentions
grep -ri "gitbutler" --include="*.md" .
# Should only show archive/ directory

grep -r "but " --include="*.md" . | grep -v archive
# Should show minimal results (not GitButler commands)

grep -ri "virtual branch" --include="*.md" .
# Should only show archive/ or none
```

**Step 9**: Verify settings valid
```bash
# Check JSON syntax
python3 -m json.tool .claude/settings.local.json > /dev/null && echo "✓ Valid JSON"

# Check hooks removed
grep -c "gitbutler\|but " .claude/settings.local.json
# Should be 0
```

**Step 10**: Test worktree workflow
```bash
# Quick smoke test
git worktree add ../ctx-eng-plus-test -b test-branch
cd ../ctx-eng-plus-test
echo "test" > TEST.txt
git add TEST.txt
git commit -m "Test worktree"
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git worktree remove ../ctx-eng-plus-test
```

---

## 4. Validation Gates

### Gate 1: GitButler Docs Archived
**Command**: `ls archive/gitbutler/`
**Expected**: 4 files (README.md, INTEGRATION-GUIDE, REFERENCE, test-automation.py)
**On Failure**: Verify files moved, not deleted

### Gate 2: GitButler Section Removed from CLAUDE.md
**Command**: `grep -c "GitButler" CLAUDE.md`
**Expected**: 0 (or only in "Removed" context if noted)
**On Failure**: Remove remaining GitButler references

### Gate 3: Worktree Section Added to CLAUDE.md
**Command**: `grep -c "## Parallel PRP Development with Git Worktrees" CLAUDE.md`
**Expected**: 1
**On Failure**: Add worktree section

### Gate 4: Hooks Removed from Settings
**Command**: `grep -c "gitbutler\|but " .claude/settings.local.json`
**Expected**: 0
**On Failure**: Remove remaining GitButler hooks/permissions

### Gate 5: Settings Valid JSON
**Command**: `python3 -m json.tool .claude/settings.local.json > /dev/null && echo "PASS" || echo "FAIL"`
**Expected**: PASS
**On Failure**: Fix JSON syntax errors

### Gate 6: Worktree Workflow Works
**Command**: Manual test (create test worktree, commit, remove)
**Expected**: All commands execute without errors
**On Failure**: Debug git worktree commands, verify git version

---

## 5. Testing Strategy

### Test Framework
Manual validation + bash smoke tests

### Test Command
```bash
# Archive verification
ls archive/gitbutler/

# Content verification
grep -c "GitButler" CLAUDE.md
grep -c "Parallel PRP Development with Git Worktrees" CLAUDE.md

# Settings verification
python3 -m json.tool .claude/settings.local.json
grep -c "but " .claude/settings.local.json

# Worktree smoke test
git worktree add ../ctx-eng-plus-test -b test && \
cd ../ctx-eng-plus-test && \
echo "test" > TEST && \
git add TEST && \
git commit -m "test" && \
cd /Users/bprzybyszi/nc-src/ctx-eng-plus && \
git worktree remove ../ctx-eng-plus-test
```

### Unit Tests
1. **Archive complete**: All 3 GitButler files moved
2. **CLAUDE.md updated**: GitButler removed, worktree added
3. **Hooks removed**: No GitButler references in settings

### Integration Tests
1. **Settings valid**: JSON parses correctly
2. **Documentation complete**: Worktree section has all subsections
3. **No broken references**: No dead links to GitButler docs

### Functional Tests
1. **Worktree creation**: Can create new worktree
2. **Worktree work**: Can commit in worktree
3. **Worktree removal**: Can remove worktree cleanly

---

## 6. Rollout Plan

### Phase 1: Development
- Create worktree: `git worktree add ../ctx-eng-plus-prp-c -b prp-c-worktree-migration`
- Execute steps 1-10 in worktree
- Archive GitButler docs (move to archive/)
- Remove GitButler from CLAUDE.md and settings
- Add comprehensive worktree documentation
- Validate all gates pass
- Commit: `git commit -m "Replace GitButler with git worktree workflow"`

### Phase 2: Review
- Push branch: `git push -u origin prp-c-worktree-migration`
- Create PR: `gh pr create --title "PRP-C: GitButler→Worktree Migration" --base main`
- Self-review: Verify documentation complete, no broken references
- Merge when ready

### Phase 3: Integration
- Merge order: 3 (merge after PRP-A and PRP-B in Stage 1)
- No conflicts expected (different files/sections)
- Verify: Documentation renders correctly on GitHub
- Test: Create real worktree, do work, merge with conflicts

### Rollback Strategy
```bash
# If issues occur
git revert HEAD

# Restore GitButler docs from archive
mv archive/gitbutler/* [original-locations]

# Or restore from git history
git checkout HEAD~1 CLAUDE.md .claude/settings.local.json
```

---

## Research Findings

### Git Worktree Capabilities
- **Parallel development**: Each worktree is isolated directory
- **Same repository**: All worktrees share .git metadata
- **Branch restriction**: Cannot checkout same branch twice
- **Conflict handling**: Standard git merge conflict resolution
- **Performance**: No overhead, standard git operations

### GitButler vs Worktree Feature Comparison

| Feature | GitButler | Git Worktree |
|---------|-----------|--------------|
| Parallel branches | Virtual (UI) | Physical (directories) |
| Branch switching | Automatic | Manual (cd command) |
| Conflict detection | Live (UI indicator) | On merge (standard git) |
| Tooling required | Custom CLI + UI | Standard git (v2.5+) |
| IDE support | Limited | Full (separate projects) |
| Universality | GitButler-specific | Works everywhere |

### Documentation Completeness
- **Quick Start**: Basic workflow in 6 commands
- **Constraints**: Critical limitation documented (same branch)
- **Conflict Resolution**: 3 scenarios with step-by-step procedures
- **Comparison**: Side-by-side GitButler vs worktree commands
- **Examples**: Multi-PRP workflow example
- **Best Practices**: Read + Edit tools for resolution

### Files Modified Summary
1. **CLAUDE.md**: ~150 lines removed (GitButler), ~200 lines added (worktree)
2. **.claude/settings.local.json**: ~15 lines removed (hooks + permission)
3. **archive/**: New directory + 4 files (archived docs)
4. **Net**: ~50 lines added, clearer workflow documentation

---

**Completion Criteria**:
- [ ] GitButler docs archived (3 files + README)
- [ ] GitButler section removed from CLAUDE.md
- [ ] Git worktree section added to CLAUDE.md (~200 lines)
- [ ] All hooks removed from settings
- [ ] Bash `but:*` permission removed
- [ ] Valid JSON syntax maintained
- [ ] No GitButler references in active docs
- [ ] Worktree workflow tested and working
