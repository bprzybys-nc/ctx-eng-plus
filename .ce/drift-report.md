## Context Drift Report - Examples/ Patterns

**Drift Score**: 6.2% (⚠️  WARNING)
**Generated**: 2025-11-06T10:54:02.618816+00:00
**Violations Found**: 9
**Missing Examples**: 0

### Part 1: Code Violating Documented Patterns

#### KISS Violations (2 violations)

1. File tools/ce/blend.py has deep_nesting (violates pattern): Reduce nesting depth (max 4 levels)
2. File tools/ce/update_context.py has deep_nesting (violates pattern): Reduce nesting depth (max 4 levels)

### Part 2: Missing Pattern Documentation

**Critical PRPs Without Examples**:

All critical PRPs have corresponding examples/ documentation.

### Proposed Solutions Summary

1. **Code Violations** (manual review):
   - Review and fix: File tools/ce/init_project.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review and fix: File tools/ce/validation_loop.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review and fix: File tools/ce/blend.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review 6 other files listed in Part 1

2. **Missing Examples** (documentation needed):
   - No missing examples

3. **Prevention**:
   - Add pre-commit hook: ce validate --level 4 (pattern conformance)
   - Run /update-context weekly to detect drift early
   - Update CLAUDE.md when new patterns emerge

### Next Steps
1. Review violations in Part 1 and fix manually
2. Create missing examples from Part 2
3. **🔧 CRITICAL - Validate Each Fix**:
   - After fixing each violation, run: ce update-context
   - Verify violation removed from drift report
   - If still present: Analyze why fix didn't work, try different approach
4. Validate: ce validate --level 4
5. Update patterns if codebase evolution is intentional
6. Re-run /update-context to verify drift resolved

**Anti-Pattern**: Batch-apply all fixes without validation (violations may persist)
**Correct Pattern**: Fix → Validate → Next fix (iterative verification)
