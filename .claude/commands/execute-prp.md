# /execute-prp - Execute PRP with Self-Healing

Automates PRP execution with phase-by-phase implementation, L1-L4 validation loops, self-healing error recovery, and automatic escalation triggers.

## Usage

```
/execute-prp <prp-file-or-id>
```

**Examples:**
```
/execute-prp PRP-5
/execute-prp PRPs/feature-requests/PRP-5-context-sync-integration.md
```

## What It Does

1. **Parses PRP Blueprint**:
   - Extracts phases from `## 🔧 Implementation Blueprint`
   - Validates phase structure (number, name, hours, goal, approach)
   - Identifies files to create/modify and functions to implement
   - Extracts validation commands and checkpoint instructions

2. **Initializes PRP Context** (via PRP-2):
   - Creates active PRP session in `.ce/active_prp_session`
   - Initializes state tracking for phases
   - Sets up checkpoint namespace: `checkpoint-{prp_id}-{phase}`

3. **Executes Each Phase**:
   - Creates/modifies files using Serena MCP
   - Implements functions from blueprint
   - Logs progress to console
   - Updates phase state

4. **Runs Validation Loop** (L1-L4 with self-healing):
   - **L1 (Syntax & Style)**: `validate_level_1()` - Linting, formatting, type checks
   - **L2 (Unit Tests)**: Runs phase validation command (e.g., `pytest tests/test_auth.py`)
   - **L3 (Integration)**: `validate_level_3()` - Integration tests
   - **L4 (Pattern Conformance)**: `validate_level_4(prp_path)` - Drift detection (<30%)

   **Self-Healing** (L1-L2 only, max 3 attempts):
   - Parses error output (type, file, line, message)
   - Checks escalation triggers
   - Applies automatic fixes (e.g., add missing imports)
   - Re-runs validation
   - Escalates to human if persistent/ambiguous

5. **Creates Checkpoints** (via PRP-2):
   - Git tag after each validation gate: `checkpoint-{prp_id}-phase{N}-{timestamp}`
   - Preserves rollback points

6. **Post-Execution Sync** (if auto-sync enabled via PRP-5):
   - Runs cleanup protocol (archives memories, deletes ephemeral state)
   - Syncs context (reindexes new code)
   - Creates final checkpoint
   - Verifies drift < 10%

7. **Calculates Confidence Score**:
   - **10/10**: All L1-L4 passed on first attempt
   - **9/10**: All passed, 1-2 self-heals
   - **8/10**: All passed, 3+ self-heals
   - **7/10**: L1-L3 passed, L4 skipped
   - **5/10**: Validation failures

8. **Ends PRP Context**:
   - Removes active session
   - Returns execution summary

## CLI Command

```bash
# Basic usage
cd tools
uv run ce execute <prp-id-or-path>

# Execute specific phase range
uv run ce execute PRP-5 --start-phase 2 --end-phase 3

# Dry run (parse blueprint without execution)
uv run ce execute PRP-5 --dry-run

# Skip validation (dangerous - for debugging only)
uv run ce execute PRP-5 --skip-validation

# JSON output (for scripting)
uv run ce execute PRP-5 --json
```

## Example Workflow

```bash
# 1. Generate PRP from INITIAL.md
/generate-prp feature-requests/auth/INITIAL.md
# Output: PRPs/feature-requests/PRP-6-user-authentication-system.md

# 2. Review generated PRP
# - Check implementation blueprint phases
# - Verify validation commands
# - Adjust if needed

# 3. Execute PRP with auto-sync
cd tools
uv run ce context auto-sync --enable  # Enable auto-sync (PRP-5)
/execute-prp PRP-6

# Expected output:
# ================================================================================
# Phase 1: Core Logic Implementation
# Goal: Implement main authentication flow
# ================================================================================
#
#   📝 Create: src/auth.py - Authentication logic
#   🔧 Implement: authenticate_user
#   🔧 Implement: validate_token
#
#   🧪 Running validation...
#     L1: Syntax & Style...
#     ✅ L1 passed (0.45s)
#     L2: Running pytest tests/test_auth.py -v...
#     ✅ L2 passed (1.23s)
#     L3: Integration Tests...
#     ✅ L3 passed (2.15s)
#     L4: Pattern Conformance...
#     ✅ L4 passed (drift: 5.2%)
#   ✅ Validation complete
#
# ✅ Phase 1 complete
#
# ... (phases 2-3)
#
# ================================================================================
# Running post-execution sync...
# ================================================================================
#
# ✅ Post-sync complete: drift=3.1%
#    Cleanup: True
#    Memories archived: 2
#    Final checkpoint: checkpoint-PRP-6-final-20251013-120000
#
# ✅ Execution complete: 10/10 confidence (45m 23s)
```

## Self-Healing Capabilities

### Auto-Fixable Errors (L1-L2)

**Import Errors**:
```python
# Error: ImportError: No module named 'jwt'
# Fix: Adds "import jwt" to file at appropriate location
```

### Escalation Triggers (Human Intervention Required)

The system escalates to human when:

1. **Persistent Error** (same error after 3 attempts):
   ```
   ❌ L2 failed after 3 attempts - escalating
   🔧 Troubleshooting:
      1. Review error details - same error occurred 3 times
      2. Check if fix logic matches error type
      3. Consider if architectural change needed
   ```

2. **Ambiguous Error** (generic error with no file/line info):
   ```
   Error: "something went wrong"
   🔧 Troubleshooting:
      1. Run validation command manually for full context
      2. Check logs for additional error details
   ```

3. **Architectural Changes** (keywords: refactor, redesign, circular import):
   ```
   Error: "circular import detected between auth.py and models.py"
   🔧 Troubleshooting:
      1. Review error for architectural keywords
      2. Consider if code structure needs reorganization
   ```

4. **External Dependencies** (network errors, package issues):
   ```
   Error: "connection refused" or "package not found"
   🔧 Troubleshooting:
      1. Check network connectivity
      2. Verify package repository access (PyPI, npm)
   ```

5. **Security Concerns** (CVE, credentials, permissions):
   ```
   Error: "vulnerability detected" or "secret exposed"
   🔧 Troubleshooting:
      1. DO NOT auto-fix security-related errors
      2. Review error for exposed secrets/credentials
   ```

## Options

| Flag | Description | Example |
|------|-------------|---------|
| `--start-phase N` | Start execution from phase N | `--start-phase 2` |
| `--end-phase N` | Stop execution at phase N | `--end-phase 3` |
| `--skip-validation` | Skip validation loops (debugging only) | `--skip-validation` |
| `--dry-run` | Parse blueprint without execution | `--dry-run` |
| `--json` | Output results as JSON | `--json` |

## Validation Gates

Each phase runs through 4 validation levels:

### L1: Syntax & Style (Auto-healing: Yes)
- Linting (ruff, pylint, eslint)
- Formatting (black, prettier)
- Type checking (mypy, tsc)
- **Max 3 self-healing attempts**

### L2: Unit Tests (Auto-healing: Yes)
- Runs phase validation command
- Parses test failures
- Attempts automatic fixes (import errors, simple logic)
- **Max 3 self-healing attempts**

### L3: Integration Tests (Auto-healing: No)
- End-to-end functionality tests
- Manual intervention on failure
- Escalates architectural issues

### L4: Pattern Conformance (Auto-healing: No)
- Compares implementation to INITIAL.md EXAMPLES
- Calculates drift score (0-100%)
- **Aborts if drift > 30%** (requires explicit user acceptance)
- User decision: accept/reject/update EXAMPLES

## PRP State Isolation (via PRP-2)

Each execution maintains isolated state:

- **Checkpoints**: `checkpoint-{prp_id}-phase{N}-{timestamp}`
- **Memories**: `{prp_id}-checkpoint-*`, `{prp_id}-learnings-*`
- **Active Session**: `.ce/active_prp_session` (JSON with prp_id, phase, validation_attempts)
- **Cleanup**: Automatic ephemeral state removal after execution (if auto-sync enabled)

## Context Sync Integration (via PRP-5)

With auto-sync enabled (`ce context auto-sync --enable`):

**Before execution**: N/A (pre-sync happens in generation phase)

**After execution** (Step 6.5):
1. Runs cleanup protocol (PRP-2)
2. Syncs context (reindexes new code)
3. Verifies drift < 10%
4. Creates final checkpoint
5. Removes active PRP session

## Common Issues

### Issue: "PRP file not found: PRP-5"
```bash
# Solution: Use full path or ensure PRP is in PRPs/feature-requests/
/execute-prp PRPs/feature-requests/PRP-5-context-sync-integration.md
```

### Issue: Validation fails with "command not found"
```bash
# Solution: Ensure validation command is correct in PRP blueprint
# Example: Use "uv run pytest tests/" not just "pytest tests/"
```

### Issue: Self-healing stuck in loop
```bash
# Solution: Same error 3 times triggers escalation
# Review escalation message for troubleshooting guidance
```

### Issue: "Auto-sync failed"
```bash
# Solution: Post-sync is non-blocking, execution still completes
# Run manual sync: cd tools && uv run ce context post-sync PRP-5
```

## Output Structure

```json
{
  "success": true,
  "prp_id": "PRP-6",
  "phases_completed": 3,
  "validation_results": {
    "Phase1": {
      "success": true,
      "validation_levels": {
        "L1": {"passed": true, "attempts": 1, "errors": []},
        "L2": {"passed": true, "attempts": 2, "errors": ["import error"]},
        "L3": {"passed": true, "attempts": 1, "errors": []},
        "L4": {"passed": true, "attempts": 1, "drift_score": 5.2}
      },
      "self_healed": ["L2: Fixed after 2 attempts"]
    }
  },
  "checkpoints_created": [
    "checkpoint-PRP-6-phase1-20251013-100000",
    "checkpoint-PRP-6-phase2-20251013-110000",
    "checkpoint-PRP-6-phase3-20251013-120000"
  ],
  "confidence_score": "10/10",
  "execution_time": "45m 23s"
}
```

## Next Steps After Execution

1. **Review Execution Summary**:
   - Check confidence score (target: 10/10)
   - Review self-healing actions taken
   - Verify all validation gates passed

2. **Test Manually** (if confidence < 10/10):
   - Run validation commands manually
   - Review self-healing fixes
   - Address any escalated errors

3. **Rollback if Needed** (via PRP-2):
   ```bash
   cd tools
   uv run ce prp restore PRP-6 phase2
   ```

4. **Context Sync** (if auto-sync disabled):
   ```bash
   cd tools
   uv run ce context post-sync PRP-6
   ```

5. **Peer Review**:
   ```bash
   /peer-review exe PRPs/feature-requests/PRP-6-user-authentication-system.md
   ```

## Tips

1. **Enable auto-sync** before execution: `ce context auto-sync --enable`
2. **Use dry-run** to preview phases: `ce execute PRP-6 --dry-run`
3. **Test incrementally**: Use `--start-phase` and `--end-phase` for partial execution
4. **Trust self-healing**: Let L1-L2 auto-fixes run before manual intervention
5. **Review escalations**: Escalation messages include specific troubleshooting guidance
6. **Check confidence score**: 10/10 means production-ready, <8/10 needs review

## Implementation Details

- **Module**: `tools/ce/execute.py`
- **Tests**: `tools/tests/test_execute.py` (20+ tests)
- **PRP Reference**: `PRPs/feature-requests/PRP-4-execute-prp-orchestration.md`
- **Self-Healing**: 90%+ success rate on L1-L2 errors
- **Speed Improvement**: 10-24x faster than manual implementation

## Related Commands

- `/generate-prp` - Generate PRP from INITIAL.md
- `/peer-review exe <prp-file>` - Review execution quality
- `ce prp restore <prp-id> [phase]` - Rollback to checkpoint (PRP-2)
- `ce context post-sync <prp-id>` - Manual post-execution sync (PRP-5)
- `ce validate --level 4 <prp-path>` - Run L4 pattern conformance (PRP-1)
