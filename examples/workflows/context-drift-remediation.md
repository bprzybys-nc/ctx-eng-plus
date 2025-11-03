# Context Drift Remediation Workflow

Complete guide for detecting, analyzing, and remediating context drift between PRPs and codebase using `analyze-context` and `update-context` commands.

## Purpose

Context drift remediation enables:

- **Drift detection**: Fast checks for PRP-codebase misalignment (2-3s)
- **Full synchronization**: Update all PRPs to match current codebase
- **Automated fixes**: Generate remediation PRPs for high drift
- **Health monitoring**: Track context health over time
- **Prevention**: Best practices to minimize drift

**When to Use**:

- After major refactoring (codebase changed significantly)
- Before starting new feature (ensure clean baseline)
- Sprint retrospectives (periodic health checks)
- High drift detected (>15% drift score)
- Before batch PRP generation (accurate context required)

**When NOT to Use**:

- Active development (expect drift during work)
- Immediately after PRP execution (drift expected temporarily)
- Clean codebase (<5% drift)

## Prerequisites

- Context Engineering tools installed (`cd tools && uv sync`)
- PRPs in `PRPs/executed/` directory
- Git repository with commit history
- Serena MCP active for symbol analysis

## Drift Scores

### Healthy (<5%)

**Status**: ✅ No action needed

**Characteristics**:

- PRPs accurately reflect codebase
- Implementation details match documentation
- File paths current
- Dependencies correct

**Example**:

```
Context Health: 3.2% drift (✅ HEALTHY)

Details:
  - 28/30 PRPs fully aligned
  - 2 PRPs with minor path updates needed
  - All validation gates current
```

### Warning (5-15%)

**Status**: ⚠️ Review recommended

**Characteristics**:

- Some PRPs outdated
- Minor file path changes
- Implementation details shifted
- Dependencies mostly correct

**Example**:

```
Context Health: 8.7% drift (⚠️ WARNING)

Details:
  - 22/30 PRPs aligned
  - 8 PRPs need updates:
    - PRP-12: File moved (tools/ce/core.py → tools/ce/file_ops.py)
    - PRP-18: Function renamed (validate_all → run_validation_suite)
    - PRP-23: Dependency added (now requires Phase 22)
  - All validation gates current
```

### Critical (≥15%)

**Status**: ❌ Action required

**Characteristics**:

- Many PRPs significantly outdated
- Major refactoring occurred
- File structure changed
- Dependencies incorrect

**Example**:

```
Context Health: 24.5% drift (❌ CRITICAL)

Details:
  - 15/30 PRPs aligned
  - 15 PRPs need major updates:
    - PRP-8: Entire file removed (feature deprecated)
    - PRP-12: Implementation approach changed (monolith → microservices)
    - PRP-18: 50% of code refactored
  - Recommend: Run update-context immediately
```

## Fast Drift Check

### Analyze-Context (2-3 seconds)

Quick drift check without updates:

```bash
# Fast check
cd tools && uv run ce analyze-context

# Or via session start hook (automatic)
# Runs every time you start Claude Code session
```

**Output**:

```
🔍 Analyzing Context Health...
============================================================

Checking 30 executed PRPs:
  ✅ PRP-1: Aligned (0% drift)
  ✅ PRP-2: Aligned (0% drift)
  ⚠️  PRP-12: Minor drift (8% - file path changed)
  ⚠️  PRP-18: Minor drift (6% - function renamed)
  ❌ PRP-23: Major drift (22% - implementation refactored)
  ...

Summary:
  Drift Score: 8.7% (⚠️ WARNING)
  28 PRPs aligned (0-5% drift)
  1 PRP needs review (5-15% drift)
  1 PRP needs update (≥15% drift)

Recommendation:
  Review PRP-23 for major drift
  Run update-context for full sync: uv run ce update-context

Exit code: 1 (warning threshold exceeded)
============================================================
```

**Exit Codes**:

- `0`: <5% drift (healthy)
- `1`: 5-15% drift (warning)
- `2`: ≥15% drift (critical)

### Force Re-Analysis

Cache results for 5 minutes, force refresh:

```bash
# Force fresh analysis
cd tools && uv run ce analyze-context --force
```

## Full Synchronization

### Update-Context (10-15 seconds)

Update all PRPs to match current codebase:

```bash
# Update all PRPs
cd tools && uv run ce update-context

# Update specific PRP
cd tools && uv run ce update-context --prp PRPs/executed/PRP-12-validation-gates.md
```

**Output**:

```
🔄 Updating Context: All PRPs
============================================================

Analyzing codebase...
  Scanning files modified since last update
  Building symbol index
  Checking dependencies

Updating PRPs:
  ✅ PRP-1: No changes needed
  ✅ PRP-2: No changes needed
  🔧 PRP-12: Updated file path (core.py → file_ops.py)
  🔧 PRP-18: Updated function name (validate_all → run_validation_suite)
  🔧 PRP-23: Major update (50% of implementation section rewritten)
  ...

Summary:
  30 PRPs checked
  27 PRPs unchanged
  3 PRPs updated
  New drift score: 1.2% (✅ HEALTHY)

Files modified:
  PRPs/executed/PRP-12-validation-gates.md
  PRPs/executed/PRP-18-test-framework.md
  PRPs/executed/PRP-23-api-refactor.md

Recommendation:
  Review updated PRPs: git diff PRPs/executed/
  Commit changes: git add PRPs/executed/ && git commit -m "Context sync: drift 8.7% → 1.2%"
============================================================
```

## Interpreting Drift Scores

### Drift Score Calculation

```python
def calculate_drift(prp, codebase):
    """Calculate drift percentage for a PRP"""

    drift_factors = {
        'files_moved': weight=0.15,
        'files_deleted': weight=0.25,
        'functions_renamed': weight=0.10,
        'signatures_changed': weight=0.20,
        'dependencies_changed': weight=0.15,
        'implementation_diverged': weight=0.15
    }

    total_drift = 0
    for factor, weight in drift_factors.items():
        if detect_drift(prp, codebase, factor):
            total_drift += weight

    return total_drift  # 0.0 to 1.0 (0% to 100%)
```

### Drift Factors Breakdown

**Example**:

```
PRP-23 Drift Analysis:
============================================================

Files (15% weight):
  ✅ tools/ce/api.py: Exists, no changes
  ⚠️  tools/ce/routes.py: Moved → tools/ce/api/routes.py (drift: 15%)

Functions (10% weight):
  ✅ create_endpoint: Signature unchanged
  ❌ validate_request: Renamed → validate_api_request (drift: 10%)

Signatures (20% weight):
  ❌ validate_api_request: Added parameter 'schema: dict' (drift: 20%)

Dependencies (15% weight):
  ✅ Phase 22: Still valid dependency
  ❌ Now also depends on Phase 25 (not documented) (drift: 15%)

Implementation (15% weight):
  ❌ 50% of code refactored (drift: 15%)

Total Drift: 75% (❌ CRITICAL)
============================================================
```

## Remediation Strategies

### Strategy 1: Minor Drift (<15%) - Direct Update

For minor drift, update PRPs directly:

```bash
# Update all PRPs with minor drift
cd tools && uv run ce update-context

# Review changes
git diff PRPs/executed/

# Commit if satisfied
git add PRPs/executed/
git commit -m "Context sync: Updated 3 PRPs with minor drift"
```

### Strategy 2: Major Drift (≥15%) - Remediation PRP

For major drift, generate remediation PRP:

```bash
# Analyze drift
cd tools && uv run ce analyze-context --verbose

# Generate remediation PRP
/generate-prp --from-drift PRP-23-api-refactor.md

# Output: PRP-34-remediate-prp-23-drift.md
```

**Remediation PRP Structure**:

```markdown
---
prp_id: 34
feature_name: Remediate PRP-23 Context Drift
status: pending
---

# Remediate PRP-23 Context Drift

## Problem

PRP-23 has 75% drift score due to:
- File moved: tools/ce/routes.py → tools/ce/api/routes.py
- Function renamed: validate_request → validate_api_request
- Signature changed: Added 'schema: dict' parameter
- Dependency added: Now depends on Phase 25
- Implementation refactored: 50% code rewrite

## Solution

Update PRP-23 to reflect current codebase state.

## Implementation Steps

1. Update file paths in PRP-23
2. Update function names and signatures
3. Add Phase 25 dependency
4. Rewrite implementation section (sections 3.2-3.5)
5. Update validation gates if needed

## Validation Gates

- L1: PRP-23 markdown syntax valid
- L2: All file paths exist
- L3: All function references valid
- L4: Drift score for PRP-23 < 5%
```

### Strategy 3: Systematic Drift (Multiple PRPs) - Batch Update

For systematic drift across many PRPs:

```bash
# Identify all PRPs with ≥10% drift
cd tools && uv run ce analyze-context --threshold 10 --list

# Output: PRP-12, PRP-18, PRP-23, PRP-27, PRP-29

# Generate batch remediation plan
/batch-gen-prp DRIFT-REMEDIATION-PLAN.md
```

**Drift Remediation Plan**:

```markdown
# Drift Remediation Plan

## Phases

### Phase 1: File Path Updates (PRP-12, PRP-18)

**Goal**: Update file paths for moved files

**Estimated Hours**: 0.5

**Dependencies**: None

### Phase 2: Function Renames (PRP-23, PRP-27)

**Goal**: Update function references

**Estimated Hours**: 1.0

**Dependencies**: Phase 1

### Phase 3: Implementation Rewrites (PRP-29)

**Goal**: Rewrite implementation sections

**Estimated Hours**: 2.0

**Dependencies**: Phase 2
```

## Drift Prevention

### Best Practice 1: Regular Health Checks

```bash
# Weekly: Fast check
cd tools && uv run ce analyze-context

# Monthly: Full sync
cd tools && uv run ce update-context

# After major refactoring: Immediate sync
git log --oneline -20  # Check recent commits
cd tools && uv run ce update-context
```

### Best Practice 2: Session Start Hook

Auto-check drift at session start (already configured):

```yaml
# .claude/hooks/session-start
#!/bin/bash

echo "Checking context drift..."
cd tools && uv run ce analyze-context

if [ $? -eq 2 ]; then
  echo "⚠️  HIGH DRIFT: Run 'ce update-context'"
fi
```

### Best Practice 3: Post-PRP Execution Sync

After executing PRP, update immediately:

```bash
# Execute PRP
/execute-prp PRPs/feature-requests/PRP-35-new-feature.md

# Update context
cd tools && uv run ce update-context --prp PRPs/executed/PRP-35-new-feature.md
```

### Best Practice 4: Pre-Batch Generation Sync

Before batch generation, ensure clean baseline:

```bash
# Check drift
cd tools && uv run ce analyze-context

# If drift > 5%, sync first
cd tools && uv run ce update-context

# Now safe to generate batch
/batch-gen-prp FEATURE-PLAN.md
```

## Common Patterns

### Pattern 1: Post-Refactoring Sync

After major refactoring:

```bash
# Step 1: Complete refactoring
git add .
git commit -m "Refactor: Modularize API layer"

# Step 2: Check drift
cd tools && uv run ce analyze-context
# Output: 18.3% drift (❌ CRITICAL)

# Step 3: Full sync
cd tools && uv run ce update-context

# Step 4: Verify
cd tools && uv run ce analyze-context
# Output: 2.1% drift (✅ HEALTHY)

# Step 5: Commit PRP updates
git add PRPs/executed/
git commit -m "Context sync: drift 18.3% → 2.1%"
```

### Pattern 2: Sprint Retrospective Cleanup

At end of sprint:

```bash
# Review sprint work
git log --since="2 weeks ago" --oneline

# Check accumulated drift
cd tools && uv run ce analyze-context --verbose

# Sync PRPs
cd tools && uv run ce update-context

# Clean obsolete content
cd tools && uv run ce vacuum --auto

# Commit cleanup
git add .
git commit -m "Sprint 45 cleanup: context sync + vacuum"
```

### Pattern 3: Continuous Monitoring

Track drift over time:

```bash
# Add to cron job (daily)
0 9 * * * cd /path/to/project/tools && uv run ce analyze-context --report >> ../drift-log.txt

# Review weekly
grep "Drift Score" drift-log.txt | tail -7
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Ignoring Drift Warnings

**Bad**:

```bash
# DON'T ignore warnings
cd tools && uv run ce analyze-context
# Output: 12% drift (⚠️ WARNING)
# ... continue working without sync
```

**Good**:

```bash
# DO address warnings
cd tools && uv run ce analyze-context
# Output: 12% drift (⚠️ WARNING)
cd tools && uv run ce update-context
```

**Why**: Drift compounds over time, becomes critical if ignored.

### ❌ Anti-Pattern 2: Over-Frequent Updates

**Bad**:

```bash
# DON'T update after every small change
# Edit 1 line
cd tools && uv run ce update-context
# Edit 1 more line
cd tools && uv run ce update-context
```

**Good**:

```bash
# DO batch updates after logical milestones
# Complete feature
git add .
git commit -m "Feature complete"
cd tools && uv run ce update-context
```

**Why**: Over-frequent updates waste time, cause churn.

### ❌ Anti-Pattern 3: No Drift Monitoring

**Bad**: Never check drift, discover 50% drift 3 months later

**Good**: Weekly analyze-context, monthly update-context

**Why**: Proactive monitoring prevents critical drift.

## Related Examples

- [batch-prp-generation.md](batch-prp-generation.md) - Sync before batch generation
- [vacuum-cleanup.md](vacuum-cleanup.md) - Complementary cleanup
- [denoise-documents.md](denoise-documents.md) - Reduce drift via compression
- [../syntropy/serena-symbol-search.md](../syntropy/serena-symbol-search.md) - Symbol analysis for drift detection

## Troubleshooting

### Issue: "High drift but update-context makes no changes"

**Symptom**: Drift score high, but update-context reports "No updates needed"

**Cause**: Drift detection algorithms incomplete or false positives

**Solution**:

```bash
# Manual review
cd tools && uv run ce analyze-context --verbose --explain

# Check specific PRP
cat PRPs/executed/PRP-23-api-refactor.md

# Manually update if needed
vim PRPs/executed/PRP-23-api-refactor.md
```

### Issue: Update-context overwrites manual changes

**Symptom**: Custom PRP edits lost after update-context

**Solution**:

```bash
# Restore from git
git checkout PRPs/executed/PRP-23-api-refactor.md

# Use selective update
cd tools && uv run ce update-context --prp PRPs/executed/PRP-23-api-refactor.md --section implementation

# Or exclude from auto-updates
echo "PRP-23" >> .context-sync-ignore
```

### Issue: "Drift score calculation unclear"

**Symptom**: Don't understand why drift is 15%

**Solution**:

```bash
# Detailed breakdown
cd tools && uv run ce analyze-context --prp PRP-23 --explain

# Output shows factor-by-factor drift calculation
```

## Performance Tips

1. **Frequency**: Analyze weekly, update monthly (unless critical)
2. **Cache**: Use cached results (5min), only force when needed
3. **Batch updates**: Update all PRPs at once, not individually
4. **Preventive sync**: Update after major refactorings immediately
5. **Monitoring**: Track drift over time to identify patterns

## Resources

- CE CLI Commands: `cd tools && uv run ce analyze-context --help`
- Session Start Hook: `.claude/hooks/session-start`
- Drift Log: `drift-log.txt`
- Context Sync Ignore: `.context-sync-ignore`
