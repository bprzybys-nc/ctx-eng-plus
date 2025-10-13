# Context Engineering CLI Tools

Minimal, efficient tooling for Context Engineering framework operations.

## Features

✅ **PRP Generation**: Automated PRP creation from INITIAL.md
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

### PRP Generation

**Generate PRP from INITIAL.md**
```bash
ce prp generate <initial-md-path> [-o OUTPUT_DIR] [--json]

# Example
ce prp generate ../feature-requests/user-auth/INITIAL.md
# Output: ../PRPs/feature-requests/PRP-6-user-authentication-system.md

# Custom output directory
ce prp generate feature.md -o /tmp/prps

# JSON output for scripting
ce prp generate feature.md --json
```

**What it does**:
1. Parses INITIAL.md (FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS)
2. Researches codebase using Serena MCP (pattern search, symbol analysis)
3. Fetches documentation using Context7 MCP (library docs, external links)
4. Generates complete 6-section PRP with YAML header
5. Auto-assigns next PRP ID (PRP-N+1)
6. Validates completeness (all required sections present)

**INITIAL.md structure** (see `.claude/commands/generate-prp.md` for details):
```markdown
# Feature: <Feature Name>

## FEATURE
<What to build - user story, acceptance criteria>

## EXAMPLES
<Code examples, file references>

## DOCUMENTATION
<Library docs, external resources>

## OTHER CONSIDERATIONS
<Security, constraints, edge cases>
```

**Graceful degradation**: Works without MCP servers (reduced functionality)

See also: `/generate-prp` slash command

---

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

---

### Markdown & Mermaid Linting

**Markdown Linting** (integrated in Level 1 validation)
```bash
# Lint markdown files
npm run lint:md

# Auto-fix markdown issues
npm run lint:md:fix
```

**What it does**:
- Validates markdown syntax using markdownlint-cli2
- Checks for common issues: trailing spaces, missing blank lines, inconsistent headings
- Auto-fixes formatting issues automatically
- Integrated into Level 1 validation gate

**Configuration**: `.markdownlint.json` in project root
```json
{
  "default": true,
  "MD013": false,  // Line length disabled (allow long code examples)
  "MD033": {       // Inline HTML allowed for badges
    "allowed_elements": ["img", "br", "sub", "sup", "User"]
  },
  "MD046": {       // Fenced code blocks required
    "style": "fenced"
  }
}
```

**Mermaid Diagram Validation** (integrated in Level 1 validation)

The mermaid validator automatically checks and fixes diagram syntax issues:

**Features**:
- ✅ Validates node text for unquoted special characters
- ✅ Checks style statements have color specified (theme compatibility)
- ✅ Auto-fixes common issues (renaming nodes, adding colors)
- ✅ HTML tag support (`<br/>`, `<sub/>`, `<sup/>`)
- ✅ Smart detection of problematic characters only

**Safe Characters** (no quoting needed):
- Colons `:` - "Level 0: CLAUDE.md" ✅
- Question marks `?` - "Why? Because!" ✅
- Exclamation marks `!` - "Important!" ✅
- Slashes `/` `\` - "path/to/file" ✅
- HTML tags - "Line 1<br/>Line 2" ✅

**Problematic Characters** (require quoting or node renaming):
- Brackets `[]` `{}` - used for node shape syntax
- Parentheses `()` - used for node shape syntax
- Pipes `|` - used for subgraph syntax
- Unbalanced quotes `"` `'` - break parsing

**Example Issues Detected**:
```mermaid
graph TD
    N1[Text with (parentheses)]    # ❌ Will be flagged
    style B fill:#ff0000,color:#fff           # ❌ Missing color specification
```

**Auto-Fixed Output**:
```mermaid
graph TD
    N1[Text with parentheses renamed]
    style B fill:#ff0000,color:#fff  # ✅ Color added
```

**Standalone Usage** (if needed):
```bash
# Validate all markdown/mermaid in docs/
cd tools
python ce/mermaid_validator.py ../docs

# Auto-fix issues
python ce/mermaid_validator.py --fix ../docs
```

**Results**:
- Files checked: 14
- Diagrams checked: 73
- Issues auto-fixed: varies based on file state

**Style Color Determination**:

The validator automatically determines appropriate text color based on background luminance:
- Light backgrounds (luminance > 0.5) → black text `#000`
- Dark backgrounds (luminance ≤ 0.5) → white text `#fff`

Uses W3C WCAG 2.0 relative luminance formula for accurate color contrast.

---

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

### Drift History Tracking

**View Drift History**
```bash
ce drift history [--last N] [--prp-id ID] [--action-filter TYPE] [--json]
# Shows drift decisions from all PRPs sorted by timestamp

# Examples:
ce drift history --last 5
ce drift history --prp-id PRP-001
ce drift history --action-filter accepted
```

**Show Drift Decision**
```bash
ce drift show <prp-id> [--json]
# Detailed view of drift decision for specific PRP

# Example:
ce drift show PRP-001
```

**Drift Summary**
```bash
ce drift summary [--json]
# Aggregate statistics across all drift decisions
# Shows: total PRPs, average score, distribution, category breakdown
```

**Compare Drift Decisions**
```bash
ce drift compare <prp-id-1> <prp-id-2> [--json]
# Compare drift decisions between two PRPs
# Shows: score difference, common/divergent categories

# Example:
ce drift compare PRP-001 PRP-002
```

**What it tracks**:
- Drift score (0-100%)
- Action taken (accepted, rejected, examples_updated)
- Justification for decisions
- Category breakdown (code_structure, error_handling, etc.)
- Reviewer (human, auto_accept, auto_fix)
- Historical patterns and trends

**Integration**: Drift history is displayed during Level 4 validation escalation to provide context for high-drift decisions.

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
├── context.py        # Context management
├── generate.py       # PRP generation from INITIAL.md
└── prp.py            # PRP state management
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
