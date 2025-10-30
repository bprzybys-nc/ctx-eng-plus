# /denoise - Boil Out Document Noise

Boil out noise from documents—remove verbosity while strictly guaranteeing complete retention of all essential information.

## Usage

```bash
# Denoise single document
/denoise path/to/document.md

# Denoise with custom compression target (default: 60-75% reduction)
/denoise path/to/document.md --target 70

# Preview changes without writing (dry-run)
/denoise path/to/document.md --dry-run

# Denoise multiple documents
/denoise docs/*.md

# Denoise and show statistics
/denoise path/to/document.md --verbose
```

## What It Does

**Removes**:
- Verbose explanations (keeps essential meaning)
- Redundant examples (keeps one representative)
- Long code blocks (keeps signature + key logic)
- Repetitive sections
- Wordy transitions
- Multiple ways of saying same thing

**Preserves**:
- All essential information
- Technical accuracy
- Commands and references
- Critical warnings and errors
- Quick reference data
- Structure and organization

**Guaranteed**: Zero information loss, only noise removal

## Algorithm

### Phase 1: Structural Analysis
- Parse markdown sections
- Identify redundant patterns
- Detect verbose vs concise sections
- Map cross-references

### Phase 2: Content Classification
- **Keep**: Commands, references, warnings, key facts
- **Compress**: Long explanations → bullet points
- **Deduplicate**: Multiple examples → single best
- **Condense**: Multi-paragraph → 2-3 lines

### Phase 3: Optimization
- Convert verbose text to scannable format
- Preserve all unique information
- Maintain readability
- Keep structure intact

### Phase 4: Validation
- Verify no information loss
- Check all references intact
- Ensure commands preserved
- Validate structure

## Output

```
📄 Denoising: CLAUDE.md

Before: 1040 lines
After:  259 lines
Reduction: 75% (781 lines)

✅ Preserved:
  - All 5 core principles
  - 48 allowed tools summary
  - 15 quick commands
  - 12 troubleshooting entries
  - All resource paths

❌ Removed:
  - 6 verbose sections (150+ lines)
  - 12 redundant code examples
  - 8 long explanations
  - 4 duplicate references

Validation: PASS ✅
All essential information preserved.

Written to: CLAUDE.md
```

## Examples

### Before (Verbose)
```markdown
## Working Directory

**Default Context:** Project root (`/Users/bprzybysz/nc-src/ctx-eng-plus`)

**For tools/ commands:** Always prefix with `cd tools &&` or use full paths from root.

**Note:** Claude Code doesn't have a persistent working directory setting per project.
Always specify context explicitly:

```bash
# Correct patterns
cd tools && uv run ce --help
cd tools && uv run pytest tests/ -v
uv run -C tools ce validate --level all  # Using uv -C flag

# Avoid (relative paths from wrong location)
uv run ce --help  # Will fail if not in tools/
```
```

### After (Denoised)
```markdown
## Working Directory

**Default**: `/Users/bprzybysz/nc-src/ctx-eng-plus`

**For tools/ commands**: Use `cd tools &&` or `uv run -C tools`
```

## Configuration

**Location**: `.ce/denoise-config.yml` (optional)

```yaml
denoise:
  # Target compression ratio (default: 60-75%)
  target_reduction: 70

  # Preserve these sections verbatim
  preserve_sections:
    - "Quick Commands"
    - "Troubleshooting"

  # Maximum examples to keep per section
  max_examples: 1

  # Condense code blocks longer than N lines
  condense_code_threshold: 20
```

## Rules

### MUST Preserve
- Commands and CLI references
- Configuration examples
- Error messages and troubleshooting
- Technical specifications
- Quick reference tables
- Resource paths

### MAY Compress
- Long explanations (→ bullet points)
- Multiple examples (→ best one)
- Verbose prose (→ concise)
- Repetitive sections (→ single instance)

### MUST NOT Change
- Technical accuracy
- Command syntax
- File paths
- URLs and references
- Code logic (only formatting/length)

## When to Use

**Good for**:
- Documentation that grew organically
- Multiple authors with varying styles
- Copy-paste accumulation
- Tutorial-style docs needing quick reference format
- Token-heavy files

**Not for**:
- Tutorial content (intentional verbosity)
- Step-by-step guides with explanations
- API documentation with full examples
- Already concise documents

## Implementation

This command uses:
1. **LLM-based analysis** (via Syntropy thinking tool)
   - Semantic understanding of content
   - Intelligent redundancy detection
   - Context-aware compression

2. **Rule-based optimization**
   - Markdown structure preservation
   - Code block condensing
   - Bullet point conversion

3. **Validation layer**
   - Information extraction (before/after)
   - Completeness check
   - Cross-reference validation

## Integration

**Pre-commit hook** (optional):
```yaml
# .claude/settings.local.json
{
  "hooks": {
    "preCommit": {
      "command": "/denoise docs/*.md --dry-run --verbose",
      "description": "Check for document bloat before commit"
    }
  }
}
```

**Weekly maintenance**:
```bash
# Add to crontab or CI/CD
/denoise CLAUDE.md syntropy-mcp/CLAUDE.md --verbose
```

## Related

- `/peer-review` - Review document quality
- `/update-context` - Sync context with codebase
- `ce validate --level 1` - Markdown linting
