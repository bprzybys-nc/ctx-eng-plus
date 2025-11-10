# Troubleshooting Guide - Unified Batch Command Framework

**Version**: 1.0
**Last Updated**: 2025-11-10
**Framework**: Phase 1 Unified Architecture
**Coverage**: Common issues, symptoms, causes, solutions

---

## Quick Reference

| Issue | Symptom | Cause | Solution |
|-------|---------|-------|----------|
| Circular dependency | `batch-gen-prp` fails immediately | Plan has cycles (A→B→C→A) | Fix plan: break the cycle |
| File conflict | Warning during review or execution | Multiple PRPs modify same file | Serialize: move to different stages |
| Subagent timeout | `Heartbeat not received after 60s` | Subagent crashed or stuck | Check error log, retry or resume |
| Validation failure | `Validation gate failed` | Code doesn't match requirements | Fix code, resume execution |
| High drift score | `Drift score >30%` | Implementation differs from plan | Verify intentional, update plan |
| Token savings low | No reduction in `batch-peer-review` | Shared context not working | Verify context passed, check report |
| Parallel slower | Stage with 3 PRPs takes longer | Resource contention | Reduce parallel limit or execute sequential |

---

## Common Issues & Solutions

### Issue 1: "Circular dependency detected"

**Symptom**:
```
Error: Circular dependency detected
Cycle: Phase-1 → Phase-2 → Phase-3 → Phase-1
File: .ce/orchestration/cycles.log
```

**Root Causes**:
1. **Typo in dependency name**
   ```yaml
   ### Phase 1
   **Dependencies**: Phase 1  # Self-reference!

   ### Phase 2
   **Dependencies**: Phase 1  # OK
   ```
   → Self-cycles are most common

2. **Logical cycle in plan**
   ```yaml
   ### Phase A: Backend
   **Dependencies**: Phase B

   ### Phase B: Frontend
   **Dependencies**: Phase A

   # A → B → A (true cycle)
   ```

3. **Transitive cycle** (hard to spot)
   ```yaml
   ### Phase 1: API
   **Dependencies**: Phase 2

   ### Phase 2: Database
   **Dependencies**: Phase 3

   ### Phase 3: Tests
   **Dependencies**: Phase 1

   # 1 → 2 → 3 → 1 (true cycle)
   ```

**Solutions**:

**Option 1: Remove the dependency (most common)**
```yaml
# Before:
### Phase 3: Tests
**Dependencies**: Phase 1

# After:
### Phase 3: Tests
**Dependencies**: Phase 2  # Only depends on latest phase
```

**Option 2: Split into smaller phases**
```yaml
# Before (causes cycle):
### Phase A: Feature with Tests
**Dependencies**: None

# After (no cycle):
### Phase 1: Feature Implementation
**Dependencies**: None

### Phase 2: Tests
**Dependencies**: Phase 1
```

**Option 3: Make dependency optional**
```yaml
# If not strictly required:
### Phase 3: Optimization
**Dependencies**: None  # Can run in parallel with Phase 1 & 2
```

**Verification**:
```bash
# Check your plan file
cat MY-PLAN.md | grep -A1 "Dependencies"

# Look for circular references manually
# Or use dependency analyzer
cd .ce/orchestration
python dependency_analyzer.py analyze ../../../MY-PLAN.md
```

**Prevention**:
- Keep dependencies to 1 or 2 phases
- Avoid phase → distant phase dependencies
- Test plan with analyzer before generating PRPs

---

### Issue 2: "File conflict detected"

**Symptom**:

During review:
```
Warning: File conflict in Stage 2
  PRP-50.2.1 modifies src/auth.py
  PRP-50.2.2 modifies src/auth.py
Recommendation: Serialize these PRPs (move to different stages)
```

During execution:
```
Stage 2: Executing in parallel
  PRP-50.2.1 modifying src/auth.py (in progress)
  PRP-50.2.2 modifying src/auth.py (in progress)
  ✗ CONFLICT: Both PRPs modified same file
  Error: Git merge conflict (auto-merged, check for issues)
```

**Root Causes**:
1. **Plan has overlapping scope**
   ```yaml
   ### Phase 2a: Add OAuth
   **Files Modified**: src/auth.py

   ### Phase 2b: Add SAML
   **Files Modified**: src/auth.py  # Same file!

   # Both in Stage 2 → parallel execution → conflict
   ```

2. **Implementation diverged from plan**
   - PRP-50.2.1 was supposed to modify `src/oauth.py`
   - Actually modified `src/auth.py` instead
   - PRP-50.2.2 also modifies `src/auth.py`
   - Result: conflict

3. **Shared utilities or config**
   - Both PRPs need to modify `pyproject.toml`
   - Or both modify `settings.py`
   - Safe to auto-merge, but worth checking

**Impact**:
- Auto-merged (orchestrator handles merge)
- But files may have both changes in wrong order
- Manual review recommended

**Solutions**:

**Option 1: Serialize (safest)**

Move one PRP to later stage:
```yaml
# Before:
### Phase 2a: Add OAuth
**Dependencies**: Phase 1

### Phase 2b: Add SAML
**Dependencies**: Phase 1  # Independent of Phase 2a

# After:
### Phase 2a: Add OAuth
**Dependencies**: Phase 1

### Phase 2b: Add SAML
**Dependencies**: Phase 2a  # Now depends on Phase 2a
```

This moves Phase 2b to Stage 3, eliminating parallel conflict.

**Option 2: Split file responsibility**

Restructure so no overlap:
```yaml
# Before (both modify src/auth.py):
### Phase 2a: Add OAuth
**Files Modified**: src/auth.py

### Phase 2b: Add SAML
**Files Modified**: src/auth.py

# After (separate files):
### Phase 2a: Add OAuth
**Files Modified**: src/oauth_provider.py

### Phase 2b: Add SAML
**Files Modified**: src/saml_provider.py
```

Then both can run in parallel safely.

**Option 3: Merge PRPs into one**

If closely related:
```yaml
# Before (2 PRPs, conflict):
### Phase 2a: Add OAuth
### Phase 2b: Add SAML

# After (1 PRP, no conflict):
### Phase 2: Add OAuth + SAML
**Files Modified**: src/auth.py
**Estimated Hours**: 6 (combined from 4+3)
**Dependencies**: Phase 1
```

**Option 4: Accept and manage conflict**

If auto-merge acceptable:
```bash
# After execution, manually verify merged file
git diff HEAD~1 src/auth.py

# If merged correctly:
git add src/auth.py
git commit -m "Verified conflict resolution from PRP-50.2.x"

# If wrong order:
# Edit file to correct order
git add src/auth.py
git commit -m "Fixed conflict resolution for auth providers"
```

**Verification**:
```bash
# Check which files are modified by each PRP
grep "Files Modified" PRP-50.2.1-oauth.md
grep "Files Modified" PRP-50.2.2-saml.md

# If overlap, check Stage assignment
cd .ce/orchestration
python dependency_analyzer.py analyze ../../MY-PLAN.md | grep Stage
```

**Prevention**:
- Review plan for file overlaps before generating
- Use `/batch-peer-review --mode structural` to catch early
- Keep PRPs focused on separate files when possible

---

### Issue 3: "Subagent timeout"

**Symptom**:
```
Stage 2: Executing PRP-50.2.1
  ... (heartbeat received every 30s)
  T=65s: ✗ Timeout! No heartbeat for 60+ seconds
  Status: FAILED

Error: Subagent PRP-50.2.1 did not complete within timeout
  Last heartbeat: "Step 2 of 5: Processing files"
  Elapsed: 65 seconds
  Action: Check error log or retry with --resume
```

**Root Causes**:
1. **Subagent crashed**
   ```
   Process killed: Out of memory, segfault, etc.
   Result: No more heartbeats, timeout after 60s
   ```

2. **Subagent stuck in loop**
   ```
   Infinite loop, deadlock, or waiting for input
   Result: Heartbeat stops updating, timeout after 60s
   ```

3. **System overload**
   ```
   CPU/RAM maxed out
   Subagent slows down, misses 30s heartbeat deadlines
   After 2 missed heartbeats (60s) → timeout
   ```

4. **Large input causing slow processing**
   ```
   PRP with 50+ steps, huge files to process
   Legitimate slow task, but exceeds 60s timeout
   ```

5. **Orchestrator heartbeat polling issue**
   ```
   Orchestrator not checking heartbeat file correctly
   Subagent alive, but orchestrator thinks it's dead
   ```

**Solutions**:

**Option 1: Increase timeout (for large PRPs)**
```bash
# Edit base-orchestrator.md Phase 4
# Change: HEARTBEAT_TIMEOUT = 60 seconds
# To:     HEARTBEAT_TIMEOUT = 120 seconds

# Then retry:
/batch-exe-prp --batch 50 --resume
```

**Option 2: Check error logs**
```bash
# Look for subagent error output
ls -la .ce/orchestration/tasks/batch-50/
cat .ce/orchestration/tasks/batch-50/task-2.result.json | jq '.errors'

# Check system logs for crashes
# macOS: log stream --predicate 'eventMessage contains[cd] "python"'
# Linux: journalctl -u claude-code
```

**Option 3: Retry with resume**
```bash
# Fix underlying issue (if crash):
# - Increase system RAM
# - Close other apps
# - Reduce PRP complexity

# Then resume:
/batch-exe-prp --batch 50 --resume

# If step N times out, steps 1-N-1 are saved
```

**Option 4: Split large PRP**

If PRP has 50+ steps:
```yaml
# Before (1 large PRP, often times out):
### Phase 2: Large Implementation
**Estimated Hours**: 8
**Implementation Steps**:
1. ... step 1
2. ... step 2
...
50. ... step 50

# After (2 smaller PRPs, faster, less timeout risk):
### Phase 2a: Initial Implementation
**Estimated Hours**: 4
**Implementation Steps**:
1. ... step 1
...
25. ... step 25

### Phase 2b: Complete Implementation
**Estimated Hours**: 4
**Dependencies**: Phase 2a
**Implementation Steps**:
1. ... step 26
...
25. ... step 50
```

**Option 5: Check orchestrator health**
```bash
# Verify orchestrator is responsive
mcp__syntropy__healthcheck

# If orchestrator unhealthy, restart:
# 1. Kill old MCP process
# 2. Run: /mcp (in Claude Code)
# 3. Retry batch execution

# Then retry:
/batch-exe-prp --batch 50 --resume
```

**Prevention**:
- Keep PRPs under 30 steps (each ~2-3 minutes)
- Monitor system resources while executing
- Use `--verbose` flag to see progress
- Test with small batch first (validate timeouts acceptable)

---

### Issue 4: "Validation gate failed"

**Symptom**:
```
Stage 2: Executing PRP-50.2.1
  Step 1: Create auth module ✓
  Step 2: Add unit tests ✓
  Step 3: Verify implementation ✓

  Validation gates:
    - [ ] All files created
      Status: ✓ PASSED
    - [ ] No linting errors
      Status: ✗ FAILED
        Error: PEP8 violations in src/auth.py:127-135
        Issue: Line too long (127 chars > 120 limit)

  ✗ Validation failed, stopping execution
  Resolution: Fix code issue, then retry with --resume
```

**Root Causes**:
1. **Code quality issues**
   - Linting errors (PEP8, ESLint, etc.)
   - Type errors (mypy, TypeScript)
   - Unused imports or variables

2. **Test failures**
   ```
   Gate: >90% test coverage
   Actual: 85%
   Missing: Tests for error cases
   ```

3. **Missing implementations**
   ```
   Gate: All required functions implemented
   Missing: authenticate() function
   ```

4. **Performance issues**
   ```
   Gate: Endpoint responds <100ms
   Actual: 500ms
   Cause: N+1 database query
   ```

5. **Gate definition mismatch**
   ```
   Gate says: "All tests pass"
   Actual test: pytest tests/ -q
   But author ran: pytest tests/unit/ -q (skipped integration tests)
   ```

**Solutions**:

**Option 1: Fix and resume (recommended)**
```bash
# 1. Read error message carefully
# Example: "PEP8 violations in src/auth.py:127-135"

# 2. Fix the issue
# Edit src/auth.py, lines 127-135
# Remove trailing whitespace, split long line, etc.

# 3. Commit your fix
git add src/auth.py
git commit -m "Fix: PEP8 violations in auth module"

# 4. Resume execution (retries the failed step)
/batch-exe-prp --batch 50 --resume

# The failed step re-runs the validation
# If passed, continues to next step
# If failed again, stops with same error
```

**Option 2: Adjust gate if unrealistic**

If gate is impossible to achieve:
```yaml
# Before (unrealistic):
### Phase 2: Optimization
**Validation Gates**:
- [ ] 95% test coverage (for 500-line module)
- [ ] All endpoints respond <50ms (impossible without caching)

# After (realistic):
### Phase 2: Optimization
**Validation Gates**:
- [ ] 85% test coverage (covers main paths)
- [ ] All endpoints respond <200ms (without caching)
```

Edit PRP file and retry.

**Option 3: Debug gate definition**
```bash
# Check what gate is actually testing
grep -A3 "Validation gates" PRP-50.2.1-auth.md

# Example:
# - [ ] No linting errors (checked: pylint src/auth.py)
#
# Try running the command manually:
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
pylint src/auth.py

# See actual errors, fix them, then retry
```

**Option 4: Update PRP if requirements changed**

If gate is correct but requirements changed:
```yaml
# If feature expanded mid-execution:
# - Test coverage needs to increase proportionally
# - Update gate accordingly

**Validation Gates**:
- [ ] 80% test coverage (instead of 90%)
```

Edit PRP, commit, and retry with `--resume`.

**Prevention**:
- Set realistic gates (achievable in estimated hours)
- Test gates manually before execution
- Use `--dry-run` to validate gates without executing
- Get review from peer (use `/batch-peer-review`)

---

### Issue 5: "Drift score >30%"

**Symptom**:
```
Running: /batch-update-context --batch 50
  PRP-50.1.1: Drift score 8% (EXCELLENT)
  PRP-50.2.1: Drift score 42% (CONCERNING)  ← High drift!

Warning: High drift detected
  Expected files: 5
  Actual files: 12 (7 extra)
  Expected lines: 800
  Actual lines: 1450 (650 extra)

Possible causes:
  1. Extra features implemented (scope creep)
  2. Extra refactoring (not in original plan)
  3. Planning was incomplete (missing steps)

Review & decide:
  - Accept drift (if intentional): Do nothing
  - Fix drift (if unintentional): Review git log and decide what to keep
  - Update plan (if incomplete): Add missing phases
```

**Root Causes**:
1. **Scope creep** (most common)
   ```
   Plan said: Add authentication
   Implementation included: Authentication + OAuth + SAML + 2FA

   Extra work: +40% lines
   Drift: High
   ```

2. **Unnecessary refactoring**
   ```
   Plan said: Add feature
   Implementation also refactored 3 other modules

   Extra changes: +50% files
   Drift: High
   ```

3. **Planning was incomplete**
   ```
   Plan was rough estimate
   Actual implementation discovered missing steps
   Had to add them during execution

   Extra files: +30%
   Drift: High
   ```

4. **Bug fixes along the way**
   ```
   Encountered bugs in existing code
   Fixed them as part of this PRP

   Extra changes: +20%
   Drift: Moderate
   ```

**Is High Drift Bad?**

**Maybe**. Depends on root cause:

| Cause | Assessment | Action |
|-------|-----------|--------|
| Scope creep | ✗ BAD | Decide what to revert |
| Planned features | ✓ OK | Update plan docs |
| Bug fixes | ✓ OK | Document in PRP |
| Refactoring | ⚠ REVIEW | Keep if improves code, revert if unrelated |

**Solutions**:

**Option 1: Accept if intentional**
```bash
# If all extra work was justified:

# 1. Update PRP with new scope
edit PRPs/feature-requests/PRP-50.2.1-auth.md

# Add to "Files Modified" section:
**Files Modified**: src/auth.py, src/oauth.py, src/saml.py, src/2fa.py

# Add to "Implementation Steps":
4. Implement OAuth integration
5. Implement SAML integration
6. Implement 2FA support

# 2. Update Serena memory with actual scope
/batch-update-context --batch 50

# Drift score will recalculate
```

**Option 2: Revert unintended changes**
```bash
# If extra work was accidental:

# 1. Review what was added
git log --oneline --grep="PRP-50.2.1" | head

# 2. See what files were changed
git show --name-only <commit-hash>

# 3. Revert specific commits or files
# Option A: Revert entire PRP
git revert <commit-hash>

# Option B: Revert specific files
git checkout <commit-hash>^ -- path/to/unwanted/file

# Option C: Edit files manually to remove extra changes

# 4. Commit the reversion
git commit -m "PRP-50.2.1: Revert unintended changes"

# 5. Re-run context update
/batch-update-context --batch 50

# Drift score will decrease
```

**Option 3: Update plan if incomplete**
```bash
# If planning was incomplete:

# 1. Create new phases for missing work
# Edit MY-FEATURE-PLAN.md

**Dependencies**: Phase 2a
**Implementation Steps**:
4. Implement OAuth provider
5. Add SAML provider

# 2. Generate new batch for Phase 2b
/batch-gen-prp MY-FEATURE-PLAN.md

# 3. Execute Phase 2b separately
/batch-exe-prp --batch 51

# This separates intentional work (Phase 2b)
# from original work (Phase 2a)
# Drift scores become accurate
```

**Prevention**:
- Be detailed in plan (include all steps, not rough outline)
- Get review before execution (catch missing steps)
- Limit scope per PRP (focus on one thing)
- Track scope creep during execution (flag before finishing)
- Use `batch-peer-review` to validate scope matches hours

---

### Issue 6: "Token usage not reduced"

**Symptom**:
```
Running: /batch-peer-review --batch 50 --verbose

Reviewing 5 PRPs...
  Shared context loaded: 20k tokens
  PRP-50.1.1 review: 30k tokens (not reduced)
  PRP-50.2.1 review: 30k tokens (not reduced)
  PRP-50.3.1 review: 30k tokens (not reduced)
  PRP-50.4.1 review: 30k tokens (not reduced)
  PRP-50.5.1 review: 30k tokens (not reduced)

  Total: 170k tokens
  Expected: 50k tokens (with 70% savings)
  Actual: 3.4x expected!

Warning: Shared context optimization not working
```

**Root Causes**:
1. **Shared context not passed to subagents**
   - Orchestrator loaded context
   - But didn't include it in task specs
   - Each subagent starts from scratch

2. **Context too large**
   - Shared context is 50k+ tokens
   - Each subagent still uses full context
   - Overhead > savings

3. **PRPs are independent**
   - Batch with completely unrelated PRPs
   - Shared context doesn't help
   - No savings expected

4. **Subagent implementation issue**
   - Shared context passed correctly
   - But subagent not using it
   - Uses its own context instead

**Solutions**:

**Option 1: Verify shared context passed**
```bash
# Check batch result file
cat .ce/orchestration/batches/batch-50.result.json | jq '.shared_context'

# If empty or null:
# - Orchestrator bug (contact dev team)
# - Or review batch is structural-only (shared context not used)

# Check: Did you use --mode structural?
# /batch-peer-review --batch 50 --mode structural
# ^ This mode skips semantic analysis, so less token usage expected

# For full savings, use default:
/batch-peer-review --batch 50
# (not --mode structural)
```

**Option 2: Check task specs**
```bash
# Look at what subagents received
ls .ce/orchestration/tasks/batch-50/
cat .ce/orchestration/tasks/batch-50/task-1.json | jq '.shared_context'

# If shared_context field is missing:
# Bug in orchestrator
# File issue with reproduction: batch ID, command used
```

**Option 3: Reduce context size**
```bash
# If shared context is huge (50k+ tokens):

# 1. Check what's in shared context
cat .ce/orchestration/batches/batch-50.result.json | jq '.shared_context' | wc -c

# 2. Trim unnecessary context
# Edit base-orchestrator.md Phase 3
# Remove sections from CLAUDE.md that aren't relevant
# Only keep framework docs, not all project docs

# 3. Retry batch review
/batch-peer-review --batch 50

# Should see improved savings
```

**Option 4: Use different review mode**

If reviewing very different PRPs:
```bash
# PRPs are unrelated (don't share common context)
# Shared context optimization won't help

# Use structural-only review (faster, cheaper):
/batch-peer-review --batch 50 --mode structural

# Cost: ~10k tokens
# Time: 1 minute
# Tradeoff: No semantic analysis (clarity, feasibility)
```

**Prevention**:
- Batch related PRPs together (shared context helpful)
- Keep CLAUDE.md lean (remove old, outdated sections)
- Use shared context for semantic review only
- Monitor token usage first time (report if not as expected)

---

### Issue 7: "Parallel execution slower than sequential"

**Symptom**:
```
Running: /batch-exe-prp --batch 50

Stage 1: PRP-50.1.1 (3 hours)
  Time: 3h 5m

Stage 2: PRP-50.2.1, PRP-50.2.2, PRP-50.2.3 (parallel, 2h each)
  Time: 4h 30m ← SLOWER than sequential (2h expected)!

  PRP-50.2.1: 2h 15m
  PRP-50.2.2: 2h 00m
  PRP-50.2.3: 4h 30m ← This one took MUCH longer

Analysis:
  - 3 PRPs running in parallel
  - Expected total: 2h (longest individual)
  - Actual total: 4h 30m (1.5x slower!)

Conclusion: Parallel not faster, system-level contention
```

**Root Causes**:
1. **CPU/RAM contention**
   ```
   System has limited resources:
   - 4-core CPU
   - 8GB RAM

   3 subagents × 2GB each = 6GB used
   System swapping to disk → 10x slower
   ```

2. **I/O contention**
   ```
   All 3 PRPs reading/writing same files
   Disk I/O becomes bottleneck
   Sequential faster (less switching)
   ```

3. **Network contention**
   ```
   All 3 subagents calling Claude API
   Rate-limited or network congested
   Total throughput reduced
   ```

4. **Lock contention**
   ```
   PRPs modifying same git repo
   Git locks prevent parallel writes
   Serialized anyway (defeats parallelism)
   ```

**Solutions**:

**Option 1: Check system resources**
```bash
# During parallel execution, monitor:
# macOS:
top -l1 | head -20  # Check CPU, Memory

# Linux:
free -h  # Check memory
htop    # Interactive monitor

# If >90% memory used:
# System is swapping to disk
# Close other apps, then retry
```

**Option 2: Reduce parallel limit**
```bash
# Edit base-orchestrator.md Phase 4
# Find: MAX_PARALLEL_SUBAGENTS = 4

# Change to:
MAX_PARALLEL_SUBAGENTS = 2

# Then retry:
/batch-exe-prp --batch 50 --resume

# Will run only 2 PRPs in parallel
# Reduces resource contention
```

**Option 3: Execute stage-by-stage manually**
```bash
# Instead of:
/batch-exe-prp --batch 50

# Run:
/batch-exe-prp --batch 50 --stage 1
# Wait for completion
/batch-exe-prp --batch 50 --stage 2
# Wait for completion
/batch-exe-prp --batch 50 --stage 3
# etc.

# Fully sequential, more predictable
# Downside: Slower overall, more manual work
```

**Option 4: Upgrade system resources**
```bash
# For laptops with limited RAM (<8GB):
# Close Chrome, Slack, IDE, etc.
# Leave only essential apps running
# Retry batch execution

# For servers with limited CPU:
# Increase instance size or run during off-peak
```

**Option 5: Restructure PRPs to reduce parallelism**

If too many parallel PRPs:
```yaml
# Before (Stage 2 has 5 PRPs, too much contention):
### Phase 2a: Auth (no deps)
### Phase 2b: API (no deps)
### Phase 2c: Tests (no deps)
### Phase 2d: Docs (no deps)
### Phase 2e: Deploy (no deps)

# After (Stage 2 has 2 PRPs, manageable):
### Phase 2a: Auth (no deps)
### Phase 2b: API (depends on 2a) ← Sequential instead
### Phase 2c: Tests (depends on 2b)
### Phase 2d: Docs (depends on 2c)
### Phase 2e: Deploy (depends on 2d)

# Tradeoff: Slower individual execution
# Benefit: No resource contention, more predictable timing
```

**Prevention**:
- Start with sequential execution (`--stage 1` then `--stage 2`)
- Monitor performance
- Only parallelize if system has resources
- Keep batch size reasonable (5-10 PRPs per stage, max 15)

---

## Advanced Debugging

### Debug Command: Check Batch Status

```bash
# Summary of current batch
cat .ce/orchestration/batches/batch-50.result.json | jq '.'

# Parse useful fields:
cat .ce/orchestration/batches/batch-50.result.json | jq '{
  batch_id: .batch_id,
  status: .status,
  total_prps: .total_prps,
  completed_prps: .completed_prps,
  failed_prps: .failed_prps,
  total_time_seconds: .total_time_seconds,
  total_tokens: .total_tokens
}'
```

### Debug Command: Check Task Details

```bash
# Get details of specific task
cat .ce/orchestration/tasks/batch-50/task-2.result.json | jq '.'

# Or just the error:
cat .ce/orchestration/tasks/batch-50/task-2.result.json | jq '.errors'

# Or progress:
cat .ce/orchestration/tasks/batch-50/task-2.hb
```

### Debug Command: Check Git Log

```bash
# See all commits for batch
git log --oneline --grep="PRP-50" | head -20

# See commits for specific PRP
git log --oneline --grep="PRP-50.2.1" | head -10

# See what changed in a commit
git show <commit-hash> --stat
```

### Debug Command: Run Dependency Analyzer

```bash
# Validate plan manually
cd .ce/orchestration
python dependency_analyzer.py analyze ../../MY-PLAN.md

# See stage assignments
python dependency_analyzer.py analyze ../../MY-PLAN.md | grep "Stage"

# See dependency graph
python dependency_analyzer.py analyze ../../MY-PLAN.md | grep "→"
```

### Debug Command: Monitor Execution

```bash
# Watch heartbeats in real-time (macOS)
watch -n 1 'cat .ce/orchestration/tasks/batch-50/task-2.hb | jq .'

# Or manually check every 30s
while true; do
  cat .ce/orchestration/tasks/batch-50/task-2.hb | jq '.progress'
  sleep 30
done
```

### Debug Command: Check MCP Health

```bash
# Verify orchestrator is working
mcp__syntropy__healthcheck

# Expected output:
# ✅ Syntropy MCP Server: Healthy (v0.1.2)
# Build: 2025-11-10T18:00:00Z
#
# MCP Server Status:
#   ✅ serena          - Healthy (5ms)
#   ✅ linear          - Healthy (200ms)
#   ✅ context7        - Healthy (150ms)

# If unhealthy, reconnect:
/mcp
```

---

## Troubleshooting Workflow

When something goes wrong:

1. **Read error message** (50% of issues solved here)
   ```
   Error: ________________
   ↓
   Go to "Common Issues" section with this error message
   ```

2. **Check this guide** (70% of issues solved here)
   ```
   Found matching issue?
   ↓
   Follow "Solution" steps
   ↓
   Retry command
   ```

3. **Use debug commands** (20% of issues solved here)
   ```
   Still stuck?
   ↓
   Run debug command for your issue
   ↓
   Check output for root cause
   ↓
   Apply relevant solution
   ```

4. **File bug report** (<5% of issues)
   ```
   Still stuck?
   ↓
   File issue with:
   - Command used
   - Full error output
   - Debug command results
   - Reproduction steps
   ```

---

## Getting Help

### Self-Service (Recommended)

1. **Check this guide** (you're reading it!)
2. **Search logs** (`grep`, `git log`)
3. **Run debug commands** (heartbeat, batch result)
4. **Review examples** (PRP-47 batch in PRPs/feature-requests/)

### Asking for Help

When stuck, provide:
```
Title: [COMMAND] Brief issue

Command used:
/batch-exe-prp --batch 50

Error message:
[full error text]

What you tried:
1. Tried solution X
2. Tried solution Y

Debug output:
[result of relevant debug command]

Expected:
[what should have happened]

Actual:
[what actually happened]
```

### Reporting Bugs

Include:
- Reproduction steps (5-10 steps to recreate)
- Full error output
- File paths mentioned in error
- System info (macOS/Linux/Windows, Python version)
- When this last worked (if regression)

---

## References

- **Usage Guide**: PRPs/feature-requests/PRP-47-USAGE-GUIDE.md
- **Architecture**: .claude/orchestrators/README.md
- **Subagents**: .claude/subagents/README.md
- **Dependency Analyzer**: .ce/orchestration/dependency_analyzer.py
- **Example Batches**: PRPs/feature-requests/PRP-47.*.md

---

**Version History**:
- 2025-11-10: v1.0 - Initial troubleshooting guide with 7 common issues

