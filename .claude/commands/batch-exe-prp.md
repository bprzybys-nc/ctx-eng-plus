# /batch-exe-prp - Parallel PRP Execution with Orchestrator Framework

Execute multiple PRPs in parallel using the base orchestrator pattern with executor subagents, dependency analysis, and git-log-based monitoring.

## Architecture

This command follows the **base orchestrator template** (`.claude/orchestrators/base-orchestrator.md`) with executor-specific adaptations:

- **Orchestrator**: Sonnet coordinates 6-phase execution
- **Subagents**: Haiku executors implement PRPs via `.claude/subagents/executor-subagent.md`
- **Monitoring**: Git log polling (checkpoint commits, not heartbeat files)
- **Dependencies**: `.ce/orchestration/dependency_analyzer.py` for stage assignment
- **Validation**: L1-L4 validation gates after each phase

### Key Differences from Base Template

| Aspect | Base Template | Executor Adaptation |
|--------|---------------|---------------------|
| **Monitoring** | Heartbeat files (30s polling) | Git log polling (checkpoint commits) |
| **Input** | Plan file (phases) | PRP files or batch ID |
| **Subagent Output** | Generated files | Implemented code + commits |
| **Resume Logic** | Task spec checkpoint | Git log analysis (skip completed phases) |

## Usage

```bash
# Execute specific PRPs in parallel
/batch-exe-prp PRP-A PRP-B PRP-C

# Execute entire batch by ID (stage-by-stage, auto-review enabled)
/batch-exe-prp --batch 34

# Execute specific stage only
/batch-exe-prp --batch 34 --stage 2

# Resume from checkpoint
/batch-exe-prp --batch 34 --resume

# Force model override (default: auto-select per PRP)
/batch-exe-prp --model haiku PRP-A PRP-B

# Disable auto-review (batch mode only)
/batch-exe-prp --batch 34 --no-auto-review
```

## 6-Phase Orchestration Pattern

### Phase 1: Parse & Load PRPs (Sequential, ~5-10s)

**Input**: PRP file paths or batch ID

**Process**:
```python
# Mode 1: Individual PRPs
prps = [read_prp(path) for path in args.prps]

# Mode 2: Batch-aware (discover all PRPs in batch)
if args.batch:
    master_plan = f"PRPs/feature-requests/PRP-{args.batch}-INITIAL.md"
    prp_files = glob(f"PRPs/feature-requests/PRP-{args.batch}.*.*.md")
    prps = [read_prp(path) for path in prp_files]
```

**Validation**:
- PRP files exist and readable
- YAML frontmatter valid
- Required fields: prp_id, title, status, estimated_hours, files_modified

**Output**: List of PRP dicts with metadata

### Phase 2: Validate Readiness (Sequential, ~10-30s)

**Pre-Flight Checks**:
- PRP status is `planning` (ready for execution)
- Dependencies met (all deps have status `completed`)
- Git repo clean (no uncommitted changes)
- MCP server health: `mcp__syntropy__healthcheck(detailed=True)`

**Model Auto-Assignment** (if not overridden by `--model` flag):
```python
def assign_model(prp):
    """Auto-select model based on complexity analysis"""
    complexity_weight = {"low": 0.5, "medium": 1.0, "high": 1.5}

    score = (
        complexity_weight[prp.complexity] * 40 +  # 20/40/60 points
        min(prp.estimated_hours * 10, 30) +       # 30 points max
        min(len(prp.files_modified) * 5, 20) +    # 20 points max
        min(prp.phase_count * 3, 10)              # 10 points max
    )

    if score < 40: return "haiku"
    elif score < 70: return "sonnet"
    else: return "opus"
```

**Abort Conditions**:
- Any PRP file not found → Exit with error
- Dependencies not met → Exit with dep tree
- MCP server unhealthy → Exit with health report
- Git repo dirty → Exit with status warning

### Phase 3: Dependency Analysis & Stage Assignment (Sequential, ~5-10s)

**Call Dependency Analyzer**:
```bash
cd .ce/orchestration
python dependency_analyzer.py /tmp/batch-{batch_id}-prps.json
```

**Input Format** (JSON):
```json
{
  "items": [
    {
      "id": "PRP-47.1.1",
      "dependencies": [],
      "files": [".claude/orchestrators/base-orchestrator.md", ...]
    },
    {
      "id": "PRP-47.2.1",
      "dependencies": ["PRP-47.1.1"],
      "files": [".ce/orchestration/dependency_analyzer.py"]
    }
  ]
}
```

**Output** (from analyzer):
```json
{
  "sorted_order": ["PRP-47.1.1", "PRP-47.2.1", "PRP-47.2.2", ...],
  "stages": {
    "1": ["PRP-47.1.1"],
    "2": ["PRP-47.2.1", "PRP-47.2.2"],
    "3": ["PRP-47.3.1"]
  },
  "file_conflicts": {
    ".claude/settings.local.json": ["PRP-47.3.1", "PRP-47.4.1"]
  },
  "has_cycles": false
}
```

**Conflict Resolution**:
- If `file_conflicts` detected: Serialize conflicting PRPs (move to different stages)
- If `has_cycles=true`: Exit with cycle path error

### Phase 4: Spawn Executor Subagents (Parallel within stage, Sequential across stages)

**For Each Stage** (sequential):

**Resume Logic** (check git log before spawning):
```python
def get_completed_phases(prp_id, branch):
    """Parse git log for checkpoint commits, determine resume point"""
    commits = git_log(branch, grep=f"PRP-{prp_id}: Phase")
    phases_completed = [extract_phase_num(msg) for msg in commits]

    if phases_completed:
        resume_from = max(phases_completed) + 1
        return f"phase_{resume_from}"
    return None  # Start from beginning
```

**Subagent Invocation** (parallel within stage):
```python
# Launch all PRPs in current stage in parallel (single message, multiple Task calls)
for prp in stage_prps:
    resume_from = get_completed_phases(prp.prp_id, prp.branch) if args.resume else None

    Task(
        subagent_type="general-purpose",
        model=prp.assigned_model,  # From Phase 2 auto-assignment
        description=f"Execute {prp.prp_id}",
        prompt=f"""
You are an executor subagent. Follow the executor subagent template exactly.

**Template**: .claude/subagents/executor-subagent.md

**Input Specification**:
{{
  "prp_path": "{prp.file_path}",
  "resume_from": "{resume_from}",  // null if starting fresh
  "validation_level": 4,
  "context": {{
    "project_root": "{project_root}",
    "branch": "{prp.branch}",
    "batch_id": "{batch_id}",
    "stage": {stage_num},
    "order": {prp.order}
  }}
}}

**Checkpoint Protocol**:
- Create git commit after each phase: "PRP-{{prp_id}}: Phase {{N}} - {{title}}"
- Run validation (L1-L4) after each phase commit
- If validation fails: Stop PRP, mark partial, report error

**Expected Output** (return as JSON):
{{
  "prp_id": "{prp.prp_id}",
  "status": "completed|partial|failed",
  "phases_completed": ["phase_1", "phase_2", ...],
  "validation_results": {{
    "level_1": {{"passed": true, "errors": []}},
    "level_2": {{"passed": true, "errors": []}},
    "level_3": {{"passed": true, "errors": []}},
    "level_4": {{"passed": true, "errors": []}}
  }},
  "git_commits": ["abc123", "def456", ...],
  "error": null
}}
"""
    )
```

### Phase 5: Monitor Execution (Git Log Polling, ~variable duration)

**Monitoring Dashboard** (update every 60s):
```python
def monitor_stage_execution(stage_prps, poll_interval=60, timeout=3600):
    """Poll git logs for checkpoint commits"""
    start_time = time.time()

    while time.time() - start_time < timeout:
        for prp in stage_prps:
            latest_commit = git_log(prp.branch, n=1, grep=f"PRP-{prp.prp_id}: Phase")
            commit_age = time.time() - git_commit_timestamp(latest_commit)

            if commit_age < 300:  # <5 min
                status = "HEALTHY"
            elif commit_age < 600:  # 5-10 min
                status = "WARNING"
            else:  # >10 min
                status = "STALLED"

            print(f"{prp.prp_id}: {status} (last commit {commit_age}s ago)")

        # Check if all subagents complete (via Task status)
        if all_tasks_complete():
            break

        time.sleep(poll_interval)
```

**Auto-Review After Stage** (batch mode only, unless `--no-auto-review`):
```python
if args.batch and not args.no_auto_review:
    # Run execution review via SlashCommand
    review_result = SlashCommand(
        command=f"/batch-peer-review --batch {batch_id} --exe --stage {stage_num}"
    )

    if review_result.status == "FAILED":
        print(f"Stage {stage_num} review FAILED. Pausing batch.")
        save_checkpoint(batch_id, last_stage_completed=stage_num - 1)
        return  # Exit, user must fix and resume

    if review_result.fixes_applied:
        print(f"Auto-fixed {len(review_result.fixes_applied)} minor issues")
```

### Phase 6: Aggregate Results & Cleanup (Sequential, ~10-30s)

**Collect Subagent Outputs**:
```python
results = {}
for prp in all_prps:
    result = get_task_result(prp.task_id)  # From Task tool
    results[prp.prp_id] = result
```

**Merge Worktrees** (if using git worktrees):
```bash
git checkout main
for prp in merge_order:
    git merge {prp.branch} --no-ff -m "Merge {prp.prp_id}: {prp.title}"

    # Conflict detection
    if merge_conflict_detected():
        show_conflict_resolution_help(prp)
        if not args.continue_on_error:
            exit(1)
```

**Update PRP Status**:
```python
for prp_id, result in results.items():
    if result.status == "completed":
        update_prp_yaml(prp_id, status="completed", completion_date=today())
```

**Cleanup**:
```bash
# Remove worktrees
for prp in all_prps:
    git worktree remove {prp.worktree_path}

git worktree prune

# Update context
cd tools && uv run ce update-context
```

**Summary Report**:
```
Batch {batch_id} Execution Complete

Total PRPs: {total}
Completed: {completed}
Partial: {partial}
Failed: {failed}
Time Elapsed: {duration}

Stage Breakdown:
  Stage 1: {stage_1_summary}
  Stage 2: {stage_2_summary} (parallel)
  Stage 3: {stage_3_summary}

Validation Results:
  {prp_1}: ✓ All levels passed
  {prp_2}: ⚠ Level 3 failed (tests)

Next Steps:
  - Review partial PRPs: {partial_list}
  - Fix failed PRPs: {failed_list}
  - Update context: /batch-update-context --batch {batch_id}
```

## Checkpoint & Resume

**Checkpoint Format** (`.ce/tmp/batch-execution-{batch_id}.json`):
```json
{
  "batch_id": 34,
  "last_stage_completed": 2,
  "current_stage": 3,
  "status": "IN_PROGRESS",
  "stages": {
    "1": {"status": "COMPLETED", "prps": [...], "results": {...}},
    "2": {"status": "COMPLETED", "prps": [...], "results": {...}},
    "3": {"status": "IN_PROGRESS", "prps": [...], "results": null}
  }
}
```

**Resume Workflow**:
```python
if args.resume:
    checkpoint = read_checkpoint(args.batch)
    resume_from_stage = checkpoint.last_stage_completed + 1

    print(f"Resuming from Stage {resume_from_stage}")

    # Skip completed stages, execute remaining
    for stage in range(resume_from_stage, total_stages + 1):
        execute_stage(stage)
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--batch <N>` | Execute all PRPs in batch N | `none` |
| `--stage <N>` | Execute specific stage only | `all` |
| `--resume` | Resume from checkpoint | `false` |
| `--no-auto-review` | Disable auto-review after each stage | `false` |
| `--model <model>` | Override auto-selection (sonnet/haiku/opus) | `auto` |
| `--max-parallel <N>` | Max concurrent PRPs within stage | `unlimited` |
| `--dry-run` | Show execution plan without running | `false` |
| `--continue-on-error` | Don't abort on failure | `false` |
| `--timeout <min>` | Max execution time per PRP | `60` |

## Git Checkpoint Commit Format

**Executor Subagent Commit Pattern**:
```
PRP-{prp_id}: Phase {N} - {phase_title}
```

**Examples**:
```
PRP-47.1.1: Phase 1 - Create base orchestrator template
PRP-47.1.1: Phase 2 - Create generator subagent template
PRP-47.1.1: Phase 3 - Create executor subagent template
```

**Resume Detection**:
```python
# Count existing phase commits to determine resume point
commits = git_log(grep="PRP-47.1.1: Phase")
phases_completed = [extract_phase_num(msg) for msg in commits]
# If phases_completed = [1, 2], resume from phase 3
```

## Validation Integration (L1-L4)

**After Each Phase Commit**:
```bash
# Executor subagent runs validation internally
uv run ce validate --level 4

# Captures output:
# Level 1 (structure): PASS/FAIL
# Level 2 (syntax): PASS/FAIL
# Level 3 (tests): PASS/FAIL
# Level 4 (integration, drift <30%): PASS/FAIL

# If any level fails:
# - Log error details
# - Stop current PRP (mark partial)
# - Continue with other PRPs in stage
```

## Error Handling

**Validation Failures** (Partial Completion):
```
⚠ PRP-B validation failed: L3 integration tests timeout

Actions:
  - Mark PRP-B as PARTIAL (2 of 3 phases done)
  - Preserve git commits (checkpoint recovery)
  - Continue with other PRPs in stage
  - Report in aggregate summary
```

**File Conflicts** (Merge Step):
```
⚠ Merge conflict detected: PRP-D
File: .claude/settings.local.json

Resolution:
  1. Read file to view conflict markers
  2. Use Edit tool to merge changes
  3. git add .claude/settings.local.json
  4. git commit -m "Merge PRP-D: Resolve conflict"
```

**Subagent Failures**:
```
❌ PRP-C subagent timeout (60 minutes exceeded)

Actions:
  - Mark PRP-C as FAILED
  - Preserve worktree for debugging
  - Continue with other PRPs (if --continue-on-error)
  - Report in aggregate summary
```

## CLI Command

```bash
cd tools
uv run ce batch-exe [options] <prp-1> <prp-2> ...
uv run ce batch-exe --batch <N> [options]
```

## Related Documentation

- **Base Orchestrator**: `.claude/orchestrators/base-orchestrator.md`
- **Executor Subagent**: `.claude/subagents/executor-subagent.md`
- **Dependency Analyzer**: `.ce/orchestration/dependency_analyzer.py`
- **Related Commands**: `/execute-prp` (single PRP), `/batch-gen-prp` (generation), `/batch-peer-review` (review)

## Notes

- Git log monitoring is executor-specific (gen uses heartbeat files)
- Checkpoint/resume is critical (preserve carefully)
- Validation integration runs after each phase (L1-L4)
- File conflict resolution: Serialize conflicting PRPs across stages
- Performance target: <30 minutes for 4-phase PRP
- This is the second command to use orchestrator framework (after gen)
