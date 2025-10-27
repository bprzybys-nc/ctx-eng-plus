# PRP-30 Setup Guide: Enable cmd+v for Image Pasting

**Status**: Configuration files created ✅ | Manual steps required ⚠️

---

## What's Been Done

✅ **Configuration files created**:
- `~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json`
- Supports: Terminal, iTerm2, Hyper, Alacritty, Kitty, Warp

✅ **Documentation updated**:
- `ctx-eng-plus/CLAUDE.md` - Keyboard Shortcuts section added
- `~/.claude/CLAUDE.md` - Claude Code Tips section added

---

## Manual Steps Required

### Step 1: Install Karabiner-Elements

```bash
brew install --cask karabiner-elements
```

**During installation**:
- You'll be prompted for sudo password (**required**)
- macOS will request Accessibility permissions (**must grant**)

**Verify installation**:
```bash
test -d "/Applications/Karabiner-Elements.app" && echo "✅ Installed" || echo "❌ Not installed"
```

---

### Step 2: Grant Accessibility Permissions

1. Open **System Settings** → **Privacy & Security** → **Accessibility**
2. Find **Karabiner-Elements** in the list
3. Toggle it **ON**
4. If not in list, click **"+"** and add `/Applications/Karabiner-Elements.app`

---

### Step 3: Enable the Custom Rule

1. Open Karabiner-Elements:
   ```bash
   open -a "Karabiner-Elements"
   ```

2. Navigate to **"Complex Modifications"** tab (top of window)

3. Click **"Add rule"** button (bottom-left)

4. Find **"Claude Code: cmd+v → ctrl+v for Image Pasting"** in the list

5. Click **"Enable"** button (right side of row)

6. Verify rule appears in **"Enabled Rules"** section at top

---

### Step 4: Test the Configuration

#### Test 1: Image Paste in Claude Code

1. Take screenshot: `cmd+shift+control+4`
2. Open Claude Code terminal session
3. Press **`cmd+v`** (not ctrl+v)

**Expected**: Image pastes into Claude Code

---

#### Test 2: Text Paste Still Works

1. Copy text: `cmd+c`
2. In Claude Code, press **`cmd+v`**

**Expected**: Text pastes normally

---

#### Test 3: Scoped to Terminals Only

1. Copy text in terminal
2. Switch to Notes or Chrome
3. Press **`cmd+v`**

**Expected**: Normal paste (remapping doesn't affect non-terminals)

---

## Troubleshooting

### Rule Doesn't Appear in UI

```bash
# Restart Karabiner
killall Karabiner-Elements
open -a "Karabiner-Elements"

# Verify JSON file exists
ls -la ~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json

# Validate JSON syntax
jq . ~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json
```

---

### cmd+v Still Not Working

```bash
# Check rule is enabled in active profile
jq '.profiles[] | select(.selected == true) | .complex_modifications.rules[]? | select(.description | contains("Claude Code"))' \
  ~/.config/karabiner/karabiner.json

# Verify terminal bundle ID
osascript -e 'id of app "Terminal"'

# Open event viewer to see key events
open "karabiner://karabiner/assets/event_viewer"
```

---

### Multiple Profiles Issue

```bash
# Check active profile
jq '.profiles[] | select(.selected == true) | .name' ~/.config/karabiner/karabiner.json

# Switch to correct profile in Karabiner UI if needed
```

---

## Quick Reference

**Config file location**:
```
~/.config/karabiner/assets/complex_modifications/claude-code-cmd-v.json
```

**Toggle remapping**:
- Open Karabiner-Elements → Complex Modifications
- Enable/Disable the "Claude Code" rule

**Uninstall** (if needed):
```bash
brew uninstall --cask karabiner-elements
rm -rf ~/.config/karabiner
```

---

## Success Criteria

- [  ] Karabiner-Elements installed
- [  ] Accessibility permissions granted
- [  ] Custom rule enabled in UI
- [  ] cmd+v pastes images in Claude Code
- [  ] Text paste still works normally
- [  ] Remapping scoped to terminals only

---

## Next Steps

After completing manual steps:

1. Test image pasting workflow
2. Verify no interference with other shortcuts
3. Mark PRP-30 as complete: Update YAML header `status: "executed"`

**PRP File**: `PRPs/feature-requests/PRP-30-cmd-v-image-paste.md`
