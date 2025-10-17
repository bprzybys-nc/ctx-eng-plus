## Context Drift Report - Examples/ Patterns

**Drift Score**: 10.0% (⚠️  WARNING)
**Generated**: 2025-10-17T15:02:51.003392+00:00
**Violations Found**: 3
**Missing Examples**: 0

### Part 1: Code Violating Documented Patterns

### Part 2: Missing Pattern Documentation

**Critical PRPs Without Examples**:

All critical PRPs have corresponding examples/ documentation.

### Proposed Solutions Summary

1. **Code Violations** (manual review):
   - Review and fix: File tools/ce/context.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review and fix: File tools/ce/pipeline.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance
   - Review and fix: File tools/ce/pattern_extractor.py has missing_troubleshooting (violates examples/patterns/error-handling.py): Add 🔧 Troubleshooting guidance

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
