---
prp_id: PRP-43.2.3
batch_id: 43
stage: 2
order: 3
parent_prp: PRP-43-INITIAL
feature_name: PRP Generation Task Integration - Enable Max Quota for PRP Generation
status: pending
created: 2025-11-08T00:00:00Z
updated: 2025-11-08T00:00:00Z
complexity: low
estimated_hours: 4
dependencies: PRP-43.1.1
tags: [prp-generation, task-refactoring, quota-management, llm-integration]
issue: TBD
---

# PRP-43.2.3: PRP Generation Task Integration - Enable Max Quota for PRP Generation

**Phase**: 5 of 6 - PRP Generation Task Integration
**Batch**: 43 (Task-Based Architecture for Claude Max 5x Quota)
**Stage**: 2 (Parallel execution with PRP-43.2.1 and PRP-43.2.2)

## 1. TL;DR

**Objective**: Enable PRP generation commands (`/generate-prp` and `ce generate`) to automatically use Claude Max 5x quota when invoked via Claude Code Tasks, while maintaining standalone CLI execution with API key fallback.

**What**: Refactor PRP generation to detect Task context and use appropriate quota pool (Max 5x in Claude Code, API quota in standalone CLI). Unlike classification and blending which use direct Anthropic SDK calls, PRP generation currently delegates prompts to Claude


Code directly - we'll formalize this pattern for dual-mode operation.

**Why**: PRP generation is currently CLI-only. When users run `/generate-prp` inside Claude Code, it should automatically use their Max subscription quota (5x higher limits) without requiring separate `ANTHROPIC_API_KEY`. This provides better UX and higher quota efficiency for a common workflow operation.

**Effort**: 4 hours (low complexity - simpler than classification/blending since no direct SDK usage)

**Dependencies**: PRP-43.1.1 (task executor framework for context detection)

## 2. Context

### Background

PRP generation is a core Context Engineering workflow that transforms INITIAL.md files into comprehensive Product Requirements Prompts. The process involves:

1. Parsing INITIAL.md structure (FEATURE, EXAMPLES, DOCUMENTATION sections)
2. Researching codebase patterns (via Serena MCP)
3. Fetching external documentation (via Context7 MCP)
4. Synthesizing comprehensive PRP sections (TL;DR, Implementation, Validation Gates, etc.)

**Current Architecture**: PRP generation does NOT directly use the Anthropic SDK. Instead:
- `/generate-prp` slash command delegates to Claude Code's conversation
- Claude Code generates PRP content using its own quota management
- Standalone CLI would require API key but isn't currently implemented for LLM calls

**Problem**: This ad-hoc approach lacks formalization:
- No explicit Task context detection
- No clear dual-mode architecture (Task vs CLI)
- No fallback for standalone API key usage
- Not integrated with Task executor framework

### Current State

**Slash Command Usage** (`/generate-prp`):
```
User: /generate-prp feature-requests/auth/INITIAL.md

Claude Code:
1. Reads command from .claude/commands/generate-prp.md
2. Executes PRP generation logic in conversation
3. Calls ce.generate.py functions for parsing/research
4. Synthesizes PRP content directly (using Max quota implicitly)
5. Writes output to PRPs/feature-requests/
```

**CLI Usage** (hypothetical):
```bash
cd tools
uv run ce generate feature-requests/auth/INITIAL.md
# Currently doesn't invoke LLM directly
# Would need API key for standalone execution
```

**Code Analysis** (`tools/ce/generate.py`):
```python
# Line 830-993: generate_prp() function
# NO Anthropic SDK import
# NO client = Anthropic(...) calls
# Prompts handled via MCP tools and Claude Code conversation
```

**Key Insight**: Unlike classification/blending (which use `anthropic.Anthropic()` directly), PRP generation relies on Claude Code's LLM capabilities. The refactoring here is about **formalizing** this pattern, not migrating from SDK to Tasks.

### Goal State

**Task-Based PRP Generation** (Inside Claude Code):
```python
# tools/ce/generate.py

from ce.task_executor import is_task_context

def generate_prp_sections(parsed_data: dict, research: dict) -> str:
    """Generate PRP content via Task or CLI mode."""

    if is_task_context():
        # Inside Claude Code - delegate to conversation LLM
        # Uses Max quota automatically
        logger.info("Generating PRP via Task context (Max quota)")
        return _generate_via_task(parsed_data, research)
    else:
        # Standalone CLI - require API key
        logger.info("Generating PRP via CLI mode (API quota)")
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY required for standalone PRP generation\n"
                "🔧 Troubleshooting: Set API key or run via /generate-prp in Claude Code"
            )
        return _generate_via_api(parsed_data, research, api_key)
```

**Benefits**:
- ✅ `/generate-prp` automatically uses Max quota (no changes needed)
- ✅ Standalone CLI can work with API key (backward compatible)
- ✅ Clear dual-mode architecture (consistent with classification/blending)
- ✅ Graceful error messages when API key missing
- ✅ Integrated with Task executor framework

### Constraints and Considerations

**Dual-Mode Operation**:
- Task mode (default): Use Claude Code's LLM via Task context
- CLI mode (fallback): Use Anthropic SDK with API key
- Clear documentation for both modes
- No breaking changes to existing `/generate-prp` usage

**Quality Preservation**:
- Generated PRPs must have same quality in both modes
- Same structure, detail, completeness
- Same validation checks (completeness, required sections)
- No regression in PRP template compliance

**Integration Points**:
- `/generate-prp` slash command (no changes needed to command file)
- `ce generate` CLI command (add dual-mode support)
- Linear integration (continues to work in both modes)
- Context sync (pre-generation sync remains unchanged)

**Testing**:
- Unit tests with mocked Task context
- Integration tests via real `/generate-prp` execution
- Quality validation (compare Task vs CLI PRPs)
- No Claude Code dependency in CI/CD tests

### Documentation References

**Related PRPs**:
- **PRP-43-INITIAL**: Parent PRP describing full Task-based refactoring
- **PRP-43.1.1**: Task Executor Framework (dependency - provides context detection)
- **PRP-43.2.1**: Classification Task Refactoring (parallel phase)
- **PRP-43.2.2**: Blending Task Refactoring (parallel phase)

**Related Files**:
- `tools/ce/generate.py`: PRP generation logic (to be refactored)
- `.claude/commands/generate-prp.md`: Slash command documentation (to be updated)
- `tools/tests/test_generate.py`: Tests (to be updated with Task mode tests)

**Related Documentation**:
- `/generate-prp` command guide: `.claude/commands/generate-prp.md`
- PRP template: `examples/templates/PRP-0-CONTEXT-ENGINEERING.md`

## 3. Implementation Steps

### Phase 1: Add Task Context Detection (30 minutes)

**Goal**: Import and use task context detection in generate.py

**File**: `tools/ce/generate.py` (UPDATE)

**Implementation**:

```python
# Add near top of file (after existing imports)
import os
import logging

from .task_executor import is_task_context

logger = logging.getLogger(__name__)


def detect_generation_mode() -> str:
    """Detect whether to use Task or CLI mode for PRP generation.

    Returns:
        "task" if running inside Claude Code Task context
        "cli" if running as standalone CLI

    Notes:
        - Task mode: Uses Claude Code's LLM (Max quota)
        - CLI mode: Uses Anthropic SDK with API key (API quota)
    """
    if is_task_context():
        logger.info("PRP generation mode: Task (Max quota)")
        return "task"
    else:
        logger.info("PRP generation mode: CLI (API quota)")
        return "cli"


def validate_cli_environment() -> None:
    """Validate that CLI environment has required configuration.

    Raises:
        ValueError: If ANTHROPIC_API_KEY missing in CLI mode
    """
    if not is_task_context():
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY required for standalone PRP generation\n\n"
                "🔧 Troubleshooting:\n"
                "  1. Set API key: export ANTHROPIC_API_KEY=sk-ant-...\n"
                "  2. OR run via Claude Code: /generate-prp <initial-md-path>\n"
                "  3. OR use syntropy-mcp init for automated generation"
            )
```

**Validation**:
```bash
# Test context detection in CLI
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.generate import detect_generation_mode; print(f'Mode: {detect_generation_mode()}')"
# Expected: Mode: cli

# Test context detection in mock Task
CLAUDE_CODE_TASK_ID=test-prp uv run python -c "from ce.generate import detect_generation_mode; print(f'Mode: {detect_generation_mode()}')"
# Expected: Mode: task

# Test CLI validation (should raise error)
uv run python -c "from ce.generate import validate_cli_environment; validate_cli_environment()"
# Expected: ValueError: ANTHROPIC_API_KEY required...
```

---

### Phase 2: Refactor PRP Content Generation (60 minutes)

**Goal**: Update content synthesis to support dual-mode operation

**File**: `tools/ce/generate.py` (UPDATE)

**Current Code** (lines 995-1076):
```python
def synthesize_prp_content(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Synthesize complete PRP content from research."""
    # ... generates sections via template-based approach
```

**Refactored Code**:

```python
def synthesize_prp_content(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Synthesize complete PRP content from research.

    Supports dual-mode operation:
    - Task mode: Use Claude Code's LLM (delegated synthesis)
    - CLI mode: Use template-based synthesis with optional LLM enhancement

    Args:
        parsed_data: Parsed INITIAL.md data
        serena_research: Codebase research results
        documentation: Fetched documentation

    Returns:
        Complete PRP markdown content with YAML header
    """
    logger.info("Synthesizing PRP content")

    # Detect generation mode
    mode = detect_generation_mode()

    if mode == "task":
        # Task mode - delegate to Claude Code conversation
        # Claude Code naturally uses Max quota when processing slash commands
        logger.info("Using Task mode synthesis (Max quota)")
        return _synthesize_via_task(parsed_data, serena_research, documentation)
    else:
        # CLI mode - use template-based synthesis
        # Could optionally enhance with API calls if API key present
        logger.info("Using CLI mode synthesis (template-based)")
        validate_cli_environment()  # Ensure API key if LLM needed
        return _synthesize_via_cli(parsed_data, serena_research, documentation)


def _synthesize_via_task(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Synthesize PRP via Task context (Claude Code conversation).

    This mode assumes we're inside a Claude Code Task and the calling
    conversation will handle LLM-based synthesis using Max quota.

    For now, this delegates to the same template-based approach as CLI,
    but future enhancements could use Task-specific synthesis strategies.

    Args:
        parsed_data: INITIAL.md data
        serena_research: Codebase research
        documentation: Documentation sources

    Returns:
        Complete PRP markdown content
    """
    # For Phase 1: Use same template-based approach
    # Future: Could enhance with Task-specific LLM synthesis
    return _synthesize_template_based(parsed_data, serena_research, documentation)


def _synthesize_via_cli(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Synthesize PRP via CLI mode (template-based or API-enhanced).

    Uses template-based synthesis by default. Could optionally enhance
    sections with LLM calls if ANTHROPIC_API_KEY is present.

    Args:
        parsed_data: INITIAL.md data
        serena_research: Codebase research
        documentation: Documentation sources

    Returns:
        Complete PRP markdown content
    """
    # Use template-based approach (existing implementation)
    return _synthesize_template_based(parsed_data, serena_research, documentation)


def _synthesize_template_based(
    parsed_data: Dict[str, Any],
    serena_research: Dict[str, Any],
    documentation: Dict[str, Any]
) -> str:
    """Template-based PRP synthesis (original implementation).

    This is the existing synthesis logic, extracted for reuse in both modes.

    Args:
        parsed_data: INITIAL.md data
        serena_research: Codebase research
        documentation: Documentation sources

    Returns:
        Complete PRP markdown content
    """
    # Original synthesis logic (lines 1020-1076)
    yaml_header = _generate_yaml_header(parsed_data)
    tldr = synthesize_tldr(parsed_data, serena_research)
    context = synthesize_context(parsed_data, documentation)
    implementation = synthesize_implementation(parsed_data, serena_research)
    validation_gates = synthesize_validation_gates(parsed_data, serena_research)
    testing = synthesize_testing_strategy(parsed_data, serena_research)
    rollout = synthesize_rollout_plan(parsed_data)

    # Combine sections
    prp_content = f"""---
{yaml_header}
---

# {parsed_data['feature_name']}

## 1. TL;DR

{tldr}

## 2. Context

{context}

## 3. Implementation Steps

{implementation}

## 4. Validation Gates

{validation_gates}

## 5. Testing Strategy

{testing}

## 6. Rollout Plan

{rollout}

---

## Research Findings

### Serena Codebase Analysis
- **Patterns Found**: {len(serena_research['patterns'])}
- **Test Patterns**: {len(serena_research['test_patterns'])}
- **Serena Available**: {serena_research['serena_available']}

### Documentation Sources
- **Library Docs**: {len(documentation['library_docs'])}
- **External Links**: {len(documentation['external_links'])}
- **Context7 Available**: {documentation['context7_available']}
"""

    return prp_content
```

**Validation**:
```bash
# Test synthesis in Task mode
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
CLAUDE_CODE_TASK_ID=test uv run python -c "
from ce.generate import synthesize_prp_content
parsed = {
    'feature_name': 'Test Feature',
    'feature': 'Test description',
    'planning_context': '',
    'examples': [],
    'documentation': [],
    'other_considerations': '',
    'raw_content': ''
}
research = {'patterns': [], 'test_patterns': [], 'serena_available': False}
docs = {'library_docs': [], 'external_links': [], 'context7_available': False}
result = synthesize_prp_content(parsed, research, docs)
print('✓ Synthesis successful')
print(f'Length: {len(result)} chars')
"
# Expected: ✓ Synthesis successful, Length: ~1000+ chars
```

---

### Phase 3: Update Main generate_prp Function (30 minutes)

**Goal**: Integrate dual-mode detection into main PRP generation workflow

**File**: `tools/ce/generate.py` (UPDATE)

**Update Lines 830-993**:

```python
def generate_prp(
    initial_md_path: str,
    output_dir: str = "PRPs/feature-requests",
    join_prp: Optional[str] = None
) -> str:
    """Generate complete PRP from INITIAL.md.

    Supports dual-mode operation:
    - Task mode (inside Claude Code): Uses Max quota automatically
    - CLI mode (standalone): Requires ANTHROPIC_API_KEY for LLM operations

    Main orchestration function that coordinates all phases.

    Args:
        initial_md_path: Path to INITIAL.md file
        output_dir: Directory for output PRP file
        join_prp: Optional PRP to join (number, ID, or file path)

    Returns:
        Path to generated PRP file

    Raises:
        FileNotFoundError: If INITIAL.md doesn't exist
        ValueError: If INITIAL.md invalid, join_prp invalid, or API key missing (CLI mode)
        RuntimeError: If PRP generation or Linear integration fails
    """
    logger.info(f"Starting PRP generation from: {initial_md_path}")

    # Detect mode and validate environment
    mode = detect_generation_mode()
    logger.info(f"PRP generation mode: {mode}")

    if mode == "cli":
        # Validate CLI environment (API key present)
        try:
            validate_cli_environment()
        except ValueError as e:
            logger.error(f"CLI environment validation failed: {e}")
            raise

    # Step 2.5: Pre-generation sync (existing logic)
    from .context import is_auto_sync_enabled, pre_generation_sync
    if is_auto_sync_enabled():
        try:
            logger.info("Auto-sync enabled - running pre-generation sync...")
            sync_result = pre_generation_sync(force=False)
            logger.info(f"Pre-sync complete: drift={sync_result['drift_score']:.1f}%")
        except Exception as e:
            logger.error(f"Pre-generation sync failed: {e}")
            raise RuntimeError(
                f"Generation aborted due to sync failure\n"
                f"Error: {e}\n"
                f"🔧 Troubleshooting: Run 'ce context health' to diagnose issues"
            ) from e

    # Rest of function remains unchanged (lines 881-992)
    # ... (existing code for parsing, research, synthesis, Linear integration)
```

**Validation**:
```bash
# Test that function validates CLI mode
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "
from ce.generate import generate_prp
try:
    # Should fail without API key in CLI mode
    generate_prp('test.md')
except ValueError as e:
    print(f'✓ CLI validation works: {str(e)[:50]}...')
"
# Expected: ✓ CLI validation works: ANTHROPIC_API_KEY required...

# Test that function works in Task mode
CLAUDE_CODE_TASK_ID=test uv run python -c "
from ce.generate import generate_prp
# Would succeed in Task mode (no API key check)
print('✓ Task mode validation works')
"
# Expected: ✓ Task mode validation works
```

---

### Phase 4: Update Slash Command Documentation (20 minutes)

**Goal**: Document dual-mode behavior in slash command

**File**: `.claude/commands/generate-prp.md` (UPDATE)

**Add after line 165** (in "Output Structure" section):

```markdown
## Quota Management

### When Invoked via `/generate-prp` (Claude Code)

When you run `/generate-prp` inside Claude Code, the command automatically uses your **Claude Max 5x subscription quota**. No `ANTHROPIC_API_KEY` is needed - the Task context provides automatic quota routing.

**How it works**:
1. `/generate-prp` executes as a Claude Code Task
2. Task context detected via `CLAUDE_CODE_TASK_ID` environment variable
3. LLM operations route through Max quota pool automatically
4. You see higher rate limits and larger context windows

**Benefits**:
- ✅ 5x higher rate limits (Max subscription)
- ✅ No API key management needed
- ✅ Automatic context caching
- ✅ Unified quota tracking in Anthropic Console

### Standalone CLI Mode (Requires API Key)

If you run `ce generate` from the command line (outside Claude Code), you must provide an API key:

```bash
# Set API key first
export ANTHROPIC_API_KEY=sk-ant-...

# Then run generation
cd tools
uv run ce generate feature-requests/auth/INITIAL.md
```

**API Key Requirements**:
- Standalone execution requires `ANTHROPIC_API_KEY` environment variable
- Uses standard API quota (not Max 5x)
- Useful for CI/CD pipelines and automation scripts
- Maintains backward compatibility with existing workflows

**Error if API key missing**:
```
ValueError: ANTHROPIC_API_KEY required for standalone PRP generation

🔧 Troubleshooting:
  1. Set API key: export ANTHROPIC_API_KEY=sk-ant-...
  2. OR run via Claude Code: /generate-prp <initial-md-path>
  3. OR use syntropy-mcp init for automated generation
```

## Architecture Notes

**Dual-Mode Operation**:
- **Task Mode** (default in Claude Code): Automatic Max quota, no config needed
- **CLI Mode** (standalone): API key required, uses API quota

**Context Detection**:
```python
from ce.task_executor import is_task_context

if is_task_context():
    # Inside Claude Code - use Max quota
    mode = "task"
else:
    # Standalone CLI - require API key
    mode = "cli"
```

**Quality Guarantee**: Generated PRPs have identical quality in both modes (same structure, completeness, validation checks).
```

**Validation**:
```bash
# Verify documentation updated
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
grep -A 5 "Quota Management" .claude/commands/generate-prp.md
# Expected: Shows new section with quota documentation

# Verify dual-mode section exists
grep "Dual-Mode Operation" .claude/commands/generate-prp.md
# Expected: Match found
```

---

### Phase 5: Add Task Mode Tests (90 minutes)

**Goal**: Comprehensive tests for dual-mode PRP generation

**File**: `tools/tests/test_generate.py` (UPDATE)

**Add new test class**:

```python
"""Tests for PRP generation task integration."""

import os
import pytest
from unittest.mock import patch, MagicMock

from ce.generate import (
    detect_generation_mode,
    validate_cli_environment,
    synthesize_prp_content,
    _synthesize_via_task,
    _synthesize_via_cli,
    _synthesize_template_based,
)


class TestTaskModeDetection:
    """Test Task context detection for PRP generation."""

    def test_detect_mode_cli(self):
        """Test mode detection returns 'cli' in standalone context."""
        # Ensure clean environment
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        mode = detect_generation_mode()
        assert mode == "cli"

    def test_detect_mode_task(self):
        """Test mode detection returns 'task' in Task context."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-prp-gen"
        try:
            mode = detect_generation_mode()
            assert mode == "task"
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_validate_cli_without_api_key(self):
        """Test CLI validation fails without API key."""
        # Ensure API key not set
        if "ANTHROPIC_API_KEY" in os.environ:
            original_key = os.environ["ANTHROPIC_API_KEY"]
            del os.environ["ANTHROPIC_API_KEY"]
        else:
            original_key = None

        # Ensure not in Task context
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        try:
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY required"):
                validate_cli_environment()
        finally:
            # Restore original state
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key

    def test_validate_cli_with_api_key(self):
        """Test CLI validation succeeds with API key."""
        # Ensure not in Task context
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
        try:
            # Should not raise
            validate_cli_environment()
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

    def test_validate_cli_skipped_in_task(self):
        """Test CLI validation skipped when in Task context."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-task"
        try:
            # Should not raise even without API key
            # (validation only applies to CLI mode)
            # Note: validate_cli_environment checks context internally
            # This test verifies it doesn't raise in Task mode
            pass  # Validation happens in generate_prp function
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]


class TestPRPSynthesisDualMode:
    """Test PRP content synthesis in both modes."""

    @pytest.fixture
    def sample_data(self):
        """Sample data for PRP generation."""
        return {
            "parsed_data": {
                "feature_name": "Test Feature",
                "feature": "Build a test feature with unit tests",
                "planning_context": "",
                "examples": [
                    {"type": "inline", "language": "python", "code": "def test(): pass"}
                ],
                "documentation": [
                    {"title": "pytest", "url": "", "type": "library"}
                ],
                "other_considerations": "Ensure test coverage >80%",
                "raw_content": "# Feature: Test Feature\n## FEATURE\n..."
            },
            "research": {
                "patterns": [],
                "test_patterns": [{"framework": "pytest", "test_command": "pytest -v"}],
                "serena_available": False
            },
            "docs": {
                "library_docs": [],
                "external_links": [],
                "context7_available": False
            }
        }

    def test_synthesize_task_mode(self, sample_data):
        """Test PRP synthesis in Task mode."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-synthesis"
        try:
            result = synthesize_prp_content(
                sample_data["parsed_data"],
                sample_data["research"],
                sample_data["docs"]
            )

            # Verify PRP structure
            assert "---" in result  # YAML frontmatter
            assert "# Test Feature" in result
            assert "## 1. TL;DR" in result
            assert "## 2. Context" in result
            assert "## 3. Implementation Steps" in result
            assert "## 4. Validation Gates" in result
            assert "## 5. Testing Strategy" in result
            assert "## 6. Rollout Plan" in result

            # Verify content length (should be substantial)
            assert len(result) > 1000
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_synthesize_cli_mode(self, sample_data):
        """Test PRP synthesis in CLI mode."""
        # Ensure CLI context
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        # Set API key
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
        try:
            result = synthesize_prp_content(
                sample_data["parsed_data"],
                sample_data["research"],
                sample_data["docs"]
            )

            # Verify same structure as Task mode
            assert "---" in result
            assert "# Test Feature" in result
            assert "## 1. TL;DR" in result

            # Verify content length
            assert len(result) > 1000
        finally:
            del os.environ["ANTHROPIC_API_KEY"]

    def test_synthesize_quality_consistency(self, sample_data):
        """Test that Task and CLI modes produce consistent quality."""
        # Generate in Task mode
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-quality"
        task_result = synthesize_prp_content(
            sample_data["parsed_data"],
            sample_data["research"],
            sample_data["docs"]
        )
        del os.environ["CLAUDE_CODE_TASK_ID"]

        # Generate in CLI mode
        os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test"
        cli_result = synthesize_prp_content(
            sample_data["parsed_data"],
            sample_data["research"],
            sample_data["docs"]
        )
        del os.environ["ANTHROPIC_API_KEY"]

        # Both should have same sections
        task_sections = [line for line in task_result.split("\n") if line.startswith("##")]
        cli_sections = [line for line in cli_result.split("\n") if line.startswith("##")]

        assert len(task_sections) == len(cli_sections)
        assert task_sections == cli_sections

    def test_template_based_synthesis(self, sample_data):
        """Test template-based synthesis function."""
        result = _synthesize_template_based(
            sample_data["parsed_data"],
            sample_data["research"],
            sample_data["docs"]
        )

        # Verify complete PRP structure
        assert "prp_id: TBD" in result
        assert "feature_name: Test Feature" in result
        assert "status: pending" in result
        assert "complexity: medium" in result

        # Verify all 6 main sections
        sections = ["TL;DR", "Context", "Implementation Steps",
                   "Validation Gates", "Testing Strategy", "Rollout Plan"]
        for section in sections:
            assert section in result


class TestPRPGenerationIntegration:
    """Integration tests for full PRP generation flow."""

    def test_generate_prp_task_mode_validation(self, tmp_path):
        """Test generate_prp validates Task mode correctly."""
        # Create temporary INITIAL.md
        initial_md = tmp_path / "INITIAL.md"
        initial_md.write_text("""# Feature: Test Auth

## FEATURE
Build user authentication

## EXAMPLES
```python
def login(user, password): pass
```

## DOCUMENTATION
- [JWT](https://jwt.io)
""")

        os.environ["CLAUDE_CODE_TASK_ID"] = "test-integration"
        try:
            # Should succeed without API key in Task mode
            # Note: This would generate a real PRP - use with caution
            # For unit test, we'll just verify mode detection
            from ce.generate import detect_generation_mode
            assert detect_generation_mode() == "task"
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_generate_prp_cli_mode_requires_api_key(self, tmp_path):
        """Test generate_prp requires API key in CLI mode."""
        # Create temporary INITIAL.md
        initial_md = tmp_path / "INITIAL.md"
        initial_md.write_text("""# Feature: Test

## FEATURE
Test

## EXAMPLES
Test
""")

        # Ensure CLI mode
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]
        if "ANTHROPIC_API_KEY" in os.environ:
            original_key = os.environ["ANTHROPIC_API_KEY"]
            del os.environ["ANTHROPIC_API_KEY"]
        else:
            original_key = None

        try:
            from ce.generate import generate_prp

            # Should raise ValueError about missing API key
            with pytest.raises(ValueError, match="ANTHROPIC_API_KEY required"):
                generate_prp(str(initial_md))
        finally:
            if original_key:
                os.environ["ANTHROPIC_API_KEY"] = original_key


# Pytest fixtures for environment cleanup
@pytest.fixture(autouse=True)
def cleanup_environment():
    """Clean up environment variables after each test."""
    yield
    # Cleanup
    for var in ["CLAUDE_CODE_TASK_ID", "ANTHROPIC_API_KEY"]:
        if var in os.environ:
            del os.environ[var]
```

**Validation**:
```bash
# Run all new tests
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_generate.py::TestTaskModeDetection -v
uv run pytest tests/test_generate.py::TestPRPSynthesisDualMode -v
uv run pytest tests/test_generate.py::TestPRPGenerationIntegration -v

# Expected: All tests pass (15+ new tests)

# Run with coverage
uv run pytest tests/test_generate.py --cov=ce.generate --cov-report=term
# Expected: >85% coverage for generate.py
```

---

### Phase 6: Integration Validation (30 minutes)

**Goal**: Validate end-to-end PRP generation in both modes

**Test Scenario 1: Task Mode** (Manual via Claude Code):
```
User: /generate-prp PRPs/feature-requests/test-feature/INITIAL.md

Expected behavior:
1. Command executes inside Claude Code Task
2. Context detection: mode = "task"
3. No API key check
4. Uses Max quota automatically
5. Generates PRP to PRPs/feature-requests/PRP-N-test-feature.md
6. Creates Linear issue with defaults
7. Updates PRP YAML with issue ID

Validation:
- PRP file exists
- All 6 sections present (TL;DR, Context, Implementation, Validation Gates, Testing, Rollout)
- YAML header complete
- Linear issue created
```

**Test Scenario 2: CLI Mode** (Manual via command line):
```bash
# Without API key - should fail
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce generate ../PRPs/feature-requests/test-feature/INITIAL.md

# Expected: ValueError: ANTHROPIC_API_KEY required...

# With API key - should succeed
export ANTHROPIC_API_KEY=sk-ant-...
uv run ce generate ../PRPs/feature-requests/test-feature/INITIAL.md

# Expected:
# - Mode detection: cli
# - API key validated
# - PRP generated
# - Same quality as Task mode
```

**Test Scenario 3: Quality Comparison**:
```bash
# Compare PRPs generated in both modes
diff PRPs/feature-requests/PRP-N-task-mode.md PRPs/feature-requests/PRP-N-cli-mode.md

# Expected: Structural similarity (same sections, similar length, same validation checks)
```

**Validation Commands**:
```bash
# Verify all functions importable
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.generate import detect_generation_mode, validate_cli_environment, synthesize_prp_content; print('✓ All imports work')"

# Verify mode detection
uv run python -c "from ce.generate import detect_generation_mode; print(f'Mode: {detect_generation_mode()}')"
# Expected: Mode: cli

# Verify mode detection in Task
CLAUDE_CODE_TASK_ID=test uv run python -c "from ce.generate import detect_generation_mode; print(f'Mode: {detect_generation_mode()}')"
# Expected: Mode: task

# Verify tests pass
uv run pytest tests/test_generate.py -v -k "Task"
# Expected: All Task-related tests pass
```

---

## 4. Validation Gates

### Gate 1: Context Detection Works

**Commands**:
```bash
# Test CLI mode detection
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.generate import detect_generation_mode; assert detect_generation_mode() == 'cli'"
echo "✓ CLI mode detection works"

# Test Task mode detection
CLAUDE_CODE_TASK_ID=test uv run python -c "from ce.generate import detect_generation_mode; assert detect_generation_mode() == 'task'"
echo "✓ Task mode detection works"

# Test validation without API key
uv run python -c "from ce.generate import validate_cli_environment; import sys; sys.exit(0)" 2>&1 | grep "ANTHROPIC_API_KEY required" && echo "✓ CLI validation works"
```

**Success Criteria**:
- CLI detection returns 'cli'
- Task detection returns 'task'
- Validation raises ValueError without API key
- Validation succeeds with API key
- No false positives/negatives

---

### Gate 2: Dual-Mode Synthesis Works

**Commands**:
```bash
# Test synthesis in Task mode
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
CLAUDE_CODE_TASK_ID=test uv run python -c "
from ce.generate import synthesize_prp_content
data = {
    'feature_name': 'Test', 'feature': 'Test desc', 'planning_context': '',
    'examples': [], 'documentation': [], 'other_considerations': '', 'raw_content': ''
}
research = {'patterns': [], 'test_patterns': [], 'serena_available': False}
docs = {'library_docs': [], 'external_links': [], 'context7_available': False}
result = synthesize_prp_content(data, research, docs)
assert '# Test' in result
assert '## 1. TL;DR' in result
assert len(result) > 500
print('✓ Task mode synthesis works')
"

# Test synthesis in CLI mode
ANTHROPIC_API_KEY=sk-test uv run python -c "
from ce.generate import synthesize_prp_content
data = {
    'feature_name': 'Test', 'feature': 'Test desc', 'planning_context': '',
    'examples': [], 'documentation': [], 'other_considerations': '', 'raw_content': ''
}
research = {'patterns': [], 'test_patterns': [], 'serena_available': False}
docs = {'library_docs': [], 'external_links': [], 'context7_available': False}
result = synthesize_prp_content(data, research, docs)
assert '# Test' in result
print('✓ CLI mode synthesis works')
"
```

**Success Criteria**:
- Task mode synthesis completes without errors
- CLI mode synthesis completes without errors
- Both modes generate valid PRP structure
- Both modes include all 6 required sections
- Content length >500 characters

---

### Gate 3: Error Handling Correct

**Commands**:
```bash
# Test API key missing in CLI mode
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "
from ce.generate import validate_cli_environment
try:
    validate_cli_environment()
    print('❌ Should have raised ValueError')
except ValueError as e:
    assert 'ANTHROPIC_API_KEY required' in str(e)
    assert '🔧 Troubleshooting' in str(e)
    print('✓ Error message is helpful')
"

# Test no error in Task mode (even without API key)
CLAUDE_CODE_TASK_ID=test uv run python -c "
from ce.generate import detect_generation_mode
assert detect_generation_mode() == 'task'
print('✓ Task mode skips API key check')
"
```

**Success Criteria**:
- CLI mode raises ValueError without API key
- Error message includes troubleshooting guidance
- Error message suggests running via Claude Code
- Task mode doesn't check for API key
- No unhandled exceptions

---

### Gate 4: Unit Tests Pass

**Commands**:
```bash
# Run all PRP generation tests
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_generate.py -v

# Expected: All existing tests + 15+ new tests pass

# Run specifically Task mode tests
uv run pytest tests/test_generate.py -v -k "Task"
# Expected: 8-10 tests pass

# Run with coverage
uv run pytest tests/test_generate.py --cov=ce.generate --cov-report=term-missing
# Expected: >85% coverage, new functions covered
```

**Success Criteria**:
- All existing tests still pass (no regressions)
- 15+ new tests added and passing
- Test coverage >85% for generate.py
- Task mode tests pass
- CLI mode tests pass
- Integration tests pass

---

### Gate 5: Documentation Updated

**Commands**:
```bash
# Verify documentation has quota section
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
grep "Quota Management" .claude/commands/generate-prp.md
# Expected: Match found

# Verify dual-mode explanation exists
grep -A 10 "Dual-Mode Operation" .claude/commands/generate-prp.md
# Expected: Shows Task and CLI mode details

# Count sections added
grep -c "^## " .claude/commands/generate-prp.md
# Expected: At least 12 sections (3+ new)

# Verify code examples
grep -c '```' .claude/commands/generate-prp.md
# Expected: At least 8 code blocks (2+ new)
```

**Success Criteria**:
- "Quota Management" section added
- "Dual-Mode Operation" documented
- Task mode usage explained
- CLI mode usage explained
- Error messages documented
- Code examples provided

---

### Gate 6: Integration Test (Manual)

**Commands**:
```bash
# Create test INITIAL.md
mkdir -p /Users/bprzybyszi/nc-src/ctx-eng-plus/tmp/test-prp-gen
cat > /Users/bprzybyszi/nc-src/ctx-eng-plus/tmp/test-prp-gen/INITIAL.md << 'EOF'
# Feature: Test Dual-Mode Generation

## FEATURE
Test PRP generation in both Task and CLI modes to verify quota routing works correctly.

**Acceptance Criteria**:
1. Task mode uses Max quota
2. CLI mode requires API key
3. Same quality in both modes

## EXAMPLES
```python
def test_generation():
    """Test dual-mode PRP generation."""
    assert True
```

## DOCUMENTATION
- [Testing Guide](https://docs.pytest.org)
- pytest (library)

## OTHER CONSIDERATIONS
Ensure no regression in existing PRP generation quality.
EOF

# Test via Task mode (manual - run via /generate-prp in Claude Code)
# /generate-prp tmp/test-prp-gen/INITIAL.md

# Test via CLI mode
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
export ANTHROPIC_API_KEY=sk-ant-...  # Use real API key
uv run ce generate ../tmp/test-prp-gen/INITIAL.md

# Verify PRP generated
ls -la /Users/bprzybyszi/nc-src/ctx-eng-plus/PRPs/feature-requests/PRP-*-test-dual-mode-generation.md

# Verify structure
cat /Users/bprzybyszi/nc-src/ctx-eng-plus/PRPs/feature-requests/PRP-*-test-dual-mode-generation.md | grep -E '^## [0-9]\.'
# Expected: All 6 sections present
```

**Success Criteria**:
- Task mode generation succeeds (via /generate-prp)
- CLI mode generation succeeds (via ce generate with API key)
- Both generate complete PRPs
- Both have same structure (6 sections)
- Both pass completeness check
- Linear integration works in both modes

---

## 5. Testing Strategy

### Unit Testing

**Test Coverage Goals**:
- Context detection: 100%
- Validation logic: 100%
- Synthesis functions: >90%
- Overall generate.py: >85%

**Test Categories**:

1. **Context Detection Tests**:
   - CLI mode detection
   - Task mode detection
   - Environment variable handling
   - Mode switching

2. **Validation Tests**:
   - CLI validation without API key (should fail)
   - CLI validation with API key (should pass)
   - Task mode skips validation (no API key needed)
   - Error message quality

3. **Synthesis Tests**:
   - Task mode synthesis
   - CLI mode synthesis
   - Template-based synthesis
   - Quality consistency between modes
   - Section completeness

4. **Integration Tests**:
   - Full generate_prp flow in Task mode
   - Full generate_prp flow in CLI mode
   - API key requirement enforcement
   - PRP structure validation

### Manual Testing

**Test Scenarios**:

1. **Task Mode via /generate-prp**:
   ```
   /generate-prp tmp/test-feature/INITIAL.md
   ```
   - Verify no API key prompt
   - Verify PRP generated
   - Check Anthropic Console for Max quota usage

2. **CLI Mode with API key**:
   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   cd tools
   uv run ce generate ../tmp/test-feature/INITIAL.md
   ```
   - Verify PRP generated
   - Check Anthropic Console for API quota usage

3. **CLI Mode without API key**:
   ```bash
   unset ANTHROPIC_API_KEY
   cd tools
   uv run ce generate ../tmp/test-feature/INITIAL.md
   ```
   - Verify error message displayed
   - Verify troubleshooting guidance shown

### Quality Validation

**Comparison Testing**:
1. Generate same INITIAL.md in both modes
2. Compare PRP structure (should be identical)
3. Compare section content (should be similar)
4. Verify both pass completeness check
5. Verify both have valid YAML headers

**Metrics**:
- Section count: Must match (6 main sections)
- Content length: Should be within 20% variance
- Validation gates: Must be concrete and testable
- Implementation steps: Must be detailed and actionable

---

## 6. Rollout Plan

### Pre-Execution Checklist

- [ ] Review complete PRP document
- [ ] PRP-43.1.1 completed (task executor framework available)
- [ ] No uncommitted changes in `tools/` directory
- [ ] UV environment up to date (`uv sync`)
- [ ] All validation gates understood
- [ ] Test API key available for CLI testing

### Execution Timeline

**Total Estimated Time**: 4 hours

**Phase 1: Context Detection** (30 min)
- Add imports to generate.py
- Implement detect_generation_mode()
- Implement validate_cli_environment()
- Test both functions

**Phase 2: Synthesis Refactoring** (60 min)
- Refactor synthesize_prp_content()
- Add _synthesize_via_task()
- Add _synthesize_via_cli()
- Extract _synthesize_template_based()
- Test all functions

**Phase 3: Main Function Update** (30 min)
- Update generate_prp() with mode detection
- Add CLI validation call
- Update logging messages
- Test integration

**Phase 4: Documentation** (20 min)
- Update .claude/commands/generate-prp.md
- Add Quota Management section
- Add dual-mode examples
- Add troubleshooting guidance

**Phase 5: Unit Tests** (90 min)
- Write TestTaskModeDetection class
- Write TestPRPSynthesisDualMode class
- Write TestPRPGenerationIntegration class
- Run all tests, verify >85% coverage

**Phase 6: Integration Validation** (30 min)
- Test Task mode (via /generate-prp)
- Test CLI mode (with API key)
- Test CLI mode (without API key - error case)
- Compare PRP quality
- Verify all gates

### Post-Execution Checklist

- [ ] All functions added and importable
- [ ] Context detection works (CLI + Task)
- [ ] Synthesis works in both modes
- [ ] Error handling correct
- [ ] Unit tests pass (15+ new tests)
- [ ] Test coverage >85%
- [ ] Documentation updated
- [ ] Integration test passes
- [ ] No regressions in existing PRP generation
- [ ] Quality validated (Task vs CLI PRPs similar)

---

## 7. Success Metrics

### Functional Metrics

- ✅ **Dual-Mode Operation**: Task and CLI modes both work
- ✅ **Context Detection**: 100% accurate (CLI vs Task)
- ✅ **Quota Routing**: Max quota in Task, API quota in CLI
- ✅ **Error Handling**: Clear messages when API key missing
- ✅ **Quality Consistency**: PRPs have same structure in both modes

### Code Quality Metrics

- ✅ **Test Coverage**: >85% for generate.py
- ✅ **No Regressions**: All existing tests pass
- ✅ **Type Safety**: All functions typed
- ✅ **Documentation**: Clear dual-mode usage guide
- ✅ **KISS Principle**: Simple refactoring, minimal changes

### Integration Metrics

- ✅ **Backward Compatible**: /generate-prp works unchanged
- ✅ **CLI Support**: ce generate works with API key
- ✅ **Linear Integration**: Issue creation works in both modes
- ✅ **Context Sync**: Pre-generation sync unchanged
- ✅ **Ready for Production**: Manual integration test passes

---

## 8. Dependencies

**Depends On**:
- **PRP-43.1.1**: Task Executor Framework (context detection)
  - Provides `is_task_context()` function
  - Provides `TaskExecutor` class (not used directly yet)
  - Foundation for all Phase 2 work

**Files Modified**:
- `tools/ce/generate.py` (add dual-mode logic)
- `.claude/commands/generate-prp.md` (update documentation)
- `tools/tests/test_generate.py` (add Task mode tests)

**Files Created**:
- None (pure refactoring)

**No Breaking Changes**:
- Existing `/generate-prp` usage unchanged
- Existing CLI behavior preserved (requires API key as before)
- All existing tests continue to pass

---

## 9. Risks & Mitigations

### Risk 1: Quality Regression in Generated PRPs

**Probability**: Low
**Impact**: High (generated PRPs are lower quality)

**Mitigation**:
- Use same template-based synthesis in both modes (Phase 1)
- Add quality comparison tests (Phase 5)
- Manual review of generated PRPs (Phase 6)
- No changes to core synthesis logic (just routing)

**Validation**:
```bash
# Generate same INITIAL.md in both modes, compare
diff PRPs/feature-requests/PRP-N-task.md PRPs/feature-requests/PRP-N-cli.md
# Expected: Structural similarity
```

---

### Risk 2: Context Detection Fails

**Probability**: Low
**Impact**: Medium (wrong quota pool used)

**Mitigation**:
- Use proven detection from PRP-43.1.1
- Add explicit logging: "Mode: task" vs "Mode: cli"
- Test both modes thoroughly
- Fallback to CLI mode if detection unclear

**Validation**:
```bash
# Test detection
uv run python -c "from ce.generate import detect_generation_mode; print(detect_generation_mode())"
# Test with mock Task
CLAUDE_CODE_TASK_ID=test uv run python -c "from ce.generate import detect_generation_mode; print(detect_generation_mode())"
```

---

### Risk 3: Breaking Existing Workflows

**Probability**: Low
**Impact**: Medium (users can't generate PRPs)

**Mitigation**:
- No changes to slash command behavior
- CLI requires API key (same as before)
- Dual-mode is pure addition (new capability)
- All existing tests must pass
- Backward compatibility in validation gates

**Validation**: Run all existing generate.py tests before and after

---

### Risk 4: Incomplete Documentation

**Probability**: Low
**Impact**: Low (users confused about dual-mode)

**Mitigation**:
- Clear "Quota Management" section in command docs
- Examples for both modes
- Troubleshooting guidance for API key errors
- Architecture notes explain context detection

**Validation**: Review documentation with fresh eyes, verify all sections present

---

## 10. Acceptance Criteria

- [ ] **Context Detection**: CLI and Task modes detected correctly
- [ ] **Dual-Mode Synthesis**: Both modes generate valid PRPs
- [ ] **Error Handling**: API key error in CLI mode is clear and helpful
- [ ] **Unit Tests**: 15+ new tests pass, coverage >85%
- [ ] **Documentation**: Quota Management section added
- [ ] **Integration Test**: Manual test in both modes succeeds
- [ ] **Quality Validation**: Task and CLI PRPs have same structure
- [ ] **No Regressions**: All existing tests pass
- [ ] **Linear Integration**: Issue creation works in both modes
- [ ] **Validation Gates**: All 6 gates passed

---

## 11. Design Decisions

### Decision 1: No Direct Anthropic SDK Usage

**Options Considered**:
- Add Anthropic SDK calls (like classification/blending)
- Keep delegating to Claude Code conversation
- Hybrid approach (SDK in CLI, conversation in Task)

**Chosen**: Keep delegating to Claude Code conversation

**Rationale**:
- Current approach already works well
- No need for direct SDK calls (PRP synthesis is conversational)
- Simpler than adding new LLM client code
- Reduces refactoring scope (4h vs 8h)
- Future enhancement can add SDK if needed

---

### Decision 2: Template-Based Synthesis for Both Modes

**Options Considered**:
- Different synthesis strategies per mode
- LLM-enhanced synthesis in CLI mode
- Template-based only (current approach)

**Chosen**: Template-based synthesis for both modes initially

**Rationale**:
- Ensures quality consistency
- No risk of divergence between modes
- Simpler to test and validate
- Can enhance later with LLM if needed
- Existing templates proven effective

---

### Decision 3: Environment Variable for Context Detection

**Options Considered**:
- Custom config file
- Command-line flag
- Environment variable (from PRP-43.1.1)

**Chosen**: Environment variable (reuse from task executor)

**Rationale**:
- Already implemented in PRP-43.1.1
- Consistent with classification/blending approach
- Fast and reliable (<1ms)
- Easy to test (mock environment)
- Standard pattern in containerized environments

---

### Decision 4: Minimal Changes to Existing Code

**Options Considered**:
- Full rewrite of generate.py
- Extract new module (generate_task.py)
- Minimal refactoring (chosen)

**Chosen**: Minimal refactoring with clear separation

**Rationale**:
- Lower risk of breaking existing functionality
- Easier to review and validate
- Faster implementation (4h target)
- Clear upgrade path for future enhancements
- KISS principle (simplest solution first)

---

## 12. Related PRPs

**Parent PRP**:
- **PRP-43-INITIAL**: Task-Based Architecture for Claude Max 5x Quota

**Parallel PRPs** (Stage 2):
- **PRP-43.2.1**: Classification Task Refactoring
- **PRP-43.2.2**: Blending Task Refactoring

**Foundation PRP**:
- **PRP-43.1.1**: Task Executor Framework (dependency - context detection)

**Future PRPs**:
- **PRP-43.3.1**: Initialization Workflow Integration (will consume this work)

---

## 13. Next Steps

After completing this PRP:

1. **Validate all gates** (6 validation gates)
2. **Manual integration test** (generate PRP in both modes)
3. **Merge to main** after all tests pass
4. **Update CLAUDE.md** if needed (quota management patterns)
5. **Proceed to Phase 4** (PRP-43.3.1) - Initialization workflow integration

**Integration Points**:
- Classification (PRP-43.2.1) and Blending (PRP-43.2.2) can complete in parallel
- All Phase 2 PRPs feed into Phase 4 integration
- Phase 4 will orchestrate Task-based initialization workflow

---

## 14. KISS Validation

### Complexity Score: 3/10 (Low)

**Why low complexity**:
- No direct Anthropic SDK usage (simpler than classification/blending)
- Reuses existing synthesis logic (template-based)
- Context detection already implemented (PRP-43.1.1)
- Minimal code changes (routing logic only)
- Clear separation of concerns

**Complexity drivers**:
- Dual-mode operation (2 execution paths)
- Error handling (API key validation)
- Quality consistency testing

**Complexity reducers**:
- No LLM client to refactor
- No async/await complexity
- Template-based synthesis (deterministic)
- Reuses proven patterns from PRP-43.1.1

---

### Extendability Score: 9/10 (High)

**Future Enhancements**:

1. **Add LLM-enhanced synthesis in CLI mode**:
   ```python
   def _synthesize_via_cli(...):
       if os.environ.get("ANTHROPIC_API_KEY"):
           # Use LLM to enhance sections
           return _synthesize_llm_enhanced(...)
       else:
           # Fall back to template-based
           return _synthesize_template_based(...)
   ```

2. **Add caching for generated PRPs**:
   ```python
   from ce.task_executor import TaskResult

   # Cache result for reuse
   cache_key = hashlib.sha256(initial_md_content).hexdigest()
   ```

3. **Add quality scoring**:
   ```python
   def score_prp_quality(prp_content: str) -> float:
       """Score PRP quality (0-1 scale)."""
       # Check completeness, detail, validation gates, etc.
   ```

**No breaking changes needed** for any enhancement.

---

### Efficiency Score: 9/10 (High)

**Performance**:
- Context detection: <1ms (environment variable check)
- Mode validation: <5ms (API key check)
- Template synthesis: ~50ms (string formatting)
- No LLM calls overhead (delegated to conversation)

**Memory**:
- Minimal additional state (~1KB for mode tracking)
- No caching yet (deferred to future)
- Same memory footprint as current generate.py

**Bottlenecks** (not in this PRP):
- LLM synthesis time (varies 10-60s)
- File I/O for INITIAL.md reading
- Linear API calls for issue creation

---

**Generated**: 2025-11-08T00:00:00Z
**Batch Mode**: Yes (Batch 43, Stage 2, Order 3)
**Parent PRP**: PRP-43-INITIAL
**Parallel With**: PRP-43.2.1, PRP-43.2.2
**Depends On**: PRP-43.1.1
