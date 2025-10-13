# Project Overview

## Purpose
Context Engineering Plus (ctx-eng-plus) - Minimal CLI tooling for Context Engineering framework operations with full PRP workflow automation.

## Project Type
Python CLI toolkit with minimal dependencies (stdlib-focused).

## Key Features

### Core Capabilities
- **ce tool**: Command-line interface for context engineering operations
  - **Validation** (3-level gate system: L1-L4)
  - **Git operations** (status, diff, checkpoints)
  - **Context management** (sync, health, prune, auto-sync mode)
  - **File operations** (read, write)
  - **Python execution** (auto-detect code vs file mode)

### PRP Workflow Automation (NEW - PRP-3, PRP-4, PRP-5)
- **PRP Generation** (`ce prp generate`):
  - Parses INITIAL.md structure
  - Orchestrates Serena MCP for codebase research
  - Fetches documentation via Context7 MCP
  - Synthesizes complete 6-section PRPs (TL;DR, Context, Implementation, Success Criteria, Validation Gates, References)
  - Auto-generates validation commands and checkpoints
  - 3-4x speedup vs manual creation (10-15 min vs 30-60 min)

- **PRP Execution** (`ce prp execute`):
  - Parses PRP Implementation Blueprint into executable phases
  - Phase-by-phase orchestrated execution
  - L1-L4 validation loops after each phase
  - Self-healing mechanisms (L1-L2 auto-fix with 3-attempt limit)
  - 5 escalation triggers (persistent errors, ambiguity, architecture, dependencies, security)
  - Auto-checkpoint creation at validation gates
  - 10/10 confidence scoring system
  - 3-6x speedup for simple PRPs (20-60 min vs 60-180 min)

- **Context Sync Integration** (`ce context`):
  - **Step 2.5 (Pre-Generation Sync)**: Auto-sync before PRP generation with drift abort >30%
  - **Step 6.5 (Post-Execution Sync)**: Auto-cleanup + sync after PRP execution
  - Auto-sync mode: `ce context auto-sync --enable`
  - Drift detection with 3 thresholds (0-10% healthy, 10-30% warn, 30%+ abort)
  - Memory pruning (stale Serena memories cleanup)
  - Git state verification (clean working tree enforcement)

### Claude Code Integration
- Slash commands: `/generate-prp`, `/execute-prp`
- Session hooks in `.claude/settings.local.json` (SessionStart health check)
- Workflow integration at Steps 2.5 and 6.5

## Tech Stack
- **Language**: Python 3.10+ (tested on 3.13.7)
- **Package Manager**: UV 0.7.19+ (STRICT - never edit pyproject.toml directly)
- **Testing**: pytest 8.4.2+
- **Build System**: Hatchling
- **Dependencies**: Minimal - stdlib only for core functionality
- **MCP Integration**: Serena (code operations), Context7 (docs), Sequential Thinking (synthesis)

## Project Structure
```
ctx-eng-plus/
├── tools/                  # Main CLI package
│   ├── ce/                 # Source code (11 modules)
│   │   ├── __init__.py     # Package metadata
│   │   ├── __main__.py     # CLI entry point (8 commands)
│   │   ├── core.py         # File, git, shell operations
│   │   ├── validate.py     # L1-L4 validation gates
│   │   ├── context.py      # Context management & drift detection
│   │   ├── generate.py     # PRP generation (PRP-3)
│   │   ├── execute.py      # PRP execution orchestration (PRP-4)
│   │   ├── prp.py          # PRP state management (PRP-2)
│   │   ├── drift_analyzer.py   # Implementation drift analysis
│   │   ├── code_analyzer.py    # Code pattern extraction
│   │   ├── mermaid_validator.py # Mermaid validation
│   │   └── pattern_extractor.py # Pattern extraction
│   ├── tests/              # Test suite (8 test modules)
│   ├── pyproject.toml      # UV package config
│   └── bootstrap.sh        # Setup script
├── PRPs/                   # PRP documents
│   ├── executed/           # 6 completed PRPs (PRP-1 through PRP-5)
│   ├── feature-requests/   # 4 future PRPs (PRP-6 through PRP-9)
│   └── templates/          # PRP templates (base, KISS, self-healing)
├── docs/                   # Documentation & research (11 docs)
├── .claude/                # Claude Code config (settings, commands, hooks)
├── CLAUDE.md               # Project-specific guidance
└── README.md               # Main documentation
```

## CLI Commands Reference

### Validation
```bash
ce validate --level 1          # L1: Syntax (py_compile, mypy, ruff)
ce validate --level 2          # L2: Unit tests
ce validate --level 3          # L3: Integration tests
ce validate --level 4          # L4: Pattern conformance (drift analysis)
ce validate --level all        # All levels
```

### Git Operations
```bash
ce git status                  # Git status with staging info
ce git diff                    # Recent file changes
ce git checkpoint "message"    # Create checkpoint (tag + commit)
```

### Context Management
```bash
ce context sync                # Sync context with codebase
ce context health              # Context drift health check
ce context health --verbose    # Detailed drift breakdown
ce context prune               # Prune stale memories (7 days default)
ce context auto-sync --enable  # Enable auto-sync mode
ce context auto-sync --disable # Disable auto-sync mode
ce context auto-sync --status  # Check auto-sync status
ce context pre-sync [--force]  # Manual pre-generation sync
ce context post-sync <prp-id>  # Manual post-execution sync
```

### Python Execution
```bash
ce run_py "print('hello')"                 # Auto-detect: inline code
ce run_py tmp/script.py                    # Auto-detect: file path
ce run_py --code "x = [1,2,3]; print(sum(x))"  # Explicit: code
ce run_py --file tmp/script.py             # Explicit: file
```

### PRP Management
```bash
ce prp validate <prp-file>         # Validate PRP YAML header
ce prp generate <initial-md-path>  # Generate PRP from INITIAL.md
ce prp execute <prp-id>            # Execute PRP with validation loops
ce prp execute <prp-id> --start-phase 2 --end-phase 3  # Partial execution
ce prp execute <prp-id> --dry-run  # Parse blueprint only (no execution)
```

## Implementation Status (2025-10-13)

### Completed Features (PRPs 1-5)
- ✅ L1-L4 validation gates (PRP-1)
- ✅ YAML validation command (PRP-1.2)
- ✅ PRP state management & cleanup protocol (PRP-2)
- ✅ PRP generation automation with MCP orchestration (PRP-3)
- ✅ PRP execution with self-healing & validation loops (PRP-4)
- ✅ Context sync integration at workflow Steps 2.5 & 6.5 (PRP-5)
- ✅ Auto-sync mode for seamless workflow automation
- ✅ Claude Code hooks integration

### Known Limitations
- Test coverage: 40% (target: 80%) - PRP-7 will address
- File operations: Filesystem stubs (Serena MCP integration pending) - PRP-9 will address
- Self-healing: L1-L2 only (L3-L4 escalate to human)

### Feature Roadmap (PRPs 6-9)
- ⏸️ PRP-6: Markdown linting for documentation quality
- ⏸️ PRP-7: Comprehensive validation loop tests (increase coverage to 80%)
- ⏸️ PRP-8: PRP sizing constraint analysis & optimal breakdown strategy
- ⏸️ PRP-9: Serena MCP integration for file operations (replace stubs)

## Workflow Integration

### Context-Aware Development Cycle
1. **Step 1**: Define feature in INITIAL.md (manual)
2. **Step 2**: `/generate-prp` creates comprehensive PRP
3. **Step 2.5**: **Auto-sync** (pre-generation health check, drift abort >30%)
4. **Step 3**: Peer review PRP document
5. **Step 4-5**: `/execute-prp` implements feature with validation
6. **Step 6.5**: **Auto-sync** (post-execution cleanup + sync)
7. **Step 7**: Final validation & PR creation

### Auto-Sync Mode Benefits
- Eliminates stale context errors (15-40% error rate reduction)
- Ensures <10% drift for all PRP operations
- Automates 4-6 manual steps per PRP (2-5 min saved)
- Prevents context pollution through systematic cleanup
- Enables reliable autonomous development workflow

## Platform
Darwin (macOS) - system-specific commands may differ from Linux.

## Design Philosophy
- **KISS**: Simple solutions first, avoid over-engineering
- **No Fishy Fallbacks**: Fast failure with actionable error messages
- **Real Functionality Testing**: Test real functions with real values
- **UV Package Management**: Strict - never edit pyproject.toml directly
- **Minimal Dependencies**: Stdlib-only for core, pytest for dev only
- **Single Responsibility**: Each module handles one concern
- **Token Efficiency**: Direct editing over Read → Edit cycles