# Feature: Vector DB Migration for NLP-Powered Vacuum

## FEATURE

Migrate batch 46 NLP implementation from pairwise O(N×M) comparisons to vector database O(log N) queries using ChromaDB.

**Goal**: Reduce vacuum scan time from 10-15s (100 docs × 45 PRPs = 4,500 comparisons) to <1s (100 indexed queries) while enabling semantic search capabilities.

**Acceptance Criteria**:

1. **AC1: ChromaDB Integration with Persistent Storage**
   - Root cause: Current DocumentSimilarity.compare() requires O(N×M) pairwise comparisons
   - Validation: ChromaDB collection persists to `.ce/vector-db/` across runs
   - Test: Index 45 PRPs, query, restart process, query again (no re-indexing)

2. **AC2: PRPLifecycleDocsStrategy Uses Vector Queries**
   - Root cause: Strategy iterates `for prp in executed_prps: compare(md_file, prp)` (4,500 calls for 100 docs)
   - Validation: Strategy calls `vector_db.query(md_file, top_k=3)` instead (100 calls)
   - Test: Run vacuum, verify <100 similarity computations via debug logs

3. **AC3: Semantic Search CLI Command**
   - Root cause: No way to query codebase semantically ("find PRPs about authentication")
   - Validation: `uv run ce search "JWT authentication"` returns top 5 relevant PRPs
   - Test: Query returns PRP-23 (auth implementation) even if "JWT" not in title

4. **AC4: Performance Target: 95% Reduction**
   - Root cause: First-run embedding computation dominates runtime (10-15s)
   - Validation: Subsequent vacuum runs complete in <1s (cached embeddings + vector index)
   - Test: Time `uv run ce vacuum` twice, second run <1s

**Files to Modify**:
- `tools/ce/nlp/similarity.py` (add VectorDBSimilarity class)
- `tools/ce/nlp/__init__.py` (export VectorDBSimilarity)
- `tools/ce/vacuum_strategies/prp_lifecycle_docs.py` (use vector queries)
- `tools/ce/cli.py` (add `search` subcommand)
- `tools/pyproject.toml` (add chromadb dependency)

**Dependencies**: PRP-46.1.1 (ce.nlp module), PRP-46.2.1 (PRPLifecycleDocsStrategy)

## EXAMPLES

### Current Implementation (Batch 46)

```python
# PRPLifecycleDocsStrategy._check_initial_md (O(N×M))
def _check_initial_md(self, md_file: Path, executed_prps: List[Path]):
    best_match = None
    best_score = 0.0

    for prp_path in executed_prps:  # 45 iterations
        similarity = self.nlp.compare(md_file, prp_path)  # EXPENSIVE
        if similarity > best_score:
            best_score = similarity
            best_match = prp_path

    # 100 INITIAL.md × 45 PRPs = 4,500 compare() calls
```

**Problems**:
- 4,500 similarity computations per vacuum run
- No caching across different md_files (only within file via EmbeddingCache)
- Can't do multi-doc queries ("find all PRPs about feature X")

### Vector DB Implementation (PRP-47)

```python
# VectorDBSimilarity class (O(log N) with HNSW index)
from chromadb import PersistentClient

class VectorDBSimilarity:
    """Vector database for semantic similarity using ChromaDB."""

    def __init__(self, db_path: Path = None):
        if db_path is None:
            db_path = Path(".ce/vector-db")

        self.client = PersistentClient(path=str(db_path))
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collections = {}

    def index_collection(self, name: str, files: List[Path]):
        """Index files into named collection (one-time operation)."""
        collection = self.client.get_or_create_collection(name)

        for file_path in files:
            # Check if already indexed (skip if mtime unchanged)
            existing = collection.get(ids=[str(file_path)])
            if existing and self._mtime_unchanged(file_path, existing):
                continue

            # Compute embedding and index
            text = self._read_and_normalize(file_path)
            embedding = self.model.encode(text).tolist()

            collection.upsert(
                embeddings=[embedding],
                metadatas=[{
                    "path": str(file_path),
                    "mtime": int(file_path.stat().st_mtime),
                    "prp_id": file_path.stem
                }],
                ids=[str(file_path)]
            )

    def query(self, file_path: Path, collection_name: str, top_k: int = 3):
        """Query collection for top K similar documents.

        Returns:
            List of (Path, similarity_score) tuples
        """
        collection = self.collections.get(collection_name)
        if not collection:
            collection = self.client.get_collection(collection_name)
            self.collections[collection_name] = collection

        # Compute query embedding
        text = self._read_and_normalize(file_path)
        embedding = self.model.encode(text).tolist()

        # Vector search (O(log N) with HNSW index)
        results = collection.query(
            query_embeddings=[embedding],
            n_results=top_k
        )

        # Convert to (Path, score) tuples
        matches = []
        for i, doc_id in enumerate(results['ids'][0]):
            path = Path(doc_id)
            # ChromaDB returns L2 distance, convert to cosine similarity
            distance = results['distances'][0][i]
            similarity = 1 / (1 + distance)  # Normalize to 0-1
            matches.append((path, similarity))

        return matches

# Updated PRPLifecycleDocsStrategy (O(N))
def __init__(self, project_root: Path, scan_path: Path = None):
    super().__init__(project_root, scan_path)
    self.nlp = VectorDBSimilarity()

    # Index executed PRPs once at initialization
    executed_dir = project_root / "PRPs" / "executed"
    if executed_dir.exists():
        executed_prps = list(executed_dir.glob("PRP-*.md"))
        self.nlp.index_collection("executed_prps", executed_prps)

def _check_initial_md(self, md_file: Path, executed_prps: List[Path]):
    # Vector query instead of loop (O(log N))
    matches = self.nlp.query(md_file, "executed_prps", top_k=3)

    if matches and matches[0][1] >= 0.75:  # Best match >= 75%
        best_match, best_score = matches[0]
        prp_id = best_match.stem.split('-')[1]

        return CleanupCandidate(
            path=md_file,
            reason=f"Generated as PRP-{prp_id} (NLP similarity: {best_score:.2f})",
            confidence=best_score * 100,
            # ... rest of fields
        )

    return None

# 100 INITIAL.md × 1 query each = 100 calls (45x reduction)
```

### Semantic Search CLI

```bash
# New command: ce search
uv run ce search "JWT authentication implementation"

# Output:
# 🔍 Semantic search results:
#
# 1. PRP-23-auth-jwt-migration.md (0.89 similarity)
#    Migrated authentication from BasicAuth to JWT tokens
#
# 2. PRP-12-api-security.md (0.76 similarity)
#    Added JWT token validation middleware
#
# 3. Feature-Auth-Refresh-Tokens.md (0.68 similarity)
#    Feature request: Implement JWT refresh token rotation
```

**Implementation**:
```python
# tools/ce/cli.py - add search subcommand
def search_command(args):
    """Semantic search across PRPs and docs."""
    from ce.nlp import VectorDBSimilarity

    vector_db = VectorDBSimilarity()

    # Index all markdown files if needed
    project_root = Path.cwd()
    all_docs = list(project_root.rglob("*.md"))
    vector_db.index_collection("all_docs", all_docs)

    # Perform text query (not file-based)
    results = vector_db.query_text(args.query, "all_docs", top_k=args.top_k)

    print(f"🔍 Semantic search results for: {args.query}\n")
    for i, (path, score) in enumerate(results, 1):
        rel_path = path.relative_to(project_root)
        print(f"{i}. {rel_path} ({score:.2f} similarity)")

        # Show first line of content
        first_line = path.read_text().split('\n')[0].strip('#').strip()
        print(f"   {first_line}\n")
```

## DOCUMENTATION

**ChromaDB**:
- Local-first vector database (no server required)
- Persistent storage to disk
- HNSW index for O(log N) similarity search
- Built-in metadata filtering
- Installation: `uv add chromadb`

**Sentence Transformers** (already installed from PRP-46.1.1):
- all-MiniLM-L6-v2 model (384-dim embeddings)
- ~90MB model size (cached to ~/.cache/huggingface/)

**Performance**:
- Indexing: ~20ms per document (one-time cost)
- Query: ~5-10ms per query (vs ~200ms for pairwise compare)
- Storage: ~1KB per document (embeddings + metadata)
- 100 PRPs = ~100KB vector DB

## OTHER CONSIDERATIONS

**Backward Compatibility**:
- Keep DocumentSimilarity.compare() for ad-hoc comparisons
- VectorDBSimilarity used only for bulk operations (vacuum strategies)
- Gradual migration: strategies can opt-in to vector DB

**Index Invalidation**:
- Check file mtime before querying
- Re-index only modified files (incremental updates)
- Full rebuild: `rm -rf .ce/vector-db`

**Multi-Collection Support**:
- "executed_prps" - All PRPs in PRPs/executed/
- "feature_requests" - All docs in PRPs/feature-requests/
- "all_docs" - Full codebase markdown (for semantic search)
- "code_files" - Python files (future: code search)

**Query Types**:
1. **File-based**: `query(file_path, collection, top_k)` - Current use case
2. **Text-based**: `query_text(text, collection, top_k)` - For CLI search
3. **Metadata filters**: `query(..., where={"prp_id": {"$gte": "40"}})` - Time-based queries

**Deduplication Use Case**:
```python
# Find duplicate PRPs (cluster analysis)
vector_db = VectorDBSimilarity()
vector_db.index_collection("all_prps", all_prp_files)

# Query each PRP against all others
duplicates = []
for prp in all_prp_files:
    matches = vector_db.query(prp, "all_prps", top_k=5)
    # Skip self-match (distance = 0)
    similar = [m for m in matches[1:] if m[1] > 0.95]
    if similar:
        duplicates.append((prp, similar))

# Output: Groups of near-duplicate PRPs
```

**Test Coverage Analysis**:
```python
# Find tests related to a module
vector_db.index_collection("tests", test_files)
vector_db.index_collection("modules", source_files)

module_path = Path("ce/vacuum.py")
related_tests = vector_db.query(module_path, "tests", top_k=10)

# Returns: Tests semantically related to vacuum.py
# Even if they don't import it directly
```

**Complexity Scoring**:
```python
# Score PRPs by semantic complexity
reference_complex = "distributed systems refactoring with async message queues"
reference_simple = "update button color in UI"

for prp in pending_prps:
    complex_score = vector_db.compare_text(prp, reference_complex)
    simple_score = vector_db.compare_text(prp, reference_simple)

    if complex_score > simple_score:
        print(f"{prp}: COMPLEX (score: {complex_score:.2f})")
    else:
        print(f"{prp}: SIMPLE (score: {simple_score:.2f})")
```

**Drift Detection**:
```python
# Find pending feature requests similar to recent PRPs
recent_prps = [p for p in executed_prps if p.stat().st_mtime > cutoff_date]
vector_db.index_collection("recent_prps", recent_prps)

for feature_request in pending_requests:
    conflicts = vector_db.query(feature_request, "recent_prps", top_k=3)
    if conflicts and conflicts[0][1] > 0.85:
        print(f"⚠️ {feature_request} may conflict with {conflicts[0][0]}")
```

## Recommendation: Switch to PRP-47 or Finalize Batch 46?

**Arguments for PRP-47 First**:
1. **Batch 46 Performance Issue**: 4,500 comparisons is already hitting limits with 100 docs
2. **Cleaner Architecture**: Vector DB eliminates nested loops in ALL strategies (46.2.1, 46.2.2, 46.3.1)
3. **Unlocks New Features**: Semantic search, dedup, coverage analysis (mentioned in your question)
4. **One-Time Migration**: Easier to migrate now (3 PRPs done) vs later (6 PRPs + tech debt)

**Arguments for Finishing Batch 46 First**:
1. **Working Implementation**: Batch 46 functional, just not optimal
2. **PRP-46.2.2, 46.3.1, 46.4.1 Almost Ready**: We're 50% done with batch 46
3. **Test Before Optimize**: Validate NLP approach works, then optimize with vector DB
4. **Smaller Scope**: PRP-47 is architectural change, batch 46 is feature delivery

## My Recommendation

**Finish Batch 46 first, then PRP-47**

**Reasoning**:
1. **Proof of Concept**: Batch 46 validates the NLP approach works (semantic similarity > naive text match)
2. **Measure Before Optimize**: Run vacuum with 100 real docs, measure actual bottleneck
3. **Clean Migration**: PRP-47 can refactor all 4 completed strategies (46.2.1, 46.2.2, 46.3.1, 46.4.1) in one pass
4. **Low Risk**: Batch 46 caching already makes performance acceptable (<3s with cache)

**Execution Plan**:
```
Today:
- Complete PRP-46.2.2 (Enhance Existing Strategies) - 1h
- Complete PRP-46.3.1 (LLM Batch Analyzer) - 1.5h
- Complete PRP-46.4.1 (Integration) - 1h
- Commit batch 46 as complete

Tomorrow:
- Create PRP-47 from this INITIAL
- Migrate all 6 strategies to VectorDBSimilarity
- Add semantic search CLI
- Benchmark: 4,500 calls → 100 calls (45x reduction)
```

**Why This Order Works**:
- Batch 46 = **Feature delivery** (NLP-powered vacuum works end-to-end)
- PRP-47 = **Performance optimization** (same features, 45x faster)
- Can deploy batch 46 today, PRP-47 is enhancement not blocker

Want me to proceed with finishing batch 46 (PRPs 46.2.2, 46.3.1, 46.4.1), or pivot to PRP-47 now?
