# Codebase Structure

## Top-Level Layout
```
ctx-eng-plus/
├── tools/                  # Main CLI package (primary workspace)
├── docs/                   # Documentation and research
├── .serena/                # Serena MCP configuration
├── .claude/                # Claude configuration
├── CLAUDE.md               # Project-specific guidance
├── README.md               # Main documentation
└── .gitignore              # Git ignore rules
```

## Tools Package (Main Component)
```
tools/
├── ce/                     # Source code package
│   ├── __init__.py         # Package metadata and version
│   ├── __main__.py         # CLI entry point (argparse)
│   ├── core.py             # Core functionality
│   ├── validate.py         # 3-level validation gates
│   └── context.py          # Context management
├── tests/                  # Test suite
│   ├── test_cli.py         # CLI interface tests
│   ├── test_core.py        # Core function tests
│   ├── test_validate.py    # Validation tests
│   └── test_context.py     # Context management tests
├── pyproject.toml          # UV package configuration
├── uv.lock                 # UV lock file (auto-generated)
├── README.md               # User documentation
└── bootstrap.sh            # Setup script
```

## Core Modules Overview

### ce/core.py
**Functions**: `run_cmd`, `read_file`, `write_file`, `git_status`, `git_diff`, `git_checkpoint`
- Shell command execution with timeout
- File operations (read/write)
- Git operations (status, diff, checkpoints)

### ce/validate.py
**Functions**: `validate_level_1`, `validate_level_2`, `validate_level_3`, `validate_all`
- 3-level validation gate system
- Progressive validation complexity

### ce/context.py
**Functions**: `sync`, `health`, `prune`
- Context synchronization with codebase
- Health checks for context drift
- Pruning stale context data

### ce/__main__.py
- CLI entry point using argparse
- Command routing and argument parsing
- Subcommands: validate, git, context

## Documentation Structure
```
docs/
└── research/               # Research and design documentation
    ├── 00-index.md         # Documentation index
    ├── 01-prp-system.md    # PRP system design
    ├── 02-context-engineering-foundations.md
    ├── 03-mcp-orchestration.md
    ├── 04-self-healing-framework.md
    ├── 05-persistence-layers.md
    ├── 06-workflow-patterns.md
    ├── 07-commands-reference.md
    ├── 08-validation-testing.md
    ├── 09-best-practices-antipatterns.md
    ├── 10-tooling-configuration.md
    └── 11-claude-code-features.md
```

## Key Design Patterns

### Minimal Dependencies
- Stdlib-only approach
- No external runtime dependencies
- pytest for testing only (dev dependency)

### Single Responsibility
- Each module handles one aspect
- core.py: system operations
- validate.py: validation logic
- context.py: context management

### CLI Architecture
- Subcommand-based interface
- JSON output support for scripting
- Clear error messages with troubleshooting guidance