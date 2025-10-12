---
prp_id: PRP-6
feature_name: Markdown & Mermaid Linting with Self-Healing
status: in_progress
created: 2025-10-13
updated: 2025-10-13
complexity: low
estimated_hours: 1-2
dependencies: markdownlint-cli2
---

# Markdown & Mermaid Linting with Self-Healing

## 1. TL;DR

**Objective**: Add markdown & mermaid linting to Level 1 validation with auto-fix capability

**What**:
- Implement markdownlint-cli2 for markdown files
- Implement custom mermaid validator for diagram syntax
- Auto-fix unquoted special chars, missing colors, broken rendering

**Why**: Ensure consistent markdown/mermaid formatting across documentation with automated fixes for common issues (nested code blocks, unquoted special chars, missing style colors)

**Effort**: Low (1-2 hours estimated)

**Dependencies**: markdownlint-cli2 (markdown), custom Python validator (mermaid)

## 2. Context

### Background

User reported broken markdown rendering in docs/research/12-git-commit-message.md due to nested code blocks. Need automated linting to catch these issues before they break rendering in IDEs and documentation sites.

### Constraints and Considerations

**Requirements:**
- Lint all markdown files in docs/, PRPs/, examples/
- Auto-fix common issues (trailing spaces, missing blank lines, etc.)
- Integrate with Level 1 validation (`npm run lint:md`)
- Self-healing: auto-fix on validation failure
- Configuration file (.markdownlint.json) with project-specific rules

**Edge Cases:**
- Nested code blocks within code blocks (should be caught)
- Mermaid diagrams with code syntax (should be allowed)
- YAML frontmatter in PRPs (should be allowed)
- Tables with variable column widths (should be flexible)

### Documentation References

- markdownlint-cli2: https://github.com/DavidAnson/markdownlint-cli2
- markdownlint rules: https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md

## 3. Implementation Steps

### Phase 1: Setup (15 min)

1. Install markdownlint-cli2
   ```bash
   cd tools
   uv add --dev markdownlint-cli2
   ```

2. Create configuration file

### Phase 2: Configuration (30 min)

1. Create `.markdownlint.json` with rules:
   - MD013 (line length): disabled (allow long lines in code examples)
   - MD033 (inline HTML): allowed (for badges, special formatting)
   - MD041 (first line heading): required
   - MD046 (code block style): fenced
   - MD047 (trailing newline): required

2. Create npm script in package.json (if exists) or add to validation

### Phase 3: Mermaid Validator (30 min)

1. Create tools/ce/mermaid_validator.py (DONE)
   - Validate node text for unquoted special chars
   - Check style statements have color specified
   - Auto-fix by renaming nodes or adding quotes/colors

2. Integration with validation.py (DONE)

### Phase 4: Testing (15 min)

1. Test with existing docs
2. Fix any detected issues
3. Verify auto-fixes work correctly

## 4. Validation Gates

### Gate 1: Markdown Lint Runs

**Command**: `npm run lint:md` or `markdownlint-cli2 "**/*.md"`

**Success Criteria**:
- Command executes without errors
- Returns valid exit code
- Identifies known issues in test files

### Gate 2: Auto-Fix Works

**Command**: `npm run lint:md:fix` or `markdownlint-cli2 --fix "**/*.md"`

**Success Criteria**:
- Common issues auto-fixed (trailing spaces, blank lines)
- Files updated correctly
- No corruption of code blocks or tables

### Gate 3: Integration with L1 Validation

**Command**: `uv run ce validate --level 1`

**Success Criteria**:
- Markdown linting runs as part of Level 1
- Errors reported clearly
- Duration tracked correctly

## 5. Testing Strategy

### Test Framework

Manual testing + validation gates

### Test Command

```bash
# Run markdown lint
cd tools
uv run ce validate --level 1

# Test auto-fix
markdownlint-cli2 --fix "**/*.md"
```

### Coverage Requirements

- Test on docs/research/*.md
- Test on PRPs/*.md
- Test on examples/patterns/*.md
- Test nested code block detection
- Test YAML frontmatter handling

## 6. Rollout Plan

### Phase 1: Development

1. Install markdownlint-cli2
2. Create configuration
3. Integrate with validation
4. Test on existing docs

### Phase 2: Fix Existing Issues

1. Run lint on all markdown files
2. Auto-fix simple issues
3. Manual fix for complex issues (nested code blocks)
4. Validate all docs render correctly

### Phase 3: Documentation

1. Update tools/README.md with lint:md command
2. Add .markdownlint.json documentation
3. Update CLAUDE.md with markdown linting reference

---

## Configuration Template

### .markdownlint.json

```json
{
  "default": true,
  "MD013": false,
  "MD033": {
    "allowed_elements": ["img", "br", "sub", "sup"]
  },
  "MD041": true,
  "MD046": {
    "style": "fenced"
  },
  "MD047": true,
  "MD024": {
    "siblings_only": true
  }
}
```

### package.json scripts (optional)

```json
{
  "scripts": {
    "lint:md": "markdownlint-cli2 \"docs/**/*.md\" \"PRPs/**/*.md\" \"examples/**/*.md\"",
    "lint:md:fix": "markdownlint-cli2 --fix \"docs/**/*.md\" \"PRPs/**/*.md\" \"examples/**/*.md\""
  }
}
```

### Python implementation (fallback if no npm)

```python
# tools/ce/markdown_lint.py
import subprocess
from pathlib import Path
from typing import Dict, Any

def lint_markdown(auto_fix: bool = False) -> Dict[str, Any]:
    """Lint markdown files using markdownlint-cli2.

    Args:
        auto_fix: If True, attempt to auto-fix issues

    Returns:
        Dict with success, errors, fixed_count
    """
    patterns = [
        "docs/**/*.md",
        "PRPs/**/*.md",
        "examples/**/*.md"
    ]

    cmd = ["markdownlint-cli2"]
    if auto_fix:
        cmd.append("--fix")
    cmd.extend(patterns)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    return {
        "success": result.returncode == 0,
        "errors": result.stderr.strip().split("\n") if result.stderr else [],
        "fixed_count": result.stdout.count("Fixed:") if auto_fix else 0
    }
```

---

**Research Findings**:
- markdownlint-cli2 is the actively maintained version (v0.x is deprecated)
- Supports glob patterns for efficient file matching
- Has built-in auto-fix for most rules
- Configuration via .markdownlint.json or .markdownlintrc
- Python fallback available if npm unavailable

**Implementation Status**: Phase 1 complete (validation.py updated), Phase 2-3 pending
