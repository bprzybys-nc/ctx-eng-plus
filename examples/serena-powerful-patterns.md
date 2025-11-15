# Serena MCP: Useful Pattern Combinations vs. Anti-patterns

Effectively using Serena MCP involves leveraging its deep, symbol-level understanding of code to guide the AI, rather than forcing manual or inefficient methods.

**Contents**:
- [Chapter 1: Basic Patterns](#chapter-1-basic-patterns) - Symbol navigation, debugging, semantic search
- [Chapter 2: Vector DB Graph Patterns](#chapter-2-vector-db-graph-patterns) - Advanced patterns when Serena memories are serialized to graph databases

---

# Chapter 1: Basic Patterns

## Useful Pattern Combinations

| Pattern Combination | Description | Example Prompt/Action |
|---------------------|-------------|----------------------|
| Semantic Search + Feature Implementation | Combine the ability to semantically find relevant existing code with the task of adding a new feature. The AI uses existing, correct patterns as templates. | "Find all functions related to `user_authentication` and use them as a guide to implement the new OAuth flow". |
| Symbolic Navigation + Deep Debugging | Use Serena's Language Server Protocol (LSP) capabilities to trace a bug through a complex call stack by locating symbol definitions and references across the codebase. | "Trace the data flow from the `process_payment` function to the `update_database_status` method to find where the status is incorrectly set". |
| Planning Mode + Semantic Editing | Work with the AI in "planning mode" to outline the sequence of edits using Serena's semantic tools. This ensures the plan is sound before execution, optimizing token usage and results. | "Plan the refactoring of the `ConfigLoader` class using Serena's editing tools, and I will review the steps before you proceed". |
| Hybrid Search + RAG Implementation | Use Serena's hybrid search (keyword + semantic) to pull in the most relevant code snippets, which are then integrated into the AI's context via Retrieval-Augmented Generation (RAG). This balances precision and the ability to handle ambiguity. | "Use hybrid search to find the `API_KEY` handling logic in `utils.py` and present it in context for modification". |

## Anti-patterns and How to Avoid Them

| Anti-pattern | Description | Pitfall/Constraint | How to Avoid |
|--------------|-------------|-------------------|--------------|
| "String Search" Mindset | Treating Serena as a simple text search tool, rather than a semantic one, leading to generic, keyword-based queries. | Misses relevant context, uses more tokens, results in less precise edits. | Use natural language queries focusing on intent, like "where do we define the `User` model?", instead of just searching for the string "User". |
| Ignoring the Onboarding Process | Immediately attempting complex tasks without allowing Serena to fully index the codebase and create its memory graph. | The AI struggles with context and performs poorly on larger projects, potentially failing to find relevant information. | Always ensure Serena completes its initial indexing (stored in the `.serena/memories` directory) when you first start a project. |
| Over-engineering with Patterns | Applying complex design patterns when a simpler, non-pattern way would suffice, making the code unnecessarily complex. | Code becomes harder to read and maintain; the AI might generate overly complex solutions. | Stick to the YAGNI (You Aren't Gonna Need It) principle; use patterns only when a clear need is identified during development. |
| Concurrent Development Issues | Running multiple instances or worktrees with a single Serena instance pointing to the same main repository. | Changes may be applied to the wrong repository instance, leading to confusion and lost work. | Configure each concurrent development environment with its own dedicated Serena instance and configuration file (`myproject.yml`). |
| Granting Excessive Permissions Blindly | Approving all of the AI's plan steps or requests for permissions without careful review in "plan mode". | The AI might make unintended, sweeping changes or introduce security vulnerabilities. | Use "plan mode" and meticulously review each step the AI suggests before approval, especially for write/edit operations. |

---

# Chapter 2: Vector DB Graph Patterns

**Context**: When Serena's memory system is serialized to a vector database with graph-based relationships (as demonstrated in [ce-framework-meta](https://github.com/bprzybysz/ce-framework-meta) and [perplexity-space-context](https://github.com/bprzybysz/perplexity-space-context)), powerful emergent patterns enable spatial knowledge representation, multi-agent collaboration, and automated pattern discovery.

**Prerequisites**:
- Vector DB integration (e.g., Pinecone, Weaviate, Qdrant)
- Graph schema following CE Framework v2.0 patterns
- Serena memories tagged with semantic metadata

## Advanced Pattern Combinations

| Pattern Combination | Description | Example Use Case | Implementation Notes |
|---------------------|-------------|-----------------|---------------------|
| **Semantic Edge Formation + Mind Maps** | Memories are nodes; vector similarity creates edges. Query a concept → retrieve semantic neighborhood → render as mind map with distance-based clustering. | "Show me all authentication-related patterns as a mind map" retrieves `auth-strategy`, `session-management`, `token-validation` memories and renders spatial relationships based on cosine similarity. | Use threshold (e.g., >0.75 similarity) for edge creation. Cluster algorithms: DBSCAN or hierarchical clustering on embedding space. |
| **Agentic Pattern Composition** | CE Framework defines 6 patterns (Observer, Facade, Cascade, Sequential, Validation, Composition). Tag memories with pattern types; compose workflows via graph queries. | `Sequential(Validation(Observer))` = "Watch for code changes, validate them, process in order". Query: "Find all memories matching Validation pattern AND linked to testing workflows". | Store pattern tags in memory metadata. Use graph traversal to compose: `MATCH (m:Memory)-[:IMPLEMENTS]->(p:Pattern {type: 'Validation'})`. |
| **Temporal Evolution Tracking** | Each PRP cycle creates memories. Graph edges represent evolution: `auth-v1` → `auth-v2` → `auth-refactor`. Query temporal chains with semantic deltas. | "How did authentication evolve from PRP-5 to PRP-23?" returns chain with diff embeddings showing conceptual drift over time. | Add `EVOLVED_FROM` edges with timestamps. Compute embedding deltas: `cosine_distance(v1_embedding, v2_embedding)` as drift metric. |
| **Multi-Agent Shared Memory Graph** | Multiple agents (code-gen, test-gen, doc-gen) write to shared graph. Semantic links auto-created. No explicit coordination needed. | Test agent writes "test-coverage-report". Code agent queries "what needs testing?" → semantic search returns test-coverage memory. Doc agent queries "document X" → finds both code and test memories. | Use namespaced memory types: `agent:code-gen`, `agent:test-gen`. Vector DB auto-links via embedding proximity. Agent reads top-K similar memories. |
| **Semantic Drift Detection** | Compute vector distance between current codebase embeddings and memory graph. Large distance = drift. Automates manual `ce context health` analysis. | "Authentication implementation drifted 0.42 from `auth-pattern` memory (threshold: 0.3). Suggest re-alignment." | Embed current code via AST analysis. Compare to `serena_read_memory('auth-pattern')` embedding. Alert if distance > threshold. |
| **Pattern Mining from Topology** | Analyze graph structure to discover recurring subgraphs. If "bug-fix" memories consistently link to "missing-validation", the pattern "validation gaps cause bugs" emerges. | Graph query: `MATCH (b:Memory {type: 'bug-fix'})-[:CAUSED_BY]->(v:Memory {type: 'missing-validation'})` returns 15 instances → infer causal pattern. | Use graph algorithms: Frequent subgraph mining (gSpan, FFSM). Minimum support: 3 occurrences. Store mined patterns as new memory nodes. |
| **Context Injection Optimization** | Instead of loading all memories, vector search retrieves top-K semantically relevant ones for current task. Solves token budget limits while maintaining relevance. | Working on authentication? Inject top-10 auth-related memories (cosine similarity >0.8). Total tokens: 5k vs 50k for all memories. | Embed current task description. Query: `SELECT * FROM memories ORDER BY cosine_similarity(task_embedding, memory_embedding) DESC LIMIT 10`. |
| **Cross-Project Pattern Transfer** | Multiple projects share vector DB. Patterns from ProjectA automatically available to ProjectB via semantic search. | ProjectB implements authentication → query "auth patterns" → returns ProjectA's `oauth-flow` memory (cosine similarity 0.85) as template. | Namespace memories by project: `project:A:auth-pattern`. Cross-project search: `WHERE project != 'current' AND similarity > 0.75`. Require manual approval for cross-project transfers. |

## Advanced Anti-patterns in Graph Systems

| Anti-pattern | Description | Pitfall/Constraint | How to Avoid |
|--------------|-------------|-------------------|--------------|
| **Graph Overfitting** | Creating too many fine-grained memories → graph becomes dense → semantic search returns noise. | 1000+ memories about "authentication" makes queries ambiguous. Top-K results contain redundant or marginally relevant nodes. | Consolidate similar memories. Use hierarchical structure: `auth` (parent) → `oauth`, `jwt`, `session` (children). Limit memories per concept: 5-10 max. |
| **Ignoring Temporal Invalidation** | Old memories remain in graph forever → outdated patterns contaminate queries. | Query "current auth strategy" returns PRP-5 memory from 6 months ago, which was superseded by PRP-23. | Add `valid_from`, `valid_until` timestamps. Filter queries: `WHERE valid_until > NOW() OR valid_until IS NULL`. Archive obsolete memories instead of deleting. |
| **Embedding Drift from Code Changes** | Codebase evolves but memory embeddings stay static → semantic search becomes inaccurate. | Memory says "we use bcrypt" but code switched to argon2 → drift = 0.6 → alerts fire but memory not updated. | Re-embed memories on major refactors. Trigger: `ce update-context` recomputes embeddings for affected memories. Store embedding version to track staleness. |
| **Namespace Pollution** | Multiple agents write memories without coordination → duplicate or conflicting nodes. | Code-gen agent writes `auth-strategy` memory. Doc-gen agent writes `authentication-strategy` memory. Semantic similarity = 0.95 but treated as separate nodes. | Enforce naming conventions: `<domain>-<concept>-<version>`. Use deduplication: if new memory similarity >0.9 to existing, merge instead of create. |
| **Over-reliance on Semantic Search** | Trusting vector similarity without validating relevance → false positives in complex domains. | Query "user authentication" returns "user authorization" (similarity 0.82) but they're different concepts. Agent uses wrong pattern. | Combine semantic + keyword filters: `WHERE similarity >0.75 AND tags CONTAINS 'authentication'`. Manual validation for critical queries (security, compliance). |
| **Graph Query Performance Degradation** | Large graphs (>10k nodes) make traversal queries slow → AI agents timeout waiting for results. | `MATCH (m)-[:RELATED*3]->(n)` on 50k-node graph takes 30+ seconds. Agent aborts task. | Index frequently queried properties. Limit traversal depth: `[:RELATED*1..2]` max. Use materialized views for common query patterns. Cache hot queries (TTL: 5 min). |

## Implementation Roadmap

**Phase 1: Foundation** (2-4 weeks)
1. Choose vector DB (Pinecone for managed, Qdrant for self-hosted, Weaviate for hybrid)
2. Design memory schema following CE Framework v2.0 patterns
3. Implement `serena_write_memory` → vector DB connector
4. Embed memories using model: `text-embedding-3-large` (OpenAI) or `bge-large-en-v1.5` (open-source)

**Phase 2: Graph Integration** (3-5 weeks)
1. Add graph database (Neo4j, Amazon Neptune, or extend vector DB with graph layer)
2. Implement edge types: `EVOLVED_FROM`, `IMPLEMENTS`, `CAUSED_BY`, `RELATED_TO`
3. Build graph traversal queries for pattern composition
4. Create mind map renderer (Mermaid, D3.js, or Graphviz)

**Phase 3: Agent Integration** (4-6 weeks)
1. Multi-agent memory coordination layer
2. Semantic drift detection service (runs on `ce update-context`)
3. Pattern mining service (weekly batch job)
4. Context injection optimizer (dynamic top-K retrieval)

**Phase 4: Cross-Project Federation** (6-8 weeks)
1. Multi-project vector DB with namespace isolation
2. Cross-project pattern transfer with approval workflow
3. Global pattern catalog (curated subset of high-quality patterns)
4. Pattern versioning and deprecation tracking

## Reference Implementations

- **ce-framework-meta**: [https://github.com/bprzybysz/ce-framework-meta](https://github.com/bprzybysz/ce-framework-meta) - Authoritative schema for graph-based pattern systems, defines 6 agentic patterns, axiom hardening
- **perplexity-space-context**: [https://github.com/bprzybysz/perplexity-space-context](https://github.com/bprzybysz/perplexity-space-context) - Orchestration layer for cyclic pattern refinement and Perplexity Space integration

## Tools and Libraries

**Vector Databases**:
- [Pinecone](https://www.pinecone.io/) - Managed, serverless, easy integration
- [Weaviate](https://weaviate.io/) - Open-source, GraphQL API, hybrid search
- [Qdrant](https://qdrant.tech/) - Rust-based, fast, self-hosted or cloud

**Graph Databases**:
- [Neo4j](https://neo4j.com/) - Industry standard, Cypher query language
- [Amazon Neptune](https://aws.amazon.com/neptune/) - Fully managed, supports Gremlin/SPARQL
- [Memgraph](https://memgraph.com/) - High-performance, compatible with Neo4j

**Embedding Models**:
- [OpenAI text-embedding-3-large](https://platform.openai.com/docs/guides/embeddings) - 3072 dimensions, SOTA performance
- [bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5) - Open-source, 1024 dimensions
- [Voyage AI](https://www.voyageai.com/) - Domain-specific embeddings (code, docs)

**Mind Map Rendering**:
- [Mermaid](https://mermaid.js.org/) - Markdown-based, integrates with GitHub/VS Code
- [D3.js Force Graph](https://d3js.org/) - Customizable, interactive
- [Graphviz](https://graphviz.org/) - Classic layout algorithms (dot, neato, fdp)