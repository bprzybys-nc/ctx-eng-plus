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
  type ProjectLayout
} from "../scanner.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

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

    // 2. Detect layout
    const layout = detectProjectLayout(projectRoot);
    console.error(`✅ Detected standard layout`);

    // 3. Copy boilerplate
    await copyBoilerplate(projectRoot, layout);

    // 4. Scaffold user structure
    await scaffoldUserStructure(projectRoot, layout);

    // 5. Create CLAUDE.md if missing
    await ensureCLAUDEmd(projectRoot, layout);

    // 6. Upsert slash commands
    await upsertSlashCommands(projectRoot, layout);

    console.error(`\n✅ Project initialization complete!`);
    console.error(`   - Boilerplate copied to ${layout.ceDir}/`);
    console.error(`   - User directories created`);
    console.error(`   - Slash commands configured`);
    console.error(`   - CLAUDE.md ready for customization`);

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
 * Copy boilerplate from syntropy/ce/ to project .ce/.
 *
 * Strategy for finding boilerplate:
 * 1. Environment variable: SYNTROPY_BOILERPLATE_PATH
 * 2. Relative to syntropy-mcp (development)
 * 3. Installed location (npm package)
 *
 * Uses force: true to overwrite if .ce/ already exists.
 */
async function copyBoilerplate(
  projectRoot: string,
  layout: ProjectLayout
): Promise<void> {
  // Find boilerplate source
  const boilerplatePath = findBoilerplatePath();

  // Verify source exists
  const sourceExists = await directoryExists(boilerplatePath);
  if (!sourceExists) {
    throw new Error(
      `Boilerplate not found: ${boilerplatePath}\n` +
      `🔧 Troubleshooting: Set SYNTROPY_BOILERPLATE_PATH env variable or ensure ctx-eng-plus repository is available`
    );
  }

  const targetCeDir = path.join(projectRoot, layout.ceDir);

  // Copy entire syntropy/ce/ to .ce/
  try {
    await fs.cp(boilerplatePath, targetCeDir, {
      recursive: true,
      force: true  // Overwrite if exists
    });

    console.error(`✅ Copied boilerplate to ${layout.ceDir}/`);
    console.error(`   - PRPs/system/ (PRP-1-28 + templates)`);
    console.error(`   - examples/system/ (model + patterns)`);
    console.error(`   - tools/ (CE CLI)`);
    console.error(`   - .serena/ (project memories)`);
    console.error(`   - RULES.md (framework rules)`);
  } catch (error) {
    throw new Error(
      `Failed to copy boilerplate to ${targetCeDir}: ${error}\n` +
      `🔧 Troubleshooting: Check file permissions and disk space`
    );
  }
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
  // From syntropy-mcp/src/tools/init.ts -> syntropy/ce
  const devPath = path.join(__dirname, "../../../../syntropy/ce");
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

  const template = `# Project Guide

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


