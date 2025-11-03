---
prp_id: 32
feature_name: Examples Completion & Index Creation with Syntropy Integration
status: pending
created: 2025-11-03T00:00:00Z
complexity: medium
estimated_hours: 2.75-4.0
dependencies: none
---

# Examples Completion & Index Creation with Syntropy Integration

## 1. TL;DR

**Objective**: Complete Context Engineering examples directory with comprehensive Syntropy MCP integration examples and create structured index.md for easy discovery

**What**:

- Add missing examples for Syntropy MCP usage patterns
- Complete workflow examples (batch PRP generation, vacuum, denoise)
- Create comprehensive index.md with searchable table
- Organize examples by type, complexity, and category

**Why**:

- Current examples are incomplete and scattered
- No unified index for discovery
- Syntropy MCP integration patterns not documented
- New users need clear examples to learn framework

**Effort**: 2.75-4.0 hours

**Dependencies**: None

---

## 2. Context

### Background

- **Current State**: 13 example files, mix of patterns and docs, no index
- **Examples Directory**: `examples/` with `patterns/` subdirectory
- **Syntropy Integration**: Multiple Syntropy-related files scattered across project
- **README.md**: Generic, doesn't list actual examples or provide structure

### Gaps Identified

**Missing Examples:**

1. Syntropy MCP tool usage patterns (serena, context7, thinking)
2. Batch PRP generation workflow
3. Batch PRP execution workflow
4. Vacuum command usage
5. Denoise command usage
6. Tool permission management
7. Context drift remediation
8. Linear integration patterns

**Missing Documentation:**

- No comprehensive index of all examples
- No categorization by type/complexity
- No Syntropy integration indicators
- No quick reference for common tasks

### Requirements

**Index.md Structure:**

- Table format with columns: Name, Type, Category, Complexity, Syntropy, Description
- Organized by category (Patterns, Workflows, Configuration, Testing, Tools)
- Links to each example file
- Quick reference section for common tasks
- Search-friendly descriptions

**Example Coverage:**

- Core framework patterns (git, validation, testing)
- Syntropy MCP integration (serena, context7, thinking, linear)
- Workflow automation (batch gen/exe, vacuum, denoise)
- Configuration examples (settings, hooks, commands)
- Tool usage patterns (native vs MCP, permissions)

---

## 3. Implementation Steps

### Phase 1: Create Missing Syntropy Examples (60-75 min)

**Step 1**: Create `examples/syntropy/README.md` overview

- Purpose of Syntropy MCP integration
- List of available Syntropy servers (serena, filesystem, git, context7, thinking, linear)
- Tool naming convention (mcp__syntropy__{server}__{function})
- When to use Syntropy tools vs native tools

**Step 2**: Create `examples/syntropy/serena-symbol-search.md`

- Example: Finding symbol definitions with `serena_find_symbol`
- Example: Getting file symbols overview with `serena_get_symbols_overview`
- Example: Searching patterns with `serena_search_for_pattern`
- Example: Finding references with `serena_find_referencing_symbols`
- Common patterns and anti-patterns

**Step 3**: Create `examples/syntropy/context7-docs-fetch.md`

- Example: Resolving library IDs with `context7_resolve_library_id`
- Example: Fetching library docs with `context7_get_library_docs`
- Example: Focusing docs on specific topics
- Token optimization strategies

**Step 4**: Create `examples/syntropy/thinking-sequential.md`

- Example: Using `sequentialthinking` for complex reasoning
- Example: Branching thoughts for alternative approaches
- Example: Revising thoughts based on new information
- When to use vs inline reasoning

**Step 5**: Create `examples/syntropy/linear-integration.md`

- Example: Creating issues with `linear_create_issue`
- Example: Updating issue status with `linear_update_issue`
- Example: Querying issues with `linear_list_issues`
- Configuration via `.ce/linear-defaults.yml`
- Linking PRPs to Linear issues

**Step 6**: Create `examples/syntropy/memory-management.md`

- Example: Writing memories with `serena_write_memory`
- Example: Reading memories with `serena_read_memory`
- Example: Listing memories with `serena_list_memories`
- Memory types (architecture, pattern, note)
- Best practices for memory organization

**Content Template for All Examples:**

Each example file should follow this structure (150-300 lines):

1. **Purpose** (1-2 paragraphs)
   - What this example demonstrates
   - When to use this approach

2. **Prerequisites** (optional)
   - Required setup or configuration
   - Links to related documentation

3. **Examples** (3-4 code blocks)
   - Example 1: Basic usage
   - Example 2: Common pattern
   - Example 3: Edge case handling
   - Each with: input → output → explanation

4. **Common Patterns** (3-5 bullet points)
   - Recommended approaches
   - Best practices

5. **Anti-Patterns** (2-3 bullet points)
   - What NOT to do
   - Why it's problematic

6. **Related Examples** (links)
   - 2-3 related example files
   - Links to relevant documentation

### Phase 2: Create Workflow Examples (45-60 min)

**Step 7**: Create `examples/workflows/batch-prp-generation.md`

- Example plan document structure
- Dependency graph building
- Stage assignment algorithm
- Parallel subagent spawning
- Health monitoring via heartbeat files
- Error handling and retry strategies
- Complete workflow from plan → PRPs

**Step 8**: Create `examples/workflows/batch-prp-execution.md`

- Git worktree creation pattern
- Parallel execution within stages
- Health monitoring via git commits
- Sequential merge with conflict resolution
- Worktree cleanup
- Complete workflow from PRPs → merged code

**Step 9**: Create `examples/workflows/vacuum-cleanup.md`

- Dry-run mode for reporting
- Execute mode for high-confidence items
- Auto mode for medium+high confidence
- Nuclear mode with confirmation
- Custom confidence thresholds
- Excluding specific strategies
- Reading vacuum reports

**Step 10**: Create `examples/workflows/denoise-documents.md`

- Single document denoising
- Batch document processing
- Custom compression targets
- Dry-run preview
- Validation of information preservation
- Integration with pre-commit hooks

**Step 11**: Create `examples/workflows/context-drift-remediation.md`

- Running analyze-context for fast checks
- Using update-context for full sync
- Interpreting drift scores
- Remediation strategies for high drift
- PRP generation from drift reports
- Best practices for maintaining context health

### Phase 3: Create Configuration Examples (15-20 min)

**Step 12**: Create `examples/config/slash-command-template.md`

- Slash command markdown structure
- Required sections (Usage, What It Does, Examples)
- Optional sections (Configuration, Troubleshooting)
- Location: `.claude/commands/`
- Naming conventions

**Step 13**: Create `examples/config/hook-configuration.md`

- Pre-commit hooks
- Session start hooks
- User prompt submit hooks
- Hook return codes and blocking
- Examples from actual project hooks

### Phase 4: Create Comprehensive Index (45-75 min)

**Step 14**: Create `examples/INDEX.md` with structured table

**Table Structure:**

| Name | Type | Category | Complexity | Syntropy | Description | Path |
|------|------|----------|------------|----------|-------------|------|
| ... | ... | ... | ... | ... | ... | ... |

**Columns:**

- **Name**: Display name of example
- **Type**: Pattern, Workflow, Configuration, Testing, Tool, Model
- **Category**: Git, Validation, MCP, Batch, Cleanup, etc.
- **Complexity**: Low, Medium, High
- **Syntropy**: Yes (with server names) / No
- **Description**: 1-2 sentence summary
- **Path**: Relative path from project root

**Categories to Include:**

1. **Patterns** (Git operations, error recovery, testing strategies)
2. **Workflows** (Batch PRP, vacuum, denoise, context sync)
3. **Syntropy MCP** (Serena, Context7, Thinking, Linear)
4. **Configuration** (Commands, hooks, settings)
5. **Tool Usage** (Native vs MCP, permissions)
6. **Models** (SystemModel.md)

**INDEX.md Table Population Process:**

For EACH file in examples/ (excluding INDEX.md, README.md):

1. Open file and extract metadata:
   - **Name**: H1 heading text
   - **Type**: Infer from directory (syntropy/→Pattern, workflows/→Workflow, config/→Configuration, patterns/→Pattern, model/→Model)
   - **Category**: Primary focus (MCP, Batch, Git, Validation, Cleanup, etc.)
   - **Complexity**: Low (<150 LOC), Medium (150-300 LOC), High (>300 LOC)
   - **Syntropy**: Search file for "mcp__syntropy__" → Yes/No + server names
   - **Description**: First paragraph after Purpose or first section
   - **Path**: Relative path from examples/ (e.g., `syntropy/serena-symbol-search.md`)

2. Add row to table in alphabetical order within category

3. Cross-reference: Verify file count matches table row count
   - Count files: `find examples -name "*.md" ! -name "INDEX.md" ! -name "README.md" | wc -l`
   - Count table rows: `grep -c "^| [^-]" examples/INDEX.md` (excluding header/separator)

**Step 15**: Add Quick Reference section to INDEX.md

**Quick Reference Sections:**

- "How do I...?" common questions
- Quick links to most-used examples
- Workflow decision tree (when to use what)
- Syntropy tool selection guide

**Step 16**: Update `examples/README.md` to reference INDEX.md

- Add prominent link to INDEX.md
- Update structure description
- Add "Getting Started" section pointing to key examples

---

## 4. Validation Gates

### Level 1: File Structure (5 min)

```bash
# Verify all new files created
ls -la examples/syntropy/
ls -la examples/workflows/
ls -la examples/config/
test -f examples/INDEX.md

# Verify markdown syntax
cd tools && uv run ce validate --level 1
```

### Level 2: Content Completeness (10 min)

```bash
# Check all examples have required sections
for file in examples/syntropy/*.md; do
  grep -q "## Purpose" "$file" || echo "Missing Purpose: $file"
  grep -q "## Example" "$file" || echo "Missing Example: $file"
done

# Verify INDEX.md table has all files
diff <(find examples -name "*.md" -not -name "INDEX.md" | wc -l) \
     <(grep -c "^|" examples/INDEX.md)
```

### Level 3: Link Validation (5 min)

```bash
# Verify all paths in INDEX.md are valid
grep -E "\| examples/" examples/INDEX.md | \
  cut -d'|' -f7 | \
  while read path; do
    test -f "$path" || echo "Broken link: $path"
  done

# Check internal links in examples
grep -r "\[.*\](examples/" examples/ | \
  cut -d'(' -f2 | cut -d')' -f1 | \
  while read path; do
    test -f "$path" || echo "Broken internal link: $path"
  done
```

### Level 4: Integration Check (5 min)

```bash
# Verify examples referenced in CLAUDE.md exist
grep -o "examples/[^)]*\.md" CLAUDE.md | \
  while read path; do
    test -f "$path" || echo "Example referenced in CLAUDE.md missing: $path"
  done

# Check SystemModel.md references
grep -o "examples/[^)]*\.md" examples/model/SystemModel.md | \
  while read path; do
    test -f "$path" || echo "Example referenced in SystemModel.md missing: $path"
  done
```

---

## 5. Implementation Checklist

**Phase 1: Syntropy Examples**

- [ ] `examples/syntropy/README.md` - Overview and tool listing
- [ ] `examples/syntropy/serena-symbol-search.md` - Symbol navigation patterns
- [ ] `examples/syntropy/context7-docs-fetch.md` - Documentation fetching
- [ ] `examples/syntropy/thinking-sequential.md` - Complex reasoning patterns
- [ ] `examples/syntropy/linear-integration.md` - Issue tracking integration
- [ ] `examples/syntropy/memory-management.md` - Serena memory usage

**Phase 2: Workflow Examples**

- [ ] `examples/workflows/batch-prp-generation.md` - Parallel PRP generation
- [ ] `examples/workflows/batch-prp-execution.md` - Parallel PRP execution
- [ ] `examples/workflows/vacuum-cleanup.md` - Project cleanup patterns
- [ ] `examples/workflows/denoise-documents.md` - Document compression
- [ ] `examples/workflows/context-drift-remediation.md` - Context maintenance

**Phase 3: Configuration Examples**

- [ ] `examples/config/slash-command-template.md` - Command creation guide
- [ ] `examples/config/hook-configuration.md` - Hook setup patterns

**Phase 4: Index & Documentation**

- [ ] `examples/INDEX.md` - Comprehensive table with all examples
- [ ] INDEX.md Quick Reference section
- [ ] Updated `examples/README.md` with INDEX.md link
- [ ] All validation gates pass

---

## 6. Expected Output

### File Count

- **Before**: 13 example files
- **After**: 26+ example files (13 new + 13 existing)

### Directory Structure

```
examples/
├── INDEX.md                          # NEW - Comprehensive index
├── README.md                         # UPDATED - Link to INDEX.md
├── syntropy/                         # NEW - Syntropy MCP examples
│   ├── README.md
│   ├── serena-symbol-search.md
│   ├── context7-docs-fetch.md
│   ├── thinking-sequential.md
│   ├── linear-integration.md
│   └── memory-management.md
├── workflows/                        # NEW - Workflow examples
│   ├── batch-prp-generation.md
│   ├── batch-prp-execution.md
│   ├── vacuum-cleanup.md
│   ├── denoise-documents.md
│   └── context-drift-remediation.md
├── config/                           # NEW - Configuration examples
│   ├── slash-command-template.md
│   └── hook-configuration.md
├── patterns/                         # EXISTING - Keep as-is
│   └── ...
├── model/                            # EXISTING - Keep as-is
│   └── SystemModel.md
└── [other existing files]            # EXISTING - Keep as-is
```

### INDEX.md Preview

```markdown
# Context Engineering Examples Index

Comprehensive catalog of all Context Engineering framework examples, organized by type and category for easy discovery.

## Quick Reference

**I want to...**
- Learn Syntropy MCP tools → [Syntropy Examples](#syntropy-mcp)
- Run batch PRPs → [Batch Workflows](#workflows-batch)
- Clean up my project → [Vacuum Guide](workflows/vacuum-cleanup.md)
- Fix context drift → [Drift Remediation](workflows/context-drift-remediation.md)

## All Examples

| Name | Type | Category | Complexity | Syntropy | Description | Path |
|------|------|----------|------------|----------|-------------|------|
| Serena Symbol Search | Pattern | MCP | Medium | Yes (Serena) | Find symbols, references, and patterns using Serena MCP | [examples/syntropy/serena-symbol-search.md](syntropy/serena-symbol-search.md) |
| ... | ... | ... | ... | ... | ... | ... |

## Categories

### Syntropy MCP
[6 examples covering Serena, Context7, Thinking, Linear, Memory]

### Workflows
[5 examples covering batch operations, cleanup, context management]

### Patterns
[7 examples covering git, testing, error handling]

### Configuration
[2 examples covering commands and hooks]

### Models
[1 example: SystemModel.md]
```

---

## 7. Success Criteria

✅ **Completeness**: All 13 new example files created with comprehensive content
✅ **Organization**: Clear directory structure (syntropy/, workflows/, config/)
✅ **Index**: INDEX.md covers all 26+ examples with accurate metadata
✅ **Discoverability**: Quick Reference section enables fast lookups
✅ **Quality**: All examples follow consistent format (Purpose, Examples, Anti-patterns)
✅ **Validation**: All 4 validation gates pass
✅ **Integration**: Examples referenced in CLAUDE.md and SystemModel.md are accurate

---

## 8. Notes

**Syntropy Integration Priority**: Focus on most-used Syntropy tools first:

1. Serena (symbol search, memory management)
2. Linear (issue creation, status updates)
3. Context7 (documentation fetching)
4. Thinking (complex reasoning)

**Example Format Consistency**: All examples should include:

- **Purpose**: What this example demonstrates
- **When to Use**: Scenarios where this pattern applies
- **Examples**: 2-3 code/command examples
- **Anti-patterns**: What NOT to do
- **Related**: Links to related examples

**INDEX.md Maintenance**: After this PRP, update INDEX.md whenever new examples are added. Consider adding a validation gate in pre-commit hook to ensure INDEX.md stays in sync.

**Future Enhancements**:

- Add tags/labels for advanced filtering
- Create example search CLI command
- Generate INDEX.md automatically from example metadata
- Add "complexity score" based on LOC and dependencies
