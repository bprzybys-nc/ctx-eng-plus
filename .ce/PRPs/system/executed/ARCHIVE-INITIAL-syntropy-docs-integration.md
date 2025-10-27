# INITIAL: Syntropy Documentation Integration

**Feature:** Integrate Context Engineering framework documentation into Syntropy MCP server with unified knowledge management and context sync capabilities.

---

## FEATURE

Syntropy becomes the single source of truth for Context Engineering framework documentation, providing it to any project via MCP tools while preserving git-based project-specific knowledge.

**Goals:**
1. Ship CE framework docs with Syntropy (research/, templates/)
2. Auto-scaffold project structure on init (PRPs/, examples/, .serena/, CLAUDE.md, .claude/commands/)
3. Upsert slash commands on init (generate-prp.md, execute-prp.md, update-context.md)
4. Scan existing project knowledge (PRPs, examples, Serena memories) on init
5. Provide unified query interface across all knowledge sources
6. Implement context sync tool that replaces `ce update-context`
7. Support flexible project layouts (root-level OR context-engineering/ subdirectory)

**Current Problems:**
- CE framework docs duplicated in every project
- No standardized project initialization
- Manual context sync is complex (multiple tools: ce + Serena + drift detection)
- Knowledge scattered (files + Serena memories + framework docs)
- No unified query interface

**Expected Outcome:**
- MCP tool for init: `syntropy_init_project` (works with `/init-context-engineering` slash command)
- ⚠️ **CRITICAL**: Slash commands auto-installed and **ALWAYS overwritten** on init:
  - `/generate-prp`, `/execute-prp`, `/update-context`
  - **User customizations LOST** - create custom commands with different names
- Framework docs accessed via: `get_framework_doc('research/01-prp-system')`
- Unified search: `knowledge_search(query)` → searches PRPs, examples, memories, rules
- Context sync tool: `syntropy_sync_context` (can replace `ce update-context`)
- Zero documentation duplication across projects

---

## EXAMPLES

### Example 1: Tool Naming Convention

**Location:** `syntropy-mcp/src/tools-definition.ts`

```typescript
// ✅ CORRECT - Syntropy tool definition format
{
  name: "syntropy_serena_find_symbol",
  description: "Find code symbols by name path",
  inputSchema: { /* ... */ }
}

// ✅ CORRECT - Healthcheck tool
{
  name: "syntropy_healthcheck",
  description: "Check health of Syntropy servers",
  inputSchema: { /* ... */ }
}
```

**Pattern:** Tools defined as `server_tool` format. Claude Code transforms to `mcp__syntropy__server_tool` (double underscore).

**Examples from permissions file:**
- Tool defined: `serena_find_symbol` → Claude Code: `mcp__syntropy__serena_find_symbol`
- Tool defined: `github_create_issue` → Claude Code: `mcp__syntropy__github_create_issue`
- Tool defined: `healthcheck` → Claude Code: `mcp__syntropy__healthcheck`

**CRITICAL**: Parser handles BOTH double and single underscore for backwards compatibility

### Example 2: MCP Client Manager Pattern

**Location:** `syntropy-mcp/src/client-manager.ts`

```typescript
export class MCPClientManager {
  private clients: Map<string, MCPClient> = new Map();
  private config: ServerConfig;

  async callTool(serverKey: string, toolName: string, args: Record<string, unknown>) {
    const client = await this.getClient(serverKey);
    return await client.callTool(toolName, args);
  }

  async closeAll() {
    for (const [key, client] of this.clients.entries()) {
      await client.close();
    }
  }
}
```

**Pattern:** Connection pooling with lazy initialization and graceful cleanup.

### Example 3: Project Structure Detection & Slash Command Upsert

**Required Logic:**

```python
# Detect existing structure
def detect_project_layout(project_root: Path) -> dict:
    """Scan for existing knowledge directories."""
    return {
        "prps": find_dirs(project_root, "PRPs"),      # Can be root or subdirs
        "examples": find_dirs(project_root, "examples"),
        "memories": project_root / ".serena/memories",  # Always this location
        "claude_md": find_file(project_root, "CLAUDE.md"),
        "claude_commands": project_root / ".claude/commands",
        "layout": "context-engineering" if (project_root / "context-engineering").exists() else "root"
    }

# Scan existing knowledge
def scan_knowledge(paths: dict) -> dict:
    """Index all found PRPs, examples, memories."""
    index = {}
    for prp_dir in paths["prps"]:
        index.update(scan_prps(prp_dir))
    for example_dir in paths["examples"]:
        index.update(scan_examples(example_dir))
    # etc...
    return index

# Upsert slash commands (create or update)
def upsert_slash_commands(project_root: Path, syntropy_commands: Path) -> None:
    """Install/update slash commands from Syntropy to project.

    IMPORTANT: ALWAYS overwrites existing commands to keep in sync with framework.
    """
    commands_dir = project_root / ".claude/commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    # Copy commands from Syntropy bundle
    for cmd in ["generate-prp.md", "execute-prp.md", "update-context.md"]:
        src = syntropy_commands / cmd
        dst = commands_dir / cmd

        # ALWAYS overwrite (even if exists) to keep commands up-to-date with framework
        if dst.exists():
            print(f"⚠️  Overwriting existing: /{cmd.replace('.md', '')}")

        shutil.copy2(src, dst)
        print(f"✅ Upserted slash command: /{cmd.replace('.md', '')}")

# Activate Serena project for code analysis
def activate_serena_project(project_root: Path) -> None:
    """Activate Serena MCP on target project for code navigation."""
    # Call via MCP: mcp__syntropy_serena_activate_project
    result = mcp_client.call("syntropy_serena_activate_project", {"project": str(project_root)})
    print(f"✅ Activated Serena project: {project_root.name}")
```

**Pattern:** Flexible directory discovery, always check `.serena/memories/`, support both layouts, auto-install slash commands, activate Serena.

### Example 4: Unified Index Schema

**Location:** `.ce/syntropy-index.json`

```json
{
  "version": "1.0",
  "project_root": "/path/to/project",
  "synced_at": "2025-10-21T10:00:00Z",
  "framework_version": "1.0",

  "paths": {
    "prps": ["PRPs", "context-engineering/PRPs"],
    "examples": ["examples"],
    "memories": [".serena/memories"],
    "claude_md": "CLAUDE.md"
  },

  "knowledge": {
    "patterns": {
      "api-error-handling": {
        "source": "examples/patterns/api-error.md",
        "tags": ["api", "error"],
        "referenced_by": ["PRP-15"]
      }
    },
    "prp_learnings": {
      "PRP-15": {
        "source": "PRPs/executed/PRP-15.md",
        "implementations": ["drift_analyzer.py"],
        "verified": true
      }
    },
    "memories": {
      "tool-usage-guide": {
        "source": ".serena/memories/tool-usage-guide.md",
        "tags": ["tools", "mcp"]
      }
    }
  },

  "drift": {
    "score": 0.05,
    "violations": []
  }
}
```

**Pattern:** Single index file, tracks all knowledge sources, includes drift tracking.

---

## DOCUMENTATION

### MCP SDK Documentation
- MCP Server SDK: https://modelcontextprotocol.io/docs/tools/building-tools
- Tool definitions require `inputSchema` (JSON Schema)
- Transport: stdio for Claude Code integration

### TypeScript/Node.js
- File system: `fs/promises` for async operations
- Path handling: `path.join()`, `path.resolve()`
- JSON parsing: `JSON.parse()`, `JSON.stringify()`
- Glob patterns: Use `glob` package for file discovery

### Python Integration
- `ce update-context` delegates to `syntropy sync`
- Use `subprocess.run()` with `shlex.split()` (CWE-78 safe)
- JSON output for automation: `--json` flag

### Existing Syntropy Architecture
- **Location:** `syntropy-mcp/src/index.ts` - Main server
- **Client Manager:** `syntropy-mcp/src/client-manager.ts` - Connection pooling
- **Tools Definition:** `syntropy-mcp/src/tools-definition.ts` - Tool schemas
- **Health Checker:** `syntropy-mcp/src/health-checker.ts` - Server monitoring

### Framework Docs to Ship with Syntropy

**Files to Move:**
```
ctx-eng-plus/docs/research/*.md → syntropy-mcp/docs/research/
ctx-eng-plus/PRPs/templates/*.md → syntropy-mcp/docs/templates/
ctx-eng-plus/docs/*.md → syntropy-mcp/docs/
ctx-eng-plus/.claude/commands/*.md → syntropy-mcp/commands/
```

**Documentation Structure in Syntropy:**
- `syntropy-mcp/docs/research/` - Complete documentation suite (00-11)
- `syntropy-mcp/docs/templates/` - PRP templates (self-healing.md, kiss.md)
- `syntropy-mcp/docs/*.md` - Top-level docs (prp-yaml-schema.md, etc.)
- `syntropy-mcp/commands/` - Slash commands (generate-prp.md, execute-prp.md, update-context.md)

**Note:** SystemModel.md not needed - documentation suite in research/ is sufficient

---

## OTHER CONSIDERATIONS

### Init Command Architecture

**Two Components:**
1. **MCP Tool**: `syntropy_init_project(project_root)` - Low-level implementation
2. **Slash Command**: `/init-context-engineering` - User-facing wrapper

**Relationship:**
- Slash command delegates to MCP tool via Claude Code
- MCP tool performs: scaffold structure, upsert commands, activate Serena project, scan knowledge, create index
- Slash command provides: user prompts, output formatting, progress updates

**Why Both:**
- MCP tool: Programmatic access for automation/CI/CD
- Slash command: Interactive mode with user guidance
- Single implementation, two interfaces

### Backward Compatibility
- Tool naming: Current `syntropy_server_tool` format is correct (Claude Code adds `mcp__` prefix)
- Existing projects must work with `syntropy init --existing`
- Support both layouts: root-level PRPs/ OR context-engineering/PRPs/
- Don't break current MCP tool calls (all 67 tools remain callable)

### Performance
- Lazy initialization for non-critical servers (Context7, Repomix)
- Cache index in `.ce/syntropy-index.json` (5-min TTL)
- Incremental reindexing (only changed files)
- Avoid full directory scans on every query

### Security
- No secret exposure in index files
- Validate all file paths (prevent directory traversal)
- Use `shlex.split()` for subprocess calls (CWE-78 safe)
- Sanitize user input in queries

### Error Handling
- Graceful degradation if Serena MCP unavailable
- Clear troubleshooting messages (🔧 format)
- No fishy fallbacks - fail fast with actionable errors
- Log errors to stderr for debugging
- **Slash command overwrites:** Warn user with clear message when overwriting existing commands

### Migration Path

**Phase 1: Restructure ctx-eng-plus (1 day)**
1. Move framework docs to Syntropy:
   - `docs/research/` → `syntropy-mcp/docs/research/`
   - `PRPs/templates/` → `syntropy-mcp/docs/templates/`
   - `docs/*.md` → `syntropy-mcp/docs/`
   - `.claude/commands/*.md` → `syntropy-mcp/commands/`
2. Delete duplicates from ctx-eng-plus:
   - `rm -rf docs/`
   - `rm -rf PRPs/templates/`
3. Update CLAUDE.md references:
   - Change "docs/research/" → "framework docs via Syntropy MCP"
   - Document new tool usage patterns

**Phase 2:** Implement init tool (create structure + scan existing)
**Phase 3:** Implement query tools (framework docs + project knowledge)
**Phase 4:** Implement sync tool (replace ce update-context)
**Phase 5:** Update ce CLI to delegate to Syntropy

### Testing Strategy
- **Unit:** Scanner, indexer, tool routing
- **Integration:** Init workflow, query tools, sync tool
- **E2E:** Full workflow on 3 project structures:
  1. Fresh project (init from scratch)
  2. Existing root-level layout (ctx-eng-plus)
  3. Existing context-engineering/ layout (certinia)

### Configuration Files
- **`.ce/syntropy-index.json`** - Unified knowledge index
- **`syntropy-mcp/docs/`** - Framework documentation
- **`syntropy-mcp/commands/`** - Slash command definitions
- **`syntropy-mcp/servers.json`** - MCP server configuration
- **`.serena/memories/`** - Project-specific learnings (always)
- **`.claude/commands/`** - Project slash commands (upserted from Syntropy)

### Gotchas
1. **Tool naming:** Current format `syntropy_server_tool` is CORRECT (don't change to `server_tool`)
2. **Layout detection:** Support BOTH root-level and context-engineering/ subdirs
3. **Serena memories:** ALWAYS at `.serena/memories/`, never elsewhere
4. **CLAUDE.md location:** Search root first, then subdirectories
5. **Framework docs:** Ship with Syntropy, DON'T copy to projects
6. **Index cache:** 5-minute TTL to avoid stale data
7. **Reindexing:** Trigger on file changes, PRP completion, manual sync
8. **Init command:** MCP tool `syntropy_init_project` works alongside existing `/init-context-engineering` slash command
9. **Slash commands:** ALWAYS overwrite existing commands on init (keeps framework in sync, no merge conflicts)
10. **Command location:** `.claude/commands/` at project root (not in context-engineering/ subdirs)
11. **User customizations:** If users modify slash commands, changes will be lost on next init (document this clearly)

### Dependencies
- **Syntropy:** `@modelcontextprotocol/sdk`, `glob` package
- **Python:** No new deps (use existing `ce` package)
- **Node.js:** fs/promises, path (stdlib only)

### Constraints
- **Offline-first:** Index cached locally, works without network
- **Zero duplication:** Framework docs in Syntropy only
- **Git-based:** Project knowledge stays in version control
- **MCP standard:** Follow MCP protocol for tool definitions

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
# TypeScript compilation
cd syntropy-mcp && npm run build

# Python type checking
cd tools && uv run mypy ce/
```

### Level 2: Unit Tests
```bash
# Test scanner logic
cd syntropy-mcp && npm test src/scanner.test.ts

# Test indexer
cd syntropy-mcp && npm test src/indexer.test.ts

# Test Python delegation
cd tools && uv run pytest tests/test_syntropy_integration.py
```

### Level 3: Integration Tests
```bash
# Test init workflow
syntropy init /tmp/test-project
ls -la /tmp/test-project  # Should have PRPs/, examples/, .serena/, CLAUDE.md

# Test knowledge query
syntropy knowledge_search "error handling"

# Test sync
syntropy sync /tmp/test-project --json
```

### Level 4: Pattern Conformance
- Tool naming: `syntropy_server_tool` format (current implementation correct)
- Error handling: Fast failure with 🔧 troubleshooting
- No fishy fallbacks: All errors actionable
- UV package management: Use `uv add`, never edit pyproject.toml
- Real functionality: No mocks in production code

---

## SUCCESS CRITERIA

1. ✅ Tool naming verified (current `syntropy_server_tool` format is correct)
2. ⬜ Init command creates standard structure + upserts slash commands
3. ⬜ Slash commands installed: `/generate-prp`, `/execute-prp`, `/update-context`
4. ⬜ Framework docs accessible via `get_framework_doc()`
5. ⬜ Unified search across PRPs, examples, memories, rules
6. ⬜ Context sync replaces `ce update-context`
7. ⬜ Works with both project layouts (root + context-engineering/)
8. ⬜ Zero breaking changes to existing projects
9. ⬜ All tests passing (unit + integration + E2E)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Large (10-14 days)
- Phase 1 (Restructure): 1 day
- Phase 2 (Init tool): 2-3 days
- Phase 3 (Query tools): 3-4 days
- Phase 4 (Sync tool): 2-3 days
- Phase 5 (Integration): 2 days
- Testing: 2-3 days

**Risk Level:** Medium
- Tool naming verified as correct (`syntropy_server_tool` format)
- Migration of framework docs from ctx-eng-plus to syntropy-mcp
- Backward compatibility with existing projects (no breaking changes expected)

**Dependencies:**
- Syntropy MCP server (existing)
- Serena MCP (existing)
- ce CLI tools (existing)

**Files to Create:**
- `syntropy-mcp/src/tools/init.ts` - MCP tool: syntropy_init_project (includes slash command upsert)
- `syntropy-mcp/src/tools/knowledge.ts` - MCP tools: get_framework_doc, knowledge_search, etc.
- `syntropy-mcp/src/tools/sync.ts` - MCP tool: syntropy_sync_context
- `syntropy-mcp/src/scanner.ts` - Project structure scanner
- `syntropy-mcp/src/indexer.ts` - Knowledge indexer
- `syntropy-mcp/docs/` - Framework docs (moved from ctx-eng-plus/docs/)
  - `syntropy-mcp/docs/research/` (from ctx-eng-plus/docs/research/)
  - `syntropy-mcp/docs/templates/` (from ctx-eng-plus/PRPs/templates/)
- `syntropy-mcp/commands/` - Slash command definitions (moved from ctx-eng-plus/.claude/commands/)
  - `syntropy-mcp/commands/generate-prp.md`
  - `syntropy-mcp/commands/execute-prp.md`
  - `syntropy-mcp/commands/update-context.md`

**Files to Modify:**
- `tools/ce/update_context.py` (delegate to syntropy sync)
- `tools/ce/core.py` (add Syntropy helpers)
- `CLAUDE.md` (document new commands)

**Files to Delete:**
- `ctx-eng-plus/docs/` (moved to syntropy-mcp/docs/)
- `ctx-eng-plus/PRPs/templates/` (moved to syntropy-mcp/docs/templates/)
- `ctx-eng-plus/context-engineering/` (deprecated layout, if exists)

**Files to Keep (Auto-Updated by Syntropy):**
- `ctx-eng-plus/.claude/commands/` - Slash commands (auto-updated from syntropy-mcp/commands/)
  - **IMPORTANT:** These files are ALWAYS overwritten on `syntropy init`
  - **User modifications will be LOST** - document clearly in init output
  - **Rationale:** Ensures all projects use latest framework commands
  - **Alternative:** Users can create custom commands with different names (e.g., `my-generate-prp.md`)
