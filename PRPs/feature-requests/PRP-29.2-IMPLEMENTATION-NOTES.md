# PRP-29.2 Implementation Notes

**Date**: 2025-10-27
**Status**: Partially Executed (Phase 1 Complete)
**Blocker**: Requires TypeScript implementation in syntropy-mcp MCP server

---

## Execution Summary

### ✅ Completed: Phase 1 - Boilerplate Cleanup

**Completed via PRP-29.5** (Centralized Config Profile System)

**Work Done**:
1. ✅ Deleted runtime/cache files from `syntropy-mcp/ce/`:
   - drift-report.md
   - syntropy-health-cache.json
   - tools/.venv/
   - tools/.pytest_cache/
   - tools/tmp/
   - tools/.coverage

2. ✅ Converted config files to templates:
   - config.yml with profile section and `<missing>` placeholders
   - linear-defaults.yml (DEPRECATED)
   - .serena/project.yml (DEPRECATED)

3. ✅ Added .gitignore with copy exceptions

4. ✅ Documented cleanup in BOILERPLATE_CHANGELOG.md

5. ✅ Updated SystemModel.md with generic placeholders

**Result**: Boilerplate is now project-naive and ready for selective copying

---

## ❌ Blocked: Phases 2-6 - TypeScript Implementation

### Why Blocked

**Current Context**: Working in `syntropy-mcp/ce/` (Python tools)
**Required Context**: `syntropy-mcp/src/` (TypeScript MCP server)

**Implementation Location Mismatch**:
- Phase 2-6 require changes to `syntropy-mcp/src/tools/init.ts`
- Phase 2-6 require changes to `syntropy-mcp/src/scanner.ts`
- Tests go in `syntropy-mcp/src/tools/init.test.ts`
- Current session is focused on Python tools, not TypeScript MCP server

### What's Blocked

**Phase 2: Already-Initialized Detection** (1 hour)
- File: `syntropy-mcp/src/scanner.ts`
- Function: `isAlreadyInitialized(projectRoot: string): boolean`
- Checks: `.ce/RULES.md`, `.ce/PRPs/system/`, `.ce/tools/`

**Phase 3: Selective Copy Logic** (2 hours)
- File: `syntropy-mcp/src/tools/init.ts`
- Function: `copyBoilerplate()` - replace full recursive with selective mapping
- Exception: `.serena/` → root (not `.ce/.serena/`)
- Exception: `RULES.md` → deferred to blending

**Phase 4: RULES.md Blending** (2 hours)
- File: `syntropy-mcp/src/tools/init.ts`
- Function: `blendRulesIntoCLAUDEmd()`
- Features:
  - Parse markdown into sections
  - Semantic deduplication (70% keyword overlap)
  - Filter anti-patterns
  - Preserve CLAUDE.md style

**Phase 5: Serena Activation** (1.5 hours)
- File: `syntropy-mcp/src/tools/init.ts`
- Function: `activateSerenaProject()`
- Non-fatal: Warns if Serena unavailable

**Phase 6: Integration** (30 minutes)
- File: `syntropy-mcp/src/tools/init.ts`
- Function: `initProject()` - orchestrate all 9 phases
- Update tests in `syntropy-mcp/src/tools/init.test.ts`

---

## Handoff Notes for TypeScript Implementation

### Prerequisites

1. **Working Directory**: Switch to `syntropy-mcp/` (MCP server root)
2. **Language**: TypeScript (not Python)
3. **Dependencies**: Node.js 18+, TypeScript
4. **PRP Reference**: Read PRP-29.2 phases 2-6 for detailed implementation

### Implementation Order

**Recommended sequence**:

1. **Phase 2 First** - Already-initialized detection is foundational
   - Prevents accidental re-init
   - Simplest to implement
   - Clear test cases

2. **Phase 3 Second** - Selective copy logic
   - Uses phase 2 detection
   - Foundation for blending

3. **Phase 4 Third** - RULES.md blending
   - Most complex algorithm
   - Depends on selective copy

4. **Phase 5 Fourth** - Serena activation
   - Independent from blending
   - Non-fatal design

5. **Phase 6 Last** - Integration
   - Orchestrates all phases
   - Comprehensive tests

### Key Design Decisions from PRP

**Already-Initialized Detection**:
- Check 3 markers (not just 1)
- Return early with success message
- Clear log output

**Selective Copying**:
- Explicit file lists (not glob patterns)
- Exception mapping for `.serena/` and `RULES.md`
- Config files to `.ce/`

**RULES.md Blending**:
- Semantic matching (not exact string)
- 70% keyword overlap threshold
- Filter anti-pattern sections
- Preserve user's CLAUDE.md style

**Serena Activation**:
- Non-fatal error handling
- Clear warnings if unavailable
- Uses client manager

### Testing Strategy

**Unit Tests Required**:
```typescript
// scanner.test.ts
describe("isAlreadyInitialized", () => {
  it("returns true when all markers exist")
  it("returns false when markers missing")
})

// init.test.ts
describe("Selective Copy", () => {
  it("copies standard dirs to .ce/")
  it("copies .serena/ to root")
  it("does not copy RULES.md directly")
})

describe("RULES.md Blending", () => {
  it("blends unique rules")
  it("skips duplicates")
  it("preserves style")
})

describe("Serena Activation", () => {
  it("activates with project path")
  it("continues on failure")
})
```

**Integration Test**:
```bash
# Full workflow
syntropy_init_project /tmp/test-project
cd /tmp/test-project

# Verify outcomes
test -d .ce/PRPs/system && echo "✅"
test -d .serena && echo "✅"
test ! -d .ce/.serena && echo "✅"
test -f CLAUDE.md && echo "✅"
test ! -f .ce/RULES.md && echo "✅"

# Verify idempotent
syntropy_init_project /tmp/test-project  # Should skip
```

### Success Criteria

**Must Have**:
- [ ] Already-initialized detection working
- [ ] Selective copying implemented
- [ ] `.serena/` at project root
- [ ] RULES.md blended (no duplicates)
- [ ] Serena activated (non-fatal)
- [ ] All tests passing
- [ ] Clear log messages

**Quality Gates**:
- 100% test coverage for new functions
- All error messages include troubleshooting
- No fishy fallbacks
- KISS principles applied

### Estimated Time

**Total**: 6-7 hours for phases 2-6

**Breakdown**:
- Phase 2: 1 hour
- Phase 3: 2 hours
- Phase 4: 2 hours
- Phase 5: 1.5 hours
- Phase 6: 30 minutes

### Files to Modify

```
syntropy-mcp/
├── src/
│   ├── scanner.ts                    # ADD isAlreadyInitialized()
│   ├── scanner.test.ts              # ADD tests
│   └── tools/
│       ├── init.ts                   # MODIFY copyBoilerplate()
│       │                             # ADD blendRulesIntoCLAUDEmd()
│       │                             # ADD activateSerenaProject()
│       │                             # MODIFY initProject()
│       └── init.test.ts             # UPDATE tests
```

### Next Steps

1. Switch working context to `syntropy-mcp/` MCP server
2. Read PRP-29.2 phases 2-6 in detail
3. Implement phase 2 (already-initialized detection)
4. Write tests for phase 2
5. Continue with phases 3-6 sequentially
6. Update PRP-29.2 status to "executed" when complete

---

## Configuration System Changes (PRP-29.5)

**IMPORTANT**: Phase 1 cleanup integrated centralized config system:

**New Config Structure**:
```yaml
# config.yml
profile:
  project_name: "<missing>"
  linear:
    project: "<missing>"
    assignee: "<missing>"
    team: "<missing>"
```

**Deprecated Files**:
- `linear-defaults.yml` → Use `config.yml profile.linear`
- `.serena/project.yml` → Use `config.yml profile.project_name`

**Migration Tool**: `ce migrate-config`

**Impact on Init Tool**:
- Copy `config.yml` with `<missing>` placeholders
- User must fill required fields before using system
- Validation happens on command startup

---

## Related Work

- **PRP-29.1**: Init tool foundation (completed)
- **PRP-29.5**: Centralized config system (completed - includes Phase 1 cleanup)
- **PRP-29.2**: This PRP (Phase 1 done, Phases 2-6 blocked)

---

**Status**: Ready for TypeScript implementation when switching to syntropy-mcp MCP server context
