---
feature: Tool Permission Documentation Update
prp_id: TBD
author: Blazej Przybyszewski
created: 2025-10-17
priority: high
category: documentation
---

# INITIAL: Document Current Tool Permission Reality

## Feature Description

Update documentation suite to reflect ACTUAL working tool permissions (46 allowed, 124 denied), not outdated study recommendations. The `tools-rationalization-study.md` document contains outdated recommendations that don't align with current empirically-optimized configuration.

## Problem Statement

**Current Issue**: Documentation is generic and doesn't reflect actual permission configuration.

**Study Discrepancies Found**:
- Study recommends denying tools we actively use (Linear, Context7, Sequential-thinking, find_referencing_symbols, edit_file)
- Study recommends allowing tools already denied (replace_symbol_body, insert_after_symbol, read_memory)
- Study counts are wrong (claims 45→31, reality is 46 allowed tools optimized for workflows)

**Impact**: Confusing guidance for agents and developers, potential workflow breakage if study recommendations followed.

## Proposed Solution

Document the current reality across 3 files with consistent 46-tool allow list organized by category.

### Files to Update

1. **CLAUDE.md** - Tool Selection Quick Reference section (lines 139-166)
   - Add explicit categorized allow list
   - Note study is outdated reference

2. **.serena/memories/tool-usage-guide.md** - Append new section
   - Document current 46-tool configuration
   - Explain rationale for each category
   - Note historical study limitations

3. **.serena/memories/serena-mcp-tool-restrictions.md** - Append new section
   - List current allowed/denied Serena tools
   - Document critical workflow tools preserved
   - Explain workaround strategies

### New Python Utility

**Created**: `tools/ce/validate_permissions.py`

**Purpose**: Replace forbidden jq/grep commands with Python-based validation

**Commands**:
```bash
cd tools && uv run python -m ce.validate_permissions count
cd tools && uv run python -m ce.validate_permissions categorize
cd tools && uv run python -m ce.validate_permissions verify <tool_name>
cd tools && uv run python -m ce.validate_permissions search <pattern> [allow|deny]
```

## Current Tool Configuration (Verified)

### Allow List: 46 Tools

**By Category**:
- **Bash patterns**: 11 (git, uv, env, brew, mcp-auth)
- **Serena**: 7 (find_symbol, overview, search, referencing, memory, create, activate)
- **Filesystem**: 8 (read, write, edit, list, search, tree, info, allowed_dirs)
- **Git**: 5 (status, diff, log, add, commit)
- **Context7**: 2 (resolve-library-id, get-library-docs)
- **Sequential-thinking**: 1 (sequentialthinking)
- **Linear**: 5 (create/get/list/update issues, list_projects)
- **Repomix**: 1 (pack_codebase)
- **Special**: 6 (Read paths, WebFetch, SlashCommands)

### Deny List: 124 Tools

**Major Categories**:
- Serena advanced: 13 (symbol mutations, thinking tools, modes, memories)
- Filesystem redundant: 6 (read variants, move, sizes)
- Git advanced: 6 (branch, checkout, show, reset, diff variants)
- GitHub MCP: 26 (all operations - use git CLI instead)
- Playwright: 31 (web automation not needed)
- Perplexity: 1 (redundant)
- Repomix partial: 4 (remote ops)
- IDE: 2 (diagnostics, executeCode)
- Linear extended: 14 (comments, cycles, docs, labels, teams, users)
- Bash text processing: 11 (cat, head, tail, find, grep, wc, awk, sed, echo, python)

## Rationale

### Why Current Config is Optimal

**Linear tools preserved** (5 tools):
- PRP generation workflow (`/generate-prp`) requires issue creation/tracking
- Auto-creates Linear issues with defaults from `.ce/linear-defaults.yml`
- Issue joining pattern documented in CLAUDE.md lines 643-651

**Context7 preserved** (2 tools):
- Documentation lookup essential for external library integration
- Used in tool-usage-patterns.md lines 307-318

**Sequential-thinking preserved** (1 tool):
- Complex reasoning for PRP generation and multi-step problem decomposition
- Used in tool-usage-patterns.md lines 328-337

**find_referencing_symbols preserved**:
- Impact analysis before code changes critical for safety
- Referenced in tool-usage-patterns.md lines 54, 451

**edit_file preserved**:
- Primary tool for surgical code edits
- Referenced in tool-usage-patterns.md lines 105-118
- Workaround for denied `replace_symbol_body`

## Success Criteria

- [ ] Python validation tool created and tested
- [ ] Tool counts verified: 46 allowed, 124 denied
- [ ] CLAUDE.md updated with categorized 46-tool list
- [ ] tool-usage-guide.md updated with permission section
- [ ] serena-mcp-tool-restrictions.md updated with current config
- [ ] All 3 files consistent (same tool lists, counts, categories)
- [ ] Study marked as outdated with explanation
- [ ] No forbidden bash commands (jq, grep) in validation instructions

## Examples

### Validation Tool Usage

```bash
# Count tools
cd tools && uv run python -m ce.validate_permissions count
# Output: Allow: 46, Deny: 124

# Show categorized breakdown
cd tools && uv run python -m ce.validate_permissions categorize
# Output: Full category listing

# Verify critical tool exists
cd tools && uv run python -m ce.validate_permissions verify mcp__linear-server__create_issue
# Output: In allow: True, In deny: False

# Search for Linear tools
cd tools && uv run python -m ce.validate_permissions search linear allow
# Output: All 5 Linear tools listed
```

## Testing Strategy

1. **Validation Tool**: Run all 4 commands (count, categorize, verify, search)
2. **Cross-Reference**: Ensure 3 updated files have matching tool lists
3. **Workflow Verification**: Confirm documented workflows still reference allowed tools
4. **Study Comparison**: Document specific discrepancies with study recommendations

## Non-Goals

- ❌ Modifying `.claude/settings.local.json` permissions
- ❌ Implementing study recommendations (they're flawed)
- ❌ Changing actual tool configuration (just documenting reality)
- ❌ Creating new workflows (only documenting existing ones)

## Dependencies

- Existing `.claude/settings.local.json` (read-only)
- Python 3.x with json, pathlib (stdlib)
- UV for running Python scripts

## Risks

**Low Risk**: Pure documentation update, no behavioral changes.

**Mitigation**: Validation tool ensures docs match actual configuration.

## Alternative Approaches Considered

1. **Follow Study Recommendations**: ❌ Would break Linear integration, Context7 docs, Sequential-thinking
2. **Hybrid Approach**: ❌ Complex, study too flawed for partial adoption
3. **Document Reality**: ✅ **CHOSEN** - Simple, accurate, maintains working config

## Open Questions

- Should we archive or delete tools-rationalization-study.md entirely? (Currently: add deprecation note)
- Should validation tool be added to pre-commit hooks? (Future consideration)

## References

- Current config: `.claude/settings.local.json`
- Study document: `PRPs/feature-requests/tools-rationalization-study.md`
- Tool patterns: `examples/tool-usage-patterns.md`
- Project guide: `CLAUDE.md`
- Serena memories: `.serena/memories/tool-usage-guide.md`, `.serena/memories/serena-mcp-tool-restrictions.md`
