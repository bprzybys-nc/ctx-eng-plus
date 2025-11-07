# PRP-39 Implementation Plan: Fix PRPMoveStrategy Subdirectory Handling

## Overview

Fix PRPMoveStrategy to recursively process PRP files in subdirectories (executed/, feature-requests/, system/, templates/) instead of only processing root-level *.md files. This will increase PRP migration rate from 2% to 100%.

## Success Criteria

- [ ] PRPMoveStrategy processes all *.md files recursively
- [ ] Subdirectory structure preserved in target
- [ ] Unit tests validate recursive behavior
- [ ] E2E test shows 100% PRP migration (92/92 files)
- [ ] Cleanup phase succeeds (no unmigrated files warning)

## Phases

### Phase 1: Implement Recursive Glob

**Goal**: Change glob pattern from "*.md" to "**/*.md" with structure preservation

**Estimated Hours**: 0.5

**Complexity**: low

**Files Modified**:
- tools/ce/blending/strategies/simple.py

**Dependencies**: None

**Implementation Steps**:
1. Read current PRPMoveStrategy.execute() method (line 84)
2. Change `source_dir.glob("*.md")` to `source_dir.glob("**/*.md")`
3. Add logic to preserve subdirectory structure:
   - Calculate relative_path = prp_file.relative_to(source_dir)
   - If parent is executed/feature-requests, preserve as-is
   - Otherwise, classify by content to executed/ or feature-requests/
4. Ensure dest.parent.mkdir(parents=True, exist_ok=True)
5. Update moved/skipped counters

**Validation Gates**:
- [ ] Code compiles without syntax errors
- [ ] glob("**/*.md") pattern matches files recursively
- [ ] Structure preservation logic handles 3 cases: executed/, feature-requests/, other

**Conflict Notes**: None - single file change, no dependencies

---

### Phase 2: Add Recursive Glob Unit Tests

**Goal**: Create comprehensive unit tests for recursive glob behavior

**Estimated Hours**: 0.5

**Complexity**: low

**Files Modified**:
- tools/tests/test_prp_move_strategy.py (new file)

**Dependencies**: Phase 1

**Implementation Steps**:
1. Create test_prp_move_strategy.py
2. Add test_recursive_glob() - verify **/*.md finds nested files
3. Add test_preserve_structure() - executed/ PRPs → target/executed/
4. Add test_mixed_structure() - root + subdirs both processed
5. Add test_templates_excluded() - optionally skip templates/
6. Add test_system_prps_preserved() - system/ PRPs stay in system/
7. Add test_hash_deduplication() - skip identical files in target

**Validation Gates**:
- [ ] All 6 unit tests pass
- [ ] Test coverage includes all 3 structure cases
- [ ] Tests validate 100% file discovery (no files missed)

**Conflict Notes**: None - new test file

---

### Phase 3: E2E Validation

**Goal**: Run full init-project E2E test and verify 100% PRP migration

**Estimated Hours**: 0.5

**Complexity**: low

**Files Modified**:
- None (testing only)

**Dependencies**: Phase 1, Phase 2

**Implementation Steps**:
1. Reset test target: git reset --hard main && git clean -fd
2. Create test branch: git checkout -b prp39-validation
3. Run init-project: uv run python -m ce.init_project /path/to/test-target
4. Verify blend phase output shows "92 files" processed (not 2)
5. Verify cleanup phase succeeds (no "unmigrated files" error)
6. Check target structure:
   - .ce/PRPs/executed/ has 20+ files
   - .ce/PRPs/feature-requests/ has 65+ files
   - .ce/PRPs/system/ has 3+ files
7. Count migrated PRPs: find .ce/PRPs -name "*.md" | wc -l (expect 92)

**Validation Gates**:
- [ ] Blend phase shows "prps (92 files)" in output
- [ ] Cleanup phase exits with code 0
- [ ] Target .ce/PRPs/ contains 92 .md files
- [ ] Source PRPs/ directory contains 0-2 .md files (only templates remain)

**Conflict Notes**: None - read-only validation

---
