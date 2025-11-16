# INITIAL: Critical Memory Consolidation + Auto-Activation

## Problem Statement

Currently have 24 Serena memories scattered across `.serena/memories/`, making it difficult to:

- Quickly understand project context
- Maintain consistency across memories
- Prevent memory drift and redundancy
- Ensure critical patterns are always loaded

The CE 1.1 framework introduced a memory type system (`type: regular` vs `type: critical`), but we haven't upgraded our memories to use it effectively.

**Note:** Serena auto-activation on `init_project` already works (implemented in syntropy-mcp/src/tools/init.ts:209-227). This PRP focuses on memory consolidation only.

## Desired Outcome

Consolidate all critical project knowledge into a single, well-structured Serena memory that:

1. **Always loads first** (critical type ensures priority)
2. **Covers essential patterns** (tool usage, code style, testing, PRP workflow)
3. **Eliminates redundancy** (merge overlapping memories)
4. **Easy to maintain** (one source of truth)
5. **Token efficient** (~3-5k tokens max)

## Success Criteria

- [ ] Single `ctx-eng-plus-essentials.md` memory with `type: critical`
- [ ] Consolidates 6-8 current memories (tool-usage, code-style, testing, etc.)
- [ ] Serena loads it on every activation
- [ ] Token count: 3k-5k (down from ~8k across multiple files)
- [ ] Validation: Run `ce validate --level 1` passes
- [ ] Test: New chat session loads essentials memory automatically
- [ ] Verify init_project auto-activates Serena (already implemented)

## Current State

**Serena auto-activation:** ✅ Already implemented in `syntropy-mcp/src/tools/init.ts:209-227`
- `init_project` receives `project_root` argument
- Calls `activate_project` with project root path
- Non-fatal (continues on failure)

**Existing memories** (24 total):

```
code-style-conventions.md
codebase-structure.md
linear-issue-creation-pattern.md
linear-issue-tracking-integration.md
linear-mcp-integration-example.md
linear-mcp-integration.md
project-overview.md
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
TOOL-USAGE-GUIDE.md
tool-usage-syntropy.md
use-syntropy-tools-not-bash.md
cwe78-prp22-newline-escape-issue.md
PRP-15-remediation-workflow-implementation.md
l4-validation-usage.md
```

**Critical memory candidates** (must consolidate):

1. `code-style-conventions.md` - KISS, no fishy fallbacks, UV strict
2. `suggested-commands.md` - Quick command reference
3. `task-completion-checklist.md` - Quality gates
4. `testing-standards.md` - TDD, real functionality, no mocks
5. `tool-usage-syntropy.md` - Serena-first approach
6. `use-syntropy-tools-not-bash.md` - Tool selection patterns
7. `tool-config-optimization-completed.md` - Post-lockdown tool state

**Keep separate** (specific/historical):

- `cwe78-prp22-newline-escape-issue.md` (specific bug)
- `PRP-15-remediation-workflow-implementation.md` (completed PRP)
- `linear-mcp-integration-example.md` (reference example)
- `prp-structure-initialized.md` (initialization record)

## Constraints

1. **Serena memory type system** (CE 1.1):

   ```yaml
   ---
   type: critical  # Loads first, always available
   category: documentation
   tags: [essentials, quick-reference, critical]
   created: "2025-11-16T14:00:00Z"
   updated: "2025-11-16T14:00:00Z"
   ---
   ```

2. **Token budget**: 3k-5k tokens (Serena loads all critical memories on activation)

3. **Structure** (suggested):

   ```markdown
   # Context Engineering Plus - Essentials

   ## Code Quality
   - KISS, no fishy fallbacks
   - UV strict, real functionality testing

   ## Tool Usage
   - Serena-first for code operations
   - Native tools for file ops
   - MCP tool naming: mcp__syntropy__<server>_<tool>

   ## Development Workflow
   - TDD cycle
   - PRP workflow (generate → review → execute)
   - Validation gates (L1-L4)

   ## Quick Commands
   - ce validate --level all
   - ce context health
   - /generate-prp, /execute-prp

   ## Testing Standards
   - Test before critical changes
   - No mocks in production code
   - Real functionality only
   ```

## Implementation Approach

1. **Audit current memories** - Identify overlaps and gaps
2. **Design consolidated structure** - Organize into logical sections
3. **Merge content** - Combine 6-8 memories into single file
4. **Add critical type header** - Ensure priority loading
5. **Test Serena activation** - Verify memory loads automatically
6. **Verify init auto-activation** - Test `init_project` activates Serena (already implemented)
7. **Archive old memories** - Move redundant files to `.serena/memories/archive/`
8. **Update documentation** - Reflect new memory structure in CLAUDE.md

## Open Questions

1. Should we keep `project-overview.md` separate or merge into essentials?
2. How to handle Linear integration memories (4 files)?
3. Archive location: `.serena/memories/archive/` or delete entirely?
4. Should `TOOL-USAGE-GUIDE.md` (comprehensive) remain separate from essentials (quick reference)?

## Estimated Effort

**Complexity**: LOW
**Time**: 2-3 hours
**Risk**: LOW (backup existing memories before consolidation)

## Dependencies

- CE 1.1 framework with memory type system
- Serena MCP active and functioning
- `.serena/memories/` directory structure

## References

- `.serena/memories/README.md` - Memory type system documentation
- `examples/INITIALIZATION.md` - Critical memory upgrade process
- Current memory files in `.serena/memories/`
