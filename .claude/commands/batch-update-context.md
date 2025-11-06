# Batch Update Context

Update context for multiple PRPs in a batch with automatic repomix rebuild.

## Usage

```bash
/batch-update-context prp <batch-ids>
/batch-update-context --prp <prp-file> [--prp <prp-file> ...]
```

## Arguments

- `prp <batch-ids>`: Space-separated batch IDs (e.g., "prp 34 36")
- `--prp <prp-file>`: Individual PRP file path (repeatable)

## What it does

Batch context update with automatic framework rebuild:

1. **Discover PRPs**
   - Parse batch IDs or individual file paths
   - Find all matching PRPs in `PRPs/feature-requests/` and `PRPs/executed/`
   - Group by batch for reporting

2. **Update Context**
   - Run `update-context --prp <file>` for each PRP
   - Verify implementations against codebase
   - Update YAML headers with sync status
   - Collect drift violations across all PRPs

3. **Aggregate Results**
   - Total PRPs scanned/updated/moved
   - Combined drift score
   - Cross-PRP pattern violations

4. **Auto-Rebuild Packages** (if examples/memories updated)
   - Detect changes in `.serena/memories/` or `examples/`
   - Run `.ce/build-and-distribute.sh`
   - Copy packages to `.ce/` directory
   - Report package sizes

5. **Generate Report**
   - Per-PRP update status
   - Aggregated drift summary
   - Package rebuild status
   - Next steps recommendations

## Examples

```bash
# Update all PRPs in batches 34 and 36
/batch-update-context prp 34 36

# Update specific PRPs
/batch-update-context --prp PRPs/executed/PRP-34.1.1-core-blending-framework.md --prp PRPs/feature-requests/PRP-36.1.1-core-module.md

# Update all PRPs in batch 34
/batch-update-context prp 34
```

## Workflow

**Step 1: Discover**
```
Scanning for batch 34 PRPs...
Found 12 PRPs:
  - PRP-34.1.1 (executed)
  - PRP-34.2.1 (executed)
  ... 10 more
```

**Step 2: Update Each PRP**
```
Updating PRP-34.1.1...
  ✅ CE updated (implementation verified)
  ⚠️ Serena unavailable

Updating PRP-34.2.1...
  ✅ CE updated
  ✅ Serena updated
```

**Step 3: Aggregate Results**
```
📊 Batch Update Summary
  PRPs scanned: 12
  PRPs updated: 12
  CE verified: 10
  Serena verified: 8

  Drift score: 4.5% (✅ HEALTHY)
  Violations: 3
```

**Step 4: Check for Framework Changes**
```
🔍 Checking for framework file changes...
  ✅ examples/ updated (3 files)
  ✅ memories/ updated (2 files)

📦 Rebuilding packages...
```

**Step 5: Report**
```
✅ Batch update complete
  📄 Detailed report: tmp/ce/batch-update-34-36-report.md
  📦 Packages rebuilt (1.1MB total)
```

## Package Rebuild Logic

Automatically rebuilds repomix packages when:
- Any file in `.serena/memories/` modified
- Any file in `examples/` modified
- User explicitly requests with `--rebuild` flag

**Rebuild Steps**:
1. Run `.ce/build-and-distribute.sh`
2. Copy `ce-32/builds/*.xml` to `.ce/`
3. Verify package integrity
4. Report new package sizes

## Characteristics vs Other Batch Commands

**vs batch-gen-prp**:
- No parallel subagents (sequential updates)
- Read-only operations (no code generation)
- Focuses on verification not creation

**vs batch-exe-prp**:
- No git branches (no code changes)
- No worktrees needed
- Aggregates drift across PRPs

**Unique Features**:
- Auto-detects framework file changes
- Rebuilds packages automatically
- Cross-PRP drift analysis
- Bulk YAML header updates

## Output Files

- `tmp/ce/batch-update-<batch-ids>-report.md` - Detailed report
- `tmp/ce/batch-update-<batch-ids>-drift.json` - Drift data (JSON)
- `.ce/ce-infrastructure.xml` - Rebuilt package (if triggered)
- `.ce/ce-workflow-docs.xml` - Rebuilt package (if triggered)

## Error Handling

**Graceful degradation**:
- Serena unavailable → Continue with CE-only updates
- Package rebuild fails → Report error, continue
- Individual PRP update fails → Skip and continue with others

**Exit codes**:
- 0: All updates successful
- 1: Some updates failed (partial success)
- 2: Critical error (no updates completed)

## Related Commands

- `/update-context` - Update single PRP
- `/batch-gen-prp` - Generate batch of PRPs
- `/batch-exe-prp` - Execute batch of PRPs

## Notes

- Updates are sequential (no parallelization needed for verification)
- Package rebuild adds ~10-15 seconds
- Drift analysis more comprehensive across batch than single PRP
- YAML header updates are atomic (per-file)

**Goal**: Maintain context sync across batches of related PRPs with automatic framework packaging.
