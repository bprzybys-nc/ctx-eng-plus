# /batch-exe-fast - Fast Pragmatic Batch Executor

Execute PRP batches using optimized shell script. Fast delivery, immediate execution.

## Usage

```bash
# Execute all stages in batch
./.ce/orchestration/batch-executor-v2.sh 47

# Execute specific stage only
./.ce/orchestration/batch-executor-v2.sh 47 2
```

## Quick Start

```bash
# Test: Show PRPs in batch 47, stage 2
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
./.ce/orchestration/batch-executor-v2.sh 47 2
```

## What It Does

1. **Load PRPs**: Find all PRP-{batch}.*.md files
2. **Validate**: Check dependencies are valid (no undefined refs)
3. **Assign Stages**: Group PRPs by stage (from YAML)
4. **Execute**: Run each PRP, track results
5. **Report**: Summary with success/failure counts

## Example Output

```
╔════════════════════════════════════════════════════════════════╗
║              BATCH EXECUTOR - Stage-Based Execution            ║
╚════════════════════════════════════════════════════════════════╝

ℹ Found 10 PRPs for batch 47
ℹ Validating dependencies...
✓ All dependencies valid
ℹ Assigning execution stages...
ℹ Stage 1:
  - PRP-47.1.1
ℹ Stage 2:
  - PRP-47.2.1
  - PRP-47.2.2
ℹ Stage 3:
  - PRP-47.3.1
  - PRP-47.3.2
  - PRP-47.4.1
...

ℹ Starting execution...
ℹ Executing PRP-47.2.1...
✓ dependency_analyzer.py exists
✓ Tests passing
✓ PRP-47.2.1 complete (3 seconds)

ℹ Executing PRP-47.2.2...
✓ test_dependency_analyzer.py exists
✓ PRP-47.2.2 complete (2 seconds)

════════════════════════════════════════════════════════════════
BATCH 47 EXECUTION SUMMARY
════════════════════════════════════════════════════════════════
Total PRPs: 2
✓ Successful: 2
════════════════════════════════════════════════════════════════

✓ Batch execution complete!
```

## How It Works

- **Parsing**: Extracts PRP IDs, stages, dependencies from YAML frontmatter
- **Validation**: Ensures all dependencies exist before execution
- **Execution**: For Phase 2 (47.2.1, 47.2.2), verifies files exist + tests pass
- **Tracking**: Git commits for each PRP execution
- **Results**: JSON output per PRP + batch summary

## Files

- **Script**: `.ce/orchestration/batch-executor-v2.sh` (12 KB, pure bash)
- **Results**: `.ce/orchestration/batches/batch-{id}.result.json`
- **Per-PRP Results**: `.ce/orchestration/batches/prp-{id}.result.json`

## Performance

- **Load & validate**: <1 second
- **Per-PRP execution**: 2-5 seconds (verification only, no actual code generation)
- **Stage 2 (2 PRPs)**: ~5-10 seconds total
- **Stage 3 (3 PRPs)**: ~10-15 seconds total
- **All stages (10 PRPs)**: ~30-40 seconds total

## Advantages Over Full Orchestrator

✅ **Ready now** (no waiting for Python orchestrator)
✅ **Fast execution** (shell scripts are lightweight)
✅ **Simple to understand** (pure bash, no complex logic)
✅ **Immediate results** (dependencies validated, stages assigned)
✅ **Git-tracked** (progress visible in git log)
✅ **Extensible** (easy to add new PRP types)

## Next: Upgrade to Full Orchestrator

Once this proves the batch concept works:
1. Port shell script logic to Python orchestrator
2. Add heartbeat monitoring (30s polling)
3. Add Sonnet/Haiku subagent spawning
4. Add advanced error recovery
5. Deploy as production system

## Example: Execute Stage 2 NOW

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
./.ce/orchestration/batch-executor-v2.sh 47 2
```

**Result**: PRP-47.2.1 verified (dependency_analyzer.py exists), results saved in JSON.

## Command Invocation via /batch-exe-fast

The `/batch-exe-fast` command is a Claude Code hook that executes the shell script. Note that the command documentation shows the interface, but the actual script uses positional arguments:

```bash
# What users might try (flag-based - from command docs)
/batch-exe-fast --batch 47 --stage 2

# What the script actually expects (positional)
./.ce/orchestration/batch-executor-v2.sh 47 2
```

**Fix**: The command hook should be updated to convert flag arguments to positional arguments when invoking the script.
