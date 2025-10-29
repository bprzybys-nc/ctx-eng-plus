---
context_sync:
  ce_updated: false
  last_sync: '2025-10-29T19:12:53.685147+00:00'
  serena_updated: false
created_date: '2025-10-27T04:00:00Z'
description: Implement Karabiner-Elements configuration to remap cmd+v to ctrl+v in
  terminal applications for seamless Claude Code image pasting workflow
execution_notes: Successfully implemented and tested. Karabiner-Elements installed,
  rule enabled, cmd+v image pasting confirmed working in Kitty terminal. Configuration
  supports Terminal, iTerm2, Kitty, Hyper, Alacritty, and Warp.
last_updated: '2025-10-27T02:54:20Z'
name: Enable cmd+v for Image Pasting in Claude Code
prp_id: PRP-30
status: executed
updated: '2025-10-29T19:12:53.685154+00:00'
updated_by: update-context-command
version: 1
---

# PRP-30: Enable cmd+v for Image Pasting in Claude Code

## Problem Statement

Claude Code requires `ctrl+v` (not `cmd+v`) to paste screenshot images from clipboard, which is non-standard on macOS and causes frequent user frustration. User reports: "i always forgot using ctrl+v"

**Root Cause**: Terminal/TUI technical limitation—terminals distinguish between:
- `cmd+v`: Paste image **files** (from Finder drag-drop)
- `ctrl+v`: Paste image **data** (screenshots from clipboard)

**Current Workaround**: Manual muscle memory training (unreliable)

**Desired State**: `cmd+v` automatically works for image pasting in Claude Code

## Solution Approach

Implement system-level keyboard remapping using Karabiner-Elements to translate `cmd+v` → `ctrl+v` exclusively in terminal applications.

### Why Karabiner-Elements?

1. **System-level integration**: Native macOS keyboard remapping
2. **App-scoped rules**: Only affects terminal apps (Terminal, iTerm2, Kitty, etc.)
3. **Toggle-able**: Can be enabled/disabled easily
4. **No Claude Code modification**: External solution, no upstream dependency

### Alternative Approaches Considered

| Approach | Pros | Cons | Verdict |
|----------|------|------|---------|
| **Karabiner-Elements** | Universal, app-scoped, toggle-able | Requires external tool | ✅ **CHOSEN** |
| Terminal-specific config | No external tools | Terminal-locked, must reconfigure per terminal | ❌ Less flexible |
| Muscle memory training | Zero config | Unreliable (user explicitly rejects) | ❌ Rejected by user |

## Implementation Plan

### Phase 1: Installation (Validation Gate 1)

**Task**: Install Karabiner-Elements via Homebrew

```bash
brew install --cask karabiner-elements
```

**Expected Output**:
```
==> Downloading Karabiner-Elements...
==> Installing Karabiner-Elements...
🍺  karabiner-elements was successfully installed!
```

**Validation**:
```bash
test -d "/Applications/Karabiner-Elements.app" && echo "✅ Installed" || echo "❌ Failed"
```

**Post-install**: macOS will prompt for Accessibility permissions—must be granted

**Verify Homebrew is functional**:
```bash
brew --version && echo "✅ Homebrew ready" || echo "❌ Homebrew not found"
```

**Troubleshooting**: If Homebrew not found, see Error Handling → Installation Failures

---

### Phase 2: Configuration File Creation (Validation Gate 2)

**Task**: Create Karabiner custom rule JSON

**File**: `~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json`

**Content**:
```json
{
  "title": "Claude Code: cmd+v → ctrl+v for Image Pasting",
  "rules": [
    {
      "description": "Remap cmd+v to ctrl+v in Terminal apps (for Claude Code image pasting)",
      "manipulators": [
        {
          "type": "basic",
          "from": {
            "key_code": "v",
            "modifiers": {
              "mandatory": ["command"]
            }
          },
          "to": [
            {
              "key_code": "v",
              "modifiers": ["control"]
            }
          ],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.apple\\.Terminal$",
                "^com\\.googlecode\\.iterm2$",
                "^co\\.zeit\\.hyper$",
                "^io\\.alacritty$",
                "^net\\.kovidgoyal\\.kitty$",
                "^dev\\.warp\\.Warp-Stable$"
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

**Bundle Identifiers Covered**:
- `com.apple.Terminal` - macOS Terminal.app
- `com.googlecode.iterm2` - iTerm2
- `co.zeit.hyper` - Hyper terminal
- `io.alacritty` - Alacritty
- `net.kovidgoyal.kitty` - Kitty terminal
- `dev.warp.Warp-Stable` - Warp terminal

**Prerequisites**:
```bash
# Create directory structure if it doesn't exist
mkdir -p ~/.config/karabiner/assets/complex_modifications

# Verify directory created
test -d ~/.config/karabiner/assets/complex_modifications && \
  echo "✅ Directory ready" || echo "❌ Directory creation failed"
```

**Validation**:
```bash
test -f ~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json && \
  jq -e '.title' ~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json > /dev/null && \
  echo "✅ JSON valid" || echo "❌ Invalid JSON"
```

---

### Phase 3: Enable Rule in Karabiner UI (Validation Gate 3)

**Task**: Activate the custom rule through Karabiner-Elements UI

**Steps**:
1. Open Karabiner-Elements preferences:
   ```bash
   open -a "Karabiner-Elements"
   ```
2. Navigate to **"Complex Modifications"** tab (top of window)
3. Click **"Add rule"** button (bottom-left of tab)
4. Scroll through available rules list to find **"Claude Code: cmd+v → ctrl+v for Image Pasting"**
5. Click **"Enable"** button next to the rule (right side of row)
6. Rule should now appear in "Enabled Rules" section at top

**Validation** (check if rule is active in karabiner.json):
```bash
# Check rule exists in active profile (handles multiple profiles)
jq '.profiles[] | select(.selected == true) | .complex_modifications.rules[]? | select(.description | contains("Claude Code"))' \
  ~/.config/karabiner/karabiner.json > /dev/null && \
  echo "✅ Rule enabled in active profile" || echo "❌ Rule not enabled"
```

**Troubleshooting**:
- If rule doesn't appear: Restart Karabiner-EventViewer
- If permissions error: Grant Accessibility permissions in System Settings

---

### Phase 4: Functional Testing (Validation Gate 4)

**Test Scenario 1: Image Paste in Claude Code**

1. Take screenshot to clipboard:
   ```bash
   # Use macOS screenshot shortcut
   cmd+shift+control+4  # Screenshot region to clipboard
   ```

2. Open Claude Code terminal session

3. Press **`cmd+v`** (not ctrl+v)

**Expected**: Image is pasted into Claude Code

**Validation**:
- ✅ Image appears in Claude Code conversation
- ✅ No error message about invalid paste
- ✅ Claude Code processes image correctly

---

**Test Scenario 2: Normal Text Paste Unaffected**

1. Copy text in browser or editor: `cmd+c`

2. Switch to Claude Code

3. Press **`cmd+v`**

**Expected**: Text is pasted normally (remapping shouldn't interfere)

**Note**: The remapping sends `ctrl+v` to Claude Code, which handles both text and image clipboard data. Text should paste correctly because Claude Code's ctrl+v implementation pastes whatever is in clipboard (text or image).

**Validation**:
- ✅ Text pastes correctly
- ✅ No double-paste or corruption

---

**Test Scenario 3: cmd+v Outside Terminals Works**

1. Copy text in terminal

2. Switch to non-terminal app (e.g., Notes, Chrome)

3. Press **`cmd+v`**

**Expected**: Normal cmd+v paste behavior (no remapping)

**Validation**:
- ✅ Text pastes normally in non-terminal apps
- ✅ Remapping is terminal-scoped only

---

**Test Scenario 4: Other Terminal Shortcuts Unaffected**

Test common terminal shortcuts still work:
- `cmd+t` (new tab)
- `cmd+w` (close tab)
- `cmd+k` (clear screen)
- `cmd+c` (copy)

**Expected**: All shortcuts function normally

**Validation**:
- ✅ No interference with other terminal shortcuts

---

## Error Handling Strategy

### Installation Failures

**Error**: `brew install` fails
**Cause**: Homebrew not installed or outdated
**Fix**:
```bash
# Install Homebrew if missing
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Update Homebrew
brew update
```

---

### Permission Denied

**Error**: "Karabiner-Elements requires Accessibility permissions"
**Cause**: macOS security settings
**Fix**:
1. Open **System Settings → Privacy & Security → Accessibility**
2. Add **Karabiner-Elements.app** to allowed list
3. Toggle permission ON
4. Restart Karabiner-Elements

---

### Rule Not Appearing

**Error**: Custom rule doesn't show in UI
**Cause**: JSON syntax error or wrong file location
**Fix**:
```bash
# Validate JSON syntax
jq . ~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json

# Check file location
ls -la ~/.config/karabiner/assets/complex_modifications/

# Restart Karabiner
killall Karabiner-Elements
open -a "Karabiner-Elements"
```

---

### Remapping Not Working

**Error**: `cmd+v` still pastes as text, not image
**Cause**: Rule not enabled or wrong bundle identifier
**Fix**:
```bash
# Check rule is active
jq '.profiles[0].complex_modifications.rules' ~/.config/karabiner/karabiner.json

# Verify terminal bundle ID
osascript -e 'id of app "Terminal"'  # Should match JSON config

# Check Karabiner event viewer for key events
open "karabiner://karabiner/assets/event_viewer"
```

---

### Multiple Profiles Issue

**Error**: Rule enabled but not working
**Cause**: Rule added to non-active Karabiner profile
**Fix**:
```bash
# Check which profile is active
jq '.profiles[] | select(.selected == true) | .name' ~/.config/karabiner/karabiner.json

# If wrong profile active, switch in Karabiner UI:
# Karabiner-Elements → Profiles tab → Select correct profile
```

**Prevention**: Always enable rule through Karabiner UI (auto-adds to active profile)

---

## Rollback Plan

If solution causes issues:

1. **Disable rule in Karabiner UI**:
   - Open Karabiner-Elements → Complex Modifications
   - Click "Remove" on Claude Code rule

2. **Uninstall Karabiner (if needed)**:
   ```bash
   brew uninstall --cask karabiner-elements
   ```

3. **Fallback to ctrl+v**: Revert to manual ctrl+v usage

---

## Documentation Updates

### Update Project CLAUDE.md (ctx-eng-plus)

**File**: `/Users/bprzybysz/nc-src/ctx-eng-plus/CLAUDE.md`

Add quick reference after completion:

```markdown
## Keyboard Shortcuts

### Image Pasting (macOS)

**cmd+v**: Paste screenshot images into Claude Code
- Requires Karabiner-Elements (auto-configured)
- Remaps cmd+v → ctrl+v in terminals only
- Toggle: Karabiner-Elements → Complex Modifications
```

### Update Global ~/.claude/CLAUDE.md

Add to Quick Reference section:

```markdown
### Claude Code Tips

**Image Pasting on macOS**: Use `cmd+v` (configured via Karabiner-Elements)
- Alternative: `ctrl+v` (native)
- Config: `~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json`
```

---

## External Dependencies

| Dependency | Purpose | Installation | Required? |
|------------|---------|--------------|-----------|
| **Homebrew** | Package manager for macOS | https://brew.sh | ✅ Yes |
| **Karabiner-Elements** | Keyboard remapping tool | `brew install --cask karabiner-elements` | ✅ Yes |
| **jq** | JSON validation/querying | `brew install jq` | ⚠️ Optional (validation only) |

---

## Success Criteria

1. ✅ Karabiner-Elements installed successfully
2. ✅ Custom rule JSON created and valid
3. ✅ Rule enabled in Karabiner UI
4. ✅ `cmd+v` pastes images in Claude Code
5. ✅ Text paste still works with `cmd+v`
6. ✅ Other terminal shortcuts unaffected
7. ✅ Remapping scoped to terminals only (no system-wide effects)
8. ✅ Documentation updated

---

## Confidence Level

**8/10** - High confidence for one-pass success

**Risks**:
- Karabiner permission prompts may require manual intervention
- Bundle identifier mismatch if using non-standard terminal
- First-time Karabiner users may need UI guidance

**Mitigation**:
- Clear step-by-step UI instructions
- Comprehensive bundle ID list (covers 5 major terminals)
- Event viewer troubleshooting path

---

## Reference Documentation

### Karabiner-Elements Official Docs
- Root structure: https://karabiner-elements.pqrs.org/docs/json/root-data-structure/
- Complex modifications: https://karabiner-elements.pqrs.org/docs/json/
- Bundle identifiers: https://karabiner-elements.pqrs.org/docs/manual/misc/bundleidentifier/

### Related Issues
- GitHub Issue #5392: https://github.com/anthropics/claude-code/issues/5392
- GitHub Issue #834: https://github.com/anthropics/claude-code/issues/834

### Project Files
- Solution doc: `CMD_V_IMAGE_PASTE_SOLUTION.md`
- Tool patterns: `.ce/examples/system/tool-usage-patterns.md`
- Shell functions: `.ce/shell-functions.sh`

---

## Post-Implementation

After successful execution:

1. Test image pasting workflow thoroughly
2. Update project and global CLAUDE.md
3. Create Linear issue for tracking (if applicable)
4. Run `/peer-review PRP-30 exe` for quality validation
5. Archive CMD_V_IMAGE_PASTE_SOLUTION.md or integrate into docs

---

## Task Checklist

- [ ] Install Karabiner-Elements via Homebrew
- [ ] Grant Accessibility permissions (macOS prompt)
- [ ] Create config directory: `~/.config/karabiner/assets/complex_modifications/`
- [ ] Write JSON rule file: `claude-code-cmd-v.json`
- [ ] Validate JSON syntax with `jq`
- [ ] Open Karabiner-Elements preferences
- [ ] Navigate to Complex Modifications tab
- [ ] Enable "Claude Code: cmd+v → ctrl+v" rule
- [ ] Test: Screenshot → Claude Code → cmd+v paste
- [ ] Verify: Text paste still works
- [ ] Verify: cmd+v works normally outside terminals
- [ ] Verify: Other terminal shortcuts unaffected
- [ ] Update project CLAUDE.md
- [ ] Update global ~/.claude/CLAUDE.md
- [ ] Run validation gates
- [ ] Create Linear issue (if tracking enabled)