---
prp_id: PRP-43.2.2
title: Blending Task Refactoring - Enable Max Quota for Content Blending
status: initial
created: "2025-11-08"
updated: "2025-11-08"
parent_prp: PRP-43-INITIAL
stage: 2
order: 2
estimated_hours: 10
complexity: high
tags: [blending, task-refactoring, llm-integration, quota-management, long-documents]
dependencies: [PRP-43.1.1]
---

# PRP-43.2.2: Blending Task Refactoring

## TL;DR

Refactor content blending logic from standalone CLI execution (requires ANTHROPIC_API_KEY, uses API quota) to Task-based execution (automatic Claude Max 5x quota). Maintain backward compatibility for CLI fallback while enabling quota-efficient blending operations for large documents.

**Impact**: Enables blending framework + target content (CLAUDE.md, memories, examples, settings) using 5x quota instead of expensive API quota.

**Complexity Drivers**:
- BlendingLLM used by 6 strategy files
- Must handle documents >100k tokens gracefully
- Dual-mode architecture (Task vs CLI)
- Quality preservation for large blends

## Problem Statement

### Current Limitations

**1. Quota Usage**
```python
# tools/ce/blending/llm_client.py line 76-80
self.client = Anthropic(
    api_key=self.api_key,  # Required
    timeout=timeout,
    max_retries=max_retries
)
# Uses API quota ❌ (expensive, limited)
```

**2. API Key Dependency**
- Blending requires ANTHROPIC_API_KEY environment variable
- Cannot leverage Claude Max's 5x quota
- User must manage separate API quota

**3. Large Document Challenges**
```python
# Current approach - single LLM call
response = self.client.messages.create(
    model="claude-sonnet-4",
    messages=[{
        "role": "user",
        "content": f"{framework_content}\n\n{target_content}"  # May exceed 200k tokens
    }]
)
# Risk: Context overflow, quality degradation
```

**4. Widespread Impact**
BlendingLLM is used by:
- `tools/ce/blending/strategies/claude_md.py` (CLAUDE.md blending)
- `tools/ce/blending/strategies/memories.py` (Memory blending)
- `tools/ce/blending/strategies/examples.py` (Example blending)
- `tools/ce/blending/strategies/settings.py` (Settings blending)
- `tools/ce/blending/strategies/commands.py` (Command blending)
- `tools/ce/blending/strategies/prps.py` (PRP blending)

All require API key, all use API quota.

### User Pain Points

**Initialization Flow**:
```bash
# Current (PRP-43.1.1 state)
npx syntropy-mcp init ce-framework

# Phase 4: Blending
# Uses API quota for each blend operation:
# - CLAUDE.md (framework 50k tokens + target 30k = 80k tokens)
# - Memories (framework 23 files + target 10 files = 150k tokens)
# - Examples (framework 8 files + target 5 files = 100k tokens)
# Total: ~330k tokens from API quota ❌
```

**Desired Flow**:
```bash
# After PRP-43.2.2
npx syntropy-mcp init ce-framework

# Phase 4: Blending
# Uses Claude Max 5x quota for all blends ✅
# Total: ~330k tokens from 5x quota (unlimited for practical purposes)
```

## Proposed Solution

### Architecture: Dual-Mode BlendingLLM

**Design Principle**: Automatic context detection with graceful fallback.

```python
class BlendingLLM:
    """LLM client for content blending - supports Task and CLI modes."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize LLM client with automatic mode detection.

        Mode Detection:
        1. Check if running inside Task context (TASK_ID env var)
        2. Task mode: Use Anthropic() without API key (Max quota)
        3. CLI mode: Require API key (API quota fallback)
        """
        self.mode = self._detect_mode()

        if self.mode == "task":
            # Task context - use Max quota
            self.client = Anthropic()
            logger.info("BlendingLLM initialized in Task mode (Max quota)")
        else:
            # CLI context - require API key
            if not api_key:
                raise ValueError(
                    "API key required for CLI mode. "
                    "Set ANTHROPIC_API_KEY or run within Task context."
                )
            self.client = Anthropic(api_key=api_key)
            logger.info("BlendingLLM initialized in CLI mode (API quota)")

    def _detect_mode(self) -> str:
        """Detect execution mode: 'task' or 'cli'."""
        return "task" if os.getenv("TASK_ID") else "cli"
```

### BlendingTask Wrapper

**Purpose**: Encapsulate blending operations as executable Tasks.

```python
# tools/ce/blending/blending_task.py (NEW)

class BlendingTask:
    """Execute content blending using Task-based LLM calls."""

    def __init__(self, executor: TaskExecutor):
        """
        Initialize blending task executor.

        Args:
            executor: TaskExecutor instance for running LLM tasks
        """
        self.executor = executor
        self.logger = logging.getLogger(__name__)

    def blend_content(
        self,
        framework_content: str,
        target_content: str,
        domain: str,
        blend_instructions: str
    ) -> str:
        """
        Blend framework and target content using Task (Max quota).

        Args:
            framework_content: Framework content (CE standard)
            target_content: Target project content (user-specific)
            domain: Content domain (claude_md, memories, examples, etc.)
            blend_instructions: Domain-specific blending rules

        Returns:
            Blended content as string

        Strategy:
            - Small documents (<50k tokens): Single Task
            - Large documents (>50k tokens): Chunked Tasks with merge step
        """
        # Estimate token count
        total_tokens = self._estimate_tokens(framework_content, target_content)

        if total_tokens < 50000:
            # Small document - single Task
            return self._blend_small(
                framework_content, target_content, domain, blend_instructions
            )
        else:
            # Large document - chunked strategy
            return self._blend_large(
                framework_content, target_content, domain, blend_instructions
            )

    def _blend_small(
        self, framework: str, target: str, domain: str, instructions: str
    ) -> str:
        """Blend small document in single Task."""
        task_prompt = self._build_blend_prompt(
            framework, target, domain, instructions
        )

        task_id = f"blend_{domain}_{int(time.time())}"
        result = self.executor.execute(
            task_id=task_id,
            task_type="content_blending",
            prompt=task_prompt,
            model="claude-sonnet-4"
        )

        return result.output

    def _blend_large(
        self, framework: str, target: str, domain: str, instructions: str
    ) -> str:
        """
        Blend large document using chunked strategy.

        Strategy:
            1. Split framework + target into logical chunks
            2. Blend each chunk pair in parallel Tasks
            3. Merge blended chunks in final Task
        """
        # Split into chunks (preserve logical boundaries)
        framework_chunks = self._chunk_content(framework, max_tokens=30000)
        target_chunks = self._chunk_content(target, max_tokens=30000)

        # Blend chunks in parallel
        blended_chunks = []
        for i, (fw_chunk, tgt_chunk) in enumerate(zip(framework_chunks, target_chunks)):
            task_id = f"blend_{domain}_chunk_{i}_{int(time.time())}"
            chunk_prompt = self._build_blend_prompt(
                fw_chunk, tgt_chunk, domain, instructions, chunk_index=i
            )

            result = self.executor.execute(
                task_id=task_id,
                task_type="content_blending_chunk",
                prompt=chunk_prompt,
                model="claude-sonnet-4"
            )
            blended_chunks.append(result.output)

        # Merge blended chunks
        merge_prompt = self._build_merge_prompt(blended_chunks, domain)
        merge_task_id = f"blend_{domain}_merge_{int(time.time())}"
        merge_result = self.executor.execute(
            task_id=merge_task_id,
            task_type="content_blending_merge",
            prompt=merge_prompt,
            model="claude-sonnet-4"
        )

        return merge_result.output

    def _build_blend_prompt(
        self,
        framework: str,
        target: str,
        domain: str,
        instructions: str,
        chunk_index: Optional[int] = None
    ) -> str:
        """Build LLM prompt for content blending."""
        chunk_info = f" (Chunk {chunk_index})" if chunk_index is not None else ""

        return f"""You are blending Context Engineering framework content with target project content.

**Domain**: {domain}{chunk_info}

**Task**: Merge framework and target content following these instructions:
{instructions}

**Framework Content**:
```
{framework}
```

**Target Content**:
```
{target}
```

**Output Requirements**:
1. Preserve all critical framework elements
2. Integrate target project specifics
3. Maintain consistent formatting
4. Remove duplicates, resolve conflicts
5. Output blended content only (no explanations)

**Blended Content**:
"""

    def _build_merge_prompt(self, chunks: List[str], domain: str) -> str:
        """Build LLM prompt for merging blended chunks."""
        chunks_text = "\n\n---CHUNK BOUNDARY---\n\n".join(
            f"CHUNK {i}:\n{chunk}" for i, chunk in enumerate(chunks)
        )

        return f"""You are merging blended content chunks for domain: {domain}

**Task**: Merge the following blended chunks into a single cohesive document.

**Requirements**:
1. Preserve logical flow across chunk boundaries
2. Remove duplicate sections introduced by chunking
3. Ensure consistent formatting throughout
4. Maintain all critical content from each chunk

**Chunks to Merge**:
{chunks_text}

**Merged Content**:
"""

    def _chunk_content(self, content: str, max_tokens: int) -> List[str]:
        """
        Split content into chunks preserving logical boundaries.

        Strategy:
            1. Split on section headers (##, ###, etc.)
            2. Group sections until approaching max_tokens
            3. Ensure no section spans chunks (preserve context)
        """
        # Split on markdown headers
        sections = re.split(r'(^#{1,6}\s+.+$)', content, flags=re.MULTILINE)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for section in sections:
            section_tokens = self._estimate_tokens(section)

            if current_tokens + section_tokens > max_tokens and current_chunk:
                # Finalize current chunk
                chunks.append("".join(current_chunk))
                current_chunk = [section]
                current_tokens = section_tokens
            else:
                current_chunk.append(section)
                current_tokens += section_tokens

        # Add final chunk
        if current_chunk:
            chunks.append("".join(current_chunk))

        return chunks

    def _estimate_tokens(self, *contents: str) -> int:
        """Estimate token count for content (rough heuristic: 4 chars/token)."""
        total_chars = sum(len(c) for c in contents)
        return total_chars // 4
```

### Strategy Integration

**Update Existing Strategies to Use BlendingTask**

```python
# tools/ce/blending/strategies/claude_md.py

class ClaudeMdBlendingStrategy:
    """Blend CLAUDE.md files from framework and target."""

    def __init__(self, blending_task: BlendingTask):
        """Initialize with BlendingTask (Task mode) or BlendingLLM (CLI mode)."""
        self.blending_task = blending_task

    def blend(
        self, framework_path: Path, target_path: Path, output_path: Path
    ) -> None:
        """Blend framework and target CLAUDE.md files."""
        framework_content = framework_path.read_text()
        target_content = target_path.read_text() if target_path.exists() else ""

        blend_instructions = """
CLAUDE.md Blending Rules:
1. Merge all sections, preserving framework structure
2. Append target-specific sections at appropriate locations
3. Resolve conflicts by preferring framework patterns
4. Maintain hierarchical header structure
5. Remove duplicate commands, consolidate similar sections
"""

        # Use Task-based blending (Max quota)
        blended_content = self.blending_task.blend_content(
            framework_content=framework_content,
            target_content=target_content,
            domain="claude_md",
            blend_instructions=blend_instructions
        )

        output_path.write_text(blended_content)
```

## Implementation Plan

### Phase 1: Core Infrastructure (3 hours)

**Step 1.1: Create BlendingTask Wrapper**
```bash
# Create new file
touch tools/ce/blending/blending_task.py

# Implement:
# - BlendingTask class
# - blend_content() method (small + large document support)
# - _build_blend_prompt() helper
# - _build_merge_prompt() helper
# - _chunk_content() helper
# - _estimate_tokens() helper
```

**Step 1.2: Add Mode Detection to BlendingLLM**
```python
# tools/ce/blending/llm_client.py

class BlendingLLM:
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with automatic mode detection."""
        self.mode = self._detect_mode()

        if self.mode == "task":
            self.client = Anthropic()  # No API key needed
        else:
            if not api_key:
                raise ValueError("API key required for CLI mode")
            self.client = Anthropic(api_key=api_key)

    def _detect_mode(self) -> str:
        """Detect if running in Task context."""
        return "task" if os.getenv("TASK_ID") else "cli"
```

**Validation**:
- [ ] BlendingTask instantiates correctly
- [ ] Mode detection works (Task vs CLI)
- [ ] Chunking preserves logical boundaries

### Phase 2: Strategy Integration (4 hours)

**Step 2.1: Update ClaudeMdBlendingStrategy**
```python
# tools/ce/blending/strategies/claude_md.py

class ClaudeMdBlendingStrategy:
    def __init__(self, blending_task: Optional[BlendingTask] = None):
        """Support both Task and CLI modes."""
        self.blending_task = blending_task  # Task mode
        self.blending_llm = None  # CLI mode (lazy init)

    def blend(self, framework_path: Path, target_path: Path, output_path: Path):
        if self.blending_task:
            # Task mode - use BlendingTask
            blended = self.blending_task.blend_content(...)
        else:
            # CLI mode - use BlendingLLM
            if not self.blending_llm:
                self.blending_llm = BlendingLLM(api_key=os.getenv("ANTHROPIC_API_KEY"))
            blended = self.blending_llm.blend_content(...)
```

**Step 2.2: Update Remaining Strategies**
Apply same pattern to:
- `memories.py`
- `examples.py`
- `settings.py`
- `commands.py`
- `prps.py`

**Validation**:
- [ ] Each strategy supports dual mode
- [ ] Task mode uses BlendingTask (Max quota)
- [ ] CLI mode uses BlendingLLM (API quota)

### Phase 3: Testing (2 hours)

**Step 3.1: Unit Tests for BlendingTask**
```python
# tools/tests/ce/blending/test_blending_task.py (NEW)

class TestBlendingTask:
    def test_blend_small_document(self, mock_executor):
        """Test blending small document (<50k tokens)."""
        task = BlendingTask(executor=mock_executor)

        result = task.blend_content(
            framework_content="# Framework\n\nContent",
            target_content="# Target\n\nContent",
            domain="claude_md",
            blend_instructions="Merge sections"
        )

        assert result is not None
        assert mock_executor.execute.call_count == 1  # Single Task

    def test_blend_large_document(self, mock_executor):
        """Test blending large document (>50k tokens)."""
        task = BlendingTask(executor=mock_executor)

        # Create large content (>50k tokens)
        large_framework = "# Section\n\n" + ("Content " * 15000)
        large_target = "# Section\n\n" + ("Content " * 15000)

        result = task.blend_content(
            framework_content=large_framework,
            target_content=large_target,
            domain="memories",
            blend_instructions="Merge files"
        )

        assert result is not None
        # Multiple Tasks: N chunks + 1 merge
        assert mock_executor.execute.call_count > 1

    def test_chunking_preserves_sections(self):
        """Test that chunking doesn't split sections."""
        task = BlendingTask(executor=Mock())

        content = """
## Section 1

Content for section 1.

## Section 2

Content for section 2.

## Section 3

Content for section 3.
"""
        chunks = task._chunk_content(content, max_tokens=100)

        # Each chunk should contain complete sections
        for chunk in chunks:
            assert chunk.count("##") > 0  # Has at least one header
            assert not chunk.startswith("Content")  # Doesn't start mid-section
```

**Step 3.2: Integration Tests for Strategies**
```python
# tools/tests/ce/blending/strategies/test_claude_md_task.py (NEW)

class TestClaudeMdBlendingStrategyTask:
    def test_blend_with_task(self, tmp_path, mock_task_executor):
        """Test CLAUDE.md blending using Task mode."""
        # Set up Task context
        os.environ["TASK_ID"] = "test_blend_123"

        blending_task = BlendingTask(executor=mock_task_executor)
        strategy = ClaudeMdBlendingStrategy(blending_task=blending_task)

        framework_file = tmp_path / "framework_CLAUDE.md"
        target_file = tmp_path / "target_CLAUDE.md"
        output_file = tmp_path / "blended_CLAUDE.md"

        framework_file.write_text("# Framework\n\nContent")
        target_file.write_text("# Target\n\nContent")

        # Blend using Task (Max quota)
        strategy.blend(framework_file, target_file, output_file)

        assert output_file.exists()
        assert mock_task_executor.execute.called

        # Cleanup
        del os.environ["TASK_ID"]
```

**Validation**:
- [ ] Unit tests pass for small documents
- [ ] Unit tests pass for large documents
- [ ] Chunking tests verify section preservation
- [ ] Integration tests verify Task mode works
- [ ] Integration tests verify CLI mode works

### Phase 4: Backward Compatibility (1 hour)

**Step 4.1: Verify CLI Mode**
```bash
# Test existing CLI workflow (should still work)
cd tools
export ANTHROPIC_API_KEY=sk-ant-...
uv run ce blend --framework framework_CLAUDE.md --target target_CLAUDE.md --output blended_CLAUDE.md

# Should use BlendingLLM in CLI mode (API quota)
```

**Step 4.2: Update Documentation**
```markdown
# tools/ce/blending/README.md

## Usage

### Task Mode (Recommended - Uses Max Quota)
```python
from ce.blending.blending_task import BlendingTask
from ce.task_executor import TaskExecutor

executor = TaskExecutor()
blending_task = BlendingTask(executor)

blended = blending_task.blend_content(
    framework_content=framework,
    target_content=target,
    domain="claude_md",
    blend_instructions="..."
)
```

### CLI Mode (Fallback - Uses API Quota)
```bash
export ANTHROPIC_API_KEY=sk-ant-...
cd tools
uv run ce blend --framework ... --target ... --output ...
```
```

**Validation**:
- [ ] CLI mode still works with API key
- [ ] CLI mode raises error without API key
- [ ] Task mode works without API key
- [ ] Documentation updated

## Testing Strategy

### Unit Tests

**File**: `tools/tests/ce/blending/test_blending_task.py`

**Coverage**:
- `test_blend_small_document` - Single Task execution
- `test_blend_large_document` - Chunked Task execution
- `test_chunking_preserves_sections` - Section boundary preservation
- `test_estimate_tokens` - Token estimation accuracy
- `test_build_blend_prompt` - Prompt formatting
- `test_build_merge_prompt` - Merge prompt formatting

**File**: `tools/tests/ce/blending/test_llm_client.py` (UPDATE)

**New Coverage**:
- `test_mode_detection_task` - Detects Task context
- `test_mode_detection_cli` - Detects CLI context
- `test_init_task_mode` - Initializes without API key
- `test_init_cli_mode_with_key` - Initializes with API key
- `test_init_cli_mode_without_key` - Raises error without key

### Integration Tests

**File**: `tools/tests/ce/blending/strategies/test_claude_md_task.py`

**Coverage**:
- `test_blend_with_task` - CLAUDE.md blending in Task mode
- `test_blend_with_cli` - CLAUDE.md blending in CLI mode
- `test_blend_large_claude_md` - Large CLAUDE.md (>100k tokens)

**File**: `tools/tests/ce/blending/strategies/test_memories_task.py`

**Coverage**:
- `test_blend_memories_with_task` - Memory blending in Task mode
- `test_blend_many_memories` - 23 framework + 10 target memories

### End-to-End Tests

**Scenario 1: Framework Initialization (Task Mode)**
```python
# Simulate npx syntropy-mcp init ce-framework
# Phase 4: Blending

def test_full_blending_task_mode(tmp_path):
    """Test full blending flow using Task mode."""
    # Set Task context
    os.environ["TASK_ID"] = "init_blending_123"

    executor = TaskExecutor()
    blending_task = BlendingTask(executor)

    # Blend CLAUDE.md
    claude_md_strategy = ClaudeMdBlendingStrategy(blending_task)
    claude_md_strategy.blend(...)

    # Blend memories
    memories_strategy = MemoriesBlendingStrategy(blending_task)
    memories_strategy.blend(...)

    # Verify Max quota usage (no API key needed)
    assert "ANTHROPIC_API_KEY" not in os.environ

    # Cleanup
    del os.environ["TASK_ID"]
```

**Scenario 2: CLI Fallback (API Mode)**
```bash
# Test standalone blending tool
export ANTHROPIC_API_KEY=sk-ant-...
cd tools
uv run ce blend --framework framework.md --target target.md --output blended.md

# Should work with API quota
```

## Validation Gates

### Functional Validation

- [ ] **Task Mode Blending Works**
  - BlendingTask executes without API key
  - Uses Claude Max 5x quota
  - Produces valid blended content

- [ ] **CLI Mode Blending Works**
  - BlendingLLM executes with API key
  - Uses API quota
  - Produces identical blended content

- [ ] **Large Document Blending**
  - Handles documents >100k tokens
  - Chunking preserves section boundaries
  - Merge step produces cohesive output

- [ ] **Dual Mode Support**
  - All 6 strategies support Task mode
  - All 6 strategies support CLI mode
  - Mode detection automatic (no user config)

### Quality Validation

- [ ] **Test Coverage**
  - Unit tests: ≥90% coverage for blending_task.py
  - Integration tests: All 6 strategies tested
  - E2E tests: Full initialization flow tested

- [ ] **Performance Validation**
  - Small documents (<50k tokens): <30s
  - Large documents (>100k tokens): <2min
  - Chunked blending: Parallel Task execution

- [ ] **Backward Compatibility**
  - Existing CLI commands work unchanged
  - API key fallback works correctly
  - Error messages guide users to Task mode

### Security Validation

- [ ] **API Key Handling**
  - Task mode never requires API key
  - CLI mode validates API key presence
  - No API key leakage in logs/errors

- [ ] **Quota Management**
  - Task mode uses TASK_ID for tracking
  - CLI mode uses API quota correctly
  - No quota mixing between modes

## Risks & Mitigations

### Risk 1: Large Document Quality Degradation

**Risk**: Chunked blending may lose context across boundaries, producing lower quality output.

**Probability**: Medium
**Impact**: High

**Mitigation**:
1. **Smart Chunking**: Split on logical boundaries (headers, sections)
2. **Overlap Strategy**: Include 10% overlap between chunks
3. **Merge Validation**: LLM-based quality check on merged output
4. **Fallback**: If merge quality low, retry with larger chunks

**Implementation**:
```python
def _chunk_content(self, content: str, max_tokens: int, overlap: int = 0.1):
    """Chunk with overlap to preserve context."""
    # ...
    overlap_tokens = int(max_tokens * overlap)
    # Include overlap_tokens from previous chunk
```

### Risk 2: Task Executor Integration Complexity

**Risk**: BlendingTask depends on TaskExecutor (PRP-43.1.1), which may have bugs or incomplete implementation.

**Probability**: Low
**Impact**: High

**Mitigation**:
1. **Mock Testing**: Extensive mocking of TaskExecutor in unit tests
2. **Fallback**: CLI mode always available as backup
3. **Early Integration**: Test BlendingTask with real TaskExecutor ASAP
4. **Dependency Validation**: Verify PRP-43.1.1 complete before starting

**Validation**:
```python
# Early integration test
def test_task_executor_integration():
    """Verify TaskExecutor works with BlendingTask."""
    executor = TaskExecutor()  # Real instance
    task = BlendingTask(executor)

    result = task.blend_content(...)
    assert result is not None
```

### Risk 3: Mode Detection False Positives

**Risk**: TASK_ID environment variable may be set accidentally, causing unintended Task mode usage.

**Probability**: Low
**Impact**: Medium

**Mitigation**:
1. **Explicit Override**: Add `force_mode` parameter to BlendingLLM
2. **Logging**: Log mode detection decision clearly
3. **Validation**: Warn if TASK_ID set but Task context not available

**Implementation**:
```python
def __init__(self, api_key: Optional[str] = None, force_mode: Optional[str] = None):
    """Initialize with optional mode override."""
    self.mode = force_mode or self._detect_mode()

    if self.mode == "task" and not os.getenv("TASK_ID"):
        logger.warning("Task mode forced but TASK_ID not set - may fail")
```

### Risk 4: Strategy Refactoring Breaking Changes

**Risk**: Updating 6 strategy files simultaneously increases risk of introducing bugs.

**Probability**: Medium
**Impact**: Medium

**Mitigation**:
1. **Incremental Rollout**: Update one strategy at a time, test, commit
2. **Comprehensive Testing**: Integration tests for each strategy
3. **Backward Compatibility**: Maintain CLI mode as fallback
4. **Rollback Plan**: Git revert if issues found

**Rollout Order**:
1. `claude_md.py` (simplest, single file)
2. `settings.py` (JSON blending, well-defined)
3. `commands.py` (similar to settings)
4. `examples.py` (file tree blending)
5. `memories.py` (multi-file blending)
6. `prps.py` (most complex, YAML + content)

## Success Criteria

### Primary Criteria

1. **Quota Efficiency**
   - Framework initialization blending uses 0 API quota
   - All blending operations route through Max quota
   - No user-reported API quota exhaustion

2. **Quality Preservation**
   - Blended content quality matches pre-refactoring baseline
   - Large document blending (>100k tokens) produces coherent output
   - No section loss or corruption in chunked blending

3. **Backward Compatibility**
   - All existing CLI commands work unchanged
   - API key fallback works for users without Max access
   - No breaking changes to strategy interfaces

### Secondary Criteria

4. **Performance**
   - Small document blending: <30s (unchanged from baseline)
   - Large document blending: <2min (new capability)
   - Chunked blending uses parallel Tasks (5x speedup potential)

5. **Developer Experience**
   - Strategy code simplified (BlendingTask abstraction)
   - Clear documentation for Task vs CLI modes
   - Easy migration path for new strategies

6. **Test Coverage**
   - Unit test coverage ≥90% for new code
   - Integration tests cover all 6 strategies
   - E2E test validates full initialization flow

## Related PRPs

**Dependencies**:
- **PRP-43.1.1**: Task Executor Framework (MUST complete first)
  - Provides TaskExecutor class
  - Provides Task execution infrastructure
  - Provides TASK_ID context management

**Parallel PRPs** (Stage 2):
- **PRP-43.2.1**: Classification Task Refactoring
  - Similar dual-mode architecture
  - Shared testing patterns
  - Coordinate merge order to avoid conflicts

**Downstream PRPs** (Stage 3):
- **PRP-43.3.1**: CLI Command Migration
  - Will use BlendingTask for `ce blend` command
  - Will benefit from dual-mode support

**Parent PRP**:
- **PRP-43-INITIAL**: Task-Based Quota Management (Overall strategy)

## Implementation Checklist

### Phase 1: Core Infrastructure
- [ ] Create `tools/ce/blending/blending_task.py`
- [ ] Implement `BlendingTask` class
- [ ] Implement `blend_content()` with small/large document support
- [ ] Implement `_chunk_content()` with section preservation
- [ ] Implement `_build_blend_prompt()`
- [ ] Implement `_build_merge_prompt()`
- [ ] Add mode detection to `BlendingLLM.__init__()`
- [ ] Test mode detection (Task vs CLI)

### Phase 2: Strategy Integration
- [ ] Update `claude_md.py` for dual mode
- [ ] Update `settings.py` for dual mode
- [ ] Update `commands.py` for dual mode
- [ ] Update `examples.py` for dual mode
- [ ] Update `memories.py` for dual mode
- [ ] Update `prps.py` for dual mode
- [ ] Test each strategy in Task mode
- [ ] Test each strategy in CLI mode

### Phase 3: Testing
- [ ] Create `test_blending_task.py`
- [ ] Write unit tests for small documents
- [ ] Write unit tests for large documents
- [ ] Write unit tests for chunking
- [ ] Update `test_llm_client.py` for mode detection
- [ ] Write integration tests for strategies
- [ ] Write E2E test for initialization flow

### Phase 4: Validation
- [ ] Run all tests: `pytest tools/tests/ce/blending/ -v`
- [ ] Test Task mode with real TaskExecutor
- [ ] Test CLI mode with API key
- [ ] Test large document blending (>100k tokens)
- [ ] Verify quota usage (Max vs API)
- [ ] Update documentation

### Final Checklist
- [ ] All validation gates passed
- [ ] Test coverage ≥90%
- [ ] Documentation updated
- [ ] Git commit with clear message
- [ ] Ready for PRP-43.3.1 (CLI migration)
