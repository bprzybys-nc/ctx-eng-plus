/**
 * Knowledge Indexer - Scans and indexes all project knowledge sources
 * 
 * Scans:
 * - Framework docs (.ce/)
 * - PRPs (PRPs/executed, PRPs/feature-requests)
 * - Examples (examples/)
 * - Serena memories (.serena/memories/)
 */

import * as fs from "fs/promises";
import * as path from "path";
import { KnowledgeIndex, IndexEntry, PatternEntry, PRPEntry, MemoryEntry, RuleEntry, ExampleEntry, ResearchEntry } from "../types/knowledge-index.js";

const INDEX_VERSION = "1.0.0";

export class KnowledgeIndexer {
  private projectRoot: string;
  private entries: IndexEntry[] = [];

  constructor(projectRoot: string) {
    this.projectRoot = projectRoot;
  }

  /**
   * Scan all knowledge sources and build index
   */
  async buildIndex(): Promise<KnowledgeIndex> {
    this.entries = [];

    // Scan each knowledge source
    await this.scanFrameworkDocs();
    await this.scanPRPs();
    await this.scanExamples();
    await this.scanMemories();
    await this.scanResearchDocs();

    return {
      version: INDEX_VERSION,
      last_updated: new Date().toISOString(),
      entries: this.entries
    };
  }

  /**
   * Scan framework documentation in .ce/
   */
  private async scanFrameworkDocs(): Promise<void> {
    const ceDir = path.join(this.projectRoot, ".ce");
    
    try {
      const exists = await fs.stat(ceDir).then(() => true).catch(() => false);
      if (!exists) return;

      // Scan for markdown files
      await this.scanDirectory(ceDir, async (filePath, relativePath) => {
        if (!filePath.endsWith(".md")) return;

        const content = await fs.readFile(filePath, "utf-8");
        const excerpt = this.extractExcerpt(content);
        const tags = this.extractTags(content, filePath);

        // Determine if it's a rule or pattern
        const isRule = relativePath.includes("RULES") || relativePath.includes("standards");
        
        if (isRule) {
          this.entries.push({
            id: this.generateId("rule", relativePath),
            type: "rule",
            title: this.extractTitle(content, relativePath),
            excerpt,
            path: relativePath,
            tags,
            rule_category: this.categorizeRule(content),
            enforcement_level: this.determineEnforcementLevel(content)
          } as RuleEntry);
        } else {
          this.entries.push({
            id: this.generateId("pattern", relativePath),
            type: "pattern",
            title: this.extractTitle(content, relativePath),
            excerpt,
            path: relativePath,
            tags,
            category: this.categorizePattern(content, relativePath),
            language: this.detectLanguage(filePath)
          } as PatternEntry);
        }
      });
    } catch (error) {
      console.warn(`Failed to scan framework docs: ${error}`);
    }
  }

  /**
   * Scan PRPs in PRPs/executed and PRPs/feature-requests
   */
  private async scanPRPs(): Promise<void> {
    const prpsDir = path.join(this.projectRoot, "PRPs");
    
    try {
      const exists = await fs.stat(prpsDir).then(() => true).catch(() => false);
      if (!exists) return;

      for (const subdir of ["executed", "feature-requests"]) {
        const dir = path.join(prpsDir, subdir);
        const dirExists = await fs.stat(dir).then(() => true).catch(() => false);
        if (!dirExists) continue;

        await this.scanDirectory(dir, async (filePath, relativePath) => {
          if (!filePath.endsWith(".md")) return;

          const content = await fs.readFile(filePath, "utf-8");
          const prpId = this.extractPRPId(relativePath);
          const tags = this.extractTags(content, filePath);
          const issueId = this.extractIssueId(content);

          this.entries.push({
            id: this.generateId("prp", relativePath),
            type: "prp",
            title: this.extractTitle(content, relativePath),
            excerpt: this.extractExcerpt(content),
            path: relativePath,
            tags,
            prp_id: prpId,
            status: subdir as "executed" | "feature-request",
            issue_id: issueId
          } as PRPEntry);
        });
      }
    } catch (error) {
      console.warn(`Failed to scan PRPs: ${error}`);
    }
  }

  /**
   * Scan examples directory
   */
  private async scanExamples(): Promise<void> {
    const examplesDir = path.join(this.projectRoot, "examples");
    
    try {
      const exists = await fs.stat(examplesDir).then(() => true).catch(() => false);
      if (!exists) return;

      await this.scanDirectory(examplesDir, async (filePath, relativePath) => {
        const content = await fs.readFile(filePath, "utf-8");
        const excerpt = this.extractExcerpt(content);
        const tags = this.extractTags(content, filePath);

        this.entries.push({
          id: this.generateId("example", relativePath),
          type: "example",
          title: this.extractTitle(content, relativePath),
          excerpt,
          path: relativePath,
          tags,
          example_type: this.categorizeExample(relativePath),
          language: this.detectLanguage(filePath),
          framework: this.detectFramework(content)
        } as ExampleEntry);
      });
    } catch (error) {
      console.warn(`Failed to scan examples: ${error}`);
    }
  }

  /**
   * Scan Serena memories in .serena/memories/
   */
  private async scanMemories(): Promise<void> {
    const memoriesDir = path.join(this.projectRoot, ".serena/memories");

    try {
      const exists = await fs.stat(memoriesDir).then(() => true).catch(() => false);
      if (!exists) return;

      await this.scanDirectory(memoriesDir, async (filePath, relativePath) => {
        if (!filePath.endsWith(".md")) return;

        const content = await fs.readFile(filePath, "utf-8");
        const tags = this.extractTags(content, filePath);

        this.entries.push({
          id: this.generateId("memory", relativePath),
          type: "memory",
          title: this.extractTitle(content, relativePath),
          excerpt: this.extractExcerpt(content),
          path: relativePath,
          tags,
          memory_type: this.extractMemoryType(relativePath, content),
          context: this.extractMemoryContext(content)
        } as MemoryEntry);
      });
    } catch (error) {
      console.warn(`Failed to scan memories: ${error}`);
    }
  }

  /**
   * Scan research docs in docs/research/
   */
  private async scanResearchDocs(): Promise<void> {
    const researchDir = path.join(this.projectRoot, "docs/research");

    try {
      const exists = await fs.stat(researchDir).then(() => true).catch(() => false);
      if (!exists) return;

      await this.scanDirectory(researchDir, async (filePath, relativePath) => {
        if (!filePath.endsWith(".md")) return;

        const content = await fs.readFile(filePath, "utf-8");
        const tags = this.extractTags(content, filePath);
        const yamlData = this.extractYAMLFrontmatter(content);

        this.entries.push({
          id: this.generateId("research", relativePath),
          type: "research",
          title: this.extractTitle(content, relativePath),
          excerpt: this.extractExcerpt(content),
          path: relativePath,
          tags,
          source: yamlData.source || "unknown",
          category: yamlData.category,
          denoise_status: yamlData.denoise_status,
          kb_integration: yamlData.kb_integration
        } as ResearchEntry);
      });
    } catch (error) {
      console.warn(`Failed to scan research docs: ${error}`);
    }
  }

  /**
   * Recursively scan directory and apply handler to each file
   */
  private async scanDirectory(
    dir: string,
    handler: (filePath: string, relativePath: string) => Promise<void>
  ): Promise<void> {
    const entries = await fs.readdir(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);
      
      if (entry.isDirectory()) {
        await this.scanDirectory(fullPath, handler);
      } else if (entry.isFile()) {
        const relativePath = path.relative(this.projectRoot, fullPath);
        await handler(fullPath, relativePath);
      }
    }
  }

  /**
   * Extract first 200 chars as excerpt
   */
  private extractExcerpt(content: string): string {
    // Remove YAML frontmatter
    const withoutYaml = content.replace(/^---\n[\s\S]*?\n---\n/, "");
    
    // Remove markdown headers and extract plain text
    const plainText = withoutYaml
      .replace(/^#+\s+/gm, "")
      .replace(/\*\*/g, "")
      .replace(/\*/g, "")
      .trim();

    return plainText.substring(0, 200).replace(/\n+/g, " ");
  }

  /**
   * Extract title from content or filename
   */
  private extractTitle(content: string, relativePath: string): string {
    // Try to find first # header
    const match = content.match(/^#\s+(.+)$/m);
    if (match) return match[1].trim();

    // Fallback to filename
    const filename = path.basename(relativePath, path.extname(relativePath));
    return filename.replace(/[-_]/g, " ");
  }

  /**
   * Extract tags from content and filepath
   */
  private extractTags(content: string, filePath: string): string[] {
    const tags: string[] = [];

    // Extract from path segments
    const segments = filePath.split(path.sep);
    tags.push(...segments.filter(s => s.length > 2));

    // Extract from YAML frontmatter
    const yamlMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (yamlMatch) {
      const tagsMatch = yamlMatch[1].match(/tags:\s*\[([^\]]+)\]/);
      if (tagsMatch) {
        tags.push(...tagsMatch[1].split(",").map(t => t.trim()));
      }
    }

    // Extract from headers (##, ###)
    const headers = content.match(/^#{2,3}\s+(.+)$/gm) || [];
    tags.push(...headers.map(h => h.replace(/^#+\s+/, "").toLowerCase()));

    return [...new Set(tags)]; // Deduplicate
  }

  /**
   * Generate unique ID for entry
   */
  private generateId(type: string, relativePath: string): string {
    return `${type}-${relativePath.replace(/[^a-z0-9]/gi, "-")}`;
  }

  /**
   * Extract PRP ID from filename (e.g., "PRP-29.3" from "PRP-29.3-feature.md")
   */
  private extractPRPId(relativePath: string): string {
    const match = path.basename(relativePath).match(/PRP-\d+(\.\d+)?/);
    return match ? match[0] : "";
  }

  /**
   * Extract Linear issue ID from YAML frontmatter
   */
  private extractIssueId(content: string): string | undefined {
    const match = content.match(/^issue:\s*(.+)$/m);
    return match ? match[1].trim() : undefined;
  }

  /**
   * Categorize rule by analyzing content
   */
  private categorizeRule(content: string): RuleEntry["rule_category"] {
    const lower = content.toLowerCase();
    if (lower.includes("test") || lower.includes("tdd")) return "testing";
    if (lower.includes("workflow") || lower.includes("process")) return "workflow";
    if (lower.includes("communication") || lower.includes("style")) return "communication";
    return "code-quality";
  }

  /**
   * Determine enforcement level from content
   */
  private determineEnforcementLevel(content: string): RuleEntry["enforcement_level"] {
    const lower = content.toLowerCase();
    if (lower.includes("mandatory") || lower.includes("must") || lower.includes("required")) {
      return "mandatory";
    }
    if (lower.includes("recommended") || lower.includes("should")) {
      return "recommended";
    }
    return "guideline";
  }

  /**
   * Categorize pattern by path and content
   */
  private categorizePattern(content: string, relativePath: string): PatternEntry["category"] {
    const lower = content.toLowerCase() + relativePath.toLowerCase();
    if (lower.includes("test")) return "testing";
    if (lower.includes("architect")) return "architecture";
    if (lower.includes("workflow") || lower.includes("process")) return "workflow";
    return "code";
  }

  /**
   * Categorize example by path
   */
  private categorizeExample(relativePath: string): ExampleEntry["example_type"] {
    const lower = relativePath.toLowerCase();
    if (lower.includes("config") || lower.endsWith(".json") || lower.endsWith(".yml")) {
      return "config";
    }
    if (lower.includes("workflow") || lower.includes("process")) {
      return "workflow";
    }
    if (lower.endsWith(".md")) {
      return "documentation";
    }
    return "code";
  }

  /**
   * Detect programming language from file extension
   */
  private detectLanguage(filePath: string): string | undefined {
    const ext = path.extname(filePath).toLowerCase();
    const langMap: Record<string, string> = {
      ".ts": "typescript",
      ".js": "javascript",
      ".py": "python",
      ".go": "go",
      ".rs": "rust",
      ".java": "java"
    };
    return langMap[ext];
  }

  /**
   * Detect framework from content
   */
  private detectFramework(content: string): string | undefined {
    const lower = content.toLowerCase();
    if (lower.includes("fastapi")) return "fastapi";
    if (lower.includes("django")) return "django";
    if (lower.includes("react")) return "react";
    if (lower.includes("next.js")) return "nextjs";
    return undefined;
  }

  /**
   * Extract memory type from filename or content
   */
  private extractMemoryType(relativePath: string, content: string): string {
    const filename = path.basename(relativePath, ".md");
    
    // Check for common patterns
    if (filename.includes("architecture")) return "architecture";
    if (filename.includes("pattern")) return "pattern";
    if (filename.includes("note")) return "note";
    
    // Check content
    const lower = content.toLowerCase();
    if (lower.includes("architecture")) return "architecture";
    if (lower.includes("pattern")) return "pattern";
    
    return "note";
  }

  /**
   * Extract context hint from memory content
   */
  private extractMemoryContext(content: string): string | undefined {
    // Look for context markers in first 500 chars
    const preview = content.substring(0, 500);
    const match = preview.match(/context:\s*(.+)/i);
    return match ? match[1].trim() : undefined;
  }

  /**
   * Extract YAML frontmatter from content
   */
  private extractYAMLFrontmatter(content: string): Record<string, any> {
    const match = content.match(/^---\n([\s\S]*?)\n---/);
    if (!match) return {};

    const yamlContent = match[1];
    const result: Record<string, any> = {};

    // Parse simple YAML key-value pairs
    const lines = yamlContent.split("\n");
    for (const line of lines) {
      if (!line.trim()) continue;

      // Handle key: value pairs
      const keyMatch = line.match(/^(\w+):\s*(.+)$/);
      if (keyMatch) {
        const key = keyMatch[1];
        let value: any = keyMatch[2].trim();

        // Parse quoted strings
        if (value.startsWith('"') && value.endsWith('"')) {
          value = value.slice(1, -1);
        } else if (value.startsWith("'") && value.endsWith("'")) {
          value = value.slice(1, -1);
        }
        // Parse arrays
        else if (value.startsWith("[") && value.endsWith("]")) {
          value = value
            .slice(1, -1)
            .split(",")
            .map((v: string) => v.trim());
        }

        result[key] = value;
      }
    }

    return result;
  }
}

/**
 * Save index to .ce/syntropy-index.json
 */
export async function saveIndex(projectRoot: string, index: KnowledgeIndex): Promise<void> {
  const indexPath = path.join(projectRoot, ".ce/syntropy-index.json");
  await fs.writeFile(indexPath, JSON.stringify(index, null, 2), "utf-8");
}

/**
 * Load index from .ce/syntropy-index.json
 */
export async function loadIndex(projectRoot: string): Promise<KnowledgeIndex | null> {
  const indexPath = path.join(projectRoot, ".ce/syntropy-index.json");
  
  try {
    const content = await fs.readFile(indexPath, "utf-8");
    return JSON.parse(content);
  } catch {
    return null;
  }
}
