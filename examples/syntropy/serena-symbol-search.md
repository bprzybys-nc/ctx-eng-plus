# Serena Symbol Search and Navigation

Comprehensive guide for using Serena MCP tools to navigate code symbols, find definitions, search patterns, track references, and perform safe refactoring operations.

## Purpose

Serena provides semantic code understanding through AST-based symbol analysis. Unlike simple text search (grep), Serena understands code structure and can accurately find symbol definitions, track references across files, and provide symbol overviews.

**When to Use**:

- Finding where a class/function/variable is defined
- Getting all symbols in a file (classes, functions, methods, variables, imports)
- Searching for code patterns with semantic understanding
- Tracking all usages of a symbol across the codebase
- Understanding code structure before making changes
- **Safe refactoring**: Renaming symbols with full reference tracking

**When NOT to Use**:

- Simple text search → Use `Grep` (native, faster)
- Reading file contents → Use `Read` (native, faster)
- Finding files by name → Use `Glob` (native, faster)

## Prerequisites

- Serena MCP server active (`/syntropy-health` to verify)
- Project activated in Serena: `mcp__syntropy__serena__activate_project(project="/full/path")`
- Code indexed (happens automatically on activation)

## Symbol Family Tools

Serena provides 4 core tools for symbol navigation:

| Tool | Purpose | Returns | Use When |
|------|---------|---------|----------|
| `find_symbol` | Find definition of specific symbol | Single symbol with location, signature, body | You know the symbol name and want its definition |
| `get_symbols_overview` | List all symbols in a file | Array of symbols with signatures | Exploring file structure before editing |
| `search_for_pattern` | Search code with regex patterns | Matches with file, line, context | Finding symbols by pattern (e.g., all `*_handler` functions) |
| `find_referencing_symbols` | Find all usages of a symbol | All references with file, line, context | Before refactoring/renaming a symbol |

**Symbol Types Supported**:

- **Functions**: Top-level and nested functions
- **Classes**: Class definitions and nested classes
- **Methods**: Instance methods, class methods, static methods
- **Variables**: Global variables, class variables, instance variables
- **Imports**: Import statements and from-imports
- **Decorators**: Function and class decorators

## Examples

### Example 1: Find Symbol Definition

**Use Case**: You see `validate_level_4()` called somewhere and want to find its definition.

```python
# Find where validate_level_4 is defined
result = mcp__syntropy__serena__find_symbol(
    name_path="validate_level_4",
    include_body=False  # Just get signature, not full implementation
)
```

**Output**:

```json
{
  "symbol": {
    "name": "validate_level_4",
    "type": "function",
    "file": "tools/ce/validate.py",
    "line": 142,
    "signature": "def validate_level_4(prp_path: str, initial_path: str = None) -> Dict[str, Any]",
    "docstring": "Level 4 validation: Pattern conformance with drift detection"
  }
}
```

**With Body** (for full implementation):

```python
result = mcp__syntropy__serena__find_symbol(
    name_path="validate_level_4",
    include_body=True  # Get full function implementation
)
# Returns: Full function code including implementation
```

### Example 2: Find Class Method

**Use Case**: Navigate to a specific method within a class.

```python
# Find ValidationLoop.run_gate method
result = mcp__syntropy__serena__find_symbol(
    name_path="ValidationLoop.run_gate",
    include_body=True
)
```

**Output**:

```json
{
  "symbol": {
    "name": "run_gate",
    "type": "method",
    "class": "ValidationLoop",
    "file": "tools/ce/validation_loop.py",
    "line": 85,
    "signature": "def run_gate(self, level: int, command: str) -> bool",
    "body": "..."  // Full method implementation
  }
}
```

### Example 3: Get File Symbol Overview

**Use Case**: Understand what a file contains before editing it.

```python
# Get all symbols in validate.py
overview = mcp__syntropy__serena__get_symbols_overview(
    relative_path="tools/ce/validate.py"
)
```

**Output**:

```json
{
  "file": "tools/ce/validate.py",
  "symbols": [
    {
      "name": "validate_level_1",
      "type": "function",
      "line": 45,
      "signature": "def validate_level_1() -> Dict[str, Any]"
    },
    {
      "name": "validate_level_2",
      "type": "function",
      "line": 78,
      "signature": "def validate_level_2(test_command: str) -> Dict[str, Any]"
    },
    {
      "name": "validate_level_3",
      "type": "function",
      "line": 110,
      "signature": "def validate_level_3() -> Dict[str, Any]"
    },
    {
      "name": "validate_level_4",
      "type": "function",
      "line": 142,
      "signature": "def validate_level_4(prp_path: str, initial_path: str = None) -> Dict[str, Any]"
    }
  ]
}
```

### Example 4: Search for Patterns

**Use Case**: Find all functions that match a specific pattern (e.g., all validation functions).

```python
# Search for validation functions
results = mcp__syntropy__serena__search_for_pattern(
    pattern=r"def validate_level_\d+",
    file_glob="tools/ce/*.py"
)
```

**Output**:

```json
{
  "matches": [
    {
      "file": "tools/ce/validate.py",
      "line": 45,
      "match": "def validate_level_1() -> Dict[str, Any]:",
      "context": "..."
    },
    {
      "file": "tools/ce/validate.py",
      "line": 78,
      "match": "def validate_level_2(test_command: str) -> Dict[str, Any]:",
      "context": "..."
    }
  ],
  "total_matches": 4
}
```

**Without file glob** (search entire project):

```python
results = mcp__syntropy__serena__search_for_pattern(
    pattern=r"class.*Strategy"  # Find all Strategy classes
)
```

### Example 5: Find All References to a Symbol

**Use Case**: Before refactoring `validate_level_4()`, find everywhere it's used.

```python
# Find all places that call validate_level_4
refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="validate_level_4"
)
```

**Output**:

```json
{
  "symbol": "validate_level_4",
  "references": [
    {
      "file": "tools/ce/execute.py",
      "line": 156,
      "context": "result = validate_level_4(prp_path, initial_path)"
    },
    {
      "file": "tools/tests/test_validate.py",
      "line": 89,
      "context": "def test_validate_level_4():"
    },
    {
      "file": "tools/ce/cli_handlers.py",
      "line": 203,
      "context": "validation = validate_level_4(args.prp_path)"
    }
  ],
  "total_references": 3
}
```

### Example 6: Navigate Nested Symbols

**Use Case**: Find a nested class method.

```python
# Find method in nested class
result = mcp__syntropy__serena__find_symbol(
    name_path="ParserStrategy.RealParserStrategy.parse_blueprint"
)
```

**Output**: Definition of `parse_blueprint` method within nested `RealParserStrategy` class.

### Example 7: Complete Symbol Family - All Types

**Use Case**: Demonstrate finding all symbol types supported by Serena.

```python
# 1. FUNCTION: Top-level function
func = mcp__syntropy__serena__find_symbol(name_path="validate_level_4")
# Returns: {"type": "function", "file": "tools/ce/validate.py", "line": 142, ...}

# 2. CLASS: Class definition
cls = mcp__syntropy__serena__find_symbol(name_path="ValidationLoop")
# Returns: {"type": "class", "file": "tools/ce/validation_loop.py", "line": 12, ...}

# 3. METHOD: Instance method
method = mcp__syntropy__serena__find_symbol(name_path="ValidationLoop.run_gate")
# Returns: {"type": "method", "class": "ValidationLoop", "line": 85, ...}

# 4. STATIC METHOD: Static method
static = mcp__syntropy__serena__find_symbol(name_path="Utils.format_output")
# Returns: {"type": "staticmethod", "class": "Utils", ...}

# 5. CLASS METHOD: Class method
classmethod = mcp__syntropy__serena__find_symbol(name_path="Config.from_file")
# Returns: {"type": "classmethod", "class": "Config", ...}

# 6. VARIABLE: Global variable
var = mcp__syntropy__serena__search_for_pattern(
    pattern=r"^DEFAULT_TIMEOUT\s*=",
    file_glob="tools/ce/config.py"
)
# Returns: Match for global variable definition

# 7. CLASS VARIABLE: Class attribute
class_var = mcp__syntropy__serena__search_for_pattern(
    pattern=r"class ValidationLoop:.*\n.*version\s*=",
    file_glob="tools/ce/validation_loop.py"
)
# Returns: Match for class variable

# 8. IMPORT: Import statement
imports = mcp__syntropy__serena__search_for_pattern(
    pattern=r"^from tools\.ce import",
    file_glob="tools/ce/*.py"
)
# Returns: All "from tools.ce import" statements

# 9. DECORATOR: Function with decorator
decorated = mcp__syntropy__serena__search_for_pattern(
    pattern=r"@.*\ndef",
    file_glob="tools/ce/*.py"
)
# Returns: All decorated functions
```

**Symbol Type Reference**:

| Symbol Type | Tool to Use | Example Name Path | Notes |
|-------------|-------------|-------------------|-------|
| Function | `find_symbol` | `function_name` | Top-level or nested |
| Class | `find_symbol` | `ClassName` | Class definition |
| Instance Method | `find_symbol` | `ClassName.method_name` | Regular method with `self` |
| Static Method | `find_symbol` | `ClassName.static_method` | Decorated with `@staticmethod` |
| Class Method | `find_symbol` | `ClassName.class_method` | Decorated with `@classmethod` |
| Variable | `search_for_pattern` | `r"^VAR_NAME\s*="` | Use pattern search, not find_symbol |
| Class Variable | `search_for_pattern` | `r"class X:.*\n.*var\s*="` | Inside class body |
| Import | `search_for_pattern` | `r"^import X"` or `r"^from X import"` | Import statements |
| Decorator | `search_for_pattern` | `r"@decorator_name"` | Decorator usage |

**Why Pattern Search for Variables/Imports?**

Variables and imports are not "callable symbols" in the AST sense, so `find_symbol` may not find them. Use `search_for_pattern` with regex for these cases.

### Example 8: Find All Symbols of Specific Type

**Use Case**: Find all class definitions in a directory.

```python
# Find all class definitions
classes = mcp__syntropy__serena__search_for_pattern(
    pattern=r"^class\s+\w+",
    file_glob="tools/ce/*.py"
)

# Output: All class definitions
for match in classes['matches']:
    print(f"{match['file']}:{match['line']} - {match['match']}")
```

**Output**:

```
tools/ce/validation_loop.py:12 - class ValidationLoop:
tools/ce/batch.py:25 - class BatchExecutor:
tools/ce/parser.py:8 - class PRPParser:
```

**Other Type-Specific Searches**:

```python
# Find all async functions
async_funcs = mcp__syntropy__serena__search_for_pattern(
    pattern=r"^async def\s+\w+",
    file_glob="**/*.py"
)

# Find all methods with specific decorator
cached_methods = mcp__syntropy__serena__search_for_pattern(
    pattern=r"@cache\s*\n\s*def",
    file_glob="**/*.py"
)

# Find all test functions
tests = mcp__syntropy__serena__search_for_pattern(
    pattern=r"def test_\w+",
    file_glob="tests/**/*.py"
)
```

## Refactoring Workflows

### Workflow 1: Rename Symbol Across Codebase

**Use Case**: Rename `validate_level_4` to `validate_pattern_conformance` across entire codebase.

```python
# Step 1: Find definition
definition = mcp__syntropy__serena__find_symbol(
    name_path="validate_level_4",
    include_body=False
)
print(f"Defined in: {definition['symbol']['file']}:{definition['symbol']['line']}")

# Step 2: Find all references
refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="validate_level_4"
)
print(f"Total references: {refs['total_references']}")

# Step 3: Review references (identify import vs usage)
for ref in refs['references']:
    print(f"{ref['file']}:{ref['line']} - {ref['context']}")

# Step 4: Replace in definition file first
Edit(
    file_path=definition['symbol']['file'],
    old_string="def validate_level_4(",
    new_string="def validate_pattern_conformance("
)

# Step 5: Replace in each reference file
for ref in refs['references']:
    # Read file to get exact context
    file_content = Read(file_path=ref['file'])

    # Replace old name with new name
    Edit(
        file_path=ref['file'],
        old_string="validate_level_4",
        new_string="validate_pattern_conformance",
        replace_all=True  # Replace all occurrences in file
    )

# Step 6: Verify no references remain
verification = mcp__syntropy__serena__find_referencing_symbols(
    name_path="validate_level_4"
)
print(f"Remaining references: {verification['total_references']}")  # Should be 0
```

**Output**: All 3 references updated, function renamed successfully.

### Workflow 2: Rename Class and Its Methods

**Use Case**: Rename `ValidationLoop` to `ValidationOrchestrator` including all method references.

```python
# Step 1: Find class definition
class_def = mcp__syntropy__serena__find_symbol(
    name_path="ValidationLoop",
    include_body=False
)

# Step 2: Get all methods in class
overview = mcp__syntropy__serena__get_symbols_overview(
    relative_path=class_def['symbol']['file']
)
class_methods = [s for s in overview['symbols'] if s.get('class') == 'ValidationLoop']

# Step 3: Find all class references
class_refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="ValidationLoop"
)

# Step 4: Replace class name in definition
Edit(
    file_path=class_def['symbol']['file'],
    old_string="class ValidationLoop:",
    new_string="class ValidationOrchestrator:"
)

# Step 5: Replace class references (imports, instantiations)
for ref in class_refs['references']:
    # Handle different reference types
    if 'import' in ref['context'].lower():
        # Update import statement
        Edit(
            file_path=ref['file'],
            old_string="from tools.ce.validation_loop import ValidationLoop",
            new_string="from tools.ce.validation_loop import ValidationOrchestrator"
        )
    elif 'ValidationLoop(' in ref['context']:
        # Update instantiation
        Edit(
            file_path=ref['file'],
            old_string="ValidationLoop(",
            new_string="ValidationOrchestrator(",
            replace_all=True
        )
```

### Workflow 3: Move Function Between Files

**Use Case**: Move `parse_prp_file()` from `utils.py` to `parser.py`.

```python
# Step 1: Find function definition with body
func_def = mcp__syntropy__serena__find_symbol(
    name_path="parse_prp_file",
    include_body=True
)

# Step 2: Find all references
refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="parse_prp_file"
)

# Step 3: Copy function to new file
Read(file_path="tools/ce/parser.py")
Edit(
    file_path="tools/ce/parser.py",
    old_string="# Add new functions below\n",
    new_string=f"# Add new functions below\n\n{func_def['symbol']['body']}\n"
)

# Step 4: Update all import statements
for ref in refs['references']:
    if 'import' in ref['context'].lower():
        Edit(
            file_path=ref['file'],
            old_string="from tools.ce.utils import parse_prp_file",
            new_string="from tools.ce.parser import parse_prp_file"
        )

# Step 5: Remove from old file
Edit(
    file_path="tools/ce/utils.py",
    old_string=func_def['symbol']['body'],
    new_string=""
)

# Step 6: Verify all references updated
verification = mcp__syntropy__serena__search_for_pattern(
    pattern="from tools.ce.utils import parse_prp_file"
)
print(f"Old imports remaining: {verification['total_matches']}")  # Should be 0
```

### Workflow 4: Update Function Signature

**Use Case**: Add parameter to `validate_level_3(test_cmd: str)` → `validate_level_3(test_cmd: str, verbose: bool = False)`.

```python
# Step 1: Find function definition
func_def = mcp__syntropy__serena__find_symbol(
    name_path="validate_level_3",
    include_body=False
)

# Step 2: Update function signature
Edit(
    file_path=func_def['symbol']['file'],
    old_string="def validate_level_3(test_cmd: str) -> Dict[str, Any]:",
    new_string="def validate_level_3(test_cmd: str, verbose: bool = False) -> Dict[str, Any]:"
)

# Step 3: Find all call sites
refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="validate_level_3"
)

# Step 4: Review each call site (manual decision needed)
for ref in refs['references']:
    if 'def test_' in ref['context']:
        # Test function - skip
        continue
    elif 'validate_level_3(' in ref['context']:
        print(f"⚠️  Review call site: {ref['file']}:{ref['line']}")
        print(f"   Context: {ref['context']}")
        # Decide if verbose=True needed, then:
        # Edit(file_path=ref['file'], old_string="validate_level_3(cmd)", new_string="validate_level_3(cmd, verbose=True)")
```

**Note**: Default parameter value makes this backward-compatible, so updating call sites is optional.

## Quick Reference

**Find symbol definition:**

```python
mcp__syntropy__serena__find_symbol(name_path="symbol_name")
```

**List all symbols in file:**

```python
mcp__syntropy__serena__get_symbols_overview(relative_path="path/to/file.py")
```

**Search by pattern:**

```python
mcp__syntropy__serena__search_for_pattern(pattern=r"regex", file_glob="path/*.py")
```

**Find all usages:**

```python
mcp__syntropy__serena__find_referencing_symbols(name_path="symbol_name")
```

**Rename symbol (3-step):**

1. `find_referencing_symbols` → Find all usages
2. `Edit` definition file → Rename in definition
3. `Edit` each reference → Update all call sites

## Usage Guide

### Decision Tree: Which Tool to Use?

```
Do you know the exact symbol name?
├─ YES → Use `find_symbol(name_path="SymbolName")`
│         Returns: Definition location, signature, body
│
└─ NO → Do you know the file?
    ├─ YES → Use `get_symbols_overview(relative_path="file.py")`
    │         Returns: All symbols in file
    │
    └─ NO → Use pattern search
        └─ `search_for_pattern(pattern=r"regex", file_glob="*.py")`
            Returns: All matches across files

Before refactoring?
└─ Use `find_referencing_symbols(name_path="SymbolName")`
   Returns: All places symbol is used
```

### Workflow: Exploring Unfamiliar Code

**Goal**: Understand how validation works in the codebase.

1. **Start broad**: Search for pattern

   ```python
   mcp__syntropy__serena__search_for_pattern(
       pattern=r"def validate_",
       file_glob="tools/ce/*.py"
   )
   ```

2. **Narrow to file**: Get file overview

   ```python
   mcp__syntropy__serena__get_symbols_overview(
       relative_path="tools/ce/validate.py"
   )
   ```

3. **Dive into specifics**: Get function body

   ```python
   mcp__syntropy__serena__find_symbol(
       name_path="validate_level_4",
       include_body=True
   )
   ```

4. **Understand usage**: Find references

   ```python
   mcp__syntropy__serena__find_referencing_symbols(
       name_path="validate_level_4"
   )
   ```

### Workflow: Safe Refactoring

**Goal**: Rename function without breaking anything.

1. **Impact analysis**: Find all references

   ```python
   refs = mcp__syntropy__serena__find_referencing_symbols(name_path="old_name")
   ```

2. **Review**: Check each reference location

   ```python
   for ref in refs['references']:
       print(f"{ref['file']}:{ref['line']}")
   ```

3. **Rename**: Update definition + all references

   ```python
   # Definition
   Edit(file_path=def_file, old_string="def old_name(", new_string="def new_name(")

   # References
   for ref in refs['references']:
       Edit(file_path=ref['file'], old_string="old_name", new_string="new_name", replace_all=True)
   ```

4. **Verify**: Confirm no old references remain

   ```python
   verification = mcp__syntropy__serena__find_referencing_symbols(name_path="old_name")
   assert verification['total_references'] == 0
   ```

## Common Patterns

### Pattern 1: Pre-Edit Symbol Discovery

Before editing a file, understand its structure:

```python
# 1. Get symbol overview
overview = mcp__syntropy__serena__get_symbols_overview(
    relative_path="tools/ce/validate.py"
)

# 2. Find specific function to edit
target = mcp__syntropy__serena__find_symbol(
    name_path="validate_level_3",
    include_body=True
)

# 3. Check for references (impact analysis)
refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="validate_level_3"
)

# 4. Now safe to edit with full context
Edit(file_path="tools/ce/validate.py", ...)
```

### Pattern 2: Refactoring Safety Check

Before renaming or moving a symbol:

```python
# 1. Find all references
refs = mcp__syntropy__serena__find_referencing_symbols(
    name_path="old_function_name"
)

# 2. Review each reference location
for ref in refs['references']:
    print(f"{ref['file']}:{ref['line']} - {ref['context']}")

# 3. If manageable, proceed with refactoring
# 4. Update all references found
```

### Pattern 3: Code Exploration

Understanding unfamiliar code:

```python
# 1. Start with overview
overview = mcp__syntropy__serena__get_symbols_overview(
    relative_path="tools/ce/prp_analyzer.py"
)

# 2. For interesting symbols, get full definition
for symbol in overview['symbols']:
    if symbol['name'].startswith('analyze_'):
        detail = mcp__syntropy__serena__find_symbol(
            name_path=f"{symbol['name']}",
            include_body=True
        )
        # Review implementation
```

### Pattern 4: Cross-File Symbol Tracking

Following a symbol across multiple files:

```python
# 1. Find definition
definition = mcp__syntropy__serena__find_symbol(name_path="ValidationLoop")

# 2. Find all usages
usages = mcp__syntropy__serena__find_referencing_symbols(name_path="ValidationLoop")

# 3. Analyze import patterns
for usage in usages['references']:
    if 'import' in usage['context'].lower():
        print(f"Imported in: {usage['file']}")
```

### Pattern 5: Search + Navigate Workflow

Combining search with symbol lookup:

```python
# 1. Search for pattern
matches = mcp__syntropy__serena__search_for_pattern(
    pattern=r"def.*_strategy\(",
    file_glob="tools/ce/testing/*.py"
)

# 2. For each match, get full symbol info
for match in matches['matches']:
    symbol_name = extract_function_name(match['match'])
    detail = mcp__syntropy__serena__find_symbol(
        name_path=symbol_name,
        include_body=True
    )
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Using Serena for Simple Text Search

**Bad**:

```python
# DON'T use Serena for simple text search
results = mcp__syntropy__serena__search_for_pattern(
    pattern="TODO"  # Simple keyword search
)
```

**Good**:

```bash
# DO use native Grep for text search
Grep(pattern="TODO", output_mode="files_with_matches")
```

**Why**: Serena is for semantic code understanding. Simple text search is much faster with native tools.

### ❌ Anti-Pattern 2: Reading Entire Files with Serena

**Bad**:

```python
# DON'T use Serena to read file contents
result = mcp__syntropy__serena__find_symbol(
    name_path="some_function",
    include_body=True  # Getting body to read file
)
```

**Good**:

```python
# DO use Read for file contents
Read(file_path="path/to/file.py")
```

**Why**: `Read` is direct and faster. Use Serena only when you need symbol-specific information.

### ❌ Anti-Pattern 3: Not Using File Glob for Large Codebases

**Bad**:

```python
# DON'T search entire codebase without constraint
results = mcp__syntropy__serena__search_for_pattern(
    pattern=r"class.*"  # Will search ALL files
)
```

**Good**:

```python
# DO narrow search with file_glob
results = mcp__syntropy__serena__search_for_pattern(
    pattern=r"class.*",
    file_glob="tools/ce/*.py"  # Only search specific directory
)
```

**Why**: Searching large codebases without constraints is slow and returns too many results.

## Related Examples

- [context7-docs-fetch.md](context7-docs-fetch.md) - Fetching library documentation
- [memory-management.md](memory-management.md) - Storing symbol discoveries
- [../workflows/context-drift-remediation.md](../workflows/context-drift-remediation.md) - Using symbols in drift analysis
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - When to use Serena vs native tools

## Troubleshooting

### Issue: "Symbol not found"

**Possible causes**:

1. Symbol name typo
2. Project not activated in Serena
3. File not indexed yet

**Solution**:

```python
# Activate project first
mcp__syntropy__serena__activate_project(
    project="/Users/bprzybyszi/nc-src/ctx-eng-plus"
)

# Wait for indexing to complete (~1-2 seconds)
# Then retry search
```

### Issue: "File path relative error"

**Solution**: Use relative paths from project root, not absolute paths:

```python
# ✅ Correct
relative_path="tools/ce/validate.py"

# ❌ Wrong
relative_path="/Users/.../tools/ce/validate.py"
```

### Issue: Too many results from pattern search

**Solution**: Use more specific pattern or add file_glob:

```python
# More specific regex
pattern=r"^def validate_level_\d+\("  # Anchored to line start

# Or narrow with file_glob
file_glob="tools/ce/validate.py"  # Single file only
```

## Performance Tips

1. **Use `include_body=False` by default**: Only get body when you need the full implementation
2. **Narrow searches with `file_glob`**: Reduces search space significantly
3. **Cache symbol overviews**: If exploring a file, get overview once and reuse
4. **Combine with native tools**: Use Serena for navigation, native tools for operations

## Resources

- Serena MCP Documentation: `.serena/README.md`
- Tool Usage Guide: `examples/TOOL-USAGE-GUIDE.md`
- Syntropy Health: `/syntropy-health` slash command
