---
name: Sequential Thinking Integration for PRP Generation
description: Integrate mcp__syntropy__thinking__sequentialthinking into INITIAL.md analysis and generate-prp workflow for deeper reasoning
prp_id: PRP-29.4
status: new
created_date: '2025-10-26T00:15:00.000000'
last_updated: '2025-10-27T00:00:00.000000'
updated_by: prp-requirements-update
dependencies:
- PRP-3 (generate-prp foundation)
- PRP-29.1 (Syntropy MCP infrastructure)
context_sync:
  ce_updated: false
  serena_updated: false
version: 1.1
execution_requirements:
  active_project: ctx-eng-plus
  working_directory: /Users/bprzybysz/nc-src/ctx-eng-plus
  language_context: Python
  reason: Modifies Python generate-prp tool (tools/ce/prp/generate.py) for thinking integration
---

# Sequential Thinking Integration for PRP Generation

## 🎯 Feature Overview

**Context:** Current generate-prp uses heuristic-based topic extraction and pattern matching. Sequential thinking MCP tool (`mcp__syntropy__thinking__sequentialthinking`) enables deeper, step-by-step reasoning for complex analysis.

**Problem:**
- Topic extraction uses simple keyword matching (line 570-618 in generate.py)
- No deep analysis of feature complexity or architectural implications
- Implementation phase breakdown is template-based (not context-aware)
- Missing opportunity for AI-assisted reasoning during planning
- INITIAL.md doesn't guide users on providing planning context

**Solution:**
Integrate sequential thinking at 3 key points:
1. **INITIAL.md analysis**: Deep feature understanding and complexity assessment
2. **Implementation planning**: Context-aware phase breakdown
3. **Validation strategy**: Risk analysis and edge case identification

**Expected Outcome:**
- ✅ Sequential thinking analyzes feature complexity in INITIAL.md
- ✅ Context-aware implementation phase generation
- ✅ Risk-based validation strategy with edge cases
- ✅ INITIAL.md template includes planning context section
- ✅ Graceful degradation when sequential thinking unavailable
- ✅ Clear reasoning chain logged for transparency

---

## 🛠️ Implementation Blueprint

### Phase 1: Update INITIAL.md Template (30 minutes)

**Goal:** Add PLANNING CONTEXT section to guide sequential thinking

**File:** `/Users/bprzybysz/nc-src/ctx-eng-plus/INITIAL.md`

**Current Structure:**
```markdown
# Feature: <Name>

## FEATURE
...

## EXAMPLES
...

## DOCUMENTATION
...

## OTHER CONSIDERATIONS
...
```

**New Structure:**
```markdown
# Feature: <Name>

## FEATURE
<What to build - user story, acceptance criteria>

## PLANNING CONTEXT
**Complexity Assessment**: <simple|medium|complex>
**Architectural Impact**: <isolated|moderate|cross-cutting>
**Risk Factors**: <list key risks>
**Success Metrics**: <how to measure success>

## EXAMPLES
...

## DOCUMENTATION
...

## OTHER CONSIDERATIONS
...
```

**Implementation:**
```bash
# Update INITIAL.md template
cat > /Users/bprzybysz/nc-src/ctx-eng-plus/INITIAL.md << 'EOF'
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
EOF
```

**Update generate-prp.md documentation:**

**File:** `.claude/commands/generate-prp.md`

Add section after INITIAL.md structure:

```markdown
### New: PLANNING CONTEXT Section

Helps sequential thinking analyze feature complexity:

```markdown
## PLANNING CONTEXT
**Complexity Assessment**: medium
- 2-3 files needed
- 100-150 LOC estimated
- Uses existing auth patterns

**Architectural Impact**: moderate
- Touches auth layer and API endpoints
- No database schema changes

**Risk Factors**:
- JWT token expiration handling
- Rate limiting integration
- Password reset flow complexity

**Success Metrics**:
- Auth success rate >99.9%
- Token refresh <100ms
- Zero security vulnerabilities in audit
```

Sequential thinking uses this to:
- Generate realistic time estimates
- Identify hidden complexity
- Propose validation gates based on risks
```

**Validation:**
```bash
# Verify template updated
test -f INITIAL.md && echo "✅ INITIAL.md exists"
grep "PLANNING CONTEXT" INITIAL.md && echo "✅ Planning section added"
```

**Success Criteria:**
- ✅ INITIAL.md has PLANNING CONTEXT section
- ✅ Documentation updated in generate-prp.md
- ✅ Examples show how to use planning context

---

### Phase 2: Sequential Thinking Integration in generate.py (3 hours)

**Goal:** Replace heuristic topic extraction with sequential thinking

**File:** `tools/ce/generate.py`

**Integration Point 1: Feature Analysis (Deep Understanding)**

**Current Code** (line 570-618):
```python
def extract_topics_from_feature(
    feature_text: str,
    serena_research: Dict[str, Any]
) -> List[str]:
    """Extract documentation topics using Sequential Thinking MCP."""
    # Graceful degradation - return heuristic-based topics
    technical_terms = []
    patterns = {
        "authentication": ["auth", "login", "jwt"],
        # ... keyword matching
    }
    # Return heuristic results
    return topics
```

**New Implementation:**
```python
def extract_topics_from_feature(
    feature_text: str,
    serena_research: Dict[str, Any]
) -> List[str]:
    """Extract documentation topics using Sequential Thinking MCP.

    Uses: mcp__syntropy__thinking__sequentialthinking

    Args:
        feature_text: FEATURE section from INITIAL.md
        serena_research: Codebase research results for additional context

    Returns:
        List of topics (e.g., ["routing", "security", "async", "testing"])

    Process:
        1. Call Sequential Thinking MCP with feature analysis prompt
        2. Extract topics from reasoning chain
        3. Deduplicate and filter to 3-5 most relevant topics
        4. Fall back to heuristic if MCP unavailable
    """
    logger.info("Extracting topics from feature text using Sequential Thinking")

    try:
        # Call sequential thinking MCP
        from .mcp_utils import call_syntropy_mcp

        prompt = f"""Analyze this feature description and identify 3-5 key technical topics that would need documentation:

Feature: {feature_text}

Codebase Context:
- Related patterns: {len(serena_research.get('patterns', []))}
- Test framework: {serena_research.get('test_patterns', [{}])[0].get('framework', 'unknown') if serena_research.get('test_patterns') else 'unknown'}

Think step-by-step about:
1. What technical areas does this feature touch? (e.g., authentication, async, database)
2. What documentation would help implement this? (e.g., library guides, API docs)
3. What are the 3-5 most critical topics to focus documentation on?

Return final answer as: TOPICS: topic1, topic2, topic3"""

        result = call_syntropy_mcp(
            "thinking",
            "sequentialthinking",
            {
                "thought": prompt,
                "thoughtNumber": 1,
                "totalThoughts": 5,
                "nextThoughtNeeded": True
            }
        )

        # Extract topics from result
        topics = _extract_topics_from_thinking_result(result)

        if topics:
            logger.info(f"Extracted topics (sequential thinking): {topics}")
            return topics

    except Exception as e:
        logger.warning(f"Sequential thinking unavailable: {e}")
        logger.warning("Falling back to heuristic topic extraction")

    # Graceful degradation - heuristic approach
    return _extract_topics_heuristic(feature_text)


def _extract_topics_from_thinking_result(result: Dict[str, Any]) -> List[str]:
    """Parse topics from sequential thinking result.

    Args:
        result: MCP tool result

    Returns:
        List of topics extracted from thinking chain
    """
    # Extract content from MCP result
    content = ""
    if isinstance(result, dict) and "content" in result:
        if isinstance(result["content"], list):
            for item in result["content"]:
                if isinstance(item, dict) and "text" in item:
                    content += item["text"] + " "
        elif isinstance(result["content"], str):
            content = result["content"]

    # Look for TOPICS: pattern in result
    topics_match = re.search(r"TOPICS:\s*(.+)", content, re.IGNORECASE)
    if topics_match:
        topics_str = topics_match.group(1)
        # Split by comma and clean
        topics = [t.strip() for t in topics_str.split(",")]
        return topics[:5]  # Limit to 5

    return []


def _extract_topics_heuristic(feature_text: str) -> List[str]:
    """Heuristic-based topic extraction (fallback).

    Args:
        feature_text: Feature description text

    Returns:
        List of topics based on keyword matching
    """
    technical_terms = []

    # Common technical patterns to look for
    patterns = {
        "authentication": ["auth", "login", "jwt", "oauth", "token"],
        "database": ["database", "sql", "nosql", "query", "model"],
        "api": ["api", "rest", "graphql", "endpoint", "route"],
        "async": ["async", "await", "concurrent", "parallel"],
        "testing": ["test", "pytest", "unittest", "mock"],
        "security": ["security", "encrypt", "hash", "bcrypt", "secure"],
        "validation": ["validate", "validation", "schema", "verify"],
    }

    feature_lower = feature_text.lower()
    for topic, keywords in patterns.items():
        if any(kw in feature_lower for kw in keywords):
            technical_terms.append(topic)

    # Limit to 3-5 topics
    topics = technical_terms[:5] if technical_terms else ["general"]

    logger.info(f"Extracted topics (heuristic): {topics}")
    return topics
```

**Integration Point 2: Implementation Phase Generation**

**New Function:**
```python
def generate_implementation_phases_with_thinking(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any]
) -> str:
    """Generate implementation phases using sequential thinking.

    Uses: mcp__syntropy__thinking__sequentialthinking

    Args:
        parsed_data: INITIAL.md structured data
        serena_research: Codebase research findings

    Returns:
        Implementation phases markdown

    Process:
        1. Extract planning context from INITIAL.md
        2. Call sequential thinking with implementation planning prompt
        3. Parse phases from reasoning chain
        4. Fall back to template-based if unavailable
    """
    logger.info("Generating implementation phases with sequential thinking")

    try:
        from .mcp_utils import call_syntropy_mcp

        # Extract planning context
        planning_context = _extract_planning_context(parsed_data)

        prompt = f"""Plan implementation phases for this feature:

Feature: {parsed_data['feature_name']}
Description: {parsed_data['feature'][:300]}...

Planning Context:
- Complexity: {planning_context.get('complexity', 'unknown')}
- Architectural Impact: {planning_context.get('architectural_impact', 'unknown')}
- Risk Factors: {', '.join(planning_context.get('risk_factors', ['unknown']))}

Codebase Context:
- Similar patterns: {len(serena_research.get('patterns', []))}
- Test framework: {serena_research.get('test_patterns', [{}])[0].get('framework', 'pytest') if serena_research.get('test_patterns') else 'pytest'}

Think step-by-step:
1. What are the logical implementation phases?
2. What dependencies exist between phases?
3. What time estimates are realistic?
4. What validation should happen at each phase?

Provide phases in format:
PHASE 1: <name> (<time estimate>)
- Step 1
- Step 2

PHASE 2: ...
"""

        result = call_syntropy_mcp(
            "thinking",
            "sequentialthinking",
            {
                "thought": prompt,
                "thoughtNumber": 1,
                "totalThoughts": 8,
                "nextThoughtNeeded": True
            }
        )

        # Extract phases from thinking result
        phases = _extract_phases_from_thinking_result(result)

        if phases:
            logger.info(f"Generated {len(phases)} implementation phases")
            return phases

    except Exception as e:
        logger.warning(f"Sequential thinking unavailable: {e}")
        logger.warning("Falling back to template-based phases")

    # Graceful degradation
    return synthesize_implementation(parsed_data, serena_research)


def _extract_planning_context(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract PLANNING CONTEXT from INITIAL.md.

    Args:
        parsed_data: Parsed INITIAL.md data

    Returns:
        {
            "complexity": "medium",
            "architectural_impact": "moderate",
            "risk_factors": ["..."],
            "success_metrics": ["..."]
        }
    """
    raw_content = parsed_data.get("raw_content", "")

    # Extract PLANNING CONTEXT section
    planning_match = re.search(
        r"##\s*PLANNING\s+CONTEXT\s*\n(.*?)(?=\n##|\Z)",
        raw_content,
        re.DOTALL | re.IGNORECASE
    )

    if not planning_match:
        return {
            "complexity": "unknown",
            "architectural_impact": "unknown",
            "risk_factors": [],
            "success_metrics": []
        }

    planning_text = planning_match.group(1)

    # Extract complexity
    complexity_match = re.search(
        r"\*\*Complexity Assessment\*\*:\s*(\w+)",
        planning_text,
        re.IGNORECASE
    )
    complexity = complexity_match.group(1) if complexity_match else "unknown"

    # Extract architectural impact
    arch_match = re.search(
        r"\*\*Architectural Impact\*\*:\s*(\w+)",
        planning_text,
        re.IGNORECASE
    )
    arch_impact = arch_match.group(1) if arch_match else "unknown"

    # Extract risk factors (lines starting with - after "Risk Factors")
    risk_section = re.search(
        r"\*\*Risk Factors\*\*:\s*\n((?:- .+\n?)+)",
        planning_text,
        re.MULTILINE
    )
    risk_factors = []
    if risk_section:
        risk_lines = risk_section.group(1).strip().split("\n")
        risk_factors = [line.lstrip("- ").strip() for line in risk_lines if line.strip()]

    return {
        "complexity": complexity,
        "architectural_impact": arch_impact,
        "risk_factors": risk_factors,
        "success_metrics": []  # TODO: Extract if needed
    }


def _extract_phases_from_thinking_result(result: Dict[str, Any]) -> str:
    """Parse implementation phases from sequential thinking result.

    Args:
        result: MCP tool result

    Returns:
        Markdown formatted phases
    """
    # Extract content
    content = ""
    if isinstance(result, dict) and "content" in result:
        if isinstance(result["content"], list):
            for item in result["content"]:
                if isinstance(item, dict) and "text" in item:
                    content += item["text"] + "\n"
        elif isinstance(result["content"], str):
            content = result["content"]

    # Extract phases (PHASE 1: ... format)
    phases_text = ""
    phase_matches = re.finditer(
        r"PHASE (\d+):\s*([^\n]+)\n((?:- .+\n?)+)",
        content,
        re.MULTILINE
    )

    for match in phase_matches:
        phase_num = match.group(1)
        phase_name = match.group(2).strip()
        phase_steps = match.group(3).strip()

        phases_text += f"### Phase {phase_num}: {phase_name}\n\n"
        phases_text += f"{phase_steps}\n\n"

    if phases_text:
        return phases_text

    # If no phases found, return empty to trigger fallback
    return ""
```

**Integration Point 3: Update synthesize_implementation()**

**File:** `tools/ce/generate.py` (line 1025)

Replace current implementation:

```python
def synthesize_implementation(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any]
) -> str:
    """Generate Implementation Steps section.

    Tries sequential thinking first, falls back to template-based.

    Args:
        parsed_data: INITIAL.md data
        serena_research: Codebase patterns

    Returns:
        Implementation steps markdown
    """
    # Try sequential thinking first
    phases_with_thinking = generate_implementation_phases_with_thinking(
        parsed_data,
        serena_research
    )

    if phases_with_thinking:
        return phases_with_thinking

    # Fallback: Template-based phases (current implementation)
    examples = parsed_data["examples"]

    steps = """### Phase 1: Setup and Research (30 min)

1. Review INITIAL.md examples and requirements
2. Analyze existing codebase patterns
3. Identify integration points

### Phase 2: Core Implementation (2-3 hours)

"""
    # Generate steps from examples
    for i, example in enumerate(examples[:3], 1):
        if example["type"] == "inline":
            steps += f"{i}. Implement {example.get('language', 'code')} component\n"
        elif example["type"] == "file_ref":
            steps += f"{i}. Reference pattern in {example['file']}\n"

    steps += """
### Phase 3: Testing and Validation (1-2 hours)

1. Write unit tests following project patterns
2. Write integration tests
3. Run validation gates
4. Update documentation
"""

    return steps
```

**Validation:**
```python
# Test sequential thinking integration
def test_extract_topics_with_thinking():
    """Test topic extraction with sequential thinking."""
    feature_text = "Build JWT authentication with FastAPI"
    serena_research = {"patterns": [], "test_patterns": [{"framework": "pytest"}]}

    topics = extract_topics_from_feature(feature_text, serena_research)

    # Should return topics (either from thinking or heuristic)
    assert len(topics) > 0
    assert len(topics) <= 5
    print(f"✅ Extracted topics: {topics}")


def test_implementation_phases_with_thinking():
    """Test implementation phase generation."""
    parsed_data = {
        "feature_name": "User Authentication",
        "feature": "Build JWT-based auth system",
        "raw_content": """
## PLANNING CONTEXT
**Complexity Assessment**: medium
**Architectural Impact**: moderate
**Risk Factors**:
- Token expiration handling
- Rate limiting
"""
    }
    serena_research = {"patterns": [], "test_patterns": []}

    phases = generate_implementation_phases_with_thinking(parsed_data, serena_research)

    # Should return phases (either from thinking or fallback)
    assert len(phases) > 0
    assert "Phase" in phases
    print(f"✅ Generated phases:\n{phases[:200]}...")
```

**Success Criteria:**
- ✅ Sequential thinking integration at 2 points (topic extraction, phase generation)
- ✅ Graceful degradation to heuristics when unavailable
- ✅ Planning context extracted from INITIAL.md
- ✅ Reasoning chain logged for transparency
- ✅ Tests verify both sequential thinking and fallback paths

---

### Phase 3: MCP Utils Module (1 hour)

**Goal:** Create reusable MCP call wrapper

**File:** `tools/ce/mcp_utils.py` (new)

**Implementation:**
```python
"""MCP utility functions for Syntropy tool calls.

Provides wrappers for calling Syntropy MCP tools with proper
error handling and logging.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def call_syntropy_mcp(
    server: str,
    tool: str,
    arguments: Dict[str, Any],
    timeout: int = 10
) -> Dict[str, Any]:
    """Call Syntropy MCP tool.

    Args:
        server: Server name (e.g., "thinking", "serena", "context7")
        tool: Tool name (e.g., "sequentialthinking", "find_symbol")
        arguments: Tool arguments
        timeout: Timeout in seconds

    Returns:
        Tool result dictionary

    Raises:
        RuntimeError: If MCP call fails

    Note: This is a placeholder. Actual implementation will use
    Claude Code's MCP infrastructure to make real tool calls.
    """
    logger.info(f"Calling Syntropy MCP: {server}:{tool}")
    logger.debug(f"Arguments: {arguments}")

    # FIXME: Placeholder - replace with actual MCP call
    # In full implementation, this would:
    # 1. Import Claude Code MCP client
    # 2. Get client for server: client = get_mcp_client(f"syntropy-{server}")
    # 3. Call tool: result = client.call_tool(tool, arguments, timeout=timeout)
    # 4. Return result

    # For now, log and raise (graceful degradation in callers)
    raise RuntimeError(
        f"MCP call not yet implemented: {server}:{tool}\n"
        f"🔧 Troubleshooting: Full MCP integration pending"
    )


def is_mcp_available(server: str) -> bool:
    """Check if MCP server is available.

    Args:
        server: Server name (e.g., "thinking", "serena")

    Returns:
        True if server available, False otherwise
    """
    try:
        # FIXME: Placeholder - replace with actual availability check
        # Would ping server or check connection status
        logger.debug(f"Checking MCP availability: {server}")
        return False  # Return False until implemented
    except Exception as e:
        logger.warning(f"MCP availability check failed: {e}")
        return False


def call_sequential_thinking(
    prompt: str,
    thought_number: int = 1,
    total_thoughts: int = 5
) -> Optional[Dict[str, Any]]:
    """Call sequential thinking MCP tool.

    Convenience wrapper for mcp__syntropy__thinking__sequentialthinking

    Args:
        prompt: Thinking prompt
        thought_number: Current thought number
        total_thoughts: Estimated total thoughts

    Returns:
        Thinking result or None if unavailable
    """
    try:
        return call_syntropy_mcp(
            "thinking",
            "sequentialthinking",
            {
                "thought": prompt,
                "thoughtNumber": thought_number,
                "totalThoughts": total_thoughts,
                "nextThoughtNeeded": True
            }
        )
    except Exception as e:
        logger.warning(f"Sequential thinking unavailable: {e}")
        return None
```

**Tests:**

**File:** `tools/tests/test_mcp_utils.py` (new)

```python
"""Tests for MCP utility functions."""

import pytest
from ce.mcp_utils import (
    call_syntropy_mcp,
    is_mcp_available,
    call_sequential_thinking
)


def test_call_syntropy_mcp_raises_not_implemented():
    """Test MCP call raises until implemented."""
    with pytest.raises(RuntimeError, match="not yet implemented"):
        call_syntropy_mcp("thinking", "sequentialthinking", {})


def test_is_mcp_available_returns_false():
    """Test availability check returns False until implemented."""
    assert is_mcp_available("thinking") is False
    assert is_mcp_available("serena") is False


def test_call_sequential_thinking_returns_none():
    """Test sequential thinking wrapper returns None gracefully."""
    result = call_sequential_thinking("Test prompt")
    assert result is None
```

**Success Criteria:**
- ✅ MCP utils module created
- ✅ Wrapper functions defined
- ✅ Error handling with graceful degradation
- ✅ Tests verify placeholder behavior

---

### Phase 4: Update generate.py Parser (30 minutes)

**Goal:** Parse PLANNING CONTEXT section from INITIAL.md

**File:** `tools/ce/generate.py`

**Update SECTION_MARKERS** (line 21-26):

```python
# Section markers for INITIAL.md parsing
SECTION_MARKERS = {
    "feature": r"^##\s*FEATURE\s*$",
    "planning": r"^##\s*PLANNING\s+CONTEXT\s*$",  # NEW
    "examples": r"^##\s*EXAMPLES\s*$",
    "documentation": r"^##\s*DOCUMENTATION\s*$",
    "other": r"^##\s*OTHER\s+CONSIDERATIONS\s*$"
}
```

**Update parse_initial_md() return** (line 123-130):

```python
    # Parse subsections
    return {
        "feature_name": feature_name,
        "feature": sections.get("feature", ""),
        "planning_context": sections.get("planning", ""),  # NEW
        "examples": extract_code_examples(sections.get("examples", "")),
        "documentation": extract_documentation_links(sections.get("documentation", "")),
        "other_considerations": sections.get("other", ""),
        "raw_content": content
    }
```

**Tests:**

**File:** `tools/tests/test_generate.py`

Add test case:

```python
def test_parse_initial_md_with_planning_context(tmp_path):
    """Test parsing INITIAL.md with PLANNING CONTEXT section."""
    initial_md = tmp_path / "INITIAL.md"
    initial_md.write_text("""
# Feature: User Auth

## FEATURE
Build JWT authentication

## PLANNING CONTEXT
**Complexity Assessment**: medium
**Architectural Impact**: moderate
**Risk Factors**:
- Token expiration
- Rate limiting

## EXAMPLES
```python
def auth():
    pass
```

## DOCUMENTATION
- [JWT](https://jwt.io)

## OTHER CONSIDERATIONS
Security concerns
""")

    result = parse_initial_md(str(initial_md))

    assert result["planning_context"]
    assert "medium" in result["planning_context"]
    assert "Token expiration" in result["planning_context"]
    print("✅ Planning context parsed successfully")
```

**Success Criteria:**
- ✅ PLANNING CONTEXT marker added
- ✅ Planning context parsed from INITIAL.md
- ✅ Test verifies parsing
- ✅ Backwards compatible (planning optional)

---

### Phase 5: CLI Integration (30 minutes)

**Goal:** Add --use-thinking flag to generate command

**File:** `tools/ce/cli_handlers.py`

**Update generate_prp_handler:**

```python
def generate_prp_handler(args):
    """Handle PRP generation command.

    Args:
        args: Argparse namespace with:
            - initial_md: Path to INITIAL.md
            - output_dir: Output directory
            - join_prp: Optional PRP to join
            - use_thinking: Use sequential thinking (default: True)
            - json: JSON output format
    """
    logger.info(f"Generating PRP from: {args.initial_md}")

    try:
        # Set environment variable for sequential thinking
        import os
        if hasattr(args, 'use_thinking'):
            os.environ['CE_USE_SEQUENTIAL_THINKING'] = 'true' if args.use_thinking else 'false'

        # Call generate_prp
        prp_path = generate_prp(
            args.initial_md,
            output_dir=args.output_dir if hasattr(args, 'output_dir') else "PRPs/feature-requests",
            join_prp=args.join_prp if hasattr(args, 'join_prp') else None
        )

        # Output
        if hasattr(args, 'json') and args.json:
            print(json.dumps({"success": True, "prp_path": prp_path}))
        else:
            print(f"✅ PRP generated: {prp_path}")

    except Exception as e:
        logger.error(f"PRP generation failed: {e}")
        if hasattr(args, 'json') and args.json:
            print(json.dumps({"success": False, "error": str(e)}))
        else:
            print(f"❌ Error: {e}")
        raise
```

**Update CLI argument parser:**

**File:** `tools/ce/__main__.py`

```python
# In prp subparser
prp_generate_parser.add_argument(
    '--use-thinking',
    action='store_true',
    default=True,
    help='Use sequential thinking for analysis (default: True)'
)
prp_generate_parser.add_argument(
    '--no-thinking',
    dest='use_thinking',
    action='store_false',
    help='Disable sequential thinking (use heuristics)'
)
```

**Usage:**
```bash
# Use sequential thinking (default)
cd tools && uv run ce prp generate ../INITIAL.md

# Disable sequential thinking
cd tools && uv run ce prp generate ../INITIAL.md --no-thinking
```

**Success Criteria:**
- ✅ --use-thinking flag added (default: True)
- ✅ --no-thinking flag for opt-out
- ✅ Environment variable controls behavior
- ✅ Backwards compatible

---

### Phase 6: Logging and Transparency (30 minutes)

**Goal:** Log sequential thinking reasoning chains

**Update generate.py logging:**

```python
def extract_topics_from_feature(
    feature_text: str,
    serena_research: Dict[str, Any]
) -> List[str]:
    """..."""
    logger.info("Extracting topics from feature text using Sequential Thinking")

    try:
        # ... sequential thinking call ...
        result = call_syntropy_mcp(...)

        # Log reasoning chain (NEW)
        _log_thinking_chain(result, "Topic Extraction")

        topics = _extract_topics_from_thinking_result(result)
        # ...
    except Exception as e:
        # ...


def _log_thinking_chain(result: Dict[str, Any], context: str) -> None:
    """Log sequential thinking reasoning chain.

    Args:
        result: MCP result with thinking chain
        context: Context label (e.g., "Topic Extraction")
    """
    logger.info(f"🧠 Sequential Thinking Chain - {context}")

    # Extract content
    content = ""
    if isinstance(result, dict) and "content" in result:
        if isinstance(result["content"], list):
            for item in result["content"]:
                if isinstance(item, dict) and "text" in item:
                    content += item["text"] + "\n"

    # Log each thought
    thoughts = re.finditer(r"Thought (\d+):\s*(.+?)(?=Thought \d+:|\Z)", content, re.DOTALL)
    for thought in thoughts:
        thought_num = thought.group(1)
        thought_text = thought.group(2).strip()[:200]  # First 200 chars
        logger.info(f"  Thought {thought_num}: {thought_text}...")

    logger.info(f"🧠 End of thinking chain - {context}")
```

**Success Criteria:**
- ✅ Reasoning chains logged with context labels
- ✅ Thought-by-thought breakdown visible
- ✅ Helps debugging and transparency

---

## 📋 Acceptance Criteria

**Must Have:**
- [ ] INITIAL.md template has PLANNING CONTEXT section
- [ ] Sequential thinking integrated for topic extraction
- [ ] Sequential thinking integrated for implementation phases
- [ ] Graceful degradation when MCP unavailable
- [ ] Planning context parsed from INITIAL.md
- [ ] MCP utils module with wrappers
- [ ] --use-thinking flag in CLI (default: True)
- [ ] Reasoning chains logged for transparency
- [ ] All tests passing (100% coverage)

**Nice to Have:**
- [ ] Sequential thinking for validation strategy
- [ ] Risk analysis using thinking chain
- [ ] Complexity estimation refinement

**Out of Scope:**
- Full MCP implementation (uses placeholders for now)
- Real-time thinking chain visualization
- Interactive thinking refinement

---

## 🧪 Testing Strategy

### Unit Tests

**File:** `tools/tests/test_generate.py`

```python
def test_extract_topics_with_thinking_fallback():
    """Test topic extraction falls back to heuristic."""
    feature_text = "Build authentication with JWT"
    serena_research = {"patterns": []}

    topics = extract_topics_from_feature(feature_text, serena_research)

    # Should get heuristic topics (thinking not yet implemented)
    assert "authentication" in topics or "general" in topics


def test_implementation_phases_fallback():
    """Test phase generation falls back to template."""
    parsed_data = {
        "feature_name": "Test",
        "feature": "Test feature",
        "examples": [],
        "raw_content": ""
    }
    serena_research = {"patterns": []}

    phases = synthesize_implementation(parsed_data, serena_research)

    # Should get template-based phases
    assert "Phase 1" in phases
    assert "Phase 2" in phases
```

### Integration Tests

```bash
# Create test INITIAL.md with planning context
cat > /tmp/test-initial.md << 'EOF'
# Feature: Test Feature

## FEATURE
Test description

## PLANNING CONTEXT
**Complexity Assessment**: simple
**Architectural Impact**: isolated

## EXAMPLES
```python
def test():
    pass
```

## DOCUMENTATION
- "pytest"
EOF

# Generate PRP
cd tools
uv run ce prp generate /tmp/test-initial.md

# Verify planning context used
grep "simple" /tmp/test-initial.md
```

---

## 📚 Dependencies

**External:**
- Syntropy MCP server with thinking tool
- Python 3.10+

**Internal:**
- PRP-3 (generate-prp foundation)
- Syntropy MCP tool: `mcp__syntropy__thinking__sequentialthinking`

**Files Modified:**
- `INITIAL.md` (add PLANNING CONTEXT section)
- `.claude/commands/generate-prp.md` (update docs)
- `tools/ce/generate.py` (integrate sequential thinking)
- `tools/ce/mcp_utils.py` (new, MCP wrappers)
- `tools/ce/__main__.py` (add --use-thinking flag)
- `tools/ce/cli_handlers.py` (update handler)
- `tools/tests/test_generate.py` (add tests)
- `tools/tests/test_mcp_utils.py` (new, test wrappers)

---

## ⚠️ Risks & Mitigations

**Risk 1: Sequential thinking slow (>5s)**
- **Mitigation:** Add timeout (10s), fall back to heuristic
- **Metric:** Log thinking duration, warn if >5s

**Risk 2: Thinking results inconsistent**
- **Mitigation:** Robust parsing with fallback
- **Testing:** Test malformed results

**Risk 3: MCP unavailable breaks workflow**
- **Mitigation:** Graceful degradation to heuristics
- **Testing:** Test all fallback paths

---

## 📖 References

**Sequential Thinking Documentation:**
- MCP tool: `mcp__syntropy__thinking__sequentialthinking`
- Syntropy docs: See syntropy-mcp/README.md

**Existing Patterns:**
- `tools/ce/generate.py` (current implementation)
- `tools/ce/context.py` (MCP resilience patterns)

**Related PRPs:**
- PRP-3: Command Automation (generate-prp foundation)
- PRP-29.1: Syntropy Init (MCP infrastructure)

---

## 🎯 Success Metrics

**Implementation:**
- Time to implement: 5-6 hours (estimated)
- Code coverage: 90%+ for new functions
- Sequential thinking success rate: Track % using thinking vs heuristic

**User Experience:**
- Deeper PRP analysis visible in logs
- Better time estimates from planning context
- Risk-aware validation strategies

**Quality:**
- All error messages include 🔧 troubleshooting
- Graceful degradation tested
- No fishy fallbacks
