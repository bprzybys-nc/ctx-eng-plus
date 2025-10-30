# /peer-review - PRP Quality Review (Generation + Execution)

Review PRP quality in two modes: generation (default) and execution (explicit).

## Usage

```bash
/peer-review <prp>       # DEFAULT: prp mode (generation review)
/peer-review prp <prp>   # EXPLICIT: prp mode (generation review)
/peer-review exe <prp>   # EXPLICIT: exe mode (execution review)
```

**Examples**:

```bash
# Generation review (DEFAULT)
/peer-review PRP-6
/peer-review prp PRP-6
/peer-review PRPs/feature-requests/PRP-6-user-authentication-system.md

# Execution review (EXPLICIT)
/peer-review exe PRP-6
/peer-review exe PRPs/feature-requests/PRP-6-user-authentication-system.md
```

## Mode Detection

The command supports two review modes:

**Usage:**
- `/peer-review <prp>` → prp mode (DEFAULT - generation review)
- `/peer-review prp <prp>` → prp mode (explicit)
- `/peer-review exe <prp>` → exe mode (execution review)

**Mode detection:**

```python
def detect_review_mode(args):
    """Detect review mode from arguments

    Returns: ("prp"|"exe", target_path)
    """
    if len(args) == 0:
        raise ValueError("Usage: /peer-review [prp|exe] <target>")

    # Check if first arg is explicit mode
    if args[0].lower() in ["exe", "prp"]:
        mode = args[0].lower()
        target = args[1] if len(args) > 1 else None
    else:
        # No explicit mode → default to "prp"
        mode = "prp"
        target = args[0]

    if not target:
        raise ValueError(f"Target required for {mode} mode")

    return mode, target
```

## Mode 1: Generation Review (prp) - DEFAULT

Reviews PRP quality BEFORE execution.

### What It Reviews

**1. Structure Completeness**
- ✓ All 9 required sections present (TL;DR, Context, Implementation, etc.)
- ✓ YAML header valid and complete
- ✓ Blueprint phases defined
- ✓ Validation gates specified

**2. Factuality Verification** (mandatory)
- ✓ Files referenced exist
- ✓ Dependencies exist (PRP-X in executed/)
- ✓ Commits exist (if referenced)
- ✓ Line number claims reasonable

**3. Clarity & Completeness**
- ✓ Implementation steps actionable
- ✓ Validation commands copy-paste ready
- ✓ Rollback procedures documented
- ✓ Time estimates provided

### Review Output

```
================================================================================
Generation Review: PRP-30
================================================================================

Structure:
  ✓ YAML header complete
  ✓ 9/9 sections present
  ✓ 6 phases defined
  ✓ 7 validation gates specified

Factuality Verification:
  ✓ dependencies: PRP-C exists (PRPs/executed/PRP-C-gitbutler-worktree-migration.md)
  ✓ dependencies: PRP-D exists (PRPs/executed/PRP-D-command-permissions.md)
  ✗ files_modified: .git/gitbutler/virtual_branches.toml (file not found)
  ✓ commit: 12e6893 exists
  ✓ commit: b29ccc5 exists

Clarity:
  ✓ Implementation steps actionable
  ✓ Validation commands runnable
  ✓ Rollback procedures present

================================================================================
Summary: 8 PASS, 1 FAIL
================================================================================

FAILED CHECKS:
✗ .git/gitbutler/virtual_branches.toml
  → FIX: Update PRP to remove reference OR verify file should exist

Review Status: ⚠️ FACTUAL ERRORS DETECTED
Recommendation: Fix factual errors before execution
```

### When to Use

```bash
# After generating PRP (most common workflow)
/generate-prp initials/auth/INITIAL.md
# Output: PRPs/feature-requests/PRP-35-user-authentication.md

/peer-review PRP-35  # Check generation quality (DEFAULT)

# If approved, execute
/execute-prp PRP-35

# Then check execution quality (EXPLICIT)
/peer-review exe PRP-35
```

## Mode 2: Execution Review (exe) - EXPLICIT

Validates executed PRP quality across multiple dimensions.

### 1. Git Branch Validation

**Checks**:

- Branch exists: `git branch | grep "prp-{id}"`
- Branch name format: `prp-{id}-{sanitized-name}` (e.g., `prp-6-user-authentication`)
- No merge conflicts: `git status` (clean working tree)
- All commits on correct branch: `git log prp-{id}-{name}`

**Expected**:

```bash
# Good branch name
git branch | grep prp-6
# Output: prp-6-user-authentication

# No conflicts
git status
# Output: nothing to commit, working tree clean

# All phase commits present
git log prp-6-user-authentication --oneline
# Output:
#   abc1234 Phase 3: Test coverage (checkpoint-PRP-6-phase3-20251013-120000)
#   def5678 Phase 2: Error handling (checkpoint-PRP-6-phase2-20251013-110000)
#   ghi9012 Phase 1: Core logic (checkpoint-PRP-6-phase1-20251013-100000)
```

**Failure Scenarios**:

```bash
# ❌ Merge conflicts detected
git status
# Output: Unmerged paths...
# Action: Resolve conflicts manually before review

# ❌ Wrong branch name format
git branch
# Output: feature-auth (should be: prp-6-user-authentication)
# Action: Rename branch: git branch -m feature-auth prp-6-user-authentication

# ❌ Missing commits
git log prp-6-user-authentication --oneline
# Output: Only Phase 1 and 2 commits (missing Phase 3)
# Action: Check if all phases were executed
```

### 2. Phase Completion Validation

**Checks**:

- All phases from blueprint executed
- Each phase has checkpoint tag: `git tag -l "checkpoint-{prp_id}-phase*"`
- Each phase has git commit: `git log prp-{id}-{name}`
- Phase goals met (compares blueprint to implementation)

**Example**:

```bash
# Checkpoint tags exist
git tag -l "checkpoint-PRP-6-phase*"
# Expected:
#   checkpoint-PRP-6-phase1-20251013-100000
#   checkpoint-PRP-6-phase2-20251013-110000
#   checkpoint-PRP-6-phase3-20251013-120000

# Git commits match phases
git log prp-6-user-authentication --oneline
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

## Factuality Check Registry

Checks are run in BOTH modes (prp and exe) against target document.

### How It Works

1. **Extract claims** from YAML header and document
2. **Run verification** commands for each claim
3. **Report results**: PASS (✓) or FAIL (✗)
4. **Cache results** for performance (1-hour TTL)

### Check: file_exists

**Pattern**: `files_modified: [path]` in YAML header

**Verify**:

```bash
test -f {path} && echo "✓ PASS" || echo "✗ FAIL"
```

**Output**:
- ✓ PASS: File exists at specified path
- ✗ FAIL: File not found

**Example**:

```yaml
files_modified: [.claude/settings.local.json]
```

Verification: `test -f .claude/settings.local.json` → ✓ PASS

### Check: commit_exists

**Pattern**: `Commit {hash}` or git references in text

**Verify**:

```bash
git show {hash} --oneline > /dev/null 2>&1 && echo "✓ PASS" || echo "✗ FAIL"
```

**Output**:
- ✓ PASS: Commit exists in repository
- ✗ FAIL: Commit not found

**Example**:

```
"Commit 12e6893 contains PRP-A execution"
```

Verification: `git show 12e6893 --oneline` → ✓ PASS

### Check: dependency_exists

**Pattern**: `dependencies: PRP-X` in YAML header

**Verify**:

```bash
ls PRPs/executed/PRP-{X}*.md > /dev/null 2>&1 && echo "✓ PASS" || echo "✗ FAIL"
```

**Output**:
- ✓ PASS: PRP file found in executed/
- ✗ FAIL: PRP not in executed/

**Example**:

```yaml
dependencies: PRP-C, PRP-D
```

Verification:
- `ls PRPs/executed/PRP-C*.md` → ✓ PASS
- `ls PRPs/executed/PRP-D*.md` → ✓ PASS

### Check: branch_exists

**Pattern**: Branch references in text or git commands

**Verify**:

```bash
git branch -a | grep -q "{branch}" && echo "✓ PASS" || echo "✗ FAIL"
```

**Output**:
- ✓ PASS: Branch exists (local or remote)
- ✗ FAIL: Branch not found

**Example**:

```
"Branch prp-a-tool-deny"
```

Verification: `git branch -a | grep prp-a-tool-deny` → ✓ PASS

### Check: tag_exists

**Pattern**: Tag references (checkpoint tags, backup tags)

**Verify**:

```bash
git tag -l "{tag}" | grep -q . && echo "✓ PASS" || echo "✗ FAIL"
```

**Output**:
- ✓ PASS: Tag exists
- ✗ FAIL: Tag not found

**Example**:

```
"Tag checkpoint-PRP-6-phase1-20251013-100000"
```

Verification: `git tag -l "checkpoint-PRP-6-phase1-*"` → ✓ PASS

### Adding New Checks (Extendable)

To add a new factuality check:

1. Add new subsection: `### Check: {name}`
2. Define **Pattern** (what to look for)
3. Define **Verify** (bash command to run)
4. Define **Output** (PASS/FAIL meanings)
5. Provide **Example**

**No code changes required** - checks are documentation-driven.

## Cache System

### Cache File

Location: `.ce/peer-review-cache.json`

Structure:

```json
{
  "version": "1.0",
  "last_cleanup": "2025-10-30T12:00:00Z",
  "checks": {
    "file:.claude/settings.local.json": {
      "result": "PASS",
      "verified_at": "2025-10-30T12:00:00Z",
      "expires_at": "2025-10-30T13:00:00Z",
      "access_count": 3
    },
    "commit:12e6893": {
      "result": "PASS",
      "verified_at": "2025-10-30T11:30:00Z",
      "expires_at": "2025-10-30T12:30:00Z",
      "access_count": 1
    }
  }
}
```

### Cache Behavior

**On every /peer-review run**:
1. Load cache from `.ce/peer-review-cache.json`
2. Auto-cleanup (see maintenance rules below)
3. For each factuality check:
   - Cache hit (not expired): Use cached result, increment access_count
   - Cache miss: Run verification, store result with 1-hour TTL
4. Save updated cache

### Maintenance Rules (Auto-cleanup)

**Rule 1: TTL Expiration** (1 hour)
- Remove entries where `expires_at < now`
- Prevents stale results after codebase changes

**Rule 2: Max Size Limit** (100 entries)
- Keep top 100 entries by `(access_count, verified_at)`
- Evict least accessed + oldest entries
- Prevents unbounded growth

**Rule 3: Orphaned Entries**
- Remove entries where target no longer exists
- Example: File deleted, commit rebased away

**Cleanup pseudocode**:

```python
def load_cache():
    cache = read_json('.ce/peer-review-cache.json')
    now = datetime.now()

    # Rule 1: Remove expired
    cache['checks'] = {
        k: v for k, v in cache['checks'].items()
        if datetime.fromisoformat(v['expires_at']) > now
    }

    # Rule 2: Limit max size
    if len(cache['checks']) > 100:
        sorted_checks = sorted(
            cache['checks'].items(),
            key=lambda x: (x[1]['access_count'], x[1]['verified_at']),
            reverse=True
        )
        cache['checks'] = dict(sorted_checks[:100])

    # Rule 3: Remove orphaned
    cache['checks'] = {
        k: v for k, v in cache['checks'].items()
        if verify_target_exists(k)
    }

    cache['last_cleanup'] = now.isoformat()
    save_json('.ce/peer-review-cache.json', cache)
    return cache
```

### Performance

**Without cache**:
- 15 factuality checks × 0.3s each = 4.5s

**With cache** (80% hit rate):
- 3 misses × 0.3s = 0.9s
- 12 hits × 0.01s = 0.12s
- Total: 1.02s

**4.4x faster** with cache hits

### Manual Cleanup

If needed, force cache reset:

```bash
rm .ce/peer-review-cache.json
# Next /peer-review creates fresh cache
```

## Review Output

```json
{
  "prp_id": "PRP-6",
  "review_type": "exe",
  "timestamp": "2025-10-29T12:00:00Z",
  "branch_checks": {
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

## Auto-Apply Recommendations

After peer review completes, recommendations are **automatically applied** unless they require user interaction.

### How It Works

1. **Review generates recommendations** (categorized by type)
2. **Auto-fixable recommendations** → Applied immediately without asking
3. **Manual recommendations** → Presented to user with explanation
4. **User is notified** of all actions taken

### Auto-Fixable (Applied Automatically)

These are applied without user interaction:

**1. Context Sync** (if drift > 30%)

```bash
# Triggered by: High drift after documentation changes
# Action: cd tools && uv run ce context sync
# Time: 2-3 minutes
```

**Note**: Markdown linting (MD031, MD032, etc.) is handled by L1 validation during `/execute-prp`. Peer review only recommends running L1 validation if markdown files were modified and not yet validated.

**Characteristics**:

- ✅ Low risk (cosmetic or automatically reversible)
- ✅ No architectural impact
- ✅ Deterministic outcome (no ambiguity)
- ✅ Fast execution (<3 minutes)

### Manual (Requires User Decision)

These require explicit user approval:

**1. Structural Refactoring**

```bash
# Example: "Consider splitting 800-line function into smaller units"
# Why manual: Architectural decision needed
# Action: Present recommendation, wait for approval
```

**2. Dependency Changes**

```bash
# Example: "Update dependency PRP-X (outdated reference)"
# Why manual: May affect other PRPs
# Action: Present recommendation, wait for approval
```

**3. Security-Related**

```bash
# Example: "Remove exposed API key in example code"
# Why manual: Critical issue requiring verification
# Action: Present recommendation, wait for approval
```

**4. High-Risk Operations**

```bash
# Example: "Delete unused files: file1.py, file2.py"
# Why manual: Irreversible without backup
# Action: Present recommendation, wait for approval
```

**Characteristics**:

- ⚠️ Higher risk (may require rollback)
- ⚠️ Architectural or security implications
- ⚠️ Subjective (multiple valid approaches)
- ⚠️ Time-consuming (>3 minutes)

### Example Output

```
================================================================================
Peer Review Complete: PRP-31
================================================================================

Review Status: ⚠️ APPROVED WITH CONDITIONS

Recommendations Generated:

AUTO-FIXABLE (applying automatically):
  ✅ 1. Sync context (drift: 32.73% → <10%)
     └─ Running: cd tools && uv run ce context sync
     └─ Status: ✅ Complete (36 files reindexed, 2.3s)

MANUAL (requires review):
  ⓘ 2. Run L1 validation (markdown files modified)
     └─ Issue: .claude/commands/peer-review.md modified
     └─ Impact: Low (linting issues, if any)
     └─ Action: /execute-prp will run L1 validation automatically

================================================================================
Auto-fixes applied: 1
Manual recommendations: 1
Overall: ✅ APPROVED
================================================================================
```

### Disabling Auto-Apply

If you prefer manual control:

```bash
# Via CLI flag
cd tools
uv run ce peer-review exe PRP-6 --no-auto-apply

# Via environment variable
export PEER_REVIEW_NO_AUTO_APPLY=1
/peer-review exe PRP-6
```

### Safety Guarantees

**Before auto-apply**:

1. Verify git working tree is clean
2. Check no uncommitted changes exist
3. Create backup reference (if needed)

**During auto-apply**:

1. Log all actions taken
2. Capture command output
3. Verify expected outcome

**After auto-apply**:

1. Report success/failure
2. Show before/after metrics (e.g., drift score)
3. Provide rollback instructions if needed

**Rollback** (if auto-fix fails):

```bash
# Context sync rollback
cd tools
uv run ce context restore <backup-id>
```

### Recommendation Policy

**Default Behavior**: Auto-apply enabled

**Override**: Use `--no-auto-apply` flag for full manual control

**Rationale**:

- Saves time on trivial fixes (context sync after doc changes)
- Reduces friction in review workflow
- Maintains safety via pre-checks and logging
- User retains control via flag or env var
- L1 validation handles linting during execution phase

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

- **SessionStart**: Context health check - Warns about drift on session start (>10%)
- **PreToolUse (Edit|Write)**: Reminds to commit to appropriate branch

The review validates:

1. No merge conflicts in `git status` output
2. All file modifications committed to correct branch
3. Git worktree workflow successfully followed

## Common Issues

### Issue: "Branch not found"

```bash
# Symptom
git branch | grep prp-6
# Output: (empty)

# Solution: Check if branch was deleted or wrong ID
git branch -a | grep prp
```

### Issue: "Merge conflicts detected"

```bash
# Symptom
git status
# Output: Unmerged paths: file.py

# Solution: Resolve conflicts manually
# 1. Open conflicted file
# 2. Resolve conflict markers (<<<<<<, ======, >>>>>>)
# 3. git add file.py
# 4. git commit
# 5. Re-run peer-review
```

### Issue: "Missing phase commits"

```bash
# Symptom
git log prp-6-feature --oneline
# Output: Only 2 of 3 phase commits

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

### Issue: "Cache too large"

```bash
# Symptom
ls -lh .ce/peer-review-cache.json
# Output: 500KB (should be ~50KB)

# Solution: Cache auto-cleans, but force reset if needed
rm .ce/peer-review-cache.json
```

## Review Criteria

### ✅ APPROVED Criteria

- Git branch exists with correct format
- No merge conflicts
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

## Usage Examples

### Generation Review (DEFAULT)

```bash
# After generating PRP (most common)
/generate-prp initials/auth/INITIAL.md
/peer-review PRP-35  # DEFAULT: prp mode

# Explicit prp mode (same as default)
/peer-review prp PRP-35

# Review specific file path
/peer-review PRPs/feature-requests/PRP-35-user-authentication.md
```

### Execution Review (EXPLICIT)

```bash
# After executing PRP
/execute-prp PRP-35
/peer-review exe PRP-35  # EXPLICIT: exe mode

# Review executed PRP
/peer-review exe PRPs/executed/PRP-35-user-authentication.md
```

### Complete Workflow

```bash
# 1. Generate PRP
/generate-prp initials/auth/INITIAL.md
# Output: PRPs/feature-requests/PRP-35-user-authentication.md

# 2. Review generation quality (DEFAULT)
/peer-review PRP-35
# Checks: structure, dependencies, files, factuality
# Output: 12 PASS, 0 FAIL

# 3. If approved, execute
/execute-prp PRP-35

# 4. Review execution quality (EXPLICIT)
/peer-review exe PRP-35
# Checks: git branches, validation gates, confidence score
# Output: 10/10 confidence
```

## Workflow Integration

### With Git Worktree Workflow

```bash
# Check branch status
git status

# View commits
git log prp-6-user-authentication --oneline

# Review execution
/peer-review exe PRP-6

# If approved, merge to main
git checkout main
git merge prp-6-user-authentication --no-ff
git push origin main
```

## Tips

1. **Run immediately after execution** for fresh context
2. **Check git status** for merge conflicts
3. **Use --verbose** for detailed validation breakdowns
4. **Trust confidence scores**: 10/10 = production ready
5. **Review self-healing logs** to understand fixes applied
6. **Check drift score** to ensure context health
7. **Verify checkpoint tags** for rollback capability

## Implementation Details

- **Module**: `tools/ce/peer_review.py`
- **Tests**: `tools/tests/test_peer_review.py`
- **Integration**: Uses native `git` commands for branch validation
- **Hooks**: Validates SessionStart hooks executed correctly
- **Context**: Checks drift score via `ce context health`

## Related Commands

- `/execute-prp <prp-file>` - Execute PRP with git worktree workflow
- `git status` - Check conflicts and branch status
- `git log <branch> --oneline` - View commit history
- `ce context health` - Check context drift
- `ce prp restore <prp-id> [phase]` - Rollback to checkpoint

## External References

- [Git Worktree Guide](../CLAUDE.md#git-worktree---parallel-prp-development) - Git worktree workflow (CLAUDE.md lines 421-681)
- [PRP-4](../PRPs/feature-requests/PRP-4-execute-prp-orchestration.md) - Execute-PRP implementation
- [PRP-2](../PRPs/feature-requests/PRP-2-prp-state-isolation.md) - Checkpoint system
- [PRP-5](../PRPs/feature-requests/PRP-5-context-sync-integration.md) - Context sync
