# Syntropy MCP - Project Guide

**v0.1.0**: Aggregation layer routing 78 tools across 9 MCP servers. Format: `mcp__syntropy_<server>_<tool>`.

## Commands

- `/generate-prp <feature>` - Generate PRP from INITIAL.md
- `/execute-prp <prp-file>` - Execute PRP
- `/update-context` - Sync context with codebase
- `/peer-review [prp] [exe]` - Review PRP or execution
- `/syntropy-health [full]` - Check MCP servers (auto-runs on start)
- `/denoise <file>` - Boil out noise, preserve all essential info (60-75% reduction)

## Session Start

Auto health check shows:
```
✅ serena, filesystem, git, thinking, linear, github, perplexity, context7, repomix
Total: 9/9 healthy
```

**Manual check**: Call `mcp__syntropy__healthcheck(detailed=true)` for diagnostics

**If failures**: `rm -rf ~/.mcp-auth` (pre-approved)

## Test Noise (Ignore)

Serena language server errors during `npm test` are expected:
- Tests delete temp dirs before async init completes
- Activation succeeds, errors are harmless background noise

## Core Rules

### No Fishy Fallbacks
- Fast failure: Let exceptions bubble up
- Actionable errors: Include 🔧 troubleshooting
- No silent corruption

### Code Quality
- Functions: 50 lines (single responsibility)
- Files: 500 lines (logical modules)
- Classes: 100 lines (single concept)
- Mark mocks with FIXME in production code

### Testing
- TDD: Test first → fail → implement → refactor
- Real functionality: No fake results
- Test before critical changes (tool naming, API changes, refactoring)

## Resources

- `.ce/` - System boilerplate (don't modify directly)
- `.ce/RULES.md` - Framework rules
- `.ce/examples/system/` - Implementation patterns
- `PRPs/` - User feature requests
- `examples/` - User code patterns
