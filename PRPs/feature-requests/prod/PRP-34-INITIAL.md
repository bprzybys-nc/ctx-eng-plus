# PRP-34 INITIAL: Generalized Framework Blending System

**Created**: 2025-11-05
**Status**: Planning
**Complexity**: High
**Estimated Effort**: 12-16 hours

---

## PROBLEM STATEMENT

Current framework initialization uses **domain-specific ad-hoc merge logic** scattered across multiple locations. Each data domain (memories, CLAUDE.md, settings, PRPs, examples) has different merge requirements, but no unified framework exists.

### Current Pain Points

1. **No legacy file detection** - Assumes files in known locations (PRPs/, examples/, .serena/)
2. **No validation** - Can't distinguish CE framework files from garbage (reports, summaries, drafts)
3. **Settings blending** implemented in PRP-33 (TypeScript in syntropy-mcp) - needs Python port
4. **CLAUDE.md blending** manual process documented in INITIALIZATION.md Phase 4
5. **Serena memories** no blending strategy - manual deduplication required
6. **Examples/PRPs** no deduplication - can copy duplicates
7. **Commands** overwrite strategy but no validation
8. **No cleanup** - Old legacy directories left behind after migration

**Problem**: Not a blending tool - it's a **complete migration pipeline** (detect → classify → blend → cleanup) with no reusable framework.

---

## SOLUTION OVERVIEW

Create a **complete migration pipeline** (`tools/ce/blend.py`) with four phases:

**Phase A: DETECTION** - Scan legacy locations for CE files
**Phase B: CLASSIFICATION** - Validate CE patterns, filter garbage
**Phase C: BLENDING** - Copy framework + import non-contradictory target content
**Phase D: CLEANUP** - Remove old organization after successful migration

Uses **Claude SDK** (Haiku + Sonnet hybrid) for intelligent classification and blending, with domain-specific strategies.

### Key Insight: Four-Phase Pipeline

```
Phase A: DETECTION (Python)
  └─ Scan: PRPs/, examples/, context-engineering/, .serena/, .claude/
  └─ Handle symlinks
  └─ Resolve paths

Phase B: CLASSIFICATION (Haiku - fast/cheap)
  └─ Validate CE patterns
  └─ Filter garbage (reports, summaries, initials)
  └─ Confidence scoring (0.0-1.0)

Phase C: BLENDING (Hybrid Haiku + Sonnet)
  ├─ Settings: Rule-based (Python)
  ├─ CLAUDE.md: Copy ours + import non-contradictory (Sonnet)
  ├─ Memories: Copy ours + import non-contradictory (Haiku similarity → Sonnet merge)
  ├─ Examples: NL-dedupe (Haiku)
  ├─ PRPs: Move all (Python, no dedupe - different projects can have same IDs)
  └─ Commands: Overwrite (Python)

Phase D: CLEANUP (Python)
  └─ Remove PRPs/ (after migration to .ce/PRPs/)
  └─ Remove examples/ (after migration to .ce/examples/)
  └─ Remove context-engineering/ (after migration)
  └─ Keep .claude/, .serena/, CLAUDE.md (standard locations)
```

**Blending Philosophy**: "Copy ours, import theirs where not contradictory"

### Architecture Principles

1. **Strategy Pattern**: Each domain has pluggable merge strategy
2. **Claude SDK Integration**: Use same tokens as Claude Code for NL-based blending
3. **Declarative Configuration**: Define merge rules in YAML/JSON
4. **Reversible Operations**: Create backups before blending
5. **Validation Gates**: Verify output integrity post-blend

---

## PHASE A: DETECTION (Legacy File Scanner)

### Purpose

Scan multiple legacy locations for CE framework files. Handle CE 1.0 → CE 1.1 migration paths.

### Legacy Locations (Exact)

**Root directories**:
- `PRPs/` - Old flat structure
- `examples/` - Old flat structure
- `CLAUDE.md` - Always root (may be symlink)
- `context-engineering/PRPs/` - CE 1.0 structure
- `context-engineering/examples/` - CE 1.0 structure

**CE directories**:
- `.ce/` - CE 1.1 structure (our TARGET, don't scan)
- `context-engineering/` - CE 1.0 (legacy source)
- `ce/` - Alternative naming (rare)

**Claude directories**:
- `.claude/` - Standard location (may be symlink)
- `.claude/commands/` - Framework commands
- `.claude/settings.local.json` - Settings

**Serena directories**:
- `.serena/memories/` - CE 1.1 only

### Detection Algorithm

```python
class LegacyFileDetector:
    """Scan project for CE framework files in legacy locations"""

    SEARCH_PATTERNS = {
        'prps': [
            'PRPs/',                        # Root flat
            'context-engineering/PRPs/'     # CE 1.0
        ],
        'examples': [
            'examples/',                    # Root flat
            'context-engineering/examples/' # CE 1.0
        ],
        'claude_md': ['CLAUDE.md'],
        'settings': ['.claude/settings.local.json'],
        'commands': ['.claude/commands/'],
        'memories': ['.serena/memories/']
    }

    def scan_all(self, target_dir: Path) -> Dict[str, List[Path]]:
        """Scan all legacy locations, resolve symlinks"""
        results = {}

        for domain, patterns in self.SEARCH_PATTERNS.items():
            files = []
            for pattern in patterns:
                path = target_dir / pattern
                if path.exists():
                    # Resolve symlinks
                    real_path = path.resolve()
                    files.extend(self._collect_files(real_path))

            results[domain] = files

        return results

    def _collect_files(self, path: Path) -> List[Path]:
        """Collect .md files recursively, skip garbage"""
        if path.is_file():
            return [path] if path.suffix == '.md' else []

        files = []
        for item in path.rglob('*.md'):
            if not self._is_garbage(item):
                files.append(item)
        return files

    def _is_garbage(self, path: Path) -> bool:
        """Filter out non-CE files"""
        name = path.name.lower()

        # Garbage patterns
        garbage = [
            'report', 'initial', 'summary',
            'analysis', 'plan', '.backup',
            '~', '.tmp', '.log'
        ]

        return any(g in name for g in garbage)
```

---

## PHASE B: CLASSIFICATION (CE Pattern Validator)

### Purpose

Validate detected files are actual CE framework files, not user experiments or garbage. Use **Haiku** for fast, cheap pattern matching.

### Garbage Patterns (CRITICAL - Must Exclude)

**Meta documents** (planning, not content):
- `*REPORT*.md` - Build reports
- `*INITIAL*.md` - Planning documents
- `*-summary.md`, `*-analysis.md` - Summaries
- `*PLAN*.md` - Plans

**Other garbage**:
- System files (`.DS_Store`, `*.log`, `*.tmp`)
- Backups (`*.backup`, `*~`)
- User drafts (no structure)

### CE Pattern Validation

**PRPs** (older versions may lack YAML):
```python
def validate_prp(content: str) -> tuple[bool, float]:
    """
    Validate PRP file. Older PRPs may not have YAML header.

    Checks (in order of importance):
    1. Has PRP ID in content (PRP-\d+) - REQUIRED
    2. Has YAML frontmatter - NICE TO HAVE
    3. Has standard sections - NICE TO HAVE
    4. File name matches PRP-\d+ - NICE TO HAVE
    """
    score = 0.0

    # REQUIRED: Has PRP ID anywhere in content
    if re.search(r'PRP-\d+', content):
        score += 0.5  # Core requirement
    else:
        return (False, 0.0)  # Not a PRP

    # NICE TO HAVE: YAML header
    if has_yaml_frontmatter(content):
        score += 0.2

    # NICE TO HAVE: Standard sections
    sections = ['problem', 'solution', 'implementation']
    found = sum(1 for s in sections if s in content.lower())
    score += (found / len(sections)) * 0.2

    # NICE TO HAVE: Proper structure
    if len(content) > 100:  # Not just stub
        score += 0.1

    return (score >= 0.6, score)
```

**Examples**:
```python
def validate_example(content: str) -> tuple[bool, float]:
    """
    Validate example file

    Checks:
    1. Has clear title (H1)
    2. Has sections (H2)
    3. Has code or command examples
    4. Has description
    """
    score = 0.0

    # Has H1 title
    if re.search(r'^#\s+.+', content, re.MULTILINE):
        score += 0.3

    # Has H2 sections
    if re.search(r'^##\s+.+', content, re.MULTILINE):
        score += 0.2

    # Has code blocks
    if '```' in content:
        score += 0.3

    # Has substantial content
    if len(content) > 200:
        score += 0.2

    return (score >= 0.5, score)
```

**Memories**:
```python
def validate_memory(content: str) -> tuple[bool, float]:
    """
    Validate Serena memory

    Checks:
    1. Has YAML frontmatter with 'type:'
    2. Type is valid (regular|critical|user)
    3. Has category
    4. Has content
    """
    score = 0.0

    if not has_yaml_frontmatter(content):
        return (False, 0.0)

    yaml_data = parse_yaml_frontmatter(content)

    if 'type' in yaml_data:
        score += 0.4
        if yaml_data['type'] in ['regular', 'critical', 'user']:
            score += 0.2

    if 'category' in yaml_data:
        score += 0.2

    if len(content) > 100:
        score += 0.2

    return (score >= 0.6, score)
```

### Classification with Haiku

```python
def classify_with_haiku(file_path: Path, content: str, domain: str) -> dict:
    """
    Use Haiku for fast, cheap classification

    Returns: {
        'valid': bool,
        'confidence': float,
        'issues': List[str]
    }
    """

    # First: Python-based quick checks
    if domain == 'prp':
        is_valid, confidence = validate_prp(content)
        if not is_valid:
            return {'valid': False, 'confidence': confidence, 'issues': ['Not a valid PRP']}

    # Second: Haiku validation for uncertain cases
    if confidence < 0.9:
        prompt = f"""Validate if this is a CE framework {domain} file.

CONTENT (first 500 chars):
{content[:500]}

DOMAIN RULES:
{get_domain_rules(domain)}

OUTPUT JSON:
{{
  "valid": true/false,
  "confidence": 0.0-1.0,
  "issues": ["list of issues"]
}}
"""
        response = haiku_client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    return {'valid': True, 'confidence': confidence, 'issues': []}
```

---

## PHASE C: BLENDING STRATEGIES BY DOMAIN

### Blending Philosophy

**"Copy ours, import theirs where not contradictory"**

1. **Start with framework version** (authoritative)
2. **Import target content** that doesn't contradict framework
3. **Ask user** for contradictions
4. **Deduplicate & denoise** to compact output

### 1. Settings JSON (Rule-Based - Python)

**Location**: PRP-33 syntropy-mcp implementation
**Strategy**: Structural merge with 3 rules
**Complexity**: Medium
**Philosophy**: Copy ours (CE settings) + import target permissions where not contradictory

```python
# Strategy: Structural merge
# Rules:
#   1. CE deny list takes precedence - if CE denies a tool, remove from target allow
#   2. Merge CE entries to target lists (deduplicate)
#   3. Ensure each tool appears in ONE list only (CE list membership wins)

def blend_settings(ce_settings: dict, target_settings: dict) -> dict:
    """
    Copy CE framework settings, import target-specific permissions.

    Process:
    1. Start with CE settings as base (authoritative)
    2. Add target allow/ask entries if not contradicting CE deny list
    3. Deduplicate across lists
    4. Ensure single membership (CE list wins if conflict)
    """
    # Already implemented in PRP-33 (TypeScript)
    # Need Python port for ce tools
    pass
```

**Action**: Port TypeScript logic to `tools/ce/blend.py` (reusable)
**Blending**: Framework deny list = law, merge non-conflicting target permissions

---

### 2. CLAUDE.md (NL-Blend with RULES.md)

**Strategy**: Natural language-based section merging
**Complexity**: High
**Tool**: Claude SDK (Sonnet for quality)
**Philosophy**: Copy ours (CE CLAUDE.md) + import target project-specific sections

#### Current Process (Manual)

From INITIALIZATION.md Phase 4:
1. Backup existing CLAUDE.md
2. Identify framework sections vs project sections
3. Manual copy-paste framework sections
4. Preserve project-specific sections (e.g., `## [PROJECT]`)
5. Manual deduplication

#### Proposed Automated Process

```python
def blend_claude_md(
    ce_claude: str,           # Framework CLAUDE.md (authoritative)
    ce_rules: str,            # Framework RULES.md (invariants)
    target_claude: str,       # Target project CLAUDE.md
    llm_client: Anthropic     # Claude SDK client
) -> str:
    """
    Blending algorithm (COPY OURS + IMPORT NON-CONTRADICTORY):
    1. Parse framework CLAUDE.md into sections (base)
    2. Parse RULES.md for framework invariants (law)
    3. Parse target CLAUDE.md into sections
    4. For each framework section:
       - Copy framework version (authoritative)
       - Check if target has complementary content
       - If complementary: Import target content
       - If contradicting: Skip target content (or ask user)
    5. Import target-only sections (marked [PROJECT])
    6. Deduplicate content (Claude SDK)
    7. Denoise and format (lists, tables, mermaid)
    8. Return blended document
    """
    pass
```

**Blending Rules**:
- **Framework sections = base** (RULES.md as law)
- **Target project sections preserved** if marked `## [PROJECT]` or unique
- **Contradicting content** → Framework wins (or ask user)
- **Complementary content** → Merge both
- **Output**: Compact, structured (lists/tables/mermaid where appropriate)

---

### 3. Serena Memories (NL-Blend)

**Strategy**: Intelligent content merging with deduplication
**Complexity**: High
**Tool**: Claude SDK (Haiku similarity check → Sonnet merge if needed)
**Philosophy**: Copy ours (CE memories) + import target non-contradictory content

#### Challenge

- Framework: 23 memories (6 critical + 17 regular)
- Target: May have 0-N existing memories
- Conflicts: Same filename, different content

#### Proposed Process

```python
def blend_memory(
    ce_memory: str,           # Framework memory content (authoritative)
    target_memory: str,       # Target memory content (if exists)
    memory_name: str,         # Filename (e.g., code-style-conventions.md)
    llm_client: Anthropic
) -> str:
    """
    Blending algorithm (COPY OURS + IMPORT NON-CONTRADICTORY):
    1. Start with framework memory as base
    2. Parse both memories into sections
    3. Use Haiku to check similarity (fast, cheap)
    4. If >90% similar: Use framework version (skip target)
    5. If contradicting: Use framework version (or ask user)
    6. If complementary: Use Sonnet to merge both sections
    7. Deduplicate repeated information
    8. Format output (structured markdown)
    9. Return blended memory
    """
    pass
```

**YAML Header Blending**:
```yaml
---
type: regular           # Framework type wins (authoritative)
category: documentation # Framework category wins
tags: [tag1, tag2]      # Merge tags from both (dedupe)
created: "2025-11-04"   # Use earlier date
updated: "2025-11-05"   # Use later date (most recent edit)
source: "blended"       # Mark as blended (or "framework" if no merge)
---
```

**Conflict Resolution**:
- **Framework critical memories**: Always use framework version (no blending)
- **Framework regular memories**: Copy ours + import complementary target content
- **Target-only memories**: Preserve as-is (add `type: user` header)

**Optimization**: Use Haiku for similarity checks (12x cheaper), Sonnet only for actual merges

---

### 4. Examples (NL-Dedupe)

**Strategy**: Semantic deduplication using Claude SDK
**Complexity**: High
**Tool**: Claude SDK (Haiku for fast comparison)
**Philosophy**: Copy ours (CE examples) + skip if target has equivalent

**Challenge**: Framework workflow package contains 13 examples. Target project may have similar (but not identical) examples. Simple hash won't detect semantic duplicates.

```python
def dedupe_examples(
    ce_examples: List[Path],     # Framework examples/ (to copy)
    target_examples: List[Path], # Target .ce/examples/ (existing)
    llm_client: Anthropic
) -> Dict[str, str]:
    """
    Algorithm (COPY OURS + SKIP IF DUPLICATE):
    1. Load all target examples (if any)
    2. For each framework example:
       - Check if identical file exists (hash) → Skip (already have it)
       - Check if semantically similar exists (Haiku) → Skip if >90% similar
       - If unique → Copy framework example
    3. Return mapping of decisions

    Semantic similarity check (Haiku - fast, cheap):
    - Compare example titles/descriptions
    - Compare code snippets
    - If >90% similar: Skip framework example (target has equivalent)
    - If <90% similar: Copy framework example
    """
    pass
```

**Example Comparison Prompt (Haiku)**:
```python
prompt = f"""Compare these two examples for semantic similarity.

FRAMEWORK EXAMPLE:
Title: {fw_title}
Content: {fw_content[:500]}...

TARGET EXAMPLE:
Title: {target_title}
Content: {target_content[:500]}...

Are these examples covering the same topic/pattern?
Answer JSON: {{"similarity": 0.0-1.0, "decision": "COPY_FRAMEWORK|SKIP_DUPLICATE"}}
"""
```

**Deduplication Strategy**:
- **Hash match**: Skip framework example (already exists)
- **>90% similar**: Skip framework example (target has equivalent)
- **<90% similar**: Copy framework example (different content)

**Source**: Framework workflow package (13 files, 85KB) needs deduplication against target `.ce/examples/`

**Note**: This is critical because workflow package is extracted during init, and we need to avoid duplicate examples cluttering the examples directory.

**Optimization**: Use Haiku for all comparisons (12x cheaper than Sonnet, sufficient for similarity checks)

---

### 5. PRPs (Move-All)

**Strategy**: Move all target PRPs (no deduplication)
**Complexity**: Low
**Tool**: Python
**Philosophy**: Copy all user PRPs (different projects can have same IDs)

```python
def move_prps(
    target_prps_dir: str,     # Target project PRPs/
    target_ce_dir: str        # Target .ce/PRPs/
) -> Dict[str, str]:
    """
    Algorithm:
    1. List all PRPs in target project (PRPs/, context-engineering/PRPs/)
    2. For each PRP:
       - Parse status from content (executed/feature-requests)
       - Move to .ce/PRPs/executed/ or .ce/PRPs/feature-requests/
       - Skip if exact file already exists (hash match)
    3. Add 'type: user' YAML header if missing
    4. Return mapping of moved files

    No ID-based deduplication - different projects can have PRP-1, PRP-2, etc.
    Framework PRPs (PRP-0) already in .ce/PRPs/executed/system/ (from infrastructure package)
    """
    pass
```

**YAML Header Addition**:
```yaml
---
prp_id: PRP-1              # Keep original ID (not USER-001)
title: User Feature
status: completed
created: "2025-11-04"
source: target-project
type: user                 # Added during migration
---
```

**No Deduplication**: Move all target PRPs
- Framework PRPs are in `.ce/PRPs/executed/system/` (PRP-0, etc.)
- Target PRPs go to `.ce/PRPs/executed/` or `.ce/PRPs/feature-requests/`
- Same IDs OK (PRP-1 in target ≠ PRP-1 in another project)
- Only skip if exact file exists (hash match, same content)

---

### 6. Commands (Overwrite)

**Strategy**: Replace existing with framework version
**Complexity**: Low
**Tool**: Python

```python
def overwrite_commands(
    ce_commands_dir: str,     # Framework .claude/commands/
    target_commands_dir: str  # Target .claude/commands/
) -> List[str]:
    """
    Algorithm:
    1. Backup existing commands to .claude/commands.backup/
    2. For each framework command:
       - Copy to target .claude/commands/
       - Overwrite if exists
    3. Return list of overwritten files

    No blending - framework commands are versioned
    """
    pass
```

**Rationale**: Framework commands are canonical, should not be modified by users
**Safety**: Backup to `.backup/` directory before overwrite

---

## PHASE D: CLEANUP (Remove Legacy Organization)

### Purpose

After successful migration and blending, remove old directory structures to avoid confusion. Keep standard locations (`.claude/`, `.serena/`, `CLAUDE.md`).

### Cleanup Strategy

```python
def cleanup_legacy_dirs(target_dir: Path, dry_run: bool = False) -> Dict[str, bool]:
    """
    Remove legacy directories after migration.

    Algorithm:
    1. Verify migration completed successfully (all files moved/blended)
    2. For each legacy directory:
       - Check if empty or only has migrated files
       - If safe to remove: Delete directory
       - If contains unmigrated files: Warn user
    3. Return mapping of deleted directories

    IMPORTANT: Only remove directories if migration verified.
    """

    legacy_dirs = [
        'PRPs/',                    # Moved to .ce/PRPs/
        'examples/',                # Moved to .ce/examples/
        'context-engineering/'      # CE 1.0 structure (moved to .ce/)
    ]

    results = {}

    for dir_path in legacy_dirs:
        full_path = target_dir / dir_path

        if not full_path.exists():
            results[dir_path] = True  # Already gone
            continue

        # Verify migration completed for this directory
        if not verify_migration_complete(dir_path, target_dir):
            logger.warning(f"Migration not verified for {dir_path}, skipping cleanup")
            results[dir_path] = False
            continue

        # Check for unmigrated files
        unmigrated = find_unmigrated_files(full_path)
        if unmigrated:
            logger.warning(f"Found {len(unmigrated)} unmigrated files in {dir_path}")
            logger.warning(f"Files: {', '.join(f.name for f in unmigrated[:5])}")
            results[dir_path] = False
            continue

        # Safe to remove
        if not dry_run:
            shutil.rmtree(full_path)
            logger.info(f"Removed {dir_path}")
        results[dir_path] = True

    return results
```

### Verification Before Cleanup

```python
def verify_migration_complete(legacy_dir: str, target_dir: Path) -> bool:
    """
    Verify all files from legacy directory have been migrated.

    Checks:
    1. Count of files in legacy directory
    2. Count of migrated files in .ce/
    3. Validate no critical files left behind
    """

    if legacy_dir == 'PRPs/':
        # Check all PRPs moved to .ce/PRPs/
        legacy_prps = list((target_dir / 'PRPs').rglob('*.md'))
        ce_prps = list((target_dir / '.ce/PRPs').rglob('*.md'))

        # Should have at least as many PRPs in .ce/ as in legacy
        return len(ce_prps) >= len(legacy_prps)

    elif legacy_dir == 'examples/':
        # Check examples copied to .ce/examples/
        legacy_examples = list((target_dir / 'examples').rglob('*.md'))
        ce_examples = list((target_dir / '.ce/examples').rglob('*.md'))

        return len(ce_examples) > 0  # At least some examples migrated

    elif legacy_dir == 'context-engineering/':
        # Check CE 1.0 structure migrated
        ce_11_exists = (target_dir / '.ce').exists()
        return ce_11_exists

    return False
```

### Directories to Keep (Standard Locations)

**DO NOT REMOVE** these directories (they are standard, not legacy):
- `.claude/` - Standard Claude Code location
- `.serena/` - Standard Serena location
- `CLAUDE.md` - Standard root file
- `.ce/` - CE 1.1 target location (our new structure)

### Cleanup Output

```
🧹 Phase D: Cleanup Legacy Directories
======================================================================

Checking legacy directories for cleanup:
  ✓ PRPs/                    - Verified migration (5 files → .ce/PRPs/)
  ✓ examples/                - Verified migration (13 files → .ce/examples/)
  ✓ context-engineering/     - Verified migration (CE 1.0 → CE 1.1)

Removing legacy directories:
  🗑️  PRPs/ (removed)
  🗑️  examples/ (removed)
  🗑️  context-engineering/ (removed)

Standard locations preserved:
  ✅ .claude/ (kept)
  ✅ .serena/ (kept)
  ✅ CLAUDE.md (kept)
  ✅ .ce/ (kept - our target structure)

======================================================================
✅ Cleanup complete! Legacy directories removed.
```

### Safety Features

1. **Dry-run mode**: Show what would be removed without actually deleting
2. **Migration verification**: Only remove if migration confirmed successful
3. **Unmigrated file warnings**: Alert user if files found that weren't migrated
4. **Standard location preservation**: Never remove `.claude/`, `.serena/`, `CLAUDE.md`, `.ce/`
5. **Backup reminder**: Remind user that backups were created during blending

### Rollback Handling

If cleanup fails or user wants to rollback:

```bash
# Rollback blending (restores backups, does NOT restore removed directories)
uv run ce blend --rollback

# Manual recovery (if directories removed but need to restore)
# User must restore from git history or backups made before blend
git checkout HEAD -- PRPs/ examples/ context-engineering/
```

**Note**: Cleanup is **irreversible** (removed directories cannot be automatically restored). Users should ensure blending completed successfully before allowing cleanup.

---

## PROPOSED ARCHITECTURE

### Core Components

```
tools/ce/
├── blend.py              # Main CLI entry point (4-phase pipeline)
├── blending/
│   ├── __init__.py
│   ├── core.py           # Base blending framework (4-phase orchestration)
│   ├── detection.py      # Phase A: Legacy file scanner
│   ├── classification.py # Phase B: CE pattern validator (Haiku)
│   ├── cleanup.py        # Phase D: Legacy directory removal
│   ├── strategies/
│   │   ├── __init__.py
│   │   ├── settings.py   # Settings JSON blending (port from PRP-33)
│   │   ├── claude_md.py  # CLAUDE.md blending (Sonnet)
│   │   ├── memories.py   # Serena memories blending (Haiku + Sonnet)
│   │   ├── examples.py   # Examples NL-dedupe (Haiku)
│   │   ├── simple.py     # PRPs move, Commands overwrite
│   │   └── base.py       # Abstract strategy interface
│   ├── llm_client.py     # Claude SDK wrapper (Haiku + Sonnet)
│   └── validation.py     # Post-blend validation
└── pyproject.toml        # Add anthropic SDK dependency
```

### Strategy Pattern Implementation

```python
# tools/ce/blending/strategies/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pathlib import Path

class BlendStrategy(ABC):
    """Base class for all blending strategies"""

    @abstractmethod
    def can_handle(self, domain: str) -> bool:
        """Check if strategy can handle this domain"""
        pass

    @abstractmethod
    def blend(
        self,
        framework_content: Any,
        target_content: Optional[Any],
        context: Dict[str, Any]
    ) -> Any:
        """
        Blend framework and target content

        Args:
            framework_content: Framework version (always present)
            target_content: Target version (may be None)
            context: Additional context (file paths, options, etc.)

        Returns:
            Blended content
        """
        pass

    @abstractmethod
    def validate(self, blended_content: Any) -> bool:
        """Validate blended content integrity"""
        pass
```

---

## CLAUDE SDK INTEGRATION

### Why Claude SDK?

1. **Same Token Pool**: Uses Claude Pro subscription quota (zero marginal cost)
2. **Already Authenticated**: Same API key as Claude Code uses
3. **Natural Language Understanding**: Best tool for semantic content blending
4. **Context Window**: Can handle full CLAUDE.md (8K tokens) + RULES.md (2K tokens)
5. **Structured Output**: Can enforce output format (markdown sections, YAML)
6. **Quality**: Human-level understanding of document structure and semantics

### Implementation

```python
# tools/ce/blending/llm_client.py

import os
from anthropic import Anthropic

class BlendingLLM:
    """Claude SDK client for blending operations"""

    def __init__(self):
        # Uses same API key as Claude Code
        self.client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-5-20250929"  # Same as Claude Code

    def blend_content(
        self,
        framework_content: str,
        target_content: str,
        rules: str,
        domain: str
    ) -> str:
        """
        Use Claude to blend two documents

        Prompt strategy:
        1. Provide framework content (authority)
        2. Provide target content (to preserve)
        3. Provide rules (invariants)
        4. Request structured output
        """

        prompt = f"""You are blending framework and project documentation.

FRAMEWORK CONTENT (authoritative):
{framework_content}

FRAMEWORK RULES (must follow):
{rules}

TARGET PROJECT CONTENT (preserve where possible):
{target_content}

TASK:
Blend these documents following these rules:
1. Framework sections take precedence (RULES are law)
2. Preserve target project-specific sections (marked [PROJECT])
3. If content conflicts, preserve framework version
4. If content is complementary, merge both
5. Deduplicate repeated information
6. Format output with:
   - Clear section headers
   - Lists where appropriate
   - Tables for structured data
   - Mermaid diagrams for flows (quote node text with special chars)
7. No vital information lost

Output ONLY the blended content (valid markdown).
"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text
```

---

## CONFIGURATION SYSTEM

### Blend Config (YAML)

```yaml
# .ce/blend-config.yml

domains:
  settings:
    strategy: rule-based
    source: .claude/settings.local.json
    backup: true
    rules:
      - ce_deny_wins
      - merge_lists
      - single_membership

  claude_md:
    strategy: nl-blend
    source: CLAUDE.md
    framework_rules: .ce/RULES.md
    backup: true
    llm_model: claude-sonnet-4-5-20250929
    max_tokens: 8192

  memories:
    strategy: nl-blend
    source: .serena/memories/
    backup: true
    llm_model: claude-sonnet-4-5-20250929
    conflict_resolution: ask-user

  examples:
    strategy: dedupe-copy
    source: examples/
    destination: .ce/examples/
    dedup_method: content-hash

  prps:
    strategy: move-all
    source: PRPs/
    destination: .ce/PRPs/
    dedup_method: content-hash  # Only skip if exact file exists
    add_user_header: true
    note: "Different projects can have same PRP IDs - no ID-based deduplication"

  commands:
    strategy: overwrite
    source: .claude/commands/
    backup: true
    backup_location: .claude/commands.backup/
```

---

## CLI INTERFACE

### Usage

```bash
# Full migration pipeline (all 4 phases)
cd .ce/tools
uv run ce blend --all

# Individual phases
uv run ce blend --phase detect       # Phase A only
uv run ce blend --phase classify     # Phase B only
uv run ce blend --phase blend        # Phase C only
uv run ce blend --phase cleanup      # Phase D only

# Blend specific domain
uv run ce blend --domain settings
uv run ce blend --domain claude_md
uv run ce blend --domain memories

# Modes
uv run ce blend --all --dry-run      # Show what would be done (all phases)
uv run ce blend --all --interactive  # Ask before each phase
uv run ce blend --all --fast         # Skip NL-dedupe, use Haiku only
uv run ce blend --all --scan         # Scan mode (detect + classify only, no blending)
uv run ce blend --all --quality      # Quality mode (use Sonnet for all LLM calls)

# Cleanup control
uv run ce blend --all --skip-cleanup # Skip Phase D (keep legacy dirs)
uv run ce blend --cleanup-only       # Run Phase D only (requires prior blend)

# Rollback (restore backups, does NOT restore removed directories)
uv run ce blend --rollback --domain settings
uv run ce blend --rollback --all
```

### Output

```
🔀 CE Framework Migration Pipeline (4 Phases)
======================================================================

📋 Phase A: DETECTION (Legacy File Scanner)
======================================================================

Scanning legacy locations...
  ✓ PRPs/                    - Found 5 PRPs
  ✓ examples/                - Found 3 examples
  ✓ context-engineering/     - Found CE 1.0 structure (12 PRPs, 8 examples)
  ✓ .claude/settings.local.json - Found
  ✓ .claude/commands/        - Found 3 commands
  ✓ CLAUDE.md                - Found (symlink → resolved)
  ✓ .serena/memories/        - Found 8 memories

Total detected: 51 files across 7 domains

======================================================================
🔍 Phase B: CLASSIFICATION (CE Pattern Validator)
======================================================================

Validating CE files with Haiku...

PRPs validation:
  ✓ PRP-1-feature.md         - Valid (confidence: 0.95)
  ✓ PRP-2-bugfix.md          - Valid (confidence: 0.88)
  ⚠️  old-notes.md           - GARBAGE (not a PRP, confidence: 0.12)
  ✓ 15 PRPs validated (14 valid, 1 garbage filtered)

Examples validation:
  ✓ tool-usage-example.md    - Valid (confidence: 0.92)
  ⚠️  REPORT-summary.md      - GARBAGE (meta document, excluded)
  ✓ 11 examples validated (10 valid, 1 garbage filtered)

Memories validation:
  ✓ code-style-conventions.md - Valid (confidence: 1.0)
  ✓ 8 memories validated (8 valid, 0 garbage)

Total classified: 46 valid CE files (5 garbage filtered)

======================================================================
🔀 Phase C: BLENDING (Copy Ours + Import Non-Contradictory)
======================================================================

Domains to process:
  ✓ settings      (rule-based)
  ✓ claude_md     (nl-blend, Sonnet)
  ✓ memories      (nl-blend, Haiku + Sonnet, 23 framework + 8 target)
  ✓ examples      (nl-dedupe, Haiku, 13 framework + 10 target)
  ✓ prps          (move-all, 14 target)
  ✓ commands      (overwrite, 11 framework)

Processing settings...
  ✓ Backed up to .claude/settings.local.json.backup
  ✓ Applied 3 blending rules (CE deny takes precedence)
  ✓ Validation passed
  ✓ Settings blended (28 tools allowed, 59 denied)

Processing claude_md...
  ⏳ Calling Sonnet for NL-blend (quality mode)...
  ✓ Backed up to CLAUDE.md.backup
  ✓ Framework sections copied (authoritative)
  ✓ Imported 2 target [PROJECT] sections
  ✓ Deduplicated 3 repeated sections
  ✓ CLAUDE.md blended (89 lines → 72 lines, 19% reduction)

Processing memories...
  ⏳ Checking similarity with Haiku (fast)...
  ✓ code-style-conventions.md - 95% similar → Using framework version
  ⏳ testing-standards.md - 45% similar → Merging with Sonnet...
  ⚠️  Conflict detected in testing-standards.md
      Framework: "Use pytest exclusively"
      Target: "Use unittest framework"

  ❓ Which to keep? [F]ramework / [T]arget / [M]erge / [S]kip
  > F

  ✓ 23 framework memories processed
  ✓ 8 target memories: 3 skipped (>90% similar), 3 merged, 2 conflicts resolved
  ✓ Total: 26 memories in .serena/ (23 framework, 3 unique target preserved)

Processing examples...
  ⏳ Checking similarity with Haiku (fast)...
  ✓ 13 framework examples
  ✓ 10 target examples: 2 duplicates (>90% similar), 8 unique
  ✓ Copied 21 examples to .ce/examples/ (13 framework + 8 unique target)

Processing prps...
  ✓ 14 PRPs in target project (5 root, 9 context-engineering/)
  ✓ Added 'type: user' headers to all
  ✓ Moved to .ce/PRPs/executed/

Processing commands...
  ✓ Backed up 3 existing commands to .claude/commands.backup/
  ✓ Overwritten with 11 framework commands

======================================================================
🧹 Phase D: CLEANUP (Remove Legacy Directories)
======================================================================

Verifying migration before cleanup...
  ✓ PRPs/                    - Migration verified (14 files → .ce/PRPs/)
  ✓ examples/                - Migration verified (21 files → .ce/examples/)
  ✓ context-engineering/     - Migration verified (CE 1.0 → CE 1.1)

Removing legacy directories...
  🗑️  PRPs/ (removed)
  🗑️  examples/ (removed)
  🗑️  context-engineering/ (removed)

Standard locations preserved:
  ✅ .claude/ (kept)
  ✅ .serena/ (kept)
  ✅ CLAUDE.md (kept)
  ✅ .ce/ (kept - our target structure)

======================================================================
✅ Migration complete! (4/4 phases)
======================================================================

Summary:
  • Phase A: 51 files detected across 7 domains
  • Phase B: 46 valid CE files (5 garbage filtered)
  • Phase C: All domains blended
    - Settings: 28 tools allowed, 59 denied
    - CLAUDE.md: 72 lines (19% reduction)
    - Memories: 26 total (23 framework + 3 unique target)
    - Examples: 21 total (13 framework + 8 unique target)
    - PRPs: 14 moved to .ce/PRPs/
    - Commands: 11 framework commands installed
  • Phase D: 3 legacy directories removed

Token usage (from Claude Pro quota):
  • Classification (Haiku): ~15K tokens
  • CLAUDE.md (Sonnet): ~18K tokens
  • Memories (Haiku + Sonnet): ~63K tokens
  • Examples (Haiku): ~40K tokens
  • Total: ~136K tokens (~2-3 Claude Code conversations)

Backups created:
  • .claude/settings.local.json.backup
  • CLAUDE.md.backup
  • .serena/memories.backup/
  • .claude/commands.backup/

Rollback: uv run ce blend --rollback
Note: Rollback restores backups but does NOT restore removed directories
      (use git to restore: git checkout HEAD -- PRPs/ examples/ context-engineering/)
```

---

## SPLIT INTO SUB-PRPS

### PRP-34: Core Blending Framework (4 hours)

**Deliverables**:
- Strategy pattern base classes
- Configuration system (YAML)
- CLI entry point (`tools/ce/blend.py`)
- Backup/rollback system
- Validation framework

**Files**:
- `tools/ce/blend.py`
- `tools/ce/blending/core.py`
- `tools/ce/blending/strategies/base.py`
- `tools/ce/blending/validation.py`
- `.ce/blend-config.yml`

---

### PRP-34.1: Settings Blending Strategy (2 hours)

**Deliverables**:
- Port PRP-33 TypeScript logic to Python
- Rule-based structural merge (3 rules)
- JSON validation
- Integration tests

**Files**:
- `tools/ce/blending/strategies/settings.py`
- `tools/tests/test_blend_settings.py`

**Dependencies**: PRP-34 core

---

### PRP-34.2: CLAUDE.md Blending Strategy (3 hours)

**Deliverables**:
- Claude SDK integration
- RULES.md-aware blending
- Section parsing and merging
- Conflict detection

**Files**:
- `tools/ce/blending/llm_client.py`
- `tools/ce/blending/strategies/claude_md.py`
- `tools/tests/test_blend_claude_md.py`

**Dependencies**: PRP-34 core

---

### PRP-34.3: Serena Memories Blending Strategy (3 hours)

**Deliverables**:
- Claude SDK-based content merging
- YAML header blending
- Conflict resolution (ask-user mode)
- Deduplication

**Files**:
- `tools/ce/blending/strategies/memories.py`
- `tools/tests/test_blend_memories.py`

**Dependencies**: PRP-34 core, PRP-34.2 (LLM client)

---

### PRP-34.4: Examples NL-Dedupe Strategy (3 hours)

**Deliverables**:
- Claude SDK-based semantic deduplication
- Example comparison logic
- User prompts for similar examples
- Integration with workflow package extraction

**Files**:
- `tools/ce/blending/strategies/examples.py`
- `tools/tests/test_blend_examples.py`

**Dependencies**: PRP-34 core, PRP-34.2 (LLM client)

---

### PRP-34.5: Simple Operations (PRPs, Commands) (1.5 hours)

**Deliverables**:
- Move-all strategy (PRPs - no ID deduplication)
- Overwrite strategy (commands)
- Hash-based deduplication (skip if exact file exists)

**Files**:
- `tools/ce/blending/strategies/simple.py`
- `tools/tests/test_simple_strategies.py`

**Dependencies**: PRP-34 core

**Note**: PRPs use move-all (not ID-based dedupe) because different projects can have same IDs (PRP-1, PRP-2, etc.)

---

### PRP-34.6: Integration with Init Workflow (2 hours)

**Deliverables**:
- Update INITIALIZATION.md to use blending tool
- Update syntropy-mcp init procedure
- End-to-end testing
- Documentation updates

**Files**:
- Update `examples/INITIALIZATION.md`
- Update `.ce/docs/syntropy-mcp-init-specification.md`
- Integration tests

**Dependencies**: All PRP-34.x complete

---

## SYMMETRIES & CODE COMPACTION

### Identified Patterns

| Pattern | Instances | Generalization Opportunity |
|---------|-----------|----------------------------|
| **Backup-Modify-Restore** | Settings, CLAUDE.md, Memories, Commands | Create `BackupContext` manager |
| **Parse-Blend-Validate** | Settings, CLAUDE.md, Memories | Create `BlendPipeline` abstraction |
| **Dedupe by Hash** | Examples, PRPs | Create `HashDedupeStrategy` base class |
| **YAML Header Ops** | Memories, PRPs | Create `YAMLHeaderManager` utility |
| **File List + Filter** | Examples, PRPs, Commands | Create `FileCollector` utility |
| **LLM Prompt Templates** | CLAUDE.md, Memories | Create `PromptTemplates` library |

**Note**: PRPs only use hash-based deduplication (skip if exact file exists). No ID-based deduplication because different projects can have same PRP IDs (PRP-1, PRP-2, etc.).

### Proposed Utilities

```python
# tools/ce/blending/utils.py

from contextlib import contextmanager
from pathlib import Path
from typing import Generator

@contextmanager
def backup_context(file_path: Path) -> Generator[Path, None, None]:
    """
    Context manager for backup-modify-restore pattern

    Usage:
        with backup_context(Path("CLAUDE.md")) as backup:
            # Modify file
            modify_file()
            # If exception, auto-restore from backup
    """
    backup_path = file_path.with_suffix(file_path.suffix + '.backup')

    # Backup
    if file_path.exists():
        shutil.copy2(file_path, backup_path)

    try:
        yield backup_path
        # Success - remove backup
        if backup_path.exists():
            backup_path.unlink()
    except Exception:
        # Failure - restore backup
        if backup_path.exists():
            shutil.copy2(backup_path, file_path)
        raise
```

---

## RESEARCH: PROVEN BLENDING PATTERNS

### 3-Way Merge (Git-style)

Used in version control systems:
```
Base → Framework version (authoritative)
Ours → Target project version
Theirs → Framework update

Result: Merge ours + theirs, prefer base on conflict
```

**Applicability**: Good for CLAUDE.md sections, memories

### Operational Transformation (OT)

Used in collaborative editing (Google Docs):
- Transform operations to maintain consistency
- Resolve concurrent edits

**Applicability**: Overkill for our use case (one-way merge)

### Conflict-Free Replicated Data Types (CRDTs)

Used in distributed systems:
- Commutative operations
- Eventual consistency

**Applicability**: Not needed (not distributed)

### Semantic Merge (NL-based)

Use LLM to understand content semantics:
- Identify duplicate information
- Merge complementary content
- Resolve contradictions with context

**Applicability**: ✅ **BEST FIT** for CLAUDE.md and memories

### Structural Merge (AST-based)

Parse documents into abstract syntax tree:
- Merge at node level
- Preserve structure

**Applicability**: Good for settings JSON (already implemented in PRP-33)

---

## EXAMPLES

### Example 1: CLAUDE.md Blending

**Framework Section**:
```markdown
## Quick Commands

```bash
cd tools
uv run ce validate --level all
uv run ce context health
```
```

**Target Section**:
```markdown
## Quick Commands

```bash
cd tools
pytest tests/ -v
```
```

**Blended Output** (Claude SDK):
```markdown
## Quick Commands

```bash
cd tools

# Validation & health
uv run ce validate --level all
uv run ce context health

# Testing
pytest tests/ -v
```
```

---

### Example 2: Memory Blending (Conflict)

**Framework Memory** (code-style-conventions.md):
```markdown
## Function Size

Functions should be ≤50 lines for readability.
```

**Target Memory** (code-style-conventions.md):
```markdown
## Function Size

Keep functions under 100 lines. Longer functions are acceptable if well-documented.
```

**Conflict Detected** → Ask User:
```
❓ Conflict in code-style-conventions.md:

Framework: "Functions should be ≤50 lines"
Target:    "Functions under 100 lines acceptable"

Which to keep? [F]ramework / [T]arget / [M]erge / [S]kip
> M

Please provide merge guidance:
> "Prefer 50 lines, but allow up to 100 with documentation"
```

**Blended Output** (Claude SDK with guidance):
```markdown
## Function Size

Functions should be ≤50 lines for readability. Longer functions (up to 100 lines) are acceptable if well-documented with clear section comments.
```

---

## DEPENDENCIES

### Python Packages

```toml
# tools/pyproject.toml

[project]
dependencies = [
    "anthropic>=0.40.0",   # Claude SDK
    "pyyaml>=6.0",         # Config parsing
    "deepdiff>=6.0",       # Content comparison
    # ... existing deps
]
```

### Environment Variables

```bash
# Required for Claude SDK
export ANTHROPIC_API_KEY="sk-ant-..."  # Same as Claude Code uses
```

---

## VALIDATION STRATEGY

### Post-Blend Checks

| Domain | Validation | Failure Action |
|--------|------------|----------------|
| **Settings** | Valid JSON, all CE tools in one list | Restore backup |
| **CLAUDE.md** | Valid markdown, all framework sections present | Restore backup |
| **Memories** | Valid YAML headers, ≥23 files | Restore backup |
| **Examples** | All files readable, no duplicates | Warn only |
| **PRPs** | Valid PRP IDs, unique IDs | Warn only |
| **Commands** | All 11 framework commands present | Restore backup |

---

## QUOTA USAGE ANALYSIS

### Claude SDK Token Usage (from Claude Pro Plan)

**Optimized with Haiku + Sonnet Hybrid Approach**

| Domain | Model | Avg Input Tokens | Avg Output Tokens | Total Tokens |
|--------|-------|------------------|-------------------|--------------|
| **Phase B: Classification** | Haiku | ~35K | ~10K | **~45K** |
| - PRPs validation (14 files) | Haiku | ~14K | ~4K | ~18K |
| - Examples validation (10 files) | Haiku | ~10K | ~3K | ~13K |
| - Memories validation (8 files) | Haiku | ~8K | ~2K | ~10K |
| - CLAUDE.md validation | Haiku | ~3K | ~1K | ~4K |
| **Settings** | Python | 0 | 0 | **0** (rule-based) |
| **CLAUDE.md** | Sonnet | ~10K (CE + target + rules) | ~8K | **~18K** |
| **Memories (23 framework + 8 target)** | Haiku + Sonnet | | | **~63K** |
| - Similarity checks (31 files) | Haiku | ~31K | ~8K | ~39K |
| - Merges (5 files, complementary only) | Sonnet | ~15K | ~9K | ~24K |
| **Examples (13 framework + 10 target)** | Haiku | ~32K | ~8K | **~40K** |
| - Similarity checks (130 pairs worst-case) | Haiku | ~26K | ~4K | ~30K |
| - Deduplication decisions | Haiku | ~6K | ~4K | ~10K |
| **PRPs** | Python | 0 | 0 | **0** (ID-based dedupe) |
| **Commands** | Python | 0 | 0 | **0** (overwrite) |
| **Total per init** | | ~107K | ~59K | **~166K tokens** |

**Optimization Breakdown**:
- **Original estimate** (all Sonnet): ~230K tokens
- **Optimized** (Haiku + Sonnet hybrid): ~166K tokens
- **Reduction**: 64K tokens (28% reduction)
- **Cost savings** (if paid): ~$0.40 per init (Haiku is 12x cheaper than Sonnet)

**Haiku vs Sonnet Selection**:
| Task | Model | Rationale |
|------|-------|-----------|
| Classification | Haiku | Pattern matching, confidence scoring (simple) |
| Similarity checks | Haiku | Comparing content (fast, sufficient accuracy) |
| CLAUDE.md blending | Sonnet | Quality critical, framework documentation |
| Memory merges | Sonnet | Only when complementary content found (rare) |
| Settings blending | Python | Rule-based, no LLM needed |

**Notes**:
- **Zero marginal cost**: Uses Claude Pro subscription quota (already paid)
- **Token quota**: Claude Pro includes generous token allowance
- **One-time usage**: ~166K tokens per project initialization
- **Context**: Claude Code typical conversation uses 50-100K tokens
- **Equivalent**: ~2-3 Claude Code conversations per init
- **Time savings**: Automates 45+ minutes of manual work
- **Value**: Prevents human error in manual blending, ensures consistency

**Quota Considerations**:
- **--fast mode**: Use Haiku for CLAUDE.md too (~148K tokens, 10% faster)
- **--quality mode**: Use Sonnet for all LLM calls (~230K tokens, higher quality)
- **--scan mode**: Skip blending (Phase A + B only, ~45K tokens)
- Can skip examples NL-dedupe if quota constrained (fall back to hash-based)

---

## TIMELINE

### Development Schedule

| PRP | Phase | Duration | Dependencies |
|-----|-------|----------|--------------|
| PRP-34 | Core framework | 4 hours | None |
| PRP-34.1 | Settings strategy | 2 hours | PRP-34 |
| PRP-34.2 | CLAUDE.md strategy | 3 hours | PRP-34 |
| PRP-34.3 | Memories strategy | 3 hours | PRP-34, PRP-34.2 |
| PRP-34.4 | Examples NL-dedupe | 3 hours | PRP-34, PRP-34.2 |
| PRP-34.5 | Simple strategies (PRPs, Commands) | 1.5 hours | PRP-34 |
| PRP-34.6 | Integration | 2 hours | All above |
| **Total** | | **18.5 hours** | |

**Parallelization**: PRP-34.1 and PRP-34.5 can run in parallel after PRP-34 complete. PRP-34.2, 34.3, 34.4 share LLM client dependency (sequential after 34.2).

---

## SUCCESS CRITERIA

**Phase A: Detection**
- ✅ Scans all legacy locations (PRPs/, examples/, context-engineering/, .claude/, .serena/)
- ✅ Resolves symlinks correctly
- ✅ Filters garbage files (REPORT, INITIAL, summary, analysis)
- ✅ Returns comprehensive file inventory

**Phase B: Classification**
- ✅ Validates PRPs without requiring YAML headers (older versions)
- ✅ Validates examples with confidence scoring
- ✅ Validates memories with YAML header checks
- ✅ Uses Haiku for fast, cheap classification
- ✅ Filters all garbage patterns correctly

**Phase C: Blending**
- ✅ All 6 domains have working blend strategies
- ✅ Claude SDK integration tested (Haiku + Sonnet hybrid)
- ✅ Settings blending produces same output as PRP-33 implementation
- ✅ CLAUDE.md blending preserves all framework sections, imports [PROJECT] sections
- ✅ Memories blending: Haiku similarity → Sonnet merge (only when needed)
- ✅ Examples NL-dedupe with Haiku prevents similar duplicates
- ✅ PRPs move-all strategy preserves all user PRPs (no deduplication by ID)
- ✅ Commands overwrite creates backups
- ✅ Blending philosophy: "Copy ours + import non-contradictory" implemented correctly

**Phase D: Cleanup**
- ✅ Verifies migration before cleanup
- ✅ Removes legacy directories safely (PRPs/, examples/, context-engineering/)
- ✅ Preserves standard locations (.claude/, .serena/, CLAUDE.md, .ce/)
- ✅ Warns on unmigrated files
- ✅ Supports dry-run mode

**General**
- ✅ CLI tool works end-to-end (all 4 phases)
- ✅ Integration tests pass (per-phase and full pipeline)
- ✅ Documentation updated (INITIALIZATION.md, syntropy-mcp spec)
- ✅ Token usage optimized (~166K tokens from Claude Pro quota per init, 28% reduction)
- ✅ All user corrections integrated (exact locations, garbage filtering, blending philosophy)

---

## RISKS

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Phase A: Detection** |
| Symlink resolution fails | Medium | Test with real symlinks, handle circular symlinks |
| Garbage filter too aggressive | Medium | Conservative patterns, dry-run mode to preview |
| **Phase B: Classification** |
| Older PRPs incorrectly filtered | High | Don't require YAML, check additional characteristics (PRP ID in content) |
| Haiku misclassifies files | Medium | Confidence scoring, manual review for low confidence (<0.7) |
| **Phase C: Blending** |
| Claude Pro quota exhaustion | Medium | `--fast` mode (Haiku only), `--scan` mode (skip blending) |
| LLM blending produces incorrect output | High | Validation gates, diff preview, manual review mode |
| Conflict resolution UX confusing | Medium | Clear prompts, examples, dry-run mode |
| Performance too slow (LLM calls) | Medium | Use Haiku (12x faster), parallel processing, progress bars |
| Backup/restore failures | High | Atomic operations, verify backups before blend |
| API key not configured | Medium | Clear error message, link to Claude Code auth docs |
| **Phase D: Cleanup** |
| Premature directory removal | Critical | Verify migration first, dry-run mode, require confirmation |
| Unmigrated files deleted | Critical | Check for unmigrated files, warn user, abort cleanup |
| Cannot restore removed dirs | High | Warn user cleanup is irreversible, suggest git commit before cleanup |

---

## QUESTIONS FOR CONSIDERATION

**Phase A: Detection**
1. **Symlink Handling**: Should we resolve symlinks or preserve them? (Lean: Resolve for scanning, warn if circular)
2. **Garbage Patterns**: Are the garbage patterns comprehensive? Missing any common naming patterns?
3. **Detection Output**: Should `--scan` mode output JSON for programmatic consumption?

**Phase B: Classification**
4. **Confidence Threshold**: Use 0.6 for PRPs, 0.5 for examples - are these too low/high?
5. **Manual Review**: Auto-skip files with confidence <0.3, or always ask user?
6. **Haiku Accuracy**: Is Haiku sufficient for classification, or should we use Sonnet for edge cases?

**Phase C: Blending**
7. **Quota Management**: Should we add `--skip-examples-nlblend` flag to save ~40K tokens if quota low?
8. **Fallback Strategy**: What if Claude SDK unavailable? Fall back to simple hash-based dedupe?
9. **Caching**: Should we cache LLM responses for identical inputs (e.g., same memory content)?
10. **Parallel Processing**: Blend memories in parallel (23 files = 23 LLM calls) to reduce latency?
11. **User Confirmation**: Always show diffs before applying LLM-generated blends?
12. **Quota Feedback**: Display running token count during blending?
13. **Fast Mode**: `--fast` mode uses Haiku for CLAUDE.md too - acceptable quality tradeoff?

**Phase D: Cleanup**
14. **Cleanup Timing**: Always run cleanup, or require explicit `--cleanup` flag?
15. **Safety Confirmation**: Require user confirmation before removing directories, or trust verification?
16. **Partial Cleanup**: Allow cleanup of specific directories (e.g., only remove `PRPs/`)?
17. **Backup Suggestion**: Force user to commit to git before cleanup, or just warn?

---

## NEXT STEPS

1. **Review & Approve** this INITIAL.md
2. **Use /batch-gen-prp** to decompose into executable PRPs:
   ```bash
   /batch-gen-prp PRPs/feature-requests/PRP-34-INITIAL.md
   ```
   This will:
   - Parse this INITIAL into phases
   - Build dependency graph (Phase A → B → C → D)
   - Assign stages for parallel execution
   - Create PRPs with format PRP-34.X.Y (X = stage, Y = order)
   - Generate Linear issues automatically

3. **Expected PRP Structure** (batch-gen-prp will determine exact breakdown):
   - **Stage 1**: Core framework (detection, classification, cleanup modules)
   - **Stage 2**: Blending strategies (can parallelize: settings, PRPs, commands)
   - **Stage 3**: LLM-based strategies (sequential: LLM client → CLAUDE.md → memories → examples)
   - **Stage 4**: Integration & documentation

4. **Implement in Stages** with validation gates between stages

---

**Status**: Ready for batch PRP generation
**Estimated Total Effort**: 12-16 hours (split across multiple PRPs by batch-gen-prp)
**Expected Impact**:
- Automates 45+ min manual blending work per project initialization
- Prevents human error in file detection, classification, and blending
- ONE workflow that adapts to any situation (0 files or 1000 files)
- Handles all cases: new projects, existing PRPs/examples, CE 1.0 migrations, partial installs

**Token Usage**: ~166K tokens per init (from Claude Pro quota, zero marginal cost)
- 28% reduction vs original estimate (230K → 166K via Haiku optimization)
- Equivalent to 2-3 Claude Code conversations
- Zero marginal cost (uses Claude Pro subscription quota)
