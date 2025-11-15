# Context Engineering Examples Index

Comprehensive catalog of all Context Engineering framework examples, organized by type and category for easy discovery.

## Quick Reference

**I want to...**

- Initialize CE framework → [Framework Initialization](#framework-initialization)
- Learn Syntropy MCP tools → [Tool Usage Guide](TOOL-USAGE-GUIDE.md)
- Initialize Serena memories → [Serena Memory Templates](#serena-memory-templates) (23 framework memories with YAML headers)
- Run batch PRPs → Slash commands: `/batch-gen-prp`, `/batch-exe-prp` (see `.claude/commands/`)
- Clean up my project → Slash command: `/vacuum` (see `.claude/commands/vacuum.md`)
- Fix context drift → `cd tools && uv run ce context health`
- Configure commands/hooks → [Slash Commands](#slash-commands)
- Understand patterns → [Patterns](#patterns)
- Migrate existing project → [Migration Workflows](#migration-workflows)

## All Examples

| Name | Type | Category | IsWorkflow | Description | Path |
|------|------|----------|-----------|-------------|------|
| **FRAMEWORK INITIALIZATION** | | | | | |
| Initialization Guide | Guide | Initialization | Yes | Master CE 1.1 framework initialization (5 phases: buckets, user files, repomix, blending, cleanup). Covers 4 scenarios: Greenfield, Mature Project, CE 1.0 Upgrade, Partial Install | [INITIALIZATION.md](INITIALIZATION.md) |
| **TEMPLATES** | | | | | |
| PRP-0 Template | Template | Initialization | Yes | Document framework installation in meta-PRP (PRP-0-CONTEXT-ENGINEERING.md template) | [templates/PRP-0-CONTEXT-ENGINEERING.md](templates/PRP-0-CONTEXT-ENGINEERING.md) |
| **SLASH COMMANDS** | | | | | |
| Batch PRP Execution | Command | Batch | Yes | Execute PRPs in parallel stages with health monitoring (see `.claude/commands/batch-exe-prp.md`) | Command: `/batch-exe-prp` |
| Batch PRP Generation | Command | Batch | Yes | Generate multiple PRPs from plan with dependency analysis (see `.claude/commands/batch-gen-prp.md`) | Command: `/batch-gen-prp` |
| Context Drift Check | Command | Context | Yes | Fast drift score check without full validation (see `.claude/commands/analyze-context.md`) | Command: `/analyze-context` |
| Denoise Documents | Command | Cleanup | Yes | Compress verbose documentation with AI-powered denoising (see `.claude/commands/denoise.md`) | Command: `/denoise` |
| Vacuum Cleanup | Command | Cleanup | Yes | Identify and remove project noise with confidence-based deletion (see `.claude/commands/vacuum.md`) | Command: `/vacuum` |
| **PATTERNS** | | | | | |
| Dedrifting Lessons | Pattern | Context | Yes | Root cause analysis for context drift with prevention strategies | [patterns/dedrifting-lessons.md](patterns/dedrifting-lessons.md) |
| Example Simple Feature | Pattern | PRP | No | Complete PRP example for adding git status summary command (ctx-eng-plus specific) | [patterns/example-simple-feature.md](patterns/example-simple-feature.md) |
| Git Message Rules | Pattern | Git | No | Git commit message formatting and convention rules (ctx-eng-plus specific) | [patterns/git-message-rules.md](patterns/git-message-rules.md) |
| Mock Marking Pattern | Pattern | Testing | Yes | Mark mocks with FIXME comments for tracking temporary test code | [patterns/mocks-marking.md](patterns/mocks-marking.md) |
| Serena Powerful Patterns | Pattern | MCP | Yes | Ch1: Basic pattern combinations (symbol navigation, debugging, semantic search). Ch2: Advanced vector DB graph patterns (mind maps, multi-agent collaboration, semantic drift detection, pattern mining) | [serena-powerful-patterns.md](serena-powerful-patterns.md) |
| **GUIDES** | | | | | |
| Tool Usage Guide | Guide | Tools | Yes | Complete tool selection guide with native-first philosophy, decision trees and examples. Updated 2025-11-06 with CE Framework Commands section | [TOOL-USAGE-GUIDE.md](TOOL-USAGE-GUIDE.md) |
| PRP Decomposition Patterns | Guide | PRP | Yes | Patterns for breaking down large features into manageable PRPs | [prp-decomposition-patterns.md](prp-decomposition-patterns.md) |
| CE Blend Command Usage | Guide | Commands | Yes | Complete guide for ce blend command (PRP-34): 4-phase pipeline, 6 domain strategies, 9 scenarios, troubleshooting | [ce-blend-usage.md](ce-blend-usage.md) |
| CE Init-Project Command Usage | Guide | Commands | Yes | Complete guide for ce init-project command (PRP-36): 4-phase pipeline, 4 scenarios, error handling for 5 known issues, performance metrics | [ce-init-project-usage.md](ce-init-project-usage.md) |
| **REFERENCE** | | | | | |
| L4 Validation Example | Reference | Validation | No | Level 4 pattern conformance validation example (ctx-eng-plus specific) | [l4-validation-example.md](l4-validation-example.md) |
| Linear Integration Example | Reference | MCP | Yes | Linear MCP integration example with configuration defaults | [linear-integration-example.md](linear-integration-example.md) |
| Mermaid Color Palette | Reference | Diagrams | Yes | Standard color palette for mermaid diagrams with light/dark themes | [mermaid-color-palette.md](mermaid-color-palette.md) |
| Syntropy Status Hook | Reference | MCP | No | Syntropy MCP health check system (references ctx-eng-plus scripts) | [syntropy-status-hook-system.md](syntropy-status-hook-system.md) |
| Settings Local Example | Reference | Configuration | Yes | Example .claude/settings.local.json with permissions (framework template) | [example.setting.local.md](example.setting.local.md) |
| tmp/ Directory Convention | Reference | Standards | Yes | Conventions for temporary file storage and cleanup | [tmp-directory-convention.md](tmp-directory-convention.md) |
| **MODEL** | | | | | |
| System Model | Model | Architecture | Yes | Complete Context Engineering framework architecture and design | [model/SystemModel.md](model/SystemModel.md) |

## Statistics

### Examples & Documentation

- **Total Examples**: 25 files (+2 new command guides)
- **Framework Initialization**: 6 (Main guide + 4 migration workflows + integration summary)
- **Templates**: 1 (PRP-0-CONTEXT-ENGINEERING.md)
- **Slash Commands**: 5 (Reference - actual commands in `.claude/commands/`)
- **Patterns**: 4 (Git, testing, context, PRP)
- **Guides**: 4 (Tools, PRP decomposition, **ce blend**, **ce init-project**) - NEW
- **Reference**: 6 (Validation, diagrams, standards, Syntropy overview)
- **Model**: 1 (System architecture)

**Note**: Workflows previously referenced in INDEX.md now exist as slash commands (`.claude/commands/`) or CLI tools (`ce` command). Migration guides and initialization documentation are new additions for CE 1.1.

### Serena Memories

- **Total Memories**: 23 files (~3,621 lines) with YAML type headers (CE 1.1)
- **Type System**: All framework memories default to `type: regular` (users upgrade to `type: critical` during target project initialization)
- **Categories**: documentation (13), pattern (5), architecture (2), configuration (4), troubleshooting (1)
- **Critical Memory Candidates**: 6 memories (code-style-conventions, suggested-commands, task-completion-checklist, testing-standards, tool-usage-syntropy, use-syntropy-tools-not-bash)
- **Memory Type README**: See `.serena/memories/README.md` for complete type system documentation
- **Storage**: `.serena/memories/` (created automatically by Serena MCP)

## Categories

### Framework Initialization

Complete CE 1.1 framework initialization and migration workflows:

| Example | Type | Duration | Description |
|---------|------|----------|-------------|
| [Initialization Guide](INITIALIZATION.md) | Guide | Variable | Master CE 1.1 framework initialization guide (5 phases: buckets, user files, repomix, blending, cleanup). Covers 4 scenarios: Greenfield (10 min), Mature Project (45 min), CE 1.0 Upgrade (40 min), Partial Install (15 min) |
| [PRP-0 Template](templates/PRP-0-CONTEXT-ENGINEERING.md) | Template | - | Document framework installation in meta-PRP |

**Total**: 2 files (1 master guide + 1 template)

**Key Features**:
- 5-phase initialization (bucket collection, user files, repomix, blending, cleanup)
- /system/ organization for framework files (separation from user files)
- YAML header system for memories and PRPs (type: regular/critical/user)
- Zero noise guarantee (legacy files cleaned up after migration)
- PRP-0 convention (document installation in meta-PRP)

### Serena Memory Templates

#### Recommended Memory Types for New Projects

Recommended initial knowledge base for Serena memory initialization in new projects:

| Memory Type | Purpose | IsWorkflow | When to Use | Example Topics |
|-------------|---------|-----------|-------------|-----------------|
| `architecture` | Document architectural decisions and design rationale | Yes | Record why certain patterns/structures were chosen | Validation approach, error handling strategy, module organization |
| `pattern` | Build reusable solution library | Yes | Store recurring solution patterns discovered during development | Retry strategies, error recovery, async patterns, testing approaches |
| `troubleshooting` | Capture issue resolution steps for recurring problems | Yes | Document root causes and fixes for common issues | MCP connection errors, git conflicts, validation failures |
| `configuration` | Setup notes and configuration guidelines | Yes | Record framework setup decisions and best practices | Serena project activation, hook configuration, path conventions |
| `documentation` | Cache frequently-accessed library documentation | Yes | Store Context7-fetched docs for quick offline access | Next.js routing, React patterns, Python asyncio guides |
| `note` | Record session insights, handoffs, and observations | Conditional | Preserve context between sessions; project-specific when filled | Session end state, discovered gotchas, optimization insights |

**Initialization Strategy**: When activating Serena for a new CE project, create template memories for architecture, pattern, troubleshooting, and configuration types with framework-level guidance. Let projects accumulate documentation and note types organically during development.

#### Existing Project Memories

Current knowledge base in `.serena/memories/` (23 files, ~3,719 lines):

**Universal Memories (IsWorkflow = Yes)** - Suitable for copying to new projects:

| Memory | Type | Purpose | Lines |
|--------|------|---------|-------|
| [code-style-conventions.md](.serena/memories/code-style-conventions.md) | pattern | Coding principles: KISS, no fishy fallbacks, mock marking, function/file size limits | 129 |
| [suggested-commands.md](.serena/memories/suggested-commands.md) | documentation | Common commands reference (UV, pytest, CE tools, Darwin) | 98 |
| [task-completion-checklist.md](.serena/memories/task-completion-checklist.md) | documentation | Pre-commit verification checklist with all quality gates | 80 |
| [testing-standards.md](.serena/memories/testing-standards.md) | pattern | Testing philosophy: real functionality, no mocks, TDD approach | 87 |
| [tool-usage-syntropy.md](.serena/memories/tool-usage-syntropy.md) | documentation | Comprehensive Syntropy tool selection guide with decision trees | 425 |
| [use-syntropy-tools-not-bash.md](.serena/memories/use-syntropy-tools-not-bash.md) | pattern | Core principle & migration patterns: prefer Syntropy over bash | 200 |

**Project-Specific Memories (IsWorkflow = No)** - Ctx-eng-plus custom knowledge:

| Memory | Type | Purpose | Lines |
|--------|------|---------|-------|
| [codebase-structure.md](.serena/memories/codebase-structure.md) | architecture | Complete directory layout and module organization | 196 |
| [cwe78-prp22-newline-escape-issue.md](.serena/memories/cwe78-prp22-newline-escape-issue.md) | troubleshooting | Security issue with Serena regex replacement and workaround | 100 |
| [l4-validation-usage.md](.serena/memories/l4-validation-usage.md) | pattern | L4 validation system usage, modules, and drift thresholds | 150 |
| [linear-issue-creation-pattern.md](.serena/memories/linear-issue-creation-pattern.md) | pattern | Working example for Linear issue creation with PRP metadata | 69 |
| [linear-issue-tracking-integration.md](.serena/memories/linear-issue-tracking-integration.md) | pattern | Bi-directional Linear/PRP integration workflow | 213 |
| [linear-mcp-integration-example.md](.serena/memories/linear-mcp-integration-example.md) | pattern | Linear MCP integration with configuration defaults | 101 |
| [linear-mcp-integration.md](.serena/memories/linear-mcp-integration.md) | documentation | Complete Linear MCP tool reference (20+ tools) | 114 |
| [project-overview.md](.serena/memories/project-overview.md) | documentation | Master project documentation with tech stack & features | 188 |
| [PRP-15-remediation-workflow-implementation.md](.serena/memories/PRP-15-remediation-workflow-implementation.md) | documentation | Implementation record for PRP-15 remediation workflow | 206 |
| [prp-2-implementation-patterns.md](.serena/memories/prp-2-implementation-patterns.md) | pattern | State management patterns and atomic write practices | 330 |
| [prp-backlog-system.md](.serena/memories/prp-backlog-system.md) | configuration | PRP backlog directory system and workflow | 106 |
| [prp-structure-initialized.md](.serena/memories/prp-structure-initialized.md) | documentation | PRP structure initialization completion record | 80 |
| [serena-implementation-verification-pattern.md](.serena/memories/serena-implementation-verification-pattern.md) | pattern | Pattern for verifying PRP implementations with Serena symbol lookup | 139 |
| [serena-mcp-tool-restrictions.md](.serena/memories/serena-mcp-tool-restrictions.md) | configuration | Current tool restrictions, allowed tools, and workarounds | 236 |
| [syntropy-status-hook-pattern.md](.serena/memories/syntropy-status-hook-pattern.md) | pattern | Cache-based architecture for SessionStart hook MCP access | 177 |
| [system-model-specification.md](.serena/memories/system-model-specification.md) | documentation | Formal specification of Context Engineering target architecture | 157 |
| [tool-config-optimization-completed.md](.serena/memories/tool-config-optimization-completed.md) | documentation | Completion record for tool config optimization (7 violations resolved) | 63 |

**Summary**: 23 framework memories with YAML type headers (CE 1.1)
- 6 critical memory candidates (type: regular by default, upgrade to type: critical during initialization)
- 17 project-specific memories (ctx-eng-plus custom knowledge)
- See `.serena/memories/README.md` for complete memory type system documentation

**Storage**: `.serena/memories/` (created automatically by Serena MCP)

**Related Documentation**:
- [Tool Usage Guide](TOOL-USAGE-GUIDE.md) - Native-first tool selection philosophy
- [Initialization Guide](INITIALIZATION.md) - Framework initialization and memory setup

### Slash Commands & CLI Tools

Workflow automation via slash commands and CLI tools:

| Command | Type | Description |
|---------|------|-------------|
| `/batch-gen-prp` | Slash Command | Generate multiple PRPs from plan with dependency analysis (see `.claude/commands/batch-gen-prp.md`) |
| `/batch-exe-prp` | Slash Command | Execute PRPs in parallel stages with health monitoring (see `.claude/commands/batch-exe-prp.md`) |
| `/vacuum` | Slash Command | Identify and remove project noise with confidence-based deletion (see `.claude/commands/vacuum.md`) |
| `/denoise` | Slash Command | Compress verbose documentation with AI-powered denoising (see `.claude/commands/denoise.md`) |
| `/analyze-context` | Slash Command | Fast drift score check without full validation (see `.claude/commands/analyze-context.md`) |
| `ce context health` | CLI Tool | Context health check with drift analysis (see `tools/ce/context.py`) |
| `ce validate --level 4` | CLI Tool | Full validation suite with L1-L4 checks (see `tools/ce/validate.py`) |
| `ce vacuum` | CLI Tool | Vacuum cleanup with execute/auto modes (see `tools/ce/` CLI) |

**Total**: 5 slash commands + 3 CLI tools

**Documentation**: All slash commands documented in `.claude/commands/`, CLI tools documented in `tools/README.md`

### Configuration

Commands and hooks:

| Example | Lines | Focus |
|---------|-------|-------|
| [Hook Configuration](config/hook-configuration.md) | 649 | Lifecycle hooks (pre-commit, session-start) |
| [Slash Command Template](config/slash-command-template.md) | 622 | Custom command creation |

**Total**: 2 examples, 1,271 lines

### Patterns

Reusable patterns and practices:

| Example | Lines | Focus |
|---------|-------|-------|
| [Dedrifting Lessons](patterns/dedrifting-lessons.md) | 241 | Context drift prevention |
| [Git Message Rules](patterns/git-message-rules.md) | 205 | Commit message conventions |
| [Example Simple Feature](patterns/example-simple-feature.md) | 182 | Complete PRP example |
| [Mock Marking](patterns/mocks-marking.md) | 96 | Test mock tracking |

**Total**: 4 examples, 724 lines

### Guides

Comprehensive guides:

| Example | Lines | Focus |
|---------|-------|-------|
| [Tool Usage Guide](TOOL-USAGE-GUIDE.md) | 606 | Native-first tool selection philosophy |
| [PRP Decomposition Patterns](prp-decomposition-patterns.md) | 357 | Breaking down large features |

**Total**: 2 examples, 963 lines

### Reference

Quick reference materials:

| Example | Lines | Focus |
|---------|-------|-------|
| [Mermaid Color Palette](mermaid-color-palette.md) | 313 | Diagram color standards |
| [L4 Validation Example](l4-validation-example.md) | 290 | Pattern conformance validation |
| [Linear Integration Example](linear-integration-example.md) | 204 | Legacy Linear example |
| [Syntropy Status Hook](syntropy-status-hook-system.md) | 149 | MCP health check |
| [tmp/ Convention](tmp-directory-convention.md) | 130 | Temp file standards |
| [Settings Local Example](example.setting.local.md) | 17 | Configuration example |

**Total**: 6 examples, 1,103 lines

### Model

System architecture:

| Example | Lines | Focus |
|---------|-------|-------|
| [System Model](model/SystemModel.md) | 2,981 | Complete framework architecture |

**Total**: 1 example, 2,981 lines

## IsWorkflow Distribution

### Examples

- **Yes** (Universal/Framework): 21 examples (84%)
- **No** (Project-Specific): 4 examples (16%)

### Serena Memories

- **Yes** (Universal/Framework): 6 memories (1,013 lines, 28%) - Suitable for all CE projects
- **No** (Project-Specific): 17 memories (2,608 lines, 72%) - Ctx-eng-plus custom knowledge

### Classification Legend

**IsWorkflow = Yes**: Universal CE framework documentation that should be copied to any target project during initialization. Includes MCP patterns, generic workflows, framework config templates, reusable practices, and essential coding/testing standards.

**IsWorkflow = No**: Project-specific documentation tied to ctx-eng-plus codebase, conventions, or implementation details. Not suitable for general distribution to other projects.

### Project-Specific Examples (No)

1. **Example Simple Feature** (patterns/) - Demonstrates adding git status summary command specific to ctx-eng-plus
2. **Git Message Rules** (patterns/) - Commit message conventions specific to this project
3. **L4 Validation Example** (reference/) - Validation patterns specific to ctx-eng-plus infrastructure
4. **Syntropy Status Hook** (reference/) - References ctx-eng-plus-specific scripts (scripts/session-startup.sh)

### Universal Serena Memories to Copy to New Projects

1. **code-style-conventions** (pattern) - Coding principles and standards
2. **suggested-commands** (documentation) - Common command reference
3. **task-completion-checklist** (documentation) - Quality gates verification
4. **testing-standards** (pattern) - Testing philosophy and practices
5. **tool-usage-syntropy** (documentation) - Syntropy tool selection guide
6. **use-syntropy-tools-not-bash** (pattern) - Migration patterns and principles

## Syntropy Integration

**Examples using Syntropy MCP**: 9/25 (36%)

- **Heavy usage** (20+ references): Serena Symbol Search (58), Linear Integration (30), Context7 Docs (29), Tool Usage Guide (34), Memory Management (34), Syntropy README (navigation hub)
- **Moderate usage** (5-20 references): Thinking Sequential (17), System Model (2)
- **Light usage** (1-5 references): Syntropy Status Hook (1), Slash Command Template (1)

## Usage Patterns

### By Use Case

**Starting with Context Engineering**:

1. [System Model](model/SystemModel.md) - Understand framework architecture
2. [Tool Usage Guide](TOOL-USAGE-GUIDE.md) - Learn tool selection
3. [Example Simple Feature](patterns/example-simple-feature.md) - See complete PRP
4. [Execute PRP workflow](workflows/batch-prp-execution.md) - Implement PRPs

**Learning Syntropy MCP**:

1. [Syntropy README](syntropy/README.md) - Master overview, decision matrix, tool naming
2. [Serena Symbol Search](syntropy/serena-symbol-search.md) - Code navigation and refactoring
3. [Context7 Docs Fetch](syntropy/context7-docs-fetch.md) - Library documentation fetching
4. [Linear Integration](syntropy/linear-integration.md) - Issue tracking and project management

**Maintaining Project Health**:

1. [Context Drift Remediation](workflows/context-drift-remediation.md) - Sync PRPs
2. [Vacuum Cleanup](workflows/vacuum-cleanup.md) - Remove noise
3. [Denoise Documents](workflows/denoise-documents.md) - Compress docs
4. [Dedrifting Lessons](patterns/dedrifting-lessons.md) - Prevention strategies

**Batch Operations**:

1. [Batch PRP Generation](workflows/batch-prp-generation.md) - Generate from plan
2. [Batch PRP Execution](workflows/batch-prp-execution.md) - Execute in parallel
3. [PRP Decomposition Patterns](prp-decomposition-patterns.md) - Break down features

**Configuration**:

1. [Slash Command Template](config/slash-command-template.md) - Create commands
2. [Hook Configuration](config/hook-configuration.md) - Lifecycle hooks
3. [Settings Local Example](example.setting.local.md) - Configuration format

## Maintenance

**Updating this index**:

When adding new examples:

1. Create example file following content template (150-300 lines)
2. Add entry to appropriate category section above
3. Update statistics
4. Commit: `git add examples/ && git commit -m "Examples: Added [name]"`

**Content template**:

- **Purpose**: What this example demonstrates, when to use
- **Prerequisites**: Required setup
- **Examples**: 3-4 concrete examples with input/output
- **Common Patterns**: 3-5 patterns
- **Anti-Patterns**: 2-3 things not to do
- **Related**: Links to related examples

## Related Documentation

- [CLAUDE.md](../CLAUDE.md) - Project guide and quick commands
- [PRPs/](../PRPs/) - Executed and feature request PRPs
- [.claude/commands/](../.claude/commands/) - Slash commands (11 framework commands including peer-review)

## Contributing

To add new examples:

1. Follow [content template](syntropy/README.md#content-template) structure
2. Add to appropriate directory (syntropy/, workflows/, config/, patterns/)
3. Update INDEX.md with new entry
4. Cross-link with related examples
5. Run validation: `cd tools && uv run ce validate --level 4`
