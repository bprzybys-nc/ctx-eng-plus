---
prp_id: PRP-A
feature_name: Tool Deny List Implementation
status: executed
created: 2025-10-29T00:00:00Z
updated: 2025-10-30T00:00:00Z
executed: 2025-10-29T00:00:00Z
execution_commit: b53e184
complexity: low
estimated_hours: 0.25-0.33
dependencies: none
stage: stage-1-parallel
worktree_path: ../ctx-eng-plus-prp-a
branch_name: prp-a-tool-deny-list
execution_order: 1
merge_order: 1
files_modified: .claude/settings.local.json
conflict_potential: MEDIUM (with PRP-D - same file, different sections)
---

# Tool Deny List Implementation

## 1. TL;DR

**Objective**: Reduce MCP tools context from ~46k to ~2k tokens by denying 55 redundant tools

**What**: Add 55 MCP tools to deny list, clean up duplicate deny arrays, verify 32 essential tools remain accessible

**Why**: Token efficiency (96% reduction), native-first philosophy, clearer tool selection

**Effort**: 15-20 minutes

**Dependencies**: None (stage-1-parallel, independent execution)

---

## 2. Context

### Background
- Current: 87 MCP tools consuming ~46k tokens
- Many tools redundant with native Claude Code tools (Read, Write, Edit, Glob, Grep, Bash)
- Native tools are more direct, faster, and better documented

### Parallel Execution Context
- **Stage**: stage-1-parallel (can run with PRP-B, PRP-C)
- **Worktree**: `../ctx-eng-plus-prp-a`
- **Branch**: `prp-a-tool-deny-list`
- **Files**: `.claude/settings.local.json` (permissions.deny section only)
- **Conflicts**: MEDIUM with PRP-D (both edit settings, different sections)

### Constraints and Considerations
- Must preserve 32 essential tools (Serena, Linear, Context7, thinking, Syntropy healthcheck/knowledge_search)
- Settings file has duplicate deny arrays (lines 120, 142) - must clean
- Must maintain valid JSON syntax
- Reversible with zero data loss

### Documentation References
- Source: TOOL-PERMISSION-LOCKDOWN-PLAN.md Section 2
- Native tools: Read, Write, Edit, Glob, Grep, Bash
- MCP reconnect required after changes: `/mcp`

---

## 3. Implementation Steps

### Phase 1: Preparation (5 min)

**Step 1**: Backup current settings
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
git stash push -m "Pre PRP-A backup" -- .claude/settings.local.json
```

**Step 2**: Read current settings structure
```bash
# Use Read tool to examine current deny list
Read .claude/settings.local.json
# Note: Duplicate deny arrays at lines 120-141, 142
```

**Step 3**: Record baseline metrics
```bash
# Run doctor to capture current token count
/doctor
# Note "MCP tools context" value (expected: ~46k tokens)
```

### Phase 2: Settings Modification (8 min)

**Step 4**: Remove duplicate deny array
- Line 142: `"deny": []` - DELETE this line
- Keep only first deny array (lines 120-141)

**Step 5**: Add 55 tools to deny list

Add to `permissions.deny` array (alphabetical by category):

**Filesystem (8)**:
```json
"mcp__syntropy__filesystem_read_file",
"mcp__syntropy__filesystem_read_text_file",
"mcp__syntropy__filesystem_write_file",
"mcp__syntropy__filesystem_edit_file",
"mcp__syntropy__filesystem_list_directory",
"mcp__syntropy__filesystem_search_files",
"mcp__syntropy__filesystem_directory_tree",
"mcp__syntropy__filesystem_get_file_info",
```

**Git (5)**:
```json
"mcp__syntropy__git_git_status",
"mcp__syntropy__git_git_diff",
"mcp__syntropy__git_git_log",
"mcp__syntropy__git_git_add",
"mcp__syntropy__git_git_commit",
```

**GitHub (26)**:
```json
"mcp__syntropy__github_create_or_update_file",
"mcp__syntropy__github_search_repositories",
"mcp__syntropy__github_create_repository",
"mcp__syntropy__github_get_file_contents",
"mcp__syntropy__github_push_files",
"mcp__syntropy__github_create_issue",
"mcp__syntropy__github_create_pull_request",
"mcp__syntropy__github_fork_repository",
"mcp__syntropy__github_create_branch",
"mcp__syntropy__github_list_commits",
"mcp__syntropy__github_list_issues",
"mcp__syntropy__github_update_issue",
"mcp__syntropy__github_add_issue_comment",
"mcp__syntropy__github_search_code",
"mcp__syntropy__github_search_issues",
"mcp__syntropy__github_search_users",
"mcp__syntropy__github_get_issue",
"mcp__syntropy__github_get_pull_request",
"mcp__syntropy__github_list_pull_requests",
"mcp__syntropy__github_create_pull_request_review",
"mcp__syntropy__github_merge_pull_request",
"mcp__syntropy__github_get_pull_request_files",
"mcp__syntropy__github_get_pull_request_status",
"mcp__syntropy__github_update_pull_request_branch",
"mcp__syntropy__github_get_pull_request_comments",
"mcp__syntropy__github_get_pull_request_reviews",
```

**Repomix (4)**:
```json
"mcp__syntropy__repomix_pack_codebase",
"mcp__syntropy__repomix_grep_repomix_output",
"mcp__syntropy__repomix_read_repomix_output",
"mcp__syntropy__repomix_pack_remote_repository",
```

**Playwright (6)**:
```json
"mcp__syntropy__playwright_navigate",
"mcp__syntropy__playwright_screenshot",
"mcp__syntropy__playwright_click",
"mcp__syntropy__playwright_fill",
"mcp__syntropy__playwright_evaluate",
"mcp__syntropy__playwright_get_visible_text",
```

**Perplexity (1)**:
```json
"mcp__syntropy__perplexity_perplexity_ask",
```

**Syntropy (5)**:
```json
"mcp__syntropy__init_project",
"mcp__syntropy__get_system_doc",
"mcp__syntropy__get_user_doc",
"mcp__syntropy__get_summary",
"mcp__syntropy__denoise",
```

**Step 6**: Verify kept tools in allow list

Ensure these remain in `permissions.allow`:
- Serena tools (11): All `mcp__syntropy__serena_*`
- Linear tools (9): `linear_create_issue`, `linear_get_issue`, `linear_list_issues`, `linear_update_issue`, `linear_list_projects`, `linear_list_teams`, `linear_list_users`, `linear_get_team`, `linear_create_project`
- Context7 (2): `context7_resolve_library_id`, `context7_get_library_docs`
- Thinking (1): `mcp__syntropy__thinking_sequentialthinking`
- Syntropy (2): `mcp__syntropy__healthcheck`, `mcp__syntropy__knowledge_search`

### Phase 3: Validation (5 min)

**Step 7**: Validate JSON syntax
```bash
python3 -m json.tool .claude/settings.local.json > /dev/null && echo "✓ Valid JSON"
```

**Step 8**: Check for duplicates
```bash
grep -n '"deny"' .claude/settings.local.json
# Should show only 1 line (inside permissions object)
```

**Step 9**: Reconnect MCP
```bash
/mcp
# Should succeed, may show "Reconnected to syntropy"
```

**Step 10**: Verify doctor output
```bash
/doctor
# Check:
# - No plugin errors
# - All servers connected
# - MCP tools context: ~2k tokens (was ~46k)
```

**Step 11**: Test tool access
- Try denied tool: Should not appear in tool list
- Try allowed tool: `serena_find_symbol` should work
- Try native tool: Read, Write, Edit should work

---

## 4. Validation Gates

### Gate 1: Settings File Valid
**Command**: `python3 -m json.tool .claude/settings.local.json > /dev/null && echo "PASS" || echo "FAIL"`
**Expected**: PASS
**On Failure**: Fix JSON syntax errors, verify no trailing commas

### Gate 2: No Duplicate Deny Arrays
**Command**: `grep -c '"deny"' .claude/settings.local.json`
**Expected**: 1 (only one deny array)
**On Failure**: Remove duplicate entries

### Gate 3: MCP Reconnect Success
**Command**: `/mcp`
**Expected**: "Reconnected to syntropy" or similar success message
**On Failure**: Check JSON syntax, rollback if needed

### Gate 4: Doctor Clean
**Command**: `/doctor`
**Expected**:
- No plugin errors
- All servers connected (9 servers)
- MCP tools context reduced to ~2k tokens
**On Failure**: Check server connectivity, verify tool list

### Gate 5: Essential Tools Accessible
**Command**: Manual verification
- Try `serena_find_symbol` (should appear in tool list)
- Try `linear_list_issues` (should appear in tool list)
**Expected**: All 32 kept tools accessible
**On Failure**: Check allow list, ensure tools not accidentally denied

---

## 5. Testing Strategy

### Test Framework
Manual testing + bash validation

### Test Command
```bash
# Validate JSON
python3 -m json.tool .claude/settings.local.json

# Check duplicates
grep -c '"deny"' .claude/settings.local.json

# Reconnect MCP
/mcp

# Check doctor
/doctor
```

### Unit Tests
1. **JSON Validation**: File parses without errors
2. **Duplicate Check**: Only one deny array exists
3. **Count Check**: 55 new tools added to deny list

### Integration Tests
1. **MCP Reconnect**: `/mcp` succeeds
2. **Server Health**: `/doctor` shows all servers connected
3. **Token Reduction**: MCP tools context ~2k (was ~46k)

### Functional Tests
1. **Denied Tools**: Filesystem, Git, GitHub tools not available
2. **Allowed Tools**: Serena, Linear, Context7 tools available
3. **Native Tools**: Read, Write, Edit, Glob, Grep work

---

## 6. Rollout Plan

### Phase 1: Development
- Create worktree: `git worktree add ../ctx-eng-plus-prp-a -b prp-a-tool-deny-list`
- Execute steps 1-11 in worktree
- Validate all gates pass
- Commit: `git commit -m "Add 55 MCP tools to deny list, clean duplicates"`

### Phase 2: Review
- Push branch: `git push -u origin prp-a-tool-deny-list`
- Create PR: `gh pr create --title "PRP-A: Tool Deny List" --base main`
- Self-review validation gates
- Merge when ready

### Phase 3: Integration
- Merge order: 1 (merge first in Stage 1)
- Handle conflicts: If PRP-D merged first, resolve settings.local.json merge
- Verify: `/mcp && /doctor` after merge

### Rollback Strategy
```bash
# If issues occur
git revert HEAD
/mcp

# Or restore from stash
git stash pop
/mcp
```

---

## Research Findings

### Rationale by Category

**Filesystem Tools (8)**: Native Read/Write/Edit/Glob tools are more direct, faster, and token-efficient. The Edit tool's old_string/new_string approach is more precise than filesystem_edit_file.

**Git Tools (5)**: Native bash `git` commands are more flexible (support all flags), already approved in permissions, and universally familiar. Example: `git diff` vs limited `git_git_diff` wrapper.

**GitHub Tools (26)**: Native `gh` CLI is official GitHub tool, more comprehensive, better documented, and supports all GitHub features. Example: `gh pr create` vs `github_create_pull_request`.

**Repomix Tools (4)**: Native incremental exploration (Glob for patterns, Grep for content, Read for files) is more efficient than packing entire codebase. Repomix creates monolithic output unsuitable for incremental work.

**Playwright Tools (6)**: Specialized browser automation rarely needed for CLI tooling projects. WebFetch handles most web content needs. If required, can use bash + playwright CLI directly.

**Perplexity Tools (1)**: Native WebSearch provides equivalent AI-powered search capability without third-party API dependency.

**Syntropy System Tools (5)**: Mostly redundant (get_system_doc/get_user_doc → use Read) or rarely used (init_project one-time, denoise specialized). Keeping only healthcheck and knowledge_search which provide unique value.

### Settings Cleanup Notes

Current `.claude/settings.local.json` issues:
- **Line 120-141**: First deny array (16 items, mostly Serena thinking tools + filesystem/git tools)
- **Line 142**: Duplicate empty `"deny": []` array
- **Solution**: Remove line 142, consolidate all denials in first array

---

**Completion Criteria**:
- [ ] 55 tools added to deny list
- [ ] Duplicate deny arrays removed
- [ ] JSON syntax valid
- [ ] MCP reconnect successful
- [ ] Token count ~2k (was ~46k)
- [ ] All 32 essential tools accessible
