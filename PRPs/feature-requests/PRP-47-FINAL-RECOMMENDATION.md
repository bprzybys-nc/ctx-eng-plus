---
title: "PRP-47: Final Recommendation - Two-Phase MVP→Prod Approach"
type: decision
created: "2025-11-10"
---

# PRP-47: Final Recommendation

## Executive Summary

**Recommendation**: Implement **PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md**

This approach:
- ✅ Ships working framework in 3 weeks (MVP)
- ✅ Uses it immediately in production
- ✅ Diagnoses issues + fixes in parallel (Phase 2)
- ✅ Avoids gold-plating (build what's needed now)
- ✅ Improves based on real data (not predictions)

---

## Evolution: Three Versions

### Version 1: Original (PRP-47-SUBAGENTS-EXECUTION-INITIAL-PLAN.md)
**Scope**: Comprehensive production design
**Timeline**: 6 weeks, 40 hours
**Best for**: Reference architecture, long-term planning
**Status**: Over-engineered for current needs

### Version 2: KISS (PRP-47-SUBAGENTS-EXECUTION-KISS-INITIAL-PLAN.md)
**Scope**: Minimal MVP (Phase 1 only)
**Timeline**: 3 weeks, 20 hours
**Best for**: Fast shipping
**Status**: Good MVP, but lacks production monitoring plan

### Version 3: Two-Phase ⭐ **RECOMMENDED** (PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md)
**Scope**: MVP + Prod phases with parallel improvement
**Timeline**: 3 weeks (MVP) + ongoing (Prod)
**Best for**: Ship fast + improve continuously
**Status**: Most pragmatic, realistic

---

## Three-Version Comparison

| Aspect | Original | KISS | Two-Phase |
|--------|----------|------|-----------|
| **MVP Delivery** | 6 weeks | 3 weeks | 3 weeks ✅ |
| **Production Ready** | Yes | Yes (basic) | Yes + monitoring ✅ |
| **Phase 2 Plan** | Vague | None | Clear ✅ |
| **Optimization Roadmap** | Pre-planned | None | Data-driven ✅ |
| **Risk Mitigation** | Comprehensive | Basic | Adaptive ✅ |
| **Complexity** | High | Low | Medium ✅ |
| **Pragmatism** | 3/5 | 5/5 | 5/5 ✅ |
| **Realistic** | 2/5 | 5/5 | 5/5 ✅ |

---

## Why Two-Phase Beats KISS

**KISS Limitations**:
- ❌ No plan for monitoring in production
- ❌ No framework for identifying issues
- ❌ No guidance on when/how to optimize
- ❌ "Ship and hope" approach
- ❌ If issues appear → ad-hoc firefighting

**Two-Phase Advantages**:
- ✅ MVP + Prod = clear phases
- ✅ Built-in monitoring from Week 4
- ✅ Data-driven optimization decisions
- ✅ Parallel improvement (use + fix)
- ✅ Real issues guide Phase 2 work
- ✅ NO wasted effort on features not needed

---

## Two-Phase Timeline

```
PHASE 1: MVP (Weeks 1-3) - Build & Ship
│
├─ Week 1: Foundation (orchestrator, subagents, dependency analyzer)
├─ Week 2: Refactor /batch-gen-prp & /batch-exe-prp + test
├─ Week 3: Refactor /batch-peer-review & /batch-update-context + ship
│
└─ Deliverable: Working batch commands, ready for production
   Cost: 20 hours | Code: ~730 lines | Files: 6

                        ↓ DEPLOY ↓
                    (End of Week 3)

PHASE 2: Prod (Weeks 4-6+) - Monitor & Improve
│
├─ Week 4: Run production batches, setup metrics collection
│         (Parallel: Run batches 1-2 with MVP)
│
├─ Week 5: Diagnose issues from real data
│         (Parallel: Run batch 3, fix top 2-3 issues)
│
├─ Week 6: Deploy fixes, optimize based on metrics
│         (Parallel: Run batch 4, deploy improvements)
│
└─ Ongoing: Continuous monitoring + iterative improvements
   Cost: Unknown (data-driven)
   Focus: Real bottlenecks only (no YAGNI waste)
```

---

## Key Principle: Use → Monitor → Fix → Deploy

Not: Plan → Build → Deploy → Hope it works

### KISS Approach (Ship & Forget)
```
Build MVP (Week 3)
    ↓
Deploy (Week 4)
    ↓
Hope it works... (Week 5+)
    ↓
Issues appear... reactive firefighting
```

### Two-Phase Approach (Ship & Improve)
```
Build MVP (Week 3)
    ↓
Deploy (Week 4)
    ↓
Monitor + Diagnose (Week 4-5)
    ↓
Fix real issues (Week 5-6)
    ↓
Continuous improvement (Week 6+)
```

---

## Phase 1: MVP Scope (Week 1-3)

**Includes**:
- ✅ Orchestrator (6 phases, simple)
- ✅ Four subagents (generator, executor, reviewer, context-updater)
- ✅ File-based coordination (specs, heartbeats, results)
- ✅ Dependency analysis (topological sort, cycle detection)
- ✅ All 4 batch commands refactored
- ✅ Print-based monitoring
- ✅ Basic documentation

**Excludes** (Phase 2):
- ❌ JSON schemas
- ❌ Config file
- ❌ Shared context optimization
- ❌ Advanced monitoring dashboard
- ❌ Inter-PRP consistency checks
- ❌ Auto-merge conflict resolution

**Why exclude**: Not needed for MVP. Phase 2 adds them if data shows bottleneck.

---

## Phase 2: Prod Approach (Week 4+)

**Framework**:
1. **Run batches** with MVP (production usage)
2. **Collect metrics** (duration, tokens, cost, errors)
3. **Analyze trends** (identify bottlenecks)
4. **Fix issues** (data-driven priorities)
5. **Deploy improvements** (continuous iteration)

**Example Issues & Fixes**:

| Issue | Data | Fix | Effort | Impact |
|-------|------|-----|--------|--------|
| Timeout failures | 2/10 batches timeout | Increase to 90m | 1h | Eliminate failures |
| Manual conflicts | 3/10 batches need manual merge | Add conflict detection | 4h | Automate rare work |
| High token use | Trending 35k → 40k | Shared context opt | 6h | 40% reduction |
| Poor UX | Users miss error messages | Better diagnostics | 2h | Faster resolution |

**Decision Rule**: Only fix if real data shows it's a problem.

---

## Deliverables Comparison

### Phase 1 (MVP) - End of Week 3

| Item | Type | Size | Status |
|------|------|------|--------|
| Orchestrator | Template | 300 lines | Done ✓ |
| 4 Subagents | Templates | 430 lines | Done ✓ |
| Dependency analyzer | Code | 100 lines | Done ✓ |
| 4 Batch commands | Refactored | 50 lines each | Done ✓ |
| Unit tests | Code | 200 lines | Done ✓ |
| Integration tests | Code | 150 lines | Done ✓ |
| Docs | Markdown | 500 lines | Done ✓ |
| **Total** | | ~2,000 lines | Ready for production |

### Phase 2 (Prod) - Week 4-6+

| Item | Type | When | Example |
|------|------|------|---------|
| Metrics collection | Code | Week 4 | batch-metrics-{id}.json |
| Trend analysis | Code | Week 4 | Identify bottlenecks |
| Issue fixes | Code | Week 5-6 | Based on real data |
| Optimizations | Code | Week 6+ | Shared context, schemas |
| Documentation | Markdown | Ongoing | Update as you learn |

**No pre-planned components. Everything driven by what you observe.**

---

## Success Definition

### Phase 1: MVP Success
- ✅ All 4 batch commands working end-to-end
- ✅ Code duplication <10% (from 30%)
- ✅ Ready for production use
- ✅ Shipped in 3 weeks
- ✅ Basic docs complete

### Phase 2: Prod Success
- ✅ 10+ batches run without critical failures
- ✅ Top issues identified + fixed
- ✅ Token usage optimized (target: 40% reduction)
- ✅ Manual conflict resolution <1% of time
- ✅ Team confident in framework
- ✅ Continuous improvement culture established

---

## Implementation Checklist

### Week 1: Foundation
- [ ] Write orchestrator template
- [ ] Write 4 subagent templates
- [ ] Implement dependency_analyzer.py
- [ ] Unit tests passing
- [ ] Checkpoint: Framework ready

### Week 2: Refactoring Phase 1
- [ ] Refactor /batch-gen-prp
- [ ] Refactor /batch-exe-prp
- [ ] Integration test (gen + exe)
- [ ] Checkpoint: 2 commands working

### Week 3: Refactoring Phase 2 + Ship
- [ ] Refactor /batch-peer-review
- [ ] Refactor /batch-update-context
- [ ] Full integration test
- [ ] Write documentation
- [ ] Checkpoint: Ready for production

### Week 4: Monitor (Phase 2)
- [ ] Setup metrics collection script
- [ ] Run batch 1 (3-4 PRPs)
- [ ] Analyze batch 1 results
- [ ] Run batch 2 (4-5 PRPs)
- [ ] Identify patterns

### Week 5: Diagnose & Fix (Phase 2)
- [ ] Review metrics from batches 1-2
- [ ] Identify top 2-3 issues
- [ ] Fix issues based on data
- [ ] Test fixes with batch 3
- [ ] Deploy fixes

### Week 6+: Continuous (Phase 2)
- [ ] Monitor all batches
- [ ] Add features as needed
- [ ] Optimize based on trends
- [ ] No pre-planned work (data-driven)

---

## Reading Guide

**For Quick Understanding**:
1. This document (5 min)
2. PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md (15 min)
3. Done. Start implementing.

**For Complete Picture**:
1. This document (5 min)
2. PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md (15 min)
3. PRP-47-REVIEW-COMPARISON.md (10 min) - understand trade-offs
4. PRP-47-SUBAGENTS-EXECUTION-INITIAL-PLAN.md (30 min) - reference
5. Start Phase 1 implementation

---

## Q&A

**Q: Why not just use the Original comprehensive plan?**
A: It's over-engineered for current needs. 6 weeks vs 3 weeks. Build what's needed now, add later if data shows it's needed.

**Q: What if Phase 2 features are really important?**
A: They become important only when real usage reveals bottlenecks. Phase 2 monitors for that. If they're important, data will show it in Week 4-5.

**Q: What if something breaks in production during Phase 1?**
A: Fallback to old commands. But comprehensive Phase 1 testing (unit + integration) should prevent this. Phase 2 monitoring catches issues early.

**Q: How long is Phase 2?**
A: Indefinite. It's the operational phase. You use + monitor + improve continuously. No end date.

**Q: Can we run Phase 1 faster?**
A: Possibly 2.5 weeks if team is focused. Not recommended < 2 weeks (quality suffers).

**Q: What if Phase 2 issues need 2+ weeks to fix?**
A: Possible for complex issues (e.g., shared context optimization). Document as technical debt, schedule for future sprint. MVP keeps working while you fix.

---

## Recommendation: Ship Two-Phase Version

**Next Step**: Start Phase 1 Week 1
```
1. Read PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md (15 min)
2. Create framework files (.claude/orchestrators/, .claude/subagents/)
3. Implement dependency_analyzer.py
4. Week 2: Refactor batch commands
5. Week 3: Ship
6. Week 4+: Monitor + improve based on real data
```

**Expected Outcome (Week 3)**:
- Working unified framework
- All 4 batch commands refactored
- Ready for production
- Clear roadmap for Phase 2 improvements
- No gold-plating, no YAGNI waste

---

## Documents Summary

| Document | Type | Use Case | Status |
|----------|------|----------|--------|
| **PRP-47-SUBAGENTS-EXECUTION-INITIAL-PLAN.md** | Comprehensive | Long-term reference | ✓ Approved |
| **PRP-47-SUBAGENTS-EXECUTION-KISS-INITIAL-PLAN.md** | MVP only | Phase 1 base | ✓ Approved |
| **PRP-47-SUBAGENTS-EXECUTION-TWOPHASE-PLAN.md** | MVP + Prod | **IMPLEMENT THIS** | ✓ Approved ⭐ |
| **PRP-47-REVIEW-COMPARISON.md** | Analysis | Decision support | ✓ Reference |
| **PRP-47-DECISION-SUMMARY.md** | Summary | Quick reference | ✓ Reference |
| **PRP-47-FINAL-RECOMMENDATION.md** | Decision | This document | ✓ Final |

---

## Sign-Off

**Framework**: Unified Batch Command Framework
**Architecture**: Sonnet Orchestrator + Haiku Subagents
**Approach**: Two-Phase (MVP → Prod)
**Phase 1**: 3 weeks, 20 hours
**Phase 2**: Ongoing, data-driven
**Timeline**: Start Week 1
**Status**: Ready for implementation

