# INITIAL: Syntropy Documentation & Project Init

**Feature:** Ship Context Engineering framework documentation with Syntropy MCP server and implement project initialization with auto-scaffolding.

---

## FEATURE

Syntropy becomes the distribution mechanism for CE framework documentation, providing it to any project via MCP tools. Projects initialize with standardized structure and slash commands.

**Goals:**
1. Ship CE framework docs with Syntropy (research/, templates/, slash commands)
2. Implement `syntropy_init_project` MCP tool for project scaffolding
3. Implement `/init-context-engineering` slash command (thin wrapper)
4. Auto-scaffold project structure: PRPs/, examples/, .serena/, CLAUDE.md, .claude/commands/
5. Upsert slash commands: generate-prp.md, execute-prp.md, update-context.md
6. Scan and index existing project knowledge (PRPs, examples, Serena memories)
7. Activate Serena MCP for code navigation
8. Support flexible layouts (root-level OR context-engineering/ subdirectory)

**Current Problems:**
- CE framework docs duplicated in every project
- No standardized project initialization
- Manual setup error-prone (missing directories, wrong slash commands)
- Framework updates don't propagate to existing projects

**Expected Outcome:**
- Framework docs shipped with Syntropy at `syntropy-mcp/docs/`
- MCP tool: `syntropy_init_project(project_root, options?)`
- Slash command: `/init-context-engineering` delegates to MCP tool
- ⚠️ **Slash commands ALWAYS overwritten** on init:
  - `/generate-prp`, `/execute-prp`, `/update-context`
  - User customizations LOST - create custom commands with different names
- Zero documentation duplication across projects
- Existing knowledge preserved and indexed (no deletion)

---

## EXAMPLES

### Example 1: Tool Definition Pattern

**Location:** `syntropy-mcp/src/tools/init.ts`

```typescript
// MCP Tool Definition
{
  name: "syntropy_init_project",
  description: "Initialize Context Engineering project structure with auto-scaffolding",
  inputSchema: {
    type: "object",
    properties: {
      project_root: {
        type: "string",
        description: "Absolute path to project root directory"
      },
      options: {
        type: "object",
        properties: {
          force: {
            type: "boolean",
            description: "Overwrite existing files without confirmation"
          },
          dry_run: {
            type: "boolean",
            description: "Preview changes without applying them"
          }
        }
      }
    },
    required: ["project_root"]
  }
}
```

**Pattern:** MCP tool owns all logic, returns JSON for automation.

### Example 2: Slash Command Wrapper

**Location:** `syntropy-mcp/commands/init-context-engineering.md`

```markdown
# /init-context-engineering - Initialize Context Engineering Project

Initialize standardized Context Engineering project structure with auto-scaffolding.

## Usage

```bash
/init-context-engineering [--force] [--dry-run]
```

## Implementation

This command delegates to MCP tool `mcp__syntropy_init_project`:

1. Detect current project root (git root or cwd)
2. Call MCP tool: `mcp__syntropy_init_project(project_root, options)`
3. Format output for user with progress updates
4. Report any errors with troubleshooting guidance

## Options

- `--force`: Overwrite existing files without confirmation
- `--dry-run`: Preview changes without applying them

## What Gets Created

- `PRPs/feature-requests/` - New feature blueprints
- `PRPs/executed/` - Completed implementations
- `examples/` - Reusable code patterns
- `.serena/memories/` - Project-specific learnings
- `CLAUDE.md` - Project guide (if missing)
- `.claude/commands/` - Slash commands (always updated)
  - `generate-prp.md`
  - `execute-prp.md`
  - `update-context.md`
- `.ce/syntropy-index.json` - Knowledge index

## What Gets Preserved

- Existing PRPs, examples, memories (scanned and indexed)
- Current CLAUDE.md content (not overwritten)
- Custom slash commands (if different names)

## What Gets Overwritten

⚠️ **WARNING**: These slash commands are ALWAYS overwritten:
- `/generate-prp`
- `/execute-prp`
- `/update-context`

User modifications will be LOST. To customize, create commands with different names (e.g., `my-generate-prp.md`).
```

**Pattern:** Slash command is user-facing wrapper, all logic in MCP tool.

### Example 3: Project Structure Detection

**Location:** `syntropy-mcp/src/scanner.ts`

```typescript
interface ProjectLayout {
  prps: string[];           // Paths to PRPs directories
  examples: string[];       // Paths to examples directories
  memories: string;         // Path to .serena/memories (always this location)
  claude_md: string | null; // Path to CLAUDE.md
  commands: string;         // Path to .claude/commands
  layout_type: 'root' | 'context-engineering';
}

export async function detectProjectLayout(projectRoot: string): Promise<ProjectLayout> {
  const layout: ProjectLayout = {
    prps: [],
    examples: [],
    memories: path.join(projectRoot, '.serena', 'memories'),
    claude_md: null,
    commands: path.join(projectRoot, '.claude', 'commands'),
    layout_type: 'root'
  };

  // Check for context-engineering/ subdirectory layout
  const ceSubdir = path.join(projectRoot, 'context-engineering');
  if (await exists(ceSubdir)) {
    layout.layout_type = 'context-engineering';
  }

  // Find PRPs directories (can be multiple)
  const prpDirs = await findDirs(projectRoot, 'PRPs');
  layout.prps = prpDirs;

  // Find examples directories
  const exampleDirs = await findDirs(projectRoot, 'examples');
  layout.examples = exampleDirs;

  // Find CLAUDE.md (root first, then subdirs)
  layout.claude_md = await findFile(projectRoot, 'CLAUDE.md');

  return layout;
}

// Helper: Find directories by name recursively
async function findDirs(root: string, name: string): Promise<string[]> {
  const results: string[] = [];

  async function search(dir: string, depth: number) {
    if (depth > 3) return; // Limit recursion

    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory()) {
        const fullPath = path.join(dir, entry.name);

        if (entry.name === name) {
          results.push(fullPath);
        }

        // Skip node_modules, .git, etc.
        if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
          await search(fullPath, depth + 1);
        }
      }
    }
  }

  await search(root, 0);
  return results;
}
```

**Pattern:** Flexible directory discovery, supports both layouts, preserves existing structure.

### Example 4: Slash Command Upsert Logic

**Location:** `syntropy-mcp/src/tools/init.ts`

```typescript
async function upsertSlashCommands(
  projectRoot: string,
  syntropyCommandsDir: string
): Promise<void> {
  const commandsDir = path.join(projectRoot, '.claude', 'commands');
  await fs.mkdir(commandsDir, { recursive: true });

  const commands = ['generate-prp.md', 'execute-prp.md', 'update-context.md'];

  for (const cmd of commands) {
    const src = path.join(syntropyCommandsDir, cmd);
    const dst = path.join(commandsDir, cmd);

    // Check if destination exists
    const exists = await fileExists(dst);

    if (exists) {
      // Compare content to detect user modifications
      const srcContent = await fs.readFile(src, 'utf-8');
      const dstContent = await fs.readFile(dst, 'utf-8');

      if (srcContent !== dstContent) {
        console.warn(
          `⚠️  Overwriting modified command: /${cmd.replace('.md', '')}\n` +
          `    User changes will be lost. To customize, use different name.`
        );
      }
    }

    // ALWAYS overwrite (keep framework commands in sync)
    await fs.copyFile(src, dst);
    console.log(`✅ Upserted slash command: /${cmd.replace('.md', '')}`);
  }
}
```

**Pattern:** Always overwrite framework commands, warn if user modifications detected.

### Example 5: Knowledge Scanning & Indexing

**Location:** `syntropy-mcp/src/indexer.ts`

```typescript
interface KnowledgeIndex {
  version: string;
  project_root: string;
  synced_at: string;
  framework_version: string;

  paths: {
    prps: string[];
    examples: string[];
    memories: string[];
    claude_md: string | null;
  };

  knowledge: {
    patterns: Record<string, PatternInfo>;
    prp_learnings: Record<string, PRPInfo>;
    memories: Record<string, MemoryInfo>;
  };
}

export async function scanAndIndex(layout: ProjectLayout): Promise<KnowledgeIndex> {
  const index: KnowledgeIndex = {
    version: '1.0',
    project_root: layout.project_root,
    synced_at: new Date().toISOString(),
    framework_version: '1.0',
    paths: {
      prps: layout.prps,
      examples: layout.examples,
      memories: [layout.memories],
      claude_md: layout.claude_md
    },
    knowledge: {
      patterns: {},
      prp_learnings: {},
      memories: {}
    }
  };

  // Scan PRPs
  for (const prpDir of layout.prps) {
    const prps = await scanPRPs(prpDir);
    Object.assign(index.knowledge.prp_learnings, prps);
  }

  // Scan examples
  for (const exampleDir of layout.examples) {
    const patterns = await scanExamples(exampleDir);
    Object.assign(index.knowledge.patterns, patterns);
  }

  // Scan Serena memories
  if (await exists(layout.memories)) {
    const memories = await scanMemories(layout.memories);
    Object.assign(index.knowledge.memories, memories);
  }

  return index;
}
```

**Pattern:** Non-destructive scanning, index all existing knowledge, preserve all files.

### Example 6: Serena Activation

**Location:** `syntropy-mcp/src/tools/init.ts`

```typescript
async function activateSerenaProject(projectRoot: string): Promise<void> {
  try {
    // Call Serena MCP via client manager
    await clientManager.callTool('serena', 'activate_project', {
      project: projectRoot
    });

    console.log(`✅ Activated Serena project: ${path.basename(projectRoot)}`);
  } catch (error) {
    // Graceful degradation if Serena unavailable
    console.warn(
      `⚠️  Could not activate Serena project: ${error.message}\n` +
      `🔧 Troubleshooting: Check Serena MCP server status\n` +
      `    Run: mcp__syntropy_healthcheck`
    );
    // Don't throw - init can succeed without Serena
  }
}
```

**Pattern:** Graceful degradation, clear troubleshooting, init succeeds even if Serena unavailable.

---

## DOCUMENTATION

### Framework Docs Migration

**Step 1: MOVE framework docs from ctx-eng-plus to syntropy-mcp** (one-time setup)

```bash
# Copy framework docs to Syntropy
cp -r ctx-eng-plus/docs/research syntropy-mcp/docs/
cp -r ctx-eng-plus/PRPs/templates syntropy-mcp/docs/
cp ctx-eng-plus/docs/*.md syntropy-mcp/docs/
cp ctx-eng-plus/.claude/commands/*.md syntropy-mcp/commands/

# Verify copy successful (check file counts match)
# Then delete from ctx-eng-plus (Syntropy is now source of truth)
rm -rf ctx-eng-plus/docs/
rm -rf ctx-eng-plus/PRPs/templates/
```

**Step 2: Syntropy becomes single source of truth**
- `syntropy-mcp/docs/research/` - Complete documentation suite (00-11)
- `syntropy-mcp/docs/templates/` - PRP templates (self-healing.md, kiss.md)
- `syntropy-mcp/docs/` - Top-level docs (prp-yaml-schema.md, etc.)
- `syntropy-mcp/commands/` - Slash command definitions

**Step 3: Init tool copies docs to target projects**
- When running `syntropy_init_project`, copy framework docs from Syntropy bundle to `<project>/docs/`
- **Rationale:** Offline reference, version pinning per project, no network dependency
- **Trade-off:** Local copies may drift from Syntropy source (acceptable for versioned releases)

### MCP Tool Implementation

**Location:** `syntropy-mcp/src/tools/init.ts`

**Exports:**
```typescript
export async function initProject(
  projectRoot: string,
  options?: InitOptions
): Promise<InitResult>
```

**Return Type:**
```typescript
interface InitResult {
  success: boolean;
  project_root: string;
  created: string[];      // Files/dirs created
  updated: string[];      // Files updated
  scanned: {
    prps: number;
    examples: number;
    memories: number;
  };
  index_path: string;     // Path to .ce/syntropy-index.json
  serena_active: boolean; // Whether Serena activated successfully
  warnings: string[];     // Non-fatal issues
  errors: string[];       // Fatal errors (if success=false)
}
```

### Slash Command Implementation

**Location:** `syntropy-mcp/commands/init-context-engineering.md`

**Workflow:**
1. Detect project root (git root or cwd)
2. Call MCP tool: `mcp__syntropy_init_project(project_root, options)`
3. Format progress output for user
4. Display summary with created/updated files
5. Show warnings (slash commands overwritten, Serena unavailable, etc.)

### TypeScript/Node.js Patterns

```typescript
// File system: async operations
import { promises as fs } from 'fs';
import * as path from 'path';

// Glob patterns: file discovery
import { glob } from 'glob';
const prpFiles = await glob('**/PRPs/**/*.md', { cwd: projectRoot });

// JSON operations
const index = JSON.parse(await fs.readFile(indexPath, 'utf-8'));
await fs.writeFile(indexPath, JSON.stringify(index, null, 2));

// Error handling with troubleshooting
try {
  await operation();
} catch (error) {
  throw new Error(
    `Operation failed: ${error.message}\n` +
    `🔧 Troubleshooting: Check permissions and retry`
  );
}
```

---

## OTHER CONSIDERATIONS

### Backward Compatibility

- Existing projects work with `syntropy init --existing`
- Both layouts supported: root-level PRPs/ OR context-engineering/PRPs/
- No breaking changes to existing MCP tool calls
- Preserve all existing knowledge (no deletion)

### Performance

- Lazy initialization for non-critical servers
- Index cached at `.ce/syntropy-index.json` (5-min TTL)
- Incremental reindexing (only changed files)
- Limit directory recursion depth (max 3 levels)

### Security

- Validate all file paths (prevent directory traversal)
- No secret exposure in index files
- Safe subprocess calls (if needed in Python delegation)
- Sanitize user input

### Error Handling

- Graceful degradation if Serena MCP unavailable
- Clear troubleshooting messages (🔧 format)
- No fishy fallbacks - fail fast with actionable errors
- Warn user when overwriting modified slash commands

### Migration Strategy

**Phase 1: Move Docs to Syntropy** (Manual, 1 hour)
```bash
# Copy framework docs to Syntropy
cp -r ctx-eng-plus/docs/research syntropy-mcp/docs/
cp -r ctx-eng-plus/PRPs/templates syntropy-mcp/docs/
cp ctx-eng-plus/docs/*.md syntropy-mcp/docs/
cp ctx-eng-plus/.claude/commands/*.md syntropy-mcp/commands/

# Verify copy successful (check file counts match)
# Then delete from ctx-eng-plus (Syntropy is now source of truth)
rm -rf ctx-eng-plus/docs/
rm -rf ctx-eng-plus/PRPs/templates/
```

**Phase 2: Implement Init Tool** (2-3 days)
- Create `syntropy-mcp/src/tools/init.ts`
- Implement scanner, indexer, upsert logic
- Add to tools-definition.ts

**Phase 3: Test Init Workflow** (1 day)
- Fresh project init
- Existing project init (root layout)
- Existing project init (context-engineering layout)

**Phase 4: Create Slash Command** (0.5 days)
- Write `syntropy-mcp/commands/init-context-engineering.md`
- Test delegation to MCP tool

### Testing Strategy

**Unit Tests:**
```typescript
// Test scanner
describe('detectProjectLayout', () => {
  it('detects root-level layout', async () => {
    const layout = await detectProjectLayout('/tmp/root-project');
    expect(layout.layout_type).toBe('root');
    expect(layout.prps).toContain('/tmp/root-project/PRPs');
  });

  it('detects context-engineering layout', async () => {
    const layout = await detectProjectLayout('/tmp/ce-project');
    expect(layout.layout_type).toBe('context-engineering');
    expect(layout.prps).toContain('/tmp/ce-project/context-engineering/PRPs');
  });
});

// Test indexer
describe('scanAndIndex', () => {
  it('indexes existing PRPs without deletion', async () => {
    const index = await scanAndIndex(layout);
    expect(Object.keys(index.knowledge.prp_learnings).length).toBeGreaterThan(0);
  });
});
```

**Integration Tests:**
```bash
# Test fresh project init
syntropy init /tmp/test-fresh --dry-run
syntropy init /tmp/test-fresh --json > result.json

# Assertions
test -d /tmp/test-fresh/PRPs/feature-requests
test -d /tmp/test-fresh/PRPs/executed
test -f /tmp/test-fresh/.claude/commands/generate-prp.md
test -f /tmp/test-fresh/.ce/syntropy-index.json
jq -e '.success == true' result.json
jq -e '.serena_active == true' result.json

# Test existing project init
cd ctx-eng-plus
syntropy init . --json > result.json
jq -e '.scanned.prps > 0' result.json  # Found existing PRPs
jq -e '.scanned.examples > 0' result.json  # Found examples
```

**E2E Tests:**
```bash
# Full workflow: init → query → verify
syntropy init /tmp/test-project
cd /tmp/test-project

# Slash commands should work
/generate-prp "test feature"  # Should create PRP-1
test -f PRPs/feature-requests/PRP-1-test-feature.md

# Index should exist
test -f .ce/syntropy-index.json
jq -e '.knowledge.prp_learnings["PRP-1"]' .ce/syntropy-index.json
```

### Configuration Files

- `.ce/syntropy-index.json` - Knowledge index (created by init)
- `syntropy-mcp/docs/` - Framework documentation (shipped)
- `syntropy-mcp/commands/` - Slash command definitions (shipped)
- `.serena/memories/` - Project memories (preserved)
- `.claude/commands/` - Slash commands (upserted)

### Constraints

- Offline-first: Index cached locally, framework docs copied to each project
- Single source of truth: Framework docs in Syntropy only (master copy)
- Git-based: Project knowledge in version control
- MCP standard: Follow protocol for tool definitions
- No deletion: Preserve all existing knowledge

### Gotchas

1. **Tool naming:** `syntropy_server_tool` format (Claude Code adds `mcp__` prefix)
2. **Layout detection:** Support BOTH root and context-engineering/ layouts
3. **Serena memories:** ALWAYS at `.serena/memories/`
4. **CLAUDE.md:** Search root first, then subdirs
5. **Framework docs distribution:** MOVE from ctx-eng-plus to Syntropy (one-time migration), then COPY from Syntropy to target projects on init
6. **Docs copy rationale:** Projects get local copy for offline reference, version pinning, no network dependency
7. **Docs drift trade-off:** Local project copies may lag Syntropy updates (acceptable for versioned releases)
8. **Slash commands:** ALWAYS overwrite on init (warn user)
9. **Command location:** `.claude/commands/` at project root only
10. **Graceful degradation:** Init succeeds even if Serena unavailable

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
cd syntropy-mcp && npm run build
cd syntropy-mcp && npm run lint
```

### Level 2: Unit Tests
```bash
cd syntropy-mcp && npm test src/scanner.test.ts
cd syntropy-mcp && npm test src/indexer.test.ts
cd syntropy-mcp && npm test src/tools/init.test.ts
```

### Level 3: Integration Tests
```bash
# Fresh project init
syntropy init /tmp/test-fresh --json
test -d /tmp/test-fresh/PRPs
test -f /tmp/test-fresh/.ce/syntropy-index.json

# Existing project init (root layout)
cd ctx-eng-plus && syntropy init . --json

# Existing project init (context-engineering/ layout) - CRITICAL E2E TEST
# IMPORTANT: Always run on branch or revert to HEAD after validation
cd ~/nc-rc/test-certinia && git checkout -b test-prp-29-1-init
syntropy init . --json

# Verify test-certinia (commit 9137b61) structure detected:
# - Existing layout: context-engineering/PRPs/, context-engineering/examples/
# - Existing Serena memories: .serena/memories/ (20 files)
# - Slash commands created: .claude/commands/
# - Framework docs copied: docs/research/, docs/templates/
# - Index created: .ce/syntropy-index.json with scanned knowledge

# Cleanup after validation:
cd ~/nc-rc/test-certinia && git checkout main && git branch -D test-prp-29-1-init
# OR: git reset --hard HEAD && git clean -fd .ce .claude docs
```

### Level 4: Pattern Conformance
- Tool naming: `syntropy_server_tool` format ✅
- Error handling: Fast failure with 🔧 troubleshooting ✅
- No fishy fallbacks: All errors actionable ✅
- Graceful degradation: Works without Serena ✅

---

## SUCCESS CRITERIA

1. ✅ Framework docs moved to `syntropy-mcp/docs/`
2. ⬜ MCP tool `syntropy_init_project` functional
3. ⬜ Slash command `/init-context-engineering` delegates correctly
4. ⬜ Fresh project init creates standard structure
5. ⬜ Existing project init preserves all knowledge
6. ⬜ Slash commands upserted and functional:
   - Run `/generate-prp` → creates valid PRP
   - Run `/execute-prp` → implements code
   - Run `/update-context` → syncs metadata
7. ⬜ Knowledge scanned and indexed correctly
8. ⬜ Serena activation successful (or graceful warning)
9. ⬜ Both layouts supported (root + context-engineering/)
10. ⬜ All tests passing (unit + integration + E2E)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Medium (3-4 days)
- Phase 1 (Move docs): 1 hour (manual)
- Phase 2 (Implement init tool): 2-3 days
- Phase 3 (Test workflows): 1 day
- Phase 4 (Slash command): 0.5 days

**Risk Level:** Low-Medium
- Framework docs migration straightforward (copy, no deletion)
- Existing knowledge preserved (no breaking changes)
- Graceful degradation if Serena unavailable

**Dependencies:**
- Syntropy MCP server (existing)
- Serena MCP (existing, optional)
- Node.js fs/promises, path (stdlib)
- glob package for file discovery

**Files to Create:**
- `syntropy-mcp/src/tools/init.ts` - MCP tool implementation
- `syntropy-mcp/src/scanner.ts` - Project structure scanner
- `syntropy-mcp/src/indexer.ts` - Knowledge indexer
- `syntropy-mcp/commands/init-context-engineering.md` - Slash command
- `syntropy-mcp/docs/` - Framework docs (moved from ctx-eng-plus)

**Files to Modify:**
- `syntropy-mcp/src/tools-definition.ts` - Add init tool
- `syntropy-mcp/src/index.ts` - Register init handler

**Files to Delete After Migration:**
- `ctx-eng-plus/docs/` - Framework docs MOVED to Syntropy (delete after successful copy verification)
- `ctx-eng-plus/PRPs/templates/` - Templates MOVED to Syntropy (delete after successful copy verification)

**Files to Keep:**
- `ctx-eng-plus/PRPs/executed/` - All existing PRPs preserved
- `ctx-eng-plus/PRPs/feature-requests/` - All existing PRPs preserved
- `ctx-eng-plus/examples/` - All existing examples preserved

**Framework Docs Distribution:**
- Syntropy: Single source of truth at `syntropy-mcp/docs/`
- Target Projects: Init tool copies docs from Syntropy to `<project>/docs/`
- **Why Copy?** Offline reference, version pinning, no network dependency
- **Trade-off:** Local copies may drift from Syntropy updates (acceptable for versioned releases)
