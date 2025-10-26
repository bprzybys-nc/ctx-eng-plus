---
name: Syntropy Init Tool Refinement
description: Selective boilerplate copying with exception mappings, already-initialized detection, RULES.md blending, and Serena activation
prp_id: PRP-29.2
status: new
created_date: '2025-10-26T00:00:00.000000'
last_updated: '2025-10-26T00:00:00.000000'
updated_by: manual
dependencies:
- PRP-29.1
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
---

# Syntropy Init Tool Refinement

## 🎯 Feature Overview

**Context:** PRP-29.1 implemented basic init tool with full recursive boilerplate copy. This PRP refines initialization with selective copying, intelligent content blending, and project activation.

**Prerequisites:** PRP-29.1 must be completed (provides init tool foundation)

**Problem:**
- Full recursive copy wasteful (copies README.md, temp files, caches)
- No already-initialized detection (re-runs on existing projects)
- `.serena/` should be at root, not `.ce/.serena/`
- RULES.md needs intelligent blending into CLAUDE.md (not direct copy)
- Serena not activated after init (project not registered)
- Boilerplate contains files not needed in target projects

**Solution:**
Implement refined initialization with:
1. **Boilerplate cleanup**: Remove README.md, drift-report.md, health-cache.json from source
2. **Already-initialized check**: Detect existing `.ce/` via 3 marker files
3. **Selective copying**: Exception-based file mapping vs full recursive
4. **RULES.md blending**: Intelligent merge into CLAUDE.md with deduplication
5. **Serena activation**: Auto-activate project after `.serena/` copied
6. **Config file filtering**: Copy only persistent config (exclude ephemeral caches)

**Expected Outcome:**
- ✅ Already-initialized projects skip re-init
- ✅ `.serena/` at project root (not `.ce/.serena/`)
- ✅ RULES.md content blended into CLAUDE.md (no duplicate file)
- ✅ Serena activated with project path
- ✅ Clean boilerplate (no README.md pollution)
- ✅ Config files in `.ce/` for framework persistence
- ✅ Non-fatal Serena activation (warns if unavailable)

---

## 🛠️ Implementation Blueprint

### Phase 1: Clean Boilerplate (30 minutes)

**Goal:** Remove files from `syntropy-mcp/ce/` that shouldn't be copied to target projects

**Files to Delete:**
```bash
syntropy-mcp/ce/
├── README.md                    # ❌ DELETE (boilerplate docs, not user-facing)
├── drift-report.md              # ❌ DELETE (generated file, project-specific)
└── syntropy-health-cache.json   # ❌ DELETE (cache file, ephemeral)
```

**Files to Keep:**
```bash
syntropy-mcp/ce/
├── PRPs/system/                 # ✅ KEEP (framework PRPs)
├── examples/system/             # ✅ KEEP (framework examples)
├── tools/                       # ✅ KEEP (CE CLI)
├── .serena/                     # ✅ KEEP (but copy to root, not .ce/)
├── RULES.md                     # ✅ KEEP (but blend into CLAUDE.md)
├── config.yml                   # ✅ KEEP (framework config)
├── hooks-config.yml             # ✅ KEEP (git hooks)
├── linear-defaults.yml          # ✅ KEEP (Linear integration)
├── shell-functions.sh           # ✅ KEEP (shell helpers)
├── tool-alternatives.yml        # ✅ KEEP (tool mappings)
└── tool-inventory.yml           # ✅ KEEP (tool catalog)
```

**Implementation:**
```bash
cd /Users/bprzybysz/nc-src/ctx-eng-plus/syntropy-mcp/ce

# Delete unwanted files
rm -f README.md
rm -f drift-report.md
rm -f syntropy-health-cache.json

# Verify cleanup
echo "✅ Boilerplate cleaned"
ls -la
```

**Validation:**
```typescript
// Test boilerplate is clean
const boilerplatePath = findBoilerplatePath();
const files = await fs.readdir(boilerplatePath);

// Should NOT contain
assert(!files.includes("README.md"));
assert(!files.includes("drift-report.md"));
assert(!files.includes("syntropy-health-cache.json"));

// Should contain
assert(files.includes("RULES.md"));
assert(files.includes("config.yml"));

console.log("✅ Boilerplate structure verified");
```

**Success Criteria:**
- ✅ README.md removed from boilerplate
- ✅ Generated files removed (drift-report.md, health-cache.json)
- ✅ Essential config files retained
- ✅ Boilerplate verification test passing

---

### Phase 2: Already-Initialized Detection (1 hour)

**Goal:** Detect existing `.ce/` structure and skip re-initialization

**Marker Files Strategy:**
Check for 3 critical markers that indicate complete initialization:
1. `.ce/RULES.md` - Framework rules (always present after init)
2. `.ce/PRPs/system/` - System PRPs directory (core content)
3. `.ce/tools/` - CE CLI tools (framework utilities)

**File:** `syntropy-mcp/src/scanner.ts`

**Implementation:**
```typescript
import { existsSync } from "fs";
import * as path from "path";

/**
 * Check if project is already initialized.
 *
 * Strategy: Verify 3 marker files/directories exist.
 * - .ce/RULES.md (framework rules)
 * - .ce/PRPs/system/ (system PRPs)
 * - .ce/tools/ (CE CLI)
 *
 * @param projectRoot Absolute path to project root
 * @returns true if already initialized, false otherwise
 */
export function isAlreadyInitialized(projectRoot: string): boolean {
  const markers = [
    path.join(projectRoot, ".ce", "RULES.md"),
    path.join(projectRoot, ".ce", "PRPs", "system"),
    path.join(projectRoot, ".ce", "tools")
  ];

  const allExist = markers.every(marker => existsSync(marker));

  if (allExist) {
    console.error("✅ Project already initialized (.ce/ exists)");
    console.error("   Skipping initialization");
  }

  return allExist;
}
```

**Integration into initProject():**

**File:** `syntropy-mcp/src/tools/init.ts`

```typescript
export async function initProject(args: InitProjectArgs): Promise<InitProjectResult> {
  const projectRoot = path.resolve(args.project_root);

  try {
    console.error(`🚀 Initializing Context Engineering project: ${projectRoot}`);

    // 1. Validate project root
    await validateProjectRoot(projectRoot);
    console.error(`✅ Project root validated`);

    // 2. Check if already initialized (NEW)
    if (isAlreadyInitialized(projectRoot)) {
      const layout = detectProjectLayout(projectRoot);
      return {
        success: true,
        message: "Project already initialized (skipped)",
        structure: ".ce/ (existing)",
        layout
      };
    }

    // 3. Detect layout
    const layout = detectProjectLayout(projectRoot);
    console.error(`✅ Detected standard layout`);

    // ... rest of init logic
  } catch (error) {
    // ... error handling
  }
}
```

**Validation:**
```typescript
// Test already-initialized detection
test("skips init if already initialized", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
  try {
    const boilerplatePath = path.join(__dirname, "../../ce");
    process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

    // First init
    const result1 = await initProject({ project_root: tmpDir });
    assert.equal(result1.success, true);
    assert(result1.message.includes("successfully"));

    // Second init (should skip)
    const result2 = await initProject({ project_root: tmpDir });
    assert.equal(result2.success, true);
    assert(result2.message.includes("already initialized"));
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});
```

**Success Criteria:**
- ✅ `isAlreadyInitialized()` checks 3 markers
- ✅ Returns early with success if already initialized
- ✅ Clear log messages indicate skip
- ✅ Test verifies idempotent behavior

---

### Phase 3: Selective Copy Logic (2 hours)

**Goal:** Replace full recursive copy with selective file mapping using exception rules

**Exception Mappings:**

```
syntropy-mcp/ce/                → Target
├── PRPs/**                     → .ce/PRPs/**              (standard)
├── examples/**                 → .ce/examples/**          (standard)
├── tools/**                    → .ce/tools/**             (standard)
├── .serena/**                  → .serena/**               (EXCEPTION: root)
├── RULES.md                    → [blend into CLAUDE.md]  (EXCEPTION: blend)
├── config.yml                  → .ce/config.yml           (standard)
├── hooks-config.yml            → .ce/hooks-config.yml     (standard)
├── linear-defaults.yml         → .ce/linear-defaults.yml  (standard)
├── shell-functions.sh          → .ce/shell-functions.sh   (standard)
├── tool-alternatives.yml       → .ce/tool-alternatives.yml(standard)
└── tool-inventory.yml          → .ce/tool-inventory.yml   (standard)
```

**File:** `syntropy-mcp/src/tools/init.ts`

**Replace copyBoilerplate():**

```typescript
/**
 * Copy boilerplate with selective file mapping.
 *
 * Standard directories → .ce/
 * Exception: .serena/ → project root
 * Exception: RULES.md → blended into CLAUDE.md (Phase 4)
 *
 * @param projectRoot Target project root
 * @param layout Project layout
 */
async function copyBoilerplate(
  projectRoot: string,
  layout: ProjectLayout
): Promise<void> {
  const boilerplatePath = findBoilerplatePath();

  // Verify source exists
  const sourceExists = await directoryExists(boilerplatePath);
  if (!sourceExists) {
    throw new Error(
      `Boilerplate not found: ${boilerplatePath}\n` +
      `🔧 Troubleshooting: Set SYNTROPY_BOILERPLATE_PATH env variable`
    );
  }

  console.error(`\n✅ Copying boilerplate with selective mapping:`);

  // 1. Copy standard directories to .ce/
  const standardDirs = ["PRPs", "examples", "tools"];
  const targetCeDir = path.join(projectRoot, layout.ceDir);

  await fs.mkdir(targetCeDir, { recursive: true });

  for (const dir of standardDirs) {
    const src = path.join(boilerplatePath, dir);
    const dst = path.join(targetCeDir, dir);

    if (await directoryExists(src)) {
      await fs.cp(src, dst, { recursive: true, force: true });
      console.error(`   ✓ ${dir}/ → .ce/${dir}/`);
    }
  }

  // 2. Copy config files to .ce/
  const configFiles = [
    "config.yml",
    "hooks-config.yml",
    "linear-defaults.yml",
    "shell-functions.sh",
    "tool-alternatives.yml",
    "tool-inventory.yml"
  ];

  for (const file of configFiles) {
    const src = path.join(boilerplatePath, file);
    const dst = path.join(targetCeDir, file);

    if (await fileExists(src)) {
      await fs.copyFile(src, dst);
      console.error(`   ✓ ${file} → .ce/${file}`);
    }
  }

  // 3. EXCEPTION: Copy .serena/ to project root (not .ce/)
  const serenaSrc = path.join(boilerplatePath, ".serena");
  const serenaDst = path.join(projectRoot, ".serena");

  if (await directoryExists(serenaSrc)) {
    await fs.cp(serenaSrc, serenaDst, { recursive: true, force: true });
    console.error(`   ✓ .serena/ → .serena/ (root)`);
  }

  // 4. EXCEPTION: RULES.md will be blended in Phase 4 (not copied directly)
  console.error(`   ⚠️  RULES.md → deferred to blending phase`);
}
```

**Validation:**
```typescript
test("copies with selective mapping", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
  try {
    const boilerplatePath = path.join(__dirname, "../../ce");
    process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

    await initProject({ project_root: tmpDir });

    // Verify standard dirs in .ce/
    assert(await directoryExists(path.join(tmpDir, ".ce/PRPs/system")));
    assert(await directoryExists(path.join(tmpDir, ".ce/examples/system")));
    assert(await directoryExists(path.join(tmpDir, ".ce/tools")));

    // Verify .serena/ at root
    assert(await directoryExists(path.join(tmpDir, ".serena")));
    assert(!await directoryExists(path.join(tmpDir, ".ce/.serena")));

    // Verify config files in .ce/
    assert(await fileExists(path.join(tmpDir, ".ce/config.yml")));
    assert(await fileExists(path.join(tmpDir, ".ce/hooks-config.yml")));

    console.log("✅ Selective copy mapping verified");
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});
```

**Success Criteria:**
- ✅ Standard dirs copied to `.ce/`
- ✅ `.serena/` copied to project root (not `.ce/`)
- ✅ Config files copied to `.ce/`
- ✅ RULES.md NOT copied (deferred to blending)
- ✅ All verification tests passing

---

### Phase 4: RULES.md Blending (2 hours)

**Goal:** Intelligently merge RULES.md into CLAUDE.md with deduplication, style preservation, and anti-pattern removal

**Blending Strategy:**

1. **Read existing CLAUDE.md** (if exists)
2. **Read RULES.md from boilerplate**
3. **Parse both into sections** (markdown headers)
4. **Detect duplicate rules** (semantic matching, not exact string)
5. **Remove anti-pattern elements** from RULES.md
6. **Preserve project's CLAUDE.md style** (heading levels, formatting)
7. **Merge unique rules** at appropriate location
8. **Write blended CLAUDE.md**

**File:** `syntropy-mcp/src/tools/init.ts`

**Implementation:**
```typescript
import * as fs from "fs/promises";
import * as path from "path";

interface MarkdownSection {
  heading: string;
  level: number;
  content: string;
}

/**
 * Blend RULES.md into CLAUDE.md intelligently.
 *
 * Features:
 * - Deduplication: Skip rules already in CLAUDE.md
 * - Style preservation: Match existing heading levels and format
 * - Anti-pattern removal: Filter out unwanted patterns
 * - Semantic matching: Detect similar rules with different wording
 *
 * @param projectRoot Target project root
 * @param layout Project layout
 */
async function blendRulesIntoCLAUDEmd(
  projectRoot: string,
  layout: ProjectLayout
): Promise<void> {
  const claudeMdPath = path.join(projectRoot, layout.claudeMd);
  const rulesMdPath = path.join(
    findBoilerplatePath(),
    "RULES.md"
  );

  try {
    // Read RULES.md from boilerplate
    const rulesContent = await fs.readFile(rulesMdPath, "utf-8");
    const rulesSections = parseMarkdownSections(rulesContent);

    // Read existing CLAUDE.md (if exists)
    let claudeContent = "";
    let claudeSections: MarkdownSection[] = [];

    try {
      claudeContent = await fs.readFile(claudeMdPath, "utf-8");
      claudeSections = parseMarkdownSections(claudeContent);
    } catch {
      // CLAUDE.md doesn't exist, will create new
      console.error(`   Creating new CLAUDE.md with RULES.md content`);
    }

    // Filter RULES.md sections
    const filteredRules = filterRulesSections(rulesSections);

    // Deduplicate against existing CLAUDE.md
    const uniqueRules = deduplicateRules(filteredRules, claudeSections);

    if (uniqueRules.length === 0) {
      console.error(`   ✅ RULES.md: All rules already in CLAUDE.md (no additions)`);
      return;
    }

    // Blend unique rules into CLAUDE.md
    const blendedContent = blendSections(claudeSections, uniqueRules);

    // Write blended CLAUDE.md
    await fs.writeFile(claudeMdPath, blendedContent);

    console.error(`   ✅ RULES.md: Blended ${uniqueRules.length} unique rules into CLAUDE.md`);
  } catch (error) {
    throw new Error(
      `Failed to blend RULES.md: ${error}\n` +
      `🔧 Troubleshooting: Check RULES.md exists in boilerplate`
    );
  }
}

/**
 * Parse markdown into sections by headers.
 */
function parseMarkdownSections(content: string): MarkdownSection[] {
  const sections: MarkdownSection[] = [];
  const lines = content.split("\n");

  let currentSection: MarkdownSection | null = null;

  for (const line of lines) {
    // Match headers (## Heading or ### Heading)
    const headerMatch = line.match(/^(#{2,6})\s+(.+)$/);

    if (headerMatch) {
      // Save previous section
      if (currentSection) {
        sections.push(currentSection);
      }

      // Start new section
      currentSection = {
        heading: headerMatch[2].trim(),
        level: headerMatch[1].length,
        content: ""
      };
    } else if (currentSection) {
      // Add line to current section
      currentSection.content += line + "\n";
    }
  }

  // Save last section
  if (currentSection) {
    sections.push(currentSection);
  }

  return sections;
}

/**
 * Filter out anti-pattern sections from RULES.md.
 *
 * Remove:
 * - Overly verbose examples
 * - Deprecated patterns
 * - Tool-specific configs (keep only universal rules)
 */
function filterRulesSections(sections: MarkdownSection[]): MarkdownSection[] {
  const antiPatterns = [
    "Context Engineering Integration",  // Project-specific, not universal
    "Tool Selection",                   // Tool-specific, not rules
    "Quick Reference",                  // Redundant with main CLAUDE.md
  ];

  return sections.filter(section => {
    // Remove anti-pattern sections
    if (antiPatterns.some(ap => section.heading.includes(ap))) {
      return false;
    }

    // Keep core rule sections
    return (
      section.heading.includes("MANDATORY") ||
      section.heading.includes("REQUIRED") ||
      section.heading.includes("FORBIDDEN") ||
      section.heading.includes("Policy") ||
      section.heading.includes("Standards") ||
      section.heading.includes("Principles")
    );
  });
}

/**
 * Deduplicate rules: skip sections already in CLAUDE.md.
 *
 * Uses semantic matching:
 * - Exact heading match
 * - Similar keywords (>70% overlap)
 * - Similar content (>50% overlap)
 */
function deduplicateRules(
  rulesSections: MarkdownSection[],
  claudeSections: MarkdownSection[]
): MarkdownSection[] {
  return rulesSections.filter(rule => {
    // Check if similar section exists in CLAUDE.md
    const isDuplicate = claudeSections.some(claude => {
      // Exact heading match
      if (rule.heading === claude.heading) {
        return true;
      }

      // Keyword overlap check
      const ruleKeywords = extractKeywords(rule.heading + " " + rule.content);
      const claudeKeywords = extractKeywords(claude.heading + " " + claude.content);
      const overlap = calculateOverlap(ruleKeywords, claudeKeywords);

      return overlap > 0.7;  // 70% keyword overlap = duplicate
    });

    return !isDuplicate;
  });
}

/**
 * Extract keywords from text (lowercase, >3 chars, no stopwords).
 */
function extractKeywords(text: string): Set<string> {
  const stopwords = new Set(["the", "and", "for", "with", "this", "that", "from"]);

  return new Set(
    text
      .toLowerCase()
      .match(/\b\w{4,}\b/g)
      ?.filter(word => !stopwords.has(word)) || []
  );
}

/**
 * Calculate Jaccard similarity (keyword overlap).
 */
function calculateOverlap(set1: Set<string>, set2: Set<string>): number {
  const intersection = new Set([...set1].filter(x => set2.has(x)));
  const union = new Set([...set1, ...set2]);

  return union.size > 0 ? intersection.size / union.size : 0;
}

/**
 * Blend unique rules into CLAUDE.md content.
 *
 * Strategy: Append unique rules at end with separator.
 */
function blendSections(
  claudeSections: MarkdownSection[],
  uniqueRules: MarkdownSection[]
): string {
  let blended = "";

  // Reconstruct existing CLAUDE.md
  for (const section of claudeSections) {
    blended += `${"#".repeat(section.level)} ${section.heading}\n`;
    blended += section.content;
  }

  // Add separator
  blended += "\n---\n\n";
  blended += "## Framework Rules (from Context Engineering)\n\n";

  // Add unique rules
  for (const rule of uniqueRules) {
    blended += `${"#".repeat(rule.level)} ${rule.heading}\n`;
    blended += rule.content;
  }

  return blended;
}
```

**Integration:**
```typescript
// In copyBoilerplate() after copying files
await blendRulesIntoCLAUDEmd(projectRoot, layout);
```

**Validation:**
```typescript
test("blends RULES.md without duplicates", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
  try {
    // Create CLAUDE.md with existing rule
    const claudeMdPath = path.join(tmpDir, "CLAUDE.md");
    await fs.writeFile(claudeMdPath, `
# Project Guide

## No Fishy Fallbacks - MANDATORY
- Fast failure: Let exceptions bubble up
`);

    process.env.SYNTROPY_BOILERPLATE_PATH = path.join(__dirname, "../../ce");
    await initProject({ project_root: tmpDir });

    const blended = await fs.readFile(claudeMdPath, "utf-8");

    // Should NOT duplicate "No Fishy Fallbacks"
    const matches = (blended.match(/No Fishy Fallbacks/g) || []).length;
    assert.equal(matches, 1, "Should not duplicate existing rules");

    console.log("✅ RULES.md blending verified");
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});
```

**Success Criteria:**
- ✅ Parses markdown into sections
- ✅ Filters anti-pattern sections
- ✅ Deduplicates using semantic matching
- ✅ Preserves CLAUDE.md style
- ✅ Appends unique rules with separator
- ✅ Test verifies no duplicates

---

### Phase 5: Serena Activation (1.5 hours)

**Goal:** Auto-activate Serena with project path after `.serena/` copied

**File:** `syntropy-mcp/src/tools/init.ts`

**Implementation:**
```typescript
import { getClientManager } from "../client-manager.js";

/**
 * Activate Serena project after .serena/ files copied.
 *
 * Non-fatal: Warns if Serena unavailable, doesn't break init.
 *
 * @param projectRoot Absolute path to project root
 */
async function activateSerenaProject(projectRoot: string): Promise<void> {
  try {
    console.error(`\n🔍 Activating Serena project...`);

    const clientManager = getClientManager();
    const serenaClient = await clientManager.getOrCreateClient("serena");

    // Call serena_activate_project tool
    const result = await serenaClient.callTool("serena_activate_project", {
      project: projectRoot
    });

    if (result && result.content) {
      console.error(`✅ Serena activated: ${projectRoot}`);
    } else {
      console.error(`⚠️  Serena activation returned unexpected result`);
    }
  } catch (error) {
    // Non-fatal: Serena may not be available or configured
    console.error(`⚠️  Serena activation failed (non-fatal): ${error.message}`);
    console.error(`   Project init will continue without Serena activation`);
    console.error(`   You can manually activate later if needed`);
  }
}
```

**Integration into initProject():**
```typescript
export async function initProject(args: InitProjectArgs): Promise<InitProjectResult> {
  const projectRoot = path.resolve(args.project_root);

  try {
    // ... validation, already-initialized check ...

    // 3. Copy boilerplate
    await copyBoilerplate(projectRoot, layout);

    // 4. Scaffold user structure
    await scaffoldUserStructure(projectRoot, layout);

    // 5. Create CLAUDE.md if missing
    await ensureCLAUDEmd(projectRoot, layout);

    // 6. Upsert slash commands
    await upsertSlashCommands(projectRoot, layout);

    // 7. Activate Serena (NEW - non-fatal)
    await activateSerenaProject(projectRoot);

    console.error(`\n✅ Project initialization complete!`);
    console.error(`   - Boilerplate copied with selective mapping`);
    console.error(`   - RULES.md blended into CLAUDE.md`);
    console.error(`   - Serena activated with project path`);
    console.error(`   - Slash commands configured`);

    return {
      success: true,
      message: "Project initialized successfully",
      structure: ".ce/ (system) + PRPs/examples/ (user)",
      layout
    };
  } catch (error) {
    // ... error handling ...
  }
}
```

**Validation:**
```typescript
test("activates Serena after init", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
  try {
    process.env.SYNTROPY_BOILERPLATE_PATH = path.join(__dirname, "../../ce");

    // Mock Serena client
    const mockSerenaClient = {
      callTool: jest.fn().mockResolvedValue({ content: "activated" })
    };

    jest.spyOn(clientManager, "getOrCreateClient").mockResolvedValue(mockSerenaClient);

    await initProject({ project_root: tmpDir });

    // Verify Serena was called with project path
    expect(mockSerenaClient.callTool).toHaveBeenCalledWith(
      "serena_activate_project",
      { project: tmpDir }
    );

    console.log("✅ Serena activation verified");
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});

test("continues init if Serena unavailable", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
  try {
    process.env.SYNTROPY_BOILERPLATE_PATH = path.join(__dirname, "../../ce");

    // Mock Serena failure
    jest.spyOn(clientManager, "getOrCreateClient").mockRejectedValue(
      new Error("Serena not available")
    );

    // Should still succeed
    const result = await initProject({ project_root: tmpDir });
    assert.equal(result.success, true);

    console.log("✅ Non-fatal Serena failure verified");
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});
```

**Success Criteria:**
- ✅ Serena activated with project path
- ✅ Non-fatal: warns if Serena unavailable
- ✅ Init continues on Serena failure
- ✅ Clear log messages
- ✅ Tests verify both success and failure paths

---

### Phase 6: Update init() Orchestration (30 minutes)

**Goal:** Integrate all phases into cohesive init flow

**File:** `syntropy-mcp/src/tools/init.ts`

**Final initProject() Flow:**
```typescript
export async function initProject(args: InitProjectArgs): Promise<InitProjectResult> {
  const projectRoot = path.resolve(args.project_root);

  try {
    console.error(`🚀 Initializing Context Engineering project: ${projectRoot}`);

    // Phase 1: Validate project root
    await validateProjectRoot(projectRoot);
    console.error(`✅ Project root validated`);

    // Phase 2: Check if already initialized
    if (isAlreadyInitialized(projectRoot)) {
      const layout = detectProjectLayout(projectRoot);
      return {
        success: true,
        message: "Project already initialized (skipped)",
        structure: ".ce/ (existing)",
        layout
      };
    }

    // Phase 3: Detect layout
    const layout = detectProjectLayout(projectRoot);
    console.error(`✅ Detected standard layout`);

    // Phase 4: Copy boilerplate (selective + RULES.md blending)
    await copyBoilerplate(projectRoot, layout);

    // Phase 5: Scaffold user structure
    await scaffoldUserStructure(projectRoot, layout);

    // Phase 6: Create CLAUDE.md if missing (before blending)
    await ensureCLAUDEmd(projectRoot, layout);

    // Phase 7: Blend RULES.md into CLAUDE.md
    await blendRulesIntoCLAUDEmd(projectRoot, layout);

    // Phase 8: Upsert slash commands
    await upsertSlashCommands(projectRoot, layout);

    // Phase 9: Activate Serena (non-fatal)
    await activateSerenaProject(projectRoot);

    console.error(`\n✅ Project initialization complete!`);
    console.error(`   - Boilerplate copied to ${layout.ceDir}/`);
    console.error(`   - User directories created`);
    console.error(`   - RULES.md blended into CLAUDE.md`);
    console.error(`   - Slash commands configured`);
    console.error(`   - Serena activated`);

    return {
      success: true,
      message: "Project initialized successfully",
      structure: ".ce/ (system) + PRPs/examples/ (user)",
      layout
    };
  } catch (error) {
    const message = (error as any)?.message || String(error);
    throw new Error(
      `Failed to initialize project: ${message}\n` +
      `🔧 Troubleshooting: Ensure directory is writable and syntropy/ce/ exists`
    );
  }
}
```

**Update Tests:**
```typescript
// Update existing test to verify full flow
test("initializes fresh project with all features", async () => {
  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
  try {
    const boilerplatePath = path.join(__dirname, "../../ce");
    process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

    const result = await initProject({ project_root: tmpDir });

    assert.equal(result.success, true);
    assert(result.message.includes("successfully"));

    // Verify all outcomes
    assert(await directoryExists(path.join(tmpDir, ".ce/PRPs/system")));
    assert(await directoryExists(path.join(tmpDir, ".serena")));  // Root
    assert(!await directoryExists(path.join(tmpDir, ".ce/.serena")));  // Not in .ce
    assert(await fileExists(path.join(tmpDir, "CLAUDE.md")));  // Blended
    assert(!await fileExists(path.join(tmpDir, ".ce/RULES.md")));  // Not copied
    assert(await fileExists(path.join(tmpDir, ".ce/config.yml")));  // Config in .ce

    console.log("✅ Full initialization flow verified");
  } finally {
    await fs.rm(tmpDir, { recursive: true, force: true });
  }
});
```

**Success Criteria:**
- ✅ All 9 phases orchestrated correctly
- ✅ Clear progress messages
- ✅ Comprehensive test coverage
- ✅ Error handling with troubleshooting

---

## 📋 Acceptance Criteria

**Must Have:**
- [ ] Boilerplate cleaned (README.md, drift-report.md, health-cache.json removed)
- [ ] Already-initialized detection working (3 marker files)
- [ ] Selective copying implemented (exception mappings)
- [ ] `.serena/` at project root (not `.ce/.serena/`)
- [ ] RULES.md blended into CLAUDE.md (no duplicates)
- [ ] Serena activated after init (non-fatal)
- [ ] Config files in `.ce/` (persistent configs only)
- [ ] All tests passing (100% coverage of new functions)
- [ ] Clear log messages throughout

**Nice to Have:**
- [ ] Configurable marker files (not hardcoded)
- [ ] Blending algorithm tunable (overlap threshold)
- [ ] Serena activation retry logic

**Out of Scope:**
- Custom boilerplate templates (single template only)
- Incremental updates (full init only)
- Multi-project initialization (one at a time)

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `syntropy-mcp/src/scanner.test.ts`
```typescript
describe("isAlreadyInitialized", () => {
  it("returns true when all markers exist", () => {
    // Setup: Create .ce/ with markers
    // Assert: Returns true
  });

  it("returns false when markers missing", () => {
    // Setup: Empty directory
    // Assert: Returns false
  });
});
```

**File:** `syntropy-mcp/src/tools/init.test.ts`
```typescript
describe("Selective Copy", () => {
  it("copies standard dirs to .ce/", async () => {});
  it("copies .serena/ to root", async () => {});
  it("copies config files to .ce/", async () => {});
  it("does not copy RULES.md directly", async () => {});
});

describe("RULES.md Blending", () => {
  it("blends unique rules into CLAUDE.md", async () => {});
  it("skips duplicate rules", async () => {});
  it("preserves CLAUDE.md style", async () => {});
  it("filters anti-pattern sections", async () => {});
});

describe("Serena Activation", () => {
  it("activates Serena with project path", async () => {});
  it("continues on Serena failure", async () => {});
});
```

### Integration Tests

```bash
# Full workflow
cd /tmp
syntropy_init_project test-project
cd test-project

# Verify structure
test -d .ce/PRPs/system && echo "✅ System PRPs"
test -d .serena && echo "✅ Serena at root"
test ! -d .ce/.serena && echo "✅ Serena NOT in .ce"
test -f CLAUDE.md && echo "✅ CLAUDE.md blended"
test ! -f .ce/RULES.md && echo "✅ RULES.md not copied"

# Verify idempotent
syntropy_init_project test-project  # Should skip
```

---

## 📚 Dependencies

**External:**
- Node.js 18+ (fs/promises)
- TypeScript

**Internal:**
- PRP-29.1 (init tool foundation)
- Syntropy MCP server (client manager for Serena)

**Files Modified:**
- `syntropy-mcp/ce/` (cleanup: delete 3 files)
- `syntropy-mcp/src/scanner.ts` (add `isAlreadyInitialized`)
- `syntropy-mcp/src/tools/init.ts` (selective copy, blending, Serena activation)
- `syntropy-mcp/src/scanner.test.ts` (add tests)
- `syntropy-mcp/src/tools/init.test.ts` (update tests)

---

## ⚠️ Risks & Mitigations

**Risk 1: RULES.md blending creates duplicates**
- **Mitigation:** Semantic matching with 70% keyword overlap threshold
- **Testing:** Explicit duplication test case

**Risk 2: Serena activation breaks init**
- **Mitigation:** Non-fatal error handling, clear warnings
- **Testing:** Test both success and failure paths

**Risk 3: Already-initialized detection false positive**
- **Mitigation:** Check 3 independent markers (not just one)
- **Testing:** Test partial initialization scenarios

**Risk 4: Selective copy misses critical files**
- **Mitigation:** Explicit file list, verification test
- **Testing:** Compare boilerplate vs target structure

---

## 📖 References

**Node.js Documentation:**
- fs/promises: https://nodejs.org/api/fs.html#promises-api

**Existing Patterns:**
- `syntropy-mcp/src/tools/init.ts` (PRP-29.1 foundation)
- `syntropy-mcp/src/scanner.ts` (layout detection)

**Related PRPs:**
- PRP-29.1: Init tool foundation (prerequisite)
- PRP-29.3: Knowledge indexing (future work)

---

## 🎯 Success Metrics

**Implementation:**
- Time to implement: 6-7 hours (estimated)
- Code coverage: 100% for new functions
- Test pass rate: 100%

**User Experience:**
- Zero re-initialization for existing projects
- Clear progress messages
- Non-fatal Serena activation

**Quality:**
- All error messages include 🔧 troubleshooting
- No fishy fallbacks
- KISS principles applied
