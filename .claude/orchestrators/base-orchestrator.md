# Base Orchestrator Template

**Purpose**: Core coordination logic for batch command execution (gen, exe, review, context-update)

**Architecture**: Sonnet orchestrator spawns Haiku subagents to execute tasks in parallel stages

---

## Overview

The orchestrator manages a 6-phase execution cycle for coordinating batch operations:

```
PHASE 1: Parse & Validate Input
    ↓ (validate plan/batch structure)
PHASE 2: Dependency Analysis
    ↓ (topological sort, cycle detection, stage assignment)
PHASE 3: Spawn Subagents
    ↓ (create tasks, write specs to disk)
PHASE 4: Monitor & Wait
    ↓ (poll heartbeat files, detect failures)
PHASE 5: Aggregate Results
    ↓ (collect output JSON, validate completeness)
PHASE 6: Report & Cleanup
    ↓ (summarize results, cleanup temp files)
```

---

## Phase 1: Parse & Validate Input

**Input**: User-provided plan file (markdown) or batch file (JSON)

**Output**: Parsed structure (dict/list of phases with metadata)

**Validation Checks**:
- File exists and readable
- Markdown/JSON syntax valid
- Each phase has: goal, complexity, estimated_hours, files_modified, dependencies
- No duplicate phase names
- Goal field non-empty

**Error Handling**:
```python
if not input_file.exists():
    raise FileNotFoundError(f"Plan file not found: {input_file}")

phases = parse_markdown_or_json(input_file)
if not phases:
    raise ValueError("No phases found in plan")

for phase in phases:
    validate_phase_schema(phase)  # Raises if missing required fields
```

**Example Input** (Markdown Plan):
```markdown
### Phase 1: Build Foundation

**Goal**: Create orchestrator and subagent templates
**Estimated Hours**: 8
**Complexity**: medium
**Files Modified**: .claude/orchestrators/base-orchestrator.md, .claude/subagents/generator-subagent.md
**Dependencies**: None
**Validation Gates**: [checkboxes]
```

---

## Phase 2: Dependency Analysis

**Input**: Parsed phases (dict/list)

**Output**: Stage assignment (dict mapping phase_name → stage_number)

**Algorithm**:
1. Build dependency graph (phase → list of dependencies)
2. Topological sort (Kahn's algorithm or DFS-based)
3. Detect cycles (if found, return cycle path and error)
4. Assign stages (sequential: each phase → stage number)
5. Detect file conflicts (multiple phases modifying same file)

**Example Dependency Graph**:
```
Phase 1 (foundation)
  ↓
Phase 2a (analyzer) ── Phase 2b (tests) [Stage 2: parallel]
  ↓                           ↓
Phase 3a (gen)  ── Phase 3b (exe) [Stage 3: parallel]
  ↓                           ↓
Phase 4 (integration)
```

**Stage Assignment Output**:
```json
{
  "Phase 1": 1,
  "Phase 2a": 2,
  "Phase 2b": 2,
  "Phase 3a": 3,
  "Phase 3b": 3,
  "Phase 4": 4
}
```

**Cycle Detection**:
```python
if cycle_detected(graph):
    cycle_path = find_cycle_path(graph)
    raise CircularDependencyError(
        f"Circular dependency detected: {' → '.join(cycle_path)}"
    )
```

**File Conflict Detection**:
```python
file_modifications = defaultdict(list)
for phase in phases:
    for file in phase["files_modified"]:
        file_modifications[file].append(phase["name"])

conflicts = {f: phases for f, phases in file_modifications.items() if len(phases) > 1}
if conflicts:
    logger.warning(f"File conflicts detected: {conflicts}")
```

---

## Phase 3: Spawn Subagents

**Input**: Parsed phases + stage assignment

**Output**: Task specs written to disk (.ce/orchestration/tasks/)

**Process**:
1. Create task directory: `.ce/orchestration/tasks/batch-{batch_id}/`
2. For each phase, write task spec JSON file: `task-{phase_id}.json`
3. Spec includes: phase_name, goal, steps, complexity, files_modified
4. Create heartbeat file: `task-{phase_id}.hb` (empty, will be written by subagent)
5. Spawn subagent via Task tool with phase-specific instructions

**Task Spec Schema** (JSON):
```json
{
  "task_id": "phase-1",
  "type": "generator|executor|reviewer|context-updater",
  "phase_name": "Phase 1: Build Foundation",
  "goal": "Create orchestrator and subagent templates",
  "steps": ["Step 1...", "Step 2..."],
  "complexity": "medium",
  "files_modified": [".claude/orchestrators/base-orchestrator.md"],
  "estimated_hours": 8,
  "created_at": "2025-11-10T14:30:00Z",
  "timeout_seconds": 3600
}
```

**Subagent Spawning**:
```python
for phase_id, phase in enumerate(phases, 1):
    task_spec_path = f".ce/orchestration/tasks/batch-{batch_id}/task-{phase_id}.json"
    write_task_spec(task_spec_path, phase)

    subagent_type = determine_subagent_type(phase)  # generator, executor, reviewer, etc.

    Task(
        description=f"Execute {phase['name']}",
        prompt=f"Read task spec from {task_spec_path}. Execute phase: {phase['goal']}",
        subagent_type=subagent_type
    )
```

---

## Phase 4: Monitor & Wait

**Input**: Task specs on disk + heartbeat files (empty initially)

**Output**: Monitor status (all tasks alive, failed, or completed)

**Monitoring Protocol**:
- Subagent writes heartbeat file every 30 seconds: `task-{id}.hb`
- Orchestrator polls heartbeat files every 30 seconds
- If heartbeat missing for 2 consecutive polls (60 seconds), mark task as failed
- When task completes, subagent writes result JSON: `task-{id}.result.json`

**Heartbeat File Format** (JSON):
```json
{
  "task_id": "phase-1",
  "status": "in_progress",
  "progress": "Step 2 of 5: Creating subagent templates",
  "tokens_used": 12500,
  "elapsed_seconds": 450,
  "last_update": "2025-11-10T14:45:30Z"
}
```

**Polling Logic**:
```python
def monitor_tasks(batch_id, timeout_seconds=3600):
    start_time = time.time()
    last_heartbeat = {}
    failed_tasks = set()
    completed_tasks = set()

    while True:
        current_time = time.time()
        elapsed = current_time - start_time

        # Check timeout
        if elapsed > timeout_seconds:
            raise TimeoutError(f"Batch {batch_id} exceeded {timeout_seconds}s timeout")

        # Poll all heartbeat files
        for task_id in all_tasks:
            hb_file = f".ce/orchestration/tasks/{batch_id}/task-{task_id}.hb"

            if os.path.exists(hb_file):
                last_heartbeat[task_id] = time.time()
                # Parse and log status
                with open(hb_file) as f:
                    hb = json.load(f)
                    print(f"[{hb['status']}] {task_id}: {hb['progress']}")
            else:
                # Check if task has completed
                result_file = f".ce/orchestration/tasks/{batch_id}/task-{task_id}.result.json"
                if os.path.exists(result_file):
                    completed_tasks.add(task_id)
                    print(f"[COMPLETED] {task_id}")
                # Check for failure (2 missed polls = 60 seconds)
                elif task_id in last_heartbeat:
                    if current_time - last_heartbeat[task_id] > 60:
                        failed_tasks.add(task_id)
                        logger.error(f"Task {task_id} failed (no heartbeat for 60s)")

        # Exit if all tasks done
        if completed_tasks | failed_tasks == set(all_tasks):
            break

        time.sleep(30)  # Poll every 30 seconds

    return completed_tasks, failed_tasks
```

**Dashboard Output** (printed every 30 seconds):
```
Batch 43 Progress (15min elapsed)
═══════════════════════════════════════════
Task  │ Status      │ Progress                    │ Time
───────┼─────────────┼─────────────────────────────┼─────
1     │ IN_PROGRESS │ Step 3 of 5: Creating temps │ 3m
2a    │ IN_PROGRESS │ Analyzing dependencies      │ 2m
2b    │ QUEUED      │ Waiting for Phase 2a        │ 0m
3     │ QUEUED      │ Waiting for Phase 2         │ 0m
═══════════════════════════════════════════
```

---

## Phase 5: Aggregate Results

**Input**: Completed task result files

**Output**: Aggregated batch result (summary JSON)

**Process**:
1. Read all result files: `task-{id}.result.json`
2. Validate each result (check required fields: task_id, status, output)
3. Check for conflicts (file modifications that overlap)
4. Merge outputs (combine generated PRPs, commits, etc.)
5. Write final result: `.ce/orchestration/batches/batch-{batch_id}.result.json`

**Result File Schema** (per subagent):
```json
{
  "task_id": "phase-1",
  "status": "success",
  "output": {
    "files_created": [".claude/orchestrators/base-orchestrator.md"],
    "files_modified": [],
    "commits": [],
    "prps_generated": []
  },
  "errors": [],
  "tokens_used": 45000,
  "elapsed_seconds": 1800
}
```

**Aggregated Batch Result**:
```json
{
  "batch_id": 43,
  "status": "success",
  "stage": 1,
  "completed_tasks": ["phase-1"],
  "failed_tasks": [],
  "total_files_created": 6,
  "total_tokens_used": 180000,
  "total_elapsed_seconds": 3600,
  "results": [
    {
      "task_id": "phase-1",
      "status": "success",
      "files_created": [...]
    }
  ]
}
```

**Conflict Resolution**:
```python
def check_file_conflicts(results):
    """Check if multiple tasks modified the same file"""
    files = defaultdict(list)
    for result in results:
        for file in result["output"]["files_created"] + result["output"]["files_modified"]:
            files[file].append(result["task_id"])

    conflicts = {f: tasks for f, tasks in files.items() if len(tasks) > 1}
    if conflicts:
        logger.warning(f"File conflicts (user must resolve): {conflicts}")
        return False
    return True
```

---

## Phase 6: Report & Cleanup

**Input**: Aggregated batch result

**Output**: Human-readable summary + cleanup

**Summary Report**:
```
Batch 43 Completed Successfully
═══════════════════════════════════════════
Status: SUCCESS
Duration: 1 hour
Cost: $0.42
Stages: 1/4 completed

Tasks Completed: 10/10
  ✓ Phase 1: Foundation (1h)
  ✓ Phase 2a: Analyzer (30m)
  ✓ Phase 2b: Tests (30m)
  ✓ Phase 3a: Gen refactor (45m)
  ✓ Phase 3b: Exe refactor (50m)
  ✓ Phase 4: Integration test (30m)
  ✓ Phase 5a: Review refactor (25m)
  ✓ Phase 5b: Context refactor (25m)
  ✓ Phase 6: Docs (30m)
  ✓ Phase 7: Metrics (40m)

Files Created: 6
Files Modified: 4
Commits: 3

Next Steps:
  1. Review generated files
  2. Commit changes
  3. Create Linear issues for any gaps
  4. Start Stage 2 execution

═══════════════════════════════════════════
```

**Cleanup**:
```python
def cleanup_batch(batch_id):
    """Remove temporary files after batch completes"""
    task_dir = f".ce/orchestration/tasks/batch-{batch_id}"

    # Archive heartbeat files
    archive_dir = f".ce/orchestration/completed-batches/batch-{batch_id}"
    shutil.copytree(task_dir, archive_dir)

    # Keep result JSON for analysis, remove heartbeats
    for hb_file in glob(f"{task_dir}/*.hb"):
        os.remove(hb_file)

    logger.info(f"Batch {batch_id} archived to {archive_dir}")
```

---

## Error Handling Strategy

**Validation Errors** (Phase 1):
- Catch during parse, fail fast with clear message
- Example: "Phase 'Build Foundation' missing 'complexity' field"

**Dependency Errors** (Phase 2):
- Detect circular dependencies, show cycle path
- Example: "Circular dependency: Phase 1 → Phase 2 → Phase 1"

**Task Failures** (Phase 4):
- Detect via missing heartbeat (60s timeout)
- Mark task failed, log error, mark dependent tasks as blocked
- Example: "Phase 2a failed, blocking Phase 3a"

**Result Conflicts** (Phase 5):
- Detect file conflicts between parallel tasks
- Warn user, require manual resolution
- Example: "Phase 2a and Phase 2b both modify .ce/config.yml"

**Timeout Errors** (Phase 4):
- If any stage exceeds 3600 seconds, kill all tasks in stage
- Log failure and require retry
- Example: "Batch exceeded 1 hour timeout"

---

## Integration with Subagents

Each subagent follows this contract:

1. **Read task spec**: `task-{id}.json`
2. **Write heartbeat every 30s**: `task-{id}.hb`
3. **Execute phase**:
   - Follow implementation steps
   - Create files, modify code, run tests
   - Validate against gates
4. **Write result**: `task-{id}.result.json` with status + output
5. **Cleanup**: Remove task spec (success only)

**Subagent Example** (Generator):
```markdown
# Task: Phase 1 - Build Foundation

Read task spec: .ce/orchestration/tasks/batch-43/task-1.json

## Steps
1. Create .claude/orchestrators/base-orchestrator.md (300 lines)
2. Create .claude/subagents/generator-subagent.md (100 lines)
3. [... remaining steps ...]

## Validation
- [ ] All 5 files created
- [ ] No syntax errors
- [ ] Total lines: ~730 ± 50

## Heartbeat Protocol
Every 30 seconds, write to task-1.hb:
{
  "status": "in_progress",
  "progress": "Step 2 of 6: Creating generator-subagent.md",
  "tokens_used": 25000
}

## Result
When complete, write to task-1.result.json:
{
  "task_id": "phase-1",
  "status": "success",
  "output": {
    "files_created": [".claude/orchestrators/base-orchestrator.md", ...],
    "errors": []
  }
}
```

---

## Configuration & Defaults

**Timeout**: 3600 seconds (1 hour per batch)

**Heartbeat Poll Interval**: 30 seconds

**Heartbeat Failure Threshold**: 2 consecutive misses (60 seconds)

**Task Directory**: `.ce/orchestration/tasks/batch-{batch_id}/`

**Archive Directory**: `.ce/orchestration/completed-batches/batch-{batch_id}/`

**Result Directory**: `.ce/orchestration/batches/batch-{batch_id}.result.json`

---

## Success Criteria (Validation Gates)

- [ ] Base orchestrator template created and readable
- [ ] All 6 phases documented with examples
- [ ] Dependency analysis algorithm clear and testable
- [ ] Monitoring protocol defined (heartbeat format, polling logic)
- [ ] Subagent contract documented with examples
- [ ] Error handling covers validation, dependencies, failures, timeouts
- [ ] Integration testing plan clear (can test each phase independently)
- [ ] No external dependencies (stdlib only for core orchestrator)
- [ ] Configuration defaults well-documented
