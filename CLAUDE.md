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

**Context7** (2): resolve_library_id, get_library_docs

**Thinking** (1): sequentialthinking

**Linear** (5): create_issue, get_issue, list_issues, update_issue, list_projects

**Repomix** (1): pack_codebase

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

**External knowledge**: `resolve_library_id`, `get_library_docs`

**Complex reasoning**: `sequentialthinking`

**Project management**: Linear tools

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
