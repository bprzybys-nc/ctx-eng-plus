# Context7 Library Documentation Fetching

Examples for using Context7 MCP tools to fetch official library documentation with semantic focus and token optimization.

## Purpose

Context7 provides access to official documentation for popular libraries (React, Next.js, MongoDB, etc.) with the ability to focus on specific topics. This is superior to general web search because it returns curated, version-specific documentation optimized for AI consumption.

**When to Use**:

- Need official library documentation for current project
- Want documentation focused on specific topic (e.g., "routing" in Next.js)
- Prefer curated docs over web search results
- Need token-optimized documentation (vs full docs website)

**When NOT to Use**:

- Library not in Context7's catalog → Use `WebSearch` or `WebFetch`
- Already have documentation link → Use `WebFetch` directly
- Need bleeding-edge docs (Context7 may lag by days/weeks)

## Prerequisites

- Context7 MCP server active (`/syntropy-health` to verify)
- Know library name or have Context7-compatible library ID

## Examples

### Example 1: Resolve Library ID

**Use Case**: You know the library name ("Next.js") but need the Context7-compatible ID.

```python
# Find Context7 ID for Next.js
library_id = mcp__syntropy__context7__resolve_library_id(
    libraryName="next.js"
)
```

**Output**:

```json
{
  "library_name": "next.js",
  "context7_id": "/vercel/next.js",
  "aliases": ["nextjs", "next"],
  "versions_available": ["14.x", "13.x", "12.x"]
}
```

**Common Library IDs**:

| Library | Context7 ID |
|---------|-------------|
| Next.js | `/vercel/next.js` |
| React | `/facebook/react` |
| MongoDB | `/mongodb/docs` |
| FastAPI | `/tiangolo/fastapi` |
| NumPy | `/numpy/numpy` |
| Pandas | `/pandas-dev/pandas` |

### Example 2: Fetch Library Docs (General)

**Use Case**: Get general documentation for a library.

```python
# Fetch MongoDB documentation
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/mongodb/docs"
)
```

**Output**:

```text
# MongoDB Documentation

MongoDB is a document database...

## Core Concepts
- Collections
- Documents
- CRUD Operations
...

## Connection Strings
mongodb://localhost:27017

## Basic Operations
insertOne(), find(), updateMany()...

[Optimized for AI, ~5000 tokens]
```

### Example 3: Fetch Focused Documentation

**Use Case**: You're implementing routing in Next.js and only need routing docs, not entire framework docs.

```python
# Get Next.js routing docs only
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="routing"
)
```

**Output**:

```text
# Next.js Routing

## App Router (v14+)
- File-based routing
- Route groups
- Dynamic routes
...

## Pages Router (Legacy)
...

[Focused on routing only, ~2000 tokens instead of 10000+]
```

**Topic Focus Benefits**:

- **80% token reduction**: From 10k tokens (full docs) to 2k tokens (topic-focused)
- **Faster reading**: AI reads only relevant sections
- **Better context fit**: More room for your code in context window

### Example 4: Multiple Topics

**Use Case**: Need documentation for authentication AND authorization.

```python
# Option 1: Combine in one topic string
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="authentication and authorization"
)

# Option 2: Fetch separately and combine
auth_docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="authentication"
)

authz_docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="authorization"
)
```

**Recommendation**: Option 1 is usually better (single call, Context7 handles the combination).

### Example 5: Token-Limited Fetching

**Use Case**: Need docs but have limited context budget.

```python
# Limit to 2000 tokens (default is 5000)
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/mongodb/docs",
    topic="aggregation",
    tokens=2000  # Limit token count
)
```

**Output**: Truncated docs optimized for 2000 tokens, focusing on most important content first.

### Example 6: Library Resolution + Docs Fetching

**Use Case**: Complete workflow from library name to documentation.

```python
# Step 1: Resolve library ID
library_id = mcp__syntropy__context7__resolve_library_id(
    libraryName="fastapi"
)

# Step 2: Fetch docs with topic focus
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID=library_id["context7_id"],  # "/tiangolo/fastapi"
    topic="dependency injection"
)

# Step 3: Use docs in implementation
# ... (implement code using fetched docs)
```

## Common Patterns

### Pattern 1: Pre-Implementation Documentation Fetch

Before implementing a feature, fetch relevant docs:

```python
# 1. Identify library and topic
library = "next.js"
topic = "api routes"

# 2. Resolve and fetch
lib_id = mcp__syntropy__context7__resolve_library_id(libraryName=library)
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID=lib_id["context7_id"],
    topic=topic
)

# 3. Store in memory for reference
mcp__syntropy__serena__write_memory(
    memory_type="documentation",
    content=f"Next.js API Routes Documentation:\n{docs}"
)

# 4. Implement feature using docs as reference
```

### Pattern 2: Multi-Library Documentation

When integrating multiple libraries:

```python
# Fetch docs for each library
libraries = [
    ("/vercel/next.js", "api routes"),
    ("/mongodb/docs", "connection"),
    ("/auth0/docs", "authentication")
]

all_docs = {}
for lib_id, topic in libraries:
    docs = mcp__syntropy__context7__get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic=topic,
        tokens=2000  # Limit each to 2k tokens (total 6k)
    )
    all_docs[lib_id] = docs

# Now have comprehensive docs for integration (6k tokens total)
```

### Pattern 3: Documentation + Code Examples

Combine Context7 docs with codebase examples:

```python
# 1. Fetch library docs
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="server actions"
)

# 2. Find existing usage in codebase
examples = mcp__syntropy__serena__search_for_pattern(
    pattern="'use server'",
    file_glob="app/**/*.ts"
)

# 3. Combine: official docs + your project patterns
# Now have both theory (docs) and practice (existing code)
```

### Pattern 4: Token Budget Management

Managing token usage across multiple doc fetches:

```python
# Total budget: 5000 tokens
# Split across 3 libraries: ~1600 tokens each

libraries = [
    ("/vercel/next.js", "routing", 1600),
    ("/mongodb/docs", "queries", 1600),
    ("/stripe/docs", "webhooks", 1600)
]

for lib_id, topic, token_limit in libraries:
    docs = mcp__syntropy__context7__get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic=topic,
        tokens=token_limit
    )
    # Use docs...
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Fetching Full Docs Without Topic

**Bad**:

```python
# DON'T fetch full documentation
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js"
    # No topic specified = returns ALL docs (10k+ tokens)
)
```

**Good**:

```python
# DO specify topic for focused docs
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="routing"  # Only routing docs (~2k tokens)
)
```

**Why**: Full docs consume massive context budget and include irrelevant information.

### ❌ Anti-Pattern 2: Using Context7 for Libraries Not in Catalog

**Bad**:

```python
# DON'T use Context7 for obscure libraries
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/unknown/mylib"  # Will fail
)
```

**Good**:

```python
# DO use WebFetch for libraries not in Context7
docs = WebFetch(
    url="https://mylib.readthedocs.io",
    prompt="Extract API documentation for authentication"
)
```

**Why**: Context7 only supports popular libraries. Use web tools for others.

### ❌ Anti-Pattern 3: Fetching Same Docs Multiple Times

**Bad**:

```python
# DON'T fetch docs repeatedly
for file in files:
    docs = mcp__syntropy__context7__get_library_docs(...)  # Repeated call
    # Use docs...
```

**Good**:

```python
# DO fetch once and reuse
docs = mcp__syntropy__context7__get_library_docs(...)

for file in files:
    # Use cached docs...
```

**Why**: Each call costs tokens and time. Fetch once, use many times.

## Token Optimization Strategies

### Strategy 1: Progressive Detail

Start with minimal tokens, fetch more if needed:

```python
# 1. Start with minimal docs (1000 tokens)
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/mongodb/docs",
    topic="aggregation",
    tokens=1000
)

# 2. If insufficient, fetch more detailed docs
if need_more_detail:
    docs = mcp__syntropy__context7__get_library_docs(
        context7CompatibleLibraryID="/mongodb/docs",
        topic="aggregation pipeline operators",  # More specific
        tokens=3000
    )
```

### Strategy 2: Topic Specificity

More specific topics = fewer tokens:

```python
# Generic (5000 tokens)
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="data fetching"
)

# Specific (2000 tokens)
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="server-side rendering with getServerSideProps"
)
```

### Strategy 3: Memory Storage

Store frequently used docs in Serena memory:

```python
# Fetch once
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="routing"
)

# Store in memory
mcp__syntropy__serena__write_memory(
    memory_type="documentation",
    content=f"Next.js Routing Docs:\n{docs}"
)

# Later: Read from memory (instant, no token cost)
cached_docs = mcp__syntropy__serena__read_memory(
    memory_type="documentation"
)
```

## Related Examples

- [serena-symbol-search.md](serena-symbol-search.md) - Finding code examples in your codebase
- [memory-management.md](memory-management.md) - Storing fetched documentation
- [../workflows/context-drift-remediation.md](../workflows/context-drift-remediation.md) - Using docs in drift analysis
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - When to use Context7 vs WebFetch

## Troubleshooting

### Issue: "Library not found"

**Solution**: Check if library is in Context7 catalog:

```python
# Try to resolve first
result = mcp__syntropy__context7__resolve_library_id(libraryName="mylibrary")
# If fails, library not in catalog → use WebFetch instead
```

### Issue: Documentation outdated

**Symptom**: Fetched docs don't mention recent features

**Solution**: Context7 docs may lag behind latest releases. For bleeding-edge features:

```python
# Use WebFetch for latest docs
docs = WebFetch(
    url="https://nextjs.org/docs",
    prompt="Extract documentation for the latest app router features"
)
```

### Issue: Topic too broad, docs still too large

**Solution**: Make topic more specific:

```python
# Too broad (5k tokens)
topic="data fetching"

# More specific (2k tokens)
topic="client-side data fetching with useEffect"
```

## Performance Tips

1. **Always specify topic**: Reduces tokens by 60-80%
2. **Use token limits**: Set `tokens` parameter to your budget
3. **Cache in memory**: Store frequently used docs
4. **Batch fetches**: Fetch all needed docs upfront, not on-demand
5. **Validate library availability**: Use `resolve_library_id` first to avoid errors

## Resources

- Context7 Documentation: https://context7.com/docs
- Available Libraries: https://context7.com/catalog
- Syntropy Health: `/syntropy-health` slash command
