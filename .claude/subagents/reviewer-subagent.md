# Reviewer Subagent Template

**Purpose**: Peer review PRPs using structural and semantic analysis modes

**Model**: Haiku 4.5 (pattern-based review, semantic analysis)

**Invocation**: Task tool with subagent_type=general-purpose

---

## Overview

The reviewer subagent reads one or more PRP files and produces a detailed peer review report:

- Structural analysis (YAML format, required fields, formatting)
- Semantic analysis (clarity, completeness, feasibility)
- Inter-PRP consistency checks (dependencies, file conflicts)
- Risk assessment (complexity vs time estimate)
- Recommendations for improvement

---

## Input Spec

**Input Source**: One or more PRP markdown files

**PRP File Structure** (expected):
```yaml
---
prp_id: PRP-43.1.1
title: Phase 1 - Foundation
type: feature
status: pending
complexity: medium
estimated_hours: 8
files_modified: [...]
dependencies: [...]
---

## Problem

[Problem statement]

## Solution

[Solution approach]

## Implementation

### Steps

1. [Step 1]
2. [Step 2]

### Validation Gates

- [ ] Gate 1
- [ ] Gate 2

### Testing Strategy

[Testing approach]

### Risk Mitigation

[Risk mitigation]
```

---

## Processing Steps

### Step 1: Parse Review Input

**Input**: List of PRP file paths (from batch or explicit list)

**Output**: Parsed PRP dicts + metadata

**Parsing Algorithm**:
1. For each PRP file:
   - Read YAML frontmatter
   - Extract main sections (Problem, Solution, Implementation, etc.)
   - Parse steps list and validation gates list
   - Extract metadata (prp_id, title, complexity, estimated_hours)
2. Build dependency graph (PRP → list of dependencies)
3. Collect all PRPs for review

**Parsed Review Input Schema**:
```python
{
    "batch_id": 43,
    "total_prps": 10,
    "prps": [
        {
            "prp_id": "PRP-43.1.1",
            "title": "Phase 1 - Foundation",
            "complexity": "medium",
            "estimated_hours": 8,
            "files_modified": [...],
            "dependencies": [...],
            "sections": {
                "problem": "...",
                "solution": "...",
                "steps": [...],
                "validation_gates": [...],
                "testing_strategy": "...",
                "risk_mitigation": "..."
            }
        },
        # ... more PRPs ...
    ],
    "dependency_graph": {
        "PRP-43.1.1": [],
        "PRP-43.2.1": ["PRP-43.1.1"],
        # ...
    }
}
```

### Step 2: Structural Analysis (Per PRP)

**Input**: Single PRP parsed dict

**Output**: Structural review report

**Checks**:

| Check | Expected | How to Validate |
|-------|----------|-----------------|
| **YAML Frontmatter** | prp_id, title, type, status, complexity, estimated_hours, files_modified, dependencies | Parse YAML, check required fields present |
| **Main Sections** | Problem, Solution, Implementation | Count headers, check `## Problem`, `## Solution`, `## Implementation` exist |
| **Implementation Subsections** | Steps, Validation Gates, Testing Strategy, Risk Mitigation | Check `### Steps`, `### Validation Gates`, etc. |
| **Steps Format** | Numbered list (1. 2. 3. ...) | Parse list, check sequential numbering |
| **Validation Gates Format** | Checkbox list (`[ ] Gate 1`, `[ ] Gate 2`) | Parse list, check all are checkboxes |
| **Gate Count** | At least 3 gates | Count gates, verify >= 3 |
| **Complexity Match** | Low=2-4h, Medium=4-8h, High=8-16h | Check estimated_hours aligns with complexity |
| **Markdown Syntax** | Valid markdown, no broken links | Run markdown linter |

**Structural Report Example**:
```
Structural Analysis - PRP-43.1.1
═══════════════════════════════════════════

YAML Frontmatter:
  ✓ prp_id: PRP-43.1.1
  ✓ title: Phase 1 - Foundation
  ✓ type: feature
  ✓ status: pending
  ✓ complexity: medium
  ✓ estimated_hours: 8
  ✓ files_modified: [5 files]
  ✓ dependencies: None

Main Sections:
  ✓ ## Problem
  ✓ ## Solution
  ✓ ## Implementation

Implementation Subsections:
  ✓ ### Steps (5 steps)
  ✓ ### Validation Gates (4 gates)
  ✓ ### Testing Strategy
  ✓ ### Risk Mitigation

Format Checks:
  ✓ Steps: Sequential numbering (1-5)
  ✓ Gates: Checkbox format (4/4)
  ✓ Gate count: 4 (minimum: 3) ✓
  ✓ Markdown syntax: Valid
  ✓ No broken links

Complexity Alignment:
  ✓ Estimated hours: 8
  ✓ Complexity level: medium
  ✓ Range: 4-8h (medium) ✓

Overall: PASSED ✓
═══════════════════════════════════════════
```

### Step 3: Semantic Analysis (Per PRP)

**Input**: Single PRP parsed dict + project context

**Output**: Semantic review report

**Checks**:

| Check | What to Evaluate | How to Validate |
|-------|------------------|-----------------|
| **Problem Clarity** | Problem statement is specific, not vague | Analyze length (>20 words), technical terms defined |
| **Problem Completeness** | Explains why problem exists | Check mentions context or root cause |
| **Solution Alignment** | Solution solves stated problem | Check solution keywords match problem keywords |
| **Solution Feasibility** | Solution is achievable in estimated time | Cross-check with complexity + hours |
| **Step Clarity** | Each step is understandable, not ambiguous | Check step length (>3 words, <100 words) |
| **Step Sequence** | Steps in logical order | Analyze dependencies between steps |
| **Gate Clarity** | Gates are testable and measurable | Check gates aren't vague (no "works well") |
| **Gate Achievability** | Gates are achievable after steps | Cross-check gates vs steps output |
| **Test Coverage** | Testing strategy covers main scenarios | Check testing strategy mentions unit/integration/e2e if needed |
| **Risk Awareness** | Risk mitigation addresses real risks | Check risk mitigation isn't generic |

**Semantic Report Example**:
```
Semantic Analysis - PRP-43.1.1
═══════════════════════════════════════════

Problem Statement:
  ✓ Specific: Yes (mentions "6-phase orchestration logic")
  ✓ Complete: Yes (explains problem context)
  ✓ Clarity: Good (23 words, clear intent)

Solution:
  ✓ Aligned with problem: Yes
  ✓ Feasible in 8h: Yes (straightforward templates)
  ✓ Clear approach: Yes

Steps:
  ✓ Step 1: "Create base-orchestrator.md..." (clear, ~50 words)
  ✓ Step 2: "Create generator-subagent.md..." (clear)
  ✓ Step 3: "Create executor-subagent.md..." (clear)
  ✓ Step 4: "Create reviewer-subagent.md..." (clear)
  ✓ Step 5: "Create context-updater..." (clear)
  ✓ Sequence: Logical (all templates first, then tests)

Validation Gates:
  ✓ Gate 1: Testable ("All 5 files created") ✓
  ✓ Gate 2: Testable ("No syntax errors") ✓
  ✓ Gate 3: Testable ("Total lines: ~730 ± 50") ✓
  ✓ Gate 4: Testable ("Examples provided") ✓
  ✓ Gate 5: Testable ("Clear input/output specs") ✓
  ✓ Achievability: Yes (gates match step outputs)

Testing:
  ✓ Strategy: "Manual code review + syntax validation"
  ✓ Coverage: Adequate for complexity level

Risk Mitigation:
  ✓ Addresses real risks (complexity, integration)
  ✓ Practical solutions (incremental, documentation)

Overall: PASSED ✓
═══════════════════════════════════════════
```

### Step 4: Inter-PRP Consistency (Batch-Level)

**Input**: All PRPs in batch + dependency graph

**Output**: Consistency report

**Checks**:

| Check | What to Validate | How to Validate |
|-------|------------------|-----------------|
| **Dependency Validity** | All declared dependencies exist | Check each dependency is another PRP in batch |
| **Circular Dependencies** | No circular dependencies | Topological sort, check all PRPs have in-degree 0 eventually |
| **File Conflicts** | No two PRPs modify same file | Build file → [PRP list] map, check all have single PRP |
| **Total Hours Estimate** | Sum of hours is reasonable | Sum all estimated_hours, check <80h for 3-week sprint |
| **Complexity Balance** | Mix of LOW, MEDIUM, HIGH | Count distribution, check >30% are LOW |
| **Dependency Clustering** | Dependencies form logical groups | Visualize graph, check no strange isolated clusters |

**Consistency Report Example** (Batch Level):
```
Inter-PRP Consistency - Batch 43 (10 PRPs)
═══════════════════════════════════════════

Dependency Analysis:
  ✓ All dependencies exist in batch
  ✓ No circular dependencies
  ✓ Dependency graph valid

File Conflict Detection:
  ✗ CONFLICT: PRP-43.2.1 and PRP-43.2.2 both modify:
    - .ce/orchestration/dependency_analyzer.py
  → Action: Manual resolution required (or merge PRPs)

Hours Estimate:
  Total: 28 hours
  Complexity: medium (8 MEDIUM, 2 LOW)
  ✓ Reasonable for 3-week sprint
  ✓ Complexity mix: 80% medium, 20% low (expect 60% low, 30% medium, 10% high)

Dependency Graph (simplified):
  Stage 1: PRP-43.1.1, PRP-43.1.2, PRP-43.1.3 (parallel)
  Stage 2: PRP-43.2.1, PRP-43.2.2 (parallel, conflict on one file)
  Stage 3: PRP-43.3.1, PRP-43.3.2, PRP-43.3.3 (parallel)
  Stage 4: PRP-43.4.1

Overall: WARNINGS (file conflict requires attention)
═══════════════════════════════════════════
```

### Step 5: Risk Assessment

**Input**: Single PRP (complexity + hours + gates + risks)

**Output**: Risk score + recommendations

**Risk Scoring Algorithm**:

| Risk Factor | Weight | Scoring |
|-------------|--------|---------|
| **Complexity Mismatch** | 25% | Low=1pt, Medium=3pts, High=5pts; add 5 if hours don't match |
| **Validation Gate Coverage** | 25% | <3 gates=5pts, 3-4 gates=2pts, >4 gates=0pts |
| **Step Clarity** | 20% | 0-2 vague steps=0pts, 3+ vague=5pts |
| **Dependency Risk** | 15% | 0 deps=0pts, 1-2 deps=2pts, 3+ deps=5pts |
| **Time Pressure** | 15% | If hours estimate seems aggressive for complexity=3pts |

**Risk Score**: Sum of weighted points (0-100)

**Risk Categories**:
- 0-15: LOW risk (green)
- 16-40: MEDIUM risk (yellow) → Review recommendations
- 41-100: HIGH risk (red) → Consider re-scoping

**Risk Report Example**:
```
Risk Assessment - PRP-43.1.1
═══════════════════════════════════════════

Complexity: medium, Hours: 8
Complexity vs Hours: ✓ Aligned

Validation Gates: 5 (good coverage)

Step Clarity: All clear

Dependencies: 0 (no blocking)

Time Pressure: ✓ Reasonable buffer

Overall Risk Score: 12/100 (LOW) 🟢
═══════════════════════════════════════════

Recommendations:
  - Proceed as planned
  - Standard code review sufficient
  - No special mitigations needed
```

---

## Output Spec

**Output Files**:
1. Peer review report: `PRPs/reviews/PRP-43-batch-review.md`
2. Heartbeat file: `task-{id}.hb` (updated every 30 seconds)
3. Result file: `task-{id}.result.json`

**Peer Review Report Format**:
```markdown
# Peer Review Report - Batch 43

**Date**: 2025-11-10
**Reviewer**: Reviewer Subagent
**Total PRPs Reviewed**: 10
**Review Status**: PASSED WITH WARNINGS

---

## Executive Summary

All 10 PRPs structurally sound. 9/10 pass semantic analysis.
File conflict detected between PRP-43.2.1 and PRP-43.2.2 (manual resolution needed).

---

## Structural Review (All PRPs)

| PRP | Frontmatter | Sections | Format | Overall |
|-----|-------------|----------|--------|---------|
| PRP-43.1.1 | ✓ | ✓ | ✓ | PASS |
| PRP-43.2.1 | ✓ | ✓ | ✓ | PASS |
| [... 8 more PRPs ...] | | | | |

---

## Semantic Review (Detailed)

### PRP-43.1.1: Foundation ✓
- Problem: Clear and specific
- Solution: Feasible in 8 hours
- Steps: 5 steps, all clear and sequential
- Gates: 5 gates, all testable
- Risk: LOW (12/100)

### PRP-43.2.1: Dependency Analyzer ✓
- Problem: Clear and specific
- Solution: Well-defined algorithm
- Steps: 3 steps, all clear
- Gates: 4 gates, all measurable
- Risk: LOW (14/100)

[... 8 more PRPs ...]

---

## Inter-PRP Analysis

### Dependency Graph
[ASCII diagram showing stages]

### File Conflicts
⚠️ **CONFLICT DETECTED**:
- PRP-43.2.1 and PRP-43.2.2 both modify `.ce/orchestration/dependency_analyzer.py`
- Recommendation: Merge these PRPs or coordinate timing

### Hours Estimate
- Total: 28 hours
- Recommendation: ✓ Reasonable for 3-week sprint

### Complexity Distribution
- LOW: 2 PRPs (20%)
- MEDIUM: 8 PRPs (80%)
- HIGH: 0 PRPs (0%)
- Note: Expected distribution is 60% LOW, 30% MEDIUM, 10% HIGH
- Recommendation: Current batch skews toward MEDIUM (higher risk)

---

## Risk Summary

| Risk Level | Count | Details |
|-----------|-------|---------|
| LOW (0-15) | 9 | All proceeding as planned |
| MEDIUM (16-40) | 1 | PRP-43.3.1: Consider additional review |
| HIGH (41-100) | 0 | None |

---

## Recommendations

1. **Resolve File Conflict**: Merge PRP-43.2.1 + PRP-43.2.2 or coordinate writes
2. **Review PRP-43.3.1**: MEDIUM risk score - additional peer review recommended
3. **Proceed with Batch**: All PRPs ready for execution

---

## Approval Status

**Overall**: ✓ APPROVED WITH MINOR CHANGES

Proceed to execution. Address file conflict before executing Stage 2.

---

**Reviewed by**: Reviewer Subagent
**Report Generated**: 2025-11-10T14:50:00Z
```

**Result JSON Format**:
```json
{
  "task_id": "review-batch-43",
  "batch_id": 43,
  "status": "success",
  "total_prps": 10,
  "structural_pass": 10,
  "structural_fail": 0,
  "semantic_pass": 9,
  "semantic_fail": 1,
  "file_conflicts": [
    {
      "prp_1": "PRP-43.2.1",
      "prp_2": "PRP-43.2.2",
      "file": ".ce/orchestration/dependency_analyzer.py"
    }
  ],
  "overall_approval": "approved_with_warnings",
  "report_file": "PRPs/reviews/PRP-43-batch-review.md",
  "elapsed_seconds": 300,
  "tokens_used": 25000
}
```

---

## Heartbeat Protocol

**Frequency**: Every 30 seconds

**Format**:
```json
{
  "task_id": "review-batch-43",
  "status": "in_progress",
  "progress": "Reviewing PRP 6/10: Semantic analysis",
  "prps_reviewed": 5,
  "total_prps": 10,
  "tokens_used": 15000,
  "elapsed_seconds": 180,
  "last_update": "2025-11-10T14:50:30Z"
}
```

---

## Integration Points

**Receives Input From**: Base Orchestrator (Phase 3: Spawn Subagents)

**Reads From**:
- PRP files (PRPs/feature-requests/)
- CLAUDE.md (project conventions)

**Writes To**:
- Review report (PRPs/reviews/)
- Heartbeat file
- Result file

---

## Example: Single PRP Review Flow

**Input**: `PRPs/feature-requests/PRP-43.1.1.md`

**Processing**:
1. Parse YAML frontmatter ✓
2. Extract sections ✓
3. Structural checks ✓ (all pass)
4. Semantic checks ✓ (all pass)
5. Complexity alignment ✓ (medium 8h)
6. Risk assessment: LOW (12/100)
7. Generate report section ✓

**Output**: Report section added to review report
