# Tool Misuse Scan Command

**Purpose**: Detect and categorize tool misuse patterns in Claude Code sessions

**Target**: AI agents working with Context Engineering codebase

**Last Updated**: 2025-10-17

---

## Command Usage

```bash
/tools-misuse-scan
```

**What it does**:
- Scans conversation history for denied tool errors
- Categorizes into: (1) Bash anti-patterns, (2) Denied tools without substitutes
- Provides remediation suggestions with proper tool alternatives
- Generates structured report for debugging and improvement

---

## Detection Patterns

### Category 1: Bash Anti-patterns

**Pattern**: Bash text processing operations that should use designated tools

**Detection Rules**:
```regex
# Bash head/tail with file piping
Bash\(.*\|\s*head\s+-\d+
Bash\(.*\|\s*tail\s+-\d+

# Bash grep with file piping
Bash\(.*\|\s*grep\s+

# Direct head/tail commands
Bash\(head\s+-\d+
Bash\(tail\s+-\d+

# Python subprocess without uv
Bash\(python3?\s+
Bash\(python3?\s+-m
```

**Remediation Mappings**:
| Anti-pattern | Correct Tool | Example |
|-------------|--------------|---------|
| `Bash("cat file \| head -50")` | `Read(file, limit=50)` | Read first 50 lines |
| `Bash("cat file \| tail -100")` | `Read(file, offset=-100)` | Read last 100 lines |
| `Bash("grep pattern file")` | `shell_utils.grep_text()` | Search with context |
| `Bash("python script.py")` | `uv run python script.py` | Proper env management |

### Category 2: Denied Tools

**Pattern**: MCP tools explicitly denied with no direct substitute

**Detection Rules**:
```regex
# Tool denied error messages
has been denied
permission denied.*mcp__
Tool.*not available
```

**Known Denied Tools**:
| Tool | Reason | Alternative |
|------|--------|-------------|
| `mcp__serena__replace_symbol_body` | Permission restricted | `mcp__serena__replace_regex()` or `mcp__filesystem__edit_file()` |

---

## Analysis Workflow

### Step 1: Error Collection

Scan conversation for:
- "has been denied" messages
- "permission denied" errors
- Failed tool invocations with error responses

### Step 2: Categorization

**Group 1: Bash Misuse**
- Extract Bash command from error context
- Match against anti-pattern regex
- Identify correct tool replacement
- Generate remediation suggestion

**Group 2: Denied Tools**
- Extract tool name from error message
- Check known alternatives table
- Provide workaround guidance

### Step 3: Report Generation

**Output Format**:
```markdown
## Tool Misuse Analysis Report

**Session**: {timestamp}
**Total Errors Found**: {count}

### Category 1: Bash Anti-patterns ({count})

1. **Error**: Bash("cat file | head -50")
   - **Issue**: Text processing with piping
   - **Remedy**: Use `Read(file, limit=50)`
   - **Location**: Message #{n}
   - **Performance Impact**: 10-50x slower (subprocess overhead)

### Category 2: Denied Tools ({count})

1. **Error**: mcp__serena__replace_symbol_body
   - **Issue**: Permission denied, no direct substitute
   - **Remedy**: Use `mcp__serena__replace_regex()` for targeted edits
   - **Location**: Message #{n}
   - **Documentation**: See .serena/memories/serena-mcp-tool-restrictions.md
```

---

## Implementation Instructions

When running this command:

1. **Scan Phase** (2 passes for thoroughness):
   - Pass 1: Search for "denied" and "permission" keywords
   - Pass 2: Validate each error against detection patterns

2. **Categorization Phase**:
   - Apply regex patterns to extract tool names and commands
   - Match against known anti-patterns and denied tools
   - Generate remediation suggestions

3. **Validation Phase**:
   - Cross-reference with `examples/tool-usage-patterns.md`
   - Verify remediation suggestions are accurate
   - Check that alternatives exist and are allowed

4. **Report Phase**:
   - Generate structured markdown report
   - Include location references (message numbers)
   - Add performance impact notes where applicable
   - Link to relevant documentation

---

## Quality Checks

**Before finalizing report**:

- ✅ All errors categorized correctly
- ✅ Remediation suggestions are actionable
- ✅ Alternatives verified in tool-usage-patterns.md
- ✅ Location references are accurate
- ✅ No false positives (legitimate tool uses)
- ✅ Performance impact documented (bash subprocess overhead)

---

## Expected Output Example

```markdown
## Tool Misuse Analysis Report

**Session**: 2025-10-17
**Total Errors Found**: 7

### Category 1: Bash Anti-patterns (6 errors)

1. **Error**: Bash("head -50 file")
   - **Issue**: Direct head command without tool
   - **Remedy**: Use `Read(file, limit=50)` or `shell_utils.head(file, 50)`
   - **Performance**: 10-50x faster with Python utilities

2. **Error**: Bash("tail -100 file")
   - **Issue**: Direct tail command without tool
   - **Remedy**: Use `Read(file, offset=-100)` or `shell_utils.tail(file, 100)`
   - **Performance**: 10-50x faster with Python utilities

3. **Error**: Bash("grep pattern file")
   - **Issue**: Text search with subprocess
   - **Remedy**: Use `shell_utils.grep_text(pattern, file_content)`
   - **Performance**: No subprocess fork overhead

4-6. [Similar patterns...]

### Category 2: Denied Tools (1 error)

1. **Error**: mcp__serena__replace_symbol_body
   - **Issue**: Permission denied for symbol mutation
   - **Remedy**: Use `mcp__serena__replace_regex()` for targeted edits
   - **Alternative**: Use `mcp__filesystem__edit_file()` for line-based changes
   - **Documentation**: .serena/memories/serena-mcp-tool-restrictions.md

---

## Recommendations

1. **Update Documentation**: Ensure examples/tool-usage-patterns.md covers all anti-patterns
2. **Add Pre-commit Validation**: Consider tool usage linting in CI/CD
3. **Agent Training**: Review remediation patterns with agents
4. **Performance Monitoring**: Track subprocess overhead reduction after fixes
```

---

## References

- **Tool Usage Patterns**: `examples/tool-usage-patterns.md`
- **Serena MCP Restrictions**: `.serena/memories/serena-mcp-tool-restrictions.md`
- **CLAUDE.md**: Text processing anti-patterns section
- **shell_utils Module**: `tools/ce/shell_utils.py`

---

## Notes

- This command is retrospective analysis, not real-time enforcement
- Helps identify patterns for documentation updates
- Useful for agent training and tool usage improvement
- Run periodically after major development sessions
