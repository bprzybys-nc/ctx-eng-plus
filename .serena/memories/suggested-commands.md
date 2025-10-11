# Suggested Commands

## Package Management (UV - MANDATORY)
```bash
# Add dependencies
uv add package-name              # Production dependency
uv add --dev package-name        # Development dependency

# Install dependencies
uv sync                          # Install all dependencies

# Run commands in virtual environment
uv run <command>                 # Run any command with venv activated

# FORBIDDEN: Never edit pyproject.toml directly!
```

## Testing
```bash
# Navigate to tools directory first
cd tools

# Run all tests
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_core.py -v

# Run specific test
uv run pytest tests/test_core.py::test_run_cmd_success -v

# Quick test run (fail fast)
uv run pytest tests/ -x --tb=short -q
```

## CE Tool Usage
```bash
cd tools

# Validation
uv run ce validate --level all    # Run all validation gates
uv run ce validate --level 1      # Run level 1 validation
uv run ce validate --level 2      # Run level 2 validation
uv run ce validate --level 3      # Run level 3 validation

# Git operations
uv run ce git status               # Git repository status
uv run ce git diff                 # Show git diff
uv run ce git checkpoint "msg"     # Create git checkpoint (tag)

# Context management
uv run ce context sync             # Sync context with codebase
uv run ce context health           # Check context health
uv run ce context prune            # Prune stale context

# JSON output (for scripting)
uv run ce git status --json | jq '.clean'
uv run ce context health --json | jq '.drift_score'
```

## Development Setup
```bash
# First time setup
cd tools
./bootstrap.sh                    # Run bootstrap script

# Install in editable mode
uv pip install -e .               # If needed for development
```

## Darwin (macOS) System Commands
```bash
# File operations
ls -la                            # List files with details
find . -name "*.py"               # Find Python files
grep -r "pattern" .               # Recursive search

# Git operations
git status                        # Repository status
git diff                          # Show changes
git log --oneline -n 10           # Recent commits

# Process management
ps aux | grep python              # Find Python processes
```

## Troubleshooting
```bash
# Tool not found
cd tools && uv pip install -e .

# Tests failing
cd tools && uv sync               # Reinstall dependencies
uv run pytest tests/ -v           # Run tests

# Permission errors
chmod +x bootstrap.sh             # Make executable
```