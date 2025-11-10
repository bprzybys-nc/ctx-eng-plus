# Iteration Orchestrator Template

**Purpose**: Coordinate init-project validation testing with parallel validation gates

**Architecture**: Sonnet orchestrator spawns Haiku subagents to validate gates in parallel

---

## Overview

The iteration orchestrator manages a 6-phase execution cycle for validating init-project on target projects:

```
PHASE 1: Parse & Validate Arguments
    ↓ (extract iteration number, project identifier)
PHASE 2: Setup & Reset Target
    ↓ (resolve project path, verify existence, reset to clean state)
PHASE 3: Initialize Project
    ↓ (run init-project, capture output)
PHASE 4: Spawn Validation Gates (Parallel)
    ↓ (spawn 5 independent gate validators as parallel Task agents)
PHASE 5: Monitor & Aggregate Results
    ↓ (wait for all gates, collect results, validate completeness)
PHASE 6: Report & Cleanup
    ↓ (generate comprehensive report, output summary)
```

---

## Phase 1: Parse & Validate Arguments

**Input**: User command `/iteration <number> <project-path-or-description>`

**Output**: Parsed structure with iteration_number and project_identifier

**Validation Checks**:
- Iteration number: either "auto" (auto-increment) or positive integer
- Project identifier: non-empty string
- Format validation: valid argument count

**Example Input**:
```
/iteration auto certinia-test-target
/iteration 5 /Users/bprzybyszi/nc-src/ctx-eng-plus-test-target
```

**Example Output**:
```python
{
    "iteration_number": 5,  # or auto-incremented value
    "project_identifier": "certinia-test-target"
}
```

---

## Phase 2: Setup & Reset Target

**Input**: Project identifier string

**Output**: Verified project path and confirmed reset to clean state

**Steps**:
1. Resolve project path:
   - If starts with `/` or `~` → use as absolute path
   - Otherwise → search for project in `~/nc-src/` with pattern matching
2. Verify project exists:
   - Check if directory exists
   - Check if it's a git repository
   - List recent commits to show status
3. Reset to clean state:
   - Get initial commit hash (git log --oneline --reverse | head -1)
   - Run `git reset --hard <hash>`
   - Run `git clean -fdx`
4. Create iteration branch:
   - Format: `iteration-<number>` (e.g., `iteration-5`)
   - git checkout -b iteration-<number>

**Example Output**:
```python
{
    "project_path": "/Users/bprzybyszi/nc-src/certinia-test-target",
    "project_name": "certinia-test-target",
    "branch": "iteration-5",
    "reset_hash": "abc1234",
    "reset_timestamp": "2025-11-10T19:30:00Z"
}
```

---

## Phase 3: Initialize Project

**Input**: Project path and confirmed clean state

**Output**: Init-project execution log and success/failure status

**Steps**:
1. Navigate to tools directory
2. Run init-project with logging:
   ```bash
   cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
   uv run ce init-project <project-path> 2>&1 | tee ../tmp/iteration-<number>.log
   ```
3. Capture:
   - Full log output
   - Exit code
   - Execution time
   - Any errors or warnings
4. Validate:
   - Exit code 0 = success
   - Non-zero exit = failure (collect error details)

**Example Output**:
```python
{
    "status": "SUCCESS",  # or "FAILED"
    "exit_code": 0,
    "duration_seconds": 45,
    "log_file": "tmp/iteration-5.log",
    "error_details": ""  # if applicable
}
```

---

## Phase 4: Spawn Validation Gates (Parallel)

**Input**: Target project path from Phase 3

**Output**: Task specifications written to disk for parallel execution

**Gates** (5 independent validators):

### Gate 1: Framework Structure Preserved
- Check: `.ce/.serena/memories/` exists
- Check: `.ce/memories/` does NOT exist (old location)
- Count: Framework memory files (should be 24)
- Status: PASS/FAIL

### Gate 2: Examples Migration
- Check: `.ce/examples/` exists
- Count: Migrated example files
- Check: Root `examples/` removed
- Status: PASS/FAIL

### Gate 3: PRPs Migration
- Check: `.ce/PRPs/` exists
- Count: Migrated PRP files
- Check: Root `PRPs/` removed
- Status: PASS/FAIL

### Gate 4: Memories Domain (conditional)
- Check: `.serena/memories/` exists (only if target had existing .serena/)
- Check: `.serena.old/` cleaned up
- Count: Memory files at canonical location
- Status: PASS/FAIL/N/A

### Gate 5: Critical Memories Present
- Check: code-style-conventions.md
- Check: task-completion-checklist.md
- Check: testing-standards.md
- Status: PASS/FAIL

**Parallel Execution Strategy**:
- Spawn 5 Task agents simultaneously in single message
- Each agent validates one gate independently
- No inter-gate dependencies (can run in parallel)
- Monitor via heartbeat files or polling

**Example Task Specification** (written to disk):
```json
{
    "task_id": "gate-1-framework-structure",
    "project_path": "/Users/bprzybyszi/nc-src/certinia-test-target",
    "validation_type": "framework_structure",
    "checks": [
        "framework_memories_exist",
        "old_location_removed",
        "memory_count_verification"
    ],
    "expected_outcomes": {
        "framework_memories_path": ".ce/.serena/memories",
        "forbidden_path": ".ce/memories",
        "memory_count": 24
    }
}
```

---

## Phase 5: Monitor & Aggregate Results

**Input**: Task specifications and project path

**Output**: Aggregated validation results from all 5 gates

**Monitoring**:
- Poll for result files: `tmp/gate-<N>-result.json`
- Timeout: 5 minutes (each gate should complete in <1 min)
- Failure handling: If gate times out, mark as FAILED
- Collect results in real-time as gates complete

**Aggregation**:
1. Wait for all 5 gates to complete
2. Parse result JSON from each gate
3. Count PASS/FAIL gates
4. Detect any issues or warnings
5. Determine overall status (ALL PASS = SUCCESS, ANY FAIL = FAILED)

**Example Aggregated Output**:
```python
{
    "overall_status": "SUCCESS",  # or "FAILED"
    "gates_passed": 5,
    "gates_failed": 0,
    "gate_results": {
        "gate-1-framework-structure": {
            "status": "PASS",
            "checks_passed": 3,
            "checks_failed": 0,
            "details": {...}
        },
        "gate-2-examples-migration": {
            "status": "PASS",
            ...
        },
        ...
    },
    "execution_time_seconds": 45,
    "timestamp": "2025-11-10T19:45:00Z"
}
```

---

## Phase 6: Report & Cleanup

**Input**: Aggregated validation results from Phase 5

**Output**: Comprehensive report file and summary output

**Report Generation**:
1. Create `tmp/iteration-<number>-report.md` with:
   - Header: iteration number, project, timestamp, branch
   - Validation results for each gate (detailed)
   - Issues found (if any)
   - Summary (pass/fail counts)
   - Confidence score (1-10)

2. Output to user:
   - Report location
   - Log file location
   - Gate results summary
   - Any critical issues
   - Next steps (if applicable)

**Example Report Structure**:
```markdown
# Iteration <number> - <Project Name>

**Date**: <timestamp>
**Target**: <project-path>
**Branch**: iteration-<number>
**Status**: ✅ SUCCESS / ❌ FAILED

## Validation Results

### ✅/❌ Gate 1: Framework Structure Preserved
- .ce/.serena/memories/: ✅ Exists
- Memory count: 24 ✅
- Old location removed: ✅

### ✅/❌ Gate 2: Examples Migration
- .ce/examples/: ✅ Exists
- Migrated examples: 14 ✅
- Root examples/ removed: ✅

... (Gates 3-5)

## Summary

Overall Status: ✅ SUCCESS (5/5 gates passed)
Confidence Score: 10/10
```

---

## Parallel Execution Benefits

**Sequential Approach** (current iteration.md):
- Gate execution: ~2-3 minutes (gates run one-by-one)
- Total time: ~5-7 minutes

**Parallel Approach** (this orchestrator):
- Gate execution: ~30-45 seconds (gates run simultaneously)
- Total time: ~3-4 minutes (40% faster)

**Token Efficiency**:
- Sequential: 5 separate execution contexts
- Parallel: Single validation dispatch, 5 concurrent contexts
- Estimated savings: 20-30% reduction in token overhead

---

## Key Design Principles

1. **Independent Gates**: All 5 validation gates have no inter-dependencies
2. **Concurrent Execution**: Spawn all gates in single Task message for true parallelism
3. **Fault Tolerance**: If one gate fails, others continue; aggregate final status
4. **Clear Reporting**: Detailed results for each gate, comprehensive summary
5. **Idempotent**: Reset ensures clean baseline for each iteration
6. **Atomic Reset**: Full project state reset ensures no cross-iteration contamination

---

## Integration with Iteration Command

The `/iteration` command orchestrates this template:

1. **User Input** → Phase 1 (Parse)
2. **Parse Logic** → Phase 2 (Setup)
3. **Init Execution** → Phase 3 (Initialize)
4. **Spawn Gates** → Phase 4 (Parallel validation)
5. **Collect Results** → Phase 5 (Monitor & Aggregate)
6. **Generate Report** → Phase 6 (Report & Cleanup)
7. **User Output** → Summary + file locations

---

## Error Handling Strategy

**Phase-Level Failures**:
- Phase 1: Invalid arguments → Prompt user with usage examples
- Phase 2: Project not found → Show searched paths, suggest fixes
- Phase 3: Init-project fails → Show error log, provide troubleshooting
- Phase 4: Gate spawn fails → Log error, continue with remaining gates
- Phase 5: Gate timeout → Mark as FAILED, continue aggregation
- Phase 6: Report generation fails → Output to stdout instead

**Gate-Level Failures**:
- Gate execution error → Capture exception, mark FAILED
- Gate timeout → Mark as FAILED with note
- Unexpected output format → Mark as FAILED with parsing error
- Partial results → Collect what's available, note missing data

---

## Testing Strategy

**Unit Tests**:
- Phase 1: Argument parsing with various input formats
- Phase 2: Project path resolution (absolute, relative, description)
- Phase 3: Init-project execution with mocked subprocess
- Phase 4: Task specification generation validation
- Phase 5: Result aggregation with various pass/fail combinations
- Phase 6: Report generation and file creation

**Integration Tests**:
- End-to-end on test-target project
- End-to-end on certinia-test-target project
- End-to-end with all gates passing
- End-to-end with selective gate failures
- Parallel execution verification (gates complete concurrently)

**Performance Tests**:
- Baseline: Sequential gate execution (~180s)
- Target: Parallel gate execution (~60s)
- Success: Parallel is 50%+ faster

---

## Files Modified by This Template

- `.claude/commands/iteration.md` - Updated to use orchestrator pattern
- `.claude/orchestrators/iteration-orchestrator.md` - This template
- `tmp/iteration-<number>.log` - Init-project execution log
- `tmp/iteration-<number>-report.md` - Validation report
- `tmp/gate-<N>-spec.json` - Task specifications (temp, cleaned up)
- `tmp/gate-<N>-result.json` - Gate results (temp, cleaned up)
