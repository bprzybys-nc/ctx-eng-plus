---
prp_id: PRP-47.5.2
title: Refactor /batch-update-context Command
status: completed
type: refactor
complexity: low
estimated_hours: 2
priority: high
dependencies: [PRP-47.1.1, PRP-47.2.1]
batch_id: 47
stage: 6
---

# PRP-47.5.2: Refactor /batch-update-context Command

## Problem

The current /batch-update-context command implements context synchronization inline with ~180 lines of custom code. This creates:

- **Code duplication**: Coordination logic repeated from other batch commands
- **Inconsistent patterns**: Different from gen/exe/review orchestration approach
- **Simple logic mixed with coordination**: Context update is straightforward but wrapped in complex coordination

Current approach:
- Sequential updates (one PRP at a time)
- Inline drift score calculation
- No parallel processing
- Coordination logic obscures simple transformation

With orchestrator and context-updater subagent templates available (PRP-47.1.1), we can:
- Reduce command to ~60 lines (67% reduction)
- Enable parallel updates (all PRPs updated simultaneously)
- Standardize on base-orchestrator.md pattern
- Delegate simple transformation to context-updater subagent

## Solution

Refactor /batch-update-context to use:
1. **Base orchestrator template** for 6-phase coordination
2. **Context-updater subagent template** for PRP status updates
3. **Parallel updates**: All PRPs updated simultaneously
4. **Dependency analyzer**: No staging needed (all updates independent)

The refactored command will:
- Parse batch ID or PRP list → load PRP files
- Validate PRPs executed (check git log for commits)
- Spawn context-updater subagents (all in parallel)
- Monitor via heartbeat files
- Aggregate drift scores → report summary

## Implementation

### Phase 1: Extract Current Context Update Patterns (20 minutes)

**Read and analyze**:
- `.claude/commands/batch-update-context.md`

**Document**:
- PRP loading and parsing
- Execution verification (git log check)
- Status update logic (planning → in_progress → completed)
- Drift score calculation
- Implementation notes format
- Summary output

**Output**: Notes document with patterns to preserve

### Phase 2: Integrate Base Orchestrator (20 minutes)

**Update**: `.claude/commands/batch-update-context.md`

**Changes**:
1. Add reference to `.claude/orchestrators/base-orchestrator.md`
2. Restructure command into 6 phases:
   - **Phase 1 (Parsing)**: Load PRP files from batch ID or explicit list
   - **Phase 2 (Validation)**: Verify PRPs executed (git log check)
   - **Phase 3 (Analysis)**: No staging needed (all updates independent)
   - **Phase 4 (Spawning)**: Launch context-updater subagents (all parallel)
   - **Phase 5 (Monitoring)**: Poll heartbeat files
   - **Phase 6 (Aggregation)**: Collect drift scores, generate summary

3. Import orchestrator instructions:
```markdown
## Orchestration Pattern

This command follows the base orchestrator template:
{{include .claude/orchestrators/base-orchestrator.md}}

### Command-Specific Adaptations

- **Subagent Type**: Context Updater (status sync)
- **Input**: PRP files + execution results (git log)
- **Output**: Updated PRP files with drift scores
- **Monitoring**: Heartbeat files (parallel updates)
- **No Staging**: All updates independent, single stage
```

**Lines reduced**: ~180 → ~100 (remove inline coordination logic)

### Phase 3: Integrate Context Updater Subagent (30 minutes)

**Update**: `.claude/commands/batch-update-context.md`

**Changes**:
1. Add reference to `.claude/subagents/context-updater-subagent.md`
2. Define subagent input spec:
```json
{
  "prp_path": "/absolute/path/to/PRP-47.1.1.md",
  "execution_result": {
    "status": "completed",
    "phases_completed": ["phase_1", "phase_2", "phase_3"],
    "git_commits": ["abc123", "def456", "ghi789"],
    "completion_date": "2025-11-10"
  },
  "validation_results": {
    "level_1": {"passed": true},
    "level_2": {"passed": true},
    "level_3": {"passed": true},
    "level_4": {"passed": true}
  }
}
```

3. Define expected output:
```json
{
  "prp_id": "PRP-47.1.1",
  "update_status": "updated|no_changes|failed",
  "drift_score": 0.05,
  "sections_updated": ["status", "implementation_notes", "validation"],
  "changes": {
    "status": "planning → completed",
    "validation_gates": "3 gates checked",
    "implementation_notes": "Added git commits, completion date"
  }
}
```

4. Subagent invocation:
```markdown
### Subagent Spawning

For each PRP (all in parallel):
1. Extract execution result from git log:
   - Commits: git log --grep="PRP-{{prp_id}}"
   - Phases: Count checkpoint commits
   - Completion: Latest commit timestamp

2. Spawn Haiku subagent:
   - Pass context-updater-subagent.md + input spec
   - Create heartbeat file: /tmp/context-{{batch_id}}-{{prp_id}}-heartbeat.json

3. Wait for all subagents to complete

4. Aggregate drift scores and update counts
```

**Lines reduced**: ~50 (remove inline update logic)

### Phase 4: Drift Score Calculation (20 minutes)

**Update**: `.claude/commands/batch-update-context.md`

**Clarify drift score formula**:
```markdown
### Drift Score Calculation

Drift score measures divergence between PRP spec and actual implementation:

\`\`\`python
# Extract files from PRP
prp_files = set(prp["files_modified"])

# Extract files from git log
git_files = set(git log --grep="PRP-{{prp_id}}" --name-only)

# Calculate drift
added_files = git_files - prp_files
removed_files = prp_files - git_files
drift = (len(added_files) + len(removed_files)) / max(len(prp_files), 1)

# Categorize
if drift < 0.05:
    status = "healthy"
elif drift < 0.15:
    status = "warning"
else:
    status = "critical"
\`\`\`

Interpretation:
- <5%: Implementation matches spec (healthy)
- 5-15%: Minor divergence (warning, acceptable)
- >15%: Significant divergence (critical, needs review)

Note: Drift >0 is normal (implementation details, helper functions).
Drift >15% indicates scope creep or missing PRP updates.
```

**Lines**: ~30 lines

### Phase 5: Summary Report & Testing (30 minutes)

**Update**: `.claude/commands/batch-update-context.md`

**Update report format**:
```markdown
### Summary Report Format

\`\`\`
Batch {{batch_id}} Context Update Complete

Total PRPs: {{total}}
Updated: {{updated}}
No Changes: {{no_changes}}
Failed: {{failed}}

Drift Score Summary:
  Healthy (<5%): {{healthy_count}}
  Warning (5-15%): {{warning_count}}
  Critical (>15%): {{critical_count}}

Details by PRP:

## PRP-{{prp_id_1}}: {{title}}
Status: {{old_status}} → {{new_status}}
Drift Score: {{drift}}% ({{status}})
Changes:
  - Updated status field
  - Added {{commit_count}} git commits
  - Checked {{gate_count}} validation gates
  - Added implementation notes

## PRP-{{prp_id_2}}: {{title}}
Status: {{old_status}} → {{new_status}}
Drift Score: {{drift}}% ({{status}})
Changes:
  - Updated status field
  - Added {{commit_count}} git commits

---

Drift Warnings:
  - PRP-{{prp_id}}: {{drift}}% ({{added_files_count}} unexpected files)

Drift Critical:
  - PRP-{{prp_id}}: {{drift}}% (significant scope change detected)

Next Steps:
1. Review critical drift PRPs: {{prp_list}}
2. Update PRP specs for warning-level drift if scope intentionally changed
3. Run /batch-peer-review if changes significant
\`\`\`
```

**Add integration test**:
```bash
# Test with 2 executed PRPs
/batch-update-context --batch 47 --prps PRP-47.1.1,PRP-47.2.1

# Verify:
# - Both PRPs updated in parallel
# - Drift scores calculated correctly
# - PRP files updated (status=completed)
# - Summary report generated
# - Test takes <3 minutes
```

## Validation

### Pre-Implementation Checks
- [ ] PRP-47.1.1 completed (orchestrator + context-updater subagent templates exist)
- [ ] PRP-47.2.1 completed (dependency_analyzer.py exists, though not used for staging)
- [ ] Read current /batch-update-context.md to understand drift calculation
- [ ] Create 2 test PRPs and execute them for testing

### Post-Implementation Checks
- [ ] Updates context for 2+ executed PRPs
- [ ] Drift scores calculated correctly (verify formula)
- [ ] PRP files updated with implementation status (status, commits, notes)
- [ ] Test takes <3 minutes for 2 PRPs (parallel execution)
- [ ] Summary report includes drift warnings and critical issues

### Integration Checks
- [ ] Orchestrator template patterns followed
- [ ] Context-updater subagent input/output spec matches
- [ ] Heartbeat monitoring protocol works
- [ ] Parallel updates work (all PRPs updated simultaneously)

### Drift Calculation Checks
- [ ] Drift score formula correct (|git_files - prp_files| / prp_files)
- [ ] Categorization correct (<5% healthy, 5-15% warning, >15% critical)
- [ ] Edge cases handled (no files in PRP, all files match)

## Acceptance Criteria

1. **Functionality Preserved**
   - All existing context update logic works (status, commits, notes)
   - Drift score calculation accurate
   - Summary report clear and actionable

2. **Code Reduction**
   - Command reduced to ~60 lines (from ~180)
   - Coordination logic delegated to orchestrator template
   - Update logic delegated to context-updater subagent

3. **Performance Improvement**
   - Parallel updates enabled (all PRPs updated simultaneously)
   - Time <3 minutes for 2 PRPs (vs ~4-5 minutes sequential)

4. **Enhanced Reporting**
   - Drift score summary (healthy/warning/critical counts)
   - Per-PRP drift details
   - Actionable next steps

## Testing Strategy

### Unit Tests
- Defer to existing batch-update-context tests (if any)
- Focus on integration testing

### Integration Tests
1. **Test Case 1: Update 2 Completed PRPs**
   - Execute 2 PRPs, then update context
   - Verify: Status updated, drift scores calculated, <3 min

2. **Test Case 2: Low Drift**
   - PRP spec matches implementation exactly
   - Verify: Drift <5%, status=healthy

3. **Test Case 3: High Drift**
   - Implementation touches 3 extra files not in PRP
   - Verify: Drift >15%, status=critical, warning in report

4. **Test Case 4: Parallel Updates**
   - Update 5 PRPs simultaneously
   - Verify: All updated in parallel, <5 min total

### Manual Testing
```bash
# Test 1: Update executed PRPs
/batch-update-context --batch 47

# Test 2: Update specific PRPs
/batch-update-context --prps PRP-47.1.1,PRP-47.2.1

# Test 3: Check drift scores
cat PRPs/feature-requests/PRP-47.1.1.md | grep "drift_score"

# Test 4: Verify summary report
# Should show drift categories and warnings
```

## Risks & Mitigations

### Risk: Drift score calculation inaccurate
**Impact**: Wrong assessment of implementation quality
**Mitigation**: Test with known drift scenarios (low/medium/high), verify formula

### Risk: Git log parsing fails
**Impact**: Execution results not extracted, updates fail
**Mitigation**: Use robust git log pattern, handle missing commits gracefully

### Risk: Parallel updates cause file conflicts
**Impact**: PRP files corrupted
**Mitigation**: Each subagent updates different file (one PRP per subagent), no conflicts possible

### Risk: Heartbeat monitoring unreliable
**Impact**: Updates appear to fail when running
**Mitigation**: Test with 5+ parallel updates, verify polling logic

### Risk: Status updates incorrect
**Impact**: PRP status wrong (planning vs completed)
**Mitigation**: Verify git log for commits before updating status

## Dependencies

- **PRP-47.1.1**: Base orchestrator + context-updater subagent templates
- **PRP-47.2.1**: Dependency analyzer (available but not used for staging)

## Related PRPs

- **Similar Refactoring**: PRP-47.3.1 (gen), PRP-47.3.2 (exe), PRP-47.5.1 (review)
- **Infrastructure**: PRP-47.1.1 (orchestrator)

## Files Modified

- `.claude/commands/batch-update-context.md` (refactor)

## Notes

- Simplest refactoring in PRP-47 batch (context update is straightforward transformation)
- No staging needed (all updates independent, single stage)
- Parallel updates provide performance improvement (5 PRPs in <5 min vs ~15 min sequential)
- Drift score is key metric for implementation quality
- Critical drift (>15%) should trigger PRP review and update
- Time savings: 2 PRPs = 2 min (parallel) vs 4 min (sequential)
