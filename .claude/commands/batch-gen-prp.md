# /batch-gen-prp - Batch PRP Generation with Parallel Subagents

Decomposes large plan documents into staged, parallelizable PRPs with automatic dependency analysis and concurrent generation using subagents.

**Architecture**: Orchestrator spawns parallel subagents running generator-subagent template

## Usage

```bash
/batch-gen-prp <plan-file-path>

# Examples:
/batch-gen-prp TOOL-PERMISSION-LOCKDOWN-PLAN.md
/batch-gen-prp feature-requests/AUTH-SYSTEM-PLAN.md
/batch-gen-prp PRPs/plans/BIG-FEATURE-PLAN.md
```

---

## Architecture Overview

This command implements the **base-orchestrator.md** 6-phase pattern:

1. **Parse & Validate** → Extract phases from plan file
2. **Dependency Analysis** → Call dependency_analyzer.py for topological sort + cycle detection
3. **Spawn Subagents** → Create generator subagents per phase (parallel within stages)
4. **Monitor & Wait** → Poll heartbeat files every 30s
5. **Aggregate Results** → Collect generated PRPs + Linear issues
6. **Report & Cleanup** → Summary + cleanup temp files

**Reference**: See `.claude/orchestrators/base-orchestrator.md` for complete orchestration pattern

---

## Phase 1: Parse & Validate Input

**Input**: Plan markdown file path

**Output**: List of parsed phases with metadata

**Process**:
1. Read plan file
2. Split by `### Phase` headers
3. Extract: goal, estimated_hours, complexity, files_modified, dependencies, steps, validation_gates
4. Validate required fields present

**Phase Schema**:
```python
{
    "name": "Phase 1: Foundation",
    "goal": "Create orchestrator templates",
    "estimated_hours": 8.0,
    "complexity": "medium",
    "files_modified": [".claude/orchestrators/base-orchestrator.md"],
    "dependencies": [],  # List of phase names
    "implementation_steps": ["Step 1...", "Step 2..."],
    "validation_gates": ["[ ] Gate 1", "[ ] Gate 2"]
}
```

**Validation Errors** → Fail fast with clear message

---

## Phase 2: Dependency Analysis

**Input**: Parsed phases (list of dicts)

**Output**: Stage assignment (dict: phase_name → stage_number)

**Delegate to**: `.ce/orchestration/dependency_analyzer.py`

**Integration**:
```python
from .ce.orchestration.dependency_analyzer import analyze_plan_file

result = analyze_plan_file(phases)

if not result["success"]:
    # Show errors (undefined deps, circular deps)
    raise ValueError("\n".join(result["errors"]))

# Use result["stage_assignment"] for parallel grouping
stage_assignment = result["stage_assignment"]
file_conflicts = result["file_conflicts"]
```

**Cycle Detection**: If circular dependency detected, analyzer returns cycle path:
```
ERROR: Circular dependency detected: Phase 1 → Phase 2 → Phase 3 → Phase 1
```

**File Conflicts**: Analyzer warns about multiple phases modifying same file

---

## Phase 3: Spawn Subagents

**Input**: Parsed phases + stage assignment

**Output**: Task specs written to `.ce/orchestration/tasks/batch-{batch_id}/`

**Process**:
1. Calculate batch ID (next free PRP number)
2. Group phases by stage
3. For each phase:
   - Write task spec JSON: `task-{phase_id}.json`
   - Create empty heartbeat file: `task-{phase_id}.hb`
   - Spawn subagent via Task tool

**Task Spec JSON**:
```json
{
  "task_id": "phase-1",
  "type": "generator",
  "phase_name": "Phase 1: Foundation",
  "goal": "Create orchestrator templates",
  "steps": ["Step 1...", "Step 2..."],
  "complexity": "medium",
  "files_modified": [".claude/orchestrators/base-orchestrator.md"],
  "estimated_hours": 8,
  "prp_id": "43.1.1",
  "batch_id": 43,
  "stage": 1,
  "dependencies": []
}
```

**Subagent Invocation**:
```python
Task(
    description=f"Generate PRP-{prp_id}",
    prompt=f"""
You are generating a PRP in batch mode.

Read task spec: .ce/orchestration/tasks/batch-{batch_id}/task-{phase_id}.json

Follow generator-subagent.md template:
1. Parse task spec
2. Generate PRP file (PRPs/feature-requests/PRP-{prp_id}.md)
3. Create Linear issue
4. Write heartbeat every 30s to task-{phase_id}.hb
5. Write result JSON to task-{phase_id}.result.json

Reference: .claude/subagents/generator-subagent.md
""",
    subagent_type="general-purpose",
    model="sonnet"
)
```

---

## Phase 4: Monitor & Wait

**Input**: Task specs + heartbeat files

**Output**: Completion/failure status per task

**Monitoring Protocol** (from base-orchestrator.md):
- Poll interval: 30 seconds
- Heartbeat file: `task-{id}.hb` (JSON with status, progress, tokens_used)
- Kill threshold: 2 consecutive missed polls (60 seconds)
- Completion signal: `task-{id}.result.json` exists

**Heartbeat Format**:
```json
{
  "task_id": "phase-1",
  "status": "in_progress",
  "progress": "Generated 3/5 PRPs",
  "tokens_used": 25000,
  "elapsed_seconds": 450,
  "last_update": "2025-11-10T14:45:30Z"
}
```

**Dashboard Output** (printed every 30s):
```
Batch 43 Progress (5min elapsed)
═══════════════════════════════════════════
Task  │ Status      │ Progress           │ Age
──────┼─────────────┼────────────────────┼────
1     │ IN_PROGRESS │ Creating PRP files │ 2m
2a    │ IN_PROGRESS │ Step 3/5           │ 1m
2b    │ COMPLETED   │ Done               │ -
3     │ QUEUED      │ Waiting            │ 0m
═══════════════════════════════════════════
```

**Error Handling**: Continue with other agents if one fails (user requirement)

---

## Phase 5: Aggregate Results

**Input**: Completed task result files (`task-{id}.result.json`)

**Output**: Batch summary JSON

**Result File Schema** (per subagent):
```json
{
  "task_id": "phase-1",
  "status": "success",
  "prp_file": "PRPs/feature-requests/PRP-43.1.1-foundation.md",
  "linear_issue": "CTX-123",
  "linear_url": "https://linear.app/...",
  "tokens_used": 45000,
  "elapsed_seconds": 1800
}
```

**Batch Summary**:
```json
{
  "batch_id": 43,
  "total_prps": 5,
  "successful": 5,
  "failed": 0,
  "stages": [
    {
      "stage_num": 1,
      "prps": ["PRP-43.1.1"]
    },
    {
      "stage_num": 2,
      "prps": ["PRP-43.2.1", "PRP-43.2.2", "PRP-43.2.3"]
    },
    {
      "stage_num": 3,
      "prps": ["PRP-43.3.1"]
    }
  ],
  "created_at": "2025-11-10T14:30:00Z"
}
```

**Write to**: `.ce/orchestration/batches/batch-{batch_id}.summary.json`

---

## Phase 6: Report & Cleanup

**Summary Output**:
```
✅ Batch PRP Generation Complete
════════════════════════════════════════════════════════

Batch ID: 43
Plan: TOOL-PERMISSION-LOCKDOWN-PLAN.md
Generated: 5/5 PRPs (100% success rate)

Stage 1 (sequential):
  ✓ PRP-43.1.1: Tool Deny List
    → PRPs/feature-requests/PRP-43.1.1-tool-deny-list.md
    → Linear: CTX-45 (https://linear.app/...)

Stage 2 (parallel - 3 agents):
  ✓ PRP-43.2.1: Usage Guide
  ✓ PRP-43.2.2: Worktree Docs
  ✓ PRP-43.2.3: Doc Updates

Stage 3 (sequential):
  ✓ PRP-43.3.1: Command Permissions

Execution time: 12m 34s
Time saved: 41% vs sequential (17m 45s)

Next steps:
  1. Review generated PRPs in PRPs/feature-requests/
  2. Execute with: /batch-exe-prp --batch 43
     or stage-by-stage: /batch-exe-prp --batch 43 --stage 1
```

**Cleanup**:
- Archive heartbeat files to `.ce/orchestration/completed-batches/batch-{batch_id}/`
- Keep result JSONs for analysis
- Remove temporary task specs

---

## Error Handling

### Validation Errors (Phase 1)
```
❌ Plan validation failed:
  - Phase 3: Missing "Estimated Hours" field
  - Phase 5: "Dependencies" references non-existent "Phase 9"
```

### Circular Dependencies (Phase 2)
```
❌ Circular dependency detected:
  Phase 2 → Phase 3 → Phase 4 → Phase 2

Please revise plan to break the cycle.
```

### Agent Failures (Phase 4)
```
Stage 2 (parallel): 3 agents
  ✓ PRP-43.2.1: SUCCESS
  ❌ PRP-43.2.2: FAILED (no heartbeat for 60s)
  ✓ PRP-43.2.3: SUCCESS

Result: 2/3 PRPs generated, proceed to Stage 3
Failed PRPs can be retried with: /generate-prp --prp-id 43.2.2 --retry
```

**User Requirement**: "Continue with other 2? Yes" → Continue on partial failure

---

## Plan Document Format

### Structure
```markdown
# Plan Title

## Overview
[High-level description]

## Phases

### Phase 1: Name

**Goal**: One-sentence objective
**Estimated Hours**: 4.0
**Complexity**: low|medium|high
**Files Modified**: path/to/file1, path/to/file2
**Dependencies**: None | Phase 1, Phase 2

**Implementation Steps**:
1. Step 1
2. Step 2

**Validation Gates**:
- [ ] Gate 1
- [ ] Gate 2

### Phase 2: Name
[Same structure]
```

**Example**: See `examples/TOOL-PERMISSION-LOCKDOWN-PLAN.md`

---

## Integration with /batch-exe-prp

**Full Workflow**:
```bash
# Step 1: Plan decomposition + generation
/batch-gen-prp BIG-FEATURE-PLAN.md
# Output: 8 PRPs in PRPs/feature-requests/PRP-43.*.md

# Step 2: Execute entire batch
/batch-exe-prp --batch 43

# OR: Execute stage-by-stage
/batch-exe-prp --batch 43 --stage 1
/batch-exe-prp --batch 43 --stage 2
/batch-exe-prp --batch 43 --stage 3
```

**Batch Metadata** (in PRP frontmatter):
```yaml
stage: 2
execution_order: 3
merge_order: 3
dependencies: [PRP-43.1.1]
conflict_potential: MEDIUM
```

---

## Configuration

**Timeout**: 300 seconds (5 minutes per batch)

**Heartbeat Interval**: 30 seconds (subagent writes)

**Poll Interval**: 30 seconds (orchestrator checks)

**Kill Threshold**: 2 consecutive missed polls (60 seconds)

**Task Directory**: `.ce/orchestration/tasks/batch-{batch_id}/`

**Archive Directory**: `.ce/orchestration/completed-batches/batch-{batch_id}/`

**Summary File**: `.ce/orchestration/batches/batch-{batch_id}.summary.json`

---

## Time Savings

**Example**: 8 PRPs sequential (30 min) → parallel (10-12 min) = **60% faster**

**Factors**:
- Parallelism: Multiple PRPs per stage
- No context switching: Subagents work independently
- Coordination overhead: Minimal (heartbeat polling only)
