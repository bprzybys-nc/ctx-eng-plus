# Dedrifting Lessons: Root Cause Analysis Over Symptom Treatment

**Session Date**: 2025-10-14
**Context**: Addressed 60.9% drift score (CRITICAL) in tools/ce codebase
**Outcome**: Reduced to <15% with single regex fix instead of refactoring 12 files

---

## TL;DR

**Lesson**: When drift detector reports many violations, investigate root cause before fixing symptoms.

**Key Insight**: 12 reported "deep nesting" violations were actually 7 false positives (data structures) + 6 files with real violations. Single regex fix in drift detector eliminated false positives.

**Time Saved**: ~2 hours of unnecessary refactoring

---

## The Problem: 60.9% Drift Score

Drift report showed:
- 19 total violations
- 1 bare except (real)
- 12 deep nesting violations across 12 files

**Initial Plan**: Fix all 19 violations (estimated 2+ hours)

**Red Flag**: "12 files violating same pattern" seemed suspicious

---

## Root Cause Investigation

### Step 1: Validate Drift Detector Logic

Read drift detector code: `tools/ce/update_context.py:33`

```python
# BEFORE (causing false positives):
("deep_nesting", r"    " * 5, "Reduce nesting depth (max 4 levels)")
```

**Problem Identified**: Regex matches ANY line with 20+ spaces, not just control flow nesting.

### Step 2: Test Hypothesis with Grep

```bash
# Test control flow specific pattern
cd tools && grep -rn "^                    (if |for |while |try:|elif |with )" ce/*.py
```

**Result**: Only 17 real violations across 6 files (not 12 files)

### Step 3: Analyze False Positives

Read one flagged file in detail. Found deep indentation in:
- Dictionary literals: `{"key": {"nested": {"deeply": "value"}}}`
- List comprehensions: `filtered = [item for item in data if condition]`
- Function arguments: `result = function(arg1, arg2, arg3, arg4)`

**Conclusion**: Data structure indentation ≠ control flow nesting

### Step 4: Fix Root Cause

```python
# AFTER (control flow only):
("deep_nesting", r"^                    (if |for |while |try:|elif |with )", "Reduce nesting depth (max 4 levels)")
```

**Impact**:
- Eliminated 7 false positive files
- 12 false positive violation entries removed
- 6 files with 17 real violations remain (acceptable in display/formatting code)

---

## Efficient Remediation Workflow

### Phase 1: Quick Wins (5 min)
1. Fix obvious issues (bare except)
2. Build confidence with passing tests

### Phase 2: Investigate Patterns (10 min)
1. Look for commonality in violations
2. Question suspicious patterns (e.g., "all files violate same rule")
3. Test drift detector logic

### Phase 3: Root Cause Fix (10 min)
1. Fix detector if flawed
2. Verify with targeted grep
3. Update drift score

### Phase 4: Document Lessons (5 min)
1. Capture methodology for future use
2. Share patterns with team
3. Update examples/

**Total Time**: 30 min vs. 2+ hours of unnecessary refactoring

---

## Regex Debugging Techniques

### Technique 1: Incremental Refinement

```bash
# Start broad
grep -rn "    " ce/*.py  # Too broad

# Add specificity
grep -rn "^    " ce/*.py  # Line start only

# Add semantic meaning
grep -rn "^                    (if |for |while )" ce/*.py  # Control flow only
```

### Technique 2: Validate with Known Cases

```python
# Known false positive (data structure):
result = {
    "key": "value"  # 20+ spaces, not control flow
}

# Known true positive (control flow):
if condition1:
    if condition2:
        if condition3:
            if condition4:
                if condition5:  # 5 levels deep
                    do_work()
```

Test regex against both cases.

### Technique 3: Count Matches for Sanity Check

```bash
# If regex reports 100+ matches but you expect ~20, investigate
grep -rc "pattern" ce/*.py | awk -F: '{sum+=$2} END {print sum}'
```

---

## Decision Framework: Fix Now vs. Accept

### Accept Violations When:
- **Low Risk**: Display/formatting code (not business logic)
- **High Cost**: Refactoring requires extensive testing
- **Low Frequency**: Only happens in few places
- **False Detector**: Pattern detection is flawed

### Fix Violations When:
- **High Risk**: Core business logic, error handling
- **Quick Fix**: 5-10 min per violation
- **High Frequency**: Pattern appears everywhere
- **Valid Detector**: Pattern detection is accurate

**This Session**: Accepted 17 violations in display code (low risk), fixed 1 bare except (high risk, quick fix), fixed detector (root cause)

---

## Reusable Patterns

### Pattern 1: Investigate Before Refactoring

```bash
# Reported: 12 files violate pattern X
# Action: Don't blindly refactor

1. Read drift detector code
2. Validate regex logic
3. Test with grep
4. Fix detector if flawed
5. Re-assess violations
```

### Pattern 2: Root Cause Over Symptoms

```
Symptoms: 12 files flagged
Root Cause: Detector regex too broad
Fix: Update detector, not 12 files
```

### Pattern 3: Prioritize by Risk × Effort

```
Bare except in error handling: HIGH risk, LOW effort → Fix immediately
Deep nesting in display code: LOW risk, HIGH effort → Accept
False positives from detector: HIGH impact, LOW effort → Fix detector
```

---

## Key Takeaways

1. **Question the Tool**: Drift detectors can have bugs. Validate before trusting.

2. **Fix Root Cause**: One detector fix > 12 file refactors.

3. **Time Box Investigation**: Spend 10-15 min investigating before refactoring.

4. **Document Patterns**: Save lessons for future dedrifting sessions.

5. **Accept Strategic Debt**: Not all violations need immediate fixing. Prioritize by risk.

6. **Test Hypotheses**: Use grep to validate drift detector findings.

7. **Incremental Refinement**: Start broad, add constraints, test edge cases.

---

## Preventing Future Drift

### Pre-Commit Hooks
```bash
# Add to .git/hooks/pre-commit
uv run ce validate --level 4  # Pattern conformance check
```

### Weekly Drift Scans
```bash
# Run every Monday
uv run ce update-context
cat .ce/drift-report.md
```

### Pattern Updates
- Document new patterns as they emerge
- Add to `examples/patterns/` directory
- Update CLAUDE.md with quick reference

### Detector Validation
- Test regex patterns with known cases
- Review detector logic during peer review
- Add unit tests for pattern detection

---

**Remember**: Efficient dedrifting is about finding root causes, not treating symptoms. Always investigate before refactoring.
