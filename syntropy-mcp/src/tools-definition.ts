/**
 * Proper MCP Tool Definitions with Input Schemas
 *
 * This follows MCP best practices by including inputSchema for each tool.
 * inputSchema is CRITICAL for Claude Code to properly register and expose tools.
 */

export const SYNTROPY_TOOLS = [
  // ============ SERENA TOOLS (9) ============
  {
    name: "syntropy_serena_find_symbol",
    description: "Find code symbols by name path in the codebase",
    inputSchema: {
      type: "object" as const,
      properties: {
        name_path: {
          type: "string",
          description: "Name path to search for (e.g., 'MyClass.my_method')"
        },
        include_body: {
          type: "boolean",
          description: "Include function/method body in results"
        }
      },
      required: ["name_path"]
    }
  },
  {
    name: "syntropy_serena_get_symbols_overview",
    description: "Get overview of all symbols in a file",
    inputSchema: {
      type: "object" as const,
      properties: {
        relative_path: {
          type: "string",
          description: "Relative path to the file to analyze (relative to project root)"
        }
      },
      required: ["relative_path"]
    }
  },
  {
    name: "syntropy_serena_search_for_pattern",
    description: "Search codebase for specific patterns",
    inputSchema: {
      type: "object" as const,
      properties: {
        pattern: {
          type: "string",
          description: "Regex pattern to search for"
        },
        file_glob: {
          type: "string",
          description: "File glob pattern to limit search"
        }
      },
      required: ["pattern"]
    }
  },
  {
    name: "syntropy_serena_find_referencing_symbols",
    description: "Find all symbols that reference a given symbol",
    inputSchema: {
      type: "object" as const,
      properties: {
        name_path: {
          type: "string",
          description: "Name path of symbol to find references for"
        }
      },
      required: ["name_path"]
    }
  },
  {
    name: "syntropy_serena_write_memory",
    description: "Store project context and knowledge in memory",
    inputSchema: {
      type: "object" as const,
      properties: {
        memory_type: {
          type: "string",
          description: "Type of memory (e.g., 'architecture', 'pattern', 'note')"
        },
        content: {
          type: "string",
          description: "Content to store"
        }
      },
      required: ["memory_type", "content"]
    }
  },
  {
    name: "syntropy_serena_create_text_file",
    description: "Create a new text file in the project",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "File path to create"
        },
        content: {
          type: "string",
          description: "File content"
        }
      },
      required: ["path", "content"]
    }
  },
  {
    name: "syntropy_serena_activate_project",
    description: "Switch active project for Serena to work with",
    inputSchema: {
      type: "object" as const,
      properties: {
        project: {
          type: "string",
          description: "Path to project root"
        }
      },
      required: ["project"]
    }
  },
  {
    name: "syntropy_serena_list_dir",
    description: "List directory contents with symbols",
    inputSchema: {
      type: "object" as const,
      properties: {
        directory_path: {
          type: "string",
          description: "Relative path to directory (relative to project root)"
        }
      },
      required: ["directory_path"]
    }
  },
  {
    name: "syntropy_serena_read_file",
    description: "Read file contents",
    inputSchema: {
      type: "object" as const,
      properties: {
        relative_path: {
          type: "string",
          description: "Relative path to file to read (relative to project root)"
        }
      },
      required: ["relative_path"]
    }
  },

  // ============ FILESYSTEM TOOLS (9) ============
  {
    name: "syntropy_filesystem_read_file",
    description: "Read file (deprecated - use read_text_file)",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "File path to read"
        },
        tail: {
          type: "number",
          description: "If provided, returns only the last N lines of the file"
        },
        head: {
          type: "number",
          description: "If provided, returns only the first N lines of the file"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_read_text_file",
    description: "Read text file contents",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "Path to text file"
        },
        tail: {
          type: "number",
          description: "If provided, returns only the last N lines of the file"
        },
        head: {
          type: "number",
          description: "If provided, returns only the first N lines of the file"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_read_media_file",
    description: "Read media file (images, etc.)",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "Path to media file"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_read_multiple_files",
    description: "Read multiple files at once",
    inputSchema: {
      type: "object" as const,
      properties: {
        paths: {
          type: "array",
          description: "Array of file paths to read"
        }
      },
      required: ["paths"]
    }
  },
  {
    name: "syntropy_filesystem_list_directory",
    description: "List directory contents",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "Directory path"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_list_directory_with_sizes",
    description: "List directory contents with file sizes",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "Directory path"
        },
        sortBy: {
          type: "string",
          description: "Sort entries by name or size"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_create_directory",
    description: "Create a directory",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "Directory path to create"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_move_file",
    description: "Move or rename a file",
    inputSchema: {
      type: "object" as const,
      properties: {
        source: {
          type: "string",
          description: "Source file path"
        },
        destination: {
          type: "string",
          description: "Destination file path"
        }
      },
      required: ["source", "destination"]
    }
  },
  {
    name: "syntropy_filesystem_write_file",
    description: "Write or overwrite file",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "File path to write"
        },
        content: {
          type: "string",
          description: "Content to write"
        }
      },
      required: ["path", "content"]
    }
  },
  {
    name: "syntropy_filesystem_edit_file",
    description: "Edit file using line-based operations",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "File path to edit"
        },
        edits: {
          type: "array",
          description: "Array of edit operations"
        },
        dryRun: {
          type: "boolean",
          description: "Preview changes using git-style diff format"
        }
      },
      required: ["path", "edits"]
    }
  },
  {
    name: "syntropy_filesystem_search_files",
    description: "Recursively search for files matching pattern",
    inputSchema: {
      type: "object" as const,
      properties: {
        pattern: {
          type: "string",
          description: "File name pattern or glob"
        },
        directory: {
          type: "string",
          description: "Directory to search in"
        }
      },
      required: ["pattern"]
    }
  },
  {
    name: "syntropy_filesystem_directory_tree",
    description: "Get JSON directory tree structure",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "Root directory path"
        },
        max_depth: {
          type: "number",
          description: "Maximum depth to traverse"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_get_file_info",
    description: "Get file metadata and information",
    inputSchema: {
      type: "object" as const,
      properties: {
        path: {
          type: "string",
          description: "File path"
        }
      },
      required: ["path"]
    }
  },
  {
    name: "syntropy_filesystem_list_allowed_directories",
    description: "List directories allowed for access",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: []
    }
  },

  // ============ GIT TOOLS (5) ============
  {
    name: "syntropy_git_git_status",
    description: "Get repository status",
    inputSchema: {
      type: "object" as const,
      properties: {
        repo_path: {
          type: "string",
          description: "Path to git repository"
        }
      },
      required: ["repo_path"]
    }
  },
  {
    name: "syntropy_git_git_diff",
    description: "Show git differences",
    inputSchema: {
      type: "object" as const,
      properties: {
        repo_path: {
          type: "string",
          description: "Path to git repository"
        },
        staged: {
          type: "boolean",
          description: "Show staged changes only"
        }
      },
      required: ["repo_path"]
    }
  },
  {
    name: "syntropy_git_git_log",
    description: "Show commit history",
    inputSchema: {
      type: "object" as const,
      properties: {
        repo_path: {
          type: "string",
          description: "Path to git repository"
        },
        max_count: {
          type: "number",
          description: "Maximum commits to show"
        }
      },
      required: ["repo_path"]
    }
  },
  {
    name: "syntropy_git_git_add",
    description: "Stage files for commit",
    inputSchema: {
      type: "object" as const,
      properties: {
        repo_path: {
          type: "string",
          description: "Path to git repository"
        },
        paths: {
          type: "array",
          items: { type: "string" },
          description: "File paths to stage"
        }
      },
      required: ["repo_path", "paths"]
    }
  },
  {
    name: "syntropy_git_git_commit",
    description: "Create git commit",
    inputSchema: {
      type: "object" as const,
      properties: {
        repo_path: {
          type: "string",
          description: "Path to git repository"
        },
        message: {
          type: "string",
          description: "Commit message"
        }
      },
      required: ["repo_path", "message"]
    }
  },

  // ============ CONTEXT7 TOOLS (2) ============
  {
    name: "syntropy_context7_resolve_library_id",
    description: "Find library ID for documentation lookup",
    inputSchema: {
      type: "object" as const,
      properties: {
        library_name: {
          type: "string",
          description: "Library name to resolve"
        }
      },
      required: ["library_name"]
    }
  },
  {
    name: "syntropy_context7_get_library_docs",
    description: "Fetch library documentation",
    inputSchema: {
      type: "object" as const,
      properties: {
        library_id: {
          type: "string",
          description: "Library ID"
        },
        section: {
          type: "string",
          description: "Documentation section"
        }
      },
      required: ["library_id"]
    }
  },

  // ============ THINKING TOOLS (1) ============
  {
    name: "syntropy_thinking_sequentialthinking",
    description: "Sequential thinking process for complex reasoning",
    inputSchema: {
      type: "object" as const,
      properties: {
        question: {
          type: "string",
          description: "Question or problem to think through"
        }
      },
      required: ["question"]
    }
  },

  // ============ LINEAR TOOLS (5) ============
  {
    name: "syntropy_linear_create_issue",
    description: "Create Linear issue",
    inputSchema: {
      type: "object" as const,
      properties: {
        title: {
          type: "string",
          description: "Issue title"
        },
        description: {
          type: "string",
          description: "Issue description"
        },
        team_id: {
          type: "string",
          description: "Team ID"
        }
      },
      required: ["title", "team_id"]
    }
  },
  {
    name: "syntropy_linear_get_issue",
    description: "Get issue details",
    inputSchema: {
      type: "object" as const,
      properties: {
        issue_id: {
          type: "string",
          description: "Issue ID"
        }
      },
      required: ["issue_id"]
    }
  },
  {
    name: "syntropy_linear_list_issues",
    description: "List issues",
    inputSchema: {
      type: "object" as const,
      properties: {
        team_id: {
          type: "string",
          description: "Team ID"
        },
        status: {
          type: "string",
          description: "Filter by status"
        }
      },
      required: []
    }
  },
  {
    name: "syntropy_linear_update_issue",
    description: "Update issue",
    inputSchema: {
      type: "object" as const,
      properties: {
        issue_id: {
          type: "string",
          description: "Issue ID"
        },
        updates: {
          type: "object",
          description: "Updates to apply"
        }
      },
      required: ["issue_id"]
    }
  },
  {
    name: "syntropy_linear_list_projects",
    description: "List projects",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: []
    }
  },

  // ============ REPOMIX TOOLS (1) ============
  {
    name: "syntropy_repomix_pack_codebase",
    description: "Package codebase for AI processing",
    inputSchema: {
      type: "object" as const,
      properties: {
        directory: {
          type: "string",
          description: "Directory to package"
        }
      },
      required: ["directory"]
    }
  }
];
