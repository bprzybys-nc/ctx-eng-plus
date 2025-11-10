---
prp_id: PRP-47.1.1
title: Foundation - Orchestrator & Subagent Templates
status: planning
type: feature
complexity: medium
estimated_hours: 8
priority: high
dependencies: []
batch_id: 47
stage: 1
---

# PRP-47.1.1: Foundation - Orchestrator & Subagent Templates

## Problem

The batch command system currently has 30% code duplication across 4 commands (/batch-gen-prp, /batch-exe-prp, /batch-peer-review, /batch-update-context). Each command reimplements coordination logic, monitoring, error handling, and subagent spawning independently.

Without reusable templates, we cannot:
- Share orchestration patterns across commands
- Standardize subagent interfaces and contracts
- Reduce maintenance burden
- Scale to new batch operations

This PRP establishes the foundation for unification by creating:
1. Base orchestrator template (coordination logic)
2. Four subagent templates (generator, executor, reviewer, context-updater)

## Solution

Create 5 template files in `.claude/` directory structure:

**Base Orchestrator Template** (.claude/orchestrators/base-orchestrator.md):
- 6-phase coordination pattern (parsing, validation, analysis, spawning, monitoring, aggregation)
- Standardized input/output contracts
- Error handling framework
- Monitoring protocol (heartbeat files)

**Subagent Templates** (.claude/subagents/):
- generator-subagent.md: PRP creation from plan phases
- executor-subagent.md: PRP implementation with checkpoints
- reviewer-subagent.md: Peer review (structural + semantic)
- context-updater-subagent.md: Context synchronization

Each template includes:
- Clear input/output specifications
- Tool allowlist (relevant tools only)
- Example usage scenarios
- Error handling patterns

## Implementation

### Phase 1: Base Orchestrator Template (2 hours)

**Create**: `.claude/orchestrators/base-orchestrator.md`

**Content Structure**:
```markdown
# Base Orchestrator Template

## Overview
Coordination pattern for batch operations using Sonnet orchestrator + Haiku subagents.

## 6-Phase Pattern
1. Parsing: Extract items from input
2. Validation: Verify item format and requirements
3. Analysis: Dependency analysis, stage assignment
4. Spawning: Launch subagents with input specs
5. Monitoring: Track progress via heartbeat/git log
6. Aggregation: Collect results, generate summary

## Orchestrator Contract

### Input
{
  "batch_id": "47",
  "operation": "generate|execute|review|update-context",
  "items": [...],
  "options": {...}
}

### Output
{
  "status": "success|partial|failure",
  "results": [...],
  "summary": {...},
  "errors": [...]
}

## Monitoring Protocol
- Heartbeat files: /tmp/subagent-{id}-heartbeat.json
- Poll interval: 30 seconds
- Failure threshold: 2 missed polls
- Cleanup: Delete heartbeat files after completion

## Error Handling
- Validation failures: Stop before spawning
- Subagent failures: Continue with other stages, report partial success
- Circular dependencies: Detect and report with cycle path
```

**Lines**: ~200 lines

### Phase 2: Generator Subagent Template (1.5 hours)

**Create**: `.claude/subagents/generator-subagent.md`

**Content Structure**:
```markdown
# Generator Subagent Template

## Purpose
Create structured PRP files from plan phases.

## Input Specification
{
  "phase": {
    "title": "Phase Title",
    "goal": "One-sentence objective",
    "estimated_hours": 2,
    "complexity": "low|medium|high",
    "files_modified": ["path/to/file"],
    "dependencies": ["PRP-47.1.1"],
    "implementation_steps": [...],
    "validation_gates": [...]
  },
  "batch_id": "47",
  "stage": 1,
  "order": 1
}

## Output Specification
{
  "prp_id": "PRP-47.1.1",
  "file_path": "/absolute/path/to/PRP-47.1.1-slug.md",
  "status": "created",
  "validation": {
    "yaml_valid": true,
    "required_sections": true,
    "dependency_links": true
  }
}

## Tool Allowlist
- Write (create PRP file)
- Read (validate existing PRPs for dependency links)
- Glob (find existing PRPs)

## Process
1. Extract phase data from input
2. Generate YAML frontmatter
3. Create Problem/Solution/Implementation sections
4. Add validation gates as checkboxes
5. Link dependencies
6. Write file
7. Validate structure
8. Return output JSON
```

**Lines**: ~150 lines

### Phase 3: Executor Subagent Template (1.5 hours)

**Create**: `.claude/subagents/executor-subagent.md`

**Content Structure**:
```markdown
# Executor Subagent Template

## Purpose
Implement PRP with checkpoint/resume logic and validation integration.

## Input Specification
{
  "prp_path": "/absolute/path/to/PRP-47.1.1.md",
  "resume_from": "phase_2",  // Optional
  "validation_level": 4
}

## Output Specification
{
  "prp_id": "PRP-47.1.1",
  "status": "completed|partial|failed",
  "phases_completed": ["phase_1", "phase_2"],
  "validation_results": {
    "level_1": true,
    "level_2": true,
    "level_3": true,
    "level_4": true
  },
  "git_commits": ["abc123", "def456"]
}

## Tool Allowlist
- Read (read PRP file)
- Edit/Write (implement changes)
- Bash (git operations, validation)
- TodoWrite (track progress)

## Process
1. Read PRP file
2. Parse implementation phases
3. If resume_from: skip completed phases
4. For each phase:
   a. Implement changes
   b. Create git checkpoint
   c. Run validation (L1-L4)
   d. If validation fails: stop and report
5. Aggregate results
6. Return output JSON

## Checkpoint Format
Git commit message: "PRP-47.1.1: Phase {N} - {title}"
```

**Lines**: ~150 lines

### Phase 4: Reviewer Subagent Template (1.5 hours)

**Create**: `.claude/subagents/reviewer-subagent.md`

**Content Structure**:
```markdown
# Reviewer Subagent Template

## Purpose
Perform peer review with structural and semantic analysis.

## Input Specification
{
  "prp_path": "/absolute/path/to/PRP-47.1.1.md",
  "mode": "structural|semantic|full",
  "shared_context": {
    "claude_md": "...",
    "project_rules": "..."
  }
}

## Output Specification
{
  "prp_id": "PRP-47.1.1",
  "review_status": "approved|needs_changes|rejected",
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "structure|logic|style|documentation",
      "description": "...",
      "location": "Section: Implementation"
    }
  ],
  "recommendations": [...]
}

## Tool Allowlist
- Read (read PRP, read shared context)
- Grep (search for patterns)
- mcp__syntropy__serena_find_symbol (code analysis)

## Process
1. Read PRP file
2. If mode=structural: Check YAML, sections, validation gates
3. If mode=semantic: Analyze logic, dependencies, feasibility
4. If mode=full: Both structural + semantic
5. Use shared_context to avoid re-reading CLAUDE.md
6. Generate issues list
7. Return output JSON

## Structural Checks
- YAML frontmatter valid
- Required sections present
- Validation gates are checkboxes
- Dependencies linked correctly

## Semantic Checks
- Implementation steps logical
- Files modified are relevant
- Complexity estimate reasonable
- Dependencies make sense
```

**Lines**: ~150 lines

### Phase 5: Context Updater Subagent Template (1 hour)

**Create**: `.claude/subagents/context-updater-subagent.md`

**Content Structure**:
```markdown
# Context Updater Subagent Template

## Purpose
Synchronize PRP status with codebase implementation state.

## Input Specification
{
  "prp_path": "/absolute/path/to/PRP-47.1.1.md",
  "execution_result": {
    "status": "completed",
    "phases_completed": ["phase_1", "phase_2"],
    "git_commits": ["abc123"]
  }
}

## Output Specification
{
  "prp_id": "PRP-47.1.1",
  "update_status": "updated|no_changes|failed",
  "drift_score": 0.05,
  "sections_updated": ["status", "implementation_notes"]
}

## Tool Allowlist
- Read (read PRP, read code)
- Edit (update PRP file)
- Grep (verify implementation)

## Process
1. Read PRP file
2. Read execution result
3. Update status field (planning → in_progress → completed)
4. Add implementation notes (git commits, completion date)
5. Calculate drift score (compare files_modified with git log)
6. Write updated PRP
7. Return output JSON

## Drift Score Calculation
drift = |git_files - prp_files| / prp_files
- <5%: Healthy
- 5-15%: Warning
- >15%: Critical
```

**Lines**: ~80 lines

### Phase 6: Documentation (1.5 hours)

**Create**: `.claude/orchestrators/README.md`

**Content**:
- Overview of orchestrator pattern
- When to use base-orchestrator.md
- How to extend for new batch operations
- Example usage

**Create**: `.claude/subagents/README.md`

**Content**:
- Overview of 4 subagent types
- Input/output contract specifications
- Tool allowlist rationale
- Example invocations

**Lines**: ~100 lines total

## Validation

### Pre-Implementation Checks
- [ ] Verify `.claude/orchestrators/` directory doesn't exist (create it)
- [ ] Verify `.claude/subagents/` directory doesn't exist (create it)
- [ ] Review existing batch command structure for patterns to extract

### Post-Implementation Checks
- [ ] All 5 template files created and readable
- [ ] Each template has clear input/output spec examples
- [ ] Orchestrator logic covers all 6 phases (parsing, validation, analysis, spawning, monitoring, aggregation)
- [ ] Subagents reference orchestrator correctly
- [ ] No syntax errors in templates (markdown validation)
- [ ] Total lines: ~730 lines (target ±50 lines)
- [ ] README files provide clear guidance

### Structure Validation
- [ ] Base orchestrator has monitoring protocol documented
- [ ] Base orchestrator has error handling framework
- [ ] Each subagent has tool allowlist
- [ ] Each subagent has process steps numbered
- [ ] Input/output specs are JSON formatted with examples

## Acceptance Criteria

1. **Template Completeness**
   - Base orchestrator covers all 6 coordination phases
   - All 4 subagent templates created with full specifications
   - Input/output contracts clearly defined with JSON examples

2. **Documentation Quality**
   - README files explain orchestrator and subagent patterns
   - Examples provided for each template
   - Tool allowlists justified

3. **Code Quality**
   - Markdown syntax valid (no broken formatting)
   - JSON examples parseable
   - Cross-references between templates accurate

4. **Usability**
   - Templates can be copy-pasted and adapted by future commands
   - Clear extension points for customization
   - Error handling patterns documented

## Testing Strategy

### Manual Testing
1. Read each template file to verify structure
2. Validate JSON examples with jq or Python json.loads()
3. Check markdown rendering in VS Code preview
4. Verify cross-references between templates

### Integration Testing
- Defer to PRP-47.3.1 (refactor /batch-gen-prp) which will be first consumer
- Defer to PRP-47.3.2 (refactor /batch-exe-prp) for executor template validation

## Risks & Mitigations

### Risk: Template abstraction too generic
**Impact**: Commands struggle to adapt templates
**Mitigation**: Include 2-3 concrete examples per template, show customization points

### Risk: Subagent contracts incompatible with existing logic
**Impact**: Refactoring PRPs (47.3.1, 47.3.2) blocked
**Mitigation**: Review existing batch command code before finalizing contracts

### Risk: Tool allowlists too restrictive
**Impact**: Subagents cannot complete tasks
**Mitigation**: Start permissive, refine after Phase 1 deployment

## Dependencies

None (foundation phase)

## Related PRPs

- **Consumers**: PRP-47.2.1 (dependency analyzer), PRP-47.3.1 (refactor gen), PRP-47.3.2 (refactor exe)
- **Related**: PRP-47.5.1 (refactor review), PRP-47.5.2 (refactor context-update)

## Files Modified

- `.claude/orchestrators/base-orchestrator.md` (create)
- `.claude/subagents/generator-subagent.md` (create)
- `.claude/subagents/executor-subagent.md` (create)
- `.claude/subagents/reviewer-subagent.md` (create)
- `.claude/subagents/context-updater-subagent.md` (create)
- `.claude/orchestrators/README.md` (create)
- `.claude/subagents/README.md` (create)

## Notes

- This is the foundation for entire PRP-47 batch (all other PRPs depend on this)
- Templates should be living documents (evolve based on Phase 2 learnings)
- Focus on clarity over brevity (templates are reference documentation)
- Use consistent terminology (orchestrator, subagent, heartbeat, checkpoint)
