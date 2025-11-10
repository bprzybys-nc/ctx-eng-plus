---
prp_id: PRP-47-TWO-PHASE
title: Pragmatic Batch Command Framework - Two Super-Phases (MVP → Prod)
status: planning
created: "2025-11-10"
updated: "2025-11-10"
type: feature
category: infrastructure
complexity: medium
estimated_hours: 20
priority: high
tags: [batch-commands, orchestration, subagents, sonnet, haiku, mvp-to-prod]
---

# Pragmatic Batch Command Framework
## Two Super-Phases: MVP (Ship & Use) → Prod (Diagnose & Fix)

> **Goal**: Deliver working unified batch framework in Phase 1 (3 weeks), use in production immediately, diagnose issues and fix in Phase 2 (parallel with usage).

---

## Overview

```
PHASE 1: MVP (Ship & Use)          PHASE 2: Prod (Diagnose & Fix)
─────────────────────────          ──────────────────────────────
Week 1-3: Build foundation         Week 4-6: Monitor + iterate
Deliverable: Working commands      Deliverable: Hardened framework
Ready for: Immediate production    Ready for: Scale to 50+ PRPs

    Build                               Validate
      ↓                                   ↓
    Test                              Diagnose
      ↓                                   ↓
    Ship ← Can use from now ←        Fix Issues
                                      ↓
                                    Optimize
```

---

## PHASE 1: MVP (Weeks 1-3) - Ship & Use Immediately

### Goal
Deliver a **fully functional batch framework** that unifies 4 batch commands and is ready for production use on Week 4.

### Scope: Minimal, Complete, Correct
- ✅ One orchestrator (Sonnet)
- ✅ Four subagents (Haiku)
- ✅ File-based coordination protocol
- ✅ Simple monitoring (print-based)
- ✅ Dependency analysis (topological sort)
- ✅ All 4 batch commands refactored & working
- ❌ Optimizations (Phase 2)
- ❌ Schemas/validation (Phase 2)
- ❌ Advanced monitoring (Phase 2)

### Deliverables (End of Week 3)

#### Code Files
```
.claude/orchestrators/
  └─ base-orchestrator.md          (300 lines)

.claude/subagents/
  ├─ generator-subagent.md         (100 lines)
  ├─ executor-subagent.md          (150 lines)
  ├─ reviewer-subagent.md          (100 lines)
  └─ context-updater-subagent.md   (80 lines)

.ce/orchestration/
  └─ dependency_analyzer.py        (100 lines)
```

#### Refactored Commands
- ✅ `/batch-gen-prp` (working, unified)
- ✅ `/batch-exe-prp` (working, unified)
- ✅ `/batch-peer-review` (working, unified)
- ✅ `/batch-update-context` (working, unified)

#### Documentation
- README: How to use batch commands
- Architecture overview (one page)
- Subagent specs (one page per type)
- Troubleshooting guide (basic)

#### Test Coverage
- Unit tests: Dependency analyzer
- Integration tests: Each batch command (3-4 PRPs)
- End-to-end test: Full batch (gen + exe + review)

### Week-by-Week Breakdown

#### Week 1: Foundation (8 hours)
**Goal**: Framework files + basic integration

**Tasks**:
- [ ] Write orchestrator template (6h)
  - 6-phase coordination logic
  - Heartbeat polling
  - Result aggregation
  - Error handling basics

- [ ] Write 4 subagent templates (4h total)
  - Input/output specs
  - Tool allowlist
  - Basic validation

- [ ] Implement `dependency_analyzer.py` (2h)
  - Topological sort
  - Cycle detection
  - Stage grouping

- [ ] Unit tests for dependency analyzer (2h)

**Checkpoint**: All framework files in place, dependency analyzer tested

#### Week 2: Integration & Refactoring (8 hours)
**Goal**: Refactor batch commands, get 2 working end-to-end

**Tasks**:
- [ ] Refactor `/batch-gen-prp` (4h)
  - Use orchestrator template
  - Use generator subagent
  - Test with 3 sample PRPs

- [ ] Refactor `/batch-exe-prp` (4h)
  - Use orchestrator template
  - Use executor subagent
  - Test with 1-2 real PRPs

- [ ] Integration test: Gen → Review (2h)
  - Batch of 4-6 PRPs
  - End-to-end validation

**Checkpoint**: 2 batch commands fully working, tests passing

#### Week 3: Completion & Polish (4 hours)
**Goal**: Finish remaining 2 commands, documentation, deploy

**Tasks**:
- [ ] Refactor `/batch-peer-review` (2h)
  - Use orchestrator template
  - Use reviewer subagent
  - Test with 3-4 PRPs

- [ ] Refactor `/batch-update-context` (2h)
  - Use orchestrator template
  - Use context-updater subagent
  - Test with 2 executed PRPs

- [ ] Write documentation (3h)
  - Usage guide
  - Troubleshooting
  - Architecture one-pager

- [ ] Final integration test (2h)
  - Full batch workflow
  - All 4 commands
  - Error handling

**Checkpoint**: All 4 commands working, docs complete, ready to ship

### Communication Protocol (MVP - Simple)

#### Input Spec (Orchestrator → Subagent)
```json
{
  "operation": "generate|execute|review|context-update",
  "batch_id": 47,
  "work_item_id": "PRP-47.2.1",
  "input": {
    "type": "phase|prp|artifact",
    "content": "...data..."
  },
  "timeout_minutes": 5
}
```

#### Heartbeat (Subagent → Orchestrator, every 30s)
```json
{
  "work_item_id": "PRP-47.2.1",
  "status": "analyzing|working|complete|failed",
  "progress": 65,
  "step": "Phase 1: Implementing...",
  "timestamp": 1699564823
}
```

#### Result (Subagent → Orchestrator)
```json
{
  "work_item_id": "PRP-47.2.1",
  "status": "success|failed",
  "output": {"files": [], "commits": [], "errors": []},
  "metrics": {"duration_seconds": 187, "tokens": 2840}
}
```

### Orchestrator: 6 Phases (MVP)

**Phase 1: Parse & Validate** (5s)
- Read input
- Validate format
- Extract metadata

**Phase 2: Dependency Analysis** (10s)
- Build graph
- Topological sort
- Detect cycles → abort if found
- Group → stages

**Phase 3: Spawn Subagents** (15s)
- For each stage:
  - Spawn N agents in parallel
  - Create heartbeat file
  - Pass input spec

**Phase 4: Monitor & Wait** (continuous)
- Poll heartbeat every 30s
- Update progress
- Kill if >60s stale (2 failed polls)
- Wait for completion

**Phase 5: Aggregate** (15s)
- Collect results
- Check file conflicts → warn if found
- Check dependencies → mark blocked if failed

**Phase 6: Report & Cleanup** (10s)
- Print summary
- Cleanup heartbeats
- Done

### Monitoring (MVP - Print-Based)

```
BATCH 47: /batch-gen-prp PLAN.md
═════════════════════════════════════════════
Stage 1 [1/4] ✓ DONE (2m 15s)
  PRP-47.1.1-api [COMPLETE] 9.1/10

Stage 2 [2/4] ⧖ IN_PROGRESS (1m 30s)
  PRP-47.2.1-auth [60%] Analyzing...
  PRP-47.2.2-middleware [45%] Generating...
  PRP-47.2.3-tests [72%] Writing...

Stage 3 [3/4] ⧗ PENDING
  PRP-47.3.1-integration (waiting)

Stage 4 [4/4] ⧗ PENDING
  PRP-47.4.1-deployment (waiting)

─────────────────────────────────────────────
Elapsed: 3m 45s | Tokens: 8,450 | Cost: $0.42
```

### Success Criteria (MVP)

| Criterion | Target |
|-----------|--------|
| **All 4 commands working** | ✅ Yes |
| **Unit tests passing** | ✅ >90% coverage |
| **Integration tests passing** | ✅ Batch of 6 PRPs |
| **Code duplication reduced** | ✅ <10% (from 30%) |
| **Docs complete** | ✅ Usable by team |
| **Ready for production** | ✅ Yes |

### Known Limitations (Phase 2)

- ⚠️ No shared context optimization (reads context independently)
- ⚠️ No JSON schemas (inline specs only)
- ⚠️ Manual conflict resolution (file conflicts need user action)
- ⚠️ Simple monitoring (no dashboard)
- ⚠️ No inter-PRP consistency checks (rare, will add if needed)

**These are acceptable for MVP. Phase 2 improves them based on real usage.**

---

## PHASE 2: Prod (Weeks 4-6+) - Diagnose & Fix in Parallel

### Goal
**Run production batches with MVP framework while diagnosing issues and fixing on the way.** Don't just deploy and forget—actively monitor, identify bottlenecks, fix iteratively.

### Approach
- **Week 4**: Start using MVP framework on real batches (4-8 PRPs typical)
- **Parallel**: Monitor, log issues, collect metrics
- **Weeks 5-6**: Fix issues based on real data, optimize based on bottlenecks
- **Ongoing**: Monitor, iterate, improve

### Parallel Workflow

```
Production Usage (MVP)              Improvement Cycle
──────────────────────              ─────────────────
Run batch 1 (gen-exe-review)        ↓
   ↓ Monitor, log, measure          Diagnose
Run batch 2                          ↓
   ↓                                Fix
Run batch 3                          ↓
   ↓                                Test
...                                 ↓
Collect metrics                     Deploy

Never paused. Always improving.
```

### Monitoring Framework (New in Phase 2)

#### Metrics to Collect
```json
{
  "batch_id": 47,
  "total_items": 8,
  "stages": 4,
  "parallelism_achieved": 3.2,
  "total_duration": 487,
  "token_usage": 24500,
  "cost": 0.42,
  "conflicts": {
    "file_conflicts": 0,
    "dependency_failures": 0,
    "circular_deps": 0
  },
  "errors": [
    {
      "work_item": "PRP-47.2.1",
      "type": "timeout",
      "duration": 3671,
      "timeout_limit": 3600
    }
  ]
}
```

#### Logging Approach
- Write batch metrics JSON to `.ce/tmp/batch-metrics-{batch_id}.json`
- Archive to `.ce/completed-batches/` for analysis
- Simple Python script to analyze trends

#### Diagnostics
```bash
# After each batch
.ce/scripts/analyze-batch.py batch-47.json

# Sample output:
✓ Batch 47: 8 PRPs, 4 stages, 3.2× parallelism
⚠ PRP-47.2.1 timeout (3671s > 3600s limit) - increase to 4000s
ℹ Avg tokens/PRP: 3062 - within budget
ℹ Cost: $0.42 - track trending

# Run analysis on all recent batches
.ce/scripts/trend-analysis.py --weeks 2
→ No critical issues, 1 timeout edge case
```

### Week 4: Initial Production + Diagnostics Setup

**Goal**: Run real batches, setup monitoring

**Tasks**:
- [ ] Run batch 1 with MVP (3-4 PRPs)
  - Document any issues
  - Measure duration, tokens, cost
  - Note any manual conflict resolutions

- [ ] Create metrics collection script (2h)
  - Write JSON after each batch
  - Archive completed batches

- [ ] Create analysis script (2h)
  - Identify bottlenecks
  - Detect patterns

- [ ] Run batch 2 with MVP (4-5 PRPs)
  - Validate metrics collection
  - Check for patterns

**Checkpoint**: Metrics collection working, 2 batches analyzed

### Week 5: Diagnose & Fix (Based on Real Data)

**Goal**: Fix issues found in real usage

**Possible Issues** (examples):
```
Issue 1: Timeout too aggressive
  Data: 3 subagents hit 60m limit out of 20 runs
  Fix: Increase timeout to 90m for executor subagents
  Effort: 1h
  Impact: Eliminate failure cases

Issue 2: File conflicts frequent
  Data: 2/8 batches had file conflicts, manual resolution took 30m total
  Fix: Add simple conflict detection + merge strategy
  Effort: 4h
  Impact: Automate rare manual work

Issue 3: Token usage trending high
  Data: Batch 3 used 35k tokens, Batch 1 used 24k (45% increase)
  Fix: Implement shared context optimization
  Effort: 6h
  Impact: 40% token reduction

Issue 4: Circular dependency edge case
  Data: 1 batch caught by topological sort, user had to re-plan
  Fix: Add better error message showing cycle path
  Effort: 1h
  Impact: Improve UX
```

**Tasks** (based on actual issues):
- [ ] Fix top 2-3 issues found in weeks 4 data
- [ ] Test each fix with a small batch
- [ ] Deploy + monitor

**Checkpoint**: Real issues fixed, improvements deployed

### Week 6+: Continuous Improvement

**Goal**: Long-term stability and optimization

**Ongoing**:
- [ ] Monitor every batch (weekly analysis)
- [ ] Fix issues as they appear (rapid iteration)
- [ ] Optimize based on trends (40-60% token reduction target)
- [ ] Add features as needed (schemas, dashboard, etc.)

**Examples of Phase 2 Optimizations** (Do only if needed):

| Enhancement | When | Effort | Impact |
|-------------|------|--------|--------|
| Shared context opt | Tokens >30k/batch | 6h | 40% reduction |
| JSON schemas | Integration bugs > 2 | 8h | Prevent bugs |
| File conflict auto-merge | Conflicts > 2/batch | 4h | Reduce manual work |
| Monitoring dashboard | Team requests | 6h | Better visibility |
| Inter-PRP consistency | Conflicts hard to find | 8h | Catch issues early |

**Decision Rule**: Only implement if:
- Actual data shows it's a bottleneck
- Team confirms it's a pain point
- ROI is clear (e.g., saves 2+ hours per week)

---

## Timeline: MVP → Prod

```
Week 1        Week 2              Week 3           Week 4-6+
─────────     ──────────          ──────           ────────────
Foundation    Refactor 2 cmds     Finish + Ship    Production
              + Integration                        + Improve
                                  ↓
                                  LIVE
                                  ↓
                              Use + Monitor
                                  ↓
                              Diagnose Issues
                                  ↓
                              Fix on the way
```

---

## Comparison: MVP vs Prod

| Aspect | MVP (Phase 1) | Prod (Phase 2+) |
|--------|---|---|
| **Commands** | All 4 working | All 4 hardened |
| **Monitoring** | Print-based | Metrics + analysis |
| **Conflicts** | Manual resolution | Auto-detected + suggested |
| **Optimization** | None | Based on real data |
| **Schemas** | No | Yes (if bugs found) |
| **Parallelism** | 3-4× typical | Measured + optimized |
| **Token usage** | ~30k/batch | ~18k/batch (goal) |
| **Cost** | ~$0.60/batch | ~$0.35/batch (goal) |
| **Timeout** | Fixed 60m | Tuned per subagent |

---

## Decision Framework: MVP vs Prod Features

**For Phase 1 (MVP): Include?**
```
Question: Is this essential to ship working framework?
  Yes → Include
  No  → Phase 2
```

**For Phase 2: Add now or wait?**
```
Question: Does real usage data show we need this?
  Yes → Fix/Add
  No  → Don't waste time (YAGNI)
```

---

## Risk Mitigation: MVP

| Risk | Mitigation |
|------|-----------|
| **Commands break in production** | Comprehensive testing in Phase 1 |
| **User can't resolve conflicts** | Clear error messages + manual option always available |
| **Timeouts wrong** | Start conservative (60m), increase in Phase 2 if needed |
| **Heartbeat polling misses failures** | Double threshold (2 failed polls = kill) |

---

## Success Metrics

### Phase 1 (MVP)
- ✅ All 4 commands working end-to-end
- ✅ Code duplication <10%
- ✅ 3-week delivery
- ✅ Ready for production
- ✅ Basic docs complete

### Phase 2 (Prod)
- ✅ 10+ batches run successfully
- ✅ Metrics collected + analyzed
- ✅ Top issues fixed
- ✅ 40%+ token reduction (vs Phase 1)
- ✅ Manual conflict resolution <1% of time

---

## Go-Live Checklist (End of Week 3)

**Code**:
- [ ] All framework files in place
- [ ] All 4 commands refactored & tested
- [ ] Unit tests passing (>90% coverage)
- [ ] Integration tests passing

**Documentation**:
- [ ] Usage guide (how to run each command)
- [ ] Architecture overview
- [ ] Troubleshooting guide
- [ ] Limitations + Phase 2 roadmap

**Testing**:
- [ ] Manual test: Batch of 6 PRPs
- [ ] Stress test: Large plan (10+ phases)
- [ ] Error handling: Timeout, conflict, circular dep

**Production Readiness**:
- [ ] Metrics collection script ready
- [ ] Analysis script ready
- [ ] Team trained on new commands
- [ ] Fallback plan (revert to old commands if needed)

---

## Phase 2: Real-World Scenarios

### Scenario 1: Everything Works
**What**: Batches run smoothly, metrics look good
**Action**: Continue monitoring, look for optimization opportunities
**Timeline**: Weeks 4-8

### Scenario 2: Occasional Timeouts
**What**: 1-2 subagents hit 60m limit
**Action**: Collect data on affected PRPs, increase timeout, test
**Timeline**: Week 5, 1-2h fix

### Scenario 3: Frequent File Conflicts
**What**: 3+ batches have file conflicts, manual resolution needed
**Action**: Implement auto-detect + merge strategy (Phase 2 enhancement)
**Timeline**: Week 5-6, 4h implementation

### Scenario 4: Token Usage High
**What**: Batches averaging 35k tokens (vs 24k goal)
**Action**: Profile, implement shared context optimization
**Timeline**: Week 6, 6h implementation, 40% reduction

---

## Files Modified/Created

### Phase 1 (New)
```
.claude/orchestrators/base-orchestrator.md
.claude/subagents/generator-subagent.md
.claude/subagents/executor-subagent.md
.claude/subagents/reviewer-subagent.md
.claude/subagents/context-updater-subagent.md
.ce/orchestration/dependency_analyzer.py
PRPs/feature-requests/PRP-47-USAGE-GUIDE.md
```

### Phase 2 (New)
```
.ce/scripts/analyze-batch.py
.ce/scripts/trend-analysis.py
.ce/orchestration/conflict_detector.py (if needed)
.ce/orchestration/shared_context_optimizer.py (if needed)
```

### Phase 1 (Refactored)
```
.claude/commands/batch-gen-prp.md
.claude/commands/batch-exe-prp.md
.claude/commands/batch-peer-review.md
.claude/commands/batch-update-context.md
```

---

## Related Documents

- **PRP-47-SUBAGENTS-EXECUTION-INITIAL-PLAN.md** - Original comprehensive (reference)
- **PRP-47-SUBAGENTS-EXECUTION-KISS-INITIAL-PLAN.md** - Simple MVP (Phase 1 base)
- **PRP-47-REVIEW-COMPARISON.md** - Detailed analysis
- **PRP-47-DECISION-SUMMARY.md** - Original recommendation

---

## Sign-Off

**Document**: PRP-47-TWO-PHASE (MVP → Prod)
**Version**: 1.0
**Status**: Ready for implementation
**Timeline**: Phase 1: 3 weeks | Phase 2: Ongoing (4-6+ weeks)
**Recommendation**: Start Phase 1 immediately, begin Phase 2 in parallel with Phase 1 Week 3

