---
prp_id: 30.2.1
feature_name: Slash Command - Sync with Syntropy Tool State
status: pending
created: 2025-10-30T13:15:00Z
updated: 2025-10-30T13:15:00Z
complexity: low
estimated_hours: 1.5
dependencies: PRP-30.1.1
batch_id: 30
stage: 2
execution_order: 2
merge_order: 2
issue: BLA-47
---

# Slash Command - Sync with Syntropy Tool State

## 1. TL;DR

**Objective**: Create `/sync-with-syntropy` slash command to sync Claude Code settings with Syntropy MCP's dynamic tool state

**What**: Slash command that:
- Calls `mcp__syntropy__list_all_tools` to get tool states
- Removes disabled tools from all permission lists in `.claude/settings.local.json`
- Adds enabled tools to allow list
- Validates JSON and outputs change summary

**Why**: Allows users to dynamically control tool availability via Syntropy MCP without manually editing settings files

**Effort**: 1.5 hours

**Dependencies**: PRP-30.1.1 (Syntropy MCP must have `list_all_tools` command)

---

## 2. Context

### Background

After PRP-30.1.1 implements dynamic tool management in Syntropy MCP, users can enable/disable tools at runtime using `mcp__syntropy__enable_tools`. However, these changes don't automatically reflect in Claude Code's `.claude/settings.local.json` permission lists.

This PRP adds a `/sync-with-syntropy` command that bridges this gap by:
1. Reading tool state from Syntropy MCP
2. Updating Claude Code settings to match
3. Providing clear feedback on changes made

### Constraints and Considerations

**File Format**:
- `.claude/settings.local.json` contains three permission lists: `allow`, `deny`, `ask`
- Tool format: `mcp__syntropy__{server}_{tool}` (double underscore after syntropy, single after server)
- Must preserve other settings (hooks, etc.)

**Error Scenarios**:
- Syntropy MCP not connected → clear error message
- Invalid JSON after update → abort with validation error
- Empty tool list → no-op (skip updates)

**Edge Cases**:
- Tools in multiple lists → remove from all
- Tools already in correct list → no change needed
- Settings file missing → create with default structure

### Documentation References

**Slash Command Structure**:
- Location: `.claude/commands/sync-with-syntropy.md`
- Format: Markdown instructions for Claude Code interpreter
- Similar: `.claude/commands/peer-review.md`

**Settings Update Pattern**:
- Reference: `tools/ce/core.py:120-145`
- Pattern: Read → Update → Validate → Write

**MCP Tool Call**:
```python
tools_list = mcp__syntropy__list_all_tools()
# Returns: [{"name": "...", "server": "...", "status": "enabled|disabled"}, ...]
```

---

## 3. Implementation Steps

### Phase 1: Create Slash Command File (30 min)

**File**: `.claude/commands/sync-with-syntropy.md`

**Content**:

````markdown
# /sync-with-syntropy - Sync Settings with Syntropy MCP Tool State

Updates `.claude/settings.local.json` to match Syntropy MCP's current tool enable/disable state.

## Workflow

1. **Call Syntropy MCP**:
   ```
   mcp__syntropy__list_all_tools
   ```

   Expected response:
   ```json
   [
     {"name": "serena_find_symbol", "description": "...", "server": "serena", "status": "enabled"},
     {"name": "filesystem_read_file", "description": "...", "server": "filesystem", "status": "disabled"}
   ]
   ```

2. **Load Settings**:
   - Read `.claude/settings.local.json`
   - If missing, create with structure: `{"allow": [], "deny": [], "ask": []}`

3. **Process Disabled Tools**:
   For each tool with `status: "disabled"`:
   - Tool name format: `mcp__syntropy__{server}_{tool}`
   - Remove from `allow` list if present
   - Remove from `deny` list if present
   - Remove from `ask` list if present

4. **Process Enabled Tools**:
   For each tool with `status: "enabled"`:
   - Tool name format: `mcp__syntropy__{server}_{tool}`
   - If NOT in `allow`, `deny`, OR `ask` lists → Add to `allow` list
   - If already in any list → No change

5. **Backup and Validate**:
   - Backup: Copy settings to `.claude/settings.local.json.backup`
   - Validate JSON syntax: `json.dumps(settings)`
   - If validation fails → Abort, restore backup, show error

6. **Write Settings**:
   - Write updated settings with `indent=2`
   - Preserve all other settings (hooks, etc.)

7. **Output Summary**:
   ```
   ✓ Synced settings with Syntropy MCP tool state

   Removed 2 disabled tools:
     - mcp__syntropy__filesystem_read_file
     - mcp__syntropy__git_git_status

   Added 1 enabled tool to allow list:
     - mcp__syntropy__serena_find_symbol

   No changes: 45 tools already correct
   ```

## Error Handling

**Syntropy MCP Not Connected**:
```
❌ Error: Syntropy MCP not connected

   Please ensure Syntropy MCP server is running:
   - Check MCP status with /mcp
   - Restart MCP if needed
```

**Invalid JSON**:
```
❌ Error: Settings file invalid after update

   Validation error: {error details}

   Settings restored from backup.
   🔧 Check .claude/settings.local.json.backup for last good state
```

**Empty Tool List**:
```
⚠ No tools returned from Syntropy MCP

  Skipping settings update (nothing to sync)
```
````

### Phase 2: Update Documentation (15 min)

**File**: `CLAUDE.md`

**Add to "Quick Commands" section**:

```markdown
## Syntropy MCP Tool Sync

```bash
# Sync settings with Syntropy MCP tool state
/sync-with-syntropy

# Workflow example:
# 1. Enable/disable tools via Syntropy
mcp__syntropy__enable_tools(
  enable=["serena_find_symbol", "context7_get_library_docs"],
  disable=["filesystem_read_file", "git_git_status"]
)

# 2. Sync settings
/sync-with-syntropy

# 3. Verify changes
cat .claude/settings.local.json
```
```

### Phase 3: Testing and Validation (45 min)

**Test Cases**:

1. **Test with Syntropy MCP connected**:
   - Enable 2 tools via `enable_tools`
   - Disable 2 tools via `enable_tools`
   - Run `/sync-with-syntropy`
   - Verify settings updated correctly

2. **Test with Syntropy MCP disconnected**:
   - Stop Syntropy MCP
   - Run `/sync-with-syntropy`
   - Verify clear error message

3. **Test with no changes needed**:
   - Settings already match tool state
   - Run `/sync-with-syntropy`
   - Verify "No changes" message

4. **Test with tools in multiple lists**:
   - Manually add tool to both allow and deny lists
   - Disable tool via Syntropy
   - Run `/sync-with-syntropy`
   - Verify tool removed from both lists

5. **Test backup and restore**:
   - Verify `.claude/settings.local.json.backup` created
   - Simulate validation error
   - Verify settings restored from backup

---

## 4. Validation Gates

### Gate 1: Command Successfully Calls list_all_tools

**Command**:
```bash
# In Claude Code:
/sync-with-syntropy
```

**Expected**:
- Command calls `mcp__syntropy__list_all_tools`
- Returns list of tools with status
- No errors if Syntropy MCP connected

**Failure Modes**:
- Syntropy MCP not connected → Clear error message
- `list_all_tools` command missing → Error (requires PRP-30.1.1)

---

### Gate 2: Disabled Tools Removed from All Lists

**Setup**:
```bash
# Add tool to multiple lists manually
# Edit .claude/settings.local.json:
{
  "allow": ["mcp__syntropy__filesystem_read_file", ...],
  "deny": ["mcp__syntropy__filesystem_read_file", ...]
}

# Disable tool via Syntropy MCP
mcp__syntropy__enable_tools(disable=["filesystem_read_file"])
```

**Command**:
```bash
/sync-with-syntropy
```

**Expected**:
- Tool removed from both `allow` and `deny` lists
- Summary shows: "Removed 1 disabled tool (from 2 lists)"

---

### Gate 3: Enabled Tools Added to Allow List

**Setup**:
```bash
# Enable tool via Syntropy MCP
mcp__syntropy__enable_tools(enable=["serena_find_symbol"])

# Ensure tool not in any list
# Edit .claude/settings.local.json: remove serena_find_symbol from all lists
```

**Command**:
```bash
/sync-with-syntropy
```

**Expected**:
- Tool added to `allow` list
- Format: `mcp__syntropy__serena_find_symbol`
- Summary shows: "Added 1 enabled tool to allow list"

---

### Gate 4: Settings File Valid JSON After Update

**Command**:
```bash
# After running /sync-with-syntropy
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
python3 -c "import json; json.load(open('.claude/settings.local.json')); print('✓ Valid JSON')"
```

**Expected**:
```
✓ Valid JSON
```

**Failure Modes**:
- Invalid JSON → Command aborts before writing
- Settings restored from backup

---

### Gate 5: Command Outputs Clear Summary

**Command**:
```bash
/sync-with-syntropy
```

**Expected Output Format**:
```
✓ Synced settings with Syntropy MCP tool state

Removed X disabled tools:
  - tool1
  - tool2

Added Y enabled tools to allow list:
  - tool3

No changes: Z tools already correct
```

**Requirements**:
- Shows counts for each category
- Lists specific tools changed
- Clear success indicator

---

### Gate 6: End-to-End Workflow Test

**Test Scenario**:
```bash
# Step 1: Configure tools via Syntropy MCP
mcp__syntropy__enable_tools(
  enable=["serena_find_symbol", "context7_get_library_docs"],
  disable=["filesystem_read_file", "git_git_status"]
)

# Step 2: Sync settings
/sync-with-syntropy

# Step 3: Verify changes
cat .claude/settings.local.json | grep serena_find_symbol
# Expected: In allow list

cat .claude/settings.local.json | grep filesystem_read_file
# Expected: NOT in any list

# Step 4: Verify backup created
ls -la .claude/settings.local.json.backup
# Expected: Backup file exists with recent timestamp
```

**Success Criteria**:
- All 4 tools updated correctly
- Backup file created
- Settings remain valid JSON
- Other settings preserved (hooks, etc.)

---

## 5. Testing Strategy

### Test Framework

**Manual Testing** (no automated tests for slash commands)

Slash commands are Claude Code interpreter instructions, not executable code. Testing requires manual execution in Claude Code environment.

### Test Command

```bash
# Test in Claude Code terminal:
/sync-with-syntropy
```

### Test Coverage

**Functional Tests**:
1. **Happy Path**: Tools enabled/disabled → sync → settings updated
2. **Error Handling**: Syntropy MCP disconnected → clear error
3. **Edge Cases**: Empty tool list, duplicate tools, no changes needed
4. **Validation**: JSON validation, backup creation, restore on error

**Integration Tests**:
1. **With PRP-30.1.1**: Syntropy MCP `list_all_tools` integration
2. **Settings File**: Read/write/validate `.claude/settings.local.json`
3. **Tool Naming**: Format `mcp__syntropy__{server}_{tool}` correct

### Test Data

**Sample Syntropy MCP Response**:
```json
[
  {"name": "serena_find_symbol", "description": "Find symbol in codebase", "server": "serena", "status": "enabled"},
  {"name": "serena_read_file", "description": "Read file contents", "server": "serena", "status": "enabled"},
  {"name": "filesystem_read_file", "description": "Read file (deprecated)", "server": "filesystem", "status": "disabled"},
  {"name": "git_git_status", "description": "Git status (deprecated)", "server": "git", "status": "disabled"}
]
```

**Expected Settings After Sync**:
```json
{
  "allow": [
    "mcp__syntropy__serena_find_symbol",
    "mcp__syntropy__serena_read_file"
  ],
  "deny": [],
  "ask": []
}
```

---

## 6. Rollout Plan

### Phase 1: Implementation (45 min)

**Actions**:
1. Create `.claude/commands/sync-with-syntropy.md`
2. Update `CLAUDE.md` with command documentation
3. Commit changes

**Validation**:
- Files created in correct locations
- Command appears in `/help` output

---

### Phase 2: Manual Testing (30 min)

**Actions**:
1. Test with Syntropy MCP connected
2. Test error scenarios (MCP disconnected)
3. Test edge cases (empty list, duplicates)
4. Verify backup creation and restore

**Validation**:
- All 6 validation gates pass
- No errors in normal usage
- Clear error messages for failure cases

---

### Phase 3: Documentation and Handoff (15 min)

**Actions**:
1. Add usage example to `CLAUDE.md`
2. Create quick reference in `tmp/PRP-30-SETUP-GUIDE.md` (if exists)
3. Mark PRP as executed

**Validation**:
- Documentation complete
- Command ready for production use

---

## 7. Success Criteria

- [ ] `.claude/commands/sync-with-syntropy.md` created with full workflow
- [ ] Command successfully calls `mcp__syntropy__list_all_tools`
- [ ] Disabled tools removed from all permission lists
- [ ] Enabled tools added to allow list (if not present)
- [ ] Settings file validated before writing
- [ ] Backup created before modification
- [ ] Clear summary output with counts and tool names
- [ ] Error handling for MCP disconnected, invalid JSON
- [ ] Documentation added to `CLAUDE.md`
- [ ] All 6 validation gates pass
- [ ] End-to-end workflow tested: enable → sync → verify

---

## 8. Rollback Plan

**If Issues Arise**:

1. **Settings Corrupted**:
   - Restore from `.claude/settings.local.json.backup`
   - Command already handles this automatically

2. **Command Not Working**:
   - Remove `.claude/commands/sync-with-syntropy.md`
   - Revert `CLAUDE.md` changes
   - Users can manually edit settings as before

3. **Syntropy MCP Incompatibility**:
   - Verify PRP-30.1.1 executed successfully
   - Check `mcp__syntropy__list_all_tools` command exists
   - Fallback: Skip command, manually edit settings

**Rollback Command**:
```bash
# Remove slash command
rm .claude/commands/sync-with-syntropy.md

# Restore settings from backup (if needed)
cp .claude/settings.local.json.backup .claude/settings.local.json

# Revert CLAUDE.md changes
git checkout CLAUDE.md
```

---

## Dependencies

**Hard Dependencies**:
- **PRP-30.1.1**: Syntropy MCP must have `list_all_tools` command
- **Syntropy MCP Running**: MCP server must be connected

**Soft Dependencies**:
- None (command degrades gracefully if MCP disconnected)

---

## Related PRPs

- **PRP-30.1.1**: Syntropy MCP - Tool Management Commands (prerequisite)
- Future: Automatic sync on MCP tool state change (webhook-based)
