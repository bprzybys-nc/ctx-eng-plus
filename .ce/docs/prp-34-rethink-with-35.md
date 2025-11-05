# PRP-34 Complete Rethink (Incorporating PRP-35)

**Date**: 2025-11-05
**Status**: Planning - Comprehensive Analysis
**Purpose**: Rethink blending system with legacy detection, pattern validation, and Haiku optimization

---

## SEQUENTIAL THINKING: Problem Decomposition

### Thought 1: What's Actually Wrong with Current Plan?

**Current PRP-34 Assumptions**:
- Files are in known, clean locations (`.claude/`, `.serena/`, `PRPs/`, `examples/`)
- All files are valid CE framework files
- Can directly blend without validation
- Use Sonnet 4.5 for everything (~230K tokens)

**Reality Check (from PRP-35)**:
- Files scattered across multiple locations (root, `.ce/`, `*ce/`, `context-engineering/`)
- Mixed with garbage (non-CE files, user experiments, old drafts)
- Need pattern validation (match CE intro repo structure)
- 230K tokens is expensive - can optimize with Haiku

**Gap**: Missing **DETECTION** and **CLASSIFICATION** phases before blending.

---

### Thought 2: What Are We Actually Building?

Not just a "blending tool" - it's a **FRAMEWORK MIGRATION PIPELINE**:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  DETECTION  │ --> │CLASSIFICATION│ --> │   BLENDING   │
│ (Find files)│     │(Validate CE) │     │(Merge smart) │
└─────────────┘     └──────────────┘     └──────────────┘
      │                    │                     │
      └────────────────────┴─────────────────────┘
                    MIGRATION PIPELINE
```

**Phase A: DETECTION** (New - from PRP-35)
- Scan multiple locations
- Handle legacy naming
- Find `.claude/`, `CLAUDE.md`, symlinks

**Phase B: CLASSIFICATION** (New - from PRP-35)
- Validate CE patterns
- Filter garbage
- Confidence scoring

**Phase C: BLENDING** (Current PRP-34)
- Merge validated files
- Handle conflicts
- Output clean structure

**Conclusion**: Need to expand PRP-34 to include Phases A & B.

---

### Thought 3: Where Do Legacy Files Live?

**Legacy Locations** (from CE evolution history):

1. **Root directories**:
   - `PRPs/` - Old flat structure
   - `examples/` - Old flat structure
   - `CLAUDE.md` - Always root
   - `context-engineering/` - Very old naming

2. **CE directories**:
   - `.ce/` - CE 1.1 structure
   - `.context-engineering/` - CE 1.0
   - `ce/` - Alternative naming
   - `*ce/` - Glob pattern for variations

3. **Claude directories**:
   - `.claude/` - Always standard
   - `.claude/commands/` - Framework commands
   - `.claude/settings.local.json` - Settings

4. **Serena directories**:
   - `.serena/memories/` - CE 1.1
   - `.context-engineering/memories/` - CE 1.0
   - `memories/` - Very old

5. **Symlinks** (mentioned in PRP-35):
   - `CLAUDE.md` → actual file
   - `.claude/` → actual directory

**Detection Strategy**:
```python
SEARCH_PATTERNS = {
    'prps': [
        'PRPs/',
        '.ce/PRPs/',
        'ce/PRPs/',
        'context-engineering/PRPs/',
        '.context-engineering/PRPs/'
    ],
    'examples': [
        'examples/',
        '.ce/examples/',
        'ce/examples/',
        'context-engineering/examples/'
    ],
    'claude_md': [
        'CLAUDE.md',
        '.ce/CLAUDE.md',
        'context-engineering/CLAUDE.md'
    ],
    'commands': [
        '.claude/commands/'
    ],
    'memories': [
        '.serena/memories/',
        '.context-engineering/memories/',
        'memories/'
    ]
}
```

---

### Thought 4: How to Validate CE Files vs Garbage?

**CE File Characteristics** (from github.com/coleam00/context-engineering-intro):

**PRPs**:
```yaml
# YAML header
---
prp_id: PRP-123
title: Feature Name
status: completed|pending|in-progress
created: YYYY-MM-DD
---

# Markdown structure
## Problem
## Solution
## Implementation
```

**Validation Rules**:
- Has YAML frontmatter with `prp_id:`
- PRP ID matches pattern: `PRP-\d+`
- Has standard sections (Problem, Solution, Implementation)
- File name matches: `PRP-\d+-.*\.md`

**Examples**:
```markdown
# Example Title

## Description
Clear description of pattern/workflow

## Usage
Code or command examples

## References
Links to related docs
```

**Validation Rules**:
- Clear title (H1)
- Sections: Description, Usage, etc.
- Code examples present
- File name: `*.md` in examples directory

**Memories** (Serena):
```yaml
---
type: regular|critical|user
category: documentation|pattern|config
tags: [tag1, tag2]
created: YYYY-MM-DDTHH:MM:SSZ
---

# Content
```

**Validation Rules**:
- Has YAML frontmatter with `type:`
- Type is one of: regular, critical, user
- Has category and tags
- Content not empty

**CLAUDE.md**:
- Contains CE framework sections
- Sections marked with `##`
- Has "Communication", "Core Principles", etc.

**Commands** (`.claude/commands/`):
- Markdown files
- Title indicates command purpose
- Contains usage examples or slash command documentation

**Settings** (`.claude/settings.local.json`):
- Valid JSON
- Has `permissions` object
- Contains `allow`, `deny`, `ask` arrays

---

### Thought 5: Garbage Patterns to Filter

**What's NOT CE framework**:

1. **User project files**:
   - `src/`, `lib/`, `app/` code
   - `node_modules/`, `venv/`, `.git/`
   - Build artifacts

2. **Experiments/drafts**:
   - Files without proper headers
   - Incomplete PRPs (no YAML)
   - Random markdown notes

3. **System files**:
   - `.DS_Store`, `Thumbs.db`
   - `*.log`, `*.tmp`
   - Backup files (`*.backup`, `*~`)

4. **Non-CE examples**:
   - Files without structure
   - Just code dumps
   - No descriptions

**Filtering Strategy**:
```python
def is_valid_ce_file(file_path: Path, content: str, domain: str) -> tuple[bool, float]:
    """
    Returns: (is_valid, confidence_score)
    confidence_score: 0.0-1.0
    """
    if domain == 'prp':
        has_yaml = has_yaml_frontmatter(content)
        has_prp_id = 'prp_id:' in content.lower()
        has_structure = has_standard_sections(content, ['Problem', 'Solution'])

        if has_yaml and has_prp_id and has_structure:
            return (True, 1.0)
        elif has_yaml and has_prp_id:
            return (True, 0.7)  # Partial match
        else:
            return (False, 0.0)

    # Similar for other domains...
```

---

### Thought 6: Token Optimization with Haiku

**Current Token Usage (Sonnet 4.5)**:
- CLAUDE.md: ~18K tokens
- Memories (23 files): ~115K tokens
- Examples (13 files): ~97.5K tokens
- **Total**: ~230K tokens

**Where Can We Use Haiku?** (Cheaper, faster, but less capable)

**Haiku Capabilities**:
- Fast classification tasks
- Simple comparisons
- Structured extraction
- Pattern matching

**Haiku Limitations**:
- Less context window (200K vs 200K - same actually)
- Less nuanced understanding
- Might miss subtle semantic similarities

**Optimization Strategy**:

| Task | Current Model | Optimized Model | Reasoning |
|------|---------------|-----------------|-----------|
| **DETECTION** | N/A (new) | Python | Simple file system ops |
| **CLASSIFICATION** | N/A (new) | Haiku | Pattern validation |
| **Settings blending** | Sonnet | Python | Rule-based, no LLM needed |
| **CLAUDE.md blending** | Sonnet | Sonnet | Complex semantic merge - keep quality |
| **Memory blending** | Sonnet | **Haiku → Sonnet** | Haiku for similarity check, Sonnet for merge |
| **Example deduplication** | Sonnet | **Haiku** | Simple comparison task |
| **Conflict resolution** | Sonnet | Sonnet | Needs nuanced understanding |

**Token Savings**:

```
CLASSIFICATION (new):
- Validate ~50 files with Haiku: ~50K tokens

MEMORY BLENDING (optimized):
- Haiku similarity check (23 files): ~23K tokens (fast filter)
- Sonnet merge (5-10 conflicts): ~30K tokens (only when needed)
- Old: 115K tokens
- New: ~53K tokens
- Savings: ~62K tokens (54% reduction)

EXAMPLE DEDUPLICATION (optimized):
- Haiku comparison (13 files): ~40K tokens
- Old: 97.5K tokens
- New: ~40K tokens
- Savings: ~57.5K tokens (59% reduction)

CLAUDE.md (keep Sonnet):
- ~18K tokens (no change - quality critical)

TOTAL:
- Old: ~230K tokens
- New: ~161K tokens (classification + optimized blending)
- Savings: ~69K tokens (30% reduction)
```

**Cost Comparison** (if using API):
- Sonnet: Input $3/M, Output $15/M
- Haiku: Input $0.25/M, Output $1.25/M
- **12x cheaper for classification/simple tasks**

**Quality Trade-off**:
- Classification: Haiku sufficient (pattern matching)
- Simple deduplication: Haiku sufficient (similarity scoring)
- Complex blending: Keep Sonnet (quality critical)

---

### Thought 7: Revised Architecture

**Three-Phase Pipeline**:

```python
# Phase A: DETECTION
detector = LegacyFileDetector()
detected_files = detector.scan_all_locations(target_dir)
# Returns: {
#   'prps': [Path(...), Path(...), ...],
#   'examples': [...],
#   'memories': [...],
#   'claude_md': Path(...),
#   'settings': Path(...),
#   'commands': [...]
# }

# Phase B: CLASSIFICATION (Haiku)
classifier = CEFileClassifier(model='haiku')
validated_files = classifier.validate_all(detected_files)
# Returns: {
#   'prps': [
#     {'path': Path(...), 'valid': True, 'confidence': 0.95},
#     {'path': Path(...), 'valid': False, 'confidence': 0.3, 'reason': 'No YAML'}
#   ],
#   ...
# }

# Phase C: BLENDING (Haiku + Sonnet)
blender = SmartBlender(
    haiku_client=haiku,
    sonnet_client=sonnet
)

# C1: Settings (Python rule-based)
blended_settings = blender.blend_settings(ce_settings, target_settings)

# C2: CLAUDE.md (Sonnet - quality critical)
blended_claude = blender.blend_claude_md(
    ce_claude, target_claude, rules_md,
    model='sonnet'
)

# C3: Memories (Haiku → Sonnet hybrid)
blended_memories = blender.blend_memories(
    ce_memories, target_memories,
    similarity_model='haiku',  # Fast pre-filter
    merge_model='sonnet'       # Quality merge
)

# C4: Examples (Haiku)
deduped_examples = blender.dedupe_examples(
    ce_examples, target_examples,
    model='haiku'  # Simple similarity
)

# C5: PRPs (Python - ID-based)
moved_prps = blender.move_prps(target_prps)

# C6: Commands (Python - overwrite)
copied_commands = blender.copy_commands(ce_commands)
```

---

### Thought 8: Classification Prompt Design

**Haiku Classification Prompt** (fast, cheap):

```python
def classify_prp(content: str) -> dict:
    prompt = f"""Analyze if this is a valid CE framework PRP.

CONTENT:
{content[:1000]}...

CHECK:
1. Has YAML frontmatter with prp_id?
2. PRP ID format: PRP-\\d+?
3. Has sections: Problem, Solution, Implementation?
4. Markdown structure valid?

OUTPUT JSON:
{{
  "valid": true/false,
  "confidence": 0.0-1.0,
  "has_yaml": true/false,
  "has_prp_id": true/false,
  "has_structure": true/false,
  "issues": ["list of issues if invalid"]
}}
"""

    response = haiku_client.messages.create(
        model="claude-3-5-haiku-20241022",
        max_tokens=500,  # Small output
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
```

**Token Usage**: ~1K input + ~100 output = ~1.1K tokens per file
**Time**: <1s per file (Haiku is fast)
**Cost**: ~$0.001 per file (practically free with Claude Pro quota)

---

### Thought 9: Hybrid Strategy for Memory Blending

**Problem**: 23 memories × Sonnet = expensive
**Solution**: Haiku pre-filter + Sonnet merge

```python
def blend_memories_hybrid(
    ce_memories: List[Memory],
    target_memories: List[Memory]
) -> List[Memory]:
    """
    Step 1: Haiku similarity check (fast, cheap)
    Step 2: Sonnet merge only for conflicts (slow, quality)
    """

    results = []

    for ce_mem in ce_memories:
        # Find target memory with same name
        target_mem = find_by_name(target_memories, ce_mem.name)

        if not target_mem:
            # No conflict - copy CE version
            results.append(ce_mem)
            continue

        # Step 1: Haiku similarity check
        similarity = check_similarity_haiku(ce_mem.content, target_mem.content)

        if similarity > 0.95:
            # Nearly identical - use CE version
            results.append(ce_mem)
        elif similarity < 0.3:
            # Very different - ask user
            choice = ask_user(ce_mem, target_mem)
            results.append(choice)
        else:
            # Similar but different - Sonnet merge
            merged = merge_with_sonnet(ce_mem, target_mem)
            results.append(merged)

    return results
```

**Token Breakdown**:
- Haiku checks (23 files): ~23K tokens (all files)
- Sonnet merges (assume 5 conflicts): ~25K tokens (only conflicts)
- **Total**: ~48K tokens (vs 115K with pure Sonnet = 58% savings)

---

### Thought 10: Confidence Scoring System

**Why**: Not all validations are binary (valid/invalid)

**Confidence Levels**:

| Score | Meaning | Action |
|-------|---------|--------|
| 1.0 | Perfect CE file | Auto-include |
| 0.7-0.9 | Likely CE file | Auto-include with warning |
| 0.4-0.6 | Uncertain | Ask user |
| 0.0-0.3 | Likely garbage | Auto-exclude with log |

**Scoring Factors**:

```python
def calculate_confidence(file_checks: dict) -> float:
    """
    file_checks = {
        'has_yaml': bool,
        'has_required_fields': bool,
        'has_structure': bool,
        'content_quality': float,
        'file_name_matches': bool
    }
    """
    score = 0.0

    if file_checks['has_yaml']:
        score += 0.3
    if file_checks['has_required_fields']:
        score += 0.3
    if file_checks['has_structure']:
        score += 0.2
    score += file_checks['content_quality'] * 0.15
    if file_checks['file_name_matches']:
        score += 0.05

    return min(score, 1.0)
```

**User Interaction** (uncertain files):

```
⚠️  Uncertain file detected:

File: PRPs/old-feature.md
Confidence: 0.55

Issues:
  ✓ Has YAML frontmatter
  ✓ Has PRP ID: PRP-42
  ✗ Missing standard sections
  ? Content seems incomplete

Include this file? [Y]es / [N]o / [V]iew content
>
```

---

### Thought 11: Revised CLI Interface

```bash
# Full pipeline with detection
uv run ce blend --all --scan

# Scan only (detection + classification)
uv run ce blend --scan-only --report

# Blend with pre-scanned files
uv run ce blend --all --skip-scan

# Use fast mode (Haiku for everything possible)
uv run ce blend --all --fast

# Use quality mode (Sonnet for everything)
uv run ce blend --all --quality

# Hybrid mode (default - Haiku + Sonnet)
uv run ce blend --all

# Report detected files
uv run ce blend --scan-only
```

**Output Example**:

```
🔍 CE Framework Migration Tool

Phase A: DETECTION
==================
Scanning for legacy files...

PRPs found:
  ✓ PRPs/ (5 files)
  ✓ .ce/PRPs/ (2 files)
  ✓ context-engineering/PRPs/ (3 files - old structure)
  Total: 10 PRP files detected

Examples found:
  ✓ examples/ (8 files)
  ✓ .ce/examples/ (3 files)
  Total: 11 example files detected

Memories found:
  ✓ .serena/memories/ (5 files)
  Total: 5 memory files detected

CLAUDE.md found:
  ✓ ./CLAUDE.md

Settings found:
  ✓ .claude/settings.local.json

Commands found:
  ✓ .claude/commands/ (3 files)

Phase B: CLASSIFICATION
========================
Validating files with Haiku...

PRPs:
  ✓ PRP-1-feature.md (confidence: 1.0)
  ✓ PRP-2-bugfix.md (confidence: 0.95)
  ⚠️  old-notes.md (confidence: 0.4) - No YAML frontmatter
  ✗ draft.md (confidence: 0.1) - Not a valid PRP

  8/10 files valid (2 excluded)

Examples:
  ✓ workflow-pattern.md (confidence: 1.0)
  ✓ tool-usage.md (confidence: 0.9)
  ⚠️  random-notes.md (confidence: 0.5) - Incomplete structure

  9/11 files valid (2 uncertain)

  ❓ Review uncertain files? [Y/n]: Y

Uncertain file: examples/random-notes.md
Confidence: 0.5
Reason: Incomplete structure, unclear purpose

Include? [Y]es / [N]o / [V]iew
> N

Phase C: BLENDING
==================
Processing with hybrid strategy (Haiku + Sonnet)...

Settings:
  ✓ Rule-based merge (Python)
  ✓ 28 tools allowed, 59 denied

CLAUDE.md:
  ⏳ Blending with Sonnet (quality mode)...
  ✓ Framework sections merged
  ✓ Preserved [PROJECT] sections
  ✓ 89 → 72 lines (19% reduction)

Memories (5 files):
  ⏳ Similarity check with Haiku...
  • code-style-conventions.md: 95% similar → Use CE version
  • testing-standards.md: 45% similar → Merge with Sonnet
  ⏳ Merging conflict with Sonnet...
  ✓ 5 files processed (3 copied, 2 merged)

Examples (9 files):
  ⏳ Deduplication with Haiku...
  ✓ 9 files checked (2 duplicates skipped)
  ✓ 7 unique examples copied

PRPs (8 files):
  ✓ ID-based deduplication (Python)
  ✓ Added 'type: user' headers
  ✓ Moved to .ce/PRPs/executed/

Commands (3 files):
  ✓ Backed up existing
  ✓ Overwritten with 11 framework commands

================================================================================
✅ Migration complete!
================================================================================

Summary:
  • Detected: 39 files across 6 domains
  • Validated: 35 files (4 excluded as garbage)
  • Blended: 35 files processed

Token usage:
  • Classification: 45K tokens (Haiku)
  • Blending: 116K tokens (53K Haiku + 63K Sonnet)
  • Total: 161K tokens (30% savings vs pure Sonnet)

Time: 2m 34s

Backups created:
  • .claude/settings.local.json.backup
  • CLAUDE.md.backup
  • .serena/memories.backup/
  • .claude/commands.backup/

Excluded files (logged to .ce/migration-excluded.log):
  • PRPs/draft.md (confidence: 0.1)
  • examples/random-notes.md (user declined)
  • ...

Rollback: uv run ce blend --rollback
```

---

### Thought 12: Updated Sub-PRP Breakdown

**PRP-34: Core Framework + Detection (5 hours)** ← Expanded
- Strategy pattern base classes
- Configuration system (YAML)
- CLI entry point
- Backup/rollback system
- **NEW**: Legacy file detection
- **NEW**: Multi-location scanning
- **NEW**: Symlink handling

**PRP-34.1: Classification System (3 hours)** ← New
- Haiku-based validation
- Confidence scoring
- Pattern matching (CE intro repo)
- Garbage filtering
- User interaction for uncertain files

**PRP-34.2: Settings Blending Strategy (2 hours)**
- Port PRP-33 TypeScript logic to Python
- Rule-based structural merge (3 rules)
- No LLM needed (pure Python)

**PRP-34.3: CLAUDE.md Blending Strategy (3 hours)**
- Sonnet-based blending (keep quality)
- RULES.md-aware blending
- Section parsing and merging
- Conflict detection

**PRP-34.4: Memory Blending Hybrid Strategy (3.5 hours)** ← Modified
- Haiku similarity pre-filter
- Sonnet merge for conflicts
- YAML header blending
- Confidence-based routing

**PRP-34.5: Example Deduplication (2.5 hours)** ← Modified
- Haiku-based comparison (not Sonnet)
- Semantic similarity scoring
- User prompts for similar examples
- Hash-based fallback

**PRP-34.6: Simple Operations (1.5 hours)**
- PRPs dedupe-move (ID-based)
- Commands overwrite
- Python-only (no LLM)

**PRP-34.7: Integration + Testing (3 hours)** ← Expanded
- Update INITIALIZATION.md
- Update syntropy-mcp init spec
- End-to-end testing with legacy detection
- Documentation updates

**Total: 23.5 hours** (was 18.5 hours)
**Added: 5 hours** for detection + classification

---

### Thought 13: Token Usage Breakdown (Final)

**Phase A: Detection** (Python - 0 tokens)
- File system scanning
- Symlink resolution
- Path normalization

**Phase B: Classification** (Haiku - 45K tokens)
- Validate ~35 files
- ~1.3K tokens per file average
- Fast, cheap pattern matching

**Phase C: Blending**

| Domain | Model | Input | Output | Total |
|--------|-------|-------|--------|-------|
| Settings | Python | 0 | 0 | 0 |
| CLAUDE.md | Sonnet | 10K | 8K | 18K |
| Memories (similarity) | Haiku | 23K | 5K | 28K |
| Memories (merge 5 files) | Sonnet | 20K | 15K | 35K |
| Examples | Haiku | 35K | 5K | 40K |
| PRPs | Python | 0 | 0 | 0 |
| Commands | Python | 0 | 0 | 0 |

**Total**:
- Classification: 45K tokens (Haiku)
- Blending: 121K tokens (75K Haiku + 46K Sonnet)
- **Grand Total: 166K tokens**

**Comparison**:
- Old plan (pure Sonnet): 230K tokens
- New plan (hybrid): 166K tokens
- **Savings: 64K tokens (28% reduction)**
- **Quality: Maintained** (Sonnet for complex tasks)

---

### Thought 14: Quality vs Speed Trade-offs

**Where Haiku is SUFFICIENT**:
✓ Classification (pattern matching)
✓ Similarity scoring (numerical comparison)
✓ Simple deduplication (hash + basic comparison)
✓ Structured extraction (YAML parsing assistance)

**Where Sonnet is REQUIRED**:
✓ Semantic merging (CLAUDE.md sections)
✓ Conflict resolution (contradicting content)
✓ Complex blending (complementary information)
✓ Nuanced understanding (subtle differences)

**Hybrid Approach Benefits**:
- 28% token reduction
- Faster classification (Haiku is 2-3x faster)
- Maintained quality for critical tasks
- User has control (--fast, --quality flags)

---

### Thought 15: Edge Cases to Handle

**Symlinks**:
```python
def resolve_symlink(path: Path) -> Path:
    """Follow symlinks to actual file"""
    if path.is_symlink():
        return path.resolve()
    return path
```

**Circular references**:
```python
visited = set()
def scan_directory(path: Path, visited: set):
    real_path = path.resolve()
    if real_path in visited:
        return  # Skip circular ref
    visited.add(real_path)
    # ... scan
```

**Permissions errors**:
```python
try:
    content = path.read_text()
except PermissionError:
    logger.warning(f"Cannot read {path} - permission denied")
    return None
```

**Binary files** (skip):
```python
def is_text_file(path: Path) -> bool:
    try:
        path.read_text()
        return True
    except UnicodeDecodeError:
        return False
```

**Large files** (>1MB):
```python
def should_process(path: Path) -> bool:
    size = path.stat().st_size
    if size > 1_000_000:  # 1MB
        logger.warning(f"{path} too large - skipping")
        return False
    return True
```

---

## FINAL RECOMMENDATIONS

### What to Include in Revised PRP-34-INITIAL

1. **Add Detection Phase (Phase A)**:
   - Multi-location scanning
   - Legacy path support
   - Symlink handling

2. **Add Classification Phase (Phase B)**:
   - Haiku validation
   - Confidence scoring
   - Garbage filtering
   - CE pattern matching

3. **Optimize Blending Phase (Phase C)**:
   - Hybrid Haiku + Sonnet
   - Keep Sonnet for quality-critical
   - Use Haiku for simple tasks

4. **Update Token Analysis**:
   - 166K tokens (was 230K)
   - 28% reduction
   - Still zero marginal cost (Claude Pro)

5. **Add Sub-PRP for Classification**:
   - PRP-34.1: Classification System (3 hours)
   - Implement Haiku validation
   - Pattern matching logic

6. **Update Total Effort**:
   - 23.5 hours (was 18.5 hours)
   - 5 additional hours for detection + classification

### What NOT to Change

1. **Settings blending** - Keep Python rule-based (already optimal)
2. **CLAUDE.md blending** - Keep Sonnet (quality critical)
3. **Core architecture** - Strategy pattern is solid
4. **CLI interface** - Just add --scan flags

### Implementation Priority

1. **PRP-34**: Core + Detection (highest priority - foundation)
2. **PRP-34.1**: Classification (required before blending)
3. **PRP-34.2**: Settings (independent, can parallelize)
4. **PRP-34.3**: CLAUDE.md (depends on core)
5. **PRP-34.4**: Memories hybrid (depends on 34.3 LLM client)
6. **PRP-34.5**: Examples (depends on 34.3 LLM client)
7. **PRP-34.6**: Simple ops (independent, can parallelize with 34.2)
8. **PRP-34.7**: Integration (depends on all above)

---

## CONCLUSION

**Should we rewrite PRP-34-INITIAL.md?**

**YES** - Add:
- Phase A: Detection (new section)
- Phase B: Classification (new sub-PRP)
- Haiku optimization (update existing sections)
- Hybrid strategy details (update existing sections)
- Revised token analysis (166K vs 230K)
- Updated effort estimate (23.5 hours)

**Keep existing sections but enhance them with hybrid approach.**

This creates a complete, production-ready migration pipeline that:
- Handles legacy installations intelligently
- Filters garbage automatically
- Optimizes token usage (28% reduction)
- Maintains quality where it matters
- Provides clear user feedback
- Is fully reversible (backups)

**Ready to integrate into PRP-34-INITIAL.md.**
