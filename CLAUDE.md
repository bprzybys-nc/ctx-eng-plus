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

# Testing
uv run pytest tests/ -v

# Run Python (3 LOC max ad-hoc)
uv run ce run_py "print('hello')"
uv run ce run_py ../tmp/script.py
```

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

**Bash** (11): git, uv run, uv add, uvx, env, brew install, rm -rf ~/.mcp-auth

**Serena** (11): find_symbol, get_symbols_overview, search_for_pattern, find_referencing_symbols, write_memory, create_text_file, read_file, list_dir, insert_after/before_symbol, activate_project

**Filesystem** (8): read_text_file, write_file, edit_file, list_directory, search_files, directory_tree, get_file_info, list_allowed_directories

**Git** (5): git_status, git_diff, git_log, git_add, git_commit

**GitHub** (26): create_or_update_file, search_repositories, create_repository, get_file_contents, push_files, create_issue, create_pull_request, fork_repository, create_branch, list_commits, list_issues, update_issue, add_issue_comment, search_code, search_issues, search_users, get_issue, get_pull_request, list_pull_requests, create_pull_request_review, merge_pull_request, get_pull_request_files, get_pull_request_status, update_pull_request_branch, get_pull_request_comments, get_pull_request_reviews

**Context7** (2): resolve_library_id, get_library_docs

**Thinking** (1): sequentialthinking

**Linear** (5): create_issue, get_issue, list_issues, update_issue, list_projects

**Perplexity** (1): perplexity_ask

**Repomix** (1): pack_codebase

**Syntropy** (7): init_project, get_system_doc, get_user_doc, knowledge_search, get_summary, healthcheck, denoise

## Quick Tool Selection

**Analyze code**:
- Know symbol → `find_symbol`
- Explore file → `get_symbols_overview`
- Search patterns → `search_for_pattern`
- Find usages → `find_referencing_symbols`

**Modify files**:
- New → `write_file`
- Existing (surgical) → `edit_file`
- Config/text → `read_text_file`

**Version control**: `git_status`, `git_diff`, `git_add`, `git_commit`

**GitHub operations**:
- File ops → `create_or_update_file`, `get_file_contents`, `push_files`
- Issues → `create_issue`, `list_issues`, `get_issue`, `update_issue`
- PRs → `create_pull_request`, `list_pull_requests`, `merge_pull_request`
- Search → `search_code`, `search_repositories`, `search_issues`

**External knowledge**:
- Documentation → `resolve_library_id`, `get_library_docs`
- AI search → `perplexity_ask`

**Complex reasoning**: `sequentialthinking`

**Project management**: Linear tools

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

## Linear Integration

**Config**: `.ce/linear-defaults.yml`
- Project: "Context Engineering"
- Assignee: "blazej.przybyszewski@gmail.com"
- Team: "Blaise78"

**Auto-create issues**: `/generate-prp` uses defaults

**Join existing issue**: `/generate-prp --join-prp 12`

**Troubleshooting**: `rm -rf ~/.mcp-auth` (pre-approved)

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
- `.ce/examples/system/` - Implementation patterns
- `PRPs/[executed,feature-requests]` - Feature requests
- `examples/` - User code patterns

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

### Archived GitButler Documentation

Previous GitButler integration docs archived at:
- `archive/gitbutler/GITBUTLER-REFERENCE.md`
- `archive/gitbutler/GITBUTLER-INTEGRATION-GUIDE.md`
- `archive/gitbutler/gitbutler-test-automation.py`

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

## Permissions

**❌ NEVER** replace all permissions with one entry in `.claude/settings.local.json`

**✅ ALLOWED**: Surgical edits to individual permissions

## Special Notes

- Linear MCP context: "linear( mcp)" = linear-server mcp
- Compact conversation: Use claude-3-haiku-20240307
- Activate Serena: Use project's root full path
- Ad-hoc code strict: 3 LOC max, no exceptions
