---
complexity: medium
context_sync:
  ce_updated: true
  last_sync: '2025-11-06T10:53:07.198803+00:00'
  serena_updated: false
created: 2025-11-06 11:18:47.779859
dependencies: repomix_unpack.py, blend tool (PRP-34), uv
estimated_hours: 2-3
execution_order: 1
feature_name: CE Framework Project Initializer - Core Module
issue: TBD
merge_order: 1
prp_id: 36.1.1
stage: 1
status: pending
updated: '2025-11-06T10:53:07.198973+00:00'
updated_by: update-context-command
---

# CE Framework Project Initializer - Core Module

## 1. TL;DR

**Objective**: CE Framework Project Initializer - Core Module

**What**: Create `tools/ce/init_project.py` module implementing the core ProjectInitializer class with 4-phase pipeline for installing CE framework on target projects.

**Goal**: Implement ProjectInitializer cl...

**Why**: Enable functionality described in INITIAL.md with 8 reference examples

**Effort**: Medium (2-3 hours estimated based on complexity)

**Dependencies**: repomix_unpack.py, blend tool (PRP-34), uv


## 2. Context

### Background

Create `tools/ce/init_project.py` module implementing the core ProjectInitializer class with 4-phase pipeline for installing CE framework on target projects.

**Goal**: Implement ProjectInitializer class with extract, blend, initialize, and verify phases

**What to Build**:
1. ProjectInitializer class with constructor accepting target_project path and dry_run flag
2. run() method orchestrating all 4 phases or specific phase
3. extract() method - extracts ce-infrastructure.xml using repomix_unpack.py, reorganizes tools/ to .ce/tools/, copies ce-workflow-docs.xml
4. blend() method - delegates to `ce blend --all --target-dir <target>` subprocess call
5. initialize() method - runs `uv sync` in .ce/tools/ and verifies installation
6. verify() method - checks critical files exist, validates settings.local.json JSON, reports summary

**Acceptance Criteria**:
1. ✅ ProjectInitializer class created with 4 methods (extract, blend, initialize, verify)
2. ✅ run() method accepts phase parameter ("all", "extract", "blend", "initialize", "verify")
3. ✅ extract() uses repomix_unpack.py to extract ce-infrastructure.xml
4. ✅ blend() calls subprocess for `uv run ce blend --all --target-dir <path>`
5. ✅ initialize() runs `uv sync` in .ce/tools/ directory
6. ✅ verify() validates installation with file checks and JSON validation
7. ✅ Dry-run mode supported (shows actions without executing)
8. ✅ Unit tests created in tools/tests/test_init_project.py
9. ✅ Error handling with actionable troubleshooting messages
10. ✅ All phases return dict with status info

### Constraints and Considerations

**Security**:
- Validate target_dir exists and is writable before operations
- Never overwrite existing .ce/ without user confirmation
- Check for ce-infrastructure.xml existence before extraction

**Error Handling**:
- Fast failure with actionable messages
- Include 🔧 troubleshooting for common errors:
  - "ce-infrastructure.xml not found" → Check .ce/ directory
  - "uv not installed" → Provide install instructions
  - "Blend phase failed" → Show blend tool error output

**File Organization**:
- Extract to .ce/tools/ (not tools/) in target project
- Preserve directory structure from repomix package
- Copy ce-workflow-docs.xml to .ce/ (reference package)

**Dependencies**:
- Requires repomix_unpack.py (exists at tools/ce/repomix_unpack.py)
- Requires blend tool from PRP-34 (exists at tools/ce/blending/)
- Requires uv binary on system PATH

**Testing Strategy**:
- Unit tests with tempfile.TemporaryDirectory for isolation
- Mock subprocess calls for blend/initialize phases
- Verify file structure after extraction phase
- Test dry-run mode doesn't modify files

**Code Quality**:
- Functions: <50 lines (split phases into helper methods if needed)
- Class: ~150 lines total (4 phases + helpers)
- No silent failures - all errors bubble up with context
- Mark subprocess mocks with FIXME in tests

**Integration Points**:
- Phase 2 (PRP-36.2.1): CLI will import this class
- Phase 3 (PRP-36.2.2): Handler will call this class
- Both depend on this module being complete and tested

### Files Modified

**NEW**:
- `tools/ce/init_project.py` - ProjectInitializer class implementation
- `tools/tests/test_init_project.py` - Unit tests for init_project module

**DEPENDENCIES**:
- `tools/ce/repomix_unpack.py` - Used by extract() method (existing)
- `tools/ce/blending/core.py` - Called via subprocess by blend() method (existing from PRP-34)

### Documentation References

- Standard (library documentation)
- File (library documentation)
- Running (library documentation)
- JSON (library documentation)
- Backup (library documentation)
- Tools (library documentation)
- Delegation (library documentation)
- Blending (library documentation)
- Package (library documentation)
- Install (library documentation)
- Verify (library documentation)


## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (1.5-2 hours)

1. Create `tools/ce/init_project.py` with ProjectInitializer class
2. Implement `__init__()` method (accept target_project path and dry_run flag)
3. Implement `extract()` method (use repomix_unpack.py, reorganize to .ce/tools/)
4. Implement `blend()` method (subprocess call to `ce blend --all`)
5. Implement `initialize()` method (run `uv sync` in .ce/tools/)
6. Implement `verify()` method (check critical files, validate JSON)
7. Implement `run()` method (orchestrate all phases with phase parameter)

### Phase 3: Testing and Validation (0.5-1 hours)

1. Create `tools/tests/test_init_project.py` with pytest fixtures
2. Write unit tests for each phase (extract, blend, initialize, verify)
3. Test dry-run mode doesn't modify files (use tempfile.TemporaryDirectory)
4. Mock subprocess calls for blend/initialize phases
5. Run validation gates: `uv run pytest tools/tests/test_init_project.py -v`


## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**: `uv run pytest tools/tests/test_init_project.py -v`

**Success Criteria**:
- All init_project unit tests pass (extract, blend, initialize, verify phases)
- Dry-run mode test passes (no file modifications)
- Mock subprocess tests pass
- Code coverage ≥ 80% for init_project.py

### Gate 2: Module Import Test

**Command**: `uv run python -c "from ce.init_project import ProjectInitializer; print('Import successful')"`

**Success Criteria**:
- Module imports without errors
- Class is accessible and instantiable

### Gate 3: Acceptance Criteria Validation

**Commands**:
```bash
# Verify all 4 methods exist
uv run python -c "from ce.init_project import ProjectInitializer; p = ProjectInitializer('/tmp/test', True); print('Methods:', [m for m in dir(p) if not m.startswith('_')])"

# Verify run() method accepts phase parameter
uv run python -c "from ce.init_project import ProjectInitializer; import inspect; print('run() signature:', inspect.signature(ProjectInitializer.run))"
```

**Success Criteria**:
- All 10 acceptance criteria from master plan validated
- ProjectInitializer class has extract(), blend(), initialize(), verify(), run() methods
- run() method accepts phase parameter


## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
uv run pytest tests/ -v
```

### Coverage Requirements

- Unit test coverage: ≥ 80%
- Integration tests for critical paths
- Edge cases from INITIAL.md covered


## 6. Risks & Mitigations

### Risk 1: Target project already has CE files

**Impact**: HIGH - Overwriting existing CE files could lose user customizations

**Mitigation**:
- Detect existing .ce/ directory before extraction
- Prompt user for action: overwrite / merge / abort
- Create backups before overwriting

### Risk 2: UV not installed on system

**Impact**: MEDIUM - initialize() phase will fail

**Mitigation**:
- Check for `uv` binary in PATH before calling
- Provide actionable error with install instructions:
  ```
  ❌ uv not found in PATH
  🔧 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### Risk 3: ce-infrastructure.xml not found

**Impact**: HIGH - Cannot extract framework files

**Mitigation**:
- Check for package in `.ce/ce-infrastructure.xml` at init
- Error with troubleshooting if missing:
  ```
  ❌ ce-infrastructure.xml not found in .ce/
  🔧 Ensure you're running from ctx-eng-plus repo root
  ```

### Risk 4: Blend phase fails

**Impact**: MEDIUM - Partial installation leaves project in inconsistent state

**Mitigation**:
- Catch subprocess errors from blend command
- Preserve file backups before blending
- Provide rollback instructions on failure

## 7. Rollout Plan

### Phase 1: Development

1. Implement core functionality
2. Write tests
3. Pass validation gates

### Phase 2: Review

1. Self-review code changes
2. Peer review (optional)
3. Update documentation

### Phase 3: Deployment

1. Merge to main branch
2. Monitor for issues
3. Update stakeholders


---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: 0
- **Test Patterns**: 1
- **Serena Available**: False

### Documentation Sources
- **Library Docs**: 0
- **External Links**: 0
- **Context7 Available**: False