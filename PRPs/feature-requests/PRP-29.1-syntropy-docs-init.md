---
name: Syntropy Documentation Migration & Init Foundation
description: Copy CE framework boilerplate from syntropy/ce/ to project .ce/ directory
  and implement automated project initialization
prp_id: PRP-29.1
status: new
created_date: '2025-10-23T21:26:23.480043'
last_updated: '2025-10-23T21:26:23.480052'
updated_by: generate-prp-command
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
---

# Syntropy Documentation Migration & Init Foundation

## 🎯 Feature Overview

**Context:** Syntropy provides automated project scaffolding by copying CE framework boilerplate from `syntropy/ce/` to project `.ce/` directory, with slash command upsert and Serena activation.

**Repository Relationship:**
- **ctx-eng-plus:** Contains `syntropy/ce/` boilerplate (static copy-paste content)
- **syntropy-mcp:** MCP server that implements `syntropy_init_project` tool
- **Target Projects:** Any project using Context Engineering framework

**Problem:**
- CE framework content scattered across projects
- No standardized project initialization  
- Slash commands manually maintained per project
- No automatic framework updates
- System PRPs mixed with user PRPs

**Solution:**
Implement `syntropy_init_project` MCP tool that:
1. Copies `syntropy/ce/` boilerplate to project `.ce/` directory
2. Creates user content directories (`PRPs/`, `examples/`) at root
3. Auto-upserts slash commands (ALWAYS overwrites)
4. Activates Serena project for code navigation
5. Provides self-contained, auto-healing workflow

**Expected Outcome:**
- Framework boilerplate in `.ce/` (system content)
- User content at root: `PRPs/`, `examples/`, `CLAUDE.md`
- Slash commands: `/generate-prp`, `/execute-prp`, `/update-context`
- Clean separation: system (`.ce/`) vs user (`PRPs/`, `examples/`)
- ⚠️ Slash commands ALWAYS overwritten on init (user customizations lost)

---

## 🛠️ Implementation Blueprint

### Phase 1: Directory Structure & Boilerplate (2 hours)

**Goal:** Verify syntropy/ce/ boilerplate structure is complete

**Tasks:**
1. Verify `syntropy/ce/PRPs/system/` contains PRP-1-28 + templates
2. Verify `syntropy/ce/examples/system/` contains model + patterns
3. Verify `syntropy/ce/tools/` contains CE CLI package
4. Verify `syntropy/ce/.serena/` exists (empty, for project memories)
5. Verify `syntropy/ce/RULES.md` contains distilled framework rules
6. Verify `syntropy/ce/README.md` documents boilerplate structure

**Validation:**
```bash
# Verify directory structure
test -d syntropy/ce/PRPs/system && echo "✅ PRPs" || echo "❌ PRPs missing"
test -d syntropy/ce/examples/system && echo "✅ Examples" || echo "❌ Examples missing"
test -d syntropy/ce/tools && echo "✅ Tools" || echo "❌ Tools missing"
test -d syntropy/ce/.serena && echo "✅ Serena" || echo "❌ Serena missing"
test -f syntropy/ce/RULES.md && echo "✅ RULES.md" || echo "❌ RULES.md missing"

# Count content
find syntropy/ce/PRPs/system/executed -name "*.md" | wc -l  # Should be 36
find syntropy/ce/PRPs/system/templates -name "*.md" | wc -l  # Should be 3
find syntropy/ce/examples/system -name "*.md" -o -name "*.py" | wc -l  # Should be 9
```

**Success Criteria:**
- ✅ All 6 boilerplate components present
- ✅ Content counts match expected values
- ✅ No missing files or directories

---

### Phase 2: Scanner Implementation (3 hours)

**Goal:** Implement project layout detection logic

**File:** `syntropy-mcp/src/scanner.ts`

**Interface:**
```typescript
interface ProjectLayout {
  ceDir: string;            // ".ce" (system content)
  prpsDir: string;          // "PRPs" (user content)
  examplesDir: string;      // "examples" (user content)
  memoriesDir: string;      // ".serena/memories"
  claudeMd: string;         // "CLAUDE.md" location
  commandsDir: string;      // ".claude/commands"
}
```

**Implementation:**
```typescript
import * as fs from "fs/promises";
import * as path from "path";

export function detectProjectLayout(projectRoot: string): ProjectLayout {
  // Standard layout: .ce/ for system, root for user
  return {
    ceDir: ".ce",                      // System content
    prpsDir: "PRPs",                   // User PRPs
    examplesDir: "examples",           // User examples
    memoriesDir: ".serena/memories",   // Serena knowledge
    claudeMd: "CLAUDE.md",             // Project guide
    commandsDir: ".claude/commands"    // Slash commands
  };
}

export async function findCLAUDEmd(projectRoot: string): Promise<string> {
  const rootClaude = path.join(projectRoot, "CLAUDE.md");
  
  try {
    await fs.access(rootClaude);
    return "CLAUDE.md";
  } catch {
    // Create default if missing
    return "CLAUDE.md";
  }
}
```

**Validation:**
```bash
# Unit tests
cd syntropy-mcp
npm test src/scanner.test.ts

# Test cases:
# - test_detectProjectLayout_standard: Verify standard layout
# - test_findCLAUDEmd_exists: Find existing CLAUDE.md
# - test_findCLAUDEmd_missing: Return default when missing
```

**Success Criteria:**
- ✅ Layout detection returns consistent structure
- ✅ All unit tests passing
- ✅ No hardcoded paths (all relative)

---

### Phase 3: Init Tool Implementation (4 hours)

**Goal:** Implement `syntropy_init_project` MCP tool

**File:** `syntropy-mcp/src/tools/init.ts`

**Main Function:**
```typescript
interface InitProjectArgs {
  project_root: string;
}

export async function initProject(args: InitProjectArgs): Promise<object> {
  const projectRoot = path.resolve(args.project_root);

  try {
    console.log(`🚀 Initializing Context Engineering project: ${projectRoot}`);
    
    // 1. Detect layout
    const layout = detectProjectLayout(projectRoot);
    console.log(`✅ Detected standard layout`);

    // 2. Copy boilerplate
    await copyBoilerplate(projectRoot, layout);

    // 3. Scaffold user structure
    await scaffoldUserStructure(projectRoot, layout);

    // 4. Upsert slash commands
    await upsertSlashCommands(projectRoot);

    // 5. Activate Serena
    await activateSerenaProject(projectRoot);

    return {
      success: true,
      message: "Project initialized successfully",
      structure: ".ce/ (system) + PRPs/examples/ (user)",
      layout
    };
  } catch (error) {
    throw new Error(
      `Failed to initialize project: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure directory is writable and syntropy/ce/ exists`
    );
  }
}
```

**Copy Boilerplate:**
```typescript
async function copyBoilerplate(
  projectRoot: string, 
  layout: ProjectLayout
): Promise<void> {
  // Find syntropy/ce/ boilerplate
  const boilerplatePath = findBoilerplatePath();
  const targetCeDir = path.join(projectRoot, layout.ceDir);

  // Verify source exists
  try {
    await fs.access(boilerplatePath);
  } catch {
    throw new Error(
      `Boilerplate not found: ${boilerplatePath}\n` +
      `🔧 Troubleshooting: Ensure ctx-eng-plus repository is available`
    );
  }

  // Copy entire syntropy/ce/ to .ce/
  await fs.cp(boilerplatePath, targetCeDir, { 
    recursive: true,
    force: true  // Overwrite if exists
  });

  console.log(`✅ Copied boilerplate to ${layout.ceDir}/`);
  console.log(`   - PRPs/system/ (PRP-1-28 + templates)`);
  console.log(`   - examples/system/ (model + patterns)`);
  console.log(`   - tools/ (CE CLI)`);
  console.log(`   - .serena/ (project memories)`);
  console.log(`   - RULES.md (framework rules)`);
}

function findBoilerplatePath(): string {
  // Strategy 1: Environment variable
  if (process.env.SYNTROPY_BOILERPLATE_PATH) {
    return path.resolve(process.env.SYNTROPY_BOILERPLATE_PATH);
  }

  // Strategy 2: Relative to syntropy-mcp (development)
  const devPath = path.join(__dirname, "../../../ctx-eng-plus/syntropy/ce");
  if (fs.existsSync(devPath)) {
    return devPath;
  }

  // Strategy 3: Installed location (npm package)
  const installedPath = path.join(__dirname, "../../boilerplate");
  if (fs.existsSync(installedPath)) {
    return installedPath;
  }

  throw new Error(
    `Boilerplate not found in standard locations\n` +
    `🔧 Troubleshooting: Set SYNTROPY_BOILERPLATE_PATH env variable`
  );
}
```

**Scaffold User Structure:**
```typescript
async function scaffoldUserStructure(
  projectRoot: string,
  layout: ProjectLayout
): Promise<void> {
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
  try {
    await fs.access(claudeMd);
    console.log(`✅ CLAUDE.md exists`);
  } catch {
    const template = `# Project Guide

Add project-specific instructions here.

## Quick Reference
- \`/generate-prp\` - Generate comprehensive PRP from INITIAL.md
- \`/execute-prp\` - Execute PRP implementation
- \`/update-context\` - Sync context with codebase
`;
    await fs.writeFile(claudeMd, template);
    console.log(`✅ Created: CLAUDE.md`);
  }
}
```

**Upsert Slash Commands:**
```typescript
async function upsertSlashCommands(projectRoot: string): Promise<void> {
  const commandsDir = path.join(projectRoot, ".claude/commands");
  const syntropyCmds = path.join(__dirname, "../../commands");

  // Ensure directory exists
  await fs.mkdir(commandsDir, { recursive: true });

  const commands = [
    "generate-prp.md",
    "execute-prp.md", 
    "update-context.md",
    "peer-review.md"
  ];

  console.log("");
  for (const cmd of commands) {
    const src = path.join(syntropyCmds, cmd);
    const dst = path.join(commandsDir, cmd);

    // Check if exists
    const exists = await fs.access(dst).then(() => true).catch(() => false);

    if (exists) {
      console.log(`⚠️  Overwriting: /${cmd.replace('.md', '')}`);
    }

    // ALWAYS copy (overwrite if exists)
    await fs.copyFile(src, dst);
    console.log(`✅ Upserted: /${cmd.replace('.md', '')}`);
  }

  console.log("");
  console.log("⚠️  IMPORTANT: Slash commands are ALWAYS overwritten on init.");
  console.log("   To customize commands, create new files with different names.");
  console.log("   Examples: my-generate-prp.md, custom-update-context.md");
}
```

**Activate Serena:**
```typescript
async function activateSerenaProject(projectRoot: string): Promise<void> {
  try {
    // Call Serena MCP via Syntropy client manager
    const clientManager = await getClientManager();
    const serenaClient = clientManager.getClient("serena");

    await serenaClient.callTool("serena_activate_project", {
      project: projectRoot
    });

    console.log(`✅ Activated Serena project: ${path.basename(projectRoot)}`);
  } catch (error) {
    // Non-fatal: Serena activation is optional
    console.warn(`⚠️  Serena activation failed (non-fatal): ${error.message}`);
    console.warn(`   Code navigation features may be limited.`);
  }
}
```

**Validation:**
```bash
# Integration test
cd syntropy-mcp
npm test src/tools/init.test.ts

# Manual test
node -e "require('./dist/tools/init').initProject({project_root: '/tmp/test-project'})"

# Verify structure
ls -la /tmp/test-project/.ce/PRPs/system
ls -la /tmp/test-project/PRPs/feature-requests
ls -la /tmp/test-project/.claude/commands
```

**Success Criteria:**
- ✅ Boilerplate copied to `.ce/`
- ✅ User directories created at root
- ✅ Slash commands upserted
- ✅ Serena activated (or graceful failure)
- ✅ All integration tests passing

---

### Phase 4: Tool Registration (1 hour)

**Goal:** Register `syntropy_init_project` in MCP server

**File:** `syntropy-mcp/src/tools-definition.ts`

**Add Tool:**
```typescript
{
  name: "syntropy_init_project",
  description: "Initialize Context Engineering project structure with boilerplate copy and slash command upsert",
  inputSchema: {
    type: "object",
    properties: {
      project_root: {
        type: "string",
        description: "Absolute path to project root directory"
      }
    },
    required: ["project_root"]
  }
}
```

**Register Handler:**
```typescript
// In main handler
case "syntropy_init_project":
  return await initProject(args as InitProjectArgs);
```

**Validation:**
```bash
# Test MCP call
echo '{"method": "tools/call", "params": {"name": "syntropy_init_project", "arguments": {"project_root": "/tmp/test"}}}' |   node syntropy-mcp/dist/index.js
```

**Success Criteria:**
- ✅ Tool registered in tools list
- ✅ Handler correctly routes to initProject()
- ✅ MCP call succeeds

---

### Phase 5: Testing & Documentation (2 hours)

**Goal:** Comprehensive testing and documentation

**Unit Tests:**
```typescript
// src/scanner.test.ts
describe("detectProjectLayout", () => {
  it("returns standard layout", () => {
    const layout = detectProjectLayout("/path/to/project");
    expect(layout.ceDir).toBe(".ce");
    expect(layout.prpsDir).toBe("PRPs");
  });
});

// src/tools/init.test.ts
describe("copyBoilerplate", () => {
  it("copies syntropy/ce to .ce/", async () => {
    const tmp = await createTempDir();
    await copyBoilerplate(tmp, detectProjectLayout(tmp));
    
    expect(await fs.access(path.join(tmp, ".ce/PRPs/system"))).resolves;
    expect(await fs.access(path.join(tmp, ".ce/examples/system"))).resolves;
  });
});

describe("upsertSlashCommands", () => {
  it("overwrites existing commands", async () => {
    const tmp = await createTempDir();
    const cmdPath = path.join(tmp, ".claude/commands/generate-prp.md");
    
    // Create existing file
    await fs.mkdir(path.dirname(cmdPath), { recursive: true });
    await fs.writeFile(cmdPath, "OLD CONTENT");
    
    await upsertSlashCommands(tmp);
    
    const content = await fs.readFile(cmdPath, "utf-8");
    expect(content).not.toContain("OLD CONTENT");
  });
});
```

**Integration Tests:**
```bash
# Test fresh project
mkdir -p /tmp/test-fresh
syntropy_init_project /tmp/test-fresh

# Verify structure
test -d /tmp/test-fresh/.ce/PRPs/system && echo "✅ System PRPs"
test -d /tmp/test-fresh/PRPs/feature-requests && echo "✅ User PRPs"
test -f /tmp/test-fresh/.claude/commands/generate-prp.md && echo "✅ Slash commands"

# Test existing project
mkdir -p /tmp/test-existing/PRPs/executed
echo "# Existing PRP" > /tmp/test-existing/PRPs/executed/PRP-1.md
syntropy_init_project /tmp/test-existing

# Verify existing content preserved
test -f /tmp/test-existing/PRPs/executed/PRP-1.md && echo "✅ Existing PRPs preserved"
```

**Documentation:**
- Update `syntropy/ce/README.md` with copy-on-init instructions
- Document `SYNTROPY_BOILERPLATE_PATH` env variable
- Add troubleshooting guide for common issues

**Success Criteria:**
- ✅ All unit tests passing (100% coverage)
- ✅ All integration tests passing
- ✅ Documentation complete
- ✅ No breaking changes to existing projects

---

## 📋 Acceptance Criteria

**Must Have:**
- [x] `syntropy/ce/` boilerplate structure complete (done in PRE-29)
- [ ] `syntropy_init_project` MCP tool implemented
- [ ] Boilerplate copy: `syntropy/ce/` → `.ce/`
- [ ] User directories created: `PRPs/`, `examples/`, `.serena/`
- [ ] Slash commands upserted: 4 commands
- [ ] Overwrite warning displayed
- [ ] Serena project activated
- [ ] All tests passing

**Nice to Have:**
- [ ] Support for custom boilerplate path (env variable)
- [ ] Dry-run mode (preview changes without copying)
- [ ] Progress bar for large copies

**Out of Scope:**
- Automatic framework updates (handled by PRP-29.3)
- Knowledge graph sync (handled by PRP-29.2)
- Migration from old layouts (manual process)

---

## 🧪 Testing Strategy

### Unit Tests (src/scanner.test.ts, src/tools/init.test.ts)
- Layout detection logic
- Boilerplate copy operations
- Directory scaffolding
- Slash command upsert
- Error handling paths

### Integration Tests
- Fresh project init (empty directory)
- Existing project init (preserve user content)
- Serena activation (success + failure)

### Manual Testing
```bash
# Test 1: Fresh project
/tmp/test-fresh> syntropy_init_project .
# Expect: Full structure created

# Test 2: Existing project
/tmp/test-existing> syntropy_init_project .
# Expect: User content preserved, system updated

# Test 3: Custom boilerplate path
SYNTROPY_BOILERPLATE_PATH=/custom/path syntropy_init_project /tmp/test
# Expect: Custom boilerplate used
```

---

## 📚 Dependencies

**External:**
- Node.js 18+ (for fs/promises, fs.cp)
- TypeScript 5.x
- @modelcontextprotocol/sdk

**Internal:**
- `syntropy/ce/` boilerplate (completed in PRE-29)
- Syntropy MCP client manager
- Serena MCP (optional)

**Files Modified:**
- `syntropy-mcp/src/scanner.ts` (new)
- `syntropy-mcp/src/tools/init.ts` (new)
- `syntropy-mcp/src/tools-definition.ts` (register tool)
- `syntropy-mcp/src/index.ts` (route handler)

---

## ⚠️ Risks & Mitigations

**Risk 1: Boilerplate path not found**
- **Mitigation:** Multi-strategy search (env var, relative, installed)
- **Fallback:** Clear error with troubleshooting steps

**Risk 2: Overwriting user customizations**
- **Mitigation:** Clear warnings, suggest alternative names
- **Documentation:** Explain slash command overwrite policy

**Risk 3: Serena activation failure**
- **Mitigation:** Non-fatal error, graceful degradation
- **Communication:** Warn user about limited features

**Risk 4: Permission errors during copy**
- **Mitigation:** Verify directory writable before copy
- **Error:** Actionable troubleshooting (check permissions)

---

## 📖 References

**MCP Documentation:**
- Tool building: https://modelcontextprotocol.io/docs/tools/building-tools
- TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

**Node.js Documentation:**
- fs/promises: https://nodejs.org/api/fs.html#promises-api
- fs.cp(): https://nodejs.org/api/fs.html#fspromisescpsrc-dest-options

**Related PRPs:**
- PRP-29.2: Syntropy Knowledge Query (depends on this)
- PRP-29.3: Syntropy Context Sync (depends on this)
- PRP-1: Init Context Engineering (original implementation)

**Boilerplate:**
- Location: `ctx-eng-plus/syntropy/ce/`
- README: `syntropy/ce/README.md`
- Structure validated: commit c5109d5

---

## 🎯 Success Metrics

**Implementation:**
- Time to implement: 12 hours (estimated)
- Code coverage: 90%+ for init tool
- Test success rate: 100%

**User Experience:**
- Init time: <5 seconds for average project
- Clear progress messages (✅ Created, ⚠️ Overwriting)
- Zero manual steps after `/init-context-engineering`

**Quality:**
- Zero breaking changes to existing projects
- All error messages include 🔧 troubleshooting
- No fishy fallbacks (fast failure only)
