# Tool & Permission Lockdown - Revised Execution Plan (REPLKAN)

**Date**: 2025-10-29
**Status**: READY FOR EXECUTION
**Source Plan**: TOOL-PERMISSION-LOCKDOWN-PLAN.md

---

## 🎯 EXECUTION SUMMARY

**Completed**:
- ✅ **Plugin Fix**: Removed 5 non-existent plugins from enabledPlugins (line .claude/settings.local.json:188)

**Remaining Work**:
- Break down into 6 PRPs across 3 stages
- Execute Stage 1 (3 PRPs) in parallel
- Execute Stage 2 (2 PRPs) in parallel
- Execute Stage 3 (1 PRP) sequentially

**Total Time Estimate**:
- Sequential: ~3-4 hours
- Parallel (this plan): ~1.5-2 hours (50% time reduction)

---

## 📋 STAGE BREAKDOWN

### **Stage 1: Foundation** (stage-1-parallel)
**Dependencies**: None
**Execution**: Parallel
**Estimated Time**: 30-45 minutes (parallel)

| PRP ID | Title | Scope | Lines | Risk |
|--------|-------|-------|-------|------|
| **PRP-A** | Tool Deny List Implementation | Add 55 MCP tools to deny list | ~200 | LOW |
| **PRP-B** | Tool Usage Guide Creation | Create TOOL-USAGE-GUIDE.md | ~400 | LOW |
| **PRP-C** | GitButler→Worktree Migration | Remove GitButler, add worktree docs | ~500 | MEDIUM |

**Why Parallel**: These tasks are completely independent:
- PRP-A: Modifies .claude/settings.local.json (permissions only)
- PRP-B: Creates new file TOOL-USAGE-GUIDE.md
- PRP-C: Modifies CLAUDE.md (GitButler section only)

**Output**:
- Deny list active (tools removed from context)
- Tool usage guide available for reference
- Worktree workflow documented

---

### **Stage 2: Integration** (stage-2-parallel)
**Dependencies**: Stage 1 complete
**Execution**: Parallel
**Estimated Time**: 30-45 minutes (parallel)

| PRP ID | Title | Scope | Lines | Risk |
|--------|-------|-------|-------|------|
| **PRP-D** | Command Permission Lists | Add auto-allow, ask-first patterns | ~300 | MEDIUM |
| **PRP-E** | Documentation Updates | Update CLAUDE.md, slash commands | ~400 | LOW |

**Why Parallel**: These tasks have different scopes:
- PRP-D: Modifies .claude/settings.local.json (permissions only)
- PRP-E: Modifies CLAUDE.md (multiple sections), slash command files

**Dependencies**:
- PRP-D depends on PRP-B (needs tool usage guide for reference)
- PRP-E depends on PRP-C (needs worktree docs to reference)
- But D and E don't depend on each other → can run in parallel

**Output**:
- Command permissions locked (auto-allow, ask-first lists)
- All documentation updated and consistent

---

### **Stage 3: Validation** (stage-3-sequential)
**Dependencies**: Stages 1 & 2 complete
**Execution**: Sequential (only 1 PRP)
**Estimated Time**: 20-30 minutes

| PRP ID | Title | Scope | Lines | Risk |
|--------|-------|-------|-------|------|
| **PRP-F** | Comprehensive Validation | Test all changes, measure impact | ~100 | LOW |

**Why Sequential**: Must run after all other changes complete

**Validation Tasks**:
- Token reduction measurement (before/after)
- Command permission testing
- MCP tool access testing
- Git worktree workflow testing (conflict resolution)
- GitButler reference removal verification

**Output**:
- Validated system
- Metrics confirmed (~44k token reduction)
- All workflows tested and working

---

## 🔄 PARALLEL EXECUTION STRATEGY

### Stage 1 Execution Plan

**Setup**:
```bash
# Create 3 git worktrees for parallel PRP development
git worktree add ../ctx-eng-plus-prp-a -b prp-a-tool-deny-list
git worktree add ../ctx-eng-plus-prp-b -b prp-b-tool-usage-guide
git worktree add ../ctx-eng-plus-prp-c -b prp-c-worktree-migration
```

**Parallel Execution**:
- Open 3 separate Claude Code sessions (or sequential with worktree switching)
- Each session works in its respective worktree
- No conflicts possible (different files/sections)

**Integration**:
```bash
# Merge PRPs in sequence
cd ../ctx-eng-plus-prp-a && gh pr create && gh pr merge
cd ../ctx-eng-plus-prp-b && git merge main && gh pr create && gh pr merge
cd ../ctx-eng-plus-prp-c && git merge main && gh pr create && gh pr merge
```

### Stage 2 Execution Plan

**Setup**:
```bash
# Update main, create 2 new worktrees
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git pull
git worktree add ../ctx-eng-plus-prp-d -b prp-d-command-permissions
git worktree add ../ctx-eng-plus-prp-e -b prp-e-doc-updates
```

**Parallel Execution**:
- 2 sessions, same pattern as Stage 1
- PRP-D and PRP-E are independent

**Integration**: Same merge sequence as Stage 1

### Stage 3 Execution Plan

**Setup**:
```bash
# Single worktree
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git pull
git worktree add ../ctx-eng-plus-prp-f -b prp-f-validation
```

**Sequential Execution**:
- Run comprehensive validation
- Measure all metrics
- Document results

---

## 📄 PRP DETAILS

### **PRP-A: Tool Deny List Implementation** (stage-1-parallel)

**Objective**: Add 55 MCP tools to deny list, reducing context by ~44k tokens

**Scope**:
- File: `.claude/settings.local.json`
- Action: Add 55 tools to `permissions.deny` array
- Verification: Ensure 9 Linear tools + Serena + thinking + context7 remain in allow list

**Tools to Deny** (55 total):
- Filesystem: 8 tools (read_file, write_file, edit_file, etc.)
- Git: 5 tools (git_status, git_diff, git_log, etc.)
- GitHub: 26 tools (create_pull_request, list_issues, etc.)
- Repomix: 4 tools (pack_codebase, etc.)
- Playwright: 6 tools (navigate, screenshot, etc.)
- Perplexity: 1 tool (perplexity_ask)
- Syntropy: 5 tools (init_project, get_system_doc, etc.)

**Keep in Allow** (32 tools):
- Serena: 11 tools
- Linear: 9 tools
- Context7: 2 tools
- Thinking: 1 tool
- Syntropy: 2 tools (healthcheck, knowledge_search)
- IDE: 2 tools
- MCP system: ~5 tools

**Size**: ~200 lines of changes
**Risk**: LOW (reversible, no data loss)
**Time**: 15-20 minutes

**Success Criteria**:
- [ ] 55 tools added to deny list
- [ ] All kept tools verified in allow list
- [ ] `/mcp` reconnect successful
- [ ] `/doctor` shows reduced token count

---

### **PRP-B: Tool Usage Guide Creation** (stage-1-parallel)

**Objective**: Create authoritative TOOL-USAGE-GUIDE.md for tool selection

**Scope**:
- File: Create `TOOL-USAGE-GUIDE.md` (new file)
- Sections: 6 sections (philosophy, decision tree, common tasks, anti-patterns, quick reference, migration)

**Content Structure**:
1. **Philosophy** - Native first, MCP when unique value
2. **Decision Tree** - "Need to... → Use this tool" mapping
3. **Common Tasks** - Table with examples
4. **Anti-Patterns** - What NOT to do
5. **Tool Quick Reference** - Native + MCP tools categorized
6. **Migration Table** - Old tool → New tool mapping

**Size**: ~400 lines
**Risk**: LOW (new file, no modifications)
**Time**: 20-25 minutes

**Success Criteria**:
- [ ] All 6 sections complete
- [ ] Decision tree clear and comprehensive
- [ ] Common tasks cover 90% of use cases
- [ ] Migration table complete (all denied tools mapped)
- [ ] File renders correctly in markdown

---

### **PRP-C: GitButler→Worktree Migration** (stage-1-parallel)

**Objective**: Remove GitButler integration, replace with git worktree workflow

**Scope**:
- File: `CLAUDE.md` (remove GitButler section, add Worktree section)
- Files: Archive GitButler docs to `archive/`
- Hooks: Remove GitButler hooks from `.claude/settings.local.json`

**Changes**:
1. **Remove from CLAUDE.md**:
   - GitButler Integration section (~100 lines)
   - GitButler hooks references

2. **Add to CLAUDE.md**:
   - "Parallel PRP Development with Git Worktrees" section (~200 lines)
   - Includes: setup, workflow, conflict resolution, comparison table

3. **Archive Documentation**:
   - `test-target/GITBUTLER-INTEGRATION-GUIDE.md` → `archive/`
   - `examples/GITBUTLER-REFERENCE.md` → `archive/`
   - `examples/gitbutler-test-automation.py` → `archive/`

4. **Remove Hooks**:
   - SessionStart hook (but status check)
   - PreToolUse hooks (but status, virtual branch reminders)

**Size**: ~500 lines (additions + deletions)
**Risk**: MEDIUM (hooks removal affects workflow)
**Time**: 25-30 minutes

**Success Criteria**:
- [ ] GitButler section removed from CLAUDE.md
- [ ] Worktree section added with all subsections
- [ ] Hooks removed from settings
- [ ] GitButler docs archived
- [ ] No "gitbutler" mentions in active docs (verified with Grep)

---

### **PRP-D: Command Permission Lists** (stage-2-parallel)

**Objective**: Lock down command permissions with auto-allow and ask-first lists

**Scope**:
- File: `.claude/settings.local.json`
- Action: Add ~55 command patterns to permissions

**Auto-Allow List** (~35 patterns):
- Navigation: ls, cd, pwd, tree, which, etc.
- Git: git:* (all subcommands including worktree, merge, etc.)
- UV/Python: uv:*, uvx:*, pytest:*, python:*
- GitHub: gh:* (all subcommands)
- Reading (fallback): cat:*, head:*, tail:*, less:*, more:*
- Search (fallback): grep:*, find:*, rg:*
- Environment: env:*, printenv:*, echo:*, export:*, source:*
- Process info: ps:*, jobs:*, pgrep:*
- Project-specific: mkdir/rm/touch for test-target, tools, PRPs, examples, tmp

**Ask-First List** (~20 patterns):
- File ops: rm:*, mv:*, cp:* (outside project)
- Directory ops: mkdir:*, rmdir:* (outside project)
- Permissions: chmod:*, chown:*, chgrp:*
- Process control: kill:*, killall:*, pkill:*
- Network: curl:*, wget:*, nc:*, ssh:*, scp:*, rsync:*
- Package management: brew install:*, npm install:*, pip install:*
- System: sudo:*
- Editors: vim:*, nano:*, emacs:*

**Never Allow** (~15 patterns - documented, not enforced):
- Destructive: rm -rf /:*, dd:*, mkfs:*, shred:*
- System control: shutdown:*, reboot:*, halt:*, systemctl:*
- User management: useradd:*, userdel:*, passwd:*
- Kernel: modprobe:*, insmod:*, rmmod:*
- Disk: fdisk:*, parted:*, mount:*, umount:*

**Size**: ~300 lines of changes
**Risk**: MEDIUM (may block legitimate commands if patterns wrong)
**Time**: 20-25 minutes

**Success Criteria**:
- [ ] Permission syntax verified (test 2-3 patterns first)
- [ ] Auto-allow patterns added
- [ ] Ask-first patterns added
- [ ] Test commands: `git status` (no prompt), `rm /tmp/test` (prompt)
- [ ] Common workflow commands work without prompts

---

### **PRP-E: Documentation Updates** (stage-2-parallel)

**Objective**: Update all documentation to reference new tools, workflows, and permissions

**Scope**:
- File: `CLAUDE.md` (multiple sections)
- Files: Slash command docs (`.claude/commands/execute-prp.md`, `.claude/commands/peer-review.md`)
- Search: All files for GitButler references

**CLAUDE.md Updates**:
1. Update "Quick Tool Selection" section with TOOL-USAGE-GUIDE.md link
2. Remove outdated Syntropy MCP tool recommendations
3. Add command permission reference section
4. Update troubleshooting section

**Slash Command Updates**:
1. `/execute-prp` command:
   - Replace GitButler workflow with worktree workflow
   - Add conflict resolution procedures

2. `/peer-review` command:
   - Replace `but status` with `git worktree list`
   - Add worktree-specific review procedures

**GitButler Reference Cleanup**:
- Search: `Grep pattern="gitbutler" -i`
- Search: `Grep pattern="but " output_mode=files_with_matches`
- Search: `Grep pattern="virtual branch"`
- Replace all with worktree equivalents

**Size**: ~400 lines of changes
**Risk**: LOW (documentation only)
**Time**: 25-30 minutes

**Success Criteria**:
- [ ] Slash command files located and updated
- [ ] CLAUDE.md all sections updated
- [ ] Tool usage guide linked
- [ ] No GitButler references remain (verified)
- [ ] All worktree examples correct

---

### **PRP-F: Comprehensive Validation** (stage-3-sequential)

**Objective**: Validate all changes, measure impact, ensure system works

**Scope**:
- Testing: All new workflows and permissions
- Measurement: Token reduction, command access
- Verification: No regressions

**Validation Tasks**:

1. **Token Reduction Measurement**:
   - [ ] Run `/doctor` and note MCP tools context tokens
   - [ ] Expected: ~2k tokens (was ~46k)
   - [ ] Document actual reduction

2. **Command Permission Testing**:
   - [ ] Auto-allow: Test `git status`, `ls`, `cat README.md`, `grep TODO`
   - [ ] Ask-first: Test `rm /tmp/test.txt`, `curl https://example.com`
   - [ ] Verify no unexpected prompts for common commands

3. **MCP Tool Access Testing**:
   - [ ] Try allowed: `serena_find_symbol`, `linear_list_issues`
   - [ ] Verify denied tools don't appear or fail gracefully
   - [ ] Count available MCP tools (should be ~32)

4. **Tool Usage Guide Verification**:
   - [ ] All common tasks covered
   - [ ] Migration table complete
   - [ ] Examples clear and actionable
   - [ ] Renders correctly

5. **Git Worktree Workflow Testing** (CRITICAL):
   - [ ] Create test worktree: `git worktree add ../ctx-eng-plus-test -b test-branch`
   - [ ] Make changes in worktree
   - [ ] Commit and push from worktree
   - [ ] Create intentional conflict with main
   - [ ] Resolve conflict using Read + Edit tools
   - [ ] Run tests: `cd tools && uv run pytest tests/ -v`
   - [ ] Verify tests pass
   - [ ] Remove worktree: `git worktree remove ../ctx-eng-plus-test`

6. **GitButler Reference Removal**:
   - [ ] Run `Grep pattern="gitbutler" -i`
   - [ ] Verify no matches in active docs
   - [ ] Check `but ` commands removed

7. **System Health**:
   - [ ] Run `/doctor`
   - [ ] No plugin errors
   - [ ] All MCP servers connected
   - [ ] Context token count reduced

**Size**: ~100 lines of validation code/notes
**Risk**: LOW (testing only, no changes)
**Time**: 20-30 minutes

**Success Criteria**:
- [ ] All validation tasks pass
- [ ] Token reduction confirmed (~44k)
- [ ] No workflow regressions
- [ ] Worktree workflow fully functional with conflict resolution
- [ ] Documentation complete and accurate

---

## 📊 COMPARISON: Original vs REPLKAN

| Aspect | Original Plan | REPLKAN |
|--------|---------------|---------|
| **Tasks** | 7 sequential tasks | 6 PRPs in 3 stages |
| **Execution** | Sequential only | 2 parallel stages + 1 sequential |
| **Time** | 3-4 hours | 1.5-2 hours (50% reduction) |
| **Isolation** | Single branch | Multiple worktrees (conflict-free) |
| **Rollback** | Per-task | Per-PRP (cleaner) |
| **Testing** | End only | Per-PRP + comprehensive end |
| **Documentation** | Embedded in plan | Separate PRP docs |

**Key Advantages**:
- ✅ 50% faster (parallel execution)
- ✅ Better isolation (worktrees prevent conflicts)
- ✅ Easier rollback (per-PRP granularity)
- ✅ Clearer scope (one PRP = one concern)
- ✅ Better tracking (PRP status vs task status)

---

## 🎯 EXECUTION SEQUENCE

### Step 1: Plugin Fix
✅ **COMPLETED** - Removed 5 non-existent plugins from enabledPlugins

### Step 2: Create PRP Documents
Generate 6 PRP markdown files in `PRPs/feature-requests/`:
- PRP-A-tool-deny-list.md
- PRP-B-tool-usage-guide.md
- PRP-C-worktree-migration.md
- PRP-D-command-permissions.md
- PRP-E-documentation-updates.md
- PRP-F-validation.md

### Step 3: Peer Review PRPs
Review all 6 PRPs for:
- Scope accuracy
- Risk assessment
- Success criteria completeness
- Time estimates
- Dependencies

### Step 4: Execute Stage 1 (Parallel)
```bash
# Create worktrees
git worktree add ../ctx-eng-plus-prp-a -b prp-a-tool-deny-list
git worktree add ../ctx-eng-plus-prp-b -b prp-b-tool-usage-guide
git worktree add ../ctx-eng-plus-prp-c -b prp-c-worktree-migration

# Execute PRPs (parallel sessions or sequential with switching)
# PRP-A: 15-20 min
# PRP-B: 20-25 min
# PRP-C: 25-30 min
# Total parallel time: 30-45 min

# Merge in sequence
# (Later ones may need conflict resolution from earlier merges)
```

### Step 5: Execute Stage 2 (Parallel)
```bash
# Update and create worktrees
git pull
git worktree add ../ctx-eng-plus-prp-d -b prp-d-command-permissions
git worktree add ../ctx-eng-plus-prp-e -b prp-e-doc-updates

# Execute PRPs
# PRP-D: 20-25 min
# PRP-E: 25-30 min
# Total parallel time: 30-45 min

# Merge in sequence
```

### Step 6: Execute Stage 3 (Sequential)
```bash
# Update and create worktree
git pull
git worktree add ../ctx-eng-plus-prp-f -b prp-f-validation

# Execute PRP-F
# Time: 20-30 min

# Merge
```

### Step 7: Final Cleanup
```bash
# Remove all worktrees
git worktree prune

# Verify final state
/doctor
git status
```

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Worktree Merge Conflicts
**Likelihood**: MEDIUM
**Impact**: LOW
**Mitigation**:
- Stage 1 PRPs edit different files (unlikely conflicts)
- If conflicts occur, use Read + Edit tools to resolve
- Test resolution before merge

### Risk 2: Command Pattern Syntax Wrong
**Likelihood**: MEDIUM
**Impact**: MEDIUM
**Mitigation**:
- PRP-D includes syntax verification step
- Test 2-3 patterns before full rollout
- Easy rollback (revert settings file)

### Risk 3: Tool Deny List Too Aggressive
**Likelihood**: LOW
**Impact**: LOW
**Mitigation**:
- PRP-A keeps all essential tools (Linear, Serena, etc.)
- Verification step ensures kept tools remain accessible
- Easy rollback (remove from deny list)

### Risk 4: GitButler Hook Removal Breaks Workflow
**Likelihood**: LOW
**Impact**: MEDIUM
**Mitigation**:
- PRP-C includes comprehensive worktree documentation
- PRP-F tests new workflow thoroughly
- Rollback: Re-add hooks from git history

---

## 📈 SUCCESS METRICS

**Token Efficiency**:
- Before: ~46k tokens for MCP tools
- After: ~2k tokens for MCP tools
- Reduction: ~44k tokens (96% reduction)

**Tool Count**:
- Before: 87 MCP tools
- After: 32 MCP tools (11 Serena + 9 Linear + 2 Context7 + 1 thinking + 2 Syntropy + rest)
- Reduction: 55 tools (63%)

**Command Permissions**:
- Auto-allow: ~35 patterns (no interruptions)
- Ask-first: ~20 patterns (safety gate)
- Clear guidance: 100% of common operations covered

**Time Efficiency**:
- Sequential: 3-4 hours
- Parallel: 1.5-2 hours
- Savings: 50%

**Documentation**:
- New guide: TOOL-USAGE-GUIDE.md
- Updated: CLAUDE.md (multiple sections)
- Migrated: GitButler → Worktree workflow
- Complete: 100% coverage

---

## 🔄 ROLLBACK STRATEGY

**Per-PRP Rollback**:
```bash
# Rollback specific PRP
git revert <commit-hash>

# Or restore from backup
git stash pop  # If stashed before execution
```

**Full Rollback**:
```bash
# Restore entire settings file
git checkout HEAD~6 .claude/settings.local.json

# Restore CLAUDE.md
git checkout HEAD~6 CLAUDE.md

# Reconnect MCP
/mcp

# Verify
/doctor
```

**Backup Before Execution**:
```bash
# Automatic via git history
# Manual backup
git stash push -m "Pre-lockdown backup" -- .claude/ CLAUDE.md
```

---

## 📝 NEXT STEPS

1. ✅ **Plugin fix** - COMPLETED
2. ⏳ **Create PRP documents** - IN PROGRESS (next)
3. ⏳ **Peer review PRPs** - PENDING
4. ⏳ **Execute Stage 1** - PENDING
5. ⏳ **Execute Stage 2** - PENDING
6. ⏳ **Execute Stage 3** - PENDING
7. ⏳ **Final validation** - PENDING

---

**Status**: ✅ REPLKAN COMPLETE - READY TO GENERATE PRPS
**Next Action**: Generate 6 PRP documents for peer review
**Estimated Total Time**: 1.5-2 hours (parallel execution)
**Expected Completion**: Same day
