# Hook Configuration

Complete guide for configuring lifecycle hooks in Claude Code to automate workflows at key trigger points (session start, pre-commit, prompt submit).

## Purpose

Hooks enable:

- **Automated validation**: Run checks before commits
- **Context awareness**: Check drift at session start
- **Custom workflows**: Execute scripts at trigger points
- **Blocking operations**: Prevent commits/actions if checks fail
- **Notification**: Display messages to user

**When to Use**:

- Validation before commit (tests, linting, format)
- Health checks at session start (drift, MCP status)
- Custom logic before AI interactions
- Enforcing team standards

**When NOT to Use**:

- Long-running operations (>10s) → Use slash commands instead
- Interactive prompts → Hooks should be non-interactive
- External dependencies → May break if services down

## Prerequisites

- Claude Code installed and configured
- Project with `.claude/hooks/` directory
- Shell scripting knowledge (bash recommended)
- Understanding of hook return codes

## Hook Types

### Available Hooks

| Hook | Trigger | Use Case | Blocking |
|------|---------|----------|----------|
| `session-start` | Claude Code session starts | Drift checks, MCP health | No |
| `pre-commit` | Before git commit | Validation, tests, format | Yes |
| `user-prompt-submit` | Before sending user prompt | Custom pre-processing | Yes |

**Blocking**: Hook can prevent action if returns non-zero exit code.

## Hook Structure

### Basic Template

```bash
#!/bin/bash

# Hook name: describe purpose
# Trigger: when this runs
# Blocking: yes/no

# Exit codes:
#   0 = success (continue)
#   1 = warning (continue with message)
#   2+ = error (block action)

# Your logic here
echo "Running hook..."

# Return appropriate exit code
exit 0
```

### Execution Environment

Hooks run in project root directory with access to:

- **Working directory**: `/Users/user/project`
- **Git repository**: Full git access
- **Environment variables**: Inherited from Claude Code
- **Tools**: CE CLI tools (`cd tools && uv run ce ...`)
- **Bash utilities**: Standard bash commands

## Session Start Hook

### Purpose

Run checks when Claude Code session starts.

### Example: Drift + MCP Health Check

**File**: `.claude/hooks/session-start`

```bash
#!/bin/bash

# Session Start Hook: Check context drift and MCP health
# Trigger: When Claude Code session starts
# Blocking: No (always allows session to start)

echo "============================================================"
echo "Context Engineering - Session Start"
echo "============================================================"

# Check context drift
echo "Checking context drift..."
cd tools && uv run ce analyze-context --quiet

drift_code=$?

if [ $drift_code -eq 0 ]; then
  echo "✅ Context health: Good (<5% drift)"
elif [ $drift_code -eq 1 ]; then
  echo "⚠️  Context health: Warning (5-15% drift)"
  echo "   Run: ce context sync"
elif [ $drift_code -eq 2 ]; then
  echo "❌ Context health: Critical (≥15% drift)"
  echo "   Run: ce context sync"
fi

# Check Syntropy MCP servers
echo ""
echo "Checking Syntropy MCP servers..."
/syntropy-health --compact

echo "============================================================"

# Always exit 0 (non-blocking)
exit 0
```

**Output at Session Start**:

```
============================================================
Context Engineering - Session Start
============================================================
Checking context drift...
⚠️  Context health: Warning (8.7% drift)
   Run: ce context sync

Checking Syntropy MCP servers...
🔧 Syntropy: 9 servers, 31 tools, all operational
============================================================
```

### Example: Compact Version

**File**: `.claude/hooks/session-start:compact`

```bash
#!/bin/bash

# Compact session start hook

# Drift check
cd tools && uv run ce analyze-context --quiet
if [ $? -eq 2 ]; then
  echo "⚠️  HIGH DRIFT: Run ce context sync"
fi

# MCP health
/syntropy-health --one-line

exit 0
```

## Pre-Commit Hook

### Purpose

Validate changes before commit, block commit if validation fails.

### Example: Run Validation Gates

**File**: `.claude/hooks/pre-commit`

```bash
#!/bin/bash

# Pre-Commit Hook: Run validation before commit
# Trigger: Before git commit
# Blocking: Yes (exit 1+ blocks commit)

echo "🔒 Pre-Commit Validation..."

# Run validation gates
cd tools && uv run ce validate --level 4

validation_code=$?

if [ $validation_code -eq 0 ]; then
  echo "✅ Validation passed - commit allowed"
  exit 0
else
  echo "❌ Validation failed - commit blocked"
  echo "   Fix issues or use: git commit --no-verify"
  exit 1
fi
```

**Behavior**:

- **Pass**: Commit proceeds
- **Fail**: Commit blocked, user sees error message

**Bypass** (use sparingly):

```bash
git commit --no-verify -m "WIP: Bypass validation"
```

### Example: Auto-Format + Test

**File**: `.claude/hooks/pre-commit:format-test`

```bash
#!/bin/bash

# Pre-commit: Auto-format and test

echo "🔒 Pre-Commit: Format + Test..."

# Format Python files
echo "Formatting Python files..."
cd tools && uv run black ce/ tests/
git add -u  # Stage formatting changes

# Run tests
echo "Running tests..."
cd tools && uv run pytest tests/ -q

if [ $? -eq 0 ]; then
  echo "✅ Tests passed - commit allowed"
  exit 0
else
  echo "❌ Tests failed - commit blocked"
  exit 1
fi
```

### Example: Deny List Check

**File**: `.claude/hooks/pre-commit:deny-check`

```bash
#!/bin/bash

# Pre-commit: Check for denied patterns

echo "🔒 Pre-Commit: Checking for denied patterns..."

# Denied patterns
DENY_PATTERNS=(
  "console.log"
  "debugger"
  "import pdb"
  "TODO.*URGENT"
  "\.env"
)

failed=0

for pattern in "${DENY_PATTERNS[@]}"; do
  matches=$(git diff --cached | grep -E "$pattern" | wc -l)
  if [ "$matches" -gt 0 ]; then
    echo "❌ Found denied pattern: $pattern"
    git diff --cached | grep -E "$pattern"
    failed=1
  fi
done

if [ $failed -eq 1 ]; then
  echo ""
  echo "Commit blocked due to denied patterns."
  echo "Remove patterns or use: git commit --no-verify"
  exit 1
fi

echo "✅ No denied patterns found"
exit 0
```

## User Prompt Submit Hook

### Purpose

Process user input before sending to AI.

### Example: Prompt Preprocessing

**File**: `.claude/hooks/user-prompt-submit`

```bash
#!/bin/bash

# User Prompt Submit Hook: Preprocess user input
# Trigger: Before sending user prompt to AI
# Blocking: No (exit 1+ shows message but doesn't block)

# This hook receives user prompt via stdin
# Can modify prompt or just log

# Read user prompt (optional)
# prompt=$(cat)

# Example: Log prompt for analytics
# echo "$prompt" >> .claude/prompt-log.txt

# Example: Check for common mistakes
# if echo "$prompt" | grep -q "delete everything"; then
#   echo "⚠️  Warning: Destructive operation detected!"
# fi

exit 0
```

### Example: Context Injection

**File**: `.claude/hooks/user-prompt-submit:context-inject`

```bash
#!/bin/bash

# Inject additional context before AI processes prompt

# Get current PRP being worked on
current_prp=$(git branch --show-current | sed 's/prp-/PRP-/' | sed 's/-/ /')

if [ ! -z "$current_prp" ]; then
  echo "📎 Context: Working on $current_prp"
fi

exit 0
```

## Return Codes

### Exit Code Meanings

| Code | Meaning | Blocking Behavior |
|------|---------|-------------------|
| `0` | Success | Continue operation |
| `1` | Warning | Show message, continue (session-start) or block (pre-commit) |
| `2+` | Error | Block operation, show error |

### Example: Tiered Return Codes

```bash
#!/bin/bash

# Check severity and return appropriate code

severity=$(check_severity)

case $severity in
  "low")
    echo "ℹ️  Low severity issues detected"
    exit 0  # Allow
    ;;
  "medium")
    echo "⚠️  Medium severity issues detected"
    exit 1  # Warn
    ;;
  "high")
    echo "❌ High severity issues detected"
    exit 2  # Block
    ;;
esac
```

## Hook Location

### Directory Structure

```
.claude/
└── hooks/
    ├── session-start           # Session start hook
    ├── session-start:compact   # Alternative version (use :suffix)
    ├── pre-commit              # Pre-commit hook
    ├── pre-commit:format-test  # Alternative pre-commit
    └── user-prompt-submit      # Prompt submit hook
```

### Selecting Hooks

**Default**: Claude Code uses hooks without suffix

**Switch**:

```bash
# Use compact session-start
mv .claude/hooks/session-start .claude/hooks/session-start:full
mv .claude/hooks/session-start:compact .claude/hooks/session-start
```

## Permissions

### Make Hooks Executable

```bash
# Required: Hooks must be executable
chmod +x .claude/hooks/session-start
chmod +x .claude/hooks/pre-commit
chmod +x .claude/hooks/user-prompt-submit

# Or all at once
chmod +x .claude/hooks/*
```

## Real Project Examples

### Example 1: Current Session Start Hook

**File**: `.claude/hooks/session-start` (from this project)

```bash
#!/bin/bash

echo "Checking context drift..."
cd tools && uv run ce analyze-context --quiet

drift_code=$?
if [ $drift_code -eq 2 ]; then
  echo "⚠️  HIGH DRIFT: Run ce context sync"
fi

echo ""
echo "Checking Syntropy MCP servers..."
/syntropy-health

exit 0
```

### Example 2: Current Pre-Commit Hook

**File**: `.claude/hooks/pre-commit` (from this project)

```bash
#!/bin/bash

echo "🔒 Running validation before commit..."
cd tools && uv run ce validate --level 4

if [ $? -ne 0 ]; then
  echo "❌ Validation failed. Commit blocked."
  echo "   Fix issues or bypass: git commit --no-verify"
  exit 1
fi

echo "✅ Validation passed"
exit 0
```

## Common Patterns

### Pattern 1: Fast Fail

Exit immediately on first error:

```bash
#!/bin/bash

set -e  # Exit on any error

check_1
check_2
check_3

echo "All checks passed"
exit 0
```

### Pattern 2: Accumulate Errors

Run all checks, report all errors:

```bash
#!/bin/bash

failed=0

if ! check_1; then failed=1; fi
if ! check_2; then failed=1; fi
if ! check_3; then failed=1; fi

if [ $failed -eq 1 ]; then
  echo "Some checks failed"
  exit 1
fi

echo "All checks passed"
exit 0
```

### Pattern 3: Conditional Execution

Only run hook in certain conditions:

```bash
#!/bin/bash

# Only run on main branch
current_branch=$(git branch --show-current)

if [ "$current_branch" != "main" ]; then
  echo "Not on main branch, skipping hook"
  exit 0
fi

# Run checks only on main
run_expensive_checks
exit $?
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Long-Running Hooks

**Bad**:

```bash
# DON'T: 5-minute hook
cd tools && uv run ce full-analysis
exit $?
```

**Good**:

```bash
# DO: Quick checks (<10s)
cd tools && uv run ce analyze-context --quick
exit $?
```

**Why**: Hooks should be fast (<10s), slow hooks frustrate users.

### ❌ Anti-Pattern 2: Interactive Hooks

**Bad**:

```bash
# DON'T: Prompt for input
read -p "Continue? (y/n): " answer
```

**Good**:

```bash
# DO: Non-interactive checks
check_condition
exit $?
```

**Why**: Hooks run in background, can't interact with user reliably.

### ❌ Anti-Pattern 3: No Error Messages

**Bad**:

```bash
# DON'T: Silent failure
check_something
exit 1
```

**Good**:

```bash
# DO: Clear error messages
if ! check_something; then
  echo "❌ Check failed: reason"
  echo "   Fix: suggested action"
  exit 1
fi
```

**Why**: Users need to understand why hook failed.

## Related Examples

- [slash-command-template.md](slash-command-template.md) - Creating commands triggered by hooks
- [../workflows/context-drift-remediation.md](../workflows/context-drift-remediation.md) - Drift checks in hooks
- [../workflows/vacuum-cleanup.md](../workflows/vacuum-cleanup.md) - Cleanup in pre-commit hooks

## Troubleshooting

### Issue: Hook not running

**Symptom**: Hook never executes

**Cause**: Not executable or wrong location

**Solution**:

```bash
# Check location
ls -la .claude/hooks/

# Make executable
chmod +x .claude/hooks/session-start

# Verify
bash .claude/hooks/session-start
```

### Issue: Hook blocks incorrectly

**Symptom**: Hook blocks when it shouldn't

**Cause**: Exit code 1+ returned on success

**Solution**:

```bash
# Review hook logic
cat .claude/hooks/pre-commit

# Ensure success returns 0
# Success: exit 0
# Failure: exit 1
```

### Issue: Hook too slow

**Symptom**: Hook takes >10s, session start delayed

**Solution**:

```bash
# Profile hook
time bash .claude/hooks/session-start

# Optimize slow commands
# Use --quick, --fast, or --cached flags
cd tools && uv run ce analyze-context --quick
```

## Performance Tips

1. **Speed**: Keep hooks <10s (ideally <5s)
2. **Caching**: Use cached results where possible
3. **Async**: For session-start, background long operations
4. **Selective**: Only run expensive checks on relevant files
5. **Fail fast**: Exit early on first error

## Resources

- Hook Directory: `.claude/hooks/`
- Claude Code Docs: https://docs.claude.com/claude-code/hooks
- Git Hooks: Standard git hook documentation
- Bash Scripting: Bash scripting guides
