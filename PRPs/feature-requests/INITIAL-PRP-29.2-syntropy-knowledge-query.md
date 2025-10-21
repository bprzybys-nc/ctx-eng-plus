# INITIAL-PRP-29.2: Syntropy Unified Knowledge Query

**Feature:** Implement unified knowledge query interface across framework docs, project PRPs, examples, and Serena memories.

---

## FEATURE

Provide a single query interface that searches all knowledge sources (framework docs, PRPs, examples, Serena memories) with semantic search capabilities.

**Goals:**
1. Implement `syntropy_get_framework_doc(doc_path)` - Fetch specific framework doc
2. Implement `syntropy_knowledge_search(query, sources?)` - Unified search across all knowledge
3. Support semantic search (not just text matching)
4. Return results with context (file location, tags, references)
5. Integrate with existing Serena memories
6. Cache frequently accessed docs (5-min TTL)
7. Support filtering by source type (framework, prp, example, memory)

**Current Problems:**
- Framework docs scattered (shipped with Syntropy, but no query tool)
- Project knowledge fragmented (PRPs separate from examples separate from memories)
- No unified search interface
- Can't find patterns across knowledge sources
- Manual grep/find commands for knowledge discovery

**Expected Outcome:**
- MCP tool: `syntropy_get_framework_doc('research/01-prp-system')` → returns doc content
- MCP tool: `syntropy_knowledge_search('error handling')` → searches all sources
- Results include: source type, file path, excerpt, tags, references
- Fast queries via cached index (`.ce/syntropy-index.json`)
- Support natural language queries: "How do I handle API errors?"

**Prerequisite:** PRP-29.1 must be completed (init tool creates index)

---

## EXAMPLES

### Example 1: Framework Doc Retrieval Tool

**Location:** `syntropy-mcp/src/tools/knowledge.ts`

```typescript
interface FrameworkDocResult {
  success: boolean;
  doc_path: string;
  content: string;
  metadata: {
    title: string;
    tags: string[];
    last_modified: string;
  };
}

export async function getFrameworkDoc(docPath: string): Promise<FrameworkDocResult> {
  // Resolve doc path relative to syntropy-mcp/docs/
  const docsRoot = path.join(__dirname, '../../docs');
  const fullPath = path.join(docsRoot, `${docPath}.md`);

  // Validate path (prevent directory traversal)
  const resolvedPath = path.resolve(fullPath);
  if (!resolvedPath.startsWith(path.resolve(docsRoot))) {
    throw new Error(
      `Invalid doc path: ${docPath}\n` +
      `🔧 Path must be relative to docs/ (e.g., 'research/01-prp-system')`
    );
  }

  // Check if file exists
  if (!await exists(resolvedPath)) {
    throw new Error(
      `Framework doc not found: ${docPath}\n` +
      `🔧 Available docs:\n` +
      `    - research/00-overview\n` +
      `    - research/01-prp-system\n` +
      `    - templates/self-healing`
    );
  }

  // Read content
  const content = await fs.readFile(resolvedPath, 'utf-8');

  // Parse metadata from frontmatter or heading
  const metadata = parseDocMetadata(content);

  return {
    success: true,
    doc_path: docPath,
    content,
    metadata
  };
}
```

**Pattern:** Secure path validation, clear error messages, metadata extraction.

### Example 2: Unified Knowledge Search Tool

**Location:** `syntropy-mcp/src/tools/knowledge.ts`

```typescript
interface SearchOptions {
  sources?: ('framework' | 'prp' | 'example' | 'memory')[];
  limit?: number;
  tags?: string[];
}

interface SearchResult {
  source_type: string;
  title: string;
  file_path: string;
  excerpt: string;
  score: number;
  tags: string[];
  referenced_by: string[];
}

interface KnowledgeSearchResult {
  success: boolean;
  query: string;
  results: SearchResult[];
  total_found: number;
  sources_searched: string[];
}

export async function knowledgeSearch(
  query: string,
  projectRoot: string,
  options?: SearchOptions
): Promise<KnowledgeSearchResult> {
  // Load cached index
  const indexPath = path.join(projectRoot, '.ce', 'syntropy-index.json');
  const index = await loadIndex(indexPath);

  // Default: search all sources
  const sources = options?.sources || ['framework', 'prp', 'example', 'memory'];
  const limit = options?.limit || 10;

  const results: SearchResult[] = [];

  // Search framework docs
  if (sources.includes('framework')) {
    const frameworkResults = await searchFrameworkDocs(query, options?.tags);
    results.push(...frameworkResults);
  }

  // Search project PRPs
  if (sources.includes('prp')) {
    const prpResults = await searchIndex(
      query,
      index.knowledge.prp_learnings,
      'prp',
      options?.tags
    );
    results.push(...prpResults);
  }

  // Search examples
  if (sources.includes('example')) {
    const exampleResults = await searchIndex(
      query,
      index.knowledge.patterns,
      'example',
      options?.tags
    );
    results.push(...exampleResults);
  }

  // Search Serena memories
  if (sources.includes('memory')) {
    const memoryResults = await searchIndex(
      query,
      index.knowledge.memories,
      'memory',
      options?.tags
    );
    results.push(...memoryResults);
  }

  // Sort by relevance score
  results.sort((a, b) => b.score - a.score);

  // Apply limit
  const limitedResults = results.slice(0, limit);

  return {
    success: true,
    query,
    results: limitedResults,
    total_found: results.length,
    sources_searched: sources
  };
}
```

**Pattern:** Unified interface, relevance scoring, source filtering, limit control.

### Example 3: Semantic Search Implementation

**Location:** `syntropy-mcp/src/tools/search.ts`

```typescript
interface SemanticSearcher {
  search(query: string): ScoredResult[];
}

// Simple TF-IDF based semantic search (no external deps)
export class TFIDFSearcher implements SemanticSearcher {
  private idf: Map<string, number> = new Map();
  private corpus: Document[];

  constructor(documents: Document[]) {
    this.corpus = documents;
    this.buildIDF(documents);
  }

  search(query: string): ScoredResult[] {
    // Search across constructor corpus only (IDF pre-built)
    const queryTokens = this.tokenize(query);
    const scores: ScoredResult[] = [];

    for (const doc of this.corpus) {
      const docTokens = this.tokenize(doc.content);
      const score = this.computeScore(queryTokens, docTokens);

      scores.push({
        document: doc,
        score,
        excerpt: this.extractExcerpt(doc.content, queryTokens)
      });
    }

    return scores.sort((a, b) => b.score - a.score);
  }

  private tokenize(text: string): string[] {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(token => token.length > 2);
  }

  private computeScore(queryTokens: string[], docTokens: string[]): number {
    let score = 0;

    for (const token of queryTokens) {
      const tf = docTokens.filter(t => t === token).length / docTokens.length;
      const idf = this.idf.get(token) || 0;
      score += tf * idf;
    }

    return score;
  }

  private extractExcerpt(content: string, queryTokens: string[]): string {
    // Find sentence containing most query tokens
    const sentences = content.split(/[.!?]+/);
    let bestSentence = sentences[0];
    let maxMatches = 0;

    for (const sentence of sentences) {
      const matches = queryTokens.filter(token =>
        sentence.toLowerCase().includes(token)
      ).length;

      if (matches > maxMatches) {
        maxMatches = matches;
        bestSentence = sentence;
      }
    }

    return bestSentence.trim().substring(0, 200) + '...';
  }

  private buildIDF(documents: Document[]): void {
    const tokenDocs = new Map<string, number>();

    for (const doc of documents) {
      const tokens = new Set(this.tokenize(doc.content));
      for (const token of tokens) {
        tokenDocs.set(token, (tokenDocs.get(token) || 0) + 1);
      }
    }

    for (const [token, docCount] of tokenDocs.entries()) {
      this.idf.set(token, Math.log(documents.length / docCount));
    }
  }
}
```

**Pattern:** Simple semantic search, no external dependencies, TF-IDF scoring, excerpt extraction.

### Example 4: Index Cache with TTL

**Location:** `syntropy-mcp/src/tools/cache.ts`

```typescript
interface CachedIndex {
  index: KnowledgeIndex;
  loaded_at: number;
  ttl_ms: number;
}

export class IndexCache {
  private cache: Map<string, CachedIndex> = new Map();
  private defaultTTL = 5 * 60 * 1000; // 5 minutes

  async loadIndex(indexPath: string, ttl?: number): Promise<KnowledgeIndex> {
    const cached = this.cache.get(indexPath);

    // Check if cached and not expired
    if (cached) {
      const age = Date.now() - cached.loaded_at;
      if (age < cached.ttl_ms) {
        return cached.index;
      }
    }

    // Load from disk
    const content = await fs.readFile(indexPath, 'utf-8');
    const index = JSON.parse(content) as KnowledgeIndex;

    // Cache with TTL
    this.cache.set(indexPath, {
      index,
      loaded_at: Date.now(),
      ttl_ms: ttl || this.defaultTTL
    });

    return index;
  }

  invalidate(indexPath: string): void {
    this.cache.delete(indexPath);
  }

  invalidateAll(): void {
    this.cache.clear();
  }
}
```

**Pattern:** TTL-based caching, manual invalidation, per-path cache entries.

### Example 5: Query Tool Definition

**Location:** `syntropy-mcp/src/tools-definition.ts`

```typescript
{
  name: "syntropy_get_framework_doc",
  description: "Retrieve specific Context Engineering framework documentation",
  inputSchema: {
    type: "object",
    properties: {
      doc_path: {
        type: "string",
        description: "Path to doc relative to docs/ (e.g., 'research/01-prp-system')"
      }
    },
    required: ["doc_path"]
  }
},
{
  name: "syntropy_knowledge_search",
  description: "Search across all knowledge sources (framework, PRPs, examples, memories)",
  inputSchema: {
    type: "object",
    properties: {
      query: {
        type: "string",
        description: "Search query (natural language or keywords)"
      },
      project_root: {
        type: "string",
        description: "Absolute path to project root"
      },
      options: {
        type: "object",
        properties: {
          sources: {
            type: "array",
            items: {
              type: "string",
              enum: ["framework", "prp", "example", "memory"]
            },
            description: "Knowledge sources to search (default: all)"
          },
          limit: {
            type: "number",
            description: "Maximum results to return (default: 10)"
          },
          tags: {
            type: "array",
            items: { type: "string" },
            description: "Filter by tags"
          }
        }
      }
    },
    required: ["query", "project_root"]
  }
}
```

**Pattern:** Clear input schemas, optional parameters with defaults, enum validation.

---

## DOCUMENTATION

### Search Algorithm

**TF-IDF (Term Frequency-Inverse Document Frequency):**
- **TF**: How often term appears in document (relevance)
- **IDF**: How rare term is across all documents (importance)
- **Score**: TF × IDF (higher = more relevant)

**No External Dependencies:**
- Implement TF-IDF from scratch (stdlib only)
- Avoid vector DB complexity (overkill for <1000 docs)
- Fast enough for real-time queries (<100ms)

### Framework Docs Structure

**Available Docs (from PRP-29.1):**
- `syntropy-mcp/docs/research/00-overview.md`
- `syntropy-mcp/docs/research/01-prp-system.md`
- `syntropy-mcp/docs/research/02-11-*.md`
- `syntropy-mcp/docs/templates/self-healing.md`
- `syntropy-mcp/docs/templates/kiss.md`
- `syntropy-mcp/docs/prp-yaml-schema.md`

**Doc Path Format:**
- Relative to `syntropy-mcp/docs/`
- Omit `.md` extension
- Examples: `research/01-prp-system`, `templates/self-healing`

### Index Schema (from PRP-29.1)

**Location:** `.ce/syntropy-index.json`

```typescript
interface KnowledgeIndex {
  knowledge: {
    patterns: Record<string, PatternInfo>;      // examples/
    prp_learnings: Record<string, PRPInfo>;     // PRPs/
    memories: Record<string, MemoryInfo>;       // .serena/memories/
  };
}
```

**Search targets:**
- Framework docs: `syntropy-mcp/docs/**/*.md`
- Patterns: `index.knowledge.patterns`
- PRPs: `index.knowledge.prp_learnings`
- Memories: `index.knowledge.memories`

---

## OTHER CONSIDERATIONS

### Performance

- Cache index in memory (5-min TTL)
- Lazy load framework docs (on first access)
- Build TF-IDF index once per search (reuse for multiple queries)
- Limit search results (default 10, max 100)
- Extract excerpts efficiently (sentence-level matching)

### Security

- Validate doc paths (prevent directory traversal)
- Sanitize query input (prevent injection)
- No secret exposure in results
- Validate project_root exists and is readable

### Error Handling

- Framework doc not found → suggest available docs
- Index missing → prompt to run init
- Index stale (>5 min old) → auto-reload
- Empty query → return error with guidance
- No results found → suggest broader query

### Cache Invalidation

**Automatic:**
- TTL expiration (5 minutes)
- Index file modification detected

**Manual:**
- After `/update-context` runs
- After new PRP created
- After example added

### Search Quality

**Ranking Formula:**
```
final_score = tfidf_score × (1 + tag_boost + title_boost + recency_boost)

Where:
- tfidf_score: Base TF-IDF relevance (0.0 - 1.0)
- tag_boost: +0.2 if query terms match document tags
- title_boost: +0.3 if query terms appear in document title
- recency_boost: +0.1 for documents modified in last 30 days
```

**Ranking Factors:**
- TF-IDF score (primary relevance measure)
- Tag matches (boost +0.2) - query terms in document tags
- Title matches (boost +0.3) - query terms in document title
- Recent documents (recency bias +0.1) - modified within 30 days

**Excerpt Quality:**
- Sentence containing most query tokens
- Max 200 chars
- Trim at word boundary

### Integration with Serena

**Serena Memories:**
- Indexed in `.ce/syntropy-index.json` by init tool (PRP-29.1)
- Searchable via `knowledge_search(sources=['memory'])`
- No duplicate storage (reference memory files directly)

**Memory Format:**
```json
{
  "tool-usage-guide": {
    "source": ".serena/memories/tool-usage-guide.md",
    "tags": ["tools", "mcp"],
    "content": "..." // Cached excerpt
  }
}
```

### Testing Strategy

**Unit Tests:**
```typescript
describe('TFIDFSearcher', () => {
  it('ranks documents by relevance', () => {
    const docs = [
      { id: '1', content: 'error handling patterns' },
      { id: '2', content: 'API client implementation' },
      { id: '3', content: 'error recovery and retry logic' }
    ];
    const searcher = new TFIDFSearcher(docs);
    const results = searcher.search('error handling');

    expect(results[0].document.id).toBe('1'); // Best match
    expect(results[0].score).toBeGreaterThan(results[1].score);
  });

  it('extracts relevant excerpt', () => {
    const searcher = new TFIDFSearcher([{
      id: '1',
      content: 'Some intro text. Error handling is critical. More text.'
    }]);
    const results = searcher.search('error handling');
    expect(results[0].excerpt).toContain('Error handling is critical');
  });
});

describe('knowledgeSearch', () => {
  it('searches all sources by default', async () => {
    const result = await knowledgeSearch('API errors', '/tmp/project');
    expect(result.sources_searched).toEqual(['framework', 'prp', 'example', 'memory']);
  });

  it('filters by source type', async () => {
    const result = await knowledgeSearch('API errors', '/tmp/project', {
      sources: ['framework', 'prp']
    });
    expect(result.sources_searched).toEqual(['framework', 'prp']);
  });

  it('respects result limit', async () => {
    const result = await knowledgeSearch('error', '/tmp/project', { limit: 5 });
    expect(result.results.length).toBeLessThanOrEqual(5);
  });
});
```

**Integration Tests:**
```bash
# Test framework doc retrieval
syntropy get_framework_doc 'research/01-prp-system' > output.json
jq -e '.success == true' output.json
jq -e '.content | length > 100' output.json  # Has content

# Test knowledge search
syntropy knowledge_search 'error handling' /tmp/test-project > results.json
jq -e '.total_found > 0' results.json
jq -e '.results[0].excerpt | length > 0' results.json

# Test source filtering
syntropy knowledge_search 'API' /tmp/test-project --sources framework,prp
jq -e '.sources_searched == ["framework", "prp"]' results.json
```

**E2E Tests:**
```bash
# Full workflow: init → query → verify results
syntropy init /tmp/test-project
cd /tmp/test-project

# Create test knowledge
echo "# API Error Handling\nUse try-catch blocks" > examples/api-errors.md

# Reindex
syntropy sync .

# Search should find example
syntropy knowledge_search 'API error' . > results.json
jq -e '.results[] | select(.source_type == "example")' results.json
```

### Constraints

- No external search dependencies (TF-IDF implementation from scratch)
- Index cached locally (5-min TTL)
- Fast queries (<100ms for typical case)
- Works offline (no network required)

### Gotchas

1. **Framework docs path:** Relative to `syntropy-mcp/docs/`, omit `.md`
2. **Index prerequisite:** PRP-29.1 must complete first (creates index)
3. **Cache invalidation:** Manual invalidation needed after knowledge changes
4. **Search scope:** Default searches ALL sources (can be expensive)
5. **Result limit:** Default 10, max 100 (prevent overwhelming output)
6. **Excerpt extraction:** Sentence-level, not paragraph (better context)

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
cd syntropy-mcp && npm run build
cd syntropy-mcp && npm run lint
```

### Level 2: Unit Tests
```bash
cd syntropy-mcp && npm test src/tools/search.test.ts
cd syntropy-mcp && npm test src/tools/cache.test.ts
cd syntropy-mcp && npm test src/tools/knowledge.test.ts
```

### Level 3: Integration Tests
```bash
# Framework doc retrieval
syntropy get_framework_doc 'research/01-prp-system' --json

# Knowledge search (all sources)
syntropy knowledge_search 'error handling' /tmp/test-project --json

# Filtered search
syntropy knowledge_search 'API' /tmp/test-project --sources framework,prp --limit 5

# E2E test on test-certinia (commit 9137b61)
# IMPORTANT: Run on branch or ensure index is gitignored
cd ~/nc-rc/test-certinia && git checkout -b test-prp-29-2-query

# Prerequisite: Run init first to create index (PRP-29.1)
syntropy init . --json

# Search existing PRPs (context-engineering/PRPs/)
syntropy knowledge_search 'job isolation' . --sources prp --json
# Expected: Find PRP-8.6, PRP-8.7 job isolation PRPs

# Search existing examples (context-engineering/examples/)
syntropy knowledge_search 'certinia output' . --sources example --json
# Expected: Find certinia-output-example.md

# Search Serena memories (.serena/memories/)
syntropy knowledge_search 'architecture patterns' . --sources memory --json
# Expected: Find unified_architecture_patterns.md, dual_path_architecture_pattern.md

# Unified search across all sources
syntropy knowledge_search 'multi-tab' . --json
# Expected: Results from PRPs (PRP-7.1, PRP-7.2), examples, and memories

# Cleanup after validation:
cd ~/nc-rc/test-certinia && git checkout main && git branch -D test-prp-29-2-query
git clean -fd .ce .claude docs
```

### Level 4: Pattern Conformance
- Error handling: Fast failure with 🔧 troubleshooting ✅
- No fishy fallbacks: All errors actionable ✅
- Security: Path validation prevents traversal ✅
- Performance: Cache with TTL, no unnecessary reloads ✅

---

## SUCCESS CRITERIA

1. ⬜ MCP tool `syntropy_get_framework_doc` functional
2. ⬜ MCP tool `syntropy_knowledge_search` functional
3. ⬜ Framework docs accessible via tool
4. ⬜ Search returns results from all sources
5. ⬜ Source filtering works (framework, prp, example, memory)
6. ⬜ Results include excerpt + score + metadata
7. ⬜ Cache with 5-min TTL working
8. ⬜ Search quality validated (relevant results ranked higher)
9. ⬜ Integration with Serena memories verified
10. ⬜ All tests passing (unit + integration + E2E)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Medium (4-5 days)
- TF-IDF implementation: 1 day
- Framework doc tool: 0.5 days
- Knowledge search tool: 1.5 days
- Cache implementation: 0.5 days
- Testing: 1-1.5 days

**Risk Level:** Low-Medium
- TF-IDF implementation straightforward (no ML complexity)
- Index schema already defined (PRP-29.1)
- No external dependencies (stdlib only)

**Dependencies:**
- PRP-29.1 (init tool must complete first)
- Syntropy MCP server (existing)
- Node.js fs/promises, path (stdlib)

**Files to Create:**
- `syntropy-mcp/src/tools/knowledge.ts` - get_framework_doc, knowledge_search
- `syntropy-mcp/src/tools/search.ts` - TF-IDF searcher
- `syntropy-mcp/src/tools/cache.ts` - Index cache with TTL
- `syntropy-mcp/tests/tools/knowledge.test.ts` - Unit tests
- `syntropy-mcp/tests/tools/search.test.ts` - Search tests

**Files to Modify:**
- `syntropy-mcp/src/tools-definition.ts` - Add knowledge tools
- `syntropy-mcp/src/index.ts` - Register knowledge handlers
