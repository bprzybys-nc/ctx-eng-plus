# Tool Usage Guide - Claude Code Native-First Philosophy

**Last Updated**: 2025-11-08
**Status**: Authoritative reference for tool selection
**Replaces**: Obsolete MCP tool documentation

**See Also**:
- [Syntropy MCP Naming Convention](syntropy-mcp-naming-convention.md) - Complete naming spec, testing, prevention
- [Syntropy Naming Quick Guide](syntropy-naming-convention.md) - Quick reference for tool names

---

## Philosophy

### Native-First Principle

Use Claude Code native tools (Read, Write, Edit, Glob, Grep, Bash) over MCP wrappers whenever possible.

**Why?**

- **Token Efficiency**: 96% reduction in MCP tools context (~46k → ~2k tokens)
- **Performance**: Direct tool access, no MCP routing overhead
- **Reliability**: Fewer abstraction layers, clearer error messages
- **Universality**: Native tools work across all codebases without configuration

### When to Use MCP Tools

**Only use MCP tools for capabilities not available natively**:

- **Serena**: Code symbol navigation, memory management
- **Linear**: Issue tracking integration
- **Context7**: Library documentation fetching
- **Sequential Thinking**: Complex reasoning workflows
- **Syntropy**: System health checks, knowledge search

---

## Decision Tree

```
Need to [action]?
│
├─ File Operations?
│  ├─ Read file → Read (native)
│  ├─ Write new file → Write (native)
│  ├─ Edit existing → Edit (native)
│  └─ Find files → Glob (native)
│
├─ Code Search?
│  ├─ Search content → Grep (native)
│  ├─ Find symbol → mcp__syntropy__serena_find_symbol
│  └─ Symbol usage → mcp__syntropy__serena_find_referencing_symbols
│
├─ Version Control?
│  ├─ Git operations → Bash(git:*)
│  └─ GitHub API → Bash(gh:*)
│
├─ External Knowledge?
│  ├─ Web search → WebSearch (native)
│  ├─ Library docs → mcp__syntropy__context7_get_library_docs
│  └─ Web content → WebFetch (native)
│
├─ Project Management?
│  └─ Linear issues → mcp__syntropy__linear_*
│
└─ Complex Reasoning?
   └─ Multi-step analysis → mcp__syntropy__thinking_sequentialthinking
```

---

## Common Tasks

### Task 1: Read and Modify Files

**❌ WRONG (MCP)**:

```python
mcp__syntropy__filesystem_read_file(path="foo.py")
mcp__syntropy__filesystem_edit_file(path="foo.py", edits=[...])
```

**✅ CORRECT (Native)**:

```python
Read(file_path="/absolute/path/foo.py")
Edit(file_path="/absolute/path/foo.py", old_string="...", new_string="...")
```

**Why**: Native tools are direct, support more features (Edit preserves formatting), consume fewer tokens.

---

### Task 2: Search Codebase

**❌ WRONG (MCP)**:

```python
mcp__syntropy__filesystem_search_files(pattern="*.py")
mcp__syntropy__repomix_pack_codebase(directory=".")
```

**✅ CORRECT (Native + Serena)**:

```python
# Find files by pattern
Glob(pattern="**/*.py")

# Search content
Grep(pattern="def calculate", type="py", output_mode="content")

# Find specific symbol (when you know the name)
mcp__syntropy__serena_find_symbol(name_path="MyClass.calculate")
```

**Why**: Incremental exploration (Glob → Grep → Read) is more efficient than packing entire codebase. Serena is for symbol-level navigation.

---

### Task 3: Git Operations

**❌ WRONG (MCP)**:

```python
mcp__syntropy__git_git_status(repo_path="/path")
mcp__syntropy__git_git_commit(repo_path="/path", message="Fix bug")
```

**✅ CORRECT (Native Bash)**:

```bash
# Pre-approved: Bash(git:*)
git status
git diff --staged
git add file.py
git commit -m "Fix bug"
```

**Why**: Native `git` supports all flags, universally familiar, no MCP routing delay.

---

### Task 4: GitHub Operations

**❌ WRONG (MCP)**:

```python
mcp__syntropy__github_create_pull_request(owner="...", repo="...", ...)
mcp__syntropy__github_list_issues(owner="...", repo="...")
```

**✅ CORRECT (Native gh CLI)**:

```bash
# Pre-approved: Bash(gh:*)
gh pr create --title "Fix bug" --body "Description"
gh issue list --label bug
gh pr view 123
```

**Why**: Official GitHub CLI, more features, better docs, no permission complexity.

---

### Task 5: Find Symbol Usages

**✅ CORRECT (Serena - unique capability)**:

```python
# Find where MyClass.calculate is used
mcp__syntropy__serena_find_referencing_symbols(name_path="MyClass.calculate")

# Get overview of all symbols in file
mcp__syntropy__serena_get_symbols_overview(relative_path="src/utils.py")
```

**Why**: Serena provides AST-level symbol analysis not available via native tools.

---

### Task 6: Library Documentation

**✅ CORRECT (Context7 - unique capability)**:

```python
# Resolve library ID
mcp__syntropy__context7_resolve_library_id(libraryName="numpy")

# Fetch docs
mcp__syntropy__context7_get_library_docs(
  context7CompatibleLibraryID="/numpy/doc",
  topic="array indexing"
)
```

**Why**: Context7 provides curated, AI-optimized library docs not available via WebSearch.

---

### Task 7: Project Management

**✅ CORRECT (Linear - unique capability)**:

```python
# List issues
mcp__syntropy__linear_list_issues(team_id="TEAM-123")

# Create issue
mcp__syntropy__linear_create_issue(
  title="Bug: Login fails",
  team_id="TEAM-123",
  description="..."
)
```

**Why**: Direct Linear API integration not available via native tools.

---

### Task 8: Complex Reasoning

**✅ CORRECT (Sequential Thinking - unique capability)**:

```python
mcp__syntropy__thinking_sequentialthinking(
  thought="Analyzing trade-offs between approach A and B...",
  thoughtNumber=1,
  totalThoughts=5,
  nextThoughtNeeded=True
)
```

**Why**: Structured multi-step reasoning process not available natively.

---

### Task 9: System Health Check

**✅ CORRECT (Syntropy - unique capability)**:

```python
# Quick health check
mcp__syntropy__healthcheck()

# Detailed diagnostics
mcp__syntropy__healthcheck(detailed=True, timeout_ms=5000)
```

**Why**: Aggregates health across all MCP servers, not available via native tools.

---

## Anti-Patterns

### Anti-Pattern 1: Using MCP for Simple File Ops

**❌ WRONG**:

```python
mcp__syntropy__filesystem_read_file(path="config.json")
mcp__syntropy__filesystem_write_file(path="config.json", content="...")
```

**Problem**: Unnecessary MCP overhead, consumes more tokens, slower execution.

**✅ FIX**:

```python
Read(file_path="/absolute/path/config.json")
Write(file_path="/absolute/path/config.json", content="...")
```

---

### Anti-Pattern 2: Packing Entire Codebase

**❌ WRONG**:

```python
mcp__syntropy__repomix_pack_codebase(directory=".")
# Then search packed output
```

**Problem**: Monolithic approach, inefficient for incremental work, high token cost.

**✅ FIX**:

```python
# Incremental exploration
Glob(pattern="**/auth*.py")  # Find relevant files
Grep(pattern="def authenticate", type="py")  # Search specific pattern
Read(file_path="/path/to/auth.py")  # Read only what you need
```

---

### Anti-Pattern 3: MCP for Git Commands

**❌ WRONG**:

```python
mcp__syntropy__git_git_status(repo_path="/path")
mcp__syntropy__git_git_diff(repo_path="/path")
```

**Problem**: Limited flag support, unnecessary abstraction.

**✅ FIX**:

```bash
git status
git diff --staged
git log --oneline -10
```

---

### Anti-Pattern 4: Using Playwright for Simple Web Content

**❌ WRONG**:

```python
mcp__syntropy__playwright_navigate(url="https://example.com")
mcp__syntropy__playwright_get_visible_text()
```

**Problem**: Overkill for static content, slow browser startup.

**✅ FIX**:

```python
# For static content
WebFetch(url="https://example.com", prompt="Extract main content")

# For search queries
WebSearch(query="Python asyncio best practices")
```

---

### Anti-Pattern 5: GitHub MCP Instead of gh CLI

**❌ WRONG**:

```python
mcp__syntropy__github_create_pull_request(
  owner="user",
  repo="project",
  title="Fix",
  head="fix-branch",
  base="main",
  body="Description"
)
```

**Problem**: Verbose, requires explicit owner/repo, limited features.

**✅ FIX**:

```bash
# Infers owner/repo from current directory
gh pr create --title "Fix" --body "Description"
```

---

## Tool Quick Reference

### Native Tools (Always Prefer)

| Tool | Purpose | Example |
|------|---------|---------|
| **Read** | Read file contents | `Read(file_path="/abs/path/file.py")` |
| **Write** | Create new file | `Write(file_path="/abs/path/new.py", content="...")` |
| **Edit** | Modify existing file | `Edit(file_path="...", old_string="...", new_string="...")` |
| **Glob** | Find files by pattern | `Glob(pattern="**/*.py")` |
| **Grep** | Search file contents | `Grep(pattern="def foo", type="py", output_mode="content")` |
| **Bash** | Run shell commands | `Bash(command="git status")` |
| **WebSearch** | AI-powered search | `WebSearch(query="Python asyncio")` |
| **WebFetch** | Fetch web content | `WebFetch(url="...", prompt="Extract...")` |

### MCP Tools (Use Only When Native Unavailable)

#### Serena (Code Navigation) - 13 tools

| Tool | Purpose | Example |
|------|---------|---------|
| `mcp__syntropy__serena_activate_project` | Activate project for symbol indexing | `project="/abs/path/to/project"` |
| `mcp__syntropy__serena_find_symbol` | Find symbol definition | `name_path="MyClass.method"` |
| `mcp__syntropy__serena_get_symbols_overview` | List all symbols in file | `relative_path="src/utils.py"` |
| `mcp__syntropy__serena_find_referencing_symbols` | Find symbol usages | `name_path="MyClass.method"` |
| `mcp__syntropy__serena_replace_symbol_body` | Replace function/class body | `name_path="MyClass.method", new_body="..."` |
| `mcp__syntropy__serena_search_for_pattern` | Regex search | `pattern="def.*async"` |
| `mcp__syntropy__serena_list_dir` | List directory contents | `directory_path="src/"` |
| `mcp__syntropy__serena_read_file` | Read file contents | `relative_path="src/main.py"` |
| `mcp__syntropy__serena_create_text_file` | Create new text file | `path="new.py", content="..."` |
| `mcp__syntropy__serena_write_memory` | Store project context | `memory_type="architecture", content="..."` |
| `mcp__syntropy__serena_read_memory` | Retrieve context | `memory_name="architecture"` |
| `mcp__syntropy__serena_list_memories` | List all memories | No parameters |
| `mcp__syntropy__serena_delete_memory` | Delete memory | `memory_name="temporary"` |

#### Linear (Project Management) - 9 tools

| Tool | Purpose | Example |
|------|---------|---------|
| `mcp__syntropy__linear_create_issue` | Create issue | `title="Bug", team_id="..."` |
| `mcp__syntropy__linear_get_issue` | Get issue details | `issue_id="ISSUE-123"` |
| `mcp__syntropy__linear_list_issues` | List issues | `team_id="TEAM-123"` |
| `mcp__syntropy__linear_update_issue` | Update issue | `issue_id="...", updates={...}` |
| `mcp__syntropy__linear_list_projects` | List all projects | No parameters |
| `mcp__syntropy__linear_list_teams` | List all teams | No parameters |
| `mcp__syntropy__linear_get_team` | Get team details | `team_id="TEAM-123"` |
| `mcp__syntropy__linear_list_users` | List all users | No parameters |
| `mcp__syntropy__linear_create_project` | Create new project | `name="Project", team_id="..."` |

#### Context7 (Library Docs) - 2 tools

| Tool | Purpose | Example |
|------|---------|---------|
| `mcp__syntropy__context7_resolve_library_id` | Find library ID | `libraryName="numpy"` |
| `mcp__syntropy__context7_get_library_docs` | Fetch docs | `context7CompatibleLibraryID="/numpy/doc"` |

#### Thinking (Reasoning) - 1 tool

| Tool | Purpose | Example |
|------|---------|---------|
| `mcp__syntropy__thinking_sequentialthinking` | Structured reasoning | `thought="...", thoughtNumber=1` |

#### Syntropy (System) - 3 tools

| Tool | Purpose | Example |
|------|---------|---------|
| `mcp__syntropy__healthcheck` | Check MCP servers | `detailed=True` |
| `mcp__syntropy__enable_tools` | Enable/disable tools dynamically | `enable=["tool1"], disable=["tool2"]` |
| `mcp__syntropy__list_all_tools` | List all tools with enabled/disabled status | No parameters |

**Total: 28 allowed tools** (13 Serena + 9 Linear + 2 Context7 + 1 Thinking + 3 Syntropy)

---

## Migration Table: Denied Tools → Alternatives

### Filesystem (8 tools denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `filesystem_read_file` | **Read** (native) | `Read(file_path="/abs/path/file.py")` |
| `filesystem_read_text_file` | **Read** (native) | Same as above |
| `filesystem_write_file` | **Write** (native) | `Write(file_path="...", content="...")` |
| `filesystem_edit_file` | **Edit** (native) | `Edit(file_path="...", old_string="...", new_string="...")` |
| `filesystem_list_directory` | **Bash** (ls) | `Bash(command="ls -la /path")` |
| `filesystem_search_files` | **Glob** (native) | `Glob(pattern="**/*.py")` |
| `filesystem_directory_tree` | **Bash** (tree) | `Bash(command="tree -L 2")` |
| `filesystem_get_file_info` | **Bash** (stat) | `Bash(command="stat file.py")` |

### Git (5 tools denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `git_git_status` | **Bash(git)** | `Bash(command="git status")` |
| `git_git_diff` | **Bash(git)** | `Bash(command="git diff --staged")` |
| `git_git_log` | **Bash(git)** | `Bash(command="git log --oneline -10")` |
| `git_git_add` | **Bash(git)** | `Bash(command="git add file.py")` |
| `git_git_commit` | **Bash(git)** | `Bash(command='git commit -m "msg"')` |

### GitHub (26 tools denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `github_create_or_update_file` | **Bash(gh)** | `gh api repos/owner/repo/contents/path -f content=...` |
| `github_search_repositories` | **Bash(gh)** | `gh search repos "keyword"` |
| `github_create_repository` | **Bash(gh)** | `gh repo create name --public` |
| `github_get_file_contents` | **Bash(gh)** | `gh api repos/owner/repo/contents/path` |
| `github_push_files` | **Bash(git)** | `git add . && git commit -m "msg" && git push` |
| `github_create_issue` | **Bash(gh)** | `gh issue create --title "Bug" --body "..."` |
| `github_create_pull_request` | **Bash(gh)** | `gh pr create --title "Fix" --body "..."` |
| `github_fork_repository` | **Bash(gh)** | `gh repo fork owner/repo` |
| `github_create_branch` | **Bash(git)** | `git checkout -b branch-name` |
| `github_list_commits` | **Bash(gh)** | `gh api repos/owner/repo/commits` |
| `github_list_issues` | **Bash(gh)** | `gh issue list --label bug` |
| `github_update_issue` | **Bash(gh)** | `gh issue edit 123 --title "New"` |
| `github_add_issue_comment` | **Bash(gh)** | `gh issue comment 123 --body "..."` |
| `github_search_code` | **Bash(gh)** | `gh search code "query"` |
| `github_search_issues` | **Bash(gh)** | `gh search issues "bug"` |
| `github_search_users` | **Bash(gh)** | `gh search users "name"` |
| `github_get_issue` | **Bash(gh)** | `gh issue view 123` |
| `github_get_pull_request` | **Bash(gh)** | `gh pr view 123` |
| `github_list_pull_requests` | **Bash(gh)** | `gh pr list --state open` |
| `github_create_pull_request_review` | **Bash(gh)** | `gh pr review 123 --approve` |
| `github_merge_pull_request` | **Bash(gh)** | `gh pr merge 123 --squash` |
| `github_get_pull_request_files` | **Bash(gh)** | `gh pr diff 123` |
| `github_get_pull_request_status` | **Bash(gh)** | `gh pr checks 123` |
| `github_update_pull_request_branch` | **Bash(git)** | `git checkout branch && git pull origin main` |
| `github_get_pull_request_comments` | **Bash(gh)** | `gh pr view 123 --comments` |
| `github_get_pull_request_reviews` | **Bash(gh)** | `gh api repos/owner/repo/pulls/123/reviews` |

### Repomix (4 tools denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `repomix_pack_codebase` | **Glob + Grep + Read** | Incremental exploration |
| `repomix_grep_repomix_output` | **Grep** (native) | `Grep(pattern="...", output_mode="content")` |
| `repomix_read_repomix_output` | **Read** (native) | `Read(file_path="...")` |
| `repomix_pack_remote_repository` | **Bash(git clone)** + native tools | `git clone <url> && Glob/Grep/Read` |

### Playwright (6 tools denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `playwright_navigate` | **WebFetch** (static) or **Bash(playwright CLI)** (dynamic) | `WebFetch(url="...", prompt="...")` |
| `playwright_screenshot` | **Bash(playwright CLI)** | `playwright screenshot <url> screenshot.png` |
| `playwright_click` | **Bash(playwright CLI)** | Rarely needed for CLI tooling |
| `playwright_fill` | **Bash(playwright CLI)** | Rarely needed for CLI tooling |
| `playwright_evaluate` | **Bash(playwright CLI)** | Rarely needed for CLI tooling |
| `playwright_get_visible_text` | **WebFetch** | `WebFetch(url="...", prompt="Extract text")` |

### Perplexity (1 tool denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `perplexity_perplexity_ask` | **WebSearch** (native) | `WebSearch(query="Python asyncio patterns")` |

### Syntropy System (5 tools denied)

| Denied Tool | Alternative | Example |
|-------------|-------------|---------|
| `init_project` | **Manual setup** | One-time operation, rarely needed |
| `get_system_doc` | **Read** (native) | `Read(file_path=".ce/RULES.md")` |
| `get_user_doc` | **Read** (native) | `Read(file_path="PRPs/executed/PRP-1.md")` |
| `get_summary` | **Read** + manual analysis | Read REPLKAN, analyze structure |
| `denoise` | **Edit** (native) | Manually edit verbose docs |

---

## Best Practices

### 1. Start with Native Tools

Always check if Read/Write/Edit/Glob/Grep/Bash can solve the task before reaching for MCP tools.

### 2. Use Serena for Symbol Navigation

When you need to find a specific function/class definition or its usages across the codebase.

### 3. Incremental > Monolithic

Prefer Glob → Grep → Read over packing entire codebase with Repomix.

### 4. Bash for System Commands

Git, gh, tree, ls, find, etc. are pre-approved and more flexible than MCP wrappers.

### 5. MCP for Integration

Use MCP tools when you need external service integration (Linear, Context7) not available via native tools.

### 6. Validate with Healthcheck

Periodically run `mcp__syntropy__healthcheck(detailed=True)` to ensure all servers are connected.

---

## CE Framework Commands

The Context Engineering framework provides specialized commands for framework management. These are project-specific tools, not generic utilities.

### When to Use CE Commands

Use CE commands for:
- **Framework installation**: `ce init-project`
- **Content merging**: `ce blend`
- **Context updates**: `ce update-context`
- **Validation**: `ce validate`
- **Cleanup**: `ce vacuum`

**Do NOT** use CE commands for:
- Generic file operations (use native tools)
- General git operations (use Bash(git:*))
- External web requests (use WebFetch/WebSearch)

---

### ce init-project

**Purpose**: Initialize CE Framework in target project

**Usage**:
```bash
cd tools
uv run ce init-project ~/projects/target-app

# With flags
uv run ce init-project ~/projects/app --dry-run
uv run ce init-project ~/projects/app --phase extract
uv run ce init-project ~/projects/app --blend-only
```

**When to use**:
- Setting up CE framework in new project
- Upgrading existing CE installation
- Re-initializing after major changes

**Output**: 4-phase pipeline (extract → blend → initialize → verify)

**See**: [ce-init-project-usage.md](ce-init-project-usage.md) for comprehensive guide

---

### ce blend

**Purpose**: Merge CE framework files with target project customizations

**Usage**:
```bash
cd tools
uv run ce blend --all
uv run ce blend --claude-md --memories
uv run ce blend --all --target-dir ~/projects/app
```

**When to use**:
- After updating framework files (memories, examples)
- Re-merging user customizations
- Upgrading framework content

**Domains**: CLAUDE.md, memories, examples, settings, commands, PRPs

**See**: [ce-blend-usage.md](ce-blend-usage.md) for comprehensive guide

---

### ce update-context

**Purpose**: Sync PRPs with codebase implementation state

**Usage**:
```bash
cd tools
uv run ce update-context
uv run ce update-context --prp PRPs/executed/PRP-34.1.1-core-blending-framework.md
```

**When to use**:
- After completing PRP implementation
- Weekly system hygiene
- Detecting pattern drift

**Auto-features**:
- Rebuilds repomix packages if framework files changed
- Detects drift violations
- Updates YAML headers

**See**: `.claude/commands/update-context.md`

---

### ce validate

**Purpose**: Validate project structure and framework files

**Usage**:
```bash
cd tools
uv run ce validate --level all
uv run ce validate --level 4  # Pattern conformance
```

**Levels**:
- L1: File structure
- L2: YAML headers
- L3: Content validation
- L4: Pattern conformance

**See**: `.serena/memories/l4-validation-usage.md`

---

### ce vacuum

**Purpose**: Clean up temporary files and obsolete artifacts

**Usage**:
```bash
cd tools
uv run ce vacuum                  # Dry-run (report only)
uv run ce vacuum --execute        # Delete temp files
uv run ce vacuum --auto           # Delete temp + obsolete
```

**See**: `.claude/commands/vacuum.md`

---

### CE Command Patterns

**✅ CORRECT**:
```python
# Use ce commands for framework operations
Bash(command="cd tools && uv run ce blend --all")
Bash(command="cd tools && uv run ce init-project ~/projects/app")
```

**❌ WRONG**:
```python
# Don't use ce commands for generic operations
Bash(command="ce blend somefile.txt")  # Blend is not for arbitrary files
Bash(command="ce init-project .")      # Must run from tools/ directory
```

---

## Troubleshooting

### Issue: "Tool not found" error

**Cause**: Tool is in deny list or MCP server disconnected.

**Fix**:

1. Check `.claude/settings.local.json` permissions.deny
2. Run `mcp__syntropy__healthcheck(detailed=True)`
3. Reconnect MCP: `/mcp` (in main repo, not worktrees)

### Issue: "Permission denied" for Bash command

**Cause**: Command not in allow list.

**Fix**:

1. Check if command matches allow pattern: `Bash(git:*)`, `Bash(uv run:*)`, etc.
2. If needed frequently, add to allow list in settings
3. Temporary: User can approve via prompt

### Issue: MCP tool slow or timing out

**Cause**: Server connectivity issue or large operation.

**Fix**:

1. Check server health: `mcp__syntropy__healthcheck()`
2. Increase timeout if supported
3. Consider native alternative (e.g., Grep instead of repomix)

### Issue: Serena "symbol not found"

**Cause**: Incorrect name_path format or file not indexed.

**Fix**:

1. Use `serena_get_symbols_overview` to list all symbols in file
2. Ensure format: `ClassName.method_name` or `function_name`
3. Check relative_path is correct from project root

---

## See Also

**Code Examples**:

- `tools/ce/examples/syntropy/` - MCP tool usage patterns in Python
- `.serena/memories/` - Serena memory management examples and patterns

**Related Documentation**:

- `CLAUDE.md` - Project guide and quick commands
- `TOOL-PERMISSION-LOCKDOWN-PLAN.md` - Detailed rationale for tool deny list
- `PRPs/executed/PRP-B-tool-usage-guide.md` - PRP that created this guide

---

**End of Guide**

For questions or suggestions, update this guide via PR following Context Engineering framework.
