# /batch-gen-prp - Batch PRP Generation with Parallel Subagents

Decomposes large plan documents into staged, parallelizable PRPs with automatic dependency analysis and concurrent generation using subagents.

**Architecture**: Coordinator spawns parallel subagents running `/generate-prp` in batch mode

## Usage

```bash
/batch-gen-prp <plan-file-path>

# Examples:
/batch-gen-prp TOOL-PERMISSION-LOCKDOWN-PLAN.md
/batch-gen-prp feature-requests/AUTH-SYSTEM-PLAN.md
/batch-gen-prp PRPs/plans/BIG-FEATURE-PLAN.md
```

## What It Does

1. **Parses plan document** → Extracts phases with metadata
2. **Builds dependency graph** → Analyzes explicit dependencies + file conflicts
3. **Assigns stages** → Groups independent PRPs for parallel execution
4. **Shows plan** → User confirms generation strategy
5. **Spawns subagents** → Parallel generation per stage (Sonnet model)
6. **Monitors progress** → Health checks via file timestamp polling (30s intervals)
7. **Aggregates results** → Collects generated PRPs + Linear issues
8. **Outputs summary** → Shows all generated PRPs grouped by stage

**Time Savings**: 8 PRPs sequential (30 min) → parallel (10-12 min) = **60% faster**

---

## Plan Document Format

### Structure

```markdown
# [Plan Title]

## Overview
[High-level description of what this plan achieves]

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Phases

### Phase 1: [Name]

**Goal**: [One-sentence objective]

**Estimated Hours**: [X.X]

**Complexity**: [low|medium|high]

**Files Modified**:
- path/to/file1.ext
- path/to/file2.ext

**Dependencies**: [None | Phase 1, Phase 2]

**Implementation Steps**:
1. Step 1
2. Step 2

**Validation Gates**:
- [ ] Validation 1
- [ ] Validation 2

**Conflict Notes**: [Optional - explicit conflict warnings]

---

### Phase 2: [Name]
[Same structure repeated]
```

### Example: TOOL-PERMISSION-LOCKDOWN-PLAN.md

```markdown
# Tool & Permission Lockdown

## Overview
Implement comprehensive tool deny list and command permission system to reduce token usage and improve security.

## Success Criteria
- [ ] 55 MCP tools denied
- [ ] Command permissions documented
- [ ] Token usage reduced by 44k (96%)

## Phases

### Phase 1: Tool Deny List

**Goal**: Add 55 denied tools to settings.local.json

**Estimated Hours**: 0.42

**Complexity**: low

**Files Modified**:
- .claude/settings.local.json

**Dependencies**: None

**Implementation Steps**:
1. Read existing settings.local.json
2. Add 55 tools to deny array (Filesystem: 8, Git: 5, GitHub: 26, Repomix: 4, Playwright: 6, Perplexity: 1, Syntropy: 5)
3. Validate JSON syntax

**Validation Gates**:
- [ ] JSON validates
- [ ] 55 tools in deny list
- [ ] No duplicates

---

### Phase 2: Usage Guide

**Goal**: Create comprehensive tool usage guide

**Estimated Hours**: 0.50

**Complexity**: low

**Files Modified**:
- TOOL-USAGE-GUIDE.md

**Dependencies**: Phase 1

**Implementation Steps**:
1. Create TOOL-USAGE-GUIDE.md
2. Add decision tree flowchart
3. Document all 55 denied tools with native alternatives
4. Add common tasks with examples

**Validation Gates**:
- [ ] All 55 denied tools documented
- [ ] Decision tree included
- [ ] 9 common task examples
```

---

## Workflow

### Step 1: Parse Plan Document

```python
# Read plan file
plan_content = Read(file_path=plan_path)

# Extract phases
phases = []
for section in parse_markdown(plan_content):
    if section.heading.startswith("### Phase"):
        phase = {
            "name": extract_after_colon(section.heading),
            "goal": extract_field(section, "Goal"),
            "estimated_hours": float(extract_field(section, "Estimated Hours")),
            "complexity": extract_field(section, "Complexity"),
            "files_modified": extract_list(section, "Files Modified"),
            "dependencies": extract_field(section, "Dependencies"),
            "implementation_steps": extract_list(section, "Implementation Steps"),
            "validation_gates": extract_list(section, "Validation Gates"),
            "conflict_notes": extract_field(section, "Conflict Notes", optional=True)
        }
        phases.append(phase)
```

**Output**:
```
Found 5 phases:
  Phase 1: Tool Deny List (0.42h, low)
  Phase 2: Usage Guide (0.50h, low)
  Phase 3: Worktree Docs (0.58h, low)
  Phase 4: Command Permissions (0.42h, low)
  Phase 5: Doc Updates (0.50h, low)
```

### Step 2: Build Dependency Graph

**Explicit Dependencies**:
```python
dep_graph = {}
for i, phase in enumerate(phases):
    phase_num = i + 1
    phase_letter = chr(64 + phase_num)  # A, B, C, ...

    dep_graph[phase_num] = {
        "name": phase.name,
        "letter": phase_letter,
        "phase": phase,
        "dependencies": parse_dependency_string(phase.dependencies),
        "files": phase.files_modified
    }
```

**Implicit Dependencies (File Conflicts)**:
```python
file_map = defaultdict(list)
for phase_num, data in dep_graph.items():
    for file in data.files:
        file_map[file].append(phase_num)

# Detect conflicts
conflicts = {}
for file, phases in file_map.items():
    if len(phases) > 1:
        conflicts[file] = phases
```

**Output**:
```
Dependency graph:
  Phase 1 (A): Tool Deny List
    Dependencies: None
    Files: .claude/settings.local.json

  Phase 2 (B): Usage Guide
    Dependencies: Phase 1
    Files: TOOL-USAGE-GUIDE.md

  Phase 3 (C): Worktree Docs
    Dependencies: Phase 1
    Files: CLAUDE.md

  Phase 4 (D): Command Permissions
    Dependencies: Phase 2, Phase 3
    Files: .claude/settings.local.json

  Phase 5 (E): Doc Updates
    Dependencies: Phase 1
    Files: CLAUDE.md

⚠ File conflicts detected:
  - .claude/settings.local.json: Phase 1, Phase 4
    → Phase 4 will merge after Phase 1 (MEDIUM conflict)

  - CLAUDE.md: Phase 3, Phase 5
    → Phase 5 will merge after Phase 3 (LOW conflict - different sections)
```

### Step 3: Assign Stages

**Algorithm**: Topological sort + conflict resolution

```python
def assign_stages(dep_graph, file_map):
    """Group phases into stages maximizing parallelism"""
    stages = []
    assigned = set()

    while len(assigned) < len(dep_graph):
        # Find phases with all dependencies satisfied
        ready = [
            phase_num for phase_num in dep_graph
            if phase_num not in assigned
            and all(dep in assigned for dep in dep_graph[phase_num].dependencies)
        ]

        if not ready:
            raise CircularDependencyError("Circular dependency detected")

        # Group by file conflicts
        parallel_groups = []
        for phase_num in ready:
            # Check if phase conflicts with any group
            placed = False
            for group in parallel_groups:
                if not has_file_conflict(phase_num, group, file_map):
                    group.append(phase_num)
                    placed = True
                    break

            if not placed:
                parallel_groups.append([phase_num])

        # Create stage
        stage_type = "parallel" if all(len(g) == 1 for g in parallel_groups) or len(ready) > 1 else "sequential"
        stages.append({
            "stage_num": len(stages) + 1,
            "type": stage_type,
            "phases": ready
        })

        assigned.update(ready)

    return stages
```

**Output**:
```
Stage assignment:
  Stage 1 (parallel): Phase 1 (A)
  Stage 2 (parallel): Phase 2 (B), Phase 3 (C), Phase 5 (E)
  Stage 3 (sequential): Phase 4 (D)

Estimated execution time:
  Sequential: 2.42 hours
  Parallel: 1.42 hours
  Savings: 41% (1.0 hours)
```

### Step 4: Calculate PRP IDs

**Format**: `PRP-X.Y.Z`
- X = Batch ID (next free PRP number)
- Y = Stage number
- Z = Order within stage

```python
# Find next batch ID
existing_prps = glob("PRPs/feature-requests/PRP-*.md")
max_id = max([extract_prp_number(p) for p in existing_prps])
batch_id = max_id + 1

# Assign PRP IDs
prp_ids = {}
execution_order = 1
for stage in stages:
    for i, phase_num in enumerate(stage.phases):
        prp_id = f"{batch_id}.{stage.stage_num}.{i+1}"
        prp_ids[phase_num] = {
            "prp_id": prp_id,
            "stage": stage.stage_num,
            "execution_order": execution_order,
            "merge_order": execution_order
        }
        execution_order += 1
```

**Output**:
```
PRP ID Assignment (Batch 43):
  PRP-43.1.1: Phase 1 - Tool Deny List
  PRP-43.2.1: Phase 2 - Usage Guide
  PRP-43.2.2: Phase 3 - Worktree Docs
  PRP-43.2.3: Phase 5 - Doc Updates
  PRP-43.3.1: Phase 4 - Command Permissions
```

### Step 5: Show Plan to User

```
📋 Batch PRP Generation Plan
============================================================

Input: TOOL-PERMISSION-LOCKDOWN-PLAN.md
Phases detected: 5

Dependency graph:
  Phase 1 (A): Tool Deny List (no deps)
  Phase 2 (B): Usage Guide (depends: Phase 1)
  Phase 3 (C): Worktree Docs (depends: Phase 1)
  Phase 4 (D): Command Permissions (depends: Phase 2, Phase 3)
  Phase 5 (E): Doc Updates (depends: Phase 1)

Stage assignment:
  Stage 1 (parallel): PRP-43.1.1
  Stage 2 (parallel): PRP-43.2.1, PRP-43.2.2, PRP-43.2.3
  Stage 3 (sequential): PRP-43.3.1

⚠ File conflicts detected:
  - .claude/settings.local.json: PRP-43.1.1, PRP-43.3.1 (MEDIUM)
    → PRP-43.3.1 will merge after PRP-43.1.1

  - CLAUDE.md: PRP-43.2.2, PRP-43.2.3 (LOW)
    → Different sections, conflicts unlikely

Estimated execution time:
  Sequential: 2.42h
  Parallel: 1.42h
  Savings: 41% (1.0h)

Generated PRPs will be created at:
  PRPs/feature-requests/PRP-43.1.1-tool-deny-list.md
  PRPs/feature-requests/PRP-43.2.1-usage-guide.md
  PRPs/feature-requests/PRP-43.2.2-worktree-docs.md
  PRPs/feature-requests/PRP-43.2.3-doc-updates.md
  PRPs/feature-requests/PRP-43.3.1-command-permissions.md

Proceed with generation? [y/N]:
```

### Step 6: Spawn Subagents (Stage by Stage)

**Create monitoring directory**:
```bash
mkdir -p .tmp/batch-gen
```

**For each stage**:
```python
for stage in stages:
    print(f"\n🔧 Stage {stage.stage_num} ({stage.type})")
    print("=" * 60)

    if stage.type == "parallel" and len(stage.phases) > 1:
        # Spawn parallel subagents
        agents = []
        for phase_num in stage.phases:
            prp_info = prp_ids[phase_num]
            phase_data = dep_graph[phase_num]

            # Build JSON input for subagent
            batch_input = {
                "batch_mode": True,
                "prp_id": prp_info.prp_id,
                "feature_name": phase_data.name,
                "goal": phase_data.phase.goal,
                "estimated_hours": phase_data.phase.estimated_hours,
                "complexity": phase_data.phase.complexity,
                "files_modified": phase_data.phase.files_modified,
                "dependencies": [prp_ids[dep].prp_id for dep in phase_data.dependencies],
                "implementation_steps": phase_data.phase.implementation_steps,
                "validation_gates": phase_data.phase.validation_gates,
                "stage": f"stage-{stage.stage_num}-parallel",
                "execution_order": prp_info.execution_order,
                "merge_order": prp_info.merge_order,
                "conflict_potential": calculate_conflict(phase_num, file_map),
                "conflict_notes": phase_data.phase.conflict_notes or "",
                "worktree_path": f"../ctx-eng-plus-prp-{prp_info.prp_id.replace('.', '-')}",
                "branch_name": f"prp-{prp_info.prp_id.replace('.', '-')}-{slugify(phase_data.name)}",
                "create_linear_issue": True,
                "plan_context": f"Part of {plan_title} initiative"
            }

            # Spawn subagent
            agent = Task(
                description=f"Generate PRP-{prp_info.prp_id}",
                prompt=f"""
You are generating a PRP in batch mode for the /batch-gen-prp coordinator.

Use the /generate-prp command with this structured JSON input:

```json
{json.dumps(batch_input, indent=2)}
```

Follow the "Batch Mode Workflow" section of /generate-prp:
1. Parse JSON input
2. Write heartbeat to .tmp/batch-gen/PRP-{prp_info.prp_id}.status
3. Generate PRP file with all metadata
4. Create Linear issue
5. Return JSON report

**IMPORTANT**:
- Write heartbeat every 10-15 seconds
- Return JSON report at end (coordinator needs it)
- On error, still return JSON with status: FAILED
""",
                subagent_type="general-purpose",
                model="sonnet"  # User specified: use Sonnet, not haiku
            )
            agents.append((phase_num, agent))

            print(f"  Spawned agent for PRP-{prp_info.prp_id}: {phase_data.name}")

        # Monitor agents
        results = monitor_parallel_agents(agents, prp_ids, timeout=300)  # 5 min timeout
    else:
        # Sequential execution
        results = []
        for phase_num in stage.phases:
            result = generate_prp_sequential(phase_num, dep_graph, prp_ids)
            results.append(result)

    # Show stage results
    show_stage_results(stage, results)
```

### Step 7: Monitor Agents (Health Check Protocol)

**Monitoring function** (runs every 30 seconds):
```python
def monitor_parallel_agents(agents, prp_ids, timeout=300):
    """Monitor subagents via file timestamp polling"""
    start_time = time.now()
    results = {}
    agent_status = {}
    failed_polls = defaultdict(int)  # Track consecutive failures

    # Initialize monitoring
    for phase_num, agent in agents:
        prp_id = prp_ids[phase_num].prp_id
        agent_status[prp_id] = {
            "agent": agent,
            "phase_num": phase_num,
            "status": "STARTING",
            "progress": 0,
            "last_heartbeat": start_time,
            "stalled_warnings": 0
        }

    # Poll every 30 seconds
    while len(results) < len(agents):
        time.sleep(30)

        # Clear screen and show header
        print("\n" + "=" * 60)
        print(f"📊 Monitoring {len(agents)} Agents")
        print("=" * 60 + "\n")

        for prp_id, status_data in agent_status.items():
            if prp_id in results:
                continue  # Already completed

            # Check heartbeat file
            heartbeat_file = f".tmp/batch-gen/PRP-{prp_id}.status"
            prp_file_pattern = f"PRPs/feature-requests/PRP-{prp_id}-*.md"

            # Check if PRP file exists (completion signal)
            prp_files = glob(prp_file_pattern)
            if prp_files:
                # Agent completed successfully
                results[prp_id] = {
                    "status": "SUCCESS",
                    "file_path": prp_files[0]
                }
                print(f"PRP-{prp_id}: {dep_graph[status_data.phase_num].name}")
                print(f"  Status: [COMPLETED] ✓ DONE")
                continue

            # Check heartbeat file
            if os.path.exists(heartbeat_file):
                heartbeat = json.load(open(heartbeat_file))
                age = time.now() - heartbeat.timestamp

                status_data.status = heartbeat.status
                status_data.progress = heartbeat.progress
                status_data.last_heartbeat = heartbeat.timestamp
                failed_polls[prp_id] = 0  # Reset failure counter

                # Determine health
                if heartbeat.status == "FAILED":
                    results[prp_id] = {
                        "status": "FAILED",
                        "error": heartbeat.get("error", "Unknown error")
                    }
                    health = "❌ FAILED"
                elif age < 120:  # 2 minutes
                    health = "✓ HEALTHY"
                elif age < 300:  # 5 minutes
                    health = "⚠ WARNING"
                    status_data.stalled_warnings += 1
                else:
                    health = "❌ STALLED"

                # Display
                print(f"PRP-{prp_id}: {dep_graph[status_data.phase_num].name}")
                print(f"  Status: [{heartbeat.status}{'.' * (15 - len(heartbeat.status))}] {health} ({int(age)}s ago)")
                if "current_step" in heartbeat:
                    print(f"  Step: {heartbeat.current_step}")
                print(f"  Progress: {heartbeat.progress}%")
            else:
                # No heartbeat file yet
                failed_polls[prp_id] += 1
                age = time.now() - start_time

                if failed_polls[prp_id] >= 2:
                    # Kill agent after 2 consecutive failed polls (user requirement)
                    print(f"PRP-{prp_id}: {dep_graph[status_data.phase_num].name}")
                    print(f"  Status: [NO_HEARTBEAT] ❌ KILLED (2 failed polls)")

                    # Kill agent
                    # Note: Task API doesn't support kill, so mark as failed
                    results[prp_id] = {
                        "status": "FAILED",
                        "error": "Agent killed: No heartbeat after 2 polls (60s)"
                    }
                elif age < 60:  # 1 minute grace period
                    print(f"PRP-{prp_id}: {dep_graph[status_data.phase_num].name}")
                    print(f"  Status: [STARTING....] ⏳ INITIALIZING ({int(age)}s)")
                else:
                    print(f"PRP-{prp_id}: {dep_graph[status_data.phase_num].name}")
                    print(f"  Status: [NO_HEARTBEAT] ⚠ WARNING ({int(age)}s, poll {failed_polls[prp_id]}/2)")

            print()  # Blank line between PRPs

        # Check timeout
        if time.now() - start_time > timeout:
            print("\n⚠ Timeout reached. Killing stalled agents...")
            for prp_id, status_data in agent_status.items():
                if prp_id not in results:
                    results[prp_id] = {
                        "status": "FAILED",
                        "error": f"Timeout after {timeout}s"
                    }
            break

    return results
```

**Display Example** (during monitoring):
```
============================================================
📊 Monitoring 3 Agents
============================================================

PRP-43.2.1: Usage Guide
  Status: [WRITING........] ✓ HEALTHY (15s ago)
  Step: Generating Implementation Steps section
  Progress: 65%

PRP-43.2.2: Worktree Docs
  Status: [COMPLETED] ✓ DONE

PRP-43.2.3: Doc Updates
  Status: [RESEARCHING....] ⚠ WARNING (3m 20s ago)
  Progress: 30%

Health Summary: 1 HEALTHY, 1 WARNING, 0 STALLED
Next poll in 30s...
```

### Step 8: Aggregate Results

```python
# Collect all results across stages
all_results = {
    "batch_id": batch_id,
    "plan_file": plan_path,
    "total_prps": len(phases),
    "successful": 0,
    "failed": 0,
    "stages": []
}

for stage in stages:
    stage_results = {
        "stage_num": stage.stage_num,
        "type": stage.type,
        "prps": []
    }

    for phase_num in stage.phases:
        prp_id = prp_ids[phase_num].prp_id
        result = results.get(prp_id, {"status": "UNKNOWN"})

        stage_results.prps.append({
            "prp_id": prp_id,
            "phase_name": dep_graph[phase_num].name,
            "status": result.status,
            "file_path": result.get("file_path"),
            "linear_issue": result.get("linear_issue"),
            "linear_url": result.get("linear_url"),
            "error": result.get("error")
        })

        if result.status == "SUCCESS":
            all_results.successful += 1
        else:
            all_results.failed += 1

    all_results.stages.append(stage_results)
```

### Step 9: Output Summary

```
✅ Batch PRP Generation Complete
============================================================

Batch ID: 43
Plan: TOOL-PERMISSION-LOCKDOWN-PLAN.md
Generated: 5/5 PRPs (100% success rate)

Stage 1 (parallel):
  ✓ PRP-43.1.1: Tool Deny List
    → PRPs/feature-requests/PRP-43.1.1-tool-deny-list.md
    → Linear: CTX-45 (https://linear.app/...)

Stage 2 (parallel - 3 agents):
  ✓ PRP-43.2.1: Usage Guide
    → PRPs/feature-requests/PRP-43.2.1-usage-guide.md
    → Linear: CTX-46 (https://linear.app/...)

  ✓ PRP-43.2.2: Worktree Docs
    → PRPs/feature-requests/PRP-43.2.2-worktree-docs.md
    → Linear: CTX-47 (https://linear.app/...)

  ✓ PRP-43.2.3: Doc Updates
    → PRPs/feature-requests/PRP-43.2.3-doc-updates.md
    → Linear: CTX-48 (https://linear.app/...)

Stage 3 (sequential):
  ✓ PRP-43.3.1: Command Permissions
    → PRPs/feature-requests/PRP-43.3.1-command-permissions.md
    → Linear: CTX-49 (https://linear.app/...)

Execution time: 12m 34s
Time saved: 41% vs sequential (17m 45s)

Next steps:
  1. Review generated PRPs in PRPs/feature-requests/
  2. Execute with:
     /batch-exe-prp --batch 43
     or stage-by-stage:
     /batch-exe-prp --batch 43 --stage 1
     /batch-exe-prp --batch 43 --stage 2
     /batch-exe-prp --batch 43 --stage 3
```

**If failures occurred**:
```
⚠ Partial Success: 4/5 PRPs generated
============================================================

[... successful PRPs listed ...]

Failed:
  ❌ PRP-43.2.3: Doc Updates
    Error: Agent killed: No heartbeat after 2 polls (60s)

    Retry with:
    /generate-prp --prp-id 43.2.3 --retry

Or regenerate entire stage:
    /batch-gen-prp TOOL-PERMISSION-LOCKDOWN-PLAN.md --stage 2 --retry-failed
```

---

## Integration with `/batch-exe-prp`

**Full workflow**:
```bash
# Step 1: Plan decomposition + generation
/batch-gen-prp BIG-FEATURE-PLAN.md
# Output: 8 PRPs in PRPs/feature-requests/PRP-43.*.md

# Step 2: Execute by batch (all stages)
/batch-exe-prp --batch 43
# Executes Stage 1 → Stage 2 (parallel) → Stage 3

# OR: Execute stage-by-stage
/batch-exe-prp --batch 43 --stage 1
/batch-exe-prp --batch 43 --stage 2
/batch-exe-prp --batch 43 --stage 3
```

**Batch metadata**: PRPs contain all necessary metadata for execution
- `stage`: Which stage the PRP belongs to
- `execution_order`: Order within batch
- `merge_order`: Global merge sequence
- `dependencies`: Other PRPs that must complete first
- `conflict_potential`: Merge conflict warning

---

## Error Handling

### 1. Circular Dependencies

**Detection**: Topological sort fails
**Error**:
```
❌ Circular dependency detected:
  Phase 2 → Phase 3 → Phase 4 → Phase 2

Please revise plan to break the cycle.
```

### 2. Agent Failures

**Behavior**: Continue with other agents (user requirement: "Continue with other 2? Yes")

**Example**:
```
Stage 2 (parallel): 3 agents
  ✓ PRP-43.2.1: SUCCESS
  ❌ PRP-43.2.2: FAILED (timeout)
  ✓ PRP-43.2.3: SUCCESS

Result: 2/3 PRPs generated, proceed to Stage 3
Failed PRPs can be retried later
```

### 3. No Heartbeat (2 Failed Polls)

**User requirement**: "second polling status failed = kill"

**Behavior**:
- Poll 1: No heartbeat → ⚠ WARNING
- Poll 2 (30s later): Still no heartbeat → ❌ KILL
- Mark as FAILED, continue with other agents

### 4. Invalid Plan Format

**Validation errors**:
```
❌ Plan validation failed:
  - Phase 3: Missing "Estimated Hours" field
  - Phase 5: "Dependencies" field references non-existent "Phase 9"

Please fix plan format and retry.
```

---

## Symmetry with `/batch-exe-prp`

### Shared Patterns

| Aspect | `/batch-gen-prp` | `/batch-exe-prp` |
|--------|------------------|------------------|
| **Coordinator Role** | Parse plan → spawn agents | Parse PRPs → spawn agents |
| **Subagent Type** | `general-purpose` | `general-purpose` |
| **Model** | Sonnet (generation) | Auto (execution) |
| **Parallelism** | Stage-based | Stage-based |
| **Polling Interval** | 30 seconds | 30 seconds |
| **Health Signals** | File timestamps | Git commit timestamps |
| **Status Levels** | HEALTHY/WARNING/STALLED | HEALTHY/WARNING/STALLED |
| **Kill Policy** | 2 failed polls | 10 minutes no commits |
| **Error Handling** | Continue on partial failure | Continue on partial failure |
| **Output Format** | JSON aggregation | JSON aggregation |

### Key Differences

| Aspect | `/batch-gen-prp` | `/batch-exe-prp` |
|--------|------------------|------------------|
| **Input** | Plan markdown file | Generated PRP files |
| **Output** | PRP files + Linear issues | Code changes in worktrees |
| **Work Location** | Single directory | Git worktrees |
| **Health Signal** | `.tmp/batch-gen/*.status` | Git log timestamps |
| **Cleanup** | Remove .tmp/ files | Remove worktrees |

---

## Example Plan Document

See `examples/TOOL-PERMISSION-LOCKDOWN-PLAN.md` for complete example.

---

## Tips

1. **Clear goals**: Each phase should have one specific, measurable objective
2. **Explicit dependencies**: Always declare "Dependencies: Phase N" if needed
3. **File accuracy**: List all files that will be modified (used for conflict detection)
4. **Validation gates**: Make them copy-pasteable bash commands
5. **Reasonable hours**: 0.25-2h per phase (larger tasks = multiple phases)
6. **Review before execution**: Generated PRPs may need minor adjustments

---

## Next Steps

After batch generation:
1. Review all generated PRPs in `PRPs/feature-requests/PRP-{batch-id}.*`
2. Adjust any PRP details if needed
3. Execute entire batch: `/batch-exe-prp --batch {batch-id}`
4. Or execute stage-by-stage for more control
