---
prp_id: PRP-34.3.1
feature_name: CLAUDE.md Blending Strategy
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
complexity: high
estimated_hours: 3.0
dependencies: [PRP-34.2.6]
batch_id: 34
stage: stage-3-parallel
execution_order: 8
merge_order: 8
conflict_potential: NONE
worktree_path: ../ctx-eng-plus-prp-34-3-1
branch_name: prp-34-3-1-claude-md-strategy
issue: TBD
---

# PRP-34.3.1: CLAUDE.md Blending Strategy

## 1. TL;DR

**Objective**: Implement natural language-based CLAUDE.md section merging using Sonnet for quality, copy framework sections + import target [PROJECT] sections, RULES.md-aware

**What**: Create `ClaudeMdBlendStrategy` class that parses CLAUDE.md into H2 sections, uses BlendingLLM (Sonnet) to intelligently merge framework and target project documentation, respecting RULES.md as invariants, and outputs formatted markdown with lists/tables/mermaid where appropriate.

**Why**: CLAUDE.md is the primary project documentation file - high-quality blending is critical. Haiku lacks the sophistication to understand framework philosophy, preserve documentation tone, and handle complex section merging. Sonnet provides the quality needed for this authoritative document.

**Effort**: 3.0 hours

**Dependencies**: PRP-34.2.6 (LLM Client Integration) - requires BlendingLLM with Sonnet support

**Files Modified**:
- `tools/ce/blending/strategies/claude_md.py` (new)
- `tools/tests/test_blend_claude_md.py` (new)

## 2. Context

### Background

PRP-34.1.1 established the core blending framework with strategy pattern. PRP-34.2.6 added BlendingLLM with Haiku + Sonnet hybrid support. PRP-34.3.1 implements the first NL-based strategy for CLAUDE.md blending.

**Current State**:
- Core blending framework exists (strategies, orchestrator, validation)
- BlendingLLM provides blend_content() method with Sonnet model
- INITIALIZATION.md documents manual CLAUDE.md blending (Phase 4)
- Manual process requires human judgment for section merging

**Target State**:
- `ClaudeMdBlendStrategy` class extending BlendStrategy protocol
- Automatic H2 section parsing and identification
- Sonnet-based intelligent blending with RULES.md context
- Framework sections preserved (authoritative)
- Target [PROJECT] sections imported where non-contradictory
- Output formatted with proper markdown (lists, tables, mermaid)

**CLAUDE.md Philosophy**: Framework documentation is authoritative. Target project customizations (project-specific commands, paths, team info) preserved. Contradictions resolved in favor of framework with explanation comments.

### CLAUDE.md Structure

Typical sections (H2 level):
- `## Core Principles` - Framework principles (authoritative)
- `## Quick Commands` - Standard commands + project customizations
- `## Framework Initialization` - CE setup instructions (authoritative)
- `## Working Directory` - Project-specific paths
- `## Hooks` - Framework hooks (authoritative)
- `## Tool Naming Convention` - Framework conventions (authoritative)
- `## Allowed Tools Summary` - Framework tools + project additions
- `## Command Permissions` - Framework + project commands
- `## Quick Tool Selection` - Framework guidance (authoritative)
- `## Project Structure` - Project-specific structure
- `## Testing Standards` - Framework standards + project specifics
- `## Code Quality` - Framework standards (authoritative)
- `## Context Commands` - Framework commands (authoritative)
- `## Syntropy MCP Tool Sync` - Framework feature (authoritative)
- `## Linear Integration` - Project-specific config
- `## Batch PRP Generation` - Framework feature (authoritative)
- `## PRP Sizing` - Framework feature (authoritative)
- `## Testing Patterns` - Framework patterns (authoritative)
- `## Documentation Standards` - Framework standards (authoritative)
- `## Efficient Doc Review` - Framework guidance (authoritative)
- `## Resources` - Framework + project paths
- `## Keyboard Shortcuts` - Framework + project shortcuts
- `## Git Worktree` - Framework feature (authoritative)
- `## Troubleshooting` - Framework + project issues

**Categorization**:
- **Framework (authoritative)**: Core Principles, Framework Initialization, Tool conventions, Testing Standards, Code Quality, Context Commands, Batch PRP, Testing Patterns, Doc Standards, Git Worktree
- **Hybrid (merge)**: Quick Commands, Allowed Tools, Command Permissions, Resources, Troubleshooting
- **Project-specific (preserve)**: Working Directory, Project Structure, Linear Integration, Keyboard Shortcuts (project-specific ones)

### Blending Algorithm

**Step 1: Parse Sections** (Python)
```python
def parse_sections(content: str) -> Dict[str, str]:
    """
    Split CLAUDE.md into H2 sections.

    Returns:
        {"section_name": "section_content"}
    """
    sections = {}
    current_section = None
    current_lines = []

    for line in content.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_lines)
            current_section = line[3:].strip()
            current_lines = [line]
        else:
            current_lines.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_lines)

    return sections
```

**Step 2: Categorize Sections** (Python)
```python
FRAMEWORK_SECTIONS = {
    "Core Principles", "Framework Initialization", "Tool Naming Convention",
    "Testing Standards", "Code Quality", "Context Commands",
    "Batch PRP Generation", "PRP Sizing", "Testing Patterns",
    "Documentation Standards", "Efficient Doc Review", "Git Worktree"
}

HYBRID_SECTIONS = {
    "Quick Commands", "Allowed Tools Summary", "Command Permissions",
    "Resources", "Troubleshooting"
}

PROJECT_SECTIONS = {
    "Working Directory", "Project Structure", "Linear Integration"
}
```

**Step 3: Blend Sections** (Sonnet)
```python
def blend(self, framework_content: str, target_content: str, context: dict) -> str:
    """
    Blend framework and target CLAUDE.md files.

    Algorithm:
    1. Parse both into H2 sections
    2. Framework sections → Copy as-is (authoritative)
    3. Hybrid sections → Sonnet merge (framework + target)
    4. Target-only sections → Import if not contradictory
    5. Reassemble in logical order
    """
    # Get LLM client from context
    llm = context.get("llm_client")
    rules = context.get("rules_content", "")

    # Parse sections
    framework_sections = self.parse_sections(framework_content)
    target_sections = self.parse_sections(target_content)

    blended_sections = {}

    # 1. Framework sections - copy as-is
    for section_name in FRAMEWORK_SECTIONS:
        if section_name in framework_sections:
            blended_sections[section_name] = framework_sections[section_name]

    # 2. Hybrid sections - Sonnet merge
    for section_name in HYBRID_SECTIONS:
        if section_name in framework_sections:
            target_section = target_sections.get(section_name, "")
            result = llm.blend_content(
                framework_content=framework_sections[section_name],
                target_content=target_section,
                rules_content=rules,
                domain=f"claude_md_{section_name}"
            )
            blended_sections[section_name] = result["blended"]

    # 3. Target-only sections - import if non-contradictory
    for section_name in target_sections:
        if section_name not in framework_sections:
            # Use Sonnet to check if contradicts RULES.md
            result = llm.blend_content(
                framework_content=rules,
                target_content=target_sections[section_name],
                domain=f"validate_{section_name}"
            )
            if result["confidence"] > 0.7:
                blended_sections[section_name] = target_sections[section_name]

    # 4. Reassemble in logical order
    return self._reassemble_sections(blended_sections)
```

**Step 4: Validate Output** (Python)
```python
def validate(self, blended_content: str) -> bool:
    """
    Validate blended CLAUDE.md.

    Checks:
    1. Valid markdown syntax
    2. Contains required framework sections
    3. No duplicate H2 sections
    """
    sections = self.parse_sections(blended_content)

    # Check required framework sections present
    required = {"Core Principles", "Framework Initialization", "Testing Standards"}
    missing = required - set(sections.keys())
    if missing:
        raise ValueError(f"Missing required sections: {missing}")

    # Check no duplicates
    section_names = [s.strip() for s in blended_content.split('\n') if s.startswith('## ')]
    duplicates = [s for s in section_names if section_names.count(s) > 1]
    if duplicates:
        raise ValueError(f"Duplicate sections: {set(duplicates)}")

    return True
```

### Constraints and Considerations

1. **Sonnet Quality**: Use Sonnet (not Haiku) for high-quality documentation blending
2. **RULES.md Context**: Pass RULES.md content to LLM as invariants (framework law)
3. **Section Ordering**: Preserve logical flow (principles → commands → tools → troubleshooting)
4. **Markdown Formatting**: Sonnet should format with lists, tables, mermaid where appropriate
5. **Token Costs**: CLAUDE.md is ~15k tokens → Sonnet costs ~$0.50 per blend (acceptable for quality)
6. **Error Handling**: Fast failure with actionable troubleshooting (no silent corruption)
7. **Testing**: Mock LLM responses for unit tests (real API integration tests optional)
8. **Function Limits**: Target 50 lines max per function (KISS principle)
9. **No Fishy Fallbacks**: Exceptions bubble up with troubleshooting messages
10. **Real Functionality**: Actual LLM calls, no hardcoded success messages

### Documentation References

**Internal**:
- PRP-34 INITIAL: Complete blending system vision
- PRP-34.1.1: Core framework (BlendStrategy protocol)
- PRP-34.2.6: BlendingLLM (Sonnet integration)
- INITIALIZATION.md: Manual CLAUDE.md blending (Phase 4)
- CLAUDE.md: This file (framework documentation)

**External**:
- Markdown specification: https://spec.commonmark.org/
- Mermaid diagrams: https://mermaid.js.org/
- Anthropic Sonnet: https://docs.anthropic.com/claude/docs/models-overview

## 3. Implementation Steps

### Phase 1: ClaudeMdBlendStrategy Class Structure (30 min)

**Goal**: Create strategy class with section parsing and categorization

**File**: `tools/ce/blending/strategies/claude_md.py`

**Implementation**:

```python
"""CLAUDE.md blending strategy with Sonnet-based section merging.

Philosophy: Copy framework sections (authoritative) + import target [PROJECT]
sections where non-contradictory. RULES.md enforced as invariants.
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Section categories
FRAMEWORK_SECTIONS = {
    "Core Principles", "Framework Initialization", "Tool Naming Convention",
    "Testing Standards", "Code Quality", "Context Commands",
    "Batch PRP Generation", "PRP Sizing", "Testing Patterns",
    "Documentation Standards", "Efficient Doc Review", "Git Worktree"
}

HYBRID_SECTIONS = {
    "Quick Commands", "Allowed Tools Summary", "Command Permissions",
    "Resources", "Troubleshooting"
}


class ClaudeMdBlendStrategy:
    """
    Blend framework and target CLAUDE.md files with Sonnet-based merging.

    Uses H2 section parsing to categorize content:
    - Framework sections: Copied as-is (authoritative)
    - Hybrid sections: Sonnet merge (framework + target)
    - Target-only sections: Imported if non-contradictory

    Usage:
        >>> strategy = ClaudeMdBlendStrategy()
        >>> blended = strategy.blend(framework_md, target_md, context)
    """

    def can_handle(self, domain: str) -> bool:
        """
        Return True for 'claude_md' domain.

        Args:
            domain: Domain identifier (e.g., 'claude_md', 'settings', 'commands')

        Returns:
            True if domain == 'claude_md', False otherwise
        """
        return domain == "claude_md"

    def parse_sections(self, content: str) -> Dict[str, str]:
        """
        Split CLAUDE.md into H2 sections.

        Args:
            content: CLAUDE.md file content

        Returns:
            Dict mapping section names to section content (including H2 header)
        """
        if not content.strip():
            return {}

        sections = {}
        current_section = None
        current_lines = []

        for line in content.split('\n'):
            if line.startswith('## '):
                # Save previous section
                if current_section:
                    sections[current_section] = '\n'.join(current_lines).strip()

                # Start new section
                current_section = line[3:].strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        # Save last section
        if current_section:
            sections[current_section] = '\n'.join(current_lines).strip()

        return sections

    def categorize_section(self, section_name: str) -> str:
        """
        Categorize section as framework, hybrid, or project.

        Args:
            section_name: Section name (from H2 header)

        Returns:
            "framework", "hybrid", or "project"
        """
        if section_name in FRAMEWORK_SECTIONS:
            return "framework"
        elif section_name in HYBRID_SECTIONS:
            return "hybrid"
        else:
            return "project"
```

**Validation**:
```bash
# Check file created
ls -lh /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/strategies/claude_md.py
# Expected: File exists, ~50 lines so far
```

### Phase 2: blend() Method Implementation (45 min)

**Goal**: Implement core blending logic with Sonnet integration

**Add to `claude_md.py`**:

```python
    def blend(
        self,
        framework_content: str,
        target_content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Blend framework and target CLAUDE.md files.

        Algorithm:
        1. Parse both into H2 sections
        2. Framework sections → Copy as-is (authoritative)
        3. Hybrid sections → Sonnet merge (framework + target)
        4. Target-only sections → Import if non-contradictory
        5. Reassemble in logical order

        Args:
            framework_content: Framework CLAUDE.md content
            target_content: Target project CLAUDE.md content (may be empty)
            context: Dict with llm_client and optional rules_content

        Returns:
            Blended CLAUDE.md content

        Raises:
            ValueError: If LLM client not provided or blending fails
        """
        if not context or "llm_client" not in context:
            raise ValueError(
                "LLM client required in context\n"
                "🔧 Troubleshooting:\n"
                "  1. Pass context={'llm_client': BlendingLLM()} to blend()\n"
                "  2. See PRP-34.2.6 for BlendingLLM setup"
            )

        llm = context["llm_client"]
        rules = context.get("rules_content", "")

        logger.info("Blending CLAUDE.md with Sonnet...")

        # Parse sections
        framework_sections = self.parse_sections(framework_content)
        target_sections = self.parse_sections(target_content) if target_content.strip() else {}

        blended_sections = {}

        # 1. Framework sections - copy as-is (authoritative)
        for section_name in FRAMEWORK_SECTIONS:
            if section_name in framework_sections:
                blended_sections[section_name] = framework_sections[section_name]
                logger.debug(f"  Framework section: {section_name} (copied)")

        # 2. Hybrid sections - Sonnet merge
        for section_name in HYBRID_SECTIONS:
            if section_name in framework_sections:
                target_section = target_sections.get(section_name, "")

                # Build merge prompt
                logger.debug(f"  Hybrid section: {section_name} (merging)")
                result = llm.blend_content(
                    framework_content=framework_sections[section_name],
                    target_content=target_section,
                    rules_content=rules,
                    domain=f"claude_md_{section_name.replace(' ', '_').lower()}"
                )

                blended_sections[section_name] = result["blended"]

        # 3. Target-only sections - import if project-specific
        for section_name in target_sections:
            if section_name not in framework_sections:
                category = self.categorize_section(section_name)

                if category == "project":
                    # Project-specific section - import as-is
                    blended_sections[section_name] = target_sections[section_name]
                    logger.debug(f"  Target section: {section_name} (imported)")
                else:
                    # Unknown section - validate with Sonnet
                    logger.debug(f"  Target section: {section_name} (validating)")
                    result = llm.blend_content(
                        framework_content=rules if rules else "# Framework Rules\n\nNo rules provided.",
                        target_content=target_sections[section_name],
                        domain=f"validate_{section_name.replace(' ', '_').lower()}"
                    )

                    # Import if high confidence (non-contradictory)
                    if result["confidence"] > 0.7:
                        blended_sections[section_name] = target_sections[section_name]
                        logger.debug(f"    → Imported (confidence: {result['confidence']:.2f})")
                    else:
                        logger.warning(f"    → Skipped (confidence: {result['confidence']:.2f})")

        # 4. Reassemble in logical order
        return self._reassemble_sections(blended_sections, framework_sections)

    def _reassemble_sections(
        self,
        blended_sections: Dict[str, str],
        framework_sections: Dict[str, str]
    ) -> str:
        """
        Reassemble sections in logical order.

        Order:
        1. Framework sections (in original order)
        2. Hybrid sections (in original order)
        3. Project sections (alphabetical)

        Args:
            blended_sections: Dict of section_name → blended_content
            framework_sections: Original framework sections (for ordering)

        Returns:
            Reassembled CLAUDE.md content
        """
        output_lines = []

        # Get framework section order
        framework_order = list(framework_sections.keys())

        # Add sections in order
        for section_name in framework_order:
            if section_name in blended_sections:
                output_lines.append(blended_sections[section_name])
                output_lines.append("")  # Blank line between sections

        # Add remaining sections (alphabetically)
        remaining = sorted(set(blended_sections.keys()) - set(framework_order))
        for section_name in remaining:
            output_lines.append(blended_sections[section_name])
            output_lines.append("")

        # Remove trailing blank lines
        while output_lines and not output_lines[-1].strip():
            output_lines.pop()

        return '\n'.join(output_lines)
```

**Validation**:
```bash
# Check method signature correct
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
python3 -c "from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy; s = ClaudeMdBlendStrategy(); print(s.blend.__doc__)"
```

### Phase 3: validate() Method Implementation (15 min)

**Goal**: Implement validation for blended output

**Add to `claude_md.py`**:

```python
    def validate(self, blended_content: str) -> bool:
        """
        Validate blended CLAUDE.md.

        Checks:
        1. Valid markdown (has H2 sections)
        2. Contains required framework sections
        3. No duplicate H2 section names

        Args:
            blended_content: Blended CLAUDE.md content

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        if not blended_content.strip():
            raise ValueError("Blended content is empty")

        # Parse sections
        sections = self.parse_sections(blended_content)

        if not sections:
            raise ValueError("No H2 sections found in blended content")

        # Check required framework sections present
        required = {"Core Principles", "Framework Initialization", "Testing Standards"}
        missing = required - set(sections.keys())
        if missing:
            raise ValueError(
                f"Missing required framework sections: {missing}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check framework CLAUDE.md has these sections\n"
                f"  2. Verify blend() preserves framework sections"
            )

        # Check no duplicate section names
        section_names = [
            line[3:].strip()
            for line in blended_content.split('\n')
            if line.startswith('## ')
        ]

        duplicates = [s for s in section_names if section_names.count(s) > 1]
        if duplicates:
            raise ValueError(
                f"Duplicate H2 sections found: {set(duplicates)}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check target CLAUDE.md for duplicate sections\n"
                f"  2. Verify blend() deduplicates correctly"
            )

        logger.info(f"✓ Validated CLAUDE.md ({len(sections)} sections)")
        return True
```

**Validation**:
```bash
# Check validation logic
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
python3 -c "from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy; s = ClaudeMdBlendStrategy(); s.validate('## Core Principles\nTest\n## Framework Initialization\nTest\n## Testing Standards\nTest')"
```

### Phase 4: Unit Tests with Mock LLM (1 hour)

**Goal**: Create comprehensive tests with mocked LLM responses

**File**: `tools/tests/test_blend_claude_md.py`

**Implementation**:

```python
"""Tests for ClaudeMdBlendStrategy.

Tests section parsing, categorization, blending logic, and validation.
Uses mock LLM responses for fast, deterministic tests.
"""

import pytest
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy


class MockLLM:
    """Mock BlendingLLM for testing."""

    def blend_content(self, framework_content, target_content, rules_content=None, domain="unknown"):
        """Mock blend_content that returns simple merge."""
        # Simple mock: append target to framework
        blended = framework_content
        if target_content and target_content.strip():
            blended += f"\n\n<!-- Target additions -->\n{target_content}"

        return {
            "blended": blended,
            "model": "mock-sonnet",
            "tokens": {"input": 100, "output": 50},
            "confidence": 0.95
        }


def test_can_handle_claude_md_domain():
    """Test can_handle() returns True for 'claude_md' domain."""
    strategy = ClaudeMdBlendStrategy()
    assert strategy.can_handle("claude_md") is True
    assert strategy.can_handle("settings") is False
    assert strategy.can_handle("commands") is False


def test_parse_sections_splits_by_h2():
    """Test parse_sections() splits content by H2 headers."""
    strategy = ClaudeMdBlendStrategy()

    content = """# CLAUDE.md

## Core Principles

Principle 1
Principle 2

## Testing Standards

Standard 1
Standard 2

## Project Structure

Structure info
"""

    sections = strategy.parse_sections(content)

    assert len(sections) == 3
    assert "Core Principles" in sections
    assert "Testing Standards" in sections
    assert "Project Structure" in sections
    assert "Principle 1" in sections["Core Principles"]


def test_parse_sections_empty_content():
    """Test parse_sections() handles empty content."""
    strategy = ClaudeMdBlendStrategy()

    sections = strategy.parse_sections("")
    assert sections == {}

    sections = strategy.parse_sections("   ")
    assert sections == {}


def test_categorize_section_framework():
    """Test categorize_section() identifies framework sections."""
    strategy = ClaudeMdBlendStrategy()

    assert strategy.categorize_section("Core Principles") == "framework"
    assert strategy.categorize_section("Testing Standards") == "framework"
    assert strategy.categorize_section("Code Quality") == "framework"


def test_categorize_section_hybrid():
    """Test categorize_section() identifies hybrid sections."""
    strategy = ClaudeMdBlendStrategy()

    assert strategy.categorize_section("Quick Commands") == "hybrid"
    assert strategy.categorize_section("Command Permissions") == "hybrid"
    assert strategy.categorize_section("Resources") == "hybrid"


def test_categorize_section_project():
    """Test categorize_section() defaults to project for unknown."""
    strategy = ClaudeMdBlendStrategy()

    assert strategy.categorize_section("Project Structure") == "project"
    assert strategy.categorize_section("Custom Section") == "project"
    assert strategy.categorize_section("Team Info") == "project"


def test_blend_requires_llm_client():
    """Test blend() raises if llm_client not in context."""
    strategy = ClaudeMdBlendStrategy()

    with pytest.raises(ValueError, match="LLM client required"):
        strategy.blend("## Test", "## Test", context={})

    with pytest.raises(ValueError, match="LLM client required"):
        strategy.blend("## Test", "## Test", context=None)


def test_blend_framework_sections_copied():
    """Test blend() copies framework sections as-is."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principle 1
Framework principle 2

## Testing Standards

Framework standard 1
"""

    target = """## Core Principles

Target principle 1

## Custom Section

Target custom info
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, target, context)

    # Framework sections should be copied (not merged)
    assert "Framework principle 1" in result
    assert "Framework principle 2" in result
    # Target changes to framework sections should NOT appear
    assert "Target principle 1" not in result


def test_blend_hybrid_sections_merged():
    """Test blend() merges hybrid sections with Sonnet."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Quick Commands

Framework command 1

## Resources

Framework resource 1
"""

    target = """## Quick Commands

Target command 1

## Resources

Target resource 1
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, target, context)

    # Hybrid sections should be merged (MockLLM appends)
    sections = strategy.parse_sections(result)
    assert "Quick Commands" in sections
    assert "Framework command 1" in sections["Quick Commands"]
    assert "Target command 1" in sections["Quick Commands"]


def test_blend_target_only_sections_imported():
    """Test blend() imports target-only project sections."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principles
"""

    target = """## Core Principles

Target principles

## Project Structure

Target project structure
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, target, context)

    # Target-only project section should be imported
    assert "Project Structure" in result
    assert "Target project structure" in result


def test_blend_empty_target():
    """Test blend() handles empty target content."""
    strategy = ClaudeMdBlendStrategy()

    framework = """## Core Principles

Framework principles

## Testing Standards

Framework standards
"""

    context = {"llm_client": MockLLM()}
    result = strategy.blend(framework, "", context)

    # Framework sections should be present
    assert "Core Principles" in result
    assert "Testing Standards" in result
    assert "Framework principles" in result


def test_validate_valid_claude_md():
    """Test validate() passes for valid CLAUDE.md."""
    strategy = ClaudeMdBlendStrategy()

    valid_content = """## Core Principles

Principles

## Framework Initialization

Init info

## Testing Standards

Standards
"""

    assert strategy.validate(valid_content) is True


def test_validate_missing_required_section():
    """Test validate() raises if required section missing."""
    strategy = ClaudeMdBlendStrategy()

    invalid_content = """## Core Principles

Principles

## Custom Section

Custom info
"""

    with pytest.raises(ValueError, match="Missing required framework sections"):
        strategy.validate(invalid_content)


def test_validate_duplicate_sections():
    """Test validate() raises if duplicate H2 sections."""
    strategy = ClaudeMdBlendStrategy()

    invalid_content = """## Core Principles

Principles 1

## Framework Initialization

Init

## Testing Standards

Standards

## Core Principles

Principles 2 (duplicate)
"""

    with pytest.raises(ValueError, match="Duplicate H2 sections"):
        strategy.validate(invalid_content)


def test_validate_empty_content():
    """Test validate() raises on empty content."""
    strategy = ClaudeMdBlendStrategy()

    with pytest.raises(ValueError, match="empty"):
        strategy.validate("")

    with pytest.raises(ValueError, match="empty"):
        strategy.validate("   ")


def test_validate_no_sections():
    """Test validate() raises if no H2 sections."""
    strategy = ClaudeMdBlendStrategy()

    invalid_content = """# Title

Some content but no H2 sections
"""

    with pytest.raises(ValueError, match="No H2 sections found"):
        strategy.validate(invalid_content)
```

**Validation**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py -v
# Expected: 16/16 tests pass
```

### Phase 5: Integration and Coverage (30 min)

**Goal**: Run tests, verify coverage, test with real BlendingLLM (optional)

**Steps**:

1. **Run unit tests**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py -v
```

2. **Check coverage**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py --cov=ce.blending.strategies.claude_md --cov-report=term-missing -v
```

**Expected Coverage**: ≥80%

3. **Optional: Test with real BlendingLLM** (requires ANTHROPIC_API_KEY):
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
export ANTHROPIC_API_KEY="sk-..."
uv run python3 << 'EOF'
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy
from ce.blending.llm_client import BlendingLLM

strategy = ClaudeMdBlendStrategy()
llm = BlendingLLM()

framework = """## Core Principles

- KISS principle
- No fishy fallbacks

## Testing Standards

- TDD approach
- Real functionality
"""

target = """## Core Principles

- User principle 1

## Project Structure

Project-specific structure
"""

context = {"llm_client": llm}
result = strategy.blend(framework, target, context)

print("✓ Blended CLAUDE.md:")
print(result)
print(f"\nToken usage: {llm.get_token_usage()}")

# Validate
strategy.validate(result)
print("✓ Validation passed")
EOF
```

4. **Update package __init__.py** (if needed):
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
# Check if ce/blending/strategies/__init__.py exists
ls ce/blending/strategies/__init__.py || echo "# Strategies" > ce/blending/strategies/__init__.py
```

## 4. Validation Gates

### Gate 1: Strategy Implements BlendStrategy Protocol

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python3 -c "
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy

s = ClaudeMdBlendStrategy()
assert hasattr(s, 'can_handle')
assert hasattr(s, 'blend')
assert hasattr(s, 'validate')
print('✓ ClaudeMdBlendStrategy implements BlendStrategy protocol')
"
```

**Expected**: "✓ ClaudeMdBlendStrategy implements BlendStrategy protocol"

**On Failure**:
- Check class has all three methods: can_handle(), blend(), validate()
- Verify method signatures match BlendStrategy protocol

### Gate 2: Section Parsing Works Correctly

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py::test_parse_sections_splits_by_h2 -v
uv run pytest tests/test_blend_claude_md.py::test_parse_sections_empty_content -v
```

**Expected**: Both tests pass

**On Failure**:
- Check parse_sections() splits on "## " correctly
- Verify empty content returns {}
- Check section content includes H2 header

### Gate 3: Section Categorization Correct

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py::test_categorize_section_framework -v
uv run pytest tests/test_blend_claude_md.py::test_categorize_section_hybrid -v
uv run pytest tests/test_blend_claude_md.py::test_categorize_section_project -v
```

**Expected**: All categorization tests pass

**On Failure**:
- Check FRAMEWORK_SECTIONS set includes all framework sections
- Check HYBRID_SECTIONS set includes all hybrid sections
- Verify categorize_section() returns correct category

### Gate 4: Framework Sections Preserved

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py::test_blend_framework_sections_copied -v
```

**Expected**: Test passes - framework sections copied as-is

**On Failure**:
- Check blend() identifies framework sections correctly
- Verify framework sections not merged (copied directly)
- Ensure target changes to framework sections excluded

### Gate 5: Target [PROJECT] Sections Imported

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py::test_blend_target_only_sections_imported -v
```

**Expected**: Test passes - target project sections imported

**On Failure**:
- Check blend() identifies target-only sections
- Verify categorize_section() for project sections
- Ensure target sections added to output

### Gate 6: RULES.md Content Passed to LLM

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python3 -c "
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy

class VerifyLLM:
    def blend_content(self, framework_content, target_content, rules_content=None, domain=''):
        assert rules_content is not None, 'rules_content must be passed'
        assert 'Framework' in rules_content, 'rules_content should contain RULES.md'
        return {'blended': framework_content, 'confidence': 0.95, 'model': 'test', 'tokens': {}}

s = ClaudeMdBlendStrategy()
context = {'llm_client': VerifyLLM(), 'rules_content': '# Framework Rules\nTest'}
s.blend('## Quick Commands\nTest', '', context)
print('✓ RULES.md content passed to LLM')
"
```

**Expected**: "✓ RULES.md content passed to LLM"

**On Failure**:
- Check blend() passes context.get("rules_content") to llm.blend_content()
- Verify rules_content parameter in llm.blend_content() calls

### Gate 7: Validation Enforces Required Sections

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py::test_validate_missing_required_section -v
```

**Expected**: Test passes - ValueError raised for missing sections

**On Failure**:
- Check validate() checks for required framework sections
- Verify ValueError raised with actionable message
- Ensure required sections set includes Core Principles, Framework Initialization, Testing Standards

### Gate 8: Unit Tests Pass (≥80% Coverage)

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_claude_md.py -v --cov=ce.blending.strategies.claude_md --cov-report=term-missing
```

**Expected**: All tests pass (≥16 tests), coverage ≥80%

**On Failure**:
- Run individual tests to isolate failures
- Check coverage report for untested lines
- Add tests for uncovered code paths

## 5. Testing Strategy

### Test Framework

**pytest** (project standard)

### Test Files

- `tools/tests/test_blend_claude_md.py` - ClaudeMdBlendStrategy tests

### Test Categories

**Unit Tests** (with MockLLM):
- ✅ `test_can_handle_claude_md_domain` - Domain handling
- ✅ `test_parse_sections_splits_by_h2` - Section parsing
- ✅ `test_parse_sections_empty_content` - Edge case (empty)
- ✅ `test_categorize_section_framework` - Framework categorization
- ✅ `test_categorize_section_hybrid` - Hybrid categorization
- ✅ `test_categorize_section_project` - Project categorization
- ✅ `test_blend_requires_llm_client` - Error handling
- ✅ `test_blend_framework_sections_copied` - Framework preservation
- ✅ `test_blend_hybrid_sections_merged` - Hybrid merging
- ✅ `test_blend_target_only_sections_imported` - Target import
- ✅ `test_blend_empty_target` - Edge case (no target)
- ✅ `test_validate_valid_claude_md` - Validation success
- ✅ `test_validate_missing_required_section` - Validation failure
- ✅ `test_validate_duplicate_sections` - Validation failure
- ✅ `test_validate_empty_content` - Edge case validation
- ✅ `test_validate_no_sections` - Edge case validation

**Integration Tests** (optional, requires ANTHROPIC_API_KEY):
- ⚪ `test_blend_with_real_llm` - Live Sonnet blending
- ⚪ `test_blend_real_claude_md` - Full CLAUDE.md blend

### Test Command

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Run all tests (unit only, MockLLM)
uv run pytest tests/test_blend_claude_md.py -v

# Run with coverage
uv run pytest tests/test_blend_claude_md.py -v --cov=ce.blending.strategies.claude_md --cov-report=term-missing

# Run integration tests (requires ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="sk-..."
uv run pytest tests/test_blend_claude_md.py -v -m "not skipif"
```

**Coverage Target**: ≥80% for claude_md.py

### Testing Patterns

**Real Functionality**:
- MockLLM for unit tests (fast, deterministic)
- Optional real BlendingLLM for integration tests (expensive)
- No mocked HTTP responses in production code

**Error Handling**:
- Test missing LLM client in context
- Test empty content edge cases
- Test validation failures (missing sections, duplicates)

**Edge Cases**:
- Empty framework content
- Empty target content
- No H2 sections
- Duplicate section names
- Unknown section categories

## 6. Rollout Plan

### Phase 1: Development (2 hours)

**Steps**:
1. ✅ Create ClaudeMdBlendStrategy class structure (30 min)
2. ✅ Implement parse_sections() and categorize_section() (30 min)
3. ✅ Implement blend() method with Sonnet integration (45 min)
4. ✅ Implement validate() method (15 min)

**Validation**: All methods implemented, no syntax errors, imports work

### Phase 2: Testing (1 hour)

**Steps**:
1. ✅ Create test_blend_claude_md.py with MockLLM (30 min)
2. ✅ Write 16 unit tests covering all functionality (30 min)
3. ✅ Run tests and fix failures (as needed)

**Validation**: All unit tests pass, coverage ≥80%

### Phase 3: Integration (SUBSEQUENT PRPs)

**Prerequisites**: This PRP (34.3.1) complete

**Next PRPs that use ClaudeMdBlendStrategy**:
- **PRP-34.4.1**: Blending orchestrator integration (Phase C)
- **PRP-34.5.1**: E2E blending pipeline tests

**Integration**: Import ClaudeMdBlendStrategy in orchestrator, register for "claude_md" domain

### Phase 4: Deployment (NOT THIS PRP)

**Prerequisites**: All PRP-34 strategies complete, E2E tests pass

**Steps**:
1. Merge all PRPs to main
2. Update INITIALIZATION.md to reference automated CLAUDE.md blending
3. Document token costs and Sonnet usage
4. Create troubleshooting guide for blending issues

**Validation**: Full blending pipeline works end-to-end

---

## Research Findings

### Codebase Analysis

**Strategy Pattern Usage** (from PRP-34.2.4):
- Protocol-based strategy interface with can_handle(), blend(), validate()
- SettingsBlendStrategy example (rule-based, no LLM)
- 3-rule blending logic (deny precedence, list merging, single membership)

**BlendingLLM API** (from PRP-34.2.6):
```python
result = llm.blend_content(
    framework_content=str,
    target_content=str,
    rules_content=str,  # RULES.md content
    domain=str          # For logging/context
)
# Returns: {"blended": str, "model": str, "tokens": dict, "confidence": float}
```

**CLAUDE.md Structure** (from actual file):
- 25+ H2 sections
- Mix of framework (authoritative) and project-specific content
- ~15k tokens total
- Markdown formatting with lists, tables, mermaid diagrams

**RULES.md Content** (expected but not found):
- Framework rules/principles
- Should be passed as invariants to Sonnet
- Enforces blending philosophy

### External Documentation

**Markdown Parsing**:
- H2 headers: Lines starting with "## "
- Section boundaries: Next H2 or EOF
- Preserve formatting within sections

**Sonnet Capabilities**:
- Excellent at understanding documentation context
- Can merge semantically similar content
- Respects system instructions (blending philosophy)
- Formats output with markdown (lists, tables, mermaid)

**Token Costs** (from PRP-34.2.6):
- Sonnet: ~$3/M input tokens, ~$15/M output tokens
- CLAUDE.md blend: ~15k input + 10k output = ~$0.20 per blend
- Acceptable for quality-critical documentation

**Best Practices**:
1. Use Sonnet for quality-critical content (not Haiku)
2. Pass RULES.md as context (invariants)
3. Preserve framework sections as-is (authoritative)
4. Validate output for required sections
5. Mock LLM for unit tests (fast, deterministic)

---

## Appendix: Usage Examples

### Example 1: Blend CLAUDE.md Files

```python
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy
from ce.blending.llm_client import BlendingLLM
from pathlib import Path

# Initialize
strategy = ClaudeMdBlendStrategy()
llm = BlendingLLM()

# Load content
framework_md = Path(".ce/CLAUDE.md").read_text()
target_md = Path("CLAUDE.md").read_text()
rules = Path(".ce/RULES.md").read_text()

# Blend
context = {
    "llm_client": llm,
    "rules_content": rules
}

blended = strategy.blend(framework_md, target_md, context)

# Validate
strategy.validate(blended)

# Write output
Path("CLAUDE.md.blended").write_text(blended)

print(f"✓ Blended CLAUDE.md")
print(f"Token usage: {llm.get_token_usage()}")
```

### Example 2: Test Section Parsing

```python
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy

strategy = ClaudeMdBlendStrategy()

content = """## Core Principles

- KISS
- No fishy fallbacks

## Testing Standards

- TDD
- Real functionality
"""

sections = strategy.parse_sections(content)

for section_name, section_content in sections.items():
    category = strategy.categorize_section(section_name)
    print(f"{section_name} ({category}):")
    print(f"  {section_content[:50]}...")
```

### Example 3: Validate Blended Output

```python
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy

strategy = ClaudeMdBlendStrategy()

blended = """## Core Principles

Framework principles

## Framework Initialization

Init instructions

## Testing Standards

Test standards

## Project Structure

Project-specific structure
"""

try:
    strategy.validate(blended)
    print("✓ Validation passed")
except ValueError as e:
    print(f"❌ Validation failed: {e}")
```

---

## Success Criteria Summary

✅ **ClaudeMdBlendStrategy class** implements BlendStrategy protocol
✅ **parse_sections() method** splits CLAUDE.md by H2 headers
✅ **categorize_section() method** identifies framework/hybrid/project sections
✅ **blend() method** uses Sonnet for intelligent merging
✅ **Framework sections** preserved as-is (authoritative)
✅ **Target [PROJECT] sections** imported where non-contradictory
✅ **RULES.md content** passed to LLM as invariants
✅ **Contradictions** resolved (framework wins)
✅ **Complementary content** merged in hybrid sections
✅ **validate() method** enforces required sections and no duplicates
✅ **Unit tests** pass (≥16 tests, ≥80% coverage)
✅ **MockLLM** used for fast, deterministic tests
✅ **Error handling** includes actionable troubleshooting messages
✅ **KISS principle** - clear code, single responsibility methods
✅ **No fishy fallbacks** - exceptions bubble up with 🔧 troubleshooting

---

## Next Steps After This PRP

**Immediate Dependencies** (PRPs that use ClaudeMdBlendStrategy):
1. **PRP-34.3.2**: Memories blending strategy (Haiku similarity + Sonnet merge)
2. **PRP-34.3.3**: Examples blending strategy (Haiku deduplication)
3. **PRP-34.4.1**: Blending orchestrator (Phase C integration)

**Integration Pattern**:
```python
# In blending orchestrator
from ce.blending.strategies.claude_md import ClaudeMdBlendStrategy

strategies = {
    "claude_md": ClaudeMdBlendStrategy(),
    "settings": SettingsBlendStrategy(),
    "memories": MemoriesBlendStrategy(),
    "examples": ExamplesBlendStrategy()
}

# Blend CLAUDE.md
strategy = strategies["claude_md"]
blended = strategy.blend(framework_content, target_content, context)
```

---

**END OF PRP-34.3.1**
