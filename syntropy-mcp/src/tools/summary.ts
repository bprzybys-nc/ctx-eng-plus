/**
 * Syntropy MCP Summary Tool
 *
 * Generates compact, readable summaries of the Syntropy MCP system
 * for bash execution and documentation persistence.
 */

import * as fs from "fs/promises";
import * as path from "path";

interface SyntropyInfo {
  version: string;
  server_count: number;
  tool_count: number;
  eager_servers: string[];
  lazy_servers: string[];
}

interface SyntropySummary {
  title: string;
  description: string;
  architecture: {
    purpose: string;
    pattern: string;
    routing: string;
  };
  servers: {
    total: number;
    eager: string[];
    lazy: string[];
  };
  tools: {
    total: number;
    categories: Record<string, number>;
  };
  usage: {
    tool_format: string;
    example: string;
  };
  documentation: string;
}

/**
 * Get Syntropy system information
 */
async function getSyntropyInfo(projectRoot: string): Promise<SyntropyInfo> {
  const serversJsonPath = path.join(projectRoot, ".ce", "servers.json");

  try {
    const content = await fs.readFile(serversJsonPath, "utf-8");
    const serversConfig = JSON.parse(content);

    const eagerServers = Object.keys(serversConfig)
      .filter(key => serversConfig[key].eager === true);

    const lazyServers = Object.keys(serversConfig)
      .filter(key => !serversConfig[key].eager);

    return {
      version: "0.1.0",
      server_count: Object.keys(serversConfig).length,
      tool_count: 78, // Approximate from current implementation
      eager_servers: eagerServers,
      lazy_servers: lazyServers
    };
  } catch (error) {
    throw new Error(`Failed to read servers.json\n🔧 Troubleshooting: Ensure project is initialized with /syntropy-init`);
  }
}

/**
 * Generate compact summary
 */
export async function generateSummary(projectRoot: string): Promise<SyntropySummary> {
  const info = await getSyntropyInfo(projectRoot);

  return {
    title: "Syntropy MCP - Unified Tool Aggregation Layer",
    description: "Routes tool calls to underlying MCP servers with unified namespace and health monitoring",
    architecture: {
      purpose: "Aggregate 9 specialized MCP servers into single interface",
      pattern: "Tool routing with format: mcp__syntropy_<server>_<tool>",
      routing: "Parse tool name → validate → forward to underlying server"
    },
    servers: {
      total: info.server_count,
      eager: info.eager_servers,
      lazy: info.lazy_servers
    },
    tools: {
      total: info.tool_count,
      categories: {
        "Code Navigation (Serena)": 28,
        "Filesystem Operations": 14,
        "Git Version Control": 12,
        "GitHub Integration": 23,
        "Linear Project Management": 5,
        "Documentation (Context7)": 2,
        "Sequential Thinking": 1,
        "Codebase Analysis (Repomix)": 1,
        "Perplexity Search": 1,
        "Health & Init": 2
      }
    },
    usage: {
      tool_format: "mcp__syntropy_<server>_<tool_name>",
      example: "mcp__syntropy_serena_find_symbol"
    },
    documentation: "See CLAUDE.md for detailed usage, .ce/servers.json for configuration"
  };
}

/**
 * Format summary as compact readable text
 */
export function formatSummaryText(summary: SyntropySummary): string {
  const lines: string[] = [];

  lines.push(`# ${summary.title}`);
  lines.push("");
  lines.push(`**Description**: ${summary.description}`);
  lines.push("");

  lines.push("## Architecture");
  lines.push(`- **Purpose**: ${summary.architecture.purpose}`);
  lines.push(`- **Pattern**: ${summary.architecture.pattern}`);
  lines.push(`- **Routing**: ${summary.architecture.routing}`);
  lines.push("");

  lines.push("## Servers");
  lines.push(`- **Total**: ${summary.servers.total}`);
  lines.push(`- **Eager** (load on start): ${summary.servers.eager.join(", ")}`);
  lines.push(`- **Lazy** (load on demand): ${summary.servers.lazy.join(", ")}`);
  lines.push("");

  lines.push("## Tools");
  lines.push(`- **Total**: ${summary.tools.total} tools across ${Object.keys(summary.tools.categories).length} categories`);
  Object.entries(summary.tools.categories).forEach(([category, count]) => {
    lines.push(`  - ${category}: ${count} tools`);
  });
  lines.push("");

  lines.push("## Usage");
  lines.push(`- **Format**: \`${summary.usage.tool_format}\``);
  lines.push(`- **Example**: \`${summary.usage.example}\``);
  lines.push("");

  lines.push(`**Documentation**: ${summary.documentation}`);

  return lines.join("\n");
}

/**
 * Format summary as compact one-liner for bash
 */
export function formatSummaryOneLine(summary: SyntropySummary): string {
  return `Syntropy MCP v0.1.0: ${summary.servers.total} servers (${summary.servers.eager.length} eager), ${summary.tools.total} tools, routing format: ${summary.usage.tool_format}`;
}

/**
 * Persist summary to documentation
 */
export async function persistSummary(projectRoot: string, summary: SyntropySummary): Promise<void> {
  // Save full summary to .ce/
  const summaryPath = path.join(projectRoot, ".ce", "SYNTROPY-SUMMARY.md");
  const content = formatSummaryText(summary);
  await fs.writeFile(summaryPath, content, "utf-8");

  // Update CLAUDE.md with compact one-liner at the top
  const claudeMdPath = path.join(projectRoot, "CLAUDE.md");
  try {
    const claudeContent = await fs.readFile(claudeMdPath, "utf-8");
    const oneLiner = formatSummaryOneLine(summary);

    // Check if summary section exists
    if (claudeContent.includes("## Syntropy MCP Summary")) {
      // Replace existing summary
      const updated = claudeContent.replace(
        /## Syntropy MCP Summary\n\n\*\*Syntropy MCP.*?\n\n/s,
        `## Syntropy MCP Summary\n\n**${oneLiner}**\n\n`
      );
      await fs.writeFile(claudeMdPath, updated, "utf-8");
    } else {
      // Add summary section at the top (after any front matter)
      const lines = claudeContent.split("\n");
      let insertIndex = 0;

      // Skip front matter if exists
      if (lines[0] === "---") {
        insertIndex = lines.findIndex((line, i) => i > 0 && line === "---") + 1;
      }

      lines.splice(
        insertIndex,
        0,
        "## Syntropy MCP Summary",
        "",
        `**${oneLiner}**`,
        ""
      );

      await fs.writeFile(claudeMdPath, lines.join("\n"), "utf-8");
    }
  } catch (error) {
    // Non-fatal - CLAUDE.md might not exist yet
    console.error(`⚠️  Could not update CLAUDE.md: ${error}`);
  }
}

/**
 * MCP Tool: Get Syntropy summary
 */
export async function getSyntropySummary(args: {
  project_root: string;
  format?: "text" | "oneline" | "json";
}): Promise<{ success: boolean; summary?: string; error?: string }> {
  try {
    const { project_root, format = "text" } = args;

    const summary = await generateSummary(project_root);

    let output: string;
    switch (format) {
      case "oneline":
        output = formatSummaryOneLine(summary);
        break;
      case "json":
        output = JSON.stringify(summary, null, 2);
        break;
      default:
        output = formatSummaryText(summary);
    }

    // Persist to .ce/SYNTROPY-SUMMARY.md
    await persistSummary(project_root, summary);

    return {
      success: true,
      summary: output
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}
