# Vacuum Cleanup Workflow

Complete guide for identifying and removing project noise using the `/vacuum` command with confidence-based deletion strategies.

## Purpose

Vacuum cleanup enables:

- **Noise reduction**: Remove temp files, obsolete docs, dead links, and redundant content
- **Token optimization**: Reduce codebase size for better context fit
- **Project hygiene**: Maintain clean working directory
- **Confidence-based deletion**: Safe removal with risk assessment
- **Dry-run mode**: Preview changes before applying

**When to Use**:

- After completing large features (accumulated temp files)
- Before major refactoring (clean slate)
- Sprint cleanup (remove obsolete documentation)
- Context drift mitigation (remove outdated references)
- Pre-deployment (ensure no temp files shipped)

**When NOT to Use**:

- Active development (may delete work-in-progress)
- Unclear project state (run dry-run first)
- Without backups (git commit before vacuum)

## Prerequisites

- Clean git working directory (commit changes first)
- Context Engineering tools installed (`cd tools && uv sync`)
- Understanding of confidence levels (high, medium, low)

## Confidence Levels

### High Confidence (90-100%)

**Safe to delete automatically**:

- Temp files: `.tmp`, `.cache`, `*.pyc`, `__pycache__/`
- Editor files: `.swp`, `.swo`, `.DS_Store`, `*~`
- Build artifacts: `dist/`, `build/`, `*.egg-info/`
- Log files: `*.log` (not in logs/)
- Empty directories

### Medium Confidence (60-89%)

**Probably safe, review recommended**:

- Duplicate documentation (99% similar content)
- Dead links in markdown (404 responses)
- Unused imports (no references found)
- Obsolete TODOs (completed in code)
- Stale heartbeat files (>7 days old)

### Low Confidence (< 60%)

**Manual review required**:

- Documentation with unclear status
- Files with mixed content (some relevant, some obsolete)
- Ambiguous references
- Potential false positives

## Vacuum Modes

### Mode 1: Dry-Run (Report Only)

**Default mode**: No deletions, only reporting

```bash
# Report all noise found
cd tools && uv run ce vacuum

# Or via slash command
/vacuum
```

**Output**:

```
🧹 Vacuum Analysis Report
============================================================

High Confidence (10 items, 2.4 MB):
  [95%] tmp/test-output-2025-11-01.json (1.2 MB)
  [92%] .cache/pytest_cache/ (800 KB)
  [90%] dist/ (400 KB)
  ...

Medium Confidence (5 items, 150 KB):
  [85%] docs/OLD-GUIDE.md (dead link to removed file)
  [75%] examples/deprecated-pattern.md (duplicate of examples/pattern.md)
  [65%] tools/ce/unused_utils.py (no imports found)
  ...

Low Confidence (2 items, 50 KB):
  [45%] docs/MAYBE-OBSOLETE.md (unclear status)
  [40%] tmp/analysis-notes.txt (mixed content)

Total:
  17 items, 2.6 MB
  Recommended: Delete high confidence items (2.4 MB savings)
============================================================

Actions:
  Dry-run complete. No files deleted.
  To delete high confidence items: uv run ce vacuum --execute
  To delete high + medium: uv run ce vacuum --auto
  To delete everything: uv run ce vacuum --nuclear
```

### Mode 2: Execute (High Confidence Only)

**Safe automatic deletion**: Only high confidence items

```bash
# Delete high confidence items
cd tools && uv run ce vacuum --execute
```

**Output**:

```
🧹 Vacuum Execution: High Confidence
============================================================

Deleting 10 items (2.4 MB):
  ✅ Deleted tmp/test-output-2025-11-01.json (1.2 MB)
  ✅ Deleted .cache/pytest_cache/ (800 KB)
  ✅ Deleted dist/ (400 KB)
  ...

Completed:
  10 items deleted, 2.4 MB freed
  7 items skipped (medium/low confidence)

Recommendation:
  Review medium confidence items: uv run ce vacuum --show-medium
============================================================
```

### Mode 3: Auto (High + Medium Confidence)

**Moderate automation**: Delete high + medium confidence items

```bash
# Delete high + medium confidence items
cd tools && uv run ce vacuum --auto
```

**Output**:

```
🧹 Vacuum Execution: Auto Mode (High + Medium)
============================================================

Deleting 15 items (2.55 MB):
  High confidence (10 items, 2.4 MB):
    ✅ [95%] tmp/test-output-2025-11-01.json
    ...
  Medium confidence (5 items, 150 KB):
    ✅ [85%] docs/OLD-GUIDE.md (dead link)
    ✅ [75%] examples/deprecated-pattern.md (duplicate)
    ...

Completed:
  15 items deleted, 2.55 MB freed
  2 items skipped (low confidence - manual review)

Manual review required:
  docs/MAYBE-OBSOLETE.md (45% confidence)
  tmp/analysis-notes.txt (40% confidence)
============================================================
```

### Mode 4: Nuclear (All Items)

**Destructive**: Delete everything, including low confidence

```bash
# Delete ALL items (requires confirmation)
cd tools && uv run ce vacuum --nuclear
```

**Confirmation Prompt**:

```
⚠️  NUCLEAR MODE: Will delete ALL 17 items (2.6 MB)
⚠️  This includes 2 low confidence items that may be needed.

Items to delete:
  - 10 high confidence (2.4 MB)
  - 5 medium confidence (150 KB)
  - 2 low confidence (50 KB)

Type 'DELETE' to confirm: _
```

**After Confirmation**:

```
🧹 Vacuum Execution: Nuclear Mode
============================================================

Deleting ALL 17 items (2.6 MB):
  ✅ [95%] tmp/test-output-2025-11-01.json
  ...
  ✅ [45%] docs/MAYBE-OBSOLETE.md
  ✅ [40%] tmp/analysis-notes.txt

Completed:
  17 items deleted, 2.6 MB freed

Recommendation:
  Run validation: uv run ce validate --level 4
  Commit changes: git add . && git commit -m "Vacuum: cleaned 2.6 MB"
============================================================
```

## Custom Confidence Thresholds

### Adjust Thresholds

```bash
# Lower high confidence threshold (80%+)
cd tools && uv run ce vacuum --execute --threshold-high 80

# Raise medium confidence threshold (70%+)
cd tools && uv run ce vacuum --auto --threshold-medium 70

# Custom range for execute mode
cd tools && uv run ce vacuum --execute --threshold-range 85-100
```

### Example: Conservative Cleanup

Only delete items with 95%+ confidence:

```bash
cd tools && uv run ce vacuum --execute --threshold-high 95
```

## Strategy Exclusion

### Available Strategies

- `temp_files`: Temp files and cache directories
- `build_artifacts`: Build outputs (dist/, *.egg-info/)
- `editor_files`: Editor temp files (.swp, .DS_Store)
- `dead_links`: Broken links in documentation
- `duplicate_docs`: Near-duplicate markdown files
- `obsolete_todos`: Completed TODO comments
- `unused_imports`: Unreferenced imports
- `empty_dirs`: Empty directories

### Exclude Specific Strategies

```bash
# Skip dead link detection (keep broken links)
cd tools && uv run ce vacuum --execute --exclude dead_links

# Skip multiple strategies
cd tools && uv run ce vacuum --auto --exclude dead_links,duplicate_docs

# Only run specific strategy
cd tools && uv run ce vacuum --execute --only temp_files
```

## Reading Vacuum Reports

### Report Structure

```
🧹 Vacuum Analysis Report
============================================================

[Confidence Level] ([Item Count] items, [Total Size]):
  [Confidence %] [File Path] ([Size])
    Strategy: [Strategy Name]
    Reason: [Why flagged for deletion]
    Risk: [Why confidence level assigned]

  ...
```

### Detailed Report

```bash
# Show detailed analysis
cd tools && uv run ce vacuum --verbose

# Export report to file
cd tools && uv run ce vacuum --report vacuum-report-2025-11-03.txt
```

**Detailed Output Example**:

```
[85%] docs/OLD-GUIDE.md (12 KB)
  Strategy: dead_links
  Reason: Contains 5 dead links to removed files
    - REMOVED-FEATURE.md (deleted 2024-10-15)
    - old-api.md (deleted 2024-09-20)
    - deprecated-cli.md (deleted 2024-08-10)
  Risk: Medium confidence (85%)
    - File still referenced in 1 location: README.md:45
    - Last modified: 2024-07-01 (4 months old)
  Recommendation: Review links, update or delete file

[75%] examples/deprecated-pattern.md (8 KB)
  Strategy: duplicate_docs
  Reason: 99% similar to examples/pattern.md
    - Diff: Only title changed ("Old Pattern" vs "Pattern")
    - Content hash: 98.7% match
  Risk: Medium confidence (75%)
    - May contain historical context worth preserving
  Recommendation: Merge content if needed, then delete
```

## Common Patterns

### Pattern 1: Pre-Deployment Cleanup

Before deploying, clean all temp files:

```bash
# Step 1: Commit current work
git add .
git commit -m "Feature complete: User authentication"

# Step 2: Dry-run to see what will be deleted
cd tools && uv run ce vacuum

# Step 3: Delete high confidence items
cd tools && uv run ce vacuum --execute

# Step 4: Verify no critical files deleted
git status
git diff

# Step 5: Commit cleanup
git add .
git commit -m "Vacuum: cleaned 2.4 MB of temp files"

# Step 6: Deploy
git push origin main
```

### Pattern 2: Sprint Retrospective Cleanup

After sprint, remove obsolete documentation:

```bash
# Review all items
cd tools && uv run ce vacuum --verbose

# Delete high + medium confidence items
cd tools && uv run ce vacuum --auto

# Manually review low confidence items
for file in $(cd tools && uv run ce vacuum --show-low | cut -d' ' -f2); do
  echo "Review: $file"
  cat "$file"
  read -p "Delete? (y/n): " choice
  if [ "$choice" = "y" ]; then
    rm "$file"
  fi
done

# Commit cleanup
git add .
git commit -m "Sprint 45 cleanup: removed obsolete docs"
```

### Pattern 3: Incremental Cleanup

Clean strategically over time:

```bash
# Week 1: Temp files only
cd tools && uv run ce vacuum --execute --only temp_files

# Week 2: Dead links
cd tools && uv run ce vacuum --execute --only dead_links

# Week 3: Duplicate docs
cd tools && uv run ce vacuum --execute --only duplicate_docs

# Week 4: Full cleanup
cd tools && uv run ce vacuum --auto
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Nuclear Mode Without Backup

**Bad**:

```bash
# DON'T use nuclear mode without commit
cd tools && uv run ce vacuum --nuclear
```

**Good**:

```bash
# DO commit first
git add .
git commit -m "Before vacuum nuclear"
cd tools && uv run ce vacuum --nuclear
```

**Why**: Nuclear mode may delete important files. Git commit enables rollback.

### ❌ Anti-Pattern 2: Ignoring Dry-Run Warnings

**Bad**:

```bash
# DON'T skip dry-run
cd tools && uv run ce vacuum --execute  # Immediately execute
```

**Good**:

```bash
# DO review dry-run first
cd tools && uv run ce vacuum  # Dry-run
# Review output...
cd tools && uv run ce vacuum --execute
```

**Why**: Dry-run reveals unexpected items flagged for deletion.

### ❌ Anti-Pattern 3: Over-Aggressive Thresholds

**Bad**:

```bash
# DON'T lower thresholds too far
cd tools && uv run ce vacuum --execute --threshold-high 50
# Deletes files with 50% confidence!
```

**Good**:

```bash
# DO use conservative thresholds
cd tools && uv run ce vacuum --execute --threshold-high 90
```

**Why**: Low thresholds increase false positives, risk deleting needed files.

## Related Examples

- [batch-prp-generation.md](batch-prp-generation.md) - Cleanup before batch generation
- [context-drift-remediation.md](context-drift-remediation.md) - Cleanup to reduce drift
- [denoise-documents.md](denoise-documents.md) - Document compression (complementary to vacuum)
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - Tool selection for cleanup tasks

## Troubleshooting

### Issue: "Permission denied" when deleting

**Symptom**: `Error: Permission denied: /path/to/file`

**Cause**: File locked by process or restricted permissions

**Solution**:

```bash
# Check file permissions
ls -la /path/to/file

# Check if file open by process
lsof /path/to/file

# Fix permissions if needed
chmod 644 /path/to/file

# Retry vacuum
cd tools && uv run ce vacuum --execute
```

### Issue: False positive - needed file flagged

**Symptom**: Vacuum flags needed file for deletion

**Solution**:

```bash
# Exclude strategy that flagged it
cd tools && uv run ce vacuum --execute --exclude <strategy>

# Or add to .vacuumignore
echo "path/to/needed/file" >> .vacuumignore

# Retry vacuum
cd tools && uv run ce vacuum --execute
```

### Issue: "No items found"

**Symptom**: Vacuum reports 0 items

**Cause**: Project already clean, or strategies not detecting noise

**Solution**:

```bash
# Run with verbose mode
cd tools && uv run ce vacuum --verbose

# Check if specific strategies disabled
cd tools && uv run ce vacuum --list-strategies

# Lower confidence threshold to find more items
cd tools && uv run ce vacuum --threshold-high 70
```

## Performance Tips

1. **Frequency**: Run dry-run weekly, execute monthly
2. **Strategy selection**: Use `--only` for targeted cleanup
3. **Threshold tuning**: Start at 90%, lower cautiously
4. **Batch cleanup**: Combine vacuum with denoise for max cleanup
5. **Git hygiene**: Always commit before vacuum operations

## Resources

- CE CLI Command: `cd tools && uv run ce vacuum --help`
- Strategy Documentation: `tools/ce/vacuum_strategies.py`
- Configuration: `.vacuumignore` (gitignore-style excludes)
- Vacuum Reports: `vacuum-report-*.txt`
