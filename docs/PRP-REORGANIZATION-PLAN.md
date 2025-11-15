# PRP Reorganization Plan

**Status:** Design Phase (Ready for Implementation)
**Date:** 2025-11-15
**Based on:** Domain Analysis & Complexity Metrics Report
**Effort:** 2-3 hours implementation

---

## Current Problem

**Feature requests scattered with no organization:**

```
PRPs/feature-requests/
├── PRP-30.1.1-syntropy-mcp-tool-management.md    ← MVP
├── PRP-31-generate-prp-linting-fix.md            ← PROD, depends 30
├── PRP-33-syntropy-integration.md                ← PROD, depends 0,24,25,26
├── PRP-34-blending-framework.md                  ← PROD, depends 33
├── PRP-34.1.1-core-blending.md                   ← PROD, depends 34
├── PRP-34.2.1-detection-module.md                ← PROD, depends 34
├── PRP-34.2.2-classification.md                  ← PROD, depends 34
├── PRP-34.2.3-cleanup.md                         ← PROD, depends 34
├── PRP-34.2.4-settings-blending.md               ← PROD, depends 34
├── PRP-34.2.5-simple-operations.md               ← PROD, depends 34
└── [26 more PRPs, unsorted]
```

**Issues:**

1. No visual distinction between MVP and PROD
2. Dependency relationships hidden in file content
3. Batch PRP generation cannot target MVP-only features
4. Parallelization opportunities not obvious
5. New contributors unclear about execution order

---

## Proposed Solution

### New Structure

```
PRPs/
├── executed/                           (existing, unchanged)
│   ├── PRP-0-*.md through PRP-42-*.md
│   ├── [57 completed PRPs]
│   └── README.md
│
├── feature-requests/                   (restructured)
│   ├── README.md                       NEW
│   ├── mvp/                            NEW
│   │   ├── ROADMAP.md                  NEW
│   │   └── PRP-30.1.1-*.md
│   │
│   ├── prod/                           NEW
│   │   ├── DEPENDENCIES.md             NEW (dependency graph)
│   │   ├── BATCH-GENERATION-PLAN.md    NEW (batch execution guide)
│   │   │
│   │   ├── stage-1-foundations/        NEW
│   │   │   ├── PRP-33-syntropy-integration.md
│   │   │   └── [foundation PRPs]
│   │   │
│   │   ├── stage-2-core-modules/       NEW
│   │   │   ├── PRP-34-blending-framework.md
│   │   │   ├── PRP-34.1.1-core-blending.md
│   │   │   ├── PRP-34.2.1-detection.md
│   │   │   ├── PRP-34.2.2-classification.md
│   │   │   ├── PRP-34.2.3-cleanup.md
│   │   │   ├── PRP-34.2.4-settings-blending.md
│   │   │   └── PRP-34.2.5-simple-operations.md
│   │   │
│   │   └── stage-3-advanced/           NEW
│   │       ├── PRP-31-linting-fix.md
│   │       ├── PRP-35-cli-refactoring.md
│   │       └── [advanced features]
│   │
│   └── archive/                        NEW (optional)
│       └── [deprecated/superseded PRPs]
│
└── templates/                          (existing, unchanged)
    └── [PRP templates]
```

---

## MVPs vs PROD Categorization

### MVP Criteria

A feature request qualifies as MVP if **ALL** conditions are met:

1. **No Dependencies:** Does not depend on other PRPs
2. **Low Effort:** ≤ 20 hours estimated
3. **Low-Medium Complexity:** CogC ≤ 60, DepC ≤ 15
4. **Standalone:** Can be executed in isolation
5. **No Circular Dependencies:** Does not create blocking chain

### Current MVP Candidates

Only **1 PRP** meets MVP criteria:

| PRP ID | Title | Effort | Dependencies | Status |
|--------|-------|--------|--------------|--------|
| **PRP-30.1.1** | Syntropy MCP Tool Management | 2.5h | None | ✓ MVP |

**Why only 1?**

- Most feature requests (35 PRPs) depend on foundational PRPs
- Typical pattern: PRP-X → PRP-X.1 → PRP-X.2.1 → PRP-X.2.2, etc.
- Batch organization reduces this over time

---

## PROD Organization by Stage

### Stage 1: Foundational Frameworks (3-5 PRPs)

**Purpose:** Set up core infrastructure that other stages depend on

**PRPs:**

- **PRP-33-syntropy-integration** (8h)
  - Syntropy MCP layer for all CLI commands
  - Integrates with LLM backends
  - Blocks: All PROD PRPs (directly or indirectly)

- **PRP-0-initialization** (reference, not re-execute)
  - Framework initialization patterns
  - Used as template for other stages

**Execution Strategy:** Sequential (no parallelization possible)
**Critical Path:** PRP-33 must complete before any stage 2 PRPs

**Batch Generation:**

```bash
/batch-gen-prp PROD-STAGE-1-ROADMAP.md
# Output: PRP-43.1.1 (Syntropy integration)
# Time: ~8 hours
```

### Stage 2: Core Modules (6 PRPs)

**Purpose:** Implement main framework features (blending, validation)

**PRPs:**

1. **PRP-34-blending-framework** (master orchestrator)
   - Sets up blending system architecture
   - Blocks: All blending submodules (34.1.1, 34.2.1-34.2.5)

2. **PRP-34.1.1-core-blending** (4h, depends: 34)
   - Core file detection and classification
   - Used by all 34.2.x modules

3. **PRP-34.2.1-detection-module** (1.5h, depends: 34.1.1)
4. **PRP-34.2.2-classification-module** (1.5h, depends: 34.1.1)
5. **PRP-34.2.3-cleanup-module** (1h, depends: 34.1.1)
6. **PRP-34.2.4-settings-blending** (2h, depends: 34.1.1)
7. **PRP-34.2.5-simple-operations** (1.5h, depends: 34.1.1)

**Execution Strategy:** Parallel (after 34.1.1 completes)

```
PRP-34
  └─ PRP-34.1.1 (sequential, 4h)
       └─ PRP-34.2.1 ─┐
          PRP-34.2.2 ─┼─ Parallel execution (1-2h total)
          PRP-34.2.3 ─┤
          PRP-34.2.4 ─┤
          PRP-34.2.5 ─┘
```

**Parallelization Benefit:**

- Sequential: 4h + 1.5h + 1.5h + 1h + 2h + 1.5h = 11.5 hours
- Parallel: 4h + 2h (max of submodules) = 6 hours
- **Savings: 48% time reduction**

**Batch Generation:**

```bash
/batch-gen-prp PROD-STAGE-2-ROADMAP.md
# Output:
#   PRP-43.2.1 (PRP-34)
#   PRP-43.2.2 (PRP-34.1.1)
#   PRP-43.2.3 (PRP-34.2.1, PRP-34.2.2, PRP-34.2.3, PRP-34.2.4, PRP-34.2.5)
# Time: ~6 hours parallel
```

### Stage 3: Advanced Features (4+ PRPs)

**Purpose:** Add advanced tooling and optimizations

**PRPs:**

1. **PRP-31-generate-prp-linting-fix** (2h, depends: 30, 3)
   - Fix PRP generator linting issues
   - Improves PRP quality checks

2. **PRP-35-cli-refactoring** (estimated, depends: cli_handlers.py refactor)
   - Split monolithic CLI handler
   - Improves maintainability

3. **PRP-36-vacuum-optimization** (estimated, depends: 34)
   - Advanced cleanup strategies
   - Removes orphaned files

4. **[Other advanced features]**

**Execution Strategy:** Mostly sequential (some parallelization within groups)

**Batch Generation:**

```bash
/batch-gen-prp PROD-STAGE-3-ROADMAP.md
# Output: Stage 3 PRPs
# Time: ~5-8 hours (less parallelizable than stage 2)
```

---

## Implementation Steps

### Step 1: Create Directory Structure (15 minutes)

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/PRPs/feature-requests

# Create new directories
mkdir -p mvp
mkdir -p prod/stage-1-foundations
mkdir -p prod/stage-2-core-modules
mkdir -p prod/stage-3-advanced
mkdir -p archive

# Verify
ls -la | grep "^d"
```

### Step 2: Categorize and Move PRPs (30 minutes)

**MVP (1 file):**

```bash
# Move to mvp/
mv PRP-30.1.1-syntropy-mcp-tool-management.md mvp/
```

**Stage 1: Foundations (1-2 files):**

```bash
# Move to prod/stage-1-foundations/
mv PRP-33-syntropy-mcp-integration*.md prod/stage-1-foundations/
mv PRP-0-initialization*.md prod/stage-1-foundations/ # If not in executed/
```

**Stage 2: Core Modules (6 files):**

```bash
# Move to prod/stage-2-core-modules/
mv PRP-34-blending-framework*.md prod/stage-2-core-modules/
mv PRP-34.1*.md prod/stage-2-core-modules/
mv PRP-34.2*.md prod/stage-2-core-modules/
```

**Stage 3: Advanced (4+ files):**

```bash
# Move to prod/stage-3-advanced/
mv PRP-31-*.md prod/stage-3-advanced/
mv PRP-35-*.md prod/stage-3-advanced/
mv PRP-36-*.md prod/stage-3-advanced/
```

**Archive: Deprecated/Superseded (remaining files):**

```bash
# Move old/redundant PRPs
mv PRP-*-OLD*.md archive/ 2>/dev/null || true
mv INIT-*.md archive/ 2>/dev/null || true

# Count remaining
ls -1 | wc -l  # Should be 0 (all organized)
```

### Step 3: Create Documentation Files (45 minutes)

#### mvp/ROADMAP.md

```markdown
# MVP Feature Roadmap

Quick start to Context Engineering fundamentals.

## Execution Plan

| PRP | Title | Effort | Status |
|-----|-------|--------|--------|
| PRP-30.1.1 | Syntropy MCP Tool Management | 2.5h | Ready |

## Quick Start

1. Extract ce-foundation.xml
2. Execute PRP-30.1.1
3. Ready for basic CE usage

## Time to Completion

**Sequential:** 2.5 hours
**Parallel:** N/A (single PRP)

## Next Steps

Once MVP is complete, proceed to `../prod/stage-1-foundations/` for full framework.

---

Generated from domain analysis on 2025-11-15
```

#### prod/DEPENDENCIES.md

```markdown
# Production PRP Dependency Graph

## Stage 1: Foundations

**PRP-33** (Syntropy Integration)
- Dependencies: PRP-0, PRP-24, PRP-25, PRP-26
- Duration: 8 hours
- Critical Path: YES (blocks all stage 2+ PRPs)

## Stage 2: Core Modules

```

PRP-34 (Blending Framework)
  └─ PRP-34.1.1 (Core Blending, 4h)
      ├─ PRP-34.2.1 (Detection, 1.5h)     ─┐
      ├─ PRP-34.2.2 (Classification, 1.5h)─┼─ Parallel (2h max)
      ├─ PRP-34.2.3 (Cleanup, 1h)         ─┤
      ├─ PRP-34.2.4 (Settings, 2h)        ─┤
      └─ PRP-34.2.5 (Simple Ops, 1.5h)    ─┘

```

**Total Time:**
- Sequential: 11.5 hours
- Parallel: 6 hours
- Savings: 5.5 hours (48% reduction)

## Stage 3: Advanced Features

```

PRP-31 (Linting Fix, 2h)

- Dependencies: PRP-30, PRP-3
- Can run after stage 2

PRP-35 (CLI Refactor, est. 6h)

- Dependencies: cli_handlers.py refactor
- Independent of other stage 3 PRPs

PRP-36 (Vacuum Optimization, est. 3h)

- Dependencies: PRP-34 (core modules)

```

## Execution Order

1. **Stage 1:** Execute PRP-33 (8h, sequential)
2. **Stage 2:** Execute PRP-34 series (6h, parallel within stage)
3. **Stage 3:** Execute stage 3 PRPs (5-8h, mixed execution)

**Total Project Duration:**
- Sequential: 35 hours
- With parallelization: 20 hours
- Savings: 43% time reduction

## Critical Path

PRP-33 → PRP-34 → PRP-34.1.1 → [PRP-34.2.1-34.2.5 parallel] → Stage 3

**On Critical Path:** PRP-33, PRP-34, PRP-34.1.1

---

Generated from domain analysis on 2025-11-15
```

#### prod/BATCH-GENERATION-PLAN.md

```markdown
# Batch PRP Generation Plan

## Overview

Decompose Stage 1, 2, and 3 PRPs into parallel batches using /batch-gen-prp.

## Phase 1: Generate Stage 1 Foundations

**Command:**
```bash
/batch-gen-prp PROD-STAGE-1-ROADMAP.md
```

**Output:**

- PRP-43.1.1 (Syntropy Integration)

**Time:** 2-3 hours (generation)
**Execution:** 8 hours

**Prerequisites:**

- PRP-0, PRP-24, PRP-25, PRP-26 (should be in executed/ from reference)

## Phase 2: Generate Stage 2 Core Modules

**Command:**

```bash
/batch-gen-prp PROD-STAGE-2-ROADMAP.md
```

**Output (Parallel Batches):**

- Batch 1: PRP-43.2.1 (PRP-34 Blending Framework)
- Batch 2: PRP-43.2.2 (PRP-34.1.1 Core Blending)
- Batch 3: PRP-43.2.3a-43.2.3e (PRP-34.2.1-34.2.5 in parallel)

**Time:** 2-3 hours (generation)
**Execution:** 6 hours parallel (4h + 2h max)

**Dependencies:**

- Batch 1 → Batch 2 → Batch 3

**Parallelization within Batch 3:**

```
PRP-43.2.3a (Detection)     ─┐
PRP-43.2.3b (Classification)─┼─ Execute in parallel (2h total)
PRP-43.2.3c (Cleanup)       ─┤
PRP-43.2.3d (Settings)      ─┤
PRP-43.2.3e (Simple Ops)    ─┘
```

## Phase 3: Generate Stage 3 Advanced Features

**Command:**

```bash
/batch-gen-prp PROD-STAGE-3-ROADMAP.md
```

**Output:**

- PRP-43.3.1 (Linting Fix)
- PRP-43.3.2 (CLI Refactoring)
- PRP-43.3.3 (Vacuum Optimization)

**Time:** 2-3 hours (generation)
**Execution:** 5-8 hours

**Dependencies:** Mostly independent (can run in parallel)

## Total Timeline

```
Day 1 (Monday):
  - Morning: Phase 1 generation (2h)
  - Day: Phase 1 execution (8h)

Day 2 (Tuesday):
  - Morning: Phase 2 generation (2h)
  - Day: Phase 2 execution (6h parallel)

Day 3 (Wednesday):
  - Morning: Phase 3 generation (2h)
  - Day: Phase 3 execution (8h)

Total: 3 days (vs 5+ days sequential)
Savings: 40% time reduction
```

## Batch Execution Checklist

### Pre-Execution

- [ ] All stages 1-2 PRPs in prod/ subdirectories
- [ ] DEPENDENCIES.md verified and accurate
- [ ] MVP PRPs archived or excluded
- [ ] .serena/memories updated with latest patterns

### Phase 1 Execution

- [ ] PRP-43.1.1 generated successfully
- [ ] Generated PRP includes all dependencies
- [ ] Linear issue created automatically
- [ ] Start execution in worktree

### Phase 2 Execution

- [ ] PRP-43.2.1 generated and ready
- [ ] PRP-43.2.2 generated (depends PRP-43.2.1)
- [ ] PRP-43.2.3a-43.2.3e generated
- [ ] Parallel execution started
- [ ] Monitor via heartbeat files (30s polling)

### Phase 3 Execution

- [ ] PRP-43.3.1, 43.3.2, 43.3.3 generated
- [ ] Execute in dependency order
- [ ] Merge completed PRPs to main
- [ ] Update PRPs/executed/ with completed work

---

Generated from domain analysis on 2025-11-15

```

#### prod/README.md

```markdown
# Production PRPs

Advanced Context Engineering framework features organized by stage.

## Structure

```

stage-1-foundations/    Core infrastructure PRPs
stage-2-core-modules/   Main blending and validation modules
stage-3-advanced/       Advanced features and optimizations

```

## Execution Guide

1. **Start with Stage 1:** Foundation PRPs must complete first
2. **Execute Stage 2:** Mostly parallelizable within stage
3. **Execute Stage 3:** Independent advanced features

See `DEPENDENCIES.md` for full dependency graph.
See `BATCH-GENERATION-PLAN.md` for parallel execution strategy.

---

Generated from domain analysis on 2025-11-15
```

#### feature-requests/README.md

```markdown
# Feature Requests

Pending implementation tasks for Context Engineering framework.

## Organization

```

mvp/                    Single MVP feature (quick start)
prod/                   Production features (3 stages)
templates/              PRP templates
archive/                Deprecated/superseded PRPs

```

## Quick Start

1. **New to CE?** Start with `mvp/ROADMAP.md`
2. **Implementing full framework?** See `prod/DEPENDENCIES.md`
3. **Using batch generation?** See `prod/BATCH-GENERATION-PLAN.md`

## Statistics

| Category | Count | Total Hours |
|----------|-------|------------|
| MVP | 1 | 2.5h |
| PROD Stage 1 | 1 | 8h |
| PROD Stage 2 | 6 | 11.5h (6h parallel) |
| PROD Stage 3 | 4+ | 8h |
| **TOTAL** | **12+** | **30h** |

---

Generated from domain analysis on 2025-11-15
```

### Step 4: Create PROD Stage Roadmap Files (30 minutes)

#### prod/PROD-STAGE-1-ROADMAP.md

```markdown
# Production Stage 1: Foundational Frameworks

## Goal
Set up core infrastructure that all other PROD stages depend on.

## Phases

### Phase 1: Syntropy Integration

**PRP:** PRP-33-syntropy-mcp-integration
**Goal:** Integrate with Syntropy MCP layer for LLM-powered operations
**Estimated Hours:** 8
**Complexity:** HIGH
**Files Modified:** tools/ce/cli_handlers.py, tools/ce/executors/
**Dependencies:** PRP-0, PRP-24, PRP-25, PRP-26
**Blocks:** All Stage 2 and Stage 3 PRPs
**Implementation Steps:**
1. Set up Syntropy client integration
2. Implement MCP adapter layer
3. Add LLM endpoint handling
4. Write integration tests
5. Update CLI documentation

**Validation Gates:**
- All imports resolve
- Integration tests pass (test_mcp_adapter.py)
- Example LLM calls work end-to-end

---

## Batch Generation

This stage is ideal for batch PRP generation:

```bash
/batch-gen-prp PROD-STAGE-1-ROADMAP.md
# Output: PRP-43.1.1 (Syntropy Integration)
```

---

Generated from domain analysis on 2025-11-15

```

#### prod/PROD-STAGE-2-ROADMAP.md

```markdown
# Production Stage 2: Core Modules

## Goal
Implement main framework features (blending, validation) with parallelizable submodules.

## Phases

### Phase 1: Blending Framework Setup
**PRPs:** PRP-34, PRP-34.1.1
**Total Hours:** 4h
**Dependencies:** PRP-33 (Stage 1)

### Phase 2: Blending Submodules (Parallel)
**PRPs:** PRP-34.2.1 through PRP-34.2.5
**Total Hours:** 7.5h (sequentially) → 2h (parallel after 34.1.1)
**Dependencies:** PRP-34.1.1
**Parallelizable:** YES (all depend only on 34.1.1)

## Batch Generation

```bash
/batch-gen-prp PROD-STAGE-2-ROADMAP.md
# Output:
#   Batch 1: PRP-43.2.1 (PRP-34)
#   Batch 2: PRP-43.2.2 (PRP-34.1.1)
#   Batch 3: PRP-43.2.3a-e (PRP-34.2.1-34.2.5 parallel)
```

## Timeline

- Sequential: 11.5 hours
- Parallel: 6 hours (4h + 2h max)
- Savings: **5.5 hours (48%)**

---

Generated from domain analysis on 2025-11-15

```

### Step 5: Verify Reorganization (15 minutes)

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/PRPs/feature-requests

# Verify structure
tree -L 2

# Count files
echo "MVP PRPs: $(ls -1 mvp/*.md 2>/dev/null | wc -l)"
echo "PROD Stage 1: $(ls -1 prod/stage-1-foundations/*.md 2>/dev/null | wc -l)"
echo "PROD Stage 2: $(ls -1 prod/stage-2-core-modules/*.md 2>/dev/null | wc -l)"
echo "PROD Stage 3: $(ls -1 prod/stage-3-advanced/*.md 2>/dev/null | wc -l)"

# Verify no files left in root
ls -1 *.md 2>/dev/null | wc -l  # Should be 0 (all moved)
```

---

## Integration with Batch PRP Generation

### Current `/batch-gen-prp` Workflow

```bash
# Before reorganization:
/batch-gen-prp FEATURE-PLAN.md
# Problem: Cannot distinguish MVP from PROD, unclear parallelization

# After reorganization:
/batch-gen-prp PRPs/feature-requests/mvp/ROADMAP.md
/batch-gen-prp PRPs/feature-requests/prod/PROD-STAGE-1-ROADMAP.md
/batch-gen-prp PRPs/feature-requests/prod/PROD-STAGE-2-ROADMAP.md
/batch-gen-prp PRPs/feature-requests/prod/PROD-STAGE-3-ROADMAP.md
# Benefit: Clear stage boundaries, automatic parallelization hints
```

### Enhanced Batch Execution

```bash
# Execute MVP (quick start)
/batch-exe-prp --batch mvp-gen-1

# Execute full PROD pipeline
/batch-exe-prp --batch prod-stage-1 --wait
/batch-exe-prp --batch prod-stage-2 --parallel
/batch-exe-prp --batch prod-stage-3
```

---

## Success Metrics

### After Implementation

1. **Clarity Improvement**
   - MVP vs PROD distinction: Immediate visual (directory structure)
   - Dependency clarity: All captured in DEPENDENCIES.md
   - Execution order: Explicit in stage subdirectories

2. **Process Improvement**
   - Batch generation targets: 4 clear entry points (mvp, stage-1, 2, 3)
   - Parallelization visibility: Stage 2 shows 48% time savings
   - New contributor onboarding: <5 min to understand roadmap

3. **Execution Efficiency**
   - Sequential execution: 35 hours
   - Parallel execution: ~20 hours (with all stages parallelized)
   - Savings: 43% time reduction

---

## File Organization Summary

| Component | Before | After | Status |
|-----------|--------|-------|--------|
| MVP PRPs | 1 mixed in | mvp/ | Organized |
| PROD PRPs | 35 mixed in | prod/stage-*/ | Organized |
| Dependency Graph | Hidden in files | DEPENDENCIES.md | Explicit |
| Batch Plan | Missing | BATCH-GENERATION-PLAN.md | Created |
| Roadmaps | None | mvp/ROADMAP.md + stage roadmaps | Created |

---

## Related Documents

- `/docs/DOMAIN-ANALYSIS-METRICS.md` - Categorization basis
- `/docs/REPOMIX-PACKAGE-STRUCTURE.md` - Foundation/Production packages

---

**Status:** Ready for Implementation
**Effort:** 2-3 hours (mostly manual file movement and doc creation)
**Risk:** Low (restructuring only, no code changes)
**Benefit:** Clear roadmap, 43% time savings with parallelization
