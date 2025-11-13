"""
Filesystem MCP File Operations Patterns

Filesystem provides file read/write/list operations through Syntropy.
Pattern: mcp__syntropy__filesystem__<operation>
"""


# ✅ PATTERN 1: Read Text File
# Use when: Reading config files, markdown, non-code text
def example_read_text_file():
    """Read configuration or text files."""
    from mcp__syntropy import syntropy_filesystem_read_text_file
    
    # Read YAML config
    result = syntropy_filesystem_read_text_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/.ce/linear-defaults.yml"
    )
    # Returns: File contents as string
    
    # Read markdown documentation
    result = syntropy_filesystem_read_text_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/README.md"
    )
    # Returns: Full markdown content


# ✅ PATTERN 2: Write File
# Use when: Creating new files or overwriting existing
def example_write_file():
    """Write file contents (creates or overwrites)."""
    from mcp__syntropy import syntropy_filesystem_write_file
    
    # Create new config file
    syntropy_filesystem_write_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/config.yml",
        content="""
        project: Context Engineering
        version: 1.0.0
        features:
          - prp-system
          - mcp-integration
        """
    )
    
    # Overwrite existing file
    syntropy_filesystem_write_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/temp.txt",
        content="Updated content"
    )
    # ⚠️ Warning: Completely replaces file, no backup


# ✅ PATTERN 3: Edit File (Surgical Changes)
# Use when: Making precise line-by-line edits
def example_edit_file():
    """Make targeted edits to existing files."""
    from mcp__syntropy import syntropy_filesystem_edit_file
    
    # Single edit
    result = syntropy_filesystem_edit_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/config.py",
        edits=[
            {
                "oldText": "DEBUG = False",
                "newText": "DEBUG = True"
            }
        ]
    )
    
    # Multiple edits in one call
    result = syntropy_filesystem_edit_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/config.py",
        edits=[
            {
                "oldText": "DEBUG = False",
                "newText": "DEBUG = True"
            },
            {
                "oldText": "LOG_LEVEL = 'info'",
                "newText": "LOG_LEVEL = 'debug'"
            }
        ]
    )
    # ✅ Safer than write: Only changes specified portions


# ✅ PATTERN 4: List Directory Contents
# Use when: Exploring directory structure
def example_list_directory():
    """List files and subdirectories."""
    from mcp__syntropy import syntropy_filesystem_list_directory
    
    # List project root
    result = syntropy_filesystem_list_directory(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus"
    )
    # Returns: [FILE] name.ext, [DIR] dirname
    
    # List specific subdirectory
    result = syntropy_filesystem_list_directory(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/tools/ce"
    )
    # Returns: All Python modules in ce/


# ✅ PATTERN 5: Search Files by Pattern
# Use when: Finding files matching glob pattern
def example_search_files():
    """Find files matching name pattern."""
    from mcp__syntropy import syntropy_filesystem_search_files
    
    # Find all test files
    result = syntropy_filesystem_search_files(
        directory="/Users/bprzybysz/nc-src/ctx-eng-plus/tools",
        pattern="test_*.py"
    )
    # Returns: List of matching file paths
    
    # Find all markdown files
    result = syntropy_filesystem_search_files(
        directory="/Users/bprzybysz/nc-src/ctx-eng-plus",
        pattern="*.md"
    )
    
    # Find PRPs
    result = syntropy_filesystem_search_files(
        directory="/Users/bprzybysz/nc-src/ctx-eng-plus/PRPs",
        pattern="PRP-*.md"
    )


# ✅ PATTERN 6: Get Directory Tree
# Use when: Visualizing project structure
def example_directory_tree():
    """Get hierarchical directory structure."""
    from mcp__syntropy import syntropy_filesystem_directory_tree
    
    # Full tree
    result = syntropy_filesystem_directory_tree(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/tools/ce",
        max_depth=3
    )
    # Returns: JSON tree structure
    
    # Shallow tree (just immediate children)
    result = syntropy_filesystem_directory_tree(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus",
        max_depth=1
    )


# ✅ PATTERN 7: Get File Info
# Use when: Getting metadata (size, timestamp, permissions)
def example_get_file_info():
    """Get file metadata."""
    from mcp__syntropy import syntropy_filesystem_get_file_info
    
    result = syntropy_filesystem_get_file_info(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/tools/ce/core.py"
    )
    # Returns: {size, modified_time, permissions, is_directory, ...}


# ✅ PATTERN 8: List Allowed Directories
# Use when: Checking sandbox boundaries
def example_list_allowed_directories():
    """Check which directories are accessible."""
    from mcp__syntropy import syntropy_filesystem_list_allowed_directories
    
    result = syntropy_filesystem_list_allowed_directories()
    # Returns: List of accessible directory paths


# 📊 PERFORMANCE CHARACTERISTICS
# - Read file: O(file_size) - sequential read
# - Write file: O(content_size) - sequential write
# - List directory: O(n) where n = items in directory
# - Search files: O(n*pattern_complexity)
# - Directory tree: O(n*depth) where n = items per level


# 🎯 WORKFLOW EXAMPLE: Configuration Management
def config_workflow():
    """Typical workflow: Read config, modify, write back."""
    from mcp__syntropy import (
        syntropy_filesystem_read_text_file,
        syntropy_filesystem_edit_file
    )
    
    # Step 1: Read current config
    config = syntropy_filesystem_read_text_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/.ce/config.yml"
    )
    print(f"Current config:\n{config}")
    
    # Step 2: Make targeted edit
    result = syntropy_filesystem_edit_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/.ce/config.yml",
        edits=[
            {
                "oldText": "cache_ttl: 5",
                "newText": "cache_ttl: 10"
            }
        ]
    )
    print(f"Edit successful: {result['success']}")


# 🎯 WORKFLOW EXAMPLE: Project Exploration
def exploration_workflow():
    """Typical workflow: Explore project structure."""
    from mcp__syntropy import (
        syntropy_filesystem_list_directory,
        syntropy_filesystem_directory_tree,
        syntropy_filesystem_search_files
    )
    
    # Step 1: List root directory
    root_items = syntropy_filesystem_list_directory(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus"
    )
    
    # Step 2: Get tree view of specific subtree
    tree = syntropy_filesystem_directory_tree(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/tools/ce",
        max_depth=2
    )
    
    # Step 3: Find all Python test files
    tests = syntropy_filesystem_search_files(
        directory="/Users/bprzybysz/nc-src/ctx-eng-plus/tools",
        pattern="test_*.py"
    )
    print(f"Found {len(tests)} test files")


# 🔧 ERROR HANDLING PATTERNS

# ✅ PATTERN: Safe Edit with Validation
def safe_edit_pattern():
    """Edit file safely with validation."""
    from mcp__syntropy import (
        syntropy_filesystem_read_text_file,
        syntropy_filesystem_edit_file
    )
    
    # Step 1: Read current content
    current = syntropy_filesystem_read_text_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/config.py"
    )
    
    # Step 2: Verify old_string exists
    if "old_value = 'X'" not in current:
        raise ValueError("Expected text not found - file may have changed\n🔧 Troubleshooting: Check inputs and system state")
    
    # Step 3: Make edit
    result = syntropy_filesystem_edit_file(
        path="/Users/bprzybysz/nc-src/ctx-eng-plus/config.py",
        edits=[
            {
                "oldText": "old_value = 'X'",
                "newText": "old_value = 'Y'"
            }
        ]
    )
    
    if not result.get("success"):
        raise RuntimeError(f"Edit failed: {result.get('error')}\n🔧 Troubleshooting: Check inputs and system state")


# ✅ PATTERN: Batch File Operations
def batch_operations():
    """Process multiple files efficiently."""
    from mcp__syntropy import (
        syntropy_filesystem_search_files,
        syntropy_filesystem_read_text_file
    )
    
    # Find all config files
    configs = syntropy_filesystem_search_files(
        directory="/Users/bprzybysz/nc-src/ctx-eng-plus",
        pattern="*.yml"
    )
    
    # Read each one
    results = {}
    for config_path in configs:
        content = syntropy_filesystem_read_text_file(path=config_path)
        results[config_path] = content
    
    return results


# 🔧 TROUBLESHOOTING
def troubleshooting():
    """Common issues and solutions."""
    # Issue: File not found
    # Solution: Use absolute paths, verify directory exists
    
    # Issue: Edit oldText not found
    # Solution: Text must match exactly (whitespace, line endings)
    # Use read_text_file first to verify exact content
    
    # Issue: Permission denied
    # Solution: Check file permissions, ensure path is in allowed directories
    # Use list_allowed_directories() to verify access
    
    # Issue: Large file operations slow
    # Solution: Use edit_file for surgical changes (faster than write)
    # Batch multiple edits in single call when possible
