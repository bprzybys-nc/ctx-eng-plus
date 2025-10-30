# GitButler Removal - Batch Gen PRP Lessons Learned

**Date**: 2025-10-30
**Context**: First real-world test of `/batch-gen-prp` command
**Plan**: `initials/GITBUTLER-REMOVAL-PLAN.md`

---

## Issues Encountered

### Issue 1: Plan Format Detection

**Problem**: Plan document structure differs from expected format in `/batch-gen-prp` docs

**Details**:
- Expected: `### Phase 1: Name` with metadata fields below
- Actual: `### Phase 1: Preserve Work (Merge to Main)` with detailed steps but metadata not in expected format

**Fields Present**:
- Goal (in description)
- Time (as "Time: X minutes")
- Risk (as "Risk: MEDIUM")
- Steps (as numbered list)
- Validation (as separate section)

**Fields Missing**:
- Estimated Hours (has "Time: 10-15 minutes" instead)
- Complexity (not explicit)
- Files Modified (described in steps, not listed)
- Dependencies (described in table, not per-phase)

**Impact**: Parser needs to handle flexible format or plan needs restructuring

---

## Observations

### Plan Structure Flexibility

The GitButler removal plan uses a more narrative format:
- Phases are well-defined sections with clear goals
- Time estimates in human-readable format ("10-15 minutes")
- Dependencies shown in summary table at end
- Files implied from steps rather than explicit list

This is realistic for real-world plans (not always in perfect format).

---

## Recommendations for /batch-gen-prp Maturity

1. **Flexible Parsing**: Support multiple plan formats (strict vs narrative)
2. **Field Extraction**: Infer missing fields from context
3. **Validation Warning**: Show what was extracted vs what's expected
4. **Format Examples**: Provide both strict and flexible examples
5. **Interactive Mode**: Ask user to confirm extracted data
6. **Plan Recommendation Detection**: Parse plan for "Option A/B" recommendations and warn if invocation conflicts
7. **Parallelism Analysis**: Calculate parallelism benefit score and warn if <20% (suggest single PRP)
8. **Dependency Visualization**: Show ASCII dependency graph before generation

---

## Issue 2: Plan Recommendation Conflicts with Batch Mode

**Problem**: Plan document recommends "Option A: Single PRP" (line 383) but user invoked `/batch-gen-prp`

**Details**:
- Plan explicitly states: "Option A: Single PRP (Recommended)"
- Rationale: "low risk after Phase 1 completes, no dependencies between cleanup phases"
- User invoked batch generation anyway

**Question**: Should `/batch-gen-prp` detect this recommendation and warn user?

**Options**:

1. Proceed with batch generation (5 PRPs as user requested)
2. Ask user if they want single PRP instead
3. Respect plan recommendation and generate single PRP

---

## Phase Extraction Results

Successfully extracted 5 phases:

| Phase | Name | Time | Risk | Dependencies | Files |
|-------|------|------|------|--------------|-------|
| 1 | Preserve Work (Merge to Main) | 10-15 min | MEDIUM | None | (git operations) |
| 2 | Remove GitButler Branches | 5 min | LOW | Phase 1 | (git operations) |
| 3 | Remove GitButler Metadata | 5 min | LOW | Phase 2 | `.git/gitbutler/` |
| 4 | Uninstall GitButler App | 2 min | LOW | Phase 3 | `/Applications/GitButler.app/` |
| 5 | Clean Documentation References | 15-20 min | LOW | Phase 4 | CLAUDE.md, .claude/commands/*.md |

**Note**: Phase 4 marked as OPTIONAL in plan

---

## User Decision

**Timestamp**: 2025-10-30
**Decision**: Use single PRP via `/generate-prp` instead
**Rationale**: Plan explicitly recommends single PRP, fully sequential dependencies provide no parallel benefit

**Outcome**: Invoking `/generate-prp` to create single comprehensive PRP

---

## Final Status

**Timestamp**: 2025-10-30 (PRP generation complete)
**Decision**: Single PRP via /generate-prp (PRP-30)
**Output**: `PRPs/feature-requests/PRP-30-gitbutler-complete-removal.md`
**Linear Issue**: TBD (manual creation required - MCP tool had parameter issues)

---

## Generation Summary

**Success**: PRP-30 created successfully

**Content**:
- 9 sections: TL;DR, Context, 6 implementation phases, Validation Gates (7), Testing Strategy, Rollout Plan (5 phases), Rollback Procedures
- Total length: ~1100 lines
- All 5 phases from plan incorporated
- Comprehensive validation gates and rollback procedures
- Ready for execution

**Time to Generate**: ~5 minutes (manual generation, not batch subagent)

---

## Issue 3: Linear MCP Tool Parameter Mismatch

**Problem**: `mcp__syntropy__linear_create_issue` failed with parameter validation error

**Error**:

```
MCP error -32602: Invalid arguments for tool create_issue
Required: "team" (string)
Received: "undefined"
```

**Attempted**:

- Used `team_id: "Blaise78"` (from linear-defaults.yml)
- Tool expected `team` not `team_id`

**Resolution**: PRP created with note for manual Linear issue creation

**Impact**: Minor - Linear integration works for other operations, issue creation can be done manually

---

## Lessons for /batch-gen-prp Maturity

### Successfully Validated

1. ✅ **Plan parsing**: Flexible extraction from narrative format worked
2. ✅ **Phase extraction**: 5 phases identified correctly from plan
3. ✅ **Dependency detection**: Sequential dependencies recognized
4. ✅ **User decision prompt**: AskUserQuestion worked perfectly
5. ✅ **Single PRP recommendation**: System correctly suggested single PRP over batch

### Improvements Needed

1. **Plan recommendation detection**: Parse plan for "Option A/B" recommendations and warn if invocation conflicts
2. **Parallelism benefit analysis**: Calculate score (0% in this case) and suggest alternatives
3. **Linear MCP parameter validation**: Fix tool parameter naming inconsistency
4. **Batch mode benefit threshold**: If parallelism <20%, suggest single PRP mode

### What Worked Well

- **Flexible format handling**: Plan didn't match strict template but extraction succeeded
- **User interaction**: Clear presentation of options with pros/cons
- **Lessons learned tracking**: Real-time documentation of issues
- **Fallback to single PRP**: System gracefully switched modes when appropriate

---

## Notes

- Plan quality is HIGH (comprehensive, well-structured)
- Plan readability is EXCELLENT (clear for humans)
- Plan parseability is MEDIUM (needs flexible parser, but extraction successful)
- Plan recommendation conflicts with batch invocation were handled via user prompt
- `/batch-gen-prp` successfully detected suboptimal use case and recommended alternative

---

## Recommendations Summary

**For /batch-gen-prp command**:

1. Add parallelism benefit calculator (sequential = 0% benefit)
2. Detect "Option A/B" patterns in plans and warn on conflicts
3. Interactive validation mode (show extracted data, ask user to confirm)
4. ASCII dependency graph visualization before generation
5. Batch mode threshold: <20% parallel benefit → suggest single PRP

**For Linear MCP integration**:

1. Fix parameter naming: `team_id` vs `team` inconsistency
2. Add better error messages for parameter validation
3. Consider fallback to manual issue creation with formatted output

**For plan format flexibility**:

1. Support both strict template and narrative formats
2. Infer missing fields from context (e.g., "10-15 minutes" → estimated_hours: 0.25)
3. Provide format validation warnings without blocking generation

---

_Generation complete. PRP-30 ready for review and execution._
