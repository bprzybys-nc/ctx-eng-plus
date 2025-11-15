---
prp_id: PRP-34.1.1
feature_name: Core Blending Framework
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
complexity: high
estimated_hours: 4.0
dependencies: []
batch_id: 34
stage: stage-1-sequential
execution_order: 1
merge_order: 1
worktree_path: ../ctx-eng-plus-prp-34-1-1
branch_name: prp-34-1-1-core-framework
---

# PRP-34.1.1: Core Blending Framework

## 1. TL;DR

**Objective**: Create foundation for 4-phase migration pipeline (detect → classify → blend → cleanup) with strategy pattern, CLI entry point, configuration system, backup/rollback, and validation framework.

**What**: Base architecture for framework blending system that automates CE initialization merging across all domains (settings, CLAUDE.md, memories, examples, PRPs, commands).

**Why**: Current initialization uses ad-hoc merge logic scattered across multiple locations. No unified framework for detecting legacy files, validating CE patterns, blending content, or cleaning up after migration. Need reusable foundation that domain-specific strategies can build upon.

**Effort**: 4 hours

**Dependencies**: None (foundation PRP for all other blending strategies)

**Files Modified**:
- `tools/ce/blend.py` (new)
- `tools/ce/blending/core.py` (new)
- `tools/ce/blending/strategies/base.py` (new)
- `tools/ce/blending/validation.py` (new)
- `.ce/blend-config.yml` (new)

## 2. Context

### Background

PRP-34 INITIAL documents the complete vision for framework blending system. This PRP (34.1.1) implements the **core foundation** that all subsequent PRPs will build upon.

**Current State**:
- No legacy file detection system
- No CE pattern validation
- Settings blending in PRP-33 (TypeScript in syntropy-mcp)
- CLAUDE.md blending manual (INITIALIZATION.md Phase 4)
- No cleanup of legacy directories after migration
- No reusable framework for blending operations

**Target State**:
- **Strategy pattern** for pluggable domain blending
- **4-phase pipeline orchestration** (detect → classify → blend → cleanup)
- **CLI entry point** with comprehensive options
- **Configuration system** via YAML
- **Backup/rollback** for all operations
- **Validation framework** for post-blend checks

**Architecture Principles** (from PRP-34 INITIAL):
1. **Strategy Pattern**: Each domain has pluggable merge strategy
2. **Claude SDK Integration**: Use same tokens as Claude Code for NL-based blending
3. **Declarative Configuration**: Define merge rules in YAML
4. **Reversible Operations**: Create backups before blending
5. **Validation Gates**: Verify output integrity post-blend

### 4-Phase Pipeline Overview

```
Phase A: DETECTION (Python)
  └─ Scan: PRPs/, examples/, context-engineering/, .serena/, .claude/
  └─ Handle symlinks, resolve paths

Phase B: CLASSIFICATION (Haiku - fast/cheap)
  └─ Validate CE patterns
  └─ Filter garbage (reports, summaries, initials)
  └─ Confidence scoring (0.0-1.0)

Phase C: BLENDING (Hybrid Haiku + Sonnet)
  ├─ Settings: Rule-based (Python)
  ├─ CLAUDE.md: NL-blend (Sonnet)
  ├─ Memories: NL-blend (Haiku similarity → Sonnet merge)
  ├─ Examples: NL-dedupe (Haiku)
  ├─ PRPs: Move all (Python, no dedupe by ID)
  └─ Commands: Overwrite (Python)

Phase D: CLEANUP (Python)
  └─ Remove PRPs/, examples/, context-engineering/
  └─ Keep .claude/, .serena/, CLAUDE.md (standard locations)
```

**Blending Philosophy**: "Copy ours (framework), import theirs (target) where not contradictory"

### Constraints and Considerations

1. **KISS Principle**: Simple solutions first, clear code over clever code
2. **No Fishy Fallbacks**: Fast failure, exceptions bubble up, actionable errors
3. **Function Limits**: Target 50 lines max per function
4. **File Limits**: Target 500 lines max per file
5. **Real Functionality**: No mocked results, no hardcoded success messages
6. **UV Package Management**: Use `uv add` for dependencies (no manual pyproject.toml edits)
7. **Strategy Pattern**: ABC base class with can_handle(), blend(), validate() methods
8. **Backup Context**: Context manager for atomic backup-modify-restore operations
9. **Configuration**: Declarative YAML config for domain rules
10. **CLI Design**: Support all modes (--all, --phase, --domain, --dry-run, --interactive, --fast, --quality, --scan, --skip-cleanup, --cleanup-only, --rollback)

### Documentation References

**Internal**:
- PRP-34 INITIAL: Complete vision for blending system
- INITIALIZATION.md: Manual blending process (Phase 4)
- PRP-33: Settings blending (TypeScript, needs Python port)
- CLAUDE.md: Code quality standards, KISS principle

**External**:
- Python ABC: https://docs.python.org/3/library/abc.html
- Context managers: https://docs.python.org/3/library/contextlib.html
- PyYAML: https://pyyaml.org/wiki/PyYAMLDocumentation
- Anthropic SDK: https://docs.anthropic.com/claude/reference/getting-started

## 3. Implementation Steps

### Phase 1: Setup and Dependencies (30 min)

**Goal**: Install required packages, create directory structure

**Steps**:

1. **Add Python dependencies via UV**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv add anthropic>=0.40.0
uv add pyyaml>=6.0
uv add deepdiff>=6.0
uv sync
```

2. **Create blending package structure**:
```bash
mkdir -p /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending
mkdir -p /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/strategies
touch /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/__init__.py
touch /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/strategies/__init__.py
```

3. **Verify structure**:
```bash
ls -la /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/blending/
```

**Validation**: Directory structure exists, UV dependencies installed

### Phase 2: Strategy Pattern Base Classes (1 hour)

**Goal**: Implement ABC base class for all blending strategies

**File**: `tools/ce/blending/strategies/base.py`

**Implementation**:

```python
"""Base classes for blending strategies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path


class BlendStrategy(ABC):
    """
    Base class for all blending strategies.

    Each domain (settings, CLAUDE.md, memories, etc.) implements this interface
    to define how framework and target content should be blended.

    Philosophy: "Copy ours (framework), import theirs (target) where not contradictory"
    """

    @abstractmethod
    def can_handle(self, domain: str) -> bool:
        """
        Check if strategy can handle this domain.

        Args:
            domain: Domain name (settings, claude_md, memories, etc.)

        Returns:
            True if strategy can handle this domain

        Example:
            >>> strategy = SettingsBlendStrategy()
            >>> strategy.can_handle("settings")
            True
            >>> strategy.can_handle("claude_md")
            False
        """
        pass

    @abstractmethod
    def blend(
        self,
        framework_content: Any,
        target_content: Optional[Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Blend framework and target content.

        Args:
            framework_content: Framework version (always present, authoritative)
            target_content: Target version (may be None)
            context: Additional context:
                - file_path: Path to output file
                - dry_run: bool (if True, return result without writing)
                - interactive: bool (if True, ask user for conflicts)
                - backup_path: Path to backup (if created)
                - rules_content: str (framework rules, e.g., RULES.md)
                - llm_client: Anthropic client (for NL-based strategies)

        Returns:
            Blended content (type varies by domain)

        Raises:
            ValueError: If framework_content invalid
            RuntimeError: If blending fails

        Note: No fishy fallbacks - exceptions bubble up with actionable messages
        """
        pass

    @abstractmethod
    def validate(self, blended_content: Any, context: Dict[str, Any]) -> bool:
        """
        Validate blended content integrity.

        Args:
            blended_content: Result from blend()
            context: Additional context (same as blend())

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If validation detects critical errors

        Example validation checks:
        - Settings: Valid JSON, all CE tools in one list
        - CLAUDE.md: Valid markdown, all framework sections present
        - Memories: Valid YAML headers, >= 23 files
        """
        pass

    def get_domain_name(self) -> str:
        """
        Get human-readable domain name.

        Returns:
            Domain name (e.g., "Settings JSON", "CLAUDE.md")
        """
        return self.__class__.__name__.replace("BlendStrategy", "")
```

**Validation**:
- File creates successfully
- No syntax errors: `python3 -m py_compile tools/ce/blending/strategies/base.py`
- Imports work: `python3 -c "from ce.blending.strategies.base import BlendStrategy"`

### Phase 3: Backup Context Manager (45 min)

**Goal**: Implement backup-modify-restore pattern for atomic operations

**File**: `tools/ce/blending/core.py`

**Implementation**:

```python
"""Core blending framework: 4-phase pipeline orchestration."""

import shutil
import logging
from pathlib import Path
from typing import Generator, Dict, List, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


@contextmanager
def backup_context(file_path: Path) -> Generator[Path, None, None]:
    """
    Context manager for backup-modify-restore pattern.

    Creates backup before modification, removes on success, restores on failure.

    Args:
        file_path: Path to file to backup

    Yields:
        backup_path: Path to backup file

    Raises:
        OSError: If backup creation fails

    Usage:
        >>> with backup_context(Path("CLAUDE.md")) as backup:
        ...     # Modify file
        ...     modify_file(Path("CLAUDE.md"))
        ...     # If exception, auto-restore from backup

    Note: Atomic operation - either all changes succeed or all rolled back
    """
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')

    # Create backup
    if file_path.exists():
        try:
            shutil.copy2(file_path, backup_path)
            logger.info(f"✓ Backed up to {backup_path.name}")
        except OSError as e:
            raise OSError(
                f"Failed to create backup: {backup_path}\n"
                f"🔧 Troubleshooting: Check file permissions and disk space"
            ) from e

    try:
        yield backup_path

        # Success - remove backup
        if backup_path.exists():
            backup_path.unlink()
            logger.debug(f"Removed backup {backup_path.name}")

    except Exception as e:
        # Failure - restore backup
        logger.error(f"❌ Operation failed, restoring backup")

        if backup_path.exists():
            try:
                shutil.copy2(backup_path, file_path)
                logger.info(f"✓ Restored from backup {backup_path.name}")
            except OSError as restore_error:
                logger.critical(
                    f"⚠️ CRITICAL: Failed to restore backup!\n"
                    f"Original error: {e}\n"
                    f"Restore error: {restore_error}\n"
                    f"🔧 Manual recovery: cp {backup_path} {file_path}"
                )
        raise


class BlendingOrchestrator:
    """
    Orchestrates 4-phase migration pipeline.

    Phase A: DETECTION - Scan legacy locations
    Phase B: CLASSIFICATION - Validate CE patterns
    Phase C: BLENDING - Merge framework + target
    Phase D: CLEANUP - Remove legacy directories
    """

    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize orchestrator.

        Args:
            config: Configuration from blend-config.yml
            dry_run: If True, show what would be done without executing
        """
        self.config = config
        self.dry_run = dry_run
        self.strategies: List[Any] = []  # Registered blend strategies

    def register_strategy(self, strategy: Any) -> None:
        """
        Register a blending strategy.

        Args:
            strategy: Instance of BlendStrategy subclass
        """
        self.strategies.append(strategy)
        logger.debug(f"Registered strategy: {strategy.get_domain_name()}")

    def run_phase(self, phase: str, target_dir: Path) -> Dict[str, Any]:
        """
        Run specific phase of pipeline.

        Args:
            phase: Phase name (detect, classify, blend, cleanup)
            target_dir: Target project directory

        Returns:
            Phase results dict

        Raises:
            ValueError: If phase unknown
            RuntimeError: If phase execution fails
        """
        if phase not in ['detect', 'classify', 'blend', 'cleanup']:
            raise ValueError(
                f"Unknown phase: {phase}\n"
                f"🔧 Valid phases: detect, classify, blend, cleanup"
            )

        logger.info(f"🔀 Running Phase: {phase.upper()}")

        # Placeholder - actual implementation in subsequent PRPs
        if phase == 'detect':
            return self._run_detection(target_dir)
        elif phase == 'classify':
            return self._run_classification(target_dir)
        elif phase == 'blend':
            return self._run_blending(target_dir)
        elif phase == 'cleanup':
            return self._run_cleanup(target_dir)

    def _run_detection(self, target_dir: Path) -> Dict[str, Any]:
        """Phase A: Scan legacy locations (stub for PRP-34.2.1)."""
        logger.info("Detection phase not yet implemented (PRP-34.2.1)")
        return {"phase": "detect", "implemented": False}

    def _run_classification(self, target_dir: Path) -> Dict[str, Any]:
        """Phase B: Validate CE patterns (stub for PRP-34.2.2)."""
        logger.info("Classification phase not yet implemented (PRP-34.2.2)")
        return {"phase": "classify", "implemented": False}

    def _run_blending(self, target_dir: Path) -> Dict[str, Any]:
        """Phase C: Blend content (stub for PRP-34.3.x)."""
        logger.info("Blending phase not yet implemented (PRP-34.3.x)")
        return {"phase": "blend", "implemented": False}

    def _run_cleanup(self, target_dir: Path) -> Dict[str, Any]:
        """Phase D: Remove legacy dirs (stub for PRP-34.2.3)."""
        logger.info("Cleanup phase not yet implemented (PRP-34.2.3)")
        return {"phase": "cleanup", "implemented": False}
```

**Validation**:
- No syntax errors: `python3 -m py_compile tools/ce/blending/core.py`
- Imports work: `python3 -c "from ce.blending.core import backup_context, BlendingOrchestrator"`
- Backup context creates/removes backups correctly (unit test)

### Phase 4: CLI Entry Point (1 hour)

**Goal**: Implement argparse-based CLI with all modes

**File**: `tools/ce/blend.py`

**Implementation**:

```python
"""CLI entry point for blending operations."""

import sys
import logging
import argparse
from pathlib import Path
from typing import Dict, Any

from .blending.core import BlendingOrchestrator
from .core import run_cmd

logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(message)s'
    )


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Load blend configuration from YAML.

    Args:
        config_path: Path to blend-config.yml

    Returns:
        Configuration dict

    Raises:
        FileNotFoundError: If config file not found
        ValueError: If config invalid
    """
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found: {config_path}\n"
            f"🔧 Create .ce/blend-config.yml (see PRP-34.1.1)"
        )

    import yaml

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if not config or 'domains' not in config:
            raise ValueError("Config missing 'domains' section")

        return config

    except yaml.YAMLError as e:
        raise ValueError(
            f"Invalid YAML config: {e}\n"
            f"🔧 Check syntax: {config_path}"
        ) from e


def run_blend(args: argparse.Namespace) -> int:
    """
    Execute blending operation.

    Args:
        args: Parsed CLI arguments

    Returns:
        Exit code (0 = success, 1 = failure)
    """
    try:
        # Load configuration
        config_path = Path(args.config)
        config = load_config(config_path)

        # Initialize orchestrator
        orchestrator = BlendingOrchestrator(
            config=config,
            dry_run=args.dry_run
        )

        # Determine target directory
        target_dir = Path(args.target_dir).resolve()
        if not target_dir.exists():
            raise ValueError(
                f"Target directory not found: {target_dir}\n"
                f"🔧 Provide valid project directory"
            )

        # Run phases
        if args.all:
            # Run all 4 phases
            phases = ['detect', 'classify', 'blend']
            if not args.skip_cleanup:
                phases.append('cleanup')

            for phase in phases:
                result = orchestrator.run_phase(phase, target_dir)
                logger.info(f"✓ Phase {phase} complete")

                # Interactive mode - ask before next phase
                if args.interactive and phase != phases[-1]:
                    response = input(f"Continue to {phases[phases.index(phase) + 1]}? [Y/n] ")
                    if response.lower() == 'n':
                        logger.info("Stopped by user")
                        return 0

        elif args.phase:
            # Run specific phase
            result = orchestrator.run_phase(args.phase, target_dir)
            logger.info(f"✓ Phase {args.phase} complete")

        elif args.cleanup_only:
            # Run cleanup only (requires prior blend)
            result = orchestrator.run_phase('cleanup', target_dir)
            logger.info("✓ Cleanup complete")

        elif args.rollback:
            # Restore backups
            logger.info("🔄 Rolling back blending operations...")
            # Stub - implement in validation.py (PRP-34.1.1)
            logger.warning("Rollback not yet fully implemented")
            return 1

        else:
            logger.error("No operation specified (use --all, --phase, --cleanup-only, or --rollback)")
            return 1

        logger.info("✅ Blending complete!")
        return 0

    except Exception as e:
        logger.error(f"❌ Blending failed: {e}")
        if args.verbose:
            logger.exception("Full traceback:")
        return 1


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CE Framework Blending Tool - Migrate and blend framework files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full pipeline (all 4 phases)
  uv run ce blend --all

  # Individual phases
  uv run ce blend --phase detect
  uv run ce blend --phase classify
  uv run ce blend --phase blend
  uv run ce blend --phase cleanup

  # Dry-run (show what would be done)
  uv run ce blend --all --dry-run

  # Interactive mode (ask before each phase)
  uv run ce blend --all --interactive

  # Skip cleanup (keep legacy directories)
  uv run ce blend --all --skip-cleanup

  # Cleanup only (requires prior blend)
  uv run ce blend --cleanup-only

  # Rollback (restore backups)
  uv run ce blend --rollback
"""
    )

    # Operation modes
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--all', action='store_true', help='Run all 4 phases')
    mode_group.add_argument('--phase', choices=['detect', 'classify', 'blend', 'cleanup'], help='Run specific phase')
    mode_group.add_argument('--cleanup-only', action='store_true', help='Run cleanup only')
    mode_group.add_argument('--rollback', action='store_true', help='Restore backups')

    # Domain selection (optional)
    parser.add_argument('--domain', help='Blend specific domain only (settings, claude_md, memories, examples, prps, commands)')

    # Behavior flags
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--interactive', action='store_true', help='Ask before each phase')
    parser.add_argument('--skip-cleanup', action='store_true', help='Skip Phase D (keep legacy dirs)')
    parser.add_argument('--fast', action='store_true', help='Fast mode (Haiku only, skip expensive ops)')
    parser.add_argument('--quality', action='store_true', help='Quality mode (Sonnet for all LLM calls)')
    parser.add_argument('--scan', action='store_true', help='Scan mode (detect + classify only, no blending)')

    # Configuration
    parser.add_argument('--config', default='.ce/blend-config.yml', help='Path to blend config (default: .ce/blend-config.yml)')
    parser.add_argument('--target-dir', default='.', help='Target project directory (default: current)')

    # Debugging
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)

    # Run blending
    return run_blend(args)


if __name__ == '__main__':
    sys.exit(main())
```

**Validation**:
- CLI runs: `uv run ce blend --help`
- All options displayed correctly
- Error handling works: `uv run ce blend --all` (should fail with config not found)

### Phase 5: Configuration System (45 min)

**Goal**: Create YAML configuration for domain rules

**File**: `.ce/blend-config.yml`

**Implementation**:

```yaml
# CE Framework Blending Configuration
# Defines blending rules for each domain (settings, CLAUDE.md, memories, etc.)

domains:
  settings:
    strategy: rule-based
    source: .claude/settings.local.json
    backup: true
    rules:
      - ce_deny_wins           # CE deny list takes precedence
      - merge_lists            # Merge CE entries to target lists
      - single_membership      # Each tool in ONE list only
    description: "Settings JSON structural merge (3 rules)"

  claude_md:
    strategy: nl-blend
    source: CLAUDE.md
    framework_rules: .ce/RULES.md
    backup: true
    llm_model: claude-sonnet-4-5-20250929
    max_tokens: 8192
    description: "CLAUDE.md NL-blend with RULES.md awareness (Sonnet)"

  memories:
    strategy: nl-blend
    source: .serena/memories/
    backup: true
    llm_model_similarity: claude-3-5-haiku-20241022    # Fast similarity checks
    llm_model_merge: claude-sonnet-4-5-20250929        # Quality merges
    conflict_resolution: ask-user
    similarity_threshold: 0.9
    description: "Serena memories NL-blend (Haiku similarity → Sonnet merge)"

  examples:
    strategy: dedupe-copy
    source: examples/
    destination: .ce/examples/
    backup: false
    dedup_method: nl-similarity
    llm_model: claude-3-5-haiku-20241022               # Fast deduplication
    similarity_threshold: 0.9
    description: "Examples NL-dedupe (Haiku semantic comparison)"

  prps:
    strategy: move-all
    source: PRPs/
    legacy_sources:
      - PRPs/
      - context-engineering/PRPs/
    destination: .ce/PRPs/
    backup: false
    dedup_method: content-hash                          # Only skip if exact file exists
    add_user_header: true
    note: "Move all user PRPs (no ID-based deduplication - different projects can have same IDs)"
    description: "PRPs move-all (hash dedupe only, no ID dedupe)"

  commands:
    strategy: overwrite
    source: .claude/commands/
    backup: true
    backup_location: .claude/commands.backup/
    description: "Commands overwrite (framework canonical)"

# LLM Configuration
llm:
  api_key_env: ANTHROPIC_API_KEY
  timeout: 60
  max_retries: 3

# Global settings
global:
  verify_before_cleanup: true
  backup_prefix: ".backup"
  legacy_directories:
    - PRPs/
    - examples/
    - context-engineering/
  standard_locations:
    - .claude/
    - .serena/
    - CLAUDE.md
    - .ce/
```

**Validation**:
- File creates successfully
- Valid YAML: `python3 -c "import yaml; yaml.safe_load(open('.ce/blend-config.yml'))"`
- Config loads in blend.py: `uv run ce blend --help` (should not error on config load)

### Phase 6: Validation Framework (45 min)

**Goal**: Implement post-blend validation checks

**File**: `tools/ce/blending/validation.py`

**Implementation**:

```python
"""Post-blend validation framework."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


def validate_settings_json(file_path: Path) -> Tuple[bool, List[str]]:
    """
    Validate settings.local.json after blending.

    Checks:
    1. Valid JSON
    2. Has allow/deny/ask lists
    3. Each CE tool in ONE list only

    Args:
        file_path: Path to settings.local.json

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    if not file_path.exists():
        return (False, [f"Settings file not found: {file_path}"])

    try:
        with open(file_path) as f:
            settings = json.load(f)
    except json.JSONDecodeError as e:
        return (False, [f"Invalid JSON: {e}"])

    # Check required lists exist
    for list_name in ['allow', 'deny', 'ask']:
        if list_name not in settings:
            errors.append(f"Missing '{list_name}' list")

    if errors:
        return (False, errors)

    # Check single membership (each tool in ONE list only)
    allow_set = set(settings.get('allow', []))
    deny_set = set(settings.get('deny', []))
    ask_set = set(settings.get('ask', []))

    # Find tools in multiple lists
    all_tools = allow_set | deny_set | ask_set
    for tool in all_tools:
        count = 0
        if tool in allow_set:
            count += 1
        if tool in deny_set:
            count += 1
        if tool in ask_set:
            count += 1

        if count > 1:
            errors.append(f"Tool in multiple lists: {tool}")

    return (len(errors) == 0, errors)


def validate_claude_md(file_path: Path, required_sections: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate CLAUDE.md after blending.

    Checks:
    1. File exists
    2. Valid markdown
    3. All framework sections present

    Args:
        file_path: Path to CLAUDE.md
        required_sections: List of required section headers (e.g., ["## Quick Commands"])

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    if not file_path.exists():
        return (False, [f"CLAUDE.md not found: {file_path}"])

    try:
        with open(file_path) as f:
            content = f.read()
    except OSError as e:
        return (False, [f"Cannot read CLAUDE.md: {e}"])

    # Check required sections present
    for section in required_sections:
        if section not in content:
            errors.append(f"Missing section: {section}")

    # Basic markdown validation
    if len(content) < 100:
        errors.append("CLAUDE.md too short (< 100 chars)")

    return (len(errors) == 0, errors)


def validate_memories(memories_dir: Path, min_count: int = 23) -> Tuple[bool, List[str]]:
    """
    Validate Serena memories after blending.

    Checks:
    1. Directory exists
    2. At least min_count memory files
    3. All have valid YAML headers

    Args:
        memories_dir: Path to .serena/memories/
        min_count: Minimum expected memory files (default: 23 framework memories)

    Returns:
        (is_valid, errors) tuple
    """
    errors = []

    if not memories_dir.exists():
        return (False, [f"Memories directory not found: {memories_dir}"])

    # Count memory files
    memory_files = list(memories_dir.glob('*.md'))

    if len(memory_files) < min_count:
        errors.append(f"Too few memories: {len(memory_files)} (expected >= {min_count})")

    # Check YAML headers (sample first 5)
    import yaml

    for memory_file in memory_files[:5]:
        try:
            with open(memory_file) as f:
                content = f.read()

            if not content.startswith('---'):
                errors.append(f"Missing YAML header: {memory_file.name}")
                continue

            # Parse YAML frontmatter
            yaml_end = content.find('---', 3)
            if yaml_end == -1:
                errors.append(f"Invalid YAML header: {memory_file.name}")
                continue

            yaml_content = content[3:yaml_end]
            yaml_data = yaml.safe_load(yaml_content)

            if not yaml_data or 'type' not in yaml_data:
                errors.append(f"YAML missing 'type': {memory_file.name}")

        except Exception as e:
            errors.append(f"Cannot parse {memory_file.name}: {e}")

    return (len(errors) == 0, errors)


def validate_all_domains(target_dir: Path, config: Dict[str, Any]) -> Dict[str, Tuple[bool, List[str]]]:
    """
    Run validation on all domains.

    Args:
        target_dir: Target project directory
        config: Blend configuration

    Returns:
        Dict of {domain: (is_valid, errors)}
    """
    results = {}

    # Validate settings
    settings_path = target_dir / '.claude' / 'settings.local.json'
    results['settings'] = validate_settings_json(settings_path)

    # Validate CLAUDE.md
    claude_md_path = target_dir / 'CLAUDE.md'
    required_sections = [
        "## Core Principles",
        "## Quick Commands",
        "## Project Structure"
    ]
    results['claude_md'] = validate_claude_md(claude_md_path, required_sections)

    # Validate memories
    memories_dir = target_dir / '.serena' / 'memories'
    results['memories'] = validate_memories(memories_dir, min_count=23)

    return results
```

**Validation**:
- No syntax errors: `python3 -m py_compile tools/ce/blending/validation.py`
- Imports work: `python3 -c "from ce.blending.validation import validate_all_domains"`
- Validation functions return expected format (unit test)

### Phase 7: Integration and Testing (30 min)

**Goal**: Wire everything together, create basic unit tests

**Steps**:

1. **Update CLI to use validation**:
   - Import validation functions in `blend.py`
   - Call `validate_all_domains()` after blending phase
   - Show validation results in output

2. **Create unit tests**:

**File**: `tools/tests/test_blend_core.py`

```python
"""Unit tests for core blending framework."""

import pytest
from pathlib import Path
import tempfile
import shutil

from ce.blending.core import backup_context, BlendingOrchestrator
from ce.blending.strategies.base import BlendStrategy


class MockBlendStrategy(BlendStrategy):
    """Mock strategy for testing."""

    def can_handle(self, domain: str) -> bool:
        return domain == "mock"

    def blend(self, framework_content, target_content, context):
        return "blended_content"

    def validate(self, blended_content, context):
        return blended_content == "blended_content"

    def get_domain_name(self):
        return "Mock"


def test_backup_context_creates_and_removes_backup():
    """Test backup context manager creates and removes backups."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("original")

        # Use backup context
        with backup_context(test_file) as backup:
            # Backup should exist
            assert backup.exists()
            assert backup.read_text() == "original"

            # Modify file
            test_file.write_text("modified")

        # Backup should be removed after success
        assert not backup.exists()
        assert test_file.read_text() == "modified"


def test_backup_context_restores_on_exception():
    """Test backup context restores file on exception."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("original")

        try:
            with backup_context(test_file) as backup:
                # Modify file
                test_file.write_text("modified")
                # Raise exception
                raise ValueError("Test error")
        except ValueError:
            pass

        # File should be restored
        assert test_file.read_text() == "original"


def test_blending_orchestrator_registers_strategies():
    """Test strategy registration."""
    config = {"domains": {}}
    orchestrator = BlendingOrchestrator(config, dry_run=True)

    strategy = MockBlendStrategy()
    orchestrator.register_strategy(strategy)

    assert len(orchestrator.strategies) == 1
    assert orchestrator.strategies[0] == strategy


def test_blending_orchestrator_run_phase_validates_phase():
    """Test run_phase validates phase name."""
    config = {"domains": {}}
    orchestrator = BlendingOrchestrator(config, dry_run=True)

    with pytest.raises(ValueError, match="Unknown phase"):
        orchestrator.run_phase("invalid_phase", Path("."))


def test_blending_orchestrator_phase_stubs():
    """Test phase methods exist (stubs for subsequent PRPs)."""
    config = {"domains": {}}
    orchestrator = BlendingOrchestrator(config, dry_run=True)

    # All phase stubs should return dict
    result = orchestrator.run_phase("detect", Path("."))
    assert isinstance(result, dict)
    assert result["phase"] == "detect"
    assert result["implemented"] == False
```

**Run tests**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_core.py -v
```

**Validation**: All tests pass

## 4. Validation Gates

### Gate 1: Dependencies Installed

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "import anthropic; import yaml; import deepdiff; print('✓ Dependencies OK')"
```

**Expected**: "✓ Dependencies OK"

**On Failure**:
- Run `uv sync` to install dependencies
- Check `pyproject.toml` has correct entries
- Verify internet connection for package downloads

### Gate 2: CLI Tool Runs

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run ce blend --help
```

**Expected**: Help text displays all options (--all, --phase, --domain, --dry-run, etc.)

**On Failure**:
- Check blend.py has no syntax errors: `python3 -m py_compile ce/blend.py`
- Verify CLI is registered in `__main__.py` or `pyproject.toml` scripts

### Gate 3: Strategy Pattern Instantiates

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.strategies.base import BlendStrategy; print('✓ Strategy base OK')"
```

**Expected**: "✓ Strategy base OK"

**On Failure**:
- Check strategies/base.py has no syntax errors
- Verify ABC imports correctly

### Gate 4: Backup Context Works

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_core.py::test_backup_context_creates_and_removes_backup -v
```

**Expected**: Test passes

**On Failure**:
- Check core.py has backup_context implementation
- Verify contextlib imports correctly
- Test file permissions in temp directory

### Gate 5: Config File Loads

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
python3 -c "import yaml; config = yaml.safe_load(open('.ce/blend-config.yml')); print(f'✓ Config loaded: {len(config[\"domains\"])} domains')"
```

**Expected**: "✓ Config loaded: 6 domains"

**On Failure**:
- Check YAML syntax in blend-config.yml
- Verify all required sections present (domains, llm, global)
- Use YAML linter to find syntax errors

### Gate 6: All Unit Tests Pass

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_core.py -v
```

**Expected**: All tests pass (6+ tests)

**On Failure**:
- Run individual tests to isolate failure
- Check test output for specific assertion errors
- Verify all stubs implemented (phase methods return dicts)

### Gate 7: Validation Framework Works

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.blending.validation import validate_all_domains; print('✓ Validation framework OK')"
```

**Expected**: "✓ Validation framework OK"

**On Failure**:
- Check validation.py has no syntax errors
- Verify all validation functions implemented
- Test with sample files if import succeeds but functions fail

## 5. Testing Strategy

### Test Framework

**pytest** (already used in project)

### Test Files

- `tools/tests/test_blend_core.py` - Core framework tests (backup context, orchestrator)
- `tools/tests/test_blend_validation.py` - Validation framework tests
- `tools/tests/test_blend_cli.py` - CLI argument parsing tests

### Test Categories

**Unit Tests** (Phase 7):
- ✅ `test_backup_context_creates_and_removes_backup` - Happy path
- ✅ `test_backup_context_restores_on_exception` - Error handling
- ✅ `test_blending_orchestrator_registers_strategies` - Strategy registration
- ✅ `test_blending_orchestrator_run_phase_validates_phase` - Phase validation
- ✅ `test_blending_orchestrator_phase_stubs` - Stub methods exist
- ✅ `test_validation_settings_json` - Settings validation
- ✅ `test_validation_claude_md` - CLAUDE.md validation
- ✅ `test_validation_memories` - Memories validation

**Integration Tests** (subsequent PRPs):
- Test full pipeline with real strategies (PRP-34.3.x)
- Test CLI with all options (PRP-34.3.x)
- Test configuration loading and domain processing (PRP-34.3.x)

**E2E Tests** (PRP-34.6):
- Test complete init workflow (detect → classify → blend → cleanup)
- Test rollback functionality
- Test dry-run mode produces correct preview

### Test Command

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_blend_core.py -v --cov=ce.blending --cov-report=term-missing
```

**Coverage Target**: ≥80% for core framework (this PRP), ≥90% for complete system (PRP-34.6)

### Testing Patterns

**Real Functionality**:
- No mocked file operations (use tempfile for real files)
- No hardcoded success messages
- Actual backup/restore operations tested

**Error Handling**:
- Test exception paths (backup restore on failure)
- Test invalid inputs (unknown phase, invalid config)
- Test missing files (config not found)

**Edge Cases**:
- Empty config
- Missing YAML sections
- File permission errors
- Disk full scenarios (where possible)

## 6. Rollout Plan

### Phase 1: Development (3.5 hours)

**Steps**:
1. ✅ Add dependencies via UV (30 min)
2. ✅ Implement strategy pattern base class (1 hour)
3. ✅ Implement backup context manager (45 min)
4. ✅ Implement CLI entry point (1 hour)
5. ✅ Create configuration system (45 min)

**Validation**: All code implements, no syntax errors, CLI runs

### Phase 2: Testing (1 hour)

**Steps**:
1. ✅ Implement validation framework (45 min)
2. ✅ Create unit tests (30 min)
3. ✅ Run all tests and fix failures (30 min)

**Validation**: All unit tests pass (≥6 tests), coverage ≥80%

### Phase 3: Documentation (30 min)

**Steps**:
1. Update CLI help text
2. Add docstrings to all public methods
3. Create USAGE.md for blend tool (optional)

**Validation**: `uv run ce blend --help` shows comprehensive help

### Phase 4: Integration (SUBSEQUENT PRPs)

**Prerequisites**: This PRP (34.1.1) complete

**Next PRPs**:
- **PRP-34.2.1**: Detection module (Phase A)
- **PRP-34.2.2**: Classification module (Phase B)
- **PRP-34.2.3**: Cleanup module (Phase D)
- **PRP-34.3.1**: Settings blending strategy (Phase C)
- **PRP-34.3.2**: CLAUDE.md blending strategy (Phase C)
- **PRP-34.3.3**: Memories blending strategy (Phase C)
- **PRP-34.3.4**: Examples dedupe strategy (Phase C)
- **PRP-34.3.5**: Simple strategies (PRPs, Commands) (Phase C)
- **PRP-34.6**: Integration and E2E tests

**Integration**: Wire strategies into orchestrator, test full pipeline

### Phase 5: Deployment (NOT THIS PRP)

**Prerequisites**: All PRP-34.x complete, E2E tests pass

**Steps**:
1. Merge all PRPs to main
2. Update INITIALIZATION.md to reference blend tool
3. Update syntropy-mcp init procedure
4. Create migration guide for existing users

**Validation**: End-to-end init workflow works

---

## Research Findings

### Codebase Analysis (Existing Patterns)

**File Operations** (`tools/ce/core.py`):
- `run_cmd()` function for safe shell execution
- Error handling with actionable troubleshooting messages
- Timeout support, capture_output flag
- Uses shlex.split() for safe parsing (CWE-78 prevention)

**Validation Patterns** (`tools/ce/validate.py`):
- 4-level validation system (syntax, logic, tests, patterns)
- Real validation, no mocked results
- Dictionary return format: `{success: bool, errors: List[str], duration: float}`
- Mermaid validation with auto-fix capability

**Configuration** (`.ce/linear-defaults.yml`):
- YAML-based configuration for defaults
- Comments explaining each field
- Validated on load (FileNotFoundError if missing)

**CLI Patterns** (`tools/ce/__main__.py`):
- argparse with subcommands (validate, context, prp, etc.)
- Clear help text with examples
- Verbose flag for debugging
- Exit codes (0 = success, 1+ = failure with meaning)

**Logging** (`tools/ce/logging_config.py`):
- Structured logging with levels
- Unicode symbols for visual clarity (✓, ✗, ⚠️, 🔧)
- Actionable error messages with troubleshooting

**Testing** (`tools/tests/`):
- pytest framework
- Real functionality (no mocks where possible)
- Fixtures for common setup
- Coverage tracking with pytest-cov

**Symmetries Identified**:
- **Backup-modify-restore**: Used for settings, CLAUDE.md, memories, commands
  - **Generalization**: `backup_context()` context manager ✅ Implemented
- **Validate-apply-rollback**: Used across all operations
  - **Generalization**: Validation framework with rollback support
- **Configuration-driven**: All tools use YAML/JSON config
  - **Generalization**: blend-config.yml for declarative rules

### External Documentation

**Python ABC** (Abstract Base Classes):
- Use `from abc import ABC, abstractmethod`
- Subclasses must implement all abstract methods
- Can have concrete methods for shared logic
- Example: https://docs.python.org/3/library/abc.html

**Context Managers** (contextlib):
- Use `@contextmanager` decorator for generator-based managers
- Yield provides value, cleanup in finally block
- Exception handling with try/except in generator
- Example: https://docs.python.org/3/library/contextlib.html

**PyYAML**:
- Use `yaml.safe_load()` for untrusted input
- Supports Python types (dict, list, str, int, bool)
- Comments preserved with `yaml.load(Loader=yaml.RoundTripLoader)`
- Example: https://pyyaml.org/wiki/PyYAMLDocumentation

**Anthropic SDK**:
- Client initialization: `Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))`
- Message creation: `client.messages.create(model="...", max_tokens=..., messages=[...])`
- Models: Haiku (fast/cheap), Sonnet (quality)
- Example: https://docs.anthropic.com/claude/reference/getting-started

---

## Appendix: Architecture Diagrams

### Strategy Pattern Class Hierarchy

```
BlendStrategy (ABC)
├── can_handle(domain: str) -> bool
├── blend(framework, target, context) -> Any
├── validate(blended, context) -> bool
└── get_domain_name() -> str

Subclasses (subsequent PRPs):
├── SettingsBlendStrategy (PRP-34.3.1)
├── ClaudeMdBlendStrategy (PRP-34.3.2)
├── MemoriesBlendStrategy (PRP-34.3.3)
├── ExamplesDedupeStrategy (PRP-34.3.4)
└── SimpleStrategy (PRP-34.3.5)
    ├── PRPsMoveAllStrategy
    └── CommandsOverwriteStrategy
```

### 4-Phase Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Blending Orchestrator                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Phase A: DETECTION (PRP-34.2.1)                                │
│    ├─ Scan: PRPs/, examples/, context-engineering/              │
│    ├─ Resolve symlinks                                          │
│    └─ Filter garbage                                            │
│                          ▼                                        │
│  Phase B: CLASSIFICATION (PRP-34.2.2)                           │
│    ├─ Validate CE patterns (Haiku)                              │
│    ├─ Confidence scoring                                        │
│    └─ Filter low-confidence files                               │
│                          ▼                                        │
│  Phase C: BLENDING (PRP-34.3.x)                                 │
│    ├─ For each domain:                                          │
│    │   ├─ Select strategy (can_handle)                          │
│    │   ├─ Create backup (backup_context)                        │
│    │   ├─ Blend content (strategy.blend)                        │
│    │   ├─ Validate output (strategy.validate)                   │
│    │   └─ Remove backup on success                              │
│    └─ Strategies: Settings, CLAUDE.md, Memories, etc.           │
│                          ▼                                        │
│  Phase D: CLEANUP (PRP-34.2.3)                                  │
│    ├─ Verify migration complete                                 │
│    ├─ Remove legacy directories                                 │
│    └─ Preserve standard locations                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Backup-Modify-Restore Pattern

```
┌──────────────────────────────────────────────────────────────┐
│           backup_context(file_path: Path)                     │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│  1. CREATE BACKUP                                             │
│     ├─ file.txt → file.txt.backup                            │
│     └─ Log: "✓ Backed up to file.txt.backup"                 │
│                                                                │
│  2. YIELD BACKUP PATH                                         │
│     └─ User code executes in context                          │
│                                                                │
│  3. SUCCESS PATH                                              │
│     ├─ User code completes                                    │
│     ├─ Remove backup: file.txt.backup deleted                 │
│     └─ Log: "Removed backup file.txt.backup"                  │
│                                                                │
│  4. FAILURE PATH                                              │
│     ├─ Exception raised in user code                          │
│     ├─ Restore: file.txt.backup → file.txt                    │
│     ├─ Log: "✓ Restored from backup file.txt.backup"          │
│     └─ Re-raise exception                                     │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

---

## Success Criteria Summary

✅ **Strategy pattern base class** implemented with ABC
✅ **Backup context manager** creates/removes backups, restores on failure
✅ **CLI entry point** with all options (--all, --phase, --domain, etc.)
✅ **Configuration system** loads blend-config.yml
✅ **Validation framework** checks settings, CLAUDE.md, memories
✅ **Unit tests** pass (≥6 tests, ≥80% coverage)
✅ **Documentation** complete with docstrings and help text
✅ **Dependencies** installed via UV (anthropic, pyyaml, deepdiff)
✅ **No fishy fallbacks** - exceptions bubble up with actionable messages
✅ **KISS principle** - simple, clear code, single responsibility functions
✅ **Real functionality** - no mocked results, actual backup/restore operations

---

## Next Steps After This PRP

1. **PRP-34.2.1**: Detection module (Phase A) - Scan legacy locations
2. **PRP-34.2.2**: Classification module (Phase B) - Validate CE patterns with Haiku
3. **PRP-34.2.3**: Cleanup module (Phase D) - Remove legacy directories safely
4. **PRP-34.3.1**: Settings blending strategy (port from PRP-33 TypeScript)
5. **PRP-34.3.2**: CLAUDE.md blending strategy (Sonnet NL-blend)
6. **PRP-34.3.3**: Memories blending strategy (Haiku similarity + Sonnet merge)
7. **PRP-34.3.4**: Examples dedupe strategy (Haiku semantic deduplication)
8. **PRP-34.3.5**: Simple strategies (PRPs move-all, Commands overwrite)
9. **PRP-34.6**: Integration and E2E tests

**Total Remaining**: 8 PRPs, ~14.5 hours

---

**END OF PRP-34.1.1**
