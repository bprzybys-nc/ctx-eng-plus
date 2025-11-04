---
prp_id: PRP-32.2.1
batch_id: 32
stage: 2
order: 1
feature_name: Documentation Refinement & Consolidation
status: pending
created: 2025-11-04T17:10:00Z
updated: 2025-11-04T17:10:00Z
complexity: medium
estimated_hours: 4-5
dependencies: Soft dependency on PRP-32.1.1 (classification report helps prioritize)
issue: TBD
---

# Documentation Refinement & Consolidation

**Phase**: 2 of 5 - Documentation Refinement & Consolidation
**Batch**: 32 (Syntropy MCP 1.1 Release Finalization)
**Stage**: 2 (Overlapping - starts k-groups analysis during Stage 1, merges Phase 1 results when available)

## 1. TL;DR

**Objective**: Consolidate similar documentation into k-groups, denoise without losing essential information

**What**: Analyze documentation files to identify clusters of similar content, create k-groups mapping (5-7 logical groups), execute systematic consolidation per group, reduce token count by 20-25% (from 280k to 210k tokens)

**Why**: Reduce documentation token overhead for Syntropy MCP 1.1 release while preserving all essential information and improving organization

**Effort**: 4-5 hours (analysis + consolidation + validation)

**Dependencies**: Soft dependency on PRP-32.1.1 (classification report helps prioritize consolidations), can start independently

## 2. Context

### Background

The Context Engineering framework documentation has grown organically to ~280k tokens across multiple directories. Phase 2 (this PRP) systematically consolidates similar content to reduce token overhead while preserving all unique information.

**Key Principles**:
- **No information loss** - All unique patterns and examples preserved
- **Logical grouping** - Similar topics consolidated into k-groups (knowledge groups)
- **Cross-reference integrity** - All internal links updated and validated
- **Conservative approach** - When uncertain, create report rather than delete

### Current State

**Documentation Locations**:
- `examples/` - 15 .md files (~280k tokens total estimate)
- `.serena/memories/` - 23 .md files (may have duplicates)
- `.claude/commands/` - 10 .md files (slash command definitions)

**Identified Clusters** (preliminary analysis):
1. Syntropy MCP guides (context7, linear, serena, thinking, troubleshooting)
2. Workflow documentation (batch generation, execution, cleanup, drift detection)
3. Configuration guides (command permissions, hooks, settings)
4. Patterns and practices (testing, code standards, validation, error handling)
5. Project management (PRP sizing, structure, Linear integration, batch execution)
6. Migration & initialization (setup, onboarding, troubleshooting)
7. Reference materials (tool usage, API docs, CLI reference, keyboard shortcuts, glossary, quick reference)

**Target Consolidation**:
- Group 1: 6 files → 3 files (33% reduction)
- Group 2: 5 files → 3 files (26% reduction)
- Group 3: 2 files → 2 files (no change, distinct topics)
- Group 4: 4 files → 2 files (31% reduction)
- Group 5: 4 files → 3 files (29% reduction)
- Group 6: 5 files (NEW from Phase 3, not counted in reduction)
- Group 7: 6 files → 4 files (29% reduction)

**Overall Target**: 20-25% token reduction (280k → 210k tokens)

### Constraints and Considerations

**Critical Constraints**:
1. **DO NOT modify INDEX.md** - Only create consolidation report. Phase 5 (PRP-32.5.1) will apply unified INDEX update
2. **Preserve all unique patterns** - No information loss allowed
3. **Update cross-references** - All internal links must work after consolidation
4. **Soft dependency on Phase 1** - Can start k-groups analysis independently, merge classification report when available
5. **Stage 2 execution** - Overlaps with Stage 1, results feed into Stage 3

**Workflow Integration**:
1. Start k-groups analysis immediately (independent of Phase 1)
2. When PRP-32.1.1 completes, read `docs/doc-classification-report.md`
3. Merge Phase 1 classification findings into k-groups mapping
4. Execute consolidations per k-group
5. Verify no information loss (before/after diffs)
6. Count tokens before/after
7. Create consolidation report with before/after comparison

**Token Counting Strategy**:
```bash
# Rough estimate: 1 token ≈ 4 characters
wc -c examples/*.md | awk '{print $1/4 " tokens", $2}'

# Accurate count using tiktoken (if needed)
python -c "import tiktoken; enc = tiktoken.get_encoding('cl100k_base'); print(len(enc.encode(open('file.md').read())))"
```

**Error Handling**:
- If Phase 1 classification not ready: Proceed with independent k-groups analysis, merge later
- If duplicate detection uncertain: Create report with recommendations, don't delete (conservative)
- If cross-reference breaks: Add to consolidation report as follow-up item for Phase 5
- If token reduction < 20%: Document why, don't force unnecessary consolidations

**Validation Requirements**:
- Diff before/after for each consolidated file
- Grep for broken cross-references: `grep -r '\[.*\](.*/.*\.md)' examples/`
- Manual review of consolidated content vs original (spot check 20% of consolidations)
- Token count verification: before/after for each k-group
- Test all cross-references in consolidated docs

**Rollback Plan**:
- Git commit before consolidation (`git commit -m "Pre-consolidation snapshot"`)
- Git commit after consolidation (`git commit -m "Phase 2: Documentation consolidation"`)
- Easy revert if issues found in Stage 3 testing: `git revert HEAD`

### Documentation References

**Related PRPs**:
- PRP-32.1.1: Documentation index & classification audit (provides classification report)
- PRP-26: Context drift analyzer (similar analysis pattern)
- PRP-28: Previous documentation consolidation effort

**Related Examples**:
- examples/INDEX.md - Read for structure planning (don't modify)
- .claude/commands/batch-gen-prp.md - Example of unified multi-section doc
- .ce/RULES.md - Framework rules (consolidation principles)

**External Resources**:
- [Reduce Prompt Complexity](https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-prompt-complexity) - Token optimization strategies
- Information Architecture principles for knowledge organization

## 3. Implementation Steps

### Phase 1: K-Groups Analysis (1.5 hours)

**Goal**: Identify clusters and create k-groups mapping document

**Steps**:
1. **Scan all documentation files** (15 minutes)
   ```bash
   # Get all markdown files with sizes
   find /Users/bprzybyszi/nc-src/ctx-eng-plus/examples -name "*.md" -type f -exec wc -c {} +
   find /Users/bprzybyszi/nc-src/ctx-eng-plus/.serena/memories -name "*.md" -type f -exec wc -c {} +
   ```

2. **Analyze content similarity** (45 minutes)
   - Use Grep to identify common topics across files:
     ```bash
     # Find Syntropy MCP mentions
     grep -l "Syntropy\|Context7\|Linear\|Serena" examples/*.md

     # Find workflow mentions
     grep -l "batch\|PRP\|execution\|generation" examples/*.md

     # Find configuration mentions
     grep -l "command\|permission\|hook\|settings" examples/*.md
     ```
   - Read 3-5 files per cluster to understand content depth
   - Identify unique vs overlapping content

3. **Create k-groups mapping document** (30 minutes)
   - Create `docs/k-groups-mapping.md`
   - Define 5-7 logical groups with clear boundaries
   - List files in each group (before state)
   - Propose consolidated structure (after state)
   - Estimate token reduction per group
   - Include consolidation strategy per group

**Output**: `docs/k-groups-mapping.md` with complete consolidation plan

**Example k-groups structure**:
```markdown
# K-Groups Mapping

## Group 1: Syntropy MCP Integration
**Files (6)**: syntropy-mcp-guide.md, context7-guide.md, linear-guide.md, serena-guide.md, thinking-guide.md, mcp-troubleshooting.md
**Consolidated (3)**: syntropy-integration.md (core concepts), mcp-servers.md (server-specific guides), mcp-troubleshooting.md (keep separate)
**Token reduction**: 45k → 30k (33%)
**Strategy**: Merge common setup/auth into integration.md, keep server-specific details in mcp-servers.md

## Group 2: Workflow Automation
**Files (5)**: batch-prp-generation.md, cleanup-workflow.md, drift-detection.md, prp-execution.md, worktree-workflow.md
**Consolidated (3)**: prp-workflows.md (generation+execution), automation-tools.md (batch+drift), worktree-guide.md (keep separate)
**Token reduction**: 38k → 28k (26%)
**Strategy**: Combine generation+execution (sequential workflow), batch+drift (automation tools)

... [Groups 3-7] ...
```

### Phase 2: Phase 1 Integration (30 minutes)

**Goal**: Merge classification report findings when available

**Steps**:
1. **Check if Phase 1 completed**
   ```bash
   test -f /Users/bprzybyszi/nc-src/ctx-eng-plus/docs/doc-classification-report.md && echo "Phase 1 complete" || echo "Phase 1 pending"
   ```

2. **If Phase 1 complete**: Read classification report
   - Read `docs/doc-classification-report.md`
   - Extract IsWorkflow classifications (framework vs project-specific)
   - Identify duplicate files flagged in Phase 1
   - Note any consolidation recommendations from Phase 1

3. **Merge findings into k-groups mapping**
   - Update `docs/k-groups-mapping.md` with Phase 1 insights
   - Prioritize framework docs (IsWorkflow=Yes) for consolidation
   - Flag project-specific docs (IsWorkflow=No) - may exclude from consolidation
   - Add Phase 1 duplicate findings to consolidation plan

4. **If Phase 1 pending**: Continue with independent k-groups analysis
   - Mark in k-groups-mapping.md: "Phase 1 classification pending, will merge when available"
   - Proceed with consolidation based on content similarity analysis

**Output**: Updated `docs/k-groups-mapping.md` with Phase 1 insights (if available)

### Phase 3: Consolidation Execution (2 hours)

**Goal**: Execute consolidations per k-group, one group at a time

**Steps for each k-group**:

1. **Pre-consolidation snapshot** (5 minutes per group)
   ```bash
   # Count tokens before (rough estimate)
   wc -c examples/file1.md examples/file2.md examples/file3.md | tail -1 | awk '{print $1/4 " tokens"}'

   # Create git checkpoint
   git add examples/
   git commit -m "Pre-consolidation: Group N snapshot"
   ```

2. **Execute consolidation** (15-20 minutes per group)
   - Read all files in the k-group
   - Extract unique content from each file
   - Create consolidated file(s) with unified structure:
     - Clear sections per original file topic
     - Merge common setup/troubleshooting
     - Preserve all unique patterns and examples
   - Write consolidated file(s)
   - Example structure:
     ```markdown
     # Syntropy Integration

     ## Overview
     [Merged common intro from all 6 files]

     ## Setup & Authentication
     [Merged common setup from all files]

     ## Context7 Server
     [Unique Context7 content]

     ## Linear Server
     [Unique Linear content]

     ## Serena Server
     [Unique Serena content]

     ## Sequential Thinking Server
     [Unique thinking content]

     ## Troubleshooting
     [Merged common troubleshooting]
     ```

3. **Update cross-references** (10 minutes per group)
   - Grep for references to old files:
     ```bash
     grep -r "old-filename.md" examples/ .serena/memories/ .claude/commands/
     ```
   - Use Edit tool to update all cross-references to new consolidated files
   - Update any relative links

4. **Verify no information loss** (10 minutes per group)
   - Diff consolidated file(s) against original files (spot check 20%)
   - Manually verify key sections preserved
   - Check for any missing unique content

5. **Post-consolidation validation** (5 minutes per group)
   ```bash
   # Count tokens after
   wc -c examples/new-consolidated.md | awk '{print $1/4 " tokens"}'

   # Check for broken links
   grep -r '\[.*\](.*/.*\.md)' examples/ | grep "old-filename"

   # Commit changes
   git add examples/
   git commit -m "Consolidation: Group N completed"
   ```

**Repeat for all 7 k-groups**

**Output**: Consolidated files per k-group, git commits per group

### Phase 4: Final Validation (1 hour)

**Goal**: Verify overall consolidation success and document results

**Steps**:
1. **Token count comparison** (15 minutes)
   ```bash
   # Before: sum all original file sizes
   find /Users/bprzybyszi/nc-src/ctx-eng-plus/examples -name "*.md" -type f -exec wc -c {} + | tail -1 | awk '{print $1/4 " tokens before"}'

   # After: sum all consolidated file sizes (check git diff)
   git diff --stat HEAD~7 HEAD examples/ | grep "files changed"
   ```

2. **Cross-reference integrity check** (15 minutes)
   ```bash
   # Find all markdown links
   grep -r '\[.*\](.*/.*\.md)' examples/

   # Verify each link target exists
   # (manual spot check of 20% of links)
   ```

3. **Content completeness spot check** (20 minutes)
   - Sample 3-4 consolidated files
   - Compare against original files (git diff)
   - Verify no unique content lost
   - Check that examples and patterns preserved

4. **Create consolidation report** (10 minutes)
   - Create `docs/consolidation-report.md`
   - Document before/after comparison per k-group
   - List all consolidated files (old → new mappings)
   - Report token reduction achieved
   - List any issues or follow-up items
   - Include git commit hashes for rollback reference

**Output**: `docs/consolidation-report.md` with complete before/after analysis

**Example report structure**:
```markdown
# Consolidation Report - Phase 2

## Summary
- **Total files before**: 32 files
- **Total files after**: 24 files (8 files removed via consolidation)
- **Token reduction**: 280k → 215k tokens (23% reduction)
- **Git commits**: 7 group commits + 1 pre-consolidation snapshot

## K-Group Results

### Group 1: Syntropy MCP Integration
- **Before**: 6 files, 45k tokens
- **After**: 3 files, 30k tokens
- **Reduction**: 33%
- **Consolidations**:
  - syntropy-mcp-guide.md + context7-guide.md + 4 others → syntropy-integration.md (15k tokens)
  - Server-specific details → mcp-servers.md (12k tokens)
  - mcp-troubleshooting.md → kept as-is (3k tokens)

... [Groups 2-7] ...

## Issues & Follow-Up Items
- None (all cross-references validated)

## Rollback Reference
- Pre-consolidation commit: abc123f
- Group 1 commit: def456a
- Group 2 commit: ghi789b
... [Group 3-7 commits] ...
```

## 4. Validation Gates

### Gate 1: K-Groups Mapping Created

**Command**:
```bash
test -f /Users/bprzybyszi/nc-src/ctx-eng-plus/docs/k-groups-mapping.md && echo "PASS" || echo "FAIL"
```

**Success Criteria**:
- K-groups mapping document exists
- 5-7 logical groups defined with clear boundaries
- Each group lists files before/after consolidation
- Token reduction estimate per group documented
- Consolidation strategy per group specified

### Gate 2: Token Reduction Achieved

**Command**:
```bash
# Calculate token reduction (manual calculation from consolidation report)
grep "Token reduction" /Users/bprzybyszi/nc-src/ctx-eng-plus/docs/consolidation-report.md
```

**Success Criteria**:
- Token count reduced by 20-25% (target: 280k → 210k-224k)
- If < 20%: Document justification in consolidation report
- Per-group reductions documented and verified

### Gate 3: No Information Loss

**Command**:
```bash
# Spot check 20% of consolidations via git diff
git log --oneline --grep="Consolidation: Group" | head -7
git diff HEAD~7 HEAD examples/ | grep "^-" | wc -l  # Lines removed
git diff HEAD~7 HEAD examples/ | grep "^+" | wc -l  # Lines added
```

**Success Criteria**:
- All unique content preserved (manual verification of sampled files)
- Examples and patterns present in consolidated docs
- No loss of critical information (warnings, security notes, troubleshooting)

### Gate 4: Cross-Reference Integrity

**Command**:
```bash
# Check for broken links
grep -r '\[.*\](.*/.*\.md)' /Users/bprzybyszi/nc-src/ctx-eng-plus/examples/ | while read -r line; do
  file=$(echo "$line" | cut -d: -f1)
  link=$(echo "$line" | grep -oP '\(.*\.md\)' | tr -d '()')
  dir=$(dirname "$file")
  target="$dir/$link"
  test -f "$target" || echo "BROKEN: $line"
done
```

**Success Criteria**:
- Zero broken internal links
- All cross-references point to existing files
- Relative links work from consolidated file locations

### Gate 5: Consolidation Report Complete

**Command**:
```bash
test -f /Users/bprzybyszi/nc-src/ctx-eng-plus/docs/consolidation-report.md && echo "PASS" || echo "FAIL"
grep -q "Summary" /Users/bprzybyszi/nc-src/ctx-eng-plus/docs/consolidation-report.md && echo "PASS" || echo "FAIL"
```

**Success Criteria**:
- Consolidation report exists
- Contains summary section with before/after totals
- Documents all k-group results
- Lists git commit hashes for rollback
- Includes any issues or follow-up items

## 5. Testing Strategy

### Test Framework

Manual validation with bash commands (no unit tests needed for documentation work)

### Test Commands

```bash
# Full validation sequence
cd /Users/bprzybyszi/nc-src/ctx-eng-plus

# Gate 1: K-groups mapping
test -f docs/k-groups-mapping.md && echo "✓ Gate 1 PASS" || echo "✗ Gate 1 FAIL"

# Gate 2: Token reduction (manual from report)
grep "Token reduction" docs/consolidation-report.md

# Gate 3: Information loss check (spot check)
git diff HEAD~7 HEAD examples/ | less

# Gate 4: Cross-reference integrity
grep -r '\[.*\](.*/.*\.md)' examples/ | wc -l
echo "^ Check for broken links (manual verification)"

# Gate 5: Consolidation report
test -f docs/consolidation-report.md && echo "✓ Gate 5 PASS" || echo "✗ Gate 5 FAIL"
grep -q "Summary" docs/consolidation-report.md && echo "✓ Report complete" || echo "✗ Report incomplete"
```

### Coverage Requirements

- All 7 k-groups consolidated and validated
- 20% spot check of consolidated content vs original
- 100% cross-reference validation (all links checked)
- Before/after token counts documented per group

## 6. Rollout Plan

### Phase 1: Development (4-5 hours)

1. Execute implementation steps (Phases 1-4)
2. Create k-groups mapping
3. Consolidate per k-group with git commits
4. Validate all gates
5. Create consolidation report

### Phase 2: Review (30 minutes)

1. Self-review consolidation report
2. Verify no information loss (spot check 20%)
3. Test cross-references (automated + manual spot check)
4. Confirm token reduction target met (20-25%)

### Phase 3: Handoff to Stage 3 (15 minutes)

1. Commit all changes to git
2. Push branch (if working in worktree)
3. Update PRP status to completed
4. Notify Stage 3 PRPs that consolidation results available:
   - PRP-32.3.1: Migration guide creation (uses consolidated docs)
   - PRP-32.3.2: Obsolete content removal (uses k-groups analysis)
5. Document any issues or recommendations for Phase 4/5

### Rollback Plan

If issues found in Stage 3 testing:
```bash
# Revert all consolidation commits
git revert HEAD~7..HEAD

# Or reset to pre-consolidation snapshot
git reset --hard <pre-consolidation-commit-hash>
```

---

## Research Findings

### K-Groups Preliminary Analysis

**Cluster 1: Syntropy MCP Integration**
- Files identified: syntropy-mcp-guide.md, context7-guide.md, linear-guide.md, serena-guide.md, thinking-guide.md, mcp-troubleshooting.md
- Common topics: MCP setup, authentication, server configuration, tool usage
- Unique content: Server-specific API details, examples per tool
- Consolidation opportunity: High (common setup/auth can be merged)

**Cluster 2: Workflow Automation**
- Files identified: batch-prp-generation.md, cleanup-workflow.md, drift-detection.md, prp-execution.md, worktree-workflow.md
- Common topics: PRP lifecycle, automation commands, batch processing
- Unique content: Workflow-specific steps, command syntax
- Consolidation opportunity: Medium (generation+execution are sequential, batch+drift are related tools)

**Cluster 3: Configuration & Setup**
- Files identified: command-permissions.md, hooks-guide.md
- Common topics: Configuration, setup
- Unique content: Distinct configuration domains (permissions vs hooks)
- Consolidation opportunity: Low (topics are distinct, keep separate)

**Cluster 4: Code Quality & Testing**
- Files identified: testing-patterns.md, code-standards.md, validation-guide.md, error-handling.md
- Common topics: Code quality, best practices, validation
- Unique content: Testing vs standards vs error handling
- Consolidation opportunity: High (standards+errors can merge, testing+validation can merge)

**Cluster 5: Project Management**
- Files identified: prp-sizing.md, prp-structure.md, linear-integration.md, batch-execution.md
- Common topics: PRP management, project tracking
- Unique content: Sizing vs structure vs execution vs Linear integration
- Consolidation opportunity: Medium (sizing+structure are related, batch-execution is distinct)

**Cluster 6: Migration & Initialization**
- Files identified: (NEW from Phase 3, not yet created)
- Expected files: migration-guide.md, initialization-checklist.md, setup-troubleshooting.md, first-steps.md, onboarding.md
- Consolidation opportunity: Will be created consolidated in Phase 3

**Cluster 7: Reference & Standards**
- Files identified: tool-usage-guide.md, api-reference.md, cli-reference.md, keyboard-shortcuts.md, glossary.md, quick-reference.md
- Common topics: Reference material, lookups
- Unique content: Different reference types (tools vs API vs CLI vs glossary)
- Consolidation opportunity: High (tool+api can merge, cli+shortcuts can merge, glossary+quick-ref can merge)

### Token Reduction Estimates

| K-Group | Files Before | Files After | Tokens Before | Tokens After | Reduction % |
|---------|--------------|-------------|---------------|--------------|-------------|
| Group 1 | 6 | 3 | 45k | 30k | 33% |
| Group 2 | 5 | 3 | 38k | 28k | 26% |
| Group 3 | 2 | 2 | 18k | 18k | 0% |
| Group 4 | 4 | 2 | 32k | 22k | 31% |
| Group 5 | 4 | 3 | 28k | 20k | 29% |
| Group 6 | 5 | 5 | 35k (new) | 35k (new) | N/A |
| Group 7 | 6 | 4 | 42k | 30k | 29% |
| **Total** | **32** | **22** | **238k** | **183k** | **23%** |

**Note**: Group 6 is new content from Phase 3, not counted in reduction. Adjusted total without Group 6: 203k → 148k = 27% reduction (exceeds 20-25% target)

### Phase 1 Integration Notes

- If PRP-32.1.1 completes before consolidation execution, merge classification findings
- IsWorkflow=Yes files prioritized for consolidation (framework docs for distribution)
- IsWorkflow=No files may be excluded from consolidation (project-specific)
- Duplicate findings from Phase 1 added to k-groups mapping

### Cross-Reference Analysis

Common cross-reference patterns found:
- CLAUDE.md → examples/*.md (many references)
- examples/*.md → other examples/*.md (internal links)
- .serena/memories/*.md → examples/*.md (rare)
- .claude/commands/*.md → examples/*.md (moderate)

**Impact**: Must update CLAUDE.md references in Phase 5 (out of scope for Phase 2, report only)
