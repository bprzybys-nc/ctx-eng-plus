# Unified Batch Command Framework - Implementation Plan

## Overview
Deliver a pragmatic, two-phase approach to unifying batch commands (gen, exe, review, context-update) with Sonnet orchestrator + Haiku subagents architecture.

## Success Criteria
- [ ] MVP framework deployed and usable in production (Week 3)
- [ ] All 4 batch commands refactored and working end-to-end
- [ ] Phase 2 monitoring infrastructure in place
- [ ] 60%+ code duplication reduction achieved
- [ ] 3-week timeline met (vs 6-week original)

---

## Phases

### Phase 1: Foundation - Orchestrator & Subagent Templates (Week 1)

**Goal**: Create reusable orchestrator template and all 4 subagent templates

**Estimated Hours**: 8

**Complexity**: medium

**Files Modified**:
- .claude/orchestrators/base-orchestrator.md
- .claude/subagents/generator-subagent.md
- .claude/subagents/executor-subagent.md
- .claude/subagents/reviewer-subagent.md
- .claude/subagents/context-updater-subagent.md

**Dependencies**: None

**Implementation Steps**:
1. Write base-orchestrator.md with 6-phase coordination logic (parsing, validation, analysis, spawning, monitoring, aggregation)
2. Write generator-subagent.md for PRP creation (input/output specs, tool allowlist)
3. Write executor-subagent.md for implementation (execution plan, checkpoint logic)
4. Write reviewer-subagent.md for peer review (structural + semantic modes)
5. Write context-updater-subagent.md for context sync (simple transformation logic)
6. Document all templates with examples

**Validation Gates**:
- [ ] All 5 template files created and readable
- [ ] Each template has clear input/output spec examples
- [ ] Orchestrator logic covers all 6 phases
- [ ] Subagents reference orchestrator correctly
- [ ] No syntax errors in templates
- [ ] Total lines: ~730 lines (target ±50 lines)

**Conflict Notes**: None (new files, no modifications to existing)

---

### Phase 2: Dependency Analyzer - Topological Sort & Cycle Detection (Week 1)

**Goal**: Implement Python utility for dependency analysis, staging, and cycle detection

**Estimated Hours**: 2

**Complexity**: medium

**Files Modified**:
- .ce/orchestration/dependency_analyzer.py
- tests/test_dependency_analyzer.py

**Dependencies**: Phase 1 (needs orchestrator template understanding)

**Implementation Steps**:
1. Create dependency_analyzer.py with topological sort algorithm
2. Implement cycle detection (return cycle path if found)
3. Implement stage assignment (group independent items)
4. Add file conflict detection (multiple items modifying same file)
5. Write unit tests (>90% coverage)
6. Test with example batches

**Validation Gates**:
- [ ] Topological sort works correctly (test with 5+ test cases)
- [ ] Cycle detection returns cycle path (verify error message)
- [ ] Stage assignment maximizes parallelism
- [ ] File conflict detection accurate
- [ ] Unit test coverage >90%
- [ ] No dependencies on external packages (stdlib only)

**Conflict Notes**: None (new file, adds to .ce/orchestration/)

---

### Phase 3: Unit Tests for Dependency Analyzer (Week 1)

**Goal**: Comprehensive test coverage for dependency analysis logic

**Estimated Hours**: 2

**Complexity**: low

**Files Modified**:
- tests/test_dependency_analyzer.py

**Dependencies**: Phase 2 (needs dependency_analyzer.py)

**Implementation Steps**:
1. Test topological sort (linear, branching, complex dependencies)
2. Test cycle detection (single cycle, multi-node cycle, error messages)
3. Test stage assignment (sequential, parallel, mixed)
4. Test file conflict detection (single file, multiple files, no conflicts)
5. Test edge cases (empty input, single item, circular refs)
6. Generate coverage report

**Validation Gates**:
- [ ] All test functions pass (pytest)
- [ ] Coverage >90% (pytest-cov)
- [ ] Test output clearly shows each scenario
- [ ] Error handling tested
- [ ] No mock data - real test cases only

**Conflict Notes**: None (test file only)

---

### Phase 4: Refactor /batch-gen-prp (Week 2)

**Goal**: Adapt /batch-gen-prp command to use orchestrator template + generator subagent

**Estimated Hours**: 4

**Complexity**: medium

**Files Modified**:
- .claude/commands/batch-gen-prp.md

**Dependencies**: Phase 1, Phase 2 (needs orchestrator + subagent + dependency analyzer)

**Implementation Steps**:
1. Extract core coordination logic from existing command
2. Adapt to use base-orchestrator.md template (6 phases)
3. Update to use generator-subagent.md for PRP creation
4. Integrate dependency_analyzer.py for stage assignment
5. Update monitoring to use file-based heartbeat protocol
6. Add integration test (3-4 sample phases)
7. Verify JSON output format matches subagent contract

**Validation Gates**:
- [ ] Command still works with existing test plan files
- [ ] Generates 3-4 PRPs in correct stages
- [ ] Heartbeat files created and monitored correctly
- [ ] Linear issues created for generated PRPs
- [ ] Error handling for circular dependencies
- [ ] Time to generate 4 PRPs <10 minutes

**Conflict Notes**: Refactoring existing command (no new files)

---

### Phase 5: Refactor /batch-exe-prp (Week 2)

**Goal**: Adapt /batch-exe-prp command to use orchestrator template + executor subagent

**Estimated Hours**: 4

**Complexity**: medium

**Files Modified**:
- .claude/commands/batch-exe-prp.md

**Dependencies**: Phase 1, Phase 2, Phase 4 (needs all infrastructure)

**Implementation Steps**:
1. Extract execution coordination logic
2. Adapt to use base-orchestrator.md template
3. Update to use executor-subagent.md for implementation
4. Integrate checkpoint/resume logic (git-based)
5. Update validation integration (L1-L4 validation)
6. Update monitoring (git log polling instead of heartbeat)
7. Add integration test (1-2 real PRPs)

**Validation Gates**:
- [ ] Executes 2 real PRPs end-to-end
- [ ] All 4 validation levels work
- [ ] Checkpoints created after each phase
- [ ] Git commits created for each phase
- [ ] Parallel execution works (stage 2 with 3+ PRPs)
- [ ] Time to execute 4-phase PRP <30 minutes

**Conflict Notes**: Refactoring existing command

---

### Phase 6: Integration Test - Gen + Exe (Week 2)

**Goal**: Test end-to-end workflow: generate PRPs, then execute them

**Estimated Hours**: 2

**Complexity**: low

**Files Modified**:
- tests/test_batch_integration_gen_exe.py

**Dependencies**: Phase 4, Phase 5 (needs refactored commands)

**Implementation Steps**:
1. Create test plan with 4-6 phases
2. Run /batch-gen-prp on test plan
3. Verify all PRPs generated correctly
4. Run /batch-exe-prp on generated batch
5. Verify all PRPs executed successfully
6. Check for any conflicts or errors
7. Validate final state (code changes, tests passing)

**Validation Gates**:
- [ ] Test plan generates 4-6 PRPs successfully
- [ ] All generated PRPs execute without errors
- [ ] Code changes match PRP requirements
- [ ] Tests pass for all executed PRPs
- [ ] No conflicts in batch merge
- [ ] Full workflow takes <45 minutes

**Conflict Notes**: None (test file only)

---

### Phase 7: Refactor /batch-peer-review (Week 3)

**Goal**: Adapt /batch-peer-review command to use orchestrator template + reviewer subagent

**Estimated Hours**: 2

**Complexity**: medium

**Files Modified**:
- .claude/commands/batch-peer-review.md

**Dependencies**: Phase 1, Phase 2, Phase 4 (needs infrastructure + generated PRPs)

**Implementation Steps**:
1. Extract review coordination logic
2. Adapt to use base-orchestrator.md template
3. Update to use reviewer-subagent.md (structural + semantic modes)
4. Implement shared context optimization (read CLAUDE.md once, pass to all reviewers)
5. Update inter-PRP consistency checks
6. Add test (review 3-4 generated PRPs)
7. Verify review report format

**Validation Gates**:
- [ ] Reviews 3-4 PRPs in parallel
- [ ] Detects issues in test PRPs (missing validation gates, etc.)
- [ ] Shared context optimization works (tokens reduced by 70%+)
- [ ] Review time <5 minutes for 3-4 PRPs
- [ ] Report includes inter-PRP consistency checks

**Conflict Notes**: Refactoring existing command

---

### Phase 8: Refactor /batch-update-context (Week 3)

**Goal**: Adapt /batch-update-context command to use orchestrator template + context-updater subagent

**Estimated Hours**: 2

**Complexity**: low

**Files Modified**:
- .claude/commands/batch-update-context.md

**Dependencies**: Phase 1, Phase 2 (needs infrastructure)

**Implementation Steps**:
1. Extract context sync logic
2. Adapt to use base-orchestrator.md template
3. Update to use context-updater-subagent.md
4. Implement PRP status update logic
5. Add test (update context for 2 executed PRPs)
6. Verify drift score calculation

**Validation Gates**:
- [ ] Updates context for 2+ executed PRPs
- [ ] Drift scores calculated correctly
- [ ] PRP files updated with implementation status
- [ ] Test takes <3 minutes for 2 PRPs

**Conflict Notes**: Refactoring existing command

---

### Phase 9: Documentation & Deployment (Week 3)

**Goal**: Complete documentation and deploy Phase 1 to production

**Estimated Hours**: 2

**Complexity**: low

**Files Modified**:
- PRPs/feature-requests/PRP-47-USAGE-GUIDE.md
- .claude/orchestrators/README.md
- .claude/subagents/README.md

**Dependencies**: Phase 4-8 (all refactored commands)

**Implementation Steps**:
1. Write usage guide for new batch command workflow
2. Document architecture overview (one page)
3. Document each subagent type (one page per type)
4. Create troubleshooting guide
5. Add examples for common workflows
6. Review all documentation
7. Deploy to production

**Validation Gates**:
- [ ] Usage guide covers all 4 batch commands
- [ ] Architecture diagram clear and accurate
- [ ] Troubleshooting guide has 5+ scenarios
- [ ] Examples include gen→exe→review workflow
- [ ] No broken links or references
- [ ] Documentation reviewed and approved

**Conflict Notes**: None (new documentation files)

---

### Phase 10: Phase 2 Preparation - Metrics & Monitoring (Week 4 start)

**Goal**: Setup production monitoring infrastructure for Phase 2

**Estimated Hours**: 4

**Complexity**: low

**Files Modified**:
- .ce/scripts/analyze-batch.py
- .ce/scripts/trend-analysis.py

**Dependencies**: Phase 1-9 (all Phase 1 work must be complete)

**Implementation Steps**:
1. Create analyze-batch.py script (batch metrics collection)
2. Create trend-analysis.py script (identify bottlenecks)
3. Define metrics schema (duration, tokens, cost, errors)
4. Setup batch metrics archival (.ce/completed-batches/)
5. Document Phase 2 workflow and decision framework
6. Test scripts with real batch data

**Validation Gates**:
- [ ] analyze-batch.py generates correct metrics JSON
- [ ] trend-analysis.py identifies patterns from 2+ batches
- [ ] Metrics schema covers all needed data
- [ ] Scripts have error handling
- [ ] Documentation explains Phase 2 decision framework

**Conflict Notes**: None (new utility scripts)

---

## Timeline Summary

| Phase | Week | Hours | Status |
|-------|------|-------|--------|
| 1-3 | 1 | 12 | Foundation (templates + analyzer + tests) |
| 4-5 | 2 | 8 | Refactoring (gen + exe + integration test) |
| 6-9 | 3 | 6 | Completion (review + context + docs) + Phase 2 prep |
| **Total Phase 1** | **1-3** | **20** | **SHIP TO PRODUCTION** |
| 10 | 4+ | 4+ | Phase 2 infrastructure (monitoring) |

## Success Definition

**Phase 1 Complete (End of Week 3)**:
- ✅ All 4 batch commands unified and working
- ✅ Code duplication reduced <10% (from 30%)
- ✅ Comprehensive documentation
- ✅ All tests passing (>90% coverage)
- ✅ Ready for production use

**Phase 2 Launch (Week 4+)**:
- ✅ Production batches running with MVP framework
- ✅ Metrics collection in place
- ✅ Issues identified and prioritized
- ✅ Data-driven improvements implemented as needed
