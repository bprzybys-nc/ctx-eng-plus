# Batch Metrics Recovery Guide

**Purpose**: Restore trend analysis capability after system restart

---

## Quick Start (After System Restart)

### Option 1: Claude Code Slash Command

```bash
# In Claude Code terminal
/batch-trend-analysis --recent 5
```

**What it does**:
- Analyzes last 5 batches
- Shows duration trends, bottlenecks, recommendations
- No arguments needed (sensible defaults)

### Option 2: Direct Script Invocation

```bash
# From project root
./.ce/scripts/run-trend-analysis.sh --recent 10

# Or all batches
./.ce/scripts/run-trend-analysis.sh --all
```

### Option 3: Manual Python Execution

```bash
cd /Users/bprzybysz/nc-src/ctx-eng-plus
python3 .ce/scripts/trend-analysis.py --recent 5
```

---

## Metric Files Location

All batch metrics are stored in:

```
.ce/completed-batches/
├── batch-47-generate.json      (generation metrics)
├── batch-47-execute.json       (execution metrics)
├── batch-47-review.json        (review metrics)
├── batch-47-update-context.json
├── batch-48-generate.json      (next batch)
└── ...
```

**Persistent**: Metrics survive system restart (stored on disk)

---

## Recovery Procedure

### Step 1: Verify Metrics Exist

```bash
ls -la .ce/completed-batches/
```

**Expected**: List of `batch-*.json` files

**If empty**: No metrics collected yet (normal for fresh install)

### Step 2: Check System Integrity

```bash
# Verify scripts exist
ls -la .ce/scripts/trend-analysis.py
ls -la .ce/scripts/analyze-batch.py

# Verify schema exists
ls -la .ce/schemas/batch-metrics.json
```

### Step 3: Run Trend Analysis

```bash
# Quick check (last 5 batches)
/batch-trend-analysis

# Or via shell script
./.ce/scripts/run-trend-analysis.sh

# Or direct Python
python3 .ce/scripts/trend-analysis.py --recent 5
```

### Step 4: Review Output

Expected output includes:
- Duration trends (mean, median, stdev by operation)
- Bottleneck analysis (slow operations, high costs)
- Success rates by operation
- Token usage trends
- Phase 2 recommendations (prioritized)

---

## Common Issues

### Issue: "Metrics directory not found"

**Cause**: No batches have been executed yet

**Solution**:
```bash
# Run a test batch to generate metrics
/batch-gen-prp PRPs/feature-requests/TEST-PLAN.md

# Then run trend analysis
/batch-trend-analysis --recent 1
```

### Issue: "Python 3 not found"

**Cause**: Python not in PATH after system restart

**Solution**:
```bash
# Check Python installation
which python3

# If not found, install Python 3.8+
# macOS: brew install python3
# Ubuntu: sudo apt install python3

# Then retry
/batch-trend-analysis
```

### Issue: "Permission denied"

**Cause**: Script not executable

**Solution**:
```bash
chmod +x .ce/scripts/run-trend-analysis.sh
chmod +x .ce/scripts/trend-analysis.py
```

### Issue: "No JSON files found"

**Cause**: Metrics directory exists but is empty

**Solution**:
- Run batches to generate metrics
- Metrics auto-generate after batch completion
- Check `.ce/completed-batches/` after running batch command

---

## Metrics Collection

### Automatic (Built-In)

Batch commands automatically generate metrics:
- `/batch-gen-prp` → `batch-{id}-generate.json`
- `/batch-exe-prp` → `batch-{id}-execute.json`
- `/batch-peer-review` → `batch-{id}-review.json`
- `/batch-update-context` → `batch-{id}-update-context.json`

### Manual (On-Demand)

```bash
# Analyze specific batch
python3 .ce/scripts/analyze-batch.py --batch 47 --operation generate

# Generate metrics JSON
# Output: .ce/completed-batches/batch-47-generate.json
```

---

## Metrics Schema

All metrics follow `.ce/schemas/batch-metrics.json`:

```json
{
  "batch_id": "47",
  "operation": "generate",
  "timestamp": "2025-11-10T14:30:00Z",
  "duration_seconds": 180,
  "metrics": {
    "total_items": 4,
    "stages": 3,
    "success_count": 4,
    "failure_count": 0,
    "tokens_used": 45600,
    "cost_usd": 0.91
  }
}
```

---

## Recovery Workflow (Full)

### After System Restart:

```bash
# 1. Verify project structure
cd /Users/bprzybysz/nc-src/ctx-eng-plus
git status

# 2. Check metrics exist
ls -la .ce/completed-batches/

# 3. Make scripts executable (if needed)
chmod +x .ce/scripts/run-trend-analysis.sh
chmod +x .ce/scripts/trend-analysis.py

# 4. Run trend analysis
/batch-trend-analysis --recent 5

# 5. Review recommendations
# Output will show Phase 2 improvements to prioritize
```

### If Everything Restored:

```bash
✅ Metrics recovered
✅ Trend analysis running
✅ Phase 2 recommendations available
✅ Ready to continue batch operations
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Last 5 batches | `/batch-trend-analysis` |
| Last N batches | `/batch-trend-analysis --recent N` |
| All batches | `/batch-trend-analysis --all` |
| Verbose output | `/batch-trend-analysis --verbose` |
| Direct script | `./.ce/scripts/run-trend-analysis.sh` |
| Manual Python | `python3 .ce/scripts/trend-analysis.py --recent 5` |
| Check metrics | `ls -la .ce/completed-batches/` |
| Schema | `cat .ce/schemas/batch-metrics.json` |

---

## Files Involved

### Scripts
- `.ce/scripts/trend-analysis.py` - Trend analyzer (Python)
- `.ce/scripts/run-trend-analysis.sh` - Launcher wrapper (Bash)
- `.ce/scripts/analyze-batch.py` - Metrics extraction

### Data
- `.ce/completed-batches/` - Metrics storage (persistent)
- `.ce/schemas/batch-metrics.json` - Metrics schema

### Documentation
- `.claude/commands/batch-trend-analysis.md` - Slash command docs
- `.ce/BATCH-METRICS-RECOVERY.md` - This file

---

## Verification Checklist

After system restart:

```bash
[ ] Project directory accessible
[ ] Git repository intact (git status)
[ ] Python 3 available (python3 --version)
[ ] Metrics directory exists (.ce/completed-batches/)
[ ] Scripts executable (ls -la .ce/scripts/)
[ ] Schema valid (cat .ce/schemas/batch-metrics.json)
[ ] Trend analysis runs (/batch-trend-analysis)
[ ] Output displays metrics
```

If all checked: **System ready, metrics recovered**

---

## Support

For issues:
1. Run `/batch-trend-analysis --help`
2. Check metrics: `ls -la .ce/completed-batches/`
3. Verify scripts: `which python3`, `ls -la .ce/scripts/`
4. Review errors: Full Python traceback shown if problem

---

## Next Steps

Once metrics recovered:

1. **Review trends** → `/batch-trend-analysis --recent 10`
2. **Identify bottlenecks** → Read recommendations section
3. **Plan Phase 2** → Create PRPs for top 3 improvements
4. **Execute improvements** → `/batch-exe-prp --batch 48`
5. **Monitor impact** → Re-run trend analysis after Phase 2

---

**Last Updated**: 2025-11-10
**Status**: Production Ready
**Recovery Time**: ~2 minutes (typical)
