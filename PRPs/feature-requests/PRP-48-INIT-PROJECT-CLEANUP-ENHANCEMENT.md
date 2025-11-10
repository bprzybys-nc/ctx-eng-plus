# PRP-48: init-project Cleanup Enhancement & Architecture Documentation

**Status**: PROPOSED
**Created**: 2025-11-10
**Related**: Iteration 2 test results, serena-procedure.md findings

---

## Executive Summary

Iteration 2 testing on certinia-test-target revealed that init-project is correctly implementing the .serena domain architecture (framework memories imported and blended with project memories at root level), but Gate validation logic was initially incorrect. This PRP documents:

1. ✅ **What's working**: Framework memory import and blend architecture
2. ❌ **What needs improvement**: Gate 1 validation definition (now fixed) and minor cleanup issues
3. 📋 **What to document**: .serena domain architecture for future reference

---

## Current State

### After Iteration 2 with Corrected Gates

```
✅ Gate 1: Framework Structure Preserved
   - Framework memories imported to .serena/memories/: ✅ PASS
   - code-style-conventions.md: ✅ Present
   - task-completion-checklist.md: ✅ Present
   - testing-standards.md: ✅ Present

✅ Gate 2: Examples Migration
   - .ce/examples/: ✅ 14 files
   - Root examples/ removed: ✅ YES
   - Result: ✅ PASS

✅ Gate 3: PRPs Migration
   - .ce/PRPs/: ✅ Exists
   - Root PRPs/ removed: ✅ YES
   - Result: ✅ PASS

✅ Gate 4: Memories Domain
   - .serena/memories/: ✅ 24 files (framework + project blended)
   - .serena.old/ removed: ✅ YES
   - Result: ✅ PASS

✅ Gate 5: Critical Memories Present
   - All 3 critical files: ✅ Present
   - Result: ✅ PASS
```

**Overall**: ✅ 5/5 PASS (with corrected Gate 1 expectations)

---

## Root Cause Analysis

### Finding 1: Correct .SERENA Domain Architecture

**Original Misunderstanding**:
- Gate 1 expected framework memories at `.ce/.serena/memories/` (separate location)
- This violated the actual CE 1.1 design

**Correct Understanding**:
- Framework memories are **imported and blended** into `.serena/memories/` (root level)
- This creates a **unified domain** with framework + project memories
- Deduplication prevents duplicate files
- Both framework and project have read/write access

**Evidence**:
- All 6 framework memories present at `.serena/memories/`
- All 18 project memories present at `.serena/memories/`
- No duplicates (proper deduplication)
- Single canonical location for all memories

### Finding 2: init-project Working Correctly

**What init-project Does** (correctly):
1. Extracts framework boilerplate to `.ce/`
2. Extracts framework memories (6 files)
3. Extracts target project memories (18 files)
4. Blends & dedupes all 24 memories
5. Writes unified domain to `.serena/memories/` (root)

**Result**: ✅ Correct behavior (memories in canonical location)

### Finding 3: Minor Cleanup Issues

**Issue 1**: Root `PRPs/` directory persistence in iteration 2
- **Status**: Already fixed (cleanup successful in later runs)
- **Impact**: Minor (doesn't break functionality)
- **Cause**: init-project cleanup logic finalization

**Issue 2**: Gate 1 validation expected wrong location
- **Status**: Fixed in iteration-orchestrator.md
- **Impact**: Testing false negative
- **Root Cause**: Incorrect gate expectation (not init-project issue)

---

## Architecture Documentation

### .SERENA Domain Design (CE 1.1)

```
certinia-test-target/
├── .serena/
│   ├── memories/                    ← UNIFIED DOMAIN (canonical location)
│   │   ├── code-style-conventions.md (framework imported)
│   │   ├── task-completion-checklist.md (framework imported)
│   │   ├── testing-standards.md (framework imported)
│   │   ├── suggested-commands.md (framework imported)
│   │   ├── tool-usage-syntropy.md (framework imported)
│   │   ├── use-syntropy-tools-not-bash.md (framework imported)
│   │   │
│   │   ├── codebase-structure.md (project-specific)
│   │   ├── project-overview.md (project-specific)
│   │   ├── cwe78-prp22-*.md (project-specific)
│   │   ├── linear-*.md (project-specific)
│   │   ├── prp-*.md (project-specific)
│   │   └── ... (18 project-specific total)
│   │
│   └── project.yml
│
├── .ce/                             ← FRAMEWORK STRUCTURE
│   ├── .serena/                     (framework templates only)
│   ├── examples/
│   ├── PRPs/
│   ├── tools/
│   └── ... (boilerplate)
```

**Key Principles**:
- ✅ Framework memories **imported** into `.serena/memories/`
- ✅ Project memories **blended** with framework memories
- ✅ **Single canonical location**: `.serena/memories/` at root
- ✅ **Deduplication**: No duplicate files
- ✅ **Unified domain**: Framework + project accessible together

---

## Proposed Improvements

### Phase 1: Documentation (QUICK)

**Task 1.1: Document .SERENA Architecture**
- Create `.ce/SERENA-DOMAIN-ARCHITECTURE.md`
- Explain import and blend process
- Show file organization with examples
- Clarify framework vs project separation

**Task 1.2: Update Iteration Gates**
- ✅ DONE: Update Gate 1 definition in iteration-orchestrator.md
- Document correct expectations for future gates
- Add detailed gate validation logic

**Effort**: 30 minutes

---

### Phase 2: Validation Gate Refinement (MEDIUM)

**Task 2.1: Improve Gate 1 Validation Logic**
- Create parametric validation for critical framework memories
- Make list of required files configurable
- Add detection for optional vs required memories

**Task 2.2: Add Deduplication Verification Gate**
- Create Gate 6: Deduplication Check
- Verify no duplicate files across domain
- Report if framework and project files overlap

**Task 2.3: Add Statistics Reporting**
- Gate 4: Provide breakdown (X framework, Y project, Z total)
- Gate 5: Validate critical files from both framework and project

**Effort**: 1-2 hours

---

### Phase 3: init-project Enhancement (LONGER TERM)

**Task 3.1: Formalize Blend Process**
- Document exact blending algorithm (deduplication rules)
- Handle file conflicts (framework vs project)
- Define precedence (which overwrites which)

**Task 3.2: Add Blend Phase Logging**
- Log which framework files imported
- Log which project files preserved
- Log deduplication decisions
- Provide visibility into blend process

**Task 3.3: Cleanup Phase Enhancement**
- Ensure all legacy directories removed
- Verify no orphaned files
- Add cleanup validation

**Effort**: 2-3 hours

---

## Recommended Execution Path

### Immediate (This Session)
1. ✅ Update Gate 1 definition (DONE)
2. ✅ Fix root PRPs/ cleanup (DONE)
3. ✅ Document .serena architecture findings (THIS DOCUMENT)
4. 📝 Create serena-procedure.md (DONE)

### Follow-up Session 1 (1-2 hours)
1. Create `.ce/SERENA-DOMAIN-ARCHITECTURE.md`
2. Implement Phase 2 gate refinements
3. Re-run Iteration 3 with improved gates
4. Validate all 5+ gates pass

### Follow-up Session 2 (2-3 hours)
1. Enhance init-project blend logging
2. Formalize deduplication rules
3. Add comprehensive cleanup validation
4. Document algorithm in framework guides

---

## Success Criteria

**Phase 1 Completion** (This Session):
- ✅ Gate 1 corrected (framework memories at root)
- ✅ Cleanup issues resolved
- ✅ Architecture findings documented

**Phase 2 Completion** (Next Session):
- ✅ Gate 6: Deduplication Check passes
- ✅ Enhanced statistics reporting in all gates
- ✅ `.serena` domain architecture documented

**Phase 3 Completion** (Following Session):
- ✅ init-project blend process logged and visible
- ✅ Cleanup phase enhanced and validated
- ✅ All deduplication rules formalized

---

## Files to Create/Modify

**Create**:
- `.ce/SERENA-DOMAIN-ARCHITECTURE.md` - Architecture guide
- `.ce/orchestration/gate-6-deduplication.md` - New gate template
- `tmp/serena-procedure.md` - Analysis document (DONE)

**Modify**:
- `.claude/orchestrators/iteration-orchestrator.md` - Update all gates (PARTIALLY DONE)
- `.claude/commands/iteration.md` - Add gate 6 to documentation
- `.ce/INIT-PROJECT-ALGORITHM.md` - Document blend process (create new)

---

## References

**Related Documents**:
- `tmp/serena-procedure.md` - Detailed .serena domain analysis
- `tmp/iteration-2-report.md` - Iteration 2 test results
- `.claude/orchestrators/iteration-orchestrator.md` - Gate definitions
- `.claude/commands/iteration.md` - Iteration command documentation

**Related Iterations**:
- Iteration 2: Initial parallel gate validation test
- Iteration 3: Re-validate with corrected Gate 1
- Iteration 4+: Additional project testing (mlx-trading-pipeline, etc.)

---

## Summary

Iteration 2 testing successfully demonstrated:
1. ✅ **Parallel validation gates working** (5 gates executed simultaneously)
2. ✅ **init-project implementation correct** (framework memories properly imported)
3. ✅ **Architecture sound** (unified .serena domain with blend)
4. ⚠️  **Gate definitions needed refinement** (Gate 1 expectations corrected)

This PRP formalizes those findings and proposes phased improvements to documentation, validation, and process enhancement. The core functionality is working correctly; improvements are in visibility, validation, and documentation.

---

**Status**: Ready for Phase 1 implementation
**Effort Estimate**:
- Phase 1: ~30 min (documentation)
- Phase 2: ~2 hours (gate enhancement)
- Phase 3: ~3 hours (init-project enhancement)
- **Total**: ~5.5 hours

**Recommended Priority**: High (improves testing confidence and future project initialization)
