# Generator Subagent Template

**Purpose**: Generate new PRPs from a structured plan document

**Model**: Haiku 4.5 (cost-effective for iterative generation)

**Invocation**: Task tool with subagent_type=general-purpose

---

## Overview

The generator subagent reads a plan markdown file and produces individual PRP markdown files, one per phase. It handles:

- Plan parsing (extract phases with metadata)
- Dependency analysis (topological sort, cycle detection)
- Stage assignment (group independent phases for parallel execution)
- PRP generation (create individual PRP files with proper YAML frontmatter)
- Linear issue creation (one issue per generated PRP)

---

## Input Spec

**Input Source**: Plan markdown file (e.g., `FEATURE-PLAN.md`)

**Plan Format**:
```markdown
# Feature Name

## Overview
[Brief description]

## Phases

### Phase 1: Name

**Goal**: One-sentence objective
**Estimated Hours**: 4
**Complexity**: low|medium|high
**Files Modified**: path/to/file1, path/to/file2
**Dependencies**: None | Phase 1, Phase 2
**Implementation Steps**:
1. Step 1
2. Step 2
3. Step 3

**Validation Gates**:
- [ ] Gate 1
- [ ] Gate 2
- [ ] Gate 3

### Phase 2: Name

[Same structure as Phase 1]
```

**Parsed Phase Schema** (dict):
```python
{
    "name": "Phase 1: Foundation",
    "goal": "Create orchestrator and subagent templates",
    "estimated_hours": 8,
    "complexity": "medium",
    "files_modified": [".claude/orchestrators/base-orchestrator.md"],
    "dependencies": [],  # List of dependent phase names
    "steps": ["Step 1...", "Step 2..."],
    "validation_gates": ["[ ] Gate 1", "[ ] Gate 2"],
    "index": 0  # Order in plan document
}
```

---

## Processing Steps

### Step 1: Parse Plan File

**Input**: Plan markdown file path

**Output**: List of phase dicts

**Algorithm**:
1. Read markdown file
2. Split by `### Phase` headers
3. For each section:
   - Extract phase name (after `###`)
   - Extract goal (after `**Goal**:`)
   - Extract hours, complexity, files_modified, dependencies
   - Extract steps (lines after `**Implementation Steps**:`)
   - Extract validation gates (checkboxes after `**Validation Gates**:`)
4. Validate each phase (all required fields present)
5. Return list of phase dicts sorted by index

**Pseudo-code**:
```python
def parse_plan(filepath):
    content = read_file(filepath)
    sections = content.split('### Phase ')
    phases = []

    for i, section in enumerate(sections[1:], 1):  # Skip first empty split
        phase = {
            "name": extract_field(section, "^Phase"),
            "goal": extract_field(section, r"\*\*Goal\*\*:\s*(.+)"),
            "estimated_hours": float(extract_field(section, r"\*\*Estimated Hours\*\*:\s*(.+)")),
            "complexity": extract_field(section, r"\*\*Complexity\*\*:\s*(.+)"),
            "files_modified": extract_field(section, r"\*\*Files Modified\*\*:\s*(.+)").split(", "),
            "dependencies": parse_dependencies(extract_field(section, r"\*\*Dependencies\*\*:\s*(.+)")),
            "steps": extract_list(section, r"\*\*Implementation Steps\*\*:"),
            "validation_gates": extract_list(section, r"\*\*Validation Gates\*\*:"),
            "index": i
        }
        phases.append(phase)

    return phases
```

### Step 2: Dependency Analysis

**Input**: List of parsed phases

**Output**: Stage assignment dict (phase_name → stage_number)

**Algorithm**:
1. Build dependency graph: phase_name → list of dependencies
2. Topological sort (Kahn's algorithm):
   - Calculate in-degree for each phase
   - Process phases with in-degree 0 (no dependencies)
   - Assign to current stage
   - Decrement in-degree of dependent phases
   - Repeat until all phases processed
3. Detect cycles (if any phase still has in-degree > 0)

**Example**:
```python
# Input phases
phases = [
    {"name": "Phase 1", "dependencies": []},
    {"name": "Phase 2a", "dependencies": ["Phase 1"]},
    {"name": "Phase 2b", "dependencies": ["Phase 1"]},
    {"name": "Phase 3", "dependencies": ["Phase 2a", "Phase 2b"]}
]

# Output: stage assignment
{
    "Phase 1": 1,
    "Phase 2a": 2,
    "Phase 2b": 2,
    "Phase 3": 3
}
```

**Cycle Detection**:
```python
def detect_cycles(graph):
    """Returns None if no cycles, else cycle path as list"""
    visited = set()
    rec_stack = set()

    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                result = dfs(neighbor, path + [neighbor])
                if result:
                    return result
            elif neighbor in rec_stack:
                return path + [neighbor]

        rec_stack.remove(node)
        return None

    for node in graph:
        if node not in visited:
            cycle = dfs(node, [node])
            if cycle:
                return cycle

    return None
```

### Step 3: Generate PRP File per Phase

**Input**: Single phase dict + batch metadata (batch_id, stage_number)

**Output**: PRP markdown file (e.g., `PRP-43.2.1.md`)

**PRP Filename Format**: `PRP-{batch_id}.{stage}.{index}.md`
- batch_id: Next available batch number (auto-detect from existing PRPs)
- stage: Stage number from dependency analysis
- index: Order within stage (1-indexed)

**PRP YAML Frontmatter**:
```yaml
---
prp_id: PRP-43.2.1
title: Phase 2a - Dependency Analyzer
type: feature
status: pending
created: "2025-11-10"
estimated_hours: 2
complexity: medium
files_modified:
  - .ce/orchestration/dependency_analyzer.py
  - tests/test_dependency_analyzer.py
dependencies:
  - PRP-43.1.1
  - PRP-43.1.2
  - PRP-43.1.3
---
```

**PRP Body Template**:
```markdown
## Problem

[Auto-generated from phase goal]

## Solution

[Auto-generated from implementation steps]

## Implementation

### Steps

1. [Step 1 from phase]
2. [Step 2 from phase]
3. [Step 3 from phase]

### Validation Gates

- [ ] [Gate 1 from phase]
- [ ] [Gate 2 from phase]
- [ ] [Gate 3 from phase]

### Testing Strategy

[Generated based on complexity level]

### Risk Mitigation

[Generated based on complexity level]
```

**Auto-generated Content** (based on complexity):

**Low Complexity**:
```markdown
### Testing Strategy

- Write unit tests for core functionality
- Manual testing of edge cases
- Verify test coverage >80%

### Risk Mitigation

- Small scope limits blast radius
- Changes are isolated to single module
- Fallback: Revert if tests fail
```

**Medium Complexity**:
```markdown
### Testing Strategy

- Write unit tests for core + integration paths
- Write integration test covering main workflow
- Manual testing of edge cases
- Verify test coverage >85%

### Risk Mitigation

- Thorough testing before merge
- Staged rollout: test in isolation first
- Fallback: Use previous implementation if critical bug found
- Time box: Allocate 20% buffer on estimated hours
```

**High Complexity**:
```markdown
### Testing Strategy

- Unit tests for all functions (>90% coverage)
- Integration tests for all workflows
- E2E test with real data
- Load testing if applicable
- Security review if handling sensitive data

### Risk Mitigation

- Break into smaller sub-phases if possible
- Detailed design review before implementation
- Daily checkpoint commits
- Pre-production staging if possible
- Rollback plan documented
- Time box: Allocate 30% buffer on estimated hours
```

### Step 4: Create Linear Issues

**Input**: Generated PRP file path + batch metadata

**Output**: Linear issue created, issue ID added to PRP frontmatter

**Linear Issue Template**:
```yaml
title: "PRP-43.2.1: Phase 2a - Dependency Analyzer"
description: |
  ## Goal
  [Phase goal]

  ## Implementation Steps
  1. [Step 1]
  2. [Step 2]

  ## Validation Gates
  - [ ] [Gate 1]
  - [ ] [Gate 2]

  See full details: PRPs/feature-requests/PRP-43.2.1.md
team_id: "Blaise78"  # From .ce/linear-defaults.yml
assignee: "blazej.przybyszewski@gmail.com"
```

**Update PRP Frontmatter**:
```yaml
issue_id: LIN-123
issue_url: https://linear.app/context-engineering/issue/CE-123
```

---

## Output Spec

**Output Files**:
1. Multiple PRP markdown files: `PRPs/feature-requests/PRP-{batch_id}.{stage}.{index}.md`
2. Linear issues created (one per PRP)
3. Batch summary JSON: `.ce/orchestration/batches/batch-{batch_id}.summary.json`

**Batch Summary JSON**:
```json
{
  "batch_id": 43,
  "plan_file": "FEATURE-PLAN.md",
  "total_phases": 10,
  "stages": 4,
  "generated_prps": [
    "PRP-43.1.1",
    "PRP-43.2.1",
    "PRP-43.2.2",
    "PRP-43.3.1",
    "PRP-43.3.2",
    "PRP-43.3.3"
  ],
  "dependencies": {
    "PRP-43.1.1": [],
    "PRP-43.2.1": ["PRP-43.1.1"],
    "PRP-43.2.2": ["PRP-43.1.1"]
  },
  "total_hours": 28,
  "total_complexity": "medium",
  "created_at": "2025-11-10T14:30:00Z"
}
```

**Heartbeat Output** (every 30 seconds):
```json
{
  "task_id": "phase-1",
  "status": "in_progress",
  "progress": "Generated 6/10 PRPs, creating Linear issues",
  "tokens_used": 35000,
  "elapsed_seconds": 450
}
```

---

## Error Handling

**Invalid Plan Format**:
```python
try:
    phases = parse_plan(plan_file)
except ValueError as e:
    return {
        "status": "error",
        "error": f"Invalid plan format: {e}",
        "error_location": str(e)
    }
```

**Circular Dependencies**:
```python
cycle = detect_cycles(dependency_graph)
if cycle:
    return {
        "status": "error",
        "error": f"Circular dependency detected: {' → '.join(cycle)}",
        "cycle_path": cycle
    }
```

**Linear Integration Failure**:
```python
try:
    issue_id = create_linear_issue(prp_dict)
except Exception as e:
    logger.warning(f"Failed to create Linear issue for {prp_id}: {e}")
    # Continue processing other PRPs, mark as pending manual issue creation
    result["pending_issues"].append((prp_id, str(e)))
```

---

## Validation Gates

- [ ] Plan file parses without errors
- [ ] All phases have required fields (goal, hours, complexity, files, steps, gates)
- [ ] No circular dependencies detected
- [ ] Stage assignment maximizes parallelism (validates topological sort)
- [ ] All PRP files created with correct YAML frontmatter
- [ ] All PRP files contain goal + steps + validation gates
- [ ] All Linear issues created with correct metadata
- [ ] Batch summary JSON complete and valid
- [ ] Total estimated hours calculated correctly
- [ ] Files modified list merged without duplicates

---

## Example: Input → Output

**Input Plan** (3 phases):
```markdown
# Unified Batch Framework

## Phases

### Phase 1: Foundation

**Goal**: Create orchestrator and subagent templates
**Estimated Hours**: 8
**Complexity**: medium
**Files Modified**: .claude/orchestrators/base-orchestrator.md, .claude/subagents/*.md
**Dependencies**: None
**Implementation Steps**:
1. Write base-orchestrator.md
2. Write 4 subagent templates
3. Document with examples

**Validation Gates**:
- [ ] All 5 files created
- [ ] No syntax errors
- [ ] Total lines: ~730 ± 50

### Phase 2: Dependency Analyzer

**Goal**: Implement topological sort and cycle detection
**Estimated Hours**: 2
**Complexity**: medium
**Files Modified**: .ce/orchestration/dependency_analyzer.py
**Dependencies**: Phase 1
**Implementation Steps**:
1. Implement topological sort (Kahn's algorithm)
2. Implement cycle detection
3. Implement stage assignment

**Validation Gates**:
- [ ] Topological sort works correctly
- [ ] Cycle detection returns path
- [ ] Stage assignment maximizes parallelism

### Phase 3: Unit Tests

**Goal**: Test dependency analyzer with >90% coverage
**Estimated Hours**: 2
**Complexity**: low
**Files Modified**: tests/test_dependency_analyzer.py
**Dependencies**: Phase 2
**Implementation Steps**:
1. Test topological sort (5+ cases)
2. Test cycle detection
3. Test stage assignment
4. Generate coverage report

**Validation Gates**:
- [ ] All tests pass
- [ ] Coverage >90%
```

**Output** (3 PRP files):
```
PRPs/feature-requests/PRP-44.1.1.md
  - PRP-44.1.1: Phase 1 - Foundation

PRPs/feature-requests/PRP-44.2.1.md
  - PRP-44.2.1: Phase 2 - Dependency Analyzer

PRPs/feature-requests/PRP-44.3.1.md
  - PRP-44.3.1: Phase 3 - Unit Tests
```

**Batch Summary**:
```json
{
  "batch_id": 44,
  "total_phases": 3,
  "stages": 3,
  "generated_prps": ["PRP-44.1.1", "PRP-44.2.1", "PRP-44.3.1"],
  "total_hours": 12,
  "dependencies": {
    "PRP-44.1.1": [],
    "PRP-44.2.1": ["PRP-44.1.1"],
    "PRP-44.3.1": ["PRP-44.2.1"]
  }
}
```

---

## Integration Points

**Receives Input From**: Base Orchestrator (Phase 1: Parse & Validate)

**Writes Output To**:
- PRPs/feature-requests/ (PRP files)
- .ce/orchestration/batches/ (batch summary JSON)
- Linear (issue creation)

**Heartbeat Protocol**: Write task-{id}.hb every 30 seconds

**Result Protocol**: Write task-{id}.result.json when done
