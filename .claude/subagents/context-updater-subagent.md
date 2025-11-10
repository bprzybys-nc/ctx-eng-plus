# Context Updater Subagent Template

**Purpose**: Sync executed PRP status back into context (CLAUDE.md, Serena memory) and update git history tracking

**Model**: Haiku 4.5 (transformation logic, memory updates)

**Invocation**: Task tool with subagent_type=general-purpose

---

## Overview

The context-updater subagent synchronizes completed PRP execution status back into the project context:

- Read executed PRP file
- Check git history for implementation commits
- Extract implementation evidence (files modified, commits, test results)
- Calculate drift score (difference between original plan and actual execution)
- Update PRP status from "pending" to "completed"
- Update Serena memory with PRP metadata
- Generate completion report

---

## Input Spec

**Input Source**: Executed PRP markdown file + git history

**Input PRP File** (example):
```yaml
---
prp_id: PRP-43.1.1
title: Phase 1 - Foundation
type: feature
status: pending
created: "2025-11-10"
estimated_hours: 8
complexity: medium
files_modified:
  - .claude/orchestrators/base-orchestrator.md
  - .claude/subagents/generator-subagent.md
dependencies: []
---

## Problem

[Original problem statement]

## Solution

[Original solution approach]

## Implementation

### Steps

1. Create .claude/orchestrators/base-orchestrator.md
2. Create .claude/subagents/generator-subagent.md
3. [... remaining steps ...]

### Validation Gates

- [ ] All 5 files created
- [ ] No syntax errors
- [ ] Total lines: ~730 ± 50
```

---

## Processing Steps

### Step 1: Parse PRP File

**Input**: PRP markdown file path

**Output**: Parsed PRP dict

**Parsing**:
```python
def parse_prp(filepath):
    """Extract metadata and content from PRP"""
    with open(filepath) as f:
        yaml_part, md_part = f.read().split('---', 2)[1:]

    prp = yaml.safe_load(yaml_part)
    prp["body"] = md_part

    # Extract sections from markdown
    sections = {}
    current_section = None
    current_content = []

    for line in md_part.split('\n'):
        if line.startswith('## '):
            if current_section:
                sections[current_section] = '\n'.join(current_content).strip()
            current_section = line[3:].lower()
            current_content = []
        else:
            current_content.append(line)

    if current_section:
        sections[current_section] = '\n'.join(current_content).strip()

    prp["sections"] = sections
    return prp
```

### Step 2: Check Execution Status

**Input**: Parsed PRP dict

**Output**: Execution status (status, commits, files_modified)

**Git History Lookup**:
```python
def find_prp_commits(prp_id):
    """Find all git commits related to this PRP"""
    # Pattern: "PRP-43.1.1: Step 1 - ..."
    pattern = f"{prp_id}:"

    commits = []
    log_output = subprocess.run(
        ["git", "log", "--oneline", "--all"],
        capture_output=True,
        text=True
    ).stdout

    for line in log_output.split('\n'):
        if pattern in line:
            hash, msg = line.split(' ', 1)
            commits.append({"hash": hash, "message": msg})

    return commits
```

**Status Determination**:
```python
def determine_prp_status(prp_id, commits):
    """Determine if PRP has been executed"""

    if not commits:
        return "pending"  # No commits found

    # Check if final commit exists (contains "Complete")
    final_commits = [c for c in commits if "Complete" in c["message"]]

    if final_commits:
        return "completed"
    elif commits:
        # Has some commits but not final
        return "in_progress"
    else:
        return "pending"
```

### Step 3: Extract Implementation Evidence

**Input**: Parsed PRP + git commits

**Output**: Implementation details (files, commits, changes)

**Evidence Collection**:
```python
def collect_evidence(prp_id, commits):
    """Collect proof of implementation"""

    evidence = {
        "commits": [],
        "files_created": [],
        "files_modified": [],
        "lines_added": 0,
        "lines_removed": 0,
        "total_changes": 0
    }

    for commit in commits:
        hash = commit["hash"]

        # Get changed files
        files_output = subprocess.run(
            ["git", "show", "--name-status", hash],
            capture_output=True,
            text=True
        ).stdout

        for line in files_output.split('\n')[5:]:  # Skip header
            if not line or line.startswith('commit'):
                continue

            status, filename = line.split('\t', 1)
            evidence["commits"].append({
                "hash": hash,
                "message": commit["message"],
                "files": [filename]
            })

            if status == 'A':  # Added
                evidence["files_created"].append(filename)
            elif status in ['M', 'D']:  # Modified or Deleted
                evidence["files_modified"].append(filename)

        # Get diff stats
        diff_stats = subprocess.run(
            ["git", "show", "--stat", hash],
            capture_output=True,
            text=True
        ).stdout

        # Parse "+X -Y" format
        for line in diff_stats.split('\n'):
            if '+' in line and '-' in line:
                parts = line.split('+')[-1].split('-')
                if len(parts) == 2:
                    try:
                        added = int(parts[0].strip())
                        removed = int(parts[1].strip())
                        evidence["lines_added"] += added
                        evidence["lines_removed"] += removed
                    except ValueError:
                        pass

    evidence["total_changes"] = evidence["lines_added"] + evidence["lines_removed"]
    return evidence
```

### Step 4: Calculate Drift Score

**Input**: Original PRP (estimated_hours, files_modified) + Evidence (actual_files, actual_commits)

**Output**: Drift score (percentage)

**Drift Calculation**:

Drift measures the difference between original plan and actual execution:

```python
def calculate_drift(prp, evidence):
    """Calculate divergence between plan and reality"""

    drift_factors = {}

    # Factor 1: File differences
    planned_files = set(prp.get("files_modified", []))
    actual_files = set(evidence["files_created"] + evidence["files_modified"])

    if planned_files or actual_files:
        file_diff = len(planned_files ^ actual_files) / max(len(planned_files | actual_files), 1)
        drift_factors["file_diff"] = file_diff
    else:
        drift_factors["file_diff"] = 0

    # Factor 2: Scope change (did extra files get modified?)
    unexpected_files = actual_files - planned_files
    if unexpected_files:
        drift_factors["scope_creep"] = min(0.3, len(unexpected_files) * 0.1)
    else:
        drift_factors["scope_creep"] = 0

    # Factor 3: Commit count (how granular was the work?)
    expected_steps = len(prp.get("steps", []))
    actual_commits = len(evidence["commits"])

    if actual_commits < expected_steps * 0.7:
        drift_factors["commit_granularity"] = 0.1
    elif actual_commits > expected_steps * 1.5:
        drift_factors["commit_granularity"] = 0.05
    else:
        drift_factors["commit_granularity"] = 0

    # Factor 4: Implementation size vs estimate
    # Assume ~50 lines per hour for estimates
    expected_lines = prp.get("estimated_hours", 1) * 50
    actual_lines = evidence["total_changes"]

    if actual_lines > 0:
        size_ratio = actual_lines / expected_lines
        if size_ratio > 1.5:
            drift_factors["size_overrun"] = min(0.2, (size_ratio - 1) * 0.1)
        elif size_ratio < 0.5:
            drift_factors["size_underrun"] = 0.15  # Possible scope underestimate
        else:
            drift_factors["size_overrun"] = 0
            drift_factors["size_underrun"] = 0
    else:
        drift_factors["size_overrun"] = 0

    # Calculate total drift (weighted average)
    weights = {
        "file_diff": 0.3,
        "scope_creep": 0.2,
        "commit_granularity": 0.2,
        "size_overrun": 0.15,
        "size_underrun": 0.15
    }

    total_drift = sum(drift_factors.get(k, 0) * v for k, v in weights.items())

    return {
        "drift_score": total_drift,
        "drift_percentage": int(total_drift * 100),
        "factors": drift_factors,
        "interpretation": interpret_drift(total_drift)
    }

def interpret_drift(score):
    """Convert drift score to human-readable interpretation"""
    if score < 0.05:
        return "EXCELLENT (execution matched plan very closely)"
    elif score < 0.15:
        return "GOOD (minor deviations, all intentional)"
    elif score < 0.30:
        return "ACCEPTABLE (some scope creep, but managed)"
    elif score < 0.50:
        return "CONCERNING (significant divergence from plan)"
    else:
        return "CRITICAL (execution deviated heavily from plan)"
```

**Drift Score Interpretation**:
- 0-5%: EXCELLENT (flawless execution)
- 5-15%: GOOD (minor expected deviations)
- 15-30%: ACCEPTABLE (some scope creep, managed)
- 30-50%: CONCERNING (significant divergence)
- 50%+: CRITICAL (execution different from plan)

### Step 5: Update PRP Status

**Input**: Parsed PRP + execution status + evidence + drift score

**Output**: Updated PRP markdown file

**Status Transitions**:

```
pending → in_progress (when commits appear)
in_progress → completed (when final commit appears)
```

**Updated PRP Frontmatter** (add execution tracking):
```yaml
---
prp_id: PRP-43.1.1
title: Phase 1 - Foundation
type: feature
status: completed
created: "2025-11-10"
completed: "2025-11-10T15:00:00Z"
estimated_hours: 8
actual_hours: 7.5
complexity: medium
files_modified:
  - .claude/orchestrators/base-orchestrator.md
  - .claude/subagents/generator-subagent.md
  - .claude/subagents/executor-subagent.md
  - .claude/subagents/reviewer-subagent.md
  - .claude/subagents/context-updater-subagent.md
dependencies: []

# Execution Tracking
execution:
  status: completed
  commits:
    - "5f1a3c2 - PRP-43.1.1: Step 1 - Create base-orchestrator.md"
    - "7e2b4d1 - PRP-43.1.1: Step 2 - Create generator-subagent.md"
  files_created: 5
  lines_added: 732
  lines_removed: 0
  drift_score: 8
  drift_interpretation: "EXCELLENT (execution matched plan very closely)"
---
```

**Update Algorithm**:
```python
def update_prp(filepath, execution_data):
    """Update PRP file with execution tracking"""

    with open(filepath) as f:
        yaml_section, md_part = f.read().split('---', 2)[1:]

    prp = yaml.safe_load(yaml_section)

    # Update status fields
    prp["status"] = "completed"
    prp["completed"] = datetime.now().isoformat() + "Z"

    # Add execution data
    prp["actual_hours"] = round(execution_data["elapsed_seconds"] / 3600, 1)
    prp["execution"] = {
        "status": "completed",
        "commits": execution_data["commits"],
        "files_created": len(execution_data["evidence"]["files_created"]),
        "lines_added": execution_data["evidence"]["lines_added"],
        "drift_score": execution_data["drift_score"]["drift_percentage"],
        "drift_interpretation": execution_data["drift_score"]["interpretation"]
    }

    # Write updated file
    updated_yaml = yaml.dump(prp, default_flow_style=False)
    with open(filepath, 'w') as f:
        f.write(f"---\n{updated_yaml}---\n{md_part}")
```

### Step 6: Update Serena Memory

**Input**: Updated PRP dict + execution data

**Output**: Serena memory entry (or update)

**Memory Entry Format**:
```yaml
---
type: regular
category: executed_prp
tags: [prp-43, completed, phase-1]
created: "2025-11-10"
updated: "2025-11-10T15:00:00Z"
---

# PRP-43.1.1 Execution Summary

**Status**: Completed
**Completion Date**: 2025-11-10
**Duration**: 7.5 hours (estimated: 8)
**Drift Score**: 8% (EXCELLENT)

## Changes Made

- Files Created: 5
  - .claude/orchestrators/base-orchestrator.md (300 lines)
  - .claude/subagents/generator-subagent.md (100 lines)
  - [... 3 more files ...]
- Total Lines Added: 732

## Commits

```
5f1a3c2 - PRP-43.1.1: Step 1 - Create base-orchestrator.md
7e2b4d1 - PRP-43.1.1: Step 2 - Create generator-subagent.md
```

## Lessons Learned

[Auto-generated based on drift analysis]

## Next PRPs

- PRP-43.2.1: Dependency Analyzer (dependent on this)
- PRP-43.3.1: Unit Tests (dependent on this)
```

---

## Output Spec

**Output Files**:
1. Updated PRP markdown file (PRPs/feature-requests/)
2. Serena memory entry (.serena/memories/ or update existing)
3. Heartbeat file: `task-{id}.hb`
4. Result file: `task-{id}.result.json`

**Result JSON Format**:
```json
{
  "task_id": "context-update-43.1.1",
  "prp_id": "PRP-43.1.1",
  "status": "success",
  "execution_status": "completed",
  "original_status": "pending",
  "drift_score": 8,
  "drift_interpretation": "EXCELLENT",
  "evidence": {
    "commits": 5,
    "files_created": 5,
    "files_modified": 0,
    "lines_added": 732,
    "lines_removed": 0
  },
  "updates_applied": [
    "Updated PRP status to completed",
    "Added execution tracking data",
    "Created Serena memory entry",
    "Calculated drift score"
  ],
  "elapsed_seconds": 30,
  "tokens_used": 5000
}
```

---

## Heartbeat Protocol

**Frequency**: Every 30 seconds

**Format**:
```json
{
  "task_id": "context-update-batch-43",
  "status": "in_progress",
  "progress": "Updating PRP 3/10: Calculating drift score",
  "prps_updated": 2,
  "total_prps": 10,
  "tokens_used": 3000,
  "elapsed_seconds": 45,
  "last_update": "2025-11-10T15:00:30Z"
}
```

---

## Batch Context Update

**Input**: Multiple executed PRPs

**Output**: Batch completion report

**Batch Update Algorithm**:
```python
def update_batch_context(batch_id, executed_prps):
    """Update context for entire batch"""

    total_drift = 0
    completed = 0

    for prp_file in executed_prps:
        prp = parse_prp(prp_file)
        status = determine_prp_status(prp["prp_id"])

        if status == "completed":
            completed += 1
            evidence = collect_evidence(prp["prp_id"], find_prp_commits(prp["prp_id"]))
            drift = calculate_drift(prp, evidence)
            total_drift += drift["drift_percentage"]

            # Update files
            update_prp(prp_file, drift)
            update_serena_memory(prp, evidence, drift)

    avg_drift = total_drift / completed if completed > 0 else 0

    return {
        "batch_id": batch_id,
        "total_prps": len(executed_prps),
        "completed_prps": completed,
        "avg_drift_score": int(avg_drift),
        "execution_quality": interpret_batch_drift(avg_drift)
    }

def interpret_batch_drift(avg_score):
    """Interpret average drift for entire batch"""
    if avg_score < 10:
        return "EXCELLENT (all PRPs executed as planned)"
    elif avg_score < 20:
        return "GOOD (minor deviations, well-managed)"
    elif avg_score < 40:
        return "ACCEPTABLE (some variance, but acceptable)"
    else:
        return "REVIEW NEEDED (significant divergences)"
```

---

## Integration Points

**Receives Input From**: Base Orchestrator (Phase 6: Report & Cleanup)

**Reads From**:
- PRP files (PRPs/feature-requests/)
- Git history (git log)
- CLAUDE.md (context)

**Writes To**:
- Updated PRP files
- Serena memory (.serena/memories/)
- Heartbeat file
- Result file

---

## Error Handling

**PRP Not Found**:
```python
try:
    prp = parse_prp(filepath)
except FileNotFoundError:
    return {"status": "error", "error": f"PRP file not found: {filepath}"}
```

**Git History Issues**:
```python
try:
    commits = find_prp_commits(prp_id)
except subprocess.CalledProcessError as e:
    logger.warning(f"Git command failed: {e}")
    # Continue with empty commits list (PRP marked pending)
    commits = []
```

**Memory Write Failure**:
```python
try:
    update_serena_memory(prp, evidence, drift)
except Exception as e:
    logger.warning(f"Failed to update Serena memory: {e}")
    # Continue anyway (PRP file update is primary)
```

---

## Example: Single PRP Context Update

**Input**: `PRPs/feature-requests/PRP-43.1.1.md` (status: pending)

**Git History**:
```
5f1a3c2 - PRP-43.1.1: Step 1 - Create base-orchestrator.md
7e2b4d1 - PRP-43.1.1: Step 2 - Create generator-subagent.md
9c3a5e2 - PRP-43.1.1: Step 3 - Create executor-subagent.md
1d4b6f3 - PRP-43.1.1: Step 4 - Create reviewer-subagent.md
2e5c7g4 - PRP-43.1.1: Step 5 - Create context-updater-subagent.md
3f6d8h5 - PRP-43.1.1: Complete - All validation gates passed
```

**Processing**:
1. Parse PRP ✓ (status: pending)
2. Find commits ✓ (6 commits found)
3. Status: completed ✓ (final commit found)
4. Collect evidence ✓ (5 files created, 732 lines added)
5. Calculate drift ✓ (8% - EXCELLENT)
6. Update PRP status ✓ (pending → completed)
7. Update Serena memory ✓
8. Generate result ✓

**Output**: Updated PRP-43.1.1.md with execution tracking, Serena memory entry
