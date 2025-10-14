# Update Context

Sync Context Engineering (CE) and Serena knowledge systems with actual codebase implementation state.

## Usage
```bash
/update-context [--prp <prp-file>]
```

## Parameters
- `--prp <prp-file>`: Optional. Target specific PRP file for sync (path relative to project root)

## What it does

Universal system hygiene command that maintains bidirectional sync between knowledge systems and codebase:

1. **Scans PRPs**
   - Universal mode: All PRPs in `PRPs/feature-requests/` and `PRPs/executed/`
   - Targeted mode: Single PRP specified with `--prp` flag

2. **Updates YAML Headers**
   - Sets `context_sync.ce_updated` flag (based on implementation verification)
   - Sets `context_sync.serena_updated` flag (if Serena MCP available)
   - Adds `last_sync` timestamp
   - Updates `updated_by` attribution

3. **Verifies Implementations**
   - Extracts expected functions/classes from PRP content
   - Cross-references with actual codebase via Serena MCP
   - Marks `ce_updated=true` only if ALL expected implementations found

4. **Manages PRP Status**
   - Auto-transitions PRPs from `status: new` → `status: executed` when verified
   - Moves files from `PRPs/feature-requests/` → `PRPs/executed/` atomically
   - Identifies deprecated PRPs for archival

5. **Detects Pattern Drift**
   - **Code Violations**: Scans codebase for violations of documented patterns (examples/)
   - **Missing Examples**: Identifies critical PRPs without corresponding pattern documentation
   - Generates structured drift report with solution proposals
   - Saves report to `.ce/drift-report.md`

6. **Reports Results**
   - Summary statistics (PRPs scanned/updated/moved)
   - Drift score and violation count
   - Clear logging of all operations

## Examples

```bash
# Sync all PRPs with codebase
/update-context

# Sync specific PRP only
/update-context --prp PRPs/executed/PRP-13-production-hardening.md

# Typical workflow
# 1. Implement feature
# 2. Run /update-context to verify and sync
# 3. Review drift report if generated
# 4. Fix violations or create missing examples
```

## When to Use

**Run /update-context after:**
- Completing PRP implementation
- Significant codebase refactoring
- Adding new examples/ patterns
- Weekly system hygiene (prevent drift accumulation)

**Run with --prp flag when:**
- Testing single PRP verification
- Debugging context sync issues
- Quick spot-check after small change

## Drift Detection

When drift is detected, generates `.ce/drift-report.md` with:

**Part 1: Code Violating Documented Patterns**
- Error handling violations (bare except, missing troubleshooting)
- Naming convention violations (versioned suffixes)
- KISS violations (overcomplicated implementations)

**Part 2: Missing Pattern Documentation**
- Critical PRPs (complexity ≥ medium) without examples/
- Suggested example paths
- Rationale for documentation need

**Each violation includes:**
- File location
- Specific issue
- Pattern reference
- Proposed solution

## Graceful Degradation

- **Serena MCP unavailable**: Continues with warnings, sets `serena_updated=false`
- **examples/ missing**: Skips drift detection with info log
- **Invalid YAML**: Skips file with warning, continues with others
- **Permission errors**: Raises error with troubleshooting guidance (no silent failures)

## YAML Header Updates

Example before:
```yaml
status: new
context_sync:
  ce_updated: false
  serena_updated: false
```

Example after:
```yaml
status: executed
context_sync:
  ce_updated: true
  serena_updated: true
  last_sync: 2025-10-14T17:00:00Z
updated_by: update-context-command
```

## Success Criteria

✅ All PRPs scanned successfully
✅ YAML headers updated accurately
✅ Status transitions executed correctly
✅ Files moved atomically (no data loss)
✅ Drift detection identifies real violations
✅ No false positives in pattern checks

## Related Commands

- `/generate-prp` - Create new PRP blueprint
- `/execute-prp` - Implement PRP feature
- `/peer-review` - Review PRP or execution
- `/validate-prp-system` - Comprehensive system validation

**Goal:** Prevent documentation rot through automated sync verification and drift detection.
