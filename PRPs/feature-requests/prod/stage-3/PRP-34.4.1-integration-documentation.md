---
prp_id: PRP-34.4.1
feature_name: Integration & Documentation
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
batch: 34
stage: 4
order: 1
complexity: medium
estimated_hours: 2.0
dependencies: 34.1.1, 34.2.1, 34.2.2, 34.2.3, 34.2.4, 34.2.5, 34.2.6, 34.3.1, 34.3.2, 34.3.3
merge_order: 11
conflict_potential: LOW
---

# Integration & Documentation

## 1. TL;DR

**Objective**: Integrate all blending strategies into 4-phase pipeline, update INITIALIZATION.md and syntropy-mcp-init-specification.md, create end-to-end tests

**What**: Final integration PRP that wires all components together (Detection, Classification, Domain Strategies, Cleanup) into a cohesive 4-phase orchestrator with comprehensive documentation and E2E validation.

**Why**: Complete the blend tool implementation by:
1. Integrating all 6 domain strategies (Settings, CLAUDE.md, Memories, Examples, PRPs, Commands)
2. Documenting the complete workflow in user-facing docs
3. Validating 3 critical scenarios: greenfield, mature project, CE 1.0 migration
4. Providing automated initialization via Syntropy MCP

**Effort**: Medium (2.0 hours)

**Dependencies**: ALL previous PRPs in batch 34 (34.1.1, 34.2.x, 34.3.x)


## 2. Context

### Background

**Current State**:
- Phase 1 (Detection): Bucket collection implemented (34.1.1)
- Phase 2 (Classification): 6 domain strategies implemented (34.2.1-34.2.6)
- Phase 3 (Blending): Orchestrator + cleanup modules implemented (34.3.1-34.3.3)
- Phase 4 (Documentation): Missing documentation and E2E validation

**Problem**:
1. Components exist in isolation - need integration into single orchestrator
2. User-facing documentation not updated with new blend workflow
3. No end-to-end tests validating complete pipeline
4. Syntropy MCP init spec doesn't reference blend tool

**Requirements**:

1. **Orchestrator Integration**:
   - Register all 6 domain strategies in core.py
   - Wire Detection → Classification → Blending → Cleanup into 4-phase pipeline
   - Expose via `uv run ce blend --all` CLI command
   - Support all flags: --dry-run, --interactive, --fast, --quality, --scan, --skip-cleanup

2. **Documentation Updates**:
   - **INITIALIZATION.md**: Add blend tool as primary workflow (Phase 3)
   - **syntropy-mcp-init-specification.md**: Integrate blend into automated init
   - Document all CLI flags and usage examples
   - Add troubleshooting section for common blend issues

3. **E2E Test Suite**:
   - **Greenfield Test**: Empty project (0 files) → successful blend
   - **Mature Project Test**: Existing files (100+) → blend with deduplication
   - **CE 1.0 Migration Test**: Legacy directories → cleanup + blend
   - Coverage target: ≥80% for blend module

4. **Validation**:
   - All validation gates from previous PRPs integrate correctly
   - CLI works with all flag combinations
   - E2E tests pass in CI/CD

### Constraints and Considerations

**Integration Constraints**:
- Must preserve existing CLI commands (no breaking changes)
- Orchestrator should handle strategy failures gracefully
- Cleanup phase is optional (--skip-cleanup flag)

**Documentation Constraints**:
- INITIALIZATION.md already has 5-phase structure - blend fits in Phase 3
- Syntropy MCP spec expects bash commands - document `uv run ce blend --all`
- Keep docs token-efficient (no duplicate content)

**Testing Constraints**:
- E2E tests need isolated temp directories (no interference)
- Test data should be minimal but representative
- Tests must clean up after themselves

**Rollback Plan**:
- If integration fails, each component can operate independently
- Documentation changes are non-breaking (additive only)
- E2E tests are new files (no impact on existing tests)

### Documentation References

- INITIALIZATION.md (CE 1.1 initialization guide)
- syntropy-mcp-init-specification.md (automated init spec)
- tools/ce/blend.py (blend module to be integrated)
- tools/ce/core.py (CLI orchestrator)


## 3. Implementation Steps

### Phase 1: Orchestrator Integration (30 min)

1. **Register Domain Strategies** (tools/ce/core.py):
   ```python
   from ce.blend import (
       SettingsBlendStrategy,
       ClaudeMdBlendStrategy,
       MemoriesBlendStrategy,
       ExamplesBlendStrategy,
       PrpsBlendStrategy,
       CommandsBlendStrategy
   )

   # In blend_files() function
   strategies = [
       SettingsBlendStrategy(),
       ClaudeMdBlendStrategy(),
       MemoriesBlendStrategy(),
       ExamplesBlendStrategy(),
       PrpsBlendStrategy(),
       CommandsBlendStrategy()
   ]
   ```

2. **Wire 4-Phase Pipeline**:
   ```python
   def blend_files(args):
       # Phase 1: Detect buckets
       buckets = detect_buckets(target_dir, args.scan)

       # Phase 2: Classify files by domain
       classified = classify_files(buckets, strategies)

       # Phase 3: Blend per domain
       results = []
       for domain, files in classified.items():
           strategy = get_strategy(domain)
           result = strategy.blend(files, mode=args.mode)
           results.append(result)

       # Phase 4: Cleanup (if not skipped)
       if not args.skip_cleanup:
           cleanup_artifacts(results)

       return results
   ```

3. **Add CLI Flags**:
   ```python
   parser.add_argument('--all', action='store_true', help='Blend all domains')
   parser.add_argument('--dry-run', action='store_true', help='Show actions without executing')
   parser.add_argument('--interactive', action='store_true', help='Prompt for conflicts')
   parser.add_argument('--fast', action='store_true', help='Fast mode (skip validations)')
   parser.add_argument('--quality', action='store_true', help='Quality mode (extra checks)')
   parser.add_argument('--scan', type=str, help='Scan directory for buckets')
   parser.add_argument('--skip-cleanup', action='store_true', help='Skip cleanup phase')
   ```

### Phase 2: Documentation Updates (45 min)

1. **Update INITIALIZATION.md** (examples/INITIALIZATION.md):
   - Add "Phase 3: Blending" section with `uv run ce blend --all`
   - Document all flags with examples:
     ```bash
     # Dry-run mode (report only, no changes)
     uv run ce blend --all --dry-run

     # Interactive mode (prompt for conflicts)
     uv run ce blend --all --interactive

     # Fast mode (skip validations)
     uv run ce blend --all --fast

     # Quality mode (extra checks)
     uv run ce blend --all --quality

     # Custom scan directory
     uv run ce blend --all --scan /path/to/buckets

     # Skip cleanup
     uv run ce blend --all --skip-cleanup
     ```
   - Add troubleshooting section for common issues

2. **Update syntropy-mcp-init-specification.md** (.ce/docs/):
   - Add blend tool to "Phase 3: Repomix Package Handling" section
   - Document automated workflow:
     ```bash
     # Extract infrastructure package
     npx repomix --unpack .ce/ce-infrastructure.xml --target tmp/extraction/

     # Blend extracted files with user files
     uv run ce blend --all --fast

     # Cleanup extraction artifacts
     rm -rf tmp/extraction/
     ```

3. **Add CLI Usage Examples** (CLAUDE.md):
   - Update "Framework Initialization" section with blend examples
   - Document flag combinations for different scenarios

### Phase 3: E2E Test Suite (45 min)

1. **Create E2E Test File** (tools/tests/test_e2e_blend.py):
   ```python
   import pytest
   from pathlib import Path
   from ce.blend import blend_files

   @pytest.fixture
   def temp_project(tmp_path):
       """Create isolated temp directory for testing"""
       project = tmp_path / "test-project"
       project.mkdir()
       return project

   def test_greenfield_blend(temp_project):
       """Test blending in empty project (0 files)"""
       # Setup: Empty directory
       assert len(list(temp_project.iterdir())) == 0

       # Execute: Blend with no existing files
       result = blend_files(target_dir=temp_project, mode='fast')

       # Verify: All framework files created
       assert (temp_project / '.claude' / 'settings.local.json').exists()
       assert (temp_project / '.serena' / 'memories').exists()
       assert (temp_project / 'CLAUDE.md').exists()
       assert result.success is True

   def test_mature_project_blend(temp_project):
       """Test blending with existing files (deduplication)"""
       # Setup: Create existing files
       (temp_project / '.claude').mkdir()
       (temp_project / '.claude' / 'settings.local.json').write_text('{"existing": true}')
       (temp_project / 'CLAUDE.md').write_text('# Existing docs')

       # Execute: Blend with existing files
       result = blend_files(target_dir=temp_project, mode='interactive')

       # Verify: Files merged (not overwritten)
       settings = (temp_project / '.claude' / 'settings.local.json').read_text()
       assert '"existing": true' in settings  # Original preserved
       assert '"mcpServers"' in settings      # Framework added

       claude_md = (temp_project / 'CLAUDE.md').read_text()
       assert '# Existing docs' in claude_md  # Original preserved
       assert '## Context Engineering' in claude_md  # Framework added

   def test_ce_1_0_migration(temp_project):
       """Test CE 1.0 → CE 1.1 migration (legacy cleanup)"""
       # Setup: Create legacy CE 1.0 structure
       (temp_project / 'system').mkdir()
       (temp_project / 'system' / 'memories').mkdir()
       (temp_project / 'system' / 'memories' / 'old-memory.md').write_text('# Old')
       (temp_project / 'tools').mkdir()
       (temp_project / 'tools' / 'ce').mkdir()

       # Execute: Blend with cleanup
       result = blend_files(target_dir=temp_project, mode='fast', skip_cleanup=False)

       # Verify: Legacy directories removed
       assert not (temp_project / 'system').exists()
       assert not (temp_project / 'tools').exists()

       # Verify: New structure created
       assert (temp_project / '.serena' / 'memories').exists()
       assert (temp_project / '.ce' / 'tools').exists()
   ```

2. **Run Tests and Verify Coverage**:
   ```bash
   uv run pytest tools/tests/test_e2e_blend.py -v --cov=ce.blend --cov-report=term-missing
   ```

3. **Add Test to CI/CD** (if applicable)


## 4. Validation Gates

### Gate 1: Orchestrator Integration

**Command**: `uv run ce blend --help`

**Success Criteria**:
- All 6 strategies registered in orchestrator
- CLI help shows all flags (--dry-run, --interactive, --fast, --quality, --scan, --skip-cleanup)
- Command executes without errors

**Verification**:
```bash
uv run ce blend --help | grep -E '(dry-run|interactive|fast|quality|scan|skip-cleanup)'
```

### Gate 2: E2E Tests Pass

**Command**: `uv run pytest tools/tests/test_e2e_blend.py -v`

**Success Criteria**:
- All 3 E2E tests pass (greenfield, mature project, CE 1.0 migration)
- Code coverage ≥80% for blend module
- No test failures or errors

**Verification**:
```bash
uv run pytest tools/tests/test_e2e_blend.py -v --cov=ce.blend --cov-report=term-missing
```

### Gate 3: Documentation Updated

**Command**: Manual review

**Success Criteria**:
- INITIALIZATION.md has "Phase 3: Blending" section with `uv run ce blend --all`
- syntropy-mcp-init-specification.md references blend tool
- All CLI flags documented with examples
- Troubleshooting section added

**Verification**:
```bash
grep -A5 "Phase 3: Blending" examples/INITIALIZATION.md
grep "uv run ce blend" .ce/docs/syntropy-mcp-init-specification.md
```

### Gate 4: All CLI Flags Work

**Command**: Test each flag combination

**Success Criteria**:
- `uv run ce blend --all` works (default mode)
- `uv run ce blend --all --dry-run` shows actions without executing
- `uv run ce blend --all --interactive` prompts for conflicts
- `uv run ce blend --all --fast` skips validations
- `uv run ce blend --all --quality` performs extra checks
- `uv run ce blend --all --scan /path` scans custom directory
- `uv run ce blend --all --skip-cleanup` skips cleanup phase

**Verification**:
```bash
# Test dry-run (should not modify files)
uv run ce blend --all --dry-run
ls -la .claude/  # Should not exist if run in empty dir

# Test interactive (should prompt)
uv run ce blend --all --interactive

# Test fast (should skip validations)
time uv run ce blend --all --fast  # Should be <5s

# Test quality (should take longer)
time uv run ce blend --all --quality  # May take 10-15s
```


## 5. Testing Strategy

### Test Framework

pytest with coverage plugin

### Test Command

```bash
uv run pytest tools/tests/test_e2e_blend.py -v --cov=ce.blend --cov-report=term-missing
```

### Coverage Requirements

- Unit test coverage: ≥80% for blend module
- E2E tests for 3 critical scenarios (greenfield, mature, migration)
- All CLI flags tested (manual verification)

### Test Data

**Greenfield**:
- Empty directory (0 files)

**Mature Project**:
- Existing `.claude/settings.local.json` with custom config
- Existing `CLAUDE.md` with user content
- Existing `.serena/memories/` with user memories

**CE 1.0 Migration**:
- Legacy `system/memories/` directory
- Legacy `tools/ce/` directory
- Outdated file structure


## 6. Rollout Plan

### Phase 1: Integration (30 min)

1. Register all 6 domain strategies in core.py
2. Wire 4-phase pipeline (detect → classify → blend → cleanup)
3. Add CLI flags to argument parser
4. Test with `uv run ce blend --help`

### Phase 2: Documentation (45 min)

1. Update INITIALIZATION.md with blend workflow
2. Update syntropy-mcp-init-specification.md
3. Add CLI examples to CLAUDE.md
4. Write troubleshooting section

### Phase 3: Testing (45 min)

1. Create test_e2e_blend.py with 3 scenarios
2. Run tests and verify ≥80% coverage
3. Manual verification of all CLI flags
4. Update CI/CD (if applicable)

### Phase 4: Validation (15 min)

1. Run all 4 validation gates
2. Fix any issues found
3. Final documentation review
4. Mark PRP as completed


---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: N/A (integration PRP, no new patterns)
- **Test Patterns**: E2E testing with pytest fixtures
- **Serena Available**: False

### Documentation Sources
- **INITIALIZATION.md**: Primary user-facing initialization guide
- **syntropy-mcp-init-specification.md**: Automated init spec for MCP integration
- **CLAUDE.md**: Project-level instructions (CLI examples)

### Integration Points
- **tools/ce/core.py**: CLI orchestrator (register strategies, add blend command)
- **tools/ce/blend.py**: Blend module (all strategies implemented in prior PRPs)
- **tools/tests/test_e2e_blend.py**: New E2E test file

### Dependencies
- ALL previous PRPs in batch 34:
  - 34.1.1: Detection (bucket collection)
  - 34.2.1-34.2.6: Classification (6 domain strategies)
  - 34.3.1-34.3.3: Blending (orchestrator, cleanup)
