---
prp_id: PRP-47.3.1
title: Refactor /batch-gen-prp Command
status: planning
type: refactor
complexity: medium
estimated_hours: 4
priority: high
dependencies: [PRP-47.1.1, PRP-47.2.1]
batch_id: 47
stage: 4
---

# PRP-47.3.1: Refactor /batch-gen-prp Command

## Problem

The current /batch-gen-prp command implements coordination logic inline (parsing, validation, dependency analysis, spawning, monitoring) with ~300 lines of custom code. This creates:

- **Code duplication**: Logic repeated in /batch-exe-prp, /batch-peer-review
- **Maintenance burden**: Changes require updates to multiple commands
- **Inconsistent patterns**: Each command uses slightly different approaches
- **Testing difficulty**: Integration logic tightly coupled

With orchestrator and dependency analyzer templates available (PRP-47.1.1, PRP-47.2.1), we can:
- Reduce command to ~100 lines (66% reduction)
- Standardize on base-orchestrator.md pattern
- Use generator-subagent.md for PRP creation
- Share dependency_analyzer.py for stage assignment

## Solution

Refactor /batch-gen-prp to use:
1. **Base orchestrator template** for 6-phase coordination
2. **Generator subagent template** for PRP creation
3. **Dependency analyzer** for stage assignment and cycle detection
4. **Standardized monitoring** via heartbeat file protocol

The refactored command will:
- Parse plan file → extract phases
- Validate phase format
- Analyze dependencies (topological sort, cycle detection, staging)
- Spawn generator subagents (one per stage, parallel within stage)
- Monitor via heartbeat files (30s polling)
- Aggregate results → create Linear issues
- Output summary

## Implementation

### Phase 1: Extract Current Logic Patterns (1 hour)

**Read and analyze**:
- `.claude/commands/batch-gen-prp.md`

**Document**:
- Plan parsing logic
- Phase extraction patterns
- Dependency analysis (current approach)
- Subagent spawning mechanism
- Monitoring protocol (current heartbeat)
- Linear issue creation

**Output**: Notes document with key patterns to preserve

### Phase 2: Integrate Base Orchestrator (1 hour)

**Update**: `.claude/commands/batch-gen-prp.md`

**Changes**:
1. Add reference to `.claude/orchestrators/base-orchestrator.md`
2. Restructure command into 6 phases:
   - **Phase 1 (Parsing)**: Extract phases from plan file
   - **Phase 2 (Validation)**: Verify phase format (required fields)
   - **Phase 3 (Analysis)**: Call dependency_analyzer.py
   - **Phase 4 (Spawning)**: Launch generator subagents per stage
   - **Phase 5 (Monitoring)**: Poll heartbeat files (30s interval)
   - **Phase 6 (Aggregation)**: Collect PRPs, create Linear issues

3. Import orchestrator instructions:
```markdown
## Orchestration Pattern

This command follows the base orchestrator template:
{{include .claude/orchestrators/base-orchestrator.md}}

### Command-Specific Adaptations

- **Subagent Type**: Generator (PRP creation)
- **Input**: Plan phases from markdown file
- **Output**: Structured PRP files with Linear issue IDs
- **Monitoring**: Heartbeat files (file-based, not git log)
```

**Lines reduced**: ~300 → ~150 (remove inline coordination logic)

### Phase 3: Integrate Generator Subagent (1 hour)

**Update**: `.claude/commands/batch-gen-prp.md`

**Changes**:
1. Add reference to `.claude/subagents/generator-subagent.md`
2. Define subagent input spec:
```json
{
  "phase": {
    "title": "{{phase.title}}",
    "goal": "{{phase.goal}}",
    "estimated_hours": {{phase.estimated_hours}},
    "complexity": "{{phase.complexity}}",
    "files_modified": {{phase.files_modified}},
    "dependencies": {{phase.dependencies}},
    "implementation_steps": {{phase.implementation_steps}},
    "validation_gates": {{phase.validation_gates}}
  },
  "batch_id": "{{batch_id}}",
  "stage": {{stage}},
  "order": {{order}},
  "context": {
    "project_root": "{{project_root}}",
    "existing_prps": {{existing_prps}}
  }
}
```

3. Define expected output:
```json
{
  "prp_id": "PRP-{{batch_id}}.{{stage}}.{{order}}",
  "file_path": "/absolute/path/to/PRP-{{batch_id}}.{{stage}}.{{order}}-slug.md",
  "status": "created",
  "validation": {
    "yaml_valid": true,
    "required_sections": true,
    "dependency_links": true
  }
}
```

4. Subagent invocation:
```markdown
### Subagent Spawning

For each stage from dependency analyzer:
1. Group phases in stage
2. Spawn Haiku subagent per phase (parallel)
3. Pass generator-subagent.md + input spec
4. Create heartbeat file: /tmp/gen-{{batch_id}}-{{stage}}-{{order}}-heartbeat.json
5. Continue to next stage after all current stage subagents complete
```

**Lines reduced**: ~50 (remove inline PRP generation logic)

### Phase 4: Integrate Dependency Analyzer (30 minutes)

**Update**: `.claude/commands/batch-gen-prp.md`

**Changes**:
1. Add dependency analyzer integration:
```markdown
### Phase 3: Dependency Analysis

Call dependency_analyzer.py with phase data:

\`\`\`bash
cd .ce/orchestration
python dependency_analyzer.py /tmp/batch-{{batch_id}}-phases.json
\`\`\`

Input format:
{
  "items": [
    {
      "id": "phase-1",
      "dependencies": [],
      "files": ["path/to/file"]
    },
    ...
  ]
}

Output:
{
  "sorted_order": ["phase-1", "phase-2", ...],
  "stages": {
    "1": ["phase-1"],
    "2": ["phase-2", "phase-3"],
    "3": ["phase-4"]
  },
  "file_conflicts": {},
  "has_cycles": false
}

If has_cycles=true: Stop and report circular dependency error with cycle path.
```

2. Replace inline stage assignment with analyzer output
3. Add cycle detection error handling

**Lines reduced**: ~40 (remove manual dependency logic)

### Phase 5: Update Monitoring Protocol (30 minutes)

**Update**: `.claude/commands/batch-gen-prp.md`

**Changes**:
1. Standardize heartbeat file format:
```json
{
  "subagent_id": "gen-47-2-1",
  "status": "running|completed|failed",
  "last_update": "2025-11-10T14:30:00Z",
  "progress": {
    "phase": "writing_prp",
    "percent_complete": 75
  },
  "output": {
    "prp_id": "PRP-47.2.1",
    "file_path": "/path/to/PRP-47.2.1.md"
  }
}
```

2. Update polling logic:
```markdown
### Phase 5: Monitoring

For each stage:
1. Poll heartbeat files every 30 seconds
2. For each subagent:
   - Read /tmp/gen-{{batch_id}}-{{stage}}-{{order}}-heartbeat.json
   - Check last_update timestamp
   - If timestamp >60s old: Mark failed (2 missed polls)
   - If status=completed: Collect output
   - If status=failed: Record error
3. Once all subagents in stage complete: Proceed to next stage
4. Cleanup heartbeat files after completion
```

**Lines reduced**: ~30 (use standardized protocol)

### Phase 6: Linear Integration & Testing (1 hour)

**Update**: `.claude/commands/batch-gen-prp.md`

**Changes**:
1. Keep Linear issue creation (no change):
```markdown
### Phase 6: Aggregation

For each generated PRP:
1. Read PRP file
2. Extract title, prp_id, estimated_hours
3. Create Linear issue:
   - Title: "{{prp_id}}: {{title}}"
   - Description: Link to PRP file
   - Team: Context Engineering
   - Priority: High
4. Update PRP file with Linear issue ID
5. Commit PRP file: "PRP-{{batch_id}}: Generated {{prp_id}}"
```

2. Update summary output format:
```markdown
### Summary Output

\`\`\`
Batch {{batch_id}} Generation Complete

Total Phases: {{total}}
Total Stages: {{stages}}
PRPs Generated: {{count}}
Time Elapsed: {{duration}}

Stage Breakdown:
  Stage 1: {{stage_1_prps}}
  Stage 2: {{stage_2_prps}} (parallel)
  Stage 3: {{stage_3_prps}}

Linear Issues Created:
  {{prp_id_1}}: {{linear_url_1}}
  {{prp_id_2}}: {{linear_url_2}}
  ...

Files Created:
  {{file_path_1}}
  {{file_path_2}}
  ...
\`\`\`
```

3. Add integration test:
```bash
# Test with sample plan
cat > /tmp/test-plan.md <<EOF
# Test Batch Plan

## Phases

### Phase 1: Foundation
**Goal**: Create base files
**Estimated Hours**: 2
**Complexity**: low
**Files Modified**: base.py
**Dependencies**: None
**Implementation Steps**: [steps]
**Validation Gates**: [gates]

### Phase 2: Integration
**Goal**: Integrate components
**Estimated Hours**: 3
**Complexity**: medium
**Files Modified**: integration.py
**Dependencies**: Phase 1
**Implementation Steps**: [steps]
**Validation Gates**: [gates]
EOF

# Run command
/batch-gen-prp /tmp/test-plan.md

# Verify outputs
ls -la PRPs/feature-requests/PRP-*.md
```

## Validation

### Pre-Implementation Checks
- [ ] PRP-47.1.1 completed (orchestrator + subagent templates exist)
- [ ] PRP-47.2.1 completed (dependency_analyzer.py exists)
- [ ] Read current /batch-gen-prp.md to understand existing patterns
- [ ] Create test plan file for integration testing

### Post-Implementation Checks
- [ ] Command still works with existing test plan files
- [ ] Generates 3-4 PRPs in correct stages
- [ ] Heartbeat files created and monitored correctly
- [ ] Linear issues created for generated PRPs
- [ ] Error handling for circular dependencies works
- [ ] Time to generate 4 PRPs <10 minutes

### Integration Checks
- [ ] Orchestrator template patterns followed
- [ ] Generator subagent input/output spec matches
- [ ] Dependency analyzer output used correctly
- [ ] Monitoring protocol consistent with base template

### Code Quality Checks
- [ ] Command length reduced from ~300 to ~100 lines (66% reduction)
- [ ] No inline coordination logic (delegated to templates)
- [ ] Clear phase separation (6 phases visible)
- [ ] Error messages reference cycle path from analyzer

## Acceptance Criteria

1. **Functionality Preserved**
   - All existing test plans work without modification
   - PRPs generated with correct structure (YAML, sections, validation gates)
   - Linear issues created with correct metadata
   - Dependency order respected

2. **Code Reduction**
   - Command reduced to ~100 lines (from ~300)
   - Coordination logic delegated to orchestrator template
   - PRP generation logic delegated to generator subagent
   - Dependency analysis delegated to analyzer

3. **Standardization**
   - Uses base-orchestrator.md 6-phase pattern
   - Uses generator-subagent.md input/output spec
   - Uses dependency_analyzer.py for staging
   - Uses standardized heartbeat protocol

4. **Error Handling**
   - Circular dependencies detected and reported with cycle path
   - File conflicts detected (if any in same stage)
   - Subagent failures handled gracefully (report partial success)
   - Missing plan fields reported clearly

## Testing Strategy

### Unit Tests
- Defer to existing batch-gen-prp tests (if any)
- Focus on integration testing

### Integration Tests
1. **Test Case 1: Linear Plan**
   - 3 phases, sequential dependencies
   - Verify: 3 stages, 3 PRPs, correct order

2. **Test Case 2: Branching Plan**
   - 4 phases: A → B, A → C, B+C → D
   - Verify: 3 stages (A, B+C parallel, D), 4 PRPs

3. **Test Case 3: Circular Dependency**
   - 3 phases: A → B, B → C, C → A
   - Verify: Error reported with cycle path

4. **Test Case 4: Real Plan**
   - Use PRP-47 batch plan (this batch)
   - Verify: 10 PRPs generated in 7 stages

### Manual Testing
```bash
# Test 1: Simple plan
/batch-gen-prp PRPs/feature-requests/TEST-PLAN-SIMPLE.md

# Test 2: Complex plan
/batch-gen-prp PRPs/feature-requests/TEST-PLAN-COMPLEX.md

# Test 3: Self-referential plan
/batch-gen-prp PRPs/feature-requests/PRP-47-BATCH-PLAN.md
```

## Risks & Mitigations

### Risk: Existing plans incompatible with new parser
**Impact**: Commands fail on legacy plans
**Mitigation**: Test with 3-5 existing plan files before finalizing

### Risk: Heartbeat protocol breaks monitoring
**Impact**: Subagents appear to fail when actually running
**Mitigation**: Test monitoring with 60s delay simulation, verify failure detection

### Risk: Linear integration breaks
**Impact**: No issues created, workflow blocked
**Mitigation**: Keep Linear logic unchanged, test with real API

### Risk: Performance regression
**Impact**: Generation slower than before
**Mitigation**: Benchmark existing command, target <10min for 4 PRPs

### Risk: Refactoring introduces bugs
**Impact**: PRPs generated incorrectly
**Mitigation**: Compare outputs with existing command on same plan, diff PRP files

## Dependencies

- **PRP-47.1.1**: Base orchestrator + generator subagent templates
- **PRP-47.2.1**: Dependency analyzer

## Related PRPs

- **Similar Refactoring**: PRP-47.3.2 (exe), PRP-47.5.1 (review), PRP-47.5.2 (context-update)
- **Integration Test**: PRP-47.4.1 (test gen + exe together)

## Files Modified

- `.claude/commands/batch-gen-prp.md` (refactor)

## Notes

- This is the first command to use the new orchestrator framework
- Lessons learned here will inform other refactoring PRPs
- Keep backward compatibility (existing plans should work)
- Performance target: <10 minutes for 4 PRPs (existing baseline)
- Monitor token usage: Should decrease due to shared templates
