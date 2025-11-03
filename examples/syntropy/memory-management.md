# Serena Memory Management

Examples for using Serena MCP memory tools to store, retrieve, and manage persistent knowledge across sessions.

## Purpose

Serena memory provides persistent knowledge storage for:

- **Architecture decisions**: Document why certain patterns were chosen
- **Implementation notes**: Record insights discovered during development
- **Context preservation**: Store frequently-referenced information
- **Pattern library**: Build reusable solution patterns
- **Troubleshooting guides**: Capture resolution steps for recurring issues

**When to Use**:

- Document architectural decisions for future reference
- Store frequently-fetched documentation for quick access
- Record insights discovered during complex reasoning
- Build a knowledge base of project-specific patterns
- Cache expensive operations (symbol searches, doc fetches)

**When NOT to Use**:

- Temporary session state → Use local variables
- Version-controlled knowledge → Use markdown files in repo
- Large datasets → Use dedicated storage (files, databases)
- Shared team knowledge → Use wiki or documentation system

## Prerequisites

- Serena MCP server active (`/syntropy-health` to verify)
- Project activated: `mcp__syntropy__serena__activate_project(project="/full/path")`
- Memory storage location: `.serena/memories/` (created automatically)

## Examples

### Example 1: Write Memory

**Use Case**: Store an architectural decision for future reference.

```python
# Write architecture decision
mcp__syntropy__serena__write_memory(
    memory_type="architecture",
    content="""# Decision: Use Separate Validation Functions

**Context**: Deciding between monolithic validate() vs separate validate_level_N() functions

**Decision**: Use separate functions (validate_level_1, validate_level_2, etc.)

**Rationale**:
- Easier to test individually
- Clear L1→L2→L3→L4 dependency flow
- Better modularity for future extensions

**Date**: 2025-11-03
"""
)
```

**Output**:

```json
{
  "success": true,
  "memory_id": "arch_001",
  "memory_type": "architecture",
  "stored_at": "2025-11-03T12:00:00Z"
}
```

### Example 2: Read Memory

**Use Case**: Retrieve stored architectural decisions.

```python
# Read all architecture memories
memories = mcp__syntropy__serena__read_memory(
    memory_type="architecture"
)
```

**Output**:

```json
{
  "memory_type": "architecture",
  "memories": [
    {
      "id": "arch_001",
      "content": "# Decision: Use Separate Validation Functions...",
      "created_at": "2025-11-03T12:00:00Z",
      "updated_at": "2025-11-03T12:00:00Z"
    }
  ],
  "total": 1
}
```

### Example 3: List All Memories

**Use Case**: Browse all stored memories to understand what knowledge exists.

```python
# List all memories across all types
all_memories = mcp__syntropy__serena__list_memories()
```

**Output**:

```json
{
  "memories": [
    {
      "id": "arch_001",
      "type": "architecture",
      "summary": "Decision: Use Separate Validation Functions",
      "created_at": "2025-11-03T12:00:00Z",
      "size_bytes": 342
    },
    {
      "id": "pattern_001",
      "type": "pattern",
      "summary": "Error Recovery Strategy",
      "created_at": "2025-11-02T10:30:00Z",
      "size_bytes": 521
    },
    {
      "id": "note_001",
      "type": "note",
      "summary": "Git worktree workflow tips",
      "created_at": "2025-11-01T15:45:00Z",
      "size_bytes": 189
    }
  ],
  "total": 3,
  "total_bytes": 1052
}
```

### Example 4: Store Pattern Library

**Use Case**: Build a library of reusable solution patterns.

```python
# Store error recovery pattern
mcp__syntropy__serena__write_memory(
    memory_type="pattern",
    content="""# Pattern: Error Recovery with Retry

**Problem**: Transient errors in external API calls

**Solution**: Exponential backoff with circuit breaker

**Implementation**:
```python
def call_with_retry(func, max_attempts=3, backoff_base=2):
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = backoff_base ** attempt
            time.sleep(wait_time)
```

**Trade-offs**:
- Pros: Handles transient errors gracefully
- Cons: Adds latency, may mask persistent issues

**When to Use**: External API calls, network operations, database queries
"""
)
```

### Example 5: Cache Documentation

**Use Case**: Store frequently-accessed library documentation to avoid repeated fetches.

```python
# Fetch Next.js routing docs once
docs = mcp__syntropy__context7__get_library_docs(
    context7CompatibleLibraryID="/vercel/next.js",
    topic="routing"
)

# Store in memory for quick access
mcp__syntropy__serena__write_memory(
    memory_type="documentation",
    content=f"""# Next.js Routing Documentation

**Fetched**: 2025-11-03T12:00:00Z
**Source**: Context7 - /vercel/next.js
**Topic**: routing

{docs}
"""
)

# Later: Read from memory instead of re-fetching
cached_docs = mcp__syntropy__serena__read_memory(
    memory_type="documentation"
)
# Instant access, no API call, no token cost
```

### Example 6: Record Complex Reasoning

**Use Case**: Store insights from sequential thinking sessions for future reference.

```python
# After completing complex reasoning with thinking tool
mcp__syntropy__serena__write_memory(
    memory_type="note",
    content="""# Analysis: Batch PRP Staging Algorithm

**Date**: 2025-11-03

**Problem**: How to assign PRPs to stages for parallel execution

**Reasoning**:
1. Build dependency graph from PRP "depends_on" fields
2. Identify independent PRPs (no deps) → Stage 1
3. For each PRP with deps, assign to stage = max(dep_stages) + 1
4. Group PRPs in same stage for parallel execution

**Key Insight**: File conflicts act as implicit dependencies. If PRP-A and PRP-B both modify `file.py`, they cannot run in parallel even if no explicit dependency exists.

**Implementation**: tools/ce/batch.py:assign_stages()

**Result**: 3-stage batches with 60% time reduction vs sequential execution
"""
)
```

### Example 7: Delete Memory

**Use Case**: Remove outdated or incorrect memories.

```python
# Delete specific memory by ID
result = mcp__syntropy__serena__delete_memory(
    memory_id="note_001"
)
```

**Output**:

```json
{
  "success": true,
  "memory_id": "note_001",
  "deleted_at": "2025-11-03T14:30:00Z"
}
```

## Common Patterns

### Pattern 1: Decision Log

Maintain a log of architectural decisions:

```python
# Document decision
mcp__syntropy__serena__write_memory(
    memory_type="architecture",
    content=f"""# Decision: {decision_title}

**Date**: {date}
**Context**: {problem_statement}
**Options Considered**: {alternatives}
**Decision**: {chosen_option}
**Rationale**: {reasoning}
**Trade-offs**: {pros_and_cons}
**Implementation**: {code_references}
"""
)

# Later: Review decisions
decisions = mcp__syntropy__serena__read_memory(memory_type="architecture")
for decision in decisions['memories']:
    print(f"- {decision['summary']} ({decision['created_at']})")
```

### Pattern 2: Knowledge Caching

Cache expensive operations for quick retrieval:

```python
# Check if cached
cached = mcp__syntropy__serena__read_memory(memory_type="documentation")
if cached and cached['memories']:
    # Use cached version
    docs = cached['memories'][0]['content']
else:
    # Fetch fresh and cache
    docs = mcp__syntropy__context7__get_library_docs(...)
    mcp__syntropy__serena__write_memory(
        memory_type="documentation",
        content=docs
    )
```

### Pattern 3: Incremental Knowledge Building

Build knowledge base incrementally during development:

```python
# During PRP execution, record insights
def record_insight(insight_text):
    mcp__syntropy__serena__write_memory(
        memory_type="note",
        content=f"""# Insight: {timestamp}

{insight_text}

**Source PRP**: {current_prp_id}
**Context**: {current_task}
"""
    )

# Example usage
record_insight("Discovered that validation L3 requires L2 to pass first")
record_insight("Git worktree cleanup should prune after removal")
```

### Pattern 4: Pattern Library Accumulation

Build reusable patterns over time:

```python
# When implementing a solution, document the pattern
def document_pattern(pattern_name, problem, solution, code_example):
    mcp__syntropy__serena__write_memory(
        memory_type="pattern",
        content=f"""# Pattern: {pattern_name}

**Problem**: {problem}

**Solution**: {solution}

**Implementation**:
```python
{code_example}
```

**Examples**: [list of PRPs where used]
**Related Patterns**: [links]
"""
    )

# Later: Search patterns for solutions
patterns = mcp__syntropy__serena__read_memory(memory_type="pattern")
# Browse patterns for reusable solutions
```

### Pattern 5: Session Handoff

Preserve context for next session:

```python
# At end of session, record state
mcp__syntropy__serena__write_memory(
    memory_type="note",
    content=f"""# Session End: {date}

**Completed**:
- PRP-32 Phase 1: 4/6 Syntropy examples done
- Created: README, serena-symbol-search, context7-docs-fetch, thinking-sequential

**In Progress**:
- linear-integration.md (Step 5)

**Next Steps**:
1. Complete memory-management.md (Step 6)
2. Start Phase 2: Workflow examples (5 files)
3. Create INDEX.md in Phase 4

**Blockers**: None
**Notes**: Follow content template (150-300 lines, required sections)
"""
)

# Next session: Read handoff note
handoff = mcp__syntropy__serena__read_memory(memory_type="note")
# Continue from where left off
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Storing Large Datasets

**Bad**:

```python
# DON'T store large datasets in memory
mcp__syntropy__serena__write_memory(
    memory_type="data",
    content=f"Complete codebase: {entire_codebase_text}"  # 100k+ lines
)
```

**Good**:

```python
# DO store summaries or references
mcp__syntropy__serena__write_memory(
    memory_type="note",
    content="""# Codebase Structure

**Core modules**: tools/ce/ (5 files, 2000 LOC)
**Tests**: tools/tests/ (8 files, 1500 LOC)
**Key files**:
- tools/ce/validate.py:142 - validate_level_4()
- tools/ce/batch.py:85 - assign_stages()
"""
)
```

**Why**: Memory is for knowledge, not data storage. Use files for large data.

### ❌ Anti-Pattern 2: Not Using Memory Types

**Bad**:

```python
# DON'T use generic memory_type
mcp__syntropy__serena__write_memory(
    memory_type="memory",  # Too generic
    content="Some note about validation"
)
```

**Good**:

```python
# DO use specific memory_type for categorization
mcp__syntropy__serena__write_memory(
    memory_type="architecture",  # Specific category
    content="# Decision: Validation Strategy..."
)
```

**Why**: Specific types enable filtering (`read_memory(memory_type="architecture")`).

### ❌ Anti-Pattern 3: Duplicate Storage

**Bad**:

```python
# DON'T store information already in version control
mcp__syntropy__serena__write_memory(
    memory_type="note",
    content=f"PRP-32 content: {read_prp_file('PRP-32.md')}"  # Redundant
)
```

**Good**:

```python
# DO store insights NOT in version control
mcp__syntropy__serena__write_memory(
    memory_type="note",
    content="""# PRP-32 Execution Insights

**Unexpected Issues**:
- Example files needed 150-300 lines (not 100-200 as estimated)
- INDEX.md metadata extraction more complex than planned

**Time Adjustments**: +25% over estimate
"""
)
```

**Why**: Memory is for ephemeral knowledge and insights, not duplicating git.

### ❌ Anti-Pattern 4: No Metadata in Content

**Bad**:

```python
# DON'T omit context metadata
mcp__syntropy__serena__write_memory(
    memory_type="pattern",
    content="Use exponential backoff for retries"  # No context
)
```

**Good**:

```python
# DO include metadata (date, source, context)
mcp__syntropy__serena__write_memory(
    memory_type="pattern",
    content="""# Pattern: Exponential Backoff

**Documented**: 2025-11-03
**Source**: PRP-32 error recovery implementation
**Context**: Handling transient MCP connection failures

**Solution**: [detailed pattern]
"""
)
```

**Why**: Metadata enables searching, filtering, and understanding origin.

## Memory Types

**Recommended Types**:

- `architecture`: Architectural decisions and design rationale
- `pattern`: Reusable solution patterns
- `note`: General observations and insights
- `documentation`: Cached external documentation
- `troubleshooting`: Issue resolution steps
- `configuration`: Setup and config notes

**Custom Types**: You can create any memory_type string. Use lowercase, no spaces.

## Related Examples

- [serena-symbol-search.md](serena-symbol-search.md) - Finding symbols to document
- [context7-docs-fetch.md](context7-docs-fetch.md) - Documentation to cache
- [thinking-sequential.md](thinking-sequential.md) - Complex reasoning to record
- [../workflows/context-drift-remediation.md](../workflows/context-drift-remediation.md) - Using memories in drift analysis

## Troubleshooting

### Issue: "Memory not persisting across sessions"

**Cause**: Project not activated in Serena

**Solution**:

```python
# Activate project first
mcp__syntropy__serena__activate_project(
    project="/Users/bprzybysz/nc-src/ctx-eng-plus"
)

# Then write memory
mcp__syntropy__serena__write_memory(...)
```

### Issue: "Cannot find memory by ID"

**Symptom**: `delete_memory()` fails with "Memory not found"

**Solution**: List memories first to find correct ID:

```python
# List all memories
all_memories = mcp__syntropy__serena__list_memories()

# Find memory by summary
target = [m for m in all_memories['memories'] if "pattern" in m['summary'].lower()]
print(target[0]['id'])  # Use this ID

# Delete with correct ID
mcp__syntropy__serena__delete_memory(memory_id=target[0]['id'])
```

### Issue: Memory content too large

**Symptom**: Write fails with "Content exceeds size limit"

**Solution**: Store summary instead of full content:

```python
# Instead of storing full docs (10k+ tokens)
docs = mcp__syntropy__context7__get_library_docs(...)

# Store summary + reference
mcp__syntropy__serena__write_memory(
    memory_type="documentation",
    content=f"""# Next.js Routing Docs (Summary)

**Key Concepts**: App Router, file-based routing, route groups, dynamic routes

**Full docs**: Use context7_get_library_docs("/vercel/next.js", topic="routing")

**Important Points**:
- App Router introduced in v13
- File-based routing: page.tsx → route
- Dynamic routes: [id] → params.id
"""
)
```

## Performance Tips

1. **Cache expensive operations**: Store Context7 docs, symbol searches in memory
2. **Use specific memory types**: Enable fast filtering (`read_memory(memory_type="...")`)
3. **Store summaries, not full content**: 500-1000 words max per memory
4. **Delete obsolete memories**: Regularly prune outdated knowledge
5. **Include search metadata**: Add keywords, tags in content for easy discovery

## Storage Location

Memories stored in: `.serena/memories/`

**Structure**:

```
.serena/
└── memories/
    ├── architecture_001.json
    ├── pattern_001.json
    ├── note_001.json
    └── documentation_001.json
```

**Backup**: Memories are plain JSON files, can be backed up with version control or separately.

**Sharing**: Copy `.serena/memories/` to another project to share knowledge base.

## Resources

- Serena MCP Documentation: `.serena/README.md`
- Memory Storage: `.serena/memories/` directory
- Tool Usage Guide: `examples/TOOL-USAGE-GUIDE.md`
- Syntropy Health: `/syntropy-health` slash command
