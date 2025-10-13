# Codebase Structure

## Top-Level Layout
```
ctx-eng-plus/
├── tools/                  # Main CLI package (primary workspace)
├── docs/                   # Documentation and research
├── PRPs/                   # PRP documents and planning
├── .serena/                # Serena MCP configuration
├── .claude/                # Claude Code configuration
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
│   ├── core.py             # Core functionality (shell, git, file ops)
│   ├── validate.py         # 3-level validation gates
│   ├── context.py          # Context management & drift detection
│   ├── generate.py         # PRP generation (PRP-3)
│   ├── execute.py          # PRP execution orchestration (PRP-4)
│   ├── prp.py              # PRP state management (PRP-2)
│   ├── drift_analyzer.py   # Implementation drift analysis
│   ├── code_analyzer.py    # Code pattern extraction
│   ├── mermaid_validator.py # Mermaid diagram validation
│   └── pattern_extractor.py # Pattern extraction utilities
├── tests/                  # Test suite
│   ├── test_cli.py         # CLI interface tests
│   ├── test_core.py        # Core function tests
│   ├── test_validate.py    # Validation tests
│   ├── test_context.py     # Context management tests
│   ├── test_generate.py    # PRP generation tests
│   └── test_execute.py     # PRP execution tests
├── pyproject.toml          # UV package configuration
├── uv.lock                 # UV lock file (auto-generated)
├── README.md               # User documentation
└── bootstrap.sh            # Setup script
```

## Core Modules Overview

### ce/core.py
**Functions**: `run_cmd`, `read_file`, `write_file`, `git_status`, `git_diff`, `git_checkpoint`, `run_py`
- Shell command execution with timeout
- File operations (read/write)
- Git operations (status, diff, checkpoints)
- Python code execution (auto-detect mode)

### ce/validate.py
**Functions**: `validate_level_1`, `validate_level_2`, `validate_level_3`, `validate_level_4`, `validate_all`
- L1: Syntax validation (py_compile, mypy, ruff)
- L2: Unit tests
- L3: Integration tests
- L4: Pattern conformance (drift analysis)

### ce/context.py
**Functions**: `sync`, `health`, `prune`, `pre_generation_sync`, `post_execution_sync`, `calculate_drift_score`, `enable_auto_sync`, `disable_auto_sync`, `is_auto_sync_enabled`
- Context synchronization with codebase
- Health checks for context drift
- Pruning stale context data
- Pre/post workflow sync automation (Steps 2.5 and 6.5)
- Auto-sync mode management

### ce/generate.py (PRP-3)
**Functions**: `parse_initial_md`, `research_codebase`, `fetch_documentation`, `generate_prp`, `synthesize_tldr`, `synthesize_implementation`
- INITIAL.md parsing
- Codebase research orchestration (Serena MCP)
- Documentation fetching (Context7 MCP)
- PRP template synthesis
- All 6 PRP sections generation

### ce/execute.py (PRP-4)
**Functions**: `parse_blueprint`, `execute_prp`, `execute_phase`, `run_validation_loop`, `apply_self_healing_fix`, `check_escalation_triggers`
- PRP blueprint parsing
- Phase-by-phase execution
- L1-L4 validation loops
- Self-healing mechanisms (L1-L2 retries)
- Escalation flow (5 trigger types)

### ce/prp.py (PRP-2)
**Functions**: State management, checkpoint creation, cleanup protocol
- PRP session tracking
- Checkpoint management
- Ephemeral state cleanup

### ce/drift_analyzer.py
**Functions**: `analyze_implementation`, `calculate_drift_score`, `get_auto_fix_suggestions`
- Implementation vs specification drift analysis
- Drift scoring for L4 validation
- Auto-fix recommendations

### ce/code_analyzer.py
**Functions**: `analyze_code_patterns`, `_analyze_python`, `_analyze_typescript`, `determine_language`, `count_code_symbols`
- Language-specific pattern extraction
- Code symbol counting
- Generic pattern analysis

### ce/mermaid_validator.py
- Mermaid diagram validation
- Theme compatibility checking

### ce/pattern_extractor.py
- Pattern extraction utilities
- Code pattern analysis

### ce/__main__.py
**CLI Commands**:
- `ce validate` - Run validation gates (L1-L4)
- `ce git` - Git operations (status, diff, checkpoint)
- `ce context` - Context management (sync, health, prune, auto-sync)
- `ce run_py` - Execute Python code (auto-detect or explicit mode)
- `ce prp validate` - PRP YAML validation
- `ce prp generate` - PRP generation from INITIAL.md
- `ce prp execute` - PRP execution with validation loops

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

## PRP Structure
```
PRPs/
├── executed/               # Completed PRPs
│   ├── PRP-1-*.md         # Init & L4 validation
│   ├── PRP-1.2-*.md       # YAML validation
│   ├── PRP-2-*.md         # State management
│   ├── PRP-3-*.md         # Generate command
│   ├── PRP-4-*.md         # Execute command
│   └── PRP-5-*.md         # Context sync
├── feature-requests/       # Future PRPs
│   ├── PRP-6-*.md         # Markdown linting
│   ├── PRP-7-*.md         # Validation loop tests
│   ├── PRP-8-*.md         # PRP sizing analysis
│   └── PRP-9-*.md         # Serena MCP file ops
└── templates/              # PRP templates
    ├── prp-base-template.md
    ├── kiss.md
    └── self-healing.md
```

## Key Design Patterns

### Minimal Dependencies
- Stdlib-only approach for core functionality
- No external runtime dependencies
- pytest for testing only (dev dependency)

### Single Responsibility
- Each module handles one aspect
- core.py: system operations
- validate.py: validation logic
- context.py: context management
- generate.py: PRP generation
- execute.py: PRP execution
- prp.py: state management

### CLI Architecture
- Subcommand-based interface
- JSON output support for scripting
- Clear error messages with troubleshooting guidance
- Workflow automation (auto-sync mode)

## Implementation Status (2025-10-13)

### Executed PRPs
- ✅ PRP-1: L4 pattern conformance validation
- ✅ PRP-1.2: YAML validation command
- ✅ PRP-2: PRP state management & cleanup
- ✅ PRP-3: PRP generation automation (all 6 phases)
- ✅ PRP-4: PRP execution orchestration (all 5 phases)
- ✅ PRP-5: Context sync integration (all 6 phases)

### Feature Requests
- ⏸️ PRP-6: Markdown linting
- ⏸️ PRP-7: Comprehensive validation loop tests (80% coverage)
- ⏸️ PRP-8: PRP sizing constraint analysis
- ⏸️ PRP-9: Serena MCP file operations integration