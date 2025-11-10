# Subagent Templates - Directory Guide

**Framework**: Unified Batch Command Framework
**Orchestrator**: Sonnet (coordination)
**Subagents**: Haiku 4.5 (execution)

---

## Quick Reference: Choose Your Subagent

| File | Purpose | When Used | Output |
|------|---------|-----------|--------|
| **generator-subagent.md** | Parse plans → generate PRPs | `/batch-gen-prp` command | Individual PRP files + Linear issues |
| **executor-subagent.md** | Execute PRP steps → modify files | `/batch-exe-prp` command | Code changes + git commits |
| **reviewer-subagent.md** | Peer review PRPs → risk score | `/batch-peer-review` command | Review report + recommendations |
| **context-updater-subagent.md** | Sync completion → update CLAUDE.md | `/batch-update-context` command | Status updates + Serena memory |

---

## Subagent Overview

### 1. Generator Subagent
**File**: `generator-subagent.md`

**Purpose**: Transform structured plan into individual PRPs

**Process**:
1. Parse plan markdown → extract phases
2. Build dependency graph
3. Topological sort → logical order
4. Assign stages → maximize parallelism
5. Generate PRP files (one per phase)
6. Create Linear issues
7. Output batch summary

**Input**:
```
Plan file (markdown with Phases section)
```

**Output**:
```
- PRP-{batch}.{stage}.{index}.md files
- Linear issues
- Batch summary JSON
```

**Example**:
```
Input: Feature plan with 10 phases
↓
Generator parses, analyzes dependencies, assigns to 4 stages
↓
Output: 10 PRPs grouped by stage, ready for execution
```

**Key Features**:
- Handles None / empty dependencies
- Detects circular dependencies early
- Maximizes parallel execution
- Integrates with Linear for issue tracking
- Generates YAML frontmatter automatically

**Test with**: `dependency_analyzer.py`

---

### 2. Executor Subagent
**File**: `executor-subagent.md`

**Purpose**: Execute PRP implementation steps end-to-end

**Process**:
1. Parse PRP file
2. Check dependencies (all must be completed first)
3. Execute each step sequentially
4. Validate against gates
5. Create git commits (per step)
6. Report completion

**Input**:
```
PRP file + task spec JSON from orchestrator
```

**Output**:
```
- Modified/created source files
- Git commits (checkpoint strategy)
- Result JSON with success/failure
```

**Example**:
```
Input: PRP-43.1.1 (Foundation - create templates)
↓
Step 1: Create base-orchestrator.md ✓ Commit
Step 2: Create generator-subagent.md ✓ Commit
Step 3: Create executor-subagent.md ✓ Commit
[... more steps ...]
↓
Output: 5 files created, 5 commits, all gates passed
```

**Key Features**:
- Step-by-step execution
- Checkpoint recovery (can resume from failure)
- Validation gate checking
- Git-based progress tracking
- Detailed error reporting

**Recovery**: If step N fails, can retry from step N+1 after fix

---

### 3. Reviewer Subagent
**File**: `reviewer-subagent.md`

**Purpose**: Comprehensive peer review of PRPs

**Process**:
1. Parse PRPs
2. Structural analysis (format, required fields)
3. Semantic analysis (clarity, feasibility)
4. Inter-PRP consistency (dependencies, conflicts)
5. Risk assessment (complexity vs time)
6. Generate review report

**Input**:
```
One or more PRP files
```

**Output**:
```
- Review report (PRPs/reviews/batch-{id}-review.md)
- Risk scores (0-100 per PRP)
- Conflict warnings
- Recommendations
```

**Example**:
```
Input: Batch 43 (10 PRPs)
↓
Reviewer checks each PRP:
  - Format ✓ (YAML, sections present)
  - Clarity ✓ (steps understandable)
  - Feasibility ✓ (hours match complexity)
  - Gates ✓ (testable and achievable)
  - Risk: 12/100 (LOW)

  File conflict detected:
  - PRP-43.2.1 and PRP-43.2.2 both modify analyzer.py
  - Recommendation: Coordinate writes or merge PRPs
↓
Output: Approval with warnings, ready for execution
```

**Key Features**:
- Structural validation (YAML, sections, format)
- Semantic validation (clarity, feasibility, risk)
- Dependency validation (valid, no cycles)
- File conflict detection
- Risk scoring algorithm
- Cross-PRP consistency checks

**Risk Score Factors**:
- Complexity mismatch (25%)
- Validation gate coverage (25%)
- Step clarity (20%)
- Dependency complexity (15%)
- Time pressure (15%)

---

### 4. Context Updater Subagent
**File**: `context-updater-subagent.md`

**Purpose**: Sync execution completion back into project context

**Process**:
1. Parse executed PRP
2. Find git commits for this PRP
3. Extract implementation evidence (files, commits, changes)
4. Calculate drift score (plan vs reality)
5. Update PRP status (pending → completed)
6. Update Serena memory
7. Generate completion report

**Input**:
```
Executed PRP file + git history
```

**Output**:
```
- Updated PRP with execution tracking
- Serena memory entry
- Drift score (0-100%)
- Completion report
```

**Example**:
```
Input: PRP-43.1.1 (originally status: pending)
↓
Context Updater finds commits:
  5f1a3c2 - PRP-43.1.1: Step 1
  7e2b4d1 - PRP-43.1.1: Step 2
  [... 3 more commits ...]
  3f6d8h5 - PRP-43.1.1: Complete
↓
Evidence collected:
  - 5 files created (matches plan)
  - 732 lines added (matches complexity)
  - 5 commits (matches step count)
  - Drift: 8% (EXCELLENT)
↓
Output: PRP updated with execution tracking, memory entry created
```

**Key Features**:
- Git history analysis
- Implementation evidence collection
- Drift calculation (how far from plan)
- Status transitions (pending → completed)
- Serena memory integration
- Batch-level context updates

**Drift Score**: Measures execution vs plan
- 0-5%: EXCELLENT
- 5-15%: GOOD
- 15-30%: ACCEPTABLE
- 30-50%: CONCERNING
- 50%+: CRITICAL

---

## Subagent Contract

All subagents follow this interface:

### Input
1. **Task Spec** (JSON file at `.ce/orchestration/tasks/batch-{id}/task-{id}.json`)
   ```json
   {
     "task_id": "phase-1",
     "type": "generator|executor|reviewer|context-updater",
     "phase_name": "Phase 1: Foundation",
     "goal": "Create orchestrator templates",
     "steps": ["Step 1...", "Step 2..."],
     "complexity": "medium",
     "estimated_hours": 8,
     "created_at": "2025-11-10T14:30:00Z"
   }
   ```

2. **Heartbeat File** (created at `.ce/orchestration/tasks/batch-{id}/task-{id}.hb`)
   - Written every 30 seconds by subagent
   - Signals "still alive" to orchestrator

3. **Context** (CLAUDE.md, existing files, git history)
   - Read as needed for decisions

### Output
1. **Result File** (JSON at `.ce/orchestration/tasks/batch-{id}/task-{id}.result.json`)
   ```json
   {
     "task_id": "phase-1",
     "status": "success|failure",
     "output": { /* task-specific */ },
     "errors": [],
     "tokens_used": 45000,
     "elapsed_seconds": 1800
   }
   ```

2. **Side Effects** (specific to subagent)
   - Generator: PRP files + Linear issues
   - Executor: Source code files + git commits
   - Reviewer: Review report
   - Context-Updater: Updated PRP + memory entry

### Heartbeat Protocol
```json
{
  "task_id": "phase-1",
  "status": "in_progress",
  "progress": "Step 2 of 5: Processing",
  "tokens_used": 25000,
  "elapsed_seconds": 450,
  "last_update": "2025-11-10T14:45:30Z"
}
```

---

## Integration with Orchestrator

### Phase 3: Spawn Subagents
Orchestrator creates task specs and invokes:
```python
Task(
    description="Execute Phase 1: Foundation",
    prompt=f"Read spec from {spec_file}. Execute phase: {goal}",
    subagent_type="general-purpose"  # All subagents use this
)
```

### Phase 4: Monitor & Wait
Orchestrator polls heartbeat files every 30 seconds
- If heartbeat missing for 2 polls (60s) → task failed
- If result file written → task completed

### Phase 5: Aggregate Results
Orchestrator collects result JSONs and merges outputs

---

## Execution Flow Diagram

```
Generator Subagent Flow:
  Input: Plan file
    ↓
  Parse plan + Extract phases
    ↓
  Build dependency graph
    ↓
  Topological sort + Stage assignment
    ↓
  Generate PRP files (one per phase)
    ↓
  Create Linear issues
    ↓
  Write result JSON
    ↓
  Output: PRPs + Linear issues

Executor Subagent Flow:
  Input: PRP file
    ↓
  Parse PRP + Check dependencies
    ↓
  For each step:
    - Execute step
    - Validate if applicable
    - Create git commit
    ↓
  Validate all gates
    ↓
  Final commit + Write result
    ↓
  Output: Code changes + commits

Reviewer Subagent Flow:
  Input: PRP file(s)
    ↓
  Structural analysis (format checks)
    ↓
  Semantic analysis (clarity, feasibility)
    ↓
  Inter-PRP analysis (dependencies, conflicts)
    ↓
  Risk assessment (complexity vs time)
    ↓
  Generate review report
    ↓
  Output: Review report + recommendations

Context Updater Flow:
  Input: Executed PRP file
    ↓
  Parse PRP + Find git commits
    ↓
  Extract implementation evidence
    ↓
  Calculate drift score
    ↓
  Update PRP status + Add execution tracking
    ↓
  Update Serena memory
    ↓
  Output: Updated PRP + memory entry
```

---

## Common Patterns

### Pattern: Dependency Validation
Used by: Generator, Executor, Context-Updater
```python
def validate_dependencies(phase):
    for dep in phase.get("dependencies", []):
        if dep not in phase_names:
            raise ValueError(f"Undefined dependency: {dep}")
```

### Pattern: Heartbeat Writing
Used by: All subagents (every 30 seconds)
```python
def write_heartbeat(progress_message):
    heartbeat = {
        "status": "in_progress",
        "progress": progress_message,
        "tokens_used": current_tokens,
        "elapsed_seconds": elapsed
    }
    with open(hb_file, 'w') as f:
        json.dump(heartbeat, f)
```

### Pattern: Git Commits (Executor)
Used by: Executor after each step
```bash
git add -A
git commit -m "PRP-{id}: Step {n} - {description}"
```

---

## Testing

All subagent logic is tested via:
- `dependency_analyzer.py` unit tests (40+ test cases)
- Real-world scenarios (PRP-47 batch execution)
- Integration tests (gen → exe → review → update flow)

---

## References

- **Orchestrator Coordination**: `.claude/orchestrators/base-orchestrator.md`
- **Dependency Analysis**: `.ce/orchestration/dependency_analyzer.py`
- **Framework Strategy**: `PRPs/feature-requests/PRP-47-FINAL-RECOMMENDATION.md`
- **Implementation Guide**: `PRPs/feature-requests/PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md`

---

## Quick Links

- Generator details → `generator-subagent.md`
- Executor details → `executor-subagent.md`
- Reviewer details → `reviewer-subagent.md`
- Context Updater details → `context-updater-subagent.md`
- Batch Commands → `.claude/commands/`
