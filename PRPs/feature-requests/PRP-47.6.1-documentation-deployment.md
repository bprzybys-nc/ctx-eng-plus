---
prp_id: PRP-47.6.1
title: Documentation & Deployment
status: completed
type: documentation
complexity: low
estimated_hours: 2
priority: high
dependencies: [PRP-47.3.1, PRP-47.3.2, PRP-47.5.1, PRP-47.5.2]
batch_id: 47
stage: 7
completed_at: 2025-11-10T18:30:00Z
---

# PRP-47.6.1: Documentation & Deployment

## Problem

After completing the unified batch command framework (Phase 1), we need comprehensive documentation for:

- **New users**: How to use refactored batch commands
- **Developers**: How to extend or modify orchestrator framework
- **Troubleshooting**: Common issues and solutions
- **Migration**: Changes from old to new implementation

Without documentation:
- Adoption blocked (users don't know how to use new commands)
- Maintenance difficult (developers can't understand framework)
- Support burden high (repeated questions about same issues)
- Knowledge lost (implementation details not captured)

## Solution

Create comprehensive documentation suite covering:

1. **Usage Guide**: End-user documentation for batch commands
2. **Architecture Overview**: System design and patterns
3. **Subagent Reference**: Each subagent type documented
4. **Troubleshooting Guide**: Common issues and solutions
5. **Migration Notes**: Changes from old implementation

Documentation will be:
- Clear and concise (avoid technical jargon)
- Example-driven (show real usage scenarios)
- Actionable (every section has practical next steps)
- Maintainable (living documents, updated with framework)

After documentation, deploy Phase 1 to production.

## Implementation

### Phase 1: Usage Guide (45 minutes)

**Create**: `PRPs/feature-requests/PRP-47-USAGE-GUIDE.md`

**Content Structure**:
```markdown
# Unified Batch Command Framework - Usage Guide

## Overview
Quick reference for using refactored batch commands with unified orchestrator framework.

## Quick Start

### Generate PRPs from Plan
\`\`\`bash
/batch-gen-prp PRPs/feature-requests/MY-PLAN.md
\`\`\`

Creates PRPs with format: PRP-{batch_id}.{stage}.{order}-{slug}.md

### Execute Batch
\`\`\`bash
# Execute entire batch
/batch-exe-prp --batch 47

# Execute specific stage
/batch-exe-prp --batch 47 --stage 2

# Execute specific PRPs
/batch-exe-prp --prps PRP-47.1.1,PRP-47.2.1
\`\`\`

### Review Batch
\`\`\`bash
# Full review (structural + semantic)
/batch-peer-review --batch 47

# Structural only (fast)
/batch-peer-review --batch 47 --mode structural

# Review specific PRPs
/batch-peer-review --prps PRP-47.1.1,PRP-47.2.1
\`\`\`

### Update Context
\`\`\`bash
/batch-update-context --batch 47
\`\`\`

## Command Reference

### /batch-gen-prp
Generates structured PRPs from plan file.

**Input**: Plan markdown file with phases
**Output**: PRP files + Linear issues
**Time**: ~10 minutes for 4 PRPs
**Parallelization**: Phases in same stage generated in parallel

### /batch-exe-prp
Executes PRPs with checkpoint/resume.

**Input**: Batch ID or PRP list
**Output**: Implemented changes + git commits
**Time**: ~30 minutes for 4-phase PRP
**Parallelization**: PRPs in same stage executed in parallel

### /batch-peer-review
Reviews PRPs for quality and consistency.

**Input**: Batch ID or PRP list
**Output**: Review report with issues
**Time**: ~5 minutes for 3-4 PRPs
**Parallelization**: All PRPs reviewed in parallel
**Token Optimization**: 70%+ reduction via shared context

### /batch-update-context
Syncs PRP status with implementation.

**Input**: Batch ID or PRP list
**Output**: Updated PRP files + drift scores
**Time**: ~3 minutes for 2 PRPs
**Parallelization**: All PRPs updated in parallel

## Workflow Examples

### End-to-End Workflow
\`\`\`bash
# 1. Generate PRPs
/batch-gen-prp MY-FEATURE-PLAN.md

# 2. Review generated PRPs
/batch-peer-review --batch 50

# 3. Execute batch
/batch-exe-prp --batch 50

# 4. Update context
/batch-update-context --batch 50

# 5. Final review
/batch-peer-review --batch 50
\`\`\`

### Stage-by-Stage Execution
\`\`\`bash
# Execute stage 1 (foundation)
/batch-exe-prp --batch 50 --stage 1

# Review stage 1
/batch-peer-review --batch 50 --stage 1

# Execute stage 2 (parallel work)
/batch-exe-prp --batch 50 --stage 2

# Continue...
\`\`\`

## What's New in Phase 1

### Token Optimization
- Shared context in batch-peer-review (70%+ reduction)
- Example: 5 PRPs = 80k tokens saved (~$0.40)

### Parallel Execution
- Gen: Phases in same stage generated in parallel
- Exe: PRPs in same stage executed in parallel
- Review: All PRPs reviewed in parallel
- Context: All PRPs updated in parallel

### Unified Patterns
- All commands use base-orchestrator.md template
- Consistent 6-phase pattern (parsing, validation, analysis, spawning, monitoring, aggregation)
- Standardized subagent contracts

### Improved Error Handling
- Circular dependency detection (with cycle path)
- File conflict detection (serialization)
- Partial success handling (continue with other PRPs)
- Resume from checkpoint (exe only)

## Troubleshooting

See: `.claude/orchestrators/TROUBLESHOOTING.md`
```

**Lines**: ~150 lines

### Phase 2: Architecture Overview (30 minutes)

**Create**: `.claude/orchestrators/README.md`

**Content Structure**:
```markdown
# Orchestrator Architecture

## Overview
Unified coordination pattern for batch operations using Sonnet orchestrator + Haiku subagents.

## Design Principles

### Separation of Concerns
- **Orchestrator**: Coordination logic (spawning, monitoring, aggregation)
- **Subagent**: Task execution (generation, implementation, review, context sync)
- **Dependency Analyzer**: Graph analysis (topological sort, cycle detection, staging)

### Code Reusability
- Base orchestrator template shared by all commands
- Subagent templates provide consistent interfaces
- Dependency analyzer used by all commands

### Parallelization
- Stages assigned by dependency analyzer
- Items in same stage execute in parallel
- Orchestrator monitors all subagents simultaneously

## Architecture Diagram

\`\`\`
┌─────────────────────────────────────────────────────────────┐
│                    Batch Command                            │
│  (/batch-gen-prp, /batch-exe-prp, /batch-peer-review, etc) │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│              Base Orchestrator Template                     │
│  (6 phases: parsing, validation, analysis, spawning,       │
│   monitoring, aggregation)                                  │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┬─────────────┐
        ▼         ▼         ▼             ▼
    ┌─────┐  ┌─────┐  ┌─────┐      ┌──────────┐
    │ Gen │  │ Exe │  │Review│      │ Context  │
    │Subag│  │Subag│  │Subag │      │  Update  │
    │ent  │  │ent  │  │ent   │      │  Subagent│
    └─────┘  └─────┘  └─────┘      └──────────┘
        │         │         │             │
        └─────────┴─────────┴─────────────┘
                    │
                    ▼
          ┌──────────────────┐
          │ Dependency       │
          │ Analyzer         │
          │ (Python utility) │
          └──────────────────┘
\`\`\`

## Component Reference

### Base Orchestrator
- **File**: `.claude/orchestrators/base-orchestrator.md`
- **Purpose**: Coordination pattern template
- **Consumers**: All 4 batch commands
- **Key Features**: 6-phase pattern, monitoring protocol, error handling

### Subagent Templates
- **Generator**: `.claude/subagents/generator-subagent.md` (PRP creation)
- **Executor**: `.claude/subagents/executor-subagent.md` (implementation)
- **Reviewer**: `.claude/subagents/reviewer-subagent.md` (peer review)
- **Context Updater**: `.claude/subagents/context-updater-subagent.md` (status sync)

### Dependency Analyzer
- **File**: `.ce/orchestration/dependency_analyzer.py`
- **Purpose**: Graph analysis and staging
- **Features**: Topological sort, cycle detection, file conflict detection

## Extending the Framework

### Adding New Batch Command

1. Create command file: `.claude/commands/batch-new-operation.md`
2. Import base orchestrator template
3. Create subagent template: `.claude/subagents/new-operation-subagent.md`
4. Define input/output specs
5. Implement 6 phases
6. Add tests

Example: See PRP-47.3.1 (batch-gen-prp refactoring)

### Modifying Existing Command

1. Review base orchestrator template
2. Identify command-specific adaptations
3. Update subagent template if needed
4. Test changes with integration test

## Performance Metrics

### Code Reduction
- batch-gen-prp: 300 → 100 lines (66% reduction)
- batch-exe-prp: 400 → 120 lines (70% reduction)
- batch-peer-review: 250 → 80 lines (68% reduction)
- batch-update-context: 180 → 60 lines (67% reduction)

### Token Savings
- batch-peer-review: 70%+ reduction (shared context optimization)
- Example: 5 PRPs = 80k tokens saved (~$0.40)

### Time Savings
- Parallel execution: 60% reduction (3 PRPs sequential 45 min → parallel 18 min)
```

**Lines**: ~120 lines

### Phase 3: Subagent Reference (20 minutes)

**Create**: `.claude/subagents/README.md`

**Content Structure**:
```markdown
# Subagent Templates

## Overview
Reusable templates for Haiku subagents in batch operations.

## Template Structure

Each subagent template includes:
- Purpose and use cases
- Input specification (JSON schema)
- Output specification (JSON schema)
- Tool allowlist (relevant tools only)
- Process steps (numbered workflow)
- Examples

## Subagent Types

### Generator Subagent
**File**: `generator-subagent.md`
**Purpose**: Create structured PRP files from plan phases
**Used By**: /batch-gen-prp
**Key Features**: YAML generation, dependency linking, validation

### Executor Subagent
**File**: `executor-subagent.md`
**Purpose**: Implement PRP with checkpoint/resume
**Used By**: /batch-exe-prp
**Key Features**: Phase execution, git checkpoints, validation integration

### Reviewer Subagent
**File**: `reviewer-subagent.md`
**Purpose**: Peer review PRPs (structural + semantic)
**Used By**: /batch-peer-review
**Key Features**: Two-mode review, issue categorization, shared context

### Context Updater Subagent
**File**: `context-updater-subagent.md`
**Purpose**: Sync PRP status with implementation
**Used By**: /batch-update-context
**Key Features**: Drift score calculation, status updates, git log parsing

## Input/Output Contracts

### Standard Fields

All subagents accept:
- `context`: Shared execution context (project root, batch ID, stage)
- `options`: Command-specific options

All subagents return:
- `status`: "success|partial|failure"
- `error`: Error message if failure

### Example Input
\`\`\`json
{
  "task_specific_input": "...",
  "context": {
    "project_root": "/absolute/path",
    "batch_id": "47",
    "stage": 2,
    "order": 1
  }
}
\`\`\`

### Example Output
\`\`\`json
{
  "task_specific_output": "...",
  "status": "success",
  "error": null
}
\`\`\`

## Tool Allowlists

Subagents only use tools relevant to their task:
- **Generator**: Write, Read, Glob (file creation)
- **Executor**: Read, Edit, Write, Bash (implementation)
- **Reviewer**: Read, Grep, serena_find_symbol (analysis)
- **Context Updater**: Read, Edit, Bash (status sync)

## Best Practices

1. Keep subagents focused (single responsibility)
2. Use JSON input/output (structured data)
3. Include examples in templates
4. Document tool allowlist rationale
5. Handle errors gracefully (return error in output)
```

**Lines**: ~90 lines

### Phase 4: Troubleshooting Guide (30 minutes)

**Create**: `.claude/orchestrators/TROUBLESHOOTING.md`

**Content Structure**:
```markdown
# Troubleshooting Guide

## Common Issues

### Issue: "Circular dependency detected"

**Symptom**: batch-gen-prp or batch-exe-prp fails with cycle path error

**Cause**: Plan has circular dependencies (A → B → C → A)

**Solution**:
1. Review cycle path in error message
2. Fix plan file to break cycle
3. Regenerate PRPs

**Example**:
\`\`\`
Error: Circular dependency: Phase-1 → Phase-2 → Phase-3 → Phase-1
Fix: Remove Phase-3 → Phase-1 dependency
\`\`\`

---

### Issue: "File conflict detected"

**Symptom**: batch-exe-prp warns about file conflicts

**Cause**: Multiple PRPs in same stage modify same file

**Solution**: Conflicts automatically resolved by serialization (PRPs moved to different stages)

**Verification**: Check stage assignments in summary output

---

### Issue: "Subagent timeout"

**Symptom**: Heartbeat files show no updates for >60s

**Cause**: Subagent crashed or stuck

**Solution**:
1. Check subagent error log
2. Verify input spec format
3. Re-run command with --verbose flag
4. If persistent, file bug report

---

### Issue: "Validation failed"

**Symptom**: batch-exe-prp stops after phase commit

**Cause**: Code doesn't pass validation (L1-L4)

**Solution**:
1. Review validation error in output
2. Fix code issue
3. Resume execution with --resume flag

---

### Issue: "Drift score >15%"

**Symptom**: batch-update-context reports critical drift

**Cause**: Implementation touched many files not in PRP spec

**Solution**:
1. Review git log for added files
2. If intentional: Update PRP files_modified list
3. If unintentional: Review implementation scope

---

### Issue: "Token usage high"

**Symptom**: batch-peer-review token usage not reduced

**Cause**: Shared context optimization not working

**Solution**:
1. Verify shared_context passed to subagents
2. Check report for token savings section
3. If missing, file bug report

---

### Issue: "Parallel execution slower than sequential"

**Symptom**: Stage with 3 PRPs takes longer than sequential

**Cause**: System resource contention

**Solution**:
1. Reduce parallel limit in orchestrator config
2. Execute stage-by-stage manually
3. Increase system resources (more CPU/RAM)

## Debug Commands

### Check Batch Status
\`\`\`bash
# List all PRPs in batch
ls PRPs/feature-requests/PRP-47.*.md

# Check status of each PRP
grep "^status:" PRPs/feature-requests/PRP-47.*.md
\`\`\`

### Check Git Log
\`\`\`bash
# See all commits for batch
git log --oneline --grep="PRP-47"

# See commits for specific PRP
git log --oneline --grep="PRP-47.1.1"
\`\`\`

### Check Heartbeat Files
\`\`\`bash
# List active heartbeat files
ls /tmp/*-heartbeat.json

# Read heartbeat content
cat /tmp/gen-47-2-1-heartbeat.json
\`\`\`

### Run Dependency Analyzer Manually
\`\`\`bash
cd .ce/orchestration
python dependency_analyzer.py test-input.json
\`\`\`

## Getting Help

1. Check this troubleshooting guide
2. Review relevant PRP (PRP-47.X.Y)
3. Check orchestrator template documentation
4. File issue with:
   - Command used
   - Error message
   - Expected vs actual behavior
   - Steps to reproduce
```

**Lines**: ~110 lines

### Phase 5: Migration Notes & Deployment (15 minutes)

**Create**: `PRPs/feature-requests/PRP-47-MIGRATION-NOTES.md`

**Content Structure**:
```markdown
# Migration Notes - Phase 1 Deployment

## What Changed

### Command Interface (No Changes)
- All batch commands use same CLI interface
- Backward compatible with existing plans and PRPs
- No user-facing changes

### Internal Architecture (Major Changes)
- Unified orchestrator template
- Standardized subagent contracts
- Dependency analyzer for staging
- Parallel execution enabled
- Token optimization (batch-peer-review)

### Performance Improvements
- 60% faster (parallel execution)
- 70% fewer tokens (batch-peer-review)
- 67% less code (all commands)

## Migration Checklist

- [ ] All 4 batch commands refactored (PRP-47.3.1, 47.3.2, 47.5.1, 47.5.2)
- [ ] Integration tests pass (PRP-47.4.1)
- [ ] Documentation complete (PRP-47.6.1)
- [ ] Existing plans tested (no regressions)
- [ ] Performance benchmarks verified
- [ ] Token usage reduced (batch-peer-review)

## Deployment Steps

1. Merge all PRP-47 Phase 1 branches to main
2. Run full test suite: `pytest tests/ -v`
3. Run integration test: `pytest tests/test_batch_integration_gen_exe.py -v`
4. Test with real batch: `/batch-gen-prp PRP-47-BATCH-PLAN.md`
5. Verify token reduction: `/batch-peer-review --batch 47`
6. Update CLAUDE.md with new documentation links
7. Announce Phase 1 completion

## Rollback Plan

If issues found in production:
1. Revert to pre-PRP-47 commit: `git reset --hard <commit>`
2. File bug report with reproduction steps
3. Fix issues in PRP-47 Phase 2
4. Redeploy after fixes

## Phase 2 Preparation

After Phase 1 deployment:
1. Run production batches (collect metrics)
2. Monitor for issues (bottlenecks, errors)
3. Analyze metrics (identify improvements)
4. Prioritize Phase 2 work based on data

Phase 2 timeline: Week 4+
```

**Lines**: ~80 lines

### Phase 6: Deployment Verification (20 minutes)

**Manual checklist**:
```bash
# 1. Verify all documentation files created
ls -la .claude/orchestrators/README.md
ls -la .claude/orchestrators/TROUBLESHOOTING.md
ls -la .claude/subagents/README.md
ls -la PRPs/feature-requests/PRP-47-USAGE-GUIDE.md
ls -la PRPs/feature-requests/PRP-47-MIGRATION-NOTES.md

# 2. Test all batch commands with new docs
/batch-gen-prp PRPs/feature-requests/PRP-47-BATCH-PLAN.md
/batch-exe-prp --batch 47 --stage 1
/batch-peer-review --batch 47
/batch-update-context --batch 47

# 3. Verify documentation accuracy
# - All commands work as documented
# - Examples run successfully
# - Troubleshooting scenarios match real issues

# 4. Deploy
git add .
git commit -m "PRP-47.6.1: Documentation and Phase 1 deployment"
git push origin main

# 5. Announce
# Post to team channel: "Phase 1 complete, documentation available"
```

## Validation

### Pre-Implementation Checks
- [ ] All refactoring PRPs completed (PRP-47.3.1, 47.3.2, 47.5.1, 47.5.2)
- [ ] Integration tests pass (PRP-47.4.1)
- [ ] Verify documentation directory structure exists

### Post-Implementation Checks
- [ ] Usage guide covers all 4 batch commands
- [ ] Architecture diagram clear and accurate
- [ ] Troubleshooting guide has 5+ scenarios
- [ ] Examples include gen→exe→review workflow
- [ ] No broken links or references
- [ ] Documentation reviewed and approved

### Deployment Checks
- [ ] All documentation files committed to main
- [ ] CLAUDE.md updated with documentation links
- [ ] Team notified of Phase 1 completion
- [ ] Metrics collection started (Phase 2 prep)

## Acceptance Criteria

1. **Documentation Completeness**
   - Usage guide covers all commands
   - Architecture overview explains system design
   - Subagent reference documents all 4 types
   - Troubleshooting guide covers common issues
   - Migration notes explain changes

2. **Documentation Quality**
   - Clear and concise (no jargon)
   - Example-driven (real usage scenarios)
   - Actionable (practical next steps)
   - Accurate (matches implementation)

3. **Deployment Success**
   - All documentation files committed
   - No broken links or references
   - Team notified
   - Phase 1 complete

4. **Phase 2 Preparation**
   - Metrics collection infrastructure documented
   - Decision framework explained
   - Timeline communicated

## Testing Strategy

### Documentation Testing
1. Follow each example in usage guide
2. Verify all commands work as documented
3. Test troubleshooting scenarios
4. Check all links and references

### Integration Testing
- Use PRP-47.4.1 integration test to verify end-to-end workflow

### Manual Testing
```bash
# Test usage guide examples
/batch-gen-prp PRPs/feature-requests/TEST-PLAN.md
/batch-exe-prp --batch 999
/batch-peer-review --batch 999
/batch-update-context --batch 999
```

## Risks & Mitigations

### Risk: Documentation outdated after changes
**Impact**: Users confused, documentation not trusted
**Mitigation**: Mark as living documents, update with each change, add "Last Updated" dates

### Risk: Examples don't work
**Impact**: Users can't follow documentation
**Mitigation**: Test all examples before committing, use real scenarios

### Risk: Troubleshooting guide incomplete
**Impact**: Common issues not covered, support burden high
**Mitigation**: Add scenarios based on integration test failures, update during Phase 2

### Risk: Migration breaks existing workflows
**Impact**: Production batches fail
**Mitigation**: Extensive testing with existing plans, rollback plan documented

## Dependencies

- **PRP-47.3.1**: Refactored /batch-gen-prp
- **PRP-47.3.2**: Refactored /batch-exe-prp
- **PRP-47.5.1**: Refactored /batch-peer-review
- **PRP-47.5.2**: Refactored /batch-update-context

## Related PRPs

- **All Phase 1 PRPs**: This PRP depends on all previous Phase 1 work
- **Phase 2 Preparation**: PRP-47.7.1 (metrics and monitoring)

## Files Modified

- `PRPs/feature-requests/PRP-47-USAGE-GUIDE.md` (create)
- `.claude/orchestrators/README.md` (create)
- `.claude/subagents/README.md` (create)
- `.claude/orchestrators/TROUBLESHOOTING.md` (create)
- `PRPs/feature-requests/PRP-47-MIGRATION-NOTES.md` (create)
- `CLAUDE.md` (update with documentation links)

## Notes

- This PRP marks completion of Phase 1 (all refactoring done)
- Documentation is living (update with framework changes)
- Phase 2 begins after production metrics collected
- Time estimate conservative (includes testing and review)
- Deployment should be during low-usage period (weekend)
