---
type: regular
category: documentation
tags: [checklist, workflow, quality]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Task Completion Checklist

## When a Task is Completed

### 1. Code Quality Checks
- ✅ No fishy fallbacks or silent failures
- ✅ All mocks marked with FIXME in production code
- ✅ Functions under 50 lines, files under 500 lines
- ✅ Business-focused naming (no version references)
- ✅ Proper docstrings with type hints
- ✅ Exception handling with troubleshooting guidance

### 2. Testing
```bash
cd tools
uv run pytest tests/ -v           # Run all tests
```
- ✅ All tests pass
- ✅ Tests use real functionality (no fake results)
- ✅ New functionality has corresponding tests
- ✅ No regressions introduced

### 3. Documentation
- ✅ Update README.md if user-facing changes
- ✅ Update CLAUDE.md if workflow changes
- ✅ Docstrings updated for modified functions
- ✅ Comments added for complex logic

### 4. Git Operations (if committing)
```bash
cd tools
uv run ce git status              # Check status
git add <files>                   # Stage changes
git commit -m "message"           # Commit with clear message
```

### 5. Validation Gates (if applicable)
```bash
cd tools
uv run ce validate --level all    # Run all validation gates
```

### 6. Quick Smoke Test
```bash
cd tools
uv run ce --help                  # Verify CLI works
uv run ce validate --level 1      # Quick validation
```

## Adding New Function Workflow
1. Write function with docstring
2. Add exception handling with troubleshooting guidance
3. Write test that calls REAL function (no mocks)
4. Run tests: `uv run pytest tests/ -v`
5. Update README if user-facing

## Fixing Bug Workflow
1. Write test that reproduces bug (should fail)
2. Fix the bug
3. Run tests (should pass now)
4. Verify no regressions: `uv run pytest tests/ -v`

## Package Management Reminder
```bash
# ✅ REQUIRED
uv add package-name              # Add production dependency
uv add --dev package-name        # Add development dependency
uv sync                          # Install dependencies

# ❌ FORBIDDEN
# Manual pyproject.toml editing
```

## Pre-Commit Checklist
- [ ] Tests pass (`uv run pytest tests/ -v`)
- [ ] No fishy fallbacks introduced
- [ ] Exception handling includes troubleshooting
- [ ] Documentation updated if needed
- [ ] No version-specific naming
- [ ] UV package management used (not manual edits)