---
prp_id: PRP-E
feature_name: Documentation Updates
status: executed
executed: 2025-10-29T00:00:00Z
execution_commit: 884b537
complexity: low
estimated_hours: 0.42-0.50
stage: stage-2-parallel
worktree_path: ../ctx-eng-plus-prp-e
branch_name: prp-e-doc-updates
execution_order: 2
merge_order: 5
files_modified:
  - CLAUDE.md
conflict_potential: NONE
dependencies:
  - PRP-B (reference TOOL-USAGE-GUIDE.md)
  - PRP-C (worktree workflow documented)
  - PRP-D (command permissions defined)
---

# PRP-E: Documentation Updates

## TL;DR

Update CLAUDE.md and related documentation to reflect all Stage 1 & 2 changes:
1. Add "Allowed Tools Summary" section (post-lockdown state)
2. Update "Quick Tool Selection" section (reference TOOL-USAGE-GUIDE.md)
3. Add "Command Permissions" section (document auto-allow, ask-first lists)
4. Remove obsolete MCP tool references
5. Update troubleshooting section

**Outcome**: Complete, accurate documentation reflecting tool & permission lockdown.

**Time**: 25-30 minutes
**Risk**: LOW (documentation only, no functional changes)
**Token Impact**: None (doc updates only)

---

## Context

### Current State

CLAUDE.md currently has:
- ✅ Git Worktree section (added in PRP-C)
- ✅ Tool naming convention
- ❌ Outdated "Allowed Tools Summary" (lists 87 tools, now only 32)
- ❌ Missing command permissions documentation
- ❌ References to denied MCP tools

### Problem

1. **Stale tool count**: "Available MCP Tools" shows 87, actual is 32
2. **Missing command permissions**: No documentation of auto-allow, ask-first patterns
3. **Outdated references**: References to denied tools (filesystem, git, github MCP)
4. **Incomplete troubleshooting**: No guidance on permission prompts

### Solution

Update CLAUDE.md sections:

**Section 1: Allowed Tools Summary**
- Update count: 87 → 32 tools
- Categorize kept tools:
  - Serena (11): Code navigation
  - Linear (9): Project management
  - Context7 (2): Library docs
  - Thinking (1): Complex reasoning
  - Syntropy (2): System tools (healthcheck, knowledge_search)
  - TOTAL: 32 (remainder denied for native tool preference)

**Section 2: Command Permissions**
- Document auto-allow patterns (~50)
- Document ask-first patterns (15)
- Reference never-allow patterns (6 documented)
- Explain permission behavior

**Section 3: Quick Tool Selection**
- Link to TOOL-USAGE-GUIDE.md for detailed guidance
- Update recommendations to use native tools
- Remove MCP tool suggestions that are now denied

**Section 4: Troubleshooting**
- Add "Permission prompt unexpectedly" issue
- Add "Command denied" issue
- Reference TOOL-USAGE-GUIDE.md

### Benefits

1. **Accuracy**: Documentation matches actual system state
2. **Clarity**: Users understand tool availability and permissions
3. **Discoverability**: Easy to find what tools are available
4. **Troubleshooting**: Clear guidance when issues arise

---

## Implementation Steps

### Phase 1: Preparation (5 minutes)

**Step 1**: Read current CLAUDE.md structure
```bash
Read(file_path="CLAUDE.md")
# Identify section boundaries
# Note line numbers for updates
```

**Step 2**: Locate sections to update
```bash
grep -n "## Allowed Tools" CLAUDE.md
grep -n "## Quick Tool Selection" CLAUDE.md
grep -n "## Troubleshooting" CLAUDE.md
```

**Step 3**: Verify TOOL-USAGE-GUIDE.md exists
```bash
test -f TOOL-USAGE-GUIDE.md && echo "✓ Guide exists"
```

### Phase 2: Section Updates (15 minutes)

**Step 4**: Update "Allowed Tools Summary" section

Replace existing content (around line 60-120) with:
```markdown
## Allowed Tools Summary

**Post-Lockdown State** (after PRP-A):
- **Before**: 87 MCP tools (via Syntropy aggregator)
- **After**: 32 MCP tools (55 denied for native tool preference)
- **Token reduction**: ~44k tokens (96% reduction)

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

**Bash Commands** (~50 patterns): See "Command Permissions" section
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
```

**Step 5**: Add "Command Permissions" section

Insert after "Allowed Tools Summary" (around line 120):
```markdown
## Command Permissions

**Permission Model**: Auto-allow safe commands, ask-first for potentially destructive operations.

### Auto-Allow Patterns (~50 patterns)

Commands that never prompt:

**File Inspection**:
- `ls`, `cat`, `head`, `tail`, `less`, `more`, `file`, `stat`

**Navigation**:
- `cd`, `pwd`, `which`, `whereis`

**Search**:
- `find`, `grep`, `rg`, `tree`

**Text Processing**:
- `sed`, `awk`, `sort`, `uniq`, `cut`, `paste`, `tr`
- `diff`, `comm`, `cmp`, `wc`

**Hashing/Encoding**:
- `md5`, `sha256sum`, `base64`, `xxd`, `strings`, `hexdump`

**System Info**:
- `env`, `ps`, `whoami`, `hostname`, `date`, `cal`, `bc`

**Development**:
- `git` (all operations), `uv run`, `uv add`, `uvx`
- `cat`, `grep`, `echo`, `jq`, `brew install`

**Special Cases**:
- `rm -rf ~/.mcp-auth` (MCP troubleshooting)

**Full list**: See `.claude/settings.local.json` "allow" array

### Ask-First Patterns (15 patterns)

Commands that require confirmation:

**File Operations** (potentially destructive):
- `rm`, `mv`, `cp` (except safe contexts like /tmp)

**Network Operations**:
- `curl`, `wget`, `nc`, `telnet`, `ssh`, `scp`, `rsync`

**System Operations**:
- `sudo` (any sudo command)
- `npm install`, `pip install`, `gem install`

**Rationale**: Safety gate for operations that modify files, access network, or require elevated privileges.

**Full list**: See `.claude/settings.local.json` "ask" array

### Never-Allow Patterns (Reference Only)

Not enforced by permissions, but documented for safety:

- `rm -rf /` - Destroy root filesystem
- `mkfs` - Format filesystems
- `dd` - Low-level disk operations
- `kill -9 1` - Kill init process
- `nmap` - Network scanning
- `:(){ :|:& };:` - Fork bomb

**Note**: These are prevented by system safeguards, not Claude Code permissions.

### Permission Behavior

**Unlisted commands**: Prompt by default (ask before execution)
**Workaround**: Add to allow list in `.claude/settings.local.json` if frequently used
```

**Step 6**: Update "Quick Tool Selection" section

Replace or update existing content (around line 180):
```markdown
## Quick Tool Selection

**🔗 Comprehensive Guide**: See [TOOL-USAGE-GUIDE.md](TOOL-USAGE-GUIDE.md) for:
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
```

**Step 7**: Update Troubleshooting section

Add new issues (around line 530):
```markdown
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
```

### Phase 3: Validation (5 minutes)

**Step 8**: Verify TOOL-USAGE-GUIDE.md link works
```bash
test -f TOOL-USAGE-GUIDE.md && echo "✓ Link target exists"
```

**Step 9**: Count section updates
```bash
grep -c "## Allowed Tools Summary" CLAUDE.md  # Should be 1
grep -c "## Command Permissions" CLAUDE.md  # Should be 1
grep -c "## Quick Tool Selection" CLAUDE.md  # Should be 1
grep -c "TOOL-USAGE-GUIDE.md" CLAUDE.md  # Should be 2-3
```

**Step 10**: Verify no broken references
```bash
# Check for references to denied tools
grep -i "filesystem_read_file" CLAUDE.md  # Should have "NOT" or "denied"
grep -i "git_git_status" CLAUDE.md  # Should have "NOT" or "denied"
```

**Step 11**: Commit changes
```bash
git add CLAUDE.md
git commit -m "Update CLAUDE.md for tool & permission lockdown

Sections updated:
- Allowed Tools Summary: 87 → 32 tools, categorized
- Command Permissions: NEW section (auto-allow, ask-first, never-allow)
- Quick Tool Selection: Link to TOOL-USAGE-GUIDE.md, updated recommendations
- Troubleshooting: 3 new issues (permission prompts, denied tools, MCP reconnect)

Key changes:
- Document 32 kept tools (Serena 11, Linear 9, Context7 2, Thinking 1, Syntropy 2)
- Document 55 denied tools with rationale
- Explain ~50 auto-allow Bash patterns
- Explain 15 ask-first patterns
- Remove outdated MCP tool recommendations

Documentation now reflects post-lockdown system state."
```

---

## Validation Gates

### L1: Syntax & Style ✓
- **Markdown syntax**: Valid (no broken links, proper formatting)
- **Headers**: Consistent hierarchy (##, ###, ####)
- **Links**: Valid relative links to TOOL-USAGE-GUIDE.md

### L2: Unit Tests ✓
- **Section exists**: "Command Permissions" added
- **Tool count**: Document shows 32 (not 87)
- **Link count**: 2-3 references to TOOL-USAGE-GUIDE.md

### L3: Integration Tests ✓
- **No functional changes**: Documentation only
- **File exists**: TOOL-USAGE-GUIDE.md present (from PRP-B)
- **Consistency**: Matches actual system state (PRP-A, PRP-D)

### L4: Pattern Conformance ✓
- **Drift**: <5% (documentation update, minimal impact)
- **Consistency**: Follows existing CLAUDE.md structure
- **Completeness**: All Stage 1 & 2 changes documented

---

## Testing Strategy

### Manual Testing (After Merge)

**Test 1: Read updated sections**
```bash
# Verify sections present
grep "## Allowed Tools Summary" CLAUDE.md
grep "## Command Permissions" CLAUDE.md
grep "## Quick Tool Selection" CLAUDE.md

# Verify content accuracy
grep "32 MCP tools" CLAUDE.md  # ✓ Should appear
grep "87 MCP tools" CLAUDE.md  # ✓ Should appear (in "Before" context)
```

**Test 2: Verify links work**
```bash
# Click link in CLAUDE.md → opens TOOL-USAGE-GUIDE.md
test -f TOOL-USAGE-GUIDE.md && echo "✓ Link target exists"
```

**Test 3: Check for broken references**
```bash
# Verify no unqualified recommendations for denied tools
grep -i "use.*filesystem_read_file" CLAUDE.md
# Expected: No results or "NOT" qualifier
```

### Automated Testing

**Section validation**:
```bash
# Count key sections
assert $(grep -c "## Allowed Tools Summary" CLAUDE.md) -eq 1
assert $(grep -c "## Command Permissions" CLAUDE.md) -eq 1
assert $(grep -c "TOOL-USAGE-GUIDE.md" CLAUDE.md) -ge 2

# Verify tool count updated
assert $(grep -c "32 MCP tools" CLAUDE.md) -ge 1
```

---

## Rollout Plan

### Pre-Rollout
1. ✅ Verify PRP-B complete (TOOL-USAGE-GUIDE.md exists)
2. ✅ Verify PRP-C complete (worktree section in CLAUDE.md)
3. ✅ Verify PRP-D complete (command permissions defined)

### Rollout Steps
1. Execute implementation steps (Phases 1-3)
2. Validate section updates and links
3. Commit changes
4. Merge to main branch
5. Read updated CLAUDE.md to verify

### Post-Rollout
1. Update session context (users may need to re-read CLAUDE.md)
2. Monitor for documentation questions
3. Add clarifications as needed

### Rollback Plan
```bash
# If issues arise
git revert <commit-hash>

# Or restore from previous version
git show HEAD~1:CLAUDE.md > CLAUDE.md
```

### Success Criteria
- ✓ "Allowed Tools Summary" shows 32 tools
- ✓ "Command Permissions" section added
- ✓ "Quick Tool Selection" links to TOOL-USAGE-GUIDE.md
- ✓ Troubleshooting has 3 new lockdown-related issues
- ✓ No broken references to denied tools
- ✓ Links to TOOL-USAGE-GUIDE.md work

---

## Notes

**Conflict Potential**: NONE
- Only modifies CLAUDE.md
- PRP-C already updated CLAUDE.md (Git Worktree section)
- No overlapping sections with other PRPs

**Dependencies**:
- Requires PRP-B (TOOL-USAGE-GUIDE.md must exist)
- References PRP-C (worktree workflow)
- References PRP-D (command permissions)

**Future Enhancements**:
- Add visual diagrams for tool selection flow
- Add comparison table (before/after lockdown)
- Add metrics section (token reduction, time savings)
