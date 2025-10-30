# Tool & Permission Lockdown Plan

**Date**: 2025-10-29
**Status**: PENDING APPROVAL

---

## 📋 EXECUTIVE SUMMARY

This plan addresses five critical areas:
1. Fix plugin marketplace configuration (5 failed plugins)
2. Create MCP tool deny list (55 tools to remove)
3. Evaluate GitButler extension necessity (verdict: remove)
4. Create tool usage guide (replace obsolete documentation)
5. Create definitive bash command lists (locked permissions)

**Impact**: ~45,000 token reduction, clearer permissions, more efficient tooling, authoritative tool usage guide

---

## 1. PLUGIN FIX

### Current Issue
```
Plugin Errors:
└ 5 plugin error(s) detected:
  └ python-development@claude-code-workflows: Plugin not found
  └ agent-orchestration@claude-code-workflows: Plugin not found
  └ backend-development@claude-code-workflows: Plugin not found
  └ api-scaffolding@claude-code-workflows: Plugin not found
  └ llm-application-dev@claude-code-workflows: Plugin not found
```

### Root Cause
Plugins reference `claude-code-workflows` marketplace, but actual source is `https://github.com/wshobson/agents`

### Solution
Update `.claude/settings.local.json` or `.claude/config.json` to:
- Remove marketplace reference
- Add direct GitHub source for plugins
- OR: Remove plugins if not actively used

---

## 2. MCP TOOL DENY LIST

### Overview
**Total Tools**: 87 MCP tools
**Recommended Deny**: 55 tools
**Recommended Keep**: 32 tools
**Token Savings**: ~45,000 tokens

### ❌ DENY: Filesystem Tools (8 tools)

**Tools to Deny**:
- `filesystem_read_file`
- `filesystem_read_text_file`
- `filesystem_write_file`
- `filesystem_edit_file`
- `filesystem_list_directory`
- `filesystem_search_files`
- `filesystem_directory_tree`
- `filesystem_get_file_info`

**Rationale**:
- Native Read tool: Direct file reading, faster, no MCP overhead
- Native Write tool: Direct file writing, simpler
- Native Edit tool: Precise old_string/new_string replacement
- Native Glob tool: Optimized file pattern matching
- Bash commands: `ls`, `tree`, `stat` for quick info

**Token Savings**: ~6,400 tokens (8 tools × 800 avg)

---

### ❌ DENY: Git Tools (5 tools)

**Tools to Deny**:
- `git_git_status`
- `git_git_diff`
- `git_git_log`
- `git_git_add`
- `git_git_commit`

**Rationale**:
- Native bash `git` commands already approved
- More flexible (all git options available)
- Standard, universal interface
- Already familiar to users
- Direct execution, no wrapper overhead

**Example Equivalence**:
- `git_git_status` → `git status`
- `git_git_diff` → `git diff` (with any flags)
- `git_git_log --max_count=10` → `git log -10` (more options)

**Token Savings**: ~4,000 tokens (5 tools × 800 avg)

---

### ❌ DENY: GitHub Tools (26 tools)

**Tools to Deny**:
- `github_create_or_update_file`
- `github_search_repositories`
- `github_create_repository`
- `github_get_file_contents`
- `github_push_files`
- `github_create_issue`
- `github_create_pull_request`
- `github_fork_repository`
- `github_create_branch`
- `github_list_commits`
- `github_list_issues`
- `github_update_issue`
- `github_add_issue_comment`
- `github_search_code`
- `github_search_issues`
- `github_search_users`
- `github_get_issue`
- `github_get_pull_request`
- `github_list_pull_requests`
- `github_create_pull_request_review`
- `github_merge_pull_request`
- `github_get_pull_request_files`
- `github_get_pull_request_status`
- `github_update_pull_request_branch`
- `github_get_pull_request_comments`
- `github_get_pull_request_reviews`

**Rationale**:
- Official GitHub CLI (`gh`) is more comprehensive
- Better documented, actively maintained by GitHub
- More flexible (supports all GitHub features)
- Already available via Bash
- Standard tool for GitHub operations

**Example Equivalence**:
- `github_create_pull_request` → `gh pr create --title "..." --body "..."`
- `github_list_issues` → `gh issue list --state open`
- `github_merge_pull_request` → `gh pr merge 123`

**Token Savings**: ~20,800 tokens (26 tools × 800 avg)

---

### ❌ DENY: Repomix Tools (4 tools)

**Tools to Deny**:
- `repomix_pack_codebase`
- `repomix_grep_repomix_output`
- `repomix_read_repomix_output`
- `repomix_pack_remote_repository`

**Rationale**:
- Native exploration is more efficient for incremental analysis
- Task agent with Explore subagent for codebase questions
- Glob + Grep + Read for targeted searches
- Repomix creates monolithic output (less efficient)
- Rare use case in practice

**Alternative Workflow**:
- Instead of packing entire codebase → Use Glob for patterns
- Instead of grep on packed output → Use Grep directly
- Instead of read packed output → Use Read on specific files
- For exploration → Use Task agent (Explore)

**Token Savings**: ~3,200 tokens (4 tools × 800 avg)

---

### ❌ DENY: Playwright Tools (6 tools)

**Tools to Deny**:
- `playwright_navigate`
- `playwright_screenshot`
- `playwright_click`
- `playwright_fill`
- `playwright_evaluate`
- `playwright_get_visible_text`

**Rationale**:
- Specialized browser automation (rare use case)
- Context Engineering CLI project doesn't require UI testing
- WebFetch handles most web content needs
- If needed, can use bash + playwright CLI directly

**Use Cases Not Needed**:
- Web scraping → WebFetch sufficient
- UI testing → Not part of CLI tooling project
- Screenshot capture → Not needed for CLI tools
- Interactive web → Not part of workflow

**Token Savings**: ~4,800 tokens (6 tools × 800 avg)

---

### ❌ DENY: Perplexity Tools (1 tool)

**Tools to Deny**:
- `perplexity_perplexity_ask`

**Rationale**:
- Native WebSearch provides equivalent capability
- Integrated search in Claude Code
- No third-party API dependency
- Simpler, more direct

**Token Savings**: ~800 tokens

---

### ❌ DENY: Syntropy System Tools (5 tools)

**Tools to Deny**:
- `init_project` (rare use, one-time setup)
- `get_system_doc` (use native Read for .ce/ files)
- `get_user_doc` (use native Read for user docs)
- `get_summary` (use bash commands or native tools)
- `denoise` (specialized, rare use)

**Rationale**:
- `init_project`: One-time setup, rarely needed
- `get_system_doc`, `get_user_doc`: Native Read is more direct
- `get_summary`: Can construct from bash/native tools
- `denoise`: Specialized document compression, rare use case

**Token Savings**: ~4,000 tokens (5 tools × 800 avg)

---

### ✅ KEEP: Linear Tools (ALL - 9 tools)

**Tools to Keep**:
- `linear_create_issue`
- `linear_get_issue`
- `linear_list_issues`
- `linear_update_issue`
- `linear_list_projects`
- `linear_list_teams`
- `linear_list_users`
- `linear_get_team`
- `linear_create_project`

**Rationale**:
- No native CLI equivalent (Linear CLI is limited)
- Critical for /generate-prp workflow
- Provides API access for issue management
- Heavily integrated into project workflow
- `.ce/linear-defaults.yml` configuration

**Use Cases**:
- Auto-create issues from PRPs
- Link PRPs to Linear issues
- Track project progress
- Query issue status

---

### ✅ KEEP: Syntropy Specialized Tools (2 tools)

**Tools to Keep**:
- `healthcheck`
- `knowledge_search`

**Rationale**:
- `healthcheck`: Debugging MCP server connectivity, diagnostics
- `knowledge_search`: Semantic search across PRPs, memories, examples

**Use Cases**:
- `healthcheck --detailed=true`: Diagnose MCP issues
- `knowledge_search`: Find relevant patterns, PRPs, examples

---

### ✅ KEEP: Core Tools (EXCEPTIONS)

**Always Keep (per requirements)**:
- All Serena tools (11 tools) - Code symbol analysis
- `thinking_sequentialthinking` (1 tool) - Complex reasoning
- `context7_resolve_library_id` (1 tool) - Library docs
- `context7_get_library_docs` (1 tool) - Library docs

---

## 3. GITBUTLER EXTENSION EVALUATION

### Current State
- Hooks configured: SessionStart, PreToolUse, Edit/Write
- Commands: `but status`, `but branch new`, `but commit`, etc.
- Integration: CLAUDE.md has extensive GitButler documentation

### Evaluation

**GitButler Provides**:
- Virtual branch UI visualization
- Parallel branch development without checkout
- Conflict detection UI
- CLI wrapper around git operations

**Native Git Provides**:
- Standard `git branch`, `git checkout`, `git commit`
- Universal, predictable interface
- More flexible (all git features)
- No additional dependencies

### Verdict: ❌ NOT NEEDED

**Reasoning**:
1. **I operate at CLI level, not UI level**: Virtual branch visualization is user-facing, not relevant to my operations
2. **Native git is more universal**: GitButler CLI (`but`) is just another git wrapper
3. **Flexibility**: Standard git commands support all operations and options
4. **Simplicity**: Fewer abstractions, more predictable behavior
5. **Hooks add complexity**: Additional layer that can cause confusion

**Recommendation**: Remove GitButler references from CLAUDE.md, remove hooks

### Replacement: Git Worktree Parallel PRP Workflow

**Problem**: GitButler provided parallel PRP development without branch switching. Need equivalent using standard git.

**Solution**: Git worktrees provide the same capability natively.

#### Git Worktree Strategy

**Concept**: Each PRP gets its own working directory (worktree) linked to the same git repository. Work on multiple PRPs simultaneously without branch switching.

#### ⚠️ Git Worktree Constraints

**CRITICAL**: Cannot check out the same branch in multiple worktrees simultaneously.

**This FAILS**:
```bash
# Main repo on 'main' branch
git worktree add ../ctx-eng-plus-prp-30 main  # ❌ ERROR
# Error: 'main' is already checked out at '/Users/.../ctx-eng-plus'
```

**Rules**:
- Main repo should stay on `gitbutler/workspace` or a dedicated branch
- Each PRP worktree MUST use a unique branch name
- Never create worktree for a branch that's already checked out elsewhere
- Solution: Always create new branch: `git worktree add ../path -b new-branch-name`

**Disk Space Impact**:
- Each worktree = full working directory copy
- Main repo: ~500MB
- 3 PRP worktrees: ~1.5GB additional
- Monitor usage: `du -sh ../ctx-eng-plus*`

**Directory Structure**:
```
ctx-eng-plus/               # Main worktree (gitbutler/workspace or main)
├── .git/                   # Git repository
├── tools/
├── PRPs/
└── ...

../ctx-eng-plus-prp-30/     # PRP-30 worktree
├── tools/
├── PRPs/
└── ...

../ctx-eng-plus-prp-31/     # PRP-31 worktree
├── tools/
├── PRPs/
└── ...
```

#### Commands

**Create worktree for new PRP**:
```bash
# From main repo
git worktree add ../ctx-eng-plus-prp-30 -b prp-30-feature

# Or from existing branch
git worktree add ../ctx-eng-plus-prp-30 prp-30-feature
```

**List all worktrees**:
```bash
git worktree list
```

**Work in PRP worktree**:
```bash
cd ../ctx-eng-plus-prp-30
# Make changes with Claude (Edit/Write)
git add .
git commit -m "Implement feature X"
git push -u origin prp-30-feature
```

**Create PR from worktree**:
```bash
cd ../ctx-eng-plus-prp-30
gh pr create --title "PRP-30: Feature" --base main
```

**Remove worktree when done**:
```bash
# From main repo
git worktree remove ../ctx-eng-plus-prp-30

# Or force remove if has uncommitted changes
git worktree remove ../ctx-eng-plus-prp-30 --force
```

**Prune stale worktrees**:
```bash
git worktree prune
```

#### Merge Conflict Resolution

**Scenario 1: Conflicts during PR merge**
```bash
# In main repo, update from remote
git fetch origin
git checkout main
git pull

# Update PRP branch with latest main
cd ../ctx-eng-plus-prp-30
git fetch origin
git merge origin/main

# If conflicts occur:
git status                    # See conflicted files
# Use Read tool to view files with conflict markers
# Use Edit tool to resolve conflicts
git add <resolved-files>
git commit -m "Merge main, resolve conflicts"
git push
```

**Scenario 2: Conflicts between multiple PRPs**
```bash
# Work on PRP-30 and PRP-31 independently
# No conflicts occur until merge time
# Each worktree is isolated

# When merging PRP-30 to main (first):
cd ../ctx-eng-plus-prp-30
gh pr merge <pr-number>       # Merges cleanly

# When merging PRP-31 to main (second):
cd ../ctx-eng-plus-prp-31
git fetch origin
git merge origin/main         # May have conflicts with PRP-30 changes

# Resolve conflicts as above
git status
# Use Read + Edit tools
git add <resolved-files>
git commit -m "Merge main after PRP-30, resolve conflicts"
git push
gh pr merge <pr-number>
```

**Scenario 3: Detecting conflicts early**
```bash
# Periodically sync PRP branch with main
cd ../ctx-eng-plus-prp-30
git fetch origin
git merge origin/main --no-commit --no-ff

# If conflicts, resolve immediately
# If clean, commit
git commit -m "Sync with main"
git push
```

#### Conflict Resolution Best Practices

1. **Read conflicts first**:
   ```bash
   # Use Read tool to see conflict markers
   # <<<<<<< HEAD
   # Your changes
   # =======
   # Their changes
   # >>>>>>> origin/main
   ```

2. **Resolve with Edit tool**:
   - Remove conflict markers
   - Keep correct changes
   - Test the resolution

3. **Verify resolution**:
   ```bash
   cd tools && uv run pytest tests/ -v
   cd tools && uv run ce validate --level all
   ```

4. **Commit resolution**:
   ```bash
   git add <resolved-files>
   git commit -m "Resolve merge conflicts between PRP-X and main"
   ```

#### Advantages over GitButler

1. **Standard git**: No additional tools required
2. **Universal**: Works everywhere git works
3. **Isolated directories**: Each PRP has clean workspace
4. **No abstraction**: Direct git commands
5. **Better IDE support**: Each worktree opens as separate project
6. **No conflicts during work**: Only at merge time (natural)

#### Workflow Comparison

| Task | GitButler | Git Worktree |
|------|-----------|--------------|
| Create PRP workspace | `but branch new prp-30` | `git worktree add ../ctx-eng-plus-prp-30 -b prp-30` |
| Switch context | Automatic (virtual) | `cd ../ctx-eng-plus-prp-30` |
| Commit changes | `but commit prp-30 -m "msg"` | `git commit -m "msg"` (in worktree) |
| View status | `but status` | `git worktree list` |
| Detect conflicts | UI indicator (🔒) | `git merge --no-commit` (manual check) |
| Remove workspace | `but branch delete prp-30` | `git worktree remove ../ctx-eng-plus-prp-30` |

#### Commands to Add to Auto-Allow

```bash
git worktree:*
git merge:*
git fetch:*
git checkout:*
git branch:*
git pull:*
git push:*
```

#### Implementation in Documentation

**Files to Update**:
1. `CLAUDE.md` - Replace GitButler section with worktree guide
2. `.claude/commands/execute-prp.md` - Update workflow references
3. `.claude/commands/peer-review.md` - Update status checks
4. `test-target/GITBUTLER-INTEGRATION-GUIDE.md` - Archive or replace
5. `examples/GITBUTLER-REFERENCE.md` - Archive or replace
6. `examples/gitbutler-test-automation.py` - Archive or remove
7. Any other files found via search

**New CLAUDE.md Section**: "Parallel PRP Development with Git Worktrees"
- **Quick Start**: Creating worktrees
- **Workflow**: Daily operations
- **Conflict Resolution**: Step-by-step procedures with Read/Edit tools
- **Commands**: Reference list (auto-approved)
- **Examples**: Multi-PRP scenarios with conflict resolution
- **Migration**: GitButler → Worktree command mapping

**Search Strategy**:
```bash
# Find all GitButler references
grep -r "gitbutler" --include="*.md" .
grep -r "but " --include="*.md" .
grep -r "virtual branch" --include="*.md" .

# Find in Python/shell files
grep -r "gitbutler" --include="*.py" --include="*.sh" .
```

---

## 4. TOOL USAGE GUIDE CREATION

### Purpose
Create a comprehensive, up-to-date tool usage guide for Claude Code to replace obsolete documentation. This guide will serve as the authoritative reference for tool selection after the lockdown.

### Current Problem
- CLAUDE.md contains outdated tool recommendations
- No clear decision tree for native vs MCP tool selection
- Mixed guidance between different tool categories
- Syntropy MCP tools heavily featured but many being removed

### New Guide Structure

#### TOOL-USAGE-GUIDE.md

**Section 1: Philosophy**
- Native tools first (Read, Write, Edit, Glob, Grep, Bash)
- MCP tools only when unique value (Serena, Linear, specialized)
- Efficiency over features
- Predictability over flexibility

**Section 2: Decision Tree**

```
Need to... → Use this tool
├─ Read file → Read tool (native)
├─ Write new file → Write tool (native)
├─ Edit existing file → Edit tool (native)
├─ Find files by pattern → Glob tool (native)
├─ Search file contents → Grep tool (native)
├─ Run command → Bash tool (native)
├─ Analyze code symbols → Serena MCP tools
├─ Manage Linear issues → Linear MCP tools
├─ Get library docs → Context7 MCP tools
├─ Complex reasoning → Sequential thinking MCP tool
└─ Debug MCP servers → Syntropy healthcheck MCP tool
```

**Section 3: Common Tasks**

| Task | Tool | Example |
|------|------|---------|
| Read configuration | `Read` | `Read pyproject.toml` |
| Update version | `Edit` | `Edit old="1.0.0" new="1.1.0"` |
| Find all tests | `Glob` | `Glob pattern="tests/**/*.py"` |
| Search for TODO | `Grep` | `Grep pattern="TODO"` |
| Git status | `Bash` | `git status` |
| Create PR | `Bash` | `gh pr create` |
| Find function | `Serena` | `serena_find_symbol name_path="MyClass.my_method"` |
| Create Linear issue | `Linear` | `linear_create_issue` |
| Get React docs | `Context7` | `context7_get_library_docs` |

**Section 4: Anti-Patterns**

❌ **DON'T**:
- Use `filesystem_read_file` → Use `Read` instead
- Use `git_git_status` → Use `Bash git status` instead
- Use `github_create_pull_request` → Use `Bash gh pr create` instead
- Use `repomix_pack_codebase` → Use `Glob/Grep/Read` for incremental exploration
- Use bash `cat` for reading → Use `Read` tool instead
- Use bash `echo` for communication → Output text directly

✅ **DO**:
- Use `Read` for all file reading
- Use `Edit` for surgical file changes
- Use `Glob` for file pattern matching
- Use `Grep` for content search
- Use `Bash` for git, gh, uv, pytest commands
- Use `Serena` for code symbol analysis
- Use `Linear` for issue management

**Section 5: Tool Quick Reference**

**Native Tools (Always Use These First)**:
- `Read` - Read files (replaces cat, filesystem_read_file)
- `Write` - Create new files (replaces echo >, filesystem_write_file)
- `Edit` - Modify existing files (replaces sed, filesystem_edit_file)
- `Glob` - Find files by pattern (replaces find, filesystem_search_files)
- `Grep` - Search file contents (replaces grep, search_for_pattern)
- `Bash` - Run commands (git, gh, uv, pytest, etc.)
- `Task` - Complex multi-step operations with specialized agents

**MCP Tools (Use Only These)**:
- `Serena` (11 tools) - Code symbol analysis
  - `serena_find_symbol` - Find function/class definitions
  - `serena_get_symbols_overview` - File structure overview
  - `serena_search_for_pattern` - Regex search in code
  - `serena_find_referencing_symbols` - Find references
  - etc.
- `Linear` (9 tools) - Issue management
  - `linear_create_issue`
  - `linear_get_issue`
  - `linear_list_issues`
  - etc.
- `Context7` (2 tools) - Library documentation
  - `context7_resolve_library_id`
  - `context7_get_library_docs`
- `Thinking` (1 tool) - Complex reasoning
  - `sequentialthinking`
- `Syntropy` (2 tools) - System utilities
  - `healthcheck`
  - `knowledge_search`

**Section 6: Migration from Old Tools**

| Old Tool (Deprecated) | New Tool | Notes |
|-----------------------|----------|-------|
| `filesystem_read_file` | `Read` | Direct, faster |
| `filesystem_write_file` | `Write` | Direct, simpler |
| `filesystem_edit_file` | `Edit` | More precise |
| `filesystem_search_files` | `Glob` | Optimized |
| `git_git_status` | `Bash git status` | More flexible |
| `github_create_pull_request` | `Bash gh pr create` | Official CLI |
| `repomix_pack_codebase` | `Glob/Grep/Read` | Incremental |
| `perplexity_ask` | `WebSearch` | Native search |

### Implementation
- Create `TOOL-USAGE-GUIDE.md` in project root
- Update CLAUDE.md to reference the guide
- Remove outdated tool recommendations from CLAUDE.md
- Add link in implementation checklist

---

## 5. DEFINITIVE COMMAND LISTS (LOCKED)

### Philosophy
- **Auto-allow**: Safe, read-only, frequent operations
- **Ask first**: Potentially destructive or system-wide changes
- **Never allow**: Destructive, system-critical operations

### ⚠️ Permission Syntax Note

**Pattern syntax verification required during Task 5 implementation**:
- Patterns use format: `command:*` for all subcommands
- Path patterns like `rm test-target/**` need syntax verification
- May be glob-style (`**/*.py`) or literal path matching
- Test a few patterns before full rollout to confirm behavior

### 🟢 AUTO-ALLOW List

#### Navigation & File Info
```bash
ls:*
cd:*
pwd:*
tree:*
which:*
whereis:*
stat:*
file:*
```

#### Git Operations (All Subcommands)
```bash
git:*

# Explicitly included (already covered by git:*):
git worktree:*    # Parallel PRP development
git merge:*       # Conflict resolution
git fetch:*       # Update from remote
git checkout:*    # Branch switching
git branch:*      # Branch management
git pull:*        # Pull changes
git push:*        # Push changes
```

#### UV/Python Tooling
```bash
uv:*
uvx:*
pytest:*
python:*
python3:*
```

#### GitHub CLI
```bash
gh:*
```

#### Reading Tools (Fallback Only)
```bash
cat:*     # Allowed but prefer Read tool
head:*    # Allowed but prefer Read tool
tail:*    # Allowed but prefer Read tool
less:*    # Allowed for interactive viewing
more:*    # Allowed for interactive viewing
```

**Note**: These are auto-approved for backward compatibility and edge cases,
but the TOOL-USAGE-GUIDE.md will direct all file reading to the Read tool.

#### Search Tools (Fallback Only)
```bash
grep:*    # Allowed but prefer Grep tool
find:*    # Allowed but prefer Glob tool
rg:*      # Allowed but prefer Grep tool
```

**Note**: These are auto-approved for backward compatibility and edge cases,
but the TOOL-USAGE-GUIDE.md will direct all searching to Grep and Glob tools.

#### Environment
```bash
env:*
printenv:*
echo:*
export:*
source:*
```

#### Process Info (Read-only)
```bash
ps:*
jobs:*
pgrep:*
```

#### Project-Specific Safe Operations
```bash
# Test directory
mkdir test-target/**
touch test-target/**
rm test-target/**
cp test-target/** test-target/**
mv test-target/** test-target/**

# Tools directory
mkdir tools/**
touch tools/**
rm tools/** (exclude pyproject.toml)
cp tools/** tools/**
mv tools/** tools/**

# PRPs directory
mkdir PRPs/**
touch PRPs/**
rm PRPs/**
cp PRPs/** PRPs/**
mv PRPs/** PRPs/**

# Examples directory
mkdir examples/**
touch examples/**
rm examples/**

# Tmp directory
mkdir tmp/**
touch tmp/**
rm tmp/**
```

#### Misc Read-only
```bash
wc:*
diff:*
comm:*
sort:*
uniq:*
cut:*
awk:* (read-only patterns)
sed:* (read-only patterns)
```

---

### 🟡 ASK FIRST List

#### File Operations (Outside Project Directories)
```bash
rm:* (except auto-allowed paths)
mv:* (except auto-allowed paths)
cp:* (except auto-allowed paths)
ln:*
```

#### Directory Operations (Outside Project)
```bash
mkdir:* (except auto-allowed paths)
rmdir:*
```

#### Permissions
```bash
chmod:*
chown:*
chgrp:*
```

#### Process Control
```bash
kill:*
killall:*
pkill:*
```

#### Network Operations
```bash
curl:*
wget:*
nc:*
telnet:*
ssh:*
scp:*
rsync:*
```

#### Package Management
```bash
brew install:*
npm install:*
pip install:*
gem install:*
cargo install:*
```

#### System Configuration
```bash
sudo:*
```

#### Interactive Editors
```bash
vim:*
nano:*
emacs:*
vi:*
```

#### Compression (Extraction ask first)
```bash
tar -xf:*
unzip:*
gunzip:*
bunzip2:*
```

---

### 🔴 NEVER ALLOW List

#### Destructive File Operations
```bash
rm -rf /:*
rm -rf /*:*
dd:*
mkfs:*
format:*
shred:*
```

#### System Control
```bash
shutdown:*
reboot:*
halt:*
poweroff:*
init:*
systemctl stop:*
systemctl restart:*
```

#### User Management
```bash
useradd:*
userdel:*
usermod:*
passwd:*
groupadd:*
groupdel:*
```

#### Kernel/System Modules
```bash
modprobe:*
insmod:*
rmmod:*
```

#### Disk Management
```bash
fdisk:*
parted:*
mkfs.*:*
mount:*
umount:*
```

#### Network Config (System-wide)
```bash
ifconfig:*
ip addr:*
ip route:*
iptables:*
```

---

## 📊 IMPACT SUMMARY

### Token Reduction
- Filesystem tools: 6,400 tokens
- Git tools: 4,000 tokens
- GitHub tools: 20,800 tokens
- Repomix tools: 3,200 tokens
- Playwright tools: 4,800 tokens
- Perplexity tools: 800 tokens
- Syntropy system tools: 4,000 tokens

**Total Savings**: ~44,000 tokens

### Tools Summary
- **Before**: 87 MCP tools
- **After**: 32 MCP tools (11 Serena + 1 thinking + 2 context7 + 9 Linear + 2 Syntropy + 2 IDE + 4 MCP system)
- **Reduction**: 55 tools (63%)

### Command Permissions
- **Auto-allow**: ~35 command patterns (predictable, no interruptions)
- **Ask first**: ~20 command patterns (safety gate for destructive ops)
- **Never allow**: ~15 command patterns (absolute safety)

### Benefits
1. **Clarity**: No ambiguity on tool selection
2. **Efficiency**: Direct native tools, no MCP wrappers
3. **Token efficiency**: ~44k token reduction in context
4. **Predictability**: Locked command lists, no guessing
5. **Simplicity**: Fewer abstractions, clearer mental model

### User Impact

**Changes require**:
- MCP reconnect: Run `/mcp` after tool deny list update
- Command re-check: First use after permission update may prompt
- No session restart needed
- No data loss or workflow interruption

### Task Execution Strategy

**Parallel execution possible** for independent tasks:
- Tasks 1, 2, 4 can run in parallel (plugin fix, tool deny, create guide)
- Tasks 3, 5, 6, 7 must run sequentially (dependencies exist)

**Estimated time savings**: ~20-30 minutes vs sequential

**Current plan**: Sequential execution for simplicity and safety
**Optional**: Run Tasks 1, 2, 4 in parallel if time-critical

---

## 🎯 IMPLEMENTATION CHECKLIST

- [ ] **Task 1**: Fix plugin marketplace configuration
  - [ ] Read current settings to understand structure
    - [ ] `Read .claude/settings.local.json` OR `Read .claude/config.json`
    - [ ] Identify plugin configuration format
  - [ ] Locate plugin config in `.claude/settings.local.json` or `.claude/config.json`
  - [ ] Update to GitHub source or remove unused plugins
  - [ ] Test with `/mcp` reconnect

- [ ] **Task 2**: Update tool deny list
  - [ ] Add 55 tools to deny list in `.claude/settings.local.json`
  - [ ] Surgical edit (not wholesale replace)
  - [ ] Verify all 9 Linear tools remain accessible
    - [ ] `linear_create_issue`, `linear_get_issue`, `linear_list_issues`
    - [ ] `linear_update_issue`, `linear_list_projects`, `linear_list_teams`
    - [ ] `linear_list_users`, `linear_get_team`, `linear_create_project`
  - [ ] Verify Serena, thinking, context7 tools remain accessible

- [ ] **Task 3**: Remove GitButler integration
  - [ ] Remove GitButler section from CLAUDE.md
  - [ ] Remove GitButler hooks from settings
  - [ ] Update git workflow documentation
  - [ ] Archive GitButler documentation (optional cleanup)
    - [ ] Move `test-target/GITBUTLER-INTEGRATION-GUIDE.md` to `archive/`
    - [ ] Move `examples/GITBUTLER-REFERENCE.md` to `archive/`
    - [ ] Move/remove `examples/gitbutler-test-automation.py`
  - [ ] Remove GitButler CLI (optional, user preference)
    - [ ] Check if installed: `which but`
    - [ ] If desired: `rm $(which but)` OR uninstall via GitButler app

- [ ] **Task 4**: Create tool usage guide
  - [ ] Create `TOOL-USAGE-GUIDE.md` with all sections
  - [ ] Include decision tree, common tasks, anti-patterns
  - [ ] Include migration table from old to new tools
  - [ ] Add quick reference for all kept MCP tools

- [ ] **Task 5**: Update command permissions
  - [ ] Verify permission pattern syntax first
    - [ ] Read existing permissions to understand format
    - [ ] Test 2-3 patterns before full rollout
  - [ ] Add auto-allow patterns to settings
  - [ ] Add ask-first patterns to settings
  - [ ] Document never-allow patterns (reference only)
  - [ ] Test with common commands (git status, ls, etc.)

- [ ] **Task 6**: Update CLAUDE.md and related documentation
  - [ ] Verify slash command file locations first
    - [ ] `find .claude -name "*.md" -type f` OR `ls .claude/commands/`
    - [ ] Identify execute-prp and peer-review command files
  - [ ] Remove GitButler section entirely from CLAUDE.md
  - [ ] Add new "Parallel PRP Development with Git Worktrees" section to CLAUDE.md
    - [ ] Include setup, workflow, conflict resolution
    - [ ] Add comparison table (GitButler vs worktree)
    - [ ] Add quick reference commands
  - [ ] Update tool selection guide with link to TOOL-USAGE-GUIDE.md
  - [ ] Remove outdated Syntropy MCP tool recommendations
  - [ ] Add command permission reference
  - [ ] Update troubleshooting section
  - [ ] Update /execute-prp slash command documentation
    - [ ] Replace GitButler references with worktree workflow
    - [ ] Add conflict resolution procedures
  - [ ] Update /peer-review slash command documentation
    - [ ] Replace GitButler status checks with worktree list
    - [ ] Add worktree-specific review procedures
  - [ ] Update any other docs referencing GitButler
    - [ ] `Grep pattern="gitbutler" -i output_mode=files_with_matches`
    - [ ] `Grep pattern="but " output_mode=files_with_matches`
    - [ ] `Grep pattern="virtual branch" output_mode=files_with_matches`
    - [ ] Replace with worktree equivalents

- [ ] **Task 7**: Validation
  - [ ] Measure token reduction
    - [ ] Run `/doctor` before changes, note MCP tools context tokens
    - [ ] Expected: ~46k tokens for MCP tools
  - [ ] Test auto-allow commands (no prompts)
    - [ ] `git status`, `ls`, `cat README.md`, `grep TODO`
  - [ ] Test ask-first commands (prompts appear)
    - [ ] `rm /tmp/test.txt`, `curl https://example.com`
  - [ ] Test MCP tools (only allowed ones work)
    - [ ] Try allowed: `serena_find_symbol`, `linear_list_issues`
    - [ ] Try denied: Should fail gracefully or not appear
  - [ ] Verify TOOL-USAGE-GUIDE.md is comprehensive
    - [ ] All common tasks covered
    - [ ] Migration table complete
    - [ ] Examples clear and actionable
  - [ ] **Test git worktree workflow** (MUST WORK)
    - [ ] Create test worktree: `git worktree add ../ctx-eng-plus-test -b test-branch`
    - [ ] Make changes in worktree
    - [ ] Commit and push from worktree
    - [ ] Create intentional conflict with main
    - [ ] Resolve conflict using Read + Edit tools
    - [ ] Verify tests pass after resolution: `cd tools && uv run pytest tests/ -v`
    - [ ] Remove worktree: `git worktree remove ../ctx-eng-plus-test`
  - [ ] Verify all GitButler references removed from docs
    - [ ] No "gitbutler" mentions: `Grep pattern="gitbutler" -i`
    - [ ] No "but " commands: `Grep pattern="but " -C 1`
  - [ ] Run `/doctor` to verify clean state
    - [ ] Verify token reduction: Expected ~2k tokens for MCP tools (was ~46k)
    - [ ] No plugin errors
    - [ ] All servers connected

---

## 🔧 ROLLBACK PLAN

If issues arise:

1. **Plugin errors persist**: Restore original plugin config from git history
2. **Tool access issues**: Remove deny list entries incrementally
3. **Command permission blocks**: Move from ask-first to auto-allow as needed
4. **GitButler needed**: Restore hooks and documentation from git history

**Backup Command**:
```bash
git stash push -m "Pre-lockdown backup" -- .claude/
```

---

## 📝 NOTES

- This plan prioritizes **efficiency** and **predictability** over maximum features
- Linear tools kept due to heavy workflow integration
- Native tools preferred (Read, Write, Edit, Glob, Grep, Bash)
- Command lists are **locked** - no exceptions without explicit approval
- GitButler replacement: Git worktrees provide equivalent parallel PRP development
- Git worktree workflow MUST work - includes complete conflict resolution procedures
- Slash commands requiring updates:
  - `/execute-prp` - Replace GitButler workflow with worktrees
  - `/peer-review` - Replace GitButler status with worktree list
- All GitButler documentation replaced with worktree equivalents
- Search and replace: "gitbutler", "but ", "virtual branch" → worktree equivalents

---

**Status**: ✅ PEER REVIEWED & READY FOR EXECUTION

**Peer Review Applied**:
- ✅ Git worktree constraints documented (same branch limitation)
- ✅ Command permission syntax verification added
- ✅ Task 1: "Read settings first" substep added
- ✅ Task 2: Linear tool verification added
- ✅ Task 3: GitButler cleanup strategy added
- ✅ Task 5: Pattern syntax testing added
- ✅ Task 6: "Find slash command files" substep added
- ✅ Task 7: Validation metrics and comprehensive testing added
- ✅ Disk space warning added to worktree section
- ✅ Session impact note added
- ✅ Parallel task execution strategy documented
- ✅ Fallback tool clarification added (cat/grep/find)

**Next**: Execute tasks 1-7 (sequential recommended, parallel optional for 1,2,4)
