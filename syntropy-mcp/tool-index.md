# Syntropy MCP Tool Index

Auto-generated from MCP server configuration.
Last updated: 2025-10-19T20:29:14.832905

## Overview

Total servers: 7
Total tools: 32

## syntropy:context7 - Documentation

**Tool Count**: 2

### `syntropy:context7:get-library-docs`

**Original**: `mcp__context7__get-library-docs`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:context7:resolve-library-id`

**Original**: `mcp__context7__resolve-library-id`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

## syntropy:filesystem - File Operations

**Tool Count**: 9

### `syntropy:filesystem:directory_tree`

**Original**: `mcp__filesystem__directory_tree`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:edit_file`

**Original**: `mcp__filesystem__edit_file`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:get_file_info`

**Original**: `mcp__filesystem__get_file_info`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:list_allowed_directories`

**Original**: `mcp__filesystem__list_allowed_directories`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:list_directory`

**Original**: `mcp__filesystem__list_directory`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:read_file`

**Original**: `mcp__filesystem__read_file`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:read_text_file`

**Original**: `mcp__filesystem__read_text_file`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:search_files`

**Original**: `mcp__filesystem__search_files`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:filesystem:write_file`

**Original**: `mcp__filesystem__write_file`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

## syntropy:git - Version Control

**Tool Count**: 5

### `syntropy:git:git_add`

**Original**: `mcp__git__git_add`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:git:git_commit`

**Original**: `mcp__git__git_commit`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:git:git_diff`

**Original**: `mcp__git__git_diff`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:git:git_log`

**Original**: `mcp__git__git_log`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:git:git_status`

**Original**: `mcp__git__git_status`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

## syntropy:linear-server - Project Management

**Tool Count**: 5

### `syntropy:linear-server:create_issue`

**Original**: `mcp__linear-server__create_issue`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:linear-server:get_issue`

**Original**: `mcp__linear-server__get_issue`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:linear-server:list_issues`

**Original**: `mcp__linear-server__list_issues`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:linear-server:list_projects`

**Original**: `mcp__linear-server__list_projects`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:linear-server:update_issue`

**Original**: `mcp__linear-server__update_issue`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

## syntropy:repomix - Codebase Analysis

**Tool Count**: 1

### `syntropy:repomix:pack_codebase`

**Original**: `mcp__repomix__pack_codebase`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

## syntropy:sequential-thinking - Advanced Reasoning

**Tool Count**: 1

### `syntropy:sequential-thinking:sequentialthinking`

**Original**: `mcp__sequential-thinking__sequentialthinking`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

## syntropy:serena - Code Intelligence Tools

**Tool Count**: 9

### `syntropy:serena:activate_project`

**Original**: `mcp__serena__activate_project`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:create_text_file`

**Original**: `mcp__serena__create_text_file`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:find_referencing_symbols`

**Original**: `mcp__serena__find_referencing_symbols`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:find_symbol`

**Original**: `mcp__serena__find_symbol`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:get_symbols_overview`

**Original**: `mcp__serena__get_symbols_overview`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:list_dir`

**Original**: `mcp__serena__list_dir`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:read_file`

**Original**: `mcp__serena__read_file`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:search_for_pattern`

**Original**: `mcp__serena__search_for_pattern`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

### `syntropy:serena:write_memory`

**Original**: `mcp__serena__write_memory`

**Description**: *(Auto-generated from MCP metadata)*

**Parameters**: *(See MCP server documentation)*

---

## Usage Examples

### Before (Direct MCP)
```typescript
await mcp.call("mcp__serena__find_symbol", {
  name_path: "MyClass/method",
  relative_path: "src/main.py"
});
```

### After (Syntropy)
```typescript
await mcp.call("syntropy:serena:find_symbol", {
  name_path: "MyClass/method",
  relative_path: "src/main.py"
});
```
