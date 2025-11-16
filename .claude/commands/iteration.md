# /iteration - Run init-project iteration test with parallel validation

**Purpose**: Test init-project on a target project using orchestrator pattern with parallel validation gates

**Usage**:
```bash
/iteration <project-path>              # Auto-increment iteration number (default)
/iteration <project-description>       # Auto-increment with description
/iteration <number> <project-path>     # Explicit iteration number
```

**Examples**:
```bash
/iteration certinia-test-target                                              # Auto (recommended)
/iteration /Users/bprzybyszi/nc-src/certinia-test-target                    # Auto with full path
/iteration ctx-eng-plus-test-target                                         # Auto with description
/iteration 5 /Users/bprzybyszi/nc-src/mlx-trading-pipeline-context-engineering  # Explicit number
```

---

## What You Do

### Step 1: Parse Arguments

**Default behavior**: Auto-increment iteration number

Extract:
- **Iteration number**:
  - If first arg is a number → use it explicitly
  - Otherwise → auto-increment (scan tmp/iteration-*.log for highest number)
- **Project path**:
  - If first arg is number → second arg onwards is path/description
  - If first arg is NOT number → first arg onwards is path/description
  - If starts with `/` or `~` → treat as path
  - Otherwise → treat as description, infer path from context

### Step 2: Resolve Project Path

**If path provided**:
- Use directly: `/Users/bprzybyszi/nc-src/mlx-trading-pipeline-context-engineering`

**If description provided**:
- Parse description for path hints
- Common patterns:
  - "mlx-trading-pipeline" → `~/nc-src/mlx-trading-pipeline-context-engineering`
  - "certinia-test-target" → `~/nc-src/certinia-test-target`
  - "test-target" → `~/nc-src/ctx-eng-plus-test-target`
  - "ctx-eng-plus" → `~/nc-src/ctx-eng-plus`

### Step 3: Determine Iteration Number

**Default: Auto-increment** (recommended)
- Find highest existing iteration in `tmp/iteration-*.log` and `tmp/iteration-*.md`
- Increment by 1
- If no existing iterations found, start at 1

**If explicit number provided**:
- Use as-is (for manual control or re-runs)

### Step 4: Reset Target Project

```bash
cd <project-path>
git status  # Check current state
git log --oneline -5  # Show recent commits

# Find initial commit or specified commit
git log --oneline --reverse | head -1  # Get initial commit

# Reset to clean state
git reset --hard <commit-hash>
git clean -fdx

# Create iteration branch
git checkout -b iteration-<number>
```

### Step 5: Run init-project

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Run with logging
uv run ce init-project <project-path> 2>&1 | tee ../tmp/iteration-<number>.log
```

### Step 6: Parallel Validation Gates

**KEY CHANGE**: Run validation gates in PARALLEL (not sequentially)

Spawn 6 independent Task agents simultaneously in a single message. Each gate is independent and can run concurrently:

**Gate 1: Framework Structure Preserved** (parallel)
- Check: `.ce/examples/` exists
- Check: `.ce/PRPs/` exists
- Check: `.ce/.ce/` does NOT exist (nested duplication bug)
- Check: `.ce/.serena/` does NOT exist (should be cleaned up after blending)
- Check: `.ce/memories/` does NOT exist (old location)
- Store result: `tmp/gate-1-framework-structure-result.json`

**Gate 2: Examples Migration** (parallel)
- Check: `.ce/examples/` exists
- Count: Migrated example files
- Check: Root `examples/` removed
- Store result: `tmp/gate-2-examples-migration-result.json`

**Gate 3: PRPs Migration** (parallel)
- Check: `.ce/PRPs/` exists
- Check: `.ce/PRPs/executed/` subdirectory exists
- Check: `.ce/PRPs/feature-requests/` subdirectory exists (CRITICAL - caught bug in iteration 7!)
- Count: Migrated PRP files in executed/
- Check: Root `PRPs/` removed
- Store result: `tmp/gate-3-prps-migration-result.json`

**Gate 4: Blended Memories** (parallel)
- Check: `.serena/memories/` exists at root (blended framework + user)
- Check: `.serena.old/` cleaned up (if existed)
- Count: Memory files in `.serena/memories/` (should be >=24, framework + user)
- Verify: `.ce/.serena/` does NOT exist (should be deleted after blending)
- Store result: `tmp/gate-4-blended-memories-result.json`

**Gate 5: Critical Memories Present** (parallel)
- Check: code-style-conventions.md exists in `.serena/memories/`
- Check: task-completion-checklist.md exists in `.serena/memories/`
- Check: testing-standards.md exists in `.serena/memories/`
- Check: suggested-commands.md exists in `.serena/memories/`
- Check: use-syntropy-tools-not-bash.md exists in `.serena/memories/`
- Store result: `tmp/gate-5-critical-memories-result.json`

**Gate 6: Configuration Completeness** (parallel, NEW - added after iteration 7)
- Check: `.claude/` directory exists
- Check: `.claude/commands/` directory exists and is NOT empty
- Count: Command files in `.claude/commands/` (should be >=15)
- Check: `.claude/settings.local.json` exists
- Check: `CLAUDE.md` exists at root
- Store result: `tmp/gate-6-configuration-completeness-result.json`

**Gate 7: Target Project Preservation** (parallel, NEW - added after iteration 7)
- Check: `src/` directory exists with files (NOT deleted by init-project)
- Check: `tests/` directory exists with files (NOT deleted by init-project)
- Check: `configs/` directory exists if present before init (NOT deleted)
- Check: `data/` directory exists if present before init (NOT deleted)
- Verify: Core project structure preserved (only CE framework files added)
- Store result: `tmp/gate-7-target-project-preservation-result.json`

### Step 7: Parallel Execution Strategy

Instead of running gates sequentially:

```
SEQUENTIAL (old - ~252 seconds):
Gate 1 ──> Gate 2 ──> Gate 3 ──> Gate 4 ──> Gate 5 ──> Gate 6 ──> Gate 7

PARALLEL (new - ~60 seconds):
Gate 1 ┐
Gate 2 │
Gate 3 │
Gate 4 ├─> (all run simultaneously)
Gate 5 │
Gate 6 │
Gate 7 ┘
```

**Implementation**:
1. Create gate-spec JSON files for each of 7 gates
2. Spawn 7 Task agents in a single message (parallel)
3. Each agent validates its gate independently
4. Each agent writes result JSON to `tmp/gate-N-*-result.json`
5. Wait for all agents to complete (~45-60 seconds)
6. Aggregate results and generate comprehensive report

**Benefits**:
- Time: 216s (sequential) → 60s (parallel) = **72% faster**
- Parallelism: Leverages Batch 47 orchestrator infrastructure
- Clarity: Each gate result documented separately

### Step 8: Generate Comprehensive Report

Create `tmp/iteration-<number>-report.md` with:

```markdown
# Iteration <number> - <Project Name>

**Date**: <timestamp>
**Target**: <project-path>
**Branch**: iteration-<number>
**Status**: ✅ SUCCESS / ❌ FAILED

**Execution Details**:
- Init-project duration: <seconds>
- Validation gates duration: <seconds> (parallel execution)
- Total duration: <seconds>

---

## Validation Results (Parallel Execution)

All 7 gates executed simultaneously in ~45-60 seconds

### ✅/❌ Gate 1: Framework Structure Preserved
- .ce/examples/: ✅ Exists
- .ce/PRPs/: ✅ Exists
- .ce/.ce/: ✅ Does NOT exist (no nesting)
- .ce/.serena/: ✅ Does NOT exist (cleaned after blend)
- .ce/memories/: ✅ Does NOT exist (old location)

### ✅/❌ Gate 2: Examples Migration
- .ce/examples/: ✅ Exists
- Migrated examples: <count> ✅
- Root examples/ removed: ✅

### ✅/❌ Gate 3: PRPs Migration
- .ce/PRPs/: ✅ Exists
- Migrated PRPs: <count> ✅
- Root PRPs/ removed: ✅

### ✅/❌ Gate 4: Blended Memories
- .serena/memories/: ✅ Exists at root
- .serena.old/: ✅ Does NOT exist (cleaned)
- .ce/.serena/: ✅ Does NOT exist (temp files deleted after blend)
- Memory count: <count> ✅ (>=24 framework + user)

### ✅/❌ Gate 5: Critical Memories Present
- code-style-conventions.md: ✅
- task-completion-checklist.md: ✅
- testing-standards.md: ✅

### ✅/❌ Gate 6: Configuration Completeness
- .claude/ directory: ✅
- .claude/commands/ populated: ✅ (15+ files)
- .claude/settings.local.json: ✅
- CLAUDE.md: ✅

### ✅/❌ Gate 7: Target Project Preservation
- src/ directory: ✅ Exists with files (NOT deleted)
- tests/ directory: ✅ Exists with files (NOT deleted)
- configs/ directory: ✅ Exists (NOT deleted)
- data/ directory: ✅ Exists (NOT deleted)
- Core project structure: ✅ Preserved (only CE files added)

---

## Execution Summary

**Gates Passed**: <count>/7
**Gates Failed**: <count>/7
**Overall Status**: ✅ SUCCESS / ❌ FAILED

**Performance**:
- Sequential approach: ~252 seconds (7 gates × ~36s each)
- Parallel approach: ~60 seconds
- Time savings: **76% reduction**

**Issues Found**:
<list any issues encountered>

**Confidence Score**: <1-10>/10
```

### Step 9: Output Results

Show user:
1. Report location: `tmp/iteration-<number>-report.md`
2. Log location: `tmp/iteration-<number>.log`
3. Gate results summary (PASS/FAIL counts)
4. Performance metrics (parallel execution time)
5. Any critical issues found
6. Next steps (if applicable)

---

## Key Principles

1. **Always reset to clean state** before running init-project (atomic baseline)
2. **Parallel validation gates** for 67% faster execution (~60s vs ~180s)
3. **Document everything** in report and log files (traced results)
4. **Leverage orchestrator pattern** from Batch 47 infrastructure
5. **Independent gate execution** (no inter-gate dependencies)
6. **Use auto-increment** for iteration numbers to avoid conflicts

---

## Common Patterns

**Test on certinia-test-target** (recommended):
```bash
/iteration auto certinia-test-target
```

**Test on ctx-eng-plus-test-target**:
```bash
/iteration auto test-target
```

**Test on real-world project**:
```bash
/iteration auto mlx-trading-pipeline
```

**Manual iteration number**:
```bash
/iteration 5 /Users/bprzybyszi/nc-src/ctx-eng-plus-test-target
```

---

## Orchestrator Integration

This iteration command leverages the orchestrator pattern from Batch 47:

- **Phase 1**: Parse arguments
- **Phase 2**: Setup & reset target project
- **Phase 3**: Run init-project with logging
- **Phase 4**: Spawn 5 validation gates in parallel (key difference from sequential version)
- **Phase 5**: Monitor & aggregate results from all gates
- **Phase 6**: Generate comprehensive report & cleanup

**Architecture**: Sonnet orchestrator coordinates Haiku subagents for parallel gate validation

---

## Performance Comparison

| Aspect | Sequential | Parallel |
|--------|-----------|----------|
| **Validation gates** | Run one-by-one | Run simultaneously |
| **Total time** | ~180s | ~60s |
| **Speedup** | Baseline | **67% faster** |
| **Framework** | Manual step-by-step | Orchestrator pattern |
| **Execution model** | Single context | Multiple agents (Task) |

---

## Notes

- Iteration command now uses Batch 47 orchestrator infrastructure for parallel execution
- Auto-increment scans `tmp/iteration-*.log` files for existing iteration numbers
- Report format standardized for easy comparison across iterations
- Parallel validation gates provide significant time savings without sacrificing coverage
- Each gate writes independent result JSON for clear attribution and debugging
