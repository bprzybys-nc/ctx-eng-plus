# Context Engineering Boilerplate

This directory contains the Context Engineering framework boilerplate that is copied to project `.ce/` directories during initialization.

## Structure

```
syntropy-mcp/ce/
├── PRPs/system/          # System PRPs (PRP-1 through PRP-28+)
│   ├── executed/         # Completed framework PRPs
│   └── templates/        # PRP templates (kiss.md, self-healing.md, etc.)
├── examples/system/      # Framework examples
│   ├── model/            # SystemModel.md
│   └── patterns/         # Code patterns and best practices
├── tools/                # CE CLI utilities
│   ├── ce/               # Python package
│   ├── tests/            # Test suite
│   └── pyproject.toml    # UV package configuration
├── .claude/              # Claude Code configuration
│   ├── settings.local.json  # Tool permissions
│   └── RULES.md          # Distilled framework rules
├── .serena/              # Serena memories (empty, for project-specific)
│   └── memories/         # Memory files
├── README.md             # This file
└── config.yml            # Framework configuration

Plus additional files:
- hooks-config.yml        # Git hooks configuration
- linear-defaults.yml     # Linear integration defaults
- shell-functions.sh      # Shell helper functions
- tool-*.yml              # Tool configuration files
```

## Usage

### Initialization

This boilerplate is automatically copied to project `.ce/` directory when running:

```bash
syntropy_init_project /path/to/project
```

### Boilerplate Path Resolution

The initialization tool searches for boilerplate in this order:

1. **Environment variable**: `SYNTROPY_BOILERPLATE_PATH`
   ```bash
   export SYNTROPY_BOILERPLATE_PATH=/custom/path/to/syntropy-mcp/ce
   ```

2. **Development path**: Relative to syntropy-mcp
   - Located at: `syntropy-mcp/ce/`
   - Used during development

3. **Installed path**: npm package location
   - Located at: `syntropy-mcp/boilerplate/`
   - Used after npm install

### What Gets Copied

When initializing a project, the entire contents of this directory are copied to:

```
project-root/.ce/
```

The following user directories are created at project root:

```
project-root/
├── PRPs/
│   ├── feature-requests/  # New PRPs
│   └── executed/          # Completed PRPs
├── examples/              # Project-specific examples
├── .serena/memories/      # Project-specific memories
├── .claude/commands/      # Slash commands
└── CLAUDE.md              # Project guide
```

### System vs User Content

- **System content** (`.ce/`): Framework boilerplate, managed by Syntropy
- **User content** (root): Project-specific PRPs, examples, and configuration

## Maintenance

### Adding System PRPs

1. Add new PRP to `PRPs/system/executed/PRP-N-feature.md`
2. Update boilerplate version in `config.yml`
3. Test initialization with new content

### Adding Examples

1. Add example to `examples/system/patterns/`
2. Document in SystemModel.md if architectural
3. Test boilerplate copy

### Updating Tools

1. Modify `tools/ce/` Python package
2. Run tests: `cd tools && uv run pytest tests/`
3. Update tool documentation

## Verification

Verify boilerplate structure is complete:

```bash
# Check directories
test -d syntropy-mcp/ce/PRPs/system && echo "✅ PRPs"
test -d syntropy-mcp/ce/examples/system && echo "✅ Examples"
test -d syntropy-mcp/ce/tools && echo "✅ Tools"
test -d syntropy-mcp/ce/.serena && echo "✅ Serena"
test -d syntropy-mcp/ce/.claude && echo "✅ .claude"
test -f syntropy-mcp/ce/.claude/RULES.md && echo "✅ RULES.md"
test -f syntropy-mcp/ce/.claude/settings.local.json && echo "✅ settings.local.json"
test -f syntropy-mcp/ce/README.md && echo "✅ README.md"

# Count content
find syntropy-mcp/ce/PRPs/system/executed -name "*.md" | wc -l  # Should be 36+
find syntropy-mcp/ce/PRPs/system/templates -name "*.md" | wc -l  # Should be 3
find syntropy-mcp/ce/examples/system -name "*.md" -o -name "*.py" | wc -l  # Should be 9+
```

## Related PRPs

- **PRP-1**: Init Context Engineering (original implementation)
- **PRP-29.1**: Syntropy Documentation Migration (boilerplate structure)
- **PRP-29.2**: Syntropy Knowledge Query (uses boilerplate)
- **PRP-29.3**: Syntropy Context Sync (updates boilerplate)

## Version

See `config.yml` for current boilerplate version.

---

**Note**: This boilerplate is managed by the Syntropy framework. User projects should NOT modify `.ce/` content directly - use `PRPs/` and `examples/` for project-specific content.
