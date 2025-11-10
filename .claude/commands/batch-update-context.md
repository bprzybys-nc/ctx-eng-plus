# Batch Update Context

Synchronize executed PRP status into project context with parallel drift analysis.

## Usage

```bash
/batch-update-context --batch <id>
/batch-update-context --prps <prp-ids>
```

## Arguments

- `--batch <id>`: Update all PRPs in batch ID
- `--prps <ids>`: Comma-separated PRP IDs (e.g., "PRP-47.1.1,PRP-47.2.1")

## What it does

Orchestrated batch context synchronization:

1. **Parse & Validate**: Load PRP files, verify existence
2. **Dependency Analysis**: Check for independent updates (no staging needed)
3. **Spawn Context Updaters**: Launch parallel subagents (one per PRP)
4. **Monitor Progress**: Poll heartbeat files, track completion
5. **Aggregate Results**: Collect drift scores, categorize quality
6. **Generate Report**: Per-PRP status, drift summary, actionable insights

## Orchestration Pattern

Follows **base-orchestrator.md** 6-phase coordination:
- All PRPs updated **in parallel** (no sequential bottleneck)
- Each subagent handles one PRP independently
- Heartbeat monitoring with 30s polling
- Aggregated drift score summary

## Subagent Integration

Uses **context-updater-subagent.md** for each PRP:
- Parses PRP + git history
- Extracts implementation evidence (files, commits, drift)
- Updates PRP status (pending → completed)
- Calculates drift score (0-100%, categorized)
- Generates completion metadata

## Drift Score Summary

Per-PRP drift categories:
- **Healthy** (<5%): Execution matched plan very closely
- **Good** (5-15%): Minor intentional deviations
- **Acceptable** (15-30%): Some scope creep, managed
- **Warning** (30-50%): Significant divergence from plan
- **Critical** (>50%): Execution heavily deviated

## Example Report

```
Batch 47 Context Update Complete

Total PRPs: 5
Updated: 5
No Changes: 0
Failed: 0

Drift Score Summary:
  Healthy (<5%): 3 PRPs
  Good (5-15%): 2 PRPs
  Critical (>50%): 0 PRPs

Details:
  PRP-47.1.1: planning → completed (drift: 3%, EXCELLENT)
  PRP-47.2.1: planning → completed (drift: 8%, EXCELLENT)
  PRP-47.3.1: in_progress → completed (drift: 12%, GOOD)
  [... 2 more ...]

Next Steps:
  1. Review any warnings/critical PRPs
  2. Update specs if scope intentionally changed
  3. Run /batch-peer-review if significant divergence
```

## Performance

- Sequential updates: 5 PRPs ≈ 15 minutes
- Parallel updates: 5 PRPs ≈ 3 minutes (80% speedup)
- Drift calculation included in parallel execution

## Related Commands

- `/update-context` - Update single PRP
- `/batch-gen-prp` - Generate batch of PRPs
- `/batch-exe-prp` - Execute batch of PRPs
- `/batch-peer-review` - Review executed PRPs

## Notes

- Updates are **fully parallel** (all PRPs simultaneously)
- No staging needed (all updates independent)
- Drift score measures plan vs implementation divergence
- Critical drift (>15%) indicates need for PRP spec review
- Time savings: ~60-70% vs sequential updates
