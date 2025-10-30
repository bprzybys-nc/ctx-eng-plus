# /sync-with-syntropy - Sync Settings with Syntropy MCP Tool State

Updates `.claude/settings.local.json` to match Syntropy MCP's current tool enable/disable state.

## Workflow

1. **Call Syntropy MCP**:
   ```
   mcp__syntropy__list_all_tools()
   ```

   Expected response:
   ```json
   {
     "total_tools": 87,
     "enabled_tools": 45,
     "disabled_tools": 42,
     "tools": [
       {"name": "mcp__syntropy__serena_find_symbol", "description": "...", "status": "enabled"},
       {"name": "mcp__syntropy__filesystem_read_file", "description": "...", "status": "disabled"}
     ]
   }
   ```

2. **Load Settings**:
   - Read `.claude/settings.local.json`
   - If missing, create with structure: `{"allow": [], "deny": [], "ask": []}`

3. **Process Disabled Tools**:
   For each tool with `status: "disabled"`:
   - Remove from `allow` list if present
   - Remove from `deny` list if present
   - Remove from `ask` list if present

4. **Process Enabled Tools**:
   For each tool with `status: "enabled"`:
   - If NOT in `allow`, `deny`, OR `ask` lists → Add to `allow` list
   - If already in any list → No change

5. **Backup and Validate**:
   - Backup: Copy settings to `.claude/settings.local.json.backup`
   - Validate JSON syntax: Parse and re-stringify to ensure validity
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
