---
prp_id: PRP-B
feature_name: Tool Usage Guide Creation
status: executed
created: 2025-10-29T00:00:00Z
updated: 2025-10-30T00:00:00Z
executed: 2025-10-29T00:00:00Z
execution_commit: 9af5bcc
complexity: low
estimated_hours: 0.33-0.42
dependencies: none
stage: stage-1-parallel
worktree_path: ../ctx-eng-plus-prp-b
branch_name: prp-b-tool-usage-guide
execution_order: 2
merge_order: 2
files_modified: examples/TOOL-USAGE-GUIDE.md (new file, symlinked to .serena/memories/)
conflict_potential: NONE (new file, no conflicts with A, C, D, E)
---

# Tool Usage Guide Creation

## 1. TL;DR

**Objective**: Create authoritative `TOOL-USAGE-GUIDE.md` as definitive tool selection reference

**What**: 6-section guide (philosophy, decision tree, common tasks, anti-patterns, quick reference, migration table) covering all native and MCP tools

**Why**: Replace scattered/outdated tool recommendations, provide clear native-first guidance, document all 55 denied tools' alternatives

**Effort**: 20-25 minutes

**Dependencies**: None (stage-1-parallel, independent execution)

---

## 2. Context

### Background
- CLAUDE.md has mixed/outdated tool recommendations
- No clear decision tree for native vs MCP tool selection
- 55 MCP tools being denied (PRP-A) need alternatives documented
- Users and Claude Code need authoritative reference

### Parallel Execution Context
- **Stage**: stage-1-parallel (can run with PRP-A, PRP-C)
- **Worktree**: `../ctx-eng-plus-prp-b`
- **Branch**: `prp-b-tool-usage-guide`
- **Files**: `TOOL-USAGE-GUIDE.md` (new file)
- **Conflicts**: NONE (new file, doesn't conflict with any other PRP)

### Constraints and Considerations
- Must cover all 32 kept MCP tools
- Must provide alternatives for all 55 denied tools
- Must include concrete, copy-paste examples
- Native-first philosophy throughout
- Clear, concise, actionable content

### Documentation References
- Source: TOOL-PERMISSION-LOCKDOWN-PLAN.md Section 4
- PRP-A deny list for tools to migrate from
- Native tools: Read, Write, Edit, Glob, Grep, Bash, Task
- Kept MCP tools: Serena (11), Linear (9), Context7 (2), thinking (1), Syntropy (2)

---

## 3. Implementation Steps

### Phase 1: File Creation (5 min)

**Step 1**: Create file at project root
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
# File will be created as TOOL-USAGE-GUIDE.md
```

**Step 2**: Write YAML-style header (optional, for consistency)
```markdown
# Tool Usage Guide

**Version**: 1.0
**Date**: 2025-10-29
**Status**: Active
```

**Step 3**: Create section skeleton
- Section 1: Philosophy
- Section 2: Decision Tree
- Section 3: Common Tasks
- Section 4: Anti-Patterns
- Section 5: Tool Quick Reference
- Section 6: Migration Table

### Phase 2: Content Writing (12 min)

**Step 4**: Write Section 1 - Philosophy (~100 words)
```markdown
## 1. Philosophy

**Native tools first**: Always prefer Claude Code's native tools (Read, Write, Edit, Glob, Grep, Bash, Task) over MCP wrappers. Native tools are:
- More direct (no MCP overhead)
- Faster (optimized for Claude Code)
- Better documented (official Claude Code docs)
- More flexible (full feature access)

**MCP tools only when unique value**: Use MCP tools only when they provide capabilities native tools cannot:
- Code symbol analysis (Serena)
- Linear issue management (Linear)
- Library documentation (Context7)
- Complex reasoning (Sequential thinking)
- MCP system diagnostics (Syntropy healthcheck/knowledge_search)

**Efficiency over features**: Prefer simple, direct tools over feature-rich but complex alternatives.

**Predictability over flexibility**: Choose tools with clear, consistent behavior.
```

**Step 5**: Write Section 2 - Decision Tree (~150 words)
```markdown
## 2. Decision Tree

When performing a task, follow this decision tree:

```
Need to... → Use this tool
├─ Read file → Read (native)
├─ Write new file → Write (native)
├─ Edit existing file → Edit (native)
├─ Find files by pattern → Glob (native)
├─ Search file contents → Grep (native)
├─ Run command (git, gh, uv, pytest) → Bash (native)
├─ Complex multi-step operation → Task (native agent)
├─ Analyze code symbols → Serena MCP
│   ├─ Find function/class → serena_find_symbol
│   ├─ File structure → serena_get_symbols_overview
│   └─ Find references → serena_find_referencing_symbols
├─ Manage Linear issues → Linear MCP
│   ├─ Create issue → linear_create_issue
│   ├─ List issues → linear_list_issues
│   └─ Update issue → linear_update_issue
├─ Get library docs → Context7 MCP
│   ├─ Resolve library → context7_resolve_library_id
│   └─ Fetch docs → context7_get_library_docs
├─ Complex reasoning → thinking MCP (sequentialthinking)
└─ Debug MCP servers → syntropy MCP (healthcheck)
```
```

**Step 6**: Write Section 3 - Common Tasks Table (~200 words)
```markdown
## 3. Common Tasks

| Task | Tool | Example |
|------|------|---------|
| Read configuration | Read | `Read pyproject.toml` |
| Read multiple files | Read | Call Read multiple times in parallel |
| Update version number | Edit | `Edit pyproject.toml old="version = \"1.0.0\"" new="version = \"1.1.0\""` |
| Create new file | Write | `Write path/to/file.py content="..."` |
| Find all Python tests | Glob | `Glob pattern="tests/**/*.py"` |
| Find TODO comments | Grep | `Grep pattern="TODO" output_mode="content"` |
| Search in specific files | Grep | `Grep pattern="def authenticate" type="py"` |
| Git status | Bash | `git status` |
| Git commit | Bash | `git add . && git commit -m "message"` |
| Create GitHub PR | Bash | `gh pr create --title "..." --body "..."` |
| List GitHub issues | Bash | `gh issue list --state open` |
| Install package | Bash | `uv add package-name` |
| Run tests | Bash | `cd tools && uv run pytest tests/ -v` |
| Find function definition | Serena | `serena_find_symbol name_path="MyClass.my_method"` |
| Get file symbols | Serena | `serena_get_symbols_overview relative_path="src/main.py"` |
| Create Linear issue | Linear | `linear_create_issue title="Bug" team_id="..."` |
| Get React docs | Context7 | `context7_get_library_docs context7CompatibleLibraryID="/vercel/next.js"` |
| Complex reasoning | Thinking | `sequentialthinking thought="..." thoughtNumber=1` |
| Check MCP health | Syntropy | `syntropy_healthcheck detailed=true` |
```

**Step 7**: Write Section 4 - Anti-Patterns (~150 words)
```markdown
## 4. Anti-Patterns

### ❌ DON'T

**File Operations**:
- ❌ `filesystem_read_file` → ✅ Use `Read` instead (more direct)
- ❌ `filesystem_write_file` → ✅ Use `Write` instead (simpler)
- ❌ `filesystem_edit_file` → ✅ Use `Edit` instead (more precise)
- ❌ `filesystem_search_files` → ✅ Use `Glob` instead (optimized)
- ❌ Bash `cat file.txt` → ✅ Use `Read` tool (preferred for file reading)

**Git Operations**:
- ❌ `git_git_status` → ✅ Use `Bash git status` (more flexible)
- ❌ `git_git_diff` → ✅ Use `Bash git diff` (supports all flags)
- ❌ `git_git_commit` → ✅ Use `Bash git commit` (full options)

**GitHub Operations**:
- ❌ `github_create_pull_request` → ✅ Use `Bash gh pr create` (official CLI)
- ❌ `github_list_issues` → ✅ Use `Bash gh issue list` (more features)
- ❌ `github_merge_pull_request` → ✅ Use `Bash gh pr merge` (comprehensive)

**Codebase Exploration**:
- ❌ `repomix_pack_codebase` → ✅ Use `Glob + Grep + Read` (incremental)
- ❌ Packing entire repo → ✅ Use targeted searches (more efficient)

**Web/Search**:
- ❌ `perplexity_ask` → ✅ Use `WebSearch` (native)
- ❌ `playwright_navigate` → ✅ Use `WebFetch` for content (simpler)

**Communication**:
- ❌ Bash `echo "message"` → ✅ Output text directly (don't use echo for user communication)

### ✅ DO

- ✅ Use `Read` for all file reading
- ✅ Use `Edit` for surgical file changes (old_string/new_string)
- ✅ Use `Glob` for file pattern matching
- ✅ Use `Grep` for content search
- ✅ Use `Bash` for git, gh, uv, pytest commands
- ✅ Use `Serena` for code symbol analysis
- ✅ Use `Linear` for issue management
- ✅ Use `Context7` for library documentation
- ✅ Output text directly to communicate with users
```

**Step 8**: Write Section 5 - Tool Quick Reference (~200 words)
```markdown
## 5. Tool Quick Reference

### Native Tools (Always Use These First)

**File Operations**:
- **Read** - Read files (replaces cat, filesystem_read_file)
  - Example: `Read /path/to/file.txt`
  - Use for: Configuration files, source code, documentation

- **Write** - Create new files (replaces echo >, filesystem_write_file)
  - Example: `Write /path/to/file.txt content="..."`
  - Use for: New files, generated code, documentation

- **Edit** - Modify existing files (replaces sed, filesystem_edit_file)
  - Example: `Edit /path/to/file.txt old_string="..." new_string="..."`
  - Use for: Surgical changes, version updates, refactoring

**Search & Discovery**:
- **Glob** - Find files by pattern (replaces find, filesystem_search_files)
  - Example: `Glob pattern="**/*.py"`
  - Use for: Finding files by extension, pattern matching

- **Grep** - Search file contents (replaces grep, search_for_pattern)
  - Example: `Grep pattern="TODO" output_mode="content"`
  - Use for: Finding code, searching logs, pattern matching

**Command Execution**:
- **Bash** - Run commands (git, gh, uv, pytest, etc.)
  - Example: `Bash command="git status"`
  - Use for: Git operations, GitHub CLI, package management, testing

**Advanced**:
- **Task** - Complex multi-step operations with specialized agents
  - Use for: Codebase exploration, complex research tasks

### MCP Tools (Use Only These)

**Serena (11 tools)** - Code Symbol Analysis
- `serena_find_symbol` - Find function/class definitions
  - Example: `serena_find_symbol name_path="MyClass.my_method"`
- `serena_get_symbols_overview` - File structure overview
  - Example: `serena_get_symbols_overview relative_path="src/main.py"`
- `serena_search_for_pattern` - Regex search in code
- `serena_find_referencing_symbols` - Find references to symbol
- `serena_write_memory`, `serena_read_memory`, `serena_list_memories` - Store project context
- `serena_create_text_file`, `serena_read_file`, `serena_list_dir` - File operations (prefer native tools)
- `serena_activate_project` - Activate Serena for project

**Linear (9 tools)** - Issue Management
- `linear_create_issue` - Create new issue
  - Example: `linear_create_issue title="Bug" team_id="..." description="..."`
- `linear_get_issue` - Get issue details
- `linear_list_issues` - List issues (filter by status, team)
- `linear_update_issue` - Update issue
- `linear_list_projects` - List projects
- `linear_list_teams` - List teams
- `linear_list_users` - List users
- `linear_get_team` - Get team details
- `linear_create_project` - Create project

**Context7 (2 tools)** - Library Documentation
- `context7_resolve_library_id` - Find library ID for docs
  - Example: `context7_resolve_library_id libraryName="react"`
- `context7_get_library_docs` - Fetch library documentation
  - Example: `context7_get_library_docs context7CompatibleLibraryID="/facebook/react"`

**Thinking (1 tool)** - Complex Reasoning
- `sequentialthinking` - Sequential thought process
  - Use for: Complex problem decomposition, multi-step reasoning

**Syntropy (2 tools)** - System Utilities
- `healthcheck` - Check MCP server health
  - Example: `healthcheck detailed=true`
- `knowledge_search` - Search across PRPs, memories, examples
  - Example: `knowledge_search query="authentication" limit=10`

**Total**: 25 MCP tools (+ 7 IDE/system tools = 32 total)
```

**Step 9**: Write Section 6 - Migration Table (~300 words)
```markdown
## 6. Migration from Old Tools

Complete mapping of all 55 denied tools to their replacements:

### Filesystem Tools → Native Tools

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `filesystem_read_file` | `Read` | Direct, faster, no MCP overhead |
| `filesystem_read_text_file` | `Read` | Same as above |
| `filesystem_write_file` | `Write` | Direct, simpler API |
| `filesystem_edit_file` | `Edit` | More precise (old_string/new_string) |
| `filesystem_list_directory` | `Bash ls` or `Glob` | Glob for patterns, ls for simple listing |
| `filesystem_search_files` | `Glob` | Optimized for pattern matching |
| `filesystem_directory_tree` | `Bash tree` | Native tree command |
| `filesystem_get_file_info` | `Bash stat` or `ls -l` | Native file info commands |

### Git Tools → Bash Git Commands

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `git_git_status` | `Bash git status` | More flexible, supports all flags |
| `git_git_diff` | `Bash git diff` | Full diff options (--cached, --stat, etc.) |
| `git_git_log` | `Bash git log` | All log formatting options available |
| `git_git_add` | `Bash git add` | Direct command execution |
| `git_git_commit` | `Bash git commit` | Full commit options (--amend, etc.) |

### GitHub Tools → Bash gh CLI

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `github_create_or_update_file` | `Bash gh api` or git push | Official GitHub CLI |
| `github_search_repositories` | `Bash gh search repos` | Comprehensive search |
| `github_create_repository` | `Bash gh repo create` | Full repo creation options |
| `github_get_file_contents` | `Bash gh api` or `Read` local | Fetch via API or read local |
| `github_push_files` | `Bash git push` | Standard git workflow |
| `github_create_issue` | `Bash gh issue create` | Official issue creation |
| `github_create_pull_request` | `Bash gh pr create` | Full PR options |
| `github_fork_repository` | `Bash gh repo fork` | Fork with gh CLI |
| `github_create_branch` | `Bash git checkout -b` | Native git branch |
| `github_list_commits` | `Bash gh api` or `git log` | List commits via API or git |
| `github_list_issues` | `Bash gh issue list` | Filter, sort, search issues |
| `github_update_issue` | `Bash gh issue edit` | Update issue fields |
| `github_add_issue_comment` | `Bash gh issue comment` | Add comments |
| `github_search_code` | `Bash gh search code` | Search code across repos |
| `github_search_issues` | `Bash gh search issues` | Advanced issue search |
| `github_search_users` | `Bash gh search users` | User search |
| `github_get_issue` | `Bash gh issue view` | View issue details |
| `github_get_pull_request` | `Bash gh pr view` | View PR details |
| `github_list_pull_requests` | `Bash gh pr list` | List and filter PRs |
| `github_create_pull_request_review` | `Bash gh pr review` | Review PRs |
| `github_merge_pull_request` | `Bash gh pr merge` | Merge with options |
| `github_get_pull_request_files` | `Bash gh pr diff` | Show changed files |
| `github_get_pull_request_status` | `Bash gh pr checks` | Check CI status |
| `github_update_pull_request_branch` | `Bash git merge` or `gh pr` | Update PR branch |
| `github_get_pull_request_comments` | `Bash gh pr view --comments` | View comments |
| `github_get_pull_request_reviews` | `Bash gh pr view --reviews` | View reviews |

### Repomix Tools → Incremental Exploration

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `repomix_pack_codebase` | `Glob + Grep + Read` | Incremental, more efficient |
| `repomix_grep_repomix_output` | `Grep` directly | Search files directly |
| `repomix_read_repomix_output` | `Read` directly | Read files directly |
| `repomix_pack_remote_repository` | Clone + explore | Clone repo, use native tools |

### Playwright Tools → WebFetch/Bash

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `playwright_navigate` | `WebFetch` | For content fetching |
| `playwright_screenshot` | Bash playwright CLI | If really needed |
| `playwright_click` | N/A | Not needed for CLI tools |
| `playwright_fill` | N/A | Not needed for CLI tools |
| `playwright_evaluate` | N/A | Not needed for CLI tools |
| `playwright_get_visible_text` | `WebFetch` | Extract text from URL |

### Perplexity Tools → WebSearch

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `perplexity_ask` | `WebSearch` | Native AI-powered search |

### Syntropy System Tools → Native/Kept Tools

| Old Tool (Denied) | New Tool | Notes |
|-------------------|----------|-------|
| `init_project` | Manual setup | One-time operation |
| `get_system_doc` | `Read .ce/FILE` | Direct file reading |
| `get_user_doc` | `Read FILE` | Direct file reading |
| `get_summary` | Bash commands | Use native tools |
| `denoise` | N/A | Specialized, rare use |

**Kept Tools** (not denied):
- `healthcheck` - MCP diagnostics
- `knowledge_search` - Semantic search across PRPs/memories
```

### Phase 3: Finalization (3 min)

**Step 10**: Add table of contents (optional)
```markdown
## Table of Contents

1. [Philosophy](#1-philosophy)
2. [Decision Tree](#2-decision-tree)
3. [Common Tasks](#3-common-tasks)
4. [Anti-Patterns](#4-anti-patterns)
5. [Tool Quick Reference](#5-tool-quick-reference)
6. [Migration from Old Tools](#6-migration-from-old-tools)
```

**Step 11**: Format and validate
- Ensure all markdown tables render correctly
- Verify all code blocks have proper syntax highlighting
- Check all tool names are accurate
- Verify examples are executable

**Step 12**: Add footer
```markdown
---

**Version**: 1.0
**Last Updated**: 2025-10-29
**Status**: Active
**Related**: TOOL-PERMISSION-LOCKDOWN-PLAN.md, PRP-A-tool-deny-list.md
```

---

## 4. Validation Gates

### Gate 1: File Created
**Command**: `ls TOOL-USAGE-GUIDE.md`
**Expected**: File exists at project root
**On Failure**: Verify file path, check write permissions

### Gate 2: All Sections Present
**Command**: `grep -c "^## [1-6]" TOOL-USAGE-GUIDE.md`
**Expected**: 6 (all sections present)
**On Failure**: Add missing sections

### Gate 3: Migration Table Complete
**Command**: `grep -c "Old Tool (Denied)" TOOL-USAGE-GUIDE.md`
**Expected**: 7 (one per category: Filesystem, Git, GitHub, Repomix, Playwright, Perplexity, Syntropy)
**On Failure**: Add missing migration entries

### Gate 4: Markdown Renders Correctly
**Command**: Visual inspection in markdown viewer or GitHub
**Expected**: All tables render, no broken formatting
**On Failure**: Fix markdown syntax, check table alignment

### Gate 5: Examples Accurate
**Command**: Manual spot-check of 5-10 examples
**Expected**: All examples are valid, executable commands/tool calls
**On Failure**: Correct examples, verify tool names

---

## 5. Testing Strategy

### Test Framework
Manual content validation + markdown rendering

### Test Command
```bash
# Check file exists
ls TOOL-USAGE-GUIDE.md

# Count sections
grep -c "^## [1-6]" TOOL-USAGE-GUIDE.md

# Validate markdown (if markdownlint installed)
markdownlint TOOL-USAGE-GUIDE.md

# View in browser/viewer
open TOOL-USAGE-GUIDE.md  # macOS
```

### Unit Tests
1. **File exists**: Created at correct path
2. **All sections present**: 6 sections complete
3. **Migration table**: Covers all 55 denied tools

### Integration Tests
1. **Renders correctly**: View in markdown viewer
2. **Links work**: TOC links jump to sections (if included)
3. **Tables format**: All tables display properly

### Functional Tests
1. **Examples executable**: Spot-check 10 examples
2. **Tool names accurate**: Cross-reference with PRP-A
3. **Complete coverage**: All use cases covered

---

## 6. Rollout Plan

### Phase 1: Development
- Create worktree: `git worktree add ../ctx-eng-plus-prp-b -b prp-b-tool-usage-guide`
- Execute steps 1-12 in worktree
- Write all 6 sections (~400-500 lines total)
- Validate all gates pass
- Commit: `git commit -m "Create TOOL-USAGE-GUIDE.md with 6 sections"`

### Phase 2: Review
- Push branch: `git push -u origin prp-b-tool-usage-guide`
- Create PR: `gh pr create --title "PRP-B: Tool Usage Guide" --base main`
- Self-review: Check all sections, validate examples
- Merge when ready

### Phase 3: Integration
- Merge order: 2 (merge after PRP-A, before PRP-C)
- No conflicts expected (new file)
- Verify: File renders correctly on GitHub
- Reference: PRP-E will add links to this guide from CLAUDE.md

### Rollback Strategy
```bash
# If issues occur (simple - just delete file)
rm TOOL-USAGE-GUIDE.md

# Or revert commit
git revert HEAD
```

---

## Research Findings

### Content Sources
- **Philosophy**: Based on native-first principle from TOOL-PERMISSION-LOCKDOWN-PLAN.md
- **Decision Tree**: Covers all common operations from project workflow
- **Common Tasks**: Synthesized from actual project usage patterns
- **Anti-Patterns**: Direct mapping from PRP-A deny list
- **Quick Reference**: All 32 kept MCP tools + native tools
- **Migration Table**: Complete mapping of all 55 denied tools

### Tool Categorization
- **Native**: 7 tools (Read, Write, Edit, Glob, Grep, Bash, Task)
- **MCP Kept**: 25 tools (Serena 11, Linear 9, Context7 2, thinking 1, Syntropy 2)
- **MCP Denied**: 55 tools (categorized in migration table)

### Example Quality
All examples are:
- Copy-paste executable
- Real-world use cases
- Properly formatted (code blocks, syntax highlighting)
- Tested for accuracy

---

**Completion Criteria**:
- [ ] File created at project root
- [ ] All 6 sections complete (~400-500 lines)
- [ ] Migration table covers all 55 denied tools
- [ ] 15+ common task examples
- [ ] Markdown renders correctly
- [ ] Examples are accurate and executable
- [ ] Native-first philosophy clear throughout
