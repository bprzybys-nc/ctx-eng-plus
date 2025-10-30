/**
 * Knowledge Query Tools
 * 
 * Provides MCP tools for querying the unified knowledge index:
 * - syntropy_get_system_doc: Access framework docs from .ce/
 * - syntropy_get_user_doc: Access project docs from root
 * - syntropy_knowledge_search: Search across all knowledge sources
 */

import * as fs from "fs/promises";
import * as path from "path";
import { KnowledgeIndex, IndexEntry, SearchResult, KnowledgeSearchQuery } from "../types/knowledge-index.js";
import { loadIndex } from "../indexer/knowledge-indexer.js";

/**
 * Get system documentation from .ce/ directory
 */
export async function getSystemDoc(args: { 
  project_root: string;
  doc_path: string;
}): Promise<{ success: boolean; content?: string; error?: string }> {
  try {
    const { project_root, doc_path } = args;
    
    // Ensure path is within .ce/
    const fullPath = path.join(project_root, ".ce", doc_path);
    const resolvedPath = path.resolve(fullPath);
    const ceDir = path.resolve(project_root, ".ce");
    
    if (!resolvedPath.startsWith(ceDir)) {
      throw new Error(`Path must be within .ce/ directory\n🔧 Troubleshooting: Use relative paths like 'RULES.md' or 'examples/patterns.md'`);
    }

    // Check file exists
    const exists = await fs.stat(resolvedPath).then(() => true).catch(() => false);
    if (!exists) {
      throw new Error(`Document not found: ${doc_path}\n🔧 Troubleshooting: Use /syntropy-health to check if index is up to date`);
    }

    // Read content
    const content = await fs.readFile(resolvedPath, "utf-8");
    
    return {
      success: true,
      content
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * Get user documentation from project root
 */
export async function getUserDoc(args: {
  project_root: string;
  doc_path: string;
}): Promise<{ success: boolean; content?: string; error?: string }> {
  try {
    const { project_root, doc_path } = args;
    
    // Ensure path is NOT within .ce/ (user docs only)
    const fullPath = path.join(project_root, doc_path);
    const resolvedPath = path.resolve(fullPath);
    const projectRoot = path.resolve(project_root);
    const ceDir = path.resolve(project_root, ".ce");
    
    if (!resolvedPath.startsWith(projectRoot)) {
      throw new Error(`Path must be within project root\n🔧 Troubleshooting: Use relative paths like 'README.md' or 'docs/api.md'`);
    }
    
    if (resolvedPath.startsWith(ceDir)) {
      throw new Error(`Use syntropy_get_system_doc for .ce/ files\n🔧 Troubleshooting: This tool is for user docs only (PRPs, examples, etc.)`);
    }

    // Check file exists
    const exists = await fs.stat(resolvedPath).then(() => true).catch(() => false);
    if (!exists) {
      throw new Error(`Document not found: ${doc_path}\n🔧 Troubleshooting: Check path or use knowledge_search to find it`);
    }

    // Read content
    const content = await fs.readFile(resolvedPath, "utf-8");
    
    return {
      success: true,
      content
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * Search across all knowledge sources using the index
 */
export async function knowledgeSearch(args: KnowledgeSearchQuery & { project_root: string }): Promise<{
  success: boolean;
  results?: SearchResult[];
  total?: number;
  error?: string;
}> {
  try {
    const { project_root, query, types, tags, limit = 10 } = args;
    
    // Load index
    const index = await loadIndex(project_root);
    if (!index) {
      throw new Error(`Knowledge index not found\n🔧 Troubleshooting: Run init tool to create index, or check .ce/syntropy-index.json exists`);
    }

    // Filter by type if specified
    let entries = index.entries;
    if (types && types.length > 0) {
      entries = entries.filter(e => types.includes(e.type));
    }

    // Filter by tags if specified
    if (tags && tags.length > 0) {
      entries = entries.filter(e => 
        tags.some(tag => e.tags.includes(tag))
      );
    }

    // Score and rank results
    const scoredResults = entries
      .map(entry => ({
        entry,
        score: calculateRelevance(entry, query),
        match_reason: explainMatch(entry, query)
      }))
      .filter(r => r.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);

    return {
      success: true,
      results: scoredResults,
      total: scoredResults.length
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}

/**
 * Calculate relevance score for an entry
 */
function calculateRelevance(entry: IndexEntry, query: string): number {
  const lowerQuery = query.toLowerCase();
  const queryTerms = lowerQuery.split(/\s+/);
  
  let score = 0;

  // Title exact match: +50
  if (entry.title.toLowerCase().includes(lowerQuery)) {
    score += 50;
  }

  // Title term matches: +10 each
  queryTerms.forEach(term => {
    if (entry.title.toLowerCase().includes(term)) {
      score += 10;
    }
  });

  // Excerpt matches: +5 each
  queryTerms.forEach(term => {
    if (entry.excerpt.toLowerCase().includes(term)) {
      score += 5;
    }
  });

  // Tag exact match: +20 each
  entry.tags.forEach(tag => {
    if (tag.toLowerCase() === lowerQuery) {
      score += 20;
    }
  });

  // Tag partial match: +10 each
  entry.tags.forEach(tag => {
    queryTerms.forEach(term => {
      if (tag.toLowerCase().includes(term)) {
        score += 10;
      }
    });
  });

  // Path match: +5
  if (entry.path.toLowerCase().includes(lowerQuery)) {
    score += 5;
  }

  return score;
}

/**
 * Explain why an entry matched the query
 */
function explainMatch(entry: IndexEntry, query: string): string {
  const reasons: string[] = [];
  const lowerQuery = query.toLowerCase();
  
  if (entry.title.toLowerCase().includes(lowerQuery)) {
    reasons.push("title match");
  }
  
  if (entry.excerpt.toLowerCase().includes(lowerQuery)) {
    reasons.push("excerpt match");
  }
  
  const matchedTags = entry.tags.filter(tag => 
    tag.toLowerCase().includes(lowerQuery)
  );
  if (matchedTags.length > 0) {
    reasons.push(`tags: ${matchedTags.join(", ")}`);
  }
  
  if (entry.path.toLowerCase().includes(lowerQuery)) {
    reasons.push("path match");
  }

  return reasons.length > 0 ? reasons.join(", ") : "partial match";
}

/**
 * Get index statistics
 */
export async function getIndexStats(project_root: string): Promise<{
  success: boolean;
  stats?: {
    total_entries: number;
    by_type: Record<string, number>;
    last_updated: string;
  };
  error?: string;
}> {
  try {
    const index = await loadIndex(project_root);
    if (!index) {
      throw new Error(`Knowledge index not found\n🔧 Troubleshooting: Run init tool to create index`);
    }

    const byType: Record<string, number> = {};
    index.entries.forEach(entry => {
      byType[entry.type] = (byType[entry.type] || 0) + 1;
    });

    return {
      success: true,
      stats: {
        total_entries: index.entries.length,
        by_type: byType,
        last_updated: index.last_updated
      }
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : String(error)
    };
  }
}
