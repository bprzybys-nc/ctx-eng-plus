# INITIAL: Syntropy Knowledge Management & Query Interface

**Feature:** Unified knowledge indexing and query system across framework docs, PRPs, examples, and Serena memories.

**Prerequisites:** PRP-29.1 must be completed first (provides init tool and structure detection)

**Dependencies:** PRP-29.3 depends on this PRP (uses knowledge index for drift detection)

---

## FEATURE

Syntropy provides a unified index and query interface for all project knowledge sources, enabling fast access to framework documentation and project-specific learnings.

**Goals:**
1. Implement unified index schema (`.ce/syntropy-index.json`)
2. Knowledge scanner (`.ce/PRPs/system/`, `.ce/examples/system/`, user PRPs/, examples/, Serena memories)
3. System doc accessor: `get_system_doc(path)` (reads from `.ce/`)
4. Unified search: `knowledge_search(query)` across system + user sources
5. Auto-index on project init (extends PRP-29.1)
6. Support `.ce/` system + root user structure
7. Track patterns, PRP learnings, and memories in index

**Current Problems:**
- Knowledge scattered (files + Serena memories + framework docs)
- No unified query interface
- Manual search across multiple locations
- Framework docs not programmatically accessible

**Expected Outcome:**
- Single index file: `.ce/syntropy-index.json`
- System docs queryable: `get_system_doc('PRPs/system/executed/PRP-1.md')`
- User docs queryable: `get_user_doc('PRPs/executed/PRP-29.md')`
- Unified search: `knowledge_search("error handling")` → system + user PRPs + examples + memories
- Auto-indexed on init (scans `.ce/` + root)
- Fast lookups (no full directory scans)

---

## EXAMPLES

### Example 1: Unified Index Schema

**Location:** `.ce/syntropy-index.json`

```json
{
  "version": "1.0",
  "project_root": "/Users/user/my-project",
  "synced_at": "2025-10-22T10:00:00Z",
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
    "system_patterns": {
      "error-recovery": {
        "source": ".ce/examples/system/patterns/error-recovery.py",
        "tags": ["resilience", "retry", "circuit-breaker"],
        "referenced_by": ["PRP-14"],
        "excerpt": "Retry with exponential backoff..."
      },
      "strategy-testing": {
        "source": ".ce/examples/system/patterns/strategy-testing.py",
        "tags": ["testing", "mocks", "pipeline"],
        "referenced_by": ["PRP-10"],
        "excerpt": "Strategy pattern for composable testing..."
      }
    },

    "user_patterns": {
      "api-error-handling": {
        "source": "examples/patterns/api-error.md",
        "tags": ["api", "error", "project-specific"],
        "referenced_by": ["PRP-29"],
        "excerpt": "Project-specific error handling..."
      }
    },

    "system_prps": {
      "PRP-1": {
        "source": ".ce/PRPs/system/executed/PRP-1-validation.md",
        "title": "Core Validation Framework",
        "implementations": ["ce/validate.py"],
        "verified": true,
        "tags": ["validation", "L1-L4"],
        "excerpt": "4-level validation gates..."
      }
    },

    "user_prps": {
      "PRP-29": {
        "source": "PRPs/executed/PRP-29-syntropy-init.md",
        "title": "Syntropy Init",
        "implementations": ["syntropy-mcp/src/tools/init.ts"],
        "verified": true,
        "tags": ["init", "scaffolding"],
        "excerpt": "Project initialization workflow..."
      }
    },

    "memories": {
      "tool-usage-guide": {
        "source": ".serena/memories/tool-usage-guide.md",
        "tags": ["tools", "mcp", "syntropy"],
        "excerpt": "Syntropy MCP tool naming convention..."
      }
    },

    "system_rules": {
      "no-fishy-fallbacks": {
        "source": ".ce/RULES.md",
        "line": 15,
        "excerpt": "Fast Failure: Let exceptions bubble up"
      }
    }
  },

  "drift": {
    "score": 0.05,
    "violations": []
  }
}
```

**Pattern:** Single index, all sources tracked, fast lookups by key, excerpt for quick reference.

### Example 2: Knowledge Scanner

**Location:** `syntropy-mcp/src/indexer.ts`

```typescript
interface KnowledgeIndex {
  version: string;
  project_root: string;
  synced_at: string;
  framework_version: string;
  paths: PathsConfig;
  knowledge: {
    patterns: Record<string, PatternEntry>;
    prp_learnings: Record<string, PRPEntry>;
    memories: Record<string, MemoryEntry>;
    rules: Record<string, RuleEntry>;
  };
  drift: DriftInfo;
}

export class KnowledgeIndexer {
  async scanProject(projectRoot: string): Promise<KnowledgeIndex> {
    const layout = detectProjectLayout(projectRoot);

    const index: KnowledgeIndex = {
      version: "1.0",
      project_root: projectRoot,
      synced_at: new Date().toISOString(),
      framework_version: "1.0",
      paths: layout,
      knowledge: {
        patterns: await this.scanPatterns(projectRoot, layout),
        prp_learnings: await this.scanPRPs(projectRoot, layout),
        memories: await this.scanMemories(projectRoot, layout),
        rules: await this.scanRules(projectRoot, layout)
      },
      drift: { score: 0, violations: [] }
    };

    return index;
  }

  private async scanPatterns(root: string, layout: ProjectLayout): Promise<Record<string, PatternEntry>> {
    const patternsDir = path.join(root, layout.examplesDir, "patterns");
    const patterns: Record<string, PatternEntry> = {};

    if (!await exists(patternsDir)) return patterns;

    const files = await glob("*.md", { cwd: patternsDir });

    for (const file of files) {
      try {
        const fullPath = path.join(patternsDir, file);
        const content = await fs.readFile(fullPath, "utf-8");
        const key = path.basename(file, ".md");

        patterns[key] = {
          source: path.relative(root, fullPath),
          tags: extractTags(content),
          referenced_by: await findReferences(key, root),
          excerpt: extractExcerpt(content, 200)
        };
      } catch (error) {
        console.warn(`⚠️  Failed to scan pattern ${file}: ${error.message}`);
        // Continue with other files
      }
    }

    return patterns;
  }

  private async scanPRPs(root: string, layout: ProjectLayout): Promise<Record<string, PRPEntry>> {
    const prpsDir = path.join(root, layout.prpsDir, "executed");
    const prps: Record<string, PRPEntry> = {};

    if (!await exists(prpsDir)) return prps;

    const files = await glob("PRP-*.md", { cwd: prpsDir });

    for (const file of files) {
      try {
        const fullPath = path.join(prpsDir, file);
        const content = await fs.readFile(fullPath, "utf-8");
        const prpId = file.match(/PRP-(\d+)/)?.[0] || file;

        prps[prpId] = {
          source: path.relative(root, fullPath),
          title: extractTitle(content),
          implementations: await findImplementations(content, root),
          verified: checkVerified(content),
          tags: extractTags(content),
          excerpt: extractExcerpt(content, 200)
        };
      } catch (error) {
        console.warn(`⚠️  Failed to scan PRP ${file}: ${error.message}`);
        // Continue with other files
      }
    }

    return prps;
  }

  private async scanMemories(root: string, layout: ProjectLayout): Promise<Record<string, MemoryEntry>> {
    const memoriesDir = path.join(root, layout.memoriesDir);
    const memories: Record<string, MemoryEntry> = {};

    if (!await exists(memoriesDir)) return memories;

    const files = await glob("*.md", { cwd: memoriesDir });

    for (const file of files) {
      try {
        const fullPath = path.join(memoriesDir, file);
        const content = await fs.readFile(fullPath, "utf-8");
        const key = path.basename(file, ".md");

        memories[key] = {
          source: path.relative(root, fullPath),
          tags: extractTags(content),
          excerpt: extractExcerpt(content, 200)
        };
      } catch (error) {
        console.warn(`⚠️  Failed to scan memory ${file}: ${error.message}`);
        // Continue with other files
      }
    }

    return memories;
  }

  private async scanRules(root: string, layout: ProjectLayout): Promise<Record<string, RuleEntry>> {
    const claudeMd = path.join(root, layout.claudeMd);
    const rules: Record<string, RuleEntry> = {};

    if (!await exists(claudeMd)) return rules;

    const content = await fs.readFile(claudeMd, "utf-8");
    const lines = content.split("\n");

    // Extract rules from CLAUDE.md (headers + important statements)
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];

      // Check for rule indicators
      if (line.includes("MANDATORY") || line.includes("REQUIRED") || line.includes("FORBIDDEN")) {
        const key = slugify(line.replace(/[#*]/g, "").trim());
        rules[key] = {
          source: layout.claudeMd,
          line: i + 1,
          excerpt: line.substring(0, 100)
        };
      }
    }

    return rules;
  }
}

// Helper: Extract tags from markdown content
function extractTags(content: string): string[] {
  // Strategy 1: Try YAML frontmatter tags
  const yamlMatch = content.match(/^---\n([\s\S]*?)\n---/);
  if (yamlMatch) {
    const tagsMatch = yamlMatch[1].match(/tags:\s*\[(.*?)\]/);
    if (tagsMatch) {
      return tagsMatch[1].split(",").map(t => t.trim().replace(/['"]/g, ""));
    }
  }

  // Strategy 2: Extract from inline tags (e.g., "Tags: api, error, fastapi")
  const inlineMatch = content.match(/Tags?:\s*([^\n]+)/i);
  if (inlineMatch) {
    return inlineMatch[1].split(",").map(t => t.trim());
  }

  // Strategy 3: Extract from markdown headers (use as tags)
  const headers = content.match(/^#{2,3}\s+(.+)$/gm);
  if (headers && headers.length > 0) {
    return headers
      .slice(0, 3)  // Max 3 header-based tags
      .map(h => h.replace(/^#+\s+/, "").trim().toLowerCase());
  }

  return [];
}
```

**Pattern:** Modular scanning (patterns, PRPs, memories, rules), extract metadata, async/await, graceful degradation if dirs missing.

### Example 3: Framework Doc Accessor

**Location:** `syntropy-mcp/src/tools/knowledge.ts`

```typescript
interface GetFrameworkDocArgs {
  path: string;  // e.g., "research/01-prp-system" or "templates/self-healing"
}

export async function getFrameworkDoc(args: GetFrameworkDocArgs): Promise<object> {
  const docsRoot = path.join(__dirname, "../../docs");
  const docPath = path.join(docsRoot, args.path + ".md");

  try {
    // Security: prevent directory traversal
    const resolvedPath = path.resolve(docPath);
    if (!resolvedPath.startsWith(docsRoot)) {
      throw new Error("Invalid path: directory traversal detected");
    }

    // Check if file exists
    await fs.access(resolvedPath);

    // Read content
    const content = await fs.readFile(resolvedPath, "utf-8");

    return {
      success: true,
      path: args.path,
      content: content,
      size: content.length
    };
  } catch (error) {
    throw new Error(
      `Framework doc not found: ${args.path}\n` +
      `🔧 Troubleshooting: Check available docs with knowledge_list_docs`
    );
  }
}
```

**Pattern:** Security (prevent traversal), fast failure, actionable errors.

### Example 4: Unified Search

**Location:** `syntropy-mcp/src/tools/knowledge.ts`

```typescript
interface KnowledgeSearchArgs {
  query: string;       // Search query
  sources?: string[];  // Optional: ["patterns", "prps", "memories", "rules"]
  limit?: number;      // Max results (default 20)
}

interface SearchResult {
  key: string;
  source: string;
  excerpt: string;
  tags?: string[];
  score: number;  // Relevance score (0-1)
}

export async function knowledgeSearch(args: KnowledgeSearchArgs): Promise<object> {
  const projectRoot = process.cwd();  // Or get from Syntropy context
  const indexPath = path.join(projectRoot, ".ce/syntropy-index.json");

  try {
    // Load index (with staleness check)
    const index = await loadIndexWithCache(indexPath);
    if (!index) {
      throw new Error("Index not found or stale, please run syntropy_init_project");
    }

    // Search across sources
    const sources = args.sources || ["patterns", "prps", "memories", "rules"];
    const results: SearchResult[] = [];

    for (const source of sources) {
      const entries = index.knowledge[source];
      if (!entries) continue;

      for (const [key, entry] of Object.entries(entries)) {
        const score = calculateRelevance(args.query, entry);
        if (score > 0.3) {  // Threshold
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
      results: limited
    };
  } catch (error) {
    throw new Error(
      `Knowledge search failed: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure project is initialized with syntropy_init_project`
    );
  }
}

// Helper: Load index with staleness check (5-min TTL)
async function loadIndexWithCache(indexPath: string): Promise<KnowledgeIndex | null> {
  try {
    const stats = await fs.stat(indexPath);
    const age = (Date.now() - stats.mtime.getTime()) / 1000 / 60;  // Minutes

    if (age > 5) {  // TTL: 5 minutes
      console.log("⚠️  Index stale (>5 min), recommend running syntropy_sync_context");
      // Still return stale index (graceful degradation), but warn user
    }

    const content = await fs.readFile(indexPath, "utf-8");
    return JSON.parse(content);
  } catch {
    return null;  // Index missing
  }
}

function calculateRelevance(query: string, entry: any): number {
  const q = query.toLowerCase();
  const queryTokens = q.split(/\s+/).filter(t => t.length > 2);  // Split and filter short words
  let score = 0;

  // Multi-word query support (all tokens must match for bonus)
  const excerpt = entry.excerpt?.toLowerCase() || "";
  const allTokensMatch = queryTokens.every(token => excerpt.includes(token));
  if (allTokensMatch && queryTokens.length > 1) {
    score += 0.6;  // Bonus for multi-word match
  } else if (excerpt.includes(q)) {
    score += 0.5;  // Exact phrase match
  } else {
    // Partial token matches
    const matchedTokens = queryTokens.filter(token => excerpt.includes(token)).length;
    score += (matchedTokens / queryTokens.length) * 0.3;
  }

  // Match in tags
  if (entry.tags?.some(tag => queryTokens.some(token => tag.toLowerCase().includes(token)))) {
    score += 0.3;
  }

  // Match in source path
  if (entry.source?.toLowerCase().includes(q)) score += 0.2;

  return Math.min(score, 1.0);
}
```

**Pattern:** Load index, search all sources, score relevance, sort, limit results.

---

## DOCUMENTATION

### TypeScript/Node.js
- File system: `fs/promises` async operations
- Glob patterns: `glob` package for file discovery
- JSON: `JSON.parse()`, `JSON.stringify()`
- Path security: Check `path.resolve()` vs allowed root

### Indexing Strategy
- **Patterns:** Scan `examples/patterns/*.md`
- **PRPs:** Scan `PRPs/executed/PRP-*.md`
- **Memories:** Scan `.serena/memories/*.md`
- **Rules:** Extract from `CLAUDE.md` (MANDATORY, REQUIRED, FORBIDDEN)

### Search Algorithm
- Simple keyword matching (phase 1)
- Future: Full-text search with vector embeddings (phase 2)
- Relevance scoring: excerpt match (0.5) + tags (0.3) + path (0.2)

---

## OTHER CONSIDERATIONS

### Performance
- Index cached in `.ce/syntropy-index.json` (5-min TTL)
- Avoid full directory scans on every query
- Incremental updates (track file mtimes)
- Lazy loading (only scan when index stale)

### Security
- Prevent directory traversal in `get_framework_doc`
- Validate all file paths against allowed roots
- Sanitize user queries (escape special chars)

### Error Handling
- Fast failure with 🔧 troubleshooting
- Clear messages: "Index not found → run syntropy_init_project"
- No fishy fallbacks (no silent failures)

### Integration with PRP-29.1
- Init tool calls `KnowledgeIndexer.scanProject()` on first run
- Creates `.ce/syntropy-index.json`
- Subsequent searches use cached index

### Testing Strategy
- **Unit:** Scanner functions (patterns, PRPs, memories, rules)
- **Integration:** Full indexing on test projects
- **E2E:** Query tools with real index

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
cd syntropy-mcp && npm run build
```

### Level 2: Unit Tests
```bash
cd syntropy-mcp && npm test src/indexer.test.ts
cd syntropy-mcp && npm test src/tools/knowledge.test.ts
```

**Specific Test Scenarios:**
- `test_scanPatterns_valid`: Index valid pattern files
- `test_scanPatterns_corrupt`: Gracefully handle corrupt markdown (warning, continue)
- `test_scanPRPs_withImplementations`: Extract implementation files from PRPs
- `test_scanPRPs_noYAML`: Handle PRPs without YAML frontmatter
- `test_scanMemories_serenaFormat`: Extract Serena memory format
- `test_scanRules_claudeMd`: Extract MANDATORY/REQUIRED/FORBIDDEN rules
- `test_extractTags_yaml`: Extract tags from YAML frontmatter
- `test_extractTags_inline`: Extract from "Tags: api, error" format
- `test_extractTags_headers`: Use markdown headers as fallback tags
- `test_loadIndexWithCache_fresh`: Load index within TTL (no warning)
- `test_loadIndexWithCache_stale`: Load stale index with warning
- `test_calculateRelevance_multiWord`: Score "error handling" query correctly
- `test_calculateRelevance_tokens`: Handle tokenized matching
- `test_knowledgeSearch_sources`: Filter by specific sources (patterns only)
- `test_knowledgeSearch_limit`: Respect result limit parameter
- `test_getFrameworkDoc_valid`: Return doc content successfully
- `test_getFrameworkDoc_traversal`: Prevent directory traversal attack

### Level 3: Integration Tests
```bash
# Test indexing
syntropy_init_project /tmp/test-project  # Should create index

# Test framework doc access
get_framework_doc "research/01-prp-system"  # Should return content

# Test unified search
knowledge_search "error handling"  # Should return results from all sources
```

### Level 4: Pattern Conformance
- Security: Path validation (no directory traversal)
- Error handling: Fast failure, actionable errors
- Performance: Index caching (no redundant scans)
- No fishy fallbacks

---

## SUCCESS CRITERIA

1. ⬜ Unified index schema implemented (`.ce/syntropy-index.json`)
2. ⬜ Knowledge scanner indexes: patterns, PRPs, memories, rules
3. ⬜ `get_framework_doc(path)` returns framework documentation
4. ⬜ `knowledge_search(query)` searches all sources
5. ⬜ Index auto-generated on `syntropy_init_project`
6. ⬜ Relevance scoring works (excerpt + tags + path + multi-word queries)
7. ⬜ Security: path validation prevents traversal
8. ⬜ Performance: index cached, no redundant scans
9. ⬜ Performance target: Knowledge search <100ms for cached index (project with <100 PRPs)
10. ⬜ Error handling: Scanner gracefully handles corrupt files
11. ⬜ Tag extraction: Supports YAML frontmatter, inline tags, and headers
12. ⬜ All tests passing (unit + integration)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Medium-High (4-5 days)
- Index schema design: 0.5 day
- Knowledge scanner: 2 days (patterns, PRPs, memories, rules)
- Framework doc accessor: 0.5 day
- Unified search: 1 day (query, scoring, limiting)
- Integration with init: 0.5 day
- Testing: 1 day

**Risk Level:** Medium
- Complex scanning logic (multiple sources)
- Index schema must be extensible
- Search relevance tuning

**Dependencies:**
- PRP-29.1 (init tool must be implemented first)
- Syntropy MCP server (existing)
- Serena MCP (optional, for memories)

**Files to Create:**
- `syntropy-mcp/src/indexer.ts`
- `syntropy-mcp/src/tools/knowledge.ts`
- `syntropy-mcp/src/tools-definition.ts` (add knowledge tools)

**Files to Modify:**
- `syntropy-mcp/src/tools/init.ts` (call indexer on init)
