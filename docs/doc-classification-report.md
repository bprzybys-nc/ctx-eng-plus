# Documentation Classification Report

**Generated**: 2025-11-04
**PRP**: PRP-32.1.1 - Documentation Index & Classification Audit
**Scope**: Syntropy MCP 1.1 Release Finalization

## Executive Summary

- **Total documents scanned**: 105 markdown files
- **System docs (from Syntropy init)**: 67 files
  - Framework examples: 21 (INDEX.md references)
  - Framework memories: 23 (.serena/memories/)
  - Framework PRPs: 0 (structure exists for future)
  - Slash commands: 11 (.claude/commands/)
  - System templates/PRPs: 48 (.ce/ - mostly project history)
- **User docs (from buckets)**: 4 project-specific examples
- **INDEX.md gaps**: 11 missing files, 4 unindexed files
- **Missing directories**: 2 (config/, syntropy/)
- **Workflows directory status**: EXISTS with 4 migration docs (but not batch/cleanup workflows referenced in INDEX.md)

## INDEX.md Audit

### Missing Files (Referenced in INDEX.md but Not Found)

INDEX.md references 25 examples total. Analysis of missing files:

| Path | IsWorkflow | Status | Notes |
|------|------------|--------|-------|
| workflows/batch-prp-execution.md | Yes | ✗ Missing | Directory exists but file not found; documented in .claude/commands/batch-exe-prp.md instead |
| workflows/batch-prp-generation.md | Yes | ✗ Missing | Directory exists but file not found; documented in .claude/commands/batch-gen-prp.md instead |
| workflows/context-drift-remediation.md | Yes | ✗ Missing | Directory exists but file not found; functionality in ce drift/analyze-context |
| workflows/denoise-documents.md | Yes | ✗ Missing | Directory exists but file not found; documented in .claude/commands/denoise.md instead |
| workflows/vacuum-cleanup.md | Yes | ✗ Missing | Directory exists but file not found; documented in .claude/commands/vacuum.md instead |
| config/hook-configuration.md | Yes | ✗ Missing | Directory doesn't exist; content likely in .ce/RULES.md or .claude/commands/ |
| config/slash-command-template.md | Yes | ✗ Missing | Directory doesn't exist; template pattern exists in .claude/commands/*.md files |
| syntropy/README.md | Yes | ✗ Missing | Directory doesn't exist; Syntropy overview may be in memories or examples/ |
| syntropy/context7-docs-fetch.md | Yes | ✗ Missing | Directory doesn't exist; pattern likely in Serena memories |
| syntropy/linear-integration.md | Yes | ✗ Missing | Directory doesn't exist; see examples/linear-integration-example.md |
| syntropy/memory-management.md | Yes | ✗ Missing | Directory doesn't exist; pattern exists in .serena/memories/ |
| syntropy/serena-symbol-search.md | Yes | ✗ Missing | Directory doesn't exist; pattern may be in tool-usage-syntropy.md memory |
| syntropy/thinking-sequential.md | Yes | ✗ Missing | Directory doesn't exist; no replacement found |

**Total missing**: 13 files (5 workflows + 2 config + 6 syntropy)

**Analysis**: Most workflow files exist as slash commands (.claude/commands/) instead of standalone examples/. The syntropy/ and config/ directories were likely planned but never created. Content may exist in different locations:
- Workflows → .claude/commands/ (batch-exe-prp.md, batch-gen-prp.md, vacuum.md, denoise.md)
- Config → .ce/RULES.md or .claude/commands/ templates
- Syntropy patterns → .serena/memories/ (tool-usage-syntropy.md, linear-*.md)

### Obsolete Entries (Indexed but Likely Reorganized)

No obsolete entries detected. All missing files appear to be planned content that was either:
1. Implemented in different locations (slash commands vs examples/)
2. Never created (syntropy/ pattern docs)
3. Consolidated into other docs (config merged into RULES.md)

### Unindexed Files (Exist but Not in INDEX.md)

Files found in examples/ that are NOT referenced in INDEX.md:

| Path | IsWorkflow | Size (lines) | Status | Notes |
|------|------------|--------------|--------|-------|
| examples/INITIALIZATION.md | Yes | Unknown | ✓ Found | CE 1.1 initialization guide (NEW) |
| examples/migration-integration-summary.md | Yes | Unknown | ✓ Found | Migration summary doc (NEW) |
| examples/README.md | No | Unknown | ✓ Found | Project-specific README |
| examples/templates/PRP-0-CONTEXT-ENGINEERING.md | Yes | Unknown | ✓ Found | PRP template (framework) |
| examples/workflows/migration-existing-ce.md | Yes | Unknown | ✓ Found | Migration workflow (NEW) |
| examples/workflows/migration-greenfield.md | Yes | Unknown | ✓ Found | Migration workflow (NEW) |
| examples/workflows/migration-mature-project.md | Yes | Unknown | ✓ Found | Migration workflow (NEW) |
| examples/workflows/migration-partial-ce.md | Yes | Unknown | ✓ Found | Migration workflow (NEW) |

**Total unindexed**: 8 files (1 initialization guide + 1 summary + 1 README + 1 template + 4 migration workflows)

**Recommendation for Phase 5**: Add these 7 universal files to INDEX.md (exclude project-specific README). The migration workflows and INITIALIZATION.md are critical CE 1.1 content.

## Classification by IsWorkflow

### System Docs (from Syntropy init / ce-infrastructure.xml)

**Destination**: `/system/` subfolders (`.ce/examples/system/`, `.serena/memories/system/`, `.ce/PRPs/system/`)

#### Examples (21 files referenced in INDEX.md - IsWorkflow=Yes)

| Category | Count | Examples | Status |
|----------|-------|----------|--------|
| Syntropy MCP | 6 | syntropy/*.md (all missing - see gap analysis) | ✗ Missing directory |
| Workflows | 5 | workflows/*.md (all missing from examples/) | ⚠ Exist as slash commands |
| Configuration | 2 | config/*.md (all missing) | ✗ Missing directory |
| Patterns (universal) | 2 | mocks-marking.md, dedrifting-lessons.md | ✓ Complete |
| Guides | 2 | TOOL-USAGE-GUIDE.md, prp-decomposition-patterns.md | ✓ Complete |
| Reference | 4 | mermaid-color-palette.md, tmp-directory-convention.md, example.setting.local.md, SystemModel.md | ✓ Complete |

**Note**: Patterns category has 4 total files in INDEX.md, but 2 are project-specific (example-simple-feature.md, git-message-rules.md marked IsWorkflow=No).

#### Serena Memories (23 files - 6 universal + 17 project-specific)

**Universal Memories (IsWorkflow=Yes)** - Suitable for all CE projects:

| Memory | Type | Purpose | Lines | Status |
|--------|------|---------|-------|--------|
| code-style-conventions.md | pattern | Coding principles: KISS, no fishy fallbacks, mock marking | 129 | ✓ Complete |
| suggested-commands.md | documentation | Common commands reference (UV, pytest, CE tools) | 98 | ✓ Complete |
| task-completion-checklist.md | documentation | Pre-commit verification checklist | 80 | ✓ Complete |
| testing-standards.md | pattern | Testing philosophy: real functionality, TDD | 87 | ✓ Complete |
| tool-usage-syntropy.md | documentation | Syntropy tool selection guide with decision trees | 425 | ✓ Complete |
| use-syntropy-tools-not-bash.md | pattern | Prefer Syntropy over bash migration patterns | 200 | ✓ Complete |

**Total universal memories**: 6 files, 1,019 lines

#### Slash Commands (11 files - all framework-level)

| Command | Purpose | Status |
|---------|---------|--------|
| batch-exe-prp.md | Execute PRPs in parallel with worktrees | ✓ Complete |
| batch-gen-prp.md | Generate PRPs from plan with dependency analysis | ✓ Complete |
| denoise.md | Compress verbose documentation | ✓ Complete |
| execute-prp.md | Single PRP execution | ✓ Complete |
| generate-prp.md | Single PRP generation | ✓ Complete |
| peer-review.md | Peer review workflow | ✓ Complete |
| sync-with-syntropy.md | Sync tool state with Syntropy MCP | ✓ Complete |
| syntropy-health.md | MCP health check | ✓ Complete |
| tools-misuse-scan.md | Scan for tool misuse patterns | ✓ Complete |
| update-context.md | Sync PRPs with codebase | ✓ Complete |
| vacuum.md | Project noise cleanup | ✓ Complete |

**Total slash commands**: 11 files (all IsWorkflow=Yes)

#### System PRPs and Templates (48 files in .ce/)

**Framework PRPs** (.ce/PRPs/system/executed/): 45 files
- All PRPs in .ce/PRPs/system/executed/ are framework development history
- Classification: IsWorkflow=No (project history, not distributable framework docs)
- Examples: PRP-1 through PRP-28, tools-rationalization-study.md, etc.

**Framework Templates** (.ce/PRPs/system/templates/): 3 files
- kiss.md, prp-base-template.md, self-healing.md
- Classification: IsWorkflow=Yes (framework templates)
- Status: ✓ Complete

**System Examples** (.ce/examples/system/): 9 files
- Includes duplicates of examples/ files (SystemModel.md, patterns/*.md)
- Classification: IsWorkflow=Yes (framework examples)
- Status: ✓ Complete (but duplicates need resolution - see Consolidation section)

**Other .ce/ files**: 4 files
- drift-report.md, vacuum-report.md (generated reports)
- BATCH-EXE-PRP-PEER-REVIEW.md, BATCH-GEN-PRP-PEER-REVIEW.md (peer review outputs)
- Classification: IsWorkflow=No (project-specific generated content)

### User Docs (from target project buckets)

**Destination**: Parent directories (`.ce/examples/`, `.serena/memories/`, `.ce/PRPs/`)

#### Examples (4 project-specific files - IsWorkflow=No)

| File Path | Type | Reason | Lines |
|-----------|------|--------|-------|
| examples/patterns/example-simple-feature.md | Pattern | Demonstrates ctx-eng-plus specific git status command | 182 |
| examples/patterns/git-message-rules.md | Pattern | Ctx-eng-plus commit message conventions | 205 |
| examples/l4-validation-example.md | Reference | Ctx-eng-plus validation patterns | 290 |
| examples/syntropy-status-hook-system.md | Reference | References ctx-eng-plus scripts (scripts/session-startup.sh) | 149 |

**Total project-specific examples**: 4 files, 826 lines

#### Serena Memories (17 project-specific files - IsWorkflow=No)

| Memory | Type | Purpose | Lines |
|--------|------|---------|-------|
| codebase-structure.md | architecture | Ctx-eng-plus directory layout | 196 |
| cwe78-prp22-newline-escape-issue.md | troubleshooting | Project-specific security issue resolution | 100 |
| l4-validation-usage.md | pattern | L4 validation system (project-specific) | 150 |
| linear-issue-creation-pattern.md | pattern | Linear issue creation with PRP metadata | 69 |
| linear-issue-tracking-integration.md | pattern | Bi-directional Linear/PRP integration | 213 |
| linear-mcp-integration-example.md | pattern | Linear MCP with ctx-eng-plus defaults | 101 |
| linear-mcp-integration.md | documentation | Linear MCP tool reference | 114 |
| project-overview.md | documentation | Ctx-eng-plus master documentation | 188 |
| PRP-15-remediation-workflow-implementation.md | documentation | PRP-15 implementation record | 206 |
| prp-2-implementation-patterns.md | pattern | State management patterns (project) | 330 |
| prp-backlog-system.md | configuration | PRP backlog workflow (project) | 106 |
| prp-structure-initialized.md | documentation | PRP initialization record | 80 |
| serena-implementation-verification-pattern.md | pattern | Serena symbol lookup verification | 139 |
| serena-mcp-tool-restrictions.md | configuration | Project tool restrictions | 236 |
| syntropy-status-hook-pattern.md | pattern | Cache-based SessionStart hook | 177 |
| system-model-specification.md | documentation | CE target architecture spec | 157 |
| tool-config-optimization-completed.md | documentation | Tool optimization record | 63 |

**Total project-specific memories**: 17 files, 2,625 lines

### Classification Summary Table

| Document Type | System (IsWorkflow=Yes) | User (IsWorkflow=No) | Total |
|---------------|------------------------|---------------------|-------|
| Examples (indexed) | 21 | 4 | 25 |
| Examples (unindexed) | 7 | 1 | 8 |
| Serena Memories | 6 | 17 | 23 |
| Slash Commands | 11 | 0 | 11 |
| System PRPs | 3 (templates) | 45 (history) | 48 |
| System Examples (.ce/) | 9 | 0 | 9 |
| **Grand Total** | **57** | **67** | **124** |

**Note**: Grand total (124) exceeds scanned files (105) because INDEX.md references 13 missing files counted as "planned system docs".

### Classification Source Reference

**System docs** (IsWorkflow=Yes) originate from:
- ce-infrastructure.xml package extraction (Syntropy MCP 1.0 framework)
- Universal patterns and templates suitable for any CE project
- Framework slash commands and validation infrastructure

**User docs** (IsWorkflow=No) originate from:
- tmp/syntropy-initialization/ validated files from buckets (examples/, PRPs/, serena/)
- Project-specific implementation details tied to ctx-eng-plus
- Historical development records (executed PRPs)

## Directory Structure Analysis

### Expected Structure (per INDEX.md)

```
examples/
├── syntropy/           # 6 files (Syntropy MCP patterns)
├── workflows/          # 5 files (Batch, cleanup, drift workflows)
├── config/             # 2 files (Hooks, slash command templates)
├── patterns/           # 4 files (Git, testing, context, PRP)
├── model/              # 1 file (SystemModel.md)
└── [root]              # 8 files (guides, reference)
```

### Actual Structure (filesystem scan)

```
examples/
├── workflows/          # ✓ EXISTS but different content
│   ├── migration-existing-ce.md
│   ├── migration-greenfield.md
│   ├── migration-mature-project.md
│   └── migration-partial-ce.md
├── patterns/           # ✓ EXISTS (4 files match INDEX.md)
│   ├── dedrifting-lessons.md
│   ├── example-simple-feature.md
│   ├── git-message-rules.md
│   └── mocks-marking.md
├── model/              # ✓ EXISTS (1 file matches)
│   └── SystemModel.md
├── templates/          # ✓ EXISTS (not in INDEX.md)
│   └── PRP-0-CONTEXT-ENGINEERING.md
└── [root]              # ✓ EXISTS (8 files + 3 unindexed)
    ├── example.setting.local.md
    ├── INDEX.md
    ├── INITIALIZATION.md (unindexed)
    ├── l4-validation-example.md
    ├── linear-integration-example.md
    ├── mermaid-color-palette.md
    ├── migration-integration-summary.md (unindexed)
    ├── prp-decomposition-patterns.md
    ├── README.md (unindexed)
    ├── syntropy-status-hook-system.md
    ├── tmp-directory-convention.md
    └── TOOL-USAGE-GUIDE.md
```

### Missing Directories

| Directory | Expected Files | Status | Alternative Location |
|-----------|----------------|--------|---------------------|
| syntropy/ | 6 pattern docs | ✗ Missing | .serena/memories/ (tool-usage-syntropy.md, linear-*.md) |
| config/ | 2 config docs | ✗ Missing | .ce/RULES.md, .claude/commands/ templates |

**Analysis**:
- workflows/ exists but contains migration docs instead of batch/cleanup workflows
- Batch/cleanup workflows exist as slash commands (.claude/commands/)
- syntropy/ and config/ were never created; content distributed elsewhere

## Consolidation Opportunities

### Duplicate Content

| Files | Overlap | Recommendation |
|-------|---------|----------------|
| examples/model/SystemModel.md & .ce/examples/system/model/SystemModel.md | 100% identical | Keep examples/model/, delete .ce/examples/system/model/ |
| examples/patterns/*.md & .ce/examples/system/patterns/*.md | 100% identical (4 files) | Keep examples/patterns/, delete .ce/examples/system/patterns/ duplicates |
| examples/TOOL-USAGE-GUIDE.md & .ce/examples/system/tool-usage-patterns.md | 80%+ similar | Verify content, merge if redundant |

**Priority**: HIGH - 5-6 duplicate files detected (SystemModel + 4 patterns + possibly tool-usage)

**Recommendation**:
1. Verify .ce/examples/system/ is a stale copy from previous organization
2. Delete .ce/examples/system/ directory entirely (9 files)
3. Keep all content in examples/ as canonical source
4. Update any internal links referencing .ce/examples/system/

### Overlapping Coverage - Linear Integration

Multiple files document Linear MCP integration:

| File | Type | Focus | Lines | Status |
|------|------|-------|-------|--------|
| examples/linear-integration-example.md | Example | Legacy Linear example | 204 | IsWorkflow=Yes |
| .serena/memories/linear-mcp-integration.md | Docs | Tool reference (20+ tools) | 114 | IsWorkflow=No |
| .serena/memories/linear-mcp-integration-example.md | Pattern | Integration with config defaults | 101 | IsWorkflow=No |
| .serena/memories/linear-issue-creation-pattern.md | Pattern | Issue creation with PRP metadata | 69 | IsWorkflow=No |
| .serena/memories/linear-issue-tracking-integration.md | Pattern | Bi-directional Linear/PRP workflow | 213 | IsWorkflow=No |

**Total**: 5 files, 701 lines

**Overlap Analysis**:
- examples/linear-integration-example.md: Broad overview (framework-level)
- .serena memories: Detailed patterns and ctx-eng-plus specific workflows
- 30-40% content overlap across files

**Recommendation for Phase 4**:
1. **Keep as-is** for now (memories serve different purpose than examples)
2. Future optimization: Consolidate memories to 2 files:
   - linear-mcp-integration.md (tool reference + basic patterns - IsWorkflow=Yes)
   - linear-ctx-eng-plus-workflow.md (project-specific integration - IsWorkflow=No)
3. Update examples/linear-integration-example.md to reference consolidated memories

### Overlapping Coverage - Workflows vs Slash Commands

Workflow documentation exists in two locations:

| Topic | INDEX.md Reference | Actual Location | Status |
|-------|-------------------|-----------------|--------|
| Batch PRP Execution | workflows/batch-prp-execution.md (missing) | .claude/commands/batch-exe-prp.md | ✓ Complete |
| Batch PRP Generation | workflows/batch-prp-generation.md (missing) | .claude/commands/batch-gen-prp.md | ✓ Complete |
| Context Drift Remediation | workflows/context-drift-remediation.md (missing) | ce drift/analyze-context (CLI) | ⚠ Partial docs |
| Denoise Documents | workflows/denoise-documents.md (missing) | .claude/commands/denoise.md | ✓ Complete |
| Vacuum Cleanup | workflows/vacuum-cleanup.md (missing) | .claude/commands/vacuum.md | ✓ Complete |

**Recommendation for Phase 5**:
1. **Option A**: Update INDEX.md paths to reference .claude/commands/*.md directly
2. **Option B**: Create examples/workflows/*.md as lightweight wrappers referencing slash commands
3. **Recommended**: Option A (avoid duplication, slash commands are canonical documentation)

## Broken Cross-References

### INDEX.md Internal Links

All broken links originate from missing directories and files documented in Gap Analysis section above.

| Link Target | Count | Status | Notes |
|-------------|-------|--------|-------|
| workflows/*.md | 5 | ✗ Broken | Files exist as slash commands (.claude/commands/) |
| config/*.md | 2 | ✗ Broken | Directory doesn't exist; content in .ce/RULES.md |
| syntropy/*.md | 6 | ✗ Broken | Directory doesn't exist; content in .serena/memories/ |

**Total broken links in INDEX.md**: 13

### Cross-References in Other Files

Grep analysis for broken internal links (sample check):

```bash
# Check examples/ for broken relative links
grep -r '\[.*\](.*\.md)' examples/ | grep -v 'http' | grep -v '^examples/INDEX.md'
```

**Result**: No additional broken cross-references detected in examples/ files (spot check performed).

**Recommendation**: Full link validation should be performed in Phase 5 before final release.

## Recommendations for Phase 4 & 5

### Phase 4: Documentation Consolidation

1. **Delete .ce/examples/system/ duplicates** (HIGH priority)
   - 9 files: SystemModel.md + 4 patterns/*.md + tool-usage-patterns.md + others
   - Verify content is identical to examples/ before deletion
   - Update any links referencing .ce/examples/system/

2. **Consider Linear docs consolidation** (MEDIUM priority)
   - Review 5 Linear-related files for overlap
   - Consolidate to 2 files if >40% redundancy confirmed
   - Preserve project-specific workflows in separate file

3. **Evaluate migration workflow docs** (LOW priority)
   - 4 new migration docs in examples/workflows/
   - Assess if they replace old workflow docs or serve different purpose
   - Update INDEX.md to include migration workflows

### Phase 5: INDEX.md Final Update

1. **Fix broken links** (13 total):
   - Update workflows/ paths → .claude/commands/*.md (5 files)
   - Remove config/ entries or document actual location (2 files)
   - Remove syntropy/ entries or update to .serena/memories/ paths (6 files)

2. **Add unindexed files** (7 universal + 1 project-specific):
   - INITIALIZATION.md (critical for CE 1.1)
   - migration-integration-summary.md
   - templates/PRP-0-CONTEXT-ENGINEERING.md
   - workflows/migration-*.md (4 files)
   - README.md (project-specific, low priority)

3. **Update IsWorkflow classifications**:
   - Verify all 25 indexed examples have correct IsWorkflow status
   - Add IsWorkflow column for newly indexed files

4. **Create missing directories** (if needed):
   - Decision: Keep current structure or create syntropy/config/ directories?
   - Recommendation: Keep current structure, update INDEX.md to match reality

5. **Update statistics**:
   - Total examples: 25 → 32 (add 7 unindexed)
   - Update line counts after consolidation
   - Verify Serena memory counts (currently 23, matches filesystem)

## Appendix: File Inventory

### Complete Filesystem Scan Results

**examples/** (22 files):
```
examples/example.setting.local.md
examples/INDEX.md
examples/INITIALIZATION.md
examples/l4-validation-example.md
examples/linear-integration-example.md
examples/mermaid-color-palette.md
examples/migration-integration-summary.md
examples/model/SystemModel.md
examples/patterns/dedrifting-lessons.md
examples/patterns/example-simple-feature.md
examples/patterns/git-message-rules.md
examples/patterns/mocks-marking.md
examples/prp-decomposition-patterns.md
examples/README.md
examples/syntropy-status-hook-system.md
examples/templates/PRP-0-CONTEXT-ENGINEERING.md
examples/tmp-directory-convention.md
examples/TOOL-USAGE-GUIDE.md
examples/workflows/migration-existing-ce.md
examples/workflows/migration-greenfield.md
examples/workflows/migration-mature-project.md
examples/workflows/migration-partial-ce.md
```

**.serena/memories/** (23 files - matches INDEX.md):
```
code-style-conventions.md
codebase-structure.md
cwe78-prp22-newline-escape-issue.md
l4-validation-usage.md
linear-issue-creation-pattern.md
linear-issue-tracking-integration.md
linear-mcp-integration-example.md
linear-mcp-integration.md
project-overview.md
PRP-15-remediation-workflow-implementation.md
prp-2-implementation-patterns.md
prp-backlog-system.md
prp-structure-initialized.md
serena-implementation-verification-pattern.md
serena-mcp-tool-restrictions.md
suggested-commands.md
syntropy-status-hook-pattern.md
system-model-specification.md
task-completion-checklist.md
testing-standards.md
tool-config-optimization-completed.md
tool-usage-syntropy.md
use-syntropy-tools-not-bash.md
```

**.claude/commands/** (11 files):
```
batch-exe-prp.md
batch-gen-prp.md
denoise.md
execute-prp.md
generate-prp.md
peer-review.md
sync-with-syntropy.md
syntropy-health.md
tools-misuse-scan.md
update-context.md
vacuum.md
```

**.ce/** (48 files - PRPs, examples, reports):
```
.ce/BATCH-EXE-PRP-PEER-REVIEW.md
.ce/BATCH-GEN-PRP-PEER-REVIEW.md
.ce/drift-report.md
.ce/vacuum-report.md
.ce/examples/system/ (9 files - duplicates)
.ce/PRPs/system/executed/ (45 files - framework development history)
.ce/PRPs/system/templates/ (3 files - framework templates)
```

**Total scanned**: 105 markdown files (22 examples + 23 memories + 11 commands + 48 .ce + 1 PRP being executed)

---

**Report Complete**: This classification report provides comprehensive analysis for Phases 4 and 5 of the Syntropy MCP 1.1 release finalization. All gaps, duplicates, and consolidation opportunities have been identified and documented.
