---
prp_id: PRP-D
feature_name: Command Permission Lists
status: pending
complexity: low
estimated_hours: 0.33-0.42
stage: stage-2-parallel
worktree_path: ../ctx-eng-plus-prp-d
branch_name: prp-d-command-permissions
execution_order: 1
merge_order: 4
files_modified:
  - .claude/settings.local.json
conflict_potential: MEDIUM (with PRP-A - same file, different sections)
dependencies:
  - PRP-B (needs tool usage guide for reference)
---

# PRP-D: Command Permission Lists

## TL;DR

Finalize command permission lockdown by:
1. Removing GitButler bash pattern (`Bash(but:*)`)
2. Adding comprehensive auto-allow patterns for safe commands (ls, cd, pwd, etc.)
3. Defining ask-first patterns for potentially destructive operations (rm, curl, npm install)
4. Documenting never-allow patterns (critical system operations)

**Outcome**: Predictable command permissions, no ambiguity, minimal interruptions for safe operations.

**Time**: 20-25 minutes
**Risk**: LOW (permissions easily reverted)
**Token Impact**: None (permission changes only)

---

## Context

### Current State

After Stage 1 (PRP-A), `.claude/settings.local.json` has:
- **Allow list**: 20+ patterns (git, uv, some bash commands)
- **Deny list**: 55 MCP tools
- **Ask list**: Empty (all unlisted commands prompt)
- **GitButler pattern**: `Bash(but:*)` still present (needs removal)

### Problem

1. **GitButler pattern obsolete**: `Bash(but:*)` no longer needed after PRP-C migration
2. **Incomplete auto-allow**: Missing common safe commands (ls, cd, pwd, find, tree, etc.)
3. **No ask-first gate**: Destructive operations (rm, curl) not explicitly flagged
4. **Implicit prompting**: Commands not in allow/ask lists prompt by default

### Solution

Define comprehensive permission lists:

**Auto-Allow** (~35 patterns):
- File inspection: ls, cat, head, tail, less, more
- Navigation: cd, pwd
- Search: find, grep, rg
- Git: All git operations (already present)
- Development: uv, pytest, npm test (read-only)
- System info: env, ps, whoami, hostname

**Ask-First** (~15 patterns):
- File operations: rm, mv, cp (except temp files)
- Network: curl, wget, nc
- Package management: npm install, pip install, brew install (already auto-allowed)
- System: sudo commands (always ask)

**Never-Allow** (documented, not enforced):
- Destructive system: rm -rf /, mkfs, dd
- Network attacks: nmap, metasploit
- Process manipulation: kill -9 system processes

### Benefits

1. **Clarity**: No guessing which commands are allowed
2. **Efficiency**: Safe commands never prompt
3. **Safety**: Destructive operations always ask
4. **Predictability**: Consistent behavior across sessions

---

## Implementation Steps

### Phase 1: Preparation (5 minutes)

**Step 1**: Read current permissions structure
```bash
Read(file_path=".claude/settings.local.json")
# Focus on "permissions" object (lines 2-147)
# Note existing allow, deny, ask lists
```

**Step 2**: Verify GitButler pattern exists
```bash
grep 'Bash(but:*)' .claude/settings.local.json
# Expected: Line 4 - "Bash(but:*)",
```

**Step 3**: Count current allow patterns
```bash
grep -c 'Bash(' .claude/settings.local.json
# Expected: ~20 patterns
```

### Phase 2: Modification (10 minutes)

**Step 4**: Remove GitButler pattern
```python
Edit(
  file_path=".claude/settings.local.json",
  old_string='"Bash(but:*)",\n      ',
  new_string=""
)
```

**Step 5**: Add comprehensive auto-allow patterns

Insert after existing Bash patterns (around line 22):
```json
"Bash(ls:*)",
"Bash(cd:*)",
"Bash(pwd:*)",
"Bash(find:*)",
"Bash(tree:*)",
"Bash(which:*)",
"Bash(whereis:*)",
"Bash(file:*)",
"Bash(stat:*)",
"Bash(du:*)",
"Bash(df:*)",
"Bash(whoami:*)",
"Bash(hostname:*)",
"Bash(date:*)",
"Bash(cal:*)",
"Bash(bc:*)",
"Bash(jq:*)",
"Bash(sed:*)",
"Bash(awk:*)",
"Bash(sort:*)",
"Bash(uniq:*)",
"Bash(cut:*)",
"Bash(paste:*)",
"Bash(tr:*)",
"Bash(diff:*)",
"Bash(comm:*)",
"Bash(cmp:*)",
"Bash(md5:*)",
"Bash(sha256sum:*)",
"Bash(base64:*)",
"Bash(xxd:*)",
"Bash(strings:*)",
"Bash(hexdump:*)"
```

**Step 6**: Add ask-first patterns

Add new "ask" array after "deny" array (around line 142):
```json
"ask": [
  "Bash(rm:*)",
  "Bash(rm *)",
  "Bash(mv:*)",
  "Bash(cp:*)",
  "Bash(curl:*)",
  "Bash(wget:*)",
  "Bash(nc:*)",
  "Bash(telnet:*)",
  "Bash(ssh:*)",
  "Bash(scp:*)",
  "Bash(rsync:*)",
  "Bash(sudo:*)",
  "Bash(npm install:*)",
  "Bash(pip install:*)",
  "Bash(gem install:*)"
]
```

**Step 7**: Add never-allow documentation comment

Add comment before "ask" array:
```json
// Never-allow patterns (not enforced, for reference):
// - Bash(rm -rf /:*) - Destroy root filesystem
// - Bash(mkfs:*) - Format filesystems
// - Bash(dd:*) - Low-level disk operations
// - Bash(kill -9 1:*) - Kill init process
// - Bash(nmap:*) - Network scanning
// - Bash(:(){ :|:& };:) - Fork bomb
```

### Phase 3: Validation (5 minutes)

**Step 8**: Validate JSON syntax
```bash
python3 -m json.tool .claude/settings.local.json > /dev/null && echo "✓ Valid JSON"
```

**Step 9**: Verify pattern counts
```bash
grep -c 'Bash(' .claude/settings.local.json
# Expected: ~50 patterns (20 existing + 30 new)

grep -c '"ask":' .claude/settings.local.json
# Expected: 1
```

**Step 10**: Verify GitButler pattern removed
```bash
grep 'Bash(but:*)' .claude/settings.local.json
# Expected: No output (pattern removed)
```

**Step 11**: Commit changes
```bash
git add .claude/settings.local.json
git commit -m "Add comprehensive command permission lists

- Remove GitButler pattern (Bash(but:*))
- Add 30+ auto-allow patterns (ls, cd, pwd, find, etc.)
- Add 15 ask-first patterns (rm, curl, sudo, etc.)
- Document never-allow patterns (reference only)

Total: ~50 Bash patterns in allow list
Ask-first: 15 patterns for safety gate
Never-allow: 6 documented (not enforced)

No more ambiguity on command permissions."
```

---

## Validation Gates

### L1: Syntax & Style ✓
- **JSON syntax**: Valid (python3 -m json.tool)
- **Format**: Consistent indentation, trailing commas
- **Comments**: Well-placed, informative

### L2: Unit Tests ✓
- **Pattern count**: ~50 Bash patterns in allow
- **GitButler removed**: `grep 'but:' → no results`
- **Ask list exists**: `grep '"ask":' → 1 result`

### L3: Integration Tests ✓
- **Restart required**: No (permission changes apply immediately)
- **Existing sessions**: May need command re-check on first use
- **No data loss**: Permissions only, no file changes

### L4: Pattern Conformance ✓
- **Drift**: <5% (minimal change, permission tweaks only)
- **Consistency**: Follows existing permission structure
- **Documentation**: Comments explain never-allow patterns

---

## Testing Strategy

### Manual Testing (After Merge)

**Test 1: Auto-allow commands (no prompts)**
```bash
ls -la
cd /tmp
pwd
find . -name "*.py"
tree -L 2
cat README.md
grep "TODO" **/*.py
date
whoami
```
**Expected**: All execute without permission prompts

**Test 2: Ask-first commands (prompts appear)**
```bash
rm /tmp/test.txt  # Should prompt
curl https://example.com  # Should prompt
sudo echo "test"  # Should prompt
```
**Expected**: Permission prompt before execution

**Test 3: GitButler command fails**
```bash
but status  # Should fail (command not found or permission denied)
```
**Expected**: Error (GitButler pattern removed)

### Automated Testing

**Pattern validation**:
```bash
# Count patterns
assert $(grep -c 'Bash(' .claude/settings.local.json) -ge 50

# Verify ask list
assert $(grep -c '"ask":' .claude/settings.local.json) -eq 1

# Verify GitButler removed
assert $(grep -c 'but:' .claude/settings.local.json) -eq 0
```

---

## Rollout Plan

### Pre-Rollout
1. ✅ Review TOOL-USAGE-GUIDE.md (PRP-B) for command recommendations
2. ✅ Verify git worktree workflow (PRP-C) doesn't require GitButler
3. ✅ Confirm current permissions structure

### Rollout Steps
1. Execute implementation steps (Phases 1-3)
2. Validate JSON syntax and pattern counts
3. Commit changes
4. Merge to main branch
5. Test commands (auto-allow, ask-first)

### Post-Rollout
1. Document in CLAUDE.md (PRP-E will update)
2. Monitor for unexpected prompts
3. Adjust ask-first list if too aggressive
4. Add patterns as needed

### Rollback Plan
```bash
# If issues arise
git revert <commit-hash>

# Or restore specific section
git show HEAD~1:.claude/settings.local.json > .claude/settings.local.json
```

### Success Criteria
- ✓ GitButler pattern removed
- ✓ ~50 Bash patterns in allow list
- ✓ Ask-first list defined (15 patterns)
- ✓ JSON valid
- ✓ Safe commands execute without prompts
- ✓ Destructive commands prompt before execution

---

## Notes

**Conflict Potential**: MEDIUM
- Both PRP-A and PRP-D modify `.claude/settings.local.json`
- PRP-A: Modifies "deny" array
- PRP-D: Modifies "allow" and "ask" arrays
- Conflict unlikely (different sections)
- If conflict: Keep both changes, merge arrays

**Dependencies**:
- Requires PRP-B (TOOL-USAGE-GUIDE.md) for reference
- No dependency on PRP-C execution (but logically follows worktree migration)

**Future Enhancements**:
- Add pattern for safe file operations in /tmp
- Add pattern for specific npm scripts (npm test, npm run build)
- Consider environment-specific patterns (dev vs prod)
