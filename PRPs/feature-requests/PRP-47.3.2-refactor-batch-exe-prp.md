---
prp_id: PRP-47.3.2
title: Refactor /batch-exe-prp Command
status: planning
type: refactor
complexity: medium
estimated_hours: 4
priority: high
dependencies: [PRP-47.1.1, PRP-47.2.1, PRP-47.3.1]
batch_id: 47
stage: 4
---

# PRP-47.3.2: Refactor /batch-exe-prp Command

## Problem

The current /batch-exe-prp command implements execution coordination inline with ~400 lines of custom code. This creates:

- **Code duplication**: Coordination logic repeated from /batch-gen-prp
- **Inconsistent patterns**: Different monitoring approach (git log polling vs heartbeat)
- **Complex checkpoint logic**: Inline resume/retry implementation
- **Tight coupling**: Validation integration hardcoded

With orchestrator and executor subagent templates available (PRP-47.1.1), and lessons from /batch-gen-prp refactoring (PRP-47.3.1), we can:
- Reduce command to ~120 lines (70% reduction)
- Standardize on base-orchestrator.md pattern
- Use executor-subagent.md for implementation
- Reuse dependency_analyzer.py for stage assignment

## Solution

Refactor /batch-exe-prp to use:
1. **Base orchestrator template** for 6-phase coordination
2. **Executor subagent template** for PRP implementation
3. **Dependency analyzer** for stage assignment (parallel execution in same stage)
4. **Git log monitoring** (not heartbeat files - different from gen)

The refactored command will:
- Parse batch ID or PRP list → load PRP files
- Validate PRP readiness (status, dependencies)
- Analyze dependencies (staging for parallel execution)
- Spawn executor subagents (one per stage, parallel within stage)
- Monitor via git log polling (checkpoint commits)
- Run validation (L1-L4) after each phase
- Aggregate results → update PRP status

## Implementation

### Phase 1: Extract Current Logic Patterns (1 hour)

**Read and analyze**:
- `.claude/commands/batch-exe-prp.md`

**Document**:
- PRP loading and parsing
- Checkpoint/resume logic
- Validation integration (L1-L4)
- Git commit patterns
- Monitoring protocol (git log polling)
- Error handling and partial success

**Output**: Notes document with patterns to preserve

### Phase 2: Integrate Base Orchestrator (1 hour)

**Update**: `.claude/commands/batch-exe-prp.md`

**Changes**:
1. Add reference to `.claude/orchestrators/base-orchestrator.md`
2. Restructure command into 6 phases:
   - **Phase 1 (Parsing)**: Load PRP files from batch ID or explicit list
   - **Phase 2 (Validation)**: Verify PRPs ready (status=planning, deps met)
   - **Phase 3 (Analysis)**: Call dependency_analyzer.py for staging
   - **Phase 4 (Spawning)**: Launch executor subagents per stage
   - **Phase 5 (Monitoring)**: Poll git log for checkpoint commits
   - **Phase 6 (Aggregation)**: Collect results, update PRP status

3. Import orchestrator instructions:
```markdown
## Orchestration Pattern

This command follows the base orchestrator template:
{{include .claude/orchestrators/base-orchestrator.md}}

### Command-Specific Adaptations

- **Subagent Type**: Executor (PRP implementation)
- **Input**: PRP files with implementation phases
- **Output**: Completed PRPs with git commits and validation results
- **Monitoring**: Git log polling (checkpoint commits, not heartbeat files)
- **Resume Logic**: Check git log for existing phase commits, skip completed phases
```

**Lines reduced**: ~400 → ~200 (remove inline coordination logic)

### Phase 3: Integrate Executor Subagent (1.5 hours)

**Update**: `.claude/commands/batch-exe-prp.md`

**Changes**:
1. Add reference to `.claude/subagents/executor-subagent.md`
2. Define subagent input spec:
```json
{
  "prp_path": "/absolute/path/to/PRP-47.1.1.md",
  "resume_from": "phase_2",  // Optional, from git log analysis
  "validation_level": 4,
  "context": {
    "project_root": "{{project_root}}",
    "branch": "prp-47-1-1-implementation",
    "batch_id": "47",
    "stage": 1,
    "order": 1
  }
}
```

3. Define expected output:
```json
{
  "prp_id": "PRP-47.1.1",
  "status": "completed|partial|failed",
  "phases_completed": ["phase_1", "phase_2", "phase_3"],
  "validation_results": {
    "level_1": {"passed": true, "errors": []},
    "level_2": {"passed": true, "errors": []},
    "level_3": {"passed": true, "errors": []},
    "level_4": {"passed": true, "errors": []}
  },
  "git_commits": ["abc123", "def456", "ghi789"],
  "error": null  // or error message if failed
}
```

4. Subagent invocation:
```markdown
### Subagent Spawning

For each stage from dependency analyzer:
1. Group PRPs in stage
2. Check git log for existing phase commits (resume logic)
3. Spawn Haiku subagent per PRP (parallel within stage)
4. Pass executor-subagent.md + input spec
5. Subagent creates branch: prp-{{batch_id}}-{{stage}}-{{order}}
6. Subagent implements phases, creates checkpoint commits
7. Wait for all subagents in stage to complete
8. Merge branches to main (or batch branch)
9. Continue to next stage
```

**Lines reduced**: ~100 (remove inline implementation logic)

### Phase 4: Integrate Dependency Analyzer (30 minutes)

**Update**: `.claude/commands/batch-exe-prp.md`

**Changes**:
1. Add dependency analyzer integration:
```markdown
### Phase 3: Dependency Analysis

Extract PRP metadata:
- prp_id
- dependencies (from YAML frontmatter)
- files_modified (from PRP content)

Call dependency_analyzer.py:

\`\`\`bash
cd .ce/orchestration
python dependency_analyzer.py /tmp/batch-{{batch_id}}-prps.json
\`\`\`

Input format:
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

Output:
{
  "sorted_order": ["PRP-47.1.1", "PRP-47.2.1", ...],
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

If has_cycles=true: Stop and report error.
If file_conflicts: Warn user, serialize conflicting PRPs (different stages).
```

2. Add conflict resolution:
```markdown
### File Conflict Handling

If file_conflicts detected:
1. Move conflicting PRPs to separate stages (serialize)
2. Log warning: "File conflicts detected, serializing PRPs: {{prps}}"
3. Re-assign stages to avoid conflicts
4. Continue execution
```

**Lines reduced**: ~40 (remove manual staging logic)

### Phase 5: Update Monitoring Protocol (45 minutes)

**Update**: `.claude/commands/batch-exe-prp.md`

**Changes**:
1. Git log checkpoint format:
```markdown
### Git Checkpoint Commits

Each phase creates checkpoint commit:

Commit message format:
PRP-{{prp_id}}: Phase {{N}} - {{phase_title}}

Example:
PRP-47.1.1: Phase 1 - Create base orchestrator template
PRP-47.1.1: Phase 2 - Create generator subagent template
PRP-47.1.1: Phase 3 - Create executor subagent template
```

2. Update monitoring logic:
```markdown
### Phase 5: Monitoring

For each stage:
1. For each PRP in stage:
   - Poll git log every 30 seconds
   - Pattern: "PRP-{{prp_id}}: Phase"
   - Count matching commits = phases_completed
   - Compare with total phases in PRP
   - If no new commits for 120s: Check subagent status
   - If status=failed: Record error, continue with other PRPs
2. Once all PRPs in stage complete (or fail): Proceed to next stage
3. After each phase commit: Run validation (L1-L4)
4. If validation fails: Stop PRP, mark partial, continue with others
```

3. Add resume logic:
```markdown
### Resume from Checkpoint

Before spawning subagent:
1. Check git log for PRP commits
2. Count existing phase commits
3. If phases_completed > 0:
   - Pass resume_from="phase_{{N+1}}" to subagent
   - Subagent skips completed phases
4. Subagent continues from next phase
```

**Lines reduced**: ~50 (standardized protocol)

### Phase 6: Validation Integration & Testing (1 hour)

**Update**: `.claude/commands/batch-exe-prp.md`

**Changes**:
1. Keep validation integration (L1-L4):
```markdown
### Validation Integration

After each phase commit:
1. Run validation: uv run ce validate --level 4
2. Capture output:
   - Level 1 (structure): PASS/FAIL
   - Level 2 (syntax): PASS/FAIL
   - Level 3 (tests): PASS/FAIL
   - Level 4 (integration): PASS/FAIL
3. If any level fails:
   - Log error details
   - Stop current PRP (mark partial)
   - Continue with other PRPs in batch
4. Record validation results in subagent output
```

2. Update summary output:
```markdown
### Summary Output

\`\`\`
Batch {{batch_id}} Execution Complete

Total PRPs: {{total}}
Completed: {{completed}}
Partial: {{partial}}
Failed: {{failed}}
Time Elapsed: {{duration}}

Stage Breakdown:
  Stage 1: {{stage_1_results}}
  Stage 2: {{stage_2_results}} (parallel)
  Stage 3: {{stage_3_results}}

Validation Results:
  {{prp_id_1}}: ✓ All levels passed
  {{prp_id_2}}: ⚠ Level 3 failed (tests)
  {{prp_id_3}}: ✗ Level 1 failed (structure)

Git Commits:
  {{commit_1}}: PRP-47.1.1: Phase 1 - Foundation
  {{commit_2}}: PRP-47.1.1: Phase 2 - Generator
  ...

Next Steps:
  - Review partial PRPs: {{partial_prp_ids}}
  - Fix failed PRPs: {{failed_prp_ids}}
  - Update context: /batch-update-context --batch {{batch_id}}
\`\`\`
```

3. Add integration test:
```bash
# Test with 2 real PRPs
/batch-exe-prp --batch 47 --prps PRP-47.1.1,PRP-47.2.1

# Verify:
# - Both PRPs executed
# - Checkpoint commits created
# - Validation ran after each phase
# - PRP status updated to completed
```

## Validation

### Pre-Implementation Checks
- [ ] PRP-47.1.1 completed (orchestrator + executor subagent templates exist)
- [ ] PRP-47.2.1 completed (dependency_analyzer.py exists)
- [ ] PRP-47.3.1 completed (refactored gen command, lessons learned)
- [ ] Read current /batch-exe-prp.md to understand checkpoint logic
- [ ] Create 2 test PRPs for integration testing

### Post-Implementation Checks
- [ ] Executes 2 real PRPs end-to-end
- [ ] All 4 validation levels work correctly
- [ ] Checkpoints created after each phase (git commits)
- [ ] Git commits follow format: "PRP-{{id}}: Phase {{N}} - {{title}}"
- [ ] Parallel execution works (stage 2 with 3+ PRPs)
- [ ] Time to execute 4-phase PRP <30 minutes

### Integration Checks
- [ ] Orchestrator template patterns followed
- [ ] Executor subagent input/output spec matches
- [ ] Dependency analyzer output used correctly
- [ ] Git log monitoring protocol works

### Checkpoint & Resume Checks
- [ ] Resume from checkpoint works (skip completed phases)
- [ ] Git log parsing detects existing phase commits
- [ ] Partial completion handled correctly

## Acceptance Criteria

1. **Functionality Preserved**
   - All existing batch executions work without modification
   - Checkpoint/resume logic works correctly
   - Validation integration (L1-L4) works after each phase
   - Parallel execution in same stage works

2. **Code Reduction**
   - Command reduced to ~120 lines (from ~400)
   - Coordination logic delegated to orchestrator template
   - Implementation logic delegated to executor subagent
   - Dependency analysis delegated to analyzer

3. **Standardization**
   - Uses base-orchestrator.md 6-phase pattern
   - Uses executor-subagent.md input/output spec
   - Uses dependency_analyzer.py for staging
   - Git commit format standardized

4. **Error Handling**
   - Validation failures handled (partial completion)
   - File conflicts detected and resolved (serialization)
   - Subagent failures handled gracefully (continue with others)
   - Resume from checkpoint works

## Testing Strategy

### Unit Tests
- Defer to existing batch-exe-prp tests (if any)
- Focus on integration testing

### Integration Tests
1. **Test Case 1: Single PRP**
   - Execute PRP-47.1.1 (8 hours, 6 phases)
   - Verify: 6 checkpoint commits, all validation levels pass

2. **Test Case 2: Sequential PRPs**
   - Execute PRP-47.1.1, then PRP-47.2.1 (depends on 47.1.1)
   - Verify: 2 stages, correct order, dependencies respected

3. **Test Case 3: Parallel PRPs**
   - Execute PRP-47.2.1 and PRP-47.2.2 (both depend on 47.1.1, no conflicts)
   - Verify: Same stage, parallel execution, <2x time of single PRP

4. **Test Case 4: Resume from Checkpoint**
   - Start PRP execution, stop after phase 2
   - Resume execution
   - Verify: Phases 1-2 skipped, continues from phase 3

5. **Test Case 5: Validation Failure**
   - Execute PRP with intentional syntax error
   - Verify: Stops at validation failure, marks partial, continues with other PRPs

### Manual Testing
```bash
# Test 1: Single PRP
/batch-exe-prp --prps PRP-47.1.1

# Test 2: Batch execution
/batch-exe-prp --batch 47

# Test 3: Resume
/batch-exe-prp --batch 47 --resume

# Test 4: Stage-by-stage
/batch-exe-prp --batch 47 --stage 1
/batch-exe-prp --batch 47 --stage 2
```

## Risks & Mitigations

### Risk: Git log monitoring unreliable
**Impact**: Checkpoint detection fails, resume doesn't work
**Mitigation**: Test with real commits, verify pattern matching, add debug logging

### Risk: Validation integration breaks
**Impact**: Errors not caught, broken code merged
**Mitigation**: Keep validation logic unchanged, test all 4 levels

### Risk: Parallel execution race conditions
**Impact**: File conflicts cause corruption
**Mitigation**: Use dependency analyzer file conflict detection, serialize conflicting PRPs

### Risk: Resume logic fails
**Impact**: Duplicate work, wasted time
**Mitigation**: Test resume with various checkpoint scenarios (phase 1, phase 2, phase N)

### Risk: Performance regression
**Impact**: Execution slower than before
**Mitigation**: Benchmark existing command, target <30min for 4-phase PRP

### Risk: Subagent failures cascade
**Impact**: Entire batch fails
**Mitigation**: Isolate failures (continue with other PRPs), report partial success

## Dependencies

- **PRP-47.1.1**: Base orchestrator + executor subagent templates
- **PRP-47.2.1**: Dependency analyzer
- **PRP-47.3.1**: Refactored gen command (lessons learned)

## Related PRPs

- **Integration Test**: PRP-47.4.1 (test gen + exe together)
- **Similar Refactoring**: PRP-47.5.1 (review), PRP-47.5.2 (context-update)

## Files Modified

- `.claude/commands/batch-exe-prp.md` (refactor)

## Notes

- Git log monitoring is executor-specific (gen uses heartbeat files)
- Checkpoint/resume is critical feature (preserve carefully)
- Validation integration is critical (L1-L4 after each phase)
- File conflict resolution: Serialize conflicting PRPs (move to different stages)
- Performance target: <30 minutes for 4-phase PRP (existing baseline)
- This is second command to use orchestrator framework (learn from PRP-47.3.1)
