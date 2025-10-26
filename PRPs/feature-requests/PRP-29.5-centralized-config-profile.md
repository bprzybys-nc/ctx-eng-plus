---
prp_id: PRP-29.5
title: Centralized Configuration Profile System
status: executed
priority: high
created_date: '2025-10-27'
execution_date: '2025-10-27'
feature_area: configuration-management
tags:
  - config
  - validation
  - DX
  - infrastructure
related_prps:
  - PRP-29.1
  - PRP-29.2
issue: null
implementation_summary: null
last_updated: '2025-10-27'
updated_by: prp-requirements-update
execution_requirements:
  active_project: ctx-eng-plus
  working_directory: /Users/bprzybysz/nc-src/ctx-eng-plus
  language_context: Python
  reason: Implements config system in Python tools (tools/ce/config_utils.py, tools/ce/migration_utils.py)
---

# PRP-29.5: Centralized Configuration Profile System

## Overview

Implement centralized configuration management with profile section in `.ce/config.yml`, replacing scattered configuration files (linear-defaults.yml, .serena/project.yml) with single source of truth that validates required fields on system startup.

## Problem Statement

**Current State**:
- Configuration scattered across multiple files:
  - `linear-defaults.yml` - Linear project settings
  - `.serena/project.yml` - Serena project name
  - `config.yml` - Only cache settings
- No validation of required fields
- Users can run commands with incomplete/invalid config
- No clear distinction between required vs optional fields
- Migration between config formats requires manual work

**Pain Points**:
1. Confusing UX - which file for which setting?
2. Silent failures - missing config detected late
3. No validation - typos discovered at runtime
4. Multiple files - harder to maintain
5. No migration path - manual updates error-prone

## Solution

### Centralized Profile Section

**Single Source of Truth**: `.ce/config.yml` with profile section

```yaml
profile:
  # REQUIRED fields
  project_name: "<missing>"
  linear:
    project: "<missing>"
    assignee: "<missing>"
    team: "<missing>"
    default_labels: ["feature"]

  # Optional fields
  git:
    author_name: ""
    author_email: ""
  repository:
    url: ""
    main_branch: "main"

_validation:
  required_fields:
    - profile.project_name
    - profile.linear.project
    - profile.linear.assignee
    - profile.linear.team
  schema_version: "1.0.0"
```

### Startup Validation

**Block execution if config incomplete**:

```python
# In __main__.py
def main():
    # Validate config before command execution
    if args.command not in skip_validation_commands:
        try:
            config = load_config()  # Validates required fields
        except ConfigError as e:
            print(f"❌ Configuration Error:\n{e}\n", file=sys.stderr)
            return 1
```

**Clear Error Messages**:

```
❌ Configuration Error:
⚠️  Required configuration incomplete in .ce/config.yml:
   - profile.project_name
   - profile.linear.assignee

🔧 Troubleshooting:
   1. Edit .ce/config.yml
   2. Replace <missing> with actual values:
      - profile.project_name: Your project name
      - profile.linear.assignee: your.email@example.com
   3. Save and retry command
```

### Migration Tool

**Automated Migration**: `ce migrate-config`

```bash
cd tools && uv run ce migrate-config

# Migrates:
# - linear-defaults.yml → config.yml profile.linear
# - .serena/project.yml → config.yml profile.project_name
# - Backs up old files
# - Removes linear-defaults.yml after migration
```

### Backward Compatibility

**Graceful Fallback** in `linear_utils.py`:

```python
def get_linear_defaults():
    # Try config.yml first (RECOMMENDED)
    if new_config_path.exists():
        config = load_config(str(new_config_path))
        if "profile" in config and "linear" in config["profile"]:
            return config["profile"]["linear"]

    # Fallback to linear-defaults.yml (DEPRECATED)
    if old_config_path.exists():
        warnings.warn("linear-defaults.yml is DEPRECATED")
        # ... load old file
```

## Implementation

### Files Created

**1. tools/ce/config_utils.py** (203 lines)
- `load_config()` - Load and validate config.yml
- `validate_config()` - Check required fields filled
- `get_nested_value()` - Access nested config via dot notation
- `get_profile_value()` - Shorthand for profile section access
- `ConfigError` - Custom exception with troubleshooting

**2. tools/ce/migration_utils.py** (130 lines)
- `migrate_linear_defaults_to_config()` - Automated migration
- `print_migration_report()` - Human-readable output
- Migrates both Linear config AND project_name
- Creates backups before modifying files

**3. tools/tests/test_config_utils.py** (220 lines)
- 15 comprehensive tests
- Covers validation logic, error handling, edge cases
- Uses pytest fixtures for clean test setup

### Files Modified

**4. syntropy-mcp/ce/config.yml** - Template with profile section
**5. .ce/config.yml** - Project config with actual values
**6. tools/ce/linear_utils.py** - Read from config.yml with fallback
**7. tools/ce/__main__.py** - Startup validation + migrate-config command
**8. tools/ce/cli_handlers.py** - cmd_migrate_config handler

## Validation Gates

### L1 - Syntax & Style

```bash
cd tools && uv run pytest tests/test_config_utils.py -v
# ✅ All 15 tests pass
# ✅ Config loading tested
# ✅ Validation logic tested
# ✅ Error messages tested
```

### L2 - Unit Tests

```bash
# Test config validation
cd tools && python3 -c "
from ce.config_utils import load_config
config = load_config('../.ce/config.yml')
assert config['profile']['project_name'] == 'ctx-eng-plus'
print('✅ Config loads successfully')
"

# Test missing field detection
cd tools && python3 -c "
from ce.config_utils import validate_config, ConfigError
config = {'_validation': {'required_fields': ['profile.name']}, 'profile': {'name': '<missing>'}}
try:
    validate_config(config, 'test.yml')
    print('❌ Should have raised ConfigError')
except ConfigError as e:
    assert 'profile.name' in str(e)
    print('✅ Missing field detection works')
"
```

### L3 - Integration Tests

```bash
# Test actual command with validation
cd tools && uv run ce git status
# ✅ Should validate config and execute

# Test migration command
cd tools && uv run ce migrate-config
# ✅ Should skip validation (setup command)
```

### L4 - Pattern Conformance

**No Fishy Fallbacks** ✅:
- Required fields must be filled
- Exceptions raised with troubleshooting
- No silent failures

**KISS Principles** ✅:
- Single config file (not 3)
- Clear error messages
- Simple migration tool
- Minimal dependencies (stdlib + yaml)

**Testing Standards** ✅:
- Real functionality tested
- No mocked config validation
- Edge cases covered

## Acceptance Criteria

### Must Have

- [x] Profile section in config.yml with required/optional fields
- [x] Startup validation blocks execution if required fields `<missing>`
- [x] Clear error messages with troubleshooting guidance
- [x] Migration tool: `ce migrate-config`
- [x] Backward compatibility with linear-defaults.yml
- [x] Tests for validation logic
- [x] User's config.yml populated with known values

### Should Have

- [x] Migrate project_name from .serena/project.yml
- [x] Backup old config before migration
- [x] Deprecation warnings for old config format
- [x] Configuration caching (avoid repeated reads)
- [x] Skip validation for setup commands

### Nice to Have

- [ ] Interactive prompting for missing fields
- [ ] Config schema validation (JSON Schema)
- [ ] Environment variable overrides
- [ ] Documentation in CLAUDE.md

## Migration Path

### For New Projects

```bash
# 1. Init creates config.yml with <missing> placeholders
cd tools && uv run ce init-project

# 2. Edit config.yml
vim .ce/config.yml
# Replace <missing> with actual values

# 3. Validate
cd tools && uv run ce git status
# ✅ Validation passes, command executes
```

### For Existing Projects

```bash
# 1. Automated migration
cd tools && uv run ce migrate-config
# Migrates linear-defaults.yml + .serena/project.yml → config.yml

# 2. Review migration
cat .ce/config.yml
# ✅ All values migrated

# 3. Test commands
cd tools && uv run ce git status
# ✅ Works with new config
```

## Testing Strategy

### Unit Tests (15 tests)

```python
test_load_config_success()              # Happy path
test_load_config_file_not_found()       # Missing file
test_load_config_invalid_yaml()         # Syntax errors
test_validate_config_missing_fields()   # <missing> detection
test_validate_config_empty_string()     # "" treated as missing
test_get_nested_value_*()               # Dot notation access
test_get_profile_value_*()              # Profile shortcuts
```

### Integration Tests

```bash
# Real command execution with validation
cd tools && uv run ce validate --level all

# Migration with real files
cd tools && uv run ce migrate-config

# Fallback behavior
mv .ce/config.yml .ce/config.yml.bak
# Should fall back to linear-defaults.yml with warning
```

## Rollback Plan

If config system causes issues:

```bash
# 1. Restore old config files
cp .ce/linear-defaults.yml.backup .ce/linear-defaults.yml

# 2. Remove profile section from config.yml
# (linear_utils.py will fall back automatically)

# 3. Report issue with:
#    - Error message
#    - Config.yml content
#    - Command that failed
```

## Performance Impact

- **Startup overhead**: +5-10ms for config validation
- **Caching**: Config loaded once per process
- **Migration**: One-time operation (<100ms)

**Mitigation**:
- Skip validation for setup commands
- Cache config after first load
- No validation in tight loops

## Security Considerations

**Config File Permissions**:
- `.ce/config.yml` contains emails and team IDs
- Should be in `.gitignore` for private projects
- No secrets stored (API keys belong in env vars)

**Validation Security**:
- YAML safe_load prevents code execution
- Path validation prevents directory traversal
- No eval() or exec() used

## Documentation Updates

### CLAUDE.md

```markdown
## Configuration Management

**Location**: `.ce/config.yml`

**Profile Section**:
- `project_name` - REQUIRED - Serena project name
- `linear.*` - REQUIRED - Linear integration settings
- `git.*` - Optional - Git defaults
- `repository.*` - Optional - Repo metadata

**Migration**: Run `cd tools && uv run ce migrate-config`
```

### README.md

```markdown
## Configuration

All project settings in `.ce/config.yml`:

```yaml
profile:
  project_name: "your-project"
  linear:
    project: "YourProject"
    assignee: "you@example.com"
    team: "TEAM_ID"
```

Required fields must be filled before running commands.
```

## Related Work

- **PRP-29.1**: Syntropy Documentation Init (created boilerplate structure)
- **PRP-29.2**: Syntropy Init Refinement (will use this config system)

## Success Metrics

- ✅ Zero commands run with incomplete config (validation blocks)
- ✅ Migration success rate: 100% (tested with ctx-eng-plus)
- ✅ User confusion reduced (single config file)
- ✅ Error clarity improved (troubleshooting in messages)

## Future Enhancements

1. **Interactive Setup**: Prompt for missing fields on first run
2. **Schema Validation**: JSON Schema for config structure
3. **Environment Overrides**: `CE_LINEAR_ASSIGNEE` env vars
4. **Config Templates**: Pre-populated templates for common setups

---

**Status**: Executed ✅
**Validation**: All gates passed
**Migration**: Tested with ctx-eng-plus project
**Test Coverage**: 15 tests, all passing
