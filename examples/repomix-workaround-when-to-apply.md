# Repomix Workaround: When to Apply

## Symptom Recognition

**Apply this workaround when:**

1. **File Count Mismatch**:
   ```bash
   # Repomix reports N files collected
   npx repomix --config .ce/repomix-profile-infrastructure.json
   # Output: "Total Files: 148 files"

   # But XML contains fewer files
   grep -c '<file path=' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
   # Output: 143

   # Diff: 148 - 143 = 5 files missing
   ```

2. **Verbose Output Shows Processing**:
   ```bash
   npx repomix --config .ce/repomix-profile-infrastructure.json --verbose 2>&1 | grep "nlp"
   # Shows: "Reading file: tools/ce/nlp/cache.py"
   # Shows: "Processing file: tools/ce/nlp/cache.py"
   # But file not in final XML
   ```

3. **Glob Patterns Match But Files Missing**:
   ```bash
   npx glob "tools/ce/**/*.py" | grep nlp
   # Shows: tools/ce/nlp/__init__.py, tools/ce/nlp/cache.py, etc.

   grep 'tools/ce/nlp' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
   # Shows: (empty - files not in XML)
   ```

## Root Cause

**Repomix v1.9.1 bug**: Collects files but silently drops some during XML generation phase.

**NOT caused by**:
- File permissions (644 vs 600)
- Glob pattern syntax
- Gitignore/repomixignore rules
- File encoding or size
- Security checks (even when disabled)

## Solution

**Automated** (preferred):
```bash
# Integrated into build process
.ce/build-and-distribute.sh
```

**Manual**:
```bash
python3 .ce/repomix-patch-missing-files.py
```

## Verification

**Before workaround**:
```bash
grep -c '<file path=' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
# Output: 143
grep '<file path="tools/ce/nlp' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
# Output: (empty)
```

**After workaround**:
```bash
grep -c '<file path=' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
# Output: 149 (143 + 6 injected)
grep '<file path="tools/ce/nlp' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml
# Output: <file path="tools/ce/nlp/__init__.py">
#         <file path="tools/ce/nlp/cache.py">
#         ... (all 4 nlp files)
```

## When NOT to Apply

- Repomix version ≠ 1.9.1 (bug may be fixed in newer versions)
- File count matches (collected = output)
- Missing files are legitimately ignored (check .gitignore, repomixignore)
- Files don't exist in repository

## Maintenance

**⚠️ IMPORTANT**: If you relocate or rename files in `tools/ce/nlp/` or `tools/ce/vacuum_strategies/`, update:

1. `.ce/repomix-patch-missing-files.py` - Update `MISSING_FILES` list
2. `.ce/repomix-profile-infrastructure.json` - Update `include` paths

**Example**: Moving `tools/ce/nlp/` to `tools/ce/text_processing/nlp/`
```python
# Update .ce/repomix-patch-missing-files.py
MISSING_FILES = [
    "tools/ce/text_processing/nlp/__init__.py",  # Updated path
    "tools/ce/text_processing/nlp/cache.py",      # Updated path
    # ...
]
```

```json
// Update .ce/repomix-profile-infrastructure.json
{
  "include": [
    "tools/ce/text_processing/nlp/__init__.py",  // Updated path
    "tools/ce/text_processing/nlp/cache.py"      // Updated path
  ]
}
```

## Alternative: Upgrade Repomix

**Long-term solution**: Upgrade to repomix version that fixes this bug.

```bash
# Check current version
npx repomix --version
# Output: 1.9.1

# Upgrade (when fix available)
npm install -g repomix@latest

# Test if bug is fixed
npx repomix --config .ce/repomix-profile-infrastructure.json
grep -c '<file path=' syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml

# If count matches (148 == 148), remove workaround from build-and-distribute.sh
```

## Related Documentation

- [.serena/memories/repomix-glob-pattern-file-permissions-issue.md](../.serena/memories/repomix-glob-pattern-file-permissions-issue.md) - Full troubleshooting process
- [.ce/repomix-patch-missing-files.py](../.ce/repomix-patch-missing-files.py) - Patch script implementation
- [.ce/build-and-distribute.sh](../.ce/build-and-distribute.sh) - Automated build process
