---
prp_id: 31
feature_name: Dual-Mode Peer Review with Factuality Validation
status: executed
created: 2025-10-30T11:30:00Z
updated: 2025-10-30T12:15:00Z
executed: 2025-10-30T12:15:00Z
complexity: low
estimated_hours: 0.75
actual_hours: 0.5
risk: low
dependencies: None
plan_source: Sequential thinking session + user requirements
issue: TBD
commit: 78f2430
branch: prp-31-dual-mode-peer-review
---

# Dual-Mode Peer Review with Factuality Validation

## 1. TL;DR

**Objective**: Add factuality validation to peer-review command to prevent hallucinated claims from poisoning the system

**What**:
- Add two review modes: `prp` (default, generation review) and `exe` (execution review)
- Add factuality verification layer that checks critical claims (files, commits, dependencies)
- Implement cache with auto-maintenance (1-hour TTL, 100-entry limit, orphan removal)

**Why**:
- Current `/peer-review exe` only reviews execution quality
- No verification that claims in PRPs are factually true
- Hallucinated file paths, commits, dependencies can poison system
- Pre-execution review needed more than post-execution

**Effort**: 45 minutes

**Risk Level**: LOW (documentation-only changes, no code modifications)

**KISS Principles Applied**:
- Two modes only (not four) - covers 95% of use cases
- Simple checks only (<5s overhead) - files, commits, dependencies
- Cache with auto-cleanup - no separate maintenance process
- Extendable via documentation - add checks to registry, no code changes

## 2. Context

### Current State

**Existing**: `/peer-review exe <prp>` reviews execution quality
- Git branch validation
- Phase completion checks
- Validation gates (L1-L4)
- Code quality review
- Context drift check

**Missing**:
- Pre-execution review (generation quality)
- Factuality verification (are claims true?)
- Hallucination detection

### Problem: Hallucination Poisoning

**Scenario**: PRP contains false claims
```yaml
# PRP-30 YAML header
files_modified: [.git/gitbutler/virtual_branches.toml]
dependencies: PRP-C, PRP-999
```

**What if**:
- ❌ File `.git/gitbutler/` doesn't exist (already removed)
- ❌ PRP-999 doesn't exist (hallucinated dependency)

**Impact**:
- False claims get embedded in executed PRPs
- Future PRPs reference false claims
- Contamination spreads through context
- Manual cleanup required

### Solution Requirements (User-Specified)

1. ✅ Check factuality (not risk scoring) - true/false only
2. ✅ Verification mandatory - always runs
3. ✅ Cache verified claims - performance optimization
4. ✅ KISS + extendable - simple now, grow later
5. ✅ `prp` mode default - most common workflow

## 3. Implementation Steps

### Phase 1: Add Mode Detection (10 minutes)

**Goal**: Support two review modes with `prp` as default

**File**: `.claude/commands/peer-review.md`

**Add at top**:
```markdown
## Mode Detection

The command supports two review modes:

Usage:
  /peer-review <prp>       → prp mode (DEFAULT - generation review)
  /peer-review prp <prp>   → prp mode (explicit)
  /peer-review exe <prp>   → exe mode (execution review)

Mode detection:
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
```

**Changes**:
- Move existing "Execution Review" content to "## Mode 2: Execution Review (exe)"
- Keep all existing content intact
- Add new "## Mode 1: Generation Review (prp)" section (Phase 2)

**Validation**:
```bash
/peer-review PRP-30         # Should detect prp mode
/peer-review prp PRP-30     # Should detect prp mode
/peer-review exe PRP-30     # Should detect exe mode
```

---

### Phase 2: Add Generation Review Mode (15 minutes)

**Goal**: Define what `prp` mode reviews (PRP generation quality)

**Add new section**:
```markdown
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
```

---

### Phase 3: Add Factuality Check Registry (10 minutes)

**Goal**: Define extendable check registry for factuality verification

**Add new section**:
```markdown
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

---

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

---

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

---

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

---

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

---

### Adding New Checks (Extendable)

To add a new factuality check:

1. Add new subsection: `### Check: {name}`
2. Define **Pattern** (what to look for)
3. Define **Verify** (bash command to run)
4. Define **Output** (PASS/FAIL meanings)
5. Provide **Example**

**No code changes required** - checks are documentation-driven.
```

---

### Phase 4: Add Cache System (5 minutes)

**Goal**: Implement cache with auto-maintenance

**Add new section**:
```markdown
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
```

---

### Phase 5: Update Examples and Documentation (5 minutes)

**Goal**: Add usage examples for new modes

**Update existing examples section**:
```markdown
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
```

**Update Common Issues section**:
Add new issue about cache:
```markdown
### Issue: "Cache too large"

```bash
# Symptom
ls -lh .ce/peer-review-cache.json
# Output: 500KB (should be ~50KB)

# Solution: Cache auto-cleans, but force reset if needed
rm .ce/peer-review-cache.json
```
```

---

## 4. Validation Gates

### Gate 1: Mode Detection Works

**Test all mode variations**:
```bash
# Default mode (prp)
/peer-review PRP-30
# Expected: "Mode: prp (generation review)"

# Explicit prp mode
/peer-review prp PRP-30
# Expected: "Mode: prp (generation review)"

# Explicit exe mode
/peer-review exe PRP-30
# Expected: "Mode: exe (execution review)"
```

**Test error cases**:
```bash
# No target
/peer-review
# Expected: Error "Usage: /peer-review [prp|exe] <target>"

# Mode without target
/peer-review exe
# Expected: Error "Target required for exe mode"

# Invalid mode
/peer-review foo PRP-30
# Expected: Error "Invalid mode: foo (use prp or exe)"
```

---

### Gate 2: Factuality Checks Work

**Test file_exists check**:
```bash
# Create PRP with file claim
echo "files_modified: [.claude/settings.local.json]" > test-prp.yaml

# Run review
/peer-review test-prp.yaml
# Expected: ✓ file:.claude/settings.local.json PASS

# Test false claim
echo "files_modified: [/fake/path.md]" > test-prp.yaml
/peer-review test-prp.yaml
# Expected: ✗ file:/fake/path.md FAIL (file not found)
```

**Test commit_exists check**:
```bash
# Test real commit
/peer-review PRP-30
# Expected: ✓ commit:12e6893 PASS

# Test fake commit
# (Add "Commit abc9999" to PRP)
# Expected: ✗ commit:abc9999 FAIL (commit not found)
```

**Test dependency_exists check**:
```bash
# Test real dependencies
/peer-review PRP-30
# Expected:
#   ✓ dependency:PRP-C PASS
#   ✓ dependency:PRP-D PASS

# Test fake dependency
# (Add "dependencies: PRP-999" to YAML)
# Expected: ✗ dependency:PRP-999 FAIL (PRP not in executed/)
```

---

### Gate 3: Cache Works

**Test cache creation**:
```bash
# First run (cache miss)
time /peer-review PRP-30
# Expected: ~5s, creates .ce/peer-review-cache.json

# Check cache file
test -f .ce/peer-review-cache.json && echo "✓ Cache created" || echo "✗ FAIL"
```

**Test cache hits**:
```bash
# Second run (cache hit)
time /peer-review PRP-30
# Expected: ~1s (4x faster)

# Verify cache hit
cat .ce/peer-review-cache.json | jq '.checks[] | select(.access_count > 1)'
# Expected: Shows entries with access_count=2
```

**Test TTL expiration**:
```bash
# Manually expire entry
jq '.checks["file:.claude/settings.local.json"].expires_at = "2020-01-01T00:00:00Z"' \
   .ce/peer-review-cache.json > tmp.json && mv tmp.json .ce/peer-review-cache.json

# Run review
/peer-review PRP-30
# Expected: Expired entry removed, re-verified

# Check cache
grep "2020-01-01" .ce/peer-review-cache.json
# Expected: No matches (expired entry removed)
```

---

### Gate 4: Cache Maintenance Works

**Test max size limit**:
```bash
# Create 150 cache entries
for i in {1..150}; do
  jq --arg key "file:/fake/path$i.md" \
     --arg now "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
     '.checks[$key] = {"result":"PASS","verified_at":$now,"expires_at":$now,"access_count":1}' \
     .ce/peer-review-cache.json > tmp.json && mv tmp.json .ce/peer-review-cache.json
done

# Run review (triggers cleanup)
/peer-review PRP-30

# Check cache size
jq '.checks | length' .ce/peer-review-cache.json
# Expected: 100 (max size enforced)
```

**Test orphan removal**:
```bash
# Add entry for non-existent file
jq '.checks["file:/fake/deleted.md"] = {"result":"PASS","verified_at":"2025-10-30T12:00:00Z","expires_at":"2025-10-30T13:00:00Z","access_count":1}' \
   .ce/peer-review-cache.json > tmp.json && mv tmp.json .ce/peer-review-cache.json

# Run review (triggers cleanup)
/peer-review PRP-30

# Check if orphan removed
grep "/fake/deleted.md" .ce/peer-review-cache.json
# Expected: No matches (orphan removed)
```

---

### Gate 5: Output is Actionable

**Test output format**:
```bash
/peer-review PRP-30
# Expected output format:
# ✓ Clear pass/fail indicators
# ✗ Failed checks listed with fix suggestions
# Summary: X PASS, Y FAIL
```

**Test fix suggestions**:
```bash
# Inject false file claim
# Expected output includes:
# ✗ file:/fake/path.md
#   → FIX: Update PRP to remove reference OR verify file should exist
```

---

## 5. Testing Strategy

### Pre-Execution Tests

**Test 1: Verify current state**
```bash
# Check current peer-review.md structure
wc -l .claude/commands/peer-review.md
# Expected: ~360 lines (baseline)

# Check no cache file exists yet
test ! -f .ce/peer-review-cache.json && echo "✓ No cache" || echo "✗ Cache exists"
```

**Test 2: Verify mode detection logic**
```bash
# Test with mock command
echo '/peer-review PRP-30' | grep -q 'PRP-30' && echo "✓ Parses target"
echo '/peer-review exe PRP-30' | grep -q 'exe' && echo "✓ Detects exe mode"
```

### Mid-Execution Tests

**After Phase 1** (mode detection added):
```bash
# Verify section added
grep -q "## Mode Detection" .claude/commands/peer-review.md && echo "✓ PASS" || echo "✗ FAIL"

# Verify line count increase
wc -l .claude/commands/peer-review.md
# Expected: ~370 lines (+10 from baseline)
```

**After Phase 2** (generation review added):
```bash
# Verify section added
grep -q "## Mode 1: Generation Review" .claude/commands/peer-review.md && echo "✓ PASS" || echo "✗ FAIL"

# Verify line count increase
wc -l .claude/commands/peer-review.md
# Expected: ~420 lines (+50 from phase 1)
```

**After Phase 3** (factuality checks added):
```bash
# Verify registry section
grep -q "## Factuality Check Registry" .claude/commands/peer-review.md && echo "✓ PASS" || echo "✗ FAIL"

# Verify all 5 checks documented
grep -c "### Check:" .claude/commands/peer-review.md
# Expected: 5 (file_exists, commit_exists, dependency_exists, branch_exists, tag_exists)
```

**After Phase 4** (cache added):
```bash
# Verify cache section
grep -q "## Cache System" .claude/commands/peer-review.md && echo "✓ PASS" || echo "✗ FAIL"

# Verify maintenance rules documented
grep -c "Rule [1-3]:" .claude/commands/peer-review.md
# Expected: 3 (TTL, max size, orphans)
```

### Post-Execution Tests

**Test 1: Complete workflow**
```bash
# Generate PRP
/generate-prp initials/test/INITIAL.md
# Output: PRP-X

# Review generation (should use new prp mode)
/peer-review PRP-X
# Expected: Factuality checks run, cache created

# Execute PRP
/execute-prp PRP-X

# Review execution (should use exe mode)
/peer-review exe PRP-X
# Expected: Uses cached results where applicable
```

**Test 2: Cache performance**
```bash
# First run (cold cache)
time /peer-review PRP-30
# Capture: baseline_time

# Second run (warm cache)
time /peer-review PRP-30
# Capture: cached_time

# Verify speedup
# Expected: cached_time < baseline_time * 0.5 (at least 2x faster)
```

**Test 3: Factuality catches errors**
```bash
# Create PRP with false claims
cat > PRPs/feature-requests/PRP-TEST.md <<EOF
---
dependencies: PRP-999
files_modified: [/fake/file.md]
---
# Test PRP
EOF

# Review
/peer-review PRP-TEST
# Expected:
#   ✗ dependency:PRP-999 FAIL
#   ✗ file:/fake/file.md FAIL
#   Summary: 0 PASS, 2 FAIL
```

### Coverage

- **Mode Detection**: 100% (all cases tested)
- **Factuality Checks**: 100% (all 5 check types tested)
- **Cache System**: 100% (creation, hits, TTL, maintenance)
- **Output Format**: 100% (verified actionable)
- **Error Handling**: 90% (common errors tested)

---

## 6. Rollout Plan

### Phase 1: Preparation (5 minutes)

**Actions**:
1. Read complete PRP
2. Verify no uncommitted changes in `.claude/commands/peer-review.md`
3. Review current peer-review.md structure
4. Decide if any existing workflows need updating

**Validation**: Ready to proceed

---

### Phase 2: Implementation (30 minutes)

**Actions**:
1. Phase 1: Add mode detection (10 min)
2. Phase 2: Add generation review mode (15 min)
3. Phase 3: Add factuality check registry (10 min)
4. Phase 4: Add cache system (5 min)
5. Phase 5: Update examples (5 min)

**Validation**: All 5 phases complete, file size ~460 lines

---

### Phase 3: Testing (10 minutes)

**Actions**:
1. Run all validation gates (Gate 1-5)
2. Test complete workflow
3. Verify cache performance
4. Test factuality detection

**Validation**: All gates pass

---

### Phase 4: Sign-off (5 minutes)

**Actions**:
1. Commit changes with descriptive message
2. Update PRP status to executed
3. Move to PRPs/executed/

**Success Criteria**:
- ✅ Two modes implemented (prp default, exe explicit)
- ✅ Factuality checks work (5 check types)
- ✅ Cache works with auto-maintenance
- ✅ All validation gates pass
- ✅ Performance target met (<5s overhead)
- ✅ Documentation complete and clear

---

## 7. Rollback Procedures

### Full Rollback

If implementation fails catastrophically:

```bash
# 1. Revert file changes
git checkout HEAD -- .claude/commands/peer-review.md

# 2. Remove cache file if created
rm -f .ce/peer-review-cache.json

# 3. Verify rollback
git diff .claude/commands/peer-review.md
# Expected: No changes
```

### Partial Rollback

**Phase 1-2 Failure** (mode detection issues):
- Remove mode detection section
- Keep single mode (exe)
- Document decision to stay with current approach

**Phase 3 Failure** (factuality checks broken):
- Remove factuality check registry section
- Keep modes without factuality validation
- Document as future enhancement

**Phase 4 Failure** (cache issues):
- Remove cache system section
- Keep factuality checks without caching
- Performance slower but functional

---

## 8. Post-Execution Notes

**Completion Checklist**:
- [ ] Mode detection works (prp default, exe explicit)
- [ ] Generation review section complete
- [ ] Factuality check registry documented (5 checks)
- [ ] Cache system implemented with auto-maintenance
- [ ] Examples updated
- [ ] All validation gates pass
- [ ] Performance target met (<5s overhead)
- [ ] PRP marked as executed

**What We Added**:
- Mode detection logic (~10 lines)
- Generation review section (~50 lines)
- Factuality check registry (~30 lines)
- Cache system documentation (~30 lines)
- Updated examples (~10 lines)
- Total addition: ~130 lines

**What We Kept**:
- All existing execution review content
- All existing validation logic
- Backward compatibility (exe mode still works)

**Performance Gains**:
- Without cache: ~5s overhead per review
- With cache (80% hit rate): ~1s overhead
- Cache maintenance: automatic, no manual intervention

---

## 9. Research Findings

### Current Peer-Review Structure

**File**: `.claude/commands/peer-review.md`
**Size**: 360 lines
**Mode**: Single mode (exe - execution review only)

**Sections**:
1. Usage
2. What It Does (Git Branch Validation, Phase Completion, etc.)
3. Review Output
4. CLI Command
5. Hook Integration
6. Common Issues
7. Review Criteria
8. Workflow Integration
9. Tips
10. Implementation Details
11. Related Commands
12. External References

### Gaps Identified

1. **No pre-execution review** - only post-execution
2. **No factuality validation** - trusts all claims
3. **No mode switching** - single mode only
4. **No caching** - repeated checks slow

### Similar Patterns in Codebase

**Pattern 1: Mode detection** (from `/generate-prp`)
- Uses first argument to detect mode
- Defaults to solo mode if no JSON
- Clean, simple logic

**Pattern 2: Cache with TTL** (from context system)
- Uses JSON cache file
- TTL-based expiration
- Auto-cleanup on load

**Pattern 3: Check registry** (from validation system)
- Documented checks, not coded
- Extendable by adding documentation
- KISS principle applied

---

## 10. Design Decisions

### Decision 1: Two Modes Only

**Options considered**:
- Four modes (exe, prp, doc, logic)
- Two modes (exe, prp)

**Chosen**: Two modes

**Rationale**:
- KISS principle - two modes cover 95% of use cases
- `doc` review = subset of `prp` review
- `logic` review = too subjective, hard to automate
- Extendable: can add more modes later if needed

---

### Decision 2: `prp` as Default Mode

**Options considered**:
- `exe` as default (current behavior)
- `prp` as default (new)
- Require explicit mode always

**Chosen**: `prp` as default

**Rationale**:
- Generation review happens BEFORE execution (more common)
- Execution review happens AFTER execution (less common)
- User workflow: generate → review → execute → review (prp first)
- Breaking change acceptable (command is new, low adoption)

---

### Decision 3: Mandatory Factuality Checks

**Options considered**:
- Optional via `--verify-claims` flag
- Always mandatory

**Chosen**: Always mandatory

**Rationale**:
- User requirement: "verification mandatory"
- Prevents accidentally skipping checks
- Fast enough (<5s) to always run
- Cache makes repeated reviews instant

---

### Decision 4: Cache with Auto-Maintenance

**Options considered**:
- No cache (always verify)
- Cache without maintenance (unbounded growth)
- Cache with manual maintenance (`ce cache clean`)
- Cache with auto-maintenance

**Chosen**: Cache with auto-maintenance

**Rationale**:
- User requirement: "cache verified claims"
- Auto-maintenance = zero user intervention
- KISS: no separate maintenance process
- Performance: 4x faster on cache hits

---

### Decision 5: Documentation-Driven Checks

**Options considered**:
- Code-based check registry (Python/TypeScript)
- Documentation-based registry (markdown)

**Chosen**: Documentation-based

**Rationale**:
- KISS: no code changes needed
- Extendable: add checks by editing markdown
- Self-documenting: checks are documentation
- Follows pattern from rest of system

---

### Decision 6: Simple Output Format

**Options considered**:
- JSON output with scores
- Risk scoring (HIGH/MEDIUM/LOW)
- Simple pass/fail with fix suggestions

**Chosen**: Simple pass/fail with fix suggestions

**Rationale**:
- User requirement: "just check if claims are factual, not risk scoring"
- Actionable: tells user how to fix
- Clear: ✓/✗ symbols easy to scan
- No subjective assessments

---

## 11. KISS Validation

### Complexity Score: 2/10 (Very Low)

**Why low complexity**:
- Documentation-only changes (no code)
- Two modes only (not four)
- Simple checks only (bash commands)
- Auto-maintenance (no manual intervention)
- ~130 lines added to single file

**Complexity drivers**:
- Cache JSON structure (simple)
- Mode detection logic (5 lines)
- Factuality checks (bash commands)

### Extendability Score: 9/10 (High)

**How to extend**:
1. Add new review mode: Add new section in markdown
2. Add new factuality check: Add new subsection in registry
3. Add new cache rule: Update maintenance section
4. Add new output format: Update output examples

**No code changes needed** for any extension.

### Efficiency Score: 9/10 (High)

**Performance**:
- Factuality checks: <5s (10-20 checks × 0.3s)
- Cache hits: ~0.01s (instant)
- Cache maintenance: <0.5s (auto-cleanup)
- Total overhead: <5s without cache, <1s with cache

**Memory**:
- Cache file: ~50KB (100 entries)
- No runtime memory impact

---

## Success Criteria

✅ Two modes work (prp default, exe explicit)
✅ Factuality checks catch false claims
✅ Cache improves performance (4x faster)
✅ Cache auto-maintains (no garbage)
✅ Output is actionable (fix suggestions)
✅ Extendable via documentation
✅ KISS aligned (simple, no overengineering)
✅ Implementation time < 1 hour

---

**Ready for approval and execution?**
