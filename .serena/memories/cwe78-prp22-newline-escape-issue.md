---
type: regular
category: troubleshooting
tags: [security, cwe78, fix]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# CWE-78 PRP-22: Critical Newline Escape Sequence Issue & Solution

## Problem Encountered

When using `mcp__serena__replace_regex` tool to insert f-strings with newline escape sequences, the tool was interpreting `\n` as actual newline characters in the source code, creating syntax errors.

### Symptoms
- **Error**: `SyntaxError: unterminated f-string literal (detected at line 76)`
- **Root Cause**: F-strings with literal newlines instead of `\n` escape sequences
- **Example Failure**:
```python
# WRONG - tool replaced with literal newline
raise ValueError(
    f"Empty command provided
"  # <-- LITERAL NEWLINE, breaks syntax
    "🔧 Troubleshooting: ..."
)
```

## Solution: Write Direct > Regex Replace

### When to Use Each Approach

**✅ USE `write_file()` FOR**:
- Multi-line functions with f-strings
- Complex error messages with escape sequences
- Any code with newlines in string literals
- Functions over ~30 lines

**⚠️ AVOID `replace_regex()` FOR**:
- F-strings with `\n` sequences (tool misinterprets them)
- Complex multi-line replacements
- Code with escape sequences or special characters
- When small tweaks to larger functions needed

### Workaround Pattern Used in PRP-22

1. **Identify problem**: Multiple f-strings with `\n` needed in core.py
2. **Create clean file**: Made `core_fixed.py` with correct syntax
3. **Replace entire file**: Used `write_file()` to replace core.py with corrected version
4. **Verify syntax**: Ran imports to verify no syntax errors

**Result**: Successfully eliminated syntax issues

## Prevention for Future PRPs

### For Serena Tool Users

When editing Python files with f-strings containing escape sequences:

```python
# ❌ DON'T use replace_regex for this
raise TimeoutError(
    f"Command timed out after {timeout}s\n"  # Tool breaks this
    f"🔧 Troubleshooting: Check for hanging process"
)

# ✅ DO use write_file() or read file completely, edit, write back
# Or use simpler find_symbol + replace_symbol_body approach
```

### Alternative: Symbol-Based Editing

For functions with complex f-strings:
1. Use `find_symbol(name_path, include_body=True)`
2. Read full function body
3. Edit the complete function
4. Use `replace_symbol_body(name_path, new_body)` 

**Advantage**: Tool handles escape sequences correctly within symbol replacement

### Quick Reference

| Task | Best Tool | Why |
|------|-----------|-----|
| F-string with `\n` | `write_file()` | Preserves escape sequences |
| Single line replacement | `replace_regex()` | Fast, precise |
| Function with escapes | `replace_symbol_body()` | Handles context properly |
| Multi-line with escapes | `write_file()` | Full control |

## Files Affected in PRP-22

- `tools/ce/core.py`: 5 functions with f-strings containing `\n`
- Issue occurred with runs of `replace_regex()` attempting to fix newline issues
- **Resolution**: Created `core_fixed.py` with proper syntax, then `write_file()` to replace

## For Next Similar PRP

If replacing code with many f-strings:
1. Prepare clean version in memory/file first
2. Use `write_file()` for entire modules
3. Or use `replace_symbol_body()` for individual functions
4. Avoid regex approach for escape-heavy code

## Test Coverage for This Issue

- `tests/test_security.py::test_run_cmd_rejects_command_chaining`: Tests f-string error messages
- All 38 security tests verify proper error message formatting
- No test failures related to syntax after using `write_file()` approach
