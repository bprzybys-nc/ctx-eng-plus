# Serena MCP Tool Restrictions & Workarounds

**Updated**: 2025-10-20 for Syntropy MCP
**Status**: All tools now route through Syntropy aggregation layer

## CRITICAL: Tool Permissions

### DENIED Tools (Syntropy Format)
- `mcp__syntropy__serena__replace_symbol_body` - ❌ DENIED (permission denied error)
  - **Reason**: Symbol-level mutations require elevated permissions
  - **Status**: Not available for this project/context

### ALLOWED Tools (Verified - Syntropy Format)
- `mcp__syntropy__serena__find_symbol` ✅ (read symbol with body)
- `mcp__syntropy__serena__get_symbols_overview` ✅ (read file structure)
- `mcp__syntropy__serena__search_for_pattern` ✅ (pattern search)
- `mcp__syntropy__filesystem__edit_file` ✅ (line-based edits)
- `mcp__syntropy__serena__replace_regex` ✅ (regex replacements)
- `mcp__syntropy__serena__read_file` ✅ (read Python files)
- `mcp__syntropy__serena__find_referencing_symbols` ✅ (usage analysis)
- `mcp__syntropy__git__*` ✅ (all git operations)

## Workarounds for Symbol Mutations (Syntropy Format)

**Instead of**: `replace_symbol_body()` ❌
**Use**: `mcp__syntropy__serena__replace_regex()` ✅ (for large changes)
**Use**: `mcp__syntropy__filesystem__edit_file()` ✅ (for line-level changes)

### Strategy
1. Use `mcp__syntropy__serena__find_symbol(include_body=True)` to read current implementation
2. Use `mcp__syntropy__serena__replace_regex()` for full function replacement (wrap in context)
3. Use `mcp__syntropy__filesystem__edit_file()` for surgical line-level changes

### Example: Replace Function Body
```python
# Instead of replace_symbol_body() which is denied:
mcp__syntropy__serena__replace_regex(
    relative_path="tools/ce/update_context.py",
    regex="def remediate_drift_workflow\\(yolo_mode.*?^def \\w+|^\\Z",  # Match function until next function
    repl="def remediate_drift_workflow(yolo_mode: bool = False) -> Dict[str, Any]:\n...",
    allow_multiple_occurrences=False
)
```

## Settings Restrictions

**CRITICAL**: `.claude/settings.local.json` cannot be overwritten
- User instruction: "NEVER OVERWRITE permissions or I WILL BE UNHAPPY"
- Deny list is intentional - respect it
- Don't try to modify tool restrictions directly

## Current Project Context
- **Project**: Context Engineering Tools (ctx-eng-plus)
- **Affected File**: tools/ce/update_context.py
- **Task**: Add PRP execution to remediate_drift_workflow()
- **Restriction**: Cannot use symbol_body mutations
- **Solution**: Use regex-based replacement instead

## Action Items
1. ✅ Identify restriction (replace_symbol_body denied)
2. ⏳ Use `replace_regex()` to update function
3. ⏳ Test the change works
4. ⏳ Verify workflow end-to-end

---

## Current Permission Configuration (Verified 2025-10-20)

### Allowed Tools via Syntropy (30 total)

**Serena Tools** (8):
- `mcp__syntropy__serena__find_symbol` - Read symbol with body
- `mcp__syntropy__serena__get_symbols_overview` - File structure mapping
- `mcp__syntropy__serena__search_for_pattern` - LSP-powered pattern search
- `mcp__syntropy__serena__find_referencing_symbols` - Usage/impact analysis
- `mcp__syntropy__serena__write_memory` - Session knowledge persistence
- `mcp__syntropy__serena__create_text_file` - File creation
- `mcp__syntropy__serena__activate_project` - Project switching
- `mcp__syntropy__serena__replace_regex` - Regex replacements (workaround for mutations)

**Filesystem Tools** (8):
- `mcp__syntropy__filesystem__read_text_file` - Read config/text files
- `mcp__syntropy__filesystem__write_file` - Create/overwrite files
- `mcp__syntropy__filesystem__edit_file` - Line-based edits (workaround for mutations)
- `mcp__syntropy__filesystem__list_directory` - Directory listing
- `mcp__syntropy__filesystem__search_files` - File pattern search
- `mcp__syntropy__filesystem__directory_tree` - Tree view
- `mcp__syntropy__filesystem__get_file_info` - File metadata
- `mcp__syntropy__filesystem__list_allowed_directories` - Allowed paths

**Git Tools** (5):
- `mcp__syntropy__git__git_status` - Repository status
- `mcp__syntropy__git__git_diff` - Show changes
- `mcp__syntropy__git__git_log` - Commit history
- `mcp__syntropy__git__git_add` - Stage files
- `mcp__syntropy__git__git_commit` - Create commits

**Other Tools** (9):
- `mcp__syntropy__context7__resolve_library_id` - Resolve library docs
- `mcp__syntropy__context7__get_library_docs` - Fetch library documentation
- `mcp__syntropy__thinking__sequentialthinking` - Complex reasoning
- `mcp__syntropy__linear__create_issue` - Create Linear issues
- `mcp__syntropy__linear__get_issue` - Retrieve issues
- `mcp__syntropy__linear__list_issues` - List issues
- `mcp__syntropy__linear__update_issue` - Update issues
- `mcp__syntropy__linear__list_projects` - List projects
- `mcp__syntropy__repomix__pack_codebase` - Package codebase

### Denied Tools (Serena - not available via Syntropy)

- **Symbol mutations**: replace_symbol_body, insert_before/after_symbol, rename_symbol
- **Thinking**: think_about_* (3 tools) - reduced autonomous behavior
- **Modes**: switch_modes, prepare_for_new_conversation
- **Memory**: read_memory, list_memories, delete_memory, check_onboarding, onboarding
- **Redundant**: get_current_config, list_dir, read_file (use Syntropy filesystem tools)

### Workaround Strategy (Syntropy Updated)

**For symbol-level edits** (replace_symbol_body denied):
1. Use `mcp__syntropy__serena__replace_regex()` for full function replacement
2. Use `mcp__syntropy__filesystem__edit_file()` for surgical line-level changes
3. Read with `mcp__syntropy__serena__find_symbol(include_body=True)` first

### Critical Workflow Tools (Preserved in Allow List - Syntropy Forwarded)

#### Linear Integration (5 tools) - PRP Generation Workflow

**Tools** (via Syntropy):
- `mcp__syntropy__linear__create_issue` - Create new Linear issues
- `mcp__syntropy__linear__get_issue` - Retrieve issue details
- `mcp__syntropy__linear__list_issues` - List issues with filtering
- `mcp__syntropy__linear__update_issue` - Update issue status/content
- `mcp__syntropy__linear__list_projects` - List available projects

**Why Preserved**:
- The `/generate-prp` command automatically creates Linear issues to track implementation work
- Essential for documented PRP workflow (see CLAUDE.md lines 498-554)
- Enables issue tracking for feature implementation blueprints

**Usage Example**:
```python
# Create issue from PRP generation
mcp__syntropy__linear__create_issue(
    team="Blaise78",
    title="PRP-25: Feature Implementation",
    description="Detailed feature from PRP blueprint",
    assignee="blazej.przybyszewski@gmail.com"
)

# Update issue status as implementation progresses
mcp__syntropy__linear__update_issue(
    issue_number="BLA-42",
    state="in_progress"
)
```

---

#### Context7 Documentation (2 tools) - Library Integration

**Tools** (via Syntropy):
- `mcp__syntropy__context7__resolve_library_id` - Resolve library identifiers
- `mcp__syntropy__context7__get_library_docs` - Fetch library documentation

**Why Preserved**:
- Essential for integrating external library documentation into PRPs
- Enables lookups for API references, framework guides, best practices
- Required for knowledge-grounded implementation planning

**Usage Example**:
```python
# Step 1: Resolve library ID
lib_id = mcp__syntropy__context7__resolve_library_id(
    libraryName="FastAPI"
)

# Step 2: Get documentation for specific topic
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID=lib_id,
    topic="dependency_injection"
)
```

---

#### Sequential Thinking (1 tool) - Complex Reasoning

**Tool** (via Syntropy):
- `mcp__syntropy__thinking__sequentialthinking` - Multi-step problem decomposition

**Why Preserved**:
- Enables structured reasoning for complex PRP generation
- Used for planning multi-phase implementations
- Essential for breaking down large features into manageable PRPs

**Usage Example**:
```python
# Structure complex problem solving
mcp__syntropy__thinking__sequentialthinking(
    thought="Step 1: Analyze current architecture and identify service boundaries",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# ... continue with thoughtNumber 2-5 for full decomposition
```

---

### Historical Note

**`PRPs/feature-requests/tools-rationalization-study.md`**:
- Study recommended denying Linear, Context7, and Sequential-thinking tools
- Empirical testing showed this recommendation was incorrect
- These tools are essential for documented workflows (see CLAUDE.md)
- Study marked as outdated historical reference
- Current configuration is empirically validated and production-tested

### Why These Tools Matter

**Without these critical tools, the following workflows break**:
1. ❌ PRP generation cannot auto-create Linear issues (breaks issue tracking)
2. ❌ External library integration impossible (blocks knowledge-grounded PRPs)
3. ❌ Complex problem decomposition unavailable (limits reasoning for large features)

**With these tools**:
1. ✅ Complete feature tracking from conception to completion
2. ✅ Knowledge-enriched implementations using real library docs
3. ✅ Structured reasoning for complex architectural decisions
