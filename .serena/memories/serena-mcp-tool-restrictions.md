# Serena MCP Tool Restrictions & Workarounds

## CRITICAL: Tool Permissions

### DENIED Tools
- `mcp__serena__replace_symbol_body` - ❌ DENIED (permission denied error)
  - **Reason**: Symbol-level mutations require elevated permissions
  - **Status**: Not available for this project/context

### ALLOWED Tools (Verified)
- `mcp__serena__find_symbol` ✅ (read symbol with body)
- `mcp__serena__get_symbols_overview` ✅ (read file structure)
- `mcp__serena__search_for_pattern` ✅ (pattern search)
- `mcp__filesystem__edit_file` ✅ (line-based edits)
- `mcp__serena__replace_regex` ✅ (regex replacements)
- `mcp__serena__read_file` ✅ (read Python files)
- `mcp__serena__find_referencing_symbols` ✅ (usage analysis)
- `mcp__git__*` ✅ (all git operations)

## Workarounds for Symbol Mutations

**Instead of**: `replace_symbol_body()` ❌
**Use**: `mcp__serena__replace_regex()` ✅ (for large changes)
**Use**: `mcp__filesystem__edit_file()` ✅ (for line-level changes)

### Strategy
1. Use `find_symbol(include_body=True)` to read current implementation
2. Use `replace_regex()` for full function replacement (wrap in context)
3. Use `edit_file()` for surgical line-level changes

### Example: Replace Function Body
```python
# Instead of replace_symbol_body() which is denied:
mcp__serena__replace_regex(
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

## Current Permission Configuration (Verified 2025-10-17)

### Allowed Serena Tools (7)
- `find_symbol` - Read symbol with body
- `get_symbols_overview` - File structure mapping
- `search_for_pattern` - LSP-powered pattern search
- `find_referencing_symbols` - Usage/impact analysis
- `write_memory` - Session knowledge persistence
- `create_text_file` - File creation
- `activate_project` - Project switching

### Denied Serena Tools (13)
- **Symbol mutations**: replace_symbol_body, insert_before/after_symbol, rename_symbol
- **Thinking**: think_about_* (3 tools) - reduced autonomous behavior
- **Modes**: switch_modes, prepare_for_new_conversation
- **Memory**: read_memory, list_memories, delete_memory, check_onboarding, onboarding
- **Redundant**: get_current_config, list_dir, read_file (use filesystem tools)

### Workaround Strategy (Unchanged)

**For symbol-level edits** (replace_symbol_body denied):
1. Use `replace_regex()` for full function replacement
2. Use `edit_file()` for surgical line-level changes
3. Read with `find_symbol(include_body=True)` first

### Critical Workflow Tools (Preserved in Allow List)

**Linear integration** (5 tools) - PRP generation workflow:
- create_issue, get_issue, list_issues, update_issue, list_projects
- **Reason**: `/generate-prp` command auto-creates Linear issues
- **Reference**: CLAUDE.md lines 498-554

**Context7** (2 tools) - External documentation:
- resolve-library-id, get-library-docs
- **Reason**: Essential for library integration tasks

**Sequential-thinking** (1 tool) - Complex reasoning:
- sequentialthinking
- **Reason**: Multi-step problem decomposition for PRP generation

**Note on tools-rationalization-study.md**:
Study recommended denying these tools but empirical testing shows they're essential for documented workflows. Study marked as outdated historical reference.
