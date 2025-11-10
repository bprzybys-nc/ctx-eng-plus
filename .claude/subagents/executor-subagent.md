# Executor Subagent Template

**Purpose**: Execute PRP implementation tasks with full code modification, testing, and validation

**Model**: Haiku 4.5 (handles code writing with checkpoint recovery)

**Invocation**: Task tool with subagent_type=general-purpose

---

## Overview

The executor subagent reads a PRP file and executes its implementation steps end-to-end:

- Parse PRP structure (problem, solution, steps, validation gates)
- Understand dependencies and context
- Execute each implementation step sequentially
- Write/modify code files as needed
- Run tests and validate against gates
- Commit progress to git (checkpoint strategy)
- Report completion or failures

---

## Input Spec

**Input Source**: PRP markdown file (e.g., `PRP-43.1.1.md`)

**PRP File Structure**:
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
dependencies:
  - None
---

## Problem

[Clear problem statement]

## Solution

[High-level solution approach]

## Implementation

### Steps

1. Create .claude/orchestrators/base-orchestrator.md (300 lines)
   - 6-phase orchestration logic
   - Validation gates and error handling
   - Detailed comments

2. Create .claude/subagents/generator-subagent.md (100 lines)
   - Plan parsing
   - Dependency analysis
   - PRP generation

[... remaining steps ...]

### Validation Gates

- [ ] All 5 template files created
- [ ] No syntax errors
- [ ] Total lines: ~730 ± 50
- [ ] Examples provided for each template
- [ ] Clear input/output specs

### Testing Strategy

- Manual code review
- Validate syntax (linting)
- Run example scenarios
- Check file counts and line counts

### Risk Mitigation

- Work in isolated branch
- Create commits after each step
- Test incrementally
```

---

## Processing Steps

### Step 1: Parse PRP File

**Input**: PRP markdown file path

**Output**: PRP dict with all metadata and content

**Parsed PRP Schema**:
```python
{
    "prp_id": "PRP-43.1.1",
    "title": "Phase 1 - Foundation",
    "complexity": "medium",
    "estimated_hours": 8,
    "files_modified": [...],
    "dependencies": [...],
    "problem": "...",
    "solution": "...",
    "steps": ["Step 1...", "Step 2..."],
    "validation_gates": ["[ ] Gate 1", "[ ] Gate 2"],
    "testing_strategy": "...",
    "risk_mitigation": "...",
}
```

### Step 2: Read Context & Dependencies

**Input**: PRP dict + dependencies list

**Output**: Shared context (CLAUDE.md, RULES.md, etc.)

**Dependencies Resolution**:
1. Check if any dependencies are pending (not yet executed)
   - If yes, fail with error message (executor can't proceed)
   - Message: "Cannot execute PRP-43.2.1: depends on PRP-43.1.1 (status: pending)"
2. If all dependencies satisfied, proceed to step 3

**Shared Context Loading**:
```python
def load_shared_context():
    """Load expensive-to-read files once, pass to all decision points"""
    context = {
        "CLAUDE_md": read_file("CLAUDE.md"),
        "RULES_md": read_file(".ce/RULES.md"),
        "existing_files": find_all_files_in_project(),
        "recent_commits": get_recent_git_log(limit=10),
    }
    return context
```

### Step 3: Execute Implementation Steps Sequentially

**Input**: PRP steps + shared context

**Output**: Files created/modified + git commits

**Execution Strategy**:

For each step:
1. **Parse step description** (understand what needs to be done)
2. **Check preconditions** (files exist, dependencies satisfied)
3. **Implement step** (write code, modify files)
4. **Validate step** (run checks if applicable)
5. **Commit checkpoint** (git commit with step name)
6. **Write heartbeat** (update task-{id}.hb with progress)

**Checkpoint Strategy** (git commits per step):
```bash
# After Step 1
git add -A
git commit -m "PRP-43.1.1: Step 1 - Create base-orchestrator.md"

# After Step 2
git add -A
git commit -m "PRP-43.1.1: Step 2 - Create generator-subagent.md"

# ... continue per step ...

# After all steps + validation
git add -A
git commit -m "PRP-43.1.1: Complete - All validation gates passed"
```

**Per-Step Pseudo-code**:
```python
def execute_step(step_number, step_description, prp_context):
    """Execute single step with full error recovery"""

    # Parse what this step needs to do
    step_details = parse_step_description(step_description)

    # Check if files mentioned in step exist (for modifications)
    if step_details["operation"] == "modify":
        for file in step_details["files"]:
            if not file_exists(file):
                logger.error(f"Cannot modify {file}: file not found")
                return False

    # Execute the step
    try:
        if step_details["operation"] == "create":
            for file, content in step_details["files_to_create"]:
                write_file(file, content)
                logger.info(f"Created {file}")

        elif step_details["operation"] == "modify":
            for file, changes in step_details["modifications"]:
                read_and_modify_file(file, changes)
                logger.info(f"Modified {file}")

        elif step_details["operation"] == "run":
            result = run_command(step_details["command"])
            logger.info(f"Ran command: {result}")

    except Exception as e:
        logger.error(f"Step {step_number} failed: {e}")
        return False

    # Validate step (if applicable)
    if step_details.get("validation"):
        try:
            validate_step(step_details["validation"])
        except ValidationError as e:
            logger.error(f"Step {step_number} validation failed: {e}")
            return False

    # Commit progress
    commit_message = f"{prp_context['prp_id']}: Step {step_number} - {step_details['summary']}"
    git_commit(commit_message)

    # Write heartbeat
    write_heartbeat(f"Step {step_number}/{total_steps}: {step_details['summary']}")

    return True
```

### Step 4: Validate Against Gates

**Input**: PRP validation gates + all files created/modified

**Output**: Pass/fail status + detailed report

**Gate Validation Process**:

For each validation gate (checkbox):
1. Parse gate requirement (what needs to be true)
2. Check implementation (run test, count lines, syntax check, etc.)
3. Report pass/fail

**Gate Examples & Checks**:

| Gate | Check | How to Validate |
|------|-------|-----------------|
| `[ ] All 5 files created` | File existence | `ls -la .claude/orchestrators/*.md .claude/subagents/*.md` |
| `[ ] No syntax errors` | Code validation | Run linter on all files |
| `[ ] Total lines: ~730 ± 50` | Line count | `wc -l` all files, sum, verify range |
| `[ ] >90% test coverage` | Test metrics | Run pytest --cov, parse output |
| `[ ] All tests pass` | Test execution | Run pytest, check exit code |

**Validation Gate Parsing**:
```python
def parse_validation_gate(gate_string):
    """Extract requirement from checkbox format"""
    # Input: "[ ] All 5 files created"
    # Output: {"type": "file_count", "expected": 5}

    # Input: "[ ] No syntax errors"
    # Output: {"type": "syntax_check", "files": ["*.md", "*.py"]}

    # Input: "[ ] Total lines: ~730 ± 50"
    # Output: {"type": "line_count", "target": 730, "tolerance": 50}

    # Input: "> 90% test coverage"
    # Output: {"type": "coverage", "minimum": 90}

def validate_gate(gate_requirement, context):
    """Execute validation for single gate"""

    if gate_requirement["type"] == "file_count":
        actual_count = count_files(gate_requirement["files"])
        if actual_count == gate_requirement["expected"]:
            return True, f"✓ Created {actual_count} files"
        else:
            return False, f"✗ Expected {gate_requirement['expected']} files, got {actual_count}"

    elif gate_requirement["type"] == "syntax_check":
        errors = run_linter(gate_requirement["files"])
        if not errors:
            return True, "✓ No syntax errors"
        else:
            return False, f"✗ Syntax errors found: {errors}"

    elif gate_requirement["type"] == "line_count":
        actual_lines = count_total_lines(gate_requirement["files"])
        target = gate_requirement["target"]
        tolerance = gate_requirement["tolerance"]
        min_lines = target - tolerance
        max_lines = target + tolerance

        if min_lines <= actual_lines <= max_lines:
            return True, f"✓ {actual_lines} lines (target: {target} ± {tolerance})"
        else:
            return False, f"✗ {actual_lines} lines (expected {target} ± {tolerance})"

    # ... handle other gate types ...
```

**Validation Report**:
```
Validation Gates - PRP-43.1.1
═══════════════════════════════════════
✓ All 5 files created
✓ No syntax errors
✓ Total lines: 732 (target: 730 ± 50)
✓ Examples provided for each template
✓ Clear input/output specs

Status: ALL GATES PASSED ✓
═══════════════════════════════════════
```

### Step 5: Handle Failures

**Failure Scenarios**:

1. **File not found** (trying to modify non-existent file)
   - Log error and context
   - Suggest fix (create file first, or check path)
   - Mark PRP as failed with clear error message

2. **Syntax error in generated code**
   - Parse error message
   - Show file + line number
   - Suggest correction
   - Retry step or mark failed

3. **Test failure**
   - Run test, capture output
   - Show failure reason
   - Provide debugging guidance
   - Decide: retry or fail

4. **Validation gate fails**
   - Show gate requirement vs actual
   - Provide next steps (e.g., "need 2 more lines to reach target")
   - Can attempt auto-fix or require manual intervention

**Recovery Strategy**:
```python
def execute_with_recovery(step, max_retries=2):
    """Execute step with automatic retry on transient failures"""

    for attempt in range(1, max_retries + 1):
        try:
            return execute_step(step)
        except TransientError as e:
            if attempt < max_retries:
                logger.warning(f"Transient error, retrying: {e}")
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Max retries exceeded: {e}")
                raise
        except PermanentError as e:
            logger.error(f"Permanent error (no retry): {e}")
            raise
```

### Step 6: Final Commit & Status

**Input**: All steps completed or failed

**Output**: Final git commit + completion status

**Final Commit**:
```bash
git add -A
git commit -m "PRP-43.1.1: Complete - All steps executed, validation gates passed"
```

**Status Report**:
```python
{
    "prp_id": "PRP-43.1.1",
    "status": "success",  # or "failed"
    "steps_completed": 5,
    "total_steps": 5,
    "gates_passed": 5,
    "gates_failed": 0,
    "files_created": [...],
    "files_modified": [...],
    "commits": ["PRP-43.1.1: Step 1 - ...", "PRP-43.1.1: Complete - ..."],
    "elapsed_seconds": 1800,
    "tokens_used": 45000
}
```

---

## Output Spec

**Output Files**:
1. All files mentioned in PRP (created or modified)
2. Git commits (one per step + final)
3. Heartbeat file: `task-{id}.hb` (updated every 30 seconds)
4. Result file: `task-{id}.result.json`

**Result JSON Format**:
```json
{
  "task_id": "PRP-43.1.1",
  "prp_id": "PRP-43.1.1",
  "status": "success",
  "steps_completed": 5,
  "total_steps": 5,
  "validation_gates": {
    "passed": 5,
    "failed": 0,
    "details": [
      {
        "gate": "All 5 files created",
        "status": "pass",
        "details": "Created: base-orchestrator.md, generator-subagent.md, ..."
      }
    ]
  },
  "files": {
    "created": [
      ".claude/orchestrators/base-orchestrator.md",
      ".claude/subagents/generator-subagent.md"
    ],
    "modified": []
  },
  "git_commits": [
    "5f1a3c2 - PRP-43.1.1: Step 1 - Create base-orchestrator.md",
    "7e2b4d1 - PRP-43.1.1: Step 2 - Create generator-subagent.md",
    "9c3a5e2 - PRP-43.1.1: Complete - All validation gates passed"
  ],
  "elapsed_seconds": 1800,
  "tokens_used": 45000,
  "errors": []
}
```

---

## Heartbeat Protocol

**Frequency**: Every 30 seconds

**Format**:
```json
{
  "task_id": "PRP-43.1.1",
  "status": "in_progress",
  "progress": "Step 3 of 5: Creating executor-subagent.md",
  "steps_completed": 2,
  "total_steps": 5,
  "tokens_used": 25000,
  "elapsed_seconds": 450,
  "last_update": "2025-11-10T14:45:30Z"
}
```

---

## Error Handling

**Pre-execution Errors**:
- Dependency not satisfied → Fail with clear message
- PRP file malformed → Fail with parsing error
- Missing required fields → Fail with field list

**Execution Errors**:
- Step fails → Log error, mark step failed, halt execution
- File write error → Capture OS error, retry, or fail
- Git commit error → Halt execution immediately
- Test failure → Log test output, decide retry vs fail

**Post-execution Errors**:
- Validation gate fails → Report gate vs actual, decide pass/fail
- Cleanup error → Log but don't fail (already succeeded)

---

## Validation Gates (Standard Template)

All PRPs include these standard gates:

- [ ] All implementation steps completed without errors
- [ ] Code follows project conventions (from CLAUDE.md)
- [ ] All specified files created/modified correctly
- [ ] No syntax errors or linting issues
- [ ] Tests written and passing (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] Git commits created with descriptive messages
- [ ] Ready for code review and merge

---

## Integration Points

**Receives Input From**: Base Orchestrator (Phase 3: Spawn Subagents)

**Reads From**:
- PRP file (input specification)
- CLAUDE.md (project conventions)
- Existing code files (for modifications)

**Writes To**:
- Source code files (create/modify)
- Test files (if applicable)
- Git repository (commits)
- Heartbeat file (status updates)
- Result file (completion status)

**Interacts With**: Git repository + file system

---

## Example: Simple PRP Execution

**Input PRP**:
```yaml
---
prp_id: PRP-44.1.1
title: Create simple module
---

## Implementation

### Steps

1. Create app/utils.py with helper functions
2. Write tests in tests/test_utils.py
3. Run tests and verify all pass

### Validation Gates

- [ ] app/utils.py exists
- [ ] tests/test_utils.py exists
- [ ] All tests pass
- [ ] No syntax errors
```

**Execution Process**:
1. Parse PRP ✓
2. Create app/utils.py ✓
3. Create tests/test_utils.py ✓
4. Run pytest ✓
5. Validate gates:
   - File existence ✓
   - Syntax check ✓
   - Test pass ✓
6. Commit final state ✓
7. Report success ✓

**Commits Created**:
- `PRP-44.1.1: Step 1 - Create app/utils.py`
- `PRP-44.1.1: Step 2 - Create tests/test_utils.py`
- `PRP-44.1.1: Complete - All validation gates passed`
