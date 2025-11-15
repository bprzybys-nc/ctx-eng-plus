---
prp_id: 36.2.1
feature_name: CE Framework Project Initializer - CLI Integration
status: pending
created: 2025-11-06T11:20:35.305302
updated: 2025-11-06T11:20:35.305302
complexity: low
estimated_hours: 0.5
dependencies: PRP-36.1.1 (ProjectInitializer class)
stage: 2
execution_order: 2
merge_order: 2
issue: TBD
---

# CE Framework Project Initializer - CLI Integration

## 1. TL;DR

**Objective**: CE Framework Project Initializer - CLI Integration

**What**: Add `init-project` subcommand to CLI parser in `tools/ce/__main__.py` with all flags for project initialization.

**Goal**: Integrate init-project command into CE CLI with proper argument parsing

**W...

**Why**: Enable functionality described in INITIAL.md with 5 reference examples

**Effort**: Low (0.5 hours - simple CLI integration)

**Dependencies**: PRP-36.1.1 (ProjectInitializer class)


## 2. Context

### Background

Add `init-project` subcommand to CLI parser in `tools/ce/__main__.py` with all flags for project initialization.

**Goal**: Integrate init-project command into CE CLI with proper argument parsing

**What to Build**:
1. Add `init-project` subparser to main argument parser
2. Add `target_dir` positional argument
3. Add `--dry-run` flag (show actions without executing)
4. Add `--phase` flag with choices [extract, blend, initialize, verify, all]
5. Add `--blend-only` flag (skip extraction for re-initialization)
6. Wire subparser to cmd_init_project handler in cli_handlers.py

**Acceptance Criteria**:
1. ✅ `uv run ce init-project --help` shows usage
2. ✅ Subparser accepts target_dir positional argument
3. ✅ All 3 flags (--dry-run, --phase, --blend-only) registered
4. ✅ Subparser calls cmd_init_project handler
5. ✅ Help text describes each flag clearly
6. ✅ Default values set correctly (phase="all", dry_run=False)

### Constraints and Considerations

**CLI Design**:
- Use argparse subparsers pattern (consistent with blend, vacuum)
- target_dir as positional (required, no flag needed)
- --dry-run flag for safety (default: False)
- --phase choices validate input
- --blend-only is convenience alias for --phase blend

**Integration**:
- Handler function cmd_init_project will be implemented in PRP-36.2.2
- This PRP only adds CLI parsing, not implementation logic
- Can be tested with placeholder handler that prints args

**Error Handling**:
- argparse validates --phase choices automatically
- target_dir Path conversion automatic
- No custom validation needed in this file

**Testing**:
- CLI integration test: call with --help
- Verify subparser registered correctly
- Test flag combinations (--dry-run, --phase extract, etc.)

**Code Quality**:
- Add subparser definition (20-30 lines)
- Wire to handler (1 line in dispatch logic)
- Total modification: ~30 lines in __main__.py

### Files Modified

**MODIFY**:
- `tools/ce/__main__.py` - Add init-project subparser with 4 arguments (target_dir, --dry-run, --phase, --blend-only)

**INTEGRATION**:
- Calls `cmd_init_project` handler from `tools/ce/cli_handlers.py` (implemented in PRP-36.2.2)

### Documentation References

- Standard (library documentation)
- Command-line (library documentation)
- Type (library documentation)
- Main (library documentation)
- Handler (library documentation)
- ProjectInitializer (library documentation)


## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (20 minutes)

1. Open `tools/ce/__main__.py` and locate subparsers section
2. Add `init-project` subparser with help text
3. Add `target_dir` positional argument (type=str)
4. Add `--dry-run` flag (action="store_true")
5. Add `--phase` argument with choices=[extract, blend, initialize, verify, all], default="all"
6. Add `--blend-only` flag (action="store_true")
7. Wire subparser to call `cmd_init_project` handler from cli_handlers module

### Phase 3: Testing and Validation (10 minutes)

1. Test CLI with `uv run ce init-project --help` (verify all flags shown)
2. Test argument parsing with placeholder handler
3. Verify default values (phase="all", dry_run=False)
4. Test flag combinations (--dry-run, --phase extract, --blend-only)


## 4. Validation Gates

### Gate 1: CLI Help Text

**Command**: `cd tools && uv run ce init-project --help`

**Success Criteria**:
- Help text displays without errors
- Shows "init-project" command description
- Lists all 4 arguments: target_dir (positional), --dry-run, --phase, --blend-only
- Shows default values and choices for --phase

### Gate 2: Argument Parsing Test

**Commands**:
```bash
cd tools
# Test with placeholder handler (if implemented)
uv run ce init-project /tmp/test --dry-run --phase extract
uv run ce init-project /tmp/test --blend-only
```

**Success Criteria**:
- Arguments parse without errors
- Placeholder handler receives correct args values
- argparse validates --phase choices automatically

### Gate 3: Subparser Registration

**Command**: `cd tools && uv run ce --help | grep init-project`

**Success Criteria**:
- "init-project" subcommand appears in main help text
- Subcommand description visible


## 5. Testing Strategy

### Test Framework

pytest

### Test Command

```bash
uv run pytest tests/ -v
```

### Coverage Requirements

- Unit test coverage: ≥ 80%
- Integration tests for critical paths
- Edge cases from INITIAL.md covered


## 6. Risks & Mitigations

### Risk 1: CLI conflicts with existing subcommands

**Impact**: LOW - argparse would error on duplicate subparser

**Mitigation**:
- Verify "init-project" name doesn't conflict with existing commands
- Check `tools/ce/__main__.py` for existing subparsers before adding

### Risk 2: Handler not yet implemented (PRP-36.2.2)

**Impact**: MEDIUM - CLI parsing works but handler missing causes runtime error

**Mitigation**:
- Can test with placeholder handler that prints args
- Final integration test requires PRP-36.2.2 completion
- Clear dependency: PRP-36.2.2 must be complete for full functionality

### Risk 3: Incorrect argparse configuration

**Impact**: LOW - Easy to test with --help flag

**Mitigation**:
- Test immediately after implementation with `uv run ce init-project --help`
- Verify default values match master plan specification
- Test all flag combinations

## 7. Rollout Plan

### Phase 1: Development

1. Implement core functionality
2. Write tests
3. Pass validation gates

### Phase 2: Review

1. Self-review code changes
2. Peer review (optional)
3. Update documentation

### Phase 3: Deployment

1. Merge to main branch
2. Monitor for issues
3. Update stakeholders


---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: 0
- **Test Patterns**: 1
- **Serena Available**: False

### Documentation Sources
- **Library Docs**: 0
- **External Links**: 0
- **Context7 Available**: False
