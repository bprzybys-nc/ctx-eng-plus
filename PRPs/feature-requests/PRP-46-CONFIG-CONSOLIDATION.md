# PRP-46: Config Consolidation - Unified .ce/config.yml

**Status**: Feature Request  
**Priority**: HIGH  
**Type**: Architecture Refactor  
**Estimated**: 2 hours  
**Start Date**: 2025-11-10

---

## Problem Statement

Init-project configuration is currently fragmented across multiple files:

- `directories.yml` - Path mappings only
- `blend-config.yml` - Blending strategies + paths (duplicates `directories.yml`)
- `repomix-profile-*.json` - Package composition (3 separate files)
- `init_project.py` - Hardcoded defaults and fallbacks
- `.gitignore` - Implicit exclusion rules

**Issues**:
- ❌ No single source of truth
- ❌ Inconsistent path specifications (e.g., `claude_dir: .ce/.claude/` vs `.claude/`)
- ❌ Difficult to add new domains or migration strategies
- ❌ Repomix config doesn't reference main config
- ❌ Cleanup logic has hardcoded domain list instead of config-driven

**Root Causes Fixed by This Feature**:
1. `.claude` path incorrectly specified as `.ce/.claude/` (fixed by consolidation)
2. `context-engineering/` missing from detection (fixed by explicit config)
3. No central documentation of cleanup behavior (fixed by config)

---

## Proposed Solution

Create single unified configuration: **`.ce/config.yml`**

### Architecture Benefits

✅ **Single Source of Truth**: All init-project config in one YAML file  
✅ **Self-Documenting**: All domains, strategies, and paths explicit  
✅ **Easy to Extend**: Add new domains, modify strategies without code changes  
✅ **Config-Driven Logic**: Detection, blending, cleanup all driven by config  
✅ **Validation Ready**: Schema validation possible for config  

### Configuration Structure

```yaml
# .ce/config.yml - Complete init-project configuration

version: "1.1"

# Phase 1: File discovery (what to look for)
detection:
  domains:
    prps:
      legacy_paths: [PRPs/, context-engineering/PRPs/, context-engineering/]
      search_patterns: ["**/*.md"]
    examples:
      legacy_paths: [examples/, context-engineering/examples/]
      search_patterns: ["**/*.md", "**/*.py"]
    memories:
      legacy_paths: [.serena/memories/]
      search_patterns: ["**/*.md"]
    # ... other domains

# Phase 2: Directory locations
directories:
  output:
    claude_dir: .claude/                 # FIXED: Not .ce/.claude/
    serena_memories: .serena/memories/   # At project root
    examples: .ce/examples/
    prps: .ce/PRPs/
  framework:
    claude_dir: .claude/
    serena_memories: .serena/memories/
  legacy_cleanup:
    - PRPs/
    - examples/
    - context-engineering/              # Fully defined
    - .serena.old/

# Phase 3: Blending strategies
blending:
  domains:
    memories:
      strategy: intelligent_merge
      critical_memories:
        - code-style-conventions.md
        - task-completion-checklist.md
        - testing-standards.md
        # ... others

# Phase 4: Cleanup verification
cleanup:
  strategy: safe
  legacy_directories:
    - name: context-engineering/
      required_migration: true
      subdirectories: [PRPs/, examples/]
      root_files: true                   # FIXED: Handle root files

# Package composition
repomix:
  infrastructure:
    include:
      - .serena/memories/**              # FIXED: Root .serena/, not .ce/.serena/
      - .claude/commands/**/*.md         # FIXED: Root .claude/
      - .ce/config.yml                   # Self-reference

# Validation gates
validation_gates:
  gate_1:
    name: Framework Structure
    checks:
      - test -d .ce/examples/
      - test ! -d .ce/.serena/          # Should NOT exist
      - test ! -d .ce/.claude/          # Should NOT exist
  gate_4:
    name: Memories Domain
    checks:
      - test -d .serena/memories/       # At project root
      - test ! -d .ce/.serena/          # Not in .ce/
```

---

## Implementation Plan

### PHASE 1: Create Config (Parallel - 3 Haiku Subagents)

**Haiku Subagent 1**: Create base `.ce/config.yml`
```
Task: Create /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/config.yml

Content:
- Copy structure from design document
- All 6 domains properly configured
- All paths correctly set (e.g., claude_dir: .claude/)
- All cleanup rules for legacy directories
- All validation gates

Validation:
- File is valid YAML (can be parsed)
- All required sections present
- All paths correct
```

**Haiku Subagent 2**: Update repomix-profile-infrastructure.json
```
Task: Update /Users/bprzybyszi/nc-src/ctx-eng-plus/.ce/repomix-profile-infrastructure.json

Changes:
- Update include list to match config.yml specification
- Add .ce/config.yml to include list (self-reference)
- Fix .serena/memories/** (ensure at root, not .ce/.serena/)
- Fix .claude/commands/** (ensure root .claude/)
- Verify all domains match config.yml

Reference:
- config.yml repomix.infrastructure.include list
```

**Haiku Subagent 3**: Update .gitignore & deprecate old configs
```
Task: Update .gitignore + prepare deprecation

Changes:
- Ensure .serena/ is only partially excluded (.serena/cache/ only)
- Verify config.yml inclusion rules match ignore patterns
- Create deprecation notice in directories.yml (references config.yml)
- Create deprecation notice in blend-config.yml (references config.yml)

Note: Keep old files for backward compatibility until migration complete
```

**Parallel Time**: ~8 minutes
**Sequential Time**: ~24 minutes

### PHASE 2: Fix Core Logic (Sequential - 2 Tasks)

**Task 1**: Update detection.py to use config.yml
```
Location: /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/detection.py

Changes:
1. Load config from .ce/config.yml
2. Use config.domains[domain].legacy_paths for searches
3. Use config.domains[domain].search_patterns for file matching
4. Properly detect context-engineering/ root files (per config)

Result:
- detection.scan_all() now config-driven
- All 6 domains properly detected
- context-engineering/ fully scanned (root + subdirs)
```

**Task 2**: Update cleanup.py to use config.yml
```
Location: /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/cleanup.py

Changes:
1. Load config from .ce/config.yml
2. Use config.cleanup.legacy_directories for cleanup rules
3. Use config.directories.legacy_cleanup list for what to remove
4. Fix context-engineering verification (handle root files per config)
5. Verify migrations match config specifications

Result:
- cleanup_legacy_dirs() now config-driven
- Safe deletion with migration verification
- context-engineering/ fully handled
```

**Time**: ~20 minutes

### PHASE 3: Update Code References (Sequential - 1 Task)

**Task 3**: Update init_project.py & core.py
```
Locations:
- /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/init_project.py
- /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/core.py

Changes:
1. Load BlendConfig from .ce/config.yml (not directories.yml)
2. Use config.directories for all path operations
3. Use config.blending for all strategy selection
4. Update docstrings to reference config.yml

Result:
- All path operations config-driven
- Single source of truth throughout codebase
```

**Time**: ~10 minutes

### PHASE 4: Testing & Validation (Sequential)

**Reset & Test**:
```
1. Reset certinia-test-target to clean state
2. Run init-project
3. Verify all 5 gates pass
4. Check: No .ce/.claude/ (only root .claude/)
5. Check: No .ce/.serena/ (only root .serena/memories/)
6. Check: context-engineering/ properly detected and handled
```

**Time**: ~15 minutes

---

## Execution Timeline

```
Phase 1 (Parallel Haiku):      8 min  ████████
  ├─ Haiku-1: Create config.yml
  ├─ Haiku-2: Update repomix
  └─ Haiku-3: Update .gitignore

Phase 2 (Sequential):          20 min ████████████████████
  ├─ Task-1: detection.py
  └─ Task-2: cleanup.py

Phase 3 (Sequential):          10 min ██████████
  └─ Task-3: init_project.py, core.py

Phase 4 (Testing):             15 min ███████████████

TOTAL: ~53 minutes (vs ~95 sequential)
```

---

## Quality Criteria

✅ Single config file contains ALL init-project configuration  
✅ No path specifications in multiple files (DRY principle)  
✅ config.yml properly structured with all 6 domains  
✅ detection.py uses config.yml for detection  
✅ cleanup.py uses config.yml for cleanup rules  
✅ init_project.py uses config.yml for all path operations  
✅ All 5 validation gates pass  
✅ .claude/ at project root (not in .ce/)  
✅ .serena/memories/ at project root (not in .ce/)  
✅ context-engineering/ fully detected and handled  
✅ Repomix package includes config.yml (self-documenting)  

---

## Risk Assessment

**Risk**: Configuration breaks during migration
- **Mitigation**: Keep old files, gradual migration
- **Rollback**: Revert to directories.yml + blend-config.yml

**Risk**: Detection finds unexpected files
- **Mitigation**: Test on certinia-test-target (107 context-engineering files)
- **Rollback**: Use previous defaults if config incomplete

**Risk**: Cleanup logic deletes wrong files
- **Mitigation**: Migration verification in config
- **Rollback**: Manual review of unmigrated files

---

## Files Modified

1. **Create**: `.ce/config.yml` (NEW - unified config)
2. **Update**: `repomix-profile-infrastructure.json` (reference config)
3. **Update**: `.gitignore` (fix .serena/ partial exclusion)
4. **Update**: `detection.py` (config-driven detection)
5. **Update**: `cleanup.py` (config-driven verification)
6. **Update**: `init_project.py` (use config.yml)
7. **Update**: `blending/core.py` (use config.yml)
8. **Deprecate**: `directories.yml` (keep for backward compat)
9. **Deprecate**: `blend-config.yml` (keep for backward compat)

---

## Success Criteria

- [ ] `.ce/config.yml` created with all configuration
- [ ] All domains properly configured with paths
- [ ] detection.py reads from config.yml
- [ ] cleanup.py reads from config.yml
- [ ] init_project.py reads from config.yml
- [ ] Repomix package includes config.yml
- [ ] certinia-test-target test passes all 5 gates
- [ ] No .ce/.claude/ directory created
- [ ] No .ce/.serena/ directory created
- [ ] context-engineering/ fully handled

---

## Post-Implementation

**For Framework Users**:
- `.ce/config.yml` is single source of truth
- Easy to customize domains, paths, strategies
- Full control without code changes

**For Framework Developers**:
- Config-driven architecture
- Add new domains: Just add to config.yml
- Change path structure: Update one file
- Extend blending strategy: Add to config + code

**Migration Path**:
- Phase 1: Create config.yml (parallel with old files)
- Phase 2: Update code to read config.yml
- Phase 3: Keep old files for backward compat
- Phase 4: Eventually deprecate old files (next major version)

---

## Related Issues Fixed

- ✅ Issue: `.claude/` incorrectly placed in `.ce/.claude/`
- ✅ Issue: `context-engineering/` not fully detected
- ✅ Issue: Configuration fragmented across files
- ✅ Issue: Repomix config doesn't reference main config

---

**Created**: 2025-11-10  
**Implementation Time**: 53 minutes (with 3 parallel Haiku subagents)  
**Ready for**: Development Sprint
