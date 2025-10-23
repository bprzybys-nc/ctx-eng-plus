# INITIAL: Syntropy Documentation Migration & Init Foundation

**Feature:** Move Context Engineering framework documentation to Syntropy and implement project initialization with slash command upsert.

**Prerequisites:** None (foundational PRP - implements base functionality for PRP-29.2 and PRP-29.3)

**Dependencies:** PRP-29.2 and PRP-29.3 require this PRP to be completed first.

---

## FEATURE

Syntropy ships with CE framework documentation and provides automated project scaffolding with slash command management.

**Repository Context:**
- **Syntropy MCP:** `~/syntropy-mcp` (separate repository, MCP server aggregator)
- **ctx-eng-plus:** Current project (Context Engineering reference implementation)
- **Relationship:** Syntropy provides framework tooling, ctx-eng-plus uses it as a project

**Goals:**
1. Move framework docs from ctx-eng-plus to syntropy-mcp (research/, templates/, docs/)
2. Move slash command definitions to syntropy-mcp/commands/
3. Implement `syntropy_init_project` tool for project scaffolding
4. Auto-upsert slash commands on init (ALWAYS overwrite to keep in sync)
5. Detect project structure (root-level vs context-engineering/ subdirectory)
6. Activate Serena project on init for code navigation
7. Clean up ctx-eng-plus (delete duplicate docs)

**Current Problems:**
- CE framework docs duplicated in every project
- No standardized project initialization
- Slash commands manually maintained per project
- No automatic framework updates

**Expected Outcome:**
- Framework docs live in `syntropy-mcp/docs/` (single source of truth)
- Slash commands auto-installed: `/generate-prp`, `/execute-prp`, `/update-context`
- `syntropy_init_project` creates: PRPs/, examples/, .serena/, CLAUDE.md, .claude/commands/
- Supports both layouts: root-level OR context-engineering/ subdirectory
- ⚠️ Slash commands ALWAYS overwritten on init (user customizations lost)

---

## EXAMPLES

### Example 1: Documentation Structure in Syntropy

**Target Structure:**
```
syntropy-mcp/
├── docs/
│   ├── research/           # 00-11 documentation suite
│   │   ├── 00-prp-overview.md
│   │   ├── 01-prp-system.md
│   │   └── ...
│   ├── templates/          # PRP templates
│   │   ├── self-healing.md
│   │   └── kiss.md
│   └── *.md               # Top-level docs (prp-yaml-schema.md, etc.)
└── commands/              # Slash command definitions
    ├── generate-prp.md
    ├── execute-prp.md
    └── update-context.md
```

**Migration:**
```bash
# Move from ctx-eng-plus to syntropy-mcp
mv ctx-eng-plus/docs/research/* → syntropy-mcp/docs/research/
mv ctx-eng-plus/PRPs/templates/* → syntropy-mcp/docs/templates/
mv ctx-eng-plus/docs/*.md → syntropy-mcp/docs/
mv ctx-eng-plus/.claude/commands/*.md → syntropy-mcp/commands/

# Clean up ctx-eng-plus
rm -rf ctx-eng-plus/docs/
rm -rf ctx-eng-plus/PRPs/templates/
```

### Example 2: Project Structure Detection

**Location:** `syntropy-mcp/src/scanner.ts`

```typescript
interface ProjectLayout {
  prpsDir: string;        // "PRPs" or "context-engineering/PRPs"
  examplesDir: string;    // "examples" or "context-engineering/examples"
  memoriesDir: string;    // Always ".serena/memories"
  claudeMd: string;       // "CLAUDE.md" location
  commandsDir: string;    // Always ".claude/commands"
  layout: "root" | "context-engineering";
}

function detectProjectLayout(projectRoot: string): ProjectLayout {
  // Check for context-engineering subdirectory
  const ceDir = path.join(projectRoot, "context-engineering");
  const hasContextEngineering = fs.existsSync(ceDir);

  if (hasContextEngineering) {
    return {
      prpsDir: "context-engineering/PRPs",
      examplesDir: "context-engineering/examples",
      memoriesDir: ".serena/memories",
      claudeMd: findCLAUDEmd(projectRoot),  // Search root first, then subdirs
      commandsDir: ".claude/commands",
      layout: "context-engineering"
    };
  }

  return {
    prpsDir: "PRPs",
    examplesDir: "examples",
    memoriesDir: ".serena/memories",
    claudeMd: findCLAUDEmd(projectRoot),
    commandsDir: ".claude/commands",
    layout: "root"
  };
}
```

**Pattern:** Support both layouts, always check `.serena/memories/` and `.claude/commands/` at root.

### Example 3: Slash Command Upsert

**Location:** `syntropy-mcp/src/tools/init.ts`

```typescript
async function upsertSlashCommands(projectRoot: string): Promise<void> {
  const commandsDir = path.join(projectRoot, ".claude/commands");
  const syntropyCmds = path.join(__dirname, "../../commands");

  // Ensure directory exists
  await fs.mkdir(commandsDir, { recursive: true });

  const commands = ["generate-prp.md", "execute-prp.md", "update-context.md"];

  for (const cmd of commands) {
    const src = path.join(syntropyCmds, cmd);
    const dst = path.join(commandsDir, cmd);

    // Check if file exists
    const exists = await fs.access(dst).then(() => true).catch(() => false);

    if (exists) {
      console.log(`⚠️  Overwriting existing: /${cmd.replace('.md', '')}`);
    }

    // ALWAYS copy (overwrite if exists) to keep commands in sync
    await fs.copyFile(src, dst);
    console.log(`✅ Upserted slash command: /${cmd.replace('.md', '')}`);
  }

  console.log("");
  console.log("⚠️  IMPORTANT: Slash commands are ALWAYS overwritten on init.");
  console.log("   To customize commands, create new files with different names.");
  console.log("   Examples: my-generate-prp.md, custom-update-context.md");
}
```

**Pattern:** Always overwrite, warn user clearly, suggest alternative for customization.

### Example 4: Init Tool Implementation

**Location:** `syntropy-mcp/src/tools/init.ts`

```typescript
interface InitProjectArgs {
  project_root: string;
}

export async function initProject(args: InitProjectArgs): Promise<object> {
  const projectRoot = path.resolve(args.project_root);

  try {
    // 1. Detect existing layout
    const layout = detectProjectLayout(projectRoot);
    console.log(`✅ Detected layout: ${layout.layout}`);

    // 2. Create missing directories
    await scaffoldStructure(projectRoot, layout);

    // 3. Upsert slash commands (ALWAYS overwrite)
    await upsertSlashCommands(projectRoot);

    // 4. Activate Serena project
    await activateSerenaProject(projectRoot);

    return {
      success: true,
      layout: layout.layout,
      message: "Project initialized successfully"
    };
  } catch (error) {
    throw new Error(
      `Failed to initialize project: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure directory is writable and not in use`
    );
  }
}

async function scaffoldStructure(projectRoot: string, layout: ProjectLayout): Promise<void> {
  const dirs = [
    path.join(projectRoot, layout.prpsDir, "feature-requests"),
    path.join(projectRoot, layout.prpsDir, "executed"),
    path.join(projectRoot, layout.examplesDir),
    path.join(projectRoot, layout.memoriesDir),
    path.join(projectRoot, ".ce"),
  ];

  for (const dir of dirs) {
    await fs.mkdir(dir, { recursive: true });
    console.log(`✅ Created: ${path.relative(projectRoot, dir)}`);
  }

  // Create CLAUDE.md if missing
  const claudeMd = path.join(projectRoot, "CLAUDE.md");
  if (!await fs.access(claudeMd).then(() => true).catch(() => false)) {
    await fs.writeFile(claudeMd, "# Project Guide\n\nAdd project-specific instructions here.\n");
    console.log(`✅ Created: CLAUDE.md`);
  }
}

async function activateSerenaProject(projectRoot: string): Promise<void> {
  // Call Serena MCP via Syntropy client manager
  try {
    const clientManager = await getClientManager();
    const serenaClient = clientManager.getClient("serena");

    await serenaClient.callTool("serena_activate_project", {
      project: projectRoot
    });

    console.log(`✅ Activated Serena project: ${path.basename(projectRoot)}`);
  } catch (error) {
    // Non-fatal: Serena activation is optional for init
    console.warn(`⚠️  Serena activation failed (non-fatal): ${error.message}`);
    console.warn(`   Code navigation features may be limited.`);
  }
}
```

**Pattern:** Fast failure, clear progress output, actionable errors, activate Serena for code navigation.

---

## DOCUMENTATION

### MCP SDK Documentation
- Tool definitions: https://modelcontextprotocol.io/docs/tools/building-tools
- Transport: stdio for Claude Code integration
- `inputSchema` required (JSON Schema)

### TypeScript/Node.js
- File system: `fs/promises` for async operations
- Path handling: `path.join()`, `path.resolve()`
- Copy files: `fs.copyFile()`
- Check existence: `fs.access()`

### Syntropy Architecture
- **Tool definition:** `syntropy-mcp/src/tools-definition.ts`
- **Client manager:** `syntropy-mcp/src/client-manager.ts`
- **Main server:** `syntropy-mcp/src/index.ts`

### Framework Docs to Move
```
ctx-eng-plus/docs/research/*.md → syntropy-mcp/docs/research/
ctx-eng-plus/PRPs/templates/*.md → syntropy-mcp/docs/templates/
ctx-eng-plus/docs/*.md → syntropy-mcp/docs/
ctx-eng-plus/.claude/commands/*.md → syntropy-mcp/commands/
```

---

## OTHER CONSIDERATIONS

### Tool Naming
- MCP tool: `syntropy_init_project` (callable as `mcp__syntropy_init_project`)
- Slash command: `/init-context-engineering` (delegates to MCP tool)

### Backward Compatibility
- Existing projects work with init (detect existing structure, don't break)
- Support both layouts: root-level and context-engineering/ subdirectory
- No breaking changes to existing MCP tools

### Error Handling
- Clear progress messages (✅ Created, ⚠️ Overwriting)
- Fast failure with 🔧 troubleshooting guidance
- No fishy fallbacks - actionable errors only

### Migration Steps
1. Create `syntropy-mcp/docs/` structure
2. Move files from ctx-eng-plus to syntropy-mcp
3. Delete duplicates from ctx-eng-plus
4. Update ctx-eng-plus/CLAUDE.md references
5. Implement init tool in Syntropy
6. Test with 3 scenarios:
   - Fresh project (init from scratch)
   - Existing root-level (ctx-eng-plus)
   - Existing context-engineering/ subdirectory

### User Communication
**On init, display warning:**
```
⚠️  IMPORTANT: Slash commands are ALWAYS overwritten on init.
   To customize commands, create new files with different names.
   Examples: my-generate-prp.md, custom-update-context.md
```

### Testing Strategy
- **Unit:** Structure detection, directory creation, file copying
- **Integration:** Full init workflow on fresh + existing projects
- **E2E:** Test with both layouts (root + context-engineering/)

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
cd syntropy-mcp && npm run build
```

### Level 2: Unit Tests
```bash
cd syntropy-mcp && npm test src/scanner.test.ts
cd syntropy-mcp && npm test src/tools/init.test.ts
```

**Specific Test Scenarios:**
- `test_detectProjectLayout_root`: Verify detection of root-level layout
- `test_detectProjectLayout_subdir`: Verify detection of context-engineering/ subdirectory
- `test_detectProjectLayout_mixed`: Handle projects with both structures
- `test_upsertSlashCommands_fresh`: Create commands in empty .claude/commands/
- `test_upsertSlashCommands_overwrite`: Overwrite existing commands with warning
- `test_scaffoldStructure_fresh`: Create all directories from scratch
- `test_scaffoldStructure_existing`: Preserve existing directories and files
- `test_activateSerena_success`: Activate Serena project successfully
- `test_activateSerena_failure`: Gracefully handle Serena unavailable (non-fatal)

### Level 3: Integration Tests
```bash
# Test fresh project
syntropy_init_project /tmp/test-fresh
ls -la /tmp/test-fresh/.claude/commands/  # Should have 3 slash commands

# Test existing project
syntropy_init_project /path/to/existing-project
# Should detect layout, not break existing files

# Verify cleanup (after migration)
test ! -d ctx-eng-plus/docs/research && echo "✅ Research docs cleaned up" || echo "❌ Research docs still present"
test ! -d ctx-eng-plus/PRPs/templates && echo "✅ Templates cleaned up" || echo "❌ Templates still present"
test ! -f ctx-eng-plus/.claude/commands/generate-prp.md && echo "✅ Commands cleaned up" || echo "❌ Commands still present"

# Verify migration (docs now in Syntropy)
test -d syntropy-mcp/docs/research && echo "✅ Research docs migrated" || echo "❌ Research docs missing"
test -d syntropy-mcp/docs/templates && echo "✅ Templates migrated" || echo "❌ Templates missing"
test -f syntropy-mcp/commands/generate-prp.md && echo "✅ Commands migrated" || echo "❌ Commands missing"
```

### Level 4: Pattern Conformance
- Tool naming: `syntropy_init_project` (correct format)
- Error handling: Fast failure, 🔧 troubleshooting
- No fishy fallbacks
- Clear user communication (overwrite warnings)

---

## SUCCESS CRITERIA

1. ⬜ Framework docs moved to `syntropy-mcp/docs/` (research, templates, docs)
2. ⬜ Slash commands moved to `syntropy-mcp/commands/`
3. ⬜ Duplicates deleted from ctx-eng-plus
4. ⬜ `syntropy_init_project` tool implemented
5. ⬜ Init creates: PRPs/, examples/, .serena/, CLAUDE.md, .claude/commands/
6. ⬜ Slash commands auto-installed: /generate-prp, /execute-prp, /update-context
7. ⬜ Overwrite warning displayed clearly
8. ⬜ Works with both layouts (root + context-engineering/)
9. ⬜ Serena project activated on init
10. ⬜ All tests passing (unit + integration)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Medium (3-4 days)
- Documentation migration: 0.5 day
- Structure detection: 0.5 day
- Init tool implementation: 1-2 days
- Slash command upsert: 0.5 day
- Testing: 0.5-1 day

**Risk Level:** Low
- File operations (well-understood)
- No breaking changes (detect existing structure)
- Clear migration path

**Dependencies:**
- Syntropy MCP server (existing)
- Serena MCP (existing, for activation)

**Files to Create:**
- `syntropy-mcp/docs/research/*` (moved from ctx-eng-plus)
- `syntropy-mcp/docs/templates/*` (moved from ctx-eng-plus)
- `syntropy-mcp/docs/*.md` (moved from ctx-eng-plus)
- `syntropy-mcp/commands/*.md` (moved from ctx-eng-plus)
- `syntropy-mcp/src/scanner.ts`
- `syntropy-mcp/src/tools/init.ts`
- `syntropy-mcp/src/tools-definition.ts` (update with init tool)

**Files to Modify:**
- `ctx-eng-plus/CLAUDE.md` (update doc references)

**Files to Delete:**
- `ctx-eng-plus/docs/` (entire directory)
- `ctx-eng-plus/PRPs/templates/` (moved to syntropy-mcp)
