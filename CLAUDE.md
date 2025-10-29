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

## GitButler Integration

**Virtual branch management for parallel multi-PRP development**
**Use it to work on multiple PRPs at the same time**

📖 **Command Reference**: [examples/GITBUTLER-BUT-COMMAND-REFERENCE.md](examples/GITBUTLER-BUT-COMMAND-REFERENCE.md)
📚 **Full Guide**: [test-target/GITBUTLER-INTEGRATION-GUIDE.md](test-target/GITBUTLER-INTEGRATION-GUIDE.md)

### Quick Start
```bash
# Install (if not already installed)
brew install --cask gitbutler
# Install CLI via GitButler app: Settings → General → Install CLI

# Initialize repo
but init

# Check status
but status
```

### Commands
- `but status` - Check virtual branches
- `but branch new <name>` - Create branch
- `but commit <branch> -m "msg"` - Commit to specific branch
- `but branch list` - List all branches
- `but branch delete <name>` - Delete branch

### Workflow
1. Create branch per PRP: `but branch new "prp-XX-feature"`
2. Make changes with Claude (Edit/Write)
3. Commit: `but commit prp-XX-feature -m "Implement X"`
4. Review/merge in GitButler UI

### Benefits
- Work on multiple PRPs simultaneously
- No branch switching (`git checkout`)
- Conflict detection without blocking (🔒 icon)
- Visual branch management in UI
- Changes auto-merged in `gitbutler/workspace` branch

### Hooks (Already Configured)
- **SessionStart**: Shows status if repo is GitButler-initialized
- **PreToolUse**: Shows status before git commits
- **Edit/Write**: Reminds to target correct branch

### Example: Multi-PRP Development
```bash
# Work on PRP-30 and PRP-31 simultaneously
but branch new "prp-30-keyboard"
# Make changes...
but commit prp-30-keyboard -m "Add cmd+v"

but branch new "prp-31-validation"  # No checkout needed!
# Make changes...
but commit prp-31-validation -m "Add validation"

# Both branches coexist cleanly
but status
```

### Documentation
See: [test-target/GITBUTLER-INTEGRATION-GUIDE.md](test-target/GITBUTLER-INTEGRATION-GUIDE.md)

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
