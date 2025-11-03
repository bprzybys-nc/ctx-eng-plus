# Slash Command Template

Complete guide for creating custom slash commands in Claude Code using markdown-based command definitions.

## Purpose

Slash commands enable:

- **Interactive workflows**: Trigger complex operations with simple commands
- **Reusable patterns**: Codify common workflows as commands
- **Team collaboration**: Share commands via git
- **Context awareness**: Commands have access to project context
- **Composability**: Chain commands together

**When to Use**:

- Repeated workflows (PRP generation, validation, cleanup)
- Complex multi-step operations
- Team-specific workflows
- Context-aware automation

**When NOT to Use**:

- One-off operations → Use direct tool calls
- Simple bash commands → Use Bash tool directly
- External tools → Use MCP integration

## Prerequisites

- Claude Code installed and configured
- Project with `.claude/commands/` directory
- Understanding of markdown syntax
- Familiarity with Claude Code tools

## Command Structure

### Required Sections

Every slash command must have:

1. **Title** (H1): Command name and brief description
2. **Usage**: How to invoke the command
3. **What It Does**: Detailed explanation of command behavior

### Optional Sections

Recommended but not required:

- **Arguments**: Parameters the command accepts
- **Examples**: Common usage patterns
- **Configuration**: Settings and customization
- **Troubleshooting**: Common issues and solutions
- **Related Commands**: Links to similar commands

## Template

```markdown
# Command Name - Brief Description

One-sentence summary of what this command does.

## Usage

```
/command-name [arguments]
```

**Arguments**:

- `arg1` (required): Description of first argument
- `arg2` (optional): Description of second argument

## What It Does

Detailed explanation of command behavior:

1. Step 1: What happens first
2. Step 2: What happens next
3. Step 3: Final step

Output: Description of what user sees

## Examples

### Example 1: Basic Usage

```
/command-name simple-arg
```

**Output**:

```
Command output example
```

### Example 2: Advanced Usage

```
/command-name arg1 --flag arg2
```

**Output**:

```
Advanced output example
```

## Configuration

**Config File**: `.ce/command-config.yml`

```yaml
setting1: value1
setting2: value2
```

**Environment Variables**:

- `ENV_VAR_1`: Description
- `ENV_VAR_2`: Description

## Troubleshooting

### Issue: Error message example

**Cause**: Why this error occurs

**Solution**:

```bash
# Steps to fix
command to run
```

## Related Commands

- `/related-command-1` - Brief description
- `/related-command-2` - Brief description
```

## Location and Naming

### Directory Structure

```
.claude/
└── commands/
    ├── execute-prp.md          # Simple name
    ├── batch-gen-prp.md        # Hyphen-separated
    ├── syntropy-health.md      # Topic-focused
    └── custom-workflow.md      # Your custom command
```

### Naming Conventions

**Format**: `{action}-{noun}.md` or `{topic}-{action}.md`

**Examples**:

- ✅ Good: `execute-prp.md`, `batch-gen-prp.md`, `syntropy-health.md`
- ❌ Bad: `ExecutePRP.md`, `execute_prp.md`, `prp.md`

**Rules**:

- Lowercase only
- Hyphens (not underscores or spaces)
- Descriptive (3-20 characters)
- Action-oriented (verb-noun)

### Command Invocation

Filename determines command name:

```
File: .claude/commands/execute-prp.md
Invoke: /execute-prp
```

## Real Examples

### Example 1: Execute PRP

**File**: `.claude/commands/execute-prp.md`

```markdown
# Execute PRP - Implement Single PRP with Validation

Execute a single PRP (Product Requirements Prompt) with full validation and Linear issue updates.

## Usage

```
/execute-prp <prp-path>
```

**Arguments**:

- `prp-path` (required): Path to PRP file (e.g., `PRPs/feature-requests/PRP-32.md`)

## What It Does

1. **Parse PRP**: Extract metadata (prp_id, status, dependencies)
2. **Validate prerequisites**: Check dependencies completed
3. **Create git branch**: `prp-{id}-{slug}`
4. **Execute phases**: Implement each phase sequentially
5. **Run validation**: L1 (syntax) → L2 (tests) → L3 (integration) → L4 (patterns)
6. **Update Linear**: Mark issue as "Done" if validation passes
7. **Commit changes**: Auto-commit with PRP ID in message

Output: Execution summary with validation results

## Examples

### Example 1: Execute New Feature PRP

```
/execute-prp PRPs/feature-requests/PRP-35-user-auth.md
```

**Output**:

```
🚀 Executing PRP-35: User Authentication
============================================================
Phase 1/4: Database Schema... ✅ (45s)
Phase 2/4: JWT Tokens... ✅ (90s)
Phase 3/4: API Endpoints... ✅ (60s)
Phase 4/4: RBAC... ✅ (75s)

Validation:
  L1 (Syntax): ✅ Pass
  L2 (Tests): ✅ Pass (24/24)
  L3 (Integration): ✅ Pass
  L4 (Patterns): ✅ Pass

Linear: CTX-145 → Done
Git: Committed to prp-35-user-auth branch
============================================================
```

## Configuration

None required. Uses Linear defaults from `.ce/linear-defaults.yml`.

## Troubleshooting

### Issue: "PRP file not found"

**Cause**: Invalid path or file doesn't exist

**Solution**:

```bash
# List available PRPs
ls PRPs/feature-requests/

# Use full path
/execute-prp PRPs/feature-requests/PRP-35-user-auth.md
```

## Related Commands

- `/batch-exe-prp` - Execute batch of PRPs
- `/generate-prp` - Create new PRP
```

### Example 2: Syntropy Health

**File**: `.claude/commands/syntropy-health.md`

```markdown
# Syntropy Health Check - MCP Server Diagnostics

Check health status of all Syntropy MCP servers and display connection details.

## Usage

```
/syntropy-health
```

**No arguments required.**

## What It Does

1. **Query Syntropy**: Call `mcp__syntropy__healthcheck` tool
2. **Parse results**: Extract server status (connected/disconnected/error)
3. **Format output**: Display table with server names and status
4. **Show tools**: List available tools per server
5. **Cache results**: Store in `/tmp/syntropy-health.json` (5min cache)

Output: Health status table + tool count summary

## Examples

### Example 1: Basic Health Check

```
/syntropy-health
```

**Output**:

```
🔧 Syntropy MCP Status
============================================================
Total: 9 | ✅ 9 | ⚠️  0 | ❌ 0

Servers:
  ✅ serena          [connected   ] 11 tools
  ✅ filesystem      [connected   ] 8 tools
  ✅ context7        [connected   ] 2 tools
  ✅ thinking        [connected   ] 1 tool
  ✅ linear          [connected   ] 9 tools

============================================================
All MCP servers operational. 31 tools available.
```

### Example 2: With Errors

```
/syntropy-health
```

**Output**:

```
🔧 Syntropy MCP Status
============================================================
Total: 9 | ✅ 7 | ⚠️  1 | ❌ 1

Servers:
  ✅ serena          [connected   ]
  ❌ linear          [disconnected] Auth required
  ⚠️  context7       [degraded    ] Slow response

Errors:
  linear: Authentication token missing
    Fix: rm -rf ~/.mcp-auth && /mcp

  context7: API rate limit exceeded
    Fix: Wait 60s or upgrade plan

============================================================
```

## Configuration

None required.

## Troubleshooting

### Issue: "All servers disconnected"

**Cause**: Syntropy MCP not running

**Solution**:

```bash
# Restart MCP servers
/mcp

# Verify
/syntropy-health
```

## Related Commands

- `/sync-with-syntropy` - Sync tool permissions
- `/mcp` - Reconnect MCP servers (built-in)
```

### Example 3: Batch Gen PRP

**File**: `.claude/commands/batch-gen-prp.md`

```markdown
# Batch Gen PRP - Generate Multiple PRPs from Plan

Generate batch of PRPs from feature plan document with automatic dependency analysis and parallel subagent execution.

## Usage

```
/batch-gen-prp <plan-path> [--join-prp <batch-id>]
```

**Arguments**:

- `plan-path` (required): Path to plan document (markdown)
- `--join-prp <id>` (optional): Add to existing batch

## What It Does

1. **Parse plan**: Extract phases with dependencies and files
2. **Build graph**: Analyze explicit + implicit (file conflict) dependencies
3. **Assign stages**: Group independent PRPs for parallel execution
4. **Create Linear issues**: One issue per PRP
5. **Spawn subagents**: Parallel Sonnet agents generate PRPs
6. **Monitor health**: 30s heartbeat polling via temp files
7. **Collect results**: Aggregate generated PRPs

Output: PRPs in `PRPs/feature-requests/PRP-{batch}.{stage}.{order}.md`

## Examples

### Example 1: Generate from Plan

```
/batch-gen-prp FEATURE-PLAN.md
```

**Output**:

```
📋 Batch PRP Generation: FEATURE-PLAN
============================================================
Parsing plan: 4 phases identified
Assigning stages:
  Stage 1: Phase 1
  Stage 2: Phase 2, Phase 4 [parallel]
  Stage 3: Phase 3

Creating Linear issues:
  ✅ CTX-45, CTX-46, CTX-47, CTX-48

Spawning subagents (parallel):
  Stage 1: ✅ (90s)
  Stage 2: ✅ (120s, parallel)
  Stage 3: ✅ (85s)

Generated PRPs:
  PRP-43.1.1-database-schema.md
  PRP-43.2.1-jwt-tokens.md
  PRP-43.2.2-rbac.md
  PRP-43.3.1-api-endpoints.md

Total time: 295s (59% faster than sequential)
============================================================
```

### Example 2: Join Existing Batch

```
/batch-gen-prp ADDITIONAL-FEATURES.md --join-prp 43
```

Adds phases to existing Batch 43 as new stages.

## Configuration

**Linear Defaults**: `.ce/linear-defaults.yml`

```yaml
project: "Context Engineering"
team_id: "Blaise78"
assignee: "blazej.przybyszewski@gmail.com"
```

## Troubleshooting

### Issue: "Circular dependency detected"

**Cause**: Phase A depends on Phase B, which depends on Phase A

**Solution**:

```bash
# Review plan dependencies
grep "Dependencies:" PLAN.md

# Fix circular reference
vim PLAN.md
```

## Related Commands

- `/batch-exe-prp` - Execute generated PRPs
- `/execute-prp` - Execute single PRP
- `/generate-prp` - Generate single PRP
```

## Common Patterns

### Pattern 1: Workflow Command

Command that orchestrates multiple operations:

```markdown
# Deploy Workflow - Build, Test, Deploy

## Usage

```
/deploy [environment]
```

## What It Does

1. Run tests: `uv run pytest`
2. Build application: `uv run ce build`
3. Deploy to environment
4. Update deployment log
5. Notify team (Linear comment)
```

### Pattern 2: Diagnostic Command

Command that reports system status:

```markdown
# Project Health - Comprehensive Health Check

## Usage

```
/project-health
```

## What It Does

1. Git status: Check working tree
2. Context drift: Run analyze-context
3. Syntropy MCP: Check server health
4. Validation: Run L1-L4 gates
5. Display summary dashboard
```

### Pattern 3: Cleanup Command

Command that performs maintenance:

```markdown
# Sprint Cleanup - End-of-Sprint Maintenance

## Usage

```
/sprint-cleanup
```

## What It Does

1. Vacuum: Remove temp files
2. Denoise: Compress verbose docs
3. Context sync: Update PRPs
4. Git: Commit cleanup changes
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Vague "What It Does"

**Bad**:

```markdown
## What It Does

This command does stuff with PRPs.
```

**Good**:

```markdown
## What It Does

1. Parse PRP: Extract metadata
2. Validate: Check dependencies
3. Execute: Implement phases
4. Commit: Auto-commit changes
```

**Why**: Users need clear step-by-step understanding.

### ❌ Anti-Pattern 2: Missing Examples

**Bad**:

```markdown
## Examples

Use the command as needed.
```

**Good**:

```markdown
## Examples

### Example 1: Basic Usage

```
/command arg1
```

**Output**: [concrete example]
```

**Why**: Examples clarify usage patterns.

### ❌ Anti-Pattern 3: No Troubleshooting

**Bad**: No troubleshooting section

**Good**: Include common errors and solutions

**Why**: Users get stuck on predictable issues.

## Related Examples

- [hook-configuration.md](hook-configuration.md) - Configuring hooks for commands
- [../workflows/batch-prp-generation.md](../workflows/batch-prp-generation.md) - Batch generation workflow
- [../syntropy/README.md](../syntropy/README.md) - MCP tool usage in commands

## Resources

- Command Directory: `.claude/commands/`
- Template File: Copy this template to create new commands
- Claude Code Docs: https://docs.claude.com/claude-code
- Slash Command Spec: Built-in command format documentation
