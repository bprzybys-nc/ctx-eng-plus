---
context_sync:
  ce_updated: false
  last_sync: '2025-11-16T19:56:13.548402+00:00'
  serena_updated: false
created_date: '2025-10-24T09:44:26.297820'
dependencies:
- PRP-29.1
description: Unified knowledge indexing and query system across framework docs, PRPs,
  examples, and Serena memories
executed_commit: 0680a90
executed_date: '2025-10-27T03:31:00Z'
execution_requirements:
  active_project: syntropy-mcp
  language_context: TypeScript
  reason: Implements MCP server tools for knowledge indexing and query interface
  working_directory: syntropy-mcp/
last_updated: '2025-10-27T00:00:00.000000'
name: Syntropy Knowledge Management & Query Interface
prp_id: PRP-29.3
status: executed
updated: '2025-11-16T19:56:13.548554+00:00'
updated_by: update-context-command
version: 1.1
---

# Syntropy Knowledge Management & Query Interface

## 🎯 Feature Overview

**Context:** Syntropy provides a unified index and query interface for all project knowledge sources, enabling fast access to framework documentation and project-specific learnings.

**Prerequisites:** PRP-29.1 must be completed (provides init tool and structure detection)

**Problem:**
- Knowledge scattered (files + Serena memories + framework docs)
- No unified query interface
- Manual search across multiple locations
- Framework docs not programmatically accessible
- No fast lookup (requires full directory scans)

**Solution:**
Implement unified knowledge indexing system that:
1. Scans `.ce/PRPs/system/`, `.ce/examples/system/`, user `PRPs/`, `examples/`, Serena memories
2. Creates searchable index: `.ce/syntropy-index.json`
3. Provides `get_system_doc(path)` for framework docs
4. Provides `get_user_doc(path)` for user content
5. Provides `knowledge_search(query)` for unified search
6. Auto-indexes on project init
7. Supports caching with TTL (5 min)

**Expected Outcome:**
- Single index file: `.ce/syntropy-index.json`
- System docs queryable: `get_system_doc('PRPs/system/executed/PRP-1.md')`
- User docs queryable: `get_user_doc('PRPs/executed/PRP-29.md')`
- Unified search: `knowledge_search("error handling")` → all sources
- Auto-indexed on init (scans `.ce/` + root)
- Fast lookups: <100ms for cached index

---

## 🛠️ Implementation Blueprint

### Phase 1: Index Schema Design (2 hours)

**Goal:** Design comprehensive index schema for `.ce/syntropy-index.json`

**Schema Structure:**
```json
{
  "version": "1.0",
  "project_root": "/path/to/project",
  "synced_at": "2025-10-23T10:00:00Z",
  "framework_version": "1.0",
  
  "paths": {
    "system_prps": ".ce/PRPs/system",
    "system_examples": ".ce/examples/system",
    "user_prps": "PRPs",
    "user_examples": "examples",
    "memories": ".serena/memories",
    "claude_md": "CLAUDE.md",
    "system_rules": ".ce/RULES.md"
  },
  
  "knowledge": {
    "system_patterns": {},
    "user_patterns": {},
    "system_prps": {},
    "user_prps": {},
    "memories": {},
    "system_rules": {}
  },
  
  "drift": {
    "score": 0.0,
    "violations": []
  }
}
```

**Entry Types:**

**Pattern Entry:**
```json
{
  "source": ".ce/examples/system/patterns/error-recovery.py",
  "tags": ["resilience", "retry", "circuit-breaker"],
  "referenced_by": ["PRP-14", "PRP-20"],
  "excerpt": "Retry with exponential backoff..."
}
```

**PRP Entry:**
```json
{
  "source": ".ce/PRPs/system/executed/PRP-1-validation.md",
  "title": "Core Validation Framework",
  "implementations": ["ce/validate.py"],
  "verified": true,
  "tags": ["validation", "L1-L4"],
  "excerpt": "4-level validation gates..."
}
```

**Memory Entry:**
```json
{
  "source": ".serena/memories/tool-usage-guide.md",
  "tags": ["tools", "mcp", "syntropy"],
  "excerpt": "Syntropy MCP tool naming convention..."
}
```

**Rule Entry:**
```json
{
  "source": ".ce/RULES.md",
  "line": 15,
  "excerpt": "Fast Failure: Let exceptions bubble up"
}
```

**Validation:**
```python
# Test schema
import json
from pathlib import Path

schema = {
    "version": "1.0",
    "project_root": "/test",
    "paths": {},
    "knowledge": {},
    "drift": {}
}

# Verify serializable
json_str = json.dumps(schema, indent=2)
assert len(json_str) > 0

print("✅ Schema valid and serializable")
```

**Success Criteria:**
- ✅ Schema supports all knowledge sources
- ✅ Entries include excerpt for fast preview
- ✅ Tags enable semantic search
- ✅ JSON serializable

---

### Phase 2: Knowledge Scanner Implementation (6 hours)

**Goal:** Implement scanner that indexes all knowledge sources

**File:** `syntropy-mcp/src/indexer.ts`

**Core Classes:**

```typescript
import * as fs from "fs/promises";
import * as path from "path";
import { glob } from "glob";
import yaml from "yaml";

interface PatternEntry {
  source: string;
  tags: string[];
  referenced_by: string[];
  excerpt: string;
}

interface PRPEntry {
  source: string;
  title: string;
  implementations: string[];
  verified: boolean;
  tags: string[];
  excerpt: string;
}

interface MemoryEntry {
  source: string;
  tags: string[];
  excerpt: string;
}

interface RuleEntry {
  source: string;
  line: number;
  excerpt: string;
}

export class KnowledgeIndexer {
  private projectRoot: string;
  
  constructor(projectRoot: string) {
    this.projectRoot = projectRoot;
  }
  
  async scanProject(): Promise<KnowledgeIndex> {
    const layout = detectProjectLayout(this.projectRoot);
    
    console.log("🔍 Scanning project knowledge...");
    
    const index: KnowledgeIndex = {
      version: "1.0",
      project_root: this.projectRoot,
      synced_at: new Date().toISOString(),
      framework_version: "1.0",
      paths: {
        system_prps: layout.ceDir + "/PRPs/system",
        system_examples: layout.ceDir + "/examples/system",
        user_prps: layout.prpsDir,
        user_examples: layout.examplesDir,
        memories: layout.memoriesDir,
        claude_md: layout.claudeMd,
        system_rules: layout.ceDir + "/RULES.md"
      },
      knowledge: {
        system_patterns: await this.scanPatterns(
          path.join(this.projectRoot, layout.ceDir, "examples/system/patterns")
        ),
        user_patterns: await this.scanPatterns(
          path.join(this.projectRoot, layout.examplesDir, "patterns")
        ),
        system_prps: await this.scanPRPs(
          path.join(this.projectRoot, layout.ceDir, "PRPs/system/executed")
        ),
        user_prps: await this.scanPRPs(
          path.join(this.projectRoot, layout.prpsDir, "executed")
        ),
        memories: await this.scanMemories(
          path.join(this.projectRoot, layout.memoriesDir)
        ),
        system_rules: await this.scanRules(
          path.join(this.projectRoot, layout.ceDir, "RULES.md")
        )
      },
      drift: { score: 0, violations: [] }
    };
    
    console.log("✅ Knowledge scan complete");
    console.log(`   System patterns: ${Object.keys(index.knowledge.system_patterns).length}`);
    console.log(`   User patterns: ${Object.keys(index.knowledge.user_patterns).length}`);
    console.log(`   System PRPs: ${Object.keys(index.knowledge.system_prps).length}`);
    console.log(`   User PRPs: ${Object.keys(index.knowledge.user_prps).length}`);
    console.log(`   Memories: ${Object.keys(index.knowledge.memories).length}`);
    console.log(`   Rules: ${Object.keys(index.knowledge.system_rules).length}`);
    
    return index;
  }
  
  private async scanPatterns(patternsDir: string): Promise<Record<string, PatternEntry>> {
    const patterns: Record<string, PatternEntry> = {};
    
    // Check if directory exists
    try {
      await fs.access(patternsDir);
    } catch {
      return patterns;  // Graceful: return empty if dir missing
    }
    
    // Find all .md and .py files
    const files = await glob("*.{md,py}", { cwd: patternsDir });
    
    for (const file of files) {
      try {
        const fullPath = path.join(patternsDir, file);
        const content = await fs.readFile(fullPath, "utf-8");
        const key = path.basename(file, path.extname(file));
        
        patterns[key] = {
          source: path.relative(this.projectRoot, fullPath),
          tags: await this.extractTags(content),
          referenced_by: await this.findReferences(key, this.projectRoot),
          excerpt: this.extractExcerpt(content, 200)
        };
      } catch (error) {
        console.warn(`⚠️  Failed to scan pattern ${file}: ${error.message}`);
        // Continue with other files (graceful degradation)
      }
    }
    
    return patterns;
  }
  
  private async scanPRPs(prpsDir: string): Promise<Record<string, PRPEntry>> {
    const prps: Record<string, PRPEntry> = {};
    
    try {
      await fs.access(prpsDir);
    } catch {
      return prps;
    }
    
    const files = await glob("PRP-*.md", { cwd: prpsDir });
    
    for (const file of files) {
      try {
        const fullPath = path.join(prpsDir, file);
        const content = await fs.readFile(fullPath, "utf-8");
        const prpId = file.match(/PRP-[\d.]+/)?.[0] || file;
        
        // Extract YAML header
        const yaml_match = content.match(/^---\n([\s\S]*?)\n---/);
        let yaml_data: any = {};
        
        if (yaml_match) {
          yaml_data = yaml.parse(yaml_match[1]);
        }
        
        prps[prpId] = {
          source: path.relative(this.projectRoot, fullPath),
          title: yaml_data.name || this.extractTitle(content),
          implementations: await this.findImplementations(content, this.projectRoot),
          verified: yaml_data.context_sync?.ce_updated || false,
          tags: yaml_data.tags || await this.extractTags(content),
          excerpt: this.extractExcerpt(content, 200)
        };
      } catch (error) {
        console.warn(`⚠️  Failed to scan PRP ${file}: ${error.message}`);
      }
    }
    
    return prps;
  }
  
  private async scanMemories(memoriesDir: string): Promise<Record<string, MemoryEntry>> {
    const memories: Record<string, MemoryEntry> = {};
    
    try {
      await fs.access(memoriesDir);
    } catch {
      return memories;
    }
    
    const files = await glob("*.md", { cwd: memoriesDir });
    
    for (const file of files) {
      try {
        const fullPath = path.join(memoriesDir, file);
        const content = await fs.readFile(fullPath, "utf-8");
        const key = path.basename(file, ".md");
        
        memories[key] = {
          source: path.relative(this.projectRoot, fullPath),
          tags: await this.extractTags(content),
          excerpt: this.extractExcerpt(content, 200)
        };
      } catch (error) {
        console.warn(`⚠️  Failed to scan memory ${file}: ${error.message}`);
      }
    }
    
    return memories;
  }
  
  private async scanRules(rulesPath: string): Promise<Record<string, RuleEntry>> {
    const rules: Record<string, RuleEntry> = {};
    
    try {
      const content = await fs.readFile(rulesPath, "utf-8");
      const lines = content.split("\n");
      
      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        
        // Look for rule indicators
        if (
          line.includes("MANDATORY") ||
          line.includes("REQUIRED") ||
          line.includes("FORBIDDEN") ||
          line.includes("✅") ||
          line.includes("❌")
        ) {
          const key = this.slugify(line.replace(/[#*✅❌]/g, "").trim());
          if (key.length > 5) {  // Filter noise
            rules[key] = {
              source: path.relative(this.projectRoot, rulesPath),
              line: i + 1,
              excerpt: line.substring(0, 100)
            };
          }
        }
      }
    } catch (error) {
      console.warn(`⚠️  Failed to scan rules: ${error.message}`);
    }
    
    return rules;
  }
  
  // Helpers
  
  private async extractTags(content: string): Promise<string[]> {
    // Strategy 1: YAML frontmatter tags
    const yamlMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (yamlMatch) {
      try {
        const data = yaml.parse(yamlMatch[1]);
        if (data.tags && Array.isArray(data.tags)) {
          return data.tags;
        }
      } catch {
        // Continue to next strategy
      }
    }
    
    // Strategy 2: Inline tags (Tags: api, error, fastapi)
    const inlineMatch = content.match(/Tags?:\s*([^\n]+)/i);
    if (inlineMatch) {
      return inlineMatch[1].split(",").map(t => t.trim());
    }
    
    // Strategy 3: Use markdown headers as tags
    const headers = content.match(/^##{2,3}\s+(.+)$/gm);
    if (headers && headers.length > 0) {
      return headers
        .slice(0, 3)
        .map(h => h.replace(/^#+\s+/, "").trim().toLowerCase());
    }
    
    return [];
  }
  
  private extractExcerpt(content: string, maxLength: number): string {
    // Remove YAML frontmatter
    const withoutYaml = content.replace(/^---\n[\s\S]*?\n---\n/, "");
    
    // Get first paragraph after title
    const paragraphs = withoutYaml.split("\n\n");
    const firstPara = paragraphs.find(p => p.length > 20) || paragraphs[0] || "";
    
    // Clean and truncate
    const cleaned = firstPara.replace(/[#*`\[\]]/g, "").trim();
    return cleaned.length > maxLength
      ? cleaned.substring(0, maxLength) + "..."
      : cleaned;
  }
  
  private extractTitle(content: string): string {
    const titleMatch = content.match(/^#\s+(.+)$/m);
    return titleMatch ? titleMatch[1].trim() : "Untitled";
  }
  
  private slugify(text: string): string {
    return text
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "");
  }
  
  private async findReferences(key: string, root: string): Promise<string[]> {
    // Scan all PRPs for references to this pattern
    const refs: string[] = [];
    
    try {
      const prpFiles = await glob("**/PRP-*.md", { 
        cwd: root,
        ignore: ["node_modules/**", ".venv/**"]
      });
      
      for (const file of prpFiles) {
        const content = await fs.readFile(path.join(root, file), "utf-8");
        if (content.includes(key)) {
          const prpId = file.match(/PRP-[\d.]+/)?.[0];
          if (prpId) refs.push(prpId);
        }
      }
    } catch {
      // Non-fatal
    }
    
    return refs;
  }
  
  private async findImplementations(content: string, root: string): Promise<string[]> {
    // Extract file references from PRP
    const impls: string[] = [];
    
    // Pattern 1: File: path/to/file.ts
    const fileMatches = content.matchAll(/File:\s*`([^`]+)`/g);
    for (const match of fileMatches) {
      impls.push(match[1]);
    }
    
    // Pattern 2: Location: path/to/file.py
    const locMatches = content.matchAll(/Location:\s*`([^`]+)`/g);
    for (const match of locMatches) {
      impls.push(match[1]);
    }
    
    return [...new Set(impls)];  // Deduplicate
  }
}
```

**Validation:**
```bash
# Unit tests
cd syntropy-mcp
npm test src/indexer.test.ts

# Test cases:
# - scanPatterns: Valid patterns with tags
# - scanPatterns: Corrupt file (graceful skip)
# - scanPRPs: Extract YAML data
# - scanPRPs: Fallback when no YAML
# - scanMemories: Serena format
# - scanRules: Extract from RULES.md
# - extractTags: YAML frontmatter
# - extractTags: Inline format
# - extractTags: Headers fallback
# - findReferences: Scan PRPs for pattern usage
# - findImplementations: Extract file references
```

**Success Criteria:**
- ✅ Scanner indexes all sources
- ✅ Gracefully handles missing directories
- ✅ Extracts tags using 3-strategy fallback
- ✅ Finds cross-references between PRPs and patterns
- ✅ All unit tests passing

---

### Phase 3: Query Tools Implementation (4 hours)

**Goal:** Implement MCP tools for doc access and search

**File:** `syntropy-mcp/src/tools/knowledge.ts`

**Get System Doc:**
```typescript
interface GetSystemDocArgs {
  path: string;  // e.g., "PRPs/system/executed/PRP-1.md"
}

export async function getSystemDoc(args: GetSystemDocArgs): Promise<object> {
  const projectRoot = process.cwd();
  const docPath = path.join(projectRoot, ".ce", args.path);
  
  try {
    // Security: prevent directory traversal
    const resolvedPath = path.resolve(docPath);
    const allowedRoot = path.resolve(projectRoot, ".ce");
    
    if (!resolvedPath.startsWith(allowedRoot)) {
      throw new Error(
        `Security error: path outside .ce/ directory\n` +
        `🔧 Troubleshooting: Ensure path is relative to .ce/`
      );
    }
    
    // Check file exists
    await fs.access(resolvedPath);
    
    // Read content
    const content = await fs.readFile(resolvedPath, "utf-8");
    
    return {
      success: true,
      path: args.path,
      content,
      size: content.length
    };
  } catch (error) {
    throw new Error(
      `System doc not found: ${args.path}\n` +
      `🔧 Troubleshooting: Check path and ensure project initialized`
    );
  }
}
```

**Get User Doc:**
```typescript
interface GetUserDocArgs {
  path: string;  // e.g., "PRPs/executed/PRP-29.md"
}

export async function getUserDoc(args: GetUserDocArgs): Promise<object> {
  const projectRoot = process.cwd();
  const docPath = path.join(projectRoot, args.path);
  
  try {
    // Security: prevent directory traversal
    const resolvedPath = path.resolve(docPath);
    const allowedRoot = path.resolve(projectRoot);
    
    if (!resolvedPath.startsWith(allowedRoot)) {
      throw new Error("Security error: directory traversal detected");
    }
    
    // Also prevent access to .ce/ via this method
    if (resolvedPath.includes(path.sep + ".ce" + path.sep)) {
      throw new Error(
        `.ce/ documents should use get_system_doc\n` +
        `🔧 Troubleshooting: Use get_system_doc() for .ce/ content`
      );
    }
    
    await fs.access(resolvedPath);
    const content = await fs.readFile(resolvedPath, "utf-8");
    
    return {
      success: true,
      path: args.path,
      content,
      size: content.length
    };
  } catch (error) {
    throw new Error(
      `User doc not found: ${args.path}\n` +
      `🔧 Troubleshooting: Check path relative to project root`
    );
  }
}
```

**Knowledge Search:**
```typescript
interface KnowledgeSearchArgs {
  query: string;
  sources?: string[];  // ["system_patterns", "user_prps", ...]
  limit?: number;
}

interface SearchResult {
  key: string;
  source: string;
  excerpt: string;
  tags?: string[];
  score: number;
}

export async function knowledgeSearch(args: KnowledgeSearchArgs): Promise<object> {
  const projectRoot = process.cwd();
  const indexPath = path.join(projectRoot, ".ce/syntropy-index.json");
  
  try {
    // Load index with staleness check
    const index = await loadIndexWithCache(indexPath);
    
    if (!index) {
      throw new Error(
        `Index not found\n` +
        `🔧 Troubleshooting: Run syntropy_init_project to create index`
      );
    }
    
    // Default to all sources
    const sources = args.sources || [
      "system_patterns",
      "user_patterns",
      "system_prps",
      "user_prps",
      "memories",
      "system_rules"
    ];
    
    const results: SearchResult[] = [];
    
    // Search across sources
    for (const source of sources) {
      const entries = index.knowledge[source];
      if (!entries) continue;
      
      for (const [key, entry] of Object.entries(entries)) {
        const score = calculateRelevance(args.query, entry);
        
        if (score > 0.3) {  // Relevance threshold
          results.push({
            key,
            source: entry.source,
            excerpt: entry.excerpt,
            tags: entry.tags,
            score
          });
        }
      }
    }
    
    // Sort by score (descending)
    results.sort((a, b) => b.score - a.score);
    
    // Limit results
    const limit = args.limit || 20;
    const limited = results.slice(0, limit);
    
    return {
      success: true,
      query: args.query,
      count: limited.length,
      total_indexed: Object.keys(index.knowledge).reduce(
        (sum, k) => sum + Object.keys(index.knowledge[k]).length,
        0
      ),
      results: limited
    };
  } catch (error) {
    throw new Error(
      `Knowledge search failed: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure project initialized and index exists`
    );
  }
}

// Load index with 5-min TTL cache
async function loadIndexWithCache(indexPath: string): Promise<any | null> {
  try {
    const stats = await fs.stat(indexPath);
    const ageMinutes = (Date.now() - stats.mtime.getTime()) / 1000 / 60;
    
    if (ageMinutes > 5) {
      console.log("⚠️  Index stale (>5 min), recommend running syntropy_sync_context");
    }
    
    const content = await fs.readFile(indexPath, "utf-8");
    return JSON.parse(content);
  } catch {
    return null;
  }
}

// Calculate search relevance
function calculateRelevance(query: string, entry: any): number {
  const q = query.toLowerCase();
  const queryTokens = q.split(/\s+/).filter(t => t.length > 2);
  let score = 0;
  
  const excerpt = entry.excerpt?.toLowerCase() || "";
  
  // Multi-word query (all tokens match)
  const allTokensMatch = queryTokens.every(token => excerpt.includes(token));
  if (allTokensMatch && queryTokens.length > 1) {
    score += 0.6;
  } else if (excerpt.includes(q)) {
    // Exact phrase match
    score += 0.5;
  } else {
    // Partial token matches
    const matchedTokens = queryTokens.filter(token => excerpt.includes(token)).length;
    score += (matchedTokens / queryTokens.length) * 0.3;
  }
  
  // Tag match
  if (entry.tags?.some(tag => queryTokens.some(token => tag.toLowerCase().includes(token)))) {
    score += 0.3;
  }
  
  // Source path match
  if (entry.source?.toLowerCase().includes(q)) {
    score += 0.2;
  }
  
  return Math.min(score, 1.0);
}
```

**Validation:**
```bash
# Integration tests
cd syntropy-mcp
npm test src/tools/knowledge.test.ts

# Test cases:
# - getSystemDoc: Valid path
# - getSystemDoc: Directory traversal (security)
# - getUserDoc: Valid path
# - getUserDoc: Prevent .ce/ access
# - knowledgeSearch: Multi-word query
# - knowledgeSearch: Filter by sources
# - knowledgeSearch: Respect limit
# - loadIndexWithCache: Fresh index
# - loadIndexWithCache: Stale index (warning)
# - calculateRelevance: Exact match
# - calculateRelevance: Token match
# - calculateRelevance: Tag match
```

**Success Criteria:**
- ✅ System docs accessible with security
- ✅ User docs accessible with security
- ✅ Search works across all sources
- ✅ Relevance scoring accurate
- ✅ All tests passing

---

### Phase 4: Integration with Init (2 hours)

**Goal:** Auto-index on project init

**File:** `syntropy-mcp/src/tools/init.ts`

**Modify initProject():**
```typescript
export async function initProject(args: InitProjectArgs): Promise<object> {
  const projectRoot = path.resolve(args.project_root);

  try {
    // ... existing init logic ...

    // 6. Index knowledge (NEW)
    await indexKnowledge(projectRoot);

    return {
      success: true,
      message: "Project initialized successfully",
      structure: ".ce/ (system) + PRPs/examples/ (user)",
      indexed: true
    };
  } catch (error) {
    throw new Error(
      `Failed to initialize project: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure directory writable`
    );
  }
}

async function indexKnowledge(projectRoot: string): Promise<void> {
  try {
    console.log("");
    console.log("📚 Indexing knowledge...");
    
    const indexer = new KnowledgeIndexer(projectRoot);
    const index = await indexer.scanProject();
    
    // Save index
    const indexPath = path.join(projectRoot, ".ce/syntropy-index.json");
    await fs.writeFile(indexPath, JSON.stringify(index, null, 2));
    
    console.log(`✅ Knowledge indexed: .ce/syntropy-index.json`);
    console.log(`   Total entries: ${
      Object.values(index.knowledge)
        .reduce((sum, source) => sum + Object.keys(source).length, 0)
    }`);
  } catch (error) {
    // Non-fatal: indexing failure shouldn't break init
    console.warn(`⚠️  Knowledge indexing failed (non-fatal): ${error.message}`);
    console.warn(`   You can manually index later with syntropy_sync_context`);
  }
}
```

**Validation:**
```bash
# Test init with indexing
syntropy_init_project /tmp/test-project

# Verify index created
test -f /tmp/test-project/.ce/syntropy-index.json && echo "✅ Index created"

# Verify index content
cat /tmp/test-project/.ce/syntropy-index.json | jq '.knowledge | keys'
```

**Success Criteria:**
- ✅ Index auto-generated on init
- ✅ Graceful failure if indexing fails
- ✅ Progress messages clear

---

### Phase 5: Tool Registration (1 hour)

**Goal:** Register knowledge tools in MCP server

**File:** `syntropy-mcp/src/tools-definition.ts`

**Add Tools:**
```typescript
{
  name: "syntropy_get_system_doc",
  description: "Retrieve system documentation from .ce/ directory",
  inputSchema: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "Path relative to .ce/ (e.g., 'PRPs/system/executed/PRP-1.md')"
      }
    },
    required: ["path"]
  }
},
{
  name: "syntropy_get_user_doc",
  description: "Retrieve user documentation from project root",
  inputSchema: {
    type: "object",
    properties: {
      path: {
        type: "string",
        description: "Path relative to project root (e.g., 'PRPs/executed/PRP-29.md')"
      }
    },
    required: ["path"]
  }
},
{
  name: "syntropy_knowledge_search",
  description: "Search across all knowledge sources (patterns, PRPs, memories, rules)",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query (keywords or phrase)"
      },
      sources: {
        type: "array",
        items: { type: "string" },
        description: "Optional: filter by sources (system_patterns, user_prps, etc.)"
      },
      limit: {
        type: "number",
        description: "Max results (default 20)"
      }
    },
    required: ["query"]
  }
}
```

**Register Handlers:**
```typescript
// In main handler
case "syntropy_get_system_doc":
  return await getSystemDoc(args as GetSystemDocArgs);

case "syntropy_get_user_doc":
  return await getUserDoc(args as GetUserDocArgs);

case "syntropy_knowledge_search":
  return await knowledgeSearch(args as KnowledgeSearchArgs);
```

**Validation:**
```bash
# Test MCP calls
echo '{"method": "tools/call", "params": {"name": "syntropy_knowledge_search", "arguments": {"query": "error handling"}}}' |   node syntropy-mcp/dist/index.js
```

**Success Criteria:**
- ✅ All 3 tools registered
- ✅ MCP calls succeed
- ✅ Correct routing to handlers

---

### Phase 6: Testing & Documentation (3 hours)

**Goal:** Comprehensive testing

**Unit Tests:**
```typescript
// src/indexer.test.ts
describe("KnowledgeIndexer", () => {
  it("scans patterns with tags", async () => {
    const indexer = new KnowledgeIndexer("/test");
    const patterns = await indexer.scanPatterns("/test/patterns");
    
    expect(patterns["error-recovery"]).toBeDefined();
    expect(patterns["error-recovery"].tags).toContain("resilience");
  });
  
  it("handles missing directories gracefully", async () => {
    const indexer = new KnowledgeIndexer("/test");
    const patterns = await indexer.scanPatterns("/nonexistent");
    
    expect(patterns).toEqual({});  // Empty, no crash
  });
  
  it("extracts YAML tags", async () => {
    const content = `---
tags: [api, error, fastapi]
---
# Content`;
    const tags = await indexer.extractTags(content);
    expect(tags).toEqual(["api", "error", "fastapi"]);
  });
});

// src/tools/knowledge.test.ts
describe("knowledgeSearch", () => {
  it("finds multi-word matches", async () => {
    const result = await knowledgeSearch({
      query: "error handling"
    });
    
    expect(result.count).toBeGreaterThan(0);
    expect(result.results[0].score).toBeGreaterThan(0.5);
  });
  
  it("filters by sources", async () => {
    const result = await knowledgeSearch({
      query: "validation",
      sources: ["system_prps"]
    });
    
    // Should only return system PRPs
    expect(result.results.every(r => r.source.includes("system"))).toBe(true);
  });
});

describe("getSystemDoc", () => {
  it("prevents directory traversal", async () => {
    await expect(
      getSystemDoc({ path: "../../../etc/passwd" })
    ).rejects.toThrow("Security error");
  });
});
```

**Integration Tests:**
```bash
# Full workflow
syntropy_init_project /tmp/test-knowledge
cd /tmp/test-knowledge

# Test doc access
syntropy_get_system_doc "PRPs/system/executed/PRP-1.md"  # Should succeed

# Test search
syntropy_knowledge_search "validation"  # Should return PRPs

# Test user docs
echo "# My PRP" > PRPs/executed/PRP-TEST.md
syntropy_get_user_doc "PRPs/executed/PRP-TEST.md"  # Should succeed
```

**Documentation:**
```markdown
# Knowledge Management

## Tools

### syntropy_get_system_doc
Access framework documentation from `.ce/` directory.

### syntropy_get_user_doc  
Access project documentation from root.

### syntropy_knowledge_search
Search across all knowledge sources.

## Index Structure

The index is stored in `.ce/syntropy-index.json` and includes:
- System patterns
- User patterns
- System PRPs
- User PRPs
- Serena memories
- System rules

## Performance

- Index cached with 5-min TTL
- Search: <100ms for cached index
- Supports up to 100 PRPs efficiently
```

**Success Criteria:**
- ✅ All unit tests passing (90%+ coverage)
- ✅ All integration tests passing
- ✅ Documentation complete
- ✅ No breaking changes

---

## 📋 Acceptance Criteria

**Must Have:**
- [ ] Index schema implemented (`.ce/syntropy-index.json`)
- [ ] Knowledge scanner indexes all sources
- [ ] `syntropy_get_system_doc` tool working
- [ ] `syntropy_get_user_doc` tool working
- [ ] `syntropy_knowledge_search` tool working
- [ ] Auto-indexing on init
- [ ] Security: directory traversal prevention
- [ ] Performance: <100ms search (cached)
- [ ] All tests passing

**Nice to Have:**
- [ ] Incremental indexing (track mtimes)
- [ ] Vector embeddings for semantic search
- [ ] Configurable TTL

**Out of Scope:**
- Full-text search (phase 2)
- Real-time index updates
- Distributed indexing

---

## 🧪 Testing Strategy

### Unit Tests
- Scanner functions (patterns, PRPs, memories, rules)
- Tag extraction (YAML, inline, headers)
- Relevance scoring
- Security (path validation)

### Integration Tests
- Full project indexing
- Tool calls via MCP
- Index staleness warnings

### Performance Tests
```bash
# Benchmark search
time syntropy_knowledge_search "error handling"
# Target: <100ms

# Large project test (100 PRPs)
# Create 100 test PRPs
for i in {1..100}; do
  echo "# PRP-$i" > PRPs/executed/PRP-$i.md
done

# Re-index and search
syntropy_init_project .
time syntropy_knowledge_search "test"
```

---

## 📚 Dependencies

**External:**
- Node.js 18+ (fs/promises)
- glob package
- yaml package

**Internal:**
- PRP-29.1 (init tool + scanner)
- Syntropy MCP server

**Files Modified:**
- `syntropy-mcp/src/indexer.ts` (new)
- `syntropy-mcp/src/tools/knowledge.ts` (new)
- `syntropy-mcp/src/tools/init.ts` (add indexing)
- `syntropy-mcp/src/tools-definition.ts` (register tools)

---

## ⚠️ Risks & Mitigations

**Risk 1: Index size explosion (large projects)**
- **Mitigation:** Excerpt truncation (200 chars), exclude binary files
- **Threshold:** Warn if index >10MB

**Risk 2: Stale index (outdated results)**
- **Mitigation:** 5-min TTL with staleness warnings
- **Future:** Incremental updates via file watchers

**Risk 3: Security (directory traversal)**
- **Mitigation:** Strict path validation, resolve() checks
- **Testing:** Explicit security test cases

**Risk 4: Search relevance poor**
- **Mitigation:** Multi-strategy scoring (excerpt, tags, path)
- **Future:** ML-based relevance tuning

---

## 📖 References

**MCP Documentation:**
- Tool definitions: https://modelcontextprotocol.io/docs/tools/building-tools

**Node.js Documentation:**
- fs/promises: https://nodejs.org/api/fs.html#promises-api
- glob: https://github.com/isaacs/node-glob

**Existing Patterns:**
- `ce/drift.py`: YAML parsing, file scanning
- `ce/update_context.py`: Directory scanning, glob patterns

**Related PRPs:**
- PRP-29.1: Init tool (prerequisite)
- PRP-29.3: Context sync (consumer of this PRP)

---

## 🎯 Success Metrics

**Implementation:**
- Time to implement: 18 hours (estimated)
- Code coverage: 90%+ for indexer + tools
- Index performance: <100ms search (cached)

**User Experience:**
- Zero manual indexing (auto on init)
- Fast search (<100ms)
- Clear error messages with troubleshooting

**Quality:**
- All error messages include 🔧 troubleshooting
- Security validated (no traversal)
- No fishy fallbacks