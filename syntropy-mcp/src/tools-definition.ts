/**
 * Proper MCP Tool Definitions with Input Schemas
 *
 * This follows MCP best practices by including inputSchema for each tool.
 * inputSchema is CRITICAL for Claude Code to properly register and expose tools.
 * 
 * ✅ All schemas are JSON Schema Draft 2020-12 compliant
 * ✅ All array types include proper 'items' definitions
 * ✅ No invalid 'any[]' type usage
 */

export const SYNTROPY_TOOLS = [
  // ============ SERENA TOOLS (9) ============
  {
    name: "serena_find_symbol",
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
    name: "serena_get_symbols_overview",
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
    name: "serena_search_for_pattern",
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
    name: "serena_find_referencing_symbols",
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
    name: "serena_write_memory",
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
    name: "serena_create_text_file",
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
    name: "serena_activate_project",
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
    name: "serena_list_dir",
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
    name: "serena_read_file",
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


  // ============ FILESYSTEM TOOLS (13) ============
  {
    name: "filesystem_read_file",
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
    name: "filesystem_read_text_file",
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
    name: "filesystem_read_media_file",
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
    name: "filesystem_read_multiple_files",
    description: "Read multiple files at once",
    inputSchema: {
      type: "object" as const,
      properties: {
        paths: {
          type: "array",
          items: { type: "string" },
          description: "Array of file paths to read"
        }
      },
      required: ["paths"]
    }
  },
  {
    name: "filesystem_list_directory",
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
    name: "filesystem_list_directory_with_sizes",
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
    name: "filesystem_create_directory",
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
    name: "filesystem_move_file",
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
    name: "filesystem_write_file",
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
    name: "filesystem_edit_file",
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
          items: {
            type: "object",
            properties: {
              oldText: { type: "string" },
              newText: { type: "string" }
            },
            required: ["oldText", "newText"]  // Add this
          },
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
    name: "filesystem_search_files",
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
    name: "filesystem_directory_tree",
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
    name: "filesystem_get_file_info",
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
    name: "filesystem_list_allowed_directories",
    description: "List directories allowed for access",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: []
    }
  },


  // ============ GIT TOOLS (5) ============
  {
    name: "git_git_status",
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
    name: "git_git_diff",
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
    name: "git_git_log",
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
    name: "git_git_add",
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
    name: "git_git_commit",
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
    name: "context7_resolve_library_id",
    description: "Find library ID for documentation lookup",
    inputSchema: {
      type: "object" as const,
      properties: {
        libraryName: {
          type: "string",
          description: "Library name to resolve (e.g., 'numpy', 'react')"
        }
      },
      required: ["libraryName"]
    }
  },
  {
    name: "context7_get_library_docs",
    description: "Fetch library documentation",
    inputSchema: {
      type: "object" as const,
      properties: {
        context7CompatibleLibraryID: {
          type: "string",
          description: "Context7-compatible library ID (e.g., '/mongodb/docs', '/vercel/next.js')"
        },
        topic: {
          type: "string",
          description: "Focus the docs on a specific topic (e.g., 'routing', 'hooks')"
        },
        tokens: {
          type: "number",
          description: "Maximum number of tokens to return (default 5000)"
        }
      },
      required: ["context7CompatibleLibraryID"]
    }
  },


  // ============ THINKING TOOLS (1) ============
  {
    name: "thinking_sequentialthinking",
    description: "Sequential thinking process for complex reasoning",
    inputSchema: {
      type: "object" as const,
      properties: {
        thought: {
          type: "string",
          description: "The current thought or reasoning step"
        },
        thoughtNumber: {
          type: "number",
          description: "Sequential number of this thought"
        },
        totalThoughts: {
          type: "number",
          description: "Estimated total number of thoughts needed"
        },
        nextThoughtNeeded: {
          type: "boolean",
          description: "Whether another thought is needed to continue reasoning"
        },
        isRevision: {
          type: "boolean",
          description: "Whether this thought revises a previous thought"
        },
        revisesThought: {
          type: "number",
          description: "Number of the thought being revised (if isRevision is true)"
        },
        branchFromThought: {
          type: "number",
          description: "Number of the thought this branches from (if branching)"
        },
        branchId: {
          type: "string",
          description: "Identifier for this branch"
        },
        needsMoreThoughts: {
          type: "boolean",
          description: "Whether more thoughts are needed beyond totalThoughts"
        }
      },
      required: ["thought", "thoughtNumber", "totalThoughts", "nextThoughtNeeded"]
    }
  },


  // ============ LINEAR TOOLS (5) ============
  {
    name: "linear_create_issue",
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
    name: "linear_get_issue",
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
    name: "linear_list_issues",
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
    name: "linear_update_issue",
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
          description: "Updates to apply",
          additionalProperties: true  // Allow any properties
        }
      },
      required: ["issue_id"]
    }
  },
  {
    name: "linear_list_projects",
    description: "List projects",
    inputSchema: {
      type: "object" as const,
      properties: {},
      required: []
    }
  },


  // ============ REPOMIX TOOLS (1) ============
  {
    name: "repomix_pack_codebase",
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
  },


  // ============ GITHUB TOOLS (27) ============
  {
    name: "github_create_or_update_file",
    description: "Create or update a single file in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        path: { type: "string", description: "Path where to create/update the file" },
        content: { type: "string", description: "Content of the file" },
        message: { type: "string", description: "Commit message" },
        branch: { type: "string", description: "Branch to create/update the file in" },
        sha: { type: "string", description: "SHA of the file being replaced (required when updating existing files)" }
      },
      required: ["owner", "repo", "path", "content", "message", "branch"]
    }
  },
  {
    name: "github_search_repositories",
    description: "Search for GitHub repositories",
    inputSchema: {
      type: "object" as const,
      properties: {
        query: { type: "string", description: "Search query (see GitHub search syntax)" },
        page: { type: "number", description: "Page number for pagination (default: 1)" },
        perPage: { type: "number", description: "Number of results per page (default: 30, max: 100)" }
      },
      required: ["query"]
    }
  },
  {
    name: "github_create_repository",
    description: "Create a new GitHub repository in your account",
    inputSchema: {
      type: "object" as const,
      properties: {
        name: { type: "string", description: "Repository name" },
        description: { type: "string", description: "Repository description" },
        private: { type: "boolean", description: "Whether the repository should be private" },
        autoInit: { type: "boolean", description: "Initialize with README.md" }
      },
      required: ["name"]
    }
  },
  {
    name: "github_get_file_contents",
    description: "Get the contents of a file or directory from a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        path: { type: "string", description: "Path to the file or directory" },
        branch: { type: "string", description: "Branch to get contents from" }
      },
      required: ["owner", "repo", "path"]
    }
  },
  {
    name: "github_push_files",
    description: "Push multiple files to a GitHub repository in a single commit",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        branch: { type: "string", description: "Branch to push to (e.g., 'main' or 'master')" },
        files: {
          type: "array",
          items: {
            type: "object",
            properties: {
              path: { type: "string" },
              content: { type: "string" }
            },
            required: ["path", "content"]
          },
          description: "Array of files to push"
        },
        message: { type: "string", description: "Commit message" }
      },
      required: ["owner", "repo", "branch", "files", "message"]
    }
  },
  {
    name: "github_create_issue",
    description: "Create a new issue in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        title: { type: "string", description: "Issue title" },
        body: { type: "string", description: "Issue body" },
        assignees: {
          type: "array",
          items: { type: "string" },
          description: "Assignees (GitHub usernames)"
        },
        milestone: { type: "number", description: "Milestone number" },
        labels: {
          type: "array",
          items: { type: "string" },
          description: "Labels"
        }
      },
      required: ["owner", "repo", "title"]
    }
  },
  {
    name: "github_create_pull_request",
    description: "Create a new pull request in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        title: { type: "string", description: "Pull request title" },
        body: { type: "string", description: "Pull request body/description" },
        head: { type: "string", description: "The name of the branch where your changes are implemented" },
        base: { type: "string", description: "The name of the branch you want the changes pulled into" },
        draft: { type: "boolean", description: "Whether to create the pull request as a draft" },
        maintainer_can_modify: { type: "boolean", description: "Whether maintainers can modify the pull request" }
      },
      required: ["owner", "repo", "title", "head", "base"]
    }
  },
  {
    name: "github_fork_repository",
    description: "Fork a GitHub repository to your account or specified organization",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        organization: { type: "string", description: "Optional: organization to fork to (defaults to your personal account)" }
      },
      required: ["owner", "repo"]
    }
  },
  {
    name: "github_create_branch",
    description: "Create a new branch in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        branch: { type: "string", description: "Name for the new branch" },
        from_branch: { type: "string", description: "Optional: source branch to create from (defaults to the repository's default branch)" }
      },
      required: ["owner", "repo", "branch"]
    }
  },
  {
    name: "github_list_commits",
    description: "Get list of commits of a branch in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        sha: { type: "string", description: "Commit SHA" },
        page: { type: "number", description: "Page number" },
        perPage: { type: "number", description: "Results per page" }
      },
      required: ["owner", "repo"]
    }
  },
  {
    name: "github_list_issues",
    description: "List issues in a GitHub repository with filtering options",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        direction: { type: "string", description: "Direction (asc or desc)" },
        labels: {
          type: "array",
          items: { type: "string" },
          description: "Labels to filter by"
        },
        page: { type: "number", description: "Page number" },
        per_page: { type: "number", description: "Results per page" },
        since: { type: "string", description: "Since date (ISO 8601 format)" },
        sort: { type: "string", description: "Sort by (created, updated, comments)" },
        state: { type: "string", description: "Issue state (open, closed, all)" }
      },
      required: ["owner", "repo"]
    }
  },
  {
    name: "github_update_issue",
    description: "Update an existing issue in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        issue_number: { type: "number", description: "Issue number" },
        title: { type: "string", description: "Issue title" },
        body: { type: "string", description: "Issue body" },
        assignees: {
          type: "array",
          items: { type: "string" },
          description: "Assignees (GitHub usernames)"
        },
        milestone: { type: "number", description: "Milestone number" },
        labels: {
          type: "array",
          items: { type: "string" },
          description: "Labels"
        },
        state: { type: "string", description: "Issue state (open or closed)" }
      },
      required: ["owner", "repo", "issue_number"]
    }
  },
  {
    name: "github_add_issue_comment",
    description: "Add a comment to an existing issue",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        issue_number: { type: "number", description: "Issue number" },
        body: { type: "string", description: "Comment body" }
      },
      required: ["owner", "repo", "issue_number", "body"]
    }
  },
  {
    name: "github_search_code",
    description: "Search for code across GitHub repositories",
    inputSchema: {
      type: "object" as const,
      properties: {
        q: { type: "string", description: "Search query" },
        order: { type: "string", description: "Sort order (asc or desc)" },
        page: { type: "number", description: "Page number" },
        per_page: { type: "number", description: "Results per page" }
      },
      required: ["q"]
    }
  },
  {
    name: "github_search_issues",
    description: "Search for issues and pull requests across GitHub repositories",
    inputSchema: {
      type: "object" as const,
      properties: {
        q: { type: "string", description: "Search query" },
        order: { type: "string", description: "Sort order (asc or desc)" },
        page: { type: "number", description: "Page number" },
        per_page: { type: "number", description: "Results per page" },
        sort: { type: "string", description: "Sort by (comments, reactions, created, updated)" }
      },
      required: ["q"]
    }
  },
  {
    name: "github_search_users",
    description: "Search for users on GitHub",
    inputSchema: {
      type: "object" as const,
      properties: {
        q: { type: "string", description: "Search query" },
        order: { type: "string", description: "Sort order (asc or desc)" },
        page: { type: "number", description: "Page number" },
        per_page: { type: "number", description: "Results per page" },
        sort: { type: "string", description: "Sort by (followers, repositories, joined)" }
      },
      required: ["q"]
    }
  },
  {
    name: "github_get_issue",
    description: "Get details of a specific issue in a GitHub repository",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner" },
        repo: { type: "string", description: "Repository name" },
        issue_number: { type: "number", description: "Issue number" }
      },
      required: ["owner", "repo", "issue_number"]
    }
  },
  {
    name: "github_get_pull_request",
    description: "Get details of a specific pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },
  {
    name: "github_list_pull_requests",
    description: "List and filter repository pull requests",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        state: { type: "string", description: "State of the pull requests to return (open, closed, all)" },
        head: { type: "string", description: "Filter by head user or head organization and branch name" },
        base: { type: "string", description: "Filter by base branch name" },
        sort: { type: "string", description: "What to sort results by (created, updated, popularity, long-running)" },
        direction: { type: "string", description: "The direction of the sort (asc or desc)" },
        per_page: { type: "number", description: "Results per page (max 100)" },
        page: { type: "number", description: "Page number of the results" }
      },
      required: ["owner", "repo"]
    }
  },
  {
    name: "github_create_pull_request_review",
    description: "Create a review on a pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" },
        commit_id: { type: "string", description: "The SHA of the commit that needs a review" },
        body: { type: "string", description: "The body text of the review" },
        event: { type: "string", description: "The review action to perform (APPROVE, REQUEST_CHANGES, COMMENT)" },
        comments: {
          type: "array",
          items: {
            type: "object",
            properties: {
              path: { type: "string" },
              position: { type: "number" },
              body: { type: "string" }
            },
            required: ["path", "body"]
          },
          description: "Comments to post as part of the review (specify either position or line, not both)"
        }
      },
      required: ["owner", "repo", "pull_number", "body", "event"]
    }
  },
  {
    name: "github_merge_pull_request",
    description: "Merge a pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" },
        commit_title: { type: "string", description: "Title for the automatic commit message" },
        commit_message: { type: "string", description: "Extra detail to append to automatic commit message" },
        merge_method: { type: "string", description: "Merge method to use (merge, squash, rebase)" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },
  {
    name: "github_get_pull_request_files",
    description: "Get the list of files changed in a pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },
  {
    name: "github_get_pull_request_status",
    description: "Get the combined status of all status checks for a pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },
  {
    name: "github_update_pull_request_branch",
    description: "Update a pull request branch with the latest changes from the base branch",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" },
        expected_head_sha: { type: "string", description: "The expected SHA of the pull request's HEAD ref" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },
  {
    name: "github_get_pull_request_comments",
    description: "Get the review comments on a pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },
  {
    name: "github_get_pull_request_reviews",
    description: "Get the reviews on a pull request",
    inputSchema: {
      type: "object" as const,
      properties: {
        owner: { type: "string", description: "Repository owner (username or organization)" },
        repo: { type: "string", description: "Repository name" },
        pull_number: { type: "number", description: "Pull request number" }
      },
      required: ["owner", "repo", "pull_number"]
    }
  },


  // ============ PERPLEXITY TOOLS (1) ============
  {
    name: "perplexity_perplexity_ask",
    description: "Engages in a conversation using the Sonar API. Accepts an array of messages (each with a role and content) and returns a ask completion response from the Perplexity model",
    inputSchema: {
      type: "object" as const,
      properties: {
        messages: {
          type: "array",
          items: {
            type: "object",
            properties: {
              role: { type: "string", description: "Message role (system, user, assistant)" },
              content: { type: "string", description: "Message content" }
            },
            required: ["role", "content"]
          },
          description: "Array of conversation messages"
        }
      },
      required: ["messages"]
    }
  },


  // ============ SYNTROPY TOOLS (7) ============
  {
    name: "denoise",
    description: "Boil out noise from documents—remove verbosity while strictly guaranteeing complete retention of all essential information",
    inputSchema: {
      type: "object" as const,
      properties: {
        file_path: {
          type: "string",
          description: "Path to document to denoise (.md, .txt, documentation files)"
        },
        target_reduction: {
          type: "number",
          description: "Target compression percentage (default: 70). Range: 50-80%"
        },
        dry_run: {
          type: "boolean",
          description: "Preview changes without writing file (default: false)"
        },
        verbose: {
          type: "boolean",
          description: "Show detailed statistics and validation report (default: false)"
        }
      },
      required: ["file_path"]
    }
  },
  {
    name: "healthcheck",
    description: "Check health status of Syntropy server and all underlying MCP servers",
    inputSchema: {
      type: "object" as const,
      properties: {
        detailed: {
          type: "boolean",
          description: "Include detailed diagnostics (call counts, last errors). Default: false"
        },
        timeout_ms: {
          type: "number",
          description: "Timeout in milliseconds for each server check. Default: 2000 (2 seconds)"
        }
      },
      required: []
    }
  },
  {
    name: "syntropy_init_project",
    description: "Initialize Context Engineering project structure with boilerplate copy and slash command upsert",
    inputSchema: {
      type: "object" as const,
      properties: {
        project_root: {
          type: "string",
          description: "Absolute path to project root directory"
        }
      },
      required: ["project_root"]
    }
  },
  {
    name: "syntropy_get_system_doc",
    description: "Access framework documentation from .ce/ directory",
    inputSchema: {
      type: "object" as const,
      properties: {
        project_root: {
          type: "string",
          description: "Absolute path to project root directory"
        },
        doc_path: {
          type: "string",
          description: "Relative path to document within .ce/ (e.g., 'RULES.md', 'examples/patterns.md')"
        }
      },
      required: ["project_root", "doc_path"]
    }
  },
  {
    name: "syntropy_get_user_doc",
    description: "Access user/project documentation from project root (excludes .ce/)",
    inputSchema: {
      type: "object" as const,
      properties: {
        project_root: {
          type: "string",
          description: "Absolute path to project root directory"
        },
        doc_path: {
          type: "string",
          description: "Relative path to document (e.g., 'README.md', 'PRPs/executed/PRP-1.md')"
        }
      },
      required: ["project_root", "doc_path"]
    }
  },
  {
    name: "syntropy_knowledge_search",
    description: "Search across all knowledge sources (framework docs, PRPs, examples, Serena memories)",
    inputSchema: {
      type: "object" as const,
      properties: {
        project_root: {
          type: "string",
          description: "Absolute path to project root directory"
        },
        query: {
          type: "string",
          description: "Search query text"
        },
        types: {
          type: "array",
          items: {
            type: "string",
            enum: ["pattern", "prp", "memory", "rule", "example"]
          },
          description: "Filter by entry types (optional)"
        },
        tags: {
          type: "array",
          items: { type: "string" },
          description: "Filter by tags (optional)"
        },
        limit: {
          type: "number",
          description: "Maximum number of results (default: 10)"
        }
      },
      required: ["project_root", "query"]
    }
  },
  {
    name: "syntropy_get_summary",
    description: "Get compact, readable summary of Syntropy MCP system (servers, tools, routing). Returns summary and persists to .ce/SYNTROPY-SUMMARY.md",
    inputSchema: {
      type: "object" as const,
      properties: {
        project_root: {
          type: "string",
          description: "Project root directory"
        },
        format: {
          type: "string",
          enum: ["text", "oneline", "json"],
          description: "Output format: text (default), oneline (bash-friendly), json"
        }
      },
      required: ["project_root"]
    }
  }
];
