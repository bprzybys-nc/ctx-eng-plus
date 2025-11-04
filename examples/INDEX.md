# Context Engineering Examples Index

Comprehensive catalog of all Context Engineering framework examples, organized by type and category for easy discovery.

## Quick Reference

**I want to...**

- Learn Syntropy MCP tools → [Syntropy MCP](#syntropy-mcp)
- Run batch PRPs → [Batch Workflows](#batch-workflows)
- Clean up my project → [Vacuum Guide](workflows/vacuum-cleanup.md)
- Fix context drift → [Drift Remediation](workflows/context-drift-remediation.md)
- Configure commands/hooks → [Configuration](#configuration)
- Understand patterns → [Patterns](#patterns)

## All Examples

| Name | Type | Category | IsWorkflow | Syntropy | Description | Path |
|------|------|----------|-----------|----------|-------------|------|
| **SYNTROPY MCP** | | | | | | |
| Syntropy README | Reference | MCP | Yes | Yes (Syntropy) | Master overview: tool naming, decision matrix, when to use Syntropy vs native tools | [syntropy/README.md](syntropy/README.md) |
| Context7 Docs Fetch | Pattern | MCP | Yes | Yes (Context7) | Fetch library documentation with topic focus and token optimization | [syntropy/context7-docs-fetch.md](syntropy/context7-docs-fetch.md) |
| Linear Integration | Pattern | MCP | Yes | Yes (Linear) | Create, update, and manage Linear issues from PRPs | [syntropy/linear-integration.md](syntropy/linear-integration.md) |
| Memory Management | Pattern | MCP | Yes | Yes (Serena) | Store and retrieve persistent knowledge using Serena memory | [syntropy/memory-management.md](syntropy/memory-management.md) |
| Serena Symbol Search | Pattern | MCP | Yes | Yes (Serena) | Navigate code symbols, find definitions, search patterns, refactor safely | [syntropy/serena-symbol-search.md](syntropy/serena-symbol-search.md) |
| Thinking Sequential | Pattern | MCP | Yes | Yes (Thinking) | Structured multi-step reasoning with branching and revision | [syntropy/thinking-sequential.md](syntropy/thinking-sequential.md) |
| **WORKFLOWS** | | | | | | |
| Batch PRP Execution | Workflow | Batch | Yes | No | Execute PRPs in parallel using git worktrees with health monitoring | [workflows/batch-prp-execution.md](workflows/batch-prp-execution.md) |
| Batch PRP Generation | Workflow | Batch | Yes | No | Generate multiple PRPs from plan with dependency analysis | [workflows/batch-prp-generation.md](workflows/batch-prp-generation.md) |
| Context Drift Remediation | Workflow | Context | Yes | No | Detect, analyze, and remediate context drift between PRPs and codebase | [workflows/context-drift-remediation.md](workflows/context-drift-remediation.md) |
| Denoise Documents | Workflow | Cleanup | Yes | No | Compress verbose documentation using AI-powered denoising | [workflows/denoise-documents.md](workflows/denoise-documents.md) |
| Vacuum Cleanup | Workflow | Cleanup | Yes | No | Identify and remove project noise with confidence-based deletion | [workflows/vacuum-cleanup.md](workflows/vacuum-cleanup.md) |
| **CONFIGURATION** | | | | | | |
| Hook Configuration | Configuration | Hooks | Yes | No | Configure lifecycle hooks (session-start, pre-commit, prompt-submit) | [config/hook-configuration.md](config/hook-configuration.md) |
| Slash Command Template | Configuration | Commands | Yes | No | Create custom slash commands using markdown-based definitions | [config/slash-command-template.md](config/slash-command-template.md) |
| **PATTERNS** | | | | | | |
| Dedrifting Lessons | Pattern | Context | Yes | No | Root cause analysis for context drift with prevention strategies | [patterns/dedrifting-lessons.md](patterns/dedrifting-lessons.md) |
| Example Simple Feature | Pattern | PRP | No | No | Complete PRP example for adding git status summary command (ctx-eng-plus specific) | [patterns/example-simple-feature.md](patterns/example-simple-feature.md) |
| Git Message Rules | Pattern | Git | No | No | Git commit message formatting and convention rules (ctx-eng-plus specific) | [patterns/git-message-rules.md](patterns/git-message-rules.md) |
| Mock Marking Pattern | Pattern | Testing | Yes | No | Mark mocks with FIXME comments for tracking temporary test code | [patterns/mocks-marking.md](patterns/mocks-marking.md) |
| **GUIDES** | | | | | | |
| Tool Usage Guide | Guide | Tools | Yes | Yes (Multiple) | Complete tool selection guide with decision trees and examples | [TOOL-USAGE-GUIDE.md](TOOL-USAGE-GUIDE.md) |
| PRP Decomposition Patterns | Guide | PRP | Yes | No | Patterns for breaking down large features into manageable PRPs | [prp-decomposition-patterns.md](prp-decomposition-patterns.md) |
| **REFERENCE** | | | | | | |
| L4 Validation Example | Reference | Validation | No | No | Level 4 pattern conformance validation example (ctx-eng-plus specific) | [l4-validation-example.md](l4-validation-example.md) |
| Linear Integration Example | Reference | MCP | Yes | No | Legacy Linear MCP integration example | [linear-integration-example.md](linear-integration-example.md) |
| Mermaid Color Palette | Reference | Diagrams | Yes | No | Standard color palette for mermaid diagrams with light/dark themes | [mermaid-color-palette.md](mermaid-color-palette.md) |
| Syntropy Status Hook | Reference | MCP | No | Yes (Syntropy) | Syntropy MCP health check system (references ctx-eng-plus scripts) | [syntropy-status-hook-system.md](syntropy-status-hook-system.md) |
| Settings Local Example | Reference | Configuration | Yes | No | Example .claude/settings.local.json with permissions (framework template) | [example.setting.local.md](example.setting.local.md) |
| tmp/ Directory Convention | Reference | Standards | Yes | No | Conventions for temporary file storage and cleanup | [tmp-directory-convention.md](tmp-directory-convention.md) |
| **MODEL** | | | | | | |
| System Model | Model | Architecture | Yes | Yes (Syntropy) | Complete Context Engineering framework architecture and design | [model/SystemModel.md](model/SystemModel.md) |

## Statistics

- **Total Examples**: 25
- **Syntropy Examples**: 6 (MCP integration overview + patterns)
- **Workflows**: 5 (Batch, cleanup, context management)
- **Configuration**: 2 (Commands, hooks)
- **Patterns**: 4 (Git, testing, context, PRP)
- **Guides**: 2 (Tools, PRP decomposition)
- **Reference**: 6 (Validation, diagrams, standards, Syntropy overview)
- **Model**: 1 (System architecture)

## Categories

### Syntropy MCP

Examples and reference for using Syntropy MCP integration (Serena, Context7, Thinking, Linear):

| Example | Tools | Lines | Description |
|---------|-------|-------|-------------|
| [Syntropy README](syntropy/README.md) | Syntropy | 208 | Master overview, tool naming, decision matrix |
| [Serena Symbol Search](syntropy/serena-symbol-search.md) | Serena | 917 | Code navigation, refactoring, symbol tracking |
| [Memory Management](syntropy/memory-management.md) | Serena | 625 | Persistent knowledge storage and retrieval |
| [Linear Integration](syntropy/linear-integration.md) | Linear | 592 | Issue tracking integration |
| [Context7 Docs Fetch](syntropy/context7-docs-fetch.md) | Context7 | 478 | Library documentation fetching |
| [Thinking Sequential](syntropy/thinking-sequential.md) | Thinking | 342 | Complex reasoning patterns |

**Total**: 6 examples, 3,162 lines

### Batch Workflows

Parallel PRP generation and execution:

| Example | Lines | Focus |
|---------|-------|-------|
| [Batch PRP Generation](workflows/batch-prp-generation.md) | 560 | Generate PRPs from plan with dependency analysis |
| [Batch PRP Execution](workflows/batch-prp-execution.md) | 526 | Execute PRPs in parallel with worktrees |

**Total**: 2 examples, 1,086 lines

### Cleanup Workflows

Project maintenance and optimization:

| Example | Lines | Focus |
|---------|-------|-------|
| [Context Drift Remediation](workflows/context-drift-remediation.md) | 637 | Sync PRPs with codebase |
| [Vacuum Cleanup](workflows/vacuum-cleanup.md) | 536 | Remove project noise |
| [Denoise Documents](workflows/denoise-documents.md) | 500 | Compress verbose docs |

**Total**: 3 examples, 1,673 lines

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

- **Yes** (Universal/Framework): 21 examples (84%)
- **No** (Project-Specific): 4 examples (16%)

### Classification Legend

**IsWorkflow = Yes**: Universal CE framework documentation that should be copied to any target project during initialization. Includes MCP patterns, generic workflows, framework config templates, and reusable practices.

**IsWorkflow = No**: Project-specific documentation tied to ctx-eng-plus codebase or conventions. Not suitable for general distribution to other projects.

### Project-Specific Examples (No)

1. **Example Simple Feature** (patterns/) - Demonstrates adding git status summary command specific to ctx-eng-plus
2. **Git Message Rules** (patterns/) - Commit message conventions specific to this project
3. **L4 Validation Example** (reference/) - Validation patterns specific to ctx-eng-plus infrastructure
4. **Syntropy Status Hook** (reference/) - References ctx-eng-plus-specific scripts (scripts/session-startup.sh)

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
- [.ce/RULES.md](../.ce/RULES.md) - Framework rules and principles
- [PRPs/](../PRPs/) - Executed and feature request PRPs
- [.claude/commands/](../.claude/commands/) - Slash commands

## Contributing

To add new examples:

1. Follow [content template](syntropy/README.md#content-template) structure
2. Add to appropriate directory (syntropy/, workflows/, config/, patterns/)
3. Update INDEX.md with new entry
4. Cross-link with related examples
5. Run validation: `cd tools && uv run ce validate --level 4`
