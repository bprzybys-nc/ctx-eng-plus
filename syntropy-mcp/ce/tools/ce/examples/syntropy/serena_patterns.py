"""
Serena MCP Code Navigation Patterns

Serena provides LSP-backed code navigation through Syntropy.
Pattern: mcp__syntropy__serena__<operation>
"""


# ✅ PATTERN 1: Find Symbol Definition
# Use when: You know the symbol name and want to see its implementation
def example_find_symbol():
    """Find function/class by exact name."""
    from mcp__syntropy import syntropy_serena_find_symbol
    
    # Find function
    result = syntropy_serena_find_symbol(
        name_path="authenticate_user",
        include_body=True
    )
    # Returns: function source code, docstring, location
    
    # Find class method
    result = syntropy_serena_find_symbol(
        name_path="UserAuth/validate",
        include_body=True
    )
    # Returns: method source, containing class, decorators


# ✅ PATTERN 2: Get File Structure Overview
# Use when: Exploring a file for the first time, need high-level structure
def example_get_symbols_overview():
    """List all top-level functions/classes in a file."""
    from mcp__syntropy import syntropy_serena_get_symbols_overview
    
    # Get file structure
    result = syntropy_serena_get_symbols_overview(
        relative_path="ce/core.py"
    )
    # Returns: List of all functions, classes, imports, metadata


# ✅ PATTERN 3: Search for Code Pattern
# Use when: Find all occurrences of a pattern (not exact symbol name)
def example_search_for_pattern():
    """Search code by regex pattern across codebase."""
    from mcp__syntropy import syntropy_serena_search_for_pattern
    
    # Find all async functions
    result = syntropy_serena_search_for_pattern(
        pattern=r"async def \w+",
        file_glob="**/*.py"
    )
    # Returns: All async function definitions
    
    # Find error handling patterns
    result = syntropy_serena_search_for_pattern(
        pattern=r"except\s+\w+Error",
        file_glob="ce/**/*.py"
    )
    # Returns: All specific error catches


# ✅ PATTERN 4: Find All References
# Use when: Impact analysis - where is this function called?
def example_find_referencing_symbols():
    """Find all uses of a symbol throughout codebase."""
    from mcp__syntropy import syntropy_serena_find_referencing_symbols
    
    # Find all calls to validate_token
    result = syntropy_serena_find_referencing_symbols(
        name_path="validate_token"
    )
    # Returns: All file locations where validate_token is called
    
    # Use in refactoring: Before changing function signature, see all call sites


# ✅ PATTERN 5: Read File Contents
# Use when: Need to read Python file with LSP indexing
def example_read_file():
    """Read file with LSP context awareness."""
    from mcp__syntropy import syntropy_serena_read_file
    
    # Read Python module
    result = syntropy_serena_read_file(
        relative_path="ce/core.py"
    )
    # Returns: Full file content with LSP metadata


# ✅ PATTERN 6: Write Memory (Context Storage)
# Use when: Store important patterns/context for future reference
def example_write_memory():
    """Store context in Serena memory for persistent reference."""
    from mcp__syntropy import syntropy_serena_write_memory
    
    # Store pattern documentation
    syntropy_serena_write_memory(
        memory_type="pattern",
        content="""
        Error Handling Pattern:
        - All functions include try/except
        - Exceptions include 🔧 Troubleshooting guidance
        - No silent failures or fallbacks
        - File: examples/patterns/error-handling.py
        """
    )
    
    # Store architecture notes
    syntropy_serena_write_memory(
        memory_type="architecture",
        content="""
        Module Structure:
        - ce/core.py: File/git/shell operations
        - ce/validate.py: 3-level validation gates
        - ce/context.py: Context management
        - ce/execute.py: PRP execution engine
        """
    )


# ✅ PATTERN 7: Activate Project Context
# Use when: Initialize Serena for project-specific operations
def example_activate_project():
    """Set active project for Serena operations."""
    from mcp__syntropy import syntropy_serena_activate_project
    
    # Activate project context
    syntropy_serena_activate_project(
        project="/Users/bprzybysz/nc-src/ctx-eng-plus"
    )
    # Enables: Symbol resolution, pattern search, code navigation


# 📊 PERFORMANCE CHARACTERISTICS
# - First call: ~1-2 seconds (server spawn)
# - Subsequent calls: <50ms (connection reused)
# - Find symbol: O(1) - direct LSP lookup
# - Search pattern: O(n) - scans matching files
# - Find references: O(n) - builds dependency graph


# 🎯 WORKFLOW EXAMPLE: Refactoring Function
def refactoring_workflow():
    """Typical workflow: Rename function with impact analysis."""
    from mcp__syntropy import (
        syntropy_serena_find_symbol,
        syntropy_serena_find_referencing_symbols,
        syntropy_serena_search_for_pattern
    )
    
    # Step 1: Find function definition
    func = syntropy_serena_find_symbol("old_function_name", include_body=True)
    
    # Step 2: Find all references
    refs = syntropy_serena_find_referencing_symbols("old_function_name")
    print(f"Found {len(refs)} call sites")
    
    # Step 3: Search for pattern variations
    patterns = syntropy_serena_search_for_pattern(
        pattern=r"old_function_name\s*\(",
        file_glob="**/*.py"
    )
    
    # Step 4: Rename with confidence (know all locations)
    # Now safe to refactor


# 🔧 TROUBLESHOOTING
def troubleshooting():
    """Common issues and solutions."""
    # Issue: find_symbol returns empty
    # Solution: Use exact symbol name (case-sensitive)
    # Verify with get_symbols_overview first
    
    # Issue: search_for_pattern returns no results
    # Solution: Test regex with: mcp__syntropy__serena__search_for_pattern
    # Use file_glob parameter to limit scope
    
    # Issue: References incomplete or missing
    # Solution: Serena LSP indexing may need refresh
    # Re-activate project: syntropy_serena_activate_project(...)
