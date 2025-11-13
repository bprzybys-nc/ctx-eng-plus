# Tests Directory

Comprehensive test suite for Context Engineering tools and batch orchestration framework.

## Test Organization

```
tests/
├── fixtures/                                  # Test fixtures and data
│   ├── batch-integration-test-plan.md         # Test plan for gen+exe workflow
│   ├── integration_test.py                    # Generated fixture file (created by test batch)
│   └── test_helpers.py                        # Test helper utilities (created by test batch)
├── test_dependency_analyzer.py                # Tests for dependency analyzer
├── test_tool_inventory.py                     # Tests for tool inventory
├── test_batch_integration_gen_exe.py          # Integration tests for batch gen+exe workflow
└── README.md                                  # This file
```

## Running Tests

### Run All Tests

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_batch_integration_gen_exe.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_batch_integration_gen_exe.py::TestBatchGenExeIntegration -v
```

### Run Specific Test Method

```bash
pytest tests/test_batch_integration_gen_exe.py::TestBatchGenExeIntegration::test_generate_prps -v
```

### Run with Output

```bash
pytest tests/test_batch_integration_gen_exe.py -v -s
```

## Integration Tests

### Batch Gen + Exe Integration

Tests the complete workflow: generate PRPs from plan → execute PRPs.

**Test file**: `tests/test_batch_integration_gen_exe.py`

**Main test classes**:

1. **TestBatchGenExeIntegration** - End-to-end workflow tests
   - `test_generate_prps` - Tests PRP generation from test plan
   - `test_dependency_structure` - Tests dependency analysis and linking
   - `test_file_creation_from_execution` - Tests that execution creates files
   - `test_prp_completion_status` - Tests PRP status transitions
   - `test_git_commits_created` - Tests git checkpoint commits

2. **TestBatchIntegrationHelpers** - Utility functions
   - `get_prp_files()` - Get all PRP files for a batch
   - `extract_dependencies()` - Parse PRP dependencies
   - `verify_prp_structure()` - Validate PRP format

3. **TestCleanup** - Cleanup utilities
   - `cleanup_test_prps()` - Remove test PRP files
   - `cleanup_test_files()` - Remove generated test files

**What it tests**:

- PRP generation from test plan (4 phases with dependencies)
- Dependency analysis and staging
- PRP structure and format (YAML frontmatter, sections)
- Batch execution with dependencies
- Checkpoint commits created in git log
- Validation integration (generated tests pass)
- Final state verification (all PRPs completed)

**Test duration**: ~5-10 minutes (generation + execution)

**Test plan**: Uses `tests/fixtures/batch-integration-test-plan.md` which defines:
- Phase 1: Create test fixture file
- Phase 2: Add test assertions to fixture
- Phase 3: Create helper module (parallel with Phase 2)
- Phase 4: Integration test suite (depends on Phase 2 and 3)

**Cleanup**: Test creates PRP-999.*.md files and test fixtures. Cleanup is available via `TestCleanup` class methods.

## Test Fixtures

### batch-integration-test-plan.md

Test batch plan used by integration tests. Defines 4 phases with dependencies:

```
Phase 1 (no deps)
    ↓
    ├→ Phase 2 (depends on Phase 1)
    │
    └→ Phase 3 (depends on Phase 1, parallel with 2)
        ↓
        Phase 4 (depends on Phase 2 and 3)
```

This tests:
- Sequential dependencies (1→2)
- Parallel execution (2, 3 in same stage)
- Multi-dependencies (4 depends on 2, 3)

## Dependency Analyzer Tests

**Test file**: `tests/test_dependency_analyzer.py`

Tests the dependency analysis module used by batch generation:

- Graph construction and topological sorting
- Cycle detection
- Stage assignment
- File conflict detection
- Dependency resolution

## Tool Inventory Tests

**Test file**: `tests/test_tool_inventory.py`

Tests the tool inventory system.

## Manual Workflow Test

To manually test the gen→exe workflow:

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus

# Step 1: Generate PRPs from test plan
/batch-gen-prp tests/fixtures/batch-integration-test-plan.md

# Step 2: Check generated PRPs
ls -la PRPs/feature-requests/PRP-999.*.md

# Step 3: Verify dependency structure
grep "dependencies:" PRPs/feature-requests/PRP-999.*.md

# Step 4: Execute generated PRPs
/batch-exe-prp --batch 999

# Step 5: Verify execution
grep "status:" PRPs/feature-requests/PRP-999.*.md

# Step 6: Verify files created
ls -la tests/fixtures/integration_test.py
ls -la tests/fixtures/test_helpers.py

# Step 7: Run verification tests
pytest tests/test_batch_integration_gen_exe.py -v

# Step 8: Cleanup (optional)
rm PRPs/feature-requests/PRP-999.*.md
rm tests/fixtures/integration_test.py tests/fixtures/test_helpers.py
```

## Test Coverage

### Generation Tests
- PRP generation from markdown plan
- Dependency analysis and linking
- Batch ID and stage assignment
- File path calculations

### Execution Tests
- PRP file structure validation
- Dependency resolution during execution
- Subagent spawning and monitoring
- Checkpoint commits
- File creation and modification

### Integration Tests
- Complete gen→exe workflow
- Data flow from generator to executor
- Dependency chain validation
- Error handling and recovery

## Test Patterns

### Real Command Testing

Tests use real `subprocess.run()` calls to execute `/batch-gen-prp` and `/batch-exe-prp` commands rather than mocking:

```python
result = subprocess.run(
    ["bash", "-c", f"cd ... && /batch-gen-prp {test_plan_path}"],
    capture_output=True,
    text=True,
    timeout=600
)
```

**Why**: We want to catch real integration issues, not mock-induced false negatives.

### File System Verification

Tests verify actual file system changes:

```python
# Verify PRPs created
generated_prps = list(prp_dir.glob(f"PRP-{batch_id}.*.md"))
assert len(generated_prps) == 4

# Verify content
content = prp_path.read_text()
assert "prp_id:" in content
```

### Git Log Validation

Tests check git commit log for checkpoint commits:

```python
result = subprocess.run(
    ["git", "log", "--oneline", "--grep", f"PRP-{batch_id}"],
    capture_output=True,
    text=True
)
```

## Troubleshooting

### Test Times Out

**Problem**: Tests take >10 minutes or hit timeout

**Solution**:
- Ensure /batch-gen-prp and /batch-exe-prp commands are working
- Check that subagents are spawning (monitor heartbeat files)
- Verify no network issues blocking LLM API calls

### Test Files Left Behind

**Problem**: PRP-999.*.md files exist after test run

**Solution**:
- Manual cleanup: `rm PRPs/feature-requests/PRP-999.*.md`
- Or enable auto-cleanup by uncommenting cleanup fixture

### Generation Fails

**Problem**: /batch-gen-prp returns non-zero exit code

**Solution**:
- Check test plan exists: `ls tests/fixtures/batch-integration-test-plan.md`
- Verify plan syntax: grep "^##" tests/fixtures/batch-integration-test-plan.md
- Check orchestrator is configured: ls .claude/orchestration/

### Execution Fails

**Problem**: /batch-exe-prp returns non-zero exit code

**Solution**:
- Check PRPs were generated: `ls PRPs/feature-requests/PRP-999.*.md`
- Verify batch ID matches: `grep batch_id PRPs/feature-requests/PRP-999.*.md`
- Check git status (clean working tree required): `git status`

## CI/CD Integration

To integrate into CI/CD pipeline:

```bash
# In CI configuration
pytest tests/ -v --tb=short --maxfail=1
```

Set timeout to 15 minutes for integration tests:

```bash
pytest tests/test_batch_integration_gen_exe.py -v --timeout=900
```

## Performance Benchmarks

Expected test duration:

- **test_generate_prps**: 3-5 minutes (orchestrator + subagents)
- **test_dependency_structure**: <1 second
- **test_file_creation_from_execution**: <1 second (if PRPs executed)
- **test_prp_completion_status**: <1 second
- **test_git_commits_created**: <1 second

**Total**: ~5-10 minutes for full integration test run

## Notes

- Use batch ID 999 for tests (outside normal range, easy to identify)
- Tests should be idempotent (can run multiple times)
- Cleanup is critical (don't pollute repository with test files)
- Integration tests use real commands, not mocks
- Test duration includes waiting for subagents to complete
