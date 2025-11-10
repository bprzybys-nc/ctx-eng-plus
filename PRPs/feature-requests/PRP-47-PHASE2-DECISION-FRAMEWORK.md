---
prp_id: PRP-47-PHASE2-DECISION-FRAMEWORK
title: Phase 2 Decision Framework - Data-Driven Prioritization
status: completed
type: documentation
complexity: low
priority: high
batch_id: 47
---

# Phase 2 Decision Framework

## Overview

Data-driven approach to prioritizing Phase 2 improvements based on production metrics.

## Prioritization Criteria

### 1. Impact (High/Medium/Low)

**High Impact**: >50% improvement potential or critical bottleneck
**Medium Impact**: 20-50% improvement potential
**Low Impact**: <20% improvement potential

**Measured by**:
- Duration reduction (seconds saved per batch)
- Token reduction (tokens saved per batch)
- Success rate improvement (% increase)

### 2. Effort (1-5 scale)

**1 point**: <4 hours (quick fix)
**2 points**: 4-8 hours (small feature)
**3 points**: 8-16 hours (medium feature)
**4 points**: 16-32 hours (large feature)
**5 points**: >32 hours (major rework)

### 3. Priority Score

Priority Score = Impact × (6 - Effort)

**High Priority**: Score ≥ 10
**Medium Priority**: Score 5-9
**Low Priority**: Score < 5

## Phase 2 Candidate Features

### Candidate 1: LLM Caching

**Impact**: High (50%+ token reduction for repeated calls)
**Effort**: 2 (8 hours)
**Priority Score**: High × 4 = 12

**Metrics Trigger**: Token usage >100k per batch

**Description**: Cache LLM responses for identical prompts to reduce token consumption and cost. Particularly effective for review operations where context is reused.

### Candidate 2: Subagent Result Caching

**Impact**: Medium (30% duration reduction for repeated operations)
**Effort**: 3 (12 hours)
**Priority Score**: Medium × 3 = 9

**Metrics Trigger**: Repeated operations (same input/output)

**Description**: Cache subagent execution results to avoid re-running identical PRPs. Enables resume-from-checkpoint capability for large batches.

### Candidate 3: Advanced Error Recovery

**Impact**: High (improve success rate from 85% to 95%+)
**Effort**: 3 (16 hours)
**Priority Score**: High × 3 = 12

**Metrics Trigger**: Success rate <90%

**Description**: Implement intelligent error handling with automatic retry, fallback models, and graceful degradation. Reduces manual intervention.

### Candidate 4: Streaming Progress Updates

**Impact**: Low (UX improvement, no performance gain)
**Effort**: 2 (8 hours)
**Priority Score**: Low × 4 = 4

**Metrics Trigger**: User feedback requests

**Description**: Real-time progress reporting during batch operations instead of waiting for final report. Improves user experience.

### Candidate 5: Multi-Model Orchestration

**Impact**: High (cost reduction 80%+ by using Haiku more)
**Effort**: 4 (24 hours)
**Priority Score**: High × 2 = 8

**Metrics Trigger**: Cost >$1 per batch

**Description**: Intelligently route operations to cheaper models (Haiku for generation, Sonnet for review) instead of always using Sonnet. Largest cost savings potential.

## Decision Process

### Step 1: Collect Metrics (Weeks 4-6)

Run production batches with metrics collection:
- Minimum 10 batches across all operations
- Mix of small (2-3 PRPs) and large (8-10 PRPs) batches
- Capture all metrics (duration, tokens, success rate, errors)

**Implementation**:
```bash
# After each batch operation
python .ce/scripts/analyze-batch.py --batch <ID> --all
```

### Step 2: Analyze Trends (Week 6)

Run trend-analysis.py:
```bash
python .ce/scripts/trend-analysis.py --all
```

Review report:
- Identify bottlenecks (long duration, high failure rate, high cost)
- Calculate improvement potential (max-mean duration, success rate gap)
- Prioritize by impact

### Step 3: Score Candidates (Week 7)

For each bottleneck or improvement opportunity:
1. Match to candidate feature (or create new candidate)
2. Estimate impact (based on metrics)
3. Estimate effort (based on complexity)
4. Calculate priority score
5. Sort by priority score

### Step 4: Plan Phase 2 (Week 7)

Select top 3-5 high-priority features:
- Total effort <80 hours (2 weeks of work)
- Mix of quick wins (effort 1-2) and high-impact features
- Create PRPs for selected features
- Execute as Phase 2 batch

## Example Decision

**Metrics from Week 4-6**:
- batch-exe-prp: Mean duration 1800s (30 min), 85% success rate
- batch-gen-prp: Mean token usage 150k, cost $0.75 per batch
- batch-peer-review: Mean duration 300s (5 min), 95% success rate

**Analysis**:
- Bottleneck 1: batch-exe-prp duration (30 min mean, 10 min min)
  - Improvement potential: 20 min (66%)
  - Match to: Subagent Result Caching (Candidate 2)

- Bottleneck 2: batch-exe-prp success rate (85%)
  - Improvement potential: 10% (to 95%)
  - Match to: Advanced Error Recovery (Candidate 3)

- Opportunity: batch-gen-prp cost ($0.75 per batch)
  - Improvement potential: $0.60 (80%)
  - Match to: Multi-Model Orchestration (Candidate 5)

**Priority Scores**:
1. Advanced Error Recovery: 12 (high impact, medium effort)
2. Subagent Result Caching: 9 (medium impact, medium effort)
3. Multi-Model Orchestration: 8 (high impact, high effort)

**Phase 2 Plan**: Execute Candidates 3, 2 in order (total 28 hours)

## Metrics Collection Checklist

- [ ] analyze-batch.py script working
- [ ] trend-analysis.py script working
- [ ] Run 10+ production batches (mix of sizes)
- [ ] Collect metrics for all operations (gen, exe, review, context-update)
- [ ] Generate trend analysis report
- [ ] Review report with team
- [ ] Score candidate features
- [ ] Create Phase 2 plan

## Acceptance Criteria

1. **Metrics Collection**
   - analyze-batch.py works for all 4 operations (gen, exe, review, context-update)
   - Metrics saved in standard JSON format
   - Schema validation passes

2. **Trend Analysis**
   - trend-analysis.py identifies bottlenecks correctly
   - Report includes duration, success rate, recommendations
   - Handles edge cases (no metrics, single batch)

3. **Decision Framework**
   - Phase 2 candidate features documented
   - Prioritization criteria defined
   - Decision process clear (4 steps)

4. **Production Ready**
   - Scripts integrated into batch commands
   - Error handling robust
   - Documentation complete

## Files Created

- `.ce/schemas/batch-metrics.json` - Metrics schema with JSON-Schema
- `.ce/scripts/analyze-batch.py` - Extract metrics from completed batches
- `.ce/scripts/trend-analysis.py` - Identify patterns and bottlenecks
- `.ce/completed-batches/` - Directory for batch data archival (auto-created)
- `PRPs/feature-requests/PRP-47-PHASE2-DECISION-FRAMEWORK.md` - This file

## Testing Standards

### Unit Tests

```python
# Test metrics schema validation
def test_metrics_schema_valid():
    schema = json.loads(Path(".ce/schemas/batch-metrics.json").read_text())
    # Test with sample metrics
    assert validate(sample_metrics, schema)

# Test duration calculation
def test_calculate_duration():
    analyzer = BatchAnalyzer("47")
    duration = analyzer._calculate_duration(first_commit, last_commit)
    assert duration > 0
```

### Integration Tests

```bash
# Test with real batch
python .ce/scripts/analyze-batch.py --batch 47 --all
python .ce/scripts/trend-analysis.py --recent 1

# Verify outputs
test -f .ce/completed-batches/batch-47-generate.json
test -f .ce/trend-analysis-report.md
```

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Metrics collection fails silently | No data for Phase 2 decisions | Add logging, error handling, verify metrics files after each batch |
| Git log parsing unreliable | Inaccurate duration metrics | Test with various commit patterns, add fallback to timestamp files |
| Trend analysis identifies wrong bottlenecks | Phase 2 optimizes wrong areas | Manual review of metrics, validate with user feedback |
| Decision framework too rigid | Miss important improvements | Allow flexibility for critical bugs or user requests |
| Metrics overhead slows batches | Performance regression | Run metrics collection async, minimize git log queries |

## Dependencies

- **Phase 1 completion**: Requires PRP-47.1.1 through PRP-47.6.1 to be completed
- **Python dateutil**: Used for timestamp parsing (uv add python-dateutil)

## Next Steps

Phase 2 features will be determined based on metrics collected in weeks 4-6. Expected Phase 2 roadmap:

1. **Advanced Error Recovery** (if success rate <90%)
2. **Subagent Result Caching** (if duration >15 min)
3. **Multi-Model Orchestration** (if cost >$0.75 per batch)

## Notes

- This document bridges Phase 1 and Phase 2
- Metrics collection starts immediately after Phase 1 deployment
- Phase 2 features TBD based on production data (Weeks 4-7)
- Decision framework flexible (adjust based on learnings)
- Scripts use stdlib + dateutil (minimal dependencies)
