---
type: regular
category: troubleshooting
tags: [repomix, glob-patterns, file-permissions, build-tools, silent-failures]
created: "2025-11-18"
updated: "2025-11-18"
---

# Repomix Glob Pattern Issue: Files Collected But Not Output

## Problem

When using Repomix v1.9.1 with `tools/ce/**/*.py` pattern, some files (tools/ce/nlp/*.py, tools/ce/vacuum_strategies/llm_analyzer.py, etc.) were collected (147 files reported) but not included in final XML output (only 143 files).

## Root Cause

**File permissions mismatch**: NLP files had restrictive permissions (`600` owner-only) while other files had standard permissions (`644` world-readable).

```bash
# Problem files:
-rw-------@ tools/ce/nlp/cache.py          # 600 permissions
-rw-------@ tools/ce/nlp/normalizer.py      # 600 permissions
-rw-------@ tools/ce/nlp/similarity.py      # 600 permissions

# Normal files:
-rw-r--r--@ tools/ce/blend.py              # 644 permissions
-rw-r--r--@ tools/ce/core.py                # 644 permissions
```

**Why it matters**: Repomix's security check phase processes files but silently drops those with restrictive permissions during XML generation.

## Symptoms

1. ✅ Repomix reports collecting N files
2. ❌ Only N-X files in final XML output
3. ✅ Glob patterns match files (`npx glob` confirms)
4. ✅ Files are git-tracked
5. ❌ Disabling security checks doesn't help
6. ❌ Adding explicit patterns doesn't help

## Solution (FAILED - See Workaround)

```bash
# Fix file permissions (necessary but not sufficient)
chmod 644 tools/ce/nlp/*.py

# Change glob patterns to explicit paths (DID NOT WORK)
# Repomix v1.9.1 bug: Processes files but doesn't write them to XML
```

## Root Cause (Confirmed)

**Repomix v1.9.1 bug with specific files:**

- Collects 148 files (verbose output shows "Reading file", "Processing file")
- Only outputs 143 files to XML
- Missing files are silently dropped AFTER processing
- NOT related to: permissions, encoding, file size, glob patterns, or ignore rules

**Affected files** (6 total):

- `tools/ce/nlp/__init__.py`
- `tools/ce/nlp/cache.py`
- `tools/ce/nlp/normalizer.py`
- `tools/ce/nlp/similarity.py`
- `tools/ce/vacuum_strategies/llm_analyzer.py`
- `tools/ce/vacuum_strategies/prp_lifecycle_docs.py`

## Workaround (Manual Injection)

Created patch script `.ce/repomix-patch-missing-files.py` that manually injects missing files into XML after repomix generation.

**Auto-applied during build**:
```bash
.ce/build-and-distribute.sh  # Auto-runs patch script after repomix
```

**Manual execution** (if needed):
```bash
python3 .ce/repomix-patch-missing-files.py
```

**Result**: 149 files in XML (143 from repomix + 6 manually injected)

## Verification

```bash
# Test glob pattern works
npx glob "tools/ce/**/*.py" | grep nlp

# Test repomix with isolated config
npx repomix --config test-config.json  # Should include all files

# Verify XML output
grep -c "<file path=" syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
```

## Maintenance Note

**⚠️ IMPORTANT:** If NLP or vacuum_strategies files are **relocated or renamed**, update:

1. `.ce/repomix-patch-missing-files.sh` - Update `MISSING_FILES` array
2. `.ce/repomix-profile-infrastructure.json` - Update `include` paths

Otherwise files will be missing from infrastructure package.

## Prevention

1. Use consistent file permissions across codebase (`644` for source files)
2. Check `git diff --stat` after regenerating packages to detect missing files
3. Compare collected vs output file counts in Repomix summary
4. Test isolated configs when debugging glob pattern issues

## Related Issues

- Repomix GitHub Issue #105: Glob ignore patterns
- Repomix GitHub Issue #443: Ignore globbing pattern intuition
- File permissions can affect build tools silently

## Debugging Process Lessons

### What Worked
- Testing with isolated config (confirmed files work in isolation)
- Using `npx glob` to verify pattern matching
- Checking file permissions with `ls -l`
- Comparing file counts (collected vs output)

### What Didn't Work
- Disabling security checks
- Adding explicit patterns alongside wildcards
- Changing pattern syntax variations

### Key Insight
When Repomix reports "N files collected" but XML contains "N-X files", check file permissions - not glob patterns.
