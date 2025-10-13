# PRP YAML Header Schema

**Version**: 3.0 (Unified: KISS + Self-Healing)
**Based on**: Certinia proven template + ctx-eng-plus standards
**Last Updated**: 2025-01-15

---

## Overview

All PRPs use a standardized YAML header for metadata tracking. The header is compact (12-20 lines) and supports both simple KISS-mode PRPs and complex Self-Healing PRPs.

---

## Required Fields

### Core Identification

```yaml
name: "Feature Title (Clear, Action-Oriented)"
description: "1-sentence description of what this PRP implements"
prp_id: "PRP-X.Y"
status: "ready"  # ready|in_progress|executed|validated|archived
```

**Field Descriptions**:

- `name`: Human-readable feature title, action-oriented (e.g., "Add Git Status Command")
- `description`: Single sentence summarizing what the PRP accomplishes
- `prp_id`: Unique identifier following PRP-X.Y format (X=major, Y=minor)
- `status`: Current lifecycle state of the PRP

**Valid Status Values**:

- `ready`: PRP is ready for execution
- `in_progress`: Currently being implemented
- `executed`: Implementation complete, validation passed
- `validated`: Post-execution validation confirmed
- `archived`: Superseded or no longer relevant

### Planning Metadata

```yaml
priority: "MEDIUM"  # HIGH|MEDIUM|LOW
confidence: "8/10"  # 1-10 scale for one-pass success probability
effort_hours: 4.0  # Realistic estimate with phase breakdown
risk: "LOW"  # LOW|MEDIUM|HIGH
```

**Field Descriptions**:

- `priority`: Business priority for implementation
- `confidence`: Estimated probability of one-pass success (1=low, 10=high)
- `effort_hours`: Total estimated effort in hours (decimal for fractional hours)
- `risk`: Technical risk level

### Tracking

```yaml
version: 1
created_date: "2025-MM-DDTHH:MM:SSZ"
last_updated: "2025-MM-DDTHH:MM:SSZ"
```

**Field Descriptions**:

- `version`: Integer version number (increment on major revisions)
- `created_date`: ISO-8601 timestamp of PRP creation
- `last_updated`: ISO-8601 timestamp of last modification

---

## Optional Fields

### Task Integration

```yaml
task_id: ""  # Optional: Linear/Jira/GitHub issue (e.g., "ENG-123", "#456")
```

Link to external task tracker for project management integration.

### Dependency Management

```yaml
dependencies: []  # ["PRP-X.0"] if depends on other PRPs
parent_prp: null  # PRP-X.0 if part of series
```

**Field Descriptions**:

- `dependencies`: Array of PRP IDs that must be completed first
- `parent_prp`: Parent PRP ID if this is part of a series (e.g., PRP-2.1's parent is PRP-2.0)

**Example - Series PRP**:

```yaml
prp_id: "PRP-8.7"
parent_prp: "PRP-8.0"  # Part of PRP-8.x series
dependencies: ["PRP-8.3", "PRP-8.5"]  # Builds on these PRPs
```

### Context Engineering Integration

```yaml
context_memories: []  # Optional: ["memory_name"] Serena memories (if using Serena MCP)
context_sync:  # Optional: if using Context Engineering framework
  ce_updated: false
  serena_updated: false
```

**Field Descriptions**:

- `context_memories`: Array of Serena MCP memory names to load before execution
- `context_sync`: Tracks whether CE and Serena contexts are synchronized
  - `ce_updated`: Boolean - CE examples/docs updated with learnings from this PRP
  - `serena_updated`: Boolean - Serena memories updated with patterns from this PRP

**When to Use**:

- Skip these fields for projects not using Context Engineering framework or Serena MCP
- Set to empty arrays `[]` and `false` values if using CE but not updating contexts

### Meeting Evidence

```yaml
meeting_evidence:  # Optional: for requirements validation
  - source: "docs/meetings/file.md"
    lines: "100-110"
    timestamp: "15:07-15:22"  # Optional
    quote: "Direct quote validating requirement"
```

**Field Descriptions**:

- `source`: Path to meeting notes or requirements document
- `lines`: Line range containing the relevant quote
- `timestamp`: Optional video/audio timestamp (HH:MM-HH:MM format)
- `quote`: Direct quote validating the requirement or design decision

**When to Use**:

- Complex PRPs where requirements traceability is important
- PRPs implementing features from stakeholder meetings
- PRPs where design decisions need to reference specific discussions

**Multiple Evidence Example**:

```yaml
meeting_evidence:
  - source: "docs/meetings/2025-01-10-planning.md"
    lines: "45-52"
    timestamp: "10:15-10:23"
    quote: "We need zero-path collisions, filename-based directories are intuitive"
  - source: "docs/requirements/feature-spec.md"
    lines: "120-125"
    quote: "System must handle 100+ concurrent batch uploads without failures"
```

---

## Complete Examples

### Example 1: Simple KISS PRP

```yaml
---
name: "Add JSON Output Flag to Git Status Command"
description: "Add --json flag to ce git status for scripting integration"
prp_id: "PRP-3.1"
task_id: "#42"
status: "ready"
priority: "LOW"
confidence: "9/10"
effort_hours: 1.0
risk: "LOW"
dependencies: []
parent_prp: null
context_memories: []
meeting_evidence: []
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
created_date: "2025-01-15T14:30:00Z"
last_updated: "2025-01-15T14:30:00Z"
---
```

### Example 2: Standard PRP with Dependencies

```yaml
---
name: "Implement Batch Upload Worker Queue"
description: "Add async worker queue to process batch uploads with concurrency control"
prp_id: "PRP-8.5"
task_id: "ENG-245"
status: "executed"
priority: "HIGH"
confidence: "8/10"
effort_hours: 6.0
risk: "MEDIUM"
dependencies: ["PRP-8.3"]
parent_prp: "PRP-8.0"
context_memories: []
meeting_evidence:
  - source: "docs/meetings/2025-01-10-arch-review.md"
    lines: "78-85"
    quote: "Worker queue pattern with asyncio preferred over threading for I/O bound tasks"
context_sync:
  ce_updated: false
  serena_updated: false
version: 1
created_date: "2025-01-12T09:00:00Z"
last_updated: "2025-01-12T18:45:00Z"
---
```

### Example 3: Self-Healing PRP with Context Integration

```yaml
---
name: "Universal /prune-prps Command - Cross-Project PRP Consolidation"
description: "Production-ready universal command for lossless PRP consolidation using series detection and semantic similarity"
prp_id: "PRP-16.0"
task_id: ""
status: "executed"
priority: "HIGH"
confidence: "9/10"
effort_hours: 10.0
risk: "LOW"
dependencies: []
parent_prp: null
context_memories: ["prp_consolidation_patterns", "jaccard_similarity_implementation"]
meeting_evidence:
  - source: "perplexity-peer-review-2025-10-08"
    lines: "N/A"
    quote: "Expert recommendations: executed/archived/ directory, YAML metadata, series compression"
context_sync:
  ce_updated: true
  serena_updated: true
version: 1
created_date: "2025-10-08T16:30:00Z"
last_updated: "2025-10-08T19:35:00Z"
---
```

---

## Field Validation Rules

### PRP ID Format

- **Pattern**: `PRP-X.Y` or `PRP-X.Y.Z` for series
- **X**: Major feature number (1-999)
- **Y**: Minor feature number or iteration (0-99)
- **Z**: Sub-iteration (optional, 0-99)

**Examples**:

- ✅ `PRP-1` - Valid (major feature)
- ✅ `PRP-2.5` - Valid (feature iteration)
- ✅ `PRP-8.7.2` - Valid (series sub-iteration)
- ❌ `PRP-001` - Invalid (leading zeros)
- ❌ `PRP-X` - Invalid (non-numeric)

### Date Format

- **Pattern**: ISO-8601 format `YYYY-MM-DDTHH:MM:SSZ`
- **Timezone**: Always UTC (Z suffix)

**Examples**:

- ✅ `2025-01-15T14:30:00Z`
- ❌ `2025-01-15` (missing time)
- ❌ `2025-01-15 14:30:00` (missing T separator)

### Confidence Score

- **Range**: 1-10 (integer or X/10 string format)
- **Interpretation**:
  - 1-3: Low confidence, significant unknowns
  - 4-6: Medium confidence, some unknowns
  - 7-8: High confidence, well-understood
  - 9-10: Very high confidence, proven patterns

---

## Adaptation Guidelines

### For Different Project Types

**Python Projects (using this template)**:

- Keep all fields as-is
- Set `context_memories` to `[]` if not using Serena MCP
- Set `context_sync` values to `false` if not using CE framework

**TypeScript/JavaScript Projects**:

- Keep YAML structure identical
- Adjust code examples in PRP body to use npm/node/jest
- Keep validation gate commands relevant to project

**Projects Without Context Engineering**:

- Remove `context_memories` field entirely
- Remove `context_sync` field entirely
- Keep all other fields for project management

**Projects Without Issue Tracker**:

- Set `task_id: ""` (empty string, not null)
- Use PRP ID as primary tracking mechanism

---

## Version History

**Version 3.0** (2025-01-15):

- Unified KISS + Self-Healing templates
- Added `task_id` field for issue tracker integration
- Standardized `meeting_evidence` structure with source/lines/timestamp/quote
- Added `parent_prp` for series tracking
- Made Serena/CE fields explicitly optional
- Comprehensive examples for KISS/Standard/Self-Healing modes

**Version 2.0** (2025-10-11):

- Added YAML header to all PRPs
- Introduced `context_sync` tracking
- Added validation gates structure

**Version 1.0** (2025-10-10):

- Initial PRP template structure
- Basic metadata fields

---

## Tools & Integration

### Generating PRPs

Use the `/generate-prp` command (if available) to auto-generate YAML headers with:

- Current timestamp
- Auto-incremented PRP ID
- Project-specific defaults

### Validating YAML

```bash
# Python validation
python -c "import yaml; yaml.safe_load(open('PRPs/PRP-X.Y.md').read().split('---')[1])"

# OR using yq (if installed)
yq eval PRPs/PRP-X.Y.md
```

### Querying PRPs by Metadata

```bash
# Find all HIGH priority PRPs
grep -l "priority: \"HIGH\"" PRPs/PRP-*.md

# Find all executed PRPs
grep -l "status: \"executed\"" PRPs/PRP-*.md

# Find PRPs in a series (e.g., PRP-8.x)
ls PRPs/PRP-8.*.md
```

---

## Best Practices

1. **Keep headers compact**: 12-20 lines maximum
2. **Update `last_updated` on every edit**: Maintain accurate timestamps
3. **Set realistic effort estimates**: Based on actual complexity, not hopes
4. **Update status promptly**: Change to "in_progress" when starting, "executed" when done
5. **Increment version on major revisions**: Not on minor typo fixes
6. **Use meeting_evidence sparingly**: Only when requirements traceability is critical
7. **Link task_id when available**: Improves project management integration
8. **Document parent_prp for series**: Helps understand PRP relationships

---

## FAQ

**Q: Do I need to fill all optional fields?**
A: No. Set to empty strings `""`, empty arrays `[]`, or `null` as appropriate. Remove fields entirely if not using that feature.

**Q: What if my project doesn't use Context Engineering?**
A: Remove `context_memories` and `context_sync` fields entirely. Keep all other fields.

**Q: How do I handle PRP series (e.g., PRP-8.1, PRP-8.2)?**
A: Set `parent_prp: "PRP-8.0"` in child PRPs, list dependencies in `dependencies` array.

**Q: Should I update confidence score during execution?**
A: Yes! Update in "Post-Execution Notes" section or "Confidence Tracking" section if using Self-Healing mode.

**Q: What's the difference between `dependencies` and `parent_prp`?**
A: `parent_prp` indicates series membership (PRP-8.5 is part of PRP-8.x series), `dependencies` lists PRPs that must complete first (PRP-8.5 depends on PRP-8.3 completing).

---

**For more details, see**:

- [PRP Base Template](../PRPs/templates/prp-base-template.md)
- [CLAUDE.md](../CLAUDE.md) - Project guidelines
- [Certinia Template Reference](../certinia/context-engineering/templates/prp-template-optimized.md)
