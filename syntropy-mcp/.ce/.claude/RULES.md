# Context Engineering Framework Rules

Distilled framework rules for Context Engineering projects.

## Core Principles

### No Fishy Fallbacks - MANDATORY
- Fast Failure: Let specific exceptions bubble up
- Explicit Logic: All business logic must be explicit
- Actionable Errors: Error messages must include 🔧 troubleshooting guidance
- No Silent Corruption: Validation failures must be visible

### KISS (Keep It Simple, Stupid)
- Simple solutions first
- Clear code over clever code
- Minimal dependencies
- Single responsibility per function
- Direct implementation
- Fast failure

### Code Quality Standards
- Functions: TARGET 50 lines (single responsibility)
- Files: TARGET 500 lines (logical modules)
- Classes: TARGET 100 lines (single concept)
- No unmarked mocks/placeholders in production code (use FIXME comments)

### Testing Standards
- TDD: Write test first, watch it fail, implement, refactor
- Real functionality testing: No fake results, no hardcoded success
- Exception handling: All errors must include troubleshooting guidance

### Package Management (Python Projects)
- UV only: NEVER edit pyproject.toml directly
- Use `uv add` for dependencies
- Use `uv sync` to install

## PRP Methodology

### PRP Structure
- YAML header with metadata
- Feature overview with context
- Implementation blueprint with phases
- Validation gates at each phase
- Acceptance criteria (must/nice/out-of-scope)
- Testing strategy
- Dependencies and risks

### PRP Lifecycle
1. Generate: `/generate-prp <feature>` creates comprehensive PRP
2. Review: `/peer-review` validates document quality
3. Execute: `/execute-prp` implements changes
4. Review: `/peer-review exe` validates execution
5. Sync: `/update-context` updates project knowledge

### Context Sync
- Run after completing PRP implementation
- Updates YAML headers with sync flags
- Detects pattern drift
- Generates drift report at `.ce/drift-report.md`

## Directory Structure

### System Content (.ce/)
- PRPs/system/: Framework PRPs (PRP-1 through PRP-N)
- examples/system/: Model and code patterns
- tools/: CE CLI utilities
- .serena/: Project memories
- RULES.md: This file
- config.yml: Framework configuration

### User Content (root)
- PRPs/feature-requests/: New PRPs (before execution)
- PRPs/executed/: Completed PRPs (after execution)
- examples/: Project-specific examples
- CLAUDE.md: Project-specific guide

## Slash Commands

- `/generate-prp <feature>`: Generate comprehensive PRP from INITIAL.md
- `/execute-prp <prp-file>`: Execute PRP implementation
- `/update-context`: Sync context with codebase
- `/peer-review [prp] [exe]`: Review PRP document or execution

## Best Practices

### Error Handling
```python
# Good
def process():
    if error_condition:
        raise ValueError(
            f"Processing failed: {reason}\n"
            f"🔧 Troubleshooting: Check input format"
        )
```

### Real Testing
```python
# Good - tests real function
def test_process():
    result = process(real_input)
    assert result.success is True

# Bad - fake result
def test_process():
    result = {"success": True}  # FAKE!
    assert result["success"]
```

### File Operations
- Prefer editing existing files over creating new ones
- Use UV for package management
- Never create unnecessary files

---

**Remember**: These rules ensure consistency, maintainability, and quality across all Context Engineering projects.
