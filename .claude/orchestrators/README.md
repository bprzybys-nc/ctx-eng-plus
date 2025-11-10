# Orchestrator Framework - Quick Start

**Last Updated**: 2025-11-10
**Status**: Phase 1 Complete (Foundation Ready)
**Timeline**: Week 1-3 MVP + Week 4+ Phase 2 Production

---

## Quick Start: How to Use the Framework

### 1. Create a Plan Document

```markdown
# My Feature Plan

## Phases

### Phase 1: Setup

**Goal**: Initialize project structure
**Estimated Hours**: 2
**Complexity**: low
**Files Modified**: src/setup.py, tests/test_setup.py
**Dependencies**: None
**Implementation Steps**:
1. Create project structure
2. Write setup tests
3. Verify with pytest

**Validation Gates**:
- [ ] Project structure created
- [ ] All tests passing
- [ ] Documentation updated
```

### 2. Generate PRPs from Plan

```bash
/batch-gen-prp my-feature-plan.md
```

Output:
```
Batch 44 Generated:
  Stage 1: PRP-44.1.1
  Stage 2: PRP-44.2.1, PRP-44.2.2 (parallel)
  Stage 3: PRP-44.3.1

Created 4 Linear issues. Ready for execution.
```

### 3. Execute the Batch

```bash
/batch-exe-prp --batch 44
```

Monitors execution stage-by-stage, detects failures, saves progress via git commits.

### 4. Review Generated Code

```bash
/batch-peer-review --batch 44
```

Produces structural and semantic review report.

### 5. Update Context

```bash
/batch-update-context --batch 44
```

Syncs execution status back into CLAUDE.md and Serena memory.

---

## Framework Architecture

```
BASE ORCHESTRATOR
├─ Phase 1: Parse & Validate Input
│  ├─ Read plan/batch file
│  ├─ Validate structure
│  └─ Extract phases with metadata
│
├─ Phase 2: Dependency Analysis
│  ├─ Build dependency graph
│  ├─ Topological sort → logical order
│  ├─ Detect cycles → fail fast
│  ├─ Assign stages → maximize parallelism
│  └─ Detect file conflicts → warn user
│
├─ Phase 3: Spawn Subagents
│  ├─ Write task specs to disk
│  ├─ Spawn Haiku subagent per phase
│  └─ Subagents execute in stages
│
├─ Phase 4: Monitor & Wait
│  ├─ Poll heartbeat files (30s interval)
│  ├─ Detect timeouts (>60s no heartbeat)
│  ├─ Log progress to stdout
│  └─ Wait for stage completion
│
├─ Phase 5: Aggregate Results
│  ├─ Collect result JSON from each phase
│  ├─ Detect conflicts (file modification overlaps)
│  ├─ Merge outputs
│  └─ Calculate metrics
│
└─ Phase 6: Report & Cleanup
   ├─ Print human-readable summary
   ├─ Update PRP status
   ├─ Archive temporary files
   └─ Ready for Phase 2 execution
```

---

## Subagent Types

| Subagent | Purpose | Complexity | When to Use |
|----------|---------|------------|------------|
| **Generator** | Parse plans → generate PRPs | Haiku | Phase 1 of batch commands |
| **Executor** | Execute PRP steps → modify files | Haiku | Phase 2-7 actual implementation |
| **Reviewer** | Peer review PRPs → risk score | Haiku | Quality gate before execution |
| **Context-Updater** | Sync completion → update CLAUDE.md | Haiku | After batch execution completes |

All subagents follow same contract:
- Read task spec from `.ce/orchestration/tasks/batch-{id}/task-{id}.json`
- Write heartbeat every 30s to `task-{id}.hb`
- Write results to `task-{id}.result.json` when done

---

## Key Concepts

### Dependency Analysis

**Topological Sort**: Arranges phases in valid execution order
- Example: Phase 1 → [Phase 2a, Phase 2b parallel] → Phase 3

**Cycle Detection**: Fails if circular dependencies found
- Example: Phase A → B → A (invalid, caught early)

**Stage Assignment**: Groups independent phases for parallel execution
- Stage 1: All phases with no dependencies
- Stage 2: All phases depending only on Stage 1
- Stage N: All phases depending on Stage N-1 only

### Heartbeat Protocol

Subagents write JSON status every 30 seconds:
```json
{
  "task_id": "phase-1",
  "status": "in_progress",
  "progress": "Step 2 of 5: Creating files",
  "tokens_used": 12500,
  "elapsed_seconds": 450
}
```

Orchestrator polls → detects missing heartbeat after 60s → marks task failed.

### Validation Gates

PRPs include testable gates that executor validates:
```
- [ ] All files created (checked: file existence)
- [ ] No syntax errors (checked: linting)
- [ ] Tests pass (checked: pytest exit code)
- [ ] >90% coverage (checked: coverage report)
```

---

## File Structure

```
.claude/
├─ orchestrators/
│  └─ base-orchestrator.md          ← Main orchestration logic
│  └─ README.md                     ← This file
│
├─ subagents/
│  ├─ generator-subagent.md         ← PRP generation
│  ├─ executor-subagent.md          ← PRP execution
│  ├─ reviewer-subagent.md          ← Code review
│  └─ context-updater-subagent.md   ← Status sync
│
└─ commands/
   ├─ batch-gen-prp.md             ← /batch-gen-prp (uses generator)
   ├─ batch-exe-prp.md             ← /batch-exe-prp (uses executor)
   ├─ batch-peer-review.md         ← /batch-peer-review (uses reviewer)
   └─ batch-update-context.md      ← /batch-update-context (uses context-updater)

.ce/orchestration/
├─ dependency_analyzer.py           ← Topological sort + cycle detection
├─ test_dependency_analyzer.py      ← Unit tests (40+ tests)
├─ tasks/batch-{id}/               ← Task specs during execution
│  ├─ task-1.json                  ← Phase 1 spec
│  ├─ task-1.hb                    ← Phase 1 heartbeat
│  └─ task-1.result.json           ← Phase 1 results (after complete)
│
├─ batches/
│  └─ batch-{id}.result.json       ← Final batch results
│
└─ completed-batches/batch-{id}/    ← Archived execution data
```

---

## Execution Flow Example

**Input**: Plan with 4 phases

```
Phase 1 (no deps)
Phase 2a (deps: Phase 1)
Phase 2b (deps: Phase 1)
Phase 3 (deps: Phase 2a, Phase 2b)
```

**Stage Assignment**:
```
Stage 1: Phase 1 (1 task)
Stage 2: Phase 2a, Phase 2b (2 tasks in parallel)
Stage 3: Phase 3 (1 task)
Total stages: 3 | Max parallelism: 2 tasks/stage
```

**Execution Timeline**:
```
T=0:   Orchestrator spawns Phase 1 subagent
T=5:   Phase 1 starts (heartbeat received)
T=30:  Phase 1 completes, results saved
T=30:  Orchestrator spawns Phase 2a + Phase 2b in parallel
T=35:  Both Phase 2 subagents start
T=45:  Phase 2a completes
T=60:  Phase 2b completes
T=60:  Orchestrator spawns Phase 3
T=65:  Phase 3 starts
T=95:  Phase 3 completes
T=95:  Batch complete, results aggregated
T=100: Report printed, context updated
```

---

## Error Handling

### Validation Errors (Phase 1)
- Missing required fields → Fail with clear message
- Invalid YAML → Parse error
- **Action**: Fix plan file and retry

### Dependency Errors (Phase 2)
- Circular dependencies detected → Fail with cycle path
- Undefined dependency → Fail with list of valid phases
- **Action**: Fix dependency and retry

### Execution Errors (Phase 4)
- Subagent timeout (>60s no heartbeat) → Mark failed
- Validation gate fails → Report failure details
- File conflict → Warn user (can continue or abort)
- **Action**: Review error, retry or fix underlying issue

---

## Phase 2: Production Monitoring (Week 4+)

After Phase 1 MVP ships, Phase 2 monitors real usage:

1. **Collect Metrics**
   - Duration per batch
   - Token usage per subagent
   - Cost per batch
   - Error rates and types

2. **Analyze Trends**
   - Which phases consistently run long?
   - Where do most errors occur?
   - Can batches be optimized?

3. **Fix Bottlenecks** (data-driven)
   - If timeout common → increase timeout
   - If tokens high → add shared context optimization
   - If conflicts common → add better conflict detection

4. **No Pre-planned Features**
   - Only add features if data shows they're needed
   - YAGNI principle: avoid gold-plating
   - Focus on what actually blocks users

---

## Success Criteria

### Phase 1 (MVP) ✓
- [x] All 5 template files created
- [x] Dependency analyzer works correctly
- [x] All validation gates passing
- [x] Ready for execution

### Phase 2 (Production)
- [ ] 10+ batches run without critical failures
- [ ] Average batch duration <3 hours
- [ ] Token usage optimized (40% reduction target)
- [ ] Manual conflict resolution <1% of time
- [ ] Team confident in framework

---

## Common Tasks

### Task: Debug a failing phase

```bash
# 1. Check heartbeat file for last status
cat .ce/orchestration/tasks/batch-43/task-2.hb

# 2. Check git log for phase commits
git log --oneline | grep "PRP-43.2"

# 3. Check result for error details
cat .ce/orchestration/tasks/batch-43/task-2.result.json

# 4. Retry phase manually
/batch-exe-prp --batch 43 --retry-phase 2
```

### Task: Check batch status

```bash
# Summary of completed batch
cat .ce/orchestration/batches/batch-43.result.json | jq .

# Timeline of execution
git log --oneline --grep="PRP-43" | head -20

# Detailed stage breakdown
.ce/orchestration/dependency_analyzer.py analyze batch-43.md
```

### Task: Optimize slow batch

```bash
# 1. Analyze which phases are slow
cat batch-result.json | jq '.results[] | {phase, elapsed_seconds}'

# 2. Check if file conflicts caused sequential execution
.ce/orchestration/dependency_analyzer.py validate batch-plan.md

# 3. Profile tokens if context too large
cat batch-result.json | jq '.results[] | {phase, tokens_used}'

# 4. Add shared context if high token use
# Edit base-orchestrator.md Phase 3 to cache CLAUDE.md
```

---

## References

- **Full Orchestrator Logic**: `.claude/orchestrators/base-orchestrator.md`
- **Generator Spec**: `.claude/subagents/generator-subagent.md`
- **Executor Spec**: `.claude/subagents/executor-subagent.md`
- **Reviewer Spec**: `.claude/subagents/reviewer-subagent.md`
- **Context Updater Spec**: `.claude/subagents/context-updater-subagent.md`
- **Dependency Analysis**: `.ce/orchestration/dependency_analyzer.py`
- **Unit Tests**: `.ce/orchestration/test_dependency_analyzer.py`
- **Strategy Guide**: `PRPs/feature-requests/PRP-47-FINAL-RECOMMENDATION.md`

---

## Questions?

Refer to the detailed template for your specific operation:
- How to generate PRPs? → `generator-subagent.md`
- How to execute PRPs? → `executor-subagent.md`
- How to review PRPs? → `reviewer-subagent.md`
- How to update context? → `context-updater-subagent.md`
- How dependencies work? → `base-orchestrator.md` Phase 2
