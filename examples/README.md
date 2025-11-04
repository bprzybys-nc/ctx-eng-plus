# Context Engineering Examples

Comprehensive collection of examples, patterns, and workflows for the Context Engineering framework.

## 📋 **[INDEX.md](INDEX.md) - Start Here**

**Complete catalog of all 25 examples** with searchable table, categories, and quick reference.

Browse by:

- **Type**: Patterns, Workflows, Configuration, Guides, Reference
- **Category**: MCP, Batch, Cleanup, Context, Git, Testing
- **Complexity**: Low, Medium, High
- **Syntropy Integration**: Yes/No with server names

## Structure

```
examples/
├── INDEX.md                    # 📋 Complete catalog (start here!)
├── README.md                   # This file
├── syntropy/                   # Syntropy MCP integration examples
│   ├── README.md               # 🔶 Master overview: tool naming, decision matrix
│   ├── serena-symbol-search.md      # Code navigation & refactoring
│   ├── memory-management.md         # Persistent knowledge storage
│   ├── linear-integration.md        # Issue tracking & project management
│   ├── context7-docs-fetch.md       # Library documentation fetching
│   └── thinking-sequential.md       # Complex multi-step reasoning
├── workflows/                  # Complete workflow examples
│   ├── batch-prp-generation.md      # Parallel PRP generation
│   ├── batch-prp-execution.md       # Parallel PRP execution
│   ├── vacuum-cleanup.md            # Project cleanup
│   ├── denoise-documents.md         # Document compression
│   └── context-drift-remediation.md # Context sync
├── config/                     # Configuration examples
│   ├── slash-command-template.md    # Create custom commands
│   └── hook-configuration.md        # Lifecycle hooks
├── patterns/                   # Reusable patterns
│   ├── dedrifting-lessons.md        # Context drift prevention
│   ├── git-message-rules.md         # Commit conventions
│   ├── example-simple-feature.md    # Complete PRP example
│   └── mocks-marking.md             # Test mock tracking
├── model/                      # System architecture
│   └── SystemModel.md               # Framework architecture
└── [other reference files]
```

## Quick Start

### New to Context Engineering?

1. **[INDEX.md](INDEX.md)** - Browse all examples
2. **[System Model](model/SystemModel.md)** - Understand framework architecture
3. **[Tool Usage Guide](TOOL-USAGE-GUIDE.md)** - Learn tool selection
4. **[Example Simple Feature](patterns/example-simple-feature.md)** - See complete PRP

### Learning Syntropy MCP?

1. **[Syntropy README](syntropy/README.md)** - Master overview, tool naming, decision matrix
2. **[Serena Symbol Search](syntropy/serena-symbol-search.md)** - Code navigation and refactoring
3. **[Context7 Docs Fetch](syntropy/context7-docs-fetch.md)** - Library documentation fetching
4. **[Linear Integration](syntropy/linear-integration.md)** - Issue tracking and project management

### Need to Clean Up Project?

1. **[Context Drift Remediation](workflows/context-drift-remediation.md)** - Sync PRPs with codebase
2. **[Vacuum Cleanup](workflows/vacuum-cleanup.md)** - Remove project noise
3. **[Denoise Documents](workflows/denoise-documents.md)** - Compress verbose docs

### Want to Run Batch PRPs?

1. **[Batch PRP Generation](workflows/batch-prp-generation.md)** - Generate from plan
2. **[Batch PRP Execution](workflows/batch-prp-execution.md)** - Execute in parallel
3. **[PRP Decomposition Patterns](prp-decomposition-patterns.md)** - Break down features

## Statistics

- **25 Examples**: Patterns, workflows, configuration, guides, reference
- **~10,963 Total Lines**: Comprehensive coverage
- **6 Syntropy Examples**: MCP integration overview + patterns (Serena, Context7, Linear, Thinking)
- **9 Examples Using Syntropy MCP**: Across all categories
- **5 Workflows**: Batch operations, cleanup, context management
- **21 IsWorkflow=Yes Examples**: Universal framework boilerplate
- **4 IsWorkflow=No Examples**: Project-specific documentation

## Content Template

All examples follow consistent structure:

1. **Purpose**: What this demonstrates, when to use
2. **Prerequisites**: Required setup
3. **Examples**: 3-4 concrete examples with input/output
4. **Common Patterns**: 3-5 recommended patterns
5. **Anti-Patterns**: 2-3 things not to do
6. **Related Examples**: Cross-links

Length: 150-300 lines (Medium complexity)

## Adding Examples

When adding new examples:

1. Follow content template structure
2. Add to appropriate directory (syntropy/, workflows/, config/, patterns/)
3. Update **[INDEX.md](INDEX.md)** with new entry
4. Cross-link with 2-3 related examples
5. Run validation: `cd tools && uv run ce validate --level 4`
6. Commit: `git add examples/ && git commit -m "Examples: Added [name]"`

## Related Documentation

- **[CLAUDE.md](../CLAUDE.md)** - Project guide and quick commands
- **[.ce/RULES.md](../.ce/RULES.md)** - Framework rules and principles
- **[PRPs/](../PRPs/)** - Executed and feature request PRPs
- **[.claude/commands/](../.claude/commands/)** - Slash commands

## Contributing

Keep examples:

- **Concise**: 150-300 lines (sweet spot)
- **Practical**: Real-world usage patterns
- **Complete**: Follow content template
- **Cross-linked**: 2-3 related examples
- **Validated**: Pass L1-L4 validation gates
