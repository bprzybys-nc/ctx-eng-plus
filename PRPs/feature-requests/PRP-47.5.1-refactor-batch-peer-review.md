---
prp_id: PRP-47.5.1
title: Refactor /batch-peer-review Command
status: completed
type: refactor
complexity: medium
estimated_hours: 2
priority: high
dependencies: [PRP-47.1.1, PRP-47.2.1, PRP-47.3.1]
batch_id: 47
stage: 6
---

# PRP-47.5.1: Refactor /batch-peer-review Command

## Problem

The current /batch-peer-review command implements review coordination inline with ~250 lines of custom code. This creates:

- **Code duplication**: Coordination logic repeated from other batch commands
- **Token inefficiency**: Re-reads CLAUDE.md and project context for each PRP review
- **Inconsistent patterns**: Different from gen/exe orchestration approach
- **Maintenance burden**: Changes to review logic require command-level updates

Current issues:
- Each review subagent re-reads shared context (~20k tokens × N PRPs)
- No parallel review (sequential only)
- Structural and semantic reviews not separated
- No inter-PRP consistency checks

With orchestrator and reviewer subagent templates available (PRP-47.1.1), and lessons from gen/exe refactoring (PRP-47.3.1, PRP-47.3.2), we can:
- Reduce command to ~80 lines (68% reduction)
- Implement shared context optimization (70%+ token reduction)
- Enable parallel reviews
- Separate structural and semantic review modes

## Solution

Refactor /batch-peer-review to use:
1. **Base orchestrator template** for 6-phase coordination
2. **Reviewer subagent template** for peer review
3. **Shared context optimization**: Read CLAUDE.md once, pass to all reviewers
4. **Parallel reviews**: All PRPs in batch reviewed simultaneously
5. **Two-mode review**: Structural (fast) and semantic (thorough)

The refactored command will:
- Parse batch ID or PRP list → load PRP files
- Read shared context once (CLAUDE.md, project rules)
- Analyze dependencies (no staging needed - all reviews parallel)
- Spawn reviewer subagents (all in parallel, pass shared context)
- Monitor via heartbeat files
- Aggregate results → generate review report
- Perform inter-PRP consistency checks

## Implementation

### Phase 1: Extract Current Review Patterns (30 minutes)

**Read and analyze**:
- `.claude/commands/batch-peer-review.md`

**Document**:
- PRP loading and parsing
- Review criteria (structural vs semantic)
- Context reading patterns
- Issue categorization (critical, high, medium, low)
- Report generation format
- Inter-PRP consistency checks

**Output**: Notes document with patterns to preserve

### Phase 2: Integrate Base Orchestrator (20 minutes)

**Update**: `.claude/commands/batch-peer-review.md`

**Changes**:
1. Add reference to `.claude/orchestrators/base-orchestrator.md`
2. Restructure command into 6 phases:
   - **Phase 1 (Parsing)**: Load PRP files from batch ID or explicit list
   - **Phase 2 (Validation)**: Verify PRPs exist and readable
   - **Phase 3 (Analysis)**: Extract shared context (CLAUDE.md, rules)
   - **Phase 4 (Spawning)**: Launch reviewer subagents (all parallel)
   - **Phase 5 (Monitoring)**: Poll heartbeat files
   - **Phase 6 (Aggregation)**: Collect reviews, generate report, check inter-PRP consistency

3. Import orchestrator instructions:
```markdown
## Orchestration Pattern

This command follows the base orchestrator template:
{{include .claude/orchestrators/base-orchestrator.md}}

### Command-Specific Adaptations

- **Subagent Type**: Reviewer (peer review)
- **Input**: PRP files + shared context
- **Output**: Review reports with issues and recommendations
- **Monitoring**: Heartbeat files (parallel reviews)
- **Optimization**: Shared context passed to all subagents (70%+ token reduction)
```

**Lines reduced**: ~250 → ~150 (remove inline coordination logic)

### Phase 3: Integrate Reviewer Subagent (30 minutes)

**Update**: `.claude/commands/batch-peer-review.md`

**Changes**:
1. Add reference to `.claude/subagents/reviewer-subagent.md`
2. Define subagent input spec:
```json
{
  "prp_path": "/absolute/path/to/PRP-47.1.1.md",
  "mode": "full",  // structural|semantic|full
  "shared_context": {
    "claude_md": "...",  // Read once, passed to all
    "project_rules": "...",
    "batch_prps": ["PRP-47.1.1", "PRP-47.2.1", ...]  // For inter-PRP checks
  },
  "review_criteria": {
    "check_yaml": true,
    "check_sections": true,
    "check_dependencies": true,
    "check_feasibility": true,
    "check_estimates": true
  }
}
```

3. Define expected output:
```json
{
  "prp_id": "PRP-47.1.1",
  "review_status": "approved|needs_changes|rejected",
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "structure|logic|style|documentation",
      "description": "Missing validation gate for checkpoint logic",
      "location": "Section: Implementation, Phase 5",
      "suggestion": "Add validation gate: [ ] Checkpoint commits created"
    }
  ],
  "recommendations": [
    "Consider adding error handling for git log parsing failure",
    "Estimated hours (2h) may be low for Phase 3 complexity"
  ],
  "token_usage": 3500
}
```

4. Subagent invocation:
```markdown
### Subagent Spawning

1. Read shared context once:
   - CLAUDE.md
   - .ce/RULES.md
   - Project conventions

2. For each PRP (all in parallel):
   - Spawn Haiku subagent
   - Pass reviewer-subagent.md + input spec (including shared context)
   - Create heartbeat file: /tmp/review-{{batch_id}}-{{prp_id}}-heartbeat.json

3. Wait for all subagents to complete
4. Aggregate review results
```

**Lines reduced**: ~60 (remove inline review logic)

### Phase 4: Shared Context Optimization (20 minutes)

**Update**: `.claude/commands/batch-peer-review.md`

**Add new phase**:
```markdown
### Phase 3: Shared Context Extraction

Before spawning subagents, read shared context once:

\`\`\`python
# Read shared context
shared_context = {
    "claude_md": read_file("CLAUDE.md"),
    "rules": read_file(".ce/RULES.md"),
    "conventions": read_file(".serena/memories/code-style-conventions.md"),
    "batch_prps": [prp_id for prp_id in batch_prps]
}

# Size: ~20k tokens
# Reused by all N subagents
# Savings: 20k × (N-1) tokens
\`\`\`

Token Savings Example:
- 3 PRPs: 40k tokens saved (20k × 2)
- 5 PRPs: 80k tokens saved (20k × 4)
- 10 PRPs: 180k tokens saved (20k × 9)

Pass shared_context to each subagent input spec.
Subagents use cached context instead of re-reading files.
```

**Token reduction**: 70%+ for batch reviews

### Phase 5: Inter-PRP Consistency Checks (30 minutes)

**Update**: `.claude/commands/batch-peer-review.md`

**Add to Phase 6 (Aggregation)**:
```markdown
### Inter-PRP Consistency Checks

After collecting individual reviews, perform batch-level checks:

1. **Dependency Consistency**
   - Verify all dependencies reference existing PRPs
   - Check for circular dependencies
   - Validate dependency order matches batch stages

2. **File Modification Consistency**
   - Check for file conflicts (multiple PRPs modifying same file)
   - Verify file paths are absolute
   - Check for missing files in critical PRPs

3. **Estimation Consistency**
   - Sum estimated hours across batch
   - Flag if total >40 hours (week of work)
   - Check for underestimated complex tasks (<2h for high complexity)

4. **Validation Gate Consistency**
   - Verify all PRPs have validation gates
   - Check for missing integration tests
   - Ensure checkpoint logic for multi-phase PRPs

Output inter-PRP issues in separate section of review report.
```

**Lines**: ~40 lines

### Phase 6: Report Generation & Testing (20 minutes)

**Update**: `.claude/commands/batch-peer-review.md`

**Update report format**:
```markdown
### Review Report Format

\`\`\`
Batch {{batch_id}} Peer Review Report
Generated: {{timestamp}}

Summary:
  Total PRPs: {{total}}
  Approved: {{approved}}
  Needs Changes: {{needs_changes}}
  Rejected: {{rejected}}
  Total Issues: {{total_issues}}

Token Savings:
  Shared context size: {{context_tokens}}k tokens
  Reviews: {{num_reviews}}
  Savings: {{savings}}k tokens ({{percent}}%)

Issues by PRP:

## PRP-{{prp_id_1}}: {{title}}
Status: {{status}}
Issues: {{issue_count}}

### Critical Issues
- {{issue_description}} ({{location}})

### High Priority Issues
- {{issue_description}} ({{location}})

### Medium Priority Issues
- {{issue_description}} ({{location}})

### Recommendations
- {{recommendation}}

---

## Inter-PRP Issues

### Dependency Issues
- {{issue_description}}

### File Conflict Issues
- {{issue_description}}

### Estimation Issues
- Total hours: {{total_hours}} ({{warning_if_high}})

---

Next Steps:
1. Address critical issues in: {{prp_list}}
2. Review high priority issues
3. Update PRPs and regenerate
\`\`\`
```

**Add integration test**:
```bash
# Test with 3-4 generated PRPs
/batch-peer-review --batch 47 --prps PRP-47.1.1,PRP-47.2.1,PRP-47.2.2

# Verify:
# - All PRPs reviewed in parallel
# - Shared context optimization (check token usage in report)
# - Review report generated
# - Inter-PRP checks performed
```

## Validation

### Pre-Implementation Checks
- [ ] PRP-47.1.1 completed (orchestrator + reviewer subagent templates exist)
- [ ] PRP-47.2.1 completed (dependency_analyzer.py for consistency checks)
- [ ] PRP-47.3.1 completed (refactored gen, lessons learned)
- [ ] Read current /batch-peer-review.md to understand review criteria
- [ ] Create 3-4 test PRPs for integration testing

### Post-Implementation Checks
- [ ] Reviews 3-4 PRPs in parallel
- [ ] Detects issues in test PRPs (missing validation gates, etc.)
- [ ] Shared context optimization works (tokens reduced by 70%+)
- [ ] Review time <5 minutes for 3-4 PRPs
- [ ] Report includes inter-PRP consistency checks

### Integration Checks
- [ ] Orchestrator template patterns followed
- [ ] Reviewer subagent input/output spec matches
- [ ] Shared context passed to all subagents
- [ ] Heartbeat monitoring protocol works

### Optimization Checks
- [ ] Shared context read once (not per PRP)
- [ ] Token savings calculated correctly
- [ ] Report shows token savings

## Acceptance Criteria

1. **Functionality Preserved**
   - All existing review criteria work (structural + semantic)
   - Issue categorization preserved (critical/high/medium/low)
   - Report format clear and actionable

2. **Code Reduction**
   - Command reduced to ~80 lines (from ~250)
   - Coordination logic delegated to orchestrator template
   - Review logic delegated to reviewer subagent

3. **Performance Improvement**
   - Token usage reduced by 70%+ (shared context optimization)
   - Review time <5 minutes for 3-4 PRPs (parallel execution)
   - Cost reduction proportional to token savings

4. **Enhanced Checks**
   - Inter-PRP consistency checks added
   - Dependency validation
   - File conflict detection
   - Estimation validation

## Testing Strategy

### Unit Tests
- Defer to existing batch-peer-review tests (if any)
- Focus on integration testing

### Integration Tests
1. **Test Case 1: Structural Review**
   - Review 3 PRPs (structural mode only)
   - Verify: YAML validation, section checks, fast execution (<2 min)

2. **Test Case 2: Full Review**
   - Review 3 PRPs (full mode)
   - Verify: All checks performed, issues detected, <5 min

3. **Test Case 3: Shared Context Optimization**
   - Review 5 PRPs
   - Verify: Token savings in report, 70%+ reduction

4. **Test Case 4: Inter-PRP Checks**
   - Review batch with circular dependency
   - Verify: Consistency issues detected in report

### Manual Testing
```bash
# Test 1: Review generated PRPs
/batch-peer-review --batch 47

# Test 2: Review specific PRPs
/batch-peer-review --prps PRP-47.1.1,PRP-47.2.1,PRP-47.2.2

# Test 3: Structural only (fast)
/batch-peer-review --batch 47 --mode structural

# Test 4: Full review
/batch-peer-review --batch 47 --mode full
```

## Risks & Mitigations

### Risk: Shared context stale or incorrect
**Impact**: Reviews based on wrong information
**Mitigation**: Verify context read timestamp in report, refresh if >1 hour old

### Risk: Parallel reviews miss inter-PRP issues
**Impact**: Inconsistencies not caught
**Mitigation**: Add explicit inter-PRP consistency check phase (Phase 6)

### Risk: Token savings don't materialize
**Impact**: No performance improvement
**Mitigation**: Measure token usage in report, verify context passed not re-read

### Risk: Review quality decreases
**Impact**: Issues not caught, PRPs have bugs
**Mitigation**: Keep all existing review criteria, add tests with known issues

### Risk: Heartbeat monitoring unreliable for parallel reviews
**Impact**: Reviews appear to fail when running
**Mitigation**: Test with 5+ parallel reviews, verify polling logic

## Dependencies

- **PRP-47.1.1**: Base orchestrator + reviewer subagent templates
- **PRP-47.2.1**: Dependency analyzer (for inter-PRP checks)
- **PRP-47.3.1**: Refactored gen command (lessons learned)

## Related PRPs

- **Similar Refactoring**: PRP-47.3.1 (gen), PRP-47.3.2 (exe), PRP-47.5.2 (context-update)
- **Infrastructure**: PRP-47.1.1 (orchestrator), PRP-47.2.1 (analyzer)

## Files Modified

- `.claude/commands/batch-peer-review.md` (refactor)

## Notes

- Shared context optimization is key innovation (70%+ token reduction)
- Parallel reviews enabled (all PRPs reviewed simultaneously)
- Inter-PRP checks critical for batch quality
- Review modes: structural (fast, 2 min), semantic (thorough, 5 min), full (both)
- Token savings scale with batch size (more PRPs = more savings)
- Cost reduction: 3 PRPs = $0.20 saved, 10 PRPs = $0.90 saved (at Haiku rates)
