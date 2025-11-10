# /batch-peer-review - Orchestrated Batch PRP Peer Review

Performs comprehensive peer review of ANY batch of PRPs using orchestrator framework.

**Architecture**: Base orchestrator coordinates parallel reviewer subagents with shared context optimization.

## Usage

```bash
/batch-peer-review --batch <batch-id> [--exe] [--fast|--quality]
/batch-peer-review --prps PRP-34.1.1,PRP-34.2.1,PRP-34.2.2

# Examples:
/batch-peer-review --batch 34                # Review batch 34 (document)
/batch-peer-review --batch 34 --exe          # Review execution results
/batch-peer-review --batch 34 --fast         # Structural only (Haiku)
/batch-peer-review --batch 34 --quality      # Deep semantic (Sonnet)
```

## What It Does

1. **Parse & Validate**: Scan `PRPs/feature-requests/PRP-{batch_id}.*.md`
2. **Load Shared Context**: Read CLAUDE.md, .ce/RULES.md once (70%+ token savings)
3. **Stage PRPs**: Topological sort by dependencies
4. **Spawn Reviewers**: All-parallel via reviewer subagent (base orchestrator Phase 3)
5. **Monitor**: Heartbeat files every 30s (Phase 4)
6. **Aggregate**: Collect reviews + inter-PRP consistency checks (Phase 5)
7. **Report**: Summary + recommendations (Phase 6)

## Orchestration Pattern

This command follows the base orchestrator template:
{{include .claude/orchestrators/base-orchestrator.md}}

### Command-Specific Adaptations

- **Subagent Type**: reviewer-subagent
- **Input**: PRP files + shared context
- **Output**: Review reports (JSON) + aggregated report (Markdown)
- **Optimization**: Shared context passed to all subagents (ONE read, N uses)
- **Parallel**: All PRPs in each stage reviewed simultaneously

## Reviewer Subagent Integration

This command delegates review logic to:
{{include .claude/subagents/reviewer-subagent.md}}

### Subagent Input Spec

```json
{
  "batch_id": 34,
  "prp_id": "PRP-34.2.1",
  "prp_path": "/absolute/path/to/PRP-34.2.1.md",
  "review_mode": "document|execution",
  "shared_context": {
    "claude_md": "...",
    "rules_md": "...",
    "master_plan": "... (if exists)",
    "batch_prps": ["PRP-34.1.1", "PRP-34.2.1", ...]
  }
}
```

### Shared Context Optimization

**Before spawning reviewers, read shared context ONCE**:

```python
shared_context = {
    "claude_md": Read("CLAUDE.md"),           # ~5-15k tokens
    "rules_md": Read(".ce/RULES.md"),         # ~3-5k tokens
    "master_plan": Read(f"PRPs/feature-requests/PRP-{batch_id}-INITIAL.md") if exists,  # ~5-15k
}

# Total: ~10-30k tokens (read once, passed to all N subagents)
# Savings: 20k × (N-1) tokens = massive reduction for batches
```

**Token Savings Example**:
- 3 PRPs: 40k tokens saved (20k × 2)
- 5 PRPs: 80k tokens saved (20k × 4)
- 10 PRPs: 180k tokens saved (20k × 9)

## Review Criteria (Delegated to Subagent)

**Structural Review** (Haiku):
- YAML frontmatter complete
- Main sections present (Problem, Solution, Implementation)
- Implementation subsections (Steps, Gates, Testing, Risks)
- Gate count ≥3
- Complexity/hours alignment

**Semantic Review** (Sonnet):
- Alignment with master plan (if exists)
- Dependencies accurate
- Architecture consistency
- Rules compliance
- No contradictions with sibling PRPs
- Effort estimates reasonable
- Test coverage adequate

**Inter-PRP Consistency**:
- File conflict detection
- Circular dependency checks
- Total hours estimation
- Terminology consistency

See reviewer-subagent.md for complete check details.

## Execution Review Mode (--exe)

When flag `--exe` provided, reviews IMPLEMENTATION against PRP requirements:
- Implementation matches PRP spec
- Code quality meets standards
- Acceptance criteria satisfied
- No side effects
- Edge cases handled
- Tests passing

See reviewer-subagent.md Step 4-5 for execution review checks.

## Workflow

### Phase 1: Parse & Validate

User invokes: `/batch-peer-review --batch 34`

Coordinator parses batch:
```python
batch_prps = glob("PRPs/feature-requests/PRP-34.*.md")  # All PRPs in batch
validate_all_readable()  # Verify files accessible
```

### Phase 2: Dependency Analysis

Topological sort to assign stages:
```python
stages = assign_stages(batch_prps)
# Example output:
# Stage 1: [PRP-34.1.1]
# Stage 2: [PRP-34.2.1, PRP-34.2.2, PRP-34.2.3, ...] (parallel)
# Stage 3: [PRP-34.3.1, PRP-34.3.2] (parallel)
# Stage 4: [PRP-34.4.1]
```

### Phase 3: Spawn Reviewers (All Parallel)

```python
# Read shared context ONCE
shared_context = prepare_shared_context(batch_id)

# Spawn all reviewers (via base orchestrator Phase 3)
for prp_id in all_batch_prps:
    Task(
        description=f"Review PRP-{prp_id}",
        prompt=reviewer_subagent_prompt(prp_id, shared_context),
        subagent_type="general-purpose"
    )
```

### Phase 4: Monitor (30s Polling)

Heartbeat files: `.ce/orchestration/tasks/batch-{batch_id}/PRP-{prp_id}.hb`

```json
{
  "prp_id": "34.2.1",
  "status": "in_progress",
  "progress": "Semantic analysis (6/8 checks)",
  "elapsed_seconds": 120
}
```

### Phase 5: Aggregate Results

Collect all review JSONs + perform inter-PRP consistency checks:
```python
all_reviews = [load_json(f"PRP-{id}.result.json") for id in all_batch_prps]
inter_prp_issues = check_consistency(all_reviews)
summary = summarize_reviews(all_reviews, inter_prp_issues)
```

### Phase 6: Report & Cleanup

Generate markdown report + save results to `.ce/orchestration/batches/batch-{batch_id}.result.json`

## Flags

```bash
--batch <id>       # Review entire batch
--exe              # Review execution (after /batch-exe-prp)
--fast             # Haiku only (structural, fast)
--quality          # Sonnet only (semantic, thorough)
--retry-failed     # Re-review failed PRPs only
--verbose          # Detailed check-by-check output
--json             # JSON output only
```

## Output

```
✅ Batch Peer Review Complete
══════════════════════════════════════════════

Batch ID: 34
PRPs Reviewed: 11/11 (100%)
Review Time: 8 minutes
Token Savings: 70% (shared context optimization)

Stage 1 (1 PRP):
  ✓ PRP-34.1.1: Foundation [APPROVED]

Stage 2 (6 PRPs - parallel):
  ✓ PRP-34.2.1: Detection [APPROVED]
  ✓ PRP-34.2.2: Classification [APPROVED]
  ⚠ PRP-34.2.3: Cleanup [NEEDS REVISION]
    - Missing validation gates (3 required, 1 found)
  ... [4 more PRPs]

Stage 3 (3 PRPs - parallel):
  ✓ PRP-34.3.1: Integration [APPROVED]
  ✓ PRP-34.3.2: Tests [APPROVED]
  ✓ PRP-34.3.3: Docs [APPROVED]

Stage 4 (1 PRP):
  ✓ PRP-34.4.1: Final [APPROVED]

═══════════════════════════════════════════════
Summary
═══════════════════════════════════════════════

✅ Approved: 10/11
⚠ Needs Revision: 1/11
❌ Rejected: 0/11

Token Usage: ~120k (70% savings via shared context)
Next: /batch-peer-review --batch 34 --retry-failed
```

Files saved:
- `.ce/orchestration/batches/batch-34.result.json` (aggregated)
- `.ce/orchestration/tasks/batch-34/PRP-*.review.json` (individual)

## Integration with Batch Workflow

```bash
# Step 1: Generate PRPs
/batch-gen-prp PRPs/feature-requests/PRP-34-INITIAL.md

# Step 2: Document review (BEFORE execution)
/batch-peer-review --batch 34

# Step 3: Fix issues, then re-review
/batch-peer-review --batch 34 --retry-failed

# Step 4: Execute batch
/batch-exe-prp --batch 34

# Step 5: Execution review (AFTER execution)
/batch-peer-review --batch 34 --exe

# Step 6: Commit
git add . && git commit -m "Implement batch 34"
```

## Performance

**Token Savings**: 70-75% via shared context (vs naive approach)
- Shared context: ~20k tokens (read once)
- Per-PRP: ~7-10k tokens
- With N=5 PRPs: 70k total vs 250k naive = 72% savings

**Time Savings**: 64% via parallel reviews
- Sequential: 11 PRPs × 2 min = 22 min
- Parallel (staged): 8 min = 64% reduction

**Cost Savings**: 70-75%
- ~$0.30-0.50 per batch (vs $1.00-1.50 naive)

---

**See Also**: `/batch-gen-prp`, `/batch-exe-prp`, `/peer-review`
