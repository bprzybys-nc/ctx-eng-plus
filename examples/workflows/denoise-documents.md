# Denoise Documents Workflow

Complete guide for compressing verbose documentation using AI-powered denoising to reduce token count while preserving critical information.

## Purpose

Document denoising enables:

- **Token reduction**: Compress verbose docs by 30-60% without information loss
- **Context optimization**: Fit more docs in LLM context window
- **Readability improvement**: Remove redundancy, improve clarity
- **Batch processing**: Denoise multiple documents simultaneously
- **Validation**: Ensure no critical information lost

**When to Use**:

- Verbose documentation (>1000 lines)
- Repetitive content (similar sections across docs)
- Before major refactoring (reduce context drift)
- Token budget exceeded (need to fit more context)
- Documentation cleanup (improve clarity)

**When NOT to Use**:

- Concise documentation (<300 lines, already optimized)
- Code files (use refactoring tools, not denoise)
- Configuration files (may break functionality)
- External docs (not under your control)

## Prerequisites

- Documentation files to denoise (.md, .txt, .rst)
- Context Engineering tools installed (`cd tools && uv sync`)
- Backup of original files (denoising is destructive)
- Understanding of compression targets (30%, 50%, etc.)

## Compression Targets

### Target 30% (Conservative)

**Use when**: Minimal risk tolerance, critical documentation

**Result**: Removes obvious redundancy, keeps all details

**Example**:

```markdown
Before (1000 tokens):
"The validation system provides multiple levels of validation including syntax validation, unit test validation, integration test validation, and pattern conformance validation. Each level builds upon the previous level and provides increasingly rigorous checking of the code quality."

After (700 tokens):
"The validation system has 4 levels: L1 (syntax), L2 (unit tests), L3 (integration), L4 (pattern conformance). Each level builds on the previous."
```

**Compression**: 30% reduction (1000 → 700 tokens)

### Target 50% (Moderate)

**Use when**: Standard documentation, some redundancy acceptable

**Result**: Removes redundancy, condenses examples, keeps core information

**Example**:

```markdown
Before (1000 tokens):
"The validation system provides multiple levels..."
[Same as above + detailed examples of each level]

After (500 tokens):
"Validation: L1 (syntax), L2 (tests), L3 (integration), L4 (patterns). Each level validates increasingly complex aspects of code quality."
```

**Compression**: 50% reduction (1000 → 500 tokens)

### Target 70% (Aggressive)

**Use when**: Internal notes, draft documentation, high redundancy

**Result**: Keeps only essential information, aggressive condensing

**Example**:

```markdown
Before (1000 tokens):
[Full detailed explanation with examples and edge cases]

After (300 tokens):
"4-level validation system (syntax → tests → integration → patterns). Each level builds on previous."
```

**Compression**: 70% reduction (1000 → 300 tokens)

## Denoise Modes

### Mode 1: Single Document

Denoise one document with custom target:

```bash
# Default target (50%)
cd tools && uv run ce denoise docs/GUIDE.md

# Custom target (30%)
cd tools && uv run ce denoise docs/GUIDE.md --target 0.3

# Aggressive (70%)
cd tools && uv run ce denoise docs/GUIDE.md --target 0.7
```

**Output**:

```
🔇 Denoising: docs/GUIDE.md
============================================================

Original: 1245 lines, ~8500 tokens
Target: 50% reduction (4250 tokens)

Processing...
  Analyzing content structure...
  Identifying redundant sections...
  Preserving critical information...
  Condensing examples...
  Optimizing readability...

Result:
  New size: 650 lines, ~4100 tokens
  Reduction: 48% (close to 50% target)
  Information preservation: 95%

Validation:
  ✅ All headings preserved
  ✅ Code examples intact
  ✅ Links functional
  ⚠️  2 examples condensed (review recommended)

File updated: docs/GUIDE.md
Backup saved: docs/GUIDE.md.backup
============================================================
```

### Mode 2: Batch Processing

Denoise multiple documents:

```bash
# Denoise all markdown in directory
cd tools && uv run ce denoise docs/*.md --target 0.5

# Denoise specific pattern
cd tools && uv run ce denoise "docs/**/VERBOSE*.md" --target 0.6

# Parallel processing (faster)
cd tools && uv run ce denoise docs/*.md --parallel --target 0.5
```

**Output**:

```
🔇 Batch Denoising: 5 documents
============================================================

Processing in parallel:
  docs/GUIDE.md: 48% reduction (8500 → 4100 tokens) ✅
  docs/API.md: 52% reduction (5200 → 2500 tokens) ✅
  docs/TUTORIAL.md: 45% reduction (12000 → 6600 tokens) ✅
  docs/FAQ.md: 50% reduction (3000 → 1500 tokens) ✅
  docs/CONCEPTS.md: 51% reduction (7500 → 3700 tokens) ✅

Total:
  36,200 → 18,400 tokens (49% reduction)
  17,800 tokens saved
  ~$0.18 saved per context window @ $0.01/1k tokens

All files updated. Backups saved: *.backup
============================================================
```

### Mode 3: Dry-Run Preview

Preview denoising without modifying files:

```bash
# Preview denoising
cd tools && uv run ce denoise docs/GUIDE.md --dry-run

# Show diff
cd tools && uv run ce denoise docs/GUIDE.md --dry-run --diff
```

**Output**:

```
🔇 Denoise Preview (Dry-Run): docs/GUIDE.md
============================================================

Original: 1245 lines, ~8500 tokens
Target: 50% reduction (4250 tokens)

Projected changes:
  - Section 1: "Introduction" → 30% shorter (450 → 315 tokens)
  - Section 2: "Getting Started" → 55% shorter (1200 → 540 tokens)
  - Section 3: "Core Concepts" → 48% shorter (2500 → 1300 tokens)
  - Section 4: "Examples" → 60% shorter (3000 → 1200 tokens)
  - Section 5: "Troubleshooting" → 35% shorter (1350 → 875 tokens)

Information preservation analysis:
  ✅ All critical concepts retained
  ✅ Code examples preserved (syntax)
  ⚠️  3 redundant examples will be condensed
  ⚠️  1 verbose explanation will be simplified

Estimated result:
  650 lines, ~4230 tokens (50.2% reduction)

Actions:
  Dry-run complete. No files modified.
  To apply: uv run ce denoise docs/GUIDE.md
============================================================
```

## Validation

### Information Preservation Check

```bash
# Denoise with validation
cd tools && uv run ce denoise docs/GUIDE.md --validate

# Custom validation prompts
cd tools && uv run ce denoise docs/GUIDE.md --validate-against validation-criteria.md
```

**Validation Criteria**:

```markdown
# Validation Criteria

## Critical Information

- [ ] All API endpoints documented
- [ ] Authentication flow explained
- [ ] Error codes listed
- [ ] Configuration options specified

## Code Examples

- [ ] All code examples present
- [ ] Syntax correct
- [ ] Output samples included

## Links

- [ ] Internal links functional
- [ ] External links valid
- [ ] References complete
```

**Output**:

```
✅ Validation: Information Preservation
============================================================

Critical Information:
  ✅ All API endpoints documented (10/10)
  ✅ Authentication flow explained
  ✅ Error codes listed (23/23)
  ✅ Configuration options specified (15/15)

Code Examples:
  ✅ All code examples present (8/8)
  ✅ Syntax correct
  ⚠️  Output samples condensed (2 simplified)

Links:
  ✅ Internal links functional (45/45)
  ✅ External links valid (12/12)
  ✅ References complete

Overall: 95% information preservation
Recommendation: Safe to use denoised version
============================================================
```

## Pre-Commit Hook Integration

### Automatic Denoising

Add denoise to pre-commit hook:

```yaml
# .claude/hooks/pre-commit
#!/bin/bash

# Denoise large markdown files before commit
for file in $(git diff --cached --name-only | grep '\.md$'); do
  size=$(wc -l < "$file")
  if [ "$size" -gt 1000 ]; then
    echo "🔇 Denoising large file: $file ($size lines)"
    cd tools && uv run ce denoise "../$file" --target 0.5
    git add "$file"
  fi
done
```

**Workflow**:

1. Edit large markdown file (1500 lines)
2. Commit: `git add docs/GUIDE.md && git commit -m "Update guide"`
3. Pre-commit hook auto-denoises to ~750 lines
4. Commit proceeds with denoised version

## Common Patterns

### Pattern 1: Iterative Denoising

Denoise in stages to find optimal compression:

```bash
# Stage 1: Conservative (30%)
cd tools && uv run ce denoise docs/GUIDE.md --target 0.3
# Review: Still too verbose

# Stage 2: Moderate (50%)
cd tools && uv run ce denoise docs/GUIDE.md --target 0.5
# Review: Good balance

# Stage 3: Validate
cd tools && uv run ce denoise docs/GUIDE.md --validate
```

### Pattern 2: Selective Denoising

Denoise only verbose sections:

```bash
# Identify verbose sections
wc -l docs/*.md | sort -n

# Denoise only large files (>1000 lines)
for file in docs/*.md; do
  lines=$(wc -l < "$file")
  if [ "$lines" -gt 1000 ]; then
    cd tools && uv run ce denoise "$file" --target 0.5
  fi
done
```

### Pattern 3: Denoise + Vacuum Combo

Combine denoising with vacuum for maximum cleanup:

```bash
# Step 1: Denoise verbose docs
cd tools && uv run ce denoise docs/*.md --target 0.5

# Step 2: Vacuum obsolete content
cd tools && uv run ce vacuum --auto

# Step 3: Validate
cd tools && uv run ce validate --level 4

# Result: Clean, optimized documentation
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Denoising Code Files

**Bad**:

```bash
# DON'T denoise source code
cd tools && uv run ce denoise tools/ce/validate.py
```

**Good**:

```bash
# DO denoise documentation only
cd tools && uv run ce denoise docs/validation-guide.md
```

**Why**: Denoising code files breaks functionality. Use refactoring tools instead.

### ❌ Anti-Pattern 2: Over-Aggressive Compression

**Bad**:

```bash
# DON'T use 90% compression on important docs
cd tools && uv run ce denoise docs/API-SPEC.md --target 0.9
```

**Good**:

```bash
# DO use conservative compression on critical docs
cd tools && uv run ce denoise docs/API-SPEC.md --target 0.3
```

**Why**: Over-compression loses critical information.

### ❌ Anti-Pattern 3: No Backup

**Bad**:

```bash
# DON'T denoise without backup
rm docs/GUIDE.md.backup
cd tools && uv run ce denoise docs/GUIDE.md
```

**Good**:

```bash
# DO keep backups or use git
git add docs/GUIDE.md
git commit -m "Before denoise"
cd tools && uv run ce denoise docs/GUIDE.md
```

**Why**: Denoising is destructive, backups enable rollback.

## Related Examples

- [vacuum-cleanup.md](vacuum-cleanup.md) - Complementary cleanup tool
- [context-drift-remediation.md](context-drift-remediation.md) - Reduce drift via denoising
- [batch-prp-generation.md](batch-prp-generation.md) - Denoise plan documents for clarity
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - Tool selection for documentation tasks

## Troubleshooting

### Issue: Information loss detected

**Symptom**: Validation reports <90% information preservation

**Solution**:

```bash
# Use more conservative target
cd tools && uv run ce denoise docs/GUIDE.md --target 0.3

# Or restore from backup
cp docs/GUIDE.md.backup docs/GUIDE.md

# Review and manually edit instead
```

### Issue: Denoise produces unreadable output

**Symptom**: Denoised version has grammar errors or unclear phrasing

**Solution**:

```bash
# Restore from backup
cp docs/GUIDE.md.backup docs/GUIDE.md

# Use lower compression target
cd tools && uv run ce denoise docs/GUIDE.md --target 0.3 --preserve-readability

# Review and manually edit
```

### Issue: "File too large to denoise"

**Symptom**: Denoise fails with "File exceeds token limit"

**Solution**:

```bash
# Split file into sections
split -l 500 docs/LARGE-GUIDE.md docs/GUIDE-part-

# Denoise each section
for file in docs/GUIDE-part-*; do
  cd tools && uv run ce denoise "$file" --target 0.5
done

# Recombine
cat docs/GUIDE-part-* > docs/GUIDE.md
```

## Performance Tips

1. **Batch size**: Process 5-10 files per batch (not 100+)
2. **Parallel mode**: Use `--parallel` for multi-file denoising
3. **Target tuning**: Start at 30%, increase cautiously
4. **Validation**: Always validate critical docs after denoising
5. **Backup strategy**: Keep .backup files or use git

## Resources

- CE CLI Command: `cd tools && uv run ce denoise --help`
- Validation Criteria: `docs/denoise-validation.md`
- Pre-Commit Hook: `.claude/hooks/pre-commit`
- Backup Location: `<original-file>.backup`
