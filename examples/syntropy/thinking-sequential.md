# Sequential Thinking for Complex Reasoning

Examples for using the Thinking MCP tool to break down complex problems into structured, sequential thought processes.

## Purpose

The `sequentialthinking` tool enables explicit, multi-step reasoning with branching, revision, and structured thought tracking. This is valuable for complex analysis, decision-making, and problems that benefit from visible reasoning steps.

**When to Use**:

- Complex problems requiring multi-step analysis
- Trade-off evaluation (comparing approaches A vs B vs C)
- Debugging complex issues with many potential causes
- Architectural decisions requiring structured reasoning
- Problems where showing your work is valuable

**When NOT to Use**:

- Simple, straightforward problems → Use inline reasoning
- Time-sensitive tasks → Sequential thinking adds overhead
- Problems you've solved many times → Use cached patterns

## Prerequisites

- Thinking MCP server active (`/syntropy-health` to verify)
- Understanding of thought structure (thought number, total, branching)

## Examples

### Example 1: Basic Sequential Thinking

**Use Case**: Analyze trade-offs between two implementation approaches.

```python
# Thought 1: State the problem
mcp__syntropy__thinking__sequentialthinking(
    thought="Need to decide between monolithic validation function vs separate L1-L4 functions. Let me analyze trade-offs.",
    thoughtNumber=1,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Thought 2: Analyze approach A
mcp__syntropy__thinking__sequentialthinking(
    thought="Approach A (monolithic): Single validate() function with level parameter. Pros: simpler API, easier to call. Cons: harder to test, less modular.",
    thoughtNumber=2,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Thought 3: Analyze approach B
mcp__syntropy__thinking__sequentialthinking(
    thought="Approach B (separate functions): validate_level_1(), validate_level_2(), etc. Pros: easier to test individually, more modular, clearer dependencies. Cons: more functions to maintain.",
    thoughtNumber=3,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Thought 4: Compare and decide
mcp__syntropy__thinking__sequentialthinking(
    thought="Comparing: modularity and testability are critical for validation gates. Approach B wins despite API complexity. Individual functions allow independent testing and clear L1→L2→L3→L4 flow.",
    thoughtNumber=4,
    totalThoughts=5,
    nextThoughtNeeded=True
)

# Thought 5: Final decision
mcp__syntropy__thinking__sequentialthinking(
    thought="Decision: Use separate validate_level_N() functions (Approach B). Implement validate_all() wrapper for convenience. This gives both modularity and simple API.",
    thoughtNumber=5,
    totalThoughts=5,
    nextThoughtNeeded=False
)
```

**Output**: Structured reasoning chain with clear decision rationale.

### Example 2: Branching Thoughts

**Use Case**: Explore alternative approaches in parallel.

```python
# Main thought chain
mcp__syntropy__thinking__sequentialthinking(
    thought="Need to implement error recovery. Two main approaches to consider.",
    thoughtNumber=1,
    totalThoughts=3,
    nextThoughtNeeded=True
)

# Branch 1: Retry approach
mcp__syntropy__thinking__sequentialthinking(
    thought="Branch 1: Retry with exponential backoff. Simple, works for transient errors. But: may waste time on persistent errors.",
    thoughtNumber=2,
    totalThoughts=3,
    nextThoughtNeeded=True,
    branchId="retry-approach",
    branchFromThought=1
)

# Branch 2: Circuit breaker approach
mcp__syntropy__thinking__sequentialthinking(
    thought="Branch 2: Circuit breaker pattern. Fails fast after threshold. But: more complex to implement, requires state tracking.",
    thoughtNumber=2,
    totalThoughts=3,
    nextThoughtNeeded=True,
    branchId="circuit-breaker",
    branchFromThought=1
)

# Converge branches
mcp__syntropy__thinking__sequentialthinking(
    thought="Synthesis: Use both. Retry (3 attempts) for immediate recovery, circuit breaker for persistent failures. Best of both worlds.",
    thoughtNumber=3,
    totalThoughts=3,
    nextThoughtNeeded=False
)
```

**Output**: Parallel exploration of alternatives, then convergence to hybrid solution.

### Example 3: Revising Thoughts

**Use Case**: Update reasoning based on new information.

```python
# Initial thought
mcp__syntropy__thinking__sequentialthinking(
    thought="Plan: Store validation results in JSON file for persistence.",
    thoughtNumber=1,
    totalThoughts=3,
    nextThoughtNeeded=True
)

# Discover new information
# ... (check codebase, find existing memory system)

# Revise earlier thought
mcp__syntropy__thinking__sequentialthinking(
    thought="REVISION: Just discovered Serena memory system exists. Don't need JSON file. Use serena_write_memory() instead. More integrated with existing infrastructure.",
    thoughtNumber=2,
    totalThoughts=3,
    nextThoughtNeeded=True,
    isRevision=True,
    revisesThought=1
)

# Continue with updated plan
mcp__syntropy__thinking__sequentialthinking(
    thought="Updated plan: Use Serena memory with memory_type='validation_results'. Leverage existing infrastructure.",
    thoughtNumber=3,
    totalThoughts=3,
    nextThoughtNeeded=False
)
```

**Output**: Revised reasoning chain reflecting new information.

### Example 4: Extending Total Thoughts

**Use Case**: Problem requires more steps than initially estimated.

```python
# Start with estimate
mcp__syntropy__thinking__sequentialthinking(
    thought="Analyzing performance bottleneck. Initial estimate: 3 thoughts needed.",
    thoughtNumber=1,
    totalThoughts=3,
    nextThoughtNeeded=True
)

# Thought 2
mcp__syntropy__thinking__sequentialthinking(
    thought="Profiled code: 60% time in file I/O, 30% in parsing, 10% in validation.",
    thoughtNumber=2,
    totalThoughts=3,
    nextThoughtNeeded=True
)

# Realize need more thoughts
mcp__syntropy__thinking__sequentialthinking(
    thought="Need to analyze each bottleneck separately. Extending analysis.",
    thoughtNumber=3,
    totalThoughts=3,
    nextThoughtNeeded=True,
    needsMoreThoughts=True  # Signal extension
)

# Continue with extended thoughts
mcp__syntropy__thinking__sequentialthinking(
    thought="File I/O optimization: Use read caching, reduce syscalls.",
    thoughtNumber=4,
    totalThoughts=6,  # Updated total
    nextThoughtNeeded=True
)

# ... thoughts 5-6
```

**Output**: Extended reasoning chain beyond initial estimate.

## Common Patterns

### Pattern 1: Problem Decomposition

```python
# 1. State problem
# 2. Break into sub-problems
# 3. Analyze each sub-problem
# 4. Synthesize solution
# 5. Validate completeness
```

### Pattern 2: Trade-off Analysis

```python
# 1. State decision to make
# 2. List options (A, B, C)
# 3. For each option: pros/cons
# 4. Compare options against criteria
# 5. Make recommendation with rationale
```

### Pattern 3: Root Cause Analysis

```python
# 1. State observed problem
# 2. List potential causes
# 3. For each cause: evaluate likelihood
# 4. Propose tests to confirm
# 5. Recommend fix based on confirmed cause
```

### Pattern 4: Architectural Design

```python
# 1. State requirements
# 2. Identify constraints
# 3. Propose architecture options
# 4. Evaluate each against requirements/constraints
# 5. Select architecture with justification
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Over-Using for Simple Problems

**Bad**:

```python
# DON'T use sequential thinking for trivial decisions
mcp__syntropy__thinking__sequentialthinking(
    thought="Should I use 'total' or 'count' as variable name?",
    thoughtNumber=1,
    totalThoughts=5,  # 5 thoughts for trivial naming decision
    nextThoughtNeeded=True
)
```

**Good**:

```python
# DO use inline reasoning for simple decisions
# Just pick 'total' (more descriptive) and move on
```

**Why**: Sequential thinking adds overhead. Use for complex problems only.

### ❌ Anti-Pattern 2: Not Using Branching for Alternatives

**Bad**:

```python
# DON'T analyze alternatives sequentially
thought1="Approach A: pros..."
thought2="Approach A: cons..."
thought3="Approach B: pros..."
thought4="Approach B: cons..."
# Sequential, not parallel comparison
```

**Good**:

```python
# DO use branching for parallel exploration
branchId="approach-a" (thoughts 2-3)
branchId="approach-b" (thoughts 2-3)
thought4="Compare both branches..."
```

**Why**: Branching makes alternative exploration explicit and parallel.

### ❌ Anti-Pattern 3: Ignoring needsMoreThoughts

**Bad**:

```python
# DON'T force fit into initial totalThoughts
totalThoughts=3  # Initial estimate
# ... realize need 6 thoughts
# ... try to cram into 3 thoughts (rushed analysis)
```

**Good**:

```python
# DO use needsMoreThoughts to extend
totalThoughts=3  # Initial
needsMoreThoughts=True  # Signal extension
totalThoughts=6  # Updated
```

**Why**: Better to extend analysis than rush to fit arbitrary limit.

## Related Examples

- [serena-symbol-search.md](serena-symbol-search.md) - Using symbol search in analysis
- [context7-docs-fetch.md](context7-docs-fetch.md) - Fetching docs for informed decisions
- [../workflows/context-drift-remediation.md](../workflows/context-drift-remediation.md) - Using thinking in drift analysis

## When to Use vs Inline Reasoning

| Use Sequential Thinking | Use Inline Reasoning |
|------------------------|---------------------|
| Complex decisions (5+ factors) | Simple decisions (2-3 factors) |
| Trade-off analysis | Obvious best choice |
| Root cause debugging | Known issue |
| Architectural design | Following established pattern |
| Need to show work | Result is what matters |

## Performance Tips

1. **Estimate totalThoughts realistically**: Start with 5-7 for most problems
2. **Use branching for alternatives**: Don't compare sequentially
3. **Revise when new info emerges**: Better to revise than ignore new facts
4. **Signal extension if needed**: Use needsMoreThoughts
5. **Stop when decision is clear**: Don't overthink

## Resources

- Thinking MCP Documentation: MCP protocol spec
- Syntropy Health: `/syntropy-health` slash command
