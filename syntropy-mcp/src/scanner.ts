/**
 * Project Layout Scanner
 *
 * Detects and validates Context Engineering project structure.
 * Provides information about where system content (.ce/) and user content
 * (PRPs/, examples/) are located.
 */

import * as fs from "fs/promises";
import * as path from "path";

/**
 * Project layout configuration.
 * Defines where system and user content should be located.
 */
export interface ProjectLayout {
  ceDir: string;            // ".ce" (system content)
  prpsDir: string;          // "PRPs" (user content)
  examplesDir: string;      // "examples" (user content)
  memoriesDir: string;      // ".serena/memories"
  claudeMd: string;         // "CLAUDE.md" location
  commandsDir: string;      // ".claude/commands"
}

/**
 * Detect standard Context Engineering project layout.
 *
 * Returns the standard layout configuration for a CE project.
 * This is deterministic - always returns the same structure.
 * The actual existence of directories is validated separately.
 */
export function detectProjectLayout(projectRoot: string): ProjectLayout {
  // Standard layout: .ce/ for system content, root for user
  return {
    ceDir: ".ce",                      // System content (boilerplate)
    prpsDir: "PRPs",                   // User PRPs (feature-requests/, executed/)
    examplesDir: "examples",           // User examples
    memoriesDir: ".serena/memories",   // Serena knowledge base
    claudeMd: "CLAUDE.md",             // Project guide
    commandsDir: ".claude/commands"    // Slash commands
  };
}

/**
 * Find CLAUDE.md location in project.
 *
 * Looks for CLAUDE.md in project root.
 * Returns the path if found, otherwise returns default location.
 */
export async function findCLAUDEmd(projectRoot: string): Promise<string> {
  const claudeMdPath = path.join(projectRoot, "CLAUDE.md");
  
  try {
    await fs.access(claudeMdPath);
    return claudeMdPath;
  } catch {
    // File doesn't exist - will be created during init
    return claudeMdPath;
  }
}

/**
 * Validate that project root is accessible and writable.
 *
 * Checks:
 * - Directory exists
 * - Is actually a directory (not a file)
 * - Is readable and writable
 *
 * Throws error with troubleshooting if validation fails.
 */
export async function validateProjectRoot(projectRoot: string): Promise<void> {
  try {
    const stats = await fs.stat(projectRoot);
    
    if (!stats.isDirectory()) {
      throw new Error(`Not a directory: ${projectRoot}`);
    }

    // Test write access by attempting to list directory
    await fs.readdir(projectRoot);
  } catch (error) {
    const message = (error as any)?.message || "Unknown error";
    throw new Error(
      `Invalid project root: ${projectRoot}\n` +
      `Error: ${message}\n` +
      `🔧 Troubleshooting: Ensure directory exists and is writable`
    );
  }
}

/**
 * Check if directory exists.
 */
export async function directoryExists(dirPath: string): Promise<boolean> {
  try {
    const stats = await fs.stat(dirPath);
    return stats.isDirectory();
  } catch {
    return false;
  }
}

/**
 * Check if file exists.
 */
export async function fileExists(filePath: string): Promise<boolean> {
  try {
    const stats = await fs.stat(filePath);
    return stats.isFile();
  } catch {
    return false;
  }
}

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
export async function isAlreadyInitialized(projectRoot: string): Promise<boolean> {
  const markers = [
    path.join(projectRoot, ".ce", "RULES.md"),
    path.join(projectRoot, ".ce", "PRPs", "system"),
    path.join(projectRoot, ".ce", "tools")
  ];

  const checks = await Promise.all(
    markers.map(async marker => {
      const isDir = await directoryExists(marker);
      const isFile = await fileExists(marker);
      return isDir || isFile;
    })
  );

  const allExist = checks.every(check => check);

  if (allExist) {
    console.error("✅ Project already initialized (.ce/ exists)");
    console.error("   Skipping initialization");
  }

  return allExist;
}
