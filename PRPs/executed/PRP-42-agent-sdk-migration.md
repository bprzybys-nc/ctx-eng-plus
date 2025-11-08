---
prp_id: PRP-42
title: Migrate from Anthropic Python SDK to Claude Agent SDK
status: rejected
created: "2025-11-08"
estimated_hours: 9
complexity: medium
tags: [infrastructure, api, quota-management]
rejection_reason: "Wrong approach - Agent SDK doesn't provide Max quota for standalone CLI. See PRP-43 for correct Task-based solution."
rejection_date: "2025-11-08"
superseded_by: "PRP-43"
---

# PRP-42: Migrate from Anthropic Python SDK to Claude Agent SDK

## TL;DR

Replace direct `anthropic` Python SDK usage with `claude-agent-sdk` to leverage Claude Max 5x quota benefits, automatic context management, and built-in retry logic.

**Impact**: Enables 5x higher quota limits for CE tooling (blending, classification, PRP generation)

**Files Modified**:
- `tools/pyproject.toml` - Update dependencies
- `tools/ce/blending/llm_client.py` - Replace Anthropic client with Agent SDK
- `tools/ce/blending/classification.py` - Replace Anthropic client with Agent SDK
- `tools/ce/mcp_utils.py` - Remove placeholder MCP logic (if Agent SDK handles it)
- `tools/tests/ce/blending/test_*.py` - Update tests for new API

## Context

### Current State

CE tools use `anthropic>=0.40.0` directly:

**tools/ce/blending/llm_client.py:76-80**
```python
self.client = Anthropic(
    api_key=self.api_key,
    timeout=timeout,
    max_retries=max_retries
)
```

**tools/ce/blending/classification.py:437**
```python
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
```

**Current limitations**:
- Standard API quota limits (not 5x Claude Max quota)
- Manual retry logic with exponential backoff
- No automatic context compaction
- Manual token tracking

### Goal State

Use `claude-agent-sdk` for all Claude API interactions:

**Benefits**:
1. **5x Quota**: Access Claude Max 5x quota pool automatically
2. **Auto Context Management**: SDK handles compaction to avoid context overflows
3. **Built-in Retries**: No manual exponential backoff needed
4. **Prompt Caching**: Automatic optimization for repeat requests
5. **Error Handling**: Richer error types for troubleshooting

**API Pattern**:
```python
from claude_agent_sdk import query, ClaudeAgentOptions

async def blend_content(framework, target):
    options = ClaudeAgentOptions(
        system_prompt=BLENDING_PHILOSOPHY,
        max_turns=1,
        model="claude-sonnet-4-5"
    )

    result = []
    async for message in query(
        prompt=build_prompt(framework, target),
        options=options
    ):
        result.append(message)

    return "".join(result)
```

## Problem

User needs to maximize Claude Max 5x quota benefits for CE tooling operations (blending, classification, PRP generation with LLM validation).

Current direct SDK usage:
- Uses standard API quota (not 5x pool)
- Manual retry logic prone to errors
- No automatic context management for long documents

## Proposed Solution

### Phase 1: Dependency Migration

**Update pyproject.toml**:
```toml
dependencies = [
    "claude-agent-sdk>=0.1.6",  # Replace anthropic>=0.40.0
    "anyio>=4.0.0",  # For async runtime
    # ... other deps unchanged
]
```

**Installation**:
```bash
cd tools
uv remove anthropic
uv add claude-agent-sdk
uv add anyio
uv sync
```

### Phase 2: Refactor BlendingLLM Class

**New wrapper pattern** (tools/ce/blending/llm_client.py):

```python
"""LLM client for blending operations using Claude Agent SDK."""

import anyio
from claude_agent_sdk import query, ClaudeAgentOptions
from typing import Dict, Any, Optional

class BlendingLLM:
    """
    Claude Agent SDK wrapper for blending operations.

    Provides hybrid model support with automatic quota management:
    - Haiku: Fast/cheap classification and similarity checks
    - Sonnet: High-quality document blending
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        # Store config for SDK calls
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.timeout = timeout
        self.max_retries = max_retries

        # Token tracking (estimate from SDK responses)
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def blend_content(
        self,
        framework_content: str,
        target_content: Optional[str],
        rules_content: Optional[str] = None,
        domain: str = "unknown"
    ) -> Dict[str, Any]:
        """Blend content using Agent SDK (Sonnet)."""

        # Build prompt (same as before)
        prompt = self._build_blend_prompt(
            framework_content, target_content, rules_content, domain
        )

        # Use Agent SDK
        options = ClaudeAgentOptions(
            system_prompt=BLENDING_PHILOSOPHY,
            max_turns=1,
            model=SONNET_MODEL,
            api_key=self.api_key,
            timeout=self.timeout
        )

        # Run async query
        blended = anyio.run(self._query_agent, prompt, options)

        return {
            "blended": blended,
            "model": SONNET_MODEL,
            "tokens": self._estimate_tokens(prompt, blended),
            "confidence": self._calculate_confidence(
                framework_content, target_content, blended
            )
        }

    async def _query_agent(self, prompt: str, options) -> str:
        """Execute Agent SDK query."""
        result = []
        async for message in query(prompt=prompt, options=options):
            result.append(message)
        return "".join(result)

    def _estimate_tokens(self, prompt: str, response: str) -> Dict[str, int]:
        """Estimate token usage (Agent SDK doesn't expose usage directly)."""
        # Rough estimate: 4 chars = 1 token
        input_tokens = len(prompt) // 4
        output_tokens = len(response) // 4

        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens

        return {
            "input": input_tokens,
            "output": output_tokens
        }
```

**Key changes**:
- Replace `Anthropic()` client with `ClaudeAgentOptions` config
- Use `anyio.run()` for async execution in sync context
- Agent SDK handles retries automatically (remove manual logic)
- Token tracking becomes estimation (SDK doesn't expose usage)

### Phase 3: Refactor Classification Module

**Update tools/ce/blending/classification.py**:

Replace `classify_with_haiku()` (lines 333-487):

```python
async def _classify_with_agent_sdk(
    file_path: str,
    file_type: str,
    content: str
) -> ClassificationResult:
    """Classify using Agent SDK (Haiku)."""

    system_prompt = _get_classification_prompt(file_type)

    options = ClaudeAgentOptions(
        system_prompt=system_prompt,
        max_turns=1,
        model="claude-3-5-haiku-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    prompt = f"Classify this file:\n\n{content[:4000]}"

    result = []
    async for message in query(prompt=prompt, options=options):
        result.append(message)

    response_text = "".join(result)

    # Parse JSON response (same as before)
    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if not json_match:
        return ClassificationResult(
            valid=False,
            confidence=0.5,
            issues=["Agent SDK returned invalid JSON"],
            file_type="unknown"
        )

    parsed = json.loads(json_match.group(0))

    return ClassificationResult(
        valid=parsed.get("valid", False),
        confidence=parsed.get("confidence", 0.5),
        issues=parsed.get("issues", []),
        file_type=file_type if parsed.get("valid") else "unknown"
    )

def classify_with_haiku(file_path: str, file_type: str) -> ClassificationResult:
    """Wrapper to run async classification in sync context."""
    content = Path(file_path).read_text(encoding='utf-8')
    return anyio.run(_classify_with_agent_sdk, file_path, file_type, content)
```

### Phase 4: Update Tests

**Test pattern changes**:

```python
# Before (mocking Anthropic client)
from unittest.mock import patch, MagicMock

@patch('ce.blending.llm_client.Anthropic')
def test_blend_content(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.return_value = mock_client
    # ...

# After (mocking Agent SDK query)
from unittest.mock import patch, AsyncMock

@patch('ce.blending.llm_client.query')
async def test_blend_content(mock_query):
    mock_query.return_value = AsyncMock(
        __aiter__=lambda self: self,
        __anext__=lambda self: "blended result"
    )
    # ...
```

**Update test files**:
- `tools/tests/ce/blending/test_llm_client.py`
- `tools/tests/ce/blending/test_classification.py`
- Any integration tests using Anthropic SDK

### Phase 5: Remove Obsolete Code

**Files to clean up**:

1. **tools/ce/mcp_utils.py** - Check if Agent SDK makes MCP wrappers obsolete
   - If Agent SDK exposes MCP tools natively, remove file
   - If not, keep as separate MCP integration layer

2. **Manual retry logic** - Remove exponential backoff code
   - Agent SDK handles retries automatically
   - Remove custom `max_retries` handling

3. **Token tracking** - Switch to estimation
   - Agent SDK doesn't expose usage directly
   - Use 4-char-per-token heuristic or token counter library

## Implementation Steps

### Step 0: Validate Quota Claim (30 min) **CRITICAL - DO FIRST**

**⚠️ BLOCKER**: Verify Agent SDK actually uses 5x Claude Max quota before proceeding.

```bash
cd tools
cat > ../tmp/test_quota.py << 'EOF'
"""Test if Agent SDK uses Claude Max 5x quota pool."""
import anyio
from claude_agent_sdk import query, ClaudeAgentOptions
from anthropic import Anthropic
import os

async def test_agent_sdk():
    """Make small API call with Agent SDK."""
    options = ClaudeAgentOptions(
        system_prompt="You are helpful",
        max_turns=1,
        model="claude-3-5-haiku-20241022",
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )

    result = []
    async for message in query(prompt="Say 'hello'", options=options):
        result.append(message)

    return "".join(result)

def test_anthropic_sdk():
    """Make small API call with Anthropic SDK."""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=10,
        messages=[{"role": "user", "content": "Say 'hello'"}]
    )
    return response.content[0].text

# Test both
print("Testing Anthropic SDK...")
anthro_result = test_anthropic_sdk()
print(f"✓ Anthropic SDK: {anthro_result}")

print("\nTesting Agent SDK...")
agent_result = anyio.run(test_agent_sdk)
print(f"✓ Agent SDK: {agent_result}")

print("\n🔧 Manual Step Required:")
print("1. Go to https://console.anthropic.com/settings/usage")
print("2. Check which quota pool was used for each call:")
print("   - Standard API quota → Not getting 5x benefit")
print("   - Claude Max quota → ✓ Getting 5x benefit")
print("\nIf Agent SDK does NOT use 5x quota → ABORT THIS PRP")
EOF

uv add claude-agent-sdk anyio  # Temporary install for test
uv run ce run_py ../tmp/test_quota.py
```

**Decision Gate**:
- [ ] Agent SDK confirmed to use Claude Max 5x quota → Proceed
- [ ] Agent SDK uses standard quota → **ABORT PRP**, use alternative approach

**Alternative if quota NOT 5x**:
1. Keep existing `anthropic` SDK
2. Optimize token usage (better prompts, caching)
3. Request quota increase from Anthropic support

### Step 1: Update Dependencies (30 min)

```bash
cd tools
uv remove anthropic
uv add claude-agent-sdk anyio
uv sync
```

**Validation**:
```bash
uv run python -c "from claude_agent_sdk import query; print('✓ Agent SDK installed')"
```

### Step 2: Refactor BlendingLLM (2 hours)

- [ ] Update imports
- [ ] Replace `Anthropic()` client with `ClaudeAgentOptions`
- [ ] Refactor `blend_content()` to use `query()`
- [ ] Add `_query_agent()` async helper
- [ ] Update `check_similarity()` and `classify_file()` similarly
- [ ] Add token estimation logic

**Test**:
```bash
cd tools
uv run python -c "
from ce.blending.llm_client import BlendingLLM
llm = BlendingLLM()
result = llm.blend_content('# Framework', None, domain='test')
print('✓ BlendingLLM works:', result['blended'][:50])
"
```

### Step 3: Refactor Classification (1.5 hours)

- [ ] Update imports in `classification.py`
- [ ] Replace `classify_with_haiku()` with Agent SDK version
- [ ] Add `anyio.run()` wrapper for sync context
- [ ] Keep deterministic validators unchanged

**Test**:
```bash
cd tools
uv run python -c "
from ce.blending.classification import classify_file
result = classify_file('PRPs/executed/PRP-1.md')
print('✓ Classification works:', result.valid, result.confidence)
"
```

### Step 4: Update Tests (2 hours)

- [ ] Update test imports (`patch` targets)
- [ ] Mock `query()` instead of `Anthropic()`
- [ ] Update async test patterns
- [ ] Run full test suite

**Validation**:
```bash
cd tools
uv run pytest tests/ce/blending/ -v
```

### Step 5: Integration Testing (1 hour)

- [ ] Test blending with real API call (small prompt)
- [ ] Test classification with real API call
- [ ] Verify quota usage in Anthropic Console
- [ ] Check token estimation accuracy

**Test script**:
```bash
cd tools
uv run ce run_py ../tmp/test_agent_sdk.py
```

```python
# tmp/test_agent_sdk.py
from ce.blending.llm_client import BlendingLLM

llm = BlendingLLM()

# Test blend
result = llm.blend_content(
    framework_content="# Test Framework\n\nCore rule.",
    target_content=None,
    domain="test"
)

print(f"✓ Blended: {result['blended'][:100]}")
print(f"✓ Tokens: {result['tokens']}")
print(f"✓ Model: {result['model']}")

# Test similarity
sim_result = llm.check_similarity("Hello world", "Hello world")
print(f"✓ Similarity: {sim_result['score']}")

print("\n✓ All Agent SDK tests passed")
```

### Step 6: Documentation Update (30 min)

- [ ] Update CLAUDE.md (Quick Commands section)
- [ ] Update docstrings in `llm_client.py`
- [ ] Add troubleshooting for Agent SDK errors
- [ ] Document quota benefits

**CLAUDE.md section**:
```markdown
## LLM Client - Claude Agent SDK

**Quota**: Uses Claude Max 5x quota pool automatically

**API**:
```python
from ce.blending.llm_client import BlendingLLM

llm = BlendingLLM()

# Blending (Sonnet)
result = llm.blend_content(framework, target, rules, domain="claude_md")

# Similarity (Haiku)
sim = llm.check_similarity(text1, text2, threshold=0.9)

# Classification (Haiku)
classification = llm.classify_file(content, patterns, file_path)
```

**Token tracking**: Estimated (4 chars = 1 token heuristic)

**Retries**: Automatic via Agent SDK (no manual backoff)
```

### Step 7: Cleanup & Validation (1.5 hours)

**Critical**: Ensure old `anthropic` SDK completely removed to force errors on any missed imports.

```bash
cd tools

# 1. Verify anthropic SDK removed from pyproject.toml
grep -q "anthropic" pyproject.toml && echo "❌ BLOCKER: anthropic still in deps" || echo "✓ anthropic removed"

# 2. Force removal from virtual env (ensure no stale imports)
uv remove anthropic
uv sync --no-cache  # Rebuild venv from scratch

# 3. Verify import fails (should error)
uv run python -c "from anthropic import Anthropic" 2>&1 | grep -q "ModuleNotFoundError" && echo "✓ anthropic SDK purged" || echo "❌ BLOCKER: anthropic still importable"
```

**Cleanup checklist**:
- [ ] `anthropic` removed from `pyproject.toml` dependencies
- [ ] `uv sync --no-cache` completed (clean rebuild)
- [ ] `from anthropic import Anthropic` fails with ModuleNotFoundError
- [ ] Review `tools/ce/mcp_utils.py` - decide keep vs remove
- [ ] Remove commented-out Anthropic SDK code
- [ ] Remove unused imports (`import os` if not needed, etc.)
- [ ] Search for stray `anthropic` references: `rg -i "anthropic" tools/ce/`

**Full regression test**:
```bash
cd tools

# Run ALL tests (not just blending)
uv run pytest tests/ -v

# Validate entire codebase
uv run ce validate --level all

# Quick functional test
uv run ce run_py ../tmp/test_agent_sdk.py
```

**Validation gates**:
- [ ] Zero `anthropic` imports in codebase: `rg "from anthropic|import anthropic" tools/ce/ || echo "✓ Clean"`
- [ ] All tests pass: `uv run pytest tests/ -v` exits 0
- [ ] Validation passes: `uv run ce validate --level all` exits 0
- [ ] Real API calls work (Step 5 test script succeeds)

## Validation Gates

### Gate 1: Dependency Migration

- [ ] `claude-agent-sdk>=0.1.6` in pyproject.toml
- [ ] `anthropic` removed from dependencies
- [ ] `uv sync` succeeds
- [ ] Import test passes: `from claude_agent_sdk import query`

### Gate 2: BlendingLLM Refactor

- [ ] All methods use Agent SDK (no `Anthropic()` calls)
- [ ] Token tracking implemented (estimation)
- [ ] Async helpers added (`_query_agent()`)
- [ ] Docstrings updated with new API

### Gate 3: Classification Refactor

- [ ] `classify_with_haiku()` uses Agent SDK
- [ ] `anyio.run()` wrapper works in sync context
- [ ] Deterministic validators unchanged (no API calls)

### Gate 4: Tests Pass

- [ ] All blending tests pass: `uv run pytest tests/ce/blending/ -v`
- [ ] Mock patterns updated (patch `query` not `Anthropic`)
- [ ] No deprecation warnings

### Gate 5: Integration Tests

- [ ] Real API call succeeds (small test)
- [ ] Quota tracked in Anthropic Console under "Agent SDK" or "Claude Max"
- [ ] Token estimates within 20% of actual (if available)
- [ ] No 429 rate limit errors (Agent SDK handles retries)

### Gate 6: Documentation

- [ ] CLAUDE.md updated with Agent SDK patterns
- [ ] Docstrings reference new API
- [ ] Troubleshooting section added for Agent SDK errors

### Gate 7: Full Validation & Cleanup

- [ ] `anthropic` SDK completely removed from pyproject.toml
- [ ] `from anthropic import Anthropic` fails with ModuleNotFoundError (stale imports purged)
- [ ] `uv sync --no-cache` completed successfully
- [ ] Zero `anthropic` references in codebase: `rg "from anthropic|import anthropic" tools/ce/` returns nothing
- [ ] `uv run ce validate --level all` passes
- [ ] `uv run pytest tests/ -v` (all tests pass, including blending)
- [ ] No regressions in blending/classification accuracy
- [ ] Real API calls work with Agent SDK (Step 5 test script succeeds)

## Risks & Mitigations

### Risk 1: Agent SDK doesn't expose token usage

**Impact**: Token tracking becomes estimation (less accurate)

**Mitigation**:
- Use 4-char-per-token heuristic (industry standard)
- Add optional integration with `tiktoken` for precise counting
- Log warning when estimates diverge from quota

**Fallback**: Keep token tracking as "estimate" and document limitation

### Risk 2: Agent SDK async pattern breaks sync code

**Impact**: Existing sync callers fail (e.g., CLI commands)

**Mitigation**:
- Wrap async calls with `anyio.run()` for sync compatibility
- Test all CLI entry points: `ce vacuum`, PRP commands

**Fallback**: Create sync wrappers in `llm_client.py`

### Risk 3: Agent SDK quota not 5x as expected

**Impact**: No quota benefit from migration

**Mitigation**:
- Verify in Anthropic Console after migration
- Test with large batch (e.g., 10 blending calls)
- Contact Anthropic support if quota not applied

**Fallback**: Document actual quota behavior, keep Agent SDK for other benefits (retries, caching)

### Risk 4: Test mocking complexity increases

**Impact**: Tests harder to write/maintain

**Mitigation**:
- Create test helper: `mock_agent_query(response_text)`
- Document async mock patterns in test docstrings
- Add examples in test files

**Fallback**: Use real API calls in integration tests, mock only unit tests

## Success Criteria

- [ ] **Zero Anthropic SDK imports**: `grep -r "from anthropic import" tools/ce/` returns nothing
- [ ] **All tests pass**: `uv run pytest tests/ -v` exits 0
- [ ] **Quota verified**: Anthropic Console shows requests using Claude Max 5x pool
- [ ] **No regressions**: Blending/classification accuracy same or better
- [ ] **Documentation updated**: CLAUDE.md and docstrings reference Agent SDK

## Rollback Plan

**If migration fails or quota benefit not realized**:

### Immediate Rollback (15 min)

```bash
cd tools

# 1. Restore anthropic SDK
uv remove claude-agent-sdk anyio
uv add anthropic>=0.40.0
uv sync

# 2. Restore code from git
git checkout tools/ce/blending/llm_client.py
git checkout tools/ce/blending/classification.py
git checkout tools/pyproject.toml

# 3. Restore tests
git checkout tools/tests/ce/blending/

# 4. Verify restoration
uv run pytest tests/ce/blending/ -v
uv run ce validate --level all
```

### Verification After Rollback

- [ ] `anthropic>=0.40.0` in pyproject.toml
- [ ] All blending tests pass
- [ ] Token tracking shows precise counts (not estimates)
- [ ] No Agent SDK imports remain

## Related PRPs

None (initial infrastructure migration)

## Notes

**Why Agent SDK over direct API?**

1. **Quota**: Claude Max 5x quota applies automatically
2. **Context Management**: Auto compaction prevents overflow
3. **Retries**: Built-in exponential backoff
4. **Future-proof**: Anthropic's recommended SDK for agents

**Token tracking limitation**:

Agent SDK doesn't expose `response.usage` like Anthropic SDK. We use estimation:
- Input: `len(prompt) // 4` tokens
- Output: `len(response) // 4` tokens

Accuracy: ~80-90% (good enough for drift scoring)

**Async pattern**:

Agent SDK is async-first. Use `anyio.run()` for sync compatibility:

```python
def blend_content(self, framework, target):
    return anyio.run(self._blend_async, framework, target)

async def _blend_async(self, framework, target):
    async for msg in query(prompt=..., options=...):
        # process
```

**MCP utils obsolescence**:

`tools/ce/mcp_utils.py` has placeholder MCP code. After migration:
- If Agent SDK exposes MCP tools → remove file
- If not → keep as separate integration (unlikely)

Check Agent SDK docs for MCP support before removing.

---

## Peer Review Notes

### Review Date: 2025-11-08

**Reviewer**: Context-naive peer review (Claude Code)

**Findings**:

1. **Critical - PRP ID Fixed**: Updated YAML header and title from `AGENT-SDK-MIGRATION` to `PRP-42`

2. **Critical - Quota Validation Added**: Added Step 0 with test script to verify 5x quota claim BEFORE migration
   - **Rationale**: No documentation confirms Agent SDK uses Claude Max 5x quota
   - **Decision gate**: ABORT PRP if quota not actually 5x
   - **Alternative**: Keep `anthropic` SDK, optimize usage instead

3. **Critical - Checkboxes Fixed**: Changed all `[x]` to `[ ]` in implementation steps (PRP not executed yet)

4. **Medium - Rollback Plan Added**: Added rollback section with git checkout steps

5. **Remaining Concerns** (for user decision):
   - **Minimal dependencies principle**: Does 5x quota justify 2 new deps (`claude-agent-sdk` + `anyio`)?
   - **Token tracking regression**: Is 80-90% estimation acceptable vs precise counts?
   - **Test complexity increase**: Async mocks more complex than current simple patches

6. **Markdown Linting**: 19 warnings remain (MD032, MD031) - blank lines needed around lists/code blocks

7. **Display Issue - Line Breaks**: Peer review output formatting needs fix
   - **Current display**: `PRP: PRP-42-agent-sdk-migration.mdReviewed: 2025-11-08T00:00:00Z` (no line break)
   - **Expected display**:

     ```
     PRP: PRP-42-agent-sdk-migration.md
     Reviewed: 2025-11-08T00:00:00Z
     ```

   - **Root cause**: Missing newline in peer review template output
   - **Fix location**: `.claude/commands/peer-review.md` template or command implementation
   - **Action**: Update peer review command to add `\n` after PRP filename in output formatting

8. **Cleanup Enhancement Added**: Step 7 now includes thorough cleanup
   - **Added**: `uv sync --no-cache` to rebuild venv from scratch (removes stale imports)
   - **Added**: Verification that `from anthropic import Anthropic` fails with ModuleNotFoundError
   - **Added**: `rg` search for any stray `anthropic` references
   - **Rationale**: Force errors on missed imports, ensure old SDK completely purged
   - **Time adjusted**: 8h → 9h (Step 7: 1h → 1.5h)

**Recommendation**: **DO NOT EXECUTE** until Step 0 quota validation confirms 5x benefit. If quota NOT 5x, consider alternative approaches.

---

## REJECTION SUMMARY (2025-11-08)

### Why This PRP Was Rejected

**Step 0 validation revealed fundamental flaw**:

1. **Tested Agent SDK quota** - CSV showed `usage_type: standard` (not Max)
2. **Researched official docs** - Anthropic Support confirms:
   - Claude Code prioritizes `ANTHROPIC_API_KEY` env var over subscription
   - To use Max quota: **must execute code inside Claude Code Task context**
3. **Validated Claude Desktop's approach**:
   - `anthropic.Anthropic()` without API key ONLY works in Task subagents
   - Standalone CLI (`uv run ce blend`) **cannot** access Max quota

### The Real Solution

**Max 5x quota is accessible** - but NOT via Agent SDK migration.

**Correct approach** (PRP-43):
- Refactor CE CLI tools to Task-based architecture
- Keep existing `anthropic` SDK (no migration needed!)
- Execute blending/classification as Task subagents inside Claude Code
- Automatic Max quota inheritance via Claude Code session

### Architecture Comparison

**Current (Standalone CLI)**:
```bash
$ uv run ce blend --source framework --target user
# Requires ANTHROPIC_API_KEY → Uses API quota ❌
```

**Task-Based (PRP-43)**:
```
User: "Initialize CE framework"
Claude Code → Task subagent:
  from anthropic import Anthropic
  client = Anthropic()  # No key needed
  # Inherits Max quota automatically ✅
```

### Lessons Learned

1. **Agent SDK ≠ Max quota** - SDK is for building agents, not quota management
2. **Execution context matters** - Same code, different quota depending on how it runs
3. **Step 0 validation essential** - Prevented 9 hours of wasted migration work

### Next Steps

- ✅ Close PRP-42 as rejected
- ✅ Create PRP-43 (Task-based architecture refactoring)
- ✅ Clean up Agent SDK test dependencies
- ✅ Use PRP-43 as input for `/batch-gen-prp` (large refactor → multiple PRPs)
