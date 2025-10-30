# GitButler Complete Removal Plan

**Status**: Initial Planning
**Created**: 2025-10-30
**Context**: Migrate from GitButler to native git worktrees (PRP-C completed)
**Complexity**: MEDIUM
**Risk**: MEDIUM (29 commits must be preserved)
**Estimated Time**: 45-60 minutes total

---

## Executive Summary

**Goal**: Safely remove GitButler integration and migrate all work to native git workflow

**Current State**:
- ✅ Git worktree workflow documented (PRP-C)
- ✅ `Bash(but:*)` permission removed (PRP-D)
- ✅ GitButler docs archived (`archive/gitbutler/`)
- ⚠️ Currently on `gitbutler/workspace` branch
- ⚠️ 29 commits ahead of `main` (all recent work)
- ⚠️ `.git/gitbutler/` directory present (virtual_branches.toml)
- ⚠️ GitButler app still installed

**What Needs Removal**:
1. Git branches (`gitbutler/workspace`, `feat/gitbutler`)
2. GitButler metadata (`.git/gitbutler/` directory)
3. GitButler app (`/Applications/GitButler.app/`)
4. GitButler references in slash commands (3 files)
5. Test repository artifacts (optional)

**Prerequisites**:
- ✅ `Bash(but:*)` permission already removed (PRP-D, commit 0f5303f)

**Critical Constraint**: Must preserve all 29 commits containing:
- PRPs A-E execution (Stage 1 & 2)
- `/batch-gen-prp` and `/generate-prp` commands
- Tool lockdown implementation
- All peer reviews and fixes

---

## Current State Analysis

### Git Branches

```bash
# Local branches with GitButler
* gitbutler/workspace (29 commits ahead of main)
  feat/gitbutler (status unknown)
  main (behind gitbutler/workspace)

# Remote branches
  remotes/origin/gitbutler/workspace (synced)
  remotes/origin/main (behind)
```

**Critical Commits on gitbutler/workspace** (newest first):
1. `12e6893` - Update YAML headers for PRPs A-E
2. `b29ccc5` - Mark PRPs A-E as executed
3. `79a9f7e` - Apply peer review fixes
4. `e637b81` - Add peer review document
5. `95b1b57` - Document /batch-gen-prp
6. `9f8ff75` - Add /batch-gen-prp command
7. `884b537` - Merge PRP-E
8. `0f5303f` - Merge PRP-D
9. `fe86977` - Update CLAUDE.md for lockdown
10. `534cdd4` - Add command permissions
... (19 more commits)

### GitButler Artifacts

**Directories**:
- `.git/gitbutler/` - GitButler metadata (virtual_branches.toml)
- `archive/gitbutler/` - Archived docs (3 files, KEEP)
- `test-target/pls-cli/.git/logs/refs/heads/gitbutler/` - Test repo artifacts

**Application**:
- `/Applications/GitButler.app/` - GitButler GUI app
- `/Applications/GitButler.app/Contents/MacOS/but` - CLI tool

**Documentation**:
- `CLAUDE.md` lines 476-680: Git Worktree section (references archived GitButler docs)

### Risk Assessment

**HIGH RISK**:
- Losing 29 commits if merge fails
- Breaking current branch state
- Remote sync issues

**MEDIUM RISK**:
- Incomplete removal (artifacts remain)
- Documentation references broken

**LOW RISK**:
- App uninstall (system-level, reversible)

---

## Phased Removal Strategy

### Phase 1: Preserve Work (Merge to Main)
**Goal**: Merge all 29 commits from gitbutler/workspace → main
**Time**: 10-15 minutes
**Risk**: MEDIUM (merge conflicts possible)

**Steps**:
1. Verify no uncommitted changes on gitbutler/workspace
2. Create backup tag: `git tag gitbutler-backup-2025-10-30`
3. Checkout main: `git checkout main`
4. Pull latest: `git pull origin main`
5. Merge gitbutler/workspace: `git merge gitbutler/workspace --no-ff -m "Merge gitbutler/workspace: Preserve 29 commits before GitButler removal"`
6. Resolve conflicts if any (expected: none, branches diverged cleanly)
7. Push to main: `git push origin main`

**Validation**:
- Verify commit count: `git log main..HEAD` should be empty
- Verify all PRPs present: `ls PRPs/executed/PRP-{A,B,C,D,E}*`
- Verify commands present: `ls .claude/commands/{batch-gen-prp,generate-prp}.md`

**Rollback**:
```bash
# If merge fails
git merge --abort
git checkout gitbutler/workspace
```

---

### Phase 2: Remove GitButler Branches
**Goal**: Delete local and remote GitButler branches
**Time**: 5 minutes
**Risk**: LOW (work already merged)

**Steps**:
1. Delete local gitbutler/workspace: `git branch -D gitbutler/workspace`
2. Delete local feat/gitbutler: `git branch -D feat/gitbutler` (if exists)
3. Delete remote gitbutler/workspace: `git push origin --delete gitbutler/workspace`
4. Verify: `git branch -a | grep -i gitbutler` (should be empty)

**Validation**:
- No local branches with "gitbutler" in name
- No remote branches with "gitbutler" in name
- `git log` on main shows all 29 commits

**Rollback**:
```bash
# If needed
git checkout -b gitbutler/workspace gitbutler-backup-2025-10-30
```

---

### Phase 3: Remove GitButler Metadata
**Goal**: Delete `.git/gitbutler/` directory and test repository artifacts
**Time**: 5 minutes
**Risk**: LOW (metadata regenerates, not critical)

**Steps**:
1. Verify directory exists: `ls -la .git/gitbutler/`
2. Remove git metadata: `rm -rf .git/gitbutler/`
3. Optional - Clean test repository artifacts:
   ```bash
   rm -rf test-target/pls-cli/.git/logs/refs/heads/gitbutler
   ```
4. Verify removal: `ls -la .git/ | grep gitbutler` (should return nothing)
5. Verify archive preserved: `ls -la archive/ | grep gitbutler` (should show directory)

**Validation**:
- `.git/gitbutler/` directory does not exist
- `archive/gitbutler/` still exists (documented history)
- No git status changes (metadata not tracked in git)
- Optional: Test repository cleaned

**Rollback**:
- Not possible (metadata regenerated by GitButler if app relaunched)
- Low risk: metadata not critical to git history

---

### Phase 4: Uninstall GitButler App
**Goal**: Remove GitButler application from system
**Time**: 2 minutes
**Risk**: LOW (system-level, no git impact)

**Steps**:
1. Quit GitButler app if running
2. Move app to trash: `trash /Applications/GitButler.app` or manual drag
3. Remove CLI symlink if exists: `unlink /usr/local/bin/but` (if present)
4. Verify: `which but` (should return nothing)

**Validation**:
- GitButler app not in `/Applications/`
- `but` command not found
- Git operations still work normally

**Rollback**:
- Reinstall from https://gitbutler.com or Mac Trash

**Note**: This step is OPTIONAL. If user wants to keep GitButler for other projects, skip this phase.

---

### Phase 5: Clean Documentation References
**Goal**: Ensure no broken references to GitButler workflow
**Time**: 15-20 minutes
**Risk**: LOW (documentation only)

**Steps**:
1. Verify CLAUDE.md references are correct:
   - Lines 421-681: "Git Worktree" section should reference `archive/gitbutler/`
   - No active GitButler workflow instructions (already migrated per PRP-C)
2. Update slash commands with GitButler references:
   - `.claude/commands/peer-review.md` - Remove GitButler integration checks
   - `.claude/commands/generate-prp.md` - Remove GitButler checkpoint instructions
   - `.claude/commands/batch-exe-prp.md` - Remove `but status` checks
3. Check for remaining GitButler references:
   ```bash
   grep -r "gitbutler" . --include="*.md" --exclude-dir=archive --exclude-dir=initials
   grep -r "but status" .claude/commands/
   grep -r "but branch" .claude/commands/
   grep -r "but log" .claude/commands/
   ```
4. Update any found references to point to git worktree workflow
5. Commit documentation updates:
   ```bash
   git add CLAUDE.md .claude/commands/
   git commit -m "Remove GitButler references, complete migration to git worktree"
   ```

**Validation**:
- All `archive/gitbutler/` links work
- No slash commands reference `but` command
- No instructions reference GitButler virtual branches
- Git worktree workflow is primary documented method

**Rollback**:
- Revert documentation commit: `git revert HEAD`

---

## Validation Gates

### Gate 1: Commit Preservation ✓
**Test**:
```bash
git checkout main
git log --oneline | head -30 | grep -E "(12e6893|b29ccc5|79a9f7e|e637b81|95b1b57|9f8ff75)"
```
**Expected**: All 6 recent commit hashes present
**On Failure**: Merge did not complete, rollback to gitbutler/workspace

### Gate 2: File Integrity ✓
**Test**:
```bash
ls PRPs/executed/PRP-{A,B,C,D,E}*.md | wc -l
ls .claude/commands/batch-gen-prp.md
ls .claude/commands/generate-prp.md
```
**Expected**: 5 PRPs + 2 commands exist
**On Failure**: Files lost, restore from gitbutler-backup tag

### Gate 3: Branch Cleanup ✓
**Test**:
```bash
git branch -a | grep -i gitbutler
```
**Expected**: Only `archive/gitbutler/` in grep results (if any)
**On Failure**: Branches not deleted, rerun Phase 2

### Gate 4: Metadata Removal ✓
**Test**:
```bash
test -d .git/gitbutler && echo "FAIL: .git/gitbutler exists" || echo "PASS"
test -d archive/gitbutler && echo "PASS: Archive preserved" || echo "FAIL"
```
**Expected**: PASS + PASS
**On Failure**: Remove .git/gitbutler manually, verify archive exists

### Gate 5: Git Operations Normal ✓
**Test**:
```bash
git status
git log --oneline -5
git branch -a
```
**Expected**: All commands succeed, no GitButler references
**On Failure**: Git corruption, restore from backup

---

## Rollback Strategy

### Full Rollback (Nuclear Option)
If removal process fails catastrophically:

```bash
# 1. Restore gitbutler/workspace branch
git checkout -b gitbutler/workspace gitbutler-backup-2025-10-30

# 2. Verify all 29 commits present
git log --oneline | head -30

# 3. Push to remote (restore remote branch)
git push -u origin gitbutler/workspace

# 4. Resume normal work
git checkout gitbutler/workspace
```

### Partial Rollback (Per-Phase)
- **Phase 1 failure**: `git merge --abort`, stay on main
- **Phase 2 failure**: Recreate branches from tags
- **Phase 3 failure**: No rollback needed (metadata regenerates)
- **Phase 4 failure**: Reinstall app from trash or web
- **Phase 5 failure**: `git revert <doc-commit>`

---

## Testing Strategy

### Pre-Removal Tests (Before Phase 1)
1. **Commit verification**: `git log gitbutler/workspace --oneline | wc -l` (should be 29+ ahead)
2. **File verification**: `ls PRPs/executed/ | wc -l` (should include A-E)
3. **Branch verification**: `git branch -a | grep gitbutler` (should show workspace)

### Mid-Removal Tests (After Each Phase)
1. **Phase 1**: Run Gate 1 + Gate 2
2. **Phase 2**: Run Gate 3
3. **Phase 3**: Run Gate 4
4. **Phase 4**: Verify `which but` returns nothing
5. **Phase 5**: Verify no broken markdown links

### Post-Removal Tests (After Phase 5)
1. **Integration test**: Create new git worktree
   ```bash
   git worktree add ../test-worktree -b test-branch
   cd ../test-worktree
   touch test.txt
   git add test.txt
   git commit -m "Test commit"
   cd ../ctx-eng-plus
   git worktree remove ../test-worktree
   ```
2. **Documentation test**: Open CLAUDE.md, verify all links clickable
3. **Context test**: Run `uv run ce update-context` (should succeed)

---

## Success Criteria

- ✅ All 29 commits merged to main
- ✅ No GitButler branches (local or remote)
- ✅ No `.gitbutler/` directory
- ✅ GitButler app removed (if Phase 4 executed)
- ✅ Documentation references accurate
- ✅ Git worktree workflow is primary method
- ✅ `archive/gitbutler/` preserved for historical reference
- ✅ All validation gates pass
- ✅ Git operations work normally

---

## Time Estimate Breakdown

| Phase | Time | Risk | Dependencies |
|-------|------|------|--------------|
| Phase 1: Merge to main | 10-15 min | MEDIUM | None |
| Phase 2: Remove branches | 5 min | LOW | Phase 1 ✓ |
| Phase 3: Remove metadata | 5 min | LOW | Phase 2 ✓ |
| Phase 4: Uninstall app | 2 min | LOW | Phase 3 ✓ (optional) |
| Phase 5: Clean docs | 15-20 min | LOW | Phase 4 ✓ |
| **Total** | **37-47 min** | - | - |

**Buffer for issues**: +15 minutes
**Total with buffer**: 50-65 minutes

---

## PRP Breakdown Recommendations

**Option A: Single PRP** (Recommended)
- All phases in one PRP
- Sequential execution
- Faster completion
- Lower overhead

**Option B: Multi-PRP** (If issues expected)
- PRP-1: Phase 1 (merge to main) - CRITICAL
- PRP-2: Phases 2-5 (cleanup) - LOW RISK
- Allows validation between critical and non-critical steps

**Recommendation**: **Option A** - low risk after Phase 1 completes, no dependencies between cleanup phases.

---

## Dependencies

**Hard Dependencies**:
- Git repository in healthy state (no uncommitted changes)
- Network access (for `git push` operations)
- Permissions to delete branches and files

**Soft Dependencies**:
- GitButler app not running (Phase 4)
- No other terminals with active git operations

**Blocker Check**:
```bash
# Check for uncommitted changes
git status

# Check for active git operations
ps aux | grep -i git | grep -v grep

# Check GitButler app running
ps aux | grep -i gitbutler | grep -v grep
```

---

## Notes

**Why Remove GitButler?**
1. **PRP-C Decision**: Migrated to native git worktrees (simpler, universal)
2. **Reduced Complexity**: One less tool to maintain
3. **Universal Workflow**: Git worktrees work everywhere, no special setup
4. **Bash Permission**: `Bash(but:*)` already removed (PRP-D)

**What We Keep**:
- `archive/gitbutler/` - Historical documentation (3 files, 58KB)
- GitButler comparison table in CLAUDE.md (educational reference)

**What We Lose**:
- GitButler UI for virtual branches (replaced by git worktree CLI)
- Real-time conflict detection UI (replaced by merge-time detection)

**Future-Proofing**:
- If GitButler needed again: Reinstall app, restore from archive
- Archive preserved for reference and potential restoration
- Git history unchanged (all commits preserved)

---

## Open Questions

1. **Q**: Keep `feat/gitbutler` branch?
   **A**: Delete if not actively used, check first with `git log feat/gitbutler`

2. **Q**: Keep GitButler app for other projects?
   **A**: Phase 4 is optional, skip if app useful elsewhere

3. **Q**: Update Linear issue if this becomes a PRP?
   **A**: Yes, create issue titled "Complete GitButler Removal"

4. **Q**: Any CI/CD changes needed?
   **A**: No, CI runs on main branch (no GitButler integration)

---

## Approval Checklist

Before executing this plan:
- [ ] User confirms 29 commits are valuable (not experimental)
- [ ] User confirms no other repos depend on gitbutler/workspace branch
- [ ] User confirms GitButler app can be uninstalled (or skip Phase 4)
- [ ] Backup tag created: `gitbutler-backup-2025-10-30`
- [ ] Current working directory clean: `git status`

---

**Next Steps**:
1. Review this initial plan
2. Generate PRP(s) using `/batch-gen-prp` or `/generate-prp`
3. Peer review generated PRP(s)
4. Execute approved PRP(s)
5. Run `/update-context` to sync system state
