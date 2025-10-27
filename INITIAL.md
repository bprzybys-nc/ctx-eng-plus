# Feature: <Feature Name>

## FEATURE
<Detailed feature description with user story and acceptance criteria>

**Example:**
- User Story: As a developer, I want to analyze PRPs with sequential thinking...
- Acceptance Criteria:
  1. PRP analysis completes in <5 seconds
  2. Reasoning chain visible in logs
  3. Gracefully degrades when MCP unavailable

## PLANNING CONTEXT
**Complexity Assessment**: <simple|medium|complex>
- Simple: Single file, <50 LOC, clear path
- Medium: 2-3 files, 50-200 LOC, standard patterns
- Complex: Multiple files, >200 LOC, new architecture

**Architectural Impact**: <isolated|moderate|cross-cutting>
- Isolated: Changes confined to single module
- Moderate: Touches 2-3 modules
- Cross-cutting: Affects core architecture or multiple layers

**Risk Factors**:
- List potential risks (e.g., breaking changes, performance, security)

**Success Metrics**:
- How to measure if implementation is successful

## EXAMPLES
<Similar code patterns from codebase>

**Inline Code Examples:**
```python
# Provide actual code examples inline
def example_function():
    pass
```

**File References:**
See src/example.py:42-67 for similar pattern

**Descriptions:**
- Uses async/await pattern
- Follows repository pattern for data access

## DOCUMENTATION
- [Library Name](https://docs.url) - Specific topic needed
- "pytest" - Testing framework
- "FastAPI" - Web framework

## OTHER CONSIDERATIONS
**Security:**
- List security concerns

**Performance:**
- Expected performance characteristics

**Edge Cases:**
- Unusual scenarios to handle

**Backwards Compatibility:**
- Migration strategy if breaking changes
