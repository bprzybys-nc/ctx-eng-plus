# INITIAL: Syntropy Documentation Migration & Init Foundation

**Feature:** Copy CE framework boilerplate from syntropy/ce/ to project .ce/ directory and implement automated project initialization.

**Prerequisites:** None (foundational PRP - implements base functionality for PRP-29.2 and PRP-29.3)

**Dependencies:** PRP-29.2 and PRP-29.3 require this PRP to be completed first.

---

## FEATURE

Syntropy provides automated project scaffolding by copying CE framework boilerplate from `syntropy/ce/` to project `.ce/` directory, with slash command upsert and Serena activation.

**Repository Context:**
- **ctx-eng-plus:** Contains `syntropy/ce/` boilerplate (static copy-paste content)
- **Target Projects:** Any project using Context Engineering framework
- **Relationship:** ctx-eng-plus provides reference boilerplate, projects copy to `.ce/`

**Goals:**
1. Copy `syntropy/ce/` boilerplate to project `.ce/` directory
2. Structure includes: `.ce/PRPs/system/`, `.ce/examples/system/`, `.ce/tools/`
3. Implement `syntropy_init_project` tool for project scaffolding
4. Auto-upsert slash commands on init (ALWAYS overwrite to keep in sync)
5. Keep user PRPs/ and examples/ at root (separate from system)
6. Activate Serena project on init for code navigation
7. Support self-contained, auto-healing workflow

**Current Problems:**
- CE framework content scattered across projects
- No standardized project initialization
- Slash commands manually maintained per project
- No automatic framework updates
- System PRPs mixed with user PRPs

**Expected Outcome:**
- Framework boilerplate in `.ce/` (copied from syntropy/ce/)
- Slash commands auto-installed: `/generate-prp`, `/execute-prp`, `/update-context`
- `syntropy_init_project` creates: `.ce/PRPs/system/`, `.ce/examples/system/`, `.ce/tools/`
- User content stays at root: `PRPs/`, `examples/`, `CLAUDE.md`
- ⚠️ Slash commands ALWAYS overwritten on init (user customizations lost)
- Self-contained workflow with RULES.md embedded

---

## EXAMPLES

### Example 1: Boilerplate Structure in syntropy/ce/

**Source Structure (ctx-eng-plus):**
```
syntropy/ce/                  # Static boilerplate
├── PRPs/                     # System PRPs
│   ├── executed/             # PRP-1-28
│   └── templates/            # self-healing.md, kiss.md
├── examples/                 # System examples
│   ├── model/                # SystemModel.md
│   └── patterns/             # Code patterns
├── serena/                   # Empty (for project-specific memories)
├── tools/                    # CE CLI tooling
│   ├── ce/                   # Python package
│   ├── tests/                # Test suite
│   └── pyproject.toml        # UV config
├── RULES.md                  # Distilled CE rules
└── README.md                 # Boilerplate guide
```

**Target Structure (after init):**
```
my-project/
├── .ce/                      # System (copied from syntropy/ce/)
│   ├── PRPs/system/
│   ├── examples/system/
│   ├── tools/
│   └── config.yml
├── PRPs/                     # User project PRPs
│   ├── feature-requests/
│   └── executed/
├── examples/                 # User project examples
├── .serena/memories/         # Serena knowledge
└── .claude/commands/         # Slash commands (auto-upserted)
```

### Example 2: Project Structure Detection

**Location:** `syntropy-mcp/src/scanner.ts`

```typescript
interface ProjectLayout {
  ceDir: string;            // ".ce" (system content)
  prpsDir: string;          // "PRPs" (user content)
  examplesDir: string;      // "examples" (user content)
  memoriesDir: string;      // ".serena/memories"
  claudeMd: string;         // "CLAUDE.md" location
  commandsDir: string;      // ".claude/commands"
}

function detectProjectLayout(projectRoot: string): ProjectLayout {
  // Standard layout: .ce/ for system, root for user
  return {
    ceDir: ".ce",                      // System content
    prpsDir: "PRPs",                   // User PRPs
    examplesDir: "examples",           // User examples
    memoriesDir: ".serena/memories",   // Serena knowledge
    claudeMd: findCLAUDEmd(projectRoot),
    commandsDir: ".claude/commands"    // Slash commands
  };
}

function findCLAUDEmd(projectRoot: string): string {
  // Check root first, then subdirectories
  const rootClaude = path.join(projectRoot, "CLAUDE.md");
  if (fs.existsSync(rootClaude)) return "CLAUDE.md";

  // Default location
  return "CLAUDE.md";
}
```

**Pattern:** Simple layout with `.ce/` for system, root for user content.

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
    console.log(`✅ Detected standard layout`);

    // 2. Copy syntropy/ce/ boilerplate to .ce/
    await copyBoilerplate(projectRoot, layout);

    // 3. Create user directories (PRPs/, examples/)
    await scaffoldUserStructure(projectRoot, layout);

    // 4. Upsert slash commands (ALWAYS overwrite)
    await upsertSlashCommands(projectRoot);

    // 5. Activate Serena project
    await activateSerenaProject(projectRoot);

    return {
      success: true,
      message: "Project initialized successfully",
      structure: ".ce/ (system) + PRPs/examples/ (user)"
    };
  } catch (error) {
    throw new Error(
      `Failed to initialize project: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure directory is writable and syntropy/ce/ exists`
    );
  }
}

async function copyBoilerplate(projectRoot: string, layout: ProjectLayout): Promise<void> {
  // Find syntropy/ce/ boilerplate (in ctx-eng-plus or specified path)
  const boilerplatePath = path.join(__dirname, "../../syntropy/ce");
  const targetCeDir = path.join(projectRoot, layout.ceDir);

  // Copy entire syntropy/ce/ to .ce/
  await fs.cp(boilerplatePath, targetCeDir, { recursive: true });
  console.log(`✅ Copied boilerplate to ${layout.ceDir}/`);
  console.log(`   - PRPs/system/ (PRP-1-28 + templates)`);
  console.log(`   - examples/system/ (model, patterns)`);
  console.log(`   - tools/ (CE CLI)`);
  console.log(`   - RULES.md (framework rules)`);
}

async function scaffoldUserStructure(projectRoot: string, layout: ProjectLayout): Promise<void> {
  const dirs = [
    path.join(projectRoot, layout.prpsDir, "feature-requests"),
    path.join(projectRoot, layout.prpsDir, "executed"),
    path.join(projectRoot, layout.examplesDir),
    path.join(projectRoot, layout.memoriesDir),
  ];

  for (const dir of dirs) {
    await fs.mkdir(dir, { recursive: true });
    console.log(`✅ Created: ${path.relative(projectRoot, dir)}`);
  }

  // Create CLAUDE.md if missing
  const claudeMd = path.join(projectRoot, layout.claudeMd);
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

### Boilerplate Structure
```
Source (ctx-eng-plus):
  syntropy/ce/ → Contains static boilerplate

Target (after init):
  .ce/ → Copied from syntropy/ce/
    - PRPs/system/ (executed + templates)
    - examples/system/ (model + patterns)
    - tools/ (CE CLI)
    - RULES.md
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

1. ⬜ Boilerplate structured in `syntropy/ce/` (PRPs, examples, tools, RULES.md)
2. ⬜ `syntropy_init_project` tool implemented
3. ⬜ Init copies `syntropy/ce/` → `.ce/` (system content)
4. ⬜ Init creates user directories: PRPs/, examples/, .serena/, CLAUDE.md
5. ⬜ Slash commands auto-installed: /generate-prp, /execute-prp, /update-context
6. ⬜ Overwrite warning displayed clearly
7. ⬜ Serena project activated on init
8. ⬜ Self-contained workflow (RULES.md embedded in .ce/)
9. ⬜ All tests passing (unit + integration)
10. ⬜ Documentation updated (README in syntropy/ce/)

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
- ✅ `syntropy/ce/PRPs/` (system PRPs boilerplate)
- ✅ `syntropy/ce/examples/` (system examples boilerplate)
- ✅ `syntropy/ce/tools/` (CE CLI boilerplate)
- ✅ `syntropy/ce/serena/` (empty, for project memories)
- ✅ `syntropy/ce/RULES.md` (distilled framework rules)
- ✅ `syntropy/ce/README.md` (boilerplate guide)
- ⬜ `syntropy-mcp/src/scanner.ts` (layout detection)
- ⬜ `syntropy-mcp/src/tools/init.ts` (init tool implementation)
- ⬜ `syntropy-mcp/src/tools-definition.ts` (register init tool)

**Files to Modify:**
- ⬜ Project CLAUDE.md (update with .ce/ references after init)

**No Files to Delete:**
- Keep existing structure (no migrations, only new boilerplate)
