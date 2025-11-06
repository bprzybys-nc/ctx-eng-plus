---
prp_id: 36.2.2
feature_name: CE Framework Project Initializer - Handler Implementation
status: pending
created: 2025-11-06T11:20:59.408959
updated: 2025-11-06T11:20:59.408959
complexity: low
estimated_hours: 0.5
dependencies: PRP-36.1.1 (ProjectInitializer class)
stage: 2
execution_order: 3
merge_order: 3
issue: TBD
---

# CE Framework Project Initializer - Handler Implementation

## 1. TL;DR

**Objective**: CE Framework Project Initializer - Handler Implementation

**What**: Implement `cmd_init_project` handler function in `tools/ce/cli_handlers.py` that orchestrates project initialization using ProjectInitializer.

**Goal**: Create handler function that connects CLI to P...

**Why**: Enable functionality described in INITIAL.md with 4 reference examples

**Effort**: Low (0.5 hours - simple handler function)

**Dependencies**: PRP-36.1.1 (ProjectInitializer class)


## 2. Context

### Background

Implement `cmd_init_project` handler function in `tools/ce/cli_handlers.py` that orchestrates project initialization using ProjectInitializer.

**Goal**: Create handler function that connects CLI to ProjectInitializer class

**What to Build**:
1. cmd_init_project(args) function in cli_handlers.py
2. Parse target_dir from args, resolve to absolute path
3. Validate target_dir exists
4. Create ProjectInitializer instance with dry_run flag
5. Handle --blend-only flag (call blend() only)
6. Handle --phase flag (call run(phase=args.phase))
7. Return exit code (0 = success, 1 = error)

**Acceptance Criteria**:
1. ✅ cmd_init_project function created in cli_handlers.py
2. ✅ Imports ProjectInitializer from ce.init_project
3. ✅ Validates target_dir exists before initialization
4. ✅ Passes dry_run flag to ProjectInitializer
5. ✅ Handles --blend-only flag correctly
6. ✅ Handles --phase flag correctly
7. ✅ Returns proper exit codes
8. ✅ Error messages include 🔧 troubleshooting

### Constraints and Considerations

**Error Handling**:
- Validate target_dir exists before creating ProjectInitializer
- Catch exceptions from ProjectInitializer methods
- Include 🔧 troubleshooting messages:
  - "Target directory not found" → Check path
  - "ProjectInitializer failed" → Show underlying error

**Flag Logic**:
- --blend-only takes precedence over --phase
- If --blend-only: call initializer.blend() directly
- Otherwise: call initializer.run(phase=args.phase)

**Exit Codes**:
- 0: Success
- 1: User error (invalid target_dir, etc.)
- 2: Initialization error (from ProjectInitializer)

**Integration**:
- PRP-36.2.1 wires this handler to CLI subparser
- Both PRPs can be developed in parallel (no file conflicts)
- Both depend on PRP-36.1.1 being complete

**Testing**:
- Unit test with mock ProjectInitializer
- Test target_dir validation
- Test --blend-only flag behavior
- Test --phase flag behavior
- Test exit codes

**Code Quality**:
- Function: ~30-40 lines
- Single responsibility: CLI arg handling + orchestration
- No business logic (delegated to ProjectInitializer)
- Clear error messages with troubleshooting

### Files Modified

**MODIFY**:
- `tools/ce/cli_handlers.py` - Add cmd_init_project(args) handler function

**IMPORTS**:
- `from ce.init_project import ProjectInitializer` (from PRP-36.1.1)
- `from pathlib import Path` (standard library)

**INTEGRATION**:
- Called by init-project subparser from `tools/ce/__main__.py` (implemented in PRP-36.2.1)

### Documentation References

- Standard (library documentation)
- File (library documentation)
- ProjectInitializer (library documentation)
- Other (library documentation)
- all (library documentation)
- CLI (library documentation)


## 3. Implementation Steps

### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (20 minutes)

1. Open `tools/ce/cli_handlers.py` and add `cmd_init_project(args)` function
2. Import ProjectInitializer from `ce.init_project`
3. Parse and resolve target_dir to absolute path: `Path(args.target_dir).resolve()`
4. Validate target_dir exists, return exit code 1 with error if not
5. Create ProjectInitializer instance with dry_run flag from args
6. Implement flag logic: if args.blend_only, call initializer.blend(), else call initializer.run(phase=args.phase)
7. Add exception handling with 🔧 troubleshooting messages
8. Return exit code (0=success, 1=error)

### Phase 3: Testing and Validation (10 minutes)

1. Create unit tests in `tools/tests/test_cli_handlers.py` with mock ProjectInitializer
2. Test target_dir validation (non-existent dir returns exit code 1)
3. Test --blend-only flag calls blend() method only
4. Test --phase flag passes correct phase to run() method
5. Test exception handling and error messages


## 4. Validation Gates

### Gate 1: Handler Unit Tests

**Command**: `uv run pytest tools/tests/test_cli_handlers.py::test_cmd_init_project -v`

**Success Criteria**:
- All cmd_init_project unit tests pass
- Mock ProjectInitializer tests pass
- target_dir validation test passes (non-existent dir returns exit code 1)
- Flag behavior tests pass (--blend-only, --phase)

### Gate 2: Handler Integration Test

**Commands**:
```bash
cd tools
# Test with real ProjectInitializer (requires PRP-36.1.1 complete)
mkdir -p /tmp/test-handler-target
uv run ce init-project /tmp/test-handler-target --dry-run
```

**Success Criteria**:
- Handler executes without errors
- Exit code 0 returned on success
- Error messages include 🔧 troubleshooting when appropriate

### Gate 3: Error Handling Test

**Commands**:
```bash
cd tools
# Test with non-existent directory
uv run ce init-project /non/existent/path
echo "Exit code: $?"
```

**Success Criteria**:
- Error message displayed: "Target directory not found"
- Exit code 1 returned
- Troubleshooting message provided


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

### Risk 1: ProjectInitializer not yet implemented (PRP-36.1.1)

**Impact**: HIGH - Cannot import or use ProjectInitializer class

**Mitigation**:
- Clear dependency: PRP-36.1.1 must be complete first
- Can implement handler with mock ProjectInitializer for unit tests
- Integration tests require PRP-36.1.1 completion

### Risk 2: Incorrect exception handling

**Impact**: MEDIUM - Users see cryptic errors without troubleshooting

**Mitigation**:
- Follow error handling pattern from cmd_blend and cmd_vacuum handlers
- Include 🔧 troubleshooting messages for all error cases
- Test with non-existent target directory

### Risk 3: Flag logic bug (--blend-only precedence)

**Impact**: LOW - Easy to test and fix

**Mitigation**:
- Write specific unit tests for flag combinations
- Test: --blend-only with --phase should ignore --phase
- Validate against master plan specification

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
