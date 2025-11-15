/**
 * Project Initialization Tool
 *
 * Implements syntropy_init_project MCP tool that initializes
 * Context Engineering project structure by delegating to Python implementation.
 */

import { execSync } from "child_process";
import { existsSync } from "fs";
import * as path from "path";
import { fileURLToPath } from "url";
import {
  detectProjectLayout,
  validateProjectRoot,
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
 * Delegates core initialization to Python implementation (uv run ce init-project),
 * then runs TypeScript-specific post-processing (Serena activation, knowledge indexing).
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

    // 2. Check if already initialized
    if (await isAlreadyInitialized(projectRoot)) {
      const layout = detectProjectLayout(projectRoot);
      console.error(`ℹ️  Project already initialized (skipping core installation)`);

      // Still run post-processing for re-init scenarios
      await runPostProcessing(projectRoot);

      return {
        success: true,
        message: "Project already initialized (ran post-processing)",
        structure: ".ce/ (existing)",
        layout
      };
    }

    // 3. Detect layout
    const layout = detectProjectLayout(projectRoot);
    console.error(`✅ Detected standard layout`);

    // 4. Call Python implementation for core initialization
    console.error(`\n📦 Running core initialization (Python)...`);

    // Find ctx-eng-plus tools directory
    const ctxEngTools = findCtxEngPlusTools();

    try {
      // Run: uv run ce init-project --target <project_root>
      const command = `uv run ce init-project ${projectRoot}`;
      execSync(command, {
        cwd: ctxEngTools,
        stdio: 'inherit', // Show Python output directly
        encoding: 'utf-8'
      });

      console.error(`✅ Core initialization complete`);
    } catch (error: any) {
      throw new Error(
        `Python initialization failed: ${error.message}\n` +
        `🔧 Troubleshooting:\n` +
        `   1. Ensure UV is installed: curl -LsSf https://astral.sh/uv/install.sh | sh\n` +
        `   2. Check that ctx-eng-plus repo is at expected location\n` +
        `   3. Verify ce-infrastructure.xml exists in .ce/\n` +
        `   4. Check log file: .ce/init-{timestamp}.log`
      );
    }

    // 5. Run post-processing (TypeScript-specific features)
    await runPostProcessing(projectRoot);

    console.error(`\n✅ Project initialization complete!`);
    console.error(`   - Core framework installed (Python)`);
    console.error(`   - Serena activated`);
    console.error(`   - Knowledge index created`);
    console.error(`   - Syntropy summary generated`);

    return {
      success: true,
      message: "Project initialized successfully",
      structure: ".ce/ (framework) + user content",
      layout
    };
  } catch (error) {
    const message = (error as any)?.message || String(error);
    throw new Error(
      `Failed to initialize project: ${message}\n` +
      `🔧 Troubleshooting: Check error details above`
    );
  }
}

/**
 * Find ctx-eng-plus tools directory.
 *
 * Tries:
 * 1. Environment variable CTX_ENG_PLUS_PATH
 * 2. Relative to syntropy-mcp (../../ctx-eng-plus/tools)
 * 3. Current working directory assumption
 */
function findCtxEngPlusTools(): string {
  // Strategy 1: Environment variable
  if (process.env.CTX_ENG_PLUS_PATH) {
    const toolsPath = path.join(process.env.CTX_ENG_PLUS_PATH, "tools");
    if (existsSync(toolsPath)) {
      return toolsPath;
    }
  }

  // Strategy 2: Relative to syntropy-mcp (development)
  const relativePath = path.join(__dirname, "../../../ctx-eng-plus/tools");
  if (existsSync(relativePath)) {
    return relativePath;
  }

  // Strategy 3: Current directory (fallback)
  const cwdPath = path.join(process.cwd(), "tools");
  if (existsSync(cwdPath)) {
    return cwdPath;
  }

  throw new Error(
    `ctx-eng-plus tools directory not found\n` +
    `🔧 Tried:\n` +
    `   1. CTX_ENG_PLUS_PATH env var: ${process.env.CTX_ENG_PLUS_PATH || '(not set)'}\n` +
    `   2. Relative: ${relativePath}\n` +
    `   3. CWD: ${cwdPath}\n` +
    `Set CTX_ENG_PLUS_PATH environment variable to ctx-eng-plus repo root`
  );
}

/**
 * Run post-processing steps (TypeScript-specific).
 */
async function runPostProcessing(projectRoot: string): Promise<void> {
  // 1. Activate Serena (non-fatal)
  await activateSerenaProject(projectRoot);

  // 2. Build knowledge index (non-fatal)
  await buildKnowledgeIndex(projectRoot);

  // 3. Generate and persist Syntropy summary (non-fatal)
  try {
    const summary = await generateSummary(projectRoot);
    await persistSummary(projectRoot, summary);
    const oneLiner = formatSummaryOneLine(summary);
    console.error(`\n📊 Syntropy Summary: ${oneLiner}`);
    console.error(`   - Saved to .ce/SYNTROPY-SUMMARY.md`);
  } catch (error: any) {
    console.error(`⚠️  Summary generation failed (non-fatal): ${error.message}`);
  }
}

/**
 * Activate Serena project (non-fatal).
 */
async function activateSerenaProject(projectRoot: string): Promise<void> {
  try {
    console.error(`\n🔍 Activating Serena project...`);

    const manager = getClientManager();
    const result = await manager.callTool("syn-serena", "activate_project", {
      project: projectRoot
    });

    if (result) {
      console.error(`✅ Serena activated: ${projectRoot}`);
    } else {
      console.error(`⚠️  Serena activation returned unexpected result`);
    }
  } catch (error: any) {
    console.error(`⚠️  Serena activation failed (non-fatal): ${error.message}`);
    console.error(`   Project init will continue without Serena activation`);
  }
}

/**
 * Build knowledge index (non-fatal).
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
    console.error(`⚠️  Knowledge indexing failed (non-fatal): ${error.message}`);
    console.error(`   Project init will continue without knowledge index`);
  }
}
