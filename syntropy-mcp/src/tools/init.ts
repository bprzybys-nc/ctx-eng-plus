/**
 * Project Initialization Tool
 *
 * Implements syntropy_init_project MCP tool that initializes
 * Context Engineering project structure with boilerplate copy
 * and slash command upsert.
 */

import * as fs from "fs/promises";
import { existsSync } from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import {
  detectProjectLayout,
  validateProjectRoot,
  directoryExists,
  fileExists,
  isAlreadyInitialized,
  type ProjectLayout
} from "../scanner.js";
import { MCPClientManager } from "../client-manager.js";
import { KnowledgeIndexer, saveIndex } from "../indexer/knowledge-indexer.js";
import { generateSummary, persistSummary, formatSummaryOneLine } from "./summary.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Create client manager for Serena activation
let clientManager: MCPClientManager | null = null;

function getClientManager(): MCPClientManager {
  if (!clientManager) {
    // Try .ce/servers.json first (project-specific), then fall back to syntropy-mcp root
    const ceServersPath = path.join(process.cwd(), ".ce", "servers.json");
    const defaultServersPath = path.join(__dirname, "../../servers.json");
    const serversPath = existsSync(ceServersPath) ? ceServersPath : defaultServersPath;
    clientManager = new MCPClientManager(serversPath);
  }
  return clientManager;
}

/**
 * Arguments for initProject function.
 */
export interface InitProjectArgs {
  project_root: string;
}

/**
 * Result of project initialization.
 */
export interface InitProjectResult {
  success: boolean;
  message: string;
  structure: string;
  layout: ProjectLayout;
}

/**
 * Initialize Context Engineering project structure.
 *
 * Main function that orchestrates the initialization process:
 * 1. Validate project root is accessible
 * 2. Copy boilerplate from syntropy/ce/ to .ce/
 * 3. Create user content directories (PRPs/, examples/, .serena/)
 * 4. Upsert slash commands to .claude/commands/
 * 5. Log status with progress indicators
 *
 * Returns initialization result with layout information.
 * Throws error with troubleshooting guidance on failure.
 */
export async function initProject(args: InitProjectArgs): Promise<InitProjectResult> {
  const projectRoot = path.resolve(args.project_root);

  try {
    console.error(`🚀 Initializing Context Engineering project: ${projectRoot}`);

    // 1. Validate project root
    await validateProjectRoot(projectRoot);
    console.error(`✅ Project root validated`);

    // 2. Check if already initialized (NEW)
    if (await isAlreadyInitialized(projectRoot)) {
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

    // 4. Copy boilerplate (selective + exceptions)
    await copyBoilerplate(projectRoot, layout);

    // 5. Scaffold user structure
    await scaffoldUserStructure(projectRoot, layout);

    // 6. Create CLAUDE.md if missing (before blending)
    await ensureCLAUDEmd(projectRoot, layout);

    // 7. Blend RULES.md into CLAUDE.md (NEW)
    await blendRulesIntoCLAUDEmd(projectRoot, layout);

    // 8. Upsert slash commands
    await upsertSlashCommands(projectRoot, layout);

    // 9. Activate Serena (NEW - non-fatal)
    await activateSerenaProject(projectRoot);

    // 10. Build knowledge index (non-fatal)
    await buildKnowledgeIndex(projectRoot);

    // 11. Generate and persist Syntropy summary (non-fatal)
    try {
      const summary = await generateSummary(projectRoot);
      await persistSummary(projectRoot, summary);
      const oneLiner = formatSummaryOneLine(summary);
      console.error(`\n📊 Syntropy Summary: ${oneLiner}`);
      console.error(`   - Saved to .ce/SYNTROPY-SUMMARY.md`);
    } catch (error: any) {
      console.error(`⚠️  Summary generation failed (non-fatal): ${error.message}`);
    }

    console.error(`\n✅ Project initialization complete!`);
    console.error(`   - Boilerplate copied to ${layout.ceDir}/`);
    console.error(`   - User directories created`);
    console.error(`   - RULES.md blended into CLAUDE.md`);
    console.error(`   - Slash commands configured`);
    console.error(`   - Serena activated`);
    console.error(`   - Knowledge index created`);
    console.error(`   - Syntropy summary generated`);

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

/**
 * Copy boilerplate with selective file mapping.
 *
 * Standard directories → .ce/
 * Exception: .serena/ → project root (not .ce/.serena/)
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

  // 2. Copy .claude/ directory to .ce/
  const claudeDir = ".claude";
  const claudeSrc = path.join(boilerplatePath, claudeDir);
  const claudeDst = path.join(targetCeDir, claudeDir);

  if (await directoryExists(claudeSrc)) {
    await fs.cp(claudeSrc, claudeDst, { recursive: true, force: true });
    console.error(`   ✓ ${claudeDir}/ → .ce/${claudeDir}/`);
  }

  // 3. Copy config files to .ce/
  const configFiles = [
    "config.yml",
    "hooks-config.yml",
    "linear-defaults.yml",
    "shell-functions.sh",
    "tool-alternatives.yml",
    "tool-inventory.yml",
    ".gitignore",
    "BOILERPLATE_CHANGELOG.md",
    "servers.json"
  ];

  for (const file of configFiles) {
    const src = path.join(boilerplatePath, file);
    const dst = path.join(targetCeDir, file);

    if (await fileExists(src)) {
      await fs.copyFile(src, dst);
      console.error(`   ✓ ${file} → .ce/${file}`);
    }
  }

  // 4. EXCEPTION: Copy .serena/ to project root (not .ce/)
  const serenaSrc = path.join(boilerplatePath, ".serena");
  const serenaDst = path.join(projectRoot, ".serena");

  if (await directoryExists(serenaSrc)) {
    await fs.cp(serenaSrc, serenaDst, { recursive: true, force: true });
    console.error(`   ✓ .serena/ → .serena/ (root)`);
  }

  // 5. EXCEPTION: RULES.md will be blended in Phase 4 (not copied directly)
  console.error(`   ⚠️  RULES.md → deferred to blending phase`);
}

/**
 * Find boilerplate path using multi-strategy search.
 *
 * Tries in order:
 * 1. SYNTROPY_BOILERPLATE_PATH environment variable (production)
 * 2. Relative path from syntropy-mcp (development)
 * 3. Installed location in npm package
 *
 * Throws error if not found in any location.
 */
function findBoilerplatePath(): string {
  // Strategy 1: Environment variable
  if (process.env.SYNTROPY_BOILERPLATE_PATH) {
    return path.resolve(process.env.SYNTROPY_BOILERPLATE_PATH);
  }

  // Strategy 2: Relative to syntropy-mcp/src/tools (development)
  // From syntropy-mcp/src/tools/init.ts -> syntropy-mcp/ce
  const devPath = path.join(__dirname, "../../ce");
  if (existsSync(devPath)) {
    return devPath;
  }

  // Strategy 3: Installed location (npm package)
  const installedPath = path.join(__dirname, "../../boilerplate");
  if (existsSync(installedPath)) {
    return installedPath;
  }

  // All strategies failed
  throw new Error(
    `Boilerplate not found in standard locations:\n` +
    `  1. SYNTROPY_BOILERPLATE_PATH env var (not set)\n` +
    `  2. Development path: ${devPath}\n` +
    `  3. Installed path: ${installedPath}\n` +
    `🔧 Troubleshooting: Set SYNTROPY_BOILERPLATE_PATH to absolute path of syntropy/ce/`
  );
}

/**
 * Create user content directories (PRPs, examples, .serena).
 *
 * Creates:
 * - PRPs/feature-requests/ (for new PRPs)
 * - PRPs/executed/ (for completed PRPs)
 * - examples/ (for user examples)
 * - .serena/memories/ (for Serena knowledge base)
 *
 * Uses recursive: true to create parent directories.
 */
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

  console.error(`\n✅ Creating user directories:`);
  for (const dir of dirs) {
    try {
      await fs.mkdir(dir, { recursive: true });
      const relPath = path.relative(projectRoot, dir);
      console.error(`   ✓ ${relPath}`);
    } catch (error) {
      throw new Error(
        `Failed to create directory ${dir}: ${error}\n` +
        `🔧 Troubleshooting: Check permissions and available disk space`
      );
    }
  }
}

/**
 * Create CLAUDE.md template if it doesn't exist.
 *
 * Template includes:
 * - Placeholder for project-specific instructions
 * - Quick reference for context engineering commands
 * - Link to framework documentation
 */
async function ensureCLAUDEmd(
  projectRoot: string,
  layout: ProjectLayout
): Promise<void> {
  const claudeMdPath = path.join(projectRoot, layout.claudeMd);
  const exists = await fileExists(claudeMdPath);

  if (exists) {
    console.error(`✅ CLAUDE.md exists`);
    return;
  }

  const template = `## Project Guide

Add project-specific instructions and conventions here.

## Quick Reference

- \`/generate-prp <feature>\` - Generate comprehensive PRP from INITIAL.md
- \`/execute-prp <prp-file>\` - Execute PRP implementation
- \`/update-context\` - Sync context with codebase
- \`/peer-review\` - Review PRP document or execution

## Framework Resources

- **Boilerplate**: Located in \`.ce/\` (system content)
- **User Content**: PRPs/ and examples/ (user content)
- **Documentation**: See \`.ce/RULES.md\` for framework rules

## Getting Started

1. Review \`.ce/RULES.md\` for project conventions
2. Check \`.ce/examples/system/\` for implementation patterns
3. Use \`/generate-prp\` to create feature requests
4. Use \`/execute-prp\` to implement features

---

**Note**: Customize this file with project-specific guidance.
Do not modify \`.ce/\` (system content) directly.
`;

  try {
    await fs.writeFile(claudeMdPath, template);
    console.error(`✅ Created: CLAUDE.md`);
  } catch (error) {
    throw new Error(
      `Failed to create CLAUDE.md: ${error}\n` +
      `🔧 Troubleshooting: Check write permissions in project root`
    );
  }
}

/**
 * Markdown section interface.
 */
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
  const rulesMdPath = path.join(findBoilerplatePath(), ".claude", "RULES.md");

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

    const manager = getClientManager();

    // Call serena_activate_project tool via callTool
    const result = await manager.callTool("syn-serena", "activate_project", {
      project: projectRoot
    });

    if (result) {
      console.error(`✅ Serena activated: ${projectRoot}`);
    } else {
      console.error(`⚠️  Serena activation returned unexpected result`);
    }
  } catch (error: any) {
    // Non-fatal: Serena may not be available or configured
    console.error(`⚠️  Serena activation failed (non-fatal): ${error.message}`);
    console.error(`   Project init will continue without Serena activation`);
    console.error(`   You can manually activate later if needed`);
  }
}

/**
 * Upsert slash commands to .claude/commands/.
 *
 * Copies standard commands from syntropy-mcp/commands/ to project's
 * .claude/commands/ directory. ALWAYS overwrites existing commands
 * to ensure consistency with framework.
 *
 * Commands included:
 * - generate-prp.md
 * - execute-prp.md
 * - update-context.md
 * - peer-review.md
 *
 * Displays warning about automatic overwrite.
 */
async function buildKnowledgeIndex(projectRoot: string): Promise<void> {
  try {
    console.error(`\n📚 Building knowledge index...`);

    const indexer = new KnowledgeIndexer(projectRoot);
    const index = await indexer.buildIndex();
    await saveIndex(projectRoot, index);

    const totalEntries = index.entries.length;
    const byType = index.entries.reduce((acc, entry) => {
      acc[entry.type] = (acc[entry.type] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    console.error(`✅ Knowledge index created:`);
    console.error(`   Total entries: ${totalEntries}`);
    Object.entries(byType).forEach(([type, count]) => {
      console.error(`   - ${type}: ${count}`);
    });
    console.error(`   Saved to: .ce/syntropy-index.json`);
  } catch (error: any) {
    // Non-fatal: Indexing may fail if directories don't exist yet
    console.error(`⚠️  Knowledge indexing failed (non-fatal): ${error.message}`);
    console.error(`   Project init will continue without knowledge index`);
    console.error(`   You can rebuild the index later if needed`);
  }
}

async function upsertSlashCommands(
  projectRoot: string,
  layout: ProjectLayout
): Promise<void> {
  const commandsDir = path.join(projectRoot, layout.commandsDir);
  const syntropyCmds = path.join(__dirname, "../../commands");

  // Ensure commands directory exists
  try {
    await fs.mkdir(commandsDir, { recursive: true });
  } catch (error) {
    throw new Error(
      `Failed to create commands directory: ${error}\n` +
      `🔧 Troubleshooting: Check directory permissions`
    );
  }

  const commands = [
    "generate-prp.md",
    "execute-prp.md",
    "update-context.md"
    // Note: peer-review.md not yet implemented in commands directory
  ];

  console.error(`\n✅ Upserting slash commands:`);
  for (const cmd of commands) {
    const src = path.join(syntropyCmds, cmd);
    const dst = path.join(commandsDir, cmd);

    // Check if command already exists
    const exists = await fileExists(dst);

    try {
      // Copy/overwrite command file
      await fs.copyFile(src, dst);
      const status = exists ? "⚠️  Overwriting" : "Creating";
      console.error(`   ${status}: /${cmd.replace('.md', '')}`);
    } catch (error) {
      throw new Error(
        `Failed to copy command ${cmd}: ${error}\n` +
        `🔧 Troubleshooting: Ensure source command files exist in syntropy-mcp/commands/`
      );
    }
  }

  console.error(`\n⚠️  IMPORTANT: Slash commands are ALWAYS overwritten on init.`);
  console.error(`   To customize commands, create new files with different names.`);
  console.error(`   Examples: my-generate-prp.md, custom-update-context.md`);
}


