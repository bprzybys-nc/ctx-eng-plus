# Context Engineering Tools - Project Guide

**Project**: CLI tooling for Context Engineering framework operations

## Communication

Direct, token-efficient. No fluff. Call out problems directly.

## Core Principles

### Syntropy MCP First
- Use `mcp__syntropy__<server>_<tool>` format
- Prefer Syntropy tools over bash/cmdline

### No Fishy Fallbacks
- Fast failure: Let exceptions bubble up
- Actionable errors: Include 🔧 troubleshooting
- No silent corruption

### KISS
- Simple solutions first
- Clear code over clever code
- Minimal dependencies (stdlib only)
- Single responsibility per function

### UV Package Management - STRICT
```bash
uv add package-name              # Production
uv add --dev package-name        # Development
uv sync                          # Install

# ❌ FORBIDDEN: Manual pyproject.toml editing
```

### Ad-Hoc Code Policy
- Max 3 LOC inline
- Longer code → tmp/ file and execute
- Must execute via run_py

## Quick Commands

```bash
cd tools

# Validation & health
uv run ce validate --level all
uv run ce context health
uv run ce git status

# Cleanup
uv run ce vacuum                  # Dry-run (report only)
uv run ce vacuum --execute        # Delete temp files only
uv run ce vacuum --auto           # Delete temp files + obsolete docs/dead links

# Testing
uv run pytest tests/ -v

# Run Python (3 LOC max ad-hoc)
uv run ce run_py "print('hello')"
uv run ce run_py ../tmp/script.py
```

## Framework Initialization

**First-time setup**: See [examples/INITIALIZATION.md](examples/INITIALIZATION.md) for complete CE 1.1 initialization guide.

**Key Steps** (5-phase workflow):
1. **Bucket Collection**: Extract existing Serena memories, examples, PRPs, CLAUDE.md, .claude directory
2. **User Files Migration**: Copy validated user files with `type: user` YAML headers
3. **Repomix Package Handling**: Extract ce-infrastructure.xml to /system/ subfolders
4. **Blending**: Merge framework + user files (CLAUDE.md sections, settings.local.json, commands)
5. **Cleanup**: Remove initialization artifacts, verify structure

**Repomix Usage** (manual context loading):

```bash
# Load workflow docs (commands, validation, PRP patterns)
# Reference package - stored in .ce/, not extracted during initialization
cat .ce/ce-workflow-docs.xml

# Load infrastructure docs (memories, rules, system architecture)
# Extracted to /system/ subfolders during Phase 3 of initialization
npx repomix --unpack .ce/ce-infrastructure.xml --target tmp/extraction/
```

**Repomix Package Structure** (CE 1.1):
- **ce-workflow-docs.xml**: <60KB (reference package, not extracted)
- **ce-infrastructure.xml**: <150KB (all framework files with /system/ organization)
- **Combined**: <210KB total

**Migration Scenarios**:

All scenarios documented in [INITIALIZATION.md](examples/INITIALIZATION.md) with scenario-specific variations within each phase:
- **Greenfield**: New project setup (10 min)
- **Mature Project**: Add CE to existing codebase (45 min)
- **CE 1.0 Upgrade**: Upgrade CE 1.0 → CE 1.1 (40 min)
- **Partial Install**: Complete partial CE installation (15 min)

**Memory Type System** (CE 1.1):

Framework memories (23 files) use `type: regular` by default:
```yaml
---
type: regular
category: documentation
tags: [tag1, tag2, tag3]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---
```

**Critical Memory Candidates** (upgrade during initialization):
- code-style-conventions.md
- suggested-commands.md
- task-completion-checklist.md
- testing-standards.md
- tool-usage-syntropy.md
- use-syntropy-tools-not-bash.md

**User File Headers** (added during Phase 2 of initialization):

User memories:
```yaml
---
type: user
source: target-project
created: "2025-11-04T00:00:00Z"
updated: "2025-11-04T00:00:00Z"
---
```

User PRPs:
```yaml
---
prp_id: USER-001
title: User Feature Implementation
status: completed
created: "2025-11-04"
source: target-project
type: user
---
```

**See Also**:
- [examples/INITIALIZATION.md](examples/INITIALIZATION.md) - Complete initialization guide
- [.serena/memories/README.md](.serena/memories/README.md) - Memory type system documentation
- [examples/templates/PRP-0-CONTEXT-ENGINEERING.md](examples/templates/PRP-0-CONTEXT-ENGINEERING.md) - Document framework installation

## Working Directory

**Default**: `/Users/bprzybysz/nc-src/ctx-eng-plus`

**For tools/ commands**: Use `cd tools &&` or `uv run -C tools`

## Hooks

**Pre-Commit**: Runs `ce validate --level 4` before commit (skip: `--no-verify`)

**Session Start**: Auto drift score check

**Shell Functions** (optional): Source `.ce/shell-functions.sh` for `cet` alias

## Tool Naming Convention

Format: `mcp__syntropy__<server>_<tool>`
- `mcp__` - MCP prefix (double underscore)
- `syntropy__` - Syntropy server (double underscore)
- `<server>_` - Server name + single underscore
- `<tool>` - Tool name

Example: `mcp__syntropy__serena_find_symbol`

## Allowed Tools Summary

**Post-Lockdown State** (after PRP-A & PRP-D):
- **Before**: 87 MCP tools (via Syntropy aggregator)
- **After**: 32 MCP tools (55 denied for native tool preference)
- **Token reduction**: ~44k tokens (96% reduction from 46k→2k)

### Kept Tools by Category

**Serena** (11 tools): Code symbol navigation
- find_symbol, get_symbols_overview, search_for_pattern
- find_referencing_symbols, write_memory, read_memory, list_memories
- create_text_file, read_file, list_dir, delete_memory

**Linear** (9 tools): Project management integration
- create_issue, get_issue, list_issues, update_issue
- list_projects, list_teams, list_users, get_team, create_project

**Context7** (2 tools): Library documentation
- resolve_library_id, get_library_docs

**Thinking** (1 tool): Complex reasoning
- sequentialthinking

**Syntropy System** (2 tools): System utilities
- healthcheck (MCP diagnostics)
- knowledge_search (semantic search across PRPs, memories)

**Bash Commands** (~50 patterns): See "Command Permissions" section below
**Native Tools**: Read, Write, Edit, Glob, Grep, WebSearch, WebFetch

### Denied Tools (55 total)

**Rationale**: Native Claude Code tools provide equivalent or better functionality

**Categories**:
- Filesystem (8): Use Read, Write, Edit, Glob instead
- Git (5): Use Bash(git:*) instead
- GitHub (26): Use Bash(gh:*) instead
- Repomix (4): Use incremental Glob/Grep/Read instead
- Playwright (6): Use WebFetch or Bash(playwright CLI) instead
- Perplexity (1): Use WebSearch instead
- Syntropy (5): Use Read for docs, rare-use tools

**Full details**: See [TOOL-USAGE-GUIDE.md](TOOL-USAGE-GUIDE.md)

## Command Permissions

**Permission Model**: Auto-allow safe commands, ask-first for potentially destructive operations.

### Auto-Allow Patterns (~35 bash patterns)

Commands that never prompt:

**File Inspection**:
- `ls`, `cat`, `head`, `tail`, `less`, `more`, `file`, `stat`

**Navigation**:
- `cd`, `pwd`, `which`, `whereis`

**Search**:
- `find`, `grep`, `rg`, `tree`

**Text Processing**:
- `sed`, `awk`, `sort`, `uniq`, `cut`, `diff`, `comm`, `wc`

**Environment**:
- `env`, `ps`, `echo`

**Development**:
- `git` (all operations), `gh` (GitHub CLI)
- `uv`, `uvx`, `pytest`
- `python`, `python3`

**Special Cases**:
- `rm -rf ~/.mcp-auth` (MCP troubleshooting)

**Full list**: See `.claude/settings.local.json` "allow" array

### Ask-First Patterns (15 patterns)

Commands that require confirmation:

**File Operations** (potentially destructive):
- `rm`, `mv`, `cp`

**Network Operations**:
- `curl`, `wget`, `nc`, `telnet`, `ssh`, `scp`, `rsync`

**Package Management**:
- `brew install`, `npm install`, `pip install`, `gem install`

**System Operations**:
- `sudo` (any sudo command)

**Rationale**: Safety gate for operations that modify files, access network, or require elevated privileges.

**Full list**: See `.claude/settings.local.json` "ask" array

### Permission Behavior

**Unlisted commands**: Prompt by default (ask before execution)
**Workaround**: Add to allow list in `.claude/settings.local.json` if frequently used

## Quick Tool Selection

**🔗 Comprehensive Guide**: See [examples/TOOL-USAGE-GUIDE.md](examples/TOOL-USAGE-GUIDE.md) for:
- Decision tree (flowchart for tool selection)
- Common tasks with right/wrong examples
- Anti-patterns to avoid
- Migration table (55 denied tools → alternatives)

**Quick Reference**:

**Analyze code**:
- Know symbol → `serena_find_symbol`
- Explore file → `serena_get_symbols_overview`
- Search patterns → `Grep` (native, not serena_search_for_pattern)
- Find usages → `serena_find_referencing_symbols`

**Modify files**:
- New → `Write` (native)
- Existing (surgical) → `Edit` (native)
- Config/text → `Read` (native)

**Version control**:
- Use `Bash(git:*)` (native git commands)
- NOT `mcp__syntropy__git_git_status` (denied)

**GitHub operations**:
- Use `Bash(gh:*)` (native gh CLI)
- NOT `mcp__syntropy__github_*` (denied)

**External knowledge**:
- Documentation → `context7_get_library_docs`
- Web search → `WebSearch` (native)
- Web content → `WebFetch` (native)

**Complex reasoning**: `sequentialthinking`

**Project management**: Linear tools (all 9 kept)

**System health**: `healthcheck` (detailed diagnostics with `detailed=true`)

## Project Structure

```
tools/
├── ce/                 # Source code
│   ├── core.py         # File, git, shell ops
│   ├── validate.py     # 3-level validation
│   └── context.py      # Context management
├── tests/              # Test suite
├── pyproject.toml      # UV config (don't edit!)
└── bootstrap.sh        # Setup script
```

## Testing Standards

**TDD**: Test first → fail → implement → refactor

**Real functionality**: No fake results, no mocks in tests

**Test before critical changes** (tool naming, API changes, refactoring)

## Code Quality

- Functions: 50 lines (single responsibility)
- Files: 300-500 lines (logical modules)
- Classes: 100 lines (single concept)
- Mark mocks with FIXME in production code

## Context Commands

```bash
# Sync all PRPs with codebase
cd tools && uv run ce update-context

# Sync specific PRP
cd tools && uv run ce update-context --prp PRPs/executed/PRP-6.md

# Fast drift check (2-3s vs 10-15s)
cd tools && uv run ce analyze-context

# Force re-analysis
cd tools && uv run ce analyze-context --force
```

**Drift Exit Codes**:
- 0: <5% (healthy)
- 1: 5-15% (warning)
- 2: ≥15% (critical)

## Syntropy MCP Tool Sync

**Dynamic tool management** - Enable/disable tools at runtime without restart

```bash
# Sync settings with Syntropy MCP tool state
/sync-with-syntropy

# Workflow example:
# 1. Enable/disable tools via Syntropy
mcp__syntropy__enable_tools(
  enable=["serena_find_symbol", "context7_get_library_docs"],
  disable=["filesystem_read_file", "git_git_status"]
)

# 2. Sync settings to .claude/settings.local.json
/sync-with-syntropy

# 3. Verify changes
cat .claude/settings.local.json
```

**How it works**:
1. Call `mcp__syntropy__list_all_tools` to get current tool states
2. Update `.claude/settings.local.json` to match
3. Backup original settings to `.claude/settings.local.json.backup`
4. Output clear summary of changes made

**Benefits**:
- Real-time tool control (no MCP restart needed)
- Persistent state across sessions (`~/.syntropy/tool-state.json`)
- Context-aware tool sets (enable 10 tools for quick tasks, all 87 for deep analysis)

## Linear Integration

**Config**: `.ce/linear-defaults.yml`
- Project: "Context Engineering"
- Assignee: "blazej.przybyszewski@gmail.com"
- Team: "Blaise78"

**Auto-create issues**: `/generate-prp` uses defaults

**Join existing issue**: `/generate-prp --join-prp 12`

**Troubleshooting**: `rm -rf ~/.mcp-auth` (pre-approved)

## Batch PRP Generation

**Decompose large plans into staged, parallelizable PRPs with automatic dependency analysis**

```bash
# Create plan document
vim FEATURE-PLAN.md

# Generate all PRPs with parallel subagents
/batch-gen-prp FEATURE-PLAN.md

# Output: Multiple PRPs with format PRP-X.Y.Z
#   X = Batch ID (next free number)
#   Y = Stage number
#   Z = Order within stage
```

**Plan Format**:
```markdown
# Plan Title

## Phases

### Phase 1: Name

**Goal**: One-sentence objective
**Estimated Hours**: 0.5
**Complexity**: low
**Files Modified**: path/to/file
**Dependencies**: None
**Implementation Steps**: [steps]
**Validation Gates**: [gates]
```

**What It Does**:
1. Parses plan document → Extracts phases
2. Builds dependency graph → Analyzes deps + file conflicts
3. Assigns stages → Groups independent PRPs for parallel execution
4. Spawns Sonnet subagents → Parallel generation per stage
5. Monitors via heartbeat files → 30s polling, kills after 2 failed polls
6. Creates Linear issues → One per PRP
7. Outputs summary → All generated PRPs grouped by stage

**Example Output**:
```
Batch 43:
  Stage 1: PRP-43.1.1
  Stage 2: PRP-43.2.1, PRP-43.2.2, PRP-43.2.3 (parallel)
  Stage 3: PRP-43.3.1
```

**Integration with Execution**:
```bash
# Generate PRPs from plan
/batch-gen-prp BIG-FEATURE-PLAN.md

# Execute entire batch
/batch-exe-prp --batch 43

# Or stage-by-stage
/batch-exe-prp --batch 43 --stage 1
/batch-exe-prp --batch 43 --stage 2
```

**Time Savings**: 8 PRPs sequential (30 min) → parallel (10-12 min) = **60% faster**

**See**: `.claude/commands/batch-gen-prp.md` for complete documentation

## PRP Sizing

```bash
cd tools && uv run ce prp analyze <path-to-prp.md>
```

**Size Categories**:
- GREEN: ≤700 lines, ≤8h, LOW-MEDIUM risk
- YELLOW: 700-1000 lines, 8-12h, MEDIUM risk
- RED: >1000 lines, >12h, HIGH risk

**Exit Codes**: 0 (GREEN), 1 (YELLOW), 2 (RED)

## Testing Patterns

**Strategy pattern** for composable testing:
- **Unit**: Test single strategy in isolation
- **Integration**: Test subgraph with real + mock
- **E2E**: Full pipeline, all external deps mocked

**Mock Strategies**: MockSerenaStrategy, MockContext7Strategy, MockLLMStrategy

**Real Strategies**: RealParserStrategy, RealCommandStrategy

## Documentation Standards

**Mermaid Diagrams**: Always specify text color
- Light backgrounds → `color:#000`
- Dark backgrounds → `color:#fff`
- Format: `style X fill:#bgcolor,color:#textcolor`

## Efficient Doc Review

**Grep-first validation** (90% token reduction):
1. Structural validation (Grep patterns, 1-2k tokens)
2. Code quality checks (Grep anti-patterns, 500 tokens)
3. Targeted reads (2-3 files only, 3-5k tokens)

**Total**: ~5-7k tokens vs 200k+ for read-all

## Resources

- `.ce/` - System boilerplate (don't modify)
- `.ce/RULES.md` - Framework rules
- `PRPs/[executed,feature-requests]` - Feature requests
- `examples/` - Framework patterns and user code

## Keyboard Shortcuts

### Image Pasting (macOS)

**cmd+v**: Paste screenshot images into Claude Code
- Requires Karabiner-Elements (configured via PRP-30)
- Remaps cmd+v → ctrl+v in terminals only
- Config: `~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json`
- Toggle: Karabiner-Elements → Complex Modifications

**Setup** (one-time):
```bash
brew install --cask karabiner-elements
# Enable rule in Karabiner-Elements UI → Complex Modifications
```

## Git Worktree - Parallel PRP Development

**Native git solution for working on multiple PRPs simultaneously**

### Quick Start

```bash
# Create worktree for PRP-A (creates ../ctx-eng-plus-prp-a)
git worktree add ../ctx-eng-plus-prp-a -b prp-a-feature

# Work in worktree
cd ../ctx-eng-plus-prp-a
# Make changes...
git add .
git commit -m "Implement feature"

# List all worktrees
git worktree list

# Remove worktree after merging
git worktree remove ../ctx-eng-plus-prp-a
```

### Commands

**Create**:
```bash
git worktree add <path> -b <branch-name>
# Example: git worktree add ../ctx-eng-plus-prp-12 -b prp-12-validation
```

**List**:
```bash
git worktree list
# Shows: path, commit hash, branch name
```

**Remove**:
```bash
git worktree remove <path>
# or: git worktree remove --force <path>  # if uncommitted changes
```

**Prune** (clean stale references):
```bash
git worktree prune
```

### Workflow for Parallel PRPs

**Stage 1: Create Worktrees**
```bash
# From main repo: /Users/bprzybysz/nc-src/ctx-eng-plus
git worktree add ../ctx-eng-plus-prp-a -b prp-a-tool-deny
git worktree add ../ctx-eng-plus-prp-b -b prp-b-usage-guide
git worktree add ../ctx-eng-plus-prp-c -b prp-c-worktree-docs
```

**Stage 2: Execute in Parallel**
```bash
# Terminal 1
cd ../ctx-eng-plus-prp-a
# Edit .claude/settings.local.json
git add .
git commit -m "PRP-A: Add tools to deny list"

# Terminal 2
cd ../ctx-eng-plus-prp-b
# Create TOOL-USAGE-GUIDE.md
git add .
git commit -m "PRP-B: Create tool usage guide"

# Terminal 3
cd ../ctx-eng-plus-prp-c
# Update CLAUDE.md
git add .
git commit -m "PRP-C: Migrate to worktree docs"
```

**Stage 3: Merge in Order**
```bash
cd /Users/bprzybysz/nc-src/ctx-eng-plus
git checkout main

# Merge PRP-A first
git merge prp-a-tool-deny --no-ff
git push origin main

# Merge PRP-B
git merge prp-b-usage-guide --no-ff
git push origin main

# Merge PRP-C (may conflict with PRP-A on settings.local.json)
git merge prp-c-worktree-docs --no-ff
# If conflicts, resolve manually (see Conflict Resolution below)
git push origin main
```

**Stage 4: Cleanup**
```bash
git worktree remove ../ctx-eng-plus-prp-a
git worktree remove ../ctx-eng-plus-prp-b
git worktree remove ../ctx-eng-plus-prp-c
git worktree prune
```

### Critical Constraints

**⚠️ Same Branch Limitation**

**CANNOT** check out the same branch in multiple worktrees simultaneously.

**Example of ERROR**:
```bash
# Main repo on `main` branch
cd /Users/bprzybysz/nc-src/ctx-eng-plus
git branch
# * main

# Try to create worktree on `main`
git worktree add ../ctx-eng-plus-test -b main
# ERROR: fatal: 'main' is already checked out at '/Users/bprzybysz/nc-src/ctx-eng-plus'
```

**Solution**: Each worktree must use a **unique branch**.

```bash
# Main repo stays on gitbutler/workspace or main
# Each PRP worktree uses dedicated branch
git worktree add ../ctx-eng-plus-prp-a -b prp-a-unique  # ✓
git worktree add ../ctx-eng-plus-prp-b -b prp-b-unique  # ✓
```

### Conflict Resolution

When merging parallel PRPs, conflicts may occur if they modify the same file sections.

**Scenario 1: No Conflicts** (PRP-A + PRP-B)
```bash
git merge prp-a-tool-deny --no-ff  # ✓ Success
git merge prp-b-usage-guide --no-ff  # ✓ Success (different files)
```

**Scenario 2: Merge Conflict** (PRP-A + PRP-D both edit settings.local.json)

**Step 1: Attempt Merge**
```bash
git merge prp-d-command-perms --no-ff
# Auto-merging .claude/settings.local.json
# CONFLICT (content): Merge conflict in .claude/settings.local.json
# Automatic merge failed; fix conflicts and then commit the result.
```

**Step 2: Check Conflict Markers**
```bash
git status
# Unmerged paths:
#   both modified:   .claude/settings.local.json
```

**Step 3: Read File to See Conflicts**
```python
Read(file_path="/Users/bprzybysz/nc-src/ctx-eng-plus/.claude/settings.local.json")
# Look for:
# <<<<<<< HEAD
# ... current branch content ...
# =======
# ... incoming branch content ...
# >>>>>>> prp-d-command-perms
```

**Step 4: Resolve with Edit Tool**
```python
# Remove conflict markers, keep desired changes from both branches
Edit(
  file_path="/Users/bprzybysz/nc-src/ctx-eng-plus/.claude/settings.local.json",
  old_string="""<<<<<<< HEAD
  "deny": [existing tools...]
=======
  "deny": [incoming tools...]
>>>>>>> prp-d-command-perms""",
  new_string="""  "deny": [merged tools from both branches...]"""
)
```

**Step 5: Stage and Commit**
```bash
git add .claude/settings.local.json
git commit -m "Merge prp-d-command-perms: Resolve settings conflict"
```

**Scenario 3: Conflicting Logic** (PRP-A denies tool, PRP-D allows same tool)

**Resolution**: Apply **last-merged wins** or **manual decision**.

```json
// PRP-A (merged first): Denies "mcp__syntropy__git_git_status"
"deny": ["mcp__syntropy__git_git_status"]

// PRP-D (merging now): Allows "git" commands implicitly
"allow": ["Bash(git:*)"]

// Decision: Keep Bash(git:*) in allow, keep git_git_status in deny
// Rationale: Native bash git preferred over MCP wrapper
```

### Comparison: GitButler vs Worktree

| Feature | GitButler | Git Worktree |
|---------|-----------|--------------|
| **Parallel Development** | ✓ Virtual branches | ✓ Physical worktrees |
| **Branch Switching** | ✗ Not needed | ✗ Not needed |
| **Conflict Detection** | ✓ Real-time 🔒 icon | ⚠️ At merge time |
| **Native Git** | ✗ Proprietary layer | ✓ Built-in since Git 2.5 |
| **Learning Curve** | Medium (new concepts) | Low (standard git) |
| **Merge Strategy** | UI-based | CLI-based (standard) |
| **Same Branch Limit** | ✓ Can work on same "virtual" branch | ✗ Must use unique branches |
| **Tool Requirement** | Requires GitButler app + CLI | ✓ Native git (no install) |
| **Workspace Branch** | Auto-merges to `gitbutler/workspace` | Manual merge to `main` |

### Benefits of Worktree Approach

1. **Native Git**: No external dependencies, works everywhere
2. **Explicit Branches**: Clear separation, standard git workflow
3. **Merge Control**: Full control over merge order and conflict resolution
4. **Universal**: Works on any git version ≥2.5 (2015)
5. **Simple Cleanup**: `git worktree remove` + `git worktree prune`

### Example: 3-PRP Parallel Execution

```bash
# Stage 1: Create worktrees (30 seconds)
git worktree add ../ctx-eng-plus-prp-a -b prp-a-tool-deny
git worktree add ../ctx-eng-plus-prp-b -b prp-b-usage-guide
git worktree add ../ctx-eng-plus-prp-c -b prp-c-worktree-docs

# Stage 2: Execute in parallel (15 minutes total, vs 45 sequential)
# Each PRP executes independently in its worktree

# Stage 3: Merge in dependency order (5 minutes)
git merge prp-a-tool-deny --no-ff     # Merge order: 1
git merge prp-b-usage-guide --no-ff   # Merge order: 2
git merge prp-c-worktree-docs --no-ff # Merge order: 3

# Stage 4: Cleanup (30 seconds)
git worktree remove ../ctx-eng-plus-prp-a
git worktree remove ../ctx-eng-plus-prp-b
git worktree remove ../ctx-eng-plus-prp-c
git worktree prune
```

**Time Savings**: 45 min sequential → 20 min parallel (55% reduction)

---

## Troubleshooting

```bash
# Tool not found
cd tools && uv pip install -e .

# Tests failing
uv sync
uv run pytest tests/ -v

# Linear "Not connected"
rm -rf ~/.mcp-auth

# Check PRP's Linear issue ID
grep "^issue:" PRPs/executed/PRP-12-feature.md
```

**New Issues** (added after lockdown):

### Issue: "Permission prompt for safe command"

**Symptom**: Commands like `ls` or `cat` prompt for permission

**Cause**: Command not in auto-allow list

**Solution**:
1. Check if command matches pattern: `grep 'Bash(ls' .claude/settings.local.json`
2. If missing, add pattern to allow list
3. Or approve once (permission remembered for session)

### Issue: "Command denied" or "tool not found"

**Symptom**: MCP tool like `mcp__syntropy__filesystem_read_file` fails

**Cause**: Tool in deny list (post-lockdown)

**Solution**:
1. Check TOOL-USAGE-GUIDE.md for alternative
2. Example: `filesystem_read_file` → Use `Read` (native) instead
3. If tool should be allowed, remove from deny list (rare)

### Issue: "MCP tools context too large"

**Symptom**: Token usage warning for MCP tools

**Cause**: Deny list not applied (MCP not reconnected)

**Solution**:
```bash
# Reconnect MCP servers
/mcp

# Verify token reduction
# Expected: ~2k tokens for MCP tools (was ~46k)
```

## Permissions

**❌ NEVER** replace all permissions with one entry in `.claude/settings.local.json`

**✅ ALLOWED**: Surgical edits to individual permissions

## Special Notes

- Linear MCP context: "linear( mcp)" = linear-server mcp
- Compact conversation: Use claude-3-haiku-20240307
- Activate Serena: Use project's root full path
- Ad-hoc code strict: 3 LOC max, no exceptions
