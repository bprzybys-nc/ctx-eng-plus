# Making cmd+v Work for Image Pasting in Claude Code

**Problem**: Claude Code requires ctrl+v (not cmd+v) to paste screenshots from clipboard, which is non-standard on macOS.

**Root Cause**: Terminal/TUI limitation—terminals distinguish between:
- `cmd+v`: Paste image **files** (from Finder)
- `ctrl+v`: Paste image **data** (screenshots from clipboard)

**Claude Code Status**: No built-in configuration to change this behavior.

---

## Solution Options

### Option 1: Karabiner-Elements (Recommended)
**System-level keyboard remapping - affects all terminal apps**

#### Installation
```bash
brew install --cask karabiner-elements
```

#### Configuration
1. Open Karabiner-Elements preferences
2. Go to "Complex Modifications" tab
3. Click "Add rule"
4. Create custom rule with JSON:

**Location**: `~/.config/karabiner/karabiner.json`

Add this to the `rules` array inside `complex_modifications`:

```json
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
            "^net\\.kovidgoyal\\.kitty$"
          ]
        }
      ]
    }
  ]
}
```

**Bundle identifiers covered**:
- `com.apple.Terminal` - Terminal.app
- `com.googlecode.iterm2` - iTerm2
- `co.zeit.hyper` - Hyper
- `io.alacritty` - Alacritty
- `net.kovidgoyal.kitty` - Kitty

#### Pros
✅ Works universally in all terminal apps
✅ Native macOS integration
✅ Can be toggled on/off easily
✅ Doesn't affect non-terminal apps

#### Cons
❌ Requires external tool installation
❌ Affects ALL cmd+v usage in terminals (not just image pasting)
❌ May interfere with other terminal workflows

---

### Option 2: Terminal-Specific Key Mapping

#### Kitty Terminal
**Location**: `~/.config/kitty/kitty.conf`

```conf
# Map cmd+v to ctrl+v for image pasting
map cmd+v send_text all \x16
```

#### iTerm2
1. Preferences → Keys → Key Bindings
2. Click "+" to add new mapping
3. Keyboard Shortcut: `cmd+v`
4. Action: "Send Text"
5. Text: `^V` (literal ctrl+v)

#### Pros
✅ No external tools needed
✅ Terminal-specific (doesn't affect other apps)
✅ Can be customized per terminal

#### Cons
❌ Only works in specific terminal
❌ Need to reconfigure if switching terminals
❌ May conflict with terminal's built-in paste

---

### Option 3: Muscle Memory Training (No Config)
**Just use ctrl+v**

#### Workflow
1. `cmd+shift+4` - Take screenshot (to clipboard)
2. Switch to Claude Code
3. **ctrl+v** - Paste image

#### Pros
✅ No installation or configuration
✅ Works everywhere, always
✅ No side effects

#### Cons
❌ Need to remember ctrl+v (not cmd+v)
❌ Breaks macOS muscle memory

---

## Recommendation

**For you specifically**: Since you "always forget to use ctrl+v", I recommend **Option 1 (Karabiner-Elements)**.

### Quick Install
```bash
# Install Karabiner-Elements
brew install --cask karabiner-elements

# Wait for installation, then grant permissions when prompted
```

After installation, I can help you:
1. Add the JSON rule to your Karabiner config
2. Test cmd+v works for image pasting in Claude Code
3. Verify normal text paste still works with cmd+v outside terminals

---

## Testing After Setup

1. Take screenshot: `cmd+shift+control+4` (screenshot to clipboard)
2. Open Claude Code
3. Try `cmd+v` (should paste image if remapping works)
4. Verify no interference with normal cmd+v in other apps

---

**Next Steps**: Choose your preferred option and let me know. I can implement Option 1 (Karabiner) or Option 2 (terminal-specific) for you.
