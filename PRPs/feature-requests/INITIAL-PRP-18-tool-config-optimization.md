---
context_sync:
  ce_updated: true
  last_sync: '2025-10-17T11:29:21.579581+00:00'
  serena_updated: false
updated: '2025-10-17T11:29:21.579584+00:00'
updated_by: update-context-command
---

# INITIAL: MCP Tool Configuration & Usage Mapping Optimization

## FEATURE

Optimize tool configuration to reduce context overhead by 30-50% and accelerate agent tool selection through:

1. **Granular MCP tool permissions** - Explicit allow/deny lists at tool function level
2. **Tool usage mapping guide** - Quick reference for agents to select correct tools
3. **Python-based bash replacements** - Efficient alternatives to bash utilities (cat, grep, awk, sed)

### Current Problems

**Context bloat**:
- Wildcard permissions load ALL tools from MCP servers into context
- 45+ broad permissions in `.claude/settings.local.json`
- No deny list = unused tools consume context space

**Query tree complexity**:
- Agent must evaluate 100+ tools for each decision
- No usage guide = trial-and-error tool selection
- Slower decision-making due to large tool inventory

**Bash inefficiency**:
- Subprocess overhead for simple text operations (cat, grep, awk)
- 45+ bash commands in allow list (most replaceable with Python)
- No shell utilities module for common operations

### Solution

**1. MCP Tool Audit & Granular Configuration**
- Grep codebase for actual MCP tool usage (`mcp__serena__*`, etc.)
- Create explicit allow list: ~31 essential tools only
- Create deny list: 50+ unused tools (efficiency optimization)
- Result: Query tree reduced by 60-70%

**2. Tool Usage Mapping Guide**
- `examples/tool-usage-patterns.md` - Quick reference for tool selection
- `.serena/memories/tool-usage-guide.md` - Copy for agent instant lookup
- Covers: code navigation, file ops, text processing, version control
- Eliminates trial-and-error tool selection

**3. Python Shell Utilities Module**
- New: `tools/ce/shell_utils.py` with 8 functions
- Replacements: grep_text(), head(), tail(), find_files(), count_lines()
- AWK equivalents: extract_fields(), sum_column(), filter_and_extract()
- Refactor ce modules to use Python instead of bash

### Expected Outcomes

- **Context reduction**: 30-50% (measured in tokens)
- **Query tree simplification**: 60-70% fewer tools to evaluate
- **Bash reduction**: From 45+ commands to 3 (git, uv only)
- **Performance**: Python utilities faster than subprocess calls
- **Agent clarity**: Tool mapping guide accelerates selection

---

## EXAMPLES

### Example 1: Granular MCP Configuration

**Current** (`.claude/settings.local.json`):
```json
{
  "permissions": {
    "allow": [
      "mcp__serena__*",  // Loads ALL 30+ serena tools
      "Bash(cat:*)",     // Subprocess for simple file read
      "Bash(grep:*)"     // Subprocess for regex search
    ]
  }
}
```

**Optimized**:
```json
{
  "permissions": {
    "allow": [
      // Explicit serena tools (10 used out of 30)
      "mcp__serena__find_symbol",
      "mcp__serena__get_symbols_overview",
      "mcp__serena__search_for_pattern",
      "mcp__serena__list_dir",
      "mcp__serena__read_file",
      "mcp__serena__activate_project",
      "mcp__serena__find_referencing_symbols",
      "mcp__serena__insert_after_symbol",
      "mcp__serena__replace_regex",
      "mcp__serena__execute_shell_command",

      // Only essential bash (3 external tools)
      "Bash(git:*)",
      "Bash(uv run:*)",
      "Bash(uv add:*)"
    ],
    "deny": [
      // 20 unused serena tools
      "mcp__serena__delete_memory",
      "mcp__serena__rename_symbol",
      // ... 18 more

      // Bash replaceable with Python
      "Bash(cat:*)",
      "Bash(grep:*)",
      "Bash(awk:*)",
      "Bash(sed:*)"
    ]
  }
}
```

### Example 2: Tool Usage Mapping Guide

**File**: `examples/tool-usage-patterns.md`

```markdown
# Tool Usage Patterns - Quick Reference

## Task: "Find a function definition"
**USE**: `mcp__serena__find_symbol`
```python
find_symbol(name_path="authenticate_user", include_body=True)
```

## Task: "Search for pattern in codebase"
**USE**: `mcp__serena__search_for_pattern`
```python
search_for_pattern(pattern="async def.*authenticate", path="src/")
```

## Task: "Read file contents"
**USE**: `mcp__filesystem__read_text_file` (non-code) OR `mcp__serena__read_file` (code)

## Task: "Extract fields from text"
**USE**: Python `shell_utils.extract_fields()` (NOT bash awk)
```python
from ce.shell_utils import extract_fields
fields = extract_fields(text, field_indices=[1, 3], delimiter=":")
```

## Anti-Patterns (DON'T USE)
❌ Bash(cat file.py) → Use filesystem__read_text_file
❌ Bash(awk '{print $1}') → Use shell_utils.extract_fields()
✅ Bash(git status) → OK (external tool)
```

### Example 3: Python Shell Utilities

**File**: `tools/ce/shell_utils.py`

```python
def extract_fields(
    text: str,
    field_indices: List[int],
    delimiter: Optional[str] = None
) -> List[List[str]]:
    """Extract specific fields from each line.

    Replaces: awk '{print $1, $3}'
    """
    lines = text.strip().split('\n')
    results = []
    for line in lines:
        fields = line.split(delimiter) if delimiter else line.split()
        extracted = [fields[i-1] for i in field_indices if i <= len(fields)]
        results.append(extracted)
    return results

def sum_column(text: str, column: int, delimiter: Optional[str] = None) -> float:
    """Sum numeric column.

    Replaces: awk '{sum += $1} END {print sum}'
    """
    lines = text.strip().split('\n')
    total = 0.0
    for line in lines:
        fields = line.split(delimiter) if delimiter else line.split()
        if column <= len(fields):
            try:
                total += float(fields[column-1])
            except ValueError:
                continue
    return total
```

**Usage in ce modules**:
```python
# Before (tools/ce/execute.py)
result = run_cmd("awk '{print $1}' validation.log")
first_col = result["stdout"].strip().split('\n')

# After
from ce.shell_utils import extract_fields
log_text = Path("validation.log").read_text()
first_col = [fields[0] for fields in extract_fields(log_text, [1])]
```

---

## DOCUMENTATION

### Key References

**MCP Tool Inventory**:
- `docs/research/10-tooling-configuration.md` - Current tool matrix (section 2.1-2.2)
- `docs/research/03-mcp-orchestration.md` - MCP command reference (section 4)

**Current Configuration**:
- `.claude/settings.local.json` - Current permissions (45+ entries)
- No deny list currently defined

**Python Standard Library**:
- `pathlib.Path` - File operations
- `re` module - Regex matching (grep alternative)
- String methods - replace(), split() (sed/awk alternatives)

### Implementation Patterns

**Permission Configuration**:
```json
{
  "allow": ["mcp__server__specific_tool"],  // Explicit function name
  "deny": ["mcp__server__unused_tool"],     // Efficiency optimization
  "ask": ["mcp__server__sensitive_tool"]    // Manual confirmation
}
```

**Python Utility Pattern**:
```python
def bash_alternative(args) -> result:
    """Docstring with 'Replaces: bash command'."""
    # Pure Python implementation
    # No subprocess calls
    return result
```

---

## OTHER CONSIDERATIONS

### Performance Impact

**Context size reduction**:
- Before: All MCP tools loaded (100+ tool schemas)
- After: 31 explicit tools (70% reduction)
- Token savings: 30-50% of tool-related context

**Query tree complexity**:
- Before: Agent evaluates 100+ tools per decision
- After: Agent evaluates 31 tools per decision
- Speed improvement: Faster tool selection

**Python vs Bash**:
- Subprocess overhead: ~10-50ms per call (fork + exec)
- Python function call: <1ms (in-process)
- Benefit: 10-50x faster for text operations

### Backward Compatibility

**Breaking changes**:
- Bash commands in deny list will fail with permission error
- Must refactor all bash usage to Python equivalents
- Mitigation: Update ce modules before deploying new config

**Non-breaking**:
- Allow list is additive (no existing code breaks)
- Deny list only affects new code attempts
- Tool mapping guide is optional reference

### Security Considerations

**Note**: Deny list is for **efficiency**, not security.

**Actual security items** (in ask list):
- `mcp__git__git_push` - Requires manual confirmation
- `mcp__filesystem__delete_file` - Requires manual confirmation

**Efficiency items** (in deny list):
- Unused MCP tools (not security risks, just bloat)
- Replaceable bash commands (efficiency optimization)

### Testing Strategy

**Unit tests** (shell_utils):
- Test each Python utility function
- Compare output to bash equivalent
- Edge cases: empty input, malformed data

**Integration tests** (configuration):
- Verify denied tools actually fail
- Verify allowed tools work
- Measure context size before/after

**Refactoring validation**:
- Grep for Bash() calls in ce modules
- Ensure all replaced with Python equivalents
- Run full test suite with new config

### Documentation Updates

**Must update**:
- `.ce/tool-inventory.yml` (NEW) - Usage statistics
- `examples/tool-usage-patterns.md` (NEW) - Tool mapping guide
- `.serena/memories/tool-usage-guide.md` (NEW) - Copy for agent
- `CLAUDE.md` - Reference tool guide
- `docs/research/10-tooling-configuration.md` - Updated tool matrix

**Validation**:
- All documentation synced with implementation
- Tool inventory reflects actual usage
- Examples tested and verified

---

## ACCEPTANCE CRITERIA

- [ ] MCP tool usage audit completed (`.ce/tool-inventory.yml` created)
- [ ] Allow list: ~31 specific MCP tools (explicit, no wildcards)
- [ ] Deny list: 50+ unused MCP tools + 11 bash commands
- [ ] Tool usage guide: `examples/tool-usage-patterns.md` created
- [ ] Serena memory: `.serena/memories/tool-usage-guide.md` populated
- [ ] Python shell_utils: 8 functions implemented (grep, wc, head, tail, find, awk×3)
- [ ] Unit tests: 100% coverage for shell_utils module
- [ ] Refactoring: Bash usage reduced from 45+ to 3 commands (git, uv)
- [ ] Context reduction: 30-50% measured improvement
- [ ] Query tree: 60-70% fewer tools in evaluation
- [ ] Performance: Python utilities faster than bash (benchmarked)
- [ ] Documentation: All 5 files updated and synced
- [ ] Integration tests: All tests pass with new configuration
- [ ] CLAUDE.md: References tool mapping guide