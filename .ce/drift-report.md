## Context Drift Report - Examples/ Patterns

**Drift Score**: 25.0% (🚨 CRITICAL)
**Generated**: 2025-10-16T19:46:56.605177+00:00
**Violations Found**: 8
**Missing Examples**: 0

### Part 1: Code Violating Documented Patterns

#### KISS Violations (2 violations)

1. File tools/ce/validation_loop.py has deep_nesting (violates pattern): Reduce nesting depth (max 4 levels)
2. File tools/ce/resilience.py has deep_nesting (violates pattern): Reduce nesting depth (max 4 levels)

### Part 2: Missing Pattern Documentation

**Critical PRPs Without Examples**:

All critical PRPs have corresponding examples/ documentation.

### Proposed Solutions Summary

1. **Code Violations** (manual review):
   - Review and fix: File tools/ce/validation_loop.py has deep_nesting (violates pattern): Reduce nesting depth (max 4 levels)
   - Review and fix: File tools/ce/blueprint_parser.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review and fix: File tools/ce/drift.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review 5 other files listed in Part 1

2. **Missing Examples** (documentation needed):
   - No missing examples

3. **Prevention**:
   - Add pre-commit hook: ce validate --level 4 (pattern conformance)
   - Run /update-context weekly to detect drift early
   - Update CLAUDE.md when new patterns emerge

### Next Steps
1. Review violations in Part 1 and fix manually
2. Create missing examples from Part 2
3. Validate: ce validate --level 4
4. Update patterns if codebase evolution is intentional
5. Re-run /update-context to verify drift resolved
