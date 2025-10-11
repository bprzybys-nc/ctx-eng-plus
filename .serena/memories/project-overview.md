# Project Overview

## Purpose
Context Engineering Plus (ctx-eng-plus) - Minimal CLI tooling for Context Engineering framework operations.

## Project Type
Python CLI toolkit with minimal dependencies (stdlib-focused).

## Key Features
- **ce tool**: Command-line interface for context engineering operations
  - Validation (3-level gate system)
  - Git operations (status, diff, checkpoints)
  - Context management (sync, health, prune)
  - File operations (read, write)

## Tech Stack
- **Language**: Python 3.10+ (tested on 3.13.7)
- **Package Manager**: UV 0.7.19+ (STRICT - never edit pyproject.toml directly)
- **Testing**: pytest 8.4.2+
- **Build System**: Hatchling
- **Dependencies**: Minimal - stdlib only for core functionality

## Project Structure
```
ctx-eng-plus/
├── tools/                  # Main CLI package
│   ├── ce/                 # Source code
│   │   ├── __init__.py     # Package metadata
│   │   ├── __main__.py     # CLI entry point
│   │   ├── core.py         # File, git, shell operations
│   │   ├── validate.py     # 3-level validation gates
│   │   └── context.py      # Context management
│   ├── tests/              # Test suite
│   ├── pyproject.toml      # UV package config
│   └── bootstrap.sh        # Setup script
├── docs/                   # Documentation
│   └── research/           # Research and design docs
├── CLAUDE.md               # Project-specific guidance
└── README.md               # Main documentation
```

## Platform
Darwin (macOS) - system-specific commands may differ from Linux.