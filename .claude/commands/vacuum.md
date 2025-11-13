# Vacuum

Clean up project noise: temp files, obsolete docs, unreferenced code, orphaned tests, dead links, commented code blocks.

## Usage
```bash
/vacuum [--path DIR] [--execute|--force|--auto|--nuclear] [--exclude-strategy STRATEGY] [--min-confidence N]
```

## Modes

**Default (dry-run)**: Generate report only, no deletions
```bash
/vacuum
```

**Scoped cleanup**: Clean specific directory only
```bash
/vacuum --path syntropy-mcp
/vacuum --path tools/ce --execute
```

**Execute mode**: Delete HIGH confidence items only (100% safe: temp files, backups)
```bash
/vacuum --execute
```

**Force/Auto mode**: Delete HIGH + MEDIUM confidence items (includes obsolete docs, orphan tests, dead links)
```bash
/vacuum --force
# or
/vacuum --auto
```

**Nuclear mode**: Delete ALL items including LOW confidence (unreferenced code, commented blocks) - requires confirmation
```bash
/vacuum --nuclear
```

## Parameters

- `--path DIR`: Directory to scan (relative to project root). Defaults to entire project
- `--execute`: Delete HIGH confidence items (≥100%)
- `--force`: Delete MEDIUM + HIGH confidence items (≥60%)
- `--auto`: Automatically delete MEDIUM + HIGH confidence items (same as --force)
- `--nuclear`: Delete ALL items including LOW confidence (<60%) - requires "yes" confirmation
- `--min-confidence N`: Set custom confidence threshold (0-100)
- `--exclude-strategy STRATEGY`: Skip specific strategy (use multiple times for multiple strategies)

## Strategies

### 1. temp-files (HIGH: 100%)
- `*.pyc`, `__pycache__/`, `.DS_Store`, `*.swp`, `.pytest_cache/`, `*.log`, `*.tmp`
- **Auto-delete with --execute**

### 2. backup-files (HIGH: 100%)
- `*.bak`, `*~`, `*.orig`, `*.rej` (git merge artifacts)
- **Auto-delete with --execute**

### 3. obsolete-docs (MEDIUM: 70%)
**Filename Patterns**:
- Versioned docs: `*-v1.md`, `*-old.md`, `*-deprecated.md`
- Temporary analysis docs: `ANALYSIS-*`, `CHANGELIST-*`, `REPORT-*`, `IMPLEMENTATION-*`, `DEPLOYMENT*`
- Planning docs: `*-PLAN.md`, `*-REPLAN.md`, `*-SUMMARY-*.md`, `*_SOLUTION.md`
- Root-level all-caps files (e.g., `VERSION` - with exceptions for LICENSE, MAKEFILE)

**Content Analysis** (reads first 20 lines):
- Status markers: "**Status**: PENDING", "**Status**: READY FOR EXECUTION"
- Execution tracking: "**Completed**:", "**Remaining Work**:"
- Planning markers: "## 📋 EXECUTIVE SUMMARY", "## 🎯 EXECUTION SUMMARY"
- Solution patterns: "**Problem**:", "**Solution**:", "## Solution Options"
- Date indicators: "**Date**: 2025-10-*" (time-bound docs)
- Workflow markers: "**Workflow:**", "Source Plan:", "This plan addresses"

**Protected Patterns**:
- `.ce/**`, `.claude/**`, `.serena/**` (framework/config dirs)
- `syntropy-mcp/**` (MCP server)
- `tmp/finalizing/**` (work-in-progress)
- `PRPs/**/*.md` with YAML headers (real PRPs)

- **Delete with --force/--auto**

### 4. orphan-tests (MEDIUM: 60%)
- `test_foo.py` where `foo.py` doesn't exist
- **Delete with --force/--auto**

### 5. unreferenced-code (LOW: 40%)
- Python files where:
  - ALL definitions (functions/classes) are unreferenced elsewhere
  - AND the file itself is not imported by any other module
- Uses Serena MCP for symbol analysis (~15s)
- **Manual review only** (use --nuclear with caution)
- Common false positives: CLI entry points, scripts meant to be run directly

### 6. commented-code (LOW: 30%)
- Commented code blocks ≥20 lines
- Excludes docstrings, license headers, teaching examples
- **Manual review only**

## Safety Mechanisms

**NEVER_DELETE Paths**:
- `.ce/**` - Framework boilerplate
- `.claude/**` - Claude Code configuration (all commands, settings)
- `.serena/**` - Serena memories and configuration
- `syntropy-mcp/**` - Syntropy MCP server directory
- `tmp/**` files < 2 days old - Recent work-in-progress (older files deleted)
- `PRPs/**/*.md` - All PRP files with YAML headers (managed by update-context)
- `pyproject.toml`, `README.md`, `CLAUDE.md`, `WARP.md`, `VERSION`
- `examples/**` - Pattern documentation
- `**/__init__.py`, `**/cli.py`, `**/__main__.py` - Entry points

**Note**: Analysis files (CHANGELIST-*, ANALYSIS-*, REPORT-*, IMPLEMENTATION-*) are **NOT** protected and can be cleaned up if obsolete, as they're temporary artifacts of PRP execution.

**Protection Rules**:
1. Files modified in last 30 days get lower confidence scores
2. Files referenced in markdown docs are flagged
3. Files with git activity are protected
4. Dry-run by default (explicit --execute required)

## Output

**Report**: `.ce/vacuum-report.md`

Sections:
1. **Summary**: Candidate count, bytes reclaimable, confidence breakdown
2. **HIGH Confidence**: Safe to delete (path, reason, size, last modified)
3. **MEDIUM Confidence**: Review recommended (path, reason, confidence, git history)
4. **LOW Confidence**: Manual verification required (path, reason, confidence, references)

## Examples

**Basic cleanup** (temp files + backups):
```bash
/vacuum --execute
```

**Deep cleanup** (temp files + backups + obsolete docs + orphan tests):
```bash
/vacuum --force
```

**Skip slow strategy**:
```bash
/vacuum --exclude-strategy unreferenced-code
```

**Custom threshold** (only delete 80%+ confidence):
```bash
/vacuum --execute --min-confidence 80
```

**Review only** (generate report without deleting):
```bash
/vacuum
# Or explicitly:
cd tools && uv run ce vacuum --dry-run
```

## Exit Codes

- `0`: No candidates found (clean)
- `1`: Candidates found (check report)
- `2`: Error occurred

## Performance

**Parallel execution** for fast strategies (temp-files, backup-files, obsolete-docs, orphan-tests, commented-code):
- ~5 seconds total

**Sequential execution** for slow strategy (unreferenced-code via Serena):
- ~15 seconds

**Total time**: ~20 seconds for all strategies

**Skip slow strategy** for quick cleanup:
```bash
/vacuum --execute --exclude-strategy unreferenced-code
# ~5 seconds
```

## Workflow Integration

**After /update-context**:
```bash
# 1. Sync context
/update-context

# 2. Clean up project
/vacuum --execute

# 3. Review report
cat .ce/vacuum-report.md
```

**Before commits**:
```bash
# Clean temp files before committing
/vacuum --execute
git add .
git commit -m "Implement feature X"
```

## Troubleshooting

**"Strategy not found"**: Check spelling, available strategies:
- `temp-files`, `backup-files`, `obsolete-docs`, `unreferenced-code`, `orphan-tests`, `commented-code`

**"Serena unavailable"**: unreferenced-code strategy will skip gracefully, other strategies run normally

**"Permission denied"**: File in use or protected by OS - check .ce/vacuum-report.md for details

**False positive**: File flagged incorrectly? Add to PROTECTED_PATTERNS in `tools/ce/vacuum_strategies/base.py` or use lower confidence threshold

## Advanced Usage

**Review LOW confidence candidates** before nuclear mode:
```bash
# 1. Generate report
/vacuum

# 2. Review .ce/vacuum-report.md LOW confidence section

# 3. If satisfied, run nuclear mode
/vacuum --nuclear
# (type "yes" to confirm)
```

**Chain with git commit**:
```bash
/vacuum --execute && git add . && git commit -m "Clean up project noise"
```

## Goal

Maintain clean project state by identifying and safely removing noise while preserving all vital content through confidence-based safety mechanisms.
