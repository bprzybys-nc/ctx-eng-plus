# Context Engineering CLI Tools

Minimal, efficient tooling for Context Engineering framework operations.

## Features

✅ **File Operations**: Read/write with security validation
✅ **Git Integration**: Status, diff, checkpoints
✅ **3-Level Validation**: Syntax, unit tests, integration tests
✅ **Context Management**: Sync and health checks
✅ **Zero Dependencies**: Pure stdlib implementation
✅ **JSON Output**: Scriptable for CI/CD pipelines

## Installation

### Quick Install
```bash
cd tools
./bootstrap.sh
```

### Manual Install
```bash
cd tools
uv venv
uv pip install -e .
```

## Commands Reference

### Validation Gates

**Level 1: Syntax & Style**
```bash
ce validate --level 1
# Runs: npm run lint && npm run type-check
```

**Level 2: Unit Tests**
```bash
ce validate --level 2
# Runs: npm test
```

**Level 3: Integration Tests**
```bash
ce validate --level 3
# Runs: npm run test:integration
```

**All Levels**
```bash
ce validate --level all
# Runs all validation levels sequentially
```

### Git Operations

**Check Status**
```bash
ce git status [--json]
# Shows: staged, unstaged, untracked files
```

**Create Checkpoint**
```bash
ce git checkpoint "Phase 1 complete"
# Creates annotated git tag: checkpoint-<timestamp>
```

**View Changes**
```bash
ce git diff [--since HEAD~5] [--json]
# Shows changed files since specified ref
```

### Context Management

**Sync Context**
```bash
ce context sync [--json]
# Detects git diff, reports files needing reindex
# Returns: reindexed_count, files, drift_score, drift_level
```

**Health Check**
```bash
ce context health [--json]
# Comprehensive health report:
# - Compilation status (Level 1)
# - Git cleanliness
# - Tests passing (Level 2)
# - Context drift score
# - Actionable recommendations
```

**Prune Memories** (placeholder)
```bash
ce context prune [--age 7] [--dry-run]
# Requires Serena MCP integration
```

## JSON Output

All commands support `--json` flag for programmatic use:

```bash
ce validate --level all --json > validation-report.json
ce git status --json | jq '.clean'
ce context health --json | jq '.drift_score'
```

## Exit Codes

- **0**: Success
- **1**: Failure

Use in scripts:
```bash
if ce validate --level 1; then
    echo "Validation passed"
else
    echo "Validation failed"
    exit 1
fi
```

## Architecture

```
ce/
├── __init__.py       # Package metadata
├── __main__.py       # CLI entry point
├── core.py           # File, git, shell operations
├── validate.py       # 3-level validation gates
└── context.py        # Context management
```

**Design Principles**:
- **KISS**: Single responsibility per function
- **SOLID**: Clear interfaces, dependency injection
- **DRY**: Shared utilities
- **No Fishy Fallbacks**: Exceptions thrown, not caught silently
- **Real Testing**: Actual functionality, no mocks

## Development

### Run Tests
```bash
uv run pytest tests/ -v

# With coverage
uv run pytest tests/ --cov=ce --cov-report=term-missing
```

### Add Dependencies
```bash
# Never edit pyproject.toml directly!
uv add package-name              # Production
uv add --dev package-name        # Development
```

### Test Locally
```bash
# Install in editable mode
uv pip install -e .

# Use anywhere
ce --help
```

## Integration with Context Engineering Framework

This CLI complements the Context Engineering framework documented in `/docs/`:

- **Validation Gates**: Implements 3-level validation from `08-validation-testing.md`
- **Context Sync**: Implements drift detection from `04-self-healing-framework.md`
- **Git Operations**: Supports checkpoint pattern from `06-workflow-patterns.md`

## Troubleshooting

**Command not found: ce**
```bash
# Ensure you're in tools directory
cd tools

# Reinstall
uv pip install -e .

# Or use directly
uv run python -m ce --help
```

**Tests failing**
```bash
# Install dev dependencies
uv sync

# Run specific test
uv run pytest tests/test_core.py::test_run_cmd_success -v
```

**npm commands not available**
```bash
# Some tests/commands require npm scripts
# Ensure package.json has required scripts:
npm run lint
npm run type-check
npm test
```

## License

Part of the Context Engineering Framework.

## Version

Current: 0.1.0
