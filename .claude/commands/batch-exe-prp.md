# /batch-exe-prp - Parallel PRP Execution with Monitoring

Execute multiple PRPs in parallel using subagents with health checks, real-time monitoring, and coordinated error handling.

## Usage

```
/batch-exe-prp [options] <prp-1> <prp-2> ... <prp-n>
```

**Examples:**
```bash
# Execute 3 PRPs in parallel (auto-selects model per PRP)
/batch-exe-prp PRP-A PRP-B PRP-C

# Force all PRPs to use Haiku (override auto-selection)
/batch-exe-prp --model haiku PRP-A PRP-B PRP-C

# Limit parallelism (useful for resource constraints)
/batch-exe-prp --max-parallel 2 PRP-A PRP-B PRP-C PRP-D

# Dry run (parse all PRPs, show model assignments)
/batch-exe-prp --dry-run PRP-A PRP-B PRP-C

# Continue on failure (don't abort if one PRP fails)
/batch-exe-prp --continue-on-error PRP-A PRP-B PRP-C
```

## What It Does

**Core Design**: Cohesive architecture with `/execute-prp`

- **Batch-exe-prp** (this command): Coordinator - analyzes PRPs, assigns models, launches parallel agents, monitors health, aggregates results
- **Execute-prp** (single PRP engine): Execution logic - phases, validation gates, self-healing, checkpoints (reused by batch agents)
- **No duplication**: Batch delegates to execute-prp via Task agents, doesn't reimplement PRP logic

### 1. Analyze PRP Complexity & Auto-Assign Models (Sequential)
**Time**: ~5-10 seconds per PRP

For each PRP, analyzes complexity and assigns optimal model (unless `--model` overrides):

**Complexity Analysis**:
```python
def complexity_weight(complexity):
    """Convert complexity label to numeric weight"""
    weights = {"low": 0.5, "medium": 1.0, "high": 1.5}
    return weights.get(complexity, 1.0)  # Default to medium

def analyze_prp_complexity(prp_path):
    # Read PRP file
    prp = read_prp(prp_path)

    # Extract metadata
    complexity = prp.yaml_header.get('complexity', 'medium')  # low/medium/high
    estimated_hours = prp.yaml_header.get('estimated_hours', 1.0)
    files_modified = len(prp.yaml_header.get('files_modified', []))
    phases = count_phases(prp.implementation_blueprint)

    # Calculate complexity score (0-100)
    # Score breakdown:
    # - Complexity weight: 0-60 points (low=20, medium=40, high=60)
    # - Hours: 0-30 points (capped at 3 hours)
    # - Files: 0-20 points (capped at 4 files)
    # - Phases: 0-10 points (capped at 3+ phases)
    score = (
        complexity_weight(complexity) * 40 +  # 20/40/60 points
        min(estimated_hours * 10, 30) +       # 30 points max
        min(files_modified * 5, 20) +         # 20 points max
        min(phases * 3, 10)                   # 10 points max
    )

    return score

def assign_model(score):
    if score < 40:
        return "haiku"    # Simple: single-file edits, <0.5h, low complexity
    elif score < 70:
        return "sonnet"   # Medium: multi-file, 0.5-2h, some judgment
    else:
        return "opus"     # High: architectural, >2h, critical decisions
```

**Model Assignment Report**:
```
🧠 Model Assignment (Auto-Selected)
============================================================
PRP-A: Tool Deny List Implementation
  Complexity: low | Hours: 0.25-0.33 | Files: 1 | Phases: 3
  Score: 37/100 → Model: haiku ✓
  Rationale: Simple JSON edit, single file, no architectural decisions
  Calculation: (0.5*40) + (0.29*10) + (1*5) + (3*3) = 20+2.9+5+9 = 37

PRP-B: Tool Usage Guide Creation
  Complexity: low | Hours: 0.33-0.42 | Files: 1 | Phases: 3
  Score: 38/100 → Model: haiku ✓
  Rationale: Straightforward doc creation, clear structure
  Calculation: (0.5*40) + (0.38*10) + (1*5) + (3*3) = 20+3.8+5+9 = 38

PRP-C: Worktree Migration
  Complexity: medium | Hours: 0.42-0.50 | Files: 3 | Phases: 3
  Score: 69/100 → Model: sonnet ✓
  Rationale: Multi-file, doc structuring requires judgment
  Calculation: (1.0*40) + (0.46*10) + (3*5) + (3*3) = 40+4.6+15+9 = 69

============================================================
Thresholds: Haiku <40, Sonnet 40-69, Opus ≥70
Cost estimate: $0.05 (vs $0.25 all-sonnet = 80% savings)
```

### 2. Pre-Flight Validation (Sequential)
**Time**: ~10-30 seconds depending on PRP count

For each PRP:
- ✓ Validate PRP file exists and is readable
- ✓ Parse YAML headers (extract stage, worktree_path, conflict_potential)
- ✓ Check git worktree availability (if worktree_path specified)
- ✓ Verify no conflicting worktrees already active
- ✓ Run health check: `mcp__syntropy__healthcheck(detailed=True)`
- ✓ Estimate total execution time from PRP metadata

**Validation Report**:
```
📋 Pre-Flight Validation
============================================================
PRPs to execute: 3
Parallelism: 3 (max)
Model assignment: auto (haiku: 2, sonnet: 1)
Total estimated time: 20-25 minutes (45m sequential, 55% savings)

PRP-A: Tool Deny List Implementation [HAIKU]
  ✓ File exists: PRPs/feature-requests/PRP-A-tool-deny-list.md
  ✓ Stage: stage-1-parallel
  ✓ Worktree: ../ctx-eng-plus-prp-a (available)
  ✓ Conflict potential: MEDIUM
  ⏱ Estimated: 15-20 minutes

PRP-B: Tool Usage Guide Creation [HAIKU]
  ✓ File exists: PRPs/feature-requests/PRP-B-tool-usage-guide.md
  ✓ Stage: stage-1-parallel
  ✓ Worktree: ../ctx-eng-plus-prp-b (available)
  ✓ Conflict potential: NONE
  ⏱ Estimated: 20-25 minutes

PRP-C: Worktree Migration [SONNET]
  ✓ File exists: PRPs/feature-requests/PRP-C-gitbutler-worktree-migration.md
  ✓ Stage: stage-1-parallel
  ✓ Worktree: ../ctx-eng-plus-prp-c (available)
  ✓ Conflict potential: LOW
  ⏱ Estimated: 25-30 minutes

✅ All validations passed
🚀 Ready to execute
============================================================
```

**Abort conditions**:
- ❌ Any PRP file not found
- ❌ Conflicting stages (e.g., stage-1 + stage-2 PRPs)
- ❌ Worktree path conflicts
- ❌ MCP server health check failed
- ❌ Git repo not clean (uncommitted changes)

### 3. Create Git Worktrees (Sequential)
**Time**: ~5-10 seconds

If PRPs specify `worktree_path` in YAML headers:
```bash
git worktree add ../ctx-eng-plus-prp-a -b prp-a-tool-deny
git worktree add ../ctx-eng-plus-prp-b -b prp-b-usage-guide
git worktree add ../ctx-eng-plus-prp-c -b prp-c-worktree-migration
```

**Output**:
```
🌳 Creating worktrees...
  ✓ Created: ../ctx-eng-plus-prp-a (branch: prp-a-tool-deny)
  ✓ Created: ../ctx-eng-plus-prp-b (branch: prp-b-usage-guide)
  ✓ Created: ../ctx-eng-plus-prp-c (branch: prp-c-worktree-migration)
```

### 4. Launch Parallel Execution (Parallel)
**Time**: Variable (depends on PRP complexity)

**Delegates to `/execute-prp` via Task agents** (in single message with multiple Task calls):

```python
# Parallel agent launch (sent in single message)
# Agent A: PRP-A (Haiku)
Task(
  subagent_type="general-purpose",
  model="haiku",  # Auto-assigned based on complexity score
  description="Execute PRP-A",
  prompt=f"""
You are a PRP execution agent. Execute the following PRP using /execute-prp logic.

**PRP**: PRPs/feature-requests/PRP-A-tool-deny-list.md
**Worktree**: /Users/bprzybysz/nc-src/ctx-eng-plus-prp-a
**Branch**: prp-a-tool-deny
**Model**: haiku (auto-assigned: complexity score 25/100)

**Execution Protocol**:
1. Change working directory to worktree: `cd /Users/bprzybysz/nc-src/ctx-eng-plus-prp-a`
2. Read PRP file completely to understand all implementation steps
3. Execute /execute-prp logic (phases, validation gates, self-healing, checkpoints):
   - Parse implementation blueprint (extract phases)
   - For each phase:
     a. Execute implementation steps
     b. Run L1 validation (syntax & style)
     c. Run L2 validation (unit tests)
     d. Run L3 validation (integration tests)
     e. Run L4 validation (pattern conformance, drift <30%)
     f. Create checkpoint: git commit
   - Self-heal L1-L2 errors (max 3 attempts)
   - Escalate if persistent/architectural/security errors
4. Commit all changes to branch with message format: "PRP-A: <summary>"
5. Return execution report (see format below)

**Health Check Protocol** (output every 5 minutes):
```
HEALTH:OK
HEALTH:ERROR:<reason>
```

**Progress Updates** (output on phase completion):
```
STATUS:PHASE_COMPLETE:1/3
STATUS:VALIDATION:L2
STATUS:SELF_HEAL:attempt_2
```

**Completion Signal**:
```
STATUS:COMPLETE:10/10        # Success (confidence score)
STATUS:FAILED:L3_timeout     # Failure reason
STATUS:PARTIAL:2/3           # Partial completion
```

**Return Format** (final report):
{{
  "prp_id": "PRP-A",
  "status": "SUCCESS|FAILED|PARTIAL",
  "phases_completed": 3,
  "phases_total": 3,
  "confidence_score": 10,
  "validation_results": {{
    "L1": {{"passed": true, "attempts": 1}},
    "L2": {{"passed": true, "attempts": 1}},
    "L3": {{"passed": true, "attempts": 1}},
    "L4": {{"passed": true, "drift_score": 4.2}}
  }},
  "self_heals": 0,
  "commit_hash": "ab3118f",
  "execution_time": "6m 12s",
  "files_modified": [".claude/settings.local.json"],
  "errors": []
}}

**Error Handling**:
- L1-L2: Attempt self-healing (max 3 attempts per error)
- L3-L4: Escalate, no auto-healing
- Persistent errors (same error 3x): Escalate
- Architectural errors: Escalate immediately
- Security errors: Escalate immediately, DO NOT auto-fix

**Constraints**:
- Work only in worktree, never touch main repo
- All validation gates must pass (L1-L4)
- Drift score must be <30%
- Create checkpoint (git commit) after each phase
"""
)

# Agent B: PRP-B (Haiku)
Task(
  subagent_type="general-purpose",
  model="haiku",
  description="Execute PRP-B",
  prompt="<same structure as PRP-A, with PRP-B details>"
)

# Agent C: PRP-C (Sonnet - higher complexity)
Task(
  subagent_type="general-purpose",
  model="sonnet",
  description="Execute PRP-C",
  prompt="<same structure as PRP-A, with PRP-C details>"
)
```

**Key Points**:
- **No logic duplication**: Agents follow /execute-prp protocol (phases, validation, self-healing)
- **Model assignment**: Auto-selected based on complexity analysis (Step 1)
- **Health monitoring**: Agents output health signals every 5 minutes
- **Parallel launch**: All Task calls in single message for true parallelism

### 5. Monitor Execution (Git Log Polling)
**Time**: Continuous during execution

**Monitoring Mechanism**: Poll git logs every 60 seconds for checkpoint commits

**Polling Logic**:
```bash
# For each worktree
for worktree in worktrees:
    latest_commit=$(git -C $worktree log -1 --oneline)
    commit_time=$(git -C $worktree log -1 --format=%ct)
    current_time=$(date +%s)
    age=$((current_time - commit_time))

    if [ $age -lt 300 ]; then
        echo "HEALTHY: Latest commit ${age}s ago"
    elif [ $age -lt 600 ]; then
        echo "WARNING: Last commit ${age}s ago (may be stalled)"
    else
        echo "STALLED: No commits for ${age}s (likely hung)"
    fi
done
```

**Monitoring Dashboard** (updates every 60 seconds):
```
📊 Batch Execution Status (Updated: 10:45:23)
============================================================
Elapsed: 12m 34s / Estimated: 45m (28% complete)

PRP-A: Tool Deny List Implementation [HEALTHY]
  Last commit: 2m ago "Phase 3: Validation complete"
  Branch: prp-a-tool-deny-list
  Status: Likely completing final phase

PRP-B: Tool Usage Guide Creation [HEALTHY]
  Last commit: 1m ago "Phase 2: Implementation complete"
  Branch: prp-b-tool-usage-guide
  Status: Moving to Phase 3

PRP-C: Worktree Migration [WARNING]
  Last commit: 8m ago "Phase 1: Preparation complete"
  Branch: prp-c-worktree-migration
  Status: May be stalled on Phase 2 (long-running step)

============================================================
Active: 3 | HEALTHY: 2 | WARNING: 1 | STALLED: 0
Timeout: 60m per PRP (fallback if no commits for >10m)
```

**Health Status Criteria**:
- **HEALTHY**: Last commit <5m ago
- **WARNING**: Last commit 5-10m ago (may be long-running phase)
- **STALLED**: Last commit >10m ago (likely hung, check agent timeout)
- **FAILED**: Agent returned error or timeout exceeded

**Stall Handling**:
```
⚠️ PRP-B stalled (no commits for 12m)
Actions:
  1. Check Task agent timeout (60m default)
  2. Agent still running → wait for timeout
  3. Agent timed out → mark FAILED, preserve worktree
  4. Review partial work: cd ../ctx-eng-plus-prp-b && git log

Note: Cannot forcibly abort Task agents mid-execution
Rely on Task timeout mechanism for automatic abort
```

### 6. Aggregate Results (Sequential)
**Time**: ~10-30 seconds

After all agents complete (or timeout):

```python
# Collect results from all agents
results = {
  "PRP-A": agent_a.result,
  "PRP-B": agent_b.result,
  "PRP-C": agent_c.result
}

# Calculate aggregate metrics
total_phases = sum(r.phases_completed for r in results.values())
total_errors = sum(len(r.errors) for r in results.values())
avg_confidence = mean(r.confidence_score for r in results.values())
```

**Aggregate Report**:
```
📊 Batch Execution Complete
============================================================
Total Time: 18m 42s (estimated: 45m, 58% faster)
PRPs Executed: 3 | Succeeded: 3 | Failed: 0

PRP-A: Tool Deny List Implementation [✅ SUCCESS]
  Phases: 3/3 completed
  Validation: L1-L4 passed
  Confidence: 10/10
  Commit: ab3118f "Add 55 MCP tools to deny list, clean duplicates"
  Execution time: 6m 12s

PRP-B: Tool Usage Guide Creation [✅ SUCCESS]
  Phases: 3/3 completed
  Validation: L1-L4 passed
  Confidence: 10/10
  Commit: 43051cb "Create comprehensive tool usage guide"
  Execution time: 8m 35s

PRP-C: Worktree Migration [✅ SUCCESS]
  Phases: 3/3 completed
  Validation: L1-L4 passed
  Confidence: 9/10 (1 self-heal: remove duplicate hooks)
  Commit: 388508b "Migrate from GitButler to git worktree documentation"
  Execution time: 10m 18s

============================================================
Aggregate Metrics:
  Total phases: 9/9
  Avg confidence: 9.7/10
  Total errors: 0
  Self-heals: 1
  Time savings: 26m 18s (58%)

✅ All PRPs executed successfully
```

### 7. Merge Worktrees (Sequential)
**Time**: ~30-60 seconds

If PRPs executed in worktrees, merge in `merge_order` from YAML headers:

```bash
# Switch to main branch
git checkout main

# Merge in order (A → B → C)
git merge prp-a-tool-deny --no-ff -m "Merge PRP-A: Tool Deny List Implementation"
git merge prp-b-usage-guide --no-ff -m "Merge PRP-B: Tool Usage Guide Creation"
git merge prp-c-worktree-migration --no-ff -m "Merge PRP-C: GitButler to Worktree Migration"
```

**Conflict Detection**:
```
⚠️ Merge conflict detected: PRP-D
File: .claude/settings.local.json
Conflict markers found at lines 145-152

Conflict Resolution Required:
  1. Read file to view conflict markers (<<<<<<< HEAD)
  2. Decide on resolution strategy (keep both, prefer incoming, prefer current)
  3. Use Edit tool to remove markers and merge changes
  4. Stage resolved file: git add .claude/settings.local.json
  5. Complete merge: git commit -m "Merge PRP-D: Resolve settings conflict"

Pausing batch execution until conflict resolved.
```

**If `--continue-on-error` flag set**:
- Skip failed PRP merge
- Log conflict details
- Continue with remaining PRPs

### 8. Cleanup (Sequential)
**Time**: ~5-10 seconds

```bash
# Remove worktrees
git worktree remove ../ctx-eng-plus-prp-a
git worktree remove ../ctx-eng-plus-prp-b
git worktree remove ../ctx-eng-plus-prp-c

# Prune stale references
git worktree prune

# Update context (sync PRPs with codebase)
cd tools && uv run ce update-context
```

**Output**:
```
🧹 Cleanup complete
  ✓ Removed 3 worktrees
  ✓ Pruned stale references
  ✓ Updated context (drift: 3.2%)
```

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--model <sonnet\|haiku\|opus>` | Model for subagents | `sonnet` |
| `--max-parallel <N>` | Max concurrent PRPs | `unlimited` |
| `--dry-run` | Parse PRPs without execution | `false` |
| `--continue-on-error` | Don't abort if one PRP fails | `false` |
| `--no-merge` | Skip worktree merge step | `false` |
| `--no-cleanup` | Keep worktrees after execution | `false` |
| `--timeout <minutes>` | Max execution time per PRP | `60` |
| `--health-check-interval <seconds>` | Health check frequency | `30` |
| `--json` | Output results as JSON | `false` |

## Model Selection Guidelines

**Default Behavior**: Automatic model assignment based on complexity analysis (see Step 1)

The batch executor analyzes each PRP and assigns the optimal model:
- **Haiku**: Score <40 (simple, single-file, <0.5h)
- **Sonnet**: Score 40-69 (medium, multi-file, 0.5-2h)
- **Opus**: Score ≥70 (complex, architectural, >2h)

### When to Override with `--model` Flag

**Scenario 1: Force Haiku (maximize cost savings)**
```bash
/batch-exe-prp --model haiku PRP-A PRP-B PRP-C
```

**Use when**:
- All PRPs are simple (you've verified manually)
- Cost is priority over execution quality
- You're willing to manually fix if Haiku makes mistakes

**Risk**: Haiku may struggle with:
- Ambiguous requirements (needs clarification)
- Multi-file coordination (may miss dependencies)
- Complex judgment calls (doc structure, error handling)

**Example**: 3 simple PRPs (JSON edits, straightforward docs)
- Auto (Haiku: 2, Sonnet: 1): ~$0.05
- Forced Haiku: ~$0.03 (40% cheaper, but higher risk)

**Scenario 2: Force Sonnet (reliability priority)**
```bash
/batch-exe-prp --model sonnet PRP-A PRP-B PRP-C
```

**Use when**:
- Some PRPs auto-assigned Haiku, but you want consistency
- You don't trust Haiku with your codebase
- Budget allows, prefer reliability

**Benefit**: Higher success rate, fewer escalations, better judgment

**Example**: 3 mixed PRPs (auto: Haiku: 2, Sonnet: 1)
- Auto: ~$0.05 (optimal)
- Forced Sonnet: ~$0.25 (5x cost, minimal quality gain for simple PRPs)

**Scenario 3: Force Opus (critical changes)**
```bash
/batch-exe-prp --model opus PRP-D PRP-E
```

**Use when**:
- Database migrations, security patches, infrastructure changes
- Confidence score must be 10/10
- Rollback would be costly/dangerous

**Cost**: ~$1.50-3.00 per PRP (10-15x more than Sonnet)

### Recommendation

**Trust auto-selection** unless you have specific reasons:
- ✅ Optimizes cost/quality trade-off per PRP
- ✅ Analyzes complexity objectively (not based on gut feeling)
- ✅ Saves 50-80% vs all-Sonnet (typical batch)

**Override only when**:
- 🔧 You've manually reviewed all PRPs and disagree with assignments
- 🔧 You have budget constraints (force Haiku)
- 🔧 You have reliability requirements (force Sonnet/Opus)

## Monitoring Protocol

### Real-Time Status Updates

**Agent Health Signals** (every 30 seconds):
```
HEALTH:OK                           # Agent running normally
HEALTH:ERROR:timeout                # Validation timeout
HEALTH:ERROR:import_error:foo.py    # Import error detected
```

**Progress Updates** (every phase completion):
```
STATUS:PHASE_COMPLETE:1/3           # Phase 1 of 3 done
STATUS:VALIDATION:L2                # Running L2 validation
STATUS:SELF_HEAL:attempt_2          # Self-healing (attempt 2/3)
```

**Completion Signals**:
```
STATUS:COMPLETE:10/10               # Success (confidence: 10/10)
STATUS:FAILED:L3_timeout            # Failed at L3 validation
STATUS:PARTIAL:2/3                  # Partial (2 of 3 phases done)
```

### Error Aggregation

All errors logged to `.ce/batch-execution-{timestamp}.log`:

```
[2025-10-29 10:45:23] PRP-A | ERROR | L2 | ImportError: No module named 'foo'
[2025-10-29 10:45:25] PRP-A | HEAL  | L2 | Added import foo at line 12
[2025-10-29 10:45:30] PRP-A | OK    | L2 | Passed after 1 self-heal
[2025-10-29 10:52:18] PRP-B | ERROR | L4 | Drift score 35% exceeds threshold
[2025-10-29 10:52:20] PRP-B | ABORT | L4 | User acceptance required
```

### Escalation Triggers

**Immediate Escalation** (pause batch execution):
1. **Security Error**: CVE detected, credentials exposed
2. **Critical Failure**: Agent crashed, worktree corrupted
3. **Merge Conflict**: Automatic merge failed (see Conflict Resolution)
4. **Drift Spike**: L4 drift >30% (user acceptance required)
5. **Resource Exhaustion**: Disk full, memory exhausted

**Deferred Escalation** (complete batch, report at end):
1. **Low Confidence**: Confidence score <7/10
2. **Self-Heal Excessive**: >5 self-healing attempts
3. **Partial Success**: Some phases completed, others skipped

## Conflict Resolution

When merge conflicts occur:

**Step 1: Detect Conflict**
```bash
git merge prp-d-command-perms --no-ff
# Auto-merging .claude/settings.local.json
# CONFLICT (content): Merge conflict in .claude/settings.local.json
# Automatic merge failed; fix conflicts and then commit the result.
```

**Step 2: Analyze Conflict**
```python
# Read conflicted file
Read(file_path=".claude/settings.local.json")
# Look for conflict markers: <<<<<<< HEAD, =======, >>>>>>>
```

**Step 3: Resolution Strategy**

**Option A: Keep Both Changes** (most common)
```python
Edit(
  file_path=".claude/settings.local.json",
  old_string="""<<<<<<< HEAD
  "deny": ["tool-a", "tool-b"]
=======
  "deny": ["tool-c", "tool-d"]
>>>>>>> prp-d-command-perms""",
  new_string="""  "deny": ["tool-a", "tool-b", "tool-c", "tool-d"]"""
)
```

**Option B: Prefer Incoming** (last-merged wins)
```python
Edit(
  file_path=".claude/settings.local.json",
  old_string="""<<<<<<< HEAD
  "allow": ["Bash(git:*)"]
=======
  "allow": ["Bash(gh:*)"]
>>>>>>> prp-d-command-perms""",
  new_string="""  "allow": ["Bash(gh:*)"]"""  # Prefer incoming
)
```

**Option C: Manual Decision** (conflicting logic)
- User chooses which change to keep
- Update PRP priority/dependency order
- Re-run batch with adjusted order

**Step 4: Complete Merge**
```bash
git add .claude/settings.local.json
git commit -m "Merge PRP-D: Resolve settings conflict (kept both)"
```

## Error Handling

### Agent Failures

**Scenario 1: Agent Timeout**
```
❌ PRP-B agent timeout (60 minutes exceeded)
Last status: L3 integration tests (running for 45m)

Actions taken:
  1. Marked PRP-B as FAILED
  2. Preserved worktree: ../ctx-eng-plus-prp-b
  3. Logged partial results to .ce/batch-execution.log

Manual intervention required:
  cd ../ctx-eng-plus-prp-b
  # Review partial work, continue manually if needed
```

**Resolution**:
- Review agent log for bottleneck
- Increase timeout: `--timeout 90`
- Split PRP into smaller phases

**Scenario 2: Agent Crash**
```
❌ PRP-C agent crashed (unexpected error)
Stack trace: [shows error details]

Actions taken:
  1. Marked PRP-C as FAILED
  2. Worktree preserved for debugging
  3. Other agents continue execution

Manual intervention:
  Review stack trace for root cause
  Check if bug in /execute-prp logic
  Re-run individually: /execute-prp PRP-C
```

### Validation Failures

**Scenario 3: L4 Drift Threshold Exceeded**
```
⚠️ PRP-B validation failed: L4 drift 35% (threshold: 30%)

User decision required:
  1. [A]ccept drift (update threshold in PRP)
  2. [R]eject and rollback (restore to checkpoint)
  3. [M]anually fix and re-validate

Pausing batch execution for user input...
```

**With `--continue-on-error`**:
- Mark PRP-B as PARTIAL
- Skip to next PRP (C)
- Report failure in aggregate results

## Performance Metrics

### Sequential vs Parallel

**3 PRPs (15m each)**:
- Sequential: 45 minutes
- Parallel (3 agents): ~18 minutes (60% faster)
- Parallel (Haiku): ~15 minutes (67% faster, 90% cheaper)

**6 PRPs (15m each)**:
- Sequential: 90 minutes
- Parallel (unlimited): ~20 minutes (78% faster)
- Parallel (--max-parallel 3): ~35 minutes (61% faster)

### Resource Usage

**Per Agent** (Sonnet):
- CPU: ~30-50% (1 core)
- Memory: ~500MB-1GB
- Tokens: ~10k-30k per PRP

**Total** (3 agents):
- CPU: ~100-150% (1.5 cores)
- Memory: ~1.5-3GB
- Tokens: ~30k-90k total

**Recommendation**: Limit to 3-4 parallel agents on typical laptop (4-core, 16GB RAM)

## Output Formats

### Standard Output (default)

Human-readable dashboard with progress bars, health status, and aggregate report (shown in sections 4-5 above).

### JSON Output (`--json`)

```json
{
  "success": true,
  "prps_total": 3,
  "prps_succeeded": 3,
  "prps_failed": 0,
  "prps_partial": 0,
  "execution_time": "18m 42s",
  "estimated_time": "45m",
  "time_savings": "26m 18s (58%)",
  "model": "sonnet",
  "max_parallel": 3,
  "results": {
    "PRP-A": {
      "prp_id": "PRP-A",
      "status": "SUCCESS",
      "phases_completed": 3,
      "phases_total": 3,
      "confidence_score": 10,
      "validation_results": {
        "L1": {"passed": true, "attempts": 1},
        "L2": {"passed": true, "attempts": 1},
        "L3": {"passed": true, "attempts": 1},
        "L4": {"passed": true, "drift_score": 4.2}
      },
      "self_heals": 0,
      "commit_hash": "ab3118f",
      "execution_time": "6m 12s",
      "files_modified": [".claude/settings.local.json"],
      "errors": []
    },
    "PRP-B": { /* similar structure */ },
    "PRP-C": { /* similar structure */ }
  },
  "aggregate_metrics": {
    "total_phases": 9,
    "total_phases_completed": 9,
    "avg_confidence_score": 9.7,
    "total_self_heals": 1,
    "total_errors": 0
  },
  "merge_status": {
    "success": true,
    "conflicts": [],
    "commits": [
      "920edd4 Merge PRP-A: Tool Deny List Implementation",
      "9af5bcc Merge PRP-B: Tool Usage Guide Creation",
      "b53e184 Merge PRP-C: GitButler to Worktree Migration"
    ]
  },
  "cleanup_status": {
    "worktrees_removed": 3,
    "context_drift": 3.2
  }
}
```

## Common Workflows

### Workflow 1: Stage-Based Execution

Execute all PRPs from a single stage (e.g., Stage 1):

```bash
# Extract stage-1 PRPs from REPLKAN
grep "stage-1-parallel" TOOL-LOCKDOWN-REPLKAN.md
# Output: PRP-A, PRP-B, PRP-C

# Execute in parallel
/batch-exe-prp PRP-A PRP-B PRP-C

# After completion, proceed to Stage 2
/batch-exe-prp PRP-D PRP-E
```

### Workflow 2: Cost-Optimized Execution

Use Haiku for simple PRPs, Sonnet for complex:

```bash
# Stage 1 (simple edits): Use Haiku
/batch-exe-prp --model haiku PRP-A PRP-B

# Stage 2 (complex refactoring): Use Sonnet
/batch-exe-prp --model sonnet PRP-D PRP-E

# Cost savings: ~70% vs all-Sonnet
```

### Workflow 3: Incremental Rollout

Execute PRPs in batches, validate between batches:

```bash
# Batch 1: Low-risk PRPs
/batch-exe-prp PRP-A PRP-B
# Validate, test manually

# Batch 2: Medium-risk PRPs (only if Batch 1 succeeded)
/batch-exe-prp PRP-C PRP-D
# Validate, test manually

# Batch 3: High-risk PRPs (only if Batches 1-2 succeeded)
/batch-exe-prp PRP-E PRP-F
```

### Workflow 4: Dry Run + Review

Preview all PRPs before execution:

```bash
# Dry run: Parse PRPs, show execution plan
/batch-exe-prp --dry-run PRP-A PRP-B PRP-C

# Review output, adjust PRPs if needed

# Execute for real
/batch-exe-prp PRP-A PRP-B PRP-C
```

## Troubleshooting

### Issue: "Worktree path conflicts"

**Symptom**: Pre-flight validation fails with "worktree path already exists"

**Cause**: Previous worktree not cleaned up

**Solution**:
```bash
git worktree list  # Check existing worktrees
git worktree remove ../ctx-eng-plus-prp-a
git worktree prune
```

### Issue: "Agent stalled (no health signal)"

**Symptom**: Agent shows "STALLED" after 2+ minutes

**Cause**: Long-running validation (e.g., integration tests)

**Solution**: Increase health check interval
```bash
/batch-exe-prp --health-check-interval 60 PRP-A PRP-B
```

### Issue: "All agents failed immediately"

**Symptom**: All agents marked FAILED within seconds

**Cause**: MCP server disconnected or permission denied

**Solution**:
```bash
# Check MCP servers
mcp__syntropy__healthcheck(detailed=True)

# Reconnect if needed
/mcp

# Verify permissions in .claude/settings.local.json
```

### Issue: "Merge conflicts on every PRP"

**Symptom**: Every merge attempt results in conflicts

**Cause**: PRPs modifying same file sections, wrong merge order

**Solution**:
1. Review PRP YAML headers: check `files_modified` and `conflict_potential`
2. Adjust `merge_order` to sequence conflicting PRPs
3. Re-run batch with adjusted order
4. Consider splitting conflicting PRPs into separate batches

## CLI Command

```bash
# From project root
cd tools
uv run ce batch-exe [options] <prp-1> <prp-2> ...

# Options (same as slash command)
--model <sonnet|haiku|opus>
--max-parallel <N>
--dry-run
--continue-on-error
--no-merge
--no-cleanup
--timeout <minutes>
--json
```

## Implementation Details

- **Module**: `tools/ce/batch_execute.py` (to be implemented)
- **Tests**: `tools/tests/test_batch_execute.py` (integration tests)
- **Dependencies**: `execute.py` (PRP execution logic), `core.py` (git operations)
- **Agent Launch**: Uses Task tool with `subagent_type="general-purpose"`
- **Monitoring**: Polling agent output every 30 seconds for health signals
- **Error Recovery**: Preserves worktrees on failure for debugging

## Related Commands

- `/execute-prp <prp>` - Execute single PRP
- `/generate-prp <initial>` - Generate PRP with parallel metadata
- `/peer-review exe <prp>` - Review executed PRP quality
- `ce prp restore <prp-id> [phase]` - Rollback PRP to checkpoint

## Security Notes

1. **Isolation**: Each agent works in isolated worktree, cannot affect main repo
2. **Permissions**: Agents inherit same permissions as main session
3. **Secrets**: Never log credentials or API keys in batch execution logs
4. **Rollback**: All changes committed to branches, easy rollback via `git reset`

## Future Enhancements

- **Auto-retry**: Retry failed PRPs with adjusted parameters
- **Smart scheduling**: Prioritize high-conflict PRPs first
- **Resource management**: Auto-throttle based on CPU/memory usage
- **Dependency resolution**: Parse PRP dependencies, auto-sequence
- **Web UI**: Real-time dashboard with progress graphs
