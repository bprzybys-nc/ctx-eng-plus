# Tool & Permission Lockdown Plan

**Date**: 2025-10-29
**Status**: PENDING APPROVAL

---

## 📋 EXECUTIVE SUMMARY

This plan addresses four critical areas:
1. Fix plugin marketplace configuration (5 failed plugins)
2. Create MCP tool deny list (55 tools to remove)
3. Evaluate GitButler extension necessity (verdict: remove)
4. Create definitive bash command lists (locked permissions)

**Impact**: ~45,000 token reduction, clearer permissions, more efficient tooling

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
- `syntropy_init_project` (rare use, one-time setup)
- `syntropy_get_system_doc` (use native Read for .ce/ files)
- `syntropy_get_user_doc` (use native Read for user docs)
- `syntropy_get_summary` (use bash commands or native tools)
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
- `syntropy_healthcheck`
- `syntropy_knowledge_search`

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

---

## 4. DEFINITIVE COMMAND LISTS (LOCKED)

### Philosophy
- **Auto-allow**: Safe, read-only, frequent operations
- **Ask first**: Potentially destructive or system-wide changes
- **Never allow**: Destructive, system-critical operations

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

#### Reading Tools (Prefer Read tool, but allow)
```bash
cat:*
head:*
tail:*
less:*
more:*
```

#### Search Tools (Prefer Grep/Glob, but allow)
```bash
grep:*
find:*
rg:*
```

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

---

## 🎯 IMPLEMENTATION CHECKLIST

- [ ] **Task 1**: Fix plugin marketplace configuration
  - [ ] Locate plugin config in `.claude/settings.local.json` or `.claude/config.json`
  - [ ] Update to GitHub source or remove unused plugins
  - [ ] Test with `/mcp` reconnect

- [ ] **Task 2**: Update tool deny list
  - [ ] Add 55 tools to deny list in `.claude/settings.local.json`
  - [ ] Surgical edit (not wholesale replace)
  - [ ] Verify Linear tools remain accessible

- [ ] **Task 3**: Remove GitButler integration
  - [ ] Remove GitButler section from CLAUDE.md
  - [ ] Remove GitButler hooks from settings
  - [ ] Update git workflow documentation

- [ ] **Task 4**: Update command permissions
  - [ ] Add auto-allow patterns to settings
  - [ ] Add ask-first patterns to settings
  - [ ] Document never-allow patterns (reference only)
  - [ ] Test with common commands

- [ ] **Task 5**: Update CLAUDE.md
  - [ ] Remove GitButler section
  - [ ] Update tool selection guide
  - [ ] Add command permission reference
  - [ ] Update troubleshooting section

- [ ] **Task 6**: Validation
  - [ ] Test auto-allow commands (no prompts)
  - [ ] Test ask-first commands (prompts appear)
  - [ ] Test MCP tools (only allowed ones work)
  - [ ] Run `/doctor` to verify clean state

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
- GitButler removal may require user workflow adjustment

---

**Status**: READY FOR APPROVAL
**Next**: Execute tasks 1-6 sequentially after approval
