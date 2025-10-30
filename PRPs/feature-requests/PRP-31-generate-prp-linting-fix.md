---
prp_id: 31
feature_name: Fix /generate-prp Linting Auto-Fix Hangs
status: pending
created: 2025-10-30T14:30:00Z
updated: 2025-10-30T14:30:00Z
complexity: medium
estimated_hours: 2-3
dependencies: markdownlint CLI, Python stdlib (subprocess, time, json)
issue: BLA-48
---

# Fix /generate-prp Linting Auto-Fix Hangs

## 1. TL;DR

**Objective**: Add timeout, retry limits, and graceful degradation to `/generate-prp` markdown linting to prevent indefinite hangs

**What**: Update `.claude/commands/generate-prp.md` to:
- Add 30s timeout for entire linting cycle (3 attempts × 10s each)
- Implement retry limit (max 3 attempts) with infinite loop detection
- Gracefully degrade on failures (output PRP with warning, don't block)
- Update heartbeat every 5-10s during linting
- Fix directory convention (`.tmp/batch-gen/` → `tmp/batch-gen/`)
- Add optional solo mode heartbeat support (`tmp/solo-gen/`)

**Why**: PRP-30.2.1 generation hung at 50% for 27 minutes during L1 markdown linting with no timeout or error handling

**Effort**: 2-3 hours (1h implementation, 1-2h testing with edge cases)

**Dependencies**: markdownlint CLI (must be installed), Python stdlib

---

## 2. Context

### Background

The `/generate-prp` command currently runs markdown linting (L1 validation) as the final step before outputting PRPs. The linting step uses `markdownlint --fix` to auto-fix formatting issues (MD031, MD032: blank lines around lists/code blocks).

**Current Implementation** (`.claude/commands/generate-prp.md:150-154`):
```markdown
5. **Runs L1 validation on generated markdown**:
   - Lints markdown (markdownlint: MD031, MD032, etc.)
   - Auto-fixes formatting issues (blank lines around lists/code blocks)
   - Ensures PRP is lint-clean before output
```

**Problem**: During PRP-30.2.1 generation (via `/batch-gen-prp`), the agent hung at 50% progress for 27 minutes. The heartbeat file showed:
```json
{"prp_id": "30.2.1", "status": "WRITING", "progress": 50, "timestamp": <old>}
```

Investigation revealed the linting step has:
- ❌ No timeout on `markdownlint --fix` execution
- ❌ No retry limit (could loop infinitely on unfixable errors)
- ❌ No error handling (fails silently or hangs)
- ❌ No heartbeat updates during linting (appears frozen)
- ❌ Wrong directory: `.tmp/batch-gen/` vs `tmp/batch-gen/` (per convention in `examples/tmp-directory-convention.md`)

### Constraints and Considerations

**Timeout Requirements**:
- Total timeout: 30 seconds (3 attempts × 10s each)
- Per-attempt timeout: 10 seconds
- Normal PRPs (<500 lines) typically lint in 1-5s, so 10s per attempt is generous

**Graceful Degradation**:
- If linting fails or times out, OUTPUT the PRP file anyway with a warning
- Don't block PRP generation on linting failures
- Log errors for debugging but continue workflow

**Heartbeat Protocol**:
- Batch mode: `tmp/batch-gen/PRP-{prp_id}.status`
- Solo mode (optional): `tmp/solo-gen/PRP-{next_id}.status`
- Update every 5-10 seconds during linting operations
- Format: `{"prp_id": "...", "status": "LINTING", "progress": 75-80, "timestamp": <unix>, "current_step": "..."}`

**Infinite Loop Detection**:
- Compare errors between consecutive attempts
- If same error repeats twice → abort (infinite loop detected)
- Return `SUCCESS_WITH_LINT_WARNINGS` status

**Edge Cases**:
- markdownlint not installed → skip linting, output warning
- File too large (>1000 lines) → increase timeout to 60s
- Syntax error in markdown → catch and continue
- Unfixable lint errors → output warning after 3 attempts

### Documentation References

**markdownlint CLI**:
- Command: `markdownlint --fix <file>`
- Exit codes: 0 = success, 1 = errors found
- Timeout: Add via `subprocess.run(timeout=N)` in Python

**Heartbeat Protocol**:
- Batch mode: `tmp/batch-gen/PRP-{prp_id}.status`
- Solo mode: `tmp/solo-gen/PRP-{next_id}.status` (optional)
- Format: JSON with `prp_id`, `status`, `progress`, `timestamp`, `current_step`

**tmp/ Directory Convention**:
- Documented in: `examples/tmp-directory-convention.md`
- Rule: `tmp/` for work-in-progress (not `.tmp/`)
- Applies to: heartbeat files, INITIAL.md, PLAN.md

**References**:
- generate-prp command: `.claude/commands/generate-prp.md:150-154, 245-249`
- batch-exe-prp health checking: `.claude/commands/batch-exe-prp.md:296-350`
- tmp convention: `examples/tmp-directory-convention.md`
- subprocess timeout: Python stdlib `subprocess.run(timeout=N)`

---

## 3. Implementation Steps

### Phase 1: Update Linting Instructions (45 min)

**File**: `.claude/commands/generate-prp.md`

**Step 1.1**: Update L1 validation description (lines 150-154)

**Before**:
```markdown
5. **Runs L1 validation on generated markdown**:
   - Lints markdown (markdownlint: MD031, MD032, etc.)
   - Auto-fixes formatting issues (blank lines around lists/code blocks)
   - Ensures PRP is lint-clean before output
```

**After**:
```markdown
5. **Runs L1 validation with timeout and retry** (30s max):
   - Lints markdown (markdownlint: MD031, MD032, etc.)
   - Auto-fixes formatting issues (max 3 attempts, 10s timeout each)
   - Detects infinite loops (abort if same error repeats)
   - Update heartbeat every 5s during linting (batch mode)
   - **Graceful degradation**: Output PRP with warning if linting fails
   - **Note**: This is markdown-specific L1, not code linting
```

**Step 1.2**: Add detailed linting workflow section (after line 160)

Add new section:
```markdown
### Linting Workflow (L1 Markdown Validation)

When Claude Code interprets this command, implement the following linting logic:

**Step 1: Write PRP file first**
```python
# Always write PRP content to file before linting
with open(prp_file_path, 'w') as f:
    f.write(prp_content)
```

**Step 2: Run markdownlint with retry and timeout**
```python
import subprocess
import time

def auto_fix_with_retry(file_path, prp_id=None, max_attempts=3):
    """Auto-fix markdown with retry limit and heartbeat

    Args:
        file_path: Path to markdown file
        prp_id: PRP ID for heartbeat (None for solo mode)
        max_attempts: Max retry attempts (default: 3)

    Returns: (success: bool, attempts: int, errors: list)
    """
    errors = []
    previous_error = None

    for attempt in range(1, max_attempts + 1):
        # Update heartbeat (batch mode only)
        if prp_id:
            write_heartbeat(prp_id, "LINTING", 75,
                          f"Auto-fix attempt {attempt}/{max_attempts}")

        try:
            # Run markdownlint with 10s timeout
            result = subprocess.run(
                ["markdownlint", "--fix", file_path],
                timeout=10,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Success: linting passed
                if prp_id:
                    write_heartbeat(prp_id, "LINTING", 80, "Linting complete")
                return (True, attempt, [])

            # Errors found
            current_error = result.stderr.strip()
            errors.append(current_error)

            # Check for infinite loop (same error twice)
            if attempt > 1 and current_error == previous_error:
                if prp_id:
                    write_heartbeat(prp_id, "LINTING", 80,
                                  "Infinite loop detected, continuing anyway")
                return (False, attempt, errors)

            previous_error = current_error

        except subprocess.TimeoutExpired:
            error_msg = f"Timeout on attempt {attempt}"
            errors.append(error_msg)
            if prp_id:
                write_heartbeat(prp_id, "LINTING", 75, error_msg)

        except FileNotFoundError:
            # markdownlint not installed
            if prp_id:
                write_heartbeat(prp_id, "LINTING", 80,
                              "markdownlint not found, skipping")
            return (False, 1, ["markdownlint not installed"])

    # Failed after max attempts
    if prp_id:
        write_heartbeat(prp_id, "LINTING", 80, "Linting failed, continuing anyway")
    return (False, max_attempts, errors)
```

**Step 3: Handle linting result with graceful degradation**
```python
# Try to lint (best effort, don't block on failure)
success, attempts, lint_errors = auto_fix_with_retry(prp_file_path, prp_id)

if not success:
    # Log warning but don't fail
    print(f"⚠️ Warning: Linting failed after {attempts} attempts")
    for error in lint_errors:
        print(f"   {error}")
    print(f"   PRP generated successfully but may have formatting issues")
    # Continue to next step (Linear issue creation)
else:
    print(f"✓ Linting passed after {attempts} attempt(s)")
```

**Step 4: Continue to Linear issue creation**
- Linting failures don't block PRP generation
- PRP file is already written in Step 1
- Proceed to create/update Linear issue
```
```

**Step 1.3**: Fix heartbeat directory (search for `.tmp/batch-gen`)

**Search pattern**: `.tmp/batch-gen`

**Replace with**: `tmp/batch-gen` (remove leading dot)

**Locations** (estimated):
- Batch mode heartbeat initialization
- Heartbeat write function
- Cleanup section

**Step 1.4**: Add solo mode heartbeat (optional, after line 161)

Add new section:
```markdown
### Solo Mode Heartbeat (Optional)

For monitoring solo mode generation progress:

1. Create heartbeat directory: `tmp/solo-gen/`
2. Determine next PRP ID: Read existing PRPs, increment by 1
3. Write heartbeat: `tmp/solo-gen/PRP-{next_id}.status`
4. Update every 15s during generation
5. Cleanup on completion (delete heartbeat file)

**Format** (same as batch mode):
```json
{
  "prp_id": "31",
  "status": "WRITING",
  "progress": 60,
  "timestamp": 1730000000,
  "current_step": "Generating Implementation Steps section"
}
```

**Note**: Solo mode heartbeat is optional and not required by `/batch-gen-prp`. Use only if user wants to monitor solo generation progress.
```

### Phase 2: Testing and Validation (1-2 hours)

**Test 1: Normal PRP (verify no regression)**
```bash
# Create small INITIAL.md
cat > tmp/feature-requests/test-normal/INITIAL.md << 'EOF'
# Feature: Test Normal PRP

## FEATURE
Test that normal PRPs still generate successfully

## EXAMPLES
```python
def test(): pass
```
EOF

# Generate PRP
/generate-prp tmp/feature-requests/test-normal/INITIAL.md

# Expected: PRP generated successfully, linting passes in <5s
```

**Test 2: Large PRP (stress test timeout)**
```bash
# Create INITIAL.md with 2000+ list items (slow to lint)
cat > tmp/feature-requests/test-large/INITIAL.md << 'EOF'
# Feature: Test Large PRP

## FEATURE
Test large PRP generation

## EXAMPLES
- Item 1
- Item 2
... (2000+ items)
EOF

# Generate PRP
/generate-prp tmp/feature-requests/test-large/INITIAL.md

# Expected:
# - Linting may timeout (acceptable)
# - PRP still created with warning
# - Warning: "Linting failed after 3 attempts"
```

**Test 3: markdownlint not installed (graceful degradation)**
```bash
# Temporarily rename markdownlint (simulate not installed)
which markdownlint && mv $(which markdownlint) $(which markdownlint).bak

# Generate PRP
/generate-prp tmp/feature-requests/test-no-lint/INITIAL.md

# Expected:
# - Warning: "markdownlint not found, skipping"
# - PRP still created successfully
# - No linting performed

# Restore markdownlint
mv $(which markdownlint).bak $(which markdownlint)
```

**Test 4: Heartbeat updates (batch mode)**
```bash
# Monitor heartbeat file during generation (separate terminal)
watch -n 1 'cat tmp/batch-gen/PRP-*.status | jq .'

# Generate PRP via /batch-gen-prp
# (use existing PLAN.md from Batch 30)

# Expected:
# - Heartbeat files in tmp/batch-gen/ (not .tmp/)
# - status: "LINTING" appears with progress 75-80
# - current_step shows "Auto-fix attempt X/3"
# - Updates every 5-10s during linting
```

**Test 5: Infinite loop detection**
```bash
# Create PRP with unfixable lint error (duplicate H1 headers)
cat > tmp/feature-requests/test-infinite/INITIAL.md << 'EOF'
# Feature: Test Infinite Loop

## FEATURE
Test infinite loop detection

## EXAMPLES
# Duplicate H1 (unfixable by markdownlint --fix)
# Duplicate H1
EOF

# Generate PRP
/generate-prp tmp/feature-requests/test-infinite/INITIAL.md

# Expected:
# - Max 3 linting attempts
# - Warning: "Infinite loop detected" or "same error repeats"
# - PRP still created successfully
```

---

## 4. Validation Gates

### Gate 1: Normal PRPs Generate Successfully

**Command**:
```bash
/generate-prp tmp/feature-requests/test-normal/INITIAL.md
```

**Expected**:
- PRP generated in PRPs/feature-requests/
- Linting passes in <5 seconds
- No timeout warnings
- Output: `✓ Linting passed after 1 attempt(s)`

**Failure Modes**:
- Timeout triggered on normal PRP → timeout too aggressive
- Linting fails → regex or logic error in retry loop

---

### Gate 2: Large PRPs Degrade Gracefully

**Setup**:
```bash
# Create INITIAL.md with 2000+ list items
cat > tmp/feature-requests/test-large/INITIAL.md << 'EOF'
# Feature: Large PRP Test

## FEATURE
Test large PRP with slow linting

## EXAMPLES
$(for i in {1..2000}; do echo "- Item $i"; done)
EOF
```

**Command**:
```bash
/generate-prp tmp/feature-requests/test-large/INITIAL.md
```

**Expected**:
- PRP file created (regardless of linting outcome)
- If linting times out: `⚠️ Warning: Linting failed after 3 attempts`
- If linting succeeds: `✓ Linting passed`
- Total linting time ≤ 30 seconds (3 attempts × 10s)

**Failure Modes**:
- PRP not created → graceful degradation broken
- Timeout exceeds 30s → timeout not enforced
- Process hangs → subprocess timeout not working

---

### Gate 3: markdownlint Not Installed (Graceful Degradation)

**Setup**:
```bash
# Temporarily hide markdownlint
which markdownlint && mv $(which markdownlint) $(which markdownlint).bak || echo "Already missing"
```

**Command**:
```bash
/generate-prp tmp/feature-requests/test-no-lint/INITIAL.md
```

**Expected**:
- Warning: `⚠️ Warning: Linting failed after 1 attempts`
- Error: `markdownlint not installed`
- PRP file created successfully
- No crash or error that blocks generation

**Cleanup**:
```bash
# Restore markdownlint
[ -f $(which markdownlint).bak ] && mv $(which markdownlint).bak $(which markdownlint)
```

**Failure Modes**:
- Process crashes on FileNotFoundError → exception not caught
- PRP not created → graceful degradation broken

---

### Gate 4: Heartbeat Files in Correct Directory

**Command**:
```bash
# Generate PRP via /batch-gen-prp (uses batch mode)
/batch-gen-prp tmp/feature-requests/syntropy-tool-management/PLAN.md
```

**Expected**:
```bash
# Check heartbeat location
ls -la tmp/batch-gen/
# Expected: PRP-*.status files present

ls -la .tmp/batch-gen/ 2>/dev/null
# Expected: directory doesn't exist or is empty
```

**Failure Modes**:
- Files in `.tmp/batch-gen/` → directory fix not applied
- Files in wrong location → path construction error

---

### Gate 5: Heartbeat Updates During Linting

**Setup**:
```bash
# Monitor heartbeat file in real-time
watch -n 1 'cat tmp/batch-gen/PRP-*.status 2>/dev/null | jq .'
```

**Command** (in separate terminal):
```bash
/batch-gen-prp tmp/feature-requests/syntropy-tool-management/PLAN.md
```

**Expected** (in watch terminal):
- status changes: `STARTING` → `PARSING` → `WRITING` → `LINTING` → `COMPLETE`
- During `LINTING` phase:
  - progress: 75-80
  - current_step: "Auto-fix attempt X/3" or "Linting complete"
  - timestamp updates every 5-10 seconds

**Failure Modes**:
- status never shows `LINTING` → heartbeat not updated during linting
- timestamp frozen → heartbeat not being written
- current_step missing → heartbeat data incomplete

---

### Gate 6: Infinite Loop Detection Works

**Setup**:
```bash
# Create PRP with unfixable lint error
cat > tmp/feature-requests/test-infinite/INITIAL.md << 'EOF'
# Feature: Infinite Loop Test

## FEATURE
Test infinite loop detection with unfixable error

## EXAMPLES
```python
# This will cause markdownlint to find errors that can't be auto-fixed
# (e.g., duplicate heading text, certain rule violations)
```
EOF
```

**Command**:
```bash
/generate-prp tmp/feature-requests/test-infinite/INITIAL.md
```

**Expected**:
- Max 3 linting attempts (not infinite)
- Warning: `⚠️ Warning: Linting failed after X attempts`
- Warning mentions: "same error repeats" or "infinite loop"
- PRP file created successfully
- Total time ≤ 30 seconds

**Failure Modes**:
- More than 3 attempts → retry limit not enforced
- Hangs indefinitely → infinite loop detection broken
- PRP not created → graceful degradation broken

---

## 5. Testing Strategy

### Test Framework

**Manual Testing** (no automated tests for slash commands)

Slash commands are Claude Code interpreter instructions, not executable Python code. Testing requires manual execution in Claude Code environment with real PRPs.

### Test Command

```bash
# In Claude Code terminal:
/generate-prp <test-initial-md-path>

# Monitor heartbeat (batch mode only):
watch -n 1 'cat tmp/batch-gen/*.status | jq .'
```

### Test Coverage

**Functional Tests**:
1. **Happy Path**: Normal PRP generation with successful linting
2. **Timeout**: Large PRP that triggers timeout → graceful degradation
3. **Missing Tool**: markdownlint not installed → skip linting, continue
4. **Infinite Loop**: Unfixable lint errors → detect, abort after 3 attempts
5. **Heartbeat**: Verify heartbeat updates during linting (batch mode)
6. **Directory Fix**: Verify files in `tmp/batch-gen/` not `.tmp/batch-gen/`

**Integration Tests**:
1. **With /batch-gen-prp**: Multiple PRPs generated in parallel
2. **With Linear**: PRP creation + Linear issue creation
3. **Solo Mode**: Single PRP generation (without batch mode)

### Test Data

**Test 1: Normal INITIAL.md** (small, should lint quickly)
```markdown
# Feature: Normal Test

## FEATURE
Simple feature to test normal flow

## EXAMPLES
```python
def test(): pass
```
```

**Test 2: Large INITIAL.md** (2000+ items, slow to lint)
```markdown
# Feature: Large Test

## FEATURE
Large feature with many list items

## EXAMPLES
- Item 1
- Item 2
... (2000+ items)
```

**Test 3: Unfixable Lint Errors** (trigger infinite loop detection)
```markdown
# Feature: Infinite Loop Test

## FEATURE
Feature with unfixable lint errors

## EXAMPLES
# Duplicate H1
# Duplicate H1
```

---

## 6. Rollout Plan

### Phase 1: Update Documentation (30 min)

**Actions**:
1. Update `.claude/commands/generate-prp.md` with new linting logic (lines 150-154)
2. Add detailed linting workflow section (after line 160)
3. Fix heartbeat directory references (`.tmp/` → `tmp/`)
4. Add optional solo mode heartbeat section
5. Commit changes

**Validation**:
- Grep for `.tmp/batch-gen` → no matches remaining
- Read lines 150-160 → new timeout/retry logic present
- Search for "Linting Workflow" → new section exists

---

### Phase 2: Manual Testing (1 hour)

**Actions**:
1. Test normal PRP generation (Gate 1)
2. Test large PRP with timeout (Gate 2)
3. Test markdownlint not installed (Gate 3)
4. Test heartbeat directory (Gate 4)
5. Test heartbeat updates (Gate 5)
6. Test infinite loop detection (Gate 6)

**Validation**:
- All 6 validation gates pass
- No regressions in normal PRP generation
- Graceful degradation works for all failure modes

---

### Phase 3: Documentation and Handoff (30 min)

**Actions**:
1. Update `CLAUDE.md` with troubleshooting section (if needed)
2. Document linting behavior in README or command docs
3. Mark PRP as executed
4. Close Linear issue

**Validation**:
- Documentation complete
- Users know how to interpret linting warnings
- Command ready for production use

---

## 7. Success Criteria

- [ ] `.claude/commands/generate-prp.md` updated with timeout/retry logic
- [ ] Linting timeout: 30s max (3 attempts × 10s each)
- [ ] Retry limit: max 3 attempts per lint error
- [ ] Infinite loop detection: abort if same error repeats
- [ ] Graceful degradation: PRP created even if linting fails
- [ ] Heartbeat updates every 5-10s during linting (batch mode)
- [ ] Heartbeat directory fixed: `tmp/batch-gen/` (not `.tmp/`)
- [ ] Optional solo mode heartbeat: `tmp/solo-gen/` (documented)
- [ ] markdownlint not installed: skip linting, output warning
- [ ] All 6 validation gates pass
- [ ] No regressions: normal PRPs still generate successfully
- [ ] Documentation complete with troubleshooting guidance

---

## 8. Rollback Plan

**If Issues Arise**:

1. **Linting breaking normal PRPs**:
   - Revert `.claude/commands/generate-prp.md` changes
   - Restore original L1 validation logic (lines 150-154)
   - Document issue for future fix

2. **Timeout too aggressive**:
   - Increase per-attempt timeout from 10s to 20s
   - Keep max attempts at 3 (still 60s total)
   - Test with large PRPs again

3. **Heartbeat causing issues**:
   - Make heartbeat writes conditional (check if batch mode)
   - Gracefully handle heartbeat write failures

**Rollback Command**:
```bash
# Revert generate-prp.md to last good version
git checkout HEAD~1 .claude/commands/generate-prp.md

# Test rollback
/generate-prp tmp/feature-requests/test-normal/INITIAL.md
```

---

## Dependencies

**Hard Dependencies**:
- Python stdlib: `subprocess`, `time`, `json`
- markdownlint CLI: Must be installed for linting (gracefully skipped if missing)

**Soft Dependencies**:
- None (command degrades gracefully if markdownlint missing)

---

## Related PRPs

- **PRP-30.2.1**: Slash Command - Sync with Syntropy Tool State (hung during generation, triggered this fix)
- **PRP-3**: Command Automation (original `/generate-prp` implementation)
- Future: Batch generation hang detection (separate PRP for `/batch-gen-prp` coordinator improvements)
