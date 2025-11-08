# /iteration - Run init-project iteration test

**Purpose**: Test init-project on a target project with validation gates

**Usage**:
```bash
/iteration <number> <project-path>
/iteration <number> <project-description>
```

**Examples**:
```bash
/iteration 1 /Users/bprzybyszi/nc-src/mlx-trading-pipeline-context-engineering
/iteration 2 mlx-trading-pipeline cloned to ~/nc-src/mlx-trading-pipeline-context-engineering
/iteration auto ctx-eng-plus-test-target
```

---

## What You Do

### Step 1: Parse Arguments

Extract:
- **Iteration number**: First argument (use "auto" for auto-increment)
- **Project path**: Second argument onwards
  - If starts with `/` or `~` → treat as path
  - Otherwise → treat as description, infer path from context

### Step 2: Resolve Project Path

**If path provided**:
- Use directly: `/Users/bprzybyszi/nc-src/mlx-trading-pipeline-context-engineering`

**If description provided**:
- Parse description for path hints
- Common patterns:
  - "mlx-trading-pipeline" → `~/nc-src/mlx-trading-pipeline-context-engineering`
  - "test-target" → `~/nc-src/ctx-eng-plus-test-target`
  - "ctx-eng-plus" → `~/nc-src/ctx-eng-plus`

### Step 3: Determine Iteration Number

**If "auto"**:
- Find highest existing iteration in `tmp/prp*-iteration-*.md` and `tmp/prp*-iteration-*.log`
- Increment by 1

**If number provided**:
- Use as-is

### Step 4: Reset Target Project

```bash
cd <project-path>
git status  # Check current state
git log --oneline -5  # Show recent commits

# Find initial commit or specified commit
git log --oneline --reverse | head -1  # Get initial commit

# Reset to clean state
git reset --hard <commit-hash>
git clean -fdx

# Create iteration branch
git checkout -b prp41-iteration-<number>
```

### Step 5: Run init-project

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools

# Run with logging
uv run ce init-project <project-path> 2>&1 | tee ../tmp/prp41-iteration-<number>.log
```

### Step 6: Validation Gates

Run these checks and document results:

**Gate 1: Framework Structure Preserved**
```bash
cd <project-path>
test -d .ce/.serena/memories && echo "✅ Framework memories at .ce/.serena/memories/"
test ! -d .ce/memories && echo "✅ No .ce/memories/ directory"
find .ce/.serena/memories -name "*.md" | wc -l  # Should be 24
```

**Gate 2: Examples Migration**
```bash
test -d .ce/examples && echo "✅ .ce/examples/ exists"
find .ce/examples -name "*.md" | wc -l  # Count migrated examples
test ! -d examples && echo "✅ Root examples/ removed" || echo "❌ Root examples/ still exists"
```

**Gate 3: PRPs Migration**
```bash
test -d .ce/PRPs && echo "✅ .ce/PRPs/ exists"
find .ce/PRPs -name "*.md" | wc -l  # Count migrated PRPs
test ! -d PRPs && echo "✅ Root PRPs/ removed" || echo "❌ Root PRPs/ still exists"
```

**Gate 4: Memories Domain (if applicable)**
```bash
# Only if target had existing .serena/
test -d .serena/memories && echo "✅ Canonical location at .serena/memories/"
test ! -d .serena.old && echo "✅ .serena.old/ cleaned up"
find .serena/memories -name "*.md" | wc -l  # Count memories
```

**Gate 5: Critical Memories Present**
```bash
for mem in code-style-conventions.md task-completion-checklist.md testing-standards.md; do
    test -f .serena/memories/$mem && echo "✅ $mem" || test -f .ce/.serena/memories/$mem && echo "✅ $mem (framework)"
done
```

### Step 7: Generate Report

Create `tmp/prp41-iteration-<number>-report.md` with:

```markdown
# PRP-41 Iteration <number> - <Project Name>

**Date**: <timestamp>
**Target**: <project-path>
**Branch**: prp41-iteration-<number>
**Status**: ✅ SUCCESS / ❌ FAILED

---

## Validation Results

### ✅/❌ Gate 1: Framework Structure Preserved
- .ce/.serena/memories/: <exists/missing>
- .ce/memories/: <exists (bad)/missing (good)>
- Framework memory count: <count>

### ✅/❌ Gate 2: Examples Migration
- .ce/examples/: <exists/missing>
- Migrated examples: <count>
- Root examples/ removed: <yes/no>

### ✅/❌ Gate 3: PRPs Migration
- .ce/PRPs/: <exists/missing>
- Migrated PRPs: <count>
- Root PRPs/ removed: <yes/no>

### ✅/❌ Gate 4: Memories Domain
- .serena/memories/: <exists/not applicable>
- .serena.old/: <removed/not applicable>
- Memory count: <count>

### ✅/❌ Gate 5: Critical Memories Present
- code-style-conventions.md: <✅/❌>
- task-completion-checklist.md: <✅/❌>
- testing-standards.md: <✅/❌>

---

## Issues Found

<list any issues encountered>

---

## Summary

<brief summary of iteration results>

**Overall Status**: <PASS/FAIL>
**Confidence Score**: <1-10>/10
```

### Step 8: Output Results

Show user:
1. Report location: `tmp/prp41-iteration-<number>-report.md`
2. Log location: `tmp/prp41-iteration-<number>.log`
3. Gate results summary (pass/fail counts)
4. Any critical issues found

---

## Key Principles

1. **Always reset to clean state** before running init-project
2. **Document everything** in report and log files
3. **Validate all gates** systematically
4. **Report failures clearly** with actionable troubleshooting
5. **Use auto-increment** for iteration numbers to avoid conflicts

---

## Common Patterns

**Test on real-world project**:
```bash
/iteration auto mlx-trading-pipeline at ~/nc-src/mlx-trading-pipeline-context-engineering
```

**Test on test target**:
```bash
/iteration auto test-target at ~/nc-src/ctx-eng-plus-test-target
```

**Manual iteration number**:
```bash
/iteration 5 /Users/bprzybyszi/nc-src/ctx-eng-plus-test-target
```

---

## Notes

- Iteration command is designed for PRP-41 validation but can be adapted for other PRPs
- Auto-increment scans `tmp/` directory for existing iteration files
- Report format is standardized for easy comparison across iterations
- Branch naming: `prp41-iteration-<number>` (or customize for other PRPs)
