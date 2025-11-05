---
prp_id: PRP-32.5
feature_name: Move tools/ to .ce/tools/ in Infrastructure Package
status: pending
created: 2025-11-05T09:01:09.960787
updated: 2025-11-05T09:01:09.960787
batch: 32
phase: 5
order: 1
complexity: medium
estimated_hours: 2-3
dependencies: PRP-32.4
---

# Move tools/ to .ce/tools/ in Infrastructure Package

## 1. TL;DR

**Objective**: Move tools/ to .ce/tools/ in Infrastructure Package

**What**: Move tools/ directory to .ce/tools/ in infrastructure package and update all documentation references.

**Current Issues**:
- tools/ is at project root (should be in .ce/tools/ for framework organizat...

**Why**: Enable functionality described in INITIAL.md with 13 reference examples

**Effort**: Medium (3-5 hours estimated based on complexity)

**Dependencies**: repomix.com, Repomix, CE


## 2. Context

### Background

Move tools/ directory to .ce/tools/ in infrastructure package and update all documentation references.

**Current Issues**:
- tools/ is at project root (should be in .ce/tools/ for framework organization)
- Inconsistent with other framework directories (.ce/PRPs/, .serena/, .claude/)
- Infrastructure package references tools/ at root
- Documentation references tools/ at root

**Requirements**:

1. **Directory Movement**:
   - Move `tools/` → `.ce/tools/` in infrastructure package profile
   - Update extraction destination from `tools/` → `.ce/tools/`
   - Keep tools/ at root in THIS repo (ctx-eng-plus development)

2. **Profile Updates**:
   - **ce-infrastructure.json**: Change `tools/ce/*.py` → `.ce/tools/ce/*.py` in target extraction
   - **ce-infrastructure.yml**: Change `tools/` → `.ce/tools/` in comments/destinations
   - Regenerate infrastructure package with new paths

3. **Documentation Updates**:
   - **INITIALIZATION.md**: Update all `tools/` references to `.ce/tools/`
   - **CLAUDE.md**: Update tool commands from `cd tools &&` to `cd .ce/tools &&`
   - **repomix-manifest.yml**: Update tool destination paths
   - **README.md** (if exists): Update any tool references

4. **Bootstrap Script Update**:
   - Update `tools/bootstrap.sh` path references if needed
   - Ensure bootstrap script works with `.ce/tools/` location

**Acceptance Criteria**:
1. Infrastructure profile references `.ce/tools/` for extraction
2. INITIALIZATION.md shows tools extracted to `.ce/tools/`
3. CLAUDE.md commands updated to use `.ce/tools/`
4. Manifest updated with new tool destination
5. Infrastructure package regenerated with correct paths
6. No broken references to old `tools/` path in docs
7. Bootstrap script compatible with new location

### Constraints and Considerations

**Path Consistency**:
- All framework directories under `.ce/` for clear separation
- `.ce/PRPs/executed/system/` (PRP-0)
- `.ce/tools/` (framework tools)
- `.ce/examples/` (workflow docs copy)

**This Repo vs Target Projects**:
- **ctx-eng-plus** (this repo): Keep tools/ at root (development convenience)
- **Target projects**: Extract to `.ce/tools/` (framework organization)
- Infrastructure package paths reference target project structure

**Documentation Scope**:
- Search for ALL `tools/` references in docs
- Update only framework-related tool paths (not project-specific)
- Ensure consistency across all documentation

**Validation**:
- Grep all docs for `tools/` references
- Verify no broken links after changes
- Test extraction workflow (dry-run with repomix if possible)

**Rollback**:
- Keep backup of infrastructure package before regeneration
- Document rollback procedure in PRP

### Documentation References

- [repomix.com](https://repomix.com)
- Repomix (library documentation)
- CE (library documentation)
- Package (library documentation)


## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (2-3 hours)

1. Implement bash component
2. Implement bash component
3. Implement bash component

### Phase 3: Testing and Validation (1-2 hours)

1. Write unit tests following project patterns
2. Write integration tests
3. Run validation gates
4. Update documentation


## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**: `uv run pytest tests/unit/ -v`

**Success Criteria**:
- All new unit tests pass
- Existing tests not broken
- Code coverage ≥ 80%

### Gate 2: Integration Tests Pass

**Command**: `uv run pytest tests/integration/ -v`

**Success Criteria**:
- Integration tests verify end-to-end functionality
- No regressions in existing features

### Gate 3: Acceptance Criteria Met

**Verification**: Manual review against INITIAL.md requirements

**Success Criteria**:

- Requirements from INITIAL.md validated


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


## 6. Rollout Plan

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
