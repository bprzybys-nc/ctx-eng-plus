/**
 * Knowledge Index Schema for .ce/syntropy-index.json
 * 
 * Unified index across all project knowledge sources:
 * - Framework docs (.ce/)
 * - PRPs (PRPs/executed, PRPs/feature-requests)
 * - Examples (examples/)
 * - Serena memories (.serena/memories/)
 */

export interface KnowledgeIndex {
  version: string;
  last_updated: string;
  entries: IndexEntry[];
}

export type IndexEntry =
  | PatternEntry
  | PRPEntry
  | MemoryEntry
  | RuleEntry
  | ExampleEntry
  | ResearchEntry;

export interface BaseEntry {
  id: string;
  type: "pattern" | "prp" | "memory" | "rule" | "example" | "research";
  title: string;
  excerpt: string; // First 200 chars for search preview
  path: string; // Relative to project root
  tags: string[];
  last_modified?: string;
}

export interface PatternEntry extends BaseEntry {
  type: "pattern";
  category: "code" | "testing" | "architecture" | "workflow";
  language?: string; // e.g., "typescript", "python"
}

export interface PRPEntry extends BaseEntry {
  type: "prp";
  prp_id: string; // e.g., "PRP-29.3"
  status: "feature-request" | "executed";
  phase?: string;
  issue_id?: string; // Linear issue ID
}

export interface MemoryEntry extends BaseEntry {
  type: "memory";
  memory_type: string; // e.g., "architecture", "pattern", "note"
  context?: string; // What context this memory relates to
}

export interface RuleEntry extends BaseEntry {
  type: "rule";
  rule_category: "code-quality" | "testing" | "workflow" | "communication";
  enforcement_level: "mandatory" | "recommended" | "guideline";
}

export interface ExampleEntry extends BaseEntry {
  type: "example";
  example_type: "code" | "config" | "workflow" | "documentation";
  language?: string;
  framework?: string;
}

export interface ResearchEntry extends BaseEntry {
  type: "research";
  source: string; // e.g., "perplexity-ai", "internal-research"
  category?: string; // e.g., "ce-graph-framework"
  denoise_status?: "pending" | "completed" | "in-progress";
  kb_integration?: "pending" | "completed" | "in-progress";
}

/**
 * Search query interface
 */
export interface KnowledgeSearchQuery {
  query: string;
  types?: Array<"pattern" | "prp" | "memory" | "rule" | "example" | "research">;
  tags?: string[];
  limit?: number; // Default 10
}

/**
 * Search result with relevance scoring
 */
export interface SearchResult {
  entry: IndexEntry;
  score: number; // Relevance score 0-100
  match_reason: string; // Why this was matched
}

/**
 * Index statistics
 */
export interface IndexStats {
  total_entries: number;
  by_type: Record<string, number>;
  last_updated: string;
  coverage_percentage: number; // % of knowledge sources indexed
}
