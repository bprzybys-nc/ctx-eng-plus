# /peer-review - PRP Execution Quality Review

Review executed PRP quality with GitButler integration checks.

## Usage

```bash
/peer-review exe <prp-file-or-id>
```

**Examples**:

```bash
/peer-review exe PRP-6
/peer-review exe PRPs/feature-requests/PRP-6-user-authentication-system.md
```

## What It Does

Validates executed PRP quality across multiple dimensions:

### 1. GitButler Virtual Branch Validation

**Checks**:

- Virtual branch exists: `but branch list | grep "prp-{id}"`
- Branch name format: `prp-{id}-{sanitized-name}` (e.g., `prp-6-user-authentication`)
- No conflicts present: `but status | grep 🔒` (aborts if conflicts detected)
- All commits on correct branch: `but log prp-{id}-{name}`

**Expected**:

```bash
# Good branch name
but branch list
# Output: prp-6-user-authentication

# No conflicts
but status
# Output: No 🔒 icon present

# All phase commits present
but log prp-6-user-authentication
# Output:
#   ● Phase 3: Test coverage (checkpoint-PRP-6-phase3-20251013-120000)
#   ● Phase 2: Error handling (checkpoint-PRP-6-phase2-20251013-110000)
#   ● Phase 1: Core logic (checkpoint-PRP-6-phase1-20251013-100000)
```

**Failure Scenarios**:

```bash
# ❌ Conflicts detected
but status
# Output: 🔒 commit abc123
# Action: Resolve in GitButler UI before review

# ❌ Wrong branch name format
but branch list
# Output: feature-auth (should be: prp-6-user-authentication)
# Action: Rename or recreate branch with correct format

# ❌ Missing commits
but log prp-6-user-authentication
# Output: Only Phase 1 and 2 (missing Phase 3)
# Action: Check if all phases were executed
```

### 2. Phase Completion Validation

**Checks**:

- All phases from blueprint executed
- Each phase has checkpoint tag: `git tag -l "checkpoint-{prp_id}-phase*"`
- Each phase has GitButler commit: `but log prp-{id}-{name}`
- Phase goals met (compares blueprint to implementation)

**Example**:

```bash
# Checkpoint tags exist
git tag -l "checkpoint-PRP-6-phase*"
# Expected:
#   checkpoint-PRP-6-phase1-20251013-100000
#   checkpoint-PRP-6-phase2-20251013-110000
#   checkpoint-PRP-6-phase3-20251013-120000

# GitButler commits match phases
but log prp-6-user-authentication
# Expected: 3 commits (one per phase)
```

### 3. Validation Gates Check

**Checks**:

- All L1-L4 validation gates passed
- Self-healing attempts logged (if any)
- Confidence score >= 8/10
- No unresolved escalations

**Thresholds**:

- **10/10**: All L1-L4 passed on first attempt - ✅ PRODUCTION READY
- **9/10**: All passed, 1-2 self-heals - ✅ PRODUCTION READY
- **8/10**: All passed, 3+ self-heals - ⚠️ REVIEW RECOMMENDED
- **7/10**: L1-L3 passed, L4 skipped - ⚠️ REVIEW REQUIRED
- **<7/10**: Validation failures - ❌ NEEDS FIXES

### 4. Code Quality Review

**Checks**:

- Files created/modified match blueprint
- Functions implemented match blueprint
- No debug code left (print statements, console.log)
- No TODO/FIXME comments
- Follows project conventions

### 5. Context Drift Check

**Checks**:

- Post-execution drift < 10%
- Auto-sync completed (if enabled)
- Ephemeral state cleaned (via PRP-2)

**Example**:

```bash
cd tools
uv run ce context health --json | jq '.drift_score'
# Expected: < 10.0
```

## Review Output

```json
{
  "prp_id": "PRP-6",
  "review_type": "exe",
  "timestamp": "2025-10-29T12:00:00Z",
  "gitbutler_checks": {
    "branch_exists": true,
    "branch_name_format": "✅ prp-6-user-authentication",
    "conflicts_detected": false,
    "commits_count": 3,
    "commits_match_phases": true
  },
  "phase_completion": {
    "phases_expected": 3,
    "phases_completed": 3,
    "checkpoint_tags": [
      "checkpoint-PRP-6-phase1-20251013-100000",
      "checkpoint-PRP-6-phase2-20251013-110000",
      "checkpoint-PRP-6-phase3-20251013-120000"
    ],
    "missing_phases": []
  },
  "validation_gates": {
    "confidence_score": "10/10",
    "self_healing_attempts": 2,
    "escalations": 0,
    "status": "PRODUCTION READY"
  },
  "code_quality": {
    "files_match_blueprint": true,
    "functions_match_blueprint": true,
    "debug_code_found": false,
    "todos_found": 0
  },
  "context_drift": {
    "drift_score": 5.2,
    "auto_sync_completed": true,
    "cleanup_completed": true
  },
  "overall_status": "✅ APPROVED",
  "recommendations": []
}
```

## CLI Command

```bash
cd tools
uv run ce peer-review exe <prp-id-or-path>

# JSON output
uv run ce peer-review exe PRP-6 --json

# Verbose (include full validation details)
uv run ce peer-review exe PRP-6 --verbose
```

## Hook Integration

The peer-review command checks the same hooks that execute-prp uses:

### Active Hooks (from .claude/settings.local.json)

- **PreToolUse (git_git_commit)**: Runs `but status` before commits - Shows conflicts (🔒)
- **PreToolUse (Edit|Write)**: Reminds to commit to appropriate virtual branch

The review validates:

1. No 🔒 icons present in `but status` output
2. All file modifications committed to correct virtual branch
3. GitButler workspace integration successful

## Common Issues

### Issue: "Branch not found"

```bash
# Symptom
but branch list | grep prp-6
# Output: (empty)

# Solution: Check if branch was deleted or wrong ID
but branch list
git branch | grep prp-6
```

### Issue: "Conflicts detected"

```bash
# Symptom
but status
# Output: 🔒 commit abc123

# Solution: Resolve in GitButler UI
# 1. Open GitButler UI
# 2. Navigate to conflicted branch
# 3. Resolve conflicts
# 4. Re-run peer-review
```

### Issue: "Missing phase commits"

```bash
# Symptom
but log prp-6-feature
# Output: Only 2 of 3 phases

# Solution: Check execution logs
# - Was execution interrupted?
# - Did phase validation fail?
# - Run execute-prp with --start-phase N to resume
```

### Issue: "High drift score"

```bash
# Symptom
cd tools && uv run ce context health
# Output: Drift: 45%

# Solution: Run manual sync
cd tools && uv run ce context post-sync PRP-6
```

## Review Criteria

### ✅ APPROVED Criteria

- GitButler branch exists with correct format
- No conflicts (🔒 icon)
- All phases completed
- All checkpoint tags exist
- Confidence score >= 8/10
- Drift < 10%
- No debug code/TODOs

### ⚠️ NEEDS REVIEW Criteria

- Confidence score 7/10
- Drift 10-15%
- 3+ self-healing attempts
- L4 validation skipped

### ❌ REJECTED Criteria

- Conflicts unresolved
- Missing phases
- Confidence score < 7/10
- Drift > 15%
- Debug code present
- Validation failures

## Workflow Integration

### After /execute-prp

```bash
# 1. Execute PRP
/execute-prp PRP-6

# 2. Review execution quality
/peer-review exe PRP-6

# 3. If approved, create PR
# (via GitButler UI or gh CLI)

# 4. If needs review, address issues
# - Fix conflicts: GitButler UI
# - Reduce drift: cd tools && uv run ce context post-sync PRP-6
# - Fix validation: cd tools && uv run ce execute PRP-6 --start-phase N
```

### With GitButler Workflow

```bash
# Check branch status
but status

# View commits
but log prp-6-user-authentication

# Review execution
/peer-review exe PRP-6

# If approved, merge in GitButler UI or push
but branch push prp-6-user-authentication
```

## Tips

1. **Run immediately after execution** for fresh context
2. **Check GitButler UI** for visual conflict inspection
3. **Use --verbose** for detailed validation breakdowns
4. **Trust confidence scores**: 10/10 = production ready
5. **Review self-healing logs** to understand fixes applied
6. **Check drift score** to ensure context health
7. **Verify checkpoint tags** for rollback capability

## Implementation Details

- **Module**: `tools/ce/peer_review.py`
- **Tests**: `tools/tests/test_peer_review.py`
- **Integration**: Uses GitButler `but` commands for branch validation
- **Hooks**: Validates PreToolUse hooks executed correctly
- **Context**: Checks drift score via `ce context health`

## Related Commands

- `/execute-prp <prp-file>` - Execute PRP with GitButler integration
- `but status` - Check conflicts and branch status
- `but log <branch>` - View commit history
- `ce context health` - Check context drift
- `ce prp restore <prp-id> [phase]` - Rollback to checkpoint

## External References

- [GitButler Reference](../examples/GITBUTLER-REFERENCE.md) - Full GitButler guide
- [PRP-4](../PRPs/feature-requests/PRP-4-execute-prp-orchestration.md) - Execute-PRP implementation
- [PRP-2](../PRPs/feature-requests/PRP-2-prp-state-isolation.md) - Checkpoint system
- [PRP-5](../PRPs/feature-requests/PRP-5-context-sync-integration.md) - Context sync
